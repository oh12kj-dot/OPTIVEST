"""Forward-only Phase 2 provider evidence capture; never projects securities."""
from __future__ import annotations
import csv, hashlib, inspect, json, os, re, tempfile, time, uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session
from .models import CaptureScope, DatasetHead, IngestionAttempt, IngestionRun, LicenseEvidenceVersion, LicenseUsePermission, Provider, ProviderDatasetVersion, RawObject, RunSnapshotResult, SourceRow, SourceSnapshot, SourceSnapshotPart, SourceSecurityCandidate, StagedMembershipEvent, IdentityReviewHead, IdentityReviewRevision
SHA=re.compile(r"^[0-9a-f]{64}$"); LICENSE_USES=("NETWORK_CAPTURE","LOCAL_RAW_STORAGE","RETENTION","DERIVED_STORAGE","INTERNAL_DISPLAY","REDISTRIBUTION","COMMERCIAL_PRODUCTION"); PARSER_VERSION="phase2-v1"; _PARSER_REGISTRY={}
class Phase2Error(ValueError):
 def __init__(self,code,*,audit=None): super().__init__(code);self.audit=audit or []
def now(): return datetime.now(timezone.utc)
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(v): return hashlib.sha256(v).hexdigest()
def parser_artifact_hash(parser):
 bundle=[parser]
 if parser is parse_sec_submissions if "parse_sec_submissions" in globals() else False:
  # A submissions capture may carry separate filing-header and XBRL evidence
  # parts.  They are one versioned parser artifact, not implicit facts inferred
  # from the submissions response.
  bundle=[parse_sec_submissions,parse_sec_filing_header,parse_sec_xbrl_evidence]
 if parser in {parse_nasdaq_capture,parse_nasdaq_part} if "parse_nasdaq_capture" in globals() else False:
  bundle=[parse_nasdaq_capture,parse_nasdaq_part,parse_nasdaq_listed,parse_nasdaq_otherlisted,_directory_rows]
 sources=[]
 for item in bundle:
  try: source=inspect.getsource(item)
  except (OSError,TypeError): source=repr(item)
  sources.append({"name":getattr(item,"__name__","parser"),"source":source})
 return digest(canon({"artifacts":sources,"format":"phase2-provider-envelope-v2"}))
def sanitize_url(v):
 p=urlsplit(v);h=p.hostname or ""; h=f"{h}:{p.port}" if p.port else h
 return urlunsplit((p.scheme,h,p.path,"",""))
def _headers(v): return {str(k):str(x) for k,x in v.items() if str(k).lower() in {"etag","last-modified","retry-after","content-type"}}
class RawStore:
 def __init__(self,root=None): self.root=Path(root or os.environ.get("OPTIVEST_RAW_ROOT",".optivest-data/raw")).resolve()
 def key(self,sha):
  if not SHA.fullmatch(sha):raise Phase2Error("INVALID_RAW_SHA256")
  p=(self.root/sha[:2]/sha).resolve()
  try:p.relative_to(self.root)
  except ValueError as e:raise Phase2Error("RAW_PATH_ESCAPE") from e
  return p
 def put(self,data):
  sha=digest(data);target=self.key(sha);target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():
   if target.is_symlink() or target.read_bytes()!=data:raise Phase2Error("RAW_INTEGRITY_MISMATCH")
  else:
   fd,tmp=tempfile.mkstemp(prefix=".tmp-",dir=target.parent)
   try:
    with os.fdopen(fd,"wb") as f:f.write(data);f.flush();os.fsync(f.fileno())
    if Path(tmp).read_bytes()!=data:raise Phase2Error("RAW_INTEGRITY_MISMATCH")
    try:os.link(tmp,target)
    except FileExistsError:
     if target.is_symlink() or target.read_bytes()!=data:raise Phase2Error("RAW_INTEGRITY_MISMATCH")
   finally:Path(tmp).unlink(missing_ok=True)
  return sha,len(data),str(target.relative_to(self.root)).replace("\\","/")
 def get(self,sha):
  p=self.key(sha)
  if not p.is_file() or p.is_symlink():raise Phase2Error("RAW_OBJECT_MISSING")
  data=p.read_bytes()
  if digest(data)!=sha:raise Phase2Error("RAW_INTEGRITY_MISMATCH")
  return data
def _directory_rows(raw,required,symbol,trailer_field_count=None):
 try:lines=raw.decode("utf-8-sig").splitlines()
 except UnicodeDecodeError as e:raise Phase2Error("NASDAQ_ENCODING_INVALID") from e
 if len(lines)<3:raise Phase2Error("NASDAQ_TRAILER_INVALID")
 header_fields=lines[0].split("|")
 trailer_fields=lines[-1].split("|")
 if (len(trailer_fields)!=(trailer_field_count or len(header_fields)) or
     not re.fullmatch(r"File Creation Time:\s*\d{8,12}:?\d{0,2}",trailer_fields[0].strip()) or
     any(field for field in trailer_fields[1:])):raise Phase2Error("NASDAQ_TRAILER_INVALID")
 rows=list(csv.DictReader(lines[:-1],delimiter="|"));header=set(rows[0].keys() if rows else [])
 if not required.issubset(header):raise Phase2Error("NASDAQ_HEADER_INVALID")
 if not rows:raise Phase2Error("NASDAQ_ZERO_ROWS")
 for r in rows:
  if not r or any(x is None for x in r.values()) or not (r.get(symbol) or "").strip():raise Phase2Error("NASDAQ_ROW_INVALID")
  if r.get("Test Issue") not in {"N","Y"}:raise Phase2Error("NASDAQ_UNKNOWN_CODE")
 return rows
def parse_nasdaq_listed(raw):
 rows=_directory_rows(raw,{"Symbol","Security Name","Market Category","Test Issue","Financial Status","Round Lot Size","ETF","NextShares"},"Symbol")
 for r in rows:
  if r["Market Category"] not in {"Q","G","S"} or r["Financial Status"] not in {"N","D","E","Q","G","H","J","K","C",""} or r["ETF"] not in {"Y","N"} or r["NextShares"] not in {"Y","N"}:raise Phase2Error("NASDAQ_UNKNOWN_CODE")
  label=(r.get("Security Name") or "").lower()
  non_common=any(token in label for token in (" warrant"," rights"," units"," preferred"," preference"," note"," bond"," etn"," etp"," fund"," trust"," depositary"," structured"))
  # The directory's flags are source evidence, but are not an implicit common-stock
  # classification.  Only an explicit publisher label can be a candidate for the
  # supported common-equity review queue; every other row remains review-required.
  explicit_common="common stock" in label or "ordinary shares" in label
  r["_instrument_evidence"]={"security_name":r["Security Name"],"etf":r["ETF"],"nextshares":r["NextShares"]}
  r["_inclusion"]="ELIGIBLE_FOR_REVIEW" if explicit_common and r["Test Issue"]=="N" and r["ETF"]=="N" and r["NextShares"]=="N" and not non_common else "REVIEW_REQUIRED"
 return rows
def parse_nasdaq_otherlisted(raw):
 # Nasdaq's current otherlisted trailer has six empty fields despite its
 # eight-column header; accept that documented observed schema only.
 rows=_directory_rows(raw,{"ACT Symbol","Security Name","Exchange","Test Issue","ETF","Round Lot Size"},"ACT Symbol",trailer_field_count=7)
 for r in rows:
  if r["Exchange"] not in {"A","N","P","Z","V","M"} or r["ETF"] not in {"Y","N"}:raise Phase2Error("NASDAQ_UNKNOWN_CODE")
  label=(r.get("Security Name") or "").lower()
  non_common=any(token in label for token in (" warrant"," rights"," units"," preferred"," preference"," note"," bond"," etn"," etp"," fund"," trust"," depositary"," structured"))
  explicit_common="common stock" in label or "ordinary shares" in label
  r["_instrument_evidence"]={"security_name":r["Security Name"],"etf":r["ETF"],"exchange":r["Exchange"]}
  r["_inclusion"]="ELIGIBLE_FOR_REVIEW" if explicit_common and r["Test Issue"]=="N" and r["ETF"]=="N" and r["Exchange"] in {"A","N","P"} and not non_common else "REVIEW_REQUIRED"
 return rows
def parse_nasdaq_part(raw):
 try:head=raw.decode("utf-8-sig").splitlines()[0].split("|")
 except UnicodeDecodeError as e:raise Phase2Error("NASDAQ_ENCODING_INVALID") from e
 if "ACT Symbol" in head:return parse_nasdaq_otherlisted(raw)
 if {"Market Category","Financial Status","ETF","NextShares"}.issubset(head):return parse_nasdaq_listed(raw)
 return _directory_rows(raw,{"Symbol","Security Name","Test Issue"},"Symbol")
def parse_nasdaq_capture(raw):
    """Marker parser: collection dispatches the two publisher formats by part name."""
    return parse_nasdaq_part(raw)
def parse_sec_submissions(raw):
 try:data=json.loads(raw.decode())
 except (UnicodeDecodeError,json.JSONDecodeError) as e:raise Phase2Error("SEC_SCHEMA_INVALID") from e
 if not isinstance(data,dict) or not str(data.get("cik","")).isdigit():raise Phase2Error("SEC_SCHEMA_INVALID")
 cik=str(data["cik"]).zfill(10);recent=(data.get("filings") or {}).get("recent") or {}
 if recent and not isinstance(recent,dict):raise Phase2Error("SEC_SCHEMA_INVALID")
 fields=("accessionNumber","form","filingDate","reportDate","acceptanceDateTime","primaryDocument","isXBRL","isInlineXBRL");n=max([len(x) for x in recent.values() if isinstance(x,list)] or [0]);filings=[]
 for i in range(n):
   f={k:(recent.get(k,[None]*n)[i] if isinstance(recent.get(k),list) and i<len(recent[k]) else None) for k in fields}
   if f["accessionNumber"] and (not isinstance(f["accessionNumber"],str) or not re.fullmatch(r"\d{10}-\d{2}-\d{6}",f["accessionNumber"])):raise Phase2Error("SEC_SCHEMA_INVALID")
   if f["form"] is not None and (not isinstance(f["form"],str) or not f["form"].strip()):raise Phase2Error("SEC_SCHEMA_INVALID")
   f["raw_linked_accession"] = f["accessionNumber"]
   f["amendment"] = bool(f["form"] and f["form"].upper().endswith("/A"))
   f["acceptance_at_claimed"] = f["acceptanceDateTime"]
   f["acceptance_timezone"] = "AS_PUBLISHED" if f["acceptanceDateTime"] else None
   f["acceptance_precision"] = "AS_PUBLISHED" if f["acceptanceDateTime"] else None
   filings.append(f)
 historical=(data.get("filings") or {}).get("files",[])
 if not isinstance(historical,list) or any(not isinstance(x,dict) for x in historical):raise Phase2Error("SEC_SCHEMA_INVALID")
 return [{"cik":cik,"name":data.get("name"),"tickers":data.get("tickers",[]),"exchanges":data.get("exchanges",[]),"filings":filings,"historical_files":historical,"xbrl_evidence":{"status":"NOT_IN_SUBMISSIONS_PAYLOAD","frame":None,"context":None,"unit":None}}]

_ACCESSION=re.compile(r"\d{10}-\d{2}-\d{6}")
def _sec_header_value(text,label):
 match=re.search(rf"(?mi)^\s*{re.escape(label)}\s*:\s*(.+?)\s*$",text)
 return match.group(1).strip() if match else None
def parse_sec_filing_header(raw):
 """Normalize a separately captured SEC filing header; never make it a fact."""
 try:text=raw.decode("utf-8-sig")
 except UnicodeDecodeError as e:raise Phase2Error("SEC_FILING_HEADER_ENCODING") from e
 accession=_sec_header_value(text,"ACCESSION NUMBER")
 form=_sec_header_value(text,"CONFORMED SUBMISSION TYPE")
 if not accession or not _ACCESSION.fullmatch(accession) or not form:raise Phase2Error("SEC_FILING_HEADER_INVALID")
 filing_date=_sec_header_value(text,"FILED AS OF DATE")
 report_date=_sec_header_value(text,"CONFORMED PERIOD OF REPORT")
 acceptance=_sec_header_value(text,"ACCEPTANCE-DATETIME")
 primary=_sec_header_value(text,"PRIMARY DOCUMENT") or _sec_header_value(text,"DOCUMENT")
 if any(value is not None and not value.strip() for value in (filing_date,report_date,acceptance,primary)):raise Phase2Error("SEC_FILING_HEADER_INVALID")
 return [{"part_semantics":"SEC_FILING_HEADER","raw_linked_accession":accession,"form":form,"filing_date":filing_date,"report_date":report_date,"acceptance_datetime":acceptance,"primary_document":primary,"amendment":form.upper().endswith("/A")}]
def parse_sec_xbrl_evidence(raw):
 """Normalize explicit XBRL evidence parts without asserting they were submissions fields."""
 try:data=json.loads(raw.decode())
 except (UnicodeDecodeError,json.JSONDecodeError) as e:raise Phase2Error("SEC_XBRL_SCHEMA_INVALID") from e
 rows=data if isinstance(data,list) else data.get("facts",data.get("data")) if isinstance(data,dict) else None
 if not isinstance(rows,list) or not rows:raise Phase2Error("SEC_XBRL_SCHEMA_INVALID")
 result=[]
 for item in rows:
  if not isinstance(item,dict):raise Phase2Error("SEC_XBRL_SCHEMA_INVALID")
  accession=item.get("accession") or item.get("accessionNumber") or item.get("accn")
  filed=item.get("filed") or item.get("filingDate")
  frame=item.get("frame")
  context=item.get("context") or item.get("contextRef") or item.get("context_id")
  unit=item.get("unit") or item.get("uom")
  dimensions=item.get("dimensions") if isinstance(item.get("dimensions"),dict) else None
  if not isinstance(accession,str) or not _ACCESSION.fullmatch(accession):raise Phase2Error("SEC_XBRL_SCHEMA_INVALID")
  if any(value is not None and not isinstance(value,str) for value in (filed,frame,context,unit)):raise Phase2Error("SEC_XBRL_SCHEMA_INVALID")
  result.append({"part_semantics":"SEC_XBRL_EVIDENCE","raw_linked_accession":accession,"filed":filed,"frame":frame,"context":context,"unit":unit,"dimensions":dimensions})
 return result
def normalized_rows(rows):return [(digest(canon(row)),row) for row in rows]
def _register_builtin_parsers():
 for parser in (parse_sec_submissions,parse_nasdaq_capture,parse_nasdaq_part):
  _PARSER_REGISTRY[(PARSER_VERSION,parser_artifact_hash(parser))]=parser
_register_builtin_parsers()
class _NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def fetch(url,headers,timeout=30):
 current=url;chain=[];opener=build_opener(_NoRedirect)
 for _ in range(10):
  try:r=opener.open(Request(current,headers=headers),timeout=timeout);status=r.status;body=r.read();hdr=dict(r.headers.items());final=r.geturl()
  except HTTPError as e:status=e.code;body=e.read();hdr=dict(e.headers.items());final=e.geturl()
  if status in {301,302,303,307,308} and hdr.get("Location"):chain.append(sanitize_url(current));current=urljoin(current,hdr["Location"]);continue
  return status,body,{"headers":_headers(hdr),"final_url":sanitize_url(final),"redirect_count":len(chain),"redirect_chain":chain}
 # The redirect chain is evidence even when the limit is reached.  Preserve it
 # through the normal attempt-audit path rather than converting it to an opaque
 # transport exception.
 raise Phase2Error("REDIRECT_LIMIT",audit=[{"status":status,"headers":_headers(hdr),"final_url":sanitize_url(current),"redirect_count":len(chain),"redirect_chain":chain,"request_started_at":now(),"response_completed_at":now(),"_body":body}])
class RateLimiter:
 def __init__(self,rate=5.,clock=time.monotonic,sleep=time.sleep):self.rate=rate;self.clock=clock;self.sleep=sleep;self.tokens=1.;self.last=clock()
 def acquire(self):
  c=self.clock();self.tokens=min(1.,self.tokens+(c-self.last)*self.rate);self.last=c
  if self.tokens<1:self.sleep((1-self.tokens)/self.rate);c=self.clock();self.tokens=min(1.,self.tokens+(c-self.last)*self.rate);self.last=c
  self.tokens-=1
DEFAULT_LIMITER=RateLimiter()
def request_with_retry(url,headers,transport=fetch,limiter=None,sleep=time.sleep,jitter=lambda _:0.,clock=time.monotonic):
 limiter=limiter or RateLimiter();audit=[];last=None;started=clock()
 for attempt in range(1,5):
  limiter.acquire();at=now()
  try:
   remaining=120-(clock()-started)
   if remaining<=0:raise Phase2Error("HTTP_DEADLINE_EXCEEDED",audit=audit)
   if transport is fetch: status,body,*tail=transport(url,headers,timeout=min(30,remaining))
   else: status,body,*tail=transport(url,headers)
   extra=tail[0] if tail else {};chain=[sanitize_url(x) for x in extra.get("redirect_chain",[])];item={"status":status,"headers":_headers(extra.get("headers",{})),"final_url":sanitize_url(extra.get("final_url",url)),"redirect_count":int(extra.get("redirect_count",len(chain))),"redirect_chain":chain,"request_started_at":at,"response_completed_at":now(),"_body":body};audit.append(item);last=(status,body)
   if clock()-started>120:raise Phase2Error("HTTP_DEADLINE_EXCEEDED",audit=audit)
   if status not in {429,503} and not 500<=status<=599:return status,body,attempt,audit
  except Phase2Error:raise
  except Exception as e:audit.append({"status":None,"headers":{},"final_url":sanitize_url(url),"redirect_count":0,"redirect_chain":[],"request_started_at":at,"response_completed_at":now(),"error_code":"TIMEOUT" if isinstance(e,TimeoutError) else "TRANSPORT_ERROR"})
  if attempt<4:
   retry=audit[-1]["headers"].get("Retry-After")
   try:
    if retry is None: raise ValueError
    try: delay=float(retry)
    except ValueError:
     retry_at=parsedate_to_datetime(retry)
     if retry_at.tzinfo is None: retry_at=retry_at.replace(tzinfo=timezone.utc)
     delay=(retry_at.astimezone(timezone.utc)-now()).total_seconds()
    delay=max(0.,min(30.,delay))
   except (TypeError,ValueError,IndexError,OverflowError):delay=min(8.,2**(attempt-1))+jitter(attempt)
   if clock()-started+delay>120:break
   sleep(delay)
 if last:return last[0],last[1],len(audit),audit
 raise Phase2Error("HTTP_RETRY_EXHAUSTED",audit=audit)
def permission(s,d,u):return s.execute(text("SELECT p.permission FROM provider_dataset_versions d JOIN license_use_permissions p ON p.license_evidence_version_id=d.license_evidence_version_id WHERE d.id=:d AND p.use_type=:u"),{"d":d,"u":u}).scalar() or "NOT_VERIFIED"
def permission_duty(s,d,u):return s.execute(text("SELECT p.duty FROM provider_dataset_versions d JOIN license_use_permissions p ON p.license_evidence_version_id=d.license_evidence_version_id WHERE d.id=:d AND p.use_type=:u"),{"d":d,"u":u}).scalar()
def require_permissions(s,d,*uses):
 if any(permission(s,d,u)!="ALLOWED" for u in uses):raise Phase2Error("BLOCKED_POLICY")
 # Retention permission is not meaningful without the applicable deletion or
 # retention duty.  Empty duty text is therefore fail-closed, not a default.
 if "RETENTION" in uses and not (permission_duty(s,d,"RETENTION") or "").strip():raise Phase2Error("BLOCKED_POLICY")
def require_capture_permission(s,d):require_permissions(s,d,"NETWORK_CAPTURE","LOCAL_RAW_STORAGE","RETENTION","DERIVED_STORAGE")
def _part_parser(name,parser):
 if parser is parse_sec_submissions:
  if name=="filing_header":return parse_sec_filing_header
  if name=="xbrl_evidence":return parse_sec_xbrl_evidence
 return (parse_nasdaq_listed if name=="nasdaqlisted" else parse_nasdaq_otherlisted) if parser is parse_nasdaq_capture and name in {"nasdaqlisted","otherlisted"} else parser
def _attempt(s,run,name,a):
 raw=None
 if isinstance(a.get("_body"),(bytes,bytearray)):
  raw,length,key=RawStore().put(bytes(a["_body"]))
  if not s.get(RawObject,raw):s.add(RawObject(sha256=raw,byte_length=length,object_key=key));s.flush()
 s.add(IngestionAttempt(id=str(uuid.uuid4()),run_id=run.id,part_name=name,request_started_at=a["request_started_at"],response_completed_at=a.get("response_completed_at"),http_status=a.get("status"),response_headers=a.get("headers",{}),final_url=a.get("final_url"),redirect_count=a.get("redirect_count",0),redirect_chain=a.get("redirect_chain",[]),error_code=a.get("error_code"),raw_sha256=raw))
def _terminal(s,run_id,state,code=None,commit=True,completed_at=None):
 result=s.execute(update(IngestionRun).where(IngestionRun.id==run_id,IngestionRun.state=="STARTED").values(state=state,response_completed_at=completed_at or now(),error_code=code,error_reason=code))
 if result.rowcount!=1:raise Phase2Error("INVALID_RUN_TRANSITION")
 if commit:s.commit()
def _failed(c):return "BLOCKED_POLICY" if c=="BLOCKED_POLICY" else "FAILED_INTEGRITY" if any(x in c for x in ("RAW_","MANIFEST_","PARSER_ARTIFACT","INTEGRITY")) else "FAILED_PARSE" if any(x in c for x in ("NASDAQ","SEC_SCHEMA","HTML","CONTENT","PAIR","CIK_MISMATCH","DUPLICATE")) else "FAILED_HTTP"
def collect(s,dataset_id,scope_key,requests,parser,headers,transport=fetch,limiter=None,request_options=None):
 scope=s.scalar(select(CaptureScope).where(CaptureScope.provider_dataset_version_id==dataset_id,CaptureScope.capture_scope_key==scope_key))
 if not scope:scope=CaptureScope(provider_dataset_version_id=dataset_id,capture_scope_key=scope_key,request_identity=scope_key);s.add(scope);s.flush()
 ds=s.get(ProviderDatasetVersion,dataset_id)
 if not ds or ds.semantic_version!=PARSER_VERSION or ds.parser_name!=getattr(parser,"__name__",None) or ds.parser_hash!=parser_artifact_hash(parser):raise Phase2Error("PARSER_ARTIFACT_MISMATCH")
 finger=digest(canon({"dataset":dataset_id,"scope":scope_key,"requests":[x[1] for x in requests]}));run=IngestionRun(capture_scope_id=scope.id,request_fingerprint=finger,state="STARTED",request_started_at=now(),configuration_hash=digest(canon({"parser_hash":ds.parser_hash,"parser_version":ds.semantic_version})));s.add(run);s.commit();parts=[]
 try:
  require_capture_permission(s,dataset_id)
  if scope_key=="US_LISTED_DIRECTORY" and [x[0] for x in requests]!=["nasdaqlisted","otherlisted"]:raise Phase2Error("NASDAQ_PAIR_INVALID")
  for name,url in requests:
   status,body,_,audits=request_with_retry(url,headers,transport=transport,limiter=limiter or DEFAULT_LIMITER,**(request_options or {}))
   for a in audits:_attempt(s,run,name,a)
   s.commit();meta=audits[-1];media=next((v for k,v in meta["headers"].items() if k.lower()=="content-type"),"").split(";",1)[0].lower()
   if status!=200:raise Phase2Error(f"HTTP_{status}")
   if body.lstrip().lower().startswith(b"<html"):raise Phase2Error("HTML_PAYLOAD")
   if name in {"submissions","xbrl_evidence"} and media and media not in {"application/json","application/octet-stream"}:raise Phase2Error("WRONG_CONTENT_TYPE")
   if name not in {"submissions","xbrl_evidence"} and media and not(media.startswith("text/") or media=="application/octet-stream"):raise Phase2Error("WRONG_CONTENT_TYPE")
   rows=_part_parser(name,parser)(body)
   if name=="submissions" and rows[0]["cik"]!=scope_key.zfill(10):raise Phase2Error("CIK_MISMATCH")
   parts.append((name,body,media or ("application/json" if name=="submissions" else "text/plain"),meta,rows))
  snap,publication_at=_advance(s,scope,run,parts,ds,parser)
  # All publication records are held in this one transaction.  The only usable
  # timestamp is stamped after all parts/rows/events exist, immediately before
  # terminal transition and CAS head publication; no partial state is committed.
  _terminal(s,run.id,"SUCCEEDED",commit=False,completed_at=publication_at)
  _publish_head(s,scope,snap,publication_at)
  s.commit()
  return snap
 except Exception as e:
  run_id=run.id
  s.rollback()
  if isinstance(e,Phase2Error) and e.audit:
   for a in e.audit:_attempt(s,run,"unknown",a)
   s.commit()
  _terminal(s,run_id,_failed(str(e)),str(e))
  raise
def _advance(s,scope,run,parts,ds,parser):
 manifest=[]
 for n,b,media,meta,rows in parts:
  sha,length,key=RawStore().put(b)
  if not s.get(RawObject,sha):s.add(RawObject(sha256=sha,byte_length=length,object_key=key))
  manifest.append({"ordinal":len(manifest)+1,"part_name":n,"raw_sha256":sha,"byte_length":length})
 mh=digest(canon({"dataset_version":ds.id,"scope":scope.capture_scope_key,"parser_version":ds.semantic_version,"parser_hash":ds.parser_hash,"parts":manifest}));old=s.scalar(select(SourceSnapshot).where(SourceSnapshot.capture_scope_id==scope.id,SourceSnapshot.manifest_sha256==mh))
 if old:
  publication_at=now()
  s.add(RunSnapshotResult(run_id=run.id,snapshot_id=old.id,result_type="REUSED",created_at=publication_at));s.flush();return old,publication_at
 observed=max((x[3]["response_completed_at"] for x in parts),default=now());snap=SourceSnapshot(capture_scope_id=scope.id,run_id=run.id,manifest=manifest,manifest_sha256=mh,parser_version=ds.semantic_version,parser_hash=ds.parser_hash,observed_at=observed,usable_at=observed,state="SUCCEEDED");s.add(snap);s.flush()
 for ordinal,(name,body,media,meta,rows) in enumerate(parts,1):
  sha,length,_=RawStore().put(body);time_text=body.decode("utf-8-sig").splitlines()[-1].split("|",1)[0].split(":",1)[1].strip() if name in {"nasdaqlisted","otherlisted"} else None;part=SourceSnapshotPart(snapshot_id=snap.id,ordinal=ordinal,part_name=name,raw_sha256=sha,byte_length=length,media_type=media,response_completed_at=meta["response_completed_at"],http_status=meta["status"],response_headers=meta["headers"],final_url=meta["final_url"],redirect_count=meta["redirect_count"],redirect_chain=meta["redirect_chain"],request_started_at=meta["request_started_at"],source_time_text=time_text,source_timezone="UNSPECIFIED" if time_text else None,source_precision="MINUTE" if time_text else None,source_published_at=None,available_at_claimed=None,available_at_validated=None,source_time_reason="TIMEZONE_NOT_DOCUMENTED" if time_text else "NO_DATASET_PUBLICATION_INSTANT");s.add(part);s.flush();keys=set()
  for h,row in normalized_rows(rows):
   key=f"{name}:{h}"
   if key in keys:raise Phase2Error("DUPLICATE_SOURCE_IDENTITY")
   keys.add(key);s.add(SourceRow(snapshot_id=snap.id,part_id=part.id,row_key=key,row_hash=h,normalized=row))
 # This is the single canonical publication timestamp for a new snapshot.  It
 # is generated only after parts and rows exist, then flows unchanged through
 # staged events, run completion, run-result, and scoped-head publication.
 publication_at=now()
 if publication_at<observed: publication_at=observed
 s.execute(update(SourceSnapshot).where(SourceSnapshot.id==snap.id).values(usable_at=publication_at))
 snap.usable_at=publication_at
 if scope.capture_scope_key=="US_LISTED_DIRECTORY":
  candidates=[]
  for name,_,_,_,rows in parts:
   for row in rows:
    if row.get("_inclusion","ELIGIBLE_FOR_REVIEW")!="ELIGIBLE_FOR_REVIEW":continue
    symbol=(row.get("Symbol") or row.get("ACT Symbol") or "").strip();venue=(row.get("Exchange") or ("NASDAQ" if name=="nasdaqlisted" else "OTHER")).strip()
    if symbol:candidates.append((f"{name}|{venue}|{symbol}","instrument identity remains unresolved"))
  append_staged_events(s,scope.id,snap,candidates,False,usable_at=publication_at)
 s.add(RunSnapshotResult(run_id=run.id,snapshot_id=snap.id,result_type="NEW",created_at=publication_at));s.flush();return snap,publication_at
def _publish_head(s,scope,snap,publication_at):
 head=s.get(DatasetHead,scope.id)
 if head:
  if s.execute(update(DatasetHead).where(DatasetHead.capture_scope_id==scope.id,DatasetHead.snapshot_id==head.snapshot_id).values(snapshot_id=snap.id,updated_at=publication_at)).rowcount!=1:raise Phase2Error("STALE_DATASET_HEAD")
 else:s.add(DatasetHead(capture_scope_id=scope.id,snapshot_id=snap.id,updated_at=publication_at))
def collector_headers(sec_contact=None):
 if not sec_contact:raise Phase2Error("SEC_CONTACT_REQUIRED")
 return {"User-Agent":"OptiVest research contact="+sec_contact,"Accept-Encoding":"identity"}
def trusted_phase2_declarations():
 """Return the sole frozen seed contract, resolving only live parser hashes.

 The objects returned here are deliberately used for both insertion and
 verification.  They are declarations, not evidence of provider, license,
 timestamp, PIT, or Production validity.
 """
 common={"provider_authority_tier":"OFFICIAL","provider_version":"phase2-v1","provider_validation_status":"NOT_VERIFIED","license_retrieved_at":datetime(2026,9,9,tzinfo=timezone.utc),"license_reviewer":"Astra design assessment","license_reason":"publisher permission not verified","permission":"NOT_VERIFIED","permission_duty":"review required","timestamp_semantics":"NOT_VERIFIED","dataset_validation_status":"NOT_VERIFIED"}
 rows=(
  {"provider_id":"phase2-provider-sec","provider_name":"SEC EDGAR","license_id":"phase2-license-sec-v1","license_url":"https://www.sec.gov/about/developer-resources","dataset_id":"phase2-dataset-sec-submissions-v1","dataset_name":"SEC_SUBMISSIONS_V1","endpoint_url":"https://data.sec.gov/submissions/CIK##########.json","parser":parse_sec_submissions,"rate_policy":{"max_requests_per_second":5}},
  {"provider_id":"phase2-provider-nasdaq","provider_name":"Nasdaq Trader Symbol Directory","license_id":"phase2-license-nasdaq-v1","license_url":"https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs","dataset_id":"phase2-dataset-nasdaq-directory-v1","dataset_name":"NASDAQ_DIRECTORY_V1","endpoint_url":"https://www.nasdaqtrader.com/dynamic/SymDir/","parser":parse_nasdaq_capture,"rate_policy":{"max_requests_per_second":1}},
 )
 result=[]
 for row in rows:
  spec={**common,**row}
  spec["provider_declarations"]={"reference_url":spec["license_url"],"license_status":"NOT_VERIFIED"}
  spec["provider_source_reference"]=spec["license_url"]
  spec["license_artifact_sha256"]=digest(canon({"reference":spec["license_url"],"all_uses":"NOT_VERIFIED"}))
  spec["parser_name"]=spec["parser"].__name__
  spec["parser_hash"]=parser_artifact_hash(spec["parser"])
  spec["permissions"]={use:{"permission":spec["permission"],"duty":spec["permission_duty"]} for use in LICENSE_USES}
  result.append(spec)
 return tuple(result)
def seed_public_evidence(s):
 for spec in trusted_phase2_declarations():
  pid,name,lid,url,did,dname,endpoint,parser=(spec[key] for key in ("provider_id","provider_name","license_id","license_url","dataset_id","dataset_name","endpoint_url","parser"))
  if not s.get(Provider,pid):s.add(Provider(id=pid,name=name,authority_tier=spec["provider_authority_tier"],version=spec["provider_version"],declarations=spec["provider_declarations"],source_reference=spec["provider_source_reference"],validation_status=spec["provider_validation_status"]));s.flush()
  if not s.get(LicenseEvidenceVersion,lid):
   s.add(LicenseEvidenceVersion(id=lid,provider_id=pid,artifact_sha256=spec["license_artifact_sha256"],canonical_url=url,retrieved_at=spec["license_retrieved_at"],reviewer=spec["license_reviewer"],reason=spec["license_reason"]));s.flush()
   for use,permission in spec["permissions"].items():s.add(LicenseUsePermission(id=f"{lid}-{use}",license_evidence_version_id=lid,use_type=use,permission=permission["permission"],duty=permission["duty"]))
  _PARSER_REGISTRY[(PARSER_VERSION,spec["parser_hash"])]=parser
  if not s.get(ProviderDatasetVersion,did):s.add(ProviderDatasetVersion(id=did,provider_id=pid,dataset_name=dname,semantic_version=PARSER_VERSION,endpoint_url=endpoint,parser_name=spec["parser_name"],parser_hash=spec["parser_hash"],license_evidence_version_id=lid,timestamp_semantics=spec["timestamp_semantics"],rate_policy=spec["rate_policy"],validation_status=spec["dataset_validation_status"]))
 s.commit();return {"datasets":2,"permission":"NOT_VERIFIED","capture":"BLOCKED_POLICY"}
def append_staged_events(s,scope_id,snapshot,candidates,commit=True,usable_at=None):
 usable_at=usable_at or snapshot.usable_at
 existing={x.stable_key:x for x in s.scalars(select(SourceSecurityCandidate).where(SourceSecurityCandidate.capture_scope_id==scope_id)).all()};seen=set()
 for key,reason in candidates:
  seen.add(key);candidate=existing.get(key)
  if not candidate:
   candidate=SourceSecurityCandidate(capture_scope_id=scope_id,stable_key=key,state="UNRESOLVED");s.add(candidate);s.flush();event="FIRST_OBSERVED";r=IdentityReviewRevision(candidate_id=candidate.id,revision=1,status="UNRESOLVED",actor="collector",method_version="phase2-collector-v1",evidence_ids=[],reason="collection creates unresolved identity");s.add(r);s.flush();s.add(IdentityReviewHead(candidate_id=candidate.id,revision_id=r.id))
  else:
   prior=s.scalar(select(StagedMembershipEvent).where(StagedMembershipEvent.candidate_id==candidate.id).order_by(StagedMembershipEvent.observed_at.desc()));event="REAPPEARED" if prior and prior.event_type=="POSSIBLE_REMOVAL" else "PRESENT"
  s.add(StagedMembershipEvent(candidate_id=candidate.id,snapshot_id=snapshot.id,event_type=event,observed_at=snapshot.observed_at,usable_at=usable_at,reason=reason))
 for key,c in existing.items():
  if key not in seen:s.add(StagedMembershipEvent(candidate_id=c.id,snapshot_id=snapshot.id,event_type="POSSIBLE_REMOVAL",observed_at=snapshot.observed_at,usable_at=usable_at,reason="absent from valid forward snapshot"))
 if commit:s.commit()
def review_successor(s,candidate_id,expected_revision_id,status,actor,method_version,evidence_ids,reason):
 if status not in {"UNRESOLVED","MATCHED_REVIEWED","CONFLICT","NO_MATCH","REJECTED"} or not reason.strip() or actor=="collector":raise Phase2Error("INVALID_REVIEW")
 h=s.get(IdentityReviewHead,candidate_id);old=s.get(IdentityReviewRevision,expected_revision_id)
 if not h or h.revision_id!=expected_revision_id or not old or old.candidate_id!=candidate_id:raise Phase2Error("STALE_REVIEW")
 row=IdentityReviewRevision(candidate_id=candidate_id,supersedes_id=old.id,revision=old.revision+1,status=status,actor=actor,method_version=method_version,evidence_ids=evidence_ids,reason=reason);s.add(row);s.flush()
 if s.execute(update(IdentityReviewHead).where(IdentityReviewHead.candidate_id==candidate_id,IdentityReviewHead.revision_id==old.id).values(revision_id=row.id)).rowcount!=1:s.rollback();raise Phase2Error("STALE_REVIEW")
 s.commit();return row
def replay_snapshot(s,snapshot_id,store=None):
 snap=s.get(SourceSnapshot,snapshot_id)
 if not snap:raise Phase2Error("SNAPSHOT_NOT_FOUND")
 parser=_PARSER_REGISTRY.get((snap.parser_version,snap.parser_hash))
 if parser is None:raise Phase2Error("PARSER_ARTIFACT_UNAVAILABLE")
 scope=s.get(CaptureScope,snap.capture_scope_id)
 require_permissions(s,scope.provider_dataset_version_id,"LOCAL_RAW_STORAGE","RETENTION","DERIVED_STORAGE")
 parts=s.scalars(select(SourceSnapshotPart).where(SourceSnapshotPart.snapshot_id==snap.id).order_by(SourceSnapshotPart.ordinal)).all();manifest=[{"ordinal":p.ordinal,"part_name":p.part_name,"raw_sha256":p.raw_sha256,"byte_length":p.byte_length} for p in parts];expected=digest(canon({"dataset_version":scope.provider_dataset_version_id,"scope":scope.capture_scope_key,"parser_version":snap.parser_version,"parser_hash":snap.parser_hash,"parts":manifest}))
 if manifest!=snap.manifest or expected!=snap.manifest_sha256:raise Phase2Error("MANIFEST_INTEGRITY_MISMATCH")
 store=store or RawStore();count=0
 for p in parts:
  raw=store.get(p.raw_sha256)
  if len(raw)!=p.byte_length:raise Phase2Error("RAW_LENGTH_MISMATCH")
  actual=sorted(x[0] for x in normalized_rows(_part_parser(p.part_name,parser)(raw)));recorded=sorted(x.row_hash for x in s.scalars(select(SourceRow).where(SourceRow.part_id==p.id)).all())
  if actual!=recorded:raise Phase2Error("ROW_REPLAY_MISMATCH")
  count+=len(actual)
 return {"snapshot_id":snap.id,"state":"REPLAYABLE","manifest_sha256":snap.manifest_sha256,"part_count":len(parts),"row_count":count}

def verify_phase2(s):
 """Read-only schema, seed, and raw-object verification for the exact Phase 2 head."""
 required={"license_evidence_versions","license_use_permissions","provider_dataset_versions","capture_scopes","ingestion_runs","ingestion_attempts","raw_objects","source_snapshots","source_snapshot_parts","source_rows","dataset_heads","run_snapshot_results","source_security_candidates","staged_membership_events","identity_review_revisions","identity_review_heads"}
 names={x[0] for x in s.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))}
 revision=s.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none() if "alembic_version" in names else None
 raw_ok=True
 for raw in s.scalars(select(RawObject)).all():
  try:raw_ok=raw_ok and RawStore().get(raw.sha256).__len__()==raw.byte_length
  except Phase2Error:raw_ok=False
 datasets=s.scalars(select(ProviderDatasetVersion)).all()
 providers=s.scalars(select(Provider)).all()
 declarations=trusted_phase2_declarations()
 expected_datasets={spec["dataset_id"]:spec for spec in declarations}
 expected_providers={spec["provider_id"]:spec for spec in declarations}
 # Local declarations are accepted only when they exactly reproduce the frozen
 # identifiers and metadata.  This never upgrades provider, license, timestamp
 # or PIT truth; it merely prevents a name-shaped fake seed from starting.
 seed_ok=len(datasets)==len(expected_datasets) and len(providers)==len(expected_providers)
 seed_ok=seed_ok and {p.id for p in providers}==set(expected_providers)
 for provider in providers:
  spec=expected_providers.get(provider.id)
  seed_ok=seed_ok and spec is not None
  if spec:
   seed_ok=seed_ok and provider.name==spec["provider_name"] and provider.authority_tier==spec["provider_authority_tier"] and provider.version==spec["provider_version"]
   seed_ok=seed_ok and provider.declarations==spec["provider_declarations"] and provider.source_reference==spec["provider_source_reference"] and provider.validation_status==spec["provider_validation_status"]
 for dataset in datasets:
  spec=expected_datasets.get(dataset.id)
  seed_ok=seed_ok and spec is not None
  if spec:
   seed_ok=seed_ok and dataset.provider_id==spec["provider_id"] and dataset.dataset_name==spec["dataset_name"] and dataset.endpoint_url==spec["endpoint_url"]
   seed_ok=seed_ok and dataset.semantic_version==PARSER_VERSION and dataset.parser_name==spec["parser_name"] and dataset.parser_hash==spec["parser_hash"]
   seed_ok=seed_ok and dataset.timestamp_semantics==spec["timestamp_semantics"] and dataset.rate_policy==spec["rate_policy"] and dataset.validation_status==spec["dataset_validation_status"] and dataset.license_evidence_version_id==spec["license_id"]
   license_row=s.get(LicenseEvidenceVersion,spec["license_id"])
   actual_retrieved=license_row.retrieved_at.replace(tzinfo=timezone.utc) if license_row and license_row.retrieved_at.tzinfo is None else license_row.retrieved_at if license_row else None
   seed_ok=seed_ok and license_row is not None and license_row.provider_id==spec["provider_id"] and license_row.artifact_sha256==spec["license_artifact_sha256"] and license_row.canonical_url==spec["license_url"]
   seed_ok=seed_ok and actual_retrieved==spec["license_retrieved_at"] and license_row.reviewer==spec["license_reviewer"] and license_row.reason==spec["license_reason"]
  if spec:
   rows=s.execute(text("SELECT use_type,permission,duty FROM license_use_permissions WHERE license_evidence_version_id=:id"),{"id":dataset.license_evidence_version_id}).all()
   matrix={r.use_type:(r.permission,r.duty) for r in rows}
   seed_ok=seed_ok and len(rows)==len(LICENSE_USES) and set(matrix)==set(LICENSE_USES)
   seed_ok=seed_ok and matrix=={use:(expected["permission"],expected["duty"]) for use,expected in spec["permissions"].items()}
 return {"phase2_schema":required.issubset(names) and revision in {"0002_phase2","0003_research_risk_editor"},"revision":revision,"seed_state":seed_ok,"raw_integrity":raw_ok,"counts":{"datasets":len(datasets),"runs":s.query(IngestionRun).count(),"snapshots":s.query(SourceSnapshot).count(),"attempts":s.query(IngestionAttempt).count(),"unresolved_identities":s.query(SourceSecurityCandidate).count(),"staged_events":s.query(StagedMembershipEvent).count()},"production_readiness":"NOT PRODUCTION READY","provider_pit":"NOT VERIFIED"}
