# Example 02 — large feature-request, routed to the formal pipeline

Demonstrates the pipeline route: a feature-request issue that spans more than one
goal outcome is comprehended and classified, but instead of being decomposed for
direct implementation it is handed to the formal `roadmap → feature → sprint`
pipeline. The orchestration stops after the hand-off; the planning skills own the
rest. This is the guard against bypassing the planning layer.

## Input prompt

> Nimm dir Issue #277 vor und setz es um. Da geht's um ein
> portfolio-weites Issue-Dashboard plus eine neue Benachrichtigungs-Integration —
> ich glaube das ist größer.

## Input files

Repository state when the skill is invoked:

- `spec/project/issue-orchestration/en.md` — present (canonical).
- Issue #277 `enhancement`-labelled: body asks for (a) a cross-repository issue
  dashboard rendered into the docs site, and (b) a new notification integration that
  posts triage outcomes to an external channel. Two distinct capabilities.
- `project/goals.md` — present; the dashboard maps to an existing outcome, the
  notification integration maps to no existing outcome.
- `project/roadmap.md` and `project/sprints/` — present.
- `skills/feature-decompose/SKILL.md` and `skills/roadmap-plan/SKILL.md` — present.
- `gh auth status` — authenticated.

## Expected behaviour

1. **Preconditions pass.** Repo, auth, and spec presence confirmed.
2. **Acquire.** The skill reads the full issue surface and scans `project/goals.md`,
   `project/roadmap.md`, and `project/features/` for prior art. It finds the
   dashboard relates to an existing outcome but the notification integration has no
   outcome yet. It confirms the acquired scope with the operator.
3. **Classify `feature-request`.** Primary class `feature-request`, rationale "two new
   capabilities, one mapped to an existing outcome, one needing a new outcome".
4. **Recognise this is not bounded.** During decomposition the skill determines the
   issue spans two goal outcomes and would need more than one coherent PR strand, and
   that the notification integration would create a new roadmap item. Per the spec's
   §Routing, this is a pipeline issue, not a direct one.
5. **Write the pre-analysis artifact with `route: pipeline`.** The artifact at
   `.audits/issue-orchestrate/277/analysis.md` records the classification, the
   in/out-of-scope split, the two capabilities, and the routing rationale. It records
   the hand-off targets: `feature-decompose` for the dashboard (existing outcome),
   `roadmap-plan` for the notification integration (new outcome). No work packages are
   dispatched and no features or roadmap items are drafted inline.
6. **Route gate.** The skill presents the route decision as an explicit operator
   gate. The operator confirms `pipeline`.
7. **Hand off, don't implement.** The skill invokes `roadmap-plan` to queue the new
   notification-integration outcome, then `feature-decompose` for the dashboard
   against its existing roadmap item — each is a separate skill that owns its own
   spec. The orchestrator does not draft the roadmap item or the feature body itself.
8. **Stop after hand-off.** The orchestration ends here; `feature-decompose`,
   `sprint-plan`, and `sprint-execute` carry the work forward on their own cadence.
   The skill posts the artifact summary to #277 (operator-confirmed) and reports the
   issue number, classification (`feature-request`), route (`pipeline`), the two
   hand-off targets, and the artifact path. No PR is opened by this orchestration.
9. **No planning bypass.** The skill does not decompose the issue into directly
   dispatched work packages, does not draft features or roadmap items inline, and does
   not mix a partial direct implementation with the pipeline route.
