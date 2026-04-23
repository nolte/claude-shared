# Claude Skill and Agent Catalog

Status: draft

## Context
This repository ships reusable Claude Code skills and agents as the `nolte-shared` plugin, and the published MkDocs site is the discovery surface for both this plugin and any other Claude Code plugins consumed alongside it. The `skill-management` and `agent-management` specs define the on-disk shape of these artifacts, but consumers need a browsable catalog to see what's available, what each artifact does, and when Claude will invoke it. Today such a catalog would have to be maintained by hand and would drift whenever a skill or agent is added, renamed, or reworked. This spec defines how the MkDocs documentation site exposes an always-current catalog of skills and agents—generated from the very source files that already govern them, across this plugin and any additional plugins configured into the docs build. It's the foundation for generating the corresponding documentation objects.

## Goals
- A single browsable catalog inside the MkDocs site that lists every skill and every agent shipped by this plugin and by any further plugins configured into the docs build
- Catalog content is derived from the source files (skill `SKILL.md`, agent `<name>.md`): no hand-maintained copy
- Each catalog entry shows the artifact's canonical metadata (`name`, `description`, `distribution` for agents, `tags` when present) and links back to the source on the originating plugin's repository
- The catalog regenerates as part of the normal `task docs` / `mkdocs build` flow with no extra manual step
- Readers can tell at a glance which plugin provides which artifact and can browse by tag
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
- **MUST** discover skills and agents from every plugin source root configured for the catalog generator; the local `claude-shared` plugin (its own `skills/` and `agents/` folders) is one such root and **MUST** always be present
- **MUST NOT** include skills or agents that don't conform to the `skill-management` / `agent-management` structure; malformed entries **MUST** fail the docs build rather than be silently omitted

### Content of a catalog entry
- **MUST** render the frontmatter `name` as the page title
- **MUST** include the full `description` verbatim
- **MUST** include the `distribution` field for agents (`plugin` or `project`)
- **MUST** label each entry with the source plugin it comes from (for example `nolte-shared`)
- **MUST** link to the source file in the originating plugin's repository on its main branch; the link base URL is configured per plugin source root (for example `https://github.com/nolte/claude-shared/blob/main/...`)
- **MUST** render any `tags` declared in the artifact's frontmatter as visible tags on the entry page
- **SHOULD** render the body of `SKILL.md` (or the agent system-prompt markdown) as the page's main content so authors' instructions are visible to readers
- **MAY** surface supporting assets by listing sibling files under `skills/<name>/` or `agents/<name>/` (for example `templates/`, `references/`, `examples/`)

### Generation mechanism
- **MUST** generate catalog pages at docs-build time from the source files; **MUST NOT** commit generated catalog markdown back into `docs/`
- **MUST** be driven by `mkdocs-gen-files` together with `mkdocs-literate-nav`, both declared in `mkdocs.yml`
- **MUST** read plugin source roots from a configured list—each entry pairing the local source path with the public repository URL used for source links—so additional plugins can be added without changing generator code
- **MUST** expose catalog generation through `task docs` so local builds and CI produce identical output
- **MUST NOT** require a separate manual "regenerate catalog" step outside the normal docs build

### Navigation and layout
- **MUST** expose the catalog under stable top-level sections in the MkDocs navigation—at minimum a `Skills` section and an `Agents` section
- **MUST** group entries within each section by source plugin so readers can see at a glance which plugin provides which artifact
- **MUST** order catalog entries deterministically—alphabetical by `name` within each plugin group—so diffs of the rendered site stay stable
- **SHOULD** provide an index page per section summarizing every entry (name + description + tags) with links to the detail pages
- **SHOULD** provide a tag index that lists every tag across all entries and links to the artifacts that declare it

### Multilingual behavior
- **MUST** render artifact metadata (`name`, `description`, `distribution`, `tags`, body) as-is from the source frontmatter; for artifacts shipped by this repository this is English by the `skill-management` / `agent-management` rule, while external plugins are rendered verbatim regardless of their own language conventions
- **SHOULD** localize only the surrounding chrome—section titles, intro paragraphs, navigation labels, the tag-index header—into each configured docs language (`docs/en/`, `docs/de/`)
- **MUST NOT** translate artifact metadata or body at generation time; translations of those fields are out of scope

### Error handling
- **MUST** fail the docs build when a skill or agent has missing or invalid frontmatter rather than producing a broken catalog
- **MUST** emit a clear error message that names the offending source file and the plugin source root it came from

## Acceptance Criteria
- [ ] `task docs` produces a docs site whose navigation contains a Skills section with one page per skill across all configured plugin source roots
- [ ] `task docs` produces a docs site whose navigation contains an Agents section with one page per agent across all configured plugin source roots
- [ ] Each catalog page displays the artifact's `name`, `description`, source plugin label, and—for agents: `distribution`
- [ ] When an artifact's frontmatter declares `tags`, those tags appear on the catalog page
- [ ] Each catalog page contains a direct link to the source file on the originating plugin's main-branch repository URL
- [ ] Adding a new skill or agent in any configured plugin source root requires no manual edit to `docs/` or `mkdocs.yml` for the entry to appear
- [ ] Removing a skill or agent removes the corresponding catalog page on the next `task docs` run
- [ ] `mkdocs.yml` declares `mkdocs-gen-files` and `mkdocs-literate-nav` and configures the list of plugin source roots (each pairing a local path with a public repository URL)
- [ ] The local `claude-shared` plugin appears as one of the configured plugin source roots
- [ ] No generated catalog markdown is committed under `docs/`
- [ ] A skill or agent with invalid frontmatter causes `task docs` to fail with an error that names the offending file and its plugin source root
- [ ] Catalog entries appear in deterministic alphabetical order by `name` within each plugin group of each section
- [ ] A tag index page exists and links to every artifact that declares the tag

## Open Questions
- Should `skill-management` and `agent-management` be amended to standardize the optional `tags` field (allowed values, normalization, length limits) so tag-based browsing stays predictable across plugins?
- Should versions of skills and agents (history, changelogs) appear in the catalog, or is the git history sufficient?
- If translations of an artifact body are ever desired, where do they live—a parallel `skills/<name>/docs/<lang>.md`, or separately curated pages under `docs/<lang>/`?
- How are plugin source roots configured exactly—inline in `mkdocs.yml` under the `gen-files` plugin config, or in a sibling YAML file referenced from there?
