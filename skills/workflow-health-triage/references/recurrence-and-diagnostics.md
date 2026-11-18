# Recurrence, first red vs last green, and side-effect-free diagnostics

Read at operation 1 (first red vs last green), at operation 2 (recurrence check before the `flake` row), and at operation 3 (diagnostics clause in the dispatch brief). Implements `spec/project/workflow-health/` §Triage before remediation and §Flake handling.

## First red vs last green

Before the `defect` row attributes the failure to the change under review, find out what else changed between the last green run and the first red one of the same workflow on the same branch:

1. `gh run list --workflow <wf> --branch <branch> --limit 50 --json conclusion,headSha,databaseId,createdAt` — walk back from the run under triage to the most recent `success`; the run right after it is the first red.
2. `git log --oneline <last-green-sha>..<first-red-sha>` — the commits in between. A single commit narrows the window; several commits widen it.
3. Diff what the workflow consumes besides the repository code. Compare the two runs' logs (`gh run view <id> --log`) for:
   - **Base-image or container digest:** `FROM` lines, `image:` keys, pulled `sha256:` digests. A floating tag such as `:latest` or `:stable` can change with no commit at all.
   - **Pinned action or reusable workflow:** each `uses:` ref, and the resolved SHA the runner logs under "Download action repository".
   - **Dependency bump:** lockfile changes in the commit range, Renovate merges, or a resolver log line that picks a newer version.
   - **Runner image:** the "Runner Image" version in the "Set up job" step.

When the first red run's head commit is older than the change under review, or something in the list above changed between the two runs, the change under review isn't the first suspect. Record both run IDs and what changed between them in the classification note, whatever class it settles on; a `defect` carries them into the fix PR's Risk / rollout notes.

## Recurrence check

A failure whose message recurs is not a `flake`, even when a single re-run of the same `headSha` came back green. Check before you take the `flake` row:

1. `gh run list --workflow <wf> --limit 30 --json conclusion,headSha,headBranch,databaseId` — the recent runs of the same workflow, across branches.
2. For every failed run in that list, `gh run view <databaseId> --log-failed` and compare the failing step and its message with the run under triage. Normalise run-specific noise (timestamps, run IDs, temporary paths) before comparing.
3. The failure **recurs** when the same failing step fails with the same message on two or more runs, or on `develop` and on a pull-request branch alike.

A recurring failure is classified `defect` until a measurement shows otherwise. A measurement is evidence that names the cause outside the repository: for example a status incident covering every recurrence (`infra`), or an expired credential (`secret drift`). A green re-run is not such a measurement; it shows only that the failure is intermittent, not that it's harmless.

## Side-effect-free diagnostics

Diagnostics added to find a cause **MUST NOT** change the state they observe. A probe that alters the system can turn a red run green and hide the defect. The dispatch brief for any lane that adds logging, probes, or debug steps carries this clause:

> Diagnostics you add to locate the cause must be side-effect free. Read state; don't trigger it. Read `/proc/self/mountinfo` or `/proc/<pid>/mountinfo` instead of running `findmnt`, `ls`, or `stat` on a path an automount would mount. Don't restart services, don't re-trigger units or timers, don't warm caches, and don't create files in the paths under test. If a diagnostic can't be made side-effect free, say so in your report and keep it out of the run that decides the classification.

Typical traps:

- Touching an automount point (`findmnt /boot`, `ls /boot`) mounts it, so an idle-unmount defect disappears in the diagnostic run.
- `systemctl restart` or `systemctl start` on a unit to "check it works" resets the state that failed.
- A `curl` probe against a service with lazy initialisation warms it up before the test's first request.
- `sleep` added to "give it time" changes the timing a race depends on.
