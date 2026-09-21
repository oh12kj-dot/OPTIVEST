# OptiVest Phase 0 Governance / Startup Blind Review

## Review identity and status

- Reviewer role/model: **GPT-5.6 Sol — Independent Reviewer / Validator**
- Review method: blind, falsification-first first pass
- Scope: Phase 0 governance, bootstrap, and startup-verifier design only
- Investment-model validation: **not performed**
- OOS, shadow, calibration, risk-model, optimizer, and production validation: **not performed**
- Approval status: **no approval is created by this review**
- Current conservative status: **NOT VERIFIED / RISK BUDGET NOT APPROVED / NOT PRODUCTION READY**

This review does not evaluate an implementation or a proposed architecture. It establishes the failure conditions that a later design and a future offline startup verifier must survive. A comparative review should occur only after the design is supplied.

## Evidence boundary

The sole file inspected for this blind pass was:

- `OPTIVEST_AI_POLICY_V10.md`
- Observed SHA-256: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- Expected SHA-256 supplied in the review mandate: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- Hash result: exact match over raw file bytes
- Observed size: 71,064 bytes
- Observed text extent: 841 lines; the complete file was read in non-truncated bounded chunks
- Encoding markers observed: no UTF-8 BOM; LF line endings

The file's internal title says `Compact V10 — Final`. That label does not displace the user's explicit selection of this exact file and hash as authoritative. A verifier must bind to the selected filename and raw-byte hash, rather than infer authority from a title string.

The delegation states that the workspace initially contained only a compact policy and a startup prompt, that Git was initialized on `main` without commits, and that the selected policy was copied byte-for-byte. Those facts were inputs to this review, not independently established from repository inspection, because the blind-pass evidence boundary permits only the authoritative policy. No claims about current branch, HEAD, tree contents, bootstrap files, or copy provenance are therefore independently verified here.

Mandate inputs are pending. No approved Mandate, approved Numerical Risk Budget, approved material decision, validation result, or production authorization was provided as evidence.

## Independent conclusion

The policy gives a strong fail-closed target, but the startup contract is not self-authenticating. The largest Phase 0 hazard is circular trust: a bootstrap program can create `START_HERE`, `DECISIONS`, `TEST_STATUS`, and related records and then pass because those same newly created records say that it should pass. Presence, syntactic validity, or internal agreement cannot prove user approval, validation, or provenance.

The future verifier should be a narrow state checker. It may establish that files and recorded state are internally consistent with a trusted policy pin and observed Git state. It cannot establish that investment semantics are sound, that a risk budget was approved, that tests or OOS/shadow validation passed, or that production use is authorized. Every such assertion needs independent evidence with provenance or must remain a blocking status.

The bootstrap and certification paths should be separated. A scaffold operation may create missing governance files with explicit pending or unverified values. It must then stop with a non-ready result. A subsequent verification operation should read without mutating and must still fail closed until external decisions and evidence satisfy the required gates. Creation and certification in the same pass would defeat the policy's approval and validation boundaries.

## Required blockers

The following conditions must prevent startup from proceeding into investment work or any production-output path. Several are valid normal states for a fresh repository, but none may be silently converted to PASS.

### P0 — policy identity and trust

1. **Missing, unreadable, non-regular, or out-of-root policy file.** The active policy must resolve inside the repository and be read as a regular file. Symlinks/reparse points escaping the repository must fail.
2. **Raw-byte hash mismatch.** Hash comparison must use the original bytes. Newline conversion, Unicode normalization, trimming, or decoding/re-encoding before hashing is forbidden.
3. **Policy pin absent or untrusted.** On first bootstrap there is no `START_HERE` record to trust. The expected filename and hash must come from an explicit bootstrap input with recorded provenance. A hash discovered from the same file being checked is not a trust anchor.
4. **Multiple active-policy declarations or ambiguous candidate selection.** Coexisting historical policy files are permissible only if exactly one active path/hash is declared. Filename heuristics such as "highest version" or "Final" must not choose authority.
5. **Recorded/current mismatch.** After bootstrap, any mismatch between the active filename/hash and `START_HERE` must produce `POLICY VERSION CHANGED`, force a complete policy reread and impact review, and prevent normal continuation.
6. **Incomplete/read-error policy parsing.** A matching hash proves identity, but startup must also demonstrate that the full file was readable. Decode error, short read, or partial streaming failure must fail.

### P0 — approval and decision provenance

7. **Mandate incomplete or unapproved.** At minimum, horizon, base currency, nominal/real treatment, pre-/after-tax treatment, contribution/withdrawal assumption, Eligible Benchmark, and approved Passive Market Implementation(s) must be explicit before an approved Mandate can be claimed.
8. **Numerical Risk Budget pending, provisional, inconsistent, or lacking explicit production activation.** Research presets are `PROVISIONAL / NOT APPROVED`. They must never become personalized or production limits through default selection, age inference, copied examples, or bootstrap convenience.
9. **Approval inferred from metadata authorship or file existence.** `approved_by`, timestamps, checked boxes, status words, or signatures generated by the bootstrapper are not approval evidence. Unknown approval provenance is a blocker.
10. **Material decisions absent or internally conflicting.** Objective, Mandate, risk semantics, portfolio method, uncertainty-set roles, and trading semantics must be identifiable in `DECISIONS.md` before dependent implementation is treated as frozen.
11. **Material design lacks the required pre-implementation review and decision freeze.** A file saying "reviewed" is insufficient without review identity, scope, referenced decision version/hash, outcome, limitations, and immutable or Git-addressable evidence.

### P0 — false readiness and unsafe continuation

12. **Any unsupported readiness claim.** Missing evidence for any material §18 condition must yield `NOT PRODUCTION READY`; indeterminate is not PASS.
13. **Validation records without executable evidence.** `TEST_STATUS` cannot elevate `not run`, missing exit status, missing tested revision, stale result, or an unbound pasted summary into PASS.
14. **OOS/shadow/model-validation claims during Phase 0.** These claims are categorically unsupported by the present evidence and must remain not performed or not verified.
15. **HANDOFF/Git disagreement.** Branch, commit, and changed-file claims must be compared with observed Git state. In an unborn repository, the explicit sentinel `UNBORN_HEAD` (or an equally unambiguous schema value) must be used; fabricating a commit ID is forbidden.
16. **Dirty or changed state hidden by startup.** The verifier must report it. It must not reset, clean, amend, commit, rewrite, or otherwise repair Git state.
17. **Bootstrap mutation during verification.** Verify mode must be read-only. Missing files should produce a structured bootstrap-required failure, not be auto-filled and certified.
18. **Unknown/invalid status token coerced to success.** Parsers must use allowlists and fail closed. Truthy strings, absent keys, comments, or natural-language guesses must not map to approval.

### P1 — provenance and documentation integrity

19. **Required governance files missing, empty, duplicated by case, or outside their canonical paths.** Windows case-insensitive collisions and alternate path spellings need explicit checks.
20. **`START_HERE`, `HANDOFF`, `DECISIONS`, and `TEST_STATUS` refer to different policy, decision, risk-budget, or Git versions.** This is a documentation mismatch and blocks dependent work.
21. **Research ledger syntax or provenance invalid.** Each nonblank JSONL line must parse independently and contain the policy/data/model/prompt/optimizer provenance applicable to that trial. Malformed later lines may not be ignored.
22. **Append-only provenance claimed without a prior anchor.** A current-file scan cannot prove that history was never edited. Until Git history, a signed/anchored prior digest, or an explicit hash-chain design exists, append-only integrity is `NOT VERIFIED`.
23. **Secrets or credentials detected in governance/source files.** Detection should block and report location without echoing the secret value.
24. **Documentation repair hides a mismatch.** A program must report stale state before offering a separate repair operation. Rewriting the record to match current state erases evidence of drift.

## Dangerous bootstrap shortcuts to reject

- Computing the "expected" hash from the selected policy and immediately comparing the file to itself.
- Trusting the policy's filename or Markdown title without a separately supplied expected hash.
- Normalizing CRLF/LF or Unicode before hashing and thereby accepting byte-different content.
- Selecting among multiple policies by version-number sorting, modification time, or a `Final` suffix.
- Copying Mandate, risk limits, statuses, or terminology from AutoScreener or any other repository.
- Treating `BALANCED_RESEARCH_V1` or `GROWTH_RESEARCH_V1` as an approved or personalized budget.
- Populating `approved_by` with the executing user, agent, hostname, or current model.
- Equating a generated file, nonempty Markdown section, or `PASS` word with evidence.
- Letting `--force`, an environment variable, or a lenient mode convert a blocker into success without a separately governed override record.
- Updating `START_HERE` or `HANDOFF` before reporting that the old record disagreed with Git or policy state.
- Inventing a commit hash for an unborn `main` branch, or treating an unborn branch as a Git error that requires an empty commit.
- Running network calls, fetching remote refs, installing dependencies, or invoking an LLM inside the startup verifier. Offline behavior must be deterministic.
- Executing repository code, importing project modules, loading plugins, or evaluating Markdown/front matter while verifying governance state.
- Following symlinks/reparse points outside the repository or accepting path traversal in configured paths.
- Parsing approval with substring checks such as `"APPROVED" in value`; this misclassifies `NOT APPROVED`.
- Catching broad exceptions and returning zero, warning-only, or a generic healthy state.
- Making scaffold creation and verification one atomic "success" action. A successful scaffold means files were created, not that governance passed.
- Using a passing verifier as evidence for forecast correctness, risk-limit calibration, OOS integrity, shadow performance, or production readiness.

## Minimum contract for a future stdlib-only offline verifier

The implementation should use only deterministic local reads and Python standard-library facilities. Calling the installed Git executable through `subprocess` is acceptable if the executable and command failures are surfaced; importing or executing repository code is not.

### Inputs

The verifier needs explicit, non-inferred inputs:

- repository root
- active policy relative path
- expected raw SHA-256
- operation mode: `scan`, `scaffold`, or `verify`
- schema version for machine-readable governance fields
- optional expected decision/risk-budget version only when supplied by an approved external decision

Secrets, production credentials, portfolio holdings, and external service access are unnecessary for Phase 0 startup verification.

### Outputs

It should emit one deterministic machine-readable report to stdout and a concise human summary to stderr or a documented alternate stream. The report should include:

- verifier version
- UTC observation time
- repository root after canonical resolution
- policy path, observed hash, expected hash, byte count, and full-read result
- Git availability, repository root, branch state, HEAD or `UNBORN_HEAD`, and dirty-state summary
- required-file results
- parsed governance versions/statuses and provenance references
- findings with stable codes, severity, policy section, and evidence path
- overall startup state
- explicit capability limits: `investment_model_validated=false`, `oos_validated=false`, `shadow_validated=false`, `production_ready=false` unless a later, separately scoped verifier can prove every gate

Exit status must be nonzero for policy mismatch, parse/integrity failure, inconsistent records, unsafe paths, or unsupported approval/readiness claims. A fresh-repository `scan` may use a distinct nonzero `BOOTSTRAP_REQUIRED` exit code so automation can distinguish an expected missing scaffold from corrupt state.

### Separation of operations

1. **Scan:** read-only inventory and falsification. It discovers current state and reports blockers.
2. **Scaffold:** creates only missing canonical files, using explicit pending values such as `NOT VERIFIED`, `RISK BUDGET NOT APPROVED`, and `NOT PRODUCTION READY`. It must not overwrite an existing file. It ends by reporting that verification is still required.
3. **Verify:** read-only consistency and provenance check. It never mutates files to make itself pass.

Atomic file creation should use same-directory temporary files, flush/close, and `os.replace` only for files that did not previously exist under the scaffold contract. A pre-existing destination must cause a conflict rather than overwrite. Crash recovery must leave either the prior state or a detectable temporary artifact, never a partially trusted record.

## Minimal falsification test set

These are the minimum negative tests. The verifier passes this review only if each mutation is detected with the expected fail-closed result.

| ID | Adversarial fixture | Required result |
|---|---|---|
| F01 | Flip one byte in the policy | `POLICY VERSION CHANGED`; nonzero exit |
| F02 | Convert LF to CRLF while preserving visible text | hash mismatch; nonzero exit |
| F03 | Supply the file's own computed hash as an implicit expected value | reject missing trusted pin |
| F04 | Add another policy and mark both active in records | ambiguous policy; nonzero exit |
| F05 | Point the policy path through `..`, symlink, or reparse escape | unsafe path; nonzero exit |
| F06 | Truncate the policy after hashing fixture metadata | full-read/hash failure; nonzero exit |
| F07 | Start with no governance files | `BOOTSTRAP_REQUIRED`; no approval/readiness claim |
| F08 | Run scaffold on the fresh repository | files contain pending statuses; overall remains not ready |
| F09 | Run scaffold again | idempotent no-overwrite behavior or explicit conflict; no content loss |
| F10 | Set risk budget to `APPROVED` without approval evidence | reject unsupported approval |
| F11 | Use value `NOT APPROVED` against a substring parser | remain unapproved |
| F12 | Omit one minimum Mandate field | Mandate incomplete; block dependent work |
| F13 | Mark `PRODUCTION READY` while any §18 item is unknown | reject claim; `NOT PRODUCTION READY` |
| F14 | Record a fabricated commit in an unborn repository | mismatch; explicit `UNBORN_HEAD` required |
| F15 | Change Git HEAD after recording handoff | `HANDOFF MISMATCH`; nonzero exit |
| F16 | Make the worktree dirty after recording a clean state | mismatch/report dirty state; no cleanup |
| F17 | Corrupt the last JSONL line | ledger invalid; do not ignore tail |
| F18 | Delete or edit a historical ledger line with no anchor | verifier reports append-only integrity not provable; with an anchor, hard fail |
| F19 | Create `DECISIONS.md` and `decisions.md` collision | ambiguous canonical file; nonzero exit |
| F20 | Replace a required file with a directory, device, or external link | invalid file type/path; nonzero exit |
| F21 | Put an unknown status such as `APPROVEDISH` in a required field | schema error; nonzero exit |
| F22 | Make `TEST_STATUS` claim PASS without revision/command/result evidence | unsupported validation claim; nonzero exit |
| F23 | Raise an I/O, decode, Git, or JSON exception | explicit error finding and nonzero exit |
| F24 | Run verify twice on unchanged inputs | byte-equivalent semantic report except documented observation time; no repository mutation |

Positive-path tests remain narrow:

- Exact policy bytes and trusted hash agree.
- All canonical paths are inside the repository and unambiguous.
- An unborn Git repository is represented honestly.
- Fresh scaffold files parse and retain pending/unverified states.
- A fully consistent research-only bootstrap may reach `GOVERNANCE STARTUP VERIFIED` while still remaining `RISK BUDGET NOT APPROVED` and `NOT PRODUCTION READY`.

## What the verifier cannot prove

Even a correct startup verifier cannot prove the truth of human approvals, the economic soundness of decisions, provider PIT semantics, security-master quality, model calibration, uncertainty-set validity, portfolio feasibility, locked OOS integrity, shadow success, or production safety merely by reading status files. It can verify that evidence references exist and are internally bound to versions/hashes. Separate domain review and validation must evaluate the underlying evidence.

The verifier also cannot prove append-only research history from a single current snapshot. That requires a prior trust anchor such as reviewed Git history or a deliberately designed digest chain. The design should state this limitation rather than advertise immutable provenance prematurely.

## Gates for the forthcoming comparative design review

The later design should be rejected or returned for revision if it does not specify:

1. the first-bootstrap trust anchor for policy filename/hash;
2. distinct scan, scaffold, and verify semantics;
3. exact schemas and allowlisted statuses for machine-read fields;
4. non-overwriting and crash-safe file behavior;
5. honest unborn-HEAD handling and read-only Git reconciliation;
6. approval provenance that the verifier cannot self-issue;
7. AND-based readiness logic with unknown treated as failure;
8. deterministic exit codes and a structured report;
9. path-containment and Windows case/reparse-point defenses;
10. a negative-test matrix at least as strong as F01–F24;
11. explicit limits on what Phase 0 verification proves; and
12. no inherited project semantics, production claims, OOS claims, or fabricated approvals.

Until those gates are satisfied and the subsequent design has completed the required pre-implementation review and decision freeze, implementation of the startup verifier should not be treated as approved design execution.
