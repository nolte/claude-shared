# Projektstruktur

Aktueller Top-Level-Aufbau:

```
claude-shared/
├── .claude/                 # lokale Claude-Code-Einstellungen (nicht paketiert)
├── .claude-plugin/
│   └── plugin.json          # Plugin-Manifest: name, version, author, repo
├── skills/
│   ├── skill-management/
│   │   └── SKILL.md
│   └── spec/
│       ├── SKILL.md
│       └── templates/
│           └── spec.template.md
├── spec/
│   ├── .spec-config.yml
│   ├── README.md            # auto-generierter Index
│   └── claude/
│       ├── agent-management/
│       │   ├── en.md        # kanonisch
│       │   └── de.md
│       └── skill-management/
│           ├── en.md
│           └── de.md
├── docs/                    # MkDocs-Quellen (diese Seite)
├── mkdocs.yml
└── README.md
```

Geplant, aber noch nicht angelegt:

```
agents/                      # wiederverwendbare Sub-Agent-Definitionen
```

## Was wohin gehört

| Inhalt | Ort |
|--------|-----|
| Plugin-Manifest | `.claude-plugin/plugin.json` |
| Skill-Quellen | `skills/<name>/` |
| Skill-Templates/Refs | `skills/<name>/templates/`, `references/`, `examples/` |
| Agent-Quellen | `agents/<name>.md` (+ `agents/<name>/` für Beispiele) |
| Spezifikationen | `spec/<topic>/<slug>/<lang>.md` |
| Spec-Config | `spec/.spec-config.yml` |
| Spec-Index | `spec/README.md` (auto-generiert — nicht von Hand bearbeiten) |
| User-Dokumentation | `docs/<lang>/…` |

## Sprachen

- **Skill- und Agent-Inhalte**: Englisch (Token-Effizienz; die Skills/Agents dürfen Claude dennoch anweisen, dem Nutzer in dessen Sprache zu antworten).
- **Spezifikationen**: kanonisch EN, Übersetzung DE, strukturell synchron.
- **Dokumentation (`docs/`)**: DE und EN, über `mkdocs-static-i18n`.

## Plugin-Namespace

Das Plugin heißt `nolte-shared` (siehe `.claude-plugin/plugin.json`). Skills sind entsprechend als `/nolte-shared:<skill>` aufrufbar. Der Plugin-Name ändert sich nicht leichtfertig — er ist Teil aller Aufrufe und Dokumentationen.
