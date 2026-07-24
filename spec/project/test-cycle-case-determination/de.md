# Test-Zyklus: Testfall-Ermittlung

Status: draft

## Kontext

Die Testfall-Ermittlung ist **Phase 1** des von `spec/project/test-cycle-foundation/` definierten iterativen Test-Zyklus: zu entscheiden, *welche* Testfälle nötig sind, und sie zu *entwerfen*, damit die nächsten Phasen etwas zum Ausführen und Analysieren haben. Es ist keine einmalige Vorab-Tätigkeit — der Zyklus produziert fortlaufend Fälle: Ein in der Analyse gefundener Defekt wird ein neuer Regressionsfall, eine Coverage-Lücke deckt einen fehlenden Fall auf, explorative Funde werden skriptbasiert, und eine geänderte Anforderung zieht Fälle ein oder zurück. Diese Spec rahmt die Testfall-Ermittlung als diesen wiederkehrenden **Prozess**.

Sie ist eine **Prozess-Spec, die bestehende Capability-Specs referenziert**, keine Wiederholung davon. `spec/project/test-case-derivation/` besitzt bereits die *Technik*, abstrakte, framework-agnostische Fälle aus einem Anforderungsdokument abzuleiten (der `test-case-extractor`-Agent realisiert sie); diese Spec konsumiert diese Capability und ergänzt die zyklus-ebenen Belange: das Erkennen der vollen Familie von Entwurfstechniken, die Auswahl von Fällen nach Risiko, die Iterations-Feedback-Regel, dass der Zyklus nie aufhört Fälle zu produzieren, und den Qualitätsmaßstab, den ein Fall erfüllen muss — während sie *welche Stufe* ein Fall landet dem Stufenmodell überlässt.

Diese Spec füllt den **Per-Phasen-Meta-Vertrag** des Fundaments (Zweck und Umfangsgrenze, Inputs und Outputs, geforderte Best Practices, referenzierte Capability-Specs, Feedback-Kanten, Anti-Patterns). Sie ist bewusst werkzeug- und stufen-agnostisch.

**Verhältnis zu den anderen Specs.** Nach Verantwortung abgegrenzt:

- `spec/project/test-cycle-foundation/` [R1] besitzt den Zyklus, den Loop und den Inter-Phasen-Vertrag dieser Phase. Diese Spec detailliert Phase 1.
- `spec/project/test-case-derivation/` [R2] besitzt die Technik der Anforderung → abstrakter-Fall-Ableitung; diese Spec referenziert sie für diesen Schritt und **DARF** sie **NICHT** wiederholen.
- `spec/project/test-pyramid-foundation/` [R3] besitzt die geschlossene Stufen-Taxonomie; diese Spec entscheidet, *dass* ein Fall nötig ist, und entwirft ihn, während *welche Stufe* er landet die Entscheidung des Stufenmodells ist (niedrigste Stufe, die Vertrauen gibt).
- `spec/project/quality-gate/` [R4] und die Stufen-Specs besitzen die Ausführung; ein Coverage-Bericht aus der Ausführung speist *zurück* in diese Phase, um fehlende Fälle aufzudecken.

Leser: Spec-Autor:innen, die die Geschwister-Phasen-Specs schreiben; Skill- und Agent-Autor:innen, die eine Testfall-Ermittlungs-Capability bauen; Entwickler:innen und Tester:innen, die entscheiden, was zu testen ist; Reviewer, die prüfen, ob ein Fall-Set risiko-priorisiert, nachvollziehbar und nicht redundant ist.

## Ziele

- Die Testfall-Ermittlung als **wiederkehrenden Prozess** rahmen, der über den ganzen Zyklus läuft, nicht nur vorab
- Das Erkennen der vollen **Technik-Familien** (spezifikationsbasiert / black-box, strukturbasiert / white-box, erfahrungsbasiert) sowie der beispiel-getriebenen, property-/modellbasierten und risikobasierten Methoden verlangen
- Die **Iterations-Feedback**-Regel bindend machen: Der Zyklus produziert fortlaufend Fälle (Regression-für-Defekt, Coverage-Lücke, explorativer Fund, Anforderungsänderung)
- Einen **Fall-Qualitätsmaßstab** kodieren (unabhängig, deterministisch-by-design, ein Verhalten, absichtsoffenbarend, beobachtbares Verhalten prüfend, nicht-redundant)
- `test-case-derivation` für anforderungs-abgeleitete Fälle referenzieren und die Stufen-Platzierung dem Stufenmodell überlassen — keine Dublette
- Die Phase werkzeug- und stufen-agnostisch halten

## Nicht-Ziele

- Die Anforderung → abstrakter-Fall-**Ableitungstechnik** zu wiederholen: Eigentum von `spec/project/test-case-derivation/` [R2]
- Zu entscheiden, **welche Stufe** ein Fall landet: Eigentum von `spec/project/test-pyramid-foundation/` [R3] (niedrigste Stufe, die Vertrauen gibt)
- Die Fälle **auszuführen** oder ihre Ergebnisse zu lesen: Phasen 2 und 3 des Zyklus
- Die **Code-Änderung** zu ermitteln, die einen Fall erfüllt: Phase 4 des Zyklus
- Ein bestimmtes Testentwurfs-Werkzeug, ein BDD-Framework oder eine Property-based-Bibliothek vorzuschreiben: Methoden sind nur als illustrative Beispiele genannt

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** diese Phase als **Entscheiden, welche Testfälle nötig sind, und ihr Entwerfen** definieren, das Fälle erzeugt, die fehlschlagen oder abwesend sein sollen, bis sie erfüllt sind, als Phase 1 des Zyklus [R1].
- **DARF NICHT [MUST NOT]** die Anforderung → abstrakter-Fall-Ableitungstechnik wiederholen; wo ein Fall aus einem Anforderungsdokument abgeleitet wird, **MUSS** diese Phase `spec/project/test-case-derivation/` [R2] verwenden und referenzieren.
- **MUSS [MUST]** die **Stufen-Platzierung** `spec/project/test-pyramid-foundation/` [R3] überlassen: Diese Phase ermittelt, *dass* ein Fall nötig ist, und seinen Entwurf; das Stufenmodell fixiert, *welche Stufe* er landet.

### Inputs und Outputs (der Phase-1-Vertrag)

- **MUSS [MUST]** als Inputs beliebige von diesen konsumieren: Anforderungen / Akzeptanzkriterien, **Coverage-Lücken** aus der Ausführung gemeldet, **Defekte** von der Ergebnis-Analyse klassifiziert, explorative Funde und geändertes Verhalten.
- **MUSS [MUST]** als Output eine Menge von Testfällen erzeugen, je mit einer **TC-ID** und einer **gewählten Stufe**, bereit zur Ausführung (Phase 2), gemäß dem Inter-Phasen-Vertrag des Fundaments [R1].

### Testentwurfs-Technik-Familien

- **MUSS [MUST]** die drei ISTQB-Technik-Familien anerkennen und dass die Testfall-Ermittlung aus allen schöpft [R5]:
  - **Spezifikationsbasiert (black-box)** — Fälle aus der Verhaltensspezifikation entwerfen, ohne Bezug auf Interna.
  - **Strukturbasiert (white-box)** — Code-Struktur (Coverage) nutzen, um zu finden, was bestehende Fälle verpassen.
  - **Erfahrungsbasiert** — Error Guessing und exploratives Testen, gestützt auf Tester-Wissen über wahrscheinliche Defekte.
- **MUSS [MUST]** die zentralen **Black-box-Techniken** anwenden, wo sie passen, jede zielt auf ihre Defektklasse [R5], [R6]:
  - **Äquivalenzklassenbildung** — Inputs in Partitionen teilen, die identisch verarbeitet werden; ein Repräsentant pro Partition genügt.
  - **Grenzwertanalyse** — die Ränder geordneter Partitionen üben (2-Wert und 3-Wert); zielt auf Off-by-one- und Falsche-Vergleichsoperator-Defekte.
  - **Entscheidungstabellen-Test** — Fälle aus einer Bedingung → Ergebnis-Tabelle für kombinatorische Geschäftsregeln ableiten.
  - **Zustandsübergangs-Test** — Fälle aus einem Zustandsmodell (`event [guard] / action`) ableiten; zielt auf ungültige oder fehlende Übergänge.
  - **Use-Case-Test** — End-to-End-Szenarien üben.
  - **Pairwise / kombinatorisch** — alle Paare von Parameterwerten abdecken, wenn der volle Kombinationsraum zu groß ist.

### Coverage als Leitlinie zu fehlenden Fällen

- **MUSS [MUST]** **strukturbasierte Coverage** (Statement, Branch/Decision, Path) als **Leitlinie verwenden, um ungetesteten Code aufzudecken, der einen neuen Fall braucht**, nie als numerisches Ziel zum Jagen; Coverage-als-Ziel ist Goodharts Gesetz und erzeugt assertion-freie Tests, gemäß der Coverage-Governance von `spec/project/test-pyramid-foundation/` und Fowler [R7].

### Beispiel-getriebene und Test-first-Ermittlung

- **SOLLTE [SHOULD]** **Example Mapping** (Rules → Examples → Questions) und **Specification by Example / BDD** (Given-When-Then) verwenden, um konkrete Beispiele kollaborativ **vor** dem Coden zu entdecken und Akzeptanzkriterien in Fälle zu verwandeln [R8], [R9]; die vollständige, tool-neutrale BDD-Behandlung (Szenariosprache, Step-Definition-Prinzipien und die Ableitung Testcase-Dokument→Szenario) besitzt `spec/project/behavior-driven-development/` [R15].
- **SOLLTE [SHOULD]** **Test-first (TDD)** als Testfall-Ermittlungs-Praxis behandeln: Der fehlschlagende Test *ist* der Fall, der das nächste Verhaltens-Inkrement definiert [R1].

### Maschinell erzeugte Fälle

- **DARF [MAY]** **Property-based Testing** (Invarianten über generierte Inputs prüfen; die Maschine ermittelt viele Fälle) und **modellbasiertes Testen** (Fälle aus einem Zustandsmodell ableiten) verwenden, um hand-entworfene Fälle zu ergänzen, wo ein Verhalten am besten als Eigenschaft oder Modell ausgedrückt wird [R10], [R11]; maschinell erzeugte Fälle **MÜSSEN** weiterhin die Determinismus-Regel des Fundaments erfüllen (ein fester Seed reproduziert einen Fehler).

### Risikobasierte Auswahl

- **MUSS [MUST]** **welche** Fälle zuerst zu ermitteln und auszuführen sind nach **Risiko** (Eintrittswahrscheinlichkeit × Auswirkung) auswählen, weil erschöpfendes Testen unmöglich ist; die Verhalten mit höchstem Risiko erhalten zuerst Fälle [R13].

### Die Iterations-Feedback-Regel

- **MUSS [MUST]** die Testfall-Ermittlung als **über den Zyklus wiederkehrend** behandeln, nicht nur vorab. Die Phase **MUSS** einen neuen Fall erzeugen, wenn:
  - ein **Defekt** in der Analyse bestätigt wird — einen **fehlschlagenden Regressionsfall schreiben, der ihn reproduziert, bevor er behoben wird** [R1], [R14];
  - eine **Coverage-Lücke** von der Ausführung aufgedeckt wird;
  - ein **explorativer Fund** einen skriptbasierten Fall rechtfertigt;
  - eine **Anforderungsänderung** neues Verhalten einzieht (und Fälle für entferntes Verhalten zurückzieht).

### Fall-Qualitätsmaßstab

- **MUSS [MUST]** verlangen, dass jeder ermittelte Fall **unabhängig** ist (keine Reihenfolge- oder geteilte-Zustand-Abhängigkeit), **deterministisch by design**, auf **ein klares Verhalten** begrenzt, **absichtsoffenbarend** im Namen, und **beobachtbares Verhalten** statt Implementierungsdetail prüft [R12].
- **DARF NICHT [MUST NOT]** **redundante oder überlappende** Fälle erzeugen und **DARF** einen Fall **NICHT** über das von ihm verifizierte Verhalten hinaus über-spezifizieren; Redundanz und Über-Spezifikation erhöhen die Wartungskosten und verursachen falsche Brüche.

### Traceability

- **MUSS [MUST]** die **Anforderung → TC-ID**-Traceability als **einzelnes projektweites Matrix-Artefakt** führen (nicht allein als Per-Fall-Frontmatter), sodass die Abdeckung von Anforderungen—einschließlich, welche Anforderungen *null* Fälle haben—an einer Stelle auditierbar und diff-bar ist, gemäß der Traceability-Kette des Fundaments [R12]. Per-Fall-Frontmatter hält die umgekehrte `Fall → Anforderung`-Kante und ist die Quelle, aus der die Matrix generiert und gegen die sie geprüft wird; es ersetzt die zentrale Matrix nicht, weil die Beantwortung von „welche Anforderungen sind ungedeckt" aus Frontmatter allein das Scannen jedes Falls erfordert und eine Anforderung, die kein Fall referenziert, nicht sichtbar machen kann.

## Akzeptanzkriterien

- [ ] Die Phase ist als Entscheiden, welche Fälle nötig sind, und ihr Entwerfen definiert, referenziert `test-case-derivation` für anforderungs-abgeleitete Ableitung und überlässt die Stufen-Platzierung dem Stufenmodell
- [ ] Inputs (Anforderungen, Coverage-Lücken, Defekte, explorative Funde, geändertes Verhalten) und Outputs (Fälle mit TC-ID + gewählter Stufe) entsprechen dem Phase-1-Vertrag des Fundaments
- [ ] Die drei Technik-Familien sind anerkannt, und die zentralen Black-box-Techniken (Äquivalenzklassen, Grenzwert, Entscheidungstabellen, Zustandsübergang, Use-Case, Pairwise) sind gefordert, wo sie passen, zitiert auf ISTQB
- [ ] Strukturbasierte Coverage ist als Leitlinie zu fehlenden Fällen gebunden, nie als numerisches Ziel (Goodhart), zitiert auf Fowler
- [ ] Example Mapping / Specification by Example / BDD und Test-first sind als beispiel-getriebene Ermittlung gefordert (SOLLTE)
- [ ] Property-based und modellbasiertes Testen sind erlaubt (DARF) mit der Determinismus-Bedingung
- [ ] Risikobasierte Auswahl (Eintrittswahrscheinlichkeit × Auswirkung) ist gefordert
- [ ] Die Iterations-Feedback-Regel ist bindend: ein Regressionsfall für jeden bestätigten Defekt (zuerst den fehlschlagenden Fall schreiben), plus Coverage-Lücken-, explorative und Anforderungsänderungs-Fälle
- [ ] Der Fall-Qualitätsmaßstab (unabhängig, deterministisch-by-design, ein Verhalten, absichtsoffenbarend, beobachtbares Verhalten, nicht-redundant, keine Über-Spezifikation) ist gefordert
- [ ] Eine Anforderung → TC-ID-Traceability-Matrix ist als einzelnes zentrales projektweites Artefakt gefordert (Per-Fall-Frontmatter ist ihre Quelle, kein Ersatz)
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-cycle-foundation/` — der Zyklus, der Loop und der Inter-Phasen-Vertrag dieser Phase
- [R2] `spec/project/test-case-derivation/` — die Anforderung → abstrakter-Fall-Ableitungstechnik, die diese Phase referenziert
- [R3] `spec/project/test-pyramid-foundation/` — besitzt, welche Stufe ein Fall landet
- [R4] `spec/project/quality-gate/` — führt Fälle aus; sein Coverage-Bericht speist zurück in diese Phase
- [R5] ISTQB / ASTQB, *Black-box Test Techniques* (die Technik-Familien; EP, BVA, Entscheidungstabellen, Zustandsübergang, Use-Case) — <https://astqb.org/4-2-black-box-test-techniques/>
- [R6] ISTQB, *Boundary Value Analysis* White Paper (2-Wert / 3-Wert; Off-by-one-Defektklasse) — <https://istqb.org/wp-content/uploads/2025/10/Boundary-Value-Analysis-white-paper.pdf>
- [R7] Martin Fowler, *TestCoverage* (Coverage als Leitlinie zu fehlenden Tests, kein Ziel) — <https://martinfowler.com/bliki/TestCoverage.html>
- [R8] Matt Wynne / Cucumber, *Example Mapping* (Rules → Examples → Questions) — <https://cucumber.io/docs/bdd/example-mapping/>
- [R9] G. Adzic, *Specification by Example* — <https://www.manning.com/books/specification-by-example>
- [R10] *Hypothesis* — Property-based Testing (Invarianten über generierte Inputs) — <https://hypothesis.readthedocs.io/>
- [R11] *quickcheck-state-machine* — modellbasiertes Testen aus einem Zustandsmodell — <https://hackage.haskell.org/package/quickcheck-state-machine>
- [R12] ISTQB Glossary, *test case* / *traceability matrix* (Fall-Qualität; Anforderung → Fall-Traceability) — <https://istqb-glossary.page/test-case/>
- [R13] *Risk-based testing* (Eintrittswahrscheinlichkeit × Auswirkung als Auswahl) — <https://en.wikipedia.org/wiki/Risk-based_testing>
- [R14] *Write a failing test that reproduces the bug before fixing it* — <https://martinfowler.com/articles/testing-culture.html>
- [R15] `spec/project/behavior-driven-development/`: der vollständige tool-neutrale BDD-Standard, den dieses SOLLTE operationalisiert (kollaborative Ermittlung, Szenariosprache, Step-Definition-Prinzipien und die Ableitung Testcase-Dokument→Szenario)

## Offene Fragen

- Sollte die Phase ein Mindest-Technik-Set je Falltyp verlangen (zum Beispiel BVA + EP bei jedem begrenzten numerischen Input) oder beratend bleiben, welche Techniken zutreffen?
- Wo Property-based Testing zutrifft, sollte die Phase es für reine Funktionen mit klaren Invarianten von DARF auf SOLLTE anheben, analog zur offenen Frage der Unit-Stufe?
- ~~Lebt die Anforderung → TC-ID-Matrix in einem einzelnen Projekt-Artefakt, oder genügt Per-Fall-Frontmatter (wie `test-case-derivation` es bereits ausgibt) als Traceability-Nachweis?~~ **Entschieden (2026-07-24): ein zentrales Artefakt.** Die Matrix lebt in einem einzelnen projektweiten Artefakt (siehe Traceability-Anforderung oben); Per-Fall-Frontmatter ist die Rückkanten-Quelle, aus der sie gebaut und gegen die sie geprüft wird, kein Ersatz. Die Audit-Frage, die die Matrix beantworten soll—„welche Anforderungen haben keinen Fall?"—ist eine Coverage-*Lücken*-Frage, und eine Lücke ist genau eine Anforderung, die *kein* Frontmatter referenziert; nur ein zentrales, nach Anforderung geschlüsseltes Artefakt kann sie sichtbar machen, ohne jeden Fall zu scannen, und nur ein diff-bares Artefakt hält den Coverage-Stand an einer Stelle reviewbar.
