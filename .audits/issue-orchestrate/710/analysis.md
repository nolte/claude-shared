---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "710"
classification: "bug"
secondary-classes: []
route: "direct"
status: approved
created: "2026-11-11"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #710 — capability-reach-audit: an ambiguous section locator counts as a change and can carry a lowered bar
- **URL**: https://github.com/nolte/claude-shared/issues/710
- **Labels**: bug
- **Linked items**: #708/#711 (Fundstelle, gemergt 19049c06), keine offene PR zu #710
- **Prior art checked**: project/requirements/reach-probe-section-anchor.md (U_gate 0.8, R4 Ambiguität), `test_674_locator_turned_ambiguous_is_stale_naming_it`, `test_674_R4_re_derivation_onto_an_ambiguous_locator_cannot_anchor`

## Classification

- **Primary class**: bug
- **Rationale**: Ein Weakening (gesenktes `expected`) liest `clean`/Exit 0, nur weil der alte Locator mehrdeutig wurde.
- **Asserted cause verified**: confirmed. Repro (scratch test, Worktree): Sequenz R0→C1(Duplikat `### 3.1` + `## 5`)→C2(re-derive auf `heading 5`, expected 3→1) liefert Exit 0, `clean`; ohne Duplikat identische Sequenz → Exit 4, `weakened: re-baselined without a declaration change`. Ursache: `reach_audit.py:2004` setzt `changed = bool(_section_mismatches(baseline…))`, und `_section_mismatches` (`:1391-1403`) meldet `is ambiguous` als Mismatch; `_unchanged_in` (`:1941`) analog.

## Scope

- **In scope**: Option 1 des Issues — für die Frage „hat sich der verankerte Inhalt geändert" zählt ein mehrdeutiger Locator nur dann als Änderung, wenn keiner der Treffer den aufgezeichneten Digest trägt. Gilt für alle Change-Fragen (`_prior_anchor` changed, `_unchanged_in`, Rename-Pfad `:2270`, Anker-Wechsel `:2285`).
- **Out of scope**: Stale-Meldung an HEAD (`:2749`) bleibt strikt (Ambiguität = stale, gewollt); Gültigkeitsprüfungen eines Ankers (`:1993` Recording-Beweis, `:2257` neuer Anker) bleiben strikt (Ambiguität kann nicht verankern, R4).

## Route

- **Decision**: direct
- **Rationale**: Ein Ergebnis, ein PR-Strang, kein Roadmap-Item.

## Work packages

### P1 — Change-Prädikat trennen von Gültigkeit

- **Problem statement**: `_section_mismatches` beantwortet zwei Fragen (Anker gültig? / Inhalt geändert?). Für die zweite einen Helfer einführen (z. B. `_sections_changed`: wahr, wenn ein Locator keinen Treffer mit seinem Digest hat) und an den Change-Stellen nutzen.
- **Acceptance criteria**: Issue-Sequenz liest `weakened` (Exit 4) am selben Pfad und über Rename; ehrliche Re-Derivation nach echter Änderung von 3.1 (mit Duplikat) bleibt `clean`; `test_674_locator_turned_ambiguous_is_stale_naming_it` und R4-Test bleiben grün; komplette Suite grün.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/capability-reach-audit/scripts/reach_audit.py`, `tests/test_reach_audit.py`, ggf. `references/runner-exit-codes.md`
- **Specialist**: nolte-engineering:fullstack-developer (Fix + Tests); Verifikation per Mutationsprobe (Fix zurückdrehen → neue Tests rot)
- **Depends on**: none

## Dependency ordering

P1

## Risks

- Andere Tests verlassen sich auf „ambiguous = changed" (z. B. Heilung über Ambiguität) → volle Suite + Mutation.
- Kein security-sensitiver Pfad im Sinne Auth/Secrets; trotzdem Integritäts-Gate → `security-review` auf den Worktree-Diff.

## Open questions

- Option 1 (Fix) vs. Option 2 (als Limit dokumentieren): Empfehlung Option 1.

## Dispatch log

- P1 → nolte-engineering:fullstack-developer: `_sections_changed` (reach_audit.py:1407) an 4 Change-Stellen (1964, 2030, 2301, 2316); strikt bleiben 2019, 2288, 2780. 4 Tests `test_710_*` (inkl. Ambiguität am Recording, Rename-Variante). Orchestrator verifiziert: `tests/` 930 passed, 3 skipped; Mutation (Helfer → `bool(_section_mismatches)`) → 4 failed, 4 passed (`-k "710 or ambiguous"`). runner-exit-codes.md Z. 126 vom Orchestrator um die Change-Regel ergänzt.
