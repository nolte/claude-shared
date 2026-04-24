# Contributing to `nolte-shared`

Thanks for taking a look. This document describes what kinds of contributions make sense today, how to set the repo up locally, and which conventions the repository enforces.

## Status

This repository is currently maintained single-handedly and is in an early consolidation phase (see the "Status" note in `README.md`). Pull requests are welcome, but there is no published review or merge SLA — triage is best-effort.

If you are unsure whether a change fits, open an issue first and describe the use case. A short issue beats a large PR that has to be redirected.

## Contributions that fit

- A bug fix to an existing skill, agent, or spec, with a concrete reproduction.
- A new skill or agent that fills a clearly articulated gap and ships together with the spec(s) it implements.
- A spec correction backed by a real contradiction or a missing Acceptance Criterion.
- Translation-parity fixes (the specs are EN-canonical with DE translations — both stay in sync).
- Documentation fixes to `README.md`, `CLAUDE.md`, or the `docs/` tree.

## Contributions that do not fit

- Copies of this plugin's skills into a consumer's `.claude/skills/` — distribution happens via the plugin marketplace (see `CLAUDE.md`).
- Version bumps to `plugin.json` / `marketplace.json` in a skill-change PR — version bumps belong in a dedicated release workflow (currently deferred).
- Generated configuration files (`.github/*.yml`, `Taskfile.yml`, workflow YAML) translated into languages other than English — portfolio consistency requires these stay EN.

## Development setup

1. Clone the repository.
2. Install the local toolchain: a recent [`task`](https://taskfile.dev), `pre-commit`, and a Python environment able to run MkDocs (details in `Taskfile.yml`).
3. Load the plugin into Claude Code for dogfooding:

   ```bash
   claude --plugin-dir .
   ```

   Inside the session, use `/reload-plugins` to pick up changes without restarting.
4. Run the lint and docs gates locally before opening a pull request:

   ```bash
   task lint
   task docs
   ```

## Authoring rules

- **New skills** are scaffolded via `/nolte-shared:skill-management`. Do not hand-roll the folder layout.
- **New agents** are drafted via the `claude-plugin-developer` agent; pick agent over skill only when `spec/claude/skill-vs-agent/` says so.
- **Specs** are authored and translated via `/nolte-shared:spec`. EN is canonical; DE is a kept-in-sync translation.
- **Reviews** for existing skills and agents use `/nolte-shared:skill-review` and `/nolte-shared:agent-review`. They produce review plans under `.audits/`; that is where follow-up work lives.

## Pull request workflow

- Branch naming and PR shape follow `spec/project/pull-request-workflow/` and `spec/project/branching-model/`.
- The PR template at `.github/pull_request_template.md` is the expected body shape (Summary, Changes, Linked issues, Testing, Risk / rollout notes). `/nolte-shared:pull-request-create` fills it correctly.
- PRs target `develop`. The required status checks on `develop` are `lint`, `test`, and `docs` (see `.github/settings.yml`).
- `main` is advanced by a fast-forward on release only — do not open PRs directly against `main`.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat(...)`, `fix(...)`, `chore(...)`, …). The scope typically names the affected skill, agent, or spec topic — for example `feat(spec,skills): add quality-gate spec and skill`.

## License of contributions

By contributing, you agree that your contributions are licensed under the MIT license of this repository (see `LICENSE`).
