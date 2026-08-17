# Claude-Skill-Review

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Bedarf oder welche Einschränkung treibt sie? -->

Die `skill-management`-Spec definiert, wie ein Skill *erstellt* wird — On-Disk-Form, Frontmatter, Templates, Distributionsform. Was sie nicht definiert, ist, wie ein Skill *reviewt* wird: welche Anforderungen ein Reviewer prüft, in welcher Reihenfolge und welches Deliverable das Review hinterlässt. Ohne eine geteilte Review-Prozedur erzeugen zwei Reviewer desselben Skills inkompatible Ergebnisse, die Rationale-Dokumentations-Regel aus `skill-vs-agent` verrutscht still, und Plugin-Entwickler, die die Review-Ausgabe konsumieren, müssen die private Form jedes Reviewers rückentwickeln. Diese Spec definiert die bindende Review-Prozedur für Skills im `nolte-shared`-Plugin, verweist auf `skill-management` und `skill-vs-agent` als Wahrheitsquellen dafür, was als Finding zählt, und delegiert den Output-Format-Vertrag an `review-plan`. Ein Skill-Review erzeugt genau ein `review-plan`-Artefakt unter `.audits/skill-review/<skill-name>.md`; sobald jeder Punkt verarbeitet ist, wird der Plan gelöscht und seine Git-Historie bleibt als Audit-Trail.

Leser: Reviewer, die ein Skill-Review gegen `skill-management` und `skill-vs-agent` durchführen, die Autoren des `skill-review`-Skills, die das Verfahren operationalisieren, sowie Plugin-Entwickler, die das resultierende `review-plan`-Artefakt konsumieren.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, ergebnisorientiert. -->
- Jedes Skill-Review wendet denselben Satz von Checks aus `skill-management` und `skill-vs-agent` in derselben Reihenfolge mit demselben Schweregrad-Mapping an
- Review-Output ist ein `review-plan`-Artefakt — parsbar, abarbeitbar und pro Finding auf eine konkrete Spec-Anforderung zurückführbar
- Skill-Autoren können das Review an ihrer eigenen Arbeit fahren, bevor sie sie einreichen; ein späterer Reviewer (Mensch oder LLM) erzielt auf demselben Quellbaum identische Ergebnisse
- Plugin-Entwickler können gegen die Review-Ausgabe skripten (Plan-Dateien parsen, Merges auf offene `Critical` gaten, offene Reviews zählen), ohne reviewer-spezifische Konventionen modellieren zu müssen
- Das Review trennt **Autoren-Spec-Konformität** (`skill-management`-Regeln) von **Entscheidungsregel-Konformität** (`skill-vs-agent`-Rationale), ohne beides zu einem einzigen Pass/Fail zu vermengen

## Nicht-Ziele
<!-- Was explizit außerhalb des Scopes liegt. Verhindert Scope Creep. -->
- Definition, was ein Skill auf Disk *ist* — das gehört zu `skill-management`
- Entscheidung, ob ein Feature Skill oder Agent hätte werden sollen — das gehört zu `skill-vs-agent`; diese Spec prüft nur, dass die Entscheidung *dokumentiert* ist
- Vorgabe des Output-Datei-Formats — das gehört zu `review-plan`
- Review von Agents — das deckt `agent-review` mit symmetrischer Struktur ab
- Ersetzung der quartalsweisen portfolioweiten Reconciliation — das gehört zu `spec-drift-audit`
- Linter- und Markdown-Style-Checks, die bereits von `task lint` / Vale / Pre-Commit-Hooks erzwungen werden — diese bleiben bei ihren eigenen Tools
- Laufzeit- oder Verhaltens-Korrektheit des Skills (ob der Skill bei Aufruf tatsächlich tut, was seine Beschreibung verspricht) — diese Spec reviewt das **erstellte Artefakt**, nicht eine Live-Ausführung

## Anforderungen
<!-- RFC-2119-Schlüsselwörter verwenden: MUST, SHOULD, MAY. Eine atomare Anforderung pro Bullet. -->

### Review-Scope

- **MUSS [MUST]** genau einen Skill als Eingabe nehmen, identifiziert durch den Pfad `skills/<name>/` in einem `nolte-shared`-Quellbaum oder den äquivalenten Runtime-Pfad `.claude/skills/<name>/` beim Review einer Consumer-Installation
- **MUSS [MUST]** folgende Dateien in dieser Reihenfolge als Review-Oberfläche behandeln: `SKILL.md` (Frontmatter und Body), jede von `SKILL.md` relativ referenzierte Datei (Templates, Assets, Beispiele) und jeden Geschwister-`agents/<name>.md`, an den der Skill dispatched (um die Orchestrierungs-Richtung zu bestätigen)
- **MUSS NICHT [MUST NOT]** mehr als einen Skill pro Plan reviewen; parallele Reviews mehrerer Skills emittieren je einen `review-plan` pro Ziel
- **KANN [MAY]** den Scope auf einen bestimmten Aspekt einschränken (nur Frontmatter, nur Templates), wenn das Review durch eine gezielte Änderung ausgelöst wurde, und **MUSS [MUST]** die Einschränkung im `## Scope`-Abschnitt des Plans dokumentieren

### Checks aus `skill-management`

- **MUSS [MUST]** für jede MUST / SHOULD / MAY-Regel der kanonischen `skill-management`-Spec einen Check laufen lassen und pro fehlgeschlagenem Check ein Finding erzeugen, mit Zitat der auslösenden Regel im eckigen Klammerpräfix gemäß `review-plan`
- **MUSS [MUST]** die Schweregrade wie folgt zuordnen und **MUSS NICHT [MUST NOT]** ohne dokumentierte Ausnahme davon abweichen:
  - Ein fehlgeschlagenes MUST → `Critical`
  - Ein fehlgeschlagenes SHOULD → `Warning`
  - Ein fehlgeschlagenes MAY, von dem der Skill klar profitieren würde → `Suggestion`
  - Eine Beobachtung, die keine Regel abdeckt, die ein künftiger Reviewer aber kennen möchte → `Info`
- **MUSS [MUST]** folgende hochwirksamen Bereiche auch dann explizit abdecken, wenn die entsprechende Regel in `skill-management` nur als SHOULD formuliert ist: Vorhandensein der Frontmatter-Felder (`name`, `description`), description-enthält-konkrete-Trigger, Fehlen hartcodierter absoluter Pfade in referenzierten Assets, Existenz jedes vom Skill referenzierten Templates — ein referenziertes Template/Asset, das nicht existiert, ist ein `Critical` (gebrochene Referenz); die Absicht, es vor dem Merge zu ergänzen, wird dadurch verfolgt, dass der Plan-Punkt offen bleibt, nicht durch einen niedrigeren Schweregrad
- **SOLLTE [SHOULD]** jeden Teil des Skill-Bodys, der in eine Geschwister-Datei ausgelagert werden könnte, um den Haupt-Prompt unter dem in `skill-management` genannten Soft-Längen-Ziel zu halten, als `Info` flaggen

### Checks aus `skill-vs-agent`

- **MUSS [MUST]** bestätigen, dass der Skill-Body einen **Rationale-Abschnitt** enthält, der mindestens eine entscheidende Dimension für die Skill-statt-Agent-Wahl benennt; dessen Fehlen ist ein `Critical`
- **SOLLTE [SHOULD]** verifizieren, dass mindestens eine Gegen-Dimension benannt ist, wenn die Entscheidung knapp war; das Fehlen ist ein `Suggestion`, konsistent mit dem SHOULD in `skill-vs-agent` und symmetrisch zur entsprechenden Regel in `agent-review`
- **MUSS [MUST]** verifizieren, dass der Skill das Skill-Tool nicht im Namen eines Agents dispatched (in dieser Richtung nicht anwendbar, aber die Gegenrichtung — ein Skill, der einen Agent via Agent-Tool ruft — ist erwartet und ist kein Finding)
- **MUSS [MUST]** einen Duplikat-Capability-Check fahren: jede andere `skills/*/SKILL.md` und `agents/*.md` `description`-Zeile **nur im aktuellen Repository** auf semantische Überlappung grepen; jede plausible Überlappung erzeugt ein `Warning`, das das Peer-Artefakt und die Überlappung benennt, damit der Autor vor dem Landen einen Merge, Rename oder klareren Split vorschlagen kann. Plugin-übergreifende Überlappung liegt hier außerhalb des Scopes — die Duplikat-Präventions-Regel aus `skill-vs-agent` ist auf dieses Plugin beschränkt, und die portfolioweite Reconciliation über installierte Plugins gehört zu `spec-drift-audit` / `portfolio-audit`. Der Duplikat-Capability-Schweregrad ist `Warning`, unabhängig davon, ob das Ziel ein neuer oder überarbeiteter Skill ist; der Kontext neu-vs-überarbeitet wird im `## Scope` des Plans festgehalten, nicht im Schweregrad kodiert

### Checks aus dem Mehrsprachigkeits-Template-Default

- **MUSS [MUST]** bestätigen, dass Frontmatter und System-Prompt-Inhalt in Englisch sind, unabhängig von der Konversationssprache, in der der Skill autoriert wurde; jeder nicht-englische Frontmatter- oder Body-Inhalt ist ein `Critical` (die Antwort-Sprache zur Laufzeit ist eine Runtime-Wahl, im Body dokumentiert, und fällt nicht unter diese Regel)

### Checks aus externer Skill-Struktur-Validierung

- **MUSS [MUST]** einen externen Skill-Struktur-Validator laufen lassen, der `SKILL.md`-Frontmatter, Body-Form und Erreichbarkeit referenzierter Assets prüft, bevor der Plan emittiert wird; Anthropics `skills-ref`-CLI ist das kanonische Beispiel, die Anforderung ist aber nicht an ein bestimmtes Binary gebunden
- **MUSS [MUST]** jeden vom Validator gemeldeten Fehler auf ein `Critical`-Finding und jede Warnung auf ein `Warning`-Finding mappen und die Regel-Kennung des Validators im eckigen Klammerpräfix gemäß `review-plan` zitieren
- **MUSS [MUST]** im `## Scope`-Abschnitt des Plans festhalten, welcher Validator und welche Version verwendet wurden, damit ein späteres Re-Review Validator-Drift genauso erkennen kann wie Spec-Drift; Validator und Version werden vom Repository-Tooling bereitgestellt (für dieses Repo das Taskfile-Target `validate:skills` als `skills-ref`-Stop-Gap) und pro Review im `## Scope` festgehalten, und diese Spec pinnt bewusst kein bestimmtes Binary und keine bestimmte Version
- **MUSS NICHT [MUST NOT]** diesen Check mit der Begründung überspringen, dass andere Checks in dieser Spec bereits überlappende Bereiche abdecken; der externe Validator läuft zusätzlich zu den spec-abgeleiteten Checks, weil er strukturelle Probleme fängt, die einem spec-lesenden Reviewer entgehen können
- **KANN [MAY]** ein einzelnes Validator-Finding nur dann unterdrücken, wenn ein expliziter Override im `## Scope` des Plans mit einer einzeiligen Begründung festgehalten wird, die in einer anderen Spec oder einer dokumentierten Projektentscheidung verankert ist

### Checks aus Skill-Creation-Best-Practices

Spiegelt die Autoren-Anforderungen aus `skill-management` §„Autoren-Qualität" (gemäß <https://agentskills.io/skill-creation/best-practices> und <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>); den Upstream-Regel-Slug zitieren, wenn ein Finding eine konkrete Regel pinnt.

- **MUSS [MUST]** verifizieren, dass `SKILL.md` unter 500 Zeilen und 5.000 Tokens liegt; Überschreitung ist ein `Critical`
- **MUSS [MUST]** verifizieren, dass jedes unter `references/` / `templates/` / `assets/` / `scripts/` referenzierte Asset eine Lade-Trigger-Formulierung in `SKILL.md` trägt („Read X when Y", „use template Z for output Q"); ungetriggerte Referenzen sind ein `Warning`
- **SOLLTE [SHOULD]** auf einen **Gotchas**-Abschnitt prüfen, wenn der Skill gegen eine nicht-offensichtliche Umgebung arbeitet; das Fehlen ist ein `Warning`, sofern der Skill klar gegen eine solche Umgebung arbeitet, ansonsten ein `Suggestion`
- **SOLLTE [SHOULD]** Menü-ohne-Default-Formulierungen (mehrere gleichwertige Optionen ohne einen designierten Default) und Einzel-Antwort-Deklarationen dort, wo wiederverwendbare Prozeduren passen würden, flaggen; beide sind `Suggestion`s

### Checks aus Frontmatter-Validierung (Anthropic-Plattform-Limits)

Spiegelt `skill-management` §„Frontmatter-Validierung"; die ursprüngliche Regel zitieren, wenn ein Finding sie pinnt.

- **MUSS [MUST]** verifizieren, dass `name` 1–64 Zeichen hat, nur ASCII-Kleinbuchstaben/-Ziffern/-Bindestriche, nicht mit `-` beginnt oder endet und kein `--` enthält; jede Verletzung ist ein `Critical`
- **MUSS [MUST]** verifizieren, dass `name` nicht die reservierten Tokens `anthropic` oder `claude` enthält (die Reserved-Word-Regel gilt nur für `name`, gemäß `skill-management` §Frontmatter validation, da beschreibende Felder wie `description` legitim `claude` erwähnen dürfen); eine Verletzung ist ein `Critical` (der Upstream-Plattform-Validator weist den Skill ab), außer der Artefakt-Body trägt einen `## Reserved-token rationale`-Abschnitt, der die enge Claude/Anthropic-Surface-Ausnahme beansprucht
- **MUSS [MUST]** verifizieren, dass weder `name` noch `description` XML-Tags enthält; eine Verletzung ist ein `Critical`
- **MUSS [MUST]** verifizieren, dass `description` nicht-leer und ≤1024 Zeichen ist; Über-Cap oder leer ist ein `Critical`
- **MUSS [MUST]** verifizieren, dass `description` in der **dritten Person** verfasst ist: das Vorkommen der Pronomen „I", „you" oder „we" (oder anderer Nicht-Dritte-Person-Marker) im Description-Text ist ein `Critical`. Zitat: `skill-management` §Frontmatter-Validierung, abgeleitet aus den Upstream-Plattform-Best-Practices ([R5](#referenzen))
- **MUSS [MUST]** verifizieren, dass `description` sowohl *was der Skill tut* als auch *wann er einzusetzen ist* benennt; das Fehlen von Trigger-Phrasen ist ein `Warning` (Skill wird schwer auffindbar)
- **SOLLTE [SHOULD]**, wenn `when_to_use` gesetzt ist, verifizieren, dass kombinierter Text aus `description` + `when_to_use` unter 1.536 Zeichen bleibt; Über-Cap ist ein `Warning` (Laufzeit kürzt und trifft typischerweise die Trigger-Phrasen)
- **SOLLTE [SHOULD]** verifizieren, dass der Skill-Name einer konsistenten Form über das Plugin folgt (Gerundium bevorzugt; Verb-Substantiv akzeptabel; gemischte Formen innerhalb eines Repositorys sind ein `Suggestion`-würdiger Smell)
- **MUSS [MUST]** generische Namen (`helper`, `utils`, `tools`, `documents`, `data`, `files`) als `Critical` flaggen; sie unterminieren Skill-Discovery

### Checks aus Progressive Disclosure und Datei-Referenzen

Spiegelt `skill-management` §„Progressive Disclosure und Datei-Referenzen"; die ursprüngliche Regel zitieren, wenn ein Finding sie pinnt.

- **MUSS [MUST]** verifizieren, dass Datei-Referenzen innerhalb von `SKILL.md` maximal eine Ebene tief sind (keine `SKILL.md` → `A.md` → `B.md`-Ketten); eine Kette ist ein `Warning` (Claude tendiert zu Partial-Reads bei verschachtelten Referenzen)
- **MUSS [MUST]** verifizieren, dass jede Hilfsdatei länger als 100 Zeilen mit einem Inhaltsverzeichnis beginnt; das Fehlen ist ein `Warning`
- **MUSS [MUST]** verifizieren, dass keine Hilfsdatei eine Regel wiederholt, die `SKILL.md` anders formuliert, und dass jede im Body genannte Anzahl über die Hilfsdateien zu dem passt, was dort liegt; eine widersprechende Hilfsdatei ist ein `Warning` oder ein `Critical`, wo genau diese Datei diejenige ist, die ein Lauf für die von der Regel bestimmte Entscheidung lädt
- **SOLLTE [SHOULD]** für jede Spec, die der Skill als maßgebliche Quelle zitiert, verifizieren, dass eine vom Skill wiederholte Regel noch dem Wortlaut der Spec entspricht; ein von einer Spec-Änderung zurückgelassener Skill ist ein `Warning`. Das ist die eine Klausel der gespiegelten Regel, die sich nicht innerhalb des Skill-Ordners prüfen lässt, bleibt hier deshalb ein SOLLTE und ist vor allem die Pflicht des Autors im Update-Durchgang des `spec`-Skills
- **MUSS [MUST]** verifizieren, dass jede Skript-Referenz die Ausführungs-Absicht explizit macht („Run X to …" vs. „See X for the algorithm of …"); mehrdeutige Formulierung ist ein `Warning`
- **MUSS [MUST]** verifizieren, dass jeder Pfad in `SKILL.md` und Hilfsdateien Forward-Slashes verwendet; Backslash-Pfade sind unter Unix ein `Critical`
- **MUSS [MUST]** verifizieren, dass jeder MCP-Tool-Verweis die voll qualifizierte `ServerName:tool_name`-Form nutzt; nackte Tool-Namen sind ein `Warning`
- **MUSS [MUST]** zeitabhängige Informationen, die nicht in einem `## Old patterns`-Abschnitt eingeschlossen sind, flaggen; „use the new API after August 2025" inline ist ein `Warning`

### Checks aus Laufzeit und Lifecycle

Spiegelt `skill-management` §„Laufzeit- und Lifecycle-Bewusstsein"; die ursprüngliche Regel zitieren, wenn ein Finding sie pinnt.

- **MUSS [MUST]** verifizieren, dass der Skill-Body als **Standing Instructions für die restliche Session** trägt; Einmal-Schritt-Formulierungen („now do X", „as a first step …"), die nach Compaction ihre Bedeutung verlieren, sind ein `Warning`. Zitat: Skill-Inhalt bleibt über Turns im Kontext und wird nicht erneut gelesen ([R4](#referenzen))
- **SOLLTE [SHOULD]** die Token-Anzahl von `SKILL.md` schätzen (grob: 4 Zeichen pro Token) und ein `Suggestion` flaggen, wenn der Skill-Body 5.000 Tokens überschreitet, da Auto-Compaction beim Re-Attach alles jenseits dieser Marke stillschweigend kürzt ([R4](#referenzen))
- **SOLLTE [SHOULD]** verifizieren, dass `allowed-tools`, sofern vorhanden, einen bewussten, im Body dokumentierten Pre-Approval-Vertrag ausdrückt (damit ein späterer Maintainer versteht, was sich der Skill selbst gewährt hat); stille `allowed-tools`-Deklarationen sind ein `Suggestion`
- **SOLLTE [SHOULD]** verifizieren, dass Skills mit `disable-model-invocation: true` nicht zugleich von der `skills:`-Preload-Liste eines Subagents referenziert werden (sie würden zur Laufzeit stillschweigend übersprungen, mit nur einer Debug-Log-Warnung) ([R4](#referenzen))

### Checks aus Evaluations-Disziplin

Spiegelt `skill-management` §„Evaluations-Disziplin"; die ursprüngliche Regel zitieren, wenn ein Finding sie pinnt.

- **SOLLTE [SHOULD]** verifizieren, dass der Skill mindestens drei Evaluations-Szenarien (Eingabe-Prompt, optionale Eingabe-Dateien, erwartetes Verhalten) unter `examples/` oder einem benachbarten Ordner hat; das Fehlen ist ein `Suggestion` für neue Skills, ein `Warning` für Skills, die seit der letzten Evaluation mehr als drei Edits hatten ([R3](#referenzen))
- **KANN [MAY]** ein `Info`-Finding aufnehmen, wenn keine Evidenz für Multi-Modell-Tests existiert (kein Kommentar, kein Beispiel-Output, kein Test-Rubric, das Haiku / Sonnet / Opus erwähnt) ([R3](#referenzen))

### Checks aus Spec-Driven-Development

- **MUSS [MUST]** einen Spec-Anchor-Check fahren: verifizieren, dass der SKILL.md-Body mindestens eine Referenz auf einen `spec/...`-Pfad enthält. Ein Skill ohne jegliche Spec-Zitation ist ein `Critical`-Finding gemäß MUST aus `spec/project/spec-driven-development/`
- **KANN [MAY]** diesen Check mit einer dokumentierten Ausnahme im `## Scope`-Abschnitt des Plans unterdrücken, wenn ein Skill ausdrücklich als „implementation-only" klassifiziert ist (z. B. `dependency-audit`, `quality-gate`) — die Unterdrückung selbst muss aber in einer Spec oder einer festgehaltenen Projektentscheidung verankert sein
- Begründung: Dieser Check operationalisiert das MUST aus Spec-Driven-Development, das bisher nur operator-enforced war

### Review-Prozedur

- **MUSS [MUST]** damit beginnen, die kanonischen Specs `skill-management`, `skill-vs-agent` und `review-plan` zu lesen, bevor ein Finding erzeugt wird; Findings ohne Anker in einer dieser Specs sind keine gültige Ausgabe dieser Prozedur
- **MUSS [MUST]** Findings in dieser Reihenfolge erzeugen: externe-Validator-Findings → Frontmatter → Description/Trigger → System-Prompt-Body → Rationale-Abschnitt → referenzierte Assets → Duplikat-Prävention-Check → Best-Practices-Checks → Spec-Anchor-Check → INFO-Beobachtungen
- **MUSS [MUST]** genau eine `review-plan`-Datei unter `.audits/skill-review/<skill-name>.md` emittieren; der Reviewer **MUSS [MUST]** jede Lifecycle-Regel aus `review-plan` befolgen, einschließlich der Single-Plan-pro-Ziel-Invariante und des Löschungs-Commit-Message-Formats
- **SOLLTE [SHOULD]** im `## Scope`-Abschnitt des Plans die Git-SHAs der angewandten Spec-Versionen einbetten, damit ein späteres Re-Review erkennen kann, ob Findings durch eine Spec-Revision veraltet sein könnten
- **KANN [MAY]** rein stilistische Beobachtungen (Vale, Markdown-Linting) als `Info`-Findings aufnehmen, wenn sie dem Autor helfen, **MUSS NICHT [MUST NOT]** sie aber zu `Warning` oder `Critical` erheben — die bleiben bei ihrem eigenen Tooling

Diese Prozedur wird als Skill (`skills/skill-review/`) ausgeliefert, gemäß der Orchestrator-ist-ein-Skill-Regel aus `skill-vs-agent`; der Plan persistiert unabhängig vom Einstiegspunkt unter `.audits/skill-review/` gemäß `review-plan`.

### Bezug zu anderen Specs

- **MUSS [MUST]** auf `review-plan` für das Output-Format verweisen; dessen Anforderungen nicht hier wiederholen
- **MUSS NICHT [MUST NOT]** irgendetwas neu spezifizieren, das bereits in `skill-management` oder `skill-vs-agent` steht; wenn diese Spec und eine jener abweichen, gewinnt die Autoren-Spec, und diese Spec ist die, die aktualisiert werden muss
- **SOLLTE [SHOULD]**, wenn der zu reviewende Skill einen Agent dispatched, ein begleitendes `agent-review` für diesen Agent nur dann auslösen, wenn der Agent noch nicht gegen seine aktuelle Quell-Revision reviewt wurde — die Entscheidung im `## Scope` des Plans festhalten, damit nachgelagerte Akteure wissen, ob der dispatched Agent abgedeckt ist

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] Ein durchgearbeitetes Beispiel existiert, das diese Review-Prozedur auf einen Skill in `nolte-shared` anwendet (z. B. `audience-identify`) und einen konformen Plan unter `.audits/skill-review/` erzeugt
- [ ] Jeder Skill in `skills/` wurde seit Adoption dieser Spec mindestens einmal gegen die aktuelle `skill-management`-Revision reviewt, verifizierbar entweder durch einen offenen Plan unter `.audits/skill-review/` oder durch einen schließenden Commit in `git log`, der dem `review-plan`-Löschmuster entspricht
- [ ] Kein Skill in `skills/` fehlt ein Rationale-Abschnitt; der Rationale-Abschnitts-Check über alle Skills erzeugt null `Critical`
- [ ] Keine zwei Skills in `skills/` teilen eine äquivalente Capability-Aussage, verifiziert durch Stichprobe jedes Plan-Duplikat-Präventions-Findings
- [ ] Jeder offene Plan unter `.audits/skill-review/` entspricht der Vier-Abschnitts-Struktur und dem YAML-Frontmatter aus `review-plan`
- [ ] Die Abnahmekriterien der `skill-management`-Spec verweisen für die Review-Seite ihrer Autoren-Regeln auf diese Spec
- [ ] Eine Stichprobe von drei geschlossenen Plan-Löschungen in `git log` zeigt exakt das Commit-Message-Format `review(skill-review): close <skill> — <counts>`
- [ ] Jeder Plan unter `.audits/skill-review/` hält fest, welcher externe Skill-Struktur-Validator und welche Version gefahren wurde, und kein Plan schließt mit einem ungelösten vom Validator gemeldeten `Critical`
- [ ] Jeder Plan unter `.audits/skill-review/` führt die Best-Practices-Checks aus §„Checks aus Skill-Creation-Best-Practices" gegen den Ziel-Skill aus
- [ ] Jeder Plan unter `.audits/skill-review/` führt die in dieser Spec neu hinzugefügten Frontmatter-Validierungs-, Progressive-Disclosure-, Laufzeit-Lifecycle- und Evaluations-Disziplin-Checks aus und zitiert `skill-management` §<Section> als Regel-Anker

## Referenzen

Quellen für die zusätzlichen Checks oben. Bei Findings, die eine konkrete Upstream-Regel pinnen, im eckigen Klammerpräfix den passenden Eintrag zitieren.

- [R1] Skill-Management-Spezifikation (dieses Plugin) — `spec/claude/skill-management/`
- [R2] Skill-vs-Agent-Entscheidung (dieses Plugin) — `spec/claude/skill-vs-agent/`
- [R3] Skill authoring best practices, Anthropic-Plattform-Doku — <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R4] Extend Claude with skills, Claude-Code-Doku — <https://code.claude.com/docs/en/skills>
- [R5] Best practices for skill creators, agentskills.io — <https://agentskills.io/skill-creation/best-practices>
- [R6] Agent Skills, formale Spezifikation — <https://agentskills.io/specification>

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Die Einzelentscheidungen und Begründungen sind in der Git-Historie erhalten (Entscheidungslog, 2026-06-06)._
