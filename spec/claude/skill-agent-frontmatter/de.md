# Skill- und Agent-Frontmatter-Feldreferenz

Status: draft
Portfolio-Scope: local

## Kontext

Ein Skill (`SKILL.md`) und ein Agent (`agents/<name>.md`) tragen beide YAML-Frontmatter, und die Regeln dafür sind über drei Specs verteilt: `skill-management` besitzt die Skill-Felder, `agent-management` besitzt die Agent-Felder und `skill-agent-catalog` besitzt die Katalog-/Routing-Felder (`phase`, `summary`, die Use-Case-Metadaten). Jede dieser Specs ist für ihre eigene Fläche vollständig, aber es gibt keinen einzigen Ort, der die zwei Fragen beantwortet, die ein Autor oder Reviewer am häufigsten stellt: *Was ist das vollständige Feldset, das ich schreiben darf, und welche davon sind portable Claude-Code-Standardfelder gegenüber den eigenen Erfindungen dieses Repositories?* Ohne diese Landkarte lebt die Standard-vs-Erfindung-Unterscheidung nur in verstreuter Prosa (hier ein beiläufiges „erweitert die formale Agent-Skills-Spec", dort ein „nolte-shared-Plugin-Entscheidung"), und ein Autor kann nicht auf einen Blick erkennen, ob das Weglassen eines Feldes die Portabilität zu einer Nicht-Claude-Code-Laufzeit bricht oder nur ein hauslokales Katalog-Feature entfernt.

Diese Spec ist diese Landkarte. Sie ist eine **beschreibende, aggregierende Referenz**: Für jedes Skill- und Agent-Frontmatter-Feld hält sie die Aufgabe des Feldes fest, den Typ, die Limits, den Pflicht-/optional-Status, einen expliziten **Provenienz-Marker** (Anthropic-/Claude-Code-Standard, mit der Upstream-Quelle — gegenüber nolte-lokaler Erfindung) und einen Rückverweis auf die Spec, die die Regeln des Feldes **normativ besitzt**. Sie wiederholt diese Regeln bewusst nicht als zweite Quelle der Wahrheit; bei jeder Abweichung gewinnt die Owner-Spec. Sie wird zusammen mit einer maschinenlesbaren JSON-Schema-Begleitdatei ausgeliefert, die dasselbe Feldset auf der Parse-Fehler-Ebene kodiert, und sie definiert den Wartungsprozess, der Referenz, Schema, Owner und `scripts/validate_skills.py` davon abhält, auseinanderzudriften.

## Ziele

- Eine konsolidierte Referenz, die **jedes** Skill- und Agent-Frontmatter-Feld in einem einzigen Dokument abdeckt, sodass ein Autor oder Reviewer die gesamte Fläche auf einmal sieht.
- Ein expliziter **Provenienz-Marker** pro Feld — portabler Claude-Code-Standard (mit seiner Upstream-Quelle) gegenüber nicht-portabler nolte-lokaler Erfindung —, sodass die Portabilitäts-Konsequenz des Nutzens oder Weglassens eines Feldes sichtbar ist.
- Ein **Rückverweis** von jedem Feld auf die Spec, die seine Regeln normativ besitzt, sodass der Leser das autoritative Limit erreicht, ohne dass dieses Dokument es wiederholen (und zu forken riskieren) muss.
- Eine maschinenlesbare **JSON-Schema-Begleitdatei** auf der Parse-Fehler-Ebene, die das Feldset für Tooling spiegelt.
- Ein **Wartungsprozess**, der jedes neue oder geänderte Feld an eine Provenienz-Prüfung und ein Sync-Gate über die Owner, das Schema und den Validator bindet.

## Nicht-Ziele

- **Die Regeln der Owner-Specs zu wiederholen oder zu ersetzen.** Diese Referenz bildet ab und verweist; sie forkt nicht. Die normativen Limits bleiben in `skill-management`, `agent-management` und `skill-agent-catalog`. Dieses Dokument zum einzigen normativen Feld-Register zu erheben, auf das sich die Owner-Specs beziehen (das abgelehnte „Modell B"), ist explizit außerhalb des Rahmens.
- **Das Verhalten von `scripts/validate_skills.py` zu ändern.** Die JSON-Schema-Begleitdatei in den Validator zu verdrahten, ist eine Wartungs-Folgearbeit, kein Teil dieser Spec.
- **Die Skill-vs-Agent-Formatentscheidung** (Owner `skill-vs-agent`), das **Plugin-Scoping** (Owner `plugin-scoping`) und das **Katalog-Rendering** dieser Felder (Owner `skill-agent-catalog`).
- **Die Laufzeit-Semantik der Claude-Code-Standardfelder** über das Zitieren der Upstream-Quelle hinaus; das autoritative Verhalten ist das von Anthropic, verlinkt aus den Referenzen.

## Anforderungen

### Normatives Modell — beschreibend und aggregierend

- **MUSS** als **beschreibende, aggregierende Referenz** verfasst sein: Für jedes Feld hält sie die Attribute des Feldes fest und verweist zurück auf die Spec, die die normativen Regeln des Feldes besitzt. Sie **DARF NICHT** als das autoritative Register dargestellt werden, auf das sich die Owner-Specs beziehen.
- **MUSS** für jedes dokumentierte Feld einen Rückverweis auf den **normativen Owner**-Abschnitt tragen (`skill-management`, `agent-management` oder `skill-agent-catalog`); die hier gezeigten Limits und erlaubten Werte sind ein **Bequemlichkeits-Digest** dieses Owners, niemals eine konkurrierende Definition.
- **MUSS** jede Abweichung zwischen dieser Referenz und einer Owner-Spec zugunsten des **Owners** auflösen; eine Divergenz ist ein Wartungsdefekt in diesem Dokument (§Wartung), keine neue Regel.
- **DARF NICHT** eine Feldregel, ein Limit oder einen erlaubten Wert einführen, den keine Owner-Spec (oder die Upstream-Quelle Claude Code / Agent Skills) bereits definiert; ein Feld, das diese Referenz neu einschränken würde, gehört zuerst in seine Owner-Spec.

### Feldreferenz-Vertrag

- **MUSS** für **jedes** Feld in §Feldreferenz alle sieben Attribute dokumentieren: **Feldname**, **gilt-für** (`skill` / `agent` / `both`), **Typ**, **Limits oder erlaubte Werte**, **Pflicht-/optional-Status**, **Provenienz-Marker** und **normativer Owner**.
- **MUSS** in diesem einen Dokument **sowohl** Skills als auch Agents abdecken, unter Nutzung der geteilten `gilt-für`-Achse, sodass ein Feld, das beiden gemeinsam ist (zum Beispiel `name`, `description`, `model` und die Katalog-Felder), einmal statt zweimal beschrieben wird.
- **MUSS** ein Feld nur dort als **Pflicht** markieren, wo seine Owner-Spec es zu einem `MUSS` macht: `name` und `description` für beide Objekte, `phase` für beide Objekte und `distribution` für Agents. Jedes andere Feld ist **optional** (manche tragen ein bedingtes `MUSS`, zum Beispiel `resumable`, wenn ein Skill oder Agent mehr als ein Freigabe-Gate umspannt — in der Zeile des Feldes vermerkt und dem Owner überlassen).
- **MUSS** den Feldnamen und jeden technischen Wert in der Referenz verbatim aus der Quelle übernehmen; Feldnamen sind Identifier und werden zwischen der kanonischen und der übersetzten Datei nicht übersetzt.

### Provenienz-Taxonomie

- **MUSS** jedes Feld mit genau einem **Provenienz-Marker** klassifizieren:
  - **Standard**: ein Feld, das durch die formale Agent-Skills-Spezifikation ([R1](#referenzen)), den Anthropic-Plattform-Validator ([R2](#referenzen)) oder das dokumentierte Claude-Code-Frontmatter ([R3](#referenzen) für Skills, [R7](#referenzen) für Agents) definiert ist. Standardfelder sind portabel zur Claude-Code-Laufzeit; die Agent-Skills-Spec-Teilmenge (`name`, `description`) ist portabel zu jeder konformen Agent-Skills-Laufzeit.
  - **nolte**: ein Feld, das dieses Repository für Katalog-Rendering, Routing oder Hauskonvention erfunden hat. Ein nolte-Feld ist **nicht portabel**: Eine Nicht-nolte-Laufzeit ignoriert es, und der Anthropic-Plattform-Validator behandelt unbekannte Felder nach seinen eigenen Regeln.
- **MUSS** für jedes **Standard**-Feld die Upstream-Quelle zitieren ([R1](#referenzen), [R2](#referenzen), [R3](#referenzen), [R7](#referenzen)), sodass die Portabilitäts-Aussage prüfbar ist.
- **MUSS** jedes derzeit von diesem Repository erfundene Feld als **nolte** erfassen: `distribution`, `tags`, `phase`, `summary`, `summary_<lang>`, `use_when`, `dont_use_when`, `see_also`, `examples` und `resumable`.
- **MUSS** die zwei querschnittlichen Reservierungen bewahren, die die Owner bereits deklarieren: Die reservierten Tokens `anthropic` und `claude` sind in `name` verboten (nicht in anderen Feldern), und das Unterstrich-Präfix (zum Beispiel `_translation-pending`) ist für Katalog-Generator-Auto-Tags reserviert und **DARF NICHT** in autor-deklarierten `tags` erscheinen.

### Maschinenlesbare Begleitdatei

- **MUSS** eine JSON-Schema-Begleitdatei unter `spec/schemas/skill-agent-frontmatter-v1.0.schema.yaml` ausliefern (JSON-Schema draft 2020-12), im Hausstil von `spec/schemas/spec-config-v1.0.schema.yaml` und `portfolio/schemas/tech-stack-v1.0.schema.yaml`.
- **MUSS** das Schema auf die **Parse-Fehler-Klasse** beschränken — Feld-Präsenz, Typ, primitive Limits (String-Länge, Listen-Länge, Enum-Zugehörigkeit, Pattern) — und **DARF NICHT** Semantik kodieren, die eine Owner-Regel forken würde (zum Beispiel die repoübergreifende Auflösbarkeit von `dont_use_when[].alternative`, die eine Audit-Zeit-Prüfung in `skill-agent-catalog` bleibt).
- **MUSS** das Schema konsistent mit §Feldreferenz halten: Jedes hier als Pflicht markierte Feld ist dort `required`, jedes Enum hier ist dort ein `enum`/`pattern`, und jeder Provenienz-Marker bildet auf eine Schema-Beschreibungsnotiz ab.
- **KANN** in einer späteren Änderung von `scripts/validate_skills.py` konsumiert werden; das Schema ist eine Begleitdatei, die der Validator übernehmen kann, und diese Spec verlangt diese Verdrahtung nicht.

### Wartung

- **MUSS** einen `## Wartung`-Abschnitt tragen, der regelt, wie ein Feld in dieser Referenz **hinzugefügt, geändert oder entfernt** wird.
- **MUSS** für jedes neue oder geänderte Feld eine **Provenienz-Prüfung** verlangen: Der Autor klassifiziert das Feld als **Standard** (und verlinkt die Upstream-Quelle, die es einführte) oder als **nolte** (und nennt die Owner-Spec und den Routing-/Katalog-Grund) und hält das Ergebnis in der Zeile des Feldes fest.
- **MUSS** bei jeder Feldänderung ein **Sync-Gate** verlangen: Die Referenz-Zeile, die JSON-Schema-Begleitdatei, die normative Owner-Spec und (wo das Feld validator-durchgesetzt ist) `scripts/validate_skills.py` werden in **derselben Änderung** aktualisiert, oder die Divergenz wird explizit benannt; ein Feld, das in einer Fläche erscheint, aber nicht in den anderen, ist ein Defekt.
- **MUSS** das Sync-Gate an einen **PR-Checklisten-Punkt** binden, sodass ein Reviewer bestätigt, dass die vier Flächen vor dem Merge übereinstimmen.
- **SOLLTE** die Provenienz-Prüfung erneut ausführen, wenn Claude Code oder die Agent-Skills-Spec ein neues Frontmatter-Feld ausliefert, sodass ein Feld, das upstream zum Standard wird, von **nolte** (oder abwesend) zu **Standard** neu markiert wird, statt still falsch etikettiert zu bleiben.

## Feldreferenz

Die Tabellen unten sind ein **Bequemlichkeits-Digest**. Die **Owner**-Spalte nennt die normative Quelle; bei jeder Abweichung gewinnt der Owner (§Normatives Modell). Feldnamen und Werte sind verbatim-Identifier und werden zwischen den Sprachdateien nicht übersetzt.

Provenienz-Marker: **Standard·AgentSkills** (Agent-Skills-Spec [R1], portabel zu jeder konformen Laufzeit), **Standard·Platform** (Anthropic-Plattform-Validator [R2]), **Standard·CC** (Claude-Code-Frontmatter [R3]/[R7], nur portabel zur Claude-Code-Laufzeit), **nolte** (Erfindung dieses Repositories, nicht portabel).

### Pflichtfelder

| Feld | gilt für | Typ | Limits / erlaubte Werte | Provenienz | Owner |
|---|---|---|---|---|---|
| `name` | both | string | 1–64 Zeichen; lowercase ASCII Buchstaben/Ziffern/Bindestriche; kein führender/abschließender Bindestrich; kein `--`; kein reserviertes Token `anthropic`/`claude`; keine XML-Tags; gleich dem Ordner-/Dateinamen | Standard·AgentSkills + Standard·Platform | `skill-management` §Frontmatter validation · `agent-management` §Structure |
| `description` | both | string | nicht-leer; ≤1024 Zeichen; dritte Person; nennt *was* und *wann*; keine XML-Tags | Standard·AgentSkills + Standard·Platform | `skill-management` §Frontmatter validation · `agent-management` §Structure |
| `distribution` | agent | enum | genau `plugin` oder `project` | nolte | `agent-management` §Distribution |
| `phase` | both | enum | eines von `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`; niemals eine Liste | nolte | `skill-agent-catalog` §Phase classification |

### Standard-Optionalfelder — Claude Code, Skill-Fläche

| Feld | gilt für | Typ | Limits / erlaubte Werte | Provenienz | Owner |
|---|---|---|---|---|---|
| `when_to_use` | skill | string | kombiniertes `description` + `when_to_use` unter 1.536 Zeichen (Laufzeit schneidet darüber ab) | Standard·CC | `skill-management` §Frontmatter validation / §Runtime & lifecycle |
| `argument-hint` | skill | string | freiformiger Hinweis für Slash-Command-Argumente | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `arguments` | skill | string | Argument-Deklaration für den Slash-Command | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `disable-model-invocation` | skill | boolean | `true` sperrt modell-getriebene Invokation (nur nutzer-invoziert); blockiert Subagent-`skills:`-Preload; nicht setzen bei einem Skill, den ein anderer Skill mid-flow dispatcht | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `user-invocable` | skill | boolean | ob der Skill als `/`-Command exponiert wird | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `allowed-tools` | skill | Liste von Strings | eine **Berechtigungsgewährung** (vorab-genehmigte Aufrufe), keine Einschränkung | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `context` | skill | enum | `fork`: den Skill in einem geforkten Subagent-Kontext ausführen (mit `agent`) | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `agent` | skill | string | Agent-Typ, der Tools/Modell liefert bei `context: fork` | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `paths` | skill | Liste von Globs | Gate nur auf **automatische** Invokation; explizites `/<plugin>:<name>` funktioniert immer; kein Routing-Budget-Hebel | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `shell` | skill | string | Shell-Bindung für die Command-Ausführung des Skills | Standard·CC | `skill-management` §Runtime & lifecycle awareness |

### Standard-Optionalfelder — Claude Code, Agent-Fläche

| Feld | gilt für | Typ | Limits / erlaubte Werte | Provenienz | Owner |
|---|---|---|---|---|---|
| `tools` | agent | Liste von Strings | geringste Autorität; **Weglassen gewährt jedes geerbte Tool** (eine Sprawl-Falle); read-only Agents tragen keine Write-/Edit-/Exec-Tools; niemals `Agent` listen | Standard·CC | `agent-management` §Tool access |
| `disallowedTools` | agent | Liste von Strings | Denylist, subtrahiert vom geerbten Set; vor `tools` angewendet | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `permissionMode` | agent | enum | `default`/`acceptEdits`/`auto`/`dontAsk`/`bypassPermissions`/`plan`; **ignoriert bei `distribution: plugin`** (DARF NICHT gesetzt werden) | Standard·CC | `agent-management` §Plugin-distribution security constraints |
| `maxTurns` | agent | integer | begrenzt agentische Turns vor dem Stopp | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `skills` | agent | Liste von Strings | preloaded vollen Skill-Inhalt beim Start; überspringt `disable-model-invocation: true`-Skills | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `mcpServers` | agent | Mapping / Refs | Subagent-eigene MCP-Server; **ignoriert bei `distribution: plugin`** (DARF NICHT gesetzt werden) | Standard·CC | `agent-management` §Plugin-distribution security constraints |
| `hooks` | agent | Mapping | Lifecycle-Hooks; **ignoriert bei `distribution: plugin`** (DARF NICHT gesetzt werden) | Standard·CC | `agent-management` §Plugin-distribution security constraints |
| `memory` | agent | enum | `user`/`project`/`local`; aktiviert Read/Write/Edit und Memory-Curation-Prompt | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `background` | agent | boolean | immer als Background-Task laufen; Berechtigungen vorab-genehmigt | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `isolation` | agent | enum | `worktree`: in einem temporären git-Worktree laufen | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `color` | agent | enum | `red`/`blue`/`green`/`yellow`/`purple`/`orange`/`pink`/`cyan` | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `initialPrompt` | agent | string | erster User-Turn, wenn der Agent als Hauptsession via `--agent` läuft | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |

### Standard-Optionalfelder — Claude Code, beide Flächen

| Feld | gilt für | Typ | Limits / erlaubte Werte | Provenienz | Owner |
|---|---|---|---|---|---|
| `model` | both | string | Modell-Alias (`sonnet`/`opus`/`haiku`), eine volle Modell-ID oder `inherit`; **Default `inherit`** bei Weglassen | Standard·CC | `agent-management` §Model selection · `skill-management` §Runtime & lifecycle awareness |
| `effort` | both | enum | `low`/`medium`/`high`/`xhigh`/`max`; überschreibt den Session-Effort | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields · `skill-management` §Runtime & lifecycle awareness |

### nolte-Optionalfelder — Katalog, Routing, Hauskonvention

| Feld | gilt für | Typ | Limits / erlaubte Werte | Provenienz | Owner |
|---|---|---|---|---|---|
| `tags` | both | Liste von Strings | lowercase ASCII kebab-case; jedes ≤30 Zeichen; ≤5 Einträge; kein Eintrag beginnt mit `_` (reserviert für Generator-Auto-Tags) | nolte | `skill-management` / `agent-management` §Tag vocabulary · `skill-agent-catalog` |
| `summary` | both | string | ≤200 Zeichen; Plain-String; Englisch (kanonisch) | nolte | `skill-agent-catalog` §Per-language short summary |
| `summary_<lang>` | both | string | ≤200 Zeichen; Plain-String; eines pro zusätzlicher Docs-Sprache (zum Beispiel `summary_de`) | nolte | `skill-agent-catalog` §Per-language short summary |
| `use_when` | both | Liste von Strings | ≤6 Einträge; jeder ≤120 Zeichen; ein Trigger-Szenario pro Eintrag | nolte | `skill-agent-catalog` §Use-case metadata |
| `dont_use_when` | both | Liste von Mappings | Schlüssel `situation` (≤120 Zeichen) + `alternative` (ein auffindbarer Artefakt-`name`); ≤6 Einträge; `alternative` muss auflösen, sonst schlägt der Docs-Build fehl | nolte | `skill-agent-catalog` §Use-case metadata |
| `see_also` | both | Liste von Strings | ≤8 Einträge; jeder ein auffindbarer Artefakt-`name`; muss auflösen | nolte | `skill-agent-catalog` §Use-case metadata |
| `examples` | both | Liste von Mappings | Schlüssel `prompt` (≤200 Zeichen) + `outcome` (≤200 Zeichen); ≤4 Einträge | nolte | `skill-agent-catalog` §Use-case metadata |
| `resumable` | both | boolean | `true`, wenn das Artefakt mehr als ein Freigabe-Gate oder mehr als eine benannte Phase umspannt; dann muss `description` Resume-Support erwähnen | nolte | `skill-management` / `agent-management` §Resumable runs · `resumable-work` |

### Querschnittliche Reservierungen

- **Reservierte Tokens.** `anthropic` und `claude` **DÜRFEN NICHT** irgendwo in `name` erscheinen; andere Felder (`description`, `tags`, `summary`, …) KÖNNEN sie erwähnen. Eine enge geschlossene Ausnahme existiert für Artefakte, die eine Claude-Code-/Anthropic-Fläche autoren, gated durch einen `## Reserved-token rationale`-Body-Abschnitt — siehe `skill-management` §Frontmatter validation und `agent-management` §Structure.
- **Reserviertes Tag-Präfix.** Ein führender Unterstrich (`_translation-pending`) markiert ein generator-emittiertes Auto-Tag; autor-deklarierte `tags` **DÜRFEN** es **NICHT** nutzen — siehe `skill-agent-catalog` §Per-language short summary.
- **Kein Per-Artefakt-Versionsfeld.** Weder Skills noch Agents tragen ein `version`- oder Kompatibilitätsfeld; Versionierung ist plugin-scoped und Per-Artefakt-Historie ist git — siehe `skill-management` §Distribution und `agent-management` §Distribution.

## Wartung

Diese Referenz bleibt nur wahr, wenn sie im Gleichschritt mit den Flächen ändert, die sie abbildet. Ein Feld lebt an bis zu vier Stellen: dieser Referenz-Zeile, der JSON-Schema-Begleitdatei, der normativen Owner-Spec und `scripts/validate_skills.py` (wenn das Feld validator-durchgesetzt ist). Der Prozess unten hält sie ausgerichtet.

**Wenn ein Feld hinzugefügt, geändert oder entfernt wird:**

1. **Provenienz-Prüfung.** Das Feld als **Standard** klassifizieren (die Upstream-Quelle nennen — Agent-Skills-Spec, Anthropic-Plattform oder Claude-Code-Docs —, die es einführte) oder als **nolte** (die Owner-Spec und den Routing-/Katalog-Grund nennen). Das Ergebnis in der §Feldreferenz-Zeile des Feldes festhalten.
2. **Zuerst den Owner aktualisieren.** Die normative Regel lebt in `skill-management`, `agent-management` oder `skill-agent-catalog`. Den Owner ändern, dann das Digest dieser Referenz zum Abgleich aktualisieren — nie umgekehrt.
3. **Die vier Flächen in einer Änderung synchronisieren.** Die §Feldreferenz-Zeile, `spec/schemas/skill-agent-frontmatter-v1.0.schema.yaml`, die Owner-Spec und (wenn validator-durchgesetzt) `scripts/validate_skills.py` werden zusammen aktualisiert, oder die bewusste Divergenz wird explizit benannt. Ein Feld, das in einer Fläche vorhanden ist, aber in einer anderen fehlt, ist ein Defekt.
4. **Das Schema auf der Parse-Fehler-Klasse halten.** Ein neues Limit, das eine primitive Einschränkung ist (Länge, Enum, Pattern), kommt ins Schema; eine repoübergreifende oder semantische Prüfung (Auflösbarkeit, Earliest-Phase-Heuristik) bleibt eine Audit-Zeit-Regel im Owner und wird **nicht** im Schema kodiert.
5. **Bei Upstream-Änderung neu markieren.** Wenn Claude Code oder die Agent-Skills-Spec ein neues Frontmatter-Feld ausliefert oder eines befördert, die Provenienz-Prüfung erneut ausführen, sodass ein Feld, das upstream zum Standard wird, von **nolte** (oder abwesend) zu **Standard** neu markiert wird.

**PR-Checklisten-Punkt** (jedem PR hinzugefügt, der die Definition eines Frontmatter-Feldes berührt):

- [ ] Frontmatter-Feldänderung: Provenienz geprüft, und die §Feldreferenz-Zeile, die JSON-Schema-Begleitdatei, die Owner-Spec und `validate_skills.py` (falls durchgesetzt) stimmen alle überein — oder die Divergenz ist benannt.

## Akzeptanzkriterien

- [ ] `spec/claude/skill-agent-frontmatter/en.md` (kanonisch) und `de.md` (Übersetzung) existieren, `Status: draft`, `Portfolio-Scope: local`, strukturell synchron.
- [ ] Jedes Feld in §Feldreferenz deklariert alle sieben Attribute (name, gilt-für, Typ, Limits/erlaubte Werte, Pflicht-Status via Tabellen-Platzierung, Provenienz, Owner).
- [ ] Sowohl Skills als auch Agents sind im einen Dokument über die `gilt-für`-Achse abgedeckt; kein beiden gemeinsames Feld wird zweimal beschrieben.
- [ ] Genau `name`, `description`, `phase` (both) und `distribution` (agent) sind als Pflicht platziert; jedes andere Feld ist optional.
- [ ] Jedes Feld trägt genau einen Provenienz-Marker; jedes **Standard**-Feld zitiert eine Upstream-Quelle ([R1](#referenzen), [R2](#referenzen), [R3](#referenzen), [R7](#referenzen)); die zehn nolte-Felder (`distribution`, `tags`, `phase`, `summary`, `summary_<lang>`, `use_when`, `dont_use_when`, `see_also`, `examples`, `resumable`) sind als **nolte** markiert.
- [ ] Jede Feld-Zeile nennt einen normativen Owner-Abschnitt, und das Dokument stellt fest, dass der Owner bei jeder Abweichung gewinnt.
- [ ] `spec/schemas/skill-agent-frontmatter-v1.0.schema.yaml` existiert (draft 2020-12), deckt nur die Parse-Fehler-Klasse ab und ist konsistent mit §Feldreferenz (Pflicht-Set, Enums, Limits).
- [ ] Ein `## Wartung`-Abschnitt definiert die Provenienz-Prüfung, das Vier-Flächen-Sync-Gate und einen PR-Checklisten-Punkt.
- [ ] Das Dokument wiederholt kein Owner-Limit als konkurrierende Definition; jedes gezeigte Limit ist ein Digest mit einem Rückverweis.
- [ ] `task test` besteht und die geänderte Spec-Prosa ist Vale-sauber (aus dem Worktree ausgeführt).

## Referenzen

- [R1] Agent Skills, formale Spezifikation: <https://agentskills.io/specification>
- [R2] Skill authoring best practices, Anthropic-Plattform-Docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R3] Extend Claude with skills, Claude-Code-Docs: <https://code.claude.com/docs/en/skills>
- [R4] `skill-management` (normativer Owner des Skill-Frontmatters): `spec/claude/skill-management/`
- [R5] `agent-management` (normativer Owner des Agent-Frontmatters): `spec/claude/agent-management/`
- [R6] `skill-agent-catalog` (normativer Owner der Katalog-/Routing-Felder): `spec/claude/skill-agent-catalog/`
- [R7] Create custom subagents, Claude-Code-Docs: <https://code.claude.com/docs/en/sub-agents>

## Offene Fragen

_Derzeit keine._
