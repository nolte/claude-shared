# Verification scoping: why a clean security report can mean nothing

Read this before running `security-review` or `code-review` in operation 6.
`spec/project/issue-orchestration/` §Verification and traceability owns the rules;
this file carries the mechanism and the commands.

## The mechanism

Both harness built-ins are prompt templates that compose their own change set from
four fixed shell substitutions:

```
GIT STATUS:      !`git status`
FILES MODIFIED:  !`git diff --name-only origin/HEAD...`
COMMITS:         !`git log --no-decorate origin/HEAD...`
DIFF CONTENT:    !`git diff origin/HEAD...`
```

None of them carries a `-C`, and the template holds no argument placeholder at all.
They resolve against the **session's** working directory, and no invocation form
redirects them. Passing the worktree path doesn't work, and neither does `--repo`.

## Why that collides with this skill

§Working-copy isolation puts every write in a worktree and keeps the session in the
primary checkout on a clean `develop`. All four substitutions therefore return empty,
and the built-in reports "no findings" having read nothing. That report is
indistinguishable from a real pass.

The second failure shape is worse and is recorded in `gotchas.md`: a bare `PR #N` that
happens to exist in the session's repository yields a confident review of unrelated
code, complete with plausible `file:line` findings.

## What to do

Capture the change set yourself, first:

```bash
git -C <worktree> diff --stat origin/develop...HEAD
```

- **Empty capture over a branch that carries commits: the gate failed.** Don't record
  a pass. Re-run the verification from a session rooted inside the worktree.
- **Non-empty capture:** compare the file list against what the built-in reports. If
  they disagree, the built-in read something else; its verdict says nothing about
  this change.
- Record the capture next to the verification outcome in the pre-analysis artifact and
  the pull request's **Risk / rollout notes**, so a later reader can tell which diff
  was actually reviewed.

## Base-ref caveat

The built-in diffs against `origin/HEAD`, which is a clone-time local ref rather than
the repository's integration branch. Where the two differ (a repo whose default is
`main` while `develop` integrates), the diff is inflated rather than empty. The same
`git -C <worktree> diff --stat origin/develop...HEAD` capture is what surfaces it.

## When `code-security-reviewer` is unavailable

It ships in `nolte-engineering`. A session without that plugin can't dispatch it.
Record the gap in the artifact and the PR notes; don't let the built-in
`security-review` stand in for it. Surface scoping and diff verification are
complementary, not interchangeable.
