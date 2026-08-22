# Close-out: artifact removal, the pull request, and the report back

Operation 6 carries the rules and the order. This file carries the reasoning and the
exact contracts, so the body doesn't have to.

## 1. Remove the pre-analysis artifact

With every package implemented and the gate green:

```bash
git rm .audits/issue-orchestrate/<n>/analysis.md
```

Commit the removal on the feature branch as a **fix-forward**.

The artifact is run-scoped per `spec/project/issue-orchestration/` §Pre-analysis
artifact lifecycle. The branch's commit trail keeps it readable for the reviewer, the
squashed merge carries none of it onto `develop`, and the durable trail is the pull
request's notes plus the issue comment. **Move any fact worth keeping into those
first** — after the removal commit, the artifact survives only in the branch history.

Two things that look like shortcuts and aren't:

- **Never `.gitignore` the path instead.** That leaves the artifact untracked and
  invisible to the reviewer rather than removed, and the next run's `git status` is
  noisy for reasons nobody remembers.
- **Never remove the requirement artefact** under `project/requirements/`. It's
  durable by design and outlives the run; the spec requires it to still be on the
  default branch after the merge.

## 2. Open the pull request

Via `pull-request-create`, so the operator confirms title and body under that skill's
externally-visible-action gate. The pull request must carry:

- **the issue linked** — `Closes #<n>`, or the repository's configured linking
  keyword. (In this repository the keyword doesn't autoclose; close the issue by hand
  after the merge.)
- **a `Risk / rollout notes` section** per `pull-request-workflow`, carrying three
  things: the issue reference, the issue classification **verbatim**, and — per work
  package — the dispatched specialist as its `subagent_type` literal, or the explicit
  `no matching specialised agent — generalist remediation` note.

The per-package line is what makes the run auditable after the fact. A reader must be
able to tell which specialist produced which part of the diff without replaying the
transcript.

## 3. Post the summary back to the issue

When the operator confirms: the classification, the package count, and the route
taken. This is the half of the durable trail that lives outside the repository, and
it's what a later reader finds first.

## Report-back

The orchestration stops at an open, audit-trailed pull request. **The merge belongs to
`pull-request-merge`**, which re-validates the gate.

Report: the issue number, the classification, the route taken, the dispatched
specialists, the artifact path, the pull request URL, and the one-line next action —
`next action: invoke pull-request-merge after CI is green`.
