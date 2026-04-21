# Repository-Projektstruktur

Status: draft

## Kontext
Projekte in diesem Ökosystem haben eine wiedererkennbare Form auf der Festplatte: eine Python- (oder mehrsprachige) Codebasis mit MkDocs-Dokumentation, Taskfile-basierter Automatisierung, pre-commit- und Renovate-Hygiene, einem `spec/`-Ordner für Anforderungen und Claude-Code-Integration über `CLAUDE.md` und `.claude/`. Referenzimplementierungen sind [`nolte/kamerplanter`](https://github.com/nolte/kamerplanter) (mehrteiliges Repository mit Backend, Frontend, Knowledge Service und HA-Integration) und [`nolte/kamerplanter-ha`](https://github.com/nolte/kamerplanter-ha) (fokussierte Home-Assistant-Custom-Integration). Neue Repositories sollen denselben strukturellen Konventionen folgen, damit Tooling-Erwartungen, CI-Verdrahtung, Onboarding und KI-gestützte Workflows projektübergreifend gleich funktionieren.

## Ziele
- Jedes neue Git-Repository hat ein vorhersagbares Top-Level-Layout, durch das sich Menschen und KI-Agenten ohne projektspezifische Entdeckung orientieren können
- Gemeinsames Tooling (pre-commit, Renovate, MkDocs, Taskfile) ist konsistent und an denselben Stellen eingebunden
- Claude-Code-Integration (`CLAUDE.md`, `.claude/`) ist vom ersten Tag an vorhanden
- Die Form skaliert von einem Einzweck-Repository bis zum mehrteiligen Monorepo, ohne reorganisiert werden zu müssen
- Lokale Entwicklerkommandos und CI-Aufrufe laufen über dieselben Einstiegspunkte

## Nicht-Ziele
- Wahl der Programmiersprache (Python, TypeScript, Go etc.)
- Spezifische CI-Plattform-Features oder die Inhalte einzelner Workflow-Jobs
- Fach- oder Geschäftslogik
- Release-, Versionierungs- und Veröffentlichungsprozesse (separate Spec)
- Branching- bzw. Git-Flow-Konventionen (separate Spec)

## Anforderungen

### Top-Level-Dateien
- **MUSS [MUST]** eine `README.md` im Repository-Wurzelverzeichnis enthalten mit Projektvorstellung, Feature-Übersicht, Quickstart und Verweisen auf die vollständige Dokumentation
- **MUSS [MUST]** eine `.gitignore` enthalten
- **MUSS [MUST]** eine `CLAUDE.md` enthalten, die KI-gestützte Entwicklungs­konventionen, Architektur-Hinweise und Kommando-Einstiegspunkte des Repositories dokumentiert
- **MUSS [MUST]** eine `renovate.json5` (bevorzugt) oder `renovate.json` für automatisierte Abhängigkeits-Updates enthalten
- **MUSS [MUST]** eine `.pre-commit-config.yaml` enthalten, die für den Stack relevante Linter und Formatter fixiert
- **SOLLTE [SHOULD]** eine `LICENSE`-Datei im Wurzelverzeichnis enthalten, wenn das Repository veröffentlicht oder zur Weiterverbreitung gedacht ist

### Claude-Code-Integration
- **MUSS [MUST]** ein `.claude/`-Verzeichnis mit projektbezogener Claude-Code-Konfiguration enthalten (beliebige Kombination aus `agents/`, `skills/`, `commands/` und `settings*.json` je nach Bedarf)
- **MUSS [MUST]** `CLAUDE.md` und `.claude/` mit dem tatsächlich verwendeten Stand des Repositories synchron halten; veraltete Verweise gelten als Fehler

### CI und Automatisierung
- **MUSS [MUST]** ein `.github/`-Verzeichnis mit Workflows unter `.github/workflows/` enthalten
- **MUSS [MUST]** eine `Taskfile.yml` (oder `Taskfile.yaml`) im Repository-Wurzelverzeichnis enthalten, die reproduzierbare Kommandos mindestens für Test-, Lint- und Docs-Ziele bereitstellt
- **SOLLTE [SHOULD]** Lint-, Test- und Docs-Kommandos in der CI über Taskfile-Targets aufrufen, damit lokales Verhalten und CI-Verhalten identisch bleiben
- **SOLLTE [SHOULD]** CI-Status-Badges für die primären Workflows in der `README.md` anzeigen

### Dokumentation
- **MUSS [MUST]** ein `docs/`-Verzeichnis als MkDocs-Quelle enthalten
- **MUSS [MUST]** eine `mkdocs.yml` im Repository-Wurzelverzeichnis enthalten
- **SOLLTE [SHOULD]** die Dokumentation über einen CI-Workflow veröffentlichen (zum Beispiel GitHub Pages)
- **KANN [MAY]** `docs/` nach Sprache aufteilen (`docs/en/`, `docs/de/`, …), wenn mehrsprachige Dokumentation erforderlich ist

### Spezifikationen
- **MUSS [MUST]** ein `spec/`-Verzeichnis im Repository-Wurzelverzeichnis für Anforderungen, NFRs, Style Guides und Domänenwissen enthalten
- **SOLLTE [SHOULD]** `spec/` nach Themen-Unterordnern organisieren (zum Beispiel `req/`, `nfr/`, `ui-nfr/`, `style-guides/`, `knowledge/`), sobald mehr als eine Handvoll Specs existieren
- **KANN [MAY]** die Konvention des mehrsprachigen Spec-Skills (`<slug>/<lang>.md`) wiederverwenden, wenn das Projekt übersetzte Specs benötigt

### Tests
- **MUSS [MUST]** ein `tests/`-Verzeichnis im Repository-Wurzelverzeichnis enthalten
- **SOLLTE [SHOULD]** die Struktur des Quellbaums innerhalb von `tests/` spiegeln
- **KANN [MAY]** End-to-End-Tests in einem eigenen Unterordner wie `tests/e2e/` ablegen

### Quellcode-Layout
- **MUSS [MUST]** den primären Quellcode unter einem der folgenden konventionellen Layouts ablegen:
  - `src/` für eine Einzweck-Bibliothek oder einen Einzweck-Dienst
  - `src/<component>/` je Teilprojekt in einem mehrteiligen Repository (zum Beispiel `src/backend/`, `src/frontend/`, `src/knowledge-service/`)
  - `custom_components/<name>/` für eine Home-Assistant-Custom-Integration
- **MUSS NICHT [MUST NOT]** primäre Quellcode-Dateien lose im Repository-Wurzelverzeichnis halten; dort dürfen nur Tooling-Konfigurationen, Metadaten und kleine Skripte liegen
- **KANN [MAY]** einen `scripts/`- und/oder `tools/`-Ordner für repository-lokale Automatisierungs-Helfer enthalten

### Home-Assistant-Integrationen (optional)
- **KANN [MAY]** eine `hacs.json` im Repository-Wurzelverzeichnis enthalten, wenn das Repository eine HA-Custom-Integration ausliefert
- **MUSS [MUST]** Integrations­code in `custom_components/<domain>/` ablegen und dabei die lowercase-ASCII-HA-Domain der Integration als Ordnernamen verwenden, wenn `hacs.json` vorhanden ist
- **KANN [MAY]** eine `info.md` für HACS-gerenderte Repository-Metadaten enthalten

### Containerisierung und Orchestrierung (optional)
- **KANN [MAY]** eine `docker-compose.yml` (sowie Varianten wie `docker-compose.e2e.yml`, `docker-compose.release.yml`) zum lokalen Hochfahren des Stacks enthalten
- **KANN [MAY]** einen `docker/`-Ordner mit per-Service-Dockerfiles und Build-Kontexten enthalten
- **KANN [MAY]** `helm/` und `skaffold.yaml` für Kubernetes-basierte Entwicklungs-Loops enthalten
- **MUSS [MUST]** eine `.env.example` bereitstellen, die jede benötigte Umgebungsvariable dokumentiert, wenn der Stack über Env-Dateien konfiguriert wird
- **MUSS NICHT [MUST NOT]** eine reale `.env` in die Versionskontrolle einchecken; `.env` **MUSS [MUST]** in der `.gitignore` stehen

### Branding und Assets (optional)
- **KANN [MAY]** einen `brand/`-Ordner für Brand-Quell-Assets (Logos, Banner) enthalten, auf die Dokumentation oder README verweisen

## Akzeptanzkriterien
- [ ] `README.md`, `.gitignore`, `CLAUDE.md`, `renovate.json5` (oder `renovate.json`) und `.pre-commit-config.yaml` existieren im Repository-Wurzelverzeichnis
- [ ] `.claude/` existiert und enthält mindestens eines von `agents/`, `skills/`, `commands/` oder einer `settings*.json`-Datei
- [ ] `.github/workflows/` enthält mindestens eine Workflow-Datei
- [ ] `Taskfile.yml` oder `Taskfile.yaml` ist vorhanden und `task --list` listet Test-, Lint- und Docs-Ziele auf
- [ ] `docs/` und `mkdocs.yml` existieren und `mkdocs build` läuft fehlerfrei durch
- [ ] `spec/` existiert im Repository-Wurzelverzeichnis
- [ ] `tests/` existiert und enthält mindestens einen Test
- [ ] Primärer Quellcode liegt unter `src/`, `src/<component>/` oder `custom_components/<name>/` — nicht lose im Wurzelverzeichnis
- [ ] Wenn eine `.env.example` vorhanden ist, erscheint ein wörtlicher `.env`-Eintrag in der `.gitignore`
- [ ] Wenn eine `hacs.json` vorhanden ist, existiert `custom_components/<domain>/` und stimmt mit der HA-Integrations-Domain überein
- [ ] CI-Status-Badges für die primären Workflows erscheinen am oberen Rand der `README.md`

## Offene Fragen
- Soll `LICENSE` für alle öffentlichen Repositories im Portfolio auf **MUSS [MUST]** angehoben werden?
- Soll die Spec eine Mindest­form für `.github/` vorgeben (Issue-Templates, PR-Template, `CODEOWNERS`)?
- Ist `renovate.json5` der kanonische Standard, oder soll `renovate.json` gleichwertig akzeptiert bleiben?
- Sollen Release-Artefakte (Changelogs, Release-Workflows, Versionierungs-Policy) von hier referenziert oder vollständig einer separaten Release-Prozess-Spec überlassen werden?
- Soll mehrsprachige Dokumentation (`docs/<lang>/`) zum **SOLLTE [SHOULD]** werden, sobald eine zweite Sprache erscheint, oder **KANN [MAY]** bleiben?
- Gibt es ein kanonisches Mindest-Set an Taskfile-Targets über Test/Lint/Docs hinaus (zum Beispiel `setup`, `ci`, `release`)?
