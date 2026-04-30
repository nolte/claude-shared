# Claude-Skill-Review

Status: draft

## Kontext
<!-- Warum existiert diese Spec? Welches Problem, welcher Bedarf oder welche Einschränkung treibt sie? -->

Die `skill-management`-Spec definiert, wie ein Skill *erstellt* wird — On-Disk-Form, Frontmatter, Templates, Distributionsform. Was sie nicht definiert, ist, wie ein Skill *reviewt* wird: welche Anforderungen ein Reviewer prüft, in welcher Reihenfolge und welches Deliverable das Review hinterlässt. Ohne eine geteilte Review-Prozedur erzeugen zwei Reviewer desselben Skills inkompatible Ergebnisse, die Rationale-Dokumentations-Regel aus `skill-vs-agent` verrutscht still, und Plugin-Entwickler, die die Review-Ausgabe konsumieren, müssen die private Form jedes Reviewers rückentwickeln. Diese Spec definiert die bindende Review-Prozedur für Skills im `nolte-shared`-Plugin, verweist auf `skill-management` und `skill-vs-agent` als Wahrheitsquellen dafür, was als Finding zählt, und delegiert den Output-Format-Vertrag an `review-plan`. Ein Skill-Review erzeugt genau ein `review-plan`-Artefakt unter `.audits/skill-review/<skill-name>.md`; sobald jeder Punkt verarbeitet ist, wird der Plan gelöscht und seine Git-Historie bleibt als Audit-Trail.

## Ziele
<!-- Was diese Spec erreichen will. Stichpunkte, ergebnisorientiert. -->
- Jedes Skill-Review wendet denselben Satz von Checks aus `skill-management` und `skill-vs-agent` in derselben Reihenfolge mit demselben Schweregrad-Mapping an
- Review-Output ist ein `review-plan`-Artefakt — parsbar, abarbeitbar und pro Finding auf eine konkrete Spec-Anforderung zurückführbar
- Skill-Autoren können das Review an ihrer eigenen Arbeit fahren, bevor sie sie einreichen; ein späterer Reviewer (Mensch oder LLM) erzielt auf demselben Quellbaum identische Ergebnisse
- Plugin-Entwickler können gegen die Review-Ausgabe skripten (Plan-Dateien parsen, Merges auf offene `BLOCKER` gaten, offene Reviews zählen), ohne reviewer-spezifische Konventionen modellieren zu müssen
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
  - Ein fehlgeschlagenes MUST → `BLOCKER`
  - Ein fehlgeschlagenes SHOULD → `WARNING`
  - Ein fehlgeschlagenes MAY, von dem der Skill klar profitieren würde → `SUGGESTION`
  - Eine Beobachtung, die keine Regel abdeckt, die ein künftiger Reviewer aber kennen möchte → `INFO`
- **MUSS [MUST]** folgende hochwirksamen Bereiche auch dann explizit abdecken, wenn die entsprechende Regel in `skill-management` nur als SHOULD formuliert ist: Vorhandensein der Frontmatter-Felder (`name`, `description`), description-enthält-konkrete-Trigger, Fehlen hartcodierter absoluter Pfade in referenzierten Assets, Existenz jedes vom Skill referenzierten Templates
- **SOLLTE [SHOULD]** jeden Teil des Skill-Bodys, der in eine Geschwister-Datei ausgelagert werden könnte, um den Haupt-Prompt unter dem in `skill-management` genannten Soft-Längen-Ziel zu halten, als `INFO` flaggen

### Checks aus `skill-vs-agent`

- **MUSS [MUST]** bestätigen, dass der Skill-Body einen **Rationale-Abschnitt** enthält, der mindestens eine entscheidende Dimension für die Skill-statt-Agent-Wahl benennt; dessen Fehlen ist ein `BLOCKER`
- **MUSS [MUST]** verifizieren, dass der Skill das Skill-Tool nicht im Namen eines Agents dispatched (in dieser Richtung nicht anwendbar, aber die Gegenrichtung — ein Skill, der einen Agent via Agent-Tool ruft — ist erwartet und ist kein Finding)
- **MUSS [MUST]** einen Duplikat-Capability-Check fahren: jede andere `skills/*/SKILL.md` und `agents/*.md` `description`-Zeile auf semantische Überlappung grepen; jede plausible Überlappung erzeugt ein `WARNING`, das das Peer-Artefakt und die Überlappung benennt, damit der Autor vor dem Landen einen Merge, Rename oder klareren Split vorschlagen kann

### Checks aus dem Mehrsprachigkeits-Template-Default

- **MUSS [MUST]** bestätigen, dass Frontmatter und System-Prompt-Inhalt in Englisch sind, unabhängig von der Konversationssprache, in der der Skill autoriert wurde; jeder nicht-englische Frontmatter- oder Body-Inhalt ist ein `BLOCKER` (die Antwort-Sprache zur Laufzeit ist eine Runtime-Wahl, im Body dokumentiert, und fällt nicht unter diese Regel)

### Checks aus externer Skill-Struktur-Validierung

- **MUSS [MUST]** einen externen Skill-Struktur-Validator laufen lassen, der `SKILL.md`-Frontmatter, Body-Form und Erreichbarkeit referenzierter Assets prüft, bevor der Plan emittiert wird; Anthropics `skills-ref`-CLI ist das kanonische Beispiel, die Anforderung ist aber nicht an ein bestimmtes Binary gebunden
- **MUSS [MUST]** jeden vom Validator gemeldeten Fehler auf ein `BLOCKER`-Finding und jede Warnung auf ein `WARNING`-Finding mappen und die Regel-Kennung des Validators im eckigen Klammerpräfix gemäß `review-plan` zitieren
- **MUSS [MUST]** im `## Scope`-Abschnitt des Plans festhalten, welcher Validator und welche Version verwendet wurden, damit ein späteres Re-Review Validator-Drift genauso erkennen kann wie Spec-Drift
- **MUSS NICHT [MUST NOT]** diesen Check mit der Begründung überspringen, dass andere Checks in dieser Spec bereits überlappende Bereiche abdecken; der externe Validator läuft zusätzlich zu den spec-abgeleiteten Checks, weil er strukturelle Probleme fängt, die einem spec-lesenden Reviewer entgehen können
- **KANN [MAY]** ein einzelnes Validator-Finding nur dann unterdrücken, wenn ein expliziter Override im `## Scope` des Plans mit einer einzeiligen Begründung festgehalten wird, die in einer anderen Spec oder einer dokumentierten Projektentscheidung verankert ist

### Checks aus Skill-Creation-Best-Practices

Spiegelt die Autoren-Anforderungen aus `skill-management` §„Autoren-Qualität" (gemäß <https://agentskills.io/skill-creation/best-practices>); den Upstream-Regel-Slug zitieren, wenn ein Finding eine konkrete Regel pinnt.

- **MUSS [MUST]** verifizieren, dass `SKILL.md` unter 500 Zeilen und 5.000 Tokens liegt; Überschreitung ist ein `BLOCKER`
- **MUSS [MUST]** verifizieren, dass jedes unter `references/` / `templates/` / `assets/` / `scripts/` referenzierte Asset eine Lade-Trigger-Formulierung in `SKILL.md` trägt („Read X when Y", „use template Z for output Q"); ungetriggerte Referenzen sind ein `WARNING`
- **SOLLTE [SHOULD]** auf einen **Gotchas**-Abschnitt prüfen, wenn der Skill gegen eine nicht-offensichtliche Umgebung arbeitet; das Fehlen ist ein `WARNING`, sofern der Skill klar gegen eine solche Umgebung arbeitet, ansonsten ein `SUGGESTION`
- **SOLLTE [SHOULD]** Menü-ohne-Default-Formulierungen (mehrere gleichwertige Optionen ohne einen designierten Default) und Einzel-Antwort-Deklarationen dort, wo wiederverwendbare Prozeduren passen würden, flaggen; beide sind `SUGGESTION`s

### Review-Prozedur

- **MUSS [MUST]** damit beginnen, die kanonischen Specs `skill-management`, `skill-vs-agent` und `review-plan` zu lesen, bevor ein Finding erzeugt wird; Findings ohne Anker in einer dieser Specs sind keine gültige Ausgabe dieser Prozedur
- **MUSS [MUST]** Findings in dieser Reihenfolge erzeugen: externe-Validator-Findings → Frontmatter → Description/Trigger → System-Prompt-Body → Rationale-Abschnitt → referenzierte Assets → Duplikat-Prävention-Check → Best-Practices-Checks → INFO-Beobachtungen
- **MUSS [MUST]** genau eine `review-plan`-Datei unter `.audits/skill-review/<skill-name>.md` emittieren; der Reviewer **MUSS [MUST]** jede Lifecycle-Regel aus `review-plan` befolgen, einschließlich der Single-Plan-pro-Ziel-Invariante und des Löschungs-Commit-Message-Formats
- **SOLLTE [SHOULD]** im `## Scope`-Abschnitt des Plans die Git-SHAs der angewandten Spec-Versionen einbetten, damit ein späteres Re-Review erkennen kann, ob Findings durch eine Spec-Revision veraltet sein könnten
- **KANN [MAY]** rein stilistische Beobachtungen (Vale, Markdown-Linting) als `INFO`-Findings aufnehmen, wenn sie dem Autor helfen, **MUSS NICHT [MUST NOT]** sie aber zu `WARNING` oder `BLOCKER` erheben — die bleiben bei ihrem eigenen Tooling

### Bezug zu anderen Specs

- **MUSS [MUST]** auf `review-plan` für das Output-Format verweisen; dessen Anforderungen nicht hier wiederholen
- **MUSS NICHT [MUST NOT]** irgendetwas neu spezifizieren, das bereits in `skill-management` oder `skill-vs-agent` steht; wenn diese Spec und eine jener abweichen, gewinnt die Autoren-Spec, und diese Spec ist die, die aktualisiert werden muss
- **SOLLTE [SHOULD]**, wenn der zu reviewende Skill einen Agent dispatched, ein begleitendes `agent-review` für diesen Agent nur dann auslösen, wenn der Agent noch nicht gegen seine aktuelle Quell-Revision reviewt wurde — die Entscheidung im `## Scope` des Plans festhalten, damit nachgelagerte Akteure wissen, ob der dispatched Agent abgedeckt ist

## Abnahmekriterien
<!-- Testbare, abhakbare Bedingungen. Reviewer müssen pro Punkt "erfüllt / nicht erfüllt" markieren können. -->
- [ ] Ein durchgearbeitetes Beispiel existiert, das diese Review-Prozedur auf einen Skill in `nolte-shared` anwendet (z. B. `audience-identify`) und einen konformen Plan unter `.audits/skill-review/` erzeugt
- [ ] Jeder Skill in `skills/` wurde seit Adoption dieser Spec mindestens einmal gegen die aktuelle `skill-management`-Revision reviewt, verifizierbar entweder durch einen offenen Plan unter `.audits/skill-review/` oder durch einen schließenden Commit in `git log`, der dem `review-plan`-Löschmuster entspricht
- [ ] Kein Skill in `skills/` fehlt ein Rationale-Abschnitt; der Rationale-Abschnitts-Check über alle Skills erzeugt null `BLOCKER`
- [ ] Keine zwei Skills in `skills/` teilen eine äquivalente Capability-Aussage, verifiziert durch Stichprobe jedes Plan-Duplikat-Präventions-Findings
- [ ] Jeder offene Plan unter `.audits/skill-review/` entspricht der Vier-Abschnitts-Struktur und dem YAML-Frontmatter aus `review-plan`
- [ ] Die Abnahmekriterien der `skill-management`-Spec verweisen für die Review-Seite ihrer Autoren-Regeln auf diese Spec
- [ ] Eine Stichprobe von drei geschlossenen Plan-Löschungen in `git log` zeigt exakt das Commit-Message-Format `review(skill-review): close <skill> — <counts>`
- [ ] Jeder Plan unter `.audits/skill-review/` hält fest, welcher externe Skill-Struktur-Validator und welche Version gefahren wurde, und kein Plan schließt mit einem ungelösten vom Validator gemeldeten `BLOCKER`
- [ ] Jeder Plan unter `.audits/skill-review/` führt die Best-Practices-Checks aus §„Checks aus Skill-Creation-Best-Practices" gegen den Ziel-Skill aus

## Offene Fragen
<!-- Ungelöste Entscheidungen, bekannte Unbekannte, Punkte, die eine Stakeholder-Antwort brauchen. -->
- Soll der Duplikat-Präventions-Check nur Agent-Descriptions aus `agents/*.md` im selben Repository lesen, oder auch den MkDocs-gerenderten Katalog über installierte Plugins abfragen, wenn ein Consumer eine Downstream-Kopie reviewt?
- Unterscheidet das Review "neuer Skill wird vorgeschlagen" von "bestehender Skill wird überarbeitet"? Dieselben Anforderungen gelten für beide, aber die Schwere eines Duplikat-Capability-Findings unterscheidet sich (Blocker vs. Warning) je nachdem, ob das Peer schon existiert oder erst mit eingeführt wird
- Soll der Rationale-Abschnitts-Check auch prüfen, dass mindestens eine *Gegen-Dimension* benannt ist, gemäß der SHOULD-Regel in `skill-vs-agent`, oder reicht die aktuelle Hürde "mindestens eine entscheidende Dimension" für das Skill-Review?
- Wenn der zu reviewende Skill von einem Template oder Asset abhängt, das noch nicht existiert: Ist das Finding ein `BLOCKER` (gebrochene Referenz) oder ein `WARNING` (Template vor Merge zu ergänzen)?
- Wie wird diese Spec aufgerufen — als `review`-Skill aus der Hauptkonversation, als Sub-Agent vergleichbar mit `audience-review` oder beides? Der Output ist in beiden Fällen derselbe Plan, aber der Einstiegspunkt beeinflusst, ob das Review automatisch persistiert
- Soll das Review eines Skills auch verifizieren, dass die `description`-Trigger des Skills nicht mit einem Runtime-Slash-Command oder einem Claude-Code-Built-in-Command überlappen, und wenn ja gegen welche autoritative Liste?
- Wo lebt das Validator-Pinning (welche Version als Ground Truth gilt) — in dieser Spec, in `skill-management` oder in der Tooling-Konfiguration des Repositories?
