# Example 01: Augment a Claude plugin draft release with project context

## Input prompt

"Curate the release notes for the open draft on develop — this repo ships skills and agents, the body needs a project-context section."

## Input files

- `.claude-plugin/plugin.json` — manifest at the repo root, asserts the Claude-plugin classification (signal 1)
- `skills/` and `agents/` — top-level folders confirming the plugin shape; `git diff <prev-tag>..origin/develop -- skills/ agents/` shows two new skills (`skills/foo/SKILL.md`, `skills/bar/SKILL.md`), one renamed slash command (description-line change in `skills/baz/SKILL.md`), and a removed agent (`agents/old.md`)
- `AUDIENCES.md` — audience artefact pinning two primary audiences: "Plugin operators" (install / upgrade the plugin in their Claude Code) and "Skill / agent authors" (contributors building on the plugin)
- `release-drafter.yml` and `.github/workflows/release-publish.yml` — both present, `release-automation` adopted
- One open draft from `gh release list --json isDraft,tagName,targetCommitish,createdAt,name` — `isDraft: true`, `tagName: v0.42.0`, `targetCommitish: develop`; the draft tag SHA is an ancestor of `origin/develop`
- The draft body so far carries only `release-drafter`'s Conventional-Commits sections (Features / Bug Fixes / Maintenance), no marker pair yet
- `spec/project/release-skill-layer/en.md` — canonical spec resolved from the target repo
- `skills/release-notes-curate/references/project-bundles.md` — the Claude-plugin bundle (Skills changed, Agents changed, Slash command renames, Plugin manifest version, Breaking changes, Upgrade notes)

## Expected behaviour

1. Run preconditions — `git rev-parse --is-inside-work-tree` succeeds, `gh auth status` clean, `spec/project/release-skill-layer/en.md` resolved in-repo, `release-drafter.yml` and `release-publish.yml` both present.
2. Resolve the open draft via `gh release list` — exactly one draft (`v0.42.0`) targets `develop`, `git merge-base --is-ancestor` confirms the draft target SHA is reachable from `origin/develop`; record tag and target SHA.
3. Detect project type via signal 1 (Claude Code plugin) — record the matching signal (`.claude-plugin/plugin.json` plus `skills/` + `agents/`) and stop scanning the remaining five signals.
4. Read `AUDIENCES.md`, identify the two primary audiences (plugin operators, skill / agent authors), and record its path; do not dispatch `audience-identify`.
5. Derive the project-context bundle from `references/project-bundles.md` — walk `git log <prev-tag>..<draft-target-sha>` and assemble per-section entries attributed to commit SHAs / PR numbers / paths: Skills changed (two new skill paths + the renamed slash command's description-line delta with PR number), Agents changed (the removed `agents/old.md` plus its commit SHA), Plugin manifest version (the `plugin.json` version bump SHA), Breaking changes (the removed agent + the renamed slash command, both load-bearing for plugin operators), Upgrade notes (one-line operator-facing migration hint for the renamed command). Self-validate: plugin operators map to Breaking changes + Upgrade notes + Plugin manifest version; skill / agent authors map to Skills changed + Agents changed — every primary audience covered, no `## Open questions` needed.
6. Compose the augmentation block between the literal markers `<!-- release-skill-layer:project-context-start -->` and `<!-- release-skill-layer:project-context-end -->`, prefixed by a `---` divider, with `## Project context`, `### Audiences served` (two bullet entries → §-pointers), then one `###` per bundle section. English-only, regardless of the repo's docs language.
7. Disclose to the operator in one block — detected project type with the matched signal, audience artefact path and the two primary audiences, the augmentation block as a literal Markdown preview, and a unified diff between the current draft body and `current body + augmentation block`. Block until the operator confirms.
8. On confirmation, write the augmented body via `gh release edit v0.42.0 --notes "<full-body>"` (or `--notes-file` when the body crosses 4 KiB). Never call `gh release edit --draft=false`. Re-read via `gh release view v0.42.0 --json body` and verify exactly one start marker and one end marker survived the round-trip; refuse to declare success otherwise. Report the augmented draft URL back to the operator.
