# Claude-Skill- und -Agent-Katalog

Status: draft

## Kontext
Dieses Repository liefert wiederverwendbare Claude-Code-Skills und -Agents als Plugin `nolte-shared` aus, und die veröffentlichte MkDocs-Seite ist die Entdeckungs-Oberfläche sowohl für dieses Plugin als auch für jedes andere Claude-Code-Plugin, das daneben konsumiert wird. Die Specs `skill-management` und `agent-management` definieren die Datei-Struktur dieser Artefakte, aber Konsumenten brauchen einen durchstöberbaren Katalog, um zu sehen, was verfügbar ist, was jedes Artefakt tut und wann Claude es aufruft. Heute müsste ein solcher Katalog von Hand gepflegt werden und würde jedes Mal veralten, sobald ein Skill oder Agent hinzugefügt, umbenannt oder überarbeitet wird. Diese Spezifikation legt fest, wie die MkDocs-Dokumentation einen stets aktuellen Katalog von Skills und Agents präsentiert—generiert aus genau den Quelldateien, die diese Artefakte ohnehin regeln, und das über dieses Plugin sowie alle weiteren in den Doku-Build konfigurierten Plugins hinweg. Sie ist die Grundlage für das Generieren der entsprechenden Dokumentations-Objekte.

**Leser**: Implementoren des Katalog-Generators (der `scripts/docs/gen_catalog.py`-Pre-Build-Schritt), Autoren des `skill-agent-catalog-apply`-Skills (konsumenten-seitige Verdrahtung), Autoren der aufgaben-orientierten Einstiegs-Seiten. Skill- und Agent-Autoren selbst lesen stattdessen `skill-management` und `agent-management`—dort liegen die Per-Artefakt-Autoren-Regeln, die katalog-spezifische Schema-Details (Per-Sprache-Kurzbeschreibung, Use-Case-Metadaten) auf diese Spec zurückverweisen.

### Betriebsmodi
Der Katalog gilt für zwei Arten von Repositories:

- **Plugin-Modus**—das Repository ist selbst ein Claude-Code-Plugin (erkennbar an einer `.claude-plugin/plugin.json` im Wurzelverzeichnis). Die eigenen `skills/`- und `agents/`-Ordner des lokalen Plugins sind eine der Quell-Wurzeln des Katalogs; zusätzliche Plugin-Quell-Wurzeln können daneben konfiguriert werden.
- **Konsumenten-Modus**—das Repository ist selbst kein Claude-Code-Plugin. Es betreibt eine MkDocs-Seite, die einen oder mehrere *externe* Plugins kataloguiert (z. B. Plugins, von denen das Repository abhängt oder die es als Abhängigkeit führt). Es gibt keine lokale Plugin-Quell-Wurzel; alle Wurzeln sind extern.

Jede Anforderung dieser Spec gilt für beide Modi, sofern sie nicht ausdrücklich mit „im Plugin-Modus" oder „im Konsumenten-Modus" qualifiziert ist.

## Ziele
- Ein einziger durchstöberbarer Katalog in der MkDocs-Seite, der jeden Skill und jeden Agent dieses Plugins sowie weiterer in den Doku-Build konfigurierter Plugins auflistet
- Katalog-Inhalt wird aus den Quelldateien (Skill-`SKILL.md`, Agent-`<name>.md`) abgeleitet—keine Handkopie
- Jeder Katalog-Eintrag zeigt die kanonischen Metadaten des Artefakts (`name`, `description`, `distribution` bei Agents, `phase`, `tags` falls vorhanden) und verlinkt zurück auf die Quelle im Repository des jeweiligen Plugins
- Der Katalog wird im Rahmen des normalen Ablaufs `task docs` / `mkdocs build` regeneriert—ohne zusätzlichen Handgriff
- Leser sehen auf einen Blick, welches Plugin welches Artefakt liefert, welcher Lieferprozess-Phase es zuzuordnen ist, und können nach Tag stöbern
- Der Katalog integriert sich in das bestehende mehrsprachige MkDocs-Layout (`docs/en/`, `docs/de/`) und **DARF [MAY]** eine übersetzte Kurzbeschreibung pro Sprache mitführen, sodass nicht-englische Leser den Katalog scannen können, ohne die englischen Routing-Metadaten zu verlieren
- Jeder Katalog-Eintrag legt scanbare Use-Case-Metadaten offen—wann das Artefakt aufzurufen ist, wann nicht (mit benannten Alternativen), Peers zum Vergleich und kurze Prompt-/Outcome-Beispiele —, damit Leser den richtigen Skill oder Agent ohne kompletten Body-Lesedurchlauf wählen können
- Leser können den Katalog über aufgaben-orientierte Einstiegs-Seiten betreten („Ich will einen Release rausgeben", „Ich will eine Spec schreiben"), die ähnliche Artefakte disambiguieren—zusätzlich zu den phasen- und tag-orientierten Indizes
- Katalog-Einträge verlinken sich automatisch quer: strukturierte Peer-Referenzen und Inline-Code-Erwähnungen bekannter Skill- oder Agent-Namen werden zu echten Links zwischen Katalog-Seiten

## Nicht-Ziele
- Die Datei-Struktur von Skills oder Agents (gehört zu `skill-management` und `agent-management`)
- Portfolio-weite MkDocs-Theme-, Farb- oder Typografie-Entscheidungen
- Laufzeit-Discovery und -Laden von Skills und Agents (übernimmt Claude Code selbst)
- Eine separate, eigenständige Katalog-Seite—der Katalog lebt innerhalb der bestehenden `claude-shared`-Doku-Seite

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
- **MUSS [MUST]** den vollständigen `description`-Text wortgetreu übernehmen—der Generator erhält den Quelltext ohne Übersetzung, Zusammenfassung oder inhaltliche Ersetzung. Der in §Cross-Linking beschriebene Cross-Linking-Pass ist die einzige sanktionierte Ausnahme: er schreibt Inline-Code-Erwähnungen bekannter Artefakt-Namen in Markdown-Links um, ohne den umgebenden Text zu verändern
- **MUSS [MUST]**, wenn das Frontmatter des Artefakts `summary` deklariert, diese Kurzbeschreibung als kurzen Untertitel über der Routing-Description rendern (siehe „Per-Sprache-Kurzbeschreibung" unten für die sprachweise Auflösung und Fallback-Regeln)
- **MUSS [MUST]**, wenn das Frontmatter des Artefakts eines der Felder `use_when`, `dont_use_when`, `see_also` oder `examples` deklariert, den jeweiligen Abschnitt scanbar mit den lokalisierten Chrome-Labels rendern (siehe „Use-Case-Metadaten" unten)
- **MUSS [MUST]** für Agents das `distribution`-Feld (`plugin` oder `project`) anzeigen
- **MUSS [MUST]** jeden Eintrag mit dem Quell-Plugin kennzeichnen, aus dem er stammt (z. B. `nolte-shared`)
- **MUSS [MUST]** auf die Quelldatei im Repository des jeweiligen Plugins (Branch `main`) verlinken; die Basis-URL des Links wird pro Plugin-Quell-Wurzel konfiguriert (z. B. `https://github.com/nolte/claude-shared/blob/main/...`). Dieser Quelldatei-Link ist zugleich die Historien-Oberfläche des Katalogs: Der Katalog **DARF NICHT [MUST NOT]** Per-Artefakt-Versions- oder Changelog-Metadaten aufzeichnen, im Einklang mit `skill-management` und `agent-management`—der Link erreicht die vollständige Git-Historie der Datei (die Per-Artefakt-Änderungs-Aufzeichnung) und Versionierung erfolgt ausschließlich auf Plugin-Ebene (die einzige `.claude-plugin/plugin.json`-Manifest-Version, gepflegt gemäß `release-automation` §Version-bearing file alignment)
- **MUSS [MUST]** etwaige im Frontmatter deklarierte `tags` als sichtbare Tags auf der Eintrags-Seite rendern; `tags` sind gemäß `skill-management` / `agent-management` normalisiert (kleingeschriebenes ASCII-Kebab-Case, ≤30 Zeichen, ≤5 Einträge)
- **MUSS [MUST]** das `phase`-Feld des Artefakts (siehe „Phasen-Klassifikation" unten) als sichtbares Badge auf der Eintrags-Seite rendern, mit dem Phasen-Label aus dem lokalisierten Chrome
- **SOLLTE [SHOULD]** den Body von `SKILL.md` (bzw. das System-Prompt-Markdown des Agents) als Hauptinhalt der Seite rendern, damit die Autoren-Anweisungen für Leser sichtbar sind
- **KANN [MAY]** begleitende Assets auflisten, indem die Schwester-Dateien unter `skills/<name>/` angezeigt werden (z. B. `templates/`, `references/`, `examples/`); Agents sind einzelne, in sich geschlossene Dateien ohne Schwester-Ordner (gemäß `agent-management` §Struktur), daher gibt es agentenseitig keine Schwester-Assets zum Auflisten

### Phasen-Klassifikation
Jeder Skill und jeder Agent **MUSS [MUST]** deklarieren, welcher Phase des Liefer-Lebenszyklus er zugeordnet ist—über ein `phase:`-Frontmatter-Feld. Der Wert ist ein einzelner kleingeschriebener ASCII-Kebab-Case-Identifier aus dem geschlossenen Vokabular unten; kein anderer Wert ist zulässig. Autoren, die wirklich keine einzelne Phase festlegen können, verwenden `cross-cutting`.

- **MUSS [MUST]** ein Top-Level-Feld `phase:` im YAML-Frontmatter jedes Skills (`SKILL.md`) und jedes Agents (`<name>.md`) enthalten
- **MUSS [MUST]** `phase` auf genau einen dieser acht Identifier beschränken (das **Phasen-Vokabular**):
  - `vision`: Rahmt das Projekt (Mission-Autoring und -Revision)
  - `plan`: Macht aus Vision queue-fähige Arbeit (Audience, Roadmap, Sprint- und Feature-Planung)
  - `design`: Schreibt die Konventionen, Scaffolds und Spezifikationen, auf denen die Arbeit aufbaut
  - `build`: Tagesgeschäft eines aktiven Sprints
  - `review`: Bringt Änderungen über reviewte Pull Requests Richtung `develop`
  - `quality`: Audits, Scans, Lint-/Typecheck-/Test-Gates, Drift-Erkennung
  - `close-release`: Sprint-Abschluss, Release-Notes, Release-Publishing
  - `cross-cutting`: Echt phasenagnostische Fähigkeiten, die über mehrere Lebenszyklus-Phasen hinweg genutzt werden (z. B. Bildkonvertierung, generisches Projekt-Bootstrap)
- **MUSS [MUST]** `phase` als Identifier behandeln, nicht als Prosa: der Wert wird niemals zwischen Doku-Sprachen übersetzt, groß-/kleinbuchstabig verändert oder umgeschrieben
- **DARF NICHT [MUST NOT]** `phase` als Liste deklarieren; ein einzelnes Artefakt besetzt genau eine Phase. Artefakte, deren Verantwortung mehrere Phasen umspannt, werden entweder feiner gesplittet oder, wenn kein sinnvoller Split möglich ist, als `cross-cutting` klassifiziert
- **SOLLTE [SHOULD]** bei der Erstellung eines neuen Artefakts die **früheste Phase** im Lebenszyklus wählen, in der das Artefakt regulär aufgerufen wird; Review- und Quality-Artefakte, die selbst von einem Build-Phase-Skill aufgerufen werden, gehören zur primären Aufgabe des Artefakts, nicht zur Phase des Aufrufers

### Per-Sprache-Kurzbeschreibung
Das `description`-Feld ist die Routing-Quelle der Wahrheit, die Claude Code liest, um über den Aufruf eines Artefakts zu entscheiden—entsprechend ist es lang, englisch und trigger-dicht: schwer scanbar für menschliche Leser, schwer erfassbar für nicht-englische Leser. Der Katalog rendert deshalb zusätzlich eine optionale, sprachweise **Kurzbeschreibung** über der Routing-Description.

- **DARF [MAY]** ein Top-Level-Feld `summary:` im YAML-Frontmatter eines Skills (`SKILL.md`) oder Agents (`<name>.md`) deklarieren; der Wert ist ein String, ≤200 Zeichen, in Englisch (der kanonischen Metadaten-Sprache gemäß `skill-management` / `agent-management`)
- **DARF [MAY]** pro zusätzlich konfigurierter Doku-Sprache `<lang>` (gemäß `spec/project/mkdocs-structure/` §i18n und Parität) ein Schwester-Feld `summary_<lang>:` (z. B. `summary_de:`) mit der übersetzten Kurzbeschreibung deklarieren; der Wert ist ein String, ≤200 Zeichen
- **MUSS [MUST]** beim Rendern der Katalog-Seite für Doku-Sprache `<lang>` die angezeigte Kurzbeschreibung in dieser Reihenfolge auflösen: (1) `summary_<lang>` falls deklariert, (2) `summary` (englische Kanonische) falls deklariert, (3) der erste Satz von `description`, auf 200 Zeichen gekürzt, als Notlösung
- **MUSS [MUST]**, wenn eine Katalog-Seite in einer nicht-englischen Doku-Sprache auf die englische `summary` oder die `description`-Kürzung zurückfällt, ein sichtbares „Übersetzung ausstehend"-Badge mit lokalisiertem Chrome-Label rendern UND die Seite mit dem reservierten Auto-Tag `_translation-pending` taggen, damit der Tag-Index jeden nicht übersetzten Eintrag sichtbar macht
- **DARF NICHT [MUST NOT]** `_translation-pending` als autor-deklarierten Tag akzeptieren; der unterstrich-präfixierte Name ist für Generator-Auto-Tags reserviert und **DARF NICHT [MUST NOT]** im `tags`-Frontmatter eines Artefakts auftauchen (das Unterstrich-Präfix ist die sichtbare Markierung dafür, dass der Tag nicht von Hand kuratiert wurde)
- **MUSS [MUST]** `summary` und jedes `summary_<lang>` als reinen String validieren; der Doku-Build scheitert mit einer klaren Datei-und-Feld-Fehlermeldung, wenn der Wert kein String ist, nach Whitespace-Strip leer ist oder 200 Zeichen überschreitet

### Use-Case-Metadaten
Das `description`-Feld kollabiert jedes Routing-Signal—positive Trigger, negative Trigger, Alternativen, Beispiele—in einen einzigen dichten Prosa-Block, was es menschlichen Lesern erschwert zu scannen und es dem Katalog unmöglich macht, Peers automatisch zu verlinken. Dieser Abschnitt definiert vier optionale, strukturierte Frontmatter-Felder, die der Katalog als scanbare Abschnitte rendert und für automatisches Cross-Linking nutzt (siehe „Cross-Linking" unten).

- **DARF [MAY]** ein `use_when:`-Feld im YAML-Frontmatter eines Skills oder Agents deklarieren; der Wert ist eine YAML-Liste reiner Strings, jeder beschreibt ein konkretes Trigger-Szenario („du willst einen Release rausgeben", „du hast einen roten CI-Lauf auf `develop`"). Grenzen: ≤6 Einträge, jeder ≤120 Zeichen
- **DARF [MAY]** ein `dont_use_when:`-Feld deklarieren; der Wert ist eine YAML-Liste von Mappings, jedes mit den Schlüsseln `situation` (reiner String, ≤120 Zeichen) und `alternative` (ein einzelner Skill- oder Agent-`name`, auf den umgeleitet wird). Grenzen: ≤6 Einträge; jeder `alternative`-Wert **MUSS [MUST]** auf einen Skill oder Agent verweisen, der in einer konfigurierten Plugin-Quell-Wurzel auffindbar ist—sonst scheitert der Doku-Build
- **DARF [MAY]** ein `see_also:`-Feld deklarieren; der Wert ist eine YAML-Liste von Skill- oder Agent-Namen (jeweils ein reiner String, der einem auffindbaren `name` entspricht). Grenzen: ≤8 Einträge; jeder Eintrag **MUSS [MUST]** auf ein auffindbares Artefakt verweisen
- **DARF [MAY]** ein `examples:`-Feld deklarieren; der Wert ist eine YAML-Liste von Mappings, jedes mit den Schlüsseln `prompt` (reiner String, ≤200 Zeichen, illustriert die Art von Anfrage, die das Artefakt auslöst) und `outcome` (reiner String, ≤200 Zeichen, beschreibt die Antwort des Artefakts). Grenzen: ≤4 Einträge
- **MUSS [MUST]** jedes deklarierte Feld als eigenen scanbaren Abschnitt auf der Katalog-Seite rendern, mit lokalisierten Chrome-Labels (für Englisch: `Use when`, `Don't use when`, `See also`, `Examples`; für Deutsch: `Anwenden wenn`, `Nicht anwenden wenn`, `Siehe auch`, `Beispiele`)
- **MUSS [MUST]** alle vier Felder in dieser Spec als optional behandeln; die Autoren-Pflicht (wann Autoren sie **SOLLTEN [SHOULD]** deklarieren) liegt bei `skill-management` und `agent-management`. Diese Spec besitzt nur Schema und Validierung, daher bleiben die Felder hier dauerhaft optional; jede Entscheidung, das Autoren-`SHOULD` zu verschärfen (oder es für neue Artefakte innerhalb eines bekannten Peer-Clusters auf ein `MUST` zu kippen), gehört zu jenen Owner-Specs, nicht hierher
- **MUSS [MUST]** Form (Listen-Typ, Element-Typ, Schlüssel-Set, Zeichen-Grenzen) jedes Felds und die Auflösbarkeit von `dont_use_when[].alternative` und `see_also[]` gegen den entdeckten Katalog validieren; bei jeder Verletzung scheitert der Doku-Build mit einer klaren Fehlermeldung, die Datei, Feld und beanstandeten Wert benennt

### Generierungs-Mechanismus
- **MUSS [MUST]** Katalog-Seiten aus den Quelldateien erzeugen
- Das Repository **DARF [MUST] NICHT** generiertes Katalog-Markdown nach `docs/` committen; der Katalog wird bei jedem Build neu generiert. Die Doku-Deploy-Pipeline (der Workflow, der die GitHub-Pages-Ausgabe erzeugt) **MUSS [MUST]** den Katalog-Generator beim Deploy-Build aufrufen—`reusable-mkdocs.yaml` ruft `task docs` auf, wenn ein Taskfile mit einem `docs`-Target existiert, und fällt andernfalls auf `mkdocs build` mit dem als `mkdocs-gen-files`-Skript verdrahteten Generator zurück —, sodass kein Frische-Check für eingecheckte Artefakte nötig ist
- **MUSS [MUST]** die Katalog-Navigation über `mkdocs-literate-nav` verdrahten, deklariert in `mkdocs.yml`
- **MUSS [MUST]** einen Katalog-Generator aufrufen, der die Einzelseiten je Artefakt, die Abschnitts-Index-Seiten, die `SUMMARY.md`-Dateien je Abschnitt (für literate-nav) und den Tag-Index erzeugt. Der Generator **KANN [MAY]** ein `mkdocs-gen-files`-Plugin-Skript ODER ein eigenständiger Pre-Build-Schritt sein (z. B. ein Taskfile-Target, das vor `mkdocs build` aufgerufen wird), der physische Dateien unter `docs/<lang>/<section>/` schreibt. Die Pre-Build-Form ist die empfohlene Wahl, sobald das Repository zusätzlich `mkdocs-static-i18n` mit `docs_structure: folder` einsetzt, weil `mkdocs-static-i18n` 1.3.x Dateien verwirft, deren `abs_src_path` nicht unter `docs_dir` liegt—und damit jede von `mkdocs-gen-files` emittierte Seite stillschweigend fallen lässt
- **MUSS [MUST]** Plugin-Quell-Wurzeln aus einer konfigurierten Liste lesen—jeder Eintrag paart einen lokalen Quellpfad mit der öffentlichen Repository-URL, die für Quell-Links genutzt wird —, damit zusätzliche Plugins ohne Generator-Code-Änderung hinzugefügt werden können. Die konfigurierte Liste der Quell-Wurzeln liegt in `docs/catalog-sources.yml` (einer Schwester-YAML-Datei unter `docs_dir`), nicht inline in `mkdocs.yml`
- **MUSS [MUST]** die Katalog-Generierung über `task docs` verfügbar machen, damit lokale Builds und CI identische Ausgabe produzieren; in der Pre-Build-Form wird das verdrahtet, indem der Generator-Schritt als Taskfile-Abhängigkeit des Doku-Tasks deklariert wird
- **DARF NICHT [MUST NOT]** einen separaten manuellen „Katalog neu generieren"-Schritt außerhalb des normalen Doku-Builds verlangen
- **MUSS [MUST]** auf jeder generierten Katalog-Datei (Per-Artefakt-Seite, Per-Sektion-`index.md`, literate-nav-`SUMMARY.md`, Tag-Index, aufgaben-orientierte Einstiegs-Seite) die fünf Per-Page-Pflicht-Frontmatter-Schlüssel (`title`, `audience`, `content_mode`, `track`, `last_updated`) gemäß `spec/project/mkdocs-structure/` §Per-Page-Struktur schreiben. Der Generator **MUSS [MUST]** `track: developer-docs` für jede Katalog-Datei fest setzen (statt den Wert per-Artefakt aus dem Quell-Frontmatter zu lesen) gemäß `spec/project/docs-audience-tracks/` §Audience-zu-Spur-Mapping, damit die Katalog-Audience über die Quell-Plugins hinweg konsistent bleibt und Per-Page-`track`-Werte nicht driften
- **MUSS [MUST]** Quell-Frontmatter mit einem Standard-YAML-Parser (PyYAML oder Äquivalent) parsen, der verschachtelte Mappings und Listen von Mappings unterstützt; der ältere flach-only-Zeilenparser reicht nicht mehr aus, weil `dont_use_when` und `examples` (siehe „Use-Case-Metadaten") Listen von Mappings deklarieren

### Cross-Linking
Der Katalog ist ein Netz verwandter Artefakte, aber ein Leser kann diesem Netz nur folgen, wenn Peer-Referenzen echte Hyperlinks sind. Der Generator führt deshalb nach der Entdeckung aller Artefakte über alle Plugin-Quell-Wurzeln zwei Cross-Linking-Pässe aus.

- **MUSS [MUST]** pro Doku-Sprache einen Index aufbauen, der jeden entdeckten Artefakt-`name` auf seine Katalog-Seiten-URL abbildet (ein Eintrag pro Skill, einer pro Agent), bevor irgendeine Seite gerendert wird
- **MUSS [MUST]** jede strukturierte Peer-Referenz in einen Markdown-Link zur Katalog-Seite des Peers transformieren: jeder `dont_use_when[].alternative`-Wert und jeder `see_also[]`-Eintrag **MUSS [MUST]** als klickbarer Link rendern, niemals als reiner Text
- **MUSS [MUST]** Inline-Code-Erwähnungen bekannter Artefakt-Namen in der gerenderten `description`, `summary`, `summary_<lang>` und im Body in Markdown-Links auf die passende Katalog-Seite transformieren, **aber nur**, wenn der Inline-Code-Span (`` `name` ``) exakt einem Eintrag im Cross-Link-Index dieser Doku-Sprache entspricht
- **DARF NICHT [MUST NOT]** Klartext-Vorkommen von Artefakt-Namen außerhalb von Inline-Code-Spans transformieren, um False Positives bei generischen Wörtern zu vermeiden, die zufällig mit einem Artefakt-Namen kollidieren
- **MUSS [MUST]**, wenn eine Inline-Code-Erwähnung mit mehr als einem Artefakt übereinstimmt (z. B. ein Skill und ein Agent teilen dieselbe Kurzbezeichnung, oder zwei Plugins liefern Artefakte gleichen Namens), die Erwähnung unverlinkt belassen UND eine Generator-Warnung emittieren, die die Datei, die mehrdeutige Erwähnung und die kollidierenden Artefakte benennt
- **MUSS [MUST]**, wenn eine strukturierte Peer-Referenz (`dont_use_when[].alternative` oder `see_also[]`) auf kein entdecktes Artefakt auflöst, den Doku-Build scheitern lassen (gemäß „Use-Case-Metadaten" oben); Inline-Code-Erwähnungen, die nicht auflösen, bleiben als einfacher Inline-Code ohne Warnung
- **SOLLTE [SHOULD]** auf jeder Artefakt-Seite einen Abschnitt „Referenziert von" rendern, der jedes Artefakt auflistet, dessen `see_also` dieses Artefakt enthält, abgeleitet durch Invertierung des Cross-Link-Index in einem einzigen In-Memory-Durchlauf über die bereits geparsten Daten, unter einem lokalisierten Chrome-Label; das macht einseitige `see_also`-Asymmetrien sichtbar, die Autoren übersehen

### Navigation und Layout
- **MUSS [MUST]** den Katalog unter stabilen Top-Level-Abschnitten in der MkDocs-Navigation sichtbar machen—mindestens einem Abschnitt `Skills` und einem Abschnitt `Agents`
- **MUSS [MUST]** Einträge innerhalb jedes Abschnitts **zuerst nach Phase** gruppieren (in der kanonischen Phasen-Reihenfolge aus „Phasen-Klassifikation": `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`), danach nach Quell-Plugin innerhalb jeder Phase, sodass Leser auf einen Blick sehen, welche Artefakte zu welcher Lebenszyklus-Phase gehören
- **MUSS [MUST]** Katalog-Einträge deterministisch sortieren—alphabetisch nach `name` innerhalb jeder Plugin-Untergruppe jeder Phase—damit Diffs der gerenderten Seite stabil bleiben
- **MUSS [MUST]** eine Phasen-Überschrift weglassen, die keine Einträge hat; eine leere Phase wird nicht gerendert
- **MUSS [MUST]** je Abschnitt eine Index-Seite bereitstellen, die jeden Eintrag (Name + Beschreibung + Phase + Tags) mit Verweis auf die Detail-Seite zusammenfasst; die Index-Seite **MUSS [MUST]** prominent auf die aufgaben-orientierte Einstiegs-Seite des Abschnitts verlinken (siehe „Aufgaben-orientierte Einstiegs-Seiten" unten). Findbarkeit ist die Kern-Mission dieser Spec, und ein Katalog ohne Per-Sektion-Index-Seiten würde Leser zurück in den Navigations-Baum zwingen
- **MUSS [MUST]** einen Tag-Index bereitstellen, der jeden Tag über alle Einträge hinweg auflistet und auf die Artefakte verlinkt, die ihn deklarieren; der Tag-Index **MUSS [MUST]** außerdem jeden reservierten Auto-Tag, den der Generator emittiert (derzeit `_translation-pending`), auflisten, sobald mindestens ein Artefakt ihn trägt. Solange kein Artefakt des Katalogs irgendeinen Tag deklariert, **DARF [MAY]** die Seite entfallen; der Generator **DARF dann NICHT [MUST NOT]** von einer anderen Katalog-Seite einen ins Leere zeigenden Link stehen lassen

### Aufgaben-orientierte Einstiegs-Seiten
Die phasen- und tag-orientierten Indizes setzen einen Leser voraus, der das Katalog-Vokabular bereits spricht. Ein Leser, der nur weiß, was er tun will—„einen Release rausgeben", „eine Spec schreiben", „einen PR aufmachen" —, ist auf Raten angewiesen. Ein kleines Set hand-kuratierter, aufgaben-orientierter Einstiegs-Seiten schließt diese Lücke, indem es Artefakte nach Nutzer-Absicht statt nach Lebenszyklus-Phase gruppiert.

- **MUSS [MUST]** pro konfigurierter Doku-Sprache mindestens eine aufgaben-orientierte Einstiegs-Seite an einem stabilen Pfad unter jedem Abschnitt ausliefern (empfohlen: `docs/<lang>/skills/by-task.md` und `docs/<lang>/agents/by-task.md`, oder eine kombinierte `docs/<lang>/by-task.md`, von beiden Abschnitts-Indizes verlinkt)
- **MUSS [MUST]** Artefakte auf der Einstiegs-Seite nach Nutzer-Absichts-Rubriken gruppieren (jede Rubrik eine kurze H2 wie „Pull Request öffnen", „Release veröffentlichen", „Spec verfassen", „Etwas auditieren"); unter jeder Rubrik die relevanten Skills und Agents mit einem Ein-Satz-Disambiguierungshinweis listen, der dem Leser sagt, welchen er wählen soll, wenn mehrere gelistet sind
- **SOLLTE [SHOULD]** das Rubrik-Set zunächst klein halten (drei bis fünf Rubriken) und wachsen lassen, sobald Use-Case-Muster sichtbar werden; eine erschöpfende Einstiegs-Seite, die den Phasen-Index spiegelt, verfehlt ihren Zweck
- **DARF [MAY]** den Katalog-Generator eine Skelett-Einstiegs-Seite aus den `use_when`-Einträgen der Artefakte erzeugen lassen, solange noch keine Einstiegs-Seite existiert; das Skelett ist ein Startpunkt für einen menschlichen Autor und wird in Folgeläufen **NICHT** erneut überschrieben, sobald die Datei existiert
- **MUSS [MUST]** die Einstiegs-Seite wie eine reguläre MkDocs-Seite behandeln, die dem fünf-schlüssigen Per-Page-Frontmatter-Kontrakt (`title`, `audience`, `content_mode`, `track`, `last_updated`) unterliegt; vom Generator emittierte Skelette deklarieren `last_updated: generated`, hand-kuratierte Einstiegs-Seiten tragen ein ISO-8601-Datum

### Mehrsprachiges Verhalten
- **MUSS [MUST]** Artefakt-Identifier (`name`, `distribution`, `tags`, `phase`) so wie sie sind aus dem Quell-Frontmatter rendern; das sind technische Identifier und sie **DÜRFEN NICHT [MUST NOT]** zwischen Doku-Sprachen übersetzt, groß-/kleinbuchstabig verändert oder anderweitig umgeschrieben werden
- **MUSS [MUST]** die Quell-`description` und den Quell-Body ohne Übersetzung, Zusammenfassung oder inhaltliche Ersetzung rendern—diese Felder sind die Routing-Quelle der Wahrheit, die Claude liest, um das Artefakt zu dispatchen, und ihr Wortlaut bleibt unangetastet. Der in §Cross-Linking beschriebene Cross-Linking-Pass ist die einzige sanktionierte Ausnahme: er schreibt Inline-Code-Erwähnungen bekannter Artefakt-Namen in Markdown-Links um, ohne den umgebenden Text zu verändern
- **DARF [MAY]** pro Doku-Sprache eine übersetzte Kurzbeschreibung über der Routing-Description rendern, gespeist aus dem `summary_<lang>`-Frontmatter-Feld gemäß „Per-Sprache-Kurzbeschreibung" oben; das ist die einzige sanktionierte Übersetzungs-Oberfläche für Katalog-Inhalt
- **SOLLTE [SHOULD]** die rahmenden Elemente—Abschnittstitel, Intro-Absätze, Navigations-Labels, der Header des Tag-Index, Phasen-Labels, Use-Case-Abschnitts-Labels, „Übersetzung ausstehend"-Badge—in die jeweils konfigurierte Doku-Sprache (`docs/en/`, `docs/de/`) lokalisieren
- **DARF NICHT [MUST NOT]** `description`, Body, Identifier oder `tags` beim Generieren übersetzen; der einzige übersetzte Katalog-Inhalt sind die sprachweise Kurzbeschreibung und das Chrome

### Fehlerbehandlung
- **MUSS [MUST]** den Doku-Build scheitern lassen, wenn ein Skill oder Agent fehlende oder ungültige Frontmatter hat, anstatt einen kaputten Katalog zu produzieren
- **MUSS [MUST]** eine klare Fehlermeldung ausgeben, die die betroffene Quelldatei und die Plugin-Quell-Wurzel benennt, aus der sie stammt
- **MUSS [MUST]** den Doku-Build scheitern lassen, wenn `phase` eines Artefakts fehlt oder nicht im Phasen-Vokabular liegt, mit einer Fehlermeldung, die die Datei, die Plugin-Quell-Wurzel und den abgelehnten `phase`-Wert benennt
- **MUSS [MUST]** den Doku-Build scheitern lassen, wenn `summary` oder ein `summary_<lang>` seine Form-Vorgaben verletzt (kein String, nach Whitespace-Strip leer oder >200 Zeichen), unter Nennung der betroffenen Datei und des Felds
- **MUSS [MUST]** den Doku-Build scheitern lassen, wenn `use_when`, `dont_use_when`, `see_also` oder `examples` seinen Form-Kontrakt aus „Use-Case-Metadaten" verletzt (falscher Typ, falsches Schlüssel-Set bei Mapping-Elementen, über der Eintrags- oder Zeichen-Grenze), unter Nennung der betroffenen Datei, des Felds und des beanstandeten Werts
- **MUSS [MUST]** den Doku-Build scheitern lassen, wenn ein `dont_use_when[].alternative`- oder `see_also[]`-Wert auf einen Skill- oder Agent-Namen verweist, den keine konfigurierte Plugin-Quell-Wurzel liefert, unter Nennung der betroffenen Datei, des nicht aufgelösten Namens und des Felds, in dem er auftrat
- **MUSS [MUST]** eine nicht-fatale Generator-Warnung emittieren (Build läuft durch), wenn eine Inline-Code-Erwähnung in einer gerenderten `description`, `summary`, `summary_<lang>` oder im Body mit mehr als einem entdeckten Artefakt übereinstimmt und deshalb unverlinkt bleibt, unter Nennung der betroffenen Datei, der mehrdeutigen Erwähnung und der kollidierenden Artefakte

## Akzeptanzkriterien
- [ ] `task docs` erzeugt eine Doku-Seite, deren Navigation einen Abschnitt `Skills` mit einer Seite pro Skill über alle konfigurierten Plugin-Quell-Wurzeln hinweg enthält
- [ ] `task docs` erzeugt eine Doku-Seite, deren Navigation einen Abschnitt `Agents` mit einer Seite pro Agent über alle konfigurierten Plugin-Quell-Wurzeln hinweg enthält
- [ ] Jede Katalog-Seite zeigt `name`, `description`, das Quell-Plugin-Label und—bei Agents—`distribution`
- [ ] Wenn das Frontmatter eines Artefakts `tags` deklariert, erscheinen diese Tags auf der Katalog-Seite
- [ ] Jede Katalog-Seite enthält einen direkten Link auf die Quelldatei unter der Main-Branch-Repository-URL des jeweiligen Plugins
- [ ] Das Hinzufügen eines neuen Skills oder Agents in einer beliebigen konfigurierten Plugin-Quell-Wurzel erfordert keine manuelle Änderung an `docs/` oder `mkdocs.yml`, damit der Eintrag erscheint
- [ ] Das Entfernen eines Skills oder Agents entfernt beim nächsten `task docs`-Lauf die entsprechende Katalog-Seite
- [ ] `mkdocs.yml` deklariert `mkdocs-literate-nav`, und eine konfigurierte Liste der Plugin-Quell-Wurzeln (jeweils ein lokaler Pfad gepaart mit einer öffentlichen Repository-URL) wird vom Katalog-Generator gelesen
- [ ] Der Katalog-Generator ist entweder als `mkdocs-gen-files`-Skript in `mkdocs.yml` deklariert oder als eigenständiger Pre-Build-Schritt in `task docs` verdrahtet
- [ ] Im Plugin-Modus erscheint das lokale Plugin als eine der konfigurierten Plugin-Quell-Wurzeln
- [ ] Im Konsumenten-Modus ist mindestens eine externe Plugin-Quell-Wurzel konfiguriert
- [ ] Generiertes Katalog-Markdown ist **nicht** unter `docs/` eingecheckt; die Doku-Deploy-Pipeline generiert den Katalog bei jedem Build neu (via `task docs`, wenn ein Taskfile-`docs`-Target existiert, sonst `mkdocs build` mit dem als `mkdocs-gen-files`-Skript verdrahteten Generator)
- [ ] Ein Skill oder Agent mit ungültiger Frontmatter lässt `task docs` mit einer Fehlermeldung scheitern, die die Datei und ihre Plugin-Quell-Wurzel benennt
- [ ] Katalog-Einträge erscheinen zuerst nach Phase (in der kanonischen Phasen-Reihenfolge) gruppiert und dann alphabetisch nach `name` innerhalb jeder Plugin-Untergruppe jeder Phase
- [ ] Jeder Skill und Agent deklariert eine `phase` aus dem geschlossenen Acht-Werte-Vokabular (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); eine fehlende oder nicht-vokabel-konforme `phase` lässt `task docs` scheitern
- [ ] Jede Katalog-Seite zeigt die `phase` des Artefakts als sichtbares Badge mit dem lokalisierten Chrome-Label
- [ ] Die Index-Seiten von Skills und Agents rendern eine Überschrift pro Phase (Phasen ohne Einträge werden weggelassen) über jeder Plugin-Untergruppe
- [ ] Eine Tag-Index-Seite existiert und verlinkt auf jedes Artefakt, das den Tag deklariert
- [ ] Jede generierte Katalog-Datei (Per-Artefakt-Seite, Per-Sektion-`index.md`, literate-nav-`SUMMARY.md`, Tag-Index, aufgaben-orientierte Einstiegs-Seite) deklariert das fünfschlüssige Per-Page-Frontmatter-Set (`title`, `audience`, `content_mode`, `track`, `last_updated`) gemäß `spec/project/mkdocs-structure/` §Per-Page-Struktur; der `track`-Wert ist generator-fixiert auf `developer-docs` gemäß `spec/project/docs-audience-tracks/`
- [ ] Jede Abschnitts-Index-Seite verlinkt prominent auf ihre aufgaben-orientierte Einstiegs-Seite (`by-task.md`)
- [ ] Pro konfigurierter Doku-Sprache existiert mindestens eine aufgaben-orientierte Einstiegs-Seite, die Artefakte nach Nutzer-Absicht mit Ein-Satz-Disambiguierungen gruppiert
- [ ] Wenn ein Artefakt `summary` deklariert, rendert die Katalog-Seite die Kurzbeschreibung als Untertitel über der Routing-`description`; wenn `summary_<lang>` für eine Doku-Sprache deklariert ist, rendert die `<lang>`-Seite stattdessen die übersetzte Kurzbeschreibung
- [ ] Wenn der Katalog in einer nicht-englischen Doku-Sprache auf die englische `summary` oder eine `description`-Kürzung zurückfällt, zeigt die Seite ein lokalisiertes „Übersetzung ausstehend"-Badge, und der Auto-Tag `_translation-pending` erscheint im Tag-Index
- [ ] Der reservierte Auto-Tag `_translation-pending` wird niemals in einem Quell-Frontmatter-`tags` akzeptiert; eine entsprechende Deklaration lässt den Doku-Build scheitern
- [ ] Wenn ein Artefakt `use_when`, `dont_use_when`, `see_also` oder `examples` deklariert, rendert die Katalog-Seite jedes deklarierte Feld als scanbaren Abschnitt mit einem lokalisierten Chrome-Label
- [ ] `dont_use_when[].alternative`- und `see_also[]`-Werte rendern als Markdown-Links auf die Katalog-Seite des referenzierten Artefakts; ein nicht aufgelöster Name lässt den Doku-Build scheitern
- [ ] Inline-Code-Erwähnungen (`` `name` ``) bekannter Artefakt-Namen in `description`, `summary`, `summary_<lang>` und Body rendern als Markdown-Links auf die passende Katalog-Seite; mehrdeutige Erwähnungen bleiben unverlinkt und erzeugen eine Generator-Warnung, die Datei und kollidierende Artefakte benennt
- [ ] Jede Artefakt-Seite rendert einen lokalisierten Abschnitt „Referenziert von", der jedes Artefakt auflistet, dessen `see_also` dieses Artefakt enthält, abgeleitet durch Invertierung des Cross-Link-Index
- [ ] Eine `summary` oder ein `summary_<lang>` mit >200 Zeichen oder leer nach Whitespace-Strip lässt den Doku-Build mit einer Datei-und-Feld-Fehlermeldung scheitern
- [ ] Ein fehlerhaftes `use_when`, `dont_use_when`, `see_also` oder `examples` (falscher Typ, falsches Schlüssel-Set, über der Grenze) lässt den Doku-Build mit einer Datei-und-Feld-Fehlermeldung scheitern
- [ ] Der Katalog-Generator parst Quell-Frontmatter mit einem Standard-YAML-Parser, der verschachtelte Mappings unterstützt (der ältere flache-only-Zeilenparser wird abgelehnt)
- [ ] Jede aufgaben-orientierte Einstiegs-Seite (Generator-emittiertes Skelett oder hand-kuratiert) deklariert das fünfschlüssige Per-Page-Frontmatter-Set; vom Generator emittierte Skelette tragen `last_updated: generated`, hand-kuratierte Einstiegs-Seiten tragen ein ISO-8601-Datum
- [ ] Wenn der Katalog-Generator eine Skelett-Einstiegs-Seite aus den `use_when`-Einträgen der Artefakte emittiert, überschreibt ein nachfolgender `task docs`-Lauf die Datei **nicht**, falls sie bereits existiert; das Skelett ist ein einmaliger Startpunkt
- [ ] Klartext-Vorkommen von Artefakt-Namen, die **nicht** in Inline-Code-Spans (Backticks) eingeschlossen sind, werden auf keiner gerenderten Katalog-Seite in Markdown-Links transformiert—nur Inline-Code-Erwähnungen sind für den Cross-Linking-Rewrite zulässig

## Offene Fragen
- §Generierungs-Mechanismus von „Pre-Build erforderlich unter Folder-Strategy-i18n" auf „beide Formen funktionieren" lockern, sobald ein `mkdocs-static-i18n`-Release (oberhalb des `>=1.2`-Pins in `docs/requirements.txt`; aktuell 1.3.1) eine `reconfigure.py` ausliefert, die Dateien mit `abs_src_path` außerhalb von `docs_dir` nicht mehr verwirft—das heißt, sie lässt `mkdocs-gen-files`-Ausgabe unter `docs_structure: folder` nicht mehr fallen. Verfolgt über <https://github.com/ultrabug/mkdocs-static-i18n> (Changelog und die `reconfigure.py`-gen-files-Interaktion). Verifizieren, indem der Katalog-Generator als `mkdocs-gen-files`-Skript verdrahtet wird und bestätigt wird, dass generierte Seiten unter Folder-Strategy-i18n in die gebaute Seite gelangen.
