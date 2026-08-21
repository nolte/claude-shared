# Why this is a skill, not an agent

Per `spec/claude/skill-vs-agent/` — the rationale for `issue-orchestrate`'s artifact type.

- **Externally-visible mutations gate on operator confirmation.** Issue-scope
  confirmation, the classification call, the pre-analysis approval, the route
  decision, each specialist dispatch, and the PR title / body are mid-flow operator
  dialogues; an agent's fire-and-forget shape would miss them.
- **Orchestrator pattern (per `skill-vs-agent`).** The work is *analyse, decompose,
  route, dispatch, verify*; the dispatched specialist does the editing. The
  orchestrator stays in the main thread and chains other skills (`feature-decompose`
  or `roadmap-plan` for the pipeline route, `quality-gate`, `pull-request-create`).
- **Multi-phase state accumulates across prompts.** A decomposition, a route
  decision, and per-package dispatches span many turns; a skill's persistent
  instruction context and the resumable-work envelope fit that naturally.
- Counter-dimension considered: a narrow agent could own the decomposition alone and
  gain context-window protection, but every downstream lane (routing, dispatch,
  verification, PR annotation) is interactive, so one orchestrating skill beats a
  split at the decomposition boundary.
