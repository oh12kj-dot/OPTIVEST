# TODO

## P0 — Capital / Data / Critical
- [x] Sol independently pre-reviewed PHASE0-GIT-IDENTITY-V2 draft 1 SHA-256 `DF3BEA3718DBD8259D077D53EEDFC9E6C29EC9A5340AB7DD940A63685F29D790`. Verdict `DESIGN CHANGE REQUIRED`; controlling review SHA-256 `A61D8804DCB95CD6721AED5EE65B886D1F23C2272FE2DA923509B4D300FA99CE`.
- [x] Astra corrected B1-B4 in `PHASE0_GIT_IDENTITY_AMENDMENT_REV2.md` with a normalized committed-tree `STATE_SHA256`, Git index semantics for clean CRLF checkouts, binary tree/index contracts and complete drift/read-only tests. Correction is not acceptance.
- [x] Sol independently re-reviewed revision 2 SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C`. B1-B2 close, but B3-B4 remain blocking; verdict `DESIGN CHANGE REQUIRED`, complete review SHA-256 `EAC0AD2B8F383DBF0DB2DAADE899E5313114E4CAF42E6ACB9C16C9DC6D62F1B7`.
- [x] Astra issued revision 3 SHA-256 `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D` as an exact overlay on revision 2, adding index-tag, path/collision and first-fault/report rules. Correction is not acceptance.
- [x] Sol independently re-reviewed the revision-2/revision-3 pair. Assume-unchanged/skip-worktree close, but F1-F3 leave B3-B4 blocking; verdict `DESIGN CHANGE REQUIRED`, complete review SHA-256 `E014F3A45A14A75E90298FA93D53C13D2DB9235BF10C03C5842E45038182A0D9`.
- [x] Astra issued revision 4 SHA-256 `BDC2119A14D67D379A0E70EDB6B7E849C8C66ADF2432B62242C2037A61E94DC0`, adding exact `-f` fsmonitor detection, host-independent ASCII paths and the fixed fault/report table. Correction is not acceptance.
- [x] Sol independently re-reviewed the exact revision-2/revision-3/revision-4 triplet. B1-B4/F1-F3 close; verdict `PASS FOR SCOPED DECISION FREEZE`, complete review SHA-256 `EF09C8EF0B7B0685678012D05115882B7A8675E444F85AD625A8B7FEFD0F7B5C`.
- [x] Astra froze the exact triplet/review as ADR-0019 / D0011 and authorized only the Phase-0 verifier, isolated tests, design reference and operational records.
- [x] Terra implemented the frozen PHASE0-GIT-IDENTITY-V2 verifier and isolated disposable-repository matrix; engineering evidence is recorded in TEST_STATUS/HANDOFF.
- [x] Sol independently post-validated the implementation against ADR-0019. Verdict `REVIEW_REQUIRED`; controlling review SHA-256 `6EFE50E741928633061D2D963235C111FC8FE94185907675F151849E4550B9B3`. B3/B4/F3 remain blocking.
- [x] Terra applied one bounded Phase-0 review-fix round for command/token precedence and state-path stderr handling; verifier/test hashes and evidence are recorded in HANDOFF/TEST_STATUS.
- [x] Sol independently rechecked that correction. Verdict remains `REVIEW_REQUIRED`; controlling review SHA-256 `FE613453AE10D5EFC2081A29C6CA98569DAEF78F8BD4F8991E956D3A05A44ABC`. Committed-HEAD stderr, missing START classification and complete permanent matrix remain blocking.
- [x] Terra completed the residual bounded verifier/test correction: committed state reads now precede all semantic rows, committed HEAD and UNBORN stderr paths fail closed, missing/executable START entries classify exactly, and the complete 12-row/66-pair snapshot matrix is permanent. Preserve B1/B2/F1/F2.
- [x] Sol independently rechecked the residual correction. Prior blockers close, but verdict remains `REVIEW_REQUIRED`: genuine `GIT_CASE_COLLISION` + `GIT_START_ENTRY` returns the later row and the nominal 66-pair fixture does not instantiate both faults.
- [x] Terra corrected collision-before-START ordering and made all 66 pair injections compositional and auditable; genuine Case/case plus executable START now returns only `GIT_CASE_COLLISION`. Focused/full/static evidence passed.
- [x] Sol independently rechecked the collision/START correction. That pair closes, but verdict remains `REVIEW_REQUIRED`: malformed committed-token plus malformed tree returns later `GIT_TREE`, and the pair helper covers only the worktree-candidate token path.
- [x] Terra restored committed malformed-token-before-tree precedence, preserved collision-before-START, and added actual/blob-trigger token fixtures with exact reports and snapshots. Focused/full/static evidence passed.
- [x] Sol independently rechecked the exact final committed-token correction and issued `PASS_ENGINEERING_PHASE0_GIT_IDENTITY`.
- [ ] Perform the separately authorized initial commit/push workflow, or explicitly defer it and resume the next authorized task. This review performed neither.
- [x] Resolve conflicting Policy files by explicit user selection; preserve selected bytes.
- [x] Verify completed bootstrap against actual file/hash/Git evidence.
- [x] Establish a reversible Generic Research Mandate; keep personal/Production fields unapproved.
- [ ] Keep Production NOT PRODUCTION READY until every material §18 gate has evidence and approval.

## P1 — Core / Model correctness
- [x] Sol blind first pass and Phase 0 comparative pre-review.
- [x] Astra scoped Decision Freeze for offline checker only (ADR-0010 PHASE0-V1).
- [x] Terra implements frozen Phase 0 checker; isolated tests; Sol post-validation.
- [x] Complete Phase 1 independent review and Decision Freeze: PIT/security master and provisional risk UI, DB/API/CLI contracts.
- [x] Implement, test and independently validate PHASE1-V1.
- [x] Design and independently pre-review forward provider/license/timestamp/coverage capture and historical-universe limitation; freeze PHASE2-V1 (ADR-0015).
- [x] Independently validate remediated PHASE2-V1 offline/fixture/SQLite engineering (`PASS_ENGINEERING_P2_OFFLINE`, ADR-0016).
- [x] Review current SEC/Nasdaq terms by use; SEC research mapping is supportable, but no permission freeze was made because immutable source-byte/hash provenance is incomplete.
- [ ] Obtain unambiguous permission for `otherlisted.txt` and the atomic Nasdaq pair, or design/review a replacement forward-universe source; only then consider bounded official capture/replay.
- [ ] Select admissible historical US universe/delisting/price source; paid access remains user-confirmation-required.
- [ ] Forecast/wealth/risk/optimizer/uncertainty ledger design, calibration plan, review before implementation.
- [x] Draft the bounded `RESEARCH-WEALTH-LAB-V1` synthetic accounting foundation (2026-09-14); no freeze or implementation/model acceptance.
- [x] Sol falsification-first pre-review of `docs/RESEARCH_WEALTH_LAB_DESIGN.md` draft 1. Verdict `DESIGN CHANGE REQUIRED`; report `docs/reviews/research_wealth_lab_pre_review.md`.
- [x] Astra correct RESEARCH-WEALTH-LAB-V1 B1-B6 in revision 2: raw bytes/bounds, recovery state machine, rational/display/comparison, closed failures/capabilities, complete source/artifact provenance and exact BASE/MAX/W fixtures. Correction is not independent acceptance.
- [x] Sol independently re-reviewed revision-2 SHA-256 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`; B1-B6 and W1-W19 are closed for design freeze. Verdict `PASS FOR SCOPED DECISION FREEZE`; review SHA-256 `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83`.
- [x] Astra added ADR-0018 / D0010 freezing the exact wealth-lab design/review pair under all six review conditions; no implementation or engineering/model acceptance implied.
- [x] Terra bounded correction for frozen RESEARCH-WEALTH-LAB-V1 B1-B8: permanent counterexamples cover PRE/POST cost clock, canonical Bundle/hash identity, dual-precision arithmetic/private invariants, raw surrogate/depth precedence, simultaneous terminal-zero findings, pre-emission provenance/Git/example authority, HTTP/CLI failure contracts and structured stale-safe UI. This is not independent acceptance.
- [x] Sol independently post-validated the first completed wealth-lab implementation attempt on 2026-09-16. Verdict `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`; no scoped engineering acceptance. All investment/model/Production gates remain open.
- [x] Independently recheck Terra's bounded B1-B8 correction. Verdict remains `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`: B1-B5/B7/static-B8 close, but copied-source probes show example/capabilities omit the frozen second pre-emission source check. See the 2026-09-17 section of the controlling post-review.
- [x] Terra corrected the residual B6/W17 example/capabilities pre-emission source race and added permanent library/GET copied-source counterexamples.
- [x] Sol independently rechecked the final B6/W17 correction using a separate disposable-copy mutation probe plus the applicable focused/MAX/full/static/no-write/migration matrix. Verdict `PASS_ENGINEERING_RESEARCH_WEALTH_LAB_NON_BROWSER`; full all-surface acceptance still awaits W18.
- [x] Obtain and independently validate genuine in-app Browser desktop/390px BASE/W2/W6c/stale/in-flight/error/XSS/ruin/rehash/download-rejection/structured rendering. W18 passed on 2026-09-20; full frozen all-surface verdict is `PASS_ENGINEERING_RESEARCH_WEALTH_LAB`.
- [x] Astra draft the next narrow `RESEARCH-RETURN-BRIDGE-LAB-V1` supplied-synthetic Economic Return Bridge / hierarchical-prior / uncertainty-ledger contract. Draft 1 is not frozen and authorizes no implementation.
- [x] Sol falsification-first pre-review of return-bridge draft 1 SHA-256 `6946F1608D638244A3677A0338B37DAC84C7290B10ED134DA6293AE10229B26B`. Verdict `DESIGN CHANGE REQUIRED`; controlling review SHA-256 `418E4D87745F8C974881F918CCA00C5426D6A9EE9EFDD0C7C0B59C388B058B5F`; no ADR freeze or implementation authorization.
- [x] Astra corrected return-bridge B1-B8 in revision 2: narrow terminal identity scope, exact accounting/distribution/prior basis, 12-row mechanical coverage registry, semantic-set canonicalization, tagged numerics, closed output/error/manifest contract and BASE/MAX/R1-R16 oracles. Correction is not acceptance.
- [x] Sol independently re-reviewed revision 2 SHA-256 `1D505E1FC643A6EE8509EC2381BDB73B23A4D56ADF2BBF907399151AD7BD491C`. B1-B6 close, but B7-B8 remain blocking; verdict `DESIGN CHANGE REQUIRED`, complete review SHA-256 `E037909BE7942E11048CE0A37ED5D04DC9B830E9EEA747297FF1DCC3B502B7CB`.
- [ ] Astra produce revision 3 closing only B7-B8: exact nested payload/status/provenance schemas and mapping, literal BASE/MAX/Unicode/tie/fault oracles, canonical input length/hash and reproducible resource protocol. Preserve B1-B6.
- [ ] Sol independently re-review revision 3 at its new exact hash; only `PASS FOR SCOPED DECISION FREEZE` may precede a new ADR/freeze and Terra dispatch.
- [ ] Locked OOS and shadow plan with preregistered acceptance; no invented realized evidence.

## P2 — Important
- [x] Terra correction for the remaining ADR-0017 S1/S2/S3 grammar/difference/all-history-verifier/UI wiring findings; retained reviewer tests remain byte-identical and new permanent regressions cover the frozen counterexamples. Sol recheck, including real browser interaction, is still required.
- [x] Run third independent post-validation including real in-app browser desktop/mobile edit/clear/preview/save/reload/history/stale/XSS and blocked-provider interaction. Verdict: `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`; see post-review section 11.
- [x] Independently validate the bounded Terra T1–T4/structured-UI correction. T3 migration/corruption and T4 preview/response probes close, but the 2026-09-13 verdict remains `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`; see post-review section 12.
- [x] Terra bounded U1–U3 fix: applicable Risk/Stress/Hybrid M wrappers reject reserved `NOT_APPLICABLE`; responsive 390px layout wraps/shrinks and current name/source preset display; 19 visible server-rendered pre-hydration controls satisfy the retained initial-HTML contract without hidden anchors. Terra focused evidence only; Sol must rerun section 11. Feasibility/impact/calibration remain `NOT VERIFIED` regardless of engineering outcome.
- [x] Sol independent final U1–U3 recheck: retained test identity, exhaustive applicable-wrapper rejection, focused/full regression, real desktop/390px browser behavior, current name/source-preset display and provider-blocked isolation passed. Scoped verdict: `PASS_ENGINEERING_RESEARCH_RISK_EDITOR`; numerical/model/readiness work remains open.
- [ ] Provider licensing/timestamp/coverage and delisting evidence investigation after universe selection.

## P3 — Nice-to-have
- [ ] Visual polish and performance tuning after verified behavior.
