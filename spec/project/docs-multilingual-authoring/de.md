# Mehrsprachige Dokumentations-Autorenschaft

Status: draft

## Kontext

Portfolio-Repositories liefern MkDocs-Sites, die standardmäßig zweisprachig sind: `spec/project/mkdocs-structure/` §Per-language layout schreibt bereits `docs/<lang>/`-Unterverzeichnisse mit strukturell identischen Datei-Bäumen vor, und `spec/project/docs-freshness/` §Finding categories auditiert die daraus entstehende Drift als `Language-parity gap`-Finding. Was keine der beiden Specs definiert, ist das **Erzeugungsprotokoll** — *wie* und *wann* eine doku-erzeugende Skill oder Agent eine Seite in jeden konfigurierten Sprachbaum schreibt. Die Folge ist asymmetrische Autorenschaft: Eine Skill schreibt `docs/en/foo.md`, lässt `docs/de/foo.md` für später, und die Lücke fällt erst im nächsten Quartals-`docs-freshness`-Audit auf. Bis dahin ist die kanonische Seite weitergezogen, der Autor hat den Kontext verloren, und die Übersetzung wird aus einem veralteten Schnappschuss rekonstruiert.

Diese Spec schließt die Lücke, indem sie den Canonical-und-Translation-Vertrag, der bereits `spec/<topic>/<slug>/` regelt (eine Datei pro Sprache, atomar geschrieben, Englisch kanonisch, Drift gemanagt), auf jede Markdown-Seite unter `docs_dir` überträgt. Sie ist das **Autorenschafts-Pendant** zum Form-Vertrag von `mkdocs-structure` und zum Audit-Vertrag von `docs-freshness`: Form sagt „die Bäume MÜSSEN [MUST] parallel sein", Audit sagt „wir erkennen, wenn sie es nicht sind", und diese Spec sagt „jeder Erzeugungsschritt hält sie von Beginn an parallel".

## Ziele

- Doku-erzeugende Skills und Agents schreiben jede konfigurierte Sprachfassung einer `docs/<lang>/`-Seite **atomar im selben Erzeugungsschritt**, mit Englisch als kanonischer Quelle und anderen konfigurierten Sprachen als strukturell identische Übersetzungen
- Das Repository erreicht infolge eines Skill- oder Agent-Outputs nie einen Zustand, in dem eine Seite in einem Sprachbaum existiert, in einem anderen aber nicht
- Das Protokoll nutzt dieselbe Konfigurationsoberfläche, die bereits `spec/<topic>/<slug>/` regelt — nämlich die Schlüssel `canonical_language` und `languages` in `spec/.spec-config.yml` — sodass ein Repository seine Sprachmatrix an genau einer Stelle deklariert
- README.md ist explizit aus dem Mehrsprachigkeitsvertrag ausgenommen; sie bleibt nur-Englisch gemäß `spec/project/readme-structure/` §File and language
- Die Abgrenzung gegen `mkdocs-structure` (Form), `docs-freshness` (Audit) und `readme-structure` (README-Ausnahme) ist scharf genug, dass keine Anforderung in zwei Specs wiederholt wird

## Nicht-Ziele

- Definition des sprachspezifischen Verzeichnis-Layouts, der Plugin-Auswahl oder des Nav-Vertrags — das gehört zu `spec/project/mkdocs-structure/`
- Drift-Erkennung zwischen Sprachbäumen im Nachhinein — das ist das `Language-parity gap`-Finding aus `spec/project/docs-freshness/`
- Übersetzung von README.md — die README bleibt nur-Englisch gemäß `spec/project/readme-structure/` §File and language, und deren Non-Goals schließen README-Übersetzungen bereits aus
- Übersetzung von Release Notes — `spec/project/release-skill-layer/` besitzt den Release-Notes-Vertrag und entscheidet seine eigene Sprachpolitik
- Übersetzung von GitHub-Issue-Forms unter `.github/ISSUE_TEMPLATE/` — `spec/project/github-issue-templates/` besitzt diese Oberfläche
- Übersetzung von CHANGELOG.md oder irgendeines Markdown-Artefakts außerhalb von `docs_dir`
- Festlegung einer bestimmten Übersetzungsqualität oder einer bestimmten Übersetzungs-Engine — diese Spec regelt das **strukturelle** Protokoll (welche Dateien existieren, welche Form sie teilen, wer wann schreibt); die Übersetzungsqualität auf Token-Ebene bleibt in der Verantwortung der erzeugenden Skill oder des erzeugenden Agents
- Vorschrift, dass eine manuelle Ad-hoc-Bearbeitung innerhalb eines einzelnen Sprachbaums sofort einen Übersetzungsdurchlauf auslöst — Drift durch manuelle Bearbeitung wird von `docs-freshness` erkannt, nicht von dieser Spec verhindert

## Anforderungen

<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Erzeugungsprotokoll

- **MUSS [MUST]** jede Skill oder jeden Agent, der eine Markdown-Datei (`*.md`) unter dem in `mkdocs.yml` konfigurierten MkDocs-`docs_dir` erzeugt, bearbeitet, umbenennt oder löscht, als *doku-erzeugende Fähigkeit* im Geltungsbereich dieser Spec behandeln; die erzeugende Fähigkeit ist dafür verantwortlich, jeden MUSS [MUST] unten im **gleichen Erzeugungsschritt** zu erfüllen (derselben Skill-Invokation, demselben Agent-Lauf, derselben Tool-Call-Folge — nicht „später", nicht „in einem Folge-Commit")
- **MUSS [MUST]** die Sprachmatrix zu Beginn jedes Erzeugungsschritts aus `spec/.spec-config.yml` auflösen (`canonical_language`, `languages`); dieselbe Datei, die `spec/<topic>/<slug>/` regelt, wird hier wiederverwendet, sodass das Repository seine Sprachmatrix an genau einer Stelle deklariert
- **MUSS [MUST]** den Wert von `canonical_language` als **Quelle der Wahrheit** für jede in diesem Schritt verfasste Seite behandeln; jeder andere Eintrag in `languages` ist eine **Übersetzung**, die die kanonische Seite strukturell spiegelt
- **MUSS [MUST]** die entsprechende Datei unter `docs/<other_language>/<same-relative-path>` für **jede** andere Sprache in `languages` schreiben oder aktualisieren, sobald die kanonische Datei unter `docs/<canonical_language>/<relative-path>` erzeugt oder aktualisiert wird; die Operation ist **atomar** — entweder wird jede Sprachfassung im selben Schritt geschrieben oder keine
- **DARF [MUST] NICHT** einen Erzeugungsschritt als erfolgreich markieren, wenn eine oder mehrere konfigurierte Sprachfassungen einer berührten Seite auf der Platte fehlen; ein partieller Schreibvorgang ist eine Verletzung, unabhängig vom Exit-Status der erzeugenden Skill
- **DARF [MUST] NICHT** `README.md` im Repository-Wurzelverzeichnis übersetzen, umbenennen oder löschen, ebenso wenig eine Datei, die die erzeugende Skill nach Repository-Konvention als nur-Englisch identifiziert (Cross-Ref: `spec/project/readme-structure/` §File and language deklariert die README als nur-Englisch)
- **MUSS [MUST]** Datei-Baum-Operationen symmetrisch über die Sprachbäume propagieren: Das Umbenennen von `docs/<canonical_language>/a.md` zu `docs/<canonical_language>/b.md` MUSS [MUST] das Gegenstück in jedem anderen Sprachbaum im selben Schritt umbenennen; das Löschen von `docs/<canonical_language>/foo.md` MUSS [MUST] jedes Gegenstück löschen

### Strukturelle Parität der Übersetzung

- **MUSS [MUST]** den Heading-Baum jeder Übersetzungsdatei strukturell identisch zur kanonischen Vorlage halten: gleiche `#`/`##`/`###`-Tiefe, gleiche Heading-Reihenfolge, gleiche Heading-Anzahl. Heading-**Text** wird übersetzt; Heading-**Struktur** nicht
- **MUSS [MUST]** das YAML-Frontmatter-Schlüssel-Set über die Sprachen erhalten: Jeder auf der kanonischen Seite deklarierte Schlüssel (`title`, `audience`, `content_mode`, `last_updated`, `track` und jeder projekttyp-spezifische MUSS-[MUST]-Schlüssel) erscheint mit dem gleichen Namen in jeder Übersetzung
- **MUSS [MUST]** Frontmatter-**Werte** lokalisieren, die sichtbare Anzeige-Strings sind (typischerweise `title`), und **DARF [MUST] NICHT** Frontmatter-**Werte** lokalisieren, die portfolio-weite Identifier sind (`audience`-IDs aus dem Audience-Artefakt gemäß `spec/project/audience-identification/`, `track`-Enum-Werte aus `spec/project/docs-audience-tracks/`, `content_mode`-Enum-Werte aus `spec/project/mkdocs-structure/`); Identifier sind sprachübergreifend stabil
- **MUSS [MUST]** relative interne Markdown-Links auf dasselbe Ziel innerhalb des sprachbaum-eigenen Pfads zeigen lassen; ein Link von `docs/en/a.md` auf `b.md` übersetzt zu einem Link von `docs/de/a.md` auf `b.md` (gleicher relativer Pfad, gleiche Zielseite, keine `../en/`-Traversierung zwischen Sprachbäumen)
- **MUSS [MUST]** `mkdocs-include-markdown-plugin`-Direktiven über Sprachversionen hinweg identisch halten, wenn die eingeschlossene Quelle sprachneutral ist (eine Datei unter `src/`, `spec/`, eine YAML-Config, ein Code-Auszug); die Include-Direktive selbst ist identischer Text in beiden Übersetzungen, sodass der gerenderte Inhalt synchron bleibt, ohne dass pro Sprache geforkt werden muss
- **MUSS [MUST]** RFC-2119-Keywords (`MUST`, `SHOULD`, `MAY`) in Übersetzungsdateien in Englisch belassen und sie inline in der Zielsprache glossieren (zum Beispiel `MUSS [MUST]`, `SOLLTE [SHOULD]`, `KANN [MAY]`), entsprechend der Konvention, der `spec/<topic>/<slug>/` bereits folgt
- **DARF [MUST] NICHT** Bullets, Listenelemente, Tabellenzeilen, Checklisteneinträge oder Codeblöcke zwischen Kanonik und Übersetzung weglassen, umordnen oder zusammenführen; der *Inhalt* jeder Einheit wird übersetzt, *Anzahl und Reihenfolge* bleiben erhalten

### Snippets

- **MUSS [MUST]** dieses Protokoll nur auf **Seiten** (Dateien außerhalb `_`-präfigierter Ordner unter `docs/<lang>/`) anwenden; Snippet-Fragmente in `_`-präfigierten Ordnern (`docs/<lang>/_snippets/` und Äquivalenten gemäß `spec/project/mkdocs-structure/` §Snippet inclusion (DRY)) sind keine Seiten und fallen nicht in den Geltungsbereich der strukturellen-Parität-MUSSe oben
- **KANN [MAY]** ein sprachneutrales Snippet (ein Code-Auszug, ein YAML-Fragment, ein CLI-Transkript) in nur einem Sprachbaum vorhalten, eingeschlossen aus beiden Sprachbäumen via `mkdocs-include-markdown-plugin`; das ist die bevorzugte Form für Inhalte, die nicht übersetzt werden
- **MUSS [MUST]** die strukturelle-Parität-MUSSe dieses Protokolls auf ein Snippet anwenden, das übersetzbaren Prosatext enthält (ein Fragment erklärenden Texts, das von mehreren Seiten eingeschlossen wird); ein solches Snippet wird einmal pro Sprache verfasst, über `docs/<lang>/_snippets/` gespiegelt wie eine Seite

### Abstimmung mit Nachbar-Specs

- **MUSS [MUST]** auf `spec/project/mkdocs-structure/` §Per-language layout für den Datei-Baum-Paritätsvertrag und auf `spec/project/docs-freshness/` §Finding categories für die Audit-Zeit-Erkennung von Verletzungen verweisen; diese Spec **DARF [MUST] NICHT** einen der beiden Verträge wiederholen
- **MUSS [MUST]** auf `spec/project/readme-structure/` §File and language als Quelle der README-nur-Englisch-Ausnahme verweisen; diese Spec **DARF [MUST] NICHT** die README-Regel wiederholen
- **DARF [MUST] NICHT** einen MUSS [MUST] aus `mkdocs-structure`, `docs-freshness`, `readme-structure`, `docs-audience-tracks` oder `audience-identification` überstimmen oder abschwächen; Konflikte werden durch Anpassung der vorgelagerten Spec aufgelöst, nicht durch eine Ausnahme in dieser
- **MUSS [MUST]** automatisch erzeugte Katalog-Seiten unter `docs/<lang>/skills/` und `docs/<lang>/agents/` als doku-erzeugenden Output behandeln, der an die strukturellen MUSSe aus §Erzeugungsprotokoll gebunden ist (eine Seite pro Sprache pro Artefakt, parallele Bäume); `spec/claude/skill-agent-catalog/` besitzt deren sprachspezifisches Rendering und verwendet seinen reservierten Auto-Tag `_translation-pending` sowie das „translation pending"-Badge als katalog-spezifische Form des `needs-review`-Auswegs. Diese Spec **DARF [MUST] NICHT** die Summary-Resolution- oder Fallback-Regeln des Katalogs wiederholen

### Übersetzungsqualität und Review

- **SOLLTE [SHOULD]** den kanonischen Edit und jede Übersetzung im selben Commit ausliefern, damit ein Reviewer beide Seiten zusammen liest; sie in getrennten Commits zu staffeln ist ein Geruch, der den Atomic-Write-MUSS [MUST] oben aushebelt
- **SOLLTE [SHOULD]** eine Übersetzung mit einem inline HTML-Kommentar `<!-- translation-status: needs-review -->` markieren, wenn die erzeugende Skill semantische Treue nicht selbst garantieren kann (zum Beispiel ein Generator, der kanonischen Inhalt aus strukturierten Daten emittiert und eine Best-Effort-Rendering in der Zielsprache); der Marker ist ein `docs-freshness`-Finding (Severity warning), bis ein Reviewer ihn entfernt
- Diese Spec definiert genau einen autorgesetzten Übersetzungsschuld-Marker, `needs-review`. Best-Effort-Generator-Output wird über den Auto-Tag `_translation-pending` aus `spec/claude/skill-agent-catalog/` signalisiert; Kanonik-gegen-Übersetzung-Veraltung wird von `spec/project/docs-freshness/` erkannt. Eine reichere geschlossene Menge landet nur dann in `docs-freshness` §Severity classification, wenn ein Audit-Muster zeigt, dass der binäre Marker unzureichend ist (siehe Offene Fragen)
- **MUSS [MUST]** den Marker `<!-- translation-status: needs-review -->` als HTML-Kommentar in der ersten Body-Zeile unmittelbar nach dem Frontmatter-Block platzieren, sodass er in der gerenderten MkDocs-Seite unsichtbar bleibt, aber aus CI heraus greppbar ist (dieselbe Inhalts-Scan-Erkennung, die `spec/project/docs-freshness/` §Finding categories bereits für veraltete Marker nutzt); der Marker **DARF [MUST] NICHT** als Frontmatter-Schlüssel ausgedrückt werden, was den Frontmatter-Schlüssel-Set-MUSS [MUST] aus §Strukturelle Parität der Übersetzung brechen würde (die kanonische Seite trägt keinen solchen Schlüssel)
- **MUSS [MUST]** einen Autor, der die Übersetzung einer noch im Entwurf befindlichen Seite noch nicht garantieren kann — einschließlich eines ADR unter `docs/<lang>/adr/` mit Status `proposed` —, an den Atomic-Write-MUSS [MUST] aus §Erzeugungsprotokoll wie jede andere Seite gebunden behandeln: Beide Sprachfassungen werden im selben Schritt ausgeliefert, mit `<!-- translation-status: needs-review -->` auf der Übersetzung als Ausweg; es gibt keine statusbedingte Ausnahme
- **KANN [MAY]** die Token-Übersetzung an `audience-doc-author` (oder einen vergleichbaren Agent, der Übersetzung im Portfolio bereits besitzt) als Sub-Schritt der erzeugenden Fähigkeit delegieren, statt Übersetzung in jeder Skill neu zu implementieren

### Einsprachige Repositories

- **KANN [MAY]** ein Repository, dessen `spec/.spec-config.yml`-`languages:`-Liste genau einen Eintrag enthält, diese Spec als trivial erfüllt behandeln: Jeder Erzeugungsschritt schreibt genau eine Sprachfassung, die zugleich die kanonische ist, und keine Paritäts-MUSSe greifen. Das Repository **MUSS [MUST]** weiterhin das `docs/<lang>/`-Layout gemäß `mkdocs-structure` §Per-language layout verwenden, sodass das Hinzufügen einer zweiten Sprache später eine rein-additive Änderung ist

## Akzeptanzkriterien

<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->

- [ ] Jede Skill unter `skills/` und jeder Agent unter `agents/`, in deren Body deklariert ist, dass sie Markdown nach `docs/<lang>/` schreiben, referenziert diese Spec in ihrem Hard-Rules-Abschnitt und folgt dem Atomic-Authoring-MUSS [MUST] oben
- [ ] Eine Test-Invokation von `audience-doc-author`, die eine neue Seite erzeugt, emittiert `docs/<canonical_language>/<slug>.md` und `docs/<other_language>/<slug>.md` im selben Lauf, mit identischen Heading-Bäumen und identischen Frontmatter-Schlüssel-Sets
- [ ] Ein simulierter einsprachiger Schreibvorgang (vorsätzliches Entfernen einer Sprachdatei nach dem Erzeugungsschritt) wird von `docs-freshness` als `Language-parity gap`-Finding mit Severity `warning` gemeldet
- [ ] `README.md` im Repository-Wurzelverzeichnis bleibt über das gesamte Skill- und Agent-Korpus nur-Englisch; keine Skill und kein Agent, die diese Spec implementieren, produziert `README.de.md` oder eine andere lokalisierte README-Variante
- [ ] `spec/project/mkdocs-structure/` §Per-language layout cross-referenziert diese Spec als Autorenschafts-Pendant (additiver Satz, keine Vertragsänderung)
- [ ] `spec/project/docs-freshness/` §Finding categories cross-referenziert diese Spec als Autorenschafts-Pendant (additiver Satz, keine Vertragsänderung)
- [ ] `spec/project/readme-structure/` §Non-Goals cross-referenziert diese Spec als die kanonische Deklaration, dass die README-Ausnahme portfolio-weit gilt (additiver Satz, keine Vertragsänderung)
- [ ] Eine Umbenennung einer kanonischen Seite (`git mv docs/en/foo.md docs/en/bar.md`), die durch eine doku-erzeugende Skill durchgeführt wird, benennt das Gegenstück in jedem konfigurierten Sprachbaum im selben Schritt um

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Siehe `.audits/decisions/2026-06-06-settle-open-questions.md` für die Einzelentscheidungen und Begründungen._
