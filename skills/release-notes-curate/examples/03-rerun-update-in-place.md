# Example 03: Re-run on an already-augmented draft updates in place via the marker pair

## Input prompt

"Re-run the release-notes curation on `v0.42.0` — three more PRs landed on develop since the last curation, the project-context section needs to catch up."

## Input files

- `.claude-plugin/plugin.json`, top-level `skills/` and `agents/` — project type still Claude plugin (no project-type drift since the previous curation)
- `AUDIENCES.md` — unchanged since the previous curation; still pins "Plugin operators" and "Skill / agent authors"
- `release-drafter.yml` and `.github/workflows/release-publish.yml` — present
- One open draft from `gh release list` — `tagName: v0.42.0`, `targetCommitish: develop`, ancestor of `origin/develop`; the draft body **already** carries the marker pair `<!-- release-skill-layer:project-context-start -->` … `<!-- release-skill-layer:project-context-end -->` from the previous curation, with the `## Project context` block and bundle sections inside
- `git log <prev-tag>..<draft-target-sha>` shows three commits since the previous curation captured the draft: a fourth new skill (`skills/qux/SKILL.md`), a `plugin.json` patch-version bump from `0.42.0-rc.1` to `0.42.0-rc.2`, and a docstring-only refactor on an existing skill (no operator-visible delta)
- `spec/project/release-skill-layer/en.md` — canonical spec
- `skills/release-notes-curate/references/project-bundles.md` — the Claude-plugin bundle

## Expected behaviour

1. Run preconditions, resolve the open draft (`v0.42.0`, single match, ancestor of `origin/develop`), detect project type via signal 1 (Claude plugin — unchanged), re-read `AUDIENCES.md` (unchanged, primary audiences identical).
2. Re-derive the bundle by walking `git log <prev-tag>..<draft-target-sha>` against the current bundle definition — assemble the new working set: Skills changed (now four entries instead of three; the docstring-only refactor is excluded as not operator-visible), Plugin manifest version (the `0.42.0-rc.1 → 0.42.0-rc.2` bump SHA appended to the existing entry), Agents changed / Breaking changes / Upgrade notes unchanged from the previous run.
3. Detect the existing marker pair in the draft body via a single grep, locate the existing block content between the markers, and diff the freshly derived bundle content against the existing block content; record the delta (one new skill bullet, one updated plugin-manifest-version bullet, no other changes).
4. Surface to the operator — the marker pair was found exactly once, the project type and audience artefact have not drifted, the bundle delta is two lines (one added skill bullet, one updated manifest-version bullet), and a unified diff between `current full body` and `current full body with the block content between the markers replaced by the new bundle content`. Block until the operator confirms; if the operator declines, stop without writing.
5. On confirmation, write the updated body via `gh release edit v0.42.0 --notes-file <tempfile>`, **replacing the content between the existing markers in place** — never append a second marker pair, never compose the new block outside the existing markers, never duplicate the `## Project context` heading or any of its `###` subsections. Never touch the `release-drafter` Conventional-Commits content above the `---` divider.
6. Re-read the draft body via `gh release view v0.42.0 --json body` and verify exactly one start marker and one end marker remain (count must equal 1 each). Refuse to declare success if either marker count drifts. A subsequent clean re-run with no further commits MUST then produce "no diff" and stop without writing.
