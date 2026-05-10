# Claude-Skill- und -Agent-Katalog

Status: draft

## Kontext
Dieses Repository liefert wiederverwendbare Claude-Code-Skills und -Agents als Plugin `nolte-shared` aus, und die veröffentlichte MkDocs-Seite ist die Entdeckungs-Oberfläche sowohl für dieses Plugin als auch für jedes andere Claude-Code-Plugin, das daneben konsumiert wird. Die Specs `skill-management` und `agent-management` definieren die Datei-Struktur dieser Artefakte, aber Konsumenten brauchen einen durchstöberbaren Katalog, um zu sehen, was verfügbar ist, was jedes Artefakt tut und wann Claude es aufruft. Heute müsste ein solcher Katalog von Hand gepflegt werden und würde jedes Mal veralten, sobald ein Skill oder Agent hinzugefügt, umbenannt oder überarbeitet wird. Diese Spezifikation legt fest, wie die MkDocs-Dokumentation einen stets aktuellen Katalog von Skills und Agents präsentiert — generiert aus genau den Quelldateien, die diese Artefakte ohnehin regeln, und das über dieses Plugin sowie alle weiteren in den Doku-Build konfigurierten Plugins hinweg. Sie ist die Grundlage für das Generieren der entsprechenden Dokumentations-Objekte.

### Betriebsmodi
Der Katalog gilt für zwei Arten von Repositories:

- **Plugin-Modus** — das Repository ist selbst ein Claude-Code-Plugin (erkennbar an einer `.claude-plugin/plugin.json` im Wurzelverzeichnis). Die eigenen `skills/`- und `agents/`-Ordner des lokalen Plugins sind eine der Quell-Wurzeln des Katalogs; zusätzliche Plugin-Quell-Wurzeln können daneben konfiguriert werden.
- **Konsumenten-Modus** — das Repository ist selbst kein Claude-Code-Plugin. Es betreibt eine MkDocs-Seite, die einen oder mehrere *externe* Plugins kataloguiert (z. B. Plugins, von denen das Repository abhängt oder die es als Abhängigkeit führt). Es gibt keine lokale Plugin-Quell-Wurzel; alle Wurzeln sind extern.

Jede Anforderung dieser Spec gilt für beide Modi, sofern sie nicht ausdrücklich mit „im Plugin-Modus" oder „im Konsumenten-Modus" qualifiziert ist.

## Ziele
- Ein einziger durchstöberbarer Katalog in der MkDocs-Seite, der jeden Skill und jeden Agent dieses Plugins sowie weiterer in den Doku-Build konfigurierter Plugins auflistet
- Katalog-Inhalt wird aus den Quelldateien (Skill-`SKILL.md`, Agent-`<name>.md`) abgeleitet — keine Handkopie
- Jeder Katalog-Eintrag zeigt die kanonischen Metadaten des Artefakts (`name`, `description`, `distribution` bei Agents, `tags` falls vorhanden) und verlinkt zurück auf die Quelle im Repository des jeweiligen Plugins
- Der Katalog wird im Rahmen des normalen Ablaufs `task docs` / `mkdocs build` regeneriert — ohne zusätzlichen Handgriff
- Leser sehen auf einen Blick, welches Plugin welches Artefakt liefert, und können nach Tag stöbern
- Der Katalog integriert sich in das bestehende mehrsprachige MkDocs-Layout (`docs/en/`, `docs/de/`), ohne Artefakt-Metadaten übersetzen zu müssen

## Nicht-Ziele
- Die Datei-Struktur von Skills oder Agents (gehört zu `skill-management` und `agent-management`)
- Portfolio-weite MkDocs-Theme-, Farb- oder Typografie-Entscheidungen
- Laufzeit-Discovery und -Laden von Skills und Agents (übernimmt Claude Code selbst)
- Eine separate, eigenständige Katalog-Seite — der Katalog lebt innerhalb der bestehenden `claude-shared`-Doku-Seite

## Anforderungen

### Umfang des Katalogs
- **MUSS [MUST]** pro Skill-Ordner mit gültiger `SKILL.md` unter jeder konfigurierten Plugin-Quell-Wurzel genau einen Katalog-Eintrag enthalten
- **MUSS [MUST]** pro Agent-Datei (`<name>.md`) unter jeder konfigurierten Plugin-Quell-Wurzel genau einen Katalog-Eintrag enthalten
- **MUSS [MUST]** Skills und Agents aus jeder für den Katalog-Generator konfigurierten Plugin-Quell-Wurzel entdecken
- **MUSS [MUST]** im Plugin-Modus das lokale Plugin (mit eigenen `skills/`- und `agents/`-Ordnern) als eine der konfigurierten Quell-Wurzeln enthalten
- **MUSS [MUST]** im Konsumenten-Modus mindestens eine externe Plugin-Quell-Wurzel konfigurieren; der Katalog ist ohne deklarierte Quellen nicht sinnvoll
- **DARF NICHT [MUST NOT]** Skills oder Agents enthalten, die nicht der `skill-management`- / `agent-management`-Struktur entsprechen; fehlerhafte Einträge **MÜSSEN [MUST]** den Doku-Build scheitern lassen, statt stillschweigend weggelassen zu werden

### Inhalt eines Katalog-Eintrags
- **MUSS [MUST]** das Frontmatter-Feld `name` als Seitentitel darstellen
- **MUSS [MUST]** den vollständigen `description`-Text wortgetreu übernehmen
- **MUSS [MUST]** für Agents das `distribution`-Feld (`plugin` oder `project`) anzeigen
- **MUSS [MUST]** jeden Eintrag mit dem Quell-Plugin kennzeichnen, aus dem er stammt (z. B. `nolte-shared`)
- **MUSS [MUST]** auf die Quelldatei im Repository des jeweiligen Plugins (Branch `main`) verlinken; die Basis-URL des Links wird pro Plugin-Quell-Wurzel konfiguriert (z. B. `https://github.com/nolte/claude-shared/blob/main/...`)
- **MUSS [MUST]** etwaige im Frontmatter deklarierte `tags` als sichtbare Tags auf der Eintrags-Seite rendern; `tags` sind gemäß `skill-management` / `agent-management` normalisiert (kleingeschriebenes ASCII-Kebab-Case, ≤30 Zeichen, ≤5 Einträge)
- **SOLLTE [SHOULD]** den Body von `SKILL.md` (bzw. das System-Prompt-Markdown des Agents) als Hauptinhalt der Seite rendern, damit die Autoren-Anweisungen für Leser sichtbar sind
- **KANN [MAY]** begleitende Assets auflisten, indem die Schwester-Dateien unter `skills/<name>/` bzw. `agents/<name>/` angezeigt werden (z. B. `templates/`, `references/`, `examples/`)

### Generierungs-Mechanismus
- **MUSS [MUST]** Katalog-Seiten aus den Quelldateien erzeugen; **DARF NICHT [MUST NOT]** generiertes Katalog-Markdown nach `docs/` committen
- **MUSS [MUST]** die Katalog-Navigation über `mkdocs-literate-nav` verdrahten, deklariert in `mkdocs.yml`
- **MUSS [MUST]** einen Katalog-Generator aufrufen, der die Einzelseiten je Artefakt, die Abschnitts-Index-Seiten, die `SUMMARY.md`-Dateien je Abschnitt (für literate-nav) und den Tag-Index erzeugt. Der Generator **KANN [MAY]** ein `mkdocs-gen-files`-Plugin-Skript ODER ein eigenständiger Pre-Build-Schritt sein (z. B. ein Taskfile-Target, das vor `mkdocs build` aufgerufen wird), der physische Dateien unter `docs/<lang>/<section>/` schreibt. Die Pre-Build-Form ist die empfohlene Wahl, sobald das Repository zusätzlich `mkdocs-static-i18n` mit `docs_structure: folder` einsetzt, weil `mkdocs-static-i18n` 1.3.x Dateien verwirft, deren `abs_src_path` nicht unter `docs_dir` liegt — und damit jede von `mkdocs-gen-files` emittierte Seite stillschweigend fallen lässt
- **MUSS [MUST]** Plugin-Quell-Wurzeln aus einer konfigurierten Liste lesen — jeder Eintrag paart einen lokalen Quellpfad mit der öffentlichen Repository-URL, die für Quell-Links genutzt wird —, damit zusätzliche Plugins ohne Generator-Code-Änderung hinzugefügt werden können
- **MUSS [MUST]** die Katalog-Generierung über `task docs` verfügbar machen, damit lokale Builds und CI identische Ausgabe produzieren; in der Pre-Build-Form wird das verdrahtet, indem der Generator-Schritt als Taskfile-Abhängigkeit des Doku-Tasks deklariert wird
- **DARF NICHT [MUST NOT]** einen separaten manuellen „Katalog neu generieren"-Schritt außerhalb des normalen Doku-Builds verlangen

### Navigation und Layout
- **MUSS [MUST]** den Katalog unter stabilen Top-Level-Abschnitten in der MkDocs-Navigation sichtbar machen — mindestens einem Abschnitt `Skills` und einem Abschnitt `Agents`
- **MUSS [MUST]** Einträge innerhalb jedes Abschnitts nach Quell-Plugin gruppieren, sodass Leser auf einen Blick sehen, welches Plugin welches Artefakt liefert
- **MUSS [MUST]** Katalog-Einträge deterministisch sortieren — alphabetisch nach `name` innerhalb jeder Plugin-Gruppe — damit Diffs der gerenderten Seite stabil bleiben
- **SOLLTE [SHOULD]** je Abschnitt eine Index-Seite bereitstellen, die jeden Eintrag (Name + Beschreibung + Tags) mit Verweis auf die Detail-Seite zusammenfasst
- **SOLLTE [SHOULD]** einen Tag-Index bereitstellen, der jeden Tag über alle Einträge hinweg auflistet und auf die Artefakte verlinkt, die ihn deklarieren

### Mehrsprachiges Verhalten
- **MUSS [MUST]** Artefakt-Metadaten (`name`, `description`, `distribution`, `tags`, Body) so wie sie sind aus dem Quell-Frontmatter rendern; für Artefakte aus diesem Repository ist das laut `skill-management`- / `agent-management`-Regel Englisch, externe Plugins werden unabhängig von ihren eigenen Sprachkonventionen wortgetreu wiedergegeben
- **MUSS [MUST]** `tags` als Identifier behandeln, nicht als Prosa: sie werden in ihrer kanonischen kleingeschriebenen ASCII-Kebab-Case-Form gerendert (gemäß `skill-management` / `agent-management`) und niemals zwischen Doku-Sprachen übersetzt, groß-/kleinbuchstabig verändert oder anderweitig umgeschrieben
- **SOLLTE [SHOULD]** nur die rahmenden Elemente — Abschnittstitel, Intro-Absätze, Navigations-Labels, der Header des Tag-Index — in die jeweils konfigurierte Doku-Sprache (`docs/en/`, `docs/de/`) lokalisieren
- **DARF NICHT [MUST NOT]** Artefakt-Metadaten oder -Body beim Generieren übersetzen; Übersetzungen dieser Felder sind außerhalb des Scope

### Fehlerbehandlung
- **MUSS [MUST]** den Doku-Build scheitern lassen, wenn ein Skill oder Agent fehlende oder ungültige Frontmatter hat, anstatt einen kaputten Katalog zu produzieren
- **MUSS [MUST]** eine klare Fehlermeldung ausgeben, die die betroffene Quelldatei und die Plugin-Quell-Wurzel benennt, aus der sie stammt

## Akzeptanzkriterien
- [ ] `task docs` erzeugt eine Doku-Seite, deren Navigation einen Abschnitt `Skills` mit einer Seite pro Skill über alle konfigurierten Plugin-Quell-Wurzeln hinweg enthält
- [ ] `task docs` erzeugt eine Doku-Seite, deren Navigation einen Abschnitt `Agents` mit einer Seite pro Agent über alle konfigurierten Plugin-Quell-Wurzeln hinweg enthält
- [ ] Jede Katalog-Seite zeigt `name`, `description`, das Quell-Plugin-Label und — bei Agents — `distribution`
- [ ] Wenn das Frontmatter eines Artefakts `tags` deklariert, erscheinen diese Tags auf der Katalog-Seite
- [ ] Jede Katalog-Seite enthält einen direkten Link auf die Quelldatei unter der Main-Branch-Repository-URL des jeweiligen Plugins
- [ ] Das Hinzufügen eines neuen Skills oder Agents in einer beliebigen konfigurierten Plugin-Quell-Wurzel erfordert keine manuelle Änderung an `docs/` oder `mkdocs.yml`, damit der Eintrag erscheint
- [ ] Das Entfernen eines Skills oder Agents entfernt beim nächsten `task docs`-Lauf die entsprechende Katalog-Seite
- [ ] `mkdocs.yml` deklariert `mkdocs-literate-nav`, und eine konfigurierte Liste der Plugin-Quell-Wurzeln (jeweils ein lokaler Pfad gepaart mit einer öffentlichen Repository-URL) wird vom Katalog-Generator gelesen
- [ ] Der Katalog-Generator ist entweder als `mkdocs-gen-files`-Skript in `mkdocs.yml` deklariert oder als eigenständiger Pre-Build-Schritt in `task docs` verdrahtet
- [ ] Im Plugin-Modus erscheint das lokale Plugin als eine der konfigurierten Plugin-Quell-Wurzeln
- [ ] Im Konsumenten-Modus ist mindestens eine externe Plugin-Quell-Wurzel konfiguriert
- [ ] Kein generiertes Katalog-Markdown ist unter `docs/` eingecheckt
- [ ] Ein Skill oder Agent mit ungültiger Frontmatter lässt `task docs` mit einer Fehlermeldung scheitern, die die Datei und ihre Plugin-Quell-Wurzel benennt
- [ ] Katalog-Einträge erscheinen innerhalb jeder Plugin-Gruppe jedes Abschnitts in deterministischer, alphabetischer Reihenfolge nach `name`
- [ ] Eine Tag-Index-Seite existiert und verlinkt auf jedes Artefakt, das den Tag deklariert

## Offene Fragen
- Sollen Versionen von Skills und Agents (Historie, Changelogs) im Katalog erscheinen oder reicht die Git-Historie?
- Falls Übersetzungen eines Artefakt-Bodys gewünscht sein sollten: wo leben sie — in einer parallelen `skills/<name>/docs/<lang>.md` oder als separat gepflegte Seiten unter `docs/<lang>/`?
- Wie genau werden Plugin-Quell-Wurzeln konfiguriert — inline in `mkdocs.yml` unter der `gen-files`-Plugin-Konfiguration oder in einer Schwester-YAML-Datei, die von dort referenziert wird?
- Wie sollte sich diese Spec weiterentwickeln, sobald `mkdocs-static-i18n` upstream Dateien unterstützt, die von `mkdocs-gen-files` emittiert werden? Stand Mai 2026 (`mkdocs-static-i18n` 1.3.1) werden solche Dateien in `reconfigure.py` stillschweigend verworfen, weil ihr `abs_src_path` außerhalb von `docs_dir` liegt — was die Pre-Build-Form erzwingt, sobald die Folder-Strategy-i18n genutzt wird.
