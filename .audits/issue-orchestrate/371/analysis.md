---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "371"
classification: "feature-request"
secondary-classes: ["spec-change", "refactor"]
route: "pipeline"
status: approved
created: "2026-07-11"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #371 — Restructure shared plugins: analyze layout and rework agents/skills to fit the agent-description token budget
- **URL**: <https://github.com/nolte/claude-shared/issues/371>
- **Labels**: enhancement, skills, agents, audit, claude-code
- **Linked items**: none (no linked/closing PRs)
- **Prior art checked**: PR #329 (merged — earlier 2-tier agent-description trim, −30%); untracked `.audits/skills-agents-sweep/2026-07-01.md` (qualitative sweep of 53 skills / 46 agents, themes T1–T13 — the 5k-token skill *body* cap is a different axis and does **not** cover the per-agent *description*-token routing budget this issue targets); `scripts/validate_skills.py` has **no** aggregate description-token guardrail today; no matching `project/roadmap.md` item; no self-resolving PR. Requirement artefact authored this run: `project/requirements/shared-plugin-restructure.md` (`U_gate = 0.8 ≥ τ_high`).

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: spec-change (the R4 agent-description contract), refactor (the R5 description remediation across ~53 agents)
- **Rationale**: The issue requests a new capability posture — a slimmer, contract-governed, guardrailed shared-plugin surface — not a defect fix; the spec-change and refactor facets are subordinate to that request.

## Scope

- **In scope** (this pipeline run's hand-off): the four "analysis + slim + guardrail" strands — (1) structural analysis with measured token costs, (2) the documented plugin-boundary decision, (3) the agent-description contract + remediation, (4) the regression guardrail in the test gate. These are routed to the planning pipeline as a new roadmap item and its features.
- **Out of scope**: the deep agent/skill **rework** (merge / split / retire / rewrite beyond descriptions) — captured as later features under the same roadmap item, not implemented now (requirement R8). Consumer-repo local `.claude/agents/` edits (each consumer owns its share). Changing the `nolte-media` / `nolte-engineering` boundaries unless the analysis flags a distribution-contract reason.

## Route

- **Decision**: pipeline
- **Rationale**: The issue spans more than one goal outcome (O-1 install-fit **and** O-2 authoring discipline) and more than one coherent PR strand (a structural-analysis document, a spec/contract change, a cross-cutting description refactor over ~53 agents, and a tooling/guardrail change), and it will create a **new** roadmap item. Per the skill's hard rules, an issue with more than one outcome / PR strand / a new roadmap item routes to the formal pipeline and is **never** decomposed for direct implementation. The operator confirmed "Analyse + Slim + Guardrail zuerst" with deeper rework as separate features (2026-07-11).
- **Pipeline hand-off**: `roadmap-plan` — add a new roadmap item under outcome **O-1** (primary; keeping the shared plugin installable within the ~15k routing budget is a precondition for "every repo that installs the plugin"), secondary **O-2** (the description contract + guardrail is one-place authoring discipline). `feature-decompose` then decomposes that item into the P1–P5 features below.

## Work packages

> For a pipeline route these are the **strand shapes handed to `roadmap-plan` / `feature-decompose`**, not packages dispatched by this skill. Each carries a testable acceptance criterion so `feature-decompose` can lift it into a feature directly.

### P1 — Structural analysis + plugin-boundary decision

- **Problem statement**: No written, measured map of the marketplace / plugin / agent / skill layout, its per-plugin description-token costs, capability overlap, and delimitation cross-references exists; and the `nolte-shared` boundary (split vs. keep-and-slim) is undecided.
- **Acceptance criteria**: An analysis document exists carrying (a) per-plugin measured agent-description token costs (method stated), (b) a capability-overlap + delimitation-chain map, (c) a boundary decision with rationale, bound by the distribution-contract split rule (`spec/claude/plugin-scoping/`) — a split justified only by runtime/dependency or consumer-audience, never topic/count. Reuses `agent-review` / `skill-review` / `skills-agents-sweep` outputs rather than redoing them.
- **Touched files / artifacts**: analysis doc under `.audits/` or `project/`; reads across `agents/`, `plugins/*/agents/`, `skills/`, `.claude-plugin/marketplace.json`.
- **Specialist**: resolved at feature-decompose time — analysis reuses `agent-review` / `skill-review` / `skills-agents-sweep`; boundary decision is authored prose (candidate `nolte-shared:audience-doc-author` or inline).
- **Depends on**: none

### P2 — Agent-description contract (spec)

- **Problem statement**: There is no documented minimal contract for an agent `description`; descriptions drift (embedded `user:`/`assistant:`/`<commentary>` blocks, over-long delimitation chains).
- **Acceptance criteria**: A documented contract exists (assumed home: extend `spec/claude/skill-agent-frontmatter/` or `spec/claude/agent-management/`) specifying the "what it does / when to activate / don't use for X → use Y" shape, EN-canonical, no example/commentary blocks in `description`, tightened delimitation chains.
- **Touched files / artifacts**: `spec/claude/skill-agent-frontmatter/` (or `agent-management/`), both languages.
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P1 (analysis informs the contract)

### P3 — Description remediation to the contract

- **Problem statement**: Shared agent descriptions exceed the contract and carry the anti-patterns P2 forbids.
- **Acceptance criteria**: Every shared agent `description` conforms to the P2 contract; no embedded example blocks remain; each remains functionally correct and correctly routed (R6 — spot-checked). Aggregate measured and recorded as the guardrail baseline.
- **Touched files / artifacts**: `agents/*.md`, `plugins/nolte-engineering/agents/*.md`, `plugins/nolte-media/agents/*.md`.
- **Specialist**: `nolte-shared:claude-plugin-developer` (per-agent description authoring); `nolte-shared:agent-review` for the conformance/routing check.
- **Depends on**: P2

### P4 — Regression guardrail in `validate_skills.py`

- **Problem statement**: Nothing prevents the aggregate description budget from silently creeping back toward the 15k ceiling.
- **Acceptance criteria**: `scripts/validate_skills.py` measures per-plugin aggregate description-token weight, holds the post-remediation baseline, and **fails** on regression above it; the check runs inside `task test` / CI. Measurement method documented for reproducibility.
- **Touched files / artifacts**: `scripts/validate_skills.py`, a baseline data file, `Taskfile.yml` (if wiring needed).
- **Specialist**: `nolte-engineering:fullstack-developer` (script/tooling) — candidate; re-resolve at dispatch.
- **Depends on**: P3 (baseline is post-remediation)

### P5 — Deep agent/skill rework (DEFERRED)

- **Problem statement**: The analysis (P1) may surface agents/skills warranting merge / split / retire / rewrite beyond descriptions.
- **Acceptance criteria**: Each such candidate is captured as its own feature under the roadmap item — **not** implemented in the analysis-slim-guardrail run (R8).
- **Touched files / artifacts**: TBD by P1 findings.
- **Specialist**: per-candidate at `feature-decompose` time.
- **Depends on**: P1

## Dependency ordering

P1 → P2 → P3 → P4 ; P5 depends on P1 and is deferred to later features.

## Risks

- **Routing regression from over-trim (R6/A2).** Aggressive description trimming can silently degrade specialist selection. Mitigation: the contract preserves the "when to activate / don't use for X → use Y" routing signal; `agent-review` spot-checks affected agents. Not a security-sensitive path — no `code-security-reviewer` / `security-review` requirement.
- **Guardrail baseline drift (A3).** A regression-only guardrail locks in whatever remediation achieves. Mitigation: set the baseline only after P3, record the measured number in the analysis.
- **Boundary decision reversing distribution-contract rule (R3).** A topic/count-driven split would violate `spec/claude/plugin-scoping/`. Mitigation: P1's decision is explicitly bound by that rule.
- **Pipeline-skill availability.** `roadmap-plan` validates outcome IDs against `goals.md`; O-1/O-2 confirmed present.

## Open questions

- **Contract home (A1)** — extend `spec/claude/skill-agent-frontmatter/` vs. `agent-management/` vs. a new spec: a design detail deferred to `feature-decompose` / the `spec` skill; does not block the route.

## Dispatch log

<!-- Pipeline route: no specialist dispatch by this skill. Hand-off to roadmap-plan recorded at the route gate. -->
