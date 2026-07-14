---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: 376
classification: feature-request
secondary-classes: [spec-change]
route: direct
status: approved
created: 2026-07-14
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #376 — [feat] Release regression scope: determine targeted E2E tests from the change set
- **URL**: <https://github.com/nolte/claude-shared/issues/376>
- **Labels**: enhancement, feat, needs-triage
- **Linked items**: none (no comments, no referencing PRs)
- **Prior art checked**: no `release-regression-scope` spec; no matching `project/features/` entry; no roadmap item (max id R-10). All anchor specs exist (`e2e-test-automation`, `test-pyramid-foundation`, `test-tier-*`, `test-cycle-foundation`, `test-cycle-case-determination`, `test-case-derivation`, `release-skill-layer`, `release-automation`, `release-artifact`). No prior art found.

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: spec-change
- **Rationale**: A new capability (release-relevant regression/E2E scoping) requested; the target artefact is explicitly a new spec operationalised into a skill + scanner agent.

## Scope

- **In scope**: A new discipline that derives impacted topic areas from a release change-set and selects the minimal-but-complete-within-area regression/E2E test scope — delivered as a spec + standalone skill + read-only scanner agent, homed in `nolte-engineering`.
- **Out of scope**: writing/running/auditing tests (`e2e-test-automation`, `test-tier-*`, `test-cycle-*`); driving the release (`release-*`); deriving new test cases (that stays `test-cycle-case-determination`). This capability only *selects* over existing cases at release level.

## Requirements gate

- **Artefact**: `project/requirements/release-regression-scope.md` (this worktree), produced by `requirements-elicit` this run.
- **U_gate**: 0.85 ≥ `τ_high` (0.8) — gate satisfied; all 8 dimensions confirmed via authoritative operator choices. Residual non-load-bearing details recorded as assumptions A1–A3.

## Route

- **Decision**: direct (operator override)
- **Rationale**: The initial pre-analysis recommended the pipeline route (the issue nominally spans spec + skill + agent). The operator overrode this to direct implementation, consistent with the repository precedent: single new capability bundles (spec + skill + read-only scanner) have historically been built directly in **one** coherent PR — `dockerfile-audit` (#364), `observability-audit` (#368), `kpi-derive` (#365) — not via the roadmap→feature→sprint pipeline. The pipeline route fit #378 because it was a *broad rollout across ~14 existing artefacts*; #376 is a *single coherent capability* ("the release-regression-scope capability"), so it is one PR strand, not many. No roadmap item is created.
- **Operator override recorded**: 2026-07-14 — "direkt umsetzen ohne roadmap planung". The four work packages P1–P4 stay a single coherent capability delivered in one PR; nothing is left silently unplanned (the whole capability is in scope), so the "never leave the remainder unplanned" rule is honoured.

## Work packages

<!-- Coarse packages for the pipeline route; feature-decompose refines these into feature files. Each carries a testable acceptance criterion. -->

### P1 — Author the discipline spec (linchpin)

- **Problem statement**: Define `spec/project/release-regression-scope/` (en canonical + de): traceability-inverse attribution (change → requirement/TC-ID → verifying tests), worst-case fallback for non-attributable changes, completeness-within-area (every functional requirement has a green test at the appropriate tier; gap = blocker/risk), the release-level-aggregate boundary vs `test-cycle-case-determination`, the guarantee triad, and delimitation against the anchor specs.
- **Acceptance criteria**: spec exists in en+de with structural parity; passes `spec-readiness-reviewer`; delimitation section cites `test-cycle-case-determination`, `e2e-test-automation`, `release-skill-layer` without duplicating them; `Portfolio-Scope` recorded.
- **Touched files / artifacts**: `spec/project/release-regression-scope/{en,de}.md`, `spec/README.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: none

### P2 — Read-only change→area scanner agent

- **Problem statement**: A read-only agent that resolves the release range, inverts the requirement/TC-ID → verifying-test index, attributes each change to topic area(s), and flags non-attributable changes for worst-case fallback. Detection only; selects nothing and writes nothing.
- **Acceptance criteria**: agent frontmatter validates (`validate_skills.py`); `tools:` are read-only; description stays within the routing budget; returns a structured attribution inventory with residual-risk flags.
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/release-regression-scope-scanner.md`
- **Specialist**: `nolte-shared:claude-plugin-developer`
- **Depends on**: P1

### P3 — Standalone scope-determination skill

- **Problem statement**: A skill that consumes the scanner's attribution, derives the minimal-complete regression scope (E2E-emphasised), and produces the auditable report (in-scope areas, selected tests, deliberately-excluded areas + rationale, residual-risk note) plus the coverage-gap blocker.
- **Acceptance criteria**: skill exists and validates; report structure covers all four report elements from R5; a missing verifying test surfaces the area as not-fully-covered per R4; produces identical output headless (no MCP dependence).
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/release-regression-scope/SKILL.md` (+ templates/examples)
- **Specialist**: `nolte-shared:skill-management` (chains to `nolte-shared:claude-plugin-developer`)
- **Depends on**: P1, P2

### P4 — Wiring: allowlist / tool grants / catalog / delimitation

- **Problem statement**: Any permission-allowlist entries or agent tool grants the scanner needs (git/`gh` reads), catalog/docs wiring for the new skill+agent, and cross-spec delimitation notes.
- **Acceptance criteria**: `task test`/`task lint` green; catalog renders the new skill+agent under `nolte-engineering`; no consumer newly gated.
- **Touched files / artifacts**: `spec/claude/permission-allowlist/`, `.claude/settings.json` (if needed), `docs/catalog-sources.yml`, cross-spec references
- **Specialist**: `nolte-shared:permission-allowlist-maintain` + `nolte-shared:skill-agent-catalog-apply`
- **Depends on**: P1, P2, P3

## Dependency ordering

`P1 → P2 → P3 → P4` (spec first as the linchpin; scanner before the skill that consumes it; wiring last).

## Risks

- **Attribution quality depends on existing traceability completeness.** If E2E tests don't consistently name their verifying requirement, or requirements/features lack IDs, many changes fall to worst-case, eroding *zielgenau*. Mitigation: the spec mandates the traceability precondition and a graceful, auditable worst-case fallback rather than a silent guess.
- **Delimitation/overlap risk** with `test-cycle-case-determination` (per-cycle), `e2e-test-automation` (traceability discipline), and `release-skill-layer` (integration surface). Mitigation: a sharp delimitation section, verified by `spec-readiness-reviewer` and `feature-consistency-reviewer` in the pipeline.
- **Not security-sensitive**: the scanner is read-only, touches no auth/secrets/PII surface → no `code-security-reviewer` / `security-review` gate required at this planning stage. (Re-evaluate if implementation adds credentialed reads.)

## Open questions

- **A1** — Release-range resolution (last release → RC tip? merged PRs? touched paths?): spec-authorship detail.
- **A2** — Inverse index read from existing traceability vs built by the scanner at scan time: spec-authorship detail.
- **A3** — "Topic area / Themengebiet" granularity vs the existing requirement/feature grouping; whether a new taxonomy artefact is needed.
- **Non-blocking** — Whether `release-skill-layer` should later *reference* this as an optional pre-rollout gate (operator chose the standalone form; a reference is a possible follow-up).

## Dispatch log

- 2026-07-14 P1 — `nolte-shared:spec` chained (in-session skill) → `spec/project/release-regression-scope/{en,de}.md` + `spec/README.md` row. Vale-clean (contractions, unspaced em-dashes); en/de parity 36 bullets / 10 checkboxes.
- 2026-07-14 P2 — `release-regression-scope-scanner` agent authored per `nolte-shared:claude-plugin-developer` conventions. Read-only (`Read, Bash, Glob, Grep`); `validate_skills.py` clean; description within budget.
- 2026-07-14 P3 — `release-regression-scope` skill authored per `nolte-shared:skill-management` conventions; resumable with detection step; report shape inline.
- 2026-07-14 P4 — wiring: `scope` added to `SKILL_ACTION_TOKENS` in `validate_skills.py` (name-form); catalog auto-discovers the new skill/agent under `nolte-engineering` (no `catalog-sources.yml` change); no permission-allowlist change needed (scanner uses read-only git Bash; skill inherits main-session MCP/`gh`). `pre-commit` green (markdownlint, validate-skills, schemas, spec-drift); Vale deferred to CI.

**Execution note (honest deviation):** the P2/P3 agent+skill authoring was done inline following the `claude-plugin-developer` / `skill-management` conventions rather than via an `Agent(subagent_type=…)` dispatch, because worktree-isolated subagents can't reach this feature worktree (`feedback_worktree_agent_permissions`); a dispatched agent would write to the wrong tree. P1 was chained through the in-session `spec` skill. All four packages are the single coherent capability delivered in one PR.
