# release-publish-trigger

_Validates every release-automation pre-publish gate locally, then dispatches release-publish.yml via `gh workflow run` for the open release-drafter draft on develop, per spec/project/release-skill-layer/<canonical_language>.md §\"Skill B — Release publish trigger\". Verifies that exactly one open draft exists, the draft tag is reachable from the develop tip, version-bearing files align under their declared transform, every required status check on develop is SUCCESS, and `.github/workflows/release-publish.yml` exists. Refuses to dispatch on any failed gate; routes red checks to workflow-health triage. Never calls `gh release edit --draft=false` directly. Invoke when the user asks to \"publish the release\", \"trigger release publish\", \"ship the release\", or equivalent German-language requests._

- **Plugin:** `nolte-shared`
- **Phase:** 7 Close & Release (`close-release`)
- **Tags:** `release`
- **Quelle:** [skills/release-publish-trigger/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/release-publish-trigger/SKILL.md)

---

## Release Publish Trigger

Operationalises `spec/project/release-skill-layer/<canonical_language>.md` §"Skill B — Release publish trigger": validates every `release-automation` §Pre-publish verification gate locally, then dispatches `release-publish.yml` via `gh workflow run`. The workflow remains the audit-trail point for the Draft → Published transition; this skill is the local pre-flight plus dispatch.

### Why this is a skill, not an agent

- **Externally-visible mutation gates on user confirmation** — `gh workflow run release-publish.yml` triggers an external publish chain (release published → `release-cd-refresh-master.yml` → `main` fast-forward → packaging workflows); mid-flow operator gating is core to the contract and would be lost in an agent's fire-and-forget shape.
- **Output flows back into the main conversation** — the gate-by-gate validation report, the dispatch URL, and the post-dispatch status all surface in the conversation so the operator can decide.
- **Orchestrator that routes to other skills on failure** — red required checks route to `workflow-health` triage; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: a tool-restricted agent (read + a single `gh` Bash) could perform the verification half cleanly, but the dispatch decision needs the operator in the loop and the skill stays in the conversation to surface the run URL and follow-up status — keeping the whole flow in one skill is simpler than a forced split.

### User-language policy

Detect the operator's language and respond in it. All `git`, `gh api`, and `gh workflow run` invocations stay English so that `release-publish.yml`'s job summary, `release-drafter`'s draft body, and downstream automation stay consistent across the portfolio.

### Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`) and the remote resolves to a GitHub repository.
- Confirm `gh` is authenticated (`gh auth status`).
- Locate `spec/project/release-skill-layer/` and `spec/project/release-automation/` — either in the target repo or via the `nolte-shared` plugin install path. Stop and ask if neither is reachable.
- Confirm the repo's default branch (`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`) is the integration branch the spec applies to (typically `develop`).

### Operations

Operations 2 to 4 form a Plan-validate-execute cycle: Operation 2 walks every pre-publish gate, Operation 3 surfaces the validated state for explicit operator confirmation, and Operation 4 dispatches `release-publish.yml`. Operation 5 verifies the dispatch landed and reports the run URL without polling to completion (unless wait mode is opted in).

#### 1. Resolve the open draft

- Run `gh release list --json isDraft,tagName,targetCommitish,createdAt,name`.
- Filter to drafts whose `targetCommitish` equals the default branch.
- **Refuse and report** when zero drafts match (operator should run `release-drafter.yml` first) or when more than one matches without an explicit `--tag` argument from the operator (no "newest wins" heuristic, per `release-automation` §Operational contract).

#### 2. Validate every pre-publish gate

Walk these gates in order. **The skill MUST NOT proceed past a failed gate**; surface the gate name, the failure detail, and the remediation path.

##### 2a. Draft tag reachable from develop

- `git fetch origin develop`.
- Resolve the draft's `targetCommitish` SHA.
- Run `git merge-base --is-ancestor <target-sha> origin/develop`.
- **Failure**: the draft is stale relative to `develop`. Remediation: re-run `release-drafter.yml` to refresh the draft target.

##### 2b. Version-bearing files aligned

- Read the version-bearing file list per `release-automation` §Version-bearing files: the default table by repo type, or the override at `.github/release-automation.yml` when the repo declares one.
- For every declared file, read the value at the `target-sha` (`git show <target-sha>:<path>` plus the spec's selector) and compare against the target tag under the file's value transform (typically "strip leading `v`" if the existing convention omits it).
- **Failure**: any file whose value does not equal the target tag under transform. Remediation: open a `chore(release): <tag>` PR (fallback path) or wait for the workflow-driven primary path to land its alignment commit.

##### 2c. Alignment commit present

- Identify the most recent commit on `develop` that touched any version-bearing file: `git log -1 --pretty=%s --follow -- <path>`.
- Verify the subject prefix starts with `chore(release): <tag>` (the prefix-match accepts the `(#N)` suffix GitHub appends on squash-merge, per `release-automation` §Pre-publish verification).
- **Failure**: no `chore(release): <tag>` commit on the path. Remediation: same as 2b.

##### 2d. Required status checks SUCCESS on develop tip

- Read the required check list from `.github/settings.yml` (`branches[name=develop].protection.required_status_checks.contexts`).
- For the develop tip SHA, query `gh api repos/<owner>/<repo>/commits/<sha>/check-runs` and confirm every required context appears with `conclusion=success`.
- **Failure**: any required check is `failure`, `cancelled`, `timed_out`, or still `in_progress`. Remediation:
  - red checks → route to `workflow-health` triage (classify as `defect` / `flake` / `infra` / `stale pin` / `secret drift` / `other`); never retry the dispatch blindly.
  - pending checks → stop and ask the operator to wait, or opt in to wait mode (see "Wait mode" below).

##### 2e. Workflow file present

- Confirm `.github/workflows/release-publish.yml` exists in the repo.
- **Failure**: the operator should adopt `release-automation` first; this skill stops and reports.

#### 3. Disclose the validated state and confirm

Before dispatch, surface to the operator as a single block:

- target tag and `target_commitish` SHA;
- result of each gate (PASS / FAIL with detail);
- version-bearing-file diff summary (file, current value, target value);
- audience-coverage summary when the draft body carries the `release-skill-layer:project-context-start` marker (Skill A has run); a non-blocking note offering to dispatch `release-notes-curate` first when the marker is absent;
- the exact `gh workflow run` invocation that will be issued.

Block the dispatch until the operator confirms.

#### 4. Dispatch

On confirmation:

- Run `gh workflow run release-publish.yml --ref develop -f tag=<tag>`. The `tag` input is mandatory regardless of how many drafts are open (per `release-automation` §Operational contract — no "newest wins" heuristic in the workflow either).
- When the operator opts in to `--dry-run`, dispatch with `-f dry_run=true` so the workflow validates without flipping `draft: false`.
- **Never** call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id>` with `draft=false`, or any other body that flips the draft state from this skill. The workflow is the only path.

#### 5. Verify the dispatch landed

Immediately after `gh workflow run` returns:

- Find the new run: `gh run list --workflow=release-publish.yml --limit 1 --json databaseId,status,conclusion,url,headSha`. The match is the run whose `headSha` equals the draft's target SHA and whose `status` is `queued` or `in_progress`.
- Report the run URL plus the current status to the operator.
- **Default behaviour is single-shot**: the skill does **not** poll to completion. The operator re-invokes (or opens the URL) once the run finishes.
- **Wait mode** is the explicit opt-in (via `--wait` argument or unambiguous prompt phrasing like "warte bis der Publish durch ist"): re-check `gh run view <id> --json status,conclusion` at the configured interval (≥60 s) until `status=completed` or the configured wall-clock timeout (≤15 min) is reached. Bound caps mirror `pull-request-merge`'s wait mode (interval default 90 s, timeout default 10 min, max retries 10, visible status line per round, failure short-circuits to `workflow-health` triage).

After the run completes (single-shot or wait mode):

- On `conclusion=success`: confirm with the operator that the release is now published (`gh release view <tag> --json isDraft` returns `{"isDraft": false}`) and that `release-cd-refresh-master.yml` has started a downstream run (`gh run list --workflow=release-cd-refresh-master.yml --limit 1`); both checks are part of `release-automation`'s acceptance criteria.
- On `conclusion=failure`: do **not** retry. Route to `workflow-health` triage — classify per `spec/project/workflow-health/`. The most common cause is a `merge_failed` from `pascalgn/automerge-action` when `release-publish.yml` itself uses `automerge-action`; check the run logs for `mergeResult: 'merge_failed'` per `pull-request-merge` step 7b and route as a stale-pin incident if so.

### Wait mode

Activated by `--wait` or unambiguous operator phrasing. Caps mirror `pull-request-merge`:

- Interval ≥ 60 s (default 90 s).
- Wall-clock timeout ≤ 15 min (default 10 min).
- Max retries ≤ 10.
- Visible status line per round.
- Failure short-circuits to `workflow-health`.

The single-shot default exists because the prompt-cache TTL is 5 min; unbounded polling burns the cache. Caps balance: short waits stay cache-warm, long waits accept one cache miss but never balloon.

### Gotchas

- `pascalgn/automerge-action` (used by some `release-publish.yml` implementations downstream) exits 0 even on `mergeResult: 'merge_failed'`. A green `release-publish.yml` run is **not** proof the publish happened. Always re-verify `gh release view <tag> --json isDraft` after a `success` conclusion.
- The `tag` input is mandatory because `release-automation` forbids the workflow's "newest wins" heuristic. Even when only one draft is open, this skill passes `-f tag=<tag>` explicitly.
- A red required check on `develop`'s tip blocks publish but is not always recoverable by re-running. The triage path is `workflow-health`, not "retry until green."
- `release-cd-refresh-master.yml` should fire automatically after `release-publish.yml` succeeds. When it doesn't fire (the known-platform-constraint case where `release: published` from `GITHUB_TOKEN` doesn't cascade to a fresh workflow run, per `workflow-health` §Known platform constraints), surface this and route to manual fast-forward of `main` per `branching-model` §Release flow.
- The skill never runs `gh release edit --draft=false` even as a fallback — that flag is reserved for incident response and remains a manual operator action documented in `release-automation` §Non-Goals.

### Hard rules

- Never dispatch when any pre-publish gate fails. Failures route to `workflow-health` triage.
- Never call `gh release edit --draft=false`, `gh api -X PATCH .../releases/<id>` with `draft=false`, or any other body that flips the draft state. The workflow is the only publish path.
- Never use a `--ref` other than the default branch (typically `develop`).
- Never poll to completion outside an explicit operator opt-in to wait mode; default behaviour is single-shot.
- Never retry a failed `release-publish.yml` run blindly. Triage classifies the failure first.
- Never proceed without explicit operator confirmation of the disclosed validation state.
- When `spec/project/release-skill-layer/` or `spec/project/release-automation/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
