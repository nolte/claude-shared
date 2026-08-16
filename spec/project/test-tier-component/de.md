# Test-Stufe: Component

Status: draft

## Kontext

Die Component-Stufe liegt **zwischen Unit und Integration** in der von `spec/project/test-pyramid-foundation/` definierten Pyramide. Sie übt eine einzelne **auslieferbare Komponente isoliert von ihren Peers**: eine ganze Komponente aus kollaborierenden Einheiten mit intakter echter interner Verdrahtung, aber mit jedem *externen* Kollaborateur ersetzt durch ein Test-Double an der Komponentengrenze. Sie ist langsamer als ein Unit-Test (Sekunden, nicht Millisekunden) und breiter (viele Einheiten, nicht eine), bleibt aber von echter Infrastruktur isoliert und damit schnell und deterministisch genug, um einen Pull Request zu gaten.

„Component-Test" bezeichnet je nach Art der Komponente zwei verschiedene Dinge, und eine werkzeug-agnostische Spec muss beide behandeln:

- ein **Frontend-Component-Test** rendert eine UI-Komponente und treibt sie, wie eine Nutzer:in es täte, mit Assertions auf den beobachtbaren Output (den gerenderten DOM / Accessibility-Tree);
- ein **Service-/Backend-Component-Test** treibt einen einzelnen Service durch seine eigene externe Schnittstelle (seine API), wobei alle externen Services, Dritt-APIs und oft der Datastore durch Doubles an der Prozessgrenze ersetzt sind.

Diese Spezifikation ist die stufenspezifische Realisierung der **invarianten Form** des Fundaments für die Component-Stufe. Sie füllt jedes von dieser Form geforderte Feld und ergänzt die stufenspezifische Substanz: die zwei Ausprägungen, die Regel beobachtbaren-Output-prüfen für Frontend, das Service-durch-eigene-Schnittstelle-Modell für Backend, die in-process/out-of-process-Realismus-vs-Geschwindigkeit-Achse und die Grenz-Doubles.

Sie ist bewusst **werkzeug-agnostisch**: Die bindenden Anforderungen nennen nie ein Framework. Konkrete Werkzeuge erscheinen nur als illustratives Referenzprofil.

**Verhältnis zu den anderen Specs.** Diese Stufe ist nach Verantwortung abgegrenzt, nicht durch Überschneidung:

- `spec/project/test-pyramid-foundation/` [R1] besitzt das Stufenmodell und die Meszaros-Test-Double-Taxonomie. Diese Spec detailliert die Component-Stufe; sie wiederholt das Modell nicht.
- `spec/project/test-tier-unit/` [R2] ist die Stufe **darunter**: eine isolierte Einheit mit gedoubelten Kollaborateuren. Die Grenze lautet „eine Einheit, Kollaborateure gemockt" (Unit) vs. „eine ganze Komponente kollaborierender Einheiten, echte interne Verdrahtung, nur Externe gedoubelt" (Component).
- `spec/project/test-tier-integration/` [R3] ist die Stufe **darüber**: Sie bringt einen **echten externen Kollaborateur** ein. Die Grenze lautet „Externe an der Grenze gestubbt" (Component) vs. „ein echter externer Kollaborateur" (Integration).
- `spec/project/quality-gate/` [R4] **führt** die Component-Stufe in der CI aus und besitzt Ausführungsmechanik und Ausgabeform.
- Für Frontend-Komponenten heften sich die Querschnitts-Dimensionen Visual Regression und Accessibility an dieser Stufe an (siehe §„Querschnitt auf Component-Ebene"); das tiefe Web-UI-Review bleibt `spec/frontend/webview-ui-optimization/`.

Leser: Spec-Autor:innen, die die Geschwister-Stufen-Specs schreiben; Skill- und Agent-Autor:innen, die die Component-Stufen-Triade (Entwicklung/Ausführung/Analyse) bauen; Frontend- und Backend-Entwickler:innen, die Component-Tests schreiben; Reviewer, die prüfen, ob ein Component-Test beobachtbares Verhalten prüft, nur Externe doubelt und deterministisch ist.

## Ziele

- Die Component-Stufe als einzelne auslieferbare Komponente in Isolation definieren und ihre zwei Ausprägungen (Frontend, Service) trennen, ohne ein Modell dem anderen aufzuzwingen
- Für Frontend Assertions auf **beobachtbaren Output über nutzerseitige Queries** verlangen, nie auf internen Zustand oder Instanzen
- Für Backend das Treiben des Service durch seine **eigene externe Schnittstelle** mit an der Grenze gedoubelten Externen verlangen
- Den **in-process-vs-out-of-process**-Realismus-/Geschwindigkeits-Trade-off zu einer expliziten, festgehaltenen Wahl machen
- Die Grenzen zur Unit-Stufe (eine isolierte Einheit) und zur Integration-Stufe (ein echter externer Kollaborateur) festzurren
- Die Stufe werkzeug-agnostisch halten, mit einem austauschbaren Referenzprofil statt eines vorgeschriebenen Frameworks

## Nicht-Ziele

- Die Stufe auszuführen oder ihre Ausführungsmechanik und Ausgabetabelle zu definieren: Eigentum von `spec/project/quality-gate/` [R4]
- Einen **echten externen Kollaborateur** einzubringen (Live-Service, echte Datenbank über das Netzwerk): Das überschreitet in die Integration-Stufe
- Eine isolierte Einheit mit gemockten Kollaborateuren zu testen: Das ist die Unit-Stufe
- Das ganze laufende System end-to-end durch seine Nutzeroberfläche zu treiben: Das ist die E2E-Stufe (`spec/project/e2e-test-automation/`)
- Ein bestimmtes Component-Test-Framework oder Service-Virtualization-Werkzeug vorzuschreiben: Das Referenzprofil ist illustrativ
- Das tiefe Web-UI-Performance-/Security-/i18n-Review zu definieren: Eigentum von `spec/frontend/webview-ui-optimization/`

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** einen Component-Test als einen definieren, der eine **einzelne auslieferbare Komponente kollaborierender Einheiten mit ihrer echten internen Verdrahtung** übt, isoliert von ihren Peers durch Ersetzen jedes externen Kollaborateurs mit einem Test-Double an der Komponentengrenze [R10].
- **MUSS [MUST]** die Grenze zur **Unit-Stufe** scharf halten: Ein Unit-Test übt eine isolierte Einheit (Kollaborateure abwesend oder gemockt); ein Component-Test übt die ganze Komponente mit echter interner Verdrahtung. Ein Verhalten, das aus einer einzelnen Einheit bestimmbar ist, gehört unter diese Stufe [R2], [R10].
- **MUSS [MUST]** die Grenze zur **Integration-Stufe** scharf halten: Auf der Component-Stufe ist jeder externe Kollaborateur an der Grenze **gedoubelt**; sobald ein Test einen **echten** externen Kollaborateur übt, ist es ein Integrationstest [R3], [R10].
- **MUSS [MUST]** auf das **beobachtbare Verhalten der Komponente über ihre öffentliche Oberfläche** prüfen (gerenderter Output für Frontend, API-Antworten und emittierte Events für Backend), nie auf internes Implementierungsdetail [R5], [R7].

### Zwei Ausprägungen: Frontend-Component und Service-Component

- **MUSS [MUST]** die zwei Ausprägungen als verschiedene Realisierungen derselben Stufe anerkennen und ein Projekt diejenige anwenden lassen, die zur getesteten Komponente passt: einen **Frontend**-UI-Component-Test und einen **Service-/Backend**-Component-Test.
- **MUSS [MUST]** die ausprägungsspezifischen Anforderungen unten auf die passende Ausprägung anwenden, während beide die Grenz-, Isolations-, Determinismus- und Platzierungsanforderungen dieser Stufe teilen.

### Frontend-Component-Tests: beobachtbaren Output prüfen, nicht Interna

- **MUSS [MUST]** Frontend-Component-Testing im Leitprinzip *„je mehr deine Tests der Art ähneln, wie deine Software benutzt wird, desto mehr Vertrauen geben sie"* verankern [R5], [R6]: Tests rendern die Komponente und prüfen, was eine Nutzer:in beobachten kann.
- **MUSS [MUST]** mit dem **gerenderten Output (DOM / Accessibility-Tree), nicht mit Komponenteninstanzen** arbeiten und **DARF NICHT [MUST NOT]** auf internen Zustand, private Methoden oder Instanz-Interna prüfen; Implementierungsdetails zu testen erzeugt **beides** — False Negatives (brüchiges Brechen bei verhaltenswahrendem Refactoring) **und** False Positives (ein Test, der besteht, während die Komponente kaputt ist) [R7], [R8].
- **DARF NICHT [MUST NOT]** **Shallow Rendering** verwenden, das die Kinder einer Komponente ausstubbt, um Interna zu inspizieren; es testet die Implementierung, nicht das Verhalten [R15].
- **MUSS [MUST]** **Snapshot-Testing** als enges Werkzeug behandeln, nicht als Default: Ein großer auto-generierter Snapshot prüft nichts Spezifisches, wird beim Update durchgewinkt und ist das dokumentierte Snapshot-Overuse-Anti-Pattern [R14]; explizite Assertions auf den spezifischen beobachtbaren Output bevorzugen.

### Frontend-Query-Priorität und die zwei legitimen Nutzer

- **MUSS [MUST]** Elemente mit **nutzerseitigen Queries in Prioritätsreihenfolge** auswählen — nach Rolle, dann Label, Placeholder, Text oder Display-Wert — und eine Test-ID-Query als **letzten Ausweg** reservieren, wenn kein nutzerwahrnehmbarer Anker existiert [R5], [R9].
- **MUSS [MUST]** eine UI-Komponente als mit genau **zwei legitimen Nutzern** behandeln — der **Endnutzer:in** (die mit dem gerenderten Output interagiert) und der **Entwickler:in** (die sie via Props rendert) — und Tests nur aus diesen zwei Blickwinkeln schreiben, nie durch eine synthetische „Test-Nutzer:in", die in den internen Zustand greift [R6].

### Service-Component-Tests: der Service durch seine eigene Schnittstelle

- **MUSS [MUST]** einen Service-Component-Test als einen definieren, der **einen einzelnen Service durch seine eigene externe Schnittstelle (seine API)** aus Consumer-Sicht treibt, wobei alle externen Kollaborateure (andere Services, Dritt-APIs und oft der Datastore) durch Test-Doubles an der Prozessgrenze ersetzt sind [R10].
- **MUSS [MUST]** die **eigenen internen Schnittstellen der Komponente nur zum Konfigurieren oder Abfragen** der Test-Double-Umgebung verwenden (Daten seeden, Stub-Antworten aufsetzen), nicht zum Umgehen des öffentlichen, getesteten Vertrags des Service [R10].
- **SOLLTE [SHOULD]** **Service Virtualization** (ein Stub von Upstream-Services, der vorgefertigte, konfigurierbare Antworten an der Netzwerk- oder In-Memory-Grenze liefert) verwenden, um den Service von seinen echten externen Abhängigkeiten zu isolieren [R12].

### In-process versus out-of-process (die Realismus-/Geschwindigkeits-Achse)

- **MUSS [MUST]** die **in-process-vs-out-of-process**-Wahl zu einer expliziten, festgehaltenen Entscheidung machen [R10]:
  - **In-process** — der Service wird in-memory mit In-Memory-Doubles und -Datastores instanziiert, kein Netzwerk wird berührt: schneller und einfacher, aber weniger realistisch, weil echte Serialisierung und Verdrahtung umgangen werden, und es braucht ein Test-Mode-Artefakt.
  - **Out-of-process** — der Service läuft als separat deployter Prozess, über seinen echten Transport geübt, mit weiterhin gedoubelten Externen: realistischer (echtes Netzwerk, Serialisierung), aber langsamer mit mehr beweglichen Teilen.
- **SOLLTE [SHOULD]** **in-process** für das schnelle Feedback bevorzugen, das die Stufe geben soll, und **out-of-process** für Komponenten reservieren, deren Transport-/Serialisierungsverhalten selbst Teil des getesteten Vertrags ist.

### Isolation und erlaubte Test-Doubles

- **MUSS [MUST]** **echt** halten: den eigenen Code der Komponente und ihre interne Verdrahtung; **MUSS [MUST]** doubeln: jeden externen Kollaborateur (andere Services, Dritt-APIs, Netzwerk und — wo Realismus es nicht verlangt — den Datastore), mit dem **Meszaros-Vokabular** des Fundaments (Dummy, Fake, Stub, Spy, Mock) und nennen, welche Art jedes Double ist [R1], [R11].
- **DARF [MAY]** einen **Fake** (zum Beispiel einen In-Memory-Datastore) anstelle eines echten Stores verwenden, wenn der Store nicht der Realismus ist, den der Test braucht; ein Test, der den **echten** Store verlangt, überschreitet in die Integration-Stufe [R3], [R11].
- **MUSS [MUST]** die Treue-Regel des Fundaments [R1] samt ihrer Ausnahme auf die Doubles an der Komponentengrenze dieser Stufe anwenden, statt sie zu wiederholen. Das **DARF [MAY]** oben ist genau das, was ein untreues Double auf dieser Stufe naheliegend macht: Es erlaubt einen In-Memory-Store gerade dort, wo der Store nicht der Realismus ist, den der Test braucht, und ein Fake, der einen Schreibvorgang akzeptiert, den der echte Store an einem Constraint ablehnen würde, macht den ganzen Component-Test zu einer Aussage über ein System, das es nicht geben kann. Jene Erlaubnis deckt Aufsetzkosten und Geschwindigkeit des Stores ab, nie seine **Ablehnungen**. Wo die Abweichung nicht geschlossen werden kann, **MUSS [MUST]** sie im Double selbst benannt werden [R1]; der resultierende Fehlermodus ist als `T9` gemäß [R16] zitierbar.

### Determinismus, Geschwindigkeit und Platzierung

- **MUSS [MUST]** die Stufe **deterministisch** halten: Zeit, Zufall und alle Netzwerk-Interaktion kontrollieren (jeder externe Aufruf ist gedoubelt), sodass ein Component-Test nie an Real-World-Lage flakt, gemäß dem Fundament.
- **MUSS [MUST]** akzeptieren, dass Component-Tests **langsamer als Unit-Tests (Sekunden)** sind, sie aber von echter Infrastruktur **isoliert** halten, damit sie schnell genug bleiben, um einen Pull Request in der CI zu **gaten**; die schnellen **DÜRFEN [MAY]** auch im Pre-Commit laufen.

### Querschnitt auf Component-Ebene

- **MUSS [MUST]** **Visual-Regression**- und **Accessibility (A11y)**-Prüfungen als die Querschnitts-Dimensionen des Fundaments behandeln, angewandt *auf* Component-Ebene (Assertions auf denselben gerenderten Output), nicht als eigene Stufe; ein Component-Test **DARF [MAY]** eine A11y-Assertion oder eine Visual-Snapshot-Baseline gegen die gerenderte Komponente tragen.
- **MUSS [MUST]** die Grenze zu `spec/frontend/webview-ui-optimization/` (tiefes Web-UI-Performance-/Security-/i18n-Review) intakt halten: Jenes Review ist ein eigener, breiterer Belang, nicht die Component-Stufe.

### Anti-Patterns

- **MUSS [MUST]** als kanonische Anti-Patterns ablehnen: Assertions auf internen Zustand/Instanzen; Shallow Rendering; Snapshot-Overuse; brüchige implementierungsgekoppelte Selektoren; das Hochfahren eines **echten** externen Kollaborateurs (das ist Integration); eine zu breite Komponentengrenze, die mehrere Komponenten verschluckt; und flaky Komponenten durch unkontrollierte Zeit oder Netzwerk.

### Traceability

- **MUSS [MUST]** einen Component-Test, der einen abgeleiteten Testfall verifiziert, die **TC-ID** (und über sie die Anforderung) benennen lassen, die er abdeckt, gemäß der Traceability-Kette des Fundaments, damit Anforderungsabdeckung auditierbar ist.

### Optionales Referenzprofil

- **DARF [MAY]** ein vollständig ausgearbeitetes, stack-spezifisches Referenzprofil pinnen, klar zu „Referenz" degradiert. Illustratives Frontend-Profil: ein Renderer der Testing-Library-Familie (React/Vue/Svelte Testing Library) mit user-event-Interaktion und role-first-Queries, optional Storybook-Play-Funktionen für Interaktion, ausgeführt unter Vitest. Illustratives Backend-Profil: ein In-Process-Service-Harness (zum Beispiel ein Framework-Test-Client wie Starlette/FastAPI `TestClient` oder ein Spring-Boot-Slice) mit einem Service-Virtualization-Stub (zum Beispiel WireMock) für Externe. Werkzeugnamen sind illustrativ, nie verlangt.

## Akzeptanzkriterien

- [ ] Die Spec definiert die Component-Stufe als einzelne auslieferbare Komponente in Isolation (echte interne Verdrahtung, Externe gedoubelt) und nennt beide Ausprägungen (Frontend, Service)
- [ ] Die Grenze zur Unit-Stufe (eine isolierte Einheit vs. eine ganze Komponente) und zur Integration-Stufe (Externe gedoubelt vs. ein echter externer Kollaborateur) ist explizit und zitiert
- [ ] Frontend-Tests sind verpflichtet, auf gerenderten Output (DOM / Accessibility-Tree) zu prüfen, verboten auf Interna zu prüfen, mit der False-Negative-+-False-Positive-Begründung und der Kein-Shallow-Rendering-Regel
- [ ] Die nutzerseitige Query-Priorität (Rolle zuerst, Test-ID letzter Ausweg) und das Zwei-legitime-Nutzer-Modell sind gefordert, zitiert auf Testing Library / Dodds
- [ ] Snapshot-Testing ist als enges Werkzeug gebunden mit benanntem Overuse-Anti-Pattern
- [ ] Service-Component-Tests sind verpflichtet, den Service durch seine eigene Schnittstelle mit gedoubelten Externen zu treiben, wobei interne Schnittstellen nur zum Konfigurieren/Abfragen dienen, zitiert auf Fowler/Clemson
- [ ] Der in-process-vs-out-of-process-Realismus-/Geschwindigkeits-Trade-off ist eine explizite festgehaltene Wahl
- [ ] Isolation hält die Komponente echt und doubelt Externe mit dem Meszaros-Vokabular; ein echter Datastore ist als Überschreiten in die Integration deklariert
- [ ] Die Treue-Regel des Fundaments wird per Verweis auf die Grenz-Doubles angewandt statt wiederholt, und die In-Memory-Store-Erlaubnis ist auf Kosten und Geschwindigkeit statt auf Ablehnungen begrenzt
- [ ] Determinismus (kontrollierte Zeit/Zufall/Netzwerk) und Platzierung (PR-gatende CI, schnelle im Pre-Commit) sind gefordert
- [ ] Visual-Regression und Accessibility sind als Querschnitt auf Component-Ebene platziert, gegen `webview-ui-optimization` abgegrenzt
- [ ] Traceability auf TC-ID ist gefordert, und ein optionales, klar degradiertes Referenzprofil (Frontend + Backend) ist bereitgestellt, ohne ein Framework vorzuschreiben
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-pyramid-foundation/` — das Stufenmodell und die Meszaros-Test-Double-Taxonomie, die diese Spec realisiert
- [R2] `spec/project/test-tier-unit/` — die Stufe darunter (eine isolierte Einheit, Kollaborateure gemockt); die Unit↔Component-Grenze
- [R3] `spec/project/test-tier-integration/` — die Stufe darüber (ein echter externer Kollaborateur); die Component↔Integration-Grenze
- [R4] `spec/project/quality-gate/` — führt die Component-Stufe in der CI aus und besitzt Ausführungsmechanik / Ausgabeform
- [R5] Testing Library, *Guiding Principles* (echter Nutzung ähneln; Query-Priorität) — <https://testing-library.com/docs/guiding-principles/>
- [R6] Kent C. Dodds, *Avoid the Test User* (die zwei legitimen Nutzer einer Komponente) — <https://kentcdodds.com/blog/avoid-the-test-user>
- [R7] Kent C. Dodds, *Testing Implementation Details* (False Negatives und False Positives) — <https://kentcdodds.com/blog/testing-implementation-details>
- [R8] Kent C. Dodds, *Introducing the React Testing Library* (DOM-Knoten testen, nicht Instanzen) — <https://kentcdodds.com/blog/introducing-the-react-testing-library>
- [R9] Testing Library, *About Queries* (Prioritätsreihenfolge, Test-ID als letzter Ausweg) — <https://testing-library.com/docs/queries/about/>
- [R10] M. Fowler & T. Clemson, *Testing Strategies in a Microservice Architecture* (Component-Test-Definition; in-process vs. out-of-process) — <https://martinfowler.com/articles/microservice-testing/>
- [R11] Martin Fowler, *Mocks Aren't Stubs* (die fünf Meszaros-Doubles) — <https://martinfowler.com/articles/mocksArentStubs.html>
- [R12] WireMock, *Service Virtualization* (Upstream-Services an der Grenze stubben) — <https://wiremock.org/docs/solutions/service-virtualization/>
- [R13] Storybook, *Interaction Testing* (Play-Funktionen) — <https://storybook.js.org/docs/writing-tests/interaction-testing>
- [R14] Jest, *Snapshot Testing* (wo es hilft; der Overuse-Vorbehalt) — <https://jestjs.io/docs/snapshot-testing>
- [R15] Kent C. Dodds, *Why I Never Use Shallow Rendering* — <https://kentcdodds.com/blog/why-i-never-use-shallow-rendering>
- [R16] `spec/project/test-falsifiability/` — die tier-übergreifende Taxonomie von Tests, die nicht fehlschlagen können; `T9` ist der Fehlermodus, den ein Grenz-Double erzeugt, das permissiver ist als der Externe, den es ersetzt, und die Spec trägt die Review-Frage, die ihn detektiert

## Offene Fragen

- Sollte das Portfolio eine A11y-Assertion einer Frontend-Komponente als Default verlangen (jede gerenderte Komponente trägt mindestens eine Accessibility-Prüfung) oder sie als Querschnitts-Ergänzung opt-in lassen?
- Sollte das Portfolio für Backend-Services auf In-Process-Component-Tests defaulten und eine explizite Begründung für Out-of-process verlangen, oder die Achse vollständig projektspezifisch lassen?
- Verdient die Entwickeln/Ausführen/Analysieren-Triade der Component-Stufe ausprägungsspezifische Agents (einen Frontend-Component-Test-Autor getrennt von einem Service-Component-Test-Autor) oder einen Component-Stufen-Autor mit Ausprägungs-Parameter?
- Wo ein Component-Test eine Visual-Regression-Baseline trägt, lebt das Baseline-Artefakt beim Test, und wie wird sein Review gegen `webview-ui-optimization` abgegrenzt?
