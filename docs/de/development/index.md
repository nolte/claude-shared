---
title: Entwicklung
audience: [external-contributor, maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-19
---

# Entwicklung

Diese Sektion richtet sich an Mitwirkende, die am `claude-shared`-Repository selbst arbeiten — neue Skills, neue Agents oder Pflege der Spezifikationen.

- [Projektstruktur](projektstruktur.md) — wo liegt was und warum
- [Beitragen](beitragen.md) — Workflow, Konventionen, Commits

## Dogfooding

Beim Arbeiten am Repository startest du Claude Code mit dem Plugin auf dem Repo-Root:

```bash
claude --plugin-dir .
```

`/reload-plugins` übernimmt Änderungen während der Session.

## Zuerst die Spec

Bevor ein neuer Skill oder Agent geschrieben wird: die passende Spezifikation lesen.

- [Skill-Autorenschaft](../specs/skill-management.md)
- [Agent-Autorenschaft](../specs/agent-management.md)

Neue Skills erstellt du mit dem [Skill-Management](../skills/nolte-shared/skill-management.md)-Skill selbst — das garantiert Konformität.
