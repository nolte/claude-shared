# MkDocs-Site-Struktur

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Nutzerbedarf, welche Einschränkung treibt sie? -->

Jedes Portfolio-Repository, das Dokumentation ausliefert, tut das über MkDocs, und `spec/project/project-structure/` schreibt bereits vor, dass `docs/` und `mkdocs.yml` existieren müssen. Was diese Spec bewusst **nicht** definiert, ist die *Gestalt* der Site: welche Top-Level-Sektionen erscheinen, in welcher Reihenfolge, in welchen Sprach-Trees, mit welchen Plugins, mit welchen Per-Page-Metadaten. `spec/project/docs-freshness/` sagt explizit: „die On-Disk-Form von MkDocs (i18n-Plugin-Auswahl, Theme, Nav-Struktur) — das sind Per-Repository-Entscheidungen" — was genau die Lücke ist, die Konsumenten spüren: Leser, die zwei nolte-Repos parallel benutzen, müssen die Navigation neu lernen, der docs-freshness-Audit kann Erwartungen nicht über Repos hinweg normalisieren, und projekt-typ-spezifisches Verhalten (der Skills-/Agents-Katalog in `nolte-shared`, künftige Cookiecutter-Template-Dokumentation, künftige Library-API-Referenzen) erfindet die MkDocs-Verdrahtung jedes Mal neu.

Diese Spec schließt diese Lücke. Sie definiert (a) das portfolio-weite MkDocs-Skelett — Site-Layout, Plugin-Basis, Navigations-Kontrakt, Per-Page-Struktur, Sprachen-Parität — und (b) zwei explizite **Erweiterungs-Hooks**, über die projekt-typ-spezifische Specs (`skill-agent-catalog`, künftige `cookiecutter-template-docs`, künftige `library-api-docs`, …) zusätzliche Sektionen und Plugins andocken, ohne das Skelett zu forken oder es stillschweigend zu übersteuern. Das Skelett wird erzwungen; die Erweiterungen sind deklarativ und nachprüfbar.

## Ziele
<!-- Was diese Spec erreichen soll. Stichpunkte, ergebnisorientiert. -->
- Jedes Portfolio-Repository mit MkDocs exponiert dieselbe Top-Level-Navigation, sodass ein Leser, der ein Repo gelernt hat, das nächste sofort navigieren kann
- Mehrsprachige Layouts (`docs/<lang>/`) folgen einem einzigen i18n-Mechanismus mit Dateinamen-Parität über jede konfigurierte Sprache
- Die Plugin-Basis ist aufgezählt und gepinnt, sodass die Dokumentation eines Repositorys lokal, in CI und in der veröffentlichten Site gleich gebaut wird
- Per-Page-Struktur (`H1`, Frontmatter, Audience-Tagging) ist vorhersehbar genug, sodass nachgelagertes Tooling (`docs-freshness`, `prose-vale-curator`, künftige Katalog-Generatoren) sich darauf verlassen kann
- Projekt-typ-spezifische Specs erweitern das Skelett über deklarierte Hooks statt es zu forken; jede Erweiterung benennt, was sie hinzufügt, was sie relaxiert, und warum
- Die On-Disk-Form ist verifizierbar: `mkdocs build --strict` ist das Rendering-Gate, und ein Audit (`docs-freshness`) behandelt die Spec als normative Quelle für die erwartete Nav und Parität

## Nicht-Ziele
<!-- Explizit außerhalb des Geltungsbereichs. Verhindert Wildwuchs. -->
- Theme-Palette, Typographie oder visuelle Identität — bleiben Per-Repo-Entscheidungen (die Spec schreibt `mkdocs-material` als Theme-Engine vor, nicht ein Farbschema)
- Der Markdown-*Inhalt* einer Seite — die Spec regelt den Container, nicht die Prosa
- Vale-Prosa-Linting — gehört zu `spec/project/prose-style/`
- Dokumentations-Build- und Deploy-Verdrahtung — gehört zu `spec/project/project-structure/` (die `docs/`- und `mkdocs.yml`-MUSSes) und dem `release-cd-deliver-docs`-Workflow
- Katalog-Generatoren selbst (zum Beispiel `skill-agent-catalog`) — das sind projekt-typ-spezifische Erweiterungs-Specs, die sich über die hier definierten Hooks andocken, aber ihre Generator-Logik lebt in der Erweiterungs-Spec
- Methodik der Audience-Identifizierung — gehört zu `spec/project/audience-identification/`; diese Spec verlangt nur, dass das *Ergebnis* (das Audience-Artefakt) aus dem Page-Frontmatter referenziert wird
- ADR-Formatierung und -Lebenszyklus — die Spec reserviert nur einen ADR-Nav-Slot; die ADR-Form gehört in eine eigene Spec, falls sie groß genug wird, um eine zu rechtfertigen

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUSS [MUST], SOLLTE [SHOULD], KANN [MAY]. Ein atomarer Anspruch pro Punkt. -->

### Site-Layout

- **MUSS [MUST]** `docs_dir` auf `docs` belassen (der MkDocs-Default), damit konsumierendes Tooling — `docs-freshness`, IDE-Link-Checker, `mkdocs-static-i18n` — sich auf einen einzigen Pfad verlassen kann
- **MUSS [MUST]** Dokumentation in pro-sprachige Unterverzeichnisse `docs/<lang>/` gliedern, eines pro in `spec/.spec-config.yml` `languages` gelistete Sprache; ein Repo mit nur einer Sprache nutzt trotzdem `docs/<lang>/` (nicht ein flaches `docs/`), damit das Hinzufügen einer zweiten Sprache später eine rein additive Änderung ist
- **MUSS [MUST]** den On-Disk-Dateibaum strukturell identisch über die konfigurierten Sprach-Trees halten: jede Seite, die in einer Sprache existiert, existiert in jeder anderen konfigurierten Sprache (geprüft vom `docs-freshness`-Paritäts-Audit)
- **DARF NICHT [MUST NOT]** Top-Level-Seiten direkt unter `docs/` platzieren (außer dem `index.md`-Fallback des i18n-Plugins, falls die konfigurierte i18n-Strategie eines verlangt); jede Seite gehört zu einem Sprach-Tree
- **SOLLTE [SHOULD]** Sektions-Ordner (`docs/<lang>/<section>/`) flach halten — höchstens eine weitere Verschachtelungsebene (`docs/<lang>/<section>/<sub>/`) — damit Navigations-Pfade vorhersehbar bleiben

### Top-Level-Navigation

- **MUSS [MUST]** diese Top-Level-Sektionen in dieser Reihenfolge exponieren, sofern die entsprechenden Inhalte existieren:
  1. **Home** (`index.md`) — Landing-Page; ein Absatz plus Sprung-Links
  2. **Getting Started** — einsteigerorientierter narrativer Pfad von Install/Clone zum ersten erfolgreichen Lauf
  3. **Guides** — aufgabenorientierte How-tos
  4. **References** — Format-/API-/Konventions-Referenzen
  5. **ADRs** — Architecture Decision Records, sofern das Repository welche pflegt
  6. **Project** — Orientierungs-Oberfläche für den `project/`-Planungs-Tree (Mission, Roadmap, Sprints, Audience-Artefakte), sofern `project/` existiert
  7. *Erweiterungs-Sektionen — siehe „Erweiterungs-Hooks" unten*
- **DARF NICHT [MUST NOT]** zusätzliche Top-Level-Sektionen ohne projekt-typ-spezifisches Spec-Opt-in hinzufügen; Per-Page-Ergänzungen bleiben innerhalb der sieben oben genannten Sektionen
- **MUSS [MUST]** Sektions-Labels über `mkdocs-static-i18n`'s `nav_translations` übersetzen, damit ein einziges mkdocs.yml die Nav jeder Sprache treibt
- **SOLLTE [SHOULD]** eine leere Sektion weglassen statt sie als Platzhalter zu shippen; eine leere Sektion ist eine Leserfalle

### Plugin-Basis

- **MUSS [MUST]** `mkdocs-material` als Theme-Engine deklarieren (`theme: name: material`); das Theme ist die Portfolio-Konvention, die Palette ist eine Per-Repo-Entscheidung
- **MUSS [MUST]** `mkdocs-static-i18n` als i18n-Plugin mit `docs_structure: folder` deklarieren, damit die pro-sprachigen Unterverzeichnisse unter `docs/<lang>/` die Quelle der Wahrheit sind
- **MUSS [MUST]** `pymdownx.superfences` in `markdown_extensions` deklarieren (die Mermaid-Integration, die `spec/project/mermaid-diagrams/` regelt, verlangt es; die Deklaration hier macht die Abhängigkeit explizit, auch wenn noch kein Mermaid-Diagramm ausgeliefert wird)
- **MUSS [MUST]** das eingebaute `search`-Plugin aktiv halten (explizit in der `plugins:`-Liste deklarieren, damit eine Erweiterungs-Spec, die `plugins:` neu deklariert, es nicht versehentlich entfernt)
- **MUSS [MUST]** jedes Plugin (einschließlich `mkdocs`, `mkdocs-material` und `pymdown-extensions`) im Python-Dependency-Manifest des Projekts (`pyproject.toml`, `requirements*.txt`, `uv.lock`, …) pinnen; keine floatenden Versionen
- **SOLLTE [SHOULD]** die Plugin-Liste kurz halten — zusätzliche Plugins werden über den **Plugin-Erweiterungs-Hook** unten eingeführt, nicht über Ad-hoc-Ergänzungen in `mkdocs.yml`
- **KANN [MAY]** `mkdocs-mermaid2-plugin` nur hinzufügen, wenn die Bedingungen in `spec/project/mermaid-diagrams/` das erlauben (der kanonische Mermaid-Stack hier ist `pymdownx.superfences`)

### Per-Page-Struktur

- **MUSS [MUST]** jede Seite (nach etwaigem Frontmatter) mit einer einzigen `# H1` beginnen, die dem Nav-Label der Seite entspricht
- **MUSS [MUST]** YAML-Frontmatter am Anfang jeder Seite deklarieren mit mindestens:
  - `title`: der menschenlesbare Seitentitel (entspricht der H1)
  - `audience`: eine oder mehrere Audience-IDs aus dem Audience-Artefakt des Projekts (`AUDIENCES.md` oder die per `spec/project/audience-identification/` dokumentierte alternative Lage)
  - `last_updated`: ISO-8601-Datum der letzten Inhaltsrevision oder das Literal `generated` für Seiten, die ein Katalog-Generator emittiert hat
- **SOLLTE [SHOULD]** eine `## Sources`-Sektion als letzte Sektion der Seite einbauen, die auf die autoritative Quelle (`spec/<path>`, `src/<path>`, einen ADR, eine externe URL) zurückverweist, sofern die Seite aus einer einzigen Quelle der Wahrheit abgeleitet ist
- **KANN [MAY]** zusätzliche Frontmatter-Schlüssel deklarieren: `tags` für Cross-Page-Lookups, `status` für explizite `draft`/`stable`/`deprecated`-Markierung, `summary` für eine einzeilige Kurzfassung, die in Sektions-Indexseiten verwendet wird
- **DARF NICHT [MUST NOT]** Frontmatter-Schlüssel mit portfolio-weiter Bedeutung erfinden, ohne sie über eine Spec-Änderung vorzuschlagen

### Audience-Targeting

- **MUSS [MUST]** jede Top-Level-Nav-Sektion auf eine oder mehrere im Audience-Artefakt des Projekts deklarierte Audiences abbilden; die Abbildung wird im Frontmatter der Sektions-Indexseite und in der Sektions-Beschreibung auf der Home-Seite festgehalten
- **MUSS [MUST]** den `audience`-Frontmatter-Wert jeder Seite auf IDs beschränken, die im Audience-Artefakt des Projekts deklariert sind; eine unbekannte Audience-ID ist ein `docs-freshness`-Befund
- **SOLLTE [SHOULD]** die portfolio-weite Audience-Basis (`user`, `contributor`, `operator`, `release-manager`) im Audience-Artefakt des Projekts abdecken, zusätzlich zu eventuellen projekt-spezifischen Audiences; ein Projekt, das eine dieser Basis-Audiences echt nicht bedient (eine Library ohne Release-Workflow bedient keinen `release-manager`, ein internes Tool ohne Contributor-Surface keinen `contributor`), notiert die Auslassung explizit im Artefakt, damit ein Reviewer eine bewusste Auslassung von einem Versehen unterscheiden kann
- **SOLLTE [SHOULD]** Nav-Sektionen nach primärer Audience gruppieren, wenn das Projekt drei oder mehr Audiences bedient; bei zwei oder weniger Audiences ist eine flache Reihenfolge klarer
- **KANN [MAY]** das `audience`-Frontmatter als zukünftigen Filter-Input nutzen (audience-spezifisches Inhaltsverzeichnis, audience-gefilterte Suche); diese Spec verlangt nur, dass der Wert vorhanden und gültig ist

### Erweiterungs-Hooks

Zwei deklarierte Erweiterungspunkte erlauben es projekt-typ-spezifischen Specs, dem Skelett etwas hinzuzufügen, ohne es zu forken.

- **Sektions-Erweiterung**: eine projekt-typ-spezifische Spec **KANN [MAY]** eine oder mehrere Top-Level-Nav-Sektionen hinzufügen.
  - Die Erweiterungs-Spec **MUSS [MUST]** jede hinzugefügte Sektion benennen, ihre Einfüge-Position relativ zu den sieben Standard-Sektionen, ihre primäre Audience, und die Per-Page-Frontmatter-Form (falls vorhanden), die sie über die Basis hinaus verlangt
  - Die Erweiterungs-Spec **MUSS [MUST]** angeben, ob die Sektion einsprachig ist (typisch wenn der Inhalt aus EN-kanonischen Artefakten stammt, deren Übersetzung nicht sinnvoll ist) oder der Standard-Sprachen-Paritäts-Regel folgt
  - Die Erweiterungs-Spec **DARF NICHT [MUST NOT]** eine Standard-Sektion stillschweigend umbenennen, umsortieren oder verstecken; das ist eine Spec-Änderung, keine Erweiterung
  - Beispiele: `spec/claude/skill-agent-catalog/` fügt **Skills**- und **Agents**-Sektionen nach **References** hinzu; eine künftige `cookiecutter-template-docs`-Spec könnte **Template variables**, **Hooks**, **Quickstart** hinzufügen; eine künftige `library-api-docs`-Spec könnte **API Reference** hinzufügen
- **Plugin-Erweiterung**: eine projekt-typ-spezifische Spec **KANN [MAY]** zusätzliche MkDocs-Plugins fordern.
  - Die Erweiterungs-Spec **MUSS [MUST]** jedes benötigte Plugin benennen, seinen Pin (oder eine Constraint, die im Dep-Manager zu einem Pin aufgelöst wird), die Rationale (warum die Basis es nicht bereits enthält) und etwaige `mkdocs.yml`-Einstellungen
  - Die Erweiterungs-Spec **MUSS [MUST]** erklären, wie das Plugin mit den Basis-Plugins interagiert, insbesondere mit `mkdocs-static-i18n` (das laut den Open Questions von `spec/claude/skill-agent-catalog/` bekannte Wechselwirkungen mit `mkdocs-gen-files` hat)
  - Die Erweiterungs-Spec **DARF NICHT [MUST NOT]** ein Basis-Plugin stillschweigend deaktivieren; ein Basis-MUSS explizit zu relaxieren erfordert eine begründete Aussage in der Erweiterungs-Spec
  - Beispiele: `spec/claude/skill-agent-catalog/` verlangt `mkdocs-gen-files` und `mkdocs-literate-nav`; eine künftige `cookiecutter-template-docs` könnte `mkdocs-include-markdown` verlangen
- **Projekt-Typ-Erkennung**: ein Repository signalisiert, welche Erweiterungen aktiv sind, durch die Anwesenheit der entsprechenden Marker-Datei (`.claude-plugin/plugin.json` → claude-plugin; `cookiecutter.json` + `{{cookiecutter.project_slug}}/` → cookiecutter-template; künftige Per-Typ-Marker nach Bedarf); die passende Erweiterungs-Spec gilt für Repositories, die den Marker tragen
- **MUSS [MUST]** die MUSSes jeder aktiven Erweiterung als additiv zu den Basis-MUSSes behandeln; eine Erweiterung relaxiert die Basis nur, wenn sie es ausdrücklich mit Rationale sagt
- **DARF NICHT [MUST NOT]** mehr als fünf Erweiterungs-Sektionen insgesamt pro Repository tragen, summiert über jede aktive Erweiterungs-Spec; das Cap zwingt Erweiterungs-Specs dazu, Sektionen zu konsolidieren statt neue zu erfinden, sobald ein Projekt die Schwelle erreicht (ein hypothetisches Repo, das drei Erweiterungs-Specs mit je zwei Sektionen aktiviert, müsste entweder Sektionen zusammenfassen oder per Spec-Änderung begründen, warum das Cap wachsen sollte)

### i18n und Parität

- **MUSS [MUST]** `docs/<lang>/`-Trees strukturell identisch halten: jede Seite in einem Sprach-Tree hat ein Gegenstück am selben relativen Pfad in jedem anderen konfigurierten Tree (siehe `spec/project/docs-freshness/` für die Audit-Form)
- **MUSS [MUST]** jede Sektions-Label-Übersetzung über `mkdocs-static-i18n`'s `nav_translations` führen; niemals `nav:`-Blöcke pro Sprache duplizieren
- **SOLLTE [SHOULD]** die umgebende Hülle (Sektions-Intros, Indexseiten, Navigations-Labels, Footer-Text) für jede konfigurierte Sprache übersetzen; **KANN [MAY]** Seiten-Bodies, deren Quelle ein EN-kanonisches Artefakt ist (Katalog-Seiten, die Quell-Frontmatter zitieren, ADR-Einträge, deren kanonische Form EN ist, …) in ihrer kanonischen Sprache über alle Sprach-Trees beibehalten, vorausgesetzt die Hülle drumherum ist übersetzt und die Seite deklariert die Quellsprache in ihrem Frontmatter via `source_language: en`

### Build-Verifikation

- **MUSS [MUST]** `mkdocs build --strict` als Teil der CI des Projekts auf jedem Pull Request laufen lassen; ein Non-Zero-Exit blockiert den Merge
- **MUSS [MUST]** das `task docs`-Target des Projekts (oder Äquivalent) dieselbe Build-Sequenz invocen lassen, die in CI läuft, damit ein lokaler Pass einem CI-Pass entspricht
- **SOLLTE [SHOULD]** einen Per-Page-Paritätscheck im selben CI-Job einbauen (heute ausgeliefert über `docs-freshness`), damit eine fehlende Übersetzung den Build vor dem Review brechen lässt, nicht danach

### Auffindbarkeit und Querverweise

- **MUSS [MUST]** einen einzeiligen Verweis auf diese Spec in `spec/project/project-structure/` neben den MkDocs-MUSSes anbringen, damit ein Leser, der auf `project-structure` landet, auf die detaillierte Form gestoßen wird
- **SOLLTE [SHOULD]** von `spec/project/docs-freshness/` als normative Quelle für die erwartete Nav und Parität referenziert werden (der Audit prüft gegen die Spec, statt die Erwartungen neu zu erfinden)
- **KANN [MAY]** von projekt-typ-spezifischen Erweiterungs-Specs (`skill-agent-catalog`, künftige `cookiecutter-template-docs`, künftige `library-api-docs`) als die Basis zitiert werden, die sie erweitern

## Akzeptanzkriterien
<!-- Testbare, prüfbare Bedingungen. Ein Reviewer sollte jede als erledigt/nicht erledigt markieren können. -->
- [ ] Jedes Portfolio-Repository mit `mkdocs.yml` behält `docs_dir: docs` bei und organisiert Dokumentation unter `docs/<lang>/` für jede Sprache aus `spec/.spec-config.yml`
- [ ] Das `mkdocs.yml` jedes Portfolio-Repositorys deklariert `mkdocs-material`, `mkdocs-static-i18n` (mit `docs_structure: folder`), `pymdownx.superfences` und das eingebaute `search`-Plugin explizit
- [ ] Jedes Plugin in `mkdocs.yml` ist im Python-Dependency-Manifest des Projekts gepinnt (keine `>=`-floatenden Versionen im Lockfile)
- [ ] Jede Top-Level-Nav-Sektion in jedem Portfolio-Repository ist eine der sieben Standard-Sektionen (Home, Getting Started, Guides, References, ADRs, Project, plus deklarierter Erweiterungs-Sektionen); eine Sektion, die nicht im Standard-Set steht, ist durch eine aktive Erweiterungs-Spec gerechtfertigt
- [ ] Jede Seite unter `docs/<lang>/` beginnt mit einer einzigen `# H1`, die dem Nav-Label entspricht, und deklariert Frontmatter mit `title`, `audience` (eine oder mehrere IDs aus dem Audience-Artefakt des Projekts) und `last_updated`
- [ ] Jeder Audience-Wert im Frontmatter jeder Seite entspricht einer im Audience-Artefakt des Projekts deklarierten ID (prüfbar via `docs-freshness`-Audit)
- [ ] Jeder `docs/<lang>/`-Tree enthält dieselbe Menge an relativen Pfaden wie jeder andere konfigurierte `docs/<lang>/`-Tree (Dateinamen-Parität, ebenfalls prüfbar via `docs-freshness`)
- [ ] `mkdocs build --strict` läuft in CI auf jedem Pull Request grün, und das `task docs` (oder lokales Äquivalent) des Projekts führt dieselbe Sequenz aus
- [ ] Jede projekt-typ-spezifische Erweiterungs-Spec, die MkDocs berührt (`spec/claude/skill-agent-catalog/`, künftige `cookiecutter-template-docs`, …), deklariert ihre hinzugefügten Sektionen (mit Einfüge-Position und Audience), ihre hinzugefügten Plugins (mit Pin und Rationale) und etwaige Basis-MUSSes, die sie explizit relaxiert
- [ ] Kein Portfolio-Repository hat in seiner `mkdocs.yml` mehr als fünf Erweiterungs-Sektionen insgesamt (Summe über jede aktive Erweiterungs-Spec); ein Repo am oder über dem Cap konsolidiert Sektionen oder schlägt eine Spec-Änderung vor
- [ ] Jedes Projekt-Audience-Artefakt deckt die portfolio-weite Audience-Basis (`user`, `contributor`, `operator`, `release-manager`) ab oder notiert die Auslassung jeder Basis-Audience, die das Projekt echt nicht bedient, ausdrücklich
- [ ] `spec/project/project-structure/` trägt einen einzeiligen Querverweis auf diese Spec neben seinen MkDocs-MUSSes
- [ ] Keine zwei Portfolio-Repositories haben in ihren `mkdocs.yml`-Dateien widersprüchliche `nav:`-Formen für die sieben Standard-Sektionen (Erweiterungs-Sektionen dürfen sich pro Projekttyp unterscheiden)

## Offene Fragen
<!-- Ungelöste Entscheidungen, bekannte Unbekannte, Punkte, die eine Stakeholder-Antwort brauchen. -->
- Keine zum Entwurfszeitpunkt. Die sieben initialen Design-Fragen (ADR-Sektions-Trigger, Project-Sektions-Opt-in, Mechanismus für Erweiterungs-Erkennung, Audience-Basis, Quellsprachen-Deskriptor, Cap für Erweiterungs-Sektionen, absolute Position von Skills/Agents) wurden während der initialen Autorenschaft geklärt; siehe den PR, der diese Spec einführt, für die Rationale jeder Frage.
