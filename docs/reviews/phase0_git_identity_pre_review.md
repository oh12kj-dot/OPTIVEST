# PHASE0-GIT-IDENTITY-V2 independent pre-implementation review

Reviewer: GPT-5.6 Sol, independent falsification-first review, 2026-09-21 (Asia/Tokyo).

Reviewed amendment: `docs/PHASE0_GIT_IDENTITY_AMENDMENT.md`, draft 1, raw SHA-256 `DF3BEA3718DBD8259D077D53EEDFC9E6C29EC9A5340AB7DD940A63685F29D790`.

Authority: selected `OPTIVEST_AI_POLICY_V10.md`, raw SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; ADR-0010/0011 and the frozen Phase-0 portion of `docs/INITIAL_DESIGN.md`.

Observed repository state: `main / HEAD UNBORN`; the checkout remains untracked. This review changed no Policy, decision, amendment, verifier, test, application, database, provider, model, trial or Production-gate artifact.

## Verdict

**DESIGN CHANGE REQUIRED**

`SELF` removes the literal commit-hash fixed point, but draft 1 does so by replacing a pinned commit identity with a statement that is true for any current commit containing the same START_HERE bytes. That weakens committed-state drift detection. The draft also fails its exact-byte rule on an ordinary clean Windows checkout with `core.autocrlf=true`, and it does not freeze the binary Git commands, tree-mode checks, failure codes and negative tests needed for a read-only cross-platform implementation.

No implementation, first commit or push is authorized from this draft. Astra must correct B1-B4, produce a new exact hash and request independent re-review before an ADR amendment/freeze.

## Independent baseline

The problem statement is correct: a commit cannot normally contain its own final SHA in a tracked file because changing that file changes the tree and therefore the commit hash. Existing exact-SHA mode can validate an uncommitted operational record, but cannot produce a clean self-referential commit. A non-self-referential representation is therefore justified.

The proposed `SELF` checks do establish that the working START_HERE file is the same as the blob at the current HEAD and that its path is clean. They do **not** establish that the current HEAD is the previously reviewed/expected commit.

## Blocking findings

### B1 - CRITICAL - Plain SELF removes exact committed-HEAD drift detection

- **Location:** amendment lines 11-24 and acceptance lines 30-31.
- **Counterexample:** in an isolated `main` repository, commit 1 contained tracked `.ai/START_HERE.md` with `Commit / HEAD: SELF`. A second commit changed only `payload.txt`. HEAD changed from `39e06c3828695c3150fc880ceae9b417d3a7fead` to `b2f1d8440890e7bed5896902810976f700a580f8`. After commit 2, every proposed SELF condition still passed: exact root, main branch, 40-character commit, regular `100644 blob` START_HERE entry, working bytes equal HEAD blob, and empty path-specific status. The verifier would therefore accept an unexpected committed change that V1's exact recorded SHA would have rejected.
- **Reason:** conditions 3-5 prove only `working START_HERE == current HEAD START_HERE`. They contain no expected identity for the remainder of the current commit or its lineage. Reporting the actual SHA after the fact does not compare it with trusted prior state.
- **Required correction:** replace bare `SELF` with a nonrecursive pinned identity, or explicitly obtain user approval to weaken drift detection—which this task's acceptance criteria do not allow. A viable design is a versioned `SELF:<sha256>` projection digest computed over a fully specified representation of branch, parent commit IDs and every HEAD tree entry except `.ai/START_HERE.md`, including path bytes, mode, object type and blob/object ID. START_HERE itself must still match its HEAD blob and have a clean index/worktree path. Any alternative such as a dedicated protected Git ref/tag must define creation, clone/fetch and verification semantics and preserve equivalent drift detection. The digest algorithm and update workflow must be exact before freeze.
- **Disposition:** **OPEN / BLOCKING**.

### B2 - HIGH - Exact byte equality fails on a clean default Windows checkout

- **Location:** amendment line 18, read-only acceptance line 39 and allowed scope line 43.
- **Counterexample:** in an isolated Windows Git repository with `core.autocrlf=true` and no START_HERE attribute, a one-line LF START_HERE blob was 24 bytes. After a normal checkout, the working file was 25 bytes with CRLF. `git status --porcelain=v1 -- .ai/START_HERE.md` was empty, but raw working bytes differed from the HEAD blob. This is an ordinary clean checkout, not drift.
- **Reason:** the current `.gitattributes` protects only `/OPTIVEST_AI_POLICY_V10.md -text`; `.ai/START_HERE.md` is unprotected, while the local Git configuration reports `core.autocrlf=true`. Draft 1's allowed file list does not authorize the required `.gitattributes` change.
- **Required correction:** either add `/.ai/START_HERE.md -text` (or another exact reviewed no-conversion rule) to `.gitattributes` and include that file in allowed implementation scope, or redefine comparison as a precisely specified Git-canonical content comparison instead of raw filesystem-byte equality. If raw equality is retained, require a fresh Windows clone/checkout test with `core.autocrlf=true`, byte equality, clean path status and read-only verification. Preserve the selected Policy's existing `-text` protection.
- **Disposition:** **OPEN / BLOCKING**.

### B3 - HIGH - Git object, path, binary-output and failure semantics are not closed

- **Location:** amendment lines 15-22 and 26-39.
- **Counterexample/reason:** `git show HEAD:.ai/START_HERE.md` alone does not prove a regular-file tree mode; a symlink is also a blob and a submodule/tree requires separate rejection. The current helper decodes stdout as UTF-8 text and applies `.strip()`, so it cannot perform exact binary equality or preserve terminal newlines. The draft does not state whether `observed.recorded_head` remains `SELF`, which code is emitted for SELF with UNBORN HEAD, missing HEAD entry, dirty path or byte mismatch, or how Git-command failure takes precedence over the generic existing mismatch finding. It also does not freeze literal pathspec, NUL-delimited status, untracked handling or no-index-refresh flags.
- **Required correction:** define the exact command and byte contract, for example:
  - root: `git rev-parse --show-toplevel` with resolved-root equality;
  - branch: `git symbolic-ref --quiet --short HEAD` exactly `main`;
  - commit: `git rev-parse --verify HEAD^{commit}` and exact 40-lowercase-SHA-1 rule;
  - entry: NUL-safe `git ls-tree -z --full-tree HEAD -- .ai/START_HERE.md`, exactly one `100644 blob` record for the literal repository path;
  - blob: `git cat-file blob HEAD:.ai/START_HERE.md` captured as raw bytes, with no text decoding, newline conversion or stripping;
  - status: `git status --porcelain=v1 -z --untracked-files=all -- .ai/START_HERE.md`, requiring zero output bytes;
  - every Git read under `GIT_OPTIONAL_LOCKS=0` and `core.refreshIndex=false`, with nonzero exit/stderr handled fail-closed and no source contents exposed.

  Freeze exact finding codes and precedence for parse/grammar, Git unavailable/root/branch/object/entry/mode/blob/status/byte/digest mismatch. Define the report fields: `observed.head` must be the actual SHA, while any `recorded_head` field's `SELF`/digest representation must be explicit. Specify working-file symlink/reparse behavior and exact repository-relative path semantics on Windows.
- **Disposition:** **OPEN / BLOCKING**.

### B4 - HIGH - The acceptance matrix omits the counterexamples needed to prove preservation

- **Location:** amendment lines 28-39.
- **Counterexample/reason:** the ten tests would not catch B1 because they never create a later commit that leaves START_HERE unchanged. They would not catch B2 because they do not perform a clean Windows checkout/clone with line-ending conversion. They also do not test a non-regular HEAD tree entry, raw trailing-newline byte differences, index-only staged changes with worktree bytes restored to HEAD, the exact SELF failure codes/precedence, SHA-256-object-format rejection, or read-only behavior of every new success/failure command.
- **Required correction:** add permanent isolated tests for:
  1. an unexpected later commit with unchanged START_HERE, which must fail the pinned projection/ref identity;
  2. authorized identity update under the exact amendment workflow, which passes and reports actual HEAD;
  3. fresh Windows checkout with `core.autocrlf=true` and exact bytes;
  4. HEAD symlink/submodule/non-regular entry rejection without relying on OS symlink creation where `git update-index --cacheinfo` can construct the tree;
  5. unstaged, staged, conflict, untracked and index-only divergence, including worktree restored to HEAD while index differs;
  6. one-byte/trailing-newline blob mismatch;
  7. corrupt/unreadable command failures and exact finding precedence;
  8. legacy equal/stale SHA and unchanged true-UNBORN behavior;
  9. byte-for-byte before/after snapshots including `.git` for all new command paths; and
  10. unsupported object format or non-40-character HEAD rejection where feasible.
- **Disposition:** **OPEN / BLOCKING**.

## Acceptance-area disposition

| Area | Disposition | Independent conclusion |
|---|---|---|
| Self-reference removal | **PARTIAL** | Bare SELF removes the cryptographic fixed point but supplies no replacement pinned identity. |
| Committed drift detection | **FAIL / CHANGE REQUIRED** | A later unrelated commit satisfies all six SELF checks. |
| Repository root and branch | **READY AFTER FREEZE** | Existing exact-root and symbolic-main behavior is appropriate; preserve it. |
| HEAD/object identity | **CHANGE REQUIRED** | Exact SHA reporting is fine, but expected committed identity and object-format/failure rules are incomplete. |
| HEAD tree path/type | **CHANGE REQUIRED** | Existence is stated; exact `100644 blob`/literal-path command semantics are not. |
| Working-vs-HEAD bytes | **CHANGE REQUIRED** | Raw binary capture is unspecified and clean Windows CRLF conversion breaks equality. |
| Path cleanliness | **CHANGE REQUIRED** | Empty scoped status is directionally correct; freeze NUL/pathspec/untracked/index semantics and failure behavior. |
| Whole-worktree dirtiness | **PASS CONCEPTUALLY** | Allowing unrelated user changes while reporting `dirty=true` preserves current scope. It must not substitute for committed-identity pinning. |
| Read-only property | **CHANGE REQUIRED** | Existing flags/snapshot principle are reusable, but every new binary/tree/status path needs explicit no-lock tests. |
| Legacy exact SHA | **READY AFTER FREEZE** | Retaining exact-equality behavior is compatible; preserve existing failure behavior and document that it need not be a clean self-contained commit. |
| Legacy UNBORN | **READY AFTER FREEZE** | Existing true-UNBORN distinction remains correct; SELF must be explicitly invalid there. |
| Windows behavior | **FAIL / CHANGE REQUIRED** | Clean CRLF checkout counterexample reproduced on the current platform. |
| Test completeness | **FAIL / CHANGE REQUIRED** | B1/B2 and tree-mode/binary/failure counterexamples are absent. |
| Production/investment boundary | **PASS** | No approval, model, provider, database or Production promotion leakage was found. |

## Evidence and commands

- Hash verification matched Policy `ACF013CE...38E67` and amendment `DF3BEA...9D790`.
- Current implementation/test identities remain the ADR-0011 frozen baseline; no code was edited.
- `python -m unittest tests.test_verify_startup -v` -> **13 passed, 1 skipped** in 9.093s. This proves the existing PHASE0-V1 baseline only; it contains no SELF tests.
- Isolated two-commit probe reproduced B1 with distinct HEADs while every proposed SELF condition remained true.
- Isolated Windows `core.autocrlf=true` checkout reproduced B2: blob 24 bytes, working file 25 bytes, CRLF present, path status empty.
- Current `.gitattributes` contains only `/OPTIVEST_AI_POLICY_V10.md -text`; `git config --get core.autocrlf` returned `true`.
- Repository remains `main / HEAD UNBORN`; no commit, push or remote operation occurred.

## Required re-review gate

A corrected revision must preserve the narrow structural-only Phase-0 boundary while closing B1-B4. Sol must independently reproduce the later-commit drift case, clean Windows checkout, regular-tree-mode/binary-byte semantics, staged/index divergences and byte-level read-only invariant. Only a new exact-hash `PASS FOR SCOPED DECISION FREEZE` may precede ADR amendment, Terra implementation, post-validation, initial commit and push.

Literal boundaries remain unchanged: structural consistency only; no investment/model/provider/OOS/shadow or approval validation; `RISK BUDGET NOT APPROVED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

## 2026-09-21 revision-2 independent re-review

Reviewer: GPT-5.6 Sol, independent falsification-first re-review. Reviewed `docs/PHASE0_GIT_IDENTITY_AMENDMENT_REV2.md`, raw SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C`, against selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, ADR-0010/0011 and the draft-1 review pre-addendum SHA-256 `A61D8804DCB95CD6721AED5EE65B886D1F23C2272FE2DA923509B4D300FA99CE`.

### Verdict

**DESIGN CHANGE REQUIRED**

The normalized `STATE_SHA256` construction closes the cryptographic fixed point and preserves content-state drift detection across ordinary commits. It also correctly moves canonical content comparison to committed bytes so a clean autocrlf checkout can pass. Revision 2 is nevertheless not ready for scoped freeze: its two stated Git checks can be bypassed by START_HERE index flags, and its new failure/output contract still does not define unique codes, precedence and case-collision semantics. These are bounded B3-B4 corrections; B1-B2 must be preserved unchanged.

### B1-B4 disposition

| Original finding | Disposition | Independent result |
|---|---|---|
| B1 bare SELF loses committed drift detection | **CLOSED — preserve** | The normalized digest excludes only the 64 self-referential digits while binding normalized START_HERE bytes and every other recursive tree record. First commit passed; an unrelated later content commit failed stale state; updating its token passed; an allow-empty/content-identical commit retained the same valid digest. |
| B2 clean Windows checkout fails raw equality | **CLOSED — preserve** | A fresh `core.autocrlf=true` clone had CRLF worktree bytes unequal to the LF committed blob, empty scoped status, equal index/HEAD OID and a matching committed state digest. No START_HERE `.gitattributes` change is required by this corrected Git-canonical contract. |
| B3 Git/index/failure semantics incomplete | **OPEN / BLOCKING** | C1 and C2 below remain material and independently reproducible or specification-underdetermined. |
| B4 acceptance matrix incomplete | **OPEN / BLOCKING** | The matrix covers the ordinary state transitions but omits the index-bit bypass and still supplies no exact fault-code/field oracle for its malformed/failure rows. |

### C1 — HIGH — Index flags make altered START_HERE bytes pass every specified cleanliness check

- **Location:** revision 2 lines 23-30 and acceptance rows 7-8 at lines 46-47.
- **Counterexample:** in a disposable valid committed repository, `git update-index --assume-unchanged .ai/START_HERE.md` was followed by a worktree-only edit outside the 64 token digits. The revision-2 status command returned zero bytes; `git ls-files -s -z` still returned the one stage-0 `100644` HEAD OID; the committed normalized digest still equalled the recorded token; the path remained a regular file inside root; yet working START_HERE bytes differed from HEAD. `--skip-worktree` independently produced empty scoped status and the same stage-0 entry (`git ls-files -v -z` exposed tag `S`). Thus the claim that unstaged divergence fails is false under allowed Git index states.
- **Reason:** porcelain status and `ls-files -s` trust/omit the assume-unchanged and skip-worktree bits. Neither command specified by revision 2 detects those flags.
- **Required correction:** freeze an exact binary/NUL-safe flag inspection and reject both flags for the canonical START_HERE entry before trusting scoped status—for example, an exact `git ls-files -v -z -- .ai/START_HERE.md` contract with the sole accepted tag and literal returned path specified. Define and test other exposed entry tags instead of relying on a generic “fail closed” sentence. Retain the stage-0/mode/OID checks. Permanent tests must mutate a non-machine START_HERE byte under each flag and prove a stable failure without clearing or modifying the flags.
- **Disposition:** **OPEN / BLOCKING**.

### C2 — HIGH — Failure/output and case-collision behavior still have multiple conforming implementations

- **Location:** revision 2 lines 28, 32-36 and acceptance rows 9-10 at lines 48-49.
- **Counterexample/reason:** revision 2 names only `GIT_STATE_DIGEST_MISMATCH`, described ambiguously as a “stable detail.” It does not assign exact finding codes and report-field values for object-format failure, malformed/truncated/duplicate tree data, missing/wrong-mode/non-blob START_HERE, blob decode/BOM/CRLF failure, malformed/extra-stage index data, hidden index flags, scoped-status failure or byte-level parser failure. The arrow-separated stage order does not say whether findings short-circuit or accumulate, nor establish order within `tree/index/status`. `observed.state_sha256` is specified as null only for legacy/UNBORN, leaving its value absent versus null versus computed under each STATE failure unresolved. “Case-collision” has no byte-level equivalence rule despite raw Git paths being arbitrary bytes and Windows/Unicode case rules differing. Tests could therefore pass incompatible JSON contracts while all merely “fail.”
- **Required correction:** add a closed table mapping every new command/parser/state fault to one exact finding code, evaluation order, fail-fast/accumulation rule, exit status and `observed.head`/`recorded_head`/`observed.state_sha256` value. Define collision comparison over exact raw paths (at minimum the canonical ASCII path and case variants) and the literal pathspec/returned-path rule. Freeze exact object-format/root/branch/HEAD commands or explicitly inherit each unchanged PHASE0-V1 command; specify `--untracked-files=all` or why index validation makes configured untracked suppression irrelevant. Permanent fault-injection tests must assert the complete JSON, not only nonzero failure.
- **Disposition:** **OPEN / BLOCKING**.

### Independent state-transition evidence

The reference probe implemented only revision 2's byte algorithm and used disposable SHA-1 repositories:

- First self-consistent commit: actual HEAD `544cfc28e6303b6673e7087ec1ddd39e678085d4`; state digest `89b6f12b45a041e46df40eb39d7ad646cd7d62ef8694ce72d982093b95082df5`; recorded/computed equality passed.
- Content-identical allow-empty commit retained the same digest and passed. An unrelated later blob commit failed its stale token.
- Add, delete, rename, `100644` to `100755` mode change and a START_HERE edit outside the token each changed the digest and failed the stale token.
- Wrong token digits failed while leaving the computed digest unchanged; replacing only the digits with that digest passed.
- Index-only staged divergence was detected by status/OID semantics. Assume-unchanged and skip-worktree counterexamples were not detected, as C1 records.
- Clean autocrlf clone produced CRLF worktree/LF blob inequality while status remained empty and the committed digest passed, confirming the intended B2 correction.
- Raw `ls-tree -z` parsing preserved a tab-containing path created directly in a disposable tree and `cat-file` preserved blob bytes `00ff0d0a`; the header remained exactly three space-delimited fields. Binary parsing direction is sound, subject to C2's required failure oracles.
- Running the proposed read commands with optional locks and index refresh suppressed preserved a byte-for-byte snapshot of all disposable `.git` files in the clean tested path. This positive case does not replace the required per-failure tests.
- The unchanged frozen PHASE0-V1 baseline remained **13 passed, 1 skipped in 9.216s**. This is regression evidence for the current verifier only; revision 2 has no implementation.

All disposable repositories were removed. The reviewed design, Policy, DECISIONS, verifier/tests, applications, databases, providers, models, trials and Production register were not changed.

### Required revision-3 gate

Astra should issue a narrowly corrected revision 3 that preserves the B1 normalized digest and B2 committed-byte/autocrlf semantics while closing only C1-C2/B3-B4. Sol must independently reproduce the ordinary matrix plus assume-unchanged, skip-worktree, exact malformed-command precedence, collision rule and all-path read-only behavior at the new hash. Only `PASS FOR SCOPED DECISION FREEZE` may precede ADR amendment or Terra dispatch.

All boundaries remain structural-only: no investment, model, provider, PIT, calibration, OOS, shadow, approval or Production validation; `RISK BUDGET NOT APPROVED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

## 2026-09-21 revision-3 exact-pair independent re-review

Reviewer: GPT-5.6 Sol, independent falsification-first re-review. Reviewed the exact pair `docs/PHASE0_GIT_IDENTITY_AMENDMENT_REV2.md` SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C` plus `docs/PHASE0_GIT_IDENTITY_AMENDMENT_REV3.md` SHA-256 `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D`, against Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, ADR-0010/0011 and this review's revision-2 complete hash `EAC0AD2B8F383DBF0DB2DAADE899E5313114E4CAF42E6ACB9C16C9DC6D62F1B7`.

### Verdict

**DESIGN CHANGE REQUIRED**

Revision 3 correctly adds exact tag-byte parsing, a first-fault code order and a fixed observed-key set, but it does not close B3-B4. Its chosen Git option cannot observe the fsmonitor-valid bit it claims to reject; the Windows round-trip predicate and Unicode version are not executable invariants; and the per-stage report values remain deferred to future tests rather than fixed by the design. The normalized digest and autocrlf semantics in revision 2 remain accepted design components and must not be reopened.

### Remaining B3-B4 disposition

| Area | Disposition | Independent conclusion |
|---|---|---|
| Assume-unchanged | **CLOSED — preserve** | `git ls-files -v -z` emits lowercase `h`; exact `H` rejection closes the reproduced bypass. |
| Skip-worktree | **CLOSED — preserve** | Both `-v` and `-t` emit `S` (or lowercase when combined with another flag); exact `H` rejection closes the reproduced bypass. |
| Fsmonitor-valid | **FAIL / BLOCKING** | The pair uses `-t`, but Git exposes this bit with `-f`; both specified tag commands can emit `H` and accept it. |
| Binary record parsing | **READY AFTER CORRECTION** | NUL termination, exact stage/tag records and raw tree/blob parsing are directionally complete. Preserve byte capture and no decoding before record framing. |
| Portable case/path rule | **FAIL / BLOCKING** | NFC/casefold collision is stated, but “round-trip as workspace-relative Windows paths” and Unicode-table identity are not defined exactly. |
| Fault precedence | **PARTIAL / BLOCKING** | Code order and first-fault behavior are present, but several faults are not uniquely mapped and per-stage observed values are not enumerated. |
| Read-only matrix | **READY AFTER CORRECTION** | The new `ls-files` reads preserved byte snapshots in tested normal/assume/skip states; the final matrix must use the corrected command and exact fault fixtures. |
| B3 overall | **OPEN / BLOCKING** | F1-F3 below remain. |
| B4 overall | **OPEN / BLOCKING** | Its fsmonitor and exact-report rows cannot produce the claimed oracle from the reviewed bytes. |

### F1 — HIGH — `ls-files -t` does not expose fsmonitor-valid

- **Location:** revision 3 line 9 and additional acceptance line 23.
- **Counterexample:** Git 2.54.0 documents `-v` as lowercase for assume-unchanged, `-f` as lowercase for fsmonitor-clean, and `-t` only as generic status tags. In a disposable repository with `core.fsmonitor=true`, the START_HERE entry emitted exact accepted bytes `H .ai/START_HERE.md\0` for both revision-3 commands `ls-files -v -z` and `ls-files -t -z`, while `ls-files -f -z` emitted lowercase `h .ai/START_HERE.md\0`. Explicit `update-index --fsmonitor-valid` retained the same result. Therefore the prescribed checks accept the forbidden flag and the statement “This rejects ... fsmonitor-valid” is false.
- **Required correction:** replace the redundant `-t` check with, or add, exact binary `git ls-files -f -z -- .ai/START_HERE.md`; require exact uppercase `H SP canonical-path NUL` from `-v`, `-f` and any retained `-t`. Add independent normal/fsmonitor/assume/skip/all-combination fixtures that assert literal bytes and `GIT_INDEX_FLAGS`. Do not rely on porcelain status to clear or interpret flags.
- **Disposition:** **OPEN / BLOCKING**.

### F2 — HIGH — Portable path acceptance is not uniquely specified

- **Location:** revision 3 line 13 and acceptance line 23.
- **Counterexample/reason:** Git accepted disposable tree entries named `CON`, `aux.txt`, `name.`, `name `, `a:b`, NFC and decomposed accented names, and an invalid-UTF-8 raw name. The explicit rules reject invalid UTF-8 and drive forms and detect the two normalized Unicode collisions, but “round-trip as workspace-relative Windows paths” has no named algorithm. For example, `PureWindowsPath('CON').as_posix()` round-trips text unchanged even though `CON` is a reserved Windows device; `name.` and `name ` also round-trip text while Win32 normalization/filesystem behavior differs. Implementations may disagree on device basenames, trailing dots/spaces, colons/ADS, controls, component limits and long paths. Python `casefold()`/NFC also depends on the interpreter's Unicode database; the project permits Python `>=3.10`, while the reviewed environment is Python 3.10/Unicode 13.0.0.
- **Required correction:** replace “round-trip” with a closed host-independent component predicate covering forbidden code points/separators, colon/ADS, trailing dot/space, device basenames, component/path limits and exact drive/UNC/absolute handling. Pin the Unicode normalization/casefold data version or restrict the accepted repertoire to a version-stable set. Map invalid UTF-8 and every portability rejection to one explicit code before collision evaluation, with literal path bytes never emitted.
- **Disposition:** **OPEN / BLOCKING**.

### F3 — HIGH — The ordered code list does not yet determine exact reports at each failure stage

- **Location:** revision 3 lines 17-19 and acceptance line 23.
- **Counterexample/reason:** “fixed inert reason” does not give the literal reason values. The design does not state whether invalid UTF-8, a reserved/non-round-tripping path, wrong raw canonical-path return, or malformed committed START blob is `GIT_TREE`, `GIT_START_ENTRY` or another listed code. Nor does it enumerate whether `recorded_head`, `recorded_branch`, `head`, `state_sha256`, `dirty` and `dirty_counts` are known or null for each first fault. For example, at `GIT_TOKEN`, branch/HEAD may already be observed and other START fields may already have parsed, but both eager population and fail-fast nulls satisfy the prose. At `GIT_INDEX_FLAGS`, computed state may or may not already exist depending on implementation order. Consequently two incompatible complete JSON objects can conform, and “exact report keys/nulls at each stage” is not independently decidable.
- **Required correction:** add a literal fault table with one row per listed code: triggering command/parse condition, exact fixed reason, finding path, exact process exit code, and all eight observed values or derivation rules at emission. State whether the first Git-identity fault suppresses only later Git-identity faults or all remaining governance findings. Include paired-fault and complete-object fixtures derived directly from that table.
- **Disposition:** **OPEN / BLOCKING**.

### Independent evidence

- Exact four identities matched: Policy, revision 2, revision 3 and pre-addendum review.
- Normal index emitted stage-0 `100644 ... 0<TAB>path<NUL>` and `H` for `-v`/`-t`; assume-unchanged emitted `h` for `-v`; skip-worktree emitted `S`; combined flags remained non-`H`. These commands preserved byte-for-byte worktree and `.git` snapshots.
- With fsmonitor enabled/valid, `-v` and `-t` both emitted accepted `H`, while the omitted `-f` emitted lowercase `h`. Local `git ls-files -h` independently states the option meanings.
- Strict UTF-8 plus NFC/casefold maps NFC/decomposed accented paths to one key and `Straße`/`STRASSE` to one key; this portion is mechanically reproducible within a pinned Unicode table.
- Revision-2 first/later/content-identical, START edit, add/delete/rename/mode, autocrlf, index and binary probes remain valid evidence from the immediately preceding re-review and were not contradicted.

No implementation test can cure these design ambiguities. A narrowly corrected revision 4 may change only F1-F3/B3-B4; it must preserve the exact revision-2 digest/autocrlf contract and all no-state/no-promotion boundaries. Sol must re-review the new exact pair before freeze.

The review changed no design, Policy, DECISIONS, verifier/test, application, database, provider, model, trial or Production-gate artifact. Repository remains `main / HEAD UNBORN`; no commit, remote or push occurred. All boundaries remain structural-only: `RISK BUDGET NOT APPROVED`, relevant evidence `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED`, `NOT PRODUCTION READY`.

## 2026-09-21 revision-4 exact-triplet independent re-review

Reviewer: GPT-5.6 Sol, independent falsification-first re-review. Reviewed the exact design triplet:

- revision 2 SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C`;
- revision 3 SHA-256 `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D`;
- revision 4 SHA-256 `BDC2119A14D67D379A0E70EDB6B7E849C8C66ADF2432B62242C2037A61E94DC0`.

Authority remains selected Policy SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`, ADR-0010/0011 and this review's revision-3 pre-addendum hash `E014F3A45A14A75E90298FA93D53C13D2DB9235BF10C03C5842E45038182A0D9`.

### Verdict

**PASS FOR SCOPED DECISION FREEZE**

Revision 4 closes F1-F3 without reopening revision 2's B1-B2 corrections. Across the exact triplet, B1-B4 are independently decidable and no material contradiction or promotion leakage remains. This verdict authorizes only an Astra exact-hash ADR amendment/freeze for PHASE0-GIT-IDENTITY-V2. It is not implementation acceptance, does not authorize a commit or push, and does not validate any investment, model, data, provider, approval or Production claim.

### Final disposition

| Finding | Final disposition | Independent basis |
|---|---|---|
| B1 / self-reference and committed drift | **CLOSED** | Revision 2's normalized `STATE_SHA256` binds normalized START_HERE plus every other recursive committed record while excluding only its own 64 digits. First/later/content-identical and content/path/mode probes passed. |
| B2 / Windows clean checkout | **CLOSED** | Digesting committed bytes plus exact index/status semantics accepts clean LF-blob/CRLF-worktree checkout without weakening committed drift detection. |
| B3 / Git, index, path, failure and output semantics | **CLOSED** | Revisions 3-4 now cover stage/mode/OID, all three hidden index bits, exact tag bytes, closed ASCII paths/collisions, first-fault codes, literal reasons/paths, report keys/null rules and denial output. |
| B4 / acceptance completeness | **CLOSED FOR DESIGN FREEZE** | The exact triplet requires the ordinary state matrix, all hidden-flag combinations, malformed binary/fault pairs, complete report objects and per-command read-only snapshots. Implementation must make these permanent before post-validation. |
| F1 / fsmonitor-valid | **CLOSED** | Added `ls-files -f -z`; eight-state independent matrix accepted only no flags. |
| F2 / portable path rule | **CLOSED** | ASCII byte grammar, exact lengths/components/device set and ASCII-lower collision eliminate host/Unicode ambiguity. |
| F3 / failure/report contract | **CLOSED** | Table fixes code, path and literal reason; table order fixes first fault; exit/readiness/finding count and established-versus-null field rules close the report contract. |

### Independent counterexample matrix

Hidden-index matrix used disposable SHA-1/main repositories and literal binary outputs for `-v`, `-t` and `-f`:

| assume | skip | fsmonitor | `-v` | `-t` | `-f` | accepted |
|---:|---:|---:|---|---|---|---|
| 0 | 0 | 0 | `H` | `H` | `H` | yes |
| 0 | 0 | 1 | `H` | `H` | `h` | no |
| 0 | 1 | 0 | `S` | `S` | `S` | no |
| 0 | 1 | 1 | `S` | `S` | `s` | no |
| 1 | 0 | 0 | `h` | `H` | `H` | no |
| 1 | 0 | 1 | `h` | `H` | `h` | no |
| 1 | 1 | 0 | `s` | `S` | `S` | no |
| 1 | 1 | 1 | `s` | `S` | `s` | no |

Every row preserved the disposable worktree and `.git` byte snapshot while running the three read commands. This closes the prior false acceptance of fsmonitor-valid and preserves assume/skip rejection.

The revision-4 portable predicate was independently applied to the 76 current non-ignored prospective tracked paths: zero grammar/length/device violations and zero ASCII-lower collisions. Crafted `CON`, `aux.txt`, trailing-dot, space, ADS/colon, traversal, absolute, backslash and non-ASCII paths all rejected; `good/path-1.txt` and exact `.ai/START_HERE.md` accepted. The rule is now independent of Python's Unicode database and the host filesystem's normalization.

The revision-4 report table is compatible with the controlling precedence overlay: the first applicable Git-identity fault emits exactly one fixed finding and stops later governance evaluation; safely established values survive and all later/unknown scalars plus pre-status dirty fields are null. Digest mismatch is the explicitly closed exception with computed state, literal recorded values and whole-worktree dirty observation. Permanent implementation tests must instantiate exact complete JSON for every row and all earlier/later paired faults; that is an implementation acceptance obligation, not a remaining design ambiguity.

### Scoped freeze conditions

1. Freeze all three design files at the exact hashes above plus this complete review hash; revision 4 controls F1-F3, revision 3 controls only non-replaced B3-B4 clauses, and revision 2 controls B1-B2/base algorithm and boundaries.
2. Terra may edit only the files authorized by the eventual ADR amendment. No implementation starts from this review alone.
3. Required implementation evidence includes the full revision-2 matrix, all eight hidden-flag rows, exact ASCII path/collision negatives, every failure/report row, paired precedence, legacy SHA, true UNBORN and byte-level read-only checks across success and failure.
4. Sol independent post-validation remains mandatory before any initial commit or push.

No design, Policy, DECISIONS, verifier/test, application, database, provider, model, trial or Production-gate artifact changed in this review. Repository remains `main / HEAD UNBORN`; no commit, remote or push occurred. The result is structural engineering scope only: `RISK BUDGET NOT APPROVED`, relevant items `NOT VERIFIED`, `SHADOW VALIDATION NOT PASSED`, `NOT PRODUCTION READY`.
