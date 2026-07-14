# Release-Regressionsumfang

Status: draft
Portfolio-Scope: local

## Context

Eine vollständige End-to-End-Regressionssuite ist zu langsam, um bei jedem Release zu laufen, und blockiert deshalb einen zeitnahen Rollout, wenn sie immer ausgeführt wird. Eine beliebige Teilmenge zu fahren ist stattdessen unsicher: Ein funktionaler Bereich kann still brechen. Das Portfolio hat bereits die Bausteine, um Tests zu *schreiben, auszuführen und zu auditieren* (`spec/project/test-pyramid-foundation/`, die `test-tier-*`-Familie, `spec/project/e2e-test-automation/`, die `test-cycle-*`-Familie) und um ein *Release zu treiben* (`spec/project/release-skill-layer/`, `release-automation`, `release-artifact`). Was fehlt, ist der **Auswahlschritt** dazwischen: Aus dem Change-Set eines Release entscheiden, *welche* Themengebiete betroffen sind und daher *welche* Regressionstests vor dem Ausliefern laufen müssen—nicht mehr und nicht weniger.

Diese Spec regelt diese Auswahl-Disziplin auf Release-Ebene. Sie ist das release-bezogene Analogon zu `spec/project/test-cycle-case-determination/`, das für einen einzelnen Testzyklus "welche Fälle" beantwortet; diese Spec beantwortet "welchen Regressionsumfang" über eine ganze Release-Range. Sie besitzt bewusst nur die *Scoping*-Entscheidung: Sie konsumiert die Test↔Requirement-Traceability, die `e2e-test-automation` und `test-case-derivation` bereits vorschreiben, und selektiert über die bereits existierenden Testfälle. Sie schreibt, führt, auditiert oder leitet niemals Tests ab und treibt niemals das Release.

Sie wird im `nolte-engineering`-Plugin operationalisiert als eigenständiger Skill (Umfangsbestimmung) plus ein read-only Scanner-Agent (Change→Bereich-Attribution) und spiegelt damit, wie `e2e-test-automation` und die `test-cycle-*`-Familie eine regelnde Spec mit einer Generator-/Reviewer-/Scanner-Toolchain paaren. Die Spec regelt die Disziplin; Skill und Agent operationalisieren sie.

Leser: Skill-/Agent-Autoren, die diese Toolchain pflegen; Release-Operatoren und Maintainer, die einen Rollout auf eine vertrauenswürdige-aber-schnelle Regressions-Teilmenge gaten müssen; Reviewer, die prüfen, dass ein gewählter Umfang sowohl zielgenau als auch im betroffenen Bereich vollständig ist.

## Goals

- Die betroffenen Themengebiete eines Release aus seinem tatsächlichen Change-Set ableiten, mechanisch und auditierbar.
- Die minimale Menge an Stufen und Tests auswählen (E2E betont für User-Journey-Abdeckung), die die funktionalen Requirements jedes betroffenen Bereichs vollständig abdeckt.
- Die Trias garantieren: **zielgenau** (nur betroffene Bereiche gaten das Release), **zeitnah** (die gewählte Teilmenge läuft schnell genug, um den Rollout nicht zu blockieren), **vollständig-im-Bereich** (die Regressionsabdeckung der funktionalen Requirements jedes betroffenen Bereichs ist vollständig, nie partiell).
- Die Rollout-Entscheidung auditierbar machen: was im Umfang ist, was bewusst ausgeschlossen wird und warum, und welches Restrisiko übrig bleibt.
- Sicher scheitern: Wenn eine Änderung nicht attribuierbar ist, auf den vollen Bereich verbreitern, statt einen engeren Umfang zu raten.

## Non-Goals

- Das Schreiben, Ausführen oder Auditieren der Tests selbst—das bleibt bei `e2e-test-automation`, der `test-tier-*`-Familie und der `test-cycle-*`-Familie.
- Das Ableiten *neuer* Testfälle—das bleibt bei `test-cycle-case-determination` (per Zyklus) und `test-case-derivation` (abstrakte Fälle). Diese Spec *selektiert* nur über bereits existierende Fälle.
- Das Treiben des Release (Veröffentlichen, Taggen, Workflow-Dispatch)—das bleibt bei den `release-*`-Specs.
- Das Vorschreiben eines bestimmten Release-Range-Mechanismus oder eines bestimmten Traceability-Index-Formats; das sind Operationalisierungs-Entscheidungen, die Skill und Agent überlassen bleiben (siehe Open Questions).

## Requirements

Change-Set und Attribution

- **R1** Die Capability MUSS das Release-Change-Set (die Menge der ins Release gehenden Änderungen: der Diff der Release-Range, ihre gemergten Pull Requests und ihre berührten Pfade) auflösen, bevor irgendetwas attribuiert wird.
- **R2** Jede Änderung MUSS ihren betroffenen Themengebieten primär durch Inversion der bestehenden Test↔Requirement-Traceability zugeordnet werden: Änderung → Requirement / Feature-ID / TC-ID → verifizierende Tests. Die Attribution MUSS sich auf die von `e2e-test-automation` und `test-case-derivation` bereits vorgeschriebene Traceability stützen, statt ein paralleles Mapping zu erfinden.
- **R3** Wenn eine Änderung nicht mechanisch einem Themengebiet zugeordnet werden kann, MUSS die Capability auf die volle Regressionsmenge jedes plausibel betroffenen Bereichs zurückfallen und MUSS eine auditierbare Restrisiko-Notiz festhalten. Sie DARF NICHT still einen engeren Umfang wählen.

Umfangsableitung und Vollständigkeit

- **R4** Aus den betroffenen Bereichen MUSS die Capability die minimale Menge an Stufen und Tests ableiten, die die funktionalen Requirements dieser Bereiche abdeckt, mit E2E-Betonung für User-Journey-Abdeckung.
- **R5** Ein betroffener Bereich MUSS nur dann als *vollständig abgedeckt* gelten, wenn jedes funktionale Requirement dieses Bereichs einen existierenden, grünen verifizierenden Test auf der angemessenen Stufe hat. Partielle Abdeckung eines berührten Bereichs ist nie "abgedeckt".
- **R6** Wenn für einen betroffenen Bereich ein verlangter verifizierender Test fehlt, MUSS die Capability diesen Bereich als nicht vollständig abgedeckt melden und MUSS die Coverage-Lücke als Release-Blocker oder explizites Risiko sichtbar machen, statt den Bereich als bestanden zu behandeln.

Report und Garantien

- **R7** Die Capability MUSS einen auditierbaren Umfangs-Report ausgeben, der die In-Scope-Bereiche, die ausgewählten Tests, die bewusst ausgeschlossenen Bereiche mit je einer Begründung und die Restrisiko-Notiz für alles nicht mechanisch Attribuierbare auflistet.
- **R8** Der gewählte Umfang MUSS die Garantie-Trias erfüllen (zielgenau, zeitnah, vollständig-im-Bereich); ein Umfang, der auf einen nicht betroffenen Bereich gatet, der nicht rechtzeitig laufen kann oder der einen betroffenen Bereich partiell abgedeckt lässt, verletzt diese Spec.
- **R9** Die Capability SOLLTE identische Ausgabe erzeugen, welcher Tooling-Pfad auch genommen wird (zum Beispiel ob sie GitHub-Daten über einen MCP-Server oder die `gh`-CLI liest), damit ein Headless- oder CI-Lauf vertrauenswürdig ist.

Abgrenzung und Operationalisierung

- **R10** Die Capability MUSS nur über bereits existierende, über die gesamte Release-Range aggregierte TC-IDs *selektieren*; das Ableiten neuer Fälle bleibt `test-cycle-case-determination`.
- **R11** Der Change→Bereich-Scanner MUSS read-only sein; er attribuiert und meldet, schreibt aber nichts und führt keine Tests aus.
- **R12** Die Disziplin SOLLTE in `nolte-engineering` angesiedelt und als eigenständiger Skill plus read-only Scanner-Agent geliefert werden, aufbauend auf den Anker-Specs (`e2e-test-automation`, `test-pyramid-foundation`, `test-tier-*`, `test-cycle-*`, `test-case-derivation`, `release-*`), ohne sie zu duplizieren.
- **R13** `release-skill-layer` KANN die Capability als optionales Pre-Rollout-Gate referenzieren; die Referenz ist eine Consumer-Entscheidung und wird von dieser Spec nicht verlangt.

## Acceptance Criteria

- [ ] Die Spec löst ein Release-Change-Set auf (Range-Diff, gemergte PRs, berührte Pfade), bevor irgendetwas attribuiert wird. (R1)
- [ ] Die Attribution invertiert die bestehende Test↔Requirement-Traceability (Änderung → Requirement/TC-ID → verifizierende Tests) statt eines parallelen Mappings. (R2)
- [ ] Eine nicht attribuierbare Änderung verbreitert auf volle Bereichs-Regression und hält eine Restrisiko-Notiz fest; sie verengt nie still. (R3)
- [ ] Der abgeleitete Umfang ist die minimale Stufen-/Testmenge, die die funktionalen Requirements der betroffenen Bereiche abdeckt, mit E2E-Betonung. (R4)
- [ ] Ein Bereich gilt nur als vollständig abgedeckt, wenn jedes funktionale Requirement einen grünen verifizierenden Test auf der angemessenen Stufe hat. (R5)
- [ ] Ein fehlender verifizierender Test erscheint als Coverage-Lücken-Blocker/Risiko, nicht als stiller Pass. (R6)
- [ ] Der Umfangs-Report listet In-Scope-Bereiche, ausgewählte Tests, bewusst ausgeschlossene Bereiche mit Begründung und die Restrisiko-Notiz. (R7)
- [ ] Der Umfang erfüllt nachweislich zielgenau, zeitnah und vollständig-im-Bereich. (R8)
- [ ] Der Scanner ist read-only und die Disziplin ist von der Fallableitung abgegrenzt (selektiert nur existierende TC-IDs). (R10, R11)
- [ ] Die Capability ist in `nolte-engineering` als Skill + read-only Scanner-Agent angesiedelt und zitiert die Anker-Specs, ohne sie zu duplizieren. (R12)

## Open Questions

- **A1**—Release-Range-Auflösung: Ist die Range das letzte veröffentlichte Release bis zur Release-Candidate-Spitze, ihre gemergten PRs oder ihre berührten Pfade—und wie werden die drei abgeglichen? Der Skill-/Agent-Operationalisierung überlassen.
- **A2**—Inverser Index: Wird der Requirement/TC-ID → verifizierende-Tests-Index aus der von `e2e-test-automation` / `test-case-derivation` bereits vorgeschriebenen Traceability gelesen oder vom Scanner zur Scan-Zeit gebaut? Operationalisierungs-Detail.
- **A3**—Themengebiet-Granularität: Bildet "Themengebiet" auf die bestehende Requirement-/Feature-Gruppierung unter `project/requirements/` und `project/features/` ab, oder braucht es ein eigenes Taxonomie-Artefakt? Die bestehende Gruppierung bevorzugt wiederverwenden, außer eine Lücke erzwingt eine neue.
- **A4**—Ob `release-skill-layer` die optionale Referenz aus R13 übernehmen sollte, und bei welchem Trigger. Nicht-blockierendes Follow-up.
