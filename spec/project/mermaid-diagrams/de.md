# Mermaid-Diagramme in der MkDocs-Dokumentation

Status: draft

## Kontext
MkDocs Material ist der dokumentierte Default für Projektdokumentation in diesem Portfolio (siehe `spec/project/project-structure/`). Sobald eine Doku-Seite nicht-triviale Beziehungen vermitteln muss — der Dependency-Graph zwischen Skills und Agents eines Claude-Code-Plugins, die Portfolio-Karte der Repositories, die `nolte/gh-plumbing` konsumieren, die Laufzeit-Sequenz eines Multi-Skill-Workflows oder das Schema einer Konfigurationsdatei — reicht reine Prosa nicht aus, und Binärbilder (PNG/SVG-Screenshots aus externen Editoren) driften still vom Code, den sie beschreiben.

Mermaid rendert text-beschriebene Diagramme inline in MkDocs Material über die Markdown-Erweiterung `pymdownx.superfences` und die in Material eingebaute Mermaid-Brücke. Damit bleibt jedes Diagramm versionskontrolliert, in Pull-Requests diff-bar und aus textuellen Änderungen re-renderbar. Diese Spec macht Mermaid zum kanonischen Diagramm-Werkzeug für Portfolio-Dokumentation, fixiert je Anwendungsfall den unterstützten Diagrammtyp, listet die MkDocs-seitigen Abhängigkeiten, die ein Repository deklarieren muss, um Diagramme zu rendern, und definiert, wie Diagramme mit den Strukturen synchron bleiben, die sie visualisieren.

Leser: Doku-Autoren, die ein Mermaid-Diagramm hinzufügen, die Autoren des `mermaid-diagrams-apply`-Skills und des `mermaid-diagram-reviewer`, die es operationalisieren und prüfen, sowie Reviewer, die kontrollieren, dass ein Diagramm synchron mit der visualisierten Struktur bleibt.

## Ziele
- Jedes Diagramm in der Portfolio-Dokumentation ist text-basiert (Mermaid), inline im Markdown, versionskontrolliert und in Pull-Request-Diffs reviewbar
- Die Dokumentation kann Strukturen visualisieren, die bereits im Repository existieren — Claude-Plugin-Manifeste, Projekt-Abhängigkeiten, Spec-Querverweise, Branching-Model-Fluss, Konfigurations-Schemata — ohne handgezeichnete Binärbilder
- Die Auswahl des Diagrammtyps ist deterministisch: dieselbe Struktur erzeugt denselben Mermaid-Diagrammtyp über alle Repositories hinweg
- Das MkDocs-Setup für Mermaid ist portfolio-weit einheitlich, sodass jede:r Mitwirkende dieselbe Konfiguration in `mkdocs.yml` und `docs/requirements.txt` vorfindet
- Diagramme bleiben re-derivierbar: handgeschriebene Diagramme halten ihre Quellbeschreibung neben dem Block fest; abgeleitete Diagramme nennen das Quell-Artefakt, damit das nächste Update weiß, was neu zu lesen ist
- Light- und Dark-Mode rendern korrekt ohne pro-Diagramm-Farb-Overrides

## Nicht-Ziele
- Methodik für beliebige Diagramm-Werkzeuge (PlantUML, Graphviz, draw.io); diese werden in dieser Spec nicht unterstützt
- Domain-Modellierung oder formale UML-/BPMN-Compliance
- Prosa zu ersetzen; Diagramme ergänzen geschriebene Erklärung, sie ersetzen sie nicht
- Stil-Customization über das hinaus, was die Mermaid-Integration von MkDocs Material bietet; pro-Diagramm-Farb-Overrides sind außerhalb des Scopes
- Diagramm-Generierung aus Code zur Build-Zeit (zum Beispiel Parsen von `pyproject.toml` während `mkdocs build`); Diagramme werden als Mermaid im Markdown geschrieben und manuell oder über einen Claude-Skill aktualisiert, nicht von der Doku-Pipeline synthetisiert
- Vor-Rendering von Mermaid-Diagrammen zu statischem SVG oder PNG unter `docs/assets/` (oder einem anderen Verzeichnis) für Offline-Vorschau oder First-Paint-Geschwindigkeit; das Rendering bleibt strikt clientseitig über Materials Runtime-Brücke, damit die Mermaid-Quelle im Markdown der einzige Wahrheits-Punkt bleibt und nie gegen ein gecachtes Bild driftet

## Anforderungen

### MkDocs-Setup
- **MUSS [MUST]** in `mkdocs.yml` unter `markdown_extensions` `pymdownx.superfences` mit einem Custom-Fence für Mermaid konfigurieren:

  ```yaml
  markdown_extensions:
    - pymdownx.superfences:
        custom_fences:
          - name: mermaid
            class: mermaid
            format: !!python/name:pymdownx.superfences.fence_code_format
  ```

- **MUSS [MUST]** `pymdown-extensions` in `docs/requirements.txt` (oder dem äquivalenten Doku-Installationsset) mit einem expliziten Versions-Spezifizierer gemäß `spec/project/project-structure/` „Format der Requirements-Dateien" listen
- **MUSS [MUST]** `mkdocs-material` als konfiguriertes Theme behalten; das Mermaid-Rendering basiert auf der in Material eingebauten JavaScript-Brücke, die die Mermaid-Runtime bei Bedarf nachlädt
- **MUSS NICHT [MUST NOT]** ein separates Mermaid-MkDocs-Plugin (zum Beispiel `mkdocs-mermaid2-plugin`) ergänzen; Materials native superfences-basierte Integration ist Portfolio-Standard, ein zweites Plugin verdoppelt nur die Runtime
- **MUSS [MUST]** etwaige Mermaid-Theme-Variablen der Marke über genau eine globale Konfiguration injizieren, die die Mermaid-Theme-Konfiguration einmal für die ganze Site setzt — einen einzelnen MkDocs-Hook oder einen einzelnen `extra_javascript`-Eintrag in `mkdocs.yml` —, niemals über eine pro-Diagramm-`%%{init: {'theme': …, 'themeVariables': …}}%%`-Direktive innerhalb einzelner Mermaid-Blöcke; dies ist der kanonische Verdrahtungs-Pfad, auf den `spec/design/corporate-design-colors/` §Anwendung pro Artefakt für die konkrete Regel verweist, und er hält die Light-/Dark-Theme-Brücke, die die Theme-Variablen pro Modus tauscht, an einer Stelle
- **SOLLTE [SHOULD]** sich für das Mermaid-Rendering auf Materials automatische Light-/Dark-Theme-Brücke verlassen, statt Mermaid-Farben pro Diagramm zu überschreiben
- **SOLLTE [SHOULD]** das Rendering durch `task docs` (welches `mkdocs build --strict` aufruft) verifizieren, bevor eine Änderung gemerged wird, die einen Mermaid-Block einführt oder ändert

### Diagramm-Katalog
Die folgenden Mermaid-Diagrammtypen sind der unterstützte Werkzeugkasten für die Portfolio-Dokumentation. Jeder Eintrag bindet einen Diagrammtyp an die Art von Struktur, die er visualisiert; eine Abweichung von diesem Mapping erfordert eine explizite Begründung auf der Doku-Seite, die das Diagramm beherbergt.

- **`flowchart`** — Dependency-Graphen, Plugin-/Modul-Komposition, Entscheidungsbäume, gerichteter Kontrollfluss. Default für „X hängt von Y ab" und „X speist Y". Default-Direction `LR` für Dependency-/Pipeline-Diagramme, `TB` für Architektur-Übersichten
- **`C4Component`** — komponenten-orientierte Architektur-Sichten: welche Services/Module existieren, wer ruft wen, wo die Grenze zu externen Systemen liegt. Default für Portfolio-Karten und „wie sieht dieses Repo auf einen Blick aus"
- **`classDiagram`** — Typ-Hierarchien, Plugin- und Skill-Schemata, Manifest-Strukturen. Default beim Visualisieren von Objektstruktur mit Attributen und Methoden
- **`sequenceDiagram`** — Laufzeit-Workflows über Akteure: eine Multi-Skill-Orchestrierung, ein CI-Pipeline-Lauf, ein End-to-End-Anwendungsfall vom User-Trigger bis zum Abschluss
- **`erDiagram`** — Datenstrukturen mit Kardinalität: Konfigurationsdatei-Schemata (zum Beispiel `.github/settings.yml`), Datenbanktabellen, Message-Verträge

`gitGraph` ist bewusst **nicht** Teil dieses Katalogs: das Rendering unter MkDocs Material ist unzuverlässig (Theme-Bridge-Lücken, Layout-Kollisionen bei nicht-trivialen Branch-Strukturen). Branching- und Release-Flüsse werden stattdessen mit `flowchart LR` illustriert — siehe den Eintrag **Branching-Modell** unter §Anerkannte Ableitungs-Quellen.

### Diagramm-Quellen
Jedes Mermaid-Diagramm stammt aus einer von zwei Origins, und diese Origin wird neben dem Diagramm festgehalten, damit zukünftige Updates wissen, was neu zu lesen ist.

- **MUSS [MUST]** die Quelle jedes Mermaid-Blocks per HTML-Kommentar unmittelbar oberhalb des Fences markieren, in einer dieser Formen:
  - `<!-- diagram-source: user-described — <ein-Zeilen-Zusammenfassung der Struktur> -->` für handgeschriebene Diagramme aus einer User-Beschreibung
  - `<!-- diagram-source: derived — <Pfad oder Identifier der Quellstruktur> -->` für Diagramme, die aus einem existierenden Artefakt abgeleitet sind (zum Beispiel `derived — .claude-plugin/plugin.json` oder `derived — spec/project/branching-model/en.md`)
- **MUSS [MUST]** ein abgeleitetes Diagramm neu zeichnen, wenn sich seine Quellstruktur ändert; eine Divergenz zwischen Quelle und Diagramm gilt als Doku-Drift
- **SOLLTE [SHOULD]** Ableitung gegenüber Handarbeit bevorzugen, sobald die Quellstruktur existiert und stabil genug zum Lesen ist; Handarbeit ist konzeptionellen Übersichten vorbehalten, für die noch keine maschinenlesbare Quelle existiert
- **KANN [MAY]** mehrere Quellen in einem Diagramm kombinieren (zum Beispiel ein `flowchart`, das das Plugin-Manifest plus seinen Skill-Ordner zeigt); jede Quelle wird im Kommentar gelistet

### Anerkannte Ableitungs-Quellen
Die folgenden Strukturen in einem Portfolio-Repository sind die typischen Inputs für abgeleitete Diagramme. Skills, die Diagramm-Generierung automatisieren, MÜSSEN ihre Quelldaten aus diesen Locations beziehen.

- **Claude-Code-Plugin** — `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, die Bäume `skills/<name>/` und `agents/<name>.md` → `flowchart` der Plugin-Inhalte oder `C4Component` des Plugins eingebettet im konsumierenden Repository
- **Python-Projekt** — `pyproject.toml`, `requirements.txt`, `requirements-dev.txt` → `flowchart` der Abhängigkeiten (direkt vs. dev), `classDiagram` für Modul-Hierarchien aus dem Source-Tree
- **Node-Projekt** — `package.json` (`dependencies`, `devDependencies`) → analoges `flowchart`
- **GitHub-Actions-Workflows** — `.github/workflows/*.yml` plus die `_extends`/`uses`-Kette nach `nolte/gh-plumbing` → `flowchart`, welcher Workflow welchen wiederverwendbaren Workflow an welchem Versions-Pin aufruft
- **Spec-Querverweise** — Markdown-Links zwischen Specs unter `spec/<topic>/<slug>/<lang>.md` → `flowchart` von „Spec X referenziert Spec Y"-Beziehungen
- **Branching-Modell** — die Regeln in `spec/project/branching-model/` → `flowchart LR` mit `subgraph`-Clustern für `develop`, `main` und Release-Branches, plus beschriftete Edges für den Merge- und Automerge-Fluss; `gitGraph` wird bewusst nicht verwendet (siehe die Katalog-Notiz oben)
- **Portfolio-Karte** — die Menge der Repositories unter der GitHub-Organisation `nolte`, die das `nolte-shared`-Plugin oder die wiederverwendbaren Workflows aus `gh-plumbing` konsumieren. **Default:** jedes konsumierende Repository rendert ein fokussiertes `C4Component`, das ausschließlich seinen eigenen Konsum zeigt (welche wiederverwendbaren Workflows oder Skills es importiert, an welchen Versions-Pins). **Konsolidierte Portfolio-Sicht:** nur `nolte-shared` und `gh-plumbing` selbst rendern ein aggregiertes `C4Component`, dessen `subgraph`-Cluster die Konsumenten gruppieren, sodass die portfolio-weite Form an einer kanonischen Stelle lesbar bleibt, ohne dass jedes Konsumenten-Repo den ganzen Graphen mittragen muss

### Authoring-Regeln
- **MUSS [MUST]** jedes Mermaid-Diagramm inline in einer Markdown-Datei unter `docs/<lang>/` platzieren, niemals in einer separaten `.mmd`-Quelldatei außerhalb des Doku-Baums
- **MUSS [MUST]** jedem Diagramm ein Heading (Level 3 oder tiefer) oder eine fettgedruckte Caption voranstellen, das/die benennt, was das Diagramm zeigt, plus einen ein-Satz-Prosa-Lead-In, der die Frage formuliert, die das Diagramm beantwortet
- **MUSS [MUST]** für alle Node-Labels, Edge-Labels und Identifier innerhalb des Mermaid-Blocks Englisch verwenden, auch in `docs/de/` oder einem anderen nicht-englischen Doku-Baum; nur die umgebende Prosa wird übersetzt
- **MUSS [MUST]** in jedem `flowchart` eine explizite Direction (`flowchart TB`, `flowchart LR`, `flowchart TD`) in der ersten Zeile deklarieren; Default `LR` für Dependency-/Pipeline-Diagramme und `TB` für Architektur-Übersichten
- **MUSS NICHT [MUST NOT]** Inline-Styling pro Node oder Edge anwenden (`style`, `linkStyle` oder `classDef` mit hartkodierten Farben); sich auf Materials Mermaid-Theme-Brücke verlassen, damit Light- und Dark-Mode-Rendering korrekt bleibt
- **SOLLTE [SHOULD]** jeden Mermaid-Block unter etwa 25 Nodes halten; in mehrere Diagramme aufteilen oder Sub-Flowcharts verwenden, sobald die Größe darüber hinaus wächst
- **SOLLTE [SHOULD]** verwandte Nodes über Mermaid-`subgraph`-Blöcke gruppieren, benannt nach dem konzeptionellen Cluster (zum Beispiel `subgraph plugin["nolte-shared plugin"]`)
- **KANN [MAY]** eine Click-Annotation (`click NodeId href "..."`) ergänzen, damit ein Node auf die zugrunde liegende Spec, den Skill-Ordner oder eine externe Seite verlinkt

### Übersetzungs-Handling
- Mermaid-Block-Inhalt ist Technical-Identifier-Territorium und bleibt in einer kanonischen Sprache (Englisch), unabhängig davon, in welchem `docs/<lang>/`-Baum die Datei liegt
- Umgebende Prosa, Captions und Lead-Ins werden pro Sprache zusammen mit dem Rest der Dokumentation übersetzt
- Skills, die Dokumentation übersetzen, MÜSSEN Mermaid-Fences als nicht-übersetzbare Code-Blöcke behandeln

### Drift-Verhalten
- **MUSS [MUST]** ein abgeleitetes Diagramm im selben Pull-Request aktualisieren, der seine genannte Quellstruktur ändert; ein unverändertes Diagramm neben einer veränderten Quelle ist ein Drift-Befund
- **MUSS [MUST]** die ein-Zeilen-Zusammenfassung in einem `user-described`-`diagram-source`-Kommentar aktuell halten; ändert sich der konzeptionelle Inhalt des Diagramms, ändert sich die Zusammenfassung mit
- **MUSS [MUST]** ungelöste Drift abgeleiteter Diagramme über das `docs-freshness`-Audit sichtbar machen (siehe `spec/project/docs-freshness/`); das Freshness-Audit behandelt einen Mermaid-Block, dessen genannte `derived`-Quelle einen jüngeren Last-Commit-Zeitstempel hat als die Markdown-Datei, die den Block enthält, als Drift-Befund

## Akzeptanzkriterien
- [ ] `mkdocs.yml` deklariert `pymdownx.superfences` unter `markdown_extensions` mit einem `mermaid`-Custom-Fence über `pymdownx.superfences.fence_code_format`
- [ ] `docs/requirements.txt` listet `pymdown-extensions` mit einem expliziten Versions-Spezifizierer
- [ ] `mkdocs.yml` behält `theme.name: material` und ergänzt `mkdocs-mermaid2-plugin` (oder ein anderes Mermaid-only-Plugin) nicht in seiner `plugins:`-Liste
- [ ] Jedem Mermaid-Block in `docs/<lang>/` geht ein HTML-`diagram-source`-Kommentar voraus, der entweder `user-described` oder `derived` plus einen Quell-Verweis nennt
- [ ] Jeder `flowchart`-Block deklariert in seiner ersten Zeile eine explizite Direction (`TB`, `LR` oder `TD`)
- [ ] Kein Mermaid-Block im Doku-Baum enthält eine `style`-, `linkStyle`- oder `classDef`-Direktive mit einer hartkodierten Farbe
- [ ] Jeder Mermaid-Block sitzt unter einem Heading oder einer fetten Caption mit einem ein-Satz-Prosa-Lead-In
- [ ] Alle Node-Labels, Edge-Labels und Identifier innerhalb von Mermaid-Fences sind Englisch, unabhängig vom umgebenden `docs/<lang>/`-Baum
- [ ] Jeder in der Doku verwendete Mermaid-Diagrammtyp passt zum Anwendungsfall im **Diagramm-Katalog**, oder die Seite, die das Diagramm beherbergt, hält eine explizite Begründung für die Abweichung fest
- [ ] `task docs` (oder `mkdocs build --strict`) rendert die Doku ohne ungelöste Mermaid-Syntax-Fehler
- [ ] Wenn sich das genannte Quell-Artefakt eines abgeleiteten Diagramms ändert, wird das Diagramm im selben Pull-Request aktualisiert oder die Divergenz als Follow-up dokumentiert
- [ ] Das `docs-freshness`-Audit des Repositories erkennt Mermaid-Diagramm-Quell-Drift als Drift-Kategorie und meldet jeden mit `derived` markierten Mermaid-Block, dessen Quelle sich seit der beherbergenden Markdown-Datei geändert hat

## Offene Fragen
- Keine zum jetzigen Zeitpunkt; die fünf Drafting-Fragen wurden am 2026-05-08 entschieden — Q1 (docs-freshness-Drift): ja, auf `MUSS` gehärtet und in `spec/project/docs-freshness/` gespiegelt; Q2 (`gitGraph`): aus dem Katalog entfernt zugunsten von `flowchart LR`; Q3 (25-Node-Cap): bleibt `SOLLTE`, bis ein zählender Lint existiert; Q4 (Portfolio-Split): Split-per-Konsument ist der Default, mit konsolidierter Sicht nur in `nolte-shared` / `gh-plumbing`; Q5 (SVG-Caching): nein, als Nicht-Ziel verankert
