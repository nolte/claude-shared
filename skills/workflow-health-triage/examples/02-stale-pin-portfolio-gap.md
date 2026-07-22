# Example 02 — `stale pin` in `nolte/gh-plumbing`, portfolio gap surfaced

Demonstrates the runtime-discovery branch where no candidate agent's `description:` line plausibly matches a `stale pin` failure on a `nolte/gh-plumbing` reusable workflow tag, and the failure class has occurred three or more times historically. The skill surfaces this as a portfolio gap per `spec/project/workflow-health/` §Specialised-agent dispatch and asks the user whether to author a new specialised agent (via `claude-plugin-developer`) before opening the fix PR with generalist remediation.

## Input prompt

> Klassifiziere bitte den fehlgeschlagenen `automerge.yaml`-Run vom letzten Squash-Merge auf `develop`: <https://github.com/nolte/claude-shared/actions/runs/9988222333>. Der Log sagt `mergeResult: 'merge_failed'` aber der Run-Status ist grün — irgendwas mit dem `pascalgn/automerge-action`-Pin, vermute ich.

## Input files

Repository state when the skill is invoked:

- `spec/project/workflow-health/en.md` — present, declares `stale pin` as one of the six classes and the §Specialised-agent dispatch contract (including the "three-or-more historical occurrences ⇒ portfolio gap" rule).
- `.github/workflows/automerge.yaml` — required check on `develop`. The file `uses:` `nolte/gh-plumbing/.github/workflows/automerge.yaml@v1.4.0`, and a newer tag `v1.6.2` exists upstream that fixes the `MERGE_METHOD` default to honour repo-allowed strategies.
- `gh run view 9988222333 --log-failed` excerpt:

  ```

  ::group::Merge PR
  Failed to merge PR: ...
  mergeResult: 'merge_failed'
  ::endgroup::
  Run completed (exit 0)

  ```

  (The `pascalgn/automerge-action` exits 0 even on `mergeResult: 'merge_failed'` — see the SKILL's *Gotchas* section.)
- `git log --oneline -1 <headSha>` resolves to a squash-merge commit on `develop` whose diff doesn't touch `automerge.yaml` — confirming the failure is in the reusable, not in the consumer's code.
- `gh run list --status failure --branch develop --limit 50 | grep -c automerge` returns `4` — the historical-occurrence threshold is met.
- `agents/` directory at runtime contains:
  - `agents/claude-plugin-developer.md` (description: spec-conformant skill / agent / plugin-manifest authoring).
  - `agents/audience-doc-author.md` (description: audience-aware MkDocs documentation prose).
  - `agents/feature-consistency-reviewer.md` (description: feature-spec consistency review).
  No agent's `description:` line names *"reusable workflow YAML maintenance"*, *"`nolte/gh-plumbing` tag bumps"*, or *"GitHub Actions pin remediation"*.

## Expected behaviour

1. **Classify as `stale pin`, not `defect` and not `flake`.** Per the spec table, a `uses:` pin pointing to a `nolte/gh-plumbing` (or other reusable) tag with a newer tag carrying the relevant fix is `stale pin`. The *Gotchas* note about `pascalgn/automerge-action` exiting 0 on `mergeResult: 'merge_failed'` resolves the green-run / red-merge ambiguity — the skill recognises this is a `stale pin` against the reusable's tag, not a consumer-side `defect`.
2. **Confirm with the user.** `stale pin` is not in the high-cost three (`defect` / `flake` / `secret drift`), but the skill still names the class out loud in German before dispatch so the user can correct.
3. **Dynamic candidate discovery — no match.** The skill `Glob`s `agents/*.md` and `~/.claude/agents/*.md`, `Read`s every `description:` line, and walks the candidates. None of `claude-plugin-developer` (skills / agents / plugin manifest), `audience-doc-author` (documentation prose), or `feature-consistency-reviewer` (feature-spec consistency) names workflow YAML maintenance, reusable-workflow tag bumps, or pin remediation. The match step yields **no candidate**.
4. **Historical-occurrence check.** The skill runs `gh run list --status failure --branch develop --limit 50` and greps for `automerge` failures; the count is `4`, meeting the spec's *three-or-more* threshold for portfolio-gap escalation.
5. **Surface the portfolio gap.** Per `spec/project/workflow-health/` §Specialised-agent dispatch, the skill stops the dispatch flow and asks the user in German: *"Ich finde im Agent-Inventar keinen passenden Spezialist für `stale pin`-Failures auf `nolte/gh-plumbing`-Reusables, und diese Klasse ist auf `develop` schon viermal aufgetreten. Möchtest du den Agenten jetzt anlegen lassen (via `claude-plugin-developer`), oder mit Generalist-Remediation den Fix-PR öffnen und das Authoring auf später vertagen?"*.
6. **Branch on the user's answer.**
   - If the user opts to author the agent: dispatch `Agent(subagent_type="nolte-claude-dev:claude-plugin-developer", …)` with the brief *"author a new specialised agent whose responsibility is `nolte/gh-plumbing` reusable-workflow tag-pin remediation, including the `pascalgn/automerge-action` `mergeResult: 'merge_failed'` quirk"*. Wait for the agent's report; then dispatch the newly-authored agent on the actual fix.
   - If the user opts for generalist now: open the fix PR with the Risk / rollout notes literally `Triage classification: stale pin` and `Dispatched agent: no matching specialised agent—generalist remediation`, and record the portfolio gap in the PR body so the deferred authoring is discoverable.
7. **Hard-rule guard against drift.** The skill **never** proposes repointing the `nolte/gh-plumbing` pin from a tag to a branch (forbidden by the *Hard rules*); the bump goes from `@v1.4.0` to `@v1.6.2`, both tag refs. The skill **never** proposes enabling Renovate automerge for `nolte/gh-plumbing` bumps (the *Gotchas* section calls this out — Renovate-generated `nolte/gh-plumbing` PRs aren't automerged in this portfolio).
8. **Stop after PR open.** No merge. Final report names the run ID, the classification (`stale pin`), the dispatched agent (or the literal generalist sentence), the fix-PR URL, the portfolio-gap status (open / authoring-dispatched), and the next-action hint *"invoke `pull-request-merge` after CI is green"*.
