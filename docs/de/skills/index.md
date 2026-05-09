# Skills

Skills sind wiederverwendbare Workflows, die Claude Code über das `Skill`-Tool aufruft. Im Quellbaum von `claude-shared` liegen sie unter `skills/<name>/SKILL.md`, zur Laufzeit in einem konsumierenden Projekt unter `.claude/skills/<name>/` oder `~/.claude/skills/<name>/` — oder, wie hier, als Teil des `nolte-shared`-Plugins.

## Enthaltene Skills

| Skill | Beschreibung |
|-------|--------------|
| [`spec`](spec.md) | Mehrsprachige Spezifikationen verwalten (DE/EN), Drift erkennen, Index pflegen |
| [`skill-management`](skill-management.md) | Skills unter `skills/<name>/` anlegen oder überarbeiten |
| `skill-review` | Skill gegen die Autoren-Spec auditieren; Findings als Review-Plan persistieren |
| `agent-review` | Agent gegen die Autoren-Spec auditieren; Findings als Review-Plan persistieren |
| `pull-request-create` | PR nach `pull-request-workflow`-Spec eröffnen |
| `pull-request-merge` | Offenen Draft-PR auf `develop` promoten, Labels + Gates anwenden |
| `release-notes-curate` | Offenen Release-Drafter-Draft um einen Projektkontext-Abschnitt anreichern (per `release-skill-layer`) |
| `release-publish-trigger` | Pre-Publish-Gates validieren und `release-publish.yml` für den offenen Draft auf `develop` dispatchen |
| `quality-gate` | Lint + Typecheck + Tests parallel ausführen, Ergebnisse tabellieren |
| `dependency-audit` | Abhängigkeiten auf bekannte CVEs (optional Lizenzen) prüfen |
| `project-structure-apply` | Repo gegen die `project-structure`-Spec auditieren und fehlende Artefakte scaffolden |
| `github-issue-templates-apply` | `.github/ISSUE_TEMPLATE/` nach der `github-issue-templates`-Spec scaffolden oder aktualisieren |
| `skill-agent-catalog-apply` | MkDocs-Katalog für alle Skills und Agents eines Plugin-Repos einrichten |
| `vocab-drift-audit` | Repo-lokales Vale-Vocabulary gegen den gepinnten `nolte/vale-style`-Release diffen |
| `audience-identify` | Zielgruppen eines Bounded Contexts identifizieren und als Artefakt ablegen |

Detailseiten existieren aktuell für `skill-management` und `spec`; weitere werden nachgezogen. Die autoritative Quelle pro Skill ist jeweils `skills/<name>/SKILL.md` im Quellbaum.

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
