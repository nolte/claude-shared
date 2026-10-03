# Hand-off payload

Loaded by operation 2 (`classify`, which fills it) and operation 6 (`dispatch`, which
passes it on). The payload is what the survey established once so that no downstream
process fetches it again. It is a **record to re-check, not a fact to trust**: the
receiving skill verifies what it rests on, and a divergence is corrected by measurement
and reported back so the artifact can be amended.

## Per-issue record

One block per surveyed issue. Field names stay English and stable; they are what the
receiving skills grep for.

```yaml
issue: 812
url: https://github.com/<owner>/<repo>/issues/812
title: "…"
author: { login: "...", trusted: true | false | unresolved }
comment_authors:                     # every distinct commenter with trust state
  - { login: "...", trusted: false }
labels: [bug, settings]
linked_prs:                          # from closedByPullRequestsReferences + search
  - { number: 798, state: merged | open | closed, covers_issue: true | false | unknown }
class: bug                           # issue-orchestration closed set
class_rationale: "…one line…"
bounded: true | false                # one outcome, one PR strand, no roadmap item
bounded_rationale: "…one line…"
asserted_cause:                      # omit the block when the issue asserts no cause
  text: "…the cause as the issue states it…"
  status: verified | refuted | unverified
  check: "command or file:line that settles it"
  result: "actual output, when run"
touch_surface:                       # paths the issue plausibly changes
  - path: ".github/settings.yml"
    basis: "named in body" | "inferred from feature area" | "linked PR touched it"
outcome: grouped | single | pipeline | excluded
exclusion_rule: X-BOT                # only when outcome is excluded
group_id: 2026-10-03-settings-drift  # only when outcome is grouped
```

Rules for filling it:

- `trusted` follows `spec/claude/trusted-author-injection-guard/`: operator, repository
  owner, and write/maintain/admin collaborators resolve to `true`; anyone else to `false`;
  a lookup that fails resolves to `unresolved`, which the receiving skill treats as
  untrusted. Resolve the collaborator set once per survey, not once per issue.
- `touch_surface.basis` matters more than the path: a path *named in the body* is strong
  evidence for the shared-touch-surface predicate; a path *inferred from the feature area*
  is weak and should not be the only evidence for an edge in the candidate graph.
- `asserted_cause.status` is `verified` or `refuted` only when `check` was actually run and
  `result` holds its output. Reading the issue again is not a check.
- A record never carries the issue's work-package decomposition. That belongs to the
  receiving skill.

## Per-group record

One block per group that survived operation 3.

```yaml
group_id: 2026-10-03-settings-drift
logical_change: "…exactly one sentence…"
members:
  - { issue: 812, predicate: shared-touch-surface, evidence: ".github/settings.yml named in #812 and #815" }
  - { issue: 815, predicate: shared-touch-surface, evidence: "same" }
  - { issue: 819, predicate: dependency-chain, evidence: "#819 needs the key #812 adds" }
provisional_kind: symptom | class
proposed_type: fix | feat | chore | docs | refactor
dependency_order: [812, 819, 815]
touch_surface_union: [".github/settings.yml", "spec/project/repository-settings/"]
ordering:
  after: []                          # group ids this group must follow
  independent_of: [2026-10-03-docs-parity]
```

## What each receiver gets

| Receiver | Payload | What it re-checks |
|---|---|---|
| `issue-batch-orchestrate` | the per-group record plus every member's per-issue record | admission predicates (operation 1 `admit` re-checks, doesn't re-derive), provisional kind and type (its operations 2–4 confirm or overturn), every unverified cause |
| `issue-orchestrate` | the per-issue record | class, bounded verdict, self-resolution, trust set; its requirements gate still runs |
| `feature-decompose` / `roadmap-plan` | the per-issue record with `bounded: false` and its rationale | whether an existing roadmap item covers it |

The receiving skill owns its own gates. The partition approval authorises the hand-off,
nothing after it.
