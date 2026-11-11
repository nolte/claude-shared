---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "709"
classification: "bug"
secondary-classes: []
route: "direct"
status: approved
created: "2026-11-11"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #709 — capability-reach-audit: runner hardening candidates from the #688 review
- **URL**: https://github.com/nolte/claude-shared/issues/709
- **Labels**: bug
- **Linked items**: #688/#707 (Ursprung), #701/#703/#705/#711 (Merge-Fixes seitdem); offene PR #713 (#710, gleiche Datei, anderer Bereich)
- **Prior art checked**: project/requirements/capability-reach-executor.md (U_gate 0.80)

## Classification

- **Primary class**: bug
- **Rationale**: Ein False Positive (K5), falsche/fehlende Findings (K3c, K4) und Robustheitslücken (K1, K2) im Runner.
- **Asserted cause verified**: gemessen auf e637bef1 (Scratch-Tests, gelöscht):
  - K1 confirmed: `Git.run` `reach_audit.py:692` ohne `--no-replace-objects`, Env geerbt.
  - K2 confirmed: `tree_entries` `:835-836` gibt `[]` bei rc≠0.
  - K3 teilweise refuted: 3a/3b/3d/3e lesen weakened (seit #703). 3c confirmed: Probe nur im Merge angelegt → exit 0, `uncommitted`, Ursache `probe_changes` `:1503` (baseline None) → `detect_change` `:2623`.
  - K4 confirmed: Merge stellt Vor-Baseline-Version her (Merge-Ergebnis = old-Parent) → weakened mit Grund „probe file has uncommitted changes“; `_merges_changing` `:1731` findet den Merge nicht, Fallback `:1519` setzt dirty.
  - K5 confirmed: Backport über Rename, Rückmerge byte-identisch für die Probe → exit 4, unlisted write; `_unlisted_write` `:1629/:1657`.

## Scope

- **In scope**: K1–K5, je mit Regressionstest und Mutationsprobe (Operator-Entscheid: alles in einem PR).
- **Out of scope**: 3a/3b/3d/3e (bereits korrekt; Messung im PR genannt).

## Route

- **Decision**: direct — ein Ergebnis (Runner-Härtung), ein PR-Strang, keine Roadmap.

## Work packages

### P1 — git-Aufrufe gegen Replace-Objects, Grafts und geerbte Umgebung
- **AC**: Ein `refs/replace/*` auf einen Probe-Blob/Commit ändert das Urteil nicht; `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE`/`GIT_OBJECT_DIRECTORY`/`GIT_ALTERNATE_OBJECT_DIRECTORIES` aus der Umgebung ändern das gelesene Repo nicht; Grafts-Verhalten gemessen und entweder neutralisiert oder als gemessenes Limit dokumentiert.
- **Files**: reach_audit.py (`Git.run`), tests
- **Specialist**: nolte-engineering:fullstack-developer
- **Depends on**: none

### P2 — `tree_entries` meldet Fehler
- **AC**: rc≠0 von `ls-tree` → `AuditError` (exit 2); Test erzwingt den Fehler.
- **Specialist**: nolte-engineering:fullstack-developer — **Depends on**: none

### P3 — Probe nur in einem Merge angelegt
- **AC**: Fall 3c liest `weakened`, exit 4, mit einer Origin-Begründung, die den Merge nennt (Linie #702/#705); kein `uncommitted` für eine committete Probe.
- **Specialist**: nolte-engineering:fullstack-developer — **Depends on**: none

### P4 — Grund nennt den Merge statt „uncommitted changes“
- **AC**: 4a/4b lesen weakened mit „probe changed in merge M …“; „uncommitted changes“ nur bei echtem Dirty-Tree (Test).
- **Specialist**: nolte-engineering:fullstack-developer — **Depends on**: P3 (gleicher Pfad in `probe_changes`)

### P5 — Backport über Rename kein unlisted write
- **AC**: 5a–5c lesen nach dem Rückmerge clean (Write nur über einen Merge-Parent erreichbar, Merge ändert die Probe ggü. First-Parent nicht); 5d bleibt weakened (Linie #701), ohne die ungenaue Unlisted-Write-Begründung; alle bestehenden Unlisted-Write-/Laundering-Tests bleiben grün.
- **Specialist**: nolte-engineering:fullstack-developer — **Depends on**: P4


### P6 — F1: Rebaseline-Vorgänger aus der Elternschaft statt aus der Walk-Reihenfolge (Review-Fund, Altlücke)
- **AC**: R0 → side ändert nur approval (Anker A0) → main re-derive R1 (A1) → `merge -s ours side` → L senkt `expected` → weakened; ehrliche Ketten bleiben clean.
- **Specialist**: nolte-engineering:fullstack-developer — **Depends on**: P5

### P7 — F2: Clean-Filter aus Config/.git/config versteckt ungespeicherte Senkung
### P8 — F3: assume-unchanged/skip-worktree versteckt ungespeicherte Senkung
- **AC (P7+P8)**: `is_dirty` vergleicht Arbeitsbaum-Bytes mit `HEAD:<path>` ohne Filter/Index-Flags; beide Varianten lesen weakened.
- **Specialist**: nolte-engineering:fullstack-developer — **Depends on**: P1

## Dependency ordering

P1 ; P2 ; P3 → P4 → P5 (eine Dispatch-Einheit, gleiche Datei)

## Risks

- P5 lockert eine Integritätsregel: Gefahr, ein echtes Laundering über einen Merge-Parent zu öffnen → adversariale Tests (Merge-Parent mit gesenktem Bar, der Merge übernimmt ihn) müssen weakened bleiben; Pre-Merge-Review.
- Konflikt mit #713 (gleiche Datei, andere Funktionen) → nach Merge von #713 rebasen.

## Open questions

none

## Dispatch log

- P1–P5 → fullstack-developer: 955 passed, 3 skipped (Orchestrator nachgeprüft); Mutation je Paket rot. Adversariales Review (general-purpose): keine Regression durch den Diff, drei Altlücken F1–F3 → Operator: alle in #709 (P6–P8).
