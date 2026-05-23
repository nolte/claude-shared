# Example 01 — Stalled PR with red required checks

A scheduled portfolio in-flight audit run from inside `claude-shared`
finds an open pull request in `nolte/release-tooling` whose only
finding driver is a red required status check. The audit emits a
single `Warning` finding that names `workflow-health-triage` as the
recommended specialist and routes the red-check driver to it
exclusively — no second specialist is attached for the same driver,
even when the same PR also stalls on other axes. Exercises the
red-check routing exclusivity rule from
`spec/portfolio/portfolio-inflight-management/` §Specialist
recommendation.

## Input prompt

> Run the in-flight triage.

## Input files

The active checkout is `claude-shared`; detection passes because
`.claude-plugin/plugin.json` and
`spec/portfolio/portfolio-inflight-management/` both exist.

The resolved Portfolio-Member set returned by
`gh api orgs/nolte/repos --paginate` contains `nolte/release-tooling`,
which carries no `portfolio: excluded` opt-out marker in `CLAUDE.md`
and no `inflight: skip-pull-requests` marker.

The `portfolio-inflight-collector` agent returns, among other entries,
the following PR summary for `nolte/release-tooling`:

```yaml
pull_requests:
  - id: 142
    title: "feat(release): bump pin to gh-plumbing v1.1.20"
    state: open
    is_draft: false
    age_days: 9
    last_reviewer_activity_days: 2
    required_checks_red: true
    failing_checks: [lint]
    conflicts_against_develop: false
    labels: []
    review_threads_unresolved: 0
```

No `release-blocker` label is set; the PR head SHA does not appear in
any open `release-drafter` draft; no sibling Portfolio-Member's
`project/roadmap.md` or `project/sprints/*.md` references `nolte/release-tooling#142`.

No `project/inflight.yml` override exists in `release-tooling`, so the
audit applies the spec defaults.

## Expected behaviour

1. **Repository-role detection passes.** The skill confirms it is
   inside `claude-shared` (plugin manifest plus
   `spec/portfolio/portfolio-inflight-management/` both present) and
   selects the Run operation.
2. **Portfolio-Member set resolved + collector dispatched.** The skill
   reuses the resolution mechanism from `portfolio-management` and
   then dispatches `portfolio-inflight-collector` for the four-source
   fan-out. The orchestrating conversation receives only the
   pre-reduced structured summary; raw PR bodies stay inside the
   agent.
3. **Stalling threshold evaluated.** The PR has crossed the
   PR-with-red-required-checks threshold (open longer than 7 days
   with red required checks). The skill records the staleness measure
   (`9 days open, 2 days since last reviewer activity`) and proceeds
   to classification.
4. **Matrix axes derived.** For PR #142:
   - `security_relevance: false` (no CVE / supply-chain / leaked-credential signal in scope)
   - `release_blocking: false` (no `release-blocker` label, no open `release-drafter` draft membership)
   - `age_multiplier: 1.3×` (9 days open ÷ 7-day threshold)
   - `cross_repo_blocking: false` (no roadmap or sprint reference scan hit)
5. **Severity assigned.** With no Critical-row trigger active and
   `age_multiplier` between `1×` and `2×`, the only Warning-row
   trigger that fires is the red required checks driver. The skill
   classifies the finding as `Warning` (not `Suggestion`, because the
   red checks driver always lifts at least to `Warning` per the
   matrix).
6. **Specialist recommendation applied with exclusivity.** Because
   the only driver of this finding is the red required check, the
   skill names `workflow-health-triage` as the recommended specialist
   and **MUST NOT** route the same red-check driver to any other
   specialist (e.g. not also to `pull-request-merge`), per
   §Specialist recommendation. The recommended-action line carries
   the verbatim slash-command invocation: `/nolte-shared:workflow-health-triage against PR nolte/release-tooling#142`.
7. **Findings-Report written** at
   `.audits/portfolio-inflight/2026-05-23.md` with the four
   `review-plan`-mandated sections in declared order — `## Scope`,
   `## Summary`, `## Findings`, `## Processing log` — and Title-Case
   severities only. The finding reads roughly:

   ```text
   [portfolio-inflight-management §Classification and prioritisation]
   Warning — release-tooling/pr/142
   driver: red required check (lint)
   axes: security_relevance=false, release_blocking=false,
         age_multiplier=1.3×, cross_repo_blocking=false
   staleness: 9d open, 2d since last reviewer activity
   recommend: /nolte-shared:workflow-health-triage against PR nolte/release-tooling#142
   ```

8. **Per-severity counts confirmed.** The closing message in the
   operator's language reports the path of the new Findings-Report
   (`.audits/portfolio-inflight/2026-05-23.md`), the per-severity
   counts (e.g. `Critical: 0`, `Warning: 1`, `Suggestion: 0`,
   `Info: 0`), and points the operator at the recommended
   `workflow-health-triage` dispatch as the next step.
9. **Hard rules honoured.** No PR closed, no PR merged, no branch
   deleted, no review comment resolved; no file modified in
   `nolte/release-tooling`; the audit's only write target is
   `.audits/portfolio-inflight/2026-05-23.md` in `claude-shared`; no
   mutating `gh api` call issued; the `Warning` severity is written
   exactly in Title Case (no `WARNING`).
