---
review-type: agent-review
target: "plugins/nolte-engineering/agents/guard-coverage-scanner.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "4ceb68722175746746241f19fbc4ebc1cd8cfb81"
  - slug: skill-vs-agent
    revision: "4ceb68722175746746241f19fbc4ebc1cd8cfb81"
  - slug: review-plan
    revision: "4ceb68722175746746241f19fbc4ebc1cd8cfb81"
  - slug: agent-review
    revision: "4ceb68722175746746241f19fbc4ebc1cd8cfb81"
repo-revision: "4ceb68722175746746241f19fbc4ebc1cd8cfb81"
created: "2026-09-13"
status: in-progress
---

# Agent Review: guard-coverage-scanner

## Scope

Target: `plugins/nolte-engineering/agents/guard-coverage-scanner.md` (148 lines, one self-contained file, no `agents/guard-coverage-scanner/` sibling folder, no external assets).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review`, read from the tree at `repo-revision`. Specs the body cites were also read and resolve: `spec/project/defect-class-guards/` (G1, G2), `spec/project/quality-gate/` §"Enforced lane per tier", `spec/claude/claim-provenance/`, `spec/project/source-code-review/` D11.
Validator: `scripts/validate_skills.py` at `repo-revision` (the script carried no version constant then; `--version` reports it from 1.0.0 on).
Narrowing: none — full review.
Read-only classification: unambiguous ("Read-only scanner … writes nothing"; body "You read; you never write").
Trigger: 2026-Q4 spec-drift audit F6 (`.audits/spec-drift/2026-Q4.md`), which found neither a plan nor a close commit for this agent, added in #579.
Explicitly out of scope: runtime behaviour, Vale/markdown style (handled by `task lint`), and the dispatching skill `guard-coverage-check` beyond the dispatch direction and the brief it passes. That skill has no plan under `.audits/skill-review/` either.

## Summary

- Critical: 2
- Warning: 1
- Suggestion: 0
- Info: 4

Go/no-go: FAIL at creation — a spec named as normative input had no absent-spec fallback, and the body required reading a file outside the repository that the declared tools and its own hard rule exclude.
Next concrete action: the Info observations stay open until the next substantive edit decides them; the Criticals and the Warning closed on 2026-09-13.

## Findings

### Critical

- [x] [agent-management.runtime-location-spec-fallback] The body makes `spec/project/quality-gate/` §"Enforced lane per tier" normative input but never says what happens when that spec is absent; the fallback it gives covers only `defect-class-guards` and doesn't mention the installed `nolte-shared` spec tree.
      Where: `plugins/nolte-engineering/agents/guard-coverage-scanner.md:29` names both specs as required reading; Preconditions item 2 (`:106`) covers only `defect-class-guards`. Rule: `spec/claude/agent-management/en.md` §Runtime location (MUST).
      Fix: widen Preconditions item 2 to both specs, read an absent spec from the installed `nolte-shared` plugin, and fall back to the inlined G1/G2 definitions plus the Step 4 lane rules with the gap recorded in **Health**.
      Verify: `grep -n "installed \`nolte-shared\`" plugins/nolte-engineering/agents/guard-coverage-scanner.md` hits in Preconditions, and `validate_skills.py` no longer counts the agent in its spec-fallback backlog.

- [x] [agent-review.tool-scope-used-undeclared] Step 4 tells the agent to follow `.github/settings.yml`'s `_extends` pointer to the commons file. In the portfolio that pointer is cross-repository (`nolte/gh-plumbing:.github/commons-settings.yml`), which `Read`, `Grep`, and `Glob` can't reach and which the agent's own hard rule forbids.
      Where: `:128` against `:5` (`tools: Read, Grep, Glob`) and `:145` ("Never widen the scan beyond the repository root"). Rule: `spec/claude/agent-review/en.md` (a tool the body needs but doesn't declare is `Critical`). Impact: an inherited empty `contexts: []` — the skill's own gotcha — is exactly the case the agent can't see, which risks a false `verdict: enforced`.
      Fix: keep the read-only surface; use resolved required contexts from the dispatch brief when the pointer leaves the root, otherwise report the dependent verdicts as undetermined under **Health** and never set `enforced` from the local file alone. The dispatching skill passes the resolved contexts in its brief.
      Verify: no instruction in the body needs content outside the repository root; `:5` and `:145` stay consistent with Step 4.

### Warning

- [x] [agent-review.description-negative-trigger] `description` carries no negative trigger although `quality-gate-enforcer` in the same plugin overlaps: both judge whether a check sits in an enforced lane among the required status checks.
      Where: `:3`; the delimitation exists only in `dont_use_when` (`:16-17`) and the body (`:94`). Rules: `spec/claude/agent-review/en.md` and `spec/claude/agent-management/en.md` §Description contract (SHOULD).
      Fix: append "Don't use to audit the required-check set (`quality-gate-enforcer`)." to `description`.
      Verify: the `description` line names `quality-gate-enforcer` after "Don't use", and `python3 scripts/validate_skills.py` reports no `description-budget-regression`.

### Info

- [ ] [agent-review.model-absent] `model` isn't declared, so the agent inherits the caller's model.
      Where: frontmatter, `:1-23`. Rule: `spec/claude/agent-review/en.md` (MAY record Info).
      Fix: n/a (observation).
      Verify: n/a.

- [ ] [agent-review.info-severity-ownership] The Step 5 severity matrix is defined only in the agent body; neither `defect-class-guards` nor the dispatching skill owns it, and it leaves `claimed: unclear` with `verdict: advisory` and an under-claim (`specified` text, `enforced` verdict) without a severity.
      Where: `:132-136`; `spec/project/defect-class-guards/en.md` has no severity section.
      Fix: n/a (observation). No rule says where a scanner's severity criteria must live.
      Verify: n/a.

- [ ] [agent-review.info-internal-consistency] The clean-run finding (`rule: n/a`) has no assertion location, yet a hard rule says a finding without `path:line` for assertion and evidence "isn't a finding".
      Where: `:97` against `:147`.
      Fix: n/a (observation); carving `rule: n/a` out of the hard rule would remove the contradiction.
      Verify: n/a.

- [ ] [agent-review.info-delimitation-divergence] The `dont_use_when` alternatives are narrower than the dispatching skill's for the same situations: predicate audits route to `python-code-reviewer` (Python only) and "whether a test can fail at all" to `unit-test-reviewer` (unit tier only), where the skill routes to `source-code-review` and `test-pyramid-check`. All alternatives resolve.
      Where: `:14-19` against `plugins/nolte-engineering/skills/guard-coverage-check/SKILL.md:13-18`.
      Fix: n/a (observation); no rule requires agent and skill delimitation to match.
      Verify: n/a.

## Verified conformant

- Filename and `name` are ASCII kebab-case and match; no reserved token.
- `distribution: plugin`; none of `hooks`, `mcpServers`, `permissionMode`, and the body needs none of them.
- `phase: quality` is in the vocabulary; `tags` `[review, audit]` are starter tags; `summary` (125 chars) and `summary_de` (153) are within 200; every `use_when` / `dont_use_when` / `see_also` target resolves.
- The description states what the agent does and a concrete dispatch trigger; no dialogue turns, no "use proactively".
- `resumable` is absent, correct for a single read-only pass.
- `tools: Read, Grep, Glob` fits a read-only agent; each declared tool is used, and apart from the `_extends` Critical no undeclared tool is needed.
- One responsibility, an explicit write mode, an output shape fixed before the procedure, and a closing **Health** block.
- No `Skill(`, `Agent(`, `subagent_type`, or `Task(`; no hard-coded absolute path; English frontmatter and body.
- The rationale heading is exactly `## Why this is an agent, not a skill`, with decisive dimensions and a counter-dimension.
- 148 lines, under the ~200-line soft target.
- Duplicate prevention over all 62 agent descriptions (`agents/*.md`, `plugins/*/agents/*.md`): no equivalent capability; `quality-gate-enforcer` is adjacent and covered by the Warning above.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
- 2026-09-13 — runtime-location-spec-fallback — Preconditions item 2 covers both specs, reads an absent one from the installed `nolte-shared` plugin, and names the inlined fallback — verified: `validate_skills.py` spec-fallback backlog count dropped by one and the grep hits.
- 2026-09-13 — tool-scope-used-undeclared — Step 4 uses brief-supplied contexts for an out-of-root `_extends` target or reports the dependent verdicts as undetermined; `guard-coverage-check` Step 2 passes the resolved contexts — verified: re-read Step 4 against the tool list and the hard rule.
- 2026-09-13 — description-negative-trigger — `description` names `quality-gate-enforcer` as the negative trigger — verified: `validate_skills.py` reports no budget regression.
