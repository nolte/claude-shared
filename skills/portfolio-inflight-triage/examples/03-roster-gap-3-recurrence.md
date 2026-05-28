# Example 03 — Roster gap crosses the 3-recurrence threshold

A scheduled portfolio in-flight audit run from inside `claude-shared`
finds a stalled item whose finding class has no matching specialist
slug in the `nolte-shared` plugin. The skill counts the recurrence
across the prior two `.audits/portfolio-inflight/*.md` artefacts plus
the current run and observes that the same `<data-source>/<finding-class-token>`
tag is now present for the third time. It presents the user-confirmation
gate that escalates the recommendation from "no specialist matches"
to "author a new specialist". Exercises the recurrence-counting
mechanic from `spec/portfolio/portfolio-inflight-management/`
§Specialist recommendation and the 3-recurrence rule from
`spec/project/continuous-improvement/` §Portfolio gap closure.

## Contents

- [Input prompt](#input-prompt)
- [Input files](#input-files)
- [Expected behaviour](#expected-behaviour)

## Input prompt

> Run the in-flight triage.

## Input files

The active checkout is `claude-shared`; detection passes because
`.claude-plugin/plugin.json` and
`spec/portfolio/portfolio-inflight-management/` both exist.

The `portfolio-inflight-collector` agent returns, among other
entries, the following Discussion summary for `nolte/home-assistant-addon`:

```yaml
discussions:
  - id: 41
    title: "Discussion: vendor a community-contributed YAML linter?"
    state: open
    age_days: 48
    last_maintainer_reply_days: null
    category: ideas
```

The Discussion has crossed the §Stalling thresholds default for
discussions (30 days open without a maintainer reply). Its content
falls outside every existing specialist's match surface — neither
`vocab-drift-audit`, nor `dependency-audit`, nor `prose-vale-curator`,
nor `workflow-health-triage`, nor `portfolio-audit`, nor any other
slug in `agents/` or `skills/` describes "evaluate vendoring a
third-party YAML linter for the portfolio". The skill records the
gap with the stable token `discussion/yaml-tooling-vendoring`.

The two prior in-flight Findings-Reports under
`.audits/portfolio-inflight/` carry the same gap token:

- `.audits/portfolio-inflight/2026-03-22.md` line 87:
  `[portfolio-inflight-management §Specialist recommendation]
   Suggestion — home-assistant-addon/discussion/41
   recommend: no specialist matches; roster gap recorded
   tag: discussion/yaml-tooling-vendoring`
- `.audits/portfolio-inflight/2026-04-22.md` line 102:
  `[portfolio-inflight-management §Specialist recommendation]
   Suggestion — home-assistant-addon/discussion/41
   recommend: no specialist matches; roster gap recorded
   tag: discussion/yaml-tooling-vendoring`

This run is therefore the third occurrence of the same gap token
across the audit history.

## Expected behaviour

1. **Repository-role detection passes** for `claude-shared` and the
   Run operation is selected.
2. **Portfolio-Member set resolved + collector dispatched.** Returns
   the four-source per-repo summary including the Discussion above.
3. **Stalling threshold evaluated.** Discussion #41 is 48 days old
   without a maintainer reply, well past the 30-day default
   threshold. The finding surfaces.
4. **Matrix axes derived.** For Discussion #41:
   - `security_relevance: false`
   - `release_blocking: false`
   - `age_multiplier: 1.6×` (48 days ÷ 30-day threshold)
   - `cross_repo_blocking: false`
5. **Severity assigned** as `Suggestion` per the §Classification and
   prioritisation matrix: `age_multiplier > 1×` but `< 2×`, not
   blocking, no other Critical-row trigger.
6. **Specialist-match miss recorded.** The skill scans the
   `nolte-shared` plugin's `agents/` and `skills/` slugs against the
   finding's content fingerprint and finds no match. A roster-gap
   entry is recorded with the stable token
   `discussion/yaml-tooling-vendoring`.
7. **Recurrence counted.** Per §Specialist recommendation the skill
   reads the most recent prior `.audits/portfolio-inflight/*.md` and
   matches gap-findings by their
   `<data-source>/<finding-class-token>` tag. It walks back through
   the artefacts in reverse chronological order and finds the same
   tag in both `2026-04-22.md` and `2026-03-22.md`. Adding the
   current occurrence, recurrence count is **3**, which meets the
   3-recurrence threshold from `continuous-improvement` §Portfolio
   gap closure.
8. **User-confirmation gate triggered.** Per §Specialist
   recommendation the 3-recurrence escalation is a load-bearing
   skill-side decision. The skill presents the operator with a
   per-step dialogue, naming the recurrence history:

   ```text
   Roster gap "discussion/yaml-tooling-vendoring" has now appeared
   in three audits (2026-03-22, 2026-04-22, 2026-05-23). Escalate
   the recommendation from "no specialist matches" to
   "author a new specialist"?

   [y] escalate    [n] keep as Suggestion-grade roster-gap entry
   ```

   The skill waits for the operator's response and records the
   choice in the `## Processing log` of the Findings-Report.
9. **Findings-Report written** at
   `.audits/portfolio-inflight/2026-05-23.md` per the
   `review-plan`-mandated four sections. If the operator accepted
   escalation, the finding reads roughly:

   ```text
   [portfolio-inflight-management §Specialist recommendation]
   Suggestion — home-assistant-addon/discussion/41
   driver: stalled discussion (48d open, no maintainer reply)
   axes: security_relevance=false, release_blocking=false,
         age_multiplier=1.6×, cross_repo_blocking=false
   tag: discussion/yaml-tooling-vendoring
   roster-gap recurrence: 3 (2026-03-22, 2026-04-22, 2026-05-23)
   recommend: author a new specialist (per continuous-improvement
              §Portfolio gap closure; 3-recurrence threshold met)
   ```

   If the operator declined, the recommend line stays at "no
   specialist matches; roster gap recorded" with the recurrence
   count noted for the next audit cycle.
10. **Per-severity counts confirmed** in the closing message, plus
    the escalation outcome from step 8 surfaced verbatim so the
    operator can trace the decision.
11. **Hard rules honoured.** The skill never authors the new
    specialist itself (that is a separate `skill-management` or
    `agent-management` flow); the audit's only write target is
    `.audits/portfolio-inflight/2026-05-23.md` in `claude-shared`;
    no mutating `gh api` call; the recurrence-count read is
    strictly read-only against the prior audit artefacts; `Suggestion`
    is written in Title Case (no `SUGGESTION`).
