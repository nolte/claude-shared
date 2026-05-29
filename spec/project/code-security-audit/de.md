# Whole-Codebase-Security-Audit

Status: draft

## Kontext

Für den Alltags-Flow des Portfolios existieren bereits zwei Security-Review-Oberflächen, und beide sind bewusst eng: Der `security-review`-CLI-Skill reviewt das **Diff** des aktuellen Branches, und `code-review` reviewt geänderte Zeilen auf Korrektheit. Keiner führt ein tiefes, repositoryweites OWASP-Audit durch, das Befunde *über* Dateien hinweg korreliert — die Authentifizierungs-Middleware gegen die Access-Control-Guards, die Data-Access-Schicht gegen die Injection-Oberfläche, das Secret-Handling gegen die Logging-Pfade, die AI/RAG-Pipeline gegen Prompt-Injection und SSRF. Ein Diff-Review kann einen fehlenden Tenant-Filter in einem Endpunkt nicht sehen, den der aktuelle Branch nie berührt hat; ein Whole-Codebase-Audit kann es.

Diese Spec regelt dieses tiefere Audit, operationalisiert durch den `code-security-reviewer`-Agent (`distribution: plugin`). Der Agent ist der generalisierte, **read-only** Nachfolger eines projektlokalen Reviewers, der das Framework einer App (FastAPI/ArangoDB/pgvector), ihre Spec-Dokument-Referenzen, ihre Tenant-Key-Konvention und — entscheidend — auch *Quelldateien zur Anwendung von Fixes editierte* hartcodiert hatte. Die Portfolio-Form lässt die Fix-Verantwortung fallen (Single-Responsibility: sie auditiert und berichtet; ein Mensch oder ein Folge-Skill wendet Fixes an) und entdeckt den Stack, statt einen anzunehmen.

Leser: Agent-Autoren, die den Auditor pflegen; Reviewer, die seinen Report konsumieren; Entwickler, die nach einem Feature oder vor einem Release einen vollen Security-Durchlauf machen.

## Ziele

- Ein Whole-Codebase-OWASP-ausgerichtetes Security-Audit bereitstellen, das Befunde über Dateien hinweg korreliert und das diff-skopierte `security-review` und `code-review` ergänzt — nicht dupliziert
- Strikt read-only bleiben: Das Audit findet und berichtet, es editiert nie Quellcode, unterdrückt keine Befunde und ändert kein Verhalten
- In der Methodik stack-agnostisch bleiben, während konkrete Patterns an den erkannten Backend- und Frontend-Stack des Projekts angepasst werden
- Einen nach Schweregrad klassifizierten, cross-file-korrelierten Report erzeugen, auf den ein Mensch reagieren kann, mit einer Datei:Zeile-Zuordnung pro Befund
- Eine explizite Grenze zum Diff-Review, zum Dependency-/CVE-Audit und zum Anforderungs-/Spec-Security-Review ziehen, sodass der Agent nur für das Whole-Codebase-Code-Audit aufgerufen wird

## Nicht-Ziele

- Diff-skopiertes Review der Änderungen des aktuellen Branches — im Besitz des `security-review`-CLI-Skills; dieses Audit ist repositoryweit
- CVE-/Dependency-/Lockfile-Schwachstellen-Scanning — im Besitz von `spec/project/dependency-audit/`; dieses Audit betrifft den eigenen Code des Projekts, nicht die bekannten CVEs seiner Dependencies
- Security-Review von *Anforderungen oder Spezifikationen* (die beabsichtigte Security-Posture) statt von implementiertem Code — ein separates Anliegen; dieses Audit liest Code, nicht die Security-Anforderungen der Spec
- **Anwenden von Fixes** — der projektlokale Vorgänger editierte Quellcode; der Portfolio-Agent ist read-only, und der Fix-Schritt gehört einem Menschen oder einem separaten Skill, sodass das Audit single-responsibility bleibt
- Ausführen von Third-Party-SAST-Tooling (semgrep, bandit, CodeQL) — der Agent führt LLM-getriebene Pattern-Analyse durch; dies bleibt hier außer Scope. Ein künftiger `sast-runner`-Skill kann Befunde emittieren, die der Operator diesem Agent als zusätzlichen Kontext bereitstellt — der read-only-Agent führt den Runner niemals selbst aus

## Anforderungen

### Read-only-Vertrag

- **MUSS [MUST]** strikt read-only sein: nur Lese- und Such-Tools (`Read`, `Grep`, `Glob`) deklarieren, kein `Edit`, `Write`, `NotebookEdit` deklarieren und keine Fixes anwenden; die einzige Ausgabe ist der Audit-Report
- **DARF NICHT [MUST NOT]** Befunde im Quellcode unterdrücken, herabstufen oder annotieren (kein Einfügen von `# nosec` / `# noqa` / eslint-disable); Berichten ist die einzige Aktion
- **MUSS [MUST]** den Report in seiner finalen Nachricht zurückgeben; ihn nach `.audits/` zu persistieren (per `spec/claude/review-plan/`) ist Aufgabe des aufrufenden Skills oder Operators, nicht des read-only-Agents. Wenn ein aufrufender Skill ihn persistiert, liegt der Report unter `.audits/code-security-audit/<target-slug>.md` per `spec/claude/review-plan/` §File location and naming; ein Re-Run überschreibt die einzige kanonische Datei, statt timestamped Snapshots zu akkumulieren

### Discovery und Stack-Anpassung

- **MUSS [MUST]** die Backend- und Frontend-Source-Roots entdecken, statt die Pfade eines Projekts hartzucodieren, und berichten, welche Roots und Globs gescannt wurden
- **MUSS [MUST]** den Stack des Projekts erkennen (Web-Framework, Data-Access-Schicht, Frontend-Framework) und konkrete Schwachstellen-Patterns daran anpassen — die Methodik (OWASP-Kategorien) ist fix, die Beispiel-Patterns sind stack-spezifisch
- **MUSS [MUST]**, wenn das Projekt eine security-relevante Konvention deklariert (einen Multi-Tenant-Isolations-Key, einen Error-Handling-Vertrag, ein Auth-Schema), den Code gegen diese deklarierte Posture auditieren; ohne deklarierte Posture gegen OWASP-Defaults auditieren und die Annahme angeben

### Audit-Abdeckung

- **MUSS [MUST]** die OWASP-Top-10-Kategorien abdecken und über Dateien hinweg korrelieren statt pro Datei: Injection (SQL/NoSQL/AQL/Command/Path-Traversal und Frontend-XSS), Broken Authentication (Token-Validierung, Passwort-Hashing, Session-Handling), Broken Access Control (Autorisierung an jedem zustandsändernden Endpunkt, **Multi-Tenant-Isolation**, IDOR), Security Misconfiguration (CORS, Security-Header, Debug-Flags, Information Disclosure in Error-Responses), Cryptographic Failures (Hashing-Stärke, Secret-Speicherung) und Software-/Daten-Integritäts-Belange
- **MUSS [MUST]** **Secret-Handling** über den gesamten Baum auditieren: hartcodierte Credentials, Secrets in Quellcode / Compose / Chart-Values / Seed-Daten, Secrets in Logs oder Error-Responses, schwache Default-Secrets
- **MUSS [MUST]** **Input-Validierung** (Schema-Validierung auf Request-Bodies, Feld-Grenzen, Datei-Upload-Validierung, Pagination-/Sort-Allowlists) und **Rate-Limiting** auf sensiblen Endpunkten (Login, Registrierung, Passwort-Reset) auditieren
- **SOLLTE [SHOULD]** **AI/LLM/RAG-Security** auditieren, wenn das Projekt eine solche Pipeline hat: Prompt-Injection (User-Input darf nicht als Instruktionen in den System-Prompt gelangen), SSRF über Embedding-/Model-Service-URLs, API-Key-Handling und Ressourcen-Erschöpfungs-Limits (`max_tokens`, Top-k, Query-Längen-Caps)
- **SOLLTE [SHOULD]** **Frontend-spezifische** Security auditieren: Token-Speicherung (Access-Token nicht im langlebigen `localStorage`; Refresh-Token als HttpOnly-Cookie), sensible Daten im Client-State, XSS über `dangerouslySetInnerHTML` / unescapte Ausgabe und Route-Level-Auth-Guards
- **MUSS [MUST]** den Multi-Tenant-Isolations-Check, wenn das Projekt multi-tenant ist, als erstklassigen korrelierten Check behandeln: Jeder tenant-scoped Datenpfad filtert nach dem Tenant-Identifier, und Cross-Tenant-Zugriff liefert Not-Found statt Forbidden (kein Existenz-Leak)

### Ausgabe

- **MUSS [MUST]** einen einzigen nach Schweregrad klassifizierten Report emittieren, der das portfolioweite Schweregrad-Vokabular aus `spec/claude/review-plan/` §Severity scale verwendet (Critical / Warning / Suggestion / Info, wortgetreu in Title Case) — er DARF NICHT [MUST NOT] ein P0–P3- oder kritisch/hoch/mittel/niedrig-Schema erfinden; jeder Befund trägt einen Titel, eine OWASP-Kategorie, eine Datei:Zeile-Zuordnung, das Problem und eine konkrete Remediation-Empfehlung (beschrieben, nicht angewendet)
- **MUSS [MUST]** mit einer Gesamtbewertungs-Tabelle anführen (pro OWASP-Kategorie: Bewertung + Befund-Anzahl) und, für Multi-Tenant-Projekte, einer Tenant-Isolations-Matrix (Endpunkt-Gruppe × Tenant-Filter × Autorisierungs-Check × Status)
- **MUSS [MUST]** den Audit-Scope angeben (gescannte Roots, Globs, erkannter Stack, deklarierte Posture oder OWASP-Default-Annahme), sodass das Audit reproduzierbar ist
- **SOLLTE [SHOULD]** bestätigte Befunde von vermuteten-aber-unsicheren unterscheiden, sodass der Konsument triagieren kann; ein unsicherer Befund wird berichtet, nicht still verworfen
- **MUSS [MUST]** diese Spec im Agent-Body oder in der `description` zitieren

## Akzeptanzkriterien

- [ ] Der Agent deklariert nur `Read`, `Grep`, `Glob` (keine Schreib-/Edit-/Ausführungs-Tools) und wendet keine Quellcode-Edits an und fügt keine Befund-Unterdrückungs-Kommentare ein
- [ ] Das Audit laufen zu lassen erzeugt einen Report, klassifiziert nach dem Schweregrad-Vokabular aus `spec/claude/review-plan/` §Severity scale (Critical / Warning / Suggestion / Info), dessen Befunde jeweils einen Titel, OWASP-Kategorie, Datei:Zeile, Problem und eine beschriebene (nicht angewendete) Remediation tragen
- [ ] Der Report führt mit einer Pro-OWASP-Kategorie-Bewertungs-Tabelle an und gibt die gescannten Roots, Globs und den erkannten Stack an
- [ ] Der Report eines Multi-Tenant-Projekts enthält eine Tenant-Isolations-Matrix und markiert jeden tenant-scoped Pfad ohne Tenant-Filter als Critical
- [ ] Ein hartcodiertes Credential oder ein Secret in Quellcode / Config / Logs wird als Critical mit einer Datei:Zeile berichtet
- [ ] Ein injection-anfälliger Data-Access-Aufruf (string-interpolierte Query) wird mit der beschriebenen parametrisierten Remediation berichtet
- [ ] Ein Projekt mit AI/RAG-Pipeline hat Prompt-Injection- und SSRF-Checks im Report repräsentiert; ein Projekt ohne eine solche lässt sie ohne spuriosen Befund weg
- [ ] Der Report unterscheidet bestätigte von vermuteten Befunden
- [ ] Das Audit ist abgegrenzt von `security-review` (Diff-Scope), `dependency-audit` (CVE-Scope) und Anforderungs-Level-Security-Review, und die `description` des Agents nennt diese Negativfälle

## Referenzen

- [R1] Agent-Autoren-Regeln und Read-only-Tool-Disziplin: `spec/claude/agent-management/`
- [R2] Skill-vs-Agent-Entscheidungsregel und Rationale-Abschnitts-Anforderung: `spec/claude/skill-vs-agent/`
- [R3] CVE-/Dependency-Schwachstellen-Audit (gegen diese Spec abgegrenzt): `spec/project/dependency-audit/`
- [R4] Review-Plan-/Audit-Ausgabe-Persistenz-Konventionen: `spec/claude/review-plan/`
- [R5] OWASP Top 10 (2021): <https://owasp.org/Top10/>
- [R6] Kanonisches portfolioweites Schweregrad-Vokabular (Critical / Warning / Suggestion / Info): `spec/claude/review-plan/` §Severity scale

## Offene Fragen

- Reziproke Grenze zu einer künftigen Architektur-Level-Threat-Modeling-Spec. Erneut prüfen, wenn eine `spec/project/threat-modeling/` (oder eine äquivalent benannte Architektur-Level-Threat-Modeling-Spec) unter `spec/` angelegt wird ODER ein Roadmap-Item dafür in `project/roadmap.md` eröffnet wird. In diesem Moment einen reziproken Abgrenzungs-Bullet sowohl zu den §Nicht-Zielen dieser Spec als auch zu den Nicht-Zielen/Zielen der Threat-Modeling-Spec hinzufügen. Heute prüfbares Prädikat: `test -d spec/project/threat-modeling` und grep in `project/roadmap.md` nach einem Threat-Modeling-Eintrag—beide false am 2026-05-29 (post-#228).
