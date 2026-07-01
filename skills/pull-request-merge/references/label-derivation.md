# Label derivation

The candidate label set for step 3 of `pull-request-merge`. Build candidates from the two sources below, intersect them with the labels that actually exist in the repository (collected in step 1), and apply only the survivors. **Never create a new label**; a candidate that doesn't exist is reported as a portfolio gap to close via `.github/settings.yml` (directly or via `nolte/gh-plumbing:.github/commons-settings.yml`), not silently added.

## Candidate sources

- **Type label** from the PR title's Conventional-Commits prefix: `feat` → candidates `type:feat`, `kind:feat`, `feat`; same pattern for `fix`, `chore`, `docs`. Take the first candidate that exists.
- **Area labels** from touched paths (case-insensitive match against existing labels):
  - paths under `spec/` → candidates `area:spec`, `spec`
  - paths under `skills/` → candidates `area:skill`, `skills`
  - paths under `agents/` → candidates `area:agent`, `agents`
  - paths under `.github/workflows/` or `.github/settings.yml` → candidates `cicd`
  - paths under `docs/` or `mkdocs.yml` → candidates `area:docs`, `documentation`
  - paths under `.claude/`, `.claude-plugin/`, or `CLAUDE.md` → candidates `area:claude`, `claude-code`

## Apply

Apply the surviving set in a single call:

```
gh pr edit <number> --add-label <label1> --add-label <label2> …
```

Report the labels that were applied and any candidates that were skipped because no matching label existed.
