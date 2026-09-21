# Phase 2 remediation validation record

Date: 2026-09-09 (Asia/Tokyo). Reviewer role: GPT-5.6 Sol, independent falsification-first rechecks. Recorder: parent Astra from the reviewer outputs and parent reproductions. Authority: ADR-0015 and `docs/PHASE2_PROVIDER_EVIDENCE_DESIGN.md`.

## Verdict

`PASS_ENGINEERING_P2_OFFLINE` for the implemented offline/fixture/SQLite forward-capture contract. This is narrower than full Phase 2 implementation acceptance because frozen design section 7 item 11, the bounded official SEC/Nasdaq capture and offline replay from those official bytes, remains `BLOCKED_POLICY / NOT VERIFIED` while required license uses are `NOT_VERIFIED`.

Do not infer provider/license/timestamp/PIT validation, historical-universe completeness, investment-model validity, Locked OOS, shadow validation or Production readiness.

## Independent falsification and closure

The first post-implementation review reproduced P0-1 through P0-6 and P1-1 through P1-3 failures. Successive independent rechecks used fresh temporary SQLite databases, raw-SQL bypass probes, loopback HTTP servers and API/CLI/UI checks. Final closure evidence covered:

- explicit common-equity evidence and fail-closed Nasdaq classification;
- separate research-only SEC filing-header/XBRL evidence parsers with raw lineage, while submissions truthfully record that XBRL is absent from that payload;
- a single publication timestamp shared by snapshot, staged events, terminal run, run result and scoped head;
- all required capture/replay/display license-use and retention-duty gates;
- HTTP status, redirect-limit, sanitized destination and RFC-date `Retry-After` audit;
- terminal-state, immutable object, complete-head, scoped-CAS and review-chain database constraints;
- exact parser artifact/version replay without fixture bypass;
- exact frozen provider, license, dataset, rate-policy and seven-use permission/duty declarations shared by seed, verifier and app startup.

The last independent forgery probe changed the SEC provider `authority_tier` to `FAKE_TIER`; `verify_phase2()` returned `seed_state=false` and application startup rejected the database. Targeted declaration tests passed 7/7.

## Reproduced verification

- Parent: `uv run pytest -q` -> 70 passed, 2 skipped, 2 upstream dependency warnings.
- Parent: Python compile, `git diff --check` and `uv run python scripts/verify_startup.py --root .` -> PASS; startup findings empty; `main` / `UNBORN`; Production denied.
- Terra: fresh SQLite `upgrade head -> downgrade 0001_phase1 -> upgrade head -> seed -> verify` -> exact `0002_phase2`, `seed_state=true`, `raw_integrity=true`.
- Sol: final targeted declaration mutation suite -> 7 passed; full suite -> 70 passed, 2 skipped, 2 warnings.
- Policy SHA-256 remained `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.

The two skips are Windows host-denied symlink fixtures and do not establish link-escape coverage. No live provider request, permission elevation, paid access, Production activation or investment output occurred.

