# Group pre-analysis: 2026-11-24-frontend-audit-install-run

> Run-scoped artifact. Committed on the integration branch, removed with a fix-forward
> `git rm` before the bundle merges. It must never reach the default branch, and it must
> never be hidden behind a `.gitignore` entry.

## Scope of this analysis

**Research question:** What does a real `skills` CLI 1.9.0 install produce for the React skill (folder, copy or link, lock key) and for an `@<ref>` that isn't version-shaped, and which text in the spec, its bundled copies, the skill, and the examples disagrees with it?

**The group's single logical change, in one sentence:** Settle the frontend-audit third-party install rules — the install folder of the React skill and the `@<ref>` pin form — with one recorded `npx skills add` run in a scratch repository, and align the spec, its bundled copies, and the skill to what the run shows.

**Out of scope:** the multi-target link layout (`.agents/skills/` + link) stays "observed once, read from source" (the run used `-a claude-code` only, the form §B prescribes); a version-shaped tag (`v1.2.3`) stays unestablished — `vercel-labs/agent-skills` carries none (`gh api repos/vercel-labs/agent-skills/tags` → only `agent-skills-<sha>` names); the `computedHash` open question (§ open questions, en.md:184).

**Tier:** 2 — one repository, no published contract beyond the spec's own text.

## Members

| Issue | Class | Admitting predicate | Evidence |
|---|---|---|---|
| #803 | bug | shared touch surface | PR #809 (9c504dbc) touched `spec/frontend/third-party-audit-skills/{en,de}.md`, both bundled copies and `frontend-audit/SKILL.md`; only AC1 (fresh install) open per operator comment 2026-11-20 |
| #808 | bug | shared touch surface + dependency chain | same §B lines (`en.md:57-59`, `de.md:57-59`, bundled `:57-59`); body: "Found by the diff review of the fix for #803" |

Re-checked live 2026-11-25: both OPEN, author `nolte` (trusted), labels `bug,skills`; partition record holds.

**Dependency ordering:** #803 → #808 (one measurement serves both; #808 edits the §B lines #803's text sits next to).

**Shared touch surface:** `spec/frontend/third-party-audit-skills/{en,de}.md`, `plugins/nolte-engineering/skills/frontend-audit/references/spec/third-party-audit-skills{,.de}.md`.

## Measurement (Research, run before the plan)

Scratch repos under the session scratchpad (outside the repository), `git init`, Node v22.22.3, `npx -y skills@1.9.0` (`npm view skills version` → 1.9.0, latest). Tag `agent-skills-dd089a8c…` → commit `dd089a8c` (2026-08-21); default branch `main` → `5a37a632`. `web-design-guidelines/SKILL.md` differs between them (sha256 `f4647ca8…` at the tag, `360b1240…` on main), so content identifies what was installed.

| Run | Command (`… -a claude-code -y`) | Exit | Installed | `skills-lock.json` entry |
|---|---|---|---|---|
| 1 | `add vercel-labs/agent-skills@agent-skills-dd089a8c… --skill vercel-react-best-practices` | 0 | `.claude/skills/vercel-react-best-practices/` **directory (copied)**, no `.agents/` | key `vercel-react-best-practices`, `commit: 5a37a632` (main), **no `ref`**, version 2 |
| 2 | `add vercel-labs/agent-skills@agent-skills-dd089a8c… --skill web-design-guidelines` | 0 | content = **main** (`360b1240…`) | `commit: 5a37a632`, **no `ref`** |
| 3 | `add vercel-labs/agent-skills@dd089a8c<40-char SHA> --skill web-design-guidelines` | 0 | content = **tag** (`f4647ca8…`) | `ref: dd089a8c…`, `commit: dd089a8c…` |
| 4 | `add vercel-labs/agent-skills#agent-skills-dd089a8c… --skill web-design-guidelines` | 0 | content = **tag** | `ref: agent-skills-dd089a8c…`, `commit: dd089a8c…` |
| 5 | `add vercel-labs/agent-skills@agent-skills-dd089a8c… --skill react-best-practices` | 1 | nothing | none; output `[SKILLS_NO_MATCHING_SKILLS] No matching skills found for: react-best-practices, agent-skills-dd089a8c…` |
| 6 | `add vercel-labs/agent-skills#dd089a8c<full SHA> --skill web-design-guidelines` | 0 | content = **tag** | `ref: dd089a8c…`, `commit: dd089a8c…` |
| 7 | `add vercel-labs/agent-skills#main --skill web-design-guidelines` | 0 | content = **main** | `ref: main`, `commit: 5a37a632` |
| 8 | `add vercel-labs/agent-skills --skill web-design-guidelines` (no ref) | 0 | content = **main** | `ref: null`, `commit: 5a37a632` |
| 9 | `add vercel-labs/agent-skills --skill react-best-practices` (no ref) | 1 | nothing | `[SKILLS_NO_MATCHING_SKILLS] No matching skills found for: react-best-practices` |
| 10 | `add vercel-labs/agent-skills@v1.0.0 --skill web-design-guidelines` | 1 | nothing | `Source: … @ v1.0.0` (read as ref), `[SKILLS_GIT_CLONE_FAILED]` (no such tag) |

Runs 6–10 were added after the diff review at 4d51738c to settle its findings 1, 2, 7, and 9.

Conclusions: (#803) folder and lock key are the frontmatter name; `-a claude-code` alone copies into `.claude/skills/<name>/`; `--skill react-best-practices` matches nothing — the claims of #809 hold for a run. (#808) `@<non-version-tag>` is taken as an extra skill filter (run 5 lists it as a skill name); together with `--skill` the install comes from the default branch, unpinned, exit 0, and the lock entry still carries a `commit` (of the default branch) but **no `ref`**. `#<ref>` and `@<full SHA>` pin, and the lock then records `ref`. So a lock entry without `commit` doesn't result (AC3 of #808 in its literal form doesn't apply); the detectable sign of an unpinned install is a missing `ref`.

## Mode decision

**Mode:** A — single strand.

**Reason:** both members are text alignments to one measurement already made; no member's acceptance is uncertain or externally dependent.

**Working copy:** `/home/nolte/repos/.worktrees/claude-shared/frontend-audit-install-run`; created via `task worktree:add` off `origin/develop` 72cba52c. Plan approved by the operator 2026-11-25 ("ja, freigegeben, umsetzen").

## Structural finding

**Cluster shape:** symptom cluster.

**Root cause or defect class:** claims about a third-party CLI's behaviour derived from reading its source instead of running it (#809 couldn't run it).

**Process finding:** none new — #809 already chose provenance marking over a guard (a guard would need a network install of third-party code in CI); this group converts those provenance marks to "established by a run" where the run covers them.

**Preventive change:** keep the provenance-marking rule; no guard.

**Recurrence fed to the portfolio loop:** not fed — first recurrence of "source-read CLI claim" within one spec, closed by the run.

## Plan approval

**Authorised by:** `2026-11-24-frontend-audit-install-run/plan-approval`, covering the members, mode, and order above.

**Group requirement artifact:** not applicable — symptom cluster, per-member elicitation.

## Completeness matrix

| Member | Spec (`spec/frontend/third-party-audit-skills/{en,de}.md`) | Bundled spec copies | Skill (`frontend-audit/SKILL.md`) | Examples | Tests | Generated index (`spec/README.md`, docs catalog) |
|---|---|---|---|---|---|---|
| #803 | §B `:62` and §C `:70`: replace "read from the source … unestablished for a run" with "established by a run of `skills` 1.9.0 on 2026-11-25" for the single-target copy and the frontmatter-name folder/lock key; `--skill react-best-practices` matches nothing (exit 1); link layout stays as observed once. check: `git grep -n 'unestablished for a run' spec/frontend/third-party-audit-skills` → only the link-layout clause | same edits; check: `cmp` of each copy against `en.md`/`de.md` → identical | not applicable — step 3 already states the frontmatter-name lookup (`SKILL.md:52`), the run confirms it | `01-full-coverage-react.md`: not applicable — `:13-16` already names `vercel-react-best-practices` and the lock commits, which the run confirms | `task test` (validate_skills incl. bundled-copy checks); check: actual output | `spec/README.md:37` last-updated → 2026-11-25; check: `task test` |
| #808 | §B `:56-59`: pin form `#<ref>` (any tag or commit) or `@<full commit SHA>`; state that `@<ref>` with a ref that isn't version-shaped or a full SHA is read as a skill filter and installs the default branch unpinned with exit 0 (run 2/5); version-shaped `@vX.Y.Z` stays unestablished. §C lock check `:72` and lock description `:73`: a pinned v2 entry records `ref`; an entry without `ref` fails the lock check (unpinned). DE mirrored. check: `git grep -n '@<ref>' spec plugins` → 0 | same edits; check: `cmp` → identical | step 3 `:52`: lock check also requires a `ref` in the entry; check: `git grep -n "ref" …/SKILL.md` + `task test` | `02-missing-react-skill.md:20`: command → `#<ref>`; `01:15-16`, `:26-27`: "records the commits" → "records the pinned refs and commits"; check: grep | `task test`; check: actual output | same row as #803 |

Existing installations / upgrade / rollback: a consumer repo whose `skills-lock.json` entries lack `ref` (installed with `@<tag>` per the old text, or unpinned) will now get a setup Warning from the lock check and must confirm or reinstall with `#<ref>`; health gate: none (Claude plugin); state surfaces read: consumer `skills-lock.json`, `.claude/skills/<name>`; no persisted state, invocation name, or artifact path of this plugin changes; rollback restores the old text and silences the Warning. check: example 01/02 walk-through + the run table above.

## Risks

- The `ref` requirement turns existing unpinned consumer installs into a Warning on the next audit — intended (they were never pinned), but visible; the Warning names the `#<ref>` reinstall.
- Version-shaped `@vX.Y.Z` remains unestablished by run; the text says so rather than claiming either way.

## Open questions for the operator

- none blocking. (Design choice taken: recommend `#<ref>` as the pin form because it pins any tag and any commit in runs 3/4; `@<full SHA>` named as the equivalent for commits.)

## Member results

| Member | Specialist | Check | Actual output |
|---|---|---|---|
| #803, #808 | no matching specialist dispatched — members implemented in the orchestrating session (text alignment to the measurement; see Deviations) | `cmp` bundled copies vs `en.md`/`de.md` | identical (no output, exit 0) |
| #803, #808 | — | `task test` @ 4d51738c | `1779 passed, 21 skipped, 8 warnings in 356.45s` |
| #803, #808 | — | `SKIP=markdownlint pre-commit run --from-ref origin/develop --to-ref HEAD` | exit 0 (Vale 3.15.2 locally; CI pins 3.28.1) |
| #803, #808 | — | `markdownlint-cli@0.50.1` with the hook's `--disable` list on changed files | only MD060 on unchanged table rows (`en.md:42,112`), the same 20 lines as on develop 72cba52c |
| #808 | — | `git grep -n '@<ref>' -- spec plugins` | only the new MUST NOT bullet (`en.md:61`, `de.md:61` + bundled copies) |

## Deviations

| Member | Kind | What changed |
|---|---|---|
| #803, #808 | local adaptation | members implemented directly in the orchestrating session instead of a nested `issue-orchestrate` run: the partition record plus the measurement already carried comprehension, class, and cause verification, and the change is a text alignment of 4 files + 2 copies |
| #808 | local adaptation | AC3 as written (a lock entry without `commit`) doesn't occur; the run shows an unpinned entry lacks `ref` instead, so the lock check now requires `ref` |
| #808 | local adaptation | review finding 4: `project/requirements/frontend-audit-rework.md` R2 named the `@<tag|commit>` form; changed to `#<tag|commit>` in this lane |

## Findings

| Finding | Source | Outcome | Reproduction | Issue |
|---|---|---|---|---|
| `en.md:56,61` `#<full SHA>` prescribed but never run | diff review @ 4d51738c | fixed directly | run 6: `#<SHA>` → content = tag, `ref` = SHA | — |
| `en.md:61` "any other text after `@`" overgeneralised | diff review @ 4d51738c | fixed directly | run 10: `@v1.0.0` → `Source: … @ v1.0.0`, read as ref | — |
| `en.md:56` vs `:61` `@<full SHA>` both required-against and allowed | diff review @ 4d51738c | fixed directly (MUST NOT `@<ref>` without exemption) | text contradiction, read | — |
| `project/requirements/frontend-audit-rework.md:65` R2 still `@<tag|commit>` | diff review @ 4d51738c | fixed directly | `git grep` | — |
| no AC for `#` form / `ref` lock condition | diff review @ 4d51738c | fixed directly (new AC, EN+DE) | read | — |
| §H header and step 3 don't record `ref` | diff review @ 4d51738c | fixed directly (`en.md:131`, `:72`, `SKILL.md:52,88`) | read | — |
| `ref: main` passes the lock check | diff review @ 4d51738c | fixed directly as a documented limit of the plausibility check (`en.md:74`) | run 7: `#main` → `ref: main` | — |
| no migration sentence for entries without `ref` / lock v1 | diff review @ 4d51738c | fixed directly (`en.md:74`) | read | — |
| unpinned-install and exit-1 claims measured only with `@<tag>` | diff review @ 4d51738c | fixed directly | runs 8, 9 (no ref) | — |
| `en.md:61,74` Vale.Spelling `install's`, `reinstalls` | pre-commit vale | fixed directly | `vale` exit 1 → 0 | — |
| re-review @ ad27be2b: all 9 resolved; 4 suggestions (`only` overgeneralised `en.md:61`; `therefore` misplaced `en.md:74`; lock v1 `ref` asserted unmeasured `en.md:74`; example 01 `:26` lacks `ref`) | diff re-review @ ad27be2b | fixed directly | read; v1 `ref` now stated as unestablished | — |
