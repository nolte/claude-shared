# Example 03 — a finding whose remedy belongs upstream

## Input prompt

> "Der PR-Linter in diesem Repo weicht vom Rest ab, kannst du das hier fixen?"

## Input state

A consumer repository whose `.github/workflows/pr-lint.yml` contains a hand-maintained local copy of the pull-request linting logic, diverging from the reusable implementation the portfolio publishes.

## Expected behaviour

1. Recognises the finding as portfolio-wide rather than repository-local: the logic is identical across repositories, so it belongs in `nolte/gh-plumbing` per `github-actions-best-practices` §E and `continuous-integration` §H.
2. **Refuses to patch the consumer copy**, and says why: patching it produces exactly the drifting fork the reuse model exists to prevent, and the same rule `workflow-health` applies to the `GITHUB_TOKEN` cascade applies here.
3. Emits a named upstream work package instead, containing:
   - the target repository (`nolte/gh-plumbing`)
   - what the reusable workflow needs to gain or fix
   - which consumer repositories are affected
   - the pinned reference each consumer would move to afterwards
4. Offers the only permitted local action: replace the local copy with a pinned call to the existing reusable workflow, if one already covers the need.
5. If the operator insists on a local workaround, records it as an interim measure that names the upstream change it waits for, so the workaround stays visibly temporary rather than becoming the new normal.

## What would be wrong

- Fixing the local copy because it's faster and the operator asked.
- Silently leaving the divergence unreported because the fix isn't in this repository.
- Opening a pull request against `nolte/gh-plumbing` unasked — the skill emits the work package; dispatching cross-repository work is the operator's call.
