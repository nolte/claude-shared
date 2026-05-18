# Portfolio Tech Stack Capture

Status: draft

## Context

The `nolte/*` portfolio already declares **what** each repository delivers via `spec/portfolio/portfolio-management/`: a capability inventory in every Portfolio-Member's `project/portfolio.yml` plus a portfolio-wide audit and a rendered cross-repository inventory. What that spec deliberately doesn't address is **how** each repository is technically built—which languages, runtimes, frameworks, build tools, CI providers, dependency bots, documentation generators, linters, test runners, and deployment targets a given repository actually relies on. Two concrete consequences follow: the audit can flag two repositories that ship the same capability, but can't flag two repositories that ship the same capability on incompatible underlying stacks; and a new contributor reading the portfolio inventory can't see at a glance whether a repository uses `mkdocs` or `docusaurus`, `uv` or `poetry`, `task` or `make`.

This spec fills that gap by introducing a **portfolio-wide tech-stack capture** with a deliberate two-layer model:

1. A **portfolio-wide global tech stack** lives in this `claude-shared` repository, at `portfolio/tech-stack.yml`. It enumerates the technical building blocks that the portfolio standardises on—for example MkDocs as the documentation generator, Renovate as the dependency bot, GitHub Actions as the CI provider. Each entry is named, classified by `kind`, given a role, and assigned a lifecycle `status`. This file is the single source of truth for portfolio-wide defaults and is hand-authored by the `claude-shared` maintainer.

2. A **per-repository tech-stack block** lives in every Portfolio-Member repository's `project/portfolio.yml`, under a new top-level key `tech_stack:`. It carries two optional sub-blocks: `additions:` for repo-specific stack entries that have no portfolio-wide equivalent (for example a Home Assistant integration's repo-specific runtime constraint), and `overrides:` for opting out of a global entry that doesn't apply to this repository (with a mandatory rationale).

The inheritance contract is **additive with explicit overrides**: every Portfolio-Member implicitly inherits the full global stack; additions broaden it; overrides selectively suppress entries from the inherited set. Silent divergence is forbidden—a repository that doesn't use a global stack entry must say so explicitly via `overrides:`, never by omission.

Readers: maintainers of `nolte/*` repositories who author or revise `project/portfolio.yml`; the `portfolio-audit` skill which verifies cross-repository consistency; the `claude-shared` maintainer who curates `portfolio/tech-stack.yml`; contributors who need to understand the technical baseline a given repository relies on.

## Goals

- Every Portfolio-Member repository declares its technical building blocks in a uniform, machine-readable shape so the portfolio audit, documentation rendering, and contributor onboarding share one inventory.
- The portfolio-wide global stack is curated centrally in `claude-shared` so additions, deprecations, and renames propagate to every Portfolio-Member by inheritance without per-repository duplication.
- Repository-specific deviations from the global stack are explicit and auditable: every override carries a non-empty `rationale`, and every per-repo addition is visible alongside the inherited set.
- The audit can mechanically distinguish four divergence classes—undeclared deviation, missing rationale on override, declared entry not detected in repo signals, deprecated global entry still inherited—and route each to the canonical severity scale from `spec/claude/review-plan/`.
- The aggregated tech-stack inventory renders into the portfolio documentation site under `docs/<lang>/portfolio/` alongside the capability inventory, so a reader can answer both "who owns this capability" and "what stack does this repository use" from a single rendered page.
- The spec composes cleanly with `spec/portfolio/portfolio-management/`: the `project/portfolio.yml` schema gains exactly one new top-level key (`tech_stack:`), defined entirely by this spec; `portfolio-management` cross-references this spec rather than redefining the field shape.

## Non-Goals

- Recommending specific tools per `kind`. Whether MkDocs or `Docusaurus` belongs in the global docs slot, or whether Renovate or Dependabot owns the dep-bot slot, is the call of the `claude-shared` maintainer when authoring `portfolio/tech-stack.yml`. This spec defines the schema, not the contents.
- Version-pinning and version-upgrade workflow. Tracking which exact MkDocs version a repository uses, when to upgrade, and how to coordinate the upgrade across the portfolio is the concern of `spec/project/dependency-audit/` and Renovate, not this spec. The `version:` field defined here is descriptive, not enforced.
- License-compliance checks. Which licenses are allowed in the portfolio is governed by `dependency-audit`'s license-compliance pass; this spec records what a repository uses, not whether the licence is acceptable.
- Repository-internal build pipeline design. Once a repository declares its CI provider, build tool, and test runner, the actual workflow files, `Taskfile.yml` targets, and test commands are governed by `spec/project/project-structure/` and `spec/project/quality-gate/`, not by this spec.
- Cross-repository runtime dependency tracking. Which deployed service depends on which other deployed service at runtime is a release-pipeline concern; this spec stays at the per-repository declarative level.
- Migration tooling for consolidating repositories onto a shared stack entry. The audit identifies the deviation; the human-driven consolidation PR is its own work.
- A formal SAT-style resolver for inheritance conflicts. Inheritance is intentionally shallow (one global layer plus one consumer layer); no transitive multi-repository chains are modelled.
- Treating portfolio-anchor repositories (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`) as a special case. An anchor repository carries an ordinary `tech_stack:` block describing how the repository itself is built; what the anchor offers the portfolio (shared workflows, vocabularies, Taskfiles, etc.) is governed by `portfolio-management`'s capability inventory and remains orthogonal to this spec.

## Requirements

### Global tech-stack manifest

- **MUST** locate the portfolio-wide global tech-stack manifest at `portfolio/tech-stack.yml` in the `claude-shared` repository root. The directory `portfolio/` is introduced by this spec and is reserved for portfolio-wide source files that aren't specific to the own project shape of `claude-shared`.
- **MUST** structure `portfolio/tech-stack.yml` as a single top-level key `entries:` whose value is a list of tech-stack entries each conforming to §"Entry schema" below; the file **MUST NOT** carry per-repository sub-blocks (those live in each consumer's `project/portfolio.yml`).
- **MUST** be hand-authored and committed; the file is the single source of truth for portfolio-wide defaults, never generated from per-repo manifests.
- **MUST NOT** appear in any other repository under `nolte/*`. Only `claude-shared` owns the portfolio-wide global stack, and a Portfolio-Member repository that ships its own copy is a `Critical` audit finding.
- **MAY** carry a top-level `notes:` field with prose explaining curation conventions (for example "we standardise on Python 3.12 across the portfolio; runtime exceptions are recorded as per-repo overrides").

### Per-repository tech-stack block

- **MUST** require every Portfolio-Member repository's `project/portfolio.yml` to carry a top-level `tech_stack:` key once it adopts this spec. The key **MAY** be empty (`tech_stack: {}`) when the repository inherits the global stack unmodified.
- **MUST** allow exactly two sub-blocks under `tech_stack:`: `additions:` (a list of full entries per §"Entry schema") and `overrides:` (a list of override records per §"Inheritance semantics"). Both sub-blocks are individually optional; an empty `tech_stack:` is valid.
- **MUST NOT** re-declare an entry from the global stack inside `additions:` when the repository merely uses it as-is; implicit inheritance is the only authoring path for unmodified global entries.
- **MUST** keep `additions:` entry names unique across the union of (global entries minus this repo's `overrides:`) and (this repo's `additions:`). A repo-specific addition that shadows an inherited entry without an explicit override is a `Critical` audit finding.
- **MUST NOT** declare a tech-stack entry the repository doesn't actually use; the audit verifies declared entries against repository signals (for example: a `kind: package-manager` entry named `uv` requires a `uv.lock` or `[tool.uv]` block; a `kind: ci` entry named `github-actions` requires at least one workflow file under `.github/workflows/`).

### Entry schema

- **MUST** require each entry—whether in `portfolio/tech-stack.yml:entries[]` or in a consumer's `tech_stack.additions[]`—to carry the four mandatory fields:
  - `name`: kebab-case identifier, unique within its layer (global entries are unique across `portfolio/tech-stack.yml`; per-repo additions are unique within their `additions:` list).
  - `kind`: a value from the closed enum defined in §"Kind enum" below.
  - `role`: one prose sentence naming what the entry does for the repository or portfolio.
  - `status`: one of `active`, `experimental`, `deprecated`.
- **MAY** carry the optional fields:
  - `version`: free-form string (semver, range, or label). Descriptive only—not enforced and not the place to manage upgrades.
  - `since`: ISO date when the entry first appeared in the global stack or the repository.
  - `source_of_truth`: a repository-relative path or a portfolio-wide URL pointing at the authoritative declaration (for example `.tool-versions`, `pyproject.toml`, `renovate.json5`).
  - `deprecated_in_favor_of`: when `status: deprecated`, a `name` reference to the replacement entry.
  - `rationale`: prose sentence naming why this entry belongs in this layer. Optional at the entry level—but **required** on overrides (see §"Inheritance semantics").
- **MUST** ensure that every `deprecated_in_favor_of` reference resolves to an entry in the same layer whose `status` isn't itself `deprecated`; chained-deprecation references (entry A points at entry B which is also `deprecated`) are a `Warning` audit finding, since they leave no concrete migration target.
- **MUST** keep `name` values stable; renames are explicit decisions tracked in the manifest's git history, and a rename of a global entry **MUST** be coordinated with every consumer's `overrides:` referencing it within the same coordination window (one closed sprint at most).

### Kind enum

- **MUST** restrict `kind` to the following twelve values; any other value is a parse error:
  - `language`: a programming language the repository is written in (for example Python, Go, TypeScript).
  - `runtime`: the language runtime or interpreter (`CPython`, Node.js, Bun).
  - `framework`: an application framework or major library defining the repository's shape (FastAPI, React, Home Assistant).
  - `build`: a build orchestrator or task runner (Task, Make, `Gradle`).
  - `package-manager`: a dependency / lockfile manager (`uv`, poetry, `pnpm`, npm).
  - `ci`: a continuous-integration provider (GitHub Actions).
  - `dep-bot`: an automated dependency-update bot (Renovate, Dependabot).
  - `docs`: a documentation generator (MkDocs, `Docusaurus`).
  - `lint`: a linter or style checker (Ruff, `ESLint`, Vale).
  - `test`: a test runner or framework (`Pytest`, Vitest, Go test).
  - `deploy-target`: a deployment target or distribution channel (Docker image, GitHub Pages, PyPI).
  - `other`: fallback for entries that legitimately don't fit any of the above.
- **SHOULD** route an `other`-classified entry that persists across two consecutive quarterly portfolio audits or 180 days from first appearance (whichever comes first) to a catalog-gap finding (severity `Suggestion`), so the enum is revised before `other` becomes a hidden bucket. The quarterly-cadence anchor matches the audit-cadence MUST in `spec/portfolio/portfolio-management/` §Portfolio audit.

### Inheritance semantics

- **MUST** treat every Portfolio-Member repository as implicitly inheriting every entry from `portfolio/tech-stack.yml` whose `status` is `active` or `experimental` at audit time. A consumer doesn't re-declare inherited entries; their effective stack is the union of `(global active/experimental entries) minus (entries the consumer overrides with inherit: false) union (the consumer's additions)`.
- **SHOULD** promote a global entry from `status: experimental` to `status: active` once at least one Portfolio-Member has carried it as an inherited entry across one closed sprint without an `overrides:` record against it. The portfolio-wide promotion criterion for capability lifecycle vocabulary is tracked under `spec/portfolio/portfolio-management/` Open Questions and not settled there; this SHOULD encodes the tech-stack-specific default in the meantime so the §Portfolio audit integration severity table doesn't leave experimentally classified entries indefinitely stuck at `Suggestion` for missing signals.
- **MUST** structure each entry in `tech_stack.overrides[]` as an override record carrying exactly three fields: `name` (referencing an existing global entry's `name`), `inherit` (which **MUST** be set to `false`; the field is named explicitly for readability and to leave room for a future opt-in semantic without re-shaping the record), and `rationale` (a non-empty prose sentence):

  ```yaml
  overrides:
    - name: mkdocs
      inherit: false
      rationale: "static-only repo; documentation ships as plain markdown without a generator"
  ```

- **MUST** refuse a `tech_stack.overrides[]` record whose `name` doesn't resolve to an existing global entry; broken override references are a `Warning` audit finding.
- **MUST NOT** allow silent divergence from the global stack. A repository that ships a `kind: docs` artefact (rendered HTML output) without inheriting the global `docs` entry and without an explicit override is a `Warning` audit finding.
- **MUST NOT** allow `tech_stack.overrides[]` to alter any field of the inherited entry other than suppressing it. A consumer who needs a different `version` of an inherited entry does so by overriding the inherited entry with `inherit: false` plus a rationale **and** declaring a repo-specific replacement under `additions:` with the desired fields.
- **MUST** treat a global entry that transitions to `status: deprecated` as still inherited by every consumer until each consumer either overrides it or the global entry transitions to `deprecated_in_favor_of` resolution; the audit emits a `Suggestion` finding for every consumer still inheriting a deprecated entry after one closed sprint.

### Portfolio audit integration

- **MUST** extend the `portfolio-audit` skill defined by `spec/portfolio/portfolio-management/` to verify tech-stack consistency in the same audit run that verifies capability consistency; no separate `tech-stack-audit` skill is introduced.
- **MUST** classify tech-stack findings using the canonical severity scale from `spec/claude/review-plan/`:
  - `Critical`: a Portfolio-Member ships its own `portfolio/tech-stack.yml` (forbidden duplication); a per-repo `additions:` entry shadows an inherited entry without a corresponding override.
  - `Warning`: an override references a global entry that doesn't exist; a declared entry with `status: active` isn't detected in repo signals; a consumer renders documentation HTML without inheriting the global `docs` entry and without an explicit override. **Rationale-downgrade clause:** a `status: active` entry whose `rationale` field carries an acknowledged-missing-signal marker (as written by the capture skill per `spec/portfolio/tech-stack-discovery/` §Discovery sequence per repository) is downgraded from `Warning` to `Suggestion`.
  - `Suggestion`: a global entry is `deprecated` and at least one consumer still inherits it after one closed sprint; an `other`-classified entry has persisted across two consecutive quarterly audits or 180 days from first appearance; an inherited entry with `status: experimental` isn't detected in repo signals (looser threshold than `active`, since experimental entries are explicitly probationary).
  - `Info`: observations that don't yet require action (for example a global entry with `since` younger than one closed sprint; an experimental entry with no consumer pickup yet).
- **MUST** verify repository signals for at least the following classes:
  - `kind: package-manager`: lockfile or tool-config presence matching the entry's `name` (for example `uv.lock` for `name: uv`).
  - `kind: ci`: at least one provider-specific workflow file (for example `.github/workflows/*.yml` for `name: github-actions`).
  - `kind: dep-bot`: bot-specific config presence (for example `renovate.json5` for `name: renovate`).
  - `kind: docs`: generator config presence (for example `mkdocs.yml` for `name: mkdocs`).
  - `kind: lint`: linter config presence (for example `.vale.ini` for `name: vale`, `pyproject.toml:[tool.ruff]` for `name: ruff`).
- **MAY** dispatch a read-only specialist agent for the per-signal probing of large repositories; the orchestration stays in the `portfolio-audit` skill per `spec/claude/skill-vs-agent/`.

### Documentation rendering

- **MUST** extend the portfolio documentation rendering defined by `spec/portfolio/portfolio-management/` to include a tech-stack section per Portfolio-Member, alongside the capability section. Rendering target: `docs/<canonical_language>/portfolio/` with translations under every other configured language.
- **MUST** render the global stack as a separate top-level section preceding the per-repository inventory, so a reader can see the portfolio-wide baseline before drilling into specific repositories.
- **MUST** show each consumer's effective tech-stack: the inherited entries (marked with an "inherited" badge), the consumer's `additions:` (marked with a "repo-specific" badge), and the consumer's `overrides:` (marked with a "suppressed" badge and surfacing the rationale).
- **MUST** be generated automatically from `portfolio/tech-stack.yml` plus every Portfolio-Member's `project/portfolio.yml`; the rendered files **MUST NOT** be hand-edited.
- **SHOULD** visualise the kind-distribution across the portfolio with a Mermaid diagram authored per `spec/project/mermaid-diagrams/` (for example a `flowchart` aggregating `kind` counts per repository) so structural outliers (a repo with no `test` entry, a repo with two `language` entries) are visible at a glance. Non-Mermaid chart formats fall outside the portfolio-wide diagram catalog and aren't used here.
- **SHOULD** include a per-consumer **delta view** alongside the effective-stack view: a compact list of inherited entries the consumer suppressed via `overrides:` (with rationale) and `additions:` the consumer introduced. The delta view sharpens drift awareness; the effective-stack view above remains the default reading order so casual readers don't pay the delta-view cognitive cost.

### Cross-references with portfolio-management

- **MUST** keep the `project/portfolio.yml` capability schema defined by `spec/portfolio/portfolio-management/` unchanged; this spec contributes exactly one new top-level key (`tech_stack:`).
- **MUST** be referenced from `spec/portfolio/portfolio-management/` (canonical and every translation) with a one-sentence pointer that names this spec as the owner of `tech_stack:`; redefining the field shape inside `portfolio-management` is forbidden.
- **MUST NOT** require any other field of `project/portfolio.yml` to change. Capability entries are unaffected; audiences are unaffected; peer references are unaffected.

### Cross-references with tech-stack-discovery

- **MUST** treat `spec/portfolio/tech-stack-discovery/` as the owner of the discovery methodology, the audience model, and the benefits prose for the tech-stack inventory; restating any of the three inside this schema spec is forbidden. This spec defines the entry shape, the inheritance contract, the audit-severity table, and the rendering contract; the sibling defines how an entry gets captured, who consumes the resulting inventory, and why the curation overhead pays back.
- **MUST** stay in sync with `spec/portfolio/tech-stack-discovery/` across revisions: a change to the `kind` enum, the inheritance contract, or the audit-severity table that affects the discovery flow or the audience model triggers a matching revision of the sibling spec in the same coordination window (one closed sprint at most).

## Acceptance Criteria

- [ ] `portfolio/tech-stack.yml` exists in the `claude-shared` repository root with at least one entry conforming to §"Entry schema."
- [ ] `git blame portfolio/tech-stack.yml` shows only maintainer-authored commits; no automated-generation commit appears in its history, verifying the hand-authoring MUST in §"Global tech-stack manifest."
- [ ] A schema-validation check for `portfolio/tech-stack.yml` runs in CI or pre-commit and rejects malformed entries, kind-enum violations, schema-violating field types, or missing mandatory fields; the check produces zero failures on the current HEAD.
- [ ] Every active Portfolio-Member's `project/portfolio.yml` carries a top-level `tech_stack:` key (possibly empty), with any `additions:` and `overrides:` conforming to this spec.
- [ ] Every `tech_stack.overrides[]` record resolves to an existing global entry; running the broken-override-reference check produces zero `Warning` findings.
- [ ] Every rename or deletion of a global-stack entry surfaces via the broken-override-reference check above within the next audit run; no `Warning`-grade override-reference finding persists beyond the one-closed-sprint rename-coordination window defined in §"Entry schema."
- [ ] Every entry with `status: deprecated` carrying `deprecated_in_favor_of` resolves to an entry in the same layer whose `status` isn't itself `deprecated`; running the deprecation-chain check produces zero `Warning` findings.
- [ ] Every `tech_stack.overrides[]` record has a non-empty `rationale`; running the rationale-presence check on overrides produces zero `Warning` findings.
- [ ] No Portfolio-Member repository other than `claude-shared` ships its own `portfolio/tech-stack.yml`; running the duplicate-global-manifest check produces zero `Critical` findings.
- [ ] No per-repo `additions:` entry shadows an inherited global entry without a corresponding `overrides:` record; running the shadow-without-override check produces zero `Critical` findings.
- [ ] For every declared entry whose `kind` is one of the signal-verified classes (`package-manager`, `ci`, `dep-bot`, `docs`, `lint`), the audit detects the matching repository signal; running the signal-presence check produces zero `Warning` findings.
- [ ] The portfolio-audit skill's spec acceptance criteria gain a tech-stack-coverage check; the resulting audit Findings-Report includes a `## Tech stack` subsection (or equivalent).
- [ ] The canonical `spec/portfolio/portfolio-management/en.md` and every existing translation each carry a one-sentence cross-reference to this spec naming it as the owner of the `tech_stack:` block.
- [ ] The rendered portfolio inventory under `docs/<canonical_language>/portfolio/` includes both a "Global tech stack" section and per-repository tech-stack subsections with inherited/repo-specific/suppressed badges.

## Open Questions

None at this revision. The questions surfaced during the spec-readiness audits were resolved as follows: structured `version:` shape and mandatory `source_of_truth:` for selected kinds are deferred (free-form / optional remain sufficient for the MVP capture flow); the `kind: other` escalation window is calibrated below to "two consecutive quarterly audits or 180 days, whichever comes first"; an explicit `replaces:` field on the global stack isn't added (`deprecated_in_favor_of` already covers the migration cue); a third per-repo `notes:` sub-block isn't added (catch-all-bucket risk); the documentation rendering delta-view is added below as a SHOULD alongside the effective-stack MUST. Future revisions may surface new questions as the capture skill and the portfolio audit land.
