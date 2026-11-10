# Why `pull-request-create` is a skill, not an agent

Read when reviewing or challenging the artifact-type choice.

- **Externally-visible action requires explicit confirmation.** `gh pr create` opens a PR that other humans see; the spec mandates presenting the title and body to the user and iterating until approval before invoking it. That gate is core to the contract.
- **Mid-flow interactivity.** Branch-freshness resolution (rebase vs merge), force-push confirmation, and the title/body iteration are per-step user dialogues an agent's structured-report shape can't carry.
- **Output flows back into the main conversation.** The diffed PR body, the touched-spec autolinks, and the resulting PR URL all live in the user's working context; isolating them behind an agent boundary would obscure the iterative drafting.
- Counter-dimension considered: a narrower agent could sharpen Conventional-Commits-title generation, but the load-bearing dimension here is the externally-visible-action gating, not title-prose quality; skill wins.
