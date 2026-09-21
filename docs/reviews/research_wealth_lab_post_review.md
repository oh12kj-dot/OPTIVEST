# RESEARCH-WEALTH-LAB-V1 independent post-implementation validation

Date: 2026-09-16, Asia/Tokyo. Reviewer role: GPT-5.6 Sol, independent falsification-first post-review. Target: the current uncommitted implementation under ADR-0018 / D0010.

## Verdict

**`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`**.

The implementation has substantial correct engineering evidence: the frozen authority hashes match, the shipped BASE evaluates, independent W3/W4/W8/W10/W11/MAX arithmetic agrees, the fast/MAX/full suites pass, CLI/library/HTTP success bytes agree, the lab request is DB-read-only, the existing provider/preflight/readiness denials remain intact, and a disposable migration round trip succeeds.

Scoped engineering acceptance is nevertheless blocked. Independent counterexamples reproduce failures in the exact frozen accounting clock, canonical input/hash identity, Decimal calculation, raw decoder, Stage-7 aggregation, provenance/authority sequencing, CLI/HTTP contracts and UI. The browser backend is unavailable, so the remaining W18 interactions also stay `NOT VERIFIED`. Green tests do not override these failures.

This verdict is limited to ADR-0018 implementation conformance. It is not investment/model validation and changes no approval state. Literal boundaries remain `RISK BUDGET NOT APPROVED`; investment model, risk feasibility, provider/PIT/tradability, calibration and OOS `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

## Authority and repository identity

- Selected Policy: `OPTIVEST_AI_POLICY_V10.md`, raw SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67` — matched.
- Frozen design: `docs/RESEARCH_WEALTH_LAB_DESIGN.md`, raw SHA-256 `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C` — matched.
- Controlling pre-review: `docs/reviews/research_wealth_lab_pre_review.md`, raw SHA-256 `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83` — matched.
- Repository: branch `main`; HEAD `UNBORN`; 18 untracked paths. `git diff --check` passed but cannot inspect the wholly untracked tree.
- No Policy, design, pre-review, ADR, implementation, test, migration, provider declaration, user database, research trial or production-gate bytes were changed by this review.

## Blocking findings

### B1 — PRE_TRADE state and initial-cost drawdown/recovery are wrong

Priority: **blocking accounting conformance**. Frozen design sections 3, 8/W9 and 8.1/W9d require a common real initial state at PRE_TRADE, then the after-cost alternative at POST_TRADE. The immediate cost must enter sampled drawdown and recovery.

`optivest/wealth_lab.py:756-764` instead builds PRE_TRADE with the alternative's post-trade units and `post_trade_cash + cost`, then initializes the high-water state from POST_TRADE. A BASE-derived alternative with E units `980000` and commission `20000` produced:

```text
sampled_max_drawdown = 0
recovery_episodes = []
PRE_TRADE cash = 20000
PRE_TRADE E value = 980000
```

The frozen oracle is drawdown `.02`, a right-censored episode anchored at `PRE_TRADE` month 0 through month 84, and the common initial E value `1000000` / cash `0`. The terminal wealth/log remain cost-once; the event ledger and path-risk clock do not.

### B2 — canonical Bundle normalization and input identity are not implemented

Priority: **blocking artifact integrity**. Design sections 2.1 and 7 require safe D normalization, trimmed text, semantic-set sorting, and one canonical normalized Bundle shared by `input_sha256` and `Artifact.input`.

`optivest/wealth_lab.py:897-911` hashes the decoded wire tree before validation normalization and preserves semantic array order. Reversing only the alternatives array changed both `input_sha256` and Artifact bytes. Replacing exact cash string `"0"` with equivalent accepted D string `"0.0"` also changed both. A title with surrounding spaces reproduced a stronger self-inconsistency:

```text
evaluation.input_sha256 = 1ba3c78a5b4bd09ee2ab3616abfdce9107942d8752ad82a45641111041d465ec
SHA256(C(artifact.input)) = 74ef852d6be68429ff15a06e87650827d3b512a017e8c544238e81aaaa6ba450
equal = false
```

The artifact contains the trimmed title, but its declared input hash covers the untrimmed tree. The unused `_normal_decimal` is not a safe remedy because its current `rstrip("0")` would turn an integer such as `"20"` into `"2"`.

### B3 — benchmark and convergence arithmetic round before aggregation

Priority: **blocking numerical conformance**. Design section 4 requires the entire log/exp/sum/min/difference payload to be independently recomputed at precision 80 and 120 and compared at 40 significant digits. No aggregation may use public rounded strings.

`optivest/wealth_lab.py:749-754` exposes only a single path-log Decimal from `_numerical_payload`; it is not the frozen full-payload seam. `optivest/wealth_lab.py:882` computes benchmark distribution utility from the already rendered 40-digit `path_log_growth.value`. An independent 120-digit Decimal fixture with equal masses and terminal ratios `175844.747054` and `0.00001` gives:

```text
expected full-precision annual log = 4.031652148162628160354760428880312239657e-2
implementation benchmark output    = 4.03165214816262816035476042888031223965e-2
```

Path CAGR/geometric-equivalent calculations also exponentiate rendered logs (`optivest/wealth_lab.py:782,827,882`). The private invariant seam receives a public Result and only checks it is non-null; it does not independently assert exact rational ledger/fraction/absorption invariants. W14/W19 private-seam acceptance is therefore not established.

### B4 — raw decoder violates closed W1 cases

Priority: **blocking raw-boundary conformance**.

- Escaped lone surrogate input in a valid JSON string returned root `INTERNAL_ERROR`; the frozen result is `JSON_ENCODING`. The raw-text surrogate scan occurs before `json.loads`, so it misses a surrogate created by a `\ud800` escape (`optivest/wealth_lab.py:117-137`).
- A document containing both an over-node subtree and a later over-depth subtree returned `JSON_NODES`. Section 6.1 requires `JSON_DEPTH` before `JSON_NODES` when both apply. Exact reproduction used a root array whose first child was 100,000 scalar zeroes and whose second child was 17 nested arrays; the 200,039-byte request returned `JSON_NODES`.
- The implementation constructs the full `json.loads` tree before enforcing depth/nodes, contrary to the bounded-parser requirement.

The independent max/one-over byte, node-only, depth-only, BOM, malformed syntax and size-helper checks otherwise behaved as specified.

### B5 — Stage-7 terminal-zero findings are not exhaustive

Priority: **blocking deterministic diagnostics**. After an asset first has price zero, a later point with both price `1` and distribution `0.01` must produce two independently applicable findings. `_cross_record_findings` chooses price *or* distribution at `optivest/wealth_lab.py:700`. The exact isolated case returned only:

```json
[{"code":"TERMINAL_ZERO_REVERSAL","path":"/paths/0/months/1/assets/0/price"}]
```

The required distribution pointer was absent. The separate W6b1 and W6b2 tests do not falsify simultaneous aggregation.

### B6 — loaded-source, pre-emission authority and Git provenance are not closed

Priority: **blocking provenance conformance**.

- Loaded hashes are captured lazily on the first invocation (`optivest/wealth_lab.py:722-725`), not when the module/route context initializes.
- There is no Policy/design/manifest recheck immediately before success emission. In a disposable copied source tree, a wrapper mutated `wealth_lab.css` after numerical computation but before return; the invocation still returned `COMPUTED_SYNTHETIC` Artifact. Only the next invocation returned `SOURCE_CHANGED`.
- A copied source tree with no `.git` was labelled `UNBORN`; the frozen contract requires `GIT_NOT_AVAILABLE`. `optivest/wealth_lab.py:726-729` maps every failed/non-40-hex `git rev-parse` outcome to UNBORN.
- `example_bytes()` does no authority/runtime verification. With the Policy hash deliberately mismatched, both the library example and `GET /api/v1/wealth-lab/example` still returned HTTP 200 BASE bytes.

Positive W17 evidence: every one of the ten manifest members returned `SOURCE_CHANGED` when mutated after a captured context; a missing member returned `SOURCE_UNAVAILABLE`; disposable Policy/design mutations returned `POLICY_MISMATCH`/`DESIGN_MISMATCH`; resetting the copied context simulated restart and changed both source hash and Artifact identity.

### B7 — HTTP/CLI failure precedence and closed error identities deviate

Priority: **blocking caller-path conformance**.

- The HTTP route checks media before authority (`optivest/wealth_lab_api.py:26-34`). Bad media returned `CONTENT_TYPE` even with a forced Policy mismatch. Transport failure provenance was null, although stage 3 requires verified provenance.
- HTTP reads `await request.body()` without incremental enforcement of the 4 MiB bound.
- CLI collapses missing, non-regular and unreadable files into `INPUT_FILE_MISSING` (`optivest/cli.py:20-23`). Passing the repository directory returned `INPUT_FILE_MISSING`; the frozen code is `INPUT_FILE_NOT_REGULAR`.
- CLI example bypasses authority via `example_bytes()`, and normal stdout writes are not protected by the frozen one-attempt `OUTPUT_WRITE_FAILED` behavior.

Positive evidence: accepted BASE bytes were byte-identical across library canonical Artifact, HTTP response, and CLI stdout excluding its single LF; CLI success exit was 0 and ordinary invalid-input exit was 2. Media acceptance/rejection for missing, quoted charset, `text/json`, exact OWS form, gzip and identity matched their status/code cases except for the authority/provenance ordering above.

### B8 — UI contract is incomplete and can make an edited result current again

Priority: **blocking W18 conformance plus missing mandatory evidence**.

The page contains only a JSON textarea and raw `<pre>` (`optivest/wealth_lab_api.py:40`). The JavaScript only dumps returned JSON with `textContent` (`optivest/static/wealth_lab.js:4`). It does not implement the frozen alternative/path panels, expandable event ledger, separately labelled base/member/lower-envelope and stress diagnostics, open-recovery/ruin presentation, separate benchmark comparator panel, or structured unavailable-component presentation.

There is also a deterministic stale race. An input edit during an in-flight evaluation calls `setStale()`, but the eventual valid response unconditionally sets `stale=false` and enables Download (`wealth_lab.js:10-12`). The textarea and Load Example button remain active during the request, and there is no request/input revision check. The downloaded Artifact can therefore correspond to older bytes than the visible editor.

The current root browser-control attempt on 2026-09-16 found zero browser backends after the required troubleshooting. Earlier Terra desktop/390px BASE load/evaluate/local-rehash/download evidence is retained only for that narrow success path. Actual stale/in-flight/error/XSS/ruin/download-rejection and structured rendering evidence remains `NOT VERIFIED`; static or Playwright substitution is not accepted.

## Independent oracle results

Expected values were calculated without importing the evaluator:

| Oracle | Independent result | Implementation disposition |
|---|---|---|
| W3 | cash0 `38`; W0 `98`; cash1 `44.8`; asset `66`; W1 `110.8` | exact values reproduced |
| W4 | `ln(.98)/7 = -0.002886101045359921201149328717741769693219...` | terminal cost-once log reproduced; initial drawdown clock fails under B1 |
| W7 | zero-mass ruin omitted; positive mass ruin `-infinity`; nonfinite comparison unavailable | reproduced |
| W8 | correlated utility `0`; offsetting `ln(1.25)/7 = 0.031877650187744250823756441472833500482085...` | reproduced |
| W10 | `(ln(.5)+ln(2))/14 = 0`; geometric equivalent `0` | reproduced |
| W11 | members `+/-ln(2)/14`; sign oracle `+ln(2)/7 = 0.099021025794277901345318874494025224010785...` | alternative fixture reproduced; global numerical contract fails under B3 |
| W14 | exact fractions `1/3`; public sum `1-10^-40` | public output reproduced; private invariant seam not established |
| MAX | 160 alternative paths; 13,760 alternative events; 1,700 benchmark events; 53,760 asset-month-alternative cells | reproduced |

## W1-W19 disposition

| ID | Post-review disposition | Basis |
|---|---|---|
| W1 | **FAIL** | B4 raw surrogate and combined depth/node precedence; B7 caller precedence. |
| W2 | **PASS, scoped** | typed-invalid/missing/dependent-accounting stages and hashes for the exact frozen cases reproduced. |
| W3 | **PASS, scoped** | independent exact cash/distribution/mark values reproduced. |
| W4 | **PASS, scoped** | cost-once terminal log reproduced; B1 is recorded under W9/event accounting. |
| W5 | **PASS, scoped** | funding, cash-only and no-trade rejection/identity cases reproduced. |
| W6 | **FAIL** | separate cases pass, but simultaneous price+distribution reversals are not exhaustively aggregated. |
| W7 | **PASS, scoped** | ruin, zero-mass and tiny-positive behavior reproduced. |
| W8 | **PASS, scoped** | correlated/offsetting wealth, utility and drawdown reproduced. |
| W9 | **FAIL** | initial-cost PRE/POST drawdown and recovery episode are wrong. |
| W10 | **PASS, scoped** | geometric-not-arithmetic fixture reproduced. |
| W11 | **PASS exact fixture / FAIL global numerical contract** | sign oracle passes; B3 rounds benchmark path logs before aggregation. |
| W12 | **PASS, scoped** | stress remains separate/unweighted; no binding promotion. |
| W13 | **PASS, scoped** | closed result has no rank/action/weight and retains unavailable alternatives. |
| W14 | **FAIL** | public representation passes; exact private invariant seam is a no-op over public Result. |
| W15 | **PASS, scoped** | success bytes agree; lab request is DB-read-only; provider/preflight/readiness denials remain. |
| W16 | **PASS, scoped** | disposable downgrade/upgrade/seed round trip reached `0003_research_risk_editor`, 33 application tables. |
| W17 | **FAIL** | B2/B6/B7 canonical/provenance/authority/Git failures. |
| W18 | **FAIL / NOT VERIFIED** | B8 static contract/race failures and mandatory browser evidence unavailable. |
| W19 | **FAIL** | MAX and size helpers pass; B3/B4/private-seam requirements fail. |

## Commands and evidence

- `uv run pytest -q tests/test_wealth_lab.py -k "not maximum_dimensions" --tb=short` -> **64 passed, 1 deselected in 7.40s**.
- `uv run pytest -q tests/test_wealth_lab.py -k maximum_dimensions -s --tb=short` -> **1 passed, 64 deselected in 37.20s**; evaluator elapsed `34.314532s`; peak `110,912,802` bytes; Evaluation `14,036,616` bytes; Artifact `14,550,059` bytes. The frozen `>10s` review trigger fired; coverage was not reduced.
- `uv run pytest -q --tb=short` -> **200 passed, 2 skipped, 2 known dependency warnings in 98.52s**.
- `uv run python -m py_compile optivest/wealth_lab.py optivest/wealth_lab_api.py optivest/cli.py optivest/app.py` -> exit 0.
- `node --check optivest/static/wealth_lab.js` -> exit 0.
- `uv run python scripts/verify_startup.py --root .` -> `startup_integrity=PASS`, findings empty, main/UNBORN/dirty, `NOT PRODUCTION READY`.
- `git diff --check` -> exit 0/no output, with the explicit wholly-untracked limitation.
- Disposable SQLite: `upgrade head -> seed -> lab POST -> exact all-table count comparison` yielded HTTP 200/`COMPUTED_SYNTHETIC` and identical maps; `downgrade base -> upgrade head -> seed` ended at revision `0003_research_risk_editor`, 33 application tables. Provider dataset route returned 403 `BLOCKED_POLICY`; decision preflight returned 201 with `eligible_for_research_decision=false`; status remained `NOT PRODUCTION READY` and `RISK BUDGET NOT APPROVED`. `.ai/RESEARCH_TRIALS.jsonl` bytes were unchanged.
- Exact parser helpers: 100,000-node root passed decode then failed Bundle type; 100,001 nodes returned `JSON_NODES`; BASE padded to 4,194,304 bytes computed; one more byte returned `JSON_SIZE`; Evaluation/Artifact bounds accepted equality and returned `RESULT_SIZE`/`ARTIFACT_SIZE` at one-over.
- Adversarial scripts in this review used only disposable directories/databases or in-process monkeypatches; original authority/source bytes were not mutated.

## Required bounded correction and recheck

1. Build one closed normalized Bundle after Stage 5: safely normalize every D and text, sort every specified semantic set, preserve time arrays, and use that same object for the hash, evaluation and Artifact input. Add the permutation, `0`/`0.0`, and trimmed-text hash-equality counterexamples.
2. Pass the common initial positions/cash into path materialization. Process PRE_TRADE then POST_TRADE through the exact drawdown/recovery state machine; add exact W9d and PRE_TRADE position/fraction assertions.
3. Implement the full 80/120 numerical payload and compare all derived outputs before emission. Retain unrounded Decimal values through benchmark/alternative sum, exp, minima and difference. Make the private exact invariant seam substantive and add the benchmark counterexample above.
4. Reject escaped lone surrogates as `JSON_ENCODING`, guarantee global depth-before-node precedence with bounded parsing, and add the combined-limit fixture.
5. Emit both independent terminal-zero findings when both fields reverse.
6. Capture loaded source identity at module/route initialization, recheck Policy/design/manifest immediately before emission, distinguish Git unavailable/corrupt/no-repository from a verified unborn repo, and apply authority checks to example/capabilities and all transports.
7. Enforce authority-before-media/acquisition, verified provenance on stage-3 failures, incremental HTTP/file byte bounds, distinct CLI file codes and the output-write contract.
8. Implement the frozen structured UI and an input/request revision guard. Disable or version editor/example interactions during evaluation. After correction, obtain actual desktop and 390px browser evidence for BASE, W2, W6c, stale/in-flight/error/XSS/ruin/rehash/download rejection.
9. Add permanent tests for each counterexample, rerun focused/MAX/full/static/migration/no-write/source-copy evidence, then request one independent Sol recheck.

These are implementation corrections within the existing exact freeze. If a correction changes input support, formulas, event order, numerical method, bounds, provenance, persistence, statuses or UI contract rather than conforming to the frozen design, return `DESIGN CHANGE REQUIRED` and renew Astra/Sol review.

## Completion report

- Changed: this independent report and factual `.ai` operational state only.
- Why: mandatory post-implementation falsification found blocking deviations despite green tests.
- Evidence/tests/results: listed above.
- Validation status: `IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`; no `PASS_ENGINEERING_RESEARCH_WEALTH_LAB`.
- Remaining issues/model limitations: B1-B8 and actual-browser W18 evidence; all deferred forecast/risk/provider/OOS/shadow/Production work remains outside this slice.
- Design deviations: **PRESENT in implementation**; the frozen design/ADR bytes remain unchanged.
- Handoff: Terra performs one bounded correction pass; Sol rechecks the exact counterexamples and full acceptance matrix.

## 2026-09-17 independent Sol recheck after the bounded B1-B8 correction

### Recheck verdict

**`IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED`**. No `PASS_ENGINEERING_RESEARCH_WEALTH_LAB` is issued.

The correction closes B1-B5, B7, and the static/non-browser part of B8 under independent reproduction. It also closes the original evaluation-path portion of B6: the loaded context is captured at module initialization, a source change before the first evaluation and a change during evaluation both fail as `SOURCE_CHANGED`, Git unavailable and verified-unborn states are distinct, and Policy authority applies to the example.

One blocking B6/W17 deviation remains. Frozen design section 7 requires source hashes to be read at each invocation **and again just before emission**. `example_bytes()` and `capabilities()` each invoke `_provenance()` only once (`optivest/wealth_lab.py:1134-1142`). In a disposable copied source context, the real `_provenance()` completed successfully and a wrapper then changed copied `optivest/static/wealth_lab.css`. Both GET surfaces still emitted success:

```text
GET /api/v1/wealth-lab/example      -> HTTP 200, 17,975 bytes, provenance calls=1
GET /api/v1/wealth-lab/capabilities -> HTTP 200,  4,645 bytes, provenance calls=1
expected after the copied manifest change: SOURCE_CHANGED / HTTP 503
```

The copied source was temporary; repository source bytes were not mutated. This is a deterministic pre-emission race, not a claim that a normal static request changed files. The evaluation POST does perform its second check and returned the required root `SOURCE_CHANGED` in the equivalent mutation probe.

Actual-browser W18 remains independently blocking and `NOT VERIFIED`. The current root browser attempt exposed no backend after required troubleshooting. Static inspection/tests confirm structured panels, safe `textContent`/`createElement` rendering, no `innerHTML`, and input/request revision guards, but those do not substitute for actual desktop and 390px BASE/W2/W6c/stale/in-flight/error/XSS/ruin/rehash/download-rejection behavior. Therefore W18 is **not** the only blocker: B6/W17 also remains open.

This remains an implementation-conformance verdict only. `RISK BUDGET NOT APPROVED`; investment model, risk feasibility, provider/PIT/tradability, calibration and OOS remain `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

### B1-B8 recheck disposition

| Finding | Recheck | Independent evidence |
|---|---|---|
| B1 PRE/POST cost clock | **CLOSED** | Common PRE_TRADE wealth/cash/holding `1e6/0/1e6`; POST wealth `9.8e5`; drawdown `2e-2`; one PRE_TRADE-anchored right-censored episode through month 84. |
| B2 normalized identity | **CLOSED** | Semantic-set permutations, `0` versus `0.0`, and padded text produced identical 201,850-byte Artifacts; `input_sha256=SHA256(C(Artifact.input))`; integer D `20` remained `20`. |
| B3 precision/invariants | **CLOSED** | Benchmark counterexample exactly `4.031652148162628160354760428880312239657e-2`; private 80/120 payload included log/exp/min/difference; a 120-only injected difference failed `NUMERICAL_NOT_VERIFIED`; exact ledger seam is substantive. |
| B4 bounded raw decoder | **CLOSED** | Escaped lone surrogate returned `JSON_ENCODING`; the 200,039-byte combined 100,000-node/17-depth input returned `JSON_DEPTH`; lexical bound scan precedes tree construction. |
| B5 simultaneous reversals | **CLOSED** | Both distribution and price `TERMINAL_ZERO_REVERSAL` pointers were returned in deterministic order. |
| B6 source/Git/example | **FAIL** | Evaluation load/pre-emission changes, Git states, and initial example authority pass; example/capabilities omit the mandatory second pre-emission source check and return HTTP 200 after the exact copied-source mutation above. |
| B7 HTTP/CLI | **CLOSED** | Authority precedes media; stage-3 failures include provenance; 4 MiB is incrementally bounded; success bytes are canonical; CLI missing/nonregular/unreadable codes and exits, restart identity, LF contract, and `OUTPUT_WRITE_FAILED` exit 1 pass. |
| B8 UI | **STATIC CLOSED / BROWSER NOT VERIFIED** | Structured alternative/benchmark/unavailable panels, event/recovery/ruin labels, safe DOM construction, and revision guards are present. Mandatory actual-browser behavior is unavailable, so W18 cannot pass. |

Independent raw-boundary follow-up also reproduced RFC-6901 duplicate pointer `/x~1y/0/a~0b`, six simultaneous nested Stage-5 findings without descending an unknown container, four Stage-6 missingness findings with hash/provenance, and four deterministic Stage-7 cross-record findings with hash/provenance.

### Numerical and maximum-fixture recheck

Expected values were recalculated with standard-library `Fraction`/`Decimal`, not evaluator formulas. Current output reproduced W3 cash/wealth `38/44.8/66/110.8` on the scaled fixture; W4 `ln(.98)/7`; W7 exact zero versus positive one-dollar terminal state; W8 correlated utility zero and offsetting `ln(1.25)/7`; W10 geometric rather than arithmetic aggregation; W11 separate-minimum difference `ln(2)/7 = 9.902102579427790134531887449402522401079e-2`; and W14 three public 40-digit thirds summing to `1-10^-40`. MAX cardinalities remain independently `160` alternative PathResults, `13,760` alternative events, `1,700` benchmark events, and `53,760` asset-month-alternative cells.

The MAX test measured evaluator time `36.962977s`, peak `106,717,753` bytes, Evaluation `14,040,496` bytes and Artifact `14,553,939` bytes. The frozen `>10s` engineering review trigger remains observable; memory is below the 256 MiB trigger. The bounded full-result construction and recorded trigger were inspected without reducing coverage. This is not a concurrency, throughput, deployment or Production capacity claim and is not an additional conformance blocker.

### Exact commands and operational evidence

- Baseline raw hashes before this dated addendum: Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; frozen design `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`; controlling pre-review `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83`; prior post-review `EEF7BF9D550AC4F615904FEABBBDD5EA33F37DB041C235B81AD3BF1346FF520B`. All matched. Branch `main`, HEAD `UNBORN`, 18 untracked root paths.
- `uv run pytest -q tests/test_wealth_lab.py -k "not maximum_dimensions" --tb=short` -> **72 passed, 1 deselected, 2 known dependency warnings in 18.70s**.
- `uv run pytest -q tests/test_wealth_lab.py -k maximum_dimensions -s --tb=short` -> **1 passed, 72 deselected, 2 known dependency warnings in 40.37s**; exact measurement above.
- `uv run pytest -q --tb=short` -> **208 passed, 2 skipped, 2 known dependency warnings in 110.85s**.
- `uv run python -m py_compile optivest/wealth_lab.py optivest/wealth_lab_api.py optivest/cli.py optivest/app.py`, `node --check optivest/static/wealth_lab.js`, startup verifier, and `git diff --check` all exited 0. Startup findings were empty and reported main/UNBORN/dirty plus `NOT PRODUCTION READY`. The tracked diff check retains its wholly-untracked limitation; explicit relevant-file trailing-whitespace inspection was empty.
- Independent HTTP probes: authority mismatch plus bad media returned Policy failure 503; bad media/encoding and one-over-4-MiB returned 415/415/413 with provenance; BASE returned exact canonical Artifact bytes and a valid independent rehash.
- Independent CLI probes: BASE twice across fresh processes returned identical 201,851 bytes including the one LF and exit 0; missing/nonregular/unreadable/misuse returned their distinct codes and exit 2; a closed stdout pipe returned exit 1 and `OUTPUT_WRITE_FAILED` on stderr.
- Disposable SQLite `upgrade head -> service/Phase2 seed -> lab POST` returned HTTP 200/`COMPUTED_SYNTHETIC`; exact row-count maps across 32 application tables and 43 rows were unchanged by the POST. Provider datasets stayed 403 `BLOCKED_POLICY`; preflight returned 201 with `eligible_for_research_decision=false`; status remained `NOT PRODUCTION READY` and `PROVISIONAL / RISK BUDGET NOT APPROVED`. `downgrade base -> upgrade head -> seed` returned revision `0003_research_risk_editor` with the same 32 application tables. The temporary DB was removed.
- `.ai/RESEARCH_TRIALS.jsonl` remained zero bytes with SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

### Required bounded continuation

1. In `example_bytes()` and `capabilities()`, re-read Policy/design/manifest against the loaded invocation context immediately before returning success. A copied manifest mutation after the first check must return root `SOURCE_CHANGED`; the HTTP routes must emit canonical failure Evaluation with status 503. Add permanent library and GET counterexamples without adding a public bypass.
2. Rerun the B6 copied-source probes, focused/MAX/full/static/startup/hash/diff and disposable no-write/migration evidence. Request one independent Sol recheck.
3. When a genuine browser backend is available, run the complete actual desktop/390px W18 matrix. Until then, keep W18 `NOT VERIFIED` and do not substitute static or Playwright evidence.

No implementation/test/frozen authority/ADR/model/service/risk-editor/Phase2/migration/dependency/lock/provider/user-database/trial/production-gate file was changed by this recheck. Only this review addendum and factual `.ai` operational records were updated.

## 2026-09-20 final independent Sol B6/W17 recheck

### Controlling scoped disposition

**`PASS_ENGINEERING_RESEARCH_WEALTH_LAB_NON_BROWSER`** for the frozen non-browser engineering contract only. The residual B6/W17 copied-source race is independently closed. There is no remaining known non-browser implementation blocker in the applicable acceptance matrix.

This is deliberately not `PASS_ENGINEERING_RESEARCH_WEALTH_LAB`. Mandatory actual-browser W18 remains `NOT VERIFIED`: no genuine browser backend was used for desktop/390px BASE, W2, W6c, stale/in-flight/error/XSS/ruin/rehash/download-rejection or structured-rendering interaction. Static DOM/JavaScript tests do not substitute for that evidence. Full all-surface engineering acceptance therefore remains pending W18, without treating the unavailable browser as a reproduced implementation failure.

The disposition is implementation conformance only. It establishes no forecast, model, risk, provider, PIT/tradability, calibration, OOS, shadow or Production gate. `RISK BUDGET NOT APPROVED`; relevant investment/model/provider items remain `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

### Residual B6/W17 independent falsification

The reviewer inspected `example_bytes()`, `capabilities()`, the HTTP wrappers and the permanent copied-source regressions before execution. Both GET-producing library functions now call the real provenance collector before work and again immediately before returning success; both HTTP routes convert a resulting `LabError` into the canonical failure Evaluation and HTTP 503.

An additional one-off probe, independent of the pytest assertions, created a fresh disposable authority/source copy for each of four paths: library example, HTTP example, library capabilities and HTTP capabilities. In every invocation a wrapper first allowed the real provenance check to complete cleanly, then appended one inert byte to copied `optivest/static/wealth_lab.css`. The second real check ran in the same invocation (`calls=2`) and returned `SOURCE_CHANGED`. Both HTTP cases returned 503 with status `INTERNAL_ERROR`, finding `[{"code":"SOURCE_CHANGED","path":""}]`, and null provenance/input hash/result. No repository manifest or authority byte was mutated.

This closes the exact residual from the preceding dated section. The four permanent regressions also pass and require two provenance calls. Evaluation-path load/pre-emission mutation, Git unavailable/verified-unborn separation, Policy/design mismatch, source unavailable, restart identity, canonical Artifact parity and CLI/HTTP contracts retain the independently passed prior disposition.

### Automated and static evidence

- `uv run pytest -q tests/test_wealth_lab.py -k "not maximum_dimensions" --tb=short` -> **76 passed, 1 deselected, 2 known dependency warnings in 20.94s**.
- `uv run pytest -q tests/test_wealth_lab.py -k maximum_dimensions -s --tb=short` -> **1 passed, 76 deselected, 2 known dependency warnings in 51.66s**. The evaluator measured `47.823778s`, peak `106,716,617` bytes, Evaluation `14,040,496` bytes and Artifact `14,553,939` bytes. Exact dimensions remain 160 alternative PathResults, 13,760 alternative events, 1,700 benchmark events and 53,760 asset-month-alternative cells. The frozen elapsed-time review trigger remains recorded; the memory trigger did not fire.
- `uv run pytest -q --tb=short` -> **212 passed, 2 skipped, 2 known dependency warnings in 127.78s**.
- `uv run python -m py_compile optivest/wealth_lab.py optivest/wealth_lab_api.py optivest/cli.py optivest/app.py` and `node --check optivest/static/wealth_lab.js` -> exit 0.
- `uv run python scripts/verify_startup.py --root .` -> `startup_integrity=PASS`, findings empty, branch `main`, HEAD `UNBORN`, 18 untracked root paths and `NOT PRODUCTION READY`.
- `git diff --check` and an explicit relevant-file trailing-whitespace scan -> no findings. The tracked diff check remains unable to inspect the wholly untracked checkout by itself.
- Exact raw identities matched: selected Policy `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`; frozen design `4097F897073E681ABAB4B5535EAA81ED38F32F2A9BAE72B49C672B6FFF74B80C`; controlling pre-review `AACE3319B6A675F6EE6873E5FAEDBA3241131483BCF8827E6150FCBD8C331E83`.

### Disposable database and isolation evidence

A fresh disposable SQLite database was upgraded to head and seeded with the existing research/service and Phase-2 declarations. Before the lab request it contained 32 application tables and 43 rows. `POST /api/v1/wealth-lab/evaluate` returned HTTP 200 / `COMPUTED_SYNTHETIC`; the complete table-count map was byte-for-byte equivalent before and after the POST. The provider dataset GET remained 403 `BLOCKED_POLICY`, status remained `NOT PRODUCTION READY` and `PROVISIONAL / RISK BUDGET NOT APPROVED`, and those read routes also left all counts unchanged.

The decision preflight was exercised separately to avoid falsely attributing its designed persistence to the lab. It returned HTTP 201 with `eligible_for_research_decision=false` and added only one `decision_snapshots` row. A downgrade-to-base, upgrade-to-head and reseed finished at `0003_research_risk_editor`, 32 application tables and 43 rows. `.ai/RESEARCH_TRIALS.jsonl` remained exactly 0 bytes with SHA-256 `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.

### Completion and next evidence

- Changed: this independent report and factual `.ai` operational records only. No implementation, test, frozen Policy/design/pre-review, ADR semantics, model/service/risk-editor/Phase-2, migration, dependency/lock, provider declaration, user database, research trial or Production-gate file changed.
- Why: record the required final independent falsification-first recheck after Terra's minimal B6/W17 correction.
- Result: residual B6/W17 **closed**; applicable non-browser engineering **PASS**; design deviations **NONE found** in the rechecked scope.
- Remaining: actual-browser W18 only for full all-surface engineering acceptance. Run it only with a genuine browser backend; do not infer it from static or pytest evidence.

## 2026-09-20 final actual-browser W18 recheck

### Controlling all-surface engineering disposition

**`PASS_ENGINEERING_RESEARCH_WEALTH_LAB`** for the frozen ADR-0018 engineering contract. A genuine Codex in-app Browser backend independently closed the sole remaining W18 gate against the disposable normal server at `http://127.0.0.1:8000/wealth-lab` and the corrupt-response proxy at `http://127.0.0.1:8001/wealth-lab`. The prior `PASS_ENGINEERING_RESEARCH_WEALTH_LAB_NON_BROWSER` remains the controlling non-browser evidence linked above; this section adds only the mandatory browser surface.

This is scoped implementation conformance, not forecast/model/risk/provider/PIT/tradability/calibration/OOS/shadow or Production validation. It does not approve a Mandate, numerical Risk Budget, optimizer, action, weight, provider or real-data path. `RISK BUDGET NOT APPROVED`; relevant investment/model/provider items remain `NOT VERIFIED`; `SHADOW VALIDATION NOT PASSED`; `NOT PRODUCTION READY`.

### Independent browser observations

- Desktop BASE: the initial page retained `SYNTHETIC ACCOUNTING LAB — NOT AN INVESTMENT MODEL`, the fixed 7Y/USD/nominal/pre-tax/no-flow and readiness blockers, and only Load/Evaluate/Download actions. BASE returned server Evaluation `COMPUTED_SYNTHETIC`, enabled Download only after the browser-local Web Crypto rehash, rendered stable `ALT_CASH`, `ALT_NO_TRADE`, `ALT_PASSIVE`, a separate `SYN_BENCHMARK` comparator, four path ledgers, separately labelled non-binding stress diagnostics and all 15 unavailable/unverified components. Document `clientWidth=scrollWidth=1265`; the JSON textarea alone retained internal horizontal scrolling.
- Immediate stale and W2: editing a current result immediately changed status to `Synthetic input edited; result is stale.`, hid structured output and disabled Download. With `initial_state.cash={state:"MISSING",reason:"Synthetic fixture."}`, both desktop and explicit 390px returned `INPUT_INCOMPLETE` with exactly `[{"code":"MISSING","path":"/initial_state/cash"}]`; the exact editor text remained present and editable, structured output stayed hidden and Download stayed disabled.
- One-submit behavior: during a real evaluation, Evaluate, Load Example and the editor were all disabled; after completion all three re-enabled. No second submission surface remained enabled while the first request was in flight.
- W6c: on desktop and 390px, setting every `SYN_E` monthly price and distribution to zero produced `ALT_NO_TRADE` terminal state `ZERO`, monetary terminal wealth `0`, base/member/lower-envelope `NEGATIVE_INFINITY` with `POSITIVE_ASSUMED_RUIN_MASS`, CAGR `-1e0`, zero-wealth mass `1e0` and difference `UNAVAILABLE/NONFINITE_COMPARISON`. The structured card visibly rendered 84 `RUIN / monetary zero` events and `open from POST_TRADE month 0` recovery text.
- XSS: a successful input with title `<img src=x onerror=alert(1)>` retained the literal text in the canonical response. The document contained zero injected `img`, zero `[onerror]`, no result-contained script and no JavaScript dialog.
- Error handling: W2's HTTP 422 was visibly reported as `Evaluation rejected; input remains editable.` with stale output/download behavior. After stopping only the disposable corrupt proxy, its already-loaded page visibly reported `Network failure; no current result.`, kept input/actions usable, hid structured output and disabled Download. The proxy was immediately restarted from its unchanged helper and reproduced the expected corrupt-hash rejection afterward; the normal server and database were never stopped.
- Rehash mismatch: the corrupt proxy changed only `artifact_sha256` to 64 zeroes. Its response still contained server Evaluation `COMPUTED_SYNTHETIC`, but the browser displayed the distinct client status `ARTIFACT_HASH_MISMATCH`, hid structured output and kept Download disabled. It did not rewrite the server Evaluation into a failure.
- 390px: the explicit viewport reported `innerWidth=390`; after the long structured render and vertical scrollbar, document `clientWidth=scrollWidth=375` (before it, `390=390`). BASE, W2 and W6c remained interactive without horizontal page scrolling; the textarea's large `scrollWidth` remained internal as permitted.

### Exact Artifact byte evidence

The reviewer initiated independent successful downloads at desktop and 390px. They produced `C:\Users\oh12k\Downloads\research-wealth-lab-artifact (1).json` and `(2).json`; each was exactly `201,850` bytes with file SHA-256 `5A55229392B6DABA138A9365126023C7CC28D0A27DCCE1D5B9A2A4C77B68EB29`. Each contained server Evaluation `COMPUTED_SYNTHETIC` and internal `artifact_sha256=7f5bc5e3c82a678b1bc38c4f4d32b594a4678014935b48e7db5f56d781766f2d`. A fresh independent POST of the frozen BASE fixture returned HTTP 200, the same `201,850` bytes and the same file SHA-256; direct byte comparison with the desktop download was true. The corrupt proxy's otherwise successful response could not be downloaded.

### Completion boundary

- Changed by this W18 review: this report and factual `.ai` operational records only. The two user-download artifacts are browser evidence outside the repository. No implementation, test, frozen Policy/design/pre-review, ADR semantics, model/service/risk-editor/Phase-2, migration, dependency/lock, provider declaration, database, research trial or Production-gate file changed.
- Result: W18 **PASS**; full frozen all-surface engineering **PASS**; design deviations **NONE found**. There is no remaining known ADR-0018 engineering acceptance item.
- Remaining limitations: all expressly excluded forecast/model/risk/provider/PIT/tradability/calibration/OOS/shadow/Production work remains outside this synthetic slice and unpromoted.
- Next broader work: none is authorized by this review. Forecast/risk/optimizer/provider/OOS/shadow/Production work remains outside this slice and subject to its own design, evidence and approvals.
