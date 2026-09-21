"""Stateless synthetic wealth-accounting laboratory (RESEARCH-WEALTH-LAB-V1).

This module deliberately has no database, provider, or investment-decision
dependency.  It accepts raw JSON bytes only and reports supplied hypothetical
accounting paths; it does not forecast, optimize, or recommend anything.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext, InvalidOperation
from fractions import Fraction
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
import json
import math
import os
import platform
import re
import subprocess
from typing import Any

POLICY_HASH = "acf013ce46f450423d83deeBA1c207b22c669670c2b9bdc83a8a665f5ad38e67".lower()
DESIGN_HASH = "4097f897073e681abab4b5535eaa81ed38f32f2a9bae72b49c672b6fff74b80c"
SCHEMA = "RESEARCH_WEALTH_LAB_V1"
METHOD = "RATIONAL_LEDGER_DECIMAL_LOG_V1"
CANON = "WLAB_CANONICAL_JSON_V1"
ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT = 4_194_304
MAX_EVALUATION = 33_554_432
MAX_ARTIFACT = 41_943_040
DECIMAL_RE = re.compile(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,6})?$")
ID_RE = re.compile(r"[A-Z][A-Z0-9_]{0,31}$")
MANIFEST = (
    "optivest/__init__.py", "optivest/wealth_lab.py", "optivest/wealth_lab_api.py",
    "optivest/app.py", "optivest/cli.py", "optivest/static/wealth_lab.js",
    "optivest/static/wealth_lab.css", "optivest/fixtures/wealth_lab_example.json",
    "pyproject.toml", "uv.lock",
)
_LOADED_SOURCE_HASHES: dict[str, str] | None = None
BOUNDARIES = {"mode":"SYNTHETIC_ACCOUNTING_LAB","investment_model":"NOT VERIFIED",
    "risk_feasibility":"NOT VERIFIED","decision_eligible":False,"production_eligible":False,
    "risk_budget":"RISK BUDGET NOT APPROVED","provider_pit":"NOT VERIFIED",
    "calibration":"NOT VERIFIED","oos":"NOT VERIFIED","shadow":"SHADOW VALIDATION NOT PASSED",
    "production_readiness":"NOT PRODUCTION READY"}
UNAVAILABLE = [
    ("ECONOMIC_RETURN_BRIDGE","ECONOMIC_RETURN_BRIDGE_NOT_IMPLEMENTED"),("HIERARCHICAL_PRIOR","HIERARCHICAL_PRIOR_NOT_IMPLEMENTED"),("FORECAST_CALIBRATION","FORECAST_CALIBRATION_NOT_IMPLEMENTED"),("U_OBJECTIVE_CALIBRATION","U_OBJECTIVE_CALIBRATION_NOT_IMPLEMENTED"),("U_RISK","U_RISK_NOT_IMPLEMENTED"),("BINDING_STRESS","BINDING_STRESS_NOT_IMPLEMENTED"),("PERMANENT_LOSS","PERMANENT_LOSS_NOT_IMPLEMENTED"),("CVAR_AND_JOINT_RISK","CVAR_AND_JOINT_RISK_NOT_IMPLEMENTED"),("LIQUIDITY_AND_LOOK_THROUGH","LIQUIDITY_AND_LOOK_THROUGH_NOT_IMPLEMENTED"),("OPTIMIZER","OPTIMIZER_NOT_IMPLEMENTED"),("CANONICAL_DECISION_HURDLE","CANONICAL_DECISION_HURDLE_NOT_IMPLEMENTED"),("PERSONALIZATION","PERSONALIZATION_NOT_IMPLEMENTED"),("REAL_ELIGIBLE_BENCHMARK","REAL_COMPARATOR_UNVERIFIED"),("APPROVED_PASSIVE_IMPLEMENTATION","PASSIVE_CANDIDATE_UNVERIFIED"),("RISK_FREE_PROXY","NO_APPROVED_RISK_FREE_PROXY")]
LEDGER_ROWS = {
    "JOINT_PATH_HYPOTHESIS":("PREDICTIVE_DISTRIBUTION","SUPPLIED_JOINT_PATHS_AND_BASE_MASSES","SYNTHETIC_NOT_CALIBRATED"),
    "MASS_FAMILY_HYPOTHESIS":("OBJECTIVE_DIAGNOSTIC","SUPPLIED_MASS_FAMILY_LOWER_ENVELOPE","SYNTHETIC_NOT_CALIBRATED"),
    "STRESS_HYPOTHESIS":("STRESS_DIAGNOSTIC","SEPARATE_UNWEIGHTED_PATHS","SYNTHETIC_NOT_CALIBRATED"),
    "ECONOMIC_AND_PRIOR_FORECAST":("FORECAST_AND_SHRINKAGE","DEFERRED","NOT_VERIFIED"),
    "RISK_AMBIGUITY":("U_RISK","DEFERRED","NOT_VERIFIED"),
    "RESIDUAL_DECISION_ERROR":("DECISION_MARGIN","DEFERRED","NOT_VERIFIED"),
    "OPTIONAL_SIZING":("SIZING_ADJUSTMENT","DISABLED","NOT_VERIFIED"),
}

class LabError(Exception):
    def __init__(self, code: str, path: str="", status: str="INVALID_INPUT", hashed: bool=False):
        self.code, self.path, self.status, self.hashed = code, path, status, hashed

def canonical_bytes(value: Any) -> bytes:
    """WLAB_CANONICAL_JSON_V1 for already-normalized JSON primitives."""
    def esc(s: str) -> str:
        out=[]
        for c in s:
            o=ord(c)
            if c=='"': out.append('\\"')
            elif c=='\\': out.append('\\\\')
            elif o <= 0x1f: out.append(f"\\u{o:04x}")
            else: out.append(c)
        return '"'+''.join(out)+'"'
    def enc(v: Any) -> str:
        if v is None: return "null"
        if v is True: return "true"
        if v is False: return "false"
        if type(v) is int: return str(v)
        if type(v) is str: return esc(v)
        if isinstance(v, list): return '['+','.join(enc(x) for x in v)+']'
        if isinstance(v, dict): return '{'+','.join(esc(k)+':'+enc(v[k]) for k in sorted(v))+ '}'
        raise TypeError("canonical JSON only accepts normalized primitives")
    return enc(value).encode("utf-8")

def _n(value: Fraction | None, reason: str | None=None, negative: bool=False) -> dict[str, Any]:
    if reason:
        return {"kind":"NEGATIVE_INFINITY" if negative else "UNAVAILABLE","value":None,"reason":reason}
    assert value is not None
    return {"kind":"FINITE","value":_render(value),"reason":None}

def _render(value: Fraction) -> str:
    if value == 0: return "0"
    with localcontext() as c:
        c.prec=80; c.rounding=ROUND_HALF_EVEN; c.Emin=-999999; c.Emax=999999
        x=Decimal(value.numerator)/Decimal(value.denominator)
        adj=x.adjusted(); mant=(x.scaleb(-adj)).quantize(Decimal(1).scaleb(-39))
        if abs(mant)==Decimal(10): mant=Decimal(1); adj+=1
        s=format(mant,"f").rstrip("0").rstrip(".")
        return f"{s}e{adj}"

def _d(value: Any, path: str, allow_missing: bool=True) -> Fraction | dict[str,str]:
    if isinstance(value, dict):
        if set(value)!={"state","reason"} or value.get("state") not in {"MISSING","UNKNOWN","STALE","CONFLICTING","UNAVAILABLE_PIT","NOT_APPLICABLE"} or not isinstance(value.get("reason"),str) or not value["reason"].strip():
            raise LabError("TYPE_INVALID",path)
        if value["state"]=="NOT_APPLICABLE": raise LabError("FIELD_NOT_APPLICABLE",path)
        return value
    if not isinstance(value,str) or not DECIMAL_RE.fullmatch(value): raise LabError("TYPE_INVALID",path)
    return Fraction(value)

def _normal_decimal(value: Any, path: str) -> str:
    x=_d(value,path)
    if isinstance(x,dict): return value
    # D has at most six fractional digits.  Normalize only the fractional
    # suffix: stripping all trailing zeroes would corrupt integers such as 20.
    s=format(Decimal(x.numerator)/Decimal(x.denominator),"f")
    if "." in s:
        s=s.rstrip("0").rstrip(".")
    return s or "0"

def _pointer_join(base: str, part: str) -> str: return base+"/"+part.replace("~","~0").replace("/","~1")

def _decode(raw: bytes) -> Any:
    if not isinstance(raw, bytes): raise LabError("TYPE_INVALID","")
    if len(raw)>MAX_INPUT: raise LabError("JSON_SIZE","")
    if raw.startswith(b"\xef\xbb\xbf"): raise LabError("JSON_ENCODING","")
    try: text=raw.decode("utf-8")
    except UnicodeDecodeError: raise LabError("JSON_ENCODING","")
    if any(0xD800<=ord(ch)<=0xDFFF for ch in text): raise LabError("JSON_ENCODING","")
    depth,nodes=_lexical_shape(text)
    if depth>16: raise LabError("JSON_DEPTH","")
    if nodes>100000: raise LabError("JSON_NODES","")
    try: value=json.loads(text, parse_constant=lambda _ : (_ for _ in ()).throw(ValueError()))
    except (json.JSONDecodeError, ValueError): raise LabError("JSON_INVALID","")
    def reject_surrogates(v: Any) -> None:
        if isinstance(v,str) and any(0xD800<=ord(ch)<=0xDFFF for ch in v):
            raise LabError("JSON_ENCODING","")
        if isinstance(v,dict):
            for key,item in v.items(): reject_surrogates(key);reject_surrogates(item)
        elif isinstance(v,list):
            for item in v: reject_surrogates(item)
    reject_surrogates(value)
    duplicate=_duplicate_pointer(text)
    if duplicate is not None: raise LabError("JSON_INVALID",duplicate)
    return value

def _lexical_shape(text: str) -> tuple[int,int]:
    """Validate JSON lexically and count semantic depth/nodes before building it.

    Object keys are syntax but not nodes.  We deliberately finish the bounded
    scan before selecting an error so JSON_DEPTH has global precedence over
    JSON_NODES when both limits are exceeded.
    """
    n=len(text); i=0; nodes=0; maximum=0
    def ws() -> None:
        nonlocal i
        while i<n and text[i] in " \t\r\n": i+=1
    def string() -> None:
        nonlocal i
        if i>=n or text[i]!='"': raise ValueError
        i+=1
        while i<n:
            c=text[i];i+=1
            if c=='"': return
            if ord(c)<0x20: raise ValueError
            if c=='\\':
                if i>=n or text[i] not in '"\\/bfnrtu': raise ValueError
                esc=text[i];i+=1
                if esc=='u':
                    if i+4>n or any(ch not in "0123456789abcdefABCDEF" for ch in text[i:i+4]): raise ValueError
                    i+=4
        raise ValueError
    def scalar() -> None:
        nonlocal i
        if i<n and text[i]=='"': string();return
        decoder=json.JSONDecoder(parse_constant=lambda _ : (_ for _ in ()).throw(ValueError()))
        value,end=decoder.raw_decode(text,i)
        if isinstance(value,(dict,list)): raise ValueError
        i=end
    def value(depth:int) -> None:
        nonlocal i,nodes,maximum
        if depth>16: raise LabError("JSON_DEPTH","")
        ws(); nodes+=1; maximum=max(maximum,depth)
        if i>=n: raise ValueError
        if text[i]=='{':
            i+=1;ws()
            if i<n and text[i]=='}':i+=1;return
            while True:
                string();ws()
                if i>=n or text[i]!=':':raise ValueError
                i+=1;value(depth+1);ws()
                if i<n and text[i]=='}':i+=1;return
                if i>=n or text[i]!=',':raise ValueError
                i+=1;ws()
        elif text[i]=='[':
            i+=1;ws()
            if i<n and text[i]==']':i+=1;return
            while True:
                value(depth+1);ws()
                if i<n and text[i]==']':i+=1;return
                if i>=n or text[i]!=',':raise ValueError
                i+=1
        else: scalar()
    try:
        value(0);ws()
        if i!=n:raise ValueError
    except (ValueError,json.JSONDecodeError):
        raise LabError("JSON_INVALID","")
    return maximum,nodes

def _duplicate_pointer(text: str) -> str | None:
    """First duplicate member in wire order, with an RFC-6901 path."""
    decoder=json.JSONDecoder(); limit=len(text)
    def ws(i:int)->int:
        while i<limit and text[i] in " \t\r\n": i+=1
        return i
    def string(i:int)->tuple[str,int]:
        value,end=decoder.raw_decode(text,i)
        if not isinstance(value,str): raise ValueError
        return value,end
    def val(i:int,path:str)->tuple[int,str|None]:
        i=ws(i)
        if text[i]=='{':
            i=ws(i+1); seen=set()
            if text[i]=='}': return i+1,None
            while True:
                key,i=string(i); i=ws(i)
                if text[i] != ':': raise ValueError
                member=_pointer_join(path,key); i,found=val(i+1,member)
                if found is not None:return i,found
                if key in seen:return i,member
                seen.add(key); i=ws(i)
                if text[i]=='}':return i+1,None
                if text[i]!=',':raise ValueError
                i=ws(i+1)
        if text[i]=='[':
            i=ws(i+1); index=0
            if text[i]==']':return i+1,None
            while True:
                i,found=val(i,f"{path}/{index}")
                if found is not None:return i,found
                index+=1; i=ws(i)
                if text[i]==']':return i+1,None
                if text[i]!=',':raise ValueError
                i=ws(i+1)
        _,end=decoder.raw_decode(text,i);return end,None
    try:return val(0,"")[1]
    except (ValueError,IndexError,json.JSONDecodeError):return None

def _assert_keys(obj: Any, keys: set[str], path: str) -> None:
    if not isinstance(obj,dict): raise LabError("TYPE_INVALID",path)
    unknown=sorted(set(obj)-keys)
    if unknown: raise LabError("UNKNOWN_FIELD",_pointer_join(path,unknown[0]))
    missing=sorted(keys-set(obj))
    if missing: raise LabError("REQUIRED_FIELD",_pointer_join(path,missing[0]))

def _id(value:Any, prefix:str,path:str)->str:
    if not isinstance(value,str) or not ID_RE.fullmatch(value) or not value.startswith(prefix): raise LabError("VALUE_RANGE",path)
    return value

def _find_missing(v:Any,path:str="") -> list[dict[str,str]]:
    out=[]
    if isinstance(v,dict):
        if set(v)=={"state","reason"} and v.get("state") in {"MISSING","UNKNOWN","STALE","CONFLICTING","UNAVAILABLE_PIT"}: out.append({"code":v["state"],"path":path})
        else:
            for k,x in v.items(): out.extend(_find_missing(x,_pointer_join(path,k)))
    elif isinstance(v,list):
        for i,x in enumerate(v): out.extend(_find_missing(x,f"{path}/{i}"))
    return out

def _stage5_findings(bundle: Any) -> list[dict[str, str]]:
    """Collect every independently decidable typed/domain finding.

    A bad container is reported once and is never traversed.  Unknown members
    are reported but ignored while the known members of the same object remain
    independently checkable.  Cross-record accounting checks deliberately do
    not live here; they are the stage-7 pass below.
    """
    findings: set[tuple[str, str]] = set()

    def add(code: str, path: str) -> None:
        findings.add((path, code))

    def obj(value: Any, keys: set[str], path: str) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            add("TYPE_INVALID", path)
            return None
        for key in value:
            if key not in keys:
                add("UNKNOWN_FIELD", _pointer_join(path, key))
        for key in keys:
            if key not in value:
                add("REQUIRED_FIELD", _pointer_join(path, key))
        return value

    def array(value: Any, path: str, low: int | None=None, high: int | None=None, exact: int | None=None) -> list[Any] | None:
        if not isinstance(value, list):
            add("TYPE_INVALID", path)
            return None
        if exact is not None and len(value) != exact:
            add("SET_MEMBERSHIP", path)
        if low is not None and len(value) < low:
            add("SET_MEMBERSHIP", path)
        if high is not None and len(value) > high:
            add("SET_MEMBERSHIP", path)
        return value

    def text(value: Any, path: str) -> str | None:
        if not isinstance(value, str):
            add("TYPE_INVALID", path)
            return None
        if not value.strip() or len(value.strip()) > 512:
            add("VALUE_RANGE", path)
        return value

    def literal(value: Any, expected: Any, path: str) -> bool:
        if type(value) is not type(expected):
            add("TYPE_INVALID", path)
            return False
        if value != expected:
            add("VALUE_RANGE", path)
            return False
        return True

    def identifier(value: Any, prefix: str, path: str, reserved: set[str] | None=None) -> str | None:
        if not isinstance(value, str):
            add("TYPE_INVALID", path)
            return None
        if not ID_RE.fullmatch(value) or not value.startswith(prefix) or (reserved and value in reserved):
            add("VALUE_RANGE", path)
            return None
        return value

    def numeric(value: Any, path: str, *, low: Fraction | None=None, high: Fraction | None=None,
                strictly_positive: bool=False) -> Fraction | None:
        if isinstance(value, dict):
            tag=obj(value, {"state", "reason"}, path)
            if tag is None:
                return None
            state=tag.get("state")
            if "state" in tag:
                if not isinstance(state, str):
                    add("TYPE_INVALID", path+"/state")
                elif state not in {"MISSING", "UNKNOWN", "STALE", "CONFLICTING", "UNAVAILABLE_PIT", "NOT_APPLICABLE"}:
                    add("VALUE_RANGE", path+"/state")
                elif state == "NOT_APPLICABLE":
                    add("FIELD_NOT_APPLICABLE", path)
            if "reason" in tag:
                text(tag["reason"], path+"/reason")
            return None
        if not isinstance(value, str) or not DECIMAL_RE.fullmatch(value):
            add("TYPE_INVALID", path)
            return None
        number=Fraction(value)
        valid=True
        if strictly_positive and number <= 0:
            add("VALUE_RANGE", path); valid=False
        if low is not None and number < low:
            add("VALUE_RANGE", path); valid=False
        if high is not None and number > high:
            add("VALUE_RANGE", path); valid=False
        return number if valid else None

    def closed_row(value: Any, keys: set[str], path: str) -> dict[str, Any] | None:
        return obj(value, keys, path)

    root_keys={"schema_version","origin","title","rationale","mandate_assumption","assets","initial_state","paths","probability_family","stress_paths","alternatives","benchmark","uncertainty_ledger"}
    b=obj(bundle, root_keys, "")
    if b is None:
        return [{"code":code,"path":path} for path,code in sorted(findings)]
    if "schema_version" in b: literal(b["schema_version"], SCHEMA, "/schema_version")
    if "origin" in b: literal(b["origin"], "SYNTHETIC_HYPOTHESIS", "/origin")
    for key in ("title", "rationale"):
        if key in b: text(b[key], "/"+key)

    mandate_spec={"reference":"ADR-0012_SYNTHETIC_SUBSET","horizon_months":84,"base_currency":"USD","nominal_real":"NOMINAL","tax_treatment":"PRE_TAX","external_flows":"SELF_FINANCING_NONE","initial_wealth":"1000000","unit_semantics":"FRACTIONAL_BUY_AND_HOLD"}
    mandate=obj(b["mandate_assumption"], set(mandate_spec), "/mandate_assumption") if "mandate_assumption" in b else None
    if mandate is not None:
        for key,expected in mandate_spec.items():
            if key not in mandate: continue
            if key == "initial_wealth":
                value=numeric(mandate[key], f"/mandate_assumption/{key}")
                if value is not None and value != 1_000_000: add("VALUE_RANGE", f"/mandate_assumption/{key}")
            else:
                literal(mandate[key], expected, f"/mandate_assumption/{key}")

    asset_ids: list[str] = []
    asset_kinds: list[str] = []
    assets=array(b["assets"], "/assets", 2, 4) if "assets" in b else None
    if assets is not None:
        ids_complete=True
        for i,value in enumerate(assets):
            path=f"/assets/{i}"; row=closed_row(value,{"asset_id","kind","initial_price","price_semantics"},path)
            if row is None: ids_complete=False; continue
            aid=identifier(row["asset_id"],"SYN_",path+"/asset_id",{"SYN_CASH","SYN_BENCHMARK"}) if "asset_id" in row else None
            if aid is None: ids_complete=False
            else: asset_ids.append(aid)
            if "kind" in row:
                if not isinstance(row["kind"],str): add("TYPE_INVALID",path+"/kind")
                elif row["kind"] not in {"SYNTHETIC_EQUITY","SYNTHETIC_PASSIVE"}: add("VALUE_RANGE",path+"/kind")
                else: asset_kinds.append(row["kind"])
            if "initial_price" in row: numeric(row["initial_price"],path+"/initial_price",strictly_positive=True)
            if "price_semantics" in row: literal(row["price_semantics"],"EX_DISTRIBUTION_AFTER_INTERNAL_EXPENSES_USD",path+"/price_semantics")
        if ids_complete and len(asset_ids)!=len(set(asset_ids)): add("SET_MEMBERSHIP","/assets")
        if len(asset_kinds)==len(assets) and (asset_kinds.count("SYNTHETIC_PASSIVE")!=1 or "SYNTHETIC_EQUITY" not in asset_kinds): add("SET_MEMBERSHIP","/assets")
    asset_universe_known=assets is not None and len(asset_ids)==len(assets) and len(asset_ids)==len(set(asset_ids))

    def positions(value: Any, path: str) -> dict[str, Fraction] | None:
        rows=array(value,path,exact=len(asset_ids) if asset_universe_known else None)
        if rows is None: return None
        result: dict[str,Fraction]={}; seen_ids:list[str]=[]; membership_ok=asset_universe_known
        for i,value in enumerate(rows):
            p=f"{path}/{i}"; row=closed_row(value,{"asset_id","units"},p)
            if row is None: membership_ok=False; continue
            aid=row.get("asset_id")
            if not isinstance(aid,str):
                if "asset_id" in row: add("TYPE_INVALID",p+"/asset_id")
                membership_ok=False
            elif aid not in asset_ids or aid in seen_ids:
                membership_ok=False
            else:
                seen_ids.append(aid)
            amount=numeric(row["units"],p+"/units",low=Fraction()) if "units" in row else None
            if isinstance(aid,str) and amount is not None: result[aid]=amount
        if membership_ok and set(seen_ids)!=set(asset_ids): membership_ok=False
        if asset_universe_known and not membership_ok: add("SET_MEMBERSHIP",path)
        return result if membership_ok and len(result)==len(asset_ids) else None

    initial=obj(b["initial_state"],{"positions","cash"},"/initial_state") if "initial_state" in b else None
    if initial is not None:
        if "positions" in initial: positions(initial["positions"],"/initial_state/positions")
        if "cash" in initial: numeric(initial["cash"],"/initial_state/cash",low=Fraction())

    path_ids: list[str]=[]; stress_ids: list[str]=[]
    def path_collection(value: Any, pointer: str, prefix: str, low: int, high: int, output_ids: list[str]) -> None:
        rows=array(value,pointer,low,high)
        if rows is None: return
        ids_complete=True
        for i,value in enumerate(rows):
            p=f"{pointer}/{i}"; row=closed_row(value,{"path_id","definition","months"},p)
            if row is None: ids_complete=False; continue
            pid=identifier(row["path_id"],prefix,p+"/path_id") if "path_id" in row else None
            if pid is None: ids_complete=False
            else: output_ids.append(pid)
            if "definition" in row: text(row["definition"],p+"/definition")
            months=array(row["months"],p+"/months",exact=84) if "months" in row else None
            if months is None: continue
            for j,value in enumerate(months):
                q=f"{p}/months/{j}"; month=closed_row(value,{"month","assets","cash_gross_factor"},q)
                if month is None: continue
                if "month" in month:
                    if type(month["month"]) is not int: add("TYPE_INVALID",q+"/month")
                    elif month["month"]!=j+1: add("VALUE_RANGE",q+"/month")
                if "cash_gross_factor" in month: numeric(month["cash_gross_factor"],q+"/cash_gross_factor",low=Fraction())
                points=array(month["assets"],q+"/assets",exact=len(asset_ids) if asset_universe_known else None) if "assets" in month else None
                if points is None: continue
                point_ids=[]; membership_ok=asset_universe_known
                for k,value in enumerate(points):
                    z=f"{q}/assets/{k}"; point=closed_row(value,{"asset_id","price","distribution_per_unit"},z)
                    if point is None: membership_ok=False; continue
                    aid=point.get("asset_id")
                    if not isinstance(aid,str):
                        if "asset_id" in point: add("TYPE_INVALID",z+"/asset_id")
                        membership_ok=False
                    else: point_ids.append(aid)
                    if "price" in point: numeric(point["price"],z+"/price",low=Fraction())
                    if "distribution_per_unit" in point: numeric(point["distribution_per_unit"],z+"/distribution_per_unit",low=Fraction())
                if membership_ok and (len(point_ids)!=len(set(point_ids)) or set(point_ids)!=set(asset_ids)): membership_ok=False
                if asset_universe_known and not membership_ok: add("SET_MEMBERSHIP",q+"/assets")
        if ids_complete and len(output_ids)!=len(set(output_ids)): add("SET_MEMBERSHIP",pointer)

    if "paths" in b: path_collection(b["paths"],"/paths","PATH_",1,16,path_ids)
    if "stress_paths" in b: path_collection(b["stress_paths"],"/stress_paths","STRESS_",0,4,stress_ids)
    if len(path_ids)==len(b.get("paths",[]) if isinstance(b.get("paths"),list) else []) and len(stress_ids)==len(b.get("stress_paths",[]) if isinstance(b.get("stress_paths"),list) else []) and set(path_ids)&set(stress_ids): add("SET_MEMBERSHIP","/stress_paths")

    distribution_ids: list[str]=[]
    def distribution(value: Any, path: str, *, base: bool=False) -> dict[str, Fraction] | None:
        row=closed_row(value,{"distribution_id","masses"},path)
        if row is None: return None
        did=identifier(row["distribution_id"],"DIST_",path+"/distribution_id") if "distribution_id" in row else None
        if did is not None: distribution_ids.append(did)
        path_universe_known=isinstance(b.get("paths"),list) and len(path_ids)==len(b["paths"]) and len(path_ids)==len(set(path_ids))
        masses=array(row["masses"],path+"/masses",exact=len(path_ids) if path_universe_known else None) if "masses" in row else None
        if masses is None: return None
        mass_ids=[]; membership_ok=path_universe_known; bad_reference=False
        probabilities:dict[str,Fraction]={}
        for i,value in enumerate(masses):
            p=f"{path}/masses/{i}"; mass=closed_row(value,{"path_id","probability"},p)
            if mass is None: membership_ok=False; continue
            pid=mass.get("path_id")
            if not isinstance(pid,str):
                if "path_id" in mass: add("TYPE_INVALID",p+"/path_id")
                membership_ok=False
            else:
                if path_universe_known and (pid not in path_ids or pid in mass_ids):
                    add("SET_MEMBERSHIP",p+"/path_id"); bad_reference=True; membership_ok=False
                mass_ids.append(pid)
            probability=numeric(mass["probability"],p+"/probability",low=Fraction(),high=Fraction(1)) if "probability" in mass else None
            if base and probability is not None and probability==0: add("VALUE_RANGE",p+"/probability")
            if isinstance(pid,str) and probability is not None: probabilities[pid]=probability
        if membership_ok and set(mass_ids)!=set(path_ids): membership_ok=False
        if path_universe_known and not membership_ok and not bad_reference: add("SET_MEMBERSHIP",path+"/masses")
        return probabilities if membership_ok and len(probabilities)==len(path_ids) else None

    family=obj(b["probability_family"],{"family_id","base","objective_members"},"/probability_family") if "probability_family" in b else None
    if family is not None:
        if "family_id" in family: identifier(family["family_id"],"FAMILY_","/probability_family/family_id")
        base_signature=distribution(family["base"],"/probability_family/base",base=True) if "base" in family else None
        members=array(family["objective_members"],"/probability_family/objective_members",1,4) if "objective_members" in family else None
        member_signatures=[]
        if members is not None:
            for i,value in enumerate(members): member_signatures.append(distribution(value,f"/probability_family/objective_members/{i}"))
            if base_signature is not None and all(signature is not None for signature in member_signatures) and base_signature not in member_signatures:
                add("SET_MEMBERSHIP","/probability_family/objective_members")
        if len(distribution_ids)!=len(set(distribution_ids)): add("SET_MEMBERSHIP","/probability_family")

    def costs(value: Any, path: str) -> dict[str,Fraction] | None:
        keys={"commission","fees","spread","slippage","market_impact","delay","rationale"}; row=closed_row(value,keys,path)
        if row is None: return None
        if "rationale" in row: text(row["rationale"],path+"/rationale")
        result={}
        for key in ("commission","fees","spread","slippage","market_impact","delay"):
            if key in row:
                value=numeric(row[key],path+"/"+key,low=Fraction())
                if value is not None: result[key]=value
        return result if len(result)==6 else None

    alternatives=array(b["alternatives"],"/alternatives",3,8) if "alternatives" in b else None
    alternative_ids=[]; roles=[]
    if alternatives is not None:
        for i,value in enumerate(alternatives):
            p=f"/alternatives/{i}"; row=closed_row(value,{"alternative_id","role","positions","entry_costs"},p)
            if row is None: continue
            aid=identifier(row["alternative_id"],"ALT_",p+"/alternative_id") if "alternative_id" in row else None
            if aid is not None: alternative_ids.append(aid)
            role=row.get("role")
            if "role" in row:
                if not isinstance(role,str): add("TYPE_INVALID",p+"/role")
                elif role not in {"NO_TRADE","CASH_ONLY","PASSIVE_ONLY","CUSTOM_SUPPLIED"}: add("VALUE_RANGE",p+"/role")
                else: roles.append(role)
            pos=positions(row["positions"],p+"/positions") if "positions" in row else None
            component_costs=costs(row["entry_costs"],p+"/entry_costs") if "entry_costs" in row else None
            if pos is not None and len(asset_kinds)==len(asset_ids) and isinstance(role,str) and role in {"CASH_ONLY","PASSIVE_ONLY"}:
                passive_ids=[asset_ids[j] for j,kind in enumerate(asset_kinds) if kind=="SYNTHETIC_PASSIVE" and j<len(asset_ids)]
                if role=="CASH_ONLY" and any(pos.values()): add("SET_MEMBERSHIP",p+"/positions")
                if role=="PASSIVE_ONLY" and (len(passive_ids)!=1 or pos.get(passive_ids[0],Fraction())<=0 or any(pos[x] for x in pos if x!=passive_ids[0])): add("SET_MEMBERSHIP",p+"/positions")
            # NO_TRADE cost/position equality belongs to stage 7.  Only the
            # present typed components are checked here.
            _=component_costs
        if len(alternative_ids)==len(alternatives) and len(alternative_ids)!=len(set(alternative_ids)): add("SET_MEMBERSHIP","/alternatives")
        if len(roles)==len(alternatives) and (roles.count("NO_TRADE")!=1 or roles.count("CASH_ONLY")!=1 or roles.count("PASSIVE_ONLY")!=1): add("SET_MEMBERSHIP","/alternatives")

    benchmark=obj(b["benchmark"],{"benchmark_id","definition","ordinary_paths","stress_paths"},"/benchmark") if "benchmark" in b else None
    if benchmark is not None:
        if "benchmark_id" in benchmark: literal(benchmark["benchmark_id"],"SYN_BENCHMARK","/benchmark/benchmark_id")
        if "definition" in benchmark: text(benchmark["definition"],"/benchmark/definition")
        for key,expected in (("ordinary_paths",path_ids),("stress_paths",stress_ids)):
            if key not in benchmark: continue
            path=f"/benchmark/{key}"; rows=array(benchmark[key],path,exact=len(expected))
            if rows is None: continue
            ids=[]; membership_ok=True
            for i,value in enumerate(rows):
                p=f"{path}/{i}"; row=closed_row(value,{"path_id","levels"},p)
                if row is None: membership_ok=False; continue
                pid=row.get("path_id")
                if not isinstance(pid,str):
                    if "path_id" in row: add("TYPE_INVALID",p+"/path_id")
                    membership_ok=False
                else: ids.append(pid)
                levels=array(row["levels"],p+"/levels",exact=85) if "levels" in row else None
                if levels is not None:
                    for j,item in enumerate(levels):
                        number=numeric(item,f"{p}/levels/{j}",low=Fraction())
                        if j==0 and number is not None and number!=1: add("VALUE_RANGE",f"{p}/levels/{j}")
            if membership_ok and (len(ids)!=len(set(ids)) or set(ids)!=set(expected)): membership_ok=False
            if not membership_ok: add("SET_MEMBERSHIP",path)

    ledger=array(b["uncertainty_ledger"],"/uncertainty_ledger",exact=7) if "uncertainty_ledger" in b else None
    ledger_ids=[]
    if ledger is not None:
        for i,value in enumerate(ledger):
            p=f"/uncertainty_ledger/{i}"; row=closed_row(value,{"source_id","role","treatment","evidence_status","rationale"},p)
            if row is None: continue
            source=row.get("source_id")
            if not isinstance(source,str):
                if "source_id" in row: add("TYPE_INVALID",p+"/source_id")
            else: ledger_ids.append(source)
            for key in ("role","treatment","evidence_status"):
                if key in row and not isinstance(row[key],str): add("TYPE_INVALID",p+"/"+key)
            if "rationale" in row: text(row["rationale"],p+"/rationale")
            if isinstance(source,str) and source in LEDGER_ROWS and all(isinstance(row.get(k),str) for k in ("role","treatment","evidence_status")):
                if tuple(row[k] for k in ("role","treatment","evidence_status"))!=LEDGER_ROWS[source]: add("SET_MEMBERSHIP",p)
            elif isinstance(source,str): add("SET_MEMBERSHIP",p)
        if len(ledger_ids)==len(ledger) and (len(ledger_ids)!=len(set(ledger_ids)) or set(ledger_ids)!=set(LEDGER_ROWS)): add("SET_MEMBERSHIP","/uncertainty_ledger")

    return [{"code":code,"path":path} for path,code in sorted(findings)]

def _check_bundle(b: Any, *, validate_cross: bool=True) -> tuple[dict[str,Any], dict[str,Fraction]]:
    required={"schema_version","origin","title","rationale","mandate_assumption","assets","initial_state","paths","probability_family","stress_paths","alternatives","benchmark","uncertainty_ledger"}
    _assert_keys(b,required,"")
    if b["schema_version"]!=SCHEMA or b["origin"]!="SYNTHETIC_HYPOTHESIS": raise LabError("VALUE_RANGE","/schema_version")
    for k in ("title","rationale"):
        if not isinstance(b[k],str) or not b[k].strip() or len(b[k].strip())>512: raise LabError("VALUE_RANGE",f"/{k}")
        b[k]=b[k].strip()
    mandate={"reference":"ADR-0012_SYNTHETIC_SUBSET","horizon_months":84,"base_currency":"USD","nominal_real":"NOMINAL","tax_treatment":"PRE_TAX","external_flows":"SELF_FINANCING_NONE","initial_wealth":"1000000","unit_semantics":"FRACTIONAL_BUY_AND_HOLD"}
    _assert_keys(b["mandate_assumption"],set(mandate),"/mandate_assumption")
    if b["mandate_assumption"] != mandate: raise LabError("VALUE_RANGE","/mandate_assumption")
    if not isinstance(b["assets"],list) or not 2<=len(b["assets"])<=4: raise LabError("SET_MEMBERSHIP","/assets")
    assets=[]; prices={}; passive=[]
    for i,a in enumerate(b["assets"]):
        p=f"/assets/{i}"; _assert_keys(a,{"asset_id","kind","initial_price","price_semantics"},p)
        aid=_id(a["asset_id"],"SYN_",p+"/asset_id")
        if aid in {"SYN_CASH","SYN_BENCHMARK"} or aid in assets: raise LabError("SET_MEMBERSHIP",p+"/asset_id")
        if a["kind"] not in {"SYNTHETIC_EQUITY","SYNTHETIC_PASSIVE"} or a["price_semantics"]!="EX_DISTRIBUTION_AFTER_INTERNAL_EXPENSES_USD": raise LabError("VALUE_RANGE",p)
        x=_d(a["initial_price"],p+"/initial_price");
        if isinstance(x,dict) or x<=0: raise LabError("VALUE_RANGE",p+"/initial_price")
        assets.append(aid);prices[aid]=x
        if a["kind"]=="SYNTHETIC_PASSIVE":passive.append(aid)
    if len(passive)!=1 or len(passive)==len(assets): raise LabError("SET_MEMBERSHIP","/assets")
    _assert_keys(b["initial_state"],{"positions","cash"},"/initial_state")
    pos=_positions(b["initial_state"]["positions"],assets,"/initial_state/positions")
    cash=_d(b["initial_state"]["cash"],"/initial_state/cash")
    if isinstance(cash,dict) or cash<0: raise LabError("VALUE_RANGE","/initial_state/cash")
    if validate_cross and cash+sum(pos[x]*prices[x] for x in assets)!=1_000_000: raise LabError("INITIAL_WEALTH_MISMATCH","/initial_state")
    if not isinstance(b["paths"],list) or not 1<=len(b["paths"])<=16: raise LabError("SET_MEMBERSHIP","/paths")
    path_ids=[]
    for i,path in enumerate(b["paths"]): _validate_path(path,assets,f"/paths/{i}","PATH_",path_ids,validate_terminal=validate_cross);path_ids.append(path["path_id"])
    if not isinstance(b["stress_paths"],list) or len(b["stress_paths"])>4: raise LabError("SET_MEMBERSHIP","/stress_paths")
    stress_ids=[]
    for i,path in enumerate(b["stress_paths"]): _validate_path(path,assets,f"/stress_paths/{i}","STRESS_",stress_ids,validate_terminal=validate_cross);stress_ids.append(path["path_id"])
    if set(path_ids) & set(stress_ids): raise LabError("SET_MEMBERSHIP","/stress_paths")
    _validate_family(b["probability_family"],path_ids,validate_sum=validate_cross)
    if not isinstance(b["alternatives"],list) or not 3<=len(b["alternatives"])<=8: raise LabError("SET_MEMBERSHIP","/alternatives")
    roles=[]; alternative_ids=set(); no_trade_positions=None
    for i,a in enumerate(b["alternatives"]):
        p=f"/alternatives/{i}"; _assert_keys(a,{"alternative_id","role","positions","entry_costs"},p);_id(a["alternative_id"],"ALT_",p+"/alternative_id")
        if a["alternative_id"] in alternative_ids: raise LabError("SET_MEMBERSHIP",p+"/alternative_id")
        alternative_ids.add(a["alternative_id"])
        if a["role"] not in {"NO_TRADE","CASH_ONLY","PASSIVE_ONLY","CUSTOM_SUPPLIED"}:raise LabError("VALUE_RANGE",p+"/role")
        roles.append(a["role"]); q=_positions(a["positions"],assets,p+"/positions"); cost=_costs(a["entry_costs"],p+"/entry_costs")
        if validate_cross and a["role"]=="NO_TRADE":
            no_trade_positions=q
            if q != pos: raise LabError("NO_TRADE_MISMATCH",p+"/positions")
            if cost != 0: raise LabError("COST_WITHOUT_TRADE",p+"/entry_costs")
        if validate_cross and q == pos and cost != 0: raise LabError("COST_WITHOUT_TRADE",p+"/entry_costs")
        if a["role"]=="CASH_ONLY" and any(q.values()): raise LabError("SET_MEMBERSHIP",p+"/positions")
        if a["role"]=="PASSIVE_ONLY" and (q[passive[0]] <= 0 or any(q[x] for x in assets if x != passive[0])): raise LabError("SET_MEMBERSHIP",p+"/positions")
    if roles.count("NO_TRADE")!=1 or roles.count("CASH_ONLY")!=1 or roles.count("PASSIVE_ONLY")!=1:raise LabError("SET_MEMBERSHIP","/alternatives")
    # Full ledger/benchmark contracts are intentionally validated as closed maps.
    _validate_benchmark(b["benchmark"],path_ids,stress_ids,validate_terminal=validate_cross)
    if not isinstance(b["uncertainty_ledger"],list) or len(b["uncertainty_ledger"])!=7: raise LabError("SET_MEMBERSHIP","/uncertainty_ledger")
    seen=set()
    for i,row in enumerate(b["uncertainty_ledger"]):
        p=f"/uncertainty_ledger/{i}"; _assert_keys(row,{"source_id","role","treatment","evidence_status","rationale"},p)
        source=row["source_id"]
        if source not in LEDGER_ROWS or source in seen or tuple(row[k] for k in ("role","treatment","evidence_status"))!=LEDGER_ROWS[source]: raise LabError("SET_MEMBERSHIP",p)
        if not isinstance(row["rationale"],str) or not row["rationale"].strip(): raise LabError("VALUE_RANGE",p+"/rationale")
        seen.add(source)
    if seen != set(LEDGER_ROWS): raise LabError("SET_MEMBERSHIP","/uncertainty_ledger")
    return b,prices

def _positions(rows:Any,assets:list[str],path:str)->dict[str,Fraction]:
    if not isinstance(rows,list) or len(rows)!=len(assets):raise LabError("SET_MEMBERSHIP",path)
    out={}
    for i,row in enumerate(rows):
        _assert_keys(row,{"asset_id","units"},f"{path}/{i}"); aid=row["asset_id"]
        if aid not in assets or aid in out:raise LabError("SET_MEMBERSHIP",f"{path}/{i}/asset_id")
        u=_d(row["units"],f"{path}/{i}/units");
        if isinstance(u,dict) or u<0:raise LabError("VALUE_RANGE",f"{path}/{i}/units")
        out[aid]=u
    return out

def _costs(costs:Any,path:str)->Fraction:
    _assert_keys(costs,{"commission","fees","spread","slippage","market_impact","delay","rationale"},path)
    if not isinstance(costs["rationale"],str) or not costs["rationale"].strip():raise LabError("VALUE_RANGE",path+"/rationale")
    total=Fraction()
    for k in ("commission","fees","spread","slippage","market_impact","delay"):
        x=_d(costs[k],path+"/"+k)
        if isinstance(x,dict) or x<0:raise LabError("VALUE_RANGE",path+"/"+k)
        total+=x
    return total

def _validate_path(path:Any, assets:list[str], pointer:str, prefix:str, prior:list[str], *, validate_terminal: bool=True)->None:
    _assert_keys(path,{"path_id","definition","months"},pointer); pid=_id(path["path_id"],prefix,pointer+"/path_id")
    if pid in prior or not isinstance(path["definition"],str) or not path["definition"].strip():raise LabError("SET_MEMBERSHIP",pointer)
    if not isinstance(path["months"],list) or len(path["months"])!=84:raise LabError("SET_MEMBERSHIP",pointer+"/months")
    extinguished:set[str]=set()
    for i,m in enumerate(path["months"]):
        p=f"{pointer}/months/{i}";_assert_keys(m,{"month","assets","cash_gross_factor"},p)
        if type(m["month"]) is not int or m["month"]!=i+1:raise LabError("VALUE_RANGE",p+"/month")
        g=_d(m["cash_gross_factor"],p+"/cash_gross_factor")
        if isinstance(g,dict) or g<0:raise LabError("VALUE_RANGE",p+"/cash_gross_factor")
        if not isinstance(m["assets"],list) or len(m["assets"])!=len(assets):raise LabError("SET_MEMBERSHIP",p+"/assets")
        seen=set()
        for j,a in enumerate(m["assets"]):
            q=f"{p}/assets/{j}";_assert_keys(a,{"asset_id","price","distribution_per_unit"},q)
            if a["asset_id"] not in assets or a["asset_id"] in seen:raise LabError("SET_MEMBERSHIP",q+"/asset_id")
            seen.add(a["asset_id"])
            for k in ("price","distribution_per_unit"):
                x=_d(a[k],q+"/"+k)
                if isinstance(x,dict) or x<0:raise LabError("VALUE_RANGE",q+"/"+k)
            price=_d(a["price"],q+"/price"); dividend=_d(a["distribution_per_unit"],q+"/distribution_per_unit")
            if validate_terminal and a["asset_id"] in extinguished and (price != 0 or dividend != 0):
                raise LabError("TERMINAL_ZERO_REVERSAL",q+"/price" if price != 0 else q+"/distribution_per_unit")
            if price == 0: extinguished.add(a["asset_id"])

def _validate_family(f:Any, path_ids:list[str], *, validate_sum: bool=True)->None:
    _assert_keys(f,{"family_id","base","objective_members"},"/probability_family");_id(f["family_id"],"FAMILY_","/probability_family/family_id")
    seen_distributions:set[str]=set()
    def dist(d:Any,p:str, *, base: bool=False):
        _assert_keys(d,{"distribution_id","masses"},p);_id(d["distribution_id"],"DIST_",p+"/distribution_id")
        if d["distribution_id"] in seen_distributions: raise LabError("SET_MEMBERSHIP",p+"/distribution_id")
        seen_distributions.add(d["distribution_id"])
        if not isinstance(d["masses"],list) or len(d["masses"])!=len(path_ids):raise LabError("SET_MEMBERSHIP",p+"/masses")
        total=Fraction();seen=set()
        for i,m in enumerate(d["masses"]):
            q=f"{p}/masses/{i}";_assert_keys(m,{"path_id","probability"},q)
            if m["path_id"] not in path_ids or m["path_id"] in seen:raise LabError("SET_MEMBERSHIP",q+"/path_id")
            seen.add(m["path_id"]);x=_d(m["probability"],q+"/probability")
            if isinstance(x,dict) or x<0 or x>1:raise LabError("VALUE_RANGE",q+"/probability")
            if base and x == 0: raise LabError("VALUE_RANGE",q+"/probability")
            total+=x
        if validate_sum and total!=1:raise LabError("PROBABILITY_SUM",p+"/masses")
    dist(f["base"],"/probability_family/base",base=True)
    if not isinstance(f["objective_members"],list) or not 1<=len(f["objective_members"])<=4:raise LabError("SET_MEMBERSHIP","/probability_family/objective_members")
    for i,x in enumerate(f["objective_members"]):dist(x,f"/probability_family/objective_members/{i}")

def _validate_benchmark(b:Any, ordinary:list[str],stress:list[str], *, validate_terminal: bool=True)->None:
    _assert_keys(b,{"benchmark_id","definition","ordinary_paths","stress_paths"},"/benchmark")
    if b["benchmark_id"]!="SYN_BENCHMARK" or not isinstance(b["definition"],str) or not b["definition"].strip():raise LabError("VALUE_RANGE","/benchmark")
    for key, ids in (("ordinary_paths",ordinary),("stress_paths",stress)):
        rows=b[key]
        if not isinstance(rows,list) or len(rows)!=len(ids):raise LabError("SET_MEMBERSHIP","/benchmark/"+key)
        seen=set()
        for i,row in enumerate(rows):
            p=f"/benchmark/{key}/{i}";_assert_keys(row,{"path_id","levels"},p)
            if row["path_id"] not in ids or row["path_id"] in seen or not isinstance(row["levels"],list) or len(row["levels"])!=85:raise LabError("SET_MEMBERSHIP",p)
            seen.add(row["path_id"])
            extinguished=False
            for j,v in enumerate(row["levels"]):
                x=_d(v,f"{p}/levels/{j}")
                if isinstance(x,dict) or x<0 or (j==0 and x!=1):raise LabError("VALUE_RANGE",f"{p}/levels/{j}")
                if validate_terminal and extinguished and x != 0: raise LabError("TERMINAL_ZERO_REVERSAL",f"{p}/levels/{j}")
                if x == 0: extinguished=True

def _cross_record_findings(bundle: dict[str,Any], prices: dict[str,Fraction]) -> list[dict[str,str]]:
    """Stage-7 independent cross-record aggregation after closed typed shape."""
    findings:set[tuple[str,str]]=set(); assets=list(prices)
    initial=_positions(bundle["initial_state"]["positions"],assets,"/initial_state/positions")
    old_cash=_d(bundle["initial_state"]["cash"],"/initial_state/cash")
    initial_ok=old_cash+sum(initial[key]*prices[key] for key in assets)==1_000_000
    if not initial_ok: findings.add(("/initial_state","INITIAL_WEALTH_MISMATCH"))
    family=bundle["probability_family"]
    for pointer,distribution in [("/probability_family/base",family["base"]),*[(f"/probability_family/objective_members/{i}",item) for i,item in enumerate(family["objective_members"])]]:
        if sum((_d(mass["probability"],pointer) for mass in distribution["masses"]),Fraction()) != 1:
            findings.add((pointer+"/masses","PROBABILITY_SUM"))
    def terminal(rows: list[dict[str,Any]], base: str, benchmark: bool=False) -> None:
        for i,path in enumerate(rows):
            if benchmark:
                zero=False
                for j,value in enumerate(path["levels"]):
                    numeric=_d(value,f"{base}/{i}/levels/{j}")
                    if zero and numeric != 0: findings.add((f"{base}/{i}/levels/{j}","TERMINAL_ZERO_REVERSAL"))
                    if numeric==0: zero=True
            else:
                zero_assets:set[str]=set()
                for j,month in enumerate(path["months"]):
                    for k,point in enumerate(month["assets"]):
                        price=_d(point["price"],""); dividend=_d(point["distribution_per_unit"],"")
                        if point["asset_id"] in zero_assets:
                            if price != 0:
                                findings.add((f"{base}/{i}/months/{j}/assets/{k}/price","TERMINAL_ZERO_REVERSAL"))
                            if dividend != 0:
                                findings.add((f"{base}/{i}/months/{j}/assets/{k}/distribution_per_unit","TERMINAL_ZERO_REVERSAL"))
                        if price==0: zero_assets.add(point["asset_id"])
    terminal(bundle["paths"],"/paths"); terminal(bundle["stress_paths"],"/stress_paths")
    terminal(bundle["benchmark"]["ordinary_paths"],"/benchmark/ordinary_paths",True); terminal(bundle["benchmark"]["stress_paths"],"/benchmark/stress_paths",True)
    for i,alternative in enumerate(bundle["alternatives"]):
        pointer=f"/alternatives/{i}"; positions=_positions(alternative["positions"],assets,pointer+"/positions"); cost=_costs(alternative["entry_costs"],pointer+"/entry_costs")
        if alternative["role"]=="NO_TRADE" and positions != initial: findings.add((pointer+"/positions","NO_TRADE_MISMATCH"))
        if (alternative["role"]=="NO_TRADE" or positions==initial) and cost != 0: findings.add((pointer+"/entry_costs","COST_WITHOUT_TRADE"))
        if initial_ok and old_cash-sum((positions[key]-initial[key])*prices[key] for key in assets)-cost < 0: findings.add((pointer,"UNFUNDED_ALTERNATIVE"))
    return [{"code":code,"path":path} for path,code in sorted(findings)]

def _source_hashes() -> dict[str,str]:
    hashes={}
    for rel in MANIFEST:
        p=ROOT/rel
        if not p.is_file() or p.is_symlink():raise LabError("SOURCE_UNAVAILABLE","","INTERNAL_ERROR")
        try: hashes[rel]=sha256(p.read_bytes()).hexdigest()
        except OSError: raise LabError("SOURCE_UNAVAILABLE","","INTERNAL_ERROR")
    return hashes

def _authority_context() -> dict[str,str]:
    policy=ROOT/"OPTIVEST_AI_POLICY_V10.md";design=ROOT/"docs/RESEARCH_WEALTH_LAB_DESIGN.md"
    if not policy.is_file() or not design.is_file():raise LabError("SOURCE_UNAVAILABLE","","INTERNAL_ERROR")
    try: policy_hash=sha256(policy.read_bytes()).hexdigest();design_hash=sha256(design.read_bytes()).hexdigest()
    except OSError: raise LabError("SOURCE_UNAVAILABLE","","INTERNAL_ERROR")
    if policy_hash!=POLICY_HASH:raise LabError("POLICY_MISMATCH","","INTERNAL_ERROR")
    if design_hash!=DESIGN_HASH:raise LabError("DESIGN_MISMATCH","","INTERNAL_ERROR")
    return _source_hashes()

def _git_identity() -> dict[str,str|None]:
    env=dict(os.environ);env.update({"GIT_OPTIONAL_LOCKS":"0","GIT_OPTIONAL_REFRESH":"0"})
    try:
        inside=subprocess.run(["git","rev-parse","--is-inside-work-tree"],cwd=ROOT,capture_output=True,text=True,timeout=2,env=env)
        if inside.returncode or inside.stdout.strip().lower()!="true":
            return {"value":None,"reason":"GIT_NOT_AVAILABLE"}
        head=subprocess.run(["git","rev-parse","--verify","HEAD"],cwd=ROOT,capture_output=True,text=True,timeout=2,env=env)
        commit=head.stdout.strip().lower()
        if head.returncode==0 and re.fullmatch(r"[0-9a-f]{40}",commit): return {"value":commit,"reason":None}
        symbolic=subprocess.run(["git","symbolic-ref","-q","HEAD"],cwd=ROOT,capture_output=True,text=True,timeout=2,env=env)
        if symbolic.returncode==0 and symbolic.stdout.strip(): return {"value":None,"reason":"UNBORN"}
    except Exception:
        pass
    return {"value":None,"reason":"GIT_NOT_AVAILABLE"}

def _provenance() -> dict[str,Any]:
    global _LOADED_SOURCE_HASHES
    hashes=_authority_context()
    if _LOADED_SOURCE_HASHES is None:
        _LOADED_SOURCE_HASHES=dict(hashes)
    elif _LOADED_SOURCE_HASHES != hashes:
        raise LabError("SOURCE_CHANGED","","INTERNAL_ERROR")
    git=_git_identity()
    try: transports={name:version(name) for name in ("fastapi","pydantic","starlette","uvicorn")}
    except Exception:raise LabError("RUNTIME_UNAVAILABLE","","INTERNAL_ERROR")
    dec=__import__('decimal')
    return {"policy_filename":"OPTIVEST_AI_POLICY_V10.md","policy_sha256":POLICY_HASH,"design_sha256":DESIGN_HASH,"schema_version":SCHEMA,"method_version":METHOD,"canonicalization_version":CANON,"source_hashes":hashes,"runtime":{"python_implementation":platform.python_implementation(),"python_version":platform.python_version(),"decimal_implementation":"C_DECIMAL" if Decimal.__module__=="decimal" else "PYTHON_DECIMAL","libmpdec_version":str(getattr(dec,'__libmpdec_version__','UNAVAILABLE')),"transport_versions":dict(sorted(transports.items()))},"commit":git,"randomness":"NONE_DETERMINISTIC","dataset_status":"SYNTHETIC_NO_MARKET_EVIDENCE","trial_status":"ENGINEERING_FIXTURE_NOT_RESEARCH_TRIAL"}

def _failure(code:str,path:str,status:str, prov:dict|None=None, h:str|None=None)->dict[str,Any]:
    return {"schema_version":"RESEARCH_WEALTH_LAB_RESULT_V1","input_sha256":h,"provenance":prov,"status":status,"boundaries":BOUNDARIES,"findings":[{"code":code,"path":path}],"result":None}

def _check_serialized_sizes(evaluation_bytes: bytes, artifact_bytes: bytes) -> None:
    """Private W19 seam: byte limits are checked on canonical serialized bytes."""
    if len(evaluation_bytes) > MAX_EVALUATION:
        raise LabError("RESULT_SIZE", "", "NUMERICAL_NOT_VERIFIED", True)
    if len(artifact_bytes) > MAX_ARTIFACT:
        raise LabError("ARTIFACT_SIZE", "", "NUMERICAL_NOT_VERIFIED", True)

def _assert_ledger_invariants(exact_state: Any) -> None:
    """Private W19 seam; normal callers receive no bypass or configuration."""
    if not isinstance(exact_state,dict) or not exact_state.get("events"):
        raise RuntimeError("missing exact ledger")
    for event in exact_state["events"]:
        cash=event["cash"]; values=event["values"]; wealth=event["wealth"]
        if cash+sum(values.values(),Fraction()) != wealth or cash<0 or any(v<0 for v in values.values()):
            raise RuntimeError("ledger equality")
        if wealth:
            fractions=[cash/wealth,*[v/wealth for v in values.values()]]
            if sum(fractions,Fraction()) != 1 or any(v<0 for v in fractions): raise RuntimeError("fraction equality")
    if exact_state["events"][0]["wealth"] != exact_state["initial_wealth"]:
        raise RuntimeError("pre-trade identity")

def _annual_log(exact_state: Fraction, precision: int) -> Decimal:
    with localcontext() as context:
        context.prec=precision; context.rounding=ROUND_HALF_EVEN
        context.Emin=-999999; context.Emax=999999
        return (Decimal(exact_state.numerator)/Decimal(exact_state.denominator)).ln()/Decimal(7)

def _numerical_payload(exact_state: dict[str,Any], precision: int) -> dict[str,str]:
    """Private W19 seam covering every derived log/exp/min/difference value."""
    with localcontext() as context:
        context.prec=precision;context.rounding=ROUND_HALF_EVEN
        context.Emin=-999999;context.Emax=999999
        values:dict[str,Decimal]={key:+value for key,value in exact_state["logs"].items() if value is not None}
        payload={}
        for key,value in values.items():
            payload[key+"/log"]=_render(Fraction(value))
            payload[key+"/exp"]=_render(Fraction(value.exp()-Decimal(1)))
        minima={key:min(values[item] for item in members) for key,members in exact_state["groups"].items() if members}
        for key,value in minima.items():payload[key+"/min"]=_render(Fraction(value))
        for key,(left,right) in exact_state["differences"].items():payload[key+"/difference"]=_render(Fraction(minima[left]-minima[right]))
        return payload

def _verify_numerical_payload(exact_state: dict[str,Any]) -> None:
    if _numerical_payload(exact_state,80) != _numerical_payload(exact_state,120):
        raise LabError("NUMERICAL_NOT_VERIFIED","","NUMERICAL_NOT_VERIFIED",True)

def _path_result(path:dict[str,Any], units:dict[str,Fraction], cash:Fraction, prices:dict[str,Fraction], cost:Fraction,
                 initial_units:dict[str,Fraction], initial_cash:Fraction)->dict[str,Any]:
    events=[]; exact_events=[]; initial=sum(initial_units[k]*prices[k] for k in initial_units)+initial_cash
    def event(month:int,kind:str,c:Fraction, vals:dict[str,Fraction]):
        wealth=c+sum(vals.values());fs=[]
        for k in sorted(vals):fs.append({"asset_id":k,"realized_hypothetical_fraction":_n(vals[k]/wealth) if wealth else _n(None,"ZERO_WEALTH_UNDEFINED")})
        fs.append({"asset_id":"SYN_CASH","realized_hypothetical_fraction":_n(c/wealth) if wealth else _n(None,"ZERO_WEALTH_UNDEFINED")})
        exact_events.append({"cash":c,"values":dict(vals),"wealth":wealth})
        return {"month":month,"event_kind":kind,"cash":_n(c),"position_values":[{"asset_id":k,"value":_n(vals[k])} for k in sorted(vals)],"wealth":_n(wealth),"wealth_state":"POSITIVE" if wealth else "ZERO","fractions":fs},wealth
    vals={k:initial_units[k]*prices[k] for k in initial_units};e,w=event(0,"PRE_TRADE",initial_cash,vals);events.append(e)
    peak=w;anchor=(0,"PRE_TRADE");open_ep=None;episodes=[];maxdd=Fraction()
    vals={k:units[k]*prices[k] for k in units};e,w=event(0,"POST_TRADE",cash,vals);events.append(e)
    maxdd=max(maxdd,1-w/peak)
    if w>=peak: peak=w;anchor=(0,"POST_TRADE")
    else: open_ep=anchor
    for month in path["months"]:
        c=_d(month["cash_gross_factor"],"")*cash
        points={x["asset_id"]:x for x in month["assets"]}
        c+=sum(units[k]*_d(points[k]["distribution_per_unit"],"") for k in units);cash=c
        vals={k:units[k]*_d(points[k]["price"],"") for k in units}; e,w=event(month["month"],"MONTH",cash,vals);events.append(e)
        if w>peak: peak=w
        maxdd=max(maxdd,1-w/peak)
        if w>=peak:
            if open_ep:
                pm,pk=open_ep;episodes.append({"peak_month":pm,"peak_event_kind":pk,"recovered_month":month["month"],"recovered_event_kind":"MONTH","observed_until_month":month["month"],"duration_months":month["month"]-pm,"right_censored":False});open_ep=None
            peak=w;anchor=(month["month"],"MONTH")
        elif open_ep is None:open_ep=anchor
    if open_ep:
        pm,pk=open_ep;episodes.append({"peak_month":pm,"peak_event_kind":pk,"recovered_month":None,"recovered_event_kind":None,"observed_until_month":84,"duration_months":None,"right_censored":True})
    if w==0:
        exact_log=None;lg=_n(None,"ZERO_TERMINAL_WEALTH",True); cagr=_n(Fraction(-1))
    else:
        exact_log=_decimal_log_value(w/initial);lg=_n(Fraction(exact_log));cagr=_n(_verified_exp_growth(exact_log))
    _assert_ledger_invariants({"events":exact_events,"initial_wealth":initial})
    output={"path_id":path["path_id"],"events":events,"terminal_wealth":_n(w),"terminal_state":"POSITIVE" if w else "ZERO","path_log_growth":lg,"path_cagr":cagr,"sampled_max_drawdown":_n(maxdd),"recovery_episodes":episodes}
    output["__ledger_log"] = exact_log
    output["__terminal_ratio"] = None if w == 0 else w/initial
    return output

def _decimal_log(x:Fraction)->dict[str,Any]:
    return {"kind":"FINITE","value":_render(Fraction(_decimal_log_value(x))),"reason":None}

def _decimal_log_value(x: Fraction) -> Decimal:
    """Verified active-precision annual log retained for unrounded comparison."""
    low=_annual_log(x,80)
    high=_annual_log(x,120)
    low_rendered=_render(Fraction(low)); high_rendered=_render(Fraction(high))
    if low_rendered != high_rendered:
        raise LabError("NUMERICAL_NOT_VERIFIED","","NUMERICAL_NOT_VERIFIED",True)
    return high
def _decimal_exp(lognum:dict[str,Any])->Fraction:
    with localcontext() as c:
        c.prec=120
        return Fraction(Decimal(lognum["value"].replace("e","E")).exp())

def _fraction_decimal(value: Fraction) -> Decimal:
    with localcontext() as context:
        context.prec=120; context.rounding=ROUND_HALF_EVEN
        return Decimal(value.numerator)/Decimal(value.denominator)

_D_FIELDS={"initial_price","initial_wealth","units","cash","cash_gross_factor","price","distribution_per_unit","probability","commission","fees","spread","slippage","market_impact","delay"}
_TEXT_FIELDS={"title","rationale","definition","reason"}

def _normalize_bundle(value: Any, key: str | None=None) -> Any:
    """Return the one canonical normalized Bundle used by hash/evaluation/artifact."""
    if isinstance(value,dict):
        normalized={k:_normalize_bundle(v,k) for k,v in value.items()}
        return normalized
    if isinstance(value,list):
        items=[_normalize_bundle(item,key) for item in value]
        if key=="levels":
            return [_normal_decimal(item,"") for item in items]
        for identity in ("asset_id","path_id","distribution_id","alternative_id","source_id"):
            if items and all(isinstance(item,dict) and isinstance(item.get(identity),str) for item in items):
                return sorted(items,key=lambda item:item[identity])
        return items
    if isinstance(value,str):
        if key in _TEXT_FIELDS:return value.strip()
        if key in _D_FIELDS:return _normal_decimal(value,"")
    return value

def _verified_distribution_log(masses: dict[str,Fraction], paths: dict[str,dict[str,Any]]) -> Decimal:
    values=[]
    for precision in (80,120):
        with localcontext() as context:
            context.prec=precision;context.rounding=ROUND_HALF_EVEN;context.Emin=-999999;context.Emax=999999
            total=Decimal(0)
            for path_id,path in paths.items():
                ratio=path["__terminal_ratio"]
                log=(Decimal(ratio.numerator)/Decimal(ratio.denominator)).ln()/Decimal(7)
                total+=(Decimal(masses[path_id].numerator)/Decimal(masses[path_id].denominator))*log
            values.append(+total)
    if _render(Fraction(values[0])) != _render(Fraction(values[1])):
        raise LabError("NUMERICAL_NOT_VERIFIED","","NUMERICAL_NOT_VERIFIED",True)
    return values[1]

def _verified_exp_growth(value: Decimal) -> Fraction:
    outputs=[]
    for precision in (80,120):
        with localcontext() as context:
            context.prec=precision;context.rounding=ROUND_HALF_EVEN;context.Emin=-999999;context.Emax=999999
            outputs.append(+(value.exp()-Decimal(1)))
    if _render(Fraction(outputs[0])) != _render(Fraction(outputs[1])):
        raise LabError("NUMERICAL_NOT_VERIFIED","","NUMERICAL_NOT_VERIFIED",True)
    return Fraction(outputs[1])

def _evaluate(bundle:dict[str,Any], prices:dict[str,Fraction])->dict[str,Any]:
    assets=list(prices);initial_pos=_positions(bundle["initial_state"]["positions"],assets,"/initial_state/positions");old_cash=_d(bundle["initial_state"]["cash"],"/initial_state/cash")
    alternatives=[]
    no_trade=None
    source_index={alt["alternative_id"]: index for index,alt in enumerate(bundle["alternatives"])}
    for alt in sorted(bundle["alternatives"],key=lambda x:x["alternative_id"]):
        q=_positions(alt["positions"],assets,""); cost=_costs(alt["entry_costs"],""); cash=old_cash-sum((q[k]-initial_pos[k])*prices[k] for k in assets)-cost
        if cash<0:raise LabError("UNFUNDED_ALTERNATIVE",f"/alternatives/{source_index[alt['alternative_id']]}","INVALID_INPUT")
        ordinary=[_path_result(p,q,cash,prices,cost,initial_pos,old_cash) for p in bundle["paths"]]
        stress=[_path_result(p,q,cash,prices,cost,initial_pos,old_cash) for p in bundle["stress_paths"]]
        byid={x["path_id"]:x for x in ordinary}; summaries=[]
        distributions=[bundle["probability_family"]["base"]]+bundle["probability_family"]["objective_members"]
        for d in distributions:
            masses={x["path_id"]:_d(x["probability"],"") for x in d["masses"]};ruin=sum(masses[k] for k,r in byid.items() if r["terminal_state"]=="ZERO")
            if ruin: log=_n(None,"POSITIVE_ASSUMED_RUIN_MASS",True); geo=_n(Fraction(-1))
            else:
                val=_verified_distribution_log(masses,byid)
                log=_n(Fraction(val));geo=_n(_verified_exp_growth(val))
            summaries.append({"distribution_id":d["distribution_id"],"annual_log_growth":log,"geometric_equivalent_growth_under_assumption":geo,"synthetic_zero_wealth_mass":_n(ruin),"__ledger_log":None if ruin else val})
        members=summaries[1:]; inf=any(x["annual_log_growth"]["kind"]=="NEGATIVE_INFINITY" for x in members)
        finite=[x["__ledger_log"] for x in members if x["__ledger_log"] is not None]
        lower_value=None if inf else min(finite)
        lower=_n(None,"POSITIVE_ASSUMED_RUIN_MASS",True) if inf else _n(Fraction(lower_value))
        displayed=lower["value"]
        ids=[x["distribution_id"] for x in members if x["annual_log_growth"]["kind"]=="NEGATIVE_INFINITY" if inf] if inf else [x["distribution_id"] for x in members if x["annual_log_growth"]["value"]==displayed]
        r={"alternative_id":alt["alternative_id"],"role":alt["role"],"entry_cost_total":_n(cost),"post_trade_cash":_n(cash),"ordinary_paths":ordinary,"stress_paths":stress,"base_summary":summaries[0],"objective_member_summaries":members,"lower_envelope":lower,"lower_envelope_member_ids":ids,"difference_to_no_trade":None,"__lower_log":lower_value}
        alternatives.append(r)
        if alt["role"]=="NO_TRADE":no_trade=r
    for r in alternatives:
        if r["lower_envelope"]["kind"]!="FINITE" or no_trade["lower_envelope"]["kind"]!="FINITE":r["difference_to_no_trade"]=_n(None,"NONFINITE_COMPARISON")
        else:
            with localcontext() as context:
                context.prec=120; context.rounding=ROUND_HALF_EVEN
                difference=r["__lower_log"]-no_trade["__lower_log"]
            r["difference_to_no_trade"]=_n(Fraction(difference))
    benchmark=_benchmark_result(bundle)
    numerical={"logs":{},"groups":{},"differences":{}}
    def capture(owner:str,item:dict[str,Any]) -> None:
        for path in [*item["ordinary_paths"],*item["stress_paths"]]:
            numerical["logs"][f"{owner}/path/{path['path_id']}"]=path["__ledger_log"]
        summaries=[item["base_summary"],*item["objective_member_summaries"]]
        for summary in summaries:numerical["logs"][f"{owner}/distribution/{summary['distribution_id']}"]=summary["__ledger_log"]
        if item["__lower_log"] is not None:
            numerical["groups"][f"{owner}/lower"]=[f"{owner}/distribution/{summary['distribution_id']}" for summary in item["objective_member_summaries"]]
    for item in alternatives:capture(item["alternative_id"],item)
    capture("SYN_BENCHMARK",benchmark)
    no_trade_group=f"{no_trade['alternative_id']}/lower"
    for item in alternatives:
        own=f"{item['alternative_id']}/lower"
        if own in numerical["groups"] and no_trade_group in numerical["groups"]:
            numerical["differences"][item["alternative_id"]]=(own,no_trade_group)
    _verify_numerical_payload(numerical)
    for r in alternatives:
        del r["__lower_log"]
        for summary in [r["base_summary"],*r["objective_member_summaries"]]: del summary["__ledger_log"]
        for path in [*r["ordinary_paths"],*r["stress_paths"]]: del path["__ledger_log"];del path["__terminal_ratio"]
    del benchmark["__lower_log"]
    for summary in [benchmark["base_summary"],*benchmark["objective_member_summaries"]]:del summary["__ledger_log"]
    for path in [*benchmark["ordinary_paths"],*benchmark["stress_paths"]]:del path["__ledger_log"];del path["__terminal_ratio"]
    return {"alternatives":alternatives,"benchmark":benchmark,"unavailable":[{"component":x,"status":"NOT VERIFIED","reason":y} for x,y in UNAVAILABLE]}

def _benchmark_result(bundle: dict[str, Any]) -> dict[str, Any]:
    """Comparator-only accounting: no holdings, cost, fractions, or weight."""
    def build(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
      by_id={x["path_id"]:x for x in rows}; output=[]
      for pid in sorted(by_id):
        levels=[_d(x,"") for x in by_id[pid]["levels"]]
        wealth=[Fraction(1_000_000)*x for x in levels]
        peak=wealth[0]; dd=Fraction(); anchor=(0,"PRE_TRADE"); opened=None; episodes=[]
        events=[]
        for month,w in enumerate(wealth):
            events.append({"month":month,"wealth":_n(w),"wealth_state":"POSITIVE" if w else "ZERO"})
            if w>peak: peak=w
            dd=max(dd,1-w/peak)
            if month==0: continue
            if w>=peak:
                if opened:
                    pm,pk=opened;episodes.append({"peak_month":pm,"peak_event_kind":pk,"recovered_month":month,"recovered_event_kind":"MONTH","observed_until_month":month,"duration_months":month-pm,"right_censored":False});opened=None
                peak=w;anchor=(month,"MONTH")
            elif opened is None: opened=anchor
        if opened:
            pm,pk=opened;episodes.append({"peak_month":pm,"peak_event_kind":pk,"recovered_month":None,"recovered_event_kind":None,"observed_until_month":84,"duration_months":None,"right_censored":True})
        terminal=wealth[-1]
        if terminal:
            ratio=terminal/Fraction(1_000_000); exact_log=_decimal_log_value(ratio)
            path_log=_n(Fraction(exact_log));path_cagr=_n(_verified_exp_growth(exact_log))
        else:
            ratio=None;exact_log=None;path_log=_n(None,"ZERO_TERMINAL_WEALTH",True);path_cagr=_n(Fraction(-1))
        output.append({"path_id":pid,"events":events,"terminal_wealth":_n(terminal),"terminal_state":"POSITIVE" if terminal else "ZERO","path_log_growth":path_log,"path_cagr":path_cagr,"sampled_max_drawdown":_n(dd),"recovery_episodes":episodes,"__ledger_log":exact_log,"__terminal_ratio":ratio})
      return output
    ordinary=build(bundle["benchmark"]["ordinary_paths"])
    stress=build(bundle["benchmark"]["stress_paths"])
    paths={x["path_id"]:x for x in ordinary}; summaries=[]
    for dist in [bundle["probability_family"]["base"]]+bundle["probability_family"]["objective_members"]:
        masses={x["path_id"]:_d(x["probability"],"") for x in dist["masses"]}; ruin=sum(masses[k] for k,p in paths.items() if p["terminal_state"]=="ZERO")
        if ruin: log=_n(None,"POSITIVE_ASSUMED_RUIN_MASS",True); geo=_n(Fraction(-1))
        else:
            exact=_verified_distribution_log(masses,paths);log=_n(Fraction(exact));geo=_n(_verified_exp_growth(exact))
        summaries.append({"distribution_id":dist["distribution_id"],"annual_log_growth":log,"geometric_equivalent_growth_under_assumption":geo,"synthetic_zero_wealth_mass":_n(ruin),"__ledger_log":None if ruin else exact})
    members=summaries[1:]; inf=any(x["annual_log_growth"]["kind"]=="NEGATIVE_INFINITY" for x in members)
    lower_value=None if inf else min(x["__ledger_log"] for x in members)
    lower=_n(None,"POSITIVE_ASSUMED_RUIN_MASS",True) if inf else _n(Fraction(lower_value))
    displayed=lower["value"]
    ids=[x["distribution_id"] for x in members if x["annual_log_growth"]["kind"]=="NEGATIVE_INFINITY"] if inf else [x["distribution_id"] for x in members if x["annual_log_growth"]["value"]==displayed]
    return {"benchmark_id":"SYN_BENCHMARK","ordinary_paths":ordinary,"stress_paths":stress,"base_summary":summaries[0],"objective_member_summaries":members,"lower_envelope":lower,"lower_envelope_member_ids":ids,"__lower_log":lower_value}

def evaluate_bytes(raw: bytes) -> dict[str,Any]:
    try: prov=_provenance()
    except LabError as e:return _failure(e.code,e.path,e.status)
    try:
        bundle=_decode(raw)
        stage5=_stage5_findings(bundle)
        if stage5:return {"schema_version":"RESEARCH_WEALTH_LAB_RESULT_V1","input_sha256":None,"provenance":prov,"status":"INVALID_INPUT","boundaries":BOUNDARIES,"findings":stage5,"result":None}
        canonical_input=_normalize_bundle(bundle)
        bundle=canonical_input
        missing=_find_missing(bundle)
        h=sha256(canonical_bytes(canonical_input)).hexdigest()
        if missing:return {"schema_version":"RESEARCH_WEALTH_LAB_RESULT_V1","input_sha256":h,"provenance":prov,"status":"INPUT_INCOMPLETE","boundaries":BOUNDARIES,"findings":sorted(missing,key=lambda x:(x["path"],x["code"])),"result":None}
        try:
            bundle,prices=_check_bundle(bundle,validate_cross=False)
        except LabError as e:
            # Cross-record failures are reached only after a fully typed,
            # present Bundle, so their canonical input identity is available.
            cross={"INITIAL_WEALTH_MISMATCH","PROBABILITY_SUM","NO_TRADE_MISMATCH","COST_WITHOUT_TRADE","TERMINAL_ZERO_REVERSAL","UNFUNDED_ALTERNATIVE"}
            if not missing and e.code in cross:
                h=sha256(canonical_bytes(canonical_input)).hexdigest()
                return _failure(e.code,e.path,e.status,prov,h)
            raise
        normalized=canonical_input
        cross=_cross_record_findings(bundle,prices)
        if cross:return {"schema_version":"RESEARCH_WEALTH_LAB_RESULT_V1","input_sha256":h,"provenance":prov,"status":"INVALID_INPUT","boundaries":BOUNDARIES,"findings":cross,"result":None}
        try:
            result=_evaluate(bundle,prices)
            ev={"schema_version":"RESEARCH_WEALTH_LAB_RESULT_V1","input_sha256":h,"provenance":prov,"status":"COMPUTED_SYNTHETIC","boundaries":BOUNDARIES,"findings":[],"result":result}
            artifact={"artifact_version":"RESEARCH_WEALTH_LAB_ARTIFACT_V1","input":normalized,"evaluation":ev};artifact["artifact_sha256"]=sha256(canonical_bytes(artifact)).hexdigest()
            try:
                # A single invocation cannot emit provenance for bytes that
                # changed while numerical work was in progress.
                _provenance()
            except LabError as authority_error:
                return _failure(authority_error.code,"",authority_error.status)
            _check_serialized_sizes(canonical_bytes(ev),canonical_bytes(artifact))
            return artifact
        except LabError as e:
            return _failure(e.code,e.path,e.status,prov,h)
        except Exception:
            return _failure("ACCOUNTING_INVARIANT","","INTERNAL_ERROR",prov,h)
    except LabError as e:return _failure(e.code,e.path,e.status,prov if e.code.startswith("JSON") else None,None)
    except Exception:return _failure("INTERNAL_ERROR","","INTERNAL_ERROR",prov,None)

def example_bytes()->bytes:
    """Return the canonical BASE Bundle, never a transport-specific rewrite."""
    _provenance()
    raw=(ROOT/"optivest/fixtures/wealth_lab_example.json").read_bytes()
    bundle=_decode(raw); findings=_stage5_findings(bundle)
    if findings: raise LabError("SOURCE_UNAVAILABLE","","INTERNAL_ERROR")
    result=canonical_bytes(_normalize_bundle(bundle))
    _provenance()
    return result
def capabilities()->dict[str,Any]:
    p=_provenance()
    result={"schema_version":"RESEARCH_WEALTH_LAB_CAPABILITIES_V1","input_schema_version":SCHEMA,"result_schema_version":"RESEARCH_WEALTH_LAB_RESULT_V1","artifact_schema_version":"RESEARCH_WEALTH_LAB_ARTIFACT_V1","method_version":METHOD,"canonicalization_version":CANON,"mandate_assumption":{"reference":"ADR-0012_SYNTHETIC_SUBSET","horizon_months":84,"base_currency":"USD","nominal_real":"NOMINAL","tax_treatment":"PRE_TAX","external_flows":"SELF_FINANCING_NONE","initial_wealth":"1000000","unit_semantics":"FRACTIONAL_BUY_AND_HOLD"},"bounds":{"input_bytes":4194304,"json_depth":16,"json_nodes":100000,"assets_min":2,"assets_max":4,"ordinary_paths_min":1,"ordinary_paths_max":16,"stress_paths_max":4,"alternatives_min":3,"alternatives_max":8,"objective_members_min":1,"objective_members_max":4,"horizon_months":84,"derived_significant_digits":40,"evaluation_bytes":33554432,"artifact_bytes":41943040},"boundaries":BOUNDARIES,"unavailable":[{"component":x,"status":"NOT VERIFIED","reason":y} for x,y in UNAVAILABLE],"provenance":p}
    _provenance()
    return result

# Freeze the source identity when this module context finishes initializing.
try:
    _LOADED_SOURCE_HASHES=_authority_context()
except LabError:
    _LOADED_SOURCE_HASHES=None
