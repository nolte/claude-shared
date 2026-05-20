# Operations — mkdocs-structure-apply

Detailed step-by-step procedures for each operation. Loaded on demand when executing any operation.

## Table of Contents

1. [Operation 1: audit (read-only)](#1-audit-read-only)
2. [Operation 2: scaffold (greenfield: mkdocs.yml absent)](#2-scaffold-greenfield-mkdocsyml-absent)
3. [Operation 3: patch (additive: mkdocs.yml present)](#3-patch-additive-mkdocsyml-present)

---

## 1. audit (read-only)

Walk through the spec's Acceptance Criteria one item at a time, plus every active extension spec's MUSTs, and classify each finding as `pass`, `missing`, or `drift`. Group findings by spec area:

- **Site layout**: `docs_dir: docs`, per-language `docs/<lang>/` trees, file-name parity across configured languages, no top-level pages directly under `docs/` (other than the i18n fallback when required).
- **Top-level navigation**: presence and order of the seven standard sections (Home, Getting Started, Guides, References, ADRs when present, Project when `project/` exists, plus declared extension sections), `nav_translations` usage, omission of empty sections.
- **Plugin baseline**: `mkdocs-material`, `mkdocs-static-i18n` with `docs_structure: folder`, `pymdownx.superfences`, the built-in `search` plugin declared explicitly, `mkdocs-include-markdown-plugin`. For each: declared in `mkdocs.yml`? Pinned in the project's Python dep manifest?
- **Per-page structure**: every page in `docs/<lang>/` starts with a single `# H1` matching the nav label, declares `title` / `audience` / `content_mode` / `track` / `last_updated` frontmatter, audience values match IDs declared in the project's audience artifact, `content_mode` is one of the closed enumeration (`tutorial`, `how-to`, `reference`, `explanation`, `troubleshooting`, `glossary`, `meta`, or an explicitly opted-in extension value), `track` is one of `user-docs` / `developer-docs` (per `spec/project/docs-audience-tracks/`, which the `docs-audience-tracks-apply` skill audits in detail — this skill only verifies presence and enumeration validity).
- **Content modes (Diátaxis alignment)**: every page declares a `content_mode` value from the closed enumeration; surface candidate mode-mixing violations (a `how-to` page that embeds extended `explanation` paragraphs, a `reference` page with instructional recipes, a `tutorial` page padded with discursive `explanation` content) for Reviewer judgement — flag, don't auto-fail. For `troubleshooting` pages verify the canonical action vocabulary is used (`symptom` / `cause` / `workaround` / `resolution`).
- **Snippet inclusion (DRY)**: detect paragraphs longer than ~3 lines that appear verbatim on two or more pages (candidate DRY violations); never auto-rewrite—surface the candidate for user decision and route to the future `docs-dry-refactor` skill when it exists.
- **i18n and parity**: language-tree parity (delegates to the `docs-freshness-checker` agent for the deep check; the audit only reports presence of the parity-checking wiring in CI).
- **Build verification**: `mkdocs build --strict` runs cleanly in CI on every PR, `task docs` (or equivalent) invokes the same sequence locally.
- **Extension conformance**: per active extension spec, report whether the added sections, added plugins, and any relaxed baseline MUSTs are wired correctly.
- **Cap check**: total extension sections per repo ≤ 5 (per spec §Extension hooks).

Audit is read-only—never autofix during audit.

---

## 2. scaffold (greenfield: mkdocs.yml absent)

For each step below, confirm with the user per file before writing. Group-level "apply all in this group" is fine when the user asks for it.

- Create `mkdocs.yml` declaring:
  - `theme: name: material` (palette is per-repo; never picked here).
  - `plugins:` with `search`, `i18n` (using `docs_structure: folder` and one entry per configured language), `include-markdown`.
  - `markdown_extensions:` including `pymdownx.superfences` and the small set the Material theme needs to render reliably.
  - A minimal `nav:` listing the seven standard sections (Home, Getting Started, Guides, References, plus ADRs / Project / extension sections only when the corresponding content folder will be created in the same scaffold step).
  - `nav_translations` skeleton (one entry per configured language) when the language list contains more than one entry.
- Create `docs/<lang>/` per configured language with:
  - `index.md`: H1 matching the nav label, `title` / `audience` / `last_updated` frontmatter, one-paragraph landing copy plus jump-off links to the section index pages.
  - Per scaffolded section (`getting-started/`, `guides/`, `references/`, plus ADRs / Project / extension sections when the user opts in): an index page (`index.md` inside the folder) with the same per-page frontmatter contract; never invent page content beyond a placeholder paragraph naming the section's purpose. Page authoring is the `audience-doc-author` agent's job.
- Patch the project's Python dep manifest to pin every baseline plugin:
  - Detect the manifest kind: `pyproject.toml` (PEP 621 `[project.dependencies]` or a `[project.optional-dependencies] docs = [...]` extras group), `requirements.txt` / `docs/requirements.txt`, `uv.lock`, `poetry.lock`.
  - Propose the additions; never run `pip install` / `uv pip install` / `poetry add` from the skill. Report the exact install command appropriate to the detected manager so the user can run it.
- When `Taskfile.yml` exists and lacks a `docs` target, propose a wire-up: a `docs` target that invokes `mkdocs build --strict` (or the project's existing equivalent) so a local pass matches CI.
- When the active extension spec is `spec/claude/skill-agent-catalog/`, surface that the catalog generator wiring is owned by the separate `skill-agent-catalog-apply` skill and route the user there; never duplicate that wiring here.

---

## 3. patch (additive: mkdocs.yml present)

For each `missing` or `drift` finding from the audit, propose the exact change and ask the user to approve it before writing. Don't bundle unrelated changes into a single approval step.

- **Missing baseline plugin in `mkdocs.yml`**: append the plugin entry to the existing `plugins:` list at the position the spec implies; preserve every other plugin the repo already declares.
- **Missing baseline plugin in the dep manifest**: propose the pin in the project's existing dep-manifest shape; never silently change the dep-management strategy (don't move `requirements.txt` content into `pyproject.toml` extras or vice versa).
- **Missing section folder**: scaffold the folder under each `docs/<lang>/` tree with an index stub (same frontmatter contract as in `scaffold`); never author the prose body beyond a placeholder paragraph.
- **Missing or invalid per-page frontmatter**: propose the minimum addition (`title` derived from the H1, `audience` set to a placeholder ID with a `# TODO: replace with audience artifact ID` comment, `content_mode` proposed from a heuristic — first H2 with imperative verbs → `how-to`, first H2 names a configuration key / API endpoint → `reference`, narrative first paragraph → `explanation`, walking-through-steps-from-zero → `tutorial`, defaults to `# TODO: confirm content_mode` when ambiguous, `track` proposed from the `audience` value via the portfolio default map, `last_updated` set to today's date). When the audience artifact is missing, route the user to `audience-identify` rather than fabricating an audience ID. When the page mixes content modes (heuristic detected during audit), surface the candidate split rather than silently rewriting.
- **Custom nav order, extra plugin, or theme palette divergence from spec baseline**: surface the conflict, propose the resolution, and wait for user approval. Patch mode is additive, not destructive. The skill never silently overrides:
  - Theme palette, typography, or visual identity (per spec §Non-Goals).
  - A custom nav order the repo has explicitly chosen, when the order still satisfies the seven-section constraint.
  - An extra plugin the repo has added on top of the baseline (the cap rule applies to extension *sections*, not to plugins).
- **Extension-spec gap**: when an active extension spec declares an added section or added plugin and `mkdocs.yml` lacks it, propose the addition; cite the extension spec's MUST line in the proposal.

After every successful write, re-run `mkdocs build --strict` so the user sees the change verified end-to-end. A failing build stops the operation and surfaces the raw output verbatim; never claim success on a red build.
