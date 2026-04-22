# Repository-README-Struktur

Status: Entwurf

## Kontext
Jedes Repository in diesem Portfolio liefert eine `README.md` auf oberster Ebene — vorgeschrieben durch die `project-structure`-Spec —, aber die innere Gestalt dieser Datei ist zwischen Repositories auseinandergelaufen. Konsumentinnen und Konsumenten (Menschen wie KI-Agenten) suchen in READMEs nach denselben Dingen in derselben Reihenfolge: *was ist das, warum existiert es, wie nutze ich es, wie fügt es sich ins Portfolio ein*. Wenn Abschnittsauswahl und -reihenfolge pro Repository abweichen, zahlen sowohl nachgelagerte Werkzeuge (Plugin-Marktplätze, Paketindizes, KI-Agenten, die Zusammenfassungen synthetisieren) als auch menschliche Leser den Preis.

Die Referenzimplementierung ist die `README.md` dieses Repositories selbst. Sie adressiert unterschiedliche Software-Elemente — Claude-Code-Plugins, wiederverwendbare GitHub-Workflow-Pakete, Home-Assistant-Integrationen, Vale-Style-Pakete, Python-Dienste —, alle auf GitHub gehostet, alle über dieselben Portfolio-Einstiegspunkte auffindbar. Diese Spec hebt diese Gestalt auf einen portfolioweiten Vertrag, damit neue Repositories und Refactorings strukturell identische READMEs erzeugen können, ohne Einzelfall-Verhandlung.

## Ziele
- Ein Leser (Mensch oder KI) kann Absicht, Install-Befehl und Portfolio-Kontext in jeder README innerhalb des ersten Bildschirms verorten
- Repositories unterschiedlicher Art (Plugin, Bibliothek, Dienst, Integration, CLI, Style-Paket) teilen sich ein erkennbares Abschnitts-Grundgerüst
- README-Metadaten (Badges, Links zur Doku, Portfolio-Peers) bleiben konsistent genug, damit automatisierte Audits Drift aufdecken können
- Konsumenten-relevante Informationen stehen vor internen/beitragsbezogenen Informationen
- Die Struktur komponiert sauber mit den Specs `project-structure`, `branching-model` und `prose-style`, statt sie zu duplizieren

## Nicht-Ziele
- Projektspezifischer Narrativ-Inhalt (Feature-Liste, Domänenerklärungen, Tutorials)
- Vollständige Dokumentationsseiten-Struktur — sie lebt unter `docs/` und wird durch die MkDocs-Konfiguration geregelt, nicht durch die README
- Architecture Decision Records, Designdokumente oder Changelogs — separate Artefakte
- Runbooks nur für Beitragende — diese gehören in `CLAUDE.md` oder `docs/`
- Badge-Katalog jenseits der CI-Status-Konvention (Shields für Lizenzen, Downloads usw. sind optional und hier nicht vorgeschrieben)
- Übersetzungen der README selbst — die README ist aus Portfolio-Konsistenzgründen nur auf Englisch; mehrsprachiger Inhalt lebt unter `docs/<lang>/`

## Anforderungen

### Datei und Sprache
- **MUSS [MUST]** als `README.md` im Repository-Wurzelverzeichnis liegen
- **MUSS [MUST]** in Englisch verfasst sein, unabhängig von der primären Arbeitssprache der Maintainer, damit portfolioweite Werkzeuge und externe Konsumentinnen eine konsistente Stimme sehen
- **MUSS [MUST]** den Regeln der `prose-style`-Spec folgen (Vale, Microsoft- + RedHat-Styles, `nolte/vale-style`-Vokabulare)

### Kopfblock (oberhalb der ersten `##`-Überschrift)
- **MUSS [MUST]** mit einer einzigen obersten Überschrift (`# <repo-name>`) beginnen, die exakt dem GitHub-Repository-Namen entspricht
- **MUSS [MUST]** CI-Status-Badges für jeden Workflow rendern, der Merges auf den Default-Branch gated, unmittelbar unter der `H1` platziert, ein Badge pro Zeile oder gruppiert in einer Zeile
- **MUSS [MUST]** einen ein- bis dreisätzigen Teaser unter den Badges enthalten, der angibt, *was dieses Repository ist* und *für wen es gedacht ist*, ohne Marketing-Sprache
- **SOLLTE [SHOULD]** primäre Eigennamen im Teaser (zum Beispiel „Claude Code", „Home Assistant", „Vale") bei erster Nennung auf ihre kanonische Upstream-Dokumentation verlinken
- **KANN [MAY]** Nicht-CI-Badges (Lizenz, neuestes Release, Paketindex) enthalten, wenn sie einer Konsumentin materiell helfen zu entscheiden, ob sie das Repository nutzt

### Pflicht-Abschnitte (in dieser Reihenfolge)
Die folgenden `##`-Überschriften **MÜSSEN [MUST]** in der angegebenen Reihenfolge erscheinen, sobald der zugrunde liegende Inhalt auf den Repository-Typ zutrifft. Ein Abschnitt **DARF NICHT [MUST NOT]** weggelassen werden, außer er hat für diesen Repository-Typ keinen sinnvollen Inhalt; er **DARF NICHT [MUST NOT]** aus stilistischen Gründen umsortiert werden.

1. **`## Purpose`** — **MUSS [MUST]** erscheinen. Erklärt das Problem, das das Repository löst, und wer die beabsichtigten Konsumentinnen sind. Zwei bis sechs Stichpunkte oder ein kurzer Absatz. Keine Feature-Aufzählung.
2. **`## Usage`** (oder `## Installation`, oder `## Getting started` — eines wählen und dabei bleiben) — **MUSS [MUST]** erscheinen. Zeigt den kürzesten Weg von null zu einer funktionierenden Konsumentenerfahrung. **MUSS [MUST]** mindestens einen ausführbaren Codeblock enthalten (Shell, Config-Snippet oder Import-Beispiel). **SOLLTE [SHOULD]** in Unter-Abschnitte (`###`) aufgeteilt werden, wenn das Repository mehrere Install- oder Konsum-Modi unterstützt (zum Beispiel Downstream-Install vs. lokale Entwicklung vs. Dogfooding).
3. **`## Structure`** — **SOLLTE [SHOULD]** für Repositories erscheinen, deren Layout für Erstleser nicht offensichtlich ist (Plugins mit `.claude-plugin/` + `skills/`, Multi-Komponenten-Monorepos, HA-Integrationen). Zeigt eine beschnittene `tree`-artige Auflistung mit einzeiligen Kommentaren pro Eintrag, kein vollständiger Dateibaum.
4. **`## Related repositories`** — **SOLLTE [SHOULD]** erscheinen, wenn das Repository auf andere Repositories im nolte-Portfolio angewiesen ist, diese erweitert oder von ihnen abhängig ist (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`, `nolte/claude-shared` und ähnliche). Jeder Eintrag ist ein Bullet-Link gefolgt von einer einzeiligen Beschreibung der Rolle des Peers.
5. **`## Status`** — **SOLLTE [SHOULD]** erscheinen. Ein kurzer Absatz, der den Lebenszyklus-Zustand beschreibt (frühes Stadium, stabil, nur Wartung, archiviert). Ergänzt die GitHub-Repository-Metadaten, dupliziert sie aber nicht.
6. **`## License`** — **MUSS [MUST]** für jedes Repository erscheinen, das eine `LICENSE`-Datei ausliefert. Verlinkt die `LICENSE`-Datei und nennt die SPDX-Kennung sowie den Rechteinhaber.

### Optionale Abschnitte
- **KANN [MAY]** einen `## Documentation`-Abschnitt enthalten, der auf die veröffentlichte MkDocs-Seite verweist, wenn `docs/` mehr als eine Handvoll Seiten umfasst; bei kleineren `docs/`-Ordnern wird stattdessen innerhalb von `## Usage` verlinkt
- **KANN [MAY]** einen `## Contributing`-Abschnitt enthalten, der auf `CONTRIBUTING.md` oder auf die portfolioweiten Beitragsregeln verweist; **DARF NICHT [MUST NOT]** Beitragsinhalte duplizieren, die in `CLAUDE.md` gehören
- **KANN [MAY]** einen `## Notes`- oder `## Caveats`-Unterabschnitt innerhalb von `## Usage` für nicht offensichtliche Stolpersteine enthalten, wenn ein eigener Top-Level-Abschnitt überdimensioniert wäre
- **KANN [MAY]** einen `## Security`-Abschnitt enthalten, wenn das Repository eine eigene Offenlegungs-Policy unterscheidbar vom Portfolio-Default hat

### Regel: Konsument zuerst
- Informationen, die eine Konsumentin braucht, um das Repository zu evaluieren oder zu installieren (`Purpose`, `Usage`), **MÜSSEN [MUST]** vor Informationen erscheinen, die Beitragende oder Maintainer brauchen (`Structure`, `Status`, `License`)
- Dogfooding- / Lokalentwicklungs-Anleitungen **MÜSSEN [MUST]** innerhalb von `## Usage` als Unterabschnitt leben (typische Überschrift: `### Work on the plugin itself (dogfooding)` oder `### Local development`), niemals als Top-Level-Abschnitt, der Konsumentenführung verdrängt

### Links, Badges und Referenzen
- **MUSS [MUST]** die `LICENSE`-Datei über einen relativen Link referenzieren (`[MIT](LICENSE)`), nicht über eine absolute GitHub-URL
- **MUSS [MUST]** absolute `https://github.com/<org>/<repo>`-URLs verwenden, wenn auf andere Portfolio-Repositories verlinkt wird, damit die README korrekt ist, wenn sie außerhalb von github.com gerendert wird (Paket-Registries, Plugin-Marktplätze, gedruckte PDFs)
- **MUSS [MUST]** jedes CI-Status-Badge auf die `Actions`-Workflow-Läufe desselben Repositories zeigen lassen; aus einem anderen Repository herüberkopierte Badges sind Drift
- **SOLLTE [SHOULD]** die Badge-Form `github.com/<org>/<repo>/actions/workflows/<file>.yml` verwenden, passend zu den bereits in der Referenz-README vorhandenen Badges

### Länge und Dichte
- **SOLLTE [SHOULD]** die gesamte README unter etwa 200 Zeilen halten; Überlauf gehört in `docs/` oder `CLAUDE.md`
- **SOLLTE [SHOULD]** kurze Absätze und Listen gegenüber Prosa-Blöcken bevorzugen; die README ist eine Nachschlage-Oberfläche, kein Handbuch

## Akzeptanzkriterien
- [ ] `README.md` existiert im Repository-Wurzelverzeichnis und ist auf Englisch verfasst
- [ ] Die Datei beginnt mit einer einzigen `# <repo-name>`-Überschrift, die exakt dem GitHub-Repository-Namen entspricht
- [ ] CI-Status-Badges für Merge-gatende Workflows erscheinen unter der H1
- [ ] Ein ein- bis dreisätziger Teaser folgt auf die Badges, mit primären Eigennamen bei erster Nennung verlinkt
- [ ] `## Purpose` ist vorhanden und enthält keine Feature-Aufzählung
- [ ] `## Usage` (oder das gewählte Äquivalent — `## Installation` oder `## Getting started`) ist vorhanden und enthält mindestens einen ausführbaren Codeblock
- [ ] Mehr-Modus-Konsum ist in `###`-Unterabschnitte unter `## Usage` aufgeteilt
- [ ] `## Structure` ist vorhanden, wenn das Repository ein nicht-triviales Layout hat, und zeigt einen beschnittenen Baum mit Kommentar pro Eintrag
- [ ] `## Related repositories` ist vorhanden, wenn Portfolio-Peers existieren, und jeder Eintrag ist ein Link plus einzeilige Beschreibung
- [ ] `## Status` ist vorhanden und beschreibt den Lebenszyklus-Zustand in einem kurzen Absatz
- [ ] `## License` verlinkt die `LICENSE`-Datei im Wurzelverzeichnis per relativem Link und nennt die SPDX-Kennung sowie den Rechteinhaber
- [ ] Pflicht-Abschnitte erscheinen in der Reihenfolge: `Purpose` → `Usage` → `Structure` → `Related repositories` → `Status` → `License`
- [ ] Konsumenten-orientierter Inhalt (`Purpose`, `Usage`) steht vor beitragsorientiertem Inhalt (`Structure`, `Status`, `License`)
- [ ] Dogfooding- oder Lokalentwicklungs-Anleitungen leben als `###`-Unterabschnitt von `## Usage`, nicht als Top-Level-Abschnitt
- [ ] Cross-Repository-Links verwenden absolute `https://github.com/<org>/<repo>`-URLs
- [ ] Die README besteht die Vale-Konfiguration, die die `prose-style`-Spec umsetzt
- [ ] Die Gesamt-READM-Länge liegt bei höchstens etwa 200 Zeilen, Codeblöcke ausgenommen

## Offene Fragen
- Sollte der Teaser ein hartes Zeichenlimit haben (zum Beispiel 280 Zeichen, damit er als Social-Card-Beschreibung passt), oder innerhalb der Satz-Anzahl-Richtlinie frei bleiben?
- Braucht es einen eigenen `## Features`-Abschnitt zwischen `## Purpose` und `## Usage` für Repositories, bei denen die Feature-Liste tragend ist (CLIs, Plugins mit vielen Befehlen), oder sollen Features innerhalb von `## Purpose` bleiben?
- Sollte ein maschinenlesbarer Front-Matter-Block (YAML) für die automatisierte Extraktion von Teaser, Homepage, Topics ergänzt werden — oder ist `.github/settings.yml` die kanonische Quelle für diese Metadaten?
- Sollte diese Spec einen eigenen Abschnitt für „Support / Contact" vorschreiben, oder genügt der GitHub-Issues-Link (implizit aus der Repository-URL)?
- Sollten Repositories, die ein Endanwender-Artefakt ausliefern (HACS-Integrationen, CLIs mit Binär-Releases), zusätzlich einen `## Installation`-Abschnitt verlangen, der von `## Usage` getrennt ist?
- Wie soll diese Spec mit Repositories umgehen, die absichtlich keine Konsumentinnen jenseits des Maintainers haben (persönliche Dotfiles, Experimente) — sind sie ausgenommen, oder folgen sie dem Grundgerüst trotzdem?
