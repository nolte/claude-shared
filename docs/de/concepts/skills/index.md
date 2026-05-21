---
title: Skills
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-19
---

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
| `mermaid-diagrams-apply` | MkDocs-Mermaid-Setup gegen die `mermaid-diagrams`-Spec auditieren und Diagramme spec-konform einfügen |
| `vocab-drift-audit` | Repo-lokales Vale-Vocabulary gegen den gepinnten `nolte/vale-style`-Release diffen |
| `workflow-health-triage` | Failing GitHub-Actions-Workflow triagieren laut `workflow-health`-Spec; klassifizieren, spezialisierten Agent dispatchen, Fix durch Standard-PR-Flow routen |
| `permission-allowlist-maintain` | Die committete `.claude/settings.json` `permissions.allow`-Liste laut `permission-allowlist`-Spec kuratieren; user-gegateter Per-Eintrag-Approval |
| `audience-identify` | Zielgruppen eines Bounded Contexts identifizieren und als Artefakt ablegen |
| `mission-define` | Erstes Schreiben von `project/mission.md` mit SMART-Vertrag pro Buchstabe |
| `mission-revise` | `project/mission.md` editieren plus `mvp_status`-Lifecycle-Flips per `mission`-Spec |
| `roadmap-init` | `project/goals.md` und `project/roadmap.md` initial scaffolden (Vision plus Outcomes plus leere Queue) |
| `roadmap-refine` | Detail-Level-Invariante in `project/roadmap.md` durchsetzen, Verstöße strukturiert melden |
| `roadmap-plan` | Roadmap-Items hinzufügen, promovieren, neu zuordnen; `mvp`-Flag flippen |
| `feature-decompose` | Roadmap-Item in `project/features/<slug>.md` zerlegen, Konsistenzcheck via `feature-consistency-reviewer` |
| `sprint-plan` | `project/sprints/<NNNN>-<slug>.md` mit `value_statement` und `verifies_sprint_value` anlegen |
| `sprint-execute` | Sprint-Lifecycle treiben: `planned → active`, Feature-Übergänge, `last_commit` aktualisieren |
| `sprint-review` | Sprint mit Artefakt-Validation schließen, optional Release-Skill-Layer chainen |

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

Details zu Regeln und Akzeptanzkriterien: [Skill-Autorenschaft](../../specs/skill-management.md).
