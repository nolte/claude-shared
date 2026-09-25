---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "666"
classification: "feature-request"
secondary-classes: []
route: "direct"
status: approved-pending
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

Group context: `issue-batch-orchestrate` run `20260925T071908Z-b7c2`, group
`2026-09-25-consumer-reachability`, integration branch `feat/2026-09-25-consumer-reachability`.
This run does not open a pull request; the bundle does.

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #666 — implementation-plan-author: accept a requirements-elicit artifact without a GitHub issue
- **URL**: <https://github.com/nolte/claude-shared/issues/666>
- **Labels**: none
- **Linked items**: none; consumer trigger `nolte/claude-goose` feature 005 R3 (`recipe-plan` borrows the work-package shape)
- **Prior art checked**: no open PR; the agent already has three issue-less paths (audit-driven ×2, review-driven) at `plugins/nolte-engineering/agents/implementation-plan-author.md:43-56`
- **Trusted author**: `nolte` (repository owner)

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: none
- **Rationale**: a new grounded-input path for an existing agent; no defect in the current behaviour
- **Asserted cause verified**: none asserted — the issue states a gap; the gap is confirmed at `:38` ("one of four sanctioned sources"), `:40-42` (requirements path bound to "an analysed GitHub issue"), `:127-129` (precondition 1 demands a single resolved issue), `:130-141` (four-source list), `:201-206` (no write path for an issue-less requirement artifact), `:241` (Targets row)

## Requirements gate

No `project/requirements/` artifact exists for #666. **Operator override** recorded at the
group write gate (2026-09-25): the issue carries a concrete proposal (fifth input, write
path `.audits/requirements/<slug>-plan.md`) authored by the maintainer; acceptance is
mechanical (validator green, budget held).

## Scope

- **In scope**: a fifth grounded input — a confirmed `requirements-elicit` artifact under `project/requirements/<slug>.md` meeting `τ_high`, with no GitHub issue — wired through the input list, the preconditions, the persist step, the write-effects table and the frontmatter routing fields
- **Out of scope**: changes to `requirements-elicit` itself; changes to `issue-orchestrate` (which always has an issue); any spec text (`spec/project/issue-orchestration/en.md` does not enumerate the agent's inputs — `grep -n 'observability-audit\|grounded input'` → 0 hits)

## Route

- **Decision**: direct
- **Rationale**: one outcome, one file, no roadmap item

## Work packages

### P1 — Fifth grounded input: requirement artifact without an issue

- **Problem statement**: Hypothesis: the agent can accept `project/requirements/<slug>.md` alone as the requirements-driven path when no issue exists, writing its plan to `.audits/requirements/<slug>-plan.md` alongside the existing issue-driven path. The specialist may refute the write path if the agent's write-effects table or `spec/project/issue-orchestration/` §Pre-analysis artifact lifecycle prescribes another location for issue-less plans; the audit-driven precedent (`:202-206`) writes next to the source artifact, which argues for `.audits/requirements/<slug>-plan.md` since `project/requirements/` is durable and must not receive run-scoped artifacts.
- **Acceptance criteria**: (a) `:38-56` lists five sources, the new one naming the artifact path and the `τ_high` condition; (b) Preconditions 1–2 (`:127-141`) admit the issue-less requirements path; (c) Step 4 (`:198-206`) names the write path `.audits/requirements/<slug>-plan.md`; (d) Write effects Targets row (`:241`) lists it; (e) a `use_when` entry covers "a confirmed requirement artifact with no issue"; (f) `description:` is extended only if `python3 scripts/validate_skills.py plugins/nolte-engineering/agents/` stays free of `agent-description-budget` findings (headroom 1389 chars measured 2026-09-25), otherwise body-only; (g) `python3 scripts/validate_skills.py plugins/nolte-engineering/agents/implementation-plan-author.md` exits 0 with no Critical
- **Touched files / artifacts**: `plugins/nolte-engineering/agents/implementation-plan-author.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: none (group ordering places it after #665)

## Dependency ordering

P1 only.

## Risks

- Plugin-wide description budget (`AGENT_DESC_BASELINE_CHARS["plugins/nolte-engineering/agents"]`) — a long description addition fails the gate for all 37 agents; body-first.
- The agent body is long; the token-cap band (`body-token-approaching`) must not trip — check the validator output.

## Open questions

none

## Dispatch log
