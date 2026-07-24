# Test-Zyklus: Ausführung

Status: draft

## Kontext

Die Ausführung ist **Phase 2** des von `spec/project/test-cycle-foundation/` definierten iterativen Test-Zyklus: Sie konsumiert die in Phase 1 ermittelten Fälle, führt sie aus und gibt rohe Ergebnisse für die Analyse in Phase 3 aus. Weil der Zyklus fortlaufend erneut ausführt (jede Code-Anpassung tritt erneut in die Ausführung ein), ist dies die Phase, deren **Geschwindigkeit und Determinismus** entscheiden, ob der ganze Zyklus vertrauenswürdig und schnell genug ist, um damit zu leben.

Sie ist eine **Prozess-Spec, die bestehende Capability-Specs referenziert**, keine Wiederholung davon. `spec/project/quality-gate/` besitzt bereits den einen erkennbaren Aufruf, der Lint + Typecheck + Test ausführt und das Ergebnis tabelliert; diese Spec wiederholt das nicht. Sie rahmt die Ausführung als die wiederkehrende Laufzeit-Disziplin — deterministische/hermetische Ausführung, Isolation, parallele/selektive Geschwindigkeit, gestufte CI-Platzierung, Flake-Handhabung und der strukturierte Ergebnis-Emissions-Vertrag — die das Gate und die Stufen-Runner realisieren.

Diese Spec füllt den **Per-Phasen-Meta-Vertrag** des Fundaments (Zweck und Umfangsgrenze, Inputs und Outputs, geforderte Best Practices, referenzierte Capability-Specs, Feedback-Kanten, Anti-Patterns). Sie ist bewusst werkzeug- und stufen-agnostisch.

**Verhältnis zu den anderen Specs.** Nach Verantwortung abgegrenzt:

- `spec/project/test-cycle-foundation/` [R1] besitzt den Zyklus und den Inter-Phasen-Vertrag dieser Phase. Diese Spec detailliert Phase 2.
- `spec/project/quality-gate/` [R2] besitzt das Single-Invocation-Gate (Lint + Typecheck + Test) und seine Ausgabetabelle; diese Spec referenziert es als Ausführer der schnellen Stufen und **DARF** seinen Aufruf-Vertrag **NICHT** wiederholen.
- `spec/project/test-pyramid-foundation/` [R3] besitzt die Determinismus-Regel und die Ausführungs-Platzierung jeder Stufe; diese Spec wendet sie zur Laufzeit an, sie definiert sie nicht neu.
- `spec/project/workflow-health/` [R4] triagiert einen *roten CI-Lauf* — diese Interpretation ist Phase 3 (Ergebnis-Analyse), nicht diese Phase; die Ausführung gibt rohe Ergebnisse aus, die Analyse klassifiziert sie.

Leser: Spec-Autor:innen, die die Geschwister-Phasen-Specs schreiben; Skill- und Agent-Autor:innen, die eine Ausführungs-Capability bauen; Entwickler:innen und CI-Engineers, die verdrahten, wie Tests laufen; Reviewer, die prüfen, ob die Ausführung deterministisch, isoliert, schnell, gestuft ist und ein strukturiertes Ergebnis ausgibt.

## Ziele

- **Deterministische, hermetische Ausführung** zum Laufzeit-Maßstab machen: gleicher Input, gleiches Ergebnis, unabhängig von Maschine, Reihenfolge oder Umgebung
- **Isolation und beliebige Reihenfolge** verlangen, mit Readiness-Bedingungs-Waits statt nackter Sleeps
- **Geschwindigkeit** aus Parallelisierung/Sharding und Testauswahl gewinnen, da der Zyklus fortlaufend erneut ausführt
- Die Ausführung in der CI staffeln: schnelle Stufen gaten den PR, langsame/breite Stufen laufen in einer dedizierten Stufe oder Nightly
- Flakes durch **gebundenes Retry + verfolgte Quarantäne** handhaben, nie Retry-bis-Grün
- Ein **strukturiertes, maschinenlesbares Per-Fall-Ergebnis** als Phase-2-Output-Vertrag ausgeben
- `quality-gate` als Gate-Ausführer und die Stufen-Specs für die Platzierung referenzieren — keine Dublette

## Nicht-Ziele

- Das Single-Invocation-Gate (Lint + Typecheck + Test) und seine Ausgabetabelle zu wiederholen: Eigentum von `spec/project/quality-gate/` [R2]
- Ergebnisse zu **interpretieren** (Pass/Fail/Flake/Defekt klassifizieren): Phase 3 (Ergebnis-Analyse)
- Einen roten CI-Lauf zu triagieren: Eigentum von `spec/project/workflow-health/` [R4], aufgerufen aus Phase 3
- Zu **ermitteln**, welche Fälle zu laufen sind (das ist Phase 1), oder die **Code-Änderung** für einen Fehlschlag (Phase 4)
- Einen bestimmten Runner, ein CI-System oder ein Report-Format vorzuschreiben: Werkzeuge und Formate sind nur als illustrative Beispiele genannt

## Anforderungen

### Zweck und Umfangsgrenze

- **MUSS [MUST]** diese Phase als **Ausführen der ermittelten Fälle und Ausgeben roher Ergebnisse** definieren, als Phase 2 des Zyklus [R1]; sie führt aus, sie interpretiert nicht.
- **DARF NICHT [MUST NOT]** den `quality-gate`-Single-Invocation-Vertrag oder die Ausgabetabelle wiederholen; diese Phase **MUSS** `spec/project/quality-gate/` [R2] als Ausführer der schnellen Stufen referenzieren.
- **MUSS [MUST]** die Determinismus-Regel von `spec/project/test-pyramid-foundation/` und die Ausführungs-Platzierung jeder Stufe zur Laufzeit anwenden statt sie neu zu definieren [R3].

### Inputs und Outputs (der Phase-2-Vertrag)

- **MUSS [MUST]** als Input die Menge der Fälle aus Phase 1 konsumieren (TC-IDs und gewählte Stufen).
- **MUSS [MUST]** als Output ein **strukturiertes, maschinenlesbares Ergebnis pro Fall** ausgeben — Pass / Fail / Error / Skip, plus Fehlermeldung und Stack-Trace, Timing, Coverage-Daten, wo die Stufe sie erzeugt, und die Screenshot-/Protokoll-Artefakte auf der E2E-Stufe — sodass Phase 3 es ohne out-of-band-Wissen analysieren kann [R13]. Standard-Formate (zum Beispiel TAPs `ok`/`not ok` mit YAML-Diagnostik oder JUnit XML) sind illustrativ.

### Deterministische und hermetische Ausführung

- **MUSS [MUST]** die Ausführung **deterministisch** machen: Derselbe Input gibt dasselbe Ergebnis, unabhängig von Maschine, Reihenfolge, Zeit oder Netzwerklage; ein nicht-deterministischer (flaky) Test ist für Regression nutzlos und untergräbt das Vertrauen in die ganze Suite [R5].
- **MUSS [MUST]** die Laufzeit-Umgebung kontrollieren, um das zu erreichen: **die Uhr wrappen** (Zeit einfrieren/substituieren), Zufall kontrollieren, Remote-/externe Services durch Test-Doubles ersetzen (validiert durch die Contract-Stufe) und geteilten Zustand isolieren [R5].
- **SOLLTE [SHOULD]** Tests **hermetisch** ausführen — jeder Lauf bringt seine eigenen Abhängigkeiten mit und hängt nicht von externem veränderlichem Zustand ab — sodass ein Lauf reproduzierbar und parallel-sicher ist [R9].

### Isolation, Reihenfolge und Readiness-Waits

- **MUSS [MUST]** Tests **isoliert** halten, sodass jede Ausführungsreihenfolge funktioniert, mit Per-Test-Setup und -Teardown; **SOLLTE** in **randomisierter Reihenfolge** laufen, um versteckte Inter-Test-Abhängigkeiten aufzudecken.
- **DARF NICHT [MUST NOT]** **nackte Sleeps** verwenden, um auf asynchrone Ergebnisse oder Dependency-Start zu warten; eine **Readiness-Bedingung** pollen (kleines Intervall, gebundenes Wartelimit) oder einen Callback nutzen [R5], [R14].
- **DARF NICHT [MUST NOT]** gegen eine **geteilte, veränderliche, langlebige** Umgebung ausführen; ephemere echte Abhängigkeiten auf der Integration-Stufe folgen derselben Wait-on-Readiness-Regel [R14].

### Geschwindigkeit: Parallelisierung, Auswahl, Caching

- **SOLLTE [SHOULD]** Tests **parallel ausführen und sharden** über Worker, um das Feedback des Zyklus schnell zu halten [R8].
- **DARF [MAY]** **Test Impact Analysis / Predictive Test Selection** verwenden, um nur die von einer Änderung betroffenen Tests auszuführen und dabei das Regressions-Signal zu bewahren (Meta berichtet, etwa ein Drittel der abhängigen Tests auszuführen und dabei über 99,9 % der fehlerhaften Änderungen zu fangen) — sofern die volle Suite weiterhin nach Zeitplan läuft, damit die Auswahl nie still Abdeckung fallen lässt [R7].
- **SOLLTE [SHOULD]** sich auf **reproduzierbare Builds** stützen, damit maschinenübergreifendes Test-/Build-Caching sicher ist (ein gecachtes Ergebnis ist nur gültig, wenn die Inputs bit-für-bit reproduzierbar sind) [R9].

### Gestufte CI-Ausführung

- **MUSS [MUST]** die Ausführung nach Stufe staffeln: Die **schnellen Stufen** (Static, Unit, Component, schmale Integration, Contract) **MÜSSEN** den Pull Request gaten, und die **langsamen/breiten Stufen** (E2E, breite Integration, Performance) **SOLLTEN** in einer dedizierten Stufe oder Nightly laufen, gemäß dem CI-Gating-Modell von `spec/project/test-pyramid-foundation/` und der Platzierung der Stufen-Specs [R3], [R10].
- **SOLLTE [SHOULD]** die PR-gatende Stufe schnell halten (eine ~10-Minuten-Commit-Build-Leitlinie) und die relevantesten oder schnellsten Specs **zuerst** ausführen (Fail-fast), damit Feedback früh ankommt; ob der Lauf dann kurzschließt oder bis zur Sammlung aller Fehlschläge durchläuft, ist eine Projekt-Wahl [R10], [R11].

### Flake-Handhabung zur Ausführungszeit

- **DARF NICHT [MUST NOT]** **einen Test wiederholen, bis er grün wird**: Auto-Retry-bis-Pass verbirgt echte Flakiness und liefert ein kaputtes Signal aus [R6], [R12].
- **MUSS [MUST]** die **Flake-Erkennung** besitzen und die **Flake-Klassifikation** Phase 3 überlassen: diese Phase erzeugt die Beobachtung, Phase 3 vergibt die Klasse. Diese Trennung hält die Invariante „ein einzelner grüner Re-Run räumt einen Fehlschlag nicht ab" durchsetzbar, weil die Komponente, die erneut ausführt, nie die Komponente ist, die den Fehlschlag für harmlos erklärt.
- **MUSS [MUST]** ein **gebundenes Flip-Signal-Retry** auf einem fehlschlagenden Fall verwenden: **N = 2 zusätzliche unabhängige Läufe** (drei Beobachtungen insgesamt), in derselben Ausführung und unter demselben gepinnten Kommando und derselben Umgebung. Zwei Zusatzläufe sind das kleinste N, das ein Kippen in beide Richtungen beobachten kann und billig genug bleibt, um auf jedem roten Fall zu laufen; N = 1 kann ein Kippen nicht von einem Zufall unterscheiden, und ein größeres N kauft Konfidenz, die diese Phase nicht ausgeben darf, weil Klassifikation Phase 3 gehört. Ein Projekt **DARF [MAY]** N erhöhen (nie senken) und **MUSS [MUST]** den verwendeten Wert festhalten.
- **MUSS [MUST]** den **Ergebnisvektor je Lauf** für diesen Fall ausgeben (zum Beispiel `fail, pass, fail`) samt einem abgeleiteten `flip-observed: true|false`-Signal als Teil des strukturierten Ergebnisses, und **DARF [MUST NOT]** den Fall **NICHT** selbst als `flaky` oder `real` etikettieren, den Vektor auf sein bestes Ergebnis kollabieren oder einen grünen Re-Run das ursprüngliche Rot im ausgegebenen Ergebnis ersetzen lassen.
- **MUSS [MUST]** einen bekannt-flaky Test **unter Quarantäne stellen** (ihn vom gatenden Signal ausschließen, während er als zu behebender Defekt verfolgt wird), statt ihn das Gate blockieren oder ihn still ewig erneut ausführen zu lassen [R5], [R12].

### Reproduzierbarkeit und Pinning

- **MUSS [MUST]** die Runner-, Tool- und Dependency-Versionen pinnen, sodass eine Ausführung über Maschinen und über die Zeit reproduzierbar ist, und **SOLLTE** den exakten Befehl und die Umgebung festhalten, die ein Ergebnis erzeugt haben, sodass ein Fehlschlag von Phase 3 identisch erneut ausgeführt werden kann [R9].

### Traceability

- **MUSS [MUST]** jedes ausgegebene Ergebnis an die **TC-ID** des ausgeführten Falls knüpfen, sodass das Ergebnis über die Traceability des Fundaments zur Anforderung zurück- und in die Analyse vorwärts-verkettet.

## Akzeptanzkriterien

- [ ] Die Phase ist als Ausführen von Fällen und Ausgeben roher Ergebnisse definiert (nicht als deren Interpretation), referenziert `quality-gate` als Fast-Tier-Ausführer und überlässt Determinismus/Platzierung dem Stufen-Fundament
- [ ] Inputs (Fälle mit TC-IDs/Stufen) und Outputs (strukturiertes Per-Fall-Ergebnis: Pass/Fail/Error/Skip + Meldung/Trace + Timing + Coverage + E2E-Artefakte) entsprechen dem Phase-2-Vertrag des Fundaments, mit TAP/JUnit als illustrativ benannt
- [ ] Deterministische + hermetische Ausführung ist gefordert, mit Uhr-Wrapping, Zufall-/Netzwerk-Kontrolle und geteilter-Zustand-Isolation, zitiert auf Fowler/Bazel
- [ ] Isolation + randomisierte Reihenfolge ist gefordert, und nackte Sleeps sind zugunsten von Readiness-Bedingungs-Waits verboten (inkl. ephemerer Deps), ohne geteilte veränderliche Umgebung
- [ ] Parallelisierung/Sharding ist gefordert (SOLLTE); Testauswahl ist erlaubt (DARF) nur, wenn die volle Suite weiterhin nach Zeitplan läuft; reproduzierbar-Build-Caching ist referenziert
- [ ] Die gestufte CI-Ausführung gatet die schnellen Stufen am PR und führt langsame/breite Stufen in einer dedizierten Stufe/Nightly aus, mit einer Schnelle-PR-Stufe + Fail-fast-Leitlinie
- [ ] Retry-bis-Grün ist verboten; das gebundene Flip-Signal-Retry ist nur Erkennung bei festem N = 2 zusätzlichen unabhängigen Läufen, gibt den Ergebnisvektor je Lauf plus ein `flip-observed`-Signal aus und nie ein `flaky`/`real`-Etikett; bekannte Flakes werden unter Quarantäne gestellt und verfolgt
- [ ] Reproduzierbarkeit via Pinning + festgehaltenem Befehl/Umgebung ist gefordert
- [ ] Jedes Ergebnis ist für Traceability an eine TC-ID geknüpft
- [ ] Die Grenze gegen `quality-gate` (Single-Invocation-Gate), `workflow-health` (Rote-CI-Triage = Phase 3) und die Phasen 1/3/4 ist explizit
- [ ] Die EN- und DE-Versionen sind strukturell identisch (gleiche Überschriften, Anforderungszahl, Akzeptanzkriterien-Zahl) und der Spec-Index listet den neuen Slug

## Referenzen

- [R1] `spec/project/test-cycle-foundation/` — der Zyklus und der Inter-Phasen-Vertrag dieser Phase
- [R2] `spec/project/quality-gate/` — das Single-Invocation-Gate (Lint + Typecheck + Test) und die Ausgabetabelle, die diese Phase referenziert
- [R3] `spec/project/test-pyramid-foundation/` — die Determinismus-Regel und die Per-Stufe-Ausführungs-Platzierung / das CI-Gating-Modell
- [R4] `spec/project/workflow-health/` — Rote-CI-Triage (aus Phase 3 aufgerufen, nicht dieser Phase)
- [R5] Martin Fowler, *Eradicating Non-Determinism in Tests* (flaky Tests; Uhr-Wrapping; Doubles; keine nackten Sleeps; Quarantäne) — <https://martinfowler.com/articles/nonDeterminism.html>
- [R6] Google Testing Blog, *Flaky Tests at Google and How We Mitigate Them* — <https://testing.googleblog.com/2016/05/flaky-tests-at-google-and-how-we.html>
- [R7] Meta Engineering, *Predictive Test Selection* (betroffene Tests ausführen, Regressions-Signal bewahren) — <https://engineering.fb.com/developer-tools/predictive-test-selection/>
- [R8] Playwright, *Test sharding* (parallele Ausführung über Worker) — <https://playwright.dev/docs/test-sharding>
- [R9] Bazel, *Hermeticity* / *Remote caching* (hermetische, reproduzierbare Ausführung ermöglicht sicheres Caching) — <https://bazel.build/basics/hermeticity>
- [R10] Martin Fowler, *Continuous Integration* (gestufter Build, ~10-Minuten-Commit-Build) — <https://martinfowler.com/articles/continuousIntegration.html>
- [R11] GitLab, *Fail-fast testing* (die relevantesten Specs zuerst ausführen) — <https://docs.gitlab.com/ci/testing/fail_fast_testing/>
- [R12] Atlassian, *Taming test flakiness* (Erkennen + Quarantäne, nicht Retry-bis-Grün) — <https://www.atlassian.com/blog/atlassian-engineering/taming-test-flakiness-how-we-built-a-scalable-tool-to-detect-and-manage-flaky-tests>
- [R13] *Test Anything Protocol (TAP)* / JUnit XML (strukturierte maschinenlesbare Ergebnisse) — <https://testanything.org/tap-version-14-specification.html>
- [R14] Testcontainers, *Startup and wait strategies* (Readiness-basierte Waits für ephemere Abhängigkeiten) — <https://java.testcontainers.org/features/startup_and_waits/>

## Offene Fragen

- Sollte das Portfolio ein konkretes Zeit-Budget für die PR-gatende Stufe setzen (zum Beispiel die ~10-Minuten-Leitlinie) als Anforderung, oder es beratend und projektspezifisch lassen?
- Sollte Test Impact Analysis / Predictive Selection für große Suites von DARF auf SOLLTE angehoben werden, angesichts der bewiesenen Kostenersparnis — und welche Kadenz ist für den Voll-Suite-Sicherheitslauf gefordert?
- ~~Wird das gebundene Flip-Signal-Retry besser hier besessen (Ausführung gibt ein `flaky`-Flag aus) oder in Phase 3 (Analyse entscheidet Flake vs. echt) — wo genau lebt die Flake-*Klassifikation* versus die Flake-*Erkennung*?~~ **Entschieden (2026-07-24): Erkennung hier, Klassifikation in Phase 3.** Die Ausführung läuft das gebundene Retry bei festem N = 2 zusätzlichen unabhängigen Läufen und gibt den Ergebnisvektor je Lauf plus `flip-observed` aus; sie gibt nie ein `flaky`-Etikett aus. `spec/project/test-cycle-result-analysis/` konsumiert diesen Vektor zusammen mit der laufübergreifenden Historie und vergibt die Klasse. Die Trennung legt das Urteil „echt bis zum Beweis des Gegenteils" in genau die Phase, deren ganze Aufgabe Klassifikation ist, und verweigert der erneut ausführenden Komponente jede Befugnis, ihr eigenes Rot wegzuerklären—genau der Fehlermodus, der aus einem gebundenen Retry ein Retry-bis-Grün macht.
