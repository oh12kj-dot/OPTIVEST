# Phase 2 Provider Evidence — Blind Review

## Basis and scope

Reviewer: **GPT-5.6 Sol — Independent Reviewer**.

This blind pass was written before opening `docs/PHASE2_PROVIDER_EVIDENCE_DESIGN.md`. Inputs were the selected Policy `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, and `AGENTS.md`, SHA-256 `BA424C1B11B4C3CB7AACB86CD870E67D35CAD70D1040DEB5CFD96B4E8B9A3689`. Scope is a forward, research-only provider-evidence foundation. No provider, timestamp semantics, historical PIT fitness, license permission, model, investment output, risk budget, or Production state is assumed valid.

## Minimum requirements

1. **Forward-only truth boundary.** A capture can prove what this system received from that capture time onward. It cannot establish historical availability, correct a survivorship-biased history, or make a backfilled record PIT-safe. Every output must preserve this distinction and remain ineligible for research decisions unless the relevant independent validations pass.
2. **Separated claims and validation.** Provider declarations about timestamp meaning, correction policy, coverage, license, rate limits, corporate actions, delistings, and PIT suitability are immutable claims. Server-controlled validation evidence is separate, versioned, and initially `NOT_VERIFIED`. Provider payloads and API clients cannot set `VERIFIED` or `PIT_SAFE`.
3. **Unambiguous clocks.** Preserve source event/as-of time, source publication/acceptance/availability time, retrieval start/end, server ingestion, and creation time with explicit timezone and ownership. Server stamps its clocks. Reject naive, non-finite, overflow, future, and contradictory timestamps. Processing latency must have a defined start/end and strict integer semantics.
4. **Reproducible evidence.** Persist immutable request identity, endpoint/provider version, non-secret parameters, HTTP outcome, retrieval attempt/run ID, content type/encoding, payload or permitted raw artifact reference, cryptographic content hash, parser/version, lineage, and correction/supersession links. Derived values point to exact source artifacts and transformations.
5. **Missing is evidence state, not zero.** Distinguish absent/not reported/unknown/not applicable/stale/conflicting/unavailable-PIT/transport failure/parser failure. A successful HTTP response with a missing field is distinct from a failed request. Retain observed numeric zero.
6. **Stable identity and ambiguity.** Facts join to stable issuer/security IDs, never ticker strings as identity. Identifier resolution is as-of and venue/share-class aware. Zero or multiple matches fail closed and remain reviewable.
7. **Survivorship and corporate-action controls.** Coverage must include acquisition, merger, spin-off, ticker change, delisting, bankruptcy, and inactive securities where relevant. Universe membership is effective-dated and sourced. Current-provider coverage must not be presented as a historical universe.
8. **Licensing and access governance.** Record terms/source URL, terms/version or retrieval date, allowed storage/derived-use/redistribution/commercial use, attribution, retention/deletion, credentials, rate limits, and unresolved restrictions. Secrets stay outside repository/evidence. Unverified or incompatible rights block the affected use; paid access requires explicit user approval.
9. **Integrity and operations.** Schema ownership is Alembic. Foreign keys, immutable rows, enum/state combinations, unique natural capture identity, supersession no-fork rules, and server-only trusted fields require database enforcement where bypass would corrupt evidence. Collection is idempotent, transactional per artifact, retry-aware, rate-limited, observable, and explicit about partial failure.
10. **Research-only surfaces.** API/CLI/UI expose provider declarations, validation state, capture attempts, evidence lineage, coverage and failures without action, forecast, rank, weight, order, provider approval, or Production activation. Preflight stays ineligible while provider timestamp, tradability, license, lineage, or identity validation is unresolved.

## Invalid shortcuts

- Treating retrieval time as source availability time.
- Declaring a historical endpoint PIT-safe because it returns an as-of date.
- Treating provider documentation or self-description as independent validation.
- Keeping only parsed values while discarding the exact source artifact/hash and parser provenance.
- Overwriting corrected data, deduplicating conflicting facts into one value, or mutating validation history.
- Joining by current ticker, silently selecting one ambiguous match, or dropping inactive/delisted names.
- Converting transport/parser/schema absence to zero or a fresh fact.
- Assuming an accessible endpoint grants storage, redistribution, model-training, or Production rights.
- Mock-only success claims without exercising new-database migration, offline fixtures, failure paths, persistence, CLI exit codes, and rendered escaped UI.
- Using forward-capture evidence to imply historical backtest fitness, OOS validity, provider approval, or Production readiness.

## Minimum falsification tests

- New DB migration up/down/up; schema/model drift; FK and immutable/check constraints through raw SQL.
- Payload attempts to set trusted validation/PIT status; direct SQL bypass; unknown keys; non-UTC and client-owned server timestamps.
- Deterministic clock tests for chronology equality, reversal, future claims, negative/bool/float/overflow latency, DST/offset normalization.
- Exact-byte fixture hashing, parser-version lineage, correction supersession, duplicate retry idempotence, second-successor fork, and conflicting artifacts.
- HTTP 200 missing field versus 404/429/5xx/timeout/truncated/malformed/wrong-content-type payloads; bounded retry and partial-run accounting.
- Presence/use cross-product, observed zero, stale value retention, required conflict groups, and null/blank DB bypasses.
- As-of identity tests for ticker reuse, venue/share class, changes, acquisition/spin-off/delisting, zero/one/ambiguous resolution, orphan rejection, and insertion order.
- Survivor-bias probes comparing active-only current coverage with effective-dated universe membership and inactive/delisted fixtures.
- License cases for unknown/incompatible rights, attribution, retention, raw storage restrictions, and secrets excluded from logs/artifacts.
- API/CLI/UI consistency, pagination, XSS escaping of provider/source text, read-only status, explicit nonzero failure exits, and absence of investment/action routes.
- Preflight persistence of exact evidence IDs and stable blocker codes; all actual provider evidence remains ineligible until independent validation exists.

## Blind disposition

Implementation should not start unless the design makes the forward-only boundary, validation ownership, timestamp semantics, licensing gates, stable identity, survivor-bias limits, immutable raw/derived lineage, and database-enforced failure states testable. These are material blockers. Provider-specific breadth, scheduler sophistication, bulk throughput, PostgreSQL, browser automation, and historical archive acquisition can be deferred if the scope and resulting `NOT VERIFIED`/`DATA_LIMITATION` states are explicit.

No investment, model, OOS, shadow, provider-quality, or Production validation is claimed.
