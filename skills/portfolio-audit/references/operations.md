# Portfolio-audit — operation runbooks

Detailed step-by-step procedures for each `portfolio-audit` operation, plus the spec anchors. `SKILL.md` carries the one-line operation summaries and the invariants; this file carries the runbooks. Load the relevant section below when you actually execute that operation.

## Table of contents

- Audit (primary path)
- Render (regenerate the inventory docs)
- Bootstrap (initial portfolio.yml for one repository)
- Discover tech stack
- Reference: spec anchors

## Audit (primary path)

Runs the cross-repository capability audit per `spec/portfolio/portfolio-management/` §Portfolio audit.

1. **Detect Portfolio-Member set** — query the GitHub API for the active set of public, non-archived, non-fork repositories under `nolte` via `gh api users/nolte/repos --paginate --jq '.[] | select(.archived==false and .private==false and .fork==false) | .name'`. `nolte` is a GitHub **user** account, so the `users/nolte/repos` endpoint is authoritative — `orgs/nolte/repos` returns 404. The `.fork==false` filter drops upstream forks, which aren't Portfolio-Members per `spec/portfolio/portfolio-management/` §Portfolio scope. Cross-check each remaining repository for an opt-out marker (`portfolio: excluded` at the top of `CLAUDE.md`); excluded repositories drop out of the audit set with their rationale recorded.
2. **Collect per-repository manifests via agent** — Dispatch `portfolio-manifest-collector` (Agent) to gather manifests from all portfolio members. Wait for its inventory report before proceeding to duplicate-detection and gap-classification. The agent fetches `project/portfolio.yml` for each member via `gh api`, reduces raw YAML to structured per-repository summaries (declared capabilities, audiences, peer references, missing-manifest indicator), and returns the full manifest-inventory report. Repositories without `project/portfolio.yml` produce a `missing-manifest` entry rather than an error.
3. **Run the four checks against the collected summary**:
   - **Manifest presence**: every Portfolio-Member repository ships a `project/portfolio.yml` or has the opt-out marker. Missing manifests on opted-in repositories are `Warning` findings.
   - **Manifest validity**: each manifest parses as YAML and contains the required fields (`name`, `description`, `audience`, `status`, `rationale`) per `spec/portfolio/portfolio-management/` §Capability inventory per repository. Schema violations are `Critical` findings.
   - **Cross-repository duplicate detection**: every pair of capabilities across all manifests gets a semantic-overlap comparison on `description` (not keyword-overlap). Fresh duplicates are `Warning`; duplicates persisting beyond the one-closed-sprint tolerance window are `Critical`. Resolution path is documented in the spec; this skill emits the finding, the operator makes the consolidation PR.
   - **Gap analysis** (three sub-classes per spec):
     - Broken peer reference: a `peers:` entry pointing to a non-existent `<repo>:<capability-name>` is a `Warning`.
     - Spec-demanded gap: a sibling spec under `spec/` declares a capability as a precondition that no manifest provides. `Warning`.
     - Cross-repository copy-paste smell: same workflow file / config block / non-trivial code pattern duplicated across three or more repositories without a corresponding shared capability is a `Suggestion` (under threshold) or `Warning` (at and above the 3-recurrence threshold from `skill-vs-agent` §Portfolio-wide consistency).
   - **Tech-stack consistency** (per `spec/portfolio/tech-stack/` §Portfolio audit integration — verified in this same audit run, never a separate `tech-stack-audit` skill): read the global manifest `portfolio/tech-stack.yml` and each member's `tech_stack:` block from its `project/portfolio.yml`, then classify with the canonical severities:
     - `Critical`: a Portfolio-Member ships its own `portfolio/tech-stack.yml` (forbidden duplication); a per-repo `additions:` entry shadows an inherited entry without a corresponding `overrides:` record; an entry is missing its mandatory `group` field (parse error).
     - `Warning`: an `overrides:` or `regroup:` record references a non-existent global entry; a `regroup:` record's `group` equals the inherited entry's `group` (no-op) or its `rationale` is missing/empty; a `regroup:` record coexists with an `overrides:` record for the same `name` (dead code); a declared `status: active` entry isn't detected in repo signals; a consumer renders documentation HTML without inheriting the global `docs` entry and without an explicit override. **Rationale-downgrade:** a `status: active` entry whose `rationale` carries an acknowledged-missing-signal marker (written by `tech-stack-capture` per `spec/portfolio/tech-stack-discovery/`) is downgraded to `Suggestion`.
     - `Suggestion`: a `deprecated` global entry still inherited after one closed sprint; an `other`-classified entry persisting across two consecutive quarterly audits or 180 days; a `status: experimental` entry not detected in repo signals.
     - `Info`: a global entry with `since` younger than one closed sprint; an experimental entry with no consumer pickup; a `regroup:` record present on a repo.
     - Verify repository signals for at least these kinds: `package-manager` (lockfile / tool-config matching `name`, e.g. `uv.lock`), `ci` (a `.github/workflows/*.yml` for `github-actions`), `dep-bot` (`renovate.json5` for `renovate`), `docs` (`mkdocs.yml` for `mkdocs`), `lint` (`.vale.ini` for `vale`, `pyproject.toml:[tool.ruff]` for `ruff`). A read-only specialist agent MAY be dispatched for per-signal probing of large repositories; orchestration stays in this skill.
4. **Write the Findings-Report** at `.audits/portfolio/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to `spec/claude/review-plan/`:
   - Required sections: `## Scope`, `## Summary`, `## Findings`, `## Tech stack`, `## Processing log`
   - The `## Tech stack` section carries the tech-stack-consistency findings from the same run (per `spec/portfolio/tech-stack/` §Portfolio audit integration), keeping them grouped and traceable alongside the capability findings rather than interleaved; organise it `group`-first per §Group enum. When the run surfaces no tech-stack findings, the section still appears with an explicit "No tech-stack findings" line so a reader knows the check ran.
   - Severity vocabulary: `Critical` / `Warning` / `Suggestion` / `Info` exactly (Title Case, never ALL-CAPS) per `review-plan` §Severity scale
   - Each finding cites the originating spec rule in the bracketed prefix (e.g. `[portfolio-management §Cross-repository duplicate detection]` or `[tech-stack §Portfolio audit integration]`) so a downstream reader can trace it
5. **Confirm in the user's language** with: the path of the new Findings-Report, the per-severity counts, and the next step (typically: open the Findings-Report and start triaging the `Critical`-grade items first via `continuous-improvement`'s specialist-dispatch loop).

Audit operation **never** consolidates duplicates, never deletes capabilities, never opens PRs against Portfolio-Member repositories. It identifies and reports; the operator (or a future remediation skill) acts.

## Render (regenerate the inventory docs)

Regenerates the aggregated portfolio inventory pages under `claude-shared/docs/<lang>/portfolio/`. The mechanism is **two-stage and deterministic**: Render assembles a committed snapshot at `portfolio/aggregate.yml` from the per-repository manifests, and the standalone generator `scripts/docs/gen_portfolio.py` (invoked by `task docs:portfolio`) renders the per-language pages as a pure function of that snapshot. Render writes the snapshot; it **never** hand-writes the `docs/<lang>/portfolio/*.md` pages — the generator owns those, including the Mermaid map, the status badges, and the historical-capabilities appendix.

1. **Manifest collection** — when the same conversation has already collected manifests (operation 1 step 2) within this turn, reuse the cached structured summary; otherwise dispatch `portfolio-manifest-collector` (Agent) afresh to collect the manifests via the same `gh api` flow as operation 1 step 2. Additionally fetch each member's `project/mission.md` and quote its `mission_statement` **verbatim**; when a member has no `project/mission.md`, record an empty `mission_statement` (the generator renders a placeholder) and surface the gap as a `Warning` in the next Audit run per the no-invention hard rule.
2. **Assemble the snapshot** `portfolio/aggregate.yml` in the schema the generator consumes (`schema_version: 1`; a `members:` list; an optional `historical:` list). For each Portfolio-Member, write: `repo` (`nolte/<name>`), `repo_url`, `mission_statement` (verbatim or empty), and a `capabilities:` list carrying each capability's `name`, `description`, `status`, `audience`, and `since`. Derive the member-level `peers:` list from the per-capability `peers:` references in `project/portfolio.yml` (`<repo>:<capability>` shape): collect the distinct **target repositories** that are themselves Portfolio-Members, drop self-references, and emit them as `nolte/<name>` entries (this is what the generator draws as repo-to-repo peer edges). Edit only this snapshot — it is the single source of truth for the render.
3. **Run the generator** with `task docs:portfolio` (equivalently `python3 scripts/docs/gen_portfolio.py`). It deterministically rewrites `docs/<lang>/portfolio/index.md` for every language in `spec/.spec-config.yml`, emitting the per-repository sections, the capability-to-repository Mermaid map (with the `diagram-source` comment per `spec/project/mermaid-diagrams/`), and the historical-capabilities appendix. Do not run `mkdocs-gen-files`-style virtual emission — the repo commits the rendered pages because `mkdocs-static-i18n` (folder strategy) drops virtual files.
4. **Verify** by running `task docs` (mkdocs `--strict`) and then `git diff --exit-code docs/<canonical_language>/portfolio docs/<other_language>/portfolio`. A non-empty diff after a fresh generator run means the committed pages were stale; commit the regenerated pages together with the snapshot. If the strict build fails, surface the error and stop — don't commit broken renders. This mirrors the CI freshness gate (`.github/workflows/ci.yml` → "Verify committed portfolio inventory is fresh").
5. **Confirm in the user's language** with: that `portfolio/aggregate.yml` plus the regenerated `docs/<lang>/portfolio/index.md` pages were written, which Portfolio-Member sections are included, and a one-line note when the rendered output didn't change (the regeneration is idempotent when the snapshot didn't change).

Render operation **never** modifies the source-of-truth manifests, never edits the spec, never publishes the docs (publication is the existing `task docs` / MkDocs pipeline's job), and never hand-edits `docs/<lang>/portfolio/*.md` (only `portfolio/aggregate.yml` is authored; the generator owns the pages).

## Bootstrap (initial portfolio.yml for one repository)

Helps a single Portfolio-Member repository author its first `project/portfolio.yml` interactively.

1. **Check the active repository** is a plausible Portfolio-Member candidate: it lives under `nolte/`, isn't archived, doesn't already carry the opt-out marker, and doesn't already have a `project/portfolio.yml`.
2. **Read the existing context**: `project/mission.md` (the mission statement constrains capability scope per `spec/project/mission/`), the audience artefact per `audience-identification`, and `project/roadmap.md` (active capabilities should align with active roadmap items).
3. **Walk the user through capability identification** — for each candidate capability:
   - Propose `name` (kebab-case, derived from the user's description) and confirm
   - Confirm `description` (one or two sentences naming what + for whom)
   - Map `audience` to entries in the existing audience artefact; new audiences need to be added to `project/audiences.md` first via `audience-identification`, this skill doesn't invent audiences inline
   - Default `status` to `active`; the user can override to `experimental` for early-stage capabilities
   - Collect `rationale` (one or two sentences naming why this repository owns the capability — never accept an empty or template rationale)
   - Optional: collect `peers` (list of `<repo>:<capability-name>` cross-references) and `since` (ISO date)
4. **Write `project/portfolio.yml`** at the repository root with the collected entries. Verify the file parses as YAML before declaring success.
5. **Confirm in the user's language** with: the file path, the capability list as a concise summary, and a follow-up reminder that the next `portfolio-audit` run from the `claude-shared` side will pick up the new manifest.

Bootstrap operation **never** modifies `project/mission.md`, `project/roadmap.md`, or the audience artefact — those are owned by their own dedicated skills and authoring flows. If the user discovers during Bootstrap that their mission or audience list needs updating first, this skill stops and routes them to the appropriate skill.

## Discover tech stack

Runs the tech-stack-discovery methodology from `spec/portfolio/tech-stack-discovery/` against a single repository or across every Portfolio-Member repository.

1. **Determine the scope** the user asked for: single-repo (the active checkout, or a user-supplied path) versus portfolio-wide (every Portfolio-Member repository known via the GitHub API).
2. **For each in-scope repository, read the canonical detection sources** declared in `spec/portfolio/tech-stack-discovery/` (typically `pyproject.toml`, `package.json`, `Taskfile.yml`, `.github/workflows/`, `Dockerfile`, language-specific lockfiles). Don't invent detection sources the spec doesn't sanction.
3. **Extract the tech-stack signal per layer** the spec defines (language runtime, package manager, build tool, lint stack, test stack, CI runner, deployment target, plugin engines, external services). Report the detected value plus the source path and line.
4. **Cross-validate against the portfolio baseline** declared in `spec/portfolio/tech-stack/`. Findings shape:
   - **In-baseline** — the detected value matches what the portfolio baseline ratifies.
   - **Drift** — the detected value diverges from the baseline (`pyproject.toml` pins a Python version different from the baseline, or a Taskfile uses a different lint target).
   - **Net-new** — the detected value isn't in the baseline at all (the repository introduces a tool the portfolio hasn't ratified yet).
5. **Persist the result** under `.audits/tech-stack/<YYYY-Q<n>>.md` (or the per-repo equivalent), conforming to `spec/claude/review-plan/` — the same `## Scope` / `## Summary` / `## Findings` / `## Processing log` section vocabulary and the same canonical severity grammar as the Audit operation's Findings-Report.

Discover-tech-stack is read-only — it doesn't modify the portfolio baseline in `spec/portfolio/tech-stack/`. When the user discovers a net-new tool worth ratifying, this skill stops and routes them to the `spec` skill to propose a baseline extension, rather than silently amending the spec from here.

## Reference: spec anchors

This skill implements rules declared in `spec/portfolio/portfolio-management/`. Read those rules when in doubt:

- §Portfolio scope — defines what counts as a Portfolio-Member repository, including the opt-out marker
- §Capability inventory per repository — defines the `project/portfolio.yml` schema
- §Cross-repository duplicate detection — defines the duplicate semantic-overlap rule and the tolerance window
- §Gap analysis — defines the three gap classes (broken peer reference, spec-demanded gap, copy-paste smell)
- §Portfolio audit — defines this skill's required output shape and integration with `continuous-improvement`
- §Documentation rendering — defines what the rendered inventory under `docs/<lang>/portfolio/` must contain
- §Decision documentation — defines the `rationale` field requirement and the re-allocation atomic-operation rule

The Discover-tech-stack operation implements `spec/portfolio/tech-stack-discovery/`:

- §Detection sources — defines which on-disk files are canonical signals for which stack layer
- §Cross-validation against baseline — defines the in-baseline / drift / net-new finding classes against `spec/portfolio/tech-stack/`
- §Audit persistence — defines the per-repo audit artefact shape under `.audits/tech-stack/`

When the spec disagrees with this skill's instructions, the spec wins. Propose a skill update rather than silently diverging.
