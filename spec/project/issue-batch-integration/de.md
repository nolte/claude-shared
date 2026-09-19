# Issue-Bündel-Integration

Status: draft

## Kontext

`spec/project/issue-orchestration/` führt **ein** rohes GitHub-Issue durch Erfassung, Klassifikation, das Anforderungs-Gate, die Zerlegung in Work-Packages, den Spezialisten-Dispatch und ein Verifikations-Gate und endet bei genau einem offenen Pull Request. Dieser Vertrag trägt für ein isoliertes Issue und wird hier nicht verändert.

Teuer wird er, sobald der Backlog ein *Cluster* enthält. Einzeln abgearbeitet kostet ein Cluster aus `n` Issues `n` Pull Requests, und `spec/project/pull-request-workflow/` §"Sequenzielles Mergen mehrerer offener PRs" verlangt dann, diese `n` seriell zu mergen — mit einem Rebase zwischen je zwei aufeinanderfolgenden. Das Cluster bezahlt also `n` Quality-Gate-Läufe, `n` Rebases und `n` Review-Kontexte für das, was ein Reviewer als eine Änderung versteht. Fassen die Mitglieder dieselben Dateien an, kollidieren diese Rebases zusätzlich miteinander.

Dass solche Cluster hier vorkommen, ist **belegt**: `git log develop` zeigt `b4dd0f16` (#623), `0316be01` (#624) und `c969bc02` (#625) als drei aufeinanderfolgende Pull Requests, die dieselbe Repository-Settings-Fläche reparieren und einzeln gemergt wurden. Ob eine Bündelung diese Kosten messbar gesenkt hätte, ist **unbelegt** — die Beobachtung, die das klären würde, ist ein Lauf dieses Prozesses gegen ein vergleichbares Cluster, und ein solcher Lauf existiert noch nicht.

Diese Spec ergänzt ausschließlich die Gruppen-Schicht: wie ein Cluster als Gruppe aufgenommen wird, einmal auf Gruppenebene verstanden und geplant wird, auf einem dedizierten Integrationsbranch entwickelt, zu genau einer Integration nach `develop` gebündelt und anschließend abgeschlossen wird.

Abgrenzung: `spec/project/issue-orchestration/` besitzt alles, was *innerhalb* eines Mitglieds-Issues geschieht. `spec/project/pull-request-workflow/` besitzt Form, Gates, Merge-Strategie und Issue-Schließungssemantik von Pull Requests. `spec/project/branching-model/` besitzt Branch-Präfixe, Protection und den Release-Fluss. `spec/project/parallel-working-copies/` besitzt Worktree-Pfade und -Lebenszyklus. `spec/claude/research-plan-implement/` besitzt die Phasen-Disziplin, die diese Spec für Analyse und Plan konsumiert. `spec/project/continuous-improvement/` besitzt den Portfoliolücken-Loop samt Rekurrenz-Schwellwert, und `spec/project/defect-class-guards/` besitzt, was eine geschlossene Defektklasse hinterlässt; §E speist beide, statt sie zu wiederholen.

Leserschaft: Operatoren, die einen gruppierten Backlog-Durchlauf fahren, Skill- und Agent-Autoren, die die Gruppen-Schicht implementieren, und Reviewer, die einen Bündel-Pull-Request erhalten und beurteilen müssen, ob die Gruppe eine Änderung war.

## Ziele

- Ein Cluster wird durch ein benanntes Prädikat zur Gruppe, nicht durch das Gefühl eines Operators, dass die Issues zusammengehören
- Die Gruppe wird **einmal** auf Gruppenebene verstanden und geplant, bevor irgendein Mitglied umgesetzt wird
- Der Plan macht Vollständigkeit prüfbar: Jedes Mitglied ist auf jede Artefaktklasse zurückführbar, die es ändern muss, sodass eine fehlende Spec, ein fehlender Test, ein fehlendes Dokument oder ein fehlendes Index-Update sichtbar wird, bevor das Bündel aufgeht — nicht erst nach dem Merge
- Die Gruppe erreicht `develop` als genau ein Pull Request, sodass das Cluster einen Review-Kontext, ein Gate und einen Merge kostet
- Die Wahl zwischen den beiden Strang-Modi ist deterministisch statt Ermessenssache
- Jedes Mitglieds-Issue wird nach der Integration geschlossen, mit einer Spur zurück zum Bündel, das es erzeugt hat
- Ein Cluster wird als Beleg über den Prozess gelesen, der es hervorgebracht hat, nicht nur als Arbeitsvorrat: Ein wiederkehrendes Muster stellt die Regel oder das Gate infrage, das seine Wiederkehr zugelassen hat
- Die bestehende Einzel-Issue-Maschinerie wird unverändert wiederverwendet

## Nicht-Ziele

- Erfassung, Klassifikation, Anforderungs-Gate, Zerlegung und Spezialisten-Dispatch je Issue: `issue-orchestration` bleibt maßgeblich, und diese Spec stößt sie an, statt sie neu zu definieren
- Aufbau des Pull-Request-Bodys, Required Checks, Merge-Strategie und die Semantik der Closing-Keywords: `pull-request-workflow` bleibt maßgeblich
- Branch-Präfixe, Branch-Protection und der Release-Fluss: `branching-model` bleibt maßgeblich
- Worktree-Pfade, -Zuordnung und -Rückbau: `parallel-working-copies` bleibt maßgeblich
- Der Research-/Plan-/Implement-Phasenvertrag und seine Stufentabelle: `spec/claude/research-plan-implement/` bleibt maßgeblich; diese Spec benennt nur, wo ihre eigenen Phasen sitzen
- Die `roadmap → feature → sprint`-Pipeline: Ein unbeschränktes Issue wird gemäß `issue-orchestration` §"Routing in die formale Pipeline (kein Planungs-Bypass)" dorthin geroutet, und Bündelung ersetzt niemals Planung
- Die Entscheidung, *welche* Issues Aufmerksamkeit verdienen: Backlog-Triage gehört `portfolio-inflight-triage` und der Sprint-Kadenz des Repositories
- Der Rekurrenz-Schwellwert, ab dem eine Portfoliolücke geschlossen werden muss, und der Schließungs-Loop selbst: `continuous-improvement` bleibt maßgeblich, und §E speist ihn, statt ihn neu herzuleiten

## Anforderungen

### A. Gruppenbildung und Aufnahme

- **MUSS [MUST]** ein Issue nur aufgrund mindestens eines von genau drei Prädikaten in eine Gruppe aufnehmen, je Mitglied festgehalten: **thematische Kopplung** (die Mitglieder ändern dieselbe Capability oder denselben Spec-Topic), **geteilte Berührungsfläche** (ihre Work-Packages ändern überlappende Dateien oder Pfade) oder **Abhängigkeitskette** (die Änderung eines Mitglieds ist Voraussetzung für die eines anderen)
- **MUSS NICHT [MUST NOT]** ein Issue mit der Begründung aufnehmen, es sei in derselben Iteration oder demselben Zeitfenster offen. Ein gemeinsames Zeitfenster ist keine Kopplung, und eine so gebildete Gruppe ist genau der Fall "unzusammenhängende Änderungen in einem Pull Request", den `pull-request-workflow` §"PR-Rahmenbedingungen" außerhalb eines `exp/`-Branches verbietet
- **MUSS [MUST]** je aufgenommenem Mitglied festhalten, welches Prädikat es aufgenommen hat und welcher Beleg dieses Prädikat stützt
- **MUSS [MUST]** die eine logische Änderung der Gruppe in einem Satz im Gruppen-Artefakt formulieren. Dieser Satz ist es, der ein Mehr-Issue-Bündel mit der Ein-logische-Änderung-Regel aus `pull-request-workflow` §"PR-Rahmenbedingungen" versöhnt: Eine Gruppe, die die Aufnahmeprädikate erfüllt, *ist* eine logische Änderung und braucht daher keine `exp/`-Ausnahme. Ein Cluster, dessen Änderung sich nicht in einem Satz sagen lässt, ist keine Gruppe — seine Issues werden einzeln abgearbeitet
- **MUSS [MUST]** jedes Mitglied innerhalb der *bounded*-Definition von `issue-orchestration` halten (ein Goal-Outcome, ein Pull-Request-Strang, kein neues oder umgehängtes Roadmap-Item). Ein unbeschränktes Issue wird in die formale Pipeline geroutet und **MUSS NICHT [MUST NOT]** in einer Gruppe mitgeführt werden
- **MUSS [MUST]** je Mitglied, dessen Issue eine **Ursache** behauptet, diese Ursache vor der ersten getrackten Änderung des Mitglieds gegen den Code verifizieren, gemäß `spec/project/issue-orchestration/` §„Issue-Akquise und Durchdringung"; die Gruppenanalyse aus §E sucht eine strukturelle Ursache über die Mitglieder hinweg und ersetzt nicht die Prüfung, ob die eigene behauptete Ursache jedes Mitglieds trägt. Eine widerlegte Mitgliedsursache wird im Gruppen-Artefakt mit der Messung festgehalten, die sie widerlegte, und der Plan des Mitglieds folgt der Messung
- **MUSS NICHT [MUST NOT]** ein Issue der Klasse `question` aufnehmen, das konstruktionsbedingt keine Work-Packages erzeugt
- **MUSS [MUST]** der Gruppe eine stabile Id `<YYYY-MM-DD>-<slug>` geben, die wortgleich für Integrationsbranch, Artefaktpfad und Checkpoint verwendet wird, damit die drei nicht auseinanderlaufen
- **SOLLTE [SHOULD]** eine Gruppe klein genug halten, dass ihr Bündel-Diff in einer Sitzung reviewbar ist; eine Gruppe, die darüber hinauswächst, wird in zwei Gruppen geteilt statt als unreviewbares Bündel gemergt

### B. Branch- und Working-Copy-Topologie

- **MUSS [MUST]** die Gruppe auf genau einem dedizierten **Integrationsbranch** entwickeln, der von `origin/develop` abzweigt, in einem dedizierten Worktree gemäß `parallel-working-copies` §"Pfad-Layout" und §"Lebenszyklus: Anlegen"; der Primärcheckout bleibt auf `develop`
- **MUSS [MUST]** den Integrationsbranch `<type>/<group-id>` nennen, wobei `<type>` der Conventional-Commits-Typ der dominierenden Änderung der Gruppe gemäß `branching-model` §"Branch-Rollen" ist
- **MUSS NICHT [MUST NOT]** für eine Gruppe mit auszulieferndem Inhalt standardmäßig das `exp/`-Präfix wählen. `branching-model` §"Branch-Rollen" schließt `exp`-Pull-Request-Titel aus den nutzerseitigen Release Notes aus, sodass ein Bündel ergebnistragender Fixes oder Features auf `exp/` dort verschwinden würde. `exp/` bleibt einer wirklich explorativen Gruppe vorbehalten
- **MUSS [MUST]** den Integrationsbranch per Rebase auf `develop` nachziehen, sobald `develop` weiterrückt, gemäß `pull-request-workflow` §"Aktualität des Branches". Der Integrationsbranch ist der einzige Punkt, an dem diese Regel greift; Mitglieds-Sub-Branches rebasen auf den Integrationsbranch, nicht auf `develop`
- **MUSS [MUST]** in Modus B (§C) jeden Mitglieds-Sub-Branch vom Kopf des Integrationsbranches in einem eigenen Worktree anlegen — ein Branch ist gemäß `parallel-working-copies` §"Branch-zu-Worktree-Zuordnung" höchstens einmal ausgecheckt — und ihn **ohne Pull Request** in den Integrationsbranch zurückmergen
- **MUSS NICHT [MUST NOT]** einen Pull Request eröffnen, dessen Basis der Integrationsbranch ist. `pull-request-workflow` §"PR-Rahmenbedingungen" verlangt, dass jeder Pull Request auf `develop` zielt, und der Bündel-Pull-Request ist die einzige Review-Oberfläche der Gruppe. Der akzeptierte Preis ist, dass ein Mitglied kein eigenes Review-Gate erhält; §"Offene Fragen" hält das fest
- **MUSS [MUST]** jeden Mitglieds-Sub-Branch samt Worktree zurückbauen, sobald er in den Integrationsbranch gemergt ist, gemäß `parallel-working-copies` §"Lebenszyklus: Stilllegen"

### C. Das Modus-Gate

- **MUSS [MUST]** den Strang-Modus festlegen, bevor das erste Mitglied umgesetzt wird, und die Entscheidung mit Begründung im Gruppen-Artefakt festhalten:
  - **Modus A (Einzelstrang)**: Jedes Mitglied wird direkt auf dem Integrationsbranch umgesetzt
  - **Modus B (Sub-Branch)**: Jedes Mitglied wird auf einem eigenen Sub-Branch umgesetzt und gemäß §B in den Integrationsbranch gemergt
- **MUSS [MUST]** Modus B wählen, sobald ein Mitglied absehbar **herauslösbar** sein muss: seine Abnahme ist unsicher, es hängt von etwas außerhalb der Kontrolle der Gruppe ab, oder ein Review, das es ablehnen kann, steht noch aus — am häufigsten ein Mitglied der Klasse `security`. Herauslösbarkeit ist das Kriterium, weil ein Modus-B-Mitglied durch Fallenlassen eines einzigen Merges aus dem Bündel entfernt werden kann, während ein Modus-A-Mitglied in einem gemeinsamen Commit-Strang verflochten ist
- **MUSS [MUST]** andernfalls Modus A wählen
- **MUSS [MUST]**, wenn sich ein Mitglied nach der Wahl von Modus A als herauslösbar erweist, dies als **strukturelle Regression** gemäß `spec/claude/research-plan-implement/` §"Replanning ist explizit" behandeln: anhalten, die gescheiterte Annahme benennen und zu Plan zurückkehren — entweder wird dieses Mitglied auf einen eigenen Branch ausgelagert oder aus der Gruppe entfernt
- **MUSS [MUST]** eine **lokale Anpassung** von einer **strukturellen Regression** gemäß `spec/claude/research-plan-implement/` §"Replanning ist explizit" unterscheiden, sobald Mitglieder umgesetzt werden: Ein Mitglied, dessen Arbeit größer oder anders geschnitten ausfällt als geplant, während Aufnahme, Modus und Reihenfolge der Gruppe weiter gelten, ist eine lokale Anpassung und wird ohne erneute Freigabe im Artefakt festgehalten; alles, was ein Aufnahmeprädikat, die Modus-Entscheidung oder die Abhängigkeitsordnung entwertet, ist eine strukturelle Regression und führt die Gruppe zur erneuten Freigabe nach Plan zurück
- **MUSS [MUST]** ein herausgelöstes Mitglied in die Einzelabarbeitung unter `issue-orchestration` zurückgeben und die Herauslösung im Gruppen-Artefakt festhalten; ein herausgelöstes Mitglied verbleibt in keiner Gruppe

### D. Gruppen-Voranalyse und Umsetzungsplan

- **MUSS [MUST]** die Arbeit der Gruppe gemäß `spec/claude/research-plan-implement/` §"Die Phasentiefe skaliert mit dem Blast Radius" einstufen und die Stufe festhalten. Eine Gruppe umfasst mehrere Issues und mehrere Dateien, ist also **mindestens Stufe 2** und Stufe 3, sobald sie Repository-Grenzen überschreitet oder einen veröffentlichten Vertrag ändert; das Operator-Freigabe-Gate zwischen Plan und Implement ist damit immer erforderlich
- **MUSS [MUST]**, sofern die Gruppe als Stufe 3 eingestuft ist, zusätzlich beide Stufe-3-Pflichten aus `spec/claude/research-plan-implement/` §"Die Phasentiefe skaliert mit dem Blast Radius" erfüllen: die Designfrage — **wo** die Änderung landet — als ausdrückliche, operatorseitige Entscheidung klären, bevor der Plan das **Wie** beschreibt, und nach der Umsetzung einen Verifikationsdurchgang durch einen Kontext ausführen lassen, der die Änderung nicht erzeugt hat
- **MUSS [MUST]**, sofern die Gruppe als Stufe 3 eingestuft ist, den Plan gemäß `spec/claude/research-plan-implement/` §"Der Plan ist die Review-Oberfläche" in unabhängig verifizierbare Scheiben zerlegen, damit die Verifikation an Scheibengrenzen stattfindet statt erst am fertigen Bündel. Die Mitgliedsreihenfolge (§F) ist die natürliche Scheibengrenze: Ein Mitglied, dessen deklarierte Prüfungen grün sind, ist eine verifizierte Scheibe
- **MUSS [MUST]** die Research-Befunde und den Plan der Gruppe als ein einziges Artefakt unter `.audits/issue-batch-integration/<group-id>/analysis.md` persistieren, das trägt: die Gruppen-Id, die Frage, auf die die Research-Phase gescoped war, die logische Änderung in einem Satz (§A), die Mitgliedstabelle (Issue, Klasse, aufnehmendes Prädikat, Beleg), die mitgliedsübergreifende Abhängigkeitsordnung, die geteilte Berührungsfläche, die Modus-Entscheidung mit Begründung (§C), die untenstehende Vollständigkeitsmatrix, die Risiken, die Grenze dessen, was diese Gruppe bewusst außerhalb des Scopes lässt, und die offenen Fragen an den Operator
- **MUSS [MUST]** jede tragende Behauptung in den Befunden an eine `file:line`, einen Pfad oder ein Kommando samt Ausgabe verankern, gemäß `spec/claude/research-plan-implement/` §"Research ist isoliert und verankert"
- **SOLLTE [SHOULD]** die Research der Gruppe in einem isolierten Kontext ausführen — ein dispatchter Reviewer-Agent, ein Subagent oder eine eigene Session —, der eine verdichtete Zusammenfassung zurückgibt statt seines Explorationsprotokolls, gemäß `spec/claude/research-plan-implement/` §"Research ist isoliert und verankert", damit der Kontext, der die Gruppe umsetzt, die Suche über alle Mitglieder hinweg nicht mitbezahlt
- **MUSS [MUST]** das Artefakt eigenständig lesbar halten, ohne das Gespräch, das es hervorgebracht hat, gemäß `spec/claude/research-plan-implement/` §"Der Plan ist die Review-Oberfläche"; das Artefakt ist der Übergabevertrag, aus dem ein zweiter Operator die Gruppe wieder aufnimmt
- **MUSS NICHT [MUST NOT]** während laufender Research- oder Plan-Phase irgendeinen Teil der Gruppenänderung schreiben, gemäß `spec/claude/research-plan-implement/` §"Phasendefinitionen und die Schreibgrenze". Das **Write-Gate** der Gruppe ist die Operator-Freigabe dieses Artefakts: Das Artefakt selbst ist ein zulässiger Schreibvorgang davor, und die erste versionierte Änderung an den Dateien eines Mitglieds ist der erste Schreibvorgang danach
- **MUSS [MUST]** eine **Vollständigkeitsmatrix** führen, deren Zeilen die Mitglieds-Issues und deren Spalten die Artefaktklassen sind, die das Repository tatsächlich ausliefert — mindestens Quellcode, Spec, Tests, Dokumentation, Konfiguration und Workflows sowie generierte Indizes oder Kataloge. Jede Zelle **MUSS [MUST]** entweder die benannte Änderung oder ein ausdrückliches `nicht zutreffend` samt Begründung enthalten. Eine leere Zelle ist ein unvollständiger Plan, kein stillschweigendes "hier ist nichts zu tun"; die Matrix ist es, die "jede relevante Anpassung hat stattgefunden" prüfbar statt behauptet macht, und sie ist die Form, die `spec/claude/research-plan-implement/` §"Der Plan ist die Review-Oberfläche" ohnehin verlangt
- **MUSS [MUST]** den Spaltensatz aus dem zu ändernden Repository ableiten statt aus einer festen Liste, damit ein Repository ohne Tests keine leere Spalte mitschleppt und eines mit generiertem Katalog diesen nicht stillschweigend auslässt
- **MUSS [MUST]** jeder Matrixzelle, die eine Änderung enthält, die Prüfung beigeben, die sie belegt, gemäß `spec/claude/research-plan-implement/` §"Verifikation gehört in den Plan"
- **MUSS [MUST]** die Freigabe des Artefakts durch den Operator einholen, bevor das erste Mitglied umgesetzt wird; die Umsetzung gegen einen nicht freigegebenen Gruppenplan ist verboten
- **MUSS [MUST]** die Aufnahme eines weiteren Mitglieds nach der Plan-Freigabe als strukturelle Regression behandeln, nicht als Nachtrag: Der Plan kehrt zu Plan zurück, die Matrix wird neu berechnet, und der Operator gibt erneut frei
- **MUSS [MUST]** das Artefakt genauso lauf-gebunden behandeln, wie `issue-orchestration` §"Lebenszyklus des Voranalyse-Artefakts (transient)" es mit seinem eigenen hält: auf dem Integrationsbranch committet, per fix-forward `git rm` entfernt, sobald jedes Mitglied umgesetzt und das Gate grün ist, niemals auf dem Default-Branch und niemals hinter einem `.gitignore`-Eintrag verborgen. Schreibt ein delegierter Mitgliedslauf sein eigenes `.audits/issue-orchestrate/<n>/analysis.md` auf denselben Branch, werden beide vor dem Merge des Bündels entfernt
- **MUSS NICHT [MUST NOT]** die Zerlegung eines Mitglieds im Gruppen-Artefakt wiederholen; das Gruppen-Artefakt hält die Gruppen-Schicht fest, und die Work-Packages des Mitglieds bleiben beim delegierten Lauf

### E. Strukturbefunde und Prozess-Rückkopplung

- **MUSS [MUST]** die Gruppe **über ihre Mitglieder hinweg** auf eine strukturelle Ursache untersuchen, bevor der Plan geschrieben wird, und das Ergebnis im Gruppen-Artefakt festhalten. Eine Gruppe ist konstruktionsbedingt eine Menge von Issues, die bereits eine Kopplung teilen, und damit der erste Korpus, in dem ein Muster sichtbar wird, das kein einzelnes Issue zeigt; jedes Mitglied nur isoliert zu analysieren wirft genau diesen Beleg weg
- **MUSS [MUST]** ein **Symptom-Cluster** (mehrere Issues, eine Grundursache) von einem **Klassen-Cluster** (mehrere Issues einer wiederkehrenden Defektklasse) unterscheiden und festhalten, welches von beiden die Gruppe ist. Ist die Gruppe ein Symptom-Cluster, **MUSS [MUST]** der Plan die Grundursache adressieren, statt `n` Symptome zu reparieren
- **MUSS [MUST]**, sofern die Gruppe ein Klassen-Cluster ist, die Klasse gemäß `spec/project/defect-class-guards/` §"Bindung in den Abschlussprozess" binden und ihren Sweep einmal auf Gruppenebene gemäß §G führen
- **MUSS [MUST]** jede wiederkehrende Finding-Klasse, die die Gruppe zutage fördert, in den Portfolio-Loop einspeisen, den `spec/project/continuous-improvement/` §"Portfoliolücken-Schließung (damit der Loop lebendig bleibt)" besitzt, samt Klasse und Rekurrenzzähler. Diese Spec **MUSS NICHT [MUST NOT]** den dortigen Rekurrenz-Schwellwert wiederholen oder neu herleiten: Die Gruppe liefert den Beleg, der Loop besitzt den Auslöser
- **MUSS [MUST]** einen **Prozessbefund** festhalten, wenn die strukturelle Ursache im Entwicklungsprozess sitzt statt in den geänderten Artefakten — eine Regel, die den Defekt zulässt, ein Gate, das ihn nicht fängt, eine Prüfung, die es nicht gibt — und ihn **MUSS [MUST]** als eigenes Issue gegen die maßgebliche Spec oder das maßgebliche Gate anlegen, mit Verweis auf die Gruppen-Id. Ein Prozessbefund **MUSS NICHT [MUST NOT]** als erledigt gelten, sobald die Mitglieder der Gruppe repariert sind, denn deren Reparatur lässt den Prozess, der sie hervorgebracht hat, unberührt
- **MUSS [MUST]** zu jedem Prozessbefund die konkrete vorbeugende Änderung benennen: die Regel, den Guard oder die Prüfung, die das Entstehen der Gruppe verhindert hätte. Ein Prozessbefund ohne benannte vorbeugende Änderung ist eine Beobachtung, kein Befund, und wird nicht als solcher angelegt
- **SOLLTE [SHOULD]** ausdrücklich festhalten, wenn keine strukturelle Ursache gefunden wurde, damit ihr Fehlen eine Aussage ist, die der Operator anfechten kann, statt einer stillen Auslassung

### F. Delegation je Mitglied

- **MUSS [MUST]** Erfassung, Klassifikation, Anforderungs-Gate, Zerlegung und Spezialisten-Dispatch jedes Mitglieds an `issue-orchestration` delegieren und **MUSS NICHT [MUST NOT]** eines davon hier neu herleiten
- **MUSS [MUST]** die Übergabegrenze gemäß `spec/claude/research-plan-implement/` §"Bindung für Skill- und Agent-Autorenschaft" benennen: Die Gruppen-Schicht besitzt Research, Plan und die Mitgliedsreihenfolge; der delegierte Lauf besitzt die Implement-Phase seines Mitglieds samt Verifikation und **MUSS NICHT [MUST NOT]** einen Pull Request eröffnen oder mergen
- **MUSS [MUST]** Mitglieder in der Abhängigkeitsreihenfolge umsetzen, die das Artefakt festhält, und **MUSS [MUST]** das Ergebnis jedes Mitglieds festhalten, bevor ein abhängiges Mitglied startet
- **MUSS [MUST]** jede Prüfung ausführen, die die Vollständigkeitsmatrix für ein Mitglied deklariert, und die **tatsächliche Ausgabe** der Prüfung festhalten statt der Behauptung, sie sei bestanden, gemäß `spec/claude/research-plan-implement/` §"Verifikation gehört in den Plan". Ein festgehaltenes Bestehen, dessen Prüfung nie lief, ist schlimmer als gar kein Eintrag, weil es sich wie ein Beleg liest
- **MUSS [MUST]** `quality-gate` gegen den **Kopf des Integrationsbranches** laufen lassen, bevor der Bündel-Pull-Request aufgeht. Ein grünes Gate auf einem Mitglieds-Sub-Branch ist kein Beleg für das Bündel, aus demselben Grund, den `parallel-working-copies` §"Zusammenspiel mit anderen Portfolio-Specs" nennt: Ein grünes Gate in einem anderen Worktree ist kein Beleg für diesen

### G. Bündelung und Integration

- **MUSS [MUST]** `develop` als genau ein Pull Request erreichen, eröffnet vom Integrationsbranch und `pull-request-workflow` vollständig erfüllend; der Typ im Titel entspricht dem Präfix des Integrationsbranches
- **MUSS [MUST]** jedes Mitglied unter `## Linked issues` mit dem Closing-Keyword des Repositories aufführen und **MUSS [MUST]** in **Risk / rollout notes** festhalten: die Gruppen-Id, das aufnehmende Prädikat je Mitglied, den Modus samt Begründung sowie je Mitglied den dispatchten Spezialisten oder den ausdrücklichen Kein-passender-Spezialist-Vermerk, den `issue-orchestration` §"Verifikation und Nachvollziehbarkeit" je Issue ohnehin verlangt
- **MUSS [MUST]**, sofern der Typ des Bündels `fix` ist, genau **einen** `## Class sweep`-Abschnitt führen, der die Defektklasse der Gruppe als Ganzes abdeckt, gemäß `pull-request-workflow` §"Klassen-Sweep (Conventional-Commits-Typ `fix`)". Eine über thematische Kopplung einer Defektklasse gebildete Gruppe hat konstruktionsbedingt ein Prädikat; ein Sweep je Mitglied würde es `n`-mal wiederholen und nichts zusätzlich messen
- **MUSS [MUST]** jedes transiente Artefakt (§D) vor dem Merge des Bündels entfernen, sodass die dauerhafte Spur der Pull-Request-Body plus die Kommentare an den Issues sind
- **MUSS [MUST]**, wenn ein Mitglied nach Eröffnung des Bündel-Pull-Requests herausgelöst werden muss, dessen Änderungen vom Integrationsbranch entfernen — in Modus B durch Fallenlassen seines Merges — und sowohl Artefakt als auch Pull-Request-Body aktualisieren, oder das Bündel schließen und neu gruppieren; ein Bündel **MUSS NICHT [MUST NOT]** mergen, solange es ein Mitglied behauptet, das es nicht mehr trägt
- **MUSS NICHT [MUST NOT]** das Bündel selbst mergen; der Gruppenprozess endet bei einem offenen, auditierbaren Pull Request und übergibt den Merge an `pull-request-merge`

### H. Abschluss

- **MUSS [MUST]** jedes Mitglieds-Issue schließen, nachdem der Squash-Commit des Bündels auf `develop` gelandet ist, mit ausdrücklicher Operator-Bestätigung. `pull-request-workflow` §"Schließen verlinkter Issues beim develop-Merge" stellt fest, dass das Closing-Keyword bei einem `develop`-Merge nicht auslöst; die Schließung ist damit eine Handlung dieses Prozesses und kein Nebeneffekt der Plattform
- **MUSS [MUST]** in jedem Schließungskommentar den Bündel-Pull-Request, den Merge-Commit-SHA auf `develop` und die Gruppen-Id nennen, sodass ein Mitglieds-Issue zurück zum Bündel führt, das es aufgelöst hat
- **MUSS NICHT [MUST NOT]** ein Mitglied schließen, das aus der Gruppe herausgelöst wurde
- **MUSS [MUST]** den Integrationsbranch samt Worktree nach dem Merge zurückbauen, gemäß `parallel-working-copies` §"Lebenszyklus: Stilllegen"

### I. Wiederaufnahme und Operator-Gating

- **MUSS [MUST]** gemäß `spec/claude/resumable-work/` wiederaufnehmbar sein, mit Checkpoints an jeder Phasengrenze — aufnehmen, analysieren, planen, Mitglied umsetzen, bündeln, schließen —, wie `spec/claude/research-plan-implement/` §"Bindung für Skill- und Agent-Autorenschaft" es mindestens verlangt
- **MUSS [MUST]** jede nach außen sichtbare Handlung auf eine Operator-Bestätigung stützen: das Schreiben des Artefakts, die Modus-Entscheidung, jeden Mitglieds-Dispatch, den Bündel-Pull-Request und jede Issue-Schließung

## Akzeptanzkriterien

- [ ] Jedes Mitglied in einem Gruppen-Artefakt hält genau ein aufnehmendes Prädikat aus der geschlossenen Dreiermenge samt Beleg fest, und kein Mitglied wurde über ein gemeinsames Zeitfenster aufgenommen
- [ ] Das Gruppen-Artefakt formuliert die logische Änderung der Gruppe in einem Satz
- [ ] Das Gruppen-Artefakt hält eine Stufe von 2 oder höher fest sowie eine Operator-Freigabe, die vor der Umsetzung des ersten Mitglieds erfolgt ist
- [ ] Die Vollständigkeitsmatrix führt eine Zeile je Mitglied und eine Spalte je ausgelieferter Artefaktklasse des Repositories, keine Zelle ist leer, und jede Zelle mit einer Änderung benennt die Prüfung, die sie belegt
- [ ] Jedes Gruppen-Artefakt hält entweder einen Strukturbefund über seine Mitglieder hinweg fest oder die ausdrückliche Aussage, dass keiner gefunden wurde
- [ ] Jedes Gruppen-Artefakt hält fest, ob die Gruppe ein Symptom-Cluster oder ein Klassen-Cluster ist, und der Plan jedes Symptom-Clusters adressiert die Grundursache statt `n` Symptomreparaturen
- [ ] Jeder Prozessbefund benennt seine vorbeugende Änderung (eine Regel, einen Guard oder eine Prüfung) und existiert als eigenes Issue mit Verweis auf die Gruppen-Id; keiner wurde allein durch die Reparatur der Gruppenmitglieder als erledigt behandelt
- [ ] Jede wiederkehrende Finding-Klasse, die eine Gruppe zutage gefördert hat, hat den `continuous-improvement`-Loop samt Rekurrenzzähler erreicht, und kein Gruppen-Artefakt wiederholt den dortigen Rekurrenz-Schwellwert
- [ ] Jedes Gruppen-Artefakt nennt die Frage, auf die seine Research-Phase gescoped war, sowie die Grenze dessen, was die Gruppe außerhalb des Scopes lässt
- [ ] Jedes Gruppen-Artefakt ist ohne das Gespräch, das es hervorgebracht hat, lesbar, und an den versionierten Dateien keines Mitglieds wurde etwas geändert, bevor der Operator das Artefakt freigegeben hat
- [ ] Bei jeder Gruppe der Stufe 3 hält das Artefakt die Designentscheidung fest, die vor der Wie-Beschreibung des Plans getroffen wurde, benennt die unabhängig verifizierbaren Scheiben des Plans und trägt einen Verifikationsdurchgang durch einen Kontext, der die Änderung nicht erzeugt hat
- [ ] Jede in einem Gruppen-Artefakt festgehaltene Mitgliedsprüfung trägt die tatsächliche Ausgabe der Prüfung statt der Behauptung, sie sei bestanden
- [ ] Jede Abweichung, die während der Umsetzung der Mitglieder auftrat, ist entweder als lokale Anpassung oder als strukturelle Regression festgehalten, die die Gruppe zur erneuten Freigabe nach Plan zurückgeführt hat
- [ ] Das Präfix des Integrationsbranches entspricht dem Conventional-Commits-Typ im Titel des Bündel-Pull-Requests und ist nur dann `exp/`, wenn die Gruppe explorativ ist
- [ ] Kein Pull Request im Repository hat eine andere Basis als `develop` (`gh pr list --state all --json baseRefName`), es wurde also kein gruppeninterner Pull Request eröffnet
- [ ] Bei jeder Modus-B-Gruppe wurde jeder Mitglieds-Sub-Branch in den Integrationsbranch gemergt und trägt keinen eigenen Pull Request
- [ ] Jedes Gruppen-Artefakt hält seinen Modus mit Begründung fest, und keine Modus-A-Gruppe führt ein als herauslösbar markiertes Mitglied
- [ ] Jedes herausgelöste Mitglied ist als in die Einzelabarbeitung zurückgegeben festgehalten und ist nicht geschlossen
- [ ] Der Baum des Default-Branches trägt keinen Pfad `.audits/issue-batch-integration/` (`git ls-tree -r --name-only develop -- .audits/issue-batch-integration/` ist leer), und kein von ihm erreichbarer Commit legt einen an
- [ ] Der Integrationsbranch trägt sowohl den Erzeugungs- als auch den Entfernungs-Commit des Artefakts, die Entfernung liegt nach dem letzten Mitgliedsergebnis, und `.gitignore` trägt keinen Eintrag `.audits/issue-batch-integration/`
- [ ] Die **Risk / rollout notes** des Bündel-Pull-Requests nennen die Gruppen-Id, das aufnehmende Prädikat je Mitglied, den Modus samt Begründung und je Mitglied den dispatchten Spezialisten oder den ausdrücklichen Kein-passender-Spezialist-Vermerk
- [ ] Ein Bündel vom Typ `fix` trägt genau einen `## Class sweep`-Abschnitt, dessen `Predicate` tatsächlich ausgeführt wurde
- [ ] `quality-gate` meldete Grün auf dem Kopf des Integrationsbranches, bevor der Bündel-Pull-Request aufging, und dieses Ergebnis wurde nicht von einem Mitglieds-Sub-Branch geerbt
- [ ] Jedes Mitglieds-Issue wurde nach dem `develop`-Merge mit einem Kommentar geschlossen, der den Bündel-Pull-Request, den Merge-Commit-SHA und die Gruppen-Id nennt; keines wurde stillschweigend vom Autolink der Plattform geschlossen
- [ ] Nach dem Merge erwähnen weder `git worktree list` noch `git branch --list` den Integrationsbranch oder einen Mitglieds-Sub-Branch
- [ ] Der Checkpoint unter `.resume/` hält einen Entscheidungseintrag für jedes Gate fest: das Schreiben des Artefakts, die Modus-Entscheidung, jeden Mitglieds-Dispatch, den Bündel-Pull-Request und jede Issue-Schließung
- [ ] Jedes Mitglied, dessen Issue eine Ursache behauptet, hat diese Ursache vor seiner ersten getrackten Änderung gegen den Code verifiziert und im Gruppen-Artefakt festgehalten, und einer widerlegten Ursache folgt die Messung statt des Issue-Texts

## Offene Fragen

- Ob eine Gruppe zusätzlich zum Herauslösbarkeits-Kriterium (§C) einen Größen-Backstop braucht, bleibt offen. Herauslösbarkeit benennt die Eigenschaft, die Modus B tatsächlich einbringt; eine Mitgliederzahl wäre ein Näherungsmaß, dessen Schwelle bislang kein Lauf kalibriert hat. **Auslöser zur Wiedervorlage:** eine dokumentierte Gruppe, deren Modus-A-Strang unreviewbar wurde, obwohl kein Mitglied herauslösbar war.
- §B nimmt das Review-Gate je Mitglied heraus, indem es gruppeninterne Pull Requests verbietet; das hält den Prozess mit `pull-request-workflow` §"PR-Rahmenbedingungen" konsistent, um den Preis, jedes Mitglied nur im Bündel zu reviewen. Ob dafür ein Ausgleichsmechanismus nötig ist — ein Review-Durchgang je Mitglied innerhalb des Bündels oder eine erklärte Ausnahme in `pull-request-workflow` —, bleibt offen, bis ein Bündel dokumentiert ist, in dem ein Mitgliedsdefekt das gemeinsame Review überlebt hat.
- Ob das Gruppen-Artefakt standardmäßig in jedes Mitglieds-Issue gespiegelt werden sollte statt nur auf Operator-Bestätigung, bleibt bis zu einer Operator-Präferenz aus echten Läufen offen.
