# Skills

Skills sind wiederverwendbare Workflows, die Claude Code über das `Skill`-Tool aufruft. Im Quellbaum von `claude-shared` liegen sie unter `skills/<name>/SKILL.md`, zur Laufzeit in einem konsumierenden Projekt unter `.claude/skills/<name>/` oder `~/.claude/skills/<name>/` — oder, wie hier, als Teil des `nolte-shared`-Plugins.

## Enthaltene Skills

| Skill | Beschreibung |
|-------|--------------|
| [Skill-Management](skill-management.md) | Neue Skills anlegen und bestehende gegen die Spec validieren |
| [Spec](spec.md) | Mehrsprachige Spezifikationen verwalten (DE/EN), Drift erkennen, Index pflegen |

## Struktur eines Skills

```
skills/<name>/
├── SKILL.md              # YAML-Frontmatter + Anweisungen
├── templates/            # optional
├── references/           # optional
└── examples/             # optional
```

Das Frontmatter jedes Skills enthält mindestens:

```yaml
---
name: <ordnername>
description: Konkrete Trigger-Phrasen, nicht abstrakte Fähigkeiten.
---
```

Details zu Regeln und Akzeptanzkriterien: [Skill-Autorenschaft](../specs/skill-management.md).
