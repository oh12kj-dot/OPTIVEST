# Phase 1 design — research control plane and PIT evidence foundation

Status: `DRAFT / ASTRA REVIEW REQUIRED / SOL INDEPENDENT REVIEW REQUIRED`. Date: 2026-09-08. Authority: selected `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`. This design defines a research-only vertical slice. It does not approve personalized settings or Production output.

## 1. Outcome and boundary

Phase 1 will deliver one locally runnable application that makes governance state, a provisional research Mandate/Risk Budget, stable security identity, provider metadata and PIT evidence records inspectable through a database, API, CLI and browser UI. It will implement fail-closed decision preflight but no forecast, optimizer, ranking, target weight or BUY/SELL output.

This phase cannot validate provider timestamp semantics, coverage, model calibration, OOS, shadow, or Production readiness because no external market/fundamental dataset is introduced. Those statuses remain `NOT VERIFIED`; Production remains `NOT PRODUCTION READY`.

## 2. Provisional Generic Research Mandate

This is an Astra-selected research baseline under the user's instruction to proceed autonomously. It is not personalized advice and does not constitute a Production approval.

| Field | Provisional value | Status / rationale |
|---|---|---|
| Mode | `GENERIC_DISCOVERY_RESEARCH` | No personal holdings, taxes or suitability inferred |
| Objective | Policy §1/§9 canonical robust long-term wealth utility | Reference only; no model implemented |
| Horizon | 7 years | Policy `BALANCED_RESEARCH_V1` reference |
| Base currency | USD | Coherent initial boundary for the US research universe; change requires a versioned research Mandate decision |
| Nominal / real | Nominal | Inflation remains a diagnostic input until a real-wealth mandate is approved |
| Tax | Pre-tax | No jurisdiction/account/lot assumptions available |
| External flows | None; self-financing research portfolio | Avoids inventing a contribution schedule |
| Portfolio scope | US listed-equity sleeve plus approved eligible alternatives when later verified | Does not claim global total-portfolio optimality |
| Universe | US primary-listed common equities on NYSE/Nasdaq; ETFs only as explicitly typed implementations; exclude OTC, preferreds, warrants, options and private assets | Phase 1 schema boundary; membership history and delistings required before backtest use |
| Eligible Benchmark | CRSP US Total Market Index, USD total-return definition | Provisional comparator; license/history/PIT availability `NOT VERIFIED` |
| Passive implementation candidate | Vanguard Total Stock Market ETF (`VTI`) | Candidate asset, not approved/validated; fee, tracking, liquidity, tax, look-through and tradability evidence required |
| Cash | USD cash ledger state | Not asserted risk-free; institution/credit/settlement semantics absent |
| Risk-free proxy | None approved | Must remain unavailable as an allocatable proxy |
| Reference capital | USD 1,000,000 research band | Capacity calculations still `NOT VERIFIED` until ADV/impact evidence exists |
| Production activation | Disabled | `RISK BUDGET NOT APPROVED`; no action or weight endpoint |

The Phase 1 UI may edit and version these research fields. It must preserve the `PROVISIONAL` state and must not offer a control that activates Production.

## 3. Technology decision

Use Python 3.10+ with FastAPI/Pydantic v2 for validated API contracts, SQLAlchemy 2 for persistence and Alembic for explicit migrations. Use SQLite for local development and isolated tests; PostgreSQL remains the likely later deployment store but is deliberately not selected or claimed compatible until dialect-specific constraints and migration tests exist. Serve a small semantic HTML/CSS/vanilla-JavaScript research dashboard from the same FastAPI process; a separate frontend build is not justified for this first control-plane slice.

Manage dependencies and a reproducible lock with `uv`. Production dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic`. Development dependencies: `pytest`, `httpx`. Resolve and commit exact versions in `uv.lock` at implementation time; do not guess version strings in this design. No telemetry, hosted service, external API call or data upload.

Rationale: the application needs strict request schemas, inspectable OpenAPI contracts, relational integrity and migration evidence now. A service split, React toolchain, message queue and asynchronous provider framework would add unneeded boundaries before a real workload exists.

## 4. Domain model and database invariants

All externally supplied schemas reject unknown fields. Database timestamps are timezone-aware UTC ISO instants at the API boundary. Dates and instants remain distinct.

### Governance and versioning

- `research_profiles` and `research_profile_heads`: stable profile ID plus the single current mandate/risk version IDs. Phase 1 seeds one `GENERIC_DISCOVERY_RESEARCH` profile. Head replacement is atomic and uses an expected-current version for optimistic concurrency; stale writes fail.
- `mandate_versions`: immutable UUID, profile ID, positive monotonic revision, nullable `supersedes_version_id`, mode, horizon, base currency, nominal/real, tax treatment, external-flow semantics, portfolio scope, universe version, benchmark definition, passive candidate, cash semantics, risk-free proxy, reference capital, status, effective/review timestamps, rationale, policy hash. Only `PROVISIONAL` is accepted in Phase 1. Unique `(profile_id, revision)` and unique non-null predecessor prevent duplicate revisions and forks. Creation requires predecessor = current head in the same profile and revision = predecessor + 1; the seed is revision 1 with no predecessor. These rules, the monotonic revision and immutable rows exclude cycles.
- `risk_budget_versions`: the same profile/revision/supersession/head invariants, plus immutable status/policy hash/mandate version/rationale. A new budget must reference the same profile's current mandate version. Seed `BALANCED_RESEARCH_V1` values exactly from Policy §8; unknown calibrated fields remain null with `NOT_VERIFIED` reason.
- `risk_constraints`: one row per versioned constraint with class (`STRUCTURAL_HARD`, `MODEL_ESTIMATED`, `HYBRID`, `STRESS`), metric, unit, horizon, operator, nullable limit/warning, epsilon/alpha, uncertainty/stress version, binding/diagnostic flag, calibration status and missing reason. Missing numeric values are null, never zero. Phase 1 rejects `APPROVED` and `PRODUCTION_ACTIVE` states.
- `validation_evidence`: evidence reference/status for individual readiness claims. Phase 1 accepts declarations but does not elevate them to validated truth; manual PASS cannot enable Production.

### Security master

- `issuers`: stable UUID `issuer_id`, legal name, incorporation country, lifecycle status.
- `securities`: stable UUID `security_id`, issuer ID, instrument/share-class type, primary listing venue, currency, lifecycle status. Ticker is not stored as identity.
- `security_identifiers`: identifier scheme/value, exchange/MIC where relevant, valid-from and valid-to, source evidence ID. Reject invalid intervals and overlapping active ticker intervals for the same security/scheme/venue. A ticker lookup at a date may return zero/one/multiple matches; ambiguity is an explicit failure, never arbitrary selection.
- `corporate_actions`: stable action ID, security lineage, action type, effective/tradable dates, predecessor/successor IDs, source evidence ID. It records lineage without retroactively replacing history.
- `universe_memberships`: universe version/security ID/inclusion interval/decision-available timestamp/reason/evidence ID. Delisted and excluded histories remain records.

### Provider and PIT evidence firewall

- `providers`: provider/version, authority tier, declared license/rate-limit/timestamp/corporate-action/coverage/PIT statements and their source reference. Separate server-controlled validation fields remain `NOT_VERIFIED` in Phase 1. Public API requests cannot set them to `VERIFIED`/`PIT_SAFE`; no endpoint exists to validate a provider. A later evidence-backed reviewer workflow must be separately designed. Manual declarations never satisfy preflight.
- `evidence_records`: immutable UUID, provider, source locator, subject type/ID, metric/field, value JSON or null, unit/currency/period, `as_of_date`, claimed `available_at`/`retrieved_at`, server-stamped `ingested_at`/`created_at`, observation mode, validated processing-latency seconds or null, quality confidence, `value_presence` (`PRESENT`, `MISSING`, `UNKNOWN`, `NOT_APPLICABLE`), separate `use_status` (`NOT_EVALUATED`, `FRESH`, `STALE`, `CONFLICTING`, `UNAVAILABLE_PIT`), reason, optional conflict-group ID, lineage/payload hashes, supersedes ID.
- `PRESENT` requires a value; all other presence states require null plus a reason. `STALE` preserves its present value. `CONFLICTING` preserves each candidate value as a separate record sharing a required conflict-group ID and is never averaged or selected automatically. Missing data never becomes numeric zero. Existing evidence is immutable; correction appends a same-subject/metric superseding record. Supersession uses the same unique-predecessor, same-chain and expected-current checks as governance versions to prevent forks/cycles.
- `decision_snapshots`: immutable research preflight record with snapshot ID, policy/mandate/risk versions, decision timestamp, requested tradable-at, evidence IDs and resulting blocker codes. It contains no action/weight.

Temporal ownership is fixed as follows: `as_of_date` is the economic period/date described by the fact; `available_at` is the source-publication instant claimed from source evidence; `retrieved_at` is the source retrieval instant claimed by an adapter/import; `ingested_at` is the API server's immutable receipt instant; `created_at` is the database append instant and cannot precede `ingested_at`. The client cannot supply or backdate server timestamps. All instants require explicit timezone offsets and are normalized to UTC. `LIVE_CAPTURE` strictly requires `available_at <= retrieved_at <= ingested_at <= created_at`; Phase 1 uses no clock-tolerance exception. `HISTORICAL_IMPORT` may preserve contradictory claimed source timestamps for audit, but remains ineligible and reports chronology blockers until independently validated historical observation/ingestion lineage exists. Import time never substitutes for historical availability. `processing_latency_seconds` is either null or a JSON integer `>= 0` (booleans/floats/non-finite values rejected); timestamp addition overflow is an invalid record, never a PASS.

PIT eligibility for each required record is true only when independently controlled provider timestamp/PIT validation is verified, claimed `available_at` and `retrieved_at` are validated, processing latency is validated, `decision_timestamp >= available_at + latency`, the record would have been ingested by that decision timestamp under validated live/historical lineage, and evidence is `PRESENT` + `FRESH` + non-conflicting. Phase 1 cannot create any of those independent validations, so actual preflight includes `PROVIDER_TIMESTAMP_NOT_VERIFIED` and returns `eligible_for_research_decision=false`. Tests may exercise the pure temporal predicate with trusted fixtures, but public/API data cannot manufacture a passing state. Requested `tradable_at` must be at or after the decision timestamp; Phase 1 also returns `TRADABILITY_NOT_VERIFIED` until an approved exchange-calendar/market-state source exists.

## 5. API, CLI and UI contract

API prefix `/api/v1`:

- `GET /status`: Policy/Mandate/Risk/Validation/Production statuses and blocker codes. Always `NOT PRODUCTION READY` in Phase 1.
- `GET /mandates/current`, `POST /mandates/versions`: read the profile head/create one provisional Generic Research successor. POST requires `expected_current_version_id`; stale/conflicting/forking updates fail atomically.
- `GET /risk-budgets/current`, `POST /risk-budgets/versions`: the same head/successor contract for provisional research budgets; return constraint classification and explicit null reasons.
- `GET/POST /providers`, `/issuers`, `/securities`, `/security-identifiers`, `/corporate-actions`, `/universe-memberships`, `/evidence-records`: typed research administration endpoints with pagination and stable IDs.
- `GET /securities/resolve?scheme=&value=&venue=&as_of=`: explicit zero/one/ambiguous resolution.
- `POST /decision-preflights`: evaluate evidence/PIT/tradability/governance blockers and persist the research audit record. Response contains `eligible_for_research_decision`, blocker codes and evidence diagnostics. It never emits an investment action, score or weight.
- No DELETE/UPDATE endpoint for immutable version/evidence/audit records. No Production activation or order endpoint.

CLI:

- `python -m optivest.cli db upgrade|downgrade|current`
- `python -m optivest.cli seed-research`
- `python -m optivest.cli verify-phase1`
- `python -m optivest.cli serve --host 127.0.0.1 --port 8000`

`seed-research` is idempotent by deterministic version keys and never overwrites records. `verify-phase1` reports schema/migration/current provisional state and the same Production denial; it does not certify external evidence.

UI route `/`: status banner; provisional Mandate editor; classified Risk Budget table; provider limitations; security/identifier history; evidence entry/list; decision-preflight form and blocker explanation. Every page labels Generic Research, `RISK BUDGET NOT APPROVED`, validation limitations and `NOT PRODUCTION READY`. Null/missing reasons are visible and never rendered as 0. No trade controls.

## 6. Fail-closed state machine

Phase 1 has only `PROVISIONAL_RESEARCH`. Requests containing Personalized mode, approved/active budget status, Production-ready status, action/target weight, unrecognized constraint classes, unapproved risk-free proxy, malformed timestamps, ticker-only subject identity, or mutation of immutable history return a typed 4xx error and write no partial state.

Decision preflight never becomes research-decision eligible from Phase 1 public inputs because independent provider timestamp and tradability validation paths do not exist. It reports structural and temporal diagnostics plus the expected validation blockers. It remains Production-ineligible unconditionally. `TRADABILITY_NOT_VERIFIED` is expected and does not authorize action. Transaction boundaries make compound writes and head movement atomic.

## 7. Migration, tests and operational acceptance

Implementation is accepted only with:

1. `uv sync --locked` succeeds from a clean environment and `uv.lock` exists.
2. Alembic upgrade → downgrade → upgrade succeeds on a new isolated SQLite database, with schema inspection after each step.
3. Unit tests cover enums, separated presence/use states (including retained stale/conflicting values), UTC/date validation, all five timestamp meanings, strict live chronology including equality boundaries, historical contradictory-claim retention with ineligibility, zero/negative/non-integer/non-finite/overflow latency, pure PIT latency boundary, ambiguity, interval overlap, immutable append/supersession and research-only state transitions.
4. Integration tests cover DB constraints/rollback, atomic expected-head versioning, stale write/fork/cross-profile/cycle rejection, every mutating API's invalid-state rejection, refusal of client server timestamps or verified provider statuses, idempotent seed, pagination, stable-ID joins, no ticker foreign keys and the exact Policy hash in seeded governance records.
5. API/UI tests prove no endpoint emits action/weight/Production approval, manual evidence PASS cannot unlock readiness, Missing is not 0, and all status surfaces agree.
6. Security tests cover path/HTML injection in displayed source locators, Pydantic unknown-field rejection and no secret/personal holdings persistence.
7. The local server is launched from this checkout, `/api/v1/status`, OpenAPI and `/` are fetched through HTTP, and the visible page is inspected at desktop/mobile widths.
8. Existing Phase 0 tests/checker remain PASS. `git diff --check` passes. Exact commands/results and tested hashes are recorded.

Synthetic fixtures establish implementation behavior only. Provider timestamps, CRSP/VTI licensing/coverage, real universe history, PIT reconstruction, capacity, forecast/model/risk calibration, OOS and shadow remain `NOT VERIFIED`.

## 8. Required review and freeze boundary

Sol must first falsify Phase 1 requirements from the Policy without relying on this narrative, then compare this design. Blocking findings are corrected before Astra freezes a version/hash. Freeze will cover the provisional Mandate, schema/state machine, API/CLI/UI contract and acceptance tests. It will not approve the Mandate/Risk Budget for Production, select a market-data provider, or freeze forecast/optimizer semantics.

After Terra implementation, Sol independently reviews migration round-trip, failure paths, code/schema/design agreement and actual HTTP/UI evidence. Material semantic changes reopen review.

## 9. Known limitations and deferred decisions

- Benchmark/passive candidate licensing, total-return history, timestamp semantics and look-through are `NOT VERIFIED`; neither may support a decision yet.
- SQLite cannot establish later PostgreSQL behavior; production database and deployment are undecided.
- Identifier overlap protection may combine database uniqueness with transactional service checks in SQLite; concurrency guarantees need later PostgreSQL validation.
- No independent provider validation workflow, exchange calendar or market-state source means research-decision PIT/tradability eligibility cannot pass in Phase 1; this is intentional fail-closed behavior.
- No personal suitability/tax/cash-flow data; Personalized mode is rejected.
- No return/risk model, `U_objective`, calibrated `U_risk`, `S_stress`, solver, ranking, action, OOS or shadow.
- No automatic external data collection in Phase 1. Provider adapters require a separately reviewed data contract and licensing evidence.

Design deviations from selected Policy: `NONE`. Deliberate incomplete scope is surfaced through blockers rather than represented as completion.
