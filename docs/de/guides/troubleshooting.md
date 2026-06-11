---
title: Fehlerbehebung
audience: [external-contributor, maintainer]
content_mode: troubleshooting
track: developer-docs
last_updated: 2026-06-06
---

# Fehlerbehebung

Häufige Fehler, auf die Mitwirkende oder Betreiber bei der Arbeit an
`claude-shared` stoßen. Jeder Eintrag nutzt das kanonische Vokabular
`symptom` / `cause` / `workaround` / `resolution`.

## Skills erscheinen nach dem Bearbeiten nicht

- **Symptom**: ein neuer oder geänderter `/nolte-shared:<skill>` taucht in der
  Session nicht auf.
- **Cause**: das Plugin wurde vor der Änderung geladen, und die Session hält noch
  die alte Definition.
- **Workaround**: `/reload-plugins` in der Session ausführen, um Änderungen zu
  übernehmen.
- **Resolution**: die Session mit `claude --plugin-dir .` aus dem Repo starten.
  Dann werden Edits aus dem Arbeitsbaum geladen (siehe
  [Installation](../getting-started/installation.md)).

## `task docs` / `mkdocs build --strict` schlägt fehl

- **Symptom**: der Docs-Build endet mit Exit-Code ungleich null, oft wegen eines
  fehlenden Frontmatter-Schlüssels, eines kaputten Links oder eines nicht
  aufgelösten Include-Markers.
- **Cause**: Einer Seite unter `docs/<lang>/` fehlt einer der fünf
  Pflicht-Frontmatter-Schlüssel. Oder eine neue Seite hat kein Gegenstück im
  anderen Sprachbaum. Oder ein `include-markdown`-Start-/End-Marker existiert in
  der Quelle nicht mehr.
- **Workaround**: die Strict-Mode-Fehlermeldung lesen; sie nennt die betroffene
  Datei und den Grund.
- **Resolution**: das fehlende Frontmatter ergänzen (`title`, `audience`,
  `content_mode`, `track`, `last_updated`), das fehlende Sprach-Gegenstück am
  selben relativen Pfad anlegen oder den Include-Marker korrigieren — dann neu
  bauen.

## Pre-commit / Vale blockiert den Commit

- **Symptom**: `git commit` wird von einem Pre-commit-Hook abgelehnt
  (Whitespace, YAML, Markdown oder ein Vale-Prosa-Befund).
- **Cause**: die Hooks wurden nicht installiert, oder die Prosa verletzt das
  gepinnte `nolte/vale-style`-Vokabular.
- **Workaround**: `task lint` ausführen, um vor dem Commit jeden Befund zu sehen.
- **Resolution**: nach dem Klonen einmalig `task setup` ausführen, um die Hooks
  zu installieren, dann jeden gemeldeten Befund beheben; bei echten
  Vokabular-Lücken siehe [Beitragen](contributing.md).

## Du bist im Hauptordner auf einem Feature-Branch

- **Symptom**: der Pre-commit-Guard verweigert den Commit, weil der Hauptordner
  (`~/repos/github/claude-shared/`) auf einem Feature-Branch steht.
- **Cause**: Feature-Arbeit wurde im reinen Integrations-Hauptordner statt in
  einem Worktree begonnen.
- **Workaround**: keine Commits mehr im Hauptordner ausführen.
- **Resolution**: den Branch in einen Worktree migrieren (`task worktree:add --
  <branch> [slug]`) und den Hauptordner auf `origin/develop` zurücksetzen, gemäß
  `CLAUDE.md` §Parallel working copies.

## Quellen

- `spec/project/mkdocs-structure/` §Build verification
- `spec/project/parallel-working-copies/` — der Hauptordner-Guard
- [Beitragen](contributing.md), [Installation](../getting-started/installation.md)
