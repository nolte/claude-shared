# Example 02 — Release-blocker detection lifts a fresh finding to Critical

A scheduled portfolio in-flight audit run from inside `claude-shared`
finds an open pull request in `nolte/changelog-bot` that has only
been open for 3 days — well under the 7-day red-check threshold — but
carries a `release-blocker` label. The `release_blocking` matrix axis
trips on the label alone, lifting the finding straight to `Critical`
without the staleness threshold having to fire. Exercises the
`release_blocking` detection MUSTs from
`spec/portfolio/portfolio-inflight-management/` §Classification and
prioritisation and the sub-threshold escalation note in §Stalling
thresholds.

## Input prompt

> Audit the portfolio in-flight.

## Input files

The active checkout is `claude-shared`; detection passes because
`.claude-plugin/plugin.json` and
`spec/portfolio/portfolio-inflight-management/` both exist.

The resolved Portfolio-Member set returned by
`gh api orgs/nolte/repos --paginate` contains `nolte/changelog-bot`,
which has neither `portfolio: excluded` nor any `inflight: skip-…`
opt-out marker in `CLAUDE.md`.

The `portfolio-inflight-collector` agent returns, among other entries,
this PR summary for `nolte/changelog-bot`:

```yaml
pull_requests:
  - id: 67
    title: "fix(parser): handle empty release-note section without crashing"
    state: open
    is_draft: false
    age_days: 3
    last_reviewer_activity_days: 1
    required_checks_red: true
    failing_checks: [test]
    conflicts_against_develop: false
    labels: [bug, release-blocker]
    review_threads_unresolved: 0
```

The collector also reports an open `release-drafter` draft on the
same repository whose body lists the PR head SHA as one of the
upcoming-release entries (so signal (b) of the detection MUST is also
active alongside the label).

No sibling Portfolio-Member's `project/roadmap.md` or
`project/sprints/*.md` references `nolte/changelog-bot#67`.

## Expected behaviour

1. **Repository-role detection passes** for `claude-shared` and the
   Run operation is selected.
2. **Portfolio-Member set resolved + collector dispatched** as in
   Example 01. The collector returns the four-source per-repo
   summary.
3. **Stalling threshold check.** PR #67 is 3 days old, well under
   the 7-day red-check threshold. Under the spec's normal stalling
   rule this finding would not surface — but the §Stalling
   thresholds `SHOULD` clause permits sub-threshold escalation when
   another matrix axis demands it. The skill defers the
   surface-or-suppress decision to the matrix-axis evaluation in step
   4.
4. **Matrix axes derived.** For PR #67:
   - `security_relevance: false`
   - `release_blocking: true` per the §Classification and
     prioritisation detection MUST: PR carries a `release-blocker`
     label (signal a) AND the PR head SHA appears in an open
     `release-drafter` draft (signal b). Either signal alone would
     suffice; both being present is recorded in the axes log for
     traceability.
   - `age_multiplier: 0.4×` (3 days open ÷ 7-day threshold; below 1×
     does not normally surface, but is irrelevant once `release_blocking` fires)
   - `cross_repo_blocking: false`
5. **Severity assigned.** `release_blocking: true` triggers the
   `Critical` row of the matrix. The §Classification and
   prioritisation `SHOULD` higher-severity-tie-break rule applies —
   `Critical` wins over any other row the same finding might also
   match.
6. **Specialist recommendation applied.** The recommended specialist
   is `workflow-health-triage` (the red required check is still the
   actionable surface for the operator). The recommended-action line
   carries the verbatim slash-command invocation:
   `/nolte-shared:workflow-health-triage against PR nolte/changelog-bot#67 (release-blocking; prioritise over non-release PRs)`.
7. **Findings-Report written** at
   `.audits/portfolio-inflight/2026-05-23.md` per the
   `review-plan`-mandated four sections. The finding reads roughly:

   ```text
   [portfolio-inflight-management §Classification and prioritisation]
   Critical — changelog-bot/pr/67
   driver: release_blocking (label `release-blocker` AND head SHA in open release-drafter draft)
   axes: security_relevance=false, release_blocking=true,
         age_multiplier=0.4×, cross_repo_blocking=false
   staleness: 3d open, 1d since last reviewer activity (sub-threshold; escalated by release_blocking)
   recommend: /nolte-shared:workflow-health-triage against PR nolte/changelog-bot#67 (release-blocking; prioritise over non-release PRs)
   ```
8. **Tracking-issue offer.** Per §Integration with
   continuous-improvement the skill `SHOULD` open a tracking issue
   in `nolte/changelog-bot` for any `Critical` finding the operator
   dispatches against. The skill presents this as an opt-in offer to
   the operator and never opens the issue automatically — operator
   authority remains intact.
9. **Per-severity counts confirmed** in the closing message:
   `Critical: 1, Warning: 0, Suggestion: 0, Info: 0`, with the path
   of the new Findings-Report and the next-step pointer.
10. **Hard rules honoured.** No PR closed, no label added or removed
    by the audit, no `release-drafter` draft edited; no file modified
    in `nolte/changelog-bot`; the only write target is the Findings-
    Report; no mutating `gh api` call issued; `Critical` is written
    in Title Case (no `CRITICAL`).
