from __future__ import annotations
import json
from tests.test_phase1 import migrated_client, close_client
from optivest.risk_editor import template
from optivest.risk_editor import EditorError, declaration_changes, diagnostics, validate_declaration
from copy import deepcopy
import pytest

def modern(head, mandate, declaration):
    return {"request_kind":"FULL_DECLARATION","schema_version":"RESEARCH_RISK_EDITOR_V1","expected_current_version_id":head,"mandate_version_id":mandate,"rationale":"offline research declaration","declaration":declaration}

def test_editor_template_preview_save_history_and_immutable_document():
    d,c,_=migrated_client()
    try:
        status=c.get("/api/v1/status").json(); payload=modern(status["risk_budget_version_id"],status["mandate_version_id"],template())
        preview=c.post("/api/v1/risk-budgets/preview",content=json.dumps(payload),headers={"content-type":"application/json"})
        assert preview.status_code==200 and preview.json()["diagnostics"]["production_readiness"]=="NOT PRODUCTION READY"
        saved=c.post("/api/v1/risk-budgets/versions",content=json.dumps(payload),headers={"content-type":"application/json"})
        assert saved.status_code==201, saved.text
        value=saved.json(); assert value["editor_document_status"]=="V1" and len(value["constraints"])==19
        current=c.get("/api/v1/risk-budgets/current").json(); assert current["id"]==value["id"]
        history=c.get("/api/v1/risk-budgets/versions").json(); assert len(history["items"])==2
        with c.app.state.engine.begin() as conn:
            import pytest
            with pytest.raises(Exception): conn.exec_driver_sql("UPDATE research_risk_editor_documents SET canonical_document='{}'")
    finally: close_client(c)

def test_editor_rejects_duplicate_keys_and_contradiction_without_head_change():
    d,c,_=migrated_client()
    try:
        st=c.get("/api/v1/status").json(); raw=(b'{"expected_current_version_id":"'+st["risk_budget_version_id"].encode()+b'","expected_current_version_id":"x"}')
        assert c.post("/api/v1/risk-budgets/preview",content=raw,headers={"content-type":"application/json"}).status_code==422
        payload=modern(st["risk_budget_version_id"],st["mandate_version_id"],template())
        payload["declaration"]["constraints"][0]["warning"]={"value":"99","reason":None}
        result=c.post("/api/v1/risk-budgets/versions",content=json.dumps(payload),headers={"content-type":"application/json"})
        assert result.status_code==422
        assert c.get("/api/v1/status").json()["risk_budget_version_id"]==st["risk_budget_version_id"]
    finally: close_client(c)

@pytest.mark.parametrize("case",["chance_forbidden","unspecified_value","epsilon_range","stress_role","hybrid_range","joint","row16_horizon","component_unit","text_type"])
def test_editor_rejects_remaining_closed_preview_matrix(case):
    d,c,_=migrated_client()
    try:
        st=c.get("/api/v1/status").json(); declaration=template()
        row=lambda metric:next(x for x in declaration["constraints"] if x["metric"]==metric)
        if case=="chance_forbidden":
            r=row("MAX_MODELED_DRAWDOWN")["risk"];r["mode"]="ROBUST_CHANCE";r["alpha"]["reason"]="SEMANTICS_NOT_VERIFIED"
        elif case=="unspecified_value": row("MAX_MODELED_DRAWDOWN")["risk"]["epsilon"]={"value":"0.1","reason":None}
        elif case=="epsilon_range":
            r=row("MAX_MODELED_DRAWDOWN")["risk"];r["mode"]="ROBUST_CHANCE";r["epsilon"]={"value":"2","reason":None};r["u_risk_version"]={"value":"u","reason":None};r["calibration_reference"]={"value":"c","reason":None};r["alpha"]={"value":None,"reason":"NOT_APPLICABLE"};r["buffer_value"]={"value":None,"reason":"NOT_APPLICABLE"};r["buffer_rationale"]={"value":None,"reason":"NOT_APPLICABLE"}
        elif case=="stress_role":row("MAX_STRESS_DRAWDOWN")["stress"]["proposed_role"]="ALIEN"
        elif case=="hybrid_range":row("MAX_DAYS_TO_LIQUIDATE")["hybrid"]["participation_assumption"]={"value":"101","reason":None}
        elif case=="joint":declaration["joint_groups"]=[{"group_id":"x","members":["UNKNOWN","PORTFOLIO_JOINT_MATERIAL_RISK","UNKNOWN"],"horizon":{"value":None,"reason":"x"},"epsilon":{"value":"2","reason":None},"u_risk_version":{"value":None,"reason":"x"},"dependency_method":{"value":None,"reason":"x"},"dependency_reference":{"value":None,"reason":"x"}}]
        elif case=="row16_horizon":row("MAX_TURNOVER_IMPLEMENTATION_COST")["horizon"]={"value":{"kind":"FIXED_PERIOD","unit":"YEARS","count":7,"event_clock":"DECISION_TO_HORIZON"},"reason":None}
        elif case=="component_unit":
            x=row("MAX_TURNOVER_IMPLEMENTATION_COST")["components"][0];x["unit"]={"value":"MONTHS","reason":None};x["limit"]={"value":"1","reason":None}
        else:row("MAX_SINGLE_NAME_EQUITY")["definition"]={"value":123,"reason":None}
        response=c.post("/api/v1/risk-budgets/preview",content=json.dumps(modern(st["risk_budget_version_id"],st["mandate_version_id"],declaration)),headers={"content-type":"application/json"})
        assert response.status_code==422,response.text
    finally:close_client(c)

@pytest.mark.parametrize("case",["row1_clock","row16_component_clock","percent_currency","currency_reason","blank_text","numeric_component_text","joint_duplicate","joint_reuse"])
def test_final_closed_declaration_regressions(case):
    declaration=template(); row=lambda metric:next(x for x in declaration["constraints"] if x["metric"]==metric)
    if case=="row1_clock": row("MAX_SINGLE_NAME_EQUITY")["horizon"]["value"]["event_clock"]="STRESS_SCENARIO_PATH"
    elif case=="row16_component_clock":
        row("MAX_TURNOVER_IMPLEMENTATION_COST")["components"][0]["horizon"]={"value":{"kind":"OBSERVATION","unit":None,"count":None,"event_clock":"ALWAYS"},"reason":None}
    elif case=="percent_currency": row("MAX_SINGLE_NAME_EQUITY")["currency"]={"value":"USD","reason":None}
    elif case=="currency_reason":
        r=row("MIN_LIQUIDITY");r["unit"]={"value":"CURRENCY","reason":None};r["currency"]={"value":None,"reason":"NOT_APPLICABLE"}
    elif case=="blank_text": row("MAX_SINGLE_NAME_EQUITY")["definition"]={"value":"  ","reason":None}
    elif case=="numeric_component_text": row("MAX_TURNOVER_IMPLEMENTATION_COST")["components"][0]["definition"]={"value":1,"reason":None}
    elif case=="joint_duplicate":
        joint={"group_id":"same","members":["MAX_MODELED_DRAWDOWN"],"horizon":{"value":None,"reason":"x"},"epsilon":{"value":None,"reason":"x"},"u_risk_version":{"value":None,"reason":"x"},"dependency_method":{"value":None,"reason":"x"},"dependency_reference":{"value":None,"reason":"x"}};declaration["joint_groups"]=[joint,{**joint}]
    else:
        joint={"group_id":"one","members":["MAX_MODELED_DRAWDOWN"],"horizon":{"value":None,"reason":"x"},"epsilon":{"value":None,"reason":"x"},"u_risk_version":{"value":None,"reason":"x"},"dependency_method":{"value":None,"reason":"x"},"dependency_reference":{"value":None,"reason":"x"}};declaration["joint_groups"]=[joint,{**joint,"group_id":"two"}]
    with pytest.raises(EditorError):validate_declaration(declaration)

def test_final_diagnostics_and_difference_regressions():
    declaration=template(); row=lambda metric:next(x for x in declaration["constraints"] if x["metric"]==metric)
    r=row("MAX_MODELED_DRAWDOWN");r["risk"].update(mode="ROBUST_CHANCE",epsilon={"value":None,"reason":"x"},u_risk_version={"value":"u","reason":None},calibration_reference={"value":"c","reason":None},alpha={"value":None,"reason":"NOT_APPLICABLE"},buffer_value={"value":None,"reason":"NOT_APPLICABLE"},buffer_rationale={"value":None,"reason":"NOT_APPLICABLE"})
    stress=row("MAX_STRESS_DRAWDOWN");stress["stress"]["proposed_role"]="BINDING";stress["stress"]["version"]={"value":None,"reason":"x"}
    declaration["joint_groups"]=[{"group_id":"z","members":["MAX_MODELED_DRAWDOWN"],"horizon":{"value":None,"reason":"x"},"epsilon":{"value":None,"reason":"x"},"u_risk_version":{"value":None,"reason":"x"},"dependency_method":{"value":None,"reason":"x"},"dependency_reference":{"value":None,"reason":"x"}}]
    blockers=diagnostics(declaration,7)["blockers"]
    assert {"RISK_SEMANTICS_INCOMPLETE","STRESS_SEMANTICS_INCOMPLETE","JOINT_DEFINITION_INCOMPLETE","JOINT_RISK_NOT_VERIFIED"} <= set(blockers)
    before=template();after=template();row_before=lambda metric:next(x for x in before["constraints"] if x["metric"]==metric);row_after=lambda metric:next(x for x in after["constraints"] if x["metric"]==metric)
    row_before("MIN_LIQUIDITY")["limit"]={"value":"1","reason":None};row_after("MIN_LIQUIDITY")["limit"]={"value":"2","reason":None}; assert next(x for x in declaration_changes(before,after) if x["path"].endswith("/limit/value"))["comparison"]=="TIGHTER"

def test_canonical_joint_members_and_directional_comparison_identity_rules():
    declaration=template()
    declaration["joint_groups"]=[{"group_id":"z","members":["MAX_RECOVERY_DURATION","MAX_MODELED_DRAWDOWN"],"horizon":{"value":None,"reason":"x"},"epsilon":{"value":None,"reason":"x"},"u_risk_version":{"value":None,"reason":"x"},"dependency_method":{"value":None,"reason":"x"},"dependency_reference":{"value":None,"reason":"x"}}]
    normalized=validate_declaration(declaration)
    assert normalized["joint_groups"][0]["members"]==["MAX_MODELED_DRAWDOWN","MAX_RECOVERY_DURATION"]
    before=template(); after=template()
    row=lambda d,metric:next(x for x in d["constraints"] if x["metric"]==metric)
    row(before,"PASSIVE_MARKET_IMPLEMENTATION")["minimum"]={"value":"0","reason":None}
    row(after,"PASSIVE_MARKET_IMPLEMENTATION")["minimum"]={"value":"1","reason":None}
    row(before,"MAX_SINGLE_NAME_EQUITY")["warning"]={"value":"5","reason":None}
    row(after,"MAX_SINGLE_NAME_EQUITY")["warning"]={"value":"6","reason":None}
    changes=declaration_changes(before,after)
    assert next(x for x in changes if x["path"].endswith("/minimum/value"))["comparison"]=="TIGHTER"
    assert next(x for x in changes if x["path"].endswith("/warning/value"))["comparison"]=="LOOSER"
    row(after,"MAX_SINGLE_NAME_EQUITY")["definition"]={"value":"different declaration","reason":None}
    changed=declaration_changes(before,after)
    assert next(x for x in changed if x["path"].endswith("/warning/value"))["comparison"]=="NOT_COMPARABLE"

def test_verifier_rejects_legacy_catalog_and_exact_trigger_replacement():
    d,c,_=migrated_client()
    try:
        with c.app.state.engine.begin() as conn:
            conn.exec_driver_sql("DROP TRIGGER trg_risk_constraints_no_update")
            conn.exec_driver_sql("UPDATE risk_constraints SET metric='UNKNOWN_METRIC' WHERE metric='MAX_SINGLE_NAME_EQUITY'")
            conn.exec_driver_sql("CREATE TRIGGER trg_risk_constraints_no_update BEFORE UPDATE ON risk_constraints BEGIN SELECT RAISE(ABORT, 'immutable risk_constraints'); END")
        assert c.get("/api/v1/status").status_code==503
    finally: close_client(c)
    d,c,_=migrated_client()
    try:
        with c.app.state.engine.begin() as conn:
            conn.exec_driver_sql("DROP TRIGGER trg_research_risk_editor_documents_update")
            conn.exec_driver_sql("CREATE TRIGGER trg_research_risk_editor_documents_update BEFORE UPDATE ON research_risk_editor_documents BEGIN SELECT 1; END")
        assert c.get("/api/v1/status").status_code==503
    finally: close_client(c)

@pytest.mark.parametrize("mutation",["zero_duration","component_percent","minimum_reason","aggregate","confidence","identifier"])
def test_t1_frozen_value_grammar_counterexamples(mutation):
    declaration=template(); row=lambda metric:next(x for x in declaration["constraints"] if x["metric"]==metric)
    if mutation=="zero_duration": row("MAX_RECOVERY_DURATION")["limit"]={"value":"0","reason":None}
    elif mutation=="component_percent":
        component=row("MAX_TURNOVER_IMPLEMENTATION_COST")["components"][0];component["unit"]={"value":"PERCENT","reason":None};component["limit"]={"value":"101","reason":None}
    elif mutation=="minimum_reason": row("MAX_SINGLE_NAME_EQUITY")["minimum"]={"value":None,"reason":"ARBITRARY"}
    elif mutation=="aggregate": row("MAX_TURNOVER_IMPLEMENTATION_COST")["definition"]={"value":"editable","reason":None}
    elif mutation=="confidence": row("MAX_SINGLE_NAME_EQUITY")["confidence_level"]={"value":"2","reason":None}
    else:
        risk=row("MAX_MODELED_DRAWDOWN")["risk"];risk["mode"]="ROBUST_CHANCE";risk["epsilon"]={"value":"0.1","reason":None};risk["u_risk_version"]={"value":"x"*129,"reason":None};risk["calibration_reference"]={"value":"c","reason":None};risk["alpha"]={"value":None,"reason":"NOT_APPLICABLE"};risk["buffer_value"]={"value":None,"reason":"NOT_APPLICABLE"};risk["buffer_rationale"]={"value":None,"reason":"NOT_APPLICABLE"}
    with pytest.raises(EditorError): validate_declaration(declaration)

def test_t1_text_is_trimmed_and_t2_findings_are_complete_and_catalog_ordered():
    declaration=template(); row=lambda metric:next(x for x in declaration["constraints"] if x["metric"]==metric)
    row("MAX_SINGLE_NAME_EQUITY")["definition"]={"value":"  exact definition  ","reason":None}
    risk=row("MAX_MODELED_DRAWDOWN")["risk"];risk.update(mode="ROBUST_CHANCE",epsilon={"value":None,"reason":"missing"},u_risk_version={"value":" u1 ","reason":None},calibration_reference={"value":" c1 ","reason":None},alpha={"value":None,"reason":"NOT_APPLICABLE"},buffer_value={"value":None,"reason":"NOT_APPLICABLE"},buffer_rationale={"value":None,"reason":"NOT_APPLICABLE"})
    declaration["joint_groups"]=[{"group_id":" joint ","members":["MAX_MODELED_DRAWDOWN","MAX_RECOVERY_DURATION"],"horizon":{"value":{"kind":"FIXED_PERIOD","unit":"YEARS","count":6,"event_clock":"DECISION_TO_HORIZON"},"reason":None},"epsilon":{"value":"0.1","reason":None},"u_risk_version":{"value":"u","reason":None},"dependency_method":{"value":"joint","reason":None},"dependency_reference":{"value":"ref","reason":None}}]
    normalized=validate_declaration(declaration); assert row("MAX_SINGLE_NAME_EQUITY")["definition"]["value"]=="exact definition" and normalized["joint_groups"][0]["group_id"]=="joint"
    result=diagnostics(normalized,7)
    assert "JOINT_HORIZON_CONTRADICTION" in {x["code"] for x in result["findings"] if x["severity"]=="ERROR"}
    assert set(result["blockers"])=={x["code"] for x in result["findings"] if x["severity"]=="BLOCKER"}|{"RISK_BUDGET_INCONSISTENT"}
    paths=[x["path"] for x in result["findings"] if x["severity"]=="BLOCKER" and "/constraints/" in x["path"]]
    ordinals=[int(path.split("/constraints/")[1].split("/")[0]) for path in paths];assert ordinals==sorted(ordinals)

def test_t1_api_typing_encoding_media_missing_version_and_z_timestamp():
    _,c,_=migrated_client()
    try:
        st=c.get("/api/v1/status").json(); payload=modern(st["risk_budget_version_id"],st["mandate_version_id"],template())
        payload["expected_current_version_id"]=7
        assert c.post("/api/v1/risk-budgets/preview",content=json.dumps(payload),headers={"content-type":"application/json"}).status_code==422
        bad=c.post("/api/v1/risk-budgets/preview",content=b"\xff",headers={"content-type":"application/json"});assert bad.status_code==422 and bad.json()["error"]["code"]=="JSON_ENCODING"
        payload["expected_current_version_id"]=st["risk_budget_version_id"]
        good=c.post("/api/v1/risk-budgets/preview",content=json.dumps(payload),headers={"content-type":"application/json;charset=utf-8"});assert good.status_code==200,good.text
        missing=c.get("/api/v1/risk-budgets/versions/missing");assert missing.status_code==404 and missing.json()["error"]["code"]=="VERSION_NOT_FOUND"
        assert c.get("/api/v1/risk-budgets/current").json()["created_at"].endswith("Z")
    finally:close_client(c)

@pytest.mark.parametrize("case",["risk","stress","hybrid"])
def test_reserved_not_applicable_reason_is_rejected_for_applicable_wrappers(case):
    declaration=template(); row=lambda metric:next(x for x in declaration["constraints"] if x["metric"]==metric)
    if case=="risk":
        wrapper=row("MAX_MODELED_DRAWDOWN")["risk"]
        wrapper.update(mode="ROBUST_CHANCE",epsilon={"value":None,"reason":"NOT_APPLICABLE"},u_risk_version={"value":"u","reason":None},calibration_reference={"value":"c","reason":None},alpha={"value":None,"reason":"NOT_APPLICABLE"},buffer_value={"value":None,"reason":"NOT_APPLICABLE"},buffer_rationale={"value":None,"reason":"NOT_APPLICABLE"})
    elif case=="stress":
        wrapper=row("MAX_STRESS_DRAWDOWN")["stress"]
        wrapper.update(proposed_role="BINDING",version={"value":None,"reason":"NOT_APPLICABLE"})
    else:
        row("MAX_FACTOR_CLUSTER")["hybrid"]["observed_component"]={"value":None,"reason":"NOT_APPLICABLE"}
    with pytest.raises(EditorError) as error: validate_declaration(declaration)
    assert error.value.code=="FIELD_NOT_APPLICABLE"
    _,client,_=migrated_client()
    try:
        status=client.get("/api/v1/status").json()
        response=client.post("/api/v1/risk-budgets/preview",content=json.dumps(modern(status["risk_budget_version_id"],status["mandate_version_id"],declaration)),headers={"content-type":"application/json"})
        assert response.status_code==422,response.text
        assert response.json()["error"]["code"]=="FIELD_NOT_APPLICABLE"
    finally: close_client(client)

def test_structured_editor_route_has_reachable_assets_without_raw_json_textarea():
    _,c,_=migrated_client()
    try:
        page=c.get("/risk-budget");assert page.status_code==200 and 'id="rows"' in page.text and '<textarea' not in page.text
        assert page.text.count("<input")>=20 and 'id="initial-structured-controls"' in page.text
        script=c.get("/risk-budget/editor.js");assert script.status_code==200 and "renderRow" in script.text and "MAX_TURNOVER_IMPLEMENTATION_COST" in script.text
        css=c.get("/risk-budget/editor.css");assert css.status_code==200 and "overflow-wrap:anywhere" in css.text and "min-width:0" in css.text
    finally:close_client(c)
