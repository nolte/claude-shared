# Review Plan Artifact

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

Reviews of Claude Code artifacts—a skill against `skill-management`, an agent against `agent-management`, future review types—need to produce a result that another actor (the author, a reviewer, a follow-up agent, a calling skill) can process step by step. If every reviewer invents a private result shape, consuming actors have to reverse-engineer the format per review, plugin developers can't script against the output, and findings get lost between runs. This spec defines a single, reusable on-disk artifact—the *review plan*: that any review procedure in the `nolte-shared` plugin emits. The plan is actionable, self-contained, lives in the repository under `.audits/`, is worked off item by item, and is removed once every item has been addressed. Its git history is the lasting audit trail; the file itself is transient.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every review in the plugin produces the same structural output shape so plugin developers, authors, and follow-up automation can parse and process it without format negotiation
- Every finding is an **actionable checkbox item**: reading one item tells the worker what's wrong, where, how to fix it, and how to verify the fix
- A plan is **self-contained**: it carries enough context (target, specs applied, bounded scope, revision) that a new actor can pick it up without re-running the review
- The plan's **lifecycle is explicit**: create fresh per review, commit, work off, remove once fully processed—no accumulation of stale plans, no partially consumed plans lingering silently
- The audit trail survives plan deletion: every create / update / remove is a commit, so `git log --follow` on a removed plan reconstructs what was reviewed and how it was closed

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Defining the review **criteria** for any specific artifact type: `skill-review`, `agent-review`, and any future review spec own that
- Prescribing **who** or **what** processes the plan (human, Claude in the main conversation, a dedicated agent, CI automation)—the plan is a format, not a pipeline
- Versioning plans across time—one plan per (target, review-type) at a time; a rerun **replaces** the plan rather than revising it
- Long-lived audit registers—this spec's plans are disposable; use `spec-drift-audit` artifacts when a permanent per-quarter audit record is needed
- Continuous-integration reporting formats (SARIF, JUnit, …)—the plan is a human- and LLM-friendly markdown file, not a CI result interchange format
- A `.audits/` index/registry file—open plans are enumerated by scanning the directory (for example `grep -l "status: open" .audits/**/*.md`); an index would be a drift-prone second source of truth that contradicts the disposable, no-accumulation lifecycle

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### File location and naming

- **MUST** live under `.audits/<review-type>/<target-slug>.md`, where:
  - `<review-type>` is the review spec slug (for example `skill-review`, `agent-review`)
  - `<target-slug>` is an ASCII kebab-case derivation of the reviewed artifact's identifier (for a skill: the skill name; for an agent: the agent name)
- **MUST** encode the `<review-type>` by the subdirectory only; the basename **MUST NOT** repeat it (no `skill-review-<target>.md`)—consuming specs cite the bare `<target-slug>.md` basename and the deletion-commit message already carries the review-type
- **MUST NOT** include a timestamp or sequence number in the filename—there is exactly **one** plan per (review-type, target) at any moment; a rerun overwrites the existing plan
- **MUST** keep `.audits/` checked into git (not `.gitignore`-d), so plans are visible in pull-request diffs and the review trail is shared
- **SHOULD**, when the reviewed artifact lives outside the current repository (for example reviewing a plugin consumer's copy of a skill), record the absolute or repo-relative path of the target in the frontmatter `target` field, while the filename still uses only the slug

### Frontmatter

- **MUST** begin with YAML frontmatter containing at minimum:
  - `review-type`: the review spec slug (string)
  - `target`: the path (repo-relative) of the reviewed artifact
  - `target-kind`: the artifact type: `skill`, `agent`, or a future classifier
  - `specs-applied`: a YAML list of spec slugs with the canonical-version git SHA or tag that the review ran against
  - `repo-revision`: the git SHA of the target repository at review time
  - `created`: ISO-8601 date the plan was produced
  - `status`: one of `open`, `in-progress`, `complete`, `superseded`
- **MUST** update `status` to `in-progress` on the first item check-off, to `complete` when every item is either `- [x]` or a tracked follow-up, and to `superseded` when a rerun replaces the plan before completion
- **MUST NOT** invent values; if a field can't be read from source (for example no git SHA because the target isn't yet committed), the value is `unknown`: not a guess

### Severity scale

This section is the single canonical source for severity vocabulary across every audit, review, and readiness artefact in the portfolio. Other specs (for example `spec/project/spec-readiness/`) **MUST** reference this section rather than redefining their own scale.

- **MUST** classify every finding into exactly one of these four severity levels, in Title Case, in this order of decreasing impact:
  - **Critical**: violates a MUST in the source spec, or directly blocks promotion / merge of the reviewed artefact (load-bearing Open Question on a pre-promotion run, ghost reference to a non-existent spec, MUST↔MUST contradiction across two specs both already promoted)
  - **Warning**: violates a SHOULD in the source spec, or names real ambiguity / drift / coverage gap that a careful reader can still navigate around but should be resolved before the next release
  - **Suggestion**: identifies a MAY-class opportunity, a stylistic improvement, or a one-line fix that elevates the artefact without being violation-class
  - **Info**: an observation, a deliberate-design acknowledgement, an infrastructure-dependent note, or a cross-reference back to a finding that's already tracked elsewhere; no action required
- **MUST NOT** invent additional severity levels (no `BLOCKER`, no `MAJOR/MINOR`, no `P0/P1/P2`); reviewers who feel another level is needed propose a spec amendment, not a local extension
- **MUST** use these labels verbatim—Title Case, no abbreviations, no upper-case variants—in `## Summary` counts, `## Findings` subsection headings, and any per-finding annotation, so downstream tooling can grep them deterministically
- **MUST NOT** downgrade a severity on local judgement alone; disagreement with the classification is a documented waiver recorded in the plan's `## Processing log`, not a silent reclassification

### Plan body structure

- **MUST** include these sections, in this order, each with the exact heading:
  1. `## Scope`: one paragraph naming the target, what was reviewed (frontmatter, body, examples, …), and what was explicitly out of scope
  2. `## Summary`: bullet counts per severity (`Critical`, `Warning`, `Suggestion`, `Info`) plus a single-line go/no-go statement
  3. `## Findings`: the actionable list; one subsection per severity present
  4. `## Processing log`: append-only, one line per item closure, capturing what was done and by whom
- **MUST** keep section headings in English even when the surrounding project's documentation language isn't English, so downstream tooling can grep them deterministically

### Findings format

- **MUST** express every finding as a markdown checkbox item in `## Findings` with the structure:

  ```
  - [ ] [<spec-slug>.<requirement-shorthand>] <one-line statement of what's wrong>.
        Where: <file:line or section reference>.
        Fix: <concrete action—one line>.
        Verify: <how to confirm the fix—one line>.
  ```

  The four labeled lines (`Where`, `Fix`, `Verify`, and the opening statement) **MUST** all be present. If a field genuinely doesn't apply, write `n/a` with one word of reason rather than omitting the line
- **MUST** group findings under severity subsections `### Critical`, `### Warning`, `### Suggestion`, `### Info`, in that order; omit a subsection only when it has zero items
- **MUST** cite the originating spec requirement in the bracketed prefix so a worker can trace every finding back to a specific MUST / SHOULD / MAY; inventions without a spec citation aren't valid findings
- **SHOULD** order items inside a severity section by affected area (frontmatter → body → tools → examples) so a worker can address related items together
- **MAY** annotate a finding with a trailing `→ deferred: <issue-url>` when the worker decides the item is real but out-of-scope for the current plan cycle; deferred items still count as closed for lifecycle purposes but carry the link so the tracked issue becomes the new home

### Lifecycle

- **MUST** be created fresh per review invocation; a rerun against the same target **MUST** overwrite the existing plan in a single commit and set the prior plan's `status` to `superseded` in the overwriting commit message, never edit the old plan into the new one
- **MUST**, when the review target is renamed mid-cycle, rename the plan file via `git mv` (preserving `git log --follow` lineage), update the `target` frontmatter field, and note the move in the commit message; **don't** regenerate, so partial check-off state and the `## Processing log` survive. This is distinct from the supersede path above, which is scoped to a rerun that produces new findings, not a target rename that keeps the same findings under a new identifier
- **MUST** have items marked `- [x]` only when both the fix has landed and the `Verify` step has been executed; partial fixes stay `- [ ]`
- **MUST** append one line to `## Processing log` per closure, in the shape: `YYYY-MM-DD—<item-shorthand>—<action taken>—<verified by>`; `<verified by>` is a single free-text actor label (for example `human:nolte`, `agent:agent-review`) and **MUST NOT** be decomposed into structured username / session / agent sub-fields—per §Non-Goals the spec doesn't prescribe who or what processes the plan, and the commit author already carries machine identity
- **MUST NOT** delete the plan file while any `- [ ]` `Critical` remains open; `Warning` / `Suggestion` / `Info` items **MAY** be deferred to tracked issues to unblock deletion
- **MUST** delete the plan file when every item is either `- [x]` or carries a `→ deferred: <url>` annotation; the deletion commit message **MUST** be `review(<review-type>): close <target>—<C>C/<W>W/<S>S/<I>I` (counts of Critical, Warning, Suggestion, Info at creation time), so the git log is the searchable audit trail
- **SHOULD**, when the plan is deleted, also close any tracked issues referenced by deferred items if the underlying fix has landed elsewhere—the plan's deletion commit names those issues in its body
- **SHOULD** be considered stale and re-evaluated—reprocessed against the current `repo-revision`, or explicitly set to `superseded` instead—if the plan has been open for more than six months without a new `## Processing log` entry. This mirrors `spec/claude/skills-agents-sweep/` §Lifecycle so both audit-artefact specs carry one consistent staleness vocabulary; it's a detect-and-surface convention, not a hard expiry or automatic deletion

### Relationship to other specs

- **MUST** reference this spec from every review spec that produces a plan (`skill-review`, `agent-review`, and any future review type)—the review spec owns the criteria, this spec owns the artifact shape
- **MUST NOT** be used as the output of `spec-drift-audit`; that spec persists a quarterly audit record that isn't meant to be deleted on processing completion
- **SHOULD**, when a review agent (for example `audience-review`) emits a report in the main conversation, still persist the structured plan to `.audits/<review-type>/<target>.md` so the processing contract is consistent regardless of who ran the review
- **SHOULD** consult `spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees when the plan is produced inside a worktree rather than the primary checkout; the per-(review-type, target) uniqueness rule from this spec is only observable inside one working tree at a time, and the worktree-local commit, transfer, and cleanup rules live there
- **SHOULD**, in repositories that forbid direct pushes to `develop`, land the plan and the fix it describes on the same feature-branch PR—create, check-off, `## Processing log` updates, and the deletion commit all in one diff—per `spec/project/parallel-working-copies/` §Audit artefacts; a standalone earlier PR is reserved for reviews run before any fix is scoped

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] `.audits/` exists in the repository and is tracked by git (not listed in `.gitignore`)
- [ ] Every plan file under `.audits/` parses as valid markdown with YAML frontmatter containing `review-type`, `target`, `target-kind`, `specs-applied`, `repo-revision`, `created`, `status`
- [ ] Every plan file contains the four required sections (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) with those exact English headings
- [ ] Every finding in a plan uses the four-line structure (opening statement + `Where` / `Fix` / `Verify`) and cites a spec requirement in the bracketed prefix
- [ ] No plan file exists with an open `- [ ]` `Critical` item and `status: complete`
- [ ] Every plan deletion in `git log` is accompanied by a commit message matching `review(<review-type>): close <target>—<counts>` so the audit trail is searchable
- [ ] At most one plan file exists per (`review-type`, `target`) pair at any commit—a rerun replaces rather than accumulates
- [ ] The `skill-review` and `agent-review` specs both reference this spec as the authoritative output format

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
- Default: an open plan is considered stale and re-evaluated once it has been open for more than six months without a new `## Processing log` entry (aligned with `spec/claude/skills-agents-sweep/` §Lifecycle). Revisit when: any `.audits/<review-type>/<target>.md` plan is observed surviving more than six months with no `## Processing log` line, OR when two or more plans for the same target are observed superseded within a single release cycle (signalling the window is too long)—recalibrate the number from that evidence.
