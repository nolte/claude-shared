---
title: Architecture overview
audience: [external-contributor, maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-06-06
---

# Architecture overview

A one-screen view of how `claude-shared` is put together, for a newcomer who
needs to navigate the codebase.

## Context: What's inside, what's outside

`claude-shared` is a single Claude Code plugin (`nolte-shared`) plus the tooling
that authors, validates, and publishes it. It's a documentation-and-automation
project—there is no runtime service.

- **Inside**: the plugin's skills, agents, and specs; the MkDocs site; the
  Taskfile-driven automation; the planning suite under `project/`.
- **Outside**: Claude Code itself (the plugin builds on it but doesn't own it),
  the downstream projects that install the plugin, and the sibling portfolio
  repos (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`) that this
  repo consumes as dependencies.

## Building blocks

- **Skills** (`skills/<name>/SKILL.md`): reusable slash commands. Each folder is
  one skill; distribution is via the plugin marketplace, never by copying into a
  consumer's `.claude/skills/`.
- **Agents** (`agents/<name>.md`): focused sub-agents with a tool allow-list and
  a system prompt.
- **Specs** (`spec/`): the EN-canonical, DE-translated conventions that govern
  how skills, agents, docs, and the project itself are authored.
- **Docs** (`docs/<lang>/`): the bilingual MkDocs site, including the
  generated skill/agent catalog.
- **Automation** (`Taskfile.yml`, `scripts/`): the quality gate, catalog
  generation, validation, and the dogfooding entry point.

## Load-bearing decisions

The non-trivial trade-offs are recorded as conventions in `spec/` and in
`CLAUDE.md` rather than as standalone ADRs (the repo keeps no `docs/<lang>/adrs/`
tree yet):

- **Plugin-only distribution**—skills are never copied into consumers; the
  marketplace is the single delivery path.
- **EN-canonical specs, bilingual docs**—one source of truth per spec, kept in
  strict translation sync.
- **Primary-checkout-on-`develop` rule**—all feature work happens in worktrees;
  the primary checkout is an integration-only launchpad (see `CLAUDE.md`
  §Parallel working copies and `spec/project/parallel-working-copies/`).

## Sources

- `CLAUDE.md`: repository orientation and the load-bearing conventions
- `spec/project/parallel-working-copies/`: the worktree decision
- [Project Structure](project-structure.md): the on-disk building-block map
