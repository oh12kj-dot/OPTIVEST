# RESEARCH-RISK-EDITOR-V1 independent pre-implementation review

Date: 2026-09-09, Asia/Tokyo. Reviewer role: GPT-5.6 Sol, independent falsification-first review. Review target: `docs/RESEARCH_RISK_EDITOR_DESIGN.md` SHA-256 `5E275D4095A20886193771C1E645AE4765FC5BA6A0E5F8D22CAE427082F10883`.

## Verdict

**`DESIGN CHANGE REQUIRED / NOT READY FOR DECISION FREEZE`**.

The bounded outcome is appropriate: an immutable, research-only declaration editor may persist provisional drafts while numerical portfolio feasibility, sensitivity, calibration, approval and Production remain `NOT VERIFIED`. This is not numerical risk validation and cannot satisfy Policy section 18 risk/model/Production gates. The proposed design also correctly keeps provider capture independent and preserves `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY`.

The draft is not freezeable yet. Eight blocking contract gaps below would require Terra to choose material data, validation, concurrency or compatibility semantics. Correct the draft and obtain a new independent review against its new hash before any ADR freeze or application implementation.

## Independent baseline before reading the proposal

The selected Policy was read in full after its raw-byte hash was independently reproduced. Policy section 8 requires separately classified constraints, metric definition/horizon/confidence/method/window, fail-closed Structural Hard behavior, explicitly unverified Model-Estimated/Hybrid results, separated `U_risk` and `S_stress`, no double counting, horizon-compatible joint-risk semantics, provisional editable research profiles, and a consistency/feasibility gate. Sections 4, 16 and 17 require a pre-review and freeze before material implementation, no inferred required inputs or approvals, Policy-as-Code enforcement, current operational records and explicit unverified results. Section 18 is a 25-item AND gate; an editor or syntactically valid declaration does not validate any numerical risk item.

Current code independently establishes the implementation baseline:

- `service._constraints()` creates exactly 19 compatibility metrics (12 reference-valued and 7 null), while `risk_successor()` replaces every successor with the Balanced seed rather than cloning current rows (`optivest/service.py:17-23,60-63`).
- `risk_constraints` uses floating columns and is immutable; profile heads are mutable CAS pointers (`alembic/versions/0001_phase1.py:17-18,29-31`).
- The current risk API accepts metadata only and exposes current compatibility rows (`optivest/app.py:44,78-86`).
- The app and `verify_phase2()` currently require exact Alembic revision `0002_phase2`; the home page is guarded by provider `INTERNAL_DISPLAY` permission (`optivest/app.py:13-31,60-64,180-188`; `optivest/phase2.py:399-440`).
- Existing preflight always denies research-decision eligibility and Production, but it requires current mandate/risk heads to be coherently paired (`optivest/service.py:65-86`).

## Blocking findings and required corrections

### B1 — No normative document/wire schema or exact compatibility projection

The prose names fields but does not define the complete JSON object shape, exact field names, types, required/null rules, per-field reason keys, server-owned versus client-supplied values, list ordering, or normalization. It also does not give an exact 19-row catalog/projection table. In particular, the relation among document `source_preset`, `RiskBudgetVersion.name`, `risk_constraints`, proposed stress binding, `u_risk_version`, and the legacy aggregate cost row is not deterministic. “Terra uses the same typed parser” is not an implementable frozen specification without these details.

Required correction:

1. Add a normative request/document/response schema or complete typed example with every key and closed enum.
2. Add an exact catalog table for all 19 metric IDs: fixed class, comparator, permitted units, template values, minimum-field applicability, horizon type, and compatibility projection for every existing column.
3. Define the canonical normalized stored representation and stable ordering. Define whether numeric values are bounded decimals or binary floats, including precision/scale and equality/diff behavior.
4. Make preset classification and `RiskBudgetVersion.name` server-derived. A client may request a template but cannot assert `BALANCED_RESEARCH_V1` or `GROWTH_RESEARCH_V1` when normalized values differ; such a declaration must be `CUSTOM_RESEARCH`.
5. Define the legacy aggregate turnover/cost row exactly. If it remains compatibility-only, mark it non-editable, keep its projected numeric fields null/`UNSPECIFIED`, give distinct stable nested IDs to turnover and implementation cost declarations, and state that they cannot be arithmetically combined.

Acceptance addition: round-trip the normative example through API, CLI, DB document and projection; assert byte-independent semantic equality and reject a preset/name spoof.

### B2 — Free-text horizons cannot enforce the promised horizon and joint-event rules

The draft makes evaluation horizon and joint horizon free text, then requires a common horizon and rejection when member horizons differ. Text cannot safely determine equivalence (`7 years`, `84 months`, and a path ending at year 7 may or may not share an event clock). It also says a mandate successor makes the prior budget “unaligned until a successor is saved”, but binding a cloned budget to a new mandate version does not prove that any risk horizon was semantically changed or should equal the investment horizon. Policy section 8 explicitly forbids undefined cross-horizon aggregation.

Required correction:

1. Use a structured horizon declaration with an exact kind/unit/value (or an explicit catalog-fixed horizon) plus a separately structured event-clock identifier/basis. Free text may remain explanatory only.
2. Permit a joint group only when every member has the same normalized horizon/event clock and the group repeats that exact identity. Cross-horizon conversion remains rejected, not inferred.
3. Separate `mandate_version_binding` from `risk_horizon_semantic_alignment`. Saving against the current mandate can make the version binding current; it must not relabel or certify stored risk horizons.
4. Define which metrics are expected to follow the mandate horizon and which intentionally use normal-liquidity, recovery, stress or other clocks. Do not apply one blanket equality test.

Acceptance addition: include equivalent-looking but distinct horizon/event-clock negatives, a mandate race, and an 8-year mandate successor that preserves explicit 7-year declarations without falsely reporting semantic alignment.

### B3 — The duplicate-key requirement is not achievable through the current FastAPI/Pydantic request path as specified

FastAPI normally converts JSON to a mapping before Pydantic validation; duplicate object keys have already collapsed by then. A standard `BaseModel(extra="forbid")` cannot detect them. CLI parsing can fail the same way if it uses ordinary `json.load`. The draft requires duplicate-key rejection but does not freeze the raw parsing boundary.

Required correction:

Define one strict raw JSON decoder used before typed validation by both API and CLI, with duplicate-key detection at every object depth, strict UTF-8/JSON content handling, non-finite rejection, numeric normalization, and a bounded request/file size. The API must not first bind the body to a Pydantic model. Parser errors return stable field/code diagnostics without echoing arbitrary file/body content.

Acceptance addition: duplicate keys at envelope, constraint, nested buffer, joint-group and reason levels must all fail with no inserts or head movement.

### B4 — Allowed semantics by constraint class are incomplete

The draft limits stress fields to stress rows, but does not fully specify which classes may select `ROBUST_CHANCE`, `ROBUST_QUANTILE` or `EQUIVALENT_BUFFER`, or which fields must be absent under every mode. As written, a Structural Hard row could carry probabilistic semantics, a Model-Estimated row could be left with an apparently selected but unevidenced buffer, or compatibility `binding_status=DIAGNOSTIC` could conceal the relation to a proposed stress `BINDING` role. That violates the Policy's class separation and fail-closed intent.

Required correction:

Add a closed class-by-semantics matrix and field implication table. Structural Hard rows cannot carry `U_risk`, chance, quantile, buffer or stress semantics. Stress rows use only `S_stress` fields and never `U_risk`. Model-Estimated and the estimated component of Hybrid rows may carry the approved draft robust forms. Observed Hybrid assumptions remain separately labelled and unmeasured. An incomplete proposed mode may be stored only with a machine blocker and must be described as uninterpretable/unverified, never as a valid constraint. Define exact projection behavior for proposed stress binding and equivalent buffers; no current compatibility field may imply approval or calibration.

Acceptance addition: exhaustively test every forbidden cross-class field combination and prove that supplied epsilon/alpha, `BINDING`, buffer value, evidence text or confidence text cannot alter server-controlled statuses.

### B5 — The evaluator and public status contract are not deterministic

The six proposed evaluator outputs are not accompanied by closed value vocabularies, finding severities/codes, exact blocker precedence, exact save/preview HTTP outcomes, or a complete list of deterministic consistency rules. “Known semantic contradictions” leaves Terra to decide what is inconsistent. API, CLI, UI, status and preflight could therefore disagree while each appears to follow the prose.

Required correction:

1. Freeze exact result schemas and allowed values for `input_validation`, `consistency_findings`, `feasibility_status`, `impact`, `validation_status`, `risk_budget_status` and `production_readiness`.
2. Enumerate deterministic input/consistency rules and stable codes, including per-metric unit applicability, bounds, warning direction, leverage zero, allocation minimum/maximum logic, mutually exclusive allocation minimum totals where applicable, semantics-field implications, joint references and horizon/event-clock equality.
3. Define invalid-input versus valid-but-inconsistent versus valid-provisional behavior and exact 422/409/200/201 outcomes. Preview may return a valid inconsistency result; save must create nothing for inconsistency.
4. Require one pure evaluator to drive API, CLI, UI, current status and preflight blocker additions. Existing provider/PIT/tradability blockers remain and public input cannot remove them.
5. Enumerate every impact field and require `value=null`, `status=NOT VERIFIED` and a specific stable reason until its separately reviewed model/data dependency exists.

### B6 — The save transaction does not freeze an atomic two-head compare-and-swap

The request carries expected mandate and budget IDs, but the draft only says to recalculate in the transaction. Current `_cas_head()` conditions on one head field. A mandate successor can move the mandate head between the risk service's read and its budget-only CAS, allowing a newly inserted risk version to become current while already bound to a noncurrent mandate. An acceptance test alone is insufficient; the required transaction predicate is material state-machine semantics.

Required correction:

The risk save must use one database transaction and a single conditional head update whose `WHERE` clause matches profile ID, expected current risk-budget ID and expected current mandate ID. All new budget/document/projection rows are flushed before that update, with no intermediate commit. Rowcount other than one is a conflict and the whole transaction is rolled back. Specify rollback for parser, projection, trigger and response-serialization failures. Keep preview read-only and based on one consistent snapshot.

Acceptance addition: deterministic interleaving/failure injection must prove zero orphan successor rows and no head movement for a mandate race, risk race, projection failure, document failure or post-flush exception.

### B7 — Legacy and full-document successor behavior is ambiguous

The existing metadata-only POST must remain compatible, while a legacy version has no editor document and the editor requires a complete document. The draft does not say whether metadata-only succession from a legacy head creates another documentless legacy version, synthesizes missing metadata, or is rejected. It also does not say whether metadata-only succession from a V1 head clones the V1 document, or how the endpoint distinguishes an intentionally metadata-only request from an accidentally omitted declaration.

Required correction:

Freeze a transition table for `(legacy head | V1 head) x (metadata-only | full declaration)`. A legacy metadata-only path may clone actual compatibility rows and remain explicitly `LEGACY_NOT_VERIFIED`, but must not synthesize a V1 document. A V1 metadata-only path must clone the complete normalized document and its exact projection if it is retained. A full declaration is the only path that materializes V1 metadata from legacy values/reasons. Use an explicit request discriminator/schema version so omission cannot silently select the compatibility path. Specify history/current response status for every case.

Acceptance addition: exercise all four transitions, including mandate mismatch, and prove no Balanced reset or fabricated evidence occurs.

### B8 — Database corruption/tamper detection is not fully frozen

An immutable SQLite JSON row can still be inserted malformed or with a forged server-owned field by direct SQL before its immutability trigger protects it. “Validate equality on read/verification” does not state whether all versions are validated, which verifier owns it, or whether application startup fails. The proposed Phase 2 revision compatibility change also needs to preserve exact earlier schema/declaration checks without allowing an unknown future revision.

Required correction:

Define database checks for one-to-one risk-budget ownership, exact schema version, valid JSON where supported, nonblank/hash fields where introduced, and immutable insert/update/delete behavior. Freeze a read-only editor verifier that validates every V1 document, its server-owned envelope, risk version/profile/predecessor chain and exact projection; malformed or divergent V1 records make editor startup/current/history/preflight fail closed. Legacy rows remain identifiable rather than reconstructed. Define separately that Phase 2 verification accepts exactly revisions `0002_phase2` and `0003_research_risk_editor` while still running every prior Phase 2 declaration/raw-integrity check; the editor requires exact `0003_research_risk_editor`. Unknown revisions fail.

Acceptance addition: raw-SQL malformed JSON, wrong schema version, wrong budget linkage, preset/status spoof, projection drift, missing document for a purported V1 version and unknown Alembic revision must be rejected or detected without mutation.

## Nonblocking conclusions and required scope labels

- Persisting a provisional research **declaration** with `feasibility_status=NOT VERIFIED` is reconcilable with Policy section 8 because the Policy explicitly provides `SAVE AS PROVISIONAL` and editable Research/Simulation profiles. This remains acceptable only if the artifact cannot enter an eligible decision/action/weight path and no surface calls it feasible, validated, approved or optimal.
- The exact current 19 compatibility metric IDs/classes are a viable legacy boundary, but they are not a complete numerical risk model. Engineering acceptance must leave TODO P2 numerical feasibility/impact open and every relevant section 18 item `NOT VERIFIED`.
- Balanced and Growth may be offered as research templates. Growth must not be labelled recommended/suitable when capacity and tolerance are unassessed, must not use age, and cannot weaken permanent-loss, evidence, PIT, OOS or shadow governance. The draft's 12.5% custom cap is a valid deliberately bounded slice; values above it remain out of scope rather than silently accepted.
- Keeping `/risk-budget` independent of provider `INTERNAL_DISPLAY` is compatible with the current app if it queries no provider/capture tables and performs no provider permission check. Existing Phase 2 routes and home-page denial must remain unchanged; direct editor access must still fail closed on database/schema corruption.
- One new migration after `0002_phase2` is compatible with current architecture. Downgrade of populated editor documents is destructive and therefore test-only; after a test downgrade/re-upgrade, surviving budget/projection rows must surface as legacy/unverified, never as reconstructed V1 documents.
- No current ADR freezes this editor. ADR-0004 remains provisional, ADR-0006/0007 remain `DESIGN REQUIRED`, and ADR-0013 freezes only PHASE1-V1. Correcting this draft, reviewing its new hash and then adding a narrowly scoped ADR is the required sequence.

## Required correction order and re-review gate

1. Resolve B1, B2, B4 and B5 together as one normative schema/catalog/evaluator appendix.
2. Resolve B3 and B6 as exact parser and transaction contracts.
3. Resolve B7 and B8 as compatibility/verifier/migration contracts.
4. Update acceptance tests to cover every new requirement, recalculate the design hash, and request a new independent pre-review.

No code, migration, decision freeze, numerical risk value, provider permission or validation status is authorized by this review. The current draft's scope acceptance is not numerical risk validation.

## Reviewed evidence hashes

| Artifact | SHA-256 |
|---|---|
| `OPTIVEST_AI_POLICY_V10.md` | `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` |
| `AGENTS.md` | `BA424C1B11B4C3CB7AACB86CD870E67D35CAD70D1040DEB5CFD96B4E8B9A3689` |
| `.ai/START_HERE.md` | `4F4D14FA342434E8EA91318B7747DA49C34C633C8C264827F9A5A1A6CB2EF704` |
| `.ai/HANDOFF.md` before this review checkpoint | `CAD3637E6E0AC06082A821EF5E559B3082160593B99DF9312C2A8AB7339E20F0` |
| `.ai/TODO.md` | `73F91F45C531BD7C8E8ED358383AC1B589C6B37BD19102CA97EFB28577C47454` |
| `.ai/DECISIONS.md` | `E4A514A8EE3A2C2A7F417B8063910A2C805534B0CD7C0E3CD7574338211539A2` |
| `docs/INITIAL_DESIGN.md` | `43FCCF65CD4320B76D835198E2C18A0DD1FF87F1A0B2E88571B0360A7A65A364` |
| `docs/PHASE1_DESIGN.md` | `C23222188016A4A164C0DBB3434D9B8CA768C91CC3B826523744E47C9FF4CD68` |
| `docs/RESEARCH_RISK_EDITOR_DESIGN.md` | `5E275D4095A20886193771C1E645AE4765FC5BA6A0E5F8D22CAE427082F10883` |
| `optivest/models.py` | `9FA517BAD81A2B8409AA3C1CD567F2A069C40A274307C43D81001857AF05F1CF` |
| `optivest/service.py` | `A63B4131779E912EF029ED8CC9AFB909D7F5E739AF14F2B50B57501A019E584E` |
| `optivest/app.py` | `223FD5D57C8B1C61660AFF76E2250D12B30061EBFA809E15FEFBEFD1C31D448E` |
| `optivest/cli.py` | `0D3B54D45213209590633314C7710F80CA63488D4DAA598C9EC6F10749CE4863` |
| `tests/test_phase1.py` | `4B96A7C8CD4E6AD37691A018A6F5C9B32DB9423A3386BA7FA28A9F7C0F73CD20` |
| `tests/test_phase2.py` | `991043DE8631818D7A84267AA02977553F016C30B93E65AA8768F43AEA2F5557` |
| `alembic/versions/0001_phase1.py` | `7441EE6FF6B38353C3F943CF68C03C49AE8E6010A52053655810EC5C6A042AD8` |
| `alembic/versions/0002_phase2.py` | `AA6A1FB6A833C39E43BE0208883F263E06E05B606AECB9F2679BE78ACE875772` |

Repository identity at review: branch `main`; HEAD `UNBORN`; all project files untracked; no network used; no tests run because this was a document/code contract pre-review, not implementation validation.

---

## Revision 2 independent disposition

Date: 2026-09-09, Asia/Tokyo. Corrected review target: `docs/RESEARCH_RISK_EDITOR_DESIGN.md` SHA-256 `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950`. The original findings above remain the historical first-pass record; this section is the controlling disposition for revision 2.

### Verdict

**`PASS FOR SCOPED DECISION FREEZE`** for the exact corrected design hash above.

No B1–B8 blocker remains, and no new material blocker was found. The design is sufficiently closed, fail-closed, immutable, backward-compatible and implementable within the current FastAPI/SQLAlchemy/Alembic/SQLite architecture. Astra may record a narrowly scoped freeze for this exact artifact. Any material change to its schema, catalog, validation/status semantics, transaction predicate, compatibility behavior or scope requires a new hash and renewed review.

This verdict accepts only the research declaration editor design and its stated engineering acceptance tests. It does not validate numerical risk, portfolio feasibility, calibration, `U_risk`, `S_stress`, model impact, mandate suitability, provider/PIT evidence, OOS, shadow, Production readiness or any risk value. Those remain respectively `NOT VERIFIED`, `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` as applicable.

### B1–B8 closure

- **B1 CLOSED.** Sections 2–5 define a closed primitive grammar, exact decimal representation, canonical serialization, full request/stored/response shapes, all 19 catalog rows, server-derived name, and exact compatibility projection. Row 16 is explicitly compatibility-only and its two component declarations cannot be combined.
- **B2 CLOSED.** Section 4 uses structured horizon kind/unit/count/event-clock identities, deliberately distinguishes 7 years from 84 months, rejects cross-clock joint claims, and separates current mandate binding from declaration-level horizon alignment without retroactive relabelling.
- **B3 CLOSED.** Section 2 places one bounded strict decoder before FastAPI model binding and CLI typing, detects duplicate keys at every depth, rejects unsafe encodings/nonfinite values/depth/size violations and emits safe closed error codes.
- **B4 CLOSED.** Section 6 provides the closed class/mode/field implication matrix. Structural Hard and Stress cannot carry `U_risk` semantics; modeled/hybrid, stress and observed hybrid declarations remain distinct and unverified; equivalent buffer is expressly substitutive rather than additive.
- **B5 CLOSED.** Section 8 freezes evaluator inputs/outputs, status vocabularies, finding ordering, contradictions, blockers, unavailable impact fields, comparison rules and HTTP outcomes. One pure evaluator drives every risk surface and cannot remove existing provider/PIT/tradability blockers.
- **B6 CLOSED.** Section 7 requires `BEGIN IMMEDIATE`, a single transaction, one conditional update matching both expected risk and mandate heads, rowcount one, pre-commit response serialization and rollback on every stated failure. This closes the current one-field `_cas_head` race for the new path.
- **B7 CLOSED.** Sections 3 and 7 define an explicit modern discriminator and all four Legacy/V1 × Clone/Full transitions. Legacy rows are cloned exactly without fabricated metadata; only a full declaration can create V1 metadata from a legacy head.
- **B8 CLOSED.** Sections 7 and 9 add checked marker/document ownership, canonical hash, immutability, all-history closed-envelope/projection/chain verification, explicit legacy detection, risk-operation rechecks, and exact `0002_phase2`/`0003_research_risk_editor` compatibility without weakening existing Phase 2 checks.

### Nonblocking implementation and validation conditions

- SQLite-specific `BEGIN IMMEDIATE`, `json_valid`, trigger-definition checks and rollback behavior must be demonstrated in isolated acceptance databases; this review does not infer runtime correctness from prose.
- The allowed catalog units and free-text research definitions remain declarations only. No consumer may interpret them as a calibrated risk metric until a separately designed model contract passes review.
- Engineering PASS requires every acceptance item in corrected design section 11, including exact legacy transitions, raw duplicate-key tests, two-session races/failure injection, populated migration round trip, raw-SQL corruption probes, API/CLI/browser evidence and full regressions.
- A populated downgrade remains destructive and test-only. It is not authorized on a user database.
- `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`, if later earned, must remain an engineering-scope status and leave TODO numerical feasibility/impact open and every applicable Policy section 18 item unpassed.

### Revision 2 reviewed hashes

| Artifact | SHA-256 |
|---|---|
| `OPTIVEST_AI_POLICY_V10.md` | `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` |
| `docs/RESEARCH_RISK_EDITOR_DESIGN.md` revision 2 | `F9EC05E7F96A3294FD819CFB53C99B9FC818B5CE9C86C96C69E701910E44B950` |
| `docs/reviews/research_risk_editor_pre_review.md` before this disposition | `5E2E16727D724D5ECBA98FFE64F127EA48228CCD02360A97A9F834B6CC1E09A9` |
| `AGENTS.md` | `BA424C1B11B4C3CB7AACB86CD870E67D35CAD70D1040DEB5CFD96B4E8B9A3689` |
| `.ai/START_HERE.md` | `F11C21F67BFEC57AA8990DD6A2FAE878F08969B328126A763F901CFF794E706F` |
| `.ai/HANDOFF.md` before revision 2 disposition | `5BE285E3F7C69E4732F3953709B99518B43EAC293B71CCFC892B5EC9C2AA43EF` |
| `.ai/TODO.md` | `73F91F45C531BD7C8E8ED358383AC1B589C6B37BD19102CA97EFB28577C47454` |
| `.ai/DECISIONS.md` | `E4A514A8EE3A2C2A7F417B8063910A2C805534B0CD7C0E3CD7574338211539A2` |
| `optivest/models.py` | `9FA517BAD81A2B8409AA3C1CD567F2A069C40A274307C43D81001857AF05F1CF` |
| `optivest/service.py` | `A63B4131779E912EF029ED8CC9AFB909D7F5E739AF14F2B50B57501A019E584E` |
| `optivest/app.py` | `223FD5D57C8B1C61660AFF76E2250D12B30061EBFA809E15FEFBEFD1C31D448E` |
| `optivest/cli.py` | `0D3B54D45213209590633314C7710F80CA63488D4DAA598C9EC6F10749CE4863` |
| `tests/test_phase1.py` | `4B96A7C8CD4E6AD37691A018A6F5C9B32DB9423A3386BA7FA28A9F7C0F73CD20` |
| `tests/test_phase2.py` | `991043DE8631818D7A84267AA02977553F016C30B93E65AA8768F43AEA2F5557` |
| `alembic/versions/0001_phase1.py` | `7441EE6FF6B38353C3F943CF68C03C49AE8E6010A52053655810EC5C6A042AD8` |
| `alembic/versions/0002_phase2.py` | `AA6A1FB6A833C39E43BE0208883F263E06E05B606AECB9F2679BE78ACE875772` |

Revision 2 review method: selected Policy hash reverified; corrected design read completely; B1–B8 compared to the original findings and current risk/schema/API/CLI/Phase 2 revision/display contracts. Branch `main`, HEAD `UNBORN`. No code, migration, decision, status, risk value or permission was changed; no network or implementation test was run.
