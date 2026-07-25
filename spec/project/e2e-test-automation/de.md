# Standard für End-to-End-Test-Automatisierung

Status: draft

## Kontext

Ein End-to-End-Test (E2E) bedient die echte Benutzeroberfläche eines laufenden Systems und prüft, was die Nutzerin tatsächlich sieht. Der wertvolle, wiederverwendbare Teil der E2E-Arbeit ist nicht der Testcode selbst, sondern die **Disziplin**, die eine Test-Suite vertrauenswürdig hält: Jede Interaktion läuft über ein Page Object, damit Selektoren an einer Stelle liegen; jedes Warten ist an eine Bedingung geknüpft statt an eine feste Pause, damit die Suite nicht flackert; jeder Test hinterlässt eine Screenshot-Spur und ein maschinell erzeugtes Protokoll, damit ein Lauf nachvollziehbar bleibt; jeder Test verweist auf die Anforderung, die er prüft; und die Suite als Ganzes deckt alle Teststufen ab, statt alles in langsame Browser-Tests zu packen. Diese Disziplin ist unabhängig vom Framework. Wegwerfbar ist nur das Stack-Beiwerk: welche Bibliothek den Browser steuert, welches Verzeichnis die Suite hält, welche Domänen-Selektoren und Routen eine App bereitstellt.

Diese Spezifikation regelt diese wiederverwendbare Disziplin. Sie ist der verallgemeinerte Kern einer projektlokalen E2E-Toolchain (kamerplanters Teststrategie `NFR-008` und Selenium-Standard `NFR-008a`), die den Python/Selenium/pytest-Stack einer App fest verdrahtet hatte, dazu ihr deutsches Anforderungs-ID-Schema (`REQ-NNN`), ihre Routen (`/pflanzen/…`) und ihren Entwicklungsserver auf `http://localhost:5173`. Die Portfolio-Form formuliert die Disziplin framework-neutral als bindenden Kern und legt dann ein konkretes, voll ausgearbeitetes **Referenzprofil** (Selenium + pytest) als normativen Anhang fest, damit ein Python-Projekt eine sofort einsatzbereite Vorlage bekommt, während andere Stacks (Playwright, Cypress) denselben Kern umsetzen.

Operationalisiert wird sie durch drei Agents und einen Skill:

- `e2e-test-generator` (`distribution: plugin`) — erzeugt das Grundgerüst einer spec-konformen E2E-Suite für ein Feature
- `e2e-test-reviewer` (`distribution: plugin`) — prüft eine bestehende Suite gegen diese Spec und repariert minimal-invasiv
- `e2e-result-reviewer` (`distribution: plugin`) — prüft Screenshots und Protokoll eines Laufs visuell gegen die Anforderungs-Specs
- `test-pyramid-check` (Skill) — auditiert die Teststufen-Vollständigkeit eines Features gegen die Stufen-Taxonomie in `spec/project/test-pyramid-foundation/` und die E2E-Disziplin in dieser Spec

**Verhältnis zu `test-case-derivation`.** Jene Spec schloss E2E-Automatisierungscode-Erzeugung/-Review, Teststufen-Audit und Screenshot-Review bewusst aus dem Plugin aus — mit der Begründung, sie seien „zu stack-gekoppelt" und „bleiben projektlokal". Diese Spec revidiert diese Position. Der einzige genannte Grund war die Stack-Kopplung, und ein framework-neutraler bindender Kern mit der konkreten Bibliothek als bloßem Referenzprofil löst genau das auf: Die Disziplin ist portfolio-weit wiederverwendbar, nur das Profil ist stack-spezifisch. `test-case-derivation` wird im Gleichschritt angepasst, damit sich die beiden Specs nicht widersprechen; die Grenze zwischen ihnen verläuft jetzt entlang der Verantwortung (abstrakte Fälle ableiten vs. sie automatisieren, ihr Ergebnis reviewen und auditieren), nicht entlang „geteilt vs. projektlokal".

Leserschaft: Agent-/Skill-Autoren, die diese Toolchain pflegen; QA-Engineers und Entwickler, die E2E-Suites aufsetzen, reviewen oder auditieren; Reviewer, die prüfen, ob eine Suite flacker­frei, rückverfolgbar und stufen-vollständig ist.

## Ziele

- Die Disziplin einer vertrauenswürdigen E2E-Suite einmal framework-neutral festhalten, als bindenden Kern, den jede Suite eines Konsumenten-Projekts erfüllen muss
- Den Kern auf jedem Browser-Automatisierungs-Stack ausführbar halten, indem die konkrete Bibliothek zu einem austauschbaren Referenzprofil herabgestuft wird statt zur Pflicht
- Ein voll ausgearbeitetes, normatives **Selenium-+-pytest**-Referenzprofil mitliefern, damit ein Python-Projekt sofort produktiv ist
- Jede E2E-Suite nachvollziehbar (Screenshot-Checkpoints + maschinelles Protokoll) und rückverfolgbar (jeder Test benennt die geprüfte Anforderung) machen
- Die E2E-Stufe der Verifikation von User-Journeys vorbehalten und das vollständige Stufenmodell samt Taxonomie an `spec/project/test-pyramid-foundation/` delegieren
- Sich an Stack, Pfade, Routen und Sprache des Projekts anpassen, statt eine App vorauszusetzen

## Nicht-Ziele

- Abstrakte, framework-agnostische **Testfälle** aus einem Anforderungsdokument ableiten — das regelt `spec/project/test-case-derivation/` mit dem Agent `test-case-extractor`; diese Spec konsumiert solche Fälle (über ihre TC-IDs), erzeugt sie aber nicht
- Das Unit-/Lint-/Typecheck-Gate ausführen und seine Fehler klassifizieren — das regelt `spec/project/quality-gate/`; diese Spec deckt *Form und Disziplin* der E2E-Stufe ab, nicht das Gate, das die schnellen Stufen in der CI ausführt
- Eine bestimmte Browser-Automatisierungs-Bibliothek vorschreiben: Der Kern ist framework-neutral; Selenium ist das mitgelieferte Referenzprofil, keine Pflicht
- Die Anforderungs-/Spec-Dokumente schreiben oder bearbeiten, auf die eine Suite verweist
- Produktiv-Anwendungscode oder `data-testid`-Hooks in der zu testenden Anwendung erzeugen (die Suite *stützt sich* auf solche Hooks; sie hinzuzufügen ist Anwendungsarbeit). Die Bereitstellung dieser Hooks ist das Provider-seitige Pendant, das `spec/frontend/testability-identifiers/` besitzt
- Die geschäftslesbare **BDD-Szenario-/Spezifikationsebene** (Given-When-Then, Feature-Dateien) autoren, die über diesen Ausführungsmechaniken liegt — besitzt `spec/project/behavior-driven-development/` [R7]; die Steps eines BDD-Szenarios delegieren in die Page Objects, die diese Spec besitzt, statt sie zu wiederholen
- Spezifizieren, wie eine BDD-Step-Definition mit diesen Page Objects integriert wird und von ihnen entkoppelt bleibt (der Verdrahtungs- und Wiederverwendbarkeits-Vertrag): besitzt `spec/project/bdd-page-object-integration/` [R8]; diese Spec besitzt die Page Objects, jene Spec, wie ein BDD-Step sie ohne Rückkopplung konsumiert

## Anforderungen

### Framework-Neutralität

- Die bindenden Anforderungen dieses Abschnitts **MÜSSEN** gegen Fähigkeiten formuliert sein, die jeder Browser-Automatisierungs-Stack bietet (navigieren, lokalisieren, auf-Bedingung-warten, agieren, Screenshot aufnehmen), und **DÜRFEN** keine konkrete Bibliothek, Sprache oder kein konkretes Runner-Werkzeug benennen
- Ein Konsumenten-Projekt **MUSS** angeben, welcher Stack den Kern umsetzt; fehlt die Angabe, **MÜSSEN** Konsumenten und die konsumierenden Agents das Selenium-+-pytest-Referenzprofil unten annehmen
- Jedes konkrete Artefakt, das diese Spec mitliefert (Verzeichnis-Layout, Fixtures, Protokoll-Generator, Beispieltests), gehört zum **Referenzprofil** und **DARF** von einem Projekt auf einem anderen Stack vollständig ersetzt werden, solange der bindende Kern weiter gilt

### Teststufen-Vollständigkeit (die Pyramide)

- Das vollständige Stufenmodell und die geschlossene funktionale Stufen-Taxonomie gehören `spec/project/test-pyramid-foundation/`; diese Spec **DARF** sie **NICHT** wiederholen. Die Suite eines Features **MUSS** gemäß diesem Fundament stufen-vollständig sein — jedes Verhalten auf der niedrigsten Stufe getestet, die Vertrauen gibt — während diese Spec nur Form und Disziplin der **E2E-Stufe** regelt
- Die **E2E-Stufe MUSS** der Verifikation von User-Journeys vorbehalten bleiben, nicht für Logik, die eine Stufe tiefer besser getestet ist; das ist die Regel der niedrigsten-Stufe-die-Vertrauen-gibt des Fundaments, an der Spitze angewandt
- Das charakteristische Fehlermuster ist eine **überbevölkerte Spitze**: Einzelflächen-Assertions auf Feldebene (ein Feld ein-/ausgeblendet, ein Button aktiviert/deaktiviert, ein Leerzustand, ein Label, ein i18n-String, eine Validierungsmeldung, ein Berechnungsergebnis) laufen als langsame Browser-Tests statt als schnelle Component-/Unit-Tests. Eine Suite, die in die Hunderte von E2E-Tests abdriftet, ist ein Symptom dafür; jeder solche Test **MUSS** auf die niedrigste Stufe gedrückt werden, die Vertrauen gibt, sodass E2E ein schlanker Satz stufenübergreifender Journeys bleibt
- Coverage-Governance (Coverage als Leitlinie statt Ziel, Mutationsscore als stärkeres Signal, keine festen stufenübergreifenden Verhältnisse) gehört dem Fundament; diese Spec **DARF** keine numerischen Coverage-Ziele setzen
- Der Skill `test-pyramid-check` **MUSS** die unten definierte **E2E-Stufen-Disziplin** auditieren und pro Feature berichten, ob die E2E-Stufe ihr folgt; seine **Stufen-Vollständigkeits**-Achse (welche Stufen vorhanden, fehlend oder `n/a` sind) ist an `spec/project/test-pyramid-foundation/` [R6] gebunden, das dieses Gebot besitzt, und diese Spec **DARF** es **NICHT** wiederholen

### Page-Object-Kapselung

- Jede UI-Interaktion in einem Test **MUSS** über ein Page Object laufen; Tests **DÜRFEN** die Element-Suchprimitive des Treibers nicht direkt aufrufen — rohe Locator-Aufrufe leben nur innerhalb von Page Objects
- Page Objects **MÜSSEN** sich eine gemeinsame Basis teilen, die die Navigations-, Warte- und Interaktions-Helfer bereitstellt, damit sich ein Test als Absicht liest (öffnen, agieren, prüfen) und nie als rohe Automatisierungs-Mechanik
- Ein Page Object **MUSS** Seitenzustand und Interaktionen als benannte Methoden anbieten; Tests prüfen den zurückgegebenen Zustand, sie greifen nicht ins DOM

### Deterministisches Warten

- Tests **DÜRFEN** keine festen Pausen verwenden, um sich mit der UI zu synchronisieren; jedes Warten **MUSS** als explizite Bedingung formuliert sein (Präsenz, Sichtbarkeit, Klickbarkeit, URL-Wechsel, Ladeindikator verschwunden)
- Eine feste Pause **DARF** nur innerhalb eines Page Objects stehen, nur für ein echt zeitbasiertes Anliegen (eine begrenzte Animation oder ein Debounce), und **MUSS** einen begründenden Kommentar und eine kleine Obergrenze tragen
- Ein **globaler impliziter Wait DARF NICHT** als Synchronisationsmechanismus herangezogen werden. Er koppelt jede Element-Suche an ein verstecktes festes Timeout, verträgt sich nicht-deterministisch mit expliziten Bedingungs-Waits (beide zu vermischen ist selbst ein Anti-Pattern) und macht — am teuersten — jede *negative* Suche (ein absichtlich fehlendes Element, ein Locator-Fallback-Fehlschlag) für das volle Timeout blockierend. Setze den impliziten Wait auf null (oder eine kleine Untergrenze) und formuliere jedes Warten explizit; ein großer impliziter Wait ist die mit Abstand häufigste versteckte Ursache einer langsamen Suite

### Locator-Strategie

- Locators **MÜSSEN** einer Robustheits-Hierarchie folgen, das Stabilste zuerst: ein dedizierter Test-Hook (z. B. `data-testid`) → Element-ID → semantischer/Rollen-Selektor → CSS → XPath als letztes Mittel
- Positionsbasiertes XPath (`//div[3]/span[2]`) **DARF** nicht verwendet werden; Selektoren **MÜSSEN** kosmetische Markup-Änderungen überstehen
- Ein Selektor, der allein auf einer strukturellen oder ARIA-Rolle baut (eine nackte Dialog- oder Listbox-Rolle, ein nackter Tabellen- oder Zellen-Selektor), **DARF** nicht ungescoped verwendet werden: Komponentenbibliotheken vergeben dieselbe Rolle an unterschiedliches Chrome an unterschiedlichen Breakpoints; ein Rollen-Selektor wird daher auf seinen besitzenden Container eingegrenzt oder durch einen dedizierten Test-Hook ersetzt; der Responsive-Hazard-Katalog hinter dieser Regel ist `spec/project/e2e-test-stability/` §G

### Screenshot-Checkpoints

- Jeder Test **MUSS** mindestens einen Screenshot aufnehmen und **MUSS** die Standard-Checkpoints aufnehmen, wo sie zutreffen: Seitenaufbau, vor einer signifikanten Aktion, danach und jeder sichtbare Fehler-/Validierungszustand; ein Fehler-Screenshot **MUSS** vom Harness bei jedem Test-Fehlschlag automatisch aufgenommen werden
- Screenshot-Namen **MÜSSEN** mit der TC-ID des Tests beginnen und mit einer lesbaren Beschreibung des sichtbaren Zustands enden, damit ein Screenshot allein an seinem Dateinamen rückverfolgbar ist

### Testprotokoll (Audit-Trail)

- Ein Lauf **MUSS** ein maschinell erzeugtes, lesbares Protokoll (Vorgabe: Markdown) ausgeben können, das Lauf-Metadaten (mindestens Zeitstempel, Commit, Branch, Browser/Laufzeitumgebung), eine Pass-/Fail-/Skip-Zusammenfassung, Ergebnisse pro Test, die Anforderungsabdeckung und die Screenshot-Galerie mit Beschreibungen festhält
- Die Protokoll-Ausgabe **MUSS** über ein Lauf-Flag aktiviert werden und **MUSS** an einen zeitgestempelten, git-ignorierten Ort geschrieben werden, damit Protokolle als Historie anwachsen, ohne in die Versionskontrolle zu geraten
- Das Protokoll **MUSS** pro Anforderung berichten, wie viele Tests ihr zugeordnet sind

### Test-Marker und Suiten

- Jeder Test **MUSS** mindestens einen Marker tragen, der ihn klassifiziert (mindestens eine Smoke-Stufe für „lädt ohne Absturz" und eine Kernverhalten-Stufe), damit ein Projekt schnelle Teilmengen (`smoke`) unabhängig von der vollen Suite ausführen kann

### Assertions und Vorbedingungen

- Jede Assertion **MUSS** eine beschreibende Fehlermeldung tragen, die die TC-ID und den beobachteten Wert enthält; leere oder tautologische Assertions (`assert True`, `assert page is not None`) sind verboten
- Eine fehlende Vorbedingung (nicht vorhandene Seed-Daten) **MUSS** zu einem expliziten, begründeten Skip führen — nie zu einem stillen vorzeitigen Return, der einen Test bestehen lässt, ohne etwas zu prüfen
- Vom Test erzeugte Daten **MÜSSEN** ein eindeutiges Suffix verwenden, um über Läufe hinweg isoliert und reproduzierbar zu bleiben; Seed-Daten mit Session-Geltungsbereich **MÜSSEN** idempotent sein (vor dem Anlegen prüfen)
- Vorbedingungen **MÜSSEN** über den schnellsten zuverlässigen Weg hergestellt werden — einen geseedeten API-Aufruf oder ein Fixture — **nicht** über ein Durchklicken der UI. Ein Test treibt durch den Browser nur die Interaktion, die er prüft; das Herstellen von Vorbedingungs-Zustand (Konten, Entitäten, Navigation) über die UI vervielfacht die Laufzeit und koppelt unbeteiligte Flows in jeden Test

### Spec-Rückverfolgbarkeit

- Jeder Test **MUSS** in seinem Docstring/seinen Metadaten die TC-ID benennen, die er umsetzt, sowie den Anforderungs-/Spec-Fall, auf den er verweist; die TC-IDs der Suite und die der Anforderung **DÜRFEN** sich in der Nummerierung unterscheiden — dann **MUSS** eine explizite Zuordnung die Verbindung herstellen
- Die Rückverfolgbarkeit **MUSS** in den Test-Artefakten selbst getragen werden (Docstrings, Namen, Protokoll-Abdeckungstabelle); ein separater maschinenlesbarer Rückverfolgbarkeits-Index **DARF** nicht ausgegeben werden, bevor ein nachgelagerter Leser das benötigte Schema festlegt

### Selenium-+-pytest-Referenzprofil (normativ)

Dieses Profil ist die bindende Umsetzung des Kerns für Python-Projekte und die Vorgabe, die die konsumierenden Agents annehmen, wenn kein anderer Stack angegeben ist. Ein Projekt auf einem anderen Stack ersetzt diesen Abschnitt vollständig, erfüllt aber weiter den Kern oben.

- Die Suite **MUSS** unter `tests/e2e/` liegen, mit: `conftest.py` (Session-Fixtures, CLI-Optionen, idempotente Seed-Daten, Marker-Registrierung), `protocol_plugin.py` (dem Protokoll-Generator), `requirements.txt`, einem `pages/`-Paket mit `base_page.py` plus einem `<entity>_<view>_page.py` pro Seite und `test_<req>_<thema>.py`-Testmodulen, gruppiert nach Anforderung
- Das Browser-Fixture **MUSS** Session-Geltungsbereich haben, standardmäßig auf Headless-Chrome laufen, Firefox über eine `--browser`-Option unterstützen und die Optionen `--base-url` und `--generate-protocol` bereitstellen; die Base-URL **MUSS** eine konfigurierbare Option sein, nie ein fest verdrahteter Host. Ein Projekt, das auf ein **Browser-Fixture pro Test (Function-Scope)** ausweichen muss, um Zustands-Verschleppung zwischen Tests zu vermeiden, **MUSS** den Grund dokumentieren und die zusätzliche Session-Allokation pro Test als bekannte Kosten behandeln, die anderswo auszugleichen sind — durch weniger, ausschließlich journey-basierte E2E-Tests und API-geseedete Vorbedingungen statt UI-Durchklicken
- `BasePage` **MUSS** die Warte-/Interaktions-Helfer bereitstellen (`navigate`, `wait_for_element`, `wait_for_element_visible`, `wait_for_element_clickable`, `wait_for_loading_complete`, `wait_for_url_contains`, framework-kompatibles Leeren/Füllen von Feldern); die Marker `smoke`, `core_crud`, `requires_auth` **MÜSSEN** registriert sein
- Die neben dieser Spec mitgelieferten Referenz-Templates (`templates/`) sind der kanonische Ausgangspunkt nach Gen-Standard; `e2e-test-generator` **MUSS** sie als anzupassendes Grundgerüst behandeln, und `e2e-test-reviewer` **MUSS** sie als Konformitäts-Basislinie behandeln

### Konsumierende Agents und Skill

- `e2e-test-generator` **MUSS** diese Spec zitieren, gegen den angegebenen Stack aufsetzen (mit dem Referenzprofil als Vorgabe), data-testid-priorisierte Locators, Screenshot-Checkpoints, Marker und Protokoll-Integration verdrahten und rohe Locator-Aufrufe ausschließlich in Page Objects halten
- `e2e-test-reviewer` **MUSS** eine bestehende Suite gegen den Kern dieser Spec (und das Referenzprofil, wenn das der Stack ist) prüfen, ein checklistenbasiertes Konformitäts-Urteil berichten und nur minimale, gezielte Korrekturen anwenden statt neu zu generieren
- `e2e-result-reviewer` **MUSS** Protokoll und Screenshots eines Laufs lesen und sie visuell gegen die Anforderungs-/TC-Specs prüfen und priorisierte Befunde zurückgeben; er **DARF** keinen Code und keine Tests bearbeiten (read-only)
- `test-pyramid-check` **MUSS** die Stufen-Vollständigkeit gegen `spec/project/test-pyramid-foundation/` und die E2E-Disziplin gegen diese Spec auditieren und einen Lückenbericht zurückgeben; er **DARF** keine Tests erzeugen oder verändern

## Akzeptanzkriterien

- [ ] Jede bindende Anforderung außerhalb des Referenzprofil-Abschnitts ist formuliert, ohne eine konkrete Bibliothek, Sprache oder ein Runner-Werkzeug zu benennen
- [ ] Das Selenium-+-pytest-Referenzprofil ist vollständig genug, dass ein Python-Projekt allein aus den mitgelieferten Templates eine konforme Suite aufsetzen kann
- [ ] Eine aufgesetzte Suite leitet jede UI-Interaktion über Page Objects, verwendet nur bedingungsbasiertes Warten, folgt der Locator-Hierarchie und trägt Marker, TC-ID-Docstrings und beschreibende Assertions
- [ ] Ein Lauf kann ein zeitgestempeltes, git-ignoriertes Markdown-Protokoll mit Metadaten, Zusammenfassung, Abdeckung pro Anforderung und einer beschriebenen Screenshot-Galerie ausgeben
- [ ] Jeder Test benennt die umgesetzte TC-ID und den Anforderungsfall, auf den er verweist; abweichende Nummerierung wird durch eine explizite Zuordnung überbrückt
- [ ] `test-pyramid-check` markiert pro Feature E2E-Disziplin-Verstöße gegen diese Spec, während sein Bericht über vorhandene/fehlende Stufen an `test-pyramid-foundation` gebunden ist
- [ ] `e2e-result-reviewer` läuft read-only und erzeugt priorisierte Befunde mit Bezug zu Anforderungs-/TC-IDs
- [ ] Jeder der drei Agents und der Skill zitiert diese Spec, und jede `description` grenzt ihn von den anderen sowie von `test-case-derivation` und `quality-gate` ab
- [ ] `test-case-derivation/{en,de}.md` widerspricht dieser Spec nicht mehr: Die Grenze zur E2E-Automatisierung verläuft entlang der Verantwortung, nicht entlang „geteilt vs. projektlokal"

## Referenzen

- [R1] Agent-Autorenregeln, denen die drei Agents folgen: `spec/claude/agent-management/`
- [R2] Skill-Autorenregeln und die Skill-vs-Agent-Entscheidung: `spec/claude/skill-management/`, `spec/claude/skill-vs-agent/`
- [R3] Abstrakte Testfall-Ableitung, abgegrenzt gegen diese Spec: `spec/project/test-case-derivation/`
- [R4] Ausführungs-Gate der schnellen Stufen, abgegrenzt gegen diese Spec: `spec/project/quality-gate/`
- [R5] Page Object Model (Hintergrund-Methodik): <https://martinfowler.com/bliki/PageObject.html>
- [R6] Test-Pyramide-Fundament (Stufenmodell und Taxonomie, auf denen die E2E-Stufe dieser Spec aufsitzt; Eigentümer von Stufen-Vollständigkeit und Coverage-Governance): `spec/project/test-pyramid-foundation/`
- [R7] `spec/project/behavior-driven-development/`: besitzt die BDD-Szenario-/Spezifikationsebene über diesen Ausführungsmechaniken; ihre Szenario-Steps delegieren an die Page Objects dieser Spec
- [R8] `spec/project/bdd-page-object-integration/`: besitzt den BDD-zu-Page-Object-Integrations- und Entkopplungs-Vertrag; die Page Objects dieser Spec werden dort konsumiert, ohne von der BDD-Ebene abzuhängen
- [R9] `spec/project/e2e-test-stability/`: das Laufzeit-Stabilitäts-Komplement zu diesem Suite-Form-Standard; dessen §G besitzt den Responsive-/Viewport-Hazard-Katalog, gegen den die Ungescoped-Rollen-Locator-Regel schützt
- [R10] `spec/project/test-falsifiability/`: die tier-übergreifende Falsifizierbarkeits-Taxonomie; sie generalisiert das Tautologie-Assertion-Verbot und die Silent-Early-Return-Regel dieser Spec als ihre T2-Kategorie

## Offene Fragen

- Ob ein zweites, gleichermaßen normatives Playwright-/TypeScript-Referenzprofil mitgeliefert werden sollte, sobald ein Portfolio-Projekt es braucht, oder ob das Selenium-Profil plus der framework-neutrale Kern als Leitfaden für einen Nicht-Python-Stack genügt. Vorläufige Vorgabe, bis ein Konsument die Frage erzwingt: nur das Selenium-Profil mitliefern und für andere Stacks auf den Kern bauen.
