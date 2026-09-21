# Research Risk Budget editor — RESEARCH-RISK-EDITOR-V1 revision 2

Date: 2026-09-09. Owner: Astra. Status: CORRECTED DRAFT / SOL INDEPENDENT RE-REVIEW REQUIRED. This revision answers B1–B8 in docs/reviews/research_risk_editor_pre_review.md; it is not frozen or implementation authorization. Authority: OPTIVEST_AI_POLICY_V10.md, verified SHA-256 ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67.

## 1. Outcome, evidence and boundaries

Provide an offline research declaration editor, immutable versions, exact changes, input-consistency checks, and explicit unavailable feasibility/impact diagnostics. Existing service.risk_successor resets every successor to Balanced, app.RiskIn cannot accept constraints, and the home view has no risk editing controls. The existing 19 risk rows lack required definition, buffer, stress and joint metadata. The home page is blocked by provider INTERNAL_DISPLAY permissions, so the editor requires an independent internal-data route.

This changes the research Risk Budget input/validation contract: required sequence is corrected design → Sol re-review → Astra scoped freeze → Terra implementation → tests → Sol post-validation. It does not define a calibrated risk estimator or optimizer, authorize investment use, or change the Policy objective/mandate/provider permissions. Drafts cannot yield eligible decisions, weights or actions. Full numerical feasibility/sensitivity/opportunity-cost work stays open in TODO P2 after this slice. Personalized capacity/tolerance, model/OOS/shadow, and activation remain unavailable. Do not call this slice Phase 3, which conflicts with older roadmap numbering.

## 2. Normative primitive and JSON rules (B1, B3)

All shapes below are closed: every listed key is required unless explicitly optional; extra keys fail at every depth. Nullable declarations use exactly M<T> = {"value": T or null, "reason": string or null}. Non-null value requires reason=null. Null requires a nonblank reason (maximum 512 characters). Inapplicable fields use exactly {"value":null,"reason":"NOT_APPLICABLE"}. No other value may use this reason. Other strings are trimmed Unicode text, nonempty, maximum 2048 characters; identifiers maximum 128 characters. Array/object ordering is defined below. JSON null is never zero.

D is a nonnegative base-10 decimal STRING matching (0|[1-9][0-9]{0,11})(\.[0-9]{1,6})?; no sign, exponent, whitespace, NaN, Infinity or binary JSON number. Normalize via exact Decimal, stripping fractional trailing zeroes and a trailing dot; zero becomes "0". More than six fractional digits is rejected, never rounded. Decimal equality/differences use these exact values. Percent references use [0,100]; probability declarations use (0,1); durations/currency/other positive reference amounts use >0 when supplied. This is an input precision/storage convention, not an estimator precision claim.

IDs use server-generated UUID text for persisted versions; an API ID path lookup never treats a ticker as identity. All schema fields denoting IDs are strings. Revision numbers and horizon counts are strict JSON integers, excluding booleans. Server timestamps are UTC ISO-8601 ending Z, six fractional digits.

API write/preview reads raw request bytes BEFORE any FastAPI body-model binding. Require Content-Type application/json, optionally charset=utf-8 only; reject compressed content. CLI reads raw bytes from --file. Shared decoder: limit 1,048,576 bytes before decoding; strict UTF-8 without BOM; standard JSON with object_pairs_hook duplicate-key rejection at EVERY nesting depth; reject parse_constant; parse real JSON numbers as Decimal until typed validation rejects them where D is required. Maximum nesting 20 and maximum 10000 JSON nodes. API oversized body is 413, unsupported media/encoding 415, other parser failures 422. No input bytes are echoed in errors. Use stable error codes JSON_DUPLICATE_KEY, JSON_INVALID, JSON_ENCODING, JSON_DEPTH, JSON_SIZE, CONTENT_TYPE and TYPE_INVALID. Typed unknown/missing keys are UNKNOWN_FIELD and REQUIRED_FIELD. CLI uses the identical decoder and schema. Error diagnostics name code/path only plus safe static messages.

Canonical storage/hash JSON uses sorted object keys, UTF-8, ensure_ascii=false, no insignificant whitespace, and no NaN; all numbers except revisions/counts are normalized D strings. Constraints sort by the catalog ordinal below; joint groups sort by group_id, members by catalog order. Preserve array order nowhere else. Store the canonical JSON text; raw wire key/array ordering is irrelevant to semantic equality.

## 3. Exact request, document and response shapes (B1, B7)

Modern request envelope:
{request_kind, schema_version, expected_current_version_id, mandate_version_id, rationale, declaration}
request_kind is FULL_DECLARATION or CLONE_CURRENT. schema_version is RESEARCH_RISK_EDITOR_V1. FULL_DECLARATION requires declaration=Dcl; CLONE_CURRENT requires declaration=null. Client status/name/hash/revision/timestamp/validation fields are prohibited.

For backward compatibility ONLY, an object containing exactly expected_current_version_id, mandate_version_id, rationale and optional status="PROVISIONAL", with no modern-envelope keys, is recognized as the historical metadata-only contract and normalized to CLONE_CURRENT. It is not the editor's wire contract. Presence of any modern key requires the ENTIRE modern envelope; omitted declaration cannot silently select the compatibility path. A missing modern declaration is REQUIRED_FIELD. Historical request status other than PROVISIONAL is STATUS_FORBIDDEN. Do not broaden historical parsing to accept arbitrary legacy-looking payloads.

Dcl = {source_preset, constraints, joint_groups}.
source_preset = BALANCED_RESEARCH_V1 or GROWTH_RESEARCH_V1; it is draft provenance, not a claimed current profile name.
constraints is exactly 19 Row objects, one per catalog ID.
joint_groups is 0–32 Joint objects.

Row = {metric, constraint_class, operator, definition, unit, currency, horizon, estimation_method, data_window, confidence_level, limit, warning, minimum, risk, stress, hybrid, components}.
metric/class/operator are the exact fixed catalog values.
definition, currency, estimation_method, data_window are M<string>.
unit is M<Unit>, where Unit is PERCENT, PERCENT_ADV, PROBABILITY, MONTHS, TRADING_DAYS or CURRENCY; permitted subsets are in the catalog.
horizon is M<Horizon>; confidence_level, limit, warning, minimum are M<D>.
risk, stress and hybrid always have the exact objects defined in section 6, even when inapplicable.
components is [] except for catalog row 16, where it is exactly [TURNOVER, IMPLEMENTATION_COST] objects.

Component = {component_id, definition, unit, currency, horizon, estimation_method, data_window, limit, warning}. Its M<T> fields have the same meanings as Row. TURNOVER permits PERCENT; IMPLEMENTATION_COST permits PERCENT or CURRENCY; no other component IDs. Components have comparator <=, do not have confidence/robust/stress/joint fields, and are draft execution-policy declarations only.

Stored envelope E = {schema_version, risk_budget_version_id, profile_id, mandate_version_id, revision, supersedes_version_id, policy_hash, name, status, created_at, declaration}. All fields except declaration are server-owned and must equal the corresponding RiskBudgetVersion and current pinned Policy. status is PROVISIONAL; schema_version is RESEARCH_RISK_EDITOR_V1. Supersedes is null only for an actual revision-1 seed; this slice creates V1 only as a successor, so new V1 predecessor is always non-null.

Version response = {id, profile_id, mandate_version_id, revision, supersedes_version_id, policy_hash, name, status, created_at, editor_document_status, declaration, constraints, diagnostics}. editor_document_status is V1 or LEGACY_NOT_VERIFIED. Legacy declaration=null; constraints exposes actual existing column values, not reconstructed defaults. V1 constraints is the verified compatibility projection. In both cases diagnostics uses section 8. All endpoints use this serializer; new success responses are serialized into validated JSON bytes before committing.

History list = {items, offset, limit}, oldest revision first; offset strict integer >=0; limit 1–100 default 50. Missing version is 404 VERSION_NOT_FOUND; request IDs outside the single Generic Research profile fail 409 HEAD_CONFLICT without cross-profile data exposure.

## 4. Structured horizons and catalog (B1, B2)

Horizon = {kind, unit, count, event_clock}.
For kind FIXED_PERIOD: unit is DAYS, TRADING_DAYS, MONTHS or YEARS; count strict integer 1–12000; event_clock is DECISION_TO_HORIZON or STRESS_SCENARIO_PATH.
For kind OBSERVATION: unit/count are null; event_clock is CURRENT_PORTFOLIO, NORMAL_LIQUIDATION_OBSERVATION or ALWAYS.
No mixed shape, conversion or free-text event-clock ID is accepted. Explanatory text belongs in definition. 7 YEARS and 84 MONTHS are intentionally distinct declarations, not normalized equivalents.

Catalog horizon H below means FIXED_PERIOD/YEARS/7/DECISION_TO_HORIZON template. S means FIXED_PERIOD/YEARS/7/STRESS_SCENARIO_PATH. N means OBSERVATION/null/null/NORMAL_LIQUIDATION_OBSERVATION. A means OBSERVATION/null/null/ALWAYS. ? means null with reason DEFINITION_NOT_VERIFIED. B/G values below are exact decimal strings; dash means null with reason CALIBRATION_NOT_VERIFIED. The catalog permits no metric creation/deletion/reclassification.

| # | Metric | Class | Op | Permitted unit | B / G limit | Minimum | Template horizon |
|---|---|---|---|---|---|---|---|
|1|MAX_SINGLE_NAME_EQUITY|STRUCTURAL_HARD|<=|PERCENT|10 / 12.5|N/A|H|
|2|PASSIVE_MARKET_IMPLEMENTATION|STRUCTURAL_HARD|<=|PERCENT|100 / 100|0|H|
|3|MAX_SECTOR_INDUSTRY|STRUCTURAL_HARD|<=|PERCENT|30 / 35|N/A|H|
|4|MAX_FACTOR_CLUSTER|HYBRID|<=|PERCENT|35 / 40|N/A|H|
|5|MAX_MODELED_DRAWDOWN|MODEL_ESTIMATED|<=|PERCENT|25 / 30|N/A|H|
|6|MAX_STRESS_DRAWDOWN|STRESS|<=|PERCENT|35 / 45|N/A|S|
|7|MAX_RECOVERY_DURATION|MODEL_ESTIMATED|<=|MONTHS|36 / 48|N/A|H|
|8|MAX_DAYS_TO_LIQUIDATE|HYBRID|<=|TRADING_DAYS|5 / 5|N/A|N|
|9|MAX_PARTICIPATION_RATE|STRUCTURAL_HARD|<=|PERCENT_ADV|10 / 10|N/A|N|
|10|CASH_ALLOCATION|STRUCTURAL_HARD|<=|PERCENT|100 / 100|0|H|
|11|LEVERAGE|STRUCTURAL_HARD|<=|PERCENT|0 / 0|N/A|A|
|12|RISK_FREE_PROXY_ALLOCATION|STRUCTURAL_HARD|<=|PERCENT|100 / 100|0|H|
|13|PORTFOLIO_CVAR|MODEL_ESTIMATED|<=|PERCENT|- / -|N/A|?|
|14|SEVERE_LOSS_PROBABILITY|MODEL_ESTIMATED|<=|PROBABILITY|- / -|N/A|?|
|15|PERMANENT_LOSS_EXPOSURE|MODEL_ESTIMATED|<=|PERCENT, PROBABILITY|- / -|N/A|?|
|16|MAX_TURNOVER_IMPLEMENTATION_COST|HYBRID|<=|none|- / -|N/A|?|
|17|PORTFOLIO_JOINT_MATERIAL_RISK|MODEL_ESTIMATED|<=|PROBABILITY|- / -|N/A|?|
|18|MIN_LIQUIDITY|HYBRID|>=|CURRENCY, TRADING_DAYS|- / -|N/A|?|
|19|MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE|STRUCTURAL_HARD|>=|PROBABILITY|- / -|N/A|?|

This is exactly the existing set of 19 IDs, with deterministic new ordering. V1 corrects only the comparators of MIN_LIQUIDITY and MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE to >=; legacy rows remain unchanged. Their unknown values are not interpreted retroactively.

For rows 1–7,10,12: editable horizon is null or FIXED_PERIOD/any period unit/DECISION_TO_HORIZON, except row 6 requires STRESS_SCENARIO_PATH. For rows 8,9: null or N only. Row 11 is A only. Rows 13–15,17: null or FIXED_PERIOD/any period unit/DECISION_TO_HORIZON. Row 18: null or N only. Row 19: null or OBSERVATION/CURRENT_PORTFOLIO only. Row 16 parent horizon is fixed null; component horizons may be null or FIXED_PERIOD/DECISION_TO_HORIZON. No horizons imply actual measured events.

Only rows 5 and 7 have expected whole-investment-horizon semantics: alignment is DECLARED_MATCH only when horizon equals FIXED_PERIOD/YEARS/current mandate horizon/DECISION_TO_HORIZON. If null, UNSPECIFIED; otherwise DECLARED_MISMATCH. These remain declaration-level checks, never risk validation. Other rows report INDEPENDENT_CLOCK and may legitimately use other periods. Mandate_version_binding is CURRENT or STALE independently of horizon alignment. An 8-year successor binding can be CURRENT while preserved 7-year rows 5/7 report DECLARED_MISMATCH; never relabel them.

Templates: all row definition/method/window/confidence/warnings are null with DEFINITION_NOT_VERIFIED, except inapplicable fields. Known reference units/horizons/limits are exactly the table; unknown rows' units remain null even if the permitted subset has one item. Currency is NOT_APPLICABLE unless unit=CURRENCY. Applicable risk/stress/hybrid fields use the unverified defaults in section 6. Row 16 parent definition is "Legacy aggregate; inspect separate turnover and implementation cost declarations"; its unit/currency/horizon/limit/warning/minimum/confidence/method/window/risk/stress/hybrid are null/inapplicable as section 6 specifies. Its two components have all M fields null with DEFINITION_NOT_VERIFIED, except currency uses NOT_APPLICABLE until unit=CURRENCY. Joint groups default [].

Templates always retain their explicit 7-year research references. They do not update a mandate. Growth template application requires mandate horizon >=7; no age/capacity inference. Only these two templates exist; no Defensive or 15% single-name option. Custom single-name cannot exceed 12.5%. Do not relax permanent-loss/evidence/PIT/model/OOS/shadow governance through templates. Risk-free remains unavailable and passive VTI remains unapproved; these range controls are not weights. Benchmark never receives a range.

Server derives RiskBudgetVersion.name by comparing the entire normalized declaration to the chosen normalized template after omitting source_preset and all M.reason values. Equality gives that template's name; any changed non-reason value gives CUSTOM_RESEARCH. Source preset remains provenance even for CUSTOM. A supplied name is UNKNOWN_FIELD. Null reasons alone do not change template classification. Definition or horizon changes do.

## 5. Exact compatibility projection (B1)

Each V1 budget has exactly 19 RiskConstraint rows. For each document Row:
id = newly generated UUID; risk_budget_version_id = envelope ID; metric/class/operator = catalog; unit = unit.value or UNSPECIFIED; limit_value/warning_value = float(Decimal(value)) or SQL null; epsilon/alpha = matching risk declaration value converted the same way or null; uncertainty_version = risk.u_risk_version.value or null; stress_version = stress.version.value or null; calibration_status=NOT_VERIFIED; binding_status=DIAGNOSTIC unconditionally.

horizon projection: null becomes UNSPECIFIED; A becomes always; N becomes normal; CURRENT_PORTFOLIO becomes current_portfolio; FIXED_PERIOD becomes "<count> <days|trading days|months|years> [<event_clock>]" with literal enum event_clock. This explicitly extends old text without rewriting any old row. minimum, definition, method/window/confidence, component/buffer/scenario metadata and proposed stress role are document-only; their absence in compatibility is explicit, never evidence of validation.

missing_reason is EDITOR_DECLARATION_UNVERIFIED for rows 1–15,17–19. Row 16 projects: unit/horizon UNSPECIFIED; numeric values epsilon/alpha all SQL null; uncertainty/stress version null; missing_reason LEGACY_AGGREGATE_SEPARATE_COMPONENTS; fixed catalog class/operator; binding/calibration as above. Its nested costs are never combined into that row.

To verify float projections, compare retrieved floats to exactly float(Decimal(canonical D)), reject nonfinite values, and compare null versus null explicitly; do not use tolerance. Decimal strings in the document are authoritative for calculations/diffs; floats remain compatibility storage. Every other column except generated constraint IDs is compared exactly. IDs must be unique, nonempty and belong to the same budget. This verifier proves projection agreement, not numeric-model accuracy.

## 6. Class/mode matrix and joint declarations (B4)

Risk = {mode, epsilon, alpha, u_risk_version, buffer_value, buffer_rationale, calibration_reference}.
epsilon/alpha/buffer_value are M<D>; remaining fields M<string>.
Modes: NOT_APPLICABLE, UNSPECIFIED, ROBUST_CHANCE, ROBUST_QUANTILE, EQUIVALENT_BUFFER.
STRUCTURAL_HARD and STRESS require NOT_APPLICABLE and all M fields NOT_APPLICABLE.
MODEL_ESTIMATED and HYBRID (except row 16) permit:
- UNSPECIFIED: all risk M values null, each reason SEMANTICS_NOT_VERIFIED.
- ROBUST_CHANCE: epsilon, u_risk_version, calibration_reference applicable; alpha/buffer_value/buffer_rationale exactly NOT_APPLICABLE.
- ROBUST_QUANTILE: alpha, u_risk_version, calibration_reference applicable; epsilon/buffer_value/buffer_rationale exactly NOT_APPLICABLE.
- EQUIVALENT_BUFFER: u_risk_version, buffer_value, buffer_rationale, calibration_reference applicable; epsilon/alpha exactly NOT_APPLICABLE. Buffer uses row unit and nonnegative D; unknown unit requires buffer_value=null. It is a proposed replacement for robust uncertainty, never an additive second penalty.
Applicable values may be null with nonblank reason; that generates RISK_SEMANTICS_INCOMPLETE. Populating every field still yields RISK_CALIBRATION_NOT_VERIFIED; references/text are declarations, not verified evidence. Mode selection with forbidden fields is invalid input, not a savable draft. Row 16 Risk is NOT_APPLICABLE. Template modeled/hybrid risk is UNSPECIFIED.

Stress = {proposed_role, version, scenario_id, definition, severity}.
Role is NOT_APPLICABLE, UNSPECIFIED, DIAGNOSTIC or BINDING. All M fields are M<string>. Only row 6 may use the last three roles. Others require NOT_APPLICABLE with every M field NOT_APPLICABLE. Row 6 template role=UNSPECIFIED and all M fields null/reason STRESS_NOT_VERIFIED. For row 6, UNSPECIFIED requires all null with STRESS_NOT_VERIFIED; DIAGNOSTIC/BINDING permit declared/null fields. Incomplete selected role yields STRESS_SEMANTICS_INCOMPLETE; every role remains STRESS_VALIDATION_NOT_VERIFIED. Proposed BINDING never changes compatibility binding_status or creates an approved constraint.

Hybrid = {observed_component, estimated_component, normal_liquidity_assumption, stress_liquidity_assumption, participation_assumption}.
First four are M<string>, last M<D> in [0,100] PERCENT_ADV. Rows 4,8,18 may declare observed/estimated components. Only rows 8,18 may declare liquidity/participation fields; other rows require those fields NOT_APPLICABLE. Other classes and row 16 require all five fields NOT_APPLICABLE. Applicable template fields are null/reason HYBRID_COMPONENT_NOT_VERIFIED. All supplied hybrid assumptions remain unmeasured; no input field can assert observed verification.

Joint = {group_id, members, horizon, epsilon, u_risk_version, dependency_method, dependency_reference}.
group_id is a nonblank unique identifier; members is 1–18 unique catalog metric IDs; horizon=M<Horizon>, epsilon=M<D>, other three fields M<string>. Only MODEL_ESTIMATED/HYBRID rows except 16 and 17 may be members; row 17 is the joint-budget summary, never a recursive member. A metric may be a member of only one group in this slice. Group epsilon is distinct from the optional row 17 reference; neither is computed from the other or added.
If every referenced member and group horizon is declared, all must match exactly, including event_clock; mismatch is JOINT_HORIZON_CONTRADICTION. If any is missing, store a draft with JOINT_DEFINITION_INCOMPLETE. Selected dependency methods are free-text declarations, never permission to assume independence. A fully populated group still has JOINT_RISK_NOT_VERIFIED. No conversion, joint simulation, epsilon allocation/summation, permanent-loss component addition or hierarchical cross-horizon model is implemented.

## 7. Persistence, transitions and transaction predicate (B6–B8)

Add ONLY migration 0003_research_risk_editor after existing 0002. Do not alter 0001/0002 or backfill legacy values. Add:
- research_risk_editor_markers: risk_budget_version_id PK/FK to risk_budget_versions with RESTRICT, schema_version NOT NULL CHECK = RESEARCH_RISK_EDITOR_V1, document_sha256 NOT NULL CHECK length=64 and lowercase hex, created_at NOT NULL.
- research_risk_editor_documents: risk_budget_version_id PK/FK to markers with RESTRICT, schema_version same check, payload TEXT NOT NULL CHECK json_valid(payload), created_at NOT NULL.
Both tables have immutable BEFORE UPDATE/DELETE abort triggers and nonblank timestamp checks. One-to-one/FK constraints block duplicate/unowned documents. No INSERT OR REPLACE. The marker is the claim that the budget is V1; missing/malformed/divergent document is corruption. The digest hashes canonical envelope E UTF-8. Inserts alone are not verification: the verifier below parses and checks all fields.

| Current head | Request | New version |
|---|---|---|
|Legacy|CLONE_CURRENT / exact historical envelope|Clone actual budget name and every existing constraint column except IDs/budget FK. No marker/document. LEGACY_NOT_VERIFIED.|
|Legacy|FULL_DECLARATION|Require the entire valid Dcl; no automatic completion. New V1 marker/document and derived projection/name.|
|V1|CLONE_CURRENT / exact historical envelope|Verify and clone exact normalized declaration; generate fresh envelope/projection/marker. Same derived name.|
|V1|FULL_DECLARATION|Validate full Dcl; new envelope/projection/marker and derived name.|

All transitions use server PROVISIONAL/pinned Policy/current mandate binding and revision=old+1. Legacy cloning must not normalize units/operators/horizons/reasons or fabricate metadata. Reject legacy corruption (invalid chain, nonfinite numeric, duplicate/missing 19 metrics, unexpected class or unexpected operator except the two historical <= minimum operators) as EDITOR_STORAGE_INVALID, not a repair. Legacy <= minimum operators carry LEGACY_COMPARATOR_UNVERIFIED diagnostic until a FULL_DECLARATION resolves them. Changed current mandate leaves preserved legacy horizons explicitly unverified. Full declaration is the ONLY legacy→V1 transition.

For risk save use one SQLite transaction acquired before reading, with explicit BEGIN IMMEDIATE before any DML to prevent concurrent head modification while reading/evaluating. Capture one profile row plus both heads, verify all current storage, validate/evaluate the candidate, create budget/document/projection/marker and flush, then perform ONE conditional update:
UPDATE research_profile_heads SET risk_budget_version_id=:new WHERE profile_id=:profile AND risk_budget_version_id=:expected_risk AND mandate_version_id=:expected_mandate.
Exactly rowcount=1 is required; zero is HEAD_CONFLICT and rollback. No intermediate commit. Profile/mandate/current risk/policy must match before writes. A mandate successor may occur after this successful transaction; then binding is correctly reported STALE and preflight stays blocked. This is not a claim that future mandate changes are impossible.

Pre-render and validate the complete success response while the transaction is open; commit only after successful serialization. Parser/schema/evaluator/storage/projection/trigger/flush/CAS/serialization/commit failures roll back all new rows and head movement. SQLITE_BUSY maps to 409 WRITE_CONFLICT after rollback; do not retry a save silently. A network disconnection after a successful commit cannot undo it: retry with the old expected head gets 409 and client reloads history. No exactly-once HTTP delivery claim.

Preview is read-only in one explicit consistent SQLite read transaction and returns expected IDs plus current observed IDs. A stale request returns 409; validation never seeds or inserts. Browser displays the draft upon conflict; it never silently replays against a new mandate/head. Verification and current/history reads use a read snapshot.

## 8. Deterministic evaluator, statuses and errors (B5)

One pure evaluator receives verified current-state DTOs plus normalized candidate. No DB/network call and no client-supplied evaluation. Every API/CLI/UI/current/status/preflight surface uses it. Diagnostics:
{input_validation, consistency_status, findings, blockers, mandate_version_binding, risk_horizon_alignment, feasibility_status, impact, validation_status, risk_budget_status, production_readiness}.
input_validation=VALID (invalid candidates return error before evaluation).
consistency_status=NO_KNOWN_CONTRADICTION or RISK BUDGET INCONSISTENT.
findings=[{code,path,severity}], severity ERROR or BLOCKER.
blockers=sorted unique code strings from BLOCKER findings plus RISK_BUDGET_INCONSISTENT when consistency is inconsistent.
mandate_version_binding=CURRENT or STALE.
risk_horizon_alignment=[{metric,status}], rows 5,7 with DECLARED_MATCH/DECLARED_MISMATCH/UNSPECIFIED; other rows status INDEPENDENT_CLOCK.
feasibility_status=NOT VERIFIED; validation_status=NOT VERIFIED; risk_budget_status=RISK BUDGET NOT APPROVED; production_readiness=NOT PRODUCTION READY unconditionally. Inconsistency is separate from approval status. Findings order is severity ERROR before BLOCKER, then catalog path ordinal then code; impact and alignment follow fixed order.

Closed schema/input-error rules, 422:
TYPE_INVALID, UNKNOWN_FIELD, REQUIRED_FIELD, NULL_REASON_INVALID, TEXT_INVALID, DECIMAL_INVALID, RANGE_INVALID, UNIT_INVALID, HORIZON_INVALID, CLASS_OR_OPERATOR_INVALID, METRIC_SET_INVALID, PRESET_INVALID, STATUS_FORBIDDEN, FIELD_NOT_APPLICABLE, SEMANTICS_FIELDS_INVALID, JOINT_REFERENCE_INVALID.
These cover the exact type/bounds/class/catalog/shape/field-applicability rules above. Null unit requires null numeric limit/warning/minimum/buffer (minimum applies only allocation rows); CURRENCY unit requires currency=M<3 uppercase ASCII letters>, optionally null with explicit reason; non-CURRENCY requires currency NOT_APPLICABLE. Warning with null limit is allowed only as unverified numeric reference and receives FIELD_UNSPECIFIED for the missing limit. Non-applicable minimum/components are rejected if populated. Duplicate IDs/members/unknown or recursively joint references use JOINT_REFERENCE_INVALID.

Closed evaluable contradictions, severity ERROR:
LIMIT_WARNING_CONTRADICTION: both known, <= warning>limit or >= warning<limit.
ALLOCATION_RANGE_CONTRADICTION: known minimum>maximum on rows 2,10,12.
ALLOCATION_MINIMUM_TOTAL: sum of supplied minima for passive/cash/risk-free rows 2,10,12 >100. Missing minima are omitted from this lower-bound impossibility check, not imputed as zero; no converse feasibility claim. Do not sum maxima or exposures of overlapping equities/sectors.
LEVERAGE_FORBIDDEN: row 11 limit not exactly "0" (null also contradiction; zero mandate requirement is not an unknown estimate).
SINGLE_NAME_SCOPE_EXCEEDED: row 1 supplied limit>12.5.
GROWTH_HORIZON_OUT_OF_SCOPE: source_preset=GROWTH and mandate horizon<7.
JOINT_HORIZON_CONTRADICTION: fully specified common-horizon equality fails.
No other mathematical or investment contradiction may be invented by Terra; additional rules require design change.

Closed BLOCKER codes:
RISK_BUDGET_NOT_APPROVED, RISK_FEASIBILITY_NOT_VERIFIED, MODEL_IMPACT_NOT_AVAILABLE always.
MANDATE_BINDING_STALE when stale.
RISK_HORIZON_UNSPECIFIED or RISK_HORIZON_DECLARED_MISMATCH per row 5/7.
FIELD_UNSPECIFIED for each applicable M field whose value is null, excluding subfields of UNSPECIFIED risk/stress and legacy-only unused fields.
RISK_SEMANTICS_UNSPECIFIED for modeled/hybrid UNSPECIFIED mode; RISK_SEMANTICS_INCOMPLETE for missing applicable selected-mode fields; RISK_CALIBRATION_NOT_VERIFIED for every modeled/hybrid risk row.
STRESS_SEMANTICS_UNSPECIFIED, STRESS_SEMANTICS_INCOMPLETE (selected role missing fields), STRESS_VALIDATION_NOT_VERIFIED for row 6.
HYBRID_COMPONENT_NOT_VERIFIED for each applicable hybrid row, regardless of populated assumptions.
JOINT_DEFINITION_MISSING for no groups; JOINT_DEFINITION_INCOMPLETE for missing group fields/member horizons; JOINT_RISK_NOT_VERIFIED for each group and row 17.
BENCHMARK_AVAILABILITY_NOT_VERIFIED, PASSIVE_IMPLEMENTATION_NOT_APPROVED, PASSIVE_LOOKTHROUGH_NOT_VERIFIED, RISK_FREE_PROXY_NOT_APPROVED always for the existing research mandate.
LEGACY_BUDGET_NOT_VERIFIED plus LEGACY_COMPARATOR_UNVERIFIED for legacy minimum operators. Legacy rows get no fabricated V1 field findings; preserve compatibility null reasons in the response.
These codes supplement existing provider/PIT/tradability blockers; they cannot remove them. No joint groups or filled metadata ever yields calibrated/feasible status.

impact has exactly keys robust_utility, expected_cagr, expected_twr, stress_drawdown, cvar, permanent_loss, joint_breach_probability, cash_allocation, concentration, binding_constraint, shadow_price, defensive_opportunity_cost. Each value is {value:null,status:"NOT VERIFIED",reason:CODE}. Reasons: UTILITY_ENGINE_UNAVAILABLE for robust_utility; FORECAST_WEALTH_MODEL_UNAVAILABLE for expected_cagr/twr; RISK_MODEL_UNAVAILABLE for stress_drawdown/cvar/permanent_loss; JOINT_MODEL_UNAVAILABLE for joint_breach_probability; OPTIMIZER_UNAVAILABLE for cash_allocation/concentration/binding_constraint/shadow_price/defensive_opportunity_cost. Under self-financing mandate, expected_twr remains null with the above reason; no return is implied.

Parser/schema error: API error {error:{code,fields:[{code,path}]}} with 422 (or 413/415 as section 2); no rows written. Consistent/inconsistent valid preview: 200 {expected_current_version_id,mandate_version_id,diagnostics,changes,candidate_name}; save inconsistency: 422 {error:{code:"RISK_BUDGET_INCONSISTENT",fields:[ERROR findings]},diagnostics}; stale/race: 409 HEAD_CONFLICT or WRITE_CONFLICT; successful draft save: 201 Version response. Storage corruption: 503 EDITOR_STORAGE_INVALID with safe reason codes, never a partial result. Unexpected internal failure: 500 INTERNAL_ERROR after rollback; never masquerades as a valid draft.

changes = array {path,before,after,comparison}, sorted by canonical JSON pointer; recursively compare all declaration leaves including reason transitions. Missing legacy V1 values are null with explicit LEGACY_FIELD_UNAVAILABLE comparison, never synthesized. comparison=TIGHTER/LOOSER only for known numeric same-row limit/warning/minimum/buffer when metric/unit/horizon/class/operator/risk-mode+U_risk/stress-version+role identities match. <= increase is LOOSER, >= increase is TIGHTER; minimum increase is TIGHTER; buffer increase is TIGHTER only for EQUIVALENT_BUFFER. Different definition/method/window/confidence or scenario/dependency declaration makes all affected comparisons NOT_COMPARABLE; component changes require same component identity/definition/unit/horizon. Other changed leaves are NOT_COMPARABLE. Equality has no change row. This compares declarations only; never label expected investment benefit or opportunity cost.

Current status adds risk_editor_status=V1 or LEGACY_NOT_VERIFIED, risk_editor_diagnostics and blockers. Preflight still requires coherent current same-profile heads as today; incoherent pair returns its existing 422. For a coherent pair add evaluator blockers, always retain eligible_for_research_decision=false and NOT PRODUCTION READY. Corrupt storage yields 503 and no snapshot insertion.

## 9. Verifier and migration fail-closed rules (B8)

Add read-only verify_risk_editor(session), also exposed by CLI verify-risk-editor. It checks exact revision 0003_research_risk_editor; presence of both tables, required PK/FK/CHECK constraints and immutable trigger definitions; all profile heads and all mandate/risk chains (same profile, unique positive consecutive revisions, exactly revision 1 root, predecessor prior revision, no forks/cycles, pinned policy, PROVISIONAL/mode), and every risk version's exact catalog rows. Existing mandatory Phase 1 chains are not repaired.

For every marker: exact schema string, syntactically valid lowercase hash and timestamp, existing same-ID budget/document; decode stored raw JSON with the same strict decoder, validate closed server envelope plus declaration, compare every server field to budget/profile, canonicalize/hash, derive name and compare, compare exact projection. For each document require marker. Validate ALL historical V1 rows, not just current. Old V1 drafts may now bind an old mandate: evaluate against their linked mandate for historical value checks and separately label current binding STALE; never apply current mandate values retroactively. A stored V1 with evaluable contradictions, malformed envelope, forged name/status/policy, missing document or projection divergence is invalid. Current/history/editor/preflight startup checks fail 503 or app initialization error; no partial eligible output. A newly discovered schema/trigger corruption invalidates serving even if startup previously passed, because each exposed risk operation verifies.

Legacy detection is the absence of both marker/document. Downgrade drops the two new tables only; old budget/projection rows survive and intentionally read as legacy after re-upgrade. Downgrade of populated editor tables is destructive and authorized ONLY in isolated acceptance databases, never user data. No retrofit guessed V1 payloads. The verifier detects corrupt checked records/constraints; it does not claim cryptographic protection against a privileged actor replacing the entire database and governance history.

Phase 2 verifier accepts exactly revisions 0002_phase2 and 0003_research_risk_editor, with actual revision reported, and retains every earlier exact provider/declaration/raw/schema check. Editor app requires new head and both new table contracts. Unknown future revisions fail both. A failing Phase 2 permission matrix still fails overall existing app startup; valid NOT_VERIFIED permission rows do not prevent /risk-budget. INTERNAL_DISPLAY remains enforced on original provider/home routes. No permissive "revision >=..." check.

## 10. API, CLI, UI and implementation scope

API: keep existing current/versions POST; add catalog GET (normalized Balanced/Growth template declarations plus catalog allowed enum metadata), version GET /api/v1/risk-budgets/versions/{id}, paginated versions GET, preview POST. Add no activation endpoint. Existing phase1 mandate horizon POST is separate; UI may edit horizon through it, preserving optimistic locking and making resulting alignment limitations visible. Editor startup/status never rewrites mandate or seed.

CLI: risk-budget show [--version-id ID], risk-budget preview --file PATH, risk-budget save --file PATH, verify-risk-editor. JSON outputs use identical serializers. Exit 0 for valid read/preview/save, 1 for storage/internal failure, 2 for input/inconsistency/conflict; inconsistent preview still prints diagnostic result and exits 2. No network or automatic retries.

/risk-budget is a separate same-process HTML/JS route using internal risk/mandate/status only. No provider captures or permission evaluation in this page; existing home/provider checks remain unchanged. Display all rows/classes/units/null reasons, current version/source preset/name/status, separate mandate binding and risk horizon alignment, draft modes and unverified evidence/estimation metadata, differences, history and diagnostics. Group row 16 into two named component forms; its aggregate is non-editable. Explain percent 0–100 versus probability 0–1. Show MODEL-ESTIMATED RISK and stress-not-guaranteed labels. Both templates require preview before save; no recommended/suitable language. SAVE AS PROVISIONAL runs server validation again. Conflict preserves unsaved draft and requires user reload/rebase. Disable duplicate submissions. Escape all free text/textContent. No assumed-zero rendering. Capacity and tolerance are separate NOT ASSESSED / PERSONALIZED MODE UNAVAILABLE panels; activation control disabled with no request generated.

Allowed future implementation files after freeze: optivest/risk_editor.py (schema/decoder/catalog/evaluator/projection/verifier), optivest/models.py, service.py, app.py, cli.py, new optivest/static/risk_editor.js and risk_editor.css if useful, alembic/versions/0003_research_risk_editor.py, tests/test_risk_editor.py and risk-surface/revision expectations in tests/test_phase1.py/tests/test_phase2.py only as required, README and .ai operational records. optivest/phase2.py change limited to exact supported revision compatibility. No new runtime dependency, old migration edits, provider parser/permission/declaration changes, production deployment, billing, approval or trading/model implementation.

## 11. Acceptance, B1–B8 closure map and review gate

B1: sections 2–5 and 8 fix closed schema, catalog, canonical decimal storage, envelope/projection/name, component handling. B2: section 4 fixes horizon/event-clock identity and separates mandate binding/alignment. B3: section 2 fixes raw parsing. B4: section 6 fixes all class/mode implications. B5: section 8 fixes input/evaluator/status/impact outcomes. B6: section 7 freezes transaction/CAS/serialization. B7: section 7 transition table plus section 3 explicit modern discriminator preserves bounded historical compatibility. B8: sections 7/9 fix marker, checks, all-history verifier and exact revisions. These are proposed corrections, not Sol acceptance.

Acceptance requires:
1. New Sol review against this exact corrected hash, then explicit scoped ADR freeze. No inference of a PASS from author corrections.
2. Normative roundtrip using generated exact templates: wire key/array permutations → identical normalized Dcl/hash semantics, preview → save → API/CLI/current/history/DB projection; reason-only changes and name spoof; all 19 rows and both cost components; null versus zero.
3. Duplicate-key raw negatives at envelope/Row/Risk/Joint/M wrapper; BOM/bad UTF-8/nonfinite/size/depth limits, strict bool/number/decimal/exponent/scale rejection.
4. Exhaustive class-by-mode and forbidden-field tests; selected incomplete modes block, complete chance/buffer/BINDING/text cannot promote validation; percentages/probabilities/currency/unknown unit/warning/minimum bounds and all closed contradictions.
5. Horizon negatives 7 YEARS vs 84 MONTHS, differing event clocks, group membership/recursion/duplicate/cross-horizon declarations; 8-year mandate/current binding with preserved 7-year references never aligned or relabelled.
6. All four legacy/V1 transitions; preserve actual pre-existing custom/legacy rows, null reasons and historical comparators; no default reset; modern envelope omission cannot take legacy path.
7. Deterministic two-session interleavings and failure injection: mandate/risk race, projection/document/marker/trigger failure, post-flush and response-serialization exception, SQLITE_BUSY; no orphan rows or stale-head promotion. Preview and failed requests leave DB rows/heads unchanged.
8. Fresh isolated SQLite upgrade→seed→0003, populated downgrade→0002→re-upgrade, preservation of old rows/providers, legacy reclassification after document removal. Raw SQL attempts against FK/checks/immutability; malformed JSON/unknown schema/wrong linkage/forged envelope/preset/status/missing V1 document/projection drift/unknown revision trigger rejection or verifier failure. Verify historical corruption also blocks current/editor/preflight.
9. Real local browser exercise on isolated DB from this checkout: edit/clear/preview/save/reload/history/stale conflict, exact null reasons and XSS-safe rendering, desktop/mobile. Repeat with seeded valid-but-blocked provider permissions; editor works while Data Evidence remains denied.
10. Full existing pytest suite, syntax checks, startup checker and git diff --check; existing phase2 negative assertions preserved. Explicit host-denied symlink skips stay limitations. Sol independently checks DB/API/CLI/UI and failures before PASS_ENGINEERING_RESEARCH_RISK_EDITOR.
11. .ai records current, TODO numerical feasibility/impact remains open, no §18 risk/model/readiness gate is set PASS because of this editor. Model limitations and NOT VERIFIED impact remain visible.

Design deviations: NONE intended. Corrected design is currently NOT FROZEN. Remaining nonblocking limitations are draft-only declarations, unverified provider/PIT/benchmark/passive/risk-free inputs, no full feasibility/model/calibration/optimizer/impact, personal assessment, OOS/shadow or production approval. No research experiment is run or ledger record manufactured by this documentation task.
