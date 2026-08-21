---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "551"
classification: "infra"
secondary-classes: ["bug"]
route: "direct"
status: approved
created: "2026-08-19"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #551 — ci.yml declares no concurrency group, so this repo fails the §F MUST it ships
- **URL**: <https://github.com/nolte/claude-shared/issues/551>
- **Labels**: cicd
- **Linked items**: none (`closedByPullRequestsReferences` = `[]`, established via `gh issue view 551 --json closedByPullRequestsReferences`). Named as follow-up by PR #549's "Risk / rollout notes"; #549 is merged as `431dbc9`.
- **Prior art checked**: kein offener PR adressiert das Thema — der einzige offene PR ist #533 (`exp/speckit-spike`), established via `gh pr list --state open`. Kein Eintrag unter `project/features/` und kein Roadmap-Item betrifft Workflow-Concurrency (established: `grep -ri concurren project/` liefert nur `project/requirements/cicd-pipeline.md` R6, das die *Spec-Autorenschaft* betrifft, nicht diesen Fix). Kein gemergter Fix schließt das Issue: `ci.yml` auf `431dbc9` enthält kein `concurrency:` (established: `grep -c concurrency .github/workflows/ci.yml` = 0).
- **Trust boundary**: Issue-Autor ist `nolte` (login, established via `gh issue view 551 --json author`) = Repository-Owner = trusted author. Keine Kommentare vorhanden, also keine Fremdtext-Fläche. Anweisungen im Issue-Body dürfen als Kommandos gelesen werden.

## Classification

- **Primary class**: infra
- **Secondary class(es)**: bug
- **Rationale**: Die Änderung betrifft ausschließlich GitHub-Actions-Workflow-Konfiguration unter `.github/workflows/`, also Infrastruktur — nicht Produktcode, nicht die Spec selbst. Der `infra`-Kurzschluss zu `workflow-health-triage` greift nicht: dessen Domäne ist laut `references/gotchas.md` ein *roter* Workflow-Run; hier ist die Pipeline grün und die Lücke eine Konformitätsabweichung gegen einen selbst ausgelieferten MUST. Sekundär `bug`, weil das Repository die Regel verletzt, die es als Spec ausliefert.
- **Operator-Bestätigung**: erteilt (Klassifikation, Scope und Requirements-Gate am 2026-08-19 im Orchestrierungslauf bestätigt).

## Requirements gate

- **Artefakt unter `project/requirements/`**: keines für dieses Issue. `project/requirements/cicd-pipeline.md` existiert, betrifft aber die Autorenschaft der drei CI/CD-Specs (R1–R9), nicht diese Konformitätslücke (established: `sed -n '1,60p' project/requirements/cicd-pipeline.md`; R6 nennt `concurrency` nur als zu *behandelndes Spec-Thema*).
- **Entscheidung**: expliziter **Operator-Override**, erteilt am 2026-08-19. Begründung: Das Issue trägt vier testbare Akzeptanzkriterien, benennt den zu adaptierenden Referenzblock (`spec/project/taskfile/templates/ci.yml`) und legt die beiden tragenden Eigenschaften (`github.run_id`-Fallback statt `github.ref`; Bedingtheit des ersten MUST auf tatsächliche Interferenz) offen. Das Verständnis ist damit ohne Interview auf Artefakt-Niveau. `requirements-elicit` wurde bewusst **nicht** dispatcht.

## Scope

- **In scope**:
  - `.github/workflows/ci.yml` erhält einen `concurrency:`-Block gemäß `spec/project/github-actions-best-practices/` §F, adaptiert aus `spec/project/taskfile/templates/ci.yml`.
  - Für **jeden** der übrigen neun Workflows unter `.github/workflows/` wird eine §F-Entscheidung getroffen und inline im jeweiligen Workflow als Kommentar festgehalten: entweder eine Gruppe mit Begründung, oder die explizite Feststellung, dass der Interferenztest nicht erfüllt ist.
  - Verifikation durch `nolte-shared:cicd-pipeline-reviewer` gegen `.github/workflows/`.
- **Out of scope**:
  - Änderungen an `spec/project/github-actions-best-practices/` oder `spec/project/taskfile/templates/ci.yml` selbst — die Spec ist die Referenz, nicht das Ziel. Sollte der Reviewer eine Spec-Lücke aufdecken, ist das ein Folge-Issue für den `spec`-Skill, nicht Teil dieses Laufs.
  - Die Job-Struktur von `ci.yml` (drei separate Jobs statt der Template-Matrix). Das Template setzt zusätzlich auf eine Matrix mit Kontexten `check (lint)` / `check (test)` / `check (docs)`; eine Umstellung würde die required contexts in `.github/settings.yml` mit umbenennen und ist ein eigener, größerer Strang. Adaptiert wird **nur** der `concurrency:`-Block.
  - Reusable Workflows unter `nolte/gh-plumbing` — `automerge.yaml`, `release-drafter.yml`, `release-cd-*.yml` rufen dort gepinnte Workflows auf. Regeln, die im Reusable selbst sitzen müssten, werden als Upstream-Work-Package gemeldet, nicht lokal kopiert (`project/requirements/cicd-pipeline.md`, `edge_cases`-Dimension).
  - Merge-Queue-Mechanik (§K). Dieses Repository fährt keine Merge Queue (Entscheidung dokumentiert: Merge Queue setzt Org-Eigentum voraus), daher entfällt die `merge_group`-Ableitung des Concurrency-Keys.

## Route

- **Decision**: direct
- **Rationale**: Ein kohärentes Ergebnis (die Workflow-Sammlung erfüllt §F), ein PR-Strang, kein neues und kein umgehängtes Roadmap-Item. Alle vier Akzeptanzkriterien des Issues liegen innerhalb eines Verzeichnisses. „Bounded" im Sinne der Gotchas ist Planungsform, nicht Aufwand — zehn berührte Dateien ändern daran nichts.
- **Pipeline hand-off**: entfällt.

## Bestandsaufnahme (established)

Vollständige Erhebung über `.github/workflows/` bei `431dbc9`, per `cat` je Datei. Das Issue listet sieben Workflows; im Repository liegen **zehn**. Die drei zusätzlichen sind unten mit `(+)` markiert — sie fehlen im Issue-Text, fallen aber unter AK 3 („kein Workflow bleibt stillschweigend ungeprüft") und unter AK 4, das gegen das ganze Verzeichnis prüft.

| Workflow | Trigger | `concurrency:` heute |
| --- | --- | --- |
| `ci.yml` | `push` (main, develop), `pull_request` (main, develop), `workflow_dispatch` | absent |
| `audit-gates.yml` | `pull_request` (paths-gefiltert) | absent |
| `release-automerge-guard.yml` | `pull_request` (labeled, reopened, synchronize) | absent |
| `automerge.yaml` | `pull_request`, `pull_request_review`, `check_suite`, `status` | absent |
| `release-drafter.yml` | `push` (develop), `workflow_dispatch` | absent |
| `release-publish.yml` | `workflow_dispatch` | present — `group: release-publish`, `cancel-in-progress: false` |
| `release-cd-deliver-docs.yml` | `release` (published), `workflow_dispatch` | job-level — `group: "pages"`, `cancel-in-progress: true` |
| `audit-cadence-reminder.yml` (+) | `schedule` (quartalsweise), `workflow_dispatch` | absent |
| `portfolio-audit-reminder.yml` (+) | `schedule` (quartalsweise), `workflow_dispatch` | absent |
| `release-cd-refresh-master.yml` (+) | `release` (published) | absent |

Zwei weitere belegte Fakten, die die Analyse tragen:

- **Required status checks auf `develop` sind `lint`, `test`, `docs`, `links`** (established: `.github/settings.yml:33-39`). Das sind exakt die Jobs aus `ci.yml`. Damit ist das im Issue beschriebene Risiko — ein `develop`-Commit trägt einen `cancelled` required check — nicht hypothetisch, sondern trifft genau die Kontexte, die der Release-Gate liest.
- **§F umfasst vier Regeln**, nicht eine (established: `spec/project/github-actions-best-practices/en.md` §F): der bedingte Gruppen-MUST, der Ableitungs-MUST (Workflow-Identität + Branch-/PR-Identität), das **MUST NOT** von cancel-on-new-run für Delivery-/Release-Workflows, und der cancel-on-new-run-SHOULD für Pre-Merge-Lanes samt Laufzeit-Vorbehalt.

## Work packages

### P1 — `ci.yml` erhält den §F-konformen Concurrency-Block

- **Problem statement**: `ci.yml` deklariert keine `concurrency:`-Gruppe. Aufeinanderfolgende Pushes auf einen Pull Request starten überlappende Läufe; nur das jüngste Verdikt zählt, der veraltete Lauf verbraucht weiter Kapazität und meldet ein obsoletes Ergebnis. Das ist §F's erster MUST plus dessen cancel-on-new-run-SHOULD. Der Block wird aus `spec/project/taskfile/templates/ci.yml:44-46` adaptiert, nicht aus Prosa komponiert, und die dortige per-Leg-Begründung wird auf dieses Repository zugeschnitten mitgeführt.
- **Acceptance criteria**:
  1. `.github/workflows/ci.yml` trägt einen Top-Level-`concurrency:`-Block, dessen `group` sowohl die Workflow-Identität als auch die PR-Identität enthält (§F, zweiter MUST).
  2. Die Push-Leg fällt **nicht** auf `github.ref` zurück, sodass kein `develop`-Commit einen `cancelled` required check (`lint`/`test`/`docs`/`links`) tragen kann.
  3. Über dem Block steht ein Kommentar, der die per-Leg-Begründung trägt: warum die PR-Leg gruppiert und cancel-fähig ist, und warum die Push-Leg in einer Gruppe je Lauf sitzt.
  4. `.github/workflows/ci.yml` bleibt gültiges YAML und die Job-Struktur (`lint`, `test`, `docs`, `links`, `docs-freshness`) ist unverändert — die required contexts aus `.github/settings.yml:33-39` behalten ihre Namen.
- **Touched files / artifacts**: `.github/workflows/ci.yml`
- **Specialist**: `nolte-shared:cicd-pipeline-design` (Skill; Beschreibung nennt „Designs, scaffolds, and audits a repository's CI/CD pipeline against … spec/project/github-actions-best-practices/ (… concurrency …). Writes and patches workflow files in the target repository." — Laufzeit-Match über `grep description: skills/*/SKILL.md`)
- **Depends on**: none

### P2 — §F-Entscheidung für die übrigen neun Workflows

- **Problem statement**: Neun weitere Workflows liegen unter `.github/workflows/`. Für jeden muss entschieden und inline dokumentiert werden, ob §F's bedingter Gruppen-MUST greift. Die Entscheidung ist **je Workflow** zu treffen und darf **nicht** als Batch-Apply des `ci.yml`-Musters ausgeführt werden. Die folgenden Einschätzungen sind Hypothesen für den Spezialisten, keine Vorgaben — jede darf mit Gegenbeleg widerlegt werden:
  - `automerge.yaml` — Merge-Akteur. cancel-on-new-run riskiert Abbruch mitten im Merge, genau der Ausfallmodus von §F's drittem MUST NOT. Die `check_suite`/`status`-Trigger bilden „Läufe auf demselben Branch" zudem nicht sauber auf eine PR-Nummer ab.
  - `release-drafter.yml` — mutiert bei jedem `develop`-Push denselben Draft-Release. Zwei Läufe interferieren tatsächlich; ein Abbruch kann den Draft um einen Eintrag ärmer zurücklassen. Vermutete Antwort: Gruppe **ohne** `cancel-in-progress`.
  - `release-automerge-guard.yml` — schreibt (entfernt ein Label, postet einen Kommentar). Zwei gleichzeitige Läufe könnten doppelt kommentieren; ein Abbruch mitten im Strip lässt das Label stehen und damit die Regel unerzwungen.
  - `audit-gates.yml` — zwei read-only Jobs auf einem PR; zu prüfen, ob überhaupt Interferenz vorliegt oder nur der Kapazitäts-SHOULD greift.
  - `release-cd-deliver-docs.yml` — trägt heute eine **Job-Level**-Gruppe `pages` mit `cancel-in-progress: true`. Zu prüfen ist, ob das gegen §F's drittes MUST NOT verstößt (Delivery-Workflow mit cancel-on-new-run) oder ob die Pages-Deployment-Semantik es rechtfertigt.
  - `release-cd-refresh-master.yml` — refresht bei jedem publizierten Release den Präsentations-Branch `main`. Zwei Läufe schreiben auf denselben Branch.
  - `release-publish.yml` — trägt bereits Gruppe plus `cancel-in-progress: false` mit Spec-Verweis; vermutlich bereits konform, ist aber ausdrücklich zu bestätigen statt zu überspringen.
  - `audit-cadence-reminder.yml`, `portfolio-audit-reminder.yml` — quartalsweise Cron plus `workflow_dispatch`; beide sind über eine Such-dann-Skip-Prüfung idempotent, was bei echter Gleichzeitigkeit ein TOCTOU-Fenster hat.
- **Acceptance criteria**:
  1. Jeder der neun Workflows trägt entweder einen `concurrency:`-Block mit inline begründendem Kommentar **oder** einen inline Kommentar, der ausdrücklich festhält, dass §F's Interferenztest nicht erfüllt ist — kein Workflow bleibt ohne Vermerk.
  2. Kein Delivery- oder Release-Workflow erhält neu `cancel-in-progress: true`; wo es heute gesetzt ist, ist es entweder entfernt oder mit Begründung gegen §F's drittes MUST NOT verteidigt.
  3. Jede Begründung verweist auf §F und benennt die konkrete Interferenz (oder deren Abwesenheit), statt die Spec-Prosa zu wiederholen.
  4. Alle neun Dateien bleiben gültiges YAML.
- **Touched files / artifacts**: `.github/workflows/{audit-gates.yml,automerge.yaml,release-automerge-guard.yml,release-drafter.yml,release-publish.yml,release-cd-deliver-docs.yml,release-cd-refresh-master.yml,audit-cadence-reminder.yml,portfolio-audit-reminder.yml}`
- **Specialist**: `nolte-shared:cicd-pipeline-design` (dieselbe Laufzeit-Auflösung wie P1)
- **Depends on**: P1 (serialisiert, weil beide Pakete dasselbe Verzeichnis anfassen und P1 das Begründungsmuster setzt, an dem P2 sich ausrichtet)

### P3 — §F-Verifikation über `.github/workflows/`

- **Problem statement**: AK 4 des Issues verlangt, dass `cicd-pipeline-reviewer` keinen §F-Befund gegen `.github/workflows/` meldet. Das ist ein eigenständiges, prüfbares Ergebnis und nicht durch P1/P2 impliziert: der Reviewer prüft alle zehn Dateien gegen die vollständige §F-Regelmenge, einschließlich der beiden Regeln, die P1 und P2 nicht direkt adressieren.
- **Acceptance criteria**:
  1. `nolte-shared:cicd-pipeline-reviewer` läuft gegen `.github/workflows/` und meldet **null** §F-Befunde.
  2. Befunde außerhalb §F (etwa zu §B-Permissions oder §G-Caching) werden im Ergebnis festgehalten und als außerhalb dieses Issues eingeordnet, statt stillschweigend mitgefixt zu werden — sie werden in den PR-Notes benannt.
- **Touched files / artifacts**: keine (read-only Audit); Ergebnis fließt in die PR-Notes.
- **Specialist**: `nolte-shared:cicd-pipeline-reviewer` (Agent; Beschreibung nennt „Read-only audit of a repository's CI/CD pipeline against … spec/project/github-actions-best-practices/: … concurrency …" — Laufzeit-Match über `grep description: agents/*.md`)
- **Depends on**: P1, P2

## Dependency ordering

P1 → P2 → P3

**Operator-Entscheidung 2026-08-19**: P1 und P2 werden in **einem** Aufruf von
`nolte-shared:cicd-pipeline-design` dispatcht statt in zwei sequentiellen. Die
DAG-Ordnung bleibt inhaltlich gültig (P1 setzt das Begründungsmuster, an dem sich P2
ausrichtet), wird aber innerhalb desselben Dispatches erfüllt. Der Dispatch-Log hält
die Ergebnisse weiterhin je Paket getrennt fest, damit AK 1/2 und AK 3 einzeln
nachvollziehbar bleiben. P3 bleibt ein eigener, nachgelagerter Dispatch.

## Risks

- **Ein Batch-Apply des `ci.yml`-Musters auf die übrigen neun Workflows** wäre die naheliegendste Fehlleistung und würde §F's drittes MUST NOT verletzen (cancel-on-new-run auf einem Delivery-Workflow). Mitigation: P2 verlangt eine Entscheidung *je Workflow* mit inline Begründung; AK 2 von P2 prüft genau darauf.
- **Ein auf `github.ref` gekeyter Push-Leg** würde `develop`-Commits mit `cancelled` required checks hinterlassen und den Release-Gate blockieren. Mitigation: P1 AK 2 macht die Abwesenheit dieses Musters zum expliziten Kriterium; die betroffenen Kontexte sind über `.github/settings.yml:33-39` belegt.
- **Regel-Drift zwischen `ci.yml` und dem ausgelieferten Template.** Wenn die Adaption vom Template abweicht, ohne den Unterschied zu begründen, entsteht genau die Diskrepanz, die dieses Issue schließen soll — nur in die andere Richtung. Mitigation: P1 AK 3 verlangt den begründenden Kommentar; Abweichungen von der Template-Form sind dort zu nennen.
- **Änderung an einem Workflow, der einen gepinnten Reusable aufruft.** `automerge.yaml`, `release-drafter.yml` und beide `release-cd-*.yml` delegieren an `nolte/gh-plumbing`. Eine Regel, die im Reusable sitzen müsste, darf nicht lokal nachgebaut werden. Mitigation: als Upstream-Work-Package melden und in den PR-Notes vermerken.
- **Security-sensitive Pfade**: `.github/workflows/` ist eine sicherheitsrelevante Fläche (Permissions, Secrets, Token-Scopes). Der Diff dieses Laufs ändert jedoch ausschließlich `concurrency:`-Blöcke und Kommentare, nicht `permissions:`, `secrets:` oder Trigger. Vor dem PR läuft dennoch der eingebaute `security-review`-Skill über den erzeugten Diff, und `cicd-pipeline-reviewer` deckt die Permission-Fläche mit ab.

## Open questions

- Keine offen. Scope (alle zehn Workflows), Klassifikation (`infra`, kein `workflow-health`-Handoff) und das Requirements-Gate (Override) sind am 2026-08-19 vom Operator entschieden.

## Dispatch log

<!-- Appended during operation 5. -->

2026-08-19 P1 + P2 dispatched together to `nolte-shared:cicd-pipeline-design` (Operator-Entscheidung, siehe §Dependency ordering) — umgesetzt in Commit `3f19628`. Alle zehn Workflows tragen jetzt einen `concurrency:`-Block mit inline begründendem Kommentar. YAML aller zehn Dateien parst; `task lint` (inkl. Vale), `task test` (159 passed, 2 skipped) und `task check:links` (0 kritisch) laufen grün im Worktree.

**Widerlegte Hypothesen aus P2** — der Spezialist hat drei der im Paket notierten Annahmen mit Gegenbeleg korrigiert:

1. **`audit-gates.yml` erfüllt §F's ersten MUST nicht.** Die Paketbeschreibung hatte offengelassen, ob Interferenz vorliegt. Gegenbeleg: `cve-scan` ruft `pip-audit` über die Manifeste auf, `license-drift` baut ein wegwerfbares venv unter `.sbom-venv` und vergleicht die SBOM gegen die committete Baseline — beide schreiben nichts außerhalb des Runners. Stattdessen: Gruppe allein aus §F's cancel-on-new-run-SHOULD für Pre-Merge-Lanes, und der Kommentar sagt das ausdrücklich, statt eine Interferenz zu behaupten, die es nicht gibt.
2. **`release-cd-deliver-docs.yml` verletzte §F's drittes MUST NOT.** Im Issue war die Datei nur als „job-level only" in der Bestandstabelle geführt, nicht als Befund. Gegenbeleg: `cancel-in-progress: true` auf einem `release: published`-Trigger ist cancel-on-new-run auf einem Delivery-Workflow — genau der von der Regel ausgeschlossene Fall. Stattdessen: auf `false` gesetzt. Dieser Befund liegt außerhalb der vier im Issue zur Analyse benannten Workflows, blockiert aber AK 4.
3. **`release-publish.yml` verletzt §F's zweiten MUST wörtlich, aber begründet.** `group: release-publish` trägt keine Branch- oder PR-Identität. Gegenbeleg gegen ein Ändern: die serialisierte Ressource ist der eine offene Draft-Release des Repositories, also global statt branch-lokal; eine per-Branch-Gruppe ließe zwei Dispatches denselben `--draft=false`-Aufruf rennen. Die Schadensklausel der Regel („so runs on different branches don't cancel each other") kann bei `cancel-in-progress: false` nicht eintreten. Stattdessen: Zustand unverändert, Verteidigung inline dokumentiert.

Vier weitere Dateien (`automerge.yaml`, `release-drafter.yml`, `release-cd-deliver-docs.yml`, `release-cd-refresh-master.yml`) deklarieren kein `name:`; dort steht ein literales Identitätspräfix statt `${{ github.workflow }}`, das sonst zum Dateipfad expandieren würde.

2026-08-19 P3 dispatched to `nolte-shared:cicd-pipeline-reviewer` (Runde 1, gegen Commit `3f19628`) — **AK 4 nicht erfüllt**. Der Reviewer widerlegte die Zero-Findings-Behauptung: 0 kritisch, 3 Warnings, 3 Suggestions in §F, dazu 5 §B-Befunde außerhalb §F. Zwei der drei Warnings waren echte Konfigurationsdefekte im Patch selbst, nicht Formulierungsmängel:

- **`automerge.yaml` mischte zwei Identitätsdomänen im Gruppenschlüssel.** Mit `github.event.pull_request.number` als erstem Glied landete ein `pull_request`-Lauf in `automerge-<nummer>`, ein `check_suite`-Lauf für dieselbe Pull Request aber in `automerge-<sha>`. Eine Gruppe serialisiert nur Läufe mit identischem Schlüsselstring, also trafen sich genau die Läufe nie, die der Block laut eigenem Kommentar serialisieren sollte. Korrigiert auf den Head-Commit als einzige Domäne, die alle vier Trigger erreichen (`pull_request.head.sha` / `check_suite.head_sha` / `sha`).
- **`release-drafter.yml` auf `github.ref` widersprach `release-publish.yml` über dieselbe Ressource.** Da der `push`-Trigger auf `develop` festliegt, `workflow_dispatch` aber von jedem Ref läuft, fielen beide in verschiedene Gruppen und konnten denselben globalen Draft gleichzeitig neu schreiben. Korrigiert auf eine globale Gruppe, konsistent mit `release-publish.yml`.
- **Die Begründung in `release-publish.yml` war plattformseitig falsch.** Sie behauptete, bei `cancel-in-progress: false` storniere kein Lauf einen anderen; tatsächlich verdrängt GitHub einen *wartenden* Lauf, sobald ein neuerer einreiht — was der `ci.yml`-Kommentar desselben Commits korrekt wiedergibt. Korrigiert: die Konsequenz wird benannt statt wegargumentiert.

Zwei Suggestions übernommen: der Pages-Block wanderte von der Job- auf die Workflow-Ebene, und `release-cd-refresh-master.yml` verlor eine Harmlosigkeitsprämisse über das Verhalten der Upstream-Reusable, die aus diesem Repository nicht nachprüfbar ist (`spec/claude/claim-provenance/`).

Zwei Operator-Entscheidungen zu den restlichen Befunden: die vier Workflows ohne `name:` bekommen einen, sodass `${{ github.workflow }}` auf einen Namen statt auf den Dateipfad auflöst und die Gruppen keine handgepflegten Literale mehr brauchen; die fünf §B-Berechtigungsbefunde werden in diesem PR mitbehoben statt in ein Folge-Issue ausgelagert. Beim Umsetzen kamen zwei weitere §B-Fälle derselben Regel hinzu, die der Reviewer nicht gelistet hatte (`issues: write` auf Workflow-Ebene in beiden Reminder-Workflows). Alle zehn Workflows tragen jetzt `contents: read` auf Workflow-Ebene mit Write-Scopes am jeweiligen Job. Umgesetzt in Commit `7ecade8`; Gate erneut grün (lint inkl. Vale, 159 Tests, 0 kritische Links).

2026-08-19 P3 Runde 2 (gegen Commit `7ecade8`) — **AK 4 weiterhin nicht erfüllt**: 3 Warnings, 2 Suggestions in §F, dazu 3 §B-Befunde. Die drei Warnings aus Runde 1 waren korrekt geschlossen, aber der Reviewer widerlegte zwei der sieben Behauptungen des Commits:

- **Die behauptete Lane-Übereinstimmung zwischen `release-drafter.yml` und `release-publish.yml` existiert nicht.** Beide Kommentare behaupteten „the two files have to agree"; die Gruppenstrings sind aber `release-drafter` und `release-publish`, und eine Gruppe serialisiert nur bei identischem String. §F's zweiter MUST verlangt die Workflow-Identität im Schlüssel und verhindert damit strukturell, dass zwei verschiedene Workflows je dieselbe Gruppe bilden. Der Draft bleibt zwischen den beiden Workflows unserialisiert. Geschlossen durch Offenlegung: die falsche Behauptung ist aus beiden Dateien gestrichen, das Restrennen ist als Open Question gegen §F benannt.
- **Derselbe Defekttyp stand unrepariert in beiden Reminder-Workflows.** `${{ github.workflow }}-${{ github.ref }}` bei einer repository-globalen Ressource: `schedule` läuft auf dem Default-Branch, `workflow_dispatch` von jedem Ref — genau das Paar, das der Block laut Kommentar serialisieren soll, landete in zwei Lanes. Der Fix-Durchgang hatte beide Dateien an `permissions:` angefasst, die Gruppe aber nicht. Beide jetzt global.

**§B: die tragende Warnung des Reviewers war ihrerseits teilweise falsch.** Er schrieb, für vier Dateien seien die Scope-Sätze „neu erfunden" und ihre Hinlänglichkeit unbelegbar. Gegenbeleg über `git show 431dbc9:.github/workflows/<datei>`: alle vier trugen ihren Job-Level-`permissions:`-Block bereits auf `develop`; verändert wurde nur die Workflow-Ebene, und da jeder dieser Workflows genau einen Job mit eigenem Block hat, blieb der effektive Token-Scope unverändert. Statt die Frage offen zu lassen, wurden die fünf Reusables am gepinnten Digest `d51e51ec` gelesen (`gh api repos/nolte/gh-plumbing/contents/...`) und die Caller-Sätze gegen die dort deklarierten Blöcke abgeglichen. Zwei echte Über-Gewährungen kamen dabei heraus, beide bestandsalt:

- `release-cd-deliver-docs.yml` gewährte `pages: write` und `id-token: write`. `reusable-mkdocs.yaml@v2.0.0` deklariert für seinen Job ausschließlich `contents: write` und deployt über `mhausenblas/mkdocs-deploy-gh-pages`, also einen `gh-pages`-Branch-Push statt der Pages-Deployment-API. Beide Scopes erreichten keinen Konsumenten; `id-token: write` war der mit dem größten Blast-Radius. Entfernt.
- `release-drafter.yml` gewährte `pull-requests: write`, die Reusable deklariert `pull-requests: read`. Verengt.

**Nebenbefund, bewusst nicht behoben:** `reusable-release-publish.yml@v2.0.0` deklariert dieselbe Concurrency-Gruppe `release-publish` wie ihr Caller. Verschachtelte identische Gruppen sind eine dokumentierte Deadlock-Form. Die Paarung ist bestandsalt und wird durch veröffentlichte Releases empirisch als durchlaufend belegt; sie ist als Verifikationspunkt gegen die Upstream-Reusable notiert, statt eine Gruppe umzubenennen, die dieses Repository nicht besitzt.

Umgesetzt in Commit `22e6844`; Gate erneut grün.

2026-08-19 P3 Runde 3 (gegen Commit `22e6844`) — **AK 4 weiterhin nicht erfüllt**: 3 Warnings, 1 Suggestion. Der Reviewer widerlegte die zentrale Behauptung des Commits, und die Widerlegung war im selben Change-Set belegbar:

- **„Two different workflows never produce an equal group string" ist falsch.** Concurrency-Gruppen sind repository-weite Strings; zwei Workflows teilen eine Lane, sobald ihr Gruppenstring gleich ist. §F Regel 2 ist eine Vorschrift, keine Plattformschranke — beides war verwechselt. Gegenbeleg zwei Dateien weiter im selben Commit: `release-cd-deliver-docs.yml` begründet das Literal `pages` ausdrücklich damit, dass künftige Workflows dieser Lane beitreten. Damit war der als „durch Offenlegung geschlossen" verbuchte Punkt eine Ausweichung, keine Auflösung.
- **Das ausgewichene Rennen ist real und belegt.** `reusable-release-publish.yml` setzt `target_commitish` (Zeile 428) deutlich vor dem `--draft=false`-Flip (Zeile 628); ein Drafter-Lauf in diesem Fenster verschiebt das Ziel, sodass ein Tag aus einem Commit geschnitten wird, den der Verify-Schritt nie geprüft hat. Behoben: beide Dateien teilen jetzt das Literal `release-draft` mit `cancel-in-progress: false`.
- **Der Verweis „recorded as an open question against §F" war eine nicht eingelöste Zusage.** Ein Grep über den `spec/`-Baum fand keinen solchen Eintrag. Das ist ein Verstoß gegen `spec/claude/claim-provenance/`: eine billig prüfbare Behauptung stand als established da.
- **Die Begründung fürs Nichtstun bei der verschachtelten Gruppe war falsch.** Umzubenennen war nicht die Gruppe der Upstream-Reusable, sondern die des Callers — und die besitzt dieses Repository sehr wohl. Der Caller-Rename auf `release-draft` löst beide Befunde in einem Zug.

**Operator-Entscheidung zur Scope-Grenze:** §F Regel 2 verlangt Workflow- *und* Branch-Identität, was bei einer repository-globalen Ressource keine korrekte Konfiguration erfüllen kann — ein Draft-Release, ein Pages-Ziel und ein Quartals-Tracking-Issue existieren je einmal pro Repository, also spaltet jeder identitätstragende Schlüssel genau die Lane auf, die sie schützt. Fünf der zehn Gruppen benennen deshalb die Ressource. Statt das je Datei einzeln zu verteidigen, wurde ein **additiver** Eintrag unter §Offene Fragen in `spec/project/github-actions-best-practices/` (EN + DE) ergänzt; er ändert keine Regel. Damit weicht der Lauf von der im Artefakt festgehaltenen Out-of-scope-Grenze für `spec/` ab — bewusst und operator-freigegeben, weil AK 4 sonst nur durch eine unbelegte Behauptung erreichbar gewesen wäre.

Drei überzogene Behauptungen wurden zusätzlich korrigiert: die PR-Nummer ist nur aus `status` unerreichbar (`check_suite` führt ein `pull_requests[]`-Array), die Serialisierung schließt bei den Remindern das Nebenläufigkeits- und nicht das Suchindex-Fenster, und `pull-requests: read` bei release-drafter ist nur für die aktuellen Trigger korrekt, weil die geerbte Commons-Config einen Autolabeler mitbringt.

Umgesetzt in Commit `199e7d8`; Gate erneut grün.
