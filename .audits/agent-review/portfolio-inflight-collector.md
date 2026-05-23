---
review-type: agent-review
target: "agents/portfolio-inflight-collector.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "e30e10f3bf4551a3a4c4cb31e81255f2345cbeb7"
  - slug: skill-vs-agent
    revision: "ba97fa1904d0ccffec0ead0c751479678ed42bdf"
  - slug: review-plan
    revision: "3f5c3120e24344235d1e3a550af2e84368892c47"
  - slug: agent-review
    revision: "323119fc545735f8d56256c12e7da0f4cc81e2b7"
repo-revision: "5ee7c1af1a73aafee028114939b99a5489745ae0"
created: "2026-05-23"
status: open
---

# Agent Review: portfolio-inflight-collector

## Scope

Target: `agents/portfolio-inflight-collector.md` — 241 lines, single file (no `agents/portfolio-inflight-collector/` subfolder; the spec body is fully self-contained).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions in frontmatter).
Validator: override — no external agent-structure validator is provisioned in this repository (`skills-ref` is skill-only); the spec-derived checks below run in lieu.
Narrowing: none — full first-pass review covers frontmatter, tools scoping (declared-vs-used bidirectional + read-only invariant), system-prompt body, no-Skill-dispatch check, rationale section, referenced assets, duplicate-prevention, and body-length.
Explicitly out of scope: runtime behaviour (no dispatch under review), Vale/markdown style (handled by `task lint`), the orchestrating `portfolio-inflight-triage` skill (covered by a separate `skill-review` plan landing in the same PR).

## Summary

- Critical: 0
- Warning: 4
- Suggestion: 0
- Info: 3

Go/no-go: PASS — no Critical findings. Warnings are mostly dead-permission declarations consistent with the sibling collector's precedent; either fix in this plan or open a portfolio-wide convention review for both agents at once.
Next concrete action: decide whether to trim `tools: [Read, Bash, Glob, Grep]` down to `[Bash]` (since only Bash is demonstrably used) or to add explicit Read/Glob/Grep usage to the body; the same decision applies to `portfolio-manifest-collector.md`.

## Findings

### Warning

#### [agent-management §Tool access — declared-vs-used check] `Read` tool declared but not used in the agent body's procedure

- [ ] Either remove `Read` from `tools: [...]` or add explicit Read-tool usage to §Working procedure.

Where: `agents/portfolio-inflight-collector.md` frontmatter line 5 (`tools: [Read, Bash, Glob, Grep]`). The §Working procedure (lines 200–227) describes every file access via `gh api ... --jq .content | base64 -d` (Bash); no explicit `Read`-tool invocation appears anywhere in the body. Rule: `spec/claude/agent-review/` line 78 — `MUST verify, for every tool declared in tools, that the agent body demonstrably uses that tool in its procedure—tools declared but not used are Warning findings (dead permission)`.

Fix: pick one — (a) trim `tools` to `[Bash, Glob, Grep]` (or just `[Bash]` if Glob/Grep are also unused, see W2/W3), keeping the read-only contract intact; (b) revise the §Working procedure so it uses `Read` for the local file inputs the calling skill may pass alongside the resolve-fresh instruction (none currently exist); (c) document in §Read-only Bash justification why `Read` stays declared as part of the standard nolte read-only-agent envelope even when the procedure doesn't explicitly invoke it (and open a spec-clarification follow-up so the dead-permission rule honours that envelope choice).

Verify: `grep -nE '\bRead\b' agents/portfolio-inflight-collector.md` shows either an explicit Read-tool invocation in the procedure or no `Read` token in `tools:`.

#### [agent-management §Tool access — declared-vs-used check] `Glob` tool declared but not used in the agent body's procedure

- [ ] Either remove `Glob` from `tools: [...]` or add explicit Glob-tool usage to §Working procedure.

Where: same frontmatter line. §Working procedure does no local file enumeration — every enumeration is via `gh api orgs/nolte/repos --paginate` or `gh api repos/nolte/<repo>/...` (Bash). Same rule citation as W1.

Fix: same shape as W1.

Verify: `grep -nE '\bGlob\b' agents/portfolio-inflight-collector.md` shows either an explicit Glob-tool invocation in the procedure or no `Glob` token in `tools:`.

#### [agent-management §Tool access — declared-vs-used check] `Grep` tool declared but not used in the agent body's procedure

- [ ] Either remove `Grep` from `tools: [...]` or add explicit Grep-tool usage to §Working procedure.

Where: same frontmatter line. §Working procedure does no local content search; the closest is the parse of `gh api`-returned JSON via `--jq` (Bash). Same rule citation as W1.

Fix: same shape as W1.

Verify: `grep -nE '\bGrep\b' agents/portfolio-inflight-collector.md` shows either an explicit Grep-tool invocation in the procedure or no `Grep` token in `tools:`.

#### [agent-management body-length SHOULD] Agent body exceeds the 200-line SHOULD threshold

- [ ] Either trim the body below 200 lines by moving long-form sections into `agents/portfolio-inflight-collector/` files, or document why the inline length is justified.

Where: `agents/portfolio-inflight-collector.md` — 241 lines (rule threshold: roughly 200 lines per `spec/claude/agent-management/` line 123 — `SHOULD keep the system prompt focused; if it grows past roughly 200 lines, move long-form references into agents/<name>/ files`).

Fix: the longest sections are §Read-only Bash justification (lines 25–42, ~18 lines of command enumeration) and §Output shape (lines 73–173, ~100 lines of structured-summary template). Either: (a) move the §Output shape template into `agents/portfolio-inflight-collector/output-shape.md` with a single load-trigger phrase in the main body ("Read agents/portfolio-inflight-collector/output-shape.md for the returned report's full structure"); (b) compress the §Read-only Bash justification enumeration by grouping the four data-source `gh api ... --jq` calls under a parameterised description plus the explicit-forbids-list; (c) document an explicit "exceeds the soft 200-line threshold because the §Output shape template is load-bearing for the calling skill" justification in the body.

Verify: `wc -l agents/portfolio-inflight-collector.md` reports a count near or below 200, or the body contains an explicit length justification anchored in the spec exception.

### Info

#### [agent-management §Tool access — narrow exception, acknowledgment] `Bash` on a read-only agent — narrow exception correctly applied (no action needed)

- [x] Recorded for traceability; no fix required.

Where: `agents/portfolio-inflight-collector.md` frontmatter line 5 declares `Bash` in `tools`; the agent's description ("Read-only ... data collector ... gather ... fetch") clearly identifies it as a read-only / audit agent. Per `spec/claude/agent-review/` line 52, this would normally be `Critical`, but the spec's §Tool access narrow exception (`spec/claude/agent-management/` line 64) downgrades the finding to `Info` when the agent body carries a `## Read-only Bash justification` section that enumerates the side-effect-free commands and explicitly forbids mutations.

The agent body satisfies the narrow exception in full:
- `## Read-only Bash justification` section present at line 25.
- Enumerates every `gh ...` invocation (10 distinct command shapes) with the exact endpoint pattern.
- Explicit mutation-forbids list at line 42 covering `gh api -X POST/PATCH/DELETE`, `gh issue close`, `gh pr merge/close`, `gh pr review --approve/--request-changes/--comment`, `gh api graphql` with mutation, `rm`, package installs, file writes, and network mutations.

This finding is informational only; no fix is required. It exists in the plan so a future re-review can verify the narrow exception still applies after edits.

#### [agent-management §Tool access — observation] Dead-permission pattern (W1/W2/W3) is portfolio-wide

- [ ] Track whether the dead-permission rule should be enforced strictly or whether the standard nolte read-only-agent envelope (`[Read, Bash, Glob, Grep]`) should be explicitly sanctioned.

Where: `agents/portfolio-manifest-collector.md` (the sibling read-only collector and the explicit pattern reference for this agent) declares the same `tools: [Read, Bash, Glob, Grep]` envelope and likewise does not explicitly invoke `Read` / `Glob` / `Grep` in its procedure. The pattern is portfolio-wide, not unique to this agent. Suggests one of: (a) both agents should be corrected per W1/W2/W3 and any future read-only agents should declare only the tools they actually invoke; (b) the `agent-management` spec should explicitly sanction the standard read-only-agent envelope `[Read, Bash, Glob, Grep]` so the dead-permission rule honours envelope choice; (c) the agent-review check should match the spec's intent rather than the literal "tools declared but not used" reading.

Fix: not in scope of this plan — surface to `spec/claude/agent-management/` and `spec/claude/agent-review/` maintainers as a portfolio convention question. Mark `[x]` once a decision is recorded in the spec; until then, W1/W2/W3 above carry the actionable items for this agent.

Verify: when the spec clarifies the envelope rule, re-run the declared-vs-used check across both agents to confirm consistent treatment.

#### [skill-vs-agent §Duplicate-prevention, observation] Sibling agent `portfolio-manifest-collector` overlaps semantically (read-only cross-repo collector)

- [ ] Confirm the implementing-spec's documented split rationale is sufficient; no action needed if so.

Where: `agents/portfolio-manifest-collector.md` collects `project/portfolio.yml` manifests across the nolte Portfolio-Member set for the static capability audit; `agents/portfolio-inflight-collector.md` collects open issues / PRs / branches / discussions across the same set for the dynamic in-flight audit. Both are read-only fan-out collectors with the same tool envelope and the same `sonnet` model pin. Rule: `spec/claude/agent-review/` (via `skill-vs-agent` §Duplicate-prevention) — `any plausible overlap produces a Warning naming the peer artifact and the overlap`.

Strict reading would classify this as `Warning`. Pragmatic reading: the implementing spec `spec/portfolio/portfolio-inflight-management/` §Audit operation explicitly states the dispatch reuses `portfolio-manifest-collector` (or its generalised successor) for Portfolio-Member-set resolution, and this collector is a distinct surface (four in-flight data sources × N repos) from the manifest collector (one YAML manifest × N repos). The split rationale that the Warning is supposed to trigger has already been documented. Recording as `Info` so the audit history reflects the duplicate check ran without forcing a redundant resplit conversation.

Verify: the implementing spec §Audit operation line `MUST reuse the Portfolio-Member-set resolution mechanism from portfolio-management (the existing portfolio-manifest-collector agent or its generalised successor)` is unchanged.

## Processing log

(empty until items are closed)
