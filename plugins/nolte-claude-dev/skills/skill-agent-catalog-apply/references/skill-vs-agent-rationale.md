# Why this is a skill, not an agent

The `skill-vs-agent` design rationale for `skill-agent-catalog-apply`, plus its boundary against `project-structure-apply`.

## Why a skill

This is a skill, not an agent, because:

- **Orchestration role**: applying the catalog spec is a scaffolding step inside a larger "bring this plugin repo in line with portfolio conventions" flow, right alongside `project-structure-apply`. The output is expected to flow into the main conversation so the caller can see each proposed change.
- **Interactivity**: per-item approval of config patches is central to the contract; skills handle that naturally.
- **Specialisation isn't the limiting factor**: the real logic lives in the spec and in the generator hook (a Python file), not in a narrow system prompt; a restricted agent wouldn't sharpen the work.
- **Counter-dimension (context-window)**: the verification step (running `task docs` and reading the build output) has a mild context-window impact, but it's bounded and fits in the main conversation.
- **Counter-dimension (parallelism / tool restriction)**: writing `scripts/docs/gen_catalog.py` is a self-contained Python-authoring task that an agent could plausibly own with a narrower tool surface (`Read`, `Write`, `Glob`). The reason it stays in the skill: the file write is one of several per-item approvals in a single apply cycle, so splitting it out would add a dispatch boundary without removing the surrounding interactivity.

## Boundary against `project-structure-apply`

This skill follows the same orchestrator-pattern precedent as `project-structure-apply`, but the two own non-overlapping surfaces and **MUST NOT** be merged:

- `project-structure-apply` scaffolds the bare MkDocs setup itself: `mkdocs.yml`, the Material theme, `docs/<lang>/` trees, the `task docs` target, the docs-requirements file. It is the prerequisite — without a working `mkdocs.yml`, this skill's preconditions fail and route the user there.
- `skill-agent-catalog-apply` (this skill) wires the catalog generator on top of an already-scaffolded MkDocs setup: the generator surface (the `on_pre_build` hook by default, or a standalone pre-build step / `gen-files` script), the `literate-nav` plugin, the `docs/catalog-sources.yml` source-root list, and the `scripts/docs/gen_catalog.py` module. It assumes the MkDocs base layer exists and never modifies the files `project-structure-apply` owns.

The split is load-bearing because the catalog generator is plugin-specific (it only runs in repositories that publish skills/agents), while the bare MkDocs setup is portfolio-wide. Folding the catalog wiring into `project-structure-apply` would force every project repo to carry the catalog plumbing it doesn't need.
