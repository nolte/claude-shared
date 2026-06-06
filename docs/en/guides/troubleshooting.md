---
title: Troubleshooting
audience: [external-contributor, maintainer]
content_mode: troubleshooting
track: developer-docs
last_updated: 2026-06-06
---

# Troubleshooting

Common failure modes a contributor or operator hits while working on
`claude-shared`. Each entry uses the canonical `symptom` / `cause` /
`workaround` / `resolution` vocabulary.

## Skills don't appear after editing them

- **Symptom**: a new or changed `/nolte-shared:<skill>` doesn't show up in the
  session.
- **Cause**: the plugin was loaded before the change, and the session still holds
  the old definition.
- **Workaround**: run `/reload-plugins` inside the session to pick up changes.
- **Resolution**: launch the session with `claude --plugin-dir .` from the repo
  so edits are loaded from the working tree (see
  [Installation](../getting-started/installation.md)).

## `task docs` / `mkdocs build --strict` fails

- **Symptom**: the docs build exits non-zero, often on a missing frontmatter key,
  a broken link, or an unresolved include marker.
- **Cause**: a page under `docs/<lang>/` is missing one of the five required
  frontmatter keys, a new page lacks its counterpart in the other language tree,
  or an `include-markdown` start/end marker no longer exists in the source.
- **Workaround**: read the strict-mode error; it names the offending file and
  reason.
- **Resolution**: add the missing frontmatter (`title`, `audience`,
  `content_mode`, `track`, `last_updated`), create the missing language
  counterpart at the same relative path, or fix the include marker — then
  rebuild.

## Pre-commit / Vale blocks the commit

- **Symptom**: `git commit` is rejected by a pre-commit hook (whitespace, YAML,
  Markdown, or a Vale prose finding).
- **Cause**: the hooks weren't installed, or the prose violates the pinned
  `nolte/vale-style` vocabulary.
- **Workaround**: run `task lint` to see every finding before committing.
- **Resolution**: run `task setup` once after cloning to install the hooks, then
  fix each reported finding; for genuine vocabulary gaps follow
  [Contributing](contributing.md).

## You're on a feature branch in the primary checkout

- **Symptom**: the pre-commit guard refuses the commit because the primary
  checkout (`~/repos/github/claude-shared/`) is on a feature branch.
- **Cause**: feature work was started in the integration-only primary checkout
  instead of a worktree.
- **Workaround**: stop committing in the primary checkout.
- **Resolution**: migrate the branch into a worktree (`task worktree:add --
  <branch> [slug]`) and reset the primary checkout to `origin/develop`, per
  `CLAUDE.md` §Parallel working copies.

## Sources

- `spec/project/mkdocs-structure/` §Build verification
- `spec/project/parallel-working-copies/` — the primary-checkout guard
- [Contributing](contributing.md), [Installation](../getting-started/installation.md)
