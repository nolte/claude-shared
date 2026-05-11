# Example 03 — Wait mode activated via `--wait` flag

Opt-in wait mode: the user passes `--wait` so the skill is allowed
to wait for state transitions inside a single invocation, bounded
by the documented hard caps (interval ≥60s, wall-clock ≤15 min,
≤10 retries per wait point, visible status line per round, failure
short-circuits to `workflow-health`). This example exercises both
wait points: step 4 (pending required checks) and step 7a (PR
still `OPEN` after the `automerge` label was applied).

## Input prompt

> Promote the draft PR --wait

(`--wait` is the canonical activation signal per
`references/wait-mode.md` §Activation. An equivalent unambiguous
phrase like "warte bis CI grün ist und merge dann" would also
activate wait mode.)

## Input files

Repository state assumed by the harness when this prompt fires:

- Current branch: `feat/portfolio-render-pipeline` (not `develop`,
  not `main`).
- Working tree: clean.
- `gh auth status`: authenticated.
- One open PR is associated with the current branch:
  - `state: OPEN`, `isDraft: true`, `baseRefName: develop`.
  - `title: feat(portfolio): render aggregated inventory under docs/`.
  - `mergeable: MERGEABLE`, `mergeStateStatus: BLOCKED` (blocked
    by draft + pending checks).
  - Touched paths: `skills/portfolio-audit/SKILL.md`,
    `skills/portfolio-audit/references/render.md`,
    `docs/en/portfolio/index.md`, `mkdocs.yml`.
- Feature branch contains `origin/develop`'s tip.
- `gh pr checks` initial snapshot:
  - `lint`: `SUCCESS`.
  - `markdownlint`: `SUCCESS`.
  - `commitlint`: `SUCCESS`.
  - `test`: `IN_PROGRESS`.
  - `docs-build`: `QUEUED`.
- `gh label list` includes `type:feat`, `area:skill`, `area:docs`,
  and `automerge`.
- Repository ships `.github/workflows/automerge.yaml` backed by
  `nolte/gh-plumbing` reusable-automerge with `MERGE_METHOD: squash`.
- Wait-mode argument parsing (per `references/wait-mode.md`):
  - `--wait` present → wait mode active.
  - No `--wait-interval` override → default `90s`.
  - No `--wait-timeout` override → default `10 min`.
  - No `--wait-retries` override → default cap `10`.

## Expected behaviour

1. **Preconditions pass silently.** Branch ≠ `develop`/`main`,
   clean tree, authenticated `gh`, freshness check passes.
2. **Step 1 inspection runs in parallel.** The skill reports the
   PR shape and the initial check rollup (3 green, 2 pending, 0
   failed). It also reports that wait mode is active and prints
   the resolved budget: `interval=90s, timeout=10min, retries≤10`.
3. **Step 2 delegates to `review`.** Touched paths include
   `mkdocs.yml` and `docs/en/portfolio/index.md` — neither is
   security-sensitive (not under `.github/workflows/`,
   `.github/settings.yml`, `**/*.sh`, and not auth/signing
   code), so `security-review` is **not** invoked. The `review`
   skill returns no blocking findings.
4. **Step 3 derives and applies labels.** Candidates: `type:feat`
   (exists → win), `area:skill` (touched `skills/`, exists),
   `area:docs` (touched `docs/` and `mkdocs.yml`, exists). The
   skill applies all three in a single
   `gh pr edit <number> --add-label type:feat --add-label
   area:skill --add-label area:docs` call.
5. **Step 4 enters wait mode for pending required checks.** The
   skill re-invokes `gh pr checks <number>` at the configured
   interval (`90s`) and emits a **visible status line per round**.
   Example trace:
   - Round 1 (t≈0s): `test=IN_PROGRESS, docs-build=QUEUED` → wait
     `90s`.
   - Round 2 (t≈90s): `test=IN_PROGRESS, docs-build=IN_PROGRESS`
     → wait `90s`.
   - Round 3 (t≈180s): `test=SUCCESS, docs-build=IN_PROGRESS` →
     wait `90s`.
   - Round 4 (t≈270s): `test=SUCCESS, docs-build=SUCCESS` → all
     required checks green; exit wait loop and proceed to step 5.
   Caps to enforce throughout this loop:
   - Interval **never** drops below `60s`.
   - Wall-clock **never** exceeds `15 min` total (default `10 min`
     in this example).
   - **Max 10 retries** at this wait point. If a 10th re-check
     still finds pending checks, stop with the same default
     "report-and-stop" outcome as Example 02 — even with `--wait`
     active.
   - **Failure short-circuits**: if any required check flips to
     `FAILURE`, the skill exits wait mode immediately and routes
     to `workflow-health` triage per step 4 of SKILL.md (no merge,
     no waiver, classify the failure).
6. **Step 5 flips draft → ready.** `gh pr ready <number>` runs;
   `gh pr view --json isDraft` confirms `false`.
7. **Step 6 triggers automerge via the label.** The skill applies
   the `automerge` label using the REST call form
   (`gh api -X POST repos/<owner>/<repo>/issues/<number>/labels
   -f "labels[]=automerge"`).
8. **Step 7a enters wait mode again to verify the merge landed.**
   `gh pr view --json state,mergedAt,mergeCommit,url` initially
   returns `state: OPEN`. The skill re-invokes the same call at
   the configured interval (`90s`), emitting a visible status
   line per round, until `state == MERGED` or the wall-clock
   budget is exhausted. Step 4 and step 7a count their retry
   budgets **independently** (each ≤10). Example trace:
   - Round 1 (t≈0s): `state=OPEN, mergedAt=null` → wait `90s`.
   - Round 2 (t≈90s): `state=MERGED, mergedAt=<ts>,
     mergeCommit.oid=<sha>` → exit wait loop.
   `git fetch origin develop && git log --oneline -1
   origin/develop` confirms the merge commit SHA on
   `origin/develop`.
9. **Step 7b precedence over wait mode.** If the wait loop in
   step 7a had timed out with `state: OPEN` and all required
   checks green, the skill would have run the
   `automerge.yaml`-log audit (the `RUN_ID` / `JOB_ID` /
   `gh api .../logs | grep -E "mergeResult: 'merge_failed'|
   Failed to merge PR"` sequence). On a `merge_failed` hit, wait
   mode terminates immediately regardless of remaining time
   budget, and the skill surfaces the workflow-health
   classification (commonly `stale pin` on the reusable workflow's
   `uses:` tag).
10. **Step 8 offers (does not execute) cleanup.** Verifies the
    remote feature branch is gone via
    `gh api repos/<owner>/<repo>/git/refs/heads/feat/portfolio-render-pipeline`
    returning `404`, then offers `git checkout develop && git
    pull --ff-only` and `git branch -d
    feat/portfolio-render-pipeline` for the user to confirm.
11. **Final report (in German per global user-language policy)**
    surfaces: PR URL, merged-at timestamp, merge commit SHA on
    `origin/develop`, the labels applied (`type:feat`,
    `area:skill`, `area:docs`, `automerge`), the per-wait-point
    round counts and total wall-clock spent, and the offered
    local-cleanup commands.

Hard-rule compliance to verify in this scenario:

- Polling occurred **only inside wait mode** (activated by
  `--wait`).
- Every wait round produced a visible status line — no silent
  background polling.
- Interval ≥60s respected (default `90s`); wall-clock ≤15 min
  respected (default `10 min` budget); per-wait-point retry cap
  ≤10 respected; step 4 and step 7a counted their retries
  independently.
- The skill did **not** flip draft → ready while any required
  check was pending — wait mode runs **before** step 5.
- The skill did **not** apply `--admin`, `--merge`, or `--rebase`.
- The skill did **not** create a new GitHub label.
- The skill did **not** treat the `automerge.yaml` workflow's
  `SUCCESS` conclusion as proof — `state == MERGED` on the PR
  itself was the gate, with step 7b standing by for the
  `OPEN`-with-green-checks edge case.
- The skill did **not** delete the remote feature branch — the
  platform setting handled it.
