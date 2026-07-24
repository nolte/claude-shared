---
review-type: agent-review
target: "plugins/nolte-engineering/agents/implementation-plan-author.md"
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

# Agent Review: implementation-plan-author

## Scope

Target: `plugins/nolte-engineering/agents/implementation-plan-author.md` (frontmatter + full body; no external referenced assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter). Two further specs are load-bearing for the tool-scope finding and are cited per finding: `spec/claude/trusted-author-injection-guard/` §Consumer obligations and `spec/claude/mcp-tool-preference/` §Authoring convention.
Narrowing: none — full check set.
Read-only classification: **write-capable** (read-and-plan agent that persists exactly one artifact via `Write`); the read-only tool bans don't apply, and the neutral `## Bash justification` heading is the correct form per `agent-management` §Tool access.
Model-choice check applied under the widened rule (PR #480): `model: opus` with an explicit `## Model pin` rationale — conformant.
Explicitly out of scope: runtime behavior, Vale/markdown style, and the correctness of the three sanctioned input paths themselves (owned by `spec/project/issue-orchestration/`).

## Summary

- Critical: 2
- Warning: 1
- Suggestion: 0
- Info: 1

Go/no-go: FAIL — two MUST violations on the MCP tool surface.
Next concrete action: author grants the two GitHub MCP read tools in `tools:` and cites `mcp-tool-preference` in the body.

## Findings

### Critical

- [ ] [agent-review.tool-scope] The body's trust-boundary resolver calls the MCP tools `github:get_me` and `github:list_repository_collaborators`, but neither is granted in the `tools:` frontmatter — a used-but-undeclared tool, which `agent-review` §Tool-scope classifies `Critical`; `trusted-author-injection-guard` §Consumer obligations states the same rule as an explicit MUST for exactly these two names.
      Where: `plugins/nolte-engineering/agents/implementation-plan-author.md:5` (`tools:`) versus `:110-111` (resolver prose).
      Fix: add `mcp__github__get_me, mcp__github__list_repository_collaborators` to `tools:` (both are already in the repo's `.claude/settings.json` allowlist, so no allowlist change is needed).
      Verify: `grep 'mcp__github__' <file>` lists both names in `tools:`; `python3 scripts/validate_skills.py` stays green.
- [ ] [mcp-tool-preference.authoring-convention] The agent adopts the MCP-preferred read path (MCP tools named in prose with a `gh api` fallback) but never references `spec/claude/mcp-tool-preference/`, which that spec requires of every adopting artefact as a MUST so a reader knows the path is optional and `gh` stays authoritative.
      Where: `plugins/nolte-engineering/agents/implementation-plan-author.md:107-114` (§Writes vs researches, trust-boundary paragraph).
      Fix: cite `spec/claude/mcp-tool-preference/` in the same paragraph, next to the existing `gh api` fallback clause.
      Verify: `grep -c 'mcp-tool-preference' <file>` ≥ 1; the sibling `release-regression-scope-scanner` shows the reference form.

### Warning

- [ ] [agent-review.prompt-structure] The system-prompt body is 222 lines, over the ~200-line soft target `agent-management` §Recommendations names; the excess is the three sanctioned input paths (issue-driven / audit-driven / review-driven) enumerated four times — opening, §Preconditions, Step 1, Step 4.
      Where: `plugins/nolte-engineering/agents/implementation-plan-author.md:33-254` (whole body).
      Fix: compress the per-path restatements so each path's artifact path, grounded source, and write target are stated once and cross-referenced thereafter.
      Verify: body line count (total minus frontmatter) drops to ≤ 200 and every one of the three paths still names its grounded source and its write target.

### Info

- [ ] [agent-management.tool-access] The `## Bash justification` section correctly uses the neutral heading (not `## Read-only Bash justification`) because the agent is write-capable overall, and states that `Bash` itself stays read-only — the exact distinction `agent-management` §Tool access draws for write-capable agents that also need a shell.
      Where: `plugins/nolte-engineering/agents/implementation-plan-author.md:83-85`.
      Fix: n/a (observation — conformant).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
