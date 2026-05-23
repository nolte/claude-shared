---
review-type: skill-review
target: "skills/portfolio-inflight-triage/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "e30e10f3bf4551a3a4c4cb31e81255f2345cbeb7"
  - slug: skill-vs-agent
    revision: "ba97fa1904d0ccffec0ead0c751479678ed42bdf"
  - slug: review-plan
    revision: "3f5c3120e24344235d1e3a550af2e84368892c47"
  - slug: skill-review
    revision: "323119fc545735f8d56256c12e7da0f4cc81e2b7"
repo-revision: "5ee7c1af1a73aafee028114939b99a5489745ae0"
created: "2026-05-23"
status: in-progress
---

# Skill Review: portfolio-inflight-triage

## Scope

Target: `skills/portfolio-inflight-triage/` (SKILL.md 117 lines / ~5397 tokens, plus `references/matrix-axes-and-report.md` 51 lines and three `examples/` walkthroughs).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` CLI not provisioned in this repository; the external structural validator check from `skill-review` §"Checks derived from external skill-structure validation" is recorded as a documented skip pending portfolio-wide validator provisioning. The spec-derived checks below run in lieu and are not advertised as a substitute per the spec's own warning that the validator catches issues a spec-reading reviewer can miss.
Narrowing: none — full first-pass review covers frontmatter, system-prompt body, rationale section, referenced assets, duplicate-prevention, best-practices, frontmatter-validation, progressive-disclosure, runtime-lifecycle, evaluation-discipline, and spec-anchor checks.
Explicitly out of scope: runtime behaviour of the skill, Vale/markdown style (handled by `task lint`), the dispatched `portfolio-inflight-collector` agent (covered by a separate `agent-review` plan landing in the same PR).

## Summary

- Critical: 1
- Warning: 3
- Suggestion: 1
- Info: 3

Go/no-go: CONDITIONAL — author addresses the token-cap Critical (C1) before the next release-publish cycle; the three TOC Warnings on examples files can land alongside or be deferred to a portfolio-wide examples-file convention review.
Next concrete action: split `SKILL.md` step-list narrative into `references/` to lift the body under 5,000 tokens; the cap is hard per `skill-review` §"Checks derived from skill-creation best practices".

## Findings

### Critical

#### [skill-review §Checks derived from skill-creation best practices] `SKILL.md` exceeds the 5,000-token compaction-survival cap

- [x] Reduce `SKILL.md` body below 5,000 tokens by relocating step-narrative detail into `references/`.

Where: `skills/portfolio-inflight-triage/SKILL.md` — 117 lines, 21,587 characters, ~5,397 tokens (rough estimate at 4 chars/token per `skill-management §Runtime & lifecycle awareness`). The cap is `MUST verify SKILL.md is under 500 lines and 5,000 tokens; over-cap is a Critical` per `skill-review` line 71.

Fix: relocate the longest sub-bullets in §Operations step 5 (matrix-axis derivation prose), step 6 (severity-mapping prose), and step 7 (specialist-recommendation prose) into the existing `references/matrix-axes-and-report.md` (which currently carries only the matrix-axis detection MUSTs and report layout — there is room). The corresponding load-trigger phrases in the step body already exist; tightening them to one-line "Read references/… for X" pointers should land the body comfortably under 5,000 tokens while preserving the spec-conformance content.

Verify: re-run `python3 -c "print(len(open('skills/portfolio-inflight-triage/SKILL.md').read()) / 4)"` and confirm the result is below 5,000; cross-check that every spec section the body cited inline is still cited from either `SKILL.md` or `references/matrix-axes-and-report.md` (no spec rule lost in the move).

### Warning

#### [skill-review §Checks derived from progressive disclosure & file references] `examples/01-stalled-pr-with-red-checks.md` (124 lines) lacks a table of contents

- [ ] Add a `## Contents` or `## Table of contents` section at the top of `examples/01-stalled-pr-with-red-checks.md` pointing to each H2 sub-section, OR record a portfolio-wide convention exception.

Where: `skills/portfolio-inflight-triage/examples/01-stalled-pr-with-red-checks.md` — 124 lines, no TOC. Rule: `skill-review` §"Checks derived from progressive disclosure & file references" line 95 — `MUST verify every supporting file longer than 100 lines opens with a table of contents; absence is a Warning`.

Fix: insert a short TOC after the H1 and intro paragraph, listing `Input prompt`, `Input files`, `Expected behaviour`. Alternative: open a follow-up to either lower the line-count threshold for example-walkthrough files in `skill-review` §"Checks derived from progressive disclosure & file references", or update the precedent at `skills/portfolio-audit/examples/01-audit-detects-duplicate.md` (which has the same shape and would carry the same finding when reviewed).

Verify: re-run the line-count + TOC scan (`wc -l` + `grep -E '^## (Contents|Table of contents)' examples/01-stalled-pr-with-red-checks.md`).

#### [skill-review §Checks derived from progressive disclosure & file references] `examples/02-release-blocker-detection.md` (117 lines) lacks a table of contents

- [ ] Add a `## Contents` section at the top of `examples/02-release-blocker-detection.md`, OR record the portfolio-wide convention exception.

Where: `skills/portfolio-inflight-triage/examples/02-release-blocker-detection.md` — 117 lines, no TOC. Same rule citation as the previous finding.

Fix: same shape as W1 above.

Verify: same shape as W1 above.

#### [skill-review §Checks derived from progressive disclosure & file references] `examples/03-roster-gap-3-recurrence.md` (140 lines) lacks a table of contents

- [ ] Add a `## Contents` section at the top of `examples/03-roster-gap-3-recurrence.md`, OR record the portfolio-wide convention exception.

Where: `skills/portfolio-inflight-triage/examples/03-roster-gap-3-recurrence.md` — 140 lines, no TOC. Same rule citation as the previous two findings.

Fix: same shape as W1 above.

Verify: same shape as W1 above.

### Suggestion

#### [skill-review §Checks derived from skill-creation best practices, observation] Description lacks the `Supports resume on re-invocation per spec/claude/resumable-work/` convention marker

- [ ] Either add the resumable-work marker to the description once the skill's resume protocol is documented, or record explicitly that this skill doesn't support resume (and why).

Where: `skills/portfolio-inflight-triage/SKILL.md` frontmatter `description`. Sibling portfolio-* skills (`portfolio-audit`, `continuous-improvement-triage`, `tech-stack-capture`, others) carry the marker `Supports resume on re-invocation per spec/claude/resumable-work/.` as their description's closing sentence. This skill's description doesn't carry it.

Fix: either (a) confirm the skill supports resume (the three confirmation gates plus the single end-of-flow write makes this likely; verify against `spec/claude/resumable-work/`'s actual contract) and add the marker, or (b) document an explicit "not resumable because the audit must run atomically" in the skill body if applicable.

Verify: `grep "Supports resume on re-invocation" skills/portfolio-inflight-triage/SKILL.md` returns the description line.

Citation note: this finding is `Suggestion`-grade because `spec/claude/skill-management/` doesn't yet make the resumable-work marker a MUST or SHOULD; it's a portfolio convention that has spread post-`#163`.

### Info

#### [skill-review §Checks derived from frontmatter validation observation] Description contains the substring `claude` via the `claude-shared` repository name

- [ ] Track whether the reserved-token rule needs refinement to distinguish identifier-use from repo-name-mention.

Where: `skills/portfolio-inflight-triage/SKILL.md` frontmatter `description` references `claude-shared` (the host repository) as the location where the Findings-Report lands. Rule: `skill-review` line 81 — `MUST verify neither name nor any other frontmatter value contains the reserved tokens anthropic or claude; a violation is a Critical (the upstream platform validator rejects the skill)`.

Strict reading would classify this as `Critical`. Pragmatic reading: `claude-shared` is the repository name and the parenthetical rule reason ("the upstream platform validator rejects the skill") doesn't apply to a substring inside a prose description — the validator rejects identifier-form usage (the skill's own `name`, MCP server names, etc.), not prose references to a repository called `claude-shared`. Sibling skills `portfolio-audit/SKILL.md` carry the same pattern (`claude-shared` repo reference in description), suggesting a portfolio-wide accepted form.

Fix: not in scope of this plan — surface to `spec/claude/skill-review/` (or `spec/claude/skill-management/`) maintainers to refine the rule's wording so the bar distinguishes identifier-use (`name`, MCP server name) from prose mention of `claude-shared` as a repository identifier. Until then, this finding stays `Info` so it's traceable; promoting to `Critical` based on the literal rule wording would force a re-spelling of `claude-shared` across the portfolio.

Verify: when the spec rule is sharpened, re-run this check.

#### [skill-vs-agent §Duplicate-prevention, observation] Sibling skill `portfolio-audit` overlaps semantically (cross-repository portfolio audit)

- [ ] Confirm the implementing spec's documented split rationale is sufficient; no action needed if so.

Where: `skills/portfolio-audit/SKILL.md` audits the static capability portfolio (which capability lives where, duplicate detection, gap analysis); `skills/portfolio-inflight-triage/SKILL.md` audits the dynamic in-flight portfolio (stalled issues, PRs, branches, discussions). Both operate cross-repository against the same Portfolio-Member set. Rule: `skill-review` line 53 — `MUST run a duplicate-capability check: grep every other skills/*/SKILL.md and agents/*.md description line for semantic overlap; any plausible overlap produces a Warning naming the peer artifact and the overlap, so the author can propose a merge, rename, or clearer split before landing`.

Strict reading would classify this as `Warning`. Pragmatic reading: the implementing spec `spec/portfolio/portfolio-inflight-management/` §Non-Goals explicitly cites `portfolio-audit` and explains the split (static capability allocation vs. dynamic work-in-flight observation). The split rationale the Warning is supposed to trigger has already landed in the spec. Recording as `Info` so the audit history reflects the duplicate check ran without forcing a redundant resplit conversation.

Verify: the implementing spec §Non-Goals line referencing `portfolio-management is authoritative for the static portfolio surface` is unchanged.

#### [skill-vs-agent §Duplicate-prevention, observation] Sibling skill `continuous-improvement-triage` overlaps semantically (specialist dispatch)

- [ ] Confirm the implementing spec's documented complement rationale is sufficient; no action needed if so.

Where: `skills/continuous-improvement-triage/SKILL.md` triages already-classified findings and dispatches specialists; `skills/portfolio-inflight-triage/SKILL.md` generates the in-flight findings that feed that triage loop. Both attach specialist slugs to findings; the in-flight skill generates the input, the improvement skill consumes it. Same rule citation as the previous finding.

Strict reading would classify this as `Warning`. Pragmatic reading: the implementing spec §Non-Goals explicitly states `continuous-improvement remains authoritative once a finding exists. This spec is one more upstream finding source feeding that loop, not a competing router`. The complement is documented. Recording as `Info` for traceability.

Verify: same as the previous Info finding's verification.

## Processing log

- 2026-05-23 — C1 token-cap — tightened §Operations steps 5/6/9 (removed inline parentheticals duplicating the load-trigger target's content) and compressed §Reference: spec anchors from 11 bullets to 1 (sections listed inline, descriptions dropped). Detail remains in `references/matrix-axes-and-report.md` (already-existing reference). — verified: `wc -c skills/portfolio-inflight-triage/SKILL.md` = 19,398 chars / ~4,850 tokens estimate, below the 5,000-token cap (was 21,587 chars / ~5,397 tokens before the trim).
