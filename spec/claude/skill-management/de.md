# Claude-Skill-Autorenschaft

Status: draft

## Kontext
Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents, die von nachgelagerten Projekten genutzt werden. Ein Skill hat zwei Ausprägungen: eine **Quell-Form** in diesem Repository (unter `skills/`) und eine **Laufzeit-Form** in einem konsumierenden Projekt, aus der Claude Code den Skill tatsächlich lädt. Der einzige unterstützte Verteilungsweg für die Laufzeit ist der Claude-Code-Plugin-Mechanismus: Dieses Repository ist selbst ein Claude-Code-Plugin (`.claude-plugin/plugin.json` plus Marketplace-Eintrag), und konsumierende Projekte erhalten Skills, indem sie das Plugin installieren. Ohne einheitliche Form und einen einzigen Verteilungspfad driften Skills in Benennung, Trigger-Beschreibungen und interner Struktur auseinander, und Konsumenten landen bei ad-hoc Kopien oder Symlinks, die mit der Zeit divergieren. Diese Spezifikation definiert, wie neue Skills erstellt werden, wie sie verteilt werden und woran sich bestehende Skills halten müssen.

## Ziele
- Jeder Skill hat dieselbe vorhersehbare Form auf der Festplatte
- Skills sind für Claude über präzise, trigger-orientierte Beschreibungen auffindbar
- Skills sind portabel über jedes Projekt, das claude-shared konsumiert, ohne versteckte Abhängigkeiten
- Autoren haben eine klare Checkliste und ein Template als Startpunkt

## Nicht-Ziele
- Einrichtung nachgelagerter Projekte und `.claude/`-Konfiguration jenseits der Plugin-Installation
- Vorgabe konkreter Skill-Inhalte jenseits struktureller Regeln
- Die konkrete Marketplace- / Plugin-Installations-UX von Claude Code (wird von Claude Code selbst verantwortet, nicht von diesem Repository)

## Anforderungen

### Struktur
- **MUSS [MUST]** als Ordner mit dem Namen `<name>/` angelegt werden, wobei `<name>` ASCII-Kebab-Case ist
- **MUSS [MUST]** eine `SKILL.md` im Wurzelverzeichnis des Skill-Ordners enthalten
- **MUSS [MUST]** YAML-Frontmatter in `SKILL.md` mit den Feldern `name` und `description` enthalten
- **MUSS [MUST]** `name` exakt auf den Ordnernamen setzen
- **MUSS [MUST]** eine `description` schreiben, die konkrete Nutzer-Trigger benennt statt abstrakter Fähigkeiten, damit Claude zuverlässig über den Aufruf entscheiden kann
- **MUSS [MUST]** Anweisungen innerhalb von `SKILL.md` aus Token-Effizienzgründen auf Englisch halten; der Skill darf Claude weiterhin anweisen, dem Nutzer in dessen Sprache zu antworten
- **MUSS [MUST]** in sich geschlossen sein — unterstützende Artefakte (Templates, Referenzen, Beispiele) liegen innerhalb des Skill-Ordners
- **KANN [MAY]** ein optionales `tags`-Feld im YAML-Frontmatter enthalten: eine Liste von kleingeschriebenen ASCII-Kebab-Case-Strings, jeder ≤30 Zeichen, mit höchstens 5 Einträgen; Tags liefern thematische Gruppierung, damit Katalog (`skill-agent-catalog`) und Peer-Cluster-Abgleich (`skill-vs-agent` §Portfolio-weite Konsistenz) nach Thema durchstöbert werden können

### Frontmatter-Validierung (Agent-Skills-Spezifikation und Anthropic-Platform-Limits)

Folgt der formalen Agent-Skills-Spezifikation ([R1](#referenzen)) und den von Anthropic veröffentlichten Validierungsregeln ([R2](#referenzen)); den Source-Slug zitieren, wenn ein Finding eine konkrete Grenze pinnt.

- **MUSS [MUST]** `name` zwischen 1 und 64 Zeichen halten, nur ASCII-Kleinbuchstaben, Ziffern und Bindestriche enthalten, **DARF NICHT [MUST NOT]** mit einem Bindestrich beginnen oder enden und **DARF NICHT [MUST NOT]** aufeinanderfolgende Bindestriche (`--`) enthalten
- **DARF NICHT [MUST NOT]** die reservierten Wörter `anthropic` oder `claude` als Wert von `name` oder an irgendeiner Stelle innerhalb von `name` verwenden, gemäß Upstream-Plattform-Validator. Die Reserved-Word-Regel **gilt ausschließlich für `name`**: Beschreibende Felder wie `description` dürfen `claude` legitim erwähnen (z. B. „Claude Code skill for X"), und viele bestehende Skills tun das — eine Einschränkung von `description` würde unnatürliche Umschreibungen erzwingen („der Assistent" / „die Agent-Laufzeit") ohne Mehrgewinn beim Plattform-Validator
  - **Enge Ausnahme** für Artefakte, deren primäre Verantwortung das Authoring oder die Pflege einer Claude-Code- oder Anthropic-Plattform-Surface ist (zum Beispiel ein `claude-plugin-developer`-Agent, der Claude-Code-Plugins scaffolden soll): Das Reserved-Token-Verbot **DARF [MAY]** ausgesetzt werden, wenn der Artefakt-Body einen `## Reserved-token rationale`-Abschnitt mitführt, der die Plattform-Surface benennt und auf diese Ausnahme verweist. Der lokale Validator (`scripts/validate_skills.py`) honoriert die Ausnahme, indem er das `frontmatter-name-reserved`-Critical unterdrückt, wenn dieser Body-Abschnitt vorhanden ist; der Upstream-Anthropic-Plattform-Validator honoriert sie nicht, sodass Konsumenten, die das Artefakt durch den Upstream-Intake-Pfad routen, **MÜSSEN [MUST]** umbenennen. Diese Ausnahme tauscht die Plattform-Validator-Spiegel-Parität gegen den Discoverability-Anker, den das reservierte Token bietet; führe keine neuen Artefakte unter dieser Ausnahme ein, sofern die Verantwortung nicht echt die Claude-/Anthropic-Surface selbst betrifft
- **DARF NICHT [MUST NOT]** XML-Tags innerhalb der `name`- oder `description`-Werte enthalten
- **MUSS [MUST]** `description` nicht-leer halten und **DARF NICHT [MUST NOT]** 1024 Zeichen überschreiten
- **MUSS [MUST]** `description` in der **dritten Person** verfassen („Generates …", „Reviews …"), niemals in erster oder zweiter Person („I help …", „You can use this to …"), weil die Description in den System-Prompt von Claude injiziert wird und uneinheitliche Sprachperson die Skill-Discovery messbar verschlechtert ([R2](#referenzen))
- **MUSS [MUST]** in `description` sowohl *was der Skill tut* als auch *wann er einzusetzen ist* benennen — beide Hälften des Discovery-Vertrags; reine Capability-Aussagen ohne Trigger-Phrasen scheitern an der Discovery-Hälfte
- **SOLLTE [SHOULD]**, falls zusätzlich Claude Codes optionales `when_to_use`-Feld ([R3](#referenzen)) verwendet wird, den kombinierten Text aus `description` + `when_to_use` unter 1.536 Zeichen halten; die Laufzeit kürzt alles darüber, und die Kürzung trifft typischerweise die Trigger-Phrasen
- **SOLLTE [SHOULD]** für den Skill-Namen die **Gerundium-Form** bevorzugen (Verb + `-ing`: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`) gemäß Anthropic-Konvention; Verb-Substantiv (`process-pdfs`) und Substantiv-Phrasen (`pdf-processing`) sind akzeptable Alternativen, aber gemischte Formen innerhalb eines Repositories nicht ([R2](#referenzen))
  - **Wahl des `nolte-shared`-Plugins**: Dieses Repository liefert jeden Skill in **Verb-Substantiv-Form** aus (`pull-request-create`, `roadmap-init`, `feature-decompose`, `dependency-audit`, `quality-gate` und so weiter). Die Wahl ist hier festgehalten, damit ein Reviewer die Konvention nicht in jeder Iteration erneut bemängelt. Die bestehende Surface in die Gerundium-Form umzubenennen wäre ein Breaking Change für jeden Downstream-Konsumenten, der `subagent_type:` aufruft, und ist nicht geplant. Neue Skills in diesem Plugin **MÜSSEN [MUST]** der Verb-Substantiv-Konvention folgen; eine eingestreute Gerundium-Namensform würde selbst die "gemischte Formen sind nicht akzeptabel"-Hälfte der Upstream-Regel verletzen. Eine künftige koordinierte Portfolio-Umbenennung (mit Deprecation-Periode) **DARF [MAY]** die Wahl umkehren; bis dahin ist Verb-Substantiv die Regel
- **DARF NICHT [MUST NOT]** vage oder generische Namen verwenden: `helper`, `utils`, `tools`, `documents`, `data`, `files` — sie unterminieren Discovery, weil Claude aus dem Namen nicht erkennen kann, was der Skill tut ([R2](#referenzen))

### Tag-Vokabular
- **SOLLTE [SHOULD]** einen Begriff aus dem Starter-Vokabular unten bevorzugen, wenn einer passt, damit Artefakte desselben funktionalen Clusters denselben Tag-String teilen
- **KANN [MAY]** einen neuen Tag einführen, der der obigen Normalisierungsregel folgt, wenn kein Starter-Begriff passt; Wildwuchs vermeiden, indem bei vertretbarer Passung ein bestehender Tag wiederverwendet wird

Starter-Vokabular:
- `pull-request` — PR-Autoring, Labeling, Landen
- `review` — Spec-, Skill-, Agent- oder PR-Level-Review
- `audit` — Drift-, Compliance-, Vokabular-, Dependency-Audits
- `scaffolding` — Projektstruktur, Katalog-Verdrahtung, Skill-/Agent-Scaffolding
- `prose` — Vale-Style-Kuratierung, Schreibhilfe, Dokumentations-Prosa
- `audience` — Audience-Identifikation und daraus folgende Doku-Gestaltung
- `release` — Release-Automation, Changelogs, Versionierung
- `quality-gate` — Lint, Typecheck, Test
- `dependency` — CVE-Scans, Lizenz-Compliance, Lockfile-Hygiene

### Quell-Ablageort (Repository claude-shared)
- **MUSS [MUST]** im Quellbaum von claude-shared unter `skills/<name>/` liegen
- **MUSS [MUST]** als Bestandteil des `nolte-shared`-Claude-Code-Plugins ausgeliefert werden, das über `.claude-plugin/plugin.json` und `.claude-plugin/marketplace.json` in diesem Repository deklariert ist; kein Skill in diesem Repository existiert außerhalb des Plugin-Scopes

### Verteilung
- **MUSS [MUST]** konsumierende Projekte ausschließlich über den Claude-Code-Plugin-Mechanismus erreichen — das Plugin wird über den Marketplace-Eintrag installiert, und Claude Code findet den Skill aus dem `skills/<name>/`-Pfad des Plugins heraus
- **DARF NICHT [MUST NOT]** durch Kopieren in das `.claude/skills/<name>/`-Verzeichnis eines konsumierenden Projekts, durch Symlink, durch Vendoring oder auf irgendeinem anderen Out-of-Band-Pfad verteilt werden; solche Kopien driften gegenüber der Quelle und untergraben den Sinn eines geteilten Plugins
- **DARF NICHT [MUST NOT]** die Plugin-Version in `.claude-plugin/plugin.json` oder im zugehörigen Marketplace-Eintrag manuell als Teil eines PRs erhöhen, der einen Skill hinzufügt, umbenennt, entfernt oder seinen Vertrag wesentlich ändert; die Version wird vom veröffentlichten GitHub-Release-Tag abgeleitet und ausschließlich durch den Release-Workflow auf dem Default-Branch aktualisiert — siehe `release-automation` §Abgleich versionstragender Dateien für den Mechanismus (einschließlich des Fallback Paths, bei dem ein Maintainer einen dedizierten `chore(release): <tag>`-PR eröffnet)
- **DARF [MAY]** in einem konsumierenden Projekt neben projektlokalen Skills unter dessen eigenem `.claude/skills/` koexistieren; solche projektlokalen Skills liegen außerhalb des Scopes dieser Spec und **DÜRFEN NICHT [MUST NOT]** einen Namen wiederverwenden, der bereits im `nolte-shared`-Plugin belegt ist

### Laufzeit-Auffindbarkeit (konsumierendes Projekt)
- **MUSS [MUST]** von Claude Code aus dem Plugin-Skills-Pfad geladen werden, sobald das Plugin installiert ist; der Skill erscheint dem Nutzer als `nolte-shared:<name>`
- **DARF NICHT [MUST NOT]** irgendeinen spezifischen absoluten oder projekt-relativen Laufzeit-Pfad voraussetzen; alle internen Pfade bleiben relativ zum Skill-Ordner und funktionieren überall dort, wo Claude Code das Plugin entpackt oder einbindet

### Empfehlungen
- **SOLLTE [SHOULD]** einen Abschnitt „Hard rules" enthalten, der Invarianten auflistet, die niemals gebrochen werden dürfen
- **SOLLTE [SHOULD]** `SKILL.md` als weiches Ziel etwa unter 150 Zeilen halten; längere Inhalte in referenzierte Dateien auslagern
- **SOLLTE [SHOULD]** unterstützende Dateien in konventionelle Unterordner legen: `templates/` (oder `assets/`), `references/`, `examples/`, `scripts/`
- **KANN [MAY]** Beispiel-Nutzer-Prompts und erwartetes Verhalten in `examples/` enthalten
- **KANN [MAY]** ein kleines Konfigurationsschema enthalten, falls der Skill projektbezogene Konfiguration benötigt

### Autoren-Qualität (gemäß Anthropic-Skill-Creation-Best-Practices)

Folgt der öffentlichen Leitlinie unter <https://agentskills.io/skill-creation/best-practices> ([R4](#referenzen)) und der offiziellen Anthropic-Skill-Authoring-Seite ([R2](#referenzen)); den Source-Slug zitieren, wenn ein Finding eine konkrete Regel pinnt.

- **MUSS [MUST]** `SKILL.md` unter 500 Zeilen und 5.000 Tokens halten (Upstream-Hard-Cap, identisch in der formalen Spezifikation ([R1](#referenzen)) und der Best-Practices-Seite ([R2](#referenzen))); Inhalte darüber **MUSS** in `references/`, `templates/`/`assets/` oder `scripts/` ausgelagert werden und **MUSS** eine explizite Lade-Trigger-Formulierung („Read X when Y", „use template Z for output Q") in `SKILL.md` tragen, damit Progressive Disclosure wie vorgesehen funktioniert
- **SOLLTE [SHOULD]** einen **Gotchas**-Abschnitt enthalten, der konkrete Korrekturen zu nicht-offensichtlichen Umgebungs-Fakten auflistet, die der Agent sonst falsch annehmen würde; das ist unterschiedlich vom **Hard rules**-Abschnitt (Invarianten) und von generischen Ratschlägen ([R4](#referenzen))
- **SOLLTE [SHOULD]** die Spezifität der Anweisungen an die Fragilität der Aufgabe anpassen (Freiheit plus *Warum* für flexible Aufgaben; präskriptiv für fragile oder sequenzielle Operationen), **einen klaren Default vorgeben** statt eines Menüs gleichwertiger Optionen und **Prozeduren statt Deklarationen bevorzugen** (vermitteln, wie eine Problemklasse anzugehen ist, nicht was für eine konkrete Instanz produziert werden soll) ([R4](#referenzen))
- **SOLLTE [SHOULD]** den Skill auf realer Expertise verankern — aus einer praktischen Aufgabe extrahieren oder aus projekt-spezifischen Artefakten synthetisieren (Runbooks, Code-Review-Kommentare, Versionsgeschichte, reale Fehlerfälle) statt allein aus generischer LLM-Ausgabe ([R4](#referenzen))
- **SOLLTE [SHOULD]** den **Default-Test „Claude weiß das schon"** anwenden, bevor irgendein erklärender Absatz hinzugefügt wird — jeden Inhaltsblock prüfen mit „Braucht Claude diese Erklärung wirklich? Rechtfertigt dieser Absatz seine Token-Kosten?" und Inhalte streichen, die den Test nicht bestehen ([R2](#referenzen))
- **SOLLTE [SHOULD]** **konsistente Terminologie** im gesamten Skill verwenden: für jedes Konzept einen Begriff wählen („API endpoint" statt „URL" statt „API route") und durchziehen; gemischte Terminologie verschlechtert die Befolgung der Anweisungen messbar ([R2](#referenzen))
- **DARF NICHT [MUST NOT]** zeitabhängige Informationen enthalten, die später falsch werden (z. B. „vor August 2025 die alte API verwenden"); historischer Kontext gehört in einen expliziten `## Old patterns`-Abschnitt mit Collapsible, niemals inline ([R2](#referenzen))
- **MUSS [MUST]** Forward-Slash-Pfade (`scripts/helper.py`, `references/guide.md`) in jeder Referenz im Skill verwenden, niemals Windows-Backslashes — Unix-Pfade funktionieren überall, Windows-Pfade brechen unter Unix ([R2](#referenzen))
- **MUSS [MUST]** beim Verweis auf MCP-Tools aus Skill-Prosa heraus die voll qualifizierte `ServerName:tool_name`-Syntax verwenden (`BigQuery:bigquery_schema`, nicht `bigquery_schema`); ohne Server-Präfix scheitert die Laufzeit beim Auflösen, sobald mehrere MCP-Server vorhanden sind ([R2](#referenzen))
- **KANN [MAY]** wiederverwendbare Skripte in `scripts/` bündeln, wenn Iteration zeigt, dass der Agent dieselbe Logik in jedem Lauf neu erfindet, und **KANN** einen **Validation-Loop**- oder **Plan-Validate-Execute**-Unterabschnitt ergänzen, wenn der Skill Batch- oder destruktive Operationen ausführt ([R2](#referenzen), [R4](#referenzen))
- **SOLLTE [SHOULD]** beim Bündeln von Skripten **„solve, don't punt"** anwenden — das Skript behandelt eigene Fehlerfälle (Datei fehlt → mit Default anlegen; Permission denied → graceful Fallback) statt zu scheitern und die Wiederherstellung Claude zu überlassen ([R2](#referenzen))
- **SOLLTE [SHOULD]** jede vom Skript deklarierte Konfigurationskonstante begründen; „Voodoo-Konstanten" (`TIMEOUT = 47`, `RETRIES = 5`) ohne erklärenden Inline-Kommentar sind ein `Warning`-würdiger Authoring-Smell ([R2](#referenzen))
- **MUSS [MUST]** in jeder Prosa, die ein Skript erwähnt, die **Ausführungs-Absicht explizit machen**: entweder „Run `analyze_form.py` to extract fields" (ausführen) oder „See `analyze_form.py` for the field extraction algorithm" (als Referenz lesen); Mehrdeutigkeit hier führt dazu, dass Claude die falsche Wahl trifft und Tokens verschwendet ([R2](#referenzen))

### Progressive Disclosure und Datei-Referenzen

Skills werden von Claude in drei Stufen geladen — Metadaten beim Start (~100 Tokens pro Skill), voller `SKILL.md`-Body bei Trigger, unterstützende Dateien nur bei explizitem Lesen ([R5](#referenzen), [R1](#referenzen)). Die On-Disk-Form **MUSS** dieses Lade-Modell unterstützen.

- **MUSS [MUST]** Datei-Referenzen innerhalb von `SKILL.md` **maximal eine Ebene tief** halten: `SKILL.md` → `references/foo.md` ist ok; `SKILL.md` → `references/foo.md` → `references/bar.md` ist verboten, weil Claude bei verschachtelten Referenzen partielle Reads (`head -100`) nutzt und dadurch Inhalte verpasst ([R2](#referenzen))
- **MUSS [MUST]** ein **Inhaltsverzeichnis** an den Anfang jeder Referenzdatei setzen, die länger als 100 Zeilen ist, damit Partial-Read-Vorschauen den vollen Umfang der Datei sichtbar machen ([R2](#referenzen))
- **MUSS [MUST]**, jedes Mal wenn `SKILL.md` eine Hilfsdatei referenziert, **was die Datei enthält** und **wann sie zu laden ist** benennen (z. B. „Read `references/api-errors.md` if the API returns a non-200 status code"); ein generisches „see `references/` for details" konterkariert Progressive Disclosure, weil Claude kein Signal für *wann* Laden hat ([R2](#referenzen), [R4](#referenzen))
- **SOLLTE [SHOULD]** Hilfsdateien nach **Domäne** organisieren, wenn der Skill mehrere Bereiche überspannt (`reference/finance.md`, `reference/sales.md`, `reference/product.md`), damit jede Nutzer-Anfrage nur den relevanten Ausschnitt lädt ([R2](#referenzen))
- **SOLLTE [SHOULD]** den Skill-Scope auf eine **kohärente Arbeits-Einheit** (Funktions-Kohärenz) begrenzen: ein Skill, der „die Datenbank abfragt und Ergebnisse formatiert", ist eine Einheit; ein Skill, der „die Datenbank abfragt, formatiert und administriert", sind zwei Einheiten und sollten getrennt werden ([R4](#referenzen))

### Laufzeit- und Lifecycle-Bewusstsein (Claude Code)

Die in diesem Plugin ausgelieferten Skills laufen in Claude Code; das Verständnis des Laufzeit-Vertrags vermeidet Authoring-Fehler, die erst zur Session-Zeit auftreten.

- **MUSS [MUST]** den Body so schreiben, dass sein Inhalt als **Standing Instructions für die restliche Session** trägt, nicht als Einmal-Schritte: Nach Skill-Aufruf wird der gerenderte `SKILL.md`-Inhalt als einzelne Nachricht in die Konversation eingefügt und bleibt dort für den Rest der Session — Claude Code liest die Datei in späteren Turns **nicht** erneut ([R3](#referenzen))
- **MUSS [MUST]** Auto-Compaction überstehen: Nach Komprimierung der Konversation hängt Claude Code die jüngste Invocation jedes Skills wieder an, behält dabei nur die **ersten 5.000 Tokens** pro Skill, mit einem kombinierten Re-Attach-Budget von **25.000 Tokens** über alle invokierten Skills; SKILL.md-Inhalt jenseits der 5.000-Tokens-Marke wird stillschweigend verworfen ([R3](#referenzen)). Der 5.000-Tokens-Authoring-Cap und das 5.000-Tokens-Re-Attach-Fenster sind nicht zufällig identisch — der Skill ist nur dann komplett compaction-safe, wenn er unter dem Limit bleibt
- **KANN [MAY]** beliebige der optionalen Claude-Code-spezifischen Frontmatter-Felder ([R3](#referenzen)) deklarieren, wenn sie zutreffen: `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context: fork`, `agent`, `hooks`, `paths`, `shell`. Diese erweitern die formale Agent-Skills-Spezifikation ([R1](#referenzen)), sind aber nicht auf Nicht-Claude-Code-Laufzeiten portabel
- **MUSS [MUST]** `allowed-tools` als **Permission-Grant** behandeln (vorab genehmigte Tool-Calls, solange der Skill aktiv ist), nicht als Tool-Restriction; es schränkt nicht ein, was der Skill aufrufen darf, sondern erweitert, was ohne User-Prompt durchläuft. Project-Level-Skills mit `allowed-tools` greifen erst, nachdem der Nutzer den Workspace-Trust-Dialog akzeptiert hat ([R3](#referenzen))
- **MUSS [MUST]**, beim Setzen von `disable-model-invocation: true` für einen Skill, der nur auf explizite User-Anfrage laufen soll, akzeptieren, dass dieser Skill nicht **per `skills:`-Feld in einen Subagent vorab geladen** werden kann — Claude Code überspringt deaktivierte Skills dort und protokolliert eine Warnung ([R3](#referenzen))
- **KANN [MAY]** eine `model`-Override am Skill deklarieren (`model: opus`, `model: haiku`, `model: inherit`); die Override gilt für den Rest des aktuellen Turns und wird **nicht in den Settings persistiert** — beim nächsten Prompt setzt das Session-Modell wieder ein ([R3](#referenzen))
- **KANN [MAY]** `context: fork` zusammen mit `agent: <type>` nutzen, um den Skill in einem geforkten Subagent-Kontext laufen zu lassen (Skill-Inhalt wird zum Prompt, der genannte Agent-Typ liefert Tools und Modell). Dies ist die **Inverse** zum `skills:`-Preload-Feld eines Subagents; beide ergeben dieselbe Komposition über unterschiedliche Eigentümerschaft ([R3](#referenzen)). Wann diese Variante einer `agents/<name>.md`-Datei vorzuziehen ist, regelt `skill-vs-agent`

### Evaluations-Disziplin

- **SOLLTE [SHOULD]** **Evaluations vor ausführlicher Dokumentation aufbauen**: Lücken identifizieren, indem Claude auf repräsentativen Aufgaben ohne den Skill läuft, die spezifischen Fehler dokumentieren und dann nur die Anweisungen schreiben, die diese Lücken schließen ([R2](#referenzen))
- **SOLLTE [SHOULD]** mindestens **drei Evaluations-Szenarien** pro nicht-trivialem Skill ausliefern (Eingabe-Prompt, optionale Eingabe-Dateien, erwartetes Verhalten) unter `examples/` oder einem benachbarten Ort, damit Iteration auf beobachtbarem Verhalten statt auf Authoring-Intuition basiert ([R2](#referenzen))
- **SOLLTE [SHOULD]** den Skill **gegen jedes Modell testen, mit dem er eingesetzt werden soll** — Haiku, Sonnet und Opus; was für Opus funktioniert, gibt Haiku evtl. nicht genug Anleitung; was für Haiku klar ist, kann für Opus überflüssig erklären ([R2](#referenzen))
- **KANN [MAY]** die Skill-Struktur mit dem Upstream-`skills-ref`-Validator validieren (`skills-ref validate ./skills/<name>`), bevor ein PR aufgemacht wird; der Validator fängt Frontmatter- und Naming-Probleme, die diese Spezifikation nicht erschöpfend auflistet ([R1](#referenzen))

## Akzeptanzkriterien
- [ ] Quellordner existiert unter `skills/<name>/` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Repository enthält eine gültige `.claude-plugin/plugin.json` und `.claude-plugin/marketplace.json`, die diesen Skill als Teil des `nolte-shared`-Plugins bereitstellen
- [ ] Skill ist in einem konsumierenden Projekt allein durch Installation des `nolte-shared`-Plugins aus dem Marketplace auffindbar — kein manuelles Kopieren oder Symlinken nach `.claude/skills/` ist nötig oder zulässig
- [ ] Die Plugin-Version in `.claude-plugin/plugin.json` entspricht dem zuletzt veröffentlichten GitHub-Release-Tag (gepflegt gemäß `release-automation` §Abgleich versionstragender Dateien, nicht durch Skill-Änderungs-PRs); kein Diff am `version`-Feld erscheint in einem PR, dessen alleiniger Zweck das Hinzufügen, Umbenennen oder Entfernen eines Skills ist
- [ ] `SKILL.md` parst mit gültigem YAML-Frontmatter, das `name` und `description` enthält
- [ ] `name` im Frontmatter entspricht dem Ordnernamen
- [ ] `description` nennt die konkreten Nutzer-Formulierungen, die den Skill auslösen sollen
- [ ] Falls `tags` im Frontmatter deklariert ist, ist jeder Eintrag ein kleingeschriebener ASCII-Kebab-Case-String ≤30 Zeichen, und die Liste enthält höchstens 5 Einträge
- [ ] Skill funktioniert in einem nachgelagerten Projekt, das keinen claude-shared-spezifischen Kontext enthält, geladen über das Plugin
- [ ] Keine hartkodierten absoluten Pfade; alle internen Pfade sind relativ zum Skill-Ordner oder zum Projekt, auf dem der Skill operiert
- [ ] Falls der Skill Dateien schreibt, sind Zielorte und Vorbedingungen dokumentiert
- [ ] Das Review eines einzelnen Skills gegen diese Spec folgt `spec/claude/skill-review/`; die Review-Ausgabe entspricht `spec/claude/review-plan/` und liegt unter `.audits/skill-review/<name>.md`
- [ ] Jede `SKILL.md` ist unter 500 Zeilen und 5.000 Tokens, und jedes referenzierte Asset unter `references/` / `templates/` / `assets/` / `scripts/` ist mit einer expliziten Lade-Trigger-Formulierung in `SKILL.md` gepaart
- [ ] `name` ist 1–64 Zeichen, ASCII-Kleinbuchstaben/-Ziffern/-Bindestriche, beginnt und endet nicht mit `-`, enthält kein `--` und enthält keinerlei Vorkommen der reservierten Tokens `anthropic` oder `claude`
- [ ] `description` ist nicht leer, ≤1024 Zeichen, in dritter Person verfasst und benennt sowohl *was* der Skill tut als auch *wann* er einzusetzen ist
- [ ] Kombinierter Text `description` + `when_to_use` ist unter 1.536 Zeichen
- [ ] Keine Datei-Referenz innerhalb von `SKILL.md` zeigt über eine andere Datei weiter (jede Referenz ist maximal einen Hop von `SKILL.md` entfernt)
- [ ] Jede Referenzdatei länger als 100 Zeilen beginnt mit einem Inhaltsverzeichnis
- [ ] Jede Skript-Referenz macht die Ausführungs-Absicht explizit („Run X to …" vs. „See X for the algorithm of …")
- [ ] Alle Pfade in `SKILL.md` und Hilfsdateien verwenden Forward-Slashes
- [ ] Kein Skill in `skills/` referenziert ein MCP-Tool ohne den `ServerName:tool_name`-Qualifier
- [ ] Keine `SKILL.md` deklariert einen `name`, der die reservierten Tokens `anthropic` oder `claude` enthält; andere Frontmatter-Felder (`description`, `tags`, `when_to_use` etc.) DÜRFEN diese Begriffe erwähnen

## Referenzen

- [R1] Agent Skills, formale Spezifikation — <https://agentskills.io/specification>
- [R2] Skill authoring best practices, Anthropic-Plattform-Doku — <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R3] Extend Claude with skills, Claude-Code-Doku — <https://code.claude.com/docs/en/skills>
- [R4] Best practices for skill creators, agentskills.io — <https://agentskills.io/skill-creation/best-practices>
- [R5] Equipping agents for the real world with Agent Skills, Anthropic Engineering, 2025-10-16 — <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R6] anthropics/skills (kanonisches Anthropic-Skill-Repository) — <https://github.com/anthropics/skills>

## Offene Fragen
- Soll der Ordnername verpflichtend einem etwaigen nutzerseitigen Slash-Command-Namen entsprechen, oder dürfen sie abweichen?
- Brauchen Skills Versions- oder Kompatibilitäts-Metadaten, während sie sich weiterentwickeln?
- Wo verläuft die Grenze zwischen einem Skill und einem Agent? Wann soll eine Fähigkeit das eine sein, wann das andere?
- Gibt es eine maximale Verschachtelungstiefe für unterstützende Unterordner, oder bleibt das lose?
