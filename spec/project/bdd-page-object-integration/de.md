# BDD und Page-Object-Integration

Status: draft
Portfolio-Scope: portfolio

## Kontext

Auf der End-to-End-Stufe existieren ein BDD-Szenario und ein Page Object beide, und der Wert der Kombination hängt vollständig davon ab, *wie sie miteinander verdrahtet werden*. Gut gemacht liest sich ein Gherkin-Szenario als Verhalten in der Sprache der Domäne, eine dünne Step-Definition übersetzt jede Zeile in einen Aufruf auf einem Page Object, und das Page Object kapselt die Benutzeroberfläche, sodass dasselbe Page Object jedem Szenario dient, das diese Ansicht berührt. Schlecht gemacht lernt das Page Object Gherkin kennen, die Step-Definition greift in den DOM, Assertions sickern über Schichten, und jedes Szenario züchtet sein eigenes Page Object, das kein anderer Test wiederverwenden kann. Der Unterschied sind nicht die beiden Patterns isoliert, die anderswo bereits spezifiziert sind: Es ist der **Integrations-Vertrag** zwischen ihnen, und speziell die **Entkopplung**, die die Page-Object-Ebene wiederverwendbar hält.

Diese Spec besitzt diesen Vertrag. Ihre lasttragende These ist eine strikte Abhängigkeitsrichtung: **Die Page-Object-Ebene MUSS null Abhängigkeit zur BDD-/Step-Ebene haben.** Ein Page Object weiß nichts von Gherkin, vom Step-Definition-Framework, von Szenarien, Tags oder dem Test-Runner, und es hält keine Assertions. Es ist eine schlichte, wiederverwendbare Benutzeroberflächen-Kapselungs-Bibliothek, die eine BDD-Step-Definition genau so konsumiert wie ein Nicht-BDD-Test sie konsumiert. Die Step-Definition ist die *einzige* Ebene, die beide Welten kennt; sie hängt von Page Objects ab, Page Objects hängen nie von ihr ab. Diese Einweg-Abhängigkeit macht ein Page Object über BDD-Steps, plain E2E-Tests und jeden anderen Client wiederverwendbar, was der ganze Sinn der Investition in das Pattern ist.

Der normative Kern ist tool-neutral: Er beschränkt *Abhängigkeitsrichtung, Entkopplung und die Verdrahtungs-Naht* gegen jede WebDriver-plus-BDD-Kombination. Weil der primäre Fall des Operators Selenium ist, macht ein normatives **Selenium + `pytest-bdd`** Referenzprofil den Vertrag konkret, wie `spec/project/e2e-test-automation/` seinen konkreten Stack zu einem austauschbaren Profil herabstuft.

**Beziehung zu den anderen Specs.** Nach Verantwortung abgegrenzt:

- `spec/project/e2e-test-automation/` [R1] besitzt das Page Object Model *selbst*: Encapsulation, die gemeinsame Basis, benannte Methoden, bedingungsbasiertes Warten, Locator-Strategie und wo Assertions leben. Diese Spec **MUSS NICHT [MUST NOT]** diese Internas wiederholen; sie referenziert sie und ergänzt die Integrations-/Entkopplungs-Ebene darüber.
- `spec/project/behavior-driven-development/` [R2] besitzt die Step-Definition-*Prinzipien* (dünne Steps, die delegieren, keine Assertions in Gherkin) und die Szenariosprache. Diese Spec referenziert jene und spezifiziert die konkrete Verdrahtung und die Abhängigkeitsrichtung, auf der die beiden Ebenen sich treffen.
- `spec/frontend/testability-identifiers/` [R3] besitzt den stabilen Selektor-Vertrag, gegen den ein Page Object auflöst. Diese Spec benennt nie einen Selektor.
- `spec/project/test-pyramid-foundation/` [R4] besitzt das Stufenmodell; diese Spec regelt nur die Integration auf der E2E-Stufe.

Leser: Entwickler, die BDD-Szenarien an Page Objects verdrahten oder diese Verdrahtung prüfen; Agent-/Skill-Autoren, die eine BDD-Szenario- oder Page-Object-Capability bauen; Reviewer, die prüfen, ob ein Page Object wiederverwendbar und frei von BDD-Kopplung blieb.

## Ziele

- Den BDD-zu-Page-Object-Integrations-Vertrag einmal formulieren, tool-neutral, als bindenden Kern, den jedes konsumierende Projekt erfüllt
- Die **Einweg-Abhängigkeit** (Steps hängen von Page Objects ab, nie umgekehrt) zur lasttragenden Regel machen, damit die Page-Object-Ebene wiederverwendbar bleibt
- Die Page-Object-Ebene unverändert aus einem Nicht-BDD-Test nutzbar halten und so die Entkopplung beweisen statt behaupten
- Die Verdrahtungs-Naht konkret spezifizieren: wie Page Objects die Step-Ebene erreichen, wo Szenario-Zustand lebt und wo Assertions sitzen
- Ein normatives Selenium + `pytest-bdd` Referenzprofil liefern, das die Entkopplung mit lauffähigem Code demonstriert
- Die Kopplungs-Anti-Patterns benennen, damit ein Reviewer sie ablehnen kann
- Die Page-Object- und Step-Definition-Eigentümer referenzieren statt wiederholen

## Nicht-Ziele

- Die Internas des Page Object Models selbst spezifizieren (Encapsulation, gemeinsame Basis, benannte Methoden, bedingungsbasiertes Warten, Locator-Strategie, wo Assertions leben): besitzt `spec/project/e2e-test-automation/` [R1]; diese Spec konsumiert diese Disziplin und regelt nur die Integration mit BDD
- Die Szenariosprache oder die allgemeinen Step-Definition-Prinzipien spezifizieren (dünne Steps, keine Assertions in Gherkin, deklarative Szenarien): besitzt `spec/project/behavior-driven-development/` [R2]
- Die stabilen Selektoren bereitstellen, gegen die ein Page Object auflöst: besitzt `spec/frontend/testability-identifiers/` [R3]
- Testfälle oder Szenarien aus Anforderungen ableiten: besitzt `spec/project/test-case-derivation/` und `spec/project/behavior-driven-development/` [R2]
- Eine bestimmte Browser-Automatisierungs-Bibliothek oder ein BDD-Framework vorschreiben: Der Kern ist tool-neutral; Selenium und `pytest-bdd` sind das illustrative Referenzprofil
- Die Stufen-Taxonomie oder Coverage-Governance festlegen: besitzt `spec/project/test-pyramid-foundation/` [R4]

## Anforderungen

### Abhängigkeitsrichtung und Schichtung

- Der Stack **MUSS [MUST]** in genau dieser Reihenfolge geschichtet sein, wobei jede Schicht nur von der darunterliegenden abhängt: Gherkin-Szenario → Step-Definition → Page Object → Browser-Automatisierungs-Driver. Abhängigkeiten **MUSS [MUST]** nur nach unten zeigen.
- Die Abhängigkeit zwischen Step-Ebene und Page-Object-Ebene **MUSS [MUST]** einseitig sein: Eine Step-Definition hängt von Page Objects ab; ein Page Object **MUSS NICHT [MUST NOT]** von einer Step-Definition, einem Step-Framework-Symbol oder einem Gherkin-Konstrukt abhängen, es importieren oder referenzieren.
- Jede Schicht **MUSS [MUST]** eine einzige Verantwortung haben: Das Szenario formuliert Verhalten, die Step-Definition übersetzt und orchestriert, das Page Object kapselt die Benutzeroberfläche, der Driver führt die rohe Automatisierung aus. Eine Verantwortung **MUSS NICHT [MUST NOT]** eine Schicht nach oben oder unten wandern (keine UI-Mechanik in einem Step, kein Verhaltens-Wording in einem Page Object).

### Page-Object-Unabhängigkeit von BDD (der Wiederverwendungs-Vertrag)

- Ein Page Object **MUSS [MUST]** frei von jeder BDD- und Test-Framework-Kopplung sein: Es **MUSS NICHT [MUST NOT]** das BDD-Framework importieren oder referenzieren (zum Beispiel `pytest_bdd`- / Cucumber-Symbole), **MUSS NICHT [MUST NOT]** Step-Dekoratoren tragen (`@given` / `@when` / `@then`) und **MUSS NICHT [MUST NOT]** von Szenarien, Tags, Feature-Dateien oder dem Test-Runner wissen.
- Ein Page Object **MUSS NICHT [MUST NOT]** Test-Assertions enthalten; es legt Seitenzustand über benannte Methoden offen und gibt ihn zurück, und die Assertion trifft der Aufrufer (gemäß `spec/project/e2e-test-automation/` [R1]). Eine Assertion in einem Page Object koppelt es an die Erwartungen eines Tests und zerstört seine Wiederverwendung.
- Ein Page Object **MUSS [MUST]** unverändert von einem anderen Client als dem BDD-Step nutzbar sein (ein plain E2E-Test, ein Smoke-Check, ein Skript). Diese Wiederverwendbarkeit **MUSS [MUST]** demonstrierbar sein, nicht angenommen: Ein Projekt **SOLLTE [SHOULD]** mindestens ein Page Object aus einem BDD-Step und einem Nicht-BDD-Test üben, um zu beweisen, dass die Entkopplung hält.
- Die Page-Object-Ebene als Ganzes **MUSS [MUST]** eine eigenständige, wiederverwendbare Benutzeroberflächen-Kapselungs-Bibliothek bilden, unabhängig vom Grund, aus dem ein bestimmter Client sie treibt.

### Der Step-als-Klebstoff-Vertrag

- Die Step-Definition **MUSS [MUST]** die einzige Ebene sein, die beide Welten kennt: Sie bindet einen Gherkin-Step und übersetzt ihn in einen oder wenige Aufrufe auf Page Objects. Sie **MUSS [MUST]** keine Benutzeroberflächen-Mechanik halten (keine rohen Driver-Aufrufe, keine Selektoren, keine Waits, keine Screenshots) und keine eigene fachliche Logik.
- Eine Step-Definition **MUSS NICHT [MUST NOT]** an der Page-Object-Ebene vorbei in den Driver oder den DOM greifen; jede Benutzeroberflächen-Interaktion **MUSS [MUST]** über ein Page Object gehen.
- Die Assertion für einen `Then`-Step **MUSS [MUST]** in der Bindung dieses Steps leben und vom Page Object zurückgegebenen Zustand gegen das erwartete Ergebnis des Szenarios vergleichen; die Assertion **MUSS NICHT [MUST NOT]** im Page Object leben und **MUSS NICHT [MUST NOT]** im Gherkin-Text leben.
- Eine Step-Definition **SOLLTE [SHOULD]** in dem, was sie ausdrückt, deklarativ bleiben, sodass das Lesen der Step-Bindungen neben der Feature-Datei weiterhin Verhalten kommuniziert statt Automatisierungs-Mechanik.

### Verdrahtung und Dependency-Bereitstellung

- Page Objects **MUSS [MUST]** Step-Definitionen per **Dependency Injection** bereitgestellt werden, nicht mit inline Driver-Mechanik im Step-Körper konstruiert: Die Referenz-Mechanismen sind Test-Fixtures (`pytest`-Fixtures für `pytest-bdd`) oder ein DI-Container (zum Beispiel PicoContainer für Cucumber-JVM). Ein Step erhält ein fertiges Page Object; er verdrahtet den Driver nicht selbst.
- Die Browser-Automatisierungs-Session/der Driver **MUSS [MUST]** von einem einzigen Provider besessen werden (eine Fixture oder Container-Bindung) und über diesen Provider in Page Objects geteilt werden, sodass ein Szenario eine Session treibt und Page Objects nie ihren eigenen Driver instanziieren.
- Page-Object-Konstruktion **MUSS NICHT [MUST NOT]** pro Step dupliziert werden: Ein Page Object wird einmal definiert und überall injiziert, wo es gebraucht wird; ein Projekt **MUSS NICHT [MUST NOT]** in jedem Step maßgeschneiderte Page-Object-Mechanik neu instanziieren.

### Zustand und Daten an der Naht

- Zustand, der über die Steps eines Szenarios geteilt wird (die getestete Entität, eine in einem `When` erfasste ID, ein in einem `Then` zu prüfender Wert), **MUSS [MUST]** in einem expliziten **szenario-scoped Context**-Objekt gehalten werden (eine `pytest-bdd`-Fixture, eine Cucumber World), nie in modulweiten Globals oder Klassenattributen auf einem Page Object.
- Ein Page Object **MUSS NICHT [MUST NOT]** szenario-spezifischen Zustand über Szenarien hinweg halten; es legt aktuellen Seitenzustand auf Anfrage offen und bleibt zustandslos in Bezug auf den Testablauf.
- Daten, die ein Step an ein Page Object übergibt (ein Name, ein Betrag, eine Zeile aus einer `Examples`-Tabelle), **MUSS [MUST]** als Methodenargumente fließen; ein Page Object **MUSS NICHT [MUST NOT]** den Szenario-Context, Tags oder Beispieldaten direkt lesen, was es zurück an BDD koppeln würde.

### Komposition

- Ein einzelner Step **KANN [MAY]** mehrere Page Objects orchestrieren (eine Seite öffnen, handeln, auf einer anderen prüfen); die Orchestrierung lebt im Step, nicht über die Page Objects verstreut.
- Ein Page Object **KANN [MAY]** ein anderes Page Object zurückgeben, um Navigation zu modellieren (eine navigierende Methode gibt das Page Object der Zielseite zurück); solche Komposition **MUSS [MUST]** innerhalb der Page-Object-Ebene bleiben und **MUSS NICHT [MUST NOT]** einen Step oder ein Szenario referenzieren.
- Ein Projekt **MUSS NICHT [MUST NOT]** ein Page Object pro Step oder pro Szenario erzeugen; Page Objects sind an Benutzeroberflächen-Flächen gebunden (eine Seite, eine Komponente, ein Dialog), und Wiederverwendung über Steps ist das erwartete Ergebnis. Ein Page Object pro Step ist ein Kopplungs-Geruch, der den Wiederverwendungs-Vertrag zunichtemacht.

### Wiederverwendung über BDD hinaus

- Dasselbe Page Object **MUSS [MUST]** sowohl einen BDD-Step als auch einen Nicht-BDD-Test treiben, ohne Änderung am Page Object. Wo ein Projekt das Referenzprofil ausliefert, **MUSS [MUST]** es ein Beispiel enthalten, das diese Doppelnutzung demonstriert (siehe Referenzprofil und `templates/`).
- Querschnitts-Page-Object-Belange (Navigation, Warten, Basis-Helfer) **MUSS [MUST]** in der Page-Object-Basis leben, die `spec/project/e2e-test-automation/` [R1] besitzt, sodass jeder Client, BDD oder nicht, dasselbe Verhalten erbt; diese Spec **MUSS NICHT [MUST NOT]** die Inhalte jener Basis wiederholen.

### Anti-Patterns

- Das Folgende **MUSS [MUST]** als Defekt behandelt und im Review abgelehnt werden:
  - **Ein Page Object, das das BDD-Framework importiert** oder `@given` / `@when` / `@then`-Dekoratoren trägt: Die Schichten sind verschmolzen und die Wiederverwendung ist weg.
  - **Assertions in einem Page Object**: Es kodiert nun die Erwartungen eines Tests und kann nicht von einem Client mit anderen Erwartungen wiederverwendet werden.
  - **Ein Step, der den Driver oder einen Selektor direkt aufruft** und das Page Object umgeht: Der Step hat Page-Object-Verantwortung absorbiert.
  - **Fachliche Logik in einem Page Object**: Verhalten ist aus dem Step/Szenario nach unten geleakt.
  - **Ein Page Object, das von Szenarien, Tags oder dem Szenario-Context weiß**: eine Aufwärts-Abhängigkeit, die die Schichtung invertiert.
  - **Ein Page Object pro Step oder pro Szenario**: maßgeschneiderte, nicht wiederverwendbare Objekte, die den Zweck des Patterns zunichtemachen.
  - **Szenario-Zustand über Globals oder auf dem Page Object geteilt** statt eines expliziten szenario-scoped Context.
  - **Ein Gott-Page-Object**, das unzusammenhängende Flächen umspannt, sodass kein Client eine fokussierte Scheibe wiederverwenden kann.

## Referenzprofil (illustrativ, nicht normativ)

Dieses Profil macht den tool-neutralen Kern mit **Selenium** und **`pytest-bdd`** konkret und komponiert mit dem Selenium + pytest Referenzprofil von `spec/project/e2e-test-automation/` [R1] und dem `pytest-bdd`-Profil von `spec/project/behavior-driven-development/` [R2]. Ein Projekt auf einem anderen Stack (Playwright, Cypress; Cucumber-JVM, Cucumber.js) erfüllt den Kern ohne es. Das mitgelieferte `templates/`-Verzeichnis trägt ein ausgearbeitetes Beispiel.

- **Page Objects** sind schlichte Klassen, die einen Selenium-`WebDriver` (oder einen Wrapper) über ihren Konstruktor erhalten, benannte Methoden offenlegen und nichts aus `pytest_bdd` importieren. Sie lösen `spec/frontend/testability-identifiers/` [R3]-Selektoren über die Basis auf, die `spec/project/e2e-test-automation/` [R1] besitzt.
- **Step-Definitionen** leben in einem `pytest-bdd`-Modul; eine `pytest`-Fixture baut den Driver und jedes Page Object und injiziert sie, plus eine szenario-scoped `context`-Fixture hält geteilten Zustand. Jeder Step ruft Page-Object-Methoden; jeder `Then`-Step prüft zurückgegebenen Zustand.
- Das mitgelieferte `templates/` trägt: ein BDD-unabhängiges Page Object (`pages/`), eine `pytest-bdd`-Step-Datei, die es verdrahtet, und einen **plain `pytest`-E2E-Test, der dasselbe Page Object unverändert treibt**, was die Entkopplung beweist.

## Akzeptanzkriterien

- [ ] Die Einweg-Abhängigkeit (Steps → Page Objects, nie umgekehrt) ist als lasttragendes MUSS formuliert
- [ ] Die Page-Object-Unabhängigkeit von BDD ist spezifiziert: keine BDD-/Framework-Importe, keine Step-Dekoratoren, kein Szenario-/Tag-/Runner-Wissen, keine Assertions
- [ ] Der Step-als-Klebstoff-Vertrag ist spezifiziert: einzige Ebene, die beide Welten kennt, keine UI-Mechanik, keine fachliche Logik, `Then`-Assertion in der Step-Bindung
- [ ] Die Verdrahtung ist spezifiziert: Dependency Injection per Fixtures/DI-Container, ein einziger Driver-Provider, keine Page-Object-Mechanik pro Step
- [ ] Szenario-Zustand ist als in einem expliziten szenario-scoped Context lebend spezifiziert, nie Globals oder das Page Object
- [ ] Komposition und Wiederverwendung-über-BDD-hinaus sind spezifiziert, inklusive der demonstrierbaren Doppelnutzung (BDD-Step + Nicht-BDD-Test) desselben Page Objects
- [ ] Die Nicht-Ziele verlinken alle vier Nachbar-Specs (`e2e-test-automation`, `behavior-driven-development`, `testability-identifiers`, `test-pyramid-foundation`) nach Verantwortung, ohne eine davon zu wiederholen
- [ ] Die Anti-Pattern-Liste benennt Framework-Importe in einem Page Object, Assertions in einem Page Object, Driver-/Selektor-Aufrufe in einem Step, fachliche Logik in einem Page Object, Szenario-Wissen in einem Page Object, ein Objekt pro Step, globalen Zustand und Gott-Page-Objects
- [ ] Ein Selenium + `pytest-bdd` Referenzprofil liefert ein `templates/`-Beispiel, das die Entkopplung beweist (dasselbe Page Object aus einem BDD-Step und einem plain Test)
- [ ] EN- und DE-Fassung sind strukturell identisch (gleiche Überschriften, Anforderungsanzahl, Akzeptanzkriterien-Anzahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/e2e-test-automation/`: besitzt die Page-Object-Model-Internas (Encapsulation, Basis, benannte Methoden, Waits, Locators, Assertions-in-Tests), die diese Spec konsumiert
- [R2] `spec/project/behavior-driven-development/`: besitzt die Step-Definition-Prinzipien und die Szenariosprache, die diese Spec an Page Objects verdrahtet
- [R3] `spec/frontend/testability-identifiers/`: besitzt den stabilen Selektor-Vertrag, gegen den ein Page Object auflöst
- [R4] `spec/project/test-pyramid-foundation/`: besitzt das Stufenmodell; diese Spec regelt nur die Integration auf der E2E-Stufe
- [R5] Martin Fowler, *PageObject* (das Page-Object-Kapselungs-Pattern): <https://martinfowler.com/bliki/PageObject.html>
- [R6] Selenium, *Page object models* (Page Objects als wiederverwendbare UI-Abstraktion): <https://www.selenium.dev/documentation/test_practices/encouraged/page_object_models/>
- [R7] `pytest-bdd`-Dokumentation (Steps als Fixtures; Dependency Injection): <https://pytest-bdd.readthedocs.io/>
- [R8] Cucumber, *Dependency Injection* (World / container-bereitgestellter Zustand und Page Objects): <https://cucumber.io/docs/cucumber/state/>

## Offene Fragen

- Sollte das Referenzprofil eine zweite Verdrahtungs-Variante (Cucumber-JVM + PicoContainer) neben `pytest-bdd` liefern, oder hält ein ausgearbeitetes Beispiel das Profil illustrativ?
- Sollte die demonstrierbare Doppelnutzung eines Page Objects (aus einem BDD-Step und einem Nicht-BDD-Test) ein hartes Review-Gate sein oder ein starkes SOLLTE?
- Wo ein Projekt gar keine Nicht-BDD-E2E-Tests hat, ist der Wiederverwendungs-Vertrag dann noch durch ein dediziertes Wiederverwendungs-Beispiel verifizierbar, oder lockert er sich zu einer Design-Review-Prüfung?
