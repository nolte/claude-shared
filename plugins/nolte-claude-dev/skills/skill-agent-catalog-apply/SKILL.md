---
name: skill-agent-catalog-apply
description: "Wires up the MkDocs skill-and-agent catalog in the current repository per the canonical-language file under spec/claude/skill-agent-catalog/. Audits the MkDocs config against the spec, scaffolds or patches the catalog generator surface (the `on_pre_build` hook by default, or a standalone pre-build step; gen-files is forbidden under mkdocs-static-i18n folder mode) plus literate-nav, writes the generator module that walks every configured plugin source root, and verifies a docs build produces Skills and Agents sections. Invoke when the user asks to \"apply the skill-agent-catalog spec\", \"wire up the catalog generator\", \"scaffold the skills/agents navigation\", or \"add another plugin source root\". Also handles equivalent German-language requests and checking whether a wired catalog is still in sync. Don't use for authoring individual skills/agents (use `skill-management`) or for general docs scaffolding (use `project-structure-apply`). Supports resume on re-invocation per `spec/claude/resumable-work/`."
tags: [scaffolding, audit]
phase: design
summary: "Wires up the MkDocs skill-and-agent catalog (on_pre_build hook by default, literate-nav, source-roots) in a plugin or consumer repo."
summary_de: "Verdrahtet den MkDocs-Skill-und-Agent-Katalog (on_pre_build-Hook als Default, literate-nav, Source-Roots) in einem Plugin- oder Konsumenten-Repo."
use_when:
  - "you want to wire up the catalog generator in a fresh repo"
  - "you want to add another plugin source root to an existing catalog setup"
  - "you want to check whether a wired catalog is still in sync with the spec"
dont_use_when:
  - situation: "You want to author an individual skill or agent rather than the catalog wiring"
    alternative: skill-management
  - situation: "You want general MkDocs scaffolding (not catalog-specific)"
    alternative: mkdocs-structure-apply
see_also:
  - mkdocs-structure-apply
  - skill-management
  - project-structure-apply
resumable: true
---

# Skill and Agent Catalog Apply

Operationalises `spec/claude/skill-agent-catalog/<canonical_language>.md` inside the current repository. The skill audits the current catalog wiring, proposes the concrete file-level changes the spec requires, and—with explicit per-change user consent—applies them.

When the spec isn't present in the target repository, stop and tell the user the catalog spec is unavailable: `spec/` is repo-wide in the source monorepo and is not shipped with any plugin (see CLAUDE.md §Layout), so there is no installed copy to read at runtime. Offer to proceed only against explicitly user-supplied spec content. Never invent requirements that don't appear in the spec.

## User-language policy

Detect the user's language from their message and respond in it. Generated file contents (`mkdocs.yml`, the `docs_gen_*` Python hook, `docs-requirements.txt` / `pyproject.toml` extras) are always written in English so portfolio-wide automation stays predictable.

## Preconditions

Before doing anything:

1. Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
2. Detect the operating mode per the spec's *Operating modes* section:
   - If `.claude-plugin/plugin.json` exists at the repo root, the repo is operating in **plugin mode**. The local plugin will be one of the catalog's source roots.
   - If `.claude-plugin/plugin.json` is absent, the repo is operating in **consumer mode**. The catalog will only expose external plugin source roots; no local plugin is added.

   Report the detected mode explicitly in the audit output so the user knows which rule set applies. Don't bail purely because `.claude-plugin/plugin.json` is absent; consumer mode is a first-class supported shape.
3. Confirm an `mkdocs.yml` exists at the repo root. If not, stop and tell the user to run `project-structure-apply` first (which is responsible for scaffolding MkDocs itself).
4. Locate `spec/claude/skill-agent-catalog/` in the current repo. If it isn't reachable — the spec corpus is repo-wide in the source monorepo and is not shipped with any plugin — stop and ask the user which spec source to use (consistent with the unavailable-spec rule above).
5. In consumer mode, ask the user which external plugin source roots should appear in the catalog before proposing any changes (for example local clones of `nolte-shared`, other nolte plugins, or third-party plugins). Require at least one; the catalog is meaningless with an empty source list.
6. Check for uncommitted changes in `mkdocs.yml`, the docs requirements file, and any existing generator hook path. If the tree is dirty there, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

## Operations

### 1. Audit

Read the spec's Acceptance Criteria and classify each item as `pass`, `missing`, or `drift`. Read `references/audit-checklist.md` when running the audit — it carries the full spec-item → how-to-check table (generator surface, i18n-legal surface, literate-nav, source roots, nav sections, index/by-task/tag pages, YAML parser, use-case schema, clean tags, committed-catalog policy, build integration, dependencies).

Two rows are load-bearing enough to keep in view: **any** of the three generator surfaces (`on_pre_build` hook, standalone pre-build step, `gen-files` script) is `pass` — a repo on the `hooks:`/`on_pre_build` surface is conformant, not drift; and under `mkdocs-static-i18n` folder mode a `gen-files` surface is `drift` (its pages are silently dropped → empty catalog).

Report findings grouped by spec section: Navigation, Generation mechanism, Source roots, Use-case metadata, Per-language summary, Dependencies, Git hygiene. Audit is read-only.

### 2. Propose and apply changes

For every `missing` or `drift` item, draft the exact change and ask the user to approve it before writing. Don't bundle unrelated changes into a single approval step; the user decides per item.

Read `references/apply-changes.md` when applying any §2 change — it carries the full per-step elaboration with the YAML snippets, source-file shapes, and command lists: the three generator surfaces (§2.1), the plugin/consumer `docs/catalog-sources.yml` shapes (§2.2), the generator module's required behaviours (§2.3), the per-surface dependency set (§2.4), and the committed-catalog policy reconciliation (§2.5). The operation skeleton and the load-bearing i18n prohibition stay here:

- **2.1 Wire the generator surface.** One generator module, one rendering core, exposed through **one of three surfaces** (spec §Generation mechanism) — the form choice **MUST NOT** fork the rendering logic. Surface A: `on_pre_build` hook under `hooks:` (**recommended default**, fires inside every `mkdocs build`, no Taskfile/CI wiring, no committed tree). Surface B: standalone pre-build step (`Taskfile.yml` `docs`-target dependency; drives a committed-catalog freshness gate). Surface C: `mkdocs-gen-files` script (virtual files). `mkdocs-literate-nav` is always added; preserve every other declared plugin. An already-wired surface is `pass`, not drift.
  - **i18n prohibition (load-bearing).** A repository using `mkdocs-static-i18n` with `docs_structure: folder` **MUST** choose Surface A or B (the two physical-file surfaces). `mkdocs-static-i18n` 1.3.x discards files whose `abs_src_path` isn't under `docs_dir`, so **Surface C silently drops every generated page → empty catalog**. Detect the i18n mode from `mkdocs.yml` before proposing a surface, and never scaffold Surface C into a folder-mode repo.
- **2.2 Configure plugin source roots.** The (local path, public repo URL) pairs the generator reads, stored in `docs/catalog-sources.yml`. Plugin mode: the local plugin (`local: .`) is the first entry, externals MAY follow. Consumer mode: no local entry; each source is an external plugin. Extending the list later is a pure data change.
- **2.3 Write the generator module.** `scripts/docs/gen_catalog.py` as one module with a single rendering core (a thin per-surface entry point delegating to it — never a per-form fork). It walks every source root, parses frontmatter with `yaml.safe_load`, **fails the build on malformed frontmatter or unresolved use-case references**, renders per-language pages, runs the inline-code cross-linking pass, and emits `SUMMARY.md`, `tags.md`, and the one-shot `by-task.md` skeleton per language.
- **2.4 Add the dependencies.** `mkdocs-literate-nav` and `pyyaml` for **every** surface; `mkdocs-gen-files` **only** for Surface C. Append to whichever docs-deps location the repo uses.
- **2.5 Reconcile the committed-catalog policy with the deploy surface.** Deploy-time generation (preferred) → the tree **MUST NOT** be committed (offer `git rm --cached` + `.gitignore`). Committed-catalog fallback → the tree **MUST** be committed **and** guarded by a CI freshness gate; the `on_pre_build` hook is the recommended way to exit the fallback.

### 3. Verify

After applying changes, run `task docs` (or `mkdocs build --strict` when no Taskfile target exists) and confirm:

- The build succeeds.
- `site/skills/index.html` or equivalent exists.
- `site/agents/index.html` or equivalent exists.
- `site/tags/index.html` exists (or `site/tags.html` depending on theme).
- The build dir `site/` is gitignored per the MkDocs convention. For the **deploy-time-generation** policy, no generated markdown appears under `git status` (the `docs/**/{skills,agents,tags.md}` tree is gitignored). For the **committed-catalog fallback**, the regenerated tree *is* tracked; confirm `git status` shows no drift against a fresh run (that no-drift state is exactly what the CI freshness gate enforces).

Report the verification outcome. If the build fails, surface the offending file per the spec's error-handling rule and don't claim success.

### 4. Adding further source roots later

Both plugin-mode repos (which want to catalog *additional* plugins alongside their own) and consumer-mode repos (which only ever reference external plugins) evolve by extending `docs/catalog-sources.yml`:

- Edit `docs/catalog-sources.yml` to add entries for each extra plugin (local clone path or installed plugin path + repo URL + branch).
- Don't fork or modify the generator hook; the data-driven sources list is enough.
- If the extra plugin doesn't live at a local checkout yet, stop and ask the user for its location; don't guess.
- In plugin mode, never demote the local plugin out of the sources list while adding externals; it stays the first entry (see Hard rules).

## Output shape

After the audit step, produce a single report:

```
# Skill and Agent Catalog Apply — <repo>

## Audit
| Spec item | Status | Evidence |
| … | pass / missing / drift | <one line> |

## Proposed changes
1. <change>; file: <path>, rationale: <one line>
2. …

## Verification (after apply)
- task docs: <pass / fail>
- site/skills: <count> pages
- site/agents: <count> pages
- site/tags: <count> tags
- git status on docs/: <clean / dirty, list offenders>
```

## Examples

- Read `examples/01-plugin-mode-fresh-wireup.md` when wiring up the catalog generator in a plugin-mode repository for the first time.
- Read `examples/02-consumer-mode-with-multiple-sources.md` when configuring a consumer-mode repository with multiple external plugin sources.
- Read `examples/03-drift-tracked-catalog-md.md` when the generated catalog markdown has drifted from the current skill/agent set and you need to see how drift is reported and resolved.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/skill-agent-catalog-apply/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** apply changes without explicit per-item user approval. The audit is read-only; writes are a separate, opt-in step.
- **Never** commit generated catalog markdown back into `docs/` **when the deploy pipeline regenerates it on every build** (deploy-time generation — the preferred policy). A committed catalog tree is **legitimate and required** only under the committed-catalog fallback (spec §Generation mechanism): when the shared deploy reusable doesn't run the generator, the tree **MUST** be committed and guarded by a CI freshness check. Never untrack a committed tree that a repo relies on for the fallback; the `on_pre_build` hook is the recommended way to retire the fallback.
- **Never** scaffold the `mkdocs-gen-files` surface into a repo using `mkdocs-static-i18n` with `docs_structure: folder`. That surface's virtual files are silently discarded there → empty catalog; choose the `on_pre_build` hook (the recommended default) or the standalone pre-build step instead.
- **Never** report a repo already wired on the `hooks:`/`on_pre_build` surface (or the standalone pre-build step) as drift for "not using gen-files". All three surfaces are spec-conformant; the `on_pre_build` hook is the recommended default, not a deviation.
- **Never** remove an existing plugin source root silently when patching the sources file. Propose the change and wait for approval.
- **Never** bump the plugin version in `.claude-plugin/plugin.json` as part of this skill's changes (per `release-automation`, the version is set by the release workflow).
- **Never** translate the routing `description`, the body, or identifiers (`name`, `distribution`, `tags`, `phase`) at generation time. The single sanctioned translation surface is the per-language summary field `summary_<lang>` and the surrounding chrome (section titles, intro text, use-case section labels, translation-pending badge), per spec §Multilingual behavior.
- **Never** overwrite an existing `docs/<lang>/by-task.md` on subsequent generator runs. The skeleton is a one-shot starting point; once a human starts curating the landing page, the generator stays out of the way (spec §Task-oriented landing pages).
- **Never** duplicate `nolte-shared` as a source root when the current repo is itself `nolte-shared`; it's the local plugin, and the sources file already has it.
- **Never** declare a local-plugin entry in consumer mode. Consumer-mode repos don't ship skills or agents of their own; adding a `local: .` source there would try to walk paths that don't exist.
- **Always**, in plugin mode, make the local plugin the first entry in the sources list so its catalog appears first in the navigation. In consumer mode, order external sources as the user requests them and default to alphabetical by `name` if unspecified.
- **Always** fail the docs build (via the generator hook) on malformed frontmatter rather than silently skipping. Broken catalogs defeat the whole point.
- **Always** point at the spec file in generated docstrings and in every reported drift item, so future readers follow the same rules.
- **Always** emit catalog pages (`docs/<lang>/skills/...`, `docs/<lang>/agents/...`, `docs/<lang>/tags.md` and equivalents) for every language tree configured in `spec/.spec-config.yml`'s `languages` list, per `spec/project/docs-multilingual-authoring/` §Authoring protocol. The generator hook reads `.spec-config.yml` at build time and emits one page per language per artefact; artefact body content (`description`, frontmatter) is rendered verbatim per the rule above, and only the surrounding chrome (section titles, intro text, nav labels) is localised per language.

## Gotchas

Read `references/gotchas.md` for the concrete corrections to non-obvious environment facts (per `spec/claude/skill-management/` §Gotchas) — the load-bearing ones: `mkdocs-static-i18n` folder mode silently drops `gen-files` pages; the `on_pre_build` hook is the recommended default and needs no Taskfile/CI wiring; `mkdocs-literate-nav` + `pyyaml` must be pinned for every surface; the generator runs only at build time; source roots are repo-relative paths; consumer mode forbids the `local: .` entry; `by-task.md` is one-shot on the first run; the cross-linking pass only transforms inline-code spans; and `_translation-pending` is never an author-declared tag.

## Why this is a skill, not an agent

Read `references/skill-vs-agent-rationale.md` for the full `skill-vs-agent` justification and the load-bearing boundary against `project-structure-apply` — in short: this is an interactive, per-item-approval orchestration step whose real logic lives in the spec and the generator hook, so it stays in skill form; and `project-structure-apply` owns the bare MkDocs scaffolding (the prerequisite) while this skill wires the catalog generator on top, a non-overlapping split that **MUST NOT** be merged.
