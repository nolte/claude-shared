# Test-Zyklus: Code-Anpassung

Status: draft

## Kontext

Die Code-Anpassung ist **Phase 4** des von `spec/project/test-cycle-foundation/` definierten iterativen Test-Zyklus: Bei einem bestätigten echten Fehlschlag oder einem fehlenden/roten Fall, den die Analyse (Phase 3) übergeben hat, ermittelt und wendet sie die **minimale korrekte Code-Änderung an, die den Fall bestehen lässt**, und tritt dann erneut in die Ausführung (Phase 2) ein, um zu verifizieren. Sie ist der *grüne* Schritt des Zyklus, vom Test-Driven Development auf jede Stufe und jeden Auslöser verallgemeinert.

Sie ist die einzige **neue** Phase der Zyklus-Familie — die anderen drei referenzieren eine bestehende Capability-Spec, aber einen roten Fall in die richtige Produktions-Änderung zu verwandeln hat keine Vorgänger-Spec. Was sie nicht werden darf, ist ein Weg, ein Grün zu *erzwingen*: Die zentrale **Nicht-Schummeln-Invariante** des Fundaments (nie einen Test abschwächen, löschen, überspringen oder special-casen, um ihn bestehen zu lassen) wird hier geerbt und konkret gemacht. Die Produktions-Änderung muss das **Verhalten** erfüllen, das der Test behauptet, nicht bloß eine Assertion verstummen lassen.

Diese Spec füllt den **Per-Phasen-Meta-Vertrag** des Fundaments (Zweck und Umfangsgrenze, Inputs und Outputs, geforderte Best Practices, referenzierte Capability-Specs, Feedback-Kanten, Anti-Patterns). Sie ist bewusst werkzeug- und stufen-agnostisch.

**Verhältnis zu den anderen Specs.** Nach Verantwortung abgegrenzt:

- `spec/project/test-cycle-foundation/` [R1] besitzt den Zyklus und die Nicht-Schummeln-Abbruchregel, die diese Phase konkret macht. Diese Spec detailliert Phase 4.
- `spec/project/test-cycle-result-analysis/` [R2] (Phase 3) übergibt dieser Phase einen **bestätigten echten Fehlschlag**; diese Phase handelt darauf, sie klassifiziert nicht.
- `spec/project/test-cycle-execution/` [R3] (Phase 2) führt die Änderung erneut aus, um sie zu verifizieren; diese Phase nimmt nie Grün ohne erneute Ausführung an.
- `spec/project/test-cycle-case-determination/` [R4] (Phase 1) besitzt den **reviewbaren Fall-Änderungs-Pfad**, wenn der Test selbst falsch war — das wird dorthin geroutet, es ist hier **kein** Code-Hack.

Leser: Spec-Autor:innen, die die Zyklus-Familie vervollständigen; Skill- und Agent-Autor:innen, die eine Code-Anpassungs-Capability bauen; Entwickler:innen, die einen roten Test grün machen; Reviewer, die prüfen, ob eine Änderung die Wurzelursache behoben und nicht den Test ausgetrickst hat.

## Ziele

- Die Änderung zur **einfachsten korrekten** machen, die den Fall erfüllt, dann unter Grün refactoren
- Das Beheben der **Wurzelursache, nicht des Symptoms** verlangen und die **allgemeine** Lösung schreiben statt auf das Beispiel zu overfitten
- Die **Nicht-Schummeln-/Test-Integritäts-Invariante** des Fundaments konkret machen: das behauptete Verhalten erfüllen, nie den Test abschwächen oder special-casen
- **Refactoring verhaltenswahrend** halten und vom Verhaltenswechsel getrennt, mit der Suite als Sicherheitsnetz
- **Verify-by-Re-Execution** verlangen (erneut in Phase 2 eintreten; alles grün, keine Regression) und eine kleine, reviewbare Änderung
- Eine Falsch-Test-Korrektur an Phase 1 routen (eine reviewbare Fall-Änderung), nicht an einen Code-Hack — keine Dublette

## Nicht-Ziele

- Einen Fehlschlag zu **klassifizieren** (zu entscheiden, dass es ein echter Defekt ist): Phase 3 (`test-cycle-result-analysis`) [R2]
- Die Tests zur Verifikation **auszuführen**: Phase 2 (`test-cycle-execution`) [R3] (diese Phase löst sie aus, besitzt sie nicht)
- Einen **falschen Test zu korrigieren**: Das ist eine reviewbare Fall-Änderung in Phase 1 (`test-cycle-case-determination`) [R4], keine Code-Änderung hier
- Eine bestimmte Sprache, einen Editor oder ein Refactoring-Werkzeug vorzuschreiben: Techniken sind nur als illustrative Beispiele genannt
- Tests zu erkennen, die von Geburt an nicht fehlschlagen konnten (nie durch eine Änderung degradiert): Eigentum von `spec/project/test-falsifiability/` [R12]; die Invariante dieser Phase deckt falsifizierbarkeits-zerstörende *Übergänge* ab, sichtbar in einem Diff

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** diese Phase als **Ermitteln und Anwenden der minimalen korrekten Code-Änderung, die einen bestätigt-roten Fall bestehen lässt** definieren, als Phase 4 des Zyklus [R1].
- **MUSS [MUST]** nur auf einem **bestätigten echten Fehlschlag** (oder einem fehlenden Fall) handeln, der von `spec/project/test-cycle-result-analysis/` [R2] geroutet wurde; sie re-klassifiziert nicht.
- **MUSS [MUST]** einen **falschen Test** an Phase 1s reviewbaren Fall-Änderungs-Pfad routen [R4], ihn nie durch Hacken des Codes auf eine falsche Assertion lösen.

### Inputs und Outputs (der Phase-4-Vertrag)

- **MUSS [MUST]** als Input eine Phase-3-Klassifikation `real-failure` (oder `missing-case`) für eine TC-ID konsumieren, mit ihrer stützenden Evidenz (Trace, Diff, Reproducer).
- **MUSS [MUST]** als Output eine **Code-Änderung** erzeugen, die erneut in die Ausführung (Phase 2) eintritt; die Änderung ist die Produktions-Edition, nie eine Edition, die den Fall abschwächt.

### Der grüne Schritt: zuerst die einfachste Änderung

- **MUSS [MUST]** die **einfachste Änderung, die möglicherweise funktionieren könnte** machen, um den Fall grün zu bekommen, dann unter Grün verbessern; der Produktionscode wird **als Antwort auf einen fehlschlagenden Test** geschrieben, nicht ihm voraus [R5].
- **DARF [MAY]** die anerkannten grünen Strategien nach Zuversicht (Beck) verwenden [R6]:
  - **Obvious Implementation** — den echten Code direkt tippen, wenn er offensichtlich ist.
  - **Fake It** — eine Konstante zurückgeben, um grün zu werden, dann generalisieren.
  - **Triangulation** — die Implementierung erst generalisieren, sobald **zwei oder mehr Beispiele** es erzwingen.

### Wurzelursache, nicht Symptom; kein Over-Fitting

- **MUSS [MUST]** die **Wurzelursache** beheben, nicht das Symptom: Eine Änderung, die eine Exception verschluckt, den fehlschlagenden Input special-cast oder anderweitig um den Defekt herum-patcht, ohne ihn zu korrigieren, ist verboten.
- **MUSS [MUST]** die **allgemeine** Lösung schreiben, nicht eine, die nur das aktuelle Beispiel erfüllt; **Triangulation** ist die Disziplin, die Allgemeinheit erzwingt, und **Property-based**-Fälle (die über generierte Inputs prüfen) widerstehen Over-Fitting, weil kein einzelner hartcodierter Wert sie erfüllt [R7].

### Die Nicht-Schummeln-/Test-Integritäts-Invariante

- **DARF NICHT [MUST NOT]** einen Fall bestehen lassen durch **Abschwächen, Löschen, Überspringen oder Hartcodieren auf den erwarteten Wert des Tests**; die Änderung muss das **Verhalten** erfüllen, das der Fall behauptet, nicht bloß eine Assertion. Das ist die Nicht-Schummeln-Invariante des Fundaments, konkret gemacht für Phase 4 [R1].
- **MUSS [MUST]** **legitime Generalisierung** der Implementierung von **Special-Casing der Test-Inputs** unterscheiden: die richtige Antwort für die allgemeine Klasse zurückzugeben ist ein Fix; eine auf den Test-Input gematchte Konstante zurückzugeben (über einen transienten Fake-It-Schritt auf dem Weg zur Generalisierung hinaus) ist Austricksen des Tests. Die Unterscheidung ist **prüfbar**, keine Geschmacksfrage. Die leitende Regel: *Eine Änderung generalisiert, wenn sie eine Regel ändert; sie special-cased, wenn sie einen Zweig auf den Daten des Falls hinzufügt.* Drei Signale entscheiden sie, in dieser Reihenfolge:
  1. **Literal-Überlappung.** Ein Wert, der sowohl im Input- oder Erwartungswert-Set des Falls als auch in der Produktionsänderung auftaucht, ist der stärkste Einzelindikator für Special-Casing. Eine Änderung mit einem solchen Literal **MUSS [MUST]** als Special-Casing behandelt werden, sofern Signal 3 sie nicht freigibt.
  2. **Prädikat-Form.** Eine neue Bedingung, deren Prädikat eine Gleichheits- oder Identitätsprüfung gegen einen fallspezifischen Wert ist (`if user_id == 42`, `if tenant == "acme-test"`), ist Special-Casing; ein Prädikat, das in den Begriffen der Domäne formuliert ist (ein Bereich, ein Typ, ein dokumentierter Zustand), ist eine Regel.
  3. **Zweit-Beispiel-Probe.** Füge ein weiteres Beispiel aus *derselben* Äquivalenzklasse mit anderen Werten hinzu. Besteht es ohne weitere Änderung an derselben Stelle, hat die Änderung generalisiert; erzwingt es dort eine weitere Änderung, war die erste ein Sonderfall. Diese Probe ist der Stichentscheid für die Signale 1 und 2, wenn sie sich widersprechen oder das Literal plausibel der Domäne gehört—kein pauschales Triangulations-Gebot.
- **DARF [MAY]** special-casen, wo die **Domäne selbst** unstetig ist (eine dokumentierte Ausnahme, eine regulatorische Grenze, eine Legacy-Kompatibilitäts-Ausnahme); eine solche Änderung **MUSS [MUST]** eine schriftliche Begründung tragen, die die Domänenregel benennt, die die Unstetigkeit erzeugt, und **MUSS [MUST]** von einem Fall begleitet sein, der den allgemeinen Zweig übt, damit die Ausnahme im Review sichtbar ist statt aus einem nackten Literal erschlossen.
- **MUSS [MUST]** den **reviewbaren Fall-Änderungs-Pfad** (an Phase 1 routen) nehmen, wenn der Fall selbst nachweislich falsch war, mit einer festgehaltenen Begründung, statt still eine Assertion auf den Code zu ändern. Eine **legitime Erwartungsänderung** ist von verbotener Test-Abschwächung durch zwei prüfbare Eigenschaften getrennt, ihre **Quelle** und ihre **Reihenfolge**: sie ist *stromaufwärts* begründet (eine geänderte Anforderung, Spec oder ein geänderter Vertrag existiert, und die festgehaltene Begründung zitiert ihn), nie durch den Fehlschlag selbst, denn „der Fall ist rot" ist keine Rechtfertigung; und sie landet als **eigene Änderung, vor der Produktionsänderung**, sodass die Historie Erwartungsänderung-dann-Code-Änderung liest statt einer still auf den Code gerückten Assertion. Phase 4 **DARF [MUST NOT]** daher eine Erwartung eines Falls **NICHT** selbst ändern: sie gibt den Fall an Phase 1 zurück und benennt das stromaufwärtige Delta, und setzt fort, sobald der korrigierte Fall aus dem richtigen Grund rot ist.

### Refactor unter Grün

- **SOLLTE [SHOULD]** nach grünem Fall refactoren: **kleine, verhaltenswahrende Transformationen** anwenden, um die Struktur zu verbessern, mit der Suite als Sicherheitsnetz — Refactoring **DARF** das beobachtbare Verhalten **NICHT** ändern [R8], [R9].
- **DARF NICHT [MUST NOT]** **Refactoring mit einem Verhaltenswechsel** im selben Schritt mischen; nur unter Grün refactoren, und Verhaltensänderungen als eigenen Red-Green-Schritt machen [R9], [R10].

### Regressionsgetriebener Fix

- **MUSS [MUST]**, wenn der Auslöser ein in der Analyse gefundener Defekt ist, den neuen **fehlschlagenden Regressionsfall** (zuerst in Phase 1 geschrieben) bestehen lassen, **während jeder vorherige Fall grün bleibt**; der grüne Regressionsfall ist der Beweis, dass der Defekt behoben ist und behoben bleibt [R10], [R11].

### Verify-by-Re-Execution und Review

- **DARF NICHT [MUST NOT]** annehmen, dass die Änderung korrekt ist: Sie **MUSS** erneut in die Ausführung (Phase 2) eintreten, und **alle** Fälle **MÜSSEN** grün sein mit **keiner Regression**, bevor die Zyklus-Umdrehung enden kann [R3], [R11].
- **MUSS [MUST]** die Änderung **klein und reviewbar** halten, und **SOLLTE** sie reviewen lassen (durch einen Menschen oder einen automatisierten Reviewer) auf Korrektheit und darauf, den Test nicht ausgetrickst zu haben, konsistent mit dem Pull-Request-Review des Projekts.

### Traceability

- **MUSS [MUST]** die Änderung an die **TC-ID(s)** knüpfen, die sie erfüllt, sodass die Produktions-Edition über Analyse und Fall zur Anforderung zurück-verkettet und die Traceability des Zyklus schließt.

## Akzeptanzkriterien

- [ ] Die Phase ist als Ermitteln/Anwenden der minimalen korrekten Code-Änderung für einen bestätigt-roten Fall definiert (Phase 4), handelt nur auf einem Phase-3-real-failure/missing-case und routet einen falschen Test an Phase 1
- [ ] Inputs (Phase-3-`real-failure`/`missing-case` + Evidenz) und Output (eine Code-Änderung, die erneut in die Ausführung eintritt, nie eine test-abschwächende Edition) entsprechen dem Phase-4-Vertrag des Fundaments
- [ ] Der grüne Schritt verlangt zuerst die einfachste Änderung (als Antwort auf einen fehlschlagenden Test), mit Becks Obvious-Implementation- / Fake-It- / Triangulation-Strategien anerkannt
- [ ] Das Beheben der Wurzelursache statt des Symptoms ist gefordert, und Over-Fitting ist verboten mit Triangulation und Property-based-Fällen als Anti-Over-Fitting-Disziplin
- [ ] Die Nicht-Schummeln-Invariante ist konkret: kein Abschwächen/Löschen/Überspringen/Hartcodieren-auf-den-erwarteten-Wert; Verhalten erfüllen, nicht eine Assertion; die Unterscheidung legitime-Generalisierung-vs-Special-Casing ist als prüfbare Drei-Signal-Heuristik gezogen (Literal-Überlappung, Prädikat-Form, Zweit-Beispiel-Probe) mit einer begründungspflichtigen Ausnahme für eine echt unstetige Domäne
- [ ] Der reviewbare Fall-Änderungs-Pfad (Test war falsch → Phase 1, festgehaltene Begründung) ist gefordert statt eines Code-Hacks, und eine legitime Erwartungsänderung ist an eine stromaufwärtige Quelle gebunden und landet als eigene Änderung vor der Produktionsänderung, wobei Phase 4 nie selbst eine Erwartung ändert
- [ ] Refactor-unter-Grün ist verhaltenswahrend und nicht mit Verhaltenswechsel gemischt, zitiert auf Fowler
- [ ] Der regressionsgetriebene Fix (neuer fehlschlagender Fall grün + alle vorherigen grün) ist gefordert, zitiert
- [ ] Verify-by-Re-Execution (erneut in Phase 2 eintreten; alles grün, keine Regression) und eine kleine reviewbare Änderung sind gefordert
- [ ] Die Änderung ist für Traceability an TC-ID(s) geknüpft, und die Grenze gegen die Phasen 1/2/3 und das Fundament ist explizit
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-cycle-foundation/` — der Zyklus und die Nicht-Schummeln-Abbruchregel, die diese Phase konkret macht
- [R2] `spec/project/test-cycle-result-analysis/` — Phase 3; übergibt dieser Phase einen bestätigten echten Fehlschlag
- [R3] `spec/project/test-cycle-execution/` — Phase 2; führt die Änderung erneut aus, um sie zu verifizieren
- [R4] `spec/project/test-cycle-case-determination/` — Phase 1; besitzt den reviewbaren Fall-Änderungs-Pfad, wenn der Test falsch war
- [R5] Martin Fowler, *TestDrivenDevelopment* (funktionalen Code schreiben, bis der Test besteht, als Antwort auf einen fehlschlagenden Test) — <https://martinfowler.com/bliki/TestDrivenDevelopment.html>
- [R6] Kent Beck, *Test-Driven Development by Example* — Fake It / Obvious Implementation / Triangulation — <https://relentlessdevelopment.wordpress.com/2014/06/18/make-it-run-make-it-right-the-three-implementation-strategies-of-tdd/>
- [R7] *Property-based testing* (Eigenschaften über generierte Inputs widerstehen Over-Fitting) — <https://arxiv.org/pdf/2307.04346>
- [R8] Martin Fowler, *Refactoring* / *RefactoringMalapropism* (kleine verhaltenswahrende Transformationen; Refactoring ändert das beobachtbare Verhalten nicht) — <https://martinfowler.com/bliki/RefactoringMalapropism.html>
- [R9] Martin Fowler, *Opportunistic Refactoring* (nur unter Grün refactoren; hängt von einer Regressions-Suite ab) — <https://martinfowler.com/bliki/OpportunisticRefactoring.html>
- [R10] Martin Fowler, *Self-Testing Code* (einen Test schreiben, der den Bug zeigt, dann beheben; die Suite als Sicherheitsnetz) — <https://martinfowler.com/bliki/SelfTestingCode.html>
- [R11] *Regression testing* (ein Fix hält vorheriges Verhalten grün) — <https://en.wikipedia.org/wiki/Regression_testing>
- [R12] `spec/project/test-falsifiability/` — die Taxonomie von Geburt an nicht fehlschlagbarer Tests; abgegrenzt von der übergangs-deckenden Invariante dieser Phase

## Offene Fragen

- ~~Welche konkreten Signale unterscheiden am besten **legitime Generalisierung** von **Special-Casing der Test-Inputs** — kann die Phase eine prüfbare Heuristik benennen, oder bleibt es eine Review-Beurteilung?~~ **Entschieden (2026-07-24): eine prüfbare Heuristik.** Die Regel lautet *ändert eine Regel = Generalisierung, fügt einen Zweig auf den Daten des Falls hinzu = Special-Casing*, entschieden durch drei geordnete Signale (Literal-Überlappung, Prädikat-Form, Zweit-Beispiel-Probe), festgehalten in §„Die Nicht-Schummeln-/Test-Integritäts-Invariante". Zwei der drei sind allein aus dem Diff maschinell erkennbar—genau das macht die Invariante durchsetzbar statt aspirativ; die Probe löst die verbleibenden Ermessensfälle, ohne Triangulation überall vorzuschreiben. Eine echt unstetige Domäne behält eine Ausnahme, bezahlt sie aber mit schriftlicher Begründung und einem Fall auf dem allgemeinen Zweig, sodass die Ausnahme nicht als Deckung dienen kann.
- ~~Wenn ein Fix tatsächlich verlangt, dass sich die **Erwartung eines bestehenden Tests ändert** (die alte Assertion kodierte ein nun entferntes Verhalten), wie hält die Phase das auf dem reviewbaren Fall-Änderungs-Pfad und außerhalb der verbotenen Test-Abschwächungs-Kategorie?~~ **Entschieden (2026-07-24): über Quelle und Reihenfolge, wobei Phase 4 nie eine Erwartung anfasst.** Eine legitime Erwartungsänderung zitiert ein stromaufwärtiges Delta (Anforderung, Spec oder Vertrag) und landet als eigene Änderung *vor* der Produktionsänderung; die verbotene Variante ist allein durch das rote Ergebnis begründet und fährt im Fix mit. Beide Eigenschaften sind in der Historie sichtbar, sodass die Unterscheidung ein Review übersteht, ohne auf Absicht schließen zu müssen. Phase 4 gibt den Fall an Phase 1 zurück, statt ihn zu ändern, und macht den Fall-Änderungs-Pfad damit per Konstruktion zur einzigen Route.
- Sollte die Phase **Triangulation oder einen Property-based-Fall** für jede nicht-triviale Generalisierung vorschreiben, um Over-Fitting strukturell schwer zu machen, oder es beratend lassen?
