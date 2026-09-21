# Test and validation status

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 final alternate-token Sol recheck — PASS_ENGINEERING_PHASE0_GIT_IDENTITY

- Controlling complete post-review SHA-256: `71CD35864C4B0FE33271458250FC920FCD3918453E85A78133F22A7A8C60C2BE`.
- Identities: verifier `D411F2043716C08302170C962A480CD6BE3C86D1632FCEA96308C6AF9DEECF45`; tests `641759C3FBA8E7936E69D119F33B8CDC9E03AB6652EADB6BCDF6486504D43953`; authority hashes unchanged.
- Independent alternate-token matrix: 18/18 exact `GIT_TOKEN` reports across six malformed committed blob forms and malformed tree/collision/executable START; null/value semantics, no-leak and snapshots passed.
- Genuine collision/START variants and candidate/blob trigger accounting passed; previous command/stderr/missing-entry and B1/B2/F1/F2 behavior remained closed.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **29 passed, 1 skipped** in **138.597s**.
- Terra full regression -> **228 passed, 2 skipped, 2 warnings, 174 subtests**. Not independently rerun because focused and separate probes directly covered the final delta.
- Compileall, structural startup, `git diff --check`, and verifier/test trailing-whitespace scan passed. Startup remained `main/UNBORN`, structural-only PASS, 78 untracked, `NOT PRODUCTION READY`.

Verdict: **`PASS_ENGINEERING_PHASE0_GIT_IDENTITY`**. Initial commit/push is technically unblocked but not performed. No broader validation/readiness status changed.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 final committed-token correction — Terra evidence; Sol recheck pending

Authority remained unchanged: selected Policy, ADR-0019/D0011, frozen rev2/rev3/rev4 and controlling prior final review `5F01878CCF140811EA7723EFB1E175D0A24558391314250E88BC9A1346F2B440`.

- Verifier `D411F2043716C08302170C962A480CD6BE3C86D1632FCEA96308C6AF9DEECF45`; tests `641759C3FBA8E7936E69D119F33B8CDC9E03AB6652EADB6BCDF6486504D43953`.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **29 passed, 1 skipped** in **137.277s**. It includes the actual committed malformed-token blob plus independently malformed tree, all six committed-blob malformed token variants against tree/collision/START, candidate-versus-blob trigger assertions, the 12 exact rows, all 66 pairs, hidden flags and read-only snapshots.
- Full `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **228 passed, 2 skipped, 2 known dependency warnings, 174 subtests passed** in **244.28s**.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests`, structural startup, `git diff --check` and a trailing-whitespace scan of all changed verifier/test/operational files -> exit **0**. Startup reports structural PASS, empty findings, `main/UNBORN`, 78 untracked paths and `NOT PRODUCTION READY`.

This is Terra implementation evidence only. Final independent Sol post-validation remains mandatory; no initial commit, push, model/provider/risk/OOS/shadow/readiness status changed.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 final residual Sol recheck — REVIEW_REQUIRED

- Controlling complete post-review SHA-256: `5F01878CCF140811EA7723EFB1E175D0A24558391314250E88BC9A1346F2B440`.
- Identities: verifier `0ED13A57DA47F4D20FB0656C291CB531B210CFD2721CE3A4DB294D4D019E3536`; tests `4FB0EFA8579D85FF2B3A17D33A43A23EBE83DC31129E9D30C68DFB7F9D1CBA26`; authority hashes unchanged.
- Requested genuine pairs passed independently: Case/case collision combined with missing, `100755 blob`, `120000 blob`, and proper `160000 commit` START returned sole exact `GIT_CASE_COLLISION`; complete snapshots unchanged.
- Blocking genuine pair: malformed committed START blob without a token plus malformed tree returned `GIT_TREE`; frozen order requires `GIT_TOKEN`. The permanent pair helper applies its named proxy faults but represents token failure only through `recorded_head_candidate`, so it does not cover this blob-token path.
- Previously closed command/stderr/missing-entry and B1/B2/F1/F2 probes remained positive.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **27 passed, 1 skipped** in **124.311s**.
- Terra full result remains **226 passed, 2 skipped, 2 warnings, 156 subtests**. Sol did not rerun it because the frozen-order counterexample already requires correction.
- Compileall, structural startup, `git diff --check` and explicit verifier/test trailing-whitespace scan passed. Startup: structural PASS, `main/UNBORN`, 78 untracked, `NOT PRODUCTION READY`.

Verdict: **`REVIEW_REQUIRED`**. No scoped engineering PASS, initial commit or push.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 final collision/START correction — Terra evidence; Sol recheck pending

Authority remained unchanged: selected Policy, ADR-0019/D0011, frozen rev2/rev3/rev4 and controlling prior final review `DA717DC223D70CDD9DF05CBCDBCE5AABDD29F7C0CC17A029C02B8D50BF2ABCFC`.

- Verifier `0ED13A57DA47F4D20FB0656C291CB531B210CFD2721CE3A4DB294D4D019E3536`; tests `4FB0EFA8579D85FF2B3A17D33A43A23EBE83DC31129E9D30C68DFB7F9D1CBA26`.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **27 passed, 1 skipped** in **124.291s**. The additional direct disposable fixture proves a simultaneous `Case.txt`/`case.txt` collision plus executable committed START returns only exact `GIT_CASE_COLLISION`; every 12-row/66-pair run asserts every named injection was applied and snapshots the worktree plus `.git` files.
- Full `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **226 passed, 2 skipped, 2 known dependency warnings, 156 subtests passed** in **231.01s**.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests`, structural startup, `git diff --check` and a trailing-whitespace scan of all changed verifier/test/operational files -> exit **0**. Startup reports structural PASS, empty findings, `main/UNBORN`, 78 untracked paths and `NOT PRODUCTION READY`.

This is Terra implementation evidence only. Final independent Sol post-validation remains mandatory; no initial commit, push, model/provider/risk/OOS/shadow/readiness status changed.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 final independent Sol recheck — REVIEW_REQUIRED

Authority and implementation identities matched: Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; frozen rev2/rev3/rev4 and ADR-0019/D0011; verifier `AB3CC7A7EEB278AD7B02A58733BFD7E2DC83897329345B754B65FB1C5B57995C`; tests `87209E30F55EABDAC372ACA2F67E61FC84069FD355F1DCE63D5A528111B16DF7`.
Controlling complete post-review SHA-256: `DA717DC223D70CDD9DF05CBCDBCE5AABDD29F7C0CC17A029C02B8D50BF2ABCFC`.

- Prior blocker probes passed independently: committed `HEAD` exit-zero/nonzero stderr; failed blob read plus invalid token; later whole-status failure paired with root/object-format/branch; actual missing/executable START entry; exact no-leak and unchanged snapshots.
- Independent exact matrix: all 12 single reports matched; 65/66 genuinely combined pairs matched. `GIT_CASE_COLLISION` + `GIT_START_ENTRY` returned the later START finding because implementation checks START validity first.
- Permanent test audit: all 12 complete JSON/null/denial reports, 66 named combinations, applicable committed/UNBORN stderr reads, binary/truncated inputs, hidden flags, no-leak checks and all-file snapshots exist. The collision/START helper path injects only collision, so that named pair is a false positive.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **26 passed, 1 skipped** in **122.406s**. The skip is unavailable Windows symlink creation.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests`, `uv --cache-dir .uv-cache run python scripts/verify_startup.py --root .`, and `git diff --check` -> exit **0**. Startup reports structural PASS, `main/UNBORN`, 78 untracked paths and `NOT PRODUCTION READY`.
- Full suite was not rerun in this recheck because the direct frozen-contract counterexample already requires correction. Prior Terra evidence remains **225 passed, 2 skipped, 156 subtests** and does not override it.

Verdict: **`REVIEW_REQUIRED`**. B1/B2/F1/F2 and prior R1/R2/global-command behavior close; B3/B4/F3 remain open only for the reproduced collision-before-START pair and its permanent fixture. No initial commit/push or readiness promotion.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 residual correction — Terra evidence; Sol recheck pending

Authority remained unchanged: selected Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; ADR-0019/D0011; frozen rev2/rev3/rev4; controlling prior recheck `FE613453AE10D5EFC2081A29C6CA98569DAEF78F8BD4F8991E956D3A05A44ABC`.

- Verifier `AB3CC7A7EEB278AD7B02A58733BFD7E2DC83897329345B754B65FB1C5B57995C`; tests `87209E30F55EABDAC372ACA2F67E61FC84069FD355F1DCE63D5A528111B16DF7`.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **26 passed, 1 skipped** in **142.207s**. The one skip is unavailable Windows symlink creation. It includes all 12 exact complete fault reports, every 66 earlier/later pair, committed and UNBORN exit-zero/nonzero stderr, malformed/truncated streams, actual missing/executable entries, no-leak checks, all-file snapshots and all eight hidden flags.
- Full `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **225 passed, 2 skipped, 2 known dependency warnings, 156 subtests passed** in **258.53s**.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests`, `uv --cache-dir .uv-cache run python scripts/verify_startup.py --root .`, `git diff --check`, and a trailing-whitespace scan of the changed verifier/tests -> exit **0**. Startup reports structural PASS, empty findings, `main/UNBORN`, 77 untracked paths and `NOT PRODUCTION READY`.

This is implementation evidence only. Independent Sol post-validation, not a green suite, decides whether B3/B4/F3 are closed. No initial commit, push, approval, model, provider, risk, OOS, shadow or Production status changed.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 independent Sol recheck — REVIEW_REQUIRED

Controlling post-review complete SHA-256 `FE613453AE10D5EFC2081A29C6CA98569DAEF78F8BD4F8991E956D3A05A44ABC`; verifier `A57762B8B9E76F17F013711612A151F37B6AF3F50AE8FA65EF5C31565C6FAB2B`; tests `773C7F18278F64C2F44F2E1D135C52657B18C3CA8B03CAA79447FCB1B17E170E`. Policy/rev2/rev3/rev4/pre-review/ADR hashes remained unchanged.

Verdict: **`REVIEW_REQUIRED`**. Prior command/token counterexample is fixed. B1/B2/F1/F2 remain closed. B3/B4/F3 remain blocking because committed `HEAD` command stderr is ignored when `HEAD^{commit}` succeeds, missing committed START_HERE is misclassified as `GIT_COMMAND` rather than `GIT_START_ENTRY`, and the frozen complete report/pair/read-only matrix is not permanent.

- Independent stderr matrix: exit-zero/nonzero stderr at root/object/branch/commit/tree/blob/stage/tags/scoped/whole status and UNBORN HEAD/commit/ref returned non-leaking `GIT_COMMAND`; the two committed-HEAD cases returned no finding. All snapshots were unchanged.
- Independent 12-row synthetic matrix: all 12 fixed code/path/reason rows and snapshots passed. Actual missing-entry and later-command precedence counterexamples above remain blocking.
- Positive independent matrix: separate normalized digest matched; content-identical/autocrlf passed; later drift failed; all eight hidden-index combinations emitted the expected literal tag triples and only `H/H/H` passed; all snapshots were unchanged.
- Focused: `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **21 passed, 1 skipped** in 73.820s.
- Root-supervised full: `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **220 passed, 2 skipped, 2 known dependency warnings, 33 subtests passed** in 195.05s.

No engineering PASS, initial commit or push. Production/model/provider/PIT/risk/OOS/shadow status remains unchanged.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 Terra B3/B4/F3 review-fix — Sol recheck pending

Controlling post-review SHA-256 `6EFE50E741928633061D2D963235C111FC8FE94185907675F151849E4550B9B3`. The correction retains stdout and stderr from every Git read, treats stderr or nonzero exit as the exact non-leaking `GIT_COMMAND`, and resolves every committed-state read before lower-priority token/tree/index/status semantics. Quiet HEAD reads preserve valid UNBORN without stderr.

Permanent disposable-repository fixtures now cover the post-review invalid-token plus failed-`cat-file` counterexample, zero-exit stderr for tree/blob/stage/three tags/scoped and whole status reads, a nonzero later-status plus malformed-tree pair, output non-leakage and byte snapshots. The focused correction test and `python -m py_compile scripts\\verify_startup.py tests\\test_verify_startup.py` passed. Full unit/pytest/startup/whitespace evidence is pending before Sol recheck; this is not engineering acceptance.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 independent Sol post-validation — REVIEW_REQUIRED

Controlling review `docs/reviews/phase0_git_identity_post_review.md`, SHA-256 `6EFE50E741928633061D2D963235C111FC8FE94185907675F151849E4550B9B3`. Authority hashes matched Policy `ACF013CE...38E67`, revisions 2/3/4 `8225D5...12E6C` / `A6E5A2...625D` / `BDC211...94DC0`, pre-review `EF09C8...7B5C` and ADR-0019/D0011.

Verdict: **`REVIEW_REQUIRED`**. B1/B2/F1/F2 are closed by independent reproduction. B3/B4/F3 remain blocking: failed `cat-file` plus invalid STATE token returns later `GIT_TOKEN` instead of table-first `GIT_COMMAND`; `_run_git` discards stderr contrary to the frozen fail-closed contract; permanent tests omit complete 12-row JSON, all earlier/later pairs and all-failure byte snapshots. No `PASS_ENGINEERING_PHASE0_GIT_IDENTITY`, initial commit or push.

- Focused: `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **20 passed, 1 skipped** in 63.473s.
- Full: `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **219 passed, 2 skipped, 2 known dependency warnings, 25 subtests passed** in 179.85s.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests`, structural startup and `git diff --check` -> exit 0.
- Independent disposable evidence: separate normalized tree digest, later/content-identical/autocrlf, all eight literal `-v/-t/-f` flag rows, staged/unstaged/index-only/mode and read-only probes behaved as frozen. The paired command/token probe reproduced the blocker. Temporary probe/repositories were removed.

Production/model/provider/PIT/risk/OOS/shadow status is unchanged: `RISK BUDGET NOT APPROVED`; applicable items `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 Terra implementation evidence — Sol post-validation pending

Authority rechecked before execution: selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; frozen revisions 2/3/4 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C` / `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D` / `BDC2119A14D67D379A0E70EDB6B7E849C8C66ADF2432B62242C2037A61E94DC0`; controlling review `EF09C8EF0B7B0685678012D05115882B7A8675E444F85AD625A8B7FEFD0F7B5C`.

- `python -m unittest -v` over the 15 non-state tests: **14 passed, 1 skipped** (external symlink creation unavailable on this Windows host).
- `python -m unittest -v` over first/later/content-identical, autocrlf clone and staged/index/untracked state tests: **3 passed**.
- `python -m unittest tests.test_verify_startup.VerifyStartupTests.test_state_digest_detects_add_delete_rename_mode_and_start_edits tests.test_verify_startup.VerifyStartupTests.test_state_hidden_index_flag_matrix_is_closed_and_readonly -v`: **2 passed**. The latter covers all eight assume-unchanged/skip-worktree/fsmonitor combinations and, for every hidden state, mutates a non-machine START_HERE byte before marking the flags; the verifier returns only `GIT_INDEX_FLAGS` without altering the fixture snapshot.
- `python -m py_compile scripts\\verify_startup.py tests\\test_verify_startup.py`: **PASS**.
- `python scripts\\verify_startup.py --root .`: exit **0**, `startup_integrity=PASS`, findings `[]`, `main / UNBORN`, 76 untracked paths, and `NOT PRODUCTION READY`.
- `git diff --check`: **PASS**. The repository is UNBORN/all files untracked, so this cannot by itself validate whitespace in those files; modified text and frozen hashes were separately inspected.

Result: the implementation evidence covers normalized digest transitions, committed-byte/autocrlf semantics, exact hidden-index tags including `-f`, portable path/collision negatives, index/worktree failure, fixed Git failure/report precedence and read-only snapshots. This is Terra evidence only, not `PASS_ENGINEERING`, investment/model/provider validation, or authorization to commit/push. Independent Sol post-validation remains required.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 revision-4 exact-triplet independent re-review

Reviewed exact triplet hashes revision 2 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C`, revision 3 `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D`, revision 4 `BDC2119A14D67D379A0E70EDB6B7E849C8C66ADF2432B62242C2037A61E94DC0`, Policy/ADR baseline and pre-addendum review `E014F3A45A14A75E90298FA93D53C13D2DB9235BF10C03C5842E45038182A0D9`. Complete review SHA-256: `EF09C8EF0B7B0685678012D05115882B7A8675E444F85AD625A8B7FEFD0F7B5C`.

Verdict: **`PASS FOR SCOPED DECISION FREEZE`**. B1-B4/F1-F3 are design-closed. Eight assume/skip/fsmonitor combinations accepted only the no-flag `H/H/H` row and preserved byte snapshots. Revision-4 ASCII grammar accepted all 76 current prospective tracked paths with zero collisions and rejected crafted portable-path counterexamples. Exact failure/reason/report/null/precedence rules are now independently decidable.

This was design-only verification using disposable repositories and local structural checks; all temporary repositories were removed. No design, DECISIONS, verifier/test, application/database/provider/model/trial/Production artifact changed. Repository remains `main / HEAD UNBORN`; no commit or push occurred. Scoped freeze, Terra implementation and Sol post-validation remain separate required gates. All non-production boundaries remain unchanged.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 revision-3 exact-pair independent re-review

Reviewed revision 2 SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C` plus revision 3 SHA-256 `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D` against Policy/ADR baseline and pre-addendum review `EAC0AD2B8F383DBF0DB2DAADE899E5313114E4CAF42E6ACB9C16C9DC6D62F1B7`. Complete review SHA-256: `E014F3A45A14A75E90298FA93D53C13D2DB9235BF10C03C5842E45038182A0D9`.

Verdict: **`DESIGN CHANGE REQUIRED`**. Assume-unchanged/skip-worktree checks close, but fsmonitor-valid does not: Git 2.54.0 returned accepted `H` from the prescribed `ls-files -v` and `-t`, while `ls-files -f` returned the required lowercase `h`. Portable Windows path/Unicode rules and the literal per-stage fault/report oracle also remain incomplete, so B3-B4 stay open.

Disposable tag probes covered normal, assume-unchanged, skip-worktree, fsmonitor-valid and combined states; stage/tag commands preserved byte snapshots. Git accepted representative reserved/trailing/ADS/Unicode/invalid-UTF-8 tree names, confirming the path rule requires an explicit predicate. All disposable repositories were removed. This was design-only: no design, DECISIONS, verifier/test, application/database/provider/model/trial/Production artifact changed. Repository remains `main / HEAD UNBORN`; no commit/push occurred and all non-production boundaries remain unchanged.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 revision-2 independent re-review

Reviewed `docs/PHASE0_GIT_IDENTITY_AMENDMENT_REV2.md` SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C` against Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, ADR-0010/0011 and the draft-1 review pre-addendum hash `A61D8804DCB95CD6721AED5EE65B886D1F23C2272FE2DA923509B4D300FA99CE`. Complete review SHA-256 is `EAC0AD2B8F383DBF0DB2DAADE899E5313114E4CAF42E6ACB9C16C9DC6D62F1B7`.

Verdict: **`DESIGN CHANGE REQUIRED`**. B1-B2 close: the normalized committed-tree digest detected later/add/delete/rename/mode/non-token changes, retained a content-identical commit and passed a clean CRLF worktree backed by an LF blob. B3-B4 remain blocking. Assume-unchanged and skip-worktree each hid altered START_HERE worktree bytes from the specified status/stage-OID checks while the committed state digest still passed. Exact failure codes, precedence, state-field values and case-collision semantics also remain non-unique.

Disposable probes covered first/corrected/wrong-token/content-identical commits, all requested tree changes, START_HERE edits, clean autocrlf, staged/index and hidden-index-flag states, raw NUL records including a tab path, arbitrary blob bytes and byte-for-byte `.git` preservation for the clean read commands. All temporary repositories were removed. The unchanged PHASE0-V1 baseline returned **13 passed, 1 skipped in 9.216s**; this is not revision-2 implementation evidence. This was design-only; no verifier/test/application/database/provider/model/trial/Production artifact changed and no commit/push occurred. Repository remains `main / HEAD UNBORN`; all non-production boundaries remain unchanged.

## 2026-09-21 PHASE0-GIT-IDENTITY-V2 independent design pre-review

Reviewed `docs/PHASE0_GIT_IDENTITY_AMENDMENT.md` SHA-256 `DF3BEA3718DBD8259D077D53EEDFC9E6C29EC9A5340AB7DD940A63685F29D790` against selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, ADR-0010/0011, the frozen Phase-0 design and current verifier/tests. Controlling review SHA-256: `A61D8804DCB95CD6721AED5EE65B886D1F23C2272FE2DA923509B4D300FA99CE`.

Verdict: **`DESIGN CHANGE REQUIRED`**. Bare `SELF` removes the literal hash fixed point but does not pin the expected committed state. An isolated second commit changed HEAD while all six proposed SELF conditions still passed. A clean Windows `core.autocrlf=true` checkout also produced a 24-byte LF HEAD blob and 25-byte CRLF worktree file with empty path status, contradicting the raw-byte rule. Exact Git binary/tree/status/failure semantics and permanent negative/read-only tests remain incomplete.

Existing PHASE0-V1 baseline command `python -m unittest tests.test_verify_startup -v` returned **13 passed, 1 skipped in 9.093s**; this contains no SELF coverage. The two falsification probes used disposable repositories and were removed. No amendment, verifier, test, Policy, DECISIONS, application, database, provider, model, trial or Production-gate artifact changed. Repository remains `main / HEAD UNBORN`; no commit, push or remote operation occurred. All non-production boundaries remain unchanged.

## 2026-09-21 RESEARCH-RETURN-BRIDGE-LAB-V1 revision-2 independent re-review

Reviewed `docs/RESEARCH_RETURN_BRIDGE_DESIGN_REV2.md` SHA-256 `1D505E1FC643A6EE8509EC2381BDB73B23A4D56ADF2BBF907399151AD7BD491C` against Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` and the pre-addendum review `418E4D87745F8C974881F918CCA00C5426D6A9EE9EFDD0C7C0B59C388B058B5F`. Controlling complete review SHA-256 is `E037909BE7942E11048CE0A37ED5D04DC9B830E9EEA747297FF1DCC3B502B7CB`.

Verdict: **`DESIGN CHANGE REQUIRED`**. B1-B6 close at the corrected narrow semantic level. B7-B8 remain blocking because the nested Evaluation/result/capabilities/status/provenance contracts are not unique and the exact BASE/MAX/Unicode/tie/fault/R1-R16 fixtures cannot be derived from the reviewed bytes. Resource byte/algorithmic limits are fixed, but the time/memory measurement protocol is not reproducible.

Independent arithmetic reproduced BASE start FCFE/share `10`, start price `100`, prior `.08`, GROWTH log `ln(2)/7`, annualized `2^(1/7)-1`, and disagreement `ln(2)/7-.08`. Exact 40-digit public GROWTH strings are `9.902102579427790134531887449402522401079e-2`, `1.040895136738123376495053876233447213253e-1`, and `1.902102579427790134531887449402522401079e-2`. Zero tags and a zero-revenue/positive-distribution case reproduced. MAX counts are 32 identity + 4 prior + 32 disagreement + 4 range + 12 registry = 84 rows, with 32 identity evaluations. Evaluation/Artifact limits reproduce as 4,194,304/5,242,880 bytes.

This was design-only review: no application/model/database/provider/trial test ran, and revision 2 was not edited. Exact hashes, `main / HEAD UNBORN`, touched-file whitespace, `git diff --check` and structural startup state are recorded with the review completion. No readiness item is promoted.

## 2026-09-21 RESEARCH-RETURN-BRIDGE-LAB-V1 independent design pre-review

Controlling report: `docs/reviews/research_return_bridge_pre_review.md`, SHA-256 `418E4D87745F8C974881F918CCA00C5426D6A9EE9EFDD0C7C0B59C388B058B5F`. Reviewed draft SHA-256: `6946F1608D638244A3677A0338B37DAC84C7290B10ED134DA6293AE10229B26B`. Selected Policy SHA-256: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.

Verdict: **`DESIGN CHANGE REQUIRED`**. Eight blocking design findings cover FCFE basis/scope, distribution timing and buyback/capital-allocation double counting, prior additivity/shrinkage, semantic uncertainty-ledger overlap, canonical wire-order contradiction, zero/nonfinite/CAGR/tie/range outputs, incomplete status/error/output/provenance/transport contracts, and non-decidable R1-R16/MAX/resource oracles. R1-R14 and R16 require correction; R15 no-state/no-promotion is retainable after correction. No implementation or ADR freeze is authorized.

Independent `Decimal` probes reproduced: terminal aggregation of price 100 plus distribution 10 gives annualized rate `0.013708856295468119...`; a year-1 distribution held at 5% through year 7 gives terminal value `113.400956406250` and rate `0.018128016064272623...`. Prior inputs `.03 + .05 + .08` yield `.16` if the factor term is incremental but `.11` if it already includes the broad-market premium; draft 1 does not distinguish those bases.

Commands/evidence: `Get-FileHash -Algorithm SHA256` matched the three identities above; `git branch --show-current` returned `main`; `git rev-parse HEAD` failed because the repository is `UNBORN`; `git status --short` showed the existing wholly untracked checkout. The complete selected Policy, project instructions, current operational authority, relevant accepted wealth-lab design and the complete draft were read. No application/model tests were run for this review because implementation is prohibited; the 2026-09-21 full-suite evidence below remains prior repository evidence, not evidence that draft 1 is valid.

No database, provider/network, financial/model experiment or research trial occurred. No production register or accepted frozen artifact changed. Statuses remain `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED`, `NOT PRODUCTION READY`.

## 2026-09-21 return-bridge revision-2 design correction

Astra preserved draft 1 and added `docs/RESEARCH_RETURN_BRIDGE_DESIGN_REV2.md` to address B1-B8. SHA-256 `1D505E1FC643A6EE8509EC2381BDB73B23A4D56ADF2BBF907399151AD7BD491C`; touched-file whitespace search and `git diff --check` passed; startup verification passed with findings empty and Production denied. This is design-only: no source/test/DB/provider/model/trial operation and no ADR/freeze. Independent Sol re-review remains required. All approval/readiness boundaries remain unchanged.

## 2026-09-20 RESEARCH-RETURN-BRIDGE-LAB-V1 design-only checkpoint

Astra added `docs/RESEARCH_RETURN_BRIDGE_DESIGN.md` draft 1. It defines a stateless supplied-synthetic FCFE-per-share Economic Return Bridge, hierarchical prior arithmetic, layer disagreement, a closed nine-row uncertainty ledger, strict non-promotion statuses and an R1–R16 future acceptance matrix. No implementation, database, provider/network call, model fit, financial experiment or research trial occurred. Status is `DRAFT / SOL INDEPENDENT REVIEW REQUIRED / NOT FROZEN`; no implementation is authorized.

Operational documentation was reconciled to the already-established ADR-0018 final browser PASS: DECISIONS, README and FILE_MAP now reflect `PASS_ENGINEERING_RESEARCH_WEALTH_LAB` and controlling report SHA-256 `049195C11ED1690BEE629483EDFDC1BDD58FF7947868BF25F0154D52214EC279`. This changes no frozen semantics or validation boundary.

Observed draft SHA-256: `6946F1608D638244A3677A0338B37DAC84C7290B10ED134DA6293AE10229B26B`. Explicit touched-file trailing-whitespace search returned no matches; `git diff --check` passed; `python scripts/verify_startup.py --root .` returned structural PASS with findings empty, main/UNBORN/dirty and `NOT PRODUCTION READY`. The Sol-high pre-review dispatch ended at the reviewer usage limit before producing a review file, so independent design review remains `NOT VERIFIED`, not failed or passed. All real forecast/provider/PIT/calibration/risk/optimizer/OOS/shadow/Production items remain unverified or unapproved.

Continuation verification on 2026-09-21: `uv --cache-dir .uv-cache run pytest -q --tb=line` completed **212 passed, 2 skipped, 2 known dependency warnings in 117.50s**. Startup verification again passed with findings empty and Production denied; `git diff --check` passed. The two skips remain the documented host-denied Windows symlink cases and are not claimed as covered. `phase2_check.db` and quarantined Nasdaq raw `.txt` captures are now explicitly ignored before any Git delivery; no raw capture was staged or transmitted.

## 2026-09-20 ADR-0018 final actual-browser W18 recheck — ALL-SURFACE PASS

Controlling report `docs/reviews/research_wealth_lab_post_review.md`, SHA-256 `049195C11ED1690BEE629483EDFDC1BDD58FF7947868BF25F0154D52214EC279`. Scoped verdict: `PASS_ENGINEERING_RESEARCH_WEALTH_LAB`. Genuine Codex in-app Browser testing closes the residual W18 surface and links to the already-recorded `PASS_ENGINEERING_RESEARCH_WEALTH_LAB_NON_BROWSER` matrix below.

Desktop and explicit 390px BASE, W6c and W2 passed. Structured alternatives, separate benchmark, 15 unavailable items, non-binding stress labels, event ledgers, open recovery, monetary zero and ruin rendered. W2 preserved the exact editor text and returned only `MISSING /initial_state/cash`. Edit made output stale immediately; stale/rejection/network/mismatch states hid structured output and disabled Download. Evaluate/Load/editor disabled during a real request and re-enabled after it. Literal `<img src=x onerror=alert(1)>` remained text with no injected image/onerror/script/dialog. A controlled disposable-proxy outage visibly returned `Network failure; no current result.`; the proxy was restarted and again returned the expected mismatch.

Normal BASE local rehash enabled Download. Corrupt `artifact_sha256=000...000` retained server `COMPUTED_SYNTHETIC` but displayed browser-local `ARTIFACT_HASH_MISMATCH` and disabled Download. Desktop and 390px independent downloads were each **201,850 bytes**, file SHA-256 `5A55229392B6DABA138A9365126023C7CC28D0A27DCCE1D5B9A2A4C77B68EB29`; internal artifact hash was `7f5bc5e3c82a678b1bc38c4f4d32b594a4678014935b48e7db5f56d781766f2d`. A fresh HTTP 200 BASE POST had the same size/hash and was byte-for-byte equal to the desktop download. Desktop document `clientWidth=scrollWidth=1265`; at explicit `innerWidth=390`, rendered document `clientWidth=scrollWidth=375` after its vertical scrollbar, with textarea overflow internal. Browser viewport was reset and tabs closed.

This is engineering-only evidence. No forecast/model/risk/provider/PIT/calibration/OOS/shadow/Production gate changes: `RISK BUDGET NOT APPROVED`, relevant items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED`, `NOT PRODUCTION READY`.

## 2026-09-20 ADR-0018 final independent B6/W17 recheck — NON-BROWSER PASS

Controlling report `docs/reviews/research_wealth_lab_post_review.md`, SHA-256 `665C19AD9AB03411009317B5C71467EEC955BB24A864D9DC432810790564E987`. Scoped verdict: `PASS_ENGINEERING_RESEARCH_WEALTH_LAB_NON_BROWSER`. Full `PASS_ENGINEERING_RESEARCH_WEALTH_LAB` is not issued because actual-browser W18 remains `NOT VERIFIED`.

Independent of the permanent tests, four fresh disposable-copy invocations covered library/HTTP example/capabilities. Each first completed the real provenance check, mutated copied `optivest/static/wealth_lab.css`, then ran a second real check in the same invocation (`calls=2`). All returned `SOURCE_CHANGED`; HTTP returned 503 canonical failure Evaluation with null provenance/input hash/result. Repository authority/source bytes were not mutated.

Commands/results: focused non-MAX **76 passed, 1 deselected, 2 warnings in 20.94s**; MAX **1 passed, 76 deselected, 2 warnings in 51.66s**, evaluator `47.823778s`, peak `106,716,617` bytes, Evaluation `14,040,496` bytes, Artifact `14,553,939` bytes; full **212 passed, 2 skipped, 2 warnings in 127.78s**. Python compile, JavaScript syntax, startup verifier, exact hashes, `git diff --check` and explicit relevant-file whitespace inspection passed. Startup reported main/UNBORN/18 untracked root paths and `NOT PRODUCTION READY`.

Disposable SQLite: lab POST HTTP 200/`COMPUTED_SYNTHETIC` preserved exact counts across 32 application tables/43 rows. Provider/readiness reads also preserved counts and stayed 403 `BLOCKED_POLICY`, `NOT PRODUCTION READY`, `PROVISIONAL / RISK BUDGET NOT APPROVED`. Preflight was isolated from the no-write assertion: it remained `eligible_for_research_decision=false` and added only one designed `decision_snapshots` row. Downgrade-base/upgrade-head/reseed returned `0003_research_risk_editor`, 32 tables/43 rows. Trial ledger stayed 0 bytes with SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

Authority hashes matched Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, design `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`, and pre-review `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83`. No implementation/test/frozen authority/ADR/model/service/risk-editor/Phase-2/migration/dependency/lock/provider/user-database/trial/Production-gate file changed. Investment/model/provider/PIT/OOS/shadow/Production boundaries remain unchanged.

## 2026-09-17 ADR-0018 final minimal B6/W17 correction evidence

Permanent disposable-copy tests now prove both `example_bytes()` and `capabilities()` re-read Policy/design/manifest immediately before emission across library and HTTP GET. A copied manifest mutation after the initial clean real check returns root `SOURCE_CHANGED`; GET returns HTTP 503 canonical failure Evaluation with null provenance/input hash/result.

Final results: focused non-MAX **76 passed, 1 deselected, 2 known warnings in 18.88s**; MAX **1 passed, 76 deselected in 38.04s** with evaluator `34.792737s`, peak `106,716,558` bytes, Evaluation `14,040,496` bytes and Artifact `14,553,939` bytes; full **212 passed, 2 skipped, 2 known warnings in 108.05s**. This is Terra evidence pending independent Sol recheck, not an engineering acceptance claim. Actual-browser W18 remains `NOT VERIFIED`.

## 2026-09-17 ADR-0018 independent Sol correction recheck — FAILED / REVIEW_REQUIRED

Controlling report `docs/reviews/research_wealth_lab_post_review.md`, SHA-256 `B6E2DBE01128DF5C0CAC3649EF70A07940ED2829C73C739DF0B03EFE8187016D`. Frozen Policy/design/pre-review hashes remain `ACF013CE...38E67` / `4097F897...74B80C` / `AACE3319...31E83`; the prior post-review baseline matched `EEF7BF9D...520B` before the dated addendum. Branch main, HEAD UNBORN, 18 untracked paths.

Independent B1-B5/B7/static-B8 counterexamples pass. Evaluation load/pre-emission changes, Git unavailable/unborn, and initial example authority pass. Residual B6/W17 blocker: in a copied authority/source root, a wrapper ran the real provenance check then changed copied `wealth_lab.css`; GET example still returned HTTP 200/17,975 bytes and GET capabilities HTTP 200/4,645 bytes with only one provenance call. Frozen section 7 requires the second check immediately before emission; expected result is SOURCE_CHANGED/503. Actual-browser W18 remains unavailable and `NOT VERIFIED`, so W18 is not the only blocker.

Commands/results: focused non-MAX **72 passed, 1 deselected, 2 warnings in 18.70s**; MAX **1 passed, 72 deselected, 2 warnings in 40.37s**, evaluator `36.962977s`, peak `106,717,753` bytes, Evaluation `14,040,496` bytes, Artifact `14,553,939` bytes; full **208 passed, 2 skipped, 2 warnings in 110.85s**. Python compile, JS syntax, startup verifier and `git diff --check` passed; startup findings were empty and reported main/UNBORN/dirty plus NOT PRODUCTION READY. Explicit relevant-file trailing-whitespace inspection was empty; tracked diff remains limited by the wholly untracked checkout.

Independent probes also passed exact W3/W4/W7/W8/W10/W11/W14/MAX arithmetic, raw RFC-6901 pointer fidelity, Stage-5 nested aggregation/no-descent, Stage-6 missingness, Stage-7 cross-record aggregation, authority-first/incrementally bounded HTTP, canonical byte/rehash parity, and CLI missing/nonregular/unreadable/misuse/success/restart/output-failure contracts. Disposable SQLite POST preserved exact row maps across 32 application tables/43 rows; provider route remained 403/BLOCKED_POLICY, preflight remained false, status remained NOT PRODUCTION READY/RISK BUDGET NOT APPROVED, migration round trip returned `0003_research_risk_editor`/32 tables, and the empty trial ledger hash remained `E3B0C442...B855`.

No implementation, test, frozen authority, ADR, model/service/risk-editor/Phase2, migration, dependency/lock, provider, user database, trial, or production-gate file was changed. Verdict `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`; all investment/model/provider/PIT/OOS/shadow/Production gates remain open.

## 2026-09-16 ADR-0018 Terra B1-B8 correction evidence — Sol recheck pending

Permanent `test_post_review_b1` through `b8` regressions cover the controlling Sol counterexamples without changing frozen semantics. Final focused non-MAX: **72 passed, 1 deselected, 2 known dependency warnings in 18.69s**. Final MAX: **1 passed, 72 deselected in 38.05s**; evaluator `34.808847s`, peak `106,715,219` bytes, Evaluation `14,040,496` bytes, Artifact `14,553,939` bytes, exact bounded dimensions retained. Final full regression after the complete dual-precision payload and last bounded decoder hardening: **208 passed, 2 skipped, 2 known dependency warnings in 108.25s**.

Python compile, JavaScript syntax, startup verifier and `git diff --check` passed. Startup findings were empty and reported `main`/`UNBORN`/dirty and `NOT PRODUCTION READY`. Raw hashes remain Policy `ACF013CE...38E67`, design `4097F897...74B80C`, pre-review `AACE3319...31E83`, post-review `EEF7BF9D...520B`. A disposable migrated/seeded SQLite POST was HTTP 200/COMPUTED_SYNTHETIC and preserved exact all-table counts across 32 application tables; a separate downgrade-base/upgrade/seed ended at `0003_research_risk_editor` with 32 application tables. No user database or trial was changed.

This is Terra evidence only, not `PASS_ENGINEERING`. Actual-browser W18 remains `NOT VERIFIED`; no available backend was present and static race/presentation tests are not substituted. Independent Sol recheck is required; all model/provider/PIT/OOS/shadow/Production boundaries remain unchanged.

## 2026-09-16 ADR-0018 independent Sol post-validation — FAILED / REVIEW_REQUIRED

Controlling report: `docs/reviews/research_wealth_lab_post_review.md`, SHA-256 `EEF7BF9D550AC4F615904FEABBBDD5EA33F37DB041C235B81AD3BF1346FF520B`. Authority bytes match Policy `ACF013CE...38E67`, design `4097F897...74B80C`, and pre-review `AACE3319...31E83`; branch main / HEAD UNBORN / 18 untracked paths. Independent Decimal oracles reproduced W3 `38/98/44.8/66/110.8`, W4 `ln(.98)/7`, W8 `ln(1.25)/7`, W10 zero, W11 `+/-ln(2)/14` and `+ln(2)/7`, plus MAX counts `160/13,760/1,700/53,760`.

Automated evidence: fast focused **64 passed, 1 deselected in 7.40s**; MAX **1 passed, 64 deselected in 37.20s**, evaluator elapsed `34.314532s`, peak `110,912,802` bytes, Evaluation `14,036,616` bytes, Artifact `14,550,059` bytes; full **200 passed, 2 skipped, 2 known dependency warnings in 98.52s**. Python compile, JavaScript syntax, startup integrity and `git diff --check` passed. Exact success bytes matched library/CLI/HTTP. A disposable lab POST preserved every table count; provider display was 403/BLOCKED_POLICY; decision preflight stayed ineligible; readiness stayed NOT PRODUCTION READY; downgrade/upgrade/seed ended at `0003_research_risk_editor` with 33 application tables; research-trial bytes were unchanged.

Green tests are insufficient. B1-B8 counterexamples reproduce wrong initial-cost PRE_TRADE/drawdown/recovery, absent canonical semantic/D/text normalization and self-inconsistent input hash, rounded-before-aggregation benchmark arithmetic, incomplete dual-precision/private-invariant seams, escaped-surrogate INTERNAL_ERROR and wrong combined depth/node precedence, missing simultaneous distribution reversal, missing pre-emission source recheck/wrong Git/example authority, HTTP/CLI closed-contract deviations, and incomplete/racy UI. Actual-browser W18 remains NOT VERIFIED because the current browser attempt found no backend. Verdict: `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`; no engineering/model/§18 promotion.

## 2026-09-16 ADR-0018 Stage-5 exhaustive nested aggregation

The final non-browser implementation gap is closed. Permanent adversarial tests prove simultaneous deterministic aggregation of all six Stage-5 codes across mandate, assets, positions, ordinary/stress path months and asset points, probability family/distributions/masses, alternatives/costs, benchmark paths/levels and uncertainty-ledger rows. Separate tests prove no descent into invalid containers or unknown keys and prove valid cross-surface missing V tags retain Stage-6 `INPUT_INCOMPLETE` aggregation. Decoder single-failure and Stage-7 cross-record precedence remain covered.

Evidence: `uv run pytest -q tests/test_wealth_lab.py -k "not maximum_dimensions" --tb=short` -> **64 passed, 1 deselected in 7.68s**; MAX -> **1 passed, 64 deselected in 38.25s**; `uv run pytest -q --tb=short` -> **200 passed, 2 skipped, 2 known upstream TestClient warnings in 96.93s**. `py_compile`, `node --check`, startup integrity and `git diff --check` passed. Startup findings were empty and reported `main`/`UNBORN`/dirty plus `NOT PRODUCTION READY`. Policy/design/review hashes remain `ACF013CE...38E67` / `4097F897...74B80C` / `AACE3319...31E83`.

This makes the implementation ready for independent Sol post-validation but is not that validation and is not `PASS_ENGINEERING`. Only W18 stale/in-flight/error/XSS/ruin/download-rejection actual-browser evidence remains `NOT VERIFIED`; earlier desktop/390px BASE success remains bounded evidence. No database/provider/network/decision/trial/Production state changed.

## RESEARCH-WEALTH-LAB-V1 continuation (2026-09-15)

Final bounded continuation: `uv run pytest tests/test_wealth_lab.py -q -k "not maximum_dimensions"` -> **60 passed, 1 deselected in 8.30s**; MAX separately -> **1 passed, 60 deselected in 36.90s**; final full `uv run pytest -q` -> **196 passed, 2 skipped, 2 known TestClient deprecation warnings in 100.35s**. `py_compile`, `node --check`, startup integrity and `git diff --check` passed; the checkout remains `main`/`UNBORN`/18 untracked paths, so the git-diff result has its usual untracked limitation. The selected Policy/design/review hashes remained the frozen values recorded in HANDOFF.

New evidence: deterministic valid-shape Stage-7 cross-record multi-finding aggregation is permanently covered alongside W6e/f, W10, W12 and W13 independent fixtures. Stage-5 envelope aggregation exists, but arbitrary nested typed/domain faults still return the first `LabError`; the frozen exhaustive Stage-5 aggregation requirement remains open. Disposable copied-checkout tests observed `SOURCE_CHANGED` followed by a computed fresh import, exact Policy/design mismatch, source missing and Git `UNBORN`; originals were unchanged. A new disposable populated SQLite database completed upgrade/seed/downgrade-base/upgrade/seed at `0003_research_risk_editor` (32 application tables); TestClient POST was HTTP 200/`COMPUTED_SYNTHETIC` with exact before/after row maps equal. Browser retry returned no available browser: retain the already observed desktop/390px BASE rehash/download success, but stale/in-flight/error/XSS/ruin/download-rejection cases are **NOT VERIFIED**. No provider, network, decision, user-DB or production operation occurred. This is not independent Sol acceptance.

`python -m pytest tests/test_wealth_lab.py -q` -> **57 passed in 50.52s**. Full `python -m pytest -q` -> **192 passed, 2 skipped, 2 known FastAPI/Starlette TestClient deprecation warnings in 116.47s**. The new permanent tests independently cover W3/W4 exact cost-once ledger values, W5 funding/no-trade, W6 settlement/ruin/cash loss, W7/W8 coupling, W9 recovery anchor, W11 separate lower-envelope minimum, W14 public 1/3 representation, W17 canonical Unicode and authority/loaded-source refusal, and W19 MAX/fault seams.

MAX actual-host measurement: 160 alternative paths, 13,760 alternative events, 1,700 benchmark events and 53,760 asset-month-alternative cells; Evaluation bytes=14,036,616, Artifact bytes=14,550,059; tracemalloc elapsed=40.777389s, peak=110,916,726 bytes. The fixed MAX test records (rather than masks) the `>10 seconds` review trigger; measured memory is below 256MiB. An isolated 33-table SQLite database had identical all-table row counts before/after HTTP lab evaluation. This does not establish provider, model or production behavior.

Residual evidence is explicit: exhaustive nested typed/cross-record aggregation, the rest of the frozen W6/W10/W12/W13 exact fixture matrix, disposable-checkout source-byte mutation, isolated migration downgrade/upgrade, and browser stale/error/XSS/ruin/download tests were not completed. The original browser desktop/390px success/re-hash/download evidence remains valid; a new session was unavailable for the remaining browser interactions. No §18 status is promoted.

## RESEARCH-WEALTH-LAB-V1 Terra milestone (2026-09-15)

`uv run pytest tests/test_wealth_lab.py -q` -> **46 passed**. `uv run python -m py_compile optivest/wealth_lab.py optivest/wealth_lab_api.py optivest/cli.py optivest/app.py` and `node --check optivest/static/wealth_lab.js` passed. `uv run python scripts/verify_startup.py --root .` reported `startup_integrity=PASS`, no findings, `main`/`UNBORN`/18 untracked paths and `NOT PRODUCTION READY`; Policy/design/review hashes remained respectively `ACF013CE...38E67`, `4097F897...74B80C`, `AACE3319...31E83`. `git diff --check` had no output but is limited by the wholly untracked checkout.

In a fresh disposable SQLite file, migrations plus research/Phase2 seed completed; FastAPI TestClient then proved accepted OWS/case-insensitive JSON media, gzip 415, `/wealth-lab` 200, and exact successful HTTP bytes equal the library's canonical Artifact. CLI `wealth-lab evaluate --file optivest/fixtures/wealth_lab_example.json` succeeded while `OPTIVEST_DATABASE_URL=sqlite:///Z:/invalid-do-not-open.db`, demonstrating the early lab dispatch did not use that database. In-app browser checks at desktop and explicit 390px loaded/evaluated the example, independently rehashed its Artifact, enabled download, retained `SYNTHETIC ACCOUNTING LAB — NOT AN INVESTMENT MODEL`, and had page `scrollWidth=375` at width 390; the textarea retained its intended internal scroll. No external provider/network or user database was used.

The complete suite was then captured through a separate local process: `python -m pytest -q` -> **181 passed, 2 skipped, 2 TestClient deprecation warnings in 68.51s**. This is still focused engineering evidence, not W1-W19 completion or acceptance. Exhaustive typed/cross-record aggregation, MAX/resource/size, source/restart mutations, migration/no-write regression and the remaining browser error/stale/XSS/ruin/download checks remain pending. No Policy §18 gate changes.

## RESEARCH-WEALTH-LAB-V1 Terra implementation checkpoint (2026-09-14)

Follow-up focused run after terminal-zero and canonical-example corrections: `python -m pytest tests/test_wealth_lab.py -q` -> `29 passed`. The permanent test module now has row-labelled W1-W19 regression anchors plus direct W1 raw/depth/duplicate, W6 terminal-zero/reversal/ruin, W9 equal-high recovery, W14 probability-sum, W17 manifest and canonical example checks. This remains incomplete relative to the full section 8.1 matrix and is not a completion/acceptance claim. Browser runtime remains unavailable.

Bounded input/output-contract follow-up: `python -m pytest tests/test_wealth_lab.py -q` -> `33 passed`; compile and JS syntax passed. Added exact seven-row ledger registry closure, source-manifest loaded-context refusal, canonical example bytes, media/encoding HTTP probe, terminal-zero price/distribution reversal checks, and typed-invalid-over-missing precedence. Disposable SQLite TestClient probe passed accepted OWS/case-insensitive JSON media, rejects text/json and gzip at 415, and capabilities 200; CLI evaluate remained DB-free under an invalid `OPTIVEST_DATABASE_URL`. These are W1/W2/W6/W12/W13/W15/W17-relevant partial engineering checks, not complete W-item dispositions or acceptance.

Comparator/result follow-up: `python -m pytest tests/test_wealth_lab.py -q` -> `36 passed`; Python compile and JavaScript syntax passed. Added comparator-only benchmark path/summaries/lower-envelope output (no holdings fraction, target weight, recommendation or action), closed result-key assertions, multi-member supplied-family ordering/difference-field regression and nested unknown/missing-key negatives. This advances W1/W11/W12/W13/W17-relevant output behavior but does not yet provide the frozen exhaustive nested-pointer/aggregation/size matrix or any engineering acceptance.

Stress-output follow-up: `python -m pytest tests/test_wealth_lab.py -q` -> `37 passed`; compile and JS syntax passed. Alternative and Benchmark stress path records now use the same terminal/drawdown/recovery shapes as ordinary paths while probability summaries/lower envelopes remain ordinary-path-only; direct W12 regression asserts that separation. Nested duplicate-pointer fidelity and independent multi-finding aggregation are still not implemented, so this is not closure of the parser/aggregation batch.

Nested duplicate-pointer follow-up: `python -m pytest tests/test_wealth_lab.py -q` -> `41 passed`; `python -m py_compile optivest/wealth_lab.py` passed. The raw decoder now syntax-validates before a lexical duplicate pass, returning the first duplicate member in wire order with RFC-6901 ancestor/array paths and `~`/`/` escaping. Permanent W1 cases cover alternatives/cost envelope, probability member/mass, joint path/month/asset and arbitrary escaped metadata ancestry. Failure remains `JSON_INVALID` without body echo. API and CLI share `evaluate_bytes`; transport does not rewrite the decoder result. Independent validator aggregation remains a separate unclosed item.

Aggregation follow-up: `python -m pytest tests/test_wealth_lab.py -q` -> `42 passed`; compile passed. Added deterministic non-cascading aggregation for independent closed Bundle-envelope unknown/missing/literal errors, sorted by JSON pointer then code, with a permanent five-finding exact-array fixture. Decoder/authority/transport still retain single-failure precedence. This does not yet aggregate every nested typed/cross-record rule, so it is not full completion of the frozen aggregation contract.

Changed only ADR-0018-authorized application files: `optivest/wealth_lab.py`, `optivest/wealth_lab_api.py`, `optivest/static/wealth_lab.js`, `optivest/static/wealth_lab.css`, `optivest/fixtures/wealth_lab_example.json`, `tests/test_wealth_lab.py`, narrow route/CLI dispatch, README and operational records. The implementation is stateless and raw-byte-only at its public core; it performs supplied synthetic ledger accounting and retains literal non-production boundaries. No model, calibration, provider, decision, risk feasibility, action, order, DB writer, migration, trial or Production state changed.

Observed focused evidence: `python -m pytest tests/test_wealth_lab.py -q` -> `4 passed`; `python -m py_compile optivest/wealth_lab.py optivest/wealth_lab_api.py optivest/cli.py optivest/app.py` -> exit 0; `node --check optivest/static/wealth_lab.js` -> exit 0; `python scripts/verify_startup.py --root .` -> structural PASS / findings [] / main UNBORN dirty / NOT PRODUCTION READY. A fresh disposable SQLite upgrade/seed plus TestClient probe reached `/wealth-lab` 200 and capabilities 200; the POST status mapping was corrected after the probe exposed a success-artifact 503 transport defect. Browser-control runtime reported no browser available, so actual desktop/390px evidence is NOT VERIFIED.

This is not PASS_ENGINEERING and not a W1-W19 acceptance claim. The full `pytest -q` invocation produced partial progress output but no captured completion summary in this runtime; treat full-regression status as NOT VERIFIED and rerun before Sol review. Exhaustive W1-W19 parser, failure, MAX, source-mutation, migration/no-write and browser evidence remains pending. All §18/model/PIT/OOS/shadow/provider states remain unchanged.

## ADR-0018 RESEARCH-WEALTH-LAB-V1 scoped freeze (2026-09-14)

Astra verified selected Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, passed design revision2 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C` and controlling Sol review `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83`, read the six freeze conditions and added ADR-0018 / D0010. Only Decisions/operational records changed. No application code/test, DB, provider/network, empirical trial, calibration/OOS/shadow or Production check was performed. W1-W19 are mandatory pending implementation evidence, not executed PASS results. Design freeze does not promote a §18 gate or create PASS_ENGINEERING. Terra implementation and independent Sol post-validation are pending.

Final freeze checks: `python scripts/verify_startup.py --root .` exit0, structural PASS, findings[], actual main/UNBORN/dirty, NOT PRODUCTION READY; `git diff --check` exit0. Re-hashing confirmed Policy/design/review bytes unchanged. Explicit whitespace search in Decisions/START_HERE/TODO/FILE_MAP found no matches (rg exit1 means no matches). The repository remains untracked, so tracked git-diff success is limited and new ADR/operational content was inspected directly.

## RESEARCH-WEALTH-LAB-V1 revision-2 independent pre-review PASS (2026-09-14)

Exact corrected design SHA-256 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`; controlling updated review `docs/reviews/research_wealth_lab_pre_review.md` SHA-256 `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83`; selected Policy remains `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`. Independent standard-library Fraction/Decimal calculations rechecked W3/W4/W8/W10/W11/W14 and MAX dimensions. B1-B6 and each W1-W19 oracle are closed for design freeze. Verdict `PASS FOR SCOPED DECISION FREEZE`.

This is document/specification review only. No wealth-lab implementation, pytest, DB, provider/network, browser, OOS, shadow or model test exists or was run; no research trial was created. Review PASS does not establish engineering acceptance or any Policy §18 item. `python scripts/verify_startup.py --root .` exited0 with `startup_integrity=PASS`, findings `[]`, actual main/UNBORN/dirty and `NOT PRODUCTION READY`. `git diff --check` exited0 but has the known all-untracked limitation; explicit touched-file inspection found no trailing whitespace.

## RESEARCH-WEALTH-LAB-V1 revision-2 design correction (2026-09-14)

Corrected draft SHA-256 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`, responding only to B1-B6 of unchanged Sol review `DAF4A7A18123A9CE136EEC4795CB1C18FA64D60E2AB4811471A4EC2726B30646`. Selected Policy remains `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; frozen editor design `F9EC...B950` and retained reviewer test `EF9E...799B` hashes unchanged. Explicit `rg -n '\s+$' docs/RESEARCH_WEALTH_LAB_DESIGN.md` found no trailing whitespace. No application/DB/provider/network/browser/model/OOS test or trial was performed; BASE/MAX and revised W-oracles are future independently decidable acceptance specifications, not measured implementation results. Status `CORRECTED DRAFT / SOL INDEPENDENT RE-REVIEW REQUIRED / NOT FROZEN`. All prior scoped engineering and mandatory non-production states remain unchanged.

After updating continuity records, `python scripts/verify_startup.py --root .` exited 0, structural startup PASS, findings [], actual main/UNBORN/dirty, Production denied. `git diff --check` exited 0; this only checks tracked content, so it does not substitute for explicit revised/new-file inspection in the untracked repository.

## RESEARCH-WEALTH-LAB-V1 independent pre-review (2026-09-14)

Exact reviewed draft SHA-256 `2DDDC542373193ABAE53165A66AE96151AFDE9FB3662F04B2EBC7F6448492AA3`; selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`. Independent standard-library Decimal calculations reproduced W3/W4/W10/W11, and direct algebra verified W7's infinity ordering. The review found six design blockers and dispositioned every W1-W19 item; controlling report `docs/reviews/research_wealth_lab_pre_review.md`, SHA-256 `DAF4A7A18123A9CE136EEC4795CB1C18FA64D60E2AB4811471A4EC2726B30646`. Verdict `DESIGN CHANGE REQUIRED / NOT READY FOR SCOPED DECISION FREEZE`.

No application, pytest, DB, provider/network, browser, OOS, shadow or model test was run because no wealth-lab implementation exists. No research trial was created. `python scripts/verify_startup.py --root .` exited 0 with `startup_integrity=PASS`, findings `[]`, actual main/UNBORN/dirty and `production_readiness=NOT PRODUCTION READY`. `git diff --check` exited 0 but is limited to tracked content in this wholly untracked repository; explicit inspection found no trailing whitespace in the new review. These checks cannot convert the document review into engineering/model/Production acceptance. All existing scoped engineering acceptances remain unchanged.

## RESEARCH-WEALTH-LAB-V1 design-only checkpoint (2026-09-14)

Draft 1 SHA-256 `2DDDC542373193ABAE53165A66AE96151AFDE9FB3662F04B2EBC7F6448492AA3`; selected Policy hash unchanged `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`. `git diff --check` returned exit 0, limited to tracked content in this main/UNBORN/untracked repository. No code changed and no application, numerical/model, provider, DB, OOS or shadow test was run in the design pass. The 19-row acceptance matrix contains future tests and independent-oracle examples, not observations. Status `DRAFT / SOL INDEPENDENT REVIEW REQUIRED / NOT FROZEN`; prior scoped engineering acceptances below are unchanged. No §18 evidence item or research trial was promoted/created.

After the operational checkpoint, `python scripts/verify_startup.py --root .` returned exit 0, `startup_integrity=PASS`, findings [], actual main/UNBORN/dirty, and `production_readiness=NOT PRODUCTION READY`. This is structural governance verification only.

## RESEARCH-RISK-EDITOR-V1 final independent acceptance (2026-09-13)

| Check | Result | Evidence / limitation |
|---|---|---|
| Authority and retained reviewer | PASS | Policy `ACF013...E67`; frozen design `F9EC...B950`; retained independent test byte-identical at `EF9E...799B`; main/UNBORN. |
| Applicable M-wrapper grammar | PASS | Independent exhaustive matrix: 30/30 reserved-reason direct mutations and 30/30 API mutations rejected `FIELD_NOT_APPLICABLE`; nonreserved incomplete reasons remained valid. |
| Initial/hydrated editor | PASS | Initial HTML exposes 19 visible labelled readonly row controls plus rationale; hydration removes them and renders 19 rows, 2 row-16 components and zero aggregate direct controls. No hidden compatibility anchors. |
| Real desktop/mobile browser | PASS | Desktop and 390x844 had no horizontal overflow; mobile effective `clientWidth=scrollWidth=375`, zero offenders. Current V1 showed `CUSTOM_RESEARCH` and source `BALANCED_RESEARCH_V1`. |
| Browser behavior | PASS, disposable SQLite | Structured edit, explicit clear/reason, preview-before-save, provisional save, reload, history, stale conflict/draft preservation and XSS-safe rendering passed. Provider-blocked matrix: editor 200, home/datasets 403 `BLOCKED_POLICY`. No external call. |
| Focused suites | PASS | `uv --cache-dir .uv-cache run pytest -q --tb=line tests/test_risk_editor_independent_review.py tests/test_risk_editor.py`: **63 passed, 2 warnings in 24.55s**. |
| Full suite | PASS | `uv --cache-dir .uv-cache run pytest -q --tb=line`: **135 passed, 2 skipped, 2 warnings in 57.24s**. Skips remain host-denied Windows symlink cases. |
| Compile / JS / startup / whitespace | PASS, structural only | Python `py_compile`, `node --check`, startup checker and `git diff --check` passed; startup findings empty and Production denied. |
| Disposable artifact | REMOVED | Confirmed `data/browser_u3_20260913.db` and its port-8768 helper were review-only; stopped helper and removed DB. User/protected DBs untouched. |
| Independent verdict | **`PASS_ENGINEERING_RESEARCH_RISK_EDITOR`** | Scoped engineering acceptance only; see post-review section 13, SHA-256 `6B49E8FF640B7648A9875F7572B205D5FA89B9241A6E935406B4580A22E55CB3`. |

Mandatory limits remain: `RISK BUDGET NOT APPROVED`; numerical feasibility, impact and calibration, provider/PIT truth, investment model and OOS remain `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

## RESEARCH-RISK-EDITOR-V1 U1-U3 Terra correction checkpoint (2026-09-13)

| Check | Result | Evidence / limitation |
|---|---|---|
| Applicable M-wrapper grammar | PASS, Terra-only | `risk_editor.py` centrally rejects `NOT_APPLICABLE` when a selected Risk/Stress/Hybrid M wrapper is applicable; other explicit nonblank null reasons remain valid incomplete declarations. New direct-schema plus API regressions cover ROBUST_CHANCE epsilon, BINDING stress version and Hybrid observed component. |
| Server-rendered editor contract | PASS, Terra-only | `/risk-budget` supplies 19 visible, labelled readonly pre-hydration row controls (plus rationale), then JS removes them when a structured draft hydrates. The retained independent test was not changed. |
| 390px structured browser probe | PASS, Terra-only | Isolated SQLite only, local `127.0.0.1`: after Balanced template hydration, 19 rows rendered; `scrollWidth=375`, `clientWidth=375`; initial controls removed; current summary includes `name` and `source_preset`. This does not replace Sol's independent browser acceptance. |
| Focused editor + retained independent suites | PASS | `uv --cache-dir .uv-cache run pytest -q tests/test_risk_editor.py tests/test_risk_editor_independent_review.py --tb=short`: **63 passed, 2 warnings**. |
| Compile / JS / startup / whitespace | PASS, structural only | Python `py_compile`, `node --check optivest/static/risk_editor.js`, startup checker and `git diff --check` passed. |
| Validation status | **IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED pending Sol** | No engineering PASS, numerical feasibility, impact, calibration, provider/PIT, OOS, shadow, approval or Production gate changed. |

The temporary `data/browser_u3_20260913.db` was created only for the isolated local browser probe; it is not a user database and no destructive cleanup was attempted. `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain mandatory.

## RESEARCH-RISK-EDITOR-V1 bounded correction — Sol revalidation (2026-09-13)

| Check | Result | Evidence / limitation |
|---|---|---|
| Policy/design identity | PASS | Policy `ACF013...E67`; frozen design `F9EC...B950`; main/UNBORN. |
| Focused retained + new editor suites | **FAIL** | `1 failed, 59 passed, 2 warnings in 25.09s`; retained static-HTML assertion sees 1 input before deferred JS instead of >=19. |
| Full suite | **FAIL** | `1 failed, 131 passed, 2 skipped, 2 warnings in 95.05s`; same assertion. Skips remain host-denied symlink cases. |
| Populated 0003→0002→0003 | PASS, isolated SQLite | Preserved 2 budgets/38 constraints/2 providers; editor tables removed/recreated; verifier VALID and current head `LEGACY_NOT_VERIFIED`; minimum comparators `>=`. |
| Historical/schema corruption | PASS for dispatched probes | Reversed V1 arrays, unauthorized marker column and rehashed historical `LEVERAGE=1` each block startup/status/preflight 503 with zero snapshot insertion. |
| Preview transaction/response | PASS | SQL trace begins with explicit `BEGIN`; checked row counts unchanged; observed heads, complete legacy diagnostics and UTC `Z` timestamp present. |
| Concurrent CAS/fault/busy | PASS for exercised SQLite contract | Two clients: one 201/one 409 `HEAD_CONFLICT`, no orphan rows; retained rollback/busy cases pass. |
| Additional closed-grammar falsification | **FAIL / BLOCKING** | Applicable Risk/Stress/Hybrid null wrappers accept reserved `NOT_APPLICABLE`; frozen section 2 requires rejection. |
| Actual structured browser | **FAIL / BLOCKING overall** | Desktop mechanics, XSS, stale handling, row-16 grouping and provider boundary pass. Mobile 390x844 overflows horizontally; current preset/name are not explicit. |
| Compile / JS / startup / whitespace | PASS, structural only | `py_compile`, `node --check`, startup checker and `git diff --check`; Production remains denied. |
| Independent verdict | **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`** | See post-review section 12. No editor engineering PASS. |

No numerical feasibility, impact, calibration, `U_risk`, `S_stress`, provider/PIT, OOS, shadow, personal suitability, approval or Production gate changed. `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain mandatory.

## RESEARCH-RISK-EDITOR-V1 T1–T4 correction checkpoint (2026-09-10)

Sol partial reproduction: `uv run pytest -q tests\test_risk_editor.py --tb=line` passed **31 tests, 2 warnings**. The startup checker passed when rerun with the repository-scoped `.uv-cache`; the first default-cache invocation failed on host cache permissions, not application behavior. `node --check` and `git diff --check` passed. Full independent section-11 validation remains pending.

Pre-UI `uv --cache-dir .uv-cache run pytest -q --tb=short tests\test_risk_editor.py tests\test_risk_editor_independent_review.py` passed **51 tests**. After adding the T1–T4/API/UI regressions and structured assets, `uv --cache-dir .uv-cache run pytest -q --tb=short tests\test_risk_editor.py` passed **31 tests** with three host/dependency/cache warnings. Python compile, `node --check optivest\static\risk_editor.js`, startup checker, exact Policy hash and `git diff --check` passed. The full suite, populated 0003→0002→0003 roundtrip, direct preview SQL trace and real-browser structured interaction were not run in this quota-bounded pass and remain `NOT VERIFIED`; Sol independent revalidation remains required. No numerical/model/provider/PIT/OOS/shadow/Production gate changed.

Updated: 2026-09-09. Scope: completed Phase 0, PHASE1-V1 and PHASE2-V1 offline engineering, not provider/PIT/full Phase 2 or an investment-model release.

| Check | Status | Evidence / limitation |
|---|---|---|
| Selected Policy full read | PASS | 841 lines read in bounded chunks |
| Source/copy SHA-256 | PASS | Both ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67 |
| Repository initial inspection | PASS | Only two user files existed; no source/deps/tests/.ai/Git |
| Git initialization | PASS | git init -b main; HEAD UNBORN |
| Governance file consistency | PASS, structural only | Parent ran python scripts/verify_startup.py --root .; exit 0, main/UNBORN, findings empty; readiness denied |
| Package install / import | PASS | `uv sync --locked`; FastAPI application and CLI imported during tests/HTTP run |
| Static type / dedicated lint | NOT VERIFIED | No mypy/pyright/ruff gate selected in PHASE1-V1; `git diff --check` PASS |
| Phase 0 Unit | 13 PASS / 1 SKIPPED | Parent and Sol independently ran python -m unittest discover -s tests -v; direct file-symlink creation unavailable on Windows |
| Application Unit / Integration | PASS for PHASE1-V1 | Detailed matrix below; no investment model included |
| CLI / API / DB / UI | PASS for PHASE1-V1 | Detailed matrix below; no external batch/provider adapter included |
| Data quality / PIT / tradability | NOT VERIFIED | No provider or data snapshot verified |
| Numerical / Model / Portfolio accounting / Constraints / Actions | NOT VERIFIED | No implementation or calibrated inputs |
| Backtest / Locked OOS | NOT VERIFIED | No dataset, split or outcomes |
| Shadow / Paper | SHADOW VALIDATION NOT PASSED | Not started |
| Independent Phase 0 pre-review | PASS, scoped contract only | Sol blind first pass then phase0_pre_review.md; design hash 43FCCF65CD4320B76D835198E2C18A0DD1FF87F1A0B2E88571B0360A7A65A364 |
| Independent Phase 0 post-review | PASS, PHASE0-V1 only | Sol reproduced suite and actual CLI, rejected junction escape, verified byte-identical read-only run; no remaining blocker |

## PHASE1-V1 evidence

| Check | Status | Evidence / limitation |
|---|---|---|
| Dependency lock | PASS | `uv sync --locked`; resolved Alembic 1.19.2, FastAPI 0.141.1, HTTPX 0.28.1, Pydantic 2.13.5, pytest 9.1.1, SQLAlchemy 2.0.52, Uvicorn 0.52.4 |
| Phase 1 unit/integration/API | 20 PASS / 1 SKIPPED / 2 warnings | Parent and Sol runs; skipped Phase 0 direct file-symlink fixture; warnings are upstream TestClient/AnyIO deprecations |
| Migration | PASS for SQLite local/test | Fresh Alembic upgrade → downgrade → upgrade; Sol reflected 15 → 1 → 15 tables; PostgreSQL NOT VERIFIED |
| Seed / CLI verify | PASS, research-only | Explicit idempotent seed; verify is read-only; exact Policy hash and 19 provisional constraints; Production denial |
| DB invariants | PASS for reviewed SQLite scope | FK, immutable rows, heads/CAS, stable identity, chronology, presence/use-state including NULL-safe conflict group |
| API / UI / HTTP | PASS for reviewed local scope | 15 API paths; fresh process returned 200 for status/OpenAPI/root; desktop/mobile displayed two forms and denial labels; no action/weight/order routes |
| Provider / PIT truth | NOT VERIFIED | Declarations cannot self-validate; no external source/calendar/history collected |
| Investment/model/portfolio/backtest/OOS | NOT VERIFIED | Not implemented |
| Shadow / Paper | SHADOW VALIDATION NOT PASSED | Not started |
| Independent Phase 1 post-review | PASS_ENGINEERING_P1 | Sol final report hash recorded in ADR-0014; no remaining engineering blocker |

Production: `NOT PRODUCTION READY`. All 25 selected Policy §18 requirements remain 0 PASS / 25 NOT VERIFIED. Phase 0/1 engineering checks cannot pass investment gates. Known test limitations: direct file-symlink fixture skipped due host privilege, while a native junction escape was independently rejected; two upstream dependency deprecation warnings. Unimplemented/unexecuted investment checks remain NOT VERIFIED.

## PHASE2-V1 remediation evidence (2026-09-09)

| Check | Status | Evidence / limitation |
|---|---|---|
| Phase 2 fixture/unit/integration/API | PASS for remediated engineering scope | `uv run pytest -q`: 53 passed, 2 skipped, 2 upstream dependency warnings. Added paired-Nasdaq second-part failure and initial-terminal-run DB-bypass regressions. |
| Python compile / whitespace | PASS | `uv run python -m py_compile optivest\\phase2.py alembic\\versions\\0002_phase2.py`; `git diff --check` passed. |
| SQLite migration round trip | PASS, local/test only | Fresh DB: CLI upgrade and Phase 2 seed, `0002_phase2 -> 0001_phase1 -> 0002_phase2`, reseed, then read-only `verify-phase2` returned exact head/schema and raw-integrity true. The intermediate Phase 1 downgrade intentionally removes Phase 2 seed records. |
| Phase 2 DB/transport/replay boundaries | PASS for fixture scope | Single 0002 migration now has started-only inserts, one terminal transition, immutable audit objects, composite scope/head checks and paired-Nasdaq head gate. Capture requires network/raw/retention/derived permissions; replay requires raw/retention/derived permissions. Parser artifact registry binds the recorded version/hash and fails closed when unavailable. |
| Live SEC/Nasdaq capture and offline replay | `BLOCKED_POLICY / NOT VERIFIED` | No license evidence has marked required uses `ALLOWED`; no external request was made in this remediation. Fixture success does not replace design §7 live acceptance. |
| Provider/license/timestamp/PIT | `NOT VERIFIED` | No provider state elevated and `available_at_validated` remains null. |
| Independent Phase 2 post-validation | `REVIEW_REQUIRED` | The prior Sol review failed. A new independent fresh-DB revalidation is required; do not claim `PASS_ENGINEERING_P2_FORWARD_CAPTURE`. |

Production remains `NOT PRODUCTION READY`; historical universe remains `NOT RELIABLY BACKTESTABLE`; risk budget remains `RISK BUDGET NOT APPROVED`; model/OOS/shadow remain `NOT VERIFIED`.

## RESEARCH-RISK-EDITOR-V1 S1–S3 correction evidence (2026-09-10)

| Check | Status | Evidence / limitation |
|---|---|---|
| Closed grammar / diagnostics / declarations / verifier | PASS for isolated SQLite/API fixture scope | `uv run pytest -q --tb=line tests/test_risk_editor.py tests/test_risk_editor_independent_review.py`: **51 passed, 2 warnings**. The retained independent reviewer file hash remains `EF9E02011A3B66249B84CFC0BD5654E5A3571CCC314D8E4E21C40143C2AB799B`. |
| Phase 1 regression | PASS | `uv run pytest -q --tb=line tests/test_phase1.py`: **8 passed, 2 warnings**. A deliberate stale mandate/risk pairing remains a preflight 422 rather than editor storage corruption. |
| Phase 2 regression | PASS | Isolated hidden-process run of `uv run pytest -q --tb=line tests/test_phase2.py`: **52 passed, 1 skipped, 2 warnings**. The skip is the existing host-denied Windows symlink limitation. |
| Startup / compile / whitespace | PASS | `uv run python -m py_compile` over editor/models/service/app/cli/phase2/migration/tests; `uv run python scripts/verify_startup.py --root .`; `git diff --check`. Startup remained main/UNBORN, dirty, structural-only and `NOT PRODUCTION READY`. |
| Full suite | PASS for current local engineering scope | Hidden-process `uv run pytest -q --tb=line`: **123 passed, 2 skipped, 2 warnings in 49.46s**. Skips remain host-denied Windows symlink limitations. |
| Browser / independent post-validation | NOT VERIFIED | Browser desktop/mobile edit/clear/preview/save/reload/history/stale/XSS and blocked-provider interaction still require a real available browser session and Sol independent post-validation. |

The correction does not establish feasibility, impact, calibration, `U_risk`, `S_stress`, provider/PIT, OOS, shadow, personal suitability, approval or Production readiness. All relevant statuses remain `NOT VERIFIED`, `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED`, and `NOT PRODUCTION READY`.

## PHASE2 review-fix loop (2026-09-09)

`uv run python -m py_compile optivest\\phase2.py alembic\\versions\\0002_phase2.py optivest\\app.py` and `uv run pytest -q` passed: 53 passed, 2 skipped, 2 upstream warnings. `git diff --check` passed. The remediation keeps license/PIT/Production states unchanged; a further independent Sol validation is required before an engineering PASS claim.

## PHASE2 final seven-defect correction loop (2026-09-09)

| Check | Status | Evidence / limitation |
|---|---|---|
| Full regression suite | PASS for current engineering scope | `uv run pytest -q`: **60 passed, 2 skipped**, 2 upstream TestClient/AnyIO deprecation warnings. The two skips are host-denied symlink fixtures, not an inferred pass. |
| Seven direct regressions | PASS for fixture/SQLite scope | Covers explicit Nasdaq common-stock evidence and non-common/ambiguous review; exact parser version/name/hash; `usable_at`; RFC HTTP-date retry and redirect limit; STARTED/zero-part head; display denial; and missing matrix startup failure. |
| Compile / whitespace | PASS | `python -m py_compile optivest\\phase2.py optivest\\app.py alembic\\versions\\0002_phase2.py`; `git diff --check`. |
| Fresh migration/reseed/verify | PASS, SQLite only | Fresh temp DB: `upgrade head -> seed -> downgrade 0001_phase1 -> upgrade head -> reseed -> verify_phase2`; schema/seed/raw integrity true at `0002_phase2`. |
| Policy identity | PASS | Raw-byte SHA-256 unchanged: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`. |
| Independent post-validation | `REVIEW_REQUIRED` | Terra evidence only; Sol must independently recheck before engineering acceptance. |

No live capture, permission elevation, provider/PIT validation, model/OOS/shadow validation, Production action, or investment-semantic change occurred.

## PHASE2 final three-open-finding correction (2026-09-09)

| Check | Status | Evidence / limitation |
|---|---|---|
| SEC filing-header/XBRL evidence parts | PASS for offline fixture scope | Separate parsers preserve raw-linked accession, filing/header and XBRL frame/context/unit fields; submissions continue to state `NOT_IN_SUBMISSIONS_PAYLOAD`. No row is decision-eligible and no external request occurred. |
| Canonical publication time | PASS for SQLite fixture scope | A deterministic-clock regression proves exact equality of new-snapshot `usable_at`, staged event times, terminal `response_completed_at`, run-result `created_at` and head `updated_at`; source rows exist before the timestamp is assigned. |
| Exact trusted declaration verification/startup | PASS for fixture scope | Verification derives current parser artifact hashes and rejects a same-name declaration with a fake endpoint; app startup fails closed. |
| Full regression suite | PASS for current engineering scope | `uv run pytest -q`: **64 passed, 2 skipped, 2 upstream warnings**. Skips are host-denied symlink tests, not passed coverage. |
| Compile / whitespace | PASS | `uv run python -m py_compile optivest\\phase2.py optivest\\app.py optivest\\cli.py tests\\test_phase2.py`; `git diff --check`. |
| Fresh migration/reseed/verify | PASS, SQLite only | Fresh isolated database: `upgrade head -> downgrade 0001_phase1 -> upgrade head -> seed-phase2-public-evidence -> verify-phase2`; revision `0002_phase2`, `seed_state=true`, `raw_integrity=true`. |
| Independent post-validation | `REVIEW_REQUIRED` | Terra evidence only. Sol must independently revalidate before any Phase 2 engineering PASS claim. |

All provider/license/timestamp/PIT, historical-universe, investment-model, OOS, shadow and Production limitations remain unchanged. Bounded live capture remains `BLOCKED_POLICY / NOT VERIFIED`.

## PHASE2 exact trusted-declaration verification correction (2026-09-09)

| Check | Status | Evidence / limitation |
|---|---|---|
| Exact frozen declaration gate | PASS for SQLite fixture scope | Shared seed/verifier declaration contract compares all provider, license, dataset and seven-permission values, including authority tier, artifact/reviewer, rate policy, status and duty. |
| Tamper regressions | PASS for fixture scope | Six raw-SQL mutations each set `seed_state=false`, cause nonzero `verify-phase2` CLI exit, and reject app startup. |
| Focused/full regression | PASS for current engineering scope | `uv run pytest tests\\test_phase2.py -q`: 50 passed, 1 skipped; `uv run pytest -q`: 70 passed, 2 skipped. Both had two upstream deprecation warnings; skips are Windows host-denied symlink fixtures. |
| Compile / whitespace | PASS | `uv run python -m py_compile optivest\\phase2.py optivest\\app.py optivest\\cli.py tests\\test_phase2.py alembic\\versions\\0002_phase2.py`; `git diff --check`. |
| Fresh migration/reseed/verify | PASS, SQLite only | Fresh `upgrade head -> downgrade 0001_phase1 -> upgrade head -> seed -> verify` returned exact `0002_phase2`, `seed_state=true`, `raw_integrity=true`, two datasets, and no captures. |
| Independent post-validation | `REVIEW_REQUIRED` | Terra evidence only; Sol must independently revalidate before any Phase 2 engineering PASS claim. |

No provider/PIT, live capture, historical-universe, investment-model, OOS, shadow or Production claim changed. Required use permissions remain `NOT VERIFIED`; bounded live capture remains `BLOCKED_POLICY`; Production remains `NOT PRODUCTION READY`.

## PHASE2 independent offline acceptance (2026-09-09)

| Check | Status | Evidence / limitation |
|---|---|---|
| Independent defect closure | `PASS_ENGINEERING_P2_OFFLINE` | Sol independently re-ran fresh-DB/raw-SQL/HTTP/parser/API/CLI/UI probes and the final trusted-declaration forgery. See `docs/reviews/phase2_remediation_validation.md`. |
| Parent full regression | PASS | `uv run pytest -q`: **70 passed, 2 skipped, 2 upstream warnings**; compile and `git diff --check` PASS. |
| Startup integrity | PASS, structural only | `uv run python scripts/verify_startup.py --root .`: no findings, main/UNBORN, dirty tree reported, Production denied. |
| Bounded official capture/replay | `BLOCKED_POLICY / NOT VERIFIED` | Required license permissions remain `NOT_VERIFIED`; no live request was made. Frozen design section 7 item 11 and full Phase 2 implementation acceptance remain incomplete. |

Provider/license/timestamp/PIT, historical universe, investment-model, OOS, shadow and Production remain unverified. The two skipped symlink fixtures are host-capability limitations, not passed coverage.

## UNVERIFIED_USER_DIRECTED_CAPTURE Nasdaq trailer compatibility (2026-09-09)

| Check | Status | Evidence / limitation |
|---|---|---|
| Offline raw parsing | PASS, parser only | User-directed local captures only: `nasdaqlisted.txt` SHA-256 `31A17FF730E8E42753E45051AC44732A3790FF36ED0A03ADF32F0170A211A2E4`, 5,592 rows (3,002 `ELIGIBLE_FOR_REVIEW`, 2,590 `REVIEW_REQUIRED`); `otherlisted.txt` SHA-256 `4F5AE4F711AFD0E39A75F07393C84C8F549DD98CF58A76459F0DD26A9ED02CE6`, 7,597 rows (1,732 `ELIGIBLE_FOR_REVIEW`, 5,865 `REVIEW_REQUIRED`). Both trailers preserve `0908202621:31` text. |
| Exact trailer regressions | PASS | Listed accepts the exact first timestamp plus seven empty fields; otherlisted accepts its observed first timestamp plus six empty fields. Both reject a nonempty trailing field. |
| Capture status | `UNVERIFIED_USER_DIRECTED_CAPTURE / NOT VERIFIED` | Parent retrieval recorded HTTP 200, request/response UTC instants, byte/line counts, hashes and source trailers in `data/unverified_nasdaq_capture_2026-09-09/CAPTURE_MANIFEST.md`. Raw files remain outside the trusted DB; license/provider/PIT states did not change. The observed `Exchange=M` row remains `REVIEW_REQUIRED`. |
| Regression / static checks | PASS | `uv run pytest tests\\test_phase2.py -q`: 52 passed, 1 skipped, 2 upstream warnings; `uv run pytest tests\\test_phase1.py -q`: 8 passed, 2 warnings; `uv run pytest tests\\test_verify_startup.py -q`: 12 passed, 1 skipped. This covers the full 74-test suite in bounded commands (72 passed, 2 skipped). `uv run python -m py_compile optivest\\phase2.py tests\\test_phase2.py` and `git diff --check`: PASS. |
| Independent real-data parser review | PASS, scoped | Sol reproduced both hashes, row/state counts and trailers; nonempty trailer fields failed; `Exchange=M` remained review-only. This does not validate provider permission or PIT. |

## RESEARCH-RISK-EDITOR-V1 Terra checkpoint (2026-09-09)

| Check | Result | Limit |
|---|---|---|
| Isolated editor migration/seed/verifier | PASS | Fresh temporary SQLite reached `0003_research_risk_editor`; no user DB touched. |
| Editor focused API/DB tests | PASS | `uv run pytest tests/test_risk_editor.py -q`: 2 passed; exercises strict duplicate key, template preview/save, version history and immutable document trigger. |
| Existing regressions | PASS | `tests/test_phase1.py`: 8 passed; `tests/test_phase2.py`: 52 passed, 1 skipped; `tests/test_verify_startup.py`: 12 passed, 1 skipped. |
| Static/startup | PASS | `py_compile`, `git diff --check`, and `uv run python scripts/verify_startup.py --root .` passed. |
| ADR-0017 engineering acceptance | REVIEW_REQUIRED | Terra-only evidence. Sol must independently validate every frozen section 11 acceptance item before any PASS_ENGINEERING claim. |

No numerical feasibility, impact, risk calibration, provider/PIT, OOS/shadow or Production gate was validated. `RISK BUDGET NOT APPROVED` and `NOT PRODUCTION READY` remain unchanged.

## RESEARCH-RISK-EDITOR-V1 review-fix result (2026-09-09)

`uv run pytest -q tests/test_risk_editor_independent_review.py --tb=short`: **29 passed**, two upstream TestClient warnings. The independent suite is retained unchanged and exercises canonical decimals, nested schema matrix, verifier corruption, status/preflight fail-closed behavior, public error contracts, concurrency mapping, canonical ordering, CLI serialization and editor controls. Sol independent recheck remains required before engineering acceptance.

## RESEARCH-RISK-EDITOR-V1 second bounded correction (2026-09-09)

`uv run pytest -q tests/test_risk_editor.py tests/test_risk_editor_independent_review.py --tb=short`: **40 passed**, two upstream warnings. Nine new permanent preview negatives cover selected-mode, epsilon, stress, hybrid, joint, row-16, component and typed-text failures. This is Terra evidence only; all validation/approval/readiness limitations remain unchanged.

## RESEARCH-RISK-EDITOR-V1 independent post-validation (2026-09-09)

| Check | Result | Evidence / limitation |
|---|---|---|
| Frozen design/Policy identity | PASS | Policy `ACF013...E67`; ADR-0017 design `F9EC...B950`; accepted pre-review `EA061...CF7`. |
| Implementer/pre-existing regression | PASS for prior coverage only | `uv run pytest -q tests/test_risk_editor.py tests/test_phase1.py tests/test_phase2.py tests/test_verify_startup.py`: **74 passed, 2 skipped, 2 warnings**. |
| Independent ADR-0017 tests | **FAIL** | `uv run pytest -q --tb=line tests/test_risk_editor_independent_review.py`: **27 failed, 2 passed**. Decimal values 10/30/100 became 1/3/1; forbidden nested declarations saved; evaluator/change/error/verifier/preflight/API/CLI/UI contracts failed. |
| Full regression with reviewer tests | **FAIL** | `uv run pytest -q --tb=no`: **27 failed, 76 passed, 2 skipped, 2 warnings**. |
| Storage corruption/fail-closed | **FAIL** | Exact verifier accepted projection drift and forged historical APPROVED envelope; nonhex digest passed DB CHECK; status swallowed digest corruption; preflight inserted a snapshot on corrupt current editor storage. |
| Transaction/transition positives | PARTIAL | Projection fault rolled back row/head; all four nominal legacy/V1 transitions ran; isolated populated 0003→0002→0003 preserved 2 versions/38 constraints and reclassified them legacy. Wrong HTTP error mapping and incomplete legacy verification remain blocking. |
| Compile/startup/whitespace | PASS, structural only | `py_compile`, `scripts/verify_startup.py --root .`, and `git diff --check` passed. Startup checker explicitly does not validate investment/model/OOS/shadow evidence; all files are untracked. |
| Browser | `NOT VERIFIED` | Isolated local HTTP/API route ran, but browser discovery returned no connected backend; desktop/mobile interaction was not claimed. Static page has zero row edit inputs and lacks required history/component forms. |
| Independent verdict | **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`** | Report `docs/reviews/research_risk_editor_post_review.md` SHA-256 `F0F13F4BCCECCBB56392CD32A55B41201AC765C12DD81CD0B88D4336D3513793`; reviewer tests `EF9E...799B`. Do not set editor engineering PASS. |

This is editor implementation conformance only, not numerical feasibility/calibration or model validation. `RISK BUDGET NOT APPROVED`, `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain unchanged. The two skips remain host-denied Windows symlink limitations.

## RESEARCH-RISK-EDITOR-V1 final independent correction recheck (2026-09-09)

| Check | Result | Evidence / limitation |
|---|---|---|
| Retained reviewer test identity/result | PASS for its encoded cases | File unchanged at `EF9E...799B`; `uv run pytest -q --tb=line tests/test_risk_editor_independent_review.py`: **29 passed**, 2 warnings. |
| Focused editor tests | PASS for encoded cases | `uv run pytest -q tests/test_risk_editor.py tests/test_risk_editor_independent_review.py`: **31 passed**, 2 warnings. |
| Full suite | PASS for encoded cases | `uv run pytest -q`: **103 passed, 2 skipped**, 2 warnings. Skips remain host-denied Windows symlink limitations. |
| Additional frozen schema/mode matrix | **FAIL** | Nine invalid candidates all returned preview 200: forbidden/incomplete Risk modes, epsilon 2, unknown Stress role, Hybrid participation 101, invalid Joint members, row-16 parent horizon, invalid component unit and numeric `M<string>`. |
| Fresh populated migration | PARTIAL | Isolated 0003→0002→0003 preserved 2 budgets/38 constraints and reclassified current as legacy. Document FK still targets budget, timestamp checks are absent. |
| Corruption/all-history verifier | **FAIL** | Unknown legacy metric + root revision 99 + missing trigger returned VALID. V1 envelope missing `created_at` with unknown server field and recomputed digest returned VALID. |
| Two-head/fault atomicity | PARTIAL | Risk/mandate races, marker failure, response serialization failure and SQLite lock all preserve atomicity. Stale head responses are 409 but code is `INTERNAL_ERROR`, not `HEAD_CONFLICT`; preview snapshot contract remains absent. |
| API/CLI/UI/browser | **FAIL / browser NOT VERIFIED** | API/CLI conflict codes diverge. Static local page has 21 inputs but no input reads/change handlers/history GET. Isolated server starts; browser backend list is empty, so desktop/mobile interaction is not claimed. |
| Compile/startup/whitespace | PASS, structural only | `py_compile`, startup checker and `git diff --check` pass; startup checker explicitly excludes investment/model/OOS/shadow validation. |
| Final verdict | **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`** | Updated report `docs/reviews/research_risk_editor_post_review.md` SHA-256 `2D3DFE96CABF9308D09E8DA6B5D1B71227CE684E1BF169CEE7001B4A38DCD54F`. No editor engineering PASS. |

B3 is closed for the tested raw decoder/HTTP boundary. B1, B2, B4, B5 and B8 remain blocking; B6 and B7 remain partial/blocking. This remains implementation-conformance evidence only. No numerical feasibility/calibration, provider/PIT, model/OOS/shadow or Production status changed.

## RESEARCH-RISK-EDITOR-V1 second-correction independent recheck (2026-09-10)

| Check | Result | Evidence / limitation |
|---|---|---|
| Retained reviewer suite | PASS for encoded cases | Unchanged SHA-256 `EF9E...799B`; **29 passed**, 2 warnings in 26.97s. |
| Permanent nine-case correction suite | PASS for encoded cases | `tests/test_risk_editor.py`: **11 passed**, including 422 for all nine previous HTTP-200 cases. |
| Full regression | PASS for encoded cases | **112 passed, 2 skipped**, 2 warnings in 60.60s. Skips remain host-denied symlink limitations. |
| Transaction/CAS/preview | PASS for exercised contract | Two concurrent heads: one 201/one 409 `HEAD_CONFLICT`; moved mandate 409 `HEAD_CONFLICT`; observed preview heads exact; marker and serialization faults fully roll back; retained busy case is `WRITE_CONFLICT`. |
| Populated migration | PASS nominally | Fresh isolated 0003→0002→0003 preserved 2 budgets/38 constraints/1 `NOT_VERIFIED` provider; editor tables dropped/recreated; current reclassified `LEGACY_NOT_VERIFIED`. |
| Exact verifier | **FAIL** | Legacy `UNKNOWN_METRIC`, same-name no-op trigger, and rehashed historical V1 missing `created_at` plus unknown key all returned VALID. Corrupt historical DB served status/current/history and inserted preflight. Root revision and digest mismatch now reject. |
| Remaining frozen grammar/evaluator/diffs | **FAIL** | Wrong row/component clocks, invalid currency applicability, blank/numeric text, duplicate/cross-group Joint references and unsorted members accepted. Selected incomplete findings absent. `>=`, minimum and identity-aware comparisons incorrect. |
| API/CLI/provider boundary | PARTIAL | API valid/CAS paths and disposable CLI show/preview/save/verify pass. With `NOT_VERIFIED` provider permissions, editor/preview remain 200 while home/datasets remain 403. Corruption serving remains fail-open. |
| UI/browser | **FAIL / blocking NOT VERIFIED** | Static editor wires only row limits; components and required declaration/diagnostic state are absent. In-app browser list `[]`; frozen §11 item 9 mandatory desktop/mobile interaction not performed. |
| Compile/startup/diff | PASS, structural only | `py_compile`, startup checker (`findings=[]`, `NOT PRODUCTION READY`) and `git diff --check` pass; main/UNBORN, all repository entries untracked. |
| Verdict | **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`** | Report SHA-256 `BA1FA18499BE421C77FDB8EEABB9DDEBAD87873928949B939C1F73BDA30F8368`; do not set editor engineering PASS. |

B3 and the independently exercised B6 transaction contract are closed. B1, B2, B4, B5 and B8 remain open/blocking; B7 remains partial/blocking. No feasibility, impact, calibration, provider/PIT, OOS, shadow or Production claim was validated.

## RESEARCH-RISK-EDITOR-V1 final non-browser Terra correction (2026-09-10)

| Check | Result | Limit |
|---|---|---|
| Editor + retained independent suite | PASS | `pytest -q tests/test_risk_editor.py tests/test_risk_editor_independent_review.py`: **49 passed**, 1 upstream warning. |
| Existing Phase 1/2 regression group | PASS | `pytest -q tests/test_phase1.py tests/test_phase2.py`: **60 passed, 1 skipped**, 1 upstream warning. |
| Fresh migration/verifier | PASS | Temporary SQLite V1 `upgrade -> seed -> verify -> downgrade -> upgrade -> verify`; both verifier calls `VALID`. |
| Compile/startup/whitespace | PASS | `python -m compileall -q optivest`; startup checker PASS (`NOT PRODUCTION READY`); `git diff --check` PASS. |
| Monolithic full suite | NOT COMPLETED | Reached 58% twice but no final result in the desktop 30-second command window. |

Terra-only correction evidence; Sol browser/review recheck remains required. No readiness, approval, calibration, feasibility, provider/PIT or model-validation status changed.

## RESEARCH-RISK-EDITOR-V1 third-correction Sol revalidation (2026-09-10)

| Check | Result | Evidence / limitation |
|---|---|---|
| Retained + implementer editor suites | PASS for encoded cases | Independent file unchanged at `EF9E...799B`; combined **51 passed**, 2 warnings. |
| Full regression | PASS for encoded cases | **123 passed, 2 skipped**, 2 warnings in 49.18s; skips are host-denied symlink cases. |
| Grammar/raw/API/evaluator | **FAIL / BLOCKING** | Positive/range/applicability/trimming/request-type cases accepted; bad UTF-8 code wrong; Joint contradiction missed; blocker findings and catalog ordering incomplete. |
| CLI/migration roundtrip | **FAIL / BLOCKING** | CLI show/preview/save/verify passes before downgrade; populated 0003→0002→0003 preserves 2/38/2 rows but re-upgrade verifier rejects preserved V1 `>=` comparators as invalid legacy. |
| Exact schema/all-history serving | **FAIL / BLOCKING** | Rehashed unsorted historical array, extra marker column and historical `LEVERAGE=1` contradiction all return verifier VALID; corrupted history allows startup/status/history/preflight insertion. |
| Transaction/read snapshot | PARTIAL / BLOCKING | Exercised write CAS/fault/busy behavior passes; successful preview executes 19 SQL statements with no explicit BEGIN. |
| Actual browser/UI | **FAIL / BLOCKING** | Desktop/mobile edit/clear/preview/save/reload/history/stale/XSS mechanics pass on isolated blocked-provider DB. Served UI is a raw textarea, not frozen structured row/component forms; row-16 aggregate remains editable. |
| Compile/startup/diff | PASS, structural only | `py_compile`, startup checker and tracked `git diff --check` pass; main/UNBORN and all project entries untracked. |
| Final verdict | **`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`** | No editor engineering PASS; exact 11-item matrix is in the post-review. |

No numerical feasibility/impact/calibration, provider/PIT, model/OOS/shadow or Production gate changed. `RISK BUDGET NOT APPROVED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain.
