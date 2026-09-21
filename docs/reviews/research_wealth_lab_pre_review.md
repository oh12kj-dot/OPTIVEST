# RESEARCH-WEALTH-LAB-V1 independent pre-implementation review

Date: 2026-09-14, Asia/Tokyo. Reviewer role: GPT-5.6 Sol, independent falsification-first pre-review. Exact reviewed draft: `docs/RESEARCH_WEALTH_LAB_DESIGN.md`, raw SHA-256 `2DDDC542373193ABAE53165A66AE96151AFDE9FB3662F04B2EBC7F6448492AA3`.

## Verdict

**`DESIGN CHANGE REQUIRED / NOT READY FOR SCOPED DECISION FREEZE`**.

The proposed narrowing is sound: a deterministic, stateless synthetic accounting laboratory can establish engineering algebra without pretending to supply the missing economic forecast, calibrated `U_objective`, `U_risk`, binding `S_stress`, risk feasibility, optimizer, ranking, action or real investment evidence. The draft also correctly preserves benchmark-versus-passive, cash-versus-risk-free, stress-versus-objective, cost-once and `NO_TRADE` boundaries.

The exact draft is not freezeable. Six bounded contract gaps below admit materially different parsers, recovery results, comparison signs, public numerical invariants, error bodies or artifact identities. Terra would have to choose those semantics. Astra must correct the design, recalculate its hash and return the new exact artifact for a short independent re-review before adding an ADR or dispatching implementation.

This is a document review, not numerical/model validation. No application code, tests, Policy, frozen design, ADR, provider state, database, Risk Budget, Production register or research trial was changed. No provider/network capture or implementation test was run.

## Independent baseline and formula reproduction

The selected Policy was independently hash-verified as `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` and read completely before this disposition. Its relevant constraints are: base-currency/flow/cost semantics belong to an approved mandate; missing is not zero; strict-log ruin cannot be clipped; cost enters wealth once; `U_objective`, `U_risk` and `S_stress` remain separated; benchmark, investable passive, cash, risk-free proxy and no-trade have different roles; material design requires blind pre-review and exact freeze; every section 18 item is an AND gate.

Before relying on Astra's rationale, the draft's closed inputs, formulas and W1-W19 were evaluated directly. Independent results, without importing a wealth-lab evaluator, are:

- W3: `cash_0 = 60 - (3-2)*20 - 2 = 38`; post-trade wealth is `38 + 3*20 = 98`. At month 1, cash is `38*1.1 + 3*1 = 44.8`, position value is `3*22 = 66`, and wealth is `110.8`. The timing convention is internally coherent.
- W4: cost-only terminal ratio is `.98`; annual log growth is `ln(.98)/7 = -0.002886101045359921201149328717741769693...`. No second cost subtraction is warranted.
- W7: a zero-mass ruin path must be omitted before the log; any positive mass on that path makes the member utility negative infinity. `(-infinity)-(-infinity)` has no usable difference. The draft's fail-closed rule is correct.
- W10: equal masses on terminal ratios `.5` and `2` give `(ln(.5)+ln(2))/14 = 0`; exponentiating gives geometric-equivalent growth zero although arithmetic mean terminal ratio is `1.25`.
- W11: the two member utilities are `+ln(2)/14` and `-ln(2)/14`, i.e. approximately `+/-0.04951051289713895067265943724701261200539`; the lower envelope is the negative member. This is a supplied-family diagnostic only, not approved `U_objective` or `U*(A)`.

## Blocking findings and required corrections

### B1 - Raw parser parity and structural bounds are not a single implementable contract

Draft line 25 requires duplicate-key rejection at every depth and HTTP/CLI/library agreement, but a library caller that supplies an already-created dictionary cannot detect raw JSON duplicates: `{"x":1,"x":2}` has already collapsed to one key. The same line requires exact maximum/one-over tests without defining whether root and scalar nodes count toward depth 16 and node count 100,000. It rejects compressed bodies without an error code or exact `Content-Encoding` rule.

Required correction:

1. Freeze separate entry points: a raw-byte decoder/evaluator shared by HTTP and CLI, and a mapping normalizer whose explicitly narrower guarantees exclude already-lost wire facts; alternatively require every public/library entry point to take raw bytes.
2. Define depth and node counting recursively, including the root, object keys versus values, scalars and empty containers, so W1 max/one-over fixtures are exact.
3. Define JSON Pointer paths for duplicate keys and decoder failures, the accepted media-type grammar, the exact rejection of any non-identity content encoding, and stable error codes/statuses.
4. Update W1 so parity is required only where the compared surfaces possess the same raw evidence.

### B2 - The recovery state machine is ambiguous at flat high-water ties

Draft line 75 says an episode anchors at the latest preceding high-water event, but says to update the anchor on a "recovered/new-high" event. Consider PRE_TRADE=1,000,000, POST_TRADE=1,000,000, month 1=1,000,000, month 2=800,000 and flat thereafter. "Latest preceding high-water event" gives peak month 1 and an unrecovered observed lower bound of 83 months. Updating only on a new high or recovery leaves peak month 0 and gives 84 months. Both readings fit part of the prose, while W9 demands exact latest-anchor behavior.

Required correction: freeze an event-indexed recovery state machine. At minimum state whether an at-high equality while no episode is open refreshes the anchor; how PRE_TRADE then POST_TRADE are ordered within month 0; the exact close/open behavior at equality/new highs; and the exact W9 episode objects for both paths, flat ties and an initial-cost episode. If event identity matters beyond duration, add `peak_event_kind`/`recovered_event_kind`; otherwise explicitly state why month alone is sufficient.

### B3 - The public numeric contract contradicts the exact-fraction acceptance and leaves the comparison formula undefined

Draft lines 67 and 164 require exact fractions summing to one, but lines 91-93 and 123 expose each fraction only as a separately rounded 40-significant-digit `Number`. A valid path can have two marked assets of USD 1 and cash USD 1 (for example, after an initial exact USD 1,000,000 state with two USD 499,999.5 positions and USD 1 cash). Each public fraction is exactly `1/3` internally. Three independently rounded 40-digit decimal renderings sum to `0.999...`, not exactly one. W14 therefore cannot be true as a black-box public-output oracle under the current schema.

Draft line 83 and output line 123 also expose one `difference_to_no_trade` without specifying which utilities it subtracts. This can reverse the sign. If alternative member utilities are `[0,-1]` and no-trade member utilities are `[-2,0]`, then difference of separate lower envelopes is `(-1)-(-2)=+1`, while the worst paired member difference is `min(0-(-2),-1-0)=-1`.

Required correction:

1. Choose and freeze one exact-fraction/output policy: expose canonical numerator/denominator state for rational ledger values, or explicitly limit exact-sum acceptance to an internal rational invariant and specify the public rounding error contract. W14 must name the surface it tests.
2. Define `difference_to_no_trade` by equation, including whether it is `lower_envelope_a-lower_envelope_NO_TRADE`, a same-member vector, or another diagnostic; define its member alignment, infinity handling and label. Add the sign-reversal counterexample as a permanent oracle.
3. Freeze the complete derived-number grammar with examples: sign, mantissa digit count, trailing zero policy, exponent sign/zero normalization, negative one, zero and rounding-before-versus-after subtraction.
4. Freeze the exact display-level tie algorithm separately from exact minimum selection and state which membership is returned when exact values differ but 40-digit displays tie.

### B4 - Failure, capabilities and unavailable-result JSON are not closed

Draft line 119 says `findings` contains only `{code,path}`, while line 129 promises generic static human explanations. No field or out-of-band code table carries those explanations. `Capabilities` is described only in prose. The exact component-specific reasons in `unavailable` are not enumerated. Failure priority and aggregation are incomplete when malformed syntax, missing V states and accounting defects coexist. Policy/design/source hash mismatch, missing/non-regular/unreadable CLI file and disallowed content encoding have no closed error mapping. The 32 MiB result check does not define which serialized bytes are counted.

Required correction:

1. Freeze complete `Capabilities`, `Evaluation`, `Artifact`, finding and unavailable arrays with exact keys, ordering, enums and reason-code table. Either add a static `message` field to each finding or remove the explanation promise and make the UI's fixed code-to-text map part of the contract.
2. Freeze precedence/aggregation: decoder failure, typed invalidity, structurally valid incompleteness, accounting invalidity, numerical nonconvergence, authority/source failure and internal failure. State when `input_sha256` and provenance are available for each class.
3. Define HTTP and CLI behavior for content encoding, authority mismatch, file missing/not-regular/too-large/unreadable, argument misuse and output write failure. Preserve one JSON object where promised and no path/source/stack leakage.
4. Define result-size measurement as an exact canonical byte serialization and specify whether the downloadable artifact has its own bound.

### B5 - Provenance does not cover every source that can determine the downloaded artifact

Draft line 139 hashes only `wealth_lab.py`, the API module and the example JSON. Yet line 141 makes the browser-downloaded artifact and its digest acceptance evidence, and line 143 assigns artifact construction/download behavior to JavaScript. A change to `wealth_lab.js`, CLI dispatch/serialization or route integration can change behavior without changing any listed source hash. If Pydantic participates in normalization, the provenance also omits its resolved version or lock identity. Thus W17's broad claim that a source change changes artifact identity and that provenance is complete is false as written.

Required correction:

1. Define the exact relative-path-keyed source manifest and include every artifact/evaluation-determining source, or narrow the reproducibility claim and W17 to the listed evaluator core.
2. Include the canonicalization/hash implementation identity and, if third-party validation is used, the resolved validation dependency/lock identity. Define behavior when a manifest file or Git executable is unavailable.
3. State exactly where artifact SHA-256 is computed, the canonical bytes hashed, and how API/CLI/browser rehash the same object independently. Client-supplied provenance remains forbidden.
4. Preserve the honest UNBORN/GIT_NOT_AVAILABLE distinction and do not turn source identity into release/authenticity evidence.

### B6 - Several W-oracles are goals rather than frozen counterexamples

The matrix is a strong outline, but W1's exact limits are undefined as noted above; W6 combines valid settlement, invalid reversal and absorbing-ruin cases such that an early invalid bundle can mask later assertions; W8 says coupling changes utility "as expected" without complete units/path values or expected results; W9 lacks exact objects; W17's source-change scope conflicts with the manifest; and W19 lacks a canonical maximum fixture, result-size bytes, fault-injection seam and exact failure payload. These cannot serve as independent pass/fail oracles until the implementer makes choices.

Required correction: split mutually exclusive cases, provide the minimum complete numerical fixture/delta and exact expected output for W6/W8/W9, scope W17 to the corrected manifest, and define W19's exact maximum bundle plus explicit test-only injected convergence/invariant faults. Retain the rule that independent expected values cannot call production normalizers/formulas.

## W1-W19 disposition

| ID | Pre-review disposition | Reason / required condition |
|---|---|---|
| W1 | **CHANGE REQUIRED** | B1/B4: raw-dict parity is impossible; exact depth/node/media/error/result bounds are not frozen. |
| W2 | **CHANGE REQUIRED** | Missingness separation is correct, but mixed-invalid precedence, hash availability and exact finding payload must be frozen under B4. |
| W3 | **READY AFTER FREEZE** | Independent exact accounting reproduces cash 38, W 98, cash 44.8, asset 66, W 110.8. |
| W4 | **READY AFTER FREEZE** | Independent oracle confirms W 98 and `ln(.98)/7`; cost is represented exactly once. |
| W5 | **READY AFTER FREEZE** | Funding/cash/no-trade rules are coherent; retain whole-bundle rejection and no fallback selection. |
| W6 | **CHANGE REQUIRED** | Algebra is coherent, but split final-settlement, reversal-rejection, absorbing-zero and unheld-positive-price cases so invalid input does not mask later assertions. |
| W7 | **READY AFTER FREEZE** | Zero-mass exclusion, positive-mass negative infinity, tiny-positive/no-floor and nonfinite comparison rules are sound. |
| W8 | **CHANGE REQUIRED** | Joint-path principle is correct; supply a complete fixture and exact wealth/utility/drawdown outcomes instead of "as expected". |
| W9 | **CHANGE REQUIRED** | B2: flat-high anchor behavior and exact recovery episode objects are ambiguous. |
| W10 | **READY AFTER FREEZE** | Independent analytical result is zero expected annual log and zero geometric equivalent, not expected CAGR. |
| W11 | **READY AFTER FREEZE, LIMITED** | Member and lower-envelope math is correct; it does not close the undefined `difference_to_no_trade` in B3. |
| W12 | **READY AFTER FREEZE** | Stress/objective separation and rejection of added uncertainty layers match Policy. |
| W13 | **READY AFTER FREEZE** | Correctly prevents feasibility, optimizer, benchmark-weight, passive-approval and proxy claims. |
| W14 | **CHANGE REQUIRED** | B3: exact internal rational sum and separately rounded public decimals cannot both satisfy the stated black-box exact-sum oracle. |
| W15 | **READY AFTER FREEZE** | Current architecture permits DB-free CLI dispatch and session-free routes; implementation must prove no DB/network writes and retain provider/preflight denials. |
| W16 | **READY AFTER FREEZE** | No schema/revision change is necessary; use only fresh disposable SQLite and preserve existing exact verifiers. |
| W17 | **CHANGE REQUIRED** | B5: manifest/canonical artifact provenance is incomplete and source-change scope is false as written. |
| W18 | **CHANGE REQUIRED** | UI behavior is well bounded, but exact error/artifact/download contracts depend on B4/B5. Keep desktop and actual 390px browser evidence mandatory. |
| W19 | **CHANGE REQUIRED** | B3/B4/B6: number grammar, exact serialized-size target, maximum fixture and injected-failure outputs are not frozen. |

## Nonblocking findings and compatibility conclusions

- The initial trade identity `W_after = W_initial - C`, interval cash-growth-before-distribution event order and terminal ex-distribution mark are coherent. Cost is neither added to prices nor subtracted again from utility/comparison.
- USD-only, nominal, pre-tax, no-flow semantics are visibly synthetic and do not claim approval of the current editable mandate. Rejecting FX/tax/flow fields while leaving real base-currency FX validation deferred is Policy-compatible.
- Strict zero classification, no wealth floor, negative-infinity expected log for positive ruin mass and null nonfinite difference are appropriate engineering semantics. They do not establish calibrated permanent-loss probability.
- The fixed seven-row ledger prevents accidental extra buffers/sizing layers. The finite supplied mass-family result is correctly called a diagnostic, not `U_objective`, `U*(A)` or a decision hurdle. Stress remains unweighted and nonbinding.
- Benchmark has no position weight; synthetic passive is a holdings asset; cash has supplied factors but is not a risk-free proxy; `NO_TRADE` is a supplied alternative. Real CRSP/VTI/proxy status stays unavailable.
- The no-model/no-action/no-DB-write boundary is compatible with the current FastAPI app factory, Alembic revision checks, provider display denial, preflight persistence and CLI structure. The proposed CLI can dispatch before `make_session()` even though importing SQLAlchemy modules is not itself a database open.
- The stated `O(A*S*M*I)` bound and 53,760 maximum asset-month-alternative evaluations are reasonable engineering bounds. They are not evidence sufficiency or service capacity claims; B4/B6 must still freeze byte measurement and maximum-fixture evidence.
- Allowed implementation files are appropriately narrow. No model, migration, service, risk-editor, phase2, dependency, Policy, frozen design, retained reviewer test, provider raw file, user DB, research ledger or Production-gate change is justified by this design.

## Astra-ready correction and re-review gate

1. Resolve B1 and B4 as one closed raw-boundary/capabilities/error appendix.
2. Resolve B2 with an event-indexed recovery state machine and exact W9 outputs.
3. Resolve B3 with an explicit rational-versus-display contract, exact derived-number grammar, display-tie algorithm and one equation for `difference_to_no_trade`; add both counterexamples.
4. Resolve B5 with a complete or explicitly narrowed source/artifact provenance contract.
5. Replace the affected W1/W2/W6/W8/W9/W14/W17/W18/W19 rows with exact, independently decidable cases while retaining W3/W4/W7/W10/W11.
6. Recalculate the design SHA-256 and request independent Sol re-review. Only a PASS on that exact corrected hash permits Astra to add a narrowly scoped ADR freeze. Terra remains undispatched until then.

## Status boundaries and next action

Controlling status: `DESIGN CHANGE REQUIRED / NOT FROZEN / IMPLEMENTATION NOT AUTHORIZED`.

All existing gates remain unchanged: `RISK BUDGET NOT APPROVED`; investment model, risk feasibility, provider/PIT/tradability, calibration and OOS remain `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`. This review does not satisfy any Policy section 18 item, approve a benchmark/passive/risk-free implementation, validate a research trial or authorize Production, deployment, billing, order or user-database operation.

Next action: Astra corrects only the six bounded design findings above, preserves the narrow synthetic/non-decision scope and submits the new exact hash for re-review. No implementation should begin from draft hash `2DDDC542373193ABAE53165A66AE96151AFDE9FB3662F04B2EBC7F6448492AA3`.

## Reviewed evidence identity

| Artifact | SHA-256 / state |
|---|---|
| `OPTIVEST_AI_POLICY_V10.md` | `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` |
| `AGENTS.md` | `BA424C1B11B4C3CB7AACB86CD870E67D35CAD70D1040DEB5CFD96B4E8B9A3689` |
| `docs/INITIAL_DESIGN.md` | `43FCCF65CD4320B76D835198E2C18A0DD1FF87F1A0B2E88571B0360A7A65A364` |
| `docs/PHASE1_DESIGN.md` | `C23222188016A4A164C0DBB3434D9B8CA768C91CC3B826523744E47C9FF4CD68` |
| `docs/RESEARCH_RISK_EDITOR_DESIGN.md` | `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950` |
| `docs/RESEARCH_WEALTH_LAB_DESIGN.md` | `2DDDC542373193ABAE53165A66AE96151AFDE9FB3662F04B2EBC7F6448492AA3` |
| Repository | branch `main`; HEAD `UNBORN`; working tree untracked/dirty |

Relevant current application hashes inspected for integration claims: `optivest/app.py` `4AFF916E4387C0A2ED5107E9E2FEF7BBB503B79850A860AA994D67169D9950B1`; `optivest/cli.py` `CB6BE592A63F41C5937F192D531E1AB11BBD1D3CAB0E0A9180160E91EDCDFEA1`; `optivest/service.py` `3F49B88D3B0756BB90B7C8DA990C65A2C698335AB3650E18128C665261E3BB4E`; `optivest/models.py` `6E429EB87E7A1C70C0AA55FD3CA20EDAAF569287BCB3554A7FBB3CB6C112AE8A`; `optivest/risk_editor.py` `7BD73E1907500089A75B775D6DDD9EF8802C07130324391D864A195E7F5F3877`; `optivest/phase2.py` `5E92ED6769097114072314CC47E1ADC0B06B2F41C0FC44FD55F2931CAC274560`.

---

## Revision 2 independent re-review — controlling disposition

Date: 2026-09-14, Asia/Tokyo. Reviewer: GPT-5.6 Sol. Exact corrected target: `docs/RESEARCH_WEALTH_LAB_DESIGN.md`, raw SHA-256 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`. The original draft-1 findings above remain historical evidence; this section is the controlling disposition for revision 2.

### Verdict

**`PASS FOR SCOPED DECISION FREEZE`**.

Independent falsification found no remaining design blocker in B1-B6. Revision 2 is sufficiently closed for Astra to freeze this exact hash as a synthetic accounting-lab implementation contract. PASS authorizes no code by itself: Astra must first add a narrowly scoped ADR that pins the exact design and review identities. Any semantic or allowed-file change requires `DESIGN CHANGE REQUIRED` and renewed review.

This PASS is not investment/model/risk/PIT/provider/OOS/shadow/Production validation. It approves only the design specificity of a stateless, supplied-synthetic accounting and finite-hypothesis diagnostic. It does not approve a mandate, Risk Budget, probability model, `U_objective`, `U_risk`, `S_stress`, optimizer, rank, action, real benchmark/passive/proxy, provider input or empirical trial.

### B1-B6 closure

| Prior blocker | Independent re-review result |
|---|---|
| B1 raw parser parity/bounds | **CLOSED.** Public evaluation accepts raw `bytes` only; dict/string/bytearray are explicitly outside duplicate-key parity. Root depth, scalar/container node count, raw-byte size, duplicate pointer escaping, media grammar, content encoding and stage precedence are exact. Sixteen nested arrays around a scalar give depth 16/17 nodes; 99,999 array scalars plus root give exactly 100,000 nodes. |
| B2 recovery clock | **CLOSED.** Events have a total index order; equality at a high refreshes the anchor even with no open episode; PRE_TRADE/POST_TRADE disambiguate month 0. The state machine and W9 objects decide the prior flat-high counterexample as peak month 1/lower bound 83. |
| B3 rational/display/comparison | **CLOSED.** Exact rational ledger invariants and bounded public decimals are separate. Fractions are not renormalized. Derived-number grammar, 40-digit error bound, minimum/tie selection and subtraction-before-rounding are fixed. `difference_to_no_trade` is explicitly the difference of separately evaluated lower envelopes, including null nonfinite behavior. |
| B4 closed results/failures | **CLOSED.** Capabilities, Evaluation, Artifact, unavailable table, findings, stage priority, aggregation, HTTP/CLI exits, authority/file/content-encoding/write failures and exact canonical size measurement are specified. No exception text, path contents or partial success is returned. |
| B5 provenance/artifact identity | **CLOSED.** The relative-path manifest now covers core canonicalization/evaluation, API/app/CLI, browser assets, fixture and dependency identities. Runtime versions, loaded-versus-disk rechecks, same-root Git states, canonical JSON bytes, server digest and independent API/CLI/browser rehash are explicit. Claims remain limited to observed reproducibility, not authenticity or empirical validity. |
| B6 exact W-oracles | **CLOSED.** BASE and MAX are complete builders. Previously conflated W6 cases are separated; W8/W9/W11/W14 have exact independent outcomes; W17 source/canonical mutations and W19 counts, byte helpers and private test-only fault seams are decidable without production formulas. |

### Independent recalculation and counterexample checks

- Raw bounds: 16 nested arrays around scalar zero produce root depth 0 through scalar depth 16 and 17 total nodes; 17 arrays fail depth. A root array with 99,999 scalar elements contains 100,000 nodes; one more element fails nodes. `S_N={"s":"` + `N-8` ASCII bytes + `"}` is exactly N bytes.
- Recovery: PRE=1,000,000, POST=1,000,000, month1=1,000,000, month2=800,000 causes the equal-high month1 event to replace the POST anchor. The open episode therefore has peak month1/MONTH and observed lower bound `84-1=83`. The four W9 objects match the specified state machine.
- W3/W4 remain exact: cash 38, post-trade wealth 98, next cash 44.8, asset 66, wealth 110.8; `ln(.98)/7=-0.002886101045359921201149328717741769693...`.
- W8: correlated paths produce wealth 500,000/2,000,000 and mean annual log zero; offsetting paths produce 1,250,000 on both and `ln(1.25)/7=0.031877650187744250823756441472833500482...`. The separate transient dip has terminal log zero and sampled drawdown .4.
- W10/W11: equal `.5/2` terminal ratios give annual expected log zero. The `.75/.25` members give `+/-ln(2)/14`. In the sign oracle, separate minima `-ln(2)/7` and `-2ln(2)/7` differ by `+ln(2)/7=0.099021025794277901345318874494025224010...`; a paired-difference minimum would incorrectly be negative. If either separate minimum is negative infinity, the public difference is UNAVAILABLE/NONFINITE_COMPARISON.
- W14: the exact ledger contains three fractions 1/3 summing to 1. Each 40-digit public rendering is `3.` plus 39 threes plus `e-1`; at sufficient independent Decimal precision the displayed sum is exactly `1-10^-40`, within the declared non-renormalized bound. Input masses `.333333+.333333+.333334` equal one exactly, while three `.333333` do not.
- MAX: 8 alternatives across 20 paths give 160 alternative PathResults; `160*86=13,760` alternative events; `20*85=1,700` benchmark events; `4*20*84*8=53,760` asset-month-alternative evaluations. The funded custom alternatives retain exact USD 1,000,000 wealth through residual cash. All lower-envelope member IDs tie at zero as specified.

### W1-W19 revision-2 disposition

These are design-oracle dispositions, not executed implementation test results.

| ID | Disposition | Re-review basis |
|---|---|---|
| W1 | **CLOSED FOR FREEZE** | Raw-only parity, exact depth/node/byte/media cases and pointers are fixed. |
| W2 | **CLOSED FOR FREEZE** | Typed-invalid, missingness and dependent-accounting precedence plus hash/provenance availability are exact. |
| W3 | **CLOSED FOR FREEZE** | Independent rational accounting matches every stated value. |
| W4 | **CLOSED FOR FREEZE** | Cost-only path and log oracle remain correct; no duplicate penalty. |
| W5 | **CLOSED FOR FREEZE** | Cash/no-trade/funding and whole-bundle rejection semantics are unambiguous. |
| W6 | **CLOSED FOR FREEZE** | Settlement, reversal, ruin, cash-factor, unheld-asset and malformed-value cases are separate. |
| W7 | **CLOSED FOR FREEZE** | Zero-mass exclusion, positive-mass negative infinity, no clipping and nonfinite comparison are exact. |
| W8 | **CLOSED FOR FREEZE** | Complete correlated/offsetting/transient fixtures reproduce the stated utilities and drawdowns. |
| W9 | **CLOSED FOR FREEZE** | Exact event-indexed episode arrays close equality, flat-tie, cost and right-censor clocks. |
| W10 | **CLOSED FOR FREEZE** | Expected annual log and geometric-equivalent labels are correct. |
| W11 | **CLOSED FOR FREEZE** | Basic member math, separate-minimum sign oracle, infinity and display-tie membership are fixed. |
| W12 | **CLOSED FOR FREEZE** | Stress remains unweighted, nonbinding and outside the supplied lower envelope. |
| W13 | **CLOSED FOR FREEZE** | No cap import, feasibility, benchmark weight, optimality or real-alternative promotion. |
| W14 | **CLOSED FOR FREEZE** | Exact private rational invariant and bounded public representation are explicitly distinct; probability sums remain exact. |
| W15 | **CLOSED FOR FREEZE** | DB/network-free evaluator and caller-path non-promotion evidence are mandatory. |
| W16 | **CLOSED FOR FREEZE** | No schema/revision/writer change; disposable migration regression remains mandatory. |
| W17 | **CLOSED FOR FREEZE** | Manifest, loaded-source, canonical Unicode, restart, input/source/artifact and Git-state oracles are complete. |
| W18 | **CLOSED FOR FREEZE** | Exact bytes, local rehash failure, stale state, XSS, mobile layout and no-action surfaces are closed. |
| W19 | **CLOSED FOR FREEZE** | MAX counts, canonical byte helpers, invariant/nonconvergence/size failures and private seams are exact. |

### Conditions for Astra's scoped exact-hash freeze

1. Freeze only `docs/RESEARCH_WEALTH_LAB_DESIGN.md` SHA-256 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C` under selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` and cite this controlling revision-2 review disposition by its final hash.
2. The ADR must state that the freeze covers the raw Bundle/parser, exact ledger/timeline/recovery/ruin algebra, finite supplied-member diagnostic, Decimal/display rules, closed Evaluation/Artifact/capabilities/failure contracts, manifest/canonical provenance, stateless API/CLI/UI integration, allowed files and W1-W19 acceptance matrix only.
3. The ADR must preserve the design's exact allowed-file list. It must prohibit models/service/risk_editor/phase2/migrations/dependencies/lock/Policy/frozen-design/reviewer-test/provider-raw/user-DB/RESEARCH_TRIALS/PRODUCTION_GATE changes and any decision/preflight/activation/provider path.
4. Terra may implement only after that ADR exists. Material changes to input support, formulas, event order, comparison, numeric method, bounds, provenance, persistence or status output require unfreeze and renewed review rather than implementer choice.
5. Engineering acceptance remains pending implementation plus all W1-W19, focused/full regression, compile/JS/startup/hash/diff, isolated DB no-write and real HTTP/CLI/browser evidence, followed by independent Sol post-validation. Green tests alone are not acceptance.
6. Every existing limitation remains literal: `RISK BUDGET NOT APPROVED`; model, risk feasibility, provider/PIT/tradability, calibration and OOS `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`. No Policy section 18 item is promoted by the design freeze.

### Scope and evidence limits

No code/test/DB/provider/network/browser execution exists for the proposed lab, so this re-review makes no `PASS_ENGINEERING` or model-validation claim. Existing app/CLI/service/model/risk-editor/phase2 contracts remain the inspected compatibility baseline and are not modified. Current repository identity remains branch `main`, HEAD `UNBORN`, wholly untracked/dirty; tracked `git diff` alone cannot inspect new files.

No blocker/nonblocker requiring design change remains. The next action is Astra's exact-hash scoped ADR freeze under the six conditions above, then Terra implementation, automated evidence and independent Sol post-validation.
