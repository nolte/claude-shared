# Diagramm-Vorschläge in Dokumentations-Prosa

Status: draft

## Kontext
Die MkDocs-Dokumentation im Portfolio nutzt Mermaid als kanonisches Diagramm-Werkzeug (siehe `spec/project/mermaid-diagrams/`). Die Mermaid-Spec regelt, wie ein Diagramm aufgesetzt, geschrieben und synchron gehalten wird, sobald es existiert—sie schweigt aber zum umgekehrten Problem: Prosa, die ein Diagramm **tragen sollte** und keines hat. Heute ist die Entscheidung, ein Diagramm zu ergänzen, eine unbegleitete Autoren-Einschätzung, und die Lücke sammelt sich still in Lang-Prosa (Architektur-Übersichten, Workflow-Beschreibungen, Schema-Erklärungen) an, bis ein Leser Beziehungen aus Text rekonstruieren muss, die ein einziges Bild offensichtlich gemacht hätte.

Diese Spec autorisiert einen read-only `diagram-opportunity-reviewer`-Agent (analog zu `mermaid-diagram-reviewer`, aber mit umgekehrter Untersuchungs-Richtung: nicht „ist dieses bestehende Diagramm spec-konform" sondern „ist diese Prosa-Passage ein Kandidat für ein fehlendes Diagramm"). Der Agent scannt Markdown-Quellen, matched Prosa-Muster deterministisch gegen den Mermaid-§Diagramm-Katalog und gibt eine audit-freundliche Befund-Liste aus. Er schreibt nie; Diagramm-Generierung bleibt bei `mermaid-diagrams-apply`. Er prüft nie bestehende Diagramme; das ist Aufgabe von `mermaid-diagram-reviewer`. Sein einziger lastentragender Job ist es, die **Lücke** zwischen aktueller Prosa und dem Katalog der Diagrammtypen sichtbar zu machen, die denselben Inhalt besser ausdrücken würden—mit strikten Volumen- und Konfidenz-Gates, damit die Betreiberin nie von einem langen Vorschlags-Strom überfordert wird.

Der Agent ist bewusst flexibel über Dokumentations-Kontexte hinweg: derselbe Agent bedient `docs/<lang>/`-Audits, README-Sweeps, ADR-Reviews und Blog-Post-Lektorats-Läufe—die Input-Form ist Single-File, Glob, Verzeichnis oder Pfad-Liste, sodass ein künftiger Dispatcher (`lektorat-apply` als Sub-Check, `audience-doc-author` als Pre-Handoff-Hook, `docs-freshness` als `info`-Severity-Befund-Kategorie) ihn ohne Re-Architektur einbinden kann.

## Ziele
- Jede Prosa-Passage in der Portfolio-Dokumentation, die auf ein Muster aus dem Mermaid-§Diagramm-Katalog passt, wird der Betreiberin als Visualisierungs-Kandidat vorgelegt—mit dem vorgeschlagenen Diagrammtyp und dem exakten Prosa-Trigger, der den Match ausgelöst hat
- Der vorgeschlagene Diagrammtyp ist deterministisch: dasselbe Prosa-Muster schlägt denselben Diagrammtyp über alle Repositories hinweg vor, und der Katalog bleibt im Gleichschritt mit `spec/project/mermaid-diagrams/`
- Befunde sind auditierbar: jeder Match zitiert den Zeilenbereich und den wortgetreuen Prosa-Auszug, der ihn ausgelöst hat, sodass ein Reviewer validieren oder verwerfen kann, ohne die Quelle neu zu lesen
- Das Befund-Volumen pro Lauf ist standardmäßig begrenzt, sodass die Betreiberin auf den Top-Report handeln kann, ohne zu „ignoriere die Vorschlags-Wand"-Muskelgedächtnis erzogen zu werden
- Der Agent ist flexibel über Dokumentations-Kontexte hinweg: derselbe Agent bedient `docs/<lang>/`-Audits, README-Sweeps, ADR-Reviews und Blog-Post-Läufe über einheitliche Input-Formen

## Nicht-Ziele
- Diagramme erzeugen, bearbeiten oder anwenden; das ist Aufgabe von `mermaid-diagrams-apply` und wird dispatcht, nachdem die Betreiberin die Befunde triagiert hat
- Diagramme reviewen, die bereits in der Dokumentation existieren, auf Spec-Konformität, Drift oder Rendering-Setup; das ist Aufgabe von `mermaid-diagram-reviewer`
- Diagramm-Werkzeuge oder -Typen außerhalb des Mermaid-§Diagramm-Katalogs vorschlagen (kein PlantUML, kein draw.io, kein `gitGraph`); der Katalog ist die geschlossene Allowlist
- Nicht-Diagramm-Visualisierungen wie Tabellen, Schema-Boxen, Callouts oder Admonitions vorschlagen; das ist eine künftige Geschwister-Spec, falls je gebraucht, nicht diese
- Prosa übersetzen oder umschreiben; der Agent ist read-only und modifiziert die Quell-Dokumente nie
- Editoriale Qualitäts-Review (Lesbarkeit, Verständlichkeit, Rechtschreibung, Stil, Audience-Fit); das ist `lektorat-apply` / `lektorat-scanner` gemäß `spec/project/lektorat/`

## Anforderungen

### Anwendungsbereich und Input-Formen
- **MUSS [MUST]** jede Kombination aus Single-File-Pfad, Glob-Pattern, Verzeichnis-Pfad oder expliziter Pfad-Liste als Input akzeptieren; alle vier Input-Formen sind gleichwertige First-Class-Einstiegspunkte
- **MUSS [MUST]** standardmäßig `docs/<lang>/**/*.md` für jede konfigurierte Dokumentations-Sprache des Repositorys scannen, wenn kein Input-Pfad übergeben wird; explizite Input-Argumente überschreiben den Default vollständig
- **MUSS [MUST]** das Scannen auf Markdown-Dateien (`*.md`) beschränken; andere Dateitypen werden still ohne Befunde übersprungen
- **KANN [MAY]** gegen jeden Pfad innerhalb des Repositorys aufgerufen werden—README-Dateien, `project/**/*.md`, `spec/**/*.md`, Blog-Posts, ADRs—wenn die Betreiberin ein explizites Pfad-Argument übergibt; nichts im Agent ist auf `docs/` festverdrahtet

### Trigger-zu-Diagrammtyp-Katalog
Der Agent matched Prosa gegen die folgenden Muster. Jedes Muster ist aus dem entsprechenden Eintrag in `spec/project/mermaid-diagrams/` §Diagramm-Katalog deriviert und schlägt den Diagrammtyp vor, den die Mermaid-Spec für diese Struktur als Default benennt. Das Pattern-Matching ist bewusst konservativ: passt eine Passage auf kein Muster mit mindestens `medium`-Konfidenz, wird kein Befund emittiert.

- **`flowchart`**: Dependency-Ketten-Prosa (`X hängt von Y ab`, `X speist Y`, `X konsumiert Z`), Pipeline-Beschreibungen mit drei oder mehr benannten Stufen, Entscheidungsbaum-Prosa mit Bedingungs-Verzweigungen und Listen von drei oder mehr gerichteten Beziehungen zwischen benannten Entitäten
- **`C4Component`**: Architektur-Übersichts-Prosa (`das System besteht aus den Modulen A, B, C`), Grenz-Beschreibungen (`X spricht mit dem externen Dienst Y`) und `wie sieht dieses Repo auf einen Blick aus`-Rahmungen mit benannten Top-Level-Komponenten
- **`classDiagram`**: Typ-Hierarchie-Prosa (`X ist eine Spezialisierung von Y`, `X hat die Attribute/Felder A, B, C und die Methoden foo(), bar()`), Manifest-Struktur-Beschreibungen mit Feldtypen und Plugin- / Skill-Schema-Erklärungen, die sowohl Daten als auch Verhalten benennen
- **`sequenceDiagram`**: geordnete Schritt-Prosa über mehrere Akteure (`zuerst ruft A B auf, dann antwortet B mit X, dann leitet A an C weiter`), Request-Response-Beschreibungen, die beide Endpunkte nennen, und End-to-End-Workflow-Durchläufe vom User-Trigger bis zum Abschluss
- **`erDiagram`**: Schema-Feld-Listungen mit Typ und Kardinalität (`jedes Foo hat 0..n Bars, jeder Bar gehört zu genau einem Foo`), Konfigurationsdatei-Schema-Beschreibungen, die Felder und Wertetypen benennen, und `1 zu n` / `n zu m`-Beziehungs-Prosa

Eine Passage, die mit vergleichbarer Konfidenz auf mehr als ein Muster passt, **MUSS [MUST]** als einzelner Befund mit `diagram_type: ambiguous` emittiert werden, der beide Kandidaten-Typen in einem `candidates`-Array auflistet; der Agent wählt nie still einen aus.

#### Strukturelle Anti-Muster
- **MUSS [MUST]** jeden Kandidaten-Match auf `low`-Konfidenz herabstufen (und damit gemäß §Konfidenz-Modell verwerfen), dessen auslösende Passage vollständig in einer erkannten Nicht-Diagramm-Struktur enthalten ist: FAQ-Frage-Antwort-Paare, eingefasste Befehls- / Install-Sequenzen und flache Fehlermeldungs-Listen. Diese Strukturen liefern häufig Signale, die diagrammfähig aussehen, aber bewusst Prosa sind; das Herabstufen hält die Falsch-Positiv-Rate niedrig, ohne Aufwand der Betreiberin
- Diese eingebaute Anti-Muster-Herabstufung **ergänzt den §Per-Stellen-Mute-Marker, ersetzt ihn nicht:** die Herabstufung ist die geschlossene, deterministische Deny-Liste des Agents für bekannte strukturelle Fälle, während `<!-- diagram-opportunity-skip: <grund> -->` das explizite Pro-Stellen-Override der Betreiberin für alles Übrige bleibt

### Konfidenz-Modell
- **MUSS [MUST]** jedem Kandidaten-Match eine von drei Konfidenz-Stufen zuweisen: `high`, `medium` oder `low`. `high` verlangt mindestens zwei unabhängige Oberflächen-Signale aus demselben Diagrammtyp-Muster in derselben Passage; `medium` verlangt ein starkes Signal; `low` verlangt nur ein schwaches Oberflächen-Signal
- **MUSS [MUST]** `low`-Konfidenz-Matches verwerfen, bevor Befunde emittiert werden; die Betreiberin sieht sie nie. Das ist der primäre Rauschen-Kontroll-Hebel
- **MUSS [MUST]** die Konfidenz-Stufe an jedem emittierten Befund festhalten, damit ein nachgelagerter Konsument weiter filtern kann

### Volumen-Kontrolle
- **MUSS [MUST]** die Befund-Anzahl pro Datei im Top-Report auf 3 deckeln; zusätzliche Matches aus derselben Datei werden nur im vollständigen Inventar festgehalten
- **MUSS [MUST]** die Befund-Anzahl pro Lauf im Top-Report auf 15 deckeln; zusätzliche Matches werden als „+ N weitere Kandidaten (siehe `full.json`)" zusammengefasst
- **MUSS [MUST]** Befunde für den Top-Report-Cap priorisieren nach (1) Konfidenz (`high` vor `medium`), dann (2) Heading-Prominenz (höhere Heading-Ebene zuerst), dann (3) Dateipfad (lexikografisch), um die Ordnung über Läufe hinweg deterministisch zu halten
- **MUSS [MUST]** das vollständige, ungedeckelte Befund-Inventar als `full.json` unter `.audits/diagram-opportunity/<YYYY-MM-DD-HHMM>/` persistieren, damit der Cap nie Daten versteckt; der Aufrufer (Skill, Agent oder Betreiberin) ist verantwortlich, die Datei zu platzieren
- **DARF NICHT [MUST NOT]** den Pro-Datei- oder Pro-Lauf-Cap still aufgrund von Konfidenz erhöhen; der Cap ist eine harte Obergrenze und Überlauf wird immer zusammengefasst, nicht durchgereicht
- **DARF NICHT [MUST NOT]** die Caps als Invocation-Zeit-Overrides freilegen; die Defaults (3 pro Datei, 15 pro Lauf) sind die einzig unterstützten Werte, portfolio-weit fixiert, damit die „Betreiberin wird nie überfordert"-Garantie einheitlich gilt. Das `caps`-Objekt in §Ausgabe-Form hält die fixierten Defaults zur Nachvollziehbarkeit fest und ist rein informativ; eine Betreiberin, die die vollständige Menge braucht, liest das ungekappte `full_findings`- / `full.json`-Inventar

### Severity-Bereich
- **MUSS [MUST]** jedem Befund eine Severity aus der geschlossenen Menge `{suggestion, info}` zuweisen: `suggestion` für Matches, auf die der Agent ein Handeln der Betreiberin erwartet, `info` für rein kontextuelle Matches (zum Beispiel eine via `<!-- diagram-opportunity-skip: ... -->` unterdrückte Passage, zur Nachvollziehbarkeit festgehalten)
- **DARF NICHT [MUST NOT]** `warning`- oder `critical`-Severities emittieren; das ist ein Vorschlags-Werkzeug, keine Mängelliste, und eine höhere Severity würde Betreiberinnen-Müdigkeit antrainieren
- **MUSS [MUST]** diese Kleinschreibungs-Namen (`suggestion` / `info`) als die maschinengelesene Editorial-Serialisierung behandeln, sanktioniert durch den Editorial-Sub-Skala-Carve-out in `spec/claude/review-plan/` §Schweregrad-Skala; jeder bildet eins-zu-eins auf die Title-Case-Stufen jener Spec ab

### Quell-Klassifikations-Vorschlag
- **MUSS [MUST]** auf jedem Befund der Severity `suggestion` eine Quell-Klassifikation vorschlagen—entweder `user-described` (mit einer ein-Zeilen-Zusammenfassungs-Kandidatur) oder `derived` (mit einem konkreten Quell-Pfad-Kandidaten innerhalb des Repositorys)—passend zur `<!-- diagram-source: ... -->`-Annotations-Form, die `spec/project/mermaid-diagrams/` §Diagramm-Quellen verlangt
- **SOLLTE [SHOULD]** `derived` gegenüber `user-described` bevorzugen, sobald die Prosa ein konkretes Repository-Artefakt benennt (eine Konfigurationsdatei, einen Workflow, ein Plugin-Manifest, einen Verzeichnisbaum), das als Quelle dienen kann
- **KANN [MAY]** mehrere Quell-Kandidaten auf einem einzelnen Befund vorschlagen, wenn die Prosa mehrere Artefakte referenziert; die Betreiberin wählt zur Apply-Zeit

### Per-Stellen-Mute-Marker
- **MUSS [MUST]** einen Markdown-Kommentar `<!-- diagram-opportunity-skip: <grund> -->`, der auf der Zeile unmittelbar vor einem Heading oder Absatz steht, als Direktive behandeln, Befunde zu unterdrücken, die sonst aus diesem Heading / Absatz und seiner umschlossenen Prosa entstehen würden—bis zum nächsten Heading gleicher oder höherer Ebene
- **MUSS [MUST]** den unterdrückten Match als `info`-Severity-Befund festhalten, der den zitierten Grund referenziert, damit die Unterdrückung im vollständigen Inventar sichtbar bleibt, ohne den Top-Report zu verunreinigen
- **DARF NICHT [MUST NOT]** irgendeine andere Marker-Form (HTML-Attribut, Frontmatter-Schlüssel, In-Prosa-Tag) als Skip-Direktive behandeln; die Kommentar-auf-vorangehender-Zeile-Form ist die einzig unterstützte Form
- **DARF NICHT [MUST NOT]** ein `--quiet`-Flag (oder Äquivalent) anbieten, das `info`-Severity-Unterdrückungs-Befunde weglässt; diese Befunde bleiben stets im vollständigen Inventar erhalten, damit die Unterdrückung nachvollziehbar bleibt, und—weil der Top-Report volumengedeckelt und gemäß §Volumen-Kontrolle nach `suggestion` zuerst priorisiert ist—verursachen sie keine Zeilen-Kosten im Top-Report

### Ausgabe-Form
- **MUSS [MUST]** Befunde als JSON emittieren, mit mindestens den folgenden Feldern pro Befund: `file` (repo-relativer Pfad), `line_start`, `line_end`, `excerpt` (wortgetreuer Prosa-Trigger, ≤ 240 Zeichen), `diagram_type` (einer der Mermaid-§Diagramm-Katalog-Einträge oder das Literal `ambiguous`), `candidates` (Array aus genau zwei Diagrammtyp-Strings, nur vorhanden bei `diagram_type == ambiguous`), `confidence` (`high` oder `medium`), `severity` (`suggestion` oder `info`), `source_classification` (`user-described` oder `derived`; vorhanden bei `suggestion`-Severity-Befunden), `source_candidate` (String oder String-Array; ein-Zeilen-Zusammenfassung für `user-described`, repo-relativer Pfad oder Pfade für `derived`)
- **MUSS [MUST]** das Pro-Befund-Array in ein Top-Level-Objekt einwickeln, das zusätzlich `scope` (die aufgelösten Input-Pfade), `caps` (`per_file`, `per_run` numerische Werte dieses Laufs), `truncated` (Boolean; true wenn der Top-Report-Cap erreicht wurde), `further_candidate_count` (Integer; null wenn nicht abgeschnitten) und `full_findings` (das ungekappte Befund-Array; der Aufrufer persistiert es als `.audits/diagram-opportunity/<YYYY-MM-DD-HHMM>/full.json`, während `findings` als Top-Report gerendert wird) trägt. Beide Arrays MÜSSEN dasselbe Pro-Befund-Objekt-Schema teilen; `findings` ist ein strikter Prefix von `full_findings`, sobald die deterministische Sortier-Reihenfolge aus §Volumen-Kontrolle angewandt ist
- **DARF NICHT [MUST NOT]** freie Prosa, Empfehlungen oder Kommentare im JSON enthalten; die Ausgabe ist ausschließlich ein strukturiertes Befund-Inventar

### Dispatcher-Integration
- **MUSS [MUST]** die JSON-Form stabil genug halten, damit künftige Dispatcher (`lektorat-apply` als Sub-Check, `audience-doc-author` als Pre-Handoff-Hook, `docs-freshness` als `info`-Severity-Befund-Kategorie) sie ohne Re-Architektur konsumieren können; Feld-Ergänzungen bleiben rückwärts-kompatibel
- **DARF NICHT [MUST NOT]** Befunde selbst persistieren; der Aufrufer ist verantwortlich, `full.json` und jede Top-Report-Rendering zu schreiben—genau wie `lektorat-scanner` die Persistierung an `lektorat-apply` delegiert, gemäß `spec/project/lektorat/`

## Akzeptanzkriterien
- [ ] Den Agent ohne Input-Argumente in einem Repository mit konfiguriertem `docs/<lang>/`-Baum aufzurufen scannt jede `*.md`-Datei unter diesem Baum und emittiert ein strukturiertes Befund-JSON
- [ ] Den Agent mit einem expliziten Pfad (eine einzelne README, ein Glob über `project/`, ein Verzeichnis oder eine Pfad-Liste) aufzurufen scannt genau die aufgelöste Menge und ignoriert den Default-Scope
- [ ] Jeder emittierte Befund zitiert einen wortgetreuen Prosa-Auszug (≤ 240 Zeichen) und einen Zeilenbereich, der zur Position des zitierten Auszugs in der Quelldatei passt
- [ ] Jeder emittierte Befund trägt einen `diagram_type`-Wert, der entweder einer von `flowchart` / `C4Component` / `classDiagram` / `sequenceDiagram` / `erDiagram` oder das Literal `ambiguous` ist; weder `gitGraph` noch ein Nicht-Mermaid-Typ erscheinen je
- [ ] Jeder `ambiguous`-Befund trägt ein `candidates`-Array mit genau zwei verschiedenen Katalog-Einträgen
- [ ] Kein emittierter Befund trägt `confidence: low`; `low`-Konfidenz-Matches fehlen sowohl im Top-Report als auch im vollständigen Inventar
- [ ] Kein emittierter Befund trägt die Severity `warning` oder `critical`; nur `suggestion` und `info` erscheinen
- [ ] In einer synthetischen Testdatei mit 10 verschiedenen `high`-Konfidenz-Matches enthält das Top-Level-`findings`-Array genau 3 Einträge für diese Datei (Pro-Datei-Cap), und die verbleibenden 7 erscheinen nur im Top-Level-`full_findings`-Array
- [ ] In einem synthetischen Lauf mit 30 verschiedenen `high`-Konfidenz-Matches über viele Dateien enthält das Top-Level-`findings`-Array genau 15 Einträge (Pro-Lauf-Cap), `truncated: true`, `further_candidate_count: 15` und das Top-Level-`full_findings`-Array enthält alle 30 Einträge; der Aufrufer persistiert `full_findings` als `.audits/diagram-opportunity/<YYYY-MM-DD-HHMM>/full.json`
- [ ] Die Top-Report-Ordnung ist über zwei Läufe gegen dieselbe Eingabe deterministisch: identische Befunde in identischer Reihenfolge
- [ ] Eine Passage, der unmittelbar `<!-- diagram-opportunity-skip: <grund> -->` vorausgeht, erzeugt keinen `suggestion`-Severity-Befund aus dieser Passage; die Unterdrückung wird als `info`-Severity-Befund festgehalten, der den zitierten Grund referenziert
- [ ] Die `source_classification` jedes emittierten `suggestion`-Severity-Befunds ist entweder `user-described` (mit einem nicht-leeren Zusammenfassungs-String) oder `derived` (mit mindestens einem repo-relativen Pfad, der im Working Tree existiert)
- [ ] Der Agent schreibt nie in eine Datei innerhalb des Repositorys, auch nicht unter `.audits/`; Persistierung ist Aufgabe des Aufrufers
- [ ] Die Tools-Liste des Agents ist das Minimum, das für read-only-Scannen nötig ist: `Read`, `Grep`, `Glob`, `Bash`; kein `Edit`, kein `Write`

## Offene Fragen
_Derzeit keine._
