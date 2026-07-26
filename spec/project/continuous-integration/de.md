# Continuous-Integration-Pipeline-Design

Status: draft
Portfolio-Scope: portfolio

## Kontext

Jedes Repository dieses Portfolios betreibt eine Pre-Merge-Pipeline, und die benachbarten Specs besitzen jeweils ein Stück davon. `spec/project/branching-model/` legt fest, **welche** Workflows existieren müssen. `spec/project/project-structure/` legt fest, **wo** sie liegen und wie ihre Reusable-Referenzen gepinnt werden. `spec/project/pull-request-workflow/` legt fest, **was** einen Merge nach `develop` gated. `spec/project/quality-gate/` legt den Lint-, Typecheck- und Test-Vertrag fest, und `spec/project/taskfile/` legt das Target-Vokabular fest, über das dieser Vertrag aufgerufen wird — einschließlich der Regel zur Parität von lokalem Lauf und CI. `spec/project/workflow-health/` legt den **operativen** Prozess fest, der diese Workflows grün hält und sie triagiert, wenn sie rot werden.

Was keine Spec festlegt, ist das **Design** der Pipeline selbst: welche Stufen es gibt, in welcher Reihenfolge sie laufen, was jede Stufe über die vorangehenden Stufen annehmen darf und welche Eigenschaften die Anordnung als Ganzes bewahren muss. Wer heute eine Pipeline aufsetzt oder umbaut, rekonstruiert diese Konvention aus sechs Dokumenten und füllt die verbleibenden Lücken, indem er das Repository kopiert, das am ähnlichsten aussieht. Das Ergebnis driftet: Die Stufenreihenfolge unterscheidet sich, Caching wird angeflanscht, bis der Lauf schnell genug ist, und niemand kann sagen, ob ein grüner Lauf in zwei Repositories dasselbe bedeutet.

Diese Spec besitzt diese Design-Disziplin für die **Pre-Merge**-Hälfte der Pipeline. Ihr Geschwister `spec/project/continuous-delivery/` besitzt die Post-Merge-Hälfte, und `spec/project/github-actions-best-practices/` bindet beide an die eine Plattform, die dieses Portfolio betreibt. Zwei Eigenschaften sind durchgängig tragend und werden als Invarianten formuliert, nicht als Absichtserklärungen:

- **Reproduzierbarkeit.** Ein Pipeline-Lauf ist eine Aussage über einen Commit. Wenn derselbe Commit einen grünen und einen roten Lauf erzeugen kann, je nachdem wann er lief, was ein Cache enthielt oder welche gleitende Version aufgelöst wurde, ist die Aussage wertlos. Jede Regel zu Pinning, Cache-Entwurf und Stufen-Isolation existiert, um dies zu schützen.
- **Wiederverwendung statt Kopieren.** Eine Regel, die einmal implementiert und von jedem Repository geerbt wird, kann nicht driften; eine Regel, die in zwanzig Repositories kopiert wurde, wird es. Diese Spec schiebt geteilte Mechanik in das Reusable-Workflow-Repository des Portfolios statt in jeden Consumer.

Pipeline-**Effizienz** — Laufzeit, Cache-Trefferquote, Feedback-Latenz — wird durchgängig als Richtwert behandelt, nie als Gate. Schnelles Feedback wird durch die Reihenfolge der Stufen entworfen, nicht durch einen Schwellenwert erzwungen, denn kein portfolioweiter Schwellenwert würde den Kontakt mit Repositories dieser Bandbreite überstehen.

**Leser:** Beitragende und KI-Agenten, die die Pre-Merge-Pipeline eines Repositories aufsetzen oder umbauen, Reviewer, die die Tragfähigkeit einer Pipeline-Änderung beurteilen, sowie die Autoren des Skills `cicd-pipeline-design` und des Agents `cicd-pipeline-reviewer`, die diese Spec operationalisieren.

## Ziele

- Die Stufen einer Pre-Merge-Pipeline, ihre Reihenfolge und ihre Vorbedingungen sind einmal festgelegt, sodass zwei Repositories, die beide grün melden, damit dasselbe meinen
- Ein Pipeline-Lauf ist reproduzierbar: Derselbe Commit liefert dasselbe Urteil, und kein Cache, keine gleitende Referenz und kein Umgebungszustand des Runners kann das ändern
- Feedback ist schnell, weil billige und breit informative Stufen zuerst laufen, nicht weil teure Stufen entfallen sind
- Jede Stufe, die auch lokal ausführbar ist, wird über denselben Einstiegspunkt aufgerufen, sodass lokales Gate und CI-Gate nicht auseinanderlaufen können
- Geteilte Pipeline-Mechanik liegt in einer Implementierung statt in Kopien pro Repository
- Die Supply-Chain-Pflichten der Pipeline (Abhängigkeits-, Lizenz- und Code-Security-Prüfung) haben einen festgelegten Platz in der Stufenfolge, statt als unverbundene Workflows zu existieren

## Nicht-Ziele

- **Welche** Workflows ein Repository enthalten muss und wie ihre Reusable-Referenzen gepinnt werden — im Besitz von `spec/project/branching-model/` §Erforderliche GitHub-Workflows und `spec/project/project-structure/`
- Der **Betrieb** einer Pipeline über die Zeit: Triage roter Läufe, Flake-Klassifikation, Upstream-Drift, Rerun-Politik — im Besitz von `spec/project/workflow-health/`
- Zusammensetzung und Ausgabevertrag des Lint-, Typecheck- und Test-Gates selbst — im Besitz von `spec/project/quality-gate/`; diese Spec platziert dieses Gate in der Stufenfolge und wiederholt seinen Inhalt nicht
- Das Taskfile-Target-Vokabular und die Namensräume — im Besitz von `spec/project/taskfile/`; diese Spec stützt sich auf die dort festgelegte Paritätsregel und definiert sie nicht neu
- Was die Tests selbst prüfen, wie sie geschrieben werden und wie eine Testsuite geformt ist — im Besitz von `spec/project/test-pyramid-foundation/`, den `test-tier-*`-Specs und `spec/project/test-falsifiability/`
- Branch-Schutz, Deklaration erforderlicher Status-Checks und Merge-Mechanik — im Besitz von `spec/project/pull-request-workflow/`
- Alles nach dem Merge: Artefakt-Veröffentlichung, Provenienz, Release-Dispatch, Rollback — im Besitz von `spec/project/continuous-delivery/`
- Plattformspezifische Syntax und Mechanik. Diese Spec ist werkzeugunabhängig; `spec/project/github-actions-best-practices/` ist die einzige konkrete Bindung

## Anforderungen

### A. Stufenfolge

- **MUSS** die Pre-Merge-Pipeline als geordnete Folge benannter Stufen strukturieren, jede mit einer festgelegten Vorbedingung an die vorangehenden Stufen. Die kanonische Folge ist:
  1. **checkout**: den exakten zu prüfenden Commit beziehen, mit der Fetch-Tiefe, die die späteren Stufen tatsächlich brauchen
  2. **provision**: die Toolchain installieren und Abhängigkeiten aus gepinnten Eingaben auflösen (§C)
  3. **statische Analyse**: die Lint- und Typecheck-Kategorien, deren Zusammensetzung `spec/project/quality-gate/` besitzt
  4. **test**: die Test-Tiers in aufsteigender Kostenordnung (§E)
  5. **package**: das Build-Artefakt erzeugen, das der Commit ausliefern würde (§F)
  6. **Supply-Chain-Prüfung**: Abhängigkeits-Schwachstellen, Lizenzpolitik und Code-Security-Review (§G)
- **MUSS** einem Repository erlauben, eine nicht zutreffende Stufe wegzulassen (etwa **package** in einem Repository, das kein Build-Artefakt ausliefert), und **MUSS** verlangen, dass die Auslassung in der Pipeline-Definition sichtbar ist, statt kommentarlos zu fehlen
- **DARF NICHT** **checkout** oder **provision** umsortieren; jede spätere Stufe hängt von ihnen ab
- **SOLLTE** **statische Analyse** und **test** als getrennt gemeldete Einheiten führen statt als einen aggregierten Schritt, sodass ein roter Lauf die Problemklasse benennt, ohne dass man das Log öffnen muss
- **KANN** unabhängige Stufen nebenläufig ausführen, solange keine Vorbedingung verletzt wird; Nebenläufigkeit ist eine Effizienzentscheidung und **DARF NICHT** dazu dienen, eine Vorbedingung zu überspringen

### B. Schnelles Feedback und Fehlerverhalten

- **MUSS** die Stufen so ordnen, dass die billigste Stufe mit der breitesten Fehlerabdeckung zuerst läuft: Ein Lint-Fehler, der in Sekunden erkennbar ist, **DARF NICHT** erst nach einer mehrminütigen Testsuite gemeldet werden
- **MUSS** den Pipeline-Lauf fehlschlagen lassen, wenn irgendeine Stufe fehlschlägt, und **DARF NICHT** einen Lauf als erfolgreich ausweisen, während eine enthaltene Stufe Fehlschlag gemeldet hat
- **DARF NICHT** über einen Continue-on-Error-Ausweg verhindern, dass eine erforderliche Stufe den Lauf fehlschlagen lässt. Ist eine Stufe wirklich beratend, **MUSS** sie als nicht erforderlicher Check deklariert werden statt als erforderlicher Check, der nicht fehlschlagen kann — eine beratende Stufe, die unabhängig von ihrem Ergebnis Erfolg meldet, ist von einer Stufe, die gar nicht läuft, nicht unterscheidbar
- **SOLLTE** die übrigen unabhängigen Stufen nach dem ersten Fehlschlag zu Ende laufen lassen, statt den gesamten Lauf abzubrechen, sodass ein Lauf jede Problemklasse zeigt statt ein Problem pro Push
- **SOLLTE** die Pipeline-Laufzeit als Design-Eingabe behandeln, die bei jeder Pipeline-Änderung geprüft wird, und **DARF NICHT** einen portfolioweiten Laufzeit-Schwellenwert als Merge-Gate festlegen
- **DARF NICHT** eine langsame Pipeline dadurch beheben, dass eine Stufe aus dem erforderlichen Satz entfernt wird; das Mittel ist, die Stufe billiger zu machen, sie nebenläufig auszuführen oder ihren Umfang einzugrenzen, und jede Reduktion der Abdeckung ist eine prüfpflichtige Änderung, keine Performance-Korrektur

### C. Reproduzierbarkeit der Eingaben

- **MUSS** jede externe Eingabe der Pipeline aus einer gepinnten Referenz auflösen: die Toolchain-Version, den Abhängigkeitssatz, das Container-Basis-Image und jede wiederverwendete Pipeline-Komponente. Eine gleitende Referenz (ein wandernder Branch, ein bloßes `latest`, ein unbegrenzter Versionsbereich) **DARF NICHT** in einer Pipeline-Definition auftauchen
- **MUSS** Abhängigkeiten aus einer eingecheckten Lock-Datei auflösen, wo das Ökosystem eine bereitstellt, sodass der Abhängigkeitssatz eine Eigenschaft des Commits ist und nicht des Zeitpunkts, zu dem die Pipeline lief
- **MUSS** eine gepinnte Referenz als prüfpflichtiges Artefakt behandeln: Sie anzuheben ist eine Änderung, die dasselbe Gate passiert wie jede andere Änderung, gemäß `spec/project/pull-request-workflow/`
- **DARF NICHT** zulassen, dass die Pipeline den Arbeitsbaum so verändert, dass sich ändert, was eine spätere Stufe sieht, ohne dass diese Veränderung eine ausdrückliche, benannte Stufe ist; ein impliziter Schreibvorgang ist für den Leser unsichtbar und bei einem erneuten Lauf nicht reproduzierbar
- **SOLLTE** jede Stufe unabhängig vom Umgebungszustand des Runners halten — Dateien in einem Home-Verzeichnis, global installierte Werkzeuge oder Umgebungsvariablen aus einem früheren, unabhängigen Lauf — sodass das Ergebnis einer Stufe nur von ihren deklarierten Eingaben abhängt
- **SOLLTE** für jeden grünen Lauf erklären können, welche gepinnten Eingaben ihn erzeugt haben, sodass ein späterer roter Lauf auf demselben Commit einer Eingabeänderung zurechenbar ist und nicht dem Zufall

### D. Caching, ohne ein Ergebnis zu verändern

Caching ist die häufigste Stelle, an der eine Pipeline versehentlich Reproduzierbarkeit gegen Geschwindigkeit tauscht. Die folgenden Regeln ziehen die Grenze.

- **MUSS** einen Cache strikt als **Beschleuniger** behandeln: Ein Lauf mit kaltem Cache und ein Lauf mit warmem Cache **MÜSSEN** auf demselben Commit dasselbe Urteil erreichen. Ein Cache, der ein Ergebnis verändern kann, ist ein Korrektheitsdefekt, kein Optimierungsproblem
- **MUSS** einen Cache-Schlüssel aus dem Inhalt ableiten, der die zwischengespeicherten Daten bestimmt — typischerweise die Lock-Datei, die Toolchain-Version und die Plattform — sodass eine Änderung an einem davon einen anderen Schlüssel ergibt statt eines veralteten Treffers
- **DARF NICHT** zwischenspeichern, was die Pipeline erzeugen und prüfen soll. Build-Ausgaben und Testergebnisse sind die Aussagen der Pipeline über den Commit; sie aus einem früheren Lauf wiederherzustellen, ersetzt die Aussage durch die Behauptung, es habe sich nichts geändert
- **DARF NICHT** Anmeldedaten, Token oder sonstiges Geheimmaterial zwischenspeichern
- **SOLLTE** beim Entwurf von Rückfallschlüsseln einen Cache-Fehlschlag einem falschen Treffer vorziehen: Ein Präfix-Rückfall ist nur dann sicher, wenn ein veralteter Eintrag von der konsumierenden Stufe erkannt und korrigiert werden kann
- **SOLLTE** Caching vollständig abschalten können und dennoch einen korrekten (langsameren) Lauf erhalten; eine Pipeline, die nur mit warmem Cache besteht, ist nicht reproduzierbar

### E. Testausführung in der Pipeline

- **MUSS** die Test-Tiers in aufsteigender Kostenordnung ausführen, sodass der billigste Tier, der einen Defekt erkennen kann, zuerst meldet; die Tiers selbst und was jeder prüft, sind im Besitz von `spec/project/test-pyramid-foundation/` und den `test-tier-*`-Specs
- **MUSS** die Teststufe über das deklarierte Taskfile-Target des Repositories aufrufen, statt den Aufruf inline nachzubauen, gemäß der Paritätsregel in `spec/project/taskfile/` §Lokal- und CI-Parität
- **DARF NICHT** die Suite schwächen, um die Pipeline grün zu bekommen: Überspringen, Abwählen oder Markieren eines Falls als erwarteter Fehlschlag, um einen Merge freizumachen, ist unzulässig, und die No-Cheating-Invariante aus `spec/project/test-cycle-foundation/` und `spec/project/test-cycle-code-adaptation/` gilt vollumfänglich für jede unter Pipeline-Druck vorgenommene Änderung
- **MUSS** sicherstellen, dass eine Teststufe fehlschlagen kann. Eine Stufe, die Erfolg meldet, wenn kein Test lief, wenn die Suite nicht eingesammelt werden konnte oder wenn der Runner vor Abschluss der Suite beendet wurde, ist ein wirkungsloses Gate; die Pipeline **MUSS** eine leere oder nicht eingesammelte Suite als Fehlschlag behandeln, nicht als Erfolg
- **SOLLTE** Testdaten je Lauf isolieren, damit nebenläufige Pipeline-Läufe auf verschiedenen Commits einander nicht stören können; die Mechanik gehört den Tier-Specs, die Anforderung, dass die Pipeline sie nicht aushebelt, gehört hierher
- **KANN** einen Tier über eine Matrix aus Plattformen oder Versionen auffächern, wenn das Ergebnis des Tiers tatsächlich von dieser Achse abhängt, und **MUSS** jeden Matrix-Zweig als erforderlich behandeln, sofern der Zweig nicht gemäß §B als beratend deklariert ist

### F. Erzeugung des Kandidaten-Artefakts

- **MUSS** in einem Repository, das ein Build-Artefakt ausliefert, dieses Artefakt in der Pre-Merge-Pipeline aus dem zu prüfenden Commit bauen, sodass ein Merge nicht der erste Bauversuch ist
- **MUSS** das Artefakt aus derselben Definition bauen, die die Post-Merge-Pipeline verwendet, sodass der Pre-Merge-Build ein Beleg über das tatsächlich auszuliefernde Artefakt ist und nicht über einen parallelen Build-Pfad
- **DARF NICHT** das Pre-Merge-Artefakt an einen für Konsumenten sichtbaren Ort veröffentlichen; Veröffentlichung ist Post-Merge und gehört zu `spec/project/continuous-delivery/`. Der Pre-Merge-Build weist nach, dass der Commit baut, und seine Ausgabe ist ein laufbezogenes Zwischenergebnis
- **SOLLTE** das Pre-Merge-Artefakt nur so lange aufbewahren, wie die Diagnose des Laufs es benötigt
- **SOLLTE NICHT** zulassen, dass etwas Nachgelagertes vom Pre-Merge-Artefakt abhängt
- Die Artefakt-Taxonomie je Projekttyp ist im Besitz von `spec/project/release-artifact/` und **DARF NICHT** hier wiederholt werden

### G. Supply-Chain-Stufen

- **MUSS** den Supply-Chain-Pflichten des Repositories eine festgelegte Position in der Stufenfolge geben, statt sie als von der Pipeline losgelöste Workflows zu belassen: Abhängigkeits-Schwachstellenprüfung (`spec/project/dependency-audit/`), Lizenzpolitik (`spec/project/license-check/`) und Code-Security-Review (`spec/project/code-security-audit/`)
- **MUSS** eine Supply-Chain-Stufe gegen den **aufgelösten** Abhängigkeitssatz des zu prüfenden Commits ausführen, nicht gegen die deklarierten Bereiche, sodass der Befund dem entspricht, was tatsächlich ausgeliefert würde
- **MUSS** die Schweregrad-Politik und die Reaktionsentscheidung bei der besitzenden Spec belassen; diese Spec platziert die Stufe und **DARF NICHT** festlegen, was ein Befund bedeutet oder wann er blockiert
- **KANN** eine Supply-Chain-Pflicht in einer Kadenz statt bei jedem Pull Request ausführen, wenn die besitzende Spec eine festlegt, und **MUSS** in diesem Fall die Kadenz im Repository sichtbar halten, statt sie in einem Zeitplan zu verstecken, den niemand liest
- **MUSS** für eine Pflicht, deren besitzende Spec weder eine Stufenposition noch eine Kadenz festlegt, eine festgehaltene Praxis außerhalb der Pipeline akzeptieren, die benennt, wann die Pflicht erfüllt wird. `spec/project/code-security-audit/` ist der aktuelle Fall: Es versteht sich als operatorgetriebener Durchgang über die gesamte Codebasis, diese Spec **DARF** daher **NICHT** eine Pipeline-Stufe verlangen, die jene nicht festlegt

### H. Wiederverwendung von Pipeline-Mechanik

- **MUSS** Pipeline-Mechanik, die über Repositories hinweg identisch ist, einmal im Reusable-Pipeline-Repository des Portfolios implementieren und über eine gepinnte Referenz konsumieren, statt sie in jedes Repository zu kopieren. Das ist dieselbe Regel, die `spec/project/pull-request-workflow/` bereits auf den Pull-Request-Linter anwendet, verallgemeinert auf die Pipeline
- **DARF NICHT** einen Defekt in geteilter Pipeline-Mechanik dadurch beheben, dass eine lokale Kopie in einem Consumer-Repository gepatcht wird; die Korrektur gehört in die geteilte Implementierung, damit jeder Consumer sie erhält. Ein Consumer-lokaler Umweg ist nur als dokumentierte Übergangsmaßnahme zulässig, die die Upstream-Änderung benennt, auf die sie wartet
- **SOLLTE** repository-spezifische Pipeline-Inhalte auf das beschränken, was sich wirklich unterscheidet: die Toolchain, die Zielmatrix und den eigenen Stufensatz des Repositories
- **SOLLTE** eine Regel, die in drei oder mehr Repositories kopiert wurde, als Kandidatin für die Auslagerung in die geteilte Implementierung behandeln

### I. Abgrenzung

- **DARF NICHT** eine Regel wiederholen, die `workflow-health`, `branching-model`, `project-structure`, `pull-request-workflow`, `quality-gate`, `taskfile`, `release-artifact` oder den Test-Specs gehört; wo diese Spec eine dieser Regeln braucht, referenziert sie sie
- **MUSS** einen roten Pipeline-Lauf zur Triage an `spec/project/workflow-health/` weiterreichen; diese Spec regelt, wie die Pipeline gebaut wird, nicht wie ein kaputter Lauf diagnostiziert wird
- **MUSS** an der Merge-Grenze an `spec/project/continuous-delivery/` übergeben; eine Stufe, die nach dem Merge läuft, gehört zu jener Spec, selbst wenn sie in derselben Datei definiert ist

## Akzeptanzkriterien

- [ ] Die Pipeline-Definition eines Repositories zeigt einen benannten, geordneten Stufensatz, der auf §A abbildet, wobei jede ausgelassene Stufe sichtbar ausgelassen ist statt kommentarlos zu fehlen
- [ ] Keine Pipeline-Definition im Repository enthält eine gleitende Referenz für Toolchain-Version, Abhängigkeitssatz, Basis-Image oder wiederverwendete Komponente
- [ ] Jede abhängigkeitsauflösende Stufe liest eine eingecheckte Lock-Datei, wo das Ökosystem eine bereitstellt
- [ ] Jeder Cache-Schlüssel der Pipeline enthält den Inhalt, der die zwischengespeicherten Daten bestimmt, und kein Cache speichert eine Build-Ausgabe, ein Testergebnis oder Geheimmaterial
- [ ] Das Abschalten des Caches erzeugt einen Lauf, der auf demselben Commit dasselbe Urteil erreicht wie der Lauf mit Cache
- [ ] Die Lint-, Typecheck- und Teststufen rufen die Taskfile-Targets des Repositories auf, statt die Befehle inline nachzubauen
- [ ] Keine erforderliche Stufe der Pipeline ist so konfiguriert, dass sie den Lauf nicht fehlschlagen lassen kann
- [ ] Eine Teststufe, die keine Tests einsammelt, meldet Fehlschlag statt Erfolg
- [ ] In einem Repository, das ein Build-Artefakt ausliefert, baut die Pre-Merge-Pipeline es aus derselben Definition, die die Post-Merge-Pipeline verwendet, und veröffentlicht es nirgends
- [ ] Dependency-Audit, License-Check und Code-Security-Review haben jeweils eine festgelegte Position in der Stufenfolge, eine festgelegte Kadenz oder eine im Repository festgehaltene Praxis außerhalb der Pipeline
- [ ] Über Repositories hinweg geteilte Pipeline-Mechanik wird über eine gepinnte Referenz aus der geteilten Implementierung konsumiert, ohne lokale Kopie eines geteilten Workflows
- [ ] Ein Abgleich der Spec mit `workflow-health`, `quality-gate`, `taskfile` und `branching-model` fördert keine wiederholte Regel zutage, nur Referenzen

## Referenzen

- `spec/project/quality-gate/`: der Lint-, Typecheck- und Test-Vertrag, den §E dieser Spec in die Folge einordnet
- `spec/project/taskfile/`: das kanonische Target-Vokabular und die Paritätsregel für lokalen Lauf und CI, auf die sich §E stützt
- `spec/project/test-pyramid-foundation/`, `spec/project/test-tier-static-analysis/`, `spec/project/test-tier-unit/`, `spec/project/test-tier-component/`, `spec/project/test-tier-integration/`, `spec/project/test-tier-contract/`: das Tier-Modell, das §E ausführt
- `spec/project/test-cycle-foundation/`, `spec/project/test-cycle-code-adaptation/`: die No-Cheating-Invariante, die §E unter Pipeline-Druck durchsetzt
- `spec/project/test-falsifiability/`: die Taxonomie von Anfang an schwacher Tests, gegen die die Regel aus §E zur wirkungslosen Stufe auf Pipeline-Ebene schützt
- `spec/project/dependency-audit/`, `spec/project/license-check/`, `spec/project/code-security-audit/`: die Supply-Chain-Pflichten, die §G platziert
- `spec/project/release-artifact/`: die Artefakt-Taxonomie, die §F ausdrücklich nicht wiederholt
- `spec/project/branching-model/`, `spec/project/project-structure/`, `spec/project/pull-request-workflow/`: welche Workflows existieren, wo sie liegen und was einen Merge gated
- `spec/project/workflow-health/`: das operative Gegenstück, an das diese Spec rote Läufe übergibt
- `spec/project/continuous-delivery/`: die Post-Merge-Hälfte der Pipeline
- `spec/project/github-actions-best-practices/`: die einzige konkrete Plattformbindung

## Offene Fragen

- Ob die geteilte Reusable-Pipeline-Implementierung eine vollständige, meinungsstarke Pipeline anbieten sollte, die ein Consumer konfiguriert, oder einen Satz komponierbarer Stufen-Bausteine, die ein Consumer zusammensetzt. Die Auslagerungsregel in §H gilt in beiden Fällen, aber die Gestalt der geteilten Implementierung ist nicht entschieden.
- §B verzichtet bewusst auf einen Laufzeit-Schwellenwert. Wird die Pipeline eines Repositories später langsam genug, um Merges zu behindern, gibt es keinen normativen Wert, auf den man sich berufen könnte, und das Mittel wäre eine Überarbeitung dieser Spec statt einer Ausnahme pro Repository. Ob ein beratendes portfolioweites Budget lohnt, sollte erneut geprüft werden, sobald genug Pipelines existieren, um eines zu kalibrieren.
- Die Regel aus §D, dass ein Lauf mit kaltem Cache dasselbe Urteil erreichen muss wie einer mit warmem Cache, ist als Invariante formuliert, aber kein Mechanismus prüft sie. Ob ein periodischer cachefreier Lauf als geplanter Check lohnt, ist ungeklärt.
