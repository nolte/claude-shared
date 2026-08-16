# Test-Stufe: Integration

Status: draft

## Kontext

Die Integration-Stufe liegt **über der Component-Stufe** in der von `spec/project/test-pyramid-foundation/` definierten Pyramide. Sie ist die erste Stufe, die Code gegen einen **echten externen Kollaborateur** übt — eine echte Datenbank, einen Message-Broker, ein Dateisystem oder einen einzelnen anderen Service — statt gegen ein Double. Wo ein Component-Test *jeden* Externen an der Grenze durch ein Double ersetzt, lässt ein Integrationstest den Code mit genau **einem** echten Kollaborateur über eine echte Verbindung sprechen und verifiziert den **Integrations-Seam**: die Stelle, an der der Code nach außen serialisiert, abfragt, mappt oder ein Wire-Protokoll spricht.

Das Wort „Integrationstest" ist gefährlich mehrdeutig, und diese Spec löst das auf. Ein **schmaler** Integrationstest übt nur den Code, der mit einem separaten Kollaborateur spricht, ist nicht größer als ein Unit-Test, läuft unter dem Unit-Framework und doubelt alles andere. Ein **breiter** Integrationstest fährt viele Live-Services zusammen hoch und ist in Wahrheit ein verkappter Systemtest; das Technology Radar von Thoughtworks setzt breite Integrationstests und geteilte unternehmensweite Testumgebungen auf **Hold** — als teure, fragile, langsame Flaschenhälse, die falsches Vertrauen und nicht lokalisierbare Fehler geben. Diese Spec **mandatiert die schmale Form** und behandelt breite Integration als unerwünscht.

Diese Spezifikation ist die stufenspezifische Realisierung der **invarianten Form** des Fundaments für die Integration-Stufe. Sie füllt jedes von dieser Form geforderte Feld und ergänzt die stufenspezifische Substanz: die schmal/breit-Unterscheidung, den seam-only-Assertion-Umfang, echte-aber-ephemere Kollaborateure (statt untreuer In-Memory-Fakes), Determinismus trotz echter Systeme und die Grenze zur Contract-Stufe.

Sie ist bewusst **werkzeug-agnostisch**: Die bindenden Anforderungen nennen nie ein Werkzeug. Konkrete Werkzeuge erscheinen nur als illustratives Referenzprofil.

**Verhältnis zu den anderen Specs.** Diese Stufe ist nach Verantwortung abgegrenzt, nicht durch Überschneidung:

- `spec/project/test-pyramid-foundation/` [R1] besitzt das Stufenmodell und die Meszaros-Test-Double-Taxonomie. Diese Spec detailliert die Integration-Stufe; sie wiederholt das Modell nicht.
- `spec/project/test-tier-component/` [R2] ist die Stufe **darunter**: *Jeder* externe Kollaborateur ist gedoubelt. Die Grenze lautet „alle Externe gedoubelt" (Component) vs. „genau ein echter externer Kollaborateur, der Rest gedoubelt" (Integration).
- `spec/project/test-tier-contract/` [R3] ist das **Geschwister daneben/darüber**: Es verifiziert ein Cross-Service-Agreement, *ohne beide Seiten hochzufahren*. Die Grenze lautet „ein echter Kollaborateur, den du besitzt und im Gleichschritt auslieferst" (Integration) vs. „ein Kollaborateur, der unabhängig von dir ausgeliefert wird, oder einer, den du gar nicht besitzt" (Contract). Die Auslieferungsgrenze entscheidet, nicht der Besitz.
- `spec/project/e2e-test-automation/` [R4] ist die System-Stufe: viele echte Kollaborateure, das ganze laufende System. Die Grenze lautet „ein Seam" (Integration) vs. „das ganze System end-to-end" (E2E).
- `spec/project/quality-gate/` [R5] **führt** die schnellen Integrationstests aus und besitzt Ausführungsmechanik und Ausgabeform.

Leser: Spec-Autor:innen, die die Geschwister-Stufen-Specs schreiben; Skill- und Agent-Autor:innen, die die Integration-Stufen-Triade (Entwicklung/Ausführung/Analyse) bauen; Entwickler:innen, die Integrationstests gegen Datenbanken, Broker und Services schreiben; Reviewer, die prüfen, ob ein Integrationstest schmal, seam-fokussiert, ephemer und deterministisch ist.

## Ziele

- Den **schmalen** Integrationstest mandatieren und breite Integration (viele Live-Services) als unerwünscht markieren
- Assertions auf den **Integrations-Seam** begrenzen (Serialisierung, echte Queries gegen ein echtes Schema, Mapping, Verbindung, Wire-Protokoll, Transaktionen, Migrationen), nie Geschäftslogik oder Ganz-System-Journeys
- **Echte, aber ephemere** Kollaborateure (wegwerfbare Container) gegenüber untreuen In-Memory-Substituten verlangen, die von der Produktionstechnologie abweichen
- Die Stufe deterministisch halten trotz echter Systeme, via ephemere Umgebungen und Per-Test-Datenisolation
- Eine scharfe Grenze zur **Contract**-Stufe ziehen (ein echter eigener Kollaborateur vs. ein Cross-Service-Agreement) und zu E2E (ein Seam vs. das ganze System)
- Die Stufe werkzeug-agnostisch halten, mit einem austauschbaren Referenzprofil statt eines vorgeschriebenen Werkzeugs

## Nicht-Ziele

- Die Stufe auszuführen oder ihre Ausführungsmechanik und Ausgabetabelle zu definieren: Eigentum von `spec/project/quality-gate/` [R5]
- **Viele** Live-Services zusammen hochzufahren (breite Integration / Systemtesten): hier unerwünscht und, in voller Breite, Eigentum der E2E-Stufe [R4]
- Geschäftslogik neu zu testen, die auf der **Unit**-Stufe bestimmbar ist: Das ist Duplikation, keine Integration
- Ein **Cross-Service-Agreement** ohne Live-Partner zu verifizieren: Das ist die Contract-Stufe [R3]
- Den getesteten Kollaborateur zu doubeln: Ein Integrationstest übt einen **echten** Kollaborateur (ein gedoubelter machte ihn zu einem Component-Test)
- Ein bestimmtes Container-, Datenbank- oder Broker-Werkzeug vorzuschreiben: Das Referenzprofil ist illustrativ

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** den Default-Integrationstest als **schmal** definieren: Er übt nur den Code, der mit **einem** separaten echten Kollaborateur spricht, ist nicht größer als ein Unit-Test, läuft unter dem Unit-Framework und doubelt jeden anderen Externen [R6], [R7].
- **MUSS [MUST]** **breite** Integrationstests (viele Live-Services zusammen hochgefahren) als **unerwünscht** behandeln: Sie sind teuer, langsam, fragil und geben nicht lokalisierbare Fehler, und das Technology Radar von Thoughtworks hält sie und geteilte unternehmensweite Testumgebungen auf Hold [R8], [R9]. Breite auf der Ebene des ganzen Systems gehört zur E2E-Stufe, nicht hierher.
- **MUSS [MUST]** die Grenze zur **Component-Stufe** scharf halten: Ein Component-Test doubelt *jeden* Externen; ein Integrationstest übt genau **einen** echten externen Kollaborateur, während er den Rest doubelt [R2].
- **MUSS [MUST]** einen Kollaborateur üben, den das Projekt **besitzt und im Gleichschritt ausliefert** (seine eigene Datenbank, seinen Broker oder einen einzelnen eigenen Service, der zusammen mit dem geprüften Code deployt und versioniert wird); Cross-Service-Agreements mit einem Partner, den das Projekt nicht kontrolliert, gehören zur Contract-Stufe [R3], [R10].
- **MUSS [MUST]** die folgende **Entscheidungsregel** anwenden, wenn der Kollaborateur ein Service ist, den das Projekt besitzt, aber **separat deployt**: Der Seam ist ein **Integrations**-Test, wenn dasselbe Team beide Seiten gemeinsam deployt *und* versioniert, sodass die beiden nur in einer vom Team gewählten Kombination in Produktion sein können; er ist ein **Contract**-Test, sobald eine der Seiten unabhängig von der anderen ausgeliefert werden kann, auch unter einem Besitzer. Nicht der Besitz ist der Unterscheider—die **Auslieferungsgrenze** ist es. Wo die Seiten unabhängig ausliefern, ist der Produktions-Fehlermodus Versions-Schiefstand zwischen einem Producer und einem Consumer, die nie zusammen ausgeliefert wurden, und ein Live-Integrationstest kann ihn nicht beobachten: Er übt ein deploytes Paar, während Produktion jedes andere halten kann. Der Broker plus das `can-i-deploy`-Gate der Contract-Stufe sind genau dafür gebaut [R3]. Wo die Seiten zusammen ausliefern, kann der Schiefstand nicht entstehen, und ein echter Kollaborateur gibt höhere Fidelität bei geringerer Zeremonie.

### Was ein Integrationstest verifiziert, und was nicht

- **MUSS [MUST]** Assertions auf den **Integrations-Seam** begrenzen: die Punkte, an denen der Code Daten serialisiert oder deserialisiert und eine Grenze überquert — echtes SQL/Queries gegen ein echtes Schema, objektrelationales Mapping, Verbindungs- und Transaktionshandhabung, Wire-Protokolle, Nachrichtenformate und Schema-Migrations-Korrektheit [R6], [R7].
- **DARF NICHT [MUST NOT]** **Geschäftslogik** neu testen, die auf der Unit-Stufe bestimmbar ist; Unit-Stufen-Verhalten auf der langsamen Integration-Stufe zu duplizieren ist Verschwendung, keine Abdeckung [R7].
- **DARF NICHT [MUST NOT]** **Ganz-System-Nutzer-Journeys** treiben; das ist die E2E-Stufe. Ein Integrationstest deckt einen Seam ab, keinen End-to-End-Pfad [R4], [R6].

### Echte, aber ephemere Kollaborateure

- **MUSS [MUST]** den Integrationstest gegen die **echte Technologie** ausführen, bereitgestellt als **wegwerfbare, ephemere** Instanz (zum Beispiel eine echte Datenbank oder ein Broker in einem Wegwerf-Container) pro Test oder pro Suite, sodass der Test Produktionstreue ohne eine geteilte, langlebige Umgebung hat [R11].
- **DARF NICHT [MUST NOT]** einen **In-Memory-Fake** substituieren, der sich anders verhält als die Produktionstechnologie (zum Beispiel eine eingebettete H2-Datenbank als Ersatz für PostgreSQL): Dialekt- und Verhaltensdrift erzeugt falsches Vertrauen — eine Query, die gegen den Fake besteht, kann gegen die echte Engine fehlschlagen [R11].
- **DARF NICHT [MUST NOT]** von einer **geteilten, veränderlichen, langlebigen** Testumgebung abhängen (einer zentralen Staging-Datenbank, die jeder Test trifft): Geteilter veränderlicher Zustand ist die dominante Flakiness- und Flaschenhals-Quelle auf dieser Stufe; jeder Test besitzt seinen ephemeren Kollaborateur [R8], [R9].

### Isolationsgrad und erlaubte Doubles

- **MUSS [MUST]** genau **einen** externen Kollaborateur (den getesteten) **echt** halten und mit dem Meszaros-Vokabular des Fundaments jeden *anderen* Externen, den der Code berührt, **gedoubelt** halten, sodass der Test Fehler auf den einzelnen Seam lokalisiert, den er abdeckt [R1], [R6].
- **MUSS [MUST]** für jeden Integrationstest nennen, welcher Kollaborateur echt und welche gedoubelt sind, damit ein Reviewer bestätigen kann, dass der Test schmal ist.
- **MUSS [MUST]** die Treue-Regel des Fundaments [R1] samt ihrer Ausnahme auf jene *anderen*, legitim gedoubelten Externen anwenden, statt sie zu wiederholen. Das ist etwas anderes als das In-Memory-Fake-Verbot oben, das den Seam des **einen echten Kollaborateurs** regelt und dort das Ersetzen der Produktionstechnologie überhaupt untersagt; hier sind die Kollaborateure korrekt gedoubelt, und die Anforderung lautet, dass jeder weiterhin **ablehnt**, was der echte ablehnt. Ein schmaler Test bezieht seine präzise Fehlerlokalisierung aus dem echten Seam, den er abdeckt, und hat nichts davon, wenn ein gedoubelter Nachbar einen Aufruf akzeptiert, den die Produktion ablehnen würde. Wo die Abweichung nicht geschlossen werden kann, **MUSS [MUST]** sie im Double selbst benannt werden [R1]; der resultierende Fehlermodus ist als `T9` gemäß [R13] zitierbar.

### Determinismus und Testdaten-Isolation

- **MUSS [MUST]** die Stufe trotz Nutzung echter Systeme **deterministisch** halten: frisches Schema und geseedete Daten pro Lauf, **Per-Test-Datenisolation** (Transaktions-Rollback, Truncation oder eine frische ephemere Instanz zwischen Tests), keine Reihenfolgeabhängigkeit und kontrollierte Zeit — sodass eine echte Datenbank oder ein Broker den Test nie flaky macht.
- **MUSS [MUST]** die stufenspezifischen Flakiness-Quellen entfernen — geteilter Zustand, Test-Reihenfolge, Netzwerklage und Container-Startup-Races — durch Warten auf Readiness-Bedingungen (nicht feste Sleeps) und Isolieren der Daten jedes Tests; größere Tests sind empirisch flake-anfälliger, ein weiterer Grund, sie schmal und wenige zu halten [R12].

### Geschwindigkeit und Platzierung

- **MUSS [MUST]** akzeptieren, dass Integrationstests **langsamer** sind als Unit- und Component-Tests (Sekunden bis Minuten, inklusive Container-Start) und daher **weniger zahlreich**, gemäß der Ökonomie der Pyramide.
- **MUSS [MUST]** einen Pull Request an den **schnellen schmalen** Integrationstests gaten (ausgeführt gemäß `spec/project/quality-gate/`, als erforderliche Checks gemäß `spec/project/pull-request-workflow/` deklariert), weil die Apex-Spec `spec/project/test-pyramid-foundation/` §CI gating model — die Autorität darüber, welche Stufen ins Gate gehören — schmale Integration zu den schnellen Stufen zählt, die das Gate durchlaufen MÜSSEN; langsamere oder schwerere Integrationstests laufen in einer dedizierten CI-Stufe oder Nightly, statt jede Änderung zu blockieren.

### Grenze zur Contract-Stufe

- **MUSS [MUST]** ein **Service-zu-Service**-Agreement an die **Contract-Stufe** routen statt an einen breiten Integrationstest: Ein Consumer-Driven-Contract-Test verifiziert, dass die Doubles, die ein Consumer nutzt, dieselbe Form zurückgeben wie der echte Provider erzeugt, **ohne beide Seiten live hochzufahren** [R3], [R10].
- **DARF NICHT [MUST NOT]** eine **echte Dritt-Produktions-API** in einem Integrationstest treffen: eine Sandbox, einen Service-Virtualization-Stub verwenden oder die Verifikation an die Contract-Stufe schieben — nie das Produktionssystem des Live-Partners.

### Anti-Patterns

- **MUSS [MUST]** als kanonische Anti-Patterns ablehnen: breite Integration als Default; eine geteilte veränderliche Staging-/Test-Datenbank, die alle Tests treffen; das Neu-Testen von Unit-Stufen-Geschäftslogik; In-Memory-Substitute, die nicht zur Produktionstechnologie passen (falsches Vertrauen); flaky Tests durch geteilten Zustand, Reihenfolge oder Container-Races; und das Treffen echter Dritt-Produktions-APIs.

### Traceability

- **MUSS [MUST]** einen Integrationstest, der einen abgeleiteten Testfall verifiziert, die **TC-ID** (und über sie die Anforderung) benennen lassen, die er abdeckt, gemäß der Traceability-Kette des Fundaments, damit Anforderungsabdeckung auditierbar ist.

### Optionales Referenzprofil

- **DARF [MAY]** ein vollständig ausgearbeitetes, stack-spezifisches Referenzprofil pinnen, klar zu „Referenz" degradiert. Ein illustratives Profil: ein Testcontainers-artiges Harness, das die **echte** Datenbank oder den Broker in einem wegwerfbaren Container startet, die echten Migrationen des Projekts anwendet, Per-Test-Daten seedet und nach der Suite abbaut; für eine unvermeidbare Dritt-Abhängigkeit einen Sandbox-Endpunkt oder einen Service-Virtualization-Stub statt des Live-Produktionsservice. Testcontainers existiert für die großen Ökosysteme (Java/Python/Go/Node/.NET); Werkzeugnamen sind illustrativ, nie verlangt.

## Akzeptanzkriterien

- [ ] Die Spec mandatiert schmale Integrationstests und markiert breite Integration (viele Live-Services) als unerwünscht, zitiert auf Fowler und den Thoughtworks-Radar-Hold
- [ ] Assertions sind auf den Integrations-Seam begrenzt (Serialisierung, echte Queries/Schema, Mapping, Verbindung, Transaktionen, Migrationen) und verboten, Unit-Stufen-Geschäftslogik neu zu testen oder Ganz-System-Journeys zu treiben
- [ ] Echte-aber-ephemere Kollaborateure sind gefordert, In-Memory-Fakes, die von der Produktionstechnologie abweichen, sind verboten (mit dem H2-vs-echte-Datenbank-Beispiel), und geteilte langlebige Testumgebungen sind verboten
- [ ] Der Isolationsgrad ist genau ein echter externer Kollaborateur mit allen anderen gedoubelt, explizit kontrastiert mit der Component-Stufe (alle gedoubelt)
- [ ] Die Treue-Regel des Fundaments wird per Verweis auf die gedoubelten Nachbarn angewandt statt wiederholt, und sie ist gegen das In-Memory-Fake-Verbot abgegrenzt, das den einen echten Seam regelt
- [ ] Determinismus via ephemere Umgebungen + Per-Test-Datenisolation ist gefordert, die stufenspezifischen Flakiness-Quellen sind benannt, und Readiness-Bedingungs-Waits (keine Sleeps) sind gefordert
- [ ] Die Stufe ist als langsamer/weniger platziert, mit schnellen schmalen Tests, die den PR gaten, und schwereren in einer dedizierten Stufe / Nightly
- [ ] Die Grenze zur Contract-Stufe (ein echter eigener Kollaborateur vs. ein Cross-Service-Agreement ohne beide Seiten live) ist scharf, wird über eine explizite Entscheidungsregel für einen eigenen, aber separat deployten Service an der Auslieferungsgrenze statt am Besitz gezogen, und das Treffen einer echten Dritt-Produktions-API ist verboten
- [ ] Die Grenze zu E2E (ein Seam vs. das ganze System) ist explizit
- [ ] Traceability auf TC-ID ist gefordert
- [ ] Ein optionales, klar degradiertes Referenzprofil (echte Abhängigkeit in einem Wegwerf-Container + Migrationen + Per-Test-Seed) ist bereitgestellt, ohne ein Werkzeug vorzuschreiben
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-pyramid-foundation/` — das Stufenmodell und die Meszaros-Test-Double-Taxonomie, die diese Spec realisiert
- [R2] `spec/project/test-tier-component/` — die Stufe darunter (alle Externe gedoubelt); die Component↔Integration-Grenze
- [R3] `spec/project/test-tier-contract/` — die Geschwister-Stufe (ein Cross-Service-Agreement ohne beide Seiten live); die Integration↔Contract-Grenze
- [R4] `spec/project/e2e-test-automation/` — die System-Stufe (das ganze laufende System); die Integration↔E2E-Grenze
- [R5] `spec/project/quality-gate/` — führt die schnellen Integrationstests aus und besitzt Ausführungsmechanik / Ausgabeform
- [R6] Martin Fowler, *IntegrationTest* (schmal vs. breit; die Mehrdeutigkeit; der Seam) — <https://martinfowler.com/bliki/IntegrationTest.html>
- [R7] Ham Vocke, *The Practical Test Pyramid* (Integration schmal behandeln, einen Integrationspunkt nach dem anderen) — <https://martinfowler.com/articles/practical-test-pyramid.html>
- [R8] Thoughtworks Technology Radar, *Broad integration tests* (Hold) — <https://www.thoughtworks.com/radar/techniques/broad-integration-tests>
- [R9] Thoughtworks Technology Radar, *Enterprise-wide integration test environments* (Hold) — <https://www.thoughtworks.com/radar/techniques/enterprise-wide-integration-test-environments>
- [R10] Martin Fowler, *ContractTest* (Doubles liefern dieselben Ergebnisse wie der echte Service) — <https://martinfowler.com/bliki/ContractTest.html>
- [R11] Testcontainers, *Replace H2 with a real database for testing* (echte wegwerfbare Container; Dialekt-Drift bei In-Memory-Fakes) — <https://testcontainers.com/guides/replace-h2-with-real-database-for-testing/>
- [R12] Google Testing Blog, *Where do our flaky tests come from?* (größere Tests sind flake-anfälliger) — <https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html>
- [R13] `spec/project/test-falsifiability/` — die tier-übergreifende Taxonomie von Tests, die nicht fehlschlagen können; `T9` ist der Fehlermodus, den ein gedoubelter Nachbar erzeugt, der permissiver ist als das, was er ersetzt, und die Spec trägt die Review-Frage, die ihn detektiert

## Offene Fragen

- Sollte das Portfolio Testcontainers-artige ephemere echte Abhängigkeiten als Default für den Datastore-Seam verlangen, oder einen dokumentierten In-Memory-Fake erlauben, wo das Team den Treue-Trade-off akzeptiert?
- Welche schmalen Integrationstests sind schnell genug, um einen PR zu gaten, versus gehören in eine Nightly-Stufe — sollte die Spec ein Größenordnungs-Budget setzen oder die Aufteilung projektspezifisch lassen?
- Braucht die Entwickeln/Ausführen/Analysieren-Triade der Integration-Stufe einen dedizierten Integration-Test-Autor-Agent, oder teilt sie eine Autor-Capability mit der Component-Stufe (beide verdrahten ein Harness und Doubles)?
- ~~Wenn ein Seam ein Service ist, den das Projekt besitzt, aber separat deployt, ist seine Verifikation ein Integrationstest (echter eigener Kollaborateur) oder ein Contract-Test (Cross-Service-Agreement) — und sollte die Spec eine Entscheidungsregel über „besitzen und kontrollieren" hinaus geben?~~ **Entschieden (2026-07-24): die Auslieferungsgrenze entscheidet, und ja, die Spec nennt die Regel.** Integration, wenn das Team beide Seiten im Gleichschritt deployt *und* versioniert; Contract, sobald eine Seite unabhängig ausgeliefert werden kann, auch unter einem Besitzer. „Besitzen und kontrollieren" war der falsche Unterscheider, weil er eine Frage zum Organigramm beantwortet, während der Fehler, den die Stufe fangen muss, Versions-Schiefstand über eine unsynchronisierte Auslieferungsgrenze ist—den unabhängige Deploybarkeit erzeugt und gemeinsamer Besitz nicht beseitigt. Die Regel steht in §„Zweck und Umfangsgrenze" oben, und `spec/project/test-tier-contract/` [R3] ist angeglichen, sodass sein „vollständig besitzt"-Ausschluss nun „besitzt und im Gleichschritt ausliefert" lautet und die Lücke schließt, in der beide Specs denselben häufigen Fall beanspruchten.
