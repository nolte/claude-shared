# Example 02 — feat PR with a spec touch, Risk/rollout enforced

A `feat/`-prefixed branch whose diff touches a spec topic for the
first time and introduces a user-visible behaviour change. Exercises
the spec-autolink path (one `Refs spec/<area>/<slug>/` line per
touched topic, deduplicated) and the **Risk / rollout notes**
enforcement: when the change has rollout implications, the skill
refuses to accept the literal `None` and pushes back until the
operator supplies a real risk paragraph.

## Input prompt

> Push this branch and open a PR.

## Input files

Current branch: `feat/release-skill-layer-publish-trigger`. The remote
default integration branch is `develop`. `gh auth status` is healthy,
`git status --porcelain` is empty, and the branch already has an
upstream (`origin/feat/release-skill-layer-publish-trigger`) from an
earlier WIP push.

`git log --oneline origin/develop..HEAD`:

```

9988aa1 feat(release-skill-layer): add release-publish-trigger skill scaffold
77ee22b feat(release-skill-layer): wire publish-trigger into plugin manifest
55cc33d docs(release-skill-layer): add EN+DE spec for the publish-trigger skill

```

`git diff --name-only origin/develop...HEAD`:

```

skills/release-publish-trigger/SKILL.md
.claude-plugin/plugin.json
spec/project/release-skill-layer/en.md
spec/project/release-skill-layer/de.md

```

`git merge-base --is-ancestor origin/develop HEAD` exits `0`. The
repository ships a `Taskfile.yml` with a `lint` target and a
`.pre-commit-config.yaml`. No open PR exists for this branch.

## Expected behaviour

1. **Preconditions pass.** `feat/` prefix is allowed, `develop` exists
   on the remote, `gh` is authenticated, working tree is clean.
2. **Change context collected in parallel** as in Example 01. The
   diff is large but sampled enough to identify three distinct
   touched areas: a new skill, the plugin manifest, and a spec topic.
3. **Branch freshness verified.** `git merge-base --is-ancestor
   origin/develop HEAD` exits `0`; no sync needed.
4. **Title derived from the `feat/` prefix.** Conventional-Commits
   type `feat`, scope `release-skill-layer`, imperative summary
   under ~70 chars:
   `feat(release-skill-layer): add release-publish-trigger skill`.
5. **Body composed with all five required sections.**
   - **Summary** — two sentences naming the new skill and the
     pre-publish gate it enforces.
   - **Changes** — imperative bullets covering the new skill, the
     plugin-manifest registration, and the spec authorship.
   - **Linked issues** — exactly one `Refs spec/<area>/<slug>/` line
     per touched spec topic (deduplicated by area/slug, **not** by
     filename — `en.md` and `de.md` collapse to a single entry):

     ```

     Refs spec/project/release-skill-layer/

     ```

     No `Closes #N` since the operator did not name a tracking issue.
   - **Testing** — names `task test -- release-publish-trigger`, the
     plugin-manifest validation command, and the manual `gh workflow
     run --dry-run` smoke check the operator performed.
   - **Risk / rollout notes** — the operator's first draft tries to
     leave this `None`. The skill **refuses**: a `feat/` change that
     dispatches a release workflow has rollout implications by
     construction. The skill cites the spec rule and asks for a real
     paragraph. The operator supplies one ("First-time activation of
     a workflow-dispatch path; rollback is `gh workflow disable
     release-publish.yml`; no data migration; staged behind operator
     opt-in per the spec"). The skill accepts and re-renders the
     body.
6. **Title and body presented for approval.** The skill iterates with
   the operator; once approved, it proceeds.
7. **Pre-push lint executed.** Both `Taskfile.yml`'s `lint` target
   and `.pre-commit-config.yaml` are present, so the skill runs
   `task lint`. It exits clean.
8. **Push and create.** Branch already has an upstream and the local
   tip is ahead of `origin` only by one commit (no rewrite), so a
   plain `git push` suffices — no `--force-with-lease` prompt. Then
   `gh pr create --base develop --draft --title "<title>" --body
   "$(cat <<'EOF' … EOF)"` runs with the body passed via HEREDOC.
9. **PR URL reported back** in the operator's language; the skill
   notes that draft mode is intentional until CI is green, and that
   merge promotion is `pull-request-merge`'s job.
