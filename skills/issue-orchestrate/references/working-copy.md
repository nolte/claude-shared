# Working copy: creation fallback and the ignore gate

The SKILL.md precondition carries the rule. This file carries the two commands a
repository outside the reference layout needs, and what to do when either one fails.

## 1. Create the worktree

Probe for the reference helper from the primary checkout:

```bash
task --summary worktree:add >/dev/null 2>&1
```

Exit 0 means the target exists: run `task worktree:add -- <branch> <slug>`, which
fetches, branches off `origin/develop`, and seeds `.resume/<slug>/plan.md`.

Any other exit (no Taskfile, no such target, or a Taskfile the shell refuses to load)
means the fallback. Run the form `spec/project/parallel-working-copies/` §Lifecycle:
Create mandates, at the location §Path layout names:

```bash
repo="$(basename "$(git remote get-url origin)" .git)"
git fetch origin develop
git worktree add -b <branch> "${NOLTE_WORKTREE_ROOT:-$HOME/repos/.worktrees}/$repo/<slug>" origin/develop
```

Write `$HOME`, not `~`: a tilde inside double quotes isn't expanded. The fallback seeds
no plan stub, so write `.resume/<slug>/plan.md` yourself when the run needs one.

**Record the fallback.** Note it in the pre-analysis artifact's `Working copy` line
(`fallback: git worktree add, no worktree:add target`) so the reviewer and a later run
see why the creation path differs. A run that used the helper records `task worktree:add`.

## 2. The ignore gate, before the artifact is written

A repository **MUST NOT** ignore the path this skill writes its transient artifact to.
Before operation 3 writes it, run inside the worktree:

```bash
git check-ignore -q .audits/issue-orchestrate/<n>/analysis.md
```

- **Exit 1**: not ignored. Write the artifact and proceed.
- **Exit 0**: ignored. **Stop.** Get the matching entry with
  `git check-ignore -v .audits/issue-orchestrate/<n>/analysis.md`
  (it prints `<source>:<line>:<pattern>`) and report it to the operator as `.gitignore`
  drift, naming `project-structure-apply` as the repair path. Never `git add -f` the
  artifact, and never continue with it untracked: either way the plan gate the
  artifact carries is hollowed out.
- **Exit 128**: the check itself failed. Treat it like exit 0 and report the error.

Probe the full file path, not the directory: `git check-ignore` matches a path that
doesn't exist yet, and the file path is what `git add` would refuse.

The remedy for a broad entry is narrowing it, not a negation alone. A directory
pattern such as `/.audits/` excludes the directory itself, and git can't re-include a
path under an excluded directory, so `!/.audits/issue-orchestrate/` after it has no
effect. A content pattern (`/.audits/*`) followed by the negation does work, and so
does replacing the broad entry with the dated paths the repository really means to keep
local (this repository ignores `.audits/2026-Q*/` only).
