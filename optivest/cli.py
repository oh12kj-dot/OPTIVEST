from __future__ import annotations
import argparse, json, os
from pathlib import Path
from alembic import command
from alembic.config import Config
from .db import make_session
from . import service
def main():
 # Dispatch the lab before parser/database construction: it never opens a DB.
 if len(os.sys.argv)>=3 and os.sys.argv[1]=="wealth-lab":
  from . import wealth_lab
  def emit(payload):
   try: os.sys.stdout.buffer.write(wealth_lab.canonical_bytes(payload)+b"\n");os.sys.stdout.buffer.flush()
   except (OSError,BrokenPipeError):
    try: os.sys.stderr.write("OUTPUT_WRITE_FAILED\n");os.sys.stderr.flush()
    except Exception: pass
    raise SystemExit(1)
  mode=os.sys.argv[2]
  if mode=="--help" and len(os.sys.argv)==3:
   os.sys.stdout.write("usage: wealth-lab {example|evaluate --file PATH}\n");return
  if mode=="example" and len(os.sys.argv)==3:
   try: payload=wealth_lab._decode(wealth_lab.example_bytes())
   except wealth_lab.LabError as e: payload=wealth_lab._failure(e.code,"",e.status)
   emit(payload)
   if payload.get("status")=="INTERNAL_ERROR":raise SystemExit(1)
   return
  if mode=="evaluate" and len(os.sys.argv)==5 and os.sys.argv[3]=="--file":
   try: provenance=wealth_lab._provenance()
   except wealth_lab.LabError as e:
    out=wealth_lab._failure(e.code,"",e.status);emit(out);raise SystemExit(1)
   source=Path(os.sys.argv[4])
   try:
    exists=os.path.lexists(source)
   except OSError: exists=False
   if not exists: out=wealth_lab._failure("INPUT_FILE_MISSING","","INVALID_INPUT",provenance)
   else:
    try:
     stat=source.lstat();reparse=bool(getattr(stat,"st_file_attributes",0)&0x400)
     regular=source.is_file() and not source.is_symlink() and not reparse
    except OSError: regular=False
    if not regular: out=wealth_lab._failure("INPUT_FILE_NOT_REGULAR","","INVALID_INPUT",provenance)
    else:
     try:
      chunks=[];total=0
      with source.open("rb") as handle:
       while True:
        chunk=handle.read(65536)
        if not chunk:break
        total+=len(chunk)
        if total>wealth_lab.MAX_INPUT:
         out=wealth_lab._failure("JSON_SIZE","","INVALID_INPUT",provenance);break
        chunks.append(chunk)
       else: pass
      if total<=wealth_lab.MAX_INPUT:out=wealth_lab.evaluate_bytes(b"".join(chunks))
     except OSError: out=wealth_lab._failure("INPUT_FILE_UNREADABLE","","INVALID_INPUT",provenance)
   emit(out)
   status=out.get("evaluation",out).get("status")
   raise SystemExit(0 if status=="COMPUTED_SYNTHETIC" else 2 if status in {"INVALID_INPUT","INPUT_INCOMPLETE"} else 1)
  out=wealth_lab._failure("ARGUMENT_INVALID","","INVALID_INPUT")
  emit(out);raise SystemExit(2)
 p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True); db=sub.add_parser("db"); db.add_argument("operation",choices=["upgrade","downgrade","current"]); sub.add_parser("seed-research"); sub.add_parser("seed-phase2-public-evidence"); sub.add_parser("verify-phase1"); sub.add_parser("verify-phase2"); rb=sub.add_parser("risk-budget"); rbsub=rb.add_subparsers(dest="risk_cmd",required=True); show=rbsub.add_parser("show");show.add_argument("--version-id"); preview=rbsub.add_parser("preview");preview.add_argument("--file",required=True); save=rbsub.add_parser("save");save.add_argument("--file",required=True); sub.add_parser("verify-risk-editor"); sec=sub.add_parser("collect-sec-submissions");sec.add_argument("--cik",required=True); sub.add_parser("collect-nasdaq-directory"); replay=sub.add_parser("replay-snapshot");replay.add_argument("--snapshot-id",required=True); serve=sub.add_parser("serve");serve.add_argument("--host",default="127.0.0.1");serve.add_argument("--port",type=int,default=8000); a=p.parse_args()
 if a.cmd=="db":
  c=Config("alembic.ini");c.set_main_option("sqlalchemy.url",os.environ.get("OPTIVEST_DATABASE_URL","sqlite:///./optivest.db"));command.upgrade(c,"head") if a.operation=="upgrade" else command.downgrade(c,"base") if a.operation=="downgrade" else command.current(c);return
 if a.cmd=="serve":
  import uvicorn
  from .app import app_for
  uvicorn.run(app_for(),host=a.host,port=a.port)
  return
 _, factory=make_session();s=factory()
 if a.cmd=="verify-risk-editor":
  from .risk_editor import verify_risk_editor, EditorStorageError
  try: print(json.dumps(verify_risk_editor(s)));s.close();return
  except EditorStorageError as e: print(json.dumps({"error":e.code}));s.close();raise SystemExit(1)
 if a.cmd=="risk-budget":
  from .risk_editor import strict_decode, EditorError
  try:
   if a.risk_cmd=="show": result=service.editor_version(s,a.version_id)
   else:
    payload=strict_decode(open(a.file,"rb").read())
    result=service.editor_preview(s,payload) if a.risk_cmd=="preview" else service.editor_save(s,payload)
   def _json_default(value):
    if hasattr(value,"isoformat"): return value.isoformat().replace("+00:00","Z")
    return str(value)
   print(json.dumps(result,default=_json_default,ensure_ascii=False));s.close()
   if result.get("diagnostics",{}).get("consistency_status")=="RISK BUDGET INCONSISTENT": raise SystemExit(2)
   return
  except (EditorError,service.ConflictError) as e:
   print(json.dumps({"error":{"code":getattr(e,"code",str(e)),"path":getattr(e,"path","")}}));s.close();raise SystemExit(2)
  except Exception:
   s.rollback();s.close();print(json.dumps({"error":{"code":"INTERNAL_ERROR"}}));raise SystemExit(1)
 if a.cmd=="seed-research":
  service.seed(s); print(json.dumps(service.status(s)));s.close();return
 if a.cmd=="seed-phase2-public-evidence":
  from .phase2 import seed_public_evidence
  print(json.dumps(seed_public_evidence(s)));s.close();return
 if a.cmd=="verify-phase1":
  report=service.status(s); print(json.dumps(report));s.close()
  if not report["mandate_version_id"] or not report["risk_budget_version_id"]: raise SystemExit(1)
 if a.cmd=="verify-phase2":
  from .phase2 import verify_phase2
  report=verify_phase2(s);print(json.dumps(report));s.close()
  if not (report["phase2_schema"] and report["seed_state"] and report["raw_integrity"]):raise SystemExit(1)
 if a.cmd in {"collect-sec-submissions","collect-nasdaq-directory"}:
  from sqlalchemy import select
  from .models import ProviderDatasetVersion
  from .phase2 import collect,collector_headers,parse_sec_submissions,parse_nasdaq_capture,Phase2Error
  name="SEC_SUBMISSIONS_V1" if a.cmd=="collect-sec-submissions" else "NASDAQ_DIRECTORY_V1"
  dataset=s.scalar(select(ProviderDatasetVersion).where(ProviderDatasetVersion.dataset_name==name))
  try:
   contact=os.environ.get("OPTIVEST_SEC_CONTACT") if a.cmd=="collect-sec-submissions" else None
   if a.cmd=="collect-sec-submissions":headers=collector_headers(contact)
   if not dataset:raise Phase2Error("BLOCKED_POLICY")
   if a.cmd=="collect-sec-submissions":
    cik=a.cik.removeprefix("CIK").zfill(10);snapshot=collect(s,dataset.id,cik,[("submissions",f"https://data.sec.gov/submissions/CIK{cik}.json")],parse_sec_submissions,headers)
   else:snapshot=collect(s,dataset.id,"US_LISTED_DIRECTORY",[("nasdaqlisted","https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"),("otherlisted","https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt")],parse_nasdaq_capture,{"User-Agent":"OptiVest research"})
   print(json.dumps({"snapshot_id":snapshot.id,"state":"SUCCEEDED"}));s.close();return
  except Phase2Error as e:
   s.close();print(json.dumps({"state":"BLOCKED_POLICY" if str(e)=="BLOCKED_POLICY" else "FAILED","reason":str(e)}));raise SystemExit(2 if str(e) in {"BLOCKED_POLICY","SEC_CONTACT_REQUIRED"} else 1)
 if a.cmd=="replay-snapshot":
  from .phase2 import replay_snapshot,Phase2Error
  try:
   print(json.dumps(replay_snapshot(s,a.snapshot_id)));s.close()
  except Phase2Error as e:print(json.dumps({"error":str(e)}));s.close();raise SystemExit(1)
if __name__=="__main__": main()
