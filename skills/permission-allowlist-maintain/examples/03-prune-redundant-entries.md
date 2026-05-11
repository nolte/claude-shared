# Example 03: Prune entries that are now in Claude Code's autoallow set

## Input prompt

"Tidy the permission allowlist — drop anything Claude Code now autoallows by default."

## Input files (optional)

- `.claude/settings.json` — existing committed allowlist with several entries that predate the latest Claude Code autoallow expansion (e.g. `Bash(ls)`, `Bash(pwd)`, `Bash(git status)` are commonly autoallowed in current harness versions).
- `spec/claude/permission-allowlist/en.md` — canonical spec; §Selection criteria condition (3) and the spec-mandated removal-reason commit-message rule both apply.

## Expected behaviour

1. Verify preconditions (git repo, branch is not `develop` / `main`, working tree clean or only `.claude/settings.json` dirty, spec reachable). Read `.claude/settings.json` and surface every current `permissions.allow` entry as a numbered list so the rest of the dialogue can reference items by index.
2. Dispatch the `fewer-permission-prompts` Claude Code built-in to re-run its step-4 autoallow check across the existing entries (the built-in is the spec's documented proposer for redundancy detection). For each entry the built-in reports as already-autoallowed, present it to the user one at a time and capture a one-line removal reason verbatim — typically "upstreamed into the Claude Code autoallow list" or "command no longer used since X migrated to Y". Per-entry user approval is required; never batch-prune. If the harness rejects the `fewer-permission-prompts` dispatch (older Claude Code versions don't ship it), fall back to operator-confirmed candidates and report the gap.
3. Edit `.claude/settings.json` in place: remove only the approved entries, preserve unrelated entries verbatim, keep the existing two-space indent, do not reorder remaining keys. Re-parse the file as JSON to verify validity (a syntactically broken file is worse than the original state). Show the diff to the user. Dispatch `nolte-shared:pull-request-create` with a `chore`-typed Conventional Commits title (e.g. `chore(allowlist): prune autoallowed entries`) whose body's **Risk / rollout notes** lists each removed entry alongside the captured removal reason — the spec-mandated audit trail. The user confirms title and body before push; merge stays out of scope.
