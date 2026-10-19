# Example 1: three open PRs, one current

`gh pr list --base develop` returns #701 (ready, `automerge`), #702 (ready), #703 (draft).

| PR | Draft | `automerge` | Head commit | Rank |
|---|---|---|---|---|
| #701 | no | yes | 2026-10-19 08:12 | 1: ready plus `automerge` |
| #702 | no | no | 2026-10-19 09:40 | 2 |
| #703 | yes | no | 2026-10-19 09:55 | 3 |

The operator confirms #701. Active `pull_request` runs: #702 has 5 (2 running, 3 queued), #703 has 4 queued. The table lists those 9 run ids; the operator approves; 9 `gh run cancel` calls return 8 cancelled and 1 already finished. #701's runs and the `push` run on `develop` are untouched.
