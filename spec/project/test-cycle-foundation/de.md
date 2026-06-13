# Fundament des Test-Zyklus

Status: draft

## Kontext

Testen ist keine einmalige Tätigkeit, die nach dem Schreiben des Codes stattfindet: Es ist ein **wiederkehrender, iterativer Zyklus**, der kontinuierlich läuft, während ein Feature gebaut und gepflegt wird. Diese Spec besitzt diesen Zyklus. Wo `spec/project/test-pyramid-foundation/` beantwortet, *was auf welcher Stufe getestet wird* (die strukturelle Dimension), beantwortet dieses Fundament, *wie die Testarbeit über die Zeit fließt* (die Prozess-Dimension) — die beiden sind orthogonal und setzen sich zusammen: Jede Umdrehung des Zyklus läuft innerhalb des Stufenmodells.

Der Zyklus hat **vier Phasen**, die verketten und schleifen:

1. **Testfall-Ermittlung** — entscheiden, welche Testfälle nötig sind (aus Anforderungen, aus Coverage-Lücken, aus gefundenen Defekten, aus geändertem Verhalten) und auf welcher Stufe jeder landet.
2. **Ausführung** — die Fälle ausführen und die rohen Ergebnisse sammeln.
3. **Ergebnis-Analyse** — die Ergebnisse interpretieren: Pass, echter Fehlschlag, Flake, Coverage-Lücke oder ein fehlender Fall.
4. **Code-Anpassung** — bei einem roten oder fehlenden Fall die minimale Code-Änderung ermitteln und anwenden, die ihn erfüllt (oder, bewusst und reviewbar, den Fall ändern, wenn der Fall selbst falsch war).

Diese bilden den klassischen **Red-Green-Refactor**-Loop des Test-Driven Development ab, verallgemeinert auf jede Stufe und jeden Punkt im Leben eines Features [R6], [R7]: Ein ermittelter-und-fehlschlagender Fall ist *rot*, eine Code-Anpassung, die ihn bestehen lässt, ist *grün*, und der Loop wiederholt sich. Die definierende Eigenschaft, die diese Spec kodiert, ist der **Loop**: Phase 4 kehrt zu Phase 2 zurück (erneut ausführen), und Phase 3 speist zurück in Phase 1 (ein gefundener Defekt wird ein neuer Regressionsfall; eine Coverage-Lücke wird ein neuer Fall). Der Zyklus endet nur bei einer expliziten Abbruchbedingung, nie durch Abschwächen eines Tests, um einen Pass zu erzwingen.

Dieses Fundament ist die **Spitze einer kleinen Prozess-Familie**: Es besitzt den Loop, die Inter-Phasen-Verträge und die Abbruchregel und delegiert die internen Best Practices jeder Phase an ihre eigene Phasen-Spec. Diese Phasen-Specs sind **Prozess-Specs, die bestehende Capability-Specs als ihre Realisierungen referenzieren**, statt sie zu wiederholen.

**Verhältnis zu den bestehenden Specs.** Dieses Fundament und seine Phasen-Specs sind ein Prozess-Layer über bereits bestehenden Capabilities; die Grenze verläuft nach Verantwortung:

- `spec/project/test-pyramid-foundation/` [R1] — das Stufenmodell, in dem der Zyklus läuft (orthogonal: Struktur vs. Prozess).
- `spec/project/test-cycle-case-determination/` [R2] (Phase 1) referenziert `spec/project/test-case-derivation/` für die Ableitung von Anforderung zu abstraktem Fall.
- `spec/project/test-cycle-execution/` [R3] (Phase 2) referenziert `spec/project/quality-gate/` und die Ausführungs-Platzierung der Stufen-Specs.
- `spec/project/test-cycle-result-analysis/` [R4] (Phase 3) referenziert den `e2e-result-reviewer` aus `spec/project/e2e-test-automation/` und `spec/project/workflow-health/` für die Fehler-Triage.
- `spec/project/test-cycle-code-adaptation/` [R5] (Phase 4) ist die neue Phase: einen roten Fall in die richtige Code-Änderung verwandeln.

Leser: Spec-Autor:innen, die die vier Phasen-Specs auf diesem Fundament schreiben; Skill- und Agent-Autor:innen, die das Per-Phasen-Tooling (Entwicklung/Ausführung/Analyse) bauen; Entwickler:innen und Reviewer, die den Zyklus durchlaufen und ein gemeinsames Vokabular dafür brauchen, in welcher Phase sie sind und wann der Zyklus fertig ist.

## Ziele

- Den **iterativen Test-Zyklus** als erstklassigen, wiederkehrenden Prozess besitzen: vier Phasen, die verketten und schleifen, getrennt vom Stufenmodell
- Die **Inter-Phasen-Verträge** definieren (Inputs und Outputs jeder Phase), damit die Phasen sich zu einem Loop zusammensetzen statt zu vier unverbundenen Tätigkeiten
- Die **Feedback-Kanten** explizit machen: Analyse erzeugt neue Fälle (Phase 3 → Phase 1) und treibt Code-Änderungen (Phase 3 → Phase 4), und Code-Anpassung tritt erneut in die Ausführung ein (Phase 4 → Phase 2)
- Die **Abbruchregel** und die **Nicht-Schummeln-Invariante** kodieren (nie einen Test abschwächen, um ein Grün zu erzwingen)
- Den **Per-Phasen-Spec-Vertrag** definieren, damit die vier Phasen-Specs strukturell konsistent bleiben und bestehende Capability-Specs referenzieren statt sie zu duplizieren
- Die ganze Familie **werkzeug- und stufen-agnostisch** halten: Der Zyklus läuft in derselben Form, ob der Fall auf der Unit-Stufe oder der E2E-Stufe landet

## Nicht-Ziele

- Die internen Best Practices einer einzelnen Phase zu spezifizieren — jede Phase erhält ihre eigene Spec, die auf dem Per-Phasen-Vertrag dieses Fundaments aufbaut
- Die von den Phasen referenzierten Capability-Specs zu wiederholen (`test-case-derivation`, `quality-gate`, `e2e-test-automation`, `workflow-health`) — die bleiben für ihre Capability maßgeblich
- Das Stufenmodell oder die Test-Double-Taxonomie zu besitzen — die gehören `spec/project/test-pyramid-foundation/` [R1]
- Ein bestimmtes Workflow-Werkzeug, einen Runner oder eine Methoden-Marke (TDD/BDD/ATDD) vorzuschreiben: Der Zyklus ist die gemeinsame Form, die diese Methoden teilen, werkzeug-agnostisch formuliert
- Die Per-Phasen-Skills und -Agents zu bauen — diese Familie deklariert die Phasen und ihre Verträge; die Artefakte werden separat unter `spec/claude/` verfasst

## Anforderungen

### Die vier Phasen und der Loop

- **MUSS [MUST]** den Test-Zyklus als die vier geordneten Phasen definieren — **Testfall-Ermittlung → Ausführung → Ergebnis-Analyse → Code-Anpassung** — die **schleifen**: Code-Anpassung kehrt zur Ausführung zurück, und der Zyklus wiederholt sich, bis eine Abbruchbedingung gilt.
- **MUSS [MUST]** den Zyklus als **wiederkehrend und kontinuierlich** behandeln, auf jeder Stufe und über das ganze Leben eines Features ausgeführt (kein einmaliger Schritt nach dem Coden), und so den Red-Green-Refactor-Loop des Test-Driven Development auf jede Stufe verallgemeinern [R6], [R7].
- **MUSS [MUST]** den Zyklus **orthogonal zum Stufenmodell** halten: Eine einzelne Umdrehung des Zyklus betrifft einen oder mehrere Fälle auf ihren gewählten Stufen gemäß `spec/project/test-pyramid-foundation/` [R1]; der Zyklus ist der Prozess, das Stufenmodell die Struktur.

### Inter-Phasen-Verträge

- Jede Phasen-Spec **MUSS [MUST]** ihre **Inputs und Outputs** deklarieren, damit die Phasen deterministisch verketten:
  - **Testfall-Ermittlung** gibt eine Menge von Testfällen aus (je mit TC-ID und gewählter Stufe), die fehlschlagen oder abwesend sein sollen, bis sie erfüllt sind.
  - **Ausführung** konsumiert die Fälle und gibt rohe Ergebnisse aus (Pass / Fail / Error, plus Coverage- und Protokoll-Artefakte, wo die Stufe sie erzeugt).
  - **Ergebnis-Analyse** konsumiert die Ergebnisse und gibt pro Fall eine **Klassifikation** aus: Pass, echter Fehlschlag, Flake, Coverage-Lücke oder fehlender Fall.
  - **Code-Anpassung** konsumiert eine rote oder fehlende Klassifikation und gibt eine **Code-Änderung** aus (oder eine bewusste Fall-Änderung), die erneut in die Ausführung eintritt.
- Eine Phasen-Spec **MUSS [MUST]** ihren Output für die nächste Phase ohne out-of-band-Wissen konsumierbar machen, damit der Loop mechanisch ist, nicht stillschweigend.

### Feedback-Kanten

- **MUSS [MUST]** die Feedback-Kanten als erstklassig definieren, nicht als Ausnahmen:
  - **Analyse → Testfall-Ermittlung** (Phase 3 → Phase 1): Ein in der Analyse gefundener echter Defekt **MUSS** einen neuen **Regressionsfall** ergeben, der ihn reproduziert, bevor er behoben wird; eine Coverage- oder Verhaltenslücke ergibt einen neuen Fall [R6].
  - **Analyse → Code-Anpassung** (Phase 3 → Phase 4): Ein bestätigter echter Fehlschlag wird an die Code-Anpassung geroutet, nicht an das Abschwächen des Tests.
  - **Code-Anpassung → Ausführung** (Phase 4 → Phase 2): Jede Code-Änderung tritt erneut in die Ausführung ein; eine Änderung wird nie ohne erneutes Ausführen der Fälle als korrekt angenommen.
- **MUSS [MUST]** einen **Regressionsfall für jeden behobenen Defekt** verlangen (zuerst den fehlschlagenden Fall schreiben, dann bestehen lassen), damit der Zyklus über die Zeit Abdeckung realer Fehler ansammelt [R6].

### Abbruch und die Nicht-Schummeln-Invariante

- **MUSS [MUST]** explizite **Abbruchbedingungen** für eine Zyklus-Umdrehung definieren: Jeder erforderliche Fall ist grün, kein zuvor grüner Fall ist regrediert, und das Coverage-/Mutations-Signal ist akzeptabel gemäß der Coverage-Governance von `spec/project/test-pyramid-foundation/`. Fehlen die, läuft der Zyklus weiter.
- **DARF NICHT [MUST NOT]** den Zyklus durch **Abschwächen, Löschen oder Überspringen eines Tests beenden, um ein Grün zu erzwingen**; ein fehlschlagender Fall wird durch eine Code-Anpassung (Phase 4) gelöst oder durch eine *bewusste, reviewbare* Fall-Änderung, wenn der Fall selbst nachweislich falsch war — nie durch einen stillen Notausgang. Das ist die zentrale Integritätsregel des Zyklus.
- **MUSS [MUST]** einen **Flake** (ein Fall, der ohne Code-Änderung mal besteht und mal fehlschlägt) an Quarantäne-und-Beheben routen gemäß der Determinismus-Regel von `spec/project/test-pyramid-foundation/`, nicht an einen Retry-bis-Grün-Loop.

### Per-Phasen-Spec-Vertrag (der Meta-Vertrag)

- Jede **Phasen-Spec MUSS [MUST]** mindestens definieren: ihren **Zweck und ihre Umfangsgrenze**; ihre **Inputs und Outputs** (gemäß §Inter-Phasen-Verträge); die **Best Practices**, die sie verlangt (je auf zitierte Quellen gegroundet); die **Capability-Specs, die sie referenziert** als Realisierungen, und die Grenze gegen sie; ihre **Feedback-Kanten** in die anderen Phasen; und ihre **kanonischen Anti-Patterns**.
- Eine Phasen-Spec **MUSS [MUST]** eine bestehende Capability-Spec referenzieren statt sie zu wiederholen, wo eine ihre Arbeit abdeckt, und **MUSS** die Grenze nach Verantwortung deklarieren.

### Traceability über den Zyklus

- **MUSS [MUST]** die Anforderung → TC-ID → Test-Traceability des Fundaments über jede Phase bewahren, sodass ein Fall von der Ermittlung über Ausführung, Analyse und die ihn erfüllende Code-Änderung verfolgt werden kann.

## Akzeptanzkriterien

- [ ] Die Spec definiert die vier geordneten Phasen (Testfall-Ermittlung, Ausführung, Ergebnis-Analyse, Code-Anpassung) und den Loop (Phase 4 → Phase 2; wiederholen bis Abbruch)
- [ ] Der Zyklus ist als wiederkehrend/kontinuierlich gerahmt und verallgemeinert Red-Green-Refactor, mit dem Stufenmodell als orthogonal deklariert
- [ ] Inputs und Outputs jeder Phase sind spezifiziert, sodass die Phasen mechanisch zu einem Loop verketten
- [ ] Die Feedback-Kanten (Analyse → Testfall-Ermittlung, Analyse → Code-Anpassung, Code-Anpassung → Ausführung) sind erstklassig, und ein Regressionsfall für jeden behobenen Defekt ist gefordert
- [ ] Explizite Abbruchbedingungen sind definiert, und die Nicht-Schummeln-Invariante (nie einen Test abschwächen/überspringen, um Grün zu erzwingen) ist ein MUSS NICHT
- [ ] Flakes werden an Quarantäne-und-Beheben geroutet, nicht an Retry-bis-Grün
- [ ] Der Per-Phasen-Spec-Meta-Vertrag zählt auf, was jede Phasen-Spec definieren muss, inklusive Referenzieren (nicht Wiederholen) der bestehenden Capability-Specs
- [ ] Der Verhältnis-Abschnitt mappt jede Phase auf ihre referenzierte Capability-Spec (Testfall-Ermittlung → test-case-derivation; Ausführung → quality-gate; Analyse → e2e-result-reviewer / workflow-health; Code-Anpassung → neu)
- [ ] Traceability Anforderung → TC-ID → Test ist über alle Phasen gefordert
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-pyramid-foundation/` — das Stufenmodell, in dem der Zyklus läuft (Struktur vs. Prozess)
- [R2] `spec/project/test-cycle-case-determination/` — Phase 1; referenziert `spec/project/test-case-derivation/`
- [R3] `spec/project/test-cycle-execution/` — Phase 2; referenziert `spec/project/quality-gate/`
- [R4] `spec/project/test-cycle-result-analysis/` — Phase 3; referenziert `e2e-result-reviewer` und `spec/project/workflow-health/`
- [R5] `spec/project/test-cycle-code-adaptation/` — Phase 4 (neu)
- [R6] Martin Fowler, *TestDrivenDevelopment* (Red-Green-Refactor; ein fehlschlagender Test treibt die nächste Änderung; Regressionstest für einen Bug) — <https://martinfowler.com/bliki/TestDrivenDevelopment.html>
- [R7] Martin Fowler, *The Practical Test Pyramid* (der Test-Loop über die Stufen) — <https://martinfowler.com/articles/practical-test-pyramid.html>

## Offene Fragen

- Sollte das Zyklus-Fundament eine Default-**Granularität einer Zyklus-Umdrehung** deklarieren (ein Fall, ein Feature, ein PR) oder sie projekt- und stufenspezifisch lassen?
- Erhalten die vier Phasen je eine Entwickeln/Ausführen/Analysieren-Skill/Agent-Triade, oder erhält der Zyklus selbst einen Orchestrator-Skill, der den Loop treibt und an Per-Phasen-Capabilities dispatcht (die bestehenden `e2e-*`-Artefakte und `quality-gate` decken Teile der Phasen 2–3 bereits ab)?
- Wo der Pfad „bewusste, reviewbare Fall-Änderung" genommen wird (der Fall war falsch), sollte das Fundament eine festgehaltene Begründung verlangen, die ihn an eine Anforderungsänderung bindet, um die Nicht-Schummeln-Invariante auditierbar zu halten?
