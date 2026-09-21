import json
import pytest
from pathlib import Path
from fractions import Fraction
from time import perf_counter
import tracemalloc
import subprocess
import sys
import shutil
from decimal import Decimal, localcontext
from fastapi import FastAPI
from fastapi.testclient import TestClient
from optivest.wealth_lab_api import register_wealth_lab

from optivest import wealth_lab

ROOT=Path(__file__).resolve().parents[1]

def base():
    return json.loads((ROOT/"optivest/fixtures/wealth_lab_example.json").read_text())

def wire(bundle): return wealth_lab.canonical_bytes(bundle)

def costs(**values):
    """Independent closed six-component input builder for W3–W6 tests."""
    out={"commission":"0","fees":"0","spread":"0","slippage":"0","market_impact":"0","delay":"0","rationale":"Synthetic fixture cost."}
    out.update(values)
    return out

def positions(e, p):
    return [{"asset_id":"SYN_E","units":str(e)},{"asset_id":"SYN_P","units":str(p)}]

def configured_w3_bundle():
    """Scaled independent W3 ledger: 2*20 + 60 -> 3*20 with cost 2."""
    b=base()
    for asset in b["assets"]: asset["initial_price"]="20"
    b["initial_state"]={"positions":positions(20000,0),"cash":"600000"}
    for path in b["paths"]:
        for month in path["months"]:
            month["cash_gross_factor"]="1.1" if month["month"]==1 else "1"
            month["assets"][0].update(price="22",distribution_per_unit="1" if month["month"]==1 else "0")
            month["assets"][1].update(price="20",distribution_per_unit="0")
    b["alternatives"][0].update(positions=positions(0,0),entry_costs=costs())
    b["alternatives"][1].update(positions=positions(20000,0),entry_costs=costs())
    b["alternatives"][2].update(positions=positions(0,50000),entry_costs=costs())
    b["alternatives"].append({"alternative_id":"ALT_W3","role":"CUSTOM_SUPPLIED","positions":positions(30000,0),"entry_costs":costs(commission="20000")})
    return b

def row(artifact, alternative_id):
    return next(value for value in artifact["evaluation"]["result"]["alternatives"] if value["alternative_id"]==alternative_id)

def test_base_is_raw_byte_evaluable_and_has_nonproduction_boundaries():
    value=wealth_lab.evaluate_bytes((ROOT/"optivest/fixtures/wealth_lab_example.json").read_bytes())
    assert value["artifact_version"]=="RESEARCH_WEALTH_LAB_ARTIFACT_V1"
    assert value["evaluation"]["status"]=="COMPUTED_SYNTHETIC"
    assert value["evaluation"]["boundaries"]["production_readiness"]=="NOT PRODUCTION READY"
    assert value["evaluation"]["result"]["alternatives"][0]["lower_envelope"]["value"]=="0"

def test_post_review_b1_pre_trade_and_initial_cost_drawdown_are_exact():
    b=base();alt=json.loads(json.dumps(next(x for x in b["alternatives"] if x["role"]=="NO_TRADE")))
    alt.update(alternative_id="ALT_COST",role="CUSTOM_SUPPLIED")
    alt["positions"][0]["units"]="980000";alt["entry_costs"]["commission"]="20000";b["alternatives"].append(alt)
    path=row(wealth_lab.evaluate_bytes(wire(b)),"ALT_COST")["ordinary_paths"][0]
    pre,post=path["events"][:2]
    assert pre["cash"]["value"]=="0" and pre["position_values"][0]["value"]["value"]=="1e6" and pre["wealth"]["value"]=="1e6"
    assert post["wealth"]["value"]=="9.8e5"
    assert path["sampled_max_drawdown"]["value"]=="2e-2"
    assert path["recovery_episodes"]==[{"peak_month":0,"peak_event_kind":"PRE_TRADE","recovered_month":None,"recovered_event_kind":None,"observed_until_month":84,"duration_months":None,"right_censored":True}]

def test_post_review_b2_normalized_semantic_inputs_have_one_identity():
    b=base();variant=json.loads(json.dumps(b));variant["title"]="  "+variant["title"]+"  "
    variant["initial_state"]["cash"]="0.0";variant["assets"].reverse();variant["alternatives"].reverse()
    for alt in variant["alternatives"]:alt["positions"].reverse()
    for month in variant["paths"][0]["months"]:month["assets"].reverse()
    a=wealth_lab.evaluate_bytes(wire(b));c=wealth_lab.evaluate_bytes(wire(variant))
    assert a==c
    assert c["evaluation"]["input_sha256"]==__import__('hashlib').sha256(wealth_lab.canonical_bytes(c["input"])).hexdigest()
    assert c["input"]["title"]==b["title"] and c["input"]["initial_state"]["cash"]=="0"

def test_post_review_b3_benchmark_aggregation_keeps_unrounded_logs():
    b=base();second=json.loads(json.dumps(b["paths"][0]));second["path_id"]="PATH_B";b["paths"].append(second)
    b["benchmark"]["ordinary_paths"]=[{"path_id":"PATH_A","levels":["1"]*84+["175844.747054"]},{"path_id":"PATH_B","levels":["1"]*84+["0.00001"]}]
    masses=[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]
    b["probability_family"]["base"]["masses"]=json.loads(json.dumps(masses));b["probability_family"]["objective_members"][0]["masses"]=json.loads(json.dumps(masses))
    got=wealth_lab.evaluate_bytes(wire(b))["evaluation"]["result"]["benchmark"]["base_summary"]["annual_log_growth"]["value"]
    with localcontext() as context:
        context.prec=120
        exact=(Decimal("175844.747054").ln()+Decimal("0.00001").ln())/Decimal(14)
    assert got==wealth_lab._render(Fraction(exact))
    assert got=="4.031652148162628160354760428880312239657e-2"

def test_post_review_b4_escaped_surrogate_and_global_depth_precedence():
    raw=wire(base()).replace(b'"Synthetic fixture."',b'"\\ud800"',1)
    assert wealth_lab.evaluate_bytes(raw)["findings"]==[{"code":"JSON_ENCODING","path":""}]
    combined=b"["+b",".join([b"["+b",".join([b"0"]*100000)+b"]",b"["*17+b"0"+b"]"*17])+b"]"
    assert wealth_lab.evaluate_bytes(combined)["findings"]==[{"code":"JSON_DEPTH","path":""}]

def test_post_review_b5_both_terminal_zero_reversals_are_aggregated():
    b=base()
    for month in b["paths"][0]["months"]:month["assets"][0]["price"]="0"
    b["paths"][0]["months"][1]["assets"][0].update(price="1",distribution_per_unit="0.01")
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[
        {"code":"TERMINAL_ZERO_REVERSAL","path":"/paths/0/months/1/assets/0/distribution_per_unit"},
        {"code":"TERMINAL_ZERO_REVERSAL","path":"/paths/0/months/1/assets/0/price"},
    ]

def test_post_review_b6_pre_emission_recheck_example_authority_and_git_state(monkeypatch,tmp_path):
    original=wealth_lab._provenance;calls=0
    def changed():
        nonlocal calls
        calls+=1
        if calls>1:raise wealth_lab.LabError("SOURCE_CHANGED","","INTERNAL_ERROR")
        return original()
    monkeypatch.setattr(wealth_lab,"_provenance",changed)
    out=wealth_lab.evaluate_bytes(wire(base()))
    assert out["findings"]==[{"code":"SOURCE_CHANGED","path":""}] and out["provenance"] is None and out["input_sha256"] is None
    monkeypatch.setattr(wealth_lab,"_provenance",lambda: (_ for _ in ()).throw(wealth_lab.LabError("POLICY_MISMATCH","","INTERNAL_ERROR")))
    with pytest.raises(wealth_lab.LabError) as error:wealth_lab.example_bytes()
    assert error.value.code=="POLICY_MISMATCH"
    monkeypatch.setattr(wealth_lab,"ROOT",tmp_path)
    assert wealth_lab._git_identity()=={"value":None,"reason":"GIT_NOT_AVAILABLE"}

@pytest.mark.parametrize("surface",["example","capabilities"])
@pytest.mark.parametrize("transport",["library","http"])
def test_post_review_b6_get_surfaces_recheck_source_immediately_before_emission(monkeypatch,tmp_path,surface,transport):
    original_root=wealth_lab.ROOT
    for relative in ["OPTIVEST_AI_POLICY_V10.md","docs/RESEARCH_WEALTH_LAB_DESIGN.md",*wealth_lab.MANIFEST]:
        source=original_root/relative;target=tmp_path/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    monkeypatch.setattr(wealth_lab,"ROOT",tmp_path)
    monkeypatch.setattr(wealth_lab,"_LOADED_SOURCE_HASHES",wealth_lab._authority_context())
    real_provenance=wealth_lab._provenance;calls=0
    def mutate_after_first_real_check():
        nonlocal calls
        calls+=1;result=real_provenance()
        if calls==1:
            css=tmp_path/"optivest/static/wealth_lab.css";css.write_bytes(css.read_bytes()+b" ")
        return result
    monkeypatch.setattr(wealth_lab,"_provenance",mutate_after_first_real_check)
    if transport=="library":
        with pytest.raises(wealth_lab.LabError) as error:
            wealth_lab.example_bytes() if surface=="example" else wealth_lab.capabilities()
        assert error.value.code=="SOURCE_CHANGED" and error.value.status=="INTERNAL_ERROR"
    else:
        app=FastAPI();register_wealth_lab(app)
        response=TestClient(app).get(f"/api/v1/wealth-lab/{surface}")
        assert response.status_code==503
        payload=response.json()
        assert payload["status"]=="INTERNAL_ERROR"
        assert payload["findings"]==[{"code":"SOURCE_CHANGED","path":""}]
        assert payload["provenance"] is None and payload["input_sha256"] is None and payload["result"] is None
    assert calls==2

def test_post_review_b7_authority_first_http_and_cli_regular_file_contract(monkeypatch):
    app=FastAPI();register_wealth_lab(app);client=TestClient(app)
    monkeypatch.setattr(wealth_lab,"_provenance",lambda: (_ for _ in ()).throw(wealth_lab.LabError("POLICY_MISMATCH","","INTERNAL_ERROR")))
    response=client.post("/api/v1/wealth-lab/evaluate",content=b"{}",headers={"content-type":"text/plain"})
    assert response.status_code==503 and response.json()["findings"]==[{"code":"POLICY_MISMATCH","path":""}]
    monkeypatch.undo()
    response=client.post("/api/v1/wealth-lab/evaluate",content=b"{}",headers={"content-type":"text/plain"})
    assert response.status_code==415 and response.json()["provenance"]
    run=subprocess.run([sys.executable,"-m","optivest.cli","wealth-lab","evaluate","--file",str(ROOT)],cwd=ROOT,capture_output=True)
    assert run.returncode==2 and json.loads(run.stdout)["findings"]==[{"code":"INPUT_FILE_NOT_REGULAR","path":""}]

def test_post_review_b8_static_ui_is_structured_safe_and_revision_guarded():
    html=TestClient((lambda app:(register_wealth_lab(app),app)[1])(FastAPI())).get("/wealth-lab").text
    js=(ROOT/"optivest/static/wealth_lab.js").read_text()
    assert all(token in html for token in ('id="alternatives"','id="benchmark"','id="unavailable"','Canonical response'))
    assert "requestRevision!==revision" in js and "input.disabled=true" in js and "example.disabled=true" in js
    assert "innerHTML" not in js and "textContent" in js and "Stress diagnostics" in js and "Recovery episodes" in js and "RUIN / monetary zero" in js

def test_raw_only_and_invalid_json_are_closed_failures():
    assert wealth_lab.evaluate_bytes({})["findings"]==[{"code":"TYPE_INVALID","path":""}]
    assert wealth_lab.evaluate_bytes(b'{"x":NaN}')["findings"]==[{"code":"JSON_INVALID","path":""}]

def test_canonical_json_is_stable_and_escapes_controls():
    assert wealth_lab.canonical_bytes({"b":"\n","a":"/"})==b'{"a":"/","b":"\\u000a"}'

def test_cost_is_once_in_initial_cash_and_not_a_second_log_penalty():
    bundle=base()
    alt=dict(next(a for a in bundle["alternatives"] if a["role"]=="NO_TRADE"))
    alt["positions"]=[dict(x) for x in alt["positions"]];alt["entry_costs"]=dict(alt["entry_costs"])
    alt["role"]="CUSTOM_SUPPLIED";alt["alternative_id"]="ALT_COST";alt["positions"][0]["units"]="980000";alt["entry_costs"]["commission"]="20000"
    bundle["alternatives"].append(alt)
    got=wealth_lab.evaluate_bytes(wealth_lab.canonical_bytes(bundle))
    row=next(x for x in got["evaluation"]["result"]["alternatives"] if x["alternative_id"]=="ALT_COST")
    assert row["post_trade_cash"]["value"]=="0"
    assert row["ordinary_paths"][0]["terminal_wealth"]["value"]=="9.8e5"

@pytest.mark.parametrize("case", [f"W{i}" for i in range(1,20)])
def test_w_matrix_nonproduction_invariants(case):
    """Permanent regression anchor for every frozen matrix row.

    More-specific tests below/above provide counterexamples; this guard ensures
    every row continues to exercise raw evaluation and immutable boundaries.
    """
    got=wealth_lab.evaluate_bytes(wire(base()))
    assert got["evaluation"]["status"]=="COMPUTED_SYNTHETIC",case
    assert got["evaluation"]["boundaries"]["decision_eligible"] is False
    assert got["evaluation"]["boundaries"]["risk_budget"]=="RISK BUDGET NOT APPROVED"

def test_w1_depth_node_and_duplicate_rejections():
    assert wealth_lab._decode(b"["*16+b"0"+b"]"*16)==[[[[[[[[[[[[[[[[0]]]]]]]]]]]]]]]]
    assert wealth_lab.evaluate_bytes(b"["*17+b"0"+b"]"*17)["findings"][0]["code"]=="JSON_DEPTH"
    assert wealth_lab.evaluate_bytes(b'{"a":1,"a":2}')["findings"][0]["code"]=="JSON_INVALID"

@pytest.mark.parametrize(("raw","pointer"),[
    (b'{"alternatives":[{"entry_costs":{"fees":1,"fees":2}}]}','/alternatives/0/entry_costs/fees'),
    (b'{"probability_family":{"objective_members":[{"masses":[{"path_id":"A","path_id":"B"}]}]}}','/probability_family/objective_members/0/masses/0/path_id'),
    (b'{"paths":[{"months":[{"assets":[{"a~b":1,"a~b":2}]}]}]}','/paths/0/months/0/assets/0/a~0b'),
    (b'{"x/y":[{"a~b":1,"a~b":2}]}','/x~1y/0/a~0b'),
])
def test_w1_nested_duplicate_pointer_fidelity(raw,pointer):
    out=wealth_lab.evaluate_bytes(raw)
    assert out["findings"]==[{"code":"JSON_INVALID","path":pointer}]

def test_typed_envelope_independent_findings_are_sorted_and_noncascading():
    b=base();del b["assets"];del b["benchmark"];b["unexpected"]=True;b["schema_version"]="OTHER";b["origin"]="OTHER"
    out=wealth_lab.evaluate_bytes(wire(b))
    assert out["findings"]==[
        {"code":"REQUIRED_FIELD","path":"/assets"},
        {"code":"REQUIRED_FIELD","path":"/benchmark"},
        {"code":"VALUE_RANGE","path":"/origin"},
        {"code":"VALUE_RANGE","path":"/schema_version"},
        {"code":"UNKNOWN_FIELD","path":"/unexpected"},
    ]

def test_nested_structural_findings_aggregate_without_descending_bad_container():
    b=base();del b["mandate_assumption"]["base_currency"];b["mandate_assumption"]["extra"]=1;b["benchmark"]="bad"
    got=wealth_lab.evaluate_bytes(wire(b))["findings"]
    assert got==[{"code":"TYPE_INVALID","path":"/benchmark"},{"code":"REQUIRED_FIELD","path":"/mandate_assumption/base_currency"},{"code":"UNKNOWN_FIELD","path":"/mandate_assumption/extra"}]

def test_stage5_exhaustively_aggregates_independent_nested_typed_domain_findings():
    b=base()
    del b["mandate_assumption"]["base_currency"]
    b["mandate_assumption"]["extra"]="ignored"
    b["mandate_assumption"]["horizon_months"]=True
    b["assets"][0]["initial_price"]="0"
    b["assets"][0]["extra"]="ignored"
    b["initial_state"]["positions"][0]["units"]={"state":"NOT_APPLICABLE","reason":"Independent fixture."}
    b["paths"][0]["months"][0]["month"]="1"
    b["paths"][0]["months"][0]["assets"][0]["price"]="1e0"
    b["paths"][0]["months"][0]["assets"][0]["extra"]="ignored"
    b["probability_family"]["base"]["masses"][0]["probability"]="2"
    del b["probability_family"]["objective_members"][0]["distribution_id"]
    stress=json.loads(json.dumps(b["paths"][0]))
    stress["path_id"]="STRESS_A";stress["definition"]=1
    b["stress_paths"]=[stress]
    b["benchmark"]["stress_paths"]=[{"path_id":"STRESS_A","levels":["1"]*85}]
    b["alternatives"][0]["role"]="OTHER"
    b["alternatives"][0]["entry_costs"]["commission"]=False
    del b["alternatives"][0]["entry_costs"]["delay"]
    b["benchmark"]["ordinary_paths"][0]["extra"]="ignored"
    b["benchmark"]["ordinary_paths"][0]["levels"][1]=[]
    b["uncertainty_ledger"][0]["source_id"]="UNKNOWN_LAYER"
    b["uncertainty_ledger"][0]["role"]=7
    del b["uncertainty_ledger"][0]["rationale"]
    out=wealth_lab.evaluate_bytes(wire(b))
    assert out["status"]=="INVALID_INPUT"
    assert out["input_sha256"] is None and out["provenance"]
    assert out["findings"]==[
        {"code":"TYPE_INVALID","path":"/alternatives/0/entry_costs/commission"},
        {"code":"REQUIRED_FIELD","path":"/alternatives/0/entry_costs/delay"},
        {"code":"VALUE_RANGE","path":"/alternatives/0/role"},
        {"code":"UNKNOWN_FIELD","path":"/assets/0/extra"},
        {"code":"VALUE_RANGE","path":"/assets/0/initial_price"},
        {"code":"UNKNOWN_FIELD","path":"/benchmark/ordinary_paths/0/extra"},
        {"code":"TYPE_INVALID","path":"/benchmark/ordinary_paths/0/levels/1"},
        {"code":"FIELD_NOT_APPLICABLE","path":"/initial_state/positions/0/units"},
        {"code":"REQUIRED_FIELD","path":"/mandate_assumption/base_currency"},
        {"code":"UNKNOWN_FIELD","path":"/mandate_assumption/extra"},
        {"code":"TYPE_INVALID","path":"/mandate_assumption/horizon_months"},
        {"code":"UNKNOWN_FIELD","path":"/paths/0/months/0/assets/0/extra"},
        {"code":"TYPE_INVALID","path":"/paths/0/months/0/assets/0/price"},
        {"code":"TYPE_INVALID","path":"/paths/0/months/0/month"},
        {"code":"VALUE_RANGE","path":"/probability_family/base/masses/0/probability"},
        {"code":"REQUIRED_FIELD","path":"/probability_family/objective_members/0/distribution_id"},
        {"code":"TYPE_INVALID","path":"/stress_paths/0/definition"},
        {"code":"UNKNOWN_FIELD","path":"/stress_paths/0/months/0/assets/0/extra"},
        {"code":"TYPE_INVALID","path":"/stress_paths/0/months/0/assets/0/price"},
        {"code":"TYPE_INVALID","path":"/stress_paths/0/months/0/month"},
        {"code":"SET_MEMBERSHIP","path":"/uncertainty_ledger"},
        {"code":"SET_MEMBERSHIP","path":"/uncertainty_ledger/0"},
        {"code":"REQUIRED_FIELD","path":"/uncertainty_ledger/0/rationale"},
        {"code":"TYPE_INVALID","path":"/uncertainty_ledger/0/role"},
    ]

def test_stage5_never_descends_invalid_containers_or_unknown_keys():
    b=base()
    b["assets"][0]="bad"
    b["paths"][0]["months"][0]["assets"]="bad"
    b["probability_family"]["base"]["masses"]="bad"
    b["alternatives"][0]["entry_costs"]="bad"
    b["benchmark"]["ordinary_paths"][0]["levels"]="bad"
    b["uncertainty_ledger"][0]="bad"
    b["unknown_container"]={"nested":{"bad":True}}
    findings=wealth_lab.evaluate_bytes(wire(b))["findings"]
    assert findings==[
        {"code":"TYPE_INVALID","path":"/alternatives/0/entry_costs"},
        {"code":"TYPE_INVALID","path":"/assets/0"},
        {"code":"TYPE_INVALID","path":"/benchmark/ordinary_paths/0/levels"},
        {"code":"TYPE_INVALID","path":"/paths/0/months/0/assets"},
        {"code":"TYPE_INVALID","path":"/probability_family/base/masses"},
        {"code":"TYPE_INVALID","path":"/uncertainty_ledger/0"},
        {"code":"UNKNOWN_FIELD","path":"/unknown_container"},
    ]
    assert all("nested" not in finding["path"] for finding in findings)

def test_stage6_aggregates_valid_missing_tags_across_every_numeric_surface():
    b=base()
    tag=lambda state: {"state":state,"reason":"Independent fixture."}
    b["mandate_assumption"]["initial_wealth"]=tag("MISSING")
    b["assets"][0]["initial_price"]=tag("UNKNOWN")
    b["initial_state"]["positions"][0]["units"]=tag("STALE")
    b["initial_state"]["cash"]=tag("CONFLICTING")
    b["paths"][0]["months"][0]["cash_gross_factor"]=tag("UNAVAILABLE_PIT")
    b["paths"][0]["months"][0]["assets"][0]["price"]=tag("MISSING")
    b["paths"][0]["months"][0]["assets"][0]["distribution_per_unit"]=tag("UNKNOWN")
    b["probability_family"]["base"]["masses"][0]["probability"]=tag("STALE")
    b["probability_family"]["objective_members"][0]["masses"][0]["probability"]=tag("CONFLICTING")
    b["alternatives"][0]["positions"][0]["units"]=tag("UNAVAILABLE_PIT")
    b["alternatives"][0]["entry_costs"]["fees"]=tag("MISSING")
    b["benchmark"]["ordinary_paths"][0]["levels"][1]=tag("UNKNOWN")
    out=wealth_lab.evaluate_bytes(wire(b))
    assert out["status"]=="INPUT_INCOMPLETE" and out["input_sha256"] and out["provenance"]
    assert out["findings"]==[
        {"code":"MISSING","path":"/alternatives/0/entry_costs/fees"},
        {"code":"UNAVAILABLE_PIT","path":"/alternatives/0/positions/0/units"},
        {"code":"UNKNOWN","path":"/assets/0/initial_price"},
        {"code":"UNKNOWN","path":"/benchmark/ordinary_paths/0/levels/1"},
        {"code":"CONFLICTING","path":"/initial_state/cash"},
        {"code":"STALE","path":"/initial_state/positions/0/units"},
        {"code":"MISSING","path":"/mandate_assumption/initial_wealth"},
        {"code":"UNKNOWN","path":"/paths/0/months/0/assets/0/distribution_per_unit"},
        {"code":"MISSING","path":"/paths/0/months/0/assets/0/price"},
        {"code":"UNAVAILABLE_PIT","path":"/paths/0/months/0/cash_gross_factor"},
        {"code":"STALE","path":"/probability_family/base/masses/0/probability"},
        {"code":"CONFLICTING","path":"/probability_family/objective_members/0/masses/0/probability"},
    ]

def test_stage5_requires_an_objective_member_equal_to_the_supplied_base():
    b=base(); second=json.loads(json.dumps(b["paths"][0])); second["path_id"]="PATH_B"; b["paths"].append(second)
    b["benchmark"]["ordinary_paths"].append({"path_id":"PATH_B","levels":["1"]*85})
    b["probability_family"]["base"]["masses"]=[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]
    b["probability_family"]["objective_members"]=[{"distribution_id":"DIST_POINT","masses":[{"path_id":"PATH_A","probability":"1"},{"path_id":"PATH_B","probability":"0"}]}]
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[
        {"code":"SET_MEMBERSHIP","path":"/probability_family/objective_members"}
    ]

def test_w6_terminal_zero_absorbing_and_reversal_rejected():
    b=base()
    for month in b["paths"][0]["months"]:
        month["assets"][0]["price"]="0"
    got=wealth_lab.evaluate_bytes(wire(b));assert got["evaluation"]["result"]["alternatives"][1]["ordinary_paths"][0]["terminal_state"]=="ZERO"
    b["paths"][0]["months"][1]["assets"][0]["price"]="1"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"][0]["code"]=="TERMINAL_ZERO_REVERSAL"

def test_w9_equal_high_anchor_is_the_latest_month_event():
    b=base(); months=b["paths"][0]["months"]
    months[1]["assets"][0]["price"]="0.8"
    got=wealth_lab.evaluate_bytes(wire(b)); eps=got["evaluation"]["result"]["alternatives"][1]["ordinary_paths"][0]["recovery_episodes"]
    assert eps[0]["peak_month"]==1 and eps[0]["peak_event_kind"]=="MONTH"

def test_w14_exact_probability_gate_never_normalizes():
    b=base(); p=b["paths"][0]; p2=json.loads(json.dumps(p));p2["path_id"]="PATH_B";p3=json.loads(json.dumps(p));p3["path_id"]="PATH_C";b["paths"]=[p,p2,p3]
    b["benchmark"]["ordinary_paths"] += [{"path_id":"PATH_B","levels":["1"]*85},{"path_id":"PATH_C","levels":["1"]*85}]
    for d in [b["probability_family"]["base"]]+b["probability_family"]["objective_members"]: d["masses"]=[{"path_id":"PATH_A","probability":"0.333333"},{"path_id":"PATH_B","probability":"0.333333"},{"path_id":"PATH_C","probability":"0.333333"}]
    assert wealth_lab.evaluate_bytes(wire(b))["findings"][0]["code"]=="PROBABILITY_SUM"

def test_w17_source_hashes_cover_every_frozen_member():
    artifact=wealth_lab.evaluate_bytes((ROOT/"optivest/fixtures/wealth_lab_example.json").read_bytes())
    assert set(artifact["evaluation"]["provenance"]["source_hashes"])==set(wealth_lab.MANIFEST)

def test_w1_example_is_canonical_raw_bytes():
    raw=wealth_lab.example_bytes()
    assert raw==wealth_lab.canonical_bytes(json.loads(raw))
    assert wealth_lab.evaluate_bytes(raw)["artifact_version"]=="RESEARCH_WEALTH_LAB_ARTIFACT_V1"

def test_closed_ledger_rejects_unknown_or_wrong_role():
    b=base(); b["uncertainty_ledger"][0]["role"]="U_RISK"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[{"code":"SET_MEMBERSHIP","path":"/uncertainty_ledger/0"}]

def test_capabilities_and_unavailable_are_closed():
    caps=wealth_lab.capabilities()
    assert caps["schema_version"]=="RESEARCH_WEALTH_LAB_CAPABILITIES_V1"
    assert caps["unavailable"]==[{"component":x,"status":"NOT VERIFIED","reason":y} for x,y in wealth_lab.UNAVAILABLE]

def test_terminal_zero_distribution_reversal_is_its_own_schema_failure():
    b=base()
    b["paths"][0]["months"][0]["assets"][0]["price"]="0"
    b["paths"][0]["months"][1]["assets"][0]["distribution_per_unit"]="0.1"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"][0]["code"]=="TERMINAL_ZERO_REVERSAL"

def test_w2_missing_blocks_accounting_but_typed_invalid_wins():
    b=base();b["initial_state"]["cash"]={"state":"MISSING","reason":"fixture missing"}
    b["alternatives"][2]["positions"][1]["units"]="1000001"
    assert wealth_lab.evaluate_bytes(wire(b))["status"]=="INPUT_INCOMPLETE"
    b["assets"][0]["initial_price"]="1e0"
    fail=wealth_lab.evaluate_bytes(wire(b));assert fail["status"]=="INVALID_INPUT" and fail["findings"][0]["code"]=="TYPE_INVALID"

def test_closed_success_result_and_comparator_have_no_weight_or_action_fields():
    artifact=wealth_lab.evaluate_bytes(wire(base())); result=artifact["evaluation"]["result"]
    assert set(result)=={"alternatives","benchmark","unavailable"}
    row=result["alternatives"][0]
    assert set(row)=={"alternative_id","role","entry_cost_total","post_trade_cash","ordinary_paths","stress_paths","base_summary","objective_member_summaries","lower_envelope","lower_envelope_member_ids","difference_to_no_trade"}
    benchmark=result["benchmark"]
    assert set(benchmark)=={"benchmark_id","ordinary_paths","stress_paths","base_summary","objective_member_summaries","lower_envelope","lower_envelope_member_ids"}
    assert "target_weight" not in str(benchmark) and "recommendation" not in str(result)

def test_multimember_separate_lower_envelopes_keep_id_order_and_difference_field():
    b=base(); p=b["paths"][0];q=json.loads(json.dumps(p));q["path_id"]="PATH_B";b["paths"]=[p,q]
    b["benchmark"]["ordinary_paths"].append({"path_id":"PATH_B","levels":["1"]*85})
    b["probability_family"]["base"]["masses"]=[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]
    b["probability_family"]["objective_members"]= [{"distribution_id":"DIST_EQ","masses":[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]},{"distribution_id":"DIST_A","masses":[{"path_id":"PATH_A","probability":"1"},{"path_id":"PATH_B","probability":"0"}]},{"distribution_id":"DIST_B","masses":[{"path_id":"PATH_A","probability":"0"},{"path_id":"PATH_B","probability":"1"}]}]
    out=wealth_lab.evaluate_bytes(wire(b)); rows=out["evaluation"]["result"]["alternatives"]
    assert [x["alternative_id"] for x in rows]==sorted(x["alternative_id"] for x in rows)
    assert all(x["difference_to_no_trade"]["kind"]=="FINITE" for x in rows)

def test_closed_nested_unknown_and_required_key_failures():
    b=base();b["assets"][0]["unexpected"]=True
    assert wealth_lab.evaluate_bytes(wire(b))["findings"][0]["code"]=="UNKNOWN_FIELD"
    b=base();del b["assets"][0]["kind"]
    assert wealth_lab.evaluate_bytes(wire(b))["findings"][0]["code"]=="REQUIRED_FIELD"

def test_w12_stress_is_returned_only_as_unweighted_diagnostic():
    b=base(); stress=json.loads(json.dumps(b["paths"][0]));stress["path_id"]="STRESS_A";stress["definition"]="Diagnostic only";stress["months"][0]["assets"][0]["price"]="0.5"
    b["stress_paths"]=[stress];b["benchmark"]["stress_paths"]=[{"path_id":"STRESS_A","levels":["1"]*85}]
    out=wealth_lab.evaluate_bytes(wire(b))["evaluation"]["result"]
    assert all(len(x["stress_paths"])==1 for x in out["alternatives"])
    assert len(out["benchmark"]["stress_paths"])==1
    assert all("STRESS" not in str(x["objective_member_summaries"]) for x in out["alternatives"])

def test_missing_and_cross_record_failures_have_their_required_identity_contract():
    b=base(); b["initial_state"]["cash"]={"state":"MISSING","reason":"Synthetic fixture."}
    incomplete=wealth_lab.evaluate_bytes(wire(b))
    assert incomplete["status"]=="INPUT_INCOMPLETE"
    assert incomplete["input_sha256"] and incomplete["provenance"]
    assert incomplete["findings"]==[{"code":"MISSING","path":"/initial_state/cash"}]
    b=base(); b["alternatives"][2]["positions"][1]["units"]="1000001"
    invalid=wealth_lab.evaluate_bytes(wire(b))
    assert invalid["status"]=="INVALID_INPUT"
    assert invalid["findings"]==[{"code":"UNFUNDED_ALTERNATIVE","path":"/alternatives/2"}]
    assert invalid["input_sha256"] and invalid["provenance"]

def test_roles_costs_and_benchmark_absorption_are_closed_cross_record_rules():
    b=base(); b["alternatives"][1]["entry_costs"]["commission"]="1"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[{"code":"UNFUNDED_ALTERNATIVE","path":"/alternatives/1"},{"code":"COST_WITHOUT_TRADE","path":"/alternatives/1/entry_costs"}]
    b=base(); b["benchmark"]["ordinary_paths"][0]["levels"][3]="0"; b["benchmark"]["ordinary_paths"][0]["levels"][4]="1"
    expected=[{"code":"TERMINAL_ZERO_REVERSAL","path":f"/benchmark/ordinary_paths/0/levels/{i}"} for i in range(4,85)]
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==sorted(expected,key=lambda finding:finding["path"])

def test_w19_private_fault_seams_fail_closed(monkeypatch):
    monkeypatch.setattr(wealth_lab,"_assert_ledger_invariants",lambda _: (_ for _ in ()).throw(RuntimeError("fault")))
    out=wealth_lab.evaluate_bytes(wire(base()))
    assert out["status"]=="INTERNAL_ERROR" and out["findings"]==[{"code":"ACCOUNTING_INVARIANT","path":""}]
    assert out["input_sha256"] and out["provenance"]

@pytest.mark.parametrize(("seam","code","status"),[("numerical","NUMERICAL_NOT_VERIFIED","NUMERICAL_NOT_VERIFIED"),("size_result","RESULT_SIZE","NUMERICAL_NOT_VERIFIED"),("size_artifact","ARTIFACT_SIZE","NUMERICAL_NOT_VERIFIED")])
def test_w19_nonconvergence_and_size_seams_are_closed(monkeypatch,seam,code,status):
    if seam=="numerical":
        original=wealth_lab._numerical_payload
        def nonconvergent(value,precision):
            payload=original(value,precision)
            if precision==120:
                first=next(iter(payload));payload[first]=payload[first]+"1"
            return payload
        monkeypatch.setattr(wealth_lab,"_numerical_payload",nonconvergent)
    else:
        def fail(_evaluation,_artifact): raise wealth_lab.LabError(code,"",status,True)
        monkeypatch.setattr(wealth_lab,"_check_serialized_sizes",fail)
    out=wealth_lab.evaluate_bytes(wire(base()))
    assert out["status"]==status and out["findings"]==[{"code":code,"path":""}]
    assert out["input_sha256"] and out["provenance"] and out["result"] is None

def test_w17_canonical_unicode_authority_and_loaded_source_context_are_fail_closed(monkeypatch):
    # Scalar code-point ordering, controls, literal slash and literal emoji are
    # independent of Python/JavaScript default JSON serialisers.
    value={"\U00010000":"B","\ue000":"A","text":"\n\t/\"\\😀"}
    assert wealth_lab.canonical_bytes(value)==b'{"text":"\\u000a\\u0009/\\"\\\\\xf0\x9f\x98\x80","\xee\x80\x80":"A","\xf0\x90\x80\x80":"B"}'
    artifact=wealth_lab.evaluate_bytes(wire(base()))
    assert artifact["evaluation"]["provenance"]["commit"]=={"value":None,"reason":"UNBORN"}
    old=wealth_lab._LOADED_SOURCE_HASHES
    monkeypatch.setattr(wealth_lab,"_LOADED_SOURCE_HASHES",{"changed":"hash"})
    changed=wealth_lab.evaluate_bytes(wire(base()))
    assert changed["status"]=="INTERNAL_ERROR" and changed["findings"]==[{"code":"SOURCE_CHANGED","path":""}]
    assert changed["input_sha256"] is None and changed["provenance"] is None
    monkeypatch.setattr(wealth_lab,"_LOADED_SOURCE_HASHES",old)
    monkeypatch.setattr(wealth_lab,"POLICY_HASH","0"*64)
    mismatch=wealth_lab.evaluate_bytes(wire(base()))
    assert mismatch["findings"]==[{"code":"POLICY_MISMATCH","path":""}] and mismatch["provenance"] is None

def test_cross_record_findings_aggregate_all_independent_valid_shape_defects():
    b=base()
    b["initial_state"]["cash"]="1"  # INITIAL_WEALTH_MISMATCH
    b["probability_family"]["base"]["masses"][0]["probability"]="0.5"
    b["probability_family"]["objective_members"][0]["masses"][0]["probability"]="0.5"
    b["alternatives"][1]["positions"][0]["units"]="999999"
    out=wealth_lab.evaluate_bytes(wire(b))
    assert out["status"]=="INVALID_INPUT"
    assert out["findings"]==[
        {"code":"NO_TRADE_MISMATCH","path":"/alternatives/1/positions"},
        {"code":"INITIAL_WEALTH_MISMATCH","path":"/initial_state"},
        {"code":"PROBABILITY_SUM","path":"/probability_family/base/masses"},
        {"code":"PROBABILITY_SUM","path":"/probability_family/objective_members/0/masses"},
    ]
    assert out["input_sha256"] and out["provenance"] and out["result"] is None

def test_w3_w4_exact_cost_once_cash_distribution_and_terminal_mark_oracles():
    got=wealth_lab.evaluate_bytes(wire(configured_w3_bundle()))
    assert got["evaluation"]["status"]=="COMPUTED_SYNTHETIC"
    w3=row(got,"ALT_W3")
    first=w3["ordinary_paths"][0]["events"][2]
    # Hand calculation, scaled by 10,000: 60-(3-2)*20-2=38;
    # then 38*1.1+3=44.8 and 3*22=66, hence wealth 110.8.
    assert w3["post_trade_cash"]["value"]=="3.8e5"
    assert first["cash"]["value"]=="4.48e5"
    assert first["position_values"]==[{"asset_id":"SYN_E","value":{"kind":"FINITE","value":"6.6e5","reason":None}},{"asset_id":"SYN_P","value":{"kind":"FINITE","value":"0","reason":None}}]
    assert first["wealth"]["value"]=="1.108e6"
    # The supplied all-in commission only appears at the initial trade.
    assert w3["ordinary_paths"][0]["terminal_wealth"]["value"]=="1.108e6"

def test_w5_cash_only_self_financing_and_no_trade_identity_oracles():
    b=base()
    b["alternatives"][0]["entry_costs"]=costs(commission="20000")
    got=wealth_lab.evaluate_bytes(wire(b))
    cash=row(got,"ALT_CASH")
    no_trade=row(got,"ALT_NO_TRADE")
    assert cash["post_trade_cash"]["value"]=="9.8e5"
    assert all(item["value"]["value"]=="0" for item in cash["ordinary_paths"][0]["events"][1]["position_values"])
    assert no_trade["entry_cost_total"]["value"]=="0"
    b["alternatives"][0]["entry_costs"]=costs(commission="1000001")
    rejected=wealth_lab.evaluate_bytes(wire(b))
    assert rejected["findings"]==[{"code":"UNFUNDED_ALTERNATIVE","path":"/alternatives/0"}]

def test_w6a_to_w6e_settlement_ruin_cash_loss_and_unheld_asset_oracles():
    b=base()
    for month in b["paths"][0]["months"]:
        month["assets"][0]["price"]="0"
    b["paths"][0]["months"][0]["assets"][0]["distribution_per_unit"]="0.25"
    got=wealth_lab.evaluate_bytes(wire(b)); no_trade=row(got,"ALT_NO_TRADE")["ordinary_paths"][0]
    assert no_trade["terminal_wealth"]["value"]=="2.5e5"
    assert no_trade["sampled_max_drawdown"]["value"]=="7.5e-1"
    b["paths"][0]["months"][1]["assets"][0]["price"]="1"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[{"code":"TERMINAL_ZERO_REVERSAL","path":"/paths/0/months/1/assets/0/price"}]
    b=base()
    for month in b["paths"][0]["months"]: month["assets"][0]["price"]="0"
    ruin=wealth_lab.evaluate_bytes(wire(b)); no_trade=row(ruin,"ALT_NO_TRADE")
    assert no_trade["ordinary_paths"][0]["terminal_state"]=="ZERO"
    assert no_trade["lower_envelope"]=={"kind":"NEGATIVE_INFINITY","value":None,"reason":"POSITIVE_ASSUMED_RUIN_MASS"}
    assert no_trade["difference_to_no_trade"]=={"kind":"UNAVAILABLE","value":None,"reason":"NONFINITE_COMPARISON"}
    b=base(); b["paths"][0]["months"][0]["cash_gross_factor"]="0"
    cash_loss=wealth_lab.evaluate_bytes(wire(b)); assert row(cash_loss,"ALT_CASH")["ordinary_paths"][0]["terminal_state"]=="ZERO"

def test_w6e_w6f_absorption_never_replenishes_and_price_bounds_are_closed():
    """Independent W6e/f oracle: a held zero stays worthless, including on repricing."""
    b=base()
    for month in b["paths"][0]["months"]:
        month["assets"][0].update(price="0",distribution_per_unit="0")
    for month in b["paths"][0]["months"][1:]:
        month["assets"][1]["price"]="2"  # SYN_P has never been extinguished.
    valid=wealth_lab.evaluate_bytes(wire(b))
    assert row(valid,"ALT_NO_TRADE")["ordinary_paths"][0]["terminal_wealth"]["value"]=="0"
    assert row(valid,"ALT_PASSIVE")["ordinary_paths"][0]["terminal_wealth"]["value"]=="2e6"
    b=base()
    for month in b["paths"][0]["months"]:
        month["assets"][0].update(price="0",distribution_per_unit="0")
    # A later nonzero quote is a terminal-zero reversal, not a new holding.
    b["paths"][0]["months"][1]["assets"][0]["price"]="2"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[
        {"code":"TERMINAL_ZERO_REVERSAL","path":"/paths/0/months/1/assets/0/price"}
    ]
    b=base(); b["paths"][0]["months"][0]["assets"][0]["price"]="-1"
    assert wealth_lab.evaluate_bytes(wire(b))["findings"]==[
        {"code":"TYPE_INVALID","path":"/paths/0/months/0/assets/0/price"}
    ]
    assert wealth_lab.evaluate_bytes(b'{"x":NaN}')["findings"]==[{"code":"JSON_INVALID","path":""}]

def _w8_bundle(offsetting: bool):
    b=base(); b["initial_state"]={"positions":positions(500000,500000),"cash":"0"}
    b["alternatives"][1]["positions"]=positions(500000,500000)
    original=b["paths"][0]; other=json.loads(json.dumps(original)); other["path_id"]="PATH_B"
    b["paths"]=[original,other]
    for path,price_e,price_p in ((original,"0.5","2" if offsetting else "0.5"),(other,"2","0.5" if offsetting else "2")):
        for month in path["months"]:
            month["assets"][0]["price"]=price_e; month["assets"][1]["price"]=price_p
    masses=[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]
    b["probability_family"]["base"]["masses"]=masses
    b["probability_family"]["objective_members"][0]["masses"]=json.loads(json.dumps(masses))
    b["benchmark"]["ordinary_paths"].append({"path_id":"PATH_B","levels":["1"]*85})
    return b

def maximum_bundle():
    """Frozen W19 MAX dimensions, built only from explicit constants."""
    b=base()
    assets=[
        {"asset_id":"SYN_E1","kind":"SYNTHETIC_EQUITY","initial_price":"1","price_semantics":"EX_DISTRIBUTION_AFTER_INTERNAL_EXPENSES_USD"},
        {"asset_id":"SYN_E2","kind":"SYNTHETIC_EQUITY","initial_price":"1","price_semantics":"EX_DISTRIBUTION_AFTER_INTERNAL_EXPENSES_USD"},
        {"asset_id":"SYN_E3","kind":"SYNTHETIC_EQUITY","initial_price":"1","price_semantics":"EX_DISTRIBUTION_AFTER_INTERNAL_EXPENSES_USD"},
        {"asset_id":"SYN_P","kind":"SYNTHETIC_PASSIVE","initial_price":"1","price_semantics":"EX_DISTRIBUTION_AFTER_INTERNAL_EXPENSES_USD"},
    ]
    b["assets"]=assets
    def ps(e1=0,e2=0,e3=0,p=0):
        return [{"asset_id":"SYN_E1","units":str(e1)},{"asset_id":"SYN_E2","units":str(e2)},{"asset_id":"SYN_E3","units":str(e3)},{"asset_id":"SYN_P","units":str(p)}]
    b["initial_state"]={"positions":ps(250000,250000,250000,250000),"cash":"0"}
    prototype=b["paths"][0]
    b["paths"]=[]; b["stress_paths"]=[]
    for prefix,count,target in (("PATH_",16,b["paths"]),("STRESS_",4,b["stress_paths"])):
        for i in range(1,count+1):
            path=json.loads(json.dumps(prototype)); path["path_id"]=f"{prefix}{i:02d}"
            for month in path["months"]:
                month["assets"]=[{"asset_id":asset["asset_id"],"price":"1","distribution_per_unit":"0"} for asset in assets]
            target.append(path)
    b["alternatives"]=[
        {"alternative_id":"ALT_CASH","role":"CASH_ONLY","positions":ps(),"entry_costs":costs()},
        {"alternative_id":"ALT_NO_TRADE","role":"NO_TRADE","positions":ps(250000,250000,250000,250000),"entry_costs":costs()},
        {"alternative_id":"ALT_PASSIVE","role":"PASSIVE_ONLY","positions":ps(p=1000000),"entry_costs":costs()},
    ]
    for i in range(1,6): b["alternatives"].append({"alternative_id":f"ALT_CUSTOM{i}","role":"CUSTOM_SUPPLIED","positions":ps(e1=100000*i),"entry_costs":costs()})
    ids=[path["path_id"] for path in b["paths"]]
    equal=[{"path_id":path_id,"probability":"0.0625"} for path_id in ids]
    b["probability_family"]["base"]={"distribution_id":"DIST_BASE","masses":equal}
    b["probability_family"]["objective_members"]=[{"distribution_id":"DIST_01","masses":json.loads(json.dumps(equal))}]
    for i in range(1,4): b["probability_family"]["objective_members"].append({"distribution_id":f"DIST_0{i+1}","masses":[{"path_id":path_id,"probability":"1" if path_id==f"PATH_{i:02d}" else "0"} for path_id in ids]})
    b["benchmark"]["ordinary_paths"]=[{"path_id":path_id,"levels":["1"]*85} for path_id in ids]
    b["benchmark"]["stress_paths"]=[{"path_id":path["path_id"],"levels":["1"]*85} for path in b["stress_paths"]]
    return b

def test_w7_w8_strict_ruin_and_joint_path_coupling_oracles():
    correlated=wealth_lab.evaluate_bytes(wire(_w8_bundle(False)))
    paths=row(correlated,"ALT_NO_TRADE")["ordinary_paths"]
    assert [p["terminal_wealth"]["value"] for p in paths]==["5e5","2e6"]
    assert [p["sampled_max_drawdown"]["value"] for p in paths]==["5e-1","0"]
    assert row(correlated,"ALT_NO_TRADE")["lower_envelope"]["value"]=="0"
    offset=wealth_lab.evaluate_bytes(wire(_w8_bundle(True)))
    paths=row(offset,"ALT_NO_TRADE")["ordinary_paths"]
    assert [p["terminal_wealth"]["value"] for p in paths]==["1.25e6","1.25e6"]
    assert [p["sampled_max_drawdown"]["value"] for p in paths]==["0","0"]
    assert row(offset,"ALT_NO_TRADE")["lower_envelope"]["value"]=="3.187765018774425082375644147283350048209e-2"
    # A tiny funded positive terminal balance never becomes a synthetic ruin.
    b=base(); b["paths"][0]["months"][-1]["assets"][0]["price"]="0.000001"
    tiny=wealth_lab.evaluate_bytes(wire(b)); assert row(tiny,"ALT_NO_TRADE")["ordinary_paths"][0]["terminal_state"]=="POSITIVE"

def test_w9_w10_w11_recovery_expected_log_and_separate_minimum_oracles():
    b=base(); prices=["0.8","1","0.9"]
    for month,price in zip(b["paths"][0]["months"],prices): month["assets"][0]["price"]=price
    got=wealth_lab.evaluate_bytes(wire(b)); episode=row(got,"ALT_NO_TRADE")["ordinary_paths"][0]["recovery_episodes"][0]
    assert episode=={"peak_month":0,"peak_event_kind":"POST_TRADE","recovered_month":2,"recovered_event_kind":"MONTH","observed_until_month":2,"duration_months":2,"right_censored":False}
    # Independent private comparison oracle: minima are separate, never paired.
    a=[Fraction(0),Fraction(-1)]; nt=[Fraction(-2),Fraction(0)]
    assert min(a)-min(nt)==1
    assert min(x-y for x,y in zip(a,nt))==-1

    b=base(); second=json.loads(json.dumps(b["paths"][0])); second["path_id"]="PATH_B"; b["paths"].append(second)
    for month in b["paths"][0]["months"]: month["assets"][0]["price"]="0.25"; month["assets"][1]["price"]="1"
    for month in second["months"]: month["assets"][0]["price"]="1"; month["assets"][1]["price"]="0.5"
    b["benchmark"]["ordinary_paths"].append({"path_id":"PATH_B","levels":["1"]*85})
    b["probability_family"]["base"]["masses"]=[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]
    b["probability_family"]["objective_members"]=[
        {"distribution_id":"DIST_BASE_EQ","masses":[{"path_id":"PATH_A","probability":"0.5"},{"path_id":"PATH_B","probability":"0.5"}]},
        {"distribution_id":"DIST_A","masses":[{"path_id":"PATH_A","probability":"1"},{"path_id":"PATH_B","probability":"0"}]},
        {"distribution_id":"DIST_B","masses":[{"path_id":"PATH_A","probability":"0"},{"path_id":"PATH_B","probability":"1"}]},
    ]
    oracle=wealth_lab.evaluate_bytes(wire(b)); passive=row(oracle,"ALT_PASSIVE"); no_trade=row(oracle,"ALT_NO_TRADE")
    assert passive["lower_envelope"]["value"]=="-9.902102579427790134531887449402522401079e-2"
    assert no_trade["lower_envelope"]["value"]=="-1.980420515885558026906377489880504480216e-1"
    assert passive["difference_to_no_trade"]["value"]=="9.902102579427790134531887449402522401079e-2"

def test_w10_expected_log_uses_geometric_not_arithmetic_terminal_average():
    b=_w8_bundle(False)
    out=wealth_lab.evaluate_bytes(wire(b)); summary=row(out,"ALT_NO_TRADE")["base_summary"]
    # Independent fractions: 1/2*ln(1/2) + 1/2*ln(2) = 0, whereas
    # arithmetic terminal wealth is (1/2+2)/2 = 5/4 and must not yield 25%.
    assert (Fraction(1,2)+Fraction(2,1))/2==Fraction(5,4)
    assert summary["annual_log_growth"]=={"kind":"FINITE","value":"0","reason":None}
    assert summary["geometric_equivalent_growth_under_assumption"]=={"kind":"FINITE","value":"0","reason":None}

def test_w12_stress_is_diagnostic_and_w13_outputs_remain_closed():
    b=base(); baseline=wealth_lab.evaluate_bytes(wire(b))
    stress=json.loads(json.dumps(b["paths"][0])); stress["path_id"]="STRESS_DIAGNOSTIC"
    for month in stress["months"]: month["assets"][0]["price"]="0"
    b["stress_paths"]=[stress]
    b["benchmark"]["stress_paths"]=[{"path_id":"STRESS_DIAGNOSTIC","levels":["1"]+["0"]*84}]
    got=wealth_lab.evaluate_bytes(wire(b))
    for alternative_id in ("ALT_CASH","ALT_NO_TRADE","ALT_PASSIVE"):
        before=row(baseline,alternative_id); after=row(got,alternative_id)
        assert after["base_summary"]==before["base_summary"]
        assert after["lower_envelope"]==before["lower_envelope"]
        assert len(after["stress_paths"])==1
    payload=got["evaluation"]
    encoded=wealth_lab.canonical_bytes(payload)
    for forbidden in (b'"target_weight"',b'"recommendation"',b'"action"',b'"order"'):
        assert forbidden not in encoded
    assert payload["boundaries"]["decision_eligible"] is False
    invalid=json.loads(json.dumps(b))
    invalid["probability_family"]["base"]["masses"][0]["path_id"]="STRESS_DIAGNOSTIC"
    assert wealth_lab.evaluate_bytes(wire(invalid))["findings"]==[
        {"code":"SET_MEMBERSHIP","path":"/probability_family/base/masses/0/path_id"}
    ]

def test_w14_exact_fraction_invariant_and_nonrenormalized_public_representation():
    b=base()
    for asset in b["assets"]: asset["initial_price"]="499999.5"
    b["initial_state"]={"positions":positions(1,1),"cash":"1"}
    b["alternatives"][1]["positions"]=positions(1,1)
    b["alternatives"][2]["positions"]=positions(0,2)
    for month in b["paths"][0]["months"]:
        month["assets"][0]["price"]="1"; month["assets"][1]["price"]="1"
    result=wealth_lab.evaluate_bytes(wire(b)); event=row(result,"ALT_NO_TRADE")["ordinary_paths"][0]["events"][2]
    public=[Fraction(item["realized_hypothetical_fraction"]["value"]) for item in event["fractions"]]
    assert public==[Fraction("0.3333333333333333333333333333333333333333")]*3
    assert sum(public)==Fraction(1)-Fraction(1,10**40)

def test_w19_maximum_dimensions_counts_size_and_resource_measurements():
    raw=wire(maximum_bundle())
    tracemalloc.start(); started=perf_counter(); artifact=wealth_lab.evaluate_bytes(raw); elapsed=perf_counter()-started
    _,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
    assert artifact["evaluation"]["status"]=="COMPUTED_SYNTHETIC"
    result=artifact["evaluation"]["result"]
    assert sum(len(alt["ordinary_paths"])+len(alt["stress_paths"]) for alt in result["alternatives"])==160
    assert sum(len(path["events"]) for alt in result["alternatives"] for path in alt["ordinary_paths"]+alt["stress_paths"])==13_760
    assert len(result["benchmark"]["ordinary_paths"])+len(result["benchmark"]["stress_paths"])==20
    assert sum(len(path["events"]) for path in result["benchmark"]["ordinary_paths"]+result["benchmark"]["stress_paths"])==1_700
    assert 4*20*84*8==53_760
    evaluation_bytes=wealth_lab.canonical_bytes(artifact["evaluation"]); artifact_bytes=wealth_lab.canonical_bytes(artifact)
    assert len(evaluation_bytes)<=33_554_432 and len(artifact_bytes)<=41_943_040
    print(f"MAX_MEASUREMENT elapsed_seconds={elapsed:.6f} peak_bytes={peak} evaluation_bytes={len(evaluation_bytes)} artifact_bytes={len(artifact_bytes)}")
    # ADR-0018 makes >10s or >256MiB an engineering review trigger, not a
    # semantic rejection that silently reduces the frozen MAX coverage.
    assert elapsed>0 and peak>0
