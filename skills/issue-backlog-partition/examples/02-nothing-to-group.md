# Example 2: the survey forms no group and says so checkably

This repository, 2026-10-03: the paginated `gh api` read of the open issues, pull requests filtered out,
returns three rows.

## collect

| Issue | Title | Rule |
|---|---|---|
| 677 | Quarterly dependency & license audit — 2026 Q4 | `X-TEMPLATE` — labels `chore,dependencies,audit`; the title pattern recurs across closed issues (`gh issue list --state closed --search "Quarterly dependency"` returns three prior quarters) |
| 676 | Quarterly portfolio audit — 2026 Q4 | `X-TEMPLATE` — labels `chore,audit`; same recurrence check |
| 393 | Dependency Dashboard | `X-BOT` — `user.login` is `renovate[bot]` |

Zero issues survive to classification.

## partition and sequence

The candidate graph has no node. There is nothing to grow and nothing to order.

## approve

The artifact still gets written, because the statement "nothing to group" has to be
checkable:

```markdown
## Per-issue table

| Issue | Class | Bounded | Outcome | Group / rule | Touch surface (basis) |
|---|---|---|---|---|---|
| #677 | — | — | excluded | X-TEMPLATE | — |
| #676 | — | — | excluded | X-TEMPLATE | — |
| #393 | — | — | excluded | X-BOT | — |

**Reconciliation:** 3 open − 3 rows = 0.

## Groups

None. The backlog holds no issue that survives the mechanical exclusion rules, so the
candidate graph is empty. The three exclusions are listed above with the rule and its
evidence; each can be challenged by name.
```

The operator is shown the table in one line: three open issues, all excluded by rule, no
group formed, nothing to hand on. The skill still asks for the one approval, so the operator
can challenge any exclusion by name, and records it as the single checkpoint decision. The
run then completes with an empty hand-off log.

## Why the artifact is written anyway

An empty result and a finished survey look the same from the outside. The table with the
rule per row is what distinguishes "I checked and there is nothing" from "I didn't look",
and it's what the next survey diffs against to see what arrived since.
