# Repository-Projektstruktur

Status: draft

## Kontext
Projekte in diesem Ökosystem haben eine wiedererkennbare Form auf der Festplatte: eine Python- (oder mehrsprachige) Codebasis mit MkDocs-Dokumentation, Taskfile-basierter Automatisierung, pre-commit- und Renovate-Hygiene, einem `spec/`-Ordner für Anforderungen und Claude-Code-Integration über `CLAUDE.md` und `.claude/`. Referenzimplementierungen sind [`nolte/kamerplanter`](https://github.com/nolte/kamerplanter) (mehrteiliges Repository mit Backend, Frontend, Knowledge Service und HA-Integration) und [`nolte/kamerplanter-ha`](https://github.com/nolte/kamerplanter-ha) (fokussierte Home-Assistant-Custom-Integration). Neue Repositories sollen denselben strukturellen Konventionen folgen, damit Tooling-Erwartungen, CI-Verdrahtung, Onboarding und KI-gestützte Workflows projektübergreifend gleich funktionieren.

## Ziele
- Jedes neue Git-Repository hat ein vorhersagbares Top-Level-Layout, durch das sich Menschen und KI-Agenten ohne projektspezifische Entdeckung orientieren können
- Gemeinsames Tooling (pre-commit, Renovate, MkDocs, Taskfile) ist konsistent und an denselben Stellen eingebunden
- Abhängigkeits-Hygiene ist portfolioweit automatisiert: jedes Repository setzt Renovate gegen das gemeinsame `nolte/gh-plumbing`-Preset ein, sodass Security- und Versions-Updates als PRs ankommen, ohne dass die Renovate-Konfiguration pro Repository abdriftet — Renovate ist damit ein elementarer Bestandteil jedes Projekts und kein optionales Add-on
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
- **MUSS [MUST]** eine `README.md` im Repository-Wurzelverzeichnis enthalten mit Projektvorstellung, Feature-Übersicht, Quickstart und Verweisen auf die vollständige Dokumentation; die innere Struktur dieser Datei (Pflicht-Abschnitte, Reihenfolge, Badges, Cross-Repository-Links) wird von der `readme-structure`-Spec geregelt
- **MUSS [MUST]** eine `.gitignore` enthalten
- **MUSS [MUST]** eine `CLAUDE.md` enthalten, die KI-gestützte Entwicklungs­konventionen, Architektur-Hinweise und Kommando-Einstiegspunkte des Repositories dokumentiert
- **MUSS [MUST]** eine `renovate.json5` (bevorzugt) oder `renovate.json` enthalten, die das portfolioweite Preset `github>nolte/gh-plumbing//renovate-configs/common#<tag>` erweitert — an einen Release-Tag gepinnt (zum Beispiel `#v1.1.12`) —, damit die Renovate-Konfiguration portfolio­übergreifend konsistent bleibt; per-Repository-Überschreibungen **SOLLTEN [SHOULD]** schmal gehalten werden (typischerweise Package-Gruppierungen oder Automerge-Regeln)
- **MUSS [MUST]** die Renovate GitHub App (<https://github.com/apps/renovate>) auf dem Repository installiert haben, damit die obige `renovate.json5`-Konfiguration tatsächlich Dependency-Updates auslöst; ohne die App ist die Konfigurationsdatei wirkungslos und es entstehen weder PRs noch ein Dependency-Dashboard-Issue — es gilt dasselbe Probot-artige Installationsmuster wie für `settings` / `boring-cyborg` / `stale`, und die Installation ist menschlich-genehmigt
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

### Release- und Dokumentations-Workflows
Das `nolte/gh-plumbing`-Portfolio liefert wiederverwendbare Workflows für Release-Management und Dokumentations-Auslieferung. Die `branching-model`-Spec listet die Release-Management-Workflows vollständig auf und macht drei davon verpflichtend. Diese Spec hebt zusätzlich die Dokumentations- und Packaging-Begleiter hervor, damit ein Projektstruktur-Audit sie auch dann erkennt, wenn die branching-model-Spec isoliert betrachtet wird.

- **MUSS [MUST]** die Release-Management-Workflows enthalten, die die `branching-model`-Spec vorschreibt: `.github/workflows/release-drafter.yml`, `.github/workflows/release-cd-refresh-master.yml` und `.github/workflows/automerge.yaml`, jeweils verkabelt mit dem entsprechenden wiederverwendbaren Workflow unter `nolte/gh-plumbing/.github/workflows/`
- **SOLLTE [SHOULD]** `.github/workflows/release-cd-deliver-docs.yml` enthalten — getriggert auf `release: [published]` und aufrufend `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml` —, sobald `mkdocs.yml` vorhanden ist, damit die Dokumentation mit jedem Release neu veröffentlicht wird
- **KANN [MAY]** einen repository-spezifischen Packaging-Workflow enthalten (zum Beispiel eine `release.yml`, die `manifest.json` patcht, ein ZIP baut und via `gh release upload` hochlädt), getriggert auf `release: [published]`, wenn das Repository ein Auslieferungs-Artefakt wie eine HACS-Integration verschifft
- **SOLLTE [SHOULD]** jede Referenz auf einen wiederverwendbaren Workflow an einen Tag pinnen (zum Beispiel `@v1.1.12`) statt an einen beweglichen Branch, damit das Release-Pipeline-Verhalten reproduzierbar bleibt

### GitHub-Repository-Konfiguration
- **MUSS [MUST]** GitHub-Repository-Einstellungen — Topics, Beschreibung, Homepage, Branch-Protection, Labels, Mitarbeitende und Merge-Button-Optionen — als Code über `.github/settings.yml` verwalten, konsumiert von der [Probot-Settings-App](https://probot.github.io/apps/settings/)
- **MUSS [MUST]** die portfolioweiten Defaults über `_extends: nolte/gh-plumbing:.github/commons-settings.yml` erben (die Kurzform `gh-plumbing:.github/commons-settings.yml` ist innerhalb der `nolte`-Organisation gleichwertig) und die per-Repository-Inhalte auf repository-spezifische Felder wie `name`, `description`, `homepage` und `topics` beschränken
- **MUSS NICHT [MUST NOT]** Repository-Einstellungen manuell über die GitHub-UI pflegen, sobald `.github/settings.yml` vorhanden ist; jede UI-Änderung gilt als Drift und muss in die Datei zurückgeführt werden
- **MUSS [MUST]** jede Label-`description` in `.github/settings.yml` (und in jeder geerbten `commons-settings.yml`) auf **maximal 100 Zeichen** begrenzen (gezählt als UTF-16-Code-Units, entsprechend JavaScript `String.length` und der Durchsetzung durch die GitHub-API). Die GitHub-Labels-API lehnt längere descriptions mit HTTP 422 `description is too long (maximum is 100 characters)` ab, woraufhin die Probot-Settings-App genau dieses eine Label still überspringt und der Rest des Sync-Laufs fehlerfrei durchläuft, ohne dass der Fehler an das Repository zurückgemeldet wird. Beobachtet am 2026-05-01 in `nolte/gh-plumbing`: eine 117-Zeichen-Description am `release`-Label hat verhindert, dass es im Live-Repo angelegt wurde, während die übrigen 19 Labels desselben Sync-Laufs erfolgreich landeten
- **MUSS [MUST]** eine `.github/release-drafter.yml` enthalten, die `nolte/gh-plumbing:.github/commons-release-drafter.yml` erweitert, um den Release-Notes-Drafter zu speisen (der zugehörige Workflow wird von der branching-model-Spec beschrieben)
- **SOLLTE [SHOULD]** eine `.github/boring-cyborg.yml` enthalten, die `nolte/gh-plumbing:.github/commons-boring-cyborg.yml` erweitert, für Newcomer-Onboarding, Auto-Labeling und Reviewer-Zuweisung über die [Boring-Cyborg-App](https://probot.github.io/apps/boring-cyborg/)
- **SOLLTE [SHOULD]** eine `.github/stale.yml` enthalten, die `nolte/gh-plumbing:.github/commons-stale.yml` erweitert, um inaktive Issues und Pull Requests über die [Stale-App](https://probot.github.io/apps/stale/) zu verwalten
- **KANN [MAY]** einzelne Schlüssel aus den geerbten `commons-*.yml`-Dateien überschreiben, wenn der Bedarf eines Repositories von den Portfolio-Defaults abweicht; solche Überschreibungen schmal halten und neben der Änderung erklären

### Dokumentation
- **MUSS [MUST]** ein `docs/`-Verzeichnis als MkDocs-Quelle enthalten
- **MUSS [MUST]** eine `mkdocs.yml` im Repository-Wurzelverzeichnis enthalten
- **SOLLTE [SHOULD]** die Dokumentation über einen CI-Workflow veröffentlichen (zum Beispiel GitHub Pages)
- **KANN [MAY]** `docs/` nach Sprache aufteilen (`docs/en/`, `docs/de/`, …), wenn mehrsprachige Dokumentation erforderlich ist

### Spezifikationen
- **MUSS [MUST]** ein `spec/`-Verzeichnis im Repository-Wurzelverzeichnis für Anforderungen, NFRs, Style Guides und Domänenwissen enthalten
- **SOLLTE [SHOULD]** `spec/` nach Themen-Unterordnern organisieren (zum Beispiel `req/`, `nfr/`, `ui-nfr/`, `style-guides/`, `knowledge/`), sobald mehr als eine Handvoll Specs existieren
- **KANN [MAY]** die Konvention des mehrsprachigen Spec-Skills (`<slug>/<lang>.md`) wiederverwenden, wenn das Projekt übersetzte Specs benötigt

### Projekt-Planungsartefakte (optional)
Das Portfolio führt Roadmap-, Sprint-, Feature- und Release-Artefakt-Datensätze als versionskontrolliertes Markdown unter einem Top-Level-Verzeichnis `project/`, sobald das Repository die Claude-getriebene Planungssuite nutzt (`roadmap-init`, `sprint-plan`, `feature-decompose` sowie die Skills `sprint-execute` / `sprint-review`, die diese Artefakte lesen). Die innere Form der einzelnen Artefakte ist jeweils durch eine eigene Spec geregelt (`roadmap`, `sprint`, `feature`, `release-artifact`); diese Spec deklariert nur das Verzeichnis-Layout, in dem sie liegen — damit ein Projektstruktur-Audit die Planungs-Oberfläche auch dann erkennt, wenn die genannten Skills noch nicht gelaufen sind.

- **KANN [MAY]** ein Top-Level-Verzeichnis `project/` für die Planungs-Artefakte enthalten; das Fehlen ist zulässig für Repositories, die die Planungs-Suite nicht nutzen
- **MUSS [MUST]**, wenn `project/` vorhanden ist, die Dateien wie folgt organisieren: `project/roadmap.md` (die Queue), `project/goals.md` (Vision plus Outcomes), `project/sprints/<NNNN>-<slug>.md` (eine Datei pro Sprint), `project/features/<slug>.md` (eine Datei pro Feature) und — sofern Out-of-Band-Releases auftreten — `project/release-artifacts/out-of-band/<NNNN>-<slug>.md` plus ein regeneriertes `project/release-artifacts/out-of-band/INDEX.md`; die jeweilige Datei-Form wird von den Specs `roadmap`, `sprint`, `feature` und `release-artifact` geregelt
- **MUSS NICHT [MUST NOT]** den `project/`-Baum unter `docs/` oder ein anderes Unterverzeichnis schachteln; die Planungs-Oberfläche ist ein Top-Level-Orientierungspunkt, parallel zu `spec/` und `tests/`
- **MUSS NICHT [MUST NOT]** hier Regeln neu definieren, die von den Specs `roadmap`, `sprint`, `feature` oder `release-artifact` deklariert werden; dieser Abschnitt ist ausschließlich Layout

### Tests
- **MUSS [MUST]** ein `tests/`-Verzeichnis im Repository-Wurzelverzeichnis enthalten
- **SOLLTE [SHOULD]** die Struktur des Quellbaums innerhalb von `tests/` spiegeln
- **KANN [MAY]** End-to-End-Tests in einem eigenen Unterordner wie `tests/e2e/` ablegen

### Quellcode-Layout
- **MUSS [MUST]** den primären Quellcode unter einem der folgenden konventionellen Layouts ablegen:
  - `src/` für eine Einzweck-Bibliothek oder einen Einzweck-Dienst
  - `src/<component>/` je Teilprojekt in einem mehrteiligen Repository (zum Beispiel `src/backend/`, `src/frontend/`, `src/knowledge-service/`)
  - `custom_components/<name>/` für eine Home-Assistant-Custom-Integration
  - `.claude-plugin/` zusammen mit `skills/<name>/` (und optional `agents/<name>.md`) für ein Claude-Code-Plugin-Repository, bei dem Prompt- und Skill-Inhalte das primäre Lieferobjekt sind und kein Runtime-Quellcode existiert
  - `playbooks/`, `roles/` und ein Inventar-Baum (`inventory/` für eine einzelne Umgebung oder `inventories/<env>/` je Umgebung gemäß `spec/ansible/playbook-development/`) sowie optional `group_vars/` und `host_vars/`, zusammen mit `ansible.cfg` und `requirements.yml` im Repository-Wurzelverzeichnis für ein Ansible-Bootstrap- bzw. Provisioning-Repository, dessen primäres Lieferobjekt Konfigurations- und Automatisierungs-Code ist und das keinen Runtime-Quellcode enthält; die Ansible-Standardkonventionen lassen sich nicht in eine `src/`-Hülle umpacken, ohne die Default-Rollen- und Inventory-Suche von `ansible-playbook` zu brechen
- **MUSS NICHT [MUST NOT]** primäre Quellcode-Dateien lose im Repository-Wurzelverzeichnis halten; dort dürfen nur Tooling-Konfigurationen, Metadaten und kleine Skripte liegen; die Ansible-Variante ist eine bewusste Ausnahme von dieser Regel
- **KANN [MAY]** einen `scripts/`- und/oder `tools/`-Ordner für repository-lokale Automatisierungs-Helfer enthalten

### Python-Entwicklung (optional)
- **MUSS [MUST]** alle Python-Projekt-Abhängigkeiten innerhalb einer projektlokalen Python-Virtual-Environment installieren und ausführen, unabhängig davon, ob diese über `python -m venv`, `uv venv`, `virtualenv` oder ein gleichwertiges Werkzeug erzeugt wird; systemweite oder user-globale Installation von Projekt-Abhängigkeiten ist nicht erlaubt
- **MUSS [MUST]** das lokale Virtual-Environment-Verzeichnis (typischerweise `.venv/`) aus der Versionskontrolle heraushalten, indem es in der `.gitignore` gelistet ist
- **MUSS [MUST]** eine `pyproject.toml` enthalten (im Repository-Wurzelverzeichnis bei einem Einzweck-Repository oder unter jeder `src/<component>/` in einem mehrteiligen Repository), die `[build-system]`, Projekt-Metadaten (`name`, `version`, `license`, `authors`, `classifiers`, `urls`) und Python-Tooling-Konfiguration (`[tool.ruff]`, `[tool.pytest.ini_options]` und Ähnliches) deklariert; `pyproject.toml` trägt Distributions-Metadaten und Tooling-Konfiguration, während Laufzeit-Abhängigkeiten in `requirements.txt` (siehe unten) verbleiben, damit sich die beiden Dateien nicht überlappen
- **MUSS [MUST]** direkte Laufzeit-Abhängigkeiten in einer `requirements.txt` pflegen — im Repository-Wurzelverzeichnis bei einem Einzweck-Repository oder unter `src/<component>/requirements.txt` je Komponente in einem mehrteiligen Repository; das Laufzeit-Installationsset wird aus `requirements.txt` bezogen, nicht aus einem `[project.dependencies]`-Block in `pyproject.toml`
- **SOLLTE [SHOULD]** Entwicklungs- und nur-für-Tests-Abhängigkeiten getrennt in einer `requirements-dev.txt` (bzw. `src/<component>/requirements-dev.txt`) führen, damit Produktiv-Installationen kein Tooling mitziehen
- **SOLLTE [SHOULD]** Taskfile-Targets (zum Beispiel `task install`, `task test`, `task lint`) so verkabeln, dass sie das projektlokale Virtual-Environment erzeugen oder nutzen und über `pip install -r requirements.txt` (sowie `requirements-dev.txt`, sofern zutreffend) installieren, damit lokale und CI-Ausführung denselben Einstiegspunkt teilen

### Format der Requirements-Dateien (optional, gilt sofern `requirements*.txt` vorhanden ist)
Diese Regeln gelten für jede `requirements.txt` und `requirements-dev.txt`, die unter dieser Spec geschrieben werden, und existieren, damit Scaffolding und Drift-Prüfungen die Datei-Struktur validieren können — nicht nur ihre Existenz.

- **MUSS [MUST]** jede Abhängigkeit auf einer eigenen Zeile mit explizitem Versions-Spezifizierer auflisten (zum Beispiel `pkg>=1.2`, `pkg==1.2.3` oder `pkg~=1.2`); reine Paketnamen ohne Spezifizierer sind nicht erlaubt, weil sie transitive Auflösung still über Installationen hinweg driften lassen
- **MUSS NICHT [MUST NOT]** `requirements-dev.txt` über eine `-r requirements.txt`-Direktive (oder das gleichwertige `--requirement`) an `requirements.txt` anketten; das Taskfile-Muster aus dem Abschnitt oben installiert beide Dateien unabhängig, sodass die Verkettung redundant ist, den Dev-only-Vertrag verwischt und einer versehentlich veralteten Runtime-Liste still folgt
- **KANN [MAY]** `#`-Kommentarzeilen für Header, Begründungen oder Upstream-Tracking-Verweise verwenden; eine ausschließlich aus Kommentaren bestehende `requirements.txt` ist als temporärer Platzhalter zulässig, solange noch keine Laufzeit-Abhängigkeit publiziert ist (zum Beispiel ein SDK vor seinem Release), aber der Platzhalter **MUSS [MUST]** durch echte Einträge ersetzt werden, sobald die erste Laufzeit-Abhängigkeit gelandet ist

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
- [ ] `renovate.json5` (oder `renovate.json`) erweitert `github>nolte/gh-plumbing//renovate-configs/common#<tag>`, gepinnt an einen Release-Tag und nicht an einen beweglichen Branch
- [ ] Die Renovate GitHub App (Slug `renovate`) ist auf dem Repository installiert — verifizierbar über die Repository-Auswahl der App, das Vorhandensein eines offenen oder geschlossenen Dependency-Dashboard-Issues, das Vorhandensein von `app/renovate-bot`-PRs oder das Mend-Renovate-Dashboard unter `https://developer.mend.io/github/<owner>/<repo>`
- [ ] `.claude/` existiert und enthält mindestens eines von `agents/`, `skills/`, `commands/` oder einer `settings*.json`-Datei
- [ ] `.github/workflows/` enthält mindestens eine Workflow-Datei
- [ ] `.github/workflows/` enthält `release-drafter.yml`, `release-cd-refresh-master.yml` und `automerge.yaml`, jeweils verkabelt mit dem passenden wiederverwendbaren `nolte/gh-plumbing`-Workflow
- [ ] Wenn `mkdocs.yml` vorhanden ist, existiert `.github/workflows/release-cd-deliver-docs.yml` und triggert auf `release: [published]`
- [ ] Jede `uses: nolte/gh-plumbing/.github/workflows/...`-Referenz in `.github/workflows/` ist an einen Release-Tag gepinnt, nicht an einen beweglichen Branch
- [ ] `.github/settings.yml` ist vorhanden und erweitert `nolte/gh-plumbing:.github/commons-settings.yml` (oder die gleichwertige Kurzform)
- [ ] Jedes Label-`description`-Feld in `.github/settings.yml` und der geerbten `commons-settings.yml` ist höchstens 100 Zeichen lang
- [ ] `.github/release-drafter.yml` ist vorhanden und erweitert `nolte/gh-plumbing:.github/commons-release-drafter.yml`
- [ ] `.github/boring-cyborg.yml` und `.github/stale.yml` sind vorhanden und erweitern die jeweilige `nolte/gh-plumbing`-commons-Datei
- [ ] `Taskfile.yml` oder `Taskfile.yaml` ist vorhanden und `task --list` listet Test-, Lint- und Docs-Ziele auf
- [ ] `docs/` und `mkdocs.yml` existieren und `mkdocs build` läuft fehlerfrei durch
- [ ] `spec/` existiert im Repository-Wurzelverzeichnis
- [ ] `tests/` existiert und enthält mindestens einen Test
- [ ] Primärer Quellcode liegt unter `src/`, `src/<component>/`, `custom_components/<name>/`, `.claude-plugin/` + `skills/<name>/`, **oder** das Repository ist ein Ansible-Bootstrap-/Provisioning-Repository mit `playbooks/`, `roles/` und einem Inventar-Baum (`inventory/` oder `inventories/<env>/`) im Wurzelverzeichnis; nicht lose im Wurzelverzeichnis
- [ ] Wenn das Repository Python-Quellcode enthält (`*.py`-Dateien, `custom_components/<name>/` oder `pyproject.toml`), ist eine `requirements.txt` im Repository-Wurzelverzeichnis oder unter jeder Python-führenden `src/<component>/` vorhanden
- [ ] Wenn das Repository Python-Quellcode enthält, existiert eine `pyproject.toml` im Repository-Wurzelverzeichnis (Einzweck) oder unter jeder `src/<component>/` (mehrteilig) und deklariert `[build-system]`, Projekt-Metadaten und alle verwendete Python-Tooling-Konfiguration
- [ ] Wenn das Repository Python-Quellcode enthält, schließt `.gitignore` das lokale Virtual-Environment-Verzeichnis (zum Beispiel `.venv/`) aus
- [ ] Wenn `requirements.txt` oder `requirements-dev.txt` vorhanden ist, trägt jede Nicht-Kommentar- und Nicht-Leerzeile einen Versions-Spezifizierer (keine reinen Paketnamen)
- [ ] Wenn `requirements-dev.txt` vorhanden ist, enthält es keine `-r requirements.txt`-Direktive (oder `--requirement`-Direktive)
- [ ] Wenn eine `.env.example` vorhanden ist, erscheint ein wörtlicher `.env`-Eintrag in der `.gitignore`
- [ ] Wenn eine `hacs.json` vorhanden ist, existiert `custom_components/<domain>/` und stimmt mit der HA-Integrations-Domain überein
- [ ] Wenn `project/` vorhanden ist, liegen die Planungs-Artefakte unter dem Layout `project/roadmap.md`, `project/goals.md`, `project/sprints/<NNNN>-<slug>.md`, `project/features/<slug>.md` oder `project/release-artifacts/out-of-band/<NNNN>-<slug>.md` (mit `project/release-artifacts/out-of-band/INDEX.md`, sofern mindestens ein Out-of-Band-Eintrag existiert); geschachtelte oder alternative Orte schlagen die Validierung fehl
- [ ] CI-Status-Badges für die primären Workflows erscheinen am oberen Rand der `README.md`

## Offene Fragen
- Soll `LICENSE` für alle öffentlichen Repositories im Portfolio auf **MUSS [MUST]** angehoben werden?
- Soll die Spec zusätzlich Issue-Templates, Pull-Request-Templates und `CODEOWNERS` für `.github/` vorschreiben? Die Probot-Konfiguration (settings, release-drafter, boring-cyborg, stale) ist nun abgedeckt; die Community-Health-Dateien bleiben offen.
- Ist `renovate.json5` der kanonische Standard, oder soll `renovate.json` gleichwertig akzeptiert bleiben?
- Sollen Release-Artefakte (Changelogs, Release-Workflows, Versionierungs-Policy) von hier referenziert oder vollständig einer separaten Release-Prozess-Spec überlassen werden?
- Soll mehrsprachige Dokumentation (`docs/<lang>/`) zum **SOLLTE [SHOULD]** werden, sobald eine zweite Sprache erscheint, oder **KANN [MAY]** bleiben?
- Gibt es ein kanonisches Mindest-Set an Taskfile-Targets über Test/Lint/Docs hinaus (zum Beispiel `setup`, `ci`, `release`)?
- Soll `tests/` für Claude-Code-Plugin-Repositories, die nur Prompt-/Skill-Inhalte ausliefern und keinen Runtime-Code enthalten, von **MUSS [MUST]** auf **SOLLTE [SHOULD]** abgeschwächt werden?
