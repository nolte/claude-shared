# Continuous-Delivery-Pipeline-Design

Status: draft
Portfolio-Scope: portfolio

## Kontext

`spec/project/continuous-integration/` besitzt die Pre-Merge-Hälfte der Pipeline: die Disziplin, die entscheidet, ob ein Commit nach `develop` darf. Sobald ein Commit gelandet ist, übernimmt eine andere Disziplin, mit anderen Auslösern, anderen Konsumenten und anderen Fehlerkosten. Ein roter Pre-Merge-Lauf blockiert einen Pull Request. Ein Delivery-Defekt geht in Auslieferung.

Die benachbarten Specs besitzen erneut die Teile, nicht das Ganze. `spec/project/release-artifact/` legt die **Taxonomie** dessen fest, was ein Projekt ausliefert, und die Form eines `artifact_ref` je Projekttyp. `spec/project/release-automation/` legt den **Übergang** vom offenen Release-Entwurf zum veröffentlichten Release fest, samt der Pre-Publish-Gates und der versionstragenden Dateien, die diese Gates abgleichen. `spec/project/branching-model/` legt fest, wie sich ein veröffentlichtes Release nach `main` fortpflanzt. `spec/project/release-skill-layer/` legt die Kurations- und Dispatch-Schicht fest, die Operatoren bedienen. `spec/project/kubernetes-deployment-best-practices/` und `spec/project/bjw-s-common-chart-deployment/` legen fest, wie eine Arbeitslast für den Betrieb konfiguriert wird.

Was keine von ihnen festlegt, ist die **Auslieferungsdisziplin**, die sie verbindet: welche Stufen eine Post-Merge-Pipeline durchläuft, welche Eigenschaft jedes ausgelieferte Artefakt tragen muss, wie ein Artefakt an den Commit und den Build gebunden wird, der es erzeugt hat, und was geschieht, wenn sich eine ausgelieferte Version als falsch erweist. Diese Spec besitzt diese Disziplin.

Ihr Geltungsbereich endet an einer bewussten Grenze. Delivery verantwortet das **Bauen, Attestieren und unveränderliche Veröffentlichen** des Artefakts sowie den Rollback-Vertrag über Artefakt-Versionen. Das Ausrollen einer Arbeitslast in einen Cluster ist Sache der Deployment-Specs, die konsumieren, was Delivery veröffentlicht. Die Grenze wird hier benannt statt überschritten, sodass keine Seite die andere wiederholt.

Zwei Eigenschaften werden aus der Pre-Merge-Hälfte übernommen und bedeuten hier etwas Schärferes:

- **Reproduzierbarkeit** wird zur **Nachvollziehbarkeit des Ausgelieferten**. Jedes veröffentlichte Artefakt muss einem Commit, einem Build und einem Satz gepinnter Eingaben zurechenbar sein. Ein Artefakt, das niemand zurückverfolgen kann, ist nicht auditierbar, nicht reproduzierbar und kein sicheres Rollback-Ziel.
- **Wiederverwendung statt Kopieren** wird zum **einen Auslieferungspfad**. Ein Projekt, das über einen Mechanismus in der Pipeline und über einen anderen von Hand veröffentlicht, hat zwei Auslieferungspfade, und nur einer davon ist geregelt.

**Leser:** Beitragende und KI-Agenten, die die Post-Merge-Auslieferung eines Repositories bauen oder umbauen, Release-Operatoren, die entscheiden, ob eine Version sicher veröffentlicht werden kann, sowie die Autoren des Skills `cicd-pipeline-design` und des Agents `cicd-pipeline-reviewer`, die diese Spec operationalisieren.

## Ziele

- Alles, was ein Projekt ausliefert, wird von der Delivery-Pipeline erzeugt, sodass kein Artefakt über einen Pfad zu einem Konsumenten gelangt, der die Garantien der Pipeline umgeht
- Jedes veröffentlichte Artefakt ist auf den Commit, den Build und die gepinnten Eingaben zurückführbar, die es erzeugt haben
- Ein veröffentlichtes Artefakt ist unveränderlich: Eine gegebene Versionsreferenz löst immer auf dieselben Bytes auf
- Jede Artefaktklasse, die ein Projekt ausliefert, hat eine benannte Delivery-Stufe, die sie absichert, sodass kein Artefakt versehentlich unattestiert ausgeliefert wird
- Die Erholung von einem fehlerhaften Release ist eine eingeübte Operation über Artefakt-Versionen statt einer Improvisation
- Die Grenze zwischen dem Veröffentlichen eines Artefakts und dessen Betrieb ist ausdrücklich, sodass Delivery und Deployment einander weder wiederholen noch widersprechen

## Nicht-Ziele

- Die Artefakt-Taxonomie und die gültigen `artifact_ref`-Formen je Projekttyp — im Besitz von `spec/project/release-artifact/`; diese Spec legt fest, was eine Delivery-Stufe über ein Artefakt garantieren muss, nicht welche Artefakte existieren
- Der Übergang vom Entwurf zum veröffentlichten Release, das Pre-Publish-Gate und der Abgleich versionstragender Dateien — im Besitz von `spec/project/release-automation/`; die Release-Stufe dieser Spec dispatcht in diese Maschinerie und definiert sie nicht neu
- Wie sich ein veröffentlichtes Release nach `main` fortpflanzt und welche Workflows existieren müssen — im Besitz von `spec/project/branching-model/`
- Die operatorseitige Kurations- und Dispatch-Schicht — im Besitz von `spec/project/release-skill-layer/`
- Wie eine Arbeitslast konfiguriert, gehärtet und in einen Cluster ausgerollt wird — im Besitz von `spec/project/kubernetes-deployment-best-practices/` und `spec/project/bjw-s-common-chart-deployment/`; Delivery übergibt an sie und endet
- Alles vor dem Merge: Stufenordnung für Pre-Merge-Feedback, das Quality-Gate, die Testausführung — im Besitz von `spec/project/continuous-integration/`
- Der Betrieb der Delivery-Workflows über die Zeit und ihre Triage, wenn sie rot werden — im Besitz von `spec/project/workflow-health/`
- Plattformspezifische Syntax und Mechanik. Diese Spec ist werkzeugunabhängig; `spec/project/github-actions-best-practices/` ist die einzige konkrete Bindung

## Anforderungen

### A. Geltungsbereich und Auslöser der Delivery-Pipeline

- **MUSS** Delivery als beginnend mit dem Merge nach `develop` und endend mit der Veröffentlichung jedes Artefakts behandeln, das die Version ausliefert; Arbeit vor dem Merge gehört zu `spec/project/continuous-integration/`
- **MUSS** jede Delivery-Stufe aus einem deklarierten Ereignis auslösen statt aus einem manuellen Aufruf, dessen Schritte nur im Gedächtnis eines Operators existieren. Wo das Portfolio bewusst einen menschlichen Entscheidungspunkt beibehält, **MUSS** diese Entscheidung ein deklarierter Auslöser mit festgehaltener Begründung sein statt einer undokumentierten Gewohnheit
- **DARF NICHT** ein Artefakt aus einem Commit veröffentlichen, der das Pre-Merge-Gate nicht bestanden hat; Delivery baut auf dem Pre-Merge-Urteil auf, statt es zu ersetzen
- **SOLLTE** die Stufe, die ein Artefakt **erzeugt**, von der Stufe trennen, die es **veröffentlicht**, sodass ein Build-Fehler und ein Veröffentlichungsfehler unterscheidbar sind und ein erzeugtes Artefakt geprüft werden kann, bevor es sichtbar wird

### B. Artefakt-Identität und Unveränderlichkeit

- **MUSS** jedem veröffentlichten Artefakt eine Versionsreferenz geben, die für immer auf dieselben Bytes auflöst; das erneute Veröffentlichen abweichenden Inhalts unter einer bestehenden Versionsreferenz ist unzulässig
- **MUSS** eine versehentliche Veröffentlichung als ausschließlich vorwärtsgerichtetes Ereignis behandeln: Das Mittel ist, eine neue Version zu veröffentlichen und, wo das Ökosystem es unterstützt, die fehlerhafte Version als zurückgezogen zu kennzeichnen. Die fehlerhafte Version an Ort und Stelle zu überschreiben, zerstört die Unveränderlichkeitsgarantie, auf die sich jeder Konsument stützt
- **DARF NICHT** eine Versionsreferenz aus etwas ableiten, das sich unabhängig vom Inhalt ändern kann, etwa aus einem wandernden Branch-Namen oder einer nächtlich neu gebauten Kennzeichnung
- **MUSS** sicherstellen, dass eine Versionsreferenz zum Zeitpunkt, zu dem die Version als ausgeliefert erklärt wird, unabhängig erneut abrufbar ist, gemäß `spec/project/release-artifact/`; diese Spec ergänzt, dass der erneute Abruf denselben Inhalt liefern **MUSS**, den die Pipeline veröffentlicht hat
- **SOLLTE** neben der Versionsreferenz einen Inhalts-Digest veröffentlichen, wo das Ökosystem einen bereitstellt, sodass ein Konsument die Identität prüfen kann, ohne allein der Referenz zu vertrauen

### C. Provenienz

- **MUSS** für jedes veröffentlichte Artefakt den Commit festhalten, aus dem es gebaut wurde, den Pipeline-Lauf, der es gebaut hat, und die gepinnten Eingaben, die der Build aufgelöst hat
- **MUSS** den Provenienz-Nachweis von der Pipeline selbst erzeugen lassen statt vom Build, der attestiert wird; ein Build, der seine eigene Integrität attestiert, kann seine eigene Kompromittierung nicht erkennen
- **MUSS** den Provenienz-Nachweis für einen Konsumenten des Artefakts abrufbar machen, statt ihn nur innerhalb der Pipeline-Logs lesbar zu halten, die verfallen
- **SOLLTE** den Provenienz-Nachweis in prüfbarer Form (als signierte Attestierung) veröffentlichen statt als unsignierte Metadaten, sodass Manipulation nach der Veröffentlichung erkennbar ist
- **SOLLTE** Provenienz als Beleg für **Herkunft** behandeln, nie als Beleg für **Sicherheit**: Ein attestiertes Artefakt ist eines, dessen Build-Pfad bekannt ist, nicht eines, das als sicher beurteilt wurde. Sicherheitsbefunde bleiben Sache der Supply-Chain-Stufen in `spec/project/continuous-integration/` §G
- **KANN** die signierte Attestierung für eine Artefaktklasse weglassen, deren Ökosystem keinen Prüfpfad bietet, und **MUSS** in diesem Fall festhalten, welchen Artefaktklassen die Provenienz fehlt, statt die Lücke implizit zu lassen

### D. Die Artefakt-zu-sichernder-Stufe-Matrix

Jede Artefaktklasse, die ein Projekt ausliefert, braucht eine benannte Stufe, die sie absichert. Der Zweck der Matrix ist, dass eine Lücke sichtbar wird: Eine Artefaktklasse ohne sichernde Stufe ist ein Artefakt, das ungeschützt ausgeliefert wird.

- **MUSS** je Projekt eine Abbildung von jeder ausgelieferten Artefaktklasse auf die Delivery-Stufe festlegen, die diese Klasse absichert, samt der Garantie, die diese Stufe bietet. Die Artefaktklassen stammen aus `spec/project/release-artifact/` §Artefakt-Taxonomie und **DÜRFEN NICHT** hier erneut aufgezählt werden
- **MUSS** die folgenden Garantien als die Sicherungspflichten behandeln, die eine Stufe tragen kann, und **MUSS** für jede Artefaktklasse mindestens eine benennen:
  - **aus-Quelle-gebaut**: Das Artefakt wurde von der Pipeline aus dem attestierten Commit erzeugt, nicht von anderswo hochgeladen
  - **Integrität**: Der Inhalt des Artefakts liegt fest und ist über Digest oder Signatur prüfbar
  - **Provenienz**: Das Artefakt trägt einen abrufbaren Herkunftsnachweis gemäß §C
  - **richtlinien-geprüft**: Die Abhängigkeits-, Lizenz- und Sicherheitspflichten des Artefakts wurden vor der Veröffentlichung bewertet, gemäß den besitzenden Specs
- **MUSS** eine Artefaktklasse ohne sichernde Stufe als Defekt im Pipeline-Design behandeln statt als hinnehmbare Auslassung, und **MUSS** sie bei der Pipeline-Prüfung als solchen ausweisen
- **SOLLTE** die Abbildung in einer Form halten, die ein Reviewer lesen kann, ohne sie aus Workflow-Dateien zu rekonstruieren
- **KANN** eine Stufe mehrere Artefaktklassen absichern lassen, wenn die Garantie tatsächlich für alle gilt

### E. Grenze zum Release-Dispatch

- **MUSS** für den Übergang vom Entwurf zum veröffentlichten Release nach `spec/project/release-automation/` dispatchen, statt diesen Übergang in der Delivery-Pipeline zu implementieren; das Pre-Publish-Gate, der Abgleich versionstragender Dateien und die Veröffentlichungsmechanik gehören dorthin
- **DARF NICHT** ein von jener Spec festgelegtes Pre-Publish-Gate wiederholen, schwächen oder abkürzen. Eine Delivery-Pipeline, die ohne diese Gates veröffentlicht, hat den geregelten Pfad durch einen ungeregelten ersetzt
- **MUSS** die Fortpflanzung eines veröffentlichten Releases nach `main` als im Besitz von `spec/project/branching-model/` behandeln und **DARF NICHT** einen parallelen Mechanismus dafür implementieren
- **SOLLTE** einen fehlgeschlagenen Dispatch als Delivery-Fehler ausweisen statt als stilles Nichts, sodass ein unveröffentlichtes Release sichtbar wird statt bloß abwesend zu sein

### F. Übergabe an das Deployment

- **MUSS** die Verantwortung der Delivery-Pipeline beim veröffentlichten Artefakt samt seiner Provenienz enden lassen; Konfigurieren, Härten und Betreiben der Arbeitslast gehören `spec/project/kubernetes-deployment-best-practices/` und `spec/project/bjw-s-common-chart-deployment/`
- **MUSS** die Übergabe ausdrücklich machen: Die Delivery-Pipeline benennt die Artefaktreferenz, die ein Deployment konsumiert, und die Deployment-Seite löst sie auf. Eine implizite Übergabe, bei der das Deployment eine neue Version durch Beobachten einer wandernden Referenz entdeckt, hebelt §B aus
- **DARF NICHT** zulassen, dass ein Deployment-Belang als undeklarierte Stufe in die Delivery-Pipeline zurückläuft; wenn Delivery tatsächlich ein Deployment auslösen muss, **MUSS** der Auslöser eine deklarierte Stufe sein, die eine Artefaktreferenz übergibt, statt einer Stufe, die die Arbeitslast konfiguriert
- **SOLLTE** die Menge der Konsumenten eines veröffentlichten Artefakts als bekannte Größe führen, sodass ein Rollback (§G) benennen kann, wer betroffen ist

### G. Rollback

- **MUSS** die Erholung von einer fehlerhaften Version als **Auswahl einer anderen Artefakt-Version** definieren, was nur möglich ist, weil §B garantiert, dass alte Versionen weiterhin auf ihren ursprünglichen Inhalt auflösen
- **DARF NICHT** Rollback als Neubau eines älteren Commits definieren: Ein Neubau löst Eingaben zum Zeitpunkt des Neubaus auf und erzeugt daher ein anderes Artefakt als das, das als gut bekannt war
- **MUSS** die zuletzt als gut bekannte Versionsreferenz so lange abrufbar halten, wie ein Rollback auf diese Version eine plausible Reaktion bleibt
- **SOLLTE** den Rollback-Pfad einüben statt ihn ungetestet zu dokumentieren; ein ungeübter Rollback erweist sich im ungünstigsten Moment als kaputt
- **SOLLTE** beim Zurückziehen einer Version festhalten, warum sie zurückgezogen wurde und welche Version sie ablöst, sodass ein auf die fehlerhafte Version gepinnter Konsument erfährt, was zu tun ist

### H. Umgebungen und Promotion

- **MUSS** einstufige Auslieferung als Standardmodell behandeln: Ein Artefakt wird einmal veröffentlicht und direkt konsumiert. Das entspricht der tatsächlichen Auslieferungspraxis des Portfolios und hält den geregelten Pfad kurz
- **MUSS**, wenn ein Projekt doch Umgebungs-Promotion einführt, **dasselbe Artefakt** durch die Umgebungen befördern statt je Umgebung neu zu bauen; ein Neubau je Umgebung bedeutet, dass das getestete Artefakt nicht das ausgelieferte Artefakt ist
- **MUSS** umgebungsspezifische Werte in einer zur Deployment-Zeit konsumierten Konfiguration halten, statt sie in das Artefakt einzubacken, sodass das beförderte Artefakt über alle Umgebungen hinweg identisch bleibt
- **MUSS** für eine Artefaktklasse, die ihre Konfiguration wirklich nicht auf die Deployment-Zeit verschieben kann, genau einen von zwei Wegen wählen und festhalten, welchen: den Build so aufteilen, dass der umgebungsspezifische Teil eine getrennt veröffentlichte, zur Deployment-Zeit aufgelöste Eingabe ist, oder eine festgehaltene Ausnahme erklären, die die Artefaktklasse, die eingebackenen Werte und die ausgleichende Prüfung benennt, dass sich die Builds je Umgebung nur in diesen Werten unterscheiden. Ein nicht festgehaltener Neubau je Umgebung bleibt unzulässig
- **SOLLTE** ein Freigabe-Gate zwischen Umgebungen als ausdrücklichen, festgehaltenen Entscheidungspunkt deklarieren, wo eines existiert, statt als Operator-Konvention
- **KANN** Umgebungs-Promotion vollständig weglassen; sie ist ein optionales Muster, und ein Projekt ohne sie ist nicht mangelhaft

### I. Abgrenzung

- **DARF NICHT** eine Regel wiederholen, die `release-artifact`, `release-automation`, `release-skill-layer`, `branching-model`, `workflow-health` oder den Deployment-Specs gehört; wo diese Spec eine dieser Regeln braucht, referenziert sie sie
- **MUSS** einen roten Delivery-Lauf zur Triage an `spec/project/workflow-health/` weiterreichen
- **MUSS** für alles, was vor dem Merge läuft, an `spec/project/continuous-integration/` zurückgeben, selbst wenn es in derselben Datei definiert ist

## Akzeptanzkriterien

- [ ] Jedes Artefakt, das ein Projekt ausliefert, wird von der Delivery-Pipeline erzeugt, und es existiert kein Veröffentlichungspfad, der sie umgeht
- [ ] Jede Delivery-Stufe läuft aus einem deklarierten Auslöser, und jeder menschliche Entscheidungspunkt der Kette ist ein deklarierter Auslöser mit festgehaltener Begründung
- [ ] Kein veröffentlichtes Artefakt führt auf einen Commit zurück, der das Pre-Merge-Gate nicht bestanden hat
- [ ] Keine veröffentlichte Versionsreferenz des Projekts kann mit abweichendem Inhalt erneut veröffentlicht werden
- [ ] Jedes veröffentlichte Artefakt hat einen abrufbaren Provenienz-Nachweis, der seinen Commit, seinen Pipeline-Lauf und seine gepinnten Eingaben benennt
- [ ] Der Provenienz-Nachweis wird von der Pipeline erzeugt, nicht von dem Build, den er attestiert
- [ ] Es existiert je Projekt eine Abbildung von jeder ausgelieferten Artefaktklasse auf eine sichernde Stufe und mindestens eine benannte Garantie, und keine ausgelieferte Artefaktklasse fehlt darin
- [ ] Artefaktklassen ohne Prüfpfad sind als solche festgehalten, statt stillschweigend in der Abbildung zu fehlen
- [ ] Der Übergang vom Entwurf zum veröffentlichten Release wird nach `release-automation` dispatcht statt lokal nachgebaut, und kein Pre-Publish-Gate wird umgangen
- [ ] Die Delivery-Pipeline übergibt der Deployment-Seite eine benannte Artefaktreferenz und konfiguriert selbst keine Arbeitslast
- [ ] Der dokumentierte Rollback-Pfad wählt eine zuvor veröffentlichte Artefakt-Version aus und baut nie einen älteren Commit neu
- [ ] Die zuletzt als gut bekannte Versionsreferenz löst zu dem Zeitpunkt auf, zu dem ein Rollback sie bräuchte
- [ ] In einem Projekt mit Umgebungs-Promotion ist das in die letzte Umgebung beförderte Artefakt bytegleich mit dem in der ersten getesteten, oder die Artefaktklasse trägt eine festgehaltene Ausnahme für Build-Zeit-Konfiguration, die ihre eingebackenen Werte und die ausgleichende Prüfung benennt
- [ ] Ein Abgleich der Spec mit `release-artifact`, `release-automation`, `branching-model` und den Deployment-Specs fördert keine wiederholte Regel zutage, nur Referenzen

## Referenzen

- `spec/project/continuous-integration/`: die Pre-Merge-Hälfte der Pipeline, an die diese Spec anschließt
- `spec/project/release-artifact/`: die Artefakt-Taxonomie und die `artifact_ref`-Formen, über die §D abbildet und die sie ausdrücklich nicht wiederholt
- `spec/project/release-automation/`: der Übergang vom Entwurf zum veröffentlichten Release und das Pre-Publish-Gate, nach dem §E dispatcht
- `spec/project/release-skill-layer/`: die operatorseitige Kurations- und Dispatch-Schicht
- `spec/project/branching-model/`: wie sich ein veröffentlichtes Release nach `main` fortpflanzt
- `spec/project/kubernetes-deployment-best-practices/`, `spec/project/bjw-s-common-chart-deployment/`: die Deployment-Seite, an die §F übergibt
- `spec/project/dockerfile-best-practices/`: die Build-Definition für die Artefaktklasse Container-Image
- `spec/project/workflow-health/`: das operative Gegenstück, an das diese Spec rote Läufe übergibt
- `spec/project/github-actions-best-practices/`: die einzige konkrete Plattformbindung
- [R1] SLSA v1.0 Build-Level: Quelle der Regel aus §C, dass Provenienz von der Build-Plattform statt vom Build selbst erzeugt wird, sowie der Unterscheidung zwischen attestierter Herkunft und nachgewiesener Sicherheit: <https://slsa.dev/spec/v1.0/levels>

## Offene Fragen

- §C verlangt einen abrufbaren Provenienz-Nachweis, verzichtet aber darauf, für jede Artefaktklasse eine signierte Attestierung vorzuschreiben, weil nicht jedes Ökosystem, in das dieses Portfolio veröffentlicht, einen Prüfpfad bietet. Welche Klassen heute signierte Provenienz erreichen können und welche tatsächlich blockiert sind, wurde nicht erhoben.
- Die Abbildung aus §D hat kein festgelegtes Dateiformat. Ob sie in das bestehende Portfolio-Manifest des Repositories, in eine eigene Datei oder in einen dokumentierten Abschnitt gehört, ist ungeklärt; die Anforderung ist, dass ein Reviewer sie lesen kann, nicht wo sie liegt.
- §G verlangt, dass eine zuletzt als gut bekannte Version so lange abrufbar bleibt, wie ein Rollback auf diese Version eine plausible Reaktion bleibt — bewusst unquantifiziert. Ob eine portfolioweite Untergrenze für die Aufbewahrung lohnt, sollte erneut geprüft werden, sobald ein echter Rollback durchgeführt wurde.
- §H spezifiziert nun beide Wege für eine Artefaktklasse, die Konfiguration zur Build-Zeit einbettet (Aufteilung zur Build-Zeit oder festgehaltene Ausnahme mit ausgleichender Prüfung). Welche Klassen dieses Portfolios einen der Wege tatsächlich brauchen, wurde nicht erhoben; die Klausel ist also spezifiziert, aber nicht an einem echten Fall erprobt.
