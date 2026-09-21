# RESEARCH-RISK-EDITOR-V1 independent post-implementation validation

Date: 2026-09-09 (Asia/Tokyo)  
Reviewer role: Sol, independent falsification-first validator  
Verdict: **IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED**  
Engineering gate: **DO NOT set `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**

## 1. Authority, identity and scope boundary

- Selected Policy: `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` (matches `AGENTS.md` and `.ai/START_HERE.md`).
- Frozen specification: ADR-0017 / decision D0009 and `docs/RESEARCH_RISK_EDITOR_DESIGN.md`, SHA-256 `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950`.
- Accepted pre-review: `docs/reviews/research_risk_editor_pre_review.md`, SHA-256 `EA061F0994AAF176515782CDFE231CA96D7D462F2BC3BE69596CD426FE3AFCF7`.
- Repository state reviewed: branch `main`, `HEAD=UNBORN`, all project files untracked. No commit or remote exists.

This verdict concerns whether the editor implementation conforms to the frozen declaration, persistence, API/CLI/UI and verification contract. It is **not** numerical risk validation. No calibrated risk model, feasibility solver, `U_risk`, `S_stress`, optimizer, impact calculation, provider/PIT proof, OOS or shadow evidence was validated. The mandate and budget remain provisional; `RISK BUDGET NOT APPROVED`, `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain unchanged.

Policy alignment is not optional here. Policy §4 requires frozen design followed by tests and post-validation; §8 separates structural/model-estimated/hybrid/stress semantics and requires fail-closed treatment; §16 forbids swallowed errors, API failures presented as valid input outcomes and UI-only completion, and requires material rules in code/tests; §17 makes ADR-0017 superior to the implementation; §18 items 2–5, 13–14, 22–25 are AND gates. The failures below therefore block engineering acceptance without implying any Production or investment approval.

## 2. Executive result

The implementation is not a close miss. It persists changed numerical reference limits and declarations that the frozen grammar explicitly prohibits, and its verifier accepts forged historical envelopes and divergent compatibility projections. A corrupt current editor document is hidden by `/api/v1/status`; preflight still inserts a decision snapshot. The frozen evaluator, change engine and editor UI are largely absent.

The implementer's 74-test set remains green (`74 passed, 2 skipped`), but its editor coverage is only two tests. The independent suite adds 29 focused cases: **27 failed, 2 passed**. The complete suite is therefore **27 failed, 76 passed, 2 skipped**. Green pre-existing tests do not offset direct contract counterexamples.

## 3. Blocking findings, prioritized

### P0-1 — Canonical decimal normalization changes the frozen risk references

`optivest/risk_editor.py:91-94` formats a normalized Decimal and then applies `rstrip("0")` to the entire string. Integer zeroes are removed, not only fractional trailing zeroes. An exact generated Balanced declaration saved through the real API returned:

| Metric | Frozen/template input | Stored declaration / projection |
|---|---:|---:|
| MAX_SINGLE_NAME_EQUITY | `"10"` | `"1"` / `1.0` |
| PASSIVE_MARKET_IMPLEMENTATION | `"100"` | `"1"` / `1.0` |
| MAX_SECTOR_INDUSTRY | `"30"` | `"3"` / `3.0` |
| MAX_PARTICIPATION_RATE | `"10"` | `"1"` / `1.0` |
| CASH_ALLOCATION | `"100"` | `"1"` / `1.0` |
| RISK_FREE_PROXY_ALLOCATION | `"100"` | `"1"` / `1.0` |

The same generated template is consequently named `CUSTOM_RESEARCH`, because `derived_name()` compares the mutated declaration to an unnormalized template (`risk_editor.py:168-172`). This violates frozen sections 2, 4, 5 and 8 and changes the intended research declaration. It is a Policy §8/§16 material correctness failure.

Required correction: normalize only the fractional portion, preserve integral zeroes, add exact B/G fixture vectors for every D field and assert declaration/hash/projection/name identity through API, CLI and DB. Template comparison must follow the frozen omission and normalization rules.

### P0-2 — Nested schema, class/mode, horizon, component and joint rules fail open

`validate_declaration()` (`risk_editor.py:107-128`) validates only the outer row keys, catalog metric/class/operator, selected top-level M wrappers, a generic horizon shape, a shallow unit check and row-16 component IDs. It does not validate the closed `Risk`, `Stress`, `Hybrid`, `Component` or `Joint` shapes or the section-6 implication matrix. It also does not enforce per-metric horizons, M string rules, reason applicability, currency rules or complete numeric bounds.

Each independent mutation below returned **HTTP 201** and was persisted, where ADR-0017 requires 422 and zero writes:

- `STRUCTURAL_HARD` row using `risk.mode=ROBUST_CHANCE` with populated epsilon/U-risk;
- unknown nested key in `risk`;
- `DIAGNOSTIC` stress declaration on a structural row;
- populated hybrid observation on a structural row;
- row 1 using the row-19-only `CURRENT_PORTFOLIO` observation clock;
- unknown field in a row-16 component;
- `NOT_APPLICABLE` reason on an applicable definition field;
- `joint_groups=[{}]`;
- row-3 percent limit `"999"`.

This directly contradicts design sections 2, 4, 6, 8 and 11 and Policy §8's class separation/fail-closed semantics.

Required correction: implement the complete closed recursive grammar and exhaustive class-by-mode/forbidden-field matrix exactly as frozen. Use catalog-ordinal paths and reject before evaluation or DML. Add parametrized coverage for every class, mode, row-specific horizon, unit/currency/range, component and joint-group rule.

### P0-3 — The all-history verifier is not an exact verifier and exposed operations fail open on corruption

`verify_risk_editor()` (`risk_editor.py:193-202`) checks only the exact revision, 19 unique rows and the V1 metric set. `get_document()` (`risk_editor.py:182-191`) checks digest/canonical bytes plus only budget ID, pinned Policy and name. It does not verify the closed server envelope, profile/mandate/revision/predecessor/status/timestamp, derived name, exact projection, profile heads, version chains, legacy invariants, required constraints or trigger definitions.

Independent raw-SQL probes on disposable databases established all of the following:

- after removing the projection update trigger and changing a stored V1 row to `limit_value=77`, `verify_risk_editor()` returned `VALID`;
- after forging a historical V1 envelope from `status=PROVISIONAL` to `status=APPROVED` and recomputing its digest, `verify_risk_editor()` returned `VALID`;
- the marker digest CHECK accepted 64 lowercase non-hex `z` characters;
- migration 0003 points the document FK directly to `risk_budget_versions`, not to the marker as frozen, and has no nonblank timestamp CHECK;
- `service.status()` catches and discards every document validation exception (`service.py:53-64`), so current digest corruption returns HTTP 200 with the editor state silently omitted;
- `service.preflight()` never verifies/evaluates the editor (`service.py:150-171`), so the same corrupt current document produced HTTP 201 and inserted a decision snapshot;
- current/history responses return stored projection rows without comparing them to `project()` (`service.py:83-96`).

These are direct violations of design sections 7–9 and Policy §16's prohibition on swallowed errors and API failures presented as normal results.

Required correction: implement the complete read-snapshot, schema/constraint/trigger, all-profile-head, mandate/risk-chain, exact server-envelope, derived-name and field-by-field projection verifier. Call it for every current/history/status/editor/preflight operation and startup; corruption must yield 503/app initialization failure with no snapshot or partial result. Correct migration ownership/hash/timestamp constraints in a new authorized migration strategy; do not edit frozen historical migrations without an explicit decision.

### P1-1 — The frozen evaluator and change engine are absent

`diagnostics()` (`risk_editor.py:144-166`) implements only five simple contradictions, two horizon alignment checks and seven static blockers. It omits the frozen `FIELD_UNSPECIFIED`, risk/stress/hybrid/joint findings and blockers, required legacy comparator blocker and deterministic severity/catalog ordering. A generated template produced none of the required missing-semantics findings. `service.preflight()` returned only the four pre-existing Phase-1 blockers, omitting `RISK_FEASIBILITY_NOT_VERIFIED` and `MODEL_IMPACT_NOT_AVAILABLE`.

`editor_preview()` unconditionally returns `changes=[]` (`service.py:142-148`). Changing the single-name limit from 10 to 9 still returned an empty difference list. It also does not return current observed IDs or start the frozen explicit read transaction.

Required correction: implement one pure evaluator and recursive declaration change engine exactly as design section 8 specifies, and use the same result in preview/save/current/history/status/preflight/API/CLI/UI. Keep feasibility/impact `NOT VERIFIED`; do not invent numerical results.

### P1-2 — HTTP/CLI failure semantics and concurrency mapping are not deterministic

The FastAPI helper raises `HTTPException` with the frozen envelope placed in `detail` (`app.py:83-87`), yielding `{"detail":{"error":...}}` rather than top-level `{"error":...}`. It maps every non-storage/non-conflict exception to 422, including injected internal projection failure. Oversized input is 422 rather than 413. `application/json; charset=shift_jis` and a declared `Content-Encoding: gzip` are accepted. A held SQLite `BEGIN IMMEDIATE` lock returned an arbitrary 422 error code instead of `409 WRITE_CONFLICT`.

The injected projection exception did prove that the successor row and head were rolled back, so the core rollback wrapper works for that fault. The failure classification and stable public contract do not.

Required correction: explicitly map parser size/media/encoding, schema, inconsistency, head/write conflict, storage and unexpected failures to the exact frozen statuses/envelopes; never expose raw driver exception text. Add two-session lock/race tests and every frozen failure-injection point, including post-flush and response serialization.

### P1-3 — Canonical ordering, exact name derivation and API/CLI serialization diverge

Reversing the 19 wire rows preserved the reversed array in the stored document rather than canonicalizing it to catalog order. Joint/member sort logic is absent. An unchanged generated Balanced template is named `CUSTOM_RESEARCH`. CLI `risk-budget show` is not byte/value-shape identical to the API serializer: the same `created_at` is rendered with a space by CLI and `T` by API (`cli.py:21-29`, `service.py:83-96`).

Required correction: normalize all frozen unordered arrays before hashing/storage/comparison, apply exact name-derivation omissions, and centralize a JSON-safe response DTO/serializer shared by API and CLI.

### P1-4 — `/risk-budget` is a template JSON demonstrator, not the frozen editor

`app.py:119-122` serves one inline `<pre>` plus four buttons and contains zero input controls. It cannot edit/clear any of the 19 rows, class-specific fields, null reasons, horizons, stress/hybrid/joint declarations or the two row-16 component forms. It does not render current version/source/name/status, history, structured differences, stale-draft conflict recovery, or the separate detailed panels required by design section 10. `textContent` is used for the output, which is a correct narrow escaping choice, and no provider tables are queried.

The local server was exercised on an isolated database and returned the page/API successfully, but no compatible browser was connected: browser discovery returned an empty list. Therefore desktop/mobile visual and interactive browser acceptance is **NOT VERIFIED**, not passed.

Required correction: implement the complete form/state/history/conflict UI from the frozen design with safe text rendering and duplicate-submit protection, then repeat the mandated real local browser desktop/mobile scenario on isolated databases, including valid-but-blocked provider permissions.

### P1-5 — Implementer tests do not cover the frozen acceptance matrix

`tests/test_risk_editor.py` contains two tests and 35 lines. It checks one top-level duplicate key, one contradiction, a nominal template save/history path and document update immutability. It does not test most of design section 11. The independent tests are retained in `tests/test_risk_editor_independent_review.py`; they are requirements tests, not implementation fixes.

Required correction: make the reviewer tests pass and add the remaining exhaustive frozen cases: all field/mode cross-products, reason-only changes, null versus zero, component and joint matrices, exact legacy corruption, complete two-session/fault matrix, response serialization, DB constraint/trigger reflection, historical chain corruption and the browser scenario.

## 4. B1–B8 implementation disposition

| Pre-review blocker | Post-implementation disposition | Evidence |
|---|---|---|
| B1 closed schema/catalog/canonical/projection/name | **OPEN / BLOCKING** | Decimal corruption; shallow nested validation; unsorted rows; wrong name; projection divergence accepted. |
| B2 horizon/event-clock identity | **OPEN / BLOCKING** | Generic Horizon shape exists, but prohibited per-row clocks persist 201. Exact 7-year/8-year alignment code is present only for rows 5/7. |
| B3 raw duplicate-safe JSON | **PARTIAL, OPEN / BLOCKING** | Nested duplicate/BOM/NaN/size decoder probes pass; API size/media/encoding status and nested typed-field enforcement fail. |
| B4 class/mode implications | **OPEN / BLOCKING** | Risk/stress/hybrid/joint objects and implication matrix are not validated. |
| B5 deterministic evaluator/status/impact | **OPEN / BLOCKING** | Required findings/blockers absent; preflight diverges; status swallows corruption; changes always empty. |
| B6 atomic two-head CAS/failure semantics | **PARTIAL, OPEN / BLOCKING** | `BEGIN IMMEDIATE`, two-head predicate and projection-fault rollback are present; preview snapshot, SQLITE_BUSY/WRITE_CONFLICT and error/serialization matrix fail or lack evidence. |
| B7 legacy/V1 transitions | **PARTIAL, OPEN / BLOCKING** | Four nominal transitions execute and populated downgrade/re-upgrade preserves rows; exact legacy validation/corruption/comparator diagnostics are absent. |
| B8 immutable marker/document/all-history verifier | **OPEN / BLOCKING** | Update/delete triggers exist, but FK/check contract differs and forged historical envelope/projection drift pass verifier. |

No new design defect was found. These are implementation deviations from the already frozen design; correction should not alter the Policy, ADR-0017 or numerical risk values.

## 5. Positive evidence and bounded limitations

- Shared raw decoder independently rejected duplicate keys at nested M/Risk/Joint locations, UTF-8 BOM, `NaN` and an over-limit byte sequence.
- The save path uses `BEGIN IMMEDIATE` and a conditional profile/risk/mandate head update. Injected projection failure rolled back both successor row and head.
- All four nominal transition categories were exercised: Legacy→Legacy clone, Legacy→V1 full declaration, V1→V1 clone, V1→V1 full declaration.
- On a disposable database populated with 2 risk versions/38 projection rows, downgrade to 0002 and re-upgrade to 0003 preserved those old rows and left zero marker/documents; current then reported `LEGACY_NOT_VERIFIED`. This narrow destructive test was isolated and authorized by the task.
- Existing Phase 1/2 and startup tests remain green; no provider permission, live capture, risk/model or Production state changed.
- Browser interaction is unavailable on this host/session; `browsers.list()` returned `[]`. Source/HTTP review does not substitute for visual acceptance.
- The two existing skipped tests remain Windows host-denied symlink limitations.

## 6. Commands and results

```text
Get-FileHash -Algorithm SHA256 <authority/design/review/implementation files>
  Policy ACF013...E67; design F9EC...B950; pre-review EA061...CF7

uv run pytest -q tests/test_risk_editor.py tests/test_phase1.py tests/test_phase2.py tests/test_verify_startup.py
  74 passed, 2 skipped, 2 warnings

uv run pytest -q --tb=line tests/test_risk_editor_independent_review.py
  27 failed, 2 passed, 2 warnings

uv run pytest -q --tb=no
  27 failed, 76 passed, 2 skipped, 2 warnings

uv run python -m py_compile optivest/risk_editor.py optivest/models.py optivest/service.py optivest/app.py optivest/cli.py optivest/phase2.py alembic/versions/0003_research_risk_editor.py tests/test_risk_editor.py tests/test_risk_editor_independent_review.py
  PASS

uv run python scripts/verify_startup.py --root .
  findings=[]; startup_integrity=PASS; main/UNBORN; dirty=true;
  capability_limits explicitly exclude investment/model/OOS/shadow validation;
  production_readiness=NOT PRODUCTION READY

git diff --check
  PASS for tracked diff; repository files are untracked, so this is not full whitespace coverage
```

Isolated local UI/API database: `upgrade head → seed-research → serve 127.0.0.1:8766 → GET status/catalog → POST generated Balanced template`. Save returned 201, revision 2, `single_name="1"`, `PROVISIONAL`, `NOT PRODUCTION READY`. The server was stopped. The temporary database was not either prohibited workspace DB.

Isolated populated migration sequence: `downgrade 0002_phase2 → upgrade head → verify-risk-editor/risk-budget show`. Final state: revision `0003_research_risk_editor`, 2 risk versions, 38 constraints, 0 markers, 0 documents; verifier returned `VALID`; current reported `LEGACY_NOT_VERIFIED`, 19 rows, `NOT PRODUCTION READY`.

## 7. Reviewed file hashes

| File | SHA-256 |
|---|---|
| `OPTIVEST_AI_POLICY_V10.md` | `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` |
| `AGENTS.md` | `BA424C1B11B4C3CB7AACB86CD870E67D35CAD70D1040DEB5CFD96B4E8B9A3689` |
| `.ai/START_HERE.md` | `66B1A37D397544F66020B65FB323E58F57A49472BAFB23CE2FAE5377ED4B35ED` |
| `.ai/TODO.md` | `A5FBDE6A742E7AA96FC13D06A52684C07CD8D6CF9C49DC3B2E225F147C1C8CF6` |
| `.ai/DECISIONS.md` | `374403BC4A246B610D3342D506D3DCA5CD33FF13652B9920A5117E0DE63C301E` |
| `docs/INITIAL_DESIGN.md` | `43FCCF65CD4320B76D835198E2C18A0DD1FF87F1A0B2E88571B0360A7A65A364` |
| `docs/PHASE1_DESIGN.md` | `C23222188016A4A164C0DBB3434D9B8CA768C91CC3B826523744E47C9FF4CD68` |
| `docs/RESEARCH_RISK_EDITOR_DESIGN.md` | `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950` |
| `docs/reviews/research_risk_editor_pre_review.md` | `EA061F0994AAF176515782CDFE231CA96D7D462F2BC3BE69596CD426FE3AFCF7` |
| `optivest/risk_editor.py` | `A533746072E82B9F5A72048D5D2CF7B0FAB0B670AF950F258504376009166DB0` |
| `optivest/models.py` | `6542D272F65646EDBF2CCC8F809B7A9DCB1019FD30A13D7B32169A8806A81E2B` |
| `optivest/service.py` | `230D7311BF214B9FECA0023679B0D9B985E07002C371DDBCAE91F1BA7D961DED` |
| `optivest/app.py` | `72EFE5DAC4E6FE0A72F10D19CE90F1A7B01388244CC3796730B6EBE774B1E7EA` |
| `optivest/cli.py` | `C5778F664FC2C882B7177D1CBB7321A33F7911E4E7EEB82CD7E4341D99594D1F` |
| `optivest/phase2.py` | `5E92ED6769097114072314CC47E1ADC0B06B2F41C0FC44FD55F2931CAC274560` |
| `alembic/versions/0003_research_risk_editor.py` | `EF528DD240147B093B5F854F0C37F85791385A79DB03DA0535B8EB81119040C6` |
| `tests/test_risk_editor.py` | `0A79D83BDAA957F4811A90F1173F21F91D690D551DB87BBEB2815F3EA21B56B9` |
| `tests/test_risk_editor_independent_review.py` | `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B` |
| `tests/test_phase1.py` | `4B96A7C8CD4E6AD37691A018A6F5C9B32DB9423A3386BA7FA28A9F7C0F73CD20` |
| `tests/test_phase2.py` | `991043DE8631818D7A84267AA02977553F016C30B93E65AA8768F43AEA2F5557` |
| `tests/test_verify_startup.py` | `FA997605EBDF54FA960A3F17FE04999C1E592E2A7F0026DC8DF52DE45393B76D` |

`.ai/HANDOFF.md` was reviewed at SHA-256 `10D664B9C38B58D47845EEEB6185680DFFB3D1F6B2FD4EE40001FF61D3DB25CB` before this validation checkpoint was appended. Final report and operational-record hashes are recorded after the update.

## 8. Required next action

Terra should correct P0-1 through P1-5 without changing the frozen semantics. The first exact action is to replace the numeric normalizer and implement the complete recursive typed grammar/matrix, then make the retained independent tests pass. Next implement the exact evaluator/change engine and all-history verifier, correct transport/error behavior, and build the specified UI. Sol must rerun the full acceptance matrix after corrections. If a correction requires changing ADR-0017 semantics or the 0003 migration strategy beyond the frozen authorization, stop and return `DESIGN CHANGE REQUIRED` to Astra rather than silently redesigning.

No application code was fixed in this review. No Policy/design/ADR/risk value/status/provider permission was changed. No network call, Production DB mutation, prohibited DB access, commit or subagent was used.

## 9. Final independent recheck after Terra correction

Recheck date: 2026-09-09 (Asia/Tokyo)  
Controlling verdict: **IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED**  
Engineering gate: **DO NOT set `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**

Terra corrected every counterexample encoded in the retained reviewer test file without changing that file: its SHA-256 remains `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B`, and all 29 cases now pass. The original decimal corruption, selected shallow mutations, projection/status/preflight probes, public envelope/status mappings, basic ordering/name/CLI checks and minimum HTML-input check are closed for those exact cases.

That is not the complete frozen section 11 matrix. Independent code inspection followed by new disposable-DB probes found the following material counterexamples.

### Recheck blocker R1 — closed schema and class/mode implications remain fail-open

All nine candidates below are forbidden by frozen sections 2, 4 and 6. The real preview endpoint returned HTTP 200 for every one instead of 422:

1. `MODEL_ESTIMATED/ROBUST_CHANCE` with its forbidden fields retaining non-`NOT_APPLICABLE` reasons;
2. `UNSPECIFIED` modeled risk with epsilon populated;
3. chance epsilon `"2"`, outside probability `(0,1)`;
4. row-6 stress `proposed_role="ALIEN"`;
5. Hybrid participation assumption `"101"`, outside `[0,100]`;
6. a joint group containing unknown, recursive and duplicate members plus epsilon `"2"`;
7. row-16 parent with a nonnull fixed-period horizon;
8. TURNOVER component with forbidden unit `MONTHS` and a numeric limit;
9. numeric `123` supplied to `M<string>` definition.

Cause: `validate_declaration()` permits a risk mode name but never applies the selected-mode required/forbidden-field matrix; it does not validate row-6 role enum/implications, Hybrid applicability/range, Joint member/group uniqueness/catalog/class/horizon rules, component unit/currency/applicability, general M text types/trim/length, or the complete per-row horizon catalog (`optivest/risk_editor.py:112-170`). This leaves B1, B2 and B4 blocking.

Required correction: implement the complete recursive type/applicability/range and implication rules, then add exhaustive parameterized tests beyond the retained 29 cases. Rejection must occur before evaluation or DML.

### Recheck blocker R2 — migration and exact all-history verifier remain fail-open

The required fresh populated `upgrade → downgrade 0002 → re-upgrade 0003` sequence itself works narrowly: 2 budget versions and 38 constraint rows survived, editor tables were removed/recreated empty, current became `LEGACY_NOT_VERIFIED`, and exact revision remained `0003_research_risk_editor`.

However, schema reflection and corruption probes failed the frozen contract:

- `PRAGMA foreign_key_list('research_risk_editor_documents')` reports FK target `risk_budget_versions`; frozen section 7 requires the document PK/FK to the marker.
- Migration 0003 still lacks nonblank timestamp CHECKs.
- After re-upgrade, removing one legacy immutability trigger, changing a current legacy metric to `UNKNOWN_METRIC`, changing the root revision to 99, and removing an editor marker update trigger still yielded `verify_risk_editor() = VALID`.
- On a V1 version, removing `created_at`, adding an unknown server-envelope field, recomputing the canonical bytes/digest and updating the isolated rows still yielded `verify_risk_editor() = VALID`.

Cause: `get_document()` checks only a subset of envelope fields and never closes the server envelope; notably `created_at` is omitted (`risk_editor.py:247-268`). `verify_risk_editor()` does not reflect tables/PK/FK/CHECK/trigger definitions and does not validate profile heads, mandate/risk chains or legacy catalog/class/operator/nonfinite invariants (`risk_editor.py:269-278`). This leaves B7 and B8 blocking and violates Policy §16 fail-closed requirements.

Required correction: implement every verifier item from frozen section 9, including schema/trigger reflection, exact closed envelope/timestamp, every profile/head/chain, exact legacy constraints and all historical V1 projections. Corruption must block startup/current/history/editor/preflight.

### Recheck blocker R3 — conflict response and preview transaction contract remain incomplete

Independent two-head/fault probes show the important atomic core now behaves correctly:

- risk-head race: first save 201, second stale save 409, exactly two versions;
- mandate-head movement: stale paired risk save 409, risk version count unchanged;
- injected marker insert failure: 500 `INTERNAL_ERROR`, successor/head rolled back;
- injected third `json.dumps` response-serialization failure: successor/head rolled back;
- retained SQLite lock probe maps to 409 `WRITE_CONFLICT`.

But both stale-head 409 responses contain `error.code="INTERNAL_ERROR"`, not frozen `HEAD_CONFLICT`, because `service.ConflictError` has no `code` and `editor_error()` substitutes `INTERNAL_ERROR` (`optivest/app.py:85-91`). API and CLI therefore expose different states. Preview also still lacks the required explicit consistent read transaction and current observed IDs (`service.py:143-151`). B6 remains blocking.

Required correction: map application head conflicts to exact `HEAD_CONFLICT`, centralize API/CLI error serialization, and implement/test the frozen preview snapshot and observed-head response.

### Recheck blocker R4 — evaluator/difference semantics and browser editor remain incomplete

`diagnostics()` still lacks selected risk-mode incomplete/calibration findings by row, selected stress incomplete findings, complete Hybrid field findings, and nonempty Joint incomplete/not-verified/horizon-contradiction evaluation (`risk_editor.py:187-218`). `declaration_changes()` only classifies paths ending `/limit/value` as if every row used `<=`; it lacks warning/minimum/buffer direction, identity predicates, reason/legacy semantics and affected-field noncomparability (`risk_editor.py:224-236`). B5 remains blocking.

The HTML now contains 21 input elements, enough to satisfy the retained count assertion, but none is read: source inspection/HTTP probe reports `reads_inputs=False`, `has_change_handler=False`, `history_get=False`. The form cannot edit the declaration, components, reasons, horizons or joint definitions and never loads history. It remains a template JSON demonstrator, not the frozen editor.

A fresh isolated local server started successfully, but the required browser runtime again reported no available backend (`[]`). Per the Browser skill, no unrelated automation surface was substituted. Desktop/mobile visual interaction remains **NOT VERIFIED**. The static functional defect independently blocks the non-browser UI contract.

### Final B1–B8 disposition

| Item | Final disposition |
|---|---|
| B1 closed schema/catalog/canonical/projection/name | **OPEN / BLOCKING** — decimal bug fixed, but recursive text/component/joint schema is incomplete. |
| B2 structured horizons/event clocks | **OPEN / BLOCKING** — row-16 parent and other per-row implication coverage remain incomplete. |
| B3 raw duplicate-safe JSON | **CLOSED for independently tested decoder/HTTP boundary**. |
| B4 class/mode matrix | **OPEN / BLOCKING** — risk/stress/hybrid/joint implication counterexamples remain accepted. |
| B5 evaluator/status/impact/differences | **OPEN / BLOCKING** — required deterministic findings and comparison rules remain incomplete. |
| B6 transaction/CAS/serialization | **PARTIAL, OPEN / BLOCKING** — rollback/two-head/lock behavior passes; head-conflict code and preview transaction contract fail. |
| B7 legacy/V1 transitions | **PARTIAL, OPEN / BLOCKING** — nominal transitions/roundtrip pass; malformed legacy chains/catalog remain accepted. |
| B8 DB/verifier | **OPEN / BLOCKING** — FK/check contract and all-history/schema/chain verification remain incomplete. |

### Final commands and results

```text
Get-FileHash -Algorithm SHA256 <authority, design, review, implementation, tests>
  Policy/design/ADR-related files unchanged; retained reviewer test hash unchanged.

uv run pytest -q --tb=line tests/test_risk_editor_independent_review.py
  29 passed, 2 upstream warnings

uv run pytest -q tests/test_risk_editor.py tests/test_risk_editor_independent_review.py
  31 passed, 2 upstream warnings

uv run pytest -q
  103 passed, 2 skipped, 2 upstream warnings

uv run python -m py_compile optivest/risk_editor.py optivest/models.py optivest/service.py optivest/app.py optivest/cli.py optivest/phase2.py alembic/versions/0003_research_risk_editor.py tests/test_risk_editor.py tests/test_risk_editor_independent_review.py
  PASS

uv run python scripts/verify_startup.py --root .
  findings=[]; main/UNBORN; dirty=true; structural-only capability limitations;
  production_readiness=NOT PRODUCTION READY

git diff --check
  PASS for tracked diff; all project files remain untracked

Independent inline API matrix
  9 forbidden candidates above: all returned HTTP 200

Fresh isolated populated migration/corruption script
  migration roundtrip preserved 2 versions/38 constraints;
  corrupt legacy metric/revision plus missing trigger: verifier incorrectly VALID;
  V1 envelope missing created_at plus unknown server key: verifier incorrectly VALID

Two-head/fault inline script
  atomic rollback/interleavings passed; stale 409 code incorrectly INTERNAL_ERROR

Local browser attempt on isolated database/port 8767
  server startup PASS; available browser backends=[]; interaction NOT VERIFIED
```

The two full-suite skips remain host-denied Windows symlink limitations. Several inline TestClient probes emitted Windows temporary-file cleanup warnings after results because Alembic retained a SQLite handle; they do not change the reproduced HTTP/verifier outcomes and no protected database was used.

Final implementation inputs reviewed in this recheck:

| File | SHA-256 |
|---|---|
| `OPTIVEST_AI_POLICY_V10.md` | `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` |
| `docs/RESEARCH_RISK_EDITOR_DESIGN.md` | `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950` |
| `.ai/DECISIONS.md` | `374403BC4A246B610D3342D506D3DCA5CD33FF13652B9920A5117E0DE63C301E` |
| `docs/reviews/research_risk_editor_pre_review.md` | `EA061F0994AAF176515782CDFE231CA96D7D462F2BC3BE69596CD426FE3AFCF7` |
| `optivest/risk_editor.py` | `44D6C8690BF4BE1D4E86B047AFC37C50C6E271514CFDA2781E7B9D7A2B72FE13` |
| `optivest/models.py` | `6542D272F65646EDBF2CCC8F809B7A9DCB1019FD30A13D7B32169A8806A81E2B` |
| `optivest/service.py` | `5B7FA348B6E97150A8A7B9A34DBB1364472ED651B38E499D5291C1A76080ACD5` |
| `optivest/app.py` | `12520E0EDF83EF09A823D46042A8DA908FA2260415096EEC0B38D486B3DB973C` |
| `optivest/cli.py` | `CB6BE592A63F41C5937F192D531E1AB11BBD1D3CAB0E0A9180160E91EDCDFEA1` |
| `optivest/phase2.py` | `5E92ED6769097114072314CC47E1ADC0B06B2F41C0FC44FD55F2931CAC274560` |
| `alembic/versions/0003_research_risk_editor.py` | `372DABEE3644E426320FBCC29E61CB47390166CF2AA8B5AC2C010CAAB96EF918` |
| `tests/test_risk_editor.py` | `0A79D83BDAA957F4811A90F1173F21F91D690D551DB87BBEB2815F3EA21B56B9` |
| `tests/test_risk_editor_independent_review.py` | `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B` |

### Final scope/status statement

The correction materially improved the implementation and closed all previously encoded reviewer tests, but green tests are insufficient when direct frozen-contract counterexamples remain. ADR-0017 engineering acceptance is denied. No numerical feasibility/calibration, model impact, provider/PIT, OOS, shadow or Production gate was evaluated. `RISK BUDGET NOT APPROVED`, all applicable `NOT VERIFIED` states, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain mandatory.

No application code, test, Policy, design, ADR, default risk value, provider permission or approval status was changed by this recheck. No network call, protected DB access, commit or subagent was used.

## 10. Final independent recheck after the second bounded correction

Recheck date: 2026-09-10 (Asia/Tokyo)  
Controlling verdict: **IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED**  
Engineering gate: **DO NOT set `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**

This recheck inspected the actual corrected files and did not rely on the implementer summary. The correction closes the nine exact invalid-preview counterexamples and the previously incorrect stale-head/observed-head behavior, but material frozen section 11 requirements remain unsatisfied.

### Closed by this correction

- The retained independent suite is byte-for-byte unchanged at SHA-256 `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B` and passes **29/29**.
- `tests/test_risk_editor.py` now permanently covers the nine prior HTTP-200 counterexamples. All nine return 422; that file's **11 tests pass**.
- A real two-request race produced exactly one 201 and one 409 `HEAD_CONFLICT`, with two versions and one marker/document. Mandate movement also returned 409 `HEAD_CONFLICT` without a risk successor.
- Marker-insert and third-`json.dumps` response-serialization faults left the version count, document/marker counts and head unchanged. The retained busy-lock case remains 409 `WRITE_CONFLICT`.
- Preview returns matching `observed_current_version_id` and `observed_mandate_version_id` and leaves all row/head counts unchanged.
- Migration document PK/FK now targets the marker. Root revision corruption and an unreconciled document digest are rejected.

### Blocking finding S1 — the recursive closed grammar and canonical rules are still incomplete

Fresh API probes, all within frozen sections 2, 4, 6 and acceptance items 2–5, reproduced these failures:

- row 1 accepts `STRESS_SCENARIO_PATH`, although it permits only `DECISION_TO_HORIZON`;
- a row-16 component accepts `OBSERVATION/ALWAYS`, although component horizons permit only null or fixed-period `DECISION_TO_HORIZON`;
- a PERCENT row accepts currency `USD`, and a CURRENCY row accepts currency reason `NOT_APPLICABLE`;
- a whitespace-only row definition and numeric component definition are accepted;
- duplicate Joint group IDs and reuse of one metric across groups are accepted;
- Joint members are persisted in input order rather than catalog order.

The selected-mode evaluator remains incomplete. A partially declared `ROBUST_CHANCE` produces no `RISK_SEMANTICS_INCOMPLETE`; selected DIAGNOSTIC stress produces no `STRESS_SEMANTICS_INCOMPLETE`; and a nonempty incomplete Joint group removes `JOINT_DEFINITION_MISSING` without adding `JOINT_DEFINITION_INCOMPLETE` or `JOINT_RISK_NOT_VERIFIED`.

The difference engine remains contrary to section 8: increasing a `>=` MIN_LIQUIDITY limit from 10 to 20 is labelled `LOOSER` instead of `TIGHTER`; increasing an allocation minimum is `NOT_COMPARABLE` instead of `TIGHTER`; and a simultaneous definition change does not force the row's numeric comparison to `NOT_COMPARABLE`.

These are not new design requirements. They are unimplemented cases in the frozen section 11 matrix. B1, B2, B4 and B5 remain blocking.

### Blocking finding S2 — exact all-history verification still fails open

A fresh populated isolated database completed 0003 → 0002 → 0003 correctly: two budgets, 38 constraints and one `NOT_VERIFIED` provider survived; both editor tables were removed at 0002 and recreated empty; the current version became `LEGACY_NOT_VERIFIED`; nominal verification returned VALID.

Independent corruption copies then showed:

- replacing one legacy metric with `UNKNOWN_METRIC`, while restoring the exact original immutability trigger, returned `VALID`;
- replacing the risk-constraint update trigger with a same-name no-op definition returned `VALID`;
- a historical V1 envelope with `created_at` removed and an unknown server key added, then canonicalized and rehashed with the exact original triggers restored, returned `VALID`;
- that database passed application startup, status/current/history returned 200, and preflight returned 201 and inserted a snapshot;
- a blank marker timestamp is not prevented by a nonblank CHECK and escapes as raw `ValueError`, rather than the required safe `EDITOR_STORAGE_INVALID` result.

Positive controls: changing the root risk revision to 99 is now rejected, and modifying canonical document bytes without recomputing the marker digest is rejected.

The remaining causes are visible in `verify_risk_editor()`/`get_document()`: trigger names are checked but definitions and exact CHECK/PK contracts are not; legacy rows are not validated against the exact catalog/class/operator/nonfinite rules; and the stored server envelope is not closed or compared on `created_at`. Exposed operations consequently do not fail closed on all historical corruption. B7 and B8 remain blocking under Policy §16 and frozen design section 9.

### Blocking finding S3 — the frozen editor UI and mandatory browser acceptance are incomplete

The page now has 21 inputs, a change listener, a history request and safe `textContent` result rendering. However, the listener handles only `data-metric` and writes only row `limit`; the two `data-component` inputs are disconnected. There are no editable/display contracts for classes, units, null reasons, horizons, risk/stress/hybrid modes and metadata, Joint groups, differences, current version/binding/alignment panels, or explicit stale-draft reload/rebase. The static UI therefore does not implement section 10.

The in-app browser runtime was queried according to the Browser skill and returned no available session (`[]`). Desktop/mobile edit/clear/preview/save/reload/history/stale-conflict/XSS interaction and the blocked-provider repeat remain **NOT VERIFIED**. This is blocking because frozen section 11 item 9 says acceptance *requires* that real local browser exercise; it is not an optional visual-polish check. The non-browser provider boundary itself works: with two seeded `NOT_VERIFIED` datasets, `/risk-budget` and preview return 200 while `/` and `/api/v1/datasets` remain denied at 403.

### Final B1–B8 disposition after the second correction

| Item | Disposition |
|---|---|
| B1 closed schema/catalog/canonical/projection/name | **OPEN / BLOCKING** — exact nine cases closed; text/currency/component/Joint/canonical-member cases remain. |
| B2 horizons/event clocks | **OPEN / BLOCKING** — noncatalog row/component clocks remain accepted. |
| B3 raw duplicate-safe JSON | **CLOSED for independently tested boundary**. |
| B4 class/mode matrix | **OPEN / BLOCKING** — selected incomplete and cross-group implications remain incomplete. |
| B5 evaluator/status/impact/differences | **OPEN / BLOCKING** — required incomplete findings and comparison identity/direction rules fail. |
| B6 transaction/CAS/serialization | **CLOSED for the independently exercised two-head, observed-head, busy and injected-fault contract**. |
| B7 legacy/V1 transitions | **PARTIAL / BLOCKING** — nominal four transitions and migration roundtrip pass; corrupt legacy catalogs still verify. |
| B8 DB/verifier | **OPEN / BLOCKING** — trigger definitions, timestamps, closed envelopes and all-history serving remain fail-open. |

### Commands and exact results

```text
uv run pytest -q --tb=line tests/test_risk_editor_independent_review.py
  29 passed, 2 warnings in 26.97s

uv run pytest -q --tb=line tests/test_risk_editor.py
  11 passed, 2 warnings in 6.82s

uv run pytest -q
  112 passed, 2 skipped, 2 warnings in 60.60s

uv run python -m py_compile <editor/models/service/app/cli/phase2/migration/editor tests>
  PASS

uv run python scripts/verify_startup.py --root .
  startup_integrity=PASS; findings=[]; main/UNBORN; dirty=true;
  production_readiness=NOT PRODUCTION READY; structural-only limitations retained

git diff --check
  PASS; all 18 repository entries remain untracked

Independent migration/verifier scripts against disposable SQLite copies
  nominal 0003: 2 budgets / 38 constraints / 1 provider / 1 document, VALID
  downgrade 0002: same budgets/constraints/provider, 0 editor tables
  re-upgrade 0003: same budgets/constraints/provider, current LEGACY_NOT_VERIFIED, VALID
  corrupt legacy catalog: incorrectly VALID
  same-name no-op trigger: incorrectly VALID
  root revision 99: rejected
  historical unknown/missing-envelope key with recomputed digest: incorrectly VALID
  digest mismatch: rejected

Independent API/CAS/fault script
  preview observed heads: 200 and exact match
  concurrent two-head saves: [409 HEAD_CONFLICT, 201], exactly 2 versions
  moved mandate: 409 HEAD_CONFLICT, risk rows unchanged
  marker failure: 500 INTERNAL_ERROR, head/rows unchanged
  response serialization failure: rollback, head/rows unchanged

Direct CLI on disposable roundtrip DB
  show exit 0; preview exit 0 with observed heads; save exit 0; verifier exit 0
  all outputs retain NOT PRODUCTION READY
```

The two suite skips remain host-denied Windows symlink limitations. Disposable TestClient databases again emitted Windows cleanup warnings because Alembic retained file handles; no result depended on cleanup and no protected database was touched.

### Reviewed hashes after the second correction

| File | SHA-256 |
|---|---|
| `OPTIVEST_AI_POLICY_V10.md` | `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` |
| `docs/RESEARCH_RISK_EDITOR_DESIGN.md` | `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950` |
| `.ai/DECISIONS.md` | `374403BC4A246B610D3342D506D3DCA5CD33FF13652B9920A5117E0DE63C301E` |
| `docs/reviews/research_risk_editor_pre_review.md` | `EA061F0994AAF176515782CDFE231CA96D7D462F2BC3BE69596CD426FE3AFCF7` |
| `optivest/risk_editor.py` | `A28C027597475AA19479840D11FBD34EA28BD14DB55C52E8B0B04988DFBB4F00` |
| `optivest/models.py` | `23FD0B559CCB0134C51C9A7A56E5350BBD7A6837A8A4111EE00AB50BC4B3103E` |
| `optivest/service.py` | `1CCBE59FA1D1096790569D341E8C14E2114BF9A77FC61B3E988FFCC82D7897EE` |
| `optivest/app.py` | `E2F352DFC506FCF574823252E61332E419981ECF8154C5A139BC2A7CB9A2C477` |
| `optivest/cli.py` | `CB6BE592A63F41C5937F192D531E1AB11BBD1D3CAB0E0A9180160E91EDCDFEA1` |
| `optivest/phase2.py` | `5E92ED6769097114072314CC47E1ADC0B06B2F41C0FC44FD55F2931CAC274560` |
| `alembic/versions/0003_research_risk_editor.py` | `3C73EB9423B73FF69156EEFB25EF12A12A601456F324D321C0D60E346AA5E65F` |
| `tests/test_risk_editor.py` | `E59571E36E34867E675553247F2A12BDFED200E3564D2C16E656356E26912BD3` |
| `tests/test_risk_editor_independent_review.py` | `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B` |

No selected Policy/design/ADR/default numerical risk value/provider permission or validation/readiness status changed. This remains engineering conformance review, not risk feasibility, impact or calibration validation. `RISK BUDGET NOT APPROVED`, applicable `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain mandatory. No application/test fix, network call, protected database access, commit or subagent was used.

## 11. Final independent revalidation after the third bounded correction

Recheck date: 2026-09-10 (Asia/Tokyo)  
Controlling verdict: **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`**  
Engineering gate: **DO NOT set `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**

The selected Policy hash remains `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; the frozen design remains `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950`. The retained independent test is byte-identical at `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B` and passes all 29 encoded cases. This evidence does not close newly reproduced frozen-contract failures.

### Blocking finding T1 — closed grammar and raw/API boundary remain incomplete

Direct calls to the current normalizer/validator accepted each of the following although frozen sections 2–4 require rejection or canonical trimming:

- `MAX_RECOVERY_DURATION.limit="0"`, despite positive duration references requiring `>0`;
- TURNOVER component `unit=PERCENT, limit="101"`, despite percent references being `[0,100]`;
- a non-allocation row's inapplicable `minimum` with reason `ARBITRARY`, rather than exact `NOT_APPLICABLE`;
- a changed row-16 aggregate definition, despite the frozen exact definition;
- `confidence_level="2"`, a 129-character risk-version identifier, and a definition value with surrounding whitespace retained instead of trimmed.

The modern envelope also accepts numeric and blank rationale. A numeric expected-current ID is reported as `409 HEAD_CONFLICT`, not a typed `422`. Raw invalid UTF-8 `0xff` maps to `JSON_INVALID`, not frozen `JSON_ENCODING`. The otherwise valid media type `application/json;charset=utf-8` is rejected as 415. A missing version returns the frozen code nested under FastAPI `detail` instead of the editor error envelope. These failures keep B1/B3/B4 and acceptance items 2–4 open.

### Blocking finding T2 — evaluator and deterministic diagnostic contract remain incomplete

A fully populated Joint group with a 6-year horizon and two 7-year members returns `NO_KNOWN_CONTRADICTION`; `JOINT_HORIZON_CONTRADICTION` is absent. Selected incomplete `ROBUST_CHANCE` correctly adds `RISK_SEMANTICS_INCOMPLETE` to the standalone blocker list, but no corresponding BLOCKER finding exists. The same defect affects the mandatory approval, feasibility, impact, calibration, stress, hybrid, Joint, benchmark/passive and risk-free blocker codes. Therefore `blockers` is not derived from BLOCKER findings as frozen.

Finding order is lexicographic by JSON pointer (`constraints/10` before `constraints/2`), not severity then catalog ordinal then code. Component ranges/contradictions and several applicable-field missing findings are likewise absent. Earlier directional `>=`, allocation-minimum and row-definition difference probes now pass, but this does not close the incomplete evaluator contract. B5 remains blocking.

### Blocking finding T3 — exact schema, canonical history and downgrade/re-upgrade remain fail-open or broken

Three fresh disposable SQLite databases produced independent failures:

1. A historical V1 document with the 19 constraint array reversed, then canonical object-key encoding and a recomputed digest with the exact immutable triggers restored, returned verifier `VALID`. Application startup succeeded; status/history returned 200; preflight returned 201 and inserted a decision snapshot. Array order is therefore not enforced for all history.
2. Adding an unauthorized column to `research_risk_editor_markers` still returned verifier `VALID`; the verifier searches required DDL substrings but does not enforce the exact closed table schema.
3. A historical V1 document/projection/name consistently changed to `LEVERAGE=1`, rehashed with exact triggers restored, was independently evaluated as `RISK BUDGET INCONSISTENT` but returned verifier `VALID`. Stored V1 contradictions therefore remain unverified.

The mandatory populated migration roundtrip also regressed. CLI show/preview/save/verify succeeded first, with 2 budgets, 38 constraints, 2 providers and 1 editor document. Downgrade to 0002 preserved the budgets/constraints/providers and removed editor tables. After re-upgrade, the V1-derived rows correctly remained `>=`, but the legacy verifier hardcodes `<=` for the two minimum metrics and raises `EDITOR_STORAGE_INVALID`. Frozen section 9 requires these document-stripped rows to reclassify as legacy after the authorized isolated roundtrip. B7/B8 and acceptance items 6/8 remain blocking.

### Blocking finding T4 — preview snapshot and response contracts remain incomplete

SQL trace of a successful preview captured 19 statements and no explicit `BEGIN`; the frozen consistent SQLite read transaction is still absent. Version timestamps serialize as a naive value such as `2026-09-09T23:31:35.565277`, without the required terminal `Z`. Legacy version diagnostics omit `mandate_version_binding`, `risk_horizon_alignment` and `impact`, and legacy `/api/v1/status` omits `risk_editor_diagnostics`. B6 is therefore reopened for the unimplemented preview/response portion even though the exercised write CAS, rollback and busy-lock behavior remains sound.

### UI and real-browser result

The in-app browser was available and exercised against a fresh isolated 0003 database containing the valid `NOT_VERIFIED` two-provider matrix. Desktop 1280x800 and mobile 390x844 had no horizontal overflow. Template load, edit, explicit null/reason clear, preview, provisional save, reload, history, stale conflict and XSS-safe output all worked. The stale draft was preserved, and `<img src=x onerror=alert(1)>` appeared as text with zero image elements. The editor remained 200 while `/` and `/api/v1/datasets` returned 403 `BLOCKED_POLICY`.

However, the served UI is one raw JSON textarea plus 19 hidden compatibility anchors. It does not provide the frozen per-row/class/unit/reason/horizon/risk/stress/hybrid/Joint controls, does not group row 16 into two named component forms, and leaves the row-16 aggregate editable in raw JSON. The second form implementation below the first `return` in `app.py` is unreachable. Thus the browser mechanics are evidenced, but section 10 UI conformance and acceptance item 9 remain **FAIL / BLOCKING**, not visual polish.

### Section 11 acceptance disposition

| Item | Disposition |
|---|---|
| 1 pre-review and freeze | **PASS** — exact hashes and ADR-0017 verified. |
| 2 normalized roundtrip/projection/differences | **FAIL / BLOCKING** — closed values/trimming and canonical historical array enforcement fail. |
| 3 raw JSON/type boundary | **FAIL / BLOCKING** — invalid UTF-8 code and modern request typing fail, despite duplicate/BOM/nonfinite/size/depth decimal negatives passing. |
| 4 class/mode/bounds/contradictions | **FAIL / BLOCKING** — positive/range/applicability/evaluator cases remain open. |
| 5 horizons/Joint/mandate alignment | **FAIL / BLOCKING** — fully specified Joint contradiction is missed. |
| 6 four transitions/legacy preservation | **FAIL / BLOCKING** — nominal four transitions pass, but the required V1-to-legacy migration roundtrip fails. |
| 7 races/faults/read transaction | **FAIL / BLOCKING** — write CAS/fault rollback/busy behavior passes; preview has no explicit read transaction. |
| 8 migration/schema/corruption/all-history | **FAIL / BLOCKING** — exact schema, canonical history, evaluator contradiction and roundtrip failures reproduced. |
| 9 real browser | **FAIL / BLOCKING** — required interactions were run, but the frozen structured editor contract is not implemented. |
| 10 regression/compile/startup/diff and independent check | **FAIL / BLOCKING overall** — automated checks pass, but direct independent failures remain. |
| 11 operational records/status boundaries | **PASS after this update** — numerical/model/provider/PIT/OOS/shadow/Production statuses remain unpromoted. |

### Commands and exact results

```text
uv run pytest -q --tb=line tests/test_risk_editor_independent_review.py tests/test_risk_editor.py
  51 passed, 2 warnings in 21.12s

uv run pytest -q
  123 passed, 2 skipped, 2 warnings in 49.18s

uv run python -m py_compile <editor/models/service/app/cli/phase2/migration/editor tests>
  PASS

uv run python scripts/verify_startup.py --root .
  startup_integrity=PASS; findings=[]; main/UNBORN; dirty=true;
  production_readiness=NOT PRODUCTION READY

git diff --check
  PASS for tracked diff only; all 18 repository entries remain untracked

Independent inline grammar/evaluator/API probes
  accepted the T1 cases; Joint mismatch remained NO_KNOWN_CONTRADICTION;
  mandatory blocker findings absent; bad UTF-8 returned JSON_INVALID

Independent SQLite corruption/serving probes
  unsorted historical V1: verifier VALID, startup/status/history/preflight succeeded;
  unauthorized schema column: verifier VALID;
  historical LEVERAGE=1 contradiction: verifier VALID

Independent populated migration/CLI probe
  show/preview/save/verify exit 0 before downgrade;
  before=(2 budgets,38 constraints,2 providers,1 document);
  0002=(2,38,2,0 editor tables);
  re-upgrade verify: EDITOR_STORAGE_INVALID

Actual in-app browser on isolated port 8768
  desktop/mobile edit/clear/preview/save/reload/history/stale/XSS exercised;
  provider-blocked editor 200, home/datasets 403
```

The two suite skips remain the documented host-denied Windows symlink limitations. The browser server and every corruption/migration probe used disposable databases. One setup command briefly fell through to the ignored repository `optivest.db` after a PowerShell path-expression error; read-only inspection showed all logical seed rows retained their original 2026-09-08 timestamps and counts, and no permission/status/value changed, but the file modification time advanced. No destructive rollback was attempted.

Current implementation hashes: `risk_editor.py` `C62E6F1D3AF59AE2472893C9BCB4020F8C60168002210B986ADCC4D721A061EB`; `models.py` `6E429EB87E7A1C70C0AA55FD3CA20EDAAF569287BCB3554A7FBB3CB6C112AE8A`; `service.py` `836BF44B21CA56665CD53941857D2E5D688462CB29776225BCE26D9ACCFB81B5`; `app.py` `771E79D62BDEE1A97A89A0B031D7B5F5C5EF8207269B3B95079F5BCB833A8D9F`; migration `5C80BE89EADBE15FDBEDBDAB55AA0BF581435C160A33958864B9595AA6041DE9`; implementer test `CF5775E252B4201B60DA666C180EA9691A37B6D86688283ED144596F893FE128`.

No application code, test, Policy, design, ADR, risk value, provider permission or readiness status was changed by this review. No network/provider call, commit or subagent was used. Numerical feasibility, impact, calibration, `U_risk`, `S_stress`, provider/PIT truth, OOS, shadow and Production remain `NOT VERIFIED`/unpassed as applicable; `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain mandatory.

## 12. Independent revalidation of the bounded T1–T4 correction

Recheck date: 2026-09-13 (Asia/Tokyo)  
Controlling verdict: **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`**  
Engineering gate: **DO NOT set `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**

The selected Policy SHA-256 is exactly `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; the ADR-0017 frozen design SHA-256 is exactly `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950`. Git remains `main` / `UNBORN`; all repository entries are untracked, so `git diff --check` covers whitespace only and cannot establish complete change identity.

### Closed T3/T4 findings

Independent fresh, disposable SQLite probes close the specifically dispatched persistence and transaction failures:

- Populated `0003 -> 0002 -> 0003` preserved 2 budgets, 38 constraints and 2 providers; editor tables were removed/recreated; the document-stripped current head verified `VALID` as `LEGACY_NOT_VERIFIED`; both minimum metrics retained the historical `>=` comparators.
- Reversed historical V1 constraint arrays with canonical object-key encoding and a recomputed digest, an unauthorized marker-table column, and a rehashed/reprojected historical `LEVERAGE=1` contradiction each caused status and preflight 503 `EDITOR_STORAGE_INVALID`, inserted zero snapshots, and blocked fresh application startup.
- Successful preview emitted an explicit SQL `BEGIN` before verifier/head/document reads. Counts for budgets, constraints, markers, documents and decision snapshots were identical before/after preview.
- Legacy status and version responses both contained `mandate_version_binding`, `risk_horizon_alignment` and `impact`; version `created_at` ended in UTC `Z`; preview returned both observed head IDs.
- A two-client race produced exactly one 201 and one 409 `HEAD_CONFLICT`, with 2 budgets, 38 constraints and 1 V1 document afterward. Retained projection-fault rollback and SQLite-busy checks also passed.

### Blocking finding U1 — reserved `NOT_APPLICABLE` still passes on applicable fields

Frozen section 2 says `NOT_APPLICABLE` is exact and exclusive to inapplicable fields. Direct independent validation nevertheless accepted all three candidates below:

1. `MAX_MODELED_DRAWDOWN.risk.mode=ROBUST_CHANCE` with applicable `epsilon={value:null,reason:"NOT_APPLICABLE"}`;
2. `MAX_STRESS_DRAWDOWN.stress.proposed_role=BINDING` with applicable `version={value:null,reason:"NOT_APPLICABLE"}`;
3. `MAX_FACTOR_CLUSTER.hybrid.observed_component={value:null,reason:"NOT_APPLICABLE"}`.

Root cause: `optivest/risk_editor.py` validates the exact reserved reason only for forbidden/inapplicable fields and one row-definition special case. Selected Risk fields at lines 225–237, selected Stress fields at lines 242–245, and applicable Hybrid fields at lines 246–253 accept any nonblank null reason. This violates the closed M-wrapper/applicability grammar and keeps acceptance items 3–4 and B1/B4 open.

### Blocking finding U2 — mobile structured editor overflows

The actual in-app browser rendered 19 structured risk rows, 2 named row-16 component fieldsets, and no editable row-16 aggregate inputs. Desktop 1280x800 had no horizontal overflow. At 390x844, however, `documentElement.scrollWidth > clientWidth` (`445 > 390` effective page viewport); long unbreakable metric headings widened rows, especially `MAX_TURNOVER_IMPLEMENTATION_COST` and `MIN_DATA_EVIDENCE_INTEGRITY_CONFIDENCE`. The one-line stylesheet lacks wrapping/min-width rules for metric headings and row/header containers. This is a real mobile acceptance failure, not merely static inspection.

Desktop edit, explicit clear/reason, preview, provisional save, reload, history, stale conflict and XSS probes otherwise passed. The saved `<img src=x onerror=alert(1)>` definition was displayed as text with zero `img` elements and no dialog. A stale draft retained its edited value and disabled save. At mobile size, edit/clear/preview also worked despite overflow. On the seeded valid-but-`NOT_VERIFIED` provider matrix, `/risk-budget` returned 200 while `/` and `/api/v1/datasets` returned 403 `BLOCKED_POLICY`; the browser control surface represented direct navigation to those denied responses as client-blocked.

The live editor is now structurally implemented, but its current summary does not explicitly expose the current declaration's `source_preset` and name as required by frozen section 10. History shows the name, and template-load state implies a preset, but neither substitutes for the required current-version fields.

### Blocking finding U3 — retained reviewer suite and live-JS contract disagree

The retained independent test `test_risk_editor_page_exposes_actual_row_and_component_edit_controls` inspects the initial server HTML and requires at least 19 `<input>` elements. The current page contains one rationale input and creates the actual row/component controls from deferred `risk_editor.js`, so the focused run and full suite both fail at line 570 with `assert 1 >= 19`. Live browser evidence proves that the controls exist after load; therefore this is partly a stale static-test assumption, not evidence that the dynamic controls are absent. Acceptance item 10 still requires the retained and new suites to pass. Resolve the contract without restoring hidden compatibility anchors: either provide honest progressive server-rendered structured controls that are hydrated/replaced, or have an independently owned browser-capable reviewer test supersede the static assertion while preserving equivalent frozen coverage. Terra must not silently weaken/delete the independent assertion.

### Section 11 acceptance disposition

| Item | Disposition |
|---|---|
| 1 pre-review and freeze | **PASS** — exact Policy/design hashes and ADR-0017 freeze verified. |
| 2 normalized roundtrip/projection/differences | **PASS for exercised frozen cases** — permutation/name/reason-only/null-vs-zero/projection and populated roundtrip probes passed. |
| 3 raw JSON/type boundary | **FAIL / BLOCKING** — retained raw/API cases pass, but applicable M wrappers accept the reserved `NOT_APPLICABLE` reason. |
| 4 class/mode/bounds/contradictions | **FAIL / BLOCKING** — the same Risk/Stress/Hybrid applicability defect violates the exhaustive closed matrix. |
| 5 horizons/Joint/mandate alignment | **PASS for exercised cases** — 7Y vs 84M, 8Y current-binding mismatch and populated Joint contradiction behavior passed. |
| 6 four transitions/legacy preservation | **PASS** — retained four-transition test passes; populated downgrade/re-upgrade now preserves and reclassifies correctly. |
| 7 races/faults/read transaction | **PASS for exercised SQLite contract** — race/fault/busy behavior and explicit preview read transaction passed. |
| 8 migration/schema/corruption/all-history | **PASS for dispatched adversarial probes** — reversed arrays, extra column and historical contradiction fail closed through startup/status/preflight. |
| 9 real browser | **FAIL / BLOCKING** — structured mechanics/XSS/stale/provider boundary pass, but mobile overflow and missing explicit current preset/name remain. |
| 10 regression/compile/startup/diff and independent check | **FAIL / BLOCKING** — compile, JS syntax, startup and diff checks pass; focused/full pytest each have the retained static-HTML failure. |
| 11 operational records/status boundaries | **PASS after this update** — numerical/model/provider/PIT/OOS/shadow/Production gates remain unpromoted. |

### Commands and exact results

```text
uv --cache-dir .uv-cache run pytest -q --tb=line tests/test_risk_editor_independent_review.py tests/test_risk_editor.py
  1 failed, 59 passed, 2 warnings in 25.09s
  failure: tests/test_risk_editor_independent_review.py:570, initial HTML has 1 input, expected >=19

uv --cache-dir .uv-cache run pytest -q --tb=line
  1 failed, 131 passed, 2 skipped, 2 warnings in 95.05s
  same retained UI assertion; skips remain host-denied symlink cases

uv --cache-dir .uv-cache run python -m py_compile <editor/models/service/app/cli/phase2/migration/editor tests>
node --check optivest/static/risk_editor.js
git diff --check
  PASS

uv --cache-dir .uv-cache run python scripts/verify_startup.py --root .
  startup_integrity=PASS; findings=[]; main/UNBORN; dirty=true;
  production_readiness=NOT PRODUCTION READY

Independent populated migration probe
  before=(2 budgets,38 constraints,2 providers,1 document)
  at 0002=(2,38,2; editor tables absent)
  re-upgrade=(2,38,2,0 documents); verifier VALID; head LEGACY_NOT_VERIFIED; minimum operators >=/>=

Independent corruption/serving probes (three separate disposable DBs)
  reversed historical arrays: status 503; preflight 503; snapshots 0->0; startup blocked
  unauthorized marker column: status 503; preflight 503; snapshots 0->0; startup blocked
  historical LEVERAGE=1: status 503; preflight 503; snapshots 0->0; startup blocked

Independent preview trace
  first statement BEGIN; one explicit BEGIN; all checked row counts unchanged;
  observed head IDs present; legacy diagnostic envelopes complete; created_at ends Z

Independent two-client race
  one 201, one 409 HEAD_CONFLICT; final counts=(2 budgets,38 constraints,1 document)

Actual in-app browser / isolated provider-blocked DB
  desktop 1280x800: 19 rows, 914 inputs, 114 selects, 2 components, no overflow
  mobile 390x844: edit/clear/preview works but horizontal overflow=true; widest page content 445px
  desktop save/reload/history/stale/XSS passed; editor 200; home/datasets 403 BLOCKED_POLICY
```

### Bounded Terra-ready fix list

1. Enforce the section-2 reserved-reason invariant centrally for every applicable M wrapper. Add permanent API and direct-schema regressions for the three U1 candidates; preserve null-with-other-nonblank-reason as an incomplete savable declaration where the frozen mode permits it.
2. Make all metric headings and nested row/component containers wrap/shrink at 390px; add a deterministic responsive regression plus real-browser recheck. Explicitly display current version name and `source_preset` (or the legacy unavailable state) in the current declaration summary.
3. Reconcile the retained static-HTML assertion with the now-dynamic editor without hidden anchors or weakened frozen coverage. An independent reviewer must approve any reviewer-test change. Then rerun focused/full suites and the exact browser mobile matrix.

No application code, test, Policy, design, ADR, default risk value, provider permission or readiness status was changed by this revalidation. No network/provider capture, protected/user database access, deployment, commit or subagent occurred. All destructive migration/corruption probes used disposable SQLite databases. Numerical feasibility, impact, calibration, `U_risk`, `S_stress`, provider/PIT truth, OOS and shadow remain `NOT VERIFIED`/unpassed as applicable; `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain mandatory.

## 13. Final independent U1-U3 correction recheck

Recheck date: 2026-09-13 (Asia/Tokyo)  
Controlling scoped verdict: **`PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**  
Prior implementation verdict: **CLOSED for the frozen RESEARCH-RISK-EDITOR-V1 engineering scope**

This is an engineering-conformance acceptance only. It does not approve a numerical Risk Budget or validate feasibility, impact, calibration, a risk/forecast/optimizer model, provider/PIT truth, OOS, shadow, personalization or Production use.

### Authority and unchanged reviewed inputs

- Selected Policy SHA-256: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.
- Frozen design SHA-256: `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950`.
- Retained independent reviewer test SHA-256: `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B`, byte-identical to the previously recorded reviewer artifact.
- Repository remains `main` / `UNBORN`; all project entries are untracked. `git diff --check` is therefore a whitespace check, not complete provenance.
- No Policy, frozen design, ADR semantics, provider permission, risk value, application code or test file was changed during this recheck.

### U1-U3 closure evidence

- **U1 PASS.** `_require_applicable_m` rejects the reserved null reason `NOT_APPLICABLE` for selected Risk fields, selected Stress fields and applicable Hybrid fields. In addition to the permanent three-candidate tests, an independent mutation matrix exercised every required field for `ROBUST_CHANCE`, `ROBUST_QUANTILE` and `EQUIVALENT_BUFFER`; every selected `DIAGNOSTIC`/`BINDING` Stress field; and every applicable Hybrid field on `MAX_FACTOR_CLUSTER`, `MAX_DAYS_TO_LIQUIDATE` and `MIN_LIQUIDITY`. All 30 direct candidates and the same 30 API preview candidates rejected with `FIELD_NOT_APPLICABLE`. A nonreserved nonblank reason remained accepted as an incomplete declaration through both direct and API paths, so the fix did not collapse draft missingness into rejection.
- **U2 PASS.** A real local browser rendered 19 structured rows and both row-16 component fieldsets. The row-16 aggregate had zero direct editable controls. At the requested 390x844 viewport, the effective document width was 375 and `scrollWidth == clientWidth == 375`; no element extended beyond the document edge. The same structured page had no horizontal overflow at the normal desktop viewport. Current V1 presentation explicitly showed `name=CUSTOM_RESEARCH` and `source_preset=BALANCED_RESEARCH_V1` after a provisional edit/save/reload cycle.
- **U3 PASS.** Initial server HTML exposes 19 genuine visible labelled readonly declaration controls plus the separate rationale input; they are not hidden compatibility anchors. Hydration removes the initial fieldset and renders the 19 editable structured rows. The retained independent test was not edited and now passes.

### Browser and operational behavior

On the disposable isolated SQLite database, the browser exercised structured edit, explicit clear with `DEFINITION_NOT_VERIFIED`, preview-before-save, provisional save, reload, history growth, stale-head conflict with unsaved draft preservation, and XSS-safe text/property rendering. The XSS payload created no `img` element and no JavaScript dialog. A stale preview reported the explicit conflict, preserved the changed `MONTHS` value and kept save disabled. With the two Phase 2 provider declarations seeded as `NOT_VERIFIED`, `/risk-budget` remained HTTP 200 while `/` and `/api/v1/datasets` returned HTTP 403 `BLOCKED_POLICY`; no provider/network capture occurred.

The file `data/browser_u3_20260913.db` was confirmed to be the disposable browser artifact: it was created with the Terra review helper, its still-running local port-8768 helper exposed the same current risk-budget ID, and no other repository reference treated it as a user database. The helper was stopped and the database was removed; `Test-Path` returned false afterward. `phase2_check.db`, `optivest.db` and all user/protected databases were untouched.

### Commands and exact results

```text
uv --cache-dir .uv-cache run pytest -q --tb=line tests/test_risk_editor_independent_review.py tests/test_risk_editor.py
  63 passed, 2 warnings in 24.55s

uv --cache-dir .uv-cache run pytest -q --tb=line
  135 passed, 2 skipped, 2 warnings in 57.24s
  skips remain the documented host-denied Windows symlink cases

Independent applicable-wrapper mutation matrix
  30/30 direct candidates rejected FIELD_NOT_APPLICABLE
  30/30 API candidates returned 422 FIELD_NOT_APPLICABLE
  nonreserved incomplete null reason accepted directly and through API

uv --cache-dir .uv-cache run python -m py_compile <editor/models/service/app/cli/phase2/migration/editor tests>
node --check optivest/static/risk_editor.js
git diff --check
  PASS

uv --cache-dir .uv-cache run python scripts/verify_startup.py --root .
  startup_integrity=PASS; findings=[]; main/UNBORN; dirty=true;
  production_readiness=NOT PRODUCTION READY

Real local browser
  initial HTML: 19 visible labelled readonly row controls plus rationale
  hydrated: 19 rows, 2 components, initial fieldset removed, row-16 aggregate direct inputs=0
  mobile 390x844: clientWidth=375, scrollWidth=375, overflow offenders=0
  current V1: name=CUSTOM_RESEARCH, source_preset=BALANCED_RESEARCH_V1
  edit/clear/preview/save/reload/history/stale/XSS: PASS
  provider-blocked matrix: editor=200; home=403 BLOCKED_POLICY; datasets=403 BLOCKED_POLICY
```

The independent wrapper probe printed a Windows interpreter-exit warning because the test helper retained an isolated temporary SQLite handle; all assertions completed and the process exit code was zero. This is the same bounded host cleanup limitation, not a failed application assertion. The repository browser artifact itself was removed after all browser processes were stopped.

### Final section-11 disposition

All eleven frozen acceptance items are now satisfied for the bounded SQLite/API/CLI/same-process-editor engineering contract. Previously accepted T1-T4 persistence, transaction, migration, verifier, raw-boundary and evaluator evidence remains applicable because the U1-U3 change did not alter those semantics, and the focused plus complete regression suites reproduce it without failure.

Final scoped status: **`PASS_ENGINEERING_RESEARCH_RISK_EDITOR`**.

Mandatory limits remain unchanged: **`RISK BUDGET NOT APPROVED`**; numerical feasibility, impact and calibration **`NOT VERIFIED`**; provider permission/PIT truth, investment model and OOS **`NOT VERIFIED`**; **`SHADOW VALIDATION NOT PASSED`**; **`NOT PRODUCTION READY`**. TODO numerical/model/provider work remains open. Design deviations: **NONE**.
