---
name: skill-agent-catalog-apply
description: "Wires up the MkDocs skill-and-agent catalog in the current Claude Code plugin repository per the canonical-language file under spec/claude/skill-agent-catalog/. Audits the MkDocs config against the spec, scaffolds or patches the gen-files + literate-nav plugin configuration, writes the generator hook that walks every configured plugin source root, adds the Python dependencies to the project's docs requirements, and verifies that `task docs` produces Skills and Agents sections in the built navigation. Invoke when the user asks to \"apply the skill-agent-catalog spec\", \"wire up the catalog generator\", \"scaffold the skills/agents navigation\", or \"add another plugin source root\". Also handles equivalent German-language requests and checking whether a wired catalog is still in sync. Don't use for authoring individual skills/agents (use `skill-management`) or for general docs scaffolding (use `project-structure-apply`)."
tags: [scaffolding, audit]
phase: design
---

# Skill and Agent Catalog Apply

Operationalises `spec/claude/skill-agent-catalog/<canonical_language>.md` inside the current repository. The skill audits the current catalog wiring, proposes the concrete file-level changes the spec requires, and—with explicit per-change user consent—applies them.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path). Never invent requirements that don't appear in the spec.

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
4. Locate `spec/claude/skill-agent-catalog/` in the current repo or via the `nolte-shared` plugin. If neither is reachable, stop and ask the user which spec source to use.
5. In consumer mode, ask the user which external plugin source roots should appear in the catalog before proposing any changes (for example local clones of `nolte-shared`, other nolte plugins, or third-party plugins). Require at least one; the catalog is meaningless with an empty source list.
6. Check for uncommitted changes in `mkdocs.yml`, the docs requirements file, and any existing generator hook path. If the tree is dirty there, report and ask whether to stash, commit, or abort—never overwrite uncommitted work.

## Operations

### 1. Audit

Read the spec's Acceptance Criteria and classify each item as `pass`, `missing`, or `drift`:

| Spec item | How to check |
|---|---|
| `mkdocs.yml` declares `mkdocs-gen-files` | Parse `plugins:` list; look for `gen-files` entry. |
| `mkdocs.yml` declares `mkdocs-literate-nav` | Look for `literate-nav` in `plugins:`. |
| Plugin source roots are configured | Look under `plugins.gen-files.scripts` or the extension config for a structure pairing local paths with public repo URLs (spec §Generation mechanism). |
| Source roots match the detected mode | In plugin mode, the local path `.` (or `skills/` + `agents/`) with the repo's own `https://github.com/<owner>/<repo>` URL must be present. In consumer mode, at least one external source root must be present and no local-plugin entry should be declared. |
| Skills and Agents navigation sections exist | Inspect `nav:` for stable top-level entries. Literate-nav `SUMMARY.md` files produced by the generator also satisfy this. |
| Tag index page exists | Either declared in `nav:` or generated as `docs/tags.md`. |
| Generated markdown stays uncommitted | Run `git ls-files docs/skills/ docs/agents/ docs/tags.md 2>/dev/null`; any hits are drift (generated pages must not be git-tracked). |
| `task docs` regenerates the catalog | Inspect `Taskfile.yml`'s `docs` target; confirm it calls `mkdocs build` (or a thin wrapper) without requiring a separate regeneration step. |
| Docs deps include `mkdocs-gen-files` and `mkdocs-literate-nav` | Read `docs-requirements.txt` / `pyproject.toml` `docs` extras / `requirements/docs.txt`, whichever the repo uses. |

Report findings grouped by spec section: Navigation, Generation mechanism, Source roots, Dependencies, Git hygiene. Audit is read-only.

### 2. Propose and apply changes

For every `missing` or `drift` item, draft the exact change and ask the user to approve it before writing. Don't bundle unrelated changes into a single approval step; the user decides per item.

#### 2.1 Add the MkDocs plugins

Patch `mkdocs.yml` to declare the two plugins. Typical shape:

```yaml
plugins:
  - search
  - gen-files:
      scripts:
        - scripts/docs/gen_catalog.py
  - literate-nav:
      nav_file: SUMMARY.md
```

Preserve every other plugin the repo already declares; only add what's missing. If `gen-files` is already present but points at a different script, report the drift and ask whether to merge scripts or replace.

#### 2.2 Configure plugin source roots

The spec's "plugin source roots" are the (local path, public repo URL) pairs the generator reads. Store the list in a sibling YAML file so `mkdocs.yml` stays compact, and have the generator load it.

**Plugin mode**: the local plugin MUST be the first entry; additional external plugins MAY follow:

```yaml
# docs/catalog-sources.yml
sources:
  - name: nolte-shared         # plugin name, used as the group label
    local: .                   # path relative to the repo root
    skills_path: skills        # optional, default "skills"
    agents_path: agents        # optional, default "agents"
    repo_url: https://github.com/nolte/claude-shared
    branch: main
```

**Consumer mode**: no local entry; each source is an external plugin (local clone path, installed plugin path, or submodule):

```yaml
# docs/catalog-sources.yml
sources:
  - name: nolte-shared
    local: ../claude-shared    # a sibling checkout or vendored path
    repo_url: https://github.com/nolte/claude-shared
    branch: main
  - name: other-plugin
    local: vendor/other-plugin
    repo_url: https://github.com/acme/other-plugin
    branch: main
```

In either mode, extending the source list later (adding more external plugins) is a pure data change; no generator-code change needed.

#### 2.3 Write the generator hook

Create `scripts/docs/gen_catalog.py`. The hook walks every configured source root, reads each skill's `SKILL.md` and each agent's `<name>.md`, parses the frontmatter, and emits catalog pages via `mkdocs_gen_files.open(...)`. Key behaviours the hook **must** honour per the spec:

- Fail the build when a skill or agent has invalid frontmatter (missing `name`, missing `description`, agent missing `distribution`, `name` mismatches folder/file). Raise a clear exception naming the offending file and its source root.
- Render `name` as page title, `description` verbatim, `distribution` for agents, `tags` as visible tags.
- Link back to the source file on the originating plugin's repo at the configured branch.
- Write entries in deterministic alphabetical order by `name` within each plugin group.
- Emit `docs/skills/SUMMARY.md` and `docs/agents/SUMMARY.md` for literate-nav.
- Render the skill body (or agent system-prompt body) as the page's main content.
- Emit a `docs/tags.md` tag index linking to every artifact that declares each tag.

Include a concise docstring on the hook summarising what it does and pointing at the spec. Don't duplicate spec rules as comments scattered across the code; keep the hook readable and let the spec be the source of truth.

#### 2.4 Add the dependencies

Add `mkdocs-gen-files` and `mkdocs-literate-nav` to whichever docs-deps location the repo already uses:

- `docs-requirements.txt`: append both packages, pinned to a minor range.
- `pyproject.toml` with `[project.optional-dependencies] docs = [...]`: append both entries.
- `requirements/docs.txt`: same as above.

Also add `pyyaml` if the hook uses YAML (likely, since it loads `catalog-sources.yml`) and it isn't already present.

#### 2.5 Ensure git hygiene

If `docs/skills/`, `docs/agents/`, or `docs/tags.md` is currently git-tracked, the catalog was generated-then-committed in the past. Offer to `git rm --cached` those paths and add matching entries to `.gitignore`:

```
# Generated by scripts/docs/gen_catalog.py — do not commit
/docs/skills/
/docs/agents/
/docs/tags.md
```

### 3. Verify

After applying changes, run `task docs` (or `mkdocs build --strict` when no Taskfile target exists) and confirm:

- The build succeeds.
- `site/skills/index.html` or equivalent exists.
- `site/agents/index.html` or equivalent exists.
- `site/tags/index.html` exists (or `site/tags.html` depending on theme).
- No generated markdown appears under `git status` (the build dir `site/` is already gitignored per the MkDocs convention).

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

## Hard rules

- **Never** apply changes without explicit per-item user approval. The audit is read-only; writes are a separate, opt-in step.
- **Never** commit generated catalog markdown back into `docs/`. Emission happens at build time via `mkdocs-gen-files`; the `site/` build output is gitignored.
- **Never** remove an existing plugin source root silently when patching the sources file. Propose the change and wait for approval.
- **Never** bump the plugin version in `.claude-plugin/plugin.json` as part of this skill's changes (per `release-automation`, the version is set by the release workflow).
- **Never** translate artifact metadata or body at generation time. The spec says artifact content is rendered verbatim; only the surrounding chrome (section titles, intro text) is localised elsewhere.
- **Never** duplicate `nolte-shared` as a source root when the current repo is itself `nolte-shared`; it's the local plugin, and the sources file already has it.
- **Never** declare a local-plugin entry in consumer mode. Consumer-mode repos don't ship skills or agents of their own; adding a `local: .` source there would try to walk paths that don't exist.
- **Always**, in plugin mode, make the local plugin the first entry in the sources list so its catalog appears first in the navigation. In consumer mode, order external sources as the user requests them and default to alphabetical by `name` if unspecified.
- **Always** fail the docs build (via the generator hook) on malformed frontmatter rather than silently skipping. Broken catalogs defeat the whole point.
- **Always** point at the spec file in generated docstrings and in every reported drift item, so future readers follow the same rules.
- **Always** emit catalog pages (`docs/<lang>/skills/...`, `docs/<lang>/agents/...`, `docs/<lang>/tags.md` and equivalents) for every language tree configured in `spec/.spec-config.yml`'s `languages` list, per `spec/project/docs-multilingual-authoring/` §Authoring protocol. The generator hook reads `.spec-config.yml` at build time and emits one page per language per artefact; artefact body content (`description`, frontmatter) is rendered verbatim per the rule above, and only the surrounding chrome (section titles, intro text, nav labels) is localised per language.

## Gotchas

Per `spec/claude/skill-management/` §Gotchas: concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **`mkdocs-gen-files` and `mkdocs-literate-nav` must be pinned in `docs/requirements.txt`.** The catalog rendering depends on both plugins; without them the docs build either falls back silently to a navigation without the catalog (worst case, drift goes unnoticed) or fails with an opaque MkDocs plugin-not-found error. `project-structure-apply` and this skill share that requirement; verify both lines exist in `docs/requirements.txt` before assuming the build will pick the catalog up.
- **The generator hook only runs at build time, not on file save.** Changes to `skills/<name>/SKILL.md` or `agents/<name>.md` don't appear in the rendered catalog until the next `task docs` (or CI build). When the user edits an artefact and asks why the catalog doesn't show it, the answer is almost always that the build hasn't run yet, not that the generator's broken.
- **Plugin source roots in `docs/catalog-sources.yml` are repo-relative paths, not install paths.** In plugin mode the entry is `local: .` (the current repo *is* the plugin). In consumer mode the entry points at where the plugin's repo content actually lives on disk relative to the docs build, typically `local: ../claude-shared` for a sibling checkout, or a vendored or submoduled subdirectory. `mkdocs-gen-files` resolves the path at build time relative to the `mkdocs.yml` location; the runtime `.claude/plugins/<plugin>/` install path is for skill discovery at session-start, not for docs generation.
- **Consumer mode forbids the local-plugin entry.** A consumer-mode repo (one that installs `nolte-shared` rather than being it) **MUST NOT** declare `local: .` as a source; the walker would then look for `skills/` and `agents/` at the consumer's repo root, find nothing, and emit an empty catalog or a hard error. Plugin mode and consumer mode are deliberately exclusive on this point.

## Rationale

This is a skill, not an agent, because:

- **Orchestration role**: applying the catalog spec is a scaffolding step inside a larger "bring this plugin repo in line with portfolio conventions" flow, right alongside `project-structure-apply`. The output is expected to flow into the main conversation so the caller can see each proposed change.
- **Interactivity**: per-item approval of config patches is central to the contract; skills handle that naturally.
- **Specialisation isn't the limiting factor**: the real logic lives in the spec and in the generator hook (a Python file), not in a narrow system prompt; a restricted agent wouldn't sharpen the work.
- **Counter-dimension (context-window)**: the verification step (running `task docs` and reading the build output) has a mild context-window impact, but it's bounded and fits in the main conversation.
- **Counter-dimension (parallelism / tool restriction)**: writing `scripts/docs/gen_catalog.py` is a self-contained Python-authoring task that an agent could plausibly own with a narrower tool surface (`Read`, `Write`, `Glob`). The reason it stays in the skill: the file write is one of several per-item approvals in a single apply cycle, so splitting it out would add a dispatch boundary without removing the surrounding interactivity.

### Boundary against `project-structure-apply`

This skill follows the same orchestrator-pattern precedent as `project-structure-apply`, but the two own non-overlapping surfaces and **MUST NOT** be merged:

- `project-structure-apply` scaffolds the bare MkDocs setup itself: `mkdocs.yml`, the Material theme, `docs/<lang>/` trees, the `task docs` target, the docs-requirements file. It is the prerequisite — without a working `mkdocs.yml`, this skill's preconditions fail and route the user there.
- `skill-agent-catalog-apply` (this skill) wires the catalog generator on top of an already-scaffolded MkDocs setup: the `gen-files` plugin, the `literate-nav` plugin, the `docs/catalog-sources.yml` source-root list, and the `scripts/docs/gen_catalog.py` hook. It assumes the MkDocs base layer exists and never modifies the files `project-structure-apply` owns.

The split is load-bearing because the catalog generator is plugin-specific (it only runs in repositories that publish skills/agents), while the bare MkDocs setup is portfolio-wide. Folding the catalog wiring into `project-structure-apply` would force every project repo to carry the catalog plumbing it doesn't need.
