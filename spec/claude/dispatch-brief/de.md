# Dispatch-Briefing

Status: draft
Portfolio-Scope: portfolio

## Context

Wenn ein Skill Analyse oder Remediation an einen Spezialisten dispatcht, komponiert es ein **Dispatch-Briefing**: die Problemstellung, den Scope und oft eine *Hypothese* darüber, was falsch ist, warum, oder wie es zu beheben ist. Ein Briefing mit Hypothese trägt die beste Vermutung des Orchestrators, während der Spezialist den Code, das Artefakt oder die Evidenz vor sich hat. Ist die Vermutung falsch und das Briefing sagt es nicht, optimiert der Spezialist darauf, die gestellte Aufgabe zu erledigen — was das korrekte Default-Verhalten ist. Eine falsche Hypothese wird so stillschweigend zu einem falschen Fix, den ein späterer Lauf neu diagnostizieren muss.

Eine vollständige E2E-Stabilisierungskampagne (`nolte/kamerplanter#768`) machte die Kosten konkret: dispatchte Spezialisten korrigierten das Briefing des Orchestrators rund zehnmal, und die Korrekturen waren substanziell statt kosmetisch. Eine benannte Grundursache, die für die installierte Bibliotheksversion nicht hielt. Eine „gib X dieselben Constraints wie Y"-Anweisung, die ein No-op war, weil auch Y keine solchen Constraints hatte. Ein `minWidth: 0`-Fix, der den Defekt, den er heilen sollte, wieder eingeführt hätte. Jede Korrektur kam aus einem expliziten Satz im Dispatch: *wenn die Evidenz dem widerspricht, sag es und ändere nichts, statt den Fix passend zu erzwingen.*

Diese Regel lebte zuerst in `spec/project/e2e-failure-diagnosis/` §E, ist aber nicht E2E-spezifisch. Sie gilt für jedes Skill, das Analyse oder Remediation mit einer benannten Hypothese dispatcht: `issue-orchestrate`, `workflow-health-triage`, `source-code-review`, `dependency-audit`, `observability-audit`, die Test-Tier-Reviewer und die Security-Reviewer. `spec/claude/` besitzt bereits die übergreifenden Agent- und Skill-Konventionen (`agent-management`, `skill-management`, `skill-vs-agent`); eine Briefing-Kompositions-Konvention gehört ebenfalls hierher. Diese Spec besitzt die Refutations-Regel portfolio-weit, sodass Domänen-Specs und dispatchende Skills sie referenzieren, statt sie jeweils erneut auszuformulieren.

## Goals

- Refutations-Autorisierung zu einer **routinemäßigen, prüfbaren Eigenschaft** jedes hypothesentragenden Dispatch-Briefings machen, statt zu einer Gewohnheit, an die der Orchestrator sich erinnern muss.
- Die **Form einer gültigen Refutation** festlegen, damit eine Refutation handlungsleitend ist und kein bloßes „Ich widerspreche".
- Der Regel einen **stabilen, zitierbaren Home** geben, auf den Domänen-Specs (`e2e-failure-diagnosis`) und dispatchende Skills zeigen, statt sie zu duplizieren.

## Non-Goals

- Den übrigen Inhalt eines Dispatch-Briefings regeln (Problemstellung, Scope, Akzeptanzkriterien); diese Spec regelt nur die Refutations-Klausel und ihre Deliverable-Form.
- Die Skill-versus-Agent-Format-Wahl für eine Capability; die bleibt bei `spec/claude/skill-vs-agent/`.
- Die eigene Routing- und Dispatch-Mechanik der Claude-Code-Runtime; diese Spec regelt, wie ein Briefing komponiert wird, nicht wie die Runtime es zustellt.
- Den **selbstgerichteten** Fall, in dem Analyst und Handelnder derselbe Agent sind, sodass kein Briefing geschrieben wird und nichts irgendetwas autorisiert. Die Regel hier braucht zwei Parteien; die Herkunft, die eine Behauptung ihrem Leser unabhängig von Delegation schuldet, besitzt `spec/claude/claim-provenance/`. Ein Briefing ist selbst ein Artefakt nach jener Spec, also gelten beide für eines: diese Spec regelt, was das Briefing dem Spezialisten schuldet, die andere, was es seinem Leser schuldet.

## Requirements

- Ein **hypothesentragendes Briefing** ist ein Dispatch-Briefing, das eine *Ursache*, einen *Mechanismus* oder eine *Remediations-Form* behauptet: jede Behauptung, die der empfangende Spezialist gegen die Evidenz vor sich bestätigen oder widerlegen könnte. Ein Briefing, das nur eine Erkennungsaufgabe scoped („scanne diese Oberfläche und berichte Befunde") ohne Ursache oder Fix zu behaupten, ist **nicht** hypothesentragend.
- Ein hypothesentragendes Briefing **MUST** [MUST] seine Hypothese benennen *und* den Spezialisten explizit autorisieren und erwarten, sie zu widerlegen. Die Autorisierung **MUST** [MUST] im Briefing explizit sein, nicht implizit bleiben; die kanonische Form lautet: *wenn die Evidenz dem widerspricht, sag es und ändere nichts, statt den Fix passend zu erzwingen.*
- Das Briefing **MUST** [MUST] eine Refutation als **gültiges, erwartetes Deliverable** rahmen, nicht als Scheitern beim Erledigen der Aufgabe. Ein Spezialist, der eine Refutation mit ihrer Evidenz zurückgibt, hat seinen Dispatch erfüllt.
- Eine Refutation **MUST** [MUST] beides enthalten:
  1. **Die Evidenz, die dem Briefing widerspricht** — einen konkreten Anker, den ein Reviewer prüfen kann: eine `file:line`, oder ein Kommando und die Ausgabe, die es entscheidet. Ein bloßes „Ich widerspreche" oder eine unverankerte Behauptung ist nicht konform.
  2. **Was der Spezialist stattdessen tat** — genau eines von: nichts geändert, einen engeren Fix angewandt (nur den Teil mit echter Lücke) oder einen anderen Fix angewandt. Der Spezialist **MUST NOT** [MUST NOT] Bounds, Constraints oder Scope erfinden, die die Evidenz nicht stützt, nur um das Briefing zu erfüllen.
- Der Orchestrator **MUST** [MUST] eine zurückgegebene Refutation als erstklassiges Ergebnis behandeln: sie im Audit-Trail des Laufs festhalten und die Hypothese gegen sie abgleichen, bevor abhängige Arbeit dispatcht wird. Er **MUST NOT** [MUST NOT] eine Refutation stillschweigend verwerfen, um die ursprüngliche Hypothese zu bewahren.
- Ein hypothesentragendes Briefing, das die Refutations-Autorisierung weglässt, **ist ein Defekt** — ein Reviewer kann ein Briefing gegen diese Regel prüfen, indem er fragt, ob es eine Ursache, einen Mechanismus oder eine Remediation behauptet, und falls ja, ob es Refutation in der obigen Deliverable-Form autorisiert.
- Ein nicht hypothesentragendes Briefing (reine Erkennung oder Scoping) **MAY** [MAY] die Klausel tragen, muss es aber nicht; die Regel bindet dort, wo eine Behauptung existiert, die widerlegt werden kann.
- Eine Domänen- oder scope-spezifische Spec, die diese Regel braucht, **MUST** [MUST] diese Spec referenzieren, statt den Regeltext neu auszuformulieren, und **MAY** [MAY] nur ihre scope-spezifische Anwendung ergänzen (etwa welche Evidenzkanäle ein Briefing tragen muss).

## Acceptance Criteria

- [ ] Die Regel lebt in dieser übergreifenden Spec unter `spec/claude/`, nicht in einer Domänen-Spec.
- [ ] „Hypothesentragendes Briefing" ist so definiert, dass ein Reviewer entscheiden kann, ob ein gegebenes Briefing im Scope ist.
- [ ] Die Refutations-Autorisierung ist als `MUST` formuliert, das ein Reviewer gegen ein tatsächliches Briefing prüfen kann.
- [ ] Die Form einer gültigen Refutation ist spezifiziert: widersprechende Evidenz (eine `file:line` oder ein Kommando mit Ausgabe) **und** was stattdessen getan wurde (nichts, ein engerer Fix oder ein anderer Fix).
- [ ] Das Rahmen einer Refutation als erwartetes Deliverable (nicht als Aufgaben-Scheitern) ist gefordert.
- [ ] Die Pflicht des Orchestrators, eine Refutation festzuhalten und abzugleichen, ist benannt.
- [ ] `e2e-failure-diagnosis` referenziert diese Spec, statt eine eigene Kopie der Regel zu tragen.
- [ ] Die dispatchenden Skills, die Hypothesen benennen, referenzieren diese Spec.

## References

- [R1] Die E2E-scoped Anwendung, aus der diese Regel gehoben wurde und die nun hierher referenziert: `spec/project/e2e-failure-diagnosis/` §E und §Einbindung in Agents und Skills.
- [R2] Der volumenstärkste hypothesentragende Dispatcher, dessen Pre-Analysis-Briefing pro Arbeitspaket eine Dekompositions-Hypothese trägt: `spec/project/issue-orchestration/`.
- [R3] Konfliktbehandlung, wenn unabhängige Kanäle widersprechen (komponieren, nicht abstimmen; stop-and-surface): `spec/claude/research-triangulate/`.
- [R4] Das Skill-orchestriert-Agent-führt-aus-Muster, dessen Dispatch-Schritt diese Regel regelt: `spec/claude/skill-vs-agent/`.
- [R5] Die Agent-Authoring-Konventionen, neben denen diese Briefing-Konvention steht: `spec/claude/agent-management/`.
- [R6] Der Quell-Arbeitsauftrag und die Kampagnen-Evidenz: Issue #528, abgeleitet aus `nolte/kamerplanter#768` (hier als #514 eingereicht).
- [R7] Das selbstgerichtete Gegenstück, an das §Non-Goals dieser Spec übergibt: `spec/claude/claim-provenance/`.

## Open Questions

- Nichts Tragendes. Die genaue Menge dispatchender Skills, die Hypothesen behaupten, wird an den Skills gepflegt, die diese Spec referenzieren, nicht hier eingefroren; ein neuer hypothesentragender Dispatcher erbt die Regel per Definition.
