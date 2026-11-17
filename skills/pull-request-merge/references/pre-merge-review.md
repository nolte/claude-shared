# Pre-merge review

Read when running step 2: choosing the review lanes, briefing the read-only agent, or confirming a review that already ran on the branch. `issue-orchestrate` and `issue-batch-orchestrate` read it for the review they run before a PR exists.

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
| (a) built-in `code-review` | a PR exists and the session cwd is a checkout of the PR's repository | the PR number |
| (b) independent read-only review agent | always available; required when the session cwd isn't the branch's worktree | the worktree path plus `git -C <worktree> diff origin/develop...HEAD` |
| security: read-only review agent briefed for security | the diff touches a security-sensitive path | the worktree path plus the same range |
| security: built-in `security-review` | only when the session cwd is that worktree | none: it reads the cwd |

`security-review` takes no target at all: it composes its diff from fixed `git ... origin/HEAD...` substitutions with no path argument, so it reads **this session's** working directory. Run from the primary checkout while the branch lives in a worktree, it reviews an empty diff and reports clean. `code-review` takes a PR number as its target, but resolves it against the cwd's repository (see the lane (a) gotcha below).

**Which lanes apply where.** Before a PR exists (`issue-orchestrate` operation 6, `issue-batch-orchestrate` operation 5) there's no PR number for lane (a): only lane (b) and, for a security-sensitive diff, the security-briefed read-only agent apply; `security-review` adds to them only from a session rooted in the worktree. At `pull-request-merge` step 2 both (a) and (b) run, and (b) is mandatory when the session cwd isn't the branch's worktree.

**Lane (a) gotcha.** `code-review <PR#>` resolves the number against the cwd's repository, so a number that exists there but belongs to another repository yields a confident review of unrelated code; check the reported repository and file list against `--stat`. It can also leave a checked-out `pr-<N>` branch or a `refs/remotes/pr/<N>` ref in the shared repository, which the feature-branch guard doesn't catch. Afterwards check the primary checkout's `HEAD` (`git -C <primary> rev-parse --abbrev-ref HEAD` must print `develop`; switch back if not), then delete the leftover with `git -C <primary> branch -D pr-<N>` or `git -C <primary> update-ref -d refs/remotes/pr/<N>`. `issue-orchestrate`'s `references/gotchas.md` records the observed failure shapes.

Security-sensitive paths: `.github/workflows/`, `.github/settings.yml`, `**/*.sh`, files that contain `secret` / `token` / `password` references, and auth or signing code.

## Briefing the read-only agent

Give the agent, verbatim:

- the absolute worktree path and the range `git -C <worktree> diff origin/develop...HEAD`;
- the head commit SHA (`git -C <worktree> rev-parse HEAD`) and the `--stat` file list, so its report can be checked against them;
- the instruction to stay read-only (no edits, no git mutations) and to return findings as blocking or non-blocking, each with `file:line`.

For the security lane, add the security brief: the security-sensitive path list above, OWASP-style checks (injection, access control, SSRF), secrets in code or logs, auth and signing code, workflow `permissions:` and untrusted input reaching `run:` steps or shell commands.

The `code-security-reviewer` agent (plugin `nolte-engineering`) is a whole-codebase OWASP audit, the option for a pre-release audit; it isn't the per-PR lane.

## Confirming a review that already ran

`issue-orchestrate` and `issue-batch-orchestrate` review the branch before the PR opens or, as a lane, before they return `committed-locally`, and record the reviewed head SHA, its `--stat` file list, the lanes, and the findings in the PR's **Risk / rollout notes** (as a lane: in the returned payload). Step 2 then confirms that review instead of starting from zero:

1. The recorded head SHA equals the PR's head commit, or it's an ancestor of it (`git -C <worktree> merge-base --is-ancestor <reviewed-sha> HEAD` exits 0) and every entry of `git -C <worktree> diff --name-status <reviewed-sha> HEAD` is a deletion (`D`) under `.audits/`; and the recorded file list, minus those artifacts, equals the current `--stat` output.
2. Every blocking finding it raised is resolved in the diff or explicitly overridden by the user.
3. If the security-sensitive condition applies and no security lane ran, run that lane now over the current range.

Any other mismatch (the reviewed SHA isn't an ancestor of the head, as after a rebase; a commit after it that isn't an `.audits/` deletion; a different file list) means the prior review doesn't cover the diff: run the lanes again over the current range.

## Failed gate

A clean result over an empty diff, or over a file list that doesn't match `--stat`, is a failed gate rather than a pass, per `spec/project/issue-orchestration/` §Verification and traceability. Re-run the lane from a working copy that holds the branch, or switch to lane (b).
