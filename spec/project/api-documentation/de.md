# API-Dokumentations-Best-Practices

Status: draft

## Kontext

Ein Repository, das eine HTTP-API ausliefert, schuldet seinen Konsumenten einen maschinenlesbaren Contract. Ohne ihn häufen sich drei Fehlermodi an: Konsumenten reverse-engineeren Endpunkte aus dem Quellcode oder per Probe-Requests; die vorhandene Dokumentation driftet still von der laufenden API weg; und nachgelagerte Capabilities, die einen publizierten Contract konsumieren — Contract-Testing, Katalog-Generierung, Client-Generierung — haben nichts Verlässliches als Grundlage. `spec/project/yaml-json-schema/` schließt OpenAPI-Schema-Object-Konventionen explizit aus und verweist sie an eine eigene Portfolio-Regel; diese Spec ist diese Regel.

Diese Spec definiert, wie ein API-ausliefererndes Repository seine HTTP-API mit einem OpenAPI-Dokument dokumentiert, sodass ein Review die Konformität mechanisch prüfen kann. Ihr Kern ist tool-agnostisch: Sie benennt Spectral als Referenz-Linter, verlangt ihn aber nie. Die Spec wird durch den `api-documentation-audit`-Skill und den read-only `api-documentation-scanner`-Agent (`nolte-engineering`-Plugin) operationalisiert, nach demselben Capability-Muster wie `dockerfile-best-practices` und `monitoring-observability`. Sie ist die Schwester-Spec zu `spec/project/api-error-handling/`: Jene Spec besitzt den Fehlerantwort-Contract, diese besitzt die Dokumentations-Oberfläche, die ihn publiziert.

Leser: Entwickler, die eine API dokumentieren; Reviewer und das Audit-Tooling, die Konformität prüfen; Skill-Autoren, die die Audit-Capability pflegen. Anforderungs-Herkunft: `project/requirements/api-documentation.md` (erhoben 2026-07-24).

## Ziele

- Ein kanonischer, maschinenlesbarer API-Contract (ein OpenAPI-Dokument) pro API-auslieferndem Repository, auffindbar an einem konventionellen Ort
- Vollständigkeit: Jede Operation ist allein aus dem Dokument navigierbar und verständlich, ohne Handler-Quellcode zu lesen
- Flavour-Neutralität: Spec-first (handgeschrieben) und code-first (framework-generiert) sind gleichermaßen erstklassig; jede Qualitätsanforderung gilt am publizierten Artefakt, unabhängig davon, wie es entsteht
- Auditierbarkeit: Ein read-only Scanner kann Konformität mechanisch feststellen und Befunde pro Dokument berichten
- Drift-Sichtbarkeit: Abweichungen zwischen dem publizierten Dokument und der laufenden API werden über die docs-freshness-Prüfungen des Repositories sichtbar, statt still zu verrotten

## Nicht-Ziele

- AsyncAPI-, GraphQL- und gRPC-Dokumentation — außerhalb des normativen Kerns dieser Spec; jede verdient ihr eigenes Profil oder ihre eigene Spec, sobald ein Portfolio-Repository sie braucht
- Das Verfassen der Dokumentations-Inhalte selbst oder der Prosa-Developer-Portal-Schicht darum herum — diese Spec regelt das Contract-Artefakt, keine Tutorials oder Guides
- REST-API-Design-Qualität (Ressourcen-Modellierung, Versionierungsstrategie, Paginierungs-Konventionen) — diese Spec beurteilt, wie die API dokumentiert ist, nicht wie sie entworfen ist
- Die Definition des Fehlerantwort-Contracts — `spec/project/api-error-handling/` besitzt die Fehler-Body-Form; diese Spec verlangt nur, dass Fehlerantworten dagegen dokumentiert sind
- Allgemeine JSON-Schema-Autorenkonventionen außerhalb von OpenAPI-Dokumenten — die bleiben bei `spec/project/yaml-json-schema/`; OpenAPI-Schema-Object-Konventionen leben hier
- Rendering- und Publishing-Infrastruktur (Swagger UI, Redoc, Hosting) — eine Entscheidung pro Repository

## Anforderungen

### Dokument-Präsenz und Format

- **MUSS** für jede HTTP-API, die das Repository ausliefert, ein OpenAPI-Dokument publizieren: entweder ins Repository eingecheckt oder reproduzierbar aus dem Code exportierbar (siehe die Flavour-Regeln unten)
- **MUSS** OpenAPI 3.0 oder höher verwenden; ein Swagger-2.0-Dokument ist ein Befund
- **SOLLTE** OpenAPI 3.1 anstreben
- **MUSS** ein kanonisches Entry-Point-Dokument auffindbar machen: an einem konventionellen Ort (zum Beispiel `openapi.yaml`, `openapi.json` oder unter `docs/` oder `api/`) oder in der Repository-Dokumentation deklariert; das Aufteilen des Dokuments in mehrere Dateien via `$ref` ist zulässig, aber der Entry-Point **MUSS** zu einem einzigen validen Dokument bündelbar sein
- **MUSS** in einem code-first Repository ein reproduzierbares Export-Kommando bereitstellen (zum Beispiel ein Taskfile-Target oder einen dokumentierten CLI-Aufruf), das das publizierte Dokument aus dem Code regeneriert, damit Scanner und CI dasselbe Artefakt prüfen, das Konsumenten sehen
- Spec-first und code-first sind gleichermaßen akzeptable Flavours; keine Anforderung dieser Spec hängt davon ab, welcher Flavour das Dokument erzeugt hat

### Info-Vollständigkeit

- **MUSS** `info.title`, `info.version` und `info.description` mit nicht-leeren, aussagekräftigen Werten füllen; `info.version` spiegelt die tatsächliche API-Version, keinen Platzhalter
- **SOLLTE** `info.contact` und `info.license` deklarieren
- **SOLLTE** `servers`-Einträge mit einer `description` pro Umgebung deklarieren

### Per-Operation-Contract

- **MUSS** jeder Operation eine eindeutige, stabile `operationId` geben
- **MUSS** jeder Operation mindestens ein Tag zuweisen und jedes verwendete Tag im Top-Level-`tags`-Array mit einer `description` deklarieren
- **MUSS** jeder Operation ein `summary` geben; eine längere `description` **SOLLTE** vorhanden sein, wo das Summary allein das Verhalten nicht erklärt
- **MUSS** jeden Parameter mit einer `description` und einem `schema` dokumentieren und `required` korrekt setzen
- **MUSS** jeden Request-Body mit einem Schema dokumentieren; ein Request-Beispiel **SOLLTE** vorhanden sein

### Response- und Schema-Hygiene

- **MUSS** jede Success-Response einer Operation mit einem Response-Schema dokumentieren
- **MUSS** die Fehlerantworten dokumentieren, die die API tatsächlich zurückgibt, pro Status-Code; das Fehler-Body-Schema folgt dem Fehler-Contract des Projekts per `spec/project/api-error-handling/` und wird hier nicht neu definiert
- **SOLLTE** Response-Beispiele für die primäre Success-Response jeder Operation bereitstellen
- **SOLLTE** gemeinsame Formen als benannte `components.schemas`-Einträge definieren, statt Inline-Schemas zu wiederholen; für Schema-Autorenfragen, die nicht OpenAPI-spezifisch sind, gilt `spec/project/yaml-json-schema/`

### Security-Dokumentation

- **MUSS**, wenn die API Aufrufer authentifiziert, die Authentifizierungsmechanismen als `components.securitySchemes` dokumentieren und sie in per-Operation- (oder Top-Level-) `security`-Requirements referenzieren
- **MUSS** bewusst öffentliche Operationen erkennbar machen (zum Beispiel ein explizites leeres `security: []`), damit ein fehlendes Requirement von einem offenen Endpunkt unterscheidbar ist
- **DARF NICHT** echte Credentials, Tokens oder Secrets in Beispiele einbetten — nur Platzhalter-Werte

### Lint-Gate und Drift

- **SOLLTE** ein Lint-Gate über das OpenAPI-Dokument in CI laufen lassen; Spectral mit seinem Default-OpenAPI-Ruleset ist der Referenz-Linter — eine Referenz, nie eine Pflicht, und jeder Linter, der äquivalente Regeln durchsetzt, erfüllt dies
- **KANN** das Referenz-Ruleset um projektspezifische Lint-Regeln erweitern
- **SOLLTE** in die optionale Repository-Level-Kategorie "API-Referenz vs. Code" von `spec/project/docs-freshness/` einsteigen, damit Drift zwischen dem publizierten Dokument und der Implementierung geprüft wird; ein code-first Repository **SOLLTE** das Dokument in CI re-exportieren und bei einem unerklärten Diff fehlschlagen

### Audit-Verhalten

- **MUSS** (Audit-Tooling): Wenn das auditierte Repository eine HTTP-API ausliefert, aber kein OpenAPI-Dokument auffindbar ist — weder eingecheckt noch exportierbar —, dies als schwersten (critical) Befund des Reports aufnehmen und das Audit fortsetzen; nie abbrechen und nie still überspringen
- **MUSS** (Audit-Tooling): Wenn mehrere OpenAPI-Dokumente in einem Repository existieren (zum Beispiel eines pro Service), jedes Dokument auditieren und Befunde pro Dokument berichten
- Das Audit ist beratend: Es berichtet und empfiehlt; ob das Lint-Gate CI blockiert, bleibt eine Entscheidung pro Repository unter dem SOLLTE oben

## Akzeptanzkriterien

- [ ] Ein Repository mit einer HTTP-API und einem eingecheckten oder exportierbaren OpenAPI-3.x-Dokument besteht den Präsenz-Check; ein Swagger-2.0-Dokument erzeugt einen Befund
- [ ] Eine Operation ohne `operationId`, Tag oder `summary` wird als Befund berichtet, attribuiert auf Pfad und Methode
- [ ] Ein Parameter ohne `description` oder `schema` wird berichtet
- [ ] Ein dokumentierter Status-Code ohne Response-Schema wird berichtet; die Fehler-Form-Prüfung zeigt auf `spec/project/api-error-handling/`, statt dessen Regeln zu duplizieren
- [ ] Eine API, die Aufrufer authentifiziert, aber keine `components.securitySchemes` deklariert, erzeugt einen Befund
- [ ] Ein Repository mit einer HTTP-API, aber ohne auffindbares OpenAPI-Dokument erzeugt einen Critical-Befund, während das Audit trotzdem durchläuft
- [ ] Ein Repository mit mehreren OpenAPI-Dokumenten erhält einen Report pro Dokument
- [ ] Ein per `$ref` aufgeteiltes Dokument mit auffindbarem Entry-Point bündelt sauber; ein Multi-File-Dokument ohne auffindbaren Entry-Point erzeugt einen Befund
- [ ] Der Audit-Report benennt die geprüften Dokumente, die OpenAPI-Version, den erkannten Flavour (spec-first oder code-first) und wie jedes Dokument entdeckt wurde
- [ ] Der Audit-Skill und der Scanner-Agent zitieren diese Spec in ihrem Body oder ihrer `description`

## Referenzen

- [R1] Fehlerantwort-Contract, an den die Fehler-Dokumentationsregeln dieser Spec delegieren: `spec/project/api-error-handling/`
- [R2] Drift-Anker — optionale Repository-Level-Kategorie "API-Referenz vs. Code": `spec/project/docs-freshness/`
- [R3] JSON-Schema-Autorenkonventionen und die Grenze, die diese Spec vervollständigt: `spec/project/yaml-json-schema/`
- [R4] Code-Level-Review-Dimension D8 (API-Contracts und Dokumentation): `spec/project/source-code-review/`
- [R5] Contract-Testing-Konsument eines publizierten OpenAPI-Dokuments: `spec/project/test-tier-contract/`
- [R6] Katalog-Konsument von OpenAPI-Dateien als API-Entitäten: `spec/project/backstage-catalog-generation/`
- [R7] Schweregrad-Skala für Audit-Reports: `spec/claude/review-plan/`
- [R8] OpenAPI-Spezifikation: <https://spec.openapis.org/oas/latest.html>
- [R9] Spectral (Referenz-Linter): <https://github.com/stoplightio/spectral>

## Offene Fragen

_Derzeit keine — die tragenden Entscheidungen (Protokoll-Scope, Versions-Untergrenze, Flavour-Haltung, Lint-Gate-Stärke) wurden in der Anforderungserhebung vom 2026-07-24 aufgelöst._
