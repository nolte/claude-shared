# Claude-Agent-Review

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Bedarf oder welche Einschränkung treibt sie? -->

Die `agent-management`-Spec definiert, wie ein Agent *erstellt* wird — Dateiname, YAML-Frontmatter (`name`, `description`, `distribution`), Tool-Scope, System-Prompt-Form, Quell- und Laufzeitpfade. Was sie nicht definiert, ist, wie ein Agent *reviewt* wird: welche Regeln ein Reviewer prüft, in welcher Reihenfolge und welches Deliverable das Review hinterlässt. Ohne eine geteilte Review-Prozedur erzeugen zwei Reviewer desselben Agents inkompatible Ergebnisse, die Rationale-Regel aus `skill-vs-agent` erodiert still, Tool-Scope-Drift sammelt sich unbemerkt an, und Plugin-Entwickler, die die Review-Ausgabe konsumieren, können nicht gegen eine stabile Form skripten. Diese Spec definiert die bindende Review-Prozedur für Agents im `nolte-shared`-Plugin; sie verweist auf `agent-management` und `skill-vs-agent` als autoritative Finding-Quellen und delegiert den Output-Format-Vertrag an `review-plan`. Ein Agent-Review erzeugt genau ein `review-plan`-Artefakt unter `.audits/agent-review/<agent-name>.md`; sobald jeder Punkt verarbeitet ist, wird der Plan gelöscht, und seine Git-Historie bleibt als Audit-Trail.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, ergebnisorientiert. -->
- Jedes Agent-Review wendet denselben Satz von Checks aus `agent-management` und `skill-vs-agent` in derselben Reihenfolge mit demselben Schweregrad-Mapping an
- Review-Output ist ein `review-plan`-Artefakt — parsbar, abarbeitbar und pro Finding auf eine konkrete Spec-Anforderung zurückführbar
- Agent-Autoren können das Review an ihrer eigenen Arbeit fahren, bevor sie sie einreichen; ein späterer Reviewer (Mensch oder LLM) erzielt auf demselben Quellbaum identische Ergebnisse
- Plugin-Entwickler können gegen die Review-Ausgabe skripten (Plan-Dateien parsen, Merges auf offene `Critical` gaten, offene Reviews zählen), ohne reviewer-spezifische Konventionen modellieren zu müssen
- Das Review erzwingt agent-spezifische Invarianten, die für Skills nicht gelten — minimaler `tools`-Scope, Read-only-Agents ohne Write-/Edit-/Execution-Tools, genau einmal deklariertes `distribution`, kein Skill-Tool-Dispatch im Agent-Body — damit sie nicht still über die Zeit regressieren

## Nicht-Ziele
<!-- Was explizit außerhalb des Scopes liegt. Verhindert Scope Creep. -->
- Definition, was ein Agent auf Disk *ist* — das gehört zu `agent-management`
- Entscheidung, ob ein Feature Skill oder Agent hätte werden sollen — das gehört zu `skill-vs-agent`; diese Spec prüft nur, dass die Entscheidung *dokumentiert* ist
- Vorgabe des Output-Datei-Formats — das gehört zu `review-plan`
- Review von Skills — das deckt `skill-review` mit symmetrischer Struktur ab
- Ersetzung der quartalsweisen portfolioweiten Reconciliation — das gehört zu `spec-drift-audit`
- Linter- und Markdown-Style-Checks, die bereits von `task lint` / Vale / Pre-Commit-Hooks erzwungen werden — diese bleiben bei ihrem eigenen Tooling
- Laufzeit- oder Verhaltens-Korrektheit des Agents (ob ein Dispatch tatsächlich die behauptete Report-Form liefert) — diese Spec reviewt das **erstellte Artefakt**, nicht eine Live-Ausführung

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUST, SHOULD, MAY. Eine atomare Anforderung pro Bullet. -->

### Review-Scope

- **MUSS [MUST]** genau einen Agent als Eingabe nehmen, identifiziert durch den Pfad `agents/<name>.md` in einem `nolte-shared`-Quellbaum oder den äquivalenten Runtime-Pfad `.claude/agents/<name>.md` / `~/.claude/agents/<name>.md` beim Review einer Consumer-Kopie
- **MUSS [MUST]** folgendes in dieser Reihenfolge als Review-Oberfläche behandeln: YAML-Frontmatter, den Markdown-Body (Rolle, Output-Format, Prozedur, Rationale), jedes Geschwister-Asset unter `agents/<name>/`, das aus dem Body referenziert wird (Beispiele, Langform-Referenzen, Prompt-Fragmente)
- **MUSS NICHT [MUST NOT]** mehr als einen Agent pro Plan reviewen; parallele Reviews mehrerer Agents emittieren je einen `review-plan` pro Ziel
- **KANN [MAY]** den Scope auf einen bestimmten Aspekt einschränken (nur Frontmatter, nur Tools, nur Rationale), wenn das Review durch eine gezielte Änderung ausgelöst wurde, und **MUSS [MUST]** die Einschränkung im `## Scope`-Abschnitt des Plans dokumentieren

### Checks aus `agent-management`

- **MUSS [MUST]** für jede MUST / SHOULD / MAY-Regel der kanonischen `agent-management`-Spec einen Check laufen lassen und pro fehlgeschlagenem Check ein Finding erzeugen, mit Zitat der auslösenden Regel im eckigen Klammerpräfix gemäß `review-plan`
- **MUSS [MUST]** die Schweregrade wie folgt zuordnen und **MUSS NICHT [MUST NOT]** ohne dokumentierte Ausnahme davon abweichen:
  - Ein fehlgeschlagenes MUST → `Critical`
  - Ein fehlgeschlagenes SHOULD → `Warning`
  - Ein fehlgeschlagenes MAY, von dem der Agent klar profitieren würde → `Suggestion`
  - Eine Beobachtung, die keine Regel abdeckt, die ein künftiger Reviewer aber kennen möchte → `Info`
- **MUSS [MUST]** folgende agent-spezifische Invarianten als jeweils eigene Checks explizit verifizieren:
  - Dateiname entspricht `<name>.md` in ASCII-Kebab-Case
  - `name` im Frontmatter entspricht dem Dateinamen ohne `.md`
  - `description` nennt konkrete Trigger (mindestens positive; negative Trigger SOLLTEN vorhanden sein, wenn Überlappung mit anderen Artefakten plausibel ist)
  - `distribution` ist genau `plugin` oder `project` — kein anderer Wert, kein fehlendes Feld
  - `tools` fehlt (volle Tool-Oberfläche im Body begründet) oder ist auf das für die deklarierte Verantwortung nötige Minimum beschränkt
  - Read-only-Agents (Agents, deren deklarierte Verantwortung Research, Review, Audit oder Reporting ist) haben **keine** Write-, Edit- oder Execution-Tools — das Vorhandensein von Edit, Write, Bash, NotebookEdit in der `tools`-Liste eines Read-only-Agents ist ein `Critical`
  - Agent-Body ruft das Skill-Tool **nicht** im Namen des Nutzers — erkannt durch Grep im Body nach `Skill(`, `Skill tool` oder äquivalenten Dispatch-Phrasen; jeder Treffer ist ein `Critical` gemäß `skill-vs-agent`
  - Keine hartcodierten absoluten Pfade im Body oder in Geschwister-Assets
  - Frontmatter-Feldnamen und Werte technischer Bezeichner (`name`, `distribution`, `tools`, `model`, `tags`) sind in Englisch; der `description`-Wert und der System-Prompt-Body folgen `agent-management.Struktur` — standardmäßig Englisch, mit Projektsprachen-Ausnahme für `distribution: project`-Agents, deren konsumierendes Projekt eine nicht-englische Dokumentationssprache deklariert und sie für Agent-Prosa autorisiert. Verifiziere die Projekt-Autorisierung (typischerweise `CLAUDE.md`) bevor ein ansonsten als `Critical` zu wertender Befund auf `Info` heruntergestuft wird

### Modell-Wahl-Checks

- **MUSS [MUST]** bei gesetztem `model`-Frontmatter-Feld verifizieren, dass dessen Wert exakt einer von `opus`, `sonnet` oder `haiku` gemäß `agent-management` ist; jeder andere Wert ist ein `Critical`
- **MUSS [MUST]** bei fixiertem `model` verifizieren, dass der System-Prompt oder ein begleitender Kommentar eine Begründung für die Wahl nennt; Fehlen ist ein `Warning` und spiegelt das SHOULD aus `agent-management`
- **SOLLTE [SHOULD]** einen Plausibilitäts-Check auf das fixierte `model` fahren: ein Read-only- oder Reporting-Agent, fixiert auf `opus` ohne genannte Begründung, erzeugt ein `Suggestion`; ein komplexer Audit- oder Planungs-Agent, fixiert auf `haiku` ohne genannte Begründung, erzeugt ein `Suggestion`
- **KANN [MAY]** ein `Info`-Finding erzeugen, wenn das `model`-Feld fehlt, und dabei festhalten, dass der Agent das Modell des Aufrufers gemäß `agent-management` erbt

### Checks aus `skill-vs-agent`

- **MUSS [MUST]** bestätigen, dass der Agent-Body einen **Rationale-Abschnitt** enthält, der mindestens eine entscheidende Dimension für die Agent-statt-Skill-Wahl benennt; dessen Fehlen ist ein `Critical`
- **SOLLTE [SHOULD]** verifizieren, dass mindestens eine Gegen-Dimension benannt ist, wenn die Entscheidung knapp war — Fehlen ist ein `Suggestion`, kein `Critical`, konsistent zur SHOULD-Formulierung in `skill-vs-agent`
- **MUSS [MUST]** einen Duplikat-Capability-Check fahren: jede andere `agents/*.md` und `skills/*/SKILL.md` `description`-Zeile auf semantische Überlappung grepen; jede plausible Überlappung erzeugt ein `Warning`, das das Peer-Artefakt und die Überlappung benennt, damit der Autor vor dem Landen einen Merge, Rename oder klareren Split vorschlagen kann

### Tool-Scope-Checks

- **MUSS [MUST]** für jedes in `tools` deklarierte Werkzeug verifizieren, dass der Agent-Body dieses Werkzeug in seiner Prozedur nachweislich benutzt — deklarierte, aber nicht genutzte Tools sind `Warning`-Findings (tote Berechtigung)
- **MUSS [MUST]** für jedes Werkzeug, das der Agent-Body klar benötigt, verifizieren, dass es in `tools` deklariert ist — genutzte, aber nicht deklarierte Tools sind `Critical`-Findings (der Agent wird nicht laufen)
- **MUSS [MUST]** verifizieren, dass der Agent das `tools`-Feld nicht **unbeabsichtigt weglässt**: Ein fehlendes `tools`-Feld erteilt die geerbte volle Tool-Oberfläche — das ist Permission-Sprawl. Wenn die Verantwortlichkeit des Agents „research" / „review" / „audit" / „report" ist und `tools` fehlt, ist das ein `Critical`; bei jedem anderen Agent ist das Fehlen ein `Warning`, sofern der Body das Erben aller Tools nicht ausdrücklich begründet ([R5](#referenzen), [R6](#referenzen))
- **SOLLTE [SHOULD]** dedizierte Tools (`Read`, `Grep`, `Glob`, `Edit`) gegenüber `Bash`-Äquivalenten bevorzugen; ein Agent, der `Bash` für Operationen nutzt, die ein dediziertes Tool abdeckt, bekommt ein `Warning`, sofern der Body die Wahl nicht begründet
- **MUSS [MUST]**, wenn `tools` und `disallowedTools` beide deklariert sind, verifizieren, dass kein Tool-Name in beiden Listen erscheint (die Laufzeit wendet zuerst Deny an, dann Allow, sodass ein doppelt gelistetes Tool stillschweigend entfernt wird) und dass das aufgelöste Set nicht leer ist; jede Bedingung ist ein `Warning`

### Plugin-Verteilungs-Constraint-Checks

Spiegelt `agent-management` §„Plugin-Verteilungs-Sicherheits-Constraints"; die ursprüngliche Regel zitieren, wenn ein Finding sie pinnt.

- **MUSS [MUST]** verifizieren, wenn `distribution: plugin` deklariert ist, dass das Frontmatter `hooks`, `mcpServers` oder `permissionMode` **nicht** setzt; jedes dieser Felder ist ein `Critical` (die Laufzeit ignoriert sie für Plugin-Agents stillschweigend, und der Autor wird in die Irre geführt zu glauben, sie seien aktiv) ([R5](#referenzen))
- **MUSS [MUST]**, wenn `distribution: project` deklariert ist, diese Felder als gültig akzeptieren; ihr Vorhandensein ist für project-distribuierte Agents **kein** Finding
- **SOLLTE [SHOULD]**, wenn ein Agent `distribution: plugin` deklariert UND der Body Verhalten beschreibt, das offensichtlich `hooks` / `mcpServers` / `permissionMode` benötigt (z. B. „dieser Agent installiert einen PreToolUse-Hook", „dieser Agent verbindet sich mit eigenem MCP-Server", „dieser Agent läuft im Plan-Modus"), ein `Warning` flaggen, auch wenn die Felder fehlen — Beschreibung und Distribution sind inkonsistent

### Subagent-Grenzen-Checks

Spiegelt `agent-management` §„Subagent-Grenzen" und `skill-vs-agent` §„Hybrid-Muster"; die ursprüngliche Regel zitieren, wenn ein Finding sie pinnt.

- **MUSS [MUST]** verifizieren, dass der Agent-Body **niemals** einen weiteren Subagent dispatched — den Body greppen nach `Agent(`, `subagent_type`, `Task(` oder äquivalenten Dispatch-Formulierungen; jeder Treffer ist ein `Critical` (Claude-Code-Subagents können keine Subagents spawnen) ([R5](#referenzen))
- **MUSS [MUST]** verifizieren, dass der Agent-Body **niemals** das Skill-Tool im Namen des Users invokiert — den Body greppen nach `Skill(`, `Skill tool` oder äquivalenten Skill-Dispatch-Formulierungen; jeder Treffer ist ein `Critical` gemäß `skill-vs-agent`

### Description-Qualität und proaktive-Delegation-Absicht

- **MUSS [MUST]** verifizieren, wenn die `description` die Phrase „use proactively" (oder das Äquivalent „use this proactively", „should be used proactively", „invoke proactively") enthält, dass die Verantwortlichkeit des Agents tatsächlich rechtfertigt, dass Claude ihn ohne explizite Nutzeraufforderung anbietet — Anzeichen, dass der Check besteht: Der Agent löst eine Problemklasse, die der Nutzer wahrscheinlich nicht explizit benennt (Security-Review bei jedem PR, Audit bei jedem Commit). Anzeichen, dass der Check scheitert: Der Agent hat destruktive Seiteneffekte, benötigt Credentials oder geht Verpflichtungen mit externen Systemen ein. Eine „proactively"-Behauptung an einem destruktiven oder credential-tragenden Agent ist ein `Critical` ([R5](#referenzen))
- **SOLLTE [SHOULD]** verifizieren, wenn der Agent klare Überlappung mit einem anderen bestehenden Artefakt (Skill oder Agent) hat, dass die `description` die Überlappung als **negativen Trigger** benennt („don't use for X, use the `<peer>` agent / skill instead"); das Fehlen des Negativs ist ein `Warning` ([R5](#referenzen))

### Prompt-Struktur-Checks

- **MUSS [MUST]** verifizieren, dass der System-Prompt den Agent auf genau eine Verantwortung eingrenzt, gemäß dem MUST in `agent-management`; Fehlen ist ein `Critical`
- **MUSS [MUST]** verifizieren, dass der System-Prompt die erwartete Output-Form benennt, gemäß dem MUST in `agent-management`; Fehlen ist ein `Critical`
- **MUSS [MUST]** verifizieren, dass der System-Prompt mit Rolle und Grenzen des Agents öffnet, dann das erwartete Output-Format nennt, dann die Arbeitsweise, gemäß dem SHOULD in `agent-management`; Abweichung ist ein `Warning`
- **MUSS [MUST]** verifizieren, dass der System-Prompt ausdrücklich festhält, ob der Agent Code schreibt oder nur recherchiert, gemäß dem SHOULD in `agent-management`; Fehlen ist ein `Warning`
- **SOLLTE [SHOULD]** Agent-Bodys, die das in `agent-management` genannte Soft-Längen-Ziel (~200 Zeilen) überschreiten, ohne unterstützendes Material nach `agents/<name>/` auszulagern, als `Warning` flaggen und damit das SHOULD aus `agent-management` spiegeln
- **SOLLTE [SHOULD]** bei Agents, die Dateien schreiben oder Seiteneffekte verursachen (`tools`-Liste enthält eines von `Edit`, `Write`, `Bash` oder `NotebookEdit`), verifizieren, dass der System-Prompt Ziele und Vorbedingungen dieser Effekte dokumentiert, gemäß dem Akzeptanzkriterium aus `agent-management`; Fehlen ist ein `Warning`

### Review-Prozedur

- **MUSS [MUST]** damit beginnen, die kanonischen Specs `agent-management`, `skill-vs-agent` und `review-plan` zu lesen, bevor ein Finding erzeugt wird; Findings ohne Anker in einer dieser Specs sind keine gültige Ausgabe dieser Prozedur
- **MUSS [MUST]** Findings in dieser Reihenfolge erzeugen: Frontmatter → Description/Trigger → Distribution → Model → Tools/Scope → Prompt-Struktur → Rationale-Abschnitt → referenzierte Assets → Duplikat-Prävention-Check → INFO-Beobachtungen
- **MUSS [MUST]** genau eine `review-plan`-Datei unter `.audits/agent-review/<agent-name>.md` emittieren; der Reviewer **MUSS [MUST]** jede Lifecycle-Regel aus `review-plan` befolgen, einschließlich der Single-Plan-pro-Ziel-Invariante und des Löschungs-Commit-Message-Formats
- **SOLLTE [SHOULD]** im `## Scope`-Abschnitt des Plans die Git-SHAs der angewandten Spec-Versionen einbetten, damit ein späteres Re-Review erkennen kann, ob Findings durch eine Spec-Revision veraltet sein könnten
- **KANN [MAY]** rein stilistische Beobachtungen (Vale, Markdown-Linting) als `Info`-Findings aufnehmen, wenn sie dem Autor helfen, **MUSS NICHT [MUST NOT]** sie aber zu `Warning` oder `Critical` erheben — die bleiben bei ihrem eigenen Tooling

### Bezug zu anderen Specs

- **MUSS [MUST]** auf `review-plan` für das Output-Format verweisen; dessen Anforderungen nicht hier wiederholen
- **MUSS NICHT [MUST NOT]** irgendetwas neu spezifizieren, das bereits in `agent-management` oder `skill-vs-agent` steht; wenn diese Spec und eine jener abweichen, gewinnt die Autoren-Spec, und diese Spec ist die, die aktualisiert werden muss
- **SOLLTE [SHOULD]**, wenn der zu reviewende Agent von einem benannten Skill dispatched wird, ein begleitendes `skill-review` für diesen Skill nur dann auslösen, wenn der Skill noch nicht gegen seine aktuelle Quell-Revision reviewt wurde — die Entscheidung im `## Scope` des Plans festhalten, damit nachgelagerte Akteure wissen, ob der dispatchende Skill abgedeckt ist

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] Ein durchgearbeitetes Beispiel existiert, das diese Review-Prozedur auf einen Agent in `nolte-shared` anwendet (z. B. `audience-review`) und einen konformen Plan unter `.audits/agent-review/` erzeugt
- [ ] Jeder Agent in `agents/` wurde seit Adoption dieser Spec mindestens einmal gegen die aktuelle `agent-management`-Revision reviewt, verifizierbar entweder durch einen offenen Plan unter `.audits/agent-review/` oder durch einen schließenden Commit in `git log`, der dem `review-plan`-Löschmuster entspricht
- [ ] Kein Agent in `agents/` fehlt ein Rationale-Abschnitt; der Rationale-Abschnitts-Check über alle Agents erzeugt null `Critical`
- [ ] Kein Agent in `agents/` ruft das Skill-Tool im Namen des Nutzers; ein Grep nach `Skill(` über alle Agent-Body-Dateien liefert null Treffer
- [ ] Kein Read-only-Agent in `agents/` deklariert `Edit`, `Write`, `Bash` oder `NotebookEdit` in seiner `tools`-Liste
- [ ] Keine zwei Agents in `agents/` teilen eine äquivalente Capability-Aussage, verifiziert durch Stichprobe jedes Plan-Duplikat-Präventions-Findings
- [ ] Jedes deklarierte Tool in der `tools`-Liste jedes Agents wird mindestens einmal im Body genutzt; jedes im Body genutzte Tool ist deklariert — beide Richtungen bestehen die Stichprobe
- [ ] Jeder Agent in `agents/` mit im Frontmatter fixiertem `model` hat eine Begründung dieser Wahl im System-Prompt oder in einem benachbarten Kommentar
- [ ] Kein offener Plan unter `.audits/agent-review/` enthält ein Prompt-Struktur-Reihenfolge-Finding auf `Critical`-Schwere ohne Zitat einer entsprechenden MUST-Regel in `agent-management`
- [ ] Jeder Agent in `agents/`, dessen `tools`-Liste `Edit`, `Write`, `Bash` oder `NotebookEdit` enthält, dokumentiert Ziele und Vorbedingungen dieser Schreibeffekte im System-Prompt
- [ ] Jeder offene Plan unter `.audits/agent-review/` entspricht der Vier-Abschnitts-Struktur und dem YAML-Frontmatter aus `review-plan`
- [ ] Die Abnahmekriterien der `agent-management`-Spec verweisen für die Review-Seite ihrer Autoren-Regeln auf diese Spec
- [ ] Eine Stichprobe von drei geschlossenen Plan-Löschungen in `git log` zeigt exakt das Commit-Message-Format `review(agent-review): close <agent> — <counts>`
- [ ] Kein Plan unter `.audits/agent-review/` schließt mit einem ungelösten `Critical` für `distribution: plugin`-Agents, die `hooks`, `mcpServers` oder `permissionMode` deklarieren
- [ ] Jeder Plan unter `.audits/agent-review/` führt die Subagent-Grenzen-Checks (kein Agent-Spawning, kein Skill-Tool-Aufruf) gegen den Ziel-Agent aus
- [ ] Jeder Plan unter `.audits/agent-review/` führt den Proaktive-Delegation-Absicht-Check gegen jeden Agent aus, dessen `description` „use proactively" oder eine äquivalente Phrase enthält
- [ ] Kein Agent lässt das `tools`-Feld weg, während er eine Research- / Review- / Audit- / Report-Verantwortlichkeit deklariert (null `Critical` auf dem neuen Permission-Sprawl-Check)

## Referenzen

Quellen für die zusätzlichen Checks oben. Bei Findings, die eine konkrete Upstream-Regel pinnen, im eckigen Klammerpräfix den passenden Eintrag zitieren.

- [R1] Agent-Management-Spezifikation (dieses Plugin) — `spec/claude/agent-management/`
- [R2] Skill-vs-Agent-Entscheidung (dieses Plugin) — `spec/claude/skill-vs-agent/`
- [R3] Skill-Management-Spezifikation (dieses Plugin, für Cross-Format-Abgleich) — `spec/claude/skill-management/`
- [R4] Review-Plan-Spezifikation (Output-Format) — `spec/claude/review-plan/`
- [R5] Create custom subagents, Claude-Code-Doku — <https://code.claude.com/docs/en/sub-agents>
- [R6] Best practices for Claude Code subagents, PubNub Engineering — <https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/>

## Offene Fragen
<!-- Ungelöste Entscheidungen, bekannte Unbekannte, Punkte, die eine Stakeholder-Antwort brauchen. -->
- Soll der Duplikat-Präventions-Check nur Skill-Descriptions aus `skills/*/SKILL.md` im selben Repository lesen, oder auch den MkDocs-gerenderten Katalog über installierte Plugins abfragen, wenn ein Consumer eine Downstream-Kopie reviewt?
- Wie wird "Read-only-Agent" mechanisch erkannt — an den Verben in der `description` (review, audit, research, lint, report), an einem expliziten `read-only: true`-Flag im Frontmatter, das noch nicht existiert, oder durch ein im `## Scope` des Plans festgehaltenes menschliches Urteil?
- Soll der Tools-genutzt-vs-Tools-deklariert-Check den Fall tolerieren, in dem ein Tool nur in einem Beispiel-Abschnitt des Bodys erscheint und nicht in der Prozedur selbst, oder ist Nur-in-Beispielen-Nutzung ein Zeichen für tote Berechtigung?
- Wenn `distribution: project` deklariert ist, soll das Review mehr als den Wert selbst verifizieren — zum Beispiel, dass der Agent keine Plugin-ko-lokalisierten Assets referenziert, was Projekt-Level-Nutzung brechen würde?
- Soll das Review eines Agents, dessen `description` negative Trigger nennt, auch verifizieren, dass diese Negativen die benannten Fälle tatsächlich ausschließen — und wenn ja, wie wird das verifiziert, ohne den Agent laufen zu lassen?
- Wie interagiert diese Spec-Invokation mit `audience-review` — dem ersten Agent im Portfolio — denn das Reviewen eines Review-Agents ist ein Rekursionsfall, der explizite Behandlung verdient: Wird der erste jemals geschriebene Plan vom Review oder von einem Menschen erzeugt, und wie wird die Rekursion terminiert?
