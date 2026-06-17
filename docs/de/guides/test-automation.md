---
title: Testautomatisierung
audience: [maintainer]
content_mode: explanation
track: developer-docs
last_updated: 2026-06-13
---

# Testautomatisierung

Das Plugin liefert eine zusammenhängende Familie von Testautomatisierungs-Capabilities: eine Reihe von Specs, die die Disziplin definieren, und eine Schicht aus Skills und Agents, die Tests gegen diese Specs entwickeln, ausführen, analysieren und auditieren. Dieser Guide ist die Landkarte. Er erklärt, wie die Teile zusammenspielen und wann man welches einsetzt; die Referenz je Artefakt liegt im auto-generierten Katalog der [Skills](../skills/index.md) und [Agents](../agents/index.md).

## Zwei Achsen

Testautomatisierung ist hier entlang zweier orthogonaler Achsen organisiert. Sie getrennt zu halten ist das, was die Familie kohärent hält.

- **Die Pyramide — _was_ auf welcher Ebene getestet wird.** Eine geschlossene, geordnete Stufen-Taxonomie (statische Analyse → Unit → Component → Integration → Contract → End-to-End), die der `test-pyramid-foundation`-Spec gehört. Jede Stufe hat ihre eigene Spec und ein Generator/Reviewer-Agent-Paar.
- **Der Zyklus — _wie_ man einen Test entwickelt.** Ein iterativer Ermitteln → Ausführen → Analysieren → Anpassen-Loop (ein verallgemeinertes Red-Green-Refactor), der der `test-cycle-foundation`-Spec gehört und vom `test-cycle-orchestrate`-Skill getrieben wird.

Ein konkreter Test lebt auf einer Stufe (Pyramiden-Achse) und entsteht durch den Zyklus (Prozess-Achse). Die Querschnitts-Capabilities — das Gate ausführen und die Stufen-Vollständigkeit auditieren — liegen quer über beiden.

## Die Pyramide: was auf welcher Stufe getestet wird

Die Stufen-Taxonomie ist geschlossen und geordnet. Jede funktionale Stufe (unterhalb der statischen Analyse) hat einen Generator-Agent, der spec-konforme Tests scaffoldet, und einen Reviewer-Agent, der bestehende gegen die Stufen-Spec auditiert.

| Stufe | Generator-Agent | Reviewer-Agent | Stufen-Spec |
|-------|-----------------|----------------|-------------|
| Statische Analyse | _(Lint + Typecheck über das Gate, kein Test-Agent)_ | — | `test-tier-static-analysis` |
| Unit | `unit-test-generator` | `unit-test-reviewer` | `test-tier-unit` |
| Component | `component-test-generator` | `component-test-reviewer` | `test-tier-component` |
| Integration | `integration-test-generator` | `integration-test-reviewer` | `test-tier-integration` |
| Contract | `contract-test-generator` | `contract-test-reviewer` | `test-tier-contract` |
| End-to-End | `e2e-test-generator` | `e2e-test-reviewer` | `e2e-test-automation` |

Die End-to-End-Stufe ergänzt `e2e-result-reviewer`, der Screenshots und Protokoll eines Laufs visuell gegen die Anforderungs- und UI-Specs prüft — eine Prüfung, die die anderen Stufen nicht brauchen.

Um zu prüfen, ob ein Feature die Stufen, die es abdecken sollte, tatsächlich abdeckt, dient der **`test-pyramid-check`**-Skill: Er auditiert die Stufen-Vollständigkeit eines Features gegen die `test-pyramid-foundation`-Taxonomie und legt Lücken sowie das Ice-Cream-Cone-Anti-Pattern offen.

## Der Zyklus: wie man einen Test entwickelt

Der `test-cycle-orchestrate`-Skill treibt den iterativen Loop. Jede Phase hat eine realisierende Spec und, wo die Arbeit spezialisiert ist, einen Agent. Der Loop kehrt von Phase 4 zu Phase 2 zurück (erneut ausführen) und speist Phase 3 in Phase 1 zurück (ein entdeckter Defekt wird ein neuer Regressionsfall); er endet nur bei einer expliziten Abbruchbedingung, nie durch das Abschwächen eines Tests, um einen Pass zu erzwingen.

| Phase | Capability | Phasen-Spec |
|-------|------------|-------------|
| 1 — Ermitteln (rot) | `test-case-extractor`-Agent (leitet rückverfolgbare, framework-agnostische Fälle aus einer Anforderung ab) | `test-cycle-case-determination`, `test-case-derivation` |
| 2 — Ausführen | `quality-gate`-Skill (führt das Gate aus) | `test-cycle-execution`, `quality-gate` |
| 3 — Analysieren | `test-result-analyzer`-Agent (klassifiziert Ergebnisse in Defekt / Flake / Test-Bug / Infra) | `test-cycle-result-analysis` |
| 4 — Anpassen (grün) | `test-code-adapter`-Agent (minimale korrekte Produktivänderung unter der No-Cheating-Regel) | `test-cycle-code-adaptation` |

## Ausführen und auditieren

Zwei Querschnitts-Capabilities gelten auf jeder Stufe:

- **`quality-gate`** (Skill) führt das Lint- + Typecheck- + Test-Gate des Projekts parallel aus und tabelliert, welche Prüfungen fehlschlugen. Es ist Phase 2 des Zyklus und die ausführbare Form der statischen-Analyse-Stufe.
- **`quality-gate-enforcer`** (Agent) prüft die _Verdrahtung_ des Gates — die Taskfile-Targets, die pre-commit-Konfiguration, den CI-Workflow und die Timeouts — auf Spec-Konformität, statt das Gate selbst auszuführen.

## End-to-End: alles zusammen

Ein typischer Durchlauf für ein neues Feature:

1. **Fälle ableiten** aus der Anforderung mit `test-case-extractor` (Phase 1), dann mit der Pyramiden-Taxonomie entscheiden, zu welcher Stufe jeder Fall gehört.
2. **Scaffolden** der Tests je Stufe mit dem passenden `*-test-generator`-Agent, und den `*-test-reviewer`-Agent sie auditieren lassen.
3. **Ausführen** der Suite über den `quality-gate`-Skill (Phase 2).
4. **Analysieren** der Fehlschläge mit `test-result-analyzer` — und, für E2E-Läufe, `e2e-result-reviewer` (Phase 3).
5. **Anpassen** des Produktivcodes mit `test-code-adapter` unter der No-Cheating-Regel, dann erneut ausführen (Phase 4 → Phase 2).
6. **Vollständigkeit auditieren** mit `test-pyramid-check`, bevor das Feature als fertig gilt.

`test-cycle-orchestrate` verbindet die Phasen 1–4 zum iterativen Loop, sodass die obigen Schritte als ein disziplinierter Zyklus statt ad hoc laufen.

## Referenz

- Seiten je Skill: [Skills-Katalog](../skills/index.md) — `quality-gate`, `test-pyramid-check`, `test-cycle-orchestrate`.
- Seiten je Agent: [Agents-Katalog](../agents/index.md) — die Stufen-Generator/Reviewer-Paare und die Zyklus-Agents.
- Die maßgeblichen Specs liegen unter `spec/project/` (`test-pyramid-foundation`, `test-cycle-foundation`, die Specs je Stufe und je Phase).
