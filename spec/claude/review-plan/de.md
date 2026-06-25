# Review-Plan-Artefakt

Status: draft
Portfolio-Scope: portfolio

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
- Eine `.audits/`-Index-/Registry-Datei — offene Pläne werden durch Scannen des Verzeichnisses aufgezählt (zum Beispiel `grep -l "status: open" .audits/**/*.md`); ein Index wäre eine drift-anfällige zweite Quelle der Wahrheit, die dem Wegwerf-Lebenszyklus ohne Ansammlung widerspricht

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUST, SHOULD, MAY. Eine atomare Anforderung pro Bullet. -->

### Dateiort und Namensgebung

- **MUSS [MUST]** unter `.audits/<review-type>/<target-slug>.md` liegen, wobei:
  - `<review-type>` der Review-Spec-Slug ist (z. B. `skill-review`, `agent-review`)
  - `<target-slug>` eine ASCII-Kebab-Case-Ableitung des Bezeichners des reviewten Artefakts ist (bei Skill: Skill-Name; bei Agent: Agent-Name)
- **MUSS [MUST]** den `<review-type>` ausschließlich über das Unterverzeichnis kodieren; der Basename **MUSS NICHT [MUST NOT]** ihn wiederholen (kein `skill-review-<target>.md`) — konsumierende Specs zitieren den blanken `<target-slug>.md`-Basename, und die Commit-Message der Löschung trägt den Review-Typ bereits
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

### Schweregrad-Skala

Dieser Abschnitt ist die einzige kanonische Quelle für das Schweregrad-Vokabular über jedes Audit-, Review- und Reife-Artefakt im Portfolio hinweg. Andere Specs **MÜSSEN [MUST]** auf diesen Abschnitt verweisen, statt eine eigene Skala zu definieren.

- **MUSS [MUST]** jedes Finding in genau eine dieser vier Schweregrad-Stufen einordnen, in Title Case, in dieser Reihenfolge abnehmender Auswirkung:
  - **Critical**: verletzt ein MUST in der Quell-Spec oder blockiert direkt die Beförderung / das Mergen des reviewten Artefakts (tragende Open Question in einem Pre-Promotion-Lauf, Geist-Referenz auf eine nicht existierende Spec, MUST↔MUST-Widerspruch zwischen zwei bereits beförderten Specs)
  - **Warning**: verletzt ein SHOULD in der Quell-Spec oder benennt reale Mehrdeutigkeit / Drift / Abdeckungslücke, die ein sorgfältiger Leser noch umgehen kann, die aber vor dem nächsten Release behoben werden sollte
  - **Suggestion**: identifiziert eine MAY-Klassen-Gelegenheit, eine stilistische Verbesserung oder einen Ein-Zeilen-Fix, der das Artefakt aufwertet, ohne Verletzungs-Klasse zu sein
  - **Info**: eine Beobachtung, eine bewusste Design-Anerkennung, eine infrastruktur-abhängige Notiz oder ein Querverweis zurück auf ein anderswo bereits getracktes Finding; keine Aktion erforderlich
- **MUSS NICHT [MUST NOT]** zusätzliche Schweregrad-Stufen erfinden (kein `BLOCKER`, kein `MAJOR/MINOR`, kein `P0/P1/P2`); Reviewer, die eine weitere Stufe für nötig halten, schlagen eine Spec-Änderung vor, keine lokale Erweiterung
- **MUSS [MUST]** diese Labels wortwörtlich verwenden — Title Case, keine Abkürzungen, keine Großbuchstaben-Varianten — in `## Summary`-Zählungen, `## Findings`-Unter-Abschnitts-Überschriften und jeder finding-bezogenen Annotation, damit nachgelagerte Tools sie deterministisch grepen können
- **MUSS NICHT [MUST NOT]** einen Schweregrad allein auf Basis lokaler Einschätzung absenken; Abweichung von der Klassifikation ist eine dokumentierte Waiver-Notiz im `## Processing log` des Plans, keine stille Re-Klassifikation

### Plan-Körper-Struktur

- **MUSS [MUST]** diese Abschnitte in dieser Reihenfolge mit exakt diesen Überschriften enthalten:
  1. `## Scope` — ein Absatz, der das Ziel nennt, was reviewt wurde (Frontmatter, Body, Beispiele, …) und was explizit außerhalb lag
  2. `## Summary` — Bullet-Zählungen pro Schweregrad (`Critical`, `Warning`, `Suggestion`, `Info`) plus eine Einzeiler-Go/No-Go-Aussage
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
- **MUSS [MUST]** Findings unter den Schweregrad-Unter-Abschnitten `### Critical`, `### Warning`, `### Suggestion`, `### Info` gruppieren, in dieser Reihenfolge; einen Unter-Abschnitt nur weglassen, wenn er null Einträge hat
- **MUSS [MUST]** die auslösende Spec-Anforderung im eckigen Klammerpräfix zitieren, damit eine verarbeitende Instanz jedes Finding auf ein konkretes MUST / SHOULD / MAY zurückführen kann; Erfindungen ohne Spec-Zitat sind keine gültigen Findings
- **SOLLTE [SHOULD]** Einträge innerhalb eines Schweregrad-Abschnitts nach betroffenem Bereich sortieren (Frontmatter → Body → Tools → Beispiele), damit verwandte Einträge zusammen adressiert werden können
- **KANN [MAY]** ein Finding mit einem abschließenden `→ deferred: <issue-url>` annotieren, wenn die verarbeitende Instanz entscheidet, dass der Punkt echt aber außerhalb des aktuellen Plan-Zyklus ist; vertagte Einträge zählen für den Lebenszyklus als geschlossen, tragen aber den Link, sodass das getrackte Issue zur neuen Heimat wird

### Lebenszyklus

- **MUSS [MUST]** pro Review-Aufruf frisch erzeugt werden; ein Re-Run gegen dasselbe Ziel **MUSS [MUST]** den bestehenden Plan in einem einzigen Commit überschreiben und den `status` des vorherigen Plans in der Commit-Message des Überschreibens auf `superseded` setzen — niemals den alten Plan in den neuen editieren
- **MUSS [MUST]**, wenn das Review-Ziel mitten im Zyklus umbenannt wird, die Plan-Datei per `git mv` mitumbenennen (erhält die `git log --follow`-Linie), das Frontmatter-Feld `target` aktualisieren und den Move in der Commit-Message benennen; **nicht** neu erzeugen, damit der teilweise Abhak-Stand und das `## Processing log` überleben. Das ist abzugrenzen vom Supersede-Pfad oben, der auf einen Re-Run mit neuen Findings begrenzt ist — nicht auf eine Ziel-Umbenennung, die dieselben Findings unter einem neuen Bezeichner behält
- **MUSS [MUST]** Einträge nur dann als `- [x]` markieren, wenn sowohl der Fix gelandet ist als auch der `Verify`-Schritt ausgeführt wurde; Teil-Fixes bleiben `- [ ]`
- **MUSS [MUST]** pro Schließung eine Zeile an `## Processing log` anhängen, in der Form: `YYYY-MM-DD — <item-shorthand> — <getätigte Aktion> — <verifiziert von>`; `<verifiziert von>` ist ein einzelnes Freitext-Akteur-Label (zum Beispiel `human:nolte`, `agent:agent-review`) und **MUSS NICHT [MUST NOT]** in strukturierte Username- / Session- / Agent-Unterfelder zerlegt werden — gemäß §Nicht-Ziele gibt die Spec nicht vor, wer oder was den Plan verarbeitet, und der Commit-Autor trägt bereits die Maschinen-Identität
- **MUSS NICHT [MUST NOT]** die Plan-Datei löschen, solange ein offener `- [ ]` `Critical` besteht; `Warning` / `Suggestion` / `Info`-Einträge **KÖNNEN [MAY]** auf getrackte Issues vertagt werden, um das Löschen zu ermöglichen
- **MUSS [MUST]** die Plan-Datei löschen, wenn jeder Eintrag entweder `- [x]` ist oder eine `→ deferred: <url>`-Annotation trägt; die Commit-Message der Löschung **MUSS [MUST]** `review(<review-type>): close <target> — <C>C/<W>W/<S>S/<I>I` lauten (Zählungen von Critical, Warning, Suggestion, Info zum Zeitpunkt der Erzeugung), sodass das Git-Log der durchsuchbare Audit-Trail ist
- **SOLLTE [SHOULD]** beim Löschen des Plans auch getrackte Issues schließen, auf die vertagte Einträge verweisen, sofern der zugrundeliegende Fix anderswo gelandet ist — die Commit-Message der Löschung benennt diese Issues in ihrem Body
- **SOLLTE [SHOULD]** als veraltet gelten und neu bewertet werden — gegen die aktuelle `repo-revision` neu verarbeitet oder explizit auf `superseded` gesetzt —, wenn der Plan länger als sechs Monate offen war, ohne dass ein neuer `## Processing log`-Eintrag hinzukam. Das spiegelt den Lebenszyklus des Geschwister-Sweep-Artefakts wider, damit beide Audit-Artefakt-Specs ein konsistentes Veraltungs-Vokabular tragen; es ist eine Erkennungs- und Sichtbarmachungs-Konvention, kein hartes Ablaufdatum und kein automatisches Löschen

### Bezug zu anderen Specs

- **MUSS [MUST]** aus jeder Review-Spec referenziert werden, die einen Plan produziert (`skill-review`, `agent-review` und jeder künftige Review-Typ) — die Review-Spec besitzt die Kriterien, diese Spec besitzt die Artefakt-Form
- **MUSS NICHT [MUST NOT]** als Ausgabe eines **datierten periodischen Audit-Records** verwendet werden: `spec-drift-audit` (`.audits/spec-drift/<YYYY>-Q<n>.md`) und `portfolio-inflight-management` (`.audits/portfolio-inflight/<YYYY-MM-DD>.md`) nutzen die Vier-Sektionen-Struktur und das Severity-Vokabular dieser Spec weiter, folgen aber ihrer eigenen datierten Dateinamens- und Nicht-Wegwerf-Lebenszyklus-Konvention; die No-Timestamp- und Ein-Plan-pro-Ziel-Regeln dieser Spec gelten **nicht** für jene Records, die nicht bei Verarbeitungs-Abschluss gelöscht werden sollen
- **SOLLTE [SHOULD]**, wenn ein Review-Agent (z. B. `audience-review`) einen Report in der Hauptkonversation emittiert, den strukturierten Plan trotzdem unter `.audits/<review-type>/<target>.md` persistieren, damit der Verarbeitungsvertrag unabhängig davon konsistent ist, wer das Review gefahren hat
- **SOLLTE [SHOULD]** `spec/project/parallel-working-copies/` §Audit-Artefakte in mehreren Worktrees konsultieren, wenn der Plan in einem Worktree statt im primären Checkout erzeugt wird; die Per-(Review-Typ, Ziel)-Eindeutigkeitsregel aus dieser Spec ist jeweils nur innerhalb eines Working Tree beobachtbar, und die worktree-lokalen Commit-, Transfer- und Cleanup-Regeln leben dort
- **SOLLTE [SHOULD]** in Repositories, die direkte Pushes nach `develop` verbieten, den Plan und den Fix, den er beschreibt, im selben Feature-Branch-PR landen lassen — Erzeugen, Abhaken, `## Processing log`-Aktualisierungen und der Lösch-Commit alle in einem Diff — gemäß `spec/project/parallel-working-copies/` §Audit-Artefakte; ein eigenständiger früherer PR ist Reviews vorbehalten, die vor jeder Fix-Abgrenzung laufen

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] `.audits/` existiert im Repository und wird von Git getrackt (nicht in `.gitignore`)
- [ ] Jede Plan-Datei unter `.audits/` parst als gültiges Markdown mit YAML-Frontmatter, das `review-type`, `target`, `target-kind`, `specs-applied`, `repo-revision`, `created`, `status` enthält
- [ ] Jede Plan-Datei enthält die vier Pflicht-Abschnitte (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) mit genau diesen englischen Überschriften
- [ ] Jedes Finding in einem Plan verwendet die vier-Zeilen-Struktur (einleitender Satz + `Where` / `Fix` / `Verify`) und zitiert eine Spec-Anforderung im eckigen Klammerpräfix
- [ ] Keine Plan-Datei existiert mit offenem `- [ ]` `Critical` und `status: complete`
- [ ] Jede Plan-Löschung in `git log` wird von einer Commit-Message begleitet, die `review(<review-type>): close <target> — <counts>` entspricht, sodass der Audit-Trail durchsuchbar ist
- [ ] Pro (`review-type`, `target`) existiert zu jedem Commit höchstens eine Plan-Datei — ein Re-Run ersetzt statt zu akkumulieren
- [ ] Die Specs `skill-review` und `agent-review` verweisen beide auf diese Spec als autoritatives Output-Format

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Siehe `.audits/decisions/2026-06-06-settle-open-questions.md` für die Einzelentscheidungen und Begründungen._
