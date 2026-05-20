---
name: mkdocs-structure-apply
description: "Audits a repository against the canonical-language file under spec/project/mkdocs-structure/ and, with per-item user approval, scaffolds or patches the MkDocs skeleton: the per-language docs/ tree, seven standard nav sections, plugin baseline (incl. mkdocs-include-markdown-plugin), pinned dep manifest, per-page frontmatter contract. Three operations: `audit` (read-only conformance report), `scaffold` (greenfield), `patch` (additive fixes). Invoke when the user asks to apply, audit, scaffold, or patch MkDocs against the spec; also handles equivalent German-language requests. Don't use for theme/typography decisions (per-repo), page-content authoring (use `audience-doc-author`), DRY refactoring (use `docs-dry-refactor` when present), drift detection (use `docs-freshness-checker`), or catalog generator wiring (use `skill-agent-catalog-apply`; this skill only verifies the catalog extension's MUSTs at the baseline level)."
tags: [scaffolding, audit]
phase: design
---

# MkDocs Structure Apply

Operationalises `spec/project/mkdocs-structure/<canonical_language>.md` inside the current repository. The skill audits the current MkDocs wiring against the baseline plus every active project-type-specific extension spec, proposes the concrete file-level changes the spec requires, and—with explicit per-item user consent—applies them.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path). Never invent requirements that don't appear in the spec.

## Rationale (why a skill, not an agent)

Per `spec/claude/skill-vs-agent/` §Decision dimensions, this capability is a skill because:

- **Mid-flow user approval is the contract.** Every scaffold or patch decision (mkdocs.yml plugin additions, docs/<lang>/ section folders, dep-manifest pins, Taskfile wiring) is written only with explicit per-change confirmation; the audit is read-only and the apply step is a sequence of approvals an agent's fire-and-forget shape can't carry.
- **Persistent on-disk output that flows back into the main conversation.** The audit table, the per-item proposals, and the build-verification output all surface in the conversation so the user can decide; isolating them in a structured-report boundary would obscure the per-file approval surface.
- **Orchestrator pattern.** The skill can later dispatch the `audience-doc-author` agent for page-content authoring or a future `docs-dry-refactor` skill for DRY refactoring; per `spec/claude/skill-vs-agent/` §Hybrid pattern, the orchestrator is always a skill.
- **Precedent.** Follows the same audit + scaffold + patch shape as `project-structure-apply` and `skill-agent-catalog-apply`; portfolio-wide consistency (`spec/claude/skill-vs-agent/` §Portfolio-wide consistency) favours the same artifact type.
- **Counter-dimension considered.** A narrower agent could specialise on mkdocs.yml-patch generation and gain on context-window protection, but the high-impact part is the per-item approval dialogue and the build-verification loop, not the boilerplate generation; skill wins.

## User-language policy

Detect the user's language from their message and respond in it. Generated file contents (`mkdocs.yml`, `docs/<lang>/index.md`, section index stubs, dep-manifest patches, `Taskfile.yml` targets) are always written in English so portfolio-wide automation stays predictable. Comments inside generated files are English as well.

## Tool selection rationale

Declared tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`.

- `Read` / `Glob` / `Grep` for repository inspection (mkdocs.yml, docs/<lang>/ trees, dep manifests, page frontmatter, active extension-spec markers).
- `Write` / `Edit` for scaffold and patch operations on `mkdocs.yml`, docs trees, and dep manifests; never overwriting existing config wholesale.
- `Bash` is necessary for `mkdocs build --strict` verification, `task docs` local invocation, and detecting the project's package manager (`pyproject.toml` shape, `uv.lock` / `poetry.lock` / `requirements*.txt` presence). The skill never runs destructive bash (`git push`, `gh pr create`, `pip install`, `rm -rf`).
- No `WebFetch` / `WebSearch`: the spec is the only source of truth; baseline plugin pins are read from the project's existing dep manifest, never from the network.

## Preconditions

Before doing anything:

1. Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
2. Locate `spec/project/mkdocs-structure/<canonical_language>.md`—either in the target repo or via the `nolte-shared` plugin. If neither is reachable, stop and ask the user which spec source to use (matches the spec's §Extension hooks §"Project-type discovery" fallback pattern).
3. Determine the operation:
   - If `mkdocs.yml` is absent → `scaffold` (default).
   - If `mkdocs.yml` is present → `patch` (or `audit` when the user explicitly asks for a read-only conformance check).
4. Detect active extension specs by scanning marker files at the repo root: `.claude-plugin/plugin.json` activates `spec/claude/skill-agent-catalog/`; `cookiecutter.json` plus `{{cookiecutter.project_slug}}/` activates a future cookiecutter-template-docs spec; and so on. Read every active extension spec at runtime; compose its MUSTs additively with the baseline (per the spec's §Extension hooks rule "every active extension's MUSTs are additive to the baseline MUSTs").
5. Resolve the language list from `spec/.spec-config.yml` `languages`. If that file is absent, ask the user which languages the docs should ship in; default to a single `en` only after explicit confirmation.
6. Check for uncommitted changes in `mkdocs.yml`, `docs/`, the dep manifest, and `Taskfile.yml`. If the tree is dirty there, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

## Operations

Read `references/operations.md` when executing any of the operations below in detail.

### 1. `audit` (read-only)

Walk the spec's Acceptance Criteria and every active extension spec's MUSTs; classify each finding as `pass`, `missing`, or `drift` grouped by spec area (Site layout, Top-level navigation, Plugin baseline, Per-page structure, Content modes, Snippet inclusion, i18n parity, Build verification, Extension conformance, Cap check). Audit is read-only—never autofix.

### 2. `scaffold` (greenfield: `mkdocs.yml` absent)

Create `mkdocs.yml` with Material theme, baseline plugins (`search`, `i18n`, `include-markdown`), seven standard nav sections, and `nav_translations` skeleton; scaffold `docs/<lang>/` trees with per-page frontmatter stubs across all configured languages; propose dep-manifest pins and Taskfile `docs` target. Confirm per file before writing.

### 3. `patch` (additive: `mkdocs.yml` present)

For each `missing` or `drift` finding, propose the minimal fix and ask for per-item approval before writing. Patch mode is additive, never destructive. Re-run `mkdocs build --strict` after every successful write.

## Output contract

The skill returns to the user, in this order:

1. **Operation + target**: which operation ran (`audit` / `scaffold` / `patch`), absolute target repo root, detected language list, detected active extension specs.
2. **Pre-state**: brief summary of what was found (`mkdocs.yml` present? per-language trees present? plugin baseline pinned? audience artifact present?).
3. **Audit findings** (always): grouped per spec area (Site layout, Top-level navigation, Plugin baseline, Per-page structure, Snippet inclusion (DRY), i18n and parity, Build verification, Extension conformance), with one row per Acceptance-Criteria item showing status (`pass` / `missing` / `drift`) and a one-line evidence snippet.
4. **Planned edits** (for `scaffold` / `patch`): list of files to create or modify, one line per file, with rationale linking back to the spec line.
5. **Approval gate** (for `scaffold` / `patch`): explicit user-decision point; nothing is written until the user confirms.
6. **Applied edits** (after approval): list of files actually written, with absolute paths.
7. **Build verification**: `mkdocs build --strict` exit code plus a raw output snippet on failure; on success report the build summary line only.
8. **Caller follow-ups**: explicit list — commit the working-tree edits, run the proposed `pip install` / `uv pip install` / `poetry add` command to install the new baseline plugins, dispatch `audience-doc-author` to fill in the page content stubs, route to `skill-agent-catalog-apply` when the catalog extension is active and not yet wired, open the PR via `pull-request-create`, and similar.

## Hard rules

1. **Never** modify theme palette, typography, or visual identity. These are per-repo decisions per `spec/project/mkdocs-structure/` §Non-Goals. The skill mandates `mkdocs-material` as the engine but never picks the colour scheme.
2. **Never** author markdown page content. The skill creates the *containers* (section folders, index pages with frontmatter, H1, and placeholder paragraph), but never the prose body. Page-content authoring belongs to the `audience-doc-author` agent or to the human author.
3. **Never** silently override existing `mkdocs.yml` decisions. When an existing config diverges from the spec baseline (a custom nav order, an extra plugin, a different theme variant), the skill surfaces the conflict, proposes the resolution, and waits for user approval. Patch mode is additive, not destructive.
4. **Always** read the spec at runtime: prefer the target repo's `spec/project/mkdocs-structure/<canonical_language>.md`; fall back to the copy shipped by the `nolte-shared` plugin (read from the plugin install path) only when the target repo lacks one. Never carry a baked-in copy inside the skill itself; never invent requirements that don't appear in either reachable copy. When neither is reachable, stop and ask the user which spec source to use (matches the spec's own §Extension hooks §"Project-type discovery" fallback pattern).
5. **Always** run `mkdocs build --strict` after every non-trivial edit. The build is the authoritative rendering gate; a passing local build is the floor, not the ceiling. Failures stop the skill and surface the raw output to the user.
6. **Never** bump versions, commit, push, tag releases, or open pull requests. The skill produces working-tree edits only; commit / PR / release lifecycle is owned by separate skills (`pull-request-create`, `pull-request-merge`, `release-publish-trigger`).
7. **Never** install Python packages on the caller's machine. When a baseline plugin is missing from the dep manifest, the skill reports the exact `pip install` / `uv pip install` / `poetry add` command appropriate to the project's package manager; the user runs it.
8. **Never** dispatch the `Skill` tool recursively into this skill (silent loops) or chain to a sibling skill outside the declared hand-off points. The skill **MAY** orchestrate the `audience-doc-author` agent and the future `docs-dry-refactor` skill at the explicit hand-off points named in the Output contract `Caller follow-ups` section; orchestration is allowed per `spec/claude/skill-vs-agent/` §Hybrid pattern, silent recursion isn't.
9. **Never** create or modify GitHub labels, branch protections, or remote state. The skill is local-only; remote state is owned by `project-structure-apply` and the platform Probot configs.
10. **Plugin-extension MUSTs from project-type-specific extension specs are additive.** The skill reads every active extension spec (discoverable via marker files per the parent spec's §Extension hooks §"Project-type discovery"), composes their MUSTs with the baseline, and emits a combined audit. The skill never silently relaxes a baseline MUST because an extension is active; explicit relaxation requires a stated rationale in the extension spec.
11. **Never** duplicate the catalog-generator wiring owned by `skill-agent-catalog-apply`. When the catalog extension is active, route the user to that skill for the `gen-files` + `literate-nav` plumbing; this skill only verifies the catalog extension's MUSTs are honoured at the baseline level.
12. **Never** rename, reorder, or hide a standard section silently. The seven-section order is fixed by the spec; reordering is a spec amendment, not a patch.
13. **Always** scaffold every container page (section folder index pages, placeholder pages with frontmatter) symmetrically across every language tree configured in `spec/.spec-config.yml`'s `languages` list, per `spec/project/docs-multilingual-authoring/` §Authoring protocol. Writing `docs/<canonical_language>/<section>/index.md` without writing the counterparts in every other configured language tree in the same operation is a violation, even when the page body is a placeholder. `README.md` at the repository root is the explicit exception per `spec/project/readme-structure/` §File and language and stays English-only.

## Gotchas

Per `spec/claude/skill-management/` §Gotchas: concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **`mkdocs-static-i18n` with `docs_structure: folder` requires every page to exist in every configured language tree.** A `docs/de/index.md` without a matching `docs/en/index.md` (or vice versa) is a build-time error, not a warning. When scaffolding for a new language, scaffold the full file tree at once rather than one page at a time; partial scaffolds break the build.
- **The built-in `search` plugin must be declared explicitly in the `plugins:` list once any other plugin is declared.** MkDocs's default behaviour is to enable `search` when `plugins:` is absent; declaring any plugin disables the default and requires `search` to be listed explicitly. Forgetting this is a common silent regression that drops the site's search bar.
- **`pymdownx.superfences` belongs in `markdown_extensions:`, not `plugins:`.** It's a Markdown extension shipped by `pymdown-extensions`, not a MkDocs plugin. Misplacing it produces an opaque build error that points at the wrong line.
- **`mkdocs-include-markdown-plugin` resolves include paths relative to the `docs_dir`, not relative to the file that contains the include directive.** A `{% include-markdown "../../../README.md" %}` from `docs/en/guides/intro.md` works because MkDocs walks up from `docs/`, not from the page file. Be explicit about the path origin when generating include directives so the user doesn't get confused.
- **`spec/.spec-config.yml`'s `languages` list is the source of truth for the configured language set, not `mkdocs.yml`'s `i18n` plugin config.** When the two diverge, treat `spec/.spec-config.yml` as authoritative and surface the divergence; never mutate `spec/.spec-config.yml` from this skill.
- **The package manager detection is order-sensitive.** Check for `uv.lock` before `poetry.lock` before `requirements*.txt` before falling back to a bare `pyproject.toml` `[project.dependencies]`; the presence of a lock file is a stronger signal than the bare manifest and dictates the install command to recommend.
- **`mkdocs build --strict` fails on every warning, not just errors.** A missing language-tree counterpart, a broken include marker, an unreferenced page in `nav:`, all trip the strict flag. When the build fails, surface the entire stderr block verbatim; the line numbers in MkDocs output are load-bearing for the user's fix.
- **The five-extension-section cap (per spec §Extension hooks) is summed across every active extension spec.** A repo activating two extension specs that each declare three sections is over the cap by one; the skill surfaces this as a Critical finding and routes the user to consolidate or amend the spec, never silently truncating.
