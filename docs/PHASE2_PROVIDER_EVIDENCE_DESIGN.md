# Phase 2 design — forward-only provider evidence and US universe capture

Status: `DRAFT / ASTRA REVIEW COMPLETE / SOL INDEPENDENT REVIEW REQUIRED`. Date: 2026-09-08. Authority: selected `OPTIVEST_AI_POLICY_V10.md`, SHA-256 `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`. This is a research data-foundation design. It does not authorize historical backtest claims, forecasts, ranking, portfolio weights, Production activation, paid subscriptions or trading.

## 1. Decision and evidence boundary

Phase 2 will add an append-only, replayable capture path for two public sources:

1. SEC EDGAR submissions metadata and filing/XBRL source material, identified by CIK and accession number.
2. Nasdaq Trader `nasdaqlisted.txt` and `otherlisted.txt` current symbol-directory snapshots.

The first successful, fully evidenced paired Nasdaq snapshot starts observation for `US_UNIVERSE_FORWARD_V1`. Its `observed_at` is the maximum server-controlled `response_completed_at` of its two required parts; its later `usable_at` is the transaction-commit instant after both parts, hashes, parse results and validations have succeeded. Membership before `usable_at` is unknown, and any later authoritative projection must use `decision_available_at >= usable_at`. Current directory files must never be backfilled as historical membership. SEC current company metadata may corroborate issuer attributes, but current tickers/exchanges must never overwrite dated security-identifier history.

This phase does not supply a complete survivor-bias-safe historical universe, authoritative delisting returns, split/dividend-adjusted prices, historical index constituents, exchange calendar, market state, or tradability evidence. Historical backtests therefore remain `NOT RELIABLY BACKTESTABLE`; Locked OOS and shadow validation do not begin in this phase.

## 2. Official-source findings and license disposition

The evidence review was performed on 2026-09-08 using primary publisher documentation.

| Source | Verified public capability | Limitation / decision |
|---|---|---|
| SEC EDGAR APIs | No API key; submissions and XBRL data; real-time updates plus nightly bulk archives; older filing history can be referenced through additional files | API observation time is not automatically decision availability. Preserve accession and filing acceptance evidence. Follow fair-access policy and identify the client. |
| SEC EDGAR archives | Daily/quarterly indexes and daily archives, including filing headers | Index/filed dates alone do not prove intraday public availability; use an evidenced acceptance instant when present and retain raw source. |
| Nasdaq Trader symbol directory | Current Nasdaq and other-exchange listings; files update during the day and include a file-creation row | A current snapshot is not historical constituent evidence. It begins forward observation only. |
| Nasdaq Daily List / historical products | Additions, deletions, symbol/name changes and corporate actions are available as commercial products | No subscription, purchase or license acceptance is authorized. Record `PAID_SOURCE_APPROVAL_REQUIRED`. |
| CRSP / Morningstar Indexes | Public methodology can define a comparator family | Research data access is licensed; historical constituents and returns are not acquired. The CRSP-to-Morningstar branding/version transition requires explicit benchmark-version provenance. |
| Vanguard VTI | Official fund page describes the fund as an implementation tracking the broad US total market benchmark | VTI is an investable candidate, not the benchmark itself. Current holdings do not establish historical PIT holdings, tracking, tax, liquidity or look-through suitability. |

Official references:

- SEC EDGAR API documentation: <https://www.sec.gov/search-filings/edgar-application-programming-interfaces>
- SEC developer resources and fair-access limit: <https://www.sec.gov/about/developer-resources>
- Nasdaq symbol-directory definitions: <https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs>
- Nasdaq current directory files: <https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt> and <https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt>
- Morningstar Indexes research data products: <https://indexes.morningstar.com/research-data-products>
- Vanguard VTI profile: <https://investor.vanguard.com/investment-products/etfs/profile/vti>

Licensing evidence preserves the exact reviewed publisher terms/documentation bytes or an immutable local artifact reference, SHA-256, canonical URL, retrieval instant and reviewer provenance. Each version has a normalized permission state (`ALLOWED`, `BLOCKED`, `NOT_VERIFIED`) for network capture, local raw storage, retention, derived storage, internal display, redistribution and commercial/Production use, plus attribution and retention/deletion duties. Public reachability does not imply any permission. Unknown or incompatible permission blocks only the affected operation with `BLOCKED_POLICY`; in particular, capture may not download a body unless network capture and local raw storage are both `ALLOWED`. No collection adapter may change license permission or elevate a provider to `LICENSE_VALIDATED`, `TIMESTAMP_VALIDATED`, `COVERAGE_VALIDATED` or `PIT_SAFE`.

## 3. Frozen candidate source semantics

### 3.1 Common capture envelope

Every HTTP attempt, including a rejected or failed parse, creates or completes an append-only ingestion run. Every stream has an immutable `capture_scope_key`: the dataset semantic version plus canonical normalized non-secret request scope. SEC submissions use the zero-padded CIK; Nasdaq directory uses the constant paired scope `US_LISTED_DIRECTORY`. Secrets, contact text and volatile request headers are excluded. The exact canonical request fingerprint is recorded separately from content identity. Heads, idempotence and compare-and-swap are keyed by `(provider_dataset_version_id, capture_scope_key)` so alternating CIK requests cannot displace each other. A successful logical snapshot records:

- provider and dataset version IDs;
- canonical request URL and source locator, excluding secrets;
- request start and response-complete server UTC instants;
- HTTP status, selected content headers, ETag and Last-Modified when supplied;
- an ordered named-part manifest and canonical manifest SHA-256; each part links to exact raw bytes SHA-256, byte length, media type and immutable local raw-object key;
- source-published/file-created/acceptance instant when the source explicitly supplies one, otherwise null plus reason;
- parser name/version/hash, parse result and row counts;
- parent snapshot ID for comparison, never overwrite;
- license-declaration version and rate-policy version used;
- `LIVE_CAPTURE` observation mode and server-created timestamps.

Raw objects are content-addressed by validated lowercase 64-hex SHA-256 under a repository-ignored local data root. Object keys are derived solely from that hash; stored/request values cannot supply a path. Resolve the root and every parent, reject absolute/parent traversal, case aliases and symlink/junction/reparse escapes, write to a same-root temporary file, verify length/hash, then atomically rename. Replay repeats confinement and integrity checks. Identical bytes across scopes may reference one immutable raw object, while every request scope and retrieval retains provenance.

Each retrieval part links to exactly one raw object. A logical snapshot's ordered manifest is canonical UTF-8 JSON with fixed key ordering and no insignificant whitespace; it contains dataset semantic version, capture-scope key, parser semantic version and ordered part tuples `(ordinal, part_name, raw_sha256, byte_length)`. Nasdaq ordinals are fixed as `1=nasdaqlisted`, `2=otherlisted`; missing, duplicate or swapped parts fail validation. Normalized source rows are canonical UTF-8 JSON with sorted keys, explicit JSON nulls and no insignificant whitespace; each deterministic row hash is over those exact bytes. Source text decoding is dataset-versioned: Phase 2 candidates require strict UTF-8/ASCII-compatible decoding after removing only an optional UTF-8 BOM, accept CRLF or LF as record separators, and never normalize source bytes before raw hashing. Failed bodies remain preserved and replayable but cannot become a valid head. No response body, identifier mapping or fact is silently corrected in place.

Run terminal states are `SUCCEEDED`, `FAILED_HTTP`, `FAILED_INTEGRITY`, `FAILED_PARSE`, `FAILED_VALIDATION`, or `BLOCKED_POLICY`. Zero rows cannot be `SUCCEEDED` unless the dataset contract explicitly permits an empty snapshot. Partial downloads and parser exceptions never advance a dataset head or Universe version.

### 3.2 Time ownership

- `request_started_at`, `response_completed_at`, `ingested_at` and `created_at` are server-controlled UTC instants.
- `source_published_at` is accepted only from a documented source field and keeps its source timezone/precision metadata before UTC normalization.
- `available_at_claimed` equals a documented source dissemination/acceptance instant only when the adapter can point to the raw field. Otherwise it is null.
- `available_at_validated` remains null and provider timestamp validation remains `NOT_VERIFIED` until an independent process validates semantics and observed latency.
- Network retrieval time never substitutes for a historical availability time. For forward research it is a conservative lower bound: a fact is not usable before `response_completed_at` plus the separately validated processing latency.
- No same-close or same-session tradability is inferred. Exchange calendar and market-state validation remain blockers.

### 3.3 SEC adapter

CIK identifies a filer/issuer record and accession identifies a filing; neither identifies an exchange-traded security or share class. SEC ticker/exchange fields are aliases to be reconciled with dated listing evidence. Automatic issuer/security merge based only on name or ticker is forbidden.

The adapter prefers bulk archives for broad refreshes and bounded entity requests for incremental work. It sends a descriptive User-Agent whose operator contact is read from an environment variable; CLI arguments, logs and persisted request data must not contain the contact. It enforces one monotonic-clock token bucket shared by all SEC requests in the process, with capacity 1 and refill 5 tokens/second, measured immediately before HTTP dispatch. HTTP 429/503 honors a valid bounded `Retry-After`; other retryable transport/5xx failures use capped exponential backoff with injected deterministic jitter for tests. Maximum attempts are 4 and maximum total elapsed time is 120 seconds. Redirect count, sanitized locations and final URL are recorded; credentials and sensitive headers are never persisted. The 5 requests/second setting is an operational safety cap below the published 10 requests/second ceiling, not evidence of provider capacity, and is versioned/configurable downward.

For submissions, preserve the complete raw JSON and every historical-file reference. For filings, preserve accession, form, filing date, report date, acceptance datetime when present, primary-document locator, amendments and raw filing-header evidence. For XBRL, preserve accession/filed/frame/context/unit dimensions. Amended or later facts append candidates; they do not rewrite what was known from an earlier accession. Company Facts aggregates are discovery material until their per-fact filing lineage is resolved.

SEC collection in Phase 2 is metadata/evidence capture. It does not make any fundamental metric decision-eligible and does not generate scores, forecasts or rankings.

### 3.4 Nasdaq directory adapter and forward universe

Fetch both directory files as one logical run. Validate delimiter/header, required columns, allowed categorical codes, trailer row and source file-creation timestamp. Store both raw byte streams before parsing. A dataset head advances atomically only when both files pass.

`US_UNIVERSE_FORWARD_V1` includes security candidates that, in a valid paired snapshot:

- are listed by Nasdaq Trader as Nasdaq or another supported US exchange listing;
- are not test issues;
- are not ETFs or other fund/structured-product types when the directory provides the flag/type;
- can be assigned an explicit instrument-type candidate supported by the directory fields;
- retain exchange code, symbol and source row as temporal aliases, not identity.

Rows whose instrument type cannot be established enter `REVIEW_REQUIRED` and are excluded from eligible common-equity membership. Missing fields never default to common stock. OTC securities and unsupported venues remain excluded with reason. Collection creates only a stable `source_security_candidate_id` with source-row lineage and an unresolved identity-review state; it cannot create an authoritative Phase 1 `security_id` or merge a same-ticker row into an existing security.

Each valid snapshot appends staged membership events keyed by stable source-candidate ID: `FIRST_OBSERVED`, `PRESENT`, `POSSIBLE_REMOVAL` or `REAPPEARED`. Events record snapshot, `observed_at` and `usable_at`; no prior event or Phase 1 membership interval is edited. A disappearance produces `POSSIBLE_REMOVAL`, not a confirmed delisting. Confirmed delisting, effective date, successor lineage and return treatment require separate evidence. Reappearance or symbol change never retroactively rewrites prior events or intervals.

Unresolved rows remain outside authoritative `issuers`, `securities`, `security_identifiers` and `universe_memberships`. Identity review is an append-only revision chain with expected-current compare-and-swap, actor/reviewer provenance, method/algorithm version, evidence IDs, decision and nonempty reason. Collection can create only `UNRESOLVED`; it cannot create `MATCHED_REVIEWED`. Projection is blocked until exactly one reviewed issuer/security/share-class/venue mapping exists and its dated identifier interval is compatible. Zero, conflicting or multiple mappings remain staged and excluded. A later independently reviewed projection may derive new immutable authoritative membership facts/events from the staged chain; it must not update a prior Phase 1 row or infer an issuer solely to satisfy a foreign key.

## 4. Schema and service change

Add one Alembic migration with these tables and integrity rules:

- `license_evidence_versions` and `license_use_permissions`: immutable reviewed terms/document artifact/hash, provenance, reviewer and per-use permission/duty matrix. Only a separate reviewer workflow may create a reviewed version; adapters read it and fail closed.
- `provider_dataset_versions`: immutable provider/dataset/endpoint/parser semantic versions, source URLs, linked license-evidence version, documented timestamp semantics, rate-policy JSON and validation states. No public endpoint can set validation states above `NOT_VERIFIED`.
- `capture_scopes`: immutable dataset-scoped canonical key and normalized non-secret request identity. Unique `(provider_dataset_version_id, capture_scope_key)`.
- `ingestion_runs`: immutable-start/terminal-completion record, server timestamps, request group, capture scope, canonical request fingerprint, state, error code, retry relation, configuration hash and aggregate counts. Exactly one terminal transition; completed rows are immutable.
- `raw_objects`: exact-byte content identity, validated lowercase SHA-256, length and derived object key. It contains no caller path. Committed objects are immutable.
- `source_snapshots`: immutable logical capture envelope, capture scope, ordered manifest JSON/hash, parser version, `observed_at` and `usable_at`. Snapshot idempotence and head comparison use scoped stream plus manifest identity.
- `source_snapshot_parts`: ordered named parts per logical snapshot, retrieval request/response metadata and raw-object link. Nasdaq valid snapshots require exactly the two fixed names/ordinals before success.
- `source_rows`: immutable normalized source row JSON, deterministic row key/hash and part lineage. Unique row identity within a snapshot; parser replay must reproduce hashes.
- `dataset_heads`: one current fully valid snapshot per `(provider_dataset_version_id, capture_scope_key)`, compare-and-swap protected.
- `source_security_candidates` and `staged_membership_events`: stable source-side candidates and append-only observations, separate from authoritative Phase 1 identity/membership tables.
- `identity_review_revisions` and `identity_review_heads`: append-only expected-current decision chains with actor/reviewer, method version, evidence and statuses (`UNRESOLVED`, `MATCHED_REVIEWED`, `CONFLICT`, `NO_MATCH`, `REJECTED`). Adapters may create only the initial unresolved revision.

Existing `providers`, `evidence_records`, `security_identifiers` and `universe_memberships` remain authoritative for Phase 1 concepts. Phase 2 does not implement authoritative projection; it only stages candidates/events and identity review records. Raw capture and normalization may not directly mark provider validation or PIT eligibility. Database constraints and immutable-update triggers must enforce trusted-state allowlists, hashes, timestamp order, nonempty reasons for failures/unknowns, terminal-state consistency, scoped heads and expected-current revision behavior.

## 5. API, CLI and UI

CLI commands:

- `python -m optivest.cli collect-sec-submissions --cik CIK##########` (requires an environment-configured contact)
- `python -m optivest.cli collect-nasdaq-directory`
- `python -m optivest.cli replay-snapshot --snapshot-id <uuid>`
- `python -m optivest.cli verify-phase2`

The contact value must be supplied by environment/config at runtime, never stored in the repository or database request log. Absence blocks SEC network collection before any request.

Research API adds read-only paginated metadata endpoints for datasets, runs, snapshots, parts, row summaries and identity candidates. It never serves raw-object bytes in Phase 2. Network collection remains CLI-only to avoid accidental browser-triggered traffic. The UI adds a Data Evidence page showing source/version/license-use matrix/timestamp/coverage states, latest run, hashes/counts, failed runs, unresolved identities, forward-universe start and explicit historical-data limitations. All source text is escaped. It has no “validate,” “approve,” ranking or trade control.

## 6. Fail-closed rules

The following block head advancement, projection and decision use:

- absent/malformed source creation or acceptance fields where required;
- body/hash mismatch, HTML/error payload masquerading as data, truncated or partial paired response;
- unknown categorical code, schema drift, duplicate deterministic row key or count inconsistency;
- missing license declaration/version, missing client identification for SEC, or rate-policy violation;
- `NOT_VERIFIED` or `BLOCKED` permission for the attempted network capture, raw storage, retention, derived storage or display operation;
- ambiguous ticker/venue identity, possible removal, unsupported instrument type or absent stable-ID evidence;
- client-supplied server timestamps or any attempt to set validated/PIT-safe states;
- failure to preserve the raw payload or deterministic offline replay;
- absolute, traversing, non-hash-derived or link/reparse-escaping object key; partial/non-atomic object commit;
- historical membership requested before the first valid forward snapshot;
- Production, portfolio, ranking, action or order request based on Phase 2 capture.

All failures expose a stable code and nonempty reason. Missing data remains null/status/reason. Retrying appends a linked run and does not erase the failure.

## 7. Acceptance evidence

Implementation acceptance requires all of the following:

1. Fresh migration upgrade/current/downgrade/upgrade succeeds and restores the Phase 1 schema on downgrade.
2. Raw-SQL and service tests reject mutable completed runs/raw objects/parts/snapshots/rows/review revisions/events, invalid/blank hashes, invalid chronology, trusted-state injection, invalid terminal transitions, stale scoped-head/review CAS and incomplete Nasdaq pairs.
3. Parser fixtures include real-format samples plus malformed headers/trailers, unknown codes, duplicates, empty/truncated/HTML bodies and encoding/newline variations.
4. Replaying a stored raw object produces exactly the recorded parser version, canonical manifest, normalized row hashes and counts; tampering, missing/duplicate/swapped parts and failed-body promotion are rejected.
5. Alternating two SEC CIK streams retain independent heads. Identical bytes under different scopes retain both request/retrieval provenances while deduplicating only the raw object. A repeated identical payload adds its retrieval run without duplicate staged events.
6. A changed valid snapshot advances only its scoped head atomically; parse/validation failure leaves the prior head unchanged.
7. Membership-event tests cover add/present/possible-removal/reappearance and late validation without mutation or backdating. Identity tests cover ticker reuse, cross-venue duplication, share classes, symbol change and ambiguous issuer links, proving that no authoritative security/membership is created while resolution is zero, multiple, incompatible or unreviewed.
8. Rate limiter is shared, measured at the HTTP boundary and tested with retries; SEC requests remain at or below configured 5 requests/second and the published 10 requests/second ceiling.
9. License matrix tests cover unknown/blocked raw storage, derived/internal-display permission, attribution/retention duties and absence of raw download. Root-confinement tests cover traversal, absolute paths, hash case/length, partial files, tampering and symlink/junction/reparse escape where supported; OS-denied link creation is explicitly skipped.
10. API/CLI/UI show the same counts, source hashes, escaped text, statuses and limitations; CLI failures return nonzero; Production remains denied and no browser route starts collection.
11. A bounded live SEC submissions capture and a paired Nasdaq directory capture succeed against the official endpoints, then replay offline from stored bytes. Live evidence records actual URL/status/headers/timestamps/hashes/counts. A live failure is reported as failure, never replaced with fixture success. The client-contact requirement is proven without persisting the secret contact value.
12. Independent Sol post-implementation validation reproduces database, parser, network-boundary, UI/API and fail-closed checks from a fresh database.

Engineering acceptance may be `PASS_ENGINEERING_P2_FORWARD_CAPTURE`. It must not imply provider/PIT validation, historical-universe completeness, investment-model validity, Locked OOS, shadow or Production readiness.

## 8. Explicitly deferred decisions

- Paid Nasdaq historical Daily List, CRSP/Morningstar research data, commercial prices/corporate actions or any provider account: `USER_CONFIRMATION_REQUIRED` before purchase, license acceptance, credential use or billing.
- Historical universe reconstruction and delisting-return policy: blocked until an admissible source and license are selected and validated.
- Price/return total-return construction, exchange calendar, tradability, liquidity/capacity, benchmark-return series and VTI implementation validation: separate design/review.
- Fundamentals projection, metric conflicts/restatements, forecast, uncertainty sets, `U_objective`, `U_risk`, `S_stress`, optimization, ranking and actions: separate material freezes.
- Production database/deployment: unselected.

## 9. Required review and freeze

Sol must perform a blind falsification pass and a comparative pre-implementation review. Astra will correct material findings and freeze an exact design hash, migration/code/test file scope and source versions in ADR-0015. Terra may then implement only the frozen forward-capture scope. Any change to universe inclusion, identity resolution, availability semantics, license status, projection eligibility or historical claims requires unfreeze and renewed review.
