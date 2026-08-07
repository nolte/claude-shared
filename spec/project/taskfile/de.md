# Taskfile-Konventionen

Status: draft
Portfolio-Scope: portfolio

## Kontext
Jedes Repository im Portfolio steuert seine lokale Automatisierung über [Task](https://taskfile.dev) — eine `Taskfile.yml` im Repository-Root ist der einzige, erkennbare Einstiegspunkt für das Installieren von Abhängigkeiten, Linting, Tests, den Doku-Build und das Schneiden von Releases. Das Verhalten rund um diese Datei ist in der Praxis konsistent gewachsen (ein `:`-namespaced Target-Baum, Argument-Durchreichung, eine geteilte Sammlung wiederverwendbarer Taskfiles aus [`nolte/taskfiles`](https://github.com/nolte/taskfiles) und CI, die genau dieselben Targets aufruft, die eine beitragende Person lokal ausführt), aber die Regeln dafür sind verstreut: `project-structure` pinnt die Existenz der Datei und den kanonischen Namen `task check`, `quality-gate` besitzt, woraus sich `task check` zusammensetzt, `cookiecutter-template-authoring` listet `task install/lint/test/docs/release`, `permission-allowlist` verbietet `Bash(task *)`-Wildcards, und `parallel-working-copies` definiert die `worktree:*`-Helfer. Keine einzige Spec benennt die Taskfile-*Mechanik*, die das gesamte Portfolio teilen soll, sodass ein neues Repository die Konvention aus fünf Stellen rückentwickeln muss.

Diese Spec konsolidiert die portfolio-weite Taskfile-*Mechanik* an einem Ort: das kanonische Target-Vokabular, das Namespacing-Schema, die Argument-Durchreichung, die Lokal↔CI-Paritätsregel und — zentral — die Nutzung der geteilten, wiederverwendbaren Taskfiles aus [`nolte/taskfiles`](https://github.com/nolte/taskfiles). Sie benennt bewusst **nicht** neu, was ein einzelnes Target *tut*; die Semantik jeder Capability bleibt bei der Spec, die sie bereits besitzt. Das Ergebnis: Die Form des Taskfiles ist überall gleich, während jede Capability eine einzige Quelle der Wahrheit behält.

## Ziele
- Eine beitragende Person findet in einem beliebigen Portfolio-Repository dieselben kanonischen Target-Namen (`task install`, `task lint`, `task test`, `task check`, `task docs`, `task release`) für dieselben Aufgaben, sodass Muskelgedächtnis und dokumentierte Aufrufe zwischen Repositories übertragbar sind
- Portfolio-gemeinsame Automatisierung (MkDocs, pre-commit und ähnliche repository-übergreifende Anliegen) wird aus der geteilten Sammlung [`nolte/taskfiles`](https://github.com/nolte/taskfiles) konsumiert statt pro Repository neu implementiert, sodass eine Änderung an gemeinsamem Verhalten einmal landet und sich verbreitet
- Die Gruppierungs-Konvention (der `:`-namespaced Target-Baum) und die Argument-Durchreichung sind einheitlich, sodass sich `task --list` über das Portfolio hinweg gleich liest
- CI ruft Lint, Test und Docs über die identischen Taskfile-Targets auf, die eine beitragende Person lokal ausführt, sodass lokales und CI-Verhalten nicht auseinanderdriften können
- Diese Spec besitzt ausschließlich die Taskfile-*Mechanik*; die *Semantik* jedes Targets bleibt bei der Capability-Spec, die sie besitzt, sodass nichts dupliziert wird und es keine zweite, synchron zu haltende Quelle der Wahrheit gibt

## Nicht-Ziele
- Die Definition dessen, woraus sich `task check` zusammensetzt, oder der Form seiner Ausgabe — das wird durch `spec/project/quality-gate/` geregelt; diese Spec pinnt nur den kanonischen Namen
- Die Forderung nach der Existenz des Taskfiles, der Verdrahtung des projektlokalen virtuellen Environments oder des `requirements*.txt`-Installationsmusters — diese werden durch `spec/project/project-structure/` geregelt; diese Spec setzt die Existenz der Datei voraus und regelt ihre Konventionen
- Die Wahl des sprachspezifischen Werkzeugs, das ein Target ausführt (ruff vs. flake8, mkdocs vs. anderer Generator) — eine Entscheidung pro Repository
- Den Ersatz von pre-commit, des Quality-Gates oder von CI — Task ist der Einstiegspunkt, der sie aufruft, kein Ersatz für sie
- Die Deklaration der Inhalte der geteilten `nolte/taskfiles`-Sammlung selbst — jenes Repository ist seine eigene Quelle der Wahrheit; diese Spec regelt nur, wie Portfolio-Repositories es *konsumieren*

## Anforderungen

### Kanonisches Target-Vokabular
- Ein Repository **MUSS** jede Capability, die es besitzt, unter dem portfolio-kanonischen Target-Namen bereitstellen statt unter einem Synonym: `task setup` (einmaliges Onboarding—Hooks installieren und das projektlokale Environment bootstrappen), `task install` (Abhängigkeiten in diesem Environment installieren oder aktualisieren), `task lint` (Linter), `task test` (Tests oder, für Prompt-only-Repositories, die Frontmatter-/Contract-Validierung), `task typecheck` (Typprüfungen, wo die Sprache sie hat), `task check` (das aggregierte Quality-Gate), `task docs` (Doku-Build) und `task release` (Release-Schnitt, wo das Repository Artefakte veröffentlicht)
- Eine Capability, die das Repository nicht besitzt (zum Beispiel `task release` in einer Bibliothek, die keine Release-Artefakte ausliefert), ist schlicht abwesend; die Regel pinnt den *Namen*, wenn die Capability existiert, nicht die Existenz jeder Capability
- Diese Spec pinnt ausschließlich die kanonischen *Namen*. Die Zusammensetzung, das Verhalten und die Ausgabe jedes Targets bleiben bei der Spec, die die Capability besitzt — `task check` bei `spec/project/quality-gate/`, der Doku-Build bei `spec/project/mkdocs-structure/` und so weiter. Ein Repository **DARF NICHT** jene Semantik in den Begriffen dieser Spec neu benennen; es **MUSS** der besitzenden Spec folgen

### Namespacing und Auffindbarkeit
- Gruppierte und Sub-Targets **SOLLTEN** den `:`-Separator verwenden, um einen lesbaren Baum zu bilden (zum Beispiel `docs:catalog`, `validate:skills`, `lint:prose`, `worktree:add`), sodass `task --list` zusammengehörige Arbeit gruppiert
- Pro-Unterordner-Varianten eines Gate-Targets **SOLLTEN** demselben Schema folgen (`task lint:backend`, `task test:frontend`); ihre Komposition in das aggregierte Gate wird durch `spec/project/quality-gate/` geregelt
- Das `default`-Target **SOLLTE** die verfügbaren Tasks auflisten (entspricht `task --list`), sodass das Ausführen von `task` ohne Argument selbstdokumentierend ist

### Argument-Durchreichung
- Ein Target, das aufrufer-gelieferte Argumente akzeptiert, **SOLLTE** diese über Tasks `CLI_ARGS` konsumieren, sodass sie nach `--` übergeben werden können (zum Beispiel `task worktree:add -- <branch> [slug]`), wodurch die Argument-Fläche über das Portfolio hinweg einheitlich bleibt

### Geteilte Taskfiles aus nolte/taskfiles
- [`nolte/taskfiles`](https://github.com/nolte/taskfiles) ist die autoritative Sammlung wiederverwendbarer, geteilter Taskfiles des Portfolios. Verhalten, das über Repositories hinweg gemeinsam ist, **SOLLTE** dort leben, nicht pro Repository geforkt werden
- Ein Repository **SOLLTE** portfolio-gemeinsame Automatisierung (zum Beispiel MkDocs- und pre-commit-Targets) konsumieren, indem es die relevanten Taskfiles aus `nolte/taskfiles` einbindet, statt äquivalente Targets lokal neu zu implementieren, sodass eine Änderung an gemeinsamem Verhalten einmal upstream gemacht wird und sich bei der nächsten Include-Auflösung verbreitet
- Wenn ein Repository Taskfiles aus `nolte/taskfiles` einbindet, **MUSS** es die Quell-Location über eine einzige Variable (zum Beispiel `TASK_COLLECTION_BASE`) pinnen, die einen expliziten Ref benennt, sodass jeder Include gegen eine deklarierte, prüfbare Quelle auflöst statt gegen verstreute Inline-URLs
- Dieser Ref **SOLLTE** unveränderlich sein (ein Release-Tag oder ein Commit-SHA) statt ein beweglicher Branch. Ein Remote-Include führt Shell-Kommandos in der CI jedes Konsumenten aus, und die nicht-interaktive Akzeptanz (unten) entfernt genau den Prompt, der eine geänderte Datei sonst sichtbar machen würde — ein beweglicher Ref bedeutet also, dass ein ungeprüfter Upstream-Push beim nächsten Build jedes Konsumenten läuft. Ein Branch-Ref **DARF** bewusst verwendet werden (etwa während Sammlung und Konsument gemeinsam entwickelt werden), wenn das Repository diese Wahl festhält
- Tasks Remote-Taskfile-Auflösung ist ein experimentelles Feature; ein Repository, das Remote-Includes konsumiert, **MUSS** Tasks Experiment-Flag (`TASK_X_REMOTE_TASKFILES=1`) überall dort setzen, wo diese Includes aufgelöst werden, einschließlich der CI-Umgebung, sodass die Auflösung explizit ist statt sich auf einen undeklarierten Default zu verlassen
- Task gated einen Remote-Include zusätzlich hinter einem interaktiven Trust-Prompt. Ein Repository, das Remote-Includes konsumiert, **MUSS** seine Targets deshalb auch nicht-interaktiv aufrufen (`task --yes <target>`), überall dort, wo kein Terminal diesen Prompt beantworten kann — also in jeder CI-Umgebung. Das Experiment-Flag allein lässt den Lauf blockiert zurück, beide Teile gehören zusammen
- Bevor ein Repository ein lokales Target an ein eingebundenes delegiert, **MUSS** es prüfen, dass das eingebundene Target existiert und dass seine Umgebungsannahmen im konsumierenden Repository zutreffen. Themengleichheit mit einer eingebundenen Datei bedeutet kein nutzbares Target: ein Include kann nur eine Teilmenge der erwarteten Tasks bereitstellen oder gegen einen Interpreter auflösen, den der Konsument nicht bereitstellt
- Repository-spezifische Automatisierung, die nicht über das Portfolio geteilt wird, **DARF** ein lokales Target in der eigenen `Taskfile.yml` des Repositorys bleiben; die geteilte Sammlung ist für portfolio-gemeinsames Verhalten, nicht für einmalige, repo-spezifische Arbeit

### Lokal- und CI-Parität
- CI **MUSS** Lint, Test und Docs über dieselben Taskfile-Targets aufrufen, die eine beitragende Person lokal ausführt (zum Beispiel `task --yes lint`, `task --yes test`, `task --yes docs`), statt diese Schritte inline neu zu implementieren, sodass das lokale Gate und das CI-Gate nicht auseinanderdriften können. Das aggregierte `task check` (dessen Zusammensetzung von `spec/project/quality-gate/` geregelt wird) ist der lokale Komfort-Einstiegspunkt; CI **DARF** jede Kategorie als separaten required-Check behalten, während es weiterhin dieselben Pro-Kategorie-Targets aufruft

### Berechtigungen
- Permission-Allowlists **DÜRFEN NICHT** ein `Bash(task *)`-Wildcard gewähren; exakte Targets (zum Beispiel `Bash(task lint)`) werden einzeln gewährt, wie durch `spec/claude/permission-allowlist/` geregelt. Diese Spec benennt nur den *Ort* der Regel neu, nicht ihren Inhalt

## Akzeptanzkriterien
- [ ] `spec/project/taskfile/` existiert mit `en.md` (canonical) und `de.md` (Übersetzung) und ist in `spec/README.md` gelistet
- [ ] Das kanonische Target-Vokabular (`setup`, `install`, `lint`, `test`, `typecheck`, `check`, `docs`, `release`) ist an genau einem Ort definiert — dieser Spec — und die Konventionen für Namespacing, Durchreichung und Lokal↔CI-Parität sind hier benannt
- [ ] `nolte/taskfiles` ist als autoritative Sammlung geteilter Taskfiles benannt, mit einem SOLLTE, portfolio-gemeinsame Automatisierung daraus zu konsumieren, einem MUSS, die Include-Quelle über eine einzige Ref-Variable zu pinnen, einem SOLLTE, dass dieser Ref unveränderlich ist, der `TASK_X_REMOTE_TASKFILES`-Experiment-Flag-Anforderung, der begleitenden `task --yes`-Anforderung zur nicht-interaktiven Akzeptanz und dem MUSS, vor dem Delegieren zu prüfen, dass ein eingebundenes Target existiert und seine Annahmen zutreffen — alles hier festgehalten statt in den konsumierenden Skills
- [ ] Die Spec delegiert statt zu duplizieren: Target-*Semantik* verweist auf `quality-gate`, Datei-Existenz und venv-Verdrahtung auf `project-structure`, `worktree:*`-Helfer auf `parallel-working-copies` und das `task *`-Wildcard-Verbot auf `permission-allowlist`
- [ ] `spec/project/project-structure/`, `spec/project/quality-gate/` und `spec/portfolio/tech-stack/` tragen eine Rück-Referenz auf diese Spec als Eigner der Taskfile-Mechanik
- [ ] Jedes Artefakt, das ein `Taskfile.yml` scaffoldet oder patcht (die Skills `project-structure-apply` und `mkdocs-structure-apply` sowie der Agent `cookiecutter-template-author` über `spec/project/cookiecutter-template-authoring/`), verweist auf diese Spec, gibt die gepinnte `includes:`-Form für Automatisierung aus, die die Sammlung tatsächlich abdeckt, und prüft vor dem Delegieren, ob ein eingebundenes Target existiert und seine Umgebungsannahmen zutreffen, statt das Target lokal zu schreiben
- [ ] Keine Anforderung in dieser Spec benennt die Zusammensetzung oder Ausgabe eines Targets neu, dessen Semantik eine andere Spec besitzt

## Offene Fragen
- Sobald Tasks Remote-Taskfile-Auflösung von experimentell auf stabil reift: Sollte das Konsumieren portfolio-gemeinsamer Automatisierung aus `nolte/taskfiles` von **SOLLTE** auf **MUSS** angehoben und die `TASK_X_REMOTE_TASKFILES`-Flag-Anforderung zurückgezogen werden? Aufgeschoben, bis das Upstream-Feature stabilisiert.

## Quellen

Die Task-Remote-Taskfile-Feature-Reifegrad-Aussage in §„Geteilte Taskfiles aus `nolte/taskfiles`" ist eine Author-Time-externe Aussage, trianguliert gemäß `spec/claude/research-triangulate/` §"Author-Time-Aussagen" (Author-Time-Stufe: mindestens drei unabhängige Quellen, Primary-first geordnet). Abrufdatum für jede Quelle unten: 2026-07-24.

- **Tasks Remote-Taskfile-Auflösung ist ein experimentelles Feature, gated durch `TASK_X_REMOTE_TASKFILES=1`**: Task-Dokumentation, „Remote Taskfiles"-Experiment-Seite, gated durch `TASK_X_REMOTE_TASKFILES` und mit der Standard-Experimental-Feature-Warnung (Primary), `https://taskfile.dev/docs/experiments/remote-taskfiles`; das Upstream-Tracking-Issue `go-task/task#1317`, weiterhin offen mit Experiment-Status „candidate" (Primary), `https://github.com/go-task/task/issues/1317`; Marmelab, „Taskfile: The Modern Alternative to Makefile" (Secondary), `https://marmelab.com/blog/2026/03/12/taskfile-alternative-makefile.html`

Verifiziert 2026-07-24: Das Feature ist weiterhin experimentell (der Status des Tracking-Issues ist von „draft" auf „candidate" fortgeschritten, aber weder stable noch standardmäßig aktiviert), und der Flag-Name `TASK_X_REMOTE_TASKFILES` ist unverändert, sodass die obige Anforderung aktuell bleibt.
