# Example 01: Add `Bash(task lint)` from a `fewer-permission-prompts` candidate

## Input prompt

"Run `fewer-permission-prompts` over my recent transcripts and add the high-frequency read-only candidates to the allowlist."

## Input files (optional)

- `.claude/settings.json` — existing committed allowlist with a small seed (e.g. `Bash(git status)`, `Bash(git diff:*)`); branch is a fresh `chore/<slug>` off `develop`, working tree clean.
- `spec/claude/permission-allowlist/en.md` — reachable canonical spec used to cite §Selection criteria during the dialogue.

## Expected behaviour

1. Verify preconditions: working directory is a git repo, current branch is not `develop` / `main`, `git status --porcelain` is clean (or the only dirty path is `.claude/settings.json`), `.claude/settings.json` exists, and `spec/claude/permission-allowlist/<canonical_language>.md` resolves. Surface the current `permissions.allow` array as a numbered list.
2. Dispatch the `fewer-permission-prompts` Claude Code built-in via the Skill tool (no plugin prefix). Receive the prioritised candidate list including `Bash(task lint)` (observed N times across recent sessions, all read-only). Present each candidate to the user one at a time — no batching.
3. For `Bash(task lint)`, walk the three §Selection criteria explicitly: (a) frequent — cite the `fewer-permission-prompts` count plus the `pull-request-workflow` §Pre-push verification anchor that justifies it portfolio-wide; (b) read-only — confirm `task lint` mutates only local files (lint cache), no remote state; (c) not already autoallowed — confirm the harness still prompts for it. Reject the spec-forbidden `Bash(task *)` wildcard form upfront and counter-propose the exact form `Bash(task lint)`.
4. After per-candidate user approval, edit `.claude/settings.json` in place, preserving two-space indent and unrelated entries verbatim, append `Bash(task lint)` to `permissions.allow`, then re-parse the file as JSON to verify validity. Show the diff to the user.
5. Dispatch `nolte-shared:pull-request-create` with a `chore`-typed Conventional Commits title (e.g. `chore(allowlist): add task lint`) and a body whose **Risk / rollout notes** lists the added entry plus the §Selection-criterion citation that justified it, and confirms no forbidden pattern was introduced. The user confirms title and body before push; merge is out of scope (handled by `pull-request-merge`).
