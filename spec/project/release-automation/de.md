# Release-Automation

Status: draft

## Kontext

Die Spec `branching-model` definiert, **wie** Releases propagieren, sobald sie veröffentlicht sind (`release-drafter` pflegt einen Draft, ein Mensch publiziert ihn, `release-cd-refresh-master.yml` zieht `main` per Fast-Forward nach). Was dort derzeit manuell bleibt, ist der eigentliche **Draft → Published**-Schritt: §Local release operation fordert, dass ein Operator `gh release edit <tag> --draft=false` ausführt (oder in der Web-UI auf *Publish* klickt).

Dieser manuelle Schritt ist das letzte nicht-automatisierte Glied in der Release-Kette und die Ursache für Finding #3 des `spec-drift-audit` 2026-Q2 — `v0.1.1` liegt auf `claude-shared` als Draft, sodass `main` HEAD nicht auf einen publizierten Release ausgerichtet sein kann. Die portfolioweite Entscheidung lautet, das Audit-Finding **nicht** durch manuelles Promoten eines Releases aufzulösen; stattdessen definiert diese Spec den automatisierten Promotion-Prozess, und das Finding löst sich auf, sobald die Automation einen echten Release geschnitten hat.

Diese Spec schließt die Lücke zwischen `release-drafter` (baut und pflegt den Draft) und `release-cd-refresh-master.yml` (reagiert auf `release: [published]`): der Workflow, der `draft: true → false` auf Abruf kippt, unter Guardrails, ohne menschlichen CLI-Tastendruck auf den Tag.

## Ziele

- Der Übergang Draft → Published erfolgt über einen reviewbaren, reproduzierbaren Workflow — nicht dadurch, dass ein Operator ein Release per CLI oder Web-UI bearbeitet.
- Der Mensch bleibt in der Schleife für die **Entscheidung** zu releasen (wann, welche Version), aber die Mechanik (Publish-Aufruf, Tag-Handling, Fehlerprüfung) ist kodifiziert.
- Die Automation verweigert, etwas zu publizieren, das nicht von `release-drafter` stammt, und schließt damit den handgeschnitzten-Tag-Failure-Mode aus, den `branching-model` §Local release operation bereits verbietet.
- Der Prozess ist portfolioweit wiederverwendbar: einmal als Reusable Workflow unter `nolte/gh-plumbing` implementiert, konsumiert von jedem Repo, das `branching-model` folgt.
- Die `main`-Alignment-Kriterien des Spec-Drift-Audits werden erfüllbar, indem der Workflow ausgelöst wird, nicht indem `gh`-Kommandos direkt gegen den Tag laufen.

## Nicht-Ziele

- Publizieren von Artefakten an externe Registries (npm, PyPI, Container-Registries, HACS-ZIP-Uploads) — das bleibt bei repository-spezifischen `release: [published]`-Packaging-Workflows, wie `project-structure` sie beschreibt.
- Binary-Builds, Signing, SBOM-Generierung.
- Erzeugung von Release-Notes-Inhalten — bleibt Aufgabe von `release-drafter`, gespeist durch Conventional-Commits-PR-Titel.
- Versionierungspolitik (SemVer-Ableitung von major/minor/patch) — geerbt aus der `release-drafter`-Konfiguration in `nolte/gh-plumbing:.github/commons-release-drafter.yml`.
- Hotfix-Flow (Release von `main` zurück nach `develop`) — offen als Open Question auf `branching-model` und außerhalb des Scopes hier.
- Vollständige Abschaffung des manuellen `gh release edit --draft=false`-Pfads; der manuelle Pfad bleibt als dokumentierter Fallback für Incident-Response, wenn der Workflow selbst kaputt ist.

## Anforderungen

### Workflow-Existenz und Trigger

- **MUSS [MUST]** einen dedizierten Workflow bereitstellen (kanonischer Name: `.github/workflows/release-publish.yml`), der den Draft → Published-Übergang durchführt; der Publish-Schritt **DARF NICHT [MUST NOT]** in `release-drafter.yml` oder in einem anderen Workflow wohnen, dessen primäre Verantwortung eine andere Release-Phase ist
- **MUSS [MUST]** `workflow_dispatch` als Trigger exponieren, damit die Release-Entscheidung eine bewusste menschliche Handlung ist, auditierbar über die Workflow-Run-Historie von GitHub
- **DARF NICHT [MUST NOT]** in der Baseline-Spezifikation auf `push`, `pull_request`, `schedule` oder `release: [created]` triggern; zusätzliche Trigger **KÖNNEN [MAY]** repositoryweise hinzugefügt werden, aber nur nachdem eine dedizierte Open Question für dieses Repo aufgelöst wurde
- **MUSS [MUST]**, sobald `nolte/gh-plumbing` ihn ausliefert, den Reusable Workflow unter `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml` konsumieren — flacher Pfad, Geschwister zu `reusable-release-drafter.yml` und `reusable-release-cd-refresh-master.yml`, damit die portfolioweite Reusable-Namenskonvention konsistent bleibt; bis dieser Reusable existiert, ist eine lokale Implementierung akzeptabel, die die Anforderungen unten erfüllt, und **MUSS [MUST]** bei erster Verfügbarkeit auf den Reusable umgezogen werden
- **MUSS [MUST]** jede `nolte/gh-plumbing`-Referenz auf ein Release-Tag pinnen (analog zu den Pinning-Regeln aus `project-structure` und `workflow-health`)
- **SOLLTE [SHOULD]** einen `concurrency`-Block deklarieren (`group: release-publish`, `cancel-in-progress: false`), damit zwei überlappende Dispatches in eine Queue laufen, statt auf dem `--draft=false`-API-Call zu rennen

### Operativer Kontrakt

- **MUSS [MUST]** ausschließlich auf einem Release operieren, das aktuell im Zustand `draft: true` ist und dessen Body von `release-drafter` geschrieben wurde — identifiziert durch Matching des Release-Tags auf den jüngsten Draft, der auf `develop` erzeugt wurde
- **MUSS [MUST]** das Publizieren verweigern, wenn kein `release-drafter`-Draft existiert oder wenn der Tag des Drafts zu keinem von `develop` aus erreichbaren Commit gehört
- **MUSS [MUST]** einen optionalen `tag`-Input auf `workflow_dispatch` akzeptieren; wenn mehrere `release-drafter`-Drafts offen sind, **MUSS [MUST]** der Workflow mit einer handlungsfähigen Fehlermeldung fehlschlagen, die alle offenen Drafts listet — es sei denn, `tag` wurde übergeben; in diesem Fall **MUSS [MUST]** ausschließlich der Draft publiziert werden, dessen Tag exakt dem Input entspricht (keine „newest wins"-Heuristik)
- **DARF NICHT [MUST NOT]** einen neuen Tag anlegen, einen bestehenden Tag überschreiben oder eine außerhalb der Pipeline platzierte `git tag` + `git push --tags`-Sequenz als Release-Quelle tolerieren; der Tag, den der `release-drafter`-Draft trägt, ist der Tag, der publiziert wird, und jedes Release, dessen Tag nicht vom Drafter stammt, **MUSS [MUST]** zurückgewiesen werden — das schließt den Failure-Mode, den `branching-model` §Local release operation bereits verbietet und der portfolioweit historisch als Tag-/Release-Namens-Drift beobachtet wurde
- **DARF NICHT [MUST NOT]** den Release-Body innerhalb dieses Workflows verändern; Body-Edits müssen, falls nötig, **vor** dem Run über `gh release edit <tag>` stattfinden (Titel-/Body-/Tag-Anpassungen per `branching-model` §Local release operation) oder über `release-drafter`-Re-Runs
- **MUSS [MUST]** den Ziel-Tag, den Titel und eine Diff-Zusammenfassung des Bodys im Workflow-Run-Output sichtbar machen, damit der menschliche Auslöser vor dem irreversiblen Schritt verifizieren kann
- **SOLLTE [SHOULD]** einen `dry_run: true`-Input auf `workflow_dispatch` unterstützen, der jeden Validierungsschritt durchführt, aber vor dem eigentlichen `--draft=false`-Call abbricht
- **SOLLTE [SHOULD]** explizit fehlschlagen (Non-Zero-Exit, handlungsfähige Fehlermeldung), wenn `release-cd-refresh-master.yml` fehlt oder deaktiviert ist, weil Publizieren ohne den nachgelagerten Refresh `main` aus dem Takt des letzten Releases laufen ließe

### Plugin-Manifest-Abgleich

- **MUSS [MUST]** für Repositories, die ein Claude-Code-Plugin ausliefern (`.claude-plugin/plugin.json` vorhanden), das `version`-Feld von `.claude-plugin/plugin.json` — und von `.claude-plugin/marketplace.json`, sofern der Eintrag existiert — so aktualisieren, dass es dem zu publizierenden Release-Tag entspricht, und diese Änderung auf `develop` mit einem Conventional-Commits-Subject `chore(release): <tag>` committen; der Commit **MUSS [MUST]** vor dem `--draft=false`-Aufruf landen, damit die Target-SHA des publizierten Releases das abgeglichene Manifest enthält
- **DARF NICHT [MUST NOT]** ein publiziertes Release bestehen lassen, dessen Tag vom `version`-Feld in `.claude-plugin/plugin.json` an der Target-SHA des Releases abweicht; jede Drift ist eine publish-blockierende Bedingung, die der Workflow vor dem Kippen des Drafts melden muss
- **DARF NICHT [MUST NOT]** ein manuell vorab erhöhtes Manifest im zu publizierenden Branch-Stand akzeptieren; wenn das `version`-Feld beim Workflow-Start bereits dem Ziel-Tag entspricht, **MUSS [MUST]** der Workflow verifizieren, dass der Match aus einem vorherigen `chore(release):`-Commit *dieses* Workflows stammt — andernfalls verweigert er den Publish, weil die Skill-Autoren-Specs (`skill-management`) Skill-Änderungs-PRs untersagen, das Versionsfeld anzufassen
- **SOLLTE [SHOULD]** das Manifest-Update innerhalb der Reusable `reusable-release-publish.yml` vornehmen, damit Konsumenten das Verhalten übernehmen, ohne es pro Repository zu wiederholen
- **SOLLTE [SHOULD]** den in das `version`-Feld geschriebenen Wert aus dem Tag ableiten, indem ein führendes `v` entfernt wird, falls die bestehende `version`-Konvention des Repos es weglässt; der Workflow **DARF NICHT [MUST NOT]** die Konvention still umschreiben
- **DARF [MAY]** das `marketplace.json`-Update überspringen, wenn das Repository keinen Marketplace-Eintrag publiziert

### Berechtigungen und Protection

- **MUSS [MUST]** mit `contents: write` und nicht breiter laufen; insbesondere **DARF NICHT [MUST NOT]** `actions: write`, `pull-requests: write` oder `id-token: write` anfordern, außer es ist in den Workflow-Kommentaren explizit begründet
- **DARF NICHT [MUST NOT]** den Branch-Schutz von `main` umgehen; Aufgabe des Workflows ist es, ein Release zu publizieren, was dann `release-cd-refresh-master.yml` triggert — der bestehende Workflow hat bereits die passend gescopte Berechtigung, `main` zu aktualisieren
- **DARF NICHT [MUST NOT]** ein Personal Access Token verwenden; `GITHUB_TOKEN` ist das einzig akzeptable Credential
- **MUSS [MUST]** berücksichtigen, dass ein `release: published`-Event, das dieser Workflow unter `GITHUB_TOKEN` erzeugt, **nicht** als neuer Workflow-Run an `release-cd-refresh-master.yml` kaskadiert — das ist deterministisches GitHub-Actions-Plattformverhalten, klassifiziert in `spec/project/workflow-health/` §Bekannte Plattform-Einschränkungen; die Remediation liegt stromaufwärts in `nolte/gh-plumbing` (Publish-Schritt mit App-Token oder PAT authentifizieren, damit das Event als user-initiiert gilt), nicht in diesem Workflow, und jede interimäre `main`-Refresh-Behelfslösung wird gemäß der dortigen Spec dokumentiert

### Verhältnis zu anderen Specs

- **MUSS [MUST]** `branching-model` §Release flow und §Local release operation durch In-Place-Edits aktualisieren — kein neuer dedizierter §Automated-release-promotion-Abschnitt — sodass: (a) der automatisierte Workflow als primärer Draft → Published-Pfad genannt wird und (b) die manuelle `gh release edit --draft=false`-Sequenz explizit als Fallback für Incident-Response gekennzeichnet ist
- **DARF NICHT [MUST NOT]** neu spezifizieren, was bereits in `branching-model` abgedeckt ist (Tag-Herkunft, `main`-Refresh, Workflow-Pinning) — stattdessen referenzieren
- **SOLLTE [SHOULD]** die Open Question in `project-structure` (zur Zeit Zeile 124) durch eine Querverlinkung aus `project-structure` §Release and documentation workflows in diese Spec auflösen

### Beobachtbarkeit und Audit

- **MUSS [MUST]** den Tag-Namen, den GitHub-Benutzernamen des Auslösers, die Workflow-Run-URL und den `created_at`-Timestamp des `release-drafter`-Drafts in die Job-Summary schreiben, damit Post-Release-Audits den Publish-Vorgang durch diesen Workflow zurückverfolgen können
- **SOLLTE [SHOULD]** einen Einzeilen-Eintrag in die Audit-Trail-Oberfläche des Repos anhängen (falls sich eine Konvention etabliert — aktuell nicht standardisiert); bis dahin ist die native Run-Historie von GitHub die Audit-Quelle
- **MUSS [MUST]** `gh run list --workflow=release-publish.yml` zur kanonischen CLI für Inspektion jüngster Publish-Aktivität machen — analog zu den Inspektions-Kommandos für `release-drafter.yml` und `release-cd-refresh-master.yml` in `branching-model` §Local release operation

## Akzeptanzkriterien

- [ ] `.github/workflows/release-publish.yml` existiert in jedem Repo, das `release-drafter.yml` und `release-cd-refresh-master.yml` besitzt
- [ ] Der Workflow deklariert `on: workflow_dispatch:` und deklariert keine `push`-, `pull_request`- oder `schedule`-Trigger
- [ ] Der `permissions:`-Block des Workflows (top-level oder job-level) fordert `contents: write` an und keinen breiteren Scope
- [ ] Der Workflow verwendet entweder `uses:` `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml@<tag>` oder ist eine temporäre lokale Implementierung mit einem getrackten Migrations-Issue
- [ ] Jede `uses: nolte/gh-plumbing/...`-Referenz ist auf einen Release-Tag gepinnt, nicht auf einen beweglichen Branch
- [ ] Der Workflow verweigert den Lauf (sichtbarer Fehler im Run-Log), wenn er aufgerufen wird, während kein `release-drafter`-Draft offen ist
- [ ] Ein `dry_run: true`-Dispatch-Input ist vorhanden und führt Validierung durch, ohne `draft: false` zu kippen
- [ ] Nach einem erfolgreichen Publish-Run gibt `gh release view <tag> --json isDraft` für den publizierten Tag `{"isDraft": false}` zurück
- [ ] Nach einem erfolgreichen Publish-Run zeigt `gh run list --workflow=release-cd-refresh-master.yml --limit 1` einen Run, der innerhalb von 5 Minuten nach dem Publish-Run gestartet ist — Bestätigung, dass der nachgelagerte Refresh gefeuert hat; falls er nicht gestartet ist, gilt der Publish als unvollständig und **MUSS [MUST]** unter `workflow-health` triagiert werden
- [ ] `branching-model` §Local release operation wurde aktualisiert, sodass `release-publish.yml` als primärer Pfad und `gh release edit <tag> --draft=false` als Fallback benannt ist
- [ ] Die letzten drei publizierten Releases in jedem Repo, das diese Spec adoptiert hat, wurden durch den `release-publish.yml`-Workflow erzeugt, verifizierbar über `gh run list --workflow=release-publish.yml --limit 10`
- [ ] Für jedes publizierte Release eines Plugin-ausliefernden Repos entspricht das `version`-Feld in `.claude-plugin/plugin.json` an der Target-SHA des Releases dem Release-Tag gemäß der bestehenden Konvention des Repos (mit oder ohne `v`-Präfix, konsistent zum vorherigen Manifest-Wert), und der `chore(release): <tag>`-Commit, der diesen Abgleich erzeugt hat, liegt auf `develop` vor dem Publish-Run
- [ ] Kein publiziertes Release im Adoption-Fenster hat einen `release-drafter`-Draft, der nach dem Publish zurückgeblieben ist (Bestätigung, dass der Workflow den intendierten Draft konsumiert hat und nicht einen parallelen erzeugt hat)

## Offene Fragen

Keine zum aktuellen Zeitpunkt — sämtliche Fragen aus der initialen Draftphase wurden während der Spec-Autorenschaft aufgelöst. Zur Nachvollziehbarkeit die getroffenen Entscheidungen:

- **Trigger**: beschränkt auf `workflow_dispatch`; label-basierte und Schedule-Trigger sind außerhalb des Scopes (zusätzliche Angriffsfläche; kollidiert mit „Mensch entscheidet, wann geshippt wird").
- **Kanonischer Reusable-Pfad**: `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml`, flacher Pfad konsistent mit der bestehenden Namenskonvention (`reusable-release-drafter.yml` / `reusable-release-cd-refresh-master.yml`).
- **Multi-Draft-Verhalten**: Fehlschlag mit handlungsfähiger Meldung, es sei denn, der Auslöser übergibt einen `tag`-Input; keine „newest-wins"-Heuristik.
- **`branching-model`-Integration**: In-Place-Edit von §Release flow + §Local release operation; kein neuer dedizierter Abschnitt.
- **Post-Publish-Sanity-Checks**: als Akzeptanzkriterien kodifiziert (`isDraft: false` und `release-cd-refresh-master.yml`-Run innerhalb von 5 Minuten), nicht als SHOULDs.
