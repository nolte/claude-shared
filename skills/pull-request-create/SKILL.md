---
name: pull-request-create
description: Create a GitHub pull request that conforms to the repository's pull-request-workflow spec. Invoke when the user asks to open a PR, create a pull request, draft a PR description, create a merge request, or push the branch and open a PR. Also handles equivalent German-language requests. Verifies the feature branch is synchronized with develop, composes a Conventional-Commits title and the five-section body (Summary, Changes, Linked issues, Testing, Risk / rollout notes), autolinks any touched spec files under spec/, confirms with the user, and runs the GitHub CLI PR creation command.
tags: [pull-request]
---

# Pull Request Create

Creates a GitHub pull request that conforms to `spec/project/pull-request-workflow/<canonical_language>.md` when that spec is present in the current project. If the spec is absent, the rules embedded in this skill still apply as the baseline.

## Why this is a skill, not an agent

- **Externally-visible action requires explicit confirmation** — `gh pr create` opens a PR that other humans see; the spec mandates presenting the title and body to the user and iterating until approval before invoking it. That gate is core to the contract.
- **Mid-flow interactivity** — branch-freshness resolution (rebase vs merge), force-push confirmation, and the title/body iteration are per-step user dialogues an agent's structured-report shape can't carry.
- **Output flows back into the main conversation** — the diffed PR body, the touched-spec autolinks, and the resulting PR URL all live in the user's working context; isolating them behind an agent boundary would obscure the iterative drafting.
- Counter-dimension considered: a narrower agent could sharpen Conventional-Commits-title generation, but the load-bearing dimension here is the externally-visible-action gating, not title-prose quality — skill wins.

## User-language policy

Detect the user's language and respond in it. The PR title and body, commit messages, and `gh` invocations are always written in English regardless of the user's language, so that `develop`'s history and release-drafter output stay consistent across the portfolio.

## Preconditions

Before running any git or `gh` command, confirm:

- Current working directory is inside a git repository.
- A default / integration branch named `develop` exists on the remote (`git ls-remote --heads origin develop`). If the repo still uses `main` as the integration branch, stop and report—this skill targets the branching-model spec's `develop` convention.
- `gh` is authenticated (`gh auth status`) and the remote resolves to a GitHub repository.
- The current branch **isn't** `develop` or `main`, and its name starts with one of the allowed prefixes: `feat/`, `fix/`, `chore/`, `docs/`, `exp/`. Otherwise stop and ask the user to rename or switch branches.

## Operations

### 1. Collect change context

Run these in parallel to understand what the PR covers—never skip this step, since the PR body depends on it:

- `git status --porcelain`: detect uncommitted changes.
- `git fetch origin develop`: refresh the local view of the integration branch.
- `git log --oneline origin/develop..HEAD`: list commits that will be part of the PR.
- `git diff --name-only origin/develop...HEAD`: list files touched.
- `git diff origin/develop...HEAD`: inspect the actual change (may be large; sample if needed).

If `git status` shows uncommitted changes, stop and ask the user whether to commit, stash, or abort. Never create a PR with a dirty working tree.

### 2. Ensure branch freshness (spec: "Branch freshness")

The feature branch **MUST** contain every commit of the current `develop` tip before the PR is opened. Check with:

```
git merge-base --is-ancestor origin/develop HEAD
```

If the command exits non-zero, `develop` **isn't** fully contained in the feature branch. In that case:

1. Report the lag to the user: number of commits the branch is behind (`git rev-list --count HEAD..origin/develop`).
2. Ask the user whether to synchronize via **merge** or **rebase**: the spec permits either; the default recommendation is:
   - **rebase** when the branch is local-only or hasn't yet been pushed (clean history).
   - **merge** when the branch has already been pushed and potentially reviewed (preserves review anchors).
3. Execute the chosen operation (`git merge origin/develop` or `git rebase origin/develop`). If conflicts arise, stop and hand control back to the user—don't attempt automatic resolution.
4. After a successful sync, re-run `git merge-base --is-ancestor origin/develop HEAD` to verify; only then continue.

If the branch has already been pushed, a rebase will require `git push --force-with-lease`. Confirm explicitly with the user before force-pushing, and **never** use plain `--force`. If the branch is visible through an **open non-draft PR**, the pull-request-workflow spec §Fix-forward on red checks requires that the rebase force-push be documented in a PR comment; post a short comment naming the lag that was resolved and the new head commit SHA after the force-push completes.

### 3. Build the PR title

Derive the Conventional-Commits type from the branch prefix (`feat/` → `feat`, `fix/` → `fix`, `chore/` → `chore`, `docs/` → `docs`, `exp/` → `exp`). No aliasing is permitted.

Format: `<type>(<scope>)?: <summary>`

- `<scope>` is optional. Prefer a scope when the change is confined to a well-known area (`auth`, `docs`, `ci`, etc.); omit it otherwise.
- `<summary>` is imperative, lowercased where natural (`add …`, `fix …`, `update …`), and fits within ~70 characters.

### 4. Build the PR body

Render exactly these five sections, in this order, with these exact headings:

```
## Summary

<one to three sentences stating what the PR changes and why>

## Changes

- <user-visible or reviewer-relevant change>
- <…>

## Linked issues

<Closes #N / Refs #N entries, or the literal text `None`>

## Testing

- <command(s) run, manual steps, screenshots>

## Risk / rollout notes

<risk class, migrations, feature flags, or the literal text `None`>
```

Rules for the body:

- Never remove a section, even when empty. Only **Linked issues** and **Risk / rollout notes** may contain the literal text `None`.
- **Summary**, **Changes**, and **Testing** must not be empty and must not contain only `None`: if the user can't fill them in, stop and ask.
- Use imperative mood in Summary and Changes (`Add …`, not `Added …`).
- If the diff touches any file under `spec/`, append a `Refs spec/<path>` line in **Linked issues** for each touched spec topic (deduplicated by `<area>/<slug>/`), unless the user explicitly declines.
- Repository-specific sections **may** be appended *after* the five required sections, never interleaved.

Derive section content from the commit log, file list, and diff collected in step 1. Present the drafted title and body back to the user and iterate until they approve.

### 5. Verify local lint before push

Before invoking any `git push` in the next step, run the repository's local lint target so prose-, format-, or YAML-level failures are caught locally rather than by the CI `lint` job. This is a **MUST** per `spec/project/pull-request-workflow/<canonical_language>.md` §Pre-push verification whenever the repository ships a `Taskfile.yml` with a `lint` target **or** a `.pre-commit-config.yaml`.

```
task lint
```

If neither tool is present, fall back to whatever equivalent linting the repository provides. Don't intentionally push a commit that's known to fail locally and rely on CI to report it.

### 6. Push and create the PR

Once the title and body are approved, and only then:

1. If the branch has no upstream, push with `git push -u origin HEAD`. If force-push is required after a rebase, use `git push --force-with-lease` and confirm first.
2. Create the PR with `gh pr create`, passing the title and body via a HEREDOC so formatting is preserved:

   ```
   gh pr create --base develop --title "<title>" --body "$(cat <<'EOF'
   <body>
   EOF
   )"
   ```

3. Default to `--draft` when the branch hasn't yet been reviewed or when CI hasn't yet run; the user can flip it to ready once the first CI pass is green. The spec says draft is `SHOULD` while work is ongoing.
4. After `gh pr create` succeeds, report the PR URL back to the user.

If `gh pr create` fails because a PR already exists for this branch, switch to `gh pr edit` to update the existing PR's title and body instead of creating a new one.

## Hard rules

- **Never** open a PR whose feature branch doesn't contain `origin/develop`'s tip. The branch-freshness check is mandatory, not advisory.
- **Never** target `main` as the base branch. The integration branch is `develop`.
- **Never** invent a Conventional-Commits type that disagrees with the branch prefix. If the branch is `feat/foo`, the type is `feat`: no translation.
- **Never** leave Summary, Changes, or Testing empty or equal to `None`. Stop and ask the user for content instead.
- **Never** silently force-push. Use `--force-with-lease` and only after explicit user confirmation; on an open non-draft PR, also document the rebase in a PR comment per pull-request-workflow §Fix-forward on red checks.
- **Never** amend a commit that has already been pushed. When iterating on an open PR to fix a red required check, push a **new** commit (fix-forward); `git commit --amend` after the push is prohibited by pull-request-workflow §Fix-forward on red checks because it destroys review context and breaks comment anchoring.
- **Never** mark a PR as ready for review while a required status check is red or pending on the head commit. Keep the PR as Draft (or return it to Draft) until every required check on the head commit is green.
- **Never** trigger merge (applying the `automerge` label or running `gh pr merge` manually) based on a status that no longer reflects the current head commit. The green signal must originate from the most recent commit on the branch.
- **Never** skip presenting the drafted title and body to the user before invoking `gh pr create`. `gh pr create` is an externally-visible action and requires confirmation.
- When `spec/project/pull-request-workflow/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.

## Gotchas

Per `spec/claude/skill-management/` §Gotchas — concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **`gh pr edit --add-label` can fail on Projects-Classic-deprecation noise.** Repos with Projects Classic still enabled return a `GraphQL: Projects (classic) is being deprecated` warning that the CLI treats as an error, even when the label edit itself would have succeeded. Prefer `gh api -X POST repos/<owner>/<repo>/issues/<number>/labels -f "labels[]=<label>"` for label application; it bypasses the GraphQL `projectCards` path entirely.
- **`gh pr view` warnings land on stderr, JSON on stdout.** When piping `gh pr view --json …` into a parser, the deprecation warning appears on stderr but the JSON on stdout still parses cleanly; when piping into another `gh` call without splitting streams, the warning may be conflated with the result. Always read state via `gh pr view --json <fields>` and route stderr to a separate log when scripting.
- **Branch-freshness check needs a fresh fetch first.** `git merge-base --is-ancestor origin/develop HEAD` is only meaningful after `git fetch origin develop` — otherwise the local `origin/develop` ref can be stale and the skill reports the branch as fresh when develop has moved. The fetch is part of the freshness contract, not a setup detail.
- **`task lint`'s prose hook can fail locally on missing Vale-style trust** (the underlying `task lint:prose` includes a remote `taskfile-include-pre-commit.yaml` that prompts for trust on first run). The CI run usually has the trust pre-granted; locally, a one-time `task --yes lint` resolves the prompt. Don't treat a local `vale-prose` red as a CI failure when direct `vale --minAlertLevel=error <files>` reports clean.
