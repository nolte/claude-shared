---
name: mermaid-diagrams-apply
description: >-
  Audit and apply the MkDocs Mermaid setup of the current repository against
  `spec/project/mermaid-diagrams/<canonical_language>.md`, and help an author
  add a single Mermaid diagram—either hand-described or derived from an
  existing structure—without violating the spec. Wires up `pymdownx.superfences`
  with the Mermaid `custom_fences` block in `mkdocs.yml`, ensures
  `pymdown-extensions` is pinned in `docs/requirements.txt` per the
  project-structure "Requirements file format" rules, and refuses to install
  `mkdocs-mermaid2-plugin` (Material's native bridge is the portfolio standard).
  When drafting a diagram, picks the type from the supported catalog
  (`flowchart`, `C4Component`, `classDiagram`, `sequenceDiagram`, `erDiagram`),
  prepends the mandatory `<!-- diagram-source ... -->` marker (either
  user-described with a one-line summary, or derived with a path pointer),
  and emits English-only labels even inside `docs/de/`. When auditing, scans
  every Mermaid block under the configured `docs_dir` and flags missing source
  markers, missing `flowchart` direction headers, inline styling, `gitGraph`
  usage, type-vs-use-case mismatches, non-English labels, and derived-source
  drift (source's last-commit timestamp newer than the hosting markdown).
  Invoke when the user asks to "wire up Mermaid in this repo", "scaffold
  Mermaid for MkDocs", "audit Mermaid setup", "draft a flowchart for the
  plugin manifest", "derive a dependency diagram from pyproject.toml", "audit
  Mermaid blocks in the docs against the spec", or equivalent German-language
  requests ("Mermaid in diesem Repo einrichten", "Mermaid-Setup auditieren",
  "Diagramm aus pyproject.toml ableiten", "Flowchart für das Plugin-Manifest
  erzeugen", "Mermaid-Blöcke gegen die Spec auditieren"). Don't use for
  general MkDocs scaffolding (that's `project-structure-apply`), for spec
  authoring (that's the `nolte-shared:spec` skill), for running the
  docs-freshness audit itself (that's the `docs-freshness-checker` agent),
  or for diagrams outside Mermaid (PlantUML, Graphviz, draw.io aren't
  covered by the spec).
tags: [scaffolding, audit]
---

# Mermaid Diagrams Apply

Audits and repairs a repository so its MkDocs Mermaid setup, its existing diagrams, and any newly authored diagram match the Mermaid Diagrams spec at `spec/project/mermaid-diagrams/<canonical_language>.md`. The skill both reports findings (read-only audit) and—with explicit per-item user consent—writes the missing or fixed pieces in place.

## Why this is a skill, not an agent

- **Per-block user approval is the contract**: every Mermaid block emitted (or fixed) is shown to the user before it lands; the audit is read-only and the apply step is a sequence of approvals an agent's fire-and-forget shape can't carry.
- **Output flows back into the main conversation**: the audit table, the per-finding fix proposals, and the diagram drafts surface inline so the user can redirect the type choice or the source pointer; isolating that in a structured-report boundary would obscure the per-block approval surface.
- **Mid-flow type selection is load-bearing**: choosing between `flowchart` and `C4Component` for a portfolio map, or between `sequenceDiagram` and `flowchart` for a runtime workflow, is an interactive judgment call against the spec's catalog; that gating fits skill form, not an autonomous agent contract.
- Counter-dimension considered: a narrower agent could specialize on parsing source artifacts (for example `pyproject.toml` → flowchart) and gain on context-window protection, but the high-impact part is the type-and-placement dialogue, not the parsing; skill wins.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path, or from the `nolte/claude-shared` repository). Never invent requirements that aren't in the spec.

## User-language policy

Detect the user's language and respond in it. Generated content is split:

- **Mermaid block content** (node labels, edge labels, identifiers, `subgraph` headings) is always English, even when the hosting markdown lives under `docs/de/`. The spec treats Mermaid fences as technical-identifier territory.
- **Surrounding prose** (heading, lead-in sentence, `<!-- diagram-source: ... -->` comment summary) follows the language of the markdown file the diagram is added to.
- **Generated config snippets** (`mkdocs.yml` keys, `docs/requirements.txt` entries) are English regardless of conversation language.

## Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
- Locate `spec/project/mermaid-diagrams/`. The spec lives either in the target repo or in the nolte-shared plugin; if neither is reachable, stop and ask the user which spec source to use.
- Locate `mkdocs.yml` at the repository root. If it's missing, stop and route the user to `project-structure-apply`. Setting up MkDocs from scratch is that skill's job, not this one.
- Read `mkdocs.yml`'s `docs_dir` (default `docs/`) and any configured language trees; the audit's scope is everything under that path.
- Check for uncommitted changes in `mkdocs.yml`, `docs/`, and `docs/requirements.txt`. If the tree is dirty there, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

## Operations

### 1. Setup audit

Walk through the spec's "MkDocs setup" requirements one item at a time and classify each as:

- **pass**: configuration matches the spec.
- **missing**: required key or file absent.
- **drift**: present but diverges (wrong format, conflicting plugin, missing version specifier, etc.).

Report findings grouped under: `mkdocs.yml` extensions, `docs/requirements.txt` entries, theme, forbidden plugins. Audit is read-only—never autofix during audit.

Items to check:

- `markdown_extensions` includes `pymdownx.superfences` with a `custom_fences` entry whose `name: mermaid`, `class: mermaid`, and `format: !!python/name:pymdownx.superfences.fence_code_format`.
- `docs/requirements.txt` lists `pymdown-extensions` with an explicit version specifier (`>=`, `==`, `~=`, …).
- `theme.name` is `material`.
- `plugins:` doesn't contain `mkdocs-mermaid2-plugin` or any other Mermaid-only plugin.

### 2. Setup apply

After the audit, walk findings one at a time. For each one, propose the minimal fix and ask for confirmation before writing:

- **`mkdocs.yml` missing the Mermaid `custom_fence`**: merge the `custom_fences` entry into the existing `pymdownx.superfences` block, or add the whole extension entry if `pymdownx.superfences` is absent. Preserve every other extension and key. Never replace the file wholesale.
- **`docs/requirements.txt` missing `pymdown-extensions`**: append the entry with a Renovate-friendly minimum-version specifier (for example, `pymdown-extensions>=10`). Honor the "Requirements file format" rules from `spec/project/project-structure/`: one entry per line, no `-r` chains, no bare names.
- **`mkdocs-mermaid2-plugin` (or another Mermaid-only plugin) present**: report it as drift and ask the user before removing—some repos may have non-spec history that needs documenting before removal.
- **Theme not `material`**: report as drift and stop. Don't switch themes silently; that's a structural decision that belongs to the user, not this skill.

After every successful write, re-run only the affected check so the user sees the item flip to **pass**. Never batch silent writes.

### 3. Diagram authoring

Add a single Mermaid diagram to a markdown file under `docs_dir`. Two source modes:

#### user-described

1. Ask for: the conceptual structure to visualize (one or two sentences), the target markdown file path (must already exist), the diagram type from the catalog (`flowchart` / `C4Component` / `classDiagram` / `sequenceDiagram` / `erDiagram`).
2. Validate the type matches the structure: dependency / pipeline → `flowchart`; component / portfolio → `C4Component`; type-or-schema hierarchy → `classDiagram`; runtime workflow with actors → `sequenceDiagram`; data structure with cardinality → `erDiagram`. If the user-picked type doesn't fit, propose the catalog-fitting type and explain.
3. Draft the block with: heading or bold caption + one-sentence prose lead-in (in the markdown file's language), `<!-- diagram-source: user-described—<one-line summary> -->` immediately above the fence, and the Mermaid content in English.
4. For `flowchart`, default direction to `LR` for dependency / pipeline diagrams and `TB` for architecture overviews; always declare the direction explicitly on the first line.
5. Show the full proposed insertion to the user. Only write after explicit approval.

#### derived

1. Ask for: the target markdown file path, the source artifact (one of the recognized derivation sources from the spec). The source must be a real path in the repo.
2. Read the source artifact and extract nodes/edges:
   - `.claude-plugin/plugin.json` → plugin name, version, owner, included skills/agents → `flowchart` or `C4Component`.
   - `pyproject.toml` + `requirements.txt` + `requirements-dev.txt` → direct vs. development dependencies → `flowchart LR` (root → direct → development).
   - `package.json` (`dependencies`, `devDependencies`) → analogous `flowchart`.
   - `.github/workflows/*.yml` with `_extends` / `uses` chains into `nolte/gh-plumbing` → `flowchart` of caller-workflow → reusable-workflow at version pin.
   - Markdown links between specs under `spec/<topic>/<slug>/<lang>.md` → `flowchart` of cross-reference relationships.
   - `spec/project/branching-model/` → `flowchart LR` with `subgraph` clusters for `develop` / `main` / release branches plus labeled merge / automerge edges. **Never emit `gitGraph`**: it's removed from the catalog.
   - Portfolio map (consumers of `nolte-shared` or `gh-plumbing`) → focused `C4Component` per consumer; consolidated `C4Component` with consumer-level `subgraph` blocks only inside `nolte-shared` and `gh-plumbing` themselves.
3. Draft the block with `<!-- diagram-source: derived—<relative path or identifier> -->` above the fence; if the derivation pulls from multiple sources, list each in the comment.
4. Same direction-default and labeling rules as user-described.
5. Show the proposed insertion and the source-to-node mapping. Only write after explicit approval.

### 4. Diagram audit

Scan every markdown file under `docs_dir`, locate Mermaid fences (` ```mermaid `), and report findings classified by category:

- **Missing source marker**: no `<!-- diagram-source: ... -->` comment on the line directly above the fence.
- **Missing `flowchart` direction**: a `flowchart` block whose first line lacks an explicit `TB` / `LR` / `TD`.
- **Inline styling**: any `style`, `linkStyle`, or `classDef` directive with a hard-coded color literal inside the block.
- **`gitGraph` usage**: any block that starts with `gitGraph`. The catalog removed this type, so any occurrence is non-conformant.
- **Type-vs-use-case mismatch**: when the surrounding heading / prose suggests one structure but the block uses another (heuristic; ask the user when unsure rather than classifying automatically).
- **Non-English labels**: any node or edge label containing characters outside ASCII letters, digits, common punctuation, or a small allowlist (English markdown).
- **Derived-source drift**: for any block marked `derived—<path>`, compare `git log -1 --format=%cs -- <path>` against `git log -1 --format=%cs -- <markdown-file>`. If the source is newer, flag drift. Surface this as a finding here even though the authoritative audit lives in the `docs-freshness-checker` agent.
- **Block size**: more than ~25 nodes (SHOULD violation, not a hard block).

For each finding, propose the minimal fix and ask for confirmation. Never write without approval. For derived-drift findings, the fix is "redraft the block from the current source"—route back to operation 3's derived mode.

### 5. Re-audit

When the user has finished approving changes, re-run operations 1 and 4 end-to-end and present a fresh grouped summary. Items still **missing**, **drift**, or with an open finding must be called out so the user knows what remains and why.

## Gotchas

- **`pymdownx.superfences` may already exist** without the Mermaid `custom_fence`. Merge into the existing block; don't add a second `pymdownx.superfences` entry—MkDocs will silently use only one and the merge order is undefined.
- **`!!python/name:pymdownx.superfences.fence_code_format`** is a YAML constructor tag. Some YAML loaders (notably plain `yaml.safe_load`) reject it. When reading `mkdocs.yml`, treat it as a string for the purpose of detection rather than parsing it.
- **Multilingual repos with `i18n`**: when the docs use the `mkdocs-static-i18n` plugin in `docs_structure: folder` mode, the audit must walk every configured language tree, not just the default. Pull the language list from `plugins.i18n.languages`.
- **Mermaid v10+ syntax**: Material loads Mermaid 10 by default. `flowchart` syntax replaces the older `graph` keyword; emit `flowchart` exclusively. Existing `graph TB` blocks discovered in the audit are drift but not breakage—Mermaid still accepts them—so propose a one-line keyword swap rather than a full rewrite.
- **`erDiagram` cardinality glyphs** (`||--o{`, `}o--||`) render only when the surrounding fence has the `mermaid` class; they break with a generic ` ```text` fence. The audit checks the fence header, not just the content keyword.
- **Trailing whitespace inside `<!-- diagram-source: ... -->`**: the marker is detected by exact prefix match. A trailing space before `-->` doesn't break the comment but breaks naive grep-based scanners; trim before writing.
- **`docs/requirements.txt` may not exist** even when MkDocs is configured—some repos rely on a `pyproject.toml` `[project.optional-dependencies.docs]` group. Ask the user where the docs install set lives before scaffolding a new `docs/requirements.txt`.

## Hard rules

- **Never** install or scaffold a Mermaid-only MkDocs plugin (`mkdocs-mermaid2-plugin` or any equivalent). Material's native superfences-based bridge is the portfolio standard, and a second plugin only duplicates the runtime.
- **Never** write a pre-rendered SVG or PNG diagram under `docs/assets/` (or any other directory) as a substitute for the Mermaid source. Rendering stays strictly client-side; the Mermaid source in markdown is the single point of truth.
- **Never** emit inline styling (`style`, `linkStyle`, or `classDef` with hard-coded colors) inside a Mermaid block this skill writes.
- **Never** emit `gitGraph` as a diagram type. The spec removed it from the catalog because of rendering quirks under MkDocs Material; branching diagrams use `flowchart LR` with `subgraph` clusters.
- **Never** emit node labels, edge labels, or identifiers in any language other than English inside a Mermaid fence—not even when the hosting markdown is in `docs/de/`.
- **Never** write a Mermaid block without a preceding `<!-- diagram-source: user-described | derived—<pointer> -->` comment.
- **Never** perform silent writes. Every file change requires explicit per-item user confirmation; every audit finding is presented to the user before any fix is written.
- **Never** take on `project-structure-apply` work. If the audit reveals that `mkdocs.yml` is missing entirely, the docs tree is absent, or `theme.name` is something other than `material`, stop and route the user to `project-structure-apply`—don't silently scaffold those out of scope.
- **Never** modify the spec while applying it. If a real-world need conflicts with `spec/project/mermaid-diagrams/`, report it and ask the user to update the spec via the `nolte-shared:spec` skill before proceeding.
- **Never** edit a Mermaid block in another markdown file as a side-effect of the current operation. Each operation touches one block (or one config file) at a time, with its own approval.
