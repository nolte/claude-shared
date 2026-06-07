# Project Release Artifact

Status: draft

## Context

Readers: repo maintainers of hobby-scale nolte projects whose `sprint-review` skill closes sprints by validating an artefact reference, plus the implementing authors writing `sprint-review` and the `release-skill-layer` skills against this taxonomy.

The sibling `sprint` spec mandates that every closed sprint points at a concrete deployable artefact via `artifact_ref` and that this artefact materialises the sprint's `value_statement` for the end user. It deliberately doesn't say what shape that reference takes, what kinds of artefacts are valid for which project type, or how the reference is validated at sprint closure. This spec fills that gap. It defines the **artefact taxonomy** per portfolio project type, the **shape of `artifact_ref`** for each kind, the **validation rules** that `sprint-review` runs at closure, and the **dispatch boundary** to the existing release machinery (`release-automation` for the Draft → Published transition, `release-skill-layer` for operator-side curation and trigger). It doesn't redefine that machinery; it's the layer where sprint-side planning meets release-side execution, and its job is to keep the two from drifting.

## Goals

- Define the per-project-type artefact taxonomy (Claude plugin, Python application, Python library, Node / TypeScript library or app, CLI tool, documentation-only) using the same project-type signals as `github-issue-templates-apply` and `release-skill-layer`, so portfolio behaviour stays consistent.
- Specify the shape of `artifact_ref` per kind (release tag, container-image tag, plugin version, package-manager version, doc-site deploy URL) and which fields a sprint-review **MUST** verify before allowing `review → closed`.
- Specify the dispatch boundary: when sprint-review touches release machinery, it dispatches `release-skill-layer` skills (`release-notes-curate`, `release-publish-trigger`) and **MUST NOT** call `gh release edit --draft=false` or other forbidden paths declared by `release-automation`.
- Specify how out-of-band artefacts (hotfixes, mid-sprint emergency releases) are tracked so they don't pollute the sprint cadence but are still discoverable from the project record.
- Stay portfolio-reusable: every adopting repo can derive its artefact rules from the project-type signal alone, without per-repo configuration beyond what `release-automation` already provides.

## Non-Goals

- Substituting `release-automation`. The Draft → Published transition is its workflow's job; this spec only declares the artefact reference and the validation rules at sprint closure.
- Substituting `release-skill-layer`. Skill A (curation) and Skill B (publish trigger) own the operator-side procedures; this spec only declares when sprint-review **MAY** dispatch them.
- Substituting `release-notes-audience-analysis`. Audience-driven content is its concern; this spec only verifies that an artefact exists and matches its declared shape.
- Replacing CI / CD systems. The artefact's existence and reachability is what matters here, not the build pipeline that produced it.
- Defining the sprint or feature lifecycle. Each is owned by its own sibling spec; this spec only specifies the artefact-side surface.
- Mandating SemVer or any specific versioning policy beyond what `release-drafter` already enforces in the consuming repo.

## Requirements

### Project-type detection

- **MUST** detect the project type using the same signals as `release-skill-layer` and `github-issue-templates-apply`: `.claude-plugin/plugin.json` for Claude plugin, `pyproject.toml` shape for Python application vs library, `package.json` for Node / TypeScript, declared CLI entry for CLI tool, `mkdocs.yml` (or equivalent) for documentation-only.
- **MAY** support a per-repo override at `.github/release-skill-layer.yml` (the same override surface `release-skill-layer` uses) when autodetection misses; **MUST NOT** introduce a new override file.
- **SHOULD** treat hybrid repos (a CLI tool plus its own docs site) as the dominant publishable kind; cross-kind sprints are an open question (see §Open Questions).

### Artefact taxonomy

- **MUST** restrict valid `artifact_ref` shapes per project type to the following table; values outside the table fail sprint-review validation:
  - **Claude plugin**: a plugin version published to the marketplace, formatted as `<plugin-name>@<version>` (for example `nolte-shared@1.7.0`); the version **MUST** match `.claude-plugin/plugin.json` at the artefact's commit, and the version **MUST** be reachable from the marketplace catalog (typically by inspecting `.claude-plugin/marketplace.json` plus a successful resolve via `claude --plugin nolte-shared@1.7.0` or equivalent); a Git tag without a marketplace-resolvable plugin version is insufficient. Until the consuming repository's `release-publish.yml` is confirmed to perform the marketplace-catalog update end-to-end, an out-of-workflow operator step (manual edit of `.claude-plugin/marketplace.json` followed by a commit on `develop`, or an equivalent dispatch) **MAY** satisfy this requirement, **provided** the manual step is recorded in `## Review notes` per §Validation at sprint closure; once the workflow is confirmed end-to-end, the manual fallback **MUST** be removed and a workflow-health finding raised against any sprint that still uses it.
  - **Python application**: a Git tag (`v<semver>`) **and** a container image tag at a published registry path (`ghcr.io/<owner>/<repo>:v<semver>` or equivalent); both **MUST** be set as a list (`artifact_ref: [v0.4.0, ghcr.io/owner/repo:v0.4.0]`), per the list-form rule below.
  - **Python library**: a Git tag `v<semver>` **and** a published distribution reference (PyPI: `<dist-name>==<version>`); both **MUST** be set as a list.
  - **Node / TypeScript library or application**: a Git tag `v<semver>` **and** the published package reference (`<pkg-name>@<version>` for npm-published, or the container image tag when the package is shipped as a runtime image); both **MUST** be set as a list.
  - **CLI tool**: a Git tag `v<semver>`; if the CLI is also distributed as a binary asset or container image, the additional reference **MUST** appear as a list entry.
  - **HACS integration** (Home Assistant Community Store custom component): a Git tag `v<semver>`; the version **MUST** match the `version` field of `custom_components/<name>/manifest.json` at the artefact's commit. The HACS listing URL **MAY** appear as a list entry once the integration is published to HACS itself.
  - **Documentation-only**: a dated deploy URL (`docs.example.com@<YYYY-MM-DD>`); when the docs site is content-addressed, the deploy commit SHA **MAY** appear as a suffix.
- **MUST** support `artifact_ref` as either a single string or a list of strings, per the sibling `sprint` spec. The list form is the standard shape for any project type that ships two or more coupled artefacts in a single sprint (the multi-artefact rows above show this); the list form is also the escape hatch for hybrid project types not in the table when one element matches a row above and the other matches a different row (for example a Python library whose sprint also deploys a docs site: `[v0.4.0, dist@0.4.0, docs.example.com@2026-05-08]`). The cross-row mix **MUST** be declared in `.github/release-skill-layer.yml` as `artifact_kinds: [python-library, documentation-only]` so `sprint-review` knows which validation commands to run.
- **MUST** require, for every shape, that the artefact is independently re-fetchable at the moment of sprint closure (the tag still resolves, the package version still exists, the doc URL still serves the deployed snapshot); reaching for ephemeral build artefacts that GC themselves is forbidden. Long-term re-fetchability after closure (registry rotation, tag deletion months later) is out of scope per the sibling `sprint` spec, which is a separate archival concern of the consuming repo.
- **MUST NOT** accept a bare commit SHA as an `artifact_ref` unless the project explicitly publishes-by-SHA and the publish path is recorded in `.github/release-skill-layer.yml`.

### Validation at sprint closure

- **MUST** run, when `sprint-review` transitions a sprint from `review` to `closed`:
  - parse `artifact_ref` (string or list) according to the detected project type and the optional `artifact_kinds` override in `.github/release-skill-layer.yml`;
  - resolve every component of the parsed reference using the per-kind verification command, namely `git rev-parse <tag>` for Git tags, `gh release view <tag>` for GitHub releases, `docker manifest inspect <image>` for container images, `pip index versions <dist>` for PyPI distributions, `npm view <pkg>@<version>` for npm packages, a HEAD request for doc deploy URLs, and for Claude plugins both `git rev-parse <plugin-version-tag>` plus a marketplace-resolution probe (the exact command depends on the host catalog; for `nolte-shared` this is reading `.claude-plugin/marketplace.json` at HEAD and confirming the plugin version is listed);
  - confirm the resolved artefact's commit (when applicable) equals the sprint's `last_commit` frontmatter field or is reachable from it; the sprint's `last_commit` is the authoritative anchor (set by `sprint-execute` per the sibling `sprint` spec), and a missing or null `last_commit` blocks closure;
  - block the transition if any verification fails, surfacing the failed check verbatim.
- **MUST** confirm that the artefact materialises the sprint's `value_statement`. The check is delegated to the feature whose `verifies_sprint_value` frontmatter field is non-null (per the sibling `feature` spec); when that feature's named acceptance criterion has a verification mechanism that's a CLI command or skill invocation, sprint-review **MAY** be configured to invoke it against the released artefact.
- **MUST** record the validation outcome in the sprint's `## Review notes`, citing the verification commands run and their results (exit codes, key output lines), so the audit trail is in-repo. Because `sprint-review` already runs every per-kind verification command above and therefore holds the exit codes and key output lines, it **SHOULD** populate the artefact-validation block in `## Review notes` automatically from those captured outputs rather than relying on the operator to re-type them; it **MAY** require operator confirmation before writing the populated block.

### Dispatch boundary to release machinery

This is the boundary where sprint-side validation hands off to the release machinery: the Draft → Published workflow governed by [`spec/project/release-automation/`](../release-automation/en.md), and the operator-side curation and trigger skills governed by [`spec/project/release-skill-layer/`](../release-skill-layer/en.md). The two links below are the navigable entry points into those lower specs.

- **MUST**, when the sprint's project type publishes via `release-publish.yml` (typical for Claude plugin, Python library, Node library, CLI tool, HACS integration), allow sprint-review to chain into [`release-skill-layer`](../release-skill-layer/en.md) skills explicitly. This spec is the authority for **which sprint state triggers the dispatch** (`review` reached, artefact validation passed, operator-opt-in given) and for **which skills are the chain points** (`release-notes-curate` for draft body, `release-publish-trigger` for the publish). The sibling `sprint` spec §Dispatch into release machinery is the authority for **how the operator-opt-in is recorded in `## Review notes`** and for the per-sprint persistence rules; that spec **MUST NOT** redefine the chain points or trigger conditions declared here.
- **MUST NOT** call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id> draft=false`, or any other path that flips the draft state outside `release-publish.yml`. The rule comes from [`release-automation`](../release-automation/en.md) and [`release-skill-layer`](../release-skill-layer/en.md) and is non-negotiable here too.
- **SHOULD**, when no draft exists at closure for a publish-via-workflow project, surface a remediation hint (run `release-drafter` re-run, ensure tag is reachable from the default branch) without blocking the sprint closure beyond what the artefact validation already requires.

### Out-of-band artefacts

- **MAY** record artefacts that were published outside of any sprint (emergency hotfixes, security patches, dependency-driven re-releases) under `project/release-artifacts/out-of-band/<NNNN>-<slug>.md`, where `<NNNN>` is a monotonically-assigned out-of-band number distinct from sprint numbering.
- **MUST**, for every out-of-band entry, record the same fields a sprint would carry at closure: `value_statement`, `artifact_ref`, `roadmap_items` (may be empty), `ended` date, and a `rationale` paragraph; the file uses the same artefact taxonomy as sprint-bound artefacts.
- **MUST**, when at least one out-of-band entry exists, maintain a flat index at `project/release-artifacts/out-of-band/INDEX.md` listing every entry by number, date, and one-line summary, so downstream tooling and human readers can discover out-of-band history without walking the directory; the index **MUST** be regenerated on every entry add or remove and **MUST NOT** be edited by hand outside of that regeneration.
- **MUST NOT** count out-of-band artefacts toward sprint cadence; they're discoverable but never satisfy a sprint's `artifact_ref` requirement.
- **MAY** cross-reference an out-of-band entry from the `## Review notes` of the sprint that was active at the time of the out-of-band release; the cross-reference is documentation, not part of the sprint's closure validation.
- Out-of-band artefacts **MUST NOT** retroactively attach to any sprint and don't extend a sprint's `roadmap_items` traceability; the only sprint linkage is the optional documentation-only cross-reference in the active sprint's `## Review notes`.

### Hobby-scale variability

- **MUST NOT** require a release on a fixed cadence; sprints close when their value is delivered, not on a schedule.
- **SHOULD** tolerate sprint closures whose artefact is a doc-site deploy or a config-only change when the project's nature genuinely makes that the user-visible artefact (a documentation-only repo, a hobby-scale infra project where the README **is** the deliverable). The taxonomy already allows it; the spec just records the legitimacy explicitly.
- **MAY** mark a sprint `cancelled` (per the sibling `sprint` spec) if no valid artefact is reachable at closure; cancellation is a first-class outcome, not a forced publish.

## Acceptance Criteria

- [ ] `sprint-review` detects the project type via the same signals as `release-skill-layer` and `github-issue-templates-apply`; the detection step is documented in the consuming skill and verifiable from its transcript. The recognised project types are Claude plugin, Python application, Python library, Node / TypeScript library or app, CLI tool, HACS integration, and documentation-only.
- [ ] Every sprint that reaches `review` carries an `artifact_ref` (string or list) that matches one of the taxonomy shapes for its detected project type, including the multi-artefact list shape for Python applications, libraries, and Node / TypeScript projects; values outside the taxonomy fail sprint-review validation with a verbatim error.
- [ ] Every Claude-plugin sprint's `artifact_ref` resolves to a marketplace-listed plugin version at the artefact's commit; a Git tag without a marketplace-resolvable plugin version fails closure.
- [ ] Every HACS-integration sprint's `artifact_ref` Git tag matches the `version` field of `custom_components/<name>/manifest.json` at that commit.
- [ ] No closed sprint carries a bare commit SHA as `artifact_ref` unless the project explicitly opts in via `.github/release-skill-layer.yml`.
- [ ] Every closed sprint's artefact is re-fetchable at closure: the per-kind verification command succeeds (`git rev-parse`, `gh release view`, `docker manifest inspect`, `pip index versions`, `npm view`, marketplace-resolution probe, or HEAD on the doc URL).
- [ ] Every closed sprint's `artifact_ref` resolves to a commit equal to or reachable from the sprint's `last_commit` frontmatter field; a missing or null `last_commit` blocks closure.
- [ ] No sprint-review run calls `gh release edit --draft=false`, `gh api -X PATCH ... draft=false`, or any equivalent path; grepping the run transcript finds zero hits.
- [ ] When `sprint-review` chains into `release-notes-curate` or `release-publish-trigger`, the chain is explicitly opt-in and recorded in the sprint's `## Review notes` per the sibling `sprint` spec §Dispatch into release machinery.
- [ ] Out-of-band artefacts, when present, live under `project/release-artifacts/out-of-band/<NNNN>-<slug>.md` with the full minimum schema (`value_statement`, `artifact_ref`, `roadmap_items`, `ended`, `rationale`); every entry is reflected in `project/release-artifacts/out-of-band/INDEX.md`, which is regenerated on add or remove and never hand-edited.
- [ ] This spec cross-links downward to `release-automation` (for the Draft → Published workflow it depends on) and to `release-skill-layer` (for the chain points it dispatches) at the relevant boundary points (the validation rules table, the dispatch boundary); the lower specs declare they `MUST` be discoverable as the dispatch target but **MUST NOT** carry an outbound link in the opposite direction.
- [ ] The sibling `sprint` spec cross-links to this spec where it requires `artifact_ref` to be set; the per-kind shape is resolved here, not in `sprint`.

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the per-item decisions and rationale._
