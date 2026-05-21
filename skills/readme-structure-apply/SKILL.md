---
name: readme-structure-apply
description: "Audits the repository's `README.md` against the canonical-language file under spec/project/readme-structure/ and, with per-item user approval, scaffolds or patches the file: H1 + tagline, CI badges, six required sections in order (Purpose, Usage, Structure, Related repositories, Status, License), the consumer-first ordering rule, the ≤200-line length budget, and link rules. Three operations: `audit` (read-only conformance report), `scaffold` (greenfield), `patch` (additive fix). Invoke when the user asks to apply, audit, scaffold, or patch the README against the spec; also handles equivalent German-language requests. Don't use for docs/ page content (`audience-doc-author`), MkDocs nav (`mkdocs-structure-apply`), Vale prose linting (`prose-vale-curator`), or the audience artefact (`audience-identify`)."
tags: [scaffolding, audit]
phase: design
---

# README Structure Apply

Operationalises `spec/project/readme-structure/<canonical_language>.md` inside the current repository. The skill audits the repository-root `README.md` against the spec's section skeleton, the consumer-first ordering rule, and the length / link / language requirements; with explicit per-item user consent it scaffolds a fresh README or patches a single finding at a time on an existing one.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path). Never invent requirements that don't appear in the spec.

## Why this is a skill, not an agent

Per `spec/claude/skill-vs-agent/` §Decision dimensions, this capability is a skill because:

- **Mid-flow user approval is the contract.** Every section addition, badge change, and tagline rewrite is written only with explicit per-change confirmation; the README is the repository's most visible artefact and the user's voice in it matters.
- **Persistent on-disk output that flows back into the main conversation.** The audit table, the per-section proposals, and the post-edit Vale check (delegated to `prose-vale-curator`) all surface in the conversation so the user can decide.
- **Orchestrator pattern.** The skill dispatches `audience-doc-author` for the tagline / Purpose / Usage prose authoring once the section containers exist, dispatches `prose-vale-curator` to Vale-check the result, and routes to `audience-identify` when the README needs an `## Audiences` section but the audience artefact doesn't exist yet; per `spec/claude/skill-vs-agent/` §Hybrid pattern, the orchestrator is always a skill.
- **Precedent.** Follows the same audit + scaffold + patch shape as `mkdocs-structure-apply`, `project-structure-apply`, `docs-audience-tracks-apply`; portfolio-wide consistency favours the same artefact type.
- **Counter-dimension considered.** A narrower agent could specialise on README authoring as a bounded one-shot, but the load-bearing dimension here is the per-section approval dialogue, not the prose authoring (which is delegated); skill wins.

## User-language policy

Detect the user's language from their message and respond in it. The README itself is English-only per `spec/project/readme-structure/` §File and language ("MUST be written in English, regardless of the primary working language of the maintainers"); never produce a `README.de.md` or similar. Multilingual content lives under `docs/<lang>/`.

## Tool selection rationale

Declared tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`.

- `Read` / `Glob` / `Grep` for repository inspection (`README.md`, `.github/workflows/`, `LICENSE`, `pyproject.toml` / `package.json` for proper-noun discovery, neighbouring portfolio repos for the related-repositories section).
- `Write` for scaffold (a fresh `README.md` doesn't exist yet) and `Edit` for patch (a section is added or fixed in an existing README).
- `Bash` is necessary for two read-only checks: counting README lines (the spec sets a ~200-line budget) and verifying CI badge URLs resolve to actual workflow files in `.github/workflows/`. No destructive bash.
- No `WebFetch` / `WebSearch`: the spec is the only source of truth; primary-proper-noun links (Claude Code, Home Assistant, Vale) come from the user or are surfaced as `# TODO` markers rather than auto-fetched.

## Preconditions

Before doing anything:

1. Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
2. Locate `spec/project/readme-structure/<canonical_language>.md` — either in the target repo or via the `nolte-shared` plugin. If neither is reachable, stop and ask the user which spec source to use.
3. Detect the operation:
   - `README.md` absent at repo root → `scaffold` (default).
   - `README.md` present → `patch` (or `audit` when the user explicitly asks for a read-only check).
4. Detect the repository type (Claude Code plugin, GitHub workflow package, Home Assistant integration, Vale style package, Python service, CLI, library) by scanning for marker files: `.claude-plugin/plugin.json`, `.github/workflows/_*.yml` (callable workflows), `custom_components/`, `styles/`, `pyproject.toml`, `package.json`. The type informs the `## Structure` section's content but doesn't change the section skeleton itself.
5. Check for uncommitted changes in `README.md`. If the file is dirty, report and ask whether to stash, commit, or abort — never overwrite uncommitted work.

## Operations

### 1. `audit` (read-only)

Walk through the spec's Acceptance Criteria one item at a time, classify each finding as `pass`, `missing`, or `drift`. Group findings by spec area:

- **File and language**: `README.md` at repo root, English-only, passes Vale (delegate the Vale check to `prose-vale-curator` rather than running Vale here — surface the count, not the alerts).
- **Header block**: single `# <repo-name>` H1 matching the GitHub repo name, CI badges under the H1 for every merge-gating workflow, one-to-three-sentence tagline naming what the repo is and who it's for (no marketing language), primary proper nouns linked on first mention, tagline ≤ 280 characters.
- **Required sections**: `## Purpose`, `## Usage` (or `## Installation` or `## Getting started`), `## Structure` (when layout non-obvious), `## Related repositories` (when peers exist), `## Status`, `## License` (when `LICENSE` ships). Verify presence and order; report sections in wrong order as `drift`.
- **Consumer-first ordering**: consumer-facing sections (`Purpose`, `Usage`) precede contributor sections (`Structure`, `Status`, `License`); dogfooding instructions live as `###` sub-sections of `## Usage`, never as top-level sections.
- **Links and badges**: `LICENSE` linked via relative path; cross-repo links use absolute `https://github.com/<org>/<repo>` URLs; CI badges point at the same repo's workflows, not copied-over from elsewhere.
- **Length and density**: total ≤ ~200 lines excluding code blocks; report a hard fail at >250 lines; short paragraphs and lists preferred over prose blocks.

Audit is read-only — never autofix during audit.

### 2. `scaffold` (greenfield: `README.md` absent)

For each step below, confirm with the user per section before writing.

- Create `README.md` at repo root with the following structure:
  - `# <repo-name>` H1 — derived from the directory name or the `name:` field of `.claude-plugin/plugin.json` / `pyproject.toml` / `package.json`.
  - CI badge block under the H1 — one badge per workflow under `.github/workflows/` that gates merges to `develop` (detected via `if: github.ref == 'refs/heads/develop'` or `branches: [develop]`). One badge per line.
  - Tagline — propose a single one-sentence stub with two `# TODO` markers: the deliverable shape and the intended consumer audience. The audience marker routes to `audience-identify` when the artefact exists, otherwise to the user.
  - `## Purpose` — empty body with a placeholder paragraph ("Replace this with two to six bullets describing the problem this repository solves."); dispatch `audience-doc-author` for the body authoring as a follow-up.
  - `## Usage` (default) or `## Installation` / `## Getting started` (when the repository type suggests one of the alternatives) — empty body with a placeholder pointing at the chosen install path, plus a `### Local development` sub-section stub when the repo carries a `Taskfile.yml`.
  - `## Structure` (only when the repo layout is non-obvious — Claude Code plugins, multi-component monorepos, HA integrations) — empty `tree`-style placeholder with `# TODO` markers for the per-entry comments.
  - `## Related repositories` (only when neighbouring portfolio repos exist) — empty bullet list with `# TODO` markers for peer-link + description.
  - `## Status` — single-line placeholder ("Early stage." or similar) with a `# TODO` marker.
  - `## License` — `[<SPDX identifier>](LICENSE)` link plus copyright holder line, both derived from the `LICENSE` file's first few lines.
- After scaffolding, route the user to `audience-doc-author` for the Purpose / Usage / Structure body authoring and to `prose-vale-curator` for the final Vale check.

### 3. `patch` (additive: `README.md` present)

For each `missing` or `drift` finding from a prior audit, propose the exact change and ask the user to approve it before writing. Don't bundle unrelated changes into a single approval step.

- **Missing required section**: propose the section header with a placeholder body and a `# TODO` marker for the prose; route the user to `audience-doc-author` for the body.
- **Required sections in wrong order**: propose the reorder as a single edit; show the before / after section sequence inline.
- **H1 doesn't match repo name**: propose the fix; verify against the GitHub repository name via the local `.git/config` `remote.origin.url`.
- **Missing or stale CI badge**: propose the badge addition / removal; the badge must point at `github.com/<org>/<repo>/actions/workflows/<file>.yml` and the workflow file must exist in `.github/workflows/`.
- **`LICENSE` linked via absolute URL**: propose the relative-link replacement.
- **Tagline > 280 characters or contains marketing language**: surface the violation and propose a short rewrite; the user approves the wording.
- **Total length > ~200 lines**: surface which sections exceed; propose moving sub-content into `docs/` and route the user to `mkdocs-structure-apply` or `audience-doc-author` as appropriate.
- **Dogfooding section at top-level**: propose moving it into `## Usage` as a `### Local development` sub-section.

After every successful write, route the user to `prose-vale-curator` for the post-edit Vale check; never claim "Vale-clean" without dispatching the curator.

## Output contract

The skill returns to the user, in this order:

1. **Operation + target**: which operation ran (`audit` / `scaffold` / `patch`), absolute path to the target `README.md`, detected repository type.
2. **Pre-state**: brief summary of what was found (README present? line count? badge count? sections present and in what order?).
3. **Audit findings** (always): grouped per spec area, with one row per Acceptance-Criteria item showing status (`pass` / `missing` / `drift`) and a one-line evidence snippet.
4. **Planned edits** (for `scaffold` / `patch`): list of changes, one line per change, with rationale linking back to the spec line.
5. **Approval gate** (for `scaffold` / `patch`): explicit user-decision point; nothing is written until the user confirms.
6. **Applied edits** (after approval): the absolute path of the written file, plus a per-section diff summary.
7. **Caller follow-ups**: explicit list — dispatch `audience-doc-author` to fill in `# TODO` body markers, dispatch `prose-vale-curator` to Vale-check the result, route to `audience-identify` if the README needs an audience reference but the artefact doesn't exist, commit the edits, open the PR via `pull-request-create`.

## Gotchas

- **Patch operations must preserve all existing frontmatter and prose**: when adding a missing section or reordering sections in an existing `README.md`, every other section's content must be carried over verbatim — a patch that truncates or omits existing prose is a data-loss bug, not a style issue.
- **Uncommitted README changes block the operation**: if `README.md` has unstaged or staged-but-uncommitted changes when the skill starts, it stops and asks the user to stash, commit, or abort — never overwrite a dirty file; confirm the precondition check runs before any `Write` or `Edit`.
- **CI badge URLs must resolve to actual workflow files**: the skill verifies badge URLs against `.github/workflows/`; a badge pointing at a renamed or deleted workflow silently becomes a broken badge in the rendered README — always re-check workflow file existence after any badge addition.

## Hard rules

1. **Never** author body prose beyond a single placeholder paragraph plus `# TODO` markers. Body authoring is delegated to `audience-doc-author`.
2. **Never** produce a non-English `README.md` (no `README.de.md`, no inline German prose). The spec's §File and language MUST is hard.
3. **Never** silently break the consumer-first ordering rule. When a patch would move a contributor section above a consumer section, stop and explain.
4. **Never** auto-publish or auto-fetch a primary-proper-noun link (Claude Code, Home Assistant, Vale, …). Surface the link as a `# TODO` marker and ask the user to provide the canonical upstream URL.
5. **Always** read the spec at runtime: prefer the target repo's `spec/project/readme-structure/<canonical_language>.md`; fall back to the copy shipped by the `nolte-shared` plugin only when the target repo lacks one.
6. **Always** delegate the Vale check to `prose-vale-curator` after a scaffold or patch; never claim "Vale-clean" without dispatching the curator.

## Sources

- `spec/project/readme-structure/` — the canonical authoritative spec this skill operationalises
- `spec/project/prose-style/` — the Vale rule set the resulting README must pass; this skill delegates the actual check to `prose-vale-curator`
- `spec/project/audience-identification/` — the audience artefact the README references for "intended consumers"
- `spec/claude/skill-vs-agent/` — the skill-vs-agent decision dimensions that justify this artefact as a skill, not an agent
