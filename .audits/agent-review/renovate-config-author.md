---
review-type: agent-review
target: "agents/renovate-config-author.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "4ceb6872"
  - slug: skill-vs-agent
    revision: "66d65137"
  - slug: review-plan
    revision: "7be3b552"
  - slug: agent-review
    revision: "27cbff13"
repo-revision: "dcae99d19e32b45a38c8aff288ab34eab2ee9732"
created: "2026-11-18"
status: open
---

# Agent Review: renovate-config-author

## Scope

Target: `agents/renovate-config-author.md` (frontmatter, body, and the three `spec/` paths the body cites; the agent has no supporting asset).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none.
Explicitly out of scope: runtime behavior of the agent, Vale/markdown style (handled by `task lint`), the orchestrating skill beyond confirming the dispatch direction.

## Summary

- Critical: 0
- Warning: 0
- Suggestion: 0
- Info: 5

Go/no-go: PASS
Next concrete action: none required; the Info items record observations for the maintainer.

## Findings

### Critical

None. Checked: filename and `name` agree and are ASCII kebab-case; `distribution: plugin` with no `hooks`, `mcpServers`, or `permissionMode`; no `model` pin; every declared tool (`Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`) is used in the body and no undeclared tool is used; single responsibility and an `## Output contract` are stated; no `Agent(`, `subagent_type`, or `Task(` in the body; the rationale names decisive dimensions; the body cites `spec/project/project-structure/`, `spec/claude/claim-provenance/`, and `spec/claude/dispatch-brief/`, and all three exist.

### Warning

None. Checked: the description carries positive triggers and negative triggers that name the overlapping peers (`project-structure-apply`, `dependency-audit`, `backlog-delivery-orchestrate`) and makes no proactive-delegation claim; the write-capable agent documents its shell use under a neutral `## Bash justification` that names the command classes and their effects, per `agent-management` §Tool access; role and boundaries open the body and the output format closes it as the report phase; the body says the agent writes configuration, not application code; write effects have stated preconditions; no hard-coded absolute path; the body is English.

### Suggestion

None. The rationale names a counter-dimension.

### Info

- [ ] [agent-review.no-skill-dispatch] The grep for `Skill tool` matches one line, and that line is a prohibition, not a dispatch.
      Where: `agents/renovate-config-author.md:79` ("Call the `Skill` tool or dispatch other agents." under "You don't").
      Fix: n/a (observation). Eighteen agents under `agents/` carry the same negated sentence.
      Verify: n/a.
- [ ] [agent-management.body-length] The body is about 4,279 estimated tokens (4-char heuristic), long for an agent; no agent body cap exists in `scripts/validate_skills.py`.
      Where: whole body.
      Fix: n/a (observation). The authoring and verification rules are the agent's substance; splitting them would need a supporting asset, which `agent-management` §Structure doesn't allow beside an agent file.
      Verify: n/a.
- [ ] [agent-management.resumable] `resumable` isn't declared. The agent has an authoring and a verification phase, but its intermediate artefact is the diff in the working copy, which an interruption doesn't lose; the rationale section says so.
      Where: frontmatter; `## Why this is an agent, not a skill`, "No persisted run state".
      Fix: n/a (observation).
      Verify: n/a.
- [ ] [agent-review.spec-anchor] The agent cites three specs, but none of them governs Renovate authoring; the body states that no such spec exists and anchors on the validator and dry run of the Renovate version in use. The spec corpus may need to grow if the authoring rules are to be normative.
      Where: `## What this agent anchors on`.
      Fix: n/a (observation).
      Verify: n/a.
- [ ] [agent-review.scope] The verification steps prescribe Renovate commands whose flags were checked against Renovate's documentation and source at commit `428581e9`, not by execution: no Renovate binary was available when the agent was authored. This review covers the artifact, not its live behavior.
      Where: `## Verification`.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
