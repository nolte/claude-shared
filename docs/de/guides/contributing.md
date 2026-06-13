---
title: Beitragen
audience: [external-contributor]
content_mode: how-to
track: developer-docs
last_updated: 2026-05-19
---

# Beitragen

**Voraussetzung:** Plugin lokal geladen (siehe [Installation](../getting-started/installation.md)). Erst dann sind `skill-management` und der `spec`-Skill verfügbar.

## Setup und Voraussetzungen

Bevor du die Checks des Repos lokal ausführen kannst, brauchst du diese Tools. Das Repo ist reine Dokumentation und Automatisierung — es gibt keinen App-Build —, daher bleiben die Tools bewusst klein.

| Tool | Version | Wofür |
|------|---------|-------|
| Python | 3.x | Führt die Validierungs- und Katalog-Skripte unter `scripts/` sowie die Testsuite aus |
| Task | aktuell | Task-Runner; jeder Check ist als `task <target>` verfügbar (siehe `Taskfile.yml`) |
| pre-commit | aktuell | Hook-Framework, das Whitespace, YAML, Markdown und Vale absichert |
| Vale | aktuell | Prosa-Linter (zieht beim `vale sync` das gepinnte `nolte/vale-style`-Vokabular) |
| Git | 2.x | Worktree-basierter Workflow gemäß der Parallel-Working-Copies-Konvention |

Außerdem brauchst du ein GitHub-Konto mit Zugriff für Forks und Pull Requests (PRs); weitere externe Konten sind nicht erforderlich.

Erstmalige Bootstrap-Sequenz, einmal nach dem Klonen auszuführen:

```bash
task setup                              # installiert die pre-commit-Hooks
pip install -r evals/requirements-dev.txt   # Test-Suite-Abhängigkeiten (pytest)
```

Nach dem Bootstrap sind die alltäglichen Checks:

```bash
task lint     # pre-commit über alle Dateien
task test     # Skill-/Agent-Frontmatter-Validierung + Eval-Harness-Unit-Tests
task check    # das develop-Quality-Gate lokal: lint + test
task docs     # baut die zweisprachige MkDocs-Site (mkdocs build --strict)
```

Wer `task check` sauber durchläuft, hat ein lauffähiges Repo.

## Workflow

1. **Spec zuerst lesen** — Skill oder Agent folgt immer einer geltenden [Spezifikation](../references/specs/index.md).
2. **Skill/Agent anlegen** — nutze den [Skill-Management](../skills/nolte-shared/skill-management.md)-Skill. Er legt ASCII-Kebab-Case-Ordner an, schreibt valides Frontmatter und verhindert typische Fehler.
3. **Spec anpassen, wenn nötig** — über den [Spec-Skill](../skills/nolte-shared/spec.md). Übersetzungen niemals direkt editieren. Der englische Kanon (die maßgebliche EN-Quelldatei) ist die Wahrheit; alles andere wird aus ihm regeneriert.
4. **Validieren lassen** — `skill-management` im Validierungsmodus prüft mechanische Defekte (Frontmatter-Mismatch, absolute Pfade, fehlende Hard-Rules) und bietet Fixes an.
5. **Index aktualisieren** — nach Änderungen an Specs: `spec/README.md` via Spec-Skill regenerieren.

## Konventionen

- **Namen**: ASCII-Kebab-Case.
- **Beschreibungen**: konkrete User-Trigger ("einsetzen, wenn der Nutzer X sagt"), keine abstrakten Fähigkeiten.
- **Tool-Zugriff bei Agents**: Prinzip der minimalen Rechte. Nur-Lese-Agents erhalten keine Schreib-Tools.
- **Keine absoluten Pfade** in Skill- oder Agent-Inhalten.
- **Inhaltssprache**: Skills und Agents in Englisch, User-Antwort in Nutzersprache.

## Commits

- Kurze, imperative Betreff-Zeilen ("add spec skill template").
- Eine logische Änderung pro Commit. Spec-Änderungen (alle Sprachen + Index-Update) bleiben **zusammen** in einem Commit, damit der englische Kanon nie ohne seine Übersetzungen auf den Branch wandert.

## Pull Requests

- Verlinke die betroffene Spec.
- Beschreibe, welche Skills/Agents neu oder geändert sind.
- Führe aus, was du getestet hast (z. B. "Plugin via `claude --plugin-dir .` geladen, `/nolte-shared:spec` erscheint im `/skills`-Dialog").

## Häufige Fallstricke

- **Übersetzung direkt editiert** → Drift. Immer Kanon ändern und regenerieren.
- **Platzhalter-Subfolder angelegt** → der Skill-Management-Skill verbietet leere Ordner "just in case".
- **`description` zu vage** → Claude kann die Skill/Agent nicht zuverlässig routen. Mindestens drei konkrete Phrasen.
- **`tools` zu großzügig bei Agents** → lesende Agents bekommen keine Schreib-/Ausführungs-Tools, auch nicht "für später".
