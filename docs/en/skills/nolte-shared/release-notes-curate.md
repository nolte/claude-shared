---
title: release-notes-curate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# release-notes-curate

> Augments the open release-drafter draft on develop with project-context-aware sections via gh release edit.

_Augments the open release-drafter draft on develop with project-context-aware sections per the canonical-language file under spec/project/release-skill-layer/ §\"Skill A — Draft notes curation\". Reads the project's audience artefact, derives a section bundle from the detected project type, wraps the augmentation in stable HTML-comment markers so re-runs update in place, and writes the body back via `gh release edit` for a release tag. Invoke when the user asks to \"curate the release notes\", \"shape the release notes for this repo\", or the German \"kuratiere die Release-Notes\", \"reichere den Release-Draft mit Projektkontext an\". Don't use to publish the release (use [`release-publish-trigger`](release-publish-trigger.md)), to identify audiences (use [`audience-identify`](audience-identify.md)), to draft notes from scratch (use the [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md) agent), or to scaffold issue / PR templates (use [`github-issue-templates-apply`](github-issue-templates-apply.md)). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 7 Close & Release (`close-release`)
- **Tags:** `release`
- **Source:** [skills/release-notes-curate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/release-notes-curate/SKILL.md)

## Use when

- you want to curate the release notes for the open release-drafter draft
- you want to augment the draft release with project-context sections
- you want to shape the release notes for this repo's audiences

## Don't use when

- **You want to actually publish the release rather than augment the draft** → [`release-publish-trigger`](release-publish-trigger.md)
- **You want to identify audiences first** → [`audience-identify`](audience-identify.md)

## See also

- [`release-publish-trigger`](release-publish-trigger.md)
- [`audience-identify`](audience-identify.md)
- [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md)

---

## Release Notes Curate

Operationalises `spec/project/release-skill-layer/<canonical_language>.md` §"Skill A — Draft notes curation" against a target repository: classifies the project type, reads the audience artefact, derives a project-context section bundle, wraps it in stable markers below the `release-drafter` body, and writes back via `gh release edit --notes`. Idempotent on re-runs.

### Why this is a skill, not an agent

- **Per-write user approval is the contract** — the spec mandates a disclose-and-confirm gate before any `gh release edit --notes`, because the body is externally visible on the GitHub release page; an agent's fire-and-forget shape would lose that gate.
- **Output flows back into the main conversation** — the project-type classification, the section bundle preview, and the diff between existing and augmented body all surface in the conversation so the operator can correct the augmentation before commit.
- **Orchestrator role** — when no audience artefact exists, this skill dispatches [`audience-identify`](audience-identify.md) first; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: a narrow Markdown-formatter agent could specialise on section composition, but the load-bearing dimension is the multi-step approval dialogue (project type → audience → bundle → diff → write), not the prose mechanics — skill wins.

### User-language policy

Detect the user's language and respond in it. The release notes themselves stay in **English**, regardless of the repo's documentation language — the GitHub release UI is English-only in practice and translated section headings would mismatch the surrounding chrome.

### Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`) and the remote resolves to a GitHub repository.
- Confirm `gh` is authenticated (`gh auth status`).
- Locate `spec/project/release-skill-layer/` — either in the target repo or, when absent, via the `nolte-shared` plugin install path. Stop and ask which spec source to use if neither is reachable.
- Confirm the repo ships `release-drafter.yml` and `release-publish.yml` per `branching-model` and `release-automation`. If `release-drafter.yml` is missing, the operator should adopt `release-automation` first; this skill stops and reports.

### Operations

Operations 4 to 6 form a stacked Plan-validate-execute cycle: Operation 4 self-validates the bundle against the audience artefact and the spec's content rules before disclosure, Operation 5 surfaces the planned diff for explicit operator confirmation, and Operation 6 writes via `gh release edit --notes` and verifies the marker pair survived the round-trip. Operation 7 closes the loop on re-runs by detecting in-place updates instead of duplicating the augmentation block.

#### 1. Resolve the open draft

- Run `gh release list --json isDraft,tagName,targetCommitish,createdAt,name`.
- Filter to entries where `isDraft == true` and `targetCommitish` equals the repo's default branch (`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` — typically `develop`).
- **Refuse and report** when:
  - no draft matches: ask the operator to push to `develop` so `release-drafter.yml` can produce a draft, or run the workflow manually with `gh workflow run release-drafter.yml --ref develop`;
  - more than one draft matches: list all candidate tags and ask which one to operate on (the spec forbids a "newest wins" heuristic);
  - the draft's tag isn't reachable from the default branch tip (`git merge-base --is-ancestor <draft-target-sha> origin/develop`): the draft is stale relative to `develop`, the operator should re-run `release-drafter.yml` first.

#### 2. Detect project type

Walk the same six derivation signals used by [`github-issue-templates-apply`](github-issue-templates-apply.md), in order; stop at the first match. Read the files via the standard read tools — never via filename heuristics alone:

1. **Claude Code plugin** — `.claude-plugin/plugin.json` exists; top-level `skills/` and / or `agents/` folder present.
2. **Python application** — `pyproject.toml` declares `[project.scripts]` (or equivalent application entry point), no library distribution metadata.
3. **Python library** — `pyproject.toml` declares a distributable package without an application entry point.
4. **Node / TypeScript library or app** — `package.json` exists; `main` / `exports` indicates library, `bin` / `scripts.start` indicates app.
5. **CLI tool** — declared CLI entry point in `pyproject.toml` (`[project.scripts]`), `package.json` (`bin`), or `Cargo.toml` (`[[bin]]`).
6. **Documentation-only repo** — `mkdocs.yml`, `docusaurus.config.*`, or similar exists with no application source.

When `.github/release-skill-layer.yml` declares an explicit `project_type:` value, use it instead of the autodetection (override path).

When no signal matches, stop and ask the operator to declare the project type manually. Never proceed with a generic fallback bundle.

#### 3. Resolve audience artefact

The spec requires that every section the skill writes traces back to an audience need.

- Grep the repo for an audience artefact: `AUDIENCES.md` at the root, an "Audiences" or "Intended consumers" section in `README.md`, or a dedicated `docs/release-audiences.md`.
- If found, read it and identify the primary audiences plus the content dimensions each one needs (per `release-notes-audience-analysis`).
- If not found, dispatch the [`audience-identify`](audience-identify.md) skill to produce one before continuing. The skill stops, hands control to [`audience-identify`](audience-identify.md), and resumes when the artefact lands.

The skill **MUST NOT** invent audience entries inline. Missing audiences become an `## Open questions` note inside the augmentation block, not fabricated content.

#### 4. Derive the project-context bundle

Read `references/project-bundles.md` for the canonical section bundle per project type. Bundles are starting points; the audience artefact may motivate further sections or trim listed sections that no audience needs.

For each bundle section, walk the commits since the previous release tag (`git log <prev-tag>..<draft-target-sha>`) and assemble the per-section content:

- **Claude Code plugin** — diff `skills/`, `agents/`, `spec/` paths between the previous release tag and the draft target SHA; identify breaking changes by inspecting renamed slash commands (description-line changes), removed skills / agents, and plugin manifest version bumps.
- **Python application** — diff `pyproject.toml` for runtime / dependency bumps, walk hardware-touching paths if the application matches the hardware-application heuristic (per [`github-issue-templates-apply`](github-issue-templates-apply.md) references).
- **Python library / Node / TypeScript** — diff API entry points (public modules, exported symbols), inspect `pyproject.toml` / `package.json` for major-version bumps.
- **CLI tool** — diff command-line definitions in `pyproject.toml [project.scripts]`, `package.json bin`, or `Cargo.toml [[bin]]`.
- **Documentation-only repo** — diff `docs/` for path moves, removals, new translations.

Attribute every entry to a concrete commit SHA, PR number, or touched path so reviewers can validate without re-walking `git log`.

**Self-validation pass** before moving to step 5: count required sections vs the audience artefact's primary audiences; verify every primary audience maps to at least one section; if a gap exists, record it in the augmentation block's `## Open questions` subsection rather than fabricating coverage.

#### 5. Build the augmentation block

Compose the augmentation in this exact shape, between the markers:

```markdown
<!-- release-skill-layer:project-context-start -->

---

### Project context

#### Audiences served

- **<Primary audience 1>** → addressed by §<section-name>(s)
- **<Primary audience 2>** → addressed by §<section-name>(s)

#### <Section 1 from bundle>

- <entry attributed to commit SHA / PR # / path>
- <…>

#### <Section 2 from bundle>

- <…>

#### Open questions

- <gap noted during step 4 self-validation, when applicable>

<!-- release-skill-layer:project-context-end -->
```

Place the block **below** the `release-drafter` Conventional-Commits sections, separated by a horizontal rule (`---`). Skip the `## Audiences served` subsection when no primary audience is recorded; skip `## Open questions` when no gap was detected.

#### 6. Disclose, confirm, write

Before any write, surface to the operator:

- detected project type (with the signal that matched);
- audience artefact path and the primary audiences it pinned;
- the planned augmentation block as a literal Markdown preview;
- a unified diff between the current draft body and the new (current body + augmentation block, or — on re-run — current body with the existing marker block replaced).

Block the write until the operator confirms.

On confirmation:

- Write the augmented body back via `gh release edit <tag> --notes "<full-body>"` (use `--notes-file <path>` with a temp file when the body crosses the shell quoting threshold).
- **Never** call `gh release edit --draft=false` from this skill — that path belongs to [`release-publish-trigger`](release-publish-trigger.md) and `release-publish.yml`.
- Re-read the draft body via `gh release view <tag> --json body` and verify exactly one `<!-- release-skill-layer:project-context-start -->` and one `<!-- release-skill-layer:project-context-end -->` marker remain. Refuse to declare success otherwise.

#### 7. Re-run drift detection

When the skill is re-invoked on a draft that already carries the marker pair:

- Locate the existing block between the markers.
- Diff the new bundle against the existing block content; if identical, report "no diff" and stop.
- If different (new commits since the previous run, audience artefact changed, project-type signals shifted), surface the diff and ask whether to apply.
- Replace the content **between** the markers; **never** create a second marker pair, append outside, or duplicate sections.

A clean re-run on an already-curated draft with no new commits MUST produce no diff.

### Gotchas

- The release UI is English-only in practice. Even when the repo's docs are German, release notes stay English.
- `release-drafter` re-runs after Skill A may overwrite the body. The marker pair should survive because `release-drafter` only generates Conventional-Commits sections above the divider, but the spec's open question on this stays open until verified against `nolte/gh-plumbing`'s `reusable-release-drafter.yml`. If a re-run is detected to have stripped the markers, the skill simply re-applies the augmentation and reports the loss as an open `workflow-health` item.
- `gh release edit --notes` accepts the body as a single argument — long bodies need `--notes-file <path>` to avoid shell-quoting issues. The skill uses a tempfile when the body exceeds 4 KiB.
- `gh release edit --draft=false` is a separate flag from `--notes` and is the publish operation. This skill never sets it, even by accident: refuse the operation if any code path would compose `--draft=false`.
- The marker comment text is the **contract** with re-runs and any other tooling that may inspect the body. Never change the marker strings; never wrap them in additional whitespace; never duplicate them.

### Examples

- Read `examples/01-claude-plugin-bundle.md` when curating release notes for a Claude plugin release bundle.
- Read `examples/02-python-library-bundle.md` when curating release notes for a Python library with multiple audience tracks.
- Read `examples/03-rerun-update-in-place.md` when re-running the skill on an existing draft to update the augmentation block in place.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/release-notes-curate/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Source triangulation

Per `spec/claude/research-triangulate/`, before this skill writes any **repo-external assertion** into the release notes — an upstream version, a migration-guide link, a breaking-change claim, or an external product name — triangulate it instead of trusting a single source:

- **Independent sources by blast radius.** At least two independent sources; **at least three** (the Release/dispatch tier) when the assertion will direct a write outside the working copy (a version pin, a sister-repo path, a third-party API signature, an external tool default).
- **Record provenance.** For every source record the URL or path, the source class, and the retrieval date in the notes' source list or an associated `.audits/release-notes-curate/<run>/` findings file; at least one source SHOULD carry a verifiable date so a stale link or version is detectable.
- **Surface conflicts, never silent-vote.** When sources disagree, name the most likely explanation and let the operator decide; never apply a majority vote or auto-pick by source class.
- **Mark `unverified` when under-triangulated.** If the required source count is unreachable, mark the assertion `unverified` and hand back to the operator; in an autonomous run with no reachable operator, abort the write and persist the conflict as a findings report.

### Hard rules

- Never write to a release outside the open `release-drafter` draft on the default branch.
- Never call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id>` with `draft=false`, or any other body that flips the draft state from this skill.
- Never invent audience entries inline — missing audiences become `## Open questions` notes, not fabricated content.
- Never modify content outside the marker boundaries on re-runs. `release-drafter` owns the body above the markers; this skill owns only the augmentation block.
- Never write a second marker pair, append the augmentation outside the markers, or duplicate sections.
- Never write template content in a language other than English.
- Never proceed to a write without explicit operator confirmation of the disclosed diff.
- When `spec/project/release-skill-layer/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
