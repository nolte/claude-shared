---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "814"
classification: "bug"
secondary-classes: []
route: "direct"
status: approved
created: "2026-11-25"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #814 — fix(scripts): report undecodable input by path in validate_skills, gen_catalog, validate_mission and check_prose
- **URL**: https://github.com/nolte/claude-shared/issues/814
- **Labels**: bug
- **Linked items**: #812, #813 (gemergt 72cba52c); zurückgenommener Versuch dd075ede, Revert dd1cb8dd
- **Prior art checked**: keine offene PR (`gh pr list --state all --search 814`); kein Artefakt unter `project/requirements/`; dd075ede gelesen (Commit-Message, Dateiliste), Inhalt nicht übernommen
- **Working copy**: `/home/nolte/repos/.worktrees/claude-shared/814-undecodable-input`, Branch `fix/814-undecodable-input` off `origin/develop` b001e8cc, erstellt via `task worktree:add`; `git check-ignore -q` auf diesem Pfad: Exit 1 (nicht ignoriert)
- **Trust**: Issue und Kommentar von `nolte` (Repo-Owner, trusted)
- **Requirements gate**: Operator-Override 2026-11-25 — das Issue mit seinen Akzeptanzkriterien und den fünf „must not repeat"-Punkten ist die Requirement-Quelle; kein `requirements-elicit`.

## Classification

- **Primary class**: bug
- **Secondary class(es)**: none
- **Rationale**: Repo-Skripte sterben bei nicht-UTF-8-Eingabe mit nacktem Traceback ohne Dateipfad und verlieren dabei alle übrigen Befunde.
- **Asserted cause verified**: confirmed. Scratch-Repo mit `skills/foo-apply/SKILL.md` (Byte `0xe9` in der description) und gültigem `skills/bar-apply/SKILL.md`: `python3 scripts/validate_skills.py` → `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 36`, Exit 1, kein Dateiname, kein Befund für `bar-apply`. Lesestellen ohne `try` bestätigt: `scripts/validate_skills.py:891,928,1139,1231`; `scripts/docs/gen_catalog.py:358,388,664,709,1129`; `scripts/validate_mission.py:127,172,187,431` (`git show … text=True`), `:438` fängt nur `OSError`; `scripts/check_prose.py:106,126` (`text=True`), `:166` fängt nur `OSError`. Hook `scripts/validate_edited_artifact.py:79` meldet nur `returncode == 1`. Docstring `validate_mission.py:15-18` verspricht Exit 2 für „file unreadable", `:439-440` liefert einen Critical (Exit 1).

## Scope

- **In scope**: Decode-Fehler an den genannten Stellen der vier Skripte; Regressionstest über `validate_skills.py` + `validate_edited_artifact.py`; Docstring-/Code-Abgleich in `validate_mission.py`.
- **Out of scope**: Die Kommentar-Punkte (`check_spec_inheritance.py` stille Fallbacks/Shape-Checks, `validate_schemas.py` `mappings`-Validierung) — andere Defektklasse (Shape statt Decode), abgespalten in #816 (Operator-Entscheidung 2026-11-25). Weitere Decode-Stellen in anderen `scripts/`-Dateien → Class-Sweep-Rest, im PR dokumentiert.

## Route

- **Decision**: direct
- **Rationale**: Eine Defektklasse, ein PR-Strang, kein Roadmap-Item.

## Design-Entscheidungen (verbindlich für alle Pakete)

1. **Exit-Codes bleiben, wie sie sind.** Eine undekodierbare Eingabedatei ist ein per-file **Critical**-Befund (→ Exit 1) in `validate_skills` und `validate_mission`; `gen_catalog` hebt `CatalogError` (→ Exit 1 / `PluginError`); `check_prose` hebt `CheckUnavailable` (→ Exit 2, sein dokumentierter „could not run"-Code). Damit meldet der Hook (nur `== 1`) weiter, ohne dass er geändert werden muss (Issue-Punkt 1).
2. **Nie in einen stillen Default fangen.** Kein `errors="replace"`, kein `None`/leerer Index ohne begleitenden Befund, kein Exit 0 aus einem Fehler.
3. **Pro Datei fangen, an der Lesestelle, und weitermachen** (Issue-Punkte 2, 3): übrige Befunde bleiben erhalten.
4. **Ausgabe für gültige Eingabe byte-identisch** zu vorher.
5. **Tests zuerst:** Jeder neue Test schlägt gegen den Code vor dem Fix fehl (rot belegt, dann grün).

## Work packages

### P1 — validate_skills: undekodierbares Artefakt als per-file Critical

- **Problem statement**: Ein nicht-UTF-8 `SKILL.md`/Agent bricht den ganzen Lauf ohne Pfad ab.
- **Acceptance criteria**:
  - `check_skill`/`check_agent`: Decode-Fehler → genau ein Critical `skill-management.unreadable` bzw. `agent-management.unreadable` mit Pfad und Byte-Position; Lauf geht weiter, Befunde anderer Artefakte erscheinen; Exit 1.
  - `_agent_tools_in`: ein undekodierbarer Agent wird als `tools` = `None` (fehlend → unbacked, also fail-closed für die Tool-Enforcement-Prüfung) eingetragen, kein Absturz.
  - `check_agent_description_budget`: undekodierbare Datei → Critical `agent-management.unreadable` mit Pfad (Budget nicht stillschweigend unterschätzt bestanden).
  - Regressionstest: `validate_edited_artifact.py` meldet (Exit 2, Pfad in stderr) ein eben editiertes undekodierbares `SKILL.md` — End-to-end über beide Skripte.
  - `python3 scripts/validate_skills.py` auf dem Repo: stdout+stderr byte-identisch zu develop.
- **Touched files**: `scripts/validate_skills.py`, `tests/test_validate_skills.py` (ggf. neuer Hook-Test dort oder `tests/test_validate_edited_artifact.py`)
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P2 — gen_catalog: Pfad im CatalogError, write_page textbasiert

- **Problem statement**: Decode-Fehler in `load_sources`, `load_languages`, `discover_skills`, `discover_agents` werden zu Tracebacks statt `CatalogError`/`PluginError`; `write_page` stürzt bei einer undekodierbaren Altseite ab.
- **Acceptance criteria**:
  - Die vier Lesestellen heben `CatalogError` mit Dateipfad → CLI Exit 1, Hook `PluginError` mit Pfad.
  - `write_page`: Textvergleich bleibt (kein Bytevergleich, CRLF/`core.autocrlf`-Idempotenz); Decode-Fehler der Altseite → „stale", überschreiben.
  - Catalog-Build auf dem Repo erzeugt byte-identische Seiten zu develop; zweiter Lauf berührt keine mtimes.
- **Touched files**: `scripts/docs/gen_catalog.py`, neu `tests/test_gen_catalog.py`
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P3 — validate_mission: per-file fangen, Befunde behalten, Docstring angleichen

- **Problem statement**: Decode-Fehler in Mission/Goals/Audiences/Features und in `git show` stürzen ab; der Docstring widerspricht dem Code.
- **Acceptance criteria**:
  - `check_mission`: `UnicodeDecodeError` wie `OSError` → Critical `mission.unreadable` mit Pfad.
  - Goals/Audiences: Decode-Fehler → `ids=None` **plus** Critical `mission.unreadable` für diese Datei; alle übrigen Befunde (z. B. `mission.mission-statement-empty`) und späteren Checks bleiben erhalten.
  - Feature-Index: undekodierbare Feature-Datei → Critical mit Pfad, übrige Features werden indexiert.
  - `_committed_version`: nicht dekodierbarer `git show`-Output → Critical mit `<ref>:<rel>`, kein Absturz, kein stilles Überspringen.
  - Docstring: „file unreadable" ist Exit 1 (Critical); Exit 2 bleibt für „path not found" und gescheiterten Self-Test. Code und Docstring stimmen überein (Issue-Punkt 5; Entscheidung: Critical, weil per-file Befunde erhalten bleiben und Hook/pre-commit-Semantik gleich bleibt).
  - `--self-test` und der Lauf auf `project/mission.md` unverändert.
- **Touched files**: `scripts/validate_mission.py`, `tests/test_validate_mission.py`
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

### P4 — check_prose: undekodierbare Ausgabe/Datei als CheckUnavailable

- **Problem statement**: `vale`- und `gh release view`-Output mit `text=True` sowie `--file` (fängt nur `OSError`) stürzen bei nicht-UTF-8 ab.
- **Acceptance criteria**:
  - Subprozesse dekodieren explizit UTF-8 (strikt); Decode-Fehler → `CheckUnavailable` mit Quelle (vale/gh/Dateipfad) → Exit 2. `--title` kann dadurch nie auf Exit 0 fallen.
  - `--file` mit nicht-UTF-8-Datei → Exit 2, Pfad in stderr.
  - Bestehende Tests mit injiziertem `runner` bleiben grün.
- **Touched files**: `scripts/check_prose.py`, `tests/test_check_prose.py`
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: none

## Existing installations / upgrade / rollback

not applicable — die Pakete ändern nur repo-interne Automations-Skripte unter `scripts/`, die nicht im Plugin-Payload ausgeliefert werden; keine persistierten Zustände, Konsumenten-Konfiguration, Aufrufnamen oder Artefaktpfade.

## Dependency ordering

P1 ; P2 ; P3 ; P4 — unabhängig (disjunkte Dateien), sequenziell dispatcht, damit jedes Ergebnis vor dem nächsten geprüft wird.

## Risks

- **Regression durch neue Exit-Codes** (wie in #813) → Design-Entscheidung 1 hält alle Exit-Codes; P1 trägt den Hook-Regressionstest.
- **Stiller Default** → Design-Entscheidung 2; Diff-Review explizit darauf gebrieft.
- **Ausgabe-Drift bei gültiger Eingabe** → Byte-Vergleich gegen develop für `validate_skills.py` und Catalog-Build im Verify.
- **Subagent erreicht den Worktree nicht** (bekannte Permission-Wand) → Dispatch im Vordergrund mit absoluten Pfaden; scheitert er, Fallback „draft-and-return" und Einspielen in der Hauptsession.
- Kein sicherheitsrelevanter Pfad.

## Class guard (Entscheidung vor dem PR)

- **Prädikat**: `grep -rn -E 'read_text\(|text=True' scripts --include='*.py'` — auf develop b001e8cc: 37 Zeilen in 16 Dateien (gemessen).
- **Vorschlag**: kein Guard. Begründung: Ein AST-Guard „jede Lesestelle in einem `try` mit `UnicodeDecodeError`" erzwingt keine korrekte Behandlung (der #813-Versuch hatte Catches und war trotzdem falsch: stille Defaults) und würde in 12 weiteren Dateien anschlagen. Stattdessen pro Stelle ein Verhaltens-Test; der Rest des Sweeps wird im PR unter `## Class sweep` mit Datei-Liste und Triage dokumentiert und in das abgespaltene Issue aufgenommen.

## Open questions

- Keine blockierenden.

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
- 2026-11-25 P1 dispatched to nolte-engineering:fullstack-developer — 6 Tests rot→grün, validate_skills-Ausgabe auf Repo byte-identisch; VALIDATOR_VERSION 1.1.0→1.2.0 vom Orchestrator nachgezogen (neuer Check)
- 2026-11-25 P2 dispatched to nolte-engineering:fullstack-developer — 8 Tests (7 rot→grün, 1 Idempotenz-Test per Mutante belegt), 358 generierte Seiten checksum-identisch, zweiter Lauf ohne mtime-Änderung
