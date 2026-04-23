# Repository README Structure

Status: draft

## Context
Every repository in this portfolio ships a top-level `README.md`: mandated by the `project-structure` spec—but the internal shape of that file has drifted across repositories. Consumers (humans and AI agents) scan READMEs for the same things in the same order: *what's this, why does it exist, how do I use it, how does it fit into the portfolio*. When the section set and ordering differ per repository, downstream tooling (plugin marketplaces, package indexes, AI agents that synthesize summaries) and human readers both pay the cost.

The reference implementation is this repository's own `README.md`. It targets diverse software elements—Claude Code plugins, reusable GitHub workflow packages, Home Assistant integrations, Vale style packages, Python services—all hosted on GitHub, all discoverable through the same portfolio entry points. This spec lifts that shape into a portfolio-wide contract so new repositories and refactors can produce structurally identical READMEs without case-by-case negotiation.

## Goals
- A reader (human or AI) can locate intent, install command, and portfolio context within the first screen of every repository's README
- Repositories of different types (plugin, library, service, integration, CLI, style package) share one recognizable section skeleton
- README metadata (badges, links to docs, portfolio peers) stays consistent enough that automated audits can flag drift
- Consumer-facing information comes before internal/contributor information
- The structure composes cleanly with the `project-structure`, `branching-model`, and `prose-style` specs rather than duplicating them

## Non-Goals
- Project-specific narrative content (feature list, domain explanations, tutorials)
- Full documentation site structure—that lives under `docs/` and is governed by MkDocs configuration, not the README
- Architecture decision records, design documents, or changelogs—separate artifacts
- Contributor-only runbooks—those belong in `CLAUDE.md` or `docs/`
- Badge catalog beyond the CI status convention (shields for licenses, downloads, etc. are optional and not prescribed here)
- Translations of the README itself—the README is English-only for portfolio consistency; multilingual content lives under `docs/<lang>/`
- Machine-readable README front-matter (YAML header blocks): `.github/settings.yml`, mandated by the `project-structure` spec, is the canonical source for repository metadata (description, homepage, topics)
- A dedicated "Support" or "Contact" section—the GitHub repository URL (issues tab, discussions tab) is the implicit and sufficient support channel for every portfolio repository

## Requirements

### File and language
- **MUST** live as `README.md` at the repository root
- **MUST** be written in English, regardless of the primary working language of the maintainers, so portfolio-wide tooling and external consumers see one consistent voice
- **MUST** follow the rules of the `prose-style` spec (Vale, Microsoft + RedHat styles, `nolte/vale-style` vocabularies)

### Header block (above the first `##` heading)
- **MUST** start with a single top-level heading (`# <repo-name>`) that matches the GitHub repository name exactly
- **MUST** render CI status badges for every workflow that gates merges on the default branch, placed immediately under the `H1`, one badge per line or grouped on a single line
- **MUST** include a one- to three-sentence tagline under the badges that states *what this repository is* and *who it's for*, without marketing language
- **SHOULD** keep the tagline at or under 280 characters (excluding markdown link syntax) so it can double as a social-card description and as the `description` field in `.github/settings.yml`
- **SHOULD** link primary proper nouns in the tagline (for example "Claude Code," "Home Assistant," "Vale") to their canonical upstream documentation on first mention
- **MAY** include non-CI badges (license, latest release, package index) when they materially help a consumer decide whether to use the repository

### Required sections (in this order)
The following `##` headings **MUST** appear, in the order given, whenever the underlying content applies to the repository type. A section **MUST** be omitted only when it has no meaningful content for that repository type; it **MUST NOT** be reordered for stylistic reasons.

1. **`## Purpose`**: **MUST** appear. Explains the problem the repository solves and who the intended consumers are. Two to six bullet points or a short paragraph. No feature dump.
2. **`## Usage`** (or `## Installation`, or `## Getting started`: pick one and stay with it): **MUST** appear. Shows the shortest path from zero to a working consumer experience. **MUST** include at least one runnable code block (shell, config snippet, or import example). **SHOULD** split into subsections (`###`) when the repository supports multiple install or consumption modes (for example downstream install vs. local development vs. dogfooding).
3. **`## Structure`**: **SHOULD** appear for repositories whose layout is non-obvious to a first-time reader (plugins with `.claude-plugin/` + `skills/`, multi-component monorepos, HA integrations). Shows a pruned `tree`-style listing with one-line comments per entry, not an exhaustive file tree.
4. **`## Related repositories`**: **SHOULD** appear when the repository depends on, extends, or is depended on by other repositories in the nolte portfolio (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`, `nolte/claude-shared`, and similar). Each entry is a bulleted link followed by a one-line description of the peer's role.
5. **`## Status`**: **SHOULD** appear. One short paragraph describing lifecycle state (early stage, stable, maintenance-only, archived). Complements but doesn't duplicate GitHub's repository metadata.
6. **`## License`**: **MUST** appear for any repository that ships a `LICENSE` file. Links to the `LICENSE` file and names the SPDX identifier and copyright holder.

### Optional sections
- **MAY** include a `## Features` section between `## Purpose` and `## Usage` when the feature list is load-bearing for consumer decisions (for example CLIs with many commands, plugins exposing multiple skills, integrations with a large supported-device matrix); when features fit into two or three bullets, they **SHOULD** stay inside `## Purpose` instead of getting their own section
- **MAY** include a `## Documentation` section pointing to the published MkDocs site when `docs/` is more than a handful of pages; for smaller `docs/` folders, link from within `## Usage` instead
- **MAY** include a `## Contributing` section pointing to `CONTRIBUTING.md` or to the portfolio-wide contribution conventions; **MUST NOT** duplicate contributor content that belongs in `CLAUDE.md`
- **MAY** include a `## Notes` or `## Caveats` subsection inside `## Usage` for non-obvious gotchas, when a separate top-level section would be overkill
- **MAY** include a `## Security` section when the repository has its own disclosure policy distinct from the portfolio default

### Consumer-first ordering rule
- Information that a consumer needs to evaluate or install the repository (`Purpose`, `Usage`) **MUST** appear before information that a contributor or maintainer needs (`Structure`, `Status`, `License`)
- Dogfooding / local-development instructions **MUST** live inside `## Usage` as a subsection (typical heading: `### Work on the plugin itself (dogfooding)` or `### Local development`), never as a top-level section that displaces consumer guidance

### Links, badges, and references
- **MUST** reference the `LICENSE` file using a relative link (`[MIT](LICENSE)`), not an absolute GitHub URL
- **MUST** use absolute `https://github.com/<org>/<repo>` URLs when linking to other portfolio repositories, so the README is correct when rendered outside github.com (package registries, plugin marketplaces, printed PDFs)
- **MUST** keep every CI status badge pointing at the same repository's `Actions` workflow runs; copied-over badges from another repository are drift
- **SHOULD** use the `github.com/<org>/<repo>/actions/workflows/<file>.yml` badge form, matching the badges already present in the reference README

### Length and density
- **SHOULD** keep the entire README under roughly 200 lines; overflow belongs in `docs/` or `CLAUDE.md`
- **SHOULD** favor short paragraphs and lists over prose blocks; the README is a lookup surface, not a manual

## Acceptance Criteria
- [ ] `README.md` exists at the repository root and is written in English
- [ ] The file starts with a single `# <repo-name>` heading matching the GitHub repository name exactly
- [ ] CI status badges for merge-gating workflows appear under the H1
- [ ] A one- to three-sentence tagline follows the badges, with primary proper nouns linked on first mention
- [ ] `## Purpose` is present and contains no feature dump
- [ ] `## Usage` (or the chosen equivalent: `## Installation` or `## Getting started`) is present and contains at least one runnable code block
- [ ] Multi-mode consumption is split into `###` subsections under `## Usage`
- [ ] `## Structure` is present whenever the repository has a non-trivial layout and shows a pruned tree with per-entry comments
- [ ] `## Related repositories` is present whenever portfolio peers exist and each entry is a link plus one-line description
- [ ] `## Status` is present and describes lifecycle state in a short paragraph
- [ ] `## License` links to the root `LICENSE` file via a relative link and names the SPDX identifier and copyright holder
- [ ] Required sections appear in the order: `Purpose` → `Usage` → `Structure` → `Related repositories` → `Status` → `License`
- [ ] Consumer-oriented content (`Purpose`, `Usage`) precedes contributor-oriented content (`Structure`, `Status`, `License`)
- [ ] Dogfooding or local-development instructions live as a `###` subsection of `## Usage`, not as a top-level section
- [ ] Cross-repository links use absolute `https://github.com/<org>/<repo>` URLs
- [ ] The README passes the Vale configuration that implements the `prose-style` spec
- [ ] Total README length is at most around 200 lines, excluding code blocks

## Open Questions
- Should repositories that ship an end-user artifact (HACS integrations, CLIs with binary releases) additionally require a `## Installation` section split from `## Usage`, or does a single `## Usage` with `###` subsections cover both cases adequately?
- How should this spec treat repositories that intentionally have no consumers beyond the maintainer (personal dotfiles, experiments): are they exempt, or do they still follow the skeleton and simply omit sections that have no meaningful content?
