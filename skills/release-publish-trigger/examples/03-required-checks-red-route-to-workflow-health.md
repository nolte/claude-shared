# Example 03 — Required check on develop tip is RED, route to workflow-health

The operator asks for a publish on `nolte/example-cli`. Exactly one
release-drafter draft is open on `develop` for tag `v2.1.0`. Gates 2a,
2b, 2c, and 2e all pass cleanly. Gate 2d ("Required status checks
SUCCESS on develop tip") fails: the required context `ci / integration`
reports `conclusion=failure` on the develop tip SHA. Per the spec the
skill MUST NOT dispatch and MUST hand the failure to `workflow-health`
triage with a classification — never retry blindly, never re-dispatch.

## Input prompt

> Ship the release.

## Input files

The active checkout is `nolte/example-cli` on branch `develop`.
Preconditions all pass: git repo, `gh auth status` OK, default branch
`develop`, both specs reachable.

`gh release list --json isDraft,tagName,targetCommitish,createdAt,name`
returns one element:

```json
[
  {
    "isDraft": true,
    "tagName": "v2.1.0",
    "targetCommitish": "develop",
    "createdAt": "2026-05-09T15:48:11Z",
    "name": "v2.1.0"
  }
]
```

`targetCommitish` resolves to SHA `c0a8b21f…` and is reachable from
`origin/develop` — Gate 2a passes.

`.github/release-automation.yml` declares one version-bearing file:

```yaml
version_bearing_files:
  - path: cmd/cli/version.go
    selector: 'const Version = "{{value}}"'
    transform: strip-leading-v
```

At the target SHA `cmd/cli/version.go` reads
`const Version = "2.1.0"` — Gate 2b passes
(`2.1.0 == v2.1.0` under the declared transform).

`git log -1 --pretty=%s --follow -- cmd/cli/version.go` returns
`chore(release): v2.1.0 (#308)` — Gate 2c passes.

`.github/settings.yml` declares three required contexts on `develop`:
`ci / lint`, `ci / unit`, `ci / integration`. The check-runs query
`gh api repos/nolte/example-cli/commits/c0a8b21f…/check-runs` returns:

```json
{
  "check_runs": [
    {"name": "ci / lint",        "conclusion": "success", "status": "completed"},
    {"name": "ci / unit",        "conclusion": "success", "status": "completed"},
    {"name": "ci / integration", "conclusion": "failure", "status": "completed",
     "html_url": "https://github.com/nolte/example-cli/actions/runs/77123456",
     "details_url": "https://github.com/nolte/example-cli/actions/runs/77123456/job/214567890"}
  ]
}
```

Inspecting the failed run logs surfaces a step error:
`error: failed to pull docker.io/library/postgres:14.5 — manifest unknown` —
a typical stale-pin pattern (the upstream tag was retracted), classified
per `spec/project/workflow-health/` as **stale pin**.

`.github/workflows/release-publish.yml` exists in the working tree.

## Expected behaviour

1. **Preconditions confirmed and single open draft resolved.** As in
   example 01.
2. **Gates 2a, 2b, 2c pass.** `merge-base` ancestry, version-bearing
   alignment under the override declared in `.github/release-automation.yml`,
   and the `chore(release): v2.1.0 (#308)` alignment commit all hold.
3. **Gate 2d fails.** The skill reads the required-context list from
   `.github/settings.yml`
   (`branches[name=develop].protection.required_status_checks.contexts`),
   queries `gh api repos/nolte/example-cli/commits/c0a8b21f…/check-runs`,
   and detects `ci / integration` with `conclusion=failure`. The
   failure detail records the failing context, its conclusion, and the
   `html_url` of the failing workflow run.
4. **Skill stops at Gate 2d.** Per the spec the skill MUST NOT proceed
   past a failed gate; Gate 2e is not evaluated. No
   `gh workflow run release-publish.yml` is issued.
5. **No retry, no re-dispatch.** The skill explicitly does **not**
   suggest "re-run the failing check" as a remediation. Per the spec a
   red required check is not always recoverable by re-running.
6. **Routed to `workflow-health` triage with classification.** The
   skill hands the failure to the `workflow-health-triage` skill with:
   the failing workflow run URL
   (`https://github.com/nolte/example-cli/actions/runs/77123456`), the
   failing context name (`ci / integration`), the develop tip SHA
   (`c0a8b21f…`), and a proposed classification (`stale pin`, derived
   from the `manifest unknown` log line on `docker.io/library/postgres:14.5`).
   The classification is proposed, not asserted — `workflow-health`
   owns the final classification per `spec/project/workflow-health/`.
7. **No flip-to-published fallback.** The skill does not call
   `gh release edit --draft=false`, does not call `gh api -X PATCH`
   on the release, and does not propose either as a workaround.
   The hard rule holds even when the gate failure is "external" to
   the publish workflow itself.
8. **No wait-mode coercion.** Wait mode is reserved for **pending**
   checks (`status=in_progress`). A `failure` conclusion is terminal
   and routes immediately to triage; the skill does not offer to wait.
9. **Hard rules honoured.** No dispatch on a failed gate, no
   `--ref` other than `develop`, no `gh release edit --draft=false`,
   no blind retry. The skill ends by handing control to
   `workflow-health-triage` with the artefacts above; the operator
   re-invokes `release-publish-trigger` only after the develop tip is
   green again.
