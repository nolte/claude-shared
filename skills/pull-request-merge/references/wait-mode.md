# Wait mode (pull-request-merge skill)

Reference content for the optional Wait-mode behaviour of the
`pull-request-merge` skill. The skill body keeps a one-paragraph
summary plus an explicit load trigger; the full contract — activation
signals, hard caps, implementation notes, and the rationale — lives
here so the SKILL.md stays under its soft length target.

## Table of contents

- [What wait mode is, and when it applies](#what-wait-mode-is-and-when-it-applies)
- [Activation](#activation)
- [Caps](#caps)
- [Implementation notes](#implementation-notes)
- [Why wait mode exists, and why it is bounded](#why-wait-mode-exists-and-why-it-is-bounded)

## What wait mode is, and when it applies

Default behavior of `pull-request-merge`: the skill is single-shot. When
step 4 finds pending checks, or step 7a finds the PR still `OPEN`, the
skill reports and stops; the user re-invokes the skill once GitHub is
in the next state. This is cheap, deterministic, and respects the
prompt-cache window.

**Wait mode** is an explicit user opt-in that lets the skill wait for
state transitions inside a single invocation. It is bounded by hard
caps so it cannot drift into long unattended runs.

## Activation

Wait mode is activated when the user invokes the skill with one of
these signals (the caller selects whichever the harness supports):

- A `--wait` argument on the skill invocation (preferred when the
  harness passes args through to the skill).
- An explicit instruction in the prompt that asks the skill to wait
  (for example "warte bis CI grün ist", "wait until checks pass and
  then merge"). When the user's intent is unambiguous, the skill MAY
  enter wait mode without an explicit `--wait` flag.

Without one of those signals, default behavior wins and pending state
stops the run.

## Caps

Wait mode MUST honor every cap below. They exist to keep the prompt
cache useful, to make the run cost-bounded, and to avoid silent
runaway:

- **Interval ≥ 60s** between consecutive re-checks (default 90s; never
  less than 60s).
- **Wall-clock timeout ≤ 15 min** total (default 10 min; never more
  than 15 min).
- **Max retries ≤ 10** consecutive re-checks per wait point (step 4 or
  step 7a counts independently).
- **Visible status line per round** — every re-check emits a one-line
  status update so the user sees the cadence; silent background
  polling is a hard violation.
- **Failure short-circuits** — a `FAILURE` on any required check
  terminates wait mode immediately; the skill routes to
  `workflow-health` triage as documented in step 4 / step 7b of
  SKILL.md.

The user MAY relax the defaults toward the caps
(`--wait-interval=120s`, `--wait-timeout=15m`, `--wait-retries=10`) but
MUST NOT exceed them. Tightening below the floors (interval `<60s`,
timeout `<60s`, retries `<1`) is not permitted because it defeats the
purpose.

## Implementation notes

- **Step 4 (Verify required checks)**: use `gh pr checks <number>
  --watch --required` if the harness can pass through the resulting
  blocking call; otherwise re-invoke `gh pr checks` at the configured
  interval and parse the output. Either way, the caps apply end-to-end.
- **Step 7a (Verify the merge landed)**: re-invoke `gh pr view <number>
  --json state,mergedAt,mergeCommit` at the configured interval. There
  is no equivalent `--watch` for `gh pr view`, so the explicit
  re-invocation pattern is the only path.
- **Step 7b precedence**: the `merge_failed` audit takes precedence
  over wait mode: if the automerge workflow logs a `merge_failed`, the
  skill stops waiting and surfaces the workflow-health classification,
  regardless of remaining time budget.

## Why wait mode exists, and why it is bounded

A single skill invocation that finishes the whole merge — no manual
re-runs — is a real ergonomic win when CI is fast and the only thing
missing is a 30-second `automerge / automerge` round-trip. The
single-shot default exists because the prompt-cache TTL is 5 min and
unbounded polling burns the cache for every retry. The caps balance
the two: short waits (<5 min) stay cache-warm, longer waits accept one
cache miss but never balloon, and the visible-status-per-round rule
keeps the user in the loop.
