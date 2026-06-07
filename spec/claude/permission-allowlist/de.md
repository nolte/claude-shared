# Pflege der Claude-Code-Permission-Allowlist

Status: draft

## Kontext
Claude Code (CLI, Plugin und Agent-SDK-Läufe) fragt den/die Nutzer:in bei jedem Shell- oder MCP-Tool-Aufruf um Bestätigung, der weder vom Harness automatisch erlaubt noch in der Allowlist des aktuellen Projekts gelistet ist. Ohne eine kuratierte, committet-verbindliche Allowlist wird in der täglichen Arbeit immer wieder dieselbe Handvoll read-only `git` / `gh` / `task`-Aufrufe manuell bestätigt, was Aufmerksamkeit abnutzt und dazu erzieht, Bestätigungsdialoge reflexhaft zu akzeptieren. Jedes Repository im Portfolio liefert daher eine versioniert-committete `.claude/settings.json` mit einer expliziten `permissions.allow`-Liste, die die kleine, gut verstandene Menge an read-only-Befehlen abdeckt, deren Bestätigungsdialoge keinen Sicherheitsgewinn bringen. Die Liste ist ein lebendes Artefakt und braucht einen definierten Pflegeprozess, damit sie weder erstarrt (fehlende Befehle, die inzwischen üblich geworden sind) noch stillschweigend ausufert (übernommene gefährliche Wildcards aus entwicklerlokalen Configs).

## Ziele
- Jedes Repository im Portfolio liefert eine committete `.claude/settings.json`, deren `permissions.allow`-Liste die in diesem Repository nachweislich häufigen read-only-Befehle abdeckt
- Die Allowlist wird bewusst und an dokumentierten Auslösern aktualisiert, nicht durch ad-hoc Einträge, die ungeprüft einziehen
- Auswahlkriterien, verbotene Pattern-Klassen und das Zusammenspiel mit den Skills `fewer-permission-prompts` / `update-config` sind schriftlich festgehalten, damit Mensch und KI-Agenten einig sind, was in die Datei gehört
- Einträge dürfen niemals Privilegien ausweiten oder eine Spec-Regel umgehen — insbesondere darf kein Pattern auf der committeten Liste das Automerge-Trigger-Protokoll oder die Anforderungen an das CI-Gate nach `develop` aus der pull-request-workflow-Spec unterlaufen

## Nicht-Ziele
- Benutzer-globale Konfiguration unter `~/.claude/settings.json` — gehört zur/zum einzelnen Entwickler:in und ist nicht im Scope
- Entwicklerlokale Overrides in `.claude/settings.local.json` — sind absichtlich unreguliert, spiegeln die persönliche Risikobereitschaft und sind nicht im Scope
- Hooks, Umgebungsvariablen oder beliebige andere `.claude/settings.json`-Felder jenseits von `permissions.allow` — die deckt der Skill `update-config` und ggf. spätere Specs ab, nicht dieser hier
- Portfolio-weite Verteilung einer gemeinsamen Basis-Allowlist (etwa via eines `_extends`-ähnlichen Mechanismus wie bei `.github/settings.yml`). Default (Revisit): Jedes Repository besitzt seine eigene `.claude/settings.json`-Allowlist; es gibt keine zentrale oder `_extends`-artige Basis-Liste, weil der Claude-Code-Harness keinen Vererbungsmechanismus hat. Erst dann revisiten, wenn ein `portfolio-audit`-Lauf den Allowlist-Block unter `portfolio-management` §Cross-repository copy-paste smell markiert (derselbe Basis-Block über drei oder mehr Portfolio-Member-Repos), woraufhin ein Generator- oder Sync-Skill—nicht eine `_extends`-Config-Änderung—die Kandidatenlösung wird.

## Anforderungen

### Scope und Ort
- **MUSS [MUST]** die committet-verbindliche Allowlist in `.claude/settings.json` am Repository-Root halten; `.claude/settings.local.json` ist explizit Nicht-Scope (bleibt Entwickler-eigen und wird nicht committet)
- **MUSS [MUST]** `.claude/settings.json` in Git tracken; die Datei **DARF NICHT [MUST NOT]** in `.gitignore` auftauchen
- **DARF NICHT [MUST NOT]** nicht-read-only-Patterns, Interpreter-Wildcards oder Task-Runner-Wildcards (`Bash(task *)`, `Bash(npm run *)`, `Bash(bun run *)` und Entsprechungen) in `.claude/settings.json` aufnehmen; exakte Task-Targets wie `Bash(task lint)` sind zulässig

### Auswahlkriterien für neue Einträge
- **MUSS [MUST]** jedes neue Pattern alle drei folgenden Bedingungen erfüllen:
  1. in einer belastbaren Stichprobe als häufig auftretend dokumentiert — mehrere jüngere Sessions, mehrere Repositories oder eine nachvollziehbare Spec-Anforderung wie pull-request-workflow §Vor-dem-Push-Prüfung
  2. read-only im Sinne von: ändert keine Remote-Zustände, keine Secrets und keine gemeinsam genutzte Infrastruktur; lokale Filesystem-Writes sind nur als Seiteneffekt einer read-only-Operation zulässig (zum Beispiel `git fetch`, das lokale Refs aktualisiert, oder `task docs`, das `mkdocs build` nach `site/` schreibt) und **MÜSSEN [MUST]** im Zweifel explizit begründet werden
  3. wird noch nicht durch die Claude-Code-Auto-Allow-Liste abgedeckt (siehe `fewer-permission-prompts`-Skill, Schritt 4); redundante Einträge werden weggelassen
- **SOLLTE [SHOULD]** die engstmögliche Pattern-Form gewählt werden: exakte Form (`Bash(git fetch)`) wenn eine Invocation dominiert, Präfix-Form (`Bash(git fetch *)`) nur wenn Flag-Varianz real beobachtet wurde
- **DARF [MAY]** beide Formen (exakt und Präfix) parallel gelistet werden, wenn beide Varianten in der beobachteten Nutzung tatsächlich vorkommen

### Turnus und Auslöser der Pflege
- **MUSS [MUST]** die Allowlist spätestens nach jeder größeren Refaktorierung des Claude-Workflows im Projekt oder bei Einführung neuer Skills, neuer Taskfile-Targets oder neuer Automatisierungsbefehle reviewed werden — anlassbezogen, nicht kalendergetrieben
- **SOLLTE [SHOULD]** mindestens einmal pro Quartal (oder beim nächsten größeren Spec-Update, was früher eintritt) per `fewer-permission-prompts`-Skill einen Drift-Check fahren, um neu häufig gewordene read-only-Patterns aufzunehmen und obsolete Einträge zu streichen
- **MUSS [MUST]** bei Streichung eines Patterns den Grund in der Commit-Message nennen (zum Beispiel „in die Claude-Code-Auto-Allow-Liste hochgewandert", „Befehl wird nicht mehr benutzt")

### Einbindung in den Authoring-Flow
- **MUSS [MUST]** jede Änderung an `.claude/settings.json` über den regulären pull-request-workflow-Prozess laufen — kein Direct-Commit auf `develop`, kein Bypass via `settings.local.json`
- **SOLLTE [SHOULD]** einen Commit mit Conventional-Commits-Type `chore` oder `docs` verwenden, passend zum Charakter der Änderung: `chore` bei reiner Allowlist-Pflege, `docs` wenn die Begleit-Spec parallel berührt wird
- **MUSS [MUST]** vor jedem Push `task lint` lokal ausführen, wie es die pull-request-workflow-Spec §Vor-dem-Push-Prüfung vorgibt

### Verhältnis zu `settings.local.json` und `~/.claude/settings.json`
- **DARF [MAY]** entwicklerlokal in `.claude/settings.local.json` oder im Home-Verzeichnis breitere Patterns geführt werden; das Risiko trägt in diesem Fall die/der Entwickler:in selbst, und diese Dateien sind ausdrücklich Nicht-Scope dieser Spec
- **DARF NICHT [MUST NOT]** ein breites Pattern aus `settings.local.json` oder `~/.claude/settings.json` in die committete `.claude/settings.json` übernommen werden, ohne es gegen die obigen Auswahlkriterien erneut zu prüfen — insbesondere mutationsfähige Wildcards wie `Bash(git *)`, `Bash(gh api *)` oder `Bash(gh pr *)` bleiben aus der committeten Datei draußen
- **DARF NICHT [MUST NOT]** diese committete Datei als Freischalt-Punkt für autonome oder Hintergrund-Agenten behandelt werden: ein nicht-interaktiver Agent, der mutationsfähige Kommandos (`git commit` / `git push`, `gh pr create`, einen Task-Runner) braucht, um innerhalb eines Worktree zu agieren, wird über die Session-`/permissions`-Freigabe oder `.claude/settings.local.json` autorisiert — gemäß `spec/project/parallel-working-copies/` §Harness-initiierte und Agent-initiierte Worktrees, niemals durch Aufnahme dieser Patterns hier

### Governance
- **MUSS [MUST]** jede Diskrepanz zwischen dieser Spec und `.claude/settings.json` durch eine Änderung an der committeten Datei aufgelöst werden — nicht durch stille Anpassung der Spec
- **SOLLTE [SHOULD]** der `fewer-permission-prompts`-Skill als Werkzeug referenziert werden, das Kandidaten *vorschlägt*; die Entscheidung, einen Kandidaten anzunehmen, einzuengen oder abzulehnen, trifft die/der Autor:in nach den obigen Kriterien

## Akzeptanzkriterien
- [ ] `.claude/settings.json` existiert am Repository-Root und enthält mindestens ein `permissions.allow`-Array
- [ ] Kein Eintrag in `.claude/settings.json` fällt in eine der verbotenen Pattern-Klassen aus §Scope und Ort (Interpreter-Wildcards, Task-Runner-Wildcards, mutationsfähige gh/git-Wildcards)
- [ ] `.claude/settings.local.json` ist entweder gar nicht committet oder steht explizit in `.gitignore`
- [ ] Für die letzten 5 nach `develop` gemergten PRs, die `.claude/settings.json` berühren, hat der PR-Body jede Änderung begründet (neue Kandidaten, gestrichene Einträge mit Grund) — Stichprobe via `gh pr list --state merged --base develop --search '.claude/settings.json' --json number,title,body`
- [ ] Keine Spec-interne MUSS-Regel wird durch einen Eintrag in `.claude/settings.json` unterlaufen — insbesondere erlaubt kein Eintrag `gh pr merge *` oder eine Entsprechung, die das Automerge-Trigger-Protokoll der pull-request-workflow-Spec umgehen würde

## Offene Fragen

_Alle zuvor zurückgestellten offenen Fragen wurden am 2026-06-06 entschieden: jeder vorläufige Default ist nun die geltende Regel. Siehe `.audits/decisions/2026-06-06-settle-open-questions.md` für die Einzelentscheidungen und Begründungen._
