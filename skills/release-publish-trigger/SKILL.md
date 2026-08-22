---
name: release-publish-trigger
description: "Validates every release-automation pre-publish gate locally, then dispatches release-publish.yml via `gh workflow run` for the open release-drafter draft on develop, per the canonical-language file under spec/project/release-skill-layer/ §\"Skill B — Release publish trigger\". Verifies that exactly one open draft exists, the draft tag is reachable from the develop tip, version-bearing files align under their declared transform, every required status check reports SUCCESS on the pull-request head the develop tip merges, and `.github/workflows/release-publish.yml` exists. Refuses to dispatch on any failed gate; routes red checks to workflow-health triage. Never calls `gh release edit --draft=false` directly. Invoke when the user asks to \"publish the release\", \"trigger release publish\", \"ship the release\", or equivalent German-language requests. Typically called by sprint-review's opt-in chain, not directly after sprint closure."
tags: [release]
phase: close-release
summary: "Validates every pre-publish gate locally, then dispatches release-publish.yml for the open release-drafter draft on develop."
summary_de: "Prüft jeden Pre-Publish-Gate lokal und dispatched dann release-publish.yml für den offenen Release-Drafter-Draft auf develop."
use_when:
  - "you want to publish the open release-drafter draft"
  - "you want to ship the release after every gate is green"
  - "you want pre-publish gate verification + workflow_dispatch in one step"
dont_use_when:
  - situation: "You want to curate the release notes rather than publish"
    alternative: release-notes-curate
  - situation: "You want to triage a red required check that blocks the gate"
    alternative: workflow-health-triage
see_also:
  - release-notes-curate
  - workflow-health-triage
---

# Release Publish Trigger

Operationalises `spec/project/release-skill-layer/<canonical_language>.md` §"Skill B — Release publish trigger": validates every `release-automation` §Pre-publish verification gate locally, then dispatches `release-publish.yml` via `gh workflow run`. The workflow remains the audit-trail point for the Draft → Published transition; this skill is the local pre-flight plus dispatch.

## Why this is a skill, not an agent

- **Externally-visible mutation gates on user confirmation** — `gh workflow run release-publish.yml` triggers an external publish chain (release published → `release-cd-refresh-master.yml` → `main` fast-forward → packaging workflows); mid-flow operator gating is core to the contract and would be lost in an agent's fire-and-forget shape.
- **Output flows back into the main conversation** — the gate-by-gate validation report, the dispatch URL, and the post-dispatch status all surface in the conversation so the operator can decide.
- **Orchestrator that routes to other skills on failure** — red required checks route to `workflow-health` triage; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: a tool-restricted agent (read + a single `gh` Bash) could perform the verification half cleanly, but the dispatch decision needs the operator in the loop and the skill stays in the conversation to surface the run URL and follow-up status — keeping the whole flow in one skill is simpler than a forced split.

## User-language policy

Detect the operator's language and respond in it. All `git`, `gh api`, and `gh workflow run` invocations stay English so that `release-publish.yml`'s job summary, `release-drafter`'s draft body, and downstream automation stay consistent across the portfolio.

## German trigger phrases

The frontmatter `description` keeps the trigger lexicon English-only per `spec/claude/skill-management/` §Structure (plugin-distributed skills). Treat the following German paraphrases as equivalent and discoverable through this skill:

- "veröffentliche das Release"
- "stoße den Release-Publish an"
- "ship das Release"

## Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`) and the remote resolves to a GitHub repository.
- Confirm `gh` is authenticated (`gh auth status`).
- Locate `spec/project/release-skill-layer/` and `spec/project/release-automation/` — either in the target repo or via the `nolte-shared` plugin install path. Stop and ask if neither is reachable.
- Confirm the repo's default branch (`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`) is the integration branch the spec applies to (typically `develop`).

## Operations

Operation 1 resolves the open draft and Operation 2 detects the project type (the index into `release-automation` §Version-bearing files, shared with Skill A per the spec's §Skill split and shared shape MUST). Operations 3 to 5 then form a Plan-validate-execute cycle: Operation 3 walks every pre-publish gate, Operation 4 surfaces the validated state for explicit operator confirmation, and Operation 5 dispatches `release-publish.yml`. Operation 6 follows the dispatched run until it leaves the queue and reports from there; a landed dispatch isn't the skill's terminal state, because a queued run can still be superseded without publishing.

### 1. Resolve the open draft

- Run `gh release list --json isDraft,tagName,targetCommitish,createdAt,name`.
- Filter to drafts whose `targetCommitish` equals the default branch.
- **Refuse and report** when zero drafts match (operator should run `release-drafter.yml` first) or when more than one matches without an explicit `--tag` argument from the operator (no "newest wins" heuristic, per `release-automation` §Operational contract).

**Tooling (optional GitHub MCP) — go/no-go: GO (narrow).** Prefer `github:list_releases` for the draft resolution here (Op 1) and `github:get_release_by_tag` for the post-publish verify (Op 6), falling back to the `gh` commands shown, per `spec/claude/mcp-tool-preference/`. The `release-publish.yml` dispatch, the required-check-runs gate, and all workflow-run status reads have no MCP tool and stay `gh` (OQ-D); the reachability / version-file / alignment gates stay local git. `gh`/git stays authoritative; output is identical.

### 2. Detect project type

Per `spec/project/release-skill-layer/` §Skill split and shared shape (MUST), both release-layer skills follow the **same** six project-type detection signals used by `github-issue-templates-apply` and by `release-notes-curate` (Skill A). Walk these six signals in order and stop at the first match. Read the files via the standard read tools — never via filename heuristics alone:

1. **Claude Code plugin** — `.claude-plugin/plugin.json` exists; top-level `skills/` and / or `agents/` folder present.
2. **Python application** — `pyproject.toml` declares `[project.scripts]` (or equivalent application entry point), no library distribution metadata.
3. **Python library** — `pyproject.toml` declares a distributable package without an application entry point.
4. **Node / TypeScript library or app** — `package.json` exists; `main` / `exports` indicates library, `bin` / `scripts.start` indicates app.
5. **CLI tool** — declared CLI entry point in `pyproject.toml` (`[project.scripts]`), `package.json` (`bin`), or `Cargo.toml` (`[[bin]]`).
6. **Documentation-only repo** — `mkdocs.yml`, `docusaurus.config.*`, or similar exists with no application source.

When `.github/release-skill-layer.yml` declares an explicit `project_type:` value, use it instead of the autodetection (override path) — the same override that Skill A honours.

When no signal matches, stop and ask the operator to declare the project type manually. Never proceed with a generic fallback.

The detected type is the index into `release-automation` §Version-bearing files: the "Version-bearing files aligned" gate uses it to select the correct default version-bearing-file rows for this repo (Claude Code plugin, Python package, Node.js package, HACS integration, etc.) before reading and comparing each file.

### 3. Validate every pre-publish gate

Walk these gates in order. **The skill MUST NOT proceed past a failed gate**; surface the gate name, the failure detail, and the remediation path.

#### 1. Draft tag reachable from develop

- `git fetch origin develop`.
- Resolve the draft's `targetCommitish` SHA.
- Run `git merge-base --is-ancestor <target-sha> origin/develop`.
- **Failure**: the draft is stale relative to `develop`. Remediation: re-run `release-drafter.yml` to refresh the draft target.

#### 2. Version-bearing files aligned

- Read the version-bearing file list per `release-automation` §Version-bearing files: select the default-table rows for the project type detected in step 2, or use the override at `.github/release-automation.yml` when the repo declares one.
- For every declared file, read the value at the `target-sha` (`git show <target-sha>:<path>` plus the spec's selector) and compare against the target tag under the file's value transform (typically "strip leading `v`" if the existing convention omits it).
- **Failure**: any file whose value does not equal the target tag under transform. Remediation: open a `chore(release): <tag>` PR (fallback path) or wait for the workflow-driven primary path to land its alignment commit.

#### 3. Alignment commit present

- Identify the most recent commit on `develop` that touched any version-bearing file: `git log -1 --pretty=%s --follow -- <path>`.
- Verify the subject prefix starts with `chore(release): <tag>` (the prefix-match accepts the `(#N)` suffix GitHub appends on squash-merge, per `release-automation` §Pre-publish verification).
- **Failure**: no `chore(release): <tag>` commit on the path. Remediation: same as the "Version-bearing files aligned" gate.

#### 4. Required status checks SUCCESS where they were enforced

Evaluate this gate on the **pull-request head** the develop tip squash-merges, not on the tip.

- Read the required check list from `.github/settings.yml` (`branches[name=develop].protection.required_status_checks.contexts`).
- Resolve the commit to judge:
  - `gh api repos/<owner>/<repo>/commits/<tip-sha>/pulls --jq '.[0].head.sha'`.
  - A SHA comes back → that is the commit to query, and report it to the operator alongside the tip so the substitution is visible.
  - Nothing comes back (a direct push, or a merge the API does not associate) → fall back to the tip SHA and say so in the report.
- Query `gh api repos/<owner>/<repo>/commits/<sha>/check-runs` for the resolved SHA and confirm every required context appears with `conclusion=success`.
- **Failure**: any required check is `failure`, `cancelled`, `timed_out`, still `in_progress`, or **absent**. Remediation:
  - red checks → route to `workflow-health` triage (classify as `defect` / `flake` / `infra` / `stale pin` / `secret drift` / `other`); never retry the dispatch blindly.
  - pending checks → stop and ask the operator to wait, or opt in to wait mode (see "Wait mode" below).
  - absent on a resolved **pull-request head** → a genuine gap: branch protection should have required it there. Report it as a protection-configuration problem, not as a missing run.
  - absent on a **fallback tip** → the repository published from a commit on which its required contexts were never enforced. Refuse, and say that plainly rather than treating absence as green.

**Why not the tip.** Branch protection enforces its contexts on the pull-request head, which is where the always-run constructions that guarantee a report live. The tip is a *different* commit, produced by squash, and only receives whatever `push`-triggered workflows apply to it — so a required check whose `push` trigger carries a `paths:` filter is simply absent whenever the merge touched none of those paths. That is the normal case, not an edge one. Reading absence strictly blocks most releases; reading it leniently validates a subset while appearing to validate the set. Neither is a gate.

The tip's tree is still the tree those checks ran against: `pull-request-workflow` §Branch freshness requires `required_status_checks.strict: true`, so a pull request can only merge while up to date with `develop`. If a repository has turned `strict` off, say so in the report — the substitution's justification does not hold there.

#### 5. Workflow file present

- Confirm `.github/workflows/release-publish.yml` exists in the repo.
- **Failure**: the operator should adopt `release-automation` first; this skill stops and reports.

### 4. Disclose the validated state and confirm

Before dispatch, surface to the operator as a single block:

- target tag and `target_commitish` SHA;
- result of each gate (PASS / FAIL with detail);
- version-bearing-file diff summary (file, current value, target value);
- audience-coverage summary when the draft body carries the `release-skill-layer:project-context-start` marker (Skill A has run); a non-blocking note offering to dispatch `release-notes-curate` first when the marker is absent;
- the exact `gh workflow run` invocation that will be issued.

Block the dispatch until the operator confirms.

### 5. Dispatch

On confirmation:

- Run `gh workflow run release-publish.yml --ref develop -f tag=<tag>`. The `tag` input is mandatory regardless of how many drafts are open (per `release-automation` §Operational contract — no "newest wins" heuristic in the workflow either).
- When the operator opts in to `--dry-run`, dispatch with `-f dry_run=true` so the workflow validates without flipping `draft: false`.
- **Never** call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id>` with `draft=false`, or any other body that flips the draft state from this skill. The workflow is the only path.

### 6. Follow the run out of the queue

Immediately after `gh workflow run` returns:

- Find the new run: `gh run list --workflow=release-publish.yml --limit 1 --json databaseId,status,conclusion,url,headSha`. The match is the run whose `headSha` equals the draft's target SHA and whose `status` is `queued` or `in_progress`.
- **A landed dispatch isn't the end of the job.** While the run is `queued` it can be superseded and `cancelled` without ever starting: GitHub drops a *pending* run as soon as a newer one queues into the same concurrency group. `release-publish.yml` shares the `release-draft` group with `release-drafter.yml`, which fires on every push to `develop`, so every merge opens the window. `cancel-in-progress: false` doesn't help here: it governs only whether an already *running* run is cancelled.
- **Re-check `gh run view <id> --json status,conclusion` until the run leaves the queue**, under the same caps as wait mode (interval ≥60 s, default 90 s; wall-clock timeout ≤15 min, default 10 min; max 10 retries; a visible status line per round). Three outcomes:
  - `status` is `in_progress` or `completed`: the run started and can no longer be superseded. Report the run URL and the status. **This is the terminal state of the single-shot default.**
  - `conclusion=cancelled` without ever starting: the dispatch was **superseded**. Handle it per the terminal-conclusion branch below.
  - still `queued` when the caps run out: report an **unresolved dispatch**. Say that the run hasn't started, that it can still be superseded, and give the URL. **Never** report this as a success.
- **The default stays single-shot**: leaving the queue is the terminal state, not completion. The operator re-invokes (or opens the URL) once the run finishes.
- **Wait mode** is the explicit opt-in (via `--wait` argument or unambiguous prompt phrasing like "warte bis der Publish durch ist"): keep polling past the queue until `status=completed` or the timeout, under the same caps. Bound caps mirror `pull-request-merge`'s wait mode, and a failure short-circuits to `workflow-health` triage.

On a terminal conclusion (reached in wait mode, or on a later re-invocation):

- On `conclusion=success`: confirm with the operator that the release is now published (`gh release view <tag> --json isDraft` returns `{"isDraft": false}`) and that `release-cd-refresh-master.yml` has started a downstream run (`gh run list --workflow=release-cd-refresh-master.yml --limit 1`); both checks are part of `release-automation`'s acceptance criteria.
- On `conclusion=cancelled`: the run was **superseded, not broken**. Report it as such, name the re-dispatch as the next action, and state plainly that the release was **not** published. Do **not** route to `workflow-health`: there's no red check to triage and it will find nothing. This is the one failure mode where a second dispatch from this skill is allowed. Re-run operation 3 before re-dispatching, because every gate is re-derived from live state and `develop` may have moved since the first attempt.
- On `conclusion=failure`: do **not** retry. Route to `workflow-health` triage — classify per `spec/project/workflow-health/`. The most common cause is a `merge_failed` from `pascalgn/automerge-action` when `release-publish.yml` itself uses `automerge-action`; check the run logs for `mergeResult: 'merge_failed'` per `pull-request-merge` step 7b and route as a stale-pin incident if so.

## Wait mode

Activated by `--wait` or unambiguous operator phrasing. Caps mirror `pull-request-merge`:

- Interval ≥ 60 s (default 90 s).
- Wall-clock timeout ≤ 15 min (default 10 min).
- Max retries ≤ 10.
- Visible status line per round.
- Failure short-circuits to `workflow-health`.

The single-shot default exists because the prompt-cache TTL is 5 min; unbounded polling burns the cache. Caps balance: short waits stay cache-warm, long waits accept one cache miss but never balloon.

## Single-shot by design (not resumable)

Every gate is re-derived from live GitHub state on each run, and the dispatch itself is idempotent to re-validate — a persisted checkpoint per `spec/claude/resumable-work/` would only cache staleness. Re-invoking after an interruption simply re-walks the gates; this is the deliberate exception to the plugin's resumable convention, recorded here so reviewers don't flag the absent `resumable` flag as an omission.

## Gotchas

- **A queued run can vanish before it runs**, and `cancel-in-progress: false` doesn't protect it. `release-publish.yml` shares the `release-draft` lane with `release-drafter.yml` deliberately, and the next merge to `develop` supersedes a still-pending publish. Read `references/supersession.md` before acting on a `cancelled` run or proposing to split the lane.
- `pascalgn/automerge-action` (used by some `release-publish.yml` implementations downstream) exits 0 even on `mergeResult: 'merge_failed'`. A green `release-publish.yml` run is **not** proof the publish happened. Always re-verify `gh release view <tag> --json isDraft` after a `success` conclusion.
- The `tag` input is mandatory because `release-automation` forbids the workflow's "newest wins" heuristic. Even when only one draft is open, this skill passes `-f tag=<tag>` explicitly.
- A red required check on `develop`'s tip blocks publish but is not always recoverable by re-running. The triage path is `workflow-health`, not "retry until green."
- `release-cd-refresh-master.yml` should fire automatically after `release-publish.yml` succeeds. When it doesn't fire (the known-platform-constraint case where `release: published` from `GITHUB_TOKEN` doesn't cascade to a fresh workflow run, per `workflow-health` §Known platform constraints), surface this and route to manual fast-forward of `main` per `branching-model` §Release flow.
- The skill never runs `gh release edit --draft=false` even as a fallback — that flag is reserved for incident response and remains a manual operator action documented in `release-automation` §Non-Goals.

## Examples

- Read `examples/01-clean-dispatch-all-gates-pass.md` when all pre-publish gates pass and the skill dispatches the release workflow cleanly.
- Read `examples/02-version-bearing-files-misaligned.md` when version-bearing files are out of sync and the gate blocks dispatch.
- Read `examples/03-required-checks-red-route-to-workflow-health.md` when a required check on `develop`'s tip is red and triage routes to `workflow-health`.
- Read `examples/04-dispatch-superseded-in-queue.md` when a dispatched run is cancelled in the queue without publishing, or is still queued when the caps run out.

## Hard rules

- Never dispatch when any pre-publish gate fails. Failures route to `workflow-health` triage.
- Never call `gh release edit --draft=false`, `gh api -X PATCH .../releases/<id>` with `draft=false`, or any other body that flips the draft state. The workflow is the only publish path.
- Never use a `--ref` other than the default branch (typically `develop`).
- Never poll to completion outside an explicit operator opt-in to wait mode; the single-shot default ends when the run leaves the queue, not when the dispatch lands.
- Never report a landed dispatch, or a run still `queued`, as a publish that happened. A dispatch that GitHub accepted can still be superseded and cancelled without publishing anything.
- Never route a `cancelled` run to `workflow-health`. It's a superseded dispatch, not a workflow defect, and re-dispatching (after re-running the gates) is the remedy.
- Never retry a failed `release-publish.yml` run blindly. Triage classifies the failure first.
- Never proceed without explicit operator confirmation of the disclosed validation state.
- When `spec/project/release-skill-layer/` or `spec/project/release-automation/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
