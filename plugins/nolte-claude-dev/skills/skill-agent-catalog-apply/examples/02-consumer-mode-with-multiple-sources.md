# Example 02 — Consumer mode with multiple external sources

## Input prompt

> Richte den Skill-/Agent-Katalog in diesem Repo ein. Wir installieren `nolte-shared` und `acme-plugin` als externe Plugins und wollen beide im Katalog sehen.

## Input files

Repository state at invocation (a downstream consumer that uses Claude Code plugins but doesn't ship its own):

```

.
├── docs/
│   ├── requirements.txt
│   └── en/
│       └── index.md
├── mkdocs.yml
├── Taskfile.yml
├── vendor/
│   └── acme-plugin/        # vendored copy of an external plugin
│       ├── skills/
│       └── agents/
├── ../claude-shared/       # sibling checkout of nolte-shared
└── spec/claude/skill-agent-catalog/en.md

```

Notably **absent**: `.claude-plugin/plugin.json`. This repo is not a plugin itself.

`mkdocs.yml` (excerpt):

```yaml

site_name: example-consumer
theme:
  name: material
plugins:
  - search
  - awesome-pages
nav:
  - Home: index.md

```

`docs/requirements.txt`:

```

mkdocs-material==9.5.*
mkdocs-awesome-pages-plugin==2.9.*

```

Working tree is clean. There is no `skills/` or `agents/` directory at the repo root.

## Expected behaviour

1. **Preconditions** — confirm git repo; detect **consumer mode** because `.claude-plugin/plugin.json` is absent; report the detected mode explicitly and state that no `local: .` entry will be added (per the Hard rule).
2. **Source-root prompt** — before proposing any changes, ask the user which external plugin source roots to wire in. The user already named `nolte-shared` (sibling checkout at `../claude-shared`) and `acme-plugin` (vendored at `vendor/acme-plugin`). Confirm the on-disk paths exist; if either is missing, stop and ask.
3. **Audit** — every catalog row is `missing`; `awesome-pages` and `search` are preserved untouched in the proposed `mkdocs.yml` patch.
4. **Propose changes** (per-item approval):
   - Patch `mkdocs.yml` to add `gen-files` (pointing at `scripts/docs/gen_catalog.py`) and `literate-nav`, keeping `search` and `awesome-pages` in place.
   - Create `docs/catalog-sources.yml` with **two** external entries and **no** `local: .`:

     ```yaml

     sources:
       - name: acme-plugin
         local: vendor/acme-plugin
         repo_url: https://github.com/acme/acme-plugin
         branch: main
       - name: nolte-shared
         local: ../claude-shared
         repo_url: https://github.com/nolte/claude-shared
         branch: main

     ```

     Default ordering is alphabetical by `name` (spec §"Always" rule for consumer mode); confirm with the user before writing if they want a different order.
   - Create `scripts/docs/gen_catalog.py` that walks both source roots, reads `<source.local>/skills/*/SKILL.md` and `<source.local>/agents/*.md` for each, groups output by `name`, and links back to each source's `repo_url` + `branch`.
   - Append `mkdocs-gen-files`, `mkdocs-literate-nav`, and `pyyaml` to `docs/requirements.txt`.
5. **Verify** — after writes, run `task docs` and confirm:
   - build pass
   - `site/skills/` contains pages from both `acme-plugin` and `nolte-shared`, grouped under their plugin labels
   - `site/agents/` likewise
   - `site/tags/` aggregates tags across **both** sources
   - `git status docs/` clean
6. **Hard-rule compliance** — never declare a `local: .` entry (consumer mode forbids it); never silently drop a source root the user named; preserve every existing `mkdocs.yml` plugin entry.
7. **Language** — the user wrote German, so all conversational output (audit table, change proposals, verification report) is in German; generated file contents (`mkdocs.yml`, hook, requirements) remain English per the User-language policy.
