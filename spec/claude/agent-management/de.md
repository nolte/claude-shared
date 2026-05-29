# Claude-Agent-Autorenschaft

Status: draft

## Kontext
Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents, die von nachgelagerten Projekten genutzt werden. Ein Agent hat zwei Ausprägungen: eine **Quell-Form** in diesem Repository (unter `agents/`) und eine **Laufzeit-Form** in einem konsumierenden Projekt (unter `.claude/agents/` oder `~/.claude/agents/`), aus der Claude Code den Agent lädt und das `Agent`-Tool per `subagent_type` an ihn weiterleitet. Ohne einheitliche Form driften Agents in Benennung, Trigger-Beschreibungen, Tool-Scoping und Qualität des System-Prompts auseinander, was Wiederverwendung brüchig und das Routing unzuverlässig macht. Diese Spezifikation definiert, wie neue Agents erstellt werden, wo sie in beiden Formen liegen und woran sich bestehende Agents halten müssen.

## Ziele
- Jeder Agent hat dieselbe vorhersehbare Form auf der Festplatte
- Agents sind für Claude über präzise, trigger-orientierte Beschreibungen routbar
- Agents haben den minimal notwendigen Tool-Zugriff, um ihre Aufgabe zu erfüllen
- Agents sind portabel über jedes Projekt, das claude-shared konsumiert, ohne versteckte Abhängigkeiten
- Autoren haben eine klare Checkliste und ein Template als Startpunkt

## Nicht-Ziele
- Plugin-Paketierung und -Verteilung (separat behandelt)
- Plugin-Level-Schnittführung — wann eine Capability in dieses Plugin gegenüber einem separaten gehört und wie das Plugin überschaubar bleibt, während seine Agent-Anzahl wächst (abgedeckt durch `plugin-scoping`)
- Einrichtung nachgelagerter Projekte und `.claude/`-Konfiguration
- Vorgabe konkreten Agent-Verhaltens jenseits struktureller Regeln
- Die Orchestrierungslogik im aufrufenden Claude (welcher Agent wann gewählt wird)

## Anforderungen

### Struktur
- **MUSS [MUST]** als einzelne Markdown-Datei mit dem Namen `<name>.md` angelegt werden, wobei `<name>` ASCII-Kebab-Case ist
- **MUSS [MUST]** YAML-Frontmatter mit den Feldern `name`, `description` und `distribution` enthalten
- **MUSS [MUST]** `name` exakt auf den Dateinamen ohne die Endung `.md` setzen
- **DARF NICHT [MUST NOT]** die reservierten Wörter `anthropic` oder `claude` als Wert von `name` oder an irgendeiner Stelle innerhalb von `name` verwenden, gemäß Upstream-Plattform-Validator. Dieselbe enge Ausnahmeklausel aus `skill-management` §Frontmatter validation gilt: Ein Agent, dessen primäre Verantwortung das Authoring oder die Pflege einer Claude-Code- oder Anthropic-Plattform-Surface ist (zum Beispiel ein `claude-plugin-developer`-Agent), **DARF [MAY]** das Verbot aussetzen, wenn der Agent-Body einen `## Reserved-token rationale`-Abschnitt mitführt, der die Plattform-Surface benennt
- **MUSS [MUST]** eine `description` schreiben, die konkrete nutzerseitige Trigger und Aufgabenformen benennt („einsetzen, wenn der Nutzer X fragt", „aufrufen für Y") statt abstrakter Fähigkeiten, damit der aufrufende Claude zuverlässig über das Dispatchen entscheiden kann
- **MUSS [MUST]** `distribution` exakt auf einen der Werte `plugin` oder `project` setzen und damit die beabsichtigte Auslieferungsform deklarieren (siehe „Distribution" unten); der Autor trifft diese Wahl bewusst bei der Erstellung und ändert sie nur durch Neuausrichtung des Agents auf die andere Form
- **MUSS [MUST]** im Markdown-Körper einen System-Prompt enthalten, der den Agent auf genau eine Verantwortlichkeit eingrenzt und die erwartete Ausgabeform benennt
- **MUSS [MUST]** Frontmatter-Feldnamen und Werte technischer Bezeichner auf Englisch halten: `name`, `distribution`, `tools`-Einträge, `model` und `tags`-Einträge bleiben unabhängig von der Dokumentationssprache des Projekts in Englisch
- **SOLLTE [SHOULD]** den `description`-Wert und den System-Prompt-Body aus Token-Effizienz- und teamweiter Portabilitätsgründen auf Englisch halten; Agenten mit `distribution: project` für ein Projekt, das in seiner Wurzel-Konventionsdatei (typischerweise `CLAUDE.md`) eine nicht-englische Dokumentationssprache deklariert, **DÜRFEN [MAY]** stattdessen `description` und Body in der Hauptdokumentationssprache des Projekts verfassen. Agenten mit `distribution: plugin` **MÜSSEN [MUST]** in Description und Body englischsprachig bleiben, da sie über mehrere Downstream-Projekte mit potenziell unterschiedlichen Sprachen ausgeliefert werden
- Der Agent **DARF [MAY]** dennoch angewiesen werden, dem Nutzer in dessen Sprache zu antworten — unabhängig davon, in welcher Sprache der Body verfasst ist
- **MUSS [MUST]** in sich geschlossen sein — unterstützende Artefakte (Referenzen, Beispiele, Prompt-Bausteine) liegen neben der Agent-Datei in einem Schwester-Ordner `agents/<name>/` und werden über relative Pfade referenziert
- **KANN [MAY]** ein optionales `tags`-Feld im YAML-Frontmatter enthalten: eine Liste von kleingeschriebenen ASCII-Kebab-Case-Strings, jeder ≤30 Zeichen, mit höchstens 5 Einträgen; Tags liefern thematische Gruppierung, damit Katalog (`skill-agent-catalog`) und Peer-Cluster-Abgleich (`skill-vs-agent` §Portfolio-weite Konsistenz) nach Thema durchstöbert werden können
- **DARF NICHT [MUST NOT]** einen `tags`-Eintrag deklarieren, der mit `_` (Unterstrich) beginnt; das Unterstrich-Präfix ist für Generator-emittierte Auto-Tags wie `_translation-pending` reserviert
- **MUSS [MUST]** ein `phase`-Feld im YAML-Frontmatter enthalten, dessen Wert genau ein Identifier aus dem Acht-Werte-Vokabular ist, das in `skill-agent-catalog` §Phasen-Klassifikation deklariert ist (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); der Katalog-Generator lässt den Doku-Build scheitern, wenn `phase` fehlt oder außerhalb des Vokabulars liegt
- **KANN [MAY]** ein optionales `summary`-Feld sowie pro zusätzlich konfigurierter Doku-Sprache ein `summary_<lang>`-Feld enthalten; beide sind kurze (≤200 Zeichen) Klartext-Strings, die der Katalog als scanbaren Untertitel über der Routing-`description` rendert. Auflösung und Fallback regelt `skill-agent-catalog` §Per-Sprache-Kurzbeschreibung
- **KANN [MAY]** beliebige der optionalen Use-Case-Felder `use_when`, `dont_use_when`, `see_also` oder `examples` enthalten; das detaillierte Schema und die Validierung leben in `skill-agent-catalog` §Use-Case-Metadaten. Autoren **SOLLTEN [SHOULD]** sie deklarieren, sobald Überlappung mit anderen Artefakten wahrscheinlich ist, damit der Katalog scanbar bleibt und der Cross-Linking-Pass verwandte Artefakte verbinden kann

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

### Distribution
Ein Agent wird für genau eine von zwei Auslieferungsformen angelegt. Die Wahl wird vorab getroffen und im Feld `distribution` festgehalten:

- `plugin` — wird als Teil eines Claude-Code-Plugins ausgeliefert. Der Agent wird über den Plugin-Mechanismus installiert und aktualisiert, zusammen mit weiteren Agents/Skills desselben Plugins, und darf die Konventionen sowie ko-lokalisierten Ressourcen des Plugins voraussetzen.
- `project` — direkte Wiederverwendung in einem einzelnen Projekt oder Nutzer-Setup. Der Agent wird in das konsumierende Setup kopiert oder symlinkt und steht für sich allein, ohne einen Plugin-Kontext vorauszusetzen.

Jeder Agent deklariert diese Absicht, damit Autoren, Reviewer und Konsumenten aus der Datei selbst erkennen, ob er zu einem Plugin-Bundle gehört oder für die eigenständige Projektnutzung gedacht ist.

### Tool-Zugriff
- **MUSS [MUST]** ein `tools`-Feld im Frontmatter deklarieren, wenn der Agent eingeschränkt werden soll; das Feld nur dann weglassen, wenn der Agent tatsächlich die volle Tool-Oberfläche benötigt — **`tools` wegzulassen erteilt implizit jedes vom Aufrufer geerbte Tool**, das ist eine Permission-Sprawl-Falle, kein sicherer Default ([R1](#referenzen), [R3](#referenzen))
- **MUSS [MUST]** `tools` auf die minimal notwendige Menge für die Verantwortlichkeit des Agents beschränken (Prinzip der minimalen Rechte); rein lesende Agents **DÜRFEN NICHT [MUST NOT]** Schreib-, Edit- oder Ausführungs-Tools erhalten
  - **Enge Ausnahme** für Read-only-Audit-/Review-Agents, deren Audit-Surface eine seiteneffektfreie Shell-Fähigkeit benötigt, die kein dediziertes Tool abdeckt (typischerweise `git log`, `git rev-parse`, `git ls-files`, `gh api ... --jq` gegen Read-only-Endpunkte): `Bash` **DARF [MAY]** in `tools` erscheinen, wenn der Agent-Body einen `## Read-only Bash justification`-Abschnitt mitführt, der die exakte Teilmenge der Read-only-Kommandos benennt, die der Agent aufruft, und alles andere (Writes, Netzwerk-Mutationen, Package-Installs, Dateibearbeitungen) explizit verbietet. Der Agent **DARF [MUST NOT]** weiterhin keine `Edit`, `Write` oder `NotebookEdit` deklarieren — diese sind für Read-only-Agents bedingungslos verboten. Die `agent-review`-Checks honorieren die Ausnahme, wenn der Body-Abschnitt vorhanden ist, und stufen den ansonsten `Critical`-grade Befund auf `Info` herab; ohne den Abschnitt bleibt `Bash` auf einem Read-only-Agent ein `Critical`
- **SOLLTE [SHOULD]** dedizierte Tools (`Read`, `Grep`, `Glob`, `Edit`) gegenüber `Bash`-Äquivalenten bevorzugen, wenn beides möglich wäre
- **KANN [MAY]** stattdessen `disallowedTools` (Denylist, subtraktiv gegen das geerbte Set) deklarieren, wenn der Agent die meisten Tools behalten, aber eine kleine spezifische Teilmenge verlieren soll — sind beide Felder gesetzt, wendet die Laufzeit zuerst `disallowedTools` an und löst danach `tools` gegen den verbliebenen Pool auf, sodass ein in beiden Listen genanntes Tool entfernt wird ([R1](#referenzen))
- **DARF NICHT [MUST NOT]** `Agent` im `tools`-Feld auflisten — Claude-Code-Subagents können keine weiteren Subagents spawnen, das Tool wäre also wirkungslos, und es zu deklarieren führt Leser in die Irre, genestetes Fan-out sei möglich. Das einzig unterstützte genestete Muster bleibt *Skill orchestriert, Agent führt aus* ([R1](#referenzen) und `skill-vs-agent` §Hybrid-Muster)

### Modell-Wahl
- **KANN [MAY]** ein `model`-Feld im Frontmatter deklarieren; erlaubte Werte gemäß Claude Code sind ein Modell-Alias (`sonnet`, `opus`, `haiku`), eine vollständige Modell-ID (z. B. `claude-opus-4-7`, `claude-sonnet-4-6`) oder das Literal `inherit` ([R1](#referenzen))
- **Der Default ist `inherit`**, nicht ein konkretes Modell — fehlt das Feld, läuft der Agent auf dem Modell des Aufrufers. Das ist für Cost-Auditing relevant: Ein „kein-`model`"-Agent erbt weiterhin, was der Aufrufer bezahlt; nur ein expliziter Alias pinnt den Kostenvertrag
- **SOLLTE [SHOULD]** ein fixiertes `model` im System-Prompt oder in einem Kommentar begründen, damit spätere Leser verstehen, warum es festgelegt wurde
- **KANN [MAY]** die Laufzeit-Auflösungsreihenfolge (`CLAUDE_CODE_SUBAGENT_MODEL`-Env-Var → Per-Invocation-`model`-Parameter → Frontmatter-`model` → Modell des Aufrufers) nutzen, wenn ein Operator pro Session überschreiben will ([R1](#referenzen))

### Optionale Claude-Code-Frontmatter-Felder

Über `name`, `description`, `tools` und `model` hinaus erkennt Claude Code zusätzliche Felder. Autoren **DÜRFEN** diese verwenden, wenn sie zutreffen; Reviewer **MÜSSEN** unbekannte Felder, die nicht in dieser Liste stehen, als Authoring-Smell flaggen.

- `disallowedTools` — Denylist von Tools, die aus dem geerbten oder angegebenen Set subtrahiert werden ([R1](#referenzen))
- `permissionMode` — einer aus `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. **Wird für Plugin-distribuierte Agents ignoriert**, siehe „Plugin-Verteilungs-Sicherheits-Constraints" unten ([R1](#referenzen))
- `maxTurns` — begrenzt, wie viele Agentic-Turns der Subagent ausführt, bevor er stoppt ([R1](#referenzen))
- `skills` — Liste von Skill-Namen zum **Vorab-Laden in den Subagent-Kontext beim Start**; der vollständige Skill-Inhalt wird injiziert, nicht nur die Description, sodass der Subagent die Regeln im Scope hat, ohne Discovery-Kosten. Skills mit `disable-model-invocation: true` können nicht vorab geladen werden — Claude Code überspringt sie und protokolliert eine Warnung ([R1](#referenzen))
- `mcpServers` — MCP-Server, die nur diesem Subagent zur Verfügung stehen; unterstützt Inline-Definitionen und String-Referenzen auf bereits konfigurierte Server. **Wird für Plugin-distribuierte Agents ignoriert** ([R1](#referenzen))
- `hooks` — Lifecycle-Hooks, die auf diesen Subagent beschränkt sind. **Wird für Plugin-distribuierte Agents ignoriert** ([R1](#referenzen))
- `memory` — `user`, `project` oder `local`; gibt dem Subagent ein persistentes Verzeichnis über Sessions hinweg. Wenn gesetzt, werden Read/Write/Edit automatisch aktiviert und der System-Prompt wird um Memory-Kuratierungs-Anweisungen ergänzt ([R1](#referenzen))
- `background` — `true`, um stets als Background-Task zu laufen; die Laufzeit genehmigt benötigte Permissions vor dem Start vorab und lehnt alles, was nicht vorab genehmigt wurde, automatisch ab ([R1](#referenzen))
- `effort` — `low` / `medium` / `high` / `xhigh` / `max`; überschreibt das Session-Effort-Level für diesen Subagent ([R1](#referenzen))
- `isolation: worktree` — lässt den Subagent in einem temporären Git-Worktree laufen, sodass dessen Datei-Bearbeitungen den Hauptcheckout nicht berühren; der Worktree wird aufgeräumt, wenn der Subagent keine Änderungen vornimmt ([R1](#referenzen))
- `color` — Anzeigefarbe in der Task-Liste (`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`) ([R1](#referenzen))
- `initialPrompt` — wird als erster User-Turn vorangestellt, wenn dieser Agent als Main-Session via `--agent` läuft ([R1](#referenzen))

### Plugin-Verteilungs-Sicherheits-Constraints

Aus Sicherheitsgründen **ignoriert Claude Code stillschweigend** die Frontmatter-Felder `hooks`, `mcpServers` und `permissionMode`, wenn ein Agent aus einem Plugin geladen wird (also hier mit `distribution: plugin` autoriert) ([R1](#referenzen)). Diese Felder trotzdem zu autorieren, führt spätere Leser in die Irre und schafft Audit-Drift; deshalb verschärft diese Spezifikation den Constraint:

- **DARF NICHT [MUST NOT]**, wenn `distribution: plugin` deklariert ist, `hooks`, `mcpServers` oder `permissionMode` im Frontmatter setzen — die Laufzeit ignoriert sie, und ein späterer Leser hat kein Signal, „bewusst weggelassen" von „stillschweigend verworfen" zu unterscheiden
- **DARF [MAY]**, wenn `distribution: project` deklariert ist, eines dieser Felder frei verwenden; der Constraint betrifft ausschließlich plugin-distribuierte Agents
- **SOLLTE [SHOULD]**, wenn ein Agent `hooks`, `mcpServers` oder `permissionMode` tatsächlich braucht, ihn entweder von Beginn an als `distribution: project` autorieren oder im Body explizit notieren, dass die Plugin-Form diese Features opfert, und den Workaround für Plugin-Konsumenten dokumentieren (z. B. die Anweisung, die Agent-Datei nach `.claude/agents/` zu kopieren, um die Felder zurückzugewinnen)

### Subagent-Grenzen (Claude-Code-Laufzeit)

- **DARF NICHT [MUST NOT]** voraussetzen, dass ein Agent einen weiteren Subagent spawnen kann — Claude-Code-Subagents **können keine anderen Subagents spawnen** ([R1](#referenzen)). Das einzig unterstützte Pattern für genestete Orchestrierung bleibt *Skill orchestriert, Agent führt aus* (geregelt durch `skill-vs-agent`); der Skill bleibt im Haupt-Thread und kann Agents sequenziell oder parallel dispatchen
- **DARF NICHT [MUST NOT]** das Skill-Tool aus dem Body eines Agents heraus aufrufen, um Skill-förmige Arbeit an die Eltern-Konversation zurück zu delegieren — der Agent läuft in einem isolierten Kontext-Fenster und hat keinen stabilen Kanal für Skill-Level-Interaktivität ([R3](#referenzen) und `skill-vs-agent` §Hybrid-Muster)
- **KANN [MAY]**, wenn der Agent von Claude **proaktiv** aufgegriffen werden soll (ohne dass der Nutzer ihn explizit nennt), die Phrase **„use proactively"** im `description`-Feld enthalten; die Laufzeit behandelt diese Phrase als Opt-in-Signal für proaktive Delegation ([R1](#referenzen)). Umgekehrt: Soll der Agent nur laufen, wenn der Nutzer ihn explizit nennt, **DARF** „use proactively" **NICHT [MUST NOT]** in `description` stehen
- **SOLLTE [SHOULD]** für jeden Agent **Single-Responsibility-Design** anwenden: ein klares Ziel, eine Eingabeform, eine Ausgabeform, eine Übergaberegel. Agents, die mehrere Verantwortlichkeiten zusammenmischen (Review + Fix, Audit + Remediation), regredieren schnell, weil das dispatchierende Claude die Description nicht zuverlässig auf eine Anfrage abbilden kann ([R6](#referenzen))
- **SOLLTE [SHOULD]** die Agent-Oberfläche des Plugins schlank und die `description` jedes Agents scharf umrissen halten: Claudes automatische Delegation lässt nach, je größer die Zahl ähnlicher oder überlappender Agents wird, sodass ein Überangebot an Agents das Routing schädigt, selbst wenn jeder einzelne für sich wohlgeformt ist ([R1](#referenzen)). Bei mehrdeutigem Routing explizite Aufrufe gegenüber dem Verlass auf Auto-Delegation bevorzugen und Überlappung gemäß `skill-vs-agent` §Duplikat-Vermeidung und den Plugin-Grenz-Regeln in `plugin-scoping` auflösen

### Quell-Ablageort (Repository claude-shared)
- **MUSS [MUST]** im Quellbaum von claude-shared unter `agents/<name>.md` liegen, damit er kopiert, symlinkt oder für die Verteilung in ein Plugin gebündelt werden kann
- **KANN [MAY]** bei Bedarf einen Schwester-Ordner `agents/<name>/` für unterstützende Dateien haben

### Laufzeit-Ablageort (konsumierendes Projekt)
Der Laufzeit-Ablageort richtet sich nach dem deklarierten `distribution`:

- Bei `distribution: plugin` **MUSS [MUST]** der Agent aus dem dafür vorgesehenen Agents-Pfad des Plugins ladbar sein, sobald das Plugin im konsumierenden Projekt installiert ist. Er **DARF NICHT [MUST NOT]** erfordern, dass die Datei manuell nach `.claude/agents/` oder `~/.claude/agents/` kopiert wird, um zu funktionieren.
- Bei `distribution: project` **MUSS [MUST]** der Agent von Claude Code aus einem der folgenden Orte ladbar sein:
  - `.claude/agents/<name>.md` — projektbezogene Installation
  - `~/.claude/agents/<name>.md` — benutzerbezogene Installation

In beiden Fällen **DARF** der Agent **NICHT [MUST NOT]** einen bestimmten absoluten Installationsort voraussetzen; alle internen Referenzen bleiben relativ zur Agent-Datei oder zum Projekt, auf dem der Agent operiert.

### Empfehlungen
- **SOLLTE [SHOULD]** den System-Prompt mit Rolle und Grenzen des Agents beginnen, dann das erwartete Ausgabeformat, dann die Arbeitsweise
- **SOLLTE [SHOULD]** im System-Prompt ausdrücklich festhalten, ob der Agent Code schreibt oder nur recherchiert, da der aufrufende Claude diese Unterscheidung beim Dispatch treffen muss
- **SOLLTE [SHOULD]** den System-Prompt fokussiert halten; wächst er über etwa 200 Zeilen, sollten längere Referenzen in Dateien unter `agents/<name>/` ausgelagert werden (diese ~200-Zeilen-Zahl ist eine lokale `nolte-shared`-Konvention; Anthropic dokumentiert kein Agent-Datei-Größenbudget, im Gegensatz zur weichen ~500-Zeilen-`SKILL.md`-Richtlinie, die `skill-management` für Skills kodifiziert)
- **SOLLTE [SHOULD]** in der `description` sowohl positive Trigger („einsetzen, wenn…") als auch typische negative Fälle („nicht einsetzen für…") nennen, wenn Überschneidungen mit anderen Agents wahrscheinlich sind
- **KANN [MAY]** Beispiel-Aufrufe und erwartete Berichte in einem Schwester-Ordner `agents/<name>/examples/` enthalten

### Wiederaufnehmbare Runs
- **MUSS [MUST]** `resumable: true` im Frontmatter des Agents deklarieren, wenn der Agent intern mehr als eine benannte Phase umspannt, die ein Zwischenartefakt produziert, das die Person bei Unterbrechung sonst verlieren würde, und `spec/claude/resumable-work/` für den On-Disk-Envelope, die Checkpoint-Kadenz, das Re-Invocation-Prompt und den Lebenszyklus befolgen; die tragenden Regeln leben in jener Spec und werden hier nicht dupliziert
- **MUSS [MUST]** Resume-Support im `description`-Text des Agents erwähnen, wann immer `resumable: true` gesetzt ist, damit der aufrufende Claude entsprechend routen kann
- **SOLLTE NICHT [SHOULD NOT]** `resumable: true` für Fire-and-Forget-Agents deklarieren, deren Vertrag ein einzelner Read-only-Pass ist, der billig neu startbar ist

## Akzeptanzkriterien
- [ ] Quelldatei existiert unter `agents/<name>.md` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Frontmatter parst als gültiges YAML und enthält mindestens `name`, `description` und `distribution`
- [ ] `name` im Frontmatter entspricht dem Dateinamen ohne `.md`
- [ ] `description` benennt konkrete Trigger, die der aufrufende Claude mit Nutzeranfragen abgleichen kann
- [ ] Falls `tags` im Frontmatter deklariert ist, ist jeder Eintrag ein kleingeschriebener ASCII-Kebab-Case-String ≤30 Zeichen, und die Liste enthält höchstens 5 Einträge
- [ ] Kein `tags`-Eintrag beginnt mit `_` (Unterstrich-Präfix ist für Generator-Auto-Tags reserviert)
- [ ] Falls `summary` oder ein `summary_<lang>` deklariert ist, ist der Wert ein nicht-leerer Klartext-String mit ≤200 Zeichen
- [ ] Falls `use_when`, `dont_use_when`, `see_also` oder `examples` deklariert ist, entspricht der Wert dem Schema aus `skill-agent-catalog` §Use-Case-Metadaten
- [ ] Frontmatter deklariert ein `phase`-Feld, dessen Wert einer von `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release` oder `cross-cutting` ist
- [ ] `distribution` ist exakt `plugin` oder `project` — kein anderer Wert, kein fehlendes Feld
- [ ] Bei `distribution: plugin` ist der Agent in einem Projekt, in dem das enthaltende Plugin installiert ist, über `subagent_type: <name>` dispatchbar, ohne dass die Datei manuell kopiert werden muss
- [ ] Bei `distribution: project` ist der Agent nach Ausbringung nach `.claude/agents/<name>.md` oder `~/.claude/agents/<name>.md` über `subagent_type: <name>` dispatchbar, ohne dass ein Plugin erforderlich ist
- [ ] Ist `tools` gesetzt, sind die gelisteten Tools ausreichend für die angegebene Verantwortlichkeit und enthalten keine ungenutzten Einträge
- [ ] Rein lesende Agents haben keine Schreib-/Edit-/Ausführungs-Tools in ihrer `tools`-Liste
- [ ] Agent funktioniert, wenn er in einem nachgelagerten Projekt aufgerufen wird, das keinen claude-shared-spezifischen Kontext enthält
- [ ] Keine hartkodierten absoluten Pfade; alle internen Referenzen sind relativ zur Agent-Datei oder zum Projekt, auf dem sie operiert
- [ ] Schreibt der Agent Dateien oder verursacht Seiteneffekte, sind Ziele und Vorbedingungen im System-Prompt dokumentiert
- [ ] Frontmatter-Feldnamen und Werte technischer Bezeichner (`name`, `distribution`, `tools`, `model`, `tags`) sind in Englisch; `description` und der System-Prompt-Body sind standardmäßig Englisch — es sei denn, der Agent deklariert `distribution: project` und die Wurzel-Konventionsdatei (typischerweise `CLAUDE.md`) des konsumierenden Projekts deklariert eine nicht-englische Dokumentationssprache und autorisiert sie für Agent-Prosa
- [ ] Das Review eines einzelnen Agents gegen diese Spec folgt `spec/claude/agent-review/`; die Review-Ausgabe entspricht `spec/claude/review-plan/` und liegt unter `.audits/agent-review/<name>.md`
- [ ] Kein als `distribution: plugin` deklarierter Agent setzt eines der Felder `hooks`, `mcpServers`, `permissionMode` im Frontmatter (diese Felder werden für plugin-distribuierte Agents von der Laufzeit stillschweigend verworfen)
- [ ] Kein Agent-Body invokiert einen weiteren Subagent über das Agent-Tool oder eine äquivalente Dispatch-Formulierung (Subagents können in Claude Code keine Subagents spawnen)
- [ ] Kein Agent listet `Agent` in seinem `tools`-Feld (Subagents können keine Subagents spawnen, der Eintrag wäre also wirkungslos)
- [ ] Jeder Agent, dessen `description` die Phrase „use proactively" enthält, rechtfertigt tatsächlich proaktive Delegation; Agents, die nur auf explizite Nutzeranfrage laufen sollen, **DÜRFEN** die Phrase **NICHT** enthalten
- [ ] Jeder Agent, der `model` auf einen anderen Wert als `inherit` pinnt, begründet das Pin entweder im System-Prompt oder trägt einen Kommentar mit der Kosten-/Qualitäts-Abwägung
- [ ] Die Verantwortlichkeit jedes Agents ist eine einzelne — ein Ziel, eine Eingabeform, eine Ausgabeform; ein Agent, dessen `description` als „X und Y" oder „X plus Z" liest, ist aufgeteilt oder hat eine dokumentierte Begründung für die Verschmelzung
- [ ] Sind `tools` und `disallowedTools` beide deklariert, erscheint kein Tool in beiden Listen, und das aufgelöste Set (deny-then-allow) ist nicht leer

## Referenzen

- [R1] Create custom subagents, Claude-Code-Doku — <https://code.claude.com/docs/en/sub-agents>
- [R2] Agent Skills, formale Spezifikation (für Cross-Format-Abgleich) — <https://agentskills.io/specification>
- [R3] Skill-vs-Agent-Entscheidung (dieses Plugin) — `spec/claude/skill-vs-agent/`
- [R4] Building Effective AI Agents, Anthropic Engineering — <https://www.anthropic.com/research/building-effective-agents>
- [R5] Equipping agents for the real world with Agent Skills, Anthropic Engineering, 2025-10-16 — <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- [R6] Best practices for Claude Code subagents, PubNub Engineering — <https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/>

## Offene Fragen
- Soll der Dateiname (und damit `name`) exakt dem `subagent_type`-String entsprechen, oder ist eine Mapping-Schicht erlaubt?
- Brauchen Agents Versions- oder Kompatibilitäts-Metadaten, während sie sich weiterentwickeln, oder genügt die Git-Historie der Agent-Datei?
- Wo verläuft die Grenze zwischen einem Skill und einem Agent? Wann soll eine Fähigkeit das eine sein, wann das andere?
- Sollen Agents deklarieren, an welche anderen Agents sie delegieren dürfen, oder bleibt Delegation vollständig dem aufrufenden Claude überlassen?
- Gibt es eine gemeinsame Konvention, wie Agents zurückmelden (strukturiert vs. freitextliche Zusammenfassung), oder ist das pro Agent?
