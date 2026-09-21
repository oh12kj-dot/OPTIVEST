from datetime import date, datetime, timezone
from html import escape
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import HTMLResponse as _HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .db import make_session
from .models import *
from . import service

def app_for(url:str|None=None)->FastAPI:
    engine,factory=make_session(url)
    # Schema ownership is Alembic-only. An unmigrated database is deliberately unavailable.
    try:
        with engine.connect() as c:
            revision=c.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            expected={"license_evidence_versions","license_use_permissions","provider_dataset_versions","capture_scopes","ingestion_runs","ingestion_attempts","raw_objects","source_snapshots","source_snapshot_parts","source_rows","dataset_heads","run_snapshot_results","source_security_candidates","staged_membership_events","identity_review_revisions","identity_review_heads"}
            names={x[0] for x in c.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
            if revision not in {"0002_phase2","0003_research_risk_editor"} or not expected.issubset(names):raise RuntimeError("Phase 2 schema is incomplete")
            if revision=="0003_research_risk_editor":
                if not {"research_risk_editor_markers","research_risk_editor_documents"}.issubset(names): raise RuntimeError("Research editor schema is incomplete")
        with factory() as startup_session:
            from .phase2 import verify_phase2
            report=verify_phase2(startup_session)
            # A Phase-1-only database may have the exact Phase-2 schema but no
            # provider declaration yet.  Once any Phase-2 dataset is present,
            # startup requires the complete frozen two-dataset permission matrix.
            if report["counts"]["datasets"] and not report["seed_state"]:raise RuntimeError("Phase 2 provider permission matrix is incomplete")
            if revision=="0003_research_risk_editor":
                from .risk_editor import verify_risk_editor
                verify_risk_editor(startup_session)
    except Exception as e:
        engine.dispose()
        raise RuntimeError("database is not migrated; run optivest.cli db upgrade") from e
    app=FastAPI(title="OptiVest Phase 1 Research Control Plane",version="0.1.0")
    app.state.engine=engine
    app.mount("/static", StaticFiles(directory=str(Path(__file__).with_name("static"))), name="static")
    # The wealth lab is a separate stateless synthetic surface.  Registration
    # does not give it a database session or alter provider/preflight routes.
    from .wealth_lab_api import register_wealth_lab
    register_wealth_lab(app)
    def db():
        s=factory()
        try: yield s
        finally:s.close()
    def commit(s:Session):
        try:s.commit()
        except IntegrityError as e:s.rollback();raise HTTPException(409,"integrity conflict") from e
    class Strict(BaseModel):model_config=ConfigDict(extra="forbid")
    class MandateIn(Strict):
        expected_current_version_id:str; horizon_years:StrictInt=Field(gt=0); rationale:str=Field(min_length=1)
    class RiskIn(Strict): expected_current_version_id:str; mandate_version_id:str; rationale:str=Field(min_length=1); status:str="PROVISIONAL"
    class ProviderIn(Strict):name:str=Field(min_length=1);authority_tier:str;version:str|None=None;declarations:dict=Field(default_factory=dict);source_reference:str|None=None;validation_status:str="NOT_VERIFIED"
    class IssuerIn(Strict):legal_name:str;incorporation_country:str|None=None;lifecycle_status:str="ACTIVE"
    class SecurityIn(Strict):issuer_id:str;instrument_type:str;primary_venue:str;currency:str;share_class:str|None=None;lifecycle_status:str="ACTIVE"
    class IdentifierIn(Strict):security_id:str;scheme:str;value:str;venue:str|None=None;valid_from:date;valid_to:date|None=None;source_evidence_id:str|None=None
    class CorporateActionIn(Strict):security_id:str;action_type:str;effective_date:date;tradable_at:datetime|None=None;predecessor_security_id:str|None=None;successor_security_id:str|None=None;source_evidence_id:str|None=None
    class MembershipIn(Strict):universe_version:str;security_id:str;included_from:date;included_to:date|None=None;decision_available_at:datetime;reason:str;source_evidence_id:str|None=None
    class EvidenceIn(Strict):
        provider_id:str;source_locator:str;subject_type:str;subject_id:str;metric:str;value:object|None=None;unit:str|None=None;currency:str|None=None;period:str|None=None;as_of_date:date|None=None;available_at:datetime|None=None;retrieved_at:datetime|None=None;observation_mode:str;processing_latency_seconds:StrictInt|None=None;quality_confidence:str|None=None;value_presence:str;use_status:str;reason:str|None=None;conflict_group_id:str|None=None;lineage_hash:str|None=None;payload_hash:str|None=None;supersedes_id:str|None=None
        @field_validator("processing_latency_seconds")
        @classmethod
        def latency(cls,v):
            if v is not None and (type(v) is not int or v<0):raise ValueError("latency must be a JSON integer >= 0")
            return v
    class PreflightIn(Strict):mandate_version_id:str;risk_budget_version_id:str;decision_timestamp:datetime;tradable_at:datetime;evidence_ids:list[str]=Field(default_factory=list)
    def page(items,offset,limit):return {"items":items,"offset":offset,"limit":limit}
    def phase2_display(s):
        from .phase2 import Phase2Error, require_permissions
        try:
            for dataset in s.scalars(select(ProviderDatasetVersion)).all(): require_permissions(s,dataset.id,"INTERNAL_DISPLAY")
        except Phase2Error as e: raise HTTPException(403,str(e))
    def require_utc(value:datetime|None):
        if value is not None: return service.utc(value)
        return None
    @app.get("/api/v1/status")
    def status(s:Session=Depends(db)):
        try:return service.status(s)
        except Exception as e:return editor_error(e)
    @app.get("/api/v1/mandates/current")
    def mandate_current(s:Session=Depends(db)):
        h=service.profile_head(s);m=s.get(MandateVersion,h.mandate_version_id);return {c.name:getattr(m,c.name) for c in MandateVersion.__table__.columns}
    @app.post("/api/v1/mandates/versions",status_code=201)
    def mandate(body:MandateIn,s:Session=Depends(db)):
        try:m=service.mandate_successor(s,body.expected_current_version_id,{"horizon_years":body.horizon_years,"rationale":body.rationale})
        except service.ConflictError as e:raise HTTPException(409,str(e))
        return {"id":m.id,"status":m.status,"supersedes_version_id":m.supersedes_version_id}
    def editor_error(e):
        from .risk_editor import EditorError, EditorConflict, EditorStorageError
        if isinstance(e,EditorStorageError): return JSONResponse({"error":{"code":"EDITOR_STORAGE_INVALID","fields":[]}},status_code=503)
        if isinstance(e,EditorError) and e.code=="JSON_SIZE": return JSONResponse({"error":{"code":"JSON_SIZE","fields":[]}},status_code=413)
        status=409 if isinstance(e,(EditorConflict,service.ConflictError)) else 422 if isinstance(e,EditorError) else 500
        code="HEAD_CONFLICT" if isinstance(e,service.ConflictError) else (getattr(e,"code","INTERNAL_ERROR") if status!=500 else "INTERNAL_ERROR")
        fields=[] if status in {409,500} else [{"code":code,"path":getattr(e,"path","")}]
        if code=="RISK_BUDGET_INCONSISTENT" and hasattr(e,"diagnostics"):
            fields=[item for item in e.diagnostics["findings"] if item["severity"]=="ERROR"]
        body={"error":{"code":code,"fields":fields}}
        if hasattr(e,"diagnostics"): body["diagnostics"]=e.diagnostics
        return JSONResponse(body,status_code=status)
    def editor_content_type(request:Request)->bool:
        if request.headers.get("content-encoding"): return False
        parts=[part.strip().lower() for part in request.headers.get("content-type","").split(";")]
        return bool(parts) and parts[0]=="application/json" and (len(parts)==1 or parts[1:]==["charset=utf-8"])
    @app.get("/api/v1/risk-budgets/current")
    def risk_current(s:Session=Depends(db)):
        try:return service.editor_version(s)
        except Exception as e: return editor_error(e)
    @app.post("/api/v1/risk-budgets/versions",status_code=201)
    async def risk(request:Request,s:Session=Depends(db)):
        from .risk_editor import strict_decode
        if not editor_content_type(request): return JSONResponse({"error":{"code":"CONTENT_TYPE","fields":[]}},status_code=415)
        try:return service.editor_save(s,strict_decode(await request.body()))
        except Exception as e:
            from sqlalchemy.exc import OperationalError
            if isinstance(e,OperationalError) and "locked" in str(e).lower(): return JSONResponse({"error":{"code":"WRITE_CONFLICT","fields":[]}},status_code=409)
            return editor_error(e)
    @app.post("/api/v1/risk-budgets/preview")
    async def risk_preview(request:Request,s:Session=Depends(db)):
        from .risk_editor import strict_decode
        if not editor_content_type(request): return JSONResponse({"error":{"code":"CONTENT_TYPE","fields":[]}},status_code=415)
        try:return service.editor_preview(s,strict_decode(await request.body()))
        except Exception as e:return editor_error(e)
    @app.get("/api/v1/risk-budgets/catalog")
    def risk_catalog():
        from .risk_editor import template, METRICS
        return {"schema_version":"RESEARCH_RISK_EDITOR_V1","templates":{"balanced":template(),"growth":template("GROWTH_RESEARCH_V1")},"catalog":[{"metric":x[0],"constraint_class":x[1],"operator":x[2],"units":x[3]} for x in METRICS]}
    @app.get("/api/v1/risk-budgets/versions")
    def risk_versions(offset:int=0,limit:int=50,s:Session=Depends(db)):
        if offset<0 or not 1<=limit<=100: raise HTTPException(422,"invalid pagination")
        h=service.profile_head(s); rows=s.scalars(select(RiskBudgetVersion).where(RiskBudgetVersion.profile_id==h.profile_id).order_by(RiskBudgetVersion.revision).offset(offset).limit(limit)).all()
        try:return page([service.editor_version(s,x.id) for x in rows],offset,limit)
        except Exception as e: return editor_error(e)
    @app.get("/api/v1/risk-budgets/versions/{version_id}")
    def risk_version(version_id:str,s:Session=Depends(db)):
        try:return service.editor_version(s,version_id)
        except service.ConflictError: return JSONResponse({"error":{"code":"VERSION_NOT_FOUND","fields":[]}},status_code=404)
        except Exception as e: return editor_error(e)
    @app.get("/risk-budget",response_class=HTMLResponse)
    def risk_budget_editor():
        from .risk_editor import METRICS
        placeholders="".join(f'<label for="initial-{metric.lower()}">{escape(metric)} declaration <input id="initial-{metric.lower()}" name="{metric.lower()}" type="text" readonly placeholder="Load a research template or current V1 declaration"></label>' for metric,*_ in METRICS)
        return HTMLResponse(f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Research Risk Budget</title><link rel="stylesheet" href="/risk-budget/editor.css"></head><body><main><header><p class="eyebrow">OptiVest · Generic Research</p><h1>Research Risk Budget editor</h1><p><strong>RISK BUDGET NOT APPROVED</strong> · <strong>NOT PRODUCTION READY</strong></p><p>Percent uses 0–100; probability uses 0–1. Missing is never zero. MODEL-ESTIMATED RISK and stress declarations are not guarantees.</p><p id="state" role="status" aria-live="polite">Choose a frozen research template or reload a V1 draft.</p></header><nav aria-label="Draft actions"><button id="balanced" type="button">Balanced research template</button><button id="growth" type="button">Growth research template</button><button id="preview" type="button" disabled>Preview</button><button id="save" type="button" disabled>SAVE AS PROVISIONAL</button><button id="reload" type="button">Reload current / rebase</button><button id="activation" type="button" disabled>Production activation unavailable</button></nav><section class="summary"><h2>Current declaration</h2><dl id="current"></dl><label>Draft rationale <input id="rationale" maxlength="2048" value="Browser research draft"></label></section><section><h2>Structured limits</h2><p>Every declaration field remains explicit. Row 16 is a non-editable compatibility aggregate; edit its two named components below.</p><fieldset id="initial-structured-controls" aria-describedby="initial-structured-help"><legend>Initial structured declaration controls</legend><p id="initial-structured-help">Load a frozen research template or the current V1 declaration to hydrate these visible row controls with editable declaration values.</p>{placeholders}</fieldset><div id="rows"></div></section><section><h2>Portfolio joint material-risk declarations</h2><button id="add-joint" type="button" disabled>Add Joint group</button><div id="joint-groups"></div></section><section><h2>Diagnostics, differences and binding</h2><pre id="diagnostics" aria-live="polite"></pre></section><section><h2>Version history</h2><div id="history"></div></section><section class="unavailable"><h2>Personalized controls</h2><p>Risk Capacity: <strong>NOT ASSESSED</strong></p><p>Risk Tolerance: <strong>NOT ASSESSED</strong></p><p>PERSONALIZED MODE UNAVAILABLE. No activation request is generated.</p></section></main><script src="/risk-budget/editor.js" defer></script></body></html>""")
    @app.get("/risk-budget/editor.css")
    def risk_budget_css():
        return Response((Path(__file__).with_name("static")/"risk_editor.css").read_text(encoding="utf-8"),media_type="text/css")
    @app.get("/risk-budget/editor.js")
    def risk_budget_js():
        return Response((Path(__file__).with_name("static")/"risk_editor.js").read_text(encoding="utf-8"),media_type="application/javascript")
    @app.get("/api/v1/providers")
    def providers(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in Provider.__table__.columns} for x in s.scalars(select(Provider).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/providers",status_code=201)
    def provider(body:ProviderIn,s:Session=Depends(db)):
        if body.validation_status!="NOT_VERIFIED":raise HTTPException(422,"provider validation is unavailable in Phase 1")
        x=Provider(**body.model_dump());s.add(x);commit(s);return {"id":x.id,"validation_status":x.validation_status}
    @app.get("/api/v1/issuers")
    def issuers(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in Issuer.__table__.columns} for x in s.scalars(select(Issuer).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/issuers",status_code=201)
    def issuer(body:IssuerIn,s:Session=Depends(db)):x=Issuer(**body.model_dump());s.add(x);commit(s);return {"id":x.id}
    @app.get("/api/v1/securities")
    def securities(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in Security.__table__.columns} for x in s.scalars(select(Security).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/securities",status_code=201)
    def security(body:SecurityIn,s:Session=Depends(db)):
        if not s.get(Issuer,body.issuer_id):raise HTTPException(422,"unknown issuer")
        x=Security(**body.model_dump());s.add(x);commit(s);return {"id":x.id}
    @app.get("/api/v1/security-identifiers")
    def identifiers(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in SecurityIdentifier.__table__.columns} for x in s.scalars(select(SecurityIdentifier).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/security-identifiers",status_code=201)
    def identifier(body:IdentifierIn,s:Session=Depends(db)):
        if not s.get(Security,body.security_id):raise HTTPException(422,"unknown security")
        if body.source_evidence_id and not s.get(EvidenceRecord,body.source_evidence_id):raise HTTPException(422,"unknown source evidence")
        if body.valid_to and body.valid_to<body.valid_from:raise HTTPException(422,"invalid identifier interval")
        rows=s.scalars(select(SecurityIdentifier).where(SecurityIdentifier.scheme==body.scheme,SecurityIdentifier.value==body.value,SecurityIdentifier.venue==body.venue)).all()
        if any(body.valid_from <= (row.valid_to or date.max) and row.valid_from <= (body.valid_to or date.max) for row in rows):raise HTTPException(409,"overlapping identifier interval")
        x=SecurityIdentifier(**body.model_dump());s.add(x);commit(s);return {"id":x.id}
    @app.get("/api/v1/securities/resolve")
    def resolve(scheme:str,value:str,venue:str|None=None,as_of:date=Query(...),s:Session=Depends(db)):
        rows=[x for x in s.scalars(select(SecurityIdentifier).where(SecurityIdentifier.scheme==scheme,SecurityIdentifier.value==value,SecurityIdentifier.valid_from<=as_of)).all() if (x.valid_to is None or x.valid_to>=as_of) and (venue is None or x.venue==venue)];return {"resolution":"ZERO" if not rows else "ONE" if len(rows)==1 else "AMBIGUOUS","security_ids":[x.security_id for x in rows]}
    @app.get("/api/v1/corporate-actions")
    def actions(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in CorporateAction.__table__.columns} for x in s.scalars(select(CorporateAction).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/corporate-actions",status_code=201)
    def corporate(body:CorporateActionIn,s:Session=Depends(db)):
        data=body.model_dump();data["tradable_at"]=require_utc(data["tradable_at"])
        for k in ("security_id","predecessor_security_id","successor_security_id"):
            if data[k] and not s.get(Security,data[k]):raise HTTPException(422,"unknown security lineage")
        if data["source_evidence_id"] and not s.get(EvidenceRecord,data["source_evidence_id"]):raise HTTPException(422,"unknown source evidence")
        x=CorporateAction(**data);s.add(x);commit(s);return {"id":x.id}
    @app.get("/api/v1/universe-memberships")
    def memberships(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in UniverseMembership.__table__.columns} for x in s.scalars(select(UniverseMembership).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/universe-memberships",status_code=201)
    def membership(body:MembershipIn,s:Session=Depends(db)):
        data=body.model_dump();data["decision_available_at"]=require_utc(data["decision_available_at"])
        if data["included_to"] and data["included_to"]<data["included_from"]:raise HTTPException(422,"invalid membership interval")
        if not s.get(Security,data["security_id"]):raise HTTPException(422,"unknown security")
        if data["source_evidence_id"] and not s.get(EvidenceRecord,data["source_evidence_id"]):raise HTTPException(422,"unknown source evidence")
        x=UniverseMembership(**data);s.add(x);commit(s);return {"id":x.id}
    @app.get("/api/v1/evidence-records")
    def evidence_list(offset:int=0,limit:int=50,s:Session=Depends(db)):return page([{c.name:getattr(x,c.name) for c in EvidenceRecord.__table__.columns} for x in s.scalars(select(EvidenceRecord).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.post("/api/v1/evidence-records",status_code=201)
    def evidence(body:EvidenceIn,s:Session=Depends(db)):
        d=body.model_dump();d["available_at"]=require_utc(d["available_at"]);d["retrieved_at"]=require_utc(d["retrieved_at"])
        if not s.get(Provider,d["provider_id"]):raise HTTPException(422,"unknown provider")
        if d["value_presence"] not in {"PRESENT","MISSING","UNKNOWN","NOT_APPLICABLE"} or d["use_status"] not in {"NOT_EVALUATED","FRESH","STALE","CONFLICTING","UNAVAILABLE_PIT"}:raise HTTPException(422,"invalid evidence state")
        if (d["value_presence"]=="PRESENT") != (d["value"] is not None):raise HTTPException(422,"presence/value mismatch")
        if d["value_presence"]!="PRESENT" and not d["reason"]:raise HTTPException(422,"missing value requires reason")
        if d["value_presence"]!="PRESENT" and d["use_status"] not in {"NOT_EVALUATED","UNAVAILABLE_PIT"}:raise HTTPException(422,"non-present evidence cannot be fresh, stale, or conflicting")
        if d["use_status"]=="CONFLICTING" and not (d["conflict_group_id"] or "").strip():raise HTTPException(422,"conflicting value requires nonempty group")
        if d["observation_mode"] not in {"LIVE_CAPTURE","HISTORICAL_IMPORT"}:raise HTTPException(422,"invalid observation mode")
        now=datetime.now(timezone.utc)
        if d["observation_mode"]=="LIVE_CAPTURE" and (not d["available_at"] or not d["retrieved_at"] or not(d["available_at"]<=d["retrieved_at"]<=now)):raise HTTPException(422,"invalid live chronology")
        if d["supersedes_id"]:
            old=s.get(EvidenceRecord,d["supersedes_id"])
            if not old or (old.subject_type,old.subject_id,old.metric)!=(d["subject_type"],d["subject_id"],d["metric"]):raise HTTPException(422,"invalid evidence supersession")
        x=EvidenceRecord(**d,ingested_at=now,created_at=now);s.add(x);commit(s);return {"id":x.id,"use_status":x.use_status,"pit_eligible":False}
    @app.post("/api/v1/decision-preflights",status_code=201)
    def preflight(body:PreflightIn,s:Session=Depends(db)):
        try:return service.preflight(s,body.mandate_version_id,body.risk_budget_version_id,body.decision_timestamp,body.tradable_at,body.evidence_ids)
        except Exception as e:
            from .risk_editor import EditorStorageError
            if isinstance(e,EditorStorageError): return editor_error(e)
            if isinstance(e,service.ConflictError): raise HTTPException(409,str(e))
            if isinstance(e,(ValueError,LookupError)): raise HTTPException(422,str(e))
            raise
    @app.get("/api/v1/datasets")
    def datasets(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in ProviderDatasetVersion.__table__.columns} for x in s.scalars(select(ProviderDatasetVersion).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/license-use-permissions")
    def license_permissions(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in LicenseUsePermission.__table__.columns} for x in s.scalars(select(LicenseUsePermission).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/ingestion-runs")
    def ingestion_runs(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in IngestionRun.__table__.columns} for x in s.scalars(select(IngestionRun).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/ingestion-attempts")
    def ingestion_attempts(offset:int=0,limit:int=50,s:Session=Depends(db)):
        phase2_display(s)
        rows=s.scalars(select(IngestionAttempt).offset(offset).limit(min(limit,100))).all()
        return page([{c.name:getattr(x,c.name) for c in IngestionAttempt.__table__.columns} for x in rows],offset,limit)
    @app.get("/api/v1/source-snapshots")
    def source_snapshots(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in SourceSnapshot.__table__.columns} for x in s.scalars(select(SourceSnapshot).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/source-snapshot-parts")
    def source_parts(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in SourceSnapshotPart.__table__.columns} for x in s.scalars(select(SourceSnapshotPart).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/source-row-summaries")
    def source_rows(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{"id":x.id,"snapshot_id":x.snapshot_id,"part_id":x.part_id,"row_key":x.row_key,"row_hash":x.row_hash} for x in s.scalars(select(SourceRow).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/identity-candidates")
    def identity_candidates(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in SourceSecurityCandidate.__table__.columns} for x in s.scalars(select(SourceSecurityCandidate).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/staged-membership-events")
    def staged_events(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in StagedMembershipEvent.__table__.columns} for x in s.scalars(select(StagedMembershipEvent).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/api/v1/identity-review-revisions")
    def identity_reviews(offset:int=0,limit:int=50,s:Session=Depends(db)):phase2_display(s);return page([{c.name:getattr(x,c.name) for c in IdentityReviewRevision.__table__.columns} for x in s.scalars(select(IdentityReviewRevision).offset(offset).limit(min(limit,100))).all()],offset,limit)
    @app.get("/",response_class=HTMLResponse)
    def home(s:Session=Depends(db)):
        # Do this before querying any manifest, run or permission material; a
        # denied display permission must not render a partial Data Evidence page.
        phase2_display(s)
        st=service.status(s); providers=s.scalars(select(Provider)).all(); evidence=s.scalars(select(EvidenceRecord)).all();datasets=s.scalars(select(ProviderDatasetVersion)).all();permissions=s.scalars(select(LicenseUsePermission)).all();runs=s.scalars(select(IngestionRun).order_by(IngestionRun.request_started_at.desc()).limit(10)).all();snapshots=s.scalars(select(SourceSnapshot).order_by(SourceSnapshot.created_at.desc()).limit(10)).all();unresolved=s.query(SourceSecurityCandidate).count();events=s.query(StagedMembershipEvent).count()
        p="".join(f"<li>{escape(x.name)} — {escape(x.validation_status)}</li>" for x in providers) or "<li>No provider declarations</li>";e="".join(f"<li>{escape(x.metric)}: {escape(x.value_presence)} / {escape(x.use_status)} — {escape(x.reason or 'no reason')}</li>" for x in evidence) or "<li>No evidence records</li>";d="".join(f"<li>{escape(x.dataset_name)} — {escape(x.validation_status)}</li>" for x in datasets) or "<li>No dataset declarations</li>";lp="".join(f"<li>{escape(x.use_type)} — {escape(x.permission)} — {escape(x.duty or 'no duty recorded')}</li>" for x in permissions) or "<li>No license-use evidence</li>"
        rr="".join(f"<li>{escape(x.state)} — {escape(x.error_code or 'no error')}</li>" for x in runs) or "<li>No collection run</li>";ss="".join(f"<li>{escape(x.manifest_sha256)} — {escape(x.state)}</li>" for x in snapshots) or "<li>No snapshot</li>"
        return f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{{font-family:system-ui;margin:auto;max-width:52rem;padding:1rem}}form{{display:grid;gap:.4rem;border:1px solid #999;padding:1rem}}@media(max-width:500px){{body{{padding:.5rem}}}}</style></head><body><main><h1>OptiVest Generic Research</h1><p><strong>{st["production_readiness"]}</strong> · RISK BUDGET NOT APPROVED</p><p>Provider/PIT/tradability validation NOT VERIFIED. Missing values remain missing.</p><h2>Data Evidence</h2><p>Forward-only provider capture metadata. License use, timestamp, coverage and PIT status remain NOT VERIFIED. Historical universe is NOT RELIABLY BACKTESTABLE; unresolved identities are excluded.</p><h3>Dataset declarations</h3><ul>{d}</ul><h3>License-use evidence</h3><ul>{lp}</ul><h3>Latest capture runs</h3><ul>{rr}</ul><h3>Snapshot manifests</h3><ul>{ss}</ul><p>Unresolved identities: {unresolved}; staged membership events: {events}. Forward-universe history has no approved start.</p><h2>Provisional Mandate</h2><form><label>Research horizon <input value="7 years" readonly></label><label>Base currency <input value="USD" readonly></label></form><h2>Risk Budget</h2><p>BALANCED_RESEARCH_V1; calibrated limits show NOT VERIFIED rather than zero.</p><h2>Provider limitations</h2><ul>{p}</ul><h2>Security and identifier history</h2><p>Stable security IDs; ticker is never identity.</p><h2>Evidence entry and list</h2><ul>{e}</ul><h2>Decision preflight</h2><form><label>Evidence IDs <input aria-label="Evidence IDs" placeholder="comma-separated stable IDs"></label><button type="button" disabled>Research preflight requires API submission</button></form><p>No forecast, ranking, action, target weight, order, or trade control exists.</p></main></body></html>'''
    return app

app:FastAPI|None=None
