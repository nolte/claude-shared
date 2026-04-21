# Spec

Der Skill `spec` verwaltet mehrsprachige Spezifikationen unterhalb von `spec/`. Pro Spec existiert ein Ordner mit genau einer Datei pro konfigurierter Sprache. Eine Sprache ist **kanonisch**, alle anderen sind strukturell und semantisch synchron gehaltene Übersetzungen.

## Wann einsetzen

- "schreib eine Spec für X", "neue Spezifikation"
- "ist X schon abgedeckt?" (Duplikat-Check)
- "übersetz die Spec" / "translate this spec"
- "Index neu bauen" / "regenerate the spec index"
- "Drift prüfen"

## Layout auf der Festplatte

```
spec/
├── .spec-config.yml
├── README.md                       # auto-generierter Index
└── [<topic>/]<slug>/
    ├── en.md                       # kanonisch
    └── de.md                       # Übersetzung
```

Topic-Ordner gruppieren verwandte Specs (z. B. `spec/claude/`, `spec/api/`). **Genau eine Ebene** Topic-Nesting ist erlaubt; ohne Topic liegt die Spec direkt unter `spec/<slug>/`.

## Defaults und Konfiguration

| Schlüssel | Default |
|-----------|---------|
| `canonical_language` | `en` |
| `languages` | `[en, de]` |
| `spec_root` | `spec` |

Überschreibbar via `spec/.spec-config.yml`:

```yaml
canonical_language: en
languages: [en, de]
spec_root: spec
```

Fehlt die Datei, greifen die Defaults. Beim ersten `create` wird sie angelegt, damit Downstream-Projekte einen sichtbaren Erweiterungspunkt haben.

## Operationen

### Create

1. Nutzerbeschreibung entgegennehmen (beliebige Sprache).
2. **Duplikat-Check zuerst** — klare Überlappung → abbrechen und fragen: erweitern, ablösen, oder als neu anlegen.
3. Kanonische Spec aus `templates/spec.template.md` entwerfen, jede Section mit User-Input füllen, Unbekanntes explizit markieren (nicht erfinden).
4. In alle übrigen Sprachen übersetzen. Struktur bleibt identisch. RFC-2119-Keywords bleiben englisch und werden in-Sprache glossiert, z. B. `MUSS [MUST]`, `SOLLTE [SHOULD]`, `KANN [MAY]`.
5. Alle Sprachdateien in **einem** Schritt schreiben — nie teilfertig.
6. Index regenerieren.

### Update / Drift verhindern

- Kanonische Version ist einzige Wahrheitsquelle.
- Edit an kanonischer Version → alle Übersetzungen regenerieren.
- Edit direkt an Übersetzung → warnen. Optionen: (a) semantische Änderung in Kanon heben und regenerieren, (b) Übersetzungs-Edit verwerfen und aus Kanon regenerieren.

### Drift Check

Prüft pro Spec-Ordner:

- gleiche Überschriften, gleiche Reihenfolge
- gleiche Anzahl Requirements-Bullets und Akzeptanzkriterien-Checkboxes
- gleiche Requirement-IDs / Reihenfolge

Mismatches werden gemeldet; Regenerieren betroffener Übersetzungen wird angeboten.

### Index regenerieren

`spec/README.md` wird neu geschrieben mit Tabelle: Slug | Titel (pro Sprache) | Status | Last updated.

- `Status` aus der `Status:`-Zeile der kanonischen Datei; fehlt diese, gilt `draft`.
- `Last updated` via `git log -1 --format=%cs -- <canonical file>`; bei untracked Dateien `unversioned`.
- Nichts erfinden — was nicht lesbar ist, wird `unknown`.

### Coverage / Duplikat-Check

Standalone oder als Schritt 2 von Create:

1. Salient nouns/verbs aus dem Requirement extrahieren.
2. `Grep` über kanonische Dateien unter `spec/`.
3. `Read` jeder kanonischen Datei mit mehr als einem Keyword-Treffer; **semantische** Überlappung beurteilen, nicht reine Keyword-Gleichheit.
4. Antwort in Nutzersprache: voll abgedeckt / teilweise (mit Lücke) / keine Überlappung.

## Hard Rules

- Kanon und Übersetzungen werden **immer zusammen** angelegt und aktualisiert.
- Nach jeder Änderung: Übersetzungen sind synchron zum Kanon — kein Drift.
- Slugs sind ASCII-Kebab-Case und ändern sich nie still.
- `spec/.spec-config.yml` nicht ohne Ansage ändern.
- `Status`, Datumsangaben und Requirement-Inhalte nie erfinden — lesen oder als unbekannt markieren.

## Quellen

- Skill-Datei: `skills/spec/SKILL.md`
- Template: `skills/spec/templates/spec.template.md`
