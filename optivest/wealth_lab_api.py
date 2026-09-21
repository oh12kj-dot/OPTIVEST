"""FastAPI transport for the isolated synthetic wealth laboratory."""
from __future__ import annotations

from html import escape
import re
from fastapi import Request
from fastapi.responses import HTMLResponse, Response
from . import wealth_lab

def _body(value: object, status: int = 200) -> Response:
    return Response(wealth_lab.canonical_bytes(value), status_code=status, media_type="application/json")

def register_wealth_lab(app) -> None:
    @app.get("/api/v1/wealth-lab/capabilities")
    async def wealth_lab_capabilities():
        try: return _body(wealth_lab.capabilities())
        except wealth_lab.LabError as e: return _body(wealth_lab._failure(e.code,"",e.status),503)

    @app.get("/api/v1/wealth-lab/example")
    async def wealth_lab_example():
        try: return Response(wealth_lab.example_bytes(),media_type="application/json")
        except wealth_lab.LabError as e: return _body(wealth_lab._failure(e.code,"",e.status),503)
        except Exception: return _body(wealth_lab._failure("INTERNAL_ERROR","","INTERNAL_ERROR"),503)

    @app.post("/api/v1/wealth-lab/evaluate")
    async def wealth_lab_evaluate(request: Request):
        try: provenance=wealth_lab._provenance()
        except wealth_lab.LabError as e: return _body(wealth_lab._failure(e.code,"",e.status),503)
        values=request.headers.getlist("content-type")
        media=re.compile(r"^[ \t]*application/json[ \t]*(?:;[ \t]*charset[ \t]*=[ \t]*utf-8[ \t]*)?$",re.I)
        if len(values)!=1 or not media.fullmatch(values[0]):
            return _body(wealth_lab._failure("CONTENT_TYPE","","INVALID_INPUT",provenance),415)
        enc=request.headers.getlist("content-encoding")
        if len(enc)>1 or (enc and enc[0].strip().lower()!="identity"):
            return _body(wealth_lab._failure("CONTENT_ENCODING","","INVALID_INPUT",provenance),415)
        chunks=[];total=0
        async for chunk in request.stream():
            total+=len(chunk)
            if total>wealth_lab.MAX_INPUT:
                return _body(wealth_lab._failure("JSON_SIZE","","INVALID_INPUT",provenance),413)
            chunks.append(chunk)
        raw=b"".join(chunks)
        value=wealth_lab.evaluate_bytes(raw)
        status=200 if value.get("artifact_version")=="RESEARCH_WEALTH_LAB_ARTIFACT_V1" else {"INPUT_INCOMPLETE":422,"INVALID_INPUT":422,"NUMERICAL_NOT_VERIFIED":503,"INTERNAL_ERROR":503}.get(value.get("status"),503)
        return _body(value,status)

    @app.get("/wealth-lab",response_class=HTMLResponse)
    async def wealth_lab_page():
        return HTMLResponse('''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/static/wealth_lab.css"></head><body><main><h1>SYNTHETIC ACCOUNTING LAB — NOT AN INVESTMENT MODEL</h1><p class="banner">Fixed 7Y / USD / nominal / pre-tax / no-flow assumptions. RISK BUDGET NOT APPROVED · NOT PRODUCTION READY.</p><p id="status">No decision, ranking, action, provider, or real-data claim is available.</p><div class="actions"><button id="example">Load synthetic example</button><button id="evaluate">Evaluate</button><button id="download" disabled>Download input + result</button></div><label for="input">Whole synthetic JSON assumptions</label><textarea id="input" spellcheck="false"></textarea><section id="structured" hidden aria-live="polite"><h2>Supplied alternatives</h2><div id="alternatives"></div><h2>Benchmark comparator — no holdings fraction</h2><div id="benchmark"></div><h2>Unavailable and unverified components</h2><div id="unavailable"></div></section><details><summary>Canonical response</summary><pre id="result" aria-live="polite"></pre></details></main><script src="/static/wealth_lab.js"></script></body></html>''')
