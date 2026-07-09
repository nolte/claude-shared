# Issue-Orchestrierung

Status: draft

## Context

Readers: Skill- und Agent-Autoren, die den Orchestrator implementieren, und
Operatoren, die ihn aufrufen, um ein Issue end-to-end zu führen. Der Operator gibt
sieben Gates frei — Issue-Scope, den Requirements-Verständnis-Check (elicit oder
Override), Klassifikation (für `security` / `spec-change`), die
Voranalyse-Dekomposition, die Routing-Entscheidung, jeden Spezialisten-Dispatch und
den PR — bevor ein Merge erreicht wird. Die gesamte On-Disk-Arbeit der Orchestrierung
findet in einem dedizierten Worktree off `develop` statt, nie im Primary-Checkout.

Das Portfolio regelt bereits eine vollständige Planungs-Pipeline — `roadmap-plan`
reiht Outcomes ein, `feature-decompose` zerlegt ein Roadmap-Item in testbare
Features, `sprint-plan` zieht Features in einen Sprint, und `sprint-execute` /
`sprint-review` treiben sie nach `done`. Es regelt außerdem ein
Orchestrator-Muster für praktische Remediation: `workflow-health-triage`
klassifiziert einen roten CI-Lauf und dispatched den am besten passenden Agenten;
`continuous-improvement-triage` verallgemeinert diesen Dispatch über jede
Audit-Quelle. Was fehlt, ist ein **Einstiegspunkt für ein rohes GitHub-Issue**.
Heute wird ein Issue erst dann zu Arbeit, wenn ein Mensch es manuell in ein
Roadmap-Item, ein Feature oder einen Ad-hoc-Branch umschreibt — es gibt keinen
Prozess, der ein Issue *vollständig durchdringt*, es in spezialisten-gerechte
Arbeitspakete zerlegt und die vorhandenen Spezialisten (Skills und Agents) bis zu
einem Pull Request orchestriert.

Ohne diese Spezifikation ist die Issue-Aufnahme undiszipliniert: Dasselbe Issue
wird von jedem Beitragenden anders analysiert, die Dekomposition lebt nur in
jemandes Kopf, die Spezialisten-Abdeckung wird inkonsistent genutzt (ein
Security-Issue erhält einen Generalisten-Fix statt `code-security-reviewer`), und
der Link von einem gemergten PR zurück zum motivierenden Issue ist informell.
Diese Spezifikation definiert einen einzelnen Orchestrierungs-Prozess —
analysieren, dekomponieren, routen, dispatchen, verifizieren — dessen
qualitätsstiftender Kern ein **persistentes Voranalyse-Artefakt** ist, das jedes
Teilproblem so aufbereitet, dass ein Spezialist es vollständig und hochwertig
umsetzen kann. Der Orchestrator ist ein Generalist: Er führt die
Spezialisten-Remediation nie selbst aus, wenn ein passender Spezialist existiert.

## Goals
- Ein rohes GitHub-Issue wird vollständig durchdrungen, bevor Code geschrieben
  wird: Body, Kommentare, Labels, verlinkte Issues und PRs sowie die
  Repository-Oberfläche, die es berührt
- Jedes Issue wird in atomare, testbare Arbeitspakete zerlegt, jedes auf den am
  besten passenden verfügbaren Skill oder Agent gemappt, und die Dekomposition wird
  als reviewbares Artefakt persistiert statt nur im Gespräch zu leben
- Die Rolle des Orchestrators ist analysieren, dekomponieren, routen, dispatchen
  und verifizieren — keine praktische Remediation, wenn ein Spezialist existiert;
  Spezialisten erledigen das Editieren durch das Standard-PR-Gate
- Ein Issue, das für die direkte Umsetzung zu groß ist, wird in die formale
  Pipeline `roadmap → feature → sprint` geroutet, statt ad hoc dekomponiert zu
  werden, sodass die Planungsschicht nie umgangen wird
- Jeder Pull Request, den die Orchestrierung produziert, ist auf das Issue
  zurückführbar, trägt die Issue-Klassifikation und benennt den Spezialisten, der
  jeden Teil des Fixes produziert hat, sodass Abdeckungslücken aus der gemergten
  Historie erkennbar sind
- Die Spezialisten-Auswahl wird aus dem Katalog aufgelöst, der zum
  Dispatch-Zeitpunkt existiert, nicht aus einem eingefrorenen Snapshot, sodass ein
  neu verfasster Spezialist sofort erreichbar ist

## Non-Goals
- Die interne Mechanik eines dispatchten Spezialisten: `feature-decompose`,
  `code-security-reviewer`, `quality-gate`, `pull-request-create` und gleichwertige
  bleiben maßgeblich für ihren eigenen Scope und ihre Trigger; diese Spezifikation
  triggert sie, sie definiert sie nicht neu
- PR-Gating, Branch-Protection und Merge-Regeln: `pull-request-workflow` und
  `branching-model` bleiben maßgeblich; dieser Prozess läuft durch deren Gates, er
  ersetzt sie nicht und merged nie (`pull-request-merge` besitzt den Merge)
- Der portfolioweite Spezialisten-Abdeckungs-Loop und die
  Drei-Wiederholungen-Gap-Closure-Regel: `continuous-improvement` bleibt maßgeblich;
  diese Spezifikation konsumiert diese Regel für ihren No-Match-Fall, statt sie neu
  herzuleiten
- CI-Failure-Triage: `workflow-health-triage` bleibt die Autorität für die
  Remediation roter Workflows; ein Issue *über* einen roten Workflow wird dorthin
  geroutet, nicht hier neu triagiert
- Roadmap-, Sprint-, Feature- und Mission-Lebenszyklus: `roadmap`, `sprint`,
  `feature` und `mission` bleiben maßgeblich für die Planungsartefakte, in die
  dieser Prozess einspeist
- Das Verfassen neuer Spezialisten, wenn keiner passt: `agent-management` und
  `skill-management` (über `claude-plugin-developer` aufgerufen) bleiben maßgeblich
  für die Gestalt des Spezialisten; diese Spezifikation triggert das Verfassen nur
  unter der Gap-Regel

## Requirements

### Issue-Akquise und Durchdringung
- **MUSS [MUST]** das Ziel-Issue als `gh issue view`-URL, Issue-Nummer oder
  eindeutige Referenz („das offene i18n-Issue") akzeptieren und vor jeder Analyse zu
  einem einzelnen Issue auflösen; ist die Referenz mehrdeutig, **MUSS [MUST]** sie
  Kandidaten-Issues auflisten und den Operator um Auswahl bitten
- **MUSS [MUST]** die vollständige Issue-Oberfläche vor der Klassifikation lesen:
  Issue-Body, jeden Kommentar, alle Labels, Assignee und Milestone sowie jedes
  verlinkte Issue oder jeden verlinkten Pull Request (über
  `gh issue view <n> --json …` und `gh issue view <n> --comments`)
- **MUSS [MUST]** die Repository-Oberfläche scannen, die das Issue plausibel berührt
  — mindestens die relevanten `spec/`-, `skills/`-, `agents/`-, Quell- und
  `docs/`-Pfade —, damit die Dekomposition im tatsächlichen Code verankert ist, nicht
  nur in der Issue-Prosa
- **MUSS [MUST]** vor der Dekomposition auf Vorarbeit prüfen: bestehende
  `project/features/`-Einträge, `project/roadmap.md`-Items und offene Pull Requests,
  die das Issue ganz oder teilweise bereits adressieren; ein Issue, das zum
  Analysezeitpunkt bereits durch einen gemergten Fix geschlossen ist, **KANN [MAY]**
  als selbst-aufgelöst ohne Dekomposition gemeldet werden
- **MUSS [MUST]** vor der Dekomposition den Requirements-Elicitation-Consumer-Vertrag
  anwenden (`spec/project/requirements-elicitation/` §H Consumer contract, der
  `issue-orchestrate` als gegateten Consumer benennt): prüfen, ob ein Requirement-
  Artefakt unter `project/requirements/` für das Issue existiert und ob dessen
  `U_gate` `τ_high` erreicht. Wenn keines existiert oder `U_gate` unter `τ_high` liegt
  — der Regelfall für ein rohes Issue, dessen Anforderungen nur als Prosa formuliert
  sind — **MUSS** zuerst `requirements-elicit` dispatcht werden, um das Issue in ein
  bestätigtes Requirement-Artefakt zu analysieren, oder ein expliziter Operator-
  Override im Voranalyse-Artefakt festgehalten werden; gegen ungenannte oder schwach
  verstandene Anforderungen zu dekomponieren ist verboten. Ein `question`-Issue (das
  keine Arbeitspakete liefert) und ein bereits durch einen gemergten Fix
  selbst-aufgelöstes Issue sind ausgenommen, da beide die Dekomposition nicht erreichen
- **DARF NICHT [MUST NOT]** mit der Dekomposition beginnen, bevor der Operator das
  akquirierte Issue und seinen aufgelösten Scope bestätigt hat, sodass eine
  fehlgelesene Issue-Referenz vor Arbeitsbeginn abgefangen wird

### Klassifikation
- **MUSS [MUST]** das Issue in genau eine primäre Klasse aus dem geschlossenen Set
  `bug / feature-request / spec-change / security / docs / refactor / question /
  infra` klassifizieren und eine einzeilige Begründung festhalten; ein
  `question`-Issue produziert eine Antwort und keine Arbeitspakete, und ein
  `infra`-Issue über CI wird an `workflow-health-triage` übergeben statt hier
  dekomponiert
- **KANN [MAY]** Sekundärklassen festhalten, wenn ein Issue echt mehr als eine
  umspannt (ein `feature-request` mit `security`-Dimension), aber die Primärklasse
  treibt die Routing-Entscheidung
- **MUSS [MUST]** die Klassifikation mit dem Operator vor der Dekomposition
  mindestens für die Klassen `security` und `spec-change` bestätigen, wo eine
  Fehlklassifikation die höchsten Folgekosten hat

### Working-Copy-Isolation
- **MUSS [MUST]** jeden versionierten Datei-Write, den die Orchestrierung produziert
  — das Voranalyse-Artefakt unter `.audits/issue-orchestrate/<issue-number>/`, jede
  Bearbeitung eines dispatchten Spezialisten und den Feature-Branch, aus dem der Pull
  Request geöffnet wird — in einem **dedizierten, off `origin/develop` erzeugten
  Worktree** ausführen, gemäß `spec/project/parallel-working-copies/`
  §Branch-to-worktree mapping und §Lifecycle: Create; der Referenz-Erzeugungspfad ist
  `task worktree:add -- <branch> [slug]`. Der Primary-Checkout **MUSS** auf `develop`
  bleiben und **DARF NICHT** auf den Feature-Branch umgeschaltet werden, auch nicht
  für ein Ein-Paket-Issue
- **MUSS [MUST]** den Worktree vor dem ersten versionierten Datei-Write etablieren,
  sodass keine Orchestrierungs-Ausgabe je im Primary-Checkout landet; das
  Voranalyse-Artefakt ist dieser erste Write. Wird das Issue stattdessen in die
  formale Pipeline geroutet, regelt die eigene Working-Copy-Disziplin der
  nachgelagerten Planungs-Skill die von ihr geschriebenen Artefakte
- **KANN [MAY]** die Issue-Bearbeitung in einem **dedizierten, worktree-isolierten
  Agenten ausführen, der die Issue-ID als Parameter übernimmt**
  (`Agent(..., isolation: "worktree")`), als sanktionierte Alternative zum
  Fresh-Top-Level-Session-Default von `spec/project/parallel-working-copies/`
  §Claude Code session scoping. Wenn er das tut, **MUSS** er den Worktree-Root des
  Agenten auf den spec-konformen Pfad
  `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/<repo>/agents/` gemäß §Path layout zeigen
  (nie unter `.claude/worktrees/`), und er akzeptiert den Resumability-Trade-off, dass
  ein Subagent-Transkript nicht eigenständig `claude --resume`-bar ist — der Per-Run-
  Checkpoint unter `.resume/issue-orchestrate/` (siehe §Resumption and operator gating)
  bleibt daher der Recovery-Anker. Die Operator-Freigabe-Gates verbleiben unabhängig
  davon bei der orchestrierenden Skill; der dedizierte Agent führt die
  Hands-on-Arbeit aus, er absorbiert die Gates nicht

### Dekomposition in Arbeitspakete (der Voranalyse-Kern)
- **MUSS [MUST]** das Issue in atomare, unabhängig testbare Arbeitspakete zerlegen;
  jedes Paket **MUSS [MUST]** festhalten: eine stabile Paket-ID, eine
  Problemstellung, seine Akzeptanzkriterien, die Dateien oder Artefakte, die es
  berührt, den Spezialisten, der es umsetzen soll (aufgelöst gemäß
  *Spezialisten-Dispatch* unten), und seine Abhängigkeiten von anderen Paketen (eine
  gerichtete azyklische Ordnung)
- **MUSS [MUST]** jedes Paket klein genug halten, dass eine einzelne
  Spezialisten-Invocation es bis zu einem verifizierbaren Akzeptanzkriterium
  abschließen kann; ein Paket, das nicht mit einem testbaren Akzeptanzkriterium
  formuliert werden kann, ist ein Signal, dass das Issue in die formale Pipeline
  gehört (siehe *Routing*), kein zu dispatchendes Paket
- **MUSS [MUST]** die Dekomposition als Voranalyse-Artefakt unter
  `.audits/issue-orchestrate/<issue-number>/analysis.md` persistieren, das die
  Issue-Metadaten, die Klassifikation und Begründung, die In/Out-of-Scope-Grenze,
  die Arbeitspaket-Tabelle, die paketübergreifende Abhängigkeitsordnung, die Risiken
  und etwaige offene Fragen an den Operator trägt
- **MUSS [MUST]** das Voranalyse-Artefakt vor jedem Dispatch zur Operator-Freigabe
  vorlegen; das Artefakt ist der reviewbare Übergabe-Vertrag, und ein Dispatch auf
  einer nicht freigegebenen Dekomposition ist verboten
- **SOLLTE [SHOULD]** das Voranalyse-Artefakt in der Sprache des Issues schreiben;
  die maschinenlesbaren Audit-Trail-Felder, die später in einem PR landen
  (Klassifikations-Label, Spezialisten-`subagent_type`, Finding-Quelle), bleiben
  Englisch, damit der Trail portfolioweit grep-bar ist

### Spezialisten-Dispatch (Wiederverwendung statt Neuerfindung)
- **MUSS [MUST]** den Spezialisten für jedes Arbeitspaket durch einen
  Runtime-Lookup des zum Dispatch-Zeitpunkt existierenden Katalogs auflösen, wobei
  jeder Distributions-Root geglobt wird: die plugin-eigenen Spezialisten unter
  `${CLAUDE_PLUGIN_ROOT}/skills/*/SKILL.md` und `${CLAUDE_PLUGIN_ROOT}/agents/*.md`
  (wo die `nolte-shared`-Spezialisten liegen, wenn der Orchestrator in einem
  Consumer-Repository läuft), die projekt-lokalen `skills/*/SKILL.md` und
  `agents/*.md` des Consumers sowie die projektverteilten `~/.claude/agents/*.md`;
  dann jedes Paket gegen die `description`-Zeilen der Kandidaten auf Basis der
  genannten Verantwortung matchen, nicht auf Basis des Kandidatennamens. Der Katalog
  **DARF NICHT [MUST NOT]** als Inline-Snapshot in einem implementierenden Skill
  eingefroren werden. Ein bloßer `skills/*/SKILL.md`-Glob ohne
  `${CLAUDE_PLUGIN_ROOT}` ist ein Defekt: In einem Consumer-Repository verfehlt er
  stillschweigend jeden plugin-verteilten Spezialisten
- **DARF NICHT [MUST NOT]** den Orchestrator das praktische Editieren eines
  Arbeitspakets selbst ausführen lassen, wenn ein passender Spezialist existiert; der
  Orchestrator analysiert, dekomponiert, dispatched über
  `Agent(subagent_type=<name>)` oder einen passenden Skill-Aufruf und verifiziert und
  **KANN [MAY]** zusätzlich mehrere Spezialisten verketten, wenn ein Paket
  Verantwortungen kreuzt
- **SOLLTE [SHOULD]** die folgenden als illustrative Dispatch-Anker behandeln —
  bekannte Portfolio-Spezialisten für gängige Klassen, jeder weiterhin per
  Description-Match zum Dispatch-Zeitpunkt neu aufgelöst und nie als eingefrorene
  Tabelle hartkodiert: ein `spec-change`-Paket durch den Spec-Authoring-Spezialisten
  (das `spec`-Skill); ein Dokumentationspaket durch den audience-gerichteten
  Dokumentations-Spezialisten; ein feature-förmiges Paket durch `feature-decompose`.
  Ein `security`-Paket folgt der unten in *Verifikation* definierten
  Audit→Fix→Verify-Kette statt einem einzelnen Dispatch: der read-only
  `code-security-reviewer`-Agent fasst die Oberfläche ab, ein coding-fähiger
  Spezialist (oder, mangels Match, der Generalist unter der Gap-Regel) verfasst den
  Fix, und das eingebaute `security-review`-Skill verifiziert den Diff
- **MUSS [MUST]** ein Arbeitspaket, für das kein Spezialist passt, als Portfoliolücke
  gemäß `continuous-improvement` §Portfolio gap closure behandeln: Der Orchestrator
  hält den No-Match fest, wendet die Drei-Wiederholungen-Regel an und **KANN [MAY]**
  `claude-plugin-developer` dispatchen, um einen neuen Spezialisten zu verfassen,
  wenn die Regel (oder eine festgehaltene High-Impact-Begründung) erfüllt ist; bis
  dahin darf der Generalist das Paket bearbeiten, und der PR hält die explizite
  Notiz „no matching specialised agent" fest
- **MUSS [MUST]** Arbeitspakete in ihrer Abhängigkeitsordnung dispatchen, an jeder
  Paketgrenze auf Operator-Bestätigung gaten und **MUSS [MUST]** das Ergebnis jedes
  Spezialisten einsammeln und festhalten, bevor ein abhängiges Paket dispatcht wird

### Routing in die formale Pipeline (kein Planungs-Bypass)
- **MUSS [MUST]** ein Issue in die formale Pipeline `roadmap → feature → sprint`
  routen, statt es für die direkte Umsetzung zu dekomponieren, wenn es mehr als ein
  Goal-Outcome umspannt, mehr als einen kohärenten PR-Strang erfordert oder ein
  Roadmap-Item anlegen oder umtargeten würde; die Routing-Entscheidung **MUSS
  [MUST]** ein explizites, operator-bestätigtes Gate sein, das im Voranalyse-Artefakt
  festgehalten wird
- **MUSS [MUST]** beim Routing in die Pipeline das Issue an `feature-decompose` (für
  ein bestehendes Roadmap-Item) oder an `roadmap-plan` (wenn ein neues Outcome oder
  Item nötig ist) übergeben, statt Features oder Roadmap-Items inline zu entwerfen,
  sodass die Planungs-Specs maßgeblich bleiben
- **KANN [MAY]** ein bounded Issue direkt über den oben definierten
  Dispatch-und-Verifizieren-Pfad umsetzen. *Bounded* bedeutet operational: ein
  kohärentes Goal-Outcome; ein einzelner PR-Strang (jedes Arbeitspaket landet auf
  einem Feature-Branch als ein Pull Request); und kein neues oder umgetargetetes
  Roadmap-Item. Sobald die Arbeit einen zweiten unabhängigen Feature-Branch braucht
  oder ein zweites Goal-Outcome berührt, ist das Issue unbounded und wird in die
  Pipeline geroutet
- **DARF NICHT [MUST NOT]** die beiden Routen für ein Issue mischen: Ein Issue wird
  entweder direkt umgesetzt oder in die Pipeline geroutet; eine teilweise
  Direktumsetzung, die den Rest stillschweigend ungeplant lässt, ist verboten

### Verifikation und Nachvollziehbarkeit
- **MUSS [MUST]** verlangen, dass `quality-gate` auf der erzeugten Änderung grün
  durchläuft, bevor der Pull Request geöffnet wird, und **MUSS [MUST]** für jedes
  Paket, das einen security-sensitiven Pfad berührt, den read-only
  `code-security-reviewer`-Agent zur Abfassung der Oberfläche und das eingebaute
  `security-review`-Skill zur Verifikation des erzeugten Diffs laufen lassen, bevor
  der PR geöffnet wird. (`security-review` ist das Claude-Code-Harness-Built-in, kein
  `nolte-shared`-Plugin-Agent; es wird als `security-review`-Skill aufgerufen, nicht
  über `Agent(subagent_type="nolte-shared:security-review")`.)
- **MUSS [MUST]** sicherstellen, dass jeder Pull Request, den die Orchestrierung
  produziert, das Issue verlinkt (`Closes #<n>` oder die Linking-Konvention des
  Repositories) und in seiner **Risk / rollout notes**-Sektion gemäß
  `pull-request-workflow` trägt: die Issue-Referenz, die Issue-Klassifikation
  wörtlich und pro Arbeitspaket den dispatchten Spezialisten
  (`subagent_type`-Literal) oder die explizite Notiz „no matching specialised agent —
  generalist remediation"
- **DARF NICHT [MUST NOT]** den Pull Request mergen; die Orchestrierung stoppt bei
  einem offenen, audit-getrailten PR und übergibt den Merge an `pull-request-merge`,
  das das Gate neu validiert
- **DARF NICHT [MUST NOT]** ein Gate aus `pull-request-workflow` oder
  `branching-model` umgehen: kein `--admin`-Override, kein
  `continue-on-error`-Maskieren eines Required-Checks, kein Entfernen eines
  Required-Checks
- **SOLLTE [SHOULD]** die Zusammenfassung des Voranalyse-Artefakts (Klassifikation,
  Paketanzahl, gewählte Route) als Kommentar zurück ins Issue posten, wenn der
  Operator bestätigt, sodass der Issue-Thread festhält, wie die Arbeit strukturiert
  wurde

### Wiederaufnehmbarkeit und Operator-Gating
- **MUSS [MUST]** gemäß `spec/claude/resumable-work/` wiederaufnehmbar sein: Der
  Zustand wird nach jedem Operator-Freigabe-Gate und jeder benannten Phasengrenze
  (acquire, analyze, decompose, route, orchestrate, verify) gecheckpointet, sodass
  ein Crash mitten in der Orchestrierung vom letzten Checkpoint fortsetzt statt
  dispatchte Spezialisten erneut auszuführen
- **MUSS [MUST]** jede extern sichtbare Aktion (das Schreiben des
  Voranalyse-Artefakts, jeden Spezialisten-Dispatch, den Issue-Kommentar, die
  PR-Erstellung) auf Operator-Bestätigung gaten; der Orchestrator feuert nie einen
  mutierenden Schritt ohne ein festgehaltenes „Ja"

## Acceptance Criteria
- [ ] Für ein akquiriertes Issue existiert das Voranalyse-Artefakt unter
  `.audits/issue-orchestrate/<issue-number>/analysis.md` und hält die
  Issue-Metadaten, die einzelne primäre Klassifikation mit Begründung, die
  In/Out-of-Scope-Grenze und eine Arbeitspaket-Tabelle fest, in der jedes Paket eine
  Problemstellung, Akzeptanzkriterien, berührte Dateien, einen Spezialisten und seine
  Abhängigkeiten benennt
- [ ] Für jeden als `security` oder `spec-change` klassifizierten Orchestrierungslauf
  hält das Voranalyse-Artefakt einen expliziten Operator-Klassifikations-Bestätigungs-
  Schritt fest, der vor dem Befüllen der Arbeitspaket-Tabelle erfolgte
- [ ] Für jedes dekomponierte Issue existierte vor der Dekomposition ein
  Requirement-Artefakt, das `τ_high` erreicht, oder das Voranalyse-Artefakt hält einen
  expliziten Operator-Override des Requirements-Elicitation-Consumer-Gates fest
- [ ] Für jedes direkt implementierte Issue lag jeder von der Orchestrierung
  produzierte versionierte Datei-Write (das Voranalyse-Artefakt, die dispatchten
  Bearbeitungen, der Feature-Branch) in einem dedizierten Worktree off `develop`, und
  der Primary-Checkout wurde nie von `develop` weggeschaltet
- [ ] Kein Arbeitspaket in einem Voranalyse-Artefakt entbehrt eines testbaren
  Akzeptanzkriteriums; ein Paket, das keines formulieren kann, wird stattdessen als
  Routing-Signal in die formale Pipeline festgehalten
- [ ] Jeder in einem Arbeitspaket benannte Spezialist wurde durch einen
  Runtime-Katalog-Lookup zur Analysezeit aufgelöst, und kein implementierendes Skill
  trägt eine eingefrorene Inline-Liste von Spezialistennamen als Dispatch-Tabelle
- [ ] Für jedes in die formale Pipeline geroutete Issue hält das Voranalyse-Artefakt
  die Routing-Begründung und das Übergabe-Ziel (`feature-decompose` oder
  `roadmap-plan`) fest, und kein Roadmap-Item oder Feature wurde vom Orchestrator
  inline entworfen
- [ ] Für die letzten 10 von dieser Orchestrierung produzierten Pull Requests
  verlinkt jeder sein ursprüngliches Issue, und seine **Risk / rollout notes**-Sektion
  benennt die Issue-Klassifikation und pro Paket den dispatchten Spezialisten oder
  die explizite Notiz „no matching specialised agent"
- [ ] Jeder von dieser Orchestrierung produzierte Pull Request trägt `Closes #<n>`
  (oder das konfigurierte Linking-Keyword des Repositories) in seinem Body; gemäß
  `pull-request-workflow` feuert der Issue-Schluss beim `main`-Fast-Forward, nicht
  beim `develop`-Merge
- [ ] Kein von dieser Orchestrierung produzierter Pull Request wurde von der
  Orchestrierung selbst gemergt, und keiner zeigt einen Branch-Protection-Override,
  eine `enforce_admins: false`-Ausnahme oder einen Required-Check-Bypass
- [ ] Für jedes `security`-Issue liefen sowohl der read-only
  `code-security-reviewer`-Agent als auch das eingebaute `security-review`-Skill,
  bevor der PR geöffnet wurde (Audit, dann Diff-Verifikation), festgehalten im
  Artefakt und in den PR-Notes
- [ ] Für jedes Arbeitspaket, dessen Finding-Klasse drei oder mehr Male ohne
  passenden Spezialisten generalistisch bearbeitet wurde, existiert nun entweder ein
  Spezialist oder ein offenes Issue trackt seine Erstellung mit benanntem Owner,
  gemäß `continuous-improvement`
- [ ] Jeder Orchestrierungslauf, der mitten im Fluss unterbrochen und mit demselben
  Issue erneut aufgerufen wurde, setzte vom letzten Checkpoint fort, statt ein bereits
  abgeschlossenes Arbeitspaket erneut zu dispatchen
- [ ] Für jeden abgeschlossenen Orchestrierungslauf hält der Checkpoint-Zustand unter
  `.resume/issue-orchestrate/` einen Entscheidungs-Eintrag für jedes extern sichtbare
  Gate fest — das Schreiben des Artefakts, jeden Spezialisten-Dispatch, den
  Issue-Kommentar und die PR-Erstellung

## Open Questions
- §Routing definiert *bounded* nun operational (ein Goal-Outcome, ein Feature-Branch
  / ein PR-Strang, kein neues oder umgetargetetes Roadmap-Item). Ob die Grenze
  zusätzlich mit einer quantitativen Schwelle (etwa einer maximalen Arbeitspaketzahl)
  gehärtet werden sollte, wird zurückgestellt, bis genug Läufe zur Kalibrierung
  existieren.
- Ob ein direkt umgesetztes Multi-Paket-Issue als ein Pull Request oder als ein PR
  pro kohärentem Paketset landen sollte, bleibt dem Operator pro Issue überlassen;
  der Default ist ein einzelner PR-Strang pro Issue. Eine festere Regel wird
  zurückgestellt.
- Ob das Voranalyse-Artefakt zusätzlich standardmäßig (statt nur auf
  Operator-Bestätigung) in den Issue-Thread gespiegelt werden sollte, wird
  zurückgestellt, bis Operator-Präferenz über reale Läufe vorliegt.
