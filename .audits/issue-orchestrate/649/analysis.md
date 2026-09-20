---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "649"
classification: "spec-change"
secondary-classes: [feature-request]
route: "direct"
status: approved
created: "2026-09-20"
---

# Issue Orchestration — Pre-analysis

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #649 — continuous-improvement: consumer-measured spec issues have no intake trigger; open findings wait until someone batches them
- **URL**: https://github.com/nolte/claude-shared/issues/649
- **Labels**: spec · **Author**: `nolte` (repository owner, trusted-author set) · **Comments**: none
- **Linked items**: none (`closedByPullRequestsReferences` empty; no open pull requests in the repository)
- **Prior art checked**: `project/features/`, `project/roadmap.md`, `project/requirements/` — no entry. The issue is the process finding of group `2026-09-19-verification-discipline-specs`, filed by this session after that bundle's gate went green.

## Requirements gate

No requirement artefact under `project/requirements/` covers #649. **Operator override** recorded: the issue is owner-authored, carries three acceptance criteria and a named preventive change, and its load-bearing claims were re-measured below rather than inherited.

## Asserted cause: verified, and the proposed mechanism refuted

Per `spec/project/issue-orchestration/` §"Issue acquisition and comprehension" (the rule #641 added, merged in `fdb9d53e`), the cause the issue asserts was measured against the code before any tracked change.

**Cause — confirmed.** `spec/project/continuous-improvement/` §"Portfolio gap closure" counts only *generalist-handled recurrences of a finding class*; nothing counts open, consumer-measured issues. Established by reading `en.md:47-55` and by `grep -n -i "open issue|issue list|gh issue|backlog|intake" spec/project/continuous-improvement/en.md`, whose only hits concern specialist distribution and the generalist-recurrence acceptance criterion (`en.md:89`).

**Proposed mechanism — refuted.** The issue proposes counting "open `spec`-labelled issues in the hub that cite a consumer-repository measurement (an issue or PR reference into a `nolte/*` consumer)", threshold three, and asserts in its third acceptance criterion that the rule fires on the state of 2026-09-19, where it counts "five such issues open". Measured against that exact corpus on 2026-09-20:

| Member | `spec` label | `nolte/<consumer>#<n>` reference in the body |
|---|---|---|
| #636 | **absent** | yes (`nolte/kamerplanter#1405`) |
| #637 | present | yes (`nolte/kamerplanter#1456`) |
| #640 | present | **no** — the body writes ``in `nolte/kamerplanter` (PR #1573, issues #1535 and #1533)``, repository and number separated |
| #641 | present | **no** — "the consuming repository's own records", no reference |
| #642 | present | **no** — "a consuming repository", no reference |

Commands: `gh issue view <n> --json labels` and `gh issue view <n> --json body --jq .body | grep -c -o -E 'nolte/(kamerplanter\|vale-style\|gh-plumbing\|terraform-github-bootstrap\|k8s-home-lab)[#/]'`.

Consequences, all three established by the table:

1. The label half would have counted **four**, not the five the acceptance criterion claims — #636 carried no label at all.
2. The citation half would have counted **two**.
3. With the proposed threshold of three, **the rule would not have fired** on 2026-09-19. The issue's own acceptance criterion 3 is false as written.

A fourth consequence follows from the first: a trigger keyed on a label the filing author must remember to apply reproduces the "someone has to notice" failure the issue exists to remove. #649 itself carries no `nolte/<consumer>#<n>` reference either (it cites hub issues #636–#642), so under its own citation rule it would not count.

**The measurement wins over the issue text.** The decomposition below implements the cause, not the proposed detector.

## Scope

- **In scope**: an intake trigger in `spec/project/continuous-improvement/` §"Portfolio gap closure" (EN + DE) whose detector is demonstrated to fire on the 2026-09-19 corpus and not on the corpus after the bundle merged; the corresponding count in the in-flight audit (`spec/portfolio/portfolio-inflight-management/` §"Data sources" / §"Classification and prioritisation" and the `portfolio-inflight-triage` skill plus `portfolio-inflight-collector` agent), so the trigger is reported rather than remembered; the labelling obligation that makes the detector reliable at filing time.
- **Out of scope**: changing `issue-batch-orchestrate`'s admission predicates (a trigger schedules a run; it doesn't admit members); a GitHub Action that files issues or opens batch runs automatically (the spec's §Operator authority keeps the dispatch decision with the operator); retro-labelling closed issues; #644's consumer-side children.

## Route

- **Decision**: direct. One coherent outcome (the intake trigger and the check that reports it), one PR strand, no roadmap item.

## Decisions proposed for the write gate

| # | Question | Proposal (operator-approved 2026-09-20) |
|---|---|---|
| D1 | What does the detector key on? | **Both, with the label made reliable**: an open hub issue counts as a consumer-measured finding when its body names any portfolio-member repository other than the hub (the loose form, which catches #640's separated `nolte/kamerplanter` … `PR #1573`) **or** it carries the `spec` label. The union counts 5 of 5 on the 2026-09-19 corpus. |
| D2 | Is the label still obligatory? | Yes, at filing time: an issue that records a consumer-measured finding **MUST** carry the `spec` label, so the cheap half of the detector stays usable. The union means a forgotten label doesn't lose the finding — it only makes it costlier to detect. |
| D3 | Threshold | Three, matching the spec's existing recurrence threshold, stated as a project-overridable default with a recorded rationale (the pattern `requirements-elicitation` uses for `τ_high`). |
| D4 | What does the trigger do? | Schedule an `issue-batch-orchestrate` run over the counted issues, as a **SHOULD** with the operator's decision preserved per `portfolio-inflight-management` §"Operator authority" — the rule surfaces the count and names the action; it never opens a run by itself. |
| D5 | Falsification in the spec | The acceptance criterion states the corrected measurement: the detector counts 5 on the 2026-09-19 corpus (fires) and 1 on the corpus after `fdb9d53e` and `9ab082cd` merged (doesn't fire). Measured, not asserted. |

## Work packages

### P1 — `continuous-improvement`: the intake trigger

- **Problem statement** (hypothesis, refutable): §"Portfolio gap closure" can carry the trigger as three bullets (count, threshold, action) plus one acceptance criterion, without restating `portfolio-inflight-management`'s collection mechanics, which §"Relationship to existing specs" already delimits.
- **Acceptance criteria**: EN canonical + DE in lockstep; the rule names the detector (union per D1), the threshold with its override clause (D3), and the action (D4); one acceptance criterion carrying the measured 5-vs-1 falsification (D5); §"Finding sources in scope" gains the consumer-measured issue as a listed source; no restatement of the collector's mechanics; `pre-commit run --files` green; EN/DE heading, bullet and checkbox counts equal.
- **Touched files**: `spec/project/continuous-improvement/{en,de}.md`
- **Specialist**: `nolte-shared:spec`
- **Depends on**: none

### P2 — `portfolio-inflight-management` + the triage pair: report the count

- **Problem statement** (hypothesis, refutable): the in-flight audit already collects every open issue per repository (`en.md` §"Data sources"), so reporting the consumer-measured count needs one classification rule and one report line, not a new data source. If the collector's output shape can't carry the flag without a new source, that refutes the hypothesis and P2 becomes a collector change.
- **Acceptance criteria**: the spec names the count and the threshold flag in §"Classification and prioritisation" or §"Findings-Report shape", and cross-references `continuous-improvement`'s trigger rather than restating the threshold; `portfolio-inflight-triage` reports it in its run output; `portfolio-inflight-collector` returns the per-issue flag it needs; EN/DE parity; `validate_skills.py` clean for both artefacts (body and description caps); `check_section_refs.py` resolves both new citations.
- **Touched files**: `spec/portfolio/portfolio-inflight-management/{en,de}.md`, `skills/portfolio-inflight-triage/SKILL.md`, `agents/portfolio-inflight-collector.md`
- **Specialist**: `nolte-shared:spec` for the spec half, `nolte-claude-dev:claude-plugin-developer` for the skill and agent half
- **Depends on**: P1 (cites its rule by section name)

### P3 — the labelling obligation at filing time

- **Problem statement** (hypothesis, refutable): the `spec` label obligation belongs where an issue is filed. **Inspection done 2026-09-20, before dispatch:** `.github/ISSUE_TEMPLATE/` ships `bug_report.yml` and `feature_request.yml`, each carrying `labels:` on line 4 (`["bug", "needs-triage"]` and `["enhancement", "needs-triage"]`), plus `config.yml`. So the label mechanism exists, but **no template produces the `spec` label** — which is why #636 was filed without one. The hypothesis that the template spec is the right home therefore holds, and the concrete shape is a template (or a template field) that applies `spec` for a consumer-measured finding.
- **Acceptance criteria**: the obligation is stated exactly once, in the home the evidence supports, and the other spec references it; `.github/ISSUE_TEMPLATE/` is inspected and the finding recorded either way; EN/DE parity if a spec changes.
- **Touched files**: `spec/project/github-issue-templates/{en,de}.md` **or** `spec/project/continuous-improvement/{en,de}.md` (decided by the inspection), possibly `.github/ISSUE_TEMPLATE/*`
- **Specialist**: `nolte-shared:spec` for the spec text; `nolte-shared:github-issue-templates-apply` for the template itself (it owns that surface)
- **Depends on**: P1

## Dependency ordering

P1 → P2 ; P1 → P3 (P2 and P3 independent of each other).

## Risks

- **Restatement.** The threshold must live in one place. `continuous-improvement` owns it; `portfolio-inflight-management` references it. Mitigation: the grep sweep for the threshold value across both specs before the gate.
- **Detector drift.** The loose "names a portfolio-member repository" form depends on the member set. Mitigation: the rule points at `portfolio-management`'s member-set resolution instead of hard-coding repository names.
- **Body-token caps.** `portfolio-inflight-triage/SKILL.md` and the collector agent carry caps; measure after P2.
- **No security-sensitive path.** Prose and read-only audit rules; no credential handling, no workflow file.

## Open questions for the operator

None blocking — D1 to D5 were approved before this artifact was written. P3's home was decided by the inspection recorded above.

## Dispatch log

<!-- Appended during operation 5. -->

- **P1** — specialist `nolte-shared:spec` (skill, run inline): `spec/project/continuous-improvement/{en,de}.md` — §"Finding sources in scope" gains the consumer-measured finding as a listed source; §"Portfolio gap closure" gains five bullets (union detector with the measured under-count of each half, threshold three with the recorded-override clause, SHOULD schedule with operator authority preserved, the report/threshold split against `portfolio-inflight-management`, and the observation the trigger comes from); two acceptance criteria carrying the 5-vs-1 falsification and the single-place threshold. Hypothesis held. Checks: EN/DE parity `H=13 B=67 SUB=14 AC=16` both; `vale` exit 0 after rephrasing two spaced em-dashes (Microsoft.Dashes); `SKIP=vale-prose pre-commit run --files` no Failed hook; threshold sweep `grep -rn -E "three or more|drei oder mehr"` finds the number only in this spec (the `portfolio-inflight-management:92` hit is its pre-existing no-specialist rule, not the threshold).
- **P2 (spec half)** — specialist `nolte-shared:spec` (inline): `spec/portfolio/portfolio-inflight-management/{en,de}.md` — §"Data sources" collects the two per-issue flags as a sub-bullet (read off data already collected, no new API call), §"Classification and prioritisation" reports their union and flags it at the threshold `continuous-improvement` states without carrying out the action, §"Findings-Report shape" carries it as a summary-table row, one acceptance criterion. Hypothesis held: no new data source was needed. Checks: EN/DE parity `B=85 SUB=14 AC=14` both; `vale` exit 0 after rephrasing two spaced em-dashes; hooks green (trailing-whitespace auto-fix re-run clean). The acceptance criterion was corrected during authoring: it first claimed the threshold number "appears nowhere in this spec", which `grep -n "three or more"` refuted — `en.md:94` carries the pre-existing *recurrence* citation. Reworded to "cites the owning section for the intake threshold instead of stating it", which the same grep confirms.
- **P3** — specialist `nolte-shared:spec` (inline; the template file itself is `github-issue-templates-apply`'s surface and is not written here): `spec/project/github-issue-templates/{en,de}.md` — §"Baseline templates" gains `spec_finding.yml` as a named optional template for a repository holding portfolio-wide specs, with the reason the label is load-bearing; §"Project-type-driven derivation" step 5 gains the obligation that a template whose issues a portfolio rule counts pre-fills the label that rule reads; one acceptance criterion. Hypothesis held: the inspection recorded above (templates carry `labels:`, none yields `spec`) supports the template spec as the home. Checks: EN/DE parity `H=15 B=51 AC=13` both; `vale` exit 0 after two contraction rewordings; hooks green.
- **P2 (skill/agent half)** — specialist `nolte-claude-dev:claude-plugin-developer`: `agents/portfolio-inflight-collector.md` gains the two detection-only per-issue flags in §Output shape, §Working procedure 4a and the §Scope "does not" list (description untouched, no budget line); `skills/portfolio-inflight-triage/SKILL.md` derives the union in step 2, reports and flags it in step 10, and cites the owning section in §"Reference: spec anchors". Checks: `validate_skills.py` 0 Critical, `check_section_refs.py` pass, markdownlint Passed, and no threshold number in the added text.
  **Partial refutation, verified by the orchestrator:** the skill body stood at ~4,997 of the 5,000-token Critical cap, 11 characters of headroom, so the addition alone breached it. The specialist reclaimed space by condensing prose in place instead of opening a `references/` file, which edits spans unrelated to this issue. Re-checked against `HEAD`: headings 11 → 11, hard rules 11 → 11, numbered steps 10 → 10, `examples/*.md` pointers identical, issue references identical, §Gotchas bullets 8 → 8 with the bot-dashboard and rate-limit entries still present by name. Body now ~4,938 tokens. Recorded as a deviation because the diff touches prose this issue didn't ask to change.

