# Example 03: Revisit after a scope change introduces a new stakeholder

## Input prompt

"We just signed a contract that puts `services/billing-api` under PCI-DSS scope and a new compliance team will review every release — please revisit the audiences."

## Input files (optional)

- `spec/project/audience-identification/en.md` — canonical methodology spec (precondition input)
- `services/billing-api/AUDIENCES.md` — existing artifact (current audiences: API consumers, on-call operators, internal contributors); no governing-party entry yet
- `services/billing-api/README.md` — mentions the new PCI-DSS scope in passing but the audience list has not been updated

## Expected behaviour

1. Verify the precondition (spec reachable), confirm the user-signalled scope change qualifies as material per the spec (new regulated data class + new stakeholder both apply), and load the existing artifact without writing anything yet.
2. Re-run operation `run` steps 1–7 as a *diff* against the existing artifact: re-confirm the bounded-context declaration in writing (capture that PCI-DSS scope is now inside the boundary), then walk the five categories and classify each existing entry as `stays` / `needs re-validation` / `becomes irrelevant`, and propose new entries (notably a Governing parties entry for the compliance review team with interaction surface = release-gate sign-off, expectation = PCI-DSS evidence per release, tag = `assumed` until the user explicitly confirms a named representative).
3. Surface the diff to the user item by item and require explicit acceptance per change before persisting; never auto-promote the new compliance-team entry to `confirmed`, never silently drop existing entries even if they look stale (mark them `needs re-validation` instead), and write back to the same artifact path only after every diff item has been accepted — confirm the updated path back to the user in their language.
