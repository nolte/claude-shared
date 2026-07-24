# Testfall-Ableitung aus Anforderungen

Status: draft

## Kontext

Ein Anforderungsdokument beschreibt, was ein System tun muss, aber es verifiziert sich nicht selbst. Eine Anforderung in eine Menge ausführbarer Testfälle zu überführen ist manuelle, fehleranfällige Arbeit, die driftet: Ein Tester liest die Spec, stellt sich die Szenarien vor und schreibt sie in welcher Form auch immer gerade zur Hand ist — sodass Abdeckungslücken unbemerkt bleiben, die Rückverfolgbarkeit zur Anforderung verloren geht und zwei Anforderungen inkonsistente Teststrukturen erhalten. Der wertvolle, wiederverwendbare Teil dieser Arbeit ist das **Ableiten von Black-Box-Testfällen aus dem nutzer-beobachtbaren Verhalten, das eine Anforderung beschreibt** — eine Disziplin (IREB/ISTQB), die unabhängig von jedem Test-Automatisierungs-Framework ist. Der Wegwerf-Teil ist der projektspezifische Klebstoff: welche Automatisierungs-Bibliothek die Fälle ausführt, welches Verzeichnis sie hält, welches Domänen-Vokabular sie nutzen.

Diese Spec regelt diese wiederverwendbare Ableitung, operationalisiert durch den `test-case-extractor`-Agent (`distribution: plugin`). Sie ist der generalisierte Kern eines projektlokalen Extractors, der die Agrar-Domäne einer App, ihr deutsch-only Anforderungsformat, ihre React/MUI-Annahme und ihren `spec/test-cases/`-Pfad hartcodiert hatte. Die Portfolio-Form leitet framework-agnostische, strukturierte, rückverfolgbare Testfall-Dokumente aus jedem Anforderungsdokument ab, in der eigenen Sprache des Quelldokuments, für welches nutzerseitige Interface das Projekt auch exponiert.

Diese Spec wird von ihren benachbarten Test-Capabilities entlang der **Verantwortung** abgegrenzt, nicht entlang einer Trennung in geteilt vs. projektlokal. E2E-Automatisierungscode erzeugen oder reviewen, die Ausgaben eines Laufs gegen die Specs prüfen und die Teststufen-Vollständigkeit auditieren werden von `spec/project/e2e-test-automation/` und seinen Agents und seinem Skill geregelt (`e2e-test-generator`, `e2e-test-reviewer`, `e2e-result-reviewer`, `test-pyramid-check`), die diese Arbeit hinter einem framework-neutralen Kern mit Selenium-Referenzprofil verallgemeinern. Test-Suiten laufen lassen und Fehler klassifizieren bleiben bei `quality-gate`. Diese Spec besitzt nur den vorgelagerten Schritt: die abstrakten, framework-agnostischen Fälle abzuleiten, die jene nachgelagerten Capabilities (über ihre TC-IDs) konsumieren.

Leser: Agent-Autoren, die den Extractor pflegen; QA-Engineers und Entwickler, die Testfälle ableiten, nachdem eine Anforderung spezifiziert ist; Reviewer, die Abdeckung und Rückverfolgbarkeit prüfen.

## Ziele

- Testfälle systematisch aus einem Anforderungsdokument ableiten, abdeckend Happy Paths, Negativfälle, Validierung, Zustandsübergänge, Navigation und Fehlerzustände, die der Nutzer beobachten kann
- Jeden Testfall aus der Perspektive des **nutzer-beobachtbaren Verhaltens** schreiben — kein internes Implementierungsdetail (API-Aufrufe, Status-Codes, Queries) in den Schritten
- Strukturierte, eigenständige, retrieval-freundliche Testfall-Dokumente mit voller Rückverfolgbarkeit zur Quell-Anforderungs-Sektion erzeugen
- Framework-agnostisch bleiben: Die abgeleiteten Fälle sind von einem manuellen Tester oder jedem Automatisierungs-Framework ausführbar, weil sie Verhalten beschreiben, nicht Framework-Aufrufe
- Sich an Sprache, Ausgabe-Ort und nutzerseitigen Interface-Typ des Projekts anpassen, statt einen Stack anzunehmen

## Nicht-Ziele

- Test-Automatisierungs-**Code** generieren (Selenium/Playwright/Cypress-Page-Objects, Fixtures) — geregelt von `spec/project/e2e-test-automation/` (Agent `e2e-test-generator`); diese Spec erzeugt die abstrakten Fälle, die eine solche Suite automatisiert
- Test-Suiten laufen lassen, Fehler klassifizieren oder Test-Code beheben — im Besitz von `spec/project/quality-gate/` und projektlokalen Runnern
- Die Test-Tier-Verteilung eines Projekts auditieren (die „Test-Pyramide"-Form) — geregelt von `spec/project/e2e-test-automation/` (Skill `test-pyramid-check`)
- Die Anforderungsdokumente selbst verfassen oder editieren — der Agent liest Anforderungen, er schreibt sie nicht
- Visuelles Review der Screenshots oder Logs eines Testlaufs gegen eine Spec — geregelt von `spec/project/e2e-test-automation/` (Agent `e2e-result-reviewer`)
- Die Batch-Orchestrierung über viele Anforderungen (Auswahl- und Commit-Politik) ist ein Konsumenten-Projekt-Skill, der diesen Agent pro Anforderung dispatcht (der Skill-orchestriert/Agent-führt-aus-Hybrid), keine Verantwortung dieses Agents

## Anforderungen

### Eingaben und Discovery

- **MUSS [MUST]** ein oder mehrere Anforderungsdokumente als Eingabe akzeptieren und jedes vollständig lesen, bevor Fälle abgeleitet werden; der Agent **DARF NICHT [MUST NOT]** den Anforderungspfad oder das ID-Schema eines Projekts hartcodieren und **MUSS [MUST]** berichten, welche Dokumente verarbeitet wurden
- **MUSS [MUST]** in der **Sprache des Quelldokuments** arbeiten: Testfälle werden in der Sprache geschrieben, in der die Anforderung verfasst ist, mit wortgetreu bewahrten Domänen-Begriffen und einer optionalen Code-Identifier-Glosse in Klammern zur Rückverfolgbarkeit
- **DARF [MAY]** die nutzerseitige Oberfläche des Projekts konsultieren (Route-Definitionen, Seiten-Inventar, CLI-Befehlsliste, öffentliche API-Oberfläche), um die Fälle im realen Interface zu verankern, wenn diese Oberfläche auffindbar ist; ohne sie leitet der Agent allein aus dem Anforderungstext ab und gibt diese Annahme an
- **MUSS [MUST]** den nutzerseitigen Interface-Typ des Projekts bestimmen (Browser-UI, CLI, API-Client, Mobile), sodass die Testschritte Aktionen in dieser Oberfläche beschreiben; wenn unbestimmbar, auf die in der Anforderung beschriebene Oberfläche zurückfallen und die Annahme angeben

### Ableitungs-Disziplin

- **MUSS [MUST]** jede Anforderung in ihre funktionalen Anforderungen, Akzeptanzkriterien, nutzerseitigen Zustandsänderungen, Eingabe-/Validierungsregeln und beobachtbaren Fehlerzustände zerlegen, bevor Fälle abgeleitet werden
- **MUSS [MUST]** jeden Testschritt als **nutzer-beobachtbare Aktion** schreiben (navigieren, klicken, tippen, auswählen, einen Befehl aufrufen) und jedes erwartete Ergebnis als **nutzer-beobachtbares Resultat** (eine Meldung, ein sichtbarer Zustand, ein zurückgegebener Wert); der Agent **DARF NICHT [MUST NOT]** interne Implementierung (HTTP-Status-Codes, Datenbank-Zustand, Funktionsaufrufe) in Schritten oder erwarteten Ergebnissen beschreiben
- **MUSS [MUST]**, wenn die Regel einer Anforderung sich nur als Verhalten zeigt (ein deaktiviertes Control, eine Validierungs-Meldung, eine fehlende Option), das Verhalten beschreiben, nicht die zugrundeliegende Regel
- **MUSS [MUST]** für jede Muss-Anforderung mindestens einen Happy-Path-Fall und mindestens einen Negativ-/Edge-Fall abdecken
- **SOLLTE [SHOULD]** die Standard-Ableitungs-Techniken anwenden — User-Journey, Eingabe/Grenzwert, Zustandsübergang, Navigation, visuelles Feedback und Error-Guessing — und die Technik, die ein Fall ausübt, in seinem Kategorie-Feld benennen

### Ausgabe-Vertrag

- **MUSS [MUST]** strukturierte Testfall-Dokumente in ein einzelnes konfigurierbares Ausgabe-Verzeichnis schreiben statt in einen hartcodierten Pfad, per Default `tests/cases/` im Konsumenten-Repository, ein Dokument pro Quell-Anforderung, benannt nach der Anforderung, auf die es zurückführt
- **MUSS [MUST]** jedem Dokument einen YAML-Frontmatter-Block geben (mindestens: Quell-Anforderungs-ID, Titel, Testfall-Anzahl, abgedeckte Bereiche, Erzeugungsdatum) und jedem Testfall die Struktur: Titel, Anforderungs-Referenz, Priorität, Kategorie, Vorbedingungen, Schritte, erwartete Ergebnisse, Nachbedingungen, Tags; diese Struktur ist portfolioweit festgelegt — nur Sprache, Ausgabe-Verzeichnis und Interface-Oberflächen-Vokabular passen sich pro Projekt an
- **MUSS [MUST]** jedes Dokument mit einer Abdeckungs-Zusammenfassung beenden, die Anforderungs-Sektionen auf die sie abdeckenden Fälle abbildet, und **MUSS [MUST]** Anforderungs-Sektionen, aus denen kein Fall abgeleitet werden konnte (offene Anforderungen), explizit auflisten statt sie still wegzulassen
- **MUSS [MUST]** jeden Testfall eigenständig und retrieval-freundlich halten (eine einzeilige Intent-Zusammenfassung, prominente Tags und Identifier, konsistentes Domänen-Vokabular, explizite Querverweise auf verwandte Fälle), sodass er die Ingestion in ein Retrieval-System als unabhängiger Chunk übersteht
- **MUSS [MUST]** das Dokument einer Anforderung deterministisch regenerieren: Ein erneuter Lauf auf derselben Anforderung liefert dieselben Fälle (modulo des Erzeugungs-Timestamps); der Agent überschreibt seine eigene frühere Ausgabe und merged nicht still mit Hand-Edits
- **MUSS [MUST]** Schreibvorgänge auf Testfall-Dokumente unter dem konfigurierten Ausgabe-Verzeichnis beschränken; der Agent **DARF NICHT [MUST NOT]** Quellcode, die Anforderungsdokumente oder eine andere Datei editieren
- Der Agent emittiert nur die menschenlesbaren Testfall-Dokumente; ihr `requirement_id`-Frontmatter pro Fall plus Tags und die Abdeckungs-Zusammenfassung pro Dokument sind die maschinell parsebare Rückverfolgbarkeits-Oberfläche. Per aktuellem Default **MUSS [MUST]** der Agent davon absehen, einen separaten maschinenlesbaren Rückverfolgbarkeits-Index zu emittieren, bis ein nachgelagertes Coverage-Tool das von ihm benötigte Schema deklariert, sodass kein zweites Artefakt die Determinismus- und Regenerations-Oberfläche ohne Leser verbreitert.

## Akzeptanzkriterien

- [ ] Den Agent auf einem Anforderungsdokument laufen zu lassen schreibt ein strukturiertes Testfall-Dokument unter dem konfigurierten Ausgabe-Verzeichnis (Default `tests/cases/`), benannt nach der Quell-Anforderung
- [ ] Jedes Dokument trägt YAML-Frontmatter mit mindestens Quell-Anforderungs-ID, Titel, Fall-Anzahl, abgedeckten Bereichen und Erzeugungsdatum
- [ ] Jeder Testfall hat die volle Struktur (Titel, Anforderungs-Referenz, Priorität, Kategorie, Vorbedingungen, Schritte, erwartete Ergebnisse, Nachbedingungen, Tags)
- [ ] Jeder Testschritt ist eine nutzer-beobachtbare Aktion und jedes erwartete Ergebnis ein nutzer-beobachtbares Resultat; kein Schritt oder erwartetes Ergebnis nennt einen HTTP-Code, eine Datenbank-Query oder einen internen Funktionsaufruf
- [ ] Jede Muss-Anforderung hat mindestens einen Happy-Path- und einen Negativ-Fall
- [ ] Das Dokument endet mit einer Abdeckungs-Tabelle und einer expliziten Liste der Anforderungs-Sektionen ohne ableitbaren Fall
- [ ] Testfälle sind in der Sprache des Quelldokuments geschrieben, mit bewahrten Domänen-Begriffen
- [ ] Ein erneuter Lauf auf derselben Anforderung reproduziert dieselben Fälle abgesehen vom Erzeugungs-Timestamp
- [ ] Der Agent schreibt nur Testfall-Dokumente unter dem konfigurierten Verzeichnis und editiert keine Quell- oder Anforderungsdateien
- [ ] Der Agent zitiert diese Spec in seinem Body oder seiner `description`, und seine `description` grenzt ihn von Automatisierungs-Code-Generierung, Test-Ausführung und Test-Tier-Auditing ab

## Referenzen

- [R1] Agent-Autoren-Regeln, denen dieser Agent entspricht: `spec/claude/agent-management/`
- [R2] Skill-vs-Agent-Entscheidungsregel und Rationale-Abschnitts-Anforderung: `spec/claude/skill-vs-agent/`
- [R3] Test-Ausführung / Fehlerbehandlung (gegen diese Spec abgegrenzt): `spec/project/quality-gate/`
- [R4] ISTQB-Test-Design-Techniken (Hintergrund-Methodik): <https://www.istqb.org/>

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._
