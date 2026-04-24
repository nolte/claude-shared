# CLAUDE.md

Orientation for Claude Code and contributors working inside this repository.

## What this repo is

`claude-shared` is a single Claude Code plugin published as `nolte-shared`. It bundles reusable skills, agents, and specifications so Claude Code workflows stay consistent across the nolte portfolio.

## Layout

- `.claude-plugin/plugin.json` — plugin manifest (name, version, author)
- `.claude-plugin/marketplace.json` — marketplace catalog (downstream install source)
- `skills/<name>/SKILL.md` — reusable skills; each folder is one skill
- `agents/<name>.md` — reusable sub-agents (when present)
- `spec/` — bilingual specifications that govern skill/agent authoring and project conventions
- `docs/` — MkDocs source, bilingual (`docs/de/`, `docs/en/`)

Plugin skills are namespaced by plugin name — e.g. `/nolte-shared:spec`, `/nolte-shared:skill-management`.

## Command entry points

Local automation runs through `Taskfile.yml`:

- `task lint` — pre-commit checks
- `task test` — test suite (placeholder — no runtime tests yet)
- `task docs` — build the MkDocs site
- `task plugin:reload` — launch Claude Code with this repo loaded as a plugin (dogfooding)

## Dogfooding

When developing inside this repository, launch Claude Code with the plugin pointed at the repo root:

```bash
claude --plugin-dir .
```

Use `/reload-plugins` inside the session to pick up changes without restarting.

## Conventions

- New skills are scaffolded via `/nolte-shared:skill-management`.
- Specs are authored and translated via `/nolte-shared:spec`.
- Project-structure drift is checked via `/nolte-shared:project-structure-apply`.
- Pull requests are created via `/nolte-shared:pull-request-create` following `spec/project/pull-request-workflow/`.

## Authoring rules

- Keep `CLAUDE.md`, `spec/`, and the plugin manifest in sync with what the repo actually ships.
- Never copy plugin-owned skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace.
- All generated configuration files (`.github/*.yml`, `Taskfile.yml`, workflow YAML) are written in English for portfolio consistency, regardless of the language used in conversation.
