# Apply-changes elaboration

The full per-item elaboration for step 2 of `skill-agent-catalog-apply`. For every `missing` or `drift` item, draft the exact change and ask the user to approve it before writing; don't bundle unrelated changes into a single approval step.

## Table of contents

- [2.1 Wire the generator surface](#21-wire-the-generator-surface)
- [2.2 Configure plugin source roots](#22-configure-plugin-source-roots)
- [2.3 Write the generator module](#23-write-the-generator-module)
- [2.4 Add the dependencies](#24-add-the-dependencies)
- [2.5 Reconcile the committed-catalog policy with the deploy surface](#25-reconcile-the-committed-catalog-policy-with-the-deploy-surface)

## 2.1 Wire the generator surface

The spec defines **one generator module with a single rendering core**, exposed through **one of three invocation surfaces** (spec §Generation mechanism). The form choice concerns only *how* the module is invoked and **MUST NOT** fork the rendering logic. Pick the surface and wire it; `mkdocs-literate-nav` is always added.

**Surface A — `on_pre_build` hook (the recommended default).** Register the generator module under `hooks:` in `mkdocs.yml`. It fires inside **every** `mkdocs build` (including a bare `mkdocs build`, `mkdocs serve`, and the `mkdocs gh-deploy` run by the shared deploy reusable), so `mkdocs` collects and localizes its physical pages exactly like hand-authored ones, with **no Taskfile or CI wiring** and no committed catalog tree:

```yaml
hooks:
  - scripts/docs/gen_catalog.py
plugins:
  - search
  - literate-nav:
      nav_file: SUMMARY.md
```

**Surface B — standalone pre-build step.** A `Taskfile.yml` `docs`-target dependency (or the module's `__main__`) that writes the same physical files before `mkdocs build`. Equally valid and explicitly supported; it's the surface that drives a **committed-catalog freshness gate** and local `git diff` review (see §2.5).

**Surface C — `mkdocs-gen-files` script.** Emits the pages as virtual files:

```yaml
plugins:
  - search
  - gen-files:
      scripts:
        - scripts/docs/gen_catalog.py
  - literate-nav:
      nav_file: SUMMARY.md
```

**i18n prohibition (load-bearing).** A repository using `mkdocs-static-i18n` with `docs_structure: folder` **MUST** choose Surface A or B (the two physical-file surfaces). `mkdocs-static-i18n` 1.3.x discards files whose `abs_src_path` isn't under `docs_dir`, so **Surface C silently drops every generated page → empty catalog**. Detect the i18n mode from `mkdocs.yml` before proposing a surface, and never scaffold Surface C into a folder-mode repo.

Preserve every other plugin the repo already declares; only add what's missing. If a surface is already wired (for example `hooks:` already lists `gen_catalog.py`), that is **conformant — report it as `pass`, not drift**. If a surface points at a different script, report the drift and ask whether to merge or replace.

## 2.2 Configure plugin source roots

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

## 2.3 Write the generator module

Create `scripts/docs/gen_catalog.py` as **one module with a single rendering core**, invoked through the surface chosen in §2.1 (a thin entry point per surface delegating to that shared core — never a per-form fork). For Surface A/B the core writes **physical files** under `docs/<lang>/<section>/`; for Surface C it emits them as `mkdocs-gen-files` virtual files. The core walks every configured source root, reads each skill's `SKILL.md` and each agent's `<name>.md`, parses the frontmatter, and emits catalog pages. Key behaviours it **must** honour per the spec:

- **Parse frontmatter with `yaml.safe_load`** (or an equivalent standard YAML parser), not a flat-line custom parser. The use-case fields `dont_use_when` and `examples` are YAML lists of mappings and require nested-mapping support per spec §Generation mechanism.
- Fail the build when a skill or agent has invalid frontmatter (missing `name`, missing `description`, agent missing `distribution`, `name` mismatches folder/file). Raise a clear exception naming the offending file and its source root.
- Validate the use-case fields (`use_when`, `dont_use_when`, `see_also`, `examples`) against the shape rules in spec §Use-case metadata: type, key-set, entry-count and per-string character limits. Resolve `dont_use_when[].alternative` and `see_also[]` against the discovered catalog; fail the build on unresolved or ambiguous names.
- Validate `summary` and every `summary_<lang>` (≤200 characters, non-empty after whitespace stripping); fail the build on shape violations.
- Reject author-declared `tags` entries that begin with `_` — the underscore prefix is reserved for generator-emitted auto-tags (`_translation-pending`).
- Render `name` as page title, the **per-language summary** as a scannable subtitle above the routing description (resolution: `summary_<lang>` → `summary` → first sentence of `description` truncated; fall back to `summary` or truncation flips a chrome-localised "translation pending" badge and tags the page with `_translation-pending`), `description` and body verbatim except for cross-linking, `distribution` for agents, the effective tags (author-declared + auto-tags) as visible tags.
- Render each declared use-case field as its own scannable section with chrome-localised labels: "Use when" / "Anwenden wenn", "Don't use when" / "Nicht anwenden wenn", "See also" / "Siehe auch", "Examples" / "Beispiele".
- Cross-linking pass: build a per-language `name → URL` index from every discovered artifact, then rewrite every `dont_use_when[].alternative` and `see_also[]` reference into a Markdown link, and rewrite inline-code mentions (`` `name` ``) in the rendered `description`, `summary`, `summary_<lang>`, and body into Markdown links — but only when the mention resolves to exactly one artifact. Ambiguous inline-code mentions stay unlinked and emit a non-fatal generator warning.
- Link back to the source file on the originating plugin's repo at the configured branch.
- Write entries in deterministic alphabetical order by `name` within each plugin group of each phase.
- Emit `docs/<lang>/skills/SUMMARY.md` and `docs/<lang>/agents/SUMMARY.md` for literate-nav per configured docs language.
- Section index pages link prominently to `../by-task.md` near the top.
- Emit a `docs/<lang>/tags.md` tag index per configured docs language, listing every author-declared tag and every auto-tag that at least one artifact carries on that language.
- Emit a **one-shot** `docs/<lang>/by-task.md` skeleton per configured docs language, pre-populated from artifacts' `use_when` entries. **Do not overwrite** the file if it already exists — the landing page transitions from generator-emitted skeleton to hand-curated artifact on the first edit.

Include a concise docstring on the hook summarising what it does and pointing at the spec. Don't duplicate spec rules as comments scattered across the code; keep the hook readable and let the spec be the source of truth.

## 2.4 Add the dependencies

Add `mkdocs-literate-nav` and `pyyaml` (needed for **every** surface — literate-nav for navigation, `pyyaml` for the standard-YAML frontmatter parsing and for loading `catalog-sources.yml`). Add `mkdocs-gen-files` **only** when the repo uses Surface C; the `on_pre_build` hook and the standalone pre-build step write physical files and need no gen-files dependency. Append to whichever docs-deps location the repo already uses:

- `docs/requirements.txt`: append the packages, pinned to a minor range.
- `pyproject.toml` with `[project.optional-dependencies] docs = [...]`: append the entries.
- `requirements/docs.txt`: same as above.

## 2.5 Reconcile the committed-catalog policy with the deploy surface

Whether a committed catalog tree is correct depends on the deploy surface (spec §Generation mechanism), so first establish which mechanism applies:

- **Deploy-time generation (preferred)** — the deploy pipeline regenerates on every build (the `on_pre_build` hook fires inside `mkdocs build`/`mkdocs gh-deploy`; or the reusable runs `task docs`; or a `gen-files` script runs in the plugin build). Here the tree **MUST NOT** be committed. If `docs/**/skills/`, `docs/**/agents/`, or `docs/**/tags.md` is git-tracked, offer to `git rm --cached` those paths and add matching `.gitignore` entries:

  ```
  # Generated by scripts/docs/gen_catalog.py — do not commit
  /docs/**/skills/
  /docs/**/agents/
  /docs/**/tags.md
  ```

- **Committed catalog with a freshness gate (fallback)** — the shared deploy reusable doesn't run the generator (for example it deploys a bare `mkdocs build` that never invokes `task docs`), so the published Pages output would otherwise be incomplete. Here the tree **MUST** be committed **and** guarded by a CI freshness check that fails when the committed tree drifts from a fresh regeneration (the generator still runs locally via the `task docs` pre-build dependency and a `docs-catalog-fresh` pre-commit hook). Do **not** untrack the tree in this case; instead verify the freshness gate exists and, if it's missing, propose adding it. Note that the `on_pre_build` hook is the **recommended way to exit this fallback**: because it fires inside the deploy build, the catalog regenerates at deploy time and the committed tree plus its gate are no longer needed.
