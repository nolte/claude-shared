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
status: active
```

The plugin demonstrates its own planning-suite specs by self-application: `project/goals.md`, `project/roadmap.md`, `project/features/`, `project/sprints/`, and `project/mission.md` exist as a reference adopter, and at least one sprint runs end-to-end (`planned → active → review → closed`) delivering the mission statement against a verifying acceptance criterion. This satisfies O-3 ("every spec the plugin ships is dogfooded before downstream adoption") because the proof-of-life happens here first.

- [ ] mission-statement-published

## Phase 2 — Release & Quality Discipline

### R-2 — Release pipeline automated end-to-end

```yaml
id: R-2
title: Release pipeline automated end-to-end
detail: fine
outcomes: [O-1, O-2]
target_sprint: 2
mvp: false
status: proposed
```

Consumers of the `nolte-shared` plugin install a published, non-draft release of `claude-shared` whose publication was performed by the repo's own pipeline rather than by a manual `gh release edit`. The path runs from a develop merge through `release-drafter` (changelog aggregation) and `release-publish.yml` (the publish workflow), gated by the `release-publish-trigger` skill which validates every pre-publish condition locally before dispatching. Closing the remaining `ci.yml` `workflow_dispatch` gap lets the skill's required-checks gate pass and produces the first end-to-end published release.

- [ ] plugin-published-via-automated-release

### R-3 — Develop branch quality gate hardened

```yaml
id: R-3
title: Develop branch quality gate hardened
detail: backlog
outcomes: [O-2, O-3]
target_sprint: null
mvp: false
status: proposed
```

Make the develop quality gate (lint, tests, Vale, Renovate, pre-commit) genuinely block regressions before they reach consumers.

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
