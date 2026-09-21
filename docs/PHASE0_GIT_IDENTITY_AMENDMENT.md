# PHASE0-GIT-IDENTITY-V2 amendment — draft 1

Date: 2026-09-21, Asia/Tokyo. Owner: Astra. Status: `DRAFT / SOL INDEPENDENT REVIEW REQUIRED / NOT FROZEN`. Authority: selected Policy §17, ADR-0010/0011, and the user's explicit request to push the currently UNBORN repository. No implementation is authorized by this draft.

## Problem

PHASE0-V1 requires `.ai/START_HERE.md` to contain the exact current commit SHA and requires that value to equal `HEAD`. Once START_HERE is committed, the commit SHA depends on START_HERE's bytes, so the file cannot contain its own resulting SHA without finding a cryptographic fixed point. The contract works for `UNBORN` but cannot produce a self-consistent committed repository.

## Minimal contract amendment

The `Commit / HEAD` machine value additionally accepts the literal `SELF`.

`SELF` means all of the following must pass:

1. Git repository root equals the explicit workspace root.
2. `HEAD` resolves to a 40-character lowercase SHA-1 commit and branch is `main`.
3. `.ai/START_HERE.md` exists as a regular file in the `HEAD` tree.
4. The current START_HERE bytes equal `git show HEAD:.ai/START_HERE.md` bytes exactly.
5. `git status --porcelain=v1 -- .ai/START_HERE.md` is empty: no staged, unstaged, untracked or conflict state for this file.
6. Verifier output reports the actual observed HEAD SHA; `SELF` is never emitted as the observed hash.

`UNBORN` remains valid only for verified main repositories with no HEAD commit/ref. A recorded 40-character SHA remains supported and must exactly equal observed HEAD for backward compatibility. Git failure is never SELF or UNBORN.

This amendment changes only self-identity representation. It does not weaken Policy hash, branch, dirty-state reporting, file/root/link safety, readiness denial, research-ledger validation or any investment/model/provider gate. It does not require the whole worktree to be clean; unrelated user changes remain reported but do not invalidate committed START_HERE identity.

## Closed failures and acceptance

Existing mismatch finding is used for invalid SELF state; no new Production meaning exists. Required isolated tests:

1. committed main repository with tracked byte-identical START_HERE=`SELF` passes and reports actual HEAD;
2. unrelated tracked/untracked dirty files still pass while dirty=true;
3. unstaged START_HERE edit fails;
4. staged START_HERE edit fails;
5. START_HERE absent from HEAD but present untracked fails;
6. detached HEAD or non-main with SELF fails under existing branch contract;
7. corrupt/unreadable Git fails;
8. legacy exact SHA passes only when equal to HEAD and stale SHA fails;
9. UNBORN behavior remains unchanged;
10. verifier remains byte-for-byte read-only, including Git metadata, for SELF success/failure.

## Allowed implementation scope

After independent PASS and exact ADR freeze only: update `docs/INITIAL_DESIGN.md` with a dated amendment reference, `scripts/verify_startup.py`, `tests/test_verify_startup.py`, START_HERE machine value, README/AGENTS only if needed, and `.ai` operational records. Do not change Policy, investment/model/provider code, database/migrations, risk/wealth/return-bridge semantics, Production gate contents or research trials.

Required sequence: Astra draft -> Sol falsification-first review -> exact-hash ADR freeze -> Terra implementation/tests -> Sol post-validation -> initial commit/push. Until then the repository remains UNBORN.
