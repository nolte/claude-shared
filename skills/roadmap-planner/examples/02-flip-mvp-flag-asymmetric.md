# Example 02: Flip the MVP flag — asymmetric rule in action

## Input prompt

Two requests in one session:

> (a) Flip `mvp` auf `true` für `R-4`.
> (b) Und auf `R-2` bitte `mvp` von `true` auf `false` zurücknehmen.

## Input files (optional)

- `project/mission.md` exists with `mvp_status: in_progress` (not yet `stabilised`).
- `project/roadmap.md` contains:
  - `R-2` with `mvp: true`, `status: active` (currently being worked on).
  - `R-4` with `mvp: false`, `status: proposed`.

## Expected behaviour

1. For request (a): locate `R-4`. Read `mission.md`; `mvp_status` is `in_progress`, not `stabilised`, so `false → true` is allowed under the mission-spec asymmetry. State the rule applied verbatim, show the diff, and confirm before writing.
2. For request (b): locate `R-2`. Detect `status: active`; the mission-spec asymmetry forbids `true → false` once an item entered `status: active` (removing it from MVP scope retroactively breaks the SMART achievability bound). Refuse with a verbatim error citing `spec/project/mission/`.
3. Offer the user the only legal alternatives for `R-2`: leave the MVP flag as `true`, or first revert `R-2` to `proposed` via a separate lifecycle-aware change (which this skill does not perform automatically because `active → proposed` is not a permitted transition).
4. Apply only request (a) on disk; perform end-to-end validation (outcomes resolve, `target_sprint` resolves, detail invariant holds, IDs unique, YAML key order intact) and write atomically. Refuse the entire write if any check fails.
5. Report which rule was applied to which item, and explicitly note that `R-2` was left untouched and why.
