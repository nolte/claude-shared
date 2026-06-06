---
title: Glossary
audience: [external-contributor, maintainer]
content_mode: glossary
track: developer-docs
last_updated: 2026-06-06
---

# Glossary

Project-specific terminology for `claude-shared`. General prose terms are owned
by the upstream `nolte/vale-style` vocabulary (per `spec/project/prose-style/`);
this glossary captures only the project-specific delta.

- **Agent**: a focused Claude Code sub-agent defined in `agents/<name>.md`,
  dispatchable by `subagent_type`, with its own tool allow-list and system
  prompt.
- **Catalog**: the auto-generated skill/agent reference pages under
  `docs/<lang>/skills/` and `docs/<lang>/agents/`, produced by the
  skill-agent-catalog generator.
- **Dogfooding**: running this repository's own plugin against itself via
  `claude --plugin-dir .` while developing.
- **Plugin marketplace**: the distribution channel through which `nolte-shared`
  reaches consumer projects; the single delivery path (no copying into
  `.claude/skills/`).
- **Portfolio**: the set of `nolte/*` repositories that share conventions; this
  repo is one member.
- **Primary checkout**: the integration-only working copy at
  `~/repos/github/claude-shared/` that MUST stay on `develop`.
- **Skill**: a reusable slash command defined in `skills/<name>/SKILL.md`,
  invocable as `/nolte-shared:<skill>`.
- **Spec**: a bilingual specification under `spec/<area>/<topic>/<lang>.md`, with
  one EN-canonical source and DE translation kept in sync.
- **Track**: the `user-docs` / `developer-docs` audience-track signal carried in
  every docs page's frontmatter (per `spec/project/docs-audience-tracks/`).
- **Worktree**: a dedicated git working copy branched off `develop` where all
  feature work happens, kept under the configurable `NOLTE_WORKTREE_ROOT`.

## Sources

- `spec/project/prose-style/` — the upstream `nolte/vale-style` vocabulary baseline
- `CLAUDE.md` — definitions of primary checkout, worktree, dogfooding
- `spec/project/docs-audience-tracks/` — track definition
