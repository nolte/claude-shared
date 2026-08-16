# Herkunft von Behauptungen

Status: draft
Portfolio-Scope: portfolio

## Kontext

Ein Agent, der „X passiert, weil Y" in ein Issue schreibt, hat keine Meinung festgehalten, sondern eine Prämisse veröffentlicht. Der nächste Leser übernimmt den Satz als belegt und baut darauf auf. Nichts im Korpus fragt, wie er belegt wurde — also reist eine Behauptung, die ein einziges `grep` widerlegt hätte, genauso weit wie eine bewiesene.

Drei Behauptungen aus einer einzigen Session in `nolte/kamerplanter` machen die Kosten konkret. Jede war selbstsicher formuliert, jede war mit dem Symptom vereinbar, das sie erklärte, jede war falsch, und jede war in unter fünf Minuten widerlegbar. `PlantCountStep ist unerreichbares UI` ging als vorgeschlagener Defekt in Issue #1207; die Komponente ist abgelöst statt kaputt, ihr Wert wird weiterhin berechnet und übermittelt, und wer das Issue aufgegriffen hätte, wäre auf die Suche nach einem Verdrahtungsdefekt gegangen, den es nicht gibt. `Der Delete-Fall skippt, weil die neue Zeile nicht auf der ersten Seite liegt` war die Arbeitsdiagnose vor einem Fix; bei 18 gesetzten Datensätzen und Seitengröße 50 sortiert die neue Zeile auf Position 8 von 19, Pagination kann also nicht beteiligt sein. `Das Harness hat bereits eine funktionierende Fassung dieses Helpers` rahmte einen Fix in einer Commit-Message; die zweite Kopie hat gar keinen Aufrufer, und der Helper hatte in keiner der beiden je funktioniert. Zwei der drei kosteten nichts, weil der nächste Schritt sie zufällig aufdeckte. Die erste stand einen Tag lang als Arbeit da, die es nicht gab.

Das Muster ist keine Nachlässigkeit im üblichen Sinn. Jede Behauptung war plausibel und jede war billig zu prüfen. Was fehlte, war der Schritt, sie zu widerlegen zu *versuchen*, bevor sie aufgeschrieben wurde.

Evidenz und Aktualität: Die drei Beobachtungen oben sind in `nolte/claude-shared#545` (2026-08-16) festgehalten und werden hier als gegeben übernommen statt neu hergeleitet. Diese Spec behauptet nichts über etwas außerhalb der Working Copy und trägt daher keine externen Quellen.

Abgrenzung: `spec/claude/dispatch-brief/` besitzt den delegierten Fall, in dem ein Orchestrator eine Hypothese an einen Spezialisten übergibt und deren Refutation autorisieren muss. `spec/claude/research-triangulate/` besitzt Aussagen über Dinge, die *nicht* in der Working Copy verifizierbar sind, und schließt repo-interne bewusst aus — genau die Lücke, die diese Spec füllt. `spec/project/e2e-failure-diagnosis/` §A besitzt die Mechanismus-Schwelle, die eine *Remediation* für einen roten End-to-End-Cluster gated, und wendet diese Spec an, statt sie zu wiederholen. `spec/project/test-falsifiability/` besitzt die Eigenschaft für Testcode. §Abgrenzung formuliert jede Grenze präzise.

Leser: jeder Agent und jedes Skill, das eine Behauptung in ein Artefakt schreibt, das jemand anderes liest; die Reviewer und Analyzer, deren Befunde *selbst* Behauptungen sind; und jeder, der ein solches Artefakt reviewt.

## Ziele

- Die Herkunft einer belastbaren Behauptung zu einer **routinemäßigen, prüfbaren Eigenschaft** des tragenden Artefakts machen, statt zu einer Gewohnheit, an die der Autor sich erinnern muss.
- Den **selbstgerichteten** Fall abdecken, in dem Analyst und Handelnder derselbe Agent sind, kein Briefing geschrieben wird und nichts irgendetwas autorisiert.
- Die geforderte Ausgabe **klein genug halten, um Alltagsarbeit zu überstehen**, damit die Regel nicht still fallengelassen wird, wie es einer verrauschten Prüfung ergeht.
- Der Regel einen **stabilen, zitierbaren Home** geben, auf den Domänen-Specs und publizierende Skills zeigen, statt sie neu auszuformulieren.

## Nicht-Ziele

- Was mit einer Ursache *geschieht*, sobald sie belegt ist. Das Remediations-Gate für einen End-to-End-Cluster gehört `spec/project/e2e-failure-diagnosis/` §A, und Codeänderung unter einer bewiesenen Ursache gehört den Test-Cycle-Specs.
- Falsifizierbarkeit von Testcode, ihre Taxonomie und ihre Detektionsrouten; besessen von `spec/project/test-falsifiability/`.
- Beschaffung und Triangulation von Aussagen über repo-externe Fakten; besessen von `spec/claude/research-triangulate/`.
- Die Refutations-Klausel, die ein dispatchender Orchestrator einem Spezialisten schuldet; besessen von `spec/claude/dispatch-brief/`.
- Behauptungen in der laufenden Konversation mit dem Operator, wo eine Korrektur eine Antwort entfernt ist.
- Die Implementierung eines Linters oder Scanners. §D prüft bewusst die Substanz statt eines Tokens, es gibt also nichts deterministisch Grepbares; Tooling ist eigene Arbeit, falls ein maschinenlesbarer Träger je ein Feld erhält.

## Anforderungen

### A. Was die Regel bindet

- Eine **belastbare Behauptung** ist eine Aussage, die zugleich **gegen die Working Copy prüfbar** ist und **etwas darstellt, worauf die Arbeit eines anderen Akteurs aufbaut**. Vier Formen qualifizieren sich, und die Regel unterscheidet nicht zwischen ihnen: eine *Ursache* („der Test scheitert, weil die Zeile auf Seite zwei sortiert"), ein *Zustand* („diese Komponente ist unerreichbar"), eine *Existenz* („das Harness hat diesen Helper bereits") und eine *Abwesenheit* („kein Aufrufer bleibt übrig"). Das Issue hinter dieser Spec benannte Ursachen, doch zwei ihrer drei gemessenen Fehlschläge waren eine Zustands- und eine Existenzbehauptung.
- Die Regel **MUSS [MUST]** jedes Artefakt binden, das die **Session überdauert** und als Prämisse gelesen werden kann: einen Issue-Body oder -Kommentar, eine Commit-Message, eine Pull-Request-Beschreibung, ein Review-Finding, eine Plandatei, einen Audit-Report, Spec-Prosa, eine Feature- oder Sprint-Datei. Diese Liste ist illustrativ; das Kriterium ist, ob der Träger die Session überlebt, nicht ob er hier auftaucht.
- Die Regel **DARF NICHT [MUST NOT]** eine Wertung („das liest sich schwer"), einen Vorschlag („wir sollten das extrahieren") oder eine Frage binden. Keines davon ist eine prüfbare Aussage über die Working Copy.
- Die Regel **DARF NICHT [MUST NOT]** eine Aussage über etwas binden, das nicht in der Working Copy verifizierbar ist — eine veröffentlichte Version, eine Drittanbieter-API-Signatur, einen Pfad im Schwester-Repo. Die besitzt `spec/claude/research-triangulate/`, dessen Quellenzahl-Disziplin der externe Zwilling dieser Regel ist.
- Die Regel **DARF NICHT [MUST NOT]** die laufende Konversation mit dem Operator binden. Die Kosten, die diese Spec adressiert, entstehen durch eine falsche Prämisse, die weiterreist; im Gespräch ist die Korrektur eine Antwort entfernt.

### B. Was das Artefakt tragen muss

- Ein Artefakt, das eine belastbare Behauptung trägt, **MUSS [MUST]** diese Behauptung als genau eines von **belegt** oder **unbelegt** ausweisen. Keines von beidem zu tragen ist der Defekt, für dessen Benennung diese Spec existiert.
- Eine als **belegt** ausgewiesene Behauptung **MUSS [MUST]** die Beobachtung nennen, die sie feststellte: ein Kommando samt der Ausgabe, die es entscheidet, oder eine `file:line`, die ein Leser öffnen kann. Eine unverankerte Aussage wird nicht dadurch belegt, dass sie selbstsicher formuliert ist — alle drei Fehlschläge in §Kontext waren selbstsicher formuliert.
- Eine als **unbelegt** ausgewiesene Behauptung **MUSS [MUST]** die Beobachtung nennen, die sie entscheiden *würde*, und **MUSS [MUST]** feststellen, dass diese Beobachtung nicht gemacht wurde. „Ich vermute X, unbelegt, und das hier würde es entscheiden" zu veröffentlichen ist voll konform und oft die richtige Antwort; „X" zu veröffentlichen, wenn X geraten ist, nicht.
- Eine Behauptung, die eine bereits belegte Behauptung aus einem anderen Artefakt wiederholt, **KANN [MAY]** die Anforderung durch Zitieren jenes Artefakts erfüllen. Das Zitat ist der Anker; eine zweite Messung ist nicht verlangt.
- Eine Behauptung als unbelegt festzuhalten **DARF NICHT [MUST NOT]** als schwächerer Beitrag gelten als sie zu belegen. Eine ehrlich markierte Hypothese überlebt unversehrt, bis sie messbar wird — genau das Ergebnis, für das diese Regel da ist.

### C. Die Behauptung belegen, und was es kostet, es nicht zu tun

- Ist die unter §B benannte Beobachtung **billig mit den Mitteln zur Hand**, **MUSS [MUST]** der Autor sie machen, statt die Behauptung als unbelegt zu veröffentlichen. Jeder Fehlschlag in §Kontext war in unter fünf Minuten messbar; eine Regel, die sie als ehrlich etikettierte Vermutungen durchgelassen hätte, hätte das Problem umbenannt statt behoben.
- **Unbelegt** steht nur zur Verfügung, wenn die Beobachtung nicht billig ist, und das Artefakt **MUSS [MUST]** dann sagen, was sie teuer macht — sie braucht einen vollen Suite-Lauf, Produktionsdaten, eine Operator-Entscheidung, einen Zugang, den der Autor nicht hat.
- Die **Billigkeits-Einschätzung bleibt beim Autor**; diese Spec fixiert keine Schwelle, denn jede feste Schwelle ist im nächsten Kontext falsch. Was die Regel verlangt, ist, dass die Einschätzung *aufgeschrieben* wird — das macht aus dem Ausweg einen prüfbaren statt eines freien: Wer die Beobachtung für billig hält, kann das nun gegen eine formulierte Behauptung sagen.
- Die Pflicht ist, **Refutation zu versuchen, nicht Beweise anzuhäufen**. Eine tatsächlich gemachte Beobachtung, die der Behauptung hätte widersprechen können, erfüllt §B und §C zusammen. Mehr zu verlangen würde jede Behauptung teuer machen und die Regel in die Missachtung treiben — das Schicksal, das `spec/project/test-falsifiability/` einer verrauschten Prüfung bereits voraussagt.

### D. Form, und wie ein Reviewer sie prüft

- Die Unterscheidung **MUSS [MUST]** an der **Substanz geprüft werden, nicht am Wortlaut**. Diese Spec schreibt kein wörtliches Token vor, denn zu ihren Trägern zählen Commit-Messages und Prosa in beiden konfigurierten Sprachen. Die kanonischen deutschen Formen lauten: *belegt — `<Kommando>` zeigt `<Ergebnis>`* und *unbelegt; `<Beobachtung>` würde es entscheiden, nicht gemessen wegen `<Kosten>`*.
- Ein Reviewer prüft ein Artefakt mit einer einzigen Frage gegen diese Spec: **kann ich allein aus dem Artefakt erkennen, ob der Autor gemessen oder geraten hat?** Wenn nicht, ist das Artefakt nicht konform. Wo eine Behauptung als belegt markiert ist, lautet die zweite Frage, ob der genannte Anker tatsächlich auflöst.
- Ein Träger, der bereits ein maschinenlesbares Finding-Format hat, **KANN [MAY]** die Unterscheidung als Feld statt als Prosa ausdrücken, sofern das Feld von der Spec definiert wird, die jenes Format besitzt. Diese Spec definiert kein solches Feld und verlangt keines.
- Eine Domänen- oder scope-spezifische Spec, die diese Regel braucht, **MUSS [MUST]** diese Spec referenzieren, statt ihren Regeltext neu auszuformulieren, und **KANN [MAY]** nur ihre scope-spezifische Anwendung ergänzen.

### Abgrenzung

Diese Spec ist gegen ihre Nachbarn begrenzt und **DARF** deren Regeln **NICHT** wiederholen:

- `spec/claude/dispatch-brief/` besitzt die **delegierte** Hälfte: ein Briefing mit Hypothese muss den empfangenden Spezialisten autorisieren, sie zu widerlegen, und definiert, was eine gültige Refutation enthält. Diese Regel braucht zwei Parteien. Diese Spec besitzt den Fall, in dem Analyst und Autor derselbe Agent sind, sodass kein Briefing existiert und nichts irgendetwas autorisiert. Ein Dispatch-Briefing ist zugleich ein Artefakt nach §A, also gelten beide für es; sie überlappen nicht, weil die eine regelt, was das Briefing dem Spezialisten schuldet, und die andere, was es seinem Leser schuldet.
- `spec/claude/research-triangulate/` besitzt **repo-externe** Aussagen und ihre Quellenzahl-Disziplin und stellt fest, dass repo-interne Aussagen nicht trianguliert werden, weil sie durch direktes Lesen der Working Copy verifiziert werden. Diese Spec ist das, was aus jener Verifikation eine Pflicht statt einer Annahme macht. Beide sind komplementär und teilen keine Anforderung.
- `spec/project/e2e-failure-diagnosis/` §A besitzt die **Mechanismus-Schwelle** für einen End-to-End-Fehlercluster: die drei zulässigen Beweisformen und den Hinreichend-und-notwendig-Standard, der eine Remediation gated. Sie wird von einem roten Lauf aus erreicht und gated eine Änderung. Diese Spec gated die *Behauptung* und wird von jedem Artefakt aus erreicht. §A wendet diese Spec an; keine wiederholt die andere, und die Beweisformen von §A bleiben dort.
- `spec/project/test-falsifiability/` besitzt die Eigenschaft für **Testcode** — ein Test, der nicht scheitern kann. Diese Spec regelt Prosa-Behauptungen. Die beiden sind Geschwister in der Denkfigur, nicht im Scope: beide benennen eine Aussage, der vertraut wird, weil nie von ihr verlangt wurde zu scheitern.
- `spec/claude/review-plan/` besitzt das **Finding-Format**, einschließlich der Anforderung, dass ein Finding die Spec-Anforderung zitiert, auf der es ruht. Jenes Zitat benennt die verletzte Regel; diese Spec regelt die Evidenz für die Ursache, die das Finding benennt. Ein Finding erfüllt die eine und verfehlt die andere immer dann, wenn es eine Regel zitiert, die Ursache aber rät.

### Einbindung in Agents und Skills

- Ein Agent, dessen Befunde eine Ursache benennen, **MUSS [MUST]** die Unterscheidung **im Befund selbst** tragen, nicht in einer Begleitnotiz, damit sie die Extraktion in ein Tracking-Artefakt überlebt. Das bindet die Reviewer- und Analyzer-Agents, die kausale Sprache emittieren.
- Ein Skill, das ein dauerhaftes Artefakt komponiert, **MUSS [MUST]** §B anwenden, wenn das geschriebene Artefakt eine belastbare Behauptung trägt. Das bindet die Skills, die Issues, Pull-Request-Bodies, Pläne, Features, Specs und Audit-Reports publizieren.
- Eine Einbindung **MUSS [MUST]** im Body des Artefakts leben, nie in seinem `description:`-Frontmatter, damit das Routing-Budget des Portfolios nicht regressiert.

## Akzeptanzkriterien

- [ ] Ein Reviewer kann allein aus §A entscheiden, ob ein gegebener Satz in Scope ist: prüfbar gegen die Working Copy, belastbar für einen anderen Akteur, und getragen von einem Artefakt, das die Session überdauert
- [ ] Die vier qualifizierenden Behauptungsformen (Ursache, Zustand, Existenz, Abwesenheit) sind benannt, und die ausgeschlossenen Klassen (Wertung, Vorschlag, repo-extern, laufende Konversation) sind mit ihren Eigentümern benannt
- [ ] Genau zwei Marker sind verlangt, jeder mit seiner eigenen formulierten Pflicht, und beide Pflichten sind gegen ein tatsächliches Artefakt prüfbar
- [ ] Die Miss-wenn-billig-Pflicht ist als `MUST` formuliert, mit der Kostenbehauptung selbst als Pflichtangabe im Artefakt, wenn der Ausweg genommen wird
- [ ] Die Billigkeitsschwelle ist ausdrücklich dem Autor überlassen, mit festgehaltener Begründung
- [ ] Die Regel wird an der Substanz statt an einem wörtlichen Token geprüft, und eine kanonische Form wird angeboten, ohne vorgeschrieben zu werden
- [ ] Die Prüfung des Reviewers ist als einzelne, allein aus dem Artefakt beantwortbare Frage formuliert
- [ ] §Abgrenzung benennt alle fünf Nachbarn und wiederholt keine ihrer Regeln
- [ ] Die Einbindungsregel verbietet `description:`-Wachstum, sodass die Übernahme dieser Spec das Routing-Budget nicht regressieren lassen kann

## Referenzen

- `spec/claude/dispatch-brief/`: die delegierte Hälfte derselben Disziplin, gegen die §Abgrenzung dieser Spec begrenzt
- `spec/claude/research-triangulate/`: der Zwilling für externe Aussagen, dessen Ausschluss repo-interner Aussagen diese Spec besitzt
- `spec/claude/review-plan/`: das Finding-Format, dessen Spec-Zitat-Anforderung orthogonal zu dieser ist
- `spec/project/e2e-failure-diagnosis/`: §A, die End-to-End-Mechanismus-Schwelle, die diese Spec anwendet
- `spec/project/test-falsifiability/`: das Testcode-Geschwister und die Quelle des Verrauschte-Prüfung-Arguments in §C
- Auftrag und Evidenz: `nolte/claude-shared#545`, dessen drei gemessene Falschbehauptungen die gesamte empirische Basis bilden; die Schwesterlücke zu Test-Doubles ist `nolte/claude-shared#542`

## Offene Fragen

- **Ob ein maschinenlesbarer Träger ein Herkunftsfeld erhalten sollte.** §D erlaubt es und definiert keines. `spec/claude/review-plan/`-Findings und die Ausgabe der Lektorat-Scanner sind die beiden Träger, die bereits ein Maschinenformat haben, und ein Feld dort würde die Regel genau dort grepbar machen, wo Befunde entstehen. *Erneut prüfen*, wenn Reviewer-Agents §Einbindung in Agents und Skills übernommen haben und sich die Prosaform als zu schwach für verlässliche Extraktion erweist.
- **Ob bestehende Artefakte nachgezogen werden sollen.** Diese Spec bindet Artefakte ab der Übernahme. Das Repository und das weitere Portfolio tragen unmarkierte Behauptungen von davor, und hier wird kein Nachziehen verlangt. *Erneut prüfen* nur mit begrenztem Scope; ein unbegrenzter Durchlauf über historische Issues und Commit-Messages kostete mehr, als die Behauptungen wert sind.
- **Ob die Billigkeits-Einschätzung beim Autor bleibt.** §C fixiert bewusst keine Schwelle und nimmt in Kauf, dass ein Autor, der die Kosten systematisch überzeichnet, den Unbelegt-Ausweg weiterhin nehmen kann. Die Milderung ist, dass die Kostenbehauptung nun aufgeschrieben und bestreitbar ist. *Erneut prüfen*, wenn Reviews beginnen, überzeichnete Kostenbehauptungen statt unmarkierter Behauptungen zu finden.
