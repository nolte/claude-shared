---
review-type: agent-review
target: "plugins/nolte-media/agents/graphic-prompt-generator.md"
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

# Agent Review: graphic-prompt-generator

## Scope

Target: `plugins/nolte-media/agents/graphic-prompt-generator.md` (frontmatter + full body; no
external supporting assets are referenced beyond `spec/` paths, all four of which resolve:
`spec/design/graphic-prompt-authoring/`, `spec/design/corporate-design-colors/`,
`spec/design/flux-image-generation/`, `spec/design/gemini-image-generation/`).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions
recorded in frontmatter).
Narrowing: none — full single-target run out of the issue #460 backlog (batch `misc`).
Classification call: the agent is **write-capable**, not read-only — its responsibility verb is
"authors and writes a prompt document", so the read-only tool bans don't apply to its `Write`
declaration.
Dispatching skill: none — the agent is invoked directly (`image-generate` and
`gemini-image-handoff` are peers, not dispatchers), so no companion `skill-review` is triggered.
Explicitly out of scope: runtime behavior of the agent (whether a generated prompt actually
renders as intended), Vale/markdown style (handled by `task lint`), and the content of the
`spec/design/` corpus itself.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 1
- Info: 1

Go/no-go: PASS — no `Critical`; the single `Warning` is a one-line delimitation gap, not a
structural defect.
Next concrete action: name the `gemini-image-handoff` overlap as a negative trigger in
`description`.

## Findings

### Warning

- [ ] [skill-vs-agent.duplicate-prevention] Plausible capability overlap with the peer skill
      `gemini-image-handoff`, whose "automated half authors a Gemini-optimised prompt from a
      brief" is the same brief-to-prompt transform this agent performs; the peer already names
      this agent as its negative trigger, but the delimitation isn't reciprocal, so
      `agent-review` §"Description quality and proactive-delegation intent" (absent negative
      trigger on a plausible overlap) fires on the same gap.
      Where: `plugins/nolte-media/agents/graphic-prompt-generator.md:3` (`description`) and
      `:14-18` (`dont_use_when`), against
      `plugins/nolte-media/skills/gemini-image-handoff/SKILL.md` `description` + `:17-18`.
      Fix: add `gemini-image-handoff` as a negative trigger in `description` (one cross-reference,
      keeping the delimitation chain tight per `agent-management` §Description contract) and mirror
      it as a `dont_use_when` entry; the split is durable brand-document authoring versus a
      one-off paste-into-the-UI prompt, so the correct remedy is delimitation, not a merge.
      Verify: `description` names `gemini-image-handoff`, `dont_use_when` carries the matching
      situation/alternative pair, and `python3 scripts/validate_skills.py` stays green.

### Suggestion

- [ ] [agent-management.portability] The consumer-install fallback in the body's opening covers
      only the absence of `spec/design/graphic-prompt-authoring/` and
      `spec/design/corporate-design-colors/`; Phase 1's instruction to consult
      `spec/design/flux-image-generation/` or `spec/design/gemini-image-generation/` dangles when
      the plugin ships no `spec/` tree, leaving the model-level baseline undefined in exactly the
      downstream case the fallback exists for.
      Where: `plugins/nolte-media/agents/graphic-prompt-generator.md:28` (fallback clause) versus
      `:78` (Phase 1 model-baseline instruction).
      Fix: state in Phase 1 that when the model-baseline spec isn't available, the generator's own
      published prompting guidance applies and the choice is recorded in the prompt document.
      Verify: Phase 1 names an explicit behaviour for the spec-absent case; re-read `:78`.

### Info

- [ ] [agent-review.tool-scope] `Grep` is declared and its role is stated generically under
      §"Writes vs researches" (loading brand sources), but no procedure phase names it, so the
      declared-vs-used check resolves only via that general statement rather than a procedural
      use site. Not a dead-permission `Warning` — the body does assign it a working-method role.
      Where: `plugins/nolte-media/agents/graphic-prompt-generator.md:5` (`tools`) and `:55`.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
