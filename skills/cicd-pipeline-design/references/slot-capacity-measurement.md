# Slot-capacity measurement

Per `spec/project/github-actions-best-practices/` §"Runner-slot economy" and
`spec/project/workflow-health/` §"Cancellation rates": how to tell a pipeline that is
*slow* from one that is *starved*, before choosing a remedy. The two look identical from
the pull-request checks tab and have opposite fixes, so the measurement comes first. No
script ships with this recipe on purpose: the calls are three REST reads, and the
reading rule is the part worth carrying, not the tooling.

## Why wait and work are measured separately

A job's wall-clock time is queue wait plus runtime. Runtime is fixed inside the job
(cache, parallelism, a smaller test set). Wait is fixed by asking the shared pool for
fewer jobs, because GitHub-hosted runners draw on one concurrent-job allotment per plan
(Free 20, Pro 40, Team 60 per `github-actions-best-practices` §"Runner-slot economy"
and its [R13]–[R15]) and every repository of the account draws on it at once. Optimising a
job's runtime when its wait dominates changes nothing the operator can see.

## The reads

A token with `actions:read` and `curl` or `gh api` suffice.

1. List the pull-request runs for the window you want:
   `GET /repos/{owner}/{repo}/actions/runs?event=pull_request&per_page=100`, paginated
   with `page=` until the window is full (`nolte/claude-shared#644` used the last 300
   pull-request runs). Filtering on `event=pull_request` keeps the sample to the lane
   whose cadence the operator controls; scheduled and push runs answer a different
   question.
2. For every run, fetch its jobs: `GET /repos/{owner}/{repo}/actions/runs/{id}/jobs`.
   Each job carries `created_at`, `started_at`, `completed_at`, `conclusion`, and the
   run's `head_sha`; the workflow file supplies `needs:` per job name.

## The three derived numbers

- **Wait** = `started_at − created_at` of the job, taken **only on jobs with no
  `needs:`**. A dependent job's `created_at` is stamped when the *run* is created, so
  its wait spans the whole upstream chain and reads like starvation even when the pool
  is idle. Take the median over the window; a mean is dragged by the one run that
  queued overnight.
- **Work** = `completed_at − started_at`. The median is the lane's honest runtime; the
  p90 tells you whether a few jobs carry most of the seconds.
- **Slot demand** = jobs per pull-request `head_sha` (median and max), plus the share
  of jobs finishing under 60 s. A sub-minute job carries little work but holds a full
  slot for its whole life including the wait, so this share is the direct measure of
  how much of the allotment buys almost nothing.

## The account-wide sweep

One repository's view understates the ceiling: the allotment is per account, so the
jobs that held the slots your job waited for were often in a different repository.
Repeat the two reads for **every** repository of the account, merge all jobs'
`started_at`/`completed_at` pairs into one list of start and stop instants, sort it,
and count concurrent jobs at each instant. The maximum is the peak the account
actually reached; compare it to the plan limit. A peak at or above the limit while
first jobs waited is the capacity finding; a peak well below it while jobs still
waited points elsewhere (a stuck job holding slots, or a `needs:` chain misread as
wait).

## The reading rule

Take the numbers in this order and stop at the first that applies:

1. **Wait ≫ work** — a capacity finding under `github-actions-best-practices`
   §"Runner-slot economy". The remedy is fewer jobs: fold sub-minute steps into an
   existing job unless one of §L's four reasons holds, and take sub-minute gates out of
   `needs:` ahead of expensive jobs. Nothing inside the job helps.
2. **Work > trigger cadence** — the lane can't reach a verdict under
   cancel-in-progress. The remedy is re-placing the trigger so the cadence matches the
   runtime, per `workflow-health` §"Cancellation rates", never
   `cancel-in-progress: false`.
3. **Work ≪ cadence, yet the lane is majority-cancelled** — churn. Base-branch updates
   (strict status checks plus auto-merge across many open pull requests) re-queue every
   open branch's fan-out on each merge. The remedy is reducing what each update
   re-queues, also under §"Cancellation rates".

## The traps

- `created_at` on a `needs:` job measures dependency waiting, not queue waiting.
  Excluding those jobs from the wait sample isn't optional.
- `timeout-minutes` bounds runtime only. A job can wait an hour for a slot without ever
  touching its timeout.
- A `cancelled` run is neither red nor green. It's absent from every "is CI healthy"
  glance, from the failure count, and from the required-checks view, so a lane that
  never reaches a verdict looks quiet rather than broken.
- A `gh run list` read that counts only `conclusion` values hides runs still queued,
  whose `conclusion` is empty. Count `status: queued` separately or the wait disappears
  from the sample.

## A worked reading

Measured in `nolte/kamerplanter` on 2026-09-19 (`nolte/claude-shared#644`), one day's
numbers and not thresholds:

- median wait for dependency-free first jobs: 20–26 min
- median job runtime: 32 s
- 66 % of jobs finished under 60 s and carried 7 % of all job-seconds
- median 10 jobs per pull-request head SHA
- peak 46 concurrent jobs across three public repositories of the account

Rule 1 applies: wait exceeds work by two orders of magnitude, two thirds of the slots
bought almost no work, and the account-wide peak of 46 exceeded both the Free (20) and
the Pro (40) allotment. The remedy was fewer jobs per head SHA, not a faster linter —
the linter already ran in 14 s.
