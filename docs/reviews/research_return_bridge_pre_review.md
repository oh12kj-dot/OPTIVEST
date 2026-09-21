# RESEARCH-RETURN-BRIDGE-LAB-V1 independent pre-implementation review

Reviewer: GPT-5.6 Sol, independent falsification-first review, 2026-09-21 (Asia/Tokyo).

Reviewed design: `docs/RESEARCH_RETURN_BRIDGE_DESIGN.md`, draft 1, raw SHA-256 `6946F1608D638244A3677A0338B37DAC84C7290B10ED134DA6293AE10229B26B`.

Authority: `OPTIVEST_AI_POLICY_V10.md`, raw SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.

Repository state observed before review: branch `main`; `HEAD` is `UNBORN`; the checkout is wholly untracked. No implementation, model, database, provider, research-trial, decision-freeze or Production-gate change was made by this review.

## Verdict

**DESIGN CHANGE REQUIRED**

Draft 1 is not ready for an exact-hash scoped decision freeze. Its non-production boundary and the choice to keep a supplied-synthetic, stateless, DB-free diagnostic are directionally sound. The current artifact nevertheless leaves material investment/accounting semantics and engineering contracts open or contradictory:

- the claimed Economic Return Bridge lacks a closed FCFE accounting basis and cannot distinguish a terminal-holder identity from a path-aware shareholder return;
- cumulative distributions, buybacks and reinvestment/capital-allocation coherence are not jointly closed;
- the hierarchical prior's additive components and shrinkage baseline are not disjointly defined;
- the nine-row ledger blocks forbidden role names but does not close economic-source overlap or derived-source dependencies;
- wire ordering and semantic canonicalization contradict one another;
- zero/nonfinite/CAGR, tie and empty-range behavior are not closed;
- Evaluation/Artifact/Capabilities, findings, stage precedence, hashes, source manifest and transport failures are not exact contracts; and
- R1-R16 and the maximum/resource case lack the complete fixtures, fixed serialized limits and exact oracles required for independent decidability.

No implementation is authorized. Astra must issue a corrected design, obtain a new raw SHA-256, and request an independent re-review before any ADR/freeze.

## Independent falsification baseline

### Scope choice

A narrow supplied-synthetic lab is an acceptable intermediate engineering slice only if it is represented as a **terminal FCFE-per-share identity and prior-decomposition diagnostic**, not as satisfaction or validation of the selected Policy's full Economic Return Bridge. Policy section 7 and Production item 8 additionally require reinvestment/Incremental ROIC consistency, capital intensity, capital allocation, base-currency/FX treatment where relevant, fitted distributions and validation. Draft lines 14-16 and 228-232 correctly deny those promotions, but lines 7-12 and the artifact name overstate what the proposed arithmetic closes.

The correction need not broaden into a forecast, path generator or optimizer. It may keep the same narrow slice by tightening its name, labels, basis literals and explicit `NOT VERIFIED` boundaries.

### Independently reproduced arithmetic

The following equations themselves reproduce when their inputs are interpreted as intended:

- `start_fcfe_per_share = start_revenue * start_fcfe_margin / start_shares`;
- terminal price factor = revenue factor x margin factor x inverse share-count factor x valuation factor;
- terminal holder factor = terminal price/start price + cumulative distribution/start price;
- `shrunk alpha = w * raw alpha + (1-w) * alpha prior`.

That arithmetic does not close the semantic ambiguities below.

Distribution timing counterexample: start and terminal price are both 100 and cumulative distribution is 10. Draft 1 returns terminal value 110 and annualized terminal rate approximately `0.013708856295468119...` regardless of when the cash was paid. If the same cash was paid after year 1 and merely held at a supplied 5% cash rate through year 7, terminal value is `113.400956406250` and the annualized rate is approximately `0.018128016064272623...`. A field described as paid "over the seven-year interval" cannot support one annualized return without a timing/reinvestment convention.

Prior counterexample: risk-free `.03`, broad-market premium `.05`, factor/sector `.08`, zero alpha yields `.16` if `.08` is an incremental factor/sector log spread, but `.11` if `.08` is a total sector excess-return prior that already includes the broad-market premium. Both interpretations satisfy the present field names and basis literal.

## Blocking findings and required corrections

### B1 - HIGH - Scope and FCFE basis are not a closed economic identity

- **Location:** sections 1-2, lines 7-24; section 4, lines 50-64; section 5, lines 85-119.
- **Counterexample/reason:** `start_revenue` can denote trailing-twelve-month revenue while scenario revenue can denote a terminal annual run rate; `start_shares` can be weighted-average diluted shares while the ending factor denotes point-in-time basic shares. Both bundles pass the numeric equations but produce economically incomparable FCFE/share and P/FCFE values. The current `basis` literal applies only to the statistical prior and does not close the accounting basis. The proposed slice also omits reinvestment, Incremental ROIC and capital intensity while calling the result an Economic Return Bridge.
- **Required correction:** define exact common start/terminal accounting-period, currency, FCFE-to-common-equity, interest/debt, recurring/nonrecurring, share-count and per-share denominator semantics as closed literals. State whether start and terminal quantities are annual run rates, trailing periods or forecast-period totals. Either rename/relabel the slice as a synthetic terminal FCFE-per-share identity or add the missing reinvestment/Incremental-ROIC consistency contract. If the narrow option is retained, expose an explicit `reinvestment_incremental_roic_status = NOT VERIFIED` and make clear that Policy section 18 item 8 is not advanced.
- **Disposition:** **OPEN / BLOCKING**.

### B2 - HIGH - Distribution timing and buyback/capital-allocation double counting are not closed

- **Location:** section 4 lines 66-74; section 5 lines 89-119; R5-R7 lines 205-207.
- **Counterexample/reason:** the distribution timing counterexample above produces different terminal wealth from the same accepted field. Separately, a scenario can combine a sharply lower share-count factor with a large cumulative cash distribution even though the design has no cumulative FCFE, repurchase-spend, issuance/SBC, debt/cash financing or capital-allocation identity. The formula uses each numeric field once, but that is not proof that the same economic cash was not used once for repurchases and again for holder distributions. The field also does not state whether issuer repurchase proceeds paid to a tendering holder are excluded.
- **Required correction:** choose and freeze one bounded convention. The narrowest correction is: distributions are non-repurchase cash paid to a continuously held start share; all such cash is assumed paid at the terminal event (or held in a zero-return cash account from payment, with that assumption explicit); repurchase/tender proceeds are excluded; share-count factor represents net fully diluted shares after issuance/SBC/repurchase. Rename the output to a terminal-equivalent holder-value rate if timing is not modeled. Narrow R6 to **mechanical channel nonduplication**, emit `capital_allocation_coherence = NOT VERIFIED`, and prohibit claims that cumulative FCFE financing or reinvestment coherence was tested. Alternatively add a complete capital-allocation path, which would be a broader design.
- **Disposition:** **OPEN / BLOCKING**.

### B3 - HIGH - The hierarchical prior is additive without disjoint component semantics

- **Location:** section 4 lines 76-83; section 6 lines 121-131; section 8 lines 154-167; R9 line 209.
- **Counterexample/reason:** the `.16` versus `.11` counterexample above is not resolvable from `SUPPLIED_SYNTHETIC_LOG_COMPONENTS`. `factor_sector_annual_log_return` may be an incremental residual, a sector total premium, or a factor-model fitted return already containing broad-market exposure. `company_alpha_prior` may likewise already embed sector/base-rate information. The shrinkage equation is arithmetically clear, but its target and the additivity boundary are not.
- **Required correction:** define every component in the same USD nominal pre-tax seven-year annual-log basis and make each non-risk-free term an explicitly **incremental, non-overlapping** spread relative to the preceding hierarchy, or replace the scalar sum with an exact supplied decomposition that states exposures and premia. Define the alpha prior's reference population and confirm it excludes the broad-market and factor/sector components already present. Add exact negative tests for an incompatible basis literal.
- **Disposition:** **OPEN / BLOCKING**.

### B4 - HIGH - The uncertainty ledger is syntactically closed but does not close overlap

- **Location:** section 8 lines 143-167; R12 line 212.
- **Counterexample/reason:** `SOURCE_MARKET_FACTOR` covers two separate prior inputs, while the economic rows are variable categories rather than actual source occurrences. `SOURCE_LAYER_DISAGREEMENT` is derived from every economic and prior input but no dependency edge records that fact. `overlap_group` is arbitrary inert text, so two economically identical assumptions can be placed in different strings and appear separate. The current role allowlist prevents a forbidden role token, but it does not establish the claimed double-counting closure.
- **Required correction:** make source-to-field coverage one-to-one and explicit. Split broad-market and factor/sector sources or combine their input field; define closed `overlap_group` literals and required group membership; record derived-source dependencies for layer disagreement; define canonical secondary-role ordering; and reject duplicate economic coverage across rows. If V1 is only a role-denial registry, rename it accordingly and stop claiming it validates overlap/double counting.
- **Disposition:** **OPEN / BLOCKING**.

### B5 - CRITICAL - Wire ordering and canonical semantic identity contradict each other

- **Location:** section 4 lines 45-48 and section 8 line 167; R2 line 202; R8 line 208; R14 line 214.
- **Counterexample/reason:** assets and scenarios are required to be canonically ordered, ledger noncanonical ordering is invalid, and R2 requires canonical-order failures. R8 and R14 instead require reordered semantic sets to preserve the canonical hash. The same swapped-assets input therefore must be both rejected and accepted with the same identity.
- **Required correction:** enumerate every array as either semantic set or semantic sequence. For semantic sets, accept arbitrary wire order, preserve wire indices for findings, sort only the canonical normalized copy and prove permutation identity. For sequences, require exact order and reject permutations. If the ledger intentionally requires presentation order, exclude it from permutation tests and state its exact order. Remove every contradictory acceptance statement.
- **Disposition:** **OPEN / BLOCKING**.

### B6 - HIGH - Zero, nonfinite, tie and range outputs are incomplete

- **Location:** section 5 lines 101-107; section 7 lines 135-141; section 9 lines 169-187; R7, R10, R11 and R13 lines 207, 210-213.
- **Counterexample/reason:** a zero terminal factor is declared exact total return `-1` and negative-infinite log, but the design then says no finite CAGR is emitted, while the extended identity `exp(-infinity)-1` and the accepted wealth-lab convention yield finite `-1`. Either convention can be chosen, but the current output shape is absent. If every scenario is zero-terminal, the finite set used by the per-asset minimum/maximum is empty and no range behavior is specified. `EQUAL_AT_ACTIVE_PRECISION` and IDs attaining a "displayed value" have no exact rounding/tie rule. A revenue-zero scenario with a positive cash distribution is not zero-terminal, so R7 is also under-specified.
- **Required correction:** define a closed tagged numeric type for finite, negative-infinite and unavailable values; decide and justify zero-terminal annualized-return behavior; specify the all-nonfinite range object; freeze rounding mode, scientific notation, signed-zero normalization, convergence comparison and display-tie membership; and provide complete zero fixtures with distribution explicitly zero or positive as separate cases.
- **Disposition:** **OPEN / BLOCKING**.

### B7 - CRITICAL - Output, failure, provenance and transport contracts are not exact enough to implement independently

- **Location:** sections 3 and 9-10, lines 26-36 and 169-195; R1-R3 and R13-R16, lines 201-216.
- **Counterexample/reason:** only top-level names and core status names are listed. There is no closed schema for Capabilities, Evaluation, Artifact, validation boundaries, numeric rows or unavailable fields; no exhaustive finding-code/pointer/status table; no stage precedence/aggregation/hash/provenance availability matrix; no exact input-file/CLI/stdout failure contract; and no exact Content-Type/Content-Encoding grammar. `413` and `415` are mentioned without closed core codes. The source manifest does not exist; line 185 says it will be pinned after freeze, while R14 requires mutation of every manifest member. The artifact hash exclusion and canonical JSON rules are only references, not an exact new-slice contract.
- **Required correction:** before freeze, specify the complete Capabilities/Evaluation/Artifact and result row schemas, tagged numbers, findings, stages, precedence, suppression, HTTP status and CLI exit table, media grammar, file/output errors, canonical JSON, hash inclusion/exclusion, runtime/Git provenance, source manifest and loaded-versus-disk/pre-emission checks. Pin the exact manifest in the reviewed design; do not let implementation choose it after freeze. Include exact example bytes and failure objects.
- **Disposition:** **OPEN / BLOCKING**.

### B8 - HIGH - R1-R16 and maximum/resource behavior are goals, not independently decidable oracles

- **Location:** section 11 lines 197-218.
- **Counterexample/reason:** R1 asks for exact boundaries without concrete raw constructions; R4-R12 name case families but provide no complete BASE bundle or exact expected row objects; R13 names private seams without defining them; R14 lacks the manifest; R16 lacks exact example/artifact/rendered expectations. The maximum fixture lists dimensions but no exact maximum text/numeric construction, cell counts, expected Evaluation, serialized byte caps, resource failure statuses or test seam. Line 218 explicitly says fixed limits must be set before freeze, confirming the draft has not met its own gate.
- **Required correction:** add a complete canonical BASE builder and exact independent expected outputs; separate every invalid case so it cannot mask a valid assertion; define a complete MAX builder, exact row/cell counts and canonical-byte oracle; set fixed raw/Evaluation/Artifact byte limits and boundary helpers; define bounded algorithmic work, fixed failure codes/null behavior, and portable resource reporting. Runtime and peak-memory ceilings may be reference-environment acceptance values, but they cannot be selected after observing implementation behavior.
- **Disposition:** **OPEN / BLOCKING**.

## R1-R16 disposition

| Item | Disposition | Independent review reason |
|---|---|---|
| R1 | **CHANGE REQUIRED** | Parser principles are reusable, but exact raw constructions, media grammar, stage precedence and closed failures are absent under B7/B8. |
| R2 | **CHANGE REQUIRED** | Input shapes are mostly enumerated, but set ordering is contradictory and exact finding codes/pointers are not frozen (B5/B7). |
| R3 | **CHANGE REQUIRED** | No-missing-as-zero and malformed-present precedence are sound; hash/provenance/finding aggregation by stage is not exact (B7/B8). |
| R4 | **CHANGE REQUIRED** | The rational equation is clear, but accounting/share-period basis, exact fixture and failure pointers are not (B1/B8). |
| R5 | **CHANGE REQUIRED** | Factor algebra reproduces, but the distribution clock and terminal-equivalent return label are unresolved (B2/B6). |
| R6 | **CHANGE REQUIRED** | Formula-channel use-once is testable; economic buyback/distribution/capital-allocation nonduplication is not established (B2). |
| R7 | **CHANGE REQUIRED** | Zero-price algebra is partly clear, but distribution-positive variants, finite `-1` versus unavailable CAGR and tagged outputs conflict or are missing (B6). |
| R8 | **CHANGE REQUIRED** | Supplied joint scenario IDs are the right boundary, but permutation acceptance contradicts canonical-order rejection and no exact complete fixture is supplied (B5/B8). |
| R9 | **CHANGE REQUIRED** | Shrinkage arithmetic is clear; prior components and alpha target are not disjoint, so the hierarchy has two valid results for the same named inputs (B3). |
| R10 | **CHANGE REQUIRED** | Signed subtraction is clear, but active-precision equality, public rounding and unavailable objects are not frozen (B6/B7). |
| R11 | **CHANGE REQUIRED** | Min/max intent is clear; all-nonfinite ranges and displayed-tie membership are undefined (B6). |
| R12 | **CHANGE REQUIRED** | Forbidden role tokens are listed, but economic coverage, overlap groups, derived dependencies and role ordering do not close double counting (B4). |
| R13 | **CHANGE REQUIRED** | Dual precision is a useful guard, but exact numeric encoding, convergence test, seams and failure Evaluation are missing (B6-B8). |
| R14 | **CHANGE REQUIRED** | Canonical permutation rules conflict and the source manifest/canonical artifact contract is absent (B5/B7). |
| R15 | **READY AFTER CORRECTION** | DB/network-free/no-promotion evidence is a valid scoped acceptance item. Retain disposable databases and exact existing denial/readiness assertions; it cannot cure B1-B8. |
| R16 | **CHANGE REQUIRED** | Browser behaviors are appropriate, but exact example, result, Artifact, error and download contracts depend on B6-B8. |

## Re-review gate

A corrected revision may be reconsidered only when all B1-B8 dispositions are closed in the design itself. The re-review must receive:

1. the new exact raw design SHA-256;
2. explicit scope wording that distinguishes a terminal synthetic identity from the complete Policy Economic Return Bridge;
3. frozen FCFE/share/distribution/buyback/prior and ledger semantics;
4. a contradiction-free wire/canonical ordering table;
5. closed numeric, output, failure, provenance and transport schemas;
6. complete BASE/MAX fixtures and exact independent R1-R16 oracles; and
7. fixed serialized and algorithmic resource bounds selected before implementation.

Only a later independent `PASS FOR SCOPED DECISION FREEZE` tied to that new hash can authorize Astra to record a scoped ADR. Green documentation checks do not validate the model, and a design PASS would still not authorize implementation until the exact freeze is recorded.

## Status boundaries and preserved state

This review does not alter ADR-0018 or any accepted engineering status. It does not validate or approve a forecast, expected return, probability distribution, FCFE basis, provider/PIT truth, security identity, calibration, `U_objective`, `U_risk`, `S_stress`, decision margin, Risk Budget, optimizer, ranking, action, OOS or shadow result.

The following remain literal and controlling:

- `RISK BUDGET NOT APPROVED`;
- applicable forecast/model/provider/PIT/calibration/risk/OOS items `NOT VERIFIED`;
- `SHADOW VALIDATION NOT PASSED`;
- `NOT PRODUCTION READY`.

No Production-readiness item is promoted. No research trial occurred. No decision freeze or implementation authorization exists for `RESEARCH-RETURN-BRIDGE-LAB-V1`.

## Commands and evidence

- `Get-FileHash -Algorithm SHA256 OPTIVEST_AI_POLICY_V10.md, docs\RESEARCH_RETURN_BRIDGE_DESIGN.md` -> Policy and reviewed-design hashes above.
- `git branch --show-current` -> `main`.
- `git rev-parse HEAD` -> failed because the repository has no commit; recorded state remains `UNBORN`.
- `git status --short` -> all project root paths remain untracked; no commit/remote inferred.
- Independent Python `Decimal` calculations reproduced the distribution-clock and prior-additivity counterexamples recorded above.
- Review-only inspection covered the complete selected Policy, project instructions, START_HERE, current HANDOFF block, DECISIONS, INITIAL_DESIGN, relevant accepted wealth-lab sections and the complete draft.

Tests: no application/model test was run because this is a design review and implementation is prohibited. Validation result: `DESIGN CHANGE REQUIRED`.

---

## Revision 2 independent re-review — controlling disposition (2026-09-21)

Reviewed correction: `docs/RESEARCH_RETURN_BRIDGE_DESIGN_REV2.md`, raw SHA-256 `1D505E1FC643A6EE8509EC2381BDB73B23A4D56ADF2BBF907399151AD7BD491C`.

Comparison baseline: this review before this section had raw SHA-256 `418E4D87745F8C974881F918CCA00C5426D6A9EE9EFDD0C7C0B59C388B058B5F`; selected Policy remains `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.

### Verdict

**DESIGN CHANGE REQUIRED**

Revision 2 materially improves draft 1 and closes the economic-semantic core of B1-B6: it narrows the claim to a terminal identity, freezes the FCFE/share/distribution basis, makes prior components incremental, disclaims economic overlap validation, resolves semantic-set ordering, and defines coherent zero/nonfinite/range representations. It also fixes the manifest member list and serialized size ceilings.

It is still not ready for an exact-hash scoped decision freeze. B7 and B8 remain open because the public wire contract is not actually closed and the exact BASE/MAX/R1-R16 oracles cannot be derived uniquely from the reviewed bytes. This is implementation-significant, not cosmetic: two incompatible implementations can satisfy revision 2 while emitting different statuses, result fields, provenance hashes and canonical artifacts.

No implementation or ADR freeze is authorized from revision 2.

### Independent arithmetic and boundary reproduction

Independent standard-library `Fraction`/`Decimal` calculations, without production helpers, reproduced the intended core:

- BASE start FCFE/share = `10`; start price = `100`.
- Prior = `.02 + .03 + .01 + (.5 * .04 + .5 * 0) = .08`.
- FLAT identity log/rate = zero; disagreement = `-0.08`.
- GROWTH log = `ln(2)/7 = 0.0990210257942779013453...`; annualized holder rate = `0.1040895136738123376495...`; disagreement = `0.0190210257942779013453...`.
- Exact 40-significant-digit public strings under the stated formatting rule are `9.902102579427790134531887449402522401079e-2`, `1.040895136738123376495053876233447213253e-1`, and `1.902102579427790134531887449402522401079e-2` respectively.
- Zero holder value consistently yields factor `0e+0`, simple/terminal-equivalent annualized holder rate `-1.000000000000000000000000000000000000000e+0`, and negative-infinite log. Zero revenue plus terminal distribution 10 yields factor `.1`, log `-0.3289407275705779548597...`, and annualized holder rate `-0.2803143269988479800712...`, so it is correctly not zero-terminal.
- MAX arithmetic counts reproduce as 32 identity rows + 4 prior rows + 32 disagreements + 4 ranges + 12 registry rows = 84 rows, with 32 identity evaluations and no asset-scenario cross-product beyond the supplied 32 rows.
- Serialized ceilings reproduce as 4,194,304 Evaluation bytes and 5,242,880 Artifact bytes, a difference of 1,048,576 bytes. Exact `limit`/`limit+1` seam behavior is decidable.

The semantic-set permutation rule is now internally consistent: sorting by semantic ID can make permutations identical while retaining original wire indices for diagnostics. However, no unique full BASE canonical byte string can be constructed because required literal fields and container/output shapes remain unspecified below.

### B1-B8 closure disposition

| Draft-1 finding | Revision-2 disposition | Independent reason |
|---|---|---|
| B1 scope/FCFE basis | **CLOSED** | Lines 7-30 narrow the claim and fix period, FCFE, share, holder, distribution, debt and reinvestment semantics while explicitly denying Policy section 18 item 8 progress. |
| B2 distribution/buyback | **CLOSED FOR THE NARROW MECHANICAL CLAIM** | Lines 21-27 and 54 fix terminal-only non-repurchase distributions, continuous non-tendering holder, net share-count channel and `capital_allocation_coherence=NOT VERIFIED`. No financing-coherence claim remains. |
| B3 prior additivity/shrinkage | **CLOSED** | Lines 56-67 define a USD nominal pre-tax incremental hierarchy and an alpha prior excluding predecessor components. The `.16` versus `.11` ambiguity is removed. |
| B4 ledger overlap | **CLOSED BY NARROWING** | Lines 97-116 rename the construct a mechanical coverage registry, split all prior inputs, fix one-to-one coverage/dependencies and retain `ledger_economic_overlap_status=NOT VERIFIED`. |
| B5 canonical order | **CLOSED FOR INPUT SETS** | Lines 32-40 accept arbitrary wire order, preserve wire pointers and sort semantic sets only in canonical identity. The prior accept/reject contradiction is removed. Public result-array ordering remains part of B7. |
| B6 zero/nonfinite/ties/ranges | **CLOSED AT THE SEMANTIC LEVEL** | Lines 89-95 define tagged values, finite `-1`, negative infinity, positive distributions, empty-finite-set ranges, rounding and public-string tie membership. Exact tie fixtures remain missing under B8. |
| B7 public/failure/provenance contract | **OPEN / BLOCKING** | Lines 118-146 name containers and codes but do not define enough nested shapes, status mappings or hash inputs to produce one implementation-independent payload. See C1. |
| B8 exact R/MAX/resource oracles | **OPEN / BLOCKING** | Lines 148-160 give arithmetic summaries, not a complete BASE/MAX builder and exact wire/output oracles. The design itself delegates C(BASE) construction to the reviewer despite leaving required literals unspecified. See C2. |

### C1 - CRITICAL - Evaluation, result, status and provenance remain non-unique

- **Location:** revision 2 sections 7-8, lines 118-146 and 160.
- **Counterexample/reason:** for a validly decoded asset with inconsistent start price, the finding is `START_BRIDGE_INCONSISTENT`, but no closed Evaluation status enumeration or code-to-status table says whether `status` is `INVALID_INPUT`, `START_BRIDGE_INCONSISTENT`, or another literal. The same ambiguity exists for missing values, source changes, size failures and CLI acquisition errors. `validation_boundaries` has prose values but no exact closed object keys. `identity_rows`, `prior_rows`, `disagreements`, `scenario_ranges` and `coverage_registry` have no row schemas, field names or array ordering. `Capabilities` lists top-level keys but not the nested shapes/values. `source_manifest` has no declared representation; `source_manifest_sha256` and `source_tree_sha256` do not specify whether they hash path strings, path/hash records, joined bytes or canonical JSON. `git_commit` nullability by Git state is not specified. As a result, two artifacts with different bytes and semantics can both claim conformance.
- **Required correction:** freeze complete closed JSON schemas for Capabilities, Evaluation, every result row, validation boundaries, provenance, Artifact and every unavailable/failure payload. Enumerate every Evaluation status and map each finding/stage to status, HTTP code, CLI exit, hash/provenance availability and aggregation/suppression. Define deterministic output-array order. Define exact manifest record shape, individual-file hash representation, manifest/tree combination algorithms, Git null/state rules and artifact canonicalization. Include decoder-code precedence inside the decoder stage rather than only stage-level precedence.
- **Disposition:** **OPEN / BLOCKING**.

### C2 - HIGH - BASE/MAX and R1-R16 still lack complete independent wire oracles

- **Location:** revision 2 lines 148-160.
- **Counterexample/reason:** BASE does not fix `title`, `rationale`, asset/scenario `definition` strings, exact scenario IDs, the uncertainty-ledger container shape, registry `description` values, or the complete accounting/mandate wire object. The single sentence `Fixed display text is ...` does not assign that text to every required field. Therefore `C(BASE)` has no unique length or SHA-256 and the reviewer cannot honestly record one. MAX likewise lacks exact asset IDs/start records, scenario IDs/definitions, registry descriptions and a full Bundle. The required below/at-40-digit tie cases provide no exact input values. R13 does not specify exact injected fault Evaluation objects. R14 requests canonical Unicode and every manifest mutation without an exact Unicode input/output byte oracle or manifest hash construction. R16 cannot verify structured rendering against absent exact result schemas.
- **Required correction:** include either literal canonical BASE/MAX JSON bytes or complete builders that assign every required key/value/string/ID and exact registry row. Record the independently checkable canonical input byte length/SHA-256. Provide complete expected Evaluation/result objects for BASE, zero, distribution, shrinkage, range/tie and MAX cases; exact values on both sides of the tie boundary; exact private-seam failure objects; a literal Unicode canonicalization oracle; and explicit expected code/path/status/hash/provenance for every R1-R16 negative. Tests may construct fixtures, but implementer-selected text or shapes cannot determine the reviewed artifact.
- **Disposition:** **OPEN / BLOCKING**.

### C3 - MEDIUM - The performance ceiling has no reproducible measurement protocol

- **Location:** revision 2 line 158.
- **Counterexample/reason:** `<=10 seconds` and `<=256 MiB traced peak` are fixed numbers, but the reference runtime/command, warm/cold process rule, number of repetitions and meaning of "traced" are unspecified. `tracemalloc` peak, process RSS and job-object peak can differ materially while all are plausible readings. This cannot be independently PASS/FAIL reproduced.
- **Required correction:** specify the reference command/process isolation, Python/runtime class, timing boundary, repetition rule and exact memory instrument. Alternatively make time/memory measured diagnostic evidence while retaining the already-fixed algorithmic and serialized-byte limits as normative gates.
- **Disposition:** **OPEN; include in B8 correction**.

### R1-R16 revision-2 disposition

| Item | Disposition | Independent reason |
|---|---|---|
| R1 | **CHANGE REQUIRED** | Boundary constructions improve, but decoder-code precedence and exact failure Evaluation/status/hash/provenance mappings remain open under C1. |
| R2 | **CHANGE REQUIRED** | Permutation semantics are fixed, but the uncertainty-ledger/container and exact finding/output shapes are not fully specified. |
| R3 | **CHANGE REQUIRED** | Missing wrappers and stage position are clear; exact multi-finding payload, Evaluation status and hash/provenance behavior are not. |
| R4 | **CLOSED FOR FREEZE AFTER C1/C2** | Exact rational start equations, positive margin and asset-pointer failure are coherent; the full fixture/payload must still be supplied. |
| R5 | **CLOSED FOR FREEZE AFTER C1/C2** | Terminal identity arithmetic and labels independently reproduce. |
| R6 | **CLOSED FOR FREEZE AFTER C1/C2** | The claim is correctly limited to mechanical field use-once with economic coherence explicitly unverified. |
| R7 | **CLOSED FOR FREEZE AFTER C1/C2** | Zero and positive-distribution arithmetic and tagged semantics reproduce. |
| R8 | **CLOSED FOR FREEZE AFTER C1/C2** | Joint supplied scenario rows and the 32-row MAX ceiling prohibit cross-product generation. |
| R9 | **CLOSED FOR FREEZE AFTER C1/C2** | Incremental hierarchy and weights 0/1/.5 are mathematically decidable. |
| R10 | **CHANGE REQUIRED** | Classification rule is closed, but exact boundary inputs and complete disagreement-row payloads are absent. |
| R11 | **CHANGE REQUIRED** | Empty-range semantics are closed, but exact public-tie fixtures and range-row bytes are absent. |
| R12 | **CHANGE REQUIRED** | Registry memberships are materially improved; exact row/container bytes, description literals and failure payloads remain unspecified. |
| R13 | **CHANGE REQUIRED** | Precision, rounding and seam names are fixed; injected-fault payload/status/hash/provenance oracles are not. |
| R14 | **CHANGE REQUIRED** | Manifest path list is fixed, but canonical BASE/Unicode bytes and manifest/tree hash construction are not. |
| R15 | **CLOSED FOR FREEZE** | Stateless DB/network/trial isolation and non-promotion remain a valid, independently testable boundary. |
| R16 | **CHANGE REQUIRED** | UI behaviors are appropriate, but exact structured/result/error/download bytes depend on C1/C2. |

### No-promotion and contradiction check

No forecast, probability, calibrated uncertainty set, risk feasibility, optimizer, rank, action, OOS, shadow or Production promotion leakage was found. Revision 2 consistently retains `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY`. Scenario jointness, terminal distribution timing, mechanical buyback separation and semantic-set canonicalization no longer contradict one another.

The remaining rejection is specification closure only. It is not a model-validation failure and does not reopen ADR-0018 or any accepted artifact.

### Exact next step

Astra should issue revision 3 that changes only B7/B8 closure: complete public/failure/provenance schemas, exact BASE/MAX/Unicode/tie/fault fixtures and a reproducible resource measurement contract. Preserve the corrected B1-B6 semantics and all non-production boundaries. A new raw design hash requires one independent re-review; Terra remains undispatched and DECISIONS remains D0010 until a later exact-hash `PASS FOR SCOPED DECISION FREEZE`.

Re-review commands/evidence: exact three-file SHA-256 verification; complete revision-2 read; independent `Fraction`/dual-precision `Decimal` arithmetic for BASE/prior/zero/positive-distribution; independent MAX row/operation count and serialized-limit arithmetic; current `main / HEAD UNBORN` verification. No application/model/database/provider/trial test was run or required for this design-only re-review.
