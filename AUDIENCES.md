# Audiences — `nolte-shared` plugin (this repository)

<!--
Produced via the `audience-identify` skill, following
spec/project/audience-identification/.
Do not add audiences without first declaring the bounded context below.

Per-audience `id:` and `track:` fields were added 2026-05-19 to satisfy
spec/project/audience-identification/ §Requirements (per-audience track key) and
spec/project/docs-audience-tracks/ §Audience-to-track mapping. The portfolio
baseline mapping is applied (user → user-docs; contributor / operator /
release-manager / governing → developer-docs); the `audience:` frontmatter
values in `docs/<lang>/` pages reference the `id` listed alongside each entry.
-->

## Bounded context

**What this context *is***:

- The repository `nolte/claude-shared`, published as the Claude Code plugin `nolte-shared` (currently `0.1.3` in `.claude-plugin/plugin.json`) via the plugin marketplace.
- It bundles reusable **skills** (`skills/<name>/SKILL.md`), **agents** (`agents/<name>.md`) and **specs** (`spec/`, EN-canonical, partly with DE translations) for portfolio-wide use.
- It also contains the MkDocs documentation setup (`docs/`, bilingual) and the Taskfile-based automation.

**Where the boundaries run**:

- External surfaces: the plugin manifest + marketplace entry (install path), the slash commands (e.g. `/nolte-shared:spec`), the agent definitions, and the published MkDocs site (including the auto-generated skill / agent catalog under `docs/<lang>/skills/` and `docs/<lang>/agents/` and the `docs/lifecycle.md` development-lifecycle page).
- The repo itself, the `develop`/`main` branches, and the CI workflows are part of the context.
- The planning-suite artefacts under `project/` (`mission.md`, `goals.md`, `roadmap.md`, `features/`, `sprints/`) are internal surface — they describe how the plugin governs its own evolution and are read by downstream specs that reference the planning suite (`mission`, `roadmap`, `sprint`, `feature`, `release-skill-layer`).

**What is explicitly *outside***:

- The downstream projects that install the plugin — their internal workflows are not this context.
- The related repos `nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles` — they are dependencies, not part of this context.
- Claude Code itself (the CLI/IDE integration) — the plugin builds on it but does not own it.
- Content concerns internal to individual skills — each has its own, narrower context if audited separately.

## Audiences

Each entry: label, relationship category, interaction surface, expectation,
open questions, `confirmed` or `assumed`, criticality (primary / secondary /
peripheral). Mark a whole category as `none — <reason>` when it does not apply.

### Direct consumers

- **Downstream Claude Code users in portfolio projects** — _id_: `downstream-user` · _category_: direct-consumer · _track_: `user-docs` · _surface_: plugin slash commands (e.g. `/nolte-shared:spec`, `/nolte-shared:skill-management`, `/nolte-shared:pull-request-create`) and sub-agents · _expects_: consistent, spec-compliant workflows without per-repo reimplementation; stable command names; reproducible outputs · _status_: `assumed` · _criticality_: primary
  - Open questions: Which repos / which people are using this plugin in practice today?

- **Plugin author dogfooding inside this repo** — _id_: `dogfooding-author` · _category_: direct-consumer · _track_: `developer-docs` (override of portfolio baseline: dogfooding is a contributor-class surface, not an end-user surface) · _surface_: `claude --plugin-dir .`, `/reload-plugins`, local skill invocation while developing; planning-suite skills (`/nolte-shared:mission-define`, `/nolte-shared:mission-revise`, `/nolte-shared:roadmap-init`, `/nolte-shared:roadmap-plan`, `/nolte-shared:roadmap-refine`, `/nolte-shared:sprint-plan`, `/nolte-shared:sprint-execute`, `/nolte-shared:sprint-review`, `/nolte-shared:feature-decompose`, `/nolte-shared:audience-identify`) applied to `claude-shared` itself, mutating `project/mission.md`, `project/goals.md`, `project/roadmap.md`, `project/features/`, `project/sprints/`, and `AUDIENCES.md` in-repo · _expects_: changes to skills/agents/specs become callable immediately without reinstall; skills also function against this repo itself (e.g. running `audience-identify` on `nolte-shared`); the planning-suite-on-self loop stays self-consistent across spec revisions · _status_: `confirmed` (validated by the plugin author dogfooding through sprint 0001 on 2026-05-11) · _criticality_: primary
  - Open questions: none

### Operators

- **GitHub Actions CI for this repo** — _id_: `ci-operator` · _category_: operator · _track_: `developer-docs` · _surface_: workflows under `.github/workflows/` (in particular `ci.yml` with `lint`/`test`/`docs` as required checks on `develop`), plus the release/automerge/`main` fast-forward infrastructure inherited from `nolte/gh-plumbing` · _expects_: reproducible runs; stable Task targets (`task lint`/`test`/`docs`); no flaky checks blocking `develop` · _status_: `assumed` · _criticality_: primary
  - Open questions: none

### Contributors / maintainers

- **Repo maintainer (nolte)** — _id_: `maintainer` · _category_: contributor · _track_: `developer-docs` · _surface_: direct commit access on all branches, review authority, release authority, spec-evolution authority · _expects_: specs, skills and plugin manifest stay consistent; `CLAUDE.md` reflects repo state; conventions (EN-canonical specs, bilingual docs, Conventional Commits, PR workflow) are upheld · _status_: `assumed` · _criticality_: primary
  - Open questions: none

- **Claude Code itself as co-author** — _id_: `claude-coauthor` · _category_: contributor · _track_: `developer-docs` · _surface_: skills like `/nolte-shared:skill-management`, `/nolte-shared:spec`, `/nolte-shared:pull-request-create` — the tool scaffolds and edits files under `skills/`, `agents/`, `spec/` and produces commits/PRs · _expects_: skills follow their own specs (meta-consistency); changes stay reviewable; skill hard rules are respected (e.g. do not copy plugin-owned skills into `.claude/skills/`) · _status_: `assumed` · _criticality_: primary
  - Open questions: Should Claude Code appear explicitly as a contributor in downstream language, or implicitly via "maintainer who uses Claude"?

- **External contributors via pull request** — _id_: `external-contributor` · _category_: contributor · _track_: `developer-docs` · _surface_: GitHub forks, PRs against `develop`, issue tracker · _expects_: clear contribution entry points (README, `CLAUDE.md`, spec layout); the PR workflow via `/nolte-shared:pull-request-create` is followable without insider knowledge; generated config files stay EN for portfolio consistency · _status_: `assumed` · _criticality_: peripheral
  - Open questions: Is this repo actively open to external contributions, or de facto single-maintainer? `CONTRIBUTING.md` is now present at the repo root.

### Governing parties

- **Portfolio-consistency anchors (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`)** — _id_: `portfolio-anchor` · _category_: governing-party · _track_: `developer-docs` · _surface_: extends pointers in `.github/settings.yml` / `release-drafter.yml` / `boring-cyborg.yml`, the pinned `vale-style` release, `TASK_COLLECTION_BASE` references to shared Taskfiles · _expects_: this repo does not diverge from portfolio standards; upstream changes are followed (e.g. via `vocab-drift-audit`) · _status_: `assumed` · _criticality_: secondary
  - Open questions: none

### Indirect audiences

- **End users of downstream projects that install `nolte-shared`** — _id_: `downstream-end-user` · _category_: indirect · _track_: `user-docs` · _surface_: none direct — they only see the downstream project's product. Influence is mediated because skills (e.g. `/quality-gate`, `/review`, `/security-review`) shape downstream code quality and release discipline · _expects_: nothing directly from this plugin. The plugin explicitly takes no responsibility for downstream end-user outcomes; skills are tooling, not guarantees, and release-quality accountability sits with the downstream maintainer · _status_: `assumed` · _criticality_: peripheral
  - Open questions: none

- **Other Nolte portfolio repos as passive consumers of the conventions** — _id_: `portfolio-peer` · _category_: indirect · _track_: `developer-docs` · _surface_: none direct — they do not install the plugin but are shaped by the specs codified here (PR workflow, project structure, prose style) as de-facto portfolio standards · _expects_: specs do not change silently in ways that would force existing repos to follow; breaking changes come with release notes · _status_: `assumed` · _criticality_: peripheral
  - Open questions: Is the effect on other portfolio repos actually passive today, or do some of those repos install the plugin (in which case they belong under Direct consumers)?

### Portfolio-baseline coverage notes

`spec/project/mkdocs-structure/` §Audience targeting and
`spec/project/audience-identification/` ask the artefact to cover the portfolio
audience baseline (`user`, `contributor`, `operator`, `release-manager`) or to
explicitly note the exclusion of any baseline audience the context genuinely
doesn't serve. The four baseline names are not used verbatim as entry labels
here; the mapping below records, per baseline name, the covering entry or the
reasoned exclusion:

- **`user`** — covered, not excluded. The functional end-user role is served by
  **`downstream-user`** (direct consumer, _track_: `user-docs`) — the Claude Code
  users in portfolio projects who invoke the plugin's slash commands — and, at
  one remove, by **`downstream-end-user`** (indirect, `user-docs`). The baseline
  `user` is therefore covered under context-specific labels; no separate `user`
  entry is added because it would duplicate `downstream-user`.
- **`contributor`** — covered by **`maintainer`**, **`external-contributor`**,
  **`claude-coauthor`** (all `developer-docs`).
- **`operator`** — covered by **`ci-operator`** (`developer-docs`).
- **`release-manager`** — **excluded with reason.** This repository has no
  separate release-manager surface: the sole maintainer (`maintainer`, nolte)
  also holds release authority, and the release mechanics are automated
  (release-drafter, automerge, the `main` fast-forward inherited from
  `nolte/gh-plumbing`) rather than driven by a dedicated release-manager role.
  Release-facing concerns are therefore already covered by the `maintainer`
  (release authority) and `ci-operator` (release automation surface) entries.
  Should release responsibility ever split from maintenance, add a
  `release-manager` entry (default _track_: `developer-docs`) — this is listed as
  a revisit trigger below.

## Open questions (cross-cutting)

- Only "Plugin author dogfooding inside this repo" is tagged `confirmed` so far (validated by the author's first end-to-end dogfood sprint on 2026-05-11). All other entries remain `assumed` until they are validated against a real representative or an authoritative source.
- A versioning and communication policy for breaking spec changes is not yet defined; it affects the governing-party (portfolio anchors) and indirect (other portfolio repos) audiences simultaneously.
- The distinction between "other portfolio repos as passive convention consumers" (Indirect) and "downstream projects as plugin users" (Direct) needs a concrete check per repo the next time this artifact is revisited.

## Revisit triggers

- A new slash command or agent is added that changes the public interaction surface.
- A downstream repo begins relying on specific plugin outputs in a reviewed way (graduates an entry from `assumed` to `confirmed`).
- Claude Code changes its plugin or skill schema in a way that breaks compatibility.
- The repo accepts its first external PR, or publishes a `CONTRIBUTING.md`.
- A new governing constraint appears (legal, security, compliance) that the current single-entry governing-party category no longer covers.
- Release responsibility splits from maintenance (a dedicated release-manager role appears), in which case add the currently-excluded `release-manager` baseline audience as its own entry (default _track_: `developer-docs`).
- `spec/project/audience-identification/` moves out of `draft` status or materially changes its requirements.
- `spec/portfolio/tech-stack-discovery/` §Audiences materially changes; that spec owns the audience model for the portfolio-wide tech-stack inventory, and additions or removals there propagate back here as new revisit work.
- The planning suite under `project/` materially changes its scope (new top-level artefact kind, change in how `mission`, `goals`, `roadmap`, `features`, or `sprints` are produced or consumed).
- The auto-generated skill / agent catalog under `docs/<lang>/skills/` and `docs/<lang>/agents/` changes its public navigation structure, source-root set, or rendering output in a way that affects how downstream readers locate artefacts.
