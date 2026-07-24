---
review-type: agent-review
target: "plugins/nolte-claude-dev/agents/claude-plugin-developer.md"
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

# Agent Review: claude-plugin-developer

## Scope

Target: `plugins/nolte-claude-dev/agents/claude-plugin-developer.md` (frontmatter + full body).
Referenced assets checked: every `spec/claude/...` path named in §Preconditions and §Working
procedure resolves.
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions
recorded in frontmatter).
Narrowing: none — full single-target run out of the issue #460 backlog (batch `misc`).
Classification call: the agent is **write-capable** (drafting executor holding `Write`/`Edit`), so
the read-only tool bans don't apply; the neutral `## Bash justification` heading is the correct
form and is present, correctly declaring that `task lint` isn't side-effect-free.
Reserved-token exception: `name` carries the banned token `claude`; the
`## Reserved-token rationale` section is present and the narrow exception in
`agent-management` §Structure applies, so this is not a finding
(`scripts/validate_skills.py` records it as `Info`).
Dispatching skill: `skill-management` chains into this agent (`use_when` names the chain). It was
reviewed under the separate `skill-review` workstream and is out of scope here; no companion
`skill-review` is triggered by this run.
Explicitly out of scope: runtime behavior (whether a dispatched run actually produces conforming
artifacts), the content of the `spec/claude/` corpus itself, and Vale/markdown style.

## Summary

- Critical: 1
- Warning: 1
- Suggestion: 1
- Info: 2

Go/no-go: CONDITIONAL — blocked until the duplicate-scan scope covers the plugin root the agent
is actually drafting into.
Next concrete action: widen the duplicate-check and sibling-scan globs to the target plugin root.

## Findings

### Critical

- [ ] [skill-vs-agent.duplicate-prevention] The mandatory pre-authoring duplicate check is scoped
      to the root plugin only: step 3 greps `skills/*/SKILL.md` and `agents/*.md`, and
      §Preconditions 3 globs "the existing siblings under `skills/` and `agents/`". But the agent
      explicitly drafts into a caller-named plugin root (`<plugin-root>/skills/<name>/`,
      `<plugin-root>/agents/<name>.md`) across all four plugins of this monorepo. Drafting into
      `plugins/nolte-engineering/` therefore de-duplicates against `nolte-shared`'s artifacts and
      never reads the target plugin's own ~30 `description` lines, so the MUST in `skill-vs-agent`
      §Duplicate prevention ("before authoring a new artifact, check the existing skills and
      agents for an equivalent capability") isn't discharged for three of the four roots the agent
      serves. `agent-review` §Checks derived from `skill-vs-agent` and the `agent-review` skill's
      own step 5.11 both scan all plugin roots, mirroring `scripts/validate_skills.py`.
      Where: `plugins/nolte-claude-dev/agents/claude-plugin-developer.md:100` (§Working procedure
      step 3) and `:92` (§Preconditions 3).
      Fix: scan the target plugin root plus the monorepo-wide set — `skills/*/SKILL.md`,
      `agents/*.md`, `plugins/*/skills/*/SKILL.md`, `plugins/*/agents/*.md` — with the in-plugin
      equivalence verdict taken against the root the artifact lands in.
      Verify: both sites name the `plugins/*/` globs; a drafting run targeting a subdirectory
      plugin reads that plugin's own `description` lines.

### Warning

- [ ] [agent-management.frontmatter-phase] The drafting checklist in §Working procedure step 4
      enumerates the frontmatter an artifact must carry (name form, `description`, `distribution`,
      `tools`) but never names `phase`, which `agent-management` §Structure and
      `skill-agent-catalog` §Phase classification both declare a MUST and whose absence hard-fails
      the docs build. The gap is navigable — step 5's self-audit against every acceptance criterion
      would catch it — but the checklist is what an executor follows in practice.
      Where: `plugins/nolte-claude-dev/agents/claude-plugin-developer.md:101-106` (step 4 bullets).
      Fix: add `phase` (one value from the eight-identifier vocabulary) to the step-4 frontmatter
      bullet, alongside the existing `distribution` requirement.
      Verify: step 4 names `phase`; a drafted artifact passes `python3 scripts/validate_skills.py`
      without a missing-phase error.

### Suggestion

- [ ] [skill-agent-naming.single-source] Step 4 restates the naming convention inline — the
      per-type forms, the `-er`/`-or`/`-ist` morphology, and both closed exception lists — while
      `spec/claude/skill-agent-naming/` is the single point of truth for exactly those rules and
      isn't in the §Preconditions "read at minimum" list. The restatement is a drift surface: an
      exception added to the owning spec leaves this body silently stale.
      Where: `plugins/nolte-claude-dev/agents/claude-plugin-developer.md:102` (step 4, first
      bullet) and `:86-91` (§Preconditions 2 spec list).
      Fix: add `spec/claude/skill-agent-naming/en.md` to the mandatory read list and reduce the
      inline text to the shape rule plus a pointer, dropping the duplicated closed lists.
      Verify: the closed exception lists appear only in the owning spec; §Preconditions 2 names it.

### Info

- [ ] [agent-management.model-selection] No `model` is declared, so the agent inherits the
      caller's model per `agent-management` §Model selection. That's conformant and deliberate for
      a drafting executor whose quality bar should track the caller's, but it means the cost
      contract is the caller's, not the agent's.
      Where: `plugins/nolte-claude-dev/agents/claude-plugin-developer.md:1-23` (frontmatter).
      Fix: n/a (observation).
      Verify: n/a.

- [ ] [agent-review.no-rule-covers] §Output contract item 3 asks the report to list "absolute
      paths", which sits oddly beside the agent's own hard rule that no absolute path leaks into an
      artifact, and leaks the operator's home directory into a report that often gets pasted into a
      PR. No `agent-management` or `skill-vs-agent` rule governs the path form of an agent's
      *report* (only of its internal references), so per the `agent-review` no-finding-without-a-
      citation rule this stays `Info` — the spec may want to grow a report-path convention.
      Where: `plugins/nolte-claude-dev/agents/claude-plugin-developer.md:74`.
      Fix: n/a (observation; a repo-relative report convention would be the natural remedy).
      Verify: n/a.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
