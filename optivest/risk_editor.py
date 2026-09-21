"""Frozen RESEARCH-RISK-EDITOR-V1 declaration grammar and persistence helpers.

This module deliberately contains no forecast, calibration, feasibility or
optimizer implementation.  It only stores a fail-closed research declaration.
"""
from __future__ import annotations
import hashlib, json, re, math
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session
from .models import (RiskBudgetVersion, RiskConstraint, ResearchProfile,
    ProfileHead, MandateVersion, ResearchRiskEditorMarker,
    ResearchRiskEditorDocument, uid, utcnow)

SCHEMA="RESEARCH_RISK_EDITOR_V1"
POLICY_HASH="ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67"
DECIMAL=re.compile(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,6})?$")
UTC_MICROSECOND=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
METRICS=[
 ("MAX_SINGLE_NAME_EQUITY","STRUCTURAL_HARD","<=",["PERCENT"],"10","12.5","H"),("PASSIVE_MARKET_IMPLEMENTATION","STRUCTURAL_HARD","<=",["PERCENT"],"100","100","H"),("MAX_SECTOR_INDUSTRY","STRUCTURAL_HARD","<=",["PERCENT"],"30","35","H"),("MAX_FACTOR_CLUSTER","HYBRID","<=",["PERCENT"],"35","40","H"),("MAX_MODELED_DRAWDOWN","MODEL_ESTIMATED","<=",["PERCENT"],"25","30","H"),("MAX_STRESS_DRAWDOWN","STRESS","<=",["PERCENT"],"35","45","S"),("MAX_RECOVERY_DURATION","MODEL_ESTIMATED","<=",["MONTHS"],"36","48","H"),("MAX_DAYS_TO_LIQUIDATE","HYBRID","<=",["TRADING_DAYS"],"5","5","N"),("MAX_PARTICIPATION_RATE","STRUCTURAL_HARD","<=",["PERCENT_ADV"],"10","10","N"),("CASH_ALLOCATION","STRUCTURAL_HARD","<=",["PERCENT"],"100","100","H"),("LEVERAGE","STRUCTURAL_HARD","<=",["PERCENT"],"0","0","A"),("RISK_FREE_PROXY_ALLOCATION","STRUCTURAL_HARD","<=",["PERCENT"],"100","100","H"),("PORTFOLIO_CVAR","MODEL_ESTIMATED","<=",["PERCENT"],None,None,"?"),("SEVERE_LOSS_PROBABILITY","MODEL_ESTIMATED","<=",["PROBABILITY"],None,None,"?"),("PERMANENT_LOSS_EXPOSURE","MODEL_ESTIMATED","<=",["PERCENT","PROBABILITY"],None,None,"?"),("MAX_TURNOVER_IMPLEMENTATION_COST","HYBRID","<=",[],None,None,"?"),("PORTFOLIO_JOINT_MATERIAL_RISK","MODEL_ESTIMATED","<=",["PROBABILITY"],None,None,"?"),("MIN_LIQUIDITY","HYBRID",">=",["CURRENCY","TRADING_DAYS"],None,None,"N"),("MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE","STRUCTURAL_HARD",">=",["PROBABILITY"],None,None,"?")]
CAT={m[0]:m for m in METRICS}; ALLOC={"PASSIVE_MARKET_IMPLEMENTATION","CASH_ALLOCATION","RISK_FREE_PROXY_ALLOCATION"}

class EditorError(ValueError):
    def __init__(self, code:str, path:str=""):
        self.code,self.path=code,path; super().__init__(code)
class EditorConflict(EditorError): pass
class EditorStorageError(EditorError): pass
def _pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise EditorError("JSON_DUPLICATE_KEY",f"/{k}")
        d[k]=v
    return d
def strict_decode(raw:bytes)->Any:
    if len(raw)>1048576: raise EditorError("JSON_SIZE")
    if raw.startswith(b"\xef\xbb\xbf"): raise EditorError("JSON_ENCODING")
    try: value=json.loads(raw.decode("utf-8","strict"),object_pairs_hook=_pairs,parse_float=Decimal,parse_constant=lambda _:(_ for _ in ()).throw(EditorError("JSON_INVALID")))
    except EditorError: raise
    except UnicodeDecodeError: raise EditorError("JSON_ENCODING")
    except json.JSONDecodeError: raise EditorError("JSON_INVALID")
    nodes=0
    def walk(x,depth=0):
        nonlocal nodes; nodes+=1
        if depth>20: raise EditorError("JSON_DEPTH")
        if nodes>10000: raise EditorError("JSON_SIZE")
        if isinstance(x,dict): [walk(v,depth+1) for v in x.values()]
        elif isinstance(x,list): [walk(v,depth+1) for v in x]
    walk(value); return value
def canonical(value:Any)->str:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def m(value=None,reason="NOT_APPLICABLE"): return {"value":value,"reason":None if value is not None else reason}
def horizon(kind:str):
    if kind=="H": return m({"kind":"FIXED_PERIOD","unit":"YEARS","count":7,"event_clock":"DECISION_TO_HORIZON"})
    if kind=="S": return m({"kind":"FIXED_PERIOD","unit":"YEARS","count":7,"event_clock":"STRESS_SCENARIO_PATH"})
    if kind=="N": return m({"kind":"OBSERVATION","unit":None,"count":None,"event_clock":"NORMAL_LIQUIDATION_OBSERVATION"})
    if kind=="A": return m({"kind":"OBSERVATION","unit":None,"count":None,"event_clock":"ALWAYS"})
    return m(None,"DEFINITION_NOT_VERIFIED")
def _risk(cls,metric):
    if cls in {"STRUCTURAL_HARD","STRESS"} or metric=="MAX_TURNOVER_IMPLEMENTATION_COST": return {"mode":"NOT_APPLICABLE","epsilon":m(),"alpha":m(),"u_risk_version":m(),"buffer_value":m(),"buffer_rationale":m(),"calibration_reference":m()}
    return {"mode":"UNSPECIFIED",**{k:m(None,"SEMANTICS_NOT_VERIFIED") for k in ("epsilon","alpha","u_risk_version","buffer_value","buffer_rationale","calibration_reference")}}
def _stress(metric):
    keys=("version","scenario_id","definition","severity")
    if metric=="MAX_STRESS_DRAWDOWN": return {"proposed_role":"UNSPECIFIED",**{k:m(None,"STRESS_NOT_VERIFIED") for k in keys}}
    return {"proposed_role":"NOT_APPLICABLE",**{k:m() for k in keys}}
def _hybrid(metric,cls):
    keys=("observed_component","estimated_component","normal_liquidity_assumption","stress_liquidity_assumption","participation_assumption")
    if cls=="HYBRID" and metric!="MAX_TURNOVER_IMPLEMENTATION_COST":
        out={k:m(None,"HYBRID_COMPONENT_NOT_VERIFIED") if k in keys[:2] or metric in {"MAX_DAYS_TO_LIQUIDATE","MIN_LIQUIDITY"} else m() for k in keys}; return out
    return {k:m() for k in keys}
def template(preset="BALANCED_RESEARCH_V1"):
    if preset not in {"BALANCED_RESEARCH_V1","GROWTH_RESEARCH_V1"}: raise EditorError("PRESET_INVALID","/source_preset")
    index=5 if preset.startswith("GROWTH") else 4; rows=[]
    for metric,cls,op,units,b,g,clock in METRICS:
        unit=m(units[0],"NOT_APPLICABLE") if len(units)==1 else m(None,"DEFINITION_NOT_VERIFIED")
        limit=m(g if preset.startswith("GROWTH") else b,"CALIBRATION_NOT_VERIFIED") if (b is not None) else m(None,"CALIBRATION_NOT_VERIFIED")
        minimum=m("0","NOT_APPLICABLE") if metric in ALLOC else m()
        if metric=="MAX_TURNOVER_IMPLEMENTATION_COST": unit=m(); limit=m(); minimum=m()
        components=[]
        if metric=="MAX_TURNOVER_IMPLEMENTATION_COST":
            components=[{"component_id":x,"definition":m(None,"DEFINITION_NOT_VERIFIED"),"unit":m(None,"DEFINITION_NOT_VERIFIED"),"currency":m(),"horizon":m(None,"DEFINITION_NOT_VERIFIED"),"estimation_method":m(None,"DEFINITION_NOT_VERIFIED"),"data_window":m(None,"DEFINITION_NOT_VERIFIED"),"limit":m(None,"DEFINITION_NOT_VERIFIED"),"warning":m(None,"DEFINITION_NOT_VERIFIED")} for x in ("TURNOVER","IMPLEMENTATION_COST")]
        aggregate=metric=="MAX_TURNOVER_IMPLEMENTATION_COST"
        rows.append({"metric":metric,"constraint_class":cls,"operator":op,
            "definition":m("Legacy aggregate; inspect separate turnover and implementation cost declarations") if aggregate else m(None,"DEFINITION_NOT_VERIFIED"),
            "unit":unit,"currency":m(),"horizon":m() if aggregate else horizon(clock),
            "estimation_method":m() if aggregate else m(None,"DEFINITION_NOT_VERIFIED"),
            "data_window":m() if aggregate else m(None,"DEFINITION_NOT_VERIFIED"),
            "confidence_level":m() if aggregate else m(None,"DEFINITION_NOT_VERIFIED"),
            "limit":limit,"warning":m() if aggregate else m(None,"DEFINITION_NOT_VERIFIED"),"minimum":minimum,
            "risk":_risk(cls,metric),"stress":_stress(metric),"hybrid":_hybrid(metric,cls),"components":components})
    return {"source_preset":preset,"constraints":rows,"joint_groups":[]}

def _expect(obj,keys,path):
    if not isinstance(obj,dict): raise EditorError("TYPE_INVALID",path)
    if set(obj)!=set(keys): raise EditorError("UNKNOWN_FIELD" if set(obj)-set(keys) else "REQUIRED_FIELD",path)
def _decimal(x,path,prob=False):
    if not isinstance(x,str) or not DECIMAL.fullmatch(x): raise EditorError("DECIMAL_INVALID",path)
    if Decimal(x)<0 or (prob and not (Decimal(0)<Decimal(x)<Decimal(1))): raise EditorError("RANGE_INVALID",path)
    # Never strip integral zeroes: 100 is a materially different declaration
    # from 1.  Decimal's fixed-point form leaves only a fractional suffix to
    # normalize.
    fixed=format(Decimal(x),"f")
    if "." in fixed: fixed=fixed.rstrip("0").rstrip(".")
    return fixed
def _validate_m(v,path,decimal=False,text_value=False,max_length=2048):
    _expect(v,("value","reason"),path); value,reason=v["value"],v["reason"]
    if value is None:
        if not isinstance(reason,str) or not reason.strip() or len(reason.strip())>512: raise EditorError("NULL_REASON_INVALID",path+"/reason")
        v["reason"]=reason.strip()
    elif reason is not None: raise EditorError("NULL_REASON_INVALID",path+"/reason")
    if decimal and value is not None: v["value"]=_decimal(value,path+"/value")
    if text_value and value is not None:
        if not isinstance(value,str) or not value.strip() or len(value.strip())>max_length:
            raise EditorError("TEXT_INVALID",path+"/value")
        v["value"]=value.strip()

def _not_applicable(value):
    return value["value"] is None and value["reason"]=="NOT_APPLICABLE"

def _require_applicable_m(value, path):
    """`NOT_APPLICABLE` is reserved for fields excluded by the selected mode."""
    if _not_applicable(value):
        raise EditorError("FIELD_NOT_APPLICABLE",path)

def _horizon_matches(value, *, kind=None, event_clock=None):
    if value is None:
        return True
    if kind is not None and value["kind"]!=kind:
        return False
    return event_clock is None or value["event_clock"]==event_clock

def _row_horizon_is_allowed(metric, value):
    """Apply the catalog's deliberately non-convertible clock rules."""
    if value is None:
        return True
    if metric in {"MAX_DAYS_TO_LIQUIDATE","MAX_PARTICIPATION_RATE","MIN_LIQUIDITY"}:
        return _horizon_matches(value,kind="OBSERVATION",event_clock="NORMAL_LIQUIDATION_OBSERVATION")
    if metric=="LEVERAGE":
        return _horizon_matches(value,kind="OBSERVATION",event_clock="ALWAYS")
    if metric=="MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE":
        return _horizon_matches(value,kind="OBSERVATION",event_clock="CURRENT_PORTFOLIO")
    if metric=="MAX_STRESS_DRAWDOWN":
        return _horizon_matches(value,kind="FIXED_PERIOD",event_clock="STRESS_SCENARIO_PATH")
    if metric=="MAX_TURNOVER_IMPLEMENTATION_COST":
        return False
    # The remaining fixed-period rows, including the modeled/joint rows, use
    # the declaration clock rather than a silently converted observation.
    return _horizon_matches(value,kind="FIXED_PERIOD",event_clock="DECISION_TO_HORIZON")
def _validate_h(v,path):
    _validate_m(v,path)
    if v["value"] is None:return
    h=v["value"]; _expect(h,("kind","unit","count","event_clock"),path+"/value")
    if h["kind"]=="FIXED_PERIOD":
        if h["unit"] not in {"DAYS","TRADING_DAYS","MONTHS","YEARS"} or type(h["count"]) is not int or isinstance(h["count"],bool) or not 1<=h["count"]<=12000 or h["event_clock"] not in {"DECISION_TO_HORIZON","STRESS_SCENARIO_PATH"}:raise EditorError("HORIZON_INVALID",path)
    elif h["kind"]=="OBSERVATION":
        if h["unit"] is not None or h["count"] is not None or h["event_clock"] not in {"CURRENT_PORTFOLIO","NORMAL_LIQUIDATION_OBSERVATION","ALWAYS"}:raise EditorError("HORIZON_INVALID",path)
    else: raise EditorError("HORIZON_INVALID",path)
def validate_declaration(d):
    _expect(d,("source_preset","constraints","joint_groups"),"/declaration")
    if d["source_preset"] not in {"BALANCED_RESEARCH_V1","GROWTH_RESEARCH_V1"}:raise EditorError("PRESET_INVALID","/declaration/source_preset")
    if not isinstance(d["constraints"],list) or len(d["constraints"])!=19:raise EditorError("METRIC_SET_INVALID","/declaration/constraints")
    seen=set()
    rowkeys=("metric","constraint_class","operator","definition","unit","currency","horizon","estimation_method","data_window","confidence_level","limit","warning","minimum","risk","stress","hybrid","components")
    for i,row in enumerate(d["constraints"]):
        p=f"/declaration/constraints/{i}";_expect(row,rowkeys,p); metric=row["metric"]
        if metric not in CAT or metric in seen:raise EditorError("METRIC_SET_INVALID",p+"/metric")
        seen.add(metric); spec=CAT[metric]
        if (row["constraint_class"],row["operator"])!=(spec[1],spec[2]):raise EditorError("CLASS_OR_OPERATOR_INVALID",p)
        for key in ("definition","unit","currency","estimation_method","data_window","confidence_level","limit","warning","minimum"):
            _validate_m(row[key],p+"/"+key, key in {"limit","warning","minimum","confidence_level"}, key in {"definition","currency","estimation_method","data_window"})
        for key in ("definition","estimation_method","data_window"):
            value=row[key]["value"]
            if value is not None and (not isinstance(value,str) or not value.strip() or len(value)>2048):raise EditorError("TEXT_INVALID",p+"/"+key)
        _validate_h(row["horizon"],p+"/horizon")
        if row["unit"]["value"] is not None and (not isinstance(row["unit"]["value"],str) or row["unit"]["value"] not in spec[3]):raise EditorError("UNIT_INVALID",p+"/unit")
        if row["unit"]["value"]=="CURRENCY":
            currency=row["currency"]
            if currency["value"] is not None and (not isinstance(currency["value"],str) or not re.fullmatch(r"[A-Z]{3}",currency["value"])):raise EditorError("UNIT_INVALID",p+"/currency")
            if currency["value"] is None and currency["reason"]=="NOT_APPLICABLE":raise EditorError("FIELD_NOT_APPLICABLE",p+"/currency")
        elif row["currency"]["value"] is not None or row["currency"]["reason"]!="NOT_APPLICABLE":raise EditorError("FIELD_NOT_APPLICABLE",p+"/currency")
        if row["unit"]["value"] is None and any(row[k]["value"] is not None for k in ("limit","warning","minimum")):raise EditorError("FIELD_NOT_APPLICABLE",p)
        if row["confidence_level"]["value"] is not None and not Decimal(0)<Decimal(row["confidence_level"]["value"])<Decimal(1):
            raise EditorError("RANGE_INVALID",p+"/confidence_level")
        if metric not in ALLOC and not _not_applicable(row["minimum"]):raise EditorError("FIELD_NOT_APPLICABLE",p+"/minimum")
        if metric=="MAX_TURNOVER_IMPLEMENTATION_COST":
            expected_definition="Legacy aggregate; inspect separate turnover and implementation cost declarations"
            if row["definition"]!={"value":expected_definition,"reason":None}:
                raise EditorError("FIELD_NOT_APPLICABLE",p+"/definition")
            for key in ("unit","currency","horizon","estimation_method","data_window","confidence_level","limit","warning","minimum"):
                if not _not_applicable(row[key]): raise EditorError("FIELD_NOT_APPLICABLE",p+"/"+key)
            if [x.get("component_id") for x in row["components"]] != ["TURNOVER","IMPLEMENTATION_COST"]:raise EditorError("METRIC_SET_INVALID",p+"/components")
            ckeys=("component_id","definition","unit","currency","horizon","estimation_method","data_window","limit","warning")
            for j,component in enumerate(row["components"]):
                _expect(component,ckeys,p+f"/components/{j}")
                for key in ckeys[1:]:
                    if key=="horizon":_validate_h(component[key],p+f"/components/{j}/{key}")
                    else:_validate_m(component[key],p+f"/components/{j}/{key}",key in {"limit","warning"},key in {"definition","currency","estimation_method","data_window"})
                allowed_units={"TURNOVER":{"PERCENT"},"IMPLEMENTATION_COST":{"PERCENT","CURRENCY"}}[component["component_id"]]
                if component["unit"]["value"] is not None and (not isinstance(component["unit"]["value"],str) or component["unit"]["value"] not in allowed_units):raise EditorError("UNIT_INVALID",p+f"/components/{j}/unit")
                for key in ("definition","estimation_method","data_window"):
                    value=component[key]["value"]
                    if value is not None and (not isinstance(value,str) or not value.strip() or len(value)>2048):raise EditorError("TEXT_INVALID",p+f"/components/{j}/"+key)
                ch=component["horizon"]["value"]
                if ch is not None and (ch["kind"]!="FIXED_PERIOD" or ch["event_clock"]!="DECISION_TO_HORIZON"):raise EditorError("HORIZON_INVALID",p+f"/components/{j}/horizon")
                if component["unit"]["value"]=="CURRENCY":
                    cv=component["currency"]["value"]
                    if cv is not None and (not isinstance(cv,str) or not re.fullmatch(r"[A-Z]{3}",cv)):raise EditorError("UNIT_INVALID",p+f"/components/{j}/currency")
                    if cv is None and component["currency"]["reason"]=="NOT_APPLICABLE":raise EditorError("FIELD_NOT_APPLICABLE",p+f"/components/{j}/currency")
                elif component["currency"]["value"] is not None or component["currency"]["reason"]!="NOT_APPLICABLE":raise EditorError("FIELD_NOT_APPLICABLE",p+f"/components/{j}/currency")
                if component["unit"]["value"] is None and any(component[k]["value"] is not None for k in ("limit","warning")):
                    raise EditorError("FIELD_NOT_APPLICABLE",p+f"/components/{j}")
                for key in ("limit","warning"):
                    value=component[key]["value"]
                    unit=component["unit"]["value"]
                    if value is not None and unit=="PERCENT" and Decimal(value)>100:
                        raise EditorError("RANGE_INVALID",p+f"/components/{j}/{key}")
                    if value is not None and unit=="CURRENCY" and Decimal(value)<=0:
                        raise EditorError("RANGE_INVALID",p+f"/components/{j}/{key}")
        elif row["components"]:raise EditorError("FIELD_NOT_APPLICABLE",p+"/components")
        r=row["risk"]; _expect(r,("mode","epsilon","alpha","u_risk_version","buffer_value","buffer_rationale","calibration_reference"),p+"/risk")
        for key in r:
            if key!="mode":_validate_m(r[key],p+"/risk/"+key,key in {"epsilon","alpha","buffer_value"},key in {"u_risk_version","buffer_rationale","calibration_reference"},128 if key=="u_risk_version" else 2048)
        if spec[1] in {"STRUCTURAL_HARD","STRESS"} or metric=="MAX_TURNOVER_IMPLEMENTATION_COST":
            if r["mode"]!="NOT_APPLICABLE" or any(v["value"] is not None or v["reason"]!="NOT_APPLICABLE" for k,v in r.items() if k!="mode"):raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/risk")
        elif r["mode"] not in {"UNSPECIFIED","ROBUST_CHANCE","ROBUST_QUANTILE","EQUIVALENT_BUFFER"}:raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/risk/mode")
        elif r["mode"]=="UNSPECIFIED":
            if any(v["value"] is not None or v["reason"]!="SEMANTICS_NOT_VERIFIED" for k,v in r.items() if k!="mode"):raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/risk")
        else:
            required={"ROBUST_CHANCE":{"epsilon","u_risk_version","calibration_reference"},"ROBUST_QUANTILE":{"alpha","u_risk_version","calibration_reference"},"EQUIVALENT_BUFFER":{"u_risk_version","buffer_value","buffer_rationale","calibration_reference"}}[r["mode"]]
            forbidden=set(r)-{"mode"}-required
            if any(r[k]["value"] is not None or r[k]["reason"]!="NOT_APPLICABLE" for k in forbidden):raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/risk")
            for key in required:_require_applicable_m(r[key],p+"/risk/"+key)
            if r["mode"]=="ROBUST_CHANCE" and r["epsilon"]["value"] is not None and not Decimal(0)<Decimal(r["epsilon"]["value"])<Decimal(1):raise EditorError("RANGE_INVALID",p+"/risk/epsilon")
            if r["mode"]=="ROBUST_QUANTILE" and r["alpha"]["value"] is not None and not Decimal(0)<Decimal(r["alpha"]["value"])<Decimal(1):raise EditorError("RANGE_INVALID",p+"/risk/alpha")
            if r["mode"]=="EQUIVALENT_BUFFER":
                value=r["buffer_value"]["value"]
                if row["unit"]["value"] is None and value is not None: raise EditorError("FIELD_NOT_APPLICABLE",p+"/risk/buffer_value")
                if value is not None:
                    if Decimal(value)<0: raise EditorError("RANGE_INVALID",p+"/risk/buffer_value")
                    if row["unit"]["value"] in {"PERCENT","PERCENT_ADV"} and Decimal(value)>100: raise EditorError("RANGE_INVALID",p+"/risk/buffer_value")
                    if row["unit"]["value"]=="PROBABILITY" and not Decimal(0)<Decimal(value)<Decimal(1): raise EditorError("RANGE_INVALID",p+"/risk/buffer_value")
        s=row["stress"];_expect(s,("proposed_role","version","scenario_id","definition","severity"),p+"/stress")
        for key in s:
            if key!="proposed_role":_validate_m(s[key],p+"/stress/"+key,text_value=True,max_length=128 if key in {"version","scenario_id"} else 2048)
        if metric!="MAX_STRESS_DRAWDOWN" and (s["proposed_role"]!="NOT_APPLICABLE" or any(v["value"] is not None or v["reason"]!="NOT_APPLICABLE" for k,v in s.items() if k!="proposed_role")):raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/stress")
        if metric=="MAX_STRESS_DRAWDOWN":
            if s["proposed_role"] not in {"UNSPECIFIED","DIAGNOSTIC","BINDING"}:raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/stress/proposed_role")
            if s["proposed_role"]=="UNSPECIFIED" and any(v["value"] is not None or v["reason"]!="STRESS_NOT_VERIFIED" for k,v in s.items() if k!="proposed_role"):
                raise EditorError("SEMANTICS_FIELDS_INVALID",p+"/stress")
            if s["proposed_role"] in {"DIAGNOSTIC","BINDING"}:
                for key in ("version","scenario_id","definition","severity"):_require_applicable_m(s[key],p+"/stress/"+key)
        h=row["hybrid"];_expect(h,("observed_component","estimated_component","normal_liquidity_assumption","stress_liquidity_assumption","participation_assumption"),p+"/hybrid")
        for key in h:_validate_m(h[key],p+"/hybrid/"+key,key=="participation_assumption",key!="participation_assumption")
        if spec[1]!="HYBRID" or metric=="MAX_TURNOVER_IMPLEMENTATION_COST":
                if any(v["value"] is not None or v["reason"]!="NOT_APPLICABLE" for v in h.values()):raise EditorError("FIELD_NOT_APPLICABLE",p+"/hybrid")
        elif metric=="MAX_FACTOR_CLUSTER":
            for key in ("normal_liquidity_assumption","stress_liquidity_assumption","participation_assumption"):
                if not _not_applicable(h[key]): raise EditorError("FIELD_NOT_APPLICABLE",p+"/hybrid/"+key)
        if spec[1]=="HYBRID" and metric!="MAX_TURNOVER_IMPLEMENTATION_COST":
            applicable={"observed_component","estimated_component"}
            if metric in {"MAX_DAYS_TO_LIQUIDATE","MIN_LIQUIDITY"}:
                applicable|={"normal_liquidity_assumption","stress_liquidity_assumption","participation_assumption"}
            for key in applicable:_require_applicable_m(h[key],p+"/hybrid/"+key)
        if h["participation_assumption"]["value"] is not None and Decimal(h["participation_assumption"]["value"])>100:raise EditorError("RANGE_INVALID",p+"/hybrid/participation_assumption")
        hv=row["horizon"]["value"]
        if not _row_horizon_is_allowed(metric,hv): raise EditorError("HORIZON_INVALID",p+"/horizon")
        for key in ("limit","warning","minimum"):
            value=row[key]["value"]
            if value is not None and row["unit"]["value"] in {"PERCENT","PERCENT_ADV"} and Decimal(value)>100:raise EditorError("RANGE_INVALID",p+"/"+key)
            if value is not None and row["unit"]["value"]=="PROBABILITY" and not Decimal(0)<Decimal(value)<Decimal(1):raise EditorError("RANGE_INVALID",p+"/"+key)
            if value is not None and row["unit"]["value"] in {"MONTHS","TRADING_DAYS","CURRENCY"} and Decimal(value)<=0:raise EditorError("RANGE_INVALID",p+"/"+key)
        for key in ("definition","currency","estimation_method","data_window","confidence_level"):
            if row[key]["value"] is None and row[key]["reason"]=="NOT_APPLICABLE" and key=="definition" and metric!="MAX_TURNOVER_IMPLEMENTATION_COST":raise EditorError("NULL_REASON_INVALID",p+"/"+key)
            if row[key]["value"] is not None and not isinstance(row[key]["value"],str):raise EditorError("TYPE_INVALID",p+"/"+key+"/value")
    if seen!=set(CAT):raise EditorError("METRIC_SET_INVALID","/declaration/constraints")
    if not isinstance(d["joint_groups"],list) or len(d["joint_groups"])>32:raise EditorError("JOINT_REFERENCE_INVALID","/declaration/joint_groups")
    joint_ids=set(); member_seen=set()
    for i,joint in enumerate(d["joint_groups"]):
        _expect(joint,("group_id","members","horizon","epsilon","u_risk_version","dependency_method","dependency_reference"),f"/declaration/joint_groups/{i}")
        if not isinstance(joint["group_id"],str) or not joint["group_id"].strip() or len(joint["group_id"].strip())>128:raise EditorError("JOINT_REFERENCE_INVALID",f"/declaration/joint_groups/{i}/group_id")
        joint["group_id"]=joint["group_id"].strip()
        if joint["group_id"] in joint_ids:raise EditorError("JOINT_REFERENCE_INVALID",f"/declaration/joint_groups/{i}/group_id")
        joint_ids.add(joint["group_id"])
        if not isinstance(joint["members"],list) or not joint["members"] or len(joint["members"])>18:raise EditorError("JOINT_REFERENCE_INVALID",f"/declaration/joint_groups/{i}/members")
        if len(joint["members"])!=len(set(joint["members"])) or any(x not in CAT or x=="PORTFOLIO_JOINT_MATERIAL_RISK" or CAT[x][1] not in {"MODEL_ESTIMATED","HYBRID"} for x in joint["members"]):raise EditorError("JOINT_REFERENCE_INVALID",f"/declaration/joint_groups/{i}/members")
        if member_seen.intersection(joint["members"]):raise EditorError("JOINT_REFERENCE_INVALID",f"/declaration/joint_groups/{i}/members")
        member_seen.update(joint["members"])
        _validate_h(joint["horizon"],f"/declaration/joint_groups/{i}/horizon")
        for key in ("epsilon","u_risk_version","dependency_method","dependency_reference"):
            _validate_m(joint[key],f"/declaration/joint_groups/{i}/"+key,key=="epsilon",key!="epsilon",128 if key=="u_risk_version" else 2048)
        if joint["epsilon"]["value"] is not None and not Decimal(0)<Decimal(joint["epsilon"]["value"])<Decimal(1):raise EditorError("RANGE_INVALID",f"/declaration/joint_groups/{i}/epsilon")
    d["constraints"].sort(key=lambda x:[m[0] for m in METRICS].index(x["metric"]))
    d["joint_groups"].sort(key=lambda x:x["group_id"])
    for joint in d["joint_groups"]:joint["members"].sort(key=lambda x:[m[0] for m in METRICS].index(x))
    return d
def normalize_request(data):
    legacy={"expected_current_version_id","mandate_version_id","rationale","status"}
    modern={"request_kind","schema_version","expected_current_version_id","mandate_version_id","rationale","declaration"}
    if not isinstance(data,dict): raise EditorError("TYPE_INVALID","")
    if not (set(data)<=legacy and {"expected_current_version_id","mandate_version_id","rationale"}<=set(data)):
        _expect(data,modern,"")
        if not isinstance(data["schema_version"],str) or data["schema_version"]!=SCHEMA: raise EditorError("TYPE_INVALID","/schema_version")
        if not isinstance(data["request_kind"],str) or data["request_kind"] not in {"FULL_DECLARATION","CLONE_CURRENT"}: raise EditorError("TYPE_INVALID","/request_kind")
        for key in ("expected_current_version_id","mandate_version_id"):
            if not isinstance(data[key],str) or not data[key].strip() or len(data[key].strip())>128: raise EditorError("TYPE_INVALID","/"+key)
            data[key]=data[key].strip()
        if not isinstance(data["rationale"],str) or not data["rationale"].strip() or len(data["rationale"].strip())>2048: raise EditorError("TEXT_INVALID","/rationale")
        data["rationale"]=data["rationale"].strip()
        if data["request_kind"]=="FULL_DECLARATION":
            if data["declaration"] is None: raise EditorError("REQUIRED_FIELD","/declaration")
            validate_declaration(data["declaration"])
        elif data["declaration"] is not None: raise EditorError("FIELD_NOT_APPLICABLE","/declaration")
        return data
    if set(data)-legacy or ("status" in data and data["status"]!="PROVISIONAL"): raise EditorError("STATUS_FORBIDDEN","/status")
    for key in ("expected_current_version_id","mandate_version_id"):
        if not isinstance(data[key],str) or not data[key].strip() or len(data[key].strip())>128: raise EditorError("TYPE_INVALID","/"+key)
        data[key]=data[key].strip()
    if not isinstance(data["rationale"],str) or not data["rationale"].strip() or len(data["rationale"].strip())>2048: raise EditorError("TEXT_INVALID","/rationale")
    data["rationale"]=data["rationale"].strip()
    return {"request_kind":"CLONE_CURRENT","schema_version":SCHEMA,"expected_current_version_id":data["expected_current_version_id"],"mandate_version_id":data["mandate_version_id"],"rationale":data["rationale"],"declaration":None,"_legacy":True}
IMPACT_REASONS={"robust_utility":"UTILITY_ENGINE_UNAVAILABLE","expected_cagr":"FORECAST_WEALTH_MODEL_UNAVAILABLE","expected_twr":"FORECAST_WEALTH_MODEL_UNAVAILABLE","stress_drawdown":"RISK_MODEL_UNAVAILABLE","cvar":"RISK_MODEL_UNAVAILABLE","permanent_loss":"RISK_MODEL_UNAVAILABLE","joint_breach_probability":"JOINT_MODEL_UNAVAILABLE","cash_allocation":"OPTIMIZER_UNAVAILABLE","concentration":"OPTIMIZER_UNAVAILABLE","binding_constraint":"OPTIMIZER_UNAVAILABLE","shadow_price":"OPTIMIZER_UNAVAILABLE","defensive_opportunity_cost":"OPTIMIZER_UNAVAILABLE"}
def _impact(): return {key:{"value":None,"status":"NOT VERIFIED","reason":reason} for key,reason in IMPACT_REASONS.items()}
def _finding_key(finding):
    match=re.search(r"/constraints/(\d+)",finding["path"])
    ordinal=int(match.group(1)) if match else 1000
    return (0 if finding["severity"]=="ERROR" else 1,ordinal,finding["code"],finding["path"])
def diagnostics(d,mandate_horizon:int,current=True,legacy=False):
    findings=[]
    def add(code,path,severity="BLOCKER"):
        item={"code":code,"path":path,"severity":severity}
        if item not in findings: findings.append(item)
    for code,path in (
        ("RISK_BUDGET_NOT_APPROVED","/risk_budget_status"),("RISK_FEASIBILITY_NOT_VERIFIED","/feasibility_status"),
        ("MODEL_IMPACT_NOT_AVAILABLE","/impact"),("BENCHMARK_AVAILABILITY_NOT_VERIFIED","/mandate/benchmark_definition"),
        ("PASSIVE_IMPLEMENTATION_NOT_APPROVED","/mandate/passive_candidate"),("PASSIVE_LOOKTHROUGH_NOT_VERIFIED","/mandate/passive_candidate"),
        ("RISK_FREE_PROXY_NOT_APPROVED","/mandate/risk_free_proxy")):
        add(code,path)
    rows={r["metric"]:r for r in d["constraints"]}
    metric_order=[x[0] for x in METRICS]
    for index,metric in enumerate(metric_order):
        row=rows[metric]; p=f"/declaration/constraints/{index}"; lim=row["limit"]["value"];warn=row["warning"]["value"]
        if lim is not None and warn is not None and ((row["operator"]=="<=" and Decimal(warn)>Decimal(lim)) or (row["operator"]==">=" and Decimal(warn)<Decimal(lim))):add("LIMIT_WARNING_CONTRADICTION",p,"ERROR")
        if metric in ALLOC and lim is not None and row["minimum"]["value"] is not None and Decimal(row["minimum"]["value"])>Decimal(lim):add("ALLOCATION_RANGE_CONTRADICTION",p,"ERROR")
        if metric=="LEVERAGE" and lim!="0":add("LEVERAGE_FORBIDDEN",p,"ERROR")
        if metric=="MAX_SINGLE_NAME_EQUITY" and lim is not None and Decimal(lim)>Decimal("12.5"):add("SINGLE_NAME_SCOPE_EXCEEDED",p,"ERROR")
        applicable=["definition","unit","horizon","estimation_method","data_window","confidence_level","limit","warning"]
        if metric in ALLOC: applicable.append("minimum")
        if row["unit"]["value"]=="CURRENCY": applicable.append("currency")
        if metric=="MAX_TURNOVER_IMPLEMENTATION_COST": applicable=[]
        for key in applicable:
            if row[key]["value"] is None:add("FIELD_UNSPECIFIED",p+"/"+key)
        if metric=="MAX_TURNOVER_IMPLEMENTATION_COST":
            for component_index,component in enumerate(row["components"]):
                cp=f"{p}/components/{component_index}"
                for key in ("definition","unit","horizon","estimation_method","data_window","limit","warning"):
                    if component[key]["value"] is None:add("FIELD_UNSPECIFIED",cp+"/"+key)
                if component["unit"]["value"]=="CURRENCY" and component["currency"]["value"] is None:add("FIELD_UNSPECIFIED",cp+"/currency")
                climit,cwarning=component["limit"]["value"],component["warning"]["value"]
                if climit is not None and cwarning is not None and Decimal(cwarning)>Decimal(climit):add("LIMIT_WARNING_CONTRADICTION",cp,"ERROR")
        if row["risk"]["mode"]=="UNSPECIFIED":
            add("RISK_SEMANTICS_UNSPECIFIED",p+"/risk")
            add("RISK_CALIBRATION_NOT_VERIFIED",p+"/risk")
        elif row["risk"]["mode"]!="NOT_APPLICABLE":
            required={"ROBUST_CHANCE":("epsilon","u_risk_version","calibration_reference"),"ROBUST_QUANTILE":("alpha","u_risk_version","calibration_reference"),"EQUIVALENT_BUFFER":("u_risk_version","buffer_value","buffer_rationale","calibration_reference")}[row["risk"]["mode"]]
            incomplete=False
            for key in required:
                if row["risk"][key]["value"] is None:
                    add("FIELD_UNSPECIFIED",p+"/risk/"+key); incomplete=True
            if incomplete:add("RISK_SEMANTICS_INCOMPLETE",p+"/risk")
            add("RISK_CALIBRATION_NOT_VERIFIED",p+"/risk")
        if row["constraint_class"]=="HYBRID" and metric!="MAX_TURNOVER_IMPLEMENTATION_COST":
            add("HYBRID_COMPONENT_NOT_VERIFIED",p+"/hybrid")
            hybrid_keys=("observed_component","estimated_component")
            if metric in {"MAX_DAYS_TO_LIQUIDATE","MIN_LIQUIDITY"}: hybrid_keys+=("normal_liquidity_assumption","stress_liquidity_assumption","participation_assumption")
            for key in hybrid_keys:
                if row["hybrid"][key]["value"] is None:add("FIELD_UNSPECIFIED",p+"/hybrid/"+key)
        if metric=="MAX_STRESS_DRAWDOWN":
            role=row["stress"]["proposed_role"]
            if role=="UNSPECIFIED":add("STRESS_SEMANTICS_UNSPECIFIED",p+"/stress")
            elif any(row["stress"][key]["value"] is None for key in ("version","scenario_id","definition","severity")):
                add("STRESS_SEMANTICS_INCOMPLETE",p+"/stress")
                for key in ("version","scenario_id","definition","severity"):
                    if row["stress"][key]["value"] is None:add("FIELD_UNSPECIFIED",p+"/stress/"+key)
            add("STRESS_VALIDATION_NOT_VERIFIED",p+"/stress")
    mins=sum((Decimal(rows[x]["minimum"]["value"]) for x in ALLOC if rows[x]["minimum"]["value"] is not None),Decimal(0))
    if mins>100:add("ALLOCATION_MINIMUM_TOTAL","/declaration/constraints","ERROR")
    if d["source_preset"]=="GROWTH_RESEARCH_V1" and mandate_horizon<7:add("GROWTH_HORIZON_OUT_OF_SCOPE","/declaration/source_preset","ERROR")
    align=[]
    for index,metric in enumerate(metric_order):
        if metric not in {"MAX_MODELED_DRAWDOWN","MAX_RECOVERY_DURATION"}:align.append({"metric":metric,"status":"INDEPENDENT_CLOCK"});continue
        h=rows[metric]["horizon"]["value"]
        status="UNSPECIFIED" if h is None else ("DECLARED_MATCH" if h=={"kind":"FIXED_PERIOD","unit":"YEARS","count":mandate_horizon,"event_clock":"DECISION_TO_HORIZON"} else "DECLARED_MISMATCH")
        align.append({"metric":metric,"status":status})
        if status!="DECLARED_MATCH":add("RISK_HORIZON_"+("UNSPECIFIED" if status=="UNSPECIFIED" else "DECLARED_MISMATCH"),f"/declaration/constraints/{index}/horizon")
    if not current:add("MANDATE_BINDING_STALE","/mandate_version_id")
    row17_index=metric_order.index("PORTFOLIO_JOINT_MATERIAL_RISK")
    add("JOINT_RISK_NOT_VERIFIED",f"/declaration/constraints/{row17_index}")
    if not d["joint_groups"]:add("JOINT_DEFINITION_MISSING","/declaration/joint_groups")
    else:
        for joint_index,joint in enumerate(d["joint_groups"]):
            jp=f"/declaration/joint_groups/{joint_index}"
            required=("horizon","epsilon","u_risk_version","dependency_method","dependency_reference")
            if any(joint[key]["value"] is None for key in required):
                add("JOINT_DEFINITION_INCOMPLETE",jp)
                for key in required:
                    if joint[key]["value"] is None:add("FIELD_UNSPECIFIED",jp+"/"+key)
            group_horizon=joint["horizon"]["value"]
            member_horizons=[rows[member]["horizon"]["value"] for member in joint["members"]]
            if group_horizon is not None and all(value is not None for value in member_horizons) and any(value!=group_horizon for value in member_horizons):
                add("JOINT_HORIZON_CONTRADICTION",jp+"/horizon","ERROR")
            add("JOINT_RISK_NOT_VERIFIED",jp)
    ordered=sorted(findings,key=_finding_key)
    inconsistent=any(x["severity"]=="ERROR" for x in ordered)
    blockers=sorted({x["code"] for x in ordered if x["severity"]=="BLOCKER"}|({"RISK_BUDGET_INCONSISTENT"} if inconsistent else set()))
    return {"input_validation":"VALID","consistency_status":"RISK BUDGET INCONSISTENT" if inconsistent else "NO_KNOWN_CONTRADICTION","findings":ordered,"blockers":blockers,"mandate_version_binding":"CURRENT" if current else "STALE","risk_horizon_alignment":align,"feasibility_status":"NOT VERIFIED","impact":_impact(),"validation_status":"NOT VERIFIED","risk_budget_status":"RISK BUDGET NOT APPROVED","production_readiness":"NOT PRODUCTION READY"}

def legacy_diagnostics(rows,current=True):
    findings=[]
    for code,path in (("RISK_BUDGET_NOT_APPROVED","/risk_budget_status"),("RISK_FEASIBILITY_NOT_VERIFIED","/feasibility_status"),("MODEL_IMPACT_NOT_AVAILABLE","/impact"),("BENCHMARK_AVAILABILITY_NOT_VERIFIED","/mandate/benchmark_definition"),("PASSIVE_IMPLEMENTATION_NOT_APPROVED","/mandate/passive_candidate"),("PASSIVE_LOOKTHROUGH_NOT_VERIFIED","/mandate/passive_candidate"),("RISK_FREE_PROXY_NOT_APPROVED","/mandate/risk_free_proxy"),("LEGACY_BUDGET_NOT_VERIFIED","/editor_document_status")):
        findings.append({"code":code,"path":path,"severity":"BLOCKER"})
    if not current: findings.append({"code":"MANDATE_BINDING_STALE","path":"/mandate_version_id","severity":"BLOCKER"})
    for index,row in enumerate(rows):
        if row.metric in {"MIN_LIQUIDITY","MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE"} and row.operator=="<=":
            findings.append({"code":"LEGACY_COMPARATOR_UNVERIFIED","path":f"/constraints/{index}/operator","severity":"BLOCKER"})
    findings=sorted(findings,key=_finding_key)
    return {"input_validation":"VALID","consistency_status":"NO_KNOWN_CONTRADICTION","findings":findings,"blockers":sorted({x["code"] for x in findings}),"mandate_version_binding":"CURRENT" if current else "STALE","risk_horizon_alignment":[{"metric":metric,"status":"UNSPECIFIED" if metric in {"MAX_MODELED_DRAWDOWN","MAX_RECOVERY_DURATION"} else "INDEPENDENT_CLOCK"} for metric,*_ in METRICS],"feasibility_status":"NOT VERIFIED","impact":_impact(),"validation_status":"NOT VERIFIED","risk_budget_status":"RISK BUDGET NOT APPROVED","production_readiness":"NOT PRODUCTION READY"}
def derived_name(d):
    scrub=lambda x: {k:scrub(v) for k,v in x.items() if k!="reason"} if isinstance(x,dict) else [scrub(v) for v in x] if isinstance(x,list) else x
    for p,name in (("BALANCED_RESEARCH_V1","BALANCED_RESEARCH_V1"),("GROWTH_RESEARCH_V1","GROWTH_RESEARCH_V1")):
        if scrub(d)==scrub(template(p)):return name
    return "CUSTOM_RESEARCH"
def declaration_changes(before,after):
    changes=[]
    identity_changed=set()
    component_identity_changed=set()
    for a,b in zip(before.get("constraints",[]),after.get("constraints",[])):
        if a.get("metric")!=b.get("metric"): continue
        metric=a["metric"]
        ar,br=a.get("risk",{}),b.get("risk",{})
        ast,bst=a.get("stress",{}),b.get("stress",{})
        identity=("definition","unit","horizon","constraint_class","operator","estimation_method","data_window","confidence_level")
        if (any(a.get(k)!=b.get(k) for k in identity)
            or (ar.get("mode"),ar.get("u_risk_version")) != (br.get("mode"),br.get("u_risk_version"))
            or (ast.get("proposed_role"),ast.get("version"),ast.get("scenario_id")) != (bst.get("proposed_role"),bst.get("version"),bst.get("scenario_id"))):
            identity_changed.add(metric)
        old_components={x.get("component_id"):x for x in a.get("components",[]) if isinstance(x,dict)}
        new_components={x.get("component_id"):x for x in b.get("components",[]) if isinstance(x,dict)}
        for component_id in set(old_components)|set(new_components):
            old,new=old_components.get(component_id),new_components.get(component_id)
            if not isinstance(old,dict) or not isinstance(new,dict) or any(old.get(k)!=new.get(k) for k in ("component_id","definition","unit","horizon","estimation_method","data_window")):
                component_identity_changed.add((metric,component_id))
    def metric_at(path):
        parts=path.split("/")
        try:
            if len(parts)>4 and parts[1:3]==["declaration","constraints"]:
                index=int(parts[3]); rows=after.get("constraints",before.get("constraints",[]))
                return rows[index]["metric"]
        except (IndexError, TypeError, ValueError, KeyError): pass
        return None
    def walk(a,b,path):
        if isinstance(a,dict) and isinstance(b,dict):
            for key in sorted(set(a)|set(b)): walk(a.get(key),b.get(key),path+"/"+key)
        elif isinstance(a,list) and isinstance(b,list):
            for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+"/"+str(i))
            for i in range(min(len(a),len(b)),max(len(a),len(b))):changes.append({"path":path+"/"+str(i),"before":a[i] if i<len(a) else None,"after":b[i] if i<len(b) else None,"comparison":"NOT_COMPARABLE"})
        elif a!=b:
            comparison="NOT_COMPARABLE"
            metric=metric_at(path)
            spec=CAT.get(metric) if metric else None
            if metric in identity_changed:comparison="NOT_COMPARABLE"
            elif isinstance(a,str) and isinstance(b,str) and (path.endswith("/limit/value") or path.endswith("/warning/value") or path.endswith("/minimum/value") or path.endswith("/buffer_value/value")):
                increasing=Decimal(b)>Decimal(a)
                # An allocation minimum is always more restrictive when raised;
                # other limits follow their declared inequality direction.
                if path.endswith("/buffer_value/value"):
                    rows=after.get("constraints",before.get("constraints",[])); row=rows[int(path.split("/")[3])]
                    if row.get("risk",{}).get("mode")!="EQUIVALENT_BUFFER": comparison="NOT_COMPARABLE"
                    else: comparison="TIGHTER" if increasing else "LOOSER"
                elif "/components/" in path:
                    rows=after.get("constraints",before.get("constraints",[])); row=rows[int(path.split("/")[3])]
                    component=row.get("components",[])[int(path.split("/")[5])]
                    if (metric,component.get("component_id")) in component_identity_changed: comparison="NOT_COMPARABLE"
                    else: comparison="LOOSER" if increasing else "TIGHTER"
                else:
                    tighter_when_increasing=path.endswith("/minimum/value") or (spec and spec[2]==">=")
                    comparison="TIGHTER" if increasing==tighter_when_increasing else "LOOSER"
            changes.append({"path":path,"before":a,"after":b,"comparison":comparison})
    walk(before,after,"/declaration");return changes
def project(budget_id,d):
    out=[]
    for row in d["constraints"]:
        h=row["horizon"]["value"]
        hs="UNSPECIFIED" if h is None else ("always" if h["event_clock"]=="ALWAYS" else "normal" if h["event_clock"]=="NORMAL_LIQUIDATION_OBSERVATION" else "current_portfolio" if h["event_clock"]=="CURRENT_PORTFOLIO" else f"{h['count']} {h['unit'].lower().replace('_',' ')} [{h['event_clock']}]")
        r=row["risk"];s=row["stress"]
        out.append(RiskConstraint(risk_budget_version_id=budget_id,metric=row["metric"],constraint_class=row["constraint_class"],operator=row["operator"],unit=row["unit"]["value"] or "UNSPECIFIED",horizon=hs,limit_value=float(Decimal(row["limit"]["value"])) if row["limit"]["value"] is not None else None,warning_value=float(Decimal(row["warning"]["value"])) if row["warning"]["value"] is not None else None,epsilon=float(Decimal(r["epsilon"]["value"])) if r["epsilon"]["value"] is not None else None,alpha=float(Decimal(r["alpha"]["value"])) if r["alpha"]["value"] is not None else None,uncertainty_version=r["u_risk_version"]["value"],stress_version=s["version"]["value"],binding_status="DIAGNOSTIC",calibration_status="NOT_VERIFIED",missing_reason="LEGACY_AGGREGATE_SEPARATE_COMPONENTS" if row["metric"]=="MAX_TURNOVER_IMPLEMENTATION_COST" else "EDITOR_DECLARATION_UNVERIFIED"))
    return out
def envelope(budget,d):
    created=budget.created_at
    if not isinstance(created,datetime): raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if created.tzinfo is None: created=created.replace(tzinfo=timezone.utc)
    return {"schema_version":SCHEMA,"risk_budget_version_id":budget.id,"profile_id":budget.profile_id,"mandate_version_id":budget.mandate_version_id,"revision":budget.revision,"supersedes_version_id":budget.supersedes_version_id,"policy_hash":POLICY_HASH,"name":budget.name,"status":"PROVISIONAL","created_at":created.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),"declaration":d}
def get_document(session,budget):
    try: marker=session.get(ResearchRiskEditorMarker,budget.id);doc=session.get(ResearchRiskEditorDocument,budget.id)
    except (TypeError, ValueError): raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if bool(marker)!=bool(doc):raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if not marker:return None
    if marker.schema_version!=SCHEMA or doc.schema_version!=SCHEMA or not isinstance(marker.created_at,datetime) or not isinstance(doc.created_at,datetime):raise EditorStorageError("EDITOR_STORAGE_INVALID")
    try: raw=doc.canonical_document.encode(); value=strict_decode(raw)
    except (AttributeError, TypeError, ValueError, UnicodeError, EditorError) as exc: raise EditorStorageError("EDITOR_STORAGE_INVALID") from exc
    if hashlib.sha256(raw).hexdigest()!=marker.document_sha256:raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if canonical(value)!=doc.canonical_document:raise EditorStorageError("EDITOR_STORAGE_INVALID")
    required_envelope={"schema_version","risk_budget_version_id","profile_id","mandate_version_id","revision","supersedes_version_id","policy_hash","name","status","created_at","declaration"}
    if not isinstance(value,dict) or set(value)!=required_envelope or not isinstance(value.get("created_at"),str) or not UTC_MICROSECOND.fullmatch(value["created_at"]):raise EditorStorageError("EDITOR_STORAGE_INVALID")
    canonical_before_validation=canonical(value)
    try: validate_declaration(value["declaration"])
    except (EditorError, TypeError, ValueError, KeyError) as exc: raise EditorStorageError("EDITOR_STORAGE_INVALID") from exc
    # Validation canonicalizes catalog, joint-group and member ordering.  A
    # stored envelope that needed this rewrite was not canonical at creation.
    if canonical(value)!=canonical_before_validation: raise EditorStorageError("EDITOR_STORAGE_INVALID")
    expected=envelope(budget,value["declaration"])
    for key in ("schema_version","risk_budget_version_id","profile_id","mandate_version_id","revision","supersedes_version_id","policy_hash","name","status","created_at"):
        if value.get(key)!=expected[key]:raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if budget.name!=derived_name(value["declaration"]):raise EditorStorageError("EDITOR_STORAGE_INVALID")
    mandate=session.get(MandateVersion,budget.mandate_version_id)
    if not mandate or diagnostics(value["declaration"],mandate.horizon_years,True)["consistency_status"]!="NO_KNOWN_CONTRADICTION":
        raise EditorStorageError("EDITOR_STORAGE_INVALID")
    actual=session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==budget.id)).all()
    wanted=project(budget.id,value["declaration"])
    if len(actual)!=19 or {x.metric for x in actual}!={x.metric for x in wanted}:raise EditorStorageError("EDITOR_STORAGE_INVALID")
    by_metric={x.metric:x for x in actual}
    for row in wanted:
        stored=by_metric[row.metric]
        for col in ("risk_budget_version_id","constraint_class","metric","unit","horizon","operator","limit_value","warning_value","epsilon","alpha","uncertainty_version","stress_version","binding_status","calibration_status","missing_reason"):
            if getattr(stored,col)!=getattr(row,col):raise EditorStorageError("EDITOR_STORAGE_INVALID")
    return value
def _ddl(sql):
    return re.sub(r"\s+","",(sql or "").replace('"','').replace('`','')).upper()

def _require_editor_schema(session):
    """Verify the exact V1 SQLite contracts, not merely their object names."""
    tables={x[0]:x[1] for x in session.execute(text("SELECT name, sql FROM sqlite_master WHERE type='table'"))}
    for table in ("research_risk_editor_markers","research_risk_editor_documents"):
        if table not in tables: raise EditorStorageError("EDITOR_STORAGE_INVALID")
    expected_columns={
        "research_risk_editor_markers":[("risk_budget_version_id","VARCHAR",1,1),("schema_version","VARCHAR",1,0),("document_sha256","VARCHAR",1,0),("created_at","DATETIME",1,0)],
        "research_risk_editor_documents":[("risk_budget_version_id","VARCHAR",1,1),("schema_version","VARCHAR",1,0),("canonical_document","TEXT",1,0),("created_at","DATETIME",1,0)],
    }
    for table,expected in expected_columns.items():
        actual=[(row["name"],row["type"].upper(),row["notnull"],row["pk"]) for row in session.execute(text(f"PRAGMA table_info('{table}')")).mappings()]
        if actual!=expected: raise EditorStorageError("EDITOR_STORAGE_INVALID")
    marker=_ddl(tables["research_risk_editor_markers"]); document=_ddl(tables["research_risk_editor_documents"])
    marker_terms=("RISK_BUDGET_VERSION_IDVARCHARNOTNULL","PRIMARYKEY(RISK_BUDGET_VERSION_ID)",
        "CONSTRAINTCK_EDITOR_MARKER_SCHEMA CHECK(SCHEMA_VERSION='RESEARCH_RISK_EDITOR_V1')",
        "CONSTRAINTCK_EDITOR_MARKER_DIGEST CHECK(LENGTH(DOCUMENT_SHA256)=64ANDDOCUMENT_SHA256GLOB'[0-9A-F]*'ANDDOCUMENT_SHA256NOTGLOB'*[^0-9A-F]*')",
        "CONSTRAINTCK_EDITOR_MARKER_CREATED_AT CHECK(LENGTH(CREATED_AT)>0)")
    document_terms=("RISK_BUDGET_VERSION_IDVARCHARNOTNULL","PRIMARYKEY(RISK_BUDGET_VERSION_ID)",
        "CONSTRAINTCK_EDITOR_DOCUMENT_SCHEMA CHECK(SCHEMA_VERSION='RESEARCH_RISK_EDITOR_V1')",
        "CONSTRAINTCK_EDITOR_DOCUMENT_JSON CHECK(JSON_VALID(CANONICAL_DOCUMENT)=1)",
        "CONSTRAINTCK_EDITOR_DOCUMENT_CREATED_AT CHECK(LENGTH(CREATED_AT)>0)")
    if not all(_ddl(term) in marker for term in marker_terms) or not all(_ddl(term) in document for term in document_terms):
        raise EditorStorageError("EDITOR_STORAGE_INVALID")
    marker_fk=session.execute(text("PRAGMA foreign_key_list('research_risk_editor_markers')")).mappings().all()
    docs_fk=session.execute(text("PRAGMA foreign_key_list('research_risk_editor_documents')")).mappings().all()
    if len(marker_fk)!=1 or not any(x["table"]=="risk_budget_versions" and x["from"]=="risk_budget_version_id" and x["to"]=="id" and x["on_delete"]=="RESTRICT" for x in marker_fk):
        raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if len(docs_fk)!=1 or not any(x["table"]=="research_risk_editor_markers" and x["from"]=="risk_budget_version_id" and x["to"]=="risk_budget_version_id" and x["on_delete"]=="RESTRICT" for x in docs_fk):
        raise EditorStorageError("EDITOR_STORAGE_INVALID")
    triggers={x[0]:x[1] for x in session.execute(text("SELECT name, sql FROM sqlite_master WHERE type='trigger'"))}
    expected={
        "trg_risk_constraints_no_update":("risk_constraints","UPDATE","immutable risk_constraints"),
        "trg_risk_constraints_no_delete":("risk_constraints","DELETE","immutable risk_constraints"),
        "trg_research_risk_editor_markers_update":("research_risk_editor_markers","UPDATE","immutable editor record"),
        "trg_research_risk_editor_markers_delete":("research_risk_editor_markers","DELETE","immutable editor record"),
        "trg_research_risk_editor_documents_update":("research_risk_editor_documents","UPDATE","immutable editor record"),
        "trg_research_risk_editor_documents_delete":("research_risk_editor_documents","DELETE","immutable editor record"),
    }
    for name,(table,action,message) in expected.items():
        required=f"CREATE TRIGGER {name} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT, '{message}'); END"
        if _ddl(triggers.get(name)) != _ddl(required): raise EditorStorageError("EDITOR_STORAGE_INVALID")

def _verify_chain(rows, profile_id, policy_hash, version_name):
    ordered=sorted(rows,key=lambda x:x.revision)
    if not ordered or [x.revision for x in ordered]!=list(range(1,len(ordered)+1)):
        raise EditorStorageError("EDITOR_STORAGE_INVALID")
    for index,row in enumerate(ordered):
        if row.profile_id!=profile_id or row.policy_hash!=policy_hash or row.status!="PROVISIONAL": raise EditorStorageError("EDITOR_STORAGE_INVALID")
        predecessor=None if index==0 else ordered[index-1].id
        if row.supersedes_version_id!=predecessor: raise EditorStorageError("EDITOR_STORAGE_INVALID")
    return ordered

def verify_risk_editor(session):
    rev=session.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
    if rev!="0003_research_risk_editor":raise EditorStorageError("EDITOR_STORAGE_INVALID")
    _require_editor_schema(session)
    budgets=session.scalars(select(RiskBudgetVersion)).all()
    mandates=session.scalars(select(MandateVersion)).all()
    profiles=session.scalars(select(ResearchProfile)).all()
    if any(not profile.id for profile in profiles): raise EditorStorageError("EDITOR_STORAGE_INVALID")
    for profile in session.scalars(select(ResearchProfile)).all():
        head=session.get(ProfileHead,profile.id)
        if not head:raise EditorStorageError("EDITOR_STORAGE_INVALID")
        mandates_for_profile=_verify_chain([x for x in mandates if x.profile_id==profile.id],profile.id,POLICY_HASH,"mandate")
        chain=_verify_chain([x for x in budgets if x.profile_id==profile.id],profile.id,POLICY_HASH,"risk")
        if head.risk_budget_version_id!=chain[-1].id or head.mandate_version_id!=mandates_for_profile[-1].id:raise EditorStorageError("EDITOR_STORAGE_INVALID")
        # A mandate successor may intentionally make the current risk binding
        # stale until a separately CAS-protected risk successor is saved.  It
        # is a preflight blocker, not storage corruption.
        if any(x.profile_id!=profile.id for x in chain+mandates_for_profile): raise EditorStorageError("EDITOR_STORAGE_INVALID")
    if {x.profile_id for x in budgets}|{x.profile_id for x in mandates}!={x.id for x in profiles}: raise EditorStorageError("EDITOR_STORAGE_INVALID")
    for b in budgets:
        doc=get_document(session,b)
        rows=session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==b.id)).all()
        if len(rows)!=19 or len({x.metric for x in rows})!=19:raise EditorStorageError("EDITOR_STORAGE_INVALID")
        if {x.metric for x in rows}!={x[0] for x in METRICS}:raise EditorStorageError("EDITOR_STORAGE_INVALID")
        mandate=session.get(MandateVersion,b.mandate_version_id)
        if not mandate or mandate.profile_id!=b.profile_id: raise EditorStorageError("EDITOR_STORAGE_INVALID")
        if not doc:
            for row in rows:
                if row.metric not in CAT: raise EditorStorageError("EDITOR_STORAGE_INVALID")
                spec=CAT[row.metric]
                allowed_operators={spec[2]}
                if row.metric in {"MIN_LIQUIDITY","MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE"}: allowed_operators.add("<=")
                if row.constraint_class!=spec[1] or row.operator not in allowed_operators or not isinstance(row.unit,str) or not row.unit.strip():raise EditorStorageError("EDITOR_STORAGE_INVALID")
                for value in (row.limit_value,row.warning_value,row.epsilon,row.alpha):
                    if value is not None and (not isinstance(value,(int,float)) or not math.isfinite(value)):raise EditorStorageError("EDITOR_STORAGE_INVALID")
    return {"status":"VALID","revision":rev,"production_readiness":"NOT PRODUCTION READY"}
