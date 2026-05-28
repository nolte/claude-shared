# Signal-source map

Load this file when running the Capture / Refresh operation step 3 (probe repository signals). It carries:

1. the per-signal mapping table (which file or section produces which candidate),
2. the deterministic `group:` proposal rules (step 5),
3. the deterministic `lifecycle:` proposal rules (step 6),
4. the `version:` extraction rules.

Authority: this file reproduces the rules declared in `spec/portfolio/tech-stack-discovery/<canonical_language>.md` §Discovery sequence per repository and the kind / group enums declared in `spec/portfolio/tech-stack/<canonical_language>.md`. When this file disagrees with either spec, the spec wins.

## Table of contents

- [Signal-source map](#signal-source-map)
  - [Table of contents](#table-of-contents)
  - [Per-signal mapping](#per-signal-mapping)
  - [Deterministic group proposal](#deterministic-group-proposal)
  - [Deterministic lifecycle proposal](#deterministic-lifecycle-proposal)
  - [Version extraction](#version-extraction)
  - [Source-of-truth path conventions](#source-of-truth-path-conventions)

## Per-signal mapping

The probe reads each signal file at most once. A missing file is an absence (no candidate emitted), not an error. Multiple signals can produce the same candidate name; the first hit owns the `source_of_truth:` path, later hits don't duplicate the candidate.

| Signal file / section                          | Candidate `name`     | `kind`            | Default `group`   | Default `lifecycle` | Notes                                                                                                            |
| ---------------------------------------------- | -------------------- | ----------------- | ----------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `pyproject.toml` (any)                         | `python`             | `language`        | *ask*             | *ask*               | Group depends on whether Python is the application runtime or a docs-only helper; ask the operator.              |
| `pyproject.toml:[project].requires-python`     | `python`             | `language`        | *ask*             | *ask*               | Version: copy the requires-python pin verbatim when present.                                                     |
| `requirements*.txt` (incl. `docs/requirements*.txt`) | `python`       | `language`        | *ask*             | *ask*               | Plain pip-style requirements file; emits a `python` candidate when no `pyproject.toml` is present.               |
| `pyproject.toml:[tool.uv]` or `uv.lock`        | `uv`                 | `package-manager` | `build-tooling`   | `development`       | The lockfile presence is the stronger signal; `[tool.uv]` alone still emits the candidate.                       |
| `pyproject.toml:[tool.poetry]` or `poetry.lock`| `poetry`             | `package-manager` | `build-tooling`   | `development`       | Mutually exclusive with `uv` in the same repo; flag both as a `Warning` if both signals fire.                    |
| `pyproject.toml:[tool.ruff]`                   | `ruff`               | `lint`            | `quality`         | `development`       | A `[tool.ruff.lint]` table is sufficient; an empty `[tool.ruff]` table is not a signal.                          |
| `package.json`                                 | `node`               | `runtime`         | *ask*             | *ask*               | Ask group/lifecycle: Node may be the application runtime or only the docs-build helper.                          |
| `package.json:engines.node`                    | `node`               | `runtime`         | *ask*             | *ask*               | Version: copy the engines.node range verbatim when present.                                                      |
| `package-lock.json`                            | `npm`                | `package-manager` | `build-tooling`   | `development`       | Mutually exclusive with `pnpm` / `yarn` in the same repo.                                                        |
| `pnpm-lock.yaml`                               | `pnpm`               | `package-manager` | `build-tooling`   | `development`       |                                                                                                                  |
| `yarn.lock`                                    | `yarn`               | `package-manager` | `build-tooling`   | `development`       |                                                                                                                  |
| `Taskfile.yml`                                 | `task`               | `build`           | `build-tooling`   | `build`             | The task orchestrator. Matches the global entry of the same name; usually drops into the inherited-confirmed set.|
| `.github/workflows/*.yml` (any)                | `github-actions`     | `ci`              | `automation`      | `build`             | At least one workflow file is sufficient; presence of the directory alone with zero workflows is not a signal.   |
| `renovate.json5` or `renovate.json`            | `renovate`           | `dep-bot`         | `automation`      | `development`       | Matches the global entry.                                                                                        |
| `.github/dependabot.yml`                       | `dependabot`         | `dep-bot`         | `automation`      | `development`       | Mutually exclusive with `renovate` in the same repo; flag both as a `Warning` if both signals fire.              |
| `mkdocs.yml`                                   | `mkdocs`             | `docs`            | `documentation`   | `build`             | Matches the global entry.                                                                                        |
| `.vale.ini` or `vale.ini`                      | `vale`               | `lint`            | `documentation`   | `development`       | Vale targets prose; group is `documentation`, not `quality`.                                                     |
| `.markdownlint*.{json,yml,yaml}`               | `markdownlint`       | `lint`            | `documentation`   | `development`       | A `.markdownlint-cli2.*` config also counts.                                                                     |
| `.pre-commit-config.yaml:repos[].hooks[].id == markdownlint` | `markdownlint` | `lint`        | `documentation`   | `development`       | Inline-in-pre-commit hook fallback when no standalone `.markdownlint*` config exists; a `.markdownlintignore` alone is not a signal but is a hint to also look at the pre-commit hook list. |
| `.pre-commit-config.yaml`                      | `pre-commit`         | `lint`            | `quality`         | `development`       | The framework, not its hooks; per-hook entries are not emitted here except for the markdownlint fallback above.   |
| `.tool-versions`                               | one per declared row | varies            | varies            | varies              | One candidate per row; the row name maps to a name in the kind enum (`python`, `node`, `golang`, …).             |
| `.claude-plugin/plugin.json`                   | `claude-code-plugin` | `framework`       | `plugin-platform` | `build`             | Confirms the repo is a Claude Code plugin source tree; matches the global entry of the same name.                |
| `.claude-plugin/marketplace.json`              | `claude-code`        | `runtime`         | `plugin-platform` | `runtime`           | Confirms the marketplace distribution channel; matches the global entry of the same name.                        |
| `.github/release-drafter.yml`                  | `release-drafter`    | `other`           | `automation`      | `build`             | Matches the global entry.                                                                                        |
| `.github/settings.yml`                         | `probot-settings`    | `other`           | `automation`      | `development`       | Probot Settings app config; matches the global entry.                                                            |
| `.github/boring-cyborg.yml`                    | `boring-cyborg`      | `other`           | `automation`      | `development`       | Matches the global entry.                                                                                        |
| `.github/stale.yml`                            | `stale-bot`          | `other`           | `automation`      | `development`       | Matches the global entry.                                                                                        |

A signal not in this table doesn't produce a candidate. Adding a new row is a coordinated edit of this file plus a one-sentence rationale in the PR body; don't ship a candidate-emitting probe without the table row to document it.

**`kind: deploy-target` is operator-curated, never auto-emitted.** Deploy targets (a GitHub Pages site, a PyPI package, a Docker image, a Claude Code marketplace channel) are too repo-specific to derive from a single signal file: the same `.github/workflows/release-cd-deliver-docs.yml` could deliver to GitHub Pages, Netlify, or S3 depending on the workflow body. The skill therefore doesn't emit any `kind: deploy-target` candidate from the probe; the operator authors these `additions[]` entries by hand in the step-7 confirmation pass. An existing `kind: deploy-target` addition presented during a refresh is preserved per the Gotcha "Refresh preserves operator-edited entries that survived a prior round".

## Deterministic group proposal

Per `spec/portfolio/tech-stack/` §Group enum, every entry carries exactly one `group` value from the closed five-value set: `documentation` / `quality` / `automation` / `build-tooling` / `plugin-platform`. The discovery spec §Discovery sequence per repository defines the default mapping from `kind:` to `group:`. The skill auto-fills the default when the table above declares one, and asks the operator when the table marks the cell *ask*.

Auto-fill rules (default mapping, reproduced from the discovery spec):

- `docs` → `documentation`
- `test` → `quality`
- `lint` running against doc sources → `documentation`; otherwise → `quality` (the `source_of_truth:` path decides — `.vale.ini` and `.markdownlint*` default to `documentation`, everything else under `pyproject.toml`, `.pre-commit-config.yaml` defaults to `quality`)
- `ci` → `automation`
- `dep-bot` → `automation`
- Probot governance bots (`release-drafter`, `probot-settings`, `boring-cyborg`, `stale-bot`) → `automation`
- `build` → `build-tooling`
- `package-manager` → `build-tooling`
- `framework` with `name` matching a Claude Code plugin shape → `plugin-platform`
- `runtime` with `name: claude-code` → `plugin-platform`

Ask-the-maintainer rules (always prompt; never guess):

- `language` — depends on whether the repo ships a service, only docs, or both
- `runtime` (non-`claude-code`) — same reasoning
- `framework` (non-Claude-Code-plugin) — depends on the application shape
- `deploy-target` — depends on whether the target is application delivery or docs publishing
- `other` — depends entirely on the specific entry

Confirmation rule (step 7): even when the auto-fill rule decides, the proposed `group:` is still presented in the per-entry confirmation pass so the operator can override. Auto-fill only removes the upfront question — it doesn't bypass confirmation.

## Deterministic lifecycle proposal

`lifecycle:` is optional. The spec's SHOULD asks the skill to propose a value when the mapping is unambiguous and to ask the operator when it isn't. "Skip" (leaving the field absent) is a legitimate operator answer.

Auto-fill mapping:

- `test`, `lint`, `dep-bot`, `package-manager` → `development`
- `ci`, `build`, `docs` → `build`
- `deploy-target` → `runtime`

Ask-the-maintainer mapping:

- `language`, `runtime`, `framework`, `other` — depend on whether the repository ships a service, only build artefacts, or both. A guessed value would mislead.

## Version extraction

`version:` is optional and descriptive — not enforced and not the place to manage upgrades. Per the discovery spec's SHOULD, pre-populate only when the signal carries an unambiguous version:

- `pyproject.toml:[project].requires-python` → `python` candidate's `version`
- `package.json:engines.node` → `node` candidate's `version`
- `.tool-versions` row → the row's version literal goes into the matching candidate's `version`

When the signal is ambiguous or absent (a lockfile pinning a transitive dep but not the top-level tool, a `pyproject.toml` without `requires-python`, a `package.json` without `engines.node`), leave `version:` blank. Don't guess.

## Source-of-truth path conventions

`source_of_truth:` carries a repository-relative path to the strongest signal that justified the candidate. The skill picks the path per these conventions:

- For tool-config signals (e.g. `mkdocs.yml`, `.vale.ini`, `renovate.json5`), the config file path itself.
- For lockfile-or-config-section pairs (e.g. `uv.lock` plus `[tool.uv]`), the lockfile wins because it's the unambiguous tie-breaker for "is this tool actually managing dependencies".
- For workflow-directory signals (`.github/workflows/`), the directory path with the trailing slash, never an individual workflow file (the audit checks for "at least one workflow file present", not for a specific one).
- For per-row signals out of `.tool-versions`, the file path (`.tool-versions`) — the row is referenced by name elsewhere in the entry, not by line number.

The path stays forward-slash regardless of host OS, per `spec/claude/skill-management/` §Authoring quality.
