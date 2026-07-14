# Example 02 — Auditing an existing requirement artifact against the KPI checklist

Exercises the `validate` operation: a read-only audit of an already
written `project/requirements/<slug>.md` against the eight-item checklist,
reporting pass/fail per item and offering to fix only *mechanical* gaps
without ever inventing `confirmed` tags or `c_d` values.

## Input prompt

> Validate the requirements doc at
> `project/requirements/houseplant-tracker.md` before I decompose it.

## Input files

An existing `houseplant-tracker.md` that is mostly sound but has three
gaps: no `c_d` derives from a `k ≥ 2` self-consistency check (every score
is self-reported), one requirement is prose rather than EARS/CNL, and the
thresholds (`τ_low`, `τ_high`, `k`, question budget) are not stated.

## Expected behaviour

1. **Read-only audit.** The skill runs the eight-item checklist against
   the file and never rewrites requirements as part of validation.
2. **Per-item pass/fail.** It reports each item explicitly, flagging the
   three failures: the missing self-consistency-derived `c_d`, the one
   un-normalised requirement, and the unstated thresholds.
3. **Distinguishes fixable from load-bearing.** Missing dimension
   placeholders or a missing threshold block are mechanical gaps it
   offers to fill in place; the un-normalised requirement and the
   self-report-only scoring are flagged as needing a real elicitation
   turn, not a silent patch.
4. **Never invents.** While offering to fix mechanical gaps, the skill
   refuses to fabricate a `confirmed` tag, a requirement, or a `c_d`
   value — Hard rule "Never invent". A missing score becomes an open
   question, not a plausible fill-in.
5. **Routes forward.** It reports that the artifact is below threshold on
   the flagged dimensions and offers to re-run `elicit` on just those
   before the user hands off to `feature-decompose`.
