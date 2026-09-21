# Phase 1 Research Control Plane / PIT Foundation — Blind Review

## Review identity and evidence boundary

- Reviewer: **GPT-5.6 Sol — Independent Reviewer / Validator**
- Method: blind, falsification-first first pass
- Authority: fully read selected `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- Raw scope supplied for this pass: research-only Generic mandate/risk versioning, stable security identity, provider/PIT evidence, preflight, DB/API/CLI/UI
- Explicit exclusions: forecast, optimizer, ranking, investment action, order, deployment, personalized production activation, and production-readiness validation
- Phase 1 design exposure at time of writing: **none**

This document defines the minimum contract and adversarial acceptance evidence that a later Phase 1 design must satisfy. It does not approve a mandate, risk budget, provider, security universe, model, recommendation, or production use.

## Blind conclusion

Phase 1 may create a useful research control plane without investment logic, but only if every stored value carries a clear authority and lifecycle. The central failure mode is semantic promotion: provisional defaults, incomplete provider metadata, or merely well-formed PIT records can be mistaken for an approved mandate, trusted evidence, or permission to produce an action.

The foundation should therefore preserve explicit unknowns, append new versions instead of rewriting history, separate comparator definitions from investable instruments, and fail preflight when required temporal or lineage facts are absent. A passing Phase 1 preflight can mean only “this research request has the required structural evidence.” It cannot mean that the evidence is economically correct, the provider is PIT-safe in practice, the risk budget is calibrated, or an investment should be made.

## Minimum policy requirements

### 1. Research-only authority and states

- Every mandate and risk-budget version must carry an immutable ID/version, status, effective/as-of metadata, creation provenance, and supersession relation where applicable.
- Initial values must remain visibly `PROVISIONAL`, `NOT VERIFIED`, and/or `RISK BUDGET NOT APPROVED`. A default, template, saved record, API success, or UI selection cannot create approval.
- Generic research must remain distinct from personalized portfolio use. No age, holdings, tax context, or investor suitability is inferred.
- The required Mandate fields must be represented separately: investment horizon, base currency, nominal/real treatment, pre-/after-tax treatment, external contribution/withdrawal assumption, Eligible Benchmark definition, and approved Passive Market Implementation candidate(s). Unknown fields remain unknown rather than receiving convenient defaults.
- User direction to choose reversible research defaults authorizes provisional research configuration only. It does not authorize §4 production risk activation or a personalized numerical risk budget.
- All Phase 1 responses and screens must retain `NOT PRODUCTION READY`; no endpoint, CLI command, UI control, or persistence transition may emit or imply an investment action.

### 2. Benchmark and investable implementation separation

- An Eligible Benchmark is a comparator definition and never receives a portfolio weight.
- VTI, another ETF, fund, or replicating basket is a candidate Passive Market Implementation with its own security/listing identity, fees, liquidity, tracking, tax, currency, tradability, and look-through limitations. It cannot silently become the benchmark itself.
- A broad-market label is insufficient. Store the benchmark definition/version separately from the implementation security ID and effective relationship.
- Cash and a risk-free proxy remain separate concepts. Phase 1 may represent candidates and unknowns, but it must not infer a risk-free instrument or approved allocation.

### 3. Stable security identity

- `internal_security_id` and `issuer_id` must be stable identifiers independent of a current ticker string.
- Listing, exchange, currency, security type, share class, ADR/underlying relation, and identifier/ticker history need effective dates and provenance where applicable.
- Ticker reuse, ticker changes, multiple listings, share classes, mergers, spin-offs, and delistings must not merge unrelated securities or sever lineage.
- A provider symbol is an alias scoped to provider/listing/time, not the primary security identity.
- Unknown issuer or lineage relationships remain explicit limitations; they must not be guessed from name similarity.

### 4. Provider and evidence registry

- Provider records must represent source class/authority, license or terms status, rate-limit information, coverage, timestamp semantics, corporate-action behavior, PIT suitability, retrieval method/version, and current verification status.
- “Official,” “free,” or a provider name is not proof of PIT suitability. Unknown semantics remain `NOT VERIFIED` or `DATA_LIMITATION`.
- Evidence must distinguish a source fact from an inference. Unsupported LLM output cannot be stored as a verified fact or become a future weight/action input.
- Lineage must bind a data observation to provider/source, retrieval event, transformation/version, and original/raw snapshot reference or immutable digest where feasible.
- Derived values must preserve references to verified inputs and transformation provenance; provenance cannot be replaced by a human-readable note alone.

### 5. PIT and temporal semantics

- At minimum preserve `as_of_date`, `available_at`, `retrieved_at` where relevant, source, staleness, quality/confidence, and lineage. Decision-oriented preflight must also carry `decision_timestamp` and `tradable_at` where those concepts apply.
- Each timestamp/date needs an explicit definition, timezone/calendar convention where relevant, source, and precision. Filing period end, publication time, ingestion time, decision time, and first tradable time are different fields.
- PIT ordering must be enforced: a decision cannot use evidence before its verified availability plus required ingestion/processing latency, and a price cannot be selected before `tradable_at`.
- Unknown provider timestamps or unverified latency cannot be replaced by retrieval time, period end, midnight, prior close, or current time. Such evidence is not PIT-eligible for a required preflight.
- Restated values must not overwrite the vintage that was available at an earlier decision time. Corrections create a new version linked to the superseded observation.
- Corporate-action and identifier histories must use the same PIT discipline; present-day identities or constituents cannot be backfilled as if known earlier.

### 6. Missingness and quality

- Missing is never numeric zero, empty-string success, false, or a negative score.
- Represent at least `Missing`, `Unknown`, `Not Applicable`, `Stale`, `Conflicting`, and `Unavailable Point-in-Time` distinctly, with reason and observed/effective time where appropriate.
- Database nullability, API schemas, CLI rendering, UI labels, and preflight rules must preserve the same states. Serialization must not collapse them.
- A required field with conflicting, stale, unavailable-PIT, or unknown evidence must fail or remain ineligible according to an explicit preflight rule. Optional absence must remain visible and cannot improve quality/confidence.
- Confidence dimensions must not be invented or compressed into one score during this phase.

### 7. Immutability and supersession

- Mandate, risk-budget, provider-policy, security-identity, and evidence records used by a research run need stable version references.
- Material edits create a new version and a supersession link. Historical versions remain queryable and cannot be silently updated to current values.
- There must be at most one active successor for a version chain under the defined scope/as-of semantics; cycles, self-supersession, duplicate active versions, and broken parents fail.
- Deletion of referenced versions/evidence must be restricted or fail. A UI “edit” should create a new provisional version, not mutate historical inputs.
- Approval fields must not be copied forward automatically. A superseding research version remains provisional unless separately approved under a later authorized process.

### 8. Preflight contract

- Preflight is a deterministic structural/data-eligibility assessment, with stable reason codes and all failures returned where practical.
- It must check version existence/status, required Mandate fields, provisional risk status, benchmark/implementation separation, security identity, provider status, evidence availability/freshness/lineage, and PIT ordering applicable to the request.
- Preflight must be evaluated server-side through one canonical service used by API, CLI, and UI. Client-only checks are insufficient.
- A successful research preflight may authorize downstream research collection or inspection only. It cannot emit forecast, rank, weight, `BUY`, `ACCUMULATE`, `HOLD`, `TRIM`, `SELL`, `AVOID`, or `NO_TRADE` as an investment conclusion.
- The result must include scope, version IDs, as-of/decision time, pass/fail, reason codes, missingness/limitation details, and the explicit production denial.
- Unknown checks fail closed for the affected eligibility claim. The system must not rename `NOT VERIFIED` to warning-only success.

### 9. DB, API, CLI, and UI consistency

- Database constraints should enforce stable identity uniqueness, version/supersession integrity, status allowlists, temporal rules that are locally decidable, and referential integrity.
- Migrations must succeed from an empty database and preserve schema/data over the supported upgrade path. Re-running initialization must not duplicate seed/reference records or change immutable versions.
- API request/response schemas must expose IDs, versions, statuses, missingness reasons, timestamps, lineage, and explicit research-only/readiness semantics.
- CLI and UI must call the same service/API path and display the same current version, status, preflight failures, and supersession history. UI completion without persistence/API behavior is not acceptance.
- Write endpoints require validation and conflict handling. Stale-version edits must not overwrite a newer version; return an explicit conflict.
- No Phase 1 surface may contain a hidden forecast/rank/action fallback or transform missing numeric inputs to zero.

## Invalid shortcuts to reject

- Marking a research preset `APPROVED`, `ACTIVE FOR PRODUCTION`, personalized, optimal, or suitable because it was selected by the user for research.
- Filling missing Mandate inputs from policy examples, environment locale, holdings, age, IP location, or another project.
- Using VTI as both the Eligible Benchmark definition and investable implementation record.
- Storing ticker as the security primary key or using one provider symbol as universal identity.
- Treating provider retrieval success, HTTPS, an official label, or current data as proof of historical PIT availability.
- Setting `available_at = retrieved_at`, `tradable_at = decision_timestamp`, or period end = publication time without verified semantics.
- Overwriting restated fundamentals, corrected evidence, ticker history, provider metadata, mandate versions, or risk versions in place.
- Encoding missing values as `0`, empty string, `false`, an empty object, or a low score.
- Letting the frontend declare preflight PASS when the server has not evaluated the same versioned inputs.
- Using a database seed or migration to create approval provenance.
- Returning HTTP 200 with an embedded failure that CLI/UI then treats as success, or swallowing provider/data errors into a healthy status.
- Adding forecast, optimizer, ranking, portfolio weights, action labels, order paths, or production enablement “for future compatibility.”
- Claiming provider, PIT, model, or investment validation from schema/unit tests alone.

## Minimum acceptance tests

### Persistence and migrations

1. Create a clean isolated database and apply all migrations from zero; inspect required tables, constraints, indexes, and foreign keys.
2. Exercise the supported migration round trip or documented forward-only boundary, then reapply and confirm records/constraints are preserved.
3. Run initialization twice and prove reference seeds are deterministic and nonduplicating.
4. Attempt in-place modification/deletion of referenced historical versions and confirm rejection or explicit superseding-version behavior.
5. Reject duplicate active versions, supersession cycles, self-links, broken parents, invalid status values, and identity-key collisions.

### Mandate and risk controls

6. Save a provisional Generic research mandate with unknown required fields and prove no approval or production state is created.
7. Exercise every required Mandate field as missing and confirm a stable preflight reason.
8. Attempt to activate a research risk preset for production and confirm fail-closed rejection without an authorized approval path.
9. Create separate benchmark and VTI implementation records; prove the benchmark has no security weight/identity and the implementation carries a security ID and its own evidence/limitations.
10. Supersede a mandate/risk version and confirm history is immutable, current selection changes explicitly, and approval is not inherited.

### Identity and PIT evidence

11. Change a ticker across effective dates and prove one stable security ID remains while point-in-time alias resolution returns the correct ticker.
12. Reuse the old ticker for another issuer/listing and prove identities do not merge.
13. Exercise multiple listings/share classes/ADR linkage, unknown lineage, delisting, and corporate-action boundaries without guessing relationships.
14. Test `available_at` after decision, insufficient latency, tradable time before availability, stale evidence, conflicting evidence, missing timezone/precision, and unavailable historical vintage; each must fail with the correct reason.
15. Add a restatement and prove an earlier as-of query still returns the prior available vintage.
16. Verify derived evidence cannot be eligible without source-input lineage and transformation version.
17. Verify every missingness state survives DB → API → CLI/UI round trip and none becomes numeric zero.

### Shared service and surfaces

18. Compare the same preflight request through service, API, and CLI; results, version IDs, reason codes, and readiness denial must agree.
19. Render each status/missingness/conflict in the UI from actual API responses; editing creates a new version and stale concurrent edits conflict.
20. Search API/OpenAPI/CLI/UI routes and responses for excluded forecast/ranking/action/order/production activation surfaces; none may exist in Phase 1.
21. Confirm malformed input, unavailable DB, and internal exceptions fail explicitly and do not return a healthy preflight.
22. Run type/lint/unit/integration/API/DB/UI build checks appropriate to the selected stack, plus a real process smoke test against a freshly migrated isolated database.

## Material design blockers to look for

A later Phase 1 design is not ready for implementation if it lacks any of the following:

1. explicit research-only state machine and immutable version/supersession semantics;
2. complete provisional Mandate fields without inferred answers;
3. a distinct benchmark definition and investable implementation model;
4. stable issuer/security/listing/provider-alias identity with temporal lineage;
5. precise timestamp meanings and PIT eligibility rules;
6. an explicit missingness/status vocabulary preserved across every layer;
7. a canonical server-side preflight with stable reason codes and fail-closed behavior;
8. database constraints/migration acceptance and shared API/CLI/UI call paths;
9. an explicit prohibition on forecast/ranking/action/order/production output; or
10. evidence that defaults and test fixtures cannot manufacture approval.

Provider selection, data licensing conclusions, security-universe breadth, calibrated risk semantics, forecasts, portfolio construction, OOS/shadow validation, and production activation may remain deferred. The design must name them as limitations rather than fill them with assumptions.
