---
review-type: skill-review
target: "skills/portfolio-audit/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "11350ca81f476bad4d8dd53eda239628e18dec73"
  - slug: skill-vs-agent
    revision: "f84b38cea237fa4af4e4926559cdb1922fbdc61c"
  - slug: review-plan
    revision: "fb5ddba2328b68fbf6837dc4951a96d5b3fdb95b"
  - slug: skill-review
    revision: "f84b38cea237fa4af4e4926559cdb1922fbdc61c"
repo-revision: "28957d4dbc98a42b923c8897edd523645abf1698"
created: "2026-06-06"
status: complete
---

# Skill Review: portfolio-audit

## Scope

Target: `skills/portfolio-audit/` (`SKILL.md` 177 lines, plus `examples/01-audit-detects-duplicate.md`, `examples/02-render-inventory-idempotent.md`, `examples/03-bootstrap-new-member.md`; dispatched agent `agents/portfolio-manifest-collector.md` confirmed present, orchestration direction skill→agent only).
Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — the upstream `skills-ref` CLI is not provisioned in this repository; the repo-local `scripts/validate_skills.py` was run instead (`76 artifacts; 0C / 13W / 0S / 1I`, portfolio-audit itself produces 0 findings). Per `skill-review` §Checks derived from external skill-structure validation, the local validator stands in for the external structure check; note that it does NOT enforce the 5,000-token authoring cap, so that check was performed manually with `tiktoken` (cl100k_base).
Narrowing: none — full review (frontmatter, body, rationale, operations vocabulary, resumability, gotchas, examples, hard rules, tech-stack integration added this session).
Explicitly out of scope: runtime behavior of the skill, Vale/markdown style (handled by `task lint`), the content of `portfolio-manifest-collector` beyond confirming the orchestration direction.

## Summary

- Critical: 1
- Warning: 1
- Suggestion: 2
- Info: 3

Go/no-go: PASS — the 5,000-token cap Critical was remediated by extracting the operation runbooks to `references/operations.md`; `SKILL.md` is now 3,084 tokens / 106 lines.
Next concrete action: none — all findings addressed; plan ready for deletion-on-close per `review-plan` §Lifecycle.

## Findings

### Critical

- [x] [skill-management.authoring-quality-token-cap] `SKILL.md` exceeds the 5,000-token hard cap — measured 5,981 tokens (cl100k_base) for 27,459 chars / 177 lines.
      Where: `skills/portfolio-audit/SKILL.md` whole file; the `## Operations` block alone is ~3,283 tokens.
      Fix: move the detailed per-operation step runbooks and the redundant `## Reference: spec anchors` restatement into `references/operations.md` (consolidated single file with TOC), leaving a tight per-operation summary plus an explicit load-trigger phrase in `SKILL.md`.
      Verify: `python3 -c "import tiktoken;print(len(tiktoken.get_encoding('cl100k_base').encode(open('skills/portfolio-audit/SKILL.md').read())))"` returns < 5000.

### Warning

- [x] [skill-management.recommendations-soft-line-target] `SKILL.md` is 177 lines, over the ~150-line soft target; the Critical extraction above will pull it down well under it, so this Warning is satisfied by the same fix rather than separately.
      Where: `skills/portfolio-audit/SKILL.md` (full file, 177 lines).
      Fix: addressed transitively by the Critical extraction; no independent action.
      Verify: `wc -l skills/portfolio-audit/SKILL.md` reports well under 150 after extraction.

### Suggestion

- [x] [review-plan.findings-format] Operation 4 step 5 promises a "`Caller follow-ups` shape" for the Discover-tech-stack persistence artefact, but the Audit operation's report shape (step 4) uses the `review-plan` four/five-section names (`## Scope` … `## Processing log`); the two persistence outputs describe their section vocabulary with different language.
      Where: `skills/portfolio-audit/SKILL.md:126` ("same `Caller follow-ups` shape") vs `:76-80` (review-plan section names).
      Fix: align the Discover-tech-stack persistence sentence to name the `review-plan` section vocabulary it actually emits, or drop the undefined `Caller follow-ups` term.
      Verify: re-read step 5; the persisted-artefact section vocabulary is described in one consistent set of terms.

- [x] [skill-management.authoring-quality-consistent-terminology] The skill mixes "the consuming repository", "the active checkout", "the calling repo", and "Portfolio-Member repository" for the same concept across operations.
      Where: e.g. `:113` ("the consuming repository"), `:160` ("the calling repo"), `:50`/`:101` ("Portfolio-Member repository").
      Fix: pick one term per concept (target/active checkout vs. Portfolio-Member) and apply it consistently; non-blocking polish.
      Verify: grep for the variants and confirm a single term per concept.
      Decision: **accepted as-is, not actioned.** This is a SHOULD-class polish item; the variant terms are individually unambiguous in context (each names the right scope at its use site), and a portfolio-wide term-sweep would touch both `SKILL.md` and `references/operations.md` for negligible discovery gain while risking churn against the just-landed tech-stack integration. Documented here per `review-plan` §Severity scale (a deliberate-design acknowledgement) rather than mass-edited.

### Info

- [x] [skill-vs-agent.rationale-section-heading] Rationale heading conformance is satisfied: both the mandatory `## Why this is a skill, not an agent` and the permitted additional `## Why this is one skill, not three` are present (additional H2 explicitly allowed by `skill-vs-agent` §Rationale section heading).
      Where: `skills/portfolio-audit/SKILL.md:28` and `:34`.
      Fix: n/a (observation).
      Verify: n/a.

- [x] [skill-management.frontmatter-validation] Frontmatter is conformant: `name` verb-noun and equals the folder name; `description` 1,011 chars (≤1024), third-person, names both what + when + the resume mention; `phase: quality`, `tags: [audit]` (in starter vocabulary), `use_when`/`dont_use_when`/`see_also` well-formed; `resumable: true` matches the multi-gate body.
      Where: `skills/portfolio-audit/SKILL.md:1-22`.
      Fix: n/a (observation).
      Verify: n/a.

- [x] [skill-vs-agent.duplicate-prevention] The tech-stack-discovery surface overlaps with the sibling `tech-stack-capture` skill, but the boundary is explicitly declared (this skill is read-only discovery + portfolio-wide audit; `tech-stack-capture` is the per-repo write path), and `dont_use_when` routes capture/refresh to `tech-stack-capture`. No duplicate-capability violation.
      Where: `skills/portfolio-audit/SKILL.md:12-14` (`dont_use_when`) and `:115-128` (Discover tech stack operation).
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->

2026-06-06 — token-cap (Critical) — extracted the four operation runbooks + spec-anchors into `references/operations.md` (with TOC + a "Read references/operations.md when you execute any operation" load-trigger in SKILL.md); replaced the verbose `## Operations` block with routing summaries — verified: `tiktoken` cl100k_base on SKILL.md = 3,084 tokens (< 5,000).
2026-06-06 — soft-line-target (Warning) — satisfied transitively by the token-cap extraction — verified: `wc -l skills/portfolio-audit/SKILL.md` = 106 (< 150).
2026-06-06 — caller-follow-ups-wording (Suggestion) — rewrote Discover-tech-stack persistence step to name the `review-plan` section vocabulary and severity grammar; dropped the undefined `Caller follow-ups` term — verified: `grep -rn "Caller follow-ups" skills/portfolio-audit/` returns no matches.
2026-06-06 — terminology-consistency (Suggestion) — accepted as-is (SHOULD-class deliberate-design acknowledgement, rationale recorded inline on the finding) — verified: decision documented per `review-plan` §Severity scale.
2026-06-06 — rationale-heading / frontmatter / duplicate-prevention (Info) — pass-observations, no action required — verified: re-read against `skill-vs-agent` and `skill-management`.
2026-06-06 — plan close — every finding `- [x]`; the single Critical landed (not deferred, not downgraded); no open `- [ ]` Critical remains. Status set to `complete`. Plan retained on disk (not deleted) as the standing AC-5 evidence that `portfolio-audit` has been reviewed against `skill-review` with the resulting plan closed; the closer intentionally does not run the `review(skill-review): close …` deletion commit in this pass — verified: `scripts/validate_skills.py` reports portfolio-audit at 0 findings (76 artifacts; 0C / 13W / 0S / 1I, all residual W/I on unrelated artefacts).
