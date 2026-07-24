# Fundament der Testpyramide

Status: draft

## Kontext

Jedes Projekt im Portfolio braucht eine automatisierte Test-Suite, aber „schreib Tests" ist keine Strategie. Ohne ein gemeinsames Modell driften Suites in die zwei klassischen Fehlermodi: eine dünne Basis mit aufgeblähter Spitze (das *Ice-Cream-Cone*-Anti-Pattern — langsame, flaky End-to-End-Tests als Ersatz für billige Prüfungen) oder ein zusammenhangloser Haufen, bei dem niemand sagen kann, welches Verhalten auf welcher Ebene verifiziert wird. Der wiederverwendbare, portfolioweite Teil des Testens ist kein bestimmter Test und kein bestimmtes Werkzeug — es ist das **Modell, das entscheidet, was auf welcher Ebene getestet wird, wie die Ebenen zusammenspielen und welche Invarianten jede Ebene halten muss**. Dieses Modell ist framework- und sprachunabhängig. Der wegwerfbare Teil ist der Glue-Code je Stufe: welcher Runner, welche Assertion-Bibliothek, welches Verzeichnis.

Diese Spezifikation ist das **Fundament** der Test-Automatisierungs-Disziplin des Portfolios. Sie besitzt das Stufenmodell, die geschlossene funktionale Stufen-Taxonomie, die orthogonalen Querschnitts-(nicht-funktionalen)-Dimensionen und die stufenübergreifenden Governance-Invarianten. Sie ist bewusst das *Apex*-Dokument: Sie spezifiziert nicht erschöpfend, wie man einen Unit- oder Integrationstest schreibt — stattdessen definiert sie die **invariante Form, die jede Stufen-Spec füllen muss**, damit die darauf aufbauenden Stufen-Specs zueinander konsistent, überschneidungsfrei und auffindbar bleiben. Der Endzustand ist eine kleine Familie: dieses Fundament, eine Spec pro funktionaler Stufe, optional eine Spec pro Querschnitts-Dimension und eine Schicht aus Skills und Agents, die Tests je Stufe entwickeln, ausführen und analysieren.

Das Modell ist in der etablierten Literatur verankert, nicht erfunden: die Testpyramide (Cohn, popularisiert und verfeinert von Fowler [R5], [R6]), ihre praktische Neufassung (Vocke [R7]), die ausdrückliche Warnung, dass die Formdebatte ohne gemeinsame Definitionen von „Unit" und „Integration" bedeutungslos ist (Fowler, *On the Diverse And Fantastical Shapes of Testing* [R8]), die architekturspezifischen Gegenmodelle (Dodds' Testing Trophy für Frontend [R9], Spotifys Testing Honeycomb für Microservices [R10]), das Test-Double-Vokabular (Meszaros via Fowler [R11]), Consumer-Driven Contract Testing als Microservice-Ersatz für breite Integration (Fowler [R12], Pact [R13], Thoughtworks-„Hold" auf breite Integrationstests [R14]) sowie die Governance-Evidenz zu Flakiness (Google [R15]), Coverage-als-Vanity-Metrik (Fowler [R16], Google [R17]) und Mutationstest als stärkeres Signal (pitest [R18]).

**Verhältnis zu den bestehenden Test-Specs.** Drei Test-Specs existieren bereits und bleiben für ihre Stufe bzw. Funktion maßgeblich; dieses Fundament referenziert sie als Stufen-Realisierungen, statt sie zu wiederholen:

- `spec/project/e2e-test-automation/` — die Realisierung der E2E-Stufe (Page-Object-Disziplin, zustandsbasierte Waits, Screenshot-/Protokoll-Auditierbarkeit, das Selenium-+-pytest-Referenzprofil, der `test-pyramid-check`-Skill und die drei `e2e-*`-Agents). Ihre eingebettete Subsektion §„Test-tier completeness (the pyramid)" ist älter als dieses Fundament; dieses Stufenmodell wird **hierher migriert**, und die e2e-Spec wird in einem Folge-PR darauf reduziert, dieses Fundament zu referenzieren (siehe Offene Fragen).
- `spec/project/test-case-derivation/` — leitet die abstrakten, framework-agnostischen Testfälle (TC-IDs) ab, die die Suites je Stufe automatisieren; der `test-case-extractor`-Agent realisiert sie. Dieses Fundament besitzt den Traceability-Vertrag, durch den diese TC-IDs fließen, nicht die Ableitungstechnik.
- `spec/project/quality-gate/` — führt die schnellen Stufen (Lint + Typecheck + Test) als einzelnen Aufruf aus und klassifiziert Pass/Fail; der `quality-gate`-Skill realisiert es. Dieses Fundament besitzt das *CI-Gating-Modell* (welche Stufen einen PR gaten); quality-gate besitzt *Ausführung und Ausgabeform* der schnellen Stufen.

Leser: Spec-Autor:innen, die die Stufen-Specs auf diesem Fundament schreiben; Skill- und Agent-Autor:innen, die das Tooling für Test-Entwicklung/-Ausführung/-Analyse je Stufe bauen; QA-Engineers und Entwickler:innen, die entscheiden, auf welcher Stufe ein Verhalten gehört; Reviewer, die prüfen, ob eine Suite stufen-balanciert, deterministisch, nachvollziehbar und gegatet ist.

## Ziele

- Das **Stufenmodell** einmal framework-neutral besitzen: die Anker-Testpyramide plus die dokumentierten architekturspezifischen Varianten, damit jedes Projekt eine Form anhand von Evidenz statt Dogma wählt
- Eine **geschlossene funktionale Stufen-Taxonomie** definieren (Static Analysis → Unit → Component → Integration → Contract → End-to-End), in die sich jede Stufen-Spec ohne Überschneidung oder Lücke einfügt
- Die **invariante Stufen-Form** definieren — den Meta-Vertrag, den jede Stufen-Spec füllen muss — damit die abgeleiteten Specs strukturell konsistent und gegen eine einzige Vorlage prüfbar bleiben
- **Querschnitts-/nicht-funktionale** Belange (Performance, Accessibility, Security, Mutation, Visual Regression, Exploratory) als orthogonale Lagen behandeln, die *auf* Stufen angewandt werden, niemals als weitere Pyramidenebene
- Die **Governance-Invarianten** kodieren, die über alle Stufen gelten: Determinismus vor Flakiness, niedrigste-Stufe-die-Vertrauen-gibt vor festen Verhältnissen, Coverage-als-Leitlinie-nicht-Ziel, Mutationsscore als stärkeres Signal, Traceability Anforderung→Fall→Test und ein gestuftes CI-Gating-Modell
- **Werkzeug-agnostisch** bleiben: Werkzeuge nur als illustrative Beispiele nennen und jede Stufen-Spec ihr eigenes optionales Referenzprofil pinnen lassen, genau wie `e2e-test-automation` Selenium + pytest pinnt
- Die **Roadmap** bereitstellen, unter der die Stufen-Specs, Querschnitts-Specs und Skills/Agents je Stufe geschrieben werden

## Nicht-Ziele

- Erschöpfend zu spezifizieren, wie man einen Test auf einer bestimmten Stufe schreibt — jede funktionale Stufe erhält (oder hat bereits) ihre **eigene** Spec, die auf der invarianten Form dieses Fundaments aufbaut; dieses Dokument definiert die Form, nicht das Stufen-Detail
- Die E2E-Disziplin, die Testfall-Ableitungstechnik oder den Quality-Gate-Ausführungsvertrag zu wiederholen — die bleiben Eigentum von `spec/project/e2e-test-automation/`, `spec/project/test-case-derivation/` bzw. `spec/project/quality-gate/`
- Einen bestimmten Runner, eine Assertion-Bibliothek, ein Mocking-Framework oder ein Automatisierungswerkzeug für irgendeine Stufe vorzuschreiben — Werkzeugnamen in dieser Spec sind illustrativ; bindende Werkzeugwahlen, falls vorhanden, liegen im optionalen Referenzprofil einer Stufen-Spec
- Eine **feste numerische Verteilung** der Tests über die Stufen vorzuschreiben (z. B. „70/20/10"); feste Verhältnisse sind laut [R5], [R7], [R8] ein Anti-Pattern, und diese Spec verbietet, sie als Anforderung zu kodieren
- Die Anforderungsdokumente zu verfassen oder zu bearbeiten, auf die Testfälle zurückverweisen
- Die Skills und Agents selbst zu bauen — diese Spec deklariert die Rollen und ihre Stufenzuordnung; die Artefakte werden separat via `skill-management` / den Plugin-Developer-Flow verfasst und durch `spec/claude/` geregelt
- Die projektspezifische Stufen-Balance zu wählen — die *Form-Entscheidung* ist projektspezifisch und evidenzgetrieben; diese Spec gibt die Entscheidungsregel, nicht die Antwort

## Anforderungen

### Das Stufenmodell und seine Varianten

- **MUSS [MUST]** die **Testpyramide als Anker-Modell des Portfolios** übernehmen: Eine Suite ist als Ebenen strukturiert, bei denen untere Ebenen zahlreicher, schneller, billiger und isolierter sind und höhere Ebenen weniger zahlreich, langsamer, teurer und breiter im Umfang, auf der invertierten Kosten/Geschwindigkeits/Brüchigkeits-Basis aus [R5], [R6].
- **MUSS [MUST]** die Pyramide als **Entscheidungsheuristik, nicht als Quote** behandeln: Die maßgebliche Regel lautet *„schreibe den Test auf der niedrigsten Stufe, die dir noch das nötige Vertrauen gibt"* [R5], [R7]. Ein Test höherer Stufe ist nur gerechtfertigt, wenn kein Test einer niedrigeren Stufe dasselbe Vertrauen herstellen kann.
- **DARF NICHT [MUST NOT]** ein festes stufenübergreifendes Verhältnis (etwa 70/20/10) als normative Anforderung in dieser oder einer abgeleiteten Spec kodieren; feste Verteilungen sind ausdrücklich ein Anti-Pattern [R7], [R8].
- **MUSS [MUST]** anerkennen, dass die Formdebatte ohne gemeinsame Stufendefinitionen inkohärent ist — „Unit" und „Integration" werden über Teams hinweg uneinheitlich verwendet [R8] — und daher **MUSS [MUST]** an die Definitionen aus §„Funktionale Stufen-Taxonomie" gebunden werden, wann immer ein Stufenname in einer abgeleiteten Spec, einem Skill oder Agent verwendet wird.
- **SOLLTE [SHOULD]** die anerkannten **architekturspezifischen Varianten** und ihre jeweilige Eignung dokumentieren, ohne eine davon als Konkurrenten zum Anker zu behandeln:
  - *Testing Trophy* (Dodds [R9]) — Static → Unit → Integration → E2E mit der **Integrationsstufe als größter**, begründet mit „je mehr deine Tests der Art ähneln, wie deine Software benutzt wird, desto mehr Vertrauen geben sie"; passt zu **Frontend-/UI-lastigem** Code.
  - *Testing Honeycomb* (Spotify [R10]) — ein kleiner Kern isolierter Tests, eine **große integrierte Test-Mitte**, wenige Implementierungsdetail-Tests; passt zu **Microservices**, wo die meiste Komplexität *zwischen* Services liegt und eine klassische Pyramide aktiv irreführend sein kann.
  - *Ice-Cream-Cone* — invertierte Pyramide (viel Manuell/E2E, wenig Unit); ausdrücklich als **Anti-Pattern** benannt, das zu erkennen und zu korrigieren ist.
  - *Testing Diamond* — eine fette Integrations-Mitte mit dünnen Unit- und E2E-Enden; eine anerkannte Form für integrationsdominante Systeme.
- **MUSS [MUST]** jedes konsumierende Projekt **seine Form anhand von Evidenz wählen** lassen (Architektur, Change-Failure-Daten, Flake-Rate) und diese Wahl festhalten; die Wahl ist eine projektspezifische Entscheidung, kein Portfolio-Mandat.

### Funktionale Stufen-Taxonomie

- **MUSS [MUST]** das Folgende als **geschlossene, geordnete Menge** funktionaler Stufen behandeln, vom Fundament bis zur Spitze. Jede Stufen-Spec, jeder Skill und Agent bildet genau einen Eintrag ab; ein Verhalten wird auf dem niedrigsten anwendbaren Eintrag getestet:
  1. **Static Analysis** — Lint, Typecheck, Format-Check sowie statische Security-/Komplexitätsregeln. Läuft, ohne das Programm auszuführen; die Fundamentebene der Pyramide gemäß der Trophy [R9]. In der Ausführung Eigentum von `spec/project/quality-gate/`.
  2. **Unit** — verifiziert eine Verhaltenseinheit isoliert. **Solitäre** Unit-Tests isolieren die Einheit mit Test-Doubles von Kollaborateuren; **gesellige** (sociable) Unit-Tests üben echte Kollaborateure [R6], [R11]. Die Definition „einer Einheit" ist **bewusst team-bestimmt** [R6], und eine projektspezifische Unit-Spec hält sie fest.
  3. **Component** — verifiziert eine einzelne deploybare/auslieferbare Komponente isoliert von ihren Peers: eine gerenderte Frontend-Komponente gegen ihren eigenen Vertrag oder ein Backend-Service, der durch seine eigene Schnittstelle geübt wird, wobei seine externen Abhängigkeiten an der Prozessgrenze durch Doubles ersetzt sind.
  4. **Integration** — verifiziert, dass eine Unit/Komponente korrekt mit einem benachbarten echten Kollaborateur spricht. **Schmale Integration** übt einen echten Kollaborateur (z. B. eine Datenbank über einen ephemeren Container) bei gedoubeltem Rest; **breite Integration** stellt viele Live-Services bereit und **MUSS [MUST]** als kostspielig behandelt und minimiert werden [R12], [R14].
  5. **Contract** — verifiziert die Vereinbarung an einer Service-Grenze, ohne beide Seiten hochzufahren. **Consumer-Driven Contracts** [R12], [R13] erlauben, die Erwartungen eines Consumers unabhängig gegen einen Provider zu verifizieren; in Microservice-Architekturen **SOLLTEN [SHOULD]** Contract-Tests breite Integrationstests über Service-Grenzen hinweg ersetzen [R13], [R14].
  6. **End-to-End / System** — treibt die echte nutzerseitige Oberfläche eines laufenden Systems und prüft auf beobachtbares Verhalten. Wenige, langsam und am anfälligsten für Flakiness; vollständig geregelt durch `spec/project/e2e-test-automation/`.
- **DARF NICHT [MUST NOT]** eine neue funktionale Stufe in einer abgeleiteten Spec einführen, ohne diese Taxonomie zuerst zu ändern; die geschlossene Menge verhindert das Problem unscharfer Definitionen [R8].
- **DARF [MAY]** jede Stufe weglassen, die auf ein gegebenes Projekt nicht zutrifft (z. B. keine Contract-Stufe, wenn das System keine Service-Grenze anbietet oder konsumiert), festgehalten als bewusste, begründete Auslassung statt als stille Lücke.

### Invariante Stufen-Form (der Meta-Vertrag)

- Jede **Stufen-Spec MUSS [MUST]** mindestens das Folgende definieren, damit die Familie strukturell konsistent und gegen eine Vorlage prüfbar bleibt:
  - **Zweck & Umfangsgrenze** — was diese Stufe verifiziert und, ausdrücklich, was sie **NICHT [MUST NOT]** behaupten darf (die Grenze zur Stufe darunter und darüber).
  - **Isolationsgrad & erlaubte Test-Doubles** — welche Kollaborateure echt und welche gedoubelt sind, mit dem Vokabular aus §„Test-Double-Taxonomie".
  - **Geschwindigkeits- & Determinismus-Budget** — eine Größenordnungserwartung (z. B. Millisekunden für Unit, Sekunden für Integration) und die Determinismus-Garantie gemäß §„Determinismus und Flakiness".
  - **Ausführungs-Platzierung** — Pre-Commit / PR-gatendes CI / Nightly, konsistent mit §„CI-Gating-Modell".
  - **Traceability** — wie ein Test dieser Stufe die Anforderung / TC-ID benennt, die er verifiziert, gemäß §„Traceability".
  - **Kanonische Anti-Patterns** — die stufenspezifischen Gerüche, die ein Reviewer ablehnt (z. B. festes `sleep` in E2E, roher Kollaborateur-Zugriff in solitären Unit-Tests, Behaupten von Implementierungsdetails in Integration).
  - **Optionales Referenzprofil** — ein vollständig ausgearbeiteter, stack-spezifischer Default **DARF [MAY]** gepinnt werden (wie `e2e-test-automation` Selenium + pytest pinnt), klar zu „Referenz" degradiert, nie zur Anforderung erhoben.
- Eine Stufen-Spec **MUSS [MUST]** ihre Grenzen zu den Nachbarstufen nach Verantwortung deklarieren, sodass zwei Stufen-Specs niemals dasselbe Verhalten beanspruchen.

### Test-Double-Taxonomie

- **MUSS [MUST]** die fünf **Meszaros-Test-Double-Kategorien** [R11] mit diesen Bedeutungen portfolioweit verwenden, damit Stufen-Specs und Reviews ein Vokabular sprechen:
  - **Dummy** — zum Füllen einer Parameterliste übergeben, nie tatsächlich genutzt.
  - **Fake** — eine funktionierende, aber abgekürzte Implementierung, die für Produktion ungeeignet ist (z. B. ein In-Memory-Repository).
  - **Stub** — liefert vorgefertigte Antworten auf Aufrufe während des Tests; unterstützt **Zustandsverifikation**.
  - **Spy** — ein Stub, der zusätzlich aufzeichnet, wie er aufgerufen wurde.
  - **Mock** — mit Erwartungen vorprogrammiert und für **Verhaltensverifikation** verwendet (prüft, *wie* Kollaborateure aufgerufen wurden) [R11].
- **MUSS [MUST]** **Zustandsverifikation** (den resultierenden Zustand prüfen) von **Verhaltensverifikation** (die Interaktionen prüfen) unterscheiden; eine Stufen-Spec nennt, welche sie erwartet, und Über-Nutzung von Verhaltensverifikation (Over-Mocking) **MUSS [MUST]** als der Geruch markiert werden, der Tests an die Implementierung koppelt.

### Querschnitts-(nicht-funktionale)-Dimensionen

- **MUSS [MUST]** das Folgende als **orthogonale Dimensionen behandeln, die auf einer oder mehreren funktionalen Stufen angewandt werden**, niemals als zusätzliche Pyramidenebene:
  - **Performance / Last** — angewandt auf Component-, Integrations- oder E2E-Umfang; gatet ein Release, üblicherweise keinen PR.
  - **Accessibility (A11y)** — angewandt auf Component- und E2E-Umfang (z. B. automatisierte Regelprüfungen auf gerendertem Output).
  - **Security** — **SAST** (statische Analyse des Quellcodes) sitzt auf der Static-Analysis-Stufe; **DAST** (dynamische Analyse eines laufenden Systems) sitzt auf E2E-/System-Umfang [R19]. Die Grenze zu `spec/project/dependency-audit/` (Dependency-CVEs) bleibt gewahrt.
  - **Mutationstest** — ein **Meta-Maß für Suite-Qualität**, keine Stufe: Er mutiert Produktionscode und prüft, ob die Suite die Änderung fängt — ein stärkeres Signal als Coverage [R18]. Berichtet als Suite-Qualitätsmetrik gemäß §„Coverage und Suite-Qualitätsmetriken".
  - **Visual Regression** — angewandt auf Component- und E2E-Umfang; vergleicht gerenderten Output gegen eine Baseline.
  - **Exploratory / Manuell** — nicht automatisiert, menschlich, ergänzend zu den automatisierten Stufen; festgehalten, aber nie gatend.
- Eine Querschnitts-Dimension **DARF [MAY]** eine eigene Spec unter diesem Fundament erhalten, **MUSS [MUST]** aber angeben, an welche funktionalen Stufen sie sich anheftet, statt eine Stufe neu zu definieren.

### Determinismus und Flakiness

- **MUSS [MUST]** verlangen, dass jeder automatisierte Test **deterministisch** ist: gleicher Input ⇒ gleiches Ergebnis, unabhängig von Ausführungsreihenfolge, Wanduhrzeit, Netzwerklage oder parallelen Läufen.
- **MUSS [MUST]** einen **flaky Test** (einer, der ohne Codeänderung mal besteht und mal fehlschlägt) als eigenständigen Defekt behandeln: Flakiness untergräbt das Vertrauen in die ganze Suite [R15]. Ein flaky Test **MUSS [MUST]** unter Quarantäne gestellt werden (vom gatenden Signal ausgeschlossen, als Defekt verfolgt), statt ihn intermittierend fehlschlagen zu lassen oder ihn still ewig erneut auszuführen.
- **DARF NICHT [MUST NOT]** feste Zeitverzögerungen (`sleep`) zur Synchronisation verwenden; Waits sind zustandsbasiert (die E2E-Realisierung davon steht in `spec/project/e2e-test-automation/`).
- **SOLLTE [SHOULD]** Tests unabhängig und in sich geschlossen machen — jeder baut seinen eigenen Zustand auf und ab — damit sie in beliebiger Reihenfolge und parallel laufen können.

### Testdaten und Isolation

- **MUSS [MUST]** Testdaten je Test isolieren, sodass kein Test von den Rückständen eines anderen abhängt; geteilte veränderliche Fixtures über Tests hinweg sind verboten.
- **SOLLTE [SHOULD]** ephemere, programmatisch geseedete Daten bevorzugen (z. B. Per-Test-Factories, ephemere Container auf der Integrationsstufe) gegenüber geteilten langlebigen Fixtures.
- **MUSS [MUST]** externe echte Ressourcen (Datenbanken, Message-Broker) auf die schmale Integrationsstufe begrenzen und deterministisch abbauen.

### Coverage und Suite-Qualitätsmetriken

- **MUSS [MUST]** Line-/Branch-**Coverage als Leitlinie, nicht als Ziel** behandeln: Coverage auf eine feste Zahl zu treiben, lädt Goodharts Gesetz ein und erzeugt assertion-freie Tests, die Code ausführen, ohne ihn zu verifizieren [R16], [R17].
- **DARF NICHT [MUST NOT]** einen PR allein an einer Coverage-Prozentschwelle als primärem Qualitätssignal gaten; Coverage-Lücken sind ein Anlass zur Frage „ist dieses Risiko einen Test wert?", kein automatisches Fail [R16].
- **SOLLTE [SHOULD]** **Mutationsscore** als stärkeres Suite-Qualitätssignal verwenden, wo die Toolchain es unterstützt, da er misst, ob Tests Verhaltensänderungen tatsächlich fangen, statt nur Zeilen auszuführen [R18].
- **DARF [MAY]** Coverage als informativen Trend berichten; sie wird beobachtet, nicht gejagt.

### CI-Gating-Modell

- **MUSS [MUST]** die Ausführung nach Stufe staffeln, damit Feedback schnell ist: Die **schnellen Stufen** (Static Analysis, Unit, Component, schmale Integration, Contract) **MÜSSEN [MUST]** einen Pull Request gaten, spiegelbildlich zu `spec/project/quality-gate/` für die Lint-/Typecheck-/Test-Teilmenge.
- **SOLLTE [SHOULD]** die **langsamen oder breiten Stufen** (E2E, breite Integration, Performance, volles DAST) nach Zeitplan (Nightly) oder in einer dedizierten Stufe ausführen, statt jeden PR zu blockieren, es sei denn, das Risikoprofil eines Projekts rechtfertigt das Gaten auf ihnen.
- **MUSS [MUST]** die Menge der **erforderlichen Status-Checks** für den Integrations-Branch als Code deklariert halten gemäß `spec/project/pull-request-workflow/` — diese Spec definiert, *welche Stufen ins Gate gehören*, jene Spec definiert, *wie das Gate erzwungen wird*.
- **MUSS [MUST]** eine fehlschlagende erforderliche Test-Stufe an Fix-Forward / `workflow-health`-Triage routen, niemals an einen Waiver, konsistent mit den Specs quality-gate und pull-request-workflow.

### Traceability

- **MUSS [MUST]** eine ununterbrochene Kette **Anforderung → abstrakter Testfall (TC-ID) → automatisierter Test** über die Stufen hinweg bewahren: Ein Test benennt die TC-ID (und über sie die Anforderung), die er verifiziert, sodass die Abdeckung von *Anforderungen* — nicht nur Code — auditierbar ist.
- **MUSS [MUST]** die unter `spec/project/test-case-derivation/` erzeugten abstrakten Fälle (ihre TC-IDs) konsumieren, statt sie neu abzuleiten; diese Spec besitzt die Kette, nicht die Ableitung.
- **SOLLTE [SHOULD]** die TC-ID im Test selbst sichtbar machen (Name, Tag oder Docstring), damit der Bericht eines Laufs ohne externe Buchführung auf Anforderungen zurückgemappt wird.

### Test-Autorenkonventionen

- **MUSS [MUST]** jeden Test als **Arrange–Act–Assert** strukturieren (äquivalent Given–When–Then): Zustand aufsetzen, ein Verhalten ausüben, das beobachtbare Ergebnis prüfen.
- **MUSS [MUST]** jedem Test einen **absichtsoffenbarenden Namen** geben, der das Verhalten und das erwartete Ergebnis nennt, nicht die getestete Methode.
- **MUSS [MUST]** Tests **unabhängig** halten — keine Reihenfolgeabhängigkeit, kein geteilter veränderlicher Zustand — gemäß §„Determinismus und Flakiness".
- **SOLLTE [SHOULD]** auf **beobachtbares Verhalten** prüfen statt auf Implementierungsdetail, damit ein Refactoring, das Verhalten bewahrt, den Test nicht bricht (am stärksten auf höheren Stufen, gegen Isolation auf niedrigeren Stufen abgewogen).

### Werkzeug-Agnostik und abgeleitete Artefakte

- **MUSS [MUST]** dieses Fundament und jede Stufen-Spec in ihren bindenden Anforderungen **werkzeug-agnostisch** halten; Werkzeugnamen (pytest / JUnit / Vitest bei Unit; Testcontainers bei Integration; Pact bei Contract; Playwright / Selenium / Cypress bei E2E; pitest / mutmut / Stryker für Mutation; k6 / Gatling / Locust für Performance; axe für A11y) erscheinen nur als illustrative Beispiele.
- **MUSS [MUST]** die Operationalisierung als **Rollen-Triade je Stufe** planen — *entwickeln* (Tests für die Stufe scaffolden/verfassen), *ausführen* (laufen lassen und Ergebnisse sammeln), *analysieren* (Ergebnisse / Suite-Qualität reviewen) — realisiert durch Skills und Agents, die unter `spec/claude/` verfasst werden. Die bestehenden E2E-Artefakte (`e2e-test-generator`, `e2e-test-reviewer`, `e2e-result-reviewer`, `test-pyramid-check`) sind die **Vorlage** für diese Triade auf der E2E-Stufe; abgeleitete Stufen folgen derselben Entwickeln/Ausführen/Analysieren-Form.
- **MUSS [MUST]** bei Erstellung eines abgeleiteten Skills oder Agents deklarieren, welche funktionale Stufe (oder Querschnitts-Dimension) und welche Triaden-Rolle er einnimmt, damit die Portfolio-Karte lücken- und überschneidungsfrei bleibt.
- **MUSS [MUST]** das **Stufen-Vollständigkeits**-Audit des Skills `test-pyramid-check` an **dieses Fundament** binden: er auditiert je Feature, welche der geschlossenen funktionalen Stufen vorhanden sind, welche fehlen und welche mit Begründung `n/a` sind, gegen die hier definierte Taxonomie und die Regel der niedrigsten-Stufe-die-Vertrauen-gibt. Sein **E2E-Disziplin**-Audit bleibt an `spec/project/e2e-test-automation/` [R1] gebunden, das die Form dieser Stufe besitzt. Der Skill hat damit zwei bindende Ziele, eines je Achse, und keine der beiden Specs wiederholt die Hälfte der anderen.

## Akzeptanzkriterien

- [ ] Die Spec definiert die Testpyramide als Anker-Modell und dokumentiert die Varianten Trophy, Honeycomb, Ice-Cream-Cone und Diamond mit ihrer Architektur-Eignung, je auf eine Primärquelle zitiert
- [ ] Die Spec nennt die Regel der niedrigsten-Stufe-die-Vertrauen-gibt und verbietet ausdrücklich, ein festes stufenübergreifendes Verhältnis als Anforderung zu kodieren
- [ ] Die funktionale Stufen-Taxonomie ist eine geschlossene, geordnete Liste von genau sechs Stufen (Static Analysis, Unit, Component, Integration, Contract, End-to-End), je mit Ein-Zeilen-Umfang und einer besitzenden oder zu erstellenden Spec
- [ ] Die invariante Stufen-Form zählt jedes Feld auf, das eine abgeleitete Stufen-Spec füllen muss (Zweck/Grenze, Isolation/Doubles, Geschwindigkeit/Determinismus, Platzierung, Traceability, Anti-Patterns, optionales Referenzprofil)
- [ ] Die fünf Meszaros-Test-Double-Kategorien sind mit der Unterscheidung Zustands- vs. Verhaltensverifikation definiert
- [ ] Querschnitts-Dimensionen (Performance, A11y, Security SAST/DAST, Mutation, Visual Regression, Exploratory) sind als orthogonale Lagen definiert, die die Stufen benennen, an die sie sich anheften, nie als Pyramidenebene
- [ ] Determinismus ist gefordert, Flakiness ist als Defekt mit Quarantäneregel definiert und feste `sleep`-Synchronisation ist verboten
- [ ] Coverage ist als Leitlinie-nicht-Ziel mit dem Goodhart-Vorbehalt gebunden, und Mutationsscore ist als stärkeres Suite-Qualitätssignal benannt
- [ ] Das CI-Gating-Modell weist schnelle Stufen dem PR-Gating und langsame/breite Stufen geplanten Läufen zu und delegiert die Gate-*Erzwingung* an `spec/project/pull-request-workflow/`
- [ ] Die Traceability-Kette Anforderung→TC-ID→Test ist gefordert und konsumiert die Ausgabe von `test-case-derivation`, statt sie neu abzuleiten
- [ ] Der Verhältnis-Abschnitt mappt die drei bestehenden Test-Specs als Stufen-/Funktions-Realisierungen, ohne sie zu wiederholen, und hält die Migration der e2e-„Pyramide"-Subsektion in dieses Fundament als Folgepunkt fest
- [ ] Der Abschnitt zu abgeleiteten Artefakten deklariert die Entwickeln/Ausführen/Analysieren-Triade, benennt die bestehenden E2E-Artefakte als ihre Vorlage und bindet die Stufen-Vollständigkeits-Achse von `test-pyramid-check` an dieses Fundament, während seine E2E-Disziplin-Achse an `e2e-test-automation` gebunden bleibt
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl und Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/e2e-test-automation/` — End-to-End Test Automation Standard (die E2E-Stufen-Realisierung; Quelle der migrierten Pyramiden-Subsektion)
- [R2] `spec/project/test-case-derivation/` — Test-Case Derivation from Requirements (erzeugt die TC-IDs, die die Traceability-Kette dieses Fundaments konsumiert)
- [R3] `spec/project/quality-gate/` — Quality Gate (führt die schnellen Stufen aus; besitzt die Gate-Ausgabeform)
- [R4] `spec/project/pull-request-workflow/` — besitzt die Erzwingung erforderlicher Status-Checks, die das CI-Gating-Modell dieser Spec speist
- [R5] Martin Fowler, *TestPyramid* — <https://martinfowler.com/bliki/TestPyramid.html>
- [R6] Martin Fowler, *UnitTest* (solitär vs. gesellig; team-bestimmte Einheit) — <https://martinfowler.com/bliki/UnitTest.html>
- [R7] Ham Vocke, *The Practical Test Pyramid* — <https://martinfowler.com/articles/practical-test-pyramid.html>
- [R8] Martin Fowler, *On the Diverse And Fantastical Shapes of Testing* — <https://martinfowler.com/articles/2021-test-shapes.html>
- [R9] Kent C. Dodds, *The Testing Trophy and Testing Classifications* — <https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications>
- [R10] Spotify Engineering, *Testing of Microservices* (Testing Honeycomb) — <https://engineering.atspotify.com/2018/01/testing-of-microservices>
- [R11] Martin Fowler, *Mocks Aren't Stubs* (Meszaros-Test-Double-Taxonomie) — <https://martinfowler.com/articles/mocksArentStubs.html>
- [R12] Martin Fowler, *IntegrationTest* / *ContractTest* — <https://martinfowler.com/bliki/IntegrationTest.html> , <https://martinfowler.com/bliki/ContractTest.html>
- [R13] Pact — Consumer-Driven Contract Testing — <https://docs.pact.io/>
- [R14] Thoughtworks Technology Radar, *Broad integration tests* (Hold) — <https://www.thoughtworks.com/radar/techniques/broad-integration-tests>
- [R15] Google Testing Blog, *Flaky Tests at Google and How We Mitigate Them* — <https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html>
- [R16] Martin Fowler, *TestCoverage* — <https://martinfowler.com/bliki/TestCoverage.html>
- [R17] Google Testing Blog, *Code Coverage Best Practices* — <https://testing.googleblog.com/2020/08/code-coverage-best-practices.html>
- [R18] pitest — Mutationstest — <https://pitest.org/>
- [R19] SAST vs. DAST (Platzierung von Security-Tests) — <https://blog.jetbrains.com/teamcity/2025/05/sast-vs-dast/>

## Offene Fragen

- Sollten die funktionalen Stufen-Specs eine-pro-Stufe (sechs Specs) oder gruppiert erstellt werden (z. B. eine einzelne „Fast Tiers"-Spec für Static/Unit/Component und eine „Boundary Tiers"-Spec für Integration/Contract)? Die Granularität beeinflusst, wie viele abgeleitete Skills/Agents die Triade erzeugt.
- ~~Wenn die eingebettete Subsektion §„Test-tier completeness (the pyramid)" der e2e-Spec auf eine Referenz zu diesem Fundament reduziert wird, richtet sich `test-pyramid-check` auf diese Spec neu aus oder bleibt nur für die E2E-Stufen-Disziplin auf die e2e-Spec gerichtet?~~ **Entschieden (2026-07-24): beides, nach Achse getrennt.** Die Stufen-Vollständigkeit richtet sich hierher neu aus; die E2E-Disziplin bleibt auf `e2e-test-automation` [R1]. Genau das tut der ausgelieferte Skill bereits—sein Frontmatter und sein Lese-Schritt benennen beide Specs, und seine Konfliktregel benennt jede als Autorität für ihre eigene Hälfte—die Entscheidung ratifiziert also die reale Verdrahtung, statt ein Ziel zu erfinden. Beide Ein-Ziel-Lesarten brechen etwas: allein auf die e2e-Spec zu zeigen ließe das Stufen-Audit eines Projekts ohne UI von einer E2E-Spec regieren, allein hierher zu zeigen verwaiste die E2E-Disziplin-Prüfungen, die das Fundament bewusst nicht besitzt. Das Gebot in §„Werkzeug-Agnostik und abgeleitete Artefakte" oben und die entsprechende Anforderung in der e2e-Spec sind passend migriert, sodass jede der beiden Achsen des Skills genau einen Besitzer hat.
- Verdienen die Querschnitts-Dimensionen (Performance, A11y, Security, Mutation, Visual Regression) je eine eigene Spec oder eine einzelne „Non-functional Testing"-Spec, die sie aufzählt? Mehrere haben bereits teilweise ein Zuhause (Security überschneidet sich mit `dependency-audit`; A11y mit `webview-ui-optimization`).
- Sollte ein projektspezifischer „Test-Strategie-Eintrag" (die gewählte Form + begründete Stufen-Auslassungen) ein erforderliches Artefakt sein (z. B. unter `project/`) oder eine optionale Notiz?
