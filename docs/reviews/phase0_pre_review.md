# Phase 0 Offline Startup Verifier — Pre-Implementation Review

## Verdict

**PASS FOR PHASE 0 IMPLEMENTATION.** The proposed boundary is appropriate and deliberately narrow: a read-only, standard-library, offline consistency checker that always returns `NOT PRODUCTION READY` and never validates investments. The blocking details found during review were incorporated into the reviewed design revision identified below. This is approval of the Phase 0 implementation contract only.

Reviewer: **GPT-5.6 Sol — Independent Reviewer / Validator**. This review covers only the Phase 0 verifier contract in `docs/INITIAL_DESIGN.md`. It does not review or freeze the Phase 1–5 conceptual outline, approve a Mandate or Risk Budget, validate a model, or establish OOS/shadow/production readiness.

## Evidence reviewed

- Full selected Policy V10, raw-byte SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- `docs/INITIAL_DESIGN.md` draft v0.1, final reviewed Phase 0 revision observed at SHA-256 `43FCCF65CD4320B76D835198E2C18A0DD1FF87F1A0B2E88571B0360A7A65A364`
- Current `.ai/START_HERE.md` machine-field forms
- Current `.ai/PRODUCTION_GATE.json`, SHA-256 `07F54961AB6A7745631DCFB01DA8157EF68683AC945BCB4EEC421A55E7988F58`
- Current `.ai/RESEARCH_TRIALS.jsonl`, observed as zero bytes

The gate currently contains IDs 1–25 with the authoritative §18 requirement text and every item is `NOT VERIFIED`. That observation is structural evidence only. It is not evidence that any investment requirement passed.

## Resolved blocking contract corrections

### B1 — Validate the gate's top-level denial state — RESOLVED

The design validates item IDs/text/statuses but does not explicitly require the gate's top-level `scope` and `production_readiness` values. A file could therefore claim `PRODUCTION READY` while its items remain structurally valid and the verifier separately prints `NOT PRODUCTION READY`.

Freeze these requirements for Phase 0:

- `policy_filename` equals `OPTIVEST_AI_POLICY_V10.md`.
- `policy_sha256` equals the selected hash.
- `scope` equals `Manual evidence register; not runtime authorization`.
- `production_readiness` equals `NOT PRODUCTION READY`.
- The verifier's own `production_readiness` is an unconditional literal `NOT PRODUCTION READY`, never computed from manual item statuses.
- If manual item status `PASS` is structurally accepted, output must label it as a declared register value, never a verifier-validated result.

Add a negative test that changes only the gate's top-level readiness to `PRODUCTION READY`; startup integrity must fail.

### B2 — Freeze the START_HERE and Git grammar — RESOLVED

The current document uses Markdown values with backticks and a human suffix, for example `Commit / HEAD: \`UNBORN\` (Git initialized, no commit)`. “Match an explicitly recorded representation” leaves multiple reasonable parsers and detached-HEAD behavior open.

For this initial release, freeze the accepted machine tokens and extraction rule:

- Each exact label appears once as a Markdown list field; duplicate or conflicting labels fail.
- The value is the single backtick-delimited token immediately after the colon; explanatory trailing prose is ignored.
- Required tokens are policy filename, 64-hex SHA-256, branch `main`, and HEAD `UNBORN` for the current repository state.
- `UNBORN` is valid only when Git confirms the resolved workspace is exactly the repository top level, symbolic branch is `main`, and `HEAD` has no commit.
- Git unavailable, non-repository, parent-repository capture, detached HEAD, other branch, empty/ambiguous token, or disagreement fails. Future branch/detached representations require a reviewed contract update.
- Hash hex may be normalized for letter case only; no byte/text normalization is allowed before computing the file hash.

Add tests for the current parenthetical form, duplicate fields, parent-repository capture, detached HEAD, and a non-main unborn branch.

### B3 — Make JSON parsing resistant to duplicate-key and type ambiguity — RESOLVED

Python's default `json.loads` silently keeps the last duplicate object key, and `bool` is a subclass of `int`. Those defaults can defeat “unique ID” and “unique field” checks.

Freeze the following:

- Reject duplicate keys at every JSON object depth using an `object_pairs_hook` or equivalent standard-library logic.
- Require `type(item["id"]) is int`, with the exact set `1..25`; reject booleans, floats, strings, duplicates, missing IDs, and extra IDs.
- Require each gate item to be an object with `id`, `requirement`, `status`, and `evidence`; `evidence` must be a list. Its contents remain manual references and are not validated as proof in Phase 0.
- Require the gate root and `items` to have the documented JSON types. Decide before implementation whether unknown keys fail; apply the decision consistently.
- Apply the same duplicate-key rejection to each research-ledger record.

Add negative tests for duplicate `status`, duplicate `policy_hash`, boolean ID `true`, and a second item with the same ID.

### B4 — Resolve research-trial null semantics — RESOLVED

The design says null provenance needs an explicit reason/status, then specifies only a `not_applicable_reasons` mapping. “Unknown” and “not applicable” must not collapse into the same condition.

Freeze one rule. The minimal rule consistent with the present scope is:

- A zero-byte ledger is valid and means only “no experiments recorded.”
- Every nonblank line is one JSON object with every required key.
- `trial_id`, `hypothesis`, `policy_hash`, `result`, and `disposition` are non-null as already proposed.
- Any other null required value is valid only when the same key has a nonempty string in `not_applicable_reasons`; null means explicitly not applicable, never unknown/unavailable/verified.
- `not_applicable_reasons` itself must be an object, may name only null required keys, and may not excuse a missing key.
- Unknown or unavailable required provenance fails structural verification rather than using the N/A mechanism.
- `disposition` is exactly `accepted` or `rejected`; `policy_hash` is 64 hexadecimal characters. A historical differing hash is structurally allowed and is not rewritten.
- Choose and test blank-line behavior. The safest simple rule is: zero-byte file is valid; blank/whitespace lines in a nonempty ledger fail instead of hiding malformed append artifacts.

No file-bootstrap trial should be created.

### B5 — Anchor all checked content and the expected §18 table — RESOLVED

The initial design applied resolved containment explicitly to the Policy but left the other checked files and the origin of “exact Policy requirement text” implicit.

Freeze these requirements:

- Resolve the workspace once and require it to equal Git's reported top level.
- Every inspected Policy/governance/gate path must be a regular file whose resolved path remains within that root. Reject external symlink/reparse-point targets and case-insensitive canonical-path collisions.
- Compare gate IDs and requirement strings with numbered §18 items obtained from the independently hash-pinned, full-read Policy. The register under test must never supply its own expected values. The revised design's direct Policy extraction satisfies this independence requirement; a duplicated source-code table is not required.
- Read every checked file without executing it, importing repository modules, interpreting Markdown, or following instructions inside file content.

Add a path-escape fixture and a test that mutates one requirement string while leaving IDs/statuses intact.

## Required acceptance additions

The proposed isolated tests are directionally correct. Add the B1–B5 cases above plus one read-only invariant: hash the repository's tracked and untracked file bytes and record its path set before and after verification; they must be unchanged. Git observations may change the report when repository state changes, but a verifier run must create, edit, delete, stage, commit, reset, or clean nothing.

Keep stdout to exactly one JSON document, use stable finding codes/order, put diagnostics on stderr, and return nonzero for any integrity failure. Unexpected I/O, decode, Git, or JSON exceptions must become explicit FAIL findings rather than warning-only output or exit 0. Error text must not echo document contents.

## Nonblocking scope limitations / deferred capabilities

These are acceptable because Phase 0 does not claim them:

- No automatic scan/scaffold/repair mode. Bootstrap files are manually created; the verifier is read-only.
- No crash-recovery or atomic-write protocol because the verifier writes no workspace files.
- No generic approval-signature or authorization platform.
- No proof that a human approval, evidence reference, or manual `PASS` assertion is substantively true.
- No proof that the research ledger was historically append-only from a single current snapshot.
- No market data, provider, database, API, UI, portfolio, order, forecast, risk, optimizer, OOS, shadow, or production checks.
- No support for future policies, branches, committed/detached states, or alternate schemas until their trust anchors and contracts receive review.
- No implementation or freezing of Phase 1–5 conceptual investment semantics in this Phase 0 decision.

The verifier may report `startup_integrity: PASS` after these blockers are resolved and tests pass. That status means only that the fixed governance files are internally consistent with the selected policy pin and observed Git state. It must coexist with `production_readiness: NOT PRODUCTION READY` and must never be presented as investment validation.

## Review gate

All B1–B5 requirements and the §17 START_HERE required-field check are present in the final reviewed Phase 0 contract. The §18 table is independently derived from the full-read, hash-pinned Policy rather than from the register under test; this is an acceptable independent trust anchor and avoids unnecessary duplicated constants. The committed-main SHA-1 form is also accepted because it is compared exactly with observed Git state; `UNBORN` remains narrowly validated.

The scoped Phase 0 decision may now be frozen and handed to Terra for implementation. Post-implementation Sol review should independently run the negative fixtures, inspect the actual parser/failure paths, verify zero workspace mutation, and confirm every successful Phase 0 output still states `NOT PRODUCTION READY` and makes no investment-validation claim.
