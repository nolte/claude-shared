# GitHub-Actions-Best-Practices

Status: draft
Portfolio-Scope: portfolio

## Kontext

`spec/project/continuous-integration/` und `spec/project/continuous-delivery/` legen die Pipeline-Disziplin dieses Portfolios fest, ohne eine Plattform zu benennen. Beide sind bewusst werkzeugunabhängig, und beide wären nicht prüfbar, wenn nichts sie an die eine Plattform bände, die hier tatsächlich jedes Repository betreibt. Diese Spec ist diese Bindung, und die einzige: GitHub Actions ist die einzige konkrete Plattform, die dieses Portfolio spezifiziert. Andere CI-Plattformen sind ein Nicht-Ziel, keine Auslassung.

Die Bindung muss zwei Dinge leisten, die die abstrakten Specs nicht können. Erstens sagt sie, wie eine plattformunabhängige Invariante in GitHub Actions konkret genug realisiert wird, um prüfbar zu sein: „Pinne jede externe Eingabe" wird zu einer Regel über Action- und Reusable-Workflow-Referenzen; „Reproduzierbarkeit" wird zu Regeln über Caches, Nebenläufigkeit und Runner-Annahmen. Zweitens deckt sie die Gefahren ab, die es nur gibt, weil diese Plattform so funktioniert, wie sie funktioniert — Token-Berechtigungen, die weiter voreingestellt sind, als ein Job braucht, Ausdrucks-Interpolation, die einen Pull-Request-Titel in Shell-Code verwandelt, und Auslöser, die dem Code eines Forks die Secrets des Repositories in die Hand geben.

Diese Gefahren sind nicht hypothetisch. Im März 2025 wurde die weit verbreitete Action `tj-actions/changed-files` kompromittiert, und ihre **bestehenden Versions-Tags wurden auf Schadcode umgebogen**; betroffene Repositories gaben daraufhin Secrets in ihren Lauf-Logs preis. Repositories, die die Action über einen Commit-Digest statt über ein Tag referenzierten, waren nicht betroffen [R4], [R5]. Die Regel, die aus diesem Vorfall folgt, steht in §A, und sie ist ein MUSS.

Diese Spec schreibt außerdem gegen eine Struktur, die das Portfolio bereits hat. `spec/project/branching-model/` §Erforderliche GitHub-Workflows legt fest, dass jedes Repository seine Release-Workflows an Reusable Workflows aus `nolte/gh-plumbing` bindet, und `spec/project/pull-request-workflow/` empfiehlt, auch den Pull-Request-Linter dort zu implementieren, „damit jedes Repository eine Implementierung erbt, statt lokale Kopien zu forken, die driften". Dieses bestehende Wiederverwendungsmodell ist die Form, die diese Spec verallgemeinert, kein paralleles Modell, das sie einführt.

**Leser:** Beitragende und KI-Agenten, die Workflow-Dateien in diesem Portfolio schreiben oder prüfen, sowie die Autoren des Skills `cicd-pipeline-design` und des Agents `cicd-pipeline-reviewer`, die diese Spec operationalisieren.

## Ziele

- Jede Workflow-Eingabe löst auf Inhalt auf, der sich dem Repository nicht unter den Füßen wegändern kann
- Ein Workflow-Job hält nur die Rechte, die er braucht, sodass ein kompromittierter Schritt den kleinstmöglichen Wirkungsradius hat
- Eingaben eines außenstehenden Beitragenden können weder zu ausführbarem Code werden noch einen privilegierten Kontext erreichen
- Anmeldedaten sind kurzlebig und eng gefasst, wo die Plattform das unterstützt, statt langlebiger Secrets, die ins Repository kopiert werden
- Über Repositories hinweg geteilte Workflow-Logik wird aus einer Implementierung geerbt, und eine Korrektur daran erreicht jeden Consumer
- Die Plattform-Mechanismen, die die Reproduzierbarkeit betreffen — Caching, Nebenläufigkeit, Runner-Zustand — werden so genutzt, dass sie das Urteil eines Laufs nicht verändern können

## Nicht-Ziele

- Das Pipeline-Design, das diese Regeln binden: Stufenfolge, Feedback-Ordnung, Auslieferungsgarantien, Rollback — im Besitz von `spec/project/continuous-integration/` und `spec/project/continuous-delivery/`
- Welche Workflows ein Repository enthalten muss und wie sich ein veröffentlichtes Release fortpflanzt — im Besitz von `spec/project/branching-model/`
- Wo Workflow-Dateien liegen und wie das Repository aufgesetzt wird — im Besitz von `spec/project/project-structure/`
- Erforderliche Status-Checks, Branch-Schutz und Merge-Mechanik — im Besitz von `spec/project/pull-request-workflow/`
- Triage eines roten Laufs, Flake-Klassifikation und die `GITHUB_TOKEN`-Ereigniskaskade — im Besitz von `spec/project/workflow-health/`
- Der Übergang vom Entwurf zum veröffentlichten Release — im Besitz von `spec/project/release-automation/`
- Jede andere CI-Plattform. Diese Spec ist die einzige konkrete Plattformbindung des Portfolios, und eine zweite Plattform bräuchte eine eigene Spec statt einer Erweiterung dieser
- Die Interna der `nolte/gh-plumbing`-Reusable-Workflows selbst; diese Spec regelt, wie ein Consumer-Repository sie konsumiert

## Anforderungen

### A. Pinning externer Referenzen

- **MUSS** jede Drittanbieter-Action über einen vollständigen Commit-Digest referenzieren statt über Tag oder Branch. GitHub stellt fest, dass das Pinnen auf einen vollständigen Commit-Digest „derzeit die einzige Möglichkeit ist, eine Action als unveränderliches Release zu nutzen" [R1], und die Kompromittierung von `tj-actions/changed-files` im März 2025 bog bestehende Tags auf Schadcode um, während Digest-gepinnte Consumer unbetroffen blieben [R4], [R5]
- **MUSS** eine Digest-gepinnte Referenz mit einem Kommentar versehen, der die zugehörige menschenlesbare Version benennt, sodass der Pin prüf- und aktualisierbar bleibt statt undurchsichtig
- **MUSS** vor dem Pinnen prüfen, dass ein gewählter Digest zum Repository der Action selbst gehört und nicht zu einem Fork [R1]
- **MUSS** jede Reusable-Workflow-Referenz auf eine unveränderliche Referenz pinnen statt auf einen wandernden Branch, gemäß `spec/project/branching-model/`, das für `nolte/gh-plumbing`-Referenzen bereits ein Tag verlangt und die Anhebungskadenz über `spec/project/workflow-health/` regelt
- **DARF NICHT** ein Tag deshalb als unveränderlich behandeln, weil der Herausgeber vertrauenswürdig ist: Der tj-actions-Vorfall kompromittierte die Tags eines vertrauenswürdigen Herausgebers, Vertrauen in den Herausgeber ist also nicht die Eigenschaft, die Pinning schützt [R4]
- **SOLLTE** die Update-Automatisierung des Repositories Pin-Anhebungen als prüfbare Pull Requests vorschlagen lassen, sodass ein Digest-Pin sichtbar altert statt still
- **KANN** eine von der eigenen Organisation dieses Portfolios herausgegebene Action über ein Tag referenzieren, wenn die Organisation die Veränderlichkeit des Tags kontrolliert, und **MUSS** diese Entscheidung festhalten, statt sie implizit zu lassen

### B. Rechte nach dem Prinzip der geringsten Rechte

- **MUSS** einen ausdrücklichen `permissions`-Block deklarieren, statt sich auf die Voreinstellung von Repository oder Organisation zu verlassen, sodass die Rechte eines Jobs im Workflow lesbar sind statt auf einer Einstellungsseite
- **MUSS** die Workflow-weiten `permissions` auf das Minimum setzen, das der Workflow braucht, und zusätzliche Schreibrechte nur dort auf Job-Ebene gewähren, wo ein Job sie wirklich braucht. GitHub empfiehlt, die voreingestellte Token-Berechtigung „auf reinen Lesezugriff" zu setzen [R1], und OpenSSF Scorecard prüft genau diese Form: schreibgeschützt auf oberster Ebene, erforderliche Schreibrechte auf Job-Ebene deklariert [R2]
- **DARF NICHT** pauschale Vollschreibrechte gewähren, um einen unklaren Fehlschlag zu umgehen; die richtige Reaktion ist, das Recht zu ermitteln, das der fehlschlagende Schritt braucht, und genau dieses zu gewähren
- **MUSS** das Schreibrecht `id-token` auf den Job begrenzen, der ein kurzlebiges Anmeldedatum anfordert (§D), nie Workflow-weit
- **SOLLTE** die Rechte eines Jobs neu ableiten, wenn sich seine Schritte ändern, denn ein Recht, das für einen inzwischen entfernten Schritt gewährt wurde, ist ein Recht, das niemand braucht

### C. Umgang mit nicht vertrauenswürdigen Eingaben und gefährlichen Auslösern

- **DARF NICHT** einen nicht vertrauenswürdigen Kontextwert direkt in ein `run`-Skript interpolieren. GitHubs angegebene Gegenmaßnahme ist, den Wert an eine zwischengeschaltete Umgebungsvariable zu binden und diese Variable im Skript zu referenzieren [R1]; OpenSSF Scorecard stuft die direkte Interpolation nicht vertrauenswürdigen Kontexts als gefährlichen Workflow ein [R2]
- **MUSS** jedes Feld, das ein außenstehender Beitragender kontrolliert, als nicht vertrauenswürdig behandeln, einschließlich Pull-Request-Titeln, -Beschreibungen, Branch-Namen und Commit-Nachrichten
- **DARF NICHT** Code aus einem nicht vertrauenswürdigen Pull Request in einem Workflow auschecken und ausführen, der Repository-Secrets oder erhöhte Token-Rechte hält. GitHub warnt, dass solche Workflows privilegiert sind und das Repository einer Kompromittierung aussetzen, und empfiehlt, den privilegierten Schritt vom nicht vertrauenswürdigen Code zu trennen [R1], [R2]
- **MUSS** jede Nutzung eines Auslösers begründen, der im privilegierten Kontext des Basis-Repositories läuft und dabei Fork-Code trägt, und **MUSS** den nicht vertrauenswürdigen Code aus diesem Kontext heraushalten, wenn der Auslöser wirklich gebraucht wird
- **SOLLTE** einen Auslöser bevorzugen, der nicht vertrauenswürdigen Code ohne Secrets ausführt und Ergebnisse an einen getrennten privilegierten Workflow übergibt, statt dem nicht vertrauenswürdigen Lauf die Rechte zu geben, die er zum direkten Handeln bräuchte [R1]

### D. Anmeldedaten

- **MUSS** Cloud-Anmeldedaten über den Austausch kurzlebiger Token der Plattform beziehen, statt langlebige Provider-Anmeldedaten als Repository-Secrets zu speichern, wo immer der Provider das unterstützt. Die Plattform stellt ein kurzlebiges Zugriffstoken aus, das nur für einen einzigen Job gilt und danach automatisch verfällt; das macht die Verdopplung von Cloud-Anmeldedaten als langlebige Secrets überflüssig [R3]
- **MUSS** die Vertrauensbeziehung auf Provider-Seite auf das konkrete Repository und, wo einschlägig, die konkrete Umgebung begrenzen, die sie berechtigterweise braucht, statt auf die gesamte Organisation [R3]
- **DARF NICHT** ein strukturiertes Datenpaket als einzelnes Secret speichern, wenn seine Teile getrennt genutzt werden; GitHub empfiehlt, Einzel-Secrets zu registrieren, sodass jeder Wert für sich geschwärzt bleibt [R1]
- **MUSS** ein Secret, das in einem Log aufgetaucht ist, als kompromittiert behandeln und rotieren, statt das Log zu löschen und die Sache damit als erledigt zu betrachten [R1]
- **DARF NICHT** Secrets breiter an einen aufgerufenen Reusable Workflow weitergeben, als dieser Workflow benötigt. Secrets erreichen nur den unmittelbar aufgerufenen Workflow, eine Kette reicht sie also bei jedem Schritt ausdrücklich weiter — diese Grenze ist bewusst zu nutzen, nicht durch pauschales Vererben auszuhebeln [R6]
- **SOLLTE** jeden sensiblen Wert, den der Workflow zur Laufzeit ableitet, beim Maskierungsmechanismus der Plattform registrieren, sodass auch eine Transformation eines Secrets geschwärzt bleibt [R1]

### E. Reusable Workflows und Composite Actions

- **MUSS** Logik, die über Repositories hinweg identisch ist, als Reusable Workflow in `nolte/gh-plumbing` implementieren und über eine gepinnte Referenz konsumieren, statt sie in jedes Repository zu kopieren. Das verallgemeinert die Regel, die `spec/project/pull-request-workflow/` bereits auf den Pull-Request-Linter und `spec/project/branching-model/` auf die Release-Workflows anwendet
- **DARF NICHT** einen Defekt in geteilter Workflow-Logik dadurch beheben, dass eine Consumer-lokale Kopie gepatcht wird. Das ist dieselbe Regel, die `spec/project/workflow-health/` für die `GITHUB_TOKEN`-Ereigniskaskade formuliert: Die Korrektur gehört upstream, damit jeder Consumer sie erhält, und ein Umweg pro Repository erzeugt genau den driftenden Fork, den das Wiederverwendungsmodell verhindern soll
- **MUSS**, wenn ein Consumer-Repository wirklich einen lokalen Übergangsumweg braucht, diesen als Übergangsmaßnahme festhalten, die die Upstream-Änderung benennt, auf die sie wartet, sodass der Umweg sichtbar temporär bleibt
- **SOLLTE** einen **Reusable Workflow** wählen, wenn die geteilte Einheit ein oder mehrere ganze Jobs mit eigenem Runner und eigenen Rechten sind, und eine **Composite Action**, wenn die geteilte Einheit eine Schrittfolge ist, die innerhalb des Jobs eines Aufrufers läuft
- **SOLLTE** die Aufrufkette flach halten. Die Plattform erzwingt eine dokumentierte maximale Verschachtelungstiefe [R6]; eine Kette, die sich ihr nähert, wird lange vor der Zurückweisung durch die Plattform schwer nachvollziehbar
- **MUSS** berücksichtigen, dass ein Reusable Workflow die Umgebung des Aufrufers nicht erbt, und **MUSS** ihm über deklarierte Eingaben übergeben, was er braucht, statt vorhandene Umgebungswerte anzunehmen [R6]
- **MUSS**, wenn der aufrufende Workflow mehr als einen Auslöser für einen Job deklariert, der einen Reusable Workflow aufruft, für jede aufgerufene Eingabe, deren Vorgabewert aus einem bestimmten Ereignis-Payload abgeleitet ist, eine entsprechende Auslöser-Eingabe deklarieren und sie über einen ausdrücklichen Rückfallausdruck durchreichen. Ein aus einem Payload abgeleiteter Vorgabewert wie `${{ github.event.release.tag_name }}` gilt nur für das Ereignis, das dieses Payload trägt; bei jedem anderen Auslöser löst er zur leeren Zeichenkette auf, sodass ein ohne die passende Eingabe hinzugefügter Auslöser genau auf dem Pfad wirkungslos ist, für den er hinzugefügt wurde
- **SOLLTE** in einem Reusable Workflow, der einen aus einem Ereignis-Payload abgeleiteten Vorgabewert deklariert, den leeren Wert zurückweisen und mit einer Meldung abbrechen, die die aufruferseitige Korrektur benennt, statt fortzufahren. Ein ungeprüfter leerer Wert bleibt nicht als „fehlt" sichtbar: Er entartet zu einem still falschen Vorgabewert, und der Lauf meldet Erfolg, während er auf etwas anderes als die beabsichtigte Referenz wirkt

### F. Nebenläufigkeit

- **MUSS** für jeden Workflow, bei dem sich zwei Läufe auf demselben Branch stören würden, eine Nebenläufigkeitsgruppe deklarieren, sodass ein überholter Lauf nicht gegen den Lauf rennen kann, der ihn ersetzt hat
- **MUSS** die Nebenläufigkeitsgruppe aus der Workflow-Identität und der Branch- oder Pull-Request-Identität ableiten, sodass Läufe auf verschiedenen Branches einander nicht abbrechen [R7]
- **DARF NICHT** das Abbrechen laufender Läufe bei einem neuen Lauf auf einen Delivery- oder Release-Workflow anwenden, wo der Abbruch eines laufenden Laufs ein teilweise veröffentlichtes Artefakt hinterlassen kann; das Muster gehört zum Pre-Merge-Feedback, wo das Überholen eines veralteten Laufs erwünscht ist
- **SOLLTE** das Abbrechen bei neuem Lauf für Pre-Merge-Workflows aktivieren, sodass ein nachgeschobener Commit keinen veralteten Lauf hinterlässt, der Kapazität verbraucht und ein überholtes Urteil meldet [R7]. Diese Empfehlung steht unter dem Vorbehalt, dass die Job-Laufzeit zur Kadenz des auslösenden Ereignisses passt: Eine Lane, deren Laufzeit die Push-Kadenz übersteigt, endet unter cancel-in-progress überwiegend mit `cancelled` und liefert nie ein Urteil — Beobachtung und Abhilfe (Trigger-Umplatzierung, nicht `cancel-in-progress: false`) regelt `spec/project/workflow-health/` §Abbruchraten

### G. Caching

- **MUSS** die Cache-Regeln aus `spec/project/continuous-integration/` §D hier als bindend behandeln und **DARF NICHT** Cache-Funktionen der Plattform so nutzen, dass ein Cache das Urteil eines Laufs verändern kann
- **MUSS** einen Cache-Schlüssel aus dem Inhalt bilden, der die zwischengespeicherten Daten bestimmt, denn ein Cache-Eintrag kann nicht an Ort und Stelle aktualisiert werden: Trifft ein Schlüssel auf einen bestehenden Eintrag, wird kein neuer geschrieben; ein Schlüssel, der sich bei Inhaltsänderung nicht ändert, pinnt die Pipeline also unbefristet auf veraltete Daten [R8]
- **DARF NICHT** sich auf einen Präfix-Rückfall verlassen, um einen veralteten Eintrag zu heilen; der Rückfall stellt einen älteren Eintrag wieder her, statt den Schlüssel zu korrigieren, die Veralterung bleibt also bestehen, sofern der konsumierende Schritt sie nicht erkennt und behebt [R8]
- **DARF NICHT** Anmeldedaten oder sonstiges Geheimmaterial zwischenspeichern [R1]
- **SOLLTE** die branch-bezogene Sichtbarkeit von Caches auf der Plattform berücksichtigen, wenn nachvollzogen wird, warum sich ein Lauf auf einem Feature-Branch anders verhält als einer auf dem Standard-Branch [R8]

### H. Provenienz

- **MUSS** den von `spec/project/continuous-delivery/` §C geforderten Provenienz-Nachweis über den Attestierungsmechanismus der Plattform erzeugen statt über einen Schritt in dem Build, der attestiert wird, denn die Plattform erzeugt und signiert den Nachweis unabhängig vom Build [R9], [R10]
- **MUSS** die attestierungsbezogenen Rechte an dem Job gewähren, der die Attestierung erzeugt, gemäß §B, und **DARF NICHT** sie auf den Workflow ausweiten
- **DARF NICHT** eine Attestierung als Beleg dafür ausgeben, dass ein Artefakt sicher ist. GitHub stellt ausdrücklich fest, dass Artefakt-Attestierungen keine Garantie für die Sicherheit eines Artefakts sind, sondern es stattdessen mit dem Quellcode und den Build-Anweisungen verknüpfen, die es erzeugt haben [R9]
- **SOLLTE** für den Build-Schritt geteilte Reusable Workflows konsumieren, wo die Organisation sie einsetzt; das ist zugleich der von der Plattform dokumentierte Weg zu einer höheren Provenienz-Stufe [R9]

### I. Runner

- **DARF NICHT** Workflows aus öffentlichen Repositories auf selbst gehosteten Runnern ausführen. GitHub stellt fest, dass selbst gehostete Runner für öffentliche Repositories nahezu nie verwendet werden sollten, weil jede Person einen Pull Request öffnen und die Runner-Umgebung dauerhaft kompromittieren kann [R1]
- **MUSS** einen Runner als wegwerfbar behandeln: Ein Job **DARF NICHT** von Zustand abhängen, den ein früherer Job oder Lauf hinterlassen hat; das ist die Plattform-Ausprägung der Stufen-Isolationsregel aus `spec/project/continuous-integration/` §C
- **SOLLTE**, wo ein selbst gehosteter Runner für ein privates Repository wirklich nötig ist, einen kurzlebigen Runner verwenden, der für jeden Job in einer sauberen Umgebung startet [R1]

### J. Abgrenzung

- **DARF NICHT** eine Regel wiederholen, die `continuous-integration`, `continuous-delivery`, `branching-model`, `project-structure`, `pull-request-workflow`, `workflow-health` oder `release-automation` gehört; wo diese Spec eine dieser Regeln an die Plattform bindet, referenziert sie die besitzende Spec und ergänzt nur die plattformspezifische Mechanik
- **MUSS** die `GITHUB_TOKEN`-Ereigniskaskade an `spec/project/workflow-health/` verweisen, das sie besitzt, statt sie hier neu herzuleiten
- **MUSS** einen roten Lauf zur Triage an `spec/project/workflow-health/` weiterreichen
- **MUSS** die Entscheidung, ob überhaupt eine Merge Queue betrieben wird, an `spec/project/pull-request-workflow/` §„Merge Queue" verweisen, das den Merge-Pfad besitzt; §K bindet nur die Plattform-Mechanik, die aus dieser Entscheidung folgt

### K. Merge-Queue-Ereignisverdrahtung

Dieser Abschnitt bindet die Merge-Queue-Mechanik an die Plattform. Ob ein Repository überhaupt eine Merge Queue betreiben sollte, liegt bei `spec/project/pull-request-workflow/` §„Merge Queue" und wird hier nicht entschieden; diese Regeln gelten, sobald eine aktiviert ist.

- **MUSS** `merge_group` (Aktivitätstyp `checks_requested`) als Trigger in jeden Workflow aufnehmen, dessen Job ein Required Status Check der eingereihten Branch ist. Eine Merge Queue wartet darauf, dass die Required Checks gegen die Merge Group gemeldet werden, und ein Workflow, der nur auf `pull_request` triggert, meldet dort nichts — der Eintrag wartet also auf einen Status, der nie eintrifft [R11], [R12]
- **DARF NICHT** einen Required Check, der nur im Pull-Request-Kontext laufen kann — ein Titel- oder Body-Linter, ein Check, der Felder aus dem `pull_request`-Payload liest —, für eine eingereihte Branch als required registriert lassen. In einer Merge Group gibt es keinen Pull Request zum Auswerten, und ein Workflow, der nicht startet, meldet überhaupt keinen Status statt eines Skips, der als Erfolg zählte. Ein solcher Check wird entweder aus dem Required-Set entfernt oder so umgebaut, dass sein Job im Merge-Group-Kontext weiterhin läuft und Erfolg meldet, während seine Pull-Request-only-Schritte übersprungen werden [R12]
- **MUSS** einen Drittanbieter-CI-Provider so konfigurieren, dass er auf Pushes zu Branches mit dem Präfix `gh-readonly-queue/{base_branch}` läuft — den temporären Branches, welche die Queue erzeugt; diese tragen eine andere SHA als der Pull-Request-Head [R12]
- **DARF NICHT** eine eingereihte Branch über eine Branch-Protection-Regel schützen, deren Namensmuster einen Wildcard verwendet: Auf einer solchen Regel lässt sich keine Merge Queue aktivieren [R12]
- **MUSS** die Nebenläufigkeitsgruppe eines Merge-Group-Laufs (§F) aus einem Schlüssel ableiten, der in diesem Kontext befüllt ist; eine Gruppe, die auf einem Pull-Request-only-Ausdruck beruht, fasst alle Merge-Group-Läufe in eine Gruppe zusammen, sodass ein neu eingereihter Eintrag genau den Lauf abbricht, auf den die Queue noch wartet
- **SOLLTE** die verdoppelte Ausführung einkalkulieren, bevor eine Queue aktiviert wird: Dieselbe Pipeline läuft nun einmal pro Pull Request und erneut pro Merge Group, und ein entfernter Eintrag baut die dahinterliegenden Einträge neu. Wo diese Kosten ins Gewicht fallen, entscheiden die Stufen-Zuschnittsregeln von `spec/project/continuous-integration/` §A und §E, was in welchem Kontext läuft — diese Spec leitet sie nicht neu her

## Akzeptanzkriterien

- [ ] Jede Referenz auf eine Drittanbieter-Action in `.github/workflows/` ist ein vollständiger Commit-Digest mit einem Kommentar, der die zugehörige Version benennt
- [ ] Jede Reusable-Workflow-Referenz ist auf eine unveränderliche Referenz gepinnt statt auf einen wandernden Branch
- [ ] Für jeden gepinnten Digest wurde geprüft, dass er zum Repository der Action selbst gehört und nicht zu einem Fork, und diese Prüfung ist in der Pinning-Änderung festgehalten
- [ ] Jeder Workflow deklariert einen ausdrücklichen `permissions`-Block, wobei Schreibrechte auf Job- statt auf Workflow-Ebene gewährt werden
- [ ] In einem Repository, das eine Merge Queue betreibt, triggert jeder Workflow hinter einem Required Status Check zusätzlich auf `merge_group`, kein Required Check hängt von Pull-Request-only-Kontext ab, und Drittanbieter-CI läuft auf dem `gh-readonly-queue/`-Präfix
- [ ] In einem Workflow, der mehr als einen Auslöser deklariert und einen Reusable Workflow aufruft, ist jede aufgerufene Eingabe mit einem aus einem Ereignis-Payload abgeleiteten Vorgabewert durch eine passende Auslöser-Eingabe abgedeckt und über einen Rückfallausdruck durchgereicht
- [ ] Kein Workflow gewährt pauschale Vollschreibrechte
- [ ] Kein `run`-Skript interpoliert einen nicht vertrauenswürdigen Kontextwert direkt; solche Werte erreichen das Skript über eine zwischengeschaltete Umgebungsvariable
- [ ] Kein Workflow checkt nicht vertrauenswürdigen Pull-Request-Code in einem Kontext aus, der Secrets oder erhöhte Rechte hält
- [ ] Wo ein Cloud-Provider den Austausch kurzlebiger Token unterstützt, nutzt das Repository ihn statt eines gespeicherten langlebigen Anmeldedatums, und die Vertrauensbedingung auf Provider-Seite benennt das konkrete Repository
- [ ] Kein Secret enthält ein strukturiertes Datenpaket, dessen Teile getrennt genutzt werden, und jedes Secret, das in einem Log aufgetaucht ist, wurde rotiert statt nur das Log zu löschen
- [ ] Kein aufgerufener Reusable Workflow erhält Secrets über die hinaus, die er braucht
- [ ] Über Repositories hinweg identische Logik wird über eine gepinnte Referenz aus `nolte/gh-plumbing` konsumiert, ohne Consumer-lokale Kopie und mit jedem Übergangsumweg als solchem festgehalten
- [ ] Jeder Workflow, dessen nebenläufige Läufe sich stören würden, deklariert eine Nebenläufigkeitsgruppe aus Workflow- und Branch-Identität
- [ ] Kein Delivery- oder Release-Workflow bricht laufende Läufe ab
- [ ] Jeder Cache-Schlüssel enthält den Inhalt, der die zwischengespeicherten Daten bestimmt, und kein Cache speichert Geheimmaterial
- [ ] Die Artefakt-Provenienz wird vom Attestierungsmechanismus der Plattform erzeugt, mit auf den erzeugenden Job begrenzten Rechten
- [ ] Kein öffentliches Repository des Portfolios adressiert einen selbst gehosteten Runner
- [ ] Kein Job hängt von Zustand ab, den ein früherer Job oder Lauf auf dem Runner hinterlassen hat
- [ ] Ein Abgleich dieser Spec mit `continuous-integration`, `continuous-delivery`, `workflow-health` und `branching-model` fördert keine wiederholte Regel zutage, nur Plattformbindungen

## Referenzen

Die Quellenklassen sind gemäß `spec/claude/research-triangulate/` ausgewiesen. Die tragenden Regeln aus §A, §B, §C und §H stützen sich jeweils auf zwei oder mehr unabhängige Quellen.

- [R1] *Secure use reference* (GitHub Docs, **Primär**): Commit-Digest-Pinning als einzige unveränderliche Action-Referenz, schreibgeschützte Token-Voreinstellung mit Schreibrechten auf Job-Ebene, die Gegenmaßnahme der zwischengeschalteten Umgebungsvariable für nicht vertrauenswürdige Eingaben, Secret-Hygiene und Maskierung, die Warnung vor privilegierten Auslösern sowie die Hinweise zu selbst gehosteten Runnern: <https://docs.github.com/en/actions/reference/security/secure-use>
- [R2] *OpenSSF-Scorecard-Checks* (**Primär**, unabhängig von GitHub): `Pinned-Dependencies` (eine gepinnte Abhängigkeit ist auf einen konkreten Hash statt auf eine veränderliche Version gesetzt), `Token-Permissions` (schreibgeschützt auf oberster Ebene, erforderliche Schreibrechte auf Lauf-Ebene) und `Dangerous-Workflow` (Auschecken nicht vertrauenswürdigen Codes und Skript-Injektion über nicht vertrauenswürdige Kontextvariablen): <https://github.com/ossf/scorecard/blob/main/docs/checks.md>
- [R3] *OpenID Connect in GitHub Actions* (GitHub Docs, **Primär**): kurzlebige Token, die nur für einen Job gelten, Wegfall verdoppelter langlebiger Cloud-Anmeldedaten und Vertrauensbedingungen auf Basis des Subject-Claims: <https://docs.github.com/en/actions/concepts/security/openid-connect>
- [R4] *GitHub Action tj-actions/changed-files supply chain attack* (Wiz, **Sekundär**, datiert März 2025): Der Angreifer bog bestehende Versions-Tags auf Schadcode um, und Hash-gepinnte Consumer blieben unbetroffen, sofern sie im Zeitfenster keinen kompromittierten Digest übernahmen: <https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066>
- [R5] *Supply Chain Compromise of Third-Party tj-actions/changed-files (CVE-2025-30066)* (CISA, **Sekundär**, unabhängig von R4, datiert 2025-03-18): die behördliche Warnmeldung zu demselben Vorfall: <https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction>
- [R6] *Reuse workflows* (GitHub Docs, **Primär**): der `workflow_call`-Mechanismus, die dokumentierte maximale Verschachtelungstiefe, die Regel, dass Umgebungen nicht vererbt werden, und die Regel, dass Secrets nur den unmittelbar aufgerufenen Workflow erreichen: <https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows>
- [R7] *Control the concurrency of workflows and jobs* (GitHub Docs, **Primär**): Nebenläufigkeitsgruppen, die Semantik von `cancel-in-progress` und das Gruppen-Ausdrucksmuster aus Workflow und Ref: <https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency>
- [R8] *actions/cache* (**Primär**, das Repository der Action selbst): Ein passender Schlüssel schreibt keinen neuen Eintrag, Cache-Einträge lassen sich also nicht an Ort und Stelle aktualisieren; `restore-keys` führt Präfix-Abgleiche gegen ältere Einträge durch; die Cache-Sichtbarkeit ist nach Schlüssel, Version und Branch begrenzt: <https://github.com/actions/cache>
- [R9] *Artifact attestations* (GitHub Docs, **Primär**): plattformerzeugte Build-Provenienz, der Weg über geteilte Reusable Workflows zu einer höheren Provenienz-Stufe und die ausdrückliche Feststellung, dass Attestierungen keine Garantie für die Sicherheit eines Artefakts sind: <https://docs.github.com/en/actions/concepts/security/artifact-attestations>
- [R10] *SLSA v1.0 Build-Level* (**Primär**, unabhängig von GitHub): die Anforderung, dass die Build-Plattform die Provenienz erzeugt und signiert, nicht der Build-Prozess selbst: <https://slsa.dev/spec/v1.0/levels>
- [R11] *Events that trigger workflows* (GitHub Docs, **Primär**): das `merge_group`-Ereignis mit seinem einzigen Aktivitätstyp `checks_requested` sowie die Feststellung, dass ein Repository, das Actions für Required Pull-Request-Checks nutzt, das Ereignis ergänzen muss, weil der Merge sonst scheitert, da der Status nie gemeldet wird, `https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows`
- [R12] *Managing a merge queue* (GitHub Docs, **Primär**): die CI-Konfigurationsanforderung, auf Merge-Group-Ereignisse zu triggern und zu melden, das Präfix `gh-readonly-queue/{base_branch}` temporärer Branches mit abweichender SHA, die Wildcard-Beschränkung der Branch-Protection sowie die durchgearbeiteten Szenarien, in denen ein entfernter Eintrag die dahinterliegenden temporären Branches neu erzeugen lässt, `https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue`
- `spec/project/continuous-integration/`, `spec/project/continuous-delivery/`: die werkzeugunabhängigen Specs, die diese Spec an die Plattform bindet
- `spec/project/branching-model/`, `spec/project/pull-request-workflow/`, `spec/project/project-structure/`, `spec/project/workflow-health/`, `spec/project/release-automation/`: die benachbarten Specs, deren Regeln diese Spec referenziert statt wiederholt

## Offene Fragen

- §A erlaubt, Actions der eigenen Organisation über ein Tag zu referenzieren, wenn die Organisation die Veränderlichkeit des Tags kontrolliert; das Portfolio hat aber nicht entschieden, ob es die Tag-Unveränderlichkeitskontrollen der Plattform aktiviert. Bis dahin beruht die Ausnahme auf Konvention statt auf einer erzwungenen Eigenschaft.
- §E legt fest, wann ein Reusable Workflow einer Composite Action vorzuziehen ist, klärt aber nicht, was der `nolte/gh-plumbing`-Katalog über das hinaus enthalten sollte, was `branching-model` und `pull-request-workflow` bereits vorschreiben. Die in `continuous-integration` §H genannten Auslagerungskandidaten wurden nicht inventarisiert.
- Die Regel aus §D zu kurzlebigen Anmeldedaten steht unter dem Vorbehalt der Provider-Unterstützung. Welche Anmeldedaten dieses Portfolio heute als langlebige Secrets hält und welche davon migrieren könnten, wurde nicht erhoben.
- Die Akzeptanzkriterien sind so formuliert, dass sie durch Inspektion prüfbar sind, aber kein Linter setzt sie durch. Ob ein bestehendes Workflow-Scanning-Werkzeug übernommen wird oder allein der Agent `cicd-pipeline-reviewer` genügt, ist ungeklärt.
- Upstream-Plattformgrenzen (Verschachtelungstiefe, Cache-Aufbewahrung, Cache-Größe) werden bewusst referenziert statt zitiert, damit diese Spec keine Zahlen trägt, die veralten. Wer den aktuellen Wert braucht, liest die zitierte Quelle.
