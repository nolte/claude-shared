# Pre-merge review

Read when running step 2: choosing the review lanes, briefing the read-only agent, or confirming a review that already ran on the same head commit.

## The gate is a diff, not a skill name

The review covers the branch's real diff against `develop`:

```sh
git -C <worktree> diff origin/develop...HEAD
git -C <worktree> diff --stat origin/develop...HEAD
```

`<worktree>` is the working copy that holds the branch, which is often a linked worktree rather than the session's working directory. Naming the gate by the diff keeps it valid when built-in skill names drift (a `review` skill no longer exists; the built-in is `code-review`) and when the session runs somewhere other than the branch.

## Lanes

| Lane | When | Target |
|---|---|---|
| (a) built-in `code-review` | from a working copy that holds the branch | the PR number |
| (b) independent read-only review agent | always available; required when the session cwd isn't the branch's worktree | the worktree path plus `git -C <worktree> diff origin/develop...HEAD` |
| security: read-only review agent briefed for security | the diff touches a security-sensitive path | the worktree path plus the same range |
| security: built-in `security-review` | only when the session cwd is that worktree | none: it reads the cwd |

The built-ins compose their diff from fixed `git ... origin/HEAD...` substitutions with no path argument, so they read **this session's** working directory. `security-review` takes no target at all: run from the primary checkout while the branch lives in a worktree, it reviews an empty diff and reports clean.

Security-sensitive paths: `.github/workflows/`, `.github/settings.yml`, `**/*.sh`, files that contain `secret` / `token` / `password` references, and auth or signing code.

## Briefing the read-only agent

Give the agent, verbatim:

- the absolute worktree path and the range `git -C <worktree> diff origin/develop...HEAD`;
- the head commit SHA (`git -C <worktree> rev-parse HEAD`) and the `--stat` file list, so its report can be checked against them;
- the instruction to stay read-only (no edits, no git mutations) and to return findings as blocking or non-blocking, each with `file:line`.

For the security lane, add the security brief: the security-sensitive path list above, OWASP-style checks (injection, access control, SSRF), secrets in code or logs, auth and signing code, workflow `permissions:` and untrusted input reaching `run:` steps or shell commands.

The `code-security-reviewer` agent (plugin `nolte-engineering`) is a whole-codebase OWASP audit, the option for a pre-release audit; it isn't the per-PR lane.

## Confirming a review that already ran

A lane run (for example `issue-orchestrate` before it returns `committed-locally`) may already have reviewed the branch. Step 2 then confirms that review instead of starting from zero:

1. The recorded head SHA equals the PR's head commit, and the recorded file list equals the current `--stat` output.
2. Every blocking finding it raised is resolved in the diff or explicitly overridden by the user.
3. If the PR's head commit is still the reviewed one but the security-sensitive condition applies and no security lane ran, run that lane now.

Any mismatch (a new commit, a rebase, a different file list) means the prior review doesn't cover the diff: run the lanes again over the current range.

## Failed gate

A clean result over an empty diff, or over a file list that doesn't match `--stat`, is a failed gate rather than a pass, per `spec/project/issue-orchestration/` §Verification and traceability. Re-run the lane from a working copy that holds the branch, or switch to lane (b).
