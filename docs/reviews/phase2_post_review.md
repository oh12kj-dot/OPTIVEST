# Phase 2 Forward Provider Evidence — Post-Implementation Review

## Verdict

**FAIL — PHASE2-V1 does not satisfy the frozen engineering contract.** The implementation correctly blocks unreviewed live collection and retains the research/Production denials, but the provider adapters, license-use enforcement, audit linkage, database invariants, replay provenance, verifier and UI acceptance surfaces have material defects.

Reviewer: **GPT-5.6 Sol — Independent Post-Implementation Validator**.

This review is bound to the frozen Phase 2 design and ADR-0015. It does not validate external provider capability, license rights, timestamp semantics, PIT suitability, historical completeness, an investment model, OOS, shadow, trading, or Production readiness.

## Reviewed hashes

- Policy: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`
- Frozen design: `9632BC6BBB2F6631CACFAF5BE587BE6083DA4A063FCE1C624F40BF4393E880EE`
- `.ai/DECISIONS.md` containing ADR-0015: `7524190E4C5385D2A22CA49CF7946CD53FB67CFC29ACCDB7DDBB54150E454E9E`
- `alembic/versions/0002_phase2.py`: `7C5D56FB10D813CE7EBFD1369A5C72F6EE5B926D8D7C09ADAA2EFC2132E22D21`
- `alembic/versions/0003_phase2_transport_audit.py`: `AE7E5BD2106B66D3AEBB3FCD7ACA3BA77A9FD85A71AE621730EAB4AE86412577`
- `optivest/models.py`: `4BA7B86B2138EDE7552D2ABA2D20006063D9A5A77DF59D674FEDC391CEA54B63`
- `optivest/phase2.py`: `EA3DBDFF0C8EF1828E824B40C9DEBB5AD7CA5A7B3656AE0F14481CBDCA30A162`
- `optivest/cli.py`: `6E6CCC2C5B1910FCA29937DEEBE3F3AC0658EBDEB7ECBD74C08C4158A0773A78`
- `optivest/app.py`: `5CF3C41C8075DA789B29AC2A7D3BAB4EF4D0F5F6C238DCA577A4FCCAB1D11A2C`
- `README.md`: `8068EFBDBEA8437CF3D87B41D4457D14AB36673EBDA05900F6CF281EA5430205`
- `tests/test_phase2.py`: `1D864464C2EA4D6F5F30649C30F8A211A23D394BEA22ED7ECF81839ABBED8BFB`
- Phase 1 regression: `4B96A7C8CD4E6AD37691A018A6F5C9B32DB9423A3386BA7FA28A9F7C0F73CD20`
- Phase 0 regression: `FA997605EBDF54FA960A3F17FE04999C1E592E2A7F0026DC8DF52DE45393B76D`

No implementation, design, Policy, decision or operational file was changed. All reviewer mutations used fresh temporary SQLite databases and a loopback-only HTTP server.

## Executed evidence

- `uv sync --locked`: exit 0; 30 packages resolved and 27 checked.
- `uv run pytest -q`: exit 0; **52 passed, 2 skipped**, with two dependency deprecation warnings. The skipped cases are link-escape tests unavailable under current Windows permissions; they do not establish link/junction coverage.
- `git diff --check`: exit 0.
- Fresh migration `upgrade head -> downgrade 0001_phase1 -> upgrade head`: **30 -> 15 -> 30** reflected tables.
- TestClient root/OpenAPI: HTTP 200, 25 paths, `NOT PRODUCTION READY` and `NOT RELIABLY BACKTESTABLE`; `/api/v1/raw-objects` returned 404.
- Actual isolated CLI seed: exit 0, two datasets and all use permissions `NOT_VERIFIED`.
- Actual SEC and Nasdaq CLI commands with the seeded state: exit 2, `BLOCKED_POLICY`; two blocked runs, zero snapshots, and no network request.
- `verify-phase2`: exit 0 on the fully migrated DB, but also incorrectly exited 0 on a DB stopped at revision `0002_phase2`.
- RawStore exact-byte hash/tamper and noncanonical-hash checks passed. Independent symlink creation was denied by Windows, so parent-link/junction escape remains unverified rather than inferred passed.
- Local HTTP probes showed a real 404 recorded as four transport errors followed by `HTTP_RETRY_EXHAUSTED`, and a real redirect recorded with final URL but redirect count 0 and empty chain.

## Blocking findings

### P0-1 — provider parsers do not implement the frozen dataset semantics

The Nasdaq parser requires a literal `Symbol` header, although the other-listed path later looks for `ACT Symbol`. An otherlisted-style header therefore fails before parsing. The parser validates only `Test Issue`; it does not enforce dataset-specific required columns or categorical allowlists. Staging accepts every non-test row and does not exclude ETF/fund/structured-product flags, unsupported venues or unknown instrument types as required.

Deterministic duplicate detection is also ineffective: each row key includes its sequence index, so the same source row repeated at another position has a different key.

The SEC parser accepts any object containing `cik` and does not bind the payload CIK to the requested scope. Independent reproduction captured under scope `0000000001` with payload CIK `0000000002`; it succeeded and advanced that wrong scope. It also does not normalize the frozen accession/form/filed/report/acceptance/amendment/historical-file and XBRL frame/context/unit evidence.

Fix: implement separate exact-format Nasdaq listed/other-listed parsers and frozen inclusion states; reject duplicate deterministic source identities; bind requested CIK to payload CIK; implement the specified SEC submission/filing/XBRL evidence fields and negative fixtures using representative publisher formats.

### P0-2 — required source-time evidence is absent and `usable_at` is premature

The Phase 2 schema lacks `source_published_at`, `available_at_claimed`, `available_at_validated`, source timezone/precision and null-reason fields required by the common envelope. Migration 0003 adds only free-form `source_time_text`. SEC acceptance time is left inside opaque JSON.

`usable_at=now()` is assigned before snapshot parts, rows, staged events, head movement and transaction commit, although the frozen contract defines it as the commit instant after all validation/persistence succeeds.

Fix: add the exact claimed/validated/source-time fields and ownership constraints; parse documented source fields with timezone/precision provenance; keep validated availability null; stamp usable time at the defined atomic publication boundary and ensure no decision/projection can precede it.

### P0-3 — license-use checks permit unreviewed retention and derived storage

`collect()` checks only `NETWORK_CAPTURE` and `LOCAL_RAW_STORAGE`. A fixture with only those two permissions `ALLOWED` successfully persisted raw objects and derived normalized rows while `RETENTION` and `DERIVED_STORAGE` were absent, which the permission lookup treats as `NOT_VERIFIED`.

Fix: require every permission implicated by the operation before the request/body write: at minimum network capture, local raw storage, retention and derived storage for capture/parse persistence. Apply the appropriate permissions to replay and any internal display of licensed data. Tests must deny each missing/blocked use before the affected operation and prove no partial artifact/head.

### P0-4 — ingestion audit can assert false success and loses retrieval lineage

A malformed non-HTML Nasdaq response reached the parser and raised `NASDAQ_HEADER_INVALID`, but the DB contained both `SUCCEEDED` and `FAILED_PARSE` ingestion runs with no valid snapshot. The code inserts a terminal success before parsing, then appends a failed run without rolling the success back.

A repeated identical capture created a second successful run and returned the existing snapshot, but only the first run was linked from `source_snapshots.run_id`; observed linkage was `[true, false]`. The second retrieval cannot be traced to the logical snapshot it reproduced.

The schema also has no durable started state/allowed one-time terminal transition. Runs and attempts are inserted only after the transport work, so abrupt process failure can leave no attempt audit.

Fix: persist one started run before dispatch, append attempts durably, and make one database-enforced transition to exactly one terminal state. Never create success until parse/validation/raw persistence completes. Add an immutable run-result/retrieval-snapshot relation so every repeated retrieval links to the resulting existing or new logical snapshot.

### P0-5 — actual HTTP transport audit misclassifies outcomes and omits redirects

`urllib` raises `HTTPError` for non-2xx responses. `fetch()` does not catch it, so a local 404 was recorded four times as `TRANSPORT_ERROR` and ended as `HTTP_RETRY_EXHAUSTED`, losing status, headers and body. The default opener follows redirects, but `fetch()` hardcodes redirect count 0 and an empty chain; a loopback 302 probe confirmed the omission.

The SEC header advertises gzip/deflate while this transport neither records `Content-Encoding` nor decompresses before JSON parsing.

Fix: capture `HTTPError` status/headers/body as an HTTP result, retry only the frozen retryable statuses, implement and sanitize actual redirect-chain auditing, and either remove compression advertisement or version and test exact decompression/raw-byte semantics. Enforce the 120-second total deadline across request time plus sleeps, not only pre-sleep estimates.

### P0-6 — database trust, hash, state and chronology invariants fail open

Direct SQL persisted every tested invalid row:

- `SUCCEEDED` run with null completion and nonempty error fields;
- source row with `row_hash='not-a-hash'`;
- source snapshot with invalid manifest hash and state `PIT_SAFE`;
- source candidate state `MATCHED_REVIEWED`;
- identity review with revision 0, status `PIT_SAFE`, collector actor and blank reason;
- staged event type `DELISTED` with blank reason and `usable_at < observed_at`.

The migration lacks the required enum, exact-hash, terminal-consistency, nonempty-reason and chronology checks for these tables. It also does not database-enforce same-scope/same-candidate relationships among heads, snapshots, runs, parts, rows and review heads.

Fix: implement the frozen checks and composite relationship constraints/triggers in the revision-owned schema; test every bypass with `pytest.raises(IntegrityError)` and verify rollback/no partial state. Keep only the intended CAS head rows mutable.

### P1-1 — parser provenance and replay are not version-faithful

The seeded parser hash is SHA-256 of `function.__code__.co_code`, which excludes constants and dependent parsing logic and can remain unchanged after semantic edits. Snapshots use a hardcoded `phase2-v1` parser version. Replay selects the current parser solely from the part name and never verifies the stored dataset parser hash or executes the recorded parser version.

Fix: hash the immutable parser artifact/package and its relevant schema/config, bind snapshot manifest to that version/hash, and refuse replay when the exact parser is unavailable or mismatched. A controlled version registry may dispatch old parsers; silently using current code is not deterministic replay.

### P1-2 — verifier and Data Evidence UI do not satisfy acceptance consistency

`verify-phase2` checks only whether `source_snapshots` exists. It passed on revision 0002 while migration 0003 and `ingestion_attempts` were absent. The app startup likewise checks only that some Alembic version exists.

The UI displays dataset names and license permissions but not the required latest run, actual states/errors, snapshot hashes/counts, unresolved identities, staged events or forward-universe start. CLI verification reports none of those counts. Therefore API/CLI/UI consistency is not established by the current test.

Fix: require exact Alembic head and expected schema, keep verification read-only, inspect trusted seed/state and raw-object integrity, and return nonzero on missing/inconsistent Phase 2 state. Render the frozen evidence/status/count fields with escaped text and compare all three surfaces in tests.

### P1-3 — migration scope deviates from the frozen decision

The design and ADR-0015 authorize one new Phase 2 migration, while implementation splits the frozen schema across 0002 and 0003. The round trip works, but the extra migration is an undocumented design deviation and enables the false 0002 verification above.

Fix: before history is released, combine the Phase 2 schema into the frozen migration or obtain an explicit design/ADR disposition for the two-revision sequence. In either case, exact-head verification is required.

## Correctly implemented boundaries

- Seeded public-source declarations keep all seven permissions `NOT_VERIFIED`; live commands fail closed before network access.
- Provider/dataset validation remains `NOT_VERIFIED`; no adapter path elevates it.
- Raw objects use lowercase content hashes, derived keys, same-root temporary writes and integrity checks; raw bytes are not exposed by the API.
- Scoped heads distinguish CIK streams in the tested service path.
- Staged membership/identity records do not project to Phase 1 securities or universe membership.
- API routes are read-only, displayed source/provider text is escaped, and no forecast/rank/weight/action/order route was found.
- Phase 0 and Phase 1 regression tests remain green.

## Bounded-live acceptance and status

The bounded live SEC and Nasdaq capture item in design §7 is **not passed**. Both official-source commands were intentionally and correctly blocked because the seeded license-use permissions are `NOT_VERIFIED`. No external request was made, so there is no live URL/status/header/timestamp/hash/count or official-byte replay evidence. Fixture success cannot replace this item.

This is distinct from the implementation defects above. After code corrections, engineering acceptance still cannot become `PASS_ENGINEERING_P2_FORWARD_CAPTURE` until an evidence-backed, authorized license review marks the required uses `ALLOWED` and both bounded live captures plus offline replay succeed.

## Final disposition and limits

- Phase 2 implementation: **IMPLEMENTATION VALIDATION FAILED / REVIEW_REQUIRED**
- Bounded live provider capture: **BLOCKED_POLICY / NOT VERIFIED**
- Provider/license/timestamp/PIT: **NOT VERIFIED**
- Historical universe: **NOT RELIABLY BACKTESTABLE**
- Investment model/OOS/shadow: **NOT VERIFIED**
- Risk Budget: **RISK BUDGET NOT APPROVED**
- Production: **NOT PRODUCTION READY**

No provider, model or Production claim may be inferred from the 52 passing tests or the working migration round trip.
