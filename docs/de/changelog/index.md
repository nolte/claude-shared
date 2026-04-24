# Changelog

Die autoritative Release-Historie ist die [GitHub-Releases-Seite](https://github.com/nolte/claude-shared/releases); dieser Changelog fasst nur die Hauptlinien pro Version zusammen.

## 0.2.0 (in Vorbereitung — erster veröffentlichter Release)

### Highlights

- Erster öffentlich publizierter Release des Plugins `nolte-shared`
- 12 Skills und 7 Agents gebündelt (siehe [Skills](../skills/index.md), [Agents](../agents/index.md))
- Review-Infrastruktur: `skill-review`, `agent-review`, `spec-readiness-reviewer`, `docs-freshness-checker`
- Release-Infrastruktur: Spec `release-automation` (Draft → Published ohne manuellen CLI-Eingriff), lokaler Übergangs-Workflow `release-publish.yml`
- Zielgruppen-Infrastruktur: Spec `audience-identification`, Skill `audience-identify`, Agents `audience-doc-author` und `audience-review`
- PR-Lifecycle: Skills `pull-request-create` und `pull-request-merge` entlang `pull-request-workflow`
- Qualitäts-Gates: `quality-gate`, `dependency-audit`, `vocab-drift-audit`

### Skills (neu gegenüber 0.1.0)

`skill-review`, `agent-review`, `pull-request-create`, `pull-request-merge`, `quality-gate`, `dependency-audit`, `project-structure-apply`, `skill-agent-catalog-apply`, `vocab-drift-audit`, `audience-identify`

### Agents (neu gegenüber 0.1.0)

`claude-plugin-developer`, `audience-doc-author`, `audience-review`, `spec-readiness-reviewer`, `docs-freshness-checker`, `prose-vale-curator`, `png-to-transparent-svg`

### Specs (neu gegenüber 0.1.0)

`skill-vs-agent`, `skill-review`, `agent-review`, `review-plan`, `skill-agent-catalog`, `permission-allowlist`, `pull-request-workflow`, `branching-model`, `release-automation`, `release-notes-audience-analysis`, `project-structure`, `quality-gate`, `dependency-audit`, `workflow-health`, `docs-freshness`, `readme-structure`, `prose-style`, `spec-drift-audit`, `spec-readiness`, `audience-identification`, `continuous-improvement`

## 0.1.0 (unveröffentlicht — Bootstrap)

### Plugin

- `.claude-plugin/plugin.json` — Plugin-Manifest `nolte-shared` v0.1.0

### Skills

- `skill-management` — Scaffolden und Validieren von Skills
- `spec` — mehrsprachige Specs verwalten (DE/EN), Drift-Check, Index-Regeneration

### Spezifikationen

- `spec/claude/skill-management/` — Claude Skill Authoring (draft)
- `spec/claude/agent-management/` — Claude Agent Authoring (draft)

### Dokumentation

- MkDocs-Setup mit `mkdocs-material` und `mkdocs-static-i18n`
- Deutsch und Englisch
- Sektionen: Startseite, Erste Schritte, Skills, Agents, Spezifikationen, Entwicklung, Changelog
