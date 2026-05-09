# Spezifikations-getriebene Entwicklung

Status: draft

## Kontext

Das Portfolio trägt bereits einen umfangreichen Spec-Bestand unter `spec/project/` und `spec/claude/`. Jede einzelne Spec regiert ein Thema — Branching-Modell, Pull-Request-Workflow, Skill-Authoring, Planning-Suite, Release-Automation — und nachgelagerte Skills, Agents und CI-Konfigurationen schöpfen daraus. Was bisher nicht axiomatisch erklärt ist: **warum Specs überhaupt existieren und in welchem Verhältnis sie zur Implementierung stehen.** Ohne diese Erklärung driftet das Portfolio Richtung „Code-First, Spec-als-nachträgliche-Dokumentation": Implementierungs-Entscheidungen sammeln sich in Claude-Code-Prompts, Ad-hoc-Konversationen oder Commit-Message-Begründungen, und der Spec-Bestand wird zum Schnappschuss vergangener Absicht statt zur lebenden Grundlage gegenwärtiger Praxis.

Diese Spec verankert das Meta-Prinzip: **jede Entwicklungs-Aktion in diesem Portfolio ist durch eine Spezifikation getrieben.** Die Spec existiert vor der Änderung, die Änderung referenziert die Spec, die sie implementiert, und wo Realität und Spec auseinanderlaufen, ist die Auflösung entweder eine Code-Änderung, die die Implementierung wieder an die Spec anpasst, oder eine Spec-Revision, die die neue Realität festschreibt — niemals stille Code-Drift.

Das Prinzip stützt sich auf vier Säulen:

1. **Nachvollziehbarkeit**: Jede Implementierungs-Entscheidung löst auf einen konkreten MUSS/SOLLTE/KANN in einer versionierten Spec unter `spec/` auf.
2. **Reproduzierbarkeit**: Dieselbe Spec, gegen ein vergleichbares Repository angewandt, produziert dieselbe Form — unabhängig vom Operator oder von der Claude-Code-Session, die sie ausgeführt hat.
3. **Transparenz**: Entscheidungs-Begründung lebt in `spec/`-getracktem Markdown unter git, nicht in flüchtigen Prompts, undokumentierter Chat-History oder mündlicher Absprache.
4. **Kontinuierliche Weiterentwicklung**: Jeder Audit-Befund, Defekt oder operative Reibung mündet entweder in einer Code-Änderung, die eine bestehende Spec implementiert, oder in einer Spec-Revision, die die geänderte Realität festschreibt — niemals in einer Code-Änderung ohne Spec-Anker.

Dieses Prinzip ist die axiomatische Vorbedingung, auf der die existierenden Process-Specs (`continuous-improvement`, `spec-drift-audit`, `spec-readiness`, `pull-request-workflow`, `skill-management`, `agent-management`) operieren. Die Planning-Suite (`mission`, `roadmap`, `feature`, `sprint`) ist selbst spec-driven by construction — jedes Artefakt unter `project/` zitiert die Spec, die es regiert. Dieses Dokument macht diesen latenten Vertrag explizit und tragend.

## Ziele

- Jede Implementierungs-Änderung in diesem Portfolio an eine versionierte Spezifikation verankern, sodass Nachvollziehbarkeit ausnahmslos über jeden Commit, PR und jedes Release hinweg hält.
- Entscheidungs-Begründungen aus flüchtigen Oberflächen (Claude-Code-Prompts, Chat-Transkripte, mündliche Absprachen) heraushalten und in `spec/`-getracktes Markdown verlagern, das Session-Grenzen und Tool-Wechsel überdauert.
- Die existierenden Process-Specs (`continuous-improvement`, `spec-drift-audit`, `spec-readiness`, `pull-request-workflow`, `skill-management`, `agent-management`) als operationale Konsequenzen dieses Prinzips behandeln, nicht als Konkurrenten.
- Die Spec zur Autorität und den Prompt zur Implementierung machen: ein Claude-Code-Prompt darf einem Beitragenden helfen, die Spec zu finden oder anzuwenden, aber überschreibt sie niemals, wenn beide auseinanderlaufen.
- Jedes ausführbare Plugin-Asset — jedes `skills/<name>/SKILL.md` und jedes `agents/<name>.md` — an die Spec verankern, die es implementiert, sodass das Verhalten des Plugins selbst auf geschriebene Absicht rückführbar ist.
- Sicherstellen, dass die Planning-Suite (`mission`, `roadmap`, `feature`, `sprint`) und jede zukünftige Portfolio-Capability denselben Spec-Anker-Vertrag automatisch erbt, indem sie zuerst unter `spec/` authored wird.

## Nicht-Ziele

- Ersatz für `continuous-improvement` (der Audit-und-Dispatch-Prozess), `spec-drift-audit` (die Spec-versus-Implementierung-Reconciliation) oder `spec-readiness` (das Per-Spec-Quality-Gate). Diese Spec deklariert, was die drei voraussetzen; sie implementiert sie nicht neu.
- Vorschreiben einer Spec-Format-Konvention jenseits dessen, was der `spec`-Skill und `templates/spec.template.md` schon regeln. Sechs Sektionen (Kontext, Ziele, Nicht-Ziele, Anforderungen, Akzeptanzkriterien, Offene Fragen), RFC-2119-Schlüsselworte, EN-canonical mit Übersetzungen — all das bleibt delegiert.
- Verlangen, dass eine vollständig geschriebene Spec vor der ersten Prototyp-Codezeile existiert. Exploration über das `exp/`-Branch-Prefix in `branching-model` bleibt erlaubt; die Spec-Anker-Verpflichtung greift bei der Promotion, nicht bei der Exploration.
- Ersatz für architektonische Entscheidungs-Records (ADRs). Die `docs-freshness`-Spec regiert ADR-Form und -Lifecycle separat; Spezifikations-getriebene Entwicklung ist die übergeordnete Norm, unter der ADRs und Specs beide leben.
- Vorschreiben eines bestimmten Tools zur Durchsetzung der Spec-Verankerung. Automatisierung kann später kommen (ein `spec-anchor-lint`-Skill, ein CI-Check); diese Spec definiert die Regel, nicht ihren Durchsetzungs-Mechanismus.

## Anforderungen

- **MUSS [MUST]** jede Änderung an Runtime-Code, CI-Konfiguration, Plugin-Assets (`skills/`, `agents/`, `.claude-plugin/`) oder Repository-Dokumentation an eine bestehende Spec verankern, die die Änderung implementiert, oder selbst eine Spec-Revision sein. Eine Änderung, die keinen der beiden Pfade erfüllt, ist ein Workflow-Health-Befund laut `spec/project/workflow-health/`.
- **MUSS [MUST]**, wenn ein Pull Request Implementierungs-Pfade berührt (alles außerhalb von `spec/`), mindestens eine `Refs spec/<topic>/<slug>/`-Zeile in seinem **Linked issues**-Abschnitt laut `spec/project/pull-request-workflow/` tragen. Die existierende Auto-Refs-Regel der Spec gilt schon für PRs, die `spec/`-getrackte Dateien berühren; diese Spec dehnt die Verpflichtung auf PRs aus, die Implementierung berühren, sodass jeder PR — nicht nur Spec-PRs — verankert ist.
- **MUSS [MUST]** jede neue Spezifikation den `spec`-Skill durchlaufen, sodass der Duplicate-Check, das EN-canonical-plus-Translation-Pairing und die `spec/README.md`-Index-Regeneration konsistent ablaufen. Eine Spec, die ohne diesen Pfad geschrieben wurde, ist ein `spec-drift-audit`-Befund, unabhängig davon, wie gut ihr Inhalt ist.
- **MUSS [MUST]** in jedem `skills/<name>/SKILL.md` und in jedem `agents/<name>.md` mindestens eine Spec zitieren, die das Artefakt implementiert — entweder im YAML-Frontmatter-`description`-Feld oder im Body-Text. Skills und Agents, die nicht auf eine Spec zurückführen, sind ein `spec-drift-audit`-Befund; die Abwesenheit ist selbst Drift, keine Ausnahme.
- **DARF NICHT [MUST NOT]** irgendein Claude-Code-Prompt — System-Prompt, Slash-Command-Argument, Ad-hoc-Chat-Anweisung, Agent-Prompt — als autoritative Quelle einer Implementierungs-Entscheidung herangezogen werden. Der Prompt darf die Spec zitieren, zusammenfassen oder beim Auffinden helfen, aber die Spec ist die stehende Antwort. Wenn Prompt und Spec auseinanderlaufen, gewinnt die Spec; der Prompt wird aktualisiert, nicht die Spec.
- **SOLLTE [SHOULD]** jeder Audit-Befund (aus `spec-drift-audit`, `workflow-health`, `quality-gate`, `docs-freshness` oder manueller Beobachtung) in genau eines von zwei Ergebnissen münden: eine Code-Änderung, die die bestehende Spec implementiert, oder eine Spec-Revision, die die neue Realität festschreibt. Ein dritter Pfad — Code-Änderung ohne Spec-Berührung — ist selbst ein Workflow-Health-Befund.
- **KANN [MAY]** ein `exp/`-Branch (laut `branching-model`) ohne Spec-Anker existieren, solange die Exploration offen ist. Bei der Promotion zu `feat/`, `fix/`, `chore/` oder `docs/` **MUSS [MUST]** der Branch entweder eine bestehende Spec referenzieren oder von einer parallelen Spec-Revision begleitet sein; die Promotion eines `exp/`-Branches mit weder noch ist verboten.
- **MUSS [MUST]** dieses Prinzip rekursiv für sich selbst gelten: Diese Spec wird über den `spec`-Skill authored, folgt `templates/spec.template.md` und referenziert die Hard Rules des Skills. Zukünftige Revisionen dieser Spec folgen demselben Pfad; keine Out-of-Band-Edits.

## Akzeptanzkriterien

- [ ] Jeder Pull Request, der nach Adoption dieser Spec auf `develop` landet und Implementierungs-Pfade berührt, trägt mindestens eine `Refs spec/<path>`-Zeile im **Linked issues**-Abschnitt seines Bodys.
- [ ] Jedes `skills/<name>/SKILL.md` und jedes `agents/<name>.md` im Repository zitiert mindestens eine Spec, die es implementiert — verifizierbar durch `grep -l "spec/" skills/*/SKILL.md agents/*.md`, das jede Datei zurückgibt.
- [ ] Kein Audit-Befund wird durch einen PR geschlossen, der weder eine bestehende Spec implementiert noch eine revidiert; PRs, die einen Befund über einen dritten Pfad schließen wollen, schlagen das Review.
- [ ] Kein `exp/`-Branch wird direkt nach `develop` gemerged; Promotion zu `feat/`/`fix/`/`chore/`/`docs/` passiert zuerst und die Spec-Anker-Verpflichtung wird an diesem Punkt erfüllt.
- [ ] Diese Spec trägt im `## Offene Fragen`-Block einen verifizierbaren Querverweis auf den `spec`-Skill (`skills/spec/SKILL.md`) und auf `templates/spec.template.md`, sodass die Rekursions-Behauptung auditierbar ist.
- [ ] Jede Spec unter `spec/` wurde über den `spec`-Skill authored — verifizierbar durch Abwesenheit von verwaisten Spec-Ordnern, die den Index-Regeneration-Schritt umgehen (jeder Eintrag in `spec/README.md` löst auf, jeder Spec-Ordner taucht im Index auf).
- [ ] Kein Claude-Code-Prompt-Artefakt unter `.claude/` oder in Skill-`description`-Feldern widerspricht einer publizierten Spec; der `spec-drift-audit`-Skill ist der kanonische Detektor für den Widerspruch.

## Offene Fragen

- Automatisierte Durchsetzung der Spec-Anker-Regel für PR-Bodies und Skill/Agent-Frontmatter ist noch nicht verdrahtet. Ein zukünftiger `spec-anchor-lint`-Skill (oder eine Erweiterung des Body-Validators von `pull-request-workflow`) würde die Schleife schließen. Bis dahin ist die Regel operator-durchgesetzt und `spec-drift-audit` fängt den Long-Tail.
- Kosmetische Edits — Tippfehler-Korrekturen, Em-Dash-Lint-Reparaturen, Vale-getriebene Prosa-Cleanups — fallen technisch unter das MUSS in Anforderung #1, tragen aber de facto keine semantische Änderung. Vorgeschlagene Lesart: solche Fixes implementieren die `prose-style`-Spec (oder welche Spec auch immer die Lint-Regel ursprünglich anstößt), sodass der Spec-Anker implizit ist. Diese Spec überlässt die explizite Benennung des impliziten Ankers einer Folge-Revision, sobald die Grenze in der Praxis beobachtet wurde.
- Renovate-Bot-PRs (`dependencies`-Bumps) landen ohne menschliches Authoring und ohne explizite `Refs spec/`-Zeile. Vorgeschlagene Lesart: Der Bot referenziert implizit die Specs `dependency-audit` und `project-structure`, die Pin-Strategie und Audit-Kadenz regeln, sodass die PRs des Bots die Regel ohne Body-Modifikation erfüllen. Diese Spec hält den Vorschlag fest, härtet aber das Body-Template des Bots noch nicht.
- Die rekursive Selbst-Anwendungs-Klausel in Anforderung #8 nennt `skills/spec/SKILL.md` und `templates/spec.template.md` als unmittelbare Vorfahren. Ob das Prinzip auch auf den `claude-plugin-developer`-Agent (der Skills und Agents aus der Spec authored) und auf den `pull-request-create`-Skill (der die PR-Bodies schreibt, die `Refs`-Zeilen tragen) ausgedehnt wird, ist eine Selbst-Anwendungs-Frage, die zurückgestellt wird, bis das Verhalten dieser Tools sich stabilisiert hat.
