---
number: 0005
status: active
started: 2026-07-19
ended: null
value_statement: "Consumer repositories can enable the shared nolte plugins and still keep enough room for their own agents, without Claude Code's agent-description routing budget tripping the ~15k warning."
artifact_ref: null
last_commit: null
roadmap_items: [R-9]
features: [F-5, F-6, F-7, F-8]
---

## Goal

Give every downstream repository that installs the `claude-shared` marketplace enough agent-description headroom to add its own agents without tripping Claude Code's ~15k-token routing-budget warning. The shared plugins today load roughly 9k of that budget into every consumer's context on every turn, leaving a repo like `kamerplanter` only ~6k for its own agents. By sprint close, the shared side is analysed and measured (F-5), a documented agent-description contract exists (F-6), every shared agent description is normalised to it without loss of routing correctness (F-7), and a regression guardrail in `scripts/validate_skills.py` — run inside `task test` and the CI gate — freezes the reclaimed headroom so it cannot silently creep back (F-8).

The verifying acceptance criterion is `F-8:acceptance-1`: the guardrail measures the per-plugin aggregate agent-description token weight, holds the post-remediation baseline, and fails on regression. That guardrail is exactly the durable-headroom promise this sprint's value statement makes — a one-off trim would satisfy the letter of "reclaim headroom" but not the durability the consumers actually need.

Deeper agent/skill rework (merge, split, retire, or rewrite beyond descriptions) and any change to the `nolte-shared` plugin boundary are **decided** in F-5 but **deferred for implementation** to follow-on features under R-9; this sprint delivers analysis, contract, remediation, and guardrail.

## Features

- [F-5](`../features/shared-plugin-structural-analysis.md`) — status: done
- [F-6](`../features/agent-description-contract.md`) — status: done
- [F-7](`../features/shared-agent-description-remediation.md`) — status: ready
- [F-8](`../features/agent-description-budget-guardrail.md`) — status: ready

## Out of scope

- Deep agent/skill rework — merge, split, retire, or rewrite beyond descriptions — deferred to follow-on features under R-9 (the pre-analysis artifact's P5).
- Any implementation of a `nolte-shared` plugin-boundary split; F-5 decides and documents the boundary, but executing a split is out of scope for this sprint.
- Consumer-repository local `.claude/agents/` edits; each consumer owns its own agent-description share.

## Review notes

_Populated by `sprint-review` at closure._
