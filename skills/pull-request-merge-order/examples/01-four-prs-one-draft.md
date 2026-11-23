# Example 1: four open PRs, one draft, one overlap, one dependency bot

Open against `develop`, all required checks green:

- #811 `feat(spec): add merge-order note`, touches `spec/a.md`, 40 lines
- #812 `chore(deps): update vale to v3.29.0`, author `app/renovate`, same-repository branch, touches `Taskfile.yml`
- #813 `docs: rework catalog intro`, draft
- #815 `fix(spec): typo in merge note`, touches `spec/a.md`, 2 lines

`order` prints:

```
| # | PR | Readiness | Bot | Why before the next |
|---|---|---|---|---|
| 1 | #812 chore(deps): update vale to v3.29.0 | CLEAN | yes | conflict risk: no file overlap first; among overlapping, smaller diff first |
| 2 | #815 fix(spec): typo in merge note | CLEAN | no | conflict risk: no file overlap first; among overlapping, smaller diff first |
| 3 | #811 feat(spec): add merge-order note | CLEAN | no | last |

Head: #812

Not mergeable now:
- #813 docs: rework catalog intro: draft
```

PR #812 leads because it shares no file with another PR; #815 and #811 both touch `spec/a.md`, so the smaller diff goes first and #811 rebases once over a two-line change. The draft #813 gets no slot.

The operator confirms. `pull-request-runner-sweep --current 812` lists the active runs of #815, #811, and #813, asks its own confirmation, and cancels them. The report names the cancelled run ids and the next step: `pull-request-merge` on #812, then run this skill again, because after #812 lands #815 and #811 read `BEHIND`.
