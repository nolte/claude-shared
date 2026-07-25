# REST-API- und URL-Design

Status: draft

## Kontext

Eine Web-API, die Bestand hat, ist eine API, deren URLs, Methoden, Status-Codes, Versionierung und Fehler-Bodys vorhersagbar bleiben, während die Oberfläche wächst. Werden diese Entscheidungen ad hoc getroffen, häufen sich vier Fehler still an: URLs driften zwischen Verb-Stil und Ressourcen-Stil (`/getUser` neben `/users/{id}`), zwischen Sprachen (`/ki-assistent` neben `/ai`) und zwischen Casing-Konventionen, sodass Konsumenten den nächsten Endpunkt nicht aus dem letzten erraten können; dieselbe Situation antwortet über Handler hinweg mit unterschiedlichen HTTP-Status-Codes, sodass Clients nicht auf die Statuszeile verzweigen können; ein Breaking Change geht in einer unversionierten URL live und bricht still jeden bestehenden Client; und die Form des Fehler-Bodys unterscheidet sich von Endpunkt zu Endpunkt, sodass kein Client Fehler einheitlich parsen kann. Keiner davon wird von einem Type-Checker oder den Happy-Path-Tests gefangen, und jeder verhärtet sich in dem Moment zu einem Kompatibilitäts-Contract, in dem ein Dritter integriert.

Diese Spec definiert, wie eine HTTP-API **gestaltet** wird—die Form ihrer URLs, die Semantik ihrer Methoden und Status-Codes, ihre Versionierungs- und Deprecation-Strategie, ihre Collection-Konventionen (Filtern, Sortieren, Paginieren, Feldauswahl), ihren kanonischen Fehler-Body und ihre Transport-Sicherheits-Basis—sodass ein Reviewer Konformität beurteilen und ein Konsument die Oberfläche vorhersagen kann. Sie ist das fehlende dritte Mitglied eines Trios: `spec/project/api-documentation/` besitzt **wie** die API dokumentiert wird (ihre Non-Goals verweisen Design-Qualität hierher), und `spec/project/api-error-handling/` besitzt die read-only **Konformitätsprüfung** der Fehler-Oberfläche (ihre Non-Goals verweisen die Definition des kanonischen Fehler-Contracts hierher). Diese Spec besitzt das Design selbst, einschließlich der kanonischen Fehler-Body-Form des Portfolios, auf die die beiden anderen verweisen.

Wo die großen Guideline-Werke der Branche einig sind (ressourcen-orientierte Substantive, Plural-Collections, RFC-9110-Methodensemantik, HTTPS, keine Secrets in URLs), übernimmt diese Spec den Konsens. Wo sie auseinandergehen—vor allem Property-Casing und Versionierungsachse—trifft diese Spec eine explizite Portfolio-Entscheidung und benennt sie, denn die eine harte Regel, die alle Guidelines teilen, lautet: *innerhalb einer API konsistent sein*.

Leser: Entwickler, die eine HTTP-API gestalten oder erweitern; Reviewer, die ein Design gegen diesen Standard prüfen; Skill- und Agent-Autoren, die darauf Design-Review-Tooling bauen.

## Ziele

- Ein vorhersagbares URL- und Methoden-Vokabular über jedes API-liefernde Repository hinweg, sodass ein Konsument einen ungesehenen Endpunkt aus den bekannten ableiten kann
- Eine einzige, explizite Antwort auf jeden Divergenzpunkt der Branche (Property-Casing, Versionierungsachse, Fehler-Body-Form), einmal gewählt und konsistent angewandt
- Eine Versionierungs- und Deprecation-Strategie, die eine API sich entwickeln lässt, ohne bestehende Clients still zu brechen, und die nie ein rückwirkendes Umschreiben einer ausgelieferten Major-Version erzwingt
- Ein kanonischer, maschinenlesbarer Fehler-Body für das Portfolio, referenziert von der API-Documentation- und der Error-Handling-Spec statt pro Projekt neu erfunden
- Eine Basis an Transport- und URL-Sicherheit (HTTPS, keine Credentials in der URL, Auth in Headern), die framework-unabhängig gilt
- Eine Scope-Regel, die den Standard inkrementell adoptierbar macht: verbindlich für neue APIs und die nächste Major-Version, nie ein Big-Bang-Retrofit einer laufenden

## Nicht-Ziele

- **Wie die API dokumentiert wird**—der OpenAPI-Contract, Vollständigkeit und Drift-Erkennung gehören `spec/project/api-documentation/`; diese Spec regelt das Design, das jenes Dokument beschreibt
- **Die read-only-Fehlerbehandlungs-Konformitätsprüfung**—Eigentum von `spec/project/api-error-handling/`; diese Spec definiert den kanonischen Fehler-Body, jene Spec prüft eine Codebasis gegen den von ihr deklarierten Contract
- **Nicht-REST-API-Stile**—GraphQL, gRPC, AsyncAPI und Message-Queue-Contracts sind außerhalb des Scopes; jeder verdient seine eigene Spec, wenn ein Repository ihn braucht
- **Design von Authentifizierungs- und Autorisierungs-Mechanismen**—Token-Ausgabe, Session-Modelle, Scope-Taxonomien und Identity-Provider; diese Spec verlangt nur, dass Credentials in Headern über HTTPS reisen, nicht wie sie erzeugt werden
- **Wire-Level-Datenmodell- und JSON-Schema-Konventionen** jenseits von Casing und Fehlerform—Eigentum von `spec/project/yaml-json-schema/` und, für OpenAPI-Schema-Objekte, von `spec/project/api-documentation/`
- **Lokalisierung von Antwort-Inhalten und Fehlermeldungen**—Eigentum von `spec/project/i18n-completeness/`; diese Spec fixiert die Sprache von URLs und Identifiern (Englisch), nicht die von menschenlesbarem Payload-Text
- **Eine bestehende API implementieren oder migrieren**—diese Spec ist der Ziel-Standard; die Migration eines Repositorys ist dessen eigene geplante Arbeit

## Anforderungen

### Geltungsbereich

- **MUSS** für jede **neu erstellte** HTTP-API und für jede **neue Major-Version** einer bestehenden API verbindlich sein; eine bereits ausgelieferte Major-Version ist **grandfathered**—sie muss nicht auf diesen Standard nachgezogen werden, und ein Retrofit **DARF NICHT** einer laufenden Major-Version aufgezwungen werden
- **MUSS** den nächsten Major-Version-Bump eines Repositorys (zum Beispiel `/v1` → `/v2`) als den Punkt behandeln, an dem der volle Standard greift, sodass Migrationskosten bewusst an einer Versionsgrenze gezahlt werden statt als In-Place-Bruch
- **SOLLTE** innerhalb einer grandfathered Major-Version die additiven und nicht-brechenden Regeln dieser Spec dennoch auf **neue** Endpunkte anwenden, wo das den etablierten Konventionen der Version nicht widerspricht (zum Beispiel nutzt ein neuer Endpunkt ressourcen-orientierte Plural-Substantive, auch wenn ältere Geschwister es nicht tun)

### URL- und Ressourcen-Struktur

- **MUSS** die API als Ressourcen modellieren, die mit **Substantiven** benannt sind, nicht mit Aktionen: `POST /orders`, nicht `POST /createOrder`; die HTTP-Methode trägt das Verb
- **MUSS** Collections im **Plural** benennen und ein Mitglied über einen als Pfadsegment angehängten Identifier adressieren: `/plant-instances` (Collection), `/plant-instances/{plantInstanceId}` (Mitglied)
- **MUSS** Enthaltensein als alternierende Collection/Identifier-Pfadsegmente ausdrücken (`/species/{speciesId}/cultivars/{cultivarId}`) und **SOLLTE** die Sub-Ressourcen-Verschachtelung auf etwa drei Ebenen begrenzen; tiefere Beziehungen werden als Top-Level-Ressourcen mit einem Filter statt weiterer Verschachtelung ausgedrückt
- **MUSS** den Pfad zur Identifikation von Ressourcen und den **Query-String** zum Filtern, Sortieren, Paginieren oder Formen einer Collection nutzen—nie um auszuwählen, welche Ressource adressiert wird
- **MUSS** eine Operation, die wirklich nicht in Ressourcen-CRUD passt, als **Custom Method** in Doppelpunkt-Notation an der Ressource ausdrücken (`POST /orders/{orderId}:cancel`), statt ein Verb-Pfadsegment zu erfinden; Custom Methods sind die dokumentierte Ausnahme, nicht der Default
- **SOLLTE** die kanonische URL einer Ressource über Versionen und Releases stabil halten; die Identität einer Ressource ist Teil ihres Contracts

### Sprache und Casing

- **MUSS** alle URL-Pfadsegmente, Query-Parameter-Namen und JSON-Property-Namen in **Englisch** und **nur mit US-ASCII** schreiben—keine Umlaute oder Nicht-ASCII-Zeichen, die sonst Percent-Encoding erforderten und unlesbar und fehleranfällig würden
- **MUSS** Pfadsegmente in **kleinschreibendem `kebab-case`** schreiben (`/care-reminders`, nicht `/CareReminders` oder `/care_reminders`); Pfade sind laut RFC 3986 case-sensitive, daher wird Kleinschreibung fixiert, um `/Users` ≠ `/users`-Kollisionen zu vermeiden
- **MUSS** JSON-Body-Property-Namen und Query-Parameter-Namen in **`camelCase`** schreiben (`birthYear`, `includeDetached`)—die gewählte Konvention des Portfolios unter den gültigen Branchen-Alternativen (der Google/Microsoft-Ökosystem-Stil); sie wird einheitlich angewandt und nie mit `snake_case` innerhalb einer API vermischt
- **MUSS** Enumerations-Werte in `UPPER_SNAKE_CASE` schreiben (`status: "IN_PROGRESS"`), sodass sie eindeutige Konstanten distinkt von Freitext sind
- **SOLLTE** boolesche Properties als bejahendes Prädikat benennen (`isActive`, nicht `disabled`) und Timestamp-Properties mit einem `At`-Suffix, das einen RFC-3339-/ISO-8601-UTC-Wert trägt (`createdAt`)
- **MUSS** HTTP-Header in konventionellem `Title-Case` benennen (`If-None-Match`) und **DARF NICHT** ein `X-`-Präfix für Custom-Header einführen (laut RFC 6648)

### HTTP-Methoden-Semantik

- **MUSS** HTTP-Methoden gemäß ihrer RFC-9110-Semantik nutzen: `GET` liest (safe, cacheable), `POST` erzeugt oder stößt nicht-idempotente Verarbeitung an, `PUT` ersetzt vollständig oder erzeugt an einer bekannten URL, `PATCH` modifiziert partiell, `DELETE` entfernt
- **MUSS** `GET`, `HEAD` und `OPTIONS` **safe** halten (keine beobachtbare Zustandsänderung) und `GET`, `HEAD`, `PUT` und `DELETE` **idempotent**; `POST` und `PATCH` müssen nicht idempotent sein
- **MUSS** `PATCH` (nicht `PUT`) für ein partielles Update nutzen, weil ein `PUT`, das Felder auslässt, die ganze Ressource ersetzt und sie damit leeren würde
- **SOLLTE** einen Idempotenz-Mechanismus für nicht-idempotente Erzeugung anbieten, wo doppeltes Absenden ein reales Risiko ist—ein client-gelieferter `Idempotency-Key`-Request-Header, der zum selben Ergebnis replayt wird, oder ein natürlicher Sekundärschlüssel—statt sich darauf zu verlassen, dass der Client nie erneut sendet

### HTTP-Status-Codes

- **MUSS** den spezifischsten Status-Code zurückgeben, der zur Situation konsistent ist, mit Standard-Semantik als Basis:

  | Situation | Status |
  |---|---|
  | Erfolg mit Body | 200 |
  | Ressource erzeugt | 201 (+ `Location` der neuen Ressource) |
  | Für asynchrone Verarbeitung akzeptiert | 202 |
  | Erfolg, kein Body | 204 |
  | Conditional GET, unverändert | 304 |
  | Fehlerhafter / nicht parsebarer Request | 400 |
  | Nicht authentifiziert (keine oder ungültige Credentials) | 401 |
  | Authentifiziert, aber verboten | 403 |
  | Ressource nicht gefunden | 404 |
  | Methode auf Ressource nicht erlaubt | 405 |
  | Duplikat / konfligierender Zustand | 409 |
  | Precondition (`If-Match`) fehlgeschlagen | 412 |
  | Semantischer Validierungsfehler bei syntaktisch gültigem Body | 422 |
  | Rate-Limit überschritten | 429 |
  | Unbehandelter Server-Fehler | 5xx (kein internes Detail im Body) |

- **MUSS** einen **fehlerhaften** Request (nicht parsebarer Body, falscher Content-Type) als `400` von einem **semantisch ungültigen** (parst korrekt, verletzt aber eine Business- oder Feld-Regel) als `422` unterscheiden
- **DARF NICHT** einen Fehler mit einem `2xx`-Status und einem Error-Payload beantworten; die Statuszeile ist das primäre, maschinenlesbare Fehlersignal
- **SOLLTE**, wenn das Verbergen der Existenz einer Ressource für die Autorisierung relevant ist, `404` statt `403` zurückgeben, sodass die Antwort nicht leakt, dass die Ressource existiert

### Versionierung und Kompatibilität

- **MUSS** die API-Version als **Major-Version-Segment im URI-Pfad** tragen (`/v1/...`), die gewählte Versionierungsachse des Portfolios; das Segment trägt **nur die Major** (`/v1`, nie `/v1.0` oder `/v1.1`)
- **DARF NICHT** eine Version in jedem einzelnen Operationspfad über das eine führende Major-Segment hinaus kodieren und **DARF NICHT** die URI-Pfad-Achse mit header- oder query-basierter Versionierung innerhalb einer API vermischen
- **MUSS** Rückwärtskompatibilität innerhalb einer Major-Version wahren: eine Änderung ist **breaking**—und erfordert daher eine neue Major-Version—wenn sie ein Feld oder einen Endpunkt entfernt oder umbenennt, den Typ eines Felds oder einen Default ändert, ein neues Pflicht-Request-Feld hinzufügt, die Validierung verschärft oder den Identifier oder die URL einer Ressource ändert
- **MUSS** rein additive Änderung als **nicht-breaking** behandeln (und daher innerhalb der aktuellen Major-Version auslieferbar): neue optionale Felder, neue Endpunkte, neue Enum-Werte, neue optionale Query-Parameter
- **MUSS** Clients—und die Erwartung an Drittanbieter-Clients dokumentiert—so gestalten, dass sie **unbekannte Antwortfelder ignorieren**, sodass additive Änderung in der Praxis nicht-breaking bleibt
- **SOLLTE** Semantic Versioning auf die veröffentlichte Spezifikation der API (das OpenAPI-Dokument) anwenden, auch wenn nur die Major-Achse in der URL erscheint, sodass Minor-/Patch-Spec-Evolution nachverfolgbar ist

### Deprecation und Sunset

- **SOLLTE** eine deprecatete Ressource oder Version mit dem `Deprecation`-HTTP-Header (RFC 9745) signalisieren und, sobald ein Entfernungsdatum feststeht, mit dem `Sunset`-Header (RFC 8594), begleitet von einer `Link`-Relation, die auf Migrationsdokumentation zeigt
- **DARF NICHT** ein `Sunset`-Datum früher als das `Deprecation`-Datum setzen (RFC 9745 §4)
- **MUSS** jede Deprecation in der veröffentlichten Spezifikation der API spiegeln (`spec/project/api-documentation/`), sodass die dokumentierte Oberfläche und das Laufzeitsignal übereinstimmen
- **SOLLTE** die Nutzung einer deprecateten Oberfläche vor ihrem Sunset überwachen und für eine entfernte Version mit `410 Gone` statt einem stillen `404` antworten

### Collections: Filtern, Sortieren, Paginieren, Feldauswahl

- **MUSS** jede Collection paginieren, deren Größe unbegrenzt ist, und **SOLLTE** **cursor-basierte** Pagination (ein opakes, URL-sicheres `cursor`-Token plus ein `limit`) gegenüber offset-basierter Pagination für große oder häufig wechselnde Collections bevorzugen, weil ein Cursor unter nebenläufigen Inserts stabil ist
- **MUSS** einen Pagination-Cursor für den Client als **opak** behandeln und keine Autorisierung darin tragen; der Client folgt einem server-gelieferten Cursor oder Navigationslink und konstruiert nie selbst eine Pagination-URL
- **SOLLTE** Pagination-Navigation als server-gelieferte Links zurückgeben (zum Beispiel ein `next`-Link oder Link-Header), statt vom Client zu verlangen, die URL der nächsten Seite zusammenzusetzen
- **SOLLTE** konventionelle Query-Parameter zum Formen von Collections nutzen—`sort` für Ordnung, `fields` für spärliche Feldauswahl, ein `filter`-Ausdruck (oder diskrete Feld-Filter) zum Eingrenzen—und das Parameter-Vokabular über die ganze API konsistent halten
- **SOLLTE** vermeiden, standardmäßig einen exakten Gesamtzähler zu berechnen, wenn der zugrundeliegende Store das teuer macht; ihn als explizites Opt-in statt als garantiertes Feld anbieten

### Fehler-Body

- **MUSS** Fehler als **RFC-9457-Problem-Details** mit dem Media-Type `application/problem+json` zurückgeben, unter Nutzung der Standard-Member `type` (eine URI, die die Problemklasse identifiziert, dokumentiert), `title`, `status`, `detail` und `instance`
- **MUSS** einen stabilen, maschinenlesbaren Fehlercode als `camelCase`-Extension-Member `code` enthalten (ein `UPPER_SNAKE_CASE`-String-Enum, das Teil des API-Contracts ist), sodass Clients auf `code` statt auf das Parsen von `detail` verzweigen; der Code KANN zusätzlich in einem Response-Header gespiegelt werden
- **MUSS** Feld-genaue Validierungsfehler in einem `errors`-Extension-Array melden, jeder Eintrag mit einem **JSON Pointer** in den Request-Body (`pointer: "#/emailAddress"`), einem per-Feld-`code` und einem menschenlesbaren `detail`; der JSON Pointer erbt die `camelCase`-Property-Namen des Bodys und hält die Referenz konsistent
- **MUSS** jeden Fehler-Extension-Member in `camelCase` und mit einem Buchstaben beginnend benennen (RFC 9457 §3.2), sodass der Body einheitlich gecast ist und ein gültiges Problem-Details-Dokument bleibt
- **DARF NICHT** einen Stack-Trace, eine rohe Treiber- oder Exception-Meldung, eine gerenderte Datenbank-Query, einen internen Host oder Pfad oder ein Secret in einen Fehler-Body legen—ein Leckage-Befund, der zugleich in `spec/project/code-security-audit/` zeigt
- **SOLLTE** einen frischen, per-Vorkommen erzeugten Korrelations-Identifier (zum Beispiel `traceId`) als Extension-Member zurückgeben, sodass ein client-gemeldeter Fehler in Server-Logs auffindbar ist, und **DARF NICHT** ihn als statische Konstante emittieren

### Transport- und URL-Sicherheit

- **MUSS** die API **nur über HTTPS** ausliefern; Credentials, Tokens und API-Keys reisen verschlüsselt in transit
- **DARF NICHT** Passwörter, Tokens, API-Keys oder andere Secrets in den URL-Pfad oder Query-String legen, wo sie in Server-Logs, Browser-History, Proxy-Logs und den `Referer`-Header lecken; Secrets reisen in einem Request-Header (zum Beispiel `Authorization: Bearer <token>`) oder im Body
- **MUSS** jeden Endpunkt mit zur Ressource passender Authentifizierung und Autorisierung absichern; ein öffentlicher Endpunkt ist eine bewusste, dokumentierte Ausnahme, kein Default
- **SOLLTE** den Request-`Content-Type` validieren und eine Methoden-Allowlist pro Ressource durchsetzen (mit `405` / `415` passend antworten) und **SOLLTE** Rate-Limiting anwenden (mit `429` und einem `Retry-After`-Header antworten), um vor unbegrenztem Ressourcenverbrauch zu schützen

### Hypermedia

- **MUSS** Richardson Maturity Level 2 erreichen (echte Ressourcen, Methoden und Status-Codes); **volles HATEOAS (Level 3) ist nicht erforderlich**
- **SOLLTE** pragmatische Navigationslinks dort einschließen, wo sie client-seitige URL-Konstruktion beseitigen (ein `next`-Pagination-Link, ein `Location` der erzeugten Ressource, ein Link zur verwandten Ressource), ohne ein volles Hypermedia-Control-Vokabular zu übernehmen

## Akzeptanzkriterien

- [ ] Ein neuer Endpunkt nutzt einen pluralen, ressourcen-orientierten, englischen, kleinschreibenden `kebab-case`-Pfad ohne Verb-Segment, und eine Nicht-CRUD-Operation nutzt Doppelpunkt-Custom-Method-Notation
- [ ] JSON-Body- und Query-Parameter-Namen sind `camelCase`; Enum-Werte sind `UPPER_SNAKE_CASE`; kein `snake_case` erscheint im Wire-Contract
- [ ] Die API ist unter einem einzigen `/v{major}`-Pfadsegment erreichbar, das nur die Major-Version trägt
- [ ] Ein Reviewer kann eine vorgeschlagene Änderung gegen die Breaking-Change-Liste der Spec als breaking oder nicht-breaking klassifizieren, und ein Breaking Change wird in eine neue Major-Version geleitet statt in-place ausgeliefert
- [ ] Eine grandfathered ausgelieferte Major-Version wird nicht für rückwirkende Konformität markiert, während eine neue Major-Version am vollen Standard gemessen wird
- [ ] Jede Situation in der Status-Code-Tabelle mappt auf den gelisteten Code in einem Beispiel-Handler-Satz; ein semantischer Validierungsfehler liefert `422`, ein fehlerhafter Request liefert `400`, und kein Fehler liefert `2xx`
- [ ] Eine Fehlerantwort ist `application/problem+json`, trägt `type`/`title`/`status`/`detail`/`instance` plus ein `camelCase`-`code`, und ein Validierungsfehler listet Feld-Fehler in einem `errors`-Array mit JSON Pointern
- [ ] Ein Fehler-Body enthält keinen Stack-Trace, keine rohe Exception, keine gerenderte Query und kein Secret; ein Korrelations-Identifier wird, wenn vorhanden, per Vorkommen erzeugt
- [ ] Die API wird über HTTPS ausgeliefert und kein Endpunkt akzeptiert ein Credential über die URL oder den Query-String
- [ ] Eine deprecatete Oberfläche nutzt, wenn signalisiert, `Deprecation`-/`Sunset`-Header mit einem `Sunset`-Datum nicht früher als das `Deprecation`-Datum, und eine entfernte Version antwortet mit `410 Gone`

## Referenzen

- [R1] Schwester-Spec—wie die API dokumentiert wird (verweist Design-Qualität hierher): `spec/project/api-documentation/`
- [R2] Schwester-Spec—read-only-Fehlerbehandlungs-Konformitätsprüfung (misst gegen den hier definierten Fehler-Contract): `spec/project/api-error-handling/`
- [R3] Whole-Codebase-Security-Audit (Fehler-Body-Leckage-Befunde zeigen hierher): `spec/project/code-security-audit/`
- [R4] Wire-Level-JSON-Schema-Konventionen außerhalb Casing/Fehlerform: `spec/project/yaml-json-schema/`
- [R5] Lokalisierung von menschenlesbarem Payload-Text: `spec/project/i18n-completeness/`
- [R6] RFC 3986—URI Generic Syntax (ASCII, Case-Sensitivity): <https://www.rfc-editor.org/rfc/rfc3986>
- [R7] RFC 9110—HTTP Semantics (Methoden, die meisten Status-Codes, 422 §15.5.21, `Retry-After`): <https://www.rfc-editor.org/rfc/rfc9110>
- [R8] RFC 4918 §11.2—ursprüngliche 422-Definition; RFC 6585 §4—429-Definition (keine davon Eigentum von RFC 9110): <https://www.rfc-editor.org/rfc/rfc4918> · <https://www.rfc-editor.org/rfc/rfc6585>
- [R9] RFC 9457—Problem Details for HTTP APIs (kanonischer Fehler-Body): <https://www.rfc-editor.org/rfc/rfc9457>
- [R10] RFC 9745—der `Deprecation`-Header; RFC 8594—der `Sunset`-Header: <https://www.rfc-editor.org/rfc/rfc9745> · <https://www.rfc-editor.org/rfc/rfc8594>
- [R11] OWASP REST Security Cheat Sheet; OWASP API Security Top 10 (2023): <https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html> · <https://owasp.org/API-Security/editions/2023/en/0x11-t10/>
- [R12] Konsens-Quell-Guidelines—Microsoft Azure, Google AIP, Zalando, JSON:API: <https://github.com/microsoft/api-guidelines> · <https://google.aip.dev/> · <https://opensource.zalando.com/restful-api-guidelines/> · <https://jsonapi.org/format/>

## Offene Fragen

- Sollte diese Spec von `Portfolio-Scope: local` auf `portfolio` promotet werden, sodass sie portfolio-weit vererbt wird (laut `spec/project/portfolio-inherited-spec-layer/`)? Sie ist als portfolio-weiter Standard verfasst, aber die Promotion ist ein expliziter Maintainer-Akt und ihre beiden Schwester-Specs sind derzeit `local`; bleibt `local`, bis bewusst promotet.
- Sollte eine read-only-Design-Review-Capability (ein `rest-api-design-scanner`-Agent und/oder ein Overlay in `spec/project/source-code-review/`) hinzugefügt werden, um Konformität mechanisch zu prüfen, analog zum `api-documentation`-/`api-error-handling`-Tooling-Muster? Auf einen Folge-Schritt verschoben.
- Sollte der kanonische Fehler-Body als wiederverwendbares OpenAPI-`components.schemas`-Fragment angeboten werden (Problem Details + die `code`-/`errors`-Extensions), sodass Projekte es importieren statt neu deklarieren?
