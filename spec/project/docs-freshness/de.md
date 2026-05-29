# Doku-Aktualität

Status: draft

## Kontext
Jedes Portfolio-Repository, das Dokumentation ausliefert, tut das über MkDocs, typischerweise in einem zweisprachigen Layout (`docs/en/` und `docs/de/`) mit Architecture Decision Records, Benutzerhandbüchern und Referenzen zurück nach `spec/`, `src/` und weitere Repo-Roots. Diese Dokumente driften: Umbenennungen in der Codebasis brechen Links, eine Sprachbaum hinkt dem anderen hinterher, ADRs sammeln `TODO`-Marker an, die niemand erneut aufgreift, und der MkDocs-Build besteht trotzdem, weil er tote relative Links oder Inhalts-Paritätslücken nicht als Fehler behandelt. Beitragende bemerken die Drift erst, wenn ein Leser sich beschwert, ein Release-Blurb auf eine verschobene Seite verlinkt oder eine Suche zwei widersprüchliche Guides liefert. Diese Spec definiert die Aktualitäts-Praxis: welche Kategorien von Drift zählen, wie sie klassifiziert werden, wann das Audit läuft und wie Befunde in Handlung übergehen. Sie ergänzt `spec/project/spec-drift-audit/` (Spec vs. Implementierung) und `spec/project/prose-style/` (Vale-getriebene Prosa-Korrektheit), indem sie die Fläche besetzt, die die beiden nicht abdecken — die Drift der Dokumentation selbst gegen den Zustand des Repositorys und gegen ihren Gegenpart-Sprachbaum.

## Ziele
- Jedes Repository mit MkDocs-Dokumentation führt an dokumentierten Triggern ein Aktualitäts-Audit durch, das jede portable Drift-Kategorie abdeckt
- Das Audit ist read-only und produziert einen nach Schweregrad sortierten Report; Korrekturen sind ein bewusster, separater Schritt
- Befunde werden nach einer geteilten Schweregrad-Skala klassifiziert, sodass ein toter interner Link portfolio-übergreifend gleich behandelt wird
- Zweisprachige Repositories verfolgen Sprach-Parität als erstklassiges Anliegen; einsprachige Repositories werden nicht dafür bestraft, keine zu haben
- Das Audit ist klar abgegrenzt gegen Vale-Prosa-Linting, gegen den MkDocs-Build selbst und gegen Spec-Drift — jedes Anliegen besetzt seine eigene Fläche

## Nicht-Ziele
- Die Prüfung externer Links (alles, was `http://` oder `https://` ist): die Tradeoffs um Rate Limits, Flakiness, Geoblocking und False Positives gehören in ein anderes Werkzeug
- Prosa-Linting, Vokabular-Konsistenz oder Style-Guide-Durchsetzung: das ist `spec/project/prose-style/` + `prose-vale-curator`
- Rendering-Validierung: MkDocs selbst (`mkdocs build --strict` in CI) ist die autoritative Prüfung, dass die Site rendert
- Die Deklaration der On-Disk-Form von MkDocs (i18n-Plugin-Wahl, Theme, Nav-Struktur) — das gehört jetzt zu `spec/project/mkdocs-structure/`. Dieses Audit liest `mkdocs.yml`, um zu erkennen, was tatsächlich verdrahtet ist, und prüft dann Konformität gegen die Erwartungen von `mkdocs-structure`; es definiert die Form nicht neu
- Die Definition operativer Details des Agents, der das Audit implementiert (`agents/docs-freshness-checker.md`): diese können sich ohne Spec-Änderung entwickeln

## Anforderungen

### Geltungsbereich
- **MUSS** jede Markdown-Datei unter dem in `mkdocs.yml` konfigurierten MkDocs-`docs_dir` einschließen; Dateien außerhalb dieses Verzeichnisses sind nicht im Geltungsbereich dieses Audits
- **MUSS** ADRs einschließen, die unter `docs/<lang>/adr/` (Portfolio-Konvention) liegen, wenn ein `adr/`-Ordner unter einem konfigurierten Sprachbaum existiert
- **MUSS** jedem internen Markdown-Link folgen (`](relative-path)` und Referenzstil `[id]: path`) sowie jeder Pfad-Referenz in Repo-Roots, die die Docs erwähnen (`spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/`); gebrochene Referenzen sind Befunde
- **DARF** den Geltungsbereich auf eine einzelne Kategorie einschränken (nur Links, nur Parität, nur ADRs), wenn die aufrufende Person ein Teilaudit anfordert; die Einschränkung **MUSS** im Audit-Artefakt festgehalten werden

### Drift-Kategorien
Das Audit **MUSS** jeden Befund in genau eine dieser Kategorien klassifizieren:

- **Interner-Link-Rot**: ein relativer Markdown-Link, dessen Ziel auf der Disk nicht existiert. Anker werden strikt aufgelöst — die Datei muss existieren; das Anker-Ziel innerhalb der Datei ist eine `SOLLTE`-Prüfung, keine `MUSS`-Prüfung, weil Anker-Erkennung über Themes hinweg fragil ist. Diese `SOLLTE`-Prüfung ist ein aufgeschobener Härtungsschritt und keine dauerhafte Obergrenze: da `spec/project/mkdocs-structure/` nun eine einzige Theme-Engine (`mkdocs-material`) vorschreibt, ist die Theme-übergreifende Variabilität portfolioweit verschwunden und das Slugifizierungs-Ziel ein einziger bekannter Algorithmus, sodass die Prüfung auf `MUSS` anhebbar ist, sobald ein Material-Slugify-basierter Detektor eine niedrige False-Positive-Rate auf realen Docs-Bäumen misst (die Anker-Behandlung in §Schweregrad-Klassifikation bleibt unverändert).
- **Cross-Tree-Referenz-Rot**: ein Link aus den Docs nach `spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/`, dessen Zielpfad im Arbeitsbaum nicht mehr existiert.
- **Sprach-Paritäts-Lücke**: in einem zweisprachigen (oder mehrsprachigen) Repository ein relativer Pfad, der in einem konfigurierten Sprachbaum existiert, aber in einem anderen fehlt. Das Autorenschafts-Pendant, das die Lücke an der Quelle verhindert, ist `spec/project/docs-multilingual-authoring/` §Erzeugungsprotokoll.
- **Inhalts-Staleness-Delta**: in einem mehrsprachigen Repository Gegenpart-Dateien, deren letzte Commit-Zeitstempel über eine Schwelle (Standard 30 Tage) divergieren oder deren Größen um mehr als 2× divergieren; diese werden an den N jüngst geänderten Dateien pro Baum (Standard N=5) stichprobenhaft geprüft, nicht erschöpfend. Die N=5-Obergrenze ist eine bewusste günstige Untergrenze; sie ist revisitierbar, wenn ein großer Docs-Baum (mehr als 50 Dateien) eine übersehene Divergenz älter als 90 Tage nachweist.
- **Mermaid-Diagramm-Quell-Drift**: ein Mermaid-Block in der Doku, annotiert mit `<!-- diagram-source: derived — <pfad> -->` (gemäß `spec/project/mermaid-diagrams/`), dessen genanntes Quell-Artefakt einen jüngeren Last-Commit-Zeitstempel hat als die Markdown-Datei, die den Block enthält — die Quelle hat sich geändert, das Diagramm wurde aber nicht neu gezeichnet. Der Detektor vergleicht `git log -1 --format=%cs -- <quelle>` und `git log -1 --format=%cs -- <markdown-datei>`; `user-described`-Blöcke werden nicht geprüft, da sie keine maschinenlesbare Quelle haben.
- **ADR-Index-Drift**: eine ADR-Datei auf der Disk, die nicht vom zugehörigen `adr/index.md` referenziert wird, oder ein `adr/index.md`-Eintrag, dessen Datei nicht existiert. Wenn `adr/index.md` generiert wird (deklariert durch einen Generator-Hook oder einen Frontmatter-Marker wie `last_updated: generated` gemäß `spec/project/mkdocs-structure/` §Per-Page-Struktur), **MUSS** der ADR-Index-Drift-Check es überspringen; die Aktualität generierter Indizes wird vom eigenen CI-Aktualitäts-Check des Generators (einem `git diff --exit-code`-Durchgang) besessen, nicht von diesem read-only-Audit (siehe §Read-only-Disziplin und §Abgrenzung).
- **ADR-Status-Hygiene**: ein ADR, dessen deklarierter Status nicht einer von `proposed`, `accepted`, `superseded`, `deprecated`, `rejected` ist; oder eine `Supersedes: ADR-NNN`-Referenz, die auf ein ADR zeigt, dessen Status noch `accepted` ist.
- **Stale-Marker**: Vorkommen von `TODO`, `FIXME`, `XXX`, `TBD`, `coming soon`, `placeholder`, `Lorem ipsum` (und ihre deutschen Entsprechungen) in der Dokumentation; die Klassifikation hängt vom Kontext ab (ADR vs. Prosa).
- **Track-Frontmatter-Drift**: eine Seite unter `docs/<lang>/` (außerhalb `_`-präfixierter Snippet-Ordner), der der `track`-Frontmatter-Schlüssel fehlt oder deren `track`-Wert nicht `user-docs`, `developer-docs` oder ein Erweiterungs-Wert ist, der von einer projekt-typ-spezifischen Spec deklariert wurde, in die das Repository eingewilligt hat. Bezugnehmend auf `spec/project/docs-audience-tracks/` §Per-Page-Kontrakt.
- **Content-Mode-Drift**: eine Seite unter `docs/<lang>/` (außerhalb Snippet-Ordnern), der der `content_mode`-Frontmatter-Schlüssel fehlt oder deren `content_mode`-Wert nicht einer aus `tutorial`, `how-to`, `reference`, `explanation`, `troubleshooting`, `glossary`, `meta` oder ein Erweiterungs-Wert einer projekt-typ-spezifischen Spec ist. Mischungs-Verstöße (eine `how-to`-Seite, die ausgedehnte `explanation`-Inhalte ausliefert, eine `reference`-Seite mit eingebetteten Rezepten) werden als `Content-Mode-Mischungs`-Befunde mit Warning-Severity gemeldet — die Erkennung ist ein Reviewer-Urteils-Signal, kein strikter Regex-Match, also listet das Audit Kandidaten-Seiten ohne Auto-Fail.
- **Audience-Track-Mismatch**: eine Seite, deren `audience`-Frontmatter-Wert auf eine andere Spur abbildet als der `track`-Frontmatter-Wert der Seite, gemäß dem Default-Mapping in `spec/project/docs-audience-tracks/` §Audience-zu-Spur-Mapping (pro Projekt mit dokumentierter Begründung im Audience-Artefakt übersteuerbar).

Zusätzliche Kategorien **DÜRFEN** von einem Repository hinzugefügt werden, wenn seine Dokumentation sie braucht (zum Beispiel ein API-Referenz-vs-Code-Check in einem Repository, das eine OpenAPI-Spec ausliefert), aber die portfolioweiten Kategorien oben sind die Untergrenze.

### Schweregrad-Klassifikation
- **MUSS** die folgende Schweregrad-Skala übernehmen:
  - **critical**: Interner-Link-Rot, Cross-Tree-Referenz-Rot, ADR-Status-Inkonsistenz, die eine Supersedes-Kette bricht, Track-Frontmatter-Drift mit nicht-erkanntem Wert (statt schlicht fehlend), Content-Mode-Drift mit nicht-erkanntem Wert; Reaktionsfenster: vor dem nächsten Release
  - **warning**: Sprach-Paritäts-Lücke, Stale-Marker in einem ADR mit Status `accepted`, ADR-Index-Drift, Inhalts-Staleness-Delta > 90 Tage, Mermaid-Diagramm-Quell-Drift, Track-Frontmatter-Drift (fehlender Schlüssel), Content-Mode-Drift (fehlender Schlüssel), Content-Mode-Mischungs-Kandidat, Audience-Track-Mismatch; Reaktionsfenster: innerhalb des laufenden Quartals
  - **info**: Stale-Marker in gewöhnlicher Prosa, Inhalts-Staleness-Delta 30 – 90 Tage, ADR ohne deklarierten Status (als Info, nicht kritisch, behandeln — das ADR ist weiterhin lesbar); Reaktionsfenster: best effort
- **DARF NICHT** einen Schweregrad allein auf Basis lokaler Einschätzung absenken; Abweichung von der Klassifikation gehört in eine explizite Waiver-Notiz, festgehalten im Audit-Artefakt

### Auslöser und Kadenz
- **MUSS** in jedem Repository mit einem `docs_dir` mindestens ein vollständiges Audit pro Kalenderquartal durchführen
- **MUSS** zusätzlich vor jedem Release-Tag laufen, der Dokumentationsänderungen seit dem vorigen Audit enthält
- **SOLLTE** als Pre-PR-Gate laufen, sobald ein PR Dokumentation modifiziert; das Gate ist optional, aber empfohlen, weil Drift zum PR-Merge-Zeitpunkt am schnellsten kaskadiert
- **DARF** auf einer kürzeren Kadenz (monatlich) laufen für Repositories, deren Dokumentation eine primäre Produktfläche ist
- **DARF** einen Pre-Release-Lauf auf ausschließlich die Kategorien mit Critical-Severity einschränken (Interner-Link-Rot, Cross-Tree-Referenz-Rot, ADR-Supersedes-Ketten-Brüche, nicht-erkannte Track-/Content-Mode-Werte) als schnelles Pre-Tag-Gate — ein benanntes „Release-Readiness"-Einschränkungs-Preset statt eines separaten Audit-Modus; die Einschränkung **MUSS** gemäß §Geltungsbereich festgehalten werden

### Read-only-Disziplin
- **MUSS** read-only sein: das Audit berichtet Befunde, und Korrekturen sind ein separater, opt-in-Schritt, den eine autorende Person (oder ein anderer Agent) unternimmt
- **DARF NICHT** während des Audits eine Datei modifizieren, erstellen oder löschen — auch nicht auf „sichere" Weise, etwa durch Korrektur eines Tippfehlers in einem gebrochenen Link
- **DARF NICHT** das Netzwerk bemühen; externe Link-Validierung ist außerhalb des Geltungsbereichs (siehe §Nicht-Ziele)
- **DARF NICHT** Inhalte über Sprachbäume hinweg übersetzen, umformulieren oder anderweitig verändern; das Audit berichtet Paritätslücken, schließt sie aber nicht

### Audit-Artefakt
- **MUSS** das Ergebnis jedes vollständigen Audits als Commit, Issue oder Datei im Repository persistieren; der Artefaktort **SOLLTE** der Portfolio-Audit-Trail-Konvention `.audits/docs-freshness/<YYYY>-Q<n>.md` folgen (passend zum andernorts verwendeten Muster `.audits/<skill>/`) und **MUSS** außerhalb des MkDocs-`docs_dir` liegen, damit das Audit niemals seine eigenen Artefakte selbst scannt. Gemeinsam mit der identischen Frage von `spec/project/spec-drift-audit/` aufgelöst.
- **MUSS** im Artefakt enthalten: Datum, Auslöser (quartalsweise, pre-release, PR-change), den verwendeten Repo-Root und `mkdocs.yml`-Pfad, welche Kategorien ausgeführt (oder ausgenommen) wurden, die auditierte Git-Revision, die Schweregrad-Zählungen pro Kategorie und die vollständige Befundliste sortiert nach Schweregrad
- **MUSS** die Listenlänge pro Kategorie im Artefakt auf 15 Einträge begrenzen und den Rest mit einer Zählung zusammenfassen, damit große Drift-Cluster den Report nicht überfluten
- **SOLLTE** `spec/project/parallel-working-copies/` §Audit-Artefakte in mehreren Worktrees konsultieren, wenn das Audit innerhalb eines Worktree statt im primären Checkout läuft; die Cross-Tree- und Paritäts-Befunde spiegeln nur den Arbeitsbaum wider, aus dem das Audit gestartet wurde, und die worktree-lokalen Commit-, Transfer- und Cleanup-Regeln für das `.audits/docs-freshness/`-Artefakt liegen dort

### Abgrenzung
- **MUSS** getrennt bleiben von `spec/project/prose-style/` und dem `prose-vale-curator`-Agent: Vale besitzt Prosa-Korrektheit und Vokabular; dieses Audit besitzt strukturelle Drift
- **MUSS** getrennt bleiben von `spec/project/spec-drift-audit/`: diese Spec deckt Spec-vs.-Implementierung-Abgleich ab; diese hier deckt Dokumentation-vs.-Repository-Abgleich ab
- **MUSS** getrennt bleiben von `mkdocs build --strict`: der Build ist die Rendering-Prüfung; das Audit ist eine Pre-Render-Drift-Prüfung
- **DARF NICHT** kontinuierliche CI-Link-Checks ersetzen, wenn ein Repository bereits einen Link-Checker in CI verdrahtet hat; das Audit ist der periodische Tiefen-Durchgang und das Pre-Release-Gate, das auf dem aufsetzt, was CI bereits leistet

## Akzeptanzkriterien
- [ ] Jedes Repository mit einem `docs_dir` enthält eine nachvollziehbare Docs-Freshness-Audit-Historie (Commits, Issues oder Audit-Dateien) mit mindestens einem Eintrag pro Kalenderquartal seit Einführung dieser Spec, oder eine dokumentierte Ausnahme, die benennt, welches Quartal warum übersprungen wurde
- [ ] Das jüngste Docs-Freshness-Audit-Artefakt deckt jede Kategorie aus §Drift-Kategorien ab, die auf das Repository zutrifft (zweisprachige Checks in zweisprachigen Repos; ADR-Checks, wo ADRs existieren)
- [ ] Kein `critical`-Befund aus dem jüngsten Audit sitzt unerledigt, wenn ein Release-Tag entsteht; Pre-Release-Audits zeigen entweder null kritische Befunde oder die Release-Notes nennen die Waivers ausdrücklich
- [ ] Jedes Docs-Freshness-Audit-Artefakt hält den Repo-Root, den `mkdocs.yml`-Pfad, die auditierte Git-Revision und die Kategorien fest, die (nicht) ausgeführt wurden
- [ ] Kein Audit-Lauf in irgendeinem Repository hat Dokumentation oder eine andere Datei modifiziert; die Read-only-Disziplin des Audits hält in der Praxis, nicht nur in der Spec
- [ ] Der Agent `agents/docs-freshness-checker.md` erzeugt Ausgaben, die 1-zu-1 auf die hier deklarierten Kategorien und Schweregrade abbilden, damit das Artefakt mechanisch erzeugt werden kann
- [ ] Das Audit meldet einen `Track-Frontmatter-Drift`-, `Content-Mode-Drift`- oder `Audience-Track-Mismatch`-Befund, sobald eine Doku-Seite unter einem Nicht-Snippet-Ordner den entsprechenden Kontrakt aus `spec/project/docs-audience-tracks/` oder `spec/project/mkdocs-structure/` §Inhalts-Modi (Diátaxis-Ausrichtung) verletzt

## Offene Fragen
- Standard: die In-Datei-Anker-Ziel-Prüfung bleibt als aufgeschobener Härtungsschritt eine `SOLLTE`-Prüfung. Revisitieren, wenn: beides gilt — (1) eine Slugifizierungs-Routine, die dem `toc.slugify`-Default von `mkdocs-material` (das einzige vorgeschriebene Theme) entspricht, ist in `docs-freshness-checker` implementiert, und (2) ein Dry-Run über den nolte-shared-Docs-Baum plus mindestens einen weiteren Portfolio-Repo-Docs-Baum ergibt eine gemessene False-Positive-Rate unter 5% der aufgelösten Anker-Links — dann die Prüfung von `SOLLTE` auf `MUSS` anheben.
- Standard: die Stichprobe der N jüngst geänderten Dateien bleibt mit N=5 als günstige Untergrenze. Revisitieren, wenn: ein Portfolio-Repo mit mehr als 50 Markdown-Dateien unter `docs_dir` ein vollständiges Docs-Freshness-Audit durchführt UND ein anschließender erschöpfender Inhalts-Staleness-Durchgang über denselben Baum mindestens eine Divergenz der Warning-Stufe (älter als 90 Tage) findet, die die N=5-Stichprobe übersehen hat — die beobachtete Miss-Rate setzt dann entweder ein höheres festes N oder eine Prozentsatz-des-Baums-Obergrenze.
