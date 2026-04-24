# Workflow-Gesundheit

Status: draft

## Kontext
GitHub-Actions-Workflows kontrollieren jeden Weg durch das Portfolio: Pull-Request-Merges (`pr-lint.yml`, CI), Release-Entwurf (`release-drafter.yml`), `main`-Refresh beim Release (`release-cd-refresh-master.yml`), Dokumentationsauslieferung (`release-cd-deliver-docs.yml`) und optionale Packaging-Workflows. Wenn einer davon zu scheitern beginnt und der Fehler nicht bemerkt wird, bleiben Merges stehen, Releases werden nicht ausgeliefert und `main` entfernt sich vom zuletzt veröffentlichten Tag. Bestehende Spezifikationen legen fest, **welche** Workflows existieren müssen (`branching-model`), **wo** sie liegen und wie sie gepinnt sind (`project-structure`) und **welche Gates** sie für PRs bilden (`pull-request-workflow`). Keine dieser Spezifikationen legt den **operativen Prozess** fest, der diese Workflows zuverlässig grün hält und reagiert, wenn sie rot werden. Diese Spezifikation schließt diese Lücke, sodass Workflow-Fehler beobachtet, klassifiziert und über dasselbe PR-Gate wie jede andere Änderung behoben werden — nie verschwiegen, nie umgangen.

## Ziele
- Ein fehlschlagender Workflow-Run auf `develop` oder `main` wird nie stillschweigend ignoriert — jeder Fehler wird entweder behoben, explizit mit Verantwortlichem deaktiviert oder als bekannter Transient klassifiziert und nachgehalten
- Jede Behebung läuft über den regulären Pull-Request-Pfad (`fix/`-Branch, Conventional-Commits-Titel, erforderliche Checks grün) — es gibt keine Admin-Override-Abkürzung
- Root-Cause-Triage erfolgt vor Re-Runs — ein roter Workflow wird nie dadurch „repariert", dass man „Re-run" klickt, bis er zufällig grün wird
- Upstream-Drift (defekte Tags in `nolte/gh-plumbing`, geänderte Reusable-Workflows) wird sichtbar gemacht und durch Tag-Bump gelöst, nicht durch Entpinnen
- Der Prozess ist über alle Repositories hinweg identisch, sodass Menschen und KI-Agenten ohne repo-spezifisches Onboarding auf einen Fehler reagieren können

## Nicht-Ziele
- Welche Workflows in einem Repository existieren müssen (abgedeckt durch die Spezifikationen `branching-model` und `project-structure`)
- PR-Beschreibungsstruktur und CI-Gating-Mechanik (abgedeckt durch die Spezifikation `pull-request-workflow`)
- Der interne Inhalt einer konkreten Workflow-Datei (Job-Steps, Matrix-Strategie, Caching)
- Vorfälle, die vollständig außerhalb des Repositories entstehen — Ausfälle der GitHub-Actions-Plattform, Ausfälle von Probot-Apps, Registry-Ausfälle — über die Feststellung hinaus, dass sie vor der Zuweisung einer Fehlerursache an den Code ausgeschlossen werden müssen
- Inhalte von Release-Artefakten, Changelog-Generierung, Versionierungs-Policy
- Test-Autorenschaftskonventionen oder Root-Cause-Analyse von Flakes eines konkreten Tests (diese Spezifikation schreibt nur vor, dass Flakes nachgehalten werden)

## Anforderungen

### Sichtbarkeit und Erkennung
- **MUSS [MUST]** den Status jedes als Required-Status-Check für `develop` deklarierten Workflows per CI-Badge in `README.md` sichtbar machen, wie bereits von der `readme-structure`-Spezifikation gefordert; die Menge der Badges **MUSS [MUST]** mit der Menge der Required-Checks in `.github/settings.yml` übereinstimmen
- **MUSS [MUST]** die Standard-GitHub-Benachrichtigungen für Workflow-Fehler für mindestens eine verantwortliche Person des Repositories aktiviert lassen oder Benachrichtigungen in einen portfolio-weiten Kanal leiten, den eine verantwortliche Person beobachtet
- **SOLLTE [SHOULD]** einen roten Required-Status-Check auf `develop` als Merge-Flow-Vorfall behandeln — weitere Merges nach `develop` werden durch Branch-Protection ohnehin blockiert, sodass das Mittel der Wahl ist, den Fehler zu beheben, nicht den Check zu erlassen
- **SOLLTE [SHOULD]** einen roten Workflow auf `main` (zum Beispiel einen fehlgeschlagenen Lauf von `release-cd-refresh-master.yml`) als Release-Integritäts-Vorfall behandeln, weil `main` gemäß `branching-model`-Spezifikation Release-Präsentation ist und eine Abweichung vom aktuellsten Release-Tag ein Bug ist

### Triage vor Behebung
- **MUSS [MUST]** beim ersten Fehlschlag eines zuvor grünen Workflows die Ursache vor jedem Re-Run in genau eine der folgenden Kategorien einordnen:
  1. **defect** — eine Code- oder Konfigurationsänderung in diesem Repository hat den Workflow beschädigt
  2. **flake** — derselbe Commit-SHA wird bei einem Re-Run ohne Code-Änderung und ohne Infrastruktursignal grün
  3. **infra / transient** — Upstream-Provider-Ausfall, Registry-5xx, Rate-Limit, Netzwerk; nur in einem engen Zeitfenster reproduzierbar
  4. **stale pin** — ein in diesem Repository gepinnter `nolte/gh-plumbing`- (oder anderer Reusable-Workflow-) Tag erfüllt den erwarteten Kontrakt nicht mehr; ein neuerer Tag mit dem Fix existiert
  5. **secret / credential drift** — ein Token, Deploy-Key oder OIDC-Trust ist abgelaufen oder wurde rotiert
  6. **other** — explizit gekennzeichnet, mit einer kurzen Notiz im Fix-PR, die erklärt, warum es nicht in die fünf Kategorien passt
- **DARF NICHT [MUST NOT]** einen fehlgeschlagenen Workflow mehr als einmal ohne protokollierte Triage-Klassifikation neu starten; wiederholte blinde Re-Runs sind Drift
- **MUSS [MUST]** die Klassifikation im Abschnitt **Risk / rollout notes** des späteren Fix-PRs festhalten (gemäß `pull-request-workflow`-Spezifikation), sodass Fehlermuster über die PR-Historie hinweg sichtbar werden
- **KANN [MAY]** statt eines sofortigen Fix-PRs ein Tracking-Issue für eine nicht-dringende Nachverfolgung (Dokumentation eines bekannten Flakes, ein geplanter Upstream-Bump) anlegen, sofern das Issue eine verantwortliche Person benennt

### Bekannte Plattform-Einschränkungen

GitHub Actions löst absichtlich keine Downstream-Workflow-Runs aus, wenn das auslösende Event von einem Schritt stammt, der mit `GITHUB_TOKEN` authentifiziert ist — mit Ausnahme von `workflow_dispatch` und `repository_dispatch`. Das ist deterministisches Plattformverhalten, keine transiente Störung, und muss eingeplant statt bei jedem Auftreten einzeln triagiert werden.

- **MUSS [MUST]** jeden Downstream-Workflow, der nicht feuert, weil sein Trigger-Event von einem `GITHUB_TOKEN`-authentifizierten Schritt in der Automations-Kette erzeugt wurde, als bekannte Plattform-Einschränkung einordnen (Triage-Tag `infra`). Bisher beobachtete Ketten:
  - `release-drafter.yml` (Trigger: `push: develop`) feuert nicht, wenn der Push auf `develop` durch einen `automerge.yaml`-Squash-Merge mit `GITHUB_TOKEN` produziert wurde
  - `release-cd-refresh-master.yml` (Trigger: `release: published`) feuert nicht, wenn der Publish-Schritt durch `release-publish.yml` mit `GITHUB_TOKEN` ausgeführt wurde
  - Jede weitere Kette, in der das Output-Event eines Workflows das Trigger-Event eines anderen ist und der Erzeuger `GITHUB_TOKEN` benutzt
- **MUSS [MUST]** die Behebung dieser Einschränkung auf Portfolio-Ebene — in den Reusable-Workflows von `nolte/gh-plumbing` — erfolgen, nicht in jedem Konsumenten-Repository, weil die Einschränkung einheitlich für jeden Konsumenten dieser Reusables gilt. Zulässige Remediation: den downstream-auslösenden Schritt mit einem Credential authentifizieren, dessen Events GitHub als user-initiiert einstuft (Installation-Token einer GitHub-App oder PAT mit passenden Scopes), nicht `GITHUB_TOKEN`.
- **DARF NICHT [MUST NOT]** diese Einschränkung umgehen werden, indem in einem Konsumenten-Workflow `GITHUB_TOKEN` durch ein persönliches PAT ersetzt wird — der Fix gehört stromaufwärts ins Reusable, damit jeder Konsument von einem korrekt gescopten Credential profitiert und nicht jedes Repo seine eigene PAT-Sammlung pflegt.
- **SOLLTE [SHOULD]** jede Übergangs-Behelfslösung, die ein Repository anwendet (user-authored Commit, um `release-drafter` neu zu feuern, manuelles Fast-Forward von `main` nach verpasstem `release-cd-refresh-master.yml`-Run, manueller `workflow_dispatch`, falls der Downstream-Workflow einen anbietet), als Kurznotiz in `README.md` dokumentieren, mit Verweis auf das zugehörige Tracking-Issue in `nolte/gh-plumbing`.

### Behebungspfad
- **MUSS [MUST]** jede Workflow-Behebung über den regulären, in der `pull-request-workflow`-Spezifikation deklarierten Pull-Request-Pfad führen — Branch-Präfix `fix/`, Conventional-Commits-Titel (Type `fix`), alle erforderlichen Checks vor dem Merge grün
- **DARF NICHT [MUST NOT]** Branch-Protection umgehen, um einen Workflow-Fix zu mergen; `enforce_admins: true` auf `develop` (aus der `pull-request-workflow`-Spezifikation) hat keinen Ausnahmepfad, und ein dauerhaft defekter Required-Check wird durch einen PR gegen `.github/settings.yml` behoben, nicht durch einen Admin-Override
- **MUSS [MUST]** die Ursache beheben, anstatt sie zu maskieren — die folgenden Muster sind als Behebung unzulässig:
  - `continue-on-error: true` an einem Job der Required-Checks anbringen, um einen roten Job grün zu stellen
  - einen fehlschlagenden Job aus der Required-Checks-Menge in `.github/settings.yml` entfernen, ohne ein Issue zu eröffnen, das seine Wiedereinbeziehung verfolgt und eine verantwortliche Person benennt
  - eine `nolte/gh-plumbing`-Reusable-Workflow-Referenz von einem Release-Tag auf einen Branch (z. B. `@main`) umstellen, um einen unveröffentlichten Fix abzugreifen
  - Assertion-Steps auskommentieren oder Nicht-Null-Exit-Codes innerhalb eines Workflow-Steps verschlucken
- **MUSS [MUST]** jede `uses: nolte/gh-plumbing/.github/workflows/...`-Referenz auch während einer Behebung auf einen Release-Tag gepinnt lassen (gemäß `project-structure`- und `branching-model`-Spezifikationen); falls der aktuell gepinnte Tag defekt ist, ist die Lösung ein Tag-Bump auf eine neuere Version
- **KANN [MAY]** einen defekten **nicht erforderlichen** Workflow vorübergehend deaktivieren, indem seine `on:`-Trigger eingeschränkt oder er in der Actions-UI deaktiviert wird, sofern am selben Tag ein Tracking-Issue eröffnet wird, das eine verantwortliche Person und ein Wiederaktivierungs-Kriterium benennt; das vorübergehende Deaktivieren eines **erforderlichen** Workflows ist nicht zulässig — die Required-Checks-Menge ist die Quelle der Wahrheit

### Delegation an spezialisierte Claude-Agents zur Behebung
Die eigentliche Implementierungsarbeit einer Workflow-Behebung — das Bearbeiten des defekten Artefakts, der Bump eines Pins, die Rotation eines Secrets, das Erstellen des Fix-PRs — wird an den spezialisiertesten verfügbaren Claude-Agent delegiert. Die Verantwortung des generalistischen Claude ist Klassifikation und Delegation, nicht das eigenständige Bearbeiten des Artefakts.

- **MUSS [MUST]** die Implementierungsarbeit einer Behebung per `Agent(subagent_type=<name>)` (wie in der `agent-management`-Spezifikation geregelt) an den spezialisiertesten verfügbaren Claude-Agent delegieren, wenn die `description` mindestens eines Agents der Triage-Klassifikation oder dem konkreten defekten Artefakt (Workflow-YAML, Renovate-Pin-Bump, Secret-Rotation, Test-Defect, Dokumentations-Build usw.) entspricht
- **DARF NICHT [MUST NOT]** den delegierenden Claude selbst spezialisierte Behebungsarbeit ausführen lassen, wenn ein passender spezialisierter Agent existiert; der Generalist triagiert, delegiert und prüft das Ergebnis — er ersetzt den spezialisierten Agent nicht
- **MUSS [MUST]** eine Fehlerklasse, die drei oder mehr Male ohne passenden spezialisierten Agent wiedergekehrt ist, als handlungsbedürftige Portfolio-Lücke behandeln: entweder einen neuen Agent gemäß `agent-management`-Spezifikation autoren (`distribution: plugin`, wenn das Muster über Repositories hinweg wiederkehrt; `distribution: project`, wenn es repository-lokal ist) oder die `description` eines bestehenden Agents erweitern, sodass künftige Fehler derselben Klasse automatisch dorthin geroutet werden; Fehlerklassen mit weniger als drei Wiederholungen **SOLLTEN [SHOULD]** als Kandidaten für dieselbe Behandlung nachgehalten werden
- **SOLLTE [SHOULD]** einem Plugin-verteilten Agent (`distribution: plugin`) den Vorzug vor einem Projekt-lokalen Agent geben für Behebungsmuster, die portfolio-weit wiederkehren, sodass die Behebungsexpertise mit dem `nolte-shared`-Plugin reist und nicht pro Repository kopiert wird
- **SOLLTE [SHOULD]** im Abschnitt **Risk / rollout notes** des Fix-PRs (neben der Triage-Klassifikation, gemäß `pull-request-workflow`-Spezifikation) festhalten, welcher spezialisierte Agent den Fix erzeugt hat, oder vermerken, dass kein passender spezialisierter Agent existiert und ein Generalist die Arbeit übernommen hat — das macht portfolio-weite Abdeckungslücken sichtbar
- **KANN [MAY]** mehrere spezialisierte Agents verketten, wenn eine einzelne Behebung verschiedene Verantwortlichkeiten umspannt (zum Beispiel: ein Workflow-YAML-Fix-Agent zur Syntax-Korrektur, dann der `pull-request-create`-Agent zum Öffnen des Fix-PRs); jeder Agent in der Kette hält sich an seinen eigenen deklarierten `tools`-Scope
- **DARF NICHT [MUST NOT]** einem delegierten spezialisierten Agent erlauben, ein Gate aus dieser Spezifikation oder der `pull-request-workflow`-Spezifikation zu umgehen — der Agent liefert seine Änderung über denselben `fix/`-PR-Flow aus, mit allen erforderlichen Checks grün und ohne Admin-Override

### Upstream-Drift (`nolte/gh-plumbing`)
- **MUSS [MUST]** einen neuen Release von `nolte/gh-plumbing` als Bump-Kandidaten behandeln, nicht als automatischen Bump; der Bump erfolgt durch Aktualisierung des gepinnten Tags in jeder betroffenen `uses:`-Zeile, und das reguläre PR-Gate validiert das Ergebnis
- **SOLLTE [SHOULD]** Renovate nutzen, um den Tag-Bump als PR vorzuschlagen; der Renovate-PR selbst durchläuft das Gate wie jede andere Änderung
- **DARF NICHT [MUST NOT]** Renovate-Auto-Merge für `nolte/gh-plumbing`-Tag-Bumps aktivieren, selbst wenn jeder Required-Check grün ist — die menschliche Bestätigung ist das portfolio-weite Rollback-Signal für eine Reusable-Workflow-Änderung, und ihr Aufwand (Sekunden) liegt unter den Kosten eines Reusable-Workflow-Defects, der in jedes Consumer-Repository fan-out; andere Renovate-Auto-Merge-Regeln **KÖNNEN [MAY]** für Nicht-`nolte/gh-plumbing`-Pakete unverändert weiterbestehen
- **DARF NICHT [MUST NOT]** den PR-Schritt für einen Version-Bump von `nolte/gh-plumbing`-Referenzen überspringen, nur weil „es nur eine Tag-Änderung ist"; das Gate existiert genau, um diese Klasse von Brüchen abzufangen

### Verfügbarkeit der Probot-Apps
- **SOLLTE [SHOULD]** vor der Zuweisung eines Fehlers in `release-drafter.yml`, Settings-Sync oder Label-Sync an den Code prüfen, dass die zugrunde liegenden Probot-Apps (`settings`, `release-drafter`, `boring-cyborg`, `stale`) weiterhin im Repository installiert sind — das `project-structure-apply`-Audit prüft dies
- **MUSS [MUST]** „Probot-App deinstalliert" als von einem Code-Defect unterschiedliche Konfigurations-Drift behandeln; die Behebung ist eine erneute Autorisierung der App, nicht eine Änderung am Repository-Code

### Umgang mit Flakes
- **MUSS [MUST]** einen Lauf nur dann als Flake einstufen, wenn der Nachweis reproduzierbar ist — ein Re-Run desselben Commit-SHAs ohne Code-Änderung wird grün, und kein Upstream-Infrastruktursignal erklärt den ersten Fehlschlag
- **MUSS [MUST]** bekannte Flakes in einem im Repository sichtbaren Artefakt führen, sodass Muster sichtbar sind und nicht stillschweigend in die Re-Run-Schleife absorbiert werden; der portfolio-weite Default ist eine `FLAKES.md` im Repository-Root, und eine dedizierte Menge von GitHub-Issues mit Label `flake` ist als Äquivalent zulässig, wenn das Repository Tracking ohnehin in Issues zentralisiert
- **DARF NICHT [MUST NOT]** beide Formen (`FLAKES.md` und eine Issue-Menge mit Label `flake`) für dasselbe Repository gleichzeitig pflegen — eine der beiden ist autoritativ, wird bewusst gewählt und aus `CLAUDE.md` oder `README.md` heraus verlinkt
- **SOLLTE [SHOULD]** einen Flake, der einen Required-Check in mehr als rund einem von zehn Läufen stolpern lässt, als Defect und nicht als Transient behandeln — bei dieser Rate blockiert der Flake Merges material und verdient einen echten Fix statt eines Tracking-Eintrags

### Zeitliche Erwartungen
- **SOLLTE [SHOULD]** einen fehlgeschlagenen Required-Check auf `develop` innerhalb eines Werktags nach Auftreten zur Kenntnis nehmen und innerhalb von zwei Werktagen einen Fix-PR geöffnet haben
- **SOLLTE [SHOULD]** einen fehlgeschlagenen Release-Flow-Workflow auf `main` (zum Beispiel `release-cd-refresh-master.yml`) mit höherer Dringlichkeit behandeln als einen `develop`-Fehler, weil er die korrekte Präsentation des nächsten Release blockiert
- **KANN [MAY]** diese Fenster ausdehnen, wenn das Repository explizit auf Low-Maintenance-Status steht, sofern dieser Status in `README.md` oder `CLAUDE.md` erklärt wird, damit spätere Lesende verstehen, warum rote Checks verbleiben

### Drittanbieter-Required-Checks
Required-Status-Checks auf `develop` können auch Anbieter umfassen, die keine GitHub-Actions-Workflows sind — SaaS-Code-Quality-Bots, Security-Scanner, Coverage-Reporter, Signed-Commit-Verifizierer. Dieselben operativen Regeln gelten.

- **MUSS [MUST]** die Triage-Klassifikationen und den Behebungspfad dieser Spezifikation auf Drittanbieter-Required-Status-Checks genauso anwenden wie auf GitHub-Actions-Workflows — das PR-Gate, die No-Override-Regel, die Pinned-Tag-Disziplin (soweit analog anwendbar) und die Delegation an spezialisierte Agents gelten identisch
- **MUSS [MUST]** jede Entfernung oder Deaktivierung eines Drittanbieter-Required-Checks als PR gegen `.github/settings.yml` deklarieren, nicht als Änderung ausschließlich über die UI des Anbieters; UI-only-Änderungen sind Drift und müssen in die Datei zurückgeführt werden
- **MUSS [MUST]** einen Ausfall eines Drittanbieter-Check-Providers für die Triage als `infra / transient` einstufen, nicht als `defect`
- **KANN [MAY]** den „Check deaktivieren"-Mechanismus des Anbieters anstelle einer `on:`-Trigger-Einschränkung (die außerhalb von Actions nicht anwendbar ist) nutzen, wenn ein **nicht erforderlicher** Drittanbieter-Check pausiert werden soll; ein Tracking-Issue mit verantwortlicher Person und Wiederaktivierungs-Kriterium ist weiterhin erforderlich, genau wie bei Actions-Workflows

### Auditing
- **SOLLTE [SHOULD]** regelmäßig `gh run list --status failure --branch develop --limit 20` und `gh run list --status failure --branch main --limit 20` prüfen, um einen Rückstau unbehobener Fehler zu erkennen, die an den Benachrichtigungen vorbeigerutscht sind
- **SOLLTE [SHOULD]** einen Workflow-Health-Durchgang in jedes Portfolio-Audit aufnehmen, das bereits `.github/workflows/` besucht (zum Beispiel das `project-structure-apply`-Skill); das Audit gleicht ab, dass kein Required-Check-Workflow am HEAD aktuell rot ist, ohne dass ein Fix-PR in Bearbeitung ist

## Akzeptanzkriterien
- [ ] Die `README.md`-CI-Badges decken jeden in `.github/settings.yml` als Required-Status-Check für `develop` gelisteten Workflow ab; beide Mengen stimmen exakt überein
- [ ] `gh run list --status failure --branch develop --limit 20` zeigt keinen fehlgeschlagenen Lauf älter als zwei Werktage, der nicht entweder (a) durch einen grünen Lauf auf einem späteren SHA abgelöst ist oder (b) von einem offenen `fix/`-PR abgedeckt wird
- [ ] `gh run list --status failure --branch main --limit 20` zeigt keinen fehlgeschlagenen Lauf eines Release-Flow-Workflows ohne entweder einen Behebungs-Commit auf `develop` oder ein offenes Tracking-Issue
- [ ] Keine Workflow-Datei unter `.github/workflows/` enthält `continue-on-error: true` an einem Step oder Job, der zur in `.github/settings.yml` deklarierten Required-Checks-Menge gehört
- [ ] Jede `uses: nolte/gh-plumbing/.github/workflows/...`-Referenz unter `.github/workflows/` löst sich auf einen Release-Tag auf (passt zu `@v[0-9]+`), nicht auf einen Branch-Namen
- [ ] Die letzten 10 PRs, die `.github/workflows/` oder Pin-Bumps von `nolte/gh-plumbing` berühren, wurden jeweils über den regulären PR-Flow gemergt (Squash-Merge, Required-Checks grün, kein Admin-Override)
- [ ] Die Renovate-Konfiguration des Repositories mergt `nolte/gh-plumbing`-Tag-Bumps nicht automatisch — entweder greift keine Auto-Merge-Regel für diese Dependency, oder die Regel schließt `nolte/gh-plumbing` explizit aus
- [ ] Wenn das Repository einen Drittanbieter-Required-Status-Check für `develop` deklariert, spiegelt `.github/settings.yml` dessen Entfernung oder Deaktivierung wider, nicht ausschließlich die UI des Anbieters
- [ ] Für die letzten 10 Workflow-Fix-PRs benennt der Abschnitt **Risk / rollout notes** die Triage-Klassifikation (`defect`, `flake`, `infra`, `stale pin`, `secret drift` oder `other` mit Kurznotiz)
- [ ] Für dieselben 10 Workflow-Fix-PRs benennt der Abschnitt **Risk / rollout notes** entweder den spezialisierten Claude-Agent, der den Fix erzeugt hat (per `Agent(subagent_type=…)`), oder vermerkt, dass kein passender spezialisierter Agent existiert und ein Generalist die Arbeit übernommen hat
- [ ] Wenn eine Fehlerklasse drei oder mehr Male wiedergekehrt ist und jedes Mal von einem Generalisten behandelt wurde, existiert entweder mittlerweile ein spezialisierter Agent im Plugin (gemäß `agent-management`-Spezifikation) oder ein offenes Issue verfolgt seine Erstellung mit benannter verantwortlicher Person
- [ ] Jeder vorübergehend deaktivierte Workflow (eingeschränkte `on:`-Trigger, auskommentierter Job, in der Actions-UI deaktiviert) ist von einem Tracking-Issue begleitet, das eine verantwortliche Person und ein Wiederaktivierungs-Kriterium benennt; kein Required-Workflow befindet sich in diesem Zustand
- [ ] Ein Register bekannter Flakes existiert im Repository — entweder `FLAKES.md` im Repository-Root oder ein Set von Issues mit Label `flake`, aber nicht beides — sobald mindestens ein Flake beobachtet und anerkannt wurde; das Register ist aus `CLAUDE.md` oder `README.md` heraus verlinkt und damit auffindbar
- [ ] `.github/settings.yml` deklariert weiterhin die vollständige Required-Checks-Menge für `develop` als Code; kein Required-Check wurde stillschweigend entfernt, um einen dauerhaften Fehler zu umgehen

## Offene Fragen
- _Derzeit keine; alle Entwurfsfragen sind geklärt._
