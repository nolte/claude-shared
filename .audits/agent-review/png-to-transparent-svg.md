---
review-type: agent-review
target: "plugins/nolte-media/agents/png-to-transparent-svg.md"
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

# Agent Review: png-to-transparent-svg

## Scope

Target: `plugins/nolte-media/agents/png-to-transparent-svg.md` (frontmatter + full body,
including the four inline Python snippets and the two tuning tables). Referenced assets checked:
`spec/design/png-to-transparent-svg/` and `spec/claude/skill-vs-agent/en.md` resolve; the
`${CLAUDE_PLUGIN_ROOT}` helper path named in §"Bash justification" does not (see the first
Warning).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions
recorded in frontmatter).
Narrowing: none — full single-target run out of the issue #460 backlog (batch `misc`).
Classification call: the agent is **write-capable**, not read-only — its responsibility verb is
"converts and writes cleaned PNGs plus SVGs", so the read-only tool bans don't apply and the
neutral `## Bash justification` heading (rather than `## Read-only Bash justification`) is the
correct form per `agent-management` §Tool access.
Dispatching skill: none — invoked directly; `graphic-prompt-generator` and `image-generate` are
peers that route *to* it, so no companion `skill-review` is triggered.
Explicitly out of scope: runtime behavior (whether the thresholds actually produce clean SVGs on
a given PNG), the correctness of the vtracer parameter defaults, and Vale/markdown style.

## Summary

- Critical: 0
- Warning: 2
- Suggestion: 1
- Info: 1

Go/no-go: PASS — no `Critical`. One Warning is a one-line accuracy fix; the other (body length)
needs a structural extraction and is deferred.
Next concrete action: correct the §"Bash justification" claim so it names the shell surface the
agent actually uses.

## Findings

### Warning

- [ ] [agent-management.tool-access-bash-justification] The `## Bash justification` section
      claims every conversion runs through "plugin-bundled Python helpers
      (`python3 "${CLAUDE_PLUGIN_ROOT}/..."`)", but `plugins/nolte-media/` bundles no such helper
      — the only script in the plugin is `skills/image-generate/scripts/image_generate.py`, which
      is unrelated. The agent in fact executes the inline Python of Phases 1-4 plus the `vtracer`
      binary, so the section names commands the agent doesn't invoke and misses the ones it does,
      which is exactly what the section exists to prevent. It also makes the reference an asset
      that doesn't resolve.
      Where: `plugins/nolte-media/agents/png-to-transparent-svg.md:32`, against
      `plugins/nolte-media/` (no `agent-assets/` or `scripts/` tree for this agent).
      Fix: restate the section in terms of the actual surface — inline `python3` running the
      Pillow/vtracer snippets in the body, plus the `python3 --version` / import probes of
      §Preconditions — keeping the existing no-git-mutation, no-install, no-network bounds.
      Verify: the section names no path that doesn't exist; `grep -r CLAUDE_PLUGIN_ROOT
      plugins/nolte-media/agents/` returns nothing.

- [ ] [agent-management.body-length] The body runs ~250 lines (file is 265 lines), over the
      ~200-line soft target `agent-management` §Recommendations sets and `agent-review`
      §Prompt-structure checks flags as a `Warning`. The bulk is the four inline Python snippets
      (~70 lines across Phases 1-4); the remaining prose is operational contract (output shape,
      thresholds, error table) that can't be cut without losing rules.
      Where: `plugins/nolte-media/agents/png-to-transparent-svg.md:16-265`.
      Fix: extract the four snippets into a bundled helper outside the recursively-scanned
      `agents/` tree, per `agent-management` §Structure — which would simultaneously make the
      `${CLAUDE_PLUGIN_ROOT}` claim of the first Warning true. That's a structural change with a
      testable Python module behind it, not a prose trim, so it exceeds this review cycle.
      Verify: `wc -l` on the agent file is ≤ ~215 and the helper resolves from
      `${CLAUDE_PLUGIN_ROOT}`.
      → deferred: https://github.com/nolte/claude-shared/issues/460 (batch `misc` closing
      comment, listed as a structure candidate)

### Suggestion

- [ ] [skill-agent-catalog.use-case-metadata] The frontmatter declares `use_when` but neither
      `dont_use_when` nor `see_also`, although the `description` already carries two negative
      triggers and two peers (`graphic-prompt-generator`, `image-generate`) point at this agent.
      The cross-links are therefore one-directional in the catalog.
      Where: `plugins/nolte-media/agents/png-to-transparent-svg.md:11-13`.
      Fix: mirror the two `description` negatives as `dont_use_when` entries and add a `see_also`
      naming the two media peers.
      Verify: `python3 scripts/validate_skills.py` stays green and the catalog renders the
      reciprocal links.

### Info

- [ ] [agent-review.subagent-boundary] The subagent-boundary and no-Skill-dispatch checks pass
      deliberately rather than vacuously: the body mentions both surfaces twice, at `:51` and
      `:261`, in each case as an explicit prohibition ("Never call the `Skill` tool or dispatch
      sibling agents"). A future mechanical grep on a looser pattern than `Skill(` / `Skill tool`
      would false-positive here.
      Where: `plugins/nolte-media/agents/png-to-transparent-svg.md:51` and `:261`.
      Fix: n/a (observation).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
