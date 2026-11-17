# Working copy: creation fallback and the ignore gate

The SKILL.md precondition carries the rule. This file carries the commands a
repository outside the reference layout needs, and what to do when one of them fails.

## 1. Create the worktree

**Detect the helper from the repository root, pinned to its own Taskfile.** `task`
searches parent directories for a Taskfile, and `--dir` doesn't stop that, so a bare
`task --summary worktree:add` can succeed on a Taskfile above the repository and run a
foreign target. Pin the file explicitly:

```bash
root="$(git rev-parse --show-toplevel)"
tf=""; for f in Taskfile.yml Taskfile.yaml taskfile.yml taskfile.yaml; do
  [ -f "$root/$f" ] && { tf="$root/$f"; break; }; done
if [ -n "$tf" ]; then task --taskfile "$tf" --summary worktree:add >/dev/null 2>&1; echo "detect=$?"; else echo "detect=no-taskfile"; fi
```

- `detect=0`: the target exists. Run `task --taskfile "$tf" worktree:add -- <branch> <slug>`,
  which fetches, branches off `origin/develop`, and seeds `.resume/<slug>/plan.md`.
- Anything else (`no-taskfile`, `200` no such target, `104` a Taskfile the shell
  refuses to load, any other code): use the fallback below.

**The fallback** is the form `spec/project/parallel-working-copies/` §Lifecycle: Create
mandates, at the location §Path layout names:

```bash
repo="$(basename "$(git remote get-url origin)" .git)"
git fetch origin develop
git worktree add -b <branch> "${NOLTE_WORKTREE_ROOT:-$HOME/repos/.worktrees}/$repo/<slug>" origin/develop
```

Write `$HOME`, not `~`: a tilde inside double quotes isn't expanded. The fallback seeds
no plan stub, so write `.resume/<slug>/plan.md` yourself when the run needs one.

**When `task worktree:add` itself fails** after `detect=0`, don't retry blindly; the
helper may have stopped after creating something. Check first:

```bash
git worktree list --porcelain | grep -Fx "worktree <dest>"
git show-ref --verify --quiet refs/heads/<branch>; echo "branch=$?"
```

- Neither the worktree nor the branch exists: take the fallback.
- The worktree exists on `<branch>`: use it, and seed the plan yourself if the helper
  stopped before writing it.
- The branch exists without a worktree, or the worktree sits on another branch: stop
  and report. Never delete the branch or the directory to make room for a retry.

**Record it.** The pre-analysis artifact's `Working copy` line names the path, the
detection result (`detect=<code>`), and the creation path (`task worktree:add` or the
`git worktree add -b` fallback), so the reviewer and a later run see why it differs.

## 2. The ignore gate, before the artifact is written

A repository **MUST NOT** ignore the path this skill writes its transient artifact to.
Before operation 3 writes it, run inside the worktree:

```bash
git check-ignore -q .audits/issue-orchestrate/<n>/analysis.md; echo "ignored=$?"
```

The `-q` exit code is the verdict; it matched `git add` in every measured case,
including paths that don't exist yet.

- **`ignored=1`**: not ignored. Write the artifact and proceed.
- **`ignored=0`**: ignored. **Stop.** Never `git add -f` the artifact, and never
  continue with it untracked: either way the plan gate it carries is hollowed out.
- **`ignored=128`**: the check itself failed. Stop and report the error.

On `ignored=0`, find the entry with
`git check-ignore -v .audits/issue-orchestrate/<n>/analysis.md`. It prints
`<source>:<line>:<pattern>`. Don't read its exit code as the verdict: `-v` also prints
a matching `!` negation and exits 0 then. Route by the source:

- **The repository's `.gitignore`** (`.gitignore` or a nested `.../.gitignore`): report
  it to the operator as `.gitignore` drift and name `project-structure-apply` as the
  repair path.
- **`.git/info/exclude`** or **the global excludes file** (`core.excludesFile`, by
  default `~/.config/git/ignore`): report it to the operator as a local setting, not
  repository drift. A `!` line in the repository can't re-include a path under a
  directory those files exclude, so `project-structure-apply` can't fix it.

**Narrowing a repository entry.** Git never re-includes a path under an excluded
directory, so the negation has to reach the directory itself:

- `/.audits/` or `/.audits`: no negation helps. Replace the entry with the dated paths
  the repository means to keep local, such as `.audits/2026-Q*/`.
- `/.audits/*`: add `!/.audits/issue-orchestrate/`. Negating only the contents
  (`!/.audits/issue-orchestrate/**`) leaves the directory excluded.
- `/.audits/**`: add both `!/.audits/issue-orchestrate/` and
  `!/.audits/issue-orchestrate/**`; either alone leaves the file ignored.

Re-run the `-q` probe afterwards and record `ignored=1`.
