# Example 01 — Plugin mode, fresh wire-up

## Input prompt

> Wire up the skill-and-agent catalog in this repo per the spec.

## Input files

Repository state at invocation:

```

.
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── foo-skill/SKILL.md
│   └── bar-skill/SKILL.md
├── agents/
│   ├── alpha-agent.md
│   └── beta-agent.md
├── docs/
│   ├── requirements.txt
│   └── en/
│       └── index.md
├── mkdocs.yml
├── Taskfile.yml
└── spec/claude/skill-agent-catalog/en.md

```

`.claude-plugin/plugin.json` (excerpt):

```json

{
  "name": "example-plugin",
  "version": "0.4.2"
}

```

`mkdocs.yml` (excerpt — base MkDocs setup already scaffolded by `project-structure-apply`, but **no** catalog plugins yet):

```yaml

site_name: example-plugin
theme:
  name: material
plugins:
  - search
nav:
  - Home: index.md

```

`docs/requirements.txt`:

```

mkdocs-material==9.5.*

```

`Taskfile.yml` already has a `docs` target that runs `mkdocs build --strict`.

No `scripts/docs/gen_catalog.py`, no `docs/catalog-sources.yml`, no generated `docs/skills/` or `docs/agents/` tree. Working tree is clean.

## Expected behaviour

1. **Preconditions** — confirm git repo; detect **plugin mode** because `.claude-plugin/plugin.json` exists; locate `spec/claude/skill-agent-catalog/en.md` in the repo; report the detected mode explicitly.
2. **Audit** — emit the table from the skill's *Output shape* section. Every row is `missing` except `mkdocs.yml exists` (`pass`) and `task docs target exists` (`pass`):
   - `gen-files` plugin → missing
   - `literate-nav` plugin → missing
   - source-roots config → missing
   - source-roots match plugin mode → missing
   - Skills/Agents nav sections → missing
   - tag index → missing
   - generated markdown uncommitted → pass (nothing tracked yet)
   - docs deps include both plugins → missing
3. **Propose changes** — present each as a separate per-item approval (do not bundle):
   - Patch `mkdocs.yml` to add `gen-files` (pointing at `scripts/docs/gen_catalog.py`) and `literate-nav` plugins, preserving the existing `search` entry.
   - Create `docs/catalog-sources.yml` with the local plugin as the **first** entry:

     ```yaml

     sources:
       - name: example-plugin
         local: .
         repo_url: https://github.com/<owner>/example-plugin
         branch: main

     ```

     Resolve `<owner>` from `git remote get-url origin`; if unresolvable, ask the user.
   - Create `scripts/docs/gen_catalog.py` honouring every "must" in §2.3 (fail on bad frontmatter, emit `SUMMARY.md` files, deterministic ordering, link back to the source repo at the configured branch, render `tags.md`). Hook docstring points at `spec/claude/skill-agent-catalog/en.md`.
   - Append `mkdocs-gen-files`, `mkdocs-literate-nav`, and `pyyaml` to `docs/requirements.txt` (pinned to a minor range).
4. **Verify** — after writes, run `task docs` and report:
   - build pass/fail
   - count of `site/skills/` and `site/agents/` pages (expect 2 each)
   - tag index present
   - `git status docs/` clean (no generated markdown leaked into the working tree)
5. **Hard-rule compliance** — never write any file before the user approves that specific item; never bump `version` in `.claude-plugin/plugin.json`; never demote the local plugin out of the sources list.
6. **Language** — the user wrote English, so explanations and the audit table are in English; generated file contents (`mkdocs.yml`, the Python hook, `docs/requirements.txt`) are English regardless.
