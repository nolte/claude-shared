# Release-Notes Audiences — `nolte-shared` plugin (this repository)

<!--
Produced following spec/project/release-notes-audience-analysis/, which applies
the audience-identification method (spec/project/audience-identification/) to the
bounded context "release notes of a GitHub release of this project."

This is a dedicated audience artifact for the RELEASE-NOTES sub-context only. It
does NOT restate the whole-plugin audience list in AUDIENCES.md — that artifact
declares the plugin itself as its bounded context. Per
release-notes-audience-analysis §Non-Goals, this spec declares no new location
rule and inherits audience-identification's accepted locations; a dedicated
`docs/release-audiences.md` is one of the named alternatives (also referenced by
release-skill-layer §Requirements as the artefact release-notes-curate consumes).

Per-audience fields follow audience-identification §Requirements (label,
relationship category, interaction surface, expectation, track, confirmed/assumed,
criticality) plus the release-notes content dimensions required by
release-notes-audience-analysis §Requirements (release-drafter section/category,
detail depth, language register, CTA, machine-readability).
-->

## Bounded context

This artifact's bounded context is **the release notes of a GitHub release of
`nolte/claude-shared`** — the body of each `release-drafter` draft that is
published through `release-publish.yml` (per `spec/project/release-automation/`)
and surfaced on the repository's GitHub Releases page and release feed. It is a
*sub-context* of the whole-plugin context declared in `AUDIENCES.md`: that
artifact answers "who consumes the plugin," whereas this one answers "who reads a
release's notes and what they need from them."

**What is inside this context**: the human-readable and machine-parseable content
of a published release — section structure, per-entry detail depth, language
register, calls-to-action, and the stable category names / PR references /
SemVer labels a machine consumer parses.

**What is explicitly outside**:

- The publish *mechanics* — `release-automation` governs the Draft → Published
  transition and is not re-specified here.
- The plugin's runtime interaction surfaces (slash commands, agents, MkDocs
  site) — those belong to `AUDIENCES.md`.
- Versioning / cadence policy (inherited from `branching-model` and
  `release-drafter` configuration).
- The code-level security review — delegated to the diff-scoped `security-review`
  skill during the PR-merge flow; this context only owns the *content coverage*
  of a security-disclosure audience (advisory pointer, CVE IDs), per
  `release-notes-audience-analysis` §Requirements.

This context is forward-only: this list governs release notes from the first
release published after adoption; already-published notes are an immutable
audit-trail artifact and are not re-audited against it.

## Release-notes audiences

Each entry records: label · `id` · relationship category · interaction surface ·
expectation · documentation `track` · `confirmed`/`assumed` · criticality. Each
also records the **content dimensions** it drives: the `release-drafter`
section/category that must exist, detail depth, language register, call-to-action,
and machine-readability constraints. The eight candidate audiences mandated by
`release-notes-audience-analysis` §Requirements are each evaluated below
(concrete entry or "not applicable" with reason).

### Direct consumers (readers of the notes)

- **Upgraders — downstream repos pinning `nolte-shared`** — _id_:
  `rel-upgrader` · _category_: direct-consumer · _track_: `developer-docs` ·
  _surface_: the GitHub release body and the `marketplace.json` / `plugin.json`
  version bump a consumer follows when moving between plugin versions ·
  _expects_: breaking-change callouts for renamed/removed slash commands, agents,
  or spec requirements, plus what to change locally · _status_: `confirmed`
  (validated 2026-05-11 by the author's own dogfood upgrade of `claude-shared`
  against its own plugin version) · _criticality_: **primary**
  - Content dimensions:
    - section: a `## Breaking Changes` / `⚠ Breaking` category MUST exist
      whenever a release renames or removes a command, agent, or spec MUST.
    - detail depth: each breaking entry links the changed spec/skill and states
      the migration step (one-line summary + linked artefact), not just a PR
      title.
    - language register: developer vocabulary (command names, spec IDs).
    - CTA: "bump the marketplace pin / re-run `/reload-plugins`" and a link to
      the changed spec.
    - machine-readability: stable `Breaking Changes` category name.

- **New adopters — repos discovering the plugin via a release tag** — _id_:
  `rel-new-adopter` · _category_: direct-consumer · _track_: `user-docs` ·
  _surface_: the release feed / marketplace listing and the release body read on
  first install · _expects_: a one-paragraph "what this release adds" framing and
  an install pointer · _status_: `assumed` · _criticality_: secondary
  - Content dimensions:
    - section: a `## Features` / `## What's Changed` summary category.
    - detail depth: one-line summary per landed capability.
    - language register: end-user / adopter vocabulary.
    - CTA: install/marketplace pointer.
    - machine-readability: stable `Features` category name.

- **Integrators — authors of downstream specs/skills tracking contract changes**
  — _id_: `rel-integrator` · _category_: direct-consumer · _track_:
  `developer-docs` · _surface_: the release body, read for changes to
  spec requirements, skill hard rules, and agent contracts other repos depend on
  · _expects_: a per-release delta of changed spec MUSTs and command signatures ·
  _status_: `assumed` · _criticality_: secondary
  - Content dimensions:
    - section: `## Spec & contract changes` (or folded into Breaking Changes when
      breaking).
    - detail depth: linked spec file + the changed requirement.
    - language register: developer vocabulary.
    - CTA: link to the spec diff.
    - machine-readability: stable PR-reference format so the delta is traceable.

### Operators

- **Operators / SREs** — _id_: `rel-operator` · _category_: operator · _track_:
  `developer-docs` · _status_: **not applicable** — reason: `nolte-shared` is a
  Claude Code plugin (skills/agents/specs), not a deployed service. It has no
  runtime to operate, no config to roll back, and no operational-impact surface
  in a release. CI/release-automation impact for *this* repo is owned by the
  `ci-operator` / `maintainer` entries in `AUDIENCES.md`, not by the release
  notes a downstream reads.

### Downstream packagers / distributors

- **Downstream packagers / distributors** — _id_: `rel-packager` · _category_:
  direct-consumer (republisher) · _track_: `developer-docs` · _status_: **not
  applicable** — reason: the plugin is distributed solely through the Claude Code
  plugin marketplace from this repo; it is not published to npm/PyPI/HACS/OS
  package registries and is not republished by third parties. Re-evaluate if the
  plugin is ever mirrored to a package registry (a recorded revisit trigger).

### Security-sensitive audiences

- **Security / CVE trackers** — _id_: `rel-security` · _category_: governing-party
  · _track_: `developer-docs` · _surface_: the release body as the disclosure
  channel for any security-relevant change in a skill, agent, or generated
  config · _expects_: an advisory pointer and CVE IDs when a release fixes a
  security-relevant defect · _status_: `assumed` · _criticality_: **primary**
  (ranked primary per `release-notes-audience-analysis` §Requirements because
  the plugin's scope — skills that scaffold configs and run `gh`/git — can
  produce security-relevant change, and release notes are the canonical
  disclosure channel)
  - Content dimensions:
    - section: a `## Security` category MUST exist whenever a release carries a
      security-relevant fix.
    - detail depth: advisory link + CVE/GHSA ID + affected versions.
    - language register: security/compliance vocabulary.
    - CTA: link to the GitHub Security Advisory.
    - machine-readability: CVE-/GHSA-ID format kept stable for trackers.
    - release-time obligation: this audience's content dimensions are verified
      before `release-publish.yml` is dispatched (per §Acceptance Criteria); the
      code-level review stays delegated to `security-review`.

### Automated consumers

- **Renovate (the portfolio dependency bot)** — _id_: `rel-renovate` ·
  _category_: direct-consumer (machine) · _track_: `developer-docs` · _surface_:
  the release body embedded into the dependency-bot PR that downstream repos
  receive when they bump the plugin pin · _expects_: a parseable category
  structure and stable section names so the bump PR body renders the change
  summary · _status_: `assumed` — validation per
  `release-notes-audience-analysis` §Requirements flips this `confirmed` by
  inspecting one incoming Renovate PR body and observing which fields it parsed
  (manual enumeration of the known bot set, not a GitHub subscriber audit) ·
  _criticality_: **primary**
  - Content dimensions / **stability expectation** for parsed fields:
    - section / category **names** are stable: `Features`, `Breaking Changes`,
      `Security` are not renamed between releases.
    - **PR-reference format** is stable (`(#NNN)` autolinks as emitted by
      `release-drafter`).
    - **SemVer label** in the tag is stable (`vX.Y.Z`).
    - detail depth: one-line per entry is sufficient for the bot.
    - language register: none (machine).
    - CTA: none (machine).

- **GitHub release-feed / Atom readers and release-tracking services** — _id_:
  `rel-feed-reader` · _category_: direct-consumer (machine) · _track_:
  `developer-docs` · _surface_: the repo's release Atom feed · _expects_: a
  stable title (the tag) and a body whose category structure does not churn ·
  _status_: `assumed` · _criticality_: peripheral
  - Content dimensions / stability expectation: stable tag-as-title (`vX.Y.Z`)
    and the same stable category names as `rel-renovate`; no per-release CTA or
    register requirement.

### Contributors and maintainers

- **Repo maintainer (nolte)** — _id_: `rel-maintainer` · _category_: contributor
  · _track_: `developer-docs` · _surface_: the draft release body reviewed before
  dispatching `release-publish.yml` · _expects_: every PR since the last release
  is attributed and categorised so the draft can be reviewed against this list
  before publish · _status_: `confirmed` (the maintainer is the operator of the
  release decision) · _criticality_: secondary
  - Content dimensions:
    - section: an attribution / `## What's Changed` listing with PR references.
    - detail depth: PR title + author + PR link.
    - language register: developer vocabulary.
    - CTA: none.
    - machine-readability: PR-reference format consistent with `release-drafter`.

### Indirect audiences

- **End users of downstream projects** — _id_: `rel-downstream-end-user` ·
  _category_: indirect · _status_: **not applicable** — reason: end users of a
  downstream product never read this plugin's release notes; the disclosure
  channel they see is the downstream project's own release notes. Mirrors the
  `downstream-end-user` reasoning in `AUDIENCES.md`.

## release-drafter category ↔ audience traceability

Per `release-notes-audience-analysis` §Acceptance Criteria, every configured
`release-drafter` category must trace back to at least one audience here:

| release-drafter category | serves audience(s) |
| --- | --- |
| Breaking Changes | `rel-upgrader`, `rel-integrator` |
| Security | `rel-security` |
| Features / What's Changed | `rel-new-adopter`, `rel-maintainer`, `rel-renovate`, `rel-feed-reader` |
| Spec & contract changes | `rel-integrator` |

When `release-drafter.yml` is next configured or materially changed, every
category it declares MUST appear in this table (add the row) and every row here
SHOULD have a backing category; categories no audience needs are removed.

## Revisit triggers

- The plugin is mirrored to a package registry (npm/PyPI/HACS) or republished by
  a third party — flips `rel-packager` from "not applicable" to a real entry.
- A new automated consumer (e.g. Dependabot) starts tracking the plugin — add it
  to the automated-consumer set.
- `release-drafter.yml` gains or renames a category — reconcile the
  traceability table and notify `rel-renovate` / `rel-feed-reader` stability
  expectations.
- A security-relevant release is published — validate `rel-security` content
  coverage and flip toward `confirmed` once exercised.
- `spec/project/release-notes-audience-analysis/` or
  `spec/project/audience-identification/` materially changes its requirements.
