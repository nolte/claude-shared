# Example 01 — fix PR on a feature branch with autolinked spec/skill paths

A small, well-scoped bugfix on a `fix/`-prefixed branch that already
contains the current `develop` tip. Exercises the smallest happy path:
preconditions pass, branch is fresh, the diff touches one skill folder
plus its governing spec, and the skill drafts a draft PR with both
`Refs spec/<path>` and `Refs skills/<name>` autolinks emitted into
**Linked issues**.

## Input prompt

> Open a draft PR for this branch.

## Input files

Current branch: `fix/skill-pr-create-empty-summary-guard`. The remote
default integration branch is `develop`. `gh auth status` reports a
healthy authentication, the remote resolves to a GitHub repository,
and `git status --porcelain` is empty.

`git log --oneline origin/develop..HEAD`:

```

a1b2c3d fix(pull-request-create): refuse empty Summary section
e4f5g6h test(pull-request-create): cover empty-Summary refusal

```

`git diff --name-only origin/develop...HEAD`:

```

skills/pull-request-create/SKILL.md
spec/project/pull-request-workflow/en.md
spec/project/pull-request-workflow/de.md

```

`git merge-base --is-ancestor origin/develop HEAD` exits `0` (branch
is fresh). The repository ships a `Taskfile.yml` with a `lint` target.
No open PR exists for this branch yet.

## Expected behaviour

1. **Preconditions pass.** The skill confirms cwd is inside a git
   repo, `origin/develop` resolves on the remote, `gh auth status` is
   green, and the current branch (`fix/skill-pr-create-empty-summary-guard`)
   starts with one of the allowed prefixes (`fix/`).
2. **Change context collected in parallel:** `git status --porcelain`,
   `git fetch origin develop`, `git log --oneline origin/develop..HEAD`,
   `git diff --name-only origin/develop...HEAD`, and a sampled
   `git diff origin/develop...HEAD`. The working tree is clean, so the
   skill proceeds without prompting for stash/commit/abort.
3. **Branch freshness verified.** `git merge-base --is-ancestor
   origin/develop HEAD` exits `0`; no rebase or merge is required and
   no force-push prompt is shown.
4. **Title derived from the `fix/` prefix.** Conventional-Commits type
   `fix`, scope `pull-request-create` (well-known skill area), summary
   imperative and ~70 chars:
   `fix(pull-request-create): refuse empty Summary section in PR body`.
5. **Body composed with all five required sections in order.**
   - **Summary** — one to three sentences stating the empty-Summary
     refusal closes a footgun in the PR-drafting flow.
   - **Changes** — imperative bullets ("Add empty-Summary guard",
     "Cover refusal path with test").
   - **Linked issues** — autolinked **both** the touched spec topic
     and the touched skill, deduplicated by `<area>/<slug>/`:

     ```

     Refs spec/project/pull-request-workflow/
     Refs skills/pull-request-create/

     ```

     No `Closes #N` since the operator did not name a tracking issue.
   - **Testing** — names the command run (`task test -- pull-request-create`)
     and the manual smoke step.
   - **Risk / rollout notes** — `None` (allowed literal for this section).
6. **Title and body presented for approval.** The skill renders the
   draft inline and waits. The operator approves verbatim.
7. **Pre-push lint executed.** Because the repository ships a
   `Taskfile.yml` with a `lint` target, the skill runs `task lint`
   before any push. It exits clean.
8. **Push and create.** Branch has no upstream, so the skill runs
   `git push -u origin HEAD`, then `gh pr create --base develop --draft
   --title "<title>" --body "$(cat <<'EOF' … EOF)"` with the body passed
   via HEREDOC so formatting is preserved. Draft mode is the default
   because CI hasn't yet run on the branch.
9. **PR URL reported back** in the operator's language; the skill
   reminds them they can flip draft → ready once the first CI pass is
   green, and that promotion to merge is owned by `pull-request-merge`,
   not by this skill.
