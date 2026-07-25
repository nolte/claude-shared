# Frontend-Source-Code-Review

Status: draft

## Kontext

`spec/project/source-code-review/` definiert das ganzheitliche Senior-Engineer-Review: einen sprachagnostischen Kern aus zehn Dimensionen (D1–D10), eine Tooling-first-Regel, je Programmiersprache ein Sprachprofil und einen Report-Vertrag, dessen disjunkte Work-Packages an Spezialisten geroutet werden. Ihre eigenen Offenen Fragen benennen das Frontend bereits als wahrscheinlichstes zweites Profil.

Frontend-Code durchbricht dieses Modell an einer Stelle. Die Profilachse der Kern-Spec ist die **Sprache**, aber was ein browsergehostetes Component schwer reviewbar macht, ist nicht TypeScript — es ist die Oberfläche. Ein Component besitzt einen DOM-Baum, der per Tastatur und assistiver Technologie bedienbar bleiben muss, eine Render-Schleife, deren Kosten der Nutzer unmittelbar spürt, eine Vertrauensgrenze, die *außerhalb* des Prozesses liegt, in dem es läuft, jeden Text, den der Nutzer liest, und Design-Entscheidungen, die als Style-Werte kodiert sind. Ein Review, das auf eine Component-Datei nur D1–D10 anwendet, geht an all dem vorbei: am verschluckten `catch`, das einen Spinner ewig drehen lässt; an der Rabattregel, die im Client berechnet und vom Server nie nachgerechnet wird; am `div` mit Click-Handler, das keine Tastatur erreicht; am Hex-Farbwert, der die Design-Tokens umgeht, die das Projekt bereits mitliefert.

Diese Spec ist die **Frontend-Erweiterung** des Kern-Reviews. Sie legt ein Dimensions-Overlay (F1–F11) über D1–D10, definiert neben den Sprachprofilen des Kerns einen Framework-Profil-Vertrag, verengt die Review-Einheit von der Datei auf den **Component-Slice** und zieht eine harte Grenze zum UX-Review: Dieses Review beurteilt Code, nie Geschmack. Es ist die Grundlage eines Review-Prozesses, der spezialistenfertige Findings mit Umsetzungsvorschlägen liefert — genau so, wie es das Python-Review für serverseitigen Code tut.

Leser: Autoren des Frontend-Reviewer-Agents und des dispatchenden Skills; Reviewer, die den Report konsumieren; Frontend-Entwickler, die das Review vor einem Release oder nach einem gelandeten Feature ausführen.

## Ziele

- Das Kern-Review erweitern statt forken: Jede Kern-Regel (Tooling-first, Severity-Vokabular, Finding-Attribution, disjunkte Work-Packages, Read-only-Reviewer) gilt wortgleich weiter, und diese Spec ergänzt nur, was die Oberfläche erzwingt
- **Geschäftslogik im Client** zu einer präzise definierten Dimension machen, die „richtiger Client, falsche Schicht" von „darf im Client überhaupt nicht laufen" trennt
- **Frontend-Fehlerbehandlung** zu einer erstklassigen Dimension mit dem Severity-Floor des Kerns machen, denn ein verschluckter Fehler im Browser erzeugt keinen Crash, keinen Exit-Code und keinen roten Health-Check — nur ein Bedienelement, das stillschweigend nichts tut
- Die Review-Einheit als **Component-Slice** definieren, damit ein Component nie ohne seine Hooks, seine Styles und seine Tests reviewt wird
- Eine explizite, operativ nutzbare Grenze zum reinen UX-Review ziehen, in beide Richtungen
- Einen Framework-Profil-Vertrag definieren, mit React und TypeScript als Referenzprofil, damit weitere Frameworks die Spec erweitern, ohne das Overlay anzufassen
- Findings erzeugen, deren Behebung ein **Umsetzungsvorschlag** ist, den ein Spezialist ausführen kann — geroutet und entlang der Slice-Grenzen geschnitten, damit die Behebung parallel läuft

## Nicht-Ziele

- Die Kern-Review-Dimensionen selbst (D1–D10), die Tooling-first-Regel, das Severity-Vokabular und den Work-Package-Vertrag — gehören `spec/project/source-code-review/` und gelten hier unverändert
- UX-, Usability-, Visual-Design- und Content-Qualitätsurteile — siehe §Abgrenzung zum UX-Review; gehören `spec/frontend/webview-ui-optimization/` §„UX and native feel" mit dem Skill `webview-ui-optimize` und dem Agent `frontend-usability-optimizer`
- Tiefes WCAG-Konformitäts-Audit, Kontrastmessung, Zielgrößen-Bewertung und Tests mit assistiver Technologie — gehören `spec/frontend/webview-ui-optimization/` §Accessibility; dieses Review meldet den Code-Defekt und routet die Konformitätsfrage weiter
- Gemessene Laufzeit-Performance: Core-Web-Vitals-Schwellen, Bundle-Size-Budgets, Profiling — gehören `spec/frontend/webview-ui-optimization/` §„Performance and rendering"; dieses Review sieht nur, was der Quelltext zeigt
- Tiefes Client-Security-Audit, Content Security Policy und HTTP-Security-Header — gehören `spec/project/code-security-audit/` und `spec/frontend/webview-ui-optimization/` §„Security and sandboxing"; Frontend-Security-Findings sind hier gemeldete Floors, die weitergeroutet werden
- Übersetzungsschlüssel-Abdeckung und Locale-Vollständigkeit — gehören `spec/project/i18n-completeness/`
- Der Test-Identifikator-Vertrag selbst — gehört `spec/frontend/testability-identifiers/`
- Einzel-Stufen-Testkonformität (Component-, Integrations-, E2E-Checklisten) — gehören den `spec/project/test-tier-*/`-Specs und ihren Reviewern
- Mechanisches Tooling ausführen (`spec/project/quality-gate/`) und Fixes anwenden: Das Review findet, klassifiziert, schlägt vor und routet; Spezialisten beheben

## Anforderungen

### Verhältnis zum Kern-Review

- **MUSS** ausschließlich zusammen mit `spec/project/source-code-review/` angewandt werden: Ein Frontend-Review ist das Kern-Review **plus** dieses Overlay, nie ein zweites, konkurrierendes Review, das Kern-Regeln in Frontend-Worten wiederholt
- **DARF KEINE** Kern-Regel duplizieren; wo eine Frontend-Regel eine Kern-Dimension schärft, benennt sie die erweiterte Kern-Dimension (F4 erweitert D4, F6 erweitert D7, F11 erweitert D6, F9 erweitert D10)
- **MUSS** jedes Finding mit genau **einer** Dimensions-ID taggen, entweder einer Kern-`D`-ID oder einer Frontend-`F`-ID; passen beide, gewinnt die **F**-ID als die spezifischere, und das Finding benennt die erweiterte Kern-Dimension
- **MUSS** den Kern-§Report-Vertrag unverändert übernehmen: das Severity-Vokabular aus `spec/claude/review-plan/` §Severity scale (Critical / Warning / Suggestion / Info, wortgleich in Title Case), je Finding `file:line`, den `production`- oder `test`-Marker, das Confirmed-oder-Suspected-Flag und den §Work-Packages-Abschnitt mit disjunkten Dateimengen und Routing-Zielen
- **MUSS** den Kern-§Reviewer-Vertrag unverändert übernehmen: Der Reviewer ist strikt read-only, wendet keine Fixes an und fügt keine Suppression-Kommentare ein
- **MUSS** die Tooling-first-Regel des Kerns übernehmen: Ein Finding, das der konfigurierte Linter, Formatter, Style-Linter, Accessibility-Linter oder Type-Checker des Projekts bereits meldet, ist kein Review-Finding, und eine fehlende Baseline ist genau **ein** Einführungs-Finding statt handgemeldeter mechanischer Verstöße

### Review-Einheit: der Component-Slice

- **MUSS** den **Component-Slice** als Review-Einheit behandeln: die Component-Datei oder -Dateien, die von ihr besessenen Hooks oder Composables, die ko-lokierten Styles, die Tests und Fixtures oder Stories sowie die referenzierten Übersetzungsschlüssel. Ein Component ohne seine Tests zu reviewen ist ein unvollständiges Review, kein teilweises
- **MUSS** die Frontend-Oberfläche aus dem Repository selbst ermitteln — Package-Manifest, Framework- und Bundler-Konfiguration, Router-Setup, Style-Pipeline, Übersetzungsschicht, Datenzugriffsschicht — statt ein Layout anzunehmen
- **MUSS** im Report-Header die vier Baselines festhalten, gegen die das Overlay urteilt: das erkannte **Framework-Profil**, die **Design-Token- oder Theme-Quelle**, die **Internationalisierungsschicht** und die **Datenzugriffsschicht**. Ein Finding unter F1, F7 oder F10, das ohne festgehaltene Baseline gefällt wurde, ist nicht reproduzierbar
- **MUSS** die Gleichrangigkeitsregel des Kerns beibehalten: Testcode trägt den `test`-Marker und dieselbe Sorgfalt wie Produktivcode
- **SOLLTE** bei engerem Ziel benennen, welche Slices reviewt und welche bewusst ausgelassen wurden

### F1 — Schichtung und Geschäftslogik im Client

Die Dimension unterscheidet drei Klassen, und ein Finding **MUSS** benennen, zu welcher es gehört, weil sich die Behebung jeweils unterscheidet.

- **Klasse 1 — falsch platzierte Logik im Component.** Eine Fachregel, Berechnung, Zustandsautomaten-Transition, Zuordnung oder Orchestrierung, die im Render-Rumpf oder im Markup steckt statt in einem Hook, einem Service oder einem framework-freien Fachmodul. Die Behebung ist eine Extraktion, die die Zielschicht benennt.
- **Klasse 2 — autoritative Regeln clientseitig implementiert.** Eine Entscheidung, die der Server dem Client nicht glauben darf: Preise, Rabatte, Steuern, Berechtigungs- und Rechteprüfungen, Kontingente, Anspruchsvoraussetzungen oder jede Regel, deren Ergebnis das Backend konsumiert. Die Severity hängt an der Durchsetzungsfrage: Setzt der Server dieselbe Regel unabhängig durch, ist die Client-Kopie zugunsten der Reaktionsfähigkeit legitim und das Finding ein **Duplizierungs- und Drift**-Finding unter F4; ist das Client-Ergebnis die einzige Durchsetzung oder übernimmt der Server es ohne Nachrechnen, ist das Finding mindestens **Warning** und bei Bestätigung **Critical** und wird unter F9 an `spec/project/code-security-audit/` geroutet.
- **Klasse 3 — Backend-artige Arbeit im Client.** Daten aus mehreren Endpunkten im Client joinen oder aggregieren, einen vollständigen Datensatz laden, um ihn lokal zu sortieren, zu filtern oder zu paginieren, oder Request-Fan-out je Listeneintrag, den ein einzelner Endpunkt bedienen sollte. Die Behebung benennt die Endpunkt- oder Schichtänderung.

Weitere F1-Regeln:

- **MUSS** direkte Netzwerkaufrufe aus einem Component heraus (oder aus markup-gebundenen Handlern) melden, wenn das Projekt eine Datenzugriffsschicht hat, und diese Schicht als Ziel benennen
- **MUSS** Transportformate melden, die durch die UI durchschlagen — rohe API-Payloads, die ungemappt in Components gefädelt werden —, wenn das Projekt eine Anti-Corruption- oder Mapping-Schicht deklariert
- **MUSS** Server-Zustand melden, der in einen Client-State-Store kopiert wird, wenn das Projekt einen Server-State-Cache hat, gemäß der Besitzregel: Daten, die der Server besitzt, gehören in die Query- oder Cache-Schicht, Daten, die der Client besitzt, in den Client-State
- **DARF** Präsentationslogik **NICHT** als Geschäftslogik klassifizieren: Anzeigeformatierung, bedingtes Rendern, Layout-Verzweigungen und View-Model-Aufbereitung sind Aufgabe des Components
- **DARF KEINE** bestimmte Architektur einfordern. Die vom Repository deklarierte Schichtung gewinnt; deklariert das Repository keine, benennt der Reviewer die angenommene Schichtung und meldet Schichtungs-Findings als **suspected**

### F2 — Fehler- und Async-Zustandsbehandlung

Der Severity-Floor aus Kern-D1 für verschluckte und fehlende Fehlerbehandlung gilt wortgleich: eine bestätigte Instanz ist **Critical**, eine vermutete mindestens **Warning**, und sie landet immer in den Work-Packages. Diese Dimension benennt die Frontend-Ausprägungen dieses Floors.

- **MUSS** einen Request melden, dessen HTTP-Status nie geprüft wird, wo die Client-API bei Fehlerstatus auflöst statt zu rejecten, sodass ein `404` oder `500` still den Erfolgspfad weiterläuft
- **MUSS** einen Rejection-Handler melden, der weder einen nutzersichtbaren Zustand erzeugt noch propagiert noch an die Fehlersenke des Projekts meldet — die Browser-Ausprägung des No-Gos „verschluckter Fehler" aus dem Kern
- **MUSS** einen asynchronen oder Event-Handler-Fehlerpfad melden, der sich auf eine Render-Error-Boundary verlässt, die ihn strukturell nicht fangen kann
- **MUSS** einen Routen- oder Widget-Teilbaum ohne darüberliegende Error-Boundary melden, bei dem ein Render-Fehler die gesamte Anwendung leert, und „eine Boundary an der Anwendungswurzel" als eben dieses Finding werten statt als Abdeckung
- **MUSS** eine Verletzung des **Drei-Zustands-Vertrags** melden: Jede asynchrone Oberfläche rendert einen Pending-Zustand, einen Fehlerzustand mit Wiederherstellungsangebot und einen Leerzustand, jeweils unterscheidbar vom Erfolg. Ein fehlender Pending- oder Leerzustand allein ist **Warning**; ein fehlender Fehlerpfad ist der Critical-Floor oben
- **SOLLTE** ein Zustandsmodell empfehlen, das widersprüchliche Kombinationen unrepräsentierbar macht, wenn unabhängige boolesche Flags sie zulassen — gleichzeitig ladend und fehlerhaft, oder abgeschlossen ohne Daten und ohne Fehler
- **MUSS** einen laufenden Request ohne Veralterungs- oder Abbruchschutz melden, wenn sich die Eingaben ändern oder das Component unmounten kann, sodass eine späte Antwort eine neuere überschreibt
- **MUSS** Fehlerausgaben melden, die rohen Exception-Text, Stacktraces oder Backend-Interna an den Nutzer durchreichen
- **MUSS** ein optimistisches Update ohne Rollback im Fehlerfall melden sowie eine Mutation, deren Fehlschlag den gerenderten Zustand inkonsistent zum Server zurücklässt
- **SOLLTE** unbegrenzte Retries ohne Backoff melden sowie pauschale Retries auf Client-Fehlerantworten, die bei Wiederholung nicht erfolgreich sein können
- **SOLLTE** eine Anwendung ohne globalen Handler für nicht gefangene Fehler und nicht behandelte Rejections melden; der Zwei-Listener-Boden und seine Senke gehören `spec/project/error-tracking/` §„Integration contract" und `spec/project/monitoring-observability/` §„Frontend observability", das Finding benennt also die Lücke und routet weiter, statt ein SDK vorzuschreiben
- **MUSS** „Fehler erreichen die Observability-Senke nie" als D10-Route-out an `spec/project/error-tracking/` (der Tracker-seitige Vertrag, dessen Regel zur expliziten Erfassung an der Entscheidungsstelle das Laufzeit-Gegenstück zu diesem Floor ist) und `spec/project/monitoring-observability/` weiterreichen, statt es hier zu vertiefen

### F3 — Component-Design und öffentliche API

- **MUSS** ein Component melden, das Rendering, Geschäftslogik, Seiteneffekte und sämtliche UI-Zustände zugleich trägt, und die zu extrahierende Verantwortung benennen
- **DARF** ein Größen-Finding **NICHT** allein auf Zeilenzahl stützen: Ein Größen-Finding benennt die Verantwortung, die das Component verlassen sollte
- **SOLLTE** konfigurationsgetriebene Components melden, die eine Komposition besser ausdrückt, boolesche Prop-Explosion, wo Varianten oder Children hingehören, sowie Props, die durch mehrere Schichten gefädelt werden, die sie nicht konsumieren
- **SOLLTE** einen geteilten Zustandsmechanismus melden, wo lokaler Zustand genügt, und lokalen Zustand, wo der geteilte Mechanismus des Projekts der deklarierte Ort ist
- **MUSS** inkohärentes Controlled-/Uncontrolled-Verhalten auf einer Eingabeoberfläche melden sowie Prop-Namen, die die Implementierung durchscheinen lassen statt den Vertrag zu beschreiben
- **MUSS** instabile Listen-Identitäten melden — positionsbasierte Keys auf einer Collection, die umsortiert, einfügt oder löscht — sowie identitätsgetriebenes Remounten als Ersatz für Zustandsdesign
- **SOLLTE** unbekannte Props melden, die auf Host-Elemente gespreadet werden, sowie imperative DOM-Manipulation, wo deklarativer Zustand dasselbe ausdrückt
- **MUSS** ein neu eingeführtes Component melden, das eines aus der geteilten Component-Schicht des Projekts dupliziert, und beide benennen

### F4 — Frontend-Fachwissens-Duplizierung (erweitert D4)

Die Kern-D4-Regel gilt: Es geht um **semantische** Duplizierung, nicht um textuelle Ähnlichkeit, jede Stelle wird benannt, und ein Single-Source-of-Truth-Ort wird vorgeschlagen. Die Frontend-Achsen sind:

- Validierungsregeln, die zwischen Client und Server dupliziert sind, ohne gemeinsames Schema oder vertragsgenerierte Quelle. Der Vorschlag benennt die gemeinsame Quelle oder den Generierungsschritt, nie „synchron halten"
- Fachkonstanten, Aufzählungen und Status-zu-Label-Zuordnungen, die im Client neu deklariert statt aus dem API-Vertrag abgeleitet werden
- Dieselbe Formatierungs- oder Beschriftungsregel — Währung, Einheiten, Schwellwerte, Statustexte — in mehr als einem Component implementiert
- Datenabruf-, Caching- und Invalidierungslogik, die je Component neu implementiert wird, obwohl eine Query-Schicht existiert
- Design-Werte, die dupliziert statt über ein Token referenziert werden (die Styling-Seite dieser Klasse ist F7; dort einordnen, wenn es um die Token-Umgehung geht, hier, wenn dieselbe *Regel* zweimal kodiert ist)

### F5 — Rendering-, Effekt- und Reaktivitäts-Korrektheit

- **MUSS** Zustand melden, der aus vorhandenen Props oder vorhandenem Zustand ableitbar ist und gespeichert statt während des Renderns berechnet wird
- **MUSS** Effekte melden, die Logik tragen, die in einen Event-Handler gehört, sowie Effektketten, deren einziger Zweck es ist, einander über Zustand auszulösen
- **MUSS** Zustandsrücksetzung über einen Effekt melden, wo der Identitätsmechanismus des Frameworks sie ausdrückt
- **MUSS** fehlendes Cleanup melden, das leakt: Event-Listener, Timer, Subscriptions, Observer und erzeugte, nie freigegebene Objekt-URLs
- **MUSS** Seiteneffekte in der Render-Phase melden — mutierter Modulzustand, geschriebener Storage oder DOM — statt im zuständigen Effekt oder Handler
- **SOLLTE** unvollständige Dependency-Mengen melden sowie solche, die von bei jedem Render neu erzeugten Identitäten abhängen, sofern der Linter des Projekts das nicht bereits abdeckt
- **MUSS** Render-Ausgaben melden, die für dieselben Eingaben nicht deterministisch sind, wenn das Projekt serverseitig rendert oder hydriert — einschließlich ungeschützter Zugriffe auf browser-exklusive globale Objekte
- **SOLLTE** einen Effekt melden, der unter der Doppelausführung im Entwicklungsmodus des Frameworks nicht idempotent ist

### F6 — Frontend-Performance im Quelltext (erweitert D7)

Diese Dimension ist auf das begrenzt, was der Quelltext zeigt. Gemessene Budgets werden an `spec/frontend/webview-ui-optimization/` geroutet.

- **MUSS** Request-Wasserfälle und Request-Fan-out je Eintrag melden, die die Datenschicht bündeln oder der Endpunkt bedienen sollte
- **MUSS** eine vollständig gerenderte Collection melden, wenn die Datenmenge Virtualisierung oder Pagination zur etablierten Antwort macht
- **SOLLTE** eine fehlende Route-Level-Aufteilung auf einer großen Route melden, Gesamtbibliotheks- oder Barrel-Importe, die Tree-Shaking aushebeln, sowie eine schwere Abhängigkeit für einen trivialen Zweck (die Abhängigkeitswahl-Seite ist D9)
- **SOLLTE** teure Ableitungen melden, die bei jeder Interaktion neu berechnet werden, obwohl sich die Eingabe weit seltener ändert
- **MUSS** das **Memoisierungs-Urteil abhängig von der Build-Konfiguration des reviewten Repositories** fällen:
  - Aktiviert das Projekt compilerbasierte automatische Memoisierung, ist handgeschriebene Memoisierung kein Finding, außer sie ist falsch, verdeckt einen echten Fehler oder hebelt den Compiler aus
  - Aktiviert es sie nicht, ist fehlende Memoisierung nur mit benannten, plausiblen Kosten ein Finding — eine große Collection, eine nachweislich teure Ableitung oder eine Abhängigkeit, die referenziell stabil bleiben muss
  - **DARF** in keine der beiden Richtungen ein pauschales Memoisierungs-Finding erhoben werden, und hinzugefügte Memoisierung **DARF NICHT** ohne diese benannten Kosten als Verbesserung dargestellt werden

### F7 — Styling und Design-System-Konformität

- **MUSS** hartkodierte Design-Werte melden, wo das Projekt Tokens oder ein Theme mitliefert: Farben, Abstände, Schriftgrößen und -schnitte, Radien, Schatten, Z-Index-Werte, Breakpoints und Bewegungsdauern
- **MUSS** Z-Index-Werte außerhalb einer deklarierten Skala melden sowie responsive Regeln gegen ad hoc gewählte Pixelwerte statt gegen die Breakpoint-Skala des Projekts
- **SOLLTE** Spezifitäts-Eskalation und erzwungene Prioritätsdeklarationen melden, mit denen das System ausgehebelt wird, Style-Regeln, die ihrem Scoping-Mechanismus in den globalen Namensraum entkommen, sowie toten oder ungenutzten Style-Code
- **SOLLTE** einen duplizierten Style-Block melden, den ein vorhandenes Token, eine Variante oder ein geteiltes Component bereits ausdrückt
- **DARF NICHT** beurteilen, ob ein gewählter Wert der *richtige* Wert ist: Das ist Design. Diese Dimension besitzt allein die Frage, ob der Code das System umgeht, das das Projekt bereits hat

### F8 — Im Code sichtbare Accessibility-Defekte

Begrenzt auf das, was ein Reviewer aus dem Quelltext entscheidet; die Konformitätsfrage wird weitergeroutet.

- **MUSS** ein nicht-semantisches Element als Bedienelement melden — ein Click-Handler auf einem generischen Element ohne Rolle, ohne Fokussierbarkeit und ohne Tastaturbehandlung —, wo ein natives Element Semantik und Verhalten bereits mitbringt
- **MUSS** eine Rolle melden, die ohne die versprochene Tastaturinteraktion und Zustandsverwaltung vergeben wurde, sowie Rollen oder Attribute, die der nativen Semantik ihres Elements widersprechen
- **MUSS** ein Element melden, das vor assistiver Technologie verborgen oder als präsentational markiert ist und dennoch fokussierbar bleibt
- **MUSS** Formularelemente ohne programmatisches Label melden, Validierungsmeldungen ohne programmatische Zuordnung zu ihrem Element, reine Icon-Bedienelemente ohne zugänglichen Namen sowie Bilder ohne getroffene Alternativtext-Entscheidung
- **SOLLTE** statisch entscheidbare Fokus-Defekte melden: einen Dialog, der Fokus weder setzt noch zurückgibt, einen Routenwechsel, der den Fokus stranden lässt, einen positiven Tab-Index sowie einen entfernten Fokusindikator ohne Ersatz
- **SOLLTE** asynchrone Statusänderungen melden, die nur sehenden Nutzern angekündigt werden, ohne Live-Region
- **MUSS** Kontrastverhältnisse, Konformitätsstufe, Zielgrößen und Erfahrungen mit assistiver Technologie an `spec/frontend/webview-ui-optimization/` §Accessibility routen, statt hier darüber zu urteilen
- **DARF NICHT** melden, was der Accessibility-Linter des Projekts bereits meldet (Tooling-first)

### F9 — Client-Vertrauensgrenze und Security-Floors (erweitert D10)

Die Kern-D10-Regel gilt: Diese Findings werden **gemeldet und geroutet**, nie hier vertieft, und die Behebungszeile lautet „das zuständige Audit dispatchen". Der Severity-Floor des Kerns gilt weiter, sodass eine aktive Senke mit angreiferkontrollierbarer Eingabe **Critical** ist.

- **MUSS** HTML-Injection-Senken melden: rohe HTML-Zuweisung oder die Escape-Hatch-Property des Frameworks, gespeist mit nicht-konstanter Eingabe und ohne Sanitisierungsschritt
- **MUSS** nutzerkontrollierte URL-Senken melden — Linkziele und Ressourcenquellen ohne Schema-Allowlist —, die das Framework-Escaping nicht abdeckt
- **MUSS** Secrets, Schlüssel und Zugangsdaten melden, die im Client-Code liegen oder vom Build in das Bundle eingebettet werden
- **MUSS** langlebige Zugangsdaten im Web-Storage melden sowie clientseitige Zugriffskontrolle, die als Durchsetzung behandelt wird (die Security-Seite von F1-Klasse 2: einmal melden, unter F9, mit Querverweis auf die F1-Klasse)
- **SOLLTE** dokumentübergreifende Gefahren melden, die in Markup und Message-Handling sichtbar sind: ein extern geöffnetes Ziel ohne Opener-Beschränkung und ein Message-Empfänger, der den Absender-Origin nicht prüft
- **SOLLTE** unsanitisierte Nutzerinhalte melden, die in einen Rich-Text-, Markdown- oder Chart-Renderer geleitet werden, sowie explizit deaktiviertes Framework-Escaping
- **DARF** hier **KEINE** Content Security Policy, keine HTTP-Security-Header und kein Authentifizierungsdesign auditieren: Das wird an `spec/frontend/webview-ui-optimization/` §„Security and sandboxing" und `spec/project/code-security-audit/` geroutet

### F10 — Nutzersichtbarer Text und Locale-Behandlung im Code

- **MUSS** nutzersichtbare Zeichenketten melden, die in Components hartkodiert sind, wenn das Projekt eine Internationalisierungsschicht mitliefert — einschließlich der Oberflächen, die ein naiver Scan verfehlt: zugängliche Namen, Alternativtexte, Tooltips und Dokumenttitel
- **MUSS** Sätze melden, die aus konkatenierten oder interpolierten Fragmenten zusammengesetzt sind und von einer Übersetzerin weder umgestellt noch flektiert werden können, sowie mengenabhängigen Text ohne Pluralbehandlung
- **MUSS** manuelle Formatierung von Datum, Uhrzeit, Zahlen, Währungen und Aufzählungen melden, wo eine locale-fähige Plattform-API existiert, sowie locale-unsicheres Sortieren, Groß-/Kleinschreiben oder Vergleichen
- **SOLLTE** Übersetzungsschlüssel melden, die an der Aufrufstelle dynamisch zusammengebaut werden und statische Abdeckungsanalyse aushebeln
- **MUSS** Schlüsselabdeckung und fehlende Übersetzungen an `spec/project/i18n-completeness/` routen

### F11 — Frontend-Testcode-Qualität (erweitert D6)

Die Kern-D6-Regeln gelten wortgleich; dies sind die Frontend-Ausprägungen, und jedes Finding trägt den `test`-Marker.

- **MUSS** Queries melden, die an der zugänglichen Oberfläche vorbeigreifen, wo eine Rollen-, Label- oder Text-Query treffen würde — Klassennamen, Component-Interna, tiefe DOM-Traversierung oder ein Test-Identifikator dort, wo eine semantische Query funktioniert
- **MUSS**, wenn ein Test *nicht* über Rolle oder Label abfragen kann, das Finding als wahrscheinlichen **Accessibility**-Defekt des getesteten Components melden (ein F8-Finding, das als F11-Symptom auftritt), nicht als reines Testproblem
- **MUSS** Assertions auf internen Zustand, Props oder Lebenszyklus melden statt auf gerenderte Ausgabe und beobachtbares Verhalten
- **MUSS** Snapshot-Assertions melden, die Verhaltens-Assertions ersetzen, sowie Snapshots, die zu groß sind, um sinnvoll reviewt zu werden
- **MUSS** Nichtdeterminismus melden: willkürliches Warten statt auf eine Assertion zu warten, nicht zurückgesetzte Fake-Timer, echten Netzwerkzugriff und Assertions, die ohne Fixierung von der Locale oder Zeitzone der Maschine abhängen
- **MUSS** das Mocken projekteigener Components oder Hooks melden, wo die Netzwerkgrenze die ehrliche Naht ist
- **MUSS** ungetestete Fehler- und Leerzweige melden, wo der Drei-Zustands-Vertrag aus F2 gilt. Ein F2-Finding über einen fehlenden Fehlerpfad und ein F11-Finding über dessen fehlende Testabdeckung gehören in **ein** Work-Package
- **MUSS** ad hoc vergebene Test-Identifikatoren an `spec/frontend/testability-identifiers/` routen und Einzel-Stufen-Konformitätsdetails an den zuständigen Stufen-Reviewer

### Framework-Profile

Jedes Framework-Profil **MUSS** Folgendes definieren, und ein Reviewer wendet es als eine Einheit an:

- **Tooling-Baseline:** den Linter mit seinen Framework- und Accessibility-Plugins, den Formatter, den Type-Checker samt Strictness, den Style-Linter und den Test-Runner mit seiner DOM-Testing-Bibliothek — die Menge, auf die die Tooling-first-Regel verweist
- **Component- und Logikmodell:** wo Logik lebt (Component, Hook oder Composable, framework-freies Fachmodul) und wie Client- und Server-Zustand kategorisiert werden
- **Reaktivitäts- und Effektmodell:** das Synchronisationsprimitiv des Frameworks und seine dokumentierten Fallstricke, geprüft unter F5
- **Render-Kostenmodell:** wie Re-Render-Kosten entstehen und ob ein automatischer Memoisierungsschritt Teil des Builds ist — die Eingabe für die bedingte Memoisierungsregel aus F6
- **Styling-Modell:** wie Components die Token- oder Theme-Schicht erreichen und wie Style-Scoping funktioniert, geprüft unter F7
- **Datenzugriffsmodell:** die Client-, Cache- oder Query-Schicht des Projekts, geprüft unter F1 und F4
- **Test-Stack-Profil:** der idiomatische Test-Stack und seine F11-relevanten Konventionen
- **Accessibility-Zugeständnisse:** was Framework und Linter kostenlos liefern, damit F8 oberhalb der Tooling-Linie bleibt

Ein Framework ohne Profil **MUSS** als nicht unterstützt gemeldet statt ad hoc reviewt werden, genau wie es die Kern-Spec für Sprachen fordert; der Report benennt das angewandte Profil.

### React- und TypeScript-Referenzprofil

- **Tooling-Baseline:** TypeScript im Strict-Modus; ESLint mit den React-Hooks-Regeln und dem JSX-Accessibility-Plugin; ein Formatter; ein Style-Linter, wo CSS geschrieben wird; ein Test-Runner mit React Testing Library, einer Nutzerinteraktions-Bibliothek und einer Mocking-Schicht auf Netzwerkebene. Formatierung, Import-Hygiene, Hook-Regelverstöße und die mechanischen Accessibility-Regeln gehören diesem Tooling — der Reviewer verweist gemäß der Tooling-first-Regel darauf
- **Component- und Logikmodell (F1):** Components rendern; zustandsbehaftetes Verhalten lebt in Custom Hooks; Fachregeln leben in framework-freien Modulen, die nichts aus React importieren; Server-Zustand lebt in der Query- oder Cache-Schicht; Client-Zustand bleibt lokal, bis ein zweiter Konsument das Hochziehen rechtfertigt
- **Typing-Disziplin (D5, F3):** kein Escape-Hatch-`any`, keine ungeprüften Casts oder Non-Null-Assertions auf Props und API-Payloads; API-Antworten an der Grenze geparst oder validiert statt in einen Typ hineinbehauptet; asynchroner UI-Zustand als Discriminated Union modelliert statt als unabhängige boolesche Flags; explizite Prop-Typen mit explizitem Children; typisierte Event-Handler
- **Effekt-Fallstricke (F5):** Zustand in einem Effekt abgeleitet statt während des Renderns berechnet; Zustand in einem Effekt zurückgesetzt statt über einen Component-Key; Event-Handler-Logik in einem Effekt platziert; Effektketten, die Renders kaskadieren; Fetches ohne Ignore-Flag oder Abbruch im Cleanup; fehlendes Cleanup bei Listenern, Timern, Subscriptions und Observern; ungeschützter `window`- oder `document`-Zugriff auf einem serverseitig gerenderten Pfad
- **Render-Kostenmodell (F6):** Re-Render-Kosten entstehen aus Identitäts-Churn und teuren Ableitungen. Ob handgeschriebene Memoisierung erwartet wird, hängt davon ab, ob das Projekt in seiner Build-Konfiguration compilerbasierte automatische Memoisierung aktiviert; der Reviewer liest das aus dem Repository und wendet die bedingte Regel aus F6 entsprechend an
- **Styling-Modell (F7):** Das Theme- oder Token-Modul des Projekts ist die Quelle der Design-Werte; scoped Styling-Mechanismen dürfen nicht global auslaufen; je Render neu erzeugte Style-Objekte sind ein F7-Finding, wenn es um Disziplin geht, und ein F6-Finding, wenn es um gemessene Kosten geht
- **Datenzugriffsmodell (F1, F4):** Eine Client- oder Query-Schicht besitzt Requests, Caching und Invalidierung; Components konsumieren Hooks über dieser Schicht, nie eine nackte Request-Funktion
- **Test-Stack-Profil (F11):** die dokumentierte Query-Priorität der Testing Library — Rolle, dann Label, dann Text, mit Test-Identifikatoren als letztem Mittel; eine Nutzerinteraktions-Bibliothek statt Low-Level-Event-Dispatch; abgewartete asynchrone Queries statt willkürlichem Warten; Mocking an der Netzwerkgrenze statt Stubbing projekteigener Module
- **Accessibility-Zugeständnisse (F8):** Das JSX-Accessibility-Plugin deckt die mechanischen Regeln ab, sodass F8-Findings hier die sind, die es nicht entscheiden kann — Rollenversprechen ohne das zugehörige Interaktionsverhalten, Fokusverwaltung, Live-Regionen und Label-Zuordnung über Component-Grenzen hinweg

Vue, Angular, Svelte und native Web Components haben in dieser Spec noch kein Profil und werden als nicht unterstützt gemeldet.

### Report, Umsetzungsvorschläge und Routing

Der Kern-§Report-Vertrag gilt unverändert. Diese Spec ergänzt:

- **MUSS** die Behebung jedes Critical- und Warning-Findings als **Umsetzungsvorschlag** formulieren, den ein Spezialist ausführen kann, ohne die Analyse neu herzuleiten. Der Vorschlag benennt: die **Zielschicht oder -datei** der Änderung, die **Form** der Änderung (die Regel in einen Hook extrahieren, eine Discriminated Union für den Request-Zustand einführen, eine Boundary um die Route legen, die Senke durch den sanitisierenden Pfad ersetzen, die Durchsetzung auf den Server verlagern), das **Abnahmesignal** (der Test oder das beobachtbare Verhalten, das die Behebung belegt) und das **Risiko** einer blinden Anwendung
- **DARF** keinen Patch anwenden, vorbereiten oder anhängen: Der Reviewer bleibt read-only, und der Vorschlag ist Prosa plus, wo es die Form verdeutlicht, ein kurzes, als illustrativ gekennzeichnetes Snippet
- **SOLLTE** Work-Packages entlang der **Component-Slice-Grenzen** schneiden, sodass keine zwei Packages denselben Slice berühren; das erfüllt und verstärkt die Disjunktheitsgarantie des Kerns, da Component, Styles und Tests eines Slice gemeinsam wandern
- **MUSS** jedes Work-Package an den zuständigen Spezialisten routen: Frontend-Produktivcode-Behebung an die umsetzende Engineering-Rolle (`fullstack-developer`); Accessibility-Konformitätsfragen an `webview-ui-expert`; Security-Floors an `code-security-reviewer`; Übersetzungsabdeckung an den Internationalisierungs-Checker; Einzel-Stufen-Testkonformität an den zuständigen Stufen-Reviewer
- **MUSS** die Findings des Reports zusätzlich zur Severity nach Component-Slice gruppieren, damit ein Spezialist eine zusammenhängende Arbeitseinheit erhält statt einer verstreuten Liste
- **MUSS** an den Kern-Artefaktort persistieren, `.audits/source-code-review/<target-slug>.md` gemäß `spec/claude/review-plan/` §„File location and naming", wobei der Target-Slug einen frontend-begrenzten Lauf von einem Gesamt-Tree-Lauf unterscheidet; ein erneuter Lauf überschreibt die kanonische Datei
- **MUSS** im Header zusätzlich zu Scope und Tooling-Baseline des Kerns festhalten: das angewandte Framework-Profil, jedes erkannte nicht unterstützte Framework und die vier Baselines aus §„Review-Einheit: der Component-Slice"

### Abgrenzung zum UX-Review

Dies ist eine tragende Grenze, kein höflicher Hinweis. Beide Reviews blicken auf denselben Bildschirm und beantworten verschiedene Fragen, und ein Frontend-Code-Review, das in UX-Urteile abdriftet, verliert genau die Autorität, die seine Findings umsetzbar macht.

**Die Regel:** Dieses Review beantwortet *Ist dieser Code korrekt, geschichtet, sicher, konstruktionsbedingt zugänglich, testbar und konsistent mit dem System, das das Projekt selbst deklariert?* Es beantwortet nie *Ist das die richtige Erfahrung?*

- **DARF KEIN** Finding erheben, dessen einziger Beleg ein gerenderter Eindruck ist. Konstruktionsbedingt außerhalb des Scopes: Wortwahl, Tonalität oder Hilfreichkeit nutzersichtbarer Texte; visuelle Hierarchie, Abstände und ästhetische Wahl; Informationsarchitektur und Navigationsfluss; ob ein Bedienelement auffindbar ist; ob ein Ablauf weniger Schritte braucht; ob sich eine Interaktion reaktionsschnell anfühlt; ob ein Leerzustand motivierend ist
- **MUSS** den **Code-seitigen Zwilling** erheben, wo es einen gibt, und nur diesen. Die wiederkehrenden Zwillinge:

| UX-Frage (nicht dieses Review) | Code-Frage (dieses Review) |
|---|---|
| Ist diese Fehlermeldung freundlich und hilfreich? | Gibt es überhaupt einen Fehlerpfad, und verschluckt er den Fehler? (F2) |
| Ist das der richtige Blauton? | Umgeht der Wert die Token-Schicht, die das Projekt mitliefert? (F7) |
| Ist dieser Dialog verwirrend? | Fängt und restauriert der Dialog den Fokus? (F8) |
| Liest sich dieser Text gut? | Ist der Text hartkodiert und nicht übersetzbar? (F10) |
| Fühlt sich diese Liste langsam an? | Wird die gesamte Collection gerendert, und lädt jede Zeile nach? (F6) |
| Ist das der richtige Standardwert? | Ist der Standardwert eine Fachregel, die der Server besitzen muss? (F1) |

- **MUSS** eine UX-Beobachtung, die dem Reviewer zufällig auffällt, als **einzelnen Info-Eintrag** mit dem Routing-Ziel `frontend-usability-optimizer` oder `webview-ui-optimize` melden, nie oberhalb von Info und nie innerhalb der Work-Packages
- **DARF NICHT** als Ersatz für das UX- oder Usability-Review dargestellt werden: Beide werden gebraucht, sie erzeugen getrennte Artefakte, und keines ist Gate für das andere
- Die Grenze gilt in Gegenrichtung genauso: Das UX-Review erhebt keine Code-Findings, und ein Usability-Report wird nie in das Code-Review-Artefakt eingemischt

## Akzeptanzkriterien

- [ ] Ein Frontend-Review führt die Kern-Dimensionen D1–D10 **und** F1–F11 dieses Overlays aus, und kein Finding trägt zugleich eine D- und eine F-ID
- [ ] Der Report-Header hält Framework-Profil, Design-Token- oder Theme-Quelle, Internationalisierungsschicht und Datenzugriffsschicht fest; ein erkanntes Framework ohne Profil erscheint als nicht unterstützt
- [ ] Ein Component wird zusammen mit seinen Hooks, Styles und Tests reviewt; ein Report über Component-Dateien ohne Testdateien wird als unvollständig zurückgewiesen
- [ ] Eine in einem Component berechnete Fachregel wird unter F1 mit benannter Klasse gemeldet, und eine Regel, die der Server besitzen müsste, aber nicht nachrechnet, ist bei Bestätigung Critical und wird an das Security-Audit geroutet
- [ ] Präsentationslogik — Anzeigeformatierung, bedingtes Rendern, Layout-Verzweigung — erzeugt kein F1-Finding
- [ ] Ein Rejection-Handler, der nichts anzeigt, nichts propagiert und nichts meldet, ist bei Bestätigung Critical und bei Vermutung mindestens Warning und erscheint in den Work-Packages
- [ ] Eine asynchrone Oberfläche ohne unterscheidbaren Pending-, Fehler-mit-Wiederherstellung- oder Leerzustand erzeugt ein F2-Finding, und ihr ungetesteter Fehlerzweig landet im **selben** Work-Package wie ein F11-Finding
- [ ] Ein Memoisierungs-Finding existiert nur mit benannten Kosten oder benannter Fehlerhaftigkeit, und in keiner Richtung erscheint ein pauschales Memoisierungs-Finding; das Urteil passt zu dem, was die Build-Konfiguration des Repositories aktiviert
- [ ] Ein hartkodierter Design-Wert wird unter F7 gemeldet, wo das Projekt Tokens mitliefert, während die Wahl des Werts selbst kein Finding erzeugt
- [ ] Ein Click-Handler auf einem nicht-semantischen Element ohne Rolle, Fokussierbarkeit oder Tastaturbehandlung wird unter F8 gemeldet, während Kontrast- und Konformitätsstufenfragen nur als Route-out erscheinen
- [ ] Eine HTML- oder URL-Injection-Senke wird unter F9 mit Routing-Hinweis und ohne Tiefenanalyse gemeldet, und ihre Severity respektiert den Floor
- [ ] Jedes Critical- und Warning-Finding trägt einen Umsetzungsvorschlag mit Zielschicht, Änderungsform, Abnahmesignal und Risiko; kein Patch wird angewandt oder angehängt
- [ ] Work-Packages sind entlang der Component-Slices geschnitten, keine zwei berühren denselben Slice, und jedes trägt ein Routing-Ziel
- [ ] Kein Finding oberhalb von Info stützt sich auf einen gerenderten Eindruck; UX-Beobachtungen erscheinen als Info-Einträge, geroutet an die Usability-Capability, und nie in den Work-Packages
- [ ] Der persistierte Report liegt unter `.audits/source-code-review/<target-slug>.md`, und ein erneuter Lauf überschreibt ihn

## Referenzen

- [R1] Das Kern-Review, das diese Spec erweitert (Dimensionen D1–D10, Tooling-first-Regel, Report- und Reviewer-Vertrag): `spec/project/source-code-review/`
- [R2] Severity-Vokabular und Audit-Artefakt-Konventionen: `spec/claude/review-plan/`
- [R3] Laufzeitqualität der Web-Oberfläche — gemessene Performance, Security-Header und CSP, WCAG-Konformität, i18n zur Laufzeit, UX und natives Gefühl (der wichtigste Route-out- und Abgrenzungspartner): `spec/frontend/webview-ui-optimization/`
- [R4] Whole-Codebase-Security-Audit (Route-out-Ziel für F9-Floors): `spec/project/code-security-audit/`
- [R5] Observability-Audit (Route-out-Ziel für nicht gemeldete Fehler): `spec/project/monitoring-observability/`
- [R6] Übersetzungsschlüssel-Abdeckung und Locale-Vollständigkeit (Route-out-Ziel für F10): `spec/project/i18n-completeness/`
- [R6a] Error-Tracking-Lebenszyklus und der Browser-Global-Handler-Boden (Route-out-Ziel für nicht gemeldete F2-Fehler): `spec/project/error-tracking/`
- [R7] Test-Identifikator-Vertrag (Route-out-Ziel für F11-Identifikator-Findings): `spec/frontend/testability-identifiers/`
- [R8] Test-Stufen-Specs und -Reviewer (Route-out-Ziele für Stufenkonformität): `spec/project/test-pyramid-foundation/` und `spec/project/test-tier-*/`
- [R9] Mechanisches Gate, auf das die Tooling-first-Regel verweist: `spec/project/quality-gate/`
- [R10] Agent-Autorenregeln und Read-only-Tool-Disziplin: `spec/claude/agent-management/`
- [R11] Recherche-Methodik und Quellenschwellen hinter den Regeln dieser Spec: `spec/claude/research-triangulate/`
- [R12] Evidenznotizen mit den Quellen je Dimension: `spec/frontend/source-code-review/research/`
- [R13] Falsifizierbarkeits-Taxonomie und Detektionskriterien für F11-Findings zu Tests, die nicht fehlschlagen können: `spec/project/test-falsifiability/`

## Offene Fragen

- Welches Framework-Profil folgt auf das React-und-TypeScript-Referenzprofil — Vue, Angular oder Svelte —, und lebt es in dieser Spec oder in einem Schwesterdokument, sobald die Profilanzahl wächst?
- Ist der Frontend-Reviewer ein Agent je Framework, analog zu den Reviewer-Agents je Sprache der Kern-Spec, oder ein profilgesteuerter Agent, der sein Profil beim Dispatch wählt? Der Dispatch je Sprache in der Kern-Spec spricht für Ersteres, das gemeinsame F1–F11-Overlay für Letzteres.
- Wo lebt ein gemeinsamer Client-und-Server-Validierungsvertrag, wenn beide Seiten in getrennten Repositories liegen, und reicht der Single-Source-of-Truth-Vorschlag aus F4 über eine Repository-Grenze hinweg, bevor die Portfolio-Inherited-Spec-Schicht einen Cross-Repo-Resolver liefert?
- Sollte F6 eine Bundle-Zusammensetzungssicht erhalten (was eine Abhängigkeit an der Importstelle kostet), oder bleibt das vollständig bei den gemessenen Budgets in `spec/frontend/webview-ui-optimization/`?
