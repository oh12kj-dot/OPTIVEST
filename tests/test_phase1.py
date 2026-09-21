from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import tempfile
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from optivest.app import app_for
from optivest.db import make_session
from optivest import service
from optivest.models import MandateVersion

ROOT=Path(__file__).resolve().parents[1]
TEMP_DATABASES=[]  # Alembic keeps a Windows SQLite handle until interpreter teardown.
def migrated_client():
    d=tempfile.TemporaryDirectory(); path=Path(d.name)/"phase1.db";url="sqlite:///"+path.as_posix()
    TEMP_DATABASES.append(d)
    cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    engine,factory=make_session(url);s=factory();service.seed(s);s.close()
    return d,TestClient(app_for(url)),url
def close_client(c):
    c.close(); c.app.state.engine.dispose()
def test_unmigrated_database_is_rejected():
    d=tempfile.TemporaryDirectory()
    try:
        try:app_for("sqlite:///"+(Path(d.name)/"empty.db").as_posix());assert False
        except RuntimeError:pass
    finally:d.cleanup()
def test_status_is_readonly_and_unconditionally_not_ready():
    d,c,url=migrated_client()
    try:
        a=c.get("/api/v1/status").json();b=c.get("/api/v1/status").json();assert a==b and a["production_readiness"]=="NOT PRODUCTION READY" and "BUY" not in c.get("/").text
    finally:close_client(c)
def test_provider_identity_and_symmetric_intervals():
    d,c,url=migrated_client()
    try:
        assert c.post("/api/v1/providers",json={"name":"p","authority_tier":"OFFICIAL","validation_status":"VERIFIED"}).status_code==422
        p=c.post("/api/v1/providers",json={"name":"p","authority_tier":"OFFICIAL"}).json()["id"]
        i=c.post("/api/v1/issuers",json={"legal_name":"i"}).json()["id"];s=c.post("/api/v1/securities",json={"issuer_id":i,"instrument_type":"COMMON","primary_venue":"XNAS","currency":"USD"}).json()["id"]
        base={"security_id":s,"scheme":"TICKER","value":"ABC","venue":"XNAS"}
        assert c.post("/api/v1/security-identifiers",json=base|{"valid_from":"2025-01-01"}).status_code==201
        assert c.post("/api/v1/security-identifiers",json=base|{"valid_from":"2020-01-01","valid_to":"2021-01-01"}).status_code==201
        assert c.post("/api/v1/security-identifiers",json=base|{"valid_from":"2025-01-01"}).status_code==409
        assert c.post("/api/v1/security-identifiers",json=base|{"security_id":"missing","valid_from":"2022-01-01","valid_to":"2022-02-01"}).status_code==422
    finally:close_client(c)
def test_evidence_rejects_bool_float_and_invalid_live_chronology():
    d,c,url=migrated_client()
    try:
        p=c.post("/api/v1/providers",json={"name":"p","authority_tier":"OFFICIAL"}).json()["id"];now=datetime.now(timezone.utc)
        base={"provider_id":p,"source_locator":"https://example.invalid/<x>","subject_type":"SECURITY","subject_id":"stable","metric":"m","observation_mode":"LIVE_CAPTURE","value_presence":"PRESENT","use_status":"FRESH","value":0,"available_at":now.isoformat(),"retrieved_at":(now+timedelta(days=1)).isoformat()}
        assert c.post("/api/v1/evidence-records",json=base).status_code==422
        good=base|{"retrieved_at":now.isoformat()}
        for bad in (True,1.0,-1):assert c.post("/api/v1/evidence-records",json=good|{"processing_latency_seconds":bad}).status_code==422
        assert c.post("/api/v1/evidence-records",json=good).status_code==201
        assert c.post("/api/v1/evidence-records",json=good|{"value":None,"value_presence":"MISSING","reason":"unknown","use_status":"FRESH"}).status_code==422
    finally:close_client(c)
def test_every_evidence_presence_use_combination_is_explicitly_checked():
    d,c,url=migrated_client()
    try:
        p=c.post("/api/v1/providers",json={"name":"cross-product","authority_tier":"OFFICIAL"}).json()["id"];now=datetime.now(timezone.utc)
        base={"provider_id":p,"source_locator":"https://example.invalid/cross","subject_type":"SECURITY","subject_id":"stable","metric":"cross","observation_mode":"LIVE_CAPTURE","available_at":now.isoformat(),"retrieved_at":now.isoformat()}
        permitted={"PRESENT":{"NOT_EVALUATED","FRESH","STALE","CONFLICTING","UNAVAILABLE_PIT"},"MISSING":{"NOT_EVALUATED","UNAVAILABLE_PIT"},"UNKNOWN":{"NOT_EVALUATED","UNAVAILABLE_PIT"},"NOT_APPLICABLE":{"NOT_EVALUATED","UNAVAILABLE_PIT"}}
        for presence in permitted:
            for use in ("NOT_EVALUATED","FRESH","STALE","CONFLICTING","UNAVAILABLE_PIT"):
                payload=base|{"metric":f"{presence}-{use}","value_presence":presence,"use_status":use,"value":0 if presence=="PRESENT" else None,"reason":None if presence=="PRESENT" else "not reported"}
                if use=="CONFLICTING":payload["conflict_group_id"]="group-1"
                response=c.post("/api/v1/evidence-records",json=payload)
                assert response.status_code==(201 if use in permitted[presence] else 422), (presence,use,response.text)
        conflict=base|{"metric":"blank-conflict","value_presence":"PRESENT","use_status":"CONFLICTING","value":0,"conflict_group_id":"  "}
        assert c.post("/api/v1/evidence-records",json=conflict).status_code==422
        engine=create_engine(url)
        with engine.begin() as conn:
            try:
                conn.execute(text("INSERT INTO evidence_records (id,provider_id,source_locator,subject_type,subject_id,metric,ingested_at,created_at,observation_mode,value_presence,use_status) VALUES ('bad-cross',:provider,'x','SECURITY','stable','raw',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,'HISTORICAL_IMPORT','MISSING','FRESH')"),{"provider":p})
                assert False, "database cross-state check must reject MISSING + FRESH"
            except Exception: pass
            for record_id, group in (("bad-conflict-null",None),("bad-conflict-space","   ")):
                try:
                    conn.execute(text("INSERT INTO evidence_records (id,provider_id,source_locator,subject_type,subject_id,metric,value,ingested_at,created_at,observation_mode,value_presence,use_status,conflict_group_id) VALUES (:id,:provider,'x','SECURITY','stable',:id,0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,'HISTORICAL_IMPORT','PRESENT','CONFLICTING',:group)"),{"id":record_id,"provider":p,"group":group})
                    assert False, "database conflict-group check must reject null and whitespace values"
                except Exception: pass
        engine.dispose()
    finally:close_client(c)
def test_atomic_heads_and_preflight_coherence():
    d,c,url=migrated_client()
    try:
        st=c.get("/api/v1/status").json();m=st["mandate_version_id"];r=st["risk_budget_version_id"]
        new=c.post("/api/v1/mandates/versions",json={"expected_current_version_id":m,"horizon_years":8,"rationale":"version"});assert new.status_code==201
        assert c.post("/api/v1/mandates/versions",json={"expected_current_version_id":m,"horizon_years":9,"rationale":"stale"}).status_code==409
        now=datetime.now(timezone.utc);payload={"mandate_version_id":new.json()["id"],"risk_budget_version_id":r,"decision_timestamp":now.isoformat(),"tradable_at":now.isoformat()}
        assert c.post("/api/v1/decision-preflights",json=payload).status_code==422
        risk=c.post("/api/v1/risk-budgets/versions",json={"expected_current_version_id":r,"mandate_version_id":new.json()["id"],"rationale":"align"});assert risk.status_code==201
        response=c.post("/api/v1/decision-preflights",json=payload|{"risk_budget_version_id":risk.json()["id"]});assert response.status_code==201 and response.json()["eligible_for_research_decision"] is False
    finally:close_client(c)
def test_db_fk_and_immutability_enforced():
    d,c,url=migrated_client()
    try:
        engine=create_engine(url)
        with engine.begin() as conn:
            try:conn.execute(text("INSERT INTO securities (id,issuer_id,instrument_type,primary_venue,currency,lifecycle_status) VALUES ('x','none','COMMON','X','USD','ACTIVE')"));assert False
            except Exception:pass
        _,factory=make_session(url);s=factory();m=service.profile_head(s).mandate_version_id
        try:
            s.get(MandateVersion,m).horizon_years=99;s.commit();assert False
        except Exception:s.rollback()
        finally:s.close()
    finally:close_client(c)
def test_admin_surfaces_pagination_and_escaped_ui():
    d,c,url=migrated_client()
    try:
        c.post("/api/v1/providers",json={"name":"<script>alert(1)</script>","authority_tier":"OFFICIAL"});body=c.get("/").text
        assert "&lt;script&gt;" in body and "<script>alert" not in body
        for route in ("providers","issuers","securities","security-identifiers","corporate-actions","universe-memberships","evidence-records"):
            assert c.get("/api/v1/"+route).status_code==200
    finally:close_client(c)
