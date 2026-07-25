# Error Tracking

Status: draft

## Kontext

Eine Anwendung, die Fehler nur in Logs schreibt, zwingt ihre Betreiber zum Ziehen: Jemand muss das Log-Backend öffnen, wissen, wonach zu suchen ist, und einen einzelnen Fehlschlag aus vielen verstreuten Zeilen rekonstruieren. Eine **Error-Tracking-Plattform** kehrt das in ein Push-Modell um: Das SDK der Anwendung fängt jede unbehandelte Exception mit ihrem vollen Kontext ein (Stack Trace, Request-Daten, Laufzeitumgebung, Release, Environment), die Plattform **gruppiert** wiederkehrende Events zu deduplizierten *Issues*, zählt sie und zeigt Trends, erkennt, wenn ein behobenes Issue in einem späteren Release **regressiert**, und **alarmiert** das zuständige Team, sobald etwas Neues oder Wiederkehrendes auftaucht. Dieser Issue-zentrische Workflow — sehen, triagieren, beheben, verifizieren — ist der Mechanismus, mit dem das Tool Eigenentwicklungen verbessert: Defekte werden Minuten nach ihrem ersten Auftreten in irgendeiner Umgebung sichtbar, nicht Wochen später über ein Support-Ticket.

Das Referenz-Tool dieser Spec ist **GlitchTip** (<https://glitchtip.com/>): Open Source (MIT-lizenziertes Backend), selbst hostbar oder gehostet, kompatibel mit den Sentry-Client-SDKs, mit Error Tracking plus Uptime-Monitoring, grundlegendem Performance-Tracing und Log-Erfassung. Der Vertrag unten bindet jedoch die **Fähigkeitsklasse**, nicht das Produkt: Jede Plattform, die das Sentry-SDK-Protokoll spricht und Gruppierung, Environments, Releases, Alerting und einen Issue-Lebenszyklus bietet, erfüllt ihn (Sentry selbst, Bugsink und vergleichbare Tracker). Am 2026-07-25 gegen die Herstellerquellen verifiziert; siehe Referenzen.

Das Tool ist in **jeder Lebenszyklusphase einer Anwendung nützlich, aber mit unterschiedlichen Anforderungen pro Phase**. Während der *Entwicklung* liefert es schnelles Feedback, ohne Produktionsdaten zu verschmutzen; in *Test/Staging* fängt es Regressionen unter produktionsgleicher Verdrahtung vor einem Release ab; im *Produktionsbetrieb* ist es der primäre Detektor für echte Nutzer-Fehlschläge und der Auslöser der Fix-Schleife. Ein großer Teil dieser Spec ist deshalb der Pro-Phase-Vertrag, plus die Pflichten, die der Betrieb eines solchen Tools überhaupt mit sich bringt (Datenschutz, Triage-Disziplin und das Betreiben des Trackers selbst).

Nachbar-Abgrenzung, damit nichts doppelt formuliert wird: `spec/project/monitoring-observability/` besitzt den vendor-neutralen Telemetrie-*Vertrag*, den die Anwendung emittiert (Metriken, strukturierte Logs, Traces, Health/SLO — einschließlich des verpflichtenden Browser-Error-Capture-Bodens und der `[locked]` PII-Redaktions-Säule); diese Spec besitzt die **Error-Tracking-Tool-Schicht**, die Fehler-Events empfängt, und den Workflow darum herum. `spec/project/gdpr-audit-process/` besitzt die PII-Klassendefinition und das Audit-Urteil. `spec/project/api-error-handling/` besitzt den Fehler-*Antwort*-Vertrag, den eine API an Clients zurückgibt. `spec/project/workflow-health/` besitzt rote CI-Läufe — Build-Zeit-Fehlschläge sind kein Laufzeit-Error-Tracking.

Leser: Entwickler, die eine Anwendung an einen Error Tracker anbinden, Betreiber, die einen betreiben (selbst gehostet oder SaaS), und Reviewer, die beurteilen, ob die Error-Tracking-Haltung eines Projekts zu seiner Lebenszyklusphase passt.

## Ziele

- Jede Eigenentwicklung mit echten Nutzern hat eine definierte Error-Tracking-Haltung: welches Tool, welche Projekte/Environments, wer alarmiert wird und wer triagiert
- Der anwendungsseitige Vertrag ist **tool-neutral**: Die Instrumentierung bindet an das Sentry-SDK-Protokoll und an Konzepte der Fähigkeitsklasse (DSN, Environment, Release, Issue-Lebenszyklus), sodass das Backend austauschbar ist, ohne Anwendungscode anzufassen; GlitchTip wird nur als nicht bindendes Referenzprofil genannt
- Die **Lebenszyklusphasen** — Entwicklung, Test/Staging, Produktion — haben jeweils ein explizites Anforderungsset, weil sich ihre Zwecke unterscheiden: Feedback-Geschwindigkeit, Release-Gating beziehungsweise Incident-Erkennung
- Die Pflichten, die **mit** dem Betrieb des Tools einhergehen, sind explizit: PII-Disziplin an der SDK-Grenze, Kontrolle des Event-Volumens, Triage-Service-Level, Datenaufbewahrung und das Betreiben des Trackers selbst als Produktionsinfrastruktur
- Error Tracking schließt die Schleife zum Lieferprozess: Vom Tracker gefundene Issues speisen den normalen Issue → Fix → Release-Fluss, und Release-Tagging macht Regressionen dem Release zuordenbar, das sie eingeführt hat

## Nicht-Ziele

- Der allgemeine Telemetrie-Vertrag der Anwendung — Metriken, strukturierte Logs, Distributed Traces, Health/SLO —, der `spec/project/monitoring-observability/` gehört; ein Error Tracker ergänzt diese vier Säulen, er ersetzt sie nie
- Zu definieren, was als personenbezogenes Datum zählt, oder Lecks zu auditieren — PII-Klasse und Urteil gehören `spec/project/gdpr-audit-process/`; diese Spec verdrahtet nur die produzentenseitigen Kontrollen in die SDK-Konfiguration
- Die Form der HTTP-Fehlerantworten an API-Clients (gehört `spec/project/api-error-handling/`)
- Die Triage von CI-/Build-Fehlschlägen (gehört `spec/project/workflow-health/`); der Tracker beobachtet laufende Anwendungen, nicht Pipelines
- Volle APM-/RUM-Adoption: Das Performance-Tracing des Referenz-Tools und die Core-Web-Vitals-Schicht bleiben advisory, genau wie `spec/project/monitoring-observability/` sie einstuft
- Einen konkreten Alerting-Kanal, eine Triage-SLA-Zahl, eine Aufbewahrungsfrist oder eine Sampling-Rate zu verpflichten — diese sind projektdefiniert; diese Spec verpflichtet, dass jede davon **existiert und aufgeschrieben ist**
- Die Tracker-Auswahl für Dritt-/Standardsoftware, die das Portfolio lediglich betreibt; der Scope hier sind Eigenentwicklungen

## Anforderungen

### Tool-neutraler Kern (Pflicht)

- Der Error Tracker **MUSS** aus der Fähigkeitsklasse gewählt werden, die durch diese sechs Fähigkeiten definiert ist: (1) Event-Ingestion über **Sentry-SDK-protokoll-kompatible** Client-SDKs, konfiguriert per **DSN**; (2) automatische **Gruppierung** wiederkehrender Events zu Issues; (3) eine **Environment**-Dimension an jedem Event; (4) eine **Release**-Dimension an jedem Event; (5) **Alert-Regeln** für neue und regressierte Issues; (6) ein **Issue-Lebenszyklus** (offen → gelöst → regressiert, plus ein expliziter Ignore-Zustand). Jedes Produkt mit diesen sechs erfüllt diese Spec — der Vertrag bindet die Klasse, nicht den Hersteller
- Die Anwendungs-Instrumentierung **MUSS** das Standard-Sentry-kompatible SDK ihrer Plattform verwenden statt eines herstellerproprietären Clients, sodass ein Backend-Wechsel (GlitchTip ↔ Sentry ↔ kompatibel) eine Konfigurationsänderung ist (die DSN), nie eine Code-Änderung
- Die DSN **MUSS** über Environment-/Deployment-Konfiguration injiziert werden und **DARF NICHT** im Quellbaum hartkodiert sein; eine fehlende DSN **MUSS** sanft degradieren — das SDK bleibt ein No-op und die Anwendung startet und läuft normal, sodass lokale Checkouts und CI keinen Tracker brauchen
- Eine logische Anwendung **SOLLTE** auf ein Tracker-Projekt pro Hauptkomponente abbilden (Backend, Frontend, Worker), wobei Deployment-Stufen innerhalb dieser Projekte über den Environment-Tag getrennt werden; ein separates Dev-Projekt **KANN** verwendet werden, wo harte Isolation von experimentellem Rauschen gewünscht ist

### Integrationsvertrag (Pflicht)

- Das SDK **MUSS** beim Prozessstart initialisiert werden, bevor Request-Verarbeitung oder Job-Konsum beginnt, mit aktiven globalen Handlern der Plattform — unbehandelte Exceptions und unbehandelte Promise-Rejections werden ohne Code an jeder Aufrufstelle eingefangen. Für Browser-Frontends ist das derselbe Zwei-Listener-Boden, den `spec/project/monitoring-observability/` §Frontend-Observability bereits verpflichtet; der Tracker ist die natürliche Senke dafür
- Jedes Event **MUSS** einen `environment`-Wert aus dem deklarierten, geschlossenen Stufen-Vokabular des Projekts tragen (zum Beispiel `development`, `staging`, `production` — die genauen Namen sind projektdefiniert, **MÜSSEN** aber über alle Komponenten der Anwendung hinweg konsistent verwendet werden, weil Alert-Regeln und Release-Gates darauf filtern)
- Jeder deployte Build **MUSS** einen `release`-Identifier setzen, der zu einem eindeutigen Code-Stand auflösbar ist (der Release-Tag oder die Commit-SHA; für Repositories unter `spec/project/release-automation/` ist der Release-Tag die natürliche Wahl). Ohne Release-Tagging sind Regressionserkennung und die Zuordnung „welches Deploy hat das eingeführt" unmöglich — Release-Tagging macht aus dem Tracker erst eine Verbesserungsschleife statt einer Fehlerliste
- Fehler, die gefangen und degradiert werden, **SOLLTEN** an der Entscheidungsstelle trotzdem explizit gemeldet werden (der Capture-Aufruf des SDKs mit angereichertem Kontext), denn ein verschluckter Fehler ist für jede Phase dieser Spec unsichtbar; das ist das Laufzeit-Gegenstück zum Swallowed-Error-No-Go in `spec/project/source-code-review/`
- Der Tracker **DARF NICHT** als allgemeine Log-Senke verwendet werden: Nur Events mit Fehler-Severity oder bewusst erfasste Messages gehören dorthin. Alle INFO-/DEBUG-Logs in den Tracker zu leiten zerstört die Gruppierungsqualität und Event-Budgets; die Strukturierte-Logs-Säule von `spec/project/monitoring-observability/` besitzt Logs
- PII-Kontrollen **MÜSSEN** an der SDK-Grenze aktiv sein: Das Default-PII-Verhalten des SDKs bleibt aus (keine rohen Cookies, Auth-Header oder Request-Bodies mit personenbezogenen Daten), und ein Scrubbing-Hook (der Before-Send-Filter des SDKs oder Äquivalent) entfernt oder maskiert identifizierte Felder, bevor das Event den Prozess verlässt. Das ist die Fehler-Event-Instanz der `[locked]` Emissionsgrenzen-Redaktions-Säule in `spec/project/monitoring-observability/`; was als personenbezogenes Datum zählt, definiert `spec/project/gdpr-audit-process/` und wird hier nicht wiederholt
- Clientseitige Volumenkontrollen **MÜSSEN** bewusst konfiguriert werden: eine explizite Sample-Rate-/Rate-Limit-Entscheidung pro Projekt (100 % ist eine akzeptable Entscheidung für Services mit wenig Traffic — die Anforderung ist, dass es eine Entscheidung ist, festgehalten in der Projektkonfiguration, kein Zufall), sodass ein Fehlersturm weder Quota erschöpfen noch den Tracker lahmlegen kann
- Für minifizierte oder transpilierte Frontend-Builds **SOLLTEN** Source Maps (oder die äquivalenten Symbolication-Artefakte der Plattform) pro Release hochgeladen werden, denn ein unlesbarer Stack Trace macht den Zweck des Tools zunichte

### Entwicklungsphase (Pflicht bei Adoption)

Der Zweck der Phase ist **schnelles Feedback für die Person, die gerade codiert** — Konsole und Debugger sind primär, der Tracker ist sekundär.

- Lokale Entwicklung **DARF NICHT** in das Produktions-Tracker-Projekt mit Produktions-Environment-Tag melden; die Default-Haltung ist *SDK lokal deaktiviert* (keine DSN gesetzt), was die Sanft-Degradations-Regel oben kostenlos macht
- Ein Entwickler **KANN** einen lokalen Lauf auf ein Dev-Projekt oder das `development`-Environment richten, wenn die Error-Tracking-Verdrahtung selbst getestet wird (Gruppierungsverhalten, Scrubbing-Hooks, Alert-Regeln); der Debug-Modus des SDKs **KANN** dort aktiviert werden
- Alert-Regeln **DÜRFEN NICHT** für Events mit Entwicklungs-Environment-Tag jemanden anpiepsen
- Die SDK-Verdrahtung **SOLLTE** vom ersten vertikalen Schnitt an Teil des Anwendungsgerüsts sein, nicht kurz vor Go-Live nachgerüstet — globale Handler, Environment-/Release-Tagging und Scrubbing spät nachzurüsten ist genau der Weg, wie PII-Lecks und ungetaggte Releases entstehen

### Test-/Staging-Phase (Pflicht, wenn eine Staging-Stufe existiert)

Der Zweck der Phase ist **das Abfangen von Regressionen vor einem Release**, unter produktionsidentischer Verdrahtung.

- Staging-/E2E-Deployments **MÜSSEN** mit eigenem Environment-Tag und dem Kandidaten-Release-Identifier an den Tracker melden, über denselben SDK-Konfigurationspfad wie Produktion — Staging ist die Generalprobe für die Produktionsverdrahtung, und ein Scrubbing-Hook, der vor Produktion nie ausgeführt wurde, ist ungetesteter PII-Schutz
- Ein neues Issue, das für ein Kandidaten-Release zuerst in Staging auftritt, **SOLLTE** die Promotion dieses Releases blockieren, bis es triagiert ist (behoben oder explizit mit dokumentiertem Grund akzeptiert); das ist ein Release-Readiness-Input neben den Gates, die das Projekt ohnehin fährt
- Bewusst provozierte Fehlschläge aus Negativ-/E2E-Tests **SOLLTEN** aus dem Alert-Rauschen herausgehalten werden — entweder clientseitig gefiltert (ein Tag, den Test-Suites setzen) oder per Alert-Regel-Scoping ausgeschlossen —, damit Staging-Alerts aussagekräftig bleiben
- Staging-Alerts **SOLLTEN** einen Team-Kanal benachrichtigen und **DÜRFEN NICHT** den Bereitschaftsdienst anpiepsen; Paging ist Produktionsauswirkungen vorbehalten

### Produktionsphase (Pflicht)

Der Zweck der Phase ist **das Erkennen echter Fehlschläge und das Antreiben der Fix-Schleife**; in Produktion ist der Tracker ein primäres Betriebssignal, keine optionale Annehmlichkeit.

- Jedes Produktions-Deployment einer Eigenentwicklung mit echten Nutzern **MUSS** an einen Error Tracker melden; ohne einen zu laufen ist eine dokumentierte, begründete Ausnahme, kein Default
- Alert-Regeln **MÜSSEN** mindestens konfiguriert sein für: ein **neues Issue** im Produktions-Environment und eine **Regression** (ein zuvor gelöstes Issue taucht wieder auf). Jede Alert-Route **MUSS** ein benanntes zuständiges Team haben — ein Alert, den niemand besitzt, ist per Konstruktion Rauschen
- Neue Produktions-Issues **MÜSSEN** innerhalb eines projektdefinierten Service-Levels triagiert werden (die Zahl ist pro Projekt; ihre Existenz nicht). Triage heißt, ein Mensch entscheidet: jetzt beheben, einplanen oder mit dokumentiertem Grund ignorieren. Die Issue-Lebenszyklus-Zustände **MÜSSEN** wahrheitsgemäß verwendet werden — lösen bei Fix, ignorieren nur bewusst —, denn eine Issue-Liste, die zu 90 % veraltet ist, ist ein Tracker, den niemand liest, und ein ungelesener Tracker ist strikt schlechter als keiner: Er erzeugt die falsche Sicherheit von „wir würden es merken"
- Issues, die Code-Änderungen erfordern, **SOLLTEN** in den normalen Issue-Workflow des Projekts überführt werden (ein verknüpftes GitHub-Issue, das das Tracker-Issue referenziert), sodass der Fix durch die Standard-Pipeline Branch → PR → Release fließt und das Tracker-Issue gelöst wird, wenn das behebende Release deployt
- Eine Regression — ein in Release N gelöstes Issue taucht in Release N+M wieder auf — **MUSS** mindestens mit der Priorität eines neuen Issues behandelt werden; Regressionen sind das wertvollste Signal des Tools und existieren nur wegen des verpflichtenden Release-Taggings oben
- Ein **Fehlersturm** (Event-Volumen, das die konfigurierten Rate-Limits sättigt) **MUSS** selbst als Incident-Signal behandelt werden, auch wenn jedes einzelne Event harmlos aussieht
- Das Uptime-Monitoring des Referenz-Tools **KANN** als Black-Box-Probe für Dritt-/eigene Endpunkte dienen und den Third-Party-Boden von `spec/project/monitoring-observability/` speisen; es ergänzt die dortige Health-/SLO-Säule und **DARF** sie **NICHT** ersetzen

### Betrieb des Tools (Pflicht während der Nutzung)

- **Datenschutz**: Wo Events trotz Scrubbing personenbezogene Daten enthalten können, ist der Tracker ein Verarbeitungssystem im Sinne der DSGVO. Selbst-Hosting hält Event-Daten im Haus und ist die Portfolio-Default-Haltung; der Einsatz eines gehosteten Trackers **MUSS** von einer Datenschutzprüfung vorausgegangen sein (Auftragsverarbeitungsvertrag, Speicherort) per `spec/project/gdpr-audit-process/`. Die Event-**Aufbewahrung MUSS** explizit konfiguriert sein (projektdefinierte Frist), nicht auf „für immer" belassen
- **Der Tracker ist Produktionsinfrastruktur**: Ein selbst gehosteter Tracker **MUSS** selbst nach der Deployment-Messlatte des Portfolios betrieben werden (für Kubernetes-Deployments gelten `spec/project/kubernetes-deployment-best-practices/` und die Chart-Specs), einschließlich Backups seines Datastores und einer gepflegten Update-Kadenz. Mindestens ein **Verfügbarkeitssignal für den Tracker selbst MUSS** außerhalb des Trackers leben (ein externer Uptime-Check oder das Monitoring des Clusters) — der Wächter braucht einen Wächter, denn ein still ausgefallener Tracker sieht identisch aus wie eine gesunde Anwendung
- **SDK-Aktualität**: Tracker-SDKs **MÜSSEN** Teil des normalen Dependency-Update-Flusses des Projekts sein (Renovate per Portfolio-Baseline, `spec/project/dependency-audit/` für die Audit-Seite); ein veraltetes SDK ist sowohl eine Sicherheitsfläche als auch ein Kompatibilitätsrisiko gegenüber dem Server
- **Zugriffskontrolle**: Tracker-Organisationen/-Teams **SOLLTEN** dem Least-Privilege-Prinzip folgen — Event-Payloads können auch nach dem Scrubbing sensiblen Kontext enthalten, Lesezugriff ist also nicht per Default organisationsweit
- **Kosten-/Quota-Hygiene**: Auf einem gehosteten Plan ist die Event-Quota ein Budget (der Free-Tier des Referenz-Tools liegt bei 1.000 Events/Monat — ein einziger lauter Produktions-Bug erschöpft das in Minuten); der Quota-Verbrauch **SOLLTE** periodisch geprüft und das Sampling bewusst justiert werden, statt die harte Plan-Grenze Events still verwerfen zu lassen

### Referenzprofil (nicht bindend)

- Konkretes Tooling **KANN** nur hier genannt werden, und dieser Abschnitt ist explizit nicht normativ. Die Portfolio-Referenz ist **GlitchTip**: Open Source (MIT-lizenziertes Backend, Quellcode auf GitLab), Sentry-SDK-kompatibel, Funktionsumfang Error Tracking, Uptime-Monitoring, grundlegendes Performance-Tracing und Log-Erfassung; einsetzbar selbst gehostet (der Portfolio-Default, Docker/Kubernetes) oder als SaaS (Free-Tier 1.000 Events/Monat, bezahlte Stufen nach Volumen, Stand 2026-07-25). Ein Projekt **KANN** jeden fähigkeitsklassen-konformen Tracker einsetzen (Sentry selbst gehostet/SaaS, Bugsink, vergleichbar) und trotzdem jede Pflicht-Anforderung erfüllen
- Auswahlkriterien beim Ersetzen: Sentry-Protokoll-Kompatibilität (schützt den anwendungsseitigen Vertrag), Selbst-Hostbarkeit und Datenlokalität (schützt die Datenschutz-Haltung) und Betriebsgewicht (ein Tracker, der schwerer zu betreiben ist als die Anwendungen, die er beobachtet, ist für ein kleines Portfolio der falsche Tausch)

## Akzeptanzkriterien

- [ ] `spec/project/error-tracking/` existiert mit `en.md` (kanonisch) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet
- [ ] Der tool-neutrale Kern ist als Pflicht-Abschnitt formuliert: die Sechs-Fähigkeiten-Klassendefinition, Sentry-SDK-Protokoll-Instrumentierung, DSN via Environment mit sanfter No-DSN-Degradation und die Projekt-/Environment-Abbildungsregel
- [ ] Der Integrationsvertrag ist mit RFC-2119-Schlüsselwörtern formuliert: SDK-Init beim Prozessstart mit globalen Handlern, verpflichtendes `environment`- und `release`-Tagging, kein Log-Senken-Missbrauch, PII-Scrubbing an der SDK-Grenze mit Referenz auf die gesperrte Observability-Säule und `gdpr-audit-process`, bewusste Volumenkontrollen und Source-Map-Upload für Frontend-Builds
- [ ] Alle drei Lebenszyklusphasen haben einen eigenen Anforderungs-Abschnitt, und die Pro-Phase-Zwecke (Feedback / Release-Gating / Incident-Erkennung) sind explizit
- [ ] Die Entwicklungsphase verbietet das Verschmutzen von Produktionsdaten und Paging aus Dev-Events und formuliert die Früh-im-Gerüst-Regel
- [ ] Die Test-/Staging-Phase verpflichtet produktionsidentische Verdrahtung mit eigenem Environment-Tag, formuliert das Neues-Issue-blockiert-Promotion-Gate als SOLLTE und reserviert Paging für Produktion
- [ ] Die Produktionsphase verpflichtet Tracker-Adoption für nutzerzugewandte Eigenentwicklungen, Neues-Issue- und Regressions-Alerts mit benannten Zuständigen, ein Triage-Service-Level, wahrheitsgemäße Issue-Lebenszyklus-Nutzung, Regressions-Priorität und die Fehlersturm-als-Incident-Regel
- [ ] Die Betriebspflichten sind formuliert: DSGVO-Haltung (Selbst-Hosting-Default, Prüfung vor SaaS, explizite Aufbewahrung), Tracker-als-Produktionsinfrastruktur mit externem Verfügbarkeitssignal, SDK-Aktualität über den Dependency-Fluss, Least-Privilege-Zugriff und Quota-Hygiene
- [ ] Die Nachbar-Abgrenzung ist explizit und nur referenzierend: `monitoring-observability` (Telemetrie-Vertrag, Frontend-Boden, gesperrte PII-Säule), `gdpr-audit-process` (PII-Klasse/Urteil), `api-error-handling` (Antwort-Vertrag), `workflow-health` (CI-Fehlschläge)
- [ ] GlitchTip erscheint nur im Kontext und im nicht bindenden Referenzprofil; jede Pflicht-Anforderung ist mit jedem fähigkeitsklassen-konformen Tracker erfüllbar
- [ ] Ein Reviewer kann ein reales Projekt gegen diese Checkliste halten und jede Anforderung als erfüllt oder nicht erfüllt markieren

## Offene Fragen

- **Erster Adopter und Dogfooding.** Welche Portfolio-Anwendung zuerst einen Tracker anbindet und ob eine gemeinsame selbst gehostete GlitchTip-Instanz das ganze Portfolio bedient oder jeder Cluster seine eigene betreibt, ist eine ausstehende Operator-Entscheidung; das Deployment folgte `spec/project/bjw-s-common-chart-deployment/`.
- **Künftige `error-tracking-audit`-Fähigkeit.** Ein read-only Scanner, der den statisch prüfbaren Anteil verifiziert (SDK vorhanden und initialisiert, DSN aus dem Environment, Environment-/Release-Tagging verdrahtet, Scrubbing-Hook vorhanden, Sampling-Entscheidung dokumentiert), analog zu `observability-audit`, ist plausible Folgearbeit; seine Form wird beim Autorieren festgelegt.
- **Issue-Brücken-Automatisierung.** Ob Tracker-Issues automatisch GitHub-Issues öffnen sollen (als Zulieferung an `spec/project/issue-orchestration/`) oder eine manuelle Triage-Entscheidung bleiben, ist ungeklärt; manuell ist der Default, bis entschieden.
- **Portfolio-Scope-Promotion.** Diese Spec startet `local`. Ob sie wie ihre Schwester `monitoring-observability` `Portfolio-Scope: portfolio` tragen soll — sodass service-tragende Repositories sie per Referenz erben —, ist eine explizite Maintainer-Entscheidung, die hier bewusst nicht getroffen wird.
- **Portfolio-Default-Zahlen.** Triage-SLA, Aufbewahrungsfrist und Default-Sample-Raten bleiben projektdefiniert; ob das Portfolio empfohlene Defaults will, ist offen.

## Referenzen

- [R1] *GlitchTip*, Produktseite — Funktionsumfang (Error Tracking, Uptime, Performance, Logs), Sentry-SDK-Kompatibilität, Hosting und Preise (verifiziert 2026-07-25): <https://glitchtip.com/>
- [R2] *GlitchTip-Dokumentation* — Installation, SDK-Integration, Feature-Doku: <https://glitchtip.com/documentation>
- [R3] *GlitchTip-Backend-Repository*, MIT-Lizenz (verifiziert 2026-07-25): <https://gitlab.com/glitchtip/glitchtip-backend>
- [R4] *Sentry-SDK-Dokumentation* — die Plattform-SDK-Konfigurationsfläche (DSN, Environment, Release, Before-Send-Scrubbing, Sampling), an die der tool-neutrale Vertrag bindet: <https://docs.sentry.io/platforms/>
- [R5] `spec/project/monitoring-observability/` — der Telemetrie-Vertrag, den diese Spec ergänzt: Frontend-Error-Capture-Boden, Third-Party-Probing und die `[locked]` PII-Redaktions-Säule
- [R6] `spec/project/gdpr-audit-process/` — PII-Klassendefinition und Audit-Urteil, referenziert von den Scrubbing- und Datenschutz-Anforderungen
