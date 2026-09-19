# Group pre-analysis: 2026-09-19-runner-slot-economy

> Run-scoped artifact. Committed on the integration branch, removed with a fix-forward
> `git rm` before the bundle merges. It must never reach the default branch, and it must
> never be hidden behind a `.gitignore` entry.

## Scope of this analysis

**Research question:** Does the hub's CI spec corpus carry the concept that a GitHub
Actions job draws on a finite, account-wide runner-slot allotment, and which rule, which
run-time signal, and which measurement recipe are missing for the starvation #644
measured to be diagnosable and preventable from any consuming repository?

**The group's single logical change, in one sentence:** The portfolio's CI corpus gains
the runner-slot economy as a design-time rule (`github-actions-best-practices`), queue
time and churn as a run-time diagnosis (`workflow-health`), and the measurement recipe
plus reviewer check that make both checkable from any consuming repository
(`cicd-pipeline-design`, `workflow-health-triage`, `cicd-pipeline-reviewer`).

**Out of scope:** #644 itself (a cross-repository tracking issue whose remaining
children live in `nolte/gh-plumbing#439`, `nolte/kamerplanter#1583`, `#1584`; it closes
when its children close, by the operator, not by this bundle); any change to §I's
self-hosted-runner MUST NOT (the issue defers that decision explicitly); a script or
Taskfile target (#647 rules it out: no skill in this repository ships executable code);
#643 (unrelated capability) and #393 (bot).

**Tier:** 3 — `github-actions-best-practices` and `workflow-health` carry
`Portfolio-Scope: portfolio` (`spec/project/github-actions-best-practices/en.md:4`,
`spec/project/workflow-health/en.md:4`), so the group changes a published contract.

## Members

| Issue | Class | Admitting predicate | Evidence |
|---|---|---|---|
| #645 | spec-change | thematic coupling | new section in `spec/project/github-actions-best-practices/{en,de}.md` (§A–§K today, `en.md:40-128`); the platform binding of `continuous-integration` §B that the corpus lacks |
| #646 | spec-change | thematic coupling | extends `spec/project/workflow-health/{en,de}.md` §"Cancellation rates" (`en.md:102-107`) with the second cause and a queue-time duty; cross-references #645's section |
| #647 | feature-request (skills/agents) | dependency chain | #644: "#647 lands after whichever spec issue goes first"; the reference cites #645's rule and #646's reading rule; touches `skills/cicd-pipeline-design/`, `skills/workflow-health-triage/SKILL.md`, `agents/cicd-pipeline-reviewer.md` |

All three authored by `nolte` (repository owner, trusted-author set); no comments. Each is
bounded: one outcome, one PR strand, no roadmap item. #644 rejected as a member (tracking
issue spanning three repositories; its hub-side work *is* these three).

**Cause verification (per `issue-orchestration` §Issue acquisition, now on `develop`):**
the asserted cause is slot starvation from an account-wide allotment, not slow jobs.
Re-measured 2026-09-19 in this repository: on the last six `ci` PR runs, the `needs:`-free
jobs `lint` and `links` waited 603 s, 1219 s, 1041 s, 1419 s for a runner against 16–68 s
of work on four runs (the other two had 0–4 s wait, showing an idle pool), while
`gh api …/actions/runs?status=in_progress` reported 0 runs in this repository — the
queue was elsewhere in the account. kamerplanter cancellation rates re-measured over the
last 40 PR runs (concluded runs only): `e2e-smoke.yml` 22/25 cancelled (88 %),
`frontend.yml` 14/19 (74 %), `docker-lint-build.yml` 13/31 (42 %); the issue's 94/79/71 %
came from a different window, the majority-cancelled finding holds for two of three
lanes, and none of the three is slower than a push. The plan-dependent limits (Free 20,
Pro 40, Team 60, Enterprise 500 concurrent jobs) are established from GitHub Docs
"Actions limits" (read 2026-09-19); that page states the macOS sub-limit is shared across
runner types but doesn't state the account-wide scope in words, so the scope claim rests
on the cross-repository observation above and is marked so in #645's source line.

**Dependency ordering:** #645 → #646 → #647. #646 cross-references #645's new section by
name; #647's reference cites both rules, so it lands last.

**Shared touch surface:** none between members at file level (#645 and #646 edit
different specs; #647 edits skills and one agent); `spec/README.md` rows for both specs.

## Mode decision

**Mode:** A — single strand

**Reason:** No member is likely to need removal: all three are owner-authored with
acceptance criteria, every decision below is answered at this gate, no member depends
on a party outside the group (the consumer-side children of #644 depend on these, not
the reverse), none is `security`-classified.

## Structural finding

**Cluster shape:** symptom cluster

**Root cause or defect class:** the corpus has no concept of runner-slot scarcity: the
tool-independent `continuous-integration` §B says "run it concurrently" as a remedy, the
platform spec binds runner *trust* (§I) but not runner *scarcity*, and `workflow-health`
observes flake and cancellation rates but not queue time — so a starved pipeline reads
as a slow one and gets the wrong remedy. The three members are the rule, the signal, and
the measurement for that one cause.

**Process finding:** none beyond the group. The cause was found by measurement (#644),
which is the path `issue-orchestration` §Issue acquisition now requires; the group is
the preventive change. Recorded so the absence is a statement, not an omission.

**Preventive change:** the group itself (rule + signal + recipe + reviewer check).

**Recurrence fed to the portfolio loop:** class "platform constraint absent from the
platform spec", recurrence 1 (this group); the earlier `GITHUB_TOKEN` event-cascade
constraint (`workflow-health` §Known platform constraints) is the same class from an
earlier wave, so the loop holds 2.

## Decisions proposed for the write gate

| Member | Question | Proposal |
|---|---|---|
| #645 | section placement | new **§L "Runner-slot economy"** after §K, plus one §J bullet routing the run-time observation to `workflow-health`. The issue says "after §I", but inserting there re-letters §J and §K, and §K is cross-referenced from `pull-request-workflow` §"Merge queue"; a stable letter costs nothing |
| #645 | the five candidate rules | adopt as written: MUST (slot cost as a design input, referencing `continuous-integration` §B per §J), MUST (measure wait separately from runtime), SHOULD NOT (no separate job for sub-minute work without one of the four reasons), SHOULD NOT (no sub-minute gate in `needs:` ahead of expensive jobs), MAY (merge advisory checks with per-step verdicts) |
| #645 | source | new [R13] GitHub Docs "Actions limits" (plan table, read 2026-09-19); the account-wide scope marked as established by cross-repository observation, with the docs page named as the place a wording would come from |
| #646 | shape | extend §Cancellation rates with a fork after the existing threshold (runtime > cadence → existing remedy; runtime ≪ cadence and updated by unrelated merges → churn, remedy: fan-out/trigger breadth/merge model, never `cancel-in-progress: false`); new MUST for queue-time observation on `needs:`-free jobs; a lane whose wait dominates runtime is a capacity finding routed to §L; existing MUSTs untouched; two acceptance criteria |
| #647 | reference home | `skills/cicd-pipeline-design/references/slot-capacity-measurement.md` (new `references/` dir), referenced from `workflow-health-triage` op 2 (classification) and from `cicd-pipeline-design` op 1 step 2 (stage sequence); reviewer agent gains the two file-only checks under §"Platform"; severity per the agent's existing scale (Warning for a sub-minute job without a reason, Warning for a sub-minute gate in `needs:`) |
| #647 | cancelled runs in triage | `workflow-health-triage` op 1 currently says a `cancelled` run is classified `other` and stops; add one sentence routing a majority-cancelled lane to `workflow-health` §Cancellation rates' fork (churn vs cadence) instead of `other` |

## Completeness matrix

| Member | Spec (EN + DE) | Skills / agents | Tests | Docs | Config / workflows | Generated index |
|---|---|---|---|---|---|---|
| #645 | `github-actions-best-practices/{en,de}.md`: §L + §J bullet + acceptance criteria + [R13]; check: `pre-commit run --files` (vale, markdownlint, check-section-refs) + EN/DE parity counts | `cicd-pipeline-design/SKILL.md` description lists the platform topics it binds — add "runner-slot economy"; check: `validate_skills.py` (description ≤ 1024) | not applicable — no test asserts spec prose | not applicable — no guide restates the spec (`grep -rl github-actions-best-practices docs/{en,de}` outside the catalog: checked at implementation) | not applicable — rule text only; this repository's own workflows are audited by the consumer-side children | `spec/README.md` row; docs catalog via `gen_catalog.py`; check: `check_links.py --offline` |
| #646 | `workflow-health/{en,de}.md`: §Cancellation rates fork + queue-time MUST + cross-reference + acceptance criteria; check: as above | `workflow-health-triage/SKILL.md` restates the cancellation rule in op 1 ("cancelled → other") — updated under #647's dispatch; check: `validate_skills.py` | not applicable | not applicable | not applicable | as #645 |
| #647 | not applicable — spec text lands in #645/#646; the reference cites them by §name; check: `check-section-refs` resolves the citations | `cicd-pipeline-design/references/slot-capacity-measurement.md` (new), `cicd-pipeline-design/SKILL.md` op 1 + §Examples/references pointer, `workflow-health-triage/SKILL.md` op 1–2, `agents/cicd-pipeline-reviewer.md` §Platform + description if needed; check: `validate_skills.py` (body caps, description cap, agent description budget for `agents/`), markdownlint | `tests/test_validate_skills.py` covers the validator; check: `python3 -m pytest tests -q` | not applicable — catalog regenerates from frontmatter | not applicable | as #645 (catalog picks up the new reference automatically) |

**Bundle-level checks (integration branch tip, recorded with output):** `pre-commit run
--all-files` before catalog generation; `python3 scripts/validate_skills.py`; `python3
-m pytest tests -q`; `gen_catalog.py` + `check_links.py --offline`; `python3 -m mkdocs
build --strict`; EN/DE parity per touched spec; #647's acceptance by reading: the
reference alone reproduces #644's table with a token and `curl`.

## Risks

- **Agent description budget.** `agents/` carries a baseline budget in `validate_skills.py`;
  extending `cicd-pipeline-reviewer`'s description may breach it. Mitigation: extend the
  body, keep the description unchanged unless the check must be routable by description.
- **Relettering.** Avoided by §L placement; recorded as a deviation from the issue's
  "after §I" wording.
- **Plan-dependent numbers age.** [R13] carries the retrieval date; the rule text states
  the mechanism, not the numbers, so a plan change doesn't falsify the rule.
- **Vale.** Words like "starved", "sub-minute" pass; "needs:" in prose is code-spanned.

## Open questions for the operator

All three answered 2026-09-19 ("Ja").

1. Approve the membership (#645, #646, #647; #644 rejected as tracking issue).
2. Approve the six proposals above (notably §L placement instead of "after §I").
3. Approve Mode A and the ordering #645 → #646 → #647.

## Member results

| Member | Specialist | Check | Actual output |
|---|---|---|---|
| #645 | skill `nolte-shared:spec` | EN/DE parity `grep -c` on github-actions-best-practices | `H=20 B=117 AC=21 R=13` both |
| #645 | — | `vale --output=line …/en.md` | 4 hits (percentage wording, SHOULD NOT ×2, "diagnosability") → reworded; re-run: no output, exit 0 |
| #645 | — | `SKIP=vale-prose pre-commit run --files <en,de>` | no Failed hook |
| #646 | skill `nolte-shared:spec` | EN/DE parity `grep -c` on workflow-health | `H=20 B=89 AC=19` both |
| #646 | — | `vale --output=line …/en.md` | 2 hits (auto-merge, quote punctuation) → reworded; re-run: no output, exit 0 |
| #646 | — | `SKIP=vale-prose pre-commit run --files <en,de,spec/README.md>` | no Failed hook |
| #647 | `nolte-claude-dev:claude-plugin-developer` | `python3 scripts/validate_skills.py` | exit 0, 0 Critical; bodies ~3012 / ~4189 / ~2670 tokens; design description 949 chars |
| #647 | — | `pre-commit run --files <4 files>` (all hooks) | no Failed hook |
| #647 | — | `python3 scripts/check_section_refs.py` | exit 0; §"Runner-slot economy" and §"Cancellation rates" resolve |

## Deviations

| Member | Kind | What changed |
|---|---|---|
| #645 | local adaptation | section placed as §L after §K instead of after §I, keeping §J/§K letters stable; two SHOULD NOT rules phrased as SHOULD (Vale) with identical meaning |
| #647 | local adaptation | stand-alone sub-minute-job check graded Suggestion instead of Warning, per the reviewer agent's own §Severity scale; gate-in-`needs:` stays Warning |
