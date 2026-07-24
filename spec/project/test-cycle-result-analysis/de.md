# Test-Zyklus: Ergebnis-Analyse

Status: draft

## Kontext

Die Ergebnis-Analyse ist **Phase 3** des von `spec/project/test-cycle-foundation/` definierten iterativen Test-Zyklus: Sie konsumiert die rohen Ergebnisse, die die Ausführung (Phase 2) ausgegeben hat, und **klassifiziert** jedes, damit der Zyklus weiß, was als Nächstes zu tun ist. Klassifikation ist die Kernaufgabe dieser Phase — ein rohes `fail` ist nicht handlungsfähig, bis es als echter Defekt, Flake, falscher Test oder Umgebungsproblem verstanden ist, und jede Kategorie routet eine andere nächste Phase.

Sie ist eine **Prozess-Spec, die bestehende Capability-Specs referenziert**, keine Wiederholung davon. Der `e2e-result-reviewer`-Agent aus `spec/project/e2e-test-automation/` besitzt bereits das **visuelle Review der Screenshots und des Protokolls eines E2E-Laufs** gegen die Anforderungs-Specs, und `spec/project/workflow-health/` besitzt bereits die **Triage-Lanes eines roten CI-Laufs** mit seiner Fehler-Taxonomie; diese Phase referenziert beide und ergänzt den zyklus-ebenen Belang: Ergebnisse in eine geroutete Klassifikation zu verwandeln, die den Loop treibt.

Diese Spec füllt den **Per-Phasen-Meta-Vertrag** des Fundaments (Zweck und Umfangsgrenze, Inputs und Outputs, geforderte Best Practices, referenzierte Capability-Specs, Feedback-Kanten, Anti-Patterns). Sie ist bewusst werkzeug- und stufen-agnostisch.

**Verhältnis zu den anderen Specs.** Nach Verantwortung abgegrenzt:

- `spec/project/test-cycle-foundation/` [R1] besitzt den Zyklus und den Inter-Phasen-Vertrag dieser Phase. Diese Spec detailliert Phase 3.
- `spec/project/test-cycle-execution/` [R2] (Phase 2) gibt die rohen Ergebnisse aus, die diese Phase konsumiert; diese Phase interpretiert, sie führt nicht aus.
- `spec/project/workflow-health/` [R3] besitzt die Rote-CI-Triage-Lanes und die Fehler-Taxonomie (Defekt / Flake / Infra / Stale Pin / Secret Drift / Sonstiges); diese Phase nutzt diese Taxonomie wieder und referenziert sie für die CI-Fehler-Triage, statt sie zu wiederholen.
- `spec/project/e2e-test-automation/` [R4] besitzt das visuelle E2E-Output-Review via `e2e-result-reviewer`; diese Phase referenziert es für die E2E-Stufe, statt es zu wiederholen.

Leser: Spec-Autor:innen, die die Geschwister-Phasen-Specs schreiben; Skill- und Agent-Autor:innen, die eine Ergebnis-Analyse-Capability bauen; Entwickler:innen und Reviewer, die Test-Output lesen; alle, die entscheiden, ob ein rotes Ergebnis ein Code-Bug, ein Test-Bug oder Rauschen ist.

## Ziele

- **Klassifikation zur verpflichtenden ersten Handlung** der Analyse machen: Kein Ergebnis treibt eine Aktion, bevor es eine Kategorie trägt
- **Real-vs-Flake-Disziplin** durchsetzen: Ein Fehlschlag wird nicht ohne Evidenz als Flake wegerklärt, und ein einzelner grüner Re-Run klärt ihn nicht
- **Root-Cause**-Technik verlangen (Diff/Trace lesen, zur verursachenden Änderung bisecten, auf einen Reproducer minimieren)
- **Coverage als Leitlinie** behandeln, die neue Fälle an Phase 1 zurückspeist, und **Mutationsscore** als stärkeres Suite-Qualitätssignal
- Den **Routing-Output-Vertrag** definieren: Jede Klassifikation routet zur richtigen nächsten Phase
- `e2e-result-reviewer` (visuelles Review) und `workflow-health` (CI-Triage) referenzieren — keine Dublette

## Nicht-Ziele

- Die Tests **auszuführen** oder rohe Ergebnisse auszugeben: Phase 2 (`test-cycle-execution`) [R2]
- Die **Rote-CI-Triage-Lanes** zu besitzen: `spec/project/workflow-health/` [R3] (hier referenziert)
- Das **visuelle E2E-Output-Review** zu besitzen: `e2e-result-reviewer` in `spec/project/e2e-test-automation/` [R4] (hier referenziert)
- Den Fix für einen bestätigten Defekt **anzuwenden**: Phase 4 (`test-cycle-code-adaptation`)
- Ein bestimmtes Analyse-Werkzeug oder Dashboard vorzuschreiben: Werkzeuge sind nur als illustrative Beispiele genannt

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** diese Phase als **Interpretieren roher Ergebnisse in eine geroutete Klassifikation** definieren, als Phase 3 des Zyklus [R1]; sie analysiert, sie führt weder Tests aus (Phase 2) noch wendet Fixes an (Phase 4).
- **MUSS [MUST]** die strukturierten Per-Fall-Ergebnisse konsumieren, die `spec/project/test-cycle-execution/` [R2] ausgibt, ohne sie erneut auszuführen.

### Klassifikation vor Aktion

- **MUSS [MUST]** **Klassifikation zur ersten Handlung** machen: Jedes Nicht-Pass-Ergebnis **MUSS** klassifiziert werden, bevor eine Aktion darauf erfolgt. Die Klassen, ausgerichtet an der Fehler-Taxonomie von `spec/project/workflow-health/` [R3], sind: **echter Defekt** (im getesteten Code), **Flake** (nicht-deterministisch), **Test-Bug** (der Test selbst ist falsch), **Infrastruktur / Umgebung**, **Stale Dependency** und **Config / Secret Drift**.
- **MUSS [MUST]** jede Klasse zur nächsten Phase routen: ein **echter Defekt** → Code-Anpassung (Phase 4), mit einem zuerst in Phase 1 ergänzten **neuen Regressionsfall**; ein **Test-Bug** → Testfall-Ermittlung (Phase 1), um den Fall zu korrigieren; ein **Flake** → Quarantäne-und-Verfolgen gemäß den Ausführungs- und Fundament-Regeln; **Infra / Stale Dep / Config Drift** → Umgebung beheben (außerhalb der Test-Zyklus-Phasen, via `workflow-health`).
- **DARF NICHT [MUST NOT]** eine Aktion auf einem **unklassifizierten** Ergebnis ergreifen (es muten, erneut ausführen oder Code ändern) — vor dem Klassifizieren zu handeln ist das Kern-Anti-Pattern dieser Phase.

### Echter Fehlschlag versus Flake

- **DARF NICHT [MUST NOT]** einen Fehlschlag als **Flake ohne Evidenz** wegerklären: Ein Fehlschlag gilt als **echt**, bis die Klassifikation etwas anderes zeigt [R5].
- **MUSS [MUST]** Flakiness durch **unabhängige Re-Runs und Historie** feststellen, nicht durch einen einzelnen Re-Run: Ein einzelner grüner Re-Run klärt einen Fehlschlag **nicht** — ein Ergebnis, das ohne Änderung fehlschlägt und dann besteht, ist Evidenz für Flakiness *die unter Quarantäne zu stellen und zu beheben ist*, nicht dafür, dass der ursprüngliche Fehlschlag gefahrlos ignoriert werden kann [R5], [R6].
- **MUSS [MUST]** den **Ergebnisvektor je Lauf** und das `flip-observed`-Signal konsumieren, das die Ausführung aus ihrem gebundenen Flip-Signal-Retry bei festem **N = 2 zusätzlichen unabhängigen Läufen** (drei Beobachtungen je fehlschlagendem Fall) ausgibt, gemäß `spec/project/test-cycle-execution/` [R2], statt eigene Re-Runs zu beauftragen. Erkennung lebt in Phase 2, Klassifikation lebt hier; diese Phase führt einen Fall nie erneut aus [R2].
- **MUSS [MUST]** `flip-observed: true` als **notwendig, aber nicht hinreichend** für eine `flake`-Klassifikation behandeln: ein Kippen innerhalb der drei Beobachtungen ist zulässige Evidenz, und die Klasse **MUSS [MUST]** zusätzlich auf **Historie** ruhen (derselbe Fall ist zuvor gekippt, oder eine bekannte nicht-deterministische Ursache ist im Trace identifiziert). Ohne dieses zweite Standbein bleibt der Fehlschlag als **echt** klassifiziert, denn ein einzelnes Kippen ist ebenso gut mit einem echten reihenfolge-, zeit- oder zustandsabhängigen Defekt vereinbar, und ein als Flake fehlabgelegter Defekt wird unter Quarantäne gestellt statt behoben.
- **DARF NICHT [MUST NOT]** eine feste Re-Run-Zahl als **Konfidenzschwelle** behandeln: die Phase klassifiziert aus einem festen, auditierbaren N plus Historie, nicht aus einer berechneten Bestehensraten-Wahrscheinlichkeit. Eine statistische Schwelle braucht ein Lauf-Historien-Volumen, das die meisten Projekte nicht haben, variiert je Fall und ist von einer reviewenden Person aus dem ausgegebenen Ergebnis nicht reproduzierbar—das feste N schon.
- **MUSS [MUST]** die **Normalisierung von Flakiness** (routinemäßiges Durchwinken von Fehlschlägen als „wahrscheinlich flaky") als vertrauenszerstörendes Anti-Pattern behandeln, gemäß der Determinismus-Regel des Fundaments.

### Root-Cause-Analyse

- **MUSS [MUST]** einen echten Fehlschlag aus der von der Ausführung ausgegebenen Evidenz lokalisieren: dem **Assertion-Diff** (erwartet vs. tatsächlich), dem **Stack-Trace**, Logs und — auf der E2E-Stufe — den Screenshots und dem Protokoll.
- **SOLLTE [SHOULD]** **Change-Bisection** (zum Beispiel `git bisect`) verwenden, um den verursachenden Commit zu finden, wenn die Ursache aus dem Trace nicht offensichtlich ist [R7].
- **SOLLTE [SHOULD]** einen fehlschlagenden Fall auf einen **minimalen Reproducer** reduzieren, sodass die Ursache isoliert und der spätere Fix verifizierbar ist [R8].

### Coverage- und Suite-Qualitäts-Analyse

- **MUSS [MUST]** **Coverage als Leitlinie** lesen, die ungetesteten Code aufdeckt und einen **neuen Fall an Phase 1 zurückspeist**, nie als Pass/Fail-Zahl, gemäß der Coverage-Governance von `spec/project/test-pyramid-foundation/` und Fowler [R9].
- **SOLLTE [SHOULD]** **Mutationsscore** als stärkeres Suite-Qualitätssignal verwenden — überlebende Mutanten deuten auf schwache oder fehlende Assertions —, als **Trend** gelesen, nicht als absolutes Ziel [R10].

### Visuelle und CI-Signal-Analyse (referenzierte Capabilities)

- **MUSS [MUST]** das **visuelle / E2E-Output-Review** (gerenderter Output, Screenshots, Protokoll gegen die Anforderungs-Specs) an `e2e-result-reviewer` in `spec/project/e2e-test-automation/` [R4] routen; diese Phase referenziert es und **DARF** seine Review-Disziplin **NICHT** wiederholen.
- **MUSS [MUST]** die **Rote-CI-Lauf-Triage** (einen CI-Fehler lesen, ihn in die Lanes klassifizieren) an `spec/project/workflow-health/` [R3] routen; diese Phase nutzt diese Taxonomie wieder und **DARF** die Lanes **NICHT** wiederholen.
- **SOLLTE [SHOULD]** **Trends über Läufe** lesen — viele Fehlschläge mit einer Ursache zu einem Finding deduplizieren und Pass-Rate / Flake-Rate über die Zeit verfolgen, um einen neu-flaky Test oder ein systemisches Infra-Problem zu erkennen.

### Routing-Output (der Phase-3-Vertrag)

- **MUSS [MUST]** pro Fall eine **Klassifikation ausgeben, die zu einer nächsten Phase routet**: `pass` (fertig), `real-failure` (→ Phase 4 + neuer Regressionsfall in Phase 1), `test-bug` (→ Phase 1), `flake` (→ Quarantäne), `coverage-gap` / `missing-case` (→ Phase 1), `infra` / `stale-dep` / `config-drift` (→ Umgebungs-Fix via workflow-health).
- **MUSS [MUST]** die Klassifikation **evidenz-tragend** machen (der Trace/Diff/Reproducer oder die Re-Run-Historie, die die Klasse rechtfertigt), sodass die geroutete nächste Phase auf einer substanziierten Entscheidung handelt, nicht auf einer Vermutung.

### Traceability

- **MUSS [MUST]** jede Klassifikation an die **TC-ID** des analysierten Ergebnisses knüpfen, sodass die Entscheidung zur Anforderung zurück- und zum ausgelösten Fall oder zur Code-Änderung vorwärts-verkettet.

## Akzeptanzkriterien

- [ ] Die Phase ist als Interpretieren roher Ergebnisse in eine geroutete Klassifikation definiert (keine Test-Ausführung, kein Fix-Anwenden), konsumiert den strukturierten Output der Ausführung
- [ ] Klassifikation ist vor jeder Aktion verpflichtend, mit der workflow-health-Fehler-Taxonomie (Defekt / Flake / Test-Bug / Infra / Stale Dep / Config-Secret Drift), und Handeln auf einem unklassifizierten Ergebnis ist verboten
- [ ] Jede Klasse routet zu einer nächsten Phase (echter Defekt → Phase 4 + Regressionsfall in Phase 1; Test-Bug → Phase 1; Flake → Quarantäne; Infra/Stale/Config → Umgebungs-Fix)
- [ ] Real-vs-Flake-Disziplin ist gefordert: echt vermuten, kein Wegerklären ohne Evidenz, und ein einzelner grüner Re-Run klärt einen Fehlschlag nicht, zitiert auf Google; die Flake-Klasse konsumiert den Flip-Signal-Vektor der Ausführung bei festem N = 2 und verlangt zusätzlich Historie, wobei eine Konfidenzschwelle ausdrücklich verworfen ist
- [ ] Root-Cause via Assertion-Diff / Trace / Logs / E2E-Artefakte, Change-Bisection und minimalen Reproducer ist gefordert, zitiert auf git-bisect und Reproducer-Guides
- [ ] Coverage wird als Leitlinie gelesen, die neue Fälle speist (keine Zahl), und Mutationsscore ist das stärkere Suite-Qualitätssignal, als Trend gelesen
- [ ] Visuelles/E2E-Review ist an `e2e-result-reviewer` und Rote-CI-Triage an `workflow-health` geroutet (referenziert, nicht wiederholt), mit Cross-Run-Trend-/Dedup-Analyse
- [ ] Der Routing-Output-Vertrag (per-Fall evidenz-tragende Klassifikation → nächste Phase) ist definiert
- [ ] Klassifikationen sind für Traceability an TC-IDs geknüpft
- [ ] Die Grenze gegen Ausführung (Phase 2), Code-Anpassung (Phase 4), `e2e-result-reviewer` und `workflow-health` ist explizit
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-cycle-foundation/` — der Zyklus und der Inter-Phasen-Vertrag dieser Phase
- [R2] `spec/project/test-cycle-execution/` — Phase 2; gibt die rohen Ergebnisse aus, die diese Phase konsumiert
- [R3] `spec/project/workflow-health/` — die Rote-CI-Triage-Lanes und die Fehler-Taxonomie, die diese Phase wiederverwendet
- [R4] `spec/project/e2e-test-automation/` — visuelles E2E-Output-Review via `e2e-result-reviewer` (referenziert)
- [R5] Google Testing Blog, *Test Flakiness — One of the Main Challenges of Automated Testing* (echt vermuten; Flakiness nicht normalisieren) — <https://testing.googleblog.com/2021/03/test-flakiness-one-of-main-challenges.html>
- [R6] Google Testing Blog, *Test Flakiness* (unabhängig re-runnen; ein Pass klärt einen Fehlschlag nicht) — <https://testing.googleblog.com/2020/12/test-flakiness-one-of-main-challenges.html>
- [R7] Git, *git-bisect* (binäre Suche nach dem verursachenden Commit) — <https://git-scm.com/docs/git-bisect>
- [R8] scikit-learn, *Crafting a minimal reproducer* (einen fehlschlagenden Fall minimieren, um die Ursache zu isolieren) — <https://scikit-learn.org/stable/developers/minimal_reproducer.html>
- [R9] Martin Fowler, *TestCoverage* (Coverage als Leitlinie zu fehlenden Tests, kein Ziel) — <https://martinfowler.com/bliki/TestCoverage.html>
- [R10] Codecov, *Mutation testing: ensuring coverage isn't a vanity metric* (Mutationsscore als stärkeres Signal) — <https://about.codecov.io/blog/mutation-testing-how-to-ensure-code-coverage-isnt-a-vanity-metric/>

## Offene Fragen

- ~~Wie viele unabhängige Re-Runs (und über welches Fenster) sollte die Phase verlangen, bevor sie einen Fehlschlag als Flake versus echt klassifiziert — eine feste Zahl oder eine Konfidenzschwelle?~~ **Entschieden (2026-07-24): eine feste Zahl, und die Phase führt sie nicht selbst aus.** Die Ausführung führt die Re-Runs bei festem N = 2 zusätzlichen unabhängigen Läufen aus und gibt den Ergebnisvektor aus; diese Phase klassifiziert aus diesem Vektor plus Historie, und ein Kippen allein genügt nie für `flake`. Ein festes N ist von einer reviewenden Person aus dem ausgegebenen Ergebnis reproduzierbar, eine berechnete Konfidenzschwelle nicht, und das Historien-Standbein liefert die Trennschärfe, für die man sonst ein größeres N kaufen müsste. Das Fenster ist daher kein Wanduhr-Fenster, sondern die festgehaltene Lauf-Historie des Falls—genau das, was die Phase für Trends ohnehin liest.
- Sollte die Deduplizierung vieler Fehlschläge zu einer Ursache ein geforderter Schritt mit einem benannten Gruppierungs-Schlüssel sein (zum Beispiel Stack-Trace-Signatur) oder beratend bleiben?
- Wo eine Klassifikation `test-bug` ist, sollte die Phase eine festgehaltene Begründung verlangen, die die Fall-Änderung an eine Anforderung bindet, analog zur Nicht-Schummeln-Auditierbarkeits-Frage des Fundaments?
