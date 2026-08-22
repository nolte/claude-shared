# Test-Stufe: Static Analysis

Status: draft

## Kontext

Static Analysis ist die **Fundamentstufe** der in `spec/project/test-pyramid-foundation/` definierten Testpyramide — die breite, billige, schnelle Basis, auf der jede andere Stufe ruht. Sie ist die einzige Stufe, die Code verifiziert, **ohne ihn auszuführen**: Sie liest Quell- (oder kompilierte) Artefakte und meldet Defekte allein aus ihrer Struktur, ohne Testfälle und ohne laufendes System [R5], [R6]. Empirisch ist sie kein redundantes Duplikat der dynamischen Stufen — statische und dynamische Analyse finden weitgehend **nicht überlappende** Defektmengen, sodass die Fundamentschicht Probleme erreicht, die Unit- und Integrationstests nie erreichen [R6], [R7].

Diese Spezifikation ist die stufenspezifische Realisierung der **invarianten Form** des Fundaments für die Static-Analysis-Stufe. Sie füllt jedes von dieser Form geforderte Feld (Zweck und Umfangsgrenze, Isolation, Geschwindigkeit und Determinismus, Ausführungs-Platzierung, Traceability, kanonische Anti-Patterns, optionales Referenzprofil) und ergänzt die stufenspezifische Governance — die Sub-Kategorien-Taxonomie, die SAST/SCA-Grenze, Type-Checking als erstklassige Sub-Stufe und das Baseline-and-Ratchet-Modell für die Einführung von Analyse auf Legacy-Code.

Sie ist bewusst **werkzeug-agnostisch**: Die bindenden Anforderungen nennen nie ein Werkzeug. Die konkreten Linter, Type-Checker, Formatter und SAST-Engines, die die Stufe realisieren, erscheinen nur als illustratives Referenzprofil.

**Verhältnis zu den anderen Specs.** Diese Stufe ist nach Verantwortung abgegrenzt, nicht durch Überschneidung:

- `spec/project/test-pyramid-foundation/` [R1] besitzt das Stufenmodell und den Platz dieser Stufe darin (die Fundamentschicht). Diese Spec detailliert die Stufe; sie wiederholt das Modell nicht.
- `spec/project/quality-gate/` [R2] **führt** die schnellen Stufen (Lint, Typecheck, Test) als einzelnen Aufruf aus und besitzt Ausführungsmechanik und Ausgabeform. Diese Spec definiert, *was die Static-Analysis-Stufe enthalten muss und wie sie gatet*; quality-gate definiert, *wie sie ausgeführt wird*.
- `spec/project/dependency-audit/` [R3] besitzt das CVE-Scanning von Dritt-Abhängigkeiten (Software Composition Analysis, SCA). Das SAST dieser Spec analysiert **First-Party-Quellcode**; sie **DARF NICHT [MUST NOT]** die Dependency-CVE-Verantwortung beanspruchen — diese Grenze ist tragend [R8], [R9].
- Die **Unit-Stufe** (`spec/project/test-tier-unit/`, Geschwister) ist die erste *ausführende* Stufe direkt über Static Analysis; die Grenze lautet „analysiert Code-Struktur" vs. „führt den Code aus und prüft Verhalten".

Leser: Spec-Autor:innen, die die Geschwister-Stufen-Specs schreiben; Skill- und Agent-Autor:innen, die die Static-Analysis-Triade (Entwicklung/Ausführung/Analyse) bauen; Entwickler:innen, die die Stufe in Pre-Commit und CI verdrahten; Reviewer, die prüfen, ob die Stufe deterministisch, gegatet und korrekt abgegrenzt ist.

## Ziele

- Definieren, was die Static-Analysis-Stufe verifiziert — und, scharf, was sie nicht kann — damit sie nie die Aufgabe einer dynamischen Stufe übernehmen soll
- Die Sub-Kategorien (Lint, Type-Check, Format, Komplexität, SAST, Dead-Code, Import-Hygiene) als eine anerkannte Taxonomie aufzählen
- Type-Checking als erstklassige Sub-Stufe etablieren — „Tests, die man nicht schreibt" — mit einem Modell für graduelle Einführung und Strictness-Ratchet
- Die SAST↔SCA-Grenze ziehen, damit statische Security-Analyse von First-Party-Code nie das Dependency-CVE-Scanning aufsaugt
- Die Governance kodieren, die die Stufe vertrauenswürdig hält: inline-schnelles Feedback, deterministische und reproduzierbare Läufe, severity-basiertes PR-Gating, Baseline-and-Ratchet für Legacy-Code und disziplinierte Suppression
- Die Stufe werkzeug-agnostisch halten, mit einem austauschbaren Referenzprofil statt einer vorgeschriebenen Toolchain

## Nicht-Ziele

- Die Stufe auszuführen oder ihre Ausführungsmechanik und Ausgabetabelle zu definieren — Eigentum von `spec/project/quality-gate/` [R2]
- Dritt-Abhängigkeiten auf bekannte Schwachstellen zu scannen (SCA / CVE-Drift) — Eigentum von `spec/project/dependency-audit/` [R3]
- Dynamische Security-Tests (DAST) eines laufenden Systems — das ist ein End-to-End-/System-Umfang-Belang gemäß den Querschnitts-Dimensionen des Fundaments, nicht diese Stufe
- Laufzeitverhalten, Geschäftslogik oder Integrations-Korrektheit zu behaupten — die gehören zu den ausführenden Stufen darüber
- Bestimmte Linter, Type-Checker, Formatter oder SAST-Engines vorzuschreiben — das Referenzprofil ist illustrativ
- Das repositoryweite Regelset oder den Inhalt der Sprach-Konfigs zu definieren — das ist eine projektspezifische Entscheidung; diese Spec definiert Form und Governance der Stufe, nicht ihre Regel-Listen
- Die Falsifizierbarkeits-Checks über Testcode zu definieren (verschluckte Post-Conditions, vakuöse Assertions, Empty-Default-Reader) — der Check-Katalog ist Eigentum von `spec/project/test-falsifiability/` [R17]; diese Stufe besitzt das Regime, unter dem diese Checks laufen (Regel-Identifier, Baseline-and-Ratchet, Effective-Signal-Governance)

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** die Static-Analysis-Stufe als Verifikation definieren, die **ohne Ausführung des Programms** erfolgt — Lesen von Quell- oder kompilierten Artefakten und Melden von Defekten aus ihrer Struktur, ohne Testfälle [R5], [R6].
- **MUSS [MUST]** die Stufe als **komplementär zu, nicht als Teilmenge der ausführenden Stufen** behandeln: Statische und dynamische Analyse fangen weitgehend nicht überlappende Defekte, sodass Static Analysis additive Abdeckung ist, niemals ein Ersatz für Unit-/Integrationstests [R6], [R7].
- **DARF NICHT [MUST NOT]** von der Static-Analysis-Stufe verlangen, **Laufzeitverhalten, Geschäftslogik-Korrektheit oder Integrations-Ergebnisse** zu behaupten; ein Defekt, der sich nur durch Ausführen des Codes beobachten lässt, gehört zur Unit-Stufe oder höher. Das ist die Grenze zur ersten ausführenden Stufe.
- **MUSS [MUST]** die Stufe als **Fundament-Schicht (breiteste, billigste, schnellste)** der Pyramide gemäß `spec/project/test-pyramid-foundation/` positionieren [R1], [R10].
- **MUSS [MUST]** durch **Werkzeuge statt durch ein Generator-plus-Reviewer-Agentenpaar** durchgesetzt werden, anders als die vier ausführenden Stufen. Die Prüfungen dieser Stufe werden einmal je Repository konfiguriert statt je Feature verfasst; ein Generator hätte für ein neues Feature also nichts zu gerüsten, und ein Reviewer seiner Ausgabe würde das Wiring-Audit duplizieren, das `quality-gate-enforcer` bereits leistet. Die Durchsetzungskette lautet: `spec/project/quality-gate/` fordert die Kategorien Lint und Type-Check, `quality-gate` führt sie aus, `quality-gate-enforcer` auditiert ihre Verdrahtung, und `test-pyramid-check` routet die Stufe aus genau diesem Grund von seinem eigenen Audit weg. Das Fehlen eines `static-analysis-test-generator` und eines `static-analysis-test-reviewer` ist damit der **beabsichtigte Zustand**, nicht die Lücke, nach der es neben den vier Geschwister-Stufen aussieht, und eine Inventur, die Stufen nach der Zahl ihrer Agentenpaare vergleicht, **DARF NICHT [MUST NOT]** es als solche melden.

### Sub-Kategorien-Taxonomie

- **MUSS [MUST]** die folgenden Sub-Kategorien als geschlossene Menge anerkennen, die die Stufe umfasst, jede fängt Defekte allein aus der Code-Struktur:
  1. **Linting / Lint-Regeln** — wahrscheinliche Bugs und Stilverletzungen (ungenutzte Variablen, Shadowing, verdächtige Konstrukte).
  2. **Type-Checking** — statische Typverifikation und -inferenz (siehe §„Type-Checking als erstklassige Sub-Stufe").
  3. **Formatierung** — deterministisches Layout, im Check-Modus verifiziert (siehe §„Formatierung wird auto-fixt, nicht per Debatte gegatet").
  4. **Komplexität & Wartbarkeit** — zyklomatische/kognitive Komplexität und Wartbarkeitsschwellen.
  5. **Statische Security-Analyse (SAST)** — Security-Defekte im First-Party-Code (siehe §„SAST-Umfang und die SCA-Grenze").
  6. **Dead-Code / Unused-Symbol-Erkennung** — unerreichbarer Code, ungenutzte Exporte.
  7. **Import- / Dependency-Hygiene** — Import-Reihenfolge, Zyklus-Erkennung, Banned-Import-Regeln (strukturell, nicht CVE — siehe Grenze).
- **DARF [MAY]** eine Sub-Kategorie weglassen, die auf eine Sprache oder ein Projekt nicht zutrifft, festgehalten als bewusste Auslassung statt stiller Lücke, gemäß der Stufen-Auslassungsregel des Fundaments.

### Type-Checking als erstklassige Sub-Stufe

- **MUSS [MUST]** statisches Type-Checking als **erstklassigen Teil der Stufe** behandeln, nicht als optionales Extra: Statische Typen sind „Tests, die man nicht schreibt", und eine empirische Studie fand, dass ein ausgereifter Type-Checker in der Größenordnung **~15% der sonst ausgelieferten öffentlichen Bugs** in ungetyptem Code fängt (Flow 0.30 / TypeScript 2.0, ICSE 2017) [R11], [R12].
- **MUSS [MUST]** **graduelle Typisierung** auf bestehendem ungetyptem Code übernehmen, statt vollständige Annotation auf einmal zu verlangen: zuerst eine Teilmenge annotieren, dann die Strictness progressiv Richtung striktem Ziel ratchen und **in der CI nur neu eingeführte Typfehler blockieren**, während die Legacy-Baseline geerbt wird [R13], [R14].
- **SOLLTE [SHOULD]** ein Strictness-Ziel verfolgen und es über die Zeit verschärfen (die Dropbox-Trajektorie über 4 Millionen Zeilen / mehrere Jahre ist die Referenzerfahrung), statt auf der lockersten Einstellung einzufrieren [R13], [R14].

### SAST-Umfang und die SCA-Grenze

- **MUSS [MUST]** die SAST-Sub-Kategorie auf **First-Party-Quellcode** begrenzen: Data-Flow-/Taint-Analyse, die Defektklassen wie Injection, Buffer Overflow, unsichere Deserialisierung und hartcodierte Secrets meldet, je mit Datei, Zeile und Snippet [R8].
- **DARF NICHT [MUST NOT]** SAST als **vollständige Security-Abdeckung** behandeln: Sie kann Authentifizierungs-, Zugriffskontroll- oder kryptografische Design-Fehler nicht zuverlässig erkennen und ist von Natur aus rauschig mit False Positives — sie ist ein Signal, kein Security-Freigabestempel [R8], [R9].
- **MUSS [MUST]** die Grenze zur **Software Composition Analysis (SCA)** scharf halten: Das Scannen *von Dritt-Abhängigkeiten* auf bekannte CVEs ist Eigentum von `spec/project/dependency-audit/` [R3], nicht dieser Stufe; SAST analysiert den eigenen Code des Projekts [R9].
- **MUSS [MUST]** die Grenze zu **DAST** scharf halten: Dynamische Security-Tests eines laufenden Systems sind ein End-to-End-/System-Umfang-Querschnittsbelang, nie Teil der ausführungslosen statischen Stufe.

### Determinismus und Reproduzierbarkeit

- **MUSS [MUST]** verlangen, dass die Stufe **vollständig deterministisch** ist: Dieselbe Quelle und dieselben gepinnten Regel-/Tool-Versionen erzeugen immer dieselben Findings, ohne Abhängigkeit von Wanduhr, Netzwerk, Maschine oder Reihenfolge. Da die Stufe nichts ausführt, gilt das Test-Double-Vokabular des Fundaments nicht — es gibt keine zu isolierenden Kollaborateure; die Determinismus-Garantie ruht stattdessen auf **gepinnten Analyzer- und Regelset-Versionen**.
- **MUSS [MUST]** die Analyzer- und Regelset-Versionen pinnen (gemäß dem Dependency-Management-Mechanismus des Repositorys), sodass ein Finding über Maschinen und über die Zeit reproduzierbar ist; ein ungepinntes Regelset, das Findings zwischen Läufen still ändert, ist ein Flakiness-Defekt gemäß dem Fundament.

### Ausführungs-Platzierung und Feedback-Ökonomie

- **MUSS [MUST]** die Stufe **zuerst und am schnellsten** in der Feedback-Kette platzieren — Editor/IDE, dann ein Pre-Commit-Hook, dann ein PR-gatender CI-Check — damit Defekte am billigstmöglichen Punkt gefangen werden [R10], [R15].
- **MUSS [MUST]** Findings **inline zur Code-Review-/PR-Zeit** liefern, nicht nur auf einem out-of-band-Nightly-Dashboard: Platzierung zur Review-Zeit ist es, was bewirkt, dass Static Analysis befolgt wird; ein separates Dashboard, das Entwickler:innen aufrufen müssen, ist ein dokumentierter Fehlermodus (FindBugs-Nightly blieb ungenutzt; der Inline-Ansatz war erfolgreich) [R15].
- **SOLLTE [SHOULD]** dasselbe Regelset in den Editor integrieren, sodass die Entwickler:in ein Finding vor dem Commit sieht, nicht erst nach dem Push.

### Severity-Gating und das Baseline-and-Ratchet-Modell

- **MUSS [MUST]** Findings eine **Severity** zuweisen und den PR an den blockierenden Severities (Errors) gaten, während nicht-blockierende Severities (Warnings/Info) sichtbar gemacht werden, aber das Gate nicht fehlschlagen lassen; die gatende Teilmenge wird als erforderliche Checks gemäß `spec/project/pull-request-workflow/` deklariert und gemäß `spec/project/quality-gate/` ausgeführt.
- **MUSS [MUST]** die Stufe nach **effektivem Signal** steuern: Eine Regel, deren Findings Entwickler:innen routinemäßig ignorieren oder übergehen, ist ein Kostenfaktor (Alert-Fatigue), und eine von Rauschen dominierte Stufe verliert Vertrauen; Regeln, die Handlung erzeugen, werden behalten, Regeln, die das nicht tun, getunt oder entfernt [R15].
- **MUSS [MUST]** **Baseline-and-Ratchet** anwenden, wenn Analyse auf einer Legacy-Codebasis eingeführt wird: die bestehenden Findings als geerbte Baseline erfassen, **jedes neue Finding über der Baseline blockieren** und die Baseline über die Zeit verschärfen — niemals den ganzen Backlog auf einmal blockieren und niemals das Gate dauerhaft ausgeschaltet lassen [R13], [R16].
- **DARF NICHT [MUST NOT]** eine feste numerische False-Positive- oder Coverage-Schwelle als Portfolio-Anforderung kodieren (z. B. „auto-deaktivieren über 10% Rauschen"); eine solche harte Schwelle ist keine etablierte, verifizierbare Invariante — nach effektivem Signal steuern, nicht nach einer magischen Zahl.

### Suppression-Disziplin

- **MUSS [MUST]** verlangen, dass jede Suppression eines Findings **eng und begründet** ist: eine inline, einzelne-Finding-Suppression mit einem Grund, niemals ein pauschales datei- oder repoweites Deaktivieren, das eine ganze Regelklasse still verbirgt.
- **SOLLTE [SHOULD]** Suppressionen reviewbar machen — sichtbar im Diff und derselben Review unterworfen wie Code — sodass eine Suppression eine bewusste, auditierbare Entscheidung ist statt eines verborgenen Notausgangs.

### Formatierung wird auto-fixt, nicht per Debatte gegatet

- **MUSS [MUST]** Formatierung als **mechanisch auto-angewandt** behandeln, nicht als Gegenstand per-PR-Debatte: Ein einzelner deterministischer Formatter ist die Quelle der Wahrheit, die CI verifiziert im Check-Modus, und Stil ist nie Gegenstand von Review-Kommentaren (Format-Kriege / Bikeshedding sind ein Anti-Pattern).
- **SOLLTE [SHOULD]** trivial fixbare Findings (Formatierung, Import-Reihenfolge) auto-fixen, statt einen PR an ihnen zu blockieren; das Gate blockiert an dem, was nicht auto-gefixt werden kann.

### Traceability

- **MUSS [MUST]** jedes Finding **auf Datei, Zeile und Regel-Identifier** rückführbar machen, sodass eine Entwickler:in es lokalisieren und verstehen kann, ohne die Analyse erneut auszuführen [R8].
- **SOLLTE [SHOULD]** jede erzwungene Regel auf den Belang abbilden, den sie schützt (eine Bug-Klasse, eine Security-Klasse, eine Wartbarkeitsschwelle), sodass das Regelset nach Absicht reviewbar ist, nicht nur nach Namen. Anders als die ausführenden Stufen führen Static-Analysis-Findings auf **Code-Stellen und Regel-IDs** zurück, nicht auf Anforderung / TC-IDs — hinter einer Lint-Regel steht kein Testfall.

### Optionales Referenzprofil

- **DARF [MAY]** ein vollständig ausgearbeitetes, stack-spezifisches Referenzprofil pinnen, klar zu „Referenz" degradiert und nie zur Anforderung erhoben. Ein illustratives Python-Profil: ein konsolidierter schneller Linter+Formatter (zum Beispiel `ruff`, der Lint + Import-Sort + Format abdeckt und den älteren `flake8`+`isort`+`black`-Stack ersetzt), ein statischer Type-Checker (zum Beispiel `mypy` oder `pyright`), verdrahtet, um neue Fehler zu blockieren, und ein First-Party-SAST-Lauf (zum Beispiel `bandit` oder `semgrep`). Andere Ökosysteme realisieren dieselbe Stufe mit ihren eigenen Werkzeugen (ESLint/`tsc`/Prettier; golangci-lint/`gofmt`; clippy/`rustfmt`). Der Trend zu **konsolidierten „Format + Lint + Fix"-Runnern** ist illustrativ angemerkt, nicht vorgeschrieben.

## Akzeptanzkriterien

- [ ] Die Spec hält fest, dass die Stufe werkzeug- statt agenten-durchgesetzt ist, benennt die Artefakte der Durchsetzungskette und sagt, dass das Fehlen eines Generator/Reviewer-Paars der beabsichtigte Zustand ist statt einer Lücke
- [ ] Die Spec benennt, welche ihrer eigenen Anforderungen die Durchsetzungskette nicht abdeckt, statt zu suggerieren, die Kette decke sie alle ab

- [ ] Die Spec definiert die Stufe als ausführungslose Verifikation, die keine Testfälle braucht, und zitiert das Fundament sowie eine Primärquelle für die statisch/dynamisch-Komplementarität (nicht überlappende Defekte)
- [ ] Die Sub-Kategorien-Taxonomie listet die sieben Sub-Kategorien (Lint, Type-Check, Format, Komplexität, SAST, Dead-Code, Import-Hygiene)
- [ ] Type-Checking ist als erstklassige Sub-Stufe etabliert mit dem Modell graduelle-Typisierung + Strictness-Ratchet + neue-Fehler-blockieren, zitiert auf die Typstudie und mypy-Quellen
- [ ] Die SAST-Sub-Kategorie ist auf First-Party-Code begrenzt, als unvollständige Security-Abdeckung deklariert und gegen SCA (`dependency-audit`) und DAST abgegrenzt
- [ ] Determinismus ist via gepinnte Analyzer-/Regel-Versionen gefordert, und die Spec merkt an, dass das Test-Double-Vokabular des Fundaments nicht gilt (keine Ausführung)
- [ ] Die Ausführungs-Platzierung fordert Inline-/Review-Zeit-Feedback und lehnt das Nur-out-of-band-Nightly-Dashboard-Muster ab, zitiert auf die Google-Quelle
- [ ] Severity-Gating, Steuern-nach-effektivem-Signal und Baseline-and-Ratchet für Legacy-Code sind gefordert, und keine feste numerische Rausch-/Coverage-Schwelle ist vorgeschrieben
- [ ] Suppression-Disziplin (eng, begründet, reviewbar) und Formatierung-auto-fixen-nicht-debattieren sind gefordert
- [ ] Traceability ist auf Datei/Zeile/Regel-ID, und die Spec merkt an, dass diese Stufe nicht auf Anforderung/TC-IDs zurückführt
- [ ] Die Abgrenzung gegen `quality-gate` (führt aus), `dependency-audit` (SCA) und die Unit-Stufe (erste ausführende Stufe) ist explizit
- [ ] Ein optionales, klar degradiertes Referenzprofil ist bereitgestellt, ohne eine Toolchain vorzuschreiben
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-pyramid-foundation/` — das Stufenmodell, das diese Spec realisiert (Static Analysis ist die Fundamentstufe)
- [R2] `spec/project/quality-gate/` — führt die schnellen Stufen aus und besitzt Ausführungsmechanik / Ausgabeform
- [R3] `spec/project/dependency-audit/` — besitzt das CVE-Scanning von Dritt-Abhängigkeiten (SCA); die SAST↔SCA-Grenze
- [R4] `spec/project/pull-request-workflow/` — besitzt die Erzwingung erforderlicher Status-Checks, die die gatende Teilmenge speist
- [R5] ISTQB / ASTQB, *Static Testing Basics* — <https://astqb.org/3-1-static-testing-basics/>
- [R6] Kent C. Dodds, *The Testing Trophy and Testing Classifications* (Static ist die Basisstufe) — <https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications>
- [R7] A. Habib & M. Pradel, *How Many of All Bugs Do We Find? A Study of Static Bug Detectors* (statisch und dynamisch finden nicht überlappende Defekte) — <https://arxiv.org/abs/1711.05019>
- [R8] OWASP, *Source Code Analysis Tools* (SAST: Taint/Data-Flow, Defektklassen, Datei/Zeile/Snippet, False Positives) — <https://owasp.org/www-community/Source_Code_Analysis_Tools>
- [R9] OWASP, *Static Code Analysis* Control / *Dependency-Check* (SAST-vs-SCA-Grenze) — <https://owasp.org/www-community/controls/Static_Code_Analysis> , <https://owasp.org/www-project-dependency-check/>
- [R10] Kent C. Dodds, *Static vs Unit vs Integration vs E2E Tests* — <https://kentcdodds.com/blog/static-vs-unit-vs-integration-vs-e2e-tests>
- [R11] Z. Gao, C. Bird & E. T. Barr, *To Type or Not to Type: Quantifying Detectable Bugs in JavaScript* (ICSE 2017; ~15% der öffentlichen Bugs) — <https://earlbarr.com/publications/typestudy.pdf>
- [R12] Microsoft Research, *To Type or Not to Type* (Studien-PDF) — <https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/gao2017javascript.pdf>
- [R13] mypy, *Using mypy with an existing codebase* (graduelle Typisierung, Ratchet zu strikt, neue Fehler blockieren) — <https://mypy.readthedocs.io/en/stable/existing_code.html>
- [R14] Dropbox, *Our journey to type checking 4 million lines of Python* — <https://dropbox.tech/application/our-journey-to-type-checking-4-million-lines-of-python>
- [R15] C. Sadowski et al., *Lessons from Building Static Analysis Tools at Google* (CACM 2018; inline schlägt Nightly-Dashboards, Steuerung nach effektivem False Positive) — <https://cacm.acm.org/research/lessons-from-building-static-analysis-tools-at-google/>
- [R16] *Ratcheting* (Baseline-and-Ratchet-Muster für Legacy-Code) — <https://ponomarev.uk/blog/ratcheting>
- [R17] `spec/project/test-falsifiability/` — besitzt den Testcode-Falsifizierbarkeits-Check-Katalog, den diese Stufe betreibt

## Offene Fragen

- Sollte das Portfolio ein minimales Baseline-Sub-Kategorien-Set deklarieren, das die Static-Analysis-Stufe jedes Repositorys aktivieren MUSS (zum Beispiel: mindestens ein Linter, ein Formatter und — wo die Sprache einen hat — ein Type-Checker), oder vollständig projektspezifisch bleiben?
- Wo die Sprache dynamisch typisiert ist und keinen ausgereiften Type-Checker hat, hält die Stufe die Abwesenheit der Type-Check-Sub-Kategorie als begründete Auslassung fest, oder verlangt sie eine typisierte Obermenge (z. B. typisiertes Python) als Portfolio-Default?
- **Entscheidung (2026-08-22, #558):** Die Triade braucht kein dediziertes Agentenpaar. `quality-gate` (Ausführen) plus `quality-gate-enforcer` (Wiring-Audit) genügt, und die Anforderung unter §„Zweck und Umfangsgrenze“ hält das fest. Offen bleibt etwas Engeres, das benannt statt stillschweigend miterledigt gehört: **Die eigenen kennzeichnenden Regeln dieser Stufe setzt heute nichts durch.** `quality-gate-enforcer` auditiert, dass die Kategorien Lint und Type-Check existieren und korrekt verdrahtet sind; er prüft weder §„Severity-Gating und das Baseline-and-Ratchet-Modell“ noch §„Suppression-Disziplin“ noch §„SAST-Umfang und die SCA-Grenze“. Ob daraus Prüfungen in jenem Agenten, eine Lint-Regel oder Reviewer-Leitlinien werden, ist nicht entschieden; diese Spec ist durch die Kette oben nur für jene Teile verankert, die die Kette tatsächlich abdeckt.
