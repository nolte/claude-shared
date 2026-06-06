# Claude Skill and Agent Catalog

Status: draft

## Context
This repository ships reusable Claude Code skills and agents as the `nolte-shared` plugin, and the published MkDocs site is the discovery surface for both this plugin and any other Claude Code plugins consumed alongside it. The `skill-management` and `agent-management` specs define the on-disk shape of these artifacts, but consumers need a browsable catalog to see what's available, what each artifact does, and when Claude will invoke it. Today such a catalog would have to be maintained by hand and would drift whenever a skill or agent is added, renamed, or reworked. This spec defines how the MkDocs documentation site exposes an always-current catalog of skills and agents—generated from the very source files that already govern them, across this plugin and any additional plugins configured into the docs build. It's the foundation for generating the corresponding documentation objects.

**Readers**: catalog-generator implementors (the `scripts/docs/gen_catalog.py` pre-build step), `skill-agent-catalog-apply` skill authors (consumer-side wiring), task-oriented landing-page authors. Skill and agent authors themselves should read `skill-management` and `agent-management` instead—those specs hold the per-artifact authoring rules and delegate catalog-specific schema details (per-language summary, use-case metadata) back to this spec.

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
- The catalog integrates with the existing multilingual MkDocs layout (`docs/en/`, `docs/de/`) and **MAY** carry a translated short summary per language so non-English readers can scan the catalog without losing the English routing metadata
- Each catalog entry surfaces scannable use-case metadata—when to invoke the artifact, when not to (with named alternatives), peers worth comparing, and short prompt/outcome examples—so readers can pick the right skill or agent without reading the full body
- Readers can enter the catalog through task-oriented landing pages ("I want to publish a release," "I want to write a spec") that disambiguate similar artifacts, in addition to the phase- and tag-oriented indexes
- Catalog entries cross-link automatically: structured peer references and inline-code mentions of known skill or agent names become real links between catalog pages

## Non-Goals
- Defining the on-disk shape of skills or agents (owned by `skill-management` and `agent-management`)
- Portfolio-wide MkDocs theme, palette, or typography decisions
- Runtime discovery and loading of skills and agents (owned by Claude Code itself)
- A separate, standalone catalog site—the catalog lives inside the existing `claude-shared` docs site

## Requirements

### MkDocs extension-hook declaration

This spec is a project-type-specific extension of `spec/project/mkdocs-structure/` and bolts onto its skeleton through the two declared extension hooks (§Extension hooks). It declares both hooks explicitly here so the additions are reviewable and additive, never a silent fork:

- **Section extension** (per mkdocs-structure §Extension hooks → Section extension):
  - **Adds** two top-level nav sections, **Skills** and **Agents**.
  - **Insertion position**: immediately after the standard **References** section (so the seven-section skeleton order is preserved and the two catalog sections trail it).
  - **Primary audience**: `contributor` (the `developer-docs` track); every generated catalog page is fixed to `track: developer-docs` per §Generation mechanism, so the sections never carry `user-docs` content.
  - **Per-page frontmatter shape**: the five baseline keys (`title`, `audience`, `content_mode`, `track`, `last_updated`) on every generated page, with `last_updated: generated` and `track: developer-docs` generator-fixed; no extra per-page keys beyond the baseline are required.
  - **Language parity**: the sections follow the standard language-parity rule (a counterpart page at the same relative path in every configured `docs/<lang>/` tree). Page **bodies** quote EN-canonical source frontmatter and therefore declare `source_language: en` per mkdocs-structure §i18n and parity, while the surrounding chrome (section intros, index pages, nav labels via `nav_translations`) is translated.
- **Plugin extension** (per mkdocs-structure §Extension hooks → Plugin extension):
  - **Requires** `mkdocs-literate-nav` and (in the `mkdocs-gen-files` form) `mkdocs-gen-files`, each pinned in the project's Python dependency manifest (`docs/requirements.txt`); no floating versions.
  - **Rationale**: the baseline ships neither plugin because catalog navigation (literate-nav `SUMMARY.md` files) and programmatic page emission are catalog-specific concerns, not skeleton-wide ones.
  - **Baseline interaction**: `mkdocs-static-i18n` with `docs_structure: folder` (a baseline MUST) discards files whose `abs_src_path` isn't under `docs_dir`, so the `mkdocs-gen-files` form silently drops generated pages; this spec's §Generation mechanism therefore recommends the pre-build form (a `task docs` dependency that writes physical files under `docs/<lang>/<section>/`) for repositories on that i18n setup. The extension **MUST NOT** disable any baseline plugin.

### Scope of the catalog
- **MUST** include exactly one catalog entry per skill folder under any configured plugin source root that contains a valid `SKILL.md`
- **MUST** include exactly one catalog entry per agent file (`<name>.md`) under any configured plugin source root
- **MUST** discover skills and agents from every plugin source root configured for the catalog generator
- **MUST**, in plugin mode, include the local plugin (its own `skills/` and `agents/` folders) as one of the configured source roots
- **MUST**, in consumer mode, configure at least one external plugin source root; the catalog isn't useful when no sources are declared
- **MUST NOT** include skills or agents that don't conform to the `skill-management` / `agent-management` structure; malformed entries **MUST** fail the docs build rather than be silently omitted

### Content of a catalog entry
- **MUST** render the frontmatter `name` as the page title
- **MUST** include the full `description` verbatim—the generator preserves the source text without translation, summarization, or content substitution. The cross-linking pass described in §Cross-linking is the single sanctioned exception: it rewrites inline-code mentions of known artifact names into Markdown links without altering surrounding prose
- **MUST**, when the artifact's frontmatter declares `summary`, render that summary as a short subtitle above the routing description (see "Per-language short summary" below for the per-language resolution and fallback rules)
- **MUST**, when the artifact's frontmatter declares any of `use_when`, `dont_use_when`, `see_also`, or `examples`, render the corresponding scannable section using the chrome-localized labels (see "Use-case metadata" below)
- **MUST** include the `distribution` field for agents (`plugin` or `project`)
- **MUST** label each entry with the source plugin it comes from (for example `nolte-shared`)
- **MUST** link to the source file in the originating plugin's repository on its main branch; the link base URL is configured per plugin source root (for example `https://github.com/nolte/claude-shared/blob/main/...`). This source-file link is also the catalog's history surface: the catalog **MUST NOT** record per-artifact version or changelog metadata, consistent with the `skill-management` and `agent-management` specs—the link reaches the file's full git history (the per-artifact change record) and versioning is plugin-level only (the single `.claude-plugin/plugin.json` manifest version, maintained per `release-automation` §Version-bearing file alignment)
- **MUST** render any `tags` declared in the artifact's frontmatter as visible tags on the entry page; `tags` are normalized per `skill-management` / `agent-management` (lowercase ASCII kebab-case, ≤30 characters, ≤5 entries)
- **MUST** render the artifact's `phase` (see "Phase classification" below) as a visible badge on the entry page, using the phase label from the localized chrome
- **SHOULD** render the body of `SKILL.md` (or the agent system-prompt markdown) as the page's main content so authors' instructions are visible to readers
- **MAY** surface supporting assets by listing sibling files under `skills/<name>/` (for example `templates/`, `references/`, `examples/`); agents are single self-contained files with no sibling folder (per `agent-management` §Structure), so there are no agent-side sibling assets to list

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

### Per-language short summary
The `description` field is the routing source-of-truth Claude Code reads to decide whether to dispatch an artifact, so it tends to be long, English, and trigger-dense—hard for a human reader to scan, hard for a non-English reader to grasp. The catalog therefore renders an additional, optional, per-language **short summary** above the routing description.

- **MAY** declare a top-level `summary:` field in the YAML frontmatter of a skill (`SKILL.md`) or agent (`<name>.md`); the value is a string, ≤200 characters, written in English (the canonical metadata language per `skill-management` / `agent-management`)
- **MAY** declare, for every additional docs language `<lang>` configured in the consuming MkDocs site (per `spec/project/mkdocs-structure/` §i18n and parity), a sibling field `summary_<lang>:` (for example `summary_de:`) carrying the translated short summary; the value is a string, ≤200 characters
- **MUST**, when rendering the catalog page for docs language `<lang>`, resolve the displayed summary in this order: (1) `summary_<lang>` if declared, (2) `summary` (the English canonical) if declared, (3) the first sentence of `description` truncated to 200 characters as the fallback
- **MUST**, when a catalog page falls back to the English `summary` or to the `description` truncation in a non-English docs language, render a visible "translation pending" badge using the chrome-localized label, AND tag the page with the reserved auto-tag `_translation-pending` so the tag index surfaces every untranslated entry
- **MUST NOT** treat `_translation-pending` as an author-declared tag; the underscore-prefixed name is reserved for generator-emitted auto-tags and **MUST NOT** appear in the artifact's `tags` frontmatter (the underscore prefix is the visible marker that the tag isn't human-curated)
- **MUST** validate `summary` and every `summary_<lang>` as plain strings; the docs build fails with a clear file-and-field error when the value is missing the string type, exceeds 200 characters, or is empty after whitespace stripping

### Use-case metadata
The `description` field collapses every routing signal—positive triggers, negative triggers, alternatives, examples—into a single dense prose block, which makes it hard for human readers to scan and impossible for the catalog to link peers automatically. This section defines four optional, structured frontmatter fields the catalog renders as scannable sections and uses to drive automatic cross-linking (see "Cross-linking" below).

- **MAY** declare a `use_when:` field in the YAML frontmatter of a skill or agent; the value is a YAML list of plain strings, each describing one concrete trigger scenario ("you want to publish a release," "you have a failing CI run on `develop`"). Limits: ≤6 entries, each ≤120 characters
- **MAY** declare a `dont_use_when:` field; the value is a YAML list of mappings, each with the keys `situation` (plain string, ≤120 characters) and `alternative` (a single skill or agent `name` to redirect to). Limits: ≤6 entries; every `alternative` value **MUST** resolve to a skill or agent discoverable in any configured plugin source root, or the docs build fails
- **MAY** declare a `see_also:` field; the value is a YAML list of skill or agent names (each a plain string matching a discoverable artifact's `name`). Limits: ≤8 entries; every entry **MUST** resolve to a discoverable artifact
- **MAY** declare an `examples:` field; the value is a YAML list of mappings, each with the keys `prompt` (plain string, ≤200 characters, illustrating the kind of request that triggers the artifact) and `outcome` (plain string, ≤200 characters, describing the artifact's response). Limits: ≤4 entries
- **MUST** render each declared field on the catalog page as its own scannable section using the chrome-localized labels (for English: `Use when`, `Don't use when`, `See also`, `Examples`; for German: `Anwenden wenn`, `Nicht anwenden wenn`, `Siehe auch`, `Beispiele`)
- **MUST** treat all four fields as optional in this spec; their authoring requirement (when authors **SHOULD** declare them) is owned by `skill-management` and `agent-management`. This spec owns only the schema and validation, so the fields stay optional here permanently; any decision to strengthen the authoring `SHOULD` (or flip it to a `MUST` for new artifacts within a known peer cluster) belongs to those owner specs, not here
- **MUST** validate every field's shape (list type, element type, key set, character limits) and the resolvability of `dont_use_when[].alternative` and `see_also[]` against the discovered catalog; on any violation the docs build fails with a clear error naming the offending file, field, and value

### Generation mechanism
- **MUST** generate catalog pages from the source files
- **MUST** keep the published catalog current by one of two mechanisms, chosen by whether the docs-deploy pipeline actually runs the generator on the deploy build:
  - **Deploy-time generation (preferred):** when the deploy pipeline invokes the catalog generator on the deploy build (for example a `reusable-mkdocs.yaml` that runs `task docs` when a Taskfile with a `docs` target exists, or `mkdocs build` with the generator wired as a `mkdocs-gen-files` script), the repository **MUST NOT** commit generated catalog markdown into `docs/`—the catalog is regenerated on every build and no committed-artifact freshness check is needed.
  - **Committed catalog with a freshness gate (fallback):** when the shared deploy reusable does **not** run the generator—for example `nolte/gh-plumbing`'s `reusable-mkdocs.yaml@v1.1.19` deploys through `mhausenblas/mkdocs-deploy-gh-pages`, which runs `mkdocs build` only and never invokes `task docs`—the repository **MUST** commit the generated catalog tree and **MUST** enforce a CI freshness check that fails when the committed tree has drifted from a fresh regeneration (the generator still runs locally via the `task docs` pre-build dependency and the `docs-catalog-fresh` pre-commit hook). This keeps the published GitHub Pages output complete despite the deploy build skipping the generator. A repository on this fallback **MUST** retire it in favour of deploy-time generation once the shared deploy reusable invokes the generator.
- **MUST** wire catalog navigation through `mkdocs-literate-nav` declared in `mkdocs.yml`
- **MUST** invoke a catalog generator that produces the per-artifact pages, per-section index pages, per-section `SUMMARY.md` files for literate-nav, and the tag index. The generator **MAY** be a `mkdocs-gen-files` plugin script OR a standalone pre-build step (for example a Taskfile target invoked before `mkdocs build`) that writes physical files under `docs/<lang>/<section>/`. The pre-build form is the recommended choice whenever the repo also uses `mkdocs-static-i18n` with `docs_structure: folder`, because `mkdocs-static-i18n` 1.3.x discards files whose `abs_src_path` isn't under `docs_dir` and therefore silently drops every page emitted by `mkdocs-gen-files`
- **MUST** read plugin source roots from a configured list—each entry pairing the local source path with the public repository URL used for source links—so additional plugins can be added without changing generator code. The configured list of source roots lives in `docs/catalog-sources.yml` (a sibling YAML file under `docs_dir`), not inline in `mkdocs.yml`
- **MUST** expose catalog generation through `task docs` so local builds and CI produce identical output; in the pre-build form this is wired by declaring the generator step as a Taskfile dependency of the docs task
- **MUST NOT** require a separate manual "regenerate catalog" step outside the normal docs build
- **MUST** write the five per-page MUST frontmatter keys (`title`, `audience`, `content_mode`, `track`, `last_updated`) per `spec/project/mkdocs-structure/` §Per-page structure on every generated catalog file (per-artifact page, per-section `index.md`, literate-nav `SUMMARY.md`, tag index, task-oriented landing page). The generator **MUST** fix `track: developer-docs` for every catalog file (rather than reading the value per-artifact from source frontmatter) per `spec/project/docs-audience-tracks/` §Audience-to-track mapping, so the catalog audience stays consistent across source plugins and per-page `track` values don't drift
- **MUST** parse source frontmatter with a standard YAML parser (PyYAML or equivalent) that supports nested mappings and sequences of mappings; the older flat-only line parser is insufficient because `dont_use_when` and `examples` (see "Use-case metadata") declare lists of mappings

### Cross-linking
The catalog is a network of related artifacts, but a reader can only follow that network when peer references are real hyperlinks. The generator therefore performs two cross-linking passes after discovering every artifact across every plugin source root.

- **MUST** build, per docs language, an index mapping each discovered artifact's `name` to its catalog page URL (one entry per skill, one per agent) before rendering any page
- **MUST** transform every structured peer reference into a Markdown link to the peer's catalog page: every `dont_use_when[].alternative` value and every `see_also[]` entry **MUST** render as a clickable link, never as plain text
- **MUST** transform inline-code mentions of known artifact names in the rendered `description`, `summary`, `summary_<lang>`, and body into Markdown links to the matching catalog page, **but only** when the inline-code span (`` `name` ``) matches exactly one entry in the cross-link index for that docs language
- **MUST NOT** transform plain-text occurrences of artifact names outside inline-code spans, to avoid false positives on generic words that coincidentally collide with an artifact name
- **MUST**, when an inline-code mention matches more than one artifact (for example a skill and an agent share the same short label, or two plugins ship artifacts of the same name), leave the mention unlinked AND emit a generator warning naming the file, the ambiguous mention, and the colliding artifacts
- **MUST**, when a structured peer reference (`dont_use_when[].alternative` or `see_also[]`) doesn't resolve to any discovered artifact, fail the docs build (per "Use-case metadata" above); inline-code mentions that don't resolve are left as plain inline code without a warning
- **SHOULD** render a "Referenced by" section on each artifact page listing every artifact whose `see_also` includes this artifact, derived by inverting the cross-link index in a single in-memory pass over the already-parsed data, under a chrome-localized label; this surfaces one-directional `see_also` asymmetries authors miss

### Navigation and layout
- **MUST** expose the catalog under stable top-level sections in the MkDocs navigation—at minimum a `Skills` section and an `Agents` section
- **MUST** group entries within each section **first by phase** (in the canonical phase order listed under "Phase classification": `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`), then by source plugin within each phase, so readers can see at a glance which artifacts apply to each delivery-lifecycle phase
- **MUST** order catalog entries deterministically—alphabetical by `name` within each plugin sub-group of each phase—so diffs of the rendered site stay stable
- **MUST** omit a phase heading that has no entries; an empty phase isn't rendered
- **MUST** provide an index page per section summarizing every entry (name + description + phase + tags) with links to the detail pages; the index page **MUST** include a prominent link to the section's task-oriented landing page (see "Task-oriented landing pages" below). Discoverability is this spec's core mission and a catalog without per-section index pages would force readers back into the navigation tree to scan
- **MUST** provide a tag index that lists every tag across all entries and links to the artifacts that declare it; the tag index **MUST** also list every reserved auto-tag emitted by the generator (currently `_translation-pending`) when at least one artifact carries it. When no artifact in the catalog declares any tag the page **MAY** be omitted; the generator then **MUST NOT** leave a dangling link from any other catalog page

### Task-oriented landing pages
The phase- and tag-oriented indexes assume a reader who already speaks the catalog's vocabulary. A reader who only knows what they want to do—"publish a release," "write a spec," "open a PR"—is left guessing. A small set of hand-curated, task-oriented landing pages closes that gap by grouping artifacts by user intent rather than by lifecycle phase.

- **MUST** ship at least one task-oriented landing page per configured docs language at a stable path under each section (recommended: `docs/<lang>/skills/by-task.md` and `docs/<lang>/agents/by-task.md`, or a combined `docs/<lang>/by-task.md` linked from both section indexes)
- **MUST** group artifacts on the landing page by user-intent rubrics (each rubric a short H2 such as "Open a pull request," "Publish a release," "Author a spec," "Audit something"); under each rubric, list the relevant skills and agents with a one-sentence disambiguation that tells the reader which one to pick when several are listed
- **SHOULD** keep the rubric set small at first (three to five rubrics) and grow it as use-case patterns emerge; an exhaustive landing page that mirrors the phase index defeats its purpose
- **MAY** have the catalog generator emit a skeleton landing-page file populated from artifacts' `use_when` entries when no landing page exists yet; the skeleton is a starting point for a human author, and the generator **MUST NOT** rewrite it on subsequent runs once the file exists
- **MUST** treat the landing page as a regular MkDocs page subject to the five-key per-page frontmatter contract (`title`, `audience`, `content_mode`, `track`, `last_updated`); generator-emitted skeletons declare `last_updated: generated`, hand-curated landing pages carry an ISO-8601 date

### Multilingual behavior
- **MUST** render artifact identifiers (`name`, `distribution`, `tags`, `phase`) as-is from the source frontmatter; these are technical identifiers and **MUST NOT** be translated, case-folded, or otherwise rewritten between docs languages
- **MUST** render the source `description` and body without translation, summarization, or content substitution—these fields are the routing source-of-truth Claude reads to dispatch the artifact, and their wording stays untouched. The cross-linking pass described in §Cross-linking is the single sanctioned exception: it rewrites inline-code mentions of known artifact names into Markdown links without altering surrounding prose
- **MAY** render a translated short summary above the routing description per docs language, sourced from the `summary_<lang>` frontmatter field per "Per-language short summary" above; this is the single sanctioned translation surface for catalog content
- **SHOULD** localize the surrounding chrome—section titles, intro paragraphs, navigation labels, tag-index header, phase labels, use-case section labels, "translation pending" badge—into each configured docs language (`docs/en/`, `docs/de/`)
- **MUST NOT** translate `description`, body, identifiers, or `tags` at generation time; the only translated catalog content is the per-language summary and the chrome

### Error handling
- **MUST** fail the docs build when a skill or agent has missing or invalid frontmatter rather than producing a broken catalog
- **MUST** emit a clear error message that names the offending source file and the plugin source root it came from
- **MUST** fail the docs build when an artifact's `phase` is missing or isn't in the phase vocabulary, with an error message that names the offending file, the plugin source root, and the value of the rejected `phase`
- **MUST** fail the docs build when `summary` or any `summary_<lang>` violates its shape constraints (non-string type, empty after whitespace stripping, or longer than 200 characters), naming the offending file and field
- **MUST** fail the docs build when any of `use_when`, `dont_use_when`, `see_also`, or `examples` violates its shape contract from "Use-case metadata" (wrong type, wrong key set on mapping elements, over the entry or character limit), naming the offending file, field, and offending value
- **MUST** fail the docs build when a `dont_use_when[].alternative` or `see_also[]` value names a skill or agent that no configured plugin source root provides, naming the offending file, the unresolved name, and the field it appeared in
- **MUST** emit a non-fatal generator warning (build still passes) when an inline-code mention in a rendered `description`, `summary`, `summary_<lang>`, or body matches more than one discovered artifact and is therefore left unlinked, naming the offending file, the ambiguous mention, and the colliding artifacts

## Acceptance Criteria
- [ ] `task docs` produces a docs site whose navigation contains a Skills section with one page per skill across all configured plugin source roots
- [ ] `task docs` produces a docs site whose navigation contains an Agents section with one page per agent across all configured plugin source roots
- [ ] Each catalog page displays the artifact's `name`, `description`, source plugin label, and—for agents: `distribution`
- [ ] When an artifact's frontmatter declares `tags`, those tags appear on the catalog page
- [ ] Each catalog page contains a direct link to the source file on the originating plugin's main-branch repository URL
- [ ] Adding a new skill or agent in any configured plugin source root requires no manual edit to `docs/` or `mkdocs.yml` for the entry to appear
- [ ] Every generated catalog file (per-artifact page, per-section `index.md`, literate-nav `SUMMARY.md`, tag index, task-oriented landing page) declares the five-key per-page frontmatter set (`title`, `audience`, `content_mode`, `track`, `last_updated`) per `spec/project/mkdocs-structure/` §Per-page structure; the `track` value is generator-fixed to `developer-docs` per `spec/project/docs-audience-tracks/`
- [ ] Removing a skill or agent removes the corresponding catalog page on the next `task docs` run
- [ ] `mkdocs.yml` declares `mkdocs-literate-nav`, and a configured list of plugin source roots (each pairing a local path with a public repository URL) is read by the catalog generator
- [ ] The catalog generator is either declared as a `mkdocs-gen-files` script in `mkdocs.yml` or wired into `task docs` as a standalone pre-build step
- [ ] In plugin mode, the local plugin appears as one of the configured plugin source roots
- [ ] In consumer mode, at least one external plugin source root is configured
- [ ] Generated catalog markdown isn't committed under `docs/`; the docs-deploy pipeline regenerates the catalog on every build (via `task docs` when a Taskfile `docs` target exists, else `mkdocs build` with the generator wired as a `mkdocs-gen-files` script)
- [ ] A skill or agent with invalid frontmatter causes `task docs` to fail with an error that names the offending file and its plugin source root
- [ ] Catalog entries appear grouped first by phase (in the canonical phase order) and then alphabetically by `name` within each plugin sub-group of each phase
- [ ] Every skill and agent declares a `phase` from the closed eight-value vocabulary (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); a missing or out-of-vocabulary `phase` fails `task docs`
- [ ] Each catalog page displays the artifact's `phase` as a visible badge using the localized chrome label
- [ ] The Skills and Agents index pages render a per-phase heading (omitting phases with zero entries) above each plugin sub-group
- [ ] A tag index page exists and links to every artifact that declares the tag
- [ ] Each section index page links prominently to its task-oriented landing page (`by-task.md`)
- [ ] At least one task-oriented landing page exists per configured docs language, grouping artifacts by user intent with one-sentence disambiguations
- [ ] When an artifact declares `summary`, the catalog page renders it as a short subtitle above the routing `description`; when `summary_<lang>` is declared for a docs language, the `<lang>` page renders the translated summary instead
- [ ] When the catalog falls back to the English `summary` or to a `description` truncation on a non-English docs language, the page shows a chrome-localized "translation pending" badge and the auto-tag `_translation-pending` appears in the tag index
- [ ] The reserved auto-tag `_translation-pending` is never accepted in source-frontmatter `tags`; declaring it there fails the docs build
- [ ] When an artifact declares `use_when`, `dont_use_when`, `see_also`, or `examples`, the catalog page renders each declared field as a scannable section under a chrome-localized label
- [ ] `dont_use_when[].alternative` and `see_also[]` values render as Markdown links pointing to the referenced artifact's catalog page; an unresolvable name fails the docs build
- [ ] Inline-code mentions (`` `name` ``) of known artifact names in `description`, `summary`, `summary_<lang>`, and body render as Markdown links to the matching catalog page; ambiguous mentions stay unlinked and emit a generator warning naming the file and colliding artifacts
- [ ] Each artifact page renders a chrome-localized "Referenced by" section listing every artifact whose `see_also` includes this artifact, derived by inverting the cross-link index
- [ ] A `summary` or `summary_<lang>` longer than 200 characters or empty after whitespace stripping fails the docs build with a file-and-field error
- [ ] A malformed `use_when`, `dont_use_when`, `see_also`, or `examples` (wrong type, wrong key set, over the limit) fails the docs build with a file-and-field error
- [ ] The catalog generator parses source frontmatter with a standard YAML parser that supports nested mappings (rejecting the older flat-only line parser)
- [ ] Every task-oriented landing page (generator-emitted skeleton or hand-curated) declares the five-key per-page frontmatter set; generator-emitted skeletons carry `last_updated: generated`, hand-curated landing pages carry an ISO-8601 date
- [ ] When the catalog generator emits a skeleton landing page from artifacts' `use_when` entries, a subsequent `task docs` run leaves the file unchanged if it already exists; the skeleton is a one-shot starting point
- [ ] Plain-text occurrences of artifact names that aren't wrapped in inline-code spans (backticks) are never transformed into Markdown links on any rendered catalog page—only inline-code mentions are eligible for the cross-linking rewrite

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the per-item decisions and rationale._
