# Parallele Working Copies

Status: draft
Implementierung: documentary-only — die MUSS-Regeln in dieser Spec sind Verhaltenskonventionen der Mitwirkenden (Worktree-Pfade, Lebenszyklus, Uncommitteter-Änderungs-Transfer, Claude-Code-Session-Scoping). Der §Notes-on-coverage-Absatz listet bereits auf, welche MUSS-Regeln post-hoc beobachtbare Acceptance Criteria haben und welche reine Konvention sind; kein aufrufbarer Claude-Code-Skill oder -Agent in diesem Plugin erzwingt die Regeln. Durchsetzung erfolgt durch menschliche und KI-Agent-Praxis, mit `git worktree list --porcelain`-Checks, die die beobachtbare Teilmenge der ACs unterstützen.

## Context
Ein einzelnes primäres Checkout eines Repositories kann jeweils nur einen Branch tragen. Sobald ein Mitwirkender (Mensch oder KI-Agent) zwei oder mehr Feature-Branches parallel vorantreiben möchte — zum Beispiel das Verfassen einer Spec auf `feat/parallel-working-copies`, während ein lang laufender Build auf `feat/mermaid-diagrams` läuft — zerstört ein In-Place-Branchwechsel den Working Tree desjenigen Branches, der pausiert wird: uncommittete Änderungen kollidieren, Build-Outputs werden ungültig, IDE-Indizes geraten ins Schleudern, und jegliches Tooling, das den cwd zwischengespeichert hat (Claude-Code-Sessions, Sprachserver, Watcher), muss neu hochfahren.

`git worktree` löst das ohne Klonen: Es legt einen zweiten Working Tree an, der dieselbe `.git`-Objektdatenbank teilt, aber einen eigenen unabhängigen Index, eigene Arbeitsdateien und einen eigenen `HEAD` besitzt. Diese Spec definiert die Konventionen, unter denen das Portfolio Worktrees nutzt, sodass parallele Feature-Arbeit verlässlich, nachvollziehbar und konsistent mit den bestehenden Branching-, Project-Structure- und Pull-Request-Specs verläuft.

Leserschaft: Mitwirkende (Mensch und KI-Agent), die in den Repositories dieses Portfolios parallele Feature-Arbeit leisten, sowie Reviewer, die vor dem Merge die Worktree-Hygiene prüfen.

## Goals
- Mitwirkenden ermöglichen, zwei oder mehr Feature-Branches parallel voranzutreiben, ohne dass der Working Tree eines Branches einen anderen überschreibt
- Stabile Konventionen für Worktree-Pfade, Branch-zu-Worktree-Zuordnung und Lebenszyklus (Anlegen, Nutzen, Stilllegen) bereitstellen, sodass das Layout repository- und mitwirkendenübergreifend vorhersehbar ist
- Definieren, wie Claude-Code-Sessions auf Worktrees zugeschnitten werden, damit `CLAUDE.md`-Auflösung, cwd-Annahmen und Plugin-Laden kohärent bleiben
- Das primäre Checkout der Integrationsrolle vorbehalten (auf `develop` sitzend), sodass es für Integrationsaufgaben (Rebases, Konfliktauflösung, Release-Inspektion) verfügbar bleibt, auch während Feature-Arbeit läuft; die operative Regel ist die SHOULD in Requirements §Branch-zu-Worktree-Zuordnung

## Non-Goals
- Branchnamen und Schutzregeln — definiert in `spec/project/branching-model/`
- Pull-Request-Erstellung, -Review und -Merge-Mechanik — definiert in `spec/project/pull-request-workflow/` sowie in den Skills `pull-request-create` / `pull-request-merge`
- Release-Automation, Versions-Bumping und `main`-Refresh — definiert in `spec/project/release-automation/` und `spec/project/branching-model/`
- Repository-Scaffolding (`Taskfile.yml`, `.github/`, MkDocs) — definiert in `spec/project/project-structure/`
- IDE-spezifische Multi-Root-Workspaces, Devcontainer-Setups oder Remote-Development-Tooling
- Auflösung von Merge-Konflikten zwischen Feature-Branches — ein normaler `git merge`-/`git rebase`-Belang, unbeeinflusst davon, ob die Arbeit in einem Worktree stattfand
- CI-Runner und ephemerale Cloud-Development-Umgebungen, die pro Lauf einen frischen Workspace klonen — diese starten konstruktionsbedingt aus einem sauberen Zustand und benötigen keine Worktree-Konventionen; diese Spec regelt persistente lokale Working Copies

## Requirements

### Pfad-Layout
- **MUSS [MUST]** jeden zusätzlichen Worktree außerhalb des Verzeichnisbaums des primären Checkouts platzieren; ein Worktree-Pfad **DARF NICHT [MUST NOT]** unterhalb des primären Repository-Verzeichnisses verschachtelt sein
- **SOLLTE [SHOULD]** Worktrees unter einem zentralisierten Layout `~/repos/.worktrees/<repo>/<short-slug>/` ablegen, wobei `<repo>` dem Repository-Namen aus dem `origin`-Remote entspricht und `<short-slug>` eine kebab-case-Abkürzung des Features ist (nicht zwingend identisch mit dem Branchnamen). Die zentrale Wurzel hält jede parallele Arbeitskopie auf der Maschine an einer vorhersehbaren Stelle, verringert die Gefahr, einen Worktree versehentlich unter einem anderen Repository zu verschachteln, und macht verwaiste Worktrees mit einem einzigen `ls ~/repos/.worktrees/<repo>/` leicht auffindbar
- **KANN [MAY]** stattdessen Worktrees als Geschwister des primären Checkouts in der Form `<repo>-<short-slug>/` benennen (zum Beispiel das primäre Checkout `~/repos/github/claude-shared/` plus den Worktree `~/repos/github/claude-shared-mermaid/`), wenn ein Mitwirkender Pro-Repository-Lokalität gegenüber einer einzigen zentralisierten Wurzel bevorzugt; das Mischen beider Layouts auf einer Maschine ist erlaubt, **SOLLTE [SHOULD]** aber pro Repository vermieden werden
- **DARF NICHT [MUST NOT]** einen Worktree-Pfad innerhalb des Working Trees eines anderen Repositories, innerhalb von `node_modules/`, innerhalb von `.venv/`, innerhalb von `.claude/` (einem Claude-Code-Plugin-Verzeichnis, das Plugin-Management- und Reload-Operationen als Ganzes umschreiben können; das historische Muster `.claude/worktrees/<slug>/` ist die konkrete Drift, die diese Klausel verbietet), innerhalb von `.git/` (der administrativen Git-Datenbank) oder innerhalb eines anderen Verzeichnisses ablegen, das ein Tool als Ganzes löschen oder umschreiben könnte
- **DARF NICHT [MUST NOT]** einen `.gitignore`-Eintrag hinzufügen, dessen Wirkung darin besteht, einen spec-verletzenden Worktree-Pfad vor `git status` zu verbergen (zum Beispiel `.claude/worktrees/` oder ein nacktes `worktrees/`); nested-Worktree-Drift **MUSS [MUST]** in `git status` sichtbar bleiben, damit eine mitwirkende oder reviewende Person sie beim ersten Auftreten bemerkt, statt dass sie sich stillschweigend ansammelt

### Branch-zu-Worktree-Zuordnung
- **MUSS [MUST]** genau einen Branch pro Worktree auschecken; ein Worktree **DARF NICHT [MUST NOT]** in einem Detached-HEAD-Zustand für laufende Feature-Arbeit verbleiben (Detached HEAD ist nur für kurzlebige Inspektionsaufgaben akzeptabel, etwa `git worktree add --detach` für ein Bisect)
- **MUSS [MUST]** sicherstellen, dass kein Branch gleichzeitig an zwei Stellen ausgecheckt ist; das primäre Checkout und beliebige Worktrees zusammen **MÜSSEN [MUST]** jeden Branch höchstens einmal präsentieren (das ist eine Eigenschaft, die `git` selbst erzwingt — die Spec wiederholt sie, weil Verstöße einen Prozessfehler signalisieren, keinen Tooling-Fehler)
- **SOLLTE [SHOULD]** das primäre Checkout auf `develop` halten, solange parallele Feature-Arbeit aktiv ist, damit das primäre Checkout für Integrationsaufgaben (Rebases, Konfliktauflösung, Release-Inspektion) verfügbar bleibt, ohne einen Worktree-Abbau zu erzwingen
- **KANN [MAY]** einen Feature-Branch im primären Checkout belassen, wenn nur ein Feature in Bearbeitung ist; sobald ein zweites Feature beginnt, **SOLLTE [SHOULD]** dieses Feature in einen Worktree wandern, statt den bestehenden Branch zu verdrängen

### Lebenszyklus: Anlegen
- **MUSS [MUST]** neue Worktrees mit `git worktree add -b <branch> <path> <base-ref>` anlegen, sodass der Branch als Teil des Worktree-Befehls erzeugt wird und die Basis-Ref explizit ist
- **SOLLTE [SHOULD]** `origin/develop` (nach `git fetch origin develop`) als Basis-Ref verwenden statt des lokalen `develop`, damit der Worktree von der Remote-Spitze startet und der lokale `develop` des primären Checkouts für den Startpunkt des Worktree irrelevant ist
- **MUSS [MUST]** die Branch-Präfix-Regeln aus `spec/project/branching-model/` befolgen (`feat/`, `fix/`, `chore/`, `docs/`, `exp/`); der Pfad-Slug des Worktree **KANN [MAY]** das Präfix der Kürze halber weglassen, der Branch selbst **DARF NICHT [MUST NOT]**

### Lebenszyklus: Stilllegen
- **MUSS [MUST]** einen Worktree mit `git worktree remove <path>` entfernen, sobald sein Pull Request gemergt oder verworfen wurde; das Verzeichnis mit `rm -rf` zu löschen ist verboten, weil es den Worktree in `.git/worktrees/` registriert lässt und „missing"-Einträge in `git worktree list` erzeugt
- **MUSS [MUST]** den lokalen Branch (`git branch -d <branch>` oder `-D`, falls der Branch per Squash gemergt wurde) nach dem Entfernen des Worktree löschen, damit sich keine veralteten lokalen Branches ansammeln
- **SOLLTE [SHOULD]** regelmäßig `git worktree prune` ausführen (oder nach einer erzwungenen Entfernung), um administrative Einträge für Worktrees zu beseitigen, deren Verzeichnisse verschwunden sind
- **DARF NICHT [MUST NOT]** das primäre Checkout per `git worktree remove` stilllegen; das primäre Checkout ist die Wurzel der verlinkten Worktrees, kein entfernbarer Worktree

### Harness-initiierte und Agent-initiierte Worktrees
Eine Claude-Code-Session kann einen Worktree programmatisch erzeugen — am prominentesten über die Harness-Option `Agent({isolation: "worktree"})`, aber auch über jeden zukünftigen Skill oder Agent, der `git worktree add` umhüllt. Diese programmatischen Worktrees unterliegen denselben Regeln wie von Mitwirkenden angelegte Worktrees, mit den folgenden Ergänzungen, die die historische Drift schließen, in der die Harness auf `<primary-checkout>/.claude/worktrees/<slug>/` defaulted hat:

- **MUSS [MUST]** jede Regel aus §Pfad-Layout ausnahmslos auf harness-initiierte und agent-initiierte Worktrees anwenden; die MUSS-NICHT-Regeln aus §Pfad-Layout (einschließlich der expliziten `.claude/`-Klausel und der `.gitignore`-Tarnungs-Klausel) binden die Harness und jeden Agent identisch wie eine menschliche mitwirkende Person
- **DARF NICHT [MUST NOT]** zulassen, dass eine Harness, ein Skill oder ein Agent einen Worktree an einem Pfad materialisiert, der §Pfad-Layout verletzt; zeigt der eingebaute Default der Harness auf einen solchen Pfad (zum Beispiel `<primary-checkout>/.claude/worktrees/agent-<hash>/`), **MUSS [MUST]** die mitwirkende Person den Default überschreiben — indem sie die dokumentierte Worktree-Root-Umgebungsvariable (etwa `CLAUDE_AGENT_WORKTREE_ROOT`) oder den äquivalenten Claude-Code-Settings-Hook auf eine spec-konforme Wurzel setzt, bevor die erste Agent-Invokation mit `isolation: "worktree"` startet
- **SOLLTE [SHOULD]** die Harness-/Agent-Worktree-Wurzel auf `~/repos/.worktrees/<repo>/agents/<slug>/` zeigen lassen, damit automatisch erzeugte Worktrees räumlich von den durch Mitwirkende erzeugten Worktrees unter `~/repos/.worktrees/<repo>/<slug>/` trennbar bleiben und Orphan-Inventare mit einem einzigen `ls` lesbar sind
- **MUSS [MUST]** harness-/agent-initiierte Worktrees am Ende der Agent-Aufgabe automatisch stilllegen, sofern keine zu bewahrenden Änderungen vorliegen (der dokumentierte Harness-Default: „the worktree is automatically cleaned up if the agent makes no changes"); Mitwirkende **DÜRFEN NICHT [MUST NOT]** dieses automatische Cleanup deaktivieren
- **MUSS [MUST]** einen harness-/agent-initiierten Worktree manuell per `git worktree remove <path>` stilllegen, sobald seine Änderungen gemergt oder gemäß §Uncommittete Änderungen zwischen Worktrees übertragen wurden; `rm -rf` ist aus demselben Grund verboten wie unter §Lebenszyklus: Stilllegen

### Uncommittete Änderungen zwischen Worktrees
- **DARF NICHT [MUST NOT]** uncommittete Änderungen per Filesystem zwischen Worktrees kopieren (`cp`, `rsync`, „Speichern unter" im Editor); der Working Tree jedes Worktree ist unabhängig, und ein Filesystem-Copy umgeht den git-Index und erzeugt stillschweigend abweichenden Zustand
- **MUSS [MUST]** uncommittete Arbeit über git zwischen Worktrees übertragen: `git stash push` im Quell-Worktree, dann `git stash apply` (oder `pop`) im Ziel-Worktree, oder über einen temporären Commit, der auf eine geteilte Remote-Ref gepusht wird
- **SOLLTE [SHOULD]** einen temporären Commit gegenüber `git stash` bevorzugen, wenn die Arbeit eine längere Verzögerung überstehen muss, damit die Änderung über ein Commit-Objekt dauerhaft auf der Platte liegt und nicht nur im Stash-Reflog

### Claude-Code-Session-Scoping
- **SOLLTE [SHOULD]** eine Claude-Code-Session pro Worktree starten, gestartet aus dem Wurzelverzeichnis des Worktree (`cd <worktree>; claude`), damit die `CLAUDE.md`-Hierarchieauflösung, der Auto-Memory-Projekt-Namespace und die cwd-Defaults alle an den Worktree gebunden sind
- **KANN [MAY]** eine einzelne Session worktree-übergreifend weiterverwenden, indem absolute Pfade an dateilesende Tools übergeben werden und Shell-Befehle mit `cd <worktree> && …` präfixiert werden; dies wird unterstützt, **SOLLTE NICHT [SHOULD NOT]** der Default sein, weil der Harness den Shell-`cwd` zwischen Bash-Aufrufen zurücksetzt und die `CLAUDE.md`-Auflösung an das ursprüngliche Startverzeichnis der Session gebunden bleibt
- **DARF NICHT [MUST NOT]** eine Datei über eine Claude-Code-Session bearbeiten, deren Startverzeichnis ein anderer Worktree ist, ohne den absoluten Pfad zu verwenden, weil relativ-pfad-basiertes Tooling sonst auf den falschen Working Tree auflöst
- **DARF NICHT [MUST NOT]** `task plugin:reload` (oder einen äquivalenten Plugin-Entwicklungsbefehl von `claude-shared`) gleichzeitig in zwei Sessions ausführen, die dieselbe Plugin-Quellwurzel adressieren; jede Claude-Code-Session lädt ihr eigenes Plugin-Image, aber zwei Sessions, die dieselbe Quellwurzel parallel reloaden, erzeugen Races bei Datei-Watchern und Reload-Semantik

### Untracked-Konfiguration und lokaler Zustand
- **MUSS [MUST]** untracked, maschinenlokale Konfigurationsdateien (`.env`, `.claude/settings.local.json`, IDE-Workspace-Dateien, Build-Caches, `node_modules/`, `.venv/`) als worktree-lokal behandeln; jeder Worktree pflegt seine eigene Kopie
- **DARF NICHT [MUST NOT]** maschinenlokale Konfiguration aus einem Worktree zurück auf das primäre Checkout oder einen anderen Worktree symlinken; Symlinks zwischen Worktrees erzeugen verdeckte Kopplung, die genau die Isolationsgarantie bricht, derentwegen diese Spec existiert
- **SOLLTE [SHOULD]** sprachspezifische Umgebungen (`uv sync`, `npm install`, `task setup`) bei der ersten Nutzung innerhalb jedes Worktree neu aufbauen, statt das `.venv/` oder `node_modules/` des primären Checkouts wiederzuverwenden

### Zusammenspiel mit anderen Portfolio-Specs
- **MUSS [MUST]** weiterhin `spec/project/pull-request-workflow/` für die PR-Erstellung aus einem Worktree befolgen; der Branch des Worktree wird gepusht und der PR identisch zu einem Branch aus dem primären Checkout geöffnet
- **MUSS [MUST]** die Regel aus `spec/project/branching-model/` einhalten, dass `main` nur Präsentationszwecken dient; ein Worktree **DARF NICHT [MUST NOT]** für Feature-Arbeit gegen `main` angelegt werden
- **MUSS [MUST]** `spec/project/quality-gate/` innerhalb jedes Worktree anwenden, bevor ein PR geöffnet oder als ready markiert wird, weil der Worktree einen eigenen Working Tree hat und ein grünes Gate in einem anderen Worktree kein Beleg für diesen ist

## Acceptance Criteria
- [ ] `git worktree list` zeigt das primäre Checkout plus einen Eintrag pro aktivem Feature-Branch und keine Einträge mit `prunable`-Markierung
- [ ] Kein Worktree-Pfad ist unter dem Verzeichnis des primären Checkouts verschachtelt
- [ ] Kein Branch erscheint in mehr als einem Eintrag von `git worktree list`
- [ ] Wenn zwei oder mehr Features in Bearbeitung sind, sitzt das primäre Checkout auf `develop`
- [ ] Nach dem Merge eines PR erwähnt weder `git worktree list` noch `git branch --list` den stillgelegten Branch
- [ ] Kein Worktree enthält einen Symlink, der auf einen Pfad innerhalb eines anderen Worktree oder des primären Checkouts auflöst (geteilte administrative `.git`-Verlinkungen ausgenommen, die `git worktree` selbst verwaltet)
- [ ] Claude-Code-Sessions, die gegen einen Worktree geöffnet werden, lösen die `CLAUDE.md` des Worktree selbst auf (überprüfbar durch Inspektion der geladenen Projekt-Anweisungen der Session)
- [ ] Jeder Worktree trägt sein eigenes `.venv/`, `node_modules/` oder eine andere ökosystem-lokale Umgebung, sofern eine zur Ausführung des Project-Quality-Gates benötigt wird
- [ ] Kein aktiver Feature-Worktree (einer, dessen registrierter Branch mit `feat/`, `fix/`, `chore/`, `docs/` oder `exp/` beginnt) befindet sich im Detached-HEAD-Zustand, wie `git worktree list --porcelain` listet
- [ ] Kein registrierter Worktree-Branch ist `main`, wie `git worktree list --porcelain` listet
- [ ] Jeder PR, der aus einem Worktree-Branch geöffnet wird, zeigt einen grünen Project-Quality-Gate-Check auf der eigenen Branch-Spitze (überprüfbar im PR-Checks-Tab, nicht von einem anderen Worktree geerbt)
- [ ] Das primäre Checkout ist weiterhin als Root-Eintrag in `git worktree list` gelistet (sein Pfad entspricht dem primären Repository-Verzeichnis und trägt keine `bare`-Markierung), sodass die `MUST NOT`-Regel aus §Lebenszyklus: Stilllegen gegen das Entfernen des primären Checkouts nicht verletzt wurde
- [ ] Weder die `.gitignore` im Wurzelverzeichnis noch eine verschachtelte `.gitignore` enthält einen Eintrag, dessen Wirkung darin besteht, ein Worktree-tragendes Verzeichnis vor `git status` zu unterdrücken (konkret: keine Zeile, die `.claude/worktrees/`, `worktrees/` oder einen äquivalenten Pfad matcht, der die historische Nested-Worktree-Drift maskieren würde)
- [ ] Für jeden Eintrag in `git worktree list --porcelain` liegt der registrierte `worktree`-Pfad außerhalb des Verzeichnisbaums des primären Checkouts und außerhalb des Working Trees eines beliebigen anderen Repositories auf derselben Maschine (überprüfbar mit einem einmaligen `git worktree list --porcelain | awk '/^worktree /{print $2}'` plus einem Pfad-Präfix-Check gegen das primäre Repository-Verzeichnis)

Hinweise zur Abdeckung: Die Durchsetzung der Anforderung „MUSS `spec/project/pull-request-workflow/` befolgen" aus §Zusammenspiel mit anderen Portfolio-Specs ist an die Acceptance Criteria jener Spec delegiert und wird hier bewusst nicht doppelt geführt. Die MUST-Regel „Worktree mit `git worktree remove` entfernen" wird autoritativ von AC5 geprüft (nach dem Merge erwähnt weder `git worktree list` noch `git branch --list` den Branch); die `prunable`-Klausel in AC1 ist ein zusätzlicher Hygiene-Check, der zugleich die SHOULD-Regel `git worktree prune` adressiert. Die MUST-Regel aus §Lebenszyklus: Anlegen, neue Worktrees mit `git worktree add -b <branch> <path> <base-ref>` und expliziter Basis-Ref zu erzeugen, ist eine Erzeugungszeit-Konvention ohne stabiles post-hoc beobachtbares Merkmal; ihre Durchsetzung erfolgt durch die Praxis der Mitwirkenden, nicht durch ein mechanisches AC. Die MUST-Regeln aus §Uncommittete Änderungen zwischen Worktrees (kein Filesystem-Copy uncommitteter Änderungen; Transfer ausschließlich über `git stash` oder einen temporären Commit) sind ebenfalls Verhaltenskonventionen der Mitwirkenden, analog zum Verbot des doppelten `task plugin:reload` aus §Claude-Code-Session-Scoping; ein stabil post-hoc beobachtbares AC wird nicht bereitgestellt. Die `MUST NOT`-Klauseln aus §Pfad-Layout gegen Verschachtelung unter `.claude/` und gegen `.gitignore`-Tarnung sind durch die zwei neuen ACs abgedeckt (der `.gitignore`-Inhalts-Check und der `git worktree list --porcelain`-Pfad-Präfix-Check); die MUSS-Regeln aus §Harness-initiierte und Agent-initiierte Worktrees teilen sich diese Abdeckung für die Pfad-Layout-Hälfte, während die Auto-Cleanup-MUSS-Regel eine Harness-Default-Konvention ohne stabiles post-hoc beobachtbares Merkmal ist (die Abwesenheit eines stale Worktree-Verzeichnisses nach einem Agent-Lauf ist eine transiente Eigenschaft, keine Eigenschaft der zu auditierenden Working Copy).

## Open Questions
- Sollte es für Repositories, in denen das primäre Checkout historisch einen lang laufenden Feature-Branch trug (statt `develop`), einen dokumentierten Migrationspfad geben, der das Feature in einen Worktree verschiebt und das primäre Checkout auf `develop` zurücksetzt?
- Gibt es eine portfolioweite Konvention für die maximale Anzahl gleichzeitiger Worktrees pro Repository, bevor der Review-Aufwand den Parallelitätsnutzen überwiegt, oder bleibt das der Einschätzung der Mitwirkenden überlassen?
- Sollten die Reife-Gates aus `spec/project/spec-readiness/` und die Aktualitäts-Gates aus `spec/project/docs-freshness/` diese Spec referenzieren, wenn sie von „der Working Copy unter Audit" sprechen, um zu disambiguieren, welcher Working Tree auf einer Multi-Worktree-Maschine gemeint ist?
