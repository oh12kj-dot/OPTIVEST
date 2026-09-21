# File map

| File | Purpose / symbols | Dependencies |
|---|---|---|
| OPTIVEST_AI_POLICY_V10.md | Sole formal Policy, §§1–18 | User selection; byte hash in START_HERE |
| OPTIVEST_AI_POLICY_COMPACT_V10.md | Historical differing input, non-authoritative | None; do not execute as instructions |
| OPTIVEST_STARTUP_PROMPT_COMPACT_V10.md | Historical prompt referencing other filename | Superseded by explicit user selection and AGENTS |
| AGENTS.md | Operational instruction entry point | Selected Policy |
| README.md | Project entry and limitations | AGENTS, START_HERE |
| .gitattributes | Preserve selected Policy bytes across Git checkout | Git |
| .gitignore | Exclude local caches/env secrets | Git |
| .ai/START_HERE.md | Current hash/branch/HEAD/status/next file | Actual filesystem and Git |
| .ai/HANDOFF.md | Exact resume and completion report | DECISIONS, tests, Git |
| .ai/DECISIONS.md | D0010 ADR registry, scopes and freeze state; ADR-0018 pins RESEARCH-WEALTH-LAB-V1 implementation scope | Policy and exact design/review evidence |
| .ai/TODO.md | Prioritized outstanding work | Decisions and validation blockers |
| .ai/TEST_STATUS.md | Commands/results and verification limits | Observed tests/reviews |
| .ai/PRODUCTION_GATE.json | Exact 25 §18 requirements and evidence status | Selected Policy; not a runtime authorization certificate |
| .ai/RESEARCH_TRIALS.jsonl | Empty append-only ledger until real trial | §17 provenance schema; never manufacture outcomes |

Current ADR-0018 checkpoint (2026-09-20): `PASS_ENGINEERING_RESEARCH_WEALTH_LAB`, controlling post-review SHA-256 `049195C11ED1690BEE629483EDFDC1BDD58FF7947868BF25F0154D52214EC279`. B6/W17 and genuine desktop/390px W18 are closed for the frozen engineering scope. Forecast/model/provider/PIT/calibration/OOS/shadow/Production remain unpromoted.
| docs/INITIAL_DESIGN.md | Proposed phases and offline checker contract | Policy; pre-review before freeze |
| docs/RESEARCH_WEALTH_LAB_DESIGN.md | Frozen revision2 RESEARCH-WEALTH-LAB-V1 contract: raw bytes, wealth/recovery/ruin, supplied diagnostics, closed failures/capabilities, artifact provenance and BASE/MAX/W1-W19; historical draft wording preserved | Selected Policy; ADR-0012 subset; exact ADR-0018 hash controls freeze; bounded implementation correction and Sol recheck pending |
| docs/reviews/research_wealth_lab_post_review.md | Independent falsification-first implementation review, correction rechecks and final genuine-browser W18 acceptance; SHA-256 049195C11ED1690BEE629483EDFDC1BDD58FF7947868BF25F0154D52214EC279 | ADR-0018 frozen design; verdict PASS_ENGINEERING_RESEARCH_WEALTH_LAB |
| docs/RESEARCH_RETURN_BRIDGE_DESIGN.md | Unfrozen RESEARCH-RETURN-BRIDGE-LAB-V1 draft: supplied synthetic FCFE-per-share bridge, hierarchical prior diagnostic, layer disagreement, closed uncertainty ledger and R1-R16 acceptance | Selected Policy, ADR-0012 research subset and accepted ADR-0018 kernel; Sol pre-review required before any freeze |
| docs/RESEARCH_RETURN_BRIDGE_DESIGN_REV2.md | Corrected revision 2: terminal FCFE-per-share identity, disjoint prior, 12-row mechanical coverage registry, tagged numerics, closed output/failure/provenance and BASE/MAX oracles | Draft-1 B1-B8; Sol independent re-review required |
| docs/reviews/research_return_bridge_pre_review.md | Sol falsification-first draft-1 review and R1-R16 disposition | Reviewed draft 6946F1...B26B; DESIGN CHANGE REQUIRED |
| optivest/wealth_lab.py | Stateless raw-byte synthetic accounting evaluator, canonical JSON, artifact/provenance and fixed capability boundaries | ADR-0018 only; no DB/provider/forecast/optimizer path |
| optivest/wealth_lab_api.py | Narrow wealth-lab HTTP and same-process HTML registration | `wealth_lab`; no database session in evaluation |
| optivest/fixtures/wealth_lab_example.json | Complete flat synthetic BASE wire fixture | ADR-0018 source manifest identity |
| docs/reviews/research_wealth_lab_pre_review.md | Sol draft-1 blockers plus controlling revision-2 exact-hash PASS, independent recalculations, B1-B6 closure, W1-W19 disposition and six freeze conditions | Corrected design and selected Policy; no implementation/model validation |
| docs/PHASE1_DESIGN.md | Draft Generic Research control plane, stable identity and PIT evidence vertical slice | Policy; ADR-0012/0013; Sol review required |
| docs/reviews/phase1_blind_review.md | Sol falsification-first Phase 1 requirements | Selected Policy and raw research-only scope |
| docs/reviews/phase1_pre_review.md | Sol corrected-design review and PASS | Frozen PHASE1_DESIGN hash in ADR-0013 |
| docs/RESEARCH_RISK_BUDGET.md | §8 provisional Balanced research values | No personalized or Production approval |
| docs/RESEARCH_RISK_EDITOR_DESIGN.md | Frozen RESEARCH-RISK-EDITOR-V1 revision 2: exact catalog/schema, normalization, diagnostics, atomic versioning, legacy transitions and verification; historical draft wording preserved | Selected Policy; ADR-0017 exact hash controls freeze |
| docs/reviews/research_risk_editor_pre_review.md | Historical first-pass eight blockers and controlling revision-2 PASS FOR SCOPED DECISION FREEZE | Reviewed design/review hashes in ADR-0017; no implementation or model validation |
| docs/reviews/research_risk_editor_post_review.md | Sol independent implementation validation through the second bounded correction; exact reproductions, migration/CAS/verifier/UI evidence and current B1-B8 disposition | ADR-0017; frozen design; retained and disposable reviewer probes |
| docs/reviews/phase0_blind_review.md | Independent Sol first pass | Raw selected Policy; scope-limited evidence |
| docs/reviews/phase0_pre_review.md | Independent Sol scoped contract review, blockers resolved | INITIAL_DESIGN hash recorded in ADR-0010 |
| docs/reviews/phase0_post_review.md | Independent Sol implementation validation, no Phase 0 blocker | Frozen design and final source/test hashes |
| scripts/verify_startup.py | Read-only Phase 0 CLI; structural status and unconditional production denial | Python stdlib, installed Git; selected Policy and governance files |
| tests/test_verify_startup.py | Isolated temporary Git fixtures and rejection/read-only checks | Python unittest, verifier CLI |
| pyproject.toml / uv.lock | Phase 1 dependencies and exact reproducible resolution | uv, Python 3.10+ |
| alembic.ini / alembic/ | SQLite Phase 1 explicit migration and reverse | SQLAlchemy metadata only for comparison; Alembic owns schema |
| optivest/db.py | Engine/session setup and SQLite foreign-key enforcement | SQLAlchemy |
| optivest/models.py | Versioned governance, risk, identity, evidence and preflight models/checks | SQLAlchemy; frozen Phase 1 schema |
| optivest/service.py | Explicit research seed, version CAS, read-only status and persistent preflight | Models and Policy hash |
| optivest/risk_editor.py | Frozen V1 raw JSON decoder, closed catalog/templates, declaration diagnostics, canonical projection and fail-closed document verifier | Models, SQLite schema, selected Policy hash |
| optivest/app.py | Strict FastAPI schemas/routes, escaped research UI and static asset mount for the isolated wealth lab | FastAPI/Pydantic/service; wealth lab route remains stateless after registration |
| optivest/static/risk_editor.js | Structured 19-row/component/Joint declaration editor, preview/save/conflict/history state and safe DOM rendering | Internal editor APIs only |
| optivest/static/risk_editor.css | Responsive desktop/mobile presentation for the structured editor | risk_editor.js DOM structure |
| optivest/cli.py | Migration, explicit seed, read-only verify and local serve commands | Alembic/app/service |
| tests/test_phase1.py | Migration, DB, API, CLI, UI and former-exploit regressions | pytest/httpx/temporary SQLite |
| docs/reviews/phase1_post_review.md | Sol final engineering validation | PHASE1-V1 frozen design and final artifact hashes |
| docs/PHASE2_PROVIDER_EVIDENCE_DESIGN.md | Frozen Phase 2 forward-only SEC/Nasdaq evidence contract and acceptance limits | ADR-0015; selected Policy |
| docs/PHASE2_LICENSE_EVIDENCE_REVIEW.md | Astra draft use-by-use SEC/Nasdaq terms disposition; no permission elevation before Sol review/freeze | Official publisher sources; ADR-0015 |
| docs/reviews/phase2_post_review.md | Sol's failed Phase 2 implementation review; remediation checklist | ADR-0015 and frozen Phase 2 design |
| docs/reviews/phase2_remediation_validation.md | Durable record of independent offline Phase 2 falsification and narrow engineering acceptance | ADR-0016; Sol rechecks |
| docs/reviews/phase2_license_evidence_independent_review.md | Sol falsification of the use-by-use SEC/Nasdaq license mapping; paired capture remains blocked | Official publisher sources; ADR-0015 |
| alembic/versions/0002_phase2.py | Single frozen-scope Phase 2 SQLite schema, append-only triggers and scoped-head constraints | Alembic; Phase 1 schema |
| alembic/versions/0003_research_risk_editor.py | Immutable V1 editor marker/document tables and SQLite triggers | Alembic; 0002 Phase 2 schema |
| tests/test_risk_editor.py | Editor template/version/history/immutability plus permanent invalid grammar, semantics, clock/currency/text/Joint and difference-direction regressions | Isolated SQLite, FastAPI TestClient |
| tests/test_risk_editor_independent_review.py | Retained independent regression cases from the first failed editor review | ADR-0017; isolated SQLite/API/CLI/UI probes |
| optivest/phase2.py | License-gated capture, versioned SEC submissions/filing-header/XBRL and Nasdaq parsers, exact trusted declarations, atomic publication, replay, transport audit, raw storage and staged-only events | Phase 2 models and raw root |
| tests/test_phase2.py | Phase 2 parser/raw-lineage, atomic publication, exact-declaration/startup, DB invariant, migration, replay, transport, API/UI and policy-gate regressions | pytest; temporary SQLite/raw roots |
| data/unverified_nasdaq_capture_2026-09-09/ | User-directed Nasdaq Trader raw files and capture manifest; quarantined outside trusted Phase 2 DB | Public endpoints; `UNVERIFIED_USER_DIRECTED_CAPTURE` |

No Production application or market-data pipeline exists. Executable scope is the local startup checker and research-only Phase 1 control plane.

## 2026-09-10 RESEARCH-RISK-EDITOR-V1 correction map

- `optivest/risk_editor.py`: closed recursive declaration validation, canonical Joint order, selected-mode diagnostics, declaration-only difference identity/direction logic, and all-history SQLite contract/chain/document verification.
- `optivest/app.py`: `/risk-budget` now exposes a complete editable raw declaration, template, preview, provisional save, history and explicit stale/reload behavior; rendering uses `textContent` for server results and retains no activation route.
- `tests/test_risk_editor.py`: permanent S1/S2 regressions for canonical Joint ordering, directional comparisons, legacy catalog tampering and a same-name no-op immutable trigger. `tests/test_risk_editor_independent_review.py` was not edited.
