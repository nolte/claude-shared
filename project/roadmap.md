# Roadmap

The queue of work for the `claude-shared` repository. See `project/goals.md` for the Vision and the outcomes this queue serves. Items are ordered top-to-bottom by priority; phase headings are documentation, not schema.

## Phase 1 — Planning suite dogfood adoption

### R-1 — Planning-suite dogfood adoption complete

```yaml
id: R-1
title: Planning-suite dogfood adoption complete
detail: fine
outcomes: [O-3]
target_sprint: 1
mvp: true
status: done
```

The plugin demonstrates its own planning-suite specs by self-application: `project/goals.md`, `project/roadmap.md`, `project/features/`, `project/sprints/`, and `project/mission.md` exist as a reference adopter, and at least one sprint runs end-to-end (`planned → active → review → closed`) delivering the mission statement against a verifying acceptance criterion. This satisfies O-3 ("every spec the plugin ships is dogfooded before downstream adoption") because the proof-of-life happens here first.

- [x] mission-statement-published

## Phase 2 — Release & Quality Discipline

### R-2 — Release pipeline automated end-to-end

```yaml
id: R-2
title: Release pipeline automated end-to-end
detail: fine
outcomes: [O-1, O-2]
target_sprint: 2
mvp: false
status: done
```

Consumers of the `nolte-shared` plugin install a published, non-draft release of `claude-shared` whose publication was performed by the repo's own pipeline rather than by a manual `gh release edit`. The path runs from a develop merge through `release-drafter` (changelog aggregation) and `release-publish.yml` (the publish workflow), gated by the `release-publish-trigger` skill which validates every pre-publish condition locally before dispatching. Closing the remaining `ci.yml` `workflow_dispatch` gap lets the skill's required-checks gate pass and produces the first end-to-end published release.

- [x] plugin-published-via-automated-release

### R-3 — Develop branch quality gate hardened

```yaml
id: R-3
title: Develop branch quality gate hardened
detail: fine
outcomes: [O-2, O-3]
target_sprint: null
mvp: false
status: proposed
```

The lint/test/docs gate already runs on every `develop`-bound PR (per `.github/workflows/ci.yml` jobs `lint`, `test`, `docs` and `.github/settings.yml` `required_status_checks.contexts`), and `.pre-commit-config.yaml` mirrors the lint category locally. The remaining gap is conformance against `spec/project/quality-gate/` §Acceptance criteria #7 (README names the gate target plus expected output shape) and the documented pre-commit-vs-CI scope, so a new contributor can reproduce the gate on day one without reading the source tree.

- [ ] quality-gate-spec-conformance-gaps-closed

### R-8 — Reviewer agent coverage across every skill cluster

```yaml
id: R-8
title: Reviewer agent coverage across every skill cluster
detail: fine
outcomes: [O-1, O-2]
target_sprint: 4
mvp: false
status: done
```

Every skill cluster gets a read-only reviewer agent paired with its existing "apply"-style skill. The six agents follow two templates: `feature-consistency-reviewer` for plan / sprint / quality clusters, and `vocab-drift-scanner` / `docs-freshness-checker` for drift-style audits. Delivers systematic review depth for roadmap, project structure, sprint, quality-gate, Mermaid diagrams, and tech-stack drift — a gap that "apply"-only skills leave open today.

- [x] roadmap-coherence-reviewer agent (#152)
- [x] project-structure-reviewer agent (#153)
- [x] sprint-readiness-reviewer agent (#154)
- [x] quality-gate-enforcer agent (#155)
- [x] mermaid-diagram-reviewer agent (#156)
- [x] tech-stack-drift-reviewer agent (#157)

## Phase 3 — Documentation Reach

### R-4 — Bilingual docs published with skill-agent catalog

```yaml
id: R-4
title: Bilingual docs published with skill-agent catalog
detail: backlog
outcomes: [O-1, O-3]
target_sprint: null
mvp: false
status: proposed
```

Publish the bilingual MkDocs site with a generated skill-and-agent catalog so consumers can discover every shipped capability without reading the source tree.

### R-5 — Portfolio inventory rendered and audited

```yaml
id: R-5
title: Portfolio inventory rendered and audited
detail: backlog
outcomes: [O-1, O-2]
target_sprint: null
mvp: false
status: proposed
```

Render and audit the cross-repository capability inventory across `nolte/*` so duplicate or gap-causing capabilities surface portfolio-wide.

### R-7 — Tech-stack capture per repo wired into portfolio inventory

```yaml
id: R-7
title: Tech-stack capture per repo wired into portfolio inventory
detail: backlog
outcomes: [O-1, O-2, O-3]
target_sprint: null
mvp: false
status: proposed
```

Capture each repository's tech stack as a two-layer model — a portfolio-wide global stack authored in `claude-shared` itself (e.g. MkDocs as the standard documentation stack, Renovate as the standard dependency-bot) plus per-repository extensions declared in each consumer's `project/portfolio.yml` — driven by a new spec and a Claude Code skill that detects entries from repo signals and confirms them interactively.

## Phase 4 — Consumer Adoption Proof

### R-6 — Plugin install path validated against a downstream consumer

```yaml
id: R-6
title: Plugin install path validated against a downstream consumer
detail: backlog
outcomes: [O-1]
target_sprint: null
mvp: false
status: proposed
```

Validate the `nolte-shared` install path by running at least one slash command end to end inside a separate nolte portfolio repository.
