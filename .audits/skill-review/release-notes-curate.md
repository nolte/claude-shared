---
review-type: skill-review
target: "skills/release-notes-curate/SKILL.md"
target-kind: skill
specs-applied:
  - slug: skill-management
    revision: "38f4fc010a020aac3da9ae8465d49889d5146f39"
  - slug: skill-vs-agent
    revision: "0e3b6f9fc64bbfd97c74c2575d25fcfcae5598d6"
  - slug: review-plan
    revision: "0e3b6f9fc64bbfd97c74c2575d25fcfcae5598d6"
  - slug: skill-review
    revision: "38f4fc010a020aac3da9ae8465d49889d5146f39"
repo-revision: "7f68d7e09576a9a51a04e5f78d4e76e6f6123c54"
created: "2026-05-01"
status: in-progress
---

# Skill Review: release-notes-curate

## Scope

Target: `skills/release-notes-curate/` — `SKILL.md` (164 lines), referenced asset `references/project-bundles.md` (76 lines, six project-type bundles). Skill source landed on `develop` via PR #30 at commit `7f68d7e`. Parent spec is `spec/project/release-skill-layer/`, also landed in #30.

Specs applied: `skill-management`, `skill-vs-agent`, `review-plan`, `skill-review` (revisions recorded in frontmatter).
Validator: override — `skills-ref` (Anthropic's canonical external skill-structure validator) is not provisioned in this repository and no alternative validator is declared in repo tooling; per `skill-review` §"Checks derived from external skill-structure validation" MAY suppress, the spec-derived checks below stand in until a validator is provisioned. Re-run this review once a validator is wired up.
Narrowing: none.
Dispatched-agent companion review: not applicable — the skill dispatches another *skill* (`audience-identify`), not an agent; `skill-vs-agent` §Hybrid pattern explicitly allows skill-to-skill calls in the same thread, and `agent-review` is not triggered.
Explicitly out of scope: runtime behavior of the skill (no live execution per `skill-review` §Non-Goals), Vale / markdown style (handled by `task lint`), the parent spec `spec/project/release-skill-layer/` (its own readiness check is `spec-readiness-reviewer`, not this review type), the sibling skill `release-publish-trigger` (separate plan).

## Summary

- BLOCKER: 0
- WARNING: 1
- SUGGESTION: 0
- INFO: 2

Go/no-go: PASS — the skill conforms to every MUST in `skill-management`, `skill-vs-agent`, and `review-plan` that this review type checks. The single WARNING flags a real boundary gap with the `audience-doc-author` agent that should be closed via an explicit anti-trigger; it is not a spec violation by itself but a skill-vs-agent SHOULD-recommendation. The two INFOs are observations.
Next concrete action: add an explicit anti-trigger against `audience-doc-author` to the skill's `description` (one phrase) and, optionally, a one-paragraph cross-reference inside the SKILL body.

## Findings

### WARNING

- [x] [skill-vs-agent.duplicate-prevention] The agent `audience-doc-author` (path `agents/audience-doc-author.md`) lists "draft release notes per our audience analysis" as an explicit use-case, while this skill curates release-drafter draft bodies derived from the audience artefact. Capabilities are not equivalent (the agent drafts a doc artefact from scratch and returns text + coverage map; this skill operates on an *existing* GitHub release draft, wraps the augmentation in stable markers, and writes back via `gh release edit --notes`), so the `skill-vs-agent` §"Duplicate prevention" MUST-NOT bar (no two artefacts with equivalent capabilities) is not violated. However, the SHOULD bar ("when the boundary is genuinely blurry between an existing artifact and a proposed new one, propose a merge, a rename, or a clearer split as part of the authoring PR—never silently ship a third overlapping artifact") asks for the boundary to be made explicit, and the current `description` lists anti-triggers against `release-publish-trigger`, `audience-identify`, `github-issue-templates-apply`, and `pull-request-workflow` but **not** against `audience-doc-author`. A reporter saying "draft release notes for this repo" could plausibly route to either side without the explicit guard.
      Where: `skills/release-notes-curate/SKILL.md` line 3 (frontmatter `description` field), specifically the trailing "Don't use to ..." sentence.
      Fix: append one anti-trigger phrase to the `description`'s "Don't use ..." sentence — for example "to draft release notes from scratch outside of an existing release-drafter draft (that's `audience-doc-author`)". Optionally add a one-paragraph cross-reference in the SKILL body (e.g. inside the User-language policy block or as a new "Boundary with `audience-doc-author`" subsection) explaining that `audience-doc-author` drafts text artefacts and this skill operates on an existing release draft via `gh release edit --notes`.
      Verify: `grep -i 'audience-doc-author' skills/release-notes-curate/SKILL.md` returns at least one hit; conceptually, a re-read of the `description` makes the routing decision unambiguous.

### INFO

- [ ] [skill-review.external-validator] External skill-structure validator (`skills-ref`) is not provisioned in this repository, so the spec's MUST-run external-validator check was suppressed via the `## Scope` override clause; this is allowed by `skill-review` §"Checks derived from external skill-structure validation" MAY but worth flagging so the project tracks the gap. Same observation applies to every skill currently shipped from this plugin.
      Where: this plan's `## Scope` "Validator: override — …" line; `skill-review` MUST §"Checks derived from external skill-structure validation".
      Fix: n/a (observation) — when `skills-ref` (or an equivalent validator declared in repo tooling) becomes available, re-run `skill-review run release-notes-curate` so the structural checks run against the binary, not just the spec-derived approximation.
      Verify: n/a (observation).
- [ ] [skill-vs-agent.rationale.counter-dimension] The rationale section names exactly one counter-dimension (specialisation — a narrow Markdown-formatter agent could specialise on section composition); `skill-vs-agent` §"Rationale documentation" SHOULD asks for at least one counter-dimension, so the bar is met. Parallelism would be a second plausible counter-dimension if multi-repo batch curation ever becomes a use case (an agent could fan out across multiple repos in parallel), but the current single-repo contract makes that hypothetical, not load-bearing. Same shape as the matching INFO recorded in `release-publish-trigger` (parallel review) and `github-issue-templates-apply`.
      Where: `skills/release-notes-curate/SKILL.md` line 16 (counter-dimension bullet under "## Why this is a skill, not an agent").
      Fix: n/a (observation) — only reconsider if the skill grows a multi-repo batch mode, at which point the rationale should be revisited.
      Verify: n/a (observation).

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-05-01 — duplicate-prevention.audience-doc-author — appended anti-trigger phrase to the skill's `description` ("to draft release notes from scratch outside of an existing release-drafter draft (that's the `audience-doc-author` agent — this skill operates only on an *existing* draft via `gh release edit --notes`)") — verified: `grep -i 'audience-doc-author' skills/release-notes-curate/SKILL.md` returns the new anti-trigger line.
