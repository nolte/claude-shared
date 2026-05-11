# permission-allowlist-maintain

_Curates the committed `.claude/settings.json` `permissions.allow` list of the current repository per `spec/claude/permission-allowlist/`. Proposes additions sourced from the `fewer-permission-prompts` built-in or from the user, applies the spec's three-condition selection criteria (frequent + read-only + not-already-autoallowed), rejects forbidden pattern classes (interpreter wildcards, task-runner wildcards, mutation-capable `gh`/`git` wildcards), and routes every change through the standard pull-request flow. Invoke when the user asks to \"tidy the permission allowlist\", \"add `Bash(task lint)` to the allowlist\", \"review `.claude/settings.json`\", or equivalent German-language requests. Don't use to edit `.claude/settings.local.json` or `~/.claude/settings.json` (out of scope per spec)._

- **Plugin:** `nolte-shared`
- **Tags:** `scaffolding`, `audit`
- **Source:** [skills/permission-allowlist-maintain/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/permission-allowlist-maintain/SKILL.md)

---

## Permission Allowlist Maintain

Implements `spec/claude/permission-allowlist/` for the repository's committed `.claude/settings.json`. The skill is the curator: it gathers candidates, applies the spec's selection criteria with the user, and routes the resulting change through the standard PR flow. The candidate-discovery half is delegated to the `fewer-permission-prompts` Claude Code built-in (the spec's documented proposer); the decision to accept, narrow, or reject lives here.

### Why this is a skill, not an agent

- **Per-entry user approval is the contract.** Every candidate triggers a small dialogue (accept verbatim, narrow the pattern, reject with reason); the spec's §Selection criteria explicitly forbids batched insertion.
- **Externally-visible mutations need user gating.** `.claude/settings.json` lands in a PR that affects every contributor's confirmation prompts; the change is reviewed publicly, so the curator's mid-flow approvals are part of the contract.
- **Orchestrator pattern (per `skill-vs-agent`).** Candidate discovery is delegated to `fewer-permission-prompts` and the eventual PR is opened via `pull-request-create`; the skill stays in the main thread to chain those tools.
- Counter-dimension considered: a narrow agent could specialise on pattern-narrowing (turning `Bash(git fetch --tags --prune)` into `Bash(git fetch *)`), but the load-bearing dimension is interactivity, not output specialisation—skill wins.

### User-language policy

Detect the user's language and respond in it. The committed `.claude/settings.json` content (pattern strings, JSON keys) and the resulting PR title/body stay English so that portfolio automation (Probot Settings App context, label-sync, PR-body validators) parses them deterministically.

### Preconditions

Before any edit:

- Confirm the working directory is a git repository, the current branch isn't `develop` or `main`, and `git status --porcelain` is clean (or the only dirty path is `.claude/settings.json` itself).
- Confirm `spec/claude/permission-allowlist/<canonical_language>.md` is reachable. If missing, stop and report—without it the selection criteria are ad-hoc; this skill is the spec's implementer, not its replacement.
- Confirm `.claude/settings.json` exists (per the spec's AC #1) or scaffold it with an empty `permissions.allow` array if the user explicitly asks the skill to create the file from scratch. Never create it silently.
- Verify `.gitignore` doesn't list `.claude/settings.json` itself (the file is committed); it MAY list `.claude/settings.local.json` (which is developer-owned).

### Operations

#### 1. Load the current allowlist

Read `.claude/settings.json` and parse `permissions.allow`. Surface the current entries to the user as a numbered list so the rest of the dialogue can reference them by index.

If `permissions.allow` is missing or empty, ask the user for the seed set explicitly. Never invent entries from "common defaults."

#### 2. Gather candidates

Two source paths:

- **User-supplied:** the user names a pattern (`Bash(task lint)`) or a small list. Apply the §Selection criteria below to each candidate before staging.
- **`fewer-permission-prompts`-driven:** invoke the `fewer-permission-prompts` Claude Code built-in (the spec's documented proposer in §Governance) to scan recent transcripts for read-only commands that triggered confirmation prompts. The built-in returns a prioritised candidate list; the user decides which to take.

Don't proceed past this step if the user can't articulate why they want each candidate; the spec's first selection criterion ("documented as frequently occurring in a defensible sample") is operator-judged, not skill-judged.

#### 3. Apply the spec's selection criteria per candidate

For every candidate, walk the three conditions from `spec/claude/permission-allowlist/` §Selection criteria explicitly with the user:

1. **Frequent in a defensible sample?** Multiple recent sessions, multiple repositories, or a traceable spec requirement (for example `pull-request-workflow` §Pre-push verification justifies `Bash(task lint)`).
2. **Read-only in remote-state / secrets / shared-infrastructure terms?** Local filesystem writes are acceptable as a side effect (`git fetch` updates local refs, `task docs` writes `site/`) but **MUST** be justified. A candidate that mutates remote state or shared infrastructure is rejected outright.
3. **Not already in Claude Code's autoallowed set?** Re-running `fewer-permission-prompts` step 4 catches redundancy. Redundant entries are omitted.

Drop the candidate at the first failed condition; record the rejection reason for the PR body.

#### 4. Reject forbidden pattern classes outright

Independently of the three criteria, the spec's §Scope and location lists forbidden patterns:

- Interpreter / task-runner wildcards: `Bash(task *)`, `Bash(npm run *)`, `Bash(bun run *)`, `Bash(uv run *)`, `Bash(pip *)`, `Bash(python -m *)`, and equivalents
- Mutation-capable `gh` / `git` wildcards: `Bash(git *)`, `Bash(gh api *)`, `Bash(gh pr *)`, `Bash(gh repo *)`, and equivalents
- Anything that would undermine `pull-request-workflow` §Automerge trigger protocol (especially `Bash(gh pr merge *)`)

A user request that asks for one of these patterns gets a hard "no" with the spec citation, not a softened narrower form. The skill's job is to propose the narrowest exact form (`Bash(task lint)`, `Bash(gh pr view --json *)`) when the user really needs the capability.

#### 5. Narrow the surviving candidates

Per §Selection criteria's SHOULD: prefer the exact form over the prefix form. If the user has only ever observed one variant of `git fetch` (`Bash(git fetch)`), don't expand it to `Bash(git fetch *)` until flag variance is also observed. Walk this with the user candidate-by-candidate.

#### 6. Apply the change to `.claude/settings.json`

Edit the file in place, preserving JSON formatting (two-space indent matches the portfolio default). Show the diff to the user. Re-run a JSON parse to verify the file is still valid.

For removals (an entry no longer used), capture the user's stated reason. The spec mandates the reason in the eventual commit message. Common reasons: "upstreamed into the Claude Code autoallow list," "command no longer used since X migrated to Y."

#### 7. Hand off to the PR flow

The change ships through the standard pull-request flow per the spec's §Authoring flow integration:

- Conventional Commits type: `chore` for pure allowlist maintenance, `docs` if a companion spec edit is bundled (rare; usually a separate PR)
- Branch prefix per `branching-model`: `chore/<short-slug>`
- The fix-PR body's **Risk / rollout notes** explicitly notes (a) which entries were added and the criterion that justified each, (b) which entries were removed and the reason, (c) confirmation that no forbidden pattern was introduced
- `task lint` runs locally before push per `pull-request-workflow` §Pre-push verification

Dispatch `nolte-shared:pull-request-create` for the PR creation; the user confirms title and body before push.

The actual merge is `pull-request-merge`'s job, not this skill's.

### Hard rules

- **Never** edit `.claude/settings.local.json` or `~/.claude/settings.json`. Both are developer-owned and out of scope per the spec's §Non-Goals.
- **Never** insert a forbidden pattern (interpreter wildcards, task-runner wildcards, mutation-capable `gh` / `git` wildcards)—even when the user asks. Counter-propose the narrowest exact form.
- **Never** copy a broad pattern from `.claude/settings.local.json` or `~/.claude/settings.json` into the committed `.claude/settings.json` without re-evaluating it against the three selection criteria; the spec's §Relationship to settings.local.json forbids the silent promotion.
- **Never** insert a pattern that undermines `pull-request-workflow` §Automerge trigger protocol or §CI gate into develop. `Bash(gh pr merge *)` and equivalents stay rejected even with operator override.
- **Never** commit `.claude/settings.json` directly to `develop` or `main`. Every change goes through the standard PR flow.
- **Never** silently re-format the file beyond the change you're making—preserve unrelated entries verbatim, keep the existing indent, don't reorder unrelated keys.
- **Always** state the removal reason in the commit message when pruning entries—the spec mandates it.
- **Always** verify the file parses as valid JSON after the edit; a syntactically broken `.claude/settings.json` makes the harness fall back to "prompt for everything," which is worse than the original state.
- When `spec/claude/permission-allowlist/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.

### Gotchas

Per `spec/claude/skill-management/` §Gotchas—concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **`fewer-permission-prompts` is a Claude Code built-in, not a plugin skill.** It lives in the harness, not under `skills/`. When dispatching it, use the Skill tool with the literal name `fewer-permission-prompts` (no plugin prefix). If the harness rejects the dispatch (older Claude Code versions don't ship it), fall back to operator-supplied candidates and report the gap.
- **`.claude/settings.json` is read at session start.** Adding an entry doesn't take effect for the running session, only for future sessions. Don't expect the post-edit prompt to disappear immediately; the user has to restart Claude Code (or open a fresh session) to see the new allowlist behaviour.
- **The Probot Settings App doesn't manage `.claude/settings.json`.** The file is repository-content, not GitHub repository settings—Probot operates on `.github/settings.yml`, not on `.claude/`. Don't conflate the two surfaces; an outage of the Settings App has no bearing on the allowlist's effect.
- **Renovate ignores `.claude/settings.json` by default.** No automated bump exists for the patterns; drift is human-detected (the `fewer-permission-prompts` skill is the proposer, this skill is the curator). Don't expect a Renovate PR for "newer Claude Code autoallow list"—the autoallow list isn't versioned at the repository level.
- **Removing an entry never breaks past sessions.** A removal-only commit is safe to merge anytime; the entry simply moves back to the per-prompt confirmation flow. The spec still requires the removal reason in the commit message so future readers see the trajectory.
