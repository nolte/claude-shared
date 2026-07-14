---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "378"
classification: "feature-request"
secondary-classes: ["spec-change"]
route: "pipeline"
status: approved
created: "2026-07-13"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #378 — Optionally use the GitHub MCP server in GitHub-touching skills and agents
- **URL**: <https://github.com/nolte/claude-shared/issues/378>
- **Labels**: enhancement, skills, agents, claude-code
- **Linked items**: none (no comments, no linked/open PRs)
- **Prior art checked**: none found — no `project/requirements/*mcp*`, no MCP item in `project/roadmap.md`, no `project/features/` MCP entry, no `.mcp.json`/MCP config in the repo, no open PR references

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: spec-change
- **Rationale**: introduces a new *optional* capability (MCP-preferred GitHub access with `gh` fallback) across the plugin surface (feature-request); its load-bearing enabler is a new authoring-convention spec plus a `permission-allowlist` spec change (spec-change).

## Requirements gate

- No `project/requirements/` artefact at `τ_high` exists for this issue.
- **Operator override recorded** (2026-07-13): decomposition proceeds without a prior `requirements-elicit` run, because issue #378 already carries a structured requirement shape (guiding principle, prerequisites, tiered candidate list, acceptance criteria). The deeper requirement rigor is deferred to the pipeline step (`roadmap-plan` → `feature-decompose`, each with its own upstream requirements gate).

## Scope

- **In scope**: comprehend, classify, and decompose #378 into atomic, independently testable work packages; record the route; hand the decomposition to the planning pipeline. The work packages below are the reviewable hand-off contract.
- **Boundary — repo vs portfolio**: the **convention spec (P3) is portfolio-wide** (candidate `Portfolio-Scope: portfolio`, inherited by consumers per `spec/project/portfolio-inherited-spec-layer/`); the **MCP-server config (P2) is claude-shared-repo-scoped** — each consumer provisions its own server. Adoption edits (P6–P9) live wherever the target skill/agent lives (root plugin or `plugins/*`).
- **MVP-first**: implementation is deliberately staged — prove the pattern end-to-end on a single Tier-1 pilot (P6) before broadening (P7–P9). The MVP-carrying strand is **P3 (convention) + P6 (pilot)**.
- **Out of scope**:
  - Authoring the spec, config, allowlist change, agent grants, or any per-skill/agent edit here — those are pipeline-owned features.
  - Making any skill/agent *depend* on MCP or removing the `gh` fallback (hard non-goal from the issue).
  - The read-only **docs/prose** agents that touch `gh` only trivially or not at all — `docs-freshness-checker`, `link-rot-scanner`, `lektorat-scanner`, `diagram-opportunity-reviewer`, `vocab-drift-scanner`, `spec-readiness-reviewer`, `quality-gate-enforcer`. They gain nothing from MCP and are explicitly excluded so no one wires it there.

## Route

- **Decision**: pipeline
- **Rationale**: the issue spans multiple goal outcomes and **several independent PR strands** (config; convention spec; allowlist; agent grants; then per-tier skill/agent edits) and **creates a new roadmap item** — the exact trigger the spec names for the pipeline route. It is not one coherent single-PR outcome, so it MUST NOT be implemented directly.
- **Pipeline hand-off**: `roadmap-plan` (new item, provisional `R-10 — Optional GitHub MCP integration across GitHub-touching skills and agents`, serving outcomes O-1 capability breadth + O-2 quality/efficiency, Phase 5 "Shared-plugin structural health" alongside R-9) → then `feature-decompose` on that item. `feature-decompose` alone has no target item today (R-1..R-9 do not cover MCP), so `roadmap-plan` is the required pipeline entry.

## Work packages

### P1 — Decide the MCP server + auth model (decision)

- **Problem statement**: fix the enabling choices before any wiring — which MCP server, how it is version-pinned, and the least-privilege auth model.
- **Acceptance criteria**: a recorded decision naming the server (provisional default: GitHub's official `github-mcp-server`, see OQ-C), the pin approach, the auth model (least-privilege scopes: repo/actions/issues/PR **read**), and the opt-in + absent-safe stance. No code in this package.
- **Touched files / artifacts**: decision recorded in the roadmap item / first feature; no repo edit.
- **Specialist**: generalist (decision) with operator confirmation.
- **Depends on**: none.

### P2 — Wire the opt-in MCP config (absent-safe)

- **Problem statement**: provision the server as opt-in in claude-shared without breaking absent-server runs.
- **Acceptance criteria**: an opt-in config exists (surface per OQ-B); with the server **absent** every in-scope skill/agent still completes via `gh`; no token/secret is committed to a tracked file.
- **Touched files / artifacts**: `.mcp.json` or `.claude/` config + docs; `.gitignore` if a token file is introduced.
- **Specialist**: `nolte-shared:project-structure-apply` (repo config surface) or generalist — re-resolve at dispatch.
- **Depends on**: P1.

### P3 — Author the MCP-preferred / `gh`-fallback convention (spec) — LINCHPIN

- **Problem statement**: no convention states how a skill/agent expresses "prefer MCP when present, always fall back to `gh`". Every per-artifact edit references it.
- **Acceptance criteria**: a spec (provisional default: new standalone `spec/claude/mcp-tool-preference/`, see OQ-A) defines the optional contract, the graceful-degradation rule, the no-behavior-change invariant, and its `Portfolio-Scope` (see OQ-E), EN-canonical + DE, with `spec/README.md` regenerated.
- **Touched files / artifacts**: `spec/claude/mcp-tool-preference/{en,de}.md`, `spec/README.md`.
- **Specialist**: `nolte-shared:spec` (skill).
- **Depends on**: none (independent of P1/P2 — the contract is server-agnostic).

### P4 — Permission-allowlist the GitHub MCP tools

- **Problem statement**: MCP tool calls would prompt per-call unless allowlisted, mirroring how `gh` calls are already allowed.
- **Acceptance criteria**: `spec/claude/permission-allowlist/` and the project allowlist include the GitHub MCP tool names; a dry check shows no per-call prompt for them.
- **Touched files / artifacts**: `spec/claude/permission-allowlist/{en,de}.md`, `.claude/settings.json`.
- **Specialist**: `nolte-shared:permission-allowlist-maintain` (skill).
- **Depends on**: P1 (tool names known), P3 (convention).

### P5 — Additive agent `tools:` grants + description/routing-budget re-check

- **Problem statement**: agents reach MCP tools only if granted in `tools:`; grants must stay additive and must not blow the plugin agent-description / routing budget.
- **Acceptance criteria**: in-scope agents' `tools:` include the needed MCP tool names; `validate_skills.py` stays green; the aggregate agent-description budget is re-measured and within its guardrail (ties to R-9).
- **Touched files / artifacts**: `agents/*.md`, `plugins/*/agents/*.md` frontmatter.
- **Specialist**: `nolte-shared:claude-plugin-developer` (agent).
- **Depends on**: P1, P3.

### P6 — Tier-1 PILOT: one artefact end-to-end (`portfolio-inflight-collector`)

- **Problem statement**: prove the optional-MCP pattern end-to-end on the single richest read-heavy, cross-repo collector before broadening.
- **Acceptance criteria**: the agent prefers MCP reads when present; **verified by running it once with MCP present and once with only `gh`, and diffing the produced collection — the two MUST be identical**; it references the P3 convention.
- **Touched files / artifacts**: `agents/portfolio-inflight-collector.md` (+ its `tools:` via P5).
- **Specialist**: `nolte-shared:claude-plugin-developer` (agent) — as a pipeline feature.
- **Depends on**: P2, P3, P4, P5.

### P7 — Tier-1 remainder

- **Problem statement**: extend the proven pattern to the rest of Tier 1: `issue-orchestrate`, `workflow-health-triage`, `portfolio-manifest-collector`, `dependency-audit-scanner`.
- **Acceptance criteria**: each prefers MCP when present and passes the same before/after `gh`-only identical-output check.
- **Touched files / artifacts**: the four SKILL.md / agent.md bodies.
- **Specialist**: per-artifact `skill-management` / `claude-plugin-developer` — pipeline features.
- **Depends on**: P6 (pattern proven).

### P8 — Tier-2 adoption (read metadata / verification)

- **Problem statement**: medium-benefit artefacts: `portfolio-audit`, `portfolio-inflight-triage`, `vocab-drift-audit`, `release-notes-curate`, `pull-request-merge` (status reads), `continuous-improvement-triage`/`sprint-review`, `project-structure-apply`.
- **Acceptance criteria**: same optional/fallback contract; same before/after identical-output check.
- **Touched files / artifacts**: the listed SKILL.md bodies.
- **Specialist**: per-artifact, pipeline features.
- **Depends on**: P7.

### P9 — Tier-3 re-evaluation (write/action)

- **Problem statement**: decide whether `pull-request-create` (create step) and `release-publish-trigger` (dispatch) gain from optional MCP; git-plumbing stays on `gh`/git.
- **Acceptance criteria**: a recorded go/no-go per artefact; edits only where net-positive; no removal of the `gh`/git fallback.
- **Touched files / artifacts**: `pull-request-create`, `release-publish-trigger` SKILL.md (only if go).
- **Specialist**: per-artifact, pipeline features.
- **Depends on**: P7, P8 (learnings).

## Dependency ordering

`P1 → {P2, P4, P5}` · `P3` (independent linchpin) · `{P2, P3, P4, P5} → P6 (pilot) → P7 → P8 → P9`.
No adoption package (P6–P9) starts before the convention (P3) exists and the pilot (P6) proves it.

## Risks

- **MCP absent in headless/cron** → the optional contract must be real; mitigation: the before/after `gh`-only identical-output check is a hard AC on P2/P6/P7/P8.
- **Agent description / tool-routing budget blowout** (P5) → additive grants only + re-measure the aggregate budget (ties to the agent-description-budget governance, R-9).
- **MCP tool-name drift across server versions** → pin the server (P1) and verify exact tool names against the pinned catalog at implementation time.
- **Auth-token scope / secret handling** (P2) → least-privilege read scopes, no token in a tracked config; treat the config as secret-adjacent at PR time.
- **Portfolio-inherited-spec propagation** (P3) → if the convention is `Portfolio-Scope: portfolio`, consumers inherit it by reference; the contract must stay *optional across inheritance* so a consumer without an MCP server is unaffected (each consumer provisions its own server, per the scope boundary). Mitigation: the convention states the optionality explicitly; see OQ-E.

## Open questions

- **OQ-A (P3 placement)** — *provisional default*: a new standalone `spec/claude/mcp-tool-preference/` topic (one-concern-per-topic, cleaner than amending `skill-management` + `agent-management`). Operator confirms in the `spec` step.
- **OQ-B (P2 surface)** — open: repo-root shipped `.mcp.json` vs. documented per-consumer setup. Resolve in `roadmap-plan`/first feature.
- **OQ-C (server choice)** — *provisional default*: GitHub's official `github-mcp-server` (best-maintained; matches the issue title). Confirm at P1.
- **OQ-D (tool coverage)** — open: some operations (GitHub-App installation checks, `gh release edit`) may lack a clean MCP tool and stay on `gh`; confirm coverage per artefact.
- **OQ-E (P3 Portfolio-Scope)** — open: is the convention `portfolio` (inherited by consumers) or `local` (claude-shared only)? Drives the propagation risk above.

## Dispatch log

<!-- Pipeline route: no specialist dispatch happens in this orchestration. Hand-off to
     roadmap-plan (new item R-10) → feature-decompose owns the per-package implementation. -->
- 2026-07-13 — route=pipeline; no direct dispatch. Hand-off target: `roadmap-plan` (new item R-10) → `feature-decompose`.
