# Claude Skill and Agent Catalog

Status: draft

## Context
This repository ships reusable Claude Code skills and agents as the `nolte-shared` plugin, and the published MkDocs site is the discovery surface for both this plugin and any other Claude Code plugins consumed alongside it. The `skill-management` and `agent-management` specs define the on-disk shape of these artifacts, but consumers need a browsable catalog to see what's available, what each artifact does, and when Claude will invoke it. Today such a catalog would have to be maintained by hand and would drift whenever a skill or agent is added, renamed, or reworked. This spec defines how the MkDocs documentation site exposes an always-current catalog of skills and agents—generated from the very source files that already govern them, across this plugin and any additional plugins configured into the docs build. It's the foundation for generating the corresponding documentation objects.

### Operating modes
The catalog applies to two kinds of repositories:

- **Plugin mode**: the repository is itself a Claude Code plugin (indicated by a top-level `.claude-plugin/plugin.json`). The local plugin's own `skills/` and `agents/` folders are one of the catalog's source roots; additional plugin source roots may be added alongside.
- **Consumer mode**: the repository isn't a Claude Code plugin itself. It hosts an MkDocs site that catalogs one or more *external* plugins (for example plugins the repository depends on or vendors in). There's no local plugin source root; all roots are external.

Every requirement in this spec applies to both modes unless explicitly qualified as "in plugin mode," or "in consumer mode."

## Goals
- A single browsable catalog inside the MkDocs site that lists every skill and every agent shipped by this plugin and by any further plugins configured into the docs build
- Catalog content is derived from the source files (skill `SKILL.md`, agent `<name>.md`): no hand-maintained copy
- Each catalog entry shows the artifact's canonical metadata (`name`, `description`, `distribution` for agents, `phase`, `tags` when present) and links back to the source on the originating plugin's repository
- The catalog regenerates as part of the normal `task docs` / `mkdocs build` flow with no extra manual step
- Readers can tell at a glance which plugin provides which artifact, which delivery-lifecycle phase it belongs to, and they can browse by tag
- The catalog integrates with the existing multilingual MkDocs layout (`docs/en/`, `docs/de/`) without forcing translation of artifact metadata

## Non-Goals
- Defining the on-disk shape of skills or agents (owned by `skill-management` and `agent-management`)
- Portfolio-wide MkDocs theme, palette, or typography decisions
- Runtime discovery and loading of skills and agents (owned by Claude Code itself)
- A separate, standalone catalog site—the catalog lives inside the existing `claude-shared` docs site

## Requirements

### Scope of the catalog
- **MUST** include exactly one catalog entry per skill folder under any configured plugin source root that contains a valid `SKILL.md`
- **MUST** include exactly one catalog entry per agent file (`<name>.md`) under any configured plugin source root
- **MUST** discover skills and agents from every plugin source root configured for the catalog generator
- **MUST**, in plugin mode, include the local plugin (its own `skills/` and `agents/` folders) as one of the configured source roots
- **MUST**, in consumer mode, configure at least one external plugin source root; the catalog isn't useful when no sources are declared
- **MUST NOT** include skills or agents that don't conform to the `skill-management` / `agent-management` structure; malformed entries **MUST** fail the docs build rather than be silently omitted

### Content of a catalog entry
- **MUST** render the frontmatter `name` as the page title
- **MUST** include the full `description` verbatim
- **MUST** include the `distribution` field for agents (`plugin` or `project`)
- **MUST** label each entry with the source plugin it comes from (for example `nolte-shared`)
- **MUST** link to the source file in the originating plugin's repository on its main branch; the link base URL is configured per plugin source root (for example `https://github.com/nolte/claude-shared/blob/main/...`)
- **MUST** render any `tags` declared in the artifact's frontmatter as visible tags on the entry page; `tags` are normalized per `skill-management` / `agent-management` (lowercase ASCII kebab-case, ≤30 characters, ≤5 entries)
- **MUST** render the artifact's `phase` (see "Phase classification" below) as a visible badge on the entry page, using the phase label from the localized chrome
- **SHOULD** render the body of `SKILL.md` (or the agent system-prompt markdown) as the page's main content so authors' instructions are visible to readers
- **MAY** surface supporting assets by listing sibling files under `skills/<name>/` or `agents/<name>/` (for example `templates/`, `references/`, `examples/`)

### Phase classification
Every skill and agent **MUST** declare which phase of the delivery lifecycle it belongs to via a `phase:` frontmatter field. The field is a single lowercase ASCII kebab-case identifier drawn from the closed vocabulary below; no other value is permitted. Authors who genuinely can't pin a single phase use `cross-cutting`.

- **MUST** include a top-level `phase:` field in the YAML frontmatter of every skill (`SKILL.md`) and every agent (`<name>.md`)
- **MUST** restrict `phase` to exactly one of these eight identifiers (the **phase vocabulary**):
  - `vision`: frames the project (mission authoring and revision)
  - `plan`: turns vision into queued work (audience, roadmap, sprint and feature planning)
  - `design`: authors the conventions, scaffolds, and specifications work depends on
  - `build`: daily mechanics of an active sprint
  - `review`: moves change toward `develop` through reviewed pull requests
  - `quality`: audits, scans, lint/typecheck/test gates, drift detection
  - `close-release`: sprint closure, release notes, release publishing
  - `cross-cutting`: genuinely phase-agnostic capabilities used across multiple lifecycle phases (for example image conversion, generic project bootstrap)
- **MUST** treat `phase` as an identifier, not prose: the value is never translated, case-folded, or rewritten between docs languages
- **MUST NOT** declare `phase` as a list; a single artifact occupies exactly one phase. Artefacts whose responsibility spans multiple phases either get a more focused split or, when no split is appropriate, are classified as `cross-cutting`
- **SHOULD**, when authoring a new artifact, pick the **earliest phase** in the lifecycle the artifact is normally invoked in; review and quality artifacts that are themselves invoked from a build-phase skill belong to the artifact's own primary purpose, not to the calling phase

### Generation mechanism
- **MUST** generate catalog pages from the source files
- The repository **MUST NOT** commit generated catalog markdown back into `docs/` _unless_ the docs-deploy pipeline (the workflow that produces the GitHub Pages output) bypasses `task docs` / the configured catalog generator and invokes `mkdocs build` directly. In that case the repository **MUST** commit the generated catalog files so the deploy build picks them up from the checkout, AND **MUST** ship a CI freshness check that fails the build when the committed catalog drifts from a fresh re-generation (typical shape: `task docs:catalog && git diff --exit-code docs/<lang>/{skills,agents} docs/<lang>/tags.md`)
- **MUST** wire catalog navigation through `mkdocs-literate-nav` declared in `mkdocs.yml`
- **MUST** invoke a catalog generator that produces the per-artifact pages, per-section index pages, per-section `SUMMARY.md` files for literate-nav, and the tag index. The generator **MAY** be a `mkdocs-gen-files` plugin script OR a standalone pre-build step (for example a Taskfile target invoked before `mkdocs build`) that writes physical files under `docs/<lang>/<section>/`. The pre-build form is the recommended choice whenever the repo also uses `mkdocs-static-i18n` with `docs_structure: folder`, because `mkdocs-static-i18n` 1.3.x discards files whose `abs_src_path` isn't under `docs_dir` and therefore silently drops every page emitted by `mkdocs-gen-files`
- **MUST** read plugin source roots from a configured list—each entry pairing the local source path with the public repository URL used for source links—so additional plugins can be added without changing generator code
- **MUST** expose catalog generation through `task docs` so local builds and CI produce identical output; in the pre-build form this is wired by declaring the generator step as a Taskfile dependency of the docs task
- **MUST NOT** require a separate manual "regenerate catalog" step outside the normal docs build

### Navigation and layout
- **MUST** expose the catalog under stable top-level sections in the MkDocs navigation—at minimum a `Skills` section and an `Agents` section
- **MUST** group entries within each section **first by phase** (in the canonical phase order listed under "Phase classification": `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`), then by source plugin within each phase, so readers can see at a glance which artifacts apply to each delivery-lifecycle phase
- **MUST** order catalog entries deterministically—alphabetical by `name` within each plugin sub-group of each phase—so diffs of the rendered site stay stable
- **MUST** omit a phase heading that has no entries; an empty phase isn't rendered
- **SHOULD** provide an index page per section summarizing every entry (name + description + phase + tags) with links to the detail pages
- **SHOULD** provide a tag index that lists every tag across all entries and links to the artifacts that declare it

### Multilingual behavior
- **MUST** render artifact metadata (`name`, `description`, `distribution`, `tags`, body) as-is from the source frontmatter; for artifacts shipped by this repository this is English by the `skill-management` / `agent-management` rule, while external plugins are rendered verbatim regardless of their own language conventions
- **MUST** treat `tags` as identifiers, not prose: they're rendered in their canonical lowercase ASCII kebab-case form (per `skill-management` / `agent-management`) and never translated, case-folded, or otherwise rewritten between docs languages
- **SHOULD** localize only the surrounding chrome—section titles, intro paragraphs, navigation labels, the tag-index header—into each configured docs language (`docs/en/`, `docs/de/`)
- **MUST NOT** translate artifact metadata or body at generation time; translations of those fields are out of scope

### Error handling
- **MUST** fail the docs build when a skill or agent has missing or invalid frontmatter rather than producing a broken catalog
- **MUST** emit a clear error message that names the offending source file and the plugin source root it came from
- **MUST** fail the docs build when an artifact's `phase` is missing or isn't in the phase vocabulary, with an error message that names the offending file, the plugin source root, and the value of the rejected `phase`

## Acceptance Criteria
- [ ] `task docs` produces a docs site whose navigation contains a Skills section with one page per skill across all configured plugin source roots
- [ ] `task docs` produces a docs site whose navigation contains an Agents section with one page per agent across all configured plugin source roots
- [ ] Each catalog page displays the artifact's `name`, `description`, source plugin label, and—for agents: `distribution`
- [ ] When an artifact's frontmatter declares `tags`, those tags appear on the catalog page
- [ ] Each catalog page contains a direct link to the source file on the originating plugin's main-branch repository URL
- [ ] Adding a new skill or agent in any configured plugin source root requires no manual edit to `docs/` or `mkdocs.yml` for the entry to appear
- [ ] Removing a skill or agent removes the corresponding catalog page on the next `task docs` run
- [ ] `mkdocs.yml` declares `mkdocs-literate-nav`, and a configured list of plugin source roots (each pairing a local path with a public repository URL) is read by the catalog generator
- [ ] The catalog generator is either declared as a `mkdocs-gen-files` script in `mkdocs.yml` or wired into `task docs` as a standalone pre-build step
- [ ] In plugin mode, the local plugin appears as one of the configured plugin source roots
- [ ] In consumer mode, at least one external plugin source root is configured
- [ ] Generated catalog markdown isn't committed under `docs/` **unless** the repo's docs-deploy pipeline bypasses `task docs`; in that case the catalog **is** committed and a CI freshness check guards against drift
- [ ] When the catalog is committed, a CI job runs the catalog generator and fails when its output differs from the committed tree
- [ ] A skill or agent with invalid frontmatter causes `task docs` to fail with an error that names the offending file and its plugin source root
- [ ] Catalog entries appear grouped first by phase (in the canonical phase order) and then alphabetically by `name` within each plugin sub-group of each phase
- [ ] Every skill and agent declares a `phase` from the closed eight-value vocabulary (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); a missing or out-of-vocabulary `phase` fails `task docs`
- [ ] Each catalog page displays the artifact's `phase` as a visible badge using the localized chrome label
- [ ] The Skills and Agents index pages render a per-phase heading (omitting phases with zero entries) above each plugin sub-group
- [ ] A tag index page exists and links to every artifact that declares the tag

## Open Questions
- Should versions of skills and agents (history, changelogs) appear in the catalog, or is the git history sufficient?
- If translations of an artifact body are ever desired, where do they live—a parallel `skills/<name>/docs/<lang>.md`, or separately curated pages under `docs/<lang>/`?
- How are plugin source roots configured exactly—inline in `mkdocs.yml` under the `gen-files` plugin config, or in a sibling YAML file referenced from there?
- How should this spec evolve once `mkdocs-static-i18n` upstream supports files emitted by `mkdocs-gen-files`? As of May 2026 (`mkdocs-static-i18n` 1.3.1) those files are silently dropped in `reconfigure.py` because their `abs_src_path` is outside `docs_dir`, which forces the pre-build form whenever folder-strategy i18n is in use.
- The docs-deploy detour: should we standardise on bumping the `nolte/gh-plumbing` `reusable-mkdocs.yaml` upstream to call `task docs` instead, so every consumer can stay on the cleaner "no committed catalog" form? The conditional rule above exists because `reusable-mkdocs.yaml@v1.1.12` invokes `mhausenblas/mkdocs-deploy-gh-pages@1.26` directly, which runs `mkdocs build` and never sees `task docs`.
