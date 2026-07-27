# Release-Automation

Status: draft
Portfolio-Scope: portfolio

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
- Erzeugung von Release-Notes-Inhalten — bleibt Aufgabe von `release-drafter`, gespeist durch Conventional-Commits-PR-Titel. Für die Zielgruppenanalyse, die festlegt, welche Inhalte diese Notes abdecken müssen, siehe die Release-Notes-Zielgruppenanalyse-Konventionen des Repositories.
- Versionierungspolitik (SemVer-Ableitung von major/minor/patch) — geerbt aus der `release-drafter`-Konfiguration in `nolte/gh-plumbing:.github/commons-release-drafter.yml`.
- Hotfix-Flow — gehört zu `branching-model` §Hotfix flow, das ihn als Standard-`fix/`-Pull-Request gegen `develop` mit nachfolgendem gewöhnlichem Patch-Release festlegt; außerhalb des Scopes hier.
- Vollständige Abschaffung des manuellen `gh release edit --draft=false`-Pfads; der manuelle Pfad bleibt als dokumentierter Fallback für Incident-Response, wenn der Workflow selbst kaputt ist.
- Vorschrift darüber, welche Ökosysteme in die Portfolio-Konventions-Tabelle in §Versionstragende Dateien aufgenommen werden; die Tabelle wächst organisch, sobald Repos neuer Typen ins Portfolio kommen, jede Ergänzung ist eine kleine Spec-Änderung, keine neue Spec.

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

### Versionstragende Dateien

Eine *versionstragende Datei* ist eine in git verfolgte Datei, die an einer wohldefinierten Stelle die aktuelle Release-Version des Projekts deklariert. Jede solche Datei muss an der Target-SHA des publizierten Releases dem Release-Tag entsprechen. Repositories dürfen null, eine oder mehrere solcher Dateien haben.

**Portfolio-Konventions-Tabelle.** Standard-versionstragende Dateien pro Repo-Typ:

| Repo-Typ | Datei | Selector | Wert-Transformation |
|---|---|---|---|
| Claude-Code-Plugin | `.claude-plugin/plugin.json` | `$.version` | führendes `v` entfernen, falls die Repo-Konvention es weglässt |
| Claude-Code-Plugin | `.claude-plugin/marketplace.json` | `$.metadata.version` und `$.plugins[].version` | führendes `v` entfernen, falls die Repo-Konvention es weglässt |
| Python-Paket | `pyproject.toml` | `[project].version` | führendes `v` entfernen, falls die Repo-Konvention es weglässt |
| Node.js-Paket | `package.json` | `$.version` | führendes `v` entfernen, falls die Repo-Konvention es weglässt |
| HACS-Integration | `custom_components/<name>/manifest.json` | `$.version` | führendes `v` entfernen, falls die Repo-Konvention es weglässt |

- **MUSS [MUST]** diese Tabelle als Default-Satz für jedes Repo behandeln, dessen Typ einer der gelisteten Zeilen entspricht; keine repo-lokale Deklaration nötig, um zu „opt-in".
- **MUSS [MUST]** die vollständige Liste versionstragender Dateien in `.github/release-automation.yml` deklarieren, wenn ein Repo von der Konvention seines Ökosystems abweicht (zusätzliche Dateien, abweichende Selectors, eine repo-lokale Datei mit Versionsangabe). Die deklarierte Liste **ersetzt** den Default, sie erweitert ihn nicht — explizit schlägt implizit.
- **DARF [MAY]** gar keine versionstragenden Dateien haben (etwa rein git-tag-basierte Versionierung wie Go-Module); der Verifikationsschritt in §Abgleich versionstragender Dateien behandelt „keine Dateien" als „nichts abzugleichen".
- **DARF NICHT [MUST NOT]** eine Repo-Typ-Zeile zu dieser Tabelle hinzufügen, ohne einen zugehörigen Änderungs-PR auf diese Spec; Ad-hoc-Konventionen erzeugen Drift im Portfolio.

Selectors in JSONPath-Notation für JSON- und YAML-Dateien, TOML-Path-Notation für TOML-Dateien. Die Wert-Transformation wird auf den Tag angewandt, bevor der Wert geschrieben oder verglichen wird — „führendes `v` entfernen, falls die Repo-Konvention es weglässt" bedeutet: `v0.1.1` wird zu `0.1.1` nur dann, wenn der bestehende Wert in der Datei kein `v`-Präfix hat; hat die Datei bereits ein `v`-Präfix, wird der Tag wortwörtlich übernommen.

### Abgleich versionstragender Dateien

Jeder publizierte Release **MUSS [MUST]** auf einem Commit landen, dessen Tree jede versionstragende Datei (§Versionstragende Dateien) auf den Ziel-Tag unter ihrer Wert-Transformation bringt. Der Abgleich-Commit **MUSS [MUST]** das Conventional-Commits-Subject `chore(release): <tag>` tragen und **MUSS [MUST]** vor dem `--draft=false`-Aufruf auf `develop` landen.

Der Abgleich geschieht über einen von zwei gleichwertigen Pfaden. Beide Pfade erzeugen denselben End-Zustand; sie unterscheiden sich nur darin, welches Credential den Commit erzeugt.

#### Primary Path: Workflow-getrieben

Anwendbar, sobald der Workflow Zugang zu einem Credential hat, das den Branch-Schutz von `develop` umgehen darf (GitHub-App-Installation-Token oder PAT, der explizit als Bypass-Actor deklariert ist). Im aktuellen Portfolio noch nicht nutzbar — der App-Token/PAT wird über `nolte/gh-plumbing` bereitgestellt (dieselbe Portfolio-Remediation wie in `spec/project/workflow-health/` §Bekannte Plattform-Einschränkungen).

- **MUSS [MUST]** die Liste versionstragender Dateien lesen (Default aus §Versionstragende Dateien oder die Liste in `.github/release-automation.yml`, falls das Repo abweicht) und jede Datei auf den Ziel-Tag unter ihrer Transformation aktualisieren
- **MUSS [MUST]** das aggregierte Update als `chore(release): <tag>` auf `develop` committen, authentifiziert vom Bypass-Credential
- **MUSS [MUST]** den Commit mit dem Bypass-Credential auf `develop` pushen, wobei `enforce_admins: true` respektiert wird (der Bypass ist deklariert, nicht gestohlen)
- **DARF NICHT [MUST NOT]** in einem Repository aktiviert werden, solange der Portfolio-App-Token/PAT nicht installiert ist und `.github/settings.yml` das Credential nicht explizit als Bypass-Actor nennt; andernfalls scheitert der Push und der Fallback Path **MUSS [MUST]** genutzt werden

#### Fallback Path: Operator-getrieben

Anwendbar, wenn nur `GITHUB_TOKEN` zur Verfügung steht und `develop` vollständig geschützt ist (aktueller Portfolio-Default).

- **MUSS [MUST]** von einem Maintainer ausgeführt werden, der einen PR mit dem Titel `chore(release): <tag>` eröffnet, der jede versionstragende Datei auf den Ziel-Tag aktualisiert
- **MUSS [MUST]** alle für `develop` in `.github/settings.yml` deklarierten Required-Status-Checks bestehen
- **MUSS [MUST]** vom Maintainer via GitHub-UI squash-gemergt werden, **nicht** über das `automerge`-Label — ein `automerge`-Label-Merge läuft unter `GITHUB_TOKEN` und unterbricht die release-drafter-Cascade gemäß `spec/project/workflow-health/` §Bekannte Plattform-Einschränkungen
- **MUSS [MUST]** gefolgt sein von einem `workflow_dispatch` von `release-publish.yml`; der Workflow erkennt, dass das Manifest bereits abgeglichen ist, skipped seinen eigenen Commit-Step, realigniert `target_commitish` am Draft und flipt `draft: false`

#### Pre-Publish-Verifikation (beide Pfade)

- **MUSS [MUST]** vor dem `--draft=false`-Aufruf verifizieren, dass jede versionstragende Datei an der Target-SHA des Drafts dem Ziel-Tag unter ihrer Transformation entspricht; jede Drift ist eine publish-blockierende Bedingung, die der Workflow meldet und verweigert
- **MUSS [MUST]** eine vorab abgeglichene Datei **nur dann** akzeptieren, wenn das jüngste Commit, das diese Datei auf `develop` anfasst, ein Subject trägt, das mit `chore(release): <tag>` **beginnt** — das lässt den `(#N)`-Suffix zu, den GitHub beim Squash-Merge anhängt; ein Fallback-Path-Squash-Merge-Commit mit dem Subject `chore(release): v0.1.1 (#21)` passiert die Prüfung
- **MUSS [MUST]** jeden anderen vorab abgeglichenen Zustand als verbotenen manuellen Bump zurückweisen; der Skill-Autoren-Vertrag untersagt Feature-PRs das Anfassen des Versionsfelds, sodass die einzig zulässigen Pre-Alignment-Quellen ein vorheriger Primary-Path-Lauf oder ein Fallback-Path-`chore(release): <tag>`-PR-Merge sind
- **SOLLTE [SHOULD]** die Verifikation innerhalb der Reusable `reusable-release-publish.yml` vornehmen, damit Konsumenten das Verhalten übernehmen, ohne es pro Repository zu wiederholen
- **SOLLTE [SHOULD]** den in (Primary Path) geschriebenen oder (beide Pfade) verglichenen Wert aus dem Tag ableiten, indem ein führendes `v` entfernt wird, falls die bestehende Konvention des Repos es weglässt, passend zum bisherigen Wert in der Datei — der Workflow **DARF NICHT [MUST NOT]** die Konvention still umschreiben

### Vererbbare Spec-Payload

Die portfolio-vererbte Spec-Schicht erlaubt es einem Consumer-Repository, die portfolioweiten Specs des Hubs an einem gepinnten Release-Tag zu referenzieren statt zu kopieren; jener Mechanismus delegiert das Marketplace-Payload-Packaging an diese Spec, sodass die Auslieferungs-Garantie hier deklariert wird.

- **MUSS [MUST]** den `spec/`-Korpus des Repositories als Teil der Plugin-Payload ausliefern, sodass für ein installiertes Hub-Plugin jede Spec, deren kanonische Datei eine `Portfolio-Scope: portfolio`-Header-Zeile trägt, unter `${CLAUDE_PLUGIN_ROOT}/spec/` lesbar ist (die Bundled-Asset-Pfad-Konvention, die jeder Plugin-Skill bereits nutzt). Die Plugin-Source-Wurzel ist der Resolver-Einstiegspunkt, und `spec/` wird darunter ausgeliefert.
- **DARF NICHT [MUST NOT]** `spec/` über einen Packaging-Filter aus der Plugin-Payload ausschließen — eine `files`-Allowlist in einem Plugin-Manifest, eine `.gitattributes export-ignore`-Regel, eine `.npmignore`-artige Ausschlussregel oder Äquivalentes. Der Korpus wird vollständig ausgeliefert; die `Portfolio-Scope:`-Header-Zeile ist das einzige Vererbbarkeits-Gate, angewendet zur Auflösungszeit, nie zur Packaging-Zeit. Die nicht-`portfolio`-Specs (`local`) werden mit ausgeliefert, von einem Consumer aber schlicht nie aufgelöst.
- **MUSS [MUST]** diese Payload an die Plugin-Release-Linie tag-pinnen: der gepinnte `ref` eines Consumers wählt das installierte Hub-Plugin-Release, und der aus diesem Release aufgelöste `spec/`-Korpus ist der regenerierbare Cache, den der Consumer referenziert — niemals eine in den eigenen Baum des Consumers committete Kopie.

### Berechtigungen und Protection

- **MUSS [MUST]** mit `contents: write` und nicht breiter laufen; insbesondere **DARF NICHT [MUST NOT]** `actions: write`, `pull-requests: write` oder `id-token: write` anfordern, außer es ist in den Workflow-Kommentaren explizit begründet
- **DARF NICHT [MUST NOT]** den Branch-Schutz von `main` umgehen; Aufgabe des Workflows ist es, ein Release zu publizieren, was dann `release-cd-refresh-master.yml` triggert — der bestehende Workflow hat bereits die passend gescopte Berechtigung, `main` zu aktualisieren
- **MUSS [MUST]** auf dem Fallback Path `GITHUB_TOKEN` verwenden (der Workflow braucht dort nur Lese- und Release-Edit-Berechtigung); **MUSS [MUST]** auf dem Primary Path den Portfolio-App-Installation-Token (oder einen designierten PAT) verwenden — siehe §Abgleich versionstragender Dateien für die Pfad-Unterscheidung
- **DARF NICHT [MUST NOT]** einen PAT verwenden, der nicht explizit in `.github/settings.yml` als Branch-Protection-Bypass-Actor deklariert ist; nicht deklarierte PATs umgehen den Audit-Trail
- **MUSS [MUST]** berücksichtigen, dass ein `release: published`-Event, das dieser Workflow unter `GITHUB_TOKEN` erzeugt, **nicht** als neuer Workflow-Run an `release-cd-refresh-master.yml` kaskadiert — deterministisches GitHub-Actions-Plattformverhalten, klassifiziert in `spec/project/workflow-health/` §Bekannte Plattform-Einschränkungen; dieselbe App-Token-Remediation, die den Primary Path oben ermöglicht, behebt auch diese Cascade-Einschränkung, beide werden also durch einen einzigen Portfolio-Fix in `nolte/gh-plumbing` gelöst

### Release-Notes-Kategorisierung

- **MUSS [MUST]** `chore(release): <tag>`-Commits und -PRs aus der `release-drafter`-Kategorisierung ausschließen, damit ein Release-Draft nicht seinen eigenen Version-Alignment-PR als Changelog-Eintrag listet
- **MUSS [MUST]** den Ausschluss portfolioweit in `nolte/gh-plumbing:.github/commons-release-drafter.yml` implementieren (Titel-Pattern-Ausschluss oder Label-Konvention, die die Drafter-Config filtert), nicht pro Repo
- **SOLLTE [SHOULD]** den Ausschluss mit bestehenden Conventional-Commits-Filtern in der Commons-Drafter-Config abstimmen, damit das Regel-Pattern konsistent bleibt

### Verhältnis zu anderen Specs

- **MUSS [MUST]** `branching-model` §Release flow und §Local release operation durch In-Place-Edits aktualisieren — kein neuer dedizierter §Automated-release-promotion-Abschnitt — sodass: (a) der automatisierte Workflow als primärer Draft → Published-Pfad genannt wird und (b) die manuelle `gh release edit --draft=false`-Sequenz explizit als Fallback für Incident-Response gekennzeichnet ist
- **DARF NICHT [MUST NOT]** neu spezifizieren, was bereits in `branching-model` abgedeckt ist (Tag-Herkunft, `main`-Refresh, Workflow-Pinning) — stattdessen referenzieren
- **SOLLTE [SHOULD]** die Open Question in `project-structure` (zur Zeit Zeile 164) durch eine Querverlinkung aus `project-structure` §Release and documentation workflows in diese Spec auflösen
- **MUSS [MUST]** von `release-artifact` als Autorität für den Übergang Draft → Veröffentlicht querreferenziert werden. `release-artifact` §Dispatch-Grenze zur Release-Maschinerie leitet sprint-seitige Artefakt-Validierungs-Ergebnisse in den Workflow weiter, den diese Spec regiert; die Grenze ist einseitig (diese Spec ist die untere Schicht, `release-artifact` ist die obere), und die konsumierende Spec **DARF NICHT [MUST NOT]** eine hier deklarierte Regel neu definieren
- Das lokale Skill-Gegenstück zu diesem Workflow liegt in [`spec/project/release-skill-layer/`](../release-skill-layer/de.md): Skill A (`release-notes-curate`) übernimmt die Body-Kuratierung via `gh release edit` außerhalb dieses Workflows, und Skill B (`release-publish-trigger`) ist der lokale ergonomische Einstiegspunkt, der jeden Gate aus §Pre-Publish-Verifikation validiert und dann diesen Workflow via `gh workflow run` dispatcht. Diese Spec **DARF NICHT [MUST NOT]** `gh release edit --draft=false` aufrufen; der einzige Veröffentlichungsweg ist der Dispatch dieses Workflows.

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
- [ ] Für jedes publizierte Release eines Repos, das versionstragende Dateien deklariert (per §Versionstragende Dateien Default oder Override), entspricht jede deklarierte Datei an der Target-SHA des Releases dem Release-Tag unter ihrer deklarierten Transformation, und ein `chore(release): <tag>`-Commit auf `develop` hat diesen Abgleich vor dem Publish-Run erzeugt — entweder via Primary oder Fallback Path
- [ ] Bei den letzten drei publizierten Releases in jedem Repo, das diese Spec adoptiert hat, beginnt das Subject des `chore(release): <tag>`-Commits auf `develop` (via `git log -1 --pretty=%s`) mit `chore(release): <tag>` — bestätigt, dass das Präfix-Match-Akzeptanzkriterium des Guards sowohl Primary-Path-Commits als auch Fallback-Path-Squash-Merges mit `(#N)`-Suffix erfasst
- [ ] `nolte/gh-plumbing:.github/commons-release-drafter.yml` schließt `chore(release): <tag>`-Commits oder -PRs aus der Release-Notes-Kategorisierung aus (§Release-Notes-Kategorisierung)
- [ ] Kein publiziertes Release im Adoption-Fenster hat einen `release-drafter`-Draft, der nach dem Publish zurückgeblieben ist (Bestätigung, dass der Workflow den intendierten Draft konsumiert hat und nicht einen parallelen erzeugt hat)
- [ ] An einem publizierten Release-Tag stellt das installierte `nolte-shared`-Plugin `spec/` unter `${CLAUDE_PLUGIN_ROOT}/spec/` bereit, ohne dass ein Packaging-Filter es ausschließt, sodass jede Spec, deren kanonische Datei `Portfolio-Scope: portfolio` trägt, dort für einen erbenden Consumer auflösbar ist (§Vererbbare Spec-Payload)

## Offene Fragen

Keine zum aktuellen Zeitpunkt — sämtliche Fragen aus der initialen Draftphase wurden während der Spec-Autorenschaft aufgelöst. Zur Nachvollziehbarkeit die getroffenen Entscheidungen:

- **Trigger**: beschränkt auf `workflow_dispatch`; label-basierte und Schedule-Trigger sind außerhalb des Scopes (zusätzliche Angriffsfläche; kollidiert mit „Mensch entscheidet, wann geshippt wird").
- **Kanonischer Reusable-Pfad**: `nolte/gh-plumbing/.github/workflows/reusable-release-publish.yml`, flacher Pfad konsistent mit der bestehenden Namenskonvention (`reusable-release-drafter.yml` / `reusable-release-cd-refresh-master.yml`).
- **Multi-Draft-Verhalten**: Fehlschlag mit handlungsfähiger Meldung, es sei denn, der Auslöser übergibt einen `tag`-Input; keine „newest-wins"-Heuristik.
- **`branching-model`-Integration**: In-Place-Edit von §Release flow + §Local release operation; kein neuer dedizierter Abschnitt.
- **Post-Publish-Sanity-Checks**: als Akzeptanzkriterien kodifiziert (`isDraft: false` und `release-cd-refresh-master.yml`-Run innerhalb von 5 Minuten), nicht als SHOULDs.
- **Zwei-Pfad-Alignment**: Primary (Workflow-getrieben mit Bypass-Credential) vs. Fallback (Operator-PR + UI-Squash-Merge); beide Pfade landen dieselbe `chore(release): <tag>`-Commit-Form. Primary ist das Portfolio-Ziel; Fallback ist der heute operative Pfad, bis der Portfolio-App-Token/PAT über `nolte/gh-plumbing` ausgeliefert wird.
- **Override-Config-Pfad**: `.github/release-automation.yml` für Repos, die vom Default aus §Versionstragende Dateien abweichen; konsistent mit anderen `.github/*.yml`-Portfolio-Configs.
- **Portfolio-Konventions-Tabelle-Umfang**: vollständige Liste (Claude-Plugin, Python, Node, HACS) dokumentiert die Portfolio-Vision; Zeilen wachsen organisch mit neuen Ökosystemen via kleine Spec-Änderungen.
- **Pre-Bump-Guard**: Präfix-Match auf `chore(release): <tag>`, akzeptiert den `(#N)`-Suffix, den GitHub beim Squash-Merge anhängt.

## Quellen

Das `GITHUB_TOKEN`-kaskadiert-nicht-Plattformverhalten in §Berechtigungen und Schutz ist eine Author-Time-externe Aussage, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-Time-Aussagen" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Es wird unter `spec/project/workflow-health/` §Bekannte Plattform-Constraints klassifiziert und referenziert, das dieselben Quellen zitiert. Abrufdatum für jede Web-Quelle unten: 2026-07-24.

- **GitHub Actions löst aus Events, die mit dem automatischen `GITHUB_TOKEN` erzeugt wurden, keine neuen Workflow-Läufe aus, außer `workflow_dispatch` und `repository_dispatch`**: GitHub Docs, „Triggering a workflow" (Primary), `https://docs.github.com/en/actions/using-workflows/triggering-a-workflow`; GitHub Changelog, „Use the GITHUB_TOKEN with workflow_dispatch and repository_dispatch" (Primary), `https://github.blog/changelog/2022-09-08-github-actions-use-github_token-with-workflow_dispatch-and-repository_dispatch/`; GitHub-Community-Discussion #25702, „Push from Action does not trigger subsequent action" (Secondary), `https://github.com/orgs/community/discussions/25702`
- **Empirischer Portfolio-Beleg**: der eigene `v0.1.5`-Release-Lauf des Portfolios bestätigte dieses Verhalten direkt, als ein von diesem Workflow unter `GITHUB_TOKEN` emittiertes `release: published`-Event nicht als neuer Lauf zu `release-cd-refresh-master.yml` kaskadierte (Primary, direkte Beobachtung; erfasst in der Release-Prozess-Verifikation für `nolte/claude-shared`).
