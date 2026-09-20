---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "652"
classification: "spec-change"
secondary-classes: [docs]
route: "direct"
status: draft
created: "2026-09-20"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Issue**: #652 — pull-request-workflow: the develop-merge autoclose rule names the wrong default branch, and the observed behaviour is inconsistent
- **Author**: `nolte` (repository owner, trusted) · **Labels**: spec · **Comments**: 1 (this session's corpus sweep, posted after the operator confirmed the intended configuration)
- **Linked items**: none. Open sibling: PR #653 (issue #649) — **no file overlap**, but it branches off the same `develop` tip, so whichever merges second is rebased per `pull-request-workflow` §"Sequential merge of multiple open PRs".
- **Prior art**: none in `project/`. The issue was filed by this session on 2026-09-20 from the merge of PR #650.

## Requirements gate

No requirement artefact. **Operator override** recorded: the issue is owner-authored, its claims were measured rather than inherited, and the operator has since fixed the load-bearing design decision ("`develop` is the intended default branch, not `main`"), which was the only open question the issue carried.

## Asserted cause: verified, and one claim in it sharpened

**Confirmed — the configuration.** `.github/settings.yml:17` declares `default_branch: develop`, committed 2026-04-22 in `19bd86a8`; `gh api repos/nolte/claude-shared --jq .default_branch` returns `develop`. The operator confirmed this is intended. The parenthetical "(`main` under this branching model)" is therefore false.

**Confirmed — the behaviour.** PR #650 merged into `develop` at `2026-09-20T06:55:10Z`; `#645`, `#646`, `#647` closed at `06:55:11Z`–`06:55:12Z` with no manual `gh issue close`. PR #648 merged at `2026-09-19T19:18:28Z` with the same keyword form; its five members were still `OPEN` 36 minutes later. **Why the runs differ stays unexplained and this run does not assert a cause.**

**Sharpened while grounding — the acceptance criterion is a category error.** `en.md:167` / `de.md:182` require that "the autolink **MUST NOT** have closed any of them silently on the `develop` merge". That forbids an action of the platform, which this repository doesn't control, and the 2026-09-20 observation violates it. A spec can require a *check*; it can't forbid GitHub from firing. This is a second defect in the same rule and the sharper one, because it makes the criterion unfalsifiable-by-design: no repository behaviour can satisfy it when the platform chooses otherwise.

**The corpus contradicts itself** (`grep -rn -i "default branch" --include='*.md' spec skills agents plugins`). Five locations already write `develop` as the default — `spec/project/elicitation-implementation-separation/en.md:109`, `spec/project/release-skill-layer/en.md:42`, `spec/project/issue-batch-integration/en.md:153`, `skills/release-publish-trigger/SKILL.md:206`, and `spec/project/branching-model/en.md:46` ("`develop`, not `main`"). Four locations write `main`, all of them restatements of this one rule. One location states the platform rule correctly and is **out of scope**: `spec/project/pull-request-workflow/en.md:193` / `de.md:193`, sourced to GitHub Docs, says the autolink fires on "the repository's default branch" without naming a branch.

## Scope

- **In scope**: the four locations that name `main` as this repository's default branch, plus the acceptance criterion in both languages that forbids the platform's action.
- **Out of scope**: `pull-request-workflow:193` (correct platform statement); the five locations that already say `develop`; the cause of the inconsistent firing; any change to `.github/settings.yml` or to the platform configuration — the operator confirmed the configuration is intended; the `release-cd-refresh-master.yml` workflow itself (only the prose that mis-states its role in issue closure changes).

## Route

**Direct.** One coherent outcome — the corpus states which branch is default and makes the closure step a check — one PR strand, no roadmap item.

## Work packages

### P1 — `pull-request-workflow`: the rule and its acceptance criterion

- **Problem statement** (hypothesis, refutable): `en.md:132` and `de.md:132` can be rewritten to name `develop` as the default branch and to state the closure duty as a per-issue `state` check, and `en.md:167` / `de.md:182` can be rewritten from "the autolink must not have closed any" to "each referenced issue is closed, and the ones the autolink didn't close carry the cross-reference comment". If the rewrite turns out to need the `release-cd-refresh-master.yml` sentence removed rather than corrected, that refines the package rather than refuting it.
- **Acceptance criteria**: neither language names `main` as the default branch; the rule requires the check and describes the autolink as unreliable rather than absent, so both observed runs grade as conformant; the acceptance criterion is satisfiable by repository behaviour alone; `:193` untouched; EN/DE parity in headings, bullets and checkboxes; `pre-commit run --files` green.
- **Touched files**: `spec/project/pull-request-workflow/{en,de}.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: none

### P2 — the three skill-side restatements

- **Problem statement** (hypothesis, refutable): `skills/pull-request-merge/references/gotchas.md:8`, `skills/pull-request-merge/references/issue-closure.md:3` and `:15`, and `skills/issue-batch-orchestrate/SKILL.md:265` restate the corrected rule and need the same two changes (branch name, check-not-prediction). The step-8 procedure itself and operation 7 of the batch skill stay as they are: both already check `state` per issue before closing, which is what the corrected rule requires.
- **Acceptance criteria**: `grep -rn "default branch is \`main\`\|default is \`main\`\|fast-forward of \`main\`" skills spec` returns nothing outside the release-flow specs that legitimately discuss `main` as the presentation branch; the two skills still instruct the operator-confirmed manual close; `validate_skills.py` clean (body-token caps: `issue-batch-orchestrate` ~3,312 tokens, headroom fine; `pull-request-merge` unmeasured, measure before editing); markdownlint green.
- **Touched files**: `skills/pull-request-merge/references/gotchas.md`, `skills/pull-request-merge/references/issue-closure.md`, `skills/issue-batch-orchestrate/SKILL.md`
- **Specialist**: `nolte-claude-dev:claude-plugin-developer`
- **Depends on**: P1 (restates its wording)

## Dependency ordering

P1 → P2 → P3.

## Defect-class decision (`spec/project/defect-class-guards/`, this is a `fix`)

**Operator decision 2026-09-20: the guard is built in this pull request, not deferred to its own issue.** The section below records the design and the measurement that shaped it; it replaces the deferral this artifact first proposed.

The class is **"a spec states a repository-specific configuration value that the configuration itself contradicts"**. G1 asks what the fix leaves behind:

- **The guard** (P3): `scripts/check_default_branch_claims.py`, wired as a `pre-commit` hook in the enforced `lint` lane (G2) and covered by `tests/test_check_default_branch_claims.py`, following the `check_section_refs.py` pattern the repository already uses (script + hook with `pass_filenames: false` + tests that build a fixture repository in `tmp_path` and then run the guard over this repository itself).
- **Predicate (G3, G6), measured three times while designing it — each widening is recorded because the first two were too narrow:**
  1. *Sentence containing "default branch" plus a branch literal*, scanned line by line → **2 hits**. Missed three known sites.
  2. *Marker widened to "default is / defaults to / Default-Branch"*, still line by line → **3 hits**. Still missed the site whose sentence wraps across two lines.
  3. *Same marker, with wrapped lines joined into logical units first* → **5 hits**, which is every site the property can decide. The line-by-line scan was itself the G6 failure the rule warns about: the selector was narrower than the property because a sentence is not a line.
- **What the predicate deliberately cannot decide**: two further sites state the same wrong premise through its *consequence* rather than through a default-branch claim — `skills/pull-request-merge/references/issue-closure.md:3` ("waiting for the next `release-cd-refresh-master.yml` fast-forward of `main`") and `:15` ("because `main` was fast-forwarded between the merge and this step"). Neither sentence names a default branch, so no mechanical selector over this property reaches them. They are repaired by hand in P2, and the guard's own docstring states the gap. Per `defect-class-guards` G7 the guard **MUST NOT** be written so that it certifies those two as conformant silently; naming the gap is what keeps it honest.
- **Allowlist (G4), one entry with its reason**: `skills/issue-orchestrate/references/verification-scoping.md` — "a repo whose default is `main` while `develop` integrates" describes a *hypothetical other repository* to explain why a built-in review reads the wrong diff. It is not a claim about this repository. The entry names that reason, and the guard fails when an allowlist entry stops matching anything (G4's staleness rule).
- **Issue number (G5)**: the script's module docstring and the hook id carry `#652`.

## Risks

- **Rebase against PR #653.** No file overlap, but the second PR to merge needs a rebase and a fresh green run. Recorded, not mitigated here.
- **Over-correction.** `main` legitimately appears in release-flow prose (the presentation branch). The sweep predicate must target *default-branch* claims, not every mention of `main`.
- **No security-sensitive path.**

## Work package P3 — the guard

- **Problem statement** (hypothesis, refutable): the repository's existing `scripts/` + `pre-commit` + `tests/` pattern carries this guard without new tooling. If a lane turns out not to exist for it, that refutes the hypothesis and the guard's home changes.
- **Acceptance criteria**: the guard reports exactly the sites whose sentence names a branch other than `.github/settings.yml`'s `default_branch` beside a default-branch marker, with wrapped lines joined; it reads the configured branch from that file rather than hard-coding one, so changing the configuration changes the guard's verdict without a code edit; an allowlist entry that matches nothing fails the run; tests pin each rule against a fixture repository and one test runs the guard over this repository, which must be clean after P1 and P2; the hook runs in the `lint` lane.
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: P1, P2 (the guard must be green when it lands)

## Open questions for the operator

None — the guard decision was taken by the operator ("direkt hier").

## Dispatch log

<!-- Appended during operation 5. -->

## Member results

- **P1** — `nolte-shared:spec` (inline): `pull-request-workflow/{en,de}.md` rule and acceptance criterion. Checks: EN/DE parity `H=24 B=122 AC=25` both; vale clean after one spaced-em-dash rewording; hooks green.
- **P2** — `nolte-claude-dev:claude-plugin-developer`: `gotchas.md:8`, `issue-closure.md:3`, `:15`, **`:22`**, `issue-batch-orchestrate/SKILL.md` gotcha. Checks: `validate_skills.py` 0 Critical, body ~3,331 tokens (from ~3,312); full `pre-commit run --files` green; the guard predicate returns empty over all three files. Skip check and operation 7 verified intact by the orchestrator (`grep -c` = 1 each).
  **Refutation, accepted and consequential:** the brief scoped `issue-closure.md` to lines 3 and 15. Line 22 — the `gh issue close --comment` template — carried the same false claim in shell-escaped backticks (`\`main\``), and that text is posted onto **every issue the procedure closes**, making it the most operator-visible instance of the defect in the corpus. It is also invisible to P3's predicate, because escaped backticks defeat the literal match. Repaired by hand; relayed to P3 for its docstring gap list.
- **P3** — `nolte-engineering:fullstack-developer`: `scripts/check_default_branch_claims.py`, a `.pre-commit-config.yaml` hook in the enforced `lint` lane (G2, name carries `#652` per G5), `tests/test_check_default_branch_claims.py`. Expected branch read from `.github/settings.yml`, never hard-coded; wrapped lines joined; fenced content scanned; escaped backticks accepted as delimiters. Allowlist granularity: path **plus** a distinctive substring of the excused sentence, because a path alone survives every rewording and would silently excuse a different sentence later; a stale entry fails the run (G4). Negative verification: 14 mutants over a file copy, never `git stash`; one survived at first (the backtick requirement) and a test was added until it died.
  **Two refutations from the specialist, both accepted:** fenced content must be scanned and escaped backticks accepted, because the operator-visible `gh issue close` template sat inside a fence with escaped delimiters — measured over both trees, that widening adds one true positive and no false positive. `.audits/` must be out of scope, because the guard otherwise fails against its own evidence record.
  **One refutation by the orchestrator, applied:** the specialist also excluded `project/`. Measured over both trees, `project/` produces **zero** hits, so the exclusion was an assumption rather than a finding, and it removes roughly sixty live mission, roadmap, feature and sprint files from a guard whose property covers them. That is the selector-narrower-than-the-property failure of G6 — the rule this guard exists to enforce. Exclusion narrowed to `.audits/` alone, docstring records why, and a new test `test_the_planning_tree_is_in_scope` pins it; negative-verified by restoring the exclusion, which kills exactly that test.

## Guard gap list (G7: what a green run does not certify)

Three shapes of this defect class the predicate cannot decide, all repaired by hand in this pull request:

1. The consequence form — "waiting for the `release-cd-refresh-master.yml` fast-forward of `main`" names no default branch (`issue-closure.md:15`).
2. The escaped-backtick form — a branch name inside a shell-comment template (`issue-closure.md:22`).
3. Any claim phrased without a default-branch marker at all.

A green guard run means no *detectable* claim contradicts `.github/settings.yml`. It does not mean the corpus is free of the class.

## Verify (operation 6)

| Gate | Result |
|---|---|
| `git diff --stat origin/develop...HEAD` | non-empty, captured before any verdict |
| `python3 scripts/check_default_branch_claims.py` on the tip | `pass (configured branch \`develop\`, 1 allowlist entry live)`, exit 0 |
| Same guard against the pre-fix tree `fc104be7` (positive control) | **5 findings**, including the escaped-backtick template line the hand repair fixed — the guard is red where the defect was and green where it isn't |
| `python3 -m pytest tests/test_check_default_branch_claims.py -q` | 31 passed |
| `python3 -m pytest tests -q` | see bundle line below |
| EN/DE parity, pull-request-workflow | `H=24 B=122 AC=25` both |

