# PHASE0-GIT-IDENTITY-V2 independent post-implementation review

Date: 2026-09-21, Asia/Tokyo. Reviewer: GPT-5.6 Sol. Method: independent falsification-first inspection and disposable-repository reproduction. This is the controlling post-implementation review for ADR-0019.

## Final alternate-token-trigger recheck

Prior complete review identity: SHA-256 `5F01878CCF140811EA7723EFB1E175D0A24558391314250E88BC9A1346F2B440`. Rechecked implementation SHA-256 `D411F2043716C08302170C962A480CD6BE3C86D1632FCEA96308C6AF9DEECF45`; permanent tests SHA-256 `641759C3FBA8E7936E69D119F33B8CDC9E03AB6652EADB6BCDF6486504D43953`.

### Final verdict

**`PASS_ENGINEERING_PHASE0_GIT_IDENTITY`**

B1-B4 and F1-F3 are closed for the exact ADR-0019 structural engineering scope. The initial commit and push sequence is technically unblocked by Phase-0 Git-identity validation, but neither operation was performed in this review.

The final correction resolves both `GIT_TOKEN` triggers before later tree semantics: the valid worktree candidate and the committed START blob. Only after a valid committed token are `GIT_TREE`, `GIT_CASE_COLLISION`, `GIT_START_ENTRY`, index, flags, worktree and digest rows evaluated. Expected missing/nonregular START blob-command failures remain classified by the already parsed tree, while unrelated Git-command failures remain table-first `GIT_COMMAND`.

### Independent final evidence

- A genuine disposable commit with a malformed committed START token and a separately injected malformed tree returned the sole exact `GIT_TOKEN` report. Branch/HEAD and Policy hash were populated; recorded/state/dirty fields were null; the snapshot was unchanged.
- An independent 18-case matrix combined six committed-blob token failures—missing machine token, duplicate token, BOM, CRLF, NUL and invalid UTF-8—with each of malformed tree, ASCII case collision and executable START. Every case returned sole exact `GIT_TOKEN`, the same complete observed/null and denial report, no injected bytes leaked, and every worktree plus `.git` snapshot was unchanged.
- Genuine collision pairs remained correct. Case/case combined with missing, `100755 blob`, `120000 blob` and proper `160000 commit` START entries returned sole exact `GIT_CASE_COLLISION`. Recorded fields were populated only where the preceding committed blob token was successfully established; expected blob-failure paths retained null recorded fields. All snapshots were unchanged.
- Candidate-versus-blob trigger accounting is explicit through `token_source` and `token_applied`. The 12-row/66-pair matrix retains the candidate route and asserts every named fault was applied. Separate permanent tests cover an actual committed malformed-token commit and all six blob variants against all three later tree rows.
- Previously closed counterexamples remained closed: committed `HEAD` exit-zero/nonzero stderr, failed `cat-file` plus invalid candidate token and later whole-status failure against root/object-format/branch all returned exact non-leaking `GIT_COMMAND`; actual missing/executable START classifications remained stable.
- B1/B2/F1/F2 nonregression passed independently: raw normalized state matched; content-identical/autocrlf passed; later content drift failed with digest mismatch; all eight assume/skip/fsmonitor combinations retained frozen behavior; portable path cases passed.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v`: **29 passed, 1 skipped** in **138.597s**. The single skip is the host-denied Windows symlink-creation fixture; symlink tree semantics were separately exercised by raw tree evidence.
- Terra full regression evidence: `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **228 passed, 2 skipped, 2 warnings, 174 subtests passed**. Sol did not repeat the full suite because the focused suite, separate probes and current hashes directly cover the residual correction.
- Compileall, structural startup, `git diff --check` and explicit verifier/test trailing-whitespace scan passed. Startup remained structural PASS on `main / UNBORN`, 78 untracked paths, and `NOT PRODUCTION READY`.

### Scope and boundaries

This verdict establishes only the frozen PHASE0-GIT-IDENTITY-V2 structural engineering contract. It does not validate investment logic, provider/PIT quality, model calibration, risk feasibility, OOS, shadow, deployment or Production readiness. `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain unchanged. No Policy/design/ADR/application/database/model/provider/risk/wealth/return-bridge/trial artifact changed in this review, and no commit or push was performed.

## Final residual recheck after collision/START correction

Prior complete review identity: SHA-256 `DA717DC223D70CDD9DF05CBCDBCE5AABDD29F7C0CC17A029C02B8D50BF2ABCFC`. Rechecked implementation SHA-256 `0ED13A57DA47F4D20FB0656C291CB531B210CFD2721CE3A4DB294D4D019E3536`; permanent tests SHA-256 `4FB0EFA8579D85FF2B3A17D33A43A23EBE83DC31129E9D30C68DFB7F9D1CBA26`.

### Residual recheck verdict

**`REVIEW_REQUIRED`**

The requested collision/START correction itself works. Independent raw-tree probes combined `Case.txt`/`case.txt` with each of a missing START entry, `100755 blob`, `120000 blob`, and a proper `160000 commit` START entry. Every probe returned the sole exact `GIT_CASE_COLLISION` finding, retained branch/HEAD and Policy hash with all later observed fields null, leaked no source bytes, and preserved the full worktree plus `.git` snapshot.

The revised permanent helper now composes same-tree mutations before returning and records every applied named fault. Its assertion `faults == applied` prevents the prior advertised-but-not-applied pair. The dedicated collision/executable-START test compares the complete report and snapshot. This closes the prior 65/66 fixture defect.

However, the correction introduced a different direct frozen-order failure. `_check_state_git` now emits `GIT_TREE` for `entries is None` before validating the committed blob token. In an independent disposable committed repository, `ls-tree` was replaced by a malformed NUL-terminated tree and the successful `cat-file` output was replaced by a malformed committed START blob with no machine token. Frozen revision 4 orders `GIT_TOKEN` before `GIT_TREE`. Expected was sole exact `GIT_TOKEN`; actual was sole exact `GIT_TREE`, exit 1, with branch/HEAD and Policy hash populated, recorded/state/dirty fields null, and an unchanged repository snapshot.

The 66-pair helper cannot detect this because its `GIT_TOKEN` fixture only overwrites `recorded_head_candidate` from the worktree parse. It does not instantiate the distinct frozen `GIT_TOKEN` condition produced by malformed committed blob bytes. The new `applied` assertion proves the selected proxy was applied, not that every triggering condition for that table row is covered. The same reordering also changed the single `GIT_TREE` complete-report oracle from the previously established recorded values to null; that broader report change was not required to make collision precede START validity.

### Residual independent evidence

- Requested genuine collision/START probes: missing, executable, symlink and gitlink START variants all returned exact `GIT_CASE_COLLISION`; snapshots unchanged.
- New genuine malformed-blob-token plus malformed-tree probe: expected `GIT_TOKEN`, actual `GIT_TREE`; snapshot unchanged and no injected bytes leaked.
- Previously closed blockers remained closed in the independent probe: committed `HEAD` exit-zero/nonzero stderr, failed `cat-file` plus invalid worktree token, and later whole-status failure against root/object-format/branch all returned non-leaking `GIT_COMMAND`; actual missing/executable START entries retained `GIT_START_ENTRY`.
- B1/B2/F1/F2 nonregression remained positive: independent digest matched, content-identical/autocrlf passed, later drift failed, all eight hidden-index combinations behaved as frozen, and portable path cases passed.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v`: **27 passed, 1 skipped** in **124.311s**. The host-denied symlink test is the one skip. The green matrix does not contain the malformed committed-token/tree pair.
- Terra full evidence remains **226 passed, 2 skipped, 2 warnings, 156 subtests**; it was not rerun because the direct frozen-contract counterexample is dispositive.
- Compileall, structural startup, `git diff --check`, and explicit verifier/test trailing-whitespace scan passed. Startup remained structural PASS on `main / UNBORN`, 78 untracked paths, with `NOT PRODUCTION READY`.

### Next bounded correction

1. Preserve the now-correct collision-before-missing/wrong/nonregular-START behavior, but restore complete `GIT_TOKEN` precedence over `GIT_TREE` for malformed committed blob-token conditions.
2. Add a genuine composed malformed committed-token blob plus malformed-tree fixture with the exact sole `GIT_TOKEN` full report and byte snapshot. Retain the worktree-candidate token pairs as a separate path.
3. Restore/freeze the exact single-row `GIT_TREE` observed-value contract consistently with the frozen safely-established rule and prior accepted oracle; do not silently redefine other report rows.
4. Preserve every previously closed command/stderr/missing-entry/B1/B2/F1/F2 behavior, rerun focused/full/static checks, and return for independent Sol review before engineering PASS, commit or push.

No `PASS_ENGINEERING_PHASE0_GIT_IDENTITY`, initial commit or push is authorized. `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain unchanged.

## Final independent recheck after residual Terra correction

Prior complete review identity: SHA-256 `FE613453AE10D5EFC2081A29C6CA98569DAEF78F8BD4F8991E956D3A05A44ABC`. Rechecked implementation SHA-256 `AB3CC7A7EEB278AD7B02A58733BFD7E2DC83897329345B754B65FB1C5B57995C`; permanent tests SHA-256 `87209E30F55EABDAC372ACA2F67E61FC84069FD355F1DCE63D5A528111B16DF7`.

### Final recheck verdict

**`REVIEW_REQUIRED`**

The previously open committed-HEAD stderr, missing START entry and global later-command precedence counterexamples are corrected. Independent probes returned sole exact `GIT_COMMAND` for committed `HEAD` exit-zero/stderr and nonzero/stderr, failed `cat-file` plus invalid token, and later whole-status command failure paired with root/object-format/branch faults. Actual missing and executable committed START entries returned exact `GIT_START_ENTRY`. Output did not leak injected bytes and every disposable repository snapshot was unchanged.

One new direct F3/B3 precedence deviation remains, and it exposes an F3/B4 defect in the permanent 66-pair oracle. A valid committed tree was independently transformed to contain both a portable ASCII case collision (`Case.txt` and `case.txt`) and a `100755 blob` START_HERE entry. Frozen revision 4 orders `GIT_CASE_COLLISION` before `GIT_START_ENTRY`; expected was the sole exact `GIT_CASE_COLLISION`, but actual was the sole exact `GIT_START_ENTRY`. In `scripts/verify_startup.py`, `_check_state_git` tests `not valid_start_entry` before testing `collision`.

The permanent test named `test_rev4_complete_exact_fault_and_pair_matrix_is_readonly` enumerates all 12 rows and all 66 `combinations(rows, 2)`, compares complete top-level JSON/null/denial/exit semantics and snapshots all worktree plus `.git` files. However, its injection helper returns the collision rewrite before applying the START-mode rewrite when both faults are requested. Thus the `GIT_CASE_COLLISION`/`GIT_START_ENTRY` subtest instantiates only the earlier collision and cannot detect the real simultaneous-fault ordering defect. The other independently combined pairs matched the frozen first-fault row.

### Final independent evidence

- Separate normalized raw-byte state calculation matched the verifier; content-identical commit passed and later payload drift returned `GIT_STATE_DIGEST_MISMATCH`.
- Fresh `core.autocrlf=true` clone passed with CRLF worktree and LF committed blob.
- All eight assume-unchanged/skip-worktree/fsmonitor combinations reproduced `H/H/H`, `H/H/h`, `S/S/S`, `S/S/s`, `h/H/H`, `h/H/h`, `s/S/S`, `s/S/s`; only the unflagged row passed and every snapshot was unchanged.
- The permanent suite does instantiate exact complete reports for each of the 12 individual rows, enumerates 66 nominal pairs, covers committed and UNBORN applicable exit-zero/nonzero stderr reads, malformed/truncated binary streams, no-leak assertions and byte snapshots. Its single combined-tree-fixture omission above keeps B4/F3 open.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v`: **26 passed, 1 skipped** in **122.406s**. The skip is the host-denied Windows symlink fixture. This green result includes the false-negative pair subtest and does not override the counterexample.
- Independent final probe: all 12 single rows exact; **65 of 66 genuine combined pairs exact**, with only `GIT_CASE_COLLISION` + `GIT_START_ENTRY` mismatching; all previously open blocker probes, B1/B2/F1/F2 probes, non-leak checks and snapshots passed.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests`, structural startup, and `git diff --check`: exit 0. Startup was structural PASS on `main / UNBORN`, 78 untracked paths, with `NOT PRODUCTION READY`.

### Residual bounded correction

1. In `_check_state_git`, enforce the frozen semantic order so `GIT_CASE_COLLISION` precedes `GIT_START_ENTRY` after token validation.
2. Make the permanent pair harness apply both tree mutations for the collision/START pair, retain the complete exact JSON and byte snapshots, and add a direct assertion for that combined fixture.
3. Preserve all corrected command/stderr/missing-entry behavior and B1/B2/F1/F2. Rerun focused/full/compile/startup/whitespace and one final independent Sol recheck before any engineering PASS, initial commit or push.

No `PASS_ENGINEERING_PHASE0_GIT_IDENTITY`, initial commit or push is authorized. This remains a narrow structural engineering review. `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain unchanged.

## Independent recheck after bounded Terra review-fix

Prior complete review identity: SHA-256 `6EFE50E741928633061D2D963235C111FC8FE94185907675F151849E4550B9B3`. Rechecked implementation SHA-256 `A57762B8B9E76F17F013711612A151F37B6AF3F50AE8FA65EF5C31565C6FAB2B`; permanent tests SHA-256 `773C7F18278F64C2F44F2E1D135C52657B18C3CA8B03CAA79447FCB1B17E170E`.

### Recheck verdict

**`REVIEW_REQUIRED`**

The prior failed-`cat-file` plus invalid-token counterexample is corrected: the verifier now returns only exact `GIT_COMMAND`, leaks no stderr bytes and preserves the disposable repository snapshot. Exit-zero/nonzero stderr on the eight committed-state reads added by Terra also fail closed. B1/B2/F1/F2 remain closed. However, independent probing found two remaining direct B3/F3 implementation deviations and B4 remains incomplete. Therefore no `PASS_ENGINEERING_PHASE0_GIT_IDENTITY`, initial commit or push is authorized.

### R1 - P1 - Committed `HEAD` command stderr is ignored

The verifier separately invokes `git rev-parse --verify --quiet HEAD` and `git rev-parse --verify --quiet HEAD^{commit}`. On a valid committed repository, when `HEAD^{commit}` succeeds, lines 485-491 use only the second command's result and do not examine `head_code` or `head_stderr`. The latter are checked only in the non-commit/UNBORN branch at lines 492-497.

Independent injection at the actual `HEAD` read produced both:

- exit 0, valid stdout and stderr `secret-stderr`; and
- exit 1, empty stdout and stderr `secret-stderr`.

In both cases verification returned no finding instead of table-first `GIT_COMMAND`. The repository byte snapshot was unchanged and the injected text did not leak, but fail-closed behavior was absent. Equivalent exit-zero/nonzero stderr injections at root, object-format, branch, `HEAD^{commit}`, tree, blob, stage, all three tags, scoped status and whole status correctly returned `GIT_COMMAND`; UNBORN HEAD/commit/show-ref stderr also failed closed. The permanent stderr matrix covers only state-path reads and does not include this committed-HEAD counterexample.

### R2 - P1 - A genuinely missing committed START_HERE is misclassified as `GIT_COMMAND`

Revision 4 maps a missing or non-regular committed START_HERE to exact `GIT_START_ENTRY`. The corrected verifier eagerly invokes `cat-file blob HEAD:.ai/START_HERE.md` and treats any nonzero blob result as `GIT_COMMAND` before parsing the tree. In an actual disposable commit with `.ai/START_HERE.md` removed, isolated state verification returned only `GIT_COMMAND`; expected is `GIT_START_ENTRY`. Wrong-mode `100755 blob` still returned `GIT_START_ENTRY`, confirming the defect is the missing/non-blob command-result path.

The correction must distinguish an expected missing/wrong-type path established by the valid tree from an unrelated Git command failure. It must not weaken the corrected failed-`cat-file` plus invalid-token precedence.

### R3 - P1 - Complete report and precedence acceptance remains non-permanent

The current permanent test still instantiates eight of the 12 single fault rows, compares findings and only the set of observed keys, and retains two original semantic pairs. The added correction test covers one prior command/token pair, stderr on eight state reads and one whole-status-command/tree pair. It does not freeze:

- exact complete JSON values/nulls for all 12 rows;
- committed root/object/branch/HEAD/commit and UNBORN ref stderr rows;
- the missing START entry path;
- all required earlier/later pairs, including later command failures against root/object-format/branch semantic faults; or
- byte snapshots for every complete report/pair fixture.

Independent 12-row injection produced the intended code/path/reason and read-only behavior for all synthetic rows. But a later whole-status command failure paired with root, object-format or branch mismatch returned respectively `GIT_ROOT`, `GIT_OBJECT_FORMAT` or `GIT_BRANCH`, not table-first `GIT_COMMAND`, because those earlier stages return before the later command is invoked. This is inconsistent with revision 4's unqualified table-order/all-pair requirement. If executing later reads after root mismatch is considered unsafe or unintended, that is a frozen-design conflict and requires `DESIGN CHANGE REQUIRED`; implementation/tests cannot silently narrow the pair contract.

### Recheck positive evidence

- Separate raw-byte digest matched verifier state; content-identical commit passed; later committed payload drift returned `GIT_STATE_DIGEST_MISMATCH`.
- Fresh autocrlf clone passed with CRLF worktree and LF committed blob.
- All eight assume/skip/fsmonitor combinations reproduced literal `H/H/H`, `H/H/h`, `S/S/S`, `S/S/s`, `h/H/H`, `h/H/h`, `s/S/S`, `s/S/s`; only normal passed and all snapshots were byte-identical.
- Independent synthetic fixtures emitted all 12 fixed code/path/reason rows without output leakage and preserved snapshots. This positive result does not cure the actual missing-entry misclassification or absent permanent complete-object matrix.
- Focused `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v`: **21 passed, 1 skipped** in 73.820s.
- Root-supervised full `uv --cache-dir .uv-cache run pytest -q --tb=line`: **220 passed, 2 skipped, 2 known dependency warnings, 33 subtests passed** in 195.05s. This is accepted as full-regression evidence but does not override reproduced counterexamples.

### Residual bounded correction

1. In committed mode, treat nonzero or stderr from both `HEAD` and `HEAD^{commit}` reads as exact non-leaking `GIT_COMMAND`; retain valid true-UNBORN handling.
2. Parse and classify the committed tree sufficiently to emit `GIT_START_ENTRY` for missing/wrong START entries before interpreting the expected `cat-file` failure, while retaining `GIT_COMMAND` for unrelated blob-command failure on a valid START entry and retaining token/table precedence.
3. Implement the complete permanent 12-row exact-report/null-value matrix, every frozen earlier/later pair, all command/stderr stages and byte snapshots. If global `GIT_COMMAND` precedence conflicts with safe root-first execution, stop for Astra `DESIGN CHANGE REQUIRED` rather than weakening revision 4.
4. Preserve B1/B2/F1/F2 and all non-production boundaries, rerun focused/full/compile/startup/whitespace, and require another independent Sol review before commit/push.

## Authority and reviewed bytes

- Selected Policy: `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.
- Frozen revision 2: `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C`.
- Frozen revision 3: `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D`.
- Frozen revision 4: `BDC2119A14D67D379A0E70EDB6B7E849C8C66ADF2432B62242C2037A61E94DC0`.
- Controlling pre-review: `EF09C8EF0B7B0685678012D05115882B7A8675E444F85AD625A8B7FEFD0F7B5C`.
- Decision authority: ADR-0019 / D0011 in `.ai/DECISIONS.md`.
- Reviewed implementation: `scripts/verify_startup.py`, SHA-256 `4A486D13DCA6CB77721277700B8EE6DCF3DCE7A832FE2E4F2C1446E843FA8B3E`.
- Reviewed permanent tests: `tests/test_verify_startup.py`, SHA-256 `502B413FBD44C42630A4BA31D08E98D01829E48625699705CCF26EE3158E5740`.
- Reviewed attributes: `.gitattributes`, SHA-256 `CA9B4F2186D45146F414E4C075054DE6AE1B8918944311D1A55C6689DCA2E91B`.

The repository remained `main / HEAD UNBORN`; no commit, remote or push operation was performed. The temporary independent probe and all disposable repositories were removed.

## Verdict

**`REVIEW_REQUIRED`**

Do not issue `PASS_ENGINEERING_PHASE0_GIT_IDENTITY`, create the initial commit or push. B1, B2, F1 and F2 are closed in the implementation evidence. B3, B4 and F3 remain blocking because the exact frozen command/fault precedence and mandatory permanent oracle matrix are not implemented.

This is a narrow structural engineering failure, not model validation. It changes no investment, provider, PIT, risk, wealth, return-bridge, OOS, shadow, approval or Production state. `RISK BUDGET NOT APPROVED`, applicable items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED` and `NOT PRODUCTION READY` remain.

## Blocking findings

### P1 - F3/B3 - A later Git-command failure loses to `GIT_TOKEN`, contrary to the frozen table order

Revision 4 makes `GIT_COMMAND` the first row, `GIT_TOKEN` the fifth row, states that table order is the first-fault precedence and requires every earlier/later paired fault to emit the earlier single finding. The verifier starts both `ls-tree` and `cat-file`, checks only `tree_code`, and then returns `GIT_TOKEN` before checking `blob_code` (`scripts/verify_startup.py` lines 376-411).

Independent disposable-repository injection retained a valid committed tree, made `git cat-file blob HEAD:.ai/START_HERE.md` return nonzero and simultaneously supplied an invalid recorded STATE token. Expected under the frozen table: the sole finding `GIT_COMMAND`. Actual: exit 1 with the sole finding `GIT_TOKEN`; branch, HEAD and Policy hash were populated and the remaining observed fields were null. A separate invalid-token plus malformed-tree pair correctly returned `GIT_TOKEN`, proving the counterexample is specific to the unexamined command result rather than the injection harness.

The current permanent paired test covers token-before-tree and tree-before-index-flags only. It does not cover `GIT_COMMAND` against later rows and therefore does not detect this deviation.

### P1 - B3/B4 - Frozen stderr fail-closed behavior is absent and untestable through the current runner

Revision 2 retains the requirement that nonzero exit or stderr from every Git read fails closed. `_run_git` captures stderr but discards it and returns only `(returncode, stdout)` (`scripts/verify_startup.py` lines 249-258). Every caller is consequently unable to distinguish a clean command from exit-zero output accompanied by stderr. There is no permanent stderr fixture. This is a direct implementation omission from the frozen command contract.

### P1 - B4/F3 - The mandatory complete failure/report/read-only matrix is not permanent

ADR-0019 incorporates pre-review freeze condition 3: every failure/report row, paired precedence and byte-level read-only checks across success and failure must be implementation evidence. Revision 4 additionally requires exact complete JSON values/nulls for every row and every earlier/later pair.

`test_state_fixed_failures_precedence_and_report_shape` injects only eight named rows (`GIT_COMMAND`, `GIT_ROOT`, `GIT_OBJECT_FORMAT`, `GIT_BRANCH`, `GIT_TREE`, `GIT_INDEX`, `GIT_INDEX_FLAGS`, `GIT_WORKTREE`), checks only the finding plus the set of observed keys, and exercises two pairs. It does not instantiate complete JSON oracles for all 12 rows, all earlier/later pairs, stderr, malformed blob/start-entry/case-collision/digest rows, or byte snapshots for those injected failures. The hidden-flag test has strong per-row snapshots, but it cannot substitute for the explicitly frozen complete matrix.

Green focused and full suites therefore do not close B4.

## Frozen finding disposition

| Finding | Disposition | Independent basis |
|---|---|---|
| B1 normalized committed-state identity | **CLOSED** | A separate raw-byte implementation reproduced the normalized START digest and whole-tree digest. Content-identical commit passed; unrelated later committed content returned `GIT_STATE_DIGEST_MISMATCH`. |
| B2 committed-byte/autocrlf semantics | **CLOSED** | A fresh `core.autocrlf=true` clone had CRLF worktree bytes and LF committed blob bytes and passed. |
| B3 exact Git/index/path/failure behavior | **OPEN / BLOCKING** | Stage/index/worktree behavior passed, but paired command/token precedence and stderr fail-closed behavior deviate. |
| B4 acceptance completeness | **OPEN / BLOCKING** | Permanent tests omit complete 12-row JSON, all earlier/later pairs, stderr and all-failure read-only snapshots. |
| F1 fsmonitor-valid plus all hidden flags | **CLOSED** | All eight assume-unchanged/skip-worktree/fsmonitor combinations were independently exercised with `-v`, `-t` and `-f`. Only `H/H/H` passed; all seven flagged states returned only `GIT_INDEX_FLAGS`. |
| F2 portable ASCII path/collision predicate | **CLOSED** | Code matches the frozen ASCII grammar, lengths, reserved stems and ASCII-lower collision rule; permanent positive/negative predicate cases passed. |
| F3 exact first-fault/report contract | **OPEN / BLOCKING** | Command-before-token counterexample fails and complete permanent report/pair oracles are absent. |

## Positive independent evidence

- Separate digest calculation over raw `ls-tree -rz --full-tree` and committed blob bytes matched verifier `state_sha256` in a fresh SHA-1/main repository.
- Content-identical commit retained the digest; a later payload commit with stale token failed.
- Fresh autocrlf clone passed while proving worktree CRLF versus committed LF bytes.
- Hidden-index literal outputs across all eight combinations were independently observed: normal `H/H/H`; fsmonitor-only `H/H/h`; skip states `S/S/S` or `S/S/s`; assume states lowercase under `-v`; combined states remained non-`H`. All verifier runs preserved file-byte snapshots.
- Staged and index-only divergence returned `GIT_INDEX`; unstaged divergence returned `GIT_WORKTREE`; committed executable START_HERE returned `GIT_START_ENTRY`. All were read-only.
- Root command/root/object-format/branch/tree/index/flags/worktree/whole-status injected failures emitted the frozen code/path/reason for the exercised single fault.
- Current `.gitattributes` preserves the selected Policy bytes; revision 2's committed-blob/index/status contract, rather than raw START_HERE worktree equality, correctly handled autocrlf.

## Commands and results

- `uv --cache-dir .uv-cache run python -m unittest tests.test_verify_startup -v` -> **20 passed, 1 skipped** in 63.473s. The skip is the host-denied symlink fixture.
- `uv --cache-dir .uv-cache run pytest -q --tb=line` -> **219 passed, 2 skipped, 2 known dependency warnings, 25 subtests passed** in 179.85s.
- `uv --cache-dir .uv-cache run python -m compileall -q optivest scripts tests` -> exit 0.
- `uv --cache-dir .uv-cache run python scripts/verify_startup.py --root .` -> exit 0, structural PASS, findings empty, `main / UNBORN / dirty`, Production denied.
- `git diff --check` -> exit 0, with the known limitation that the repository is wholly untracked.
- Independent disposable probe -> positive matrix above plus the blocking command/token counterexample; temporary script and repositories removed.

## Bounded Terra correction specification

1. Change only `scripts/verify_startup.py`, `tests/test_verify_startup.py` and necessary Phase-0 operational records. Preserve Policy, frozen design triplet/pre-review/ADR, `.gitattributes` semantics, application/DB/provider/model/risk/wealth/return-bridge/trial/Production files and all positive B1/B2/F1/F2 behavior.
2. Make every Git read retain stdout and stderr and apply the frozen `GIT_COMMAND` rule without leaking command output. Resolve command results before a lower-priority semantic finding can win. The command-failure plus invalid-token counterexample must emit only exact `GIT_COMMAND`.
3. Add permanent complete-report oracles for all 12 rows with exact top-level report, finding, observed values/nulls, exit 1 and denial values. Add every earlier/later paired fault required by revision 4, including command failures at later Git reads versus earlier semantic defects.
4. Add exit-zero-with-stderr and nonzero-with-stderr fixtures for each applicable Git-read stage, malformed/truncated/duplicate binary outputs, missing/wrong START entry, case collision, digest mismatch and exact no-source-output assertions.
5. Snapshot worktree and all `.git` file bytes around every success/failure command path, including the complete fault/pair matrix. Retain the existing all-eight hidden-flag mutation proof.
6. Run focused Phase-0 tests, full pytest, compile, structural startup and whitespace checks. Return to Sol for one independent recheck before any engineering PASS, initial commit or push.

No design change is required for these defects; the implementation must conform to the already-frozen triplet. If fixing global table precedence is believed to require different semantics, stop and return `DESIGN CHANGE REQUIRED` to Astra rather than silently redefining the table.
