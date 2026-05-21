# Skills and Agents Sweep Audit

Status: draft

## Context

The `skill-review` and `agent-review` specs define how a single artifact is reviewed: which rules a reviewer checks, in which order, and what plan is produced. What they don't define is how to audit the entire plugin inventory as a coherent system. Per-artifact reviews are deliberately isolated: each plan focuses on one skill or agent and doesn't consider how that artifact relates to all its neighbors.

Portfolio-wide concerns are systematically invisible to per-artifact reviews. Boundary conflicts between two skills only surface when both are reviewed in the same session with explicit cross-referencing. Spec-induced gaps -- where a spec requires a skill or agent that doesn't yet exist -- are never caught by reviewing existing artifacts. Operations-vocabulary drift accumulates across the inventory without any single per-artifact finding calling it out. Naming inconsistencies and lifecycle-ordering gaps require an inventory-wide view to detect.

This spec codifies the methodology for a skills-and-agents sweep audit: a periodic, portfolio-wide procedure that supplements per-artifact reviews with cross-cutting analysis. The methodology was developed empirically during the 2026-05-20 baseline sweep of the `nolte-shared` plugin (34 skills, 9 agents) and is documented in `.audits/skills-agents-sweep/2026-05-20-baseline.md`. This spec generalises that experience into a repeatable procedure.

## Goals

- Every sweep audit applies the same cross-cutting analysis dimensions, in the same order, producing a consolidated report that's comparable across sweep instances
- Cross-cutting findings -- boundary conflicts, spec-induced phantom skills, operations-vocabulary drift, naming inconsistencies, incorrect skill-vs-agent classification decisions -- are detected systematically and cited with specific artifact pairs or spec paths
- Plugin developers can plan implementation waves from the consolidated report without having to re-derive priorities from 40-plus individual plan files
- The wave-based implementation roadmap produced by each sweep is ordered by effort times impact, distinguishing mechanical sweeps from spec extensions from structural new artifacts, so contributors can execute waves in parallel or sequentially without coordination overhead
- The sweep procedure is tool-agnostic: it can be executed manually by a human reviewer, driven by an LLM session, or operationalised by a future `skills-agents-sweep` skill without changing the output contract
- The lifecycle invariant -- exactly one open sweep at a time, closed only when every wave item is resolved or explicitly deferred -- prevents overlapping audits from producing a contradictory implementation roadmap

## Non-Goals

- Defining how individual skills are authored: `skill-management` owns that
- Defining how individual agents are authored: `agent-management` owns that
- Defining the per-artifact review procedure: `skill-review` and `agent-review` own that; this spec dispatches those procedures but doesn't restate them
- Prescribing the per-artifact plan format: `review-plan` owns that
- Auditing Vale vocabularies for upstream drift: `vocab-drift-audit` owns that
- Checking runtime or behavioral correctness of skills or agents
- Checking linting and markdown-style issues already enforced by `task lint` / Vale / pre-commit hooks
- Auditing spec files themselves for internal consistency or audience fit: `spec-readiness-reviewer` owns that

## Requirements

### Sweep scope

- **MUST** cover every skill under `skills/<name>/` and every agent under `agents/<name>.md` in the repository at the time the sweep is opened
- **MUST** record the repository revision (git SHA) at which the sweep was opened, in the consolidated report frontmatter
- **MUST** analyse the following cross-artifact dimensions: boundary conflicts and overlaps, workflow-chain documentation, spec-induced gaps, adoption friction, operations-vocabulary consistency, skill-vs-agent classification correctness, and naming consistency
- **MAY** narrow the sweep to a subset of artifacts by lifecycle phase or frontmatter tag when the sweep is triggered by a specific concern, and **MUST** record the narrowing in the consolidated report's scope section so that reviewers know which artifacts were excluded

### Triggers

- **MUST** run before each major plugin release (a release that increments the first version segment)
- **SHOULD** run when more than five new skills or agents have landed on `develop` since the last sweep was closed
- **MAY** run ad hoc when a contributor suspects cross-artifact drift that per-artifact reviews would not surface

### Phases of a sweep

- **MUST** execute the following phases in order: (1) per-artifact reviews delegated to `skill-review` and `agent-review`, (2) cross-cutting analysis across all artifacts, (3) consolidated report authoring, (4) wave-based implementation
- **MUST** persist the consolidated report under `.audits/skills-agents-sweep/<date>-<slug>.md` before beginning phase 4
- **MUST NOT** begin phase 4 implementation before the consolidated report exists on disk, so that every implementation PR can reference the report as its evidence source
- **SHOULD** execute per-artifact reviews in phase 1 before cross-cutting analysis in phase 2, because the per-artifact plans surface individual findings that feed the cross-cutting dimensions

### Cross-cutting dimensions

- **MUST** analyse the boundary matrix: for every pair of artifacts whose descriptions address overlapping trigger phrases, record the overlap, propose a resolution (merge, rename, or bidirectional "Don't use for" clause), and classify the pair as conflict, adjacent, or chain
- **MUST** inventory spec-induced gaps: for every `spec/` path referenced in any skill or agent body that doesn't correspond to an existing skill or agent, record the gap, the referencing artifacts, and a proposed resolution
- **MUST** classify every finding by implementation wave: mechanical sweep (automated or near-automated edit), spec extension (requires a spec change before implementation), or structural new artifact (requires authoring a new skill or agent)
- **MUST** analyse skill-vs-agent classification: for every skill and agent, verify the rationale section justifies the chosen artifact type using the decision criteria from `spec/claude/skill-vs-agent/`; cases that don't match the decision criteria are findings
- **SHOULD** analyse operations-vocabulary consistency: detect skills that use non-standard operation headings or operation verbs, and record deviations against the vocabulary defined in `spec/claude/skill-management/`
- **SHOULD** analyse naming consistency: detect artifacts whose names deviate from the dominant naming convention in their lifecycle cluster (gerund or verb-noun form), and record the deviation with a proposed canonical form
- **SHOULD** distinguish findings that block release (failed MUST rules, Critical per `review-plan`) from findings that are deferrable (failed SHOULD, Warning or Suggestion per `review-plan`)

### Consolidated report format

- **MUST** contain all of the following sections, in this order: YAML frontmatter, executive summary with top findings table, artifact inventory table, boundary matrix, spec-induced gap inventory, adoption-friction analysis, skill-vs-agent classification findings, wave-based implementation roadmap, and a processing log
- **MUST** include in the YAML frontmatter: `audit-type: skills-agents-sweep`, `target`, `scope` (artifact counts), `repo-revision`, `created` (ISO date), `status: open`, and `per-artefact-plans` (count)
- **MUST** cite the per-artifact plan paths under `.audits/skill-review/` and `.audits/agent-review/` in the executive summary so that reviewers can trace cross-cutting findings to specific per-artifact evidence
- **SHOULD** include a go/no-go recommendation in the executive summary that states whether Critical findings block release promotion

### Wave-based implementation roadmap

- **MUST** sort proposed PRs by effort times impact, making the ordering rationale explicit in the roadmap section
- **MUST** distinguish mechanical sweep PRs (no spec change required), spec-extension PRs (spec change is a precondition), and structural new-artifact PRs (require authoring a new skill or agent)
- **MUST** express ordering constraints between waves when a later wave depends on a spec change or a new artifact introduced in an earlier wave
- **SHOULD** propose three to six waves, where wave 1 contains the highest-impact mechanical fixes and later waves contain structural changes that depend on earlier waves completing

### Lifecycle

- **MUST** maintain exactly one open sweep per repository at a time; a second sweep **MUST NOT** be opened until the previous sweep is closed
- **MUST** be closed via a commit that removes the consolidated report file from `.audits/skills-agents-sweep/`; the commit message **MUST** follow the pattern `sweep(skills-agents-sweep): close <slug>--<wave-summary>` where `<wave-summary>` describes which waves were implemented or deferred
- **MUST** record in the consolidated report's processing log one entry per wave closure, with the date, the wave identifier, the action taken, and a verification method
- **SHOULD** be considered stale and requiring re-opening if it has been open for more than six months without a processing-log entry

### Relationship to other specs

- **MUST** reference `spec/claude/skill-review/` and `spec/claude/agent-review/` as the procedures for per-artifact reviews dispatched in sweep phase 1; don't restate their requirements here
- **MUST** reference `spec/claude/review-plan/` for the per-artifact plan format; don't restate its requirements here
- **MUST NOT** duplicate checks already covered by `skill-review` or `agent-review`; cross-cutting analysis only covers dimensions that require seeing the full inventory simultaneously
- **SHOULD** coordinate with `spec/project/spec-drift-audit/` by noting that `spec-drift-audit` covers spec-file content drift while `skills-agents-sweep` covers artifact-to-spec binding gaps; the two specs have different scopes and complementary findings

## Acceptance Criteria

- [ ] Every consolidated sweep report under `.audits/skills-agents-sweep/` contains all required sections in the required order, and the YAML frontmatter contains all required fields
- [ ] Every wave proposed in the roadmap section is either implemented with a PR reference, deferred with a tracked issue reference, or explicitly retired with a stated rationale
- [ ] No skill or agent referenced in a "Don't use for ... use X instead" clause anywhere in the plugin points at a non-existent artifact slug
- [ ] The most recent consolidated sweep report was opened within the last six months, or a sweep is currently open
- [ ] Every per-artifact plan path cited in the executive summary resolves to an existing file under `.audits/skill-review/` or `.audits/agent-review/` at the time the report was written
- [ ] The processing log in the consolidated report contains one entry per closed wave, each with date, wave identifier, action, and verification method

## Open Questions

- Should the sweep methodology codify a specific subagent-based execution pattern for phase 1 (for example, spawning one `skill-review` subagent per skill in parallel), or should the methodology remain tool-agnostic and leave execution strategy to the operator?
- How's sweep coordination handled when multiple contributors are working on the same repository? The single-open-sweep invariant prevents parallel sweeps, but doesn't define a lock mechanism.
- Should the consolidated report's go/no-go recommendation be machine-readable (for example, a `release-blocker: true/false` frontmatter field) to allow the `release-publish-trigger` skill to gate on it automatically?
- How's the sweep coordinated with the periodic `spec-drift-audit` procedure? The two specs have different scopes (`skills-agents-sweep` covers artifact-to-spec binding under `spec/claude/`; `spec-drift-audit` covers spec-file content under `spec/project/`), but a single contributor session might want to run both. Should there be a combined entry point?
