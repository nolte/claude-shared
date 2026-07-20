---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "416"
classification: "feature-request"
secondary-classes: ["refactor", "spec-change"]
route: "pipeline"
status: approved
created: "2026-07-20"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #416 — Shared-plugin deep agent/skill rework + finer-grained plugin boundary (R-9/P5 follow-on)
- **URL**: <https://github.com/nolte/claude-shared/issues/416>
- **Labels**: enhancement, skills, agents
- **Author**: nolte (trusted: repository owner/operator)
- **Linked items**: origin #371 (closed, delivered v0.1.11); roadmap R-9 (done); sprint 0005 (closed).
- **Prior art checked**: `.audits/shared-plugin-analysis/2026-07-19.md` (F-5 analysis: keep-and-slim verdict, no duplicate capabilities found, authoring-slice is skill-shaped); `project/requirements/shared-plugin-restructure.md` (from #371, `U_gate = 0.8 ≥ τ_high`) — its **R2/R3** (boundary decision + distribution-contract split justification) and **R8** (pipeline routing of the deep rework) already state #416's two strands, so the requirements gate is cleared without a fresh `requirements-elicit`. No existing feature or roadmap item covers this follow-on; R-9's own features are all `done`.

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: refactor (the deep agent/skill rework), spec-change (a possible `spec/claude/plugin-scoping/` refinement if the carve-out is taken)
- **Rationale**: The issue requests a new capability posture — finer-grained, opt-into-able plugin boundaries and a leaner reworked artefact surface — not a defect fix. It is the deferred continuation of #371's P5 strand.

## Scope

- **In scope** (handed to the planning pipeline): the two deferred strands — (1) deep agent/skill rework where an analysis warrants it, (2) the finer-grained plugin-boundary / authoring-slice carve-out re-evaluation on a skill-budget/audience axis. Both routed to `roadmap-plan` as a new Backlog roadmap item.
- **Out of scope**: any hands-on merge/split/retire/rewrite or plugin split in this run (that is the decomposed features' work, gated on a candidate sweep and a boundary decision); the agent-description budget itself (settled and guardrailed by R-9); the `nolte-media` / `nolte-engineering` boundaries (unless a future analysis flags a distribution-contract reason).

## Route

- **Decision**: pipeline
- **Rationale**: The issue spans both goal outcomes (O-1 install-fit via the boundary; O-2 authoring discipline via the rework), needs more than one coherent PR strand, and requires a **new roadmap item** (R-9 is `done`). Per the orchestration hard rules an issue with more than one outcome / PR strand / a new roadmap item routes to the formal pipeline and is never decomposed for direct implementation. It is also not yet sprint-ready: the deep rework is "where warranted" and depends on a fresh `skills-agents-sweep` to surface concrete candidates first, so the new roadmap item lands as **Backlog** (`target_sprint: null`).
- **Pipeline hand-off**: `roadmap-plan` — add a new roadmap item under outcomes **O-1** (finer-grained boundary keeps consumers loading only what they use) and **O-2** (a leaner, drift-free artefact surface is one-place authoring discipline). `feature-decompose` later decomposes it into the P-strands below, once the candidate sweep and the boundary decision have run.

## Work packages

> Pipeline route: these are **strand shapes handed to `roadmap-plan` / `feature-decompose`**, not packages this skill dispatches. Each carries a testable acceptance criterion so the planning pipeline can lift it into a feature.

### P1 — Candidate-surfacing sweep (analysis gate for the rework)

- **Problem statement**: F-5 found no duplicate capabilities and clean family clusters, so deep-rework candidates are not yet identified. Before any merge/split/retire/rewrite, a fresh `skills-agents-sweep` (+ targeted `agent-review` / `skill-review`) must surface concrete candidates with evidence.
- **Acceptance criteria**: A consolidated sweep report under `.audits/skills-agents-sweep/` lists each rework candidate (agent/skill), the observed overlap/dead-capability/drift, and the proposed action (merge/split/retire/rewrite), or explicitly records that none warrant rework.
- **Specialist (resolved at feature-decompose time)**: `skills-agents-sweep` skill.
- **Depends on**: none.

### P2 — Per-candidate deep rework (one feature each)

- **Problem statement**: Each candidate P1 surfaces is reworked beyond its description — merged, split, retired, or rewritten — while preserving routing correctness and consumer compatibility.
- **Acceptance criteria**: Per candidate, the rework lands with routing preserved (spot-checked via `agent-review`/`skill-review`), `validate_skills.py` green, and the `dont_use_when`/`see_also` cross-reference graph kept consistent; each is its own feature and PR.
- **Specialist**: per-candidate (`claude-plugin-developer` / `skill-management` for authoring; `agent-review`/`skill-review` for verification).
- **Depends on**: P1.

### P3 — Authoring-slice carve-out decision (finer-grained boundary)

- **Problem statement**: Consumers cannot opt into a slice of `nolte-shared` (#371 observation 4). F-5 declined the authoring-slice carve-out *for the agent-description budget* (five skills + one 122 t agent), but it remains open on a **skill-mechanism budget + consumer-audience** axis: most consumers never author a plugin/skill yet load the authoring slice's skill descriptions every turn.
- **Acceptance criteria**: A written decision (split vs. keep), bound by `spec/claude/plugin-scoping/`, justified by skill-budget/audience (never topic/count), weighed against the fourth-plugin lockstep-versioning cost. If split → a follow-on execution feature; if keep → recorded rationale closing the question.
- **Specialist**: authored prose / `spec` skill (if a `plugin-scoping` refinement results); measurement analogous to F-5 but over the skill surface.
- **Depends on**: none (independent of P1/P2).

## Dependency ordering

P1 → P2 ; P3 independent. All three are Backlog features under the new roadmap item; none is sprint-scheduled by this run.

## Risks

- **Premature decomposition.** Turning "deep rework where warranted" into features before P1's sweep would fabricate work. Mitigation: P1 is the gate; P2 features are created only for surfaced candidates.
- **Boundary decision reversing the distribution-contract rule.** A topic/count-driven split would violate `spec/claude/plugin-scoping/`. Mitigation: P3's decision is explicitly bound by that rule and re-uses F-5's method on the skill axis.
- **Scope creep back into the settled agent-description budget.** R-9 settled and guardrailed it; this follow-on must not re-open it. Mitigation: the out-of-scope boundary above.

## Open questions

- **Roadmap-item granularity** — RESOLVED (operator, 2026-07-20): **one Backlog item** covering all three strands (P1/P2/P3); `feature-decompose` later separates the strands into features. No open questions remain.

## Dispatch log

<!-- Pipeline route: no specialist dispatch by this skill. Hand-off to roadmap-plan recorded at the route gate (2026-07-20). -->
