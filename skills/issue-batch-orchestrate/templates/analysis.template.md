# Group pre-analysis: {{group-id}}

> Run-scoped artifact. Committed on the integration branch, removed with a fix-forward
> `git rm` before the bundle merges. It must never reach the default branch, and it must
> never be hidden behind a `.gitignore` entry.

## Scope of this analysis

**Research question:** {{the question this analysis was scoped to answer}}

**The group's single logical change, in one sentence:** {{one sentence — if it cannot
be written, this is not a group}}

**Out of scope:** {{what this group deliberately leaves out, and why}}

**Tier:** {{2 or 3}} — {{reason; Tier 3 when the group crosses repositories or a
published contract}}

## Members

| Issue | Class | Admitting predicate | Evidence |
|---|---|---|---|
| #{{n}} | {{bug / feature-request / spec-change / security / docs / refactor / infra}} | {{thematic coupling / shared touch surface / dependency chain}} | {{file:line, path, or command output}} |

**Dependency ordering:** {{topological order; state explicitly when members are
independent}}

**Shared touch surface:** {{the files or paths more than one member changes}}

## Mode decision

**Mode:** {{A — single strand / B — sub-branch per member}}

**Reason:** {{Mode B requires a member likely to need removal: uncertain acceptance, an
external dependency, or an outstanding review that could reject it}}

## Structural finding

**Cluster shape:** {{symptom cluster / class cluster / neither — none found}}

**Root cause or defect class:** {{what the members have in common beneath the symptom}}

**Process finding:** {{the rule, gate, or missing check in the development process, plus
the issue it was filed as — or "none"}}

**Preventive change:** {{the concrete rule, guard, or check that would have stopped this
group from arising}}

**Recurrence fed to the portfolio loop:** {{finding class and its recurrence count}}

## Completeness matrix

One row per member, one column per artifact class this repository ships. Every cell
holds a named change plus its proving check, or `not applicable` with a reason. No cell
is empty.

| Member | {{class}} | {{class}} | {{class}} |
|---|---|---|---|
| #{{n}} | {{change; check: `{{command}}`}} | {{not applicable — reason}} | {{change; check: `{{command}}`}} |

## Risks

- {{risk, and what it would cost}}

## Open questions for the operator

- {{question that must be answered before the write gate}}

## Member results

Filled during implementation. Each entry records the dispatched specialist and the
**actual output** of every declared check, never an assertion that it passed.

| Member | Specialist | Check | Actual output |
|---|---|---|---|
| #{{n}} | {{subagent_type or skill name, or "no matching specialist — generalist"}} | {{command}} | {{verbatim result}} |

## Deviations

| Member | Kind | What changed |
|---|---|---|
| #{{n}} | {{local adaptation / structural regression}} | {{what differed, and for a regression: which assumption failed and when the plan was re-approved}} |
