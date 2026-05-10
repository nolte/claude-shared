# Example 01: Scaffold a new skill

## Input prompt

"Scaffold a new skill called `dependency-update` that helps me bump pinned dependencies in `pyproject.toml` and `package.json` after a Renovate PR has been reviewed."

## Input files

- `.claude-plugin/plugin.json` — present at the repo root, signalling that this repo is the `nolte-shared` plugin source tree, so the new skill belongs at `skills/dependency-update/`.
- `spec/claude/skill-management/en.md` — canonical authoring spec, applied because it exists in this project (per SKILL.md §"Operations").
- `skills/` — existing sibling skills (e.g. `dependency-audit/`, `quality-gate/`) used to confirm the proposed name doesn't collide and to model the SKILL.md shape.

## Expected behaviour

1. Detect that `.claude-plugin/plugin.json` exists at the repo root, lock the target path to `skills/dependency-update/`, and verify it does not already exist before doing anything else (per SKILL.md §"Target location" and §"Operations" step 2).
2. Collect the missing inputs interactively in the user's language (German, per the user-language policy): confirm the **purpose** is "bump pinned dependencies in `pyproject.toml` and `package.json` after a Renovate PR has been reviewed", probe for at least three concrete **trigger phrasings** (e.g. "bump the dependency pins", "apply the Renovate PR locally", "update the lockfile after merging Renovate"), and accept `dependency-update` as the **name** (already ASCII-kebab-case, doesn't collide with `dependency-audit`).
3. Draft `skills/dependency-update/SKILL.md` with valid YAML frontmatter — `name: dependency-update` (matching the folder), `description:` enumerating the collected triggers explicitly plus a `Do NOT use` carve-out against `dependency-audit` (CVE scanning) so routing stays unambiguous, and `tags: [...]` chosen from existing portfolio tags — followed by a brief body covering Purpose, User-language policy, Operations, and Hard rules. Do not scaffold empty `templates/`, `references/`, or `examples/` subfolders "just in case" (per SKILL.md §"Hard rules").
4. Present the proposed SKILL.md to the user for explicit approval before writing, then create the folder, write the file, and confirm back in German with the absolute created path.
5. Remind the user (in German) that a new plugin release is needed so consumers can pick the skill up via the marketplace flow, and explicitly state that this PR must **not** bump the version in `.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json` — `release-automation` owns that at publish time (per SKILL.md §"Target location" closing paragraph). Suggest invoking `skill-review` as the next step to validate the freshly scaffolded skill against the spec.
