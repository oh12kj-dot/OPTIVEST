# OptiVest agent instructions

## Authority, mission and objectives
Read `OPTIVEST_AI_POLICY_V10.md` completely at first use. It is the sole formal Policy selected explicitly by the user on 2026-09-07. Expected SHA-256: `ACF013CE46F450423D83DEEBA1C207B22C669670C2B9BDC83A8A665F5AD38E67`.
The existing `OPTIVEST_AI_POLICY_COMPACT_V10.md` and `OPTIVEST_STARTUP_PROMPT_COMPACT_V10.md` are retained historical inputs, not active authority. Never merge their different semantics into the selected Policy.
Mission/objective: Policy §1; mandate boundary: §2; precise rules remain in the Policy, not this operational index. Greenfield: no legacy architecture, data, approvals, or model compatibility is inherited.
Source of truth: latest explicit user instruction → Policy §1 → approved Mandate/Risk Budget → approved `.ai/DECISIONS.md` → this file → START_HERE/HANDOFF operational state → implementation. Apply the selected Policy's canonical sections throughout.

## Roles and delegation
Astra owns design/final design approval (§3). Terra implements frozen specifications without changing investment semantics. Sol performs independent falsification-first review. One active subagent, depth=1; no recursive delegation or parent parallel reimplementation (§4). Every delegation specifies Objective, Scope, Acceptance Criteria, Required Files, Do NOT Change, Expected Output.
Required sequence for material semantics: design → required pre-review → decision freeze → implementation → tests → independent post-validation. Freeze scope must be explicit; documentation review is not model validation.

## Startup and architecture
Hash the actual selected Policy before using cached state. Compare `.ai/START_HERE.md`; changed hash means `POLICY VERSION CHANGED`, full reread and impact review (§17). Then read HANDOFF, TODO, relevant DECISIONS and only required files; verify Git branch/HEAD/status. A new repository with no commit has HEAD `UNBORN`, never a fabricated hash.
Architecture and phase boundaries: `docs/INITIAL_DESIGN.md`. Phase 0 is complete. Frozen Phase 1 architecture and research-only boundaries are in `docs/PHASE1_DESIGN.md` and ADR-0013. The current stack is FastAPI/Pydantic, SQLAlchemy/Alembic, SQLite local/test and a same-process HTML UI. PostgreSQL, external providers and forecast/optimizer architecture remain unselected until separately justified and reviewed.

## Coding, investment and trading
Apply §5 PIT/tradability/security identity, §7 uncertainty ledger/hurdle, §8 risk feasibility, §9 objective/ranking/accounting, §11 actions, §12 overlay rerun, §13 one-time cost, §14 validation isolation, §16 fail-closed and §18 all-item AND gates directly.
No inferred approvals, missing-as-zero, unsupported inference into weights, Expected Return replacement gate, duplicate cost/uncertainty deductions, or post-optimizer overrides. Unknown required inputs remain `NOT VERIFIED`.
Orders, production budget activation, deployment, billing and other §4 approval operations require explicit user authorization. Research presets never constitute personalized approval. Do not store secrets or credentials in repository/context files.

## Testing and Git
Use risk-appropriate tests with actual commands/results in `.ai/TEST_STATUS.md`. Synthetic/unit evidence never establishes PIT/provider quality, OOS, shadow, calibrated risk or production readiness. No tests against unrelated/live databases.
Preserve user edits and original Policy bytes. Git working tree changes are not commits. Record actual HEAD/branch, verify diffs; no history rewrite without explicit approval. Protect the selected Policy from newline conversion with `.gitattributes`.

## Handoff
Update all §17 operational records and report §16 Changed / Why / Evidence / Tests / Results / Validation Status / Remaining Issues / Model Limitations / Design Deviations / Handoff. Research trial ledger is append-only; no fake trial for bootstrap. Record every §18 item individually; missing or unverified evidence is never PASS.
