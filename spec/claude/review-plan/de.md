# Review-Plan-Artefakt

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Bedarf oder welche Einschränkung treibt sie? -->

Reviews von Claude-Code-Artefakten — ein Skill gegen `skill-management`, ein Agent gegen `agent-management`, künftige Review-Typen — müssen ein Ergebnis liefern, das ein anderer Akteur (Autor, Reviewer, nachgelagerter Agent, rufender Skill) Schritt für Schritt abarbeiten kann. Wenn jeder Reviewer eine private Ergebnisform erfindet, müssen konsumierende Akteure das Format pro Review rückentwickeln, Plugin-Entwickler können nicht gegen die Ausgabe skripten, und Findings gehen zwischen Läufen verloren. Diese Spec definiert ein einziges, wiederverwendbares On-Disk-Artefakt — den *Review-Plan* — den jede Review-Prozedur im `nolte-shared`-Plugin emittiert. Der Plan ist abarbeitbar, in sich abgeschlossen, lebt im Repository unter `.audits/`, wird punktweise abgearbeitet und entfernt, sobald jeder Punkt adressiert ist. Seine Git-Historie ist der bleibende Audit-Trail; die Datei selbst ist vergänglich.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, ergebnisorientiert. -->
- Jedes Review im Plugin erzeugt dieselbe strukturelle Ausgabeform, damit Plugin-Entwickler, Autoren und nachgelagerte Automatisierung sie ohne Formatverhandlung parsen und verarbeiten können
- Jedes Finding ist ein **abarbeitbarer Checkbox-Punkt**: Beim Lesen eines Punktes erfährt die verarbeitende Instanz, was falsch ist, wo, wie es zu beheben ist und wie die Behebung zu verifizieren ist
- Ein Plan ist **in sich abgeschlossen** — er trägt genug Kontext (Ziel, angewandte Specs, abgesteckter Scope, Revision), dass ein neuer Akteur ihn aufnehmen kann, ohne das Review erneut laufen zu lassen
- Der **Lebenszyklus des Plans ist explizit**: pro Review frisch erzeugen, committen, abarbeiten, entfernen nach vollständiger Verarbeitung — keine Ansammlung veralteter Pläne, keine still liegen gebliebenen halb-abgearbeiteten Pläne
- Der Audit-Trail überlebt das Löschen: jedes Erzeugen / Aktualisieren / Entfernen ist ein Commit, sodass `git log --follow` auf einem entfernten Plan rekonstruiert, was reviewt und wie es geschlossen wurde

## Nicht-Ziele
<!-- Was explizit außerhalb des Scopes liegt. Verhindert Scope Creep. -->
- Definition der Review-**Kriterien** für einen bestimmten Artefakt-Typ — das gehört zu `skill-review`, `agent-review` und künftigen Review-Specs
- Vorgabe, **wer** oder **was** den Plan verarbeitet (Mensch, Claude in der Hauptkonversation, dedizierter Agent, CI-Automatisierung) — der Plan ist ein Format, keine Pipeline
- Versionierung von Plänen über Zeit — pro (Ziel, Review-Typ) existiert genau ein Plan zugleich; ein Re-Run **ersetzt** den Plan statt ihn zu revisionieren
- Langlebige Audit-Register — die Pläne dieser Spec sind Wegwerf-Artefakte; für ein permanentes Quartals-Audit-Record gilt `spec-drift-audit`
- CI-Reporting-Formate (SARIF, JUnit, …) — der Plan ist eine menschen- und LLM-freundliche Markdown-Datei, kein CI-Ergebnis-Austauschformat

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUST, SHOULD, MAY. Eine atomare Anforderung pro Bullet. -->

### Dateiort und Namensgebung

- **MUSS [MUST]** unter `.audits/<review-type>/<target-slug>.md` liegen, wobei:
  - `<review-type>` der Review-Spec-Slug ist (z. B. `skill-review`, `agent-review`)
  - `<target-slug>` eine ASCII-Kebab-Case-Ableitung des Bezeichners des reviewten Artefakts ist (bei Skill: Skill-Name; bei Agent: Agent-Name)
- **MUSS NICHT [MUST NOT]** einen Zeitstempel oder eine laufende Nummer im Dateinamen enthalten — es gibt zu jedem Zeitpunkt genau **einen** Plan pro (Review-Typ, Ziel); ein Re-Run überschreibt den bestehenden Plan
- **MUSS [MUST]** `.audits/` in Git einchecken (nicht ge-`.gitignore`-d), damit Pläne in Pull-Request-Diffs sichtbar sind und der Review-Pfad geteilt wird
- **SOLLTE [SHOULD]**, wenn das reviewte Artefakt außerhalb des aktuellen Repositories liegt (z. B. Review der Kopie eines Skills in einem Plugin-Consumer), den absoluten oder repo-relativen Pfad des Ziels im Frontmatter-Feld `target` führen, während der Dateiname weiterhin nur den Slug nutzt

### Frontmatter

- **MUSS [MUST]** mit YAML-Frontmatter beginnen und mindestens folgende Felder enthalten:
  - `review-type` — der Review-Spec-Slug (String)
  - `target` — der (repo-relative) Pfad des reviewten Artefakts
  - `target-kind` — der Artefakttyp: `skill`, `agent` oder ein künftiger Klassifikator
  - `specs-applied` — eine YAML-Liste von Spec-Slugs mit dem Git-SHA oder Tag der kanonischen Version, gegen die das Review lief
  - `repo-revision` — der Git-SHA des Ziel-Repositories zum Review-Zeitpunkt
  - `created` — ISO-8601-Datum, an dem der Plan erzeugt wurde
  - `status` — einer von `open`, `in-progress`, `complete`, `superseded`
- **MUSS [MUST]** `status` beim ersten Abhaken eines Punktes auf `in-progress` setzen, auf `complete`, wenn jeder Punkt entweder `- [x]` oder ein getrackter Follow-up ist, und auf `superseded`, wenn ein Re-Run den Plan vor Abschluss ersetzt
- **MUSS NICHT [MUST NOT]** Werte erfinden; wenn ein Feld nicht aus der Quelle gelesen werden kann (z. B. kein Git-SHA, weil das Ziel noch nicht committed ist), lautet der Wert `unknown` — keine Vermutung

### Plan-Körper-Struktur

- **MUSS [MUST]** diese Abschnitte in dieser Reihenfolge mit exakt diesen Überschriften enthalten:
  1. `## Scope` — ein Absatz, der das Ziel nennt, was reviewt wurde (Frontmatter, Body, Beispiele, …) und was explizit außerhalb lag
  2. `## Summary` — Bullet-Zählungen pro Schweregrad (`BLOCKER`, `WARNING`, `SUGGESTION`, `INFO`) plus eine Einzeiler-Go/No-Go-Aussage
  3. `## Findings` — die abarbeitbare Liste; ein Unter-Abschnitt pro vorhandenem Schweregrad
  4. `## Processing log` — append-only, eine Zeile pro geschlossenem Punkt, die festhält, was getan wurde und von wem
- **MUSS [MUST]** die Abschnittsüberschriften auch dann in Englisch halten, wenn die Dokumentationssprache des umgebenden Projekts nicht Englisch ist, damit nachgelagerte Tools sie deterministisch grepen können

### Findings-Format

- **MUSS [MUST]** jedes Finding als Markdown-Checkbox-Eintrag in `## Findings` ausdrücken, mit folgender Struktur:

  ```
  - [ ] [<spec-slug>.<requirement-shorthand>] <Einzeiler-Beschreibung, was falsch ist>.
        Where: <Datei:Zeile oder Abschnittsreferenz>.
        Fix: <konkrete Aktion — einzeilig>.
        Verify: <wie die Behebung bestätigt wird — einzeilig>.
  ```

  Die vier beschrifteten Zeilen (`Where`, `Fix`, `Verify` und der einleitende Satz) **MÜSSEN [MUST]** alle vorhanden sein. Wenn ein Feld wirklich nicht zutrifft, schreibe `n/a` mit einem Wort Begründung, statt die Zeile wegzulassen
- **MUSS [MUST]** Findings unter den Schweregrad-Unter-Abschnitten `### BLOCKER`, `### WARNING`, `### SUGGESTION`, `### INFO` gruppieren, in dieser Reihenfolge; einen Unter-Abschnitt nur weglassen, wenn er null Einträge hat
- **MUSS [MUST]** die auslösende Spec-Anforderung im eckigen Klammerpräfix zitieren, damit eine verarbeitende Instanz jedes Finding auf ein konkretes MUST / SHOULD / MAY zurückführen kann; Erfindungen ohne Spec-Zitat sind keine gültigen Findings
- **SOLLTE [SHOULD]** Einträge innerhalb eines Schweregrad-Abschnitts nach betroffenem Bereich sortieren (Frontmatter → Body → Tools → Beispiele), damit verwandte Einträge zusammen adressiert werden können
- **KANN [MAY]** ein Finding mit einem abschließenden `→ deferred: <issue-url>` annotieren, wenn die verarbeitende Instanz entscheidet, dass der Punkt echt aber außerhalb des aktuellen Plan-Zyklus ist; vertagte Einträge zählen für den Lebenszyklus als geschlossen, tragen aber den Link, sodass das getrackte Issue zur neuen Heimat wird

### Lebenszyklus

- **MUSS [MUST]** pro Review-Aufruf frisch erzeugt werden; ein Re-Run gegen dasselbe Ziel **MUSS [MUST]** den bestehenden Plan in einem einzigen Commit überschreiben und den `status` des vorherigen Plans in der Commit-Message des Überschreibens auf `superseded` setzen — niemals den alten Plan in den neuen editieren
- **MUSS [MUST]** Einträge nur dann als `- [x]` markieren, wenn sowohl der Fix gelandet ist als auch der `Verify`-Schritt ausgeführt wurde; Teil-Fixes bleiben `- [ ]`
- **MUSS [MUST]** pro Schließung eine Zeile an `## Processing log` anhängen, in der Form: `YYYY-MM-DD — <item-shorthand> — <getätigte Aktion> — <verifiziert von>`
- **MUSS NICHT [MUST NOT]** die Plan-Datei löschen, solange ein offener `- [ ]` `BLOCKER` besteht; `WARNING` / `SUGGESTION` / `INFO`-Einträge **KÖNNEN [MAY]** auf getrackte Issues vertagt werden, um das Löschen zu ermöglichen
- **MUSS [MUST]** die Plan-Datei löschen, wenn jeder Eintrag entweder `- [x]` ist oder eine `→ deferred: <url>`-Annotation trägt; die Commit-Message der Löschung **MUSS [MUST]** `review(<review-type>): close <target> — <B>B/<W>W/<S>S/<I>I` lauten (Zählungen von BLOCKER, WARNING, SUGGESTION, INFO zum Zeitpunkt der Erzeugung), sodass das Git-Log der durchsuchbare Audit-Trail ist
- **SOLLTE [SHOULD]** beim Löschen des Plans auch getrackte Issues schließen, auf die vertagte Einträge verweisen, sofern der zugrundeliegende Fix anderswo gelandet ist — die Commit-Message der Löschung benennt diese Issues in ihrem Body

### Bezug zu anderen Specs

- **MUSS [MUST]** aus jeder Review-Spec referenziert werden, die einen Plan produziert (`skill-review`, `agent-review` und jeder künftige Review-Typ) — die Review-Spec besitzt die Kriterien, diese Spec besitzt die Artefakt-Form
- **MUSS NICHT [MUST NOT]** als Ausgabe von `spec-drift-audit` verwendet werden; jene Spec persistiert ein quartalsweises Audit-Record, das nicht bei Verarbeitungs-Abschluss gelöscht werden soll
- **SOLLTE [SHOULD]**, wenn ein Review-Agent (z. B. `audience-review`) einen Report in der Hauptkonversation emittiert, den strukturierten Plan trotzdem unter `.audits/<review-type>/<target>.md` persistieren, damit der Verarbeitungsvertrag unabhängig davon konsistent ist, wer das Review gefahren hat

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] `.audits/` existiert im Repository und wird von Git getrackt (nicht in `.gitignore`)
- [ ] Jede Plan-Datei unter `.audits/` parst als gültiges Markdown mit YAML-Frontmatter, das `review-type`, `target`, `target-kind`, `specs-applied`, `repo-revision`, `created`, `status` enthält
- [ ] Jede Plan-Datei enthält die vier Pflicht-Abschnitte (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) mit genau diesen englischen Überschriften
- [ ] Jedes Finding in einem Plan verwendet die vier-Zeilen-Struktur (einleitender Satz + `Where` / `Fix` / `Verify`) und zitiert eine Spec-Anforderung im eckigen Klammerpräfix
- [ ] Keine Plan-Datei existiert mit offenem `- [ ]` `BLOCKER` und `status: complete`
- [ ] Jede Plan-Löschung in `git log` wird von einer Commit-Message begleitet, die `review(<review-type>): close <target> — <counts>` entspricht, sodass der Audit-Trail durchsuchbar ist
- [ ] Pro (`review-type`, `target`) existiert zu jedem Commit höchstens eine Plan-Datei — ein Re-Run ersetzt statt zu akkumulieren
- [ ] Die Specs `skill-review` und `agent-review` verweisen beide auf diese Spec als autoritatives Output-Format

## Offene Fragen
<!-- Ungelöste Entscheidungen, bekannte Unbekannte, Punkte, die eine Stakeholder-Antwort brauchen. -->
- Soll `## Processing log` die Akteur-Identität (menschlicher Username, Claude-Session, Agent-Typ) als strukturierte Felder erfassen, oder reicht freier Text für die aktuelle Skala?
- Wird eine `.audits/`-Index-Datei benötigt, die offene Pläne auflistet, oder reicht `ls .audits/**/*.md`?
- Sollen Plan-Dateinamen den Review-Typ-Präfix auch im Basenamen tragen (`skill-review-<target>.md`) für flachere `ls`-Ansichten, oder ist die Unterverzeichnis-Gruppierung vorzuziehen?
- Wenn ein Review-Ziel mitten im Zyklus umbenannt wird: Wird die Plan-Datei mitumbenannt (und der Rename-Commit benennt den Move) oder frisch neu erzeugt?
- Muss diese Spec ein maximales Alter eines offenen Plans vorgeben, jenseits dessen er als veraltet gilt und entweder neu verarbeitet oder explizit superseded wird?
- Wie interagiert der Plan-Lebenszyklus mit Repositories, die direkte Pushes nach `develop` verbieten — landet der Plan im selben PR wie der Fix, den er beschreibt, oder als separater früherer PR?
