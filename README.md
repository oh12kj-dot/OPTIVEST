# OptiVest

## Synthetic accounting laboratory

`/wealth-lab` is a stateless, supplied-synthetic accounting laboratory.  It is
not an investment model: it has no provider, forecast, optimizer, risk-budget,
ranking, action, or production path.  The fixed 7-year USD nominal pre-tax
self-financing example is available through `python -m optivest.cli wealth-lab
example`; evaluate a local raw JSON file with `wealth-lab evaluate --file`.
Its result retains `NOT VERIFIED` and `NOT PRODUCTION READY` boundaries.

Greenfield investment decision-support project. Sole formal Policy: [OPTIVEST_AI_POLICY_V10.md](OPTIVEST_AI_POLICY_V10.md), explicitly selected by the user on 2026-09-07. The similarly named COMPACT Policy and startup prompt are preserved historical inputs and are not active instructions.

Start with [AGENTS.md](AGENTS.md) and [.ai/START_HERE.md](.ai/START_HERE.md). Design: [docs/INITIAL_DESIGN.md](docs/INITIAL_DESIGN.md).

Current stage: Phase 1, Phase 2 offline evidence, the research Risk Budget editor and the synthetic wealth laboratory have narrow independent engineering passes. PHASE2-V1 live capture remains blocked by provider-permission evidence. `RISK BUDGET NOT APPROVED`; `NOT PRODUCTION READY`. Provider/PIT truth, historical-universe completeness, investment models, portfolios and orders remain unvalidated.

## Local startup verification

Requires Python 3.10+ and Git. No package installation or network is needed.

```powershell
python scripts/verify_startup.py --root .
python -m unittest discover -s tests -v
```

The verifier reads local files and prints one JSON report. Exit 0 / `startup_integrity: PASS` means only structural consistency with the pinned Policy and observed Git state. `production_readiness` always remains `NOT PRODUCTION READY`. It does not repair files, authenticate approvals, prove historical ledger immutability, or validate a forecast/portfolio.

This Phase 0 release accepts the selected V10 and `main` (unborn or an exactly recorded SHA-1 commit). Policy changes require §17 full reread/impact review and a reviewed checker trust-anchor update. Branch/schema support changes require the scoped design to be updated. Record real commit changes in START_HERE/HANDOFF; never invent a HEAD to pass a check.

## Phase 1 research application

The application is a local research control plane. It versions a provisional Generic Research Mandate and `BALANCED_RESEARCH_V1`, stores stable issuer/security identity and evidence metadata, and persists fail-closed preflight diagnostics. It has no forecast, ranking, target-weight, action, order or Production-activation route.

```powershell
uv sync --locked
uv run python -m optivest.cli db upgrade
uv run python -m optivest.cli seed-research
uv run python -m optivest.cli verify-phase1
uv run python -m optivest.cli serve --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` for the research UI and `/docs` for OpenAPI. The default local database is `optivest.db` and is ignored by Git. Set `OPTIVEST_DATABASE_URL` to use a separate SQLite database. `verify-phase1` is read-only and fails until migration and explicit research seeding are complete.

The seeded reference is 7-year, USD, nominal, pre-tax, self-financing Generic Research over a US listed-equity sleeve, with CRSP US Total Market as a provisional comparator and VTI as an unverified passive implementation candidate. These are reversible research assumptions, not personalized settings or approvals. Provider declarations cannot make PIT/tradability validated in Phase 1, so decision preflight remains ineligible and Production remains disabled.

### Research Risk Budget editor

`RESEARCH-RISK-EDITOR-V1` adds an offline, immutable research-declaration editor at `/risk-budget` and API/CLI preview/save/history surfaces. It uses explicit decimal-string inputs and reports unavailable feasibility, impact, calibration and approval as `NOT VERIFIED`; it cannot activate a budget, issue an action, or grant provider access. Use a separate database for edits:

```powershell
uv run python -m optivest.cli risk-budget show
uv run python -m optivest.cli risk-budget preview --file draft.json
uv run python -m optivest.cli risk-budget save --file draft.json
uv run python -m optivest.cli verify-risk-editor
```

The editor has `PASS_ENGINEERING_RESEARCH_RISK_EDITOR` under ADR-0017. This validates only the frozen research editor contract; feasibility, calibration, approval and Production remain unverified. `RISK BUDGET NOT APPROVED` and `NOT PRODUCTION READY` remain unconditional.

### Synthetic return-bridge design

`docs/RESEARCH_RETURN_BRIDGE_DESIGN.md` is the unfrozen Astra draft for the next narrow research slice. It proposes supplied-synthetic Economic Return Bridge and hierarchical-prior arithmetic plus a closed uncertainty ledger. It is not yet authorized for implementation and does not produce a forecast, probability distribution, path, optimizer, ranking or action.

## Phase 2 forward evidence foundation

PHASE2-V1 stages replayable SEC submissions and paired Nasdaq current-directory captures without projecting them into authoritative security or universe history. Raw bytes are content-addressed outside Git, request scopes have independent heads, failed responses remain audited, and offline replay verifies the manifest, raw hashes, parser output and normalized rows. No raw payload is exposed through the API. Current Nasdaq snapshots cannot establish past membership or delisting returns, so historical backtests remain `NOT RELIABLY BACKTESTABLE`.

```powershell
uv run python -m optivest.cli seed-phase2-public-evidence
uv run python -m optivest.cli verify-phase2
uv run python -m optivest.cli collect-sec-submissions --cik 0000320193
uv run python -m optivest.cli collect-nasdaq-directory
uv run python -m optivest.cli replay-snapshot --snapshot-id <uuid>
```

The public-evidence seed creates two reproducible source assessments with every license use set to `NOT_VERIFIED`. As a result, both live collection commands intentionally exit with `BLOCKED_POLICY`; public reachability does not grant storage or Production rights. A separate evidence-backed license review must explicitly allow `NETWORK_CAPTURE`, `LOCAL_RAW_STORAGE`, `RETENTION`, and `DERIVED_STORAGE` before the collectors can make a request. SEC collection also requires `OPTIVEST_SEC_CONTACT` at runtime; the value is sent only in the User-Agent and is excluded from logs, database records, manifests and raw artifacts.
