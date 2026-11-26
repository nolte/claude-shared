---
artifact-type: issue-orchestration-analysis
repo: nolte/claude-shared
issue: "816"
classification: bug
secondary-classes: []
route: direct
status: approved
created: 2026-11-26
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #816 — fix(scripts): fail closed on malformed config shape in check_spec_inheritance and validate_schemas
- **URL**: https://github.com/nolte/claude-shared/issues/816
- **Labels**: bug
- **Linked items**: Refs #814 (geschlossen via #817, 137fa2e3), Refs #813 (Revert 51d36428)
- **Prior art checked**: #817 (gemergt, deckt nur die Decode-Klasse von #814 ab); keine offenen PRs (`gh pr list --state open` leer); kein `project/features/`-Eintrag.
- **Working copy**: /home/nolte/repos/.worktrees/claude-shared/fix-fail-closed-config-shape; detect=0; created via `task worktree:add`; ignore check `git check-ignore -q` on this path: ignored=1
- **Trust**: Issue-Body und beide Kommentare von `nolte` (association `owner`) → trusted.
- **Requirements gate**: Kein Artefakt unter `project/requirements/`. **Operator-Override** (2026-11-26): Die Acceptance-Sektion des Issues ist ausreichend konkret.

## Classification

- **Primary class**: bug
- **Secondary class(es)**: none
- **Rationale**: Fehlerhafter Config-Input wird zu einem stillen Default (exit 0) oder zu einer unbehandelten Exception statt zu einem Befund mit Dateiname.
- **Asserted cause verified**: Gegen develop 29184a54 reproduziert (Fixtures im Scratchpad, Python 3.14):
  - `own_plugin_name`: plugin.json `{bad` → exit 0, Zyklus-Check still aus (confirmed); Root `[1]` → `AttributeError`, exit 1 (confirmed).
  - `hub_canonical_lang`: Hub-Config `a: [` → exit 0, still `"en"` (confirmed); Root `- a` → `AttributeError` (confirmed).
  - `run()`: `canonical_language:` leer → exit 0, 0 Befunde (confirmed); `spec_root: 1` → `TypeError` (confirmed).
  - `validate_schemas` mappings: `null` → `TypeError` (confirmed); `/tmp/*.yml` → `NotImplementedError` (confirmed); `../*.yml` → **refuted as stated**: kein `ValueError` unter 3.14; stattdessen bindet das Muster still `../x.yml` außerhalb des Roots (gemessen: Befund `../x.yml: bound schema … does not exist`). Defekt besteht in schärferer Form (Root-Escape).
  - Kommentar 1: `validate_skills._read_utf8` mit Verzeichnis als SKILL.md → `IsADirectoryError`-Traceback (confirmed); `gen_catalog._read_utf8` desgl. (confirmed); `load_sources` mit Listen-Root → `AttributeError` ohne Dateiname (confirmed).

## Scope

- **In scope**: Issue-Body (3 Stellen-Gruppen) + Kommentar 1 (2 Stellen-Gruppen), siehe P1–P4.
- **Out of scope**: Kommentar 2 (Decode-Rest von #814, 13 Zeilen in 7 Dateien) — andere Defektklasse; wird nach Operator-Entscheidung als eigenes Issue angelegt.

## Route

- **Decision**: direct
- **Rationale**: Ein Ergebnis (fail closed bei fehlerhafter Config-Form), ein PR-Strang, kein Roadmap-Item.

## Work packages

### P1 — check_spec_inheritance: Hub-/Plugin-/Consumer-Config fail closed

- **Problem statement**: `own_plugin_name` und `hub_canonical_lang` fallen bei Parse-Fehler still zurück und crashen bei Nicht-Mapping-Root; nicht-String `name`/`canonical_language` ungeprüft. `run()` validiert `canonical_language` und `spec_root` der Consumer-Config nicht.
- **Acceptance criteria**: Jeder Fall endet als Critical-Befund (exit 1) oder exit 2 (bestehender Code), mit Dateipfad und betroffenem Schlüssel; nie exit 0, nie Traceback. `canonical_language` muss nicht-leerer String sein, `spec_root` nicht-leerer relativer String. Fehlende Datei/fehlender Schlüssel behalten das bisherige Default-Verhalten. Je Fall ein Test in `tests/test_spec_inheritance.py`, der gegen develop rot ist.
- **Touched files / artifacts**: scripts/check_spec_inheritance.py, tests/test_spec_inheritance.py
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P2 — validate_schemas: `mappings`-Einträge validieren

- **Problem statement**: Einträge in `mappings` werden ungeprüft an `Path /` und `root.glob` gereicht.
- **Acceptance criteria**: Muster muss nicht-leerer relativer String ohne `..`-Segment sein, Schema-Pfad nicht-leerer relativer String, der innerhalb von root auflöst; sonst eine `failures`-Zeile mit `.schemas-config.yaml` und dem Muster/Schlüssel → exit 1 (bestehend). Tests für `null`, absolutes Muster, `../`-Muster, nicht-String-Schlüssel; rot gegen develop.
- **Touched files / artifacts**: scripts/validate_schemas.py, tests/test_validate_schemas.py
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P3 — validate_skills: `_read_utf8` fängt `OSError`

- **Problem statement**: Nur `UnicodeDecodeError` wird gefangen; ein Verzeichnis/eine unlesbare Datei endet als Traceback.
- **Acceptance criteria**: `OSError` → Critical-Befund `<kind>-management.unreadable` mit Pfad (analog `mission.unreadable`), übrige Artefakte werden weiter geprüft, exit 1. Test rot gegen develop.
- **Touched files / artifacts**: scripts/validate_skills.py, tests/test_validate_skills.py
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P4 — gen_catalog: `_read_utf8` + `load_sources`-Shape

- **Problem statement**: `_read_utf8` fängt kein `OSError`; `load_sources` prüft nicht, dass der Top-Level ein Mapping ist.
- **Acceptance criteria**: Beides → `CatalogError` mit Dateipfad. Tests rot gegen develop.
- **Touched files / artifacts**: scripts/docs/gen_catalog.py, tests/test_gen_catalog.py
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

## Existing installations / upgrade / rollback

health gate: none (Claude-Plugin; betroffen sind nur Repo-interne Validator-Skripte). State surfaces: keine — Exit-Code-Vertrag bleibt (0/1/2 wie bisher). Caller-Grep (#816 Acceptance): `scripts/validate_edited_artifact.py` wertet nur `returncode == 1` von `validate_skills.py` aus; P3 erzeugt exit 1 → kompatibel. `Taskfile.yml:211/233/245/287` und `mkdocs.yml:24` werten jeden Nicht-Null-Code als Fehler. Kein neuer Exit-Code.

## Dependency ordering

P1–P4 unabhängig (disjunkte Dateien); ein gemeinsamer Dispatch.

## Class sweep (defect-class-guards)

- **Predicate**: `git grep -n -E 'yaml\.safe_load\(|json\.loads?\(' -- 'scripts/*.py' 'scripts/**/*.py'` auf develop 29184a54 → 22 Zeilen in 12 Dateien.
- **Remainder triage**: established in operation 6 (verify).
- **Guard**: Entscheidung in operation 6.

## Risks

- Bisher still tolerierte, aber fehlerhafte Configs in Consumer-Repos werden rot. Beabsichtigt (fail closed).

## Open questions

- none

## Dispatch log

| Package | Specialist | Result | Head SHA |
|---|---|---|---|

## Findings

| Source | Finding | Triage | Reviewed head SHA |
|---|---|---|---|
