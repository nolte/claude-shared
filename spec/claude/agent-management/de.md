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
- Einrichtung nachgelagerter Projekte und `.claude/`-Konfiguration
- Vorgabe konkreten Agent-Verhaltens jenseits struktureller Regeln
- Die Orchestrierungslogik im aufrufenden Claude (welcher Agent wann gewählt wird)

## Anforderungen

### Struktur
- **MUSS [MUST]** als einzelne Markdown-Datei mit dem Namen `<name>.md` angelegt werden, wobei `<name>` ASCII-Kebab-Case ist
- **MUSS [MUST]** YAML-Frontmatter mit den Feldern `name`, `description` und `distribution` enthalten
- **MUSS [MUST]** `name` exakt auf den Dateinamen ohne die Endung `.md` setzen
- **MUSS [MUST]** eine `description` schreiben, die konkrete nutzerseitige Trigger und Aufgabenformen benennt („einsetzen, wenn der Nutzer X fragt", „aufrufen für Y") statt abstrakter Fähigkeiten, damit der aufrufende Claude zuverlässig über das Dispatchen entscheiden kann
- **MUSS [MUST]** `distribution` exakt auf einen der Werte `plugin` oder `project` setzen und damit die beabsichtigte Auslieferungsform deklarieren (siehe „Distribution" unten); der Autor trifft diese Wahl bewusst bei der Erstellung und ändert sie nur durch Neuausrichtung des Agents auf die andere Form
- **MUSS [MUST]** im Markdown-Körper einen System-Prompt enthalten, der den Agent auf genau eine Verantwortlichkeit eingrenzt und die erwartete Ausgabeform benennt
- **MUSS [MUST]** Frontmatter-Feldnamen und Werte technischer Bezeichner auf Englisch halten: `name`, `distribution`, `tools`-Einträge, `model` und `tags`-Einträge bleiben unabhängig von der Dokumentationssprache des Projekts in Englisch
- **SOLLTE [SHOULD]** den `description`-Wert und den System-Prompt-Body aus Token-Effizienz- und teamweiter Portabilitätsgründen auf Englisch halten; Agenten mit `distribution: project` für ein Projekt, das in seiner Wurzel-Konventionsdatei (typischerweise `CLAUDE.md`) eine nicht-englische Dokumentationssprache deklariert, **DÜRFEN [MAY]** stattdessen `description` und Body in der Hauptdokumentationssprache des Projekts verfassen. Agenten mit `distribution: plugin` **MÜSSEN [MUST]** in Description und Body englischsprachig bleiben, da sie über mehrere Downstream-Projekte mit potenziell unterschiedlichen Sprachen ausgeliefert werden
- Der Agent **DARF [MAY]** dennoch angewiesen werden, dem Nutzer in dessen Sprache zu antworten — unabhängig davon, in welcher Sprache der Body verfasst ist
- **MUSS [MUST]** in sich geschlossen sein — unterstützende Artefakte (Referenzen, Beispiele, Prompt-Bausteine) liegen neben der Agent-Datei in einem Schwester-Ordner `agents/<name>/` und werden über relative Pfade referenziert
- **KANN [MAY]** ein optionales `tags`-Feld im YAML-Frontmatter enthalten: eine Liste von kleingeschriebenen ASCII-Kebab-Case-Strings, jeder ≤30 Zeichen, mit höchstens 5 Einträgen; Tags liefern thematische Gruppierung, damit Katalog (`skill-agent-catalog`) und Peer-Cluster-Abgleich (`skill-vs-agent` §Portfolio-weite Konsistenz) nach Thema durchstöbert werden können

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
- **MUSS [MUST]** ein `tools`-Feld im Frontmatter deklarieren, wenn der Agent eingeschränkt werden soll; das Feld nur dann weglassen, wenn der Agent tatsächlich die volle Tool-Oberfläche benötigt
- **MUSS [MUST]** `tools` auf die minimal notwendige Menge für die Verantwortlichkeit des Agents beschränken (Prinzip der minimalen Rechte); rein lesende Agents **DÜRFEN NICHT [MUST NOT]** Schreib-, Edit- oder Ausführungs-Tools erhalten
- **SOLLTE [SHOULD]** dedizierte Tools (`Read`, `Grep`, `Glob`, `Edit`) gegenüber `Bash`-Äquivalenten bevorzugen, wenn beides möglich wäre

### Modell-Wahl
- **KANN [MAY]** ein `model`-Feld im Frontmatter deklarieren (`opus`, `sonnet`, `haiku`), wenn der Agent einen klaren Kosten-/Qualitäts-Abwägungsfall hat; ohne Feld wird das Modell des Aufrufers übernommen
- **SOLLTE [SHOULD]** ein fixiertes `model` im System-Prompt oder in einem Kommentar begründen, damit spätere Leser verstehen, warum es festgelegt wurde

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
- **SOLLTE [SHOULD]** den System-Prompt fokussiert halten; wächst er über etwa 200 Zeilen, sollten längere Referenzen in Dateien unter `agents/<name>/` ausgelagert werden
- **SOLLTE [SHOULD]** in der `description` sowohl positive Trigger („einsetzen, wenn…") als auch typische negative Fälle („nicht einsetzen für…") nennen, wenn Überschneidungen mit anderen Agents wahrscheinlich sind
- **KANN [MAY]** Beispiel-Aufrufe und erwartete Berichte in einem Schwester-Ordner `agents/<name>/examples/` enthalten

## Akzeptanzkriterien
- [ ] Quelldatei existiert unter `agents/<name>.md` in claude-shared mit `<name>` in ASCII-Kebab-Case
- [ ] Frontmatter parst als gültiges YAML und enthält mindestens `name`, `description` und `distribution`
- [ ] `name` im Frontmatter entspricht dem Dateinamen ohne `.md`
- [ ] `description` benennt konkrete Trigger, die der aufrufende Claude mit Nutzeranfragen abgleichen kann
- [ ] Falls `tags` im Frontmatter deklariert ist, ist jeder Eintrag ein kleingeschriebener ASCII-Kebab-Case-String ≤30 Zeichen, und die Liste enthält höchstens 5 Einträge
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

## Offene Fragen
- Soll der Dateiname (und damit `name`) exakt dem `subagent_type`-String entsprechen, oder ist eine Mapping-Schicht erlaubt?
- Brauchen Agents Versions- oder Kompatibilitäts-Metadaten, während sie sich weiterentwickeln, oder genügt die Git-Historie der Agent-Datei?
- Wo verläuft die Grenze zwischen einem Skill und einem Agent? Wann soll eine Fähigkeit das eine sein, wann das andere?
- Sollen Agents deklarieren, an welche anderen Agents sie delegieren dürfen, oder bleibt Delegation vollständig dem aufrufenden Claude überlassen?
- Gibt es eine gemeinsame Konvention, wie Agents zurückmelden (strukturiert vs. freitextliche Zusammenfassung), oder ist das pro Agent?
