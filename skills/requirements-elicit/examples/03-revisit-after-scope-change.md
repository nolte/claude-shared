# Example 03 — Revisiting the artifact after a prototype-driven scope change (IKIWISI)

Exercises the `revisit` operation: the user has built a prototype, seen
it, and changed their mind (the IKIWISI feedback loop). The skill re-runs
the interview as a *diff* against the existing artifact rather than from
scratch, resetting confidence only where the change invalidates it.

## Input prompt

> I threw together a quick prototype of the houseplant tracker and
> realised I actually need it to work for a shared household — multiple
> people watering the same plants. Update the requirements.

## Input files

The existing `project/requirements/houseplant-tracker.md` from Example 01,
written for a single-owner assumption throughout the gap matrix.

## Expected behaviour

1. **Recognises a material scope change.** A new actor (household members)
   plus a shared-ownership constraint triggers `revisit`, not a fresh
   `elicit` — the artifact is amended, not replaced.
2. **Presents the change as a diff.** The skill shows which requirements
   **stay** (watering-interval reminders), which need **re-validation**
   with their `c_d` reset (notification target, plant ownership), and
   which become **irrelevant** (single-owner assumptions).
3. **Adds the new dimension evidence.** The `actors` dimension gains a
   second actor; the `constraints` and `scope_boundaries` cells are
   re-opened and their `c_d` dropped until the user confirms the new
   shared-household behaviour via teach-back.
4. **Persists per accepted diff item.** Nothing is written until the user
   accepts each diff line; confirmed changes update the requirement list,
   the gap matrix, and the surviving-assumptions section in place.
5. **Keeps confirmed work.** Requirements untouched by the scope change
   keep their existing `confirmed` tags and `c_d` — the skill does not
   re-ask what the change didn't invalidate.
