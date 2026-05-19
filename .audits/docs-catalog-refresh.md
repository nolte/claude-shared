# Docs & Catalog Refresh — Audit Report

- Date: 2026-05-19
- Branch: `chore/docs-catalog-refresh`
- Repo root: `nolte/claude-shared`
- Audited revision: `f742fd2` (develop tip at worktree creation)
- Skills dispatched: `mkdocs-structure-apply` (audit), `docs-audience-tracks-apply` (audit), `skill-agent-catalog-apply` (audit), `docs-freshness-checker` (audit)
- Scope: full audit + decision to patch F1, F2, F3, F5 in this PR; F4 captured as proposal only.

## Findings

### F1 — `mkdocs-include-markdown-plugin` missing (critical)

`spec/project/mkdocs-structure/en.md` §Plugin baseline mandates the plugin in `mkdocs.yml` and pinned in the Python dep manifest. Neither is currently the case.

- `mkdocs.yml` plugins list: only `search`, `i18n`, `literate-nav`.
- `docs/requirements.txt`: no `mkdocs-include-markdown-plugin` entry.

Patch: add plugin to `mkdocs.yml` plugins block; add `mkdocs-include-markdown-plugin>=6.2` (current major) to `docs/requirements.txt`.

**Sub-finding F1a (proposed spec amendment)**: the plugin's default `opening_tag` / `closing_tag` (`{%` / `%}`) match verbatim occurrences of the directive inside skill-body prose (the `docs-dry-refactor` skill explicitly documents `{% include-markdown … %}` as the canonical form, and that prose is rendered into `docs/<lang>/skills/**` by the catalog generator). The patch pins custom tags (`{!` / `!}`) in `mkdocs.yml` so doc-examples don't trigger the directive. `spec/project/mkdocs-structure/` §Snippet inclusion (DRY) names `{%` / `%}` as canonical; the proposed amendment relaxes this to "the canonical form names `<opening-tag> include-markdown ... <closing-tag>` where the tags are pinned in `mkdocs.yml`". Track as a follow-up via the `spec` skill.

### F2 — 32 hand-authored pages lack per-page frontmatter (critical)

`spec/project/mkdocs-structure/en.md` §Per-page structure requires `title`, `audience`, `content_mode`, `last_updated`; `spec/project/docs-audience-tracks/en.md` §Per-page contract adds `track`. None of the hand-authored pages under `docs/de/` and `docs/en/` carry any frontmatter.

Files affected (32):

```
docs/<lang>/index.md
docs/<lang>/lifecycle.md
docs/<lang>/planning-suite.md
docs/<lang>/concepts/agents/index.md
docs/<lang>/concepts/skills/index.md
docs/<lang>/concepts/skills/skill-management.md
docs/<lang>/concepts/skills/spec.md
docs/<lang>/development/index.md
docs/<lang>/development/projektstruktur.md
docs/<lang>/development/beitragen.md
docs/<lang>/getting-started/index.md
docs/<lang>/getting-started/installation.md
docs/<lang>/getting-started/nutzung.md
docs/<lang>/specs/index.md
docs/<lang>/specs/skill-management.md
docs/<lang>/specs/agent-management.md
```

Default heuristic applied during patch (every page is part of the `developer-docs` track because the repo's audience artefact maps all contributor / operator / governing audiences to that track):

| Path | `audience` | `content_mode` | `track` |
| --- | --- | --- | --- |
| `index.md` (Home) | `contributor`, `user` | `meta` | `developer-docs` |
| `getting-started/index.md` | `contributor` | `meta` | `developer-docs` |
| `getting-started/installation.md` | `contributor`, `user` | `how-to` | `developer-docs` |
| `getting-started/nutzung.md` | `contributor`, `user` | `how-to` | `developer-docs` |
| `lifecycle.md` | `contributor` | `explanation` | `developer-docs` |
| `planning-suite.md` | `contributor` | `explanation` | `developer-docs` |
| `concepts/skills/index.md`, `concepts/agents/index.md` | `contributor` | `explanation` | `developer-docs` |
| `concepts/skills/skill-management.md`, `concepts/skills/spec.md` | `contributor` | `explanation` | `developer-docs` |
| `specs/index.md` | `contributor` | `meta` | `developer-docs` |
| `specs/skill-management.md`, `specs/agent-management.md` | `contributor` | `reference` | `developer-docs` |
| `development/index.md` | `contributor` | `meta` | `developer-docs` |
| `development/projektstruktur.md` | `contributor` | `reference` | `developer-docs` |
| `development/beitragen.md` | `contributor` | `how-to` | `developer-docs` |

`last_updated: 2026-05-19` portfolio-wide for this batch.

### F3 — `AUDIENCES.md` missing per-entry IDs and `track:` mapping (critical)

`spec/project/audience-identification/en.md` §Requirements lists `track` as a per-audience MUST since the docs-audience-tracks spec landed. `spec/project/docs-audience-tracks/en.md` §Audience-to-track mapping carries the portfolio default mapping (`user` → `user-docs`; `contributor` / `operator` / `release-manager` → `developer-docs`).

The current `AUDIENCES.md` uses prose-only labels with no canonical kebab-case IDs, so `audience:` frontmatter values in F2 have no anchor to point at. The patch introduces short stable IDs alongside the existing prose labels and records the track-mapping inline:

| Existing label | New ID | Track |
| --- | --- | --- |
| Downstream Claude Code users in portfolio projects | `downstream-user` | `user-docs` |
| Plugin author dogfooding inside this repo | `dogfooding-author` | `developer-docs` |
| GitHub Actions CI for this repo | `ci-operator` | `developer-docs` |
| Repo maintainer (nolte) | `maintainer` | `developer-docs` |
| Claude Code itself as co-author | `claude-coauthor` | `developer-docs` |
| External contributors via pull request | `external-contributor` | `developer-docs` |
| Portfolio-consistency anchors (gh-plumbing/vale-style/taskfiles) | `portfolio-anchor` | `developer-docs` |
| End users of downstream projects | `downstream-end-user` | `user-docs` |
| Other Nolte portfolio repos as passive consumers | `portfolio-peer` | `developer-docs` |

Per-page `audience:` frontmatter values in F2 reference these IDs (with the additional convenience aliases `contributor` ≔ `maintainer`, `user` ≔ `downstream-end-user`).

### F4 — Top-level nav drift (critical) — captured as proposal only

`spec/project/mkdocs-structure/en.md` §Top-level navigation defines the seven canonical sections (Home, Getting Started, Guides, References, ADRs, Project, plus declared extension sections). The repo's `mkdocs.yml` carries ten:

| Current nav | Standard? | Proposed disposition |
| --- | --- | --- |
| Startseite (Home) | ✓ Home | keep |
| Erste Schritte (Getting Started) | ✓ Getting Started | keep |
| Skills | ✓ Extension (skill-agent-catalog) | keep |
| Agents | ✓ Extension (skill-agent-catalog) | keep |
| Tags | ✗ extra | move under **References** as `references/tags.md` (it is the catalog's tag index) |
| Konzepte | ✗ extra | merge into a new **Guides** section (`how-to` and `explanation` pages); `concepts/agents/index.md` and `concepts/skills/index.md` become per-topic guides |
| Spezifikationen | ✗ extra | move under **References** (skill-management.md, agent-management.md are reference content) |
| Planning-Suite | ✗ extra | move under a new **Project** section (planning artefacts: mission, goals, roadmap, sprints, features) |
| Entwicklungszyklus (`lifecycle.md`) | ✗ extra | move under **Guides** as `guides/development-lifecycle.md` (it is the developer-docs explanation) |
| Entwicklung | ✗ extra | move under **Guides** (`development/projektstruktur.md`, `development/beitragen.md`) |

Resulting nav (proposal):

1. Home
2. Getting Started
3. Guides (was Konzepte + Entwicklung + Entwicklungszyklus)
4. References (was Spezifikationen + Tags)
5. Project (was Planning-Suite)
6. Skills (extension)
7. Agents (extension)

Total: 5 standard + 2 extension = 7, within cap. The proposal is **not** applied in this PR; it requires a follow-up PR that also relocates the corresponding `docs/<lang>/<section>/` folders and updates every cross-link. Tracking suggestion: open a follow-up issue tagged with the same audit ID.

### F5 — Generated catalog pages emit no frontmatter (warning)

`scripts/docs/gen_catalog.py` writes per-artifact catalog pages, section index pages, and the tag index without a YAML frontmatter block. `spec/project/mkdocs-structure/en.md` §Per-page structure is explicit that the per-page MUST set (`title`, `audience`, `content_mode`, `last_updated`) applies to every page under `docs/<lang>/`; the docs-audience-tracks spec adds `track`. The closed enumeration permits `last_updated: generated` for catalog-emitted pages.

Patch: extend `gen_catalog.py` to emit a frontmatter block on every page it writes — index pages as `content_mode: meta`, detail pages as `content_mode: reference`, the tag index as `content_mode: meta`. Track is fixed `developer-docs` (per the skill-agent-catalog spec's Open Question that the per-spec default minimises drift). Audience defaults to `contributor`; the source artefact's frontmatter `audience` value, when present, is propagated to the catalog page.

## Pass-class findings

- DE/EN file parity: identical `find . -type f -name '*.md'` set across both language trees (no `language-parity gap` per `spec/project/docs-freshness/`).
- Catalog generation: spec-compliant (pre-build form, `mkdocs-literate-nav` declared, generated tree committed under `docs/<lang>/skills/`, `docs/<lang>/agents/`, CI freshness check `Verify committed catalog is fresh` in `ci.yml`, pre-commit hook `docs-catalog-fresh`, phase-grouping per the closed eight-value vocabulary).
- ADR drift: `docs/<lang>/adr/` does not exist; entire ADR category is out of scope per `spec/project/docs-freshness/`.
- Internal link rot: only false positives (regex examples and `<slug>` placeholders inside skill body prose, which the catalog faithfully renders verbatim per the skill-agent-catalog spec).
- Stale markers: hits are all inside skill bodies as legitimate examples (`# TODO` markers in `readme-structure-apply`, `mkdocs-structure-apply`); none in author-prose surfaces.
- Mermaid `diagram-source: derived` drift: no `derived` markers in scope (every diagram in scope is `user-described`).

## Side-effects applied alongside the patch

- `.markdownlint.yaml`: added repo-wide config that pins `MD025.front_matter_title: ""` so the per-page MUST set (frontmatter `title:` + body `# H1`) doesn't trip the single-title rule. Captures a tweak that wasn't possible to express through the existing `--disable` list in `.pre-commit-config.yaml`.
- `skills/sprint-plan/SKILL.md`: the sprint-file template code-fence language switched from `markdown` to `text` and the placeholder feature links wrapped in backticks. MkDocs' link-validation regex doesn't honour fenced-code-block scope, so placeholder Markdown-link syntax inside the catalog-rendered fence triggered `unrecognized link` warnings under `--strict`; the wrapping defuses that without changing the template's authoring intent.
- `docs/<lang>/index.md` title and H1: aligned to the nav label (`Startseite` / `Home`) instead of the repo identifier `claude-shared`. The repo-identifier form tripped `Vale.Terms` whenever the page declared frontmatter (Vale's tokenizer flips into a stricter mode when `title:` is present, and `Vale.Terms = NO` toggles don't override the built-in rule). The aligned form also satisfies the spec's §Per-page transitivity rule (`title` matches H1, H1 matches nav label).

## Caller follow-ups (after this PR merges)

- Open a follow-up issue for the F4 nav restructuring (proposal in §F4); the move is mechanical but touches every section folder and every cross-link.
- Author a spec amendment via `/nolte-shared:spec` to relax `mkdocs-structure/` §Snippet inclusion (DRY) so the include-markdown opening / closing tags are pinned per-repo (F1a in this audit). Until then, this repo carries the custom-tag pin in `mkdocs.yml`.
- Once F2 lands, dispatch `audience-doc-author` for any page whose `# TODO` audience refinement is desired.
- Re-run `docs-freshness-checker` quarterly per the spec's §Triggers and cadence.
