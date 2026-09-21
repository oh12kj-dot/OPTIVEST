# Phase 2 Provider Evidence — Final Comparative Pre-Implementation Review

## Verdict

**PASS — the corrected PHASE2-V1 design is suitable for decision freeze and implementation within the exact boundary below.**

Reviewer: **GPT-5.6 Sol — Independent Reviewer**.

Reviewed design: `docs/PHASE2_PROVIDER_EVIDENCE_DESIGN.md`, SHA-256 `9632BC6BBB2F6631CACFAF5BE587BE6083DA4A063FCE1C624F40BF4393E880EE`.

Authority and comparison inputs:

- Selected Policy: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- `AGENTS.md`: `BA424C1B11B4C3CB7AACB86CD870E67D35CAD70D1040DEB5CFD96B4E8B9A3689`
- Frozen Phase 1 design: `C23222188016A4A164C0DBB3434D9B8CA768C91CC3B826523744E47C9FF4CD68`
- Current Phase 1 models: `C3A1E40534541B999E9191DCF555B605D7B51A13AF1B9A65A631E7F5ED8945E7`
- Current Phase 1 migration: `7441EE6FF6B38353C3F943CF68C03C49AE8E6010A52053655810EC5C6A042AD8`
- Blind review: `docs/reviews/phase2_blind_review.md`, SHA-256 `2094DBC28BA983D9CC38B762B65CB28E08A0C05F808041F587CB5FFD7D67959D`

This supersedes the FAIL disposition against design hash `3027B3C123AD01B55253A3213046B78873F1B4094CC601038516B4A9B57726C5`.

## Correction disposition

| Finding | Disposition | Corrected contract |
|---|---|---|
| B1 scoped SEC identity/heads | **Closed** | Immutable normalized capture scopes; CIK-specific keys; request fingerprint separate from content; head/CAS/idempotence keyed by dataset version plus scope. |
| B2 paired logical snapshot/raw identity | **Closed** | Content-addressed raw objects, ordered named parts, canonical manifest hash, deterministic canonical row JSON, explicit decoding/newline rules, and preserved failed bodies. |
| B3 immutable forward membership | **Closed** | Staged append-only membership events; `observed_at=max(part response_completed_at)`; later `usable_at`; no Phase 1 interval mutation or backdating. |
| B4 unresolved/authoritative identity | **Closed** | Collection creates only `source_security_candidate_id`; unresolved candidates remain outside authoritative Phase 1 tables; reviewed identity is an immutable expected-current chain; projection is deferred and blocked without one compatible reviewed mapping. |
| B5 reproducible license permission | **Closed** | Exact reviewed terms artifact/hash and provenance; per-use `ALLOWED/BLOCKED/NOT_VERIFIED` matrix and duties; affected operations fail with `BLOCKED_POLICY`; adapters cannot approve. |
| B6 raw-object path safety | **Closed** | Hash-derived keys only, root/parent resolution, traversal/case/link/reparse rejection, same-root temporary write, length/hash validation and atomic rename, with replay revalidation. |

The stale B4 sentence was corrected: line 94 now explicitly prohibits collection from creating an authoritative Phase 1 `security_id` or merging by ticker. No new material blocker was found in the corrected delta.

## Acceptance matrix disposition

The corrected design now requires all previously requested falsification coverage:

- Raw-SQL lifecycle, trusted-state, immutability, null/blank/hash/chronology, scoped-head and identity-review CAS tests.
- Alternating CIK streams and equal bytes across distinct request scopes.
- Missing/duplicate/swapped Nasdaq parts, deterministic manifest/row hashes, replay/tamper and failed-body non-promotion.
- Append-only add/present/possible-removal/reappearance events with late-validation and no-backdating checks.
- Zero/multiple/incompatible/unreviewed identity exclusion from authoritative tables.
- License-use matrix, attribution/retention and raw-download denial tests.
- Absolute/traversing/case/partial/tampered/symlink/junction/reparse object-path tests, with honest OS-denied skips.
- Environment-only SEC contact, shared monotonic HTTP-boundary limiter, bounded Retry-After/backoff and deterministic test jitter.
- API/CLI/UI consistency, escaped source text, nonzero CLI failures, no browser collection and no investment routes.
- Fresh migration round trip, bounded live official captures, exact stored evidence, offline replay and independent post-validation.

Passing fixtures alone cannot replace the required bounded live captures. A network/provider failure remains a failed acceptance item.

## Exact freeze boundary

ADR-0015 may freeze only the following under design hash `9632BC6BBB2F6631CACFAF5BE587BE6083DA4A063FCE1C624F40BF4393E880EE`:

1. One Phase 2 Alembic migration for the new license evidence/permissions, dataset versions, capture scopes, ingestion runs, raw objects, logical snapshots/parts/rows, scoped heads, source-security candidates, staged membership events, and identity-review revision/head tables and constraints.
2. Research-only adapters for SEC submissions/filing/XBRL evidence capture and the paired Nasdaq Trader current-directory capture, using the frozen forward-only and timestamp semantics.
3. Content-addressed local raw storage, deterministic parser/replay services, scoped head advancement, staged universe-event generation, and unresolved identity-review records.
4. CLI commands `collect-sec-submissions`, `collect-nasdaq-directory`, `replay-snapshot`, and read-only `verify-phase2`.
5. Read-only paginated metadata API and Data Evidence UI; no raw-byte download, network-triggering browser route, validation/approval control, projection, investment output or Production activation.
6. The complete Section 7 acceptance suite, Phase 0/1 regression, bounded live captures, offline replay, and independent Sol post-implementation validation.
7. Exact source URLs, dataset/endpoint/parser semantic versions, rate policy, license-evidence versions and implementation/test file scope recorded in ADR-0015 before Terra starts.

The freeze excludes authoritative projection into Phase 1 issuer/security/identifier/membership tables; historical universe reconstruction; delisting returns; prices/returns; exchange calendar/tradability; liquidity/capacity; benchmark/VTI validation; fundamentals projection; forecast; uncertainty sets; risk-model calibration; optimizer; ranking; actions/orders; paid sources/accounts; credentials; deployment; and Production activation. Any change to universe inclusion, identity resolution, availability clocks, license status, projection eligibility or historical claims requires unfreeze and renewed review.

## Limits and statuses

This review did not browse or independently establish the external provider capability, terms, rate-limit, licensing, timestamp or coverage claims in the design. Those remain versioned inputs that implementation and live acceptance must evidence. No implementation, live network capture, provider account, paid source, credential, model, investment, OOS, shadow, trading or Production validation occurred.

- Phase 2 design: **PRE-IMPLEMENTATION REVIEW PASSED / ELIGIBLE FOR ADR-0015 FREEZE**
- Provider/license/timestamp/PIT: **NOT VERIFIED**, except only the explicitly reviewed per-use permission needed for an attempted operation
- Historical universe: **NOT RELIABLY BACKTESTABLE**
- Risk Budget: **RISK BUDGET NOT APPROVED**
- Production: **NOT PRODUCTION READY**

This is a design-contract PASS, not `PASS_ENGINEERING_P2_FORWARD_CAPTURE` and not model validation.
