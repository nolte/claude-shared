---
title: Nach Aufgabe
audience: [maintainer]
content_mode: meta
track: developer-docs
last_updated: 2026-05-26
---

# Nach Aufgabe

Aufgaben-orientierte Einstiegs-Seite: gruppiert Skills und Agents nach Nutzer-Absicht statt nach Phase des Liefer-Lebenszyklus. Hand-kuratiert; Rubriken wachsen, sobald weitere Artefakte `use_when`-Metadaten ausspielen.

> **Hinweis:** Bislang erscheinen hier nur die pilot-migrierten Artefakte. Was noch nicht gelistet ist, findest du im phasen-gruppierten [Skills](skills/index.md)- und [Agents](agents/index.md)-Index oder über den [Tag-Index](references/tags.md).

## Pull Request öffnen oder landen

- **Draft-PR auf dem aktuellen Feature-Branch öffnen** → [`pull-request-create`](skills/nolte-shared/pull-request-create.md). Prüft, dass der Branch mit `develop` synchron ist, komponiert Conventional-Commits-Titel und den fünfteiligen Body, autolinkt berührte Specs, ruft anschließend `gh pr create`.
- **Bereits offenen Draft-PR auf `develop` landen** → [`pull-request-merge`](skills/nolte-shared/pull-request-merge.md). Delegiert Pre-Merge-Review, leitet Labels aus Commit-Typ und berührten Pfaden ab, flippt draft → ready, setzt `automerge`, verifiziert den Squash-Merge-Commit.

## Spezifikation verfassen oder prüfen

- **Eine Spec unter `spec/` schreiben, übersetzen oder auffrischen** → [`spec`](skills/nolte-shared/spec.md). Hält jede konfigurierte Sprachbaum-Variante mit der kanonischen Quelle synchron, regeneriert den Spec-Index, dedupliziert gegen bestehende Coverage.
- **Eine Spec vor der Downstream-Implementierung prüfen** → [`spec-readiness-reviewer`](agents/nolte-shared/spec-readiness-reviewer.md). Nur-Lese-Audit auf Widersprüche, Audience-Fit, Requirement-↔-AC-Coverage (AC, Acceptance Criteria) und Ghost-Referenzen auf nicht existierende Specs. Severity-sortierter Report; editiert nie.

## Einen Claude-Code-Skill verfassen

- **Einen `nolte-shared`-Skill-Ordner scaffolden oder überarbeiten** → [`skill-management`](skills/nolte-claude-dev/skill-management.md). Schreibt das `SKILL.md`-Template mit gültiger Frontmatter und kettet anschließend zu `claude-plugin-developer` für den spec-konformen Body-Entwurf.

## Skill oder Agent wählen

Wenn die Aufgabe plausibel in beiden Formen leben könnte, lies zuerst die [skill-vs-agent-Spec](https://github.com/nolte/claude-shared/blob/main/spec/claude/skill-vs-agent/de.md) — sie hält die Entscheidungsdimensionen fest (Orchestrierung vs. Spezialisierung, Kontext-Fenster-Druck, Parallelität, Interaktivität), die die Wahl treiben.
