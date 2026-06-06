---
title: Specifications
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-19
---

# Specifications

The specifications under `spec/` define the binding rules for skill and agent authors. They're **multilingual**: canonical in English, translated to German, kept structurally and semantically in sync via the [Spec skill](../../skills/nolte-shared/spec.md).

## Existing specs

The authoritative, always-current list lives in [`spec/README.md`](https://github.com/nolte/claude-shared/blob/develop/spec/README.md) and is maintained by the [Spec skill](../../skills/nolte-shared/spec.md); it lists every spec with topic, slug, language titles, status and last-update date.

Rough map for orientation:

- **`spec/claude/`**: rules for authors of skills and agents (includes `skill-management`, `agent-management`, `skill-vs-agent`, `skill-review`, `agent-review`, `skill-agent-catalog`, `permission-allowlist`, `review-plan`)
- **`spec/project/`**: rules for project and release conventions (includes `project-structure`, `github-issue-templates`, `pull-request-workflow`, `parallel-working-copies`, `branching-model`, `release-automation`, `release-artifact`, `release-skill-layer`, `release-notes-audience-analysis`, `quality-gate`, `dependency-audit`, `workflow-health`, `docs-freshness`, `mermaid-diagrams`, `readme-structure`, `prose-style`, `spec-drift-audit`, `spec-driven-development`, `spec-readiness`, `audience-identification`, `mission`, `roadmap`, `sprint`, `feature`, `continuous-improvement`)

Detail pages in this documentation currently exist for `skill-management` and `agent-management`; more are being added.

## RFC 2119 conventions

Normative statements use RFC 2119 (Request for Comments 2119) keywords. Translations keep the English form as a gloss:

- `MUST` → `MUSS [MUST]`
- `MUST NOT` → `DARF NICHT [MUST NOT]`
- `SHOULD` → `SOLLTE [SHOULD]`
- `SHOULD NOT` → `SOLLTE NICHT [SHOULD NOT]`
- `MAY` → `KANN [MAY]`

## Contributing to specs

New spec or change? Always go through the [Spec skill](../../skills/nolte-shared/spec.md): that's the only way canonical, translations and index stay in sync. Direct edits to translations are the single most common drift source and will be flagged at the next drift check.
