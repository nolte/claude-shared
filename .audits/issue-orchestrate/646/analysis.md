---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "646"
classification: "spec-change"
route: "direct"
status: approved
created: "2026-09-19"
group: "2026-09-19-runner-slot-economy"
---

# Issue Orchestration — Pre-analysis (member of a group run)

- **Classification:** spec-change. **Route:** direct. **Requirements gate:** operator
  override at the group write gate (decision: extend §Cancellation rates with the fork,
  add the queue-time MUST and the capacity routing; existing MUSTs untouched).
- **Asserted cause verified:** the spec attributes mass cancellation to one cause and
  observes no queue time: confirmed by reading `workflow-health/en.md:102-107` before
  editing (three MUSTs: observe rate, treat majority-cancelled as absent, re-place the
  trigger; no wait metric anywhere: `grep -n -i "queue\|wait\|started_at" en.md` → none).
  kamerplanter cancellation rates re-measured (group artifact): 88 / 74 / 42 % of
  concluded runs, none of the lanes slower than a push.
- **P1 spec** → `nolte-shared:spec` (inline): three MUST bullets appended to §Cancellation
  rates (two-cause fork with churn, queue-time observation on `needs:`-free jobs,
  capacity routing to §L), two acceptance criteria; EN + DE. The consuming repository's
  numbers appear as an observation with date, not as a threshold (issue's delimitation).
- **Vale:** "auto-merge" → "automerge", one quote-punctuation rewording.
- **Refutation:** none.
