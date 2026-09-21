# Research return-bridge laboratory — RESEARCH-RETURN-BRIDGE-LAB-V1, draft 1

Date: 2026-09-20, Asia/Tokyo. Owner: Astra. Status: `DRAFT / SOL INDEPENDENT REVIEW REQUIRED / NOT FROZEN`. Authority: selected `OPTIVEST_AI_POLICY_V10.md`, raw SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; ADR-0012 provisional Generic Research boundary; accepted ADR-0018 accounting kernel. This document does not authorize implementation.

## 1. Outcome and narrow boundary

Build a stateless, DB-free laboratory that evaluates **supplied synthetic economic-return and statistical-prior hypotheses**. It closes only four testable contracts that sit immediately above the accepted wealth-accounting kernel:

1. an explicit FCFE-per-share Economic Return Bridge;
2. a supplied hierarchical statistical/economic prior diagnostic;
3. a visible disagreement calculation between those two layers; and
4. a closed uncertainty ledger that prevents one stated source from silently occupying incompatible roles.

The lab does not learn from data, choose probabilities, calibrate a forecast, construct `U_objective` or `U_risk`, define `S_stress`, generate monthly paths, optimize holdings, apply a Risk Budget, rank a security, emit an action, or write a decision snapshot. Its UI must state `SYNTHETIC RETURN-BRIDGE LAB — NOT A FORECAST OR INVESTMENT MODEL`.

This is deliberately not an integrated Phase 2 model. The accepted wealth lab remains unchanged and receives no output directly from this slice: terminal bridge hypotheses do not define the 84-month joint paths, cash timing, drawdowns or recovery episodes required by ADR-0018. A later reviewed integration must supply those missing path semantics and empirical calibration.

## 2. Fixed research assumptions and non-goals

The contract is fixed to the ADR-0012 synthetic subset: seven-year horizon, USD, nominal, pre-tax, no external flows. Inputs describe invented companies and invented market priors only. IDs cannot be real tickers, CIKs, URLs, provider IDs, evidence IDs, account IDs or personal holdings.

Non-goals: issuer facts; provider/network access; security-master linkage; PIT claims; historical fitting; market-implied extraction; analyst estimates; real FX; real tax; debt/enterprise-value bridge; accounting normalization; probability estimation; confidence calibration; scenario interpolation; Monte Carlo; path generation; cost, liquidity or capacity estimation; risk feasibility; permanent-loss probabilities; optimizer/ranking/action; persistence; OOS; shadow; Production.

The lab may prove arithmetic and closed-contract behavior only. Terms such as expected return, calibrated probability, forecast confidence, fair value, target price, upside, alpha edge, BUY, HOLD, weight and optimal are prohibited in result labels.

## 3. Public contract and bounded raw input

The single core entry is `evaluate_return_bridge_bytes(raw: bytes)`. HTTP and CLI pass the original bytes. Mapping/string/bytearray input is rejected. Evaluation is stateless and cannot access the database, environment-provided market data or network.

Use the accepted ADR-0018 raw-wire conventions unless this design explicitly narrows them: strict UTF-8 JSON without BOM; duplicate keys, non-standard constants and lone surrogates rejected; closed objects at every depth; RFC-6901 findings; no coercion/defaulting; deterministic canonical JSON; raw input at most 1,048,576 bytes, depth at most 12 and nodes at most 20,000. These limits are independent contract values and must not be obtained by importing private wealth-lab parser state.

`D` is a decimal string matching `(0|[1-9][0-9]{0,11})(\.[0-9]{1,9})?`, canonicalized by removing fractional trailing zeroes and the trailing decimal point. `SD` adds an optional leading minus and otherwise follows `D`; negative zero canonicalizes to `0`. JSON numbers, booleans, signs in `D`, exponent syntax, whitespace, NaN and Infinity are invalid. Decimal syntax is an engineering input convention, not a precision claim.

Every numeric domain field is `V = D | SD | {state, reason}` as specified by its field definition. Allowed states are `MISSING`, `UNKNOWN`, `STALE`, `CONFLICTING`, `UNAVAILABLE_PIT`, `NOT_APPLICABLE`. Applicable fields reject `NOT_APPLICABLE`; any other state blocks the complete evaluation as `INPUT_INCOMPLETE` without numeric substitution. Malformed present values take precedence over incomplete-state reporting.

IDs are ASCII `[A-Z][A-Z0-9_]{0,31}` with the prefixes below. Display text is inert trimmed Unicode of 1–512 characters. No HTML interpretation is permitted.

## 4. Closed Bundle

`Bundle = {schema_version, origin, title, rationale, mandate_assumption, assets, scenarios, statistical_prior, uncertainty_ledger}`.

- `schema_version = RESEARCH_RETURN_BRIDGE_LAB_V1`.
- `origin = SYNTHETIC_HYPOTHESIS`.
- `mandate_assumption = {reference, horizon_years, base_currency, nominal_real, tax_treatment, external_flows}` with exact values `ADR-0012_SYNTHETIC_SUBSET`, `7`, `USD`, `NOMINAL`, `PRE_TAX`, `SELF_FINANCING_NONE`.
- `assets`: 1–4 unique `Asset` records ordered canonically by `asset_id`.
- `scenarios`: 2–8 unique, supplied joint `Scenario` records ordered by `scenario_id`. The lab does not combine asset marginals independently.
- `statistical_prior`: one supplied diagnostic per asset, with no scenario probability or combination rule.
- `uncertainty_ledger`: the closed registry in section 8.

`Asset = {asset_id, kind, definition, start_revenue, start_fcfe_margin, start_shares, start_price, start_price_to_fcfe}`.

- `asset_id` begins `SYN_`; reserved IDs `SYN_CASH` and `SYN_BENCHMARK` are forbidden.
- `kind` is `SYNTHETIC_EQUITY` or `SYNTHETIC_PASSIVE`; at least one equity is required. No look-through or investability inference follows from `SYNTHETIC_PASSIVE`.
- `start_revenue`, `start_shares` and `start_price` are applicable `D > 0`.
- `start_fcfe_margin` is applicable `D` in `[0,1]`.
- `start_price_to_fcfe` is applicable `D > 0`.

The starting bridge must satisfy exactly:

`start_fcfe_per_share = start_revenue * start_fcfe_margin / start_shares`

`start_price = start_fcfe_per_share * start_price_to_fcfe`.

All arithmetic uses exact rationals before any logarithm. A mismatch is `START_BRIDGE_INCONSISTENT`; the lab does not solve for or repair an input.

`Scenario = {scenario_id, definition, assets}`; `scenario_id` begins `SCENARIO_`. Each scenario has exactly one `ScenarioAsset` for every asset and no others. `ScenarioAsset = {asset_id, revenue_gross_factor, ending_fcfe_margin, ending_share_count_factor, ending_price_to_fcfe, cumulative_cash_distribution_per_start_share}`.

- `revenue_gross_factor` is applicable `D >= 0` and means terminal total revenue divided by starting total revenue.
- `ending_fcfe_margin` is applicable `D` in `[0,1]`.
- `ending_share_count_factor` is applicable `D > 0` and means terminal shares divided by starting shares. It is the only dilution/buyback channel in V1.
- `ending_price_to_fcfe` is applicable `D > 0`.
- `cumulative_cash_distribution_per_start_share` is applicable `D >= 0`, paid over the seven-year interval but used only in the terminal-holder-return identity. Timing and reinvestment are deliberately not modeled.

Scenarios are joint labels across assets and economic variables. The contract supplies no probability, ordering, base/bear/bull meaning or severity. A scenario definition may describe a hypothesis but cannot change formulas.

`StatisticalPrior = {assets}` with exactly one `PriorAsset` per asset. `PriorAsset = {asset_id, horizon_years, risk_free_annual_log_return, broad_market_premium_annual_log_return, factor_sector_annual_log_return, company_alpha_raw_annual_log_return, company_alpha_shrinkage_weight, company_alpha_prior_annual_log_return, basis}`.

- `horizon_years` is exactly `7`.
- the five return terms are applicable `SD` in `[-1,1]` and are explicitly supplied annual continuously compounded hypothetical components;
- `company_alpha_shrinkage_weight` is applicable `D` in `[0,1]`;
- `basis = SUPPLIED_SYNTHETIC_LOG_COMPONENTS`.

The lab does not call the supplied values estimates and does not infer a value from asset kind.

## 5. Economic Return Bridge arithmetic

For asset `i` in scenario `s`, with horizon `T=7`:

`revenue_T = start_revenue_i * revenue_gross_factor_si`

`shares_T = start_shares_i * ending_share_count_factor_si`

`fcfe_T = revenue_T * ending_fcfe_margin_si`

`fcfe_per_share_T = fcfe_T / shares_T`

`terminal_price = fcfe_per_share_T * ending_price_to_fcfe_si`

`terminal_holder_value = terminal_price + cumulative_cash_distribution_per_start_share_si`

`terminal_total_return_factor = terminal_holder_value / start_price_i`.

If `terminal_holder_value = 0`, the terminal state is `ZERO`, total return is exactly `-1`, annual log return is negative infinity with reason `ZERO_TERMINAL_HOLDER_VALUE`, and no finite CAGR is fabricated. Otherwise:

`annual_log_return_economic = ln(terminal_total_return_factor) / 7`

`annualized_total_return_economic = exp(annual_log_return_economic) - 1`.

The result exposes a multiplicative bridge, not an additive attribution:

- revenue factor;
- margin factor `ending_fcfe_margin/start_fcfe_margin` when the starting margin is positive;
- per-share factor `1/ending_share_count_factor`;
- valuation factor `ending_price_to_fcfe/start_price_to_fcfe`;
- distribution contribution shown separately as `distribution/start_price`.

When `start_fcfe_margin = 0`, the exact starting consistency equations and positive starting price cannot both hold; therefore such an otherwise syntactically valid asset is `START_BRIDGE_INCONSISTENT`. V1 does not invent a turnaround valuation convention.

The product of the four price factors equals `terminal_price/start_price`; distributions are then added exactly once. Do not add growth, margin, dilution and multiple percentages as if they were independent returns. Do not treat buybacks both as share-count reduction and cash distribution.

## 6. Hierarchical statistical/economic prior diagnostic

For each asset:

`shrunk_company_alpha = w * company_alpha_raw + (1-w) * company_alpha_prior`

`annual_log_return_prior = risk_free + broad_market_premium + factor_sector + shrunk_company_alpha`.

This is a supplied arithmetic diagnostic, not a fitted forecast. The result must expose all components, the shrinkage weight and the shrunk alpha. It must not silently shrink the broad-market component because company-specific information is weak.

No terminal price is derived from the prior. No probability distribution is formed. No layer receives precedence and no combined forecast is emitted.

## 7. Layer disagreement and scenario summaries

For every asset/scenario pair with finite economic annual log return:

`layer_disagreement = annual_log_return_economic - annual_log_return_prior`.

This signed value is a diagnostic only. The lab reports `ECONOMIC_ABOVE_PRIOR`, `ECONOMIC_BELOW_PRIOR` or `EQUAL_AT_ACTIVE_PRECISION`; it does not call either layer correct. If the economic value is non-finite, disagreement is unavailable with `NONFINITE_ECONOMIC_LAYER`.

Across supplied scenarios the lab reports the exact minimum and maximum finite economic annual log return for each asset, IDs attaining each displayed value, and whether any scenario is zero-terminal. It does not compute an expectation, quantile, confidence interval, probability-weighted result, robust minimum over `U_objective`, or risk constraint.

## 8. Closed uncertainty ledger

There are exactly nine rows, one for each `source_id` below. Each row is `{source_id, description, primary_role, secondary_roles, overlap_group, status}`.

| source_id | Required primary_role |
|---|---|
| `SOURCE_REVENUE_GROWTH` | `PREDICTIVE_INPUT` |
| `SOURCE_FCFE_MARGIN` | `PREDICTIVE_INPUT` |
| `SOURCE_SHARE_COUNT` | `PREDICTIVE_INPUT` |
| `SOURCE_VALUATION_MULTIPLE` | `PREDICTIVE_INPUT` |
| `SOURCE_CASH_DISTRIBUTION` | `PREDICTIVE_INPUT` |
| `SOURCE_RISK_FREE` | `PRIOR_INPUT` |
| `SOURCE_MARKET_FACTOR` | `PRIOR_INPUT` |
| `SOURCE_COMPANY_ALPHA` | `PRIOR_INPUT` |
| `SOURCE_LAYER_DISAGREEMENT` | `DIAGNOSTIC_ONLY` |

`secondary_roles` is an explicit array drawn from `PREDICTIVE_DISTRIBUTION`, `SHRINKAGE`, `U_OBJECTIVE`, `U_RISK`, `S_STRESS`, `DECISION_MARGIN`, `SIZING`, `DIAGNOSTIC`; `overlap_group` is inert nonempty text; `status` is exactly `SYNTHETIC_UNCALIBRATED`.

V1 permits only these secondary-role assignments:

- `SOURCE_COMPANY_ALPHA` may contain `SHRINKAGE` and `DIAGNOSTIC`;
- `SOURCE_LAYER_DISAGREEMENT` may contain only `DIAGNOSTIC`;
- every other row may contain only `DIAGNOSTIC`.

`U_OBJECTIVE`, `U_RISK`, `S_STRESS`, `DECISION_MARGIN`, `SIZING` and `PREDICTIVE_DISTRIBUTION` are therefore rejected in V1. This is intentional: the lab records that those roles are uncalibrated rather than letting a synthetic hypothesis masquerade as their construction. Duplicate rows, unknown sources/roles, omitted rows, repeated secondary roles and noncanonical ordering are invalid.

## 9. Numerical and canonical output contract

Rational operations remain exact. Natural log and exponential use two independent Decimal evaluations at precision 80 and 120; their canonical 40-significant-digit public values and all classifications must agree or evaluation returns `NUMERICAL_NOT_VERIFIED`. Zero-terminal handling bypasses log/exp and is exact. No clipping or wealth floor is permitted.

Success status is `COMPUTED_SYNTHETIC_RETURN_BRIDGE`. Required top-level output is `{schema_version,status,validation_boundaries,provenance,input_sha256,findings,result}`. `result` contains canonicalized input identity, asset/scenario bridge rows, prior rows, disagreement rows, per-asset scenario ranges, ledger disposition and the literal boundaries:

- `forecast_status = NOT VERIFIED`;
- `calibration_status = NOT VERIFIED`;
- `provider_pit_status = NOT VERIFIED`;
- `risk_feasibility_status = NOT VERIFIED`;
- `optimizer_status = NOT VERIFIED`;
- `oos_status = NOT VERIFIED`;
- `shadow_status = SHADOW VALIDATION NOT PASSED`;
- `risk_budget_status = RISK BUDGET NOT APPROVED`;
- `production_readiness = NOT PRODUCTION READY`.

The success Artifact includes canonical input, Evaluation, exact Policy/design/source-manifest hashes, observed Git state and artifact hash using the same hash-exclusion convention as ADR-0018. The new design and exact new source manifest are independently pinned after freeze; accepted ADR-0018 files are not added to the new manifest unless imported by the implementation.

Findings are deterministically ordered by JSON pointer then code. Decoder/authority failures remain single-root failures. Independently applicable closed-schema and domain findings aggregate without cascading into invalid subtrees. Incomplete states aggregate only after schema/domain validity is established.

## 10. Closed status and transport behavior

Core statuses are `COMPUTED_SYNTHETIC_RETURN_BRIDGE`, `INPUT_INCOMPLETE`, `INVALID_INPUT`, `SOURCE_CHANGED`, `POLICY_MISMATCH`, `DESIGN_MISMATCH`, `NUMERICAL_NOT_VERIFIED`, `INTERNAL_ERROR`. Unknown exceptions fail closed as `INTERNAL_ERROR`; no partial result or Artifact is emitted.

HTTP provides `GET /api/research/return-bridge/capabilities`, `GET /api/research/return-bridge/example`, `POST /api/research/return-bridge/evaluate`, and `GET /return-bridge`. Success is 200; invalid/incomplete input is 422; content contract is 415; size is 413; authority/source/numerical/internal failure is 503. CLI provides `return-bridge capabilities`, `example`, and `evaluate --file`; it is DB-free and network-free.

The UI is a raw JSON editor plus structured safe-DOM result. It must implement stale-result invalidation, one in-flight request, explicit failure, XSS-safe text, local Artifact rehash before Download, rejected/mismatched download disabling, desktop and 390px behavior, and clear non-promotion labels. It must never show ranking, action, target price, expected-return claim or current Risk Budget impact.

## 11. Independent acceptance matrix

Each item requires an independent oracle that does not call the evaluator's private formula helper.

1. **R1 parser bounds and precedence:** exact byte/depth/node boundaries, duplicate pointers, BOM/surrogate/nonfinite/number-vs-string cases, malformed syntax precedence and library/HTTP/CLI parity.
2. **R2 closed grammar:** unknown/missing keys at every shape; ID, literal, range, membership and canonical-order failures; no bool/int or number/string coercion.
3. **R3 incomplete values:** every applicable V slot, deterministic multi-finding aggregation, `NOT_APPLICABLE` rejection, malformed-present precedence and no missing-as-zero.
4. **R4 start consistency:** independently exact consistent case and one-unit-last-decimal mismatches for price, margin, shares and multiple.
5. **R5 economic bridge:** hand-computed flat, growth, margin compression, dilution, buyback, multiple compression and distribution cases; prove factor product and distribution addition exactly once.
6. **R6 no double count:** buyback changes only share-count factor; distribution changes only cash-distribution term; simultaneous case equals the exact formula and no additive percentage shortcut.
7. **R7 zero terminal:** revenue zero and margin zero terminal cases produce exact -100%/negative-infinity semantics; no clipping, finite CAGR or disagreement.
8. **R8 joint scenarios:** correlated and offsetting multi-asset scenario labels remain joint; reordering semantic sets preserves the canonical hash; no cross-product scenario generation.
9. **R9 prior hierarchy:** exact positive/negative alpha shrinkage at weights 0, 1 and an interior rational; market component remains unchanged; no terminal price or probability output.
10. **R10 disagreement:** positive/negative/zero/nonfinite cases and active-precision tie classification; no winner, combination or forecast label.
11. **R11 range diagnostics:** exact min/max IDs, displayed ties, zero-terminal presence and no expectation/quantile/probability fields.
12. **R12 ledger closure:** all allowed role arrays; every forbidden `U_OBJECTIVE/U_RISK/S_STRESS/DECISION_MARGIN/SIZING/PREDICTIVE_DISTRIBUTION` placement; duplicate/unknown/missing/noncanonical rows and roles.
13. **R13 numerical independence:** separately recompute logs/exponentials; force precision disagreement and invariant faults through private test seams; require null result and closed status.
14. **R14 provenance/canonical bytes:** object/set permutation equality, text/numeric semantic changes, Unicode oracle, every manifest-member mutation, Policy/design mismatch, source missing, Git unborn/unavailable, pre-emission recheck for example/capabilities/evaluate.
15. **R15 no-state/no-promotion:** fresh populated SQLite row map byte/logical preservation; provider/readiness/preflight boundaries unchanged; no trial append; no route emits recommendation/weight/approval.
16. **R16 real browser:** desktop/390px load/evaluate/incomplete/zero/stale/in-flight/error/XSS/rehash/download-rejection/structured rendering with genuine browser backend.

The maximum valid fixture uses four assets, eight scenarios and all nine ledger rows. Measure time, peak memory, Evaluation bytes and Artifact bytes; the design review must set fixed limits before freeze rather than accepting host-dependent values after implementation.

## 12. Proposed implementation and change control

Allowed only after Sol PASS and exact-hash ADR freeze: new `optivest/return_bridge.py`, `optivest/return_bridge_api.py`, `optivest/static/return_bridge.js`, `optivest/static/return_bridge.css`, `optivest/fixtures/return_bridge_example.json`, `tests/test_return_bridge.py`; narrow route/CLI registration; README and `.ai` operational records.

Do not change the selected Policy, accepted wealth-lab/risk-editor/provider designs or implementations, models, service, phase2, migrations, dependencies/lock, provider permissions, raw captures, user databases, retained reviewer tests, research ledger or Production register. Do not reuse the wealth-lab name to imply integrated forecast/wealth acceptance.

Required sequence: Astra draft → Sol falsification-first pre-review → Astra correction if needed → exact design/review hash freeze in a new ADR/decision version → Terra implementation → automated evidence → Sol independent post-validation. Material changes to formulas, return basis, data origin, scenario/probability semantics, path generation, uncertainty roles, persistence or output promotion require renewed design review and freeze.

## 13. Gate disposition and next broader work

This draft promotes no Policy §18 item. It supplies no real forecast, provider/PIT evidence, calibration, `U_objective`, `U_risk`, `S_stress`, decision margin, risk limit, optimizer, OOS or shadow result. Existing scoped engineering passes remain intact. Literal states remain `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED`, `NOT PRODUCTION READY`.

After an independently accepted implementation, the next material design still requires admissible PIT historical data; corporate-action/delisting/price lineage; development/validation splits; fitted economic and statistical forecast distributions; dependency construction; calibration and ledger overlap evidence; monthly path semantics; `U_objective/U_risk/S_stress`; risk event/horizon semantics; costs/capacity; optimizer; preregistered locked OOS and shadow. Synthetic arithmetic cannot substitute for those gates.

