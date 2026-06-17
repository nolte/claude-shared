# API-Fehlerbehandlungs-Konformität

Status: draft

## Kontext

Eine Web-API beantwortet Fehler mit HTTP-Fehlerantworten. Drei Schwächen häufen sich still an, während die Oberfläche wächst: Die Form des Fehler-Bodys driftet von Endpunkt zu Endpunkt (einer liefert `{"detail": "..."}`, ein anderer einen nackten String, ein dritter ein reiches Objekt), sodass Clients Fehler nicht einheitlich parsen können; der falsche HTTP-Status-Code wird zurückgegeben (eine fehlende Entität mit `200` und leerem Body, ein Validierungsfehler mit `500`), sodass Clients nicht auf die Statuszeile verzweigen können; und interne Details gelangen in die Antwort (ein Stack-Trace, eine rohe Datenbank-Treibermeldung, eine gerenderte SQL/AQL-Query, ein Secret in einem Log-and-Return-Pfad), was zugleich ein Usability-Defekt und eine Sicherheitslücke ist. Keine davon wird von einem Type-Checker oder der Happy-Path-Test-Suite gefangen, und sie tauchen als brüchige Client-Integrationen und als Befunde in einem Security-Review auf.

Diese Spec regelt eine fokussierte, **read-only-Konformitätsprüfung** der Fehlerbehandlungs-Oberfläche einer Web-API gegen den projekteigenen deklarierten Fehler-Contract, operationalisiert durch den `api-error-check`-Skill (`nolte-engineering`-Plugin). Sie ist der generalisierte Nachfolger eines projektlokalen Checkers, der das Framework einer einzelnen Anwendung (FastAPI), das Fehlerantwort-Modell, die Anforderungs-ID und die Exception-Strings des Persistenz-Treibers hartcodiert hatte. Die Portfolio-Form entdeckt das API-Framework, den Fehlerantwort-Contract und den Fehlerbehandlungs-Standard aus dem Projekt, statt einen einzelnen Stack anzunehmen.

Leser: Skill-Autoren, die den Checker pflegen; Reviewer, die seine Befunde prüfen; Entwickler, die ihn nach dem Hinzufügen oder Ändern von Endpunkten, vor einem Release oder innerhalb eines Pre-PR-Checks laufen lassen.

## Ziele

- Die drei Fehlerbehandlungs-Drifts — uneinheitliche Fehler-Body-Form, falscher HTTP-Status-Code und Leckage interner Details — als einen einzigen nach Schweregrad sortierten Report aufzeigen
- In den Kern-Prüfungen (einheitliche Fehlerform, Status-Code-Semantik, Leckage-Scan) framework-agnostisch bleiben, während die Call-Site-Patterns an das tatsächliche Web-Framework des Projekts angepasst werden
- Die API gegen den **eigenen** deklarierten Fehler-Contract des Projekts messen, wenn einer existiert, und nur dann auf dokumentierte HTTP-Defaults zurückfallen (RFC 9457 Problem Details, Standard-Status-Code-Semantik), wenn keiner deklariert ist
- Strikt read-only bleiben: Die Prüfung berichtet und empfiehlt, sie editiert nie Handler-Code
- Die Prüfung billig wiederholbar innerhalb eines Sprints machen, weil sie seiteneffektfrei ist
- Eine klare Grenze zum breiten Code-Security-Audit und zum allgemeinen Code-Review ziehen, sodass der Skill nur für Fehlerbehandlungs-Konformität aufgerufen wird

## Nicht-Ziele

- Fehler-Handler implementieren oder reparieren — die Prüfung berichtet Lücken; ein Entwickler behebt sie
- Das Whole-Codebase-OWASP-Security-Audit, das `spec/project/code-security-audit/` besitzt; diese Spec ist die enge Fehlerantwort-Scheibe, und ein Leckage-Befund hier ist ein Zeiger in dieses breitere Audit, kein Ersatz dafür
- Allgemeines Code-Quality- oder Korrektheits-Review (Eigentum des `review`-Skills); diese Prüfung beurteilt nur den Fehlerbehandlungs-Contract
- Den Fehler-Contract eines Projekts definieren: Die Prüfung misst gegen den Contract, den das Projekt deklariert, sie zwingt Projekten ohne Contract kein kanonisches Schema auf
- Laufzeit-Fault-Injection oder Live-API-Probing; die Prüfung ist statisch (liest Quellcode, ruft die laufende API nicht auf)
- Lokalisierung von Fehlermeldungen (Eigentum von `spec/project/i18n-completeness/`)

## Anforderungen

### Eingaben und Discovery

- **MUSS** ein Ziel akzeptieren, das entweder ein expliziter Handler-/Router-Datei- oder Verzeichnispfad ist oder ein Anforderungs-/Feature-Identifier, mit dem das Projekt Endpunkte gruppiert (zum Beispiel `REQ-013`); bei einem Identifier diesen über das projekteigene Layout zu den besitzenden Handler-Dateien auflösen, statt über einen hartcodierten Pfad
- **MUSS** den **Fehlerbehandlungs-Standard** des Projekts entdecken, statt eine Anforderungs-ID anzunehmen: nach einer nicht-funktionalen Anforderung oder einem Spec-Dokument suchen, das Fehlerantworten regelt (zum Beispiel unter `spec/`, `docs/` oder einem ADR), und wenn eines existiert, die Konformität dagegen messen; berichten, welches Dokument verwendet wurde
- **MUSS** den **Fehlerantwort-Contract** des Projekts (das kanonische Fehler-Body-Modell) entdecken, statt das Schema einer einzelnen Anwendung hartzucodieren: die Fehler-Schema-Definition lokalisieren (ein gemeinsames Fehler-Modell-Modul, ein Framework-Exception-Handler, ein OpenAPI-`components.schemas`-Fehlertyp oder Äquivalent) und ihre Felder als die geforderte Form behandeln; berichten, wo der Contract gefunden wurde
- **MUSS** das **Web-Framework** aus Projekt-Signalen erkennen (Dependency-Manifest plus Import-/Decorator-Patterns — FastAPI/Starlette, Flask, Django REST Framework, Express/NestJS, Spring und Vergleichbares) und die Handler- und Exception-auslösenden Call-Site-Patterns entsprechend anpassen; wenn das Framework nicht bestimmbar ist, das angenommene Pattern-Set im Report angeben
- **MUSS** pro aufgelöster Eingabe berichten, ob der Wert aus einem Operator-Argument, einem entdeckten Standard-/Contract-Dokument oder einem dokumentierten Default stammt
- **KANN** eine optionale repository-lokale Konfigurationsdatei lesen, die das Standard-Dokument, den Ort des Fehler-Contracts, die Handler-Roots und das Framework deklariert; ist sie vorhanden, haben ihre Werte Vorrang vor der Discovery, ist sie abwesend, ist die Discovery pro Aufruf der dokumentierte Default

### Konformitäts-Dimensionen

- **MUSS** die **Fehler-Body-Einheitlichkeit** prüfen: Jeder Fehlerpfad gibt die deklarierte Fehler-Contract-Form des Projekts zurück (oder, ohne deklarierten Contract, eine einzige konsistente Form über die Oberfläche); jeden Endpunkt berichten, dessen Fehlerantwort von dieser Form abweicht
- **MUSS** prüfen, dass die **Pflichtfelder** des deklarierten Fehler-Contracts auf jedem Fehlerpfad befüllt sind — einschließlich, wenn der Contract sie deklariert, eines eindeutigen Fehler-/Korrelations-Identifiers, eines stabilen maschinenlesbaren Fehler-Codes, einer menschenlesbaren Meldung, optionaler feldspezifischer Details und des Request-Kontexts (Pfad, Methode, Zeitstempel)
- **MUSS** verifizieren, dass ein deklarierter **eindeutiger Fehler-Identifier dynamisch erzeugt** wird (pro Auftreten, zum Beispiel eine frische UUID) und nie als statische oder hartcodierte Konstante ausgegeben wird, da ein konstanter Identifier die Log-Korrelation zunichtemacht
- **MUSS** die **HTTP-Status-Code-Semantik** gegen die Situation prüfen, auf die der Handler antwortet, mit der Standard-Semantik als Baseline:

  | Situation | Erwarteter Status |
  |---|---|
  | Ressource nicht gefunden | 404 |
  | Request-/Validierungsfehler | 400 oder 422 (je nach Framework-Konvention) |
  | Nicht authentifiziert | 401 |
  | Authentifiziert, aber nicht berechtigt | 403 |
  | Domänen-/Business-Rule-Verletzung | 409 oder 422 (je nach Projekt-Konvention) |
  | Duplikat / Konflikt-Zustand | 409 |
  | Unbehandelter Server-Fehler | 5xx (ohne interne Details im Body) |

  Jeden Handler berichten, dessen Status-Code der Situation widerspricht, mit einer file:line-Attribution.
- **MUSS** einen **Leckage-Scan** für interne Details ausführen, die in den Antwort-Body gelangen: rohe Exception-/stringifizierte Treibermeldungen, Stack-Traces oder Tracebacks, gerenderte Datenbank-Queries, interne Host-/Pfad-/Config-Werte und Secrets. Jeder Treffer ist ein sicherheitsrelevanter Befund (**critical**), file:line attribuiert und als Zeiger in `spec/project/code-security-audit/` markiert
- **MUSS** statisch unentscheidbare Fehlerpfade (ein Status-Code oder Body, der aus einer nicht auflösbaren Laufzeitvariable zusammengesetzt wird) als vermerkten Vorbehalt behandeln — sie als „dynamisch, statisch nicht verifizierbar“ berichten, sodass sie die Befund-Zahlen weder aufblähen noch still verschwinden
- **SOLLTE** Endpunkte berichten, deren **Fehlerpfade überhaupt keine Abdeckung** haben (ein Handler ohne Fehler-Branch und ohne ihn absichernden Framework-Exception-Handler), da ein unbehandelter Fehlerpfad auf den Framework-Default durchfällt, der häufig einen Stack-Trace leakt

### Ausgabe und Seiteneffekte

- **MUSS** strikt read-only sein: nie Handler-Code, das Fehler-Contract-Modul oder eine andere Datei editieren; die einzige Ausgabe ist ein Report
- **MUSS** einen einzigen nach Schweregrad sortierten Report ausgeben, geordnet **critical** (Leckage interner Details; unbehandelte Fehlerpfade, die auf einen leckenden Default durchfallen), dann **warning** (falscher Status-Code; fehlendes Pflicht-Contract-Feld; statischer Fehler-Identifier), dann **info** (Body-Form-Drift, wo kein Contract deklariert ist; dynamisch, statisch nicht verifizierbar), angeführt von einer Übersichtstabelle (geprüfte Endpunkte, konform, abweichend, Leckage-Treffer, dynamisch-übersprungen)
- **MUSS** die Ausgabe pro Kategorie deckeln (die ersten N Einträge zeigen und den Rest als „… und {n} weitere“ zusammenfassen), sodass ein großer Drift keine unlesbare Wand von Befunden erzeugt
- **MUSS** jeden Befund einer Quell-Position (Datei und Zeile) zuordnen, damit er handlungsfähig ist
- **MUSS** berichten, welches Ziel, Framework, Fehlerbehandlungs-Standard-Dokument und welchen Fehlerantwort-Contract es verwendet hat, sodass der Umfang der Prüfung auditierbar und reproduzierbar ist
- **MUSS**, wenn kein Projekt-Fehler-Contract entdeckbar ist, den HTTP-Default angeben, auf den es zurückgefallen ist (einheitliche Form plus Standard-Status-Code-Semantik, RFC 9457 Problem Details als empfohlene Baseline), statt still ein projektspezifisches Schema zu erfinden

## Akzeptanzkriterien

- [ ] Die Ausführung der Prüfung auf einem Ziel mit abweichenden Fehlerantworten erzeugt einen nach Schweregrad sortierten Report, dessen Übersichtstabelle geprüfte Endpunkte, konform, abweichend, Leckage-Treffer und dynamisch-übersprungen auflistet
- [ ] Ein Endpunkt, dessen Fehler-Body vom deklarierten Fehler-Contract abweicht, wird mit einer file:line-Attribution berichtet
- [ ] Ein Fehlerpfad, der einen der Situation widersprechenden Status-Code zurückgibt (zum Beispiel `500` für ein Not-Found), wird als Warning mit file:line berichtet
- [ ] Ein Handler, der eine rohe Exception-Meldung, einen Stack-Trace oder eine gerenderte Datenbank-Query im Antwort-Body zurückgibt, wird als kritischer Leckage-Befund berichtet, der auf `spec/project/code-security-audit/` zeigt
- [ ] Ein deklarierter eindeutiger Fehler-Identifier, der als statische Konstante ausgegeben wird, wird als Warning berichtet
- [ ] Ein statisch unentscheidbarer Fehlerpfad wird als „dynamisch, statisch nicht verifizierbar“ berichtet und aus den konform/abweichend-Zahlen ausgeschlossen
- [ ] Der Report nennt das aufgelöste Ziel, das erkannte Framework, das Fehlerbehandlungs-Standard-Dokument und den Ort des Fehlerantwort-Contracts sowie ob jedes aus einem Argument, der Discovery oder einem Default stammt
- [ ] Wenn kein Projekt-Fehler-Contract entdeckbar ist, nennt der Report den HTTP-Default, gegen den gemessen wurde
- [ ] Der Skill nimmt keine Datei-Änderungen vor (read-only)
- [ ] Der Skill zitiert diese Spec in seinem Body oder seiner `description`

## Referenzen

- [R1] Skill-Autorenregeln, denen dieser Skill folgt: `spec/claude/skill-management/`
- [R2] Skill-vs-Agent-Entscheidungsregel und Anforderung an den Rationale-Abschnitt: `spec/claude/skill-vs-agent/`
- [R3] Angrenzendes Whole-Codebase-Security-Audit (gegen diese Spec abgegrenzt; Leckage-Befunde zeigen hierhin): `spec/project/code-security-audit/`
- [R4] Review-Plan-/Audit-Ausgabe-Konventionen für nach Schweregrad sortierte Reports: `spec/claude/review-plan/`
- [R5] RFC 9457 — Problem Details for HTTP APIs (empfohlener Default-Fehler-Contract): <https://www.rfc-editor.org/rfc/rfc9457>

## Offene Fragen

_Derzeit keine._
