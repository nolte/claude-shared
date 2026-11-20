---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "803"
classification: "bug"
secondary-classes: []
route: "direct"
status: approved
created: "2026-11-20"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #803 — fix(frontend-audit): verify the install folder name of react-best-practices and align spec, skill and example
- **URL**: https://github.com/nolte/claude-shared/issues/803
- **Labels**: bug, skills
- **Linked items**: Refs #802 (merged 5de7cd07), #789; no pull request references #803
- **Prior art checked**: `project/requirements/frontend-audit-rework.md` (`U_gate = 0.8 = τ_high`, line 42); no open pull request; no feature or roadmap item for this defect
- **Working copy**: `/home/nolte/repos/.worktrees/claude-shared/issue-803`; detect=0; created via `task worktree:add`; ignore check `git check-ignore -q` on this path: ignored=1 (exit 1, not ignored)

## Classification

- **Primary class**: bug
- **Secondary class(es)**: none
- **Rationale**: spec, skill, and example state an install folder name that an observed install contradicts, and the lock check depends on that name.
- **Asserted cause verified**: partly. Read, not run, from the `skills` CLI 1.9.0 npm tarball (`dist/_chunks/remove.mjs`):
  - **established by source reading** — the install folder is `sanitizeName(skill.name || basename(skill.path))` (line 2903), and `skill.name` is the frontmatter `name` (line 2652). For this skill that's `vercel-react-best-practices`, not `react-best-practices`.
  - **established by source reading** — the files go to `.agents/skills/<name>/` (`getCanonicalSkillsDir`, line 2813) and `.claude/skills/<name>` is a link to it in the default `symlink` mode; `--copy` writes a directory instead.
  - **established by source reading** — the lock key is `skill.name` (`addSkillToLocalLock(skill.name, …)`, `dist/cli.mjs` line 911).
  - **established by source reading** — `--skill` is matched against the frontmatter name, exactly or after lower-casing and replacing spaces and underscores (`filterSkills`, line 2782). `react-best-practices` matches no skill of `vercel-labs/agent-skills`, whose frontmatter name is `vercel-react-best-practices` (upstream `skills/react-best-practices/SKILL.md` at 5a37a632).
  - **unestablished** — what a real run prints and writes. A fresh `npx skills@1.9.0 add … -a claude-code` in a scratch repository would settle it; the run was refused by the session's permission classifier and wasn't made. Acceptance criterion 1 of the issue stays open until the operator runs it.

## Scope

- **In scope**:
  - §C of `spec/frontend/third-party-audit-skills/` (EN, DE) and both bundled copies: the claim that the install folder is `react-best-practices`, and the lock check wording
  - step 3 of `plugins/nolte-engineering/skills/frontend-audit/SKILL.md`
  - `examples/01-full-coverage-react.md`
  - the `--skill react-best-practices` install command in §B (EN, DE, both copies), in §C's parenthesis, and in `examples/02-missing-react-skill.md` (operator-approved scope extension, 2026-11-20)
- **Out of scope**: the `react-best-practices` strand label in §A, §E, §G and the references (it names the upstream folder, which is correct); the `web-design-guidelines` and `frontend-design` installs (not asserted wrong; no measurement here)

## Route

- **Decision**: direct
- **Rationale**: one coherent outcome, a single PR strand, no new roadmap item.

## Work packages

### P1 — Record the fresh install

- **Problem statement**: acceptance criterion 1 needs the output of a fresh install, and the source reading isn't a run.
- **Acceptance criteria**: the pull request carries the CLI version, the install output, the folder listing of `.claude/skills/` and `.agents/skills/`, and `skills-lock.json` for a fresh install of the React skill in a scratch repository.
- **Touched files / artifacts**: none tracked; the output goes into the pull request body.
- **Specialist**: operator (the run is refused in this session)
- **Depends on**: none

### P2 — Align the spec with the observed layout

- **Problem statement**: §B names an install command whose `--skill` value doesn't select the skill; §C says the install folder differs from the listed name and words the lock check around "a folder of that name".
- **Acceptance criteria**:
  - §B's command selects the skill by the name the CLI matches.
  - §C no longer states an install folder `react-best-practices`.
  - the lock check names the lock key, the folder, and the link by the listed name and passes for the layout P1 records.
  - EN and DE agree, and each bundled copy is byte-identical to its source (`diff -q`).
- **Touched files / artifacts**: `spec/frontend/third-party-audit-skills/en.md`, `de.md`; `plugins/nolte-engineering/skills/frontend-audit/references/spec/third-party-audit-skills.md`, `.de.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: P1 for the wording of the observation; the source reading is enough to draft

### P3 — Align the skill and its examples

- **Problem statement**: step 3 of the skill and example 01 repeat the folder claim; example 02 repeats the install command.
- **Acceptance criteria**:
  - `grep -rn 'install folder' plugins/nolte-engineering/skills/frontend-audit/` shows no claim of a folder `react-best-practices`.
  - example 01 lists the folder `vercel-react-best-practices`.
  - example 02 carries the same command as §B.
  - `task test` passes, and the skill body stays within its token cap.
- **Touched files / artifacts**: `plugins/nolte-engineering/skills/frontend-audit/SKILL.md`, `examples/01-full-coverage-react.md`, `examples/02-missing-react-skill.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P2

## Existing installations / upgrade / rollback

P2, P3: not applicable — touches no persisted state, consumer configuration key, invocation name or artifact path. health gate: none (Claude plugin).

## Dependency ordering

P1 (operator, independent) ; P2 → P3

## Risks

- The source reading diverges from a real run (a fallback not read). Mitigation: P1 before the pull request leaves draft; the PR states which claims rest on source reading.
- An older `skills` CLI may have used the upstream folder name, so existing consumer installs could carry `react-best-practices`. Mitigation: the lock check says which name it looks for, as acceptance criterion 3 asks.
- The frontend-audit `SKILL.md` is near its token cap. Mitigation: `scripts/validate_skills.py` is the token authority; step 3 gets shorter, not longer.

## Open questions

- none blocking the draft. P1's result decides whether the pull request can claim acceptance criterion 1.

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| `--skill react-best-practices` selects no skill in `skills` 1.9.0 | acquire, source reading | fixed directly (P2, P3) | `filterSkills`, `dist/_chunks/remove.mjs` line 2782; unrun | #803 |
| §B said the CLI links `.claude/skills/<name>` into `.agents/skills/<name>/` by default; with one target folder the default is a copy | diff review @ b7b53e6e | fixed directly (§B, EN, DE, copies) | `defaultInstallMode`, `dist/_chunks/remove.mjs` line 5606; `docs/api.md` line 118; unrun | #803 |
| "only with `--copy`" too strong: a failed link falls back to a copy | diff review @ b7b53e6e | fixed directly (same sentence) | `dist/_chunks/remove.mjs` lines 2974–2984 | #803 |
| "names the folder after the frontmatter name" imprecise (sanitised name, `--rename`) | diff review @ b7b53e6e | fixed directly ("derives … from") | `dist/_chunks/remove.mjs` line 2903 | #803 |
| `@<ref>` parses as a ref only for a version-shaped tag or a 40-character SHA; another tag name becomes a skill filter | diff review @ b7b53e6e | filed | `isVersionPin`, `dist/_chunks/remove.mjs` lines 770–772, 895–905; unrun | follow-up |

## Dispatch log

2026-11-20 P2 dispatched to nolte-shared:spec — §B and §C updated in EN and DE, copies byte-identical
2026-11-20 P3 dispatched to nolte-claude-dev:claude-plugin-developer — step 3, examples 01 and 02 aligned; `validate_skills.py` exit 0
2026-11-20 P1 not run — operator-owned, refused in this session
