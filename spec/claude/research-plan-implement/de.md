# Research-Plan-Implement-Disziplin

Status: draft
Portfolio-Scope: portfolio

## Context

Jedes Skill und jeder Agent in diesem Monorepo, das etwas verändert, tut dieselben drei Dinge in irgendeiner Reihenfolge: es baut ein Verständnis der Oberfläche auf, die es gleich anfasst, es entscheidet, was zu ändern ist, und es schreibt. Heute erfindet jede Capability diese Sequenz für sich selbst. `issue-orchestrate` dekomponiert vor dem Dispatch, `sprint-execute` führt Zustandsübergänge direkt aus, die Reviewer-Agents lesen ohne zu schreiben, und `spec` interviewt vor dem Autorenschritt. Die Formen ähneln sich, aber nichts benennt sie, also kann nichts sie prüfen. Ein Skill, das im ersten Zug schreibt, ist weder zur Autorenzeit noch im Review von einem unterscheidbar, das zuerst gelesen hat.

Die Branche hat sich auf einen Namen für diese Sequenz geeinigt. Anthropics Claude-Code-Leitfaden rahmt sie als explore, plan, implement, commit, mit einem read-only Plan-Mode, der die Grenze durchsetzt. HumanLayers Context-Engineering-Arbeit benennt dieselben drei Phasen und ergänzt den Grund, warum ihre Trennung sich lohnt: die Kosten eines Fehlers skalieren mit der Phase, in der er passiert, denn eine falsche Recherche-Zeile lenkt einen ganzen Plan fehl, und eine falsche Plan-Zeile erzeugt hunderte falsche Code-Zeilen. Diese Asymmetrie macht den Plan — nicht den Diff — zum günstigen Ort, an dem ein Fehler auffällt. `AgentPatterns` katalogisiert das Muster mit einer Tabelle nach Aufgaben-Komplexität und einem expliziten Re-Plan-Gate. LangChain hat den Nutzen von der anderen Seite gemessen: Reasoning-Aufwand auf Planung und Verifikation zu konzentrieren und ihn während der Implementierung zu senken, hob eine Coding-Harness von 52,8 % auf 66,5 % auf Terminal Bench 2.0 — ohne Modellwechsel.

Derselbe Erfahrungsbestand trägt eine Warnung, die genauso wichtig ist wie das Muster. Feldstudien zu Spec-Driven Development berichten den Fehlermodus, volle Zeremonie auf einen Bugfix anzuwenden: 1.300 Zeilen generiertes Markdown für ein Datums-Anzeige-Feature, Reviewer, die Markdown-Stapel ermüdender finden als den Code, den sie ersetzen, ein Team, das Spezifikation bei 50 % der Gesamtprojektzeit maß, bevor es den Prozess zurückfuhr. Die Weiterentwicklung des Musters zu QRSPI entstand aus drei beobachteten Fehlern einer naiven Lesart: ein ungescopetes Recherche-Prompt, das rund 40 % des Kontextfensters allein für Orientierung verbrauchte, Recherche-Zusammenfassungen, die zu unzuverlässig für ihre Kosten waren, und Agents, die Plan-Schritte still übersprangen, ohne den Operator zu informieren. Eine Disziplin, die nur sagt „immer recherchieren, immer planen", reproduziert genau diese Fehler.

Diese Spec fixiert beide Hälften: den Phasen-Vertrag, dem schreibende Capabilities folgen, und die Regel, dass die Phasentiefe mit dem Blast Radius skaliert, damit ein Einzeiler keine Planungssteuer zahlt. Sie ist das Fundament, auf das `skill-management`, `agent-management` und `skill-vs-agent` sich beziehen, wenn sie den Workflow einer Capability formen.

**Leser:** Skill- und Agent-Autoren in diesem Plugin-Monorepo, Reviewer, die `skill-review` und `agent-review` ausführen, und die Claude-Code-Runtime, die diese Capabilities im Auftrag eines Operators ausführt.

## Goals

- Den drei Phasen stabile Namen und eine prüfbare Read-only-gegen-Schreib-Grenze geben, sodass ein Reviewer am Text eines Skills selbst erkennt, zu welcher Phase jeder Schritt gehört.
- Die Phasentiefe am Blast Radius skalieren, damit triviale Änderungen günstig und übergreifende prüfbar bleiben.
- Den Plan — nicht den Diff — zur Oberfläche machen, die ein Mensch reviewt, und diese Oberfläche konkret genug für ein Review machen.
- Explorations-Rauschen aus dem implementierenden Kontext heraushalten, ohne dass die verdichtete Zusammenfassung zu einer Behauptung wird, die niemand auditieren kann.
- Replanning zu einem expliziten, benannten Übergang machen statt zu stillem Drift während der Ausführung.
- `skill-management`, `agent-management` und `skill-vs-agent` eine einzige Spec zum Zitieren für die Workflow-Form geben, statt sie jeweils erneut auszuformulieren.

## Non-Goals

- Zu entscheiden, **was** zu bauen ist. Die Erfassung der Absicht besitzt `spec/project/requirements-elicitation/`; diese Disziplin beginnt, sobald die Absicht feststeht, und fragt, wie sie auszuführen ist.
- `spec/project/spec-driven-development/` zu ersetzen. Jene Spec macht die geschriebene Spezifikation zur Autorität für eine Änderung; diese regelt, wie eine Capability ihre Arbeit unter dieser Autorität sequenziert.
- `spec/project/elicitation-implementation-separation/` zu ersetzen. Jene Spec regelt einen Repository-weiten Arbeitsmodus, in dem Requirements als eigener Pull Request landen; diese regelt die Phasensequenz innerhalb eines einzelnen Arbeitspakets, gleich welcher Modus es erzeugt hat.
- Zu regeln, wie viele unabhängige Quellen eine repo-externe Behauptung braucht — das besitzt `spec/claude/research-triangulate/` — oder was eine Behauptung ihrem Leser schuldet, was `spec/claude/claim-provenance/` besitzt.
- Das Review-**Befunds**-Artefakt zu definieren, das `spec/claude/review-plan/` besitzt. Ein Review-Plan hält fest, was ein Reviewer gefunden hat; ein Implementierungsplan hält fest, was ein Implementierer vorhat. Das sind verschiedene Artefakte mit verschiedenen Lebenszyklen.
- Zwischen Skill- und Agent-Format für eine Capability zu wählen; das bleibt bei `spec/claude/skill-vs-agent/`.
- Token-Zahlen, Kontext-Auslastungs-Prozente oder Reasoning-Effort-Stufen als normative Schwellen vorzuschreiben. Die Messwerte in §Context sind Evidenz für die Form der Regeln, nicht Grenzwerte, die diese Spec durchsetzt.

## Requirements

### Phasendefinitionen und die Schreibgrenze

- Die Disziplin benennt genau drei Phasen. **Research** baut ein Verständnis der betroffenen Oberfläche auf und hält es fest. **Plan** überführt dieses Verständnis in eine entschiedene, reviewbare Änderungsbeschreibung. **Implement** führt den Plan aus und weist ihn nach.
- Eine Capability, die Research oder Plan ausführt, **MUST NOT** [MUST NOT] die Änderung selbst schreiben. Das Schreiben des phaseneigenen Artefakts auf den Pfad, den seine zuständige Spec zuweist (`.resume/<slug>/` gemäß `spec/claude/resumable-work/`, `.audits/<review-type>/` gemäß `spec/claude/review-plan/` oder ein Scratch-Verzeichnis), ist erlaubt — **auch dort, wo dieser Pfad versioniert ist**: `spec/claude/review-plan/` verlangt, dass `.audits/` in git eingecheckt bleibt, und `spec/project/issue-orchestration/` verlangt, dass sein Pre-Analysis-Artefakt committet statt ignoriert wird; diese Regel hebt keines von beiden auf. Die Grenze verläuft zwischen Artefakt und Änderung, nicht zwischen versioniert und unversioniert.
- Research **MUST** [MUST] ein **Findings-Artefakt** erzeugen und Plan **MUST** [MUST] ein **Plan-Artefakt** erzeugen, wann immer die Phase überhaupt läuft. Das Artefakt ist entweder eine Datei oder — für eine Capability ohne Schreib-Tools — der strukturierte Report, den sie an die dispatchende Capability zurückgibt, die dann für seine Persistierung zuständig ist. Eine Phase, die weder das eine noch das andere erzeugt, ist nicht gelaufen, sondern erzählt worden.
- Das **Schreib-Gate** ist der erste Schreibvorgang der Capability auf versionierten Zustand, der Teil der Änderung ist. Wo eine Plan-Phase läuft, ist das Gate der Übergang von Plan zu Implement; auf Stufe 0, wo keine Plan-Phase läuft, ist es der Beginn von Implement. Jede Stufe hat ein Schreib-Gate.

### Die Phasentiefe skaliert mit dem Blast Radius

- Jede schreibende Capability **MUST** [MUST] die vorliegende Arbeit in eine von vier Stufen klassifizieren und **MUST** [MUST] genau die Phasen ausführen, die diese Stufe verlangt:

  | Stufe | Arbeitsform | Phasen |
  |---|---|---|
  | 0 | Der Diff ist in einem Satz beschreibbar, betrifft eine Datei und ist trivial rückgängig zu machen | Implement |
  | 1 | Grundursache oder Ziel sind bereits bekannt, die Oberfläche ist vertraut, keine veröffentlichte Schnittstelle ändert sich | Plan, Implement |
  | 2 | Mehrere Dateien, eine unvertraute Oberfläche oder eine neue Capability | Research, Plan, Implement |
  | 3 | Repository-übergreifend, eine Migration oder eine Änderung an einem veröffentlichten Vertrag | Research, Plan, Implement, zusätzlich das Design-Gate und der Verifikationsdurchlauf unten |

- Trifft eine Änderung auf mehr als eine Zeile der Stufentabelle zu, gewinnt die **höchste** zutreffende Stufe. Eine Einzeilenänderung an einem veröffentlichten Vertrag ist Stufe 3, nicht Stufe 0, weil die Zeile „veröffentlichter Vertrag" die Zeile „Diff in einem Satz" überstimmt.
- Eine Capability **MUST NOT** [MUST NOT] eine höhere Stufe erzwingen, als die Arbeit verlangt. Stufe-2-Zeremonie auf eine Stufe-0-Änderung anzuwenden ist ein Defekt der Capability, keine Sorgfalt: der gemessene Fehlermodus ist Markdown-Volumen, das Reviewer überfliegen und Agents ignorieren.
- Eine Capability **MUST NOT** [MUST NOT] **still** unter die Stufe fallen, die die Arbeit verlangt. Herunterklassifizieren (etwa eine Mehrdatei-Änderung als Stufe 1) ist nur dokumentiert zulässig: die Capability **MUST** [MUST] Klassifikation und Begründung in dem Artefakt festhalten, das die gewählte Stufe erzeugt, oder — wo die gewählte Stufe kein Artefakt erzeugt — im Pull-Request-Body der resultierenden Änderung. Ein undokumentiertes Herunterklassifizieren ist der Defekt, den diese Regel benennt.
- Auf Stufe 3 **MUST** [MUST] die Capability zusätzlich: die Design-Frage (**wohin** die Änderung geht) als explizite, operatorseitige Entscheidung klären, bevor der Plan beschreibt, **wie** sie dorthin kommt, und nach der Implementierung einen Verifikationsdurchlauf gegen den Plan ausführen, durchgeführt von einem Kontext, der die Änderung nicht erzeugt hat.

### Der Plan ist die Review-Oberfläche

- Ein Plan-Artefakt **MUST** [MUST] für jeden Schritt benennen: die exakten Dateien, die er anfasst, die Änderung, die er an jeder vornimmt, und die Prüfung, die diesen Schritt nachweist. Ein Plan, der Absicht beschreibt, ohne Dateien zu benennen, ist gegen den Diff, den er erzeugen wird, nicht reviewbar.
- Ein Plan-Artefakt **MUST** [MUST] für sich allein lesbar sein, ohne das Gespräch, das es erzeugt hat.
- Ein Plan-Artefakt **MUST** [MUST] benennen, was für diese Änderung außerhalb des Scopes liegt.
- Auf Stufe 2 und Stufe 3 **MUST** [MUST] ein Operator-Freigabe-Gate zwischen Plan und Implement liegen. Die Capability **MUST NOT** [MUST NOT] das Schreib-Gate auf einem nicht freigegebenen Plan überschreiten.
- Auf Stufe 3 **MUST** [MUST] die Capability den Plan in unabhängig verifizierbare Scheiben zerlegen, sodass Verifikation an Scheibengrenzen stattfindet statt nur am Ende.

### Research ist isoliert und verankert

- Research **SHOULD** [SHOULD] in einem isolierten Kontext laufen (ein Subagent, ein dispatchter Reviewer-Agent oder eine separate Session) und eine verdichtete Zusammenfassung statt seines Explorations-Transkripts zurückgeben, damit der implementierende Kontext nicht für die Suche zahlt.
- Ein Findings-Artefakt **MUST** [MUST] für jede tragende Behauptung über das Repository einen auflösbaren Anker führen: eine `file:line`, einen Pfad oder ein Kommando mit der Ausgabe, die es entscheidet. Eine ankerlose Zusammenfassung ist genau der Fehlermodus „veraltete, nicht auditierbare Recherche", für den das Muster bekannt ist, und sie verwandelt einen Recherche-Fehler in einen stillen Plan-Fehler.
- Ein Findings-Artefakt **MUST** [MUST] die Frage benennen, auf die es gescopet war. Ungescopete Untersuchung ist der dokumentierte Weg, auf dem eine Recherche-Phase das Budget verbraucht, das die Implementierung gebraucht hätte.
- Behauptungen in einem Findings-Artefakt über alles außerhalb der Arbeitskopie unterliegen weiterhin `spec/claude/research-triangulate/`; diese Spec ergänzt die Anker-Pflicht, sie lockert die Quellenzahl-Pflicht nicht.
- Eine Capability, die Research an einen Spezialisten dispatcht und dabei eine vermutete Ursache benennt, **MUST** [MUST] den Dispatch gemäß `spec/claude/dispatch-brief/` komponieren, einschließlich der Refutations-Klausel.

### Verifikation gehört in den Plan

- Jeder Plan-Schritt **MUST** [MUST] eine Prüfung tragen, die ein Signal zurückgibt, das die ausführende Capability lesen kann: ein Test, ein Build-Exit-Code, ein Linter, ein Diff gegen eine Fixture oder ein vergleichbares Artefakt. Ein Schritt, dessen einziges Abschluss-Signal das eigene Urteil der Capability ist, dass es fertig aussieht, ist ein unvollständiger Plan-Schritt.
- Die Implement-Phase **MUST** [MUST] die deklarierte Prüfung jedes Schritts ausführen und **MUST** [MUST] die tatsächliche Ausgabe der Prüfung berichten, nicht die Behauptung, sie sei bestanden.
- Auf Stufe 3 **MUST** [MUST] der Verifikationsdurchlauf von einem Kontext durchgeführt werden, der die Änderung nicht erzeugt hat, und **MUST** [MUST] auf Korrektheit gegen die benannten Anforderungen des Plans gescopet sein statt auf Stilpräferenz. Ein ungescopeter adversarialer Reviewer liefert zuverlässig Befunde, ob die Arbeit solide ist oder nicht, und alle davon zu bearbeiten erzeugt Over-Engineering.

### Replanning ist explizit

- Wenn die Implementierung Informationen zutage fördert, die dem Plan widersprechen, **MUST** [MUST] die Capability anhalten, die gescheiterte Annahme benennen und zu Plan zurückkehren (oder zu Research, wenn die gescheiterte Annahme ein Recherche-Befund ist). Sie **MUST NOT** [MUST NOT] still anpassen und weitermachen.
- Die Capability **MUST** [MUST] eine **lokale Anpassung** — ein Schritt weicht im Detail ab, die Struktur des Plans hält, und die Abweichung wird im Plan-Artefakt festgehalten — von einer **strukturellen Rückkehr** unterscheiden, bei der eine Entscheidung, auf der der Plan ruht, falsch ist und die Phase erneut laufen muss. Nur Erstere darf auf Stufe 2 und Stufe 3 ohne neue Freigabe fortfahren.
- Eine zurückgegebene Refutation eines dispatchten Spezialisten **MUST** [MUST] gemäß `spec/claude/dispatch-brief/` als Re-Plan-Auslöser behandelt werden.

### Bindung für Skill- und Agent-Autorenschaft

- Ein Skill, dessen Workflow in versionierte Pfade schreibt, **MUST** [MUST] diesen Workflow in diesen Phasennamen ausdrücken, **MUST** [MUST] die Stufe oder den Stufenbereich benennen, auf den es zielt, und **MUST** [MUST] den Punkt benennen, an dem es das Schreib-Gate überschreitet.
- Die Phasennamen dieser Spec **DARF NICHT [MUST NOT]** mit dem Frontmatter-Feld `phase:` vermengt werden, und keines von beiden **MUSS [MUST]** über das andere ausgedrückt werden. `spec/claude/skill-agent-frontmatter/` definiert `phase:` über das Enum `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`: eine Position im **Lieferzyklus**, also wo im Ablauf des Portfolios eine Capability sitzt. Research, Plan und Implement sind eine **workflow-interne** Abfolge, also in welchem Teil ihrer eigenen Ausführung eine Capability steckt. Die Tokens `plan` und `review` kommen in beiden mit verschiedener Bedeutung vor; ein Skill mit `phase: plan` sagt also nichts darüber aus, ob es eine Plan-Phase durchläuft, und ein Reviewer-Agent der Research-Phase muss nicht `phase: review` tragen. Eine Capability nennt Stufe und Schreib-Gate in ihrem **Body**, nie durch Wiederverwendung jenes Frontmatter-Feldes.
- Ein read-only Reviewer- oder Scanner-Agent ist eine **Research-Phasen-Capability**. Sein Tool-Set regelt `spec/claude/agent-management/` §Tool access, einschließlich der dortigen engen Ausnahmen für read-only `Bash` und Netzwerk-Lesezugriffe; diese Spec ergänzt kein eigenes Tool-Verbot. Seine Ausgabe **MUST** [MUST] die obige Findings-Artefakt-Anker-Regel erfüllen.
- Eine Capability, die Arbeit an eine andere Capability übergibt, **MUST** [MUST] die Phasengrenze benennen, an der sie übergibt, damit die empfangende Capability weiß, welche Phasen sie besitzt.
- Eine wiederaufnehmbare Capability **MUST** [MUST] ihre Checkpoints gemäß `spec/claude/resumable-work/` mindestens an Phasengrenzen setzen, denn eine Phasengrenze ist der Ort, an dem ein Artefakt existiert, das ein wiederaufgenommener Lauf lesen kann, statt es zu rekonstruieren.
- Eine Capability, die dieser Spec unterliegt, **MUST** [MUST] sie zitieren, gemäß der Zitierregel in `spec/project/spec-driven-development/`.
- Eine Domänen-Spec, die diese Disziplin braucht, **MUST** [MUST] diese Spec referenzieren, statt ihre Regeln erneut auszuformulieren, und **MAY** [MAY] nur ihre scope-spezifische Anwendung ergänzen (etwa, welche Artefakte ihre Research-Phase lesen muss).

## Acceptance Criteria

- [ ] Die drei Phasennamen und die Read-only-gegen-Schreib-Grenze zwischen Plan und Implement sind so definiert, dass ein Reviewer jeden Schritt jedes Skills dagegen klassifizieren kann.
- [ ] Die Stufentabelle ist vollständig genug, um eine gegebene Änderung ohne weitere Ermessensentscheidungen darüber zu klassifizieren, welche Phasen gelten, und die Regel „keine höhere Stufe erzwingen" ist als prüfbares **MUST NOT** [MUST NOT] formuliert.
- [ ] Der Plan-Artefakt-Vertrag (Dateien, Änderung je Datei, Prüfung je Schritt, Out-of-Scope-Aussage, eigenständige Lesbarkeit) ist als Anforderung formuliert, die ein Reviewer gegen eine echte Plan-Datei prüfen kann.
- [ ] Die Anker-Regel für das Findings-Artefakt benennt die akzeptierten Ankerformen (`file:line`, Pfad, Kommando mit Ausgabe) und ist als **MUST** [MUST] formuliert.
- [ ] Jede Anforderung, die eine bestehende Spec überlappt, referenziert diese Spec, statt ihren Inhalt erneut auszuformulieren: `research-triangulate` für Quellenzahlen, `claim-provenance` für leserseitige Herkunft, `dispatch-brief` für Refutation, `review-plan` für Review-Befunde, `resumable-work` für Checkpoints, `spec-driven-development` für die Zitierregel.
- [ ] `skills/*/SKILL.md` und `agents/*.md`, die in versionierte Pfade schreiben, lassen sich gegen die Regeln aus §"Bindung für Skill- und Agent-Autorenschaft" allein durch Lesen des Artefakts auditieren, ohne es auszuführen.
- [ ] Das Lieferzyklus-Frontmatter-Feld `phase:` und die Phasennamen dieser Spec sind als verschiedene Achsen ausgewiesen, sodass eine Capability die eine nicht durch Deklaration der anderen erfüllen kann.
- [ ] Jede externe Behauptung in §Context löst sich zu einem Eintrag in §References auf.

## References

- Anthropic, *Best practices for Claude Code*: <https://code.claude.com/docs/en/best-practices> (explore, plan, implement, commit; die Regel „wenn du den Diff in einem Satz beschreiben kannst, überspring den Plan"; Subagents für Untersuchung; der adversariale Review-Schritt und sein Over-Engineering-Vorbehalt; Verifikation als wirksamste Praxis).
- Anthropic, *Effective context engineering for AI agents*: <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents> (Kontext als endliches Attention-Budget; Context Rot; Subagent-Architekturen, die verdichtete Zusammenfassungen zurückgeben; Compaction und strukturierte Notizen).
- HumanLayer, *Advanced Context Engineering for Coding Agents*: <https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md> (die Phasen Research, Plan, Implement und ihre Artefakte; die Fehlerkosten-Hierarchie über Recherche-, Plan- und Code-Zeilen; das Kontext-Auslastungsziel von 40 % bis 60 %; rund 200 Zeilen Plan zu reviewen statt 2.000 Zeilen Code).
- AgentPatterns, *The Research-Plan-Implement Pattern*: <https://agentpatterns.ai/workflows/research-plan-implement/> (die Tabelle Phasen-nach-Aufgabenkomplexität; das Re-Plan-Gate; das Implement-First-Antipattern; die Bedingungen, unter denen das Muster nach hinten losgeht).
- `betterquestions.ai`, *The Necessary Evolution of Research, Plan, Implement as an Agentic Practice in 2026*: <https://betterquestions.ai/the-necessary-evolution-of-research-plan-implement-as-an-agentic-practice-in-2026/> (die drei beobachteten Fehlermodi: ungescopete Recherche, die rund 40 % des Fensters verbraucht, unzuverlässige Recherche-Ausgabe und still übersprungene Plan-Schritte; die Unterscheidung Design gegen Structure).
- `matanshavit/qrspi`: <https://github.com/matanshavit/qrspi> (Artefakte je Phase, frischer Kontext je Phase, unabhängig verifizierbare vertikale Scheiben und die Rückwärts-Regeln, die Anpassung vor Ort von Rückkehr unterscheiden).
- LangChain Harness Engineering auf Terminal Bench 2.0, berichtet unter <https://www.zenml.io/llmops-database/harness-engineering-for-agentic-coding-systems> und <https://blockchain.news/news/langchain-terminal-bench-harness-engineering-breakthrough> (die Reasoning-Verteilung, die die Harness ohne Modellwechsel von 52,8 % auf 66,5 % hob).
- `O'Reilly Radar`, *The Right Amount of Spec for Agentic Development*: <https://www.oreilly.com/radar/the-right-amount-of-spec-for-agentic-development/> (Spezifikationstiefe nach Arbeitsart; der Zielkonflikt zwischen Vorab-Kosten und nachgelagerten Korrekturkosten).
- `ianhxu/agentic-engineering-field-study`, *Spec-Driven Development*: <https://github.com/ianhxu/agentic-engineering-field-study/blob/main/04-spec-driven-development.md> (die Über-Zeremonie-Evidenz: 1.300 Zeilen Markdown für ein Datums-Anzeige-Feature, Spezifikation bei 50 % der Projektzeit, der Problemgrößen-Mismatch, Spec-Drift und Nichtbefolgung durch Agents).

## Open Questions

- **Entscheidung (2026-08-23): Für Skills ist die Durchsetzung verdrahtet, für Agenten bleibt sie zurückgestellt.** Der Revisit-Trigger oben war nicht gefeuert — eine Prüfung aller 65 Skills fand keines, das das Schreib-Gate ohne Review-Oberfläche überschreitet —, dies ist also eine dem Trigger vorgreifende Operator-Entscheidung und wird hier als solche festgehalten, nicht als ausgelöster Trigger dargestellt. Die mechanische Hälfte (Zitat vorhanden, Stufe benannt, Schreib-Gate benannt) prüft `scripts/validate_skills.py`; die Ermessenshälfte (passt die genannte Stufe zur Arbeit, ist das Gate an der richtigen Stelle benannt) liegt bei `skill-review` gemäß `spec/claude/skill-review/` §„Checks derived from research-plan-implement“. Die Prüfung ist **adoptionsgebunden**: Ein noch nicht adoptiertes Skill fließt in einen aggregierten Rückstands-Befund, und mit dem Zitat werden seine Stufen- und Schreib-Gate-Regeln blockierend. Das ist das Baseline-and-Ratchet-Modell, das `spec/project/test-tier-static-analysis/` §„Severity-Gating und das Baseline-and-Ratchet-Modell“ für die Einführung von Analyse über einem bestehenden Korpus verlangt, und der Grund, warum nicht der gesamte Rückstand auf einmal blockiert. Die Agenten-Hälfte bleibt unberührt: `agent-review` prüft aus dieser Spec noch nichts. **Revisit-Trigger für Agenten:** wenn der Ratchet auf der Skill-Seite bei seinen ersten Adoptierenden eingerastet ist, die Prüfform also belegt ist, bevor sie gespiegelt wird.
- Die Stufengrenzen sind über die Arbeitsform statt über eine messbare Schwelle (Dateizahl, Diff-Größe) formuliert. Ein messbarer Proxy würde die Klassifikation auch nachträglich auditierbar machen statt nur zur Autorenzeit, aber jeder bisher geprüfte Kandidat klassifiziert genau die Fälle falsch, auf die es ankommt (eine Einzeilenänderung an einem veröffentlichten Vertrag ist Stufe 3). **Revisit-Auslöser:** ein dokumentierter Fall, in dem zwei Reviewer dieselbe Änderung unterschiedlich einstufen.
- Ob das Design-Gate auf Stufe 3 einen eigenen Phasennamen verdient, wie ihn die separate Design-Phase in QRSPI ihm gibt, bleibt offen. Diese Spec faltet es als Ordnungsregel in Plan (erst wohin, dann wie), weil ein vierter Phasenname einen eigenen Artefakt-Vertrag bräuchte, um prüfbar zu sein, und bisher kein Fall in diesem Monorepo einen verlangt hat.
