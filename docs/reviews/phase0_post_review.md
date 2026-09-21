# Phase 0 Offline Startup Verifier — Post-Implementation Review

## Verdict

**PASS for the frozen PHASE0-V1 scope.** The implementation conforms to the reviewed Phase 0 contract after Terra's single fix round. The earlier two blockers are closed: dirty worktree state is now observed and reported, and a syntactically valid but dangling `main` ref is no longer accepted as a committed or unborn repository.

This verdict means only that the read-only offline governance checker is implemented and falsifies the scoped structural failures. It does not validate investments, models, data, approvals, OOS, shadow operation, portfolio feasibility, or production readiness. Every observed report remained `NOT PRODUCTION READY`.

Reviewer: **GPT-5.6 Sol — Independent Reviewer / Validator**.

## Reviewed authority and artifacts

- Selected Policy SHA-256: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- Frozen `docs/INITIAL_DESIGN.md` SHA-256: `43FCCF65CD4320B76D835198E2C18A0DD1FF87F1A0B2E88571B0360A7A65A364`
- Decision: `.ai/DECISIONS.md`, ADR-0010 scoped freeze `PHASE0-V1`
- `scripts/verify_startup.py` SHA-256: `CE9BA6060EDCA2942AA1E3CF35F970B0AC1D07E62271B0CCA53D38CDDD7B77DC` (417 lines)
- `tests/test_verify_startup.py` SHA-256: `FA997605EBDF54FA960A3F17FE04999C1E592E2A7F0026DC8DF52DE45393B76D` (255 lines)

Only the frozen Phase 0 implementation and its tests were evaluated. No implementation files were changed by the reviewer.

## Independent execution evidence

### Isolated unit suite

Command:

```text
python -m unittest discover -s tests -v
```

Result: exit `0`; **13 passed, 1 skipped**, 9.006 seconds. The skipped case was direct Windows file-symlink creation because the host denied that operation.

The suite independently exercised valid unborn state, committed `main`, dirty reporting, status-command failure, dangling refs, byte/newline policy mutation, duplicate JSON keys, boolean gate IDs, gate readiness contradiction, malformed and unknown trial provenance, N/A/null handling, blank ledger lines, START_HERE metadata and Git mismatches, parent-repository capture, non-main branch, missing files, directory substitution, and the byte-level read-only invariant.

### Native Windows junction escape

A reversible temporary fixture replaced `.ai` with a native directory junction pointing outside the temporary repository. Junction creation succeeded. The verifier returned exit `1`, `startup_integrity: FAIL`, and `FILE_OUTSIDE_ROOT` findings. The temporary fixture was removed by its managed temporary-directory context.

This verifies the relevant directory-junction escape on this Windows host. The exact direct file-symlink fixture remains unexecuted because symlink creation was unavailable; the same resolved-path containment function protects every inspected file, but this review does not claim that unavailable OS operation was executed.

### Actual workspace run and read-only check

Command:

```text
python scripts/verify_startup.py --root C:\AI\App_Dev\OPTIVEST
```

Observed result:

- exit `0`
- `startup_integrity: PASS`
- `production_readiness: NOT PRODUCTION READY`
- actual policy hash matched the selected authority
- branch `main`; HEAD `UNBORN`
- dirty state `true`; bounded total count `11`
- findings `0`
- full workspace file-path/SHA-256 snapshot, including `.git`, was byte-identical before and after the run
- capability limits explicitly deny investment/model, OOS, shadow, approval-provenance, and append-only-history validation

The dirty state is informational under the frozen contract; it is not silently treated as clean and is not repaired.

## Critical failure-path inspection

The verifier now distinguishes the three relevant Git states:

1. A commit is accepted only when `HEAD^{commit}` resolves and is a lowercase 40-character SHA-1 matching the recorded HEAD.
2. True unborn state is accepted only on symbolic branch `main` when neither HEAD nor `refs/heads/main` resolves.
3. A present/dangling ref or non-commit object produces `GIT_HEAD_OBJECT_INVALID`; a Git status failure produces `GIT_STATUS_FAILED`.

The previous dangling-ref exploit was reproduced before the fix by recording the same nonexistent 40-character object ID in START_HERE. The old implementation returned exit `0`/PASS. The repaired implementation and its isolated regression fixture reject that state.

Dirty state is obtained through `git status --porcelain` with `GIT_OPTIONAL_LOCKS=0` and `core.refreshIndex=false`. The report exposes only a boolean and bounded staged/unstaged/untracked/total counts, so it does not leak file paths or contents. Status failure is fail-closed.

The remaining reviewed paths conform to the freeze: raw-byte policy hashing and UTF-8 full read; strict START_HERE fields and denial tokens; exact hash-pinned §18 gate extraction independent of the register; duplicate-key/type/schema checks for gate and JSONL; explicit trial N/A handling; regular-file/root-containment checks; stable sorted findings; one JSON stdout document; exception-to-FAIL behavior; and an unconditional `NOT PRODUCTION READY` result.

## Residual limitations

- Direct Windows file-symlink creation was unavailable and that exact fixture was skipped. A native directory-junction escape was successfully exercised and rejected. Other unusual reparse-point types were not independently created.
- Manual evidence references and metadata are structurally checked assertions. Their truth and approval provenance are outside this verifier.
- A current JSONL snapshot cannot prove historical append-only behavior; the report correctly retains that limitation.
- Dirty counts are bounded diagnostics, not a complete disclosure of changed paths. That is consistent with the frozen contract.
- The actual repository was unborn and dirty during this run. Committed-main behavior was validated in isolation, not asserted for the actual workspace.
- No investment, model, data, OOS, shadow, portfolio, order, deployment, or production validation was performed.

No remaining blocker was found within PHASE0-V1. Phase 0 may be recorded complete after the parent updates operational handoff/test-status records without changing the reviewed source or test artifacts.
