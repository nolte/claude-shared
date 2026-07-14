# Why this is a skill, not an agent

The `skill-vs-agent` design rationale for `pull-request-merge`.

- **Externally-visible mutations gate on user confirmation** — flipping draft → ready, applying the `automerge` label, and (in the fallback path) calling `gh pr merge --squash --auto` all act on a shared GitHub PR; mid-flow user gating is core to the contract and would be lost in an agent's fire-and-forget shape.
- **Orchestrator that chains other skills** — this skill dispatches `review` and (conditionally) `security-review` mid-flow, then conditionally hands off to `workflow-health` triage on failure; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- **Wait mode requires visible status updates per round** — bounded polling for required-check completion has a hard "every wait round produces a visible status line" rule, which only works inside a skill that stays in the main conversation.
- Counter-dimension considered: a tool-restricted agent (read + a single `gh` Bash) could perform the verification half (steps 1, 4, 7) cleanly, but the externally-visible-mutation half (steps 5, 6) needs the user in the loop — keeping the whole flow in one skill is simpler than a forced split.
