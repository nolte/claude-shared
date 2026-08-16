# Test-Stufe: Unit

Status: draft

## Kontext

Die Unit-Stufe ist die **breite, schnelle Basis der ausführenden Tests** in der von `spec/project/test-pyramid-foundation/` definierten Pyramide: Sie ist die erste Stufe, die den Code tatsächlich ausführt (anders als die Static Analysis darunter, die nur die Code-Struktur liest), und diejenige mit der billigsten, präzisesten Fehlerlokalisierung. Ein Unit-Test übt eine kleine Verhaltenseinheit und prüft das beobachtbare Ergebnis, in Millisekunden, ohne Kontakt zur Außenwelt.

Diese Spezifikation ist die stufenspezifische Realisierung der **invarianten Form** des Fundaments für die Unit-Stufe. Sie füllt jedes von dieser Form geforderte Feld (Zweck und Umfangsgrenze, Isolation und erlaubte Test-Doubles, Geschwindigkeit und Determinismus, Ausführungs-Platzierung, Traceability, kanonische Anti-Patterns, optionales Referenzprofil) und ergänzt die stufenspezifische Substanz: die bewusst team-bestimmte Definition „einer Einheit", die Unterscheidungen solitär/sociable und classicist/mockist, die FIRST-Eigenschaften, die Regel Verhalten-statt-Implementierung-prüfen und den Platz von Property-based Testing.

Sie ist bewusst **werkzeug-agnostisch**: Die bindenden Anforderungen nennen nie einen Runner oder eine Mocking-Bibliothek. Konkrete Werkzeuge erscheinen nur als illustratives Referenzprofil.

**Verhältnis zu den anderen Specs.** Diese Stufe ist nach Verantwortung abgegrenzt, nicht durch Überschneidung:

- `spec/project/test-pyramid-foundation/` [R1] besitzt das Stufenmodell, die FIRST-nahen Governance-Invarianten und die Meszaros-Test-Double-Taxonomie. Diese Spec detailliert die Unit-Stufe; sie wiederholt das Modell nicht.
- `spec/project/test-tier-static-analysis/` [R2] ist die Stufe **darunter**: Sie analysiert Code, ohne ihn auszuführen. Die Grenze lautet „liest Code-Struktur" (statisch) vs. „führt die Einheit aus und prüft Verhalten" (Unit).
- Die **Component-Stufe** (`spec/project/test-tier-component/`, Geschwister, darüber) übt eine ganze auslieferbare Komponente; die **Integration-Stufe** (`spec/project/test-tier-integration/`, darüber) bringt einen echten externen Kollaborateur ein. Die Grenze lautet „eine isolierte Einheit" (diese Stufe) vs. „eine Komponente / kollaborierende Einheiten mit echten Abhängigkeiten".
- `spec/project/quality-gate/` [R3] **führt** die Unit-Stufe als Teil des schnellen Gates aus und besitzt Ausführungsmechanik und Ausgabeform. Diese Spec definiert, was die Unit-Stufe enthalten muss; quality-gate definiert, wie sie ausgeführt wird.

Leser: Spec-Autor:innen, die die Geschwister-Stufen-Specs schreiben; Skill- und Agent-Autor:innen, die die Unit-Stufen-Triade (Entwicklung/Ausführung/Analyse) bauen; Entwickler:innen, die Unit-Tests schreiben und reviewen; Reviewer, die prüfen, ob eine Unit-Suite schnell, isoliert, verhaltensprüfend und nicht over-mockt ist.

## Ziele

- Definieren, was ein Unit-Test verifiziert und, scharf, was ihn in eine andere Stufe verwandelt (die I/O-Linie überschreiten, echte Kollaborateure hereinholen)
- Die bewusst team-bestimmte Definition „einer Einheit" und die Wahlmöglichkeiten solitär/sociable und classicist/mockist verankern, damit ein Projekt bewusst einen konsistenten Stil wählt
- Die FIRST-Eigenschaften (Fast, Isolated, Repeatable, Self-validating, Timely) als Qualitätsmaßstab der Stufe kodieren
- Assertions auf **beobachtbares Verhalten über die öffentliche Schnittstelle** verlangen, nie auf privates Implementierungsdetail, damit Tests Refactoring überleben
- Die Test-Double-Nutzung begrenzen, damit die Stufe nicht in Over-Mocking abdriftet, das Tests an die Implementierung koppelt
- Die Stufe werkzeug-agnostisch halten, mit einem austauschbaren Referenzprofil statt eines vorgeschriebenen Runners

## Nicht-Ziele

- Die Stufe auszuführen oder ihre Ausführungsmechanik und Ausgabetabelle zu definieren: Eigentum von `spec/project/quality-gate/` [R3]
- Echte externe Kollaborateure (Datenbank, Netzwerk, Dateisystem, Broker) zu üben: Das überschreitet in die Integration-Stufe
- Eine ganze auslieferbare Komponente durch ihre eigene Schnittstelle zu üben: Das ist die Component-Stufe
- Einen bestimmten Test-Runner, eine Assertion-Bibliothek oder ein Mocking-Framework vorzuschreiben: Das Referenzprofil ist illustrativ
- Ein numerisches Coverage-Ziel vorzuschreiben: Coverage ist gemäß dem Fundament eine Leitlinie, kein Unit-Stufen-Gate
- Test-Driven Development zu verlangen: TDD ist eine empfohlene Praxis zur Erzeugung von Unit-Tests, keine Vorbedingung der Stufe

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** einen Unit-Test als einen definieren, der **eine einzelne Verhaltenseinheit ausführt und das beobachtbare Ergebnis prüft**, mit präziser Fehlerlokalisierung, als breite schnelle Basis der ausführenden Stufen [R1], [R5].
- **DARF NICHT [MUST NOT]** einen Unit-Test die **Außenwelt** berühren lassen: keine echte Datenbank, kein Dateisystem, kein Netzwerk, keine Systemuhr, keine Zufallsquelle. Diese Linie zu überschreiten macht den Test zu einem Integrationstest, kein Unit-Test, egal wie er etikettiert ist [R5], [R9].
- **MUSS [MUST]** die Grenze zur **Static Analysis** scharf halten: Static Analysis liest Code-Struktur, ohne ihn auszuführen; die Unit-Stufe führt die Einheit aus. Eine Prüfung, die keine Ausführung braucht, gehört unter diese Stufe [R2].
- **MUSS [MUST]** die Grenze zur **Component- und Integration-Stufe** scharf halten: Ein Unit-Test deckt eine isolierte Einheit ab, nicht eine ganze auslieferbare Komponente und nicht einen echten externen Kollaborateur.

### Was „eine Einheit" ist, und solitär versus sociable

- **MUSS [MUST]** die Definition „einer Einheit" als **bewusst team-bestimmt** behandeln: Eine Einheit kann eine einzelne Funktion, eine Klasse oder ein kleiner Cluster verwandter Objekte sein, projektspezifisch entschieden und festgehalten, statt portfolioweit diktiert [R5].
- **MUSS [MUST]** ein Projekt zwischen **solitären** Unit-Tests (die Einheit wird mit Test-Doubles von ihren Kollaborateuren isoliert) und **sociable** Unit-Tests (die Einheit übt ihre echten Kollaborateure) wählen lassen und festhalten, welcher Stil der Default ist; Fowler merkt an, dass beide legitim sind und Classicisten tendenziell sociable bevorzugen [R5].
- **SOLLTE [SHOULD]** **sociable** Tests bevorzugen, wo die echten Kollaborateure selbst schnell und deterministisch sind (in-process, kein I/O), weil sie den Test weniger an die interne Struktur koppeln und FIRST weiterhin erfüllen; zur solitären Isolation greifen, wenn ein Kollaborateur langsam, nicht-deterministisch oder noch nicht gebaut ist [R5].

### Die Schulen Classicist und Mockist

- **MUSS [MUST]** die beiden Schulen als bewusste Wahl anerkennen, kein Versehen: die **classicist** (Detroit / Chicago, zustandsbasiert, echte Kollaborateure, sociable) und die **mockist** (London, interaktionsbasiert, gemockte Kollaborateure, solitär, outside-in) [R5], [R6].
- **MUSS [MUST]** festhalten, dass **mockist / interaktionsbasierte** Tests prüfen, *wie* Kollaborateure aufgerufen wurden, und daher stärker **an die Implementierung gekoppelt und refactor-fragiler** sind; ein Projekt, das sie übernimmt, akzeptiert diesen Tausch für stärkere Isolation und outside-in-Design-Druck [R5], [R6].

### FIRST-Eigenschaften

- **MUSS [MUST]** verlangen, dass Unit-Tests die **FIRST**-Eigenschaften (Ottinger & Schuchert) erfüllen [R9], [R10]:
  - **Fast** — läuft in Millisekunden, sodass die ganze Suite in Sekunden Feedback gibt und Entwickler:innen sie ständig ausführen.
  - **Isolated / Independent** — keine Abhängigkeit von anderen Tests, von Reihenfolge oder von geteiltem veränderlichem Zustand; jeder baut seine eigene Welt auf und ab.
  - **Repeatable** — dasselbe Ergebnis bei jedem Lauf, in jeder Umgebung; erreicht durch Entfernen von I/O und externem Zustand.
  - **Self-validating** — besteht oder schlägt eigenständig mit einer klaren Assertion fehl; keine menschliche Inspektion der Ausgabe.
  - **Timely** — nahe am getesteten Code geschrieben (das TDD-Ideal davor, mindestens aber daneben, nie lange danach).

### Isolation und erlaubte Test-Doubles

- **MUSS [MUST]** das **Meszaros-Test-Double-Vokabular** des Fundaments (Dummy, Fake, Stub, Spy, Mock) verwenden und nennen, welche Art ein gegebenes Double ist, damit Reviews eine Sprache sprechen [R1], [R7].
- **MUSS [MUST]** **Zustandsverifikation** (den resultierenden Zustand prüfen) bevorzugen und **Verhaltensverifikation** (Mocks, die Interaktionen prüfen) für die Fälle reservieren, in denen die Interaktion *der* beobachtbare Vertrag ist; Über-Nutzung von Verhaltensverifikation ist der Over-Mocking-Geruch [R6], [R7].
- **DARF NICHT [MUST NOT]** **over-mocken**: nur Kollaborateure mocken, die das Projekt besitzt und die eine echte Grenze darstellen; keine Value Objects mocken, keine Typen mocken, die man nicht besitzt, und nicht so viel von der Welt der Einheit ersetzen, dass der Test nur sein eigenes Gerüst prüft [R7], [R8].
- **DARF NICHT [MUST NOT]** ein Double **permissiver machen als den Kollaborateur, den es ersetzt**, entlang irgendeiner Dimension, auf die sich der Test stützt, gemäß der Treue-Regel des Fundaments [R1]. Die drei Regeln oben begrenzen, *wie viel* ein Unit-Test doubelt; diese begrenzt, ob das Double **ablehnen** kann, und auf dieser Stufe ist der wiederkehrende Übeltäter ein handgeschriebenes Double einer **Persistenz- oder Repository-Grenze**: Der echte Kollaborateur erzeugt oder verwirft Keys, erzwingt Eindeutigkeit und lehnt Nulls ab, während das Double all das stillschweigend unterlässt und jeder Test der Datei dann für einen Zustand besteht, den die Datenbank nie halten würde. Wo die Abweichung nicht geschlossen werden kann, **MUSS [MUST]** sie im Double selbst benannt werden [R1], und der resultierende Fehlermodus ist als `T9` gemäß [R12] zitierbar.

### Was geprüft wird

- **MUSS [MUST]** **beobachtbares Verhalten über die öffentliche Schnittstelle der Einheit** prüfen, nie privates Implementierungsdetail; ein Test, der weiß, wie die Einheit intern funktioniert, bricht bei verhaltenswahrendem Refactoring, was die kanonische Ursache fragiler Tests ist [R8].
- **MUSS [MUST]** jeden Test als **Arrange–Act–Assert** (Given–When–Then) strukturieren: aufsetzen, ein Verhalten ausüben, das Ergebnis prüfen.
- **MUSS [MUST]** **ein logisches Verhalten pro Test** prüfen und ihm einen **absichtsoffenbarenden Namen** geben, der das Verhalten und das erwartete Ergebnis nennt, nicht die getestete Methode.
- **MUSS [MUST]** Tests **unabhängig** halten: keine Reihenfolgeabhängigkeit, kein geteiltes veränderliches Fixture, gemäß der Determinismus-Regel des Fundaments.

### Property-based und parametrisiertes Testen

- **SOLLTE [SHOULD]** **parametrisierte / table-driven** Tests verwenden, um ein Verhalten über viele Eingaben abzudecken, ohne Test-Bodies zu duplizieren.
- **DARF [MAY]** **Property-based Testing** (Invarianten über generierte Eingaben prüfen, Fehler auf einen minimalen Fall schrumpfen) auf der Unit-Stufe verwenden, wo ein Verhalten besser als Eigenschaft denn als festes Beispiel ausgedrückt wird [R11]; Property-based Tests **MÜSSEN [MUST]** weiterhin im Sinne des Fundaments deterministisch sein (ein fester Seed reproduziert einen Fehler).

### Determinismus, Geschwindigkeit und Platzierung

- **MUSS [MUST]** die Stufe **deterministisch und schnell** halten: Ein flaky oder langsamer „Unit"-Test ist ein Defekt; die übliche Ursache ist verstecktes I/O, Zeit, Zufall oder Reihenfolgeabhängigkeit, die diese Stufe alle verbietet [R5], [R9].
- **MUSS [MUST]** die Unit-Stufe in **Pre-Commit und als PR-gatenden CI-Check** ausführen (das Fast-Tier-Gate gemäß `spec/project/pull-request-workflow/`, ausgeführt gemäß `spec/project/quality-gate/`), weil sie billig genug ist, um jede Änderung zu gaten.

### Coverage und Suite-Qualität

- **MUSS [MUST]** Unit-**Coverage als Leitlinie, nicht als Ziel** behandeln, gemäß dem Fundament: hohe Line-Coverage mit schwachen Assertions ist ein falsches Signal, und **Mutationsscore** ist das stärkere Maß dafür, ob die Unit-Tests Verhaltensänderungen tatsächlich fangen.
- **SOLLTE [SHOULD]** den Test auf der **niedrigsten Stufe schreiben, die Vertrauen gibt** (die Regel des Fundaments): Ein Verhalten, das aus einer Einheit vollständig bestimmbar ist, gehört hierher, nicht in eine langsamere höhere Stufe.

### Traceability

- **MUSS [MUST]** einen Unit-Test, der einen abgeleiteten Testfall verifiziert, die **TC-ID** (und über sie die Anforderung) benennen lassen, die er abdeckt, gemäß der Traceability-Kette des Fundaments, damit Anforderungsabdeckung auditierbar ist; rein interne Einheiten, die auf keine Anforderung zurückführen, brauchen keine TC-ID, **SOLLTEN [SHOULD]** aber dennoch einen absichtsoffenbarenden Namen tragen.

### Optionales Referenzprofil

- **DARF [MAY]** ein vollständig ausgearbeitetes, stack-spezifisches Referenzprofil pinnen, klar zu „Referenz" degradiert. Ein illustratives Python-Profil: `pytest` als Runner (mit parametrisierten Fixtures), `unittest.mock` für das seltene owned-boundary-Double und `Hypothesis` für Property-based-Invarianten. Andere Ökosysteme realisieren dieselbe Stufe mit ihren eigenen Werkzeugen (JUnit/TestNG + Mockito; Vitest/Jest + Sinon + fast-check; Gos `testing`; Rusts `cargo test`). Werkzeugnamen sind illustrativ, nie verlangt.

## Akzeptanzkriterien

- [ ] Die Spec definiert einen Unit-Test als Einzel-Verhalten-Ausführung ohne Außenwelt-Kontakt und erklärt, dass das Überschreiten der I/O-Linie ihn zum Integrationstest macht
- [ ] „Eine Einheit" ist als team-bestimmt etabliert, und die solitär/sociable-Wahl ist als festzuhalten gefordert, zitiert auf Fowler
- [ ] Die Schulen Classicist und Mockist sind mit dem Implementierungs-Kopplungs-/Refactor-Fragilitäts-Trade-off interaktionsbasierter Tests beschrieben
- [ ] Die FIRST-Eigenschaften sind mit der Bedeutung jeder Eigenschaft aufgezählt, Ottinger & Schuchert zugeschrieben
- [ ] Test-Doubles verwenden das Meszaros-Vokabular des Fundaments, Zustandsverifikation wird bevorzugt, und Over-Mocking ist verboten mit der Mock-nur-was-du-besitzt-Regel
- [ ] Einem Double ist verboten, permissiver zu sein als der Kollaborateur, den es ersetzt, die Persistenzgrenze ist als wiederkehrender Übeltäter dieser Stufe benannt, und eine nicht schließbare Abweichung muss im Double deklariert werden
- [ ] Assertions sind auf beobachtbares Verhalten über die öffentliche Schnittstelle gefordert, mit AAA, ein-Verhalten-pro-Test, absichtsoffenbarenden Namen und Unabhängigkeit
- [ ] Parametrisiertes Testen ist empfohlen und Property-based Testing erlaubt mit einer Determinismus-(fester-Seed)-Bedingung
- [ ] Determinismus und Geschwindigkeit sind gefordert, die flaky/langsam-Unit-Ursachen benannt, und die Stufe in Pre-Commit + PR-Gate platziert
- [ ] Coverage ist als Leitlinie mit Mutationsscore als stärkerem Signal gebunden, und die Regel niedrigste-Stufe-die-Vertrauen-gibt referenziert
- [ ] Traceability auf TC-ID ist für anforderungsverifizierende Einheiten gefordert
- [ ] Die Abgrenzung gegen Static Analysis (darunter), Component/Integration (darüber) und quality-gate (führt aus) ist explizit
- [ ] Ein optionales, klar degradiertes Referenzprofil ist bereitgestellt, ohne eine Toolchain vorzuschreiben
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-pyramid-foundation/` — das Stufenmodell, die FIRST-nahe Governance und die Meszaros-Test-Double-Taxonomie, die diese Spec realisiert
- [R2] `spec/project/test-tier-static-analysis/` — die Stufe darunter (analysiert Code, ohne ihn auszuführen); die statisch↔Unit-Grenze
- [R3] `spec/project/quality-gate/` — führt die Unit-Stufe im schnellen Gate aus und besitzt Ausführungsmechanik / Ausgabeform
- [R4] `spec/project/pull-request-workflow/` — besitzt die Erzwingung erforderlicher Status-Checks, die das Unit-Stufen-Gate speist
- [R5] Martin Fowler, *UnitTest* (team-bestimmte Einheit; solitär vs. sociable; classicist vs. mockist) — <https://martinfowler.com/bliki/UnitTest.html>
- [R6] Martin Fowler, *Mocks Aren't Stubs* (Zustands- vs. Verhaltensverifikation; mockist-Kopplung) — <https://martinfowler.com/articles/mocksArentStubs.html>
- [R7] Martin Fowler, *TestDouble* (die fünf Doubles; Over-Mocking) — <https://martinfowler.com/bliki/TestDouble.html>
- [R8] Kent C. Dodds, *Testing Implementation Details* (Verhalten prüfen, nicht Interna) — <https://kentcdodds.com/blog/testing-implementation-details>
- [R9] T. Ottinger & B. Schuchert, *FIRST* (Fast, Isolated, Repeatable, Self-validating, Timely) — <http://agileinaflash.blogspot.com/2009/02/first.html>
- [R10] T. Ottinger, *Brett Schuchert and I came up with FIRST* (maßgebliche Zuschreibung) — <https://medium.com/@tottinge_79838/brett-schuchert-and-i-came-up-with-first-so-this-is-an-authoritative-statement-ec6006f6a59e>
- [R11] *fast-check* — Property-based Testing (Invarianten über generierte Eingaben, Shrinking) — <https://fast-check.dev/>
- [R12] `spec/project/test-falsifiability/` — die tier-übergreifende Taxonomie von Tests, die nicht fehlschlagen können; `T9` ist der Fehlermodus, den ein Double erzeugt, das permissiver ist als sein Kollaborateur, und die Spec trägt die Review-Frage, die ihn detektiert

## Offene Fragen

- Sollte das Portfolio einen Unit-Stil eines Projekts als Default setzen (sociable/classicist vs. solitär/mockist) oder ihn projektspezifisch lassen mit nur der „halte deine Wahl fest"-Anforderung?
- Braucht die Entwickeln/Ausführen/Analysieren-Triade der Unit-Stufe einen dedizierten Unit-Test-Autor-Agent und einen Over-Mocking-Reviewer, oder genügt `quality-gate` (Ausführen) plus eine dünne Autor-Capability — und sollte ein Over-Mocking-/Implementierungsdetail-Review ein eigener Agent sein oder ein Check innerhalb eines breiteren Test-Reviewers?
- Sollte Property-based Testing für reine Funktionen mit klaren Invarianten von MAY auf SHOULD angehoben werden oder optional bleiben?
