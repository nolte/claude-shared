---
review-type: agent-review
target: "plugins/nolte-engineering/agents/license-check-scanner.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "92086e1803ec5667da892807749636461de55b39"
  - slug: skill-vs-agent
    revision: "92086e1803ec5667da892807749636461de55b39"
  - slug: review-plan
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
  - slug: agent-review
    revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
repo-revision: "e75ffbbafaf33cd55ae46dda966894add3ae01e4"
created: "2026-07-24"
status: open
---

# Agent Review: license-check-scanner

## Scope

Target: `plugins/nolte-engineering/agents/license-check-scanner.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none — full check set.
Read-only classification: read-only inventory scanner holding `Bash` under the narrow exception; the body carries the required `## Read-only Bash justification` section, names the exact command set, and explicitly covers two of the sanctioned classes `agent-management` §Tool access adds — ephemeral tool runners (`npx --yes`, `uvx`) and network reads (`curl` against PyPI). The otherwise-`Critical` `Bash` finding is therefore downgraded and not raised.
Model-choice check applied under the widened rule (PR #480): `model: sonnet`, rationale stated inline in the rationale section — conformant.
Explicitly out of scope: runtime behavior, Vale/markdown style, and whether the `license-check` skill's own SBOM-generation step is correct.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 0
- Info: 0

Go/no-go: CONDITIONAL — passes once discovery moves off `Bash find` and the description carries its negative trigger.
Next concrete action: author declares `Glob` and adds the CVE-scanning negative trigger.

## Findings

### Warning

- [ ] [agent-review.tool-scope] The justified command list includes `find . -maxdepth 3 -name "<manifest>"` for manifest and lockfile discovery — an operation the dedicated `Glob` tool covers — with no justification for choosing `Bash`; `agent-management` §Tool access and `agent-review` §Tool-scope both make preferring the dedicated tool a SHOULD. The sibling scanners (`kpi-signal-scanner`, `observability-audit-scanner`, `release-regression-scope-scanner`) all state the opposite convention explicitly.
      Where: `plugins/nolte-engineering/agents/license-check-scanner.md:48` (justification list) and `:107` (Phase 1 "Search the repo root and common subroots").
      Fix: add `Glob` to `tools:`, drop `find` from the justified command list, and state that manifest/lockfile discovery uses `Glob` / `Read` rather than shelling out — matching the sibling scanners' wording.
      Verify: `grep -n 'find \.' <file>` returns nothing; `tools:` lists `Glob`; `python3 scripts/validate_skills.py` stays green.
- [ ] [agent-review.description-quality] The `description` carries no negative trigger although the agent has a clear, body-acknowledged overlap with `dependency-audit-scanner` (both are read-only scanners dispatched over the same dependency tree); the agent's own hard rules end with "Never run a CVE / vulnerability scan; that is `dependency-audit-scanner`", so the delimitation is real but never reaches the routing budget.
      Where: `plugins/nolte-engineering/agents/license-check-scanner.md:3` (`description`) versus `:198` (hard rule).
      Fix: append one short negative trigger — `Don't use for CVE scanning (\`dependency-audit-scanner\`).`
      Verify: `description` names `dependency-audit-scanner`; `python3 scripts/validate_skills.py` stays green.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
