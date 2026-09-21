# PHASE0-GIT-IDENTITY-V2 amendment — corrected revision 4

Date: 2026-09-21, Asia/Tokyo. Owner: Astra. Status: `CORRECTED DRAFT / SOL INDEPENDENT RE-REVIEW REQUIRED / NOT FROZEN`.

This artifact incorporates revision 2 SHA-256 `8225D5DAE489BEB4B9533CFE2D3B84308B26A214B889FE437E69E9F9DFC12E6C` and revision 3 SHA-256 `A6E5A229934EAE977A7EEFA73F8310D64FB9B22655F8D863787768473EBB625D`, closing F1-F3. A freeze pins all three. No implementation is authorized.

## F1: all hidden-index tags

In addition to revision 3, run `git ls-files -f -z -- .ai/START_HERE.md`. Each of `-v`, `-t`, and `-f` must independently return exactly `H SP .ai/START_HERE.md NUL`. Any other byte is `GIT_INDEX_FLAGS`. Acceptance toggles assume-unchanged, skip-worktree, fsmonitor-valid and every combination, proving each is rejected before status.

## F2: portable ASCII path grammar

Replace revision-3 Unicode/round-trip rule with this closed rule for every HEAD path:

- raw path bytes must be ASCII and match `(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+`;
- total byte length 1-240; each component 1-100;
- component is not `.` or `..`, does not end dot/space, and its ASCII-uppercase stem before the first dot is not `CON,PRN,AUX,NUL,CLOCK$,COM1..COM9,LPT1..LPT9`;
- distinct raw paths compare unique under ASCII lowercase;
- exact `/` separator only; colon, backslash, control, non-ASCII and leading/trailing slash are impossible under grammar.

Any grammar/length/device violation is `GIT_TREE`; lowercase collision is `GIT_CASE_COLLISION`. No Unicode normalization/version or NTFS round-trip claim remains.

## F3: exact failure/report table

All findings are `{code,path,reason}`; exit is 1; `startup_integrity=FAIL`; `production_readiness=NOT PRODUCTION READY`. Fixed mapping:

| code | exact path | exact reason |
|---|---|---|
| GIT_COMMAND | `` | `Git command failed or returned malformed binary output.` |
| GIT_ROOT | `` | `Git root does not equal the requested workspace root.` |
| GIT_OBJECT_FORMAT | `` | `Git object format is not sha1.` |
| GIT_BRANCH | `` | `Git branch is not main.` |
| GIT_TOKEN | `.ai/START_HERE.md` | `Recorded Commit / HEAD token is invalid.` |
| GIT_TREE | `` | `Committed tree record or portable path is invalid.` |
| GIT_CASE_COLLISION | `` | `Committed tree paths collide under ASCII case folding.` |
| GIT_START_ENTRY | `.ai/START_HERE.md` | `Committed START_HERE entry is missing or is not a regular 100644 blob.` |
| GIT_INDEX | `.ai/START_HERE.md` | `START_HERE index entry does not equal the committed stage-0 entry.` |
| GIT_INDEX_FLAGS | `.ai/START_HERE.md` | `START_HERE has a hidden index or worktree flag.` |
| GIT_WORKTREE | `.ai/START_HERE.md` | `START_HERE worktree state is not clean and regular inside the workspace.` |
| GIT_STATE_DIGEST_MISMATCH | `.ai/START_HERE.md` | `Recorded state digest does not match committed workspace content.` |

First-fault precedence is the table order. Report always contains exactly the revision-3 observed keys. Fields safely established before the failing stage retain their values; all not-yet-established scalar fields are null, dirty is null and dirty_counts is null until whole-worktree status succeeds. For digest mismatch, branch/head/computed state/recorded fields/policy hash are populated and dirty fields use observed whole-worktree values. Findings is exactly one Git finding at these stages. No later governance findings are evaluated after a Git failure.

Acceptance pairs each earlier fault with every later fault and proves the earlier single finding, exact JSON keys/values/nulls/reason/exit. Read-only snapshots include commands for `-f` as well as revision-3 commands. Revision-2/3 scope and non-production boundaries remain unchanged.
