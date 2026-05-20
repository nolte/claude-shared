---
title: github-issue-templates-apply
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# github-issue-templates-apply

_Apply the canonical-language file under spec/project/github-issue-templates/ to a target repository — detect the project type, resolve or dispatch the audience artefact, derive triage questions, and scaffold or update .github/ISSUE_TEMPLATE/ (bug_report.yml, feature_request.yml, config.yml, plus project-type-specific extras) as GitHub Issue Forms. Invoke when the user asks to "generate issue templates for this repo", "scaffold GitHub issue forms", "create bug and feature templates", "set up .github/ISSUE_TEMPLATE", "apply the github-issue-templates spec", or equivalent German-language requests. Don't use for pull-request templates (that's `pull-request-workflow`), CODEOWNERS / SECURITY.md, discussion templates, or generic .github/ scaffolding (that's `project-structure-apply`)._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `scaffolding`
- **Quelle:** [skills/github-issue-templates-apply/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/github-issue-templates-apply/SKILL.md)

---

## GitHub Issue Templates Apply

Operationalises `spec/project/github-issue-templates/<canonical_language>.md` against a target repository: classifies the project type, reads or produces the audience artefact, derives the triage-question set, and writes `.github/ISSUE_TEMPLATE/*.yml` plus `config.yml` as GitHub Issue Forms — atomically and only after explicit user confirmation of the derivation.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Issue-Templates für dieses Repo erzeugen"
- "GitHub-Issue-Forms anlegen"
- "Bug- und Feature-Template scaffolden"
- "spec github-issue-templates anwenden"

### Why this is a skill, not an agent

- **Per-template user approval is the contract** — the spec mandates that the derivation (project type, audiences, chosen templates, project-specific fields) is surfaced and confirmed before any file is written; an agent's fire-and-forget shape would lose that gate.
- **Output flows back into the main conversation** — the project-type classification, the chosen field set per template, and the drift report on re-runs all surface in the conversation so the user can correct them; isolating them in a structured-report boundary would obscure the per-decision approval surface.
- **Orchestrator role** — when no audience artefact exists, this skill dispatches the `audience-identify` skill before generating templates; the skill-orchestrates pattern (per `skill-vs-agent`) defaults the orchestrator to skill form.
- Counter-dimension considered: a narrow YAML-form-generator agent could specialise on Issue Forms syntax, but the load-bearing dimension is the multi-step approval dialogue (project type → audience → chosen templates → fields → write), not the YAML mechanics — skill wins.

### User-language policy

Detect the user's language and respond in it. Generated `.github/ISSUE_TEMPLATE/*.yml` and `config.yml` content (including comments inside the YAML) is always written in **English**, regardless of the repo's documentation language — the GitHub issue UI is English-only in practice and translating template strings makes them mismatch the surrounding chrome. The spec's "Storage and format" requirements pin this rule.

### Preconditions

Before doing anything:

- Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
- Locate `spec/project/github-issue-templates/` — either in the target repo or, when absent, via the `nolte-shared` plugin install path. If neither is reachable, stop and ask the user which spec source to use; do not improvise requirements.
- Check for uncommitted changes under `.github/ISSUE_TEMPLATE/`. If dirty, report and ask whether to stash, commit, or abort — never overwrite uncommitted work.
- Verify that `pull-request-workflow` is in scope for PR-template authoring and that this skill stays away from `.github/pull_request_template.md`, `CODEOWNERS`, `SECURITY.md`, `SUPPORT.md`, and `.github/DISCUSSION_TEMPLATE/`.

### Operations

Operations 3 to 5 form a stacked Plan-validate-execute cycle: Operation 3 self-validates the working set against the strictness profile before disclosure, Operation 4 surfaces the plan for explicit user confirmation, and Operation 5 writes atomically with rollback on partial failure. Operation 6 closes the loop on re-runs by detecting drift instead of silently overwriting.

#### 1. Detect project type

Walk the spec's six derivation signals in order; stop at the first match. Read these files via the standard read tools, never via heuristics on filenames alone:

1. **Claude Code plugin** — `.claude-plugin/plugin.json` exists; top-level `skills/` and/or `agents/` folder present.
2. **Python application** — `pyproject.toml` declares `[project.scripts]` (or equivalent application entry point) and **does not** declare distributable library metadata (`[tool.hatch.build.targets.wheel]`, `[project]` `classifiers` containing `Topic :: Software Development :: Libraries`, etc.).
3. **Python library** — `pyproject.toml` declares a distributable package without an application entry point.
4. **Node / TypeScript library or app** — `package.json` exists; library bias when `main` / `exports` is set, app bias when `bin` / `scripts.start` is set. Both can hold; record the dominant one.
5. **CLI tool** — declared CLI entry point in `pyproject.toml` (`[project.scripts]`), `package.json` (`bin`), or `Cargo.toml` (`[[bin]]`).
6. **Documentation-only repo** — `mkdocs.yml`, `docusaurus.config.*`, or similar exists with no application source.

Edge handling:

- **Hybrid repos** (CLI tool that's also a library, monorepo with multiple package roots): record both classifications and ask the user which audience drives the issue templates. Do not silently pick one.
- **Hardware-touching applications** (cameras, sensors, robotics, embedded — for example `kamerplanter`): in addition to the Python-application bundle, the spec requires hardware fields (model, firmware). Detect via the presence of references to hardware libraries (`gphoto2`, `picamera2`, `pyserial`, `RPi.GPIO`, `smbus`, `pyudev`) in `pyproject.toml` / `requirements*.txt` or via the user's confirmation.
- **Unknown** — if no signal matches, stop and ask the user to declare the project type explicitly. Never proceed with a generic fallback set.

#### 2. Resolve audience profile

The spec requires an identified *reporter* audience and *triager* audience before fields are derived.

- If the repository already has an audience artefact (per `audience-identification` — typically `AUDIENCES.md`, an "Audiences" section in `README.md`, or an ADR), read it and confirm it covers reporters and triagers. Grep for `AUDIENCES.md` and for headings matching `Audiences` / `Intended consumers`.
- If no artefact exists or it doesn't cover reporters and triagers, dispatch the `audience-identify` skill to produce one before continuing. Do not invent audiences inline; the spec forbids it.
- When the artefact exists but is older than the most recent material change to the repo (new public API, new deployment target, new regulated data class), prompt the user to run `audience-identify` in `revisit` mode before continuing — stale audiences silently invalidate the derived field set.

#### 3. Derive templates and fields

For each baseline template plus any project-type-specific extras, list the questions a triager will ask within the first five minutes after the issue arrives. Those questions become required Issue Forms fields.

Read `references/project-type-fields.md` when deriving project-type-specific fields — it bundles the canonical extra components per project type (Claude plugin, Python application, Python library, Node / TypeScript, CLI tool, documentation-only) and keeps the SKILL.md compact.

When the user has confirmed the project type and audiences, build the working set:

- **Baseline (every project type)**: `bug_report.yml` + `feature_request.yml`.
- **Documentation-only repos**: replace `bug_report.yml` with `documentation.yml`; keep `feature_request.yml` only when the repo accepts content suggestions.
- **Project-type extras**: append fields from the matching bundle in `references/project-type-fields.md`. Do not copy a bundle that does not match the project type.
- **Audience-derived extras**: when the audience artefact lists a triager group whose triage questions are not yet covered (for example "compliance reviewer" expecting a regulated-data-class dropdown), add a field for it explicitly and record the audience entry that motivates it.

Encode each question with the minimum component complexity that fits (`input`, `textarea` with `render: shell` for logs, `dropdown` with concrete values, `checkboxes` for multi-select and acknowledgement gates). Do not add an "Other / please specify" option to dropdowns — it makes the field useless for triage filtering.

Always include a single required search-before-filing acknowledgement at the top of every form (the templates in `templates/` already carry one).

**Per-template strictness profile** (per spec §"Field hygiene"):

- **Bug reports are strict.** Mark every field a triager needs as `required: true`. `dropdown` and `checkboxes` are encouraged for operational choices because they let triage filter on the values.
- **Feature requests are deliberately permissive.** A `feature_request.yml` MUST end up with at most two required fields total — the search-before-filing acknowledgement and exactly one substantive `textarea`. Project-type extras from `references/project-type-fields.md` and audience-derived extras MUST stay optional on the feature template, even when the same field is required on the matching bug template. Never require severity, priority, target release, milestone, or owner — those are maintainer triage decisions, not reporter inputs at filing time.

Before moving to step 4, run a self-validation pass against the working set: count required fields per template, confirm the substantive required input on `feature_request.yml` is a `textarea`, and confirm no closed-taxonomy field is `required: true` on the feature template. If any of these fails, fix the working set; do not surface a non-conforming plan to the user.

#### 4. Disclose the plan and confirm

Before writing any file, surface the derivation to the user as a single block:

- detected project type (with the signal that matched);
- audience artefact path and the reporter / triager audiences it pinned;
- list of templates to be written, with their filenames;
- per template, the project-type-specific and audience-derived fields beyond the baseline;
- the planned `config.yml` shape (`blank_issues_enabled` value, any `contact_links`);
- the labels and assignees pre-fill, with the source taxonomy (`.github/labels.yml`, Probot `settings.yml`, or `none`).

Block writing until the user confirms — either "apply all" or per-template approval. Do not write a partial set on partial approval; the spec mandates an atomic apply (see Hard rules).

#### 5. Apply

When the user has confirmed, write `.github/ISSUE_TEMPLATE/` in a single operation:

- Use `templates/bug_report.template.yml` as the starting point when scaffolding a fresh `bug_report.yml`.
- Use `templates/feature_request.template.yml` as the starting point when scaffolding a fresh `feature_request.yml`.
- Use `templates/config.template.yml` as the starting point when scaffolding a fresh `.github/ISSUE_TEMPLATE/config.yml`.
- Append the project-type-specific and audience-derived fields from step 3 to each template's `body:` list, after the baseline fields.
- Pre-fill `labels:` from the repo's label taxonomy when one exists; leave the array empty (not omitted) when none does. Pre-fill `assignees:` only when the repo has a documented stable triage owner — never default to the latest committer.
- Set `blank_issues_enabled: false` in `config.yml` unless the user has explicitly opted in to blank issues.
- Record the applied derivation as a YAML comment block at the top of `config.yml` (project type, audience artefact path and date, list of generated templates, hash or short identifier of the audience set) so the next run can detect drift without re-asking the user from scratch.

Atomicity: hold every file write until the full set is ready, then write them in one batch. If any single write fails, roll back by deleting the partially written files so the directory never lands in a half-configured state.

#### 6. Re-audit and drift detection

Re-running the skill on a repo that already has templates **MUST** detect drift, not silently overwrite:

- **Project-type drift** — the previously recorded project type no longer matches the current detection (for example a CLI repo grew into a library). Surface the diff and ask whether to migrate or keep.
- **Audience drift** — the audience artefact's identifier in `config.yml`'s comment block differs from the current artefact. Surface which audiences are new or gone and which fields they motivated.
- **Field drift** — a template is missing a required field that the current derivation says it should carry, or carries a stale field whose audience entry is gone. Surface a per-field diff.
- **Strictness drift** — `feature_request.yml` has accumulated more than two required fields, the substantive required input is no longer a `textarea`, or a closed-taxonomy field has been raised to `required: true`. Surface as a strictness-cap violation and propose downgrades to optional.
- **Format drift** — a template uses Markdown (`.md`) instead of Issue Forms (`.yml`) for structured input. Propose a migration; do not auto-rewrite.

Present the diff and ask per-item ("apply", "skip", "skip and remember"). After applied changes, re-read `.github/ISSUE_TEMPLATE/` end-to-end and confirm no `.md` issue templates remain (except purely informational stubs the user explicitly kept).

A clean re-run on a conformant repo MUST produce no diff.

### Gotchas

- The GitHub issue UI is English-only in practice. Even when the repo's docs are in another language, the templates stay English; mixing languages produces visibly inconsistent forms (translated form labels next to English chrome).
- `blank_issues_enabled` defaults to `true` when the key is absent. Always write the key explicitly, even when setting it to `true`, so the intent is visible and the `config.yml` survives audits.
- Issue Forms files MUST live directly under `.github/ISSUE_TEMPLATE/`, never in a subdirectory — GitHub does not recurse the folder. The folder name is case-sensitive (`ISSUE_TEMPLATE` in upper case); filenames inside it are not.
- Templates only become visible to reporters once the file is on the repository's **default branch**. Templates merged onto a feature branch are inert; the chooser only reads the default branch's `.github/ISSUE_TEMPLATE/`.
- Bug-report and feature-request templates use the same Issue Forms YAML schema and the same directory, but the strictness profiles diverge: bug reports want every field required, feature requests want the opposite. Copy-pasting bug-style required fields into the feature template is a common spec violation — the per-template strictness rule in step 3 catches it.
- Pre-filling `assignees:` looks helpful, but if the named user is unavailable (vacation, role change), every newly filed issue silently lands on a stale owner. Pre-fill only when the repo has a documented stable triage rota.
- `dropdown` options with an "Other / please specify" entry defeat the structured-data point — the field becomes free text again. Either enumerate the real values or drop the field.
- `id:` keys on form components are referenced by the GitHub API and by repo-level automation. Choose stable, descriptive IDs (`plugin-version`, not `field-3`) so renaming the label later doesn't break consumers.
- `render: shell` (and `render: python`, `render: javascript`, …) only takes effect on `textarea`; on `input` it is silently ignored.
- `contact_links` is a flat list under `config.yml`'s top level — not nested under any template. Putting it inside a `body:` block makes the chooser drop it without an error message.

### Hard rules

- Never write any file under `.github/ISSUE_TEMPLATE/` without first surfacing the full derivation (project type, audiences, templates, fields, labels, assignees) to the user and getting an explicit confirmation.
- Never leave `.github/ISSUE_TEMPLATE/` in a half-configured state — apply is atomic. On any single-file failure, roll back the partial set.
- Never write template content in a language other than English, regardless of the repo's documentation language.
- Never proceed without an audience artefact that covers reporters and triagers — either read an existing one or dispatch `audience-identify` first.
- Never write a `feature_request.yml` with more than two required fields total (search acknowledgement + one substantive `textarea`). Never raise a project-type-specific or audience-derived feature-template field to `required: true`. Never require a closed-taxonomy field (severity, priority, target release, milestone, owner) on the feature template.
- Never touch `.github/pull_request_template.md`, `.github/DISCUSSION_TEMPLATE/`, `CODEOWNERS`, `SECURITY.md`, or `SUPPORT.md` from this skill — those are out of scope per the spec.
- Never silently overwrite an existing `.github/ISSUE_TEMPLATE/` directory on a re-run. Diff first, then ask per item.
- Never pre-fill `assignees:` unless the repo has a documented stable triage owner; the default is to leave it empty.
- Never add an "Other / please specify" option to a `dropdown` — enumerate the real values or drop the field.
- When `spec/project/github-issue-templates/` disagrees with this skill's instructions, the spec wins. Propose updating this skill rather than silently diverging.
