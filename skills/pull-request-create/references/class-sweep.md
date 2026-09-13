# Filling the `## Class sweep` section

Read this when the PR title's type is `fix`. `spec/project/pull-request-workflow/<canonical_language>.md` §"Class sweep (Conventional-Commits type `fix`)" makes the section a MUST on that type and forbids it on every other type, so `feat`, `chore`, `docs`, and `exp` PRs never render it.

## Why the fields are numbers

A fix that repairs the site where a defect was found and says nothing about the rest of its class leaves the siblings in place. The next report then reads as a new defect rather than as the same one. A sentence of reassurance ("checked for similar cases") can't be distinguished from no check at all once it's in the body; an integer can. That's the entire design of the section.

## The four fields

```
## Class sweep

- Predicate: <the property that describes the class, stated so it can be run>
- Hits: <integer>
- Repaired: <integer>
- Guard: <path or required-check context that holds the rest, or `none` plus a reason>
```

1. **Predicate.** Ask what property describes the class this defect belongs to, then turn the answer into something runnable: a grep pattern, an AST query, a lint rule, a named check. Refuse a restatement of the bug. "Tenant handling" isn't a predicate. "Every route handler that reads a tenant id from the request body" is. Where a guard already exists for this class, reuse the guard's own selector verbatim, so the sweep and the guard can't drift apart.
2. **Hits.** Run the predicate against the working copy and count the matches. Never write a number that wasn't measured. An unmeasured count renders identically to a measured one and so reads as evidence while being a guess, which is worse than leaving the work undone visibly.
3. **Repaired.** Count the sites this PR actually repairs. When it's below `Hits`, add one line under the four fields naming which remaining sites are out of scope and why, and ask the user whether to file them as issues before the PR opens. Under `spec/project/issue-orchestration/` §"Verification and traceability" an orchestrated run **MUST** file them.
4. **Guard.** Name what stops the class from recurring: the path of a check, a required-status-check context, or the literal `none` plus the reason none is possible. A `fix` whose class has one member and can't recur still states that, in those words.

## Checklist before `gh pr create`

- [ ] `## Class sweep` is present, after all five required sections.
- [ ] `Predicate` is runnable, and it was actually run in this session.
- [ ] `Hits` and `Repaired` are integers, and `Hits` is the measured count.
- [ ] `Guard` names a path or a required-check context, or is `none` with a reason.
- [ ] When `Repaired` is below `Hits`, the out-of-scope remainder is named below the fields.

## What the check enforces

The reusable workflow `nolte/gh-plumbing/.github/workflows/reusable-pr-lint.yaml` (wired as the `pr-body / PR Lint` required status check) fails a `fix` PR when the section is missing, when any of the four fields is missing or empty, or when `Hits` or `Repaired` doesn't parse as an integer. It passes the same body on any other type. It can't tell a measured count from a guessed one, which is why that obligation sits here and in the skill's hard rules rather than in the checker.
