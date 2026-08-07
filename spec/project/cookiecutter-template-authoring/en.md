# Cookiecutter Template Authoring

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

The portfolio uses [Cookiecutter](https://www.cookiecutter.io/) as the canonical scaffolding tool for new projects that need to start in spec-conformant shape from the first commit. The `cookiecutter-template-author` agent already authors these templates today, but it does so against a set of MUSTs that live only in the agent's body—there's no spec a Reviewer can audit the agent against, no spec a follow-up agent can read, and no spec the `spec-drift-audit` process can compare implementations against. This spec lifts those MUSTs into the same shape every other portfolio capability uses: a normative requirements list, testable acceptance criteria, and a clear boundary to neighbouring specs (`project-structure`, `pull-request-workflow`, `branching-model`, `release-automation`, `release-skill-layer`).

A Cookiecutter template in this portfolio is a project-scaffold artefact that renders, in one step, a new repository whose initial commit satisfies every applicable MUST in those neighbouring specs. The template carries its own hooks (`pre_prompt.py`, `pre_gen_project.py`, `post_gen_project.py`), its own `cookiecutter.json` variable shape, and its own test harness (`pytest-cookies` plus a GitHub Actions matrix). This spec governs that artefact: what the template MUST produce, what hooks it MUST run, how its tests MUST exercise the rendered output, and which anti-patterns it MUST refuse to ship.

Readers: authors of the `cookiecutter-template-author` agent and the templates it produces, reviewers auditing a template against the neighbouring scaffolding specs, and the `spec-drift-audit` process comparing template implementations against this spec.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Every Cookiecutter template authored in the portfolio renders a project whose initial commit passes every applicable MUST in `spec/project/project-structure/`, `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, `spec/project/release-automation/`, and `spec/project/release-skill-layer/`
- Templates ship with a `pytest-cookies`-based test harness that exercises the rendered output, so a regression in any neighbouring spec breaks the template's CI before it ships
- The Cookiecutter hooks (`pre_prompt.py`, `pre_gen_project.py`, `post_gen_project.py`) follow a documented contract—what each may and may not do, what side-effects are permitted, how they interact with the rendered tree
- The `cookiecutter-template-author` agent has a normative anchor it can be audited against by `spec-readiness-reviewer` and reconciled against by the periodic `spec-drift-audit` process
- New portfolio templates inherit the same anti-pattern list (no committed virtualenv directories, no rendered `__pycache__`, no hard-coded secrets, no untested hook side-effects, …) instead of each template re-discovering them

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Consuming an existing template (a plain `cookiecutter <url>` invocation needs no spec or agent)
- Generic Python-project bootstrap unrelated to Cookiecutter (use the standard Python project structure under `spec/project/project-structure/`)
- Copier or cruft templates—those have different anti-patterns and different hook contracts; cross-references to them belong in the agent's body, not this spec. A dedicated `copier-template-authoring` / `cruft-template-authoring` spec is created only if and when the portfolio ships such a template.
- Templates that intentionally diverge from the nolte portfolio specs (those are out-of-scope for the agent and for this spec; the divergence requires an explicit waiver recorded outside this surface)
- The render-time `cookiecutter.json` variable schema (it varies per template by design—the spec governs the shape of the resulting project, not the input shape)
- Visual identity or branding of the rendered project (per-template decision, gated by the rendered project's own `mkdocs-material` palette settings)

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->

### Rendered-project conformance

- **MUST** render a project whose initial commit satisfies every MUST in `spec/project/project-structure/`: the seven baseline files / folders (`README.md`, `LICENSE`, `.gitignore`, `Taskfile.yml`, `mkdocs.yml` when docs ship, `.github/`, `pyproject.toml` or equivalent), the seven baseline GitHub configs (`.github/settings.yml`, `release-drafter.yml`, `boring-cyborg.yml`, `stale.yml`, plus the Probot `extends:` pointers), and the project-structure-mandated Renovate setup
- **MUST** render a project whose initial commit satisfies the branching shape defined in `spec/project/branching-model/`: at least a `develop` branch (`main` is created by the user's first release), no committed feature-branch state, no committed working-tree pollution (`__pycache__`, `.venv`, `node_modules`, build artefacts)
- **MUST** render a `.github/workflows/` set that satisfies `spec/project/release-automation/` and `spec/project/release-skill-layer/` for the chosen release flow: a `release-drafter` workflow on PR-merge to `develop`, a `release-publish.yml` workflow that the `release-publish-trigger` skill can dispatch, and the required-checks contract on `develop` per `spec/project/workflow-health/`
- **MUST** render a `.github/PULL_REQUEST_TEMPLATE.md` and an issue-template set that satisfies `spec/project/pull-request-workflow/` and `spec/project/github-issue-templates/` (when the rendered project is configured to ship issues / PRs at all)
- **MUST** render a Taskfile whose targets match the portfolio convention: `task install`, `task lint`, `task test`, `task docs` (when docs ship), `task release` (when release flow is wired); each target invokes the project-local toolchain rather than relying on globally installed binaries. The canonical target vocabulary, the namespacing scheme, and the argument-passthrough rules stay owned by `spec/project/taskfile/`, which this requirement doesn't restate
- **SHOULD** render a Taskfile that consumes portfolio-common automation (MkDocs, pre-commit, and similar cross-repo concerns) from the shared [`nolte/taskfiles`](https://github.com/nolte/taskfiles) collection through an `includes:` block wherever that collection covers the need with a runnable target, rather than re-implementing equivalent targets inline, per `spec/project/taskfile/` §Shared Taskfiles. A template that re-implements genuinely shared behaviour locally hands every rendered project a private copy that upstream fixes never reach; conversely, a template that delegates to an included target which doesn't exist, or whose environment assumptions don't hold in the rendered project, ships a Taskfile that fails on first use. Verify the include before delegating to it
- **MUST**, when the rendered Taskfile does include files from `nolte/taskfiles`, pin the source location through a single variable (for example `TASK_COLLECTION_BASE`) naming an explicit ref, and render a CI workflow that both sets `TASK_X_REMOTE_TASKFILES=1` and invokes every target non-interactively (`task --yes <target>`) wherever those includes resolve. Task's remote-Taskfile resolution is experimental, off by default, and additionally gated behind a trust prompt that a CI runner has no terminal to answer, so a rendered project missing either piece fails on its first CI run
- **MUST** include in the rendered project an `AUDIENCES.md` stub or a `## Audiences` README section, per `spec/project/audience-identification/`, so the rendered project starts with the audience-identification step rather than retrofitting it later
- **MUST NOT** render committed secrets, hard-coded API keys, or credentials of any shape—even in example or test files. Render-time secrets enter the project via `.env.example` or equivalent placeholder shape only.

### Hook contract

- **MUST** restrict `pre_prompt.py` to read-only operations and variable-validation logic. The hook **MUST NOT** mutate the filesystem outside its own ephemeral working directory, **MUST NOT** make network calls, and **MUST NOT** spawn shell processes that produce side-effects.
- **MUST** restrict `pre_gen_project.py` to validation, normalisation, and abort logic (printing a clear error and `sys.exit(1)` for invalid input). The hook **MUST NOT** mutate the rendered project tree before render—it runs *before* generation by design and the tree doesn't exist yet.
- **MUST** restrict `post_gen_project.py` to operations that finalise the rendered project: removing files / folders the user opted out of via `cookiecutter.json` variables, initialising a git repository (`git init` is permitted; `git remote add` and `git push` are forbidden), running `pre-commit install`, and printing a final "next steps" banner. The hook **MUST NOT** install dependencies (Python, Node, system), **MUST NOT** make network calls, and **MUST NOT** modify files outside the rendered project tree.
- **MUST** make every hook side-effect verifiable by a `pytest-cookies` test (see §Test harness below); a hook that mutates the rendered tree without a covering test is an authoring failure
- **SHOULD** keep each hook under ~100 lines of Python; longer hooks indicate the responsibility belongs to a separate skill or a runtime tool, not to the template
- **MAY** dispatch the rendered project to the `audience-identify` skill as the post-generation next step (printed in the banner, not automatically invoked), so the operator follows the spec-mandated audience-identification flow right after generation. This stays MAY (banner-only) by design: the rendered-project hook isn't a skill and MUST NOT invoke the Skill tool (see `spec/claude/skill-vs-agent/`, which forbids an agent from invoking the Skill tool on the user's behalf), and the authoring-time `cookiecutter-template-manage` skill can't reach the consumer's generation-time context. Upgrading to automatic dispatch requires a new generation-time wrapper, not a change to the hook contract.

### Test harness

- **MUST** ship a `pytest-cookies` test suite that renders the template with a representative variable set and asserts the rendered tree satisfies every MUST in §Rendered-project conformance
- **MUST** wire the test suite into a GitHub Actions matrix that exercises the template on at least the Python versions declared in `pyproject.toml` (or equivalent) and at least the OS that matches the rendered project's target—typically `ubuntu-latest`. When a template's rendered target implies Windows execution (Windows binary releases, a Home Assistant integration), "the OS that matches the rendered project's target" resolves to including `windows-latest` in that template's matrix.
- **MUST** assert post-generation hook outcomes mechanically (file presence, file absence, `pre-commit` install state, …) rather than via printed banner inspection
- **SHOULD** include a "render twice with the same variables yields identical trees" idempotency test, so non-deterministic hooks are caught at template-CI time
- **MAY** include a "render with optional features off then on" matrix dimension when the template's `cookiecutter.json` exposes feature-toggle variables; this catches features that secretly depend on each other

### Anti-pattern refusal

The template **MUST NOT** render any of the following:

- Committed `.venv/`, `node_modules/`, `__pycache__/`, `.pytest_cache/`, build artefacts, or other ignorable working-tree state
- Editor-specific configuration outside the portfolio convention (`.idea/`, `.vscode/settings.json` with user-specific paths)
- Hard-coded user-specific paths (`/home/<user>/`, `C:\\Users\\<user>\\`) in any rendered file
- Documentation that contradicts the rendered project's actual shape (a `README.md` that documents files the template doesn't render)
- `LICENSE` files copied verbatim from another project without the SPDX identifier and copyright holder fields filled in correctly for the rendered project
- A `CHANGELOG.md` with placeholder entries that pretend the rendered project has shipped releases when it hasn't

### Documentation

- **MUST** ship a template-level `README.md` (at the template repository root, separate from the rendered project's `README.md`) that names: what the template renders, the `cookiecutter.json` variable shape, the optional features and their toggles, the post-generation banner output, and the link to this spec
- **MUST** declare the agent that authors this template (`cookiecutter-template-author`) as the canonical authoring tool in the template-level README
- **SHOULD** ship a `docs/` MkDocs site for the template itself when the template renders more than ~20 variables, so the variable surface stays discoverable

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] Every Cookiecutter template in the portfolio renders a project whose initial commit passes every applicable MUST in `project-structure`, `pull-request-workflow`, `branching-model`, `release-automation`, and `release-skill-layer`; verifiable by the template's `pytest-cookies` test suite running green
- [ ] Every template ships a `pytest-cookies` test suite wired into a GitHub Actions matrix; CI on the template repo proves the suite runs
- [ ] Every `pre_prompt.py`, `pre_gen_project.py`, and `post_gen_project.py` hook in the portfolio honours the operations / side-effect restrictions above; verifiable by a Reviewer audit of the hook bodies (no network calls, no dep installs, no out-of-tree writes)
- [ ] Every template's `post_gen_project.py` banner directs the operator to the `audience-identify` skill as the post-generation next step
- [ ] Every rendered project ships an `AUDIENCES.md` stub or `## Audiences` README section, so the audience-identification flow starts at generation time
- [ ] Every template's rendered `Taskfile.yml` conforms to `spec/project/taskfile/`. A template that renders no remote include passes this criterion (the collection covers no CI-gating target today, so writing `lint` / `test` / `docs` locally is conformant, not a gap). A template that *does* render remote includes additionally pins them through a single base variable and renders a CI workflow that sets `TASK_X_REMOTE_TASKFILES` and calls each target with `task --yes`; verifiable by a `pytest-cookies` assertion that's conditional on the rendered Taskfile carrying an `includes:` block
- [ ] No template in the portfolio renders any of the listed anti-pattern artefacts (committed `.venv/`, `__pycache__/`, hard-coded credentials, user-specific paths, …); the template's own CI catches every one mechanically
- [ ] The `cookiecutter-template-author` agent's body cites this spec as its normative source instead of restating the requirements

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._

## Sources
<!-- Authoritative external references the requirements above were validated against (≥2 independent sources per claim). -->
- Cookiecutter documentation (cookiecutter.readthedocs.io)—canonical reference for the hook lifecycle (`pre_prompt.py` / `pre_gen_project.py` / `post_gen_project.py`) and the `cookiecutter.json` variable shape
- `pytest-cookies` documentation (github.com/hackebrot/pytest-cookies)—canonical reference for the test-harness fixtures used to exercise rendered output
- `spec/project/project-structure/`, `spec/project/pull-request-workflow/`, `spec/project/branching-model/`, `spec/project/release-automation/`, `spec/project/release-skill-layer/`, `spec/project/audience-identification/`: the portfolio specs this spec lifts requirements from
- The cookiecutter-template-author agent's current body (`agents/cookiecutter-template-author.md`)—the de-facto requirements list that this spec ratifies into a normative shape
