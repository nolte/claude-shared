# Linked-issue closure procedure

The step-8 procedure for `pull-request-merge`. GitHub's `Closes #<n>` / `Fixes #<n>` / `Resolves #<n>` autolinks fire only on default-branch merges, so a squash-merge into `develop` leaves referenced tracking issues `OPEN`. This procedure closes them with operator confirmation rather than waiting for the next `release-cd-refresh-master.yml` fast-forward of `main`, per `spec/project/pull-request-workflow/<canonical_language>.md` §"Linked-issue closure on develop merge".

Run only when step 7a confirmed `state == MERGED`. If the PR body carries no closing-keyword references, skip.

1. Scan the PR body for closing-keyword references — case-insensitive `(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s+#(\d+)`. Deduplicate by issue number. `Refs #<n>` is **not** a closing keyword and is ignored on purpose.

2. For each referenced issue, read its current state:

   ```
   gh issue view <n> --json state,title --jq .
   ```

   Skip when `state == CLOSED` — the autolink may have fired (for example because `main` was fast-forwarded between the merge and this step), or another path closed it already.

3. Present the remaining `OPEN` list to the operator, one line per issue (`#<n> <title>`), and require explicit confirmation before any close call. The operator **MAY** select all, a subset, or none.

4. For each confirmed issue, close with a cross-reference comment that names the merging PR and the merge-commit SHA on `develop`:

   ```
   gh issue close <n> --reason completed --comment "Resolved by #<pr> (merged to \`develop\` as \`<merge_sha>\`). The \`Closes #<n>\` autolink fires only on default-branch merges; this repo's default is \`main\`, fast-forwarded from \`develop\` via \`release-cd-refresh-master\` — closing manually now rather than waiting for that promotion."
   ```

Report back which issues were closed, which were skipped because they were already closed, and which the operator declined.
