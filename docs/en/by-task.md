---
title: By task
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-26
---

# By task

Task-oriented landing page: groups skills and agents by user intent rather than by delivery-lifecycle phase. Hand-curated; rubrics grow as more artifacts expose `use_when` metadata.

> **Note:** Only the pilot-migrated artifacts currently appear here. For anything not yet listed, browse the phase-grouped [Skills](skills/index.md) and [Agents](agents/index.md) indexes, or the [Tag index](references/tags.md) for thematic browsing.

## Open or land a pull request

- **Open a draft PR on the current feature branch** → [`pull-request-create`](skills/nolte-shared/pull-request-create.md). Verifies the branch is in sync with `develop`, composes a Conventional-Commits title and the five-section body, autolinks any touched specs, then runs `gh pr create`.
- **Land an already-open draft PR on `develop`** → [`pull-request-merge`](skills/nolte-shared/pull-request-merge.md). Delegates pre-merge review, derives labels from the commit type and touched paths, flips draft → ready, applies `automerge`, and verifies the squash-merge commit landed.

## Author or audit a specification

- **Write, translate, or refresh a spec under `spec/`** → [`spec`](skills/nolte-shared/spec.md). Keeps every configured language tree in sync with the canonical source, regenerates the spec index, and de-duplicates against existing coverage.
- **Audit a spec before downstream implementation** → [`spec-readiness-reviewer`](agents/nolte-shared/spec-readiness-reviewer.md). Read-only audit for contradictions, audience fit, requirement-to-AC coverage, and ghost references to non-existent specs. Severity-sorted report; never edits.

## Author a Claude Code skill

- **Scaffold or revise a `nolte-shared` skill folder** → [`skill-management`](skills/nolte-shared/skill-management.md). Writes the `SKILL.md` template with valid frontmatter, then chains to `claude-plugin-developer` for the spec-conformant body draft.

## Pick a skill vs. an agent

When the task could plausibly live in either form, read the [skill-vs-agent spec](https://github.com/nolte/claude-shared/blob/main/spec/claude/skill-vs-agent/en.md) first—it captures the decision dimensions (orchestration vs. specialisation, context-window pressure, parallelism, interactivity) that drive the choice.
