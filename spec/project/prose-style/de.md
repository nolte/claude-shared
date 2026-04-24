# Textstil

Status: draft

## Kontext
Dokumentation, Spezifikationen, READMEs, Release-Notes und sonstiges menschenlesbares Markdown in diesem Portfolio sollen sich gleich lesen – unabhängig davon, wer oder was den Text geschrieben hat. [Vale](https://vale.sh) ist der gemeinsam genutzte Prose-Linter, der diese Konsistenz durchsetzt. Die kanonische Quelle ist das portfolio-eigene Style-Paket in [`nolte/vale-style`](https://github.com/nolte/vale-style); die `.vale.ini` eines Repositories kombiniert die Upstream-Style-Pakete von Microsoft und RedHat mit einem gepinnten Release dieses Pakets, das zugleich das gemeinsame Fachvokabular trägt. Wird ein neuer Begriff, Produktname oder eine neue Formulierungs-Konvention eingeführt, gehört diese nach `nolte/vale-style` und nicht in einen repository-lokalen Sonderweg – damit künftige Texterzeugung, ob durch Menschen oder durch eine KI-Assistenz, Ergebnisse liefert, die das gemeinsame Regelwerk bereits einhalten.

## Ziele
- Menschenlesbarer Text in jedem Repository folgt denselben lint-geprüften Stilregeln
- Das gemeinsame Fachvokabular hat einen einzigen kanonischen Ort in `nolte/vale-style`
- Neu eingeführte Begriffe sind portfolio-weit prüfbar und wiederverwendbar, statt pro Repository zu driften
- KI-gestützte Texterzeugung erzeugt Output, der die gemeinsame Vale-Konfiguration bereits besteht

## Nicht-Ziele
- Code-Kommentare, Docstrings und API-Referenztext (werden durch code-seitiges Tooling geprüft, nicht durch Vale)
- Visuelle Gestaltung des gerenderten Outputs (Themes, CSS, Typografie)
- Übersetzungsqualität jenseits von Vokabular-Konsistenz
- Sprachwahl zwischen Englisch und Deutsch (wird durch die projektspezifische Dokumentations-Policy geregelt)

## Anforderungen

### Gemeinsame Vale-Konfiguration
- **MUSS [MUST]** Vale in jedem Repository, das menschenlesbares Markdown enthält, über eine `.vale.ini` konfigurieren, die die Microsoft- und RedHat-Pakete mit einem gepinnten Release von [`nolte/vale-style`](https://github.com/nolte/vale-style) als kanonischer Portfolio-Style-Quelle kombiniert
- **MUSS [MUST]** das `nolte/vale-style`-Paket auf eine explizite Release-Version pinnen (nicht `develop`/`main`), damit lokale Läufe und CI-Läufe reproduzierbar bleiben
- **MUSS [MUST]** `StylesPath` und `MinAlertLevel` konsistent setzen, damit lokale Läufe und CI-Läufe dieselben Alerts produzieren
- **SOLLTE [SHOULD]** die `IgnoredScopes`-Liste aus der kanonischen Konfiguration spiegeln (mindestens `code`, `tt`, `em`), damit Code-Fences keine Prose-Regeln auslösen
- **SOLLTE [SHOULD]** Vale auf jeden im Repository vorhandenen Markdown-Bereich anwenden, einschließlich sprachspezifischer Dokumentations-Ordner (`docs/en/`, `docs/de/`, …)

### Vale ausführen
- **MUSS [MUST]** `vale sync` vor dem ersten Lint-Lauf ausführen, damit die gepinnten Pakete geholt werden
- **MUSS [MUST]** ein Taskfile-Ziel bereitstellen (zum Beispiel `task docs:lint` oder `task lint:prose`), das Vale über alles menschenlesbare Markdown laufen lässt
- **MUSS [MUST]** dieses Taskfile-Ziel in die CI einbinden, damit Pull Requests scheitern, wenn Vale auf `error`-Stufe alarmiert
- **MUSS [MUST]** einen pre-commit-Hook registrieren, der Vale lokal auf geänderte Markdown-Dateien ausführt und dasselbe Taskfile-Ziel wie die CI aufruft

### Texterzeugung
- **MUSS [MUST]** die aktive Vale-Konfiguration (Microsoft + RedHat + `nolte/vale-style`) als verbindliches Regelwerk behandeln, wenn Prosa erzeugt oder umgeschrieben wird – unabhängig davon, ob der Autor ein Mensch oder eine KI-Assistenz ist
- **MUSS [MUST]** neues oder substanziell umgeschriebenes Markdown auf dem konfigurierten `MinAlertLevel` gegen Vale prüfen, bevor die Änderung als fertige Arbeit behandelt wird
- **SOLLTE [SHOULD]** Formulierungen bevorzugen, die das gemeinsame Vokabular bereits akzeptiert, und Terminologie aus benachbarten Specs und Docs wiederverwenden, wenn sie passt, statt neue Begriffe zu prägen
- **MUSS NICHT [MUST NOT]** Vale-Alerts durch dateilokale Ignore-Kommentare stummschalten, wenn die eigentliche Lösung ein Vokabular- oder Stil-Update in `nolte/vale-style` wäre

### Neue Begriffe und Formulierungen
- **MUSS [MUST]** neu eingeführte Fachbegriffe, Produktnamen oder projektspezifischen Jargon im gemeinsamen Vokabular in [`nolte/vale-style`](https://github.com/nolte/vale-style) ablegen, konkret unter `src/styles/config/vocabularies/<vocab>/accept.txt`, und nicht in einem repository-lokalen Override
- **MUSS [MUST]** Einträge einem bestehenden Vokabular-Thema zuordnen (zum Beispiel `technical`, `esphome`), wenn eines passt, und nur dann ein neues Vokabular vorschlagen, wenn keines der bestehenden anwendbar ist
- **SOLLTE [SHOULD]** einen Pull Request gegen `nolte/vale-style` eröffnen, mit einer einzeiligen Begründung je neuem Eintrag, damit Ergänzungen prüfbar sind
- **KANN [MAY]** einen Begriff nur übergangsweise in einem repository-lokalen Vokabular halten, solange der Upstream-PR offen ist; nach Release der Upstream-Änderung **MUSS [MUST]** der lokale Eintrag entfernt und das gepinnte `nolte/vale-style`-Release **MUSS [MUST]** angehoben werden

### Pull-Request-Beschreibungen und Release-Notes
- **MUSS [MUST]** dasselbe gemeinsame Vale-Regelwerk auf Pull-Request-Beschreibungen und GitHub-Release-Notes anwenden (vom release-drafter entworfen, vor der Veröffentlichung bearbeitet), denn diese Prosa fließt direkt in externe Changelogs und nutzerseitige Release-Seiten
- **MUSS [MUST]** Pull-Request-Beschreibungen in der CI prüfen (zum Beispiel über einen PR-Check-Workflow) auf dem im Repository konfigurierten `MinAlertLevel` und auf `error`-Stufe genauso scheitern wie die Dokumentation
- **SOLLTE [SHOULD]** die finalen Release-Notes vor der Veröffentlichung gegen Vale prüfen, damit der veröffentlichte Changelog keine Prosa-Verstöße in die Öffentlichkeit trägt

### Mehrsprachige Texte
- **MUSS [MUST]** Vale ausschließlich auf englischsprachig verfassten Inhalt anwenden; Dateien, die in einer anderen Sprache als Englisch verfasst sind, **DÜRFEN NICHT [MUST NOT]** in den Vale-Lint-Scope aufgenommen werden
- **MUSS [MUST]** den englischsprachigen Lint-Scope sowohl in den `.vale.ini`-Format-Abschnitten als auch im Taskfile-Ziel `lint:prose` definieren, damit lokale Läufe und CI denselben Scope anwenden; typische englische Pfade sind `README.md`, `docs/en/`, `skills/*/SKILL.md` (gemäß `skill-management`-Spec in Englisch verfasst) sowie die kanonische Sprachdatei jeder Spec, wenn Englisch kanonisch ist (`spec/<topic>/<slug>/en.md`)
- **DARF NICHT [MUST NOT]** Pfade in den Lint-Scope aufnehmen, die nicht-englischen Inhalt halten: `docs/de/`, `spec/<topic>/<slug>/de.md`, `*.de.md` und jeder entsprechende nicht-englische Pfad bleibt außerhalb von Vale
- **MUSS [MUST]** jede Datei im Vale-Scope frei von nicht-englischer Prosa halten – Fließtext, YAML-Frontmatter-Felder, Inline-Kommentare, zitierte Beispiel-Strings – denn Vale kann Sprachgrenzen innerhalb einer gescopten Datei nicht erkennen und markiert fremde Wörter als Rechtschreibfehler
- **SOLLTE [SHOULD]** signifikante englische Dokumentation in eine parallele nicht-englische Datei unter `docs/de/` oder `spec/<topic>/<slug>/de.md` spiegeln, damit Lesende dieser Sprache sie nutzen können; diese Dateien werden ohne Vale-Checks verfasst und gepflegt und dürfen ihr eigenes natives Vokabular verwenden
- **DARF NICHT [MUST NOT]** ein sprachgebundenes Vokabular (zum Beispiel `vocabularies/technical-de/`) in `nolte/vale-style` als Behelfslösung für sprachgemischte Dateien innerhalb des Vale-Scopes einführen; die kanonische Lösung für eine nicht-englische Passage in einer gescopten Datei ist, die Passage in eine sprachgebundene Datei außerhalb des Scopes zu verschieben, und nicht, Vale Fremdvokabular beizubringen

## Akzeptanzkriterien
- [ ] `.vale.ini` existiert im Repository-Wurzelverzeichnis (oder an der Dokumentationswurzel) und verweist auf ein gepinntes `nolte/vale-style`-Release
- [ ] `vale sync` läuft gegen die eingecheckte Konfiguration ohne manuelle Eingriffe erfolgreich durch
- [ ] Ein Taskfile-Ziel führt Vale über alles menschenlesbare Markdown des Repositories aus
- [ ] CI scheitert, wenn Vale auf geändertem Markdown Alerts auf `error`-Stufe meldet
- [ ] `.pre-commit-config.yaml` registriert einen Vale-Hook, der über dasselbe Taskfile-Ziel wie die CI gegen geändertes Markdown läuft
- [ ] Keine repository-lokale Vokabular-Datei enthält einen Begriff, den das gepinnte `nolte/vale-style`-Release bereits akzeptiert
- [ ] Jeder in einer jüngeren Änderung eingeführte Fachbegriff erscheint in einem PR oder einem jüngeren Release von `nolte/vale-style`, nicht nur im Downstream-Repository
- [ ] Jede KI-gestützte Texterzeugungs-Operation prüft den Output vor Abschluss gegen die Vale-Konfiguration des Repositories
- [ ] Pull-Request-Beschreibungen und GitHub-Release-Notes bestehen Vale auf dem konfigurierten `MinAlertLevel` unter derselben Konfiguration wie die Markdown-Dokumentation des Repositories
- [ ] Der konfigurierte Vale-Lint-Scope enthält keine Dateien, die in einer anderen Sprache als Englisch verfasst sind; `docs/de/`, `spec/<topic>/<slug>/de.md` und jede `*.de.md` sind ausdrücklich nicht im Scope
- [ ] Keine Datei im englischsprachigen Scope enthält irgendwo nicht-englische Prosa – weder im Fließtext, im YAML-Frontmatter, in Inline-Kommentaren noch in zitierten Beispielen; Vale auf `error`-Stufe bestätigt dies

## Offene Fragen
- _Keine – alle vorherigen offenen Punkte sind geklärt. Der Drift-Audit zwischen repository-lokalen Vokabularen und dem gepinnten `nolte/vale-style`-Release wird über einen dedizierten Claude-Skill abgedeckt statt über einen periodischen CI-Cron erzwungen._
