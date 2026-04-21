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

### Struktur der PR-Beschreibung
Ein Pull-Request-Template **MUSS [MUST]** unter `.github/pull_request_template.md` existieren und **MUSS [MUST]** die folgenden Abschnitte in genau dieser Reihenfolge und mit genau diesen Überschriften enthalten:

1. **Summary** — ein bis drei Sätze, die *was* der PR ändert und *warum* benennen
2. **Changes** — Bullet-Liste der für Nutzer oder Reviewer relevanten Änderungen
3. **Linked issues** — `Closes #…` / `Refs #…`-Einträge oder der Literaltext `None`
4. **Testing** — wie die Änderung verifiziert wurde (ausgeführte Befehle, manuelle Schritte, Screenshots)
5. **Risk / rollout notes** — Risikoklasse, Migrationen, Feature-Flags oder der Literaltext `None`

- **MUSS [MUST]** jeden Template-Abschnitt im PR-Body erhalten; Abschnitte werden niemals entfernt, auch wenn sie leer wären
- **DARF NICHT [MUST NOT]** Summary, Changes oder Testing leer lassen; Linked issues und Risk / rollout notes **DÜRFEN [MAY]** den Literaltext `None` verwenden
- **SOLLTE [SHOULD]** Imperativform in Summary und Changes verwenden (`Add …`, `Fix …`, nicht `Added …`)
- **SOLLTE [SHOULD]** auf die relevante Spec-Datei unter `spec/` verlinken, wenn die Änderung eine Spec umsetzt oder modifiziert

### CI-Gate nach `develop`
- **MUSS [MUST]** die vollständige Menge der erforderlichen Status-Checks für `develop` als Code in `.github/settings.yml` deklarieren (direkt oder via der `nolte/gh-plumbing`-Commons-Extension); das GitHub-UI ist **KEIN** akzeptabler Ort, um erforderliche Checks hinzuzufügen oder zu entfernen
- **MUSS [MUST]** verlangen, dass jeder deklarierte Check Erfolg meldet, bevor ein PR nach `develop` gemergt werden kann
- **MUSS [MUST]** den `automerge.yaml`-Workflow so konfigurieren, dass er einen PR nur dann mergt, wenn jeder erforderliche Check Erfolg meldet und der PR freigegeben ist
- **SOLLTE [SHOULD]** `enforce_admins: true` für die `develop`-Branch-Protection setzen, damit Admin-Overrides keinen fehlschlagenden Check umgehen können; jedes Repository, das davon abweicht, **MUSS [MUST]** den Grund in der `README.md` des Repositorys oder in einer expliziten `.github/BRANCH_PROTECTION.md` dokumentieren
- **SOLLTE [SHOULD]** den Merge blockieren, solange ein Review ausdrücklich Änderungen anfordert, auch nachdem die CI grün geworden ist

### Draft- und Work-in-Progress-PRs
- **SOLLTE [SHOULD]** PRs während laufender Arbeit als Draft öffnen und erst dann als bereit für Review markieren, wenn die CI voraussichtlich grün wird und die Beschreibung vollständig ist
- **DARF NICHT [MUST NOT]** einen PR als bereit für Review markieren, wenn ein erforderlicher Beschreibungsabschnitt entgegen den obigen Regeln fehlt oder leer ist

## Akzeptanzkriterien
- [ ] `.github/pull_request_template.md` existiert, und seine Abschnittsüberschriften stimmen in Reihenfolge und Wortlaut mit den fünf Überschriften in „Struktur der PR-Beschreibung" überein
- [ ] `.github/settings.yml` deklariert erforderliche Status-Checks für `develop` (direkt oder via der `nolte/gh-plumbing`-Commons-Extension)
- [ ] `enforce_admins` ist für die Branch-Protection-Regel von `develop` auf `true` gesetzt, oder eine Ausnahme ist in `README.md` oder `.github/BRANCH_PROTECTION.md` dokumentiert
- [ ] Für die letzten 10 nach `develop` gemergten PRs war jeder erforderliche Status-Check zum Merge-Zeitpunkt grün (Stichprobe via `gh pr list --state merged --base develop --limit 10 --json number,title,mergedAt,statusCheckRollup`)
- [ ] Für dieselben 10 PRs entsprechen die Titel der Conventional-Commits-Form, und `type` entspricht dem Branch-Präfix
- [ ] Die Quell-Branches derselben 10 PRs verwendeten eines der Präfixe `feat/`, `fix/`, `chore/`, `docs/`, und der Type im PR-Titel entsprach dem Präfix wortgleich
- [ ] Eine Stichprobe aktueller PR-Bodies zeigt alle fünf erforderlichen Abschnitte; nur Linked issues und Risk / rollout notes dürfen den Literaltext `None` enthalten

## Offene Fragen
- Sollte die Squash-Merge- vs. Merge-Commit-Policy für PRs nach `develop` hier oder im Branching-Modell-Spec festgelegt werden?
- Ist `enforce_admins: true` ein hartes **MUSS [MUST]** über das gesamte Portfolio oder ist ein fallweiser Opt-out über eine dokumentierte Ausnahme dauerhaft akzeptabel?
- Sollte die Abschnittsliste des PR-Templates portfolio-weit strikt identisch sein oder darf ein Repository unterhalb der fünf erforderlichen Abschnitte repo-spezifische Abschnitte hinzufügen?
- Brauchen wir einen automatisierten Linter (z. B. einen Reusable Workflow), der einen PR mit spec-widrigem Body oder Titel scheitern lässt, anstatt auf Reviewer-Disziplin zu setzen?
