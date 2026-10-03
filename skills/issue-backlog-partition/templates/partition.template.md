# Backlog partition: {{repository}} — {{YYYY-MM-DD}}

> Run-scoped artifact. Consumed by the hand-offs of operation 6, left untracked, never
> committed to any branch, never hidden behind a `.gitignore` entry. The durable trail is
> the group artifacts and pull requests the outcomes produce.

## Survey scope

- **Repository:** {{owner/repo}}
- **Surveyed at:** {{ISO timestamp}}
- **Open issues at survey time:** {{n}} (`gh issue list --state open --json number | jq length`)
- **Exclusion rules applied:** {{X-QUESTION, X-BOT, X-TEMPLATE, X-RESOLVED, X-INFLIGHT}}
- **Trusted-author set resolved via:** {{command and result count}}
- **Research question:** Which of the {{n}} open issues form groups under the three
  admission predicates of `spec/project/issue-batch-integration/` §A, and in what order
  can those groups be worked?

## Per-issue table

Every open issue appears exactly once. Row count must equal the count above.

| Issue | Class | Bounded | Outcome | Group / rule | Touch surface (basis) |
|---|---|---|---|---|---|
| #{{n}} | {{class}} | {{yes/no}} | {{grouped / single / pipeline / excluded}} | {{group id or X-rule}} | {{path (named in body)}} |

**Reconciliation:** {{n}} open − {{rows}} rows = {{0}}.

## Groups

### {{YYYY-MM-DD}}-{{slug}}

**Logical change, in one sentence:** {{one sentence — if it cannot be written, this is not
a group}}

| Member | Predicate | Evidence |
|---|---|---|
| #{{n}} | {{thematic coupling / shared touch surface / dependency chain}} | {{file:line, path named in body, or command output}} |

- **Provisional cluster kind:** {{symptom / class}} — {{why}}
- **Proposed type:** {{fix / feat / chore / docs / refactor}} — {{dominant member class}}
- **Dependency order inside the group:** {{topological order, or "independent"}}
- **Touch-surface union:** {{paths}}
- **Unverified asserted causes:** {{issue → check that would settle it, or "none"}}

## Dissolved candidates

| Candidate members | Why it dissolved | Resulting outcomes |
|---|---|---|
| {{#a, #b, #c}} | {{no one-sentence change; cut at weak edge …}} | {{singles / two groups}} |

## Ordering

| Group | After | Independent of | Reason |
|---|---|---|---|
| {{group id}} | {{group id or —}} | {{group ids}} | {{shared path / dependency / disjoint on both tests}} |

## Singles

{{issue numbers, each with its class — handed to `issue-orchestrate` with its record}}

## Pipeline

{{issue numbers with the bounded rationale — handed to `feature-decompose` /
`roadmap-plan`, or recorded as unhandable when `nolte-planning` isn't installed}}

## Excluded

| Issue | Rule | Evidence |
|---|---|---|
| #{{n}} | {{X-…}} | {{author login / PR number / label set}} |

## Open questions for the operator

- {{a membership the evidence leaves ambiguous, and the two readings}}

## Approval

- **Partition approved by operator:** {{yes / pending}} — {{timestamp}}
- **Covers:** membership, outcomes, ordering. Not a write gate for any group, not a
  dispatch gate for any single.

## Hand-off log

| Outcome | Receiver | Handed at | Receiver's correction (if any) |
|---|---|---|---|
| {{group id}} | issue-batch-orchestrate | {{timestamp}} | {{—}} |
