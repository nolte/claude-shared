# Example 01: Fresh run for a new bounded context

## Input prompt

"Identify the audiences for our new `payments-webhook-router` module before I start writing its README."

## Input files (optional)

- `spec/project/audience-identification/en.md` — canonical methodology spec (precondition input)
- `modules/payments-webhook-router/` — the bounded context (no audience artifact yet)
- `modules/payments-webhook-router/README.md` — partial README under construction (may already hint at consumers)

## Expected behaviour

1. Verify the precondition: confirm `spec/project/audience-identification/<canonical_language>.md` is reachable, resolve `<canonical_language>` from `spec/.spec-config.yml`, and stop with a pointer to the spec if it is missing — never improvise a replacement methodology.
2. Open operation `run` step 1 by prompting the user to declare the bounded context in writing (what `payments-webhook-router` *is*, where its boundaries run, what is explicitly outside such as upstream payment providers and downstream ledger services); refuse to enumerate audiences until the written context is captured, then locate the artifact (step 2) by grepping the repo for existing `AUDIENCES.md`, README "Audiences" / "Intended consumers" sections, and audience-related ADRs, and propose `modules/payments-webhook-router/AUDIENCES.md` only if no precedent contradicts it.
3. Walk the five relationship categories one at a time in spec order (Direct consumers → Operators → Contributors / maintainers → Governing parties → Indirect audiences), capture per audience the label / category / interaction surface / expectation / open question, default every entry to `assumed` (never `confirmed` without an explicit user statement), offer criticality ranking and optional subdivisions only when the user can express them, and finally write the artifact at the confirmed path using `templates/audiences.template.md` with all five categories addressed (or explicitly marked `none` with reason) — confirm the resulting path back to the user in their language.
