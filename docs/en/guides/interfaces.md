---
title: Interfaces and contracts
audience: [external-contributor, maintainer]
content_mode: reference
track: developer-docs
last_updated: 2026-06-06
---

# Interfaces and contracts

Every interface `claude-shared` exposes that another component, plugin, or human
caller can drive. The bulk of the per-item detail lives in the generated catalog
pages under [Skills](../skills/index.md) and [Agents](../agents/index.md); this
page enumerates the interface *kinds* and where each one's contract is defined.

## Slash commands (skills)

Each skill under `skills/<name>/SKILL.md` is invocable as a slash command
`/nolte-shared:<skill>`. The command name equals the skill folder name. The
authoritative per-skill contract (trigger phrasing, operations, inputs) is the
skill's own `SKILL.md` frontmatter and body; the rendered catalog is at
[Skills](../skills/index.md).

## Agents (subagent types)

Each agent under `agents/<name>.md` is dispatchable as a sub-agent whose
`subagent_type` equals the agent file name. The agent's frontmatter declares its
tool allow-list and model; its body is the system prompt. The rendered catalog
is at [Agents](../agents/index.md).

## Plugin manifest contract

`.claude-plugin/plugin.json` is the install-time contract consumed by the plugin
marketplace: it declares `name` (`nolte-shared`, part of every slash invocation),
`version`, `author`, and the repository pointer. The marketplace catalog
(`.claude-plugin/marketplace.json`) is the downstream install source.

## Specification frontmatter contract

Every spec under `spec/<area>/<topic>/<lang>.md` follows the structure governed by
`spec/project/spec-driven-development/` and is configured by
`spec/.spec-config.yml` (canonical language, translation languages). The
generated index is `spec/README.md` (don't hand-edit).

## MkDocs per-page frontmatter contract

Every page under `docs/<lang>/` declares the five-key frontmatter MUST set
(`title`, `audience`, `content_mode`, `track`, `last_updated`) defined by
`spec/project/mkdocs-structure/` §Per-page structure and
`spec/project/docs-audience-tracks/` §Per-page contract. Catalog-generated pages
carry `last_updated: generated`. The frontmatter is the contract downstream
tooling (`docs-freshness`, the catalog generator) relies on.

## Sources

- `spec/project/docs-audience-tracks/` §Developer-docs content contract (interface block)
- `spec/project/mkdocs-structure/` §Per-page structure
- `spec/claude/skill-agent-catalog/` — the generator that carries the per-item interface detail
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
