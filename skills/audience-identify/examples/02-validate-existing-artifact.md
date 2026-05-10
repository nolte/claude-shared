# Example 02: Validate an existing AUDIENCES.md with missing categories

## Input prompt

"Audit `libs/notification-client/AUDIENCES.md` against the audience-identification spec — I think we forgot a couple of categories."

## Input files (optional)

- `spec/project/audience-identification/en.md` — canonical methodology spec (validator input)
- `libs/notification-client/AUDIENCES.md` — existing artifact under audit; declares Direct consumers and Contributors but omits Operators, Governing parties, and Indirect audiences; several entries lack `confirmed` / `assumed` tags and the criticality column is absent throughout

## Expected behaviour

1. Verify the precondition (spec reachable at `spec/project/audience-identification/<canonical_language>.md`), then load the artifact at the user-supplied path without modifying it; refuse to proceed if the spec is missing.
2. Run the operation `validate` checklist item by item against the artifact and report pass/fail per item: bounded context declared in writing before any entry, all five relationship categories addressed (or `none` + reason), every entry has label / category / interaction surface / expectation / open-questions field, every entry tagged `confirmed` or `assumed`, criticality ranking present or openly marked unresolved, and artifact co-located with its bounded context — flagging the missing Operators / Governing parties / Indirect audiences categories, the absent tags, and the missing criticality ranking.
3. Offer to fix only the mechanical gaps in place (insert the three missing category placeholders with `none — open question` markers, default missing tags to `assumed`, add an "unresolved" criticality marker), explicitly refuse to invent `confirmed` tags or new audience entries during the fix, and surface the remaining substantive gaps as open questions for the user to resolve in a follow-up `run` or `revisit` operation.
