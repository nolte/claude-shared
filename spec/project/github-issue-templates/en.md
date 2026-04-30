# GitHub Issue Templates

Status: draft

## Context

GitHub repositories in the nolte portfolio cover diverse project types: Claude Code plugins (skills, agents, specs), Python applications (for example `kamerplanter`), CLIs, libraries, documentation-only repos. A single generic "bug report" / "feature request" template gives maintainers and contributors too little context. A Claude-plugin bug needs the plugin version and the affected skill name; a `kamerplanter` bug needs the camera model, the firmware version, and the failing planting step. Without project-specific prompts, issues land incomplete and triage cost rises.

The `project-structure` spec leaves this gap explicitly open: community-health files (issue templates, CODEOWNERS) aren't yet prescribed. This spec closes the issue-template half of that gap and defines a methodology (not a fixed template) that a downstream skill can run on any repo to generate the right templates for that repo's project type.

## Goals

- Define a repeatable procedure for deriving project-specific issue templates from a repo's project type and audience profile.
- Establish a minimum baseline (which template kinds every repo MUST ship) and a structured way to add project-specific fields beyond it.
- Standardise on GitHub Issue Forms (YAML) so triage data is structured, validated, and filterable, not free-form prose.
- Provide enough detail that a skill can scaffold templates for a fresh repo and incrementally update templates for an existing repo without a human authoring each file.
- Stay aligned with the `audience-identification` spec; issue templates are a documentation artefact aimed at identified audiences (reporters, the triage role, maintainers).

## Non-Goals

- Pull-request templates. Those are governed by `pull-request-workflow`.
- Authoring concrete templates for every imaginable project type. This spec defines the *method*; templates themselves are generated per repo.
- Discussion templates (`.github/DISCUSSION_TEMPLATE/`). Out of scope; can be a follow-up spec.
- Localisation of issue templates. The GitHub issue UI is English-only in practice; templates remain English regardless of the repo's documentation language.
- CODEOWNERS, SECURITY.md, SUPPORT.md. Tracked separately under the `project-structure` open questions.

## Requirements

### Storage and format

- **MUST** place every issue template under `.github/ISSUE_TEMPLATE/` in the repo root.
<!-- vale Microsoft.Contractions = NO -->
- **MUST** use GitHub Issue Forms (`.yml`, top-level keys `name`, `description`, `body`, optional `title`, `labels`, `assignees`, `projects`, `type`) for any template that asks for structured information. Free-form Markdown templates (`.md`) are reserved for purely informational stubs and **SHOULD NOT** be used otherwise.
<!-- vale Microsoft.Contractions = YES -->
- **MUST** include a `.github/ISSUE_TEMPLATE/config.yml` with at minimum `blank_issues_enabled: false` unless the project type explicitly opts in to blank issues.
- **MUST** keep all template content in English regardless of the repo's documentation language, because the GitHub issue UI doesn't translate.

### Baseline templates

Every repo **MUST** ship at least:

- **`bug_report.yml`**: captures observed vs expected behaviour, reproduction steps, environment.
- **`feature_request.yml`**: captures the proposed change, the user need behind it, and the alternatives considered.

Repos **SHOULD** add further templates only when the audience analysis or the project type makes them load-bearing. Common additions:

- `documentation.yml`: for repos whose primary deliverable is documentation, or whose docs are heavy.
- `question.yml`: only when GitHub Discussions aren't enabled; otherwise route to Discussions via `config.yml`.
- `chore.yml` / `maintenance.yml`: for repos with frequent dependency or housekeeping issues.

### Project-type-driven derivation

A template-generation skill **MUST** follow this derivation procedure, in order:

1. **Identify project type.** Inspect the repository to classify it. Suggested signals (non-exhaustive):
   - Claude Code plugin → `.claude-plugin/plugin.json` exists, `skills/` and/or `agents/` folders present.
   - Python application → `pyproject.toml` with an application entry point, no library distribution metadata.
   - Python library → `pyproject.toml` declaring a distributable package.
   - Node / TypeScript library or app → `package.json` with `main` / `exports` (library) versus `bin` / `scripts.start` (app).
   - CLI tool → declared CLI entry point in `pyproject.toml` / `package.json` / `Cargo.toml`.
   - Documentation-only repo → presence of `mkdocs.yml`, `docusaurus.config.*`, or similar with no application code.
2. **Resolve audience profile.** If an audience artefact already exists per `audience-identification`, read it; otherwise dispatch the `audience-identify` skill on the repo first. Issue templates are written for the *reporter* audience and the *triage* audience; both must be identified.
3. **Derive triage questions.** For each baseline template plus any project-type-specific extras, list the questions a maintainer doing triage will ask within five minutes of receiving the issue. Those questions become required fields. Examples:
   - Claude-plugin bug: which skill or agent, plugin version, Claude Code version, command transcript.
   - Python application bug: OS, Python version, install method, command / transcript, `traceback`.
   - Library API bug: library version, minimal reproducer snippet, runtime version.
   - Application feature: which user goal it serves, which audience segment, alternatives considered.
4. **Encode questions as Issue Forms components.** Use the minimum component complexity that fits:
   - Single short string → `input`.
   - Long free text → `textarea` (with `render: shell` for logs and `traceback` output).
   - One-of choice → `dropdown` with the actual valid values, not "Other / please specify."
   - Multiple-of choice → `checkboxes`.
   - Acknowledgement gates (code of conduct, search check) → `checkboxes` with `required: true`.
5. **Set labels and assignees.** Pre-fill `labels:` from the project's label taxonomy (often a `.github/labels.yml` or Probot `settings.yml`). Only pre-fill `assignees:` when the repo has a stable triage owner.
6. **Wire the chooser.** Update `.github/ISSUE_TEMPLATE/config.yml` with `contact_links` for any external destinations (Discussions, support forum, security policy) so the chooser surfaces them alongside the templates.

### Field hygiene

Bug reports and feature requests share the same storage mechanism (`.github/ISSUE_TEMPLATE/*.yml` as Issue Forms) but **MUST NOT** share the same field-strictness profile. Bug reports carry triage-critical structured data and are strict by design; feature requests need room for half-formed ideas and stay permissive by design. The rules below split accordingly.

#### Common to every template

- **MUST** include a search-before-filing acknowledgement on every template (a single required `checkboxes` entry pointing at the issue tracker).
- **SHOULD** keep each template under ten total components; longer forms reduce reporter completion rate.
- **MAY** pre-fill the issue title via the form's top-level `title:` key when the project type has a strong title convention (for example `[bug] <area>: <summary>` or `[feat] <summary>`).

#### Bug reports: Strict by design

- **MUST** mark every field that maintainers need for triage before they can act as `validations: required: true`.
<!-- vale Microsoft.Contractions = NO -->
- **SHOULD NOT** carry a free-form "additional context" field as the only structured input. At least one structured field per template must capture triage-critical data.
<!-- vale Microsoft.Contractions = YES -->
- **MAY** use `dropdown` and `checkboxes` liberally to enumerate concrete operational choices (install method, runtime, OS) so triage can filter on the values.

#### Feature requests: Permissive by design

A feature request often arrives as a half-formed thought that needs room to be discussed and refined before it converges on a shape. Tight required-field gates discourage submission and force premature commitment to one solution, so the spec biases feature templates toward openness:

- **MUST** keep total required fields on `feature_request.yml` at no more than two: the search-before-filing acknowledgement plus exactly one substantive input.
- **MUST** use `textarea` (not `dropdown` and not `checkboxes`) for the substantive required input, so the reporter can express the idea in their own words rather than picking from a pre-defined taxonomy.
- **MUST NOT** require the reporter to select from a closed taxonomy (severity, priority, target release, milestone, owner). Those are triage decisions made by the maintainer after the issue is read, not by the reporter at filing time.
- **SHOULD** expose project-type-specific extras (target artefact, audience segment, scope hint, …) as optional fields rather than required, even when the same field would be required on the matching `bug_report.yml`.
- **SHOULD** offer at most one optional `textarea` for additional context rather than three separate optional fields ("alternatives," "screenshots," "prior discussion"); fewer empty fields keeps the form scannable and signals that the reporter doesn't owe the maintainer a finished proposal.

### Skill contract

A downstream skill that applies this spec **MUST**:

- detect the project type per the procedure above.
- read or create the audience artefact before generating templates.
- surface its derivation (project type, audiences, chosen template kinds, project-specific fields, **and the per-template strictness profile**) to the user before writing files.
- write `.github/ISSUE_TEMPLATE/*.yml` and `.github/ISSUE_TEMPLATE/config.yml` together, never leaving the directory in a half-configured state.
- before writing `feature_request.yml`, validate that no more than the search-acknowledgement plus one substantive field is `required: true`, and that the substantive required field is a `textarea`; reject the write if either condition fails.
- be re-runnable: a re-run on a repo that already has templates **MUST** detect drift (project type changed, new audiences, missing required fields, **or feature_request.yml that has accumulated required fields beyond the cap**) and offer a diff rather than silently overwriting.

## Acceptance Criteria

- [ ] A repo audited under this spec has `.github/ISSUE_TEMPLATE/config.yml` with `blank_issues_enabled` set explicitly.
- [ ] A repo audited under this spec has at minimum `bug_report.yml` and `feature_request.yml` as Issue Forms.
- [ ] Each bug template's required fields can be traced back to a triage question identified in step 3 of the derivation procedure.
- [ ] Each template includes a required search-before-filing acknowledgement.
- [ ] `feature_request.yml` carries at most two required fields total (search-before-filing acknowledgement + one substantive input).
- [ ] `feature_request.yml`'s primary substantive required input is a `textarea`, not a `dropdown` or `checkboxes`.
- [ ] `feature_request.yml` doesn't require any closed-taxonomy field (severity, priority, target release, milestone, owner).
- [ ] For a Claude-plugin repo, the bug template asks for plugin version and the affected skill or agent.
- [ ] For an application repo (for example `kamerplanter`), the bug template asks for the runtime environment specific to that application (OS, Python / runtime version, relevant hardware where applicable).
- [ ] No template uses Markdown (`.md`) form unless the template is a purely informational stub.
- [ ] The applied derivation (project type, audiences, chosen templates, project-specific fields) is recorded somewhere the skill can re-read on the next run, either inside the templates as comments or in a sibling artefact.
- [ ] Re-running the generator on a repo that already conforms produces no diff.

## Open Questions

- Should the derivation record (project type, audiences, chosen templates) live inline as a YAML comment block in `config.yml`, or in a separate file (for example `.github/ISSUE_TEMPLATE/.derivation.yml`)? Inline is simpler; a sibling file is easier for the skill to parse.
- How does this spec interact with the open `project-structure` question on community-health files? Once CODEOWNERS / SECURITY.md are also specified, should the issue-template chooser link to SECURITY.md via `config.yml.contact_links` automatically?
- Should a "security vulnerability" template be allowed at all, or always routed to a private channel via `contact_links`? Current default: route privately, no public template.
- Discussion templates: defer to a follow-up spec, or fold them in here?
