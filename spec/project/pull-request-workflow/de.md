# Pull-Request-Workflow

Status: draft

## Kontext
Pull Requests (PRs, entsprechen GitLab Merge Requests / MRs) sind der einzige Weg, über den Änderungen in den Integrations-Branch `develop` gelangen, wie im Branching-Modell-Spec festgelegt. Zwei wiederkehrende Probleme motivieren diese Spezifikation: (1) PR-Beschreibungen haben uneinheitliche Struktur, was das Review erschwert und die Release-Drafter-Zusammenfassung der `develop`-Aktivitäten verschlechtert, und (2) PRs werden gelegentlich nach `develop` gemergt, bevor die CI grün gemeldet hat, was die „immer grüner develop"-Annahme des Release-Flows untergräbt. Diese Spezifikation definiert, wie PRs erstellt werden und welche Gates sie vor dem Merge in `develop` bestehen müssen. Sie ergänzt — und wiederholt nicht — das Branching-Modell-Spec, das den Ziel-Branch und den Automerge-Workflow festlegt, sowie das Project-Structure-Spec, das die `.github/settings.yml`-Mechanik festlegt.

## Ziele
- Jeder PR nach `develop` folgt einer einzigen, konsistenten Beschreibungsstruktur, sodass Reviewer, Release-Drafter und KI-Agenten immer die gleiche Form sehen
- Kein PR erreicht `develop`, solange nicht jeder erforderliche CI-Check Erfolg gemeldet hat
- Rahmenbedingungen (Branch-Benennung, Ziel-Branch, Titelform) sind vollständig als Code deklariert und über Branch-Protection erzwingbar
- Menschen und KI-Agenten, die PRs gegen diese Repositories erstellen, erzeugen Artefakte, die ohne repo-spezifisches Onboarding demselben Standard entsprechen

## Nicht-Ziele
- Ziel-Branch-Policy und Release-Flow (abgedeckt durch das Branching-Modell-Spec)
- Deklarationsmechanik der Branch-Protection via `.github/settings.yml` (abgedeckt durch das Project-Structure-Spec; diese Spezifikation benennt lediglich, welche Regeln deklariert sein müssen)
- Interna des Automerge-Workflows (abgedeckt durch `nolte/gh-plumbing` reusable-automerge und referenziert im Branching-Modell-Spec)
- Release-Notes- / Changelog-Inhalte (verantwortet durch Release-Drafter)
- Code-Review-Approval-Policy (wer reviewt, wie viele Freigaben) — hier nicht im Umfang

## Anforderungen

### PR-Rahmenbedingungen
- **MUSS [MUST]** `develop` als Basis-Branch adressieren
- **MUSS [MUST]** aus einem Branch stammen, dessen Name mit einem der Präfixe `feat/`, `fix/`, `chore/` oder `docs/` beginnt (wie im Branching-Modell-Spec festgelegt)
- **MUSS [MUST]** einen PR-Titel in Conventional-Commits-Form `<type>(<scope>)?: <summary>` verwenden, wobei `<type>` wortgleich dem Branch-Präfix entspricht (Präfix `feat/` → Type `feat`, `fix/` → `fix`, `chore/` → `chore`, `docs/` → `docs`); eine Übersetzung oder Aliasbildung ist nicht zulässig
- **MUSS [MUST]** einen einzelnen PR auf genau eine logische Änderung begrenzen; unzusammenhängende Änderungen werden in separate PRs aufgeteilt
- **SOLLTE [SHOULD]** mindestens ein verwandtes Issue via `Closes #<n>` oder `Refs #<n>` in der Beschreibung verlinken, wenn ein Tracking-Issue existiert

### Aktualität des Branches
- **MUSS [MUST]** sicherstellen, dass der Feature-Branch vor dem Öffnen des PRs jeden Commit des aktuellen `develop`-Tip enthält, damit der CI-Lauf den Zustand widerspiegelt, der nach dem Merge auf `develop` existieren wird; dies wird erreicht, indem `develop` in den Feature-Branch gemergt oder der Feature-Branch auf `develop` rebased wird
- **MUSS [MUST]** den Feature-Branch erneut mit `develop` synchronisieren, sobald `develop` sich bewegt, während der PR offen ist — und zwar bevor der PR aus dem Draft-Zustand genommen oder Automerge zum Zug gelassen wird; ein PR, dessen Branch hinter `develop` zurückhängt, gilt nicht als merge-bereit
- **MUSS [MUST]** die GitHub-Option „require branches to be up to date before merging" für `develop` in `.github/settings.yml` aktivieren (via `protection.required_status_checks.strict: true`, direkt oder via der `nolte/gh-plumbing`-Commons-Extension), sodass die Plattform diese Vorbedingung zusätzlich zum clientseitigen Workflow erzwingt
- **DARF [MAY]** Rebase oder Merge für die Synchronisation verwenden; die Spec schreibt keine der beiden Varianten vor, aber die gewählte Operation **MUSS [MUST]** dazu führen, dass `develop` vor dem Öffnen oder erneuten Review-Request vollständig im Feature-Branch enthalten ist

### Struktur der PR-Beschreibung
Ein Pull-Request-Template **MUSS [MUST]** unter `.github/pull_request_template.md` existieren und **MUSS [MUST]** die folgenden Abschnitte in genau dieser Reihenfolge und mit genau diesen Überschriften enthalten:

1. **Summary** — ein bis drei Sätze, die *was* der PR ändert und *warum* benennen
2. **Changes** — Bullet-Liste der für Nutzer oder Reviewer relevanten Änderungen
3. **Linked issues** — `Closes #…` / `Refs #…`-Einträge oder der Literaltext `None`
4. **Testing** — wie die Änderung verifiziert wurde (ausgeführte Befehle, manuelle Schritte, Screenshots)
5. **Risk / rollout notes** — Risikoklasse, Migrationen, Feature-Flags oder der Literaltext `None`

- **MUSS [MUST]** jeden erforderlichen Template-Abschnitt im PR-Body erhalten; Abschnitte werden niemals entfernt, auch wenn sie leer wären
- **DARF NICHT [MUST NOT]** Summary, Changes oder Testing leer lassen; Linked issues und Risk / rollout notes **DÜRFEN [MAY]** den Literaltext `None` verwenden
- **DARF [MAY]** repo-spezifische Abschnitte *unterhalb* der fünf erforderlichen Abschnitte hinzufügen; zusätzliche Abschnitte **MÜSSEN [MUST]** nach allen fünf Pflichtabschnitten erscheinen und **DÜRFEN NICHT [MUST NOT]** zwischen ihnen eingefügt werden
- **SOLLTE [SHOULD]** Imperativform in Summary und Changes verwenden (`Add …`, `Fix …`, nicht `Added …`)
- **SOLLTE [SHOULD]** auf die relevante Spec-Datei unter `spec/` verlinken, wenn die Änderung eine Spec umsetzt oder modifiziert

### PR-Lint-Workflow
- **MUSS [MUST]** einen Workflow unter `.github/workflows/` enthalten (z. B. `pr-lint.yml`), der PR-Titel und -Body auf den `pull_request`-Events `opened`, `edited`, `synchronize` und `ready_for_review` lintet
- **MUSS [MUST]** den Job dieses Workflows als erforderlichen Status-Check für `develop` in `.github/settings.yml` registrieren
- **MUSS [MUST]** den Check fehlschlagen lassen, wenn der PR-Titel nicht der Conventional-Commits-Form `<type>(<scope>)?: <summary>` mit `<type>` ∈ {`feat`, `fix`, `chore`, `docs`} entspricht
- **MUSS [MUST]** den Check fehlschlagen lassen, wenn der PR-Body nicht alle fünf erforderlichen Abschnittsüberschriften in der festgelegten Reihenfolge enthält
- **MUSS [MUST]** den Check fehlschlagen lassen, wenn Summary, Changes oder Testing leer ist oder ausschließlich den Literaltext `None` enthält
- **DARF NICHT [MUST NOT]** den Check fehlschlagen lassen, wenn der Body zusätzliche repo-spezifische Abschnitte enthält, die *nach* den fünf Pflichtabschnitten angehängt sind, solange die Pflichtabschnitte selbst vorhanden, in der richtigen Reihenfolge und an den geforderten Stellen nicht leer sind
- **SOLLTE [SHOULD]** den Linter als wiederverwendbaren Workflow unter `nolte/gh-plumbing` umsetzen (zum Beispiel `reusable-pr-lint.yaml`), sodass jedes Repository dieselbe Implementierung erbt statt lokaler Kopien, die auseinanderdriften

### CI-Gate nach `develop`
- **MUSS [MUST]** die vollständige Menge der erforderlichen Status-Checks für `develop` als Code in `.github/settings.yml` deklarieren (direkt oder via der `nolte/gh-plumbing`-Commons-Extension); das GitHub-UI ist **KEIN** akzeptabler Ort, um erforderliche Checks hinzuzufügen oder zu entfernen
- **MUSS [MUST]** verlangen, dass jeder deklarierte Check Erfolg meldet, bevor ein PR nach `develop` gemergt werden kann
- **MUSS [MUST]** den `automerge.yaml`-Workflow so konfigurieren, dass er einen PR nur dann mergt, wenn jeder erforderliche Check Erfolg meldet und der PR freigegeben ist
- **MUSS [MUST]** `enforce_admins: true` für die `develop`-Branch-Protection setzen, damit Admin-Overrides keinen fehlschlagenden erforderlichen Check umgehen können; das CI-Gate hat keinen Ausnahmepfad, und eine Waiver-Regelung ist nicht zulässig — wenn ein erforderlicher Check dauerhaft defekt ist, ist die korrekte Abhilfe ein PR gegen `.github/settings.yml` (der selbst das Gate passiert), der den Check entfernt oder ersetzt, keine einmalige Umgehung
- **SOLLTE [SHOULD]** den Merge blockieren, solange ein Review ausdrücklich Änderungen anfordert, auch nachdem die CI grün geworden ist

### Merge-Strategie
- **MUSS [MUST]** PRs mittels Squash-Merge nach `develop` mergen; der resultierende Commit auf `develop` ist ein einziger Commit pro PR, der den Conventional-Commits-konformen PR-Titel als Nachricht trägt
- **MUSS [MUST]** Squash-Merge als einzige aktivierte Merge-Option in `.github/settings.yml` für Repositories, die dieser Spec folgen, deklarieren: `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false`
- **SOLLTE [SHOULD]** den PR-Titel als Default-Squash-Commit-Nachricht beibehalten, sodass die `develop`-Historie ein linearer Strom von Conventional-Commits-Nachrichten bleibt, den Release-Drafter direkt verarbeiten kann

### Draft- und Work-in-Progress-PRs
- **SOLLTE [SHOULD]** PRs während laufender Arbeit als Draft öffnen und erst dann als bereit für Review markieren, wenn die CI voraussichtlich grün wird und die Beschreibung vollständig ist
- **DARF NICHT [MUST NOT]** einen PR als bereit für Review markieren, wenn ein erforderlicher Beschreibungsabschnitt entgegen den obigen Regeln fehlt oder leer ist

## Akzeptanzkriterien
- [ ] `.github/pull_request_template.md` existiert, und seine Abschnittsüberschriften stimmen in Reihenfolge und Wortlaut mit den fünf Überschriften in „Struktur der PR-Beschreibung" überein
- [ ] `.github/settings.yml` deklariert erforderliche Status-Checks für `develop` (direkt oder via der `nolte/gh-plumbing`-Commons-Extension)
- [ ] `enforce_admins` ist für die Branch-Protection-Regel von `develop` auf `true` gesetzt; es existiert keine Waiver-Regelung im Repository
- [ ] Für die letzten 10 nach `develop` gemergten PRs war jeder erforderliche Status-Check zum Merge-Zeitpunkt grün (Stichprobe via `gh pr list --state merged --base develop --limit 10 --json number,title,mergedAt,statusCheckRollup`)
- [ ] Für dieselben 10 PRs entsprechen die Titel der Conventional-Commits-Form, und `type` entspricht dem Branch-Präfix
- [ ] Die Quell-Branches derselben 10 PRs verwendeten eines der Präfixe `feat/`, `fix/`, `chore/`, `docs/`, und der Type im PR-Titel entsprach dem Präfix wortgleich
- [ ] Eine Stichprobe aktueller PR-Bodies zeigt alle fünf erforderlichen Abschnitte; nur Linked issues und Risk / rollout notes dürfen den Literaltext `None` enthalten; etwaige repo-spezifische Abschnitte erscheinen *nach* den fünf Pflichtabschnitten, niemals dazwischen
- [ ] `.github/workflows/pr-lint.yml` (oder ein gleichwertig benannter Workflow) existiert, und sein Job ist in `.github/settings.yml` als erforderlicher Status-Check für `develop` deklariert
- [ ] `.github/settings.yml` setzt `allow_squash_merge: true`, `allow_merge_commit: false`, `allow_rebase_merge: false` für das Repository
- [ ] Die letzten 10 First-Parent-Commits auf `develop` (via `git log --first-parent develop -n 10`) entsprechen je genau einem squash-gemergten PR und tragen eine Conventional-Commits-konforme Nachricht
- [ ] `.github/settings.yml` setzt `required_status_checks.strict: true` für die Branch-Protection von `develop` (direkt oder via der `nolte/gh-plumbing`-Commons-Extension), sodass GitHub die Branch-Up-to-date-Vorbedingung erzwingt

## Offene Fragen
- _Keine aktuell; alle Fragen aus der Entwurfsphase sind geklärt._
