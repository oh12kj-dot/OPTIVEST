# Synthetic terminal-return identity laboratory — RESEARCH-RETURN-BRIDGE-LAB-V1, corrected revision 2

Date: 2026-09-21, Asia/Tokyo. Owner: Astra. Status: `CORRECTED DRAFT / SOL INDEPENDENT RE-REVIEW REQUIRED / NOT FROZEN`. Authority: selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, ADR-0012 and accepted ADR-0018. This revision addresses B1-B8 of `docs/reviews/research_return_bridge_pre_review.md`. Draft 1 remains immutable review evidence. No implementation is authorized.

## 1. Scope and fixed basis

This stateless, DB-free lab computes only (a) a supplied-synthetic **terminal FCFE-per-share holder-value identity**, (b) a disjoint supplied hierarchical annual-log prior, (c) their signed disagreement, and (d) a mechanical source-to-field coverage registry. It is not the complete Policy §7 Economic Return Bridge and does not advance §18 item 8. Reinvestment, Incremental ROIC, capital intensity/allocation coherence, financing, empirical forecasts, probabilities, monthly paths, FX, calibration, `U_objective`, `U_risk`, `S_stress`, risk feasibility, optimizer, ranking, action, persistence, OOS and shadow remain absent or `NOT VERIFIED`.

UI literal: `SYNTHETIC TERMINAL-RETURN IDENTITY LAB — NOT A FORECAST OR INVESTMENT MODEL`.

Every Bundle fixes seven years, USD nominal, pre-tax, no external flows and this exact `accounting_basis`:

```text
start_period=SYNTHETIC_ANNUAL_RUN_RATE_AT_T0
terminal_period=SYNTHETIC_ANNUAL_RUN_RATE_AT_T7
revenue_basis=CONSOLIDATED_CONTINUING_OPERATIONS_SYNTHETIC
fcfe_basis=CASH_AVAILABLE_TO_COMMON_EQUITY_AFTER_INTEREST_AND_NET_DEBT_CASH_FLOW_SYNTHETIC
nonrecurring_treatment=EXCLUDED_FROM_BOTH_PERIODS_SYNTHETIC
share_basis=POINT_IN_TIME_FULLY_DILUTED_COMMON_EQUIVALENT
per_share_holder=CONTINUOUS_NON_TENDERING_START_SHARE
distribution_clock=ALL_NON_REPURCHASE_CASH_DISTRIBUTIONS_AT_TERMINAL_EVENT
distribution_reinvestment=NONE
repurchase_tender_proceeds=EXCLUDED
share_count_channel=NET_FULLY_DILUTED_EFFECT_OF_ISSUANCE_SBC_CONVERSION_AND_REPURCHASE
debt_enterprise_value_bridge=NOT_MODELED
reinvestment_incremental_roic=NOT_MODELED
capital_allocation_coherence=NOT_MODELED
```

Different periods, currencies, share denominators, FCFE definitions or distribution clocks are invalid, not alternate interpretations. Inputs are invented `SYN_` assets only; no real ticker, provider, evidence, account or personal field exists.

## 2. Raw wire and canonical identity

Core entry: `evaluate_terminal_identity_bytes(raw: bytes)`. Other argument types fail `TYPE_INVALID` at root. Strict UTF-8 JSON without BOM; duplicate keys, nonstandard constants, lone surrogates and unknown fields fail. No coercion/defaulting. Raw maximum 1,048,576 bytes inclusive, root depth 12, nodes 20,000. Findings use original RFC-6901 wire indices.

`D` is `(0|[1-9][0-9]{0,11})(\.[0-9]{1,9})?`; `SD` adds an optional minus. No JSON number/bool/exponent/plus/whitespace/nonfinite. Canonicalization trims fractional zeroes and maps negative zero to zero. Applicable missing wrapper is `{state,reason}` with `MISSING|UNKNOWN|STALE|CONFLICTING|UNAVAILABLE_PIT`; `NOT_APPLICABLE` is invalid.

Every array is a **semantic set**: assets, scenarios, scenario assets, prior assets, registry rows, roles, coverage and dependencies accept arbitrary wire order, retain wire pointers for findings, and canonicalize by their semantic ID (roles by closed role order, coverage by pointer). Permutations have identical canonical bytes/hash. There is no noncanonical-order failure.

Canonical JSON sorts object keys by Unicode scalar, uses compact UTF-8, lowercase `\u00xx` only for controls, standard quote/backslash escapes, literal slash/other Unicode, and no NaN.

## 3. Closed Bundle

`Bundle={schema_version,origin,title,rationale,mandate_assumption,accounting_basis,assets,scenarios,statistical_prior,uncertainty_ledger}`. Schema/origin are `RESEARCH_RETURN_BRIDGE_LAB_V1` / `SYNTHETIC_HYPOTHESIS`. Mandate is exactly `{reference:"ADR-0012_SYNTHETIC_SUBSET",horizon_years:7,base_currency:"USD",nominal_real:"NOMINAL",tax_treatment:"PRE_TAX",external_flows:"SELF_FINANCING_NONE"}`.

`Asset={asset_id,kind,definition,start_revenue,start_fcfe_margin,start_shares,start_price,start_price_to_fcfe}`; 1-4 unique `SYN_` IDs, excluding `SYN_CASH/SYN_BENCHMARK`; kind equity/passive, at least one equity. Revenue/shares/price/multiple are `D>0`, margin `D` in `(0,1]`. Require exactly:

`start_fcfe_per_share=start_revenue*start_fcfe_margin/start_shares`

`start_price=start_fcfe_per_share*start_price_to_fcfe`.

Mismatch is `START_BRIDGE_INCONSISTENT` at the asset pointer; nothing is repaired.

`Scenario={scenario_id,definition,assets}`; 2-8 unique `SCENARIO_` IDs and exactly one row per asset. `ScenarioAsset={asset_id,revenue_gross_factor,ending_fcfe_margin,ending_share_count_factor,ending_price_to_fcfe,terminal_nonrepurchase_cash_distribution_per_start_share}`. Domains are respectively `D>=0`, `[0,1]`, `D>0`, `D>0`, `D>=0`. Distribution occurs only at T7, earns no interim return and excludes repurchase/tender proceeds. Share factor is the sole issuance/SBC/conversion/repurchase channel. The lab proves only mechanical use-once, never economic financeability; `capital_allocation_coherence=NOT VERIFIED`.

`StatisticalPrior={basis,assets}`; basis is `USD_NOMINAL_PRETAX_ANNUAL_LOG_INCREMENTAL_HIERARCHY_V1`. One row per asset:

```text
{asset_id,horizon_years,risk_free_base_annual_log_return,
 broad_market_incremental_annual_log_spread,
 factor_sector_incremental_annual_log_spread,
 company_alpha_raw_incremental_annual_log_spread,
 company_alpha_shrinkage_weight,
 company_alpha_prior_incremental_annual_log_spread,alpha_prior_reference}
```

Horizon is 7; returns/spreads are `SD` in `[-1,1]`; weight `[0,1]`; reference is `SYNTHETIC_COMPARABLE_COMPANY_RESIDUAL_EXCLUDING_MARKET_AND_FACTOR_SECTOR_V1`. Each spread is explicitly incremental/non-overlapping relative to preceding components; alpha raw/prior exclude risk-free, market and factor/sector. Alternate basis/reference is `LITERAL_INVALID`.

## 4. Exact arithmetic

For asset i/scenario s:

```text
revenue_T=start_revenue_i*revenue_gross_factor_si
shares_T=start_shares_i*ending_share_count_factor_si
fcfe_T=revenue_T*ending_fcfe_margin_si
fcfe_per_share_T=fcfe_T/shares_T
terminal_price=fcfe_per_share_T*ending_price_to_fcfe_si
terminal_holder_value=terminal_price+terminal_nonrepurchase_cash_distribution_per_start_share_si
terminal_holder_factor=terminal_holder_value/start_price_i
```

For positive holder value: `terminal_equivalent_annual_log_rate=ln(factor)/7`; `terminal_equivalent_annualized_holder_rate=exp(log_rate)-1`. These mandatory names are not TWR, CAGR, expected return, fair value or target price. Price factor is revenue x margin x inverse-share x multiple; distribution/start price is added once.

Prior: `shrunk_alpha=w*raw_alpha+(1-w)*alpha_prior`; `annual_log_prior=risk_free_base+broad_market_incremental+factor_sector_incremental+shrunk_alpha`. No component contains a predecessor. No probability, price or combined forecast is produced.

For finite identity log, disagreement is identity log minus prior, classified `IDENTITY_ABOVE_PRIOR|IDENTITY_BELOW_PRIOR|EQUAL_AT_PUBLIC_PRECISION`; otherwise unavailable. Neither layer wins.

## 5. Closed numeric outputs

Public numeric is exactly `{state:"FINITE",value:<string>,reason:null}`, `{state:"NEGATIVE_INFINITY",value:null,reason:"ZERO_TERMINAL_HOLDER_VALUE"}`, or `{state:"UNAVAILABLE",value:null,reason:<closed reason>}`. Exact rationals precede Decimal ln/exp at precision 80 and 120 with ROUND_HALF_EVEN. Public finite values use 40 significant digits: `[-]d.` plus 39 digits, lowercase `e`, signed exponent without leading zero; zero is `0e+0`. Both precisions must round identically or status is `NUMERICAL_NOT_VERIFIED`.

At zero holder value: factor is finite zero; simple return and terminal-equivalent annualized holder rate are finite `-1.000000000000000000000000000000000000000e+0`; log is negative infinity. Revenue zero plus positive distribution remains finite positive-holder.

Per-asset range is either finite with min/max tagged values, public-tie ID arrays and zero-terminal IDs, or `{state:"UNAVAILABLE",reason:"NO_FINITE_SCENARIOS",minimum:null,minimum_scenario_ids:[],maximum:null,maximum_scenario_ids:[],zero_terminal_scenario_ids:[...]}`. Min/max use unrounded values; membership and equality classification use identical 40-digit public strings.

## 6. Mechanical source-coverage registry

This is not an economic overlap validator; `ledger_economic_overlap_status=NOT VERIFIED`. Exactly 12 rows have `{source_id,description,primary_role,secondary_roles,overlap_group,coverage,derived_dependencies,status}` and `status=SYNTHETIC_UNCALIBRATED`.

| source | primary | group | exact coverage |
|---|---|---|---|
| SOURCE_REVENUE_GROWTH | PREDICTIVE_INPUT | ECONOMIC_REVENUE | /scenarios/*/assets/*/revenue_gross_factor |
| SOURCE_FCFE_MARGIN | PREDICTIVE_INPUT | ECONOMIC_MARGIN | /scenarios/*/assets/*/ending_fcfe_margin |
| SOURCE_SHARE_COUNT | PREDICTIVE_INPUT | ECONOMIC_SHARE_COUNT | /scenarios/*/assets/*/ending_share_count_factor |
| SOURCE_VALUATION_MULTIPLE | PREDICTIVE_INPUT | ECONOMIC_VALUATION | /scenarios/*/assets/*/ending_price_to_fcfe |
| SOURCE_CASH_DISTRIBUTION | PREDICTIVE_INPUT | ECONOMIC_DISTRIBUTION | /scenarios/*/assets/*/terminal_nonrepurchase_cash_distribution_per_start_share |
| SOURCE_RISK_FREE | PRIOR_INPUT | PRIOR_RISK_FREE | /statistical_prior/assets/*/risk_free_base_annual_log_return |
| SOURCE_BROAD_MARKET | PRIOR_INPUT | PRIOR_BROAD_MARKET | /statistical_prior/assets/*/broad_market_incremental_annual_log_spread |
| SOURCE_FACTOR_SECTOR | PRIOR_INPUT | PRIOR_FACTOR_SECTOR | /statistical_prior/assets/*/factor_sector_incremental_annual_log_spread |
| SOURCE_ALPHA_RAW | PRIOR_INPUT | PRIOR_ALPHA_RAW | /statistical_prior/assets/*/company_alpha_raw_incremental_annual_log_spread |
| SOURCE_ALPHA_PRIOR | PRIOR_INPUT | PRIOR_ALPHA_PRIOR | /statistical_prior/assets/*/company_alpha_prior_incremental_annual_log_spread |
| SOURCE_ALPHA_WEIGHT | PRIOR_INPUT | PRIOR_ALPHA_WEIGHT | /statistical_prior/assets/*/company_alpha_shrinkage_weight |
| SOURCE_LAYER_DISAGREEMENT | DIAGNOSTIC_ONLY | DERIVED_LAYER_DISAGREEMENT | /result/disagreements/* |

Input rows require `[DIAGNOSTIC]`, except alpha raw/prior/weight require `[SHRINKAGE,DIAGNOSTIC]`; derived row requires `[DIAGNOSTIC]`. Non-derived dependencies are empty; derived dependencies are all preceding 11 IDs. `PREDICTIVE_DISTRIBUTION,U_OBJECTIVE,U_RISK,S_STRESS,DECISION_MARGIN,SIZING` are forbidden. Exact one-to-one coverage/group/roles/dependencies reject duplicates, omissions and alterations.

## 7. Evaluation, Artifact, provenance and failure

`Evaluation={schema_version,status,validation_boundaries,provenance,input_sha256,findings,result}`, closed. Schema is `RESEARCH_RETURN_BRIDGE_EVALUATION_V1`; findings `{path,code}` sorted pointer/code. Boundaries exactly retain synthetic origin; forecast/calibration/provider-PIT/reinvestment-ROIC/capital-allocation/economic-overlap/risk-feasibility/optimizer/OOS `NOT VERIFIED`; shadow `SHADOW VALIDATION NOT PASSED`; risk budget `RISK BUDGET NOT APPROVED`; Production `NOT PRODUCTION READY`.

`provenance={policy_filename,policy_sha256,design_filename,design_sha256,source_manifest,source_manifest_sha256,source_tree_sha256,git_commit,git_state}`; git state `COMMIT|UNBORN|GIT_NOT_AVAILABLE`. On success, status `COMPUTED_SYNTHETIC_TERMINAL_IDENTITY`, findings empty, input hash SHA-256 of canonical Bundle, result `{identity_rows,prior_rows,disagreements,scenario_ranges,coverage_registry,validation_boundaries}` with every intermediate tagged. Failure keeps seven keys and null result; input hash exists only after normalized Bundle; provenance null only for authority/source failure.

`Artifact={schema_version,input,evaluation,artifact_sha256}`, schema `RESEARCH_RETURN_BRIDGE_ARTIFACT_V1`; hash is SHA-256 of canonical Artifact with hash key omitted. No Artifact on failure. Capabilities is exactly `{schema_version,core_entry,accepted_origin,mandate_assumption,accounting_basis,array_taxonomy,limits,statuses,validation_boundaries,source_identity}`. Example bytes equal canonical BASE fixture.

Fixed ordered manifest:

```text
OPTIVEST_AI_POLICY_V10.md
docs/RESEARCH_RETURN_BRIDGE_DESIGN_REV2.md
optivest/return_bridge.py
optivest/return_bridge_api.py
optivest/static/return_bridge.js
optivest/static/return_bridge.css
optivest/fixtures/return_bridge_example.json
optivest/app.py
optivest/cli.py
```

Context captures authority/source/Git at load and rechecks Policy/design/all manifest members immediately before every successful evaluate/example/capabilities emission.

Stages: authority/source single finding -> HTTP/CLI acquisition single -> decoder single -> aggregated shape/type/range without invalid descent -> aggregated missing states -> aggregated membership/start/registry -> single arithmetic/numerical/internal/size. Earlier stage suppresses later. Closed codes: `POLICY_MISMATCH,DESIGN_MISMATCH,SOURCE_UNAVAILABLE,SOURCE_CHANGED,CONTENT_TYPE,CONTENT_ENCODING,JSON_SIZE,JSON_ENCODING,JSON_INVALID,JSON_DEPTH,JSON_NODES,DUPLICATE_KEY,TYPE_INVALID,UNKNOWN_FIELD,MISSING_FIELD,LITERAL_INVALID,VALUE_RANGE,FIELD_NOT_APPLICABLE,MISSING,UNKNOWN,STALE,CONFLICTING,UNAVAILABLE_PIT,DUPLICATE_ID,MEMBERSHIP_INVALID,START_BRIDGE_INCONSISTENT,COVERAGE_INVALID,ACCOUNTING_INVARIANT,NUMERICAL_NOT_VERIFIED,RESULT_SIZE,ARTIFACT_SIZE,INTERNAL_ERROR,FILE_MISSING,FILE_NOT_REGULAR,FILE_UNREADABLE,OUTPUT_FAILURE,CLI_USAGE`.

HTTP media grammar matches ADR-0018 exactly: sole application/json with optional sole unquoted charset=utf-8; absent/sole trimmed identity encoding; duplicates/comma/blank/other fail, content type first. Success 200, invalid/incomplete 422, JSON_SIZE 413, media 415, authority/source/numerical/internal 503. CLI capabilities/example/evaluate has exits 0 success, 2 input/incomplete/acquisition/usage, 1 authority/source/numerical/internal. stdout is canonical payload plus LF; output failure emits no fallback JSON.

Evaluation maximum 4,194,304 bytes; Artifact 5,242,880 bytes, inclusive. `_check_serialized_sizes`, `_assert_exact_invariants`, `_numeric_payload(state,precision)` are private test seams only.

## 8. Exact BASE/MAX and acceptance

BASE has one equity `SYN_E`: revenue100, margin.1, shares1, price100, multiple10. FLAT/GROWTH scenarios use margin.1/share1/multiple10/distribution0 and revenue factors1/2. Prior is risk-free.02, market.03, factor.01, raw alpha.04, weight.5, prior0 with exact literals. All 12 registry rows appear. Fixed display text is `Synthetic terminal identity BASE.`

Exact outputs: FLAT price/value100, factor1, log/rate0; GROWTH price/value200, factor2, log ln2/7, annualized `2^(1/7)-1`; prior exactly .08; disagreements -.08 and ln2/7-.08. `C(BASE)` defines exact fixture bytes; independent re-review constructs them and records length/hash before freeze. Production helpers cannot be its oracle.

Required counterexamples: price100.000000001 gives one start inconsistency; terminal distribution10 produces holder110 with no interim growth; share factor.5 only doubles price while distribution only adds cash and coherence stays NOT VERIFIED; zero revenue/margin/distribution gives exact zero tags while positive distribution is finite; prior weights0/1/.5 and incompatible literals; all semantic-set permutations preserve identity; all-zero scenarios yield unavailable range; below/at 40-digit tie boundaries fix membership.

Parser oracles: 12 nested arrays pass and 13 fail depth; 19,999 zero elements produce 20,000 nodes and decode then root type failure, 20,000 elements fail nodes; BASE padded to 1,048,576 bytes passes and one more fails; duplicate `{"x/y":[{"a~b":1,"a~b":2}]}` points `/x~1y/0/a~0b`, while malformed syntax is root JSON_INVALID.

MAX has four assets, eight scenarios, 32 supplied asset-scenario rows, four priors, 32 disagreements, four ranges, 12 registry rows = 84 result rows. Scenario j uses revenue factor j and otherwise BASE; exact outputs use factor j, log ln(j)/7, annualized j^(1/7)-1, disagreement ln(j)/7-.08; ranges scenario01..08. No cross product beyond 32. Algorithmic ceiling is 32 identity evaluations and 12 registry rows. Reference acceptance <=10 seconds and <=256 MiB traced peak; measurements cannot loosen fixed byte/algorithmic limits. Size seam accepts exact limits and rejects +1.

R1 covers parser/media/stages; R2 shapes/permutations; R3 every applicable wrapper; R4 rational start identity; R5 terminal factor cases; R6 mechanical use-once only; R7 zero/positive distribution; R8 no scenario cross-product; R9 incremental prior; R10/R11 ties/nonfinite/ranges; R12 exact registry/forbidden roles; R13 independent Decimal and fault seams; R14 canonical Unicode, BASE, every manifest mutation, pre-emission and Git; R15 disposable populated DB row-map/provider/trial/no-promotion isolation; R16 genuine desktop/390px BASE/incomplete/zero/stale/in-flight/error/XSS/local-rehash/corrupt-download/structured UI.

Allowed after Sol PASS and exact ADR freeze only: new return_bridge module/API/static/fixture/test plus narrow app/CLI and docs. Do not modify Policy, accepted artifacts, models/service/phase2/risk_editor/wealth_lab, migrations, dependencies, provider/raw/user DB, reviewer tests, ledger or Production gate. Required sequence remains correction -> independent re-review -> exact freeze -> Terra -> tests -> Sol validation. Literal boundaries remain unchanged.
