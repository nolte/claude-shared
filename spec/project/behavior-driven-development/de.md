# Behavior-Driven Development

Status: draft
Portfolio-Scope: portfolio

## Kontext

Behavior-Driven Development (BDD) ist die Praxis, das Verhalten eines Systems durch konkrete, geschäftslesbare Beispiele zu spezifizieren — kollaborativ entdeckt und so geschrieben, dass dieselben Beispiele zugleich als Akzeptanzkriterien, als automatisierter Test und als lebende Dokumentation dienen. Der wiederverwendbare, portfolioweite Teil ist kein Framework und kein Dateiformat: Es ist die Disziplin, ein geteiltes Verständnis davon, *was das System tun soll*, in Beispiele zu überführen, die in der Sprache der Domäne lesbar sind, je genau ein Verhalten beschreiben, deklarativ über das *Was* statt das *Wie* bleiben und auf die Anforderung zurückverweisen, die sie verifizieren. Diese Disziplin ist tool-unabhängig. Der Wegwerf-Teil ist der Klebstoff: welche Bibliothek die Beispiele parst, welches Verzeichnis sie hält, welche Step-Bindungs-Syntax ein bestimmter Stack verwendet.

Diese Spec besitzt diese wiederverwendbare Disziplin. Sie ist die normative Behandlung, die BDD in diesem Korpus erhält: kollaborative Beispiel-Ermittlung, die Given-When-Then-Szenariosprache, deklaratives Szenario-Design, Ubiquitous Language, lebende Dokumentation und Step-Definition-Prinzipien, plus den Ableitungspfad von einem abstrakten **Testcase-Dokument** zu **ausführbaren BDD-Szenarien**. `spec/project/test-cycle-case-determination/` benennt Example Mapping und Specification by Example / BDD (Given-When-Then) bereits als **SOLLTE**, um Fälle vor dem Coden zu entdecken, schreibt aber kein BDD-Framework vor; diese Spec verwandelt jenen Verweis in einen vollständigen, weiterhin tool-neutralen Standard. Der normative Kern ist **stufen-neutral**: Ein BDD-Szenario kann einen Unit-, Component-, Integration- oder End-to-End-Test treiben. End-to-End (E2E) ist der primäre Anwendungsfall und erhält eine eigene Anforderungsgruppe, weil ein geschäftslesbares Szenario dort am meisten einbringt, aber der Kern nimmt nie eine Stufe an.

Weil der Korpus mehrsprachig ist, formuliert diese Spec die Disziplin als bindenden Kern und pinnt ein konkretes, illustratives **Referenzprofil** (Gherkin plus die Cucumber-Familie) als nicht-normativen Anhang, damit eine Autorin die Disziplin konkret sieht, ohne dass das Profil zur Anforderung wird. Das spiegelt, wie `spec/project/e2e-test-automation/` seinen Selenium-Stack zu einem austauschbaren Referenzprofil herabstuft.

**Beziehung zu den anderen Specs.** Nach Verantwortung abgegrenzt:

- `spec/project/test-cycle-case-determination/` [R1] besitzt, *wann* im wiederkehrenden Testzyklus Beispiele entdeckt werden und welche Design-Techniken gelten. Diese Spec besitzt, *wie* BDD diese Ermittlung strukturiert und als Szenarien kodiert; sie wiederholt den Zyklus nicht.
- `spec/project/test-case-derivation/` [R2] besitzt die Ableitung abstrakter, framework-agnostischer Testfälle aus einem Anforderungsdokument. Diese Spec **konsumiert** ein solches Testcase-Dokument als Eingabe und leitet es nicht neu ab.
- `spec/project/e2e-test-automation/` [R3] besitzt die E2E-Ausführungsmechanik: Page Objects, bedingungsbasierte Waits, Screenshots, Protokolle und Anforderungs-Traceability. Diese Spec besitzt die Szenario-/Spezifikationsebene *über* dieser Mechanik; ein Step delegiert hinab, statt sie zu wiederholen.
- `spec/frontend/testability-identifiers/` [R4] besitzt den stabilen Selektor-Vertrag, gegen den ein Step letztlich auflöst. Diese Spec spezifiziert nie Selektoren; sie stützt sich über die Ausführungsebene auf diesen Provider-seitigen Vertrag.

Leser: Spec-Autoren, die die Schwester-Test-Specs schreiben; Skill- und Agent-Autoren, die eine BDD-Capability bauen, die ein Testcase-Dokument in ausführbare Szenarien verwandelt; Entwickler, Tester und Business-Analysten, die Szenarien schreiben oder prüfen; Reviewer, die prüfen, ob ein Szenario-Set deklarativ, ein-Verhalten-pro-Szenario, traceable und als Dokumentation lesbar ist.

## Ziele

- Die tool-neutrale BDD-Disziplin einmal formulieren, als bindenden Kern, den jedes konsumierende Projekt unabhängig von Framework oder Stufe erfüllt
- Den Kern auf jedem BDD-Stack ausführbar halten, indem Gherkin und die Cucumber-Familie zu einem illustrativen, austauschbaren Referenzprofil statt zu einer Anforderung herabgestuft werden
- Kollaborative Ermittlung (Example Mapping, Three Amigos) zur Eingangstür machen, damit Szenarien ein geteiltes Verständnis kodieren statt der Vermutung einer einzelnen Autorin
- Einen normativen, geordneten Workflow definieren, der ein abstraktes Testcase-Dokument in ausführbare BDD-Szenarien mit durchgängiger Traceability verwandelt
- Szenarien als lebende Dokumentation in der Ubiquitous Language der Domäne behandeln, nicht als getarnte Testskripte
- BDD-auf-E2E eigene Anforderungen geben, während der Kern stufen-neutral bleibt, und die Ausführungsmechanik an `spec/project/e2e-test-automation/` delegieren
- Die wiederkehrenden BDD-Anti-Patterns benennen, damit ein konsumierendes Skill und seine Reviewer sie ablehnen können

## Nicht-Ziele

- Entscheiden, *wann* im Zyklus Beispiele entdeckt werden oder welche Test-Design-Technik-Familien gelten: besitzt `spec/project/test-cycle-case-determination/` [R1], die diese Spec für den BDD-Fall operationalisiert statt wiederholt
- Die abstrakten, framework-agnostischen **Testfälle** aus einem Anforderungsdokument ableiten: besitzt `spec/project/test-case-derivation/` [R2]; diese Spec konsumiert solche Fälle (über ihre TC-IDs) als Eingabe und erzeugt sie nicht
- Die E2E-**Ausführungsmechanik**, auf der ein Szenario läuft (Page Objects, Waits, Screenshots, Protokoll, Driver-Klebstoff): besitzt `spec/project/e2e-test-automation/` [R3]; diese Spec regelt die Szenario-Ebene darüber
- Die stabilen **Selektoren** bereitstellen, gegen die ein Step auflöst: besitzt `spec/frontend/testability-identifiers/` [R4]; ein Szenario stützt sich auf diesen Vertrag und benennt nie einen Selektor
- Ein bestimmtes BDD-Framework, einen Parser oder eine Dateiendung vorschreiben: Der Kern ist tool-neutral; Gherkin und die Cucumber-Familie sind das illustrative Referenzprofil, keine Anforderung
- Die Stufen-Taxonomie oder Coverage-Governance festlegen: besitzt `spec/project/test-pyramid-foundation/` [R5]
- Spezifizieren, wie eine BDD-Step-Definition an Page Objects verdrahtet wird und von ihnen entkoppelt bleibt (der Integrations- und Wiederverwendbarkeits-Vertrag): besitzt `spec/project/bdd-page-object-integration/` [R13]; diese Spec setzt die Step-Definition-Prinzipien, jene Spec die konkrete Page-Object-Verdrahtung

## Anforderungen

### Tool-Neutralität und Stufen-Umfang

- Die bindenden Anforderungen dieser Spec **MUSS [MUST]** gegen Fähigkeiten formuliert werden, die jeder BDD-Ansatz bereitstellt (Beispiele entdecken, ein Verhalten als Vorbedingung / Aktion / erwartetes Ergebnis ausdrücken, diesen Ausdruck an ausführbare Steps binden, ihn als Test ausführen, der zugleich Dokumentation ist), und **MUSS NICHT [MUST NOT]** ein konkretes Framework, einen Parser, eine Sprache oder eine Dateiendung benennen.
- Der normative Kern **MUSS [MUST]** stufen-neutral bleiben: Ein BDD-Szenario **KANN [MAY]** einen Unit-, Component-, Integration- oder End-to-End-Test treiben, und diese Spec **MUSS NICHT [MUST NOT]** eine Stufe für den Kern annehmen. Die Stufenplatzierung bleibt Sache des Stufenmodells [R5] (niedrigste Stufe, die Vertrauen gibt).
- End-to-End **MUSS [MUST]** als primärer Anwendungsfall behandelt werden (siehe *BDD auf End-to-End-Tests*), aber ein konsumierendes Projekt **KANN [MAY]** die Disziplin auf jeder Stufe anwenden, ohne die E2E-spezifischen Anforderungen zu übernehmen.
- Alles, was das Referenzprofil liefert (Gherkin-Syntax, Feature-Datei-Layout, Step-Bindungs-Beispiele, die Cucumber-Familie), ist illustrativ und **KANN [MAY]** von einem Projekt auf einem anderen Stack vollständig ersetzt werden, sofern der bindende Kern weiter gilt.

### Kollaborative Ermittlung

- Ein konsumierendes Projekt **SOLLTE [SHOULD]** die Beispiele, die zu Szenarien werden, **kollaborativ vor dem Coden** entdecken, damit ein Szenario ein geteiltes Verständnis kodiert statt der nachträglichen Vermutung einer einzelnen Autorin [R6], [R7].
- Es **SOLLTE [SHOULD]** **Example Mapping** verwenden, um diese Ermittlung zu strukturieren: für eine Story ihre fachlichen **Rules**, ein konkretes **Example** je Rule und die offenen **Questions**, die das Gespräch aufwirft, kartieren, damit eine unterspezifizierte oder überdimensionierte Story vor dem Coden entlarvt wird [R7].
- Es **SOLLTE [SHOULD]** die Ermittlung als **Three-Amigos**-Gespräch über die drei Perspektiven (Business / Product, Entwicklung, Testing) führen, weil jede Perspektive Beispiele fängt, die die anderen verpassen [R6], [R8].
- Eine während der Ermittlung aufgeworfene offene Frage **MUSS [MUST]** festgehalten und aufgelöst werden, statt still als Annahme in ein Szenario kodiert zu werden; eine ungelöste Frage bedeutet, dass das Verhalten noch nicht verstanden ist.

### Szenariosprache

- Ein Verhalten **MUSS [MUST]** in der **Given-When-Then**-Struktur ausgedrückt werden: **Given** der Ausgangskontext, **When** das auslösende Ereignis, **Then** das erwartete beobachtbare Ergebnis [R9]. Zusätzlicher Kontext oder zusätzliche Ergebnisse verwenden **And** / **But**; dies ist das strukturelle Äquivalent zu Arrange-Act-Assert, das `spec/project/test-pyramid-foundation/` [R5] benennt.
- Jedes Szenario **MUSS [MUST]** **genau ein Verhalten** beschreiben. Ein Szenario mit mehr als einem eigenständigen **When**, das mehr als ein Verhalten auslöst, **MUSS [MUST]** aufgeteilt werden.
- Ein Szenario **MUSS [MUST]** **deklarativ** sein und in Domänenbegriffen sagen, *was* das Verhalten ist, nicht *wie* die Nutzerin die Oberfläche bedient. Imperative, UI-mechanische Steps („X ins dritte Feld tippen, den blauen Button klicken") gehören in die Step-Ebene, nie in den Szenariotext [R10].
- Eine gemeinsame Vorbedingung, die jedem Szenario eines Features gemein ist, **SOLLTE [SHOULD]** in ein **Background** gehoben statt wiederholt werden, und ein Background **MUSS [MUST]** nur Setup enthalten, nie ein **When** oder ein **Then**.
- Ein Verhalten, das über ein Set von Beispielzeilen (Äquivalenzklassen, Grenzwerte) geübt wird, **SOLLTE [SHOULD]** ein **Scenario Outline** mit einer **Examples**-Tabelle verwenden statt kopierter, nahezu identischer Szenarien; jede Zeile **MUSS [MUST]** dasselbe einzelne Verhalten üben.
- Szenarien **SOLLTE [SHOULD]** **Tags** zur Selektion und Traceability tragen (siehe den Ableitungs-Workflow), und ein Projekt **SOLLTE [SHOULD]** sein Tag-Vokabular definieren, statt Tags ad hoc anwachsen zu lassen.
- Jedes Szenario und Feature **MUSS [MUST]** einen **absichtsoffenbarenden Titel** haben, der das Verhalten benennt, nicht die Steps; ein Titel, der bloß das Given-When-Then wiederholt, ist ein Geruch.

### Ubiquitous Language

- Szenarien **MUSS [MUST]** in der **Ubiquitous Language** der Domäne geschrieben sein: dieselben Begriffe, die Business, Anforderungen und Code für dieselben Konzepte verwenden, damit ein Nicht-Programmierer-Stakeholder ein Szenario lesen und bestätigen kann [R11].
- Ein in einem Szenario verwendeter Begriff **MUSS NICHT [MUST NOT]** von seiner Bedeutung in der Anforderung abweichen, auf die er zurückverweist; wo der Domäne ein vereinbarter Begriff fehlt, **MUSS [MUST]** die Ermittlung (oben) einen etablieren, statt dass ein Szenario ein privates Synonym erfindet.

### Lebende Dokumentation

- Das Szenario-Set **MUSS [MUST]** als **lebende Dokumentation** nutzbar sein: die autoritative, ausführbare Beschreibung dessen, was das System tut, wahrheitsgemäß gehalten, weil sie gegen das System läuft und fehlschlägt, wenn sie driftet [R12].
- Ein Szenario, das obsolet ist, weil sich das Verhalten geändert hat, **MUSS [MUST]** im Gleichschritt mit der Änderung aktualisiert oder zurückgezogen werden, nie grün-aber-lügend belassen oder ohne festgehaltenen Grund deaktiviert werden; ein dauerhaft übersprungenes Szenario ist Dokumentation, die nicht mehr dokumentiert.
- Dokumentations-Prosa, die wiederholt, was ein Szenario bereits aussagt, **SOLLTE [SHOULD]** stattdessen auf das Szenario verweisen, damit das ausführbare Beispiel die einzige Quelle der Wahrheit bleibt.

### Step-Definition-Design

- Eine Step-Definition **MUSS [MUST]** **dünn** sein: Sie übersetzt einen Gherkin-Step in eine Aktion gegen das System (oder, bei E2E, in einen Aufruf der Page-Object-Ebene [R3]) und hält keine eigene fachliche Logik.
- Step-Definitionen **MUSS [MUST]** über Szenarien hinweg **wiederverwendet** werden; derselbe Domänen-Step **MUSS NICHT [MUST NOT]** je Feature neu implementiert werden. Gemeinsames Setup und Hilfslogik leben in der Step-/Support-Ebene, nicht in jede Bindung kopiert.
- Ein Gherkin-Step **MUSS NICHT [MUST NOT]** Assertions enthalten; die *Bindung* des **Then**-Steps führt die Assertion aus, während der Szenariotext das erwartete Ergebnis in Domänenbegriffen aussagt. Assertion-Logik **MUSS NICHT [MUST NOT]** in die Szenariodatei durchsickern.
- Die Bindung eines Steps **MUSS [MUST]** Selektoren und Low-Level-Interaktion nur über die Ebene auflösen, die sie besitzt (die Page Objects von `spec/project/e2e-test-automation/` [R3], die den Vertrag von `spec/frontend/testability-identifiers/` [R4] bei E2E auflösen); ein Step **MUSS NICHT [MUST NOT]** einen rohen Selektor inline benennen.

### Vom Testcase-Dokument zu ausführbaren Szenarien

- Die Ableitung **MUSS [MUST]** ein abstraktes **Testcase-Dokument** (TC-IDs und ihre Verhalten, wie unter `spec/project/test-case-derivation/` [R2] erzeugt) als Eingabe konsumieren und **MUSS NICHT [MUST NOT]** die Fälle neu ableiten; dieser Workflow kodiert bestehende Fälle als Szenarien, er erfindet sie nicht.
- Die Ableitung **MUSS [MUST]** diesem geordneten Workflow folgen:
  1. **MUSS [MUST]** die Testfälle nach der Domänen-Fähigkeit gruppieren, die sie üben, und jede Fähigkeit auf ein **Feature** abbilden.
  2. **MUSS [MUST]** **ein Szenario je eigenständigem TC-Verhalten** ableiten; ein Testfall, der mehrere Verhalten beschreibt, wird zu mehreren Szenarien, und nahezu identische Fälle über ein Datenset **SOLLTE [SHOULD]** zu einem **Scenario Outline** mit einer Zeile je Fall kollabieren.
  3. **MUSS [MUST]** die Teile jedes Falls in Given-When-Then übersetzen: seine **Vorbedingung** wird **Given**, seine **Aktion** wird **When**, sein **erwartetes Ergebnis** wird **Then**, wobei jeder Step deklarativ bleibt, selbst wenn der Quellfall UI-Mechanik auflistet.
  4. **MUSS [MUST]** jedes resultierende Szenario mit seiner Quell-**TC-ID** taggen (zum Beispiel `@TC-042`), damit die Anforderung-zu-Szenario-Verbindung maschinenprüfbar und bidirektional ist; der Tag ist ein **hartes Review-Gate**, sodass ein Szenario ohne auflösbaren TC-ID-Tag im Review **fehlschlagen MUSS [MUST]**, statt nur markiert zu werden. Ein exploratives Szenario, das einem formalen Testfall vorausgeht, prägt seine TC-ID zuerst in der Case-Determination (`spec/project/test-cycle-case-determination/`), ist also keine Ausnahme vom Gate—es ist traceable, wenn es landet.
  5. **SOLLTE [SHOULD]** Vorbedingungen, die jedem Szenario eines Features gemein sind, in ein **Background** heben, und **SOLLTE [SHOULD]** den Stufen-Hinweis des Falls mitführen, damit das Szenario auf der Stufe landet, die der Fall gewählt hat [R1].
- Die Ableitung **MUSS [MUST]** die **TC-ID → Szenario**-Traceability erhalten, damit die Abdeckung des Testcase-Dokuments auditierbar ist, und erweitert damit die Traceability-Kette, die `spec/project/test-cycle-case-determination/` [R1] und `spec/project/e2e-test-automation/` [R3] bereits verlangen.
- Ein Testfall, der **MUSS NICHT [MUST NOT]** in ein einzelnes deklaratives Verhalten normalisiert werden (er ist eigentlich mehrere Verhalten, oder sein erwartetes Ergebnis ist nicht beobachtbar), **MUSS [MUST]** zurückgemeldet statt in ein missgestaltetes Szenario gezwungen werden; ein Fall, der dem Workflow widersteht, ist noch nicht verstanden.

### BDD auf End-to-End-Tests

- Auf der E2E-Stufe **MUSS [MUST]** die BDD-Szenario-Ebene *über* der Ausführungsmaschinerie sitzen: Das Szenario benennt die Absicht in der Ubiquitous Language, seine Step-Bindung delegiert an die Page-Object-Ebene, die `spec/project/e2e-test-automation/` [R3] besitzt, und diese Ebene besitzt Waits, Screenshots, Protokoll und Selektorauflösung.
- Ein Szenario bei E2E **MUSS NICHT [MUST NOT]** die Verantwortungen absorbieren, die die Ausführungs-Spec besitzt: Es **MUSS NICHT [MUST NOT]** Waits, Sleeps, Screenshot-Aufrufe oder Selektoren kodieren und **MUSS NICHT [MUST NOT]** die Page-Object-Disziplin wiederholen. Es stützt sich über die Step-Ebene auf jene Spec.
- E2E-Szenarien **MUSS [MUST]** schlank und journey-fokussiert bleiben, konsistent mit der Regel des überbevölkerten Apex in `spec/project/e2e-test-automation/` [R3] und dem Stufenmodell [R5]: Eine feldbezogene Prüfung, die eine niedrigere Stufe verifizieren könnte, **MUSS NICHT [MUST NOT]** als E2E-Szenario geschrieben werden, nur weil BDD sie lesbar macht.
- Der **TC-ID**-Tag des Szenarios **MUSS [MUST]** sich mit der Anforderungs-Traceability, die die Ausführungs-Spec bereits verlangt, komponieren, nicht sie ersetzen, damit ein Lauf von der Anforderung über den Fall zum Szenario zum Screenshot auditierbar ist.

### Anti-Patterns

- Das Folgende **MUSS [MUST]** als Defekt behandelt und im Review abgelehnt werden:
  - **Imperative, UI-gekoppelte Szenarien**: Steps, die Klicken, Tippen und Selektoren beschreiben statt des Verhaltens [R10].
  - **Assertions in der Szenariodatei** oder fachliche Logik in einer Step-Bindung: Die Ebenen sind vertauscht.
  - **Mehr-Verhalten-Szenarien**: mehrere unzusammenhängende **When/Then**-Paare in einem Szenario oder eine konjunktionslastige Kette von **And**-Steps, die eigenständige Verhalten verbirgt.
  - **Nebensächliche Details**: Daten oder Steps, die für das getestete Verhalten irrelevant sind, die die Absicht verschleiern und falsche Fehlschläge verursachen.
  - **Szenario-pro-Methode / Internas testen**: Szenarien, die die Implementierungsstruktur spiegeln statt nutzerbeobachtbaren Verhaltens.
  - **Szenarien als Skripte, nicht als Dokumentation**: Titel, die Steps wiederholen, keine Ubiquitous Language, unlesbar für einen Nicht-Programmierer-Stakeholder.
  - **Nicht traceable Szenarien**: kein auflösbarer TC-ID- oder Anforderungs-Link, sodass die Abdeckung nicht auditierbar ist.

## Referenzprofil (illustrativ, nicht normativ)

Dieses Profil macht den tool-neutralen Kern mit **Gherkin** und der **Cucumber-Familie** (Cucumber-JVM, Cucumber.js, `pytest-bdd`, `behave`) konkret. Es ist illustrativ: Ein Projekt auf einem anderen Stack erfüllt den bindenden Kern ohne es. Das mitgelieferte `templates/`-Verzeichnis trägt ein ausgearbeitetes Beispiel.

- **Feature-Dateien** (`*.feature`) halten Gherkin: ein `Feature:`, ein optionales `Background:` und `Scenario:` / `Scenario Outline:`-Blöcke mit `Given` / `When` / `Then` / `And` / `But`-Steps, Tags auf der Zeile darüber (`@TC-042`) und eine `Examples:`-Tabelle für Outlines [R9].
- **Step-Definitionen** binden den Text jedes Steps an Code in der Sprache des Projekts und bleiben dünn, indem sie an die Domäne oder, bei E2E, an die Page-Object-Ebene [R3] delegieren.
- Eine ausgearbeitete Feature-Datei plus ein passendes Step-Definition-Skelett (`pytest-bdd`, gewählt, um zum Python-Referenzprofil von `spec/project/e2e-test-automation/` zu passen) liegt unter `spec/project/behavior-driven-development/templates/`.

## Akzeptanzkriterien

- [ ] Der bindende Kern ist tool-neutral formuliert, mit Gherkin und der Cucumber-Familie auf das illustrative Referenzprofil beschränkt
- [ ] Der Kern ist explizit stufen-neutral, mit E2E als primärem Anwendungsfall in einer eigenen Anforderungsgruppe benannt
- [ ] Kollaborative Ermittlung (Example Mapping Rules/Examples/Questions, Three Amigos) ist als Eingangstür gefordert
- [ ] Die Given-When-Then-Szenariosprache ist spezifiziert: ein Verhalten pro Szenario, deklarativ statt imperativ, Background für gemeinsames Setup, Scenario Outline für Datensets, Tags, absichtsoffenbarende Titel
- [ ] Anforderungen an Ubiquitous Language und lebende Dokumentation sind vorhanden
- [ ] Step-Definition-Prinzipien sind spezifiziert: dünne Steps, szenarienübergreifende Wiederverwendung, keine Assertions in Gherkin, Selektorauflösung nur über die besitzende Ebene
- [ ] Die Ableitung Testcase-Dokument zu ausführbaren Szenarien ist ein geordneter MUSS/SOLLTE-Workflow: ein Szenario je TC-Verhalten, Vorbedingung/Aktion/Ergebnis zu Given-When-Then und ein TC-ID-Szenario-Tag, der ein hartes Review-Gate ist (ein nicht auflösbarer Tag schlägt im Review fehl), für maschinenprüfbare Traceability
- [ ] BDD-auf-E2E-Anforderungen platzieren die Szenario-Ebene über der Ausführungsebene und delegieren die Mechanik an `e2e-test-automation`
- [ ] Die Nicht-Ziele verlinken alle vier Nachbar-Specs (`test-cycle-case-determination`, `test-case-derivation`, `e2e-test-automation`, `testability-identifiers`) nach Verantwortung
- [ ] Die Anti-Pattern-Liste benennt imperative Szenarien, Assertions in Gherkin, Mehr-Verhalten-Szenarien, nebensächliche Details, Internas testen, Skripte-statt-Dokumentation und nicht traceable Szenarien
- [ ] EN- und DE-Fassung sind strukturell identisch (gleiche Überschriften, Anforderungsanzahl, Akzeptanzkriterien-Anzahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-cycle-case-determination/`: besitzt, wann im Zyklus Beispiele entdeckt werden und welche Design-Techniken gelten; benennt Example Mapping / BDD als SOLLTE, das diese Spec operationalisiert
- [R2] `spec/project/test-case-derivation/`: leitet die abstrakten Testfälle ab, die diese Spec als Eingabe konsumiert
- [R3] `spec/project/e2e-test-automation/`: besitzt die E2E-Ausführungsmechanik, an die die Steps eines Szenarios delegieren
- [R4] `spec/frontend/testability-identifiers/`: besitzt den stabilen Selektor-Vertrag, gegen den ein Step letztlich auflöst
- [R5] `spec/project/test-pyramid-foundation/`: besitzt die Stufen-Taxonomie und Coverage-Governance; benennt Given-When-Then als strukturelles Äquivalent zu Arrange-Act-Assert
- [R6] Dan North, *Introducing BDD* (Behavior-Driven Development, Ursprung von Ubiquitous Language und Beispiel): <https://dannorth.net/introducing-bdd/>
- [R7] Matt Wynne / Cucumber, *Example Mapping* (Rules, Examples, Questions): <https://cucumber.io/docs/bdd/example-mapping/>
- [R8] George Dinwiddie / Cucumber, *The Three Amigos* (Perspektiven Business, Entwicklung, Testing): <https://cucumber.io/docs/bdd/who-does-what/>
- [R9] Cucumber, *Gherkin Reference* (Given-When-Then, Background, Scenario Outline, Tags): <https://cucumber.io/docs/gherkin/reference/>
- [R10] Cucumber, *Writing better Gherkin* (deklarative statt imperative Szenarien): <https://cucumber.io/docs/bdd/better-gherkin/>
- [R11] Eric Evans / Martin Fowler, *Ubiquitous Language*: <https://martinfowler.com/bliki/UbiquitousLanguage.html>
- [R12] Gojko Adzic, *Specification by Example* (lebende Dokumentation aus ausführbaren Beispielen): <https://www.manning.com/books/specification-by-example>
- [R13] `spec/project/bdd-page-object-integration/`: besitzt den BDD-zu-Page-Object-Integrations- und Entkopplungs-Vertrag, auf den sich die Step-Definitionen dieser Spec bei E2E stützen

## Offene Fragen

- ~~Sollte der TC-ID-Szenario-Tag ein hartes Gate im Review sein (ein Szenario ohne auflösbare TC-ID schlägt fehl), oder ein starkes SOLLTE, da manche explorativen Szenarien einem formalen Testfall vorausgehen?~~ **Entschieden (2026-07-24): hartes Gate.** Ein Szenario ohne auflösbaren TC-ID-Tag schlägt im Review fehl (Schritt 4 oben). Das ist die einzige konsistente Lesart des eigenen normativen Ableitungs-Workflows der Spec: jedes Szenario wird per Konstruktion *aus* einer TC-ID abgeleitet, sodass ein nicht-traceables Szenario bedeutet, dass sein Quell-Testfall nicht verstanden wurde—genau das Versagen, das der Workflow verhindern soll. Explorative Szenarien sind keine Ausnahme: sie prägen ihre TC-ID in der Case-Determination, bevor sie landen, sodass das Gate legitime Exploration nie blockiert, sondern nur verwaiste Szenarien.
- Sollte das Referenzprofil mehr als ein Cucumber-Familie-Skelett liefern (zum Beispiel eine Cucumber.js-Bindung neben `pytest-bdd`), oder genügt ein ausgearbeitetes Beispiel, um das Profil illustrativ zu halten?
- Rechtfertigt die Ubiquitous-Language-Anforderung ein projektweites Glossar-Artefakt, oder genügt Konsistenz innerhalb des Szenario-Sets, ohne ein separates Dokument vorzuschreiben?
