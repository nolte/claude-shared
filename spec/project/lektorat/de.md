# Lektorat

Status: draft

## Kontext

Portfolio-Repositories setzen bereits einen mechanischen Prosa-Standard durch: [`spec/project/prose-style/`](../prose-style/de.md) verdrahtet Vale (Microsoft + RedHat + `nolte/vale-style`) über jede englischsprachige Markdown-Fläche, und [`spec/project/docs-multilingual-authoring/`](../docs-multilingual-authoring/de.md) garantiert, dass die DE/EN-Seitenbäume strukturell parallel bleiben. Was keine der beiden Specs beantwortet, ist die **redaktionelle** Frage, sobald ein Entwurf existiert: ist die Seite tatsächlich **lesbar** für ihre Zielgruppe, ist sie **ohne versteckte Vorannahmen verständlich**, ist die **deutsche** Seite korrekt geschrieben, und passt die **Tonalität** zu der Audience, für die das Dokument verfasst wurde?

`Lektorat` schließt diese Lücke. Es ist die operative Ebene, die bereits **vorhandene** Prosa **auditiert, patcht oder überarbeitet** — entlang vier Qualitätsdimensionen (Lesbarkeit, Verständlichkeit, Rechtschreibung/Grammatik, Schreibstil) plus einer fünften **Zielgruppen-Fit**-Dimension, die die Prosa an das Audience-Artefakt aus [`spec/project/audience-identification/`](../audience-identification/de.md) und an den Per-Seite-Track-Vertrag aus [`spec/project/docs-audience-tracks/`](../docs-audience-tracks/de.md) zurückbindet. Vale bleibt für seine Regelmechanik zuständig; `audience-doc-author` bleibt für Erstautorschaft zuständig; diese Spec definiert, was **nachdem** ein Text existiert und **bevor** er als fertige Arbeit behandelt wird, geschieht.

Zwei Designvorgaben prägen die Spec. Erstens ist die Ebene **operativ**, nicht deskriptiv: sie verlangt drei Operationen (`audit`, `patch`, `revise`) mit expliziten Vor- und Nachbedingungen, sodass nachgelagerte Skills und Agents den Vertrag implementieren können, ohne die Semantik neu verhandeln zu müssen. Zweitens ist die Ebene **pro Sprache**: jede Sprachfassung wird gegen die Regeln ihrer eigenen Sprache geprüft (DE-Regeln auf DE-Text, EN-Regeln auf EN-Text), und Übersetzungs-Synchronisation bleibt Aufgabe von `spec` und `docs-freshness`.

**Leserschaft** dieser Spec sind Implementierer der `lektorat-apply`-Skill und des `lektorat-scanner`-Agents (primär) sowie Operatoren, die `audit` / `patch` / `revise` aus CI-, Sprint-Review- oder Release-Publish-Gates aufrufen (sekundär). Vertrautheit mit `spec/project/mkdocs-structure/` (dem `content_mode`-Enum), `spec/project/audience-identification/` (dem Audience-Artefakt) und `spec/project/docs-audience-tracks/` (dem Per-Seite-`audience` / `track`-Frontmatter) wird vorausgesetzt; Begriffe aus jenen Specs werden ohne erneute Erklärung verwendet.

## Ziele

- Bestehende menschenlesbare Prosa in diesem Repo (und in Konsumenten-Repos, die die Spec übernehmen) lässt sich gegen einen stabilen, benannten Satz redaktioneller Qualitätsdimensionen prüfen und überarbeiten, ohne die Regeln pro Skill neu zu implementieren
- Skills und Agents, die redaktionelle Arbeit verrichten, unterscheiden drei Operationen (`audit` für read-only-Inspektion, `patch` für Per-Befund-Edits mit explizitem OK, `revise` für Volldokument-Überarbeitungen mit Diff-Review), und die gewählte Operation ist in ihrer Ausgabe sichtbar
- Redaktionelle Befunde werden reproduzierbar nach **Severity** klassifiziert (`critical` / `warning` / `suggestion`), sodass ein nachgelagertes Gate (CI, sprint-review, release-publish) entscheiden kann, was blockiert und was beratend ist
- Lesbarkeits- und Verständlichkeits-Befunde referenzieren **benannte Metriken mit sprach­spezifischen Zielkorridoren**, sodass ein Befund auditierbar ist statt eine stilistische Meinung zu sein
- Zielgruppen-Fit wird gegen das **Audience-Artefakt** geprüft, das das Repository ohnehin produziert, nicht gegen eine ad-hoc geratene Audience pro Review
- DE-Text und EN-Text werden mit **sprachgerechter Mechanik** geprüft; die DE-Pipeline hängt nicht an Vale, das `prose-style` explizit auf Englisch beschränkt
- Die Abgrenzung gegen `prose-style` (Regelmechanik), `audience-doc-author` (Erstautorschaft), `docs-freshness` (Drift-Erkennung) und `spec` (Übersetzungs-Synchronisation) ist scharf genug, dass keine Anforderung in zwei Specs steht

## Nicht-Ziele

- Definition oder Pflege der Vale-Konfiguration, des Vale-Vokabulars oder der Prosa-Regelmechanik — das gehört [`spec/project/prose-style/`](../prose-style/de.md) und dem stromaufwärtigen Paket [`nolte/vale-style`](https://github.com/nolte/vale-style)
- Erstautorschaft neuer Seiten — das gehört dem Agent `audience-doc-author` und seinen aufrufenden Skills (`readme-structure-apply`, `audience-doc-author` selbst); `Lektorat` operiert auf bereits vorhandener Prosa
- Übersetzung von Prosa von einer Sprache in eine andere — das gehört der `spec`-Skill (für `spec/`-Inhalte), `docs-multilingual-authoring` (für atomare DE/EN-Parität pro Seite) und `audience-doc-author` (für neue Seiten); `Lektorat` prüft jede Sprache eigenständig
- Synchronisation der Parität zwischen DE- und EN-Fassung desselben Artefakts — das gehört `docs-freshness` (Audit-Zeit-Erkennung) und `docs-multilingual-authoring` (Authoring-Zeit-Verhinderung)
- Lektorat von Quellcode, Code-Kommentaren, Docstrings, API-Referenz-Texten, generierten Manifesten, generierten Configs oder YAML/JSON-Config-Bodys; die Ebene prüft Prosa **in Markdown** und behandelt umzäunte Code-Blöcke als unantastbar
- Lektorat von Dateien unter `spec/` — sie folgen dem Übersetzungs-Flow der `spec`-Skill und haben eigene autoritative Drift-Checks; eine Aufnahme hier würde eine zweite Quelle der Wahrheit für Spec-Prosa erzeugen
- Autorschaft von Vale-Regeln (Active-Voice-Detektor, gendered-pronoun-Detektor und Ähnliches): `prose-style` führt das bereits als aufgeschobene Entscheidung und `Lektorat` greift dem nicht vor
- Slack-Nachrichten, Wiki-Seiten, Blog-Posts oder andere Nicht-Markdown-Prosa-Flächen für Menschen — `Lektorat` deckt GitHub-Issue- und Pull-Request-Bodys als bewusste Scope-Erweiterung ab (sie sind nutzersichtbares Markdown, das in Suchmaschinen und Projekt-Historie landet). Anmerkung: `prose-style` §Pull-request descriptions and release notes verlangt bereits Vale-Abdeckung auf EN-PR-Bodys und EN-Release-Note-Bodys; `Lektorat` führt diese Abdeckung dort **nicht** ein, sondern erweitert sie um die D1/D2/D5-Dimensionen und die DE-Pipeline. Befunde aus dem Vale-CI-Gate von `prose-style` werden gemäß §Koordination mit Nachbarspecs per Vale-Regel-ID dedupliziert. Andere Prosa-Flächen bleiben außerhalb des Scopes, bis sie separat spezifiziert sind
- Ein blockierendes Gate für redaktionelle Befunde der Severity `suggestion`; nur `critical`-Befunde sind gate-tauglich, und selbst dann opt-in pro Repository (siehe §Severity-Klassifikation)

## Anforderungen

### Geltungsbereich und Anwendbarkeit

- **MUSS [MUST]** die folgenden Artefakt-Typen als **im Scope** von `Lektorat` behandeln: MkDocs-Seiten unter `docs/<lang>/` (ausschließlich `_`-präfigierter Snippet-Ordner, die mit ihrer einbindenden Seite geprüft werden), Top-Level-Repository-Markdown (`README.md`, `ONBOARDING.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`), den Body von GitHub Releases (Release-Notes) sowie den Body von GitHub Issues und Pull-Requests
- **DARF NICHT [MUST NOT]** Dateien unter `spec/` in den `Lektorat`-Scope aufnehmen; Spec-Prosa wird durch den autoritativen Flow der `spec`-Skill und ihre Übersetzungs-Sync-Regeln regiert. Ein Befund, der die Bearbeitung einer Spec-Datei erfordert, ist ein Befund **gegen die Anweisungen der aufrufenden Skill**, nicht gegen die Spec
- **DARF NICHT [MUST NOT]** Quellcode, Code-Kommentare, Docstrings, generierte Konfiguration (`.github/*.yml` aus `project-structure-apply`, `mkdocs.yml`, `Taskfile.yml`, Lockfiles), LLM-Instruktions-Artefakte (`skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`) oder irgendein binäres Artefakt in den `Lektorat`-Scope aufnehmen
- **MUSS [MUST]** umzäunte Code-Blöcke (```` ``` ```` … ```` ``` ````), Inline-Code (`` ` `` … `` ` ``), HTML-Kommentare (`<!-- … -->`) und YAML-Frontmatter (` --- … --- ` am Dateianfang) als **read-only** behandeln: die Ebene liest sie für Kontext, **DARF** sie aber **NICHT** umschreiben, umformatieren oder annotieren
- **MUSS [MUST]** einem Repository erlauben, den In-Scope-Satz über eine `Lektorat`-lokale Konfiguration (Pfad-Globs, Artefakt-Typ-Allowlist) zu **verengen**, **DARF** einem Repository aber **NICHT** erlauben, den Scope um Artefakt-Typen zu erweitern, die die Spec oben ausdrücklich verbietet

### Qualitätsdimensionen

Die fünf Dimensionen unten sind die **autoritative** Liste. Jeder von einer `Lektorat`-Operation erzeugte Befund **MUSS [MUST]** genau eine Dimension nennen. Severitäten mappen auf eine dimensionsspezifische Rubrik unter §Severity-Klassifikation.

#### D1 — Lesbarkeit

- **MUSS [MUST]** Lesbarkeit gegen benannte Metriken mit expliziten sprach­spezifischen Zielkorridoren bewerten:
  - **Englischer Text**: Flesch Reading Ease (FRE) und Flesch–Kincaid Grade Level (FKGL)
  - **Deutscher Text**: Wiener Sachtextformel (WSTF) Variante 1 und LIX
- **MUSS [MUST]** Zielkorridore pro `content_mode` ausweisen, sodass eine `tutorial`-Seite nicht an derselben Dichte gemessen wird wie eine `reference`-Seite; die Default-Korridore sind:

  | `content_mode` (per `spec/project/mkdocs-structure/`) | EN: FRE warn / crit | EN: FKGL warn / crit | DE: WSTF warn / crit | DE: LIX warn / crit |
  | --- | --- | --- | --- | --- |
  | `tutorial`, `how-to`, `troubleshooting` | < 60 / < 45 | > 10 / > 14 | > 7 / > 10 | > 50 / > 60 |
  | `explanation`, `reference`, `glossary` | < 45 / < 30 | > 14 / > 18 | > 10 / > 13 | > 60 / > 70 |

  Die `crit`-Spalte ist abgeleitet, indem die `warn`-Grenze um eine **Korridor­breite** (den absoluten Abstand zwischen den beiden `content_mode`-Zeilen derselben Metrik) verlängert wird: FRE-Breite = 15, FKGL-Breite = 4, WSTF-Breite = 3, LIX-Breite = 10. Die `crit`-Schwellen oben sind die operativen Werte; die Herleitung ist dokumentiert, damit eine künftige `content_mode`-Zeile konsistent ergänzt werden kann.

- **MUSS [MUST]** eine Metrik, deren Wert die `warn`-Schwelle überschreitet (aber nicht die `crit`-Schwelle), als `warning`-Befund klassifizieren, und eine Metrik, deren Wert die `crit`-Schwelle überschreitet, als `critical`-Befund; die Schwellen werden aus der Per-`content_mode`-Zeile oben gelesen
- **DARF NICHT [MUST NOT]** D1-Bewertung auf eine Seite anwenden, deren `content_mode` `meta` ist (gemäß `spec/project/mkdocs-structure/`); Meta-Seiten (Home, Per-Section-Index) sind von Lesbarkeits-Metriken ausgenommen, weil ihre Prosa navigatorisch und nicht instruktiv ist und keine Korridor-Zeile auf sie passt. Top-Level-Repository-Markdown ohne `content_mode`-Frontmatter-Key (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `ONBOARDING.md`) **MUSS [MUST]** für D1-Zwecke auf `content_mode: meta` defaulten; dieser Default propagiert **nicht** in D3/D4/D5, die den Text gemäß ihrer eigenen Regeln bewerten
- **DARF [MAY]** die Per-`content_mode`-Korridore **pro Datei** über einen `Lektorat`-lokalen Konfigurations-Eintrag der Form `{path: <glob>, FRE_warn: <int>, FRE_crit: <int>, FKGL_warn: <int>, FKGL_crit: <int>, WSTF_warn: <float>, WSTF_crit: <float>, LIX_warn: <int>, LIX_crit: <int>}` überschreiben. Das Override **MUSS [MUST]** eine konkrete Begründung benennen (inline in der Konfiguration deklariert) und **MUSS [MUST]** innerhalb ±50 % des Default-Korridor-Werts bleiben; ein Override außerhalb dieses Bands ist ein Spec-Verstoß, und der Operator **MUSS [MUST]** stattdessen den Quelltext überarbeiten. Die portfolio-weite Re-Kalibrierung der Default-Korridore ist eine Open Question, gated auf mindestens drei Portfolio-Member-Repos, die Audit-Daten liefern
- **MUSS [MUST]** den berechneten Metrik-Wert, den Korridor und mindestens ein verstoßendes Beispiel (längster Satz, tiefste Schachtelung) im Befund nennen, damit er auditierbar ist
- **DARF NICHT [MUST NOT]** im `patch`-Modus eine Passage aus reinen Lesbarkeits-Gründen umschreiben, ohne einen Metrik-Wert oder eine benannte Heuristik-Quelle im Befund; eine Meinung ist kein Befund
- **SOLLTE [SHOULD]** Metrik-Befunde durch **strukturelle Heuristiken** ergänzen (Absätze länger als drei Sätze, Listen mit mehr als sieben Peers, Überschriften tiefer als `####`) — diese sind per Default `suggestion`
- **SOLLTE [SHOULD]** die benannten Metriken berechnen, indem eine gepflegte sprach­spezifische Lesbarkeits-Bibliothek konsumiert wird (eine `textstat`-Klasse-Bibliothek für Englisch, eine `readability-de`-Klasse-Bibliothek für Deutsch), statt die klassischen Formeln neu zu implementieren; die Spec schränkt nur die Metrik-Namen und die Korridore oben ein, nicht die Implementierung, und die gewählte Bibliothek **KANN [MAY]** neben den Pipeline-Metadaten (§Ausgaben) zur Reproduzierbarkeit aufgezeichnet werden

#### D2 — Verständlichkeit

- **MUSS [MUST]** die folgenden Muster als Verständlichkeits-Befunde flaggen:
  - **Jargon-Last**: ein Fachterm taucht ohne vorherige Definition auf, wobei „Fachterm" alles abdeckt, was nicht im audience-passenden Grundvokabular des Projekts steht (siehe §Audience-Bindung)
  - **Ungeklärte Abkürzungen**: eine Abkürzung (`SRE`, `RTO`, `CSP`) erscheint ohne Auflösung bei Erstnennung auf der Seite
  - **Versteckte Vorannahmen**: eine Anweisung oder Aussage hängt von einer früheren Datei, einem Umgebungs­zustand oder einem Werkzeug ab, das auf der aktuellen Seite nicht genannt wird
  - **Implizite Annahmen**: ein Satz unterstellt Rolle, Tooling oder Background der Leserschaft, ohne es zu sagen. Die Markerwort-Liste liegt in [`spec/project/lektorat/markers-de.yml`](markers-de.yml) (Deutsch) und [`spec/project/lektorat/markers-en.yml`](markers-en.yml) (Englisch) als versionierte, pflegbare Liste statt einer inline-Aufzählung; das per-Eintrag `severity_floor` (`suggestion` oder `warning`) bestimmt die höchste Severity, die der Marker unter der §D2-Eskalationstabelle erreichen kann
- **MUSS [MUST]** jedes D2-Muster mit der unten genannten Default-Severity klassifizieren und nur über die genannte Regel eskalieren. Das Severity-Bucket-Vokabular `critical` / `warning` / `suggestion` ist in §Severity-Klassifikation definiert; diese Tabelle ist die pro-Muster-Auflösung und das, was Implementierungen anwenden:

  | D2-Muster | Default-Severity | Eskalation |
  | --- | --- | --- |
  | Jargon-Last | `warning` | `critical`, wenn das Artefakt eine publizierte Fläche ist (`README.md`, Release-Note-Body, Top-Level-Docs) **und** die aufgelöste Audience eine Nicht-Operator-Rolle enthält |
  | Ungeklärte Abkürzungen | `warning` | `critical`, wenn die Abkürzung in einer Überschrift, im ersten Absatz oder in einem Callout erscheint (den lasttragenden Flächen der Seite) |
  | Versteckte Vorannahmen | `warning` | `critical` auf Seiten, deren `content_mode` `tutorial` oder `how-to` ist (die Vorannahme würde den Leser blockieren) |
  | Implizite Annahmen | `suggestion` | `warning`, wenn das Markerwort („einfach", „nur", „offensichtlich") mit einem Schritt gepaart ist, den die Leserschaft ausführen muss |

- **MUSS [MUST]** im Zweifel den **Kontext-Ergänzen**-Patch (ein kurzer Satz, eine inline-Auflösung) gegenüber dem **Jargon-Streichen**-Patch bevorzugen, wenn ein Fachterm wirklich tragend ist; Verständlichkeits-Befunde sind kein Freibrief, technische Präzision zu entfernen
- **DARF NICHT [MUST NOT]** einen Term, der an anderer Stelle der Seite erklärt ist (Definitionsliste, vorheriger Abschnitt, eingeklammerter Hinweis), als Verständlichkeits-Befund flaggen

#### D3 — Rechtschreibung und Grammatik

- **MUSS [MUST]** **sprach­spezifische** Rechtschreib- und Grammatikprüfung anwenden:
  - **Englischer Text** — delegiert an die von `prose-style` regierte Vale-Mechanik; `Lektorat` implementiert Rechtschreibung/Grammatik für Englisch **nicht** neu, sondern konsumiert die Vale-Ausgabe und surfaced sie als `D3`-Befunde im einheitlichen Report
  - **Deutscher Text** — wendet eine `Lektorat`-eigene DE-Pipeline an (Portfolio-Default: LanguageTool HTTP API; siehe §Sprach-Handhabung), weil `prose-style` Vale ausdrücklich auf Englisch beschränkt und eine DE-Alternative portfolio-weit nicht verfügbar ist
- **MUSS [MUST]** die folgenden Klassen vor jeder Rechtschreib-Korrektur schützen: **Eigennamen, Produktnamen, technische Identifier, Befehlsnamen, Dateipfade, URLs, projektspezifischer Jargon** — die Quelle der geschützten Menge ist das Audience-Artefakt und das `nolte/vale-style`-Vokabular (für Englisch) bzw. [`spec/project/lektorat/protected-terms-de.yml`](protected-terms-de.yml) (für Deutsch); die Geschützte-Begriffe-Datei ist YAML, versioniert, und Hinzufügungen verlangen einen einzeiligen Rationale-Kommentar, damit Reviewer jeden Eintrag beurteilen können
- **MUSS [MUST]** einen Rechtschreib- oder Grammatik-Befund als `critical` klassifizieren, wenn er die gerenderte Bedeutung verändern würde oder in einem publizierten Artefakt sichtbar ist (Release-Note-Body, README, Top-Level-Docs); andernfalls als `warning`
- **DARF NICHT [MUST NOT]** eine Schreibweise korrigieren, die das Audience-Artefakt oder die Geschützte-Begriffe-Liste als beabsichtigt markiert (Markenname, Produkt-Schreibweise, bewusste Stilisierung)

#### D4 — Schreibstil

- **MUSS [MUST]** Schreibstil für englischen Text gegen den **anwendbaren** Ausschnitt von `prose-style` §Voice and tone bewerten; die dort gelisteten Regeln sind autoritativ und `Lektorat` definiert sie nicht neu
- **MUSS [MUST]** analoge Regeln auf deutschen Text anwenden (Aktiv als Default, Präsens für Systemverhalten, Satz-Großschreibung in Überschriften, „Sie"-Anrede auf tutorial/how-to/troubleshooting-Seiten und unpersönlich auf reference/explanation/glossary, keine gendered-generic-Konstruktionen); ein Verstoß ist per Default `warning` und ein `critical`-Befund, wenn er das Register des Dokuments gegen seine deklarierte Audience verschiebt
- **MUSS [MUST]** **Inkonsistenzen innerhalb desselben Artefakts** als `warning` flaggen: gemischter Voice (Aktiv/Passiv-Wechsel), gemischtes Tempus (Präsens/Futur-Wechsel), gemischte Anrede (`du`/`Sie`-Wechsel auf derselben Seite), gemischte Großschreibung in Überschriften — interne Konsistenz wiegt schwerer als die Einzelwahl
- **DARF [MAY]** im `patch`-Modus einen Stil-Rewrite vorschlagen, der das gesamte Artefakt auf eine konsistente Haltung dreht, mit explizitem Vorher/Nachher-Diff

#### D5 — Zielgruppen-Fit

- **MUSS [MUST]** die **deklarierte Audience** eines Artefakts auflösen — aus dem Frontmatter der Seite (`audience`-Key bei MkDocs-Seiten gemäß `docs-audience-tracks`) oder, wenn kein Frontmatter existiert, aus den Artefakt-Typ-Defaults gemäß §Audience-Bindung unten
- **MUSS [MUST]** das von `audience-identification` produzierte **Audience-Artefakt** aus seinem kanonischen Ort lesen (`AUDIENCES.md` am Root des Bounded Context gemäß `audience-identification` §Anforderungen, oder der dort deklarierte Alternativ-Ort — README-Abschnitt "## Audiences" / "## Intended consumers" oder ein ADR) und es als **autoritative Beschreibung** verwenden, was jede Audience versteht und nicht versteht; `Lektorat` **DARF NICHT [MUST NOT]** Audience-Eigenschaften erfinden, die nicht im Artefakt stehen
- **MUSS [MUST]** Zielgruppen-Fit-Befunde unter den folgenden Mustern flaggen:
  - **Register-Mismatch**: eine instruktive Seite für Endnutzer, die operator-internen Jargon verwendet (oder umgekehrt)
  - **Fehlender audience-pflichtiger Inhalt**: ein Artefakt, dessen deklarierte Audience einen bestimmten Abschnitt erwartet (gemäß den `docs-audience-tracks`-Content-Blöcken), der fehlt oder leer ist
  - **Falsche-Audience-Inhalt**: ein Abschnitt, der eine Audience adressiert, die die Seite nicht deklariert (typisch: ein contributor-orientierter Anhang auf einem Endnutzer-Quickstart)
- **MUSS [MUST]** Register-Mismatch und fehlenden audience-pflichtigen Inhalt als `critical` klassifizieren für jedes Artefakt, dessen deklarierte Audience eine Nicht-Operator-Audience einschließt (Endnutzer, Kunden, Evaluatoren); eine Dokumentations-Lücke, die ein zahlender Konsument bemerkt, ist kein `suggestion`
- **DARF NICHT [MUST NOT]** Inhalt umschreiben, um eine **andere** Audience zu treffen als die deklarierte; die Auflösung für einen Falsche-Audience-Abschnitt ist, **ihn dem Operator zur Verschiebung zu flaggen**, nicht ihn still neu zu rahmen

### Severity-Klassifikation

- **MUSS [MUST]** jeden Befund in genau eine von drei Severitäten klassifizieren:
  - `critical`: würde gerenderte Bedeutung verändern, ist in einem publizierten Artefakt sichtbar oder verfehlt das Zielgruppen-Fit-Gate oben
  - `warning`: verfehlt einen benannten Metrik-Korridor, verfehlt eine `prose-style`-MUSS, die nicht in `critical` kippte, oder bricht interne Konsistenz
  - `suggestion`: qualifiziert eine Heuristik, schlägt eine stilistische Verfeinerung vor oder weitet einen Satz für Klarheit, ohne die Bedeutung zu verändern
- **MUSS [MUST]** diese Severity-Namen wörtlich in maschinenlesbarer Ausgabe verwenden (JSON-Keys, Frontmatter-Values, CLI-Exit-Code-Mapping); `info`, `error`, `notice` und ähnliche Synonyme sind **DARF NICHT [MUST NOT]**
- **MUSS [MUST]** Severity-Klassifikation **dimensions­bewusst** halten: ein D3-Tippfehler in einem publizierten Release-Note ist `critical`, derselbe Tippfehler in einem Markdown-Kommentar als Entwurf ist `warning`, derselbe Tippfehler innerhalb eines Code-Identifiers ist **kein Befund** (außer Scope gemäß §Geltungsbereich)
- **MUSS [MUST]** `critical`-Befunde in nachgelagerten Gates (`sprint-review`, `release-publish-trigger`) **per Default beratend** behandeln: ein `critical`-Befund **DARF NICHT [MUST NOT]** für sich allein einen Sprint-Review oder ein Release blockieren. Ein Repository **KANN [MAY]** über ein `Lektorat`-lokales Flag in das Blockieren bei `critical` opt-in gehen — analog dazu, wie `docs-freshness` Befunde surfaced, ohne Releases zu blockieren. Die portfolio-weite Promotion von `critical` von beratend zu blockierend ist ein nachverfolgter Follow-up, gated auf das erste Quartal akkumulierter Audit-Daten, und ist noch nicht in Kraft

### Operationen

Die `Lektorat`-Ebene **MUSS [MUST]** genau drei Operationen unterscheiden. Die Namen unten sind die **einzigen** zulässigen Operationsnamen in maschinenlesbarer Ausgabe.

#### Operation A: `audit`

- **MUSS [MUST]** **read-only** sein; die Operation **DARF NICHT [MUST NOT]** in ein In-Scope-Artefakt schreiben, **DARF NICHT [MUST NOT]** andere Dateien bearbeiten und **DARF NICHT [MUST NOT]** ein Werkzeug dispatchen, das Repository-Zustand verändert
- **MUSS [MUST]** einen **strukturierten Befunde-Report** (§Ausgaben) produzieren, sortiert nach Severity (`critical` zuerst, dann `warning`, dann `suggestion`) und innerhalb Severity nach Quellpfad, dann Dimension
- **MUSS [MUST]** ohne Operator-Interaktion abschließen (keine Mid-Flow-Approvals, keine Rückfragen), sodass die Operation aus CI, pre-commit, sprint-review und release-publish-Gates aufgerufen werden kann
- **MUSS [MUST]** für denselben Input **deterministisch** sein: ein Re-Run von `audit` auf demselben Artefakt-Satz mit derselben Konfiguration erzeugt dieselben Befunde (Reihenfolge identisch, Severitäten identisch, Metrik-Werte innerhalb ±1 für Float-Berechnungen)

#### Operation B: `patch`

- **MUSS [MUST]** höchstens **einen Befund** pro Approval-Zyklus auflösen; dem Operator wird der Befund und der vorgeschlagene Edit (als Unified Diff) gezeigt, und er **MUSS [MUST]** zustimmen, bevor der Edit auf Platte landet
- **MUSS [MUST]** jeden Aspekt des Artefakts, der nicht vom genehmigten Befund abgedeckt ist, erhalten: umliegende Absätze, Frontmatter, Code-Blöcke, Link-Ziele, Heading-IDs, datei-relative Pfade
- **DARF NICHT [MUST NOT]** mehrere Befunde still zu einem Edit kombinieren; eine Mehr-Befund-Korrektur ist eine Sequenz von `patch`-Operationen, nicht eine einzige
- **MUSS [MUST]** einen „skip"- und einen „skip-and-record"-Pfad anbieten, sodass der Operator einen Befund aufschieben oder dauerhaft verwerfen kann; eine notierte Verwerfung wird so persistiert, dass künftige `audit`-Läufe sie nicht erneut surfacen
- **SOLLTE [SHOULD]** Befunde dem Operator in Severity-Reihenfolge präsentieren, sodass `critical`-Punkte zuerst behandelt werden

#### Operation C: `revise`

- **MUSS [MUST]** das **gesamte Artefakt** in einem Zug umschreiben und dabei jeden `critical`- und `warning`-Befund auflösen, den der vorherige `audit` produzierte; `suggestion`-Befunde sind optional und **SOLLTEN [SHOULD]** dann adressiert werden, wenn ihre Übernahme den Rewrite-Umfang nicht ausweitet
- **MUSS [MUST]** einen **Unified Diff** des vorgeschlagenen Voll-Rewrites produzieren und den Rewrite **DARF NICHT [MUST NOT]** auf Platte schreiben, bevor der Operator den Diff explizit genehmigt
- **MUSS [MUST]** **semantischen Inhalt erhalten**: jede Tatsache, jede Aussage, jeder Befehl, jeder Identifier, jedes Link-Ziel, jeder Frontmatter-Key, jeder Code-Block des Originals **MUSS [MUST]** im Rewrite weiterhin vorhanden sein, mit höchstens lexikalischen Änderungen (Aktiv, kürzere Sätze, ausgesprochene Vorbedingungen)
- **DARF NICHT [MUST NOT]** einen Abschnitt streichen, einen Listenpunkt droppen, einen Checklisten­eintrag droppen, eine Tabellenzeile droppen oder einen Code-Block verändern; strukturelle Löschungen sind außerhalb des `revise`-Scopes und sind eine getrennte Operator-Entscheidung
- **DARF NICHT [MUST NOT]** neue Sach­inhalte einführen (neue Befehle, neue Dateipfade, neue Produktnamen, neue URLs), die im Original nicht standen; wenn die Prosa eine Ergänzung erforderte, **MUSS [MUST]** die Operation einen `suggestion` an den Operator surfacen und stoppen
- **MUSS [MUST]** auf dem überarbeiteten Artefakt erneut `audit` ausführen und alle **neuen** Befunde surfacen, die der Rewrite eingeführt hat; wenn der Post-`revise`-`audit` mehr Gesamt-Befunde zeigt als der Pre-`revise`-`audit`, ist die Operation eine **Regression** und der Operator **MUSS [MUST]** vor der Diff-Genehmigung darauf hingewiesen werden

### Audience-Bindung

- **MUSS [MUST]** das von `audience-identification` produzierte **Audience-Artefakt** aus seinem kanonischen Ort lesen (`AUDIENCES.md` am Root des Bounded Context gemäß `audience-identification` §Anforderungen) oder einem der dort deklarierten Alternativ-Orte (README-Abschnitt "## Audiences" / "## Intended consumers", oder ein ADR); wenn an keinem dieser Orte ein solches Artefakt existiert, **MUSS [MUST]** `Lektorat` mit einer Ein-Satz-Fehlermeldung stoppen, die auf die `audience-identify`-Skill zeigt — statt Audiences zu raten
- **MUSS [MUST]** für jedes Artefakt die **anwendbaren Audiences** wie folgt auflösen (in Priorität):
  1. Seiten-Frontmatter `audience:`-Wert (ein oder mehrere Audience-IDs aus dem Artefakt) — für MkDocs-Seiten mit angewendetem `docs-audience-tracks`-Frontmatter
  2. Artefakt-Typ-Defaults, abgeleitet aus dem `track`-Feld, das `audience-identification` §Anforderungen auf jedem Audience-Eintrag verlangt:
     - `README.md` → jede im Artefakt gelistete Audience (das README ist der universelle Einstieg und bedient jede Leser-Kategorie)
     - `ONBOARDING.md`, `CONTRIBUTING.md`, GitHub-Issue-Bodys, GitHub-Pull-Request-Bodys → Audiences mit `track` = `developer-docs` (typischerweise Contributors, Operators, Maintainers, Release-Manager)
     - GitHub-Release-Note-Bodys → die in `spec/project/release-notes-audience-analysis/` aufgezählten Audiences, das ist der autoritative Resolver für diese Fläche
     - `SECURITY.md`, `CHANGELOG.md` → jede im Artefakt gelistete Audience (beide Flächen adressieren jeden Leser)
  3. Den **vollen Audience-Satz** des Artefakts — für jedes In-Scope-Artefakt, das die ersten beiden Regeln nicht matchen
- **MUSS [MUST]** `audience`-Werte sprachübergreifend als **stabile Identifier** behandeln; eine Audience-ID wird nie lokalisiert (passt zu `docs-multilingual-authoring` §Strukturelle Parität der Übersetzung)
- **DARF [MAY]** den `audience-review`-Agent dispatchen, um eine **Zweitlese** dazu zu erhalten, ob der deklarierte Audience-Satz eines Artefakts noch passt (z.B. wenn ein `D5`-Register-Mismatch-Befund nahelegt, dass die deklarierte Audience die falsche ist); der Dispatch ist **opt-in** pro Repository und die Agent-Ausgabe ist beratend

### Sprach-Handhabung

- **MUSS [MUST]** das Regelwerk **pro Datei** anhand der Dateisprache wählen, aufgelöst in dieser Priorität:
  1. Pfadsegment unter `docs/<lang>/` — `docs/en/foo.md` ist Englisch, `docs/de/foo.md` ist Deutsch
  2. Suffix-Konvention — `foo.en.md` ist Englisch, `foo.de.md` ist Deutsch
  3. Repository-Default aus `spec/.spec-config.yml` (`canonical_language`) — für Top-Level-Markdown ohne Sprachsegment (`README.md` löst typischerweise auf die canonical-Sprache auf)
  4. Im letzten Fall wählt der Operator interaktiv; `Lektorat` **DARF NICHT [MUST NOT]** die Sprache aus dem Text-Inhalt für Scope-Entscheidungen autodetektieren
- **MUSS [MUST]** **englisch-only-Mechanik** (Vale, prose-style §Voice and tone, FRE/FKGL) auf englisch-aufgelöste Dateien anwenden und **deutsch-only-Mechanik** (DE-Rechtschreib/Grammatik-Pipeline, WSTF/LIX, deutsche Ton-Heuristiken) auf deutsch-aufgelöste Dateien
- **MUSS [MUST]** YAML-Frontmatter, umzäunte Code-Blöcke, Inline-Code-Spans, HTML-Kommentare und Markdown-Link- / Bild-Ziele aus der Prosa entfernen, **bevor** der Text an eine satzweise Grammatik-Pipeline geht (Vale auf Englisch, die DE-Pipeline auf Deutsch); die entfernten Tokens **MÜSSEN [MUST]** byte-restlos entfernt werden (keine Ersetzung durch Whitespace), damit die Pipeline Strip-Artefakte nicht als Typografie-Befunde interpretieren kann. Die Zeilennummerierung des gestrippten Textes **MUSS [MUST]** auf die Quelldatei zurückführbar bleiben (Leerzeilen stehen für entfernte strukturelle Elemente), damit Befund-Positionen operator-auditierbar bleiben
- **MUSS [MUST]** die folgenden Klassen vor jeder sprach-mechanischen Korrektur in jeder Operation schützen: Code-Blöcke (gemäß §Geltungsbereich), Inline-Code, URL-Ziele, Kommandozeilen-Aufrufe, Dateipfade, identifier-artige Tokens (`camelCase`, `snake_case`, `kebab-case`-Sequenzen, die sichtbar Identifier sind), im Audience-Artefakt oder in der Geschützte-Begriffe-Liste deklarierte Produktnamen sowie Eigennamen aus denselben Quellen
- **DARF NICHT [MUST NOT]** eine nicht-englische Passage innerhalb einer englisch-aufgelösten Datei umschreiben (oder umgekehrt); eine solche Passage ist ein Befund (`D3` für Rechtschreibung, `D5` für Register), und die Auflösung wird **dem Operator geflaggt**, nicht still korrigiert
- **MUSS [MUST]** die gewählte DE-Pipeline in der `Lektorat`-lokalen Konfiguration als `{tool: <name>, version: <version>, configured_path: <Endpoint-oder-Binary-Pfad>}` aufzeichnen, sodass der Operator einen Lauf reproduzieren kann; der **Portfolio-Default** ist die **LanguageTool HTTP API** (`tool: "languagetool-http"`, mit `configured_path` entweder auf den Public-Endpoint `https://api.languagetool.org/v2` oder eine selbst gehostete Bereitstellung derselben Engine zeigend — der API-Vertrag ist in beiden Formen identisch). Ein Repository **KANN [MAY]** den Default überschreiben, indem es ein alternatives Werkzeug in seiner `Lektorat`-lokalen Konfiguration pinnt; der lastentragende Vertrag ist die in §Outputs deklarierte JSON-Ausgabe-Form, nicht die Werkzeug-Identität

### Refactor-Sicherheit

- **MUSS [MUST]** den **wörtlichen Text jedes Blockzitats** (`> …`) und den **wörtlichen Text jedes HTML-Kommentar-Markers** (`<!-- … -->`) über jede Operation hinweg erhalten; beide Klassen sind paraphrasierungs-tabu
- **MUSS [MUST]** **Linktext und Linkziel** jedes Markdown-Links erhalten, außer die Befund-Auflösung schlägt explizit eine Linkänderung vor; der sichere Default-Pfad ist `[text](target)` → `[text](target)` byte-identisch
- **MUSS [MUST]** **Heading-IDs** erhalten (der Slug, den MkDocs aus dem Überschriftstext ableitet); wenn ein Befund eine Heading-Text-Änderung erfordert, **MUSS [MUST]** die Operation surfacen, dass sich der Heading-Slug ändert, und den Operator zur Bestätigung auffordern — Slug-Drift bricht Deeplinks von anderen Seiten
- **MUSS [MUST]** **Frontmatter-Key-Set und -Reihenfolge** erhalten; Werte dürfen nur von einer Operation editiert werden, deren Befund explizit einen Frontmatter-Wert adressiert (typischerweise ein `D5`-Audience-Binding-Befund)
- **MUSS [MUST]** **eingebettete Include-Direktiven** des `mkdocs-include-markdown-plugin` byte-identisch erhalten; die eingebundene Quelle wird geprüft, wenn ihre eigene Datei im Scope ist — nicht über die konsumierende Seite
- **DARF NICHT [MUST NOT]** Listenpunkte in irgendeiner Operation umordnen, zusammenführen oder aufsplitten; lexikalische Edits innerhalb eines Bullets sind erlaubt, strukturelle Edits über Bullets hinweg nicht
- **DARF NICHT [MUST NOT]** Leerzeilen einführen oder entfernen, die das Markdown-Rendering verändern (Trenner zwischen Absätzen und Listen, Trenner zwischen Heading und Folge-Inhalt)

### Ausgaben

#### Befunde-Report (maschinenlesbar)

- **MUSS [MUST]** neben jeder Operation, die Befunde produziert (`audit` immer, `patch` und `revise` für den umschlossenen Pre-`audit` und Post-`audit`), einen Befunde-Report in **JSON** emittieren
- **MUSS [MUST]** diese Top-Level-Form verwenden:

  ```json
  {
    "operation": "audit",
    "operation_version": "1",
    "repository": "<kurzer Repo-Identifier>",
    "ran_at": "<RFC 3339 UTC-Timestamp>",
    "language_summary": [{"language": "en", "files": 12}, {"language": "de", "files": 11}],
    "pipeline_metadata": {
      "en": {
        "tool": "vale",
        "version": "<Ausgabe von `vale --version`>",
        "configured_path": "<repo-relativer Pfad zur aktiven .vale.ini oder vale.yml>"
      },
      "de": {
        "tool": "languagetool-http",
        "version": "<Wert von LanguageTool /v2/info `buildDate` oder das selbst gehostete Release-Tag>",
        "configured_path": "<HTTP-Endpoint-URL (Public oder self-hosted) oder, bei alternativem Werkzeug, der aufgelöste Binary-Pfad>"
      }
    },
    "inventory_findings": [
      {
        "kind": "vale-unavailable|language-pipeline-missing|language-ambiguous|content-mode-missing|audience-artefact-missing",
        "language": "en|de|null",
        "file": "<repo-relativer Pfad, oder null wenn die Bedingung repository-weit ist>",
        "message": "<Ein-Satz-Beschreibung für den Operator, ≤ 240 Zeichen>"
      }
    ],
    "findings": [
      {
        "id": "<stabiler Hash aus Datei + Dimension + Zeile>",
        "severity": "critical|warning|suggestion",
        "dimension": "D1|D2|D3|D4|D5",
        "file": "<repo-relativer Pfad>",
        "line_start": 1,
        "line_end": 1,
        "message": "<Ein-Satz-Befund>",
        "rule": "<Regel- oder Metrik-Identifier>",
        "language": "en|de",
        "audience": ["<audience id>", "..."],
        "evidence": "<verstoßendes Beispiel, ≤ 240 Zeichen>",
        "suggested_resolution": "<Ein-Zeilen-Operator-Hinweis, ≤ 240 Zeichen>"
      }
    ]
  }
  ```

- **MUSS [MUST]** `pipeline_metadata.<sprache>` für jede in `language_summary` vertretene Sprache befüllen, deren Pipeline aufgelöst werden konnte; die drei Unterfelder `tool`, `version` und `configured_path` sind sämtlich erforderlich und lasttragend für das Reproduzierbarkeits-Akzeptanzkriterium. Platzhalter-Werte sind verboten — wenn eines der drei nicht auflösbar ist (z. B. die Binary fehlt), wird der entsprechende `pipeline_metadata.<sprache>`-Block **weggelassen** und der Scan-Zustand stattdessen in `inventory_findings` aufgezeichnet (siehe unten)
- **MUSS [MUST]** jede Infrastruktur-Level-Scan-Bedingung im Array `inventory_findings` surfacen, **niemals** in `findings`. Das `findings`-Array trägt ausschließlich redaktionelle Befunde, klassifiziert nach der closed-Severity-Menge (`critical` / `warning` / `suggestion`) aus §Severity-Klassifikation; `inventory_findings` trägt Vorbedingungen, die einen Teil des Scans verhindert haben. Das `kind`-Feld ist eine geschlossene Aufzählung mit genau diesen fünf Werten:
  - `vale-unavailable`: Vale-Binary nicht aufrufbar, obwohl englische Dateien im Scope sind; D3/D4-EN-Mechanik wird übersprungen. `file: null`.
  - `language-pipeline-missing`: deutsche Dateien sind im Scope, aber keine DE-Pipeline-Konfiguration wurde übergeben (oder der konfigurierte Endpoint/die Binary ist nicht aufrufbar); D3 für die betroffene Datei wird übersprungen. `file` benennt die betroffene Datei; pro betroffener Datei ein Eintrag.
  - `language-ambiguous`: die Sprach-Auflösungs-Prioritätenkette (siehe §Sprach-Handhabung) kann die Datei nicht auflösen; der Operator entscheidet interaktiv. `file` benennt die betroffene Datei.
  - `content-mode-missing`: die Datei ist eine Seite im `docs/<lang>/`-Baum, die keinen `content_mode` in der Caller-übergebenen Map hat; D1 für diese Datei wird übersprungen (die `meta`-Ausnahme hängt von einem bekannten Mode ab). `file` benennt die betroffene Datei. Top-Level-Repository-Markdown (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `ONBOARDING.md`) erzeugt diesen Inventory-Befund **nicht** — es defaultet gemäß §D1 auf `content_mode: meta`, unabhängig davon, ob ein Frontmatter-Key vorhanden ist.
  - `audience-artefact-missing`: der Audience-Artefakt-Pfad löst sich zu nichts auf; D5 wird für jede Datei im Scope übersprungen. `file: null`.
- **DARF NICHT [MUST NOT]** weitere `kind`-Werte ohne vorherige Änderung dieser Spec einführen; ein unbekanntes `kind` in `inventory_findings` ist ein Spec-Konformitäts-Verstoß, kein Erweiterungspunkt
- **MUSS [MUST]** `id` über Läufe hinweg stabil halten für denselben Befund auf derselben Datei/Zeile/Dimension, sodass eine Verwerfung per `id` aufgezeichnet werden kann
- **MUSS [MUST]** zusätzlich eine **menschenlesbare** Markdown-Zusammenfassung (severity-sortiert) für den Operator-Review emittieren; JSON ist für Maschinen, Markdown ist für Menschen
- **SOLLTE [SHOULD]** beide Ausgaben unter `.audits/lektorat/<YYYY-MM-DD-HHMM>/` schreiben, sodass ein Repository einen prüfbaren Audit-Verlauf akkumuliert (spiegelt `spec/project/spec-drift-audit/` und ähnliche geschichtete Audits)
- Das `.audits/lektorat/`-JSON ist der **Vertrag**; das Rendern von Befunden als **Pull-Request-Zeilenkommentare** (oder CI-Annotationen) ist für diese Spec ausdrücklich **außerhalb des Scopes** und eine nachgelagerte CI-/Rendering-Entscheidung über jenem JSON — konsistent damit, wie die übrigen Audit-Specs des Portfolios ihren On-Disk-Audit-Verlauf als das Liefergut behandeln

#### Edit-Diff (für `patch` und `revise`)

- **MUSS [MUST]** jeden vorgeschlagenen Edit als **Unified Diff** gegen das Artefakt auf Platte präsentieren, mit mindestens drei Kontextzeilen, vor jedem Write
- **DARF NICHT [MUST NOT]** einen `patch`-Edit mit einem `revise`-Edit in einem einzigen Diff kombinieren; eine Operation, ein Diff
- **MUSS [MUST]** den Diff mit dem Operationsnamen, der/den adressierten Befund-ID(s) und dem repo-relativen Pfad der betroffenen Datei beschriften

### Skill- und Agent-Aufteilung (Empfehlung)

Die Spec lässt die Implementierungsform bewusst **offen**, **SOLLTE [SHOULD]** aber als der folgende Split umgesetzt werden, der dem hybriden Portfolio-Muster entspricht (zum Beispiel `dependency-audit`-Skill + `dependency-audit-scanner`-Agent, `vocab-drift-audit`-Skill + `vocab-drift-scanner`-Agent):

- **`lektorat-apply`-Skill** — User-Facing Einstieg; orchestriert `audit` / `patch` / `revise`; verantwortet alle Operator-Dialoge (Approvals, Verwerfungen, Sprach-Disambiguierung); komponiert die finalen Ausgaben; liest für den Audit-Schritt selbst keine Quelldateien
- **`lektorat-scanner`-Agent** — Read-only-Scanner; führt D1–D5-Erkennung über ein oder mehrere In-Scope-Artefakte aus; gibt das strukturierte Befunde-Inventar zurück, das die Skill rendert; ediert nie, fragt nie
- Die Skill **DARF [MAY]** den vorhandenen `prose-vale-curator`-Agent für D3/D4-Mechanik auf englischem Text und den `audience-review`-Agent für beratende D5-Zweitlesen dispatchen; beide Dispatches sind **opt-in** pro Repository
- Als Default-Erstimplementierungsform **SOLLTE [SHOULD]** die Skill `lektorat-scanner` einmal für den gesamten In-Scope-Satz dispatchen (gebatcht), dabei `language_summary` pro Sprache aggregieren und die Vale-Regel-ID-Deduplikation aus §Koordination in einem Durchlauf anwenden; Per-Datei-Dispatch (optional parallel) bleibt zulässig und erzeugt identisches JSON, und ein Repository **DARF [MAY]** ihn übernehmen, sobald ein gemessenes Audit zeigt, dass gebatchte Latenz oder Kosten nicht akzeptabel sind

### Koordination mit Nachbarspecs

- **MUSS [MUST]** `spec/project/prose-style/` als autoritative Quelle für EN-Voice/Tone-Regeln und Vale-Mechanik referenzieren; `Lektorat` konsumiert sie und **DARF NICHT [MUST NOT]** sie neu definieren
- **MUSS [MUST]** `spec/project/audience-identification/` als autoritative Quelle für Audience-Identifier und Audience-Eigenschaften referenzieren; `Lektorat` liest das Artefakt und **DARF NICHT [MUST NOT]** Audiences erfinden
- **MUSS [MUST]** `spec/project/docs-audience-tracks/` für den Per-Seite-`audience`/`track`/`content_mode`-Frontmatter-Vertrag referenzieren; `Lektorat` löst anwendbare Audiences darüber auf
- **MUSS [MUST]** `spec/project/mkdocs-structure/` für das `content_mode`-Enum referenzieren, das die Lesbarkeits-Korridore treibt, und für die `_`-präfigierte Snippet-Ordner-Konvention
- **MUSS [MUST]** `spec/project/docs-multilingual-authoring/` für den sprachübergreifenden Paritätsvertrag referenzieren; `Lektorat` **DARF NICHT [MUST NOT]** Übersetzungen synchronisieren
- **MUSS [MUST]** `spec/project/docs-freshness/` für die sprachübergreifende Drift-Erkennung referenzieren; `Lektorat` **DARF NICHT [MUST NOT]** Paritäts-Drift erkennen
- **MUSS [MUST]** jeden D3- oder D4-Befund auf **jeder EN-Datei im Lint-Scope von `prose-style`s Vale** (Top-Level-Markdown, `docs/en/`-Seiten, EN-PR-Bodys, EN-Release-Note-Bodys), den das Vale-CI-Gate von `prose-style` bereits surfaced hat — identifiziert durch das `rule`-Feld, das die Vale-Regel-ID trägt —, als konsumiert behandeln; `Lektorat` **DARF NICHT [MUST NOT]** denselben Befund (gleiche Vale-Regel-ID, gleiche Datei) erneut als eigenen Befund surfacen. Die Deduplikation ist einseitig: Vale prüft die Prosa zuerst, `Lektorat` ergänzt darüber hinaus die D1/D2/D5-Dimensionen und die DE-seitige D3/D4-Mechanik
- **DARF NICHT [MUST NOT]** eine MUSS-Aussage aus den obigen Specs überschreiben, abschwächen oder duplizieren; Konflikte werden durch Änderung der stromaufwärtigen Spec gelöst, nicht durch Ausnahme in `Lektorat`

## Akzeptanzkriterien

- [ ] Die `languages`-Liste aus `spec/.spec-config.yml` wird von jeder `Lektorat`-Operation gelesen und treibt die Datei-zu-Sprache-Auflösung gemäß §Sprach-Handhabung
- [ ] Ein `audit`-Aufruf gegen ein repräsentatives bilinguales Repository produziert einen JSON-Report, dessen Form §Ausgaben wörtlich entspricht (Top-Level-Keys, Finding-Objekt-Keys, Severity-Werte aus der geschlossenen Menge)
- [ ] Ein `audit`-Aufruf produziert neben dem JSON eine Markdown-Zusammenfassung, sortiert nach Severity (`critical` zuerst), und schreibt beides unter `.audits/lektorat/<YYYY-MM-DD-HHMM>/`
- [ ] Ein `audit`-Aufruf läuft ohne Operator-Interaktion durch (CI / pre-commit / sprint-review-tauglich)
- [ ] Ein Re-Run desselben `audit`-Aufrufs erzeugt auf einem unveränderten Repository ein byte-identisches `findings`-Array (modulo `ran_at`)
- [ ] Eine englische Datei produziert mindestens einen D1-Befund, wenn Flesch Reading Ease unter ihren content-mode-Korridor fällt — mit Metrik-Wert und Korridor im Befund
- [ ] Eine deutsche Datei produziert mindestens einen D1-Befund, wenn WSTF ihren content-mode-Korridor überschreitet — mit Metrik-Wert und Korridor im Befund
- [ ] Eine Seite, deren `content_mode` `meta` ist, produziert **keinen** D1-Befund (die Meta-Ausnahme wird beachtet)
- [ ] Eine Top-Level-Markdown-Datei ohne `content_mode`-Frontmatter-Key (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `ONBOARDING.md`) wird ausschließlich für D1 als `content_mode: meta` behandelt; die Datei erzeugt **keinen** `content-mode-missing`-Inventory-Befund
- [ ] Eine Datei mit einer ungeklärten Abkürzung produziert mindestens einen D2-Befund, der die Abkürzung, die fehlende Auflösung und die Zeile der Erstnennung benennt
- [ ] Eine Datei mit einer versteckten Vorannahme (eine Anweisung, die auf ein Werkzeug oder einen Umgebungszustand verweist, der auf der Seite nicht erwähnt ist) produziert einen D2-Befund, der die fehlende Voraussetzung identifiziert
- [ ] Ein Jargon-Last-D2-Befund in einem Artefakt auf publizierter Fläche (`README.md`, Release-Note-Body, Top-Level-Docs), dessen aufgelöste Audience eine Nicht-Operator-Rolle enthält, wird `critical` klassifiziert; derselbe Jargon-Last-Befund in einem internen Entwurfs-Doc oder in einer publizierten Fläche mit Operator-only-Audience bleibt `warning` (D2-Jargon-Last-Eskalation honoriert)
- [ ] Ein D2-Befund zu einer ungeklärten Abkürzung, deren Abkürzung in einer Überschrift, im ersten Absatz oder in einem Callout erscheint, wird `critical` klassifiziert; dieselbe Abkürzung, die nur in einem späteren Body-Absatz erscheint, bleibt `warning` (D2-Abkürzungs-Eskalation honoriert)
- [ ] Ein D2-Befund zu einer versteckten Vorannahme auf einer Seite mit `content_mode` `tutorial` oder `how-to` wird `critical` klassifiziert; derselbe Befund auf einer `reference`- oder `explanation`-Seite bleibt `warning` (D2-Vorannahme-Eskalation honoriert)
- [ ] Ein D2-Befund zu einer impliziten Annahme, dessen Markerwort („einfach", „nur", „offensichtlich") mit einem Schritt gepaart ist, den die Leserschaft ausführen muss, wird `warning` klassifiziert; dasselbe Markerwort in einem nicht-imperativen Kontext bleibt `suggestion` (D2-Implizite-Annahme-Eskalation honoriert)
- [ ] Ein D3-Rechtschreibbefund für eine englische Datei stammt aus Vale (gemäß `prose-style`) und ist in `Lektorat` nicht neu implementiert
- [ ] Ein D3-Rechtschreibbefund für eine deutsche Datei stammt aus einer `Lektorat`-eigenen DE-Pipeline, deren `tool`-Name, `version` und `configured_path` sämtlich in `pipeline_metadata.de` der JSON-Ausgabe des Laufs vermerkt sind
- [ ] Ein D3-Tippfehler in einem publizierten Artefakt (`README.md`, Release-Note-Body, Top-Level-Docs) wird als `critical` klassifiziert; derselbe Tippfehler in einem Markdown-Kommentar als Entwurf wird als `warning` klassifiziert; dieselbe Zeichenkette innerhalb eines Code-Identifiers erzeugt keinen Befund (dimensions­bewusste Severity wird beachtet)
- [ ] Eine Datei mit gemischtem Voice (Aktiv/Passiv-Wechsel in benachbarten Sätzen), gemischtem Tempus oder gemischter Anrede (`du`/`Sie`-Wechsel) produziert mindestens einen D4-Inkonsistenz-Befund innerhalb desselben Artefakts
- [ ] Eine Seite, die einen Frontmatter-`audience:`-Wert deklariert, der vom Artefakt-Typ-Default für ihren Pfad abweicht, löst auf den Frontmatter-Wert auf (Prioritäts-Regel 1 schlägt Regel 2); eine Datei ohne Frontmatter und ohne passenden Artefakt-Typ-Default löst auf den vollen Audience-Satz auf (Regel 3 greift)
- [ ] Ein `patch`-Aufruf wendet genau einen Befund pro Approval-Zyklus an und surfaced einen Unified Diff vor jedem Write
- [ ] Ein `patch`-Aufruf bietet einen „skip"- und einen „skip-and-record"-Pfad; eine notierte Verwerfung erscheint in nachfolgenden `audit`-Läufen nicht erneut
- [ ] Ein `revise`-Aufruf produziert einen Unified Diff des Voll-Rewrites, löst jeden `critical`- und `warning`-Befund des vorherigen `audit` auf und verweigert den Write bis zur Operator-Zustimmung
- [ ] Ein `revise`-Aufruf führt auf dem Rewrite erneut `audit` aus und flaggt den Lauf als **Regression**, wenn die Post-`revise`-Gesamt-Befundzahl höher ist als die Pre-`revise`-Zahl
- [ ] Ein `revise`-Aufruf erhält jeden Code-Block, jeden Frontmatter-Key, jedes Link-Ziel, jede Heading-ID und jeden HTML-Kommentar byte-identisch zum Original
- [ ] Ein `revise`- oder `patch`-Aufruf erhält den wörtlichen Text jedes Blockzitats (`> …`) byte-identisch zum Original
- [ ] Ein `revise`- oder `patch`-Aufruf erhält Reihenfolge und Anzahl jedes Listenpunkts, jeder Tabellenzeile und jedes Checklisten­eintrags; lexikalische Edits innerhalb eines Eintrags sind erlaubt, strukturelle Cross-Eintrag-Edits nicht
- [ ] Eine Datei unter `spec/` wird von jeder `Lektorat`-Operation mit einer Ein-Satz-Meldung abgelehnt, die die `spec`-Skill als autoritativen Pfad nennt
- [ ] Eine Datei unter `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**` oder `agents/*.md` wird von jeder `Lektorat`-Operation abgelehnt
- [ ] Ein Zielgruppen-Fit-Befund (D5) nennt genau eine Audience-ID aus dem Audience-Artefakt und referenziert den Artefakt-Pfad
- [ ] Wenn das Audience-Artefakt fehlt, stoppt jede `Lektorat`-Operation mit einer Meldung, die auf die `audience-identify`-Skill zeigt, und **DARF NICHT [MUST NOT]** Audiences erfinden
- [ ] Jeder Markdown-Link `[text](target)` ist byte-identisch über jede Operation hinweg, die nicht explizit einen Befund gegen diesen Link produziert
- [ ] Jede Heading-Text-Änderung, die ein `patch`- oder `revise`-Lauf surfaced, kündigt dem Operator den Slug-Wechsel vor der Write-Zustimmung an

## Offene Fragen

- Soll `Lektorat` seinen Scope auf **API-Referenz-Text aus Quellcode** (typedoc, sphinx, godoc-Output) ausweiten? Erneut bewerten, sobald ein `nolte/*`-Portfolio-Repository eine generierte API-Referenz-Site liefert (typedoc/sphinx/godoc-Output, gerendert nach `docs/`), deren Seiten-Frontmatter `audience:` gemäß Audience-Artefakt auf mindestens eine Nicht-Entwickler-Audience-ID auflöst (Track anders als `developer-docs`). Das stromaufwärtige Signal, auf das zu achten ist, ist die Autorschaft der ersten `library-api-docs`-artigen mkdocs-structure-Erweiterungsspec (in [`spec/project/mkdocs-structure/`](../mkdocs-structure/de.md) §Discovery and cross-referencing als künftige Erweiterung benannt) — dann steht eine Nicht-Entwickler-Referenz-Fläche bevor. Bis ein solches Repo existiert, gibt es keine Nutzungsdaten, um gegen den geltenden Default **nein** zu entscheiden (generierter Referenz-Text ist bereits durch §Geltungsbereich und Anwendbarkeit und die §Nicht-Ziele-Markdown-Prosa-Grenze ausgeschlossen).
- Soll der `lektorat-scanner`-Agent **parallel pro Datei** dispatchbar sein oder **gebatcht** (ein Agent-Run für das ganze Repository)? Default: gebatcht dispatchen (ein Scanner-Run für den gesamten In-Scope-Satz pro Audit), die Variante mit geringerem Overhead, die `language_summary` aggregiert und die Vale-Regel-ID-Deduplikation aus §Koordination in einem Durchlauf anwendet; Per-Datei-Dispatch (optional parallel) bleibt zulässig und erzeugt identisches JSON. Erneut bewerten, sobald das erste reale `audit` gegen ein repräsentatives bilinguales Repo (mindestens 20 In-Scope-Markdown-Dateien über `docs/en` + `docs/de`) einen Wall-Clock- und Token-Kosten-Vergleich von gebatchtem versus Per-Datei-Dispatch aufzeichnet, der gebatchte p95-Latenz über einer operator-akzeptablen Grenze (Vorschlag: über 5 Minuten pro Audit) oder Token-Kosten pro Audit über der Per-Datei-Parallel-Alternative um eine messbare Marge zeigt. Es existiert ein editorialer `audit`-Lauf (`.audits/lektorat/2026-05-30-0727`), der jedoch keinen Vergleich von gebatchtem versus Per-Datei-Dispatch aufzeichnet; die Revisit-Bedingung ist damit unerfüllt und der gebatchte Default steht.

## Quellen

<!-- Autoritative externe Referenzen, gegen die die obigen Anforderungen geprüft sind. -->

- Flesch, R. (1948). *A new readability yardstick.* Journal of Applied Psychology — Originaldefinition von Flesch Reading Ease.
- Kincaid, J. P., Fishburne, R. P., Rogers, R. L., Chissom, B. S. (1975). *Derivation of new readability formulas.* Definiert den Flesch–Kincaid Grade Level.
- Bamberger, R., Vanecek, E. (1984). *Lesen — Verstehen — Lernen — Schreiben.* Definiert die Wiener-Sachtextformel-Varianten (WSTF).
- Björnsson, C. H. (1968). *Läsbarhet.* Definiert LIX (Läsbarhetsindex); per Lesbarkeits-Forschung übertragbar auf Deutsch.
- Microsoft Writing Style Guide (learn.microsoft.com/style-guide) — Voice, Tone, Bias-Free Communication; konsumiert via `spec/project/prose-style/`.
- Microsoft Localization Style Guides — Deutsch (learn.microsoft.com/de-de/globalization/localization/styleguides) — DACH-Konventionen für Kontraktionen und Anredeformen.
- Google Developer Documentation Style Guide (developers.google.com/style) — Audience- und Voice-Prinzipien; konsumiert via `spec/project/prose-style/`.
- Diátaxis (diataxis.fr) — das `content_mode`-Enum (`tutorial` / `how-to` / `reference` / `explanation`), das die `Lektorat`-Lesbarkeits-Korridore treibt; konsumiert via `spec/project/mkdocs-structure/`.
