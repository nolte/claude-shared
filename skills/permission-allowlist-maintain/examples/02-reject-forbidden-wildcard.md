# Example 02: Refuse `Bash(git *)` wildcard, counter-propose narrowest exact form

## Input prompt

"Add `Bash(git *)` to the allowlist — I'm tired of the prompt firing every time I run a git command."

## Input files (optional)

- `.claude/settings.json` — existing committed allowlist on a `chore/<slug>` branch off `develop`, working tree clean.
- `spec/claude/permission-allowlist/en.md` — canonical spec; §Scope and location lists the forbidden pattern classes that block this request.

## Expected behaviour

1. Acknowledge the candidate but do **not** stage it. Cite `spec/claude/permission-allowlist/` §Scope and location verbatim: mutation-capable `git` wildcards (`Bash(git *)`) are a forbidden pattern class because they would silently authorise destructive operations (`git push --force`, `git reset --hard`, `git checkout --`) that the `pull-request-workflow` §Automerge trigger protocol and the `git`-safety conventions explicitly gate behind per-prompt confirmation. This is a hard "no", not a softened narrower form negotiation.
2. Ask the user which concrete `git` invocations actually triggered the prompts. If the user names read-only forms (e.g. `git fetch --tags --prune`, `git log --oneline -20`, `git rev-parse --abbrev-ref HEAD`), counter-propose the narrowest exact form per §Selection criteria's SHOULD: `Bash(git fetch --tags --prune)` over `Bash(git fetch *)`, and only expand to a prefix form when flag variance is independently observed.
3. For each counter-proposed exact form, re-walk the three §Selection criteria (frequent, read-only in remote-state terms, not already autoallowed) before staging. Drop any candidate that fails. Record the original `Bash(git *)` rejection plus the spec-citation in a note for the eventual PR body's **Risk / rollout notes** so the audit trail captures that a forbidden pattern was requested and refused. No edit to `.claude/settings.json` happens until at least one surviving narrowed candidate is approved; if all candidates are dropped, the skill exits without a PR.
