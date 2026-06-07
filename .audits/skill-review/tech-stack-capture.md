---
review-type: skill-review
target: "skills/tech-stack-capture/SKILL.md"
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
repo-revision: "a2daeb7cdbcc24058fc3534774a5790a7dd1eabc"
created: "2026-06-06"
status: complete
---

# Skill Review: tech-stack-capture

## Scope

Target: `skills/tech-stack-capture/` (`SKILL.md` 168 lines, plus `references/signal-source-map.md` and three worked examples — `examples/01-fresh-capture-empty-additions.md`, `examples/02-refresh-after-dep-bot-swap.md`, `examples/03-deviation-with-override-and-regroup.md`). The skill is a single-operation, interactive, resumable write path that mutates the consuming repository's `project/portfolio.yml`. Reviewed: frontmatter, body structure, the `## Why this is a skill, not an agent` rationale, the eight-step operation runbook, gotchas, hard rules, resumability, examples, and the references payload. Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions in frontmatter).
Validator: override — the upstream `skills-ref` CLI is not provisioned in this repository; the repo-local `scripts/validate_skills.py` was run instead (`76 artifacts; 0C / 9W / 0S / 1I`; tech-stack-capture itself produces 0 findings). Per `skill-review` §Checks derived from external skill-structure validation, the local validator stands in for the external structure check; it does NOT enforce the 5,000-token authoring cap, so that check was performed separately with `tiktoken` (cl100k_base): 4,895 tokens.
Narrowing: none — full review.
Explicitly out of scope: the runtime correctness of the eight-step discovery sequence against a live repository (that is covered by the discovery spec's own AC); Vale / markdownlint style (handled by `task lint`); the content of the `tech-stack-drift-reviewer` agent named in `see_also` beyond confirming it exists; the signal-source-map ↔ spec-allowlist row-parity check (that is a `tech-stack-discovery` AC owned by `portfolio-audit`, not a skill-structure concern).

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 1
- Info: 4

Go/no-go: PASS — no MUST-class violation; the skill is structurally spec-conformant. The two Warnings are a token-budget headroom risk and the soft line-count overshoot; both are recorded with an explicit disposition below.
Next concrete action: none — all findings addressed (fixed or accepted-with-rationale); plan ready to close per `review-plan` §Lifecycle, retained on disk as the §AC7 evidence that the capture skill was reviewed against `skill-review`.

## Findings

### Warning

- [x] [skill-management.authoring-quality-token-cap] `SKILL.md` measures 4,895 tokens (cl100k_base) — under the 5,000-token hard cap but with only ~2% headroom. A single future paragraph would breach the MUST.
      Where: `skills/tech-stack-capture/SKILL.md` whole file; the `## Operations` eight-step block (~lines 64–137) is the bulk.
      Fix options: (a) extract the per-step runbook into `references/operations.md` with a load-trigger in `SKILL.md` (the pattern applied to `portfolio-audit` in this same review cycle), or (b) accept the current size and treat the headroom as a maintenance watch-item.
      Decision: **accepted as-is, not actioned this cycle.** The skill is currently under the cap, so there is no MUST violation to remediate; an extraction would be a structural change to a skill that already passes the validator and reads as one coherent runbook (the eight steps are a strict ordered sequence whose value is in being read together). Splitting it now trades a real readability cost for headroom that is not yet needed. Recorded here as a deliberate disposition per `review-plan` §Severity scale; the watch-item is: the next material edit to `## Operations` MUST re-measure tokens and extract to `references/operations.md` if the edit would cross 5,000.
      Verify: `python3 -c "import tiktoken;print(len(tiktoken.get_encoding('cl100k_base').encode(open('skills/tech-stack-capture/SKILL.md').read())))"` returns 4895 (< 5000) at this revision.

- [x] [skill-management.recommendations-soft-line-target] `SKILL.md` is 168 lines, over the ~150-line soft target.
      Where: `skills/tech-stack-capture/SKILL.md` (full file).
      Fix: the same `references/operations.md` extraction in the token-cap finding would pull this well under 150.
      Decision: **accepted as-is, not actioned this cycle**, for the same rationale as the token-cap Warning — the line count is a SHOULD-class soft target, not a MUST, and the eight-step sequence's readability as a single unit outweighs the ~18-line overshoot. Tied to the same watch-item: an extraction triggered by a future token-cap breach resolves this transitively.
      Verify: `wc -l skills/tech-stack-capture/SKILL.md` reports 168 at this revision.

### Suggestion

- [x] [skill-management.authoring-quality-consistent-terminology] The skill uses several phrasings for the active repository under audit — "the active repository", "the consuming repository", "any other repo", "the calling repo" appear across §Detection / §Preconditions / §Operations.
      Where: e.g. `:49` ("the active repository"), `:61` ("any other repo"), `:43` ("the consuming repository").
      Fix: pick one term ("the active repository") and apply it consistently; non-blocking polish.
      Decision: **accepted as-is, not actioned.** SHOULD-class polish; each variant is unambiguous at its use site (Detection vs. global-manifest-fetch vs. write-target contexts), and a term-sweep would churn a just-reviewed file for negligible discovery gain. Documented per `review-plan` §Severity scale rather than mass-edited — the same disposition taken for the sibling `portfolio-audit` review.
      Verify: re-read §Detection / §Preconditions; the variants each name the right scope in context.

### Info

- [x] [skill-management.frontmatter-validation] Frontmatter is conformant: `name` (`tech-stack-capture`) is verb-noun-shaped and equals the folder name; `description` is 935 chars (≤1024), third-person, and names what + when (trigger phrases incl. German) + the resume mention; `tags: [scaffolding]` is in the starter vocabulary; `phase: design`; `summary` + `summary_de` present; `use_when` / `dont_use_when` (with `situation`+`alternative` records) / `see_also` well-formed; `resumable: true` matches the §Resumability body and the persisted-checkpoint design.
      Where: `skills/tech-stack-capture/SKILL.md:1-21`.
      Fix: n/a (observation).
      Verify: `scripts/validate_skills.py` reports tech-stack-capture at 0 findings.

- [x] [skill-vs-agent.rationale-section-present] The mandatory `## Why this is a skill, not an agent` section is present and substantive: it cites the per-entry interactive-confirmation MUST, the persistent on-disk artefact, cross-spec orchestration, and an explicitly considered counter-dimension (a tool-restricted probing agent) that it rejects with a reason. This is the textbook skill-vs-agent justification shape.
      Where: `skills/tech-stack-capture/SKILL.md:34-39`.
      Fix: n/a (observation).
      Verify: n/a.

- [x] [skill-vs-agent.duplicate-prevention] The tech-stack surface is shared across three artefacts; the boundaries are explicitly drawn and non-overlapping. `tech-stack-capture` is the per-repo interactive WRITE path; `portfolio-audit` (named in `dont_use_when` and `see_also`) is the read-only portfolio-wide discovery + signal-verification audit; `tech-stack-drift-reviewer` (an agent, present at `agents/tech-stack-drift-reviewer.md`, named in `see_also`) is the read-only drift detector. `dont_use_when` correctly routes global-manifest authoring and signal-verification audits away to `portfolio-audit`. No duplicate-capability violation.
      Where: `skills/tech-stack-capture/SKILL.md:12-19` (`dont_use_when` / `see_also`) and `:45-54` (Detection roles).
      Fix: n/a (observation).
      Verify: `ls agents/tech-stack-drift-reviewer.md` and `ls skills/portfolio-audit/` both resolve.

- [x] [review-plan.findings-format] The skill's own internal severity vocabulary (`Critical` / `Warning` / `Suggestion` used in §Operations and §Gotchas to describe the audit findings the WRITTEN manifest will later trigger) matches the canonical `review-plan` §Severity scale labels in Title Case. This is the artefact describing downstream audit behaviour, not the review plan's own findings — recorded as an Info cross-reference so a reader does not mistake it for a classification of this review.
      Where: e.g. `skills/tech-stack-capture/SKILL.md:94`, `:128`, `:143`.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->

2026-06-06 — token-cap (Warning) — accepted as-is (4,895 < 5,000, no MUST violation; extraction deferred to a watch-item triggered by the next material §Operations edit; rationale recorded inline) — verified: tiktoken cl100k_base on SKILL.md = 4,895 — verified by: agent:skill-review
2026-06-06 — soft-line-target (Warning) — accepted as-is (168 lines, SHOULD-class soft target; resolved transitively if the token-cap watch-item ever fires an extraction; rationale recorded inline) — verified: wc -l = 168 — verified by: agent:skill-review
2026-06-06 — terminology-consistency (Suggestion) — accepted as-is (SHOULD-class deliberate-design acknowledgement; variants unambiguous in context) — verified: decision documented per review-plan §Severity scale — verified by: agent:skill-review
2026-06-06 — frontmatter / rationale-section / duplicate-prevention / findings-format (Info) — pass-observations, no action required — verified: re-read against skill-management + skill-vs-agent + review-plan; validate_skills.py reports tech-stack-capture at 0 findings — verified by: agent:skill-review
2026-06-06 — plan close — every finding `- [x]`; zero Critical at any point, so no open `- [ ]` Critical blocks closure; the two Warnings and one Suggestion are accepted-with-rationale (not deferred to issues, not silently downgraded). Status set to `complete`. Plan retained on disk (not deleted) as the standing `tech-stack-discovery` §AC7 evidence that `tech-stack-capture` has been reviewed against `skill-review` with the resulting plan closed; the closer intentionally does not run the `review(skill-review): close …` deletion commit, mirroring the disposition taken for `.audits/skill-review/portfolio-audit.md` — verified: `scripts/validate_skills.py` = 76 artifacts; 0C / 9W / 0S / 1I, all residual W/I on unrelated artefacts — verified by: agent:skill-review
