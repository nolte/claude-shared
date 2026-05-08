# Mermaid Diagrams in MkDocs Documentation

Status: draft

## Context
MkDocs Material is the documented default for project documentation across this portfolio (see `spec/project/project-structure/`). Whenever a documentation page needs to communicate non-trivial relationships—the dependency graph between a Claude Code plugin's skills and agents, the portfolio map of repositories that consume `nolte/gh-plumbing`, the runtime sequence of a multi-skill workflow, or the schema of a configuration file—prose alone is insufficient and binary images (PNG/SVG screenshots from external editors) drift silently from the code they describe.

Mermaid renders text-described diagrams inline in MkDocs Material via the `pymdownx.superfences` markdown extension and Material's built-in Mermaid bridge. That keeps every diagram source-controlled, diff-able in pull requests, and re-renderable from textual changes. This spec makes Mermaid the canonical diagram tool for portfolio documentation, fixes the supported diagram type per use case, lists the MkDocs-side dependencies a repository must declare to render diagrams, and defines how diagrams stay in sync with the structures they visualize.

## Goals
- Every diagram in portfolio documentation is text-sourced (Mermaid), inline in markdown, source-controlled, and reviewable in a pull-request diff
- Documentation can visualize the structures already present in the repository—Claude plugin manifests, project dependencies, spec cross-references, branching-model flow, configuration schemas—without hand-drawn binaries
- Diagram type selection is deterministic: the same kind of structure always yields the same Mermaid diagram type across repositories
- MkDocs setup for Mermaid is uniform across the portfolio, so any contributor finds the same configuration in `mkdocs.yml` and `docs/requirements.txt`
- Diagrams stay re-derivable: hand-authored diagrams capture their source description next to the block; derived diagrams name the source artifact so the next update knows what to re-read
- Light- and dark-mode rendering is correct without per-diagram color overrides

## Non-Goals
- Methodology for arbitrary diagram tools (PlantUML, Graphviz, draw.io); those aren't supported in this spec
- Domain modeling or formal UML/BPMN compliance
- Replacing prose; diagrams complement, not substitute for, written explanation
- Style customization beyond what MkDocs Material's Mermaid integration provides; per-diagram color overrides are out of scope
- Generation of diagrams from code at build time (for example, parsing `pyproject.toml` during `mkdocs build`); diagrams are written as Mermaid in markdown and updated manually or via a Claude skill, not synthesized by the docs pipeline
- Pre-rendering Mermaid diagrams to static SVG or PNG under `docs/assets/` (or any other directory) for offline preview or first-paint speed; rendering stays strictly client-side via Material's runtime bridge so the Mermaid source in markdown remains the single point of truth and never drifts against a cached image

## Requirements

### MkDocs setup
- **MUST** configure `pymdownx.superfences` in `mkdocs.yml` under `markdown_extensions` with a custom fence for Mermaid:

  ```yaml
  markdown_extensions:
    - pymdownx.superfences:
        custom_fences:
          - name: mermaid
            class: mermaid
            format: !!python/name:pymdownx.superfences.fence_code_format
  ```

- **MUST** include `pymdown-extensions` in `docs/requirements.txt` (or the equivalent docs install set) with an explicit version specifier per `spec/project/project-structure/` "Requirements file format"
- **MUST** keep `mkdocs-material` as the configured theme; Mermaid rendering relies on Material's built-in JavaScript bridge that loads the Mermaid runtime on demand
- **MUST NOT** add a separate Mermaid MkDocs plugin (for example, `mkdocs-mermaid2-plugin`); Material's native superfences-based integration is the portfolio standard, and a second plugin only duplicates the runtime
- **SHOULD** rely on Material's automatic light/dark theme bridge for Mermaid rendering rather than overriding Mermaid colors per diagram
- **SHOULD** verify rendering by running `task docs` (which invokes `mkdocs build --strict`) before merging any change that introduces or modifies a Mermaid block

### Diagram catalog
The following Mermaid diagram types are the supported toolkit for portfolio documentation. Each entry binds one diagram type to the kind of structure it visualizes; deviating from this mapping requires an explicit reason captured in the documentation page that hosts the diagram.

- **`flowchart`**: dependency graphs, plugin / module composition, decision trees, single-direction control flow. Default for "X depends on Y" and "X feeds into Y" diagrams. Default direction `LR` for dependency / pipeline diagrams, `TB` for architecture overviews
- **`C4Component`**: component-level architecture views: which services / modules exist, who calls whom, where the boundary to external systems sits. Default for portfolio maps and "what does this repo look like at a glance"
- **`classDiagram`**: type hierarchies, plugin and skill schemas, manifest structures. Default when visualizing object structure with attributes and methods
- **`sequenceDiagram`**: runtime workflows across actors: a multi-skill orchestration, a CI pipeline run, an end-to-end use case from user trigger to completion
- **`erDiagram`**: data structures with cardinality: configuration file schemas (for example `.github/settings.yml`), database tables, message contracts

`gitGraph` is intentionally **not** part of this catalog: its rendering under MkDocs Material is unreliable (theme-bridge gaps, layout collisions on non-trivial branch structures). Branching and release flows are illustrated with `flowchart LR` instead—see the **Branching model** entry under §Recognized derivation sources.

### Diagram sources
Every Mermaid diagram is sourced from one of two origins, and that origin is captured next to the diagram so future updates know what to re-read.

- **MUST** mark the source of every Mermaid block with an HTML comment immediately above the fence, in one of these forms:
  - `<!-- diagram-source: user-described—<one-line summary of the structure> -->` for hand-authored diagrams from a user description
  - `<!-- diagram-source: derived—<path or identifier of the source structure> -->` for diagrams derived from an existing artifact (for example, `derived—.claude-plugin/plugin.json` or `derived—spec/project/branching-model/en.md`)
- **MUST** redraw a derived diagram when its source structure changes; treat divergence between source and diagram as documentation drift
- **SHOULD** prefer derivation over hand-authoring whenever the source structure exists and is stable enough to read; hand-authoring is for conceptual overviews that don't yet have a machine-readable source
- **MAY** combine multiple sources in one diagram (for example, a `flowchart` showing the plugin manifest plus its skill folder); list each source in the comment

### Recognized derivation sources
The following structures in a portfolio repository are the typical inputs for derived diagrams. Skills that automate diagram generation MUST resolve their source data from these locations.

- **Claude Code plugin**: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, the `skills/<name>/` and `agents/<name>.md` trees → `flowchart` of the plugin's contents, or `C4Component` of the plugin embedded in its consuming repository
- **Python project**: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` → `flowchart` of dependencies (direct vs. development), `classDiagram` for module hierarchies derived from the source tree
- **Node project**: `package.json` (`dependencies`, `devDependencies`) → analogous `flowchart`
- **GitHub Actions workflows**: `.github/workflows/*.yml` plus the `_extends` / `uses` chain into `nolte/gh-plumbing` → `flowchart` of which workflow calls which reusable workflow at which version pin
- **Spec cross-references**: markdown links between specs under `spec/<topic>/<slug>/<lang>.md` → `flowchart` of "spec X references spec Y" relationships
- **Branching model**: the rules in `spec/project/branching-model/` → `flowchart LR` with `subgraph` clusters for `develop`, `main`, and release branches, plus labeled edges for the merge and automerge flow; `gitGraph` is intentionally not used (see the catalog note above)
- **Portfolio map**: the set of repositories under the `nolte` GitHub organization that consume the `nolte-shared` plugin or the `gh-plumbing` reusable workflows. **Default:** each consuming repository renders a focused `C4Component` showing only its own consumption (which reusable workflows or skills it imports, at which version pins). **Consolidated portfolio view:** only `nolte-shared` and `gh-plumbing` themselves render an aggregate `C4Component` whose `subgraph` clusters group consumers, so the portfolio-wide shape stays readable from one canonical place without forcing every consumer repo to track the whole graph

### Authoring rules
- **MUST** place every Mermaid diagram inline in a markdown file under `docs/<lang>/`, never in a separate `.mmd` source file outside the docs tree
- **MUST** precede each diagram with a heading (level 3 or deeper) or a bold caption naming what the diagram shows, plus a one-sentence prose lead-in stating the question the diagram answers
- **MUST** use English for all node labels, edge labels, and identifiers inside the Mermaid block, even in `docs/de/` or any other non-English documentation tree; only the surrounding prose is translated
- **MUST** declare an explicit direction (`flowchart TB`, `flowchart LR`, `flowchart TD`) at the top of every `flowchart`; default to `LR` for dependency / pipeline diagrams and `TB` for architecture overviews
- **MUST NOT** apply per-node or per-edge inline styling (`style`, `linkStyle`, or `classDef` with hard-coded colors); rely on Material's Mermaid theme bridge so light- and dark-mode rendering stays correct
- **SHOULD** keep each Mermaid block under roughly 25 nodes; split into multiple diagrams or use sub-flowcharts when it grows beyond that
- **SHOULD** group related nodes via Mermaid `subgraph` blocks named after the conceptual cluster (for example, `subgraph plugin["nolte-shared plugin"]`)
- **MAY** add a click annotation (`click NodeId href "..."`) to make a node link to the underlying spec, skill folder, or external page

### Translation handling
- Mermaid block content is technical-identifier territory and stays in one canonical language (English) regardless of which `docs/<lang>/` tree the file lives in
- Surrounding prose, captions, and lead-ins are translated per language alongside the rest of the documentation
- Skills that translate documentation MUST treat Mermaid fences as untranslatable code blocks

### Drift behavior
- **MUST** update a derived diagram in the same pull request that changes its named source structure; an unchanged diagram alongside a changed source is a drift finding
- **MUST** keep the one-line summary in a `user-described` diagram-source comment current; if the conceptual content of the diagram changes, the summary changes with it
- **MUST** surface unresolved derived-diagram drift via the `docs-freshness` audit (see `spec/project/docs-freshness/`); the freshness audit treats a Mermaid block whose named `derived` source has been modified more recently than the markdown file containing the block as a drift finding

## Acceptance Criteria
- [ ] `mkdocs.yml` declares `pymdownx.superfences` under `markdown_extensions` with a `mermaid` custom fence using `pymdownx.superfences.fence_code_format`
- [ ] `docs/requirements.txt` lists `pymdown-extensions` with an explicit version specifier
- [ ] `mkdocs.yml` keeps `theme.name: material` and doesn't add `mkdocs-mermaid2-plugin` (or any other Mermaid-only plugin) to its `plugins:` list
- [ ] Every Mermaid block in `docs/<lang>/` is preceded by an HTML `diagram-source` comment naming either `user-described` or `derived` plus a source pointer
- [ ] Every `flowchart` block declares an explicit direction (`TB`, `LR`, or `TD`) on its first line
- [ ] No Mermaid block in the documentation tree contains a `style`, `linkStyle`, or `classDef` directive with a hard-coded color
- [ ] Every Mermaid block sits under a heading or bold caption with a one-sentence prose lead-in
- [ ] All node labels, edge labels, and identifiers inside Mermaid fences are English regardless of the surrounding `docs/<lang>/` tree
- [ ] Each Mermaid diagram type used in the documentation matches the use case in the **Diagram catalog**, or the page that hosts the diagram captures an explicit reason for deviating
- [ ] `task docs` (or `mkdocs build --strict`) renders the documentation without unresolved Mermaid syntax errors
- [ ] When a derived diagram's named source artifact changes, the diagram is updated in the same pull request, or the divergence is recorded as a tracked follow-up
- [ ] The repository's `docs-freshness` audit recognizes Mermaid diagram-source drift as a drift category and reports any `derived`-marked Mermaid block whose source has changed since the hosting markdown file

## Open Questions
- None at this time; the five drafting questions were resolved on 2026-05-08—Q1 (docs-freshness drift): yes, hardened to `MUST` and reflected in `spec/project/docs-freshness/`; Q2 (`gitGraph`): removed from the catalog in favor of `flowchart LR`; Q3 (25-node cap): stays `SHOULD` until a counting lint exists; Q4 (portfolio split): split-per-consumer is the default with a consolidated view only in `nolte-shared` / `gh-plumbing`; Q5 (SVG caching): no, captured as a Non-Goal
