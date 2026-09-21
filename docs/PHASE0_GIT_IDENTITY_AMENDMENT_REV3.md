# PHASE0-GIT-IDENTITY-V2 amendment — corrected revision 3

Date: 2026-09-21, Asia/Tokyo. Owner: Astra. Status: `CORRECTED DRAFT / SOL INDEPENDENT RE-REVIEW REQUIRED / NOT FROZEN`.

This artifact incorporates revision 2 by exact SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C` and adds controlling B3-B4 closure. A freeze pins both files/hashes. No implementation is authorized.

## Hidden index flags

Before trusting status, run binary commands for literal `.ai/START_HERE.md`: `git ls-files -s -z`, `git ls-files -v -z`, and `git ls-files -t -z`, each followed by `-- <literal path>`. Stage output must be exactly one stage-0 `100644 <HEAD-tree-OID> 0<TAB>path<NUL>` record. Each tag output must be exactly `H SP path NUL`. Lowercase, `S`, other/unknown tag, missing/extra/truncated record is `GIT_INDEX_FLAGS`. This rejects assume-valid/assume-unchanged, skip-worktree, fsmonitor-valid and unknown states before the revision-2 porcelain check. Tests independently set each flag, alter worktree bytes and prove rejection. Production never changes flags/index.

## Case/path semantics

Every HEAD path must be strict UTF-8, Unicode NFC then Python `casefold()` unique. Distinct raw paths with the same normalized key fail `GIT_CASE_COLLISION`. Reject dot/dot-dot components, backslash, absolute/drive paths and paths that do not round-trip as workspace-relative Windows paths. START_HERE must be exact ASCII path and 100644 blob. These are conservative portable rules.

## Closed precedence and report

First applicable only: `GIT_COMMAND`, `GIT_ROOT`, `GIT_OBJECT_FORMAT`, `GIT_BRANCH`, `GIT_TOKEN`, `GIT_TREE`, `GIT_CASE_COLLISION`, `GIT_START_ENTRY`, `GIT_INDEX`, `GIT_INDEX_FLAGS`, `GIT_WORKTREE`, `GIT_STATE_DIGEST_MISMATCH`. Each causes startup failure/nonzero exit and a fixed inert reason without bytes. Finding path is START_HERE for token/start/index/flags/worktree/digest and root otherwise.

Observed report always has exactly `{branch,head,state_sha256,recorded_branch,recorded_head,dirty,dirty_counts,policy_sha256}`; unknowns are null. Valid committed mode reports actual HEAD and computed state even on digest mismatch, plus literal recorded token. UNBORN/legacy uses null state. Dirty counts retain existing whole-worktree semantics and never replace scoped checks.

## Additional acceptance

Cover assume-unchanged, skip-worktree and both; lowercase/unknown/truncated/duplicate tags; non-ASCII NFC/casefold collision; invalid UTF-8/backslash/dot/drive paths; paired-fault first-error ordering; exact report keys/nulls at each stage; and before/after worktree plus Git index/config/refs/logs/objects snapshots for every command. Revision-2 boundaries/workflow remain unchanged. PASS must cover the exact two-file pair before freeze.
