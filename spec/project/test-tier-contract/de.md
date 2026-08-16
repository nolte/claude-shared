# Test-Stufe: Contract

Status: draft

## Kontext

Die Contract-Stufe verifiziert ein **Service-zu-Service-Agreement an einer Grenze, ohne beide Seiten live hochzufahren**. Sie ist die Spitze der funktionalen Stufen der von `spec/project/test-pyramid-foundation/` definierten Pyramide und existiert, um ein spezifisches Problem zu lösen, das die anderen Stufen nicht können: Wenn ein Service einen anderen konsumiert, nutzen die Tests des Consumers ein **Double** des Providers, und dieses Double **driftet** still von dem ab, was der echte Provider tatsächlich zurückgibt. Ein Contract-Test schließt diese Lücke — er prüft, dass die Doubles, auf die ein Consumer sich verlässt, **dieselben Ergebnisse zurückgeben wie der echte Provider** [R5], [R6], sodass eine brechende Änderung auf beiden Seiten an der Grenze gefangen wird statt in der Produktion.

In einem **consumer-driven** Contract (dem Referenzmodell) zeichnet der **Consumer** seine Erwartungen an den Provider als Contract auf; der **Provider** wird dann unabhängig gegen diesen Contract verifiziert. Keiner der Services braucht den anderen gleichzeitig laufend: Der Consumer läuft gegen einen Mock, der den Contract emittiert, und der Provider spielt die aufgezeichneten Interaktionen des Contracts gegen seine echte Implementierung ab. Deshalb **ersetzt** ein Contract-Test in einer Microservice-Architektur **einen breiten Integrationstest über eine Service-Grenze** (gemäß dem Fundament): Das Agreement wird ohne eine geteilte, fragile Integrationsumgebung verifiziert.

Diese Spezifikation ist die stufenspezifische Realisierung der **invarianten Form** des Fundaments für die Contract-Stufe. Sie füllt jedes von dieser Form geforderte Feld und ergänzt die stufenspezifische Substanz: das consumer-driven-Modell und seine provider-driven- und bi-directional-Varianten, den Kompatibilität-des-Agreements-Assertion-Umfang, den Broker und das `can-i-deploy`-Deployment-Gate und die Grenze zur Integration-Stufe.

Sie ist bewusst **werkzeug-agnostisch**: Die bindenden Anforderungen nennen nie ein Werkzeug. Konkrete Werkzeuge erscheinen nur als illustratives Referenzprofil.

**Verhältnis zu den anderen Specs.** Diese Stufe ist nach Verantwortung abgegrenzt, nicht durch Überschneidung:

- `spec/project/test-pyramid-foundation/` [R1] besitzt das Stufenmodell und die Aussage, dass Contract-Tests breite Integration über Service-Grenzen ersetzen. Diese Spec detailliert die Contract-Stufe; sie wiederholt das Modell nicht.
- `spec/project/test-tier-integration/` [R2] ist die Geschwister-Stufe für einen Kollaborateur, den das Projekt **besitzt und live übt** (seine eigene Datenbank, seinen Broker oder Service) über eine echte Verbindung. Die Grenze lautet „ein echter eigener Kollaborateur, live geübt" (Integration) vs. „ein Cross-Service-Agreement, ohne beide Seiten live verifiziert" (Contract).
- Die **Unit-** und **Component-**Stufen (`spec/project/test-tier-unit/`, `spec/project/test-tier-component/`) verifizieren die **eigene interne Korrektheit** jedes Service; die Contract-Stufe verifiziert das **Cross-Boundary-Agreement** zwischen zwei Services und behauptet nichts über das interne Verhalten eines der Services [R7].
- `spec/project/e2e-test-automation/` [R8] verifiziert das ganze laufende System; die Contract-Stufe verifiziert die **Kompatibilität einer einzelnen Grenze**, keine End-to-End-Journey.
- `spec/project/quality-gate/` [R9] **führt** die consumer-seitigen Contract-Tests im schnellen Gate aus und besitzt Ausführungsmechanik und Ausgabeform.

Leser: Spec-Autor:innen, die die Geschwister-Stufen-Specs schreiben; Skill- und Agent-Autor:innen, die die Contract-Stufen-Triade (Entwicklung/Ausführung/Analyse) bauen; Entwickler:innen, die Consumer- und Provider-Contract-Tests über Service-Grenzen schreiben; Reviewer, die prüfen, ob ein Contract-Test Kompatibilität (nicht Geschäftslogik) prüft und an einen Broker mit Deployment-Gate verdrahtet ist.

## Ziele

- Die Contract-Stufe als Verifikation eines Service-Grenz-Agreements **ohne beide Seiten live** definieren, die die Stub-Drift-Lücke schließt
- Das **consumer-driven**-Modell als Referenz etablieren und die provider-driven- und bi-directional-Varianten mit ihrer Eignung dokumentieren
- Assertions auf die **Kompatibilität des Agreements** begrenzen (Nachrichtenform, Feld-Präsenz und -Typen, Status-Codes, die protokoll-ebene Interaktion), nie Geschäftslogik oder End-to-End-Verhalten
- Einen **Contract-Austausch (Broker)** und ein **`can-i-deploy`-artiges Kompatibilitäts-Gate** vor dem Deployment verlangen, sodass ein Contract, der nicht gegen den aktuellen Provider verifiziert ist, nicht ausgeliefert werden kann
- Eine scharfe Grenze zur Integration-Stufe (ein echter eigener, im Gleichschritt ausgelieferter, live geübter Kollaborateur) und zu E2E (das ganze System) ziehen
- Die Stufe werkzeug-agnostisch halten, mit einem austauschbaren Referenzprofil statt eines vorgeschriebenen Frameworks

## Nicht-Ziele

- Die Stufe auszuführen oder ihre Ausführungsmechanik und Ausgabetabelle zu definieren: Eigentum von `spec/project/quality-gate/` [R9]
- Einen **echten eigenen, im Gleichschritt ausgelieferten Kollaborateur** live zu üben (eine echte Datenbank oder einen Broker über eine Verbindung, oder einen eigenen Service, der zusammen mit dem geprüften Code deployt und versioniert wird): Das ist die Integration-Stufe [R2]
- Die **Geschäftslogik oder interne Korrektheit** eines der Services zu verifizieren: Das sind die eigenen Unit- und Component-Stufen jedes Service [R7]
- Eine **Ganz-System-Journey** zu treiben: Das ist die E2E-Stufe [R8]
- **Beide** — Consumer und Provider — zusammen hochzufahren: Die Contract-Stufe existiert genau, um das zu vermeiden
- Ein bestimmtes Contract-Framework, einen Broker oder ein Schema-Format vorzuschreiben: Das Referenzprofil ist illustrativ
- Die portfolioweite Double-Treue-Regel aus `spec/project/test-pyramid-foundation/` §"Test-Double-Taxonomie" für den consumer-seitigen Mock dieser Stufe auszuprägen: Die Anforderung unten, dass die Doubles eines Consumers **dieselben Ergebnisse liefern wie der echte Provider**, ist strikt stärker als „nicht permissiver als der Kollaborateur, den es ersetzt", und die Provider-Verifikation erzwingt sie maschinell statt per Review, sodass eine Wiederholung der schwächeren Untergrenze hier nur verwischen würde, welche Garantie gilt. Das gilt allein für die **replay-verifizierten** Ausprägungen (consumer-driven und provider-driven); die bi-direktionale Ausprägung, unter der kein Provider-Code läuft, regelt ihre eigene Anforderung unten statt dieser Ausschluss. Die verbleibende Exposition dieser Stufe unter den replay-verifizierten Ausprägungen ist das Provider-State-Setup, das die Anforderungen unten direkt abdecken [R18]

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** einen Contract-Test als einen definieren, der verifiziert, dass eine Komponente einen **Contract erfüllt, den eine andere Komponente von ihr erwartet**, und sicherstellt, dass die **Doubles, die ein Consumer nutzt, dieselben Ergebnisse zurückgeben wie der echte Provider** — ohne beide Services live hochzufahren [R5], [R6].
- **MUSS [MUST]** die Grenze zur **Integration-Stufe** scharf halten: Integration übt einen echten Kollaborateur, den das Projekt besitzt und kontrolliert, **live** über eine echte Verbindung; die Contract-Stufe verifiziert ein **Cross-Service-Agreement** ohne eine der beiden Seiten live [R2], [R6].
- **MUSS [MUST]** die Grenze zu den **Unit- und Component-Stufen** scharf halten: Jene verifizieren die eigene interne Korrektheit eines Service; ein Contract-Test behauptet nur das **Cross-Boundary-Agreement** und nichts über das interne Verhalten eines der Services [R7].
- **MUSS [MUST]** die Grenze zu **E2E** scharf halten: Ein Contract-Test verifiziert die Kompatibilität einer einzelnen Grenze, nicht das ganze System end-to-end [R8].

### Consumer-driven Contracts (das Referenzmodell)

- **MUSS [MUST]** **consumer-driven Contracts** als Referenzmodell übernehmen: Der **Consumer** definiert seine Erwartungen an den Provider als den Contract (typischerweise die Teilmenge der Provider-Oberfläche, die der Consumer tatsächlich nutzt), und der **Provider** wird **unabhängig** gegen diesen Contract **verifiziert** [R6], [R10], [R11].
- **MUSS [MUST]** den Provider verifizieren, indem die **aufgezeichneten Interaktionen des Contracts gegen die echte Provider-Implementierung abgespielt werden** (Provider-Verifikation), mit einem Provider-State-/Setup-Mechanismus, der den Provider in die Vorbedingung versetzt, die jede Interaktion braucht [R12].
- **DARF NICHT [MUST NOT]** zulassen, dass ein **Provider State** Daten arrangiert, die der echte Provider selbst ablehnen würde: einen Identifier, den der Provider erzeugt statt entgegenzunehmen, einen Wert, den seine Validierung zurückweist, ein Duplikat, das sein Uniqueness-Constraint verbietet. Die Provider-Verifikation prüft die Interaktionen, die der Contract aufzeichnet, und nie das Setup, das ihnen vorausgeht — ein zu permissiver Provider State liefert also einen verifizierten Contract für eine Vorbedingung, die die Produktion nicht erreichen kann; das ist die stufeneigene Ausprägung der Treue-Regel aus `spec/project/test-pyramid-foundation/` §"Test-Double-Taxonomie", zitierbar als `T9` gemäß [R18]. Wo der State nicht über den validierten Pfad des Providers selbst aufgebaut werden kann, **MUSS [MUST]** diese Abweichung im Setup-Code des States benannt werden.
- **MUSS [MUST]** den **consumer-seitigen Mock** gegen die portfolioweite Treue-Regel aus `spec/project/test-pyramid-foundation/` §"Test-Double-Taxonomie" prüfen, wann immer das Projekt die **bi-direktionale** Ausprägung unten fährt: Jene Ausprägung verifiziert den Mock des Consumers gegen eine veröffentlichte Spezifikation, ohne Provider-Code auszuführen [R15], der Mock erhält also nichts von der maschinellen Garantie, die replay-basierte Verifikation liefert, und das Review ist die einzige verbleibende Prüfung. Unter den replay-verifizierten Ausprägungen ist diese Prüfung entbehrlich, und der Non-Goals-Eintrag oben sagt warum.
- **MUSS [MUST]** den consumer-seitigen Lauf als Ausführung gegen einen **Mock, der den Contract emittiert** behandeln, sodass der Consumer-Test schnell, deterministisch und ohne Live-Provider ist [R12], [R14].

### Die drei Ausprägungen

- **MUSS [MUST]** die drei Ausprägungen anerkennen und ein Projekt die zu seinen Randbedingungen passende wählen lassen:
  - **Consumer-driven** (Referenz): Consumer-Erwartungen treiben den Contract; der Provider wird dagegen verifiziert. Am besten, wenn Consumer und Provider unabhängig evolvieren und beide Seiten das Framework ausführen können [R6], [R11].
  - **Provider-driven**: Der Provider veröffentlicht den Contract, und Consumer erhalten daraus generierte Stubs; der Producer besitzt die Contract-Definition. Nützlich, wenn ein Provider viele Consumer bedient und die API-Form besitzt [R13].
  - **Bi-directional**: Der Provider veröffentlicht eine statische API-Spezifikation (zum Beispiel OpenAPI), und der Mock/Contract des Consumers wird gegen diese Spezifikation verifiziert, mit **keiner Ausführung von Provider-Code** — ein stärker entkoppelter Ansatz, wenn das Ausführen der Provider-Verifikation unpraktisch ist [R15].
- **SOLLTE [SHOULD]** auf die **consumer-driven**-Ausprägung defaulten und eine Begründung festhalten, wenn provider-driven oder bi-directional gewählt wird, weil consumer-driven die consumer-relevanten brechenden Änderungen am direktesten fängt.

### Was ein Contract-Test verifiziert, und was nicht

- **MUSS [MUST]** Assertions auf die **Kompatibilität des Agreements** begrenzen: die Request-/Response-Struktur, Feld-Präsenz und -Typen, Status-Codes und die protokoll-ebene Interaktion an der Grenze [R5], [R7].
- **DARF NICHT [MUST NOT]** **Geschäftslogik oder funktionale Korrektheit** eines der Services behaupten; das dupliziert die eigenen Unit-/Component-Stufen der Services und überkoppelt den Contract [R7].
- **DARF NICHT [MUST NOT]** den Contract **über-spezifizieren**, indem auf Felder oder Verhalten geprüft wird, die der Consumer tatsächlich nicht nutzt: Über-Spezifikation erzeugt falsche Brüche, wenn der Provider etwas ändert, das für diesen Consumer irrelevant ist [R6], [R11].

### Isolation und Determinismus

- **MUSS [MUST]** die Stufe **schnell und deterministisch** halten, indem **keine der echten Services live** hochgefahren wird: Der Consumer läuft gegen einen Contract-Mock und der Provider spielt aufgezeichnete Interaktionen ab, sodass es keine Netzwerk-Flakiness gibt, gemäß der Determinismus-Regel des Fundaments [R12].

### Der Broker und das Deployment-Gate

- **MUSS [MUST]** Contracts über einen **Broker** austauschen (ein Contract-Repository, das Contracts und Verifikationsergebnisse versioniert und festhält, welche Consumer- und Provider-Versionen kompatibel sind) statt durch ad-hoc-Datei-Austausch [R16].
- **MUSS [MUST]** das Deployment mit einer **`can-i-deploy`-artigen Kompatibilitätsprüfung** gaten: Bevor eine Consumer- oder Provider-Version deployt wird, wird der Broker abgefragt, um zu bestätigen, dass diese Version verifiziert-kompatibel mit den Versionen ist, denen sie in der Zielumgebung begegnet [R17].
- **DARF NICHT [MUST NOT]** **Contract-Drift** erlauben: Ein Contract, der nicht gegen den aktuellen Provider verifiziert ist (kein Broker, kein `can-i-deploy`), gibt falsches Vertrauen und ist ein Spec-Verstoß [R16], [R17].

### Ausführungs-Platzierung

- **MUSS [MUST]** den **consumer-seitigen** Contract-Test in der **Pipeline des Consumers** als schnellen PR-gatenden Check ausführen (ausgeführt gemäß `spec/project/quality-gate/`, als erforderlich deklariert gemäß `spec/project/pull-request-workflow/`).
- **MUSS [MUST]** die **Provider-Verifikation** in der **Pipeline des Providers** gegen veröffentlichte Consumer-Contracts ausführen und das **`can-i-deploy`-Gate** als Pre-Deployment-Prüfung laufen lassen, sodass keine Seite eine brechende Änderung ausliefert.

### Wann verwenden, wann nicht

- **MUSS [MUST]** die Contract-Stufe an **Service-zu-Service-/API-Grenzen** anwenden, wo Consumer und Provider unabhängig evolvieren und brechende Änderungen **ohne eine geteilte Integrationsumgebung** gefangen werden müssen — der Microservice-Fall des Fundaments, in dem Contract-Tests breite Integration ersetzen [R1].
- **DARF NICHT [MUST NOT]** sie auf eine Grenze anwenden, die das Projekt **besitzt und im Gleichschritt ausliefert** und bereits als schmalen Integrationstest übt (eine echte Datenbank, die es kontrolliert, oder einen eigenen Service, der zusammen mit seinem Consumer deployt und versioniert wird), noch sie für vollständige funktionale Verifikation verwenden; das sind die Integration- bzw. Unit-/Component-Stufen [R2], [R7].
- **MUSS [MUST]** sie umgekehrt auf einen Service anwenden, den das Projekt **besitzt, aber unabhängig ausliefert**: Gemeinsamer Besitz beseitigt den Versions-Schiefstand nicht, den unabhängiges Deployment erzeugt, also ist eine eigene, aber unabhängig ausgelieferte Grenze eine Contract-Grenze. `spec/project/test-tier-integration/` [R2] nennt dieselbe Regel von der anderen Seite; der Unterscheider ist die **Auslieferungsgrenze**, nicht der Besitz.

### Anti-Patterns

- **MUSS [MUST]** als kanonische Anti-Patterns ablehnen: Geschäftslogik in Contracts testen; Contract-Tests als vollständige funktionale oder Integrationstests behandeln; Contract-Drift (kein Broker, kein `can-i-deploy`); den Contract über das hinaus über-spezifizieren, was der Consumer nutzt; und Consumer- und Provider-Versionen, die nie über den Broker abgeglichen werden.

### Traceability

- **MUSS [MUST]** einen Contract-Test, der einen abgeleiteten Testfall verifiziert, die **TC-ID** (und über sie die Anforderung) benennen lassen, die er abdeckt, gemäß der Traceability-Kette des Fundaments, damit Anforderungsabdeckung auditierbar ist.

### Optionales Referenzprofil

- **DARF [MAY]** ein vollständig ausgearbeitetes, stack-spezifisches Referenzprofil pinnen, klar zu „Referenz" degradiert. Ein illustratives consumer-driven-Profil: ein Pact-Consumer-Test, der eine Pact-Datei generiert, eine Provider-Verifikation, die sie mit Provider-States gegen den echten Provider abspielt, und ein Pact-Broker (oder PactFlow), der die Contracts mit einem `can-i-deploy`-Deployment-Gate hält; Pact existiert für die großen Ökosysteme (pact-jvm, pact-python, pact-js, pact-go). Für die provider-driven-Ausprägung ist ein illustratives Profil Spring Cloud Contract; für bi-directional eine OpenAPI-Spezifikation, die gegen den Mock des Consumers verifiziert wird. Werkzeugnamen sind illustrativ, nie verlangt.

## Akzeptanzkriterien

- [ ] Die Spec definiert einen Contract-Test als Verifikation eines Grenz-Agreements ohne beide Seiten live, gerahmt als Schließen der Stub-Drift-Lücke, zitiert auf Fowler/Pact
- [ ] Das consumer-driven-Modell ist als Referenz etabliert (Consumer definiert Erwartungen, Provider unabhängig per Replay verifiziert), mit dem Provider-State-Mechanismus
- [ ] Einem Provider State ist verboten, Daten zu arrangieren, die der echte Provider ablehnen würde, der Grund, warum die Provider-Verifikation das nicht fangen kann, ist benannt, und die Abgrenzung der Stufe gegen die portfolioweite Double-Treue-Regel ist explizit und auf die replay-verifizierten Ausprägungen begrenzt
- [ ] Die bi-direktionale Ausprägung trägt ihre eigene Anforderung, den consumer-seitigen Mock gegen die portfolioweite Treue-Regel zu prüfen, formuliert in den Requirements statt nur als Non-Goals-Nebenbemerkung, weil dort kein Provider-Code läuft
- [ ] Die drei Ausprägungen (consumer-driven, provider-driven, bi-directional) sind mit ihrer Eignung beschrieben, und consumer-driven ist der festgehaltene Default
- [ ] Assertions sind auf Agreement-Kompatibilität begrenzt (Form, Felder, Typen, Status-Codes, Protokoll), verboten für Geschäftslogik, und das Über-Spezifikations-Anti-Pattern ist benannt
- [ ] Determinismus via keine-Seite-live (Consumer-Mock + Provider-Replay) ist gefordert
- [ ] Ein Broker und ein `can-i-deploy`-artiges Deployment-Gate sind gefordert, und Contract-Drift (kein Broker / kein Gate) ist verboten
- [ ] Die Ausführungs-Platzierung weist Consumer-Tests der Consumer-Pipeline (PR-Gate), Provider-Verifikation der Provider-Pipeline und can-i-deploy als Pre-Deploy-Gate zu
- [ ] Die Wann-verwenden-/Wann-nicht-Regeln knüpfen an den Microservice-Fall (breite Integration ersetzen), schließen im Gleichschritt ausgelieferte Owned-Collaborator-Integration und vollständige funktionale Verifikation aus und schließen einen eigenen, aber unabhängig ausgelieferten Service über den Auslieferungsgrenzen-Unterscheider ein
- [ ] Die Grenze zur Integration-Stufe (echter eigener Kollaborateur live), zu den Unit-/Component-Stufen (interne Korrektheit) und zu E2E (ganzes System) ist explizit
- [ ] Traceability auf TC-ID ist gefordert, und ein optionales, klar degradiertes Referenzprofil (consumer-driven + Varianten) ist bereitgestellt, ohne ein Framework vorzuschreiben
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-pyramid-foundation/` — das Stufenmodell und die Aussage, dass Contract-Tests breite Integration über Service-Grenzen ersetzen
- [R2] `spec/project/test-tier-integration/` — die Geschwister-Stufe (ein echter eigener, live geübter Kollaborateur); die Integration↔Contract-Grenze
- [R7] `spec/project/test-tier-unit/` und `spec/project/test-tier-component/` — die eigene interne Korrektheit jedes Service, getrennt vom Cross-Boundary-Agreement
- [R8] `spec/project/e2e-test-automation/` — die Ganz-System-Stufe; die Contract↔E2E-Grenze
- [R9] `spec/project/quality-gate/` — führt die consumer-seitigen Contract-Tests aus und besitzt Ausführungsmechanik / Ausgabeform
- [R5] Martin Fowler, *ContractTest* (eine Komponente erfüllt einen Contract, den eine andere erwartet; Doubles liefern Echt-Service-Ergebnisse) — <https://martinfowler.com/bliki/ContractTest.html>
- [R6] Martin Fowler / I. Robinson, *Consumer-Driven Contracts* — <https://martinfowler.com/articles/consumerDrivenContracts.html>
- [R10] M. Fowler & T. Clemson, *Testing Strategies in a Microservice Architecture* (Contract-Tests, keine Component-Tests) — <https://martinfowler.com/articles/microservice-testing/>
- [R11] Ham Vocke, *The Practical Test Pyramid* (CDC; die vom Consumer genutzte Teilmenge) — <https://martinfowler.com/articles/practical-test-pyramid.html>
- [R12] Pact, *How Pact works* / *Provider verification* (Consumer-Mock generiert den Contract; Provider spielt ihn ab) — <https://docs.pact.io/getting_started/how_pact_works> , <https://docs.pact.io/provider>
- [R13] Spring Cloud Contract, *Consumer-Driven Contracts* (provider-driven-Ausprägung) — <https://docs.spring.io/spring-cloud-contract/reference/getting-started/cdc.html>
- [R14] Microsoft Engineering Playbook, *Consumer-Driven Contract Testing* — <https://microsoft.github.io/code-with-engineering-playbook/automated-testing/cdc-testing/>
- [R15] PactFlow, *Bi-Directional Contract Testing* (Provider veröffentlicht OpenAPI; keine Ausführung von Provider-Code) — <https://pactflow.io/bi-directional-contract-testing/>
- [R16] Pact, *Pact Broker* (Contract-Austausch, Versionierung, Kompatibilitätsmatrix) — <https://docs.pact.io/pact_broker>
- [R17] Pact, *can-i-deploy* (Pre-Deployment-Kompatibilitäts-Gate) — <https://docs.pact.io/pact_broker/can_i_deploy>
- [R18] `spec/project/test-falsifiability/` — die tier-übergreifende Taxonomie von Tests, die nicht fehlschlagen können; `T9` ist der Fehlermodus, den ein zu permissiver Provider State erzeugt, und `spec/project/test-pyramid-foundation/` §"Test-Double-Taxonomie" verantwortet die Treue-Regel, die die Exakt-Übereinstimmungs-Anforderung dieser Stufe für den consumer-seitigen Mock bereits übertrifft

## Offene Fragen

- Für ein Portfolio, das überwiegend aus einem einzelnen Claude-Code-Plugin und kleinen Services statt aus einem großen Microservice-Bestand besteht, wird die Contract-Stufe typischerweise **als begründet nicht-zutreffende Stufe ausgelassen** (gemäß der Stufen-Auslassungsregel des Fundaments), und sollte diese Spec das ausdrücklich sagen?
- Sollte das Portfolio sich auf ein Contract-Framework und einen Broker standardisieren (damit `can-i-deploy`-Gates über Repos hinweg einheitlich sind), oder projektspezifisch bleiben mit nur der Broker-+-Gate-Anforderung?
- Braucht die Entwickeln/Ausführen/Analysieren-Triade der Contract-Stufe eigene Agents, da sie zwei Repositories (Consumer und Provider) und einen Broker umspannt — oder ist sie besser als Cross-Repo-Workflow operationalisiert denn als Per-Repo-Skills?
- Wo ein Provider einen externen (nicht-Portfolio-)Consumer bedient, wird die bi-directional-Ausprägung (OpenAPI veröffentlichen) zum Default, da der externe Consumer das Framework des Portfolios nicht ausführen kann?
