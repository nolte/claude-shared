# MkDocs Site Structure

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

Every portfolio repository that ships documentation does so through MkDocs, and `spec/project/project-structure/` already mandates that `docs/` and `mkdocs.yml` exist. What that spec deliberately doesn't define is the *shape* of the site: which top-level sections appear, in which order, in which language trees, with which plugins, with which per-page metadata. `spec/project/docs-freshness/` is explicit that "declaring the on-disk shape of MkDocs (i18n plugin choice, theme, nav structure)—those are per-repository decisions", which is exactly the gap consumers feel: readers crossing two nolte repos relearn the navigation, the docs-freshness audit can't normalise expectations across repos, and project-type-specific behaviours (the skills/agents catalog in `nolte-shared`, future cookiecutter-template docs, future library API references) each invent their own MkDocs wiring from scratch.

This spec closes that gap. It defines (a) the portfolio-wide MkDocs skeleton—site layout, plugin baseline, navigation contract, per-page structure, language parity—and (b) two explicit **extension hooks** through which project-type-specific specs (`skill-agent-catalog`, future `cookiecutter-template-docs`, future `library-api-docs`, …) bolt on additional sections and plugins without forking the skeleton or silently overriding it. The skeleton is enforced; the extensions are declarative and reviewable.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every portfolio repository with MkDocs exposes the same top-level navigation, so a reader who learned one repo knows how to navigate the next
- Multilingual layouts (`docs/<lang>/`) follow one i18n mechanism with file-name parity across every configured language
- The plugin baseline is enumerated and pinned, so a repository's documentation builds the same way locally, in CI, and in the published site
- Per-page structure (`H1`, frontmatter, audience tagging) is predictable enough that downstream tooling (`docs-freshness`, `prose-vale-curator`, future catalog generators) can rely on it
- Project-type-specific specs extend the skeleton through declared hooks rather than forking it; every extension names what it adds, what it relaxes, and why
- The on-disk shape is verifiable: `mkdocs build --strict` is the rendering gate, and an audit (`docs-freshness`) treats the spec as the normative source for the expected nav and parity

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Theme palette, typography, or visual identity—those stay per-repo decisions (the spec mandates `mkdocs-material` as the theme engine, not a colour scheme)
- The markdown *content* of any page—the spec governs the container, not the prose
- Vale prose linting—owned by `spec/project/prose-style/`
- Documentation build and deploy wiring—owned by `spec/project/project-structure/` (the `docs/` and `mkdocs.yml` existence MUSTs) and the `release-cd-deliver-docs` workflow
- Catalog generators themselves (for example `skill-agent-catalog`)—those are project-type-specific extension specs that bolt on through the hooks defined here, but their generator logic lives in the extension spec
- Audience identification methodology—owned by `spec/project/audience-identification/`; this spec only requires that the *result* (the audience artifact) is referenced from page frontmatter
- ADR formatting and lifecycle—the spec only carves out an ADR nav slot; the ADR shape belongs to a separate spec if and when it grows large enough to warrant one

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Site layout

- **MUST** keep `docs_dir` at `docs` (the MkDocs default), so consuming tooling (`docs-freshness`, IDE link-checkers, `mkdocs-static-i18n`) can rely on a single path
- **MUST** organise documentation into per-language subdirectories `docs/<lang>/`, one per language listed in `spec/.spec-config.yml` `languages`; a repo using only one language still uses `docs/<lang>/` (not a flat `docs/`) so adding a second language later is a pure-additive change
- **MUST** keep the on-disk file tree structurally identical across configured language trees: every page that exists in one language exists in every other configured language (cross-checked by `docs-freshness` parity audit)
- **MUST NOT** place top-level pages directly under `docs/` (other than the i18n plugin's fallback `index.md` when the configured i18n strategy requires one); every page belongs to a language tree
- **SHOULD** keep section folders (`docs/<lang>/<section>/`) flat—at most one further nesting level (`docs/<lang>/<section>/<sub>/`)—to keep navigation paths predictable

### Top-level navigation

- **MUST** expose these top-level sections, in this order, when the corresponding content exists:
  1. **Home** (`index.md`): landing page; one paragraph plus jump-off links
  2. **Getting Started**: newcomer-oriented narrative path from install/clone to first successful run
  3. **Guides**: task-oriented how-tos
  4. **References**: format / API / convention references
  5. **ADRs**: Architecture Decision Records, when the repository keeps them
  6. **Project**: orientation surface for the `project/` planning tree (mission, roadmap, sprints, audience artifacts), when `project/` exists
  7. *Extension sections—see "Extension hooks" below*
- **MUST NOT** add additional top-level sections without a project-type-specific spec opt-in; per-page additions stay inside the seven sections above
- **MUST** translate section labels through `mkdocs-static-i18n`'s `nav_translations` so a single `mkdocs.yml` drives every language's nav
- **SHOULD** omit an empty section rather than ship it as a placeholder; an empty section is a reader trap

### Plugin baseline

- **MUST** declare `mkdocs-material` as the theme engine (`theme: name: material`); the theme is the portfolio convention, the palette is a per-repo decision
- **MUST** declare `mkdocs-static-i18n` as the i18n plugin with `docs_structure: folder` so the per-language subdirectories under `docs/<lang>/` are the source of truth
- **MUST** declare `pymdownx.superfences` in `markdown_extensions` (the Mermaid integration governed by `spec/project/mermaid-diagrams/` requires it; declaring it here makes the dependency explicit even when no Mermaid diagram ships yet)
- **MUST** keep the built-in `search` plugin active (declare it explicitly in the `plugins:` list so an extension spec that re-declares `plugins:` doesn't accidentally drop it)
- **MUST** pin every plugin (including `mkdocs`, `mkdocs-material`, and `pymdown-extensions`) in the project's Python dependency manifest (`pyproject.toml`, `requirements*.txt`, `uv.lock`, …); no floating versions
- **SHOULD** keep the plugin list short; additional plugins are introduced through the **Plugin extension hook** below, not through ad-hoc additions to `mkdocs.yml`
- **MAY** add `mkdocs-mermaid2-plugin` only when the conditions in `spec/project/mermaid-diagrams/` allow it (the canonical Mermaid stack here is `pymdownx.superfences`)

### Per-page structure

- **MUST** start every page (after any frontmatter) with a single `# H1` that matches the page's nav label
- **MUST** declare YAML frontmatter at the top of every page with at minimum:
  - `title`: the human-readable page title (matches the H1)
  - `audience`: one or more audience IDs declared in the project's audience artifact (`AUDIENCES.md` or the documented alternative location per `spec/project/audience-identification/`)
  - `last_updated`: ISO-8601 date the content was last revised, or the literal `generated` for pages emitted by a catalog generator
- **SHOULD** include a `## Sources` section as the page's last section, linking back to the authoritative source (`spec/<path>`, `src/<path>`, an ADR, an external URL) when the page derives from a single source of truth
- **MAY** declare additional frontmatter keys: `tags` for cross-page lookups, `status` for explicitly marking `draft` / `stable` / `deprecated`, `summary` for a one-line abstract used in section index pages
- **MUST NOT** invent frontmatter keys with portfolio-wide meaning without proposing them via a spec amendment

### Audience targeting

- **MUST** map every top-level nav section to one or more audiences declared in the project's audience artifact; the mapping is recorded in the section's index page frontmatter and in the section description on the Home page
- **MUST** restrict every page's `audience` frontmatter value to IDs declared in the project's audience artifact; an unknown audience ID is a `docs-freshness` finding
- **SHOULD** cover the portfolio audience baseline (`user`, `contributor`, `operator`, `release-manager`) in the project's audience artifact in addition to any project-specific audiences; a project that genuinely doesn't serve one of these baseline audiences (a library without a release workflow doesn't serve `release-manager`, an internal tool with no contributor surface doesn't serve `contributor`) explicitly notes the exclusion in the artifact so a reviewer can tell a deliberate omission from an oversight
- **SHOULD** group nav sections by primary audience when the project serves three or more audiences; for two or fewer audiences a flat ordering is clearer
- **MAY** use the `audience` frontmatter as a future filter input (audience-scoped TOC, audience-filtered search); this spec only requires that the value is present and valid

### Extension hooks

Two declared extension points let project-type-specific specs add to the skeleton without forking it.

- **Section extension**: a project-type-specific spec **MAY** add one or more top-level nav sections.
  - The extension spec **MUST** name each added section, its insertion position relative to the seven standard sections, its primary audience, and the per-page frontmatter shape (if any) it requires beyond the baseline
  - The extension spec **MUST** declare whether the section is single-language (typically when the content is sourced from EN-canonical artifacts whose translation isn't meaningful) or follows the standard language-parity rule
  - The extension spec **MUST NOT** rename, reorder, or hide a standard section silently; that's a spec amendment, not an extension
  - Examples: `spec/claude/skill-agent-catalog/` adds **Skills** and **Agents** sections after **References**; a future `cookiecutter-template-docs` spec may add **Template variables**, **Hooks**, **Quickstart**; a future `library-api-docs` spec may add **API Reference**
- **Plugin extension**: a project-type-specific spec **MAY** require additional MkDocs plugins.
  - The extension spec **MUST** name each required plugin, its pin (or a constraint that resolves to a pin in the dep-manager), the rationale (why the baseline doesn't already include it), and any `mkdocs.yml` settings it needs
  - The extension spec **MUST** explain how the plugin interacts with the baseline plugins, especially `mkdocs-static-i18n` (which has known interactions with `mkdocs-gen-files` per `spec/claude/skill-agent-catalog/` Open Questions)
  - The extension spec **MUST NOT** silently disable a baseline plugin; explicitly relaxing a baseline MUST requires a stated rationale in the extension spec
  - Examples: `spec/claude/skill-agent-catalog/` requires `mkdocs-gen-files` and `mkdocs-literate-nav`; a future `cookiecutter-template-docs` may require `mkdocs-include-markdown`
- **Project-type discovery**: a repository signals which extensions are active by carrying the corresponding marker file (`.claude-plugin/plugin.json` for claude-plugin; `cookiecutter.json` plus `{{cookiecutter.project_slug}}/` for cookiecutter-template; future per-type markers as needed); the matching extension spec applies for repositories that carry the marker
- **MUST** treat every active extension's MUSTs as additive to the baseline MUSTs; an extension only relaxes the baseline when it explicitly says so with rationale
- **MUST NOT** carry more than five extension sections in total per repository, summed across every active extension spec; the cap forces extension specs to consolidate sections rather than mint new ones whenever a project crosses the threshold (a hypothetical repo that activates three extension specs with two sections each would need to either fold sections together or justify why the cap should grow via a spec amendment)

### i18n and parity

- **MUST** keep `docs/<lang>/` trees structurally identical: every page in one language tree has a counterpart at the same relative path in every other configured tree (see `spec/project/docs-freshness/` for the audit shape)
- **MUST** route every section-label translation through `mkdocs-static-i18n`'s `nav_translations`; never duplicate `nav:` blocks per language
- **SHOULD** translate the surrounding chrome (section intros, index pages, navigation labels, footer copy) for every configured language; **MAY** keep page bodies sourced from EN-canonical artifacts (catalog pages quoting source frontmatter, ADR records whose canonical form is EN, …) in their canonical language across all language trees, provided the chrome around them is translated and the page declares the source language in its frontmatter via `source_language: en`

### Build verification

- **MUST** run `mkdocs build --strict` as part of the project's CI on every pull request; a non-zero exit blocks merge
- **MUST** keep the project's `task docs` target (or equivalent) invoke the same build sequence used in CI, so a local pass matches the CI pass
- **SHOULD** include a per-page parity check in the same CI job (currently shipped through `docs-freshness`), so a missing translation fails the build before review rather than after merge

### Discovery and cross-referencing

- **MUST** add a one-line reference to this spec in `spec/project/project-structure/` next to the MkDocs MUSTs, so a reader landing on `project-structure` is pointed at the detailed shape
- **SHOULD** be referenced from `spec/project/docs-freshness/` as the normative source for the expected nav and parity (the audit checks against the spec rather than reinventing the expectations)
- **MAY** be cited from project-type-specific extension specs (`skill-agent-catalog`, future `cookiecutter-template-docs`, future `library-api-docs`) as the baseline they extend

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] Every portfolio repository with `mkdocs.yml` keeps `docs_dir: docs` and organises documentation under `docs/<lang>/` for every language in `spec/.spec-config.yml`
- [ ] Every portfolio repository's `mkdocs.yml` declares `mkdocs-material`, `mkdocs-static-i18n` (with `docs_structure: folder`), `pymdownx.superfences`, and the built-in `search` plugin explicitly
- [ ] Every plugin in `mkdocs.yml` is pinned in the project's Python dependency manifest (no `>=`-style floating versions in the lockfile)
- [ ] Every top-level nav section in every portfolio repository is one of the seven standard sections (Home, Getting Started, Guides, References, ADRs, Project, plus declared extension sections); a section that isn't listed in the standard set is justified by an active extension spec
- [ ] Every page under `docs/<lang>/` starts with a single `# H1` matching the nav label and declares frontmatter with `title`, `audience` (one or more IDs from the project's audience artifact), and `last_updated`
- [ ] Every audience value in every page's frontmatter matches an ID declared in the project's audience artifact (verifiable by `docs-freshness` audit)
- [ ] Every `docs/<lang>/` tree contains the same set of relative paths as every other configured `docs/<lang>/` tree (file-name parity, also verifiable by `docs-freshness`)
- [ ] `mkdocs build --strict` passes in CI on every pull request, and the project's `task docs` (or equivalent local target) runs the same sequence
- [ ] Every project-type-specific extension spec that touches MkDocs (`spec/claude/skill-agent-catalog/`, future `cookiecutter-template-docs`, …) declares its added sections (with insertion position and audience), its added plugins (with pin and rationale), and any baseline MUSTs it explicitly relaxes
- [ ] No portfolio repository's `mkdocs.yml` carries more than five extension sections in total (sum across every active extension spec); a repo at or above the cap consolidates sections or proposes a spec amendment
- [ ] Every project's audience artifact covers the portfolio audience baseline (`user`, `contributor`, `operator`, `release-manager`) or explicitly notes the exclusion of any baseline audience the project genuinely doesn't serve
- [ ] `spec/project/project-structure/` carries a one-line cross-reference to this spec next to its MkDocs MUSTs
- [ ] No two portfolio repositories' `mkdocs.yml` files declare conflicting `nav:` shapes for the seven standard sections (extension sections may vary by project type)

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
- None at draft time. The seven initial design questions (ADR-section trigger, Project-section opt-in, extension discovery mechanism, audience baseline, source-language descriptor, extension-section cap, Skills/Agents absolute position) were resolved during initial authoring; see the PR that introduces this spec for the rationale of each.
