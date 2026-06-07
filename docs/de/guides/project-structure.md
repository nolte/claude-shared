---
title: Projektstruktur
audience: [external-contributor, maintainer]
content_mode: reference
track: developer-docs
last_updated: 2026-05-29
---

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
| Agent-Quellen | `agents/<name>.md` (einzelne, in sich geschlossene Datei; kein Schwester-Ordner) |
| Spezifikationen | `spec/<topic>/<slug>/<lang>.md` |
| Spec-Config | `spec/.spec-config.yml` |
| Spec-Index | `spec/README.md` (auto-generiert — nicht von Hand bearbeiten) |
| User-Dokumentation | `docs/<lang>/…` |

## Sprachen

- **Skill- und Agent-Inhalte**: Englisch — das senkt Claudes Verarbeitungskosten. Skills/Agents dürfen Claude dennoch anweisen, dem Nutzer in dessen Sprache zu antworten.
- **Spezifikationen**: kanonisch EN, Übersetzung DE, strukturell synchron.
- **Dokumentation (`docs/`)**: DE und EN, über `mkdocs-static-i18n`.

## Plugin-Namespace

Das Plugin heißt `nolte-shared` (siehe `.claude-plugin/plugin.json`). Skills sind entsprechend als `/nolte-shared:<skill>` aufrufbar. Der Plugin-Name bleibt stabil — er ist Teil aller Aufrufe und Dokumentationen.

## Tech-Stack

Das Repository ist ein Dokumentations- und Automatisierungsprojekt, keine kompilierte Anwendung: Es gibt keinen Laufzeit-Service, sondern nur ein Claude-Code-Plugin samt der Werkzeuge, die es autorisieren, linten und veröffentlichen. Das kanonische Inventar dieser Bausteine — jeweils mit `kind`, `group`, Rolle und Source-of-Truth-Datei — ist die handgepflegte Portfolio-Quelle `portfolio/tech-stack.yml` (geregelt durch `spec/portfolio/tech-stack/`); die Liste unten spiegelt sie und darf nicht davon abweichen.

| Komponente | Rolle | Source of Truth |
|------------|-------|-----------------|
| Python | Laufzeit für die Validierungs-, Katalog-Generierungs- und Journal-Skripte unter `scripts/` | `scripts/` |
| MkDocs (Material + static-i18n) | Dokumentationsgenerator, der die zweisprachige Site unter `docs/` erzeugt | `mkdocs.yml` |
| Task | Task-Orchestrator für die Quality-Gate-, Docs-, Lint- und Dogfooding-Targets | `Taskfile.yml` |
| Vale | Prosa-Linter mit den gepinnten `nolte/vale-style`-Vokabularen | `.vale.ini` |
| pre-commit | Hook-Framework, das Whitespace-, YAML-, Markdown- und Vale-Checks verdrahtet | `.pre-commit-config.yaml` |
| Renovate | Automatischer Dependency-Update-Bot, der das `nolte/gh-plumbing`-Preset erweitert | `renovate.json5` |
| GitHub Actions | CI-Provider für die Lint-, Test-, Docs- und Release-Workflows | `.github/workflows/` |

Pinning-Absicht: Jedes MkDocs-Plugin ist in `docs/requirements.txt` gepinnt, der Vale-Style ist in `.vale.ini` auf ein `nolte/vale-style`-Release gepinnt, und die wiederverwendbaren CI-Workflows pinnen ihre `nolte/gh-plumbing`-Version. Projektlokale Ergänzungen über der Portfolio-Basis sind oben inline neben der kanonischen Quelle gelistet.

## Quellen

- `portfolio/tech-stack.yml` — kanonisches Portfolio-Tech-Stack-Inventar (gemäß `spec/portfolio/tech-stack/`)
- `Taskfile.yml`, `mkdocs.yml`, `.vale.ini`, `.pre-commit-config.yaml` — die oben referenzierten Source-of-Truth-Dateien je Komponente
