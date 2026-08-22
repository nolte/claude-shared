# Post-merge branch cleanup

Step 9 carries the rules. This file carries the mechanism and the one-off catch-up
case, so the body doesn't have to.

## The remote branch is the platform's job

`spec/project/pull-request-workflow/<canonical_language>.md` §Post-merge branch
cleanup makes `delete_branch_on_merge: true` in `.github/settings.yml` (directly, or
via the `nolte/gh-plumbing` commons extension) the routine path. GitHub removes the
branch itself right after the squash-merge.

Confirm it in step 7:

```bash
gh api repos/<owner>/<repo>/git/refs/heads/<feature-branch>   # expect 404
```

A `404` is the success case. Anything else means the branch is still there.

## When the branch survives

The platform setting is missing, or it was enabled after this branch was created.
That's a **one-off catch-up**, not a routine step. Offer the manual call and act only
on explicit user confirmation:

```bash
gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<feature-branch>
```

**Never** run `git push origin --delete …` or `gh api -X DELETE` without that
confirmation, and never fold remote deletion into the automatic merge flow. The hard
rule at the end of the skill body states this; it isn't softened here.

## The serial-flow reminder

After cleanup, surface what's still queued:

```bash
gh pr list --state open --base develop --json number,title,headRefName,isDraft,labels
```

Every remaining pull request now **lags the advanced `develop` tip**. Each one must be
rebased onto it, and its required checks must go green again on the rebased head,
before this skill is re-invoked for it — in dependency order where a dependency
exists.

Don't rebase and don't re-invoke automatically. The next pull request is a separate,
operator-driven run; that separation is what keeps a failed rebase from cascading
through the queue unattended.
