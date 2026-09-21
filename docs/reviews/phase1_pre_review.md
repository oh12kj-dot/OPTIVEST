# Phase 1 Research Control Plane / PIT Foundation — Pre-Implementation Review

## Verdict

**PASS FOR PHASE 1 IMPLEMENTATION.** The proposed scope and technology choice are suitable for a research-only vertical slice, and the design correctly denies Production, forecast, optimizer, ranking, weight, action, and order output. The four foundation blockers found in the first comparison and the final temporal-invariant gap were corrected in the reviewed revision bound below. This approval is limited to the Phase 1 implementation contract.

Reviewer: **GPT-5.6 Sol — Independent Reviewer / Validator**. This is a pre-implementation design review only. It does not approve the provisional Mandate or Risk Budget, validate providers/PIT data, or establish model/OOS/shadow/production readiness.

## Evidence reviewed

- Full selected `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- Blind review completed before design exposure: `docs/reviews/phase1_blind_review.md`, SHA-256 `90D3634ADF309546BFE6AD8E7B6803DF36B8B5E3DB0E8D27D3C9A63627DA2953`
- Initial reviewed `docs/PHASE1_DESIGN.md`: SHA-256 `A6B47DC460E1F109386918C5CAB0FFAD7EA9DA9B15758EE737AD74C7034EB1EB`
- Final corrected `docs/PHASE1_DESIGN.md`: SHA-256 `C23222188016A4A164C0DBB3434D9B8CA768C91CC3B826523744E47C9FF4CD68`
- `AGENTS.md`, SHA-256 `E362DDF9B4BB6D0E7F7F635EF9701BEE6A732CEEC002B9167DCA6D26CB6C1598`
- `.ai/DECISIONS.md` D0004, including ADR-0012 and ADR-0013, SHA-256 `9EC70110CDEEA316B5BA5E52AA869B9878AC04EF09B702552914D2206FDDBAC3`

ADR-0012 is correctly recorded as `PROPOSED / NOT APPROVED / REVIEW REQUIRED`; ADR-0013 is `DRAFT / NOT FROZEN`. The user's direction to choose and proceed supports reversible research defaults only and does not authorize personalized or Production risk activation.

## Design elements that withstand falsification

- The 7-year/USD/nominal/pre-tax/self-financing baseline is explicitly provisional and Generic Research. Unknown personal inputs are not invented.
- CRSP US Total Market Index is modeled as a comparator, while VTI is a separate candidate security with unverified fee/tracking/liquidity/tax/look-through/tradability evidence. No benchmark weight is proposed.
- Cash is not called risk-free, and no risk-free proxy is approved.
- The selected stack—Python 3.10+, FastAPI/Pydantic v2, SQLAlchemy 2, Alembic, SQLite local/test, same-process semantic HTML/JavaScript UI, and `uv` lock—is proportionate to the Phase 1 contract. PostgreSQL behavior is expressly unclaimed.
- Stable issuer/security UUIDs replace ticker identity; identifier intervals, ambiguity, corporate-action lineage, universe history, and delistings are represented.
- Missing numeric data remains null, explicit evidence states exist, and no single confidence score or investment output is introduced.
- API, CLI, UI, migration, clean-database, HTTP, OpenAPI, responsive-browser, and Phase 0 regression acceptance are included.
- Mutations that request personalized, approved/active, Production, action, weight, or ticker-only semantics are fail-closed and atomic.

## Resolved blocking findings

### B1 — Version creation has no frozen lineage/current-selection invariant — RESOLVED

The initial design created mandate/risk versions and exposed `/current`, but did not define a predecessor/supersession field or how one current version was selected. Timestamps and deterministic seed keys would not prevent forks, cycles, two active successors, or ambiguous “latest” ordering. An implementer would have had to invent the state machine.

Required correction:

- Add immutable `supersedes_version_id` (nullable only for a root), same-entity/profile chain identity, creation sequence or other deterministic ordering, and explicit current/superseded state.
- Define `/current` as the unique unsuperseded leaf for the requested research scope. It must not mean maximum timestamp or lexical version ID.
- Reject self-supersession, cycles, cross-chain/type supersession, a second successor to the same current leaf, broken predecessors, and stale-base writes. Use a transaction and return a typed conflict.
- Seed idempotence must resolve the exact deterministic root/version and never silently replace or fork it.
- Approval/validation fields are not inherited. Every created successor remains `PROVISIONAL / RISK BUDGET NOT APPROVED`.
- Apply an equivalent explicit version/supersession rule to provider metadata if provider corrections are represented as versions.

Acceptance must include two concurrent/stale attempts to supersede the same current version, deterministic `/current`, complete history retrieval, and proof that referenced historical decision snapshots still resolve their original versions.

### B2 — Evidence state destroys stale and conflicting observations — RESOLVED

The initial design put `OBSERVED`, `MISSING`, `UNKNOWN`, `NOT_APPLICABLE`, `STALE`, `CONFLICTING`, and `UNAVAILABLE_PIT` in one enum, then required null value for every state except `OBSERVED`. A stale observation still has an observed source value, and a conflict consists of two or more observed candidate facts. That rule would have discarded raw evidence and prevented audit/reconstruction.

Required correction:

- Separate value presence from decision eligibility/quality. One workable contract is:
  - `value_state`: `OBSERVED`, `MISSING`, `UNKNOWN`, `NOT_APPLICABLE`;
  - `eligibility_state`: `ELIGIBLE`, `STALE`, `CONFLICTING`, `UNAVAILABLE_PIT`, `NOT_VERIFIED`.
- `MISSING`, `UNKNOWN`, and `NOT_APPLICABLE` require null value and an explicit reason. `OBSERVED` requires a value, even when the separate eligibility state is stale/conflicting/unavailable-PIT.
- Conflicting observations retain each candidate value/source and share an immutable conflict-group or explicit relation. Resolution appends evidence; it never rewrites or deletes candidates.
- A stale/unavailable/conflicting observation always fails PIT eligibility while remaining queryable and visible through API/CLI/UI.

Acceptance must round-trip a legitimate numeric zero as observed, a stale nonzero value, two conflicting values, missing, unknown, not-applicable, and a currently known value unavailable at an earlier decision time. Only the legitimate observed zero may serialize as numeric zero.

### B3 — A manual provider write can manufacture “verified” PIT eligibility — RESOLVED

The initial design correctly said Phase 1 could not validate provider timestamp semantics, coverage, licensing, or PIT suitability, but it exposed provider writes without separating declarations from trusted validation. A client could have submitted `VERIFIED`/PIT-suitable metadata and obtained an eligibility result that appeared evidence-grounded.

Required correction:

- Separate provider declarations from validated status and provenance, for example `declared_*` fields plus reviewer-controlled `validation_status`, `validated_by/ref`, and validation version.
- In Phase 1, external provider semantic validation remains unavailable. Public/API research-administration writes must reject `VERIFIED`, `PIT_SAFE`, approved-license, or equivalent authoritative states, or store them only as untrusted declarations that preflight never treats as validated.
- Manual `validation_evidence PASS`, a nonempty evidence reference, or successful POST cannot elevate provider/PIT status.
- PIT preflight must require independently validated provider semantics; with the Phase 1 evidence available here, that check remains `NOT VERIFIED` and fail-closed. Structural record validity may be reported separately from PIT eligibility.

Acceptance must attempt to self-assert every trusted provider/PIT status through the API, CLI, seed, and direct service path and prove that no request becomes PIT-eligible or Production-capable.

### B4 — Timestamp ownership and eligibility clocks are underspecified — RESOLVED

The initial design named `as_of_date`, `available_at`, `retrieved_at`, observed ingestion time, created time, processing latency, decision time, and requested tradable time, but did not define which actor supplied each value, which were server-stamped, or how live capture differed from historical reconstruction. “Timezone-aware UTC at the API boundary” alone would not prevent backdating or substitution of collection time for source availability.

Required correction:

- Define `as_of_date` as the economic/reporting observation date or period, not publication or ingestion time.
- Define `available_at` as the source-publication instant supported by source evidence; unknown remains null/unverified.
- Define `retrieved_at` as the collector retrieval instant and `ingested_at`/created time as server-controlled persistence instants. Client input cannot set server-owned timestamps.
- Define verified processing latency as a versioned provider/pipeline fact, not the elapsed time inferred from one row.
- State the ordering checks appropriate to direct capture, and state explicitly whether retrieved/ingested timestamps are provenance-only or eligibility clocks for historical reconstruction. If both live and replay modes are intended later, store the mode and give each a separate rule; Phase 1 must not guess.
- Preserve the canonical condition `decision_timestamp >= available_at + verified latency`; require `tradable_at >= decision_timestamp`. Unknown timestamp semantics, precision/timezone, latency, or relevant clock relation yields a stable blocker.
- Define timestamp precision, inclusive boundary behavior, UTC normalization, and overflow/negative-latency rejection.

Acceptance must test source timezones/DST conversion, equal-boundary eligibility, one-unit-before failure, negative/overflow latency, client attempts to backdate server timestamps, retrieval before availability, ingestion before retrieval where the capture rule applies, and unavailable historical publication time.

## Nonblocking limitations and deferred work

The following are properly deferred and do not block the corrected Phase 1 design:

- Researching or validating CRSP, VTI, or any provider's licensing, timestamps, coverage, corporate actions, or PIT history.
- Selecting PostgreSQL or claiming SQLite/PostgreSQL parity. SQLite overlap/concurrency limitations are already disclosed and must remain in acceptance results.
- Defining a full exchange calendar, halt/auction state, or executable tradability source. `TRADABILITY_NOT_VERIFIED` is appropriate.
- Automatic external collection/provider adapters.
- Forecast distributions, economic/statistical return models, uncertainty sets, risk calibration, solver, ranking, weights, actions, orders, OOS, shadow, or deployment.
- Personalized mandate/tax/cash-flow/suitability handling and Production activation.
- Proving economic correctness from synthetic fixtures. Phase 1 tests may validate contracts only.

The design's security model is adequate for the bounded US-primary-listing research slice if unknown ADR/underlying, alternate-listing, and complex lineage cases remain explicit limitations. A later broader universe may require first-class listing and security-relationship tables; that expansion need not be added to Phase 1 unless the implementation claims those cases are resolved.

## Delta resolution and review gate

The final design revision resolves the findings as follows:

- B1: `research_profile_heads`, monotonic same-profile revisions, unique predecessor, expected-current optimistic concurrency, atomic head movement, and stale/fork/cross-profile/cycle tests define deterministic current versions while preserving immutable history.
- B2: value presence is separated from use status. Stale, conflicting, and unavailable-PIT observations retain source values; conflict groups preserve all candidates without automatic averaging or selection.
- B3: provider declarations are separate from server-controlled validation. Phase 1 exposes no provider-validation path, rejects trusted-state writes, and actual preflight remains ineligible with explicit provider/timestamp/tradability blockers.
- B4: all five timestamps have fixed ownership and meanings. Live capture requires strict `available_at <= retrieved_at <= ingested_at <= created_at`; historical contradictions remain auditable but ineligible. Latency is null or an exact nonnegative JSON integer, with boolean/float/non-finite/overflow cases rejected and required in tests.

No blocker remains in the Phase 1 design contract. Astra may bind `C23222188016A4A164C0DBB3434D9B8CA768C91CC3B826523744E47C9FF4CD68` in a scoped freeze and authorize Terra to implement that exact scope. ADR-0012 must remain provisional/not approved, and the implementation must preserve unconditional `NOT PRODUCTION READY` plus the absence of forecast/ranking/action/order paths.

Post-implementation Sol review remains required for code/schema/design agreement, migration round trip, immutable-version failure paths, status and missingness round trips, actual shared API/CLI/UI behavior, and real HTTP/browser evidence. This verdict is not `MODEL VALIDATION PASSED`; no investment model exists in scope.
