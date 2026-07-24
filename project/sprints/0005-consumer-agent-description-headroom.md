---
number: 0005
status: closed
started: 2026-07-19
ended: 2026-07-19
value_statement: "Consumer repositories can enable the shared nolte plugins and still keep enough room for their own agents, without Claude Code's agent-description routing budget tripping the ~15k warning."
artifact_ref: "nolte-shared@0.1.11"
last_commit: c00bcb1fa664b71281977f22c8d3ae4214e7689b
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
- [F-7](`../features/shared-agent-description-remediation.md`) — status: done
- [F-8](`../features/agent-description-budget-guardrail.md`) — status: done

## Out of scope

- Deep agent/skill rework — merge, split, retire, or rewrite beyond descriptions — deferred to follow-on features under R-9 (the pre-analysis artifact's P5).
- Any implementation of a `nolte-shared` plugin-boundary split; F-5 decides and documents the boundary, but executing a split is out of scope for this sprint.
- Consumer-repository local `.claude/agents/` edits; each consumer owns its own agent-description share.

## Review notes

Closed 2026-07-19 by `sprint-review`. All four features (F-5–F-8) are `done` and merged to `develop`, shipped in release **v0.1.11**.

**Value verification.** Verifier: `features/agent-description-budget-guardrail.md` (F-8), `verifies_sprint_value: acceptance-1`, checked. The per-plugin agent-description budget guardrail in `scripts/validate_skills.py` measures each plugin's aggregate `description` weight (the 4-char/token method), holds the F-7 baseline, and fails Critical on regression — green in CI on the develop tip. The reclaimed headroom (~9,227 → ~7,064 est. tokens, −23.4%) is now durable, not a one-off trim.

**Artefact validation (Claude plugin).**
- `git rev-parse v0.1.11` → `c00bcb1fa664b71281977f22c8d3ae4214e7689b` (equals `last_commit`).
- `gh release view v0.1.11 --json isDraft` → `{"isDraft": false}`; published 2026-07-19T21:58:07Z.
- Marketplace resolution: `.claude-plugin/marketplace.json` `metadata.version` = 0.1.11; all four version-bearing files aligned at 0.1.11.
- Required checks (lint, test, docs, links) all SUCCESS on the develop tip.

**Release-skill-layer chain.** Chained: `release-publish-trigger` dispatched `release-publish.yml` (run 29705286747, conclusion success), publishing v0.1.11 (<https://github.com/nolte/claude-shared/releases/tag/v0.1.11>). `release-notes-curate` was not run separately; the release-drafter draft body was sufficient for this internal-improvement release.

**Blog-trigger deferrals.** No unconsumed blog-trigger deferrals (`project/blog-triggers/` carries no `deferred` entries).

**Delivered artefacts.**
- the F-5 structural analysis (retired to git history) — F-5 structural analysis + the keep-and-slim boundary verdict (bound by `spec/claude/plugin-scoping/`).
- the F-7 post-remediation baseline (retired to git history) — F-7 recorded baseline.
- `spec/claude/agent-management/` §Description contract + `spec/claude/skill-agent-frontmatter/` digest update — F-6.
- 54 normalised agent descriptions — F-7.
- `check_agent_description_budget` guardrail + tests in `scripts/validate_skills.py` / `tests/test_validate_skills.py` — F-8.

**Follow-on (deferred, out of scope this sprint).** Deeper agent/skill rework (merge / split / retire / rewrite beyond descriptions) and the consumer-audience authoring-plugin carve-out (evaluated and declined *for the agent-description budget* in F-5, but left open as a skill-budget/audience question) remain to be decomposed — they need fresh roadmap items and features, since R-9's own features are all delivered here.
