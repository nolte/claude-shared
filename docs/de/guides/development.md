---
title: Entwicklung
audience: [external-contributor, maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-19
---

# Entwicklung

Diese Sektion richtet sich an Mitwirkende, die am `claude-shared`-Repository selbst arbeiten — neue Skills, neue Agents oder Pflege der Spezifikationen.

- [Projektstruktur](project-structure.md) — wo liegt was und warum
- [Beitragen](contributing.md) — Workflow, Konventionen, Commits

## Dogfooding

Beim Arbeiten am Repository startest du Claude Code mit dem Plugin auf dem Repo-Root:

```bash
claude --plugin-dir .
```

`/reload-plugins` übernimmt Änderungen während der Session.

## Zuerst die Spec

Bevor ein neuer Skill oder Agent geschrieben wird: die passende Spezifikation lesen.

- [Skill-Autorenschaft](../references/specs/skill-management.md)
- [Agent-Autorenschaft](../references/specs/agent-management.md)

Neue Skills erstellt du mit dem [Skill-Management](../skills/nolte-claude-dev/skill-management.md)-Skill selbst — das garantiert Konformität.
