# PHASE0-GIT-IDENTITY-V2 amendment — corrected revision 2

Date: 2026-09-21, Asia/Tokyo. Owner: Astra. Status: `CORRECTED DRAFT / SOL INDEPENDENT RE-REVIEW REQUIRED / NOT FROZEN`. Authority: selected Policy §17 and ADR-0010/0011. Responds to B1-B4 of `docs/reviews/phase0_git_identity_pre_review.md`. Draft 1 remains review evidence. No implementation is authorized.

## Contract

Committed repositories record `Commit / HEAD` as `STATE_SHA256:<64 lowercase hex>`, a self-reference-free digest of the complete committed content state. Verifier output still reports actual observed HEAD SHA separately.

State digest algorithm, byte-exact:

1. Require Git object format `sha1`, branch `main`, resolvable HEAD and exact workspace Git root.
2. Read `git ls-tree -rz --full-tree HEAD` as binary NUL-delimited records. Each record is exactly `<mode SP type SP object TAB path NUL>` using Git's raw `-z` path bytes. Reject malformed records, duplicate paths, non-blob START_HERE, START_HERE mode other than `100644`, or missing START_HERE.
3. Retain every record except `.ai/START_HERE.md` byte-for-byte.
4. Read committed START_HERE with `git cat-file blob HEAD:.ai/START_HERE.md` as binary. Require strict UTF-8 without BOM, LF only, exactly one full machine line matching `- Commit / HEAD: `STATE_SHA256:[0-9a-f]{64}`` with existing optional-parenthetical grammar, and no NUL.
5. Replace only those 64 hex characters with 64 ASCII zeroes; preserve every other byte. Compute lowercase `normalized_start_sha256=SHA256(normalized committed START_HERE bytes)`.
6. Replace its tree record with exact bytes `100644 blob sha256:<normalized_start_sha256>\t.ai/START_HERE.md\0`.
7. Sort resulting records by raw path bytes, concatenate and compute `state_sha256=SHA256(records)`. Recorded token must equal `STATE_SHA256:<state_sha256>`.

The typed SHA-256 replacement removes the cycle. Paths, modes, types and Git blob OIDs for every other file remain inputs. Any tracked content/path/mode addition, deletion or change outside the 64 digits changes the digest. A content-identical commit is accepted because commit metadata is not workspace-content drift.

## Worktree/index semantics

Use Git index semantics rather than raw worktree newline equality:

- `git status --porcelain=v1 -z -- .ai/START_HERE.md` must be empty.
- `git ls-files -s -z -- .ai/START_HERE.md` must return exactly one stage-0 `100644` entry whose OID equals the HEAD tree START_HERE OID; merge stages/extra entries fail.
- Clean `core.autocrlf=true` LF-blob/CRLF-worktree checkout passes because digest uses committed blob bytes.
- Symlink, executable, gitlink/tree, case-collision, unreadable/corrupt output or command failure fails closed.

`UNBORN` remains valid only on main with no HEAD/ref. Legacy 40-character SHA remains accepted only when equal to observed HEAD. Existing regular/resolved-inside-root checks still apply.

## Failure and output

Precedence: root/branch/object-format -> recorded-token syntax -> committed tree/index/status -> digest comparison -> remaining governance checks. Use stable detail `GIT_STATE_DIGEST_MISMATCH` without source contents. Output reports actual `observed.head`, literal `recorded_head`, and new `observed.state_sha256`; legacy/UNBORN state_sha256 is null.

Git commands retain optional-lock/index-refresh suppression. Existing before/after read-only snapshot is extended to every invoked Git path; no checkout/add/update-index/hash-object-write or mutation.

## Acceptance matrix

1. First committed main with correct token passes and reports actual HEAD/digest.
2. Later unrelated blob change fails stale token; updating token within that commit to the normalized new state passes.
3. Content-identical commit passes unchanged digest.
4. Add/delete/rename/mode-change fails stale token.
5. Any START_HERE byte outside the 64 digits changes digest and stale token fails.
6. Changing only digits succeeds only when equal to computed digest.
7. Clean Windows autocrlf checkout passes; staged/unstaged START_HERE divergence fails.
8. Index-only divergence, merge stages, untracked replacement and HEAD/index mismatch fail.
9. START_HERE symlink/executable/tree/gitlink/missing/duplicate/case-collision and malformed UTF-8/BOM/CRLF committed blob fail deterministically.
10. Malformed/truncated/duplicate ls-tree/ls-files, command failure, non-sha1 object format and corrupt Git fail.
11. Legacy SHA and UNBORN remain covered; stale legacy SHA fails.
12. Every success/failure is byte-for-byte read-only.

## Scope and workflow

After Sol PASS and exact ADR freeze only: update INITIAL_DESIGN with amendment reference, verifier, isolated tests, START_HERE token, README/AGENTS if needed and operational records. No Policy, investment/model/provider code, DB/migration, risk/wealth/return-bridge semantics, Production gate or trial change.

Sequence: corrected design -> Sol re-review -> exact ADR freeze -> Terra implementation/tests -> Sol post-validation -> initial commit -> remote/push. Until post-validation, remain UNBORN.
