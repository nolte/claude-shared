# Branching-Modell

Status: draft

## Kontext
Repositories in diesem Portfolio verwenden `main` als reinen Präsentations-Branch, der stets das zuletzt veröffentlichte GitHub Release widerspiegelt. Aktive Entwicklung findet auf `develop` statt; Feature-Branches zielen per Pull Request auf `develop`. Wenn ein GitHub Release veröffentlicht wird, führen wiederverwendbare Workflows aus [`nolte/gh-plumbing`](https://github.com/nolte/gh-plumbing) einen Fast-Forward von `main` auf den freigegebenen Tag durch, sodass `main` eine maschinell gepflegte, lesende Sicht auf das zuletzt ausgelieferte Artefakt bleibt. Menschen und KI-Agenten, die auf `main` schauen, sehen genau das, was ausgeliefert wurde — niemals einen Work-in-Progress-Stand.

## Ziele
- `main` entspricht immer dem zuletzt veröffentlichten GitHub Release, nichts anderem
- Keine manuellen Commits, Pushes oder Merges landen auf `main` — jede Änderung läuft über `develop` und ein Release
- Die Überführung von `develop` nach `main` ist automatisiert, auditierbar und nur durch ein veröffentlichtes Release ausgelöst
- Branch-Rollen sind für Menschen und KI-Agenten, die das Repository lesen, eindeutig

## Nicht-Ziele
- Tag-Namensschema (von der release-drafter-Konfiguration abgedeckt)
- Changelog-Erzeugung (von release-drafter abgedeckt)
- Veröffentlichung in externen Registries (HACS, PyPI, Container-Registries)
- Inhalt projektweiter Taskfile-/CI-Targets (durch die project-structure-Spec abgedeckt)

## Anforderungen

### Branch-Rollen
- **MUSS [MUST]** `develop` als Integrations-Branch festlegen, auf dem alle Feature-Arbeit per Pull Request landet
- **MUSS [MUST]** `main` als Release-Präsentations-Branch festlegen, der das zuletzt veröffentlichte GitHub Release widerspiegelt
- **MUSS NICHT [MUST NOT]** manuelle Commits, Pushes oder Merges direkt auf `main` zulassen; der Branch wird ausschließlich durch die Release-Automatisierung beschrieben
- **MUSS [MUST]** Feature-Branches mit einem der Präfixe `feat/`, `fix/`, `chore/` oder `docs/` benennen und in ihrem Pull Request auf `develop` zielen; diese Präfixe sind identisch mit den in PR-Titeln verwendeten Conventional-Commits-Types, sodass Branch-Name und Commit-Type ohne Übersetzung zueinander passen

### Branch-Protection
- **MUSS [MUST]** alle Branch-Protection-Regeln als Code in `.github/settings.yml` deklarieren (direkt oder über `_extends: nolte/gh-plumbing:.github/commons-settings.yml`) und über die [Probot-Settings-App](https://probot.github.io/apps/settings/) synchronisieren; Protection-Regeln **MUSS NICHT [MUST NOT]** ad-hoc über die GitHub-UI konfiguriert werden
- **MUSS [MUST]** `main` so schützen, dass direkte Pushes von Menschen blockiert werden und nur der Release-Workflow (via `GITHUB_TOKEN`) ihn aktualisieren kann
- **SOLLTE [SHOULD]** `develop` so schützen, dass Pull Requests vor dem Merge grüne CI voraussetzen
- **SOLLTE [SHOULD]** lineare Historie auf `main` erzwingen, damit der Fast-Forward von Release-Tags sauber bleibt

### Release-Flow
- **MUSS [MUST]** GitHub Releases aus Tags erzeugen, die auf dem `develop`-Branch entstehen — release-drafter hält den Entwurf aktuell, ein Mensch veröffentlicht ihn
- **MUSS [MUST]** `main` ausschließlich über den Release-Workflow auf `release: [published]` aktualisieren
- **MUSS [MUST]** den Inhalt von `main` mechanisch aus dem Release ableiten; direkte Datei-Änderungen auf `main` sind ein Fehler
- **SOLLTE [SHOULD]** die Default-Pull-Request-Basis auf `develop` lassen, nicht auf `main`

### Erforderliche GitHub-Workflows
Das Repository **MUSS [MUST]** die folgenden Workflows unter `.github/workflows/` enthalten, jeweils an den entsprechenden wiederverwendbaren Workflow aus `nolte/gh-plumbing` angeschlossen:

- **`release-drafter.yml`** — löst auf `push: [develop]` aus; nutzt `nolte/gh-plumbing/.github/workflows/reusable-release-drafter.yml`, um den GitHub-Release-Entwurf der nächsten Version aktuell zu halten
- **`release-cd-refresh-master.yml`** — löst auf `release: [published]` aus; nutzt `nolte/gh-plumbing/.github/workflows/reusable-release-cd-refresh-master.yml` mit `target_branch: main`, um `main` per Fast-Forward auf den veröffentlichten Commit zu bringen; benötigt die Berechtigung `contents: write`
- **`automerge.yaml`** — löst auf Pull-Request-/Review-/Check-Suite-Events aus; nutzt `nolte/gh-plumbing/.github/workflows/reusable-automerge.yaml`, damit freigegebene, grüne Pull Requests gegen `develop` automatisch gemergt werden

Das Repository **SOLLTE [SHOULD]** außerdem enthalten, wo anwendbar:

- **`release-cd-deliver-docs.yml`** — auf `release: [published]`; veröffentlicht die MkDocs-Ausgabe über `nolte/gh-plumbing/.github/workflows/reusable-mkdocs.yaml`
- Weitere `release: [published]`-Packaging-Workflows (zum Beispiel `release.yml` zur Erzeugung eines HACS-ZIP), die spezifisch für das Liefer-Artefakt des Repositories sind

### Workflow-Integrität
- **MUSS [MUST]** die drei Pflicht-Workflows (`release-drafter.yml`, `release-cd-refresh-master.yml`, `automerge.yaml`) in jedem Repository halten, das diesem Branching-Modell folgt
- **SOLLTE [SHOULD]** die Referenz auf die wiederverwendbaren `nolte/gh-plumbing`-Workflows auf einen Tag fixieren (zum Beispiel `@v1.1.12`) statt auf einen wandernden Branch, damit das Refresh-Verhalten von `main` reproduzierbar bleibt

## Akzeptanzkriterien
- [ ] `develop` existiert und ist die Default-Basis für Pull Requests
- [ ] `main` existiert und ist per Branch-Protection so geschützt, dass Menschen nicht direkt pushen können
- [ ] Branch-Protection-Regeln für `main` und `develop` sind in `.github/settings.yml` deklariert (direkt oder über die `nolte/gh-plumbing`-commons-Erweiterung), nicht ausschließlich über die GitHub-UI
- [ ] `.github/workflows/release-drafter.yml` ist vorhanden und löst auf `push: [develop]` aus
- [ ] `.github/workflows/release-cd-refresh-master.yml` ist vorhanden, löst auf `release: [published]` aus und setzt `target_branch: main`
- [ ] `.github/workflows/automerge.yaml` ist vorhanden und ruft den wiederverwendbaren Automerge-Workflow aus `nolte/gh-plumbing` auf
- [ ] Der HEAD von `main` entspricht einem veröffentlichten GitHub-Release-Tag (`git tag --points-at main` liefert einen Release-Tag zurück)
- [ ] Zwischen zwei aufeinanderfolgenden Releases gibt es keine menschlich erzeugten Commits auf `main` — nur Commits, die der Refresh-Workflow eingebracht hat
- [ ] Feature-Branches im Repository verwenden einen der Präfixe `feat/`, `fix/`, `chore/`, `docs/`
- [ ] Wenn MkDocs verwendet wird, ist `.github/workflows/release-cd-deliver-docs.yml` vorhanden und löst auf `release: [published]` aus

## Offene Fragen
- Wie sollen Notfall-Hotfixes behandelt werden — Branch ab `main`, Merge zurück nach `main` und `develop`, oder immer über `develop` plus neues Patch-Release?
- Soll `target_branch` einheitlich `main` bleiben, auch für HACS-Integrationen, deren historische Konvention `master` war?
- Gibt es eine portfolioweite Policy, welchen `nolte/gh-plumbing`-Versions-Tag alle Repositories pinnen, und wie wird dieser hochgezogen?
- Soll diese Spec ein Tag-Namensschema (`v1.2.3` vs `1.2.3`) vorschreiben oder das der release-drafter-Konfiguration je Repository überlassen?
- Soll der Automerge-Workflow verpflichtend sein oder optional, wenn ein Repository manuelle Merges bevorzugt?
