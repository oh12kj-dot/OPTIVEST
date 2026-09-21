from __future__ import annotations
from datetime import datetime, timedelta, timezone
from copy import deepcopy
from sqlalchemy import select, update, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import *
from . import risk_editor

POLICY_HASH="ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67"
NOT_READY="NOT PRODUCTION READY"
BLOCKERS=["RISK_BUDGET_NOT_APPROVED","PROVIDER_TIMESTAMP_NOT_VERIFIED","TRADABILITY_NOT_VERIFIED","PIT_LINEAGE_NOT_VERIFIED"]
class ConflictError(ValueError): pass

def utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None: raise ValueError("timestamp requires explicit timezone")
    return value.astimezone(timezone.utc)

def iso_z(value: datetime) -> str:
    if value.tzinfo is None: value=value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def _constraints(budget_id: str):
    # Exact BALANCED_RESEARCH_V1 references; unknown calibrated values are null with a reason.
    known=[("MAX_SINGLE_NAME_EQUITY","STRUCTURAL_HARD",10,"PERCENT","7 years","<="),("PASSIVE_MARKET_IMPLEMENTATION","STRUCTURAL_HARD",100,"PERCENT","7 years","<="),("MAX_SECTOR_INDUSTRY","STRUCTURAL_HARD",30,"PERCENT","7 years","<="),("MAX_FACTOR_CLUSTER","HYBRID",35,"PERCENT","7 years","<="),("MAX_MODELED_DRAWDOWN","MODEL_ESTIMATED",25,"PERCENT","7 years","<="),("MAX_STRESS_DRAWDOWN","STRESS",35,"PERCENT","7 years","<="),("MAX_RECOVERY_DURATION","MODEL_ESTIMATED",36,"MONTHS","7 years","<="),("MAX_DAYS_TO_LIQUIDATE","HYBRID",5,"TRADING_DAYS","normal","<="),("MAX_PARTICIPATION_RATE","STRUCTURAL_HARD",10,"PERCENT_ADV","normal","<="),("CASH_ALLOCATION","STRUCTURAL_HARD",100,"PERCENT","7 years","<="),("LEVERAGE","STRUCTURAL_HARD",0,"PERCENT","always","<="),("RISK_FREE_PROXY_ALLOCATION","STRUCTURAL_HARD",100,"PERCENT","7 years","<=" )]
    unknown=[("PORTFOLIO_CVAR","MODEL_ESTIMATED"),("SEVERE_LOSS_PROBABILITY","MODEL_ESTIMATED"),("PERMANENT_LOSS_EXPOSURE","MODEL_ESTIMATED"),("PORTFOLIO_JOINT_MATERIAL_RISK","MODEL_ESTIMATED"),("MIN_LIQUIDITY","HYBRID"),("MAX_TURNOVER_IMPLEMENTATION_COST","HYBRID"),("MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE","STRUCTURAL_HARD")]
    rows=[RiskConstraint(risk_budget_version_id=budget_id,metric=m,constraint_class=c,limit_value=v,unit=u,horizon=h,operator=o,warning_value=None,epsilon=None,alpha=None,uncertainty_version=None,stress_version=None,binding_status="DIAGNOSTIC",calibration_status="NOT_VERIFIED",missing_reason="NOT_VERIFIED") for m,c,v,u,h,o in known]
    rows += [RiskConstraint(risk_budget_version_id=budget_id,metric=m,constraint_class=c,limit_value=None,unit="UNSPECIFIED",horizon="UNSPECIFIED",operator="<=",warning_value=None,epsilon=None,alpha=None,uncertainty_version=None,stress_version=None,binding_status="DIAGNOSTIC",calibration_status="NOT_VERIFIED",missing_reason="CALIBRATION_OR_DEFINITION_NOT_VERIFIED") for m,c in unknown]
    return rows

def seed(session: Session) -> tuple[MandateVersion,RiskBudgetVersion]:
    profile=session.scalar(select(ResearchProfile).where(ResearchProfile.name=="GENERIC_DISCOVERY_RESEARCH"))
    if profile:
        head=session.get(ProfileHead,profile.id)
        if head and head.mandate_version_id and head.risk_budget_version_id: return session.get(MandateVersion,head.mandate_version_id),session.get(RiskBudgetVersion,head.risk_budget_version_id)
        raise ValueError("seeded profile is incomplete; repair is not permitted")
    profile=ResearchProfile(name="GENERIC_DISCOVERY_RESEARCH"); session.add(profile); session.flush()
    mandate=MandateVersion(profile_id=profile.id,revision=1,supersedes_version_id=None,mode="GENERIC_DISCOVERY_RESEARCH",horizon_years=7,base_currency="USD",nominal_real="NOMINAL",tax_treatment="PRE_TAX",external_flows="SELF_FINANCING_NONE",portfolio_scope="US_LISTED_EQUITY_SLEEVE",universe_version="US_PRIMARY_NYSE_NASDAQ_COMMON_EQUITIES",benchmark_definition="CRSP US Total Market Index, USD total-return definition",passive_candidate="VTI (candidate; NOT VERIFIED)",cash_semantics="USD cash ledger state; not risk-free",risk_free_proxy=None,reference_capital=1_000_000,status="PROVISIONAL",rationale="Provisional Generic Research baseline; no approval",policy_hash=POLICY_HASH)
    session.add(mandate);session.flush()
    budget=RiskBudgetVersion(profile_id=profile.id,mandate_version_id=mandate.id,revision=1,supersedes_version_id=None,name="BALANCED_RESEARCH_V1",status="PROVISIONAL",rationale="Policy section 8 research defaults; calibration remains NOT VERIFIED",policy_hash=POLICY_HASH)
    session.add(budget);session.flush();session.add(ProfileHead(profile_id=profile.id,mandate_version_id=mandate.id,risk_budget_version_id=budget.id));session.add_all(_constraints(budget.id));session.commit();return mandate,budget

def profile_head(session: Session) -> ProfileHead:
    profile=session.scalar(select(ResearchProfile).where(ResearchProfile.name=="GENERIC_DISCOVERY_RESEARCH"))
    if not profile: raise LookupError("research seed absent; run seed-research")
    head=session.get(ProfileHead,profile.id)
    if not head: raise LookupError("research profile head absent")
    return head

def status(session: Session) -> dict:
    profile=session.scalar(select(ResearchProfile).where(ResearchProfile.name=="GENERIC_DISCOVERY_RESEARCH")); head=session.get(ProfileHead,profile.id) if profile else None
    mandate=session.get(MandateVersion,head.mandate_version_id) if head and head.mandate_version_id else None; budget=session.get(RiskBudgetVersion,head.risk_budget_version_id) if head and head.risk_budget_version_id else None
    result={"policy_hash":POLICY_HASH,"mode":"GENERIC_DISCOVERY_RESEARCH","mandate_status":mandate.status if mandate else "NOT VERIFIED","risk_budget_status":"PROVISIONAL / RISK BUDGET NOT APPROVED" if budget else "NOT VERIFIED","validation_status":"NOT VERIFIED","production_readiness":NOT_READY,"blocker_codes":BLOCKERS,"mandate_version_id":mandate.id if mandate else None,"risk_budget_version_id":budget.id if budget else None}
    # Phase-1/2 callers may legitimately run before the editor migration.  At
    # V1, expose the same pure diagnostics without allowing them to remove the
    # existing PIT/tradability blockers.
    if budget and mandate:
        try:
            # A V1 database is a closed immutable history.  Do not let a
            # corrupted predecessor or projection surface as a healthy head.
            if session.execute(text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='research_risk_editor_markers' ")).scalar(): risk_editor.verify_risk_editor(session)
            doc=risk_editor.get_document(session,budget)
            result["risk_editor_status"]="V1" if doc else "LEGACY_NOT_VERIFIED"
            if doc:
                result["risk_budget_name"]=budget.name
                result["source_preset"]=doc["declaration"]["source_preset"]
                diag=risk_editor.diagnostics(doc["declaration"],mandate.horizon_years,True)
            else:
                result["risk_budget_name"]=budget.name
                result["source_preset"]=None
                rows=session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==budget.id)).all()
                diag=risk_editor.legacy_diagnostics(rows,budget.mandate_version_id==head.mandate_version_id)
            result["risk_editor_diagnostics"]=diag
            result["blocker_codes"]=sorted(set(BLOCKERS)|set(diag["blockers"]))
        except risk_editor.EditorStorageError:
            raise
        except Exception:
            # Pre-editor migrations legitimately have no document tables.
            pass
    return result

def _cas_head(session:Session, profile_id:str, field:str, expected:str, replacement:str):
    result=session.execute(update(ProfileHead).where(ProfileHead.profile_id==profile_id,getattr(ProfileHead,field)==expected).values(**{field:replacement}))
    if result.rowcount != 1: raise ConflictError("stale current version")

def mandate_successor(session:Session, expected:str, changes:dict) -> MandateVersion:
    head=profile_head(session); old=session.get(MandateVersion,expected)
    if not old or old.profile_id!=head.profile_id or head.mandate_version_id!=expected: raise ConflictError("stale or cross-profile mandate")
    values={c.name:getattr(old,c.name) for c in MandateVersion.__table__.columns if c.name not in {"id","revision","supersedes_version_id","created_at","effective_at","review_at","rationale"}}
    values.update(changes); values.update(profile_id=old.profile_id,revision=old.revision+1,supersedes_version_id=old.id,status="PROVISIONAL",mode="GENERIC_DISCOVERY_RESEARCH",policy_hash=POLICY_HASH)
    new=MandateVersion(**values); session.add(new);session.flush();_cas_head(session,old.profile_id,"mandate_version_id",old.id,new.id);session.commit();return new

def risk_successor(session:Session, expected:str, mandate_id:str, rationale:str) -> RiskBudgetVersion:
    head=profile_head(session); old=session.get(RiskBudgetVersion,expected); mandate=session.get(MandateVersion,mandate_id)
    if not old or not mandate or old.profile_id!=head.profile_id or mandate.profile_id!=head.profile_id or head.risk_budget_version_id!=expected or head.mandate_version_id!=mandate_id: raise ConflictError("stale, cross-profile, or non-current risk pair")
    new=RiskBudgetVersion(profile_id=old.profile_id,mandate_version_id=mandate_id,revision=old.revision+1,supersedes_version_id=old.id,name="BALANCED_RESEARCH_V1",status="PROVISIONAL",rationale=rationale,policy_hash=POLICY_HASH);session.add(new);session.flush();session.add_all(_constraints(new.id));_cas_head(session,old.profile_id,"risk_budget_version_id",old.id,new.id);session.commit();return new

def editor_version(session:Session,budget_id:str|None=None)->dict:
    h=profile_head(session); budget=session.get(RiskBudgetVersion,budget_id or h.risk_budget_version_id)
    if not budget or budget.profile_id!=h.profile_id: raise ConflictError("stale or cross-profile budget")
    risk_editor.verify_risk_editor(session)
    doc=risk_editor.get_document(session,budget)
    mandate=session.get(MandateVersion,budget.mandate_version_id)
    if not mandate: raise risk_editor.EditorStorageError("EDITOR_STORAGE_INVALID")
    if doc:
        d=doc["declaration"]; diag=risk_editor.diagnostics(d,mandate.horizon_years,budget.mandate_version_id==h.mandate_version_id)
        constraints=risk_editor.project(budget.id,d)
        # serializer exposes the persisted compatibility rows, never a calculated model result.
        stored=session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==budget.id)).all()
        return {"id":budget.id,"profile_id":budget.profile_id,"mandate_version_id":budget.mandate_version_id,"revision":budget.revision,"supersedes_version_id":budget.supersedes_version_id,"policy_hash":budget.policy_hash,"name":budget.name,"status":budget.status,"created_at":iso_z(budget.created_at),"editor_document_status":"V1","declaration":d,"constraints":[{c.name:getattr(x,c.name) for c in RiskConstraint.__table__.columns} for x in stored],"diagnostics":diag}
    rows=session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==budget.id).order_by(RiskConstraint.metric)).all()
    diag=risk_editor.legacy_diagnostics(rows,budget.mandate_version_id==h.mandate_version_id)
    return {"id":budget.id,"profile_id":budget.profile_id,"mandate_version_id":budget.mandate_version_id,"revision":budget.revision,"supersedes_version_id":budget.supersedes_version_id,"policy_hash":budget.policy_hash,"name":budget.name,"status":budget.status,"created_at":iso_z(budget.created_at),"editor_document_status":"LEGACY_NOT_VERIFIED","declaration":None,"constraints":[{c.name:getattr(x,c.name) for c in RiskConstraint.__table__.columns} for x in rows],"diagnostics":diag}

def _clone_legacy_constraints(old_id,new_id,session):
    rows=session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==old_id)).all()
    for row in rows:
        values={c.name:getattr(row,c.name) for c in RiskConstraint.__table__.columns if c.name not in {"id","risk_budget_version_id"}}
        session.add(RiskConstraint(id=uid(),risk_budget_version_id=new_id,**values))

def editor_save(session:Session, request:dict)->dict:
    request=risk_editor.normalize_request(request)
    # The explicit write lock is part of the frozen two-head transaction contract.
    session.execute(text("BEGIN IMMEDIATE"))
    try:
        profile=session.scalar(select(ResearchProfile).where(ResearchProfile.name=="GENERIC_DISCOVERY_RESEARCH")); head=session.get(ProfileHead,profile.id) if profile else None
        if not profile or not head: raise risk_editor.EditorStorageError("EDITOR_STORAGE_INVALID")
        if request["expected_current_version_id"]!=head.risk_budget_version_id or request["mandate_version_id"]!=head.mandate_version_id: raise ConflictError("HEAD_CONFLICT")
        old=session.get(RiskBudgetVersion,head.risk_budget_version_id); mandate=session.get(MandateVersion,head.mandate_version_id)
        if not old or not mandate or old.profile_id!=profile.id or mandate.profile_id!=profile.id: raise risk_editor.EditorStorageError("EDITOR_STORAGE_INVALID")
        old_doc=risk_editor.get_document(session,old)
        if request["request_kind"]=="FULL_DECLARATION": declaration=request["declaration"]
        elif old_doc: declaration=deepcopy(old_doc["declaration"])
        else: declaration=None
        if declaration is not None:
            diag=risk_editor.diagnostics(declaration,mandate.horizon_years,True)
            if diag["consistency_status"]!="NO_KNOWN_CONTRADICTION":
                error=risk_editor.EditorError("RISK_BUDGET_INCONSISTENT")
                error.diagnostics=diag
                raise error
            name=risk_editor.derived_name(declaration)
        else: name=old.name
        new=RiskBudgetVersion(profile_id=profile.id,mandate_version_id=mandate.id,revision=old.revision+1,supersedes_version_id=old.id,name=name,status="PROVISIONAL",rationale=request["rationale"],policy_hash=POLICY_HASH)
        session.add(new); session.flush()
        if declaration is None: _clone_legacy_constraints(old.id,new.id,session)
        else: session.add_all(risk_editor.project(new.id,declaration))
        session.flush()
        if declaration is not None:
            doc=risk_editor.envelope(new,declaration); raw=risk_editor.canonical(doc); digest=__import__("hashlib").sha256(raw.encode()).hexdigest()
            session.add(ResearchRiskEditorMarker(risk_budget_version_id=new.id,schema_version=risk_editor.SCHEMA,document_sha256=digest))
            session.flush()
            session.add(ResearchRiskEditorDocument(risk_budget_version_id=new.id,schema_version=risk_editor.SCHEMA,canonical_document=raw))
        session.flush()
        result=session.execute(update(ProfileHead).where(ProfileHead.profile_id==profile.id,ProfileHead.risk_budget_version_id==old.id,ProfileHead.mandate_version_id==mandate.id).values(risk_budget_version_id=new.id))
        if result.rowcount!=1: raise ConflictError("HEAD_CONFLICT")
        response=editor_version(session,new.id)
        # Force response serialization before commit, so a serialization failure rolls back too.
        import json; json.dumps(response,default=str,allow_nan=False)
        session.commit(); return response
    except Exception:
        session.rollback(); raise

def editor_preview(session:Session, request:dict)->dict:
    request=risk_editor.normalize_request(request)
    # SQLite does not emit a BEGIN for an ordinary deferred read until needed;
    # issue it explicitly so every head/document/diagnostic read shares one
    # observable snapshot.
    session.execute(text("BEGIN"))
    try:
        risk_editor.verify_risk_editor(session); head=profile_head(session)
        if request["expected_current_version_id"]!=head.risk_budget_version_id or request["mandate_version_id"]!=head.mandate_version_id: raise ConflictError("HEAD_CONFLICT")
        mandate=session.get(MandateVersion,head.mandate_version_id); old=session.get(RiskBudgetVersion,head.risk_budget_version_id); old_doc=risk_editor.get_document(session,old)
        d=request["declaration"] if request["request_kind"]=="FULL_DECLARATION" else (old_doc["declaration"] if old_doc else None)
        observed={"observed_current_version_id":head.risk_budget_version_id,"observed_mandate_version_id":head.mandate_version_id}
        if d is None:
            result={"expected_current_version_id":head.risk_budget_version_id,"mandate_version_id":head.mandate_version_id,**observed,"diagnostics":risk_editor.legacy_diagnostics(session.scalars(select(RiskConstraint).where(RiskConstraint.risk_budget_version_id==old.id)).all(),True),"changes":[],"candidate_name":old.name}
        else:
            baseline=old_doc["declaration"] if old_doc else None
            changes=risk_editor.declaration_changes(baseline,d) if baseline else [{"path":"/declaration","before":None,"after":None,"comparison":"LEGACY_FIELD_UNAVAILABLE"}]
            result={"expected_current_version_id":head.risk_budget_version_id,"mandate_version_id":head.mandate_version_id,**observed,"diagnostics":risk_editor.diagnostics(d,mandate.horizon_years,True),"changes":changes,"candidate_name":risk_editor.derived_name(d)}
        return result
    finally:
        session.rollback()

def preflight(session:Session, mandate_id:str,risk_id:str,decision:datetime,tradable:datetime,evidence_ids:list[str])->dict:
    decision,tradable=utc(decision),utc(tradable)
    if tradable<decision: raise ValueError("tradable_at must be at or after decision_timestamp")
    risk_editor.verify_risk_editor(session)
    head=profile_head(session); mandate=session.get(MandateVersion,mandate_id);risk=session.get(RiskBudgetVersion,risk_id)
    if not mandate or not risk or mandate.id!=head.mandate_version_id or risk.id!=head.risk_budget_version_id or mandate.profile_id!=risk.profile_id or risk.mandate_version_id!=mandate.id or mandate.policy_hash!=POLICY_HASH or risk.policy_hash!=POLICY_HASH: raise ValueError("preflight requires current same-profile coherent mandate and risk heads")
    # A checked V1 declaration is an input gate even though its feasibility is
    # deliberately unavailable.  Corruption therefore blocks before any
    # DecisionSnapshot insert.
    document=risk_editor.get_document(session,risk)
    if len(evidence_ids)!=len(set(evidence_ids)): raise ValueError("duplicate evidence id")
    diagnostics=[]; blockers=list(BLOCKERS)
    if document: blockers.extend(risk_editor.diagnostics(document["declaration"],mandate.horizon_years,True)["blockers"])
    for evidence_id in evidence_ids:
        e=session.get(EvidenceRecord,evidence_id)
        if not e: raise LookupError("evidence not found")
        reasons=[]
        if e.observation_mode=="HISTORICAL_IMPORT": reasons.append("HISTORICAL_IMPORT_INELIGIBLE")
        if e.value_presence!="PRESENT" or e.use_status!="FRESH": reasons.append("EVIDENCE_NOT_PRESENT_FRESH")
        if not e.available_at or not e.retrieved_at: reasons.append("TIMESTAMPS_NOT_CLAIMED")
        elif e.processing_latency_seconds is not None:
            try:
                if decision < utc(e.available_at)+timedelta(seconds=e.processing_latency_seconds): reasons.append("PIT_LATENCY_NOT_MET")
            except OverflowError: reasons.append("LATENCY_OVERFLOW")
        diagnostics.append({"evidence_id":e.id,"blockers":reasons})
        blockers.extend(reasons)
    blockers=list(dict.fromkeys(blockers)); snapshot=DecisionSnapshot(mandate_version_id=mandate.id,risk_budget_version_id=risk.id,policy_hash=POLICY_HASH,decision_timestamp=decision,tradable_at=tradable,evidence_ids=evidence_ids,blocker_codes=blockers,diagnostics=diagnostics);session.add(snapshot);session.commit()
    return {"snapshot_id":snapshot.id,"eligible_for_research_decision":False,"production_readiness":NOT_READY,"blocker_codes":blockers,"evidence_diagnostics":diagnostics}
