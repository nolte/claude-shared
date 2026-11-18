---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "782"
classification: "infra"
secondary-classes: []
route: "direct"
status: draft
created: "2026-11-18"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #782 — guard: fail when a skill, agent or spec delegates to a skill that doesn't exist
- **URL**: https://github.com/nolte/claude-shared/issues/782
- **Labels**: bug, skills
- **Linked items**: #772, #778 (closed by #783, `247ae8de`: the instance fix); `spec/project/defect-class-guards/`
- **Prior art checked**: no open PR (`gh pr list --state open` → empty); no `project/features/` or roadmap item for a delegation guard; `tests/test_spec_action_pins.py` is the precedent shape (detector, positive control, corpus test)
- **Working copy**: `/home/nolte/repos/.worktrees/claude-shared/782-delegation-target-guard`; created via `task worktree:add`; ignore check `git check-ignore -q` on this path: ignored=1 (not ignored)
- **Lane**: `lane: true`, handed over by `issue-backlog-partition` (survey 2026-11-18); returns `committed-locally`
- **Requirements gate**: operator override, 2026-11-18 ("2 = override"): the three acceptance criteria in the issue body are explicit and testable; no `requirements-elicit` run

## Classification

- **Primary class**: infra
- **Secondary class(es)**: none
- **Rationale**: a new mechanical guard in the repository's test tooling; the defect instance is already fixed. Not a CI failure, so no hand-over to `workflow-health-triage`. Confirmed by the operator 2026-11-18 ("3 = infra").
- **Asserted cause verified**: confirmed on `046ae49a`: no delegation-target check among the `check_*` functions of `scripts/validate_skills.py`, no built-in list tracked (`git ls-files | grep -iE 'built-?in'` → empty), no matching test under `tests/`. The issue's count of 13 sites is unestablished (the sites are fixed; re-measuring would need `git grep` at `247ae8de^`, not made because nothing rests on the number).

## Scope

- **In scope** (operator, 2026-11-18 "1 Ja"): the three acceptance criteria, plus cleaning up what the new guard finds on develop so it lands green: real dead references are corrected, false positives are excluded by a more precise pattern, never by an allowlist of names.
- **Out of scope**: wiring the check into `scripts/validate_skills.py` (pytest already runs under `task test` and CI); validating agent names (`subagent_type`); references outside the five roots named in AC1.

### Measured baseline (develop `046ae49a`)

The two prose forms of AC1 match 61 distinct names; `Skill(skill="<name>")` matches none today. Eight names resolve to no shipped skill:

| Name | Hits | Site | Verdict |
|---|---|---|---|
| `fewer-permission-prompts` | 8 | several | harness built-in → built-in list |
| `security-review` | 5 | several | harness built-in → built-in list |
| `update-config` | 1 | — | harness built-in → built-in list |
| `release-skill-layer` | 4 | `spec/project/release-artifact/{en,de}.md:8,16`, `spec/project/sprint/de.md:84` | false positive: plural "skills"/"Skills" → word boundary in the pattern |
| `nolte-engineering` | 2 | `spec/project/capability-maturity-assessment/de.md:16`, `spec/project/kpi-definition-process/de.md:14` | a plugin name used as qualifier, not a skill → reword |
| `sast-runner` | 1 | `spec/project/code-security-audit/de.md:27` | announced future skill ("künftiger") → reword |
| `spec-anchor-lint` | 2 | `spec/project/spec-driven-development/de.md:37` | announced future skill → reword |
| `tech-stack-audit` | 1 | `spec/portfolio/tech-stack/de.md:150` | a skill the spec says must not exist → reword |

The three "reword" rows are mentions, not delegations. Detecting "future" or "never" by regex is out (free-text negation patterns misfire); the sentence is reworded so the name no longer stands in a delegation form.

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (a guard and a green corpus), one PR strand, no roadmap item.

## Work packages

### P1 — Delegation-target guard and built-in list

- **Problem statement**: nothing fails when a skill, agent or spec names a skill that neither the repository ships nor the harness provides.
- **Acceptance criteria**:
  1. `tests/test_delegation_targets.py` enumerates the three reference forms (`Skill(skill="<name>")`, "the `<name>` skill", "`<name>`-Skill") across `skills/`, `plugins/*/skills/`, `agents/`, `plugins/*/agents/`, `spec/` and fails, naming `file:line` and the name, for one that is neither a shipped skill directory (`skills/*/SKILL.md`, `plugins/*/skills/*/SKILL.md`) nor in the built-in list. A `<plugin>:<name>` reference is resolved by its name part.
  2. The built-in list is one committed text file (`tests/data/harness-builtin-skills.txt`, one name per line) whose header comment says how to refresh it and when it was last refreshed.
  3. A detector test feeds a reference to a non-existent skill in each of the three forms and asserts it is flagged, and feeds a shipped and a built-in name and asserts they pass; the plural form ("`x` skills") is asserted not to match.
  4. Mutation control, recorded for the PR: a deliberately introduced dead reference in a real file makes `python3 -m pytest tests/test_delegation_targets.py` fail; reverted afterwards.
- **Touched files / artifacts**: `tests/test_delegation_targets.py` (new), `tests/data/harness-builtin-skills.txt` (new)
- **Specialist**: no matching specialised agent — generalist remediation. The match by responsibility is `nolte-engineering:fullstack-developer`, but the session's agent inventory carries no `nolte-engineering` agent type (only `nolte-shared`, `nolte-claude-dev`, `nolte-planning`), so it could not be dispatched; recorded as unavailability, not as a portfolio gap.
- **Depends on**: none

### P2 — Reword the mentions the guard flags

- **Problem statement**: four German spec passages name a plugin, a future skill, or a forbidden skill in a delegation form.
- **Acceptance criteria**: the corpus test of P1 passes on the branch with no name added to the built-in list beyond real harness built-ins; meaning of each passage unchanged; EN canonical untouched unless it matches too; `task lint` green on the touched files.
- **Touched files / artifacts**: `spec/project/capability-maturity-assessment/de.md`, `spec/project/kpi-definition-process/de.md`, `spec/project/code-security-audit/de.md`, `spec/project/spec-driven-development/de.md`, `spec/portfolio/tech-stack/de.md` — plus whatever else P1's final pattern reports (measured, not assumed)
- **Specialist**: no matching specialised agent — generalist remediation (translation-only rewording of five sentences; `spec` owns authoring and translation sync, and its drift check is run afterwards)
- **Depends on**: P1 (the final pattern decides the hit list)

## Existing installations / upgrade / rollback

- P1: not applicable — touches no persisted state, consumer configuration key, invocation name or artifact path (`tests/` is not shipped in any plugin payload).
- P2: not applicable — touches no persisted state, consumer configuration key, invocation name or artifact path (prose in translated specs only).

## Dependency ordering

P1 → P2.

## Risks

- Prose patterns over-match (a mention is not a delegation) → the pattern stays the three literal forms from AC1 with word boundaries; every baseline hit is classified above, and new hits are classified before any rewording.
- The built-in list drifts with harness releases → that is the point of AC2: the drift shows as a red test and a reviewed one-line diff; the header names the refresh procedure.
- The built-in list is taken from one session's skill listing → only harness built-ins go in, never third-party or `anthropic-skills:` plugin skills; the header says which session version it came from.
- No security-sensitive path is touched.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| "The `x` skill" (sentence-initial) unchecked, 15 corpus lines | diff review @ 04307a74 | fixed directly (d07ba5df) | mutation "The `review` skill runs first." in `skills/spec/SKILL.md` → `1 failed, 3 passed` | — |
| hollow check summed over all forms | diff review @ 04307a74 | fixed directly (d07ba5df): per-form assertion for both prose forms | per-form counts {0: 0, 1: 247, 2: 108} | — |
| a missing root goes unnoticed | diff review @ 04307a74 | fixed directly (d07ba5df) | reviewer's scratch copy without `agents/`: `4 passed` | — |
| indented comment in the built-in list read as a name | diff review @ 04307a74 | fixed directly (d07ba5df) | code reading, `line.startswith("#")` | — |
| refresh note lets user/project skills into the list | diff review @ 04307a74 | fixed directly (d07ba5df) | — | — |
| guard misses forms beyond the three in AC1; replay at `247ae8de^` reports 5 lines in 3 files only | diff review @ 04307a74 | filed (operator decision 2026-11-18) | widened pattern: 326 refs, 11 unresolved, none a dead delegation | #799 |
| built-ins referenced only in unchecked forms (`code-review` ×21) | diff review @ 04307a74 | filed | reviewer's count via `references()` | #799 |
| wrong plugin prefix passes | diff review @ 04307a74 | filed | scratch mutation `nolte-shared:quality-gate` → `4 passed` | #799 |
| German rewordings sidestep rather than satisfy the guard; EN counterparts pass only through the article gap | diff review @ 04307a74 | filed (needs the naming convention) | see #799 | #799 |

## Dispatch log

2026-11-18 P1 generalist — `tests/test_delegation_targets.py` + `tests/data/harness-builtin-skills.txt`; first corpus run red on exactly the six predicted sites (`tech-stack-audit`, `nolte-engineering` ×2, `sast-runner`, `spec-anchor-lint` ×2), the plural false positive gone.
2026-11-18 P2 generalist — six German sentences reworded in five spec translations; guard 4 passed. Mutation control: appended "Hand it to the `review` skill." to `skills/pull-request-merge/SKILL.md` → `1 failed, 3 passed`, reporting `skills/pull-request-merge/SKILL.md:193: \`review\``; reverted.
2026-11-18 verify — `python3 scripts/validate_skills.py` rc 0, `python3 scripts/validate_mission.py` rc 0, `python3 -m pytest tests -q` → 1690 passed, 21 skipped; pre-commit on the touched files green (markdownlint via `npx markdownlint-cli@0.50.0`: 396 output lines on develop and on the lane, unchanged). `task test` itself did not run: the worktree's remote Taskfile include is untrusted, so its four commands were run directly.
