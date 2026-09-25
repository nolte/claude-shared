# Group pre-analysis: 2026-09-25-consumer-reachability

> Run-scoped artifact. Committed on the integration branch, removed with a fix-forward
> `git rm` before the bundle merges. It must never reach the default branch, and it must
> never be hidden behind a `.gitignore` entry.

## Scope of this analysis

**Research question:** Welche der offenen Issues #664–#667 (und das Tracking-Issue #644)
bilden eine Gruppe mit einem gemeinsamen strukturellen Grund, und was muss sich in diesem
Repository ändern, damit die drei betroffenen Artefakte aus einem Consumer-Repository
heraus nutzbar sind?

**The group's single logical change, in one sentence:** Drei Hub-Artefakte — der Skill
`requirements-elicit`, der Agent `implementation-plan-author` und der Validator
`scripts/validate_skills.py` — werden aus einem Consumer-Repository heraus nutzbar, das
weder eine lokale Spec-Kopie noch ein GitHub-Issue noch einen Clone dieses Repositories hat.

**Out of scope:**

- #664 (`error-tracking-audit-scanner` / Sentry 11 `dataCollection`): eigene Defektklasse
  („Messwerkzeug prüft eine Schreibweise statt den Effekt", vgl. #660), eigener
  Touch-Surface (Scanner-Agent + `spec/project/error-tracking/`), kein Consumer-Reach-Bezug.
  Geht einzeln an `issue-orchestrate`.
- #644 (Actions-Concurrency, Tracking-Issue): kein bounded Issue — es hält Evidenz und
  wartet laut Kommentar vom 2026-09-20 nur noch auf `nolte/kamerplanter#1584`. Nicht
  admittierbar.
- #393 (Dependency Dashboard): Bot-Issue, kein Arbeitsgegenstand.
- Option 2 aus #665 (`Portfolio-Scope: portfolio` für `requirements-elicitation`): eine
  Kurations-Entscheidung des Hub-Maintainers je Spec
  (`spec/project/portfolio-inherited-spec-layer/en.md:33`), und der Inheritance-Resolver
  ist noch nicht ausgeliefert — die Markierung allein macht den Skill heute nicht lauffähig.
  Wird nur aufgenommen, wenn der Operator sie am Write-Gate explizit wählt.
- Die Consumer-Seite (`nolte/claude-goose` Feature 005: `recipe-requirements-elicit`,
  `recipe-plan`, `OMISSIONS.md`): wird durch die Gruppe entblockt, aber nicht hier geändert.

**Tier:** 3 — #667 veröffentlicht einen neuen Consumer-Vertrag (Hook-ID `validate-skills`,
den Consumer per `rev:` pinnen), und der Auslöser der Gruppe liegt in einem anderen
Repository (`nolte/claude-goose`). Tier-3-Pflichten: (1) die „Wo landet die Änderung"-Fragen
sind in §"Open questions for the operator" als explizite Operator-Entscheidungen vor dem
„Wie" gestellt; (2) nach der Implementierung läuft ein Verifikationspass in einem Kontext,
der die Änderung nicht produziert hat (`/code-review` aus dem Worktree plus
`nolte-engineering:python-code-reviewer` für den Validator-Refactor); (3) die Member-Reihenfolge
ist die Slice-Grenze — ein Member mit grünen Checks ist ein verifizierter Slice.

## Members

| Issue | Class | Admitting predicate | Evidence |
|---|---|---|---|
| #665 | bug | thematic coupling | `skills/requirements-elicit/SKILL.md:53` bricht ab, wenn `spec/project/requirements-elicitation/<canonical_language>.md` nicht *im aktuellen Projekt* liegt; 11 Geschwister-Skills tragen den `${CLAUDE_PLUGIN_ROOT}/spec/...`-Fallback (`grep -rln 'CLAUDE_PLUGIN_ROOT}/spec' skills/*/SKILL.md` → 11 Treffer, z. B. `skills/github-issue-templates-apply/SKILL.md:49`); `spec/README.md:104` führt die Spec als `local`, kein `Portfolio-Scope:`-Header in `spec/project/requirements-elicitation/en.md` |
| #666 | feature-request | thematic coupling + dependency chain (nach #665) | `plugins/nolte-engineering/agents/implementation-plan-author.md:38` „one of four sanctioned sources"; `:40-42` bindet den Requirements-Pfad an ein „analysed GitHub issue"; `:130-141` wiederholt die Vier-Quellen-Liste als Precondition; `:201-206` und `:241` kennen keinen Schreibpfad für ein issue-loses Requirements-Artefakt |
| #667 | feature-request | thematic coupling | `ls .pre-commit-hooks.yaml` → „No such file"; `scripts/validate_skills.py:36` `REPO = Path(__file__).resolve().parent.parent`, `:974`/`:1005` `p = REPO / t`, `:991` `path.relative_to(REPO)` — Ziele werden gegen den *Clone des Validators* aufgelöst, nicht gegen das Repository des Aufrufers; ein Consumer-Pfad außerhalb des Clones wirft `ValueError` |

**Gemeinsame Kopplung (thematisch):** Jedes Member ist ein Hub-Artefakt, das stillschweigend
das Hub-Repository als Ausführungskontext voraussetzt — Spec lokal vorhanden (#665),
GitHub-Issue vorhanden (#666), Aufrufer = eigener Clone (#667). Alle drei wurden vom
selben Consumer (`nolte/claude-goose` Feature 005) beim Adoptionsversuch gefunden; das
Zeitfenster ist Begleitumstand, nicht Prädikat.

**Dependency ordering:** #665 → #666 → #667. #665 vor #666, weil #666 ein
`requirements-elicit`-Artefakt konsumiert, das ein Consumer erst nach #665 erzeugen kann
(semantische Kette; keine Code-Abhängigkeit). #667 ist von beiden unabhängig und läuft
zuletzt, weil es den größten Diff und den einzigen Python-Refactor trägt.

**Shared touch surface:** Keine Datei wird von mehr als einem Member geändert.
Gemeinsam sind nur die Prüfpfade: `scripts/validate_skills.py` prüft #665 und #666
(Frontmatter/Body-Gates, Description-Budget) und ist zugleich das Änderungsobjekt von #667 —
deshalb läuft #667 zuletzt, damit die Checks von #665/#666 gegen den unveränderten
Validator gemessen werden.

## Mode decision

**Mode:** A — single strand

**Reason:** Kein Member erfüllt das Removability-Kriterium: alle drei sind vom Maintainer
selbst eingebracht, bounded, ohne externe Abhängigkeit und ohne ausstehendes Review, das
sie ablehnen könnte. Die einzige Unsicherheit (Hook-Form in #667) wird am Write-Gate als
Operator-Entscheidung geschlossen, nicht in der Implementierung entdeckt. Die Touch-Surfaces
sind disjunkt, also bliebe ein späteres Herauslösen von #667 auf das Revertieren seiner
eigenen Commits beschränkt.

## Structural finding

**Cluster shape:** class cluster

**Root cause or defect class:** „Hub-Kontext-Annahme": ein Plugin-Artefakt funktioniert nur,
wenn es im `claude-shared`-Repository selbst läuft. Die drei Ausprägungen: Spec-Pfad ohne
Plugin-Root-Fallback (#665), Eingabevertrag an den hub-eigenen Issue-Flow gebunden (#666),
Pfadauflösung gegen `Path(__file__)` statt gegen das aufrufende Repository (#667).

**Process finding:** Der Validator kennt die Klasse bereits für *Agents*:
`scripts/validate_skills.py:811-843` (`SPEC_FALLBACK_UNSTATED` / `AGENTS_CHECKED`,
Finding `agent-management.spec-fallback-backlog`, #592) zählt Agents, die `spec/<topic>/<slug>/`
als Eingabe nennen, ohne zu sagen, was sie bei fehlender Spec im Consumer tun. Für *Skills*
gibt es keinen solchen Check — deshalb ist `requirements-elicit` (Skill, Precondition ohne
Fallback) durchgerutscht, obwohl 11 Geschwister das Muster tragen. Noch nicht als Issue
gefiled; wird nach Operator-Freigabe als eigenes Issue mit Verweis auf diese Group-ID
angelegt.

**Preventive change:** Den Spec-Fallback-Check auf Skills ausdehnen: ein Skill, dessen
Precondition eine `spec/<topic>/<slug>/`-Datei „in the current project" verlangt, ohne
`${CLAUDE_PLUGIN_ROOT}`-Fallback oder inlined Baseline oder expliziten Stop-and-report,
wird gemeldet. Für die Ausprägungen #666/#667 (Eingabevertrag, Pfadauflösung) existiert kein
mechanischer Guard; Nachweis bleibt Consumer-Dogfooding.

**Recurrence fed to the portfolio loop:** Klasse „Hub-Kontext-Annahme in Plugin-Artefakten";
Recurrence 2 — Vorläufer #592 (46 von 63 Agents ohne Spec-Fallback-Aussage, laut
`python3 scripts/validate_skills.py`-Lauf vom 2026-09-25), jetzt diese Gruppe.

## Completeness matrix

Spalten aus dem Repository abgeleitet: Plugin-Artefakte (`skills/`, `plugins/*/agents/`),
Source (`scripts/`, `pyproject.toml`), Spec (`spec/`), Tests (`tests/`, `task test`),
Docs (`docs/`, `mkdocs.yml`, `README.md`), Config/Workflows (`.pre-commit-config.yaml`,
`.github/`, `Taskfile.yml`), Generated index (Docs-Katalog via `on_pre_build` — `docs/en/skills/`
ist gitignored und wird bei `task docs` erzeugt; `spec/README.md`).

| Member | Plugin artefacts | Source | Spec | Tests | Docs | Config / workflows | Generated index |
|---|---|---|---|---|---|---|---|
| #665 | `skills/requirements-elicit/SKILL.md:53` §Precondition: Fallback auf `${CLAUDE_PLUGIN_ROOT}/spec/project/requirements-elicitation/<canonical_language>.md` im Wortlaut von `skills/github-issue-templates-apply/SKILL.md:49`; Body-only, die Description (999/1024 Zeichen) bleibt unverändert; check: `python3 scripts/validate_skills.py skills/requirements-elicit/` (Exit 0, kein Critical) | not applicable — kein Script beteiligt | not applicable — Option 1 ändert keinen Spec-Text (Option 2 wäre `spec/project/requirements-elicitation/{en,de}.md` Header + `spec/README.md:104`) | not applicable — Prosa-Änderung, der Validator-Lauf ist der Check | not applicable — die Katalogseite wird aus dem Frontmatter erzeugt, das unverändert bleibt | not applicable | Katalog regeneriert aus unverändertem Frontmatter; check: `task docs` (mkdocs `--strict`, Exit 0) |
| #666 | `plugins/nolte-engineering/agents/implementation-plan-author.md`: fünfte Quelle in `:38-56`, Precondition-Liste `:130-141`, Schreibpfad `.audits/requirements/<slug>-plan.md` in `:201-206` und Targets-Zeile `:241`, `use_when`-Eintrag; Description nur ergänzen, wenn das Plugin-Budget hält (Headroom 1389 Zeichen bei 25149 Ceiling, gemessen 2026-09-25), sonst Body-only; check: `python3 scripts/validate_skills.py plugins/nolte-engineering/agents/` (Exit 0, kein `agent-description-budget`-Critical) | not applicable — kein Script beteiligt | not applicable — `spec/project/issue-orchestration/en.md` zählt die Eingabequellen des Agents nicht auf (`grep -n 'observability-audit\|grounded input' spec/project/issue-orchestration/en.md` → 0 Treffer) | not applicable — Prosa-Änderung, der Validator-Lauf ist der Check | not applicable — Agent-Katalogseite wird aus dem Frontmatter erzeugt | not applicable | Katalog regeneriert; check: `task docs` (Exit 0) |
| #667 | not applicable — kein Skill/Agent ändert sich | `scripts/validate_skills.py` `main()`: Ziele und `rel` gegen `Path.cwd()` auflösen (Hub-exklusive Checks — Description-Baselines `:910-916`, Backlog-Drains `:652`/`:834` — bleiben über ihre hub-relativen Schlüssel wirkungslos im Consumer); `pyproject.toml`: `[project.scripts] validate-skills` + setuptools-Konfiguration (`package-dir`/`py-modules` für `scripts/validate_skills.py`), sofern Hook-Form „python" gewählt wird; check: `python3 -m pytest tests/test_validate_skills.py -q` + `pre-commit try-repo . validate-skills --all-files` (Exit 0) + Negativprobe: Consumer-ähnlicher Baum in `tmp_path` mit kaputtem Frontmatter → Exit 1 | not applicable — `spec/claude/skill-management/en.md` nennt den Validator nur als lokalen Stop-gap (`:47`), kein Consumer-Vertrag spezifiziert | `tests/test_validate_skills.py`: neue Tests für CWD-relative Auflösung (Aufruf aus fremdem cwd, Pfad außerhalb `REPO`) und für den Hook-Entry; check: `python3 -m pytest tests -q` (Exit 0) | Consumer-Snippet (`repo: https://github.com/nolte/claude-shared`, `rev: v0.1.12`, `hooks: [id: validate-skills]`) in `docs/en/using.md` + `docs/de/`-Pendant; `README.md` steht bei 201 Zeilen gegen das 200-Zeilen-Budget aus `spec/project/readme-structure/`, also kein README-Zuwachs; check: `task docs` (Exit 0) | `.pre-commit-hooks.yaml` neu (Hook-ID `validate-skills`, `files:` auf `SKILL.md`/`agents/*.md`, `additional_dependencies: [PyYAML>=6]` bei Form „python"); `.pre-commit-config.yaml:51-56` bleibt als hub-lokaler Aufruf, bekommt aber denselben Entry-Pfad; check: `pre-commit run validate-skills --all-files` (Exit 0) | not applicable — kein Katalogeintrag für Scripts; `task docs` läuft ohnehin für die Docs-Spalte |

## Risks

- **#667 Hook-Form „python":** `pip install .` gegen den Clone muss gelingen; das
  Flat-Layout mit `tests/__init__.py` kann setuptools' Auto-Discovery stolpern lassen
  („Multiple top-level packages"). Kosten: eine explizite `[tool.setuptools]`-Konfiguration;
  ohne sie schlägt der Hook beim Consumer beim ersten Install fehl.
- **#667 Hook-Form „script":** kein Install, aber PyYAML muss im Consumer-Environment
  liegen; `scripts/validate_skills.py:32-34` degradiert sonst den Strict-Parse-Check still zum
  No-op — ein grüner Hook, der weniger prüft, als der Consumer glaubt.
- **#667 Tests:** `tests/test_validate_skills.py` nutzt `v.REPO` an mehreren Stellen
  (`:128`, `:135`, `:145`); der Refactor muss `REPO` für Hub-exklusive Checks behalten und
  nur die Zielauflösung auf `cwd` umstellen, sonst brechen die Budget-Tests.
- **#666 Description-Budget:** 1389 Zeichen Headroom im `nolte-engineering`-Agent-Budget;
  ein zu langer Description-Zusatz kippt das Gate für das ganze Plugin. Body-first.
- **#665 Description-Cap:** `requirements-elicit` steht bei 999/1024 Zeichen; die Änderung
  bleibt im Body.
- **`Closes #n` auf `develop`:** feuert unzuverlässig; Operation 7 prüft jeden State und
  schließt explizit.

## Open questions for the operator

- **Membership:** #665 + #666 + #667 als Gruppe bestätigen? (#664, #644, #393 bewusst nicht
  aufgenommen, Gründe oben.)
- **Wo landet #665 (Tier-3-Designfrage):** Option 1 — Plugin-Root-Fallback im
  SKILL-Precondition, Muster der 11 Geschwister (Empfehlung: minimal, sofort wirksam,
  keine Kurations-Entscheidung); Option 2 — `Portfolio-Scope: portfolio` (Kuration, wirkt
  erst mit Resolver); oder beides.
- **Wo landet #667 (Tier-3-Designfrage):** Hook-Form „python" (Console-Script
  `validate-skills` aus `pyproject.toml`, PyYAML als `additional_dependencies`, isoliertes
  Env — Empfehlung) oder „script" (direkter Aufruf, PyYAML aus dem System-Env).
- **Mode A** bestätigen.
- **Process-Finding** als eigenes Issue anlegen (Spec-Fallback-Check auf Skills ausdehnen)?

## Member results

Filled during implementation. Each entry records the dispatched specialist and the
**actual output** of every declared check, never an assertion that it passed.

| Member | Specialist | Check | Actual output |
|---|---|---|---|
| #665 | `nolte-claude-dev:claude-plugin-developer` | `python3 scripts/validate_skills.py skills/requirements-elicit/` | `validate_skills: 1 artifacts; 0C / 0W / 0S / 2I` (Info: description-headroom 999/1024, rpi-adoption-backlog — beide vorbestehend); Exit 0 |
| #665 | `nolte-claude-dev:claude-plugin-developer` | `git diff --stat` | `skills/requirements-elicit/SKILL.md \| 2 +-`, `skills/requirements-elicit/examples/01-vague-greenfield-elicit.md \| 3 ++-` — 2 files changed, 3 insertions(+), 2 deletions(-) |
| #665 | `nolte-claude-dev:claude-plugin-developer` | `grep -c CLAUDE_PLUGIN_ROOT skills/requirements-elicit/SKILL.md` | `1` |
| #665 | `nolte-claude-dev:claude-plugin-developer` | `task lint` (Agent-Lauf) + `pre-commit` beim Commit | alle Hooks Passed |
| #666 | `nolte-claude-dev:claude-plugin-developer` | `python3 scripts/validate_skills.py plugins/nolte-engineering/agents/` | `validate_skills: 39 artifacts; 0C / 0W / 0S / 1I` (Info: spec-fallback-backlog, vorbestehend); `agent-description-budget`-Treffer: 0; Description 886 → 942 Zeichen |
| #666 | `nolte-claude-dev:claude-plugin-developer` | `grep -n 'four sanctioned\|one of four' plugins/nolte-engineering/agents/implementation-plan-author.md` | leer, Exit 1 |
| #666 | `nolte-claude-dev:claude-plugin-developer` | `git diff --stat` | `plugins/nolte-engineering/agents/implementation-plan-author.md \| 42 +++++++++++++++-------` — 1 file changed, 29 insertions(+), 13 deletions(-) |
| #666 | `nolte-claude-dev:claude-plugin-developer` | `pre-commit` beim Commit | alle Hooks Passed |
| #667 | `nolte-engineering:fullstack-developer` (P1, P2); generalist (P3, no matching specialist — `audience-doc-author` needs an audience artifact this repo lacks) | Consumer-Negativprobe: tmp-Verzeichnis mit kaputter `skills/x/SKILL.md`, `python3 <hub>/scripts/validate_skills.py skills/x/SKILL.md` | `validate_skills: 1 artifacts; 3C / 0W / 1S / 1I`, erste Zeile `Critical    skills/x/SKILL.md  [skill-management.frontmatter-yaml-invalid] …`; Exit 1 |
| #667 | `nolte-engineering:fullstack-developer` | `python3 -m pytest tests -q` | `568 passed, 2 skipped in 16.44s`; Exit 0 (46 in `test_validate_skills.py`, davon 4 neu) |
| #667 | `nolte-engineering:fullstack-developer` | `python3 scripts/validate_skills.py` vom Hub-Root vor/nach dem Refactor, `diff` | Validator Exit 0; `diff` leer, Exit 0 (40 Zeilen identisch) |
| #667 | `nolte-engineering:fullstack-developer` | `pip install <worktree>` in frisches venv; `validate-skills --version` | pip Exit 0; `validate_skills.py 1.0.0` |
| #667 | `nolte-engineering:fullstack-developer` | `pre-commit try-repo <worktree> validate-skills --all-files` (Hub) | `validate skill/agent frontmatter.........Passed`; Exit 0 |
| #667 | `nolte-engineering:fullstack-developer` | `pre-commit try-repo <worktree> validate-skills --files skills/x/SKILL.md` in einem Consumer-Testrepo | `Failed - exit code: 1`, `Critical    skills/x/SKILL.md  [skill-management.frontmatter-yaml-invalid] …` (PyYAML kommt über `additional_dependencies` an); Exit 1 |
| #667 | `nolte-engineering:fullstack-developer` | `pre-commit run --files .pre-commit-hooks.yaml pyproject.toml scripts/validate_skills.py tests/test_validate_skills.py` | alle Hooks Passed; Exit 0 |
| #667 | generalist (P3) | `pre-commit run --files docs/en/using.md docs/de/using.md`; `task --yes docs` (mkdocs `--strict`, Docs-venv aus `docs/requirements.lock.txt`) | alle Hooks Passed; `Documentation built in 22.70 seconds`, Exit 0 |

## Deviations

| Member | Kind | What changed |
|---|---|---|
| #665 | local adaptation | Zweite Gate-Restatement-Stelle `skills/requirements-elicit/examples/01-vague-greenfield-elicit.md:16` mitgezogen (skill-management §Progressive disclosure); Matrix-Zelle „Plugin artefacts" um die Beispieldatei erweitert. Admission, Mode und Ordering unverändert. |
| #666 | local adaptation | Ein erster `use_when`-Eintrag mit 126 Zeichen löste `agent-management.frontmatter-use-case-field` (Critical, Katalog-Limit 120) aus und wurde auf 116 Zeichen gekürzt; Step 1 und die Write-effects-Zeilen Preconditions/Idempotency wurden für die issue-lose Quelle mit nachgezogen. Admission, Mode und Ordering unverändert. |
| #667 | local adaptation | Widerlegung durch den Spezialisten: ein cwd-relativer Schlüssel macht das Description-Budget im Consumer *nicht* inert — ein Consumer-`agents/` trägt denselben Schlüssel `agents` wie der Hub (`AGENT_DESC_BASELINE_CHARS`, Wert 9413). `check_agent_description_budget` bildet den Schlüssel deshalb über `resolve().relative_to(REPO)` und liefert `[]` außerhalb des Hubs; Hub-Verhalten per leerem Vorher/Nachher-Diff belegt. Zweite Anpassung: `packages = []` in `[tool.setuptools]` schaltet die Flat-Layout-Autodiscovery ab; `/build/` in `.gitignore`, weil `pip install .` es im Baum anlegt. `try-repo` gegen den Worktree braucht die getrackte `.pre-commit-hooks.yaml` (`git add`), sonst `InvalidManifestError`. Admission, Mode und Ordering unverändert. |
