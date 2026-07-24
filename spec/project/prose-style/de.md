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

Die Drift zwischen repository-lokalen Vokabularen und dem gepinnten `nolte/vale-style`-Release wird über den `vocab-drift-audit`-Skill geprüft statt über einen periodischen CI-Cron.

### Pull-Request-Beschreibungen und Release-Notes
- **MUSS [MUST]** dasselbe gemeinsame Vale-Regelwerk auf Pull-Request-Beschreibungen und GitHub-Release-Notes anwenden (vom release-drafter entworfen, vor der Veröffentlichung bearbeitet), denn diese Prosa fließt direkt in externe Changelogs und nutzerseitige Release-Seiten
- **MUSS [MUST]** Pull-Request-Beschreibungen in der CI prüfen (zum Beispiel über einen PR-Check-Workflow) auf dem im Repository konfigurierten `MinAlertLevel` und auf `error`-Stufe genauso scheitern wie die Dokumentation
- **SOLLTE [SHOULD]** die finalen Release-Notes vor der Veröffentlichung gegen Vale prüfen, damit der veröffentlichte Changelog keine Prosa-Verstöße in die Öffentlichkeit trägt

### Stimme und Ton

Die Vale-Regelsätze erzwingen eine mechanische Basislinie, aber die folgenden Regeln kodifizieren die *redaktionelle* Haltung, die jeder verfasste oder KI-generierte Absatz schon haben muss, **bevor** Vale läuft. Sie sind aus dem Microsoft Writing Style Guide (Top-10-Tipps + Brand voice), dem Google Developer Documentation Style Guide (Voice und Audience) und den Write-the-Docs-Dokumentationsprinzipien bezogen; jede Regel unten stützt sich auf mindestens zwei dieser Quellen.

- **MUSS [MUST]** standardmäßig im **Aktiv** schreiben; Passiv **KANN [MAY]** nur verwendet werden, wenn der Akteur wirklich unbekannt oder irrelevant ist oder das Aktiv ein gequältes Subjekt erzwingen würde (Microsoft Top-10 §Revise weak writing: „Most of the time, start each statement with a verb"; Google Voice and Tone)
- **MUSS [MUST]** den Leser in der **zweiten Person** ansprechen (`du`/`Sie`, je nach Sprachzweig) auf jeder Seite, deren `content_mode` `tutorial` (was Quickstart-Seiten gemäß `spec/project/docs-audience-tracks/` §Inhaltskontrakt der user-docs einschließt), `how-to` oder `troubleshooting` ist; `reference`-, `explanation`- und `glossary`-Seiten bleiben unpersönlich (Microsoft Top-10 §Project friendliness; Diátaxis tutorials/how-to-guides: „the learner / the reader"; Diátaxis Explanation: „higher and wider perspective" impliziert dritte Person)
- **MUSS [MUST]** das **Präsens** für System-Verhalten verwenden („der Befehl liefert", nicht „der Befehl wird liefern") und für Anweisungen („wähle", nicht „du wirst wählen"); Vergangenheitsformen bleiben Changelog- und Release-Note-Prosa vorbehalten (Microsoft Brand voice; Google Voice)
- **MUSS [MUST]** **Sentence-Case-Großschreibung** für jede Überschrift, jeden Listeneintrag, jeden Button-Namen und jede Tabellenzelle mit drei oder weniger Wörtern verwenden; Title-Case („Like This") ist außerhalb von Eigennamen und Produktnamen verboten (Microsoft Top-10 §When in doubt, don't capitalize: „Never Use Title Capitalization (Like This). Never Ever"; durch Vales Microsoft-Style ratifiziert)
- **MUSS [MUST]** die Antwort oder den ersten Befehl vor jedem Hintergrund nach vorne ziehen; das ist das seiten-weite Äquivalent zur §Inhalts-Modi-Rahmungsregel in `spec/project/mkdocs-structure/` (Microsoft Top-10 §Get to the point fast; Google „Clear information first"; WtD Skimmable)
- **SOLLTE [SHOULD]** Absätze kurz halten (typischerweise drei Sätze oder weniger) und Listen für jede Sequenz aus drei oder mehr parallelen Punkten bevorzugen (Microsoft Top-10 §Be brief; WtD Skimmable)
- **SOLLTE [SHOULD]** **Kontraktionen** sparsam, aber konsistent pro Sprachzweig verwenden (englische Doku nutzt `you're`, `it's`, `don't`; der deutsche Zweig behält die ausgeschriebenen Formen bei, die der Microsoft Localization Style Guide für Deutsch verlangt) (Microsoft Top-10 §Project friendliness; Microsoft Localization Style Guides — Deutsch)
- **SOLLTE [SHOULD]** jede Nicht-`reference`-Seite mit einem ein- bis drei-Satz-Rahmungsabsatz öffnen, der die Situation des Lesers benennt (was er hat, was er will), bevor die erste H2 kommt (spiegelt `spec/project/mkdocs-structure/` §Inhalts-Modi (Diátaxis-Ausrichtung))
- **DARF NICHT [MUST NOT]** **Idiome, Slang, Sport-Metaphern, militärische Metaphern oder kulturell spezifische Referenzen** in englisch-gescopter Prosa ausliefern; die Prosa muss für ein globales Publikum lesen, dessen Muttersprache nicht zwingend Englisch ist (Google Voice „No culturally specific references"; Microsoft Bias-Free Communication §Militaristic language)
- **DARF NICHT [MUST NOT]** **generische geschlechts-gebundene Pronomen** ausliefern (`he`, `she`, `his`, `hers`, `he/she`); in zweite Person, Plural oder rollenbasierte Referenzen umschreiben (Microsoft Bias-Free Communication: „Don't use he, him, his, she, her, or hers in generic references"; Linguistic Society of America Guidelines for Inclusive Language)
- **DARF NICHT [MUST NOT]** **ableistische oder anderweitig nicht-inklusive Formulierungen** ausliefern; insbesondere sind die Ersetzungen aus Microsofts Bias-Free Communication §Don't use terms that may carry unconscious racial bias verpflichtend (`primary` / `subordinate` statt `master` / `slave`; `stop responding` statt `hang`; `perimeter network` statt `DMZ`). Das gemeinsame Vale-Vokabular unter `nolte/vale-style` trägt die kuratierte Ersetzungs-Liste; neue Inklusiv-Sprach-Substitutionen werden gemäß §Neue Begriffe und Formulierungen dort deponiert, nicht in Per-Repo-Overrides.
- **DARF NICHT [MUST NOT]** **Ausrufezeichen** außerhalb echter Betonung ausliefern (Release-Note-Stil ist in Release-Notes erlaubt; Dokumentations-Prosa ist nicht der Ort dafür) (Google Voice „Avoid exclamation marks")
- **DARF NICHT [MUST NOT]** **Emoji** in Spec-, ADR- oder Reference-Prosa ausliefern; Emoji **DÜRFEN [MAY]** in Release-Notes, README-Badge-Zeilen und informellen Blog-Posts auftauchen, wenn die Stimme des Projekts es trägt (Portfolio-Konvention; nicht im Widerspruch zu Upstream-Style-Guides)
- **KANN [MAY]** **Microcopy-Muster** verwenden, die Microsoft Top-10 ratifiziert (verb-first List-Items, „you can" gestrichen, zwei-oder-drei-Wort-Überschriften ohne Schluss-Punktion)

Standardmäßig bleiben diese §Stimme-und-Ton-Regeln **redaktionelle Leitlinien**: Sie werden über den menschlichen oder KI-gestützten Lektorat-Lauf (`spec/project/lektorat/` §Erkennungs-Dimensionen, der sie als D4-Stilbefunde aufzeigt) und über das Pull-Request-Review durchgesetzt, nicht über maßgeschneiderte Vale-Regeln. Das Portfolio verfasst keinen allgemeinen Aktiv-Detektor, keinen Title-Case-Detektor und keinen Pronomen-Detektor in `nolte/vale-style`, bis dokumentierte Drift die Regel-Kosten rechtfertigt; die [`spec/project/lektorat/`](../lektorat/de.md) §Nicht-Ziele verweisen dieselbe Entscheidung an diese Spec als Eigentümerin zurück. Die einzige bereits automatisierte Ausnahme ist die Bias-Free-Ersetzungs-Tabelle, die `nolte/vale-style` upstream trägt (siehe den Inklusiv-Sprach-Punkt oben und den zugehörigen §Akzeptanzkriterien-Eintrag). Wird die Automatisierung gerechtfertigt, deponiere gezielte Upstream-Regeln in dieser Reihenfolge – zuerst generische geschlechts-gebundene Pronomen, Ausrufezeichen und Title-Case-Überschriften, weil sie die Klassen mit den wenigsten False-Positives sind – und halte die allgemeine Aktiv-Klasse manuell, weil sie am anfälligsten für False-Positives ist. Der zählbare Revisit-Trigger ist in §Offene Fragen festgehalten.

### Mehrsprachige Texte
- **MUSS [MUST]** Vale ausschließlich auf englischsprachig verfassten Inhalt anwenden; Dateien, die in einer anderen Sprache als Englisch verfasst sind, **DÜRFEN NICHT [MUST NOT]** in den Vale-Lint-Scope aufgenommen werden
- **MUSS [MUST]** den englischsprachigen Lint-Scope sowohl in den `.vale.ini`-Format-Abschnitten als auch im Taskfile-Ziel `lint:prose` definieren, damit lokale Läufe und CI denselben Scope anwenden; der Scope deckt ausschließlich endnutzer-gerichtete Prosa ab – typische englische Pfade sind `README.md`, `docs/en/` und die kanonische Sprachdatei jeder Spec, wenn Englisch kanonisch ist (`spec/<topic>/<slug>/en.md`)
- **DARF NICHT [MUST NOT]** Pfade in den Lint-Scope aufnehmen, die nicht-englischen Inhalt halten: `docs/de/`, `spec/<topic>/<slug>/de.md`, `*.de.md` und jeder entsprechende nicht-englische Pfad bleibt außerhalb von Vale
- **DARF NICHT [MUST NOT]** LLM-Instruktions-Artefakte in den Lint-Scope aufnehmen – `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md` und jedes vergleichbare plugin-seitige Claude-Code-Artefakt bleibt außerhalb von Vale; diese Dateien sind Tool-Autor-zu-LLM-Instruktionen, keine endnutzer-gerichtete Prosa, und Microsoft-Style-Regeln für Endnutzer-Texte erzeugen auf ihnen Rauschen statt Signal
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
- [ ] Der konfigurierte Vale-Lint-Scope enthält keine LLM-Instruktions-Artefakte; `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**` und `agents/*.md` sind ausdrücklich nicht im Scope
- [ ] Keine Datei im englischsprachigen Scope enthält irgendwo nicht-englische Prosa – weder im Fließtext, im YAML-Frontmatter, in Inline-Kommentaren noch in zitierten Beispielen; Vale auf `error`-Stufe bestätigt dies
- [ ] Verfasste oder KI-generierte Absätze folgen den §Stimme-und-Ton-Regeln (Aktiv, zweite Person auf instruktiven Seiten, Präsens, Sentence-Case-Überschriften, vorgezogene Antwort); ein Reviewer kann jede Seite stichprobenartig prüfen und die Regeln eingehalten finden
- [ ] Keine englisch-gescopte Prosa trägt generische geschlechts-gebundene Pronomen (`he`, `she`, `his`, `hers`, `he/she`), militaristische oder ableistische Ersetzungen, die die Microsoft-Bias-Free-Communication-Tabelle ratifiziert, Ausrufezeichen außerhalb echter Betonung oder kulturell spezifische Idiome; das gemeinsame Vale-Vokabular unter `nolte/vale-style` markiert jeden bekannten Verstoß auf `error`-Stufe
- [ ] Das gemeinsame Vale-Vokabular unter `nolte/vale-style` trägt Microsofts Bias-Free-Ersetzungen (`primary` / `subordinate`, `stop responding`, `perimeter network`, …), damit zur Durchsetzung kein Per-Repo-Override nötig ist

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._

## Quellen
<!-- Autoritative externe Referenzen, gegen die die obigen Anforderungen validiert wurden (≥2 unabhängige Quellen pro Aussage). -->
- Microsoft Writing Style Guide (learn.microsoft.com/style-guide) — Top-10-Tipps, Brand voice, Bias-Free Communication, Militaristic-Language-Hinweise
- Microsoft Localization Style Guides — Deutsch (learn.microsoft.com/de-de/globalization/localization/styleguides) — DACH-Hausstil-Regeln für Kontraktionen und Anredeformen im deutschen Sprachzweig
- Google Developer Documentation Style Guide (developers.google.com/style) — Voice and Tone, Audience, „Clear information first"-Rahmung
- Write the Docs documentation principles (writethedocs.org/guide) — ARID, Skimmable, Exemplary, Current, Consistent
- Linguistic Society of America Guidelines for Inclusive Language (linguisticsociety.org) — Zweitlinien-Ratifizierung der inklusiven Pronomen-Hinweise, auf die Microsoft sich bezieht
