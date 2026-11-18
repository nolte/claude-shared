---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "789"
classification: "spec-change"
secondary-classes: ["security"]
route: "direct"
status: draft
created: "2026-11-18"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #789 — fix(frontend-audit): reconcile the data-not-instruction rule, the trust boundary and the pin gap found in the #787 review
- **URL**: https://github.com/nolte/claude-shared/issues/789
- **Labels**: none
- **Linked items**: #787 (merged `0fa23c19`), #798 (merged `046ae49a`); `spec/frontend/third-party-audit-skills/`
- **Prior art checked**: no open PR (`gh pr list --state open` → empty); requirement artefact `project/requirements/frontend-audit-rework.md` (`U_gate = 0.8`, `τ_high = 0.8`, line 40–42) covers the rework; no roadmap item
- **Working copy**: `/home/nolte/repos/.worktrees/claude-shared/789-frontend-audit-review-findings`; created via `task worktree:add` off `7b3dda80`; ignore check `git check-ignore -q` on this path: ignored=1 (not ignored)
- **Lane**: `lane: true`, second lane of the 2026-11-18 backlog partition; returns `committed-locally`
- **Requirements gate**: met by the existing artefact at `τ_high`; the three open design points were decided by the operator on 2026-11-18 ("Alle Empfehlungen": A1, B1, C1)

## Classification

- **Primary class**: spec-change
- **Secondary class(es)**: security (finding 2, the trust boundary toward third-party skill text)
- **Rationale**: six of the seven open findings change normative text of `spec/frontend/third-party-audit-skills/`; confirmed by the operator 2026-11-18. Commit type `fix`, as the issue title states.
- **Asserted cause verified**: confirmed per finding on `7b3dda80` (the spec and skill files are unchanged since `046ae49a`):
  - 1 holds — `en.md:90-91` has no exception for the review frame; the spec names no WebFetch limitation
  - 2 holds — `SKILL.md` has no check of a listed skill against `skills-lock.json` (`SKILL.md:52` records the commit only); `allowed-tools` is a permission grant, not a restriction (`spec/claude/skill-management/en.md:157`), so the issue's first proposal can't enforce a boundary
  - 3 holds — `en.md:56` pins every install, `en.md:59` allows the unpinned marketplace plugin
  - 4 superseded — #798 removed the fallback concept (`grep -n "uncovered\|fallback" SKILL.md en.md` → 0)
  - 5 done — `grep "§Barrierefreiheit" de.md` and the bundled copy → 0
  - 6 holds — `SKILL.md:85` forbids every write outside two directories, `SKILL.md:54` writes a `mktemp` file outside the repository
  - 7 holds — §E covers fetched rule text only
  - 8 holds — `grep -i "licen" en.md` → 0. Measured 2026-11-18 via `gh api repos/<r>` and `repos/<r>/license`: `vercel-labs/agent-skills` no detected licence and no LICENSE file, README says "MIT" (`## License` at line 214); `anthropics/skills` none detected at the root, `skills/frontend-design/LICENSE.txt` exists; `vercel-labs/web-interface-guidelines` MIT with LICENSE; `microsoft/playwright-cli` Apache-2.0 with LICENSE
  - 9 holds — `en.md:11` "requirements R1–R15" beside the `[R1]`–`[R5]` references

## Scope

- **In scope**: findings 1, 2, 3, 6, 7, 8, 9 in `spec/frontend/third-party-audit-skills/{en,de}.md`, the bundled copies under `plugins/nolte-engineering/skills/frontend-audit/references/spec/`, `plugins/nolte-engineering/skills/frontend-audit/SKILL.md`, and an example where the changed header fields show.
- **Out of scope**: finding 4 (superseded) and 5 (done), noted in the PR; running the skill against a real frontend (its runtime claims stay untested, as #787 already says); `plugins/nolte-engineering/agents/webview-ui-expert.md`.

### Operator decisions (2026-11-18)

- **A1 — trust boundary**: the availability check compares each listed skill's location with `skills-lock.json`; a same-named skill from another location, or one without a lock entry, is a setup Warning in the report header, and the operator confirms in the plan step whether it runs.
- **B1 — pin gap**: the `frontend-design` marketplace plugin is explicitly exempt from the pin rule; the report header records the plugin version.
- **C1 — committing and licence**: committing `skills-lock.json` stays SHOULD; committing the installed skill files is MAY, and whoever commits them checks each skill's licence; the spec records the measured licence state with its date and names the missing LICENSE file of `vercel-labs/agent-skills`.

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome (the spec and its skill agree with each other and with the upstream text), one PR strand, no roadmap item.

## Work packages

### P1 — Spec text

- **Problem statement**: §B, §C, §E, §H and the Context paragraph of `spec/frontend/third-party-audit-skills/` contradict the upstream text, each other, or leave the trust boundary and licence unregulated.
- **Acceptance criteria**:
  1. §E exempts the review frame and the output-format section of the fetched guidelines from the setup Warning and keeps the Warning for anything that would cause a write, a tool call, or network access; it states that the skill's own fetch may return a summary, so the recorded hash is normally from a separate fetch (finding 1).
  2. §E treats rendered page content and console output collected by `playwright-cli` as foreign text under the same data-only rule (finding 7).
  3. §C requires the location comparison with `skills-lock.json` and the setup Warning plus operator confirmation of A1; §H's header lists the result (finding 2).
  4. §B exempts the marketplace plugin from the pin rule and §H's header records its version (finding 3).
  5. §B states C1 and a dated licence observation per source (finding 8).
  6. `en.md:11` no longer reads as the `[R1]`–`[R5]` references (finding 9).
  7. `de.md` carries the same changes; both bundled copies are byte-identical to their spec file after the first five lines' convention is kept (`diff` of spec against bundled copy unchanged from today's empty diff); Acceptance Criteria of the spec gain one line per new MUST.
- **Touched files / artifacts**: `spec/frontend/third-party-audit-skills/en.md`, `…/de.md`, `plugins/nolte-engineering/skills/frontend-audit/references/spec/third-party-audit-skills.md`, `…/third-party-audit-skills.de.md`
- **Specialist**: `nolte-shared:spec` (skill; authors the canonical and keeps the translation in sync)
- **Depends on**: none

### P2 — Skill procedure

- **Problem statement**: `frontend-audit/SKILL.md` records the lock commit without comparing it, contradicts itself on the temporary file, and doesn't bind the new §E and §B rules.
- **Acceptance criteria**:
  1. Step 3 compares each listed skill's location with `skills-lock.json` and step 4 shows mismatches for operator confirmation (A1); the plugin version is recorded for the marketplace `frontend-design` (B1).
  2. Step 5 and the Gotchas apply the §E exception and name the summary limitation; step 7 treats snapshots and console output as data.
  3. The hard rule at `SKILL.md:85` permits exactly the one `mktemp` file outside the repository that step 5 deletes (finding 6).
  4. `python3 scripts/validate_skills.py` exits 0 (description and token budgets hold); no rule of the spec is restated where a section reference suffices.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/frontend-audit/SKILL.md`, `plugins/nolte-engineering/skills/frontend-audit/examples/01-full-coverage-react.md` if its header shows the changed fields
- **Specialist**: `nolte-claude-dev:claude-plugin-developer` (draft-and-return: a background subagent can't write into the worktree; the orchestrating session applies the returned edits unchanged)
- **Depends on**: P1 (the skill binds the spec's final wording and section letters)

## Existing installations / upgrade / rollback

health gate: none (Claude plugin). State surfaces the installed version reads: the skill name `frontend-audit` (unchanged), the checkpoint under `.resume/frontend-audit/` (P2 adds no field a resumed run requires; an old checkpoint lacks the lock comparison, which step 3 repeats on every resume, `SKILL.md:79`), the report path (unchanged).

| Package | Upgraded state | Update health gate | What a rollback restores and what it can't | Proving check |
|---|---|---|---|---|
| P1 | spec text only, plus the bundled copy read when the target lacks the spec | none (Claude plugin) | previous wording; nothing persisted | `diff` spec vs bundled copy |
| P2 | a resumed run re-runs step 3 and gains the comparison | none (Claude plugin) + checkpoint, skill name | previous procedure; a report already written keeps its header | `git diff 7b3dda80 -- …/SKILL.md` shows `name:` and the resume phases unchanged |

## Dependency ordering

P1 → P2.

## Risks

- Security-sensitive surface: the change defines how third-party text is trusted. The diff review before `committed-locally` is briefed for security (does any new wording widen what fetched or rendered text may cause; can the lock comparison be satisfied by a same-named local skill).
- The procedure is untested against a real frontend; every new step is prose a model follows. Mitigation: none in this lane, stated in the PR.
- EN canonical gains German words by accident, or DE drifts → `task lint` (Vale, section references, spec drift hooks) and a manual parity read.
- `SKILL.md` token and description budgets are tight → `scripts/validate_skills.py` is the authority.
- develop carries the delegation guard (#800): a new sentence of the form "the `x` skill" with a non-shipped name fails `test`; third-party skills are named without that form.

## Open questions

none

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|

## Dispatch log
