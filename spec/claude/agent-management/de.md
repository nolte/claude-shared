# Claude-Agent-Autorenschaft

Status: draft

## Kontext
Das Repository claude-shared sammelt wiederverwendbare Claude-Code-Skills und -Agents, die von nachgelagerten Projekten genutzt werden. Ein Agent hat zwei Ausprägungen: eine **Quell-Form** in diesem Repository (unter `agents/`) und eine **Laufzeit-Form** in einem konsumierenden Projekt (unter `.claude/agents/` oder `~/.claude/agents/`), aus der Claude Code den Agent lädt und das `Agent`-Tool per `subagent_type` an ihn weiterleitet. Ohne einheitliche Form driften Agents in Benennung, Trigger-Beschreibungen, Tool-Scoping und Qualität des System-Prompts auseinander, was Wiederverwendung brüchig und das Routing unzuverlässig macht. Diese Spezifikation definiert, wie neue Agents erstellt werden, wo sie in beiden Formen liegen und woran sich bestehende Agents halten müssen.

Für eine konsolidierte artefaktübergreifende Referenz jedes Skill- und Agent-Frontmatter-Feldes, seiner Provenienz (portabler Claude-Code-Standard gegenüber nolte-lokaler Erfindung) und seines normativen Owners siehe `spec/claude/skill-agent-frontmatter/`. Diese Referenz bildet ab und verweist auf diese Spec zurück; sie wiederholt die Regeln hier nicht.

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
  - **Namensform**: Die vollständige Agent-Namenskonvention — die `<subject>-<role-noun>`-Objekt-Rolle-Wahl, die Rollen-Nomen-Morphologie, die geschlossene Ausnahmeliste (`png-to-transparent-svg`, `audience-review`), die Eine-Form-pro-Plugin-Regel und die Rename-Policy — gehört `spec/claude/skill-agent-naming/`. Diese Spec wiederholt bewusst nichts davon; bei Diskrepanz gewinnt die Naming-Spec, und `check_name_form` im Validator spiegelt deren geschlossene Listen.
- **MUSS [MUST]** eine `description` schreiben, die konkrete nutzerseitige Trigger und Aufgabenformen benennt („einsetzen, wenn der Nutzer X fragt", „aufrufen für Y") statt abstrakter Fähigkeiten, damit der aufrufende Claude zuverlässig über das Dispatchen entscheiden kann
- **MUSS [MUST]** `distribution` exakt auf einen der Werte `plugin` oder `project` setzen und damit die beabsichtigte Auslieferungsform deklarieren (siehe „Distribution" unten); der Autor trifft diese Wahl bewusst bei der Erstellung und ändert sie nur durch Neuausrichtung des Agents auf die andere Form
- **MUSS [MUST]** im Markdown-Körper einen System-Prompt enthalten, der den Agent auf genau eine Verantwortlichkeit eingrenzt und die erwartete Ausgabeform benennt
- **MUSS [MUST]** Frontmatter-Feldnamen und Werte technischer Bezeichner auf Englisch halten: `name`, `distribution`, `tools`-Einträge, `model` und `tags`-Einträge bleiben unabhängig von der Dokumentationssprache des Projekts in Englisch
- **SOLLTE [SHOULD]** den `description`-Wert und den System-Prompt-Body aus Token-Effizienz- und teamweiter Portabilitätsgründen auf Englisch halten; Agenten mit `distribution: project` für ein Projekt, das in seiner Wurzel-Konventionsdatei (typischerweise `CLAUDE.md`) eine nicht-englische Dokumentationssprache deklariert, **DÜRFEN [MAY]** stattdessen `description` und Body in der Hauptdokumentationssprache des Projekts verfassen. Agenten mit `distribution: plugin` **MÜSSEN [MUST]** in Description und Body englischsprachig bleiben, da sie über mehrere Downstream-Projekte mit potenziell unterschiedlichen Sprachen ausgeliefert werden
- Der Agent **DARF [MAY]** dennoch angewiesen werden, dem Nutzer in dessen Sprache zu antworten — unabhängig davon, in welcher Sprache der Body verfasst ist
- **MUSS [MUST]** in sich geschlossen sein: ein Agent ist genau eine Top-Level-Markdown-Datei `agents/<name>.md`. Unterstützendes Material (Referenzen, Beispiele, Prompt-Bausteine, Output-Shape-Templates) wird direkt in den Agent-Body inlined. **DARF NICHT [MUST NOT]** eine Begleit-Markdown-Datei in einem Schwester-Ordner `agents/<name>/` ablegen, weil Claude Codes Default-Agent-Discovery `agents/` **rekursiv** scannt: jede genestete `.md` wird als gescopeter Phantom-Agent (`<name>:<file>`) registriert und erbt mangels Frontmatter die volle Tool-Oberfläche ohne `tools`-Einschränkung. Ist ein unterstützendes Artefakt wirklich zu groß zum Inlinen, wird es **außerhalb** des rekursiv gescannten `agents/`-Baums abgelegt (zum Beispiel unter einem Top-Level-`agent-assets/<name>/`) und über einen relativen Pfad referenziert
- **KANN [MAY]** ein optionales `tags`-Feld im YAML-Frontmatter enthalten: eine Liste von kleingeschriebenen ASCII-Kebab-Case-Strings, jeder ≤30 Zeichen, mit höchstens 5 Einträgen; Tags liefern thematische Gruppierung, damit Katalog (`skill-agent-catalog`) und Peer-Cluster-Abgleich (`skill-vs-agent` §Portfolio-weite Konsistenz) nach Thema durchstöbert werden können
- **DARF NICHT [MUST NOT]** einen `tags`-Eintrag deklarieren, der mit `_` (Unterstrich) beginnt; das Unterstrich-Präfix ist für Generator-emittierte Auto-Tags wie `_translation-pending` reserviert
- **MUSS [MUST]** ein `phase`-Feld im YAML-Frontmatter enthalten, dessen Wert genau ein Identifier aus dem Acht-Werte-Vokabular ist, das in `skill-agent-catalog` §Phasen-Klassifikation deklariert ist (`vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`); der Katalog-Generator lässt den Doku-Build scheitern, wenn `phase` fehlt oder außerhalb des Vokabulars liegt
- **KANN [MAY]** ein optionales `summary`-Feld sowie pro zusätzlich konfigurierter Doku-Sprache ein `summary_<lang>`-Feld enthalten; beide sind kurze (≤200 Zeichen) Klartext-Strings, die der Katalog als scanbaren Untertitel über der Routing-`description` rendert. Auflösung und Fallback regelt `skill-agent-catalog` §Per-Sprache-Kurzbeschreibung
- **KANN [MAY]** beliebige der optionalen Use-Case-Felder `use_when`, `dont_use_when`, `see_also` oder `examples` enthalten; das detaillierte Schema und die Validierung leben in `skill-agent-catalog` §Use-Case-Metadaten. Autoren **SOLLTEN [SHOULD]** sie deklarieren, sobald Überlappung mit anderen Artefakten wahrscheinlich ist, damit der Katalog scanbar bleibt und der Cross-Linking-Pass verwandte Artefakte verbinden kann

### Description-Contract

Die `description` ist das Feld, das Claude Code in jeder Runde in das Agent-Routing-Budget lädt, daher **MUSS [MUST]** sie sowohl zuverlässig routbar als auch günstig zu laden sein. Die folgenden Regeln konsolidieren und schärfen die description-Leitlinien, die bereits unter §Struktur und §Empfehlungen stehen, zu einem einzigen Contract, sodass ein Autor eine Stelle zum Konformieren und ein Reviewer eine Stelle zum Prüfen hat. `skill-agent-frontmatter` §Feldreferenz digestet diesen Contract und verweist hierher zurück; bei jeder Diskrepanz gewinnt dieser Owner.

- **MUSS [MUST]** der description-**Form** in dieser Reihenfolge folgen: (1) *was er tut* — die Fähigkeit in einem Satzteil; (2) *wann zu aktivieren* — konkrete nutzerseitige Trigger („einsetzen, wenn der Nutzer X fragt", „aufrufen für Y") statt abstrakter Fähigkeiten; (3) *wann nicht* — die negativen Fälle als `don't use for X → use <other>`. Teile (1) und (2) sind immer vorhanden; Teil (3) ist nur erforderlich, wo Überlappung mit einem anderen Artefakt wahrscheinlich ist (§Empfehlungen). Dies fasst die Trigger-Regel aus §Struktur und die Positiv/Negativ-Trigger-Empfehlung unten in einer Form zusammen.
- **DARF NICHT [MUST NOT]** einen Beispiel- oder Kommentar-Block in einer `description` einbetten: keine `user:` / `assistant:`-Gesprächszüge und kein `<commentary>` / `<example>` (oder sonstiges) Tag-Paar. Dies spezialisiert die „no XML tags"-Regel aus §Struktur auf die Routing-Prosa und verbietet zusätzlich die tag-freie `user:` / `assistant:`-Transkript-Form. Ausgearbeitete Beispiele, Beispieldialoge und Begründungen gehören in den **Agent-Body**, den der Router nicht in das Routing-Budget lädt. Zum Zeitpunkt der F-5-Strukturanalyse der Shared-Plugins (2026-07-19; analysis retired to git history) trägt die Shared-Agent-Surface bereits keine solchen Blöcke; diese Regel **sichert diesen sauberen Zustand** ab, statt bestehende Verstöße zu bereinigen.
- **SOLLTE [SHOULD]** Delimitations-**Ketten knapp** halten: einen einzelnen günstigen Querverweis (`→ use <other>`) einer aufgezählten `don't use for A → use X; don't use for B → use Y; …`-Kette vorziehen, wenn ein Querverweis den Leser bereits korrekt routet. Eine lange aufgezählte Kette wiederholt Routing-Token, die die `description` des Peer-Artefakts und die `dont_use_when`-Metadaten des Katalogs bereits tragen; nur die wirklich mehrdeutige Delimitation benennen und den Rest per Querverweis abhandeln. Dies ist eine Token-Ökonomie-Regel, kein Routing-Signal-Schnitt — niemals einen negativen Trigger streichen, den ein Leser tatsächlich zum korrekten Routen braucht.

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
- `design` — Brand-/Design-Assets, Bild-Prompts, visuelles Tooling
- `media` — Bild- und Medienverarbeitung oder -generierung
- `privacy` — DSGVO-/Datenschutz-Flächen
- `orchestrate` — Multi-Skill-/Multi-Agent-Orchestrierungs-Flows
- `implementation` — Hands-on-Code-Implementierung
- `planning` — Work-Package- und Implementierungs-Planung
- `frontend` — browser-gerenderte UI-Flächen
- `ui` — UI-/UX-Review und -Optimierung
- `fullstack` — kombinierte Frontend+Backend-Implementierung
- `issue` — GitHub-Issue-Aufnahme und -Orchestrierung
- `lifecycle` — Sprint-/Feature-Lifecycle-Übergänge und -Trigger
- `triage` — Aufnahme, Klassifikation und Routing von Findings oder Issues
- `validation` — Schema- und Struktur-Validierungs-Tooling

### Distribution
Ein Agent wird für genau eine von zwei Auslieferungsformen angelegt. Die Wahl wird vorab getroffen und im Feld `distribution` festgehalten:

- `plugin` — wird als Teil eines Claude-Code-Plugins ausgeliefert. Der Agent wird über den Plugin-Mechanismus installiert und aktualisiert, zusammen mit weiteren Agents/Skills desselben Plugins, und darf die Konventionen sowie ko-lokalisierten Ressourcen des Plugins voraussetzen.
- `project` — direkte Wiederverwendung in einem einzelnen Projekt oder Nutzer-Setup. Der Agent wird in das konsumierende Setup kopiert oder symlinkt und steht für sich allein, ohne einen Plugin-Kontext vorauszusetzen.

Jeder Agent deklariert diese Absicht, damit Autoren, Reviewer und Konsumenten aus der Datei selbst erkennen, ob er zu einem Plugin-Bundle gehört oder für die eigenständige Projektnutzung gedacht ist.

Agents führen keine Per-Datei-Versions-Metadaten mit; die Versionierung wird auf Plugin-Ebene (`.claude-plugin/plugin.json`) und über die Git-Historie gehandhabt. Ein Per-Agent-`version`-Frontmatter-Feld wird zurückgestellt, bis der Verteilungsmechanismus unabhängiges Per-Agent-Pinning unterstützt (siehe `plugin-scoping`).

### Tool-Zugriff
- **MUSS [MUST]** ein `tools`-Feld im Frontmatter deklarieren, wenn der Agent eingeschränkt werden soll; das Feld nur dann weglassen, wenn der Agent tatsächlich die volle Tool-Oberfläche benötigt — **`tools` wegzulassen erteilt implizit jedes vom Aufrufer geerbte Tool**, das ist eine Permission-Sprawl-Falle, kein sicherer Default ([R1](#referenzen), [R3](#referenzen))
- **MUSS [MUST]** `tools` auf die minimal notwendige Menge für die Verantwortlichkeit des Agents beschränken (Prinzip der minimalen Rechte); rein lesende Agents **DÜRFEN NICHT [MUST NOT]** Schreib-, Edit- oder Ausführungs-Tools erhalten
  - **Enge Ausnahme** für Read-only-Audit-/Review-Agents, deren Audit-Surface eine seiteneffektfreie Shell-Fähigkeit benötigt, die kein dediziertes Tool abdeckt (typischerweise `git log`, `git rev-parse`, `git ls-files`, `gh api ... --jq` gegen Read-only-Endpunkte): `Bash` **DARF [MAY]** in `tools` erscheinen, wenn der Agent-Body einen `## Read-only Bash justification`-Abschnitt mitführt, der die exakte Teilmenge der Read-only-Kommandos benennt, die der Agent aufruft, und alles andere (Writes, Netzwerk-Mutationen, Package-Installs, Dateibearbeitungen) explizit verbietet. Der Agent **DARF [MUST NOT]** weiterhin keine `Edit`, `Write` oder `NotebookEdit` deklarieren — diese sind für Read-only-Agents bedingungslos verboten. Die `agent-review`-Checks honorieren die Ausnahme, wenn der Body-Abschnitt vorhanden ist, und stufen den ansonsten `Critical`-grade Befund auf `Info` herab; ohne den Abschnitt bleibt `Bash` auf einem Read-only-Agent ein `Critical`
  - **Write-fähige Agents, die zusätzlich `Bash` brauchen**: ein Agent, der legitim `Edit`/`Write` hält (ein Drafting- oder Repair-Agent) und zusätzlich Shell-Kommandos ausführt (typischerweise `task lint`, einen Build oder einen Test-Lauf), dokumentiert diese Shell-Nutzung unter einem neutralen `## Bash justification`-Abschnitt — **nicht** `## Read-only Bash justification`, dessen Seiteneffektfreiheits-Zusage für einen write-fähigen Agent nicht gilt und eine falsche Behauptung wäre. Der Abschnitt benennt die aufgerufenen Kommandos und ihre Effekte. Man beachte, dass `task lint` (und `pre-commit run`) **nicht** seiteneffektfrei ist: es führt Auto-Fixer aus (trailing-whitespace, end-of-file, Formatierer), die getrackte Dateien mutieren, sodass ein Agent, der es aufruft, es NICHT als seiteneffektfrei beschreiben darf.
  - **Sanktionierte Kommando-Klassen jenseits des strikten Read-only-Satzes**: fünf wiederkehrende Kommando-Klassen liegen außerhalb des Seiteneffektfreiheits-Rahmens, sind für einen Read-only-Agent aber sanktioniert, wenn sein `## Read-only Bash justification`-Abschnitt sie explizit benennt und die Grenze angibt: (1) **ephemere Tool-Runner** (`npx --yes <tool>`, `uvx <tool>`), deren einziger Write der Tool-Cache des Runners außerhalb des Repositories ist — sanktioniert zum Auflösen eines gepinnten Analyse-Tools, das das Repository nicht vendort; (2) **Netzwerk-Reads** (`curl` oder der eigene Fetch eines Tools gegen Read-only-Endpunkte) zum Auflösen eines Upstream-Identifiers oder -Releases — niemals ein mutierender Request; (3) **ein begrenzter Re-Run eines einzelnen Flaky-Verdacht-Tests**, wenn die Verantwortung des Agents Test-Result-Analyse ist — er führt Projekt-Code aus und ist damit nicht seiteneffektfrei; die Justification benennt die Einzeltest-Grenze und verbietet Suite-weite Läufe. (4) **Paketmanager-Metadaten-Reads** (`pip show <pkg>`, `npm ls <pkg>` oder die entsprechende Abfrage des jeweiligen Ökosystems), wenn das Audit davon abhängt, ob eine Abhängigkeit tatsächlich installiert und gepinnt ist statt nur in Prosa erwähnt — die Grenze ist reine Abfrage: niemals `install`, `update`, `add` oder ein Kommando, das eine Lockfile auflöst oder schreibt; (5) **ein dokumentierter Einzelaufruf im Export- oder Report-Modus eines Analyse-Werkzeugs, das das Repository bereits vendort**, wenn das Werkzeug keine reine Abfrageform hat und der einzige Write des Laufs der Report-Pfad ist, den der Agent anschließend liest — die Justification benennt das exakte Kommando und den geschriebenen Pfad. Eine Klasse, die der Abschnitt nicht auflistet, bleibt verboten, und das `agent-review`-Downgrade gilt für diese Klassen genau wie für den git-/`gh`-Satz.
  - **Netzwerk-Lese-Surface (`WebSearch` / `WebFetch`)**: ein Read-only-Agent DARF `WebSearch` oder `WebFetch` halten, wenn seine Audit-Surface das Lesen externer Quellen wirklich erfordert (etwa das Auflösen eines SPDX-Identifiers oder das Prüfen von Upstream-Release-Notes). Weil diese Tools die Anfrage exfiltrieren und Remote-Inhalte abrufen — ein Datenfluss-Effekt, den die Seiteneffektfreiheits-Rahmung für `Bash` nicht abdeckt — **SOLLTE** ein solcher Agent einen `## Network-read justification`-Abschnitt mitführen, der benennt, warum der Netzwerk-Lesezugriff nötig ist, und verbietet, ihn zum Mutieren von Remote-State zu nutzen. Das hält den Least-Authority-Audit-Trail symmetrisch zur `Bash`-Ausnahme.
  - **Reviewer-Review-und-Repair-Klassifikation**: ein Agent, dessen einzige Verantwortung ein Review ist, das das Anwenden des gefundenen Fixes *einschließt* (ein Review-und-Repair- oder Lint-und-Fix-Agent), ist legitim write-fähig und **kein** Read-only-Agent; die obigen Read-only-Tool-Verbote gelten für ihn nicht. Read-only-Status wird aus den Verantwortungs-Verben (review, audit, research, lint, report) in `description` / System-Prompt abgeleitet, und diese Verb-Heuristik darf nicht so wörtlich angewandt werden, dass ein echter Repair-Agent fälschlich als read-only-mit-Write-Tools geflaggt wird. Wenn die Klassifikation wirklich mehrdeutig ist, den intendierten Modus (read-only vs. review-und-repair) explizit im System-Prompt benennen.
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
- **DARF NICHT [MUST NOT]** einen Schwester-Ordner `agents/<name>/` für unterstützende Markdown-Dateien einführen; die rekursive Agent-Discovery würde ihn als Phantom-Agent registrieren (siehe §Struktur). Unterstützende Artefakte, die sich nicht inlinen lassen, liegen außerhalb des `agents/`-Baums (zum Beispiel `agent-assets/<name>/`) und werden über relative Pfade referenziert

### Laufzeit-Ablageort (konsumierendes Projekt)
Der Laufzeit-Ablageort richtet sich nach dem deklarierten `distribution`:

- Bei `distribution: plugin` **MUSS [MUST]** der Agent aus dem dafür vorgesehenen Agents-Pfad des Plugins ladbar sein, sobald das Plugin im konsumierenden Projekt installiert ist. Er **DARF NICHT [MUST NOT]** erfordern, dass die Datei manuell nach `.claude/agents/` oder `~/.claude/agents/` kopiert wird, um zu funktionieren.
- Bei `distribution: project` **MUSS [MUST]** der Agent von Claude Code aus einem der folgenden Orte ladbar sein:
  - `.claude/agents/<name>.md` — projektbezogene Installation
  - `~/.claude/agents/<name>.md` — benutzerbezogene Installation

In beiden Fällen **DARF** der Agent **NICHT [MUST NOT]** einen bestimmten absoluten Installationsort voraussetzen; alle internen Referenzen bleiben relativ zur Agent-Datei oder zum Projekt, auf dem der Agent operiert.

### Empfehlungen
- **SOLLTE [SHOULD]** den System-Prompt mit Rolle und Grenzen des Agents beginnen und das erwartete Ausgabeformat entweder vor der Arbeitsweise **oder** als explizite abschließende „Report"-/Ausgabekontrakt-Phase nennen, die die Arbeitsweise abschließt. Das Haus-Template über die Agents dieses Plugins platziert den Ausgabekontrakt als diese abschließende Phase (ein „Report"- oder „Output"-Schritt nach den Analyse-Phasen); das ist eine bewusste, konforme Haus-Konvention, keine Reihenfolge-Abweichung, weil der Leser Rolle und Grenzen weiterhin zuerst antrifft und die Ausgabeform eindeutig deklariert ist. **Nicht** konform ist, die Ausgabeform implizit zu lassen oder über die Prozedur zu verstreuen
- **SOLLTE [SHOULD]** im System-Prompt ausdrücklich festhalten, ob der Agent Code schreibt oder nur recherchiert, da der aufrufende Claude diese Unterscheidung beim Dispatch treffen muss
- Jeder Agent deklariert seinen eigenen Output-Vertrag im System-Prompt (bereits von §Struktur gefordert); es gibt kein einzelnes repoweites Bericht-Schema. Review-, Audit- und Recherche-Agents **SOLLTEN [SHOULD]** einen strukturierten Bericht zurückgeben (zum Beispiel schweregrad-klassifizierte Befunde oder eine Coverage-Map) und **SOLLTEN [SHOULD]** mit einem expliziten Caller-Follow-ups-/Übergabe-Abschnitt abschließen; freitextliche Zusammenfassungen sind nur für triviale Einzelfakt-Antworten akzeptabel
- **SOLLTE [SHOULD]** den System-Prompt fokussiert halten; wächst er über etwa 200 Zeilen, sollte die Prosa gestrafft statt aufgeteilt werden—ein Agent bleibt eine einzelne Datei (siehe §Struktur), längeres Material wird also inlined oder, nur wenn wirklich zu groß, außerhalb des `agents/`-Baums abgelegt (zum Beispiel `agent-assets/<name>/`). Die ~200-Zeilen-Zahl ist eine lokale `nolte-shared`-Konvention; Anthropic dokumentiert kein Agent-Datei-Größenbudget, im Gegensatz zur weichen ~500-Zeilen-`SKILL.md`-Richtlinie, die `skill-management` für Skills kodifiziert
- **SOLLTE [SHOULD]** in der `description` sowohl positive Trigger („einsetzen, wenn…") als auch typische negative Fälle („nicht einsetzen für…") nennen, wenn Überschneidungen mit anderen Agents wahrscheinlich sind
- **KANN [MAY]** Beispiel-Aufrufe und erwartete Berichte inline im Agent-Body enthalten; sind sie zu groß zum Inlinen, werden sie außerhalb des `agents/`-Baums abgelegt (zum Beispiel `agent-assets/<name>/examples/`) und über relative Pfade referenziert—niemals in einem Schwester-Ordner `agents/<name>/`, den die rekursive Discovery als Phantom-Agent registrieren würde

### Wiederaufnehmbare Runs
- **MUSS [MUST]** `resumable: true` im Frontmatter des Agents deklarieren, wenn der Agent intern mehr als eine benannte Phase umspannt, die ein Zwischenartefakt produziert, das die Person bei Unterbrechung sonst verlieren würde, und `spec/claude/resumable-work/` für den On-Disk-Envelope, die Checkpoint-Kadenz, das Re-Invocation-Prompt und den Lebenszyklus befolgen; die tragenden Regeln leben in jener Spec und werden hier nicht dupliziert
- **MUSS [MUST]** Resume-Support im `description`-Text des Agents erwähnen, wann immer `resumable: true` gesetzt ist, damit der aufrufende Claude entsprechend routen kann
- **SOLLTE NICHT [SHOULD NOT]** `resumable: true` für Fire-and-Forget-Agents deklarieren, deren Vertrag ein einzelner Read-only-Pass ist, der billig neu startbar ist

## Akzeptanzkriterien
- [ ] Quelldatei existiert unter `agents/<name>.md` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Keine unterstützende Markdown-Datei liegt in einem Schwester-Ordner `agents/<name>/`; die rekursive Agent-Discovery würde sie als Phantom-Agent mit allen Tools registrieren. Unterstützende Artefakte, die sich nicht inlinen lassen, liegen außerhalb des `agents/`-Baums (überprüfbar mit `find agents -mindepth 2 -name '*.md'`, das keine Treffer liefert)
- [ ] Frontmatter parst als gültiges YAML und enthält mindestens `name`, `description` und `distribution`
- [ ] `name` im Frontmatter entspricht dem Dateinamen ohne `.md`
- [ ] `description` benennt konkrete Trigger, die der aufrufende Claude mit Nutzeranfragen abgleichen kann
- [ ] `description` folgt der §Description-Contract-Form — *was er tut*, dann konkrete Aktivierungs-Trigger, dann negative Fälle als `don't use for X → use <other>`, wo Überlappung mit einem anderen Artefakt wahrscheinlich ist
- [ ] Keine `description` bettet einen Beispiel- oder Kommentar-Block ein — keine `user:` / `assistant:`-Transkript-Züge und kein `<commentary>` / `<example>`-Tag-Paar; solche Inhalte leben im Agent-Body, nicht in der Routing-Prosa
- [ ] Delimitation in `description` bleibt knapp — ein einzelner Querverweis wird einer aufgezählten `don't use for …`-Kette vorgezogen, wo der Querverweis den Leser bereits korrekt routet
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
_Derzeit keine._
