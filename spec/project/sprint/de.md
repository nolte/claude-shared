# Projekt-Sprint

Status: draft

## Kontext

Leser: Repo-Maintainer von Hobby-Projekten im nolte-Portfolio, die die Skills `sprint-plan`, `sprint-execute` und `sprint-review` aufrufen, sowie die Implementierer dieser Skills, die gegen das hier definierte Schema bauen.

Die Geschwister-Spec `roadmap` definiert die Arbeits-Warteschlange und verknüpft jedes Item mit einem Projekt-Outcome, sagt aber bewusst nichts darüber, wie diese Arbeit gruppiert, abgearbeitet und ausgeliefert wird. Diese Spec füllt diese Lücke. Ein Sprint im nolte-Portfolio ist eine über Markdown verwaltete Arbeitseinheit, die ein oder mehrere Features (definiert in der Geschwister-Spec `feature`) bündelt und **mit einem ausrollbaren Artefakt enden MUSS** (definiert in der Geschwister-Spec `release-artifact`), **das einen direkten Mehrwert für den Endnutzer liefert**. Zwei Eigenschaften sind wichtig: Hobby-Projekte brauchen echt variable Sprint-Dauern (ein Sprint kann ein Wochenende oder drei Monate dauern), und konsumierende Claude-Skills (`sprint-plan`, `sprint-execute`, `sprint-review`) brauchen eine deterministische Markdown-Form, die sie lesen, ändern und validieren können. Diese Spec legt diese Form und den Lifecycle fest, der sie regiert.

## Ziele

- Die Datei-Form eines Sprints als eine einzige Markdown-Datei unter `project/sprints/<NNNN>-<slug>.md` festlegen, eine Datei pro Sprint, niemals gesplittet.
- Das Sprint-Frontmatter-Schema festlegen (Sprint-Nummer, Status, Mehrwert-Statement, Artefakt-Referenz, Feature-Liste), damit konsumierende Skills Sprints ohne Ad-hoc-Parser parsen und ändern können.
- Den Mehrwert-Vertrag erzwingen: jeder Sprint **MUSS [MUST]** ein einzeiliges `value_statement` aus Endnutzer-Sicht tragen, und mindestens ein Feature im Sprint **MUSS [MUST]** ein Akzeptanzkriterium tragen, das genau dieses Statement direkt prüft.
- Den Artefakt-Vertrag erzwingen: jeder geschlossene Sprint **MUSS [MUST]** auf ein konkretes ausrollbares Artefakt zeigen (Release-Tag, Container-Image-Tag, Plugin-Version oder Doc-Site-Deploy), das das Mehrwert-Statement materialisiert; die Detailregeln dazu liegen in der Geschwister-Spec `release-artifact`.
- Den Sprint-Lifecycle festlegen (`planned → active → review → closed`) und welche Übergänge zulässig sind, damit `sprint-plan`, `sprint-execute` und `sprint-review` nicht überlappende Zuständigkeiten haben.
- Portfolio-weit wiederverwendbar bleiben über Hobby-Skala-Varianz: Sprint-Dauer ist ein Output der Arbeit, kein Input, und die Spec toleriert Pausen und unregelmäßige Kadenz ausdrücklich.

## Nicht-Ziele

- Roadmap-, Feature- oder Release-Artefakt-Innenleben festzulegen. Jedes davon gehört seiner eigenen Geschwister-Spec; diese Spec erklärt nur Beziehungen und die Sprint-seitige Oberfläche.
- Projektmanagement-Tooling zu ersetzen. Das Sprint-Markdown ist der autoritative Datensatz unter Versionskontrolle; Verweise auf Issue-Tracker sind erlaubt, aber nie autoritativ.
- Eine feste Kadenz oder Dauer zu erzwingen. Die Geschwister-Spec `roadmap` erklärt Daten und Zeitschätzungen bereits als außerhalb des Geltungsbereichs, und diese Spec folgt dem auf Sprint-Granularität.
- `continuous-improvement` zu ersetzen. Retrospektive Prozessänderungen sind dort ereignis- und kalendergetrieben; Sprint-Review hier ist ein Sprint-Abschluss-Ritual, kein Prozess-Audit.
- `release-automation` oder `release-skill-layer` zu ersetzen. Die Artefakt-Referenz zeigt **auf** diese Mechanismen; sie definiert sie nicht neu.
- Akzeptanzkriterien zu erfinden. Feature-seitige Akzeptanz lebt in der Geschwister-Spec `feature`; Sprint-Review prüft nur, dass das `value_statement` durch ein bestehendes Kriterium eines Features abgedeckt ist.

## Anforderungen

### Verzeichnislayout und Datei-Form

- **MUSS [MUST]** jeden Sprint unter `project/sprints/<NNNN>-<slug>.md` ablegen, wobei `<NNNN>` eine vierstellige nullgepolsterte monoton vergebene Sprint-Nummer ist und `<slug>` eine ASCII-kebab-case-Zusammenfassung des Sprint-Ziels.
- **MUSS [MUST]** genau eine Markdown-Datei pro Sprint führen; Sprint-Inhalt wird nie über mehrere Dateien gesplittet.
- **DARF NICHT [MUST NOT]** eine Sprint-Nummer wiederverwenden, nachdem ein Sprint `cancelled` oder `closed` ist; Nummern sind über die gesamte Projekt-Lebensdauer streng monoton.
- **SOLLTE [SHOULD]** `<slug>` mit dem `value_statement` des Sprints abgleichen, damit Verzeichnislisten selbsterklärend bleiben.

### Frontmatter-Schema

- **MUSS [MUST]** die Datei mit einem YAML-Frontmatter-Fence öffnen, der folgende Felder in dieser Reihenfolge trägt:
  - `number` (Integer, verpflichtend) — passt zu `<NNNN>` im Dateinamen;
  - `status` (Enum, verpflichtend) — einer von `planned`, `active`, `review`, `closed`, `cancelled`;
  - `started` (ISO-Datum oder null, verpflichtend) — das Datum, an dem der Sprint nach `active` ging; null bis dahin;
  - `ended` (ISO-Datum oder null, verpflichtend) — das Datum, an dem der Sprint entweder `closed` oder `cancelled` erreicht hat (beide terminalen Zustände teilen dieses Feld, daher der neutrale Name); null bis der Sprint terminal ist;
  - `value_statement` (String, verpflichtend, nicht leer) — ein Satz, der den direkten Endnutzer-Mehrwert dieses Sprints beschreibt;
  - `artifact_ref` (String, Liste von Strings oder null, verpflichtend) — das Feld ist immer im Frontmatter vorhanden; **MUSS [MUST]** spätestens beim Übergang nach `review` nicht-null sein. Konkrete Referenz auf das ausrollbare Artefakt (zum Beispiel `v0.4.0`, `ghcr.io/owner/repo:v0.4.0`, `nolte-shared@1.7.0`, `docs.example.com@2026-05-08`); eine Listenform ist erlaubt für Hybrid-Projekttypen, die in einem Sprint zwei gekoppelte Artefakte ausliefern (zum Beispiel `[v0.4.0, ghcr.io/owner/repo:v0.4.0]`); die zulässigen Formen je Projekttyp regelt die Geschwister-Spec `release-artifact`;
  - `last_commit` (String oder null, verpflichtend) — der Commit-SHA der letzten Quellcode-Änderung, die dieser Sprint beigetragen hat; null bis das erste Feature im Sprint `done` erreicht. `sprint-execute` aktualisiert dieses Feld jedes Mal, wenn ein Feature im Sprint nach `done` geht. Das Feld verankert den Artefakt-Vorfahren-Check, den die Geschwister-Spec `release-artifact` beim Abschluss laufen lässt;
  - `roadmap_items` (Liste von Roadmap-Item-IDs, verpflichtend, darf leer sein) — jeder Eintrag **MUSS [MUST]** ein in `project/roadmap.md` definiertes `R-<n>` matchen;
  - `features` (Liste von Feature-IDs, verpflichtend, darf leer sein) — jeder Eintrag **MUSS [MUST]** eine Feature-ID matchen, die in `project/features/<slug>.md` per Geschwister-Spec `feature` definiert ist.
- **DARF NICHT [MUST NOT]** Aufwandsschätzungen, Velocity-Metriken oder Zuweisungsfelder jenseits der oben deklarierten enthalten; Lints flaggen unbekannte Frontmatter-Schlüsselwörter.

### Body-Sections

- **MUSS [MUST]** folgende Level-2-Sections in dieser Reihenfolge tragen, auch wenn leer (Skills hängen an stabilen Section-Überschriften):
  - `## Goal` — ein Absatz, der das `value_statement` aus Operator-Sicht ausführt; wie sieht Erfolg beim Sprint-Abschluss aus.
  - `## Features` — Aufzählungsliste der Features im Scope, jedes verlinkt auf `project/features/<slug>.md` und zeigt den aktuellen Feature-Status; die Feature-Liste **MUSS [MUST]** das Frontmatter-Feld `features` exakt spiegeln.
  - `## Out of scope` — explizite Liste von Items, die erwogen, aber aus diesem Sprint ausgeschlossen wurden, jedes zeigt auf das zugehörige Roadmap-Item, falls anwendbar; verhindert Scope-Creep mitten im Sprint.
  - `## Review notes` — wird beim Abschluss durch `sprint-review` befüllt; davor existiert die Section, kann aber leer sein oder einen Platzhalter tragen.
- **KANN [MAY]** eine zusätzliche `## Risks`-Section tragen, die bekannte Unbekannte und Mitigationen listet; empfohlen für Sprints, deren Features unbekannte Grenzen überschreiten.

### Lifecycle

- **MUSS [MUST]** `status` nur entlang dieser Pfade übergehen lassen: `planned → active`, `active → review`, `review → closed`, `review → cancelled`, `planned → cancelled`, `active → cancelled`. Direkte Übergänge außerhalb dieser Pfade sind verboten; insbesondere `active → closed` ohne `review` ist verboten, weil der Mehrwert-Coverage-Check (siehe §Mehrwert-Vertrag) im Status `review` lebt. Der Pfad `review → cancelled` existiert für den Fall, dass die Artefakt-Validierung laut Geschwister-Spec `release-artifact` beim Abschluss scheitert und der Sprint sich nicht erholen kann (zum Beispiel die zugrundeliegende Release-Pipeline ist defekt und ein Neu-Cut des Artefakts ist aktuell nicht machbar).
- **MUSS [MUST]** sicherstellen, dass zu jedem Zeitpunkt höchstens ein Sprint pro Projekt im Status `active` ist; mehrere parallel aktive Sprints brechen die lineare Kadenz-Annahme, auf die konsumierende Skills bauen.
- **MUSS [MUST]** den niedrigst-nummerierten `planned`-Sprint automatisch nach `active` befördern, spätestens in dem Moment, in dem eines seiner Features laut Geschwister-Spec `feature` von `ready` nach `in_progress` geht; `sprint-execute` ist der kanonische Durchsetzungspunkt. Die Beförderung schlägt fehl (und der Feature-Übergang wird abgelehnt), wenn bereits ein anderer Sprint `active` ist.
- **KANN [MAY]** mehrere Sprints gleichzeitig im Status `planned` halten; der nächste Sprint ist immer der niedrigst-nummerierte `planned`-Sprint.
- **SOLLTE [SHOULD]** einen Sprint nach `review` schieben, sobald jedes seiner Features laut `feature`-Spec `done` ist; **MUSS [MUST]** `## Review notes` befüllen und den Mehrwert-Vertrag prüfen, bevor der Übergang nach `closed` erfolgt.
- **MUSS [MUST]** jeden `active → review`-Übergang ablehnen, solange die `features`-Frontmatter-Liste des Sprints leer ist, weil eine leere Liste den §Mehrwert-Vertrag nicht erfüllen kann (kein Feature kann `verifies_sprint_value` deklarieren); `sprint-execute` und `sprint-review` setzen dieses Gate durch. Die schema-seitige Erlaubnis "verpflichtend, darf leer sein" für `features` (siehe §Frontmatter-Schema) gilt während `planned`; im Moment des Übergangsversuchs `active → review` ist der Leer-Listen-Zustand nicht mehr zulässig.

### Mehrwert-Vertrag

- **MUSS [MUST]** ein nicht-leeres `value_statement` aus Endnutzer-Sicht tragen; operator-interne Sprache ist kein Mehrwert-Statement und **MUSS [MUST]** von `sprint-plan` abgelehnt werden, bevor die Sprint-Datei persistiert wird. Die Ablehnungsregel **MUSS [MUST]** mindestens dann greifen, wenn das Statement mit einem internen Verb in der Hauptsprache des Projekts beginnt oder darum aufgebaut ist (`refactor`, `restructure`, `set up`, `configure`, `clean up`, `migrate`, `bump`, `update dependency`, sowie dieselbe Liste auf Deutsch: `refaktorieren`, `umbauen`, `einrichten`, `konfigurieren`, `aufräumen`, `migrieren`, `aktualisieren`, `Abhängigkeit erneuern`); `sprint-plan` **MUSS [MUST]** die Verletzung mit dem zitierten beanstandeten Verb sichtbar machen und **KANN [MAY]** die Regelliste pro Projekt erweitern. Die Prüfung ist eine Heuristik, kein vollständiger Klassifikator — Operatoren, die wirklich eine endnutzer-orientierte Veränderung liefern und deren Formulierung zufällig mit einem dieser Verben startet, **KÖNNEN [MAY]** die Ablehnung mit einer einzeiligen Begründung in der `## Goal`-Section des Sprints überstimmen.
- **MUSS [MUST]** sicherstellen, dass mindestens ein im Sprint gelistetes Feature sich selbst per Frontmatter-Feld `verifies_sprint_value: acceptance-<n>` (laut Geschwister-Spec `feature`) als Mehrwert-Verifizierer deklariert und dass das benannte Akzeptanzkriterium beim Abhaken das `value_statement` direkt prüft. Das Kriterium des verifizierenden Features **KANN [MAY]** als CLI-Befehl, manueller Demo-Schritt oder Test-Referenz formuliert sein; die Form ist `feature`-Spec-Sache, aber die **Existenz** des Frontmatter-Markers wird hier erzwungen.
- **MUSS [MUST]** das Schließen eines Sprints (`review → closed`) verweigern, wenn kein Feature im Sprint `verifies_sprint_value` deklariert, das benannte Kriterium auf dem Feature nicht existiert oder das benannte Kriterium noch nicht abgehakt ist.
- **MUSS [MUST]** den vollständigen Ort des verifizierenden Kriteriums (`features/<slug>.md` plus `acceptance-<n>`-ID) beim Abschluss in `## Review notes` festhalten, damit zukünftige Leser den Audit-Pfad finden, ohne die Feature-Dateien neu zu durchforsten.

### Artefakt-Vertrag

- **MUSS [MUST]** spätestens beim Übergang nach `review` ein nicht-null `artifact_ref` tragen; ein leeres `artifact_ref` bei `review` ist ein Blocker.
- **KANN [MAY]** `artifact_ref` als Liste von Strings tragen, wenn der Projekttyp in einem Sprint zwei gekoppelte Artefakte ausliefert (zum Beispiel ein CLI-Tool plus Container-Image oder eine Python-Bibliothek plus Doc-Site-Deploy); jeder Listeneintrag **MUSS [MUST]** zu einer Taxonomie-Form aus der Geschwister-Spec `release-artifact` passen.
- **MUSS [MUST]** sicherstellen, dass das referenzierte Artefakt konkret genug ist, um **zum Zeitpunkt des Sprint-Abschlusses** erneut abrufbar zu sein (ein Git-Tag, ein Container-Image-Digest-Tag, eine veröffentlichte Plugin-Version, eine datierte Doc-Site-Deploy-URL); Commit-SHAs allein reichen nicht, sofern das Projekt nicht ausdrücklich per SHA veröffentlicht. Die Spec verspricht keine unbegrenzte Re-Fetchbarkeit über die eigene Aufbewahrungs-Politik des Projekts hinaus: Tag-Löschung oder Registry-Rotation nach Abschluss ist eine separate Sorge (Sache der Archivierungs-Haltung des konsumierenden Repos, nicht dieser Spec).
- **MUSS [MUST]** sicherstellen, dass das Artefakt **produktiv ausrollbar** im Sinne des Projekts ist (für Hobby-Projekte kann "produktiv" auch "die eigene Deploy-Instanz des Operators" bedeuten — aber das Artefakt muss durchgängig lauffähig sein, nicht eine halbfertige Branch).
- **MUSS [MUST]** die Artefakt-Referenz beim Sprint-Abschluss validieren: die Geschwister-Spec `release-artifact` definiert die Validierungsregeln je Projekttyp und das Dispatchen in `release-skill-layer`-Skills; Sprint-Review delegiert an diese Regeln, statt sie nachzuimplementieren.

### Dispatch in die Release-Maschinerie

- **KANN [MAY]**, wenn `sprint-review` läuft und der Projekttyp über `release-publish.yml` veröffentlicht, `release-notes-curate` dispatchen, um den Body des offenen Drafts anzureichern, und `release-publish-trigger` dispatchen, um die Veröffentlichung durchzuführen. Beide Dispatches sind beim Sprint-Abschluss vom Operator opt-in zu bestätigen; `sprint-review` **DARF NICHT [MUST NOT]** unbeaufsichtigt chainen, und der Sprint **MUSS [MUST]** die Operator-Entscheidung (chained oder übersprungen) in `## Review notes` festhalten.
- **DARF NICHT [MUST NOT]** `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id> draft=false` oder einen anderen Pfad aufrufen, der den Draft-Zustand außerhalb von `release-publish.yml` umschaltet. Die Regel kommt aus `release-automation` und `release-skill-layer` und ist auch hier nicht verhandelbar.
- **SOLLTE [SHOULD]**, wenn der Operator beim Abschluss die Curate-/Publish-Verkettung ablehnt, eine einzeilige Notiz in `## Review notes` hinterlassen, die festhält, wer oder was die Veröffentlichung später dispatchen soll (Operator manuell, automatisierter Post-Merge-Job oder ein Folge-Sprint), damit der Audit-Pfad nicht reißt.

### Roadmap- und Feature-Verknüpfung

- **MUSS [MUST]** sicherstellen, dass jeder Eintrag in `roadmap_items` auf ein in `project/roadmap.md` definiertes `R-<n>` auflöst; ein Sprint **KANN [MAY]** eine leere `roadmap_items`-Liste tragen (zum Beispiel ein Härtungs-Sprint, der für sich selbst existiert), aber seine Features **MÜSSEN [MUST]** trotzdem laut Geschwister-Spec `feature` ein `roadmap_item` tragen — die Härtungs-Absicht zuerst als Roadmap-Item deklarieren, die Features daran verknüpfen und dann die `roadmap_items` des Sprints leer lassen, wenn das Härtungs-Item das einzige ist. Die `## Goal`-Section des Sprints **MUSS [MUST]** den Leerlisten-Fall ausdrücklich benennen, wenn er auftritt, die Härtungs-Absicht nennen und das Roadmap-Item zitieren, an das die Features verknüpft sind.
- **MUSS [MUST]** sicherstellen, dass jeder Eintrag in `features` auf eine Feature-Datei unter `project/features/` auflöst; das Frontmatter der Feature-Datei **MUSS [MUST]** `sprint: <NNNN>` tragen, das die Sprint-Nummer matcht, sonst ist die Rück-Referenz gebrochen (die Rück-Referenz selbst regelt die Geschwister-Spec `feature`).
- **MUSS [MUST]** die `## Features`-Bullet-Liste im Body mit der `features`-Frontmatter-Liste in Sync halten; `sprint-execute` ist der kanonische Durchsetzungspunkt und **MUSS [MUST]** sich weigern, eine ohne die andere in derselben Operation zu aktualisieren.
- **KANN [MAY]** Features mid-sprint im Status `active` hinzufügen oder entfernen, **DARF NICHT [MUST NOT]** aber das `value_statement` nach Aktivierung ändern; passt das Statement nicht mehr zur Realität, **MUSS [MUST]** der Sprint abgebrochen und neu geplant werden.

### Hobby-Skala-Varianz

- **DARF NICHT [MUST NOT]** ein Dauer-Ziel, eine Kalender-Frist oder eine Kadenz-Annahme erzwingen; `started` und `closed` werden nachträglich erfasst, nicht im Voraus prognostiziert.
- **SOLLTE [SHOULD]** pausierte Sprints tolerieren: ein Sprint kann längere Zeit in `active` liegen; die Mehrwert- und Artefakt-Verträge gelten beim Abschluss unabhängig von der verstrichenen Zeit.
- **KANN [MAY]** einen Sprint `cancelled` markieren, wenn sich die Realität schneller ändert als der Sprint sich anpassen kann, und **KANN [MAY]** `cancelled` aus `planned`, `active` oder `review` erreichen; Abbruch ist ein erstklassiges Ergebnis, kein Fehlerzustand, und **MUSS [MUST]** in `## Review notes` mit einer einabsätzigen Begründung dokumentiert werden, bevor `cancelled` final wird. Die Begründung **MUSS [MUST]** den Lifecycle-Status nennen, in dem der Sprint zum Zeitpunkt des Abbruchs war, und warum Erholung aktuell nicht machbar war.

## Akzeptanzkriterien

- [ ] Jeder Sprint existiert als genau eine Datei unter `project/sprints/<NNNN>-<slug>.md` mit monoton vergebenem `<NNNN>`; keine Sprint-Nummer wird über die Projekt-Lebensdauer wiederverwendet.
- [ ] Das Frontmatter jedes Sprints trägt die neun Schema-Felder (`number`, `status`, `started`, `ended`, `value_statement`, `artifact_ref`, `last_commit`, `roadmap_items`, `features`) in der festgelegten Reihenfolge; Lints flaggen unbekannte Schlüsselwörter und lehnen `closed` als Frontmatter-Feldname ab (das Feld heißt `ended`, weil es sowohl `closed` als auch `cancelled` als terminale Zustände abdeckt).
- [ ] Der Body jedes Sprints trägt die vier verpflichtenden Level-2-Sections (`Goal`, `Features`, `Out of scope`, `Review notes`) in der festgelegten Reihenfolge; fehlende Sections schlagen die Validierung.
- [ ] Kein Sprint wechselt `active → closed` ohne Durchlauf durch `review`; Verstöße gegen den Übergangsgraphen werden von `sprint-execute` und `sprint-review` abgelehnt.
- [ ] Kein Sprint bewegt ein Feature nach `in_progress`, solange ein anderer Sprint im Status `active` ist; `sprint-execute` lässt den Feature-Übergang fehlschlagen, statt einen parallelen aktiven Sprint zu starten.
- [ ] Jeder geschlossene Sprint hat mindestens ein Feature in seiner `features`-Liste, dessen Frontmatter `verifies_sprint_value: acceptance-<n>` deklariert, und das benannte Akzeptanzkriterium ist abgehakt; `sprint-review` verweigert sonst den Abschluss.
- [ ] Jeder Sprint, der `review` erreicht, trägt ein nicht-null `artifact_ref`, dessen Form (String oder Liste) zur Geschwister-Spec `release-artifact` für den erkannten Projekttyp passt; reine Commit-SHA-Referenzen schlagen fehl, sofern das Projekt nicht per SHA veröffentlicht.
- [ ] `last_commit` jedes geschlossenen Sprints ist nicht-null und zeigt auf einen Commit, der vom in `artifact_ref` referenzierten Artefakt erreichbar ist; `sprint-execute` ist gemäß §Frontmatter-Schema die kanonische Schreib-Autorität für dieses Feld (es schreibt es inkrementell, sobald Features im Sprint `done` erreichen), und `sprint-review` bestätigt beim Übergang `active → review`, dass das Feld nicht-null und konsistent mit `artifact_ref` ist, statt es zu erzeugen.
- [ ] Die `## Features`-Body-Section und die `features`-Frontmatter-Liste sind bei jeder Sprint-Mutation identisch; `sprint-execute` lehnt Teil-Updates ab.
- [ ] Jeder Eintrag in `roadmap_items` löst auf ein `R-<n>` in `project/roadmap.md` auf; jeder Eintrag in `features` löst auf eine Feature-Datei auf, deren eigenes Frontmatter die `number` dieses Sprints rückreferenziert.
- [ ] Jede Operator-Entscheidung zur `release-skill-layer`-Verkettung beim Sprint-Abschluss (chained oder übersprungen) ist in `## Review notes` festgehalten; Sprint-Dateien, die ohne festgehaltene Entscheidung geschlossen werden, schlagen die Validierung.
- [ ] In den `## Review notes` jedes abgebrochenen Sprints steht eine ein-absätzige Begründung, die den Lifecycle-Status zum Abbruchszeitpunkt nennt (`planned`, `active` oder `review`); fehlt die Begründung oder die Status-Angabe, schlägt die Validierung.
- [ ] Kein Sprint wechselt `active → review`, solange seine `features`-Frontmatter-Liste leer ist; eine leere Liste machte den Mehrwert-Vertrag in §Mehrwert-Vertrag unerfüllbar, daher lehnen `sprint-execute` und `sprint-review` den Übergang mit einer expliziten Fehlermeldung ab, die auf die leere Liste zeigt.

## Offene Fragen

- Soll ein Projekt jemals parallele Sprint-Spuren haben (zum Beispiel eine Endnutzer-Spur und eine Infrastruktur-Spur), und wenn ja, wie lockert sich die Invariante "höchstens ein aktiver Sprint"? Verschoben, bis ein Portfolio-Projekt parallele Spuren wirklich braucht; die einfachere Invariante deckt heute Hobby-Skala ab.
- Soll `value_statement` ein strukturiertes Format akzeptieren (Audience-ID + Nutzen) statt Freitext, damit nachgelagertes Tooling Sprints nach Audience gruppieren kann? Verschoben, bis ein echtes Reporting-Bedürfnis erscheint; strukturierte Statements bringen Zeremonie für wenig Nutzen auf Hobby-Skala.
- Sollen `cancelled`-Sprints zusätzlich zur Begründungs-Prosa einen `cancelled_reason`-Enum tragen (`replanned`, `descope`, `obsoleted`, `paused-indefinitely`)? Billig nachzurüsten; aktuell reicht der Begründungs-Absatz.
- Mid-Sprint-Hotfixes werden als Out-of-Band-Artefakte unter `project/release-artifacts/out-of-band/` laut Geschwister-Spec `release-artifact` erfasst; eine offene Frage ist, ob ein solches Out-of-Band-Release zusätzlich rückwirkend in den `## Review notes` des aktuell aktiven Sprints vermerkt werden sollte. Verschoben, bis ein realer Hotfix-Fall auftaucht.
- Die Liste der operator-internen Verben für die Ablehnung in §Mehrwert-Vertrag ist heuristisch. Soll sie nach `.github/sprint-rejection-rules.yml` wandern, damit jedes Repo sie erweitern kann, ohne die Spec zu forken? Verschoben, bis ein Projekt eine Pro-Repo-Erweiterung wirklich braucht.
