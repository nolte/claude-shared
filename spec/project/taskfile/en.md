# Taskfile Conventions

Status: draft
Portfolio-Scope: portfolio

## Context
Every repository in the portfolio drives its local automation through [Task](https://taskfile.dev). A `Taskfile.yml` at the repository root is the single, recognisable entry point for installing dependencies, linting, testing, building docs, and cutting releases. The behaviour around that file has grown consistent in practice (a `:`-namespaced target tree, argument passthrough, a shared collection of reusable Taskfiles pulled from [`nolte/taskfiles`](https://github.com/nolte/taskfiles), and CI that calls the very same targets a contributor runs locally), but the rules for it are scattered: `project-structure` pins the file's presence and the canonical `task check` name, `quality-gate` owns what `task check` composes, `cookiecutter-template-authoring` lists `task install/lint/test/docs/release`, `permission-allowlist` forbids `Bash(task *)` wildcards, and `parallel-working-copies` defines the `worktree:*` helpers. No single spec states the Taskfile *mechanics* the whole portfolio is expected to share, so a new repository has to reverse-engineer the convention from five places.

This spec consolidates the portfolio-wide Taskfile *mechanics* in one place: the canonical target vocabulary, the namespacing scheme, argument passthrough, the local↔CI parity rule, and—centrally—the use of the shared reusable Taskfiles published in [`nolte/taskfiles`](https://github.com/nolte/taskfiles). It deliberately **doesn't** restate what any individual target *does*; the semantics of each capability stay with the spec that already owns it. The result is that the shape of the Taskfile is the same everywhere, while each capability keeps a single source of truth.

## Goals
- A contributor in any portfolio repository finds the same canonical target names (`task install`, `task lint`, `task test`, `task check`, `task docs`, `task release`) for the same jobs, so muscle memory and documented invocations transfer between repositories
- Portfolio-common automation (MkDocs, pre-commit, and similar cross-repo concerns) is consumed from the shared [`nolte/taskfiles`](https://github.com/nolte/taskfiles) collection rather than re-implemented per repository, so a change to shared behaviour lands once and propagates
- The grouping convention (the `:`-namespaced target tree) and argument passthrough are uniform, so `task --list` reads the same way across the portfolio
- CI invokes lint, test, and docs through the identical Taskfile targets a contributor runs locally, so local and CI behaviour can't drift apart
- This spec owns the Taskfile *mechanics* only; the *semantics* of each target stay with the capability spec that owns them, so nothing is duplicated and there is no second source of truth to keep in sync

## Non-Goals
- Defining what `task check` composes or the shape of its output—that's governed by `spec/project/quality-gate/`; this spec only pins the canonical name
- Requiring the Taskfile's presence, the project-local virtual-environment wiring, or the `requirements*.txt` install pattern—those are governed by `spec/project/project-structure/`; this spec assumes the file exists and governs its conventions
- Choosing the language-specific tool a target runs (ruff vs. flake8, MkDocs vs. another generator)—a per-repository decision
- Replacing pre-commit, the quality gate, or CI—Task is the entry point that invokes them, not a substitute for them
- Declaring the contents of the shared `nolte/taskfiles` collection itself—that repository is its own source of truth; this spec governs only how portfolio repositories *consume* it

## Requirements

### Canonical target vocabulary
- A repository **MUST** expose each capability it has under the portfolio-canonical target name rather than a synonym: `task setup` (one-time onboarding—install hooks and bootstrap the project-local environment), `task install` (install or refresh dependencies in that environment), `task lint` (linters), `task test` (tests or, for prompt-only repositories, the frontmatter/contract validation), `task typecheck` (type checks, where the language has them), `task check` (the aggregate quality gate), `task docs` (documentation build), and `task release` (release cut, where the repository releases artefacts)
- A capability the repository doesn't have (for example `task release` in a library that ships no release artefacts) is simply absent; the rule pins the *name* when the capability exists, not the existence of every capability
- This spec pins the canonical *names* only. The composition, behaviour, and output of each target stay with the spec that owns the capability—for example `task check` with `spec/project/quality-gate/` and the documentation build with `spec/project/mkdocs-structure/`. A repository **MUST NOT** restate those semantics in this spec's terms; it **MUST** follow the owning spec

### Namespacing and discoverability
- Grouped and sub-targets **SHOULD** use the `:` separator to form a readable tree (for example `docs:catalog`, `validate:skills`, `lint:prose`, `worktree:add`), so `task --list` groups related work
- Per-subroot variants of a gate target **SHOULD** follow the same scheme (`task lint:backend`, `task test:frontend`); their composition into the aggregate gate is governed by `spec/project/quality-gate/`
- The `default` target **SHOULD** list the available tasks (equivalent to `task --list`), so running `task` with no argument is self-documenting

### Argument passthrough
- A target that accepts caller-supplied arguments **SHOULD** consume them through Task's `CLI_ARGS` so they can be passed after `--` (for example `task worktree:add -- <branch> [slug]`), keeping the argument surface uniform across the portfolio

### Shared Taskfiles from `nolte/taskfiles`
- [`nolte/taskfiles`](https://github.com/nolte/taskfiles) is the portfolio's authoritative collection of reusable, shared Taskfiles. Behaviour that's common across repositories **SHOULD** live there, not be forked per repository
- A repository **SHOULD** consume portfolio-common automation (for example MkDocs and pre-commit targets) by including the relevant Taskfiles from `nolte/taskfiles` rather than re-implementing equivalent targets locally, so a change to shared behaviour is made once upstream and propagates on the next include resolution
- When a repository includes Taskfiles from `nolte/taskfiles`, it **MUST** pin the source location through a single variable (for example `TASK_COLLECTION_BASE`) that names an explicit ref, so every include resolves against one declared, reviewable source rather than scattered inline URLs
- Task's remote-Taskfile resolution is an experimental feature; a repository that consumes remote includes **MUST** enable Task's experiment flag (`TASK_X_REMOTE_TASKFILES=1`) wherever those includes are resolved, including the CI environment, so resolution is explicit rather than relying on an undeclared default
- Repository-specific automation that's not shared across the portfolio **MAY** remain a local target in the repository's own `Taskfile.yml`; the shared collection is for portfolio-common behaviour, not for one-off, repo-specific work

### Local and CI parity
- CI **MUST** invoke lint, test, and docs through the same Taskfile targets a contributor runs locally (for example `task --yes lint`, `task --yes test`, `task --yes docs`) rather than re-implementing those steps inline, so the local gate and the CI gate can't drift apart. The aggregate `task check` (whose composition is governed by `spec/project/quality-gate/`) is the local convenience entry point; CI **MAY** keep each category as a separate required check while still calling the same per-category targets

### Permissions
- Permission allowlists **MUST NOT** grant a `Bash(task *)` wildcard; exact targets (for example `Bash(task lint)`) are granted individually, as governed by `spec/claude/permission-allowlist/`. This spec restates the rule's *location* only, not its content

## Acceptance Criteria
- [ ] `spec/project/taskfile/` exists with `en.md` (canonical) and `de.md` (translation) and is listed in `spec/README.md`
- [ ] The canonical target vocabulary (`setup`, `install`, `lint`, `test`, `typecheck`, `check`, `docs`, `release`) is defined in exactly one place—this spec—and the namespacing, passthrough, and local↔CI-parity conventions are stated here
- [ ] `nolte/taskfiles` is named as the authoritative shared-Taskfile collection, with a SHOULD to consume portfolio-common automation from it, a MUST to pin the include source via a single ref variable, and the `TASK_X_REMOTE_TASKFILES` experiment-flag requirement recorded
- [ ] The spec delegates rather than duplicates: target *semantics* point to `quality-gate`, file presence and venv wiring to `project-structure`, `worktree:*` helpers to `parallel-working-copies`, and the `task *` wildcard ban to `permission-allowlist`
- [ ] `spec/project/project-structure/`, `spec/project/quality-gate/`, and `spec/portfolio/tech-stack/` carry a back-reference to this spec as the owner of the Taskfile mechanics
- [ ] Every artefact that scaffolds or patches a `Taskfile.yml` (the `project-structure-apply` and `mkdocs-structure-apply` skills, plus the `cookiecutter-template-author` agent through `spec/project/cookiecutter-template-authoring/`) points at this spec and emits the shared-collection include form instead of a locally re-implemented target
- [ ] No requirement in this spec restates the composition or output of a target whose semantics another spec owns

## Open Questions
- Once Task's remote-Taskfile resolution graduates from experimental to stable, should consuming portfolio-common automation from `nolte/taskfiles` be raised from **SHOULD** to **MUST**, and the `TASK_X_REMOTE_TASKFILES` flag requirement retired? Deferred until the upstream feature stabilises.

## Sources

The Task remote-Taskfile feature-maturity assertion in §"Shared Taskfiles from `nolte/taskfiles`" is an author-time external assertion triangulated per `spec/claude/research-triangulate/` §Author-time assertions (author-time tier: at least three independent sources, ordered Primary-first). Retrieval date for every source below: 2026-07-24.

- **Task's remote-Taskfile resolution is an experimental feature gated by `TASK_X_REMOTE_TASKFILES=1`**: Task documentation, "Remote Taskfiles" experiment page, gated by `TASK_X_REMOTE_TASKFILES` and carrying the standard experimental-feature warning (Primary), `https://taskfile.dev/docs/experiments/remote-taskfiles`; the upstream tracking issue `go-task/task#1317`, still open with experiment status "candidate" (Primary), `https://github.com/go-task/task/issues/1317`; `Marmelab`, "Taskfile: The Modern Alternative to `Makefile`" (Secondary), `https://marmelab.com/blog/2026/03/12/taskfile-alternative-makefile.html`

Verified 2026-07-24: the feature is still experimental (the tracking issue's status has advanced from "draft" to "candidate" but is neither stable nor enabled by default), and the flag name `TASK_X_REMOTE_TASKFILES` is unchanged, so the requirement above remains current.
