import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from optivest.db import make_session
from optivest.models import Provider, ProviderDatasetVersion, CaptureScope, DatasetHead, IngestionAttempt, RawObject, RunSnapshotResult, SourceSnapshot, SourceSnapshotPart, SourceRow, IngestionRun, SourceSecurityCandidate, StagedMembershipEvent, IdentityReviewHead
from optivest.phase2 import collect, review_successor, replay_snapshot, seed_public_evidence
from optivest.phase2 import LICENSE_USES, Phase2Error, RawStore, RateLimiter, PARSER_VERSION, parser_artifact_hash, parse_nasdaq_capture, parse_nasdaq_listed, parse_nasdaq_otherlisted, parse_nasdaq_part, parse_sec_submissions, parse_sec_filing_header, parse_sec_xbrl_evidence, request_with_retry, collector_headers, require_permissions
from optivest.app import app_for
from optivest import service

def test_raw_store_is_content_addressed_and_rejects_bad_hashes():
    with tempfile.TemporaryDirectory() as d:
        store=RawStore(d);sha,length,key=store.put(b"abc")
        assert sha==hashlib.sha256(b"abc").hexdigest() and length==3 and store.get(sha)==b"abc"
        with pytest.raises(Phase2Error):store.get("A"*64)
def test_deterministic_candidate_parsers_fail_closed():
    good=b"Symbol|Security Name|Test Issue\r\nABC|ABC Corp|N\r\nFile Creation Time: 20260908||\r\n"
    assert parse_nasdaq_part(good)[0]["Symbol"]=="ABC"
    with pytest.raises(Phase2Error):parse_nasdaq_part(b"<html>error</html>")
    assert parse_sec_submissions(b'{"cik":"1","name":"Example","filings":{}}')[0]["cik"]=="0000000001"
    with pytest.raises(Phase2Error):parse_sec_submissions(b"{}")
    with pytest.raises(Phase2Error):parse_sec_filing_header(b"ACCESSION NUMBER: bad\n")
    with pytest.raises(Phase2Error):parse_sec_xbrl_evidence(b'{"facts":[]}')

def test_nasdaq_exact_publisher_trailers_preserve_timestamp_and_reject_nonempty_fields():
    listed=(b"Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
            b"ABC|ABC Common Stock|Q|N|N|100|N|N\n"
            b"File Creation Time: 0908202621:31|||||||\n")
    other=(b"ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\n"
           b"ABC|ABC Common Stock|N|ABC|N|100|N|ABC\n"
           b"File Creation Time: 0908202621:31||||||\n")
    assert parse_nasdaq_listed(listed)[0]["Symbol"]=="ABC"
    assert parse_nasdaq_otherlisted(other)[0]["ACT Symbol"]=="ABC"
    for body in (listed.replace(b"|||||||",b"||||||X"),other.replace(b"||||||",b"|||||X")):
        with pytest.raises(Phase2Error,match="NASDAQ_TRAILER_INVALID"):parse_nasdaq_part(body)
@pytest.mark.parametrize("body",[
    b"Symbol|Security Name|Test Issue\nFile Creation Time: 0908202621:31\n",
    b"Symbol|Security Name|Test Issue\nABC|ABC Corp|Z\nFile Creation Time: 0908202621:31\n",
    b"Symbol|Security Name|Test Issue\nABC|ABC Corp|N\n",
    b"<html>error</html>",b"Symbol|Security Name\nABC|x\nFile Creation Time: 0908202621:31\n",
])
def test_nasdaq_negative_parser_matrix(body):
    with pytest.raises((Phase2Error,UnicodeDecodeError)):parse_nasdaq_part(body)
@pytest.mark.parametrize("sha",["../"+"a"*64,"a"*63,"A"*64,"/"+"a"*64])
def test_raw_store_rejects_noncanonical_keys(sha):
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(Phase2Error):RawStore(d).key(sha)
def test_http_retry_is_injected_and_bounded():
    calls=[]
    def transport(url,headers):
        calls.append(url)
        return (503,b"busy") if len(calls)<3 else (200,b"ok")
    class Limiter:
        def __init__(self):self.calls=0
        def acquire(self):self.calls+=1
    limiter=Limiter();status,body,attempt,audit=request_with_retry("https://official.invalid",{},transport=transport,limiter=limiter,sleep=lambda _:None)
    assert (status,body,attempt,limiter.calls,len(audit))==(200,b"ok",3,3,3)
def test_five_hz_token_bucket_spaces_http_dispatches():
    state={"now":0.0};dispatch=[]
    def clock():return state["now"]
    def sleep(delay):state["now"]+=delay
    limiter=RateLimiter(rate=5.0,clock=clock,sleep=sleep)
    for _ in range(4):
        limiter.acquire();dispatch.append(clock())
    assert dispatch==pytest.approx([0.0,0.2,0.4,0.6])
def test_sec_contact_is_required_and_only_transient_header_data():
    with pytest.raises(Phase2Error):collector_headers(None)
    headers=collector_headers("operator@example.invalid")
    assert "operator@example.invalid" in headers["User-Agent"]

ROOT=Path(__file__).resolve().parents[1]
def phase2_session(tmp_path, parser=parse_sec_submissions, display_permission="ALLOWED"):
    url="sqlite:///"+(tmp_path/"phase2.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();p=Provider(name="fixture-provider",authority_tier="OFFICIAL",declarations={},validation_status="NOT_VERIFIED");s.add(p);s.flush()
    for license_id,hash_value in (("lic","a"*64),("lic-nasdaq","c"*64)):
        s.execute(text("INSERT INTO license_evidence_versions (id,provider_id,artifact_sha256,canonical_url,retrieved_at,reviewer,reason,created_at) VALUES (:id,:p,:h,'fixture',CURRENT_TIMESTAMP,'test','fixture permission only',CURRENT_TIMESTAMP)"),{"id":license_id,"p":p.id,"h":hash_value})
        for u in LICENSE_USES:s.execute(text("INSERT INTO license_use_permissions (id,license_evidence_version_id,use_type,permission,duty) VALUES (:id,:license,:u,:permission,:d)"),{"id":license_id+"-"+u,"license":license_id,"u":u,"permission":display_permission if u=="INTERNAL_DISPLAY" else "ALLOWED","d":"retain only for fixture deletion policy" if u=="RETENTION" else None})
    d=ProviderDatasetVersion(provider_id=p.id,dataset_name="SEC_SUBMISSIONS_V1",semantic_version=PARSER_VERSION,endpoint_url="fixture",parser_name=parser.__name__,parser_hash=parser_artifact_hash(parser),license_evidence_version_id="lic",timestamp_semantics="NOT_VERIFIED",rate_policy={},validation_status="NOT_VERIFIED")
    d2=ProviderDatasetVersion(provider_id=p.id,dataset_name="NASDAQ_DIRECTORY_V1",semantic_version=PARSER_VERSION,endpoint_url="fixture",parser_name="parse_nasdaq_capture",parser_hash=parser_artifact_hash(parse_nasdaq_capture),license_evidence_version_id="lic-nasdaq",timestamp_semantics="NOT_VERIFIED",rate_policy={},validation_status="NOT_VERIFIED")
    s.add_all((d,d2));s.commit();return s,d
def test_sec_scopes_deduplicate_bytes_and_repeat_does_not_duplicate_snapshot(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path);body=b'{"cik":"1","name":"Example","filings":{}}'
    transport=lambda url,*_: (200, body if url.endswith("/1") else b'{"cik":"2","name":"Example","filings":{}}')
    a=collect(s,d.id,"0000000001",[("submissions","https://fixture/1")],parse_sec_submissions,{},transport=transport)
    b=collect(s,d.id,"0000000002",[("submissions","https://fixture/2")],parse_sec_submissions,{},transport=transport)
    again=collect(s,d.id,"0000000001",[("submissions","https://fixture/1")],parse_sec_submissions,{},transport=transport)
    assert a.id==again.id and s.query(DatasetHead).count()==2 and s.query(RawObject).count()==2 and s.query(SourceSnapshot).count()==2
    s.close()
def test_sec_filing_header_and_xbrl_parts_preserve_exact_raw_linked_evidence(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path)
    submissions=b'{"cik":"1","name":"Example","filings":{"recent":{"accessionNumber":["0000123456-24-000001"],"form":["10-K/A"],"filingDate":["2024-02-01"],"reportDate":["2023-12-31"],"acceptanceDateTime":["20240201123456"],"primaryDocument":["annual.htm"]}}}'
    header=(b"ACCESSION NUMBER: 0000123456-24-000001\nCONFORMED SUBMISSION TYPE: 10-K/A\nFILED AS OF DATE: 20240201\nCONFORMED PERIOD OF REPORT: 20231231\nACCEPTANCE-DATETIME: 20240201123456\nPRIMARY DOCUMENT: annual.htm\n")
    xbrl=b'{"facts":[{"accn":"0000123456-24-000001","filed":"2024-02-01","frame":"CY2023","contextRef":"ctx-annual","uom":"USD","dimensions":{"segment":"consolidated"}}]}'
    payloads={"submissions":submissions,"filing_header":header,"xbrl_evidence":xbrl}
    def transport(url,*_):
        name=url.rsplit("/",1)[-1]
        return 200,payloads[name],{"headers":{"Content-Type":"text/plain" if name=="filing_header" else "application/json"}}
    snapshot=collect(s,d.id,"0000000001",[(name,"fixture://"+name) for name in payloads],parse_sec_submissions,{},transport=transport,limiter=_NoWaitLimiter())
    parts=s.scalars(select(SourceSnapshotPart).where(SourceSnapshotPart.snapshot_id==snapshot.id)).all()
    rows=s.scalars(select(SourceRow).where(SourceRow.snapshot_id==snapshot.id)).all()
    normalized=[row.normalized for row in rows]
    header_row=next(row for row in normalized if row.get("part_semantics")=="SEC_FILING_HEADER")
    xbrl_row=next(row for row in normalized if row.get("part_semantics")=="SEC_XBRL_EVIDENCE")
    assert header_row=={"part_semantics":"SEC_FILING_HEADER","raw_linked_accession":"0000123456-24-000001","form":"10-K/A","filing_date":"20240201","report_date":"20231231","acceptance_datetime":"20240201123456","primary_document":"annual.htm","amendment":True}
    assert xbrl_row["raw_linked_accession"]=="0000123456-24-000001" and xbrl_row["filed"]=="2024-02-01" and xbrl_row["frame"]=="CY2023" and xbrl_row["context"]=="ctx-annual" and xbrl_row["unit"]=="USD" and xbrl_row["dimensions"]=={"segment":"consolidated"}
    assert {part.part_name for part in parts}==set(payloads) and all(RawStore(str(tmp_path/"raw")).get(part.raw_sha256)==payloads[part.part_name] for part in parts)
    submission_row=next(row for row in normalized if "filings" in row)
    assert submission_row["xbrl_evidence"]["status"]=="NOT_IN_SUBMISSIONS_PAYLOAD"
    s.close()
@pytest.mark.parametrize("parser,body",[(parse_sec_filing_header,b"ACCESSION NUMBER: 0000123456-24-000001\n"),(parse_sec_xbrl_evidence,b'{"facts":[{"accn":"bad"}]}')])
def test_sec_explicit_evidence_part_parsers_reject_missing_or_malformed_fields(parser,body):
    with pytest.raises(Phase2Error):parser(body)
def test_nasdaq_invalid_pair_never_moves_existing_head_and_records_failure(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path,parse_nasdaq_part);good=b"Symbol|Security Name|Test Issue\nABC|ABC Corp|N\nFile Creation Time: 0908202621:31||\n";transport=lambda *_:(200,good)
    first=collect(s,d.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","a"),("otherlisted","b")],parse_nasdaq_part,{},transport=transport)
    with pytest.raises(Phase2Error):collect(s,d.id,"US_LISTED_DIRECTORY",[("otherlisted","b"),("nasdaqlisted","a")],parse_nasdaq_part,{},transport=transport)
    assert s.get(DatasetHead,s.scalar(select(DatasetHead.capture_scope_id))).snapshot_id==first.id
    assert any(state!="SUCCEEDED" for state in s.scalars(select(IngestionRun.state)).all())
    s.close()
def test_paired_nasdaq_collection_rejects_a_bad_second_part_without_a_head(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path,parse_nasdaq_capture)
    listed=b"Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\nABC|ABC Corp|Q|N|N|100|N|N\nFile Creation Time: 0908202621:31|||||||\n"
    other=b"ACT Symbol|Security Name|Exchange|Test Issue|ETF|Round Lot Size\nABC|ABC Corp|X|N|N|100\nFile Creation Time: 0908202621:31||||||\n"
    calls=[]
    def transport(*_):
        calls.append(1);return (200,listed if len(calls)==1 else other)
    with pytest.raises(Phase2Error,match="NASDAQ_UNKNOWN_CODE"):
        collect(s,d.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","a"),("otherlisted","b")],parse_nasdaq_capture,{},transport=transport,limiter=_NoWaitLimiter())
    assert len(calls)==2 and s.query(DatasetHead).count()==0
    assert s.scalar(select(IngestionRun.state))=="FAILED_PARSE"
    s.close()
@pytest.mark.parametrize("requests,body",[
    ([("nasdaqlisted","a")],b"Symbol|Security Name|Test Issue\nABC|ABC Corp|N\nFile Creation Time: 0908202621:31\n"),
    ([("nasdaqlisted","a"),("nasdaqlisted","b")],b"Symbol|Security Name|Test Issue\nABC|ABC Corp|N\nFile Creation Time: 0908202621:31\n"),
    ([("nasdaqlisted","a"),("otherlisted","b")],b"<html>error</html>"),
    ([("nasdaqlisted","a"),("otherlisted","b")],b"Symbol|Security Name|Test Issue\nFile Creation Time: 0908202621:31\n"),
])
def test_failed_nasdaq_inputs_never_move_prior_head(tmp_path,monkeypatch,requests,body):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path,parse_nasdaq_part);good=b"Symbol|Security Name|Test Issue\nABC|ABC Corp|N\nFile Creation Time: 0908202621:31||\n";ok=lambda *_:(200,good)
    first=collect(s,d.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","a"),("otherlisted","b")],parse_nasdaq_part,{},transport=ok)
    with pytest.raises(Phase2Error):collect(s,d.id,"US_LISTED_DIRECTORY",requests,parse_nasdaq_part,{},transport=lambda *_:(200,body))
    assert s.get(DatasetHead,s.scalar(select(DatasetHead.capture_scope_id))).snapshot_id==first.id
    if body.startswith(b"<html>"):assert s.query(RawObject).count()==2
    s.close()
def test_permission_matrix_blocks_unknown_and_blocked_uses(tmp_path):
    s,d=phase2_session(tmp_path)
    require_permissions(s,d.id,"NETWORK_CAPTURE","LOCAL_RAW_STORAGE")
    require_permissions(s,d.id,"INTERNAL_DISPLAY")
    s.close()
def test_raw_tamper_and_partial_are_rejected(tmp_path):
    store=RawStore(str(tmp_path/"raw"));sha,_,_=store.put(b"safe");path=store.key(sha);path.write_bytes(b"tampered")
    with pytest.raises(Phase2Error):store.get(sha)
    partial=path.parent/".tmp-partial";partial.write_bytes(b"partial")
    assert not store.key(sha).name.startswith(".tmp")
def test_raw_store_rejects_symlink_escape_or_skips_when_windows_denies(tmp_path):
    store=RawStore(str(tmp_path/"raw"));sha,_,_=store.put(b"safe");target=store.key(sha);outside=tmp_path/"outside";outside.write_bytes(b"outside");target.unlink()
    try:target.symlink_to(outside)
    except OSError:pytest.skip("Windows symlink creation denied")
    with pytest.raises(Phase2Error):store.get(sha)

class _NoWaitLimiter:
    def acquire(self):
        return None

def _attempt_rows(session):
    return session.execute(text(
        "SELECT request_started_at, response_completed_at, http_status, response_headers, "
        "final_url, redirect_count, redirect_chain, error_code FROM ingestion_attempts ORDER BY rowid"
    )).all()

def test_attempt_audit_persists_redirect_and_sanitizes_metadata(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path)
    body=b'{"cik":"1","name":"Example","filings":{}}'
    def transport(url,headers):
        return 200,body,{"headers":{"ETag":"v1","Content-Type":"application/json","Authorization":"secret","X-Trace":"hidden"},"final_url":"https://user:pw@fixture.invalid/final?token=secret#frag","redirect_count":1,"redirect_chain":["https://fixture.invalid/start?secret=1"]}
    collect(s,d.id,"0000000001",[("submissions","https://fixture.invalid/start")],parse_sec_submissions,{},transport=transport,limiter=_NoWaitLimiter())
    rows=_attempt_rows(s);assert len(rows)==1
    start,end,status,headers,url,count,chain,error=rows[0]
    assert start<=end and status==200 and count==1 and error is None
    assert json.loads(headers)=={"ETag":"v1","Content-Type":"application/json"}
    assert url=="https://fixture.invalid/final" and json.loads(chain)==["https://fixture.invalid/start"]
    assert "secret" not in headers+url+chain.lower()
    part=s.execute(text("SELECT response_headers,final_url,redirect_chain FROM source_snapshot_parts")).one()
    persisted=json.dumps(dict(part._mapping))
    assert "Authorization" not in persisted and "token=" not in persisted
    s.close()

def test_attempt_audit_persists_retry_after_then_success(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path);calls=[];delays=[]
    body=b'{"cik":"1","name":"Example","filings":{}}'
    def transport(url,headers):
        calls.append(1)
        if len(calls)==1:return 429,b"busy",{"headers":{"Retry-After":"0","Content-Type":"text/plain"}}
        return 200,body,{"headers":{"Content-Type":"application/json"}}
    collect(s,d.id,"0000000001",[("submissions","https://fixture.invalid/sec")],parse_sec_submissions,{},transport=transport,limiter=_NoWaitLimiter(),request_options={"sleep":delays.append})
    rows=_attempt_rows(s);assert [r.http_status for r in rows]==[429,200]
    assert json.loads(rows[0].response_headers)["Retry-After"]=="0" and delays==[0.0]
    assert all(r.request_started_at<=r.response_completed_at for r in rows)
    s.close()

@pytest.mark.parametrize("mode,expected_code",[("5xx","HTTP_503"),("timeout","HTTP_RETRY_EXHAUSTED")])
def test_terminal_transport_failures_are_audited_without_head(tmp_path,monkeypatch,mode,expected_code):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path)
    def transport(url,headers):
        if mode=="timeout":raise TimeoutError("contains no secret")
        return 503,b"busy",{"headers":{"Content-Type":"text/plain"}}
    with pytest.raises(Phase2Error,match=expected_code):
        collect(s,d.id,"0000000001",[("submissions","https://fixture.invalid/sec")],parse_sec_submissions,{},transport=transport,limiter=_NoWaitLimiter(),request_options={"sleep":lambda _:None})
    rows=_attempt_rows(s);assert len(rows)==4 and s.query(DatasetHead).count()==0
    if mode=="timeout":assert all(r.http_status is None and r.error_code=="TIMEOUT" for r in rows)
    else:assert all(r.http_status==503 for r in rows)
    run=s.scalar(select(IngestionRun));assert run.state=="FAILED_HTTP" and run.error_code==expected_code
    s.close()

def test_sec_contact_never_persists_in_success_or_blocked_subprocess(tmp_path,monkeypatch):
    secret="DISTINCT-CONTACT-DO-NOT-PERSIST@example.invalid"
    raw_root=tmp_path/"raw";monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(raw_root));s,d=phase2_session(tmp_path)
    body=b'{"cik":"1","name":"Example","filings":{}}'
    headers=collector_headers(secret)
    collect(s,d.id,"0000000001",[("submissions","https://fixture.invalid/sec")],parse_sec_submissions,headers,transport=lambda *_:(200,body,{"headers":{"Content-Type":"application/json"}}),limiter=_NoWaitLimiter())
    # The subprocess must exercise the production fail-closed declaration, not
    # the test-only permission used for the isolated local capture above.
    s.execute(text("DROP TRIGGER trg_license_use_permissions_immutable_update"));s.execute(text("UPDATE license_use_permissions SET permission='NOT_VERIFIED' WHERE license_evidence_version_id='lic' AND use_type='NETWORK_CAPTURE'"));s.commit()
    s.close()
    db_path=tmp_path/"phase2.db"
    assert secret.encode() not in db_path.read_bytes()
    assert all(secret.encode() not in p.read_bytes() for p in raw_root.rglob("*") if p.is_file())
    env=os.environ.copy();env.update({"OPTIVEST_DATABASE_URL":"sqlite:///"+db_path.as_posix(),"OPTIVEST_RAW_ROOT":str(raw_root),"OPTIVEST_SEC_CONTACT":secret,"PYTHONPATH":str(ROOT)})
    proc=subprocess.run([sys.executable,"-m","optivest.cli","collect-sec-submissions","--cik","1"],cwd=ROOT,env=env,text=True,capture_output=True)
    assert proc.returncode==2 and secret not in proc.stdout and secret not in proc.stderr
    assert secret.encode() not in db_path.read_bytes()
    assert all(secret.encode() not in p.read_bytes() for p in raw_root.rglob("*") if p.is_file())

def _directory_body(*symbols):
    rows="".join(f"{symbol}|{symbol} Common Stock|N\n" for symbol in symbols)
    return ("Symbol|Security Name|Test Issue\n"+rows+"File Creation Time: 0908202621:31||\n").encode()

def test_staged_membership_events_and_identity_review_are_append_only(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path,parse_nasdaq_part)
    def capture(*symbols):
        body=_directory_body(*symbols)
        return collect(s,d.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","a"),("otherlisted","b")],parse_nasdaq_part,{},transport=lambda *_:(200,body),limiter=_NoWaitLimiter())
    first=capture("ABC")
    candidate=s.scalar(select(SourceSecurityCandidate).where(SourceSecurityCandidate.stable_key.like("%ABC")))
    assert candidate and [x.event_type for x in s.scalars(select(StagedMembershipEvent).where(StagedMembershipEvent.candidate_id==candidate.id)).all()]==["FIRST_OBSERVED"]
    head=s.get(IdentityReviewHead,candidate.id);assert head;old_revision_id=head.revision_id
    successor=review_successor(s,candidate.id,old_revision_id,"NO_MATCH","reviewer","manual-v1",[],"no stable mapping evidence")
    with pytest.raises(Phase2Error,match="STALE_REVIEW"):review_successor(s,candidate.id,old_revision_id,"REJECTED","reviewer","manual-v1",[],"stale")
    assert s.get(IdentityReviewHead,candidate.id).revision_id==successor.id
    capture("DEF");capture("ABC","GHI")
    events=s.execute(text("SELECT event_type FROM staged_membership_events WHERE candidate_id=:c ORDER BY rowid"),{"c":candidate.id}).scalars().all()
    assert events==["FIRST_OBSERVED","POSSIBLE_REMOVAL","REAPPEARED"]
    assert s.execute(text("SELECT count(*) FROM securities")).scalar()==0 and s.execute(text("SELECT count(*) FROM universe_memberships")).scalar()==0
    s.close()

def test_identical_snapshot_keeps_retrieval_run_and_replay_detects_row_tamper(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path);body=b'{"cik":"1","name":"Example","filings":{}}'
    first=collect(s,d.id,"0000000001",[("submissions","https://fixture/sec")],parse_sec_submissions,{},transport=lambda *_:(200,body),limiter=_NoWaitLimiter())
    again=collect(s,d.id,"0000000001",[("submissions","https://fixture/sec")],parse_sec_submissions,{},transport=lambda *_:(200,body),limiter=_NoWaitLimiter())
    assert first.id==again.id and s.query(IngestionRun).count()==2
    assert replay_snapshot(s,first.id,RawStore(str(tmp_path/"raw")))["row_count"]==1
    s.execute(text("DROP TRIGGER trg_source_rows_immutable_update"));s.execute(text("UPDATE source_rows SET row_hash=:h"),{"h":"0"*64});s.commit()
    with pytest.raises(Phase2Error,match="ROW_REPLAY_MISMATCH"):replay_snapshot(s,first.id,RawStore(str(tmp_path/"raw")))
    s.close()

def test_raw_sql_hash_permission_and_attempt_immutability_guards(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path)
    with pytest.raises(IntegrityError):
        s.execute(text("INSERT INTO raw_objects (sha256,byte_length,object_key,created_at) VALUES (:h,1,:k,CURRENT_TIMESTAMP)"),{"h":"z"*64,"k":"zz/"+"z"*64});s.commit()
    s.rollback()
    scope=CaptureScope(provider_dataset_version_id=d.id,capture_scope_key="direct",request_identity="direct");s.add(scope);s.commit()
    with pytest.raises(IntegrityError):
        s.execute(text("INSERT INTO ingestion_runs (id,capture_scope_id,request_fingerprint,state,request_started_at,response_completed_at,configuration_hash,created_at) VALUES ('terminal',:scope,:hash,'SUCCEEDED',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,:hash,CURRENT_TIMESTAMP)"),{"scope":scope.id,"hash":"a"*64});s.commit()
    s.rollback()
    with pytest.raises(IntegrityError):
        s.execute(text("INSERT INTO license_use_permissions (id,license_evidence_version_id,use_type,permission) VALUES ('bad','lic','UNKNOWN_USE','ALLOWED')"));s.commit()
    s.rollback()
    body=b'{"cik":"1","name":"Example","filings":{}}'
    collect(s,d.id,"0000000001",[("submissions","https://fixture/sec")],parse_sec_submissions,{},transport=lambda *_:(200,body),limiter=_NoWaitLimiter())
    attempt_id=s.execute(text("SELECT id FROM ingestion_attempts LIMIT 1")).scalar_one()
    with pytest.raises(IntegrityError):s.execute(text("UPDATE ingestion_attempts SET final_url='changed' WHERE id=:id"),{"id":attempt_id});s.commit()
    s.rollback();s.close()

def test_phase2_read_only_api_ui_counts_escape_text_and_never_serve_raw_bytes(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));url="sqlite:///"+(tmp_path/"phase2.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();service.seed(s);seed_public_evidence(s)
    # Startup validates the untouched frozen declaration.  This test then uses
    # its already-created app only to exercise the fixture-only display path.
    client=TestClient(app_for(url))
    # Test-only permission elevation permits offline fixture capture; provider and
    # dataset declarations themselves remain the exact frozen trusted records.
    s.execute(text("DROP TRIGGER trg_license_use_permissions_immutable_update"));s.execute(text("UPDATE license_use_permissions SET permission='ALLOWED'"));s.commit()
    d=s.scalar(select(ProviderDatasetVersion).where(ProviderDatasetVersion.id=="phase2-dataset-sec-submissions-v1"))
    body=b'{"cik":"1","name":"Example","filings":{}}'
    collect(s,d.id,"0000000001",[("submissions","https://fixture/sec")],parse_sec_submissions,{},transport=lambda *_:(200,body),limiter=_NoWaitLimiter());s.close()
    expected={"datasets":2,"license-use-permissions":14,"ingestion-runs":1,"ingestion-attempts":1,"source-snapshots":1,"source-snapshot-parts":1,"source-row-summaries":1,"identity-candidates":0,"staged-membership-events":0,"identity-review-revisions":0}
    for route,count in expected.items():
        response=client.get("/api/v1/"+route);assert response.status_code==200 and len(response.json()["items"])==count
    assert client.get("/api/v1/raw-objects").status_code==404
    html=client.get("/").text
    assert "SEC_SUBMISSIONS_V1" in html and "NETWORK_CAPTURE" in html and "ALLOWED" in html
    assert "NOT PRODUCTION READY" in html and "NOT RELIABLY BACKTESTABLE" in html

def test_public_evidence_seed_is_idempotent_and_keeps_capture_blocked(tmp_path):
    url="sqlite:///"+(tmp_path/"seed.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();first=seed_public_evidence(s);second=seed_public_evidence(s)
    assert first==second=={"datasets":2,"permission":"NOT_VERIFIED","capture":"BLOCKED_POLICY"}
    assert s.query(ProviderDatasetVersion).count()==2
    assert s.execute(text("SELECT count(*) FROM license_use_permissions")).scalar_one()==14
    for dataset in s.scalars(select(ProviderDatasetVersion)).all():
        with pytest.raises(Phase2Error,match="BLOCKED_POLICY"):require_permissions(s,dataset.id,"NETWORK_CAPTURE","LOCAL_RAW_STORAGE")
    s.close()

def test_nasdaq_instrument_eligibility_requires_explicit_source_evidence():
    def body(name):
        return ("Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
                f"ABC|{name}|Q|N|N|100|N|N\nFile Creation Time: 0908202621:31|||||||\n").encode()
    assert parse_nasdaq_listed(body("ABC Corp"))[0]["_inclusion"]=="REVIEW_REQUIRED"
    assert parse_nasdaq_listed(body("ABC Common Stock"))[0]["_inclusion"]=="ELIGIBLE_FOR_REVIEW"
    for non_common in ("ABC Units", "ABC Warrants", "ABC Preferred Stock", "ABC Structured Note", "ABC Fund"):
        assert parse_nasdaq_listed(body(non_common))[0]["_inclusion"]=="REVIEW_REQUIRED"

def test_nasdaq_otherlisted_observed_m_exchange_is_review_required():
    body=(b"ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\n"
          b"MTEST|NYSE Texas, Inc. TEST Common Stock|M|MTEST|N|100|Y|MTEST\n"
          b"File Creation Time: 0908202621:31||||||\n")
    assert parse_nasdaq_otherlisted(body)[0]["_inclusion"]=="REVIEW_REQUIRED"

def test_collect_refuses_parser_not_matching_stored_artifact(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path)
    with pytest.raises(Phase2Error,match="PARSER_ARTIFACT_MISMATCH"):
        collect(s,d.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","fixture"),("otherlisted","fixture")],parse_nasdaq_part,{},transport=lambda *_:(200,b""))
    assert s.query(IngestionRun).count()==0
    s.close()

def test_publication_timestamp_is_exactly_shared_by_snapshot_run_result_head_and_events(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path,parse_nasdaq_part)
    publication=datetime(2026,9,9,1,2,3,tzinfo=timezone.utc)
    monkeypatch.setattr(__import__("optivest.phase2",fromlist=["now"]),"now",lambda:publication)
    body=_directory_body("ABC")
    snapshot=collect(s,d.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","a"),("otherlisted","b")],parse_nasdaq_part,{},transport=lambda *_:(200,body),limiter=_NoWaitLimiter())
    parts=s.scalars(select(SourceSnapshotPart).where(SourceSnapshotPart.snapshot_id==snapshot.id)).all()
    events=s.scalars(select(StagedMembershipEvent).where(StagedMembershipEvent.snapshot_id==snapshot.id)).all()
    normalize=lambda value:value.replace(tzinfo=None)
    run=s.get(IngestionRun,snapshot.run_id);result=s.scalar(select(RunSnapshotResult).where(RunSnapshotResult.run_id==run.id));head=s.get(DatasetHead,snapshot.capture_scope_id)
    timestamps=(snapshot.usable_at,run.response_completed_at,result.created_at,head.updated_at,*[event.usable_at for event in events])
    assert events and all(normalize(value)==normalize(publication) for value in timestamps)
    assert normalize(snapshot.usable_at)>=max(normalize(part.response_completed_at) for part in parts)
    assert run.state=="SUCCEEDED" and head.snapshot_id==snapshot.id
    s.close()

def test_redirect_limit_audit_and_http_date_retry_after_are_not_lost(tmp_path,monkeypatch):
    monkeypatch.setenv("OPTIVEST_RAW_ROOT",str(tmp_path/"raw"));s,d=phase2_session(tmp_path);delays=[]
    calls=[]
    def retry_transport(*_):
        calls.append(1)
        return (429,b"busy",{"headers":{"Retry-After":"Wed, 21 Oct 2015 07:28:00 GMT"}}) if len(calls)==1 else (200,b"ok")
    assert request_with_retry("https://fixture.invalid",{},transport=retry_transport,limiter=_NoWaitLimiter(),sleep=delays.append)[0]==200 and delays==[0.0]
    audit={"status":302,"headers":{"Location":"https://fixture.invalid/final"},"final_url":"https://fixture.invalid/final","redirect_count":10,"redirect_chain":["https://fixture.invalid/start","https://fixture.invalid/final"],"request_started_at":__import__("optivest.phase2",fromlist=["now"]).now(),"response_completed_at":__import__("optivest.phase2",fromlist=["now"]).now(),"_body":b"redirect"}
    with pytest.raises(Phase2Error,match="REDIRECT_LIMIT"):
        collect(s,d.id,"0000000001",[("submissions","fixture")],parse_sec_submissions,{},transport=lambda *_:(_ for _ in ()).throw(Phase2Error("REDIRECT_LIMIT",audit=[audit])),limiter=_NoWaitLimiter())
    attempt=s.scalar(select(IngestionAttempt).where(IngestionAttempt.redirect_count==10))
    assert attempt and attempt.final_url=="https://fixture.invalid/final" and attempt.redirect_chain[-1].endswith("/final")
    s.close()

def test_dataset_head_rejects_started_zero_part_snapshot_bypass(tmp_path):
    s,d=phase2_session(tmp_path);scope=CaptureScope(provider_dataset_version_id=d.id,capture_scope_key="empty",request_identity="empty");s.add(scope);s.flush()
    run=IngestionRun(capture_scope_id=scope.id,request_fingerprint="e"*64,state="STARTED",configuration_hash="f"*64);s.add(run);s.flush()
    snapshot=SourceSnapshot(capture_scope_id=scope.id,run_id=run.id,manifest=[],manifest_sha256="a"*64,parser_version=PARSER_VERSION,parser_hash=d.parser_hash,observed_at=run.request_started_at,usable_at=run.request_started_at,state="SUCCEEDED");s.add(snapshot);s.flush();s.add(RunSnapshotResult(run_id=run.id,snapshot_id=snapshot.id,result_type="NEW"));s.flush()
    s.execute(text("UPDATE ingestion_runs SET state='SUCCEEDED', response_completed_at=request_started_at WHERE id=:id"),{"id":run.id});s.flush();s.add(DatasetHead(capture_scope_id=scope.id,snapshot_id=snapshot.id))
    with pytest.raises(IntegrityError):s.commit()
    s.rollback();s.close()

def test_display_denial_blocks_every_phase2_surface_before_home_renders(tmp_path):
    url="sqlite:///"+(tmp_path/"phase2.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();seed_public_evidence(s);s.close();client=TestClient(app_for(url))
    for route in ("datasets","license-use-permissions","ingestion-runs","ingestion-attempts","source-snapshots","source-snapshot-parts","source-row-summaries","identity-candidates","staged-membership-events","identity-review-revisions"):
        assert client.get("/api/v1/"+route).status_code==403
    assert client.get("/").status_code==403

def test_verify_and_startup_reject_missing_permission_matrix_row(tmp_path):
    url="sqlite:///"+(tmp_path/"phase2.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();seed_public_evidence(s)
    s.execute(text("DROP TRIGGER trg_license_use_permissions_immutable_delete"));s.execute(text("DELETE FROM license_use_permissions WHERE id=(SELECT id FROM license_use_permissions WHERE use_type='INTERNAL_DISPLAY' LIMIT 1)"));s.commit()
    from optivest.phase2 import verify_phase2
    assert not verify_phase2(s)["seed_state"]
    s.close()
    with pytest.raises(RuntimeError,match="database is not migrated"):
        app_for(url)

def test_verify_and_startup_reject_name_shaped_but_wrong_frozen_declaration(tmp_path):
    url="sqlite:///"+(tmp_path/"phase2.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();seed_public_evidence(s)
    # Keep the expected names and permission matrix, but alter a trusted field
    # that a matrix-shape check would miss.
    s.execute(text("DROP TRIGGER trg_provider_dataset_versions_immutable_update"));s.execute(text("UPDATE provider_dataset_versions SET endpoint_url='https://fake.invalid/submissions' WHERE id='phase2-dataset-sec-submissions-v1'"));s.commit()
    from optivest.phase2 import verify_phase2
    assert not verify_phase2(s)["seed_state"]
    s.close()
    with pytest.raises(RuntimeError,match="database is not migrated"):
        app_for(url)

@pytest.mark.parametrize(("trigger","statement"),[
    ("trg_providers_no_update","UPDATE providers SET authority_tier='UNOFFICIAL' WHERE id='phase2-provider-sec'"),
    ("trg_license_evidence_versions_immutable_update","UPDATE license_evidence_versions SET artifact_sha256='b' || substr(artifact_sha256,2) WHERE id='phase2-license-sec-v1'"),
    ("trg_license_evidence_versions_immutable_update","UPDATE license_evidence_versions SET reviewer='unreviewed substitute' WHERE id='phase2-license-sec-v1'"),
    ("trg_provider_dataset_versions_immutable_update","UPDATE provider_dataset_versions SET rate_policy='{\"max_requests_per_second\":99}' WHERE id='phase2-dataset-sec-submissions-v1'"),
    ("trg_license_use_permissions_immutable_update","UPDATE license_use_permissions SET permission='ALLOWED' WHERE id='phase2-license-sec-v1-NETWORK_CAPTURE'"),
    ("trg_license_use_permissions_immutable_update","UPDATE license_use_permissions SET duty='changed duty' WHERE id='phase2-license-sec-v1-RETENTION'"),
])
def test_verify_cli_and_startup_reject_each_mutated_frozen_declaration_field(tmp_path,trigger,statement):
    url="sqlite:///"+(tmp_path/"phase2.db").as_posix();cfg=Config(str(ROOT/"alembic.ini"));cfg.set_main_option("sqlalchemy.url",url);command.upgrade(cfg,"head")
    _,factory=make_session(url);s=factory();seed_public_evidence(s)
    s.execute(text(f"DROP TRIGGER IF EXISTS {trigger}"));s.connection().exec_driver_sql(statement);s.commit()
    from optivest.phase2 import verify_phase2
    assert not verify_phase2(s)["seed_state"]
    s.close()
    with pytest.raises(RuntimeError,match="database is not migrated"):
        app_for(url)
    env=os.environ.copy();env.update({"OPTIVEST_DATABASE_URL":url,"PYTHONPATH":str(ROOT)})
    proc=subprocess.run([sys.executable,"-m","optivest.cli","verify-phase2"],cwd=ROOT,env=env,text=True,capture_output=True)
    assert proc.returncode != 0
