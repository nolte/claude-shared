# Beitragen

## Workflow

1. **Spec zuerst lesen** — Skill oder Agent folgt immer einer geltenden Spezifikation.
2. **Skill/Agent anlegen** — nutze den [Skill-Management](../skills/nolte-shared/skill-management.md)-Skill. Er scaffolden ASCII-Kebab-Case-Ordner, schreibt valides Frontmatter und verhindert typische Fehler.
3. **Spec anpassen, wenn nötig** — über den [Spec-Skill](../skills/nolte-shared/spec.md). Niemals Übersetzungen direkt bearbeiten; der Kanon (EN) ist die Wahrheit, alles andere wird aus ihm regeneriert.
4. **Validieren lassen** — `skill-management` im Validierungsmodus. Mechanische Defekte (Frontmatter-Mismatch, absolute Pfade, fehlende Hard-Rules) werden angeboten zu fixen.
5. **Index aktualisieren** — nach Änderungen an Specs: `spec/README.md` via Spec-Skill regenerieren.

## Konventionen

- **Namen**: ASCII-Kebab-Case.
- **Beschreibungen**: konkrete User-Trigger ("einsetzen, wenn der Nutzer X sagt"), keine abstrakten Fähigkeiten.
- **Tool-Zugriff bei Agents**: Prinzip der minimalen Rechte. Read-only = keine Schreib-Tools.
- **Keine absoluten Pfade** in Skill- oder Agent-Inhalten.
- **Inhaltssprache**: Skills und Agents in Englisch, User-Antwort in Nutzersprache.

## Commits

- Kurze, imperativen Subject-Zeilen ("add spec skill template").
- Eine logische Änderung pro Commit. Spec-Änderungen (alle Sprachen + Index-Update) bleiben **zusammen** in einem Commit, damit der Kanon nie ohne Übersetzungen auf den Branch wandert.

## Pull Requests

- Verlinke die betroffene Spec.
- Beschreibe, welche Skills/Agents neu oder geändert sind.
- Führe aus, was du getestet hast (z. B. "Plugin via `claude --plugin-dir .` geladen, `/nolte-shared:spec` erscheint im `/skills`-Dialog").

## Häufige Fallstricke

- **Übersetzung direkt editiert** → Drift. Immer Kanon ändern und regenerieren.
- **Platzhalter-Subfolder angelegt** → der Skill-Management-Skill verbietet leere Ordner "just in case".
- **`description` zu vage** → Claude kann die Skill/Agent nicht zuverlässig routen. Mindestens drei konkrete Phrasen.
- **`tools` zu großzügig bei Agents** → lesende Agents bekommen keine Schreib-/Ausführungs-Tools, auch nicht "für später".
