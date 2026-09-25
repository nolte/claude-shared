---
artifact-type: issue-orchestration-analysis
repo: "nolte/claude-shared"
issue: "667"
classification: "feature-request"
secondary-classes: [infra]
route: "direct"
status: implemented
created: "2026-09-25"
---

# Issue Orchestration — Pre-analysis

Group context: `issue-batch-orchestrate` run `20260925T071908Z-b7c2`, group
`2026-09-25-consumer-reachability`, integration branch `feat/2026-09-25-consumer-reachability`.
This run does not open a pull request; the bundle does.

## Issue metadata

- **Repository**: nolte/claude-shared
- **Issue**: #667 — Expose scripts/validate_skills.py as a pre-commit hook (.pre-commit-hooks.yaml)
- **URL**: <https://github.com/nolte/claude-shared/issues/667>
- **Labels**: none
- **Linked items**: none; consumer trigger `nolte/claude-goose` feature 005 `OMISSIONS.md`
- **Prior art checked**: no open PR; the hub's own `.pre-commit-config.yaml:51-56` runs the validator as a `repo: local` / `language: system` hook with `pass_filenames: false`; `.pre-commit-config.yaml:72-78` shows the `language: python` + `additional_dependencies` pattern already in use
- **Trusted author**: `nolte` (repository owner)

## Classification

- **Primary class**: feature-request
- **Secondary class(es)**: infra (packaging / hook wiring)
- **Rationale**: a new consumer-facing contract (hook id pinned by `rev:`); nothing is broken for the hub itself
- **Asserted cause verified**: the issue's premise "takes a target path" is **refuted as sufficient** — `scripts/validate_skills.py:36` `REPO = Path(__file__).resolve().parent.parent`; `:974` and `:1005` `p = REPO / t` resolve every target against the validator's own clone; `:991` `path.relative_to(REPO)` raises `ValueError` for a path outside it. A consumer path passed by pre-commit would be looked up inside pre-commit's clone of this repository, not in the consumer. Second measurement: `pip install <this repo>` into a fresh venv (2026-09-25) fails at build time with `setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions … Please remove: License :: OSI Approved :: MIT License` — so a `language: python` hook cannot install today.

## Requirements gate

No `project/requirements/` artifact exists for #667. **Operator override** recorded at the
group write gate (2026-09-25): the issue carries the consumer's exact expected snippet;
the operator chose `language: python`; acceptance is mechanical (`pre-commit try-repo`).

## Scope

- **In scope**: CWD-relative target resolution in `main()`; a `validate-skills` console script; installable `pyproject.toml`; `.pre-commit-hooks.yaml`; tests; the hub's own hook aligned; consumer docs snippet
- **Out of scope**: retiring the validator for `skills-ref` (docstring note); changing any check's semantics; hub-only checks (description baselines, backlog drains) — they stay keyed to hub-relative paths and are inert for consumers

## Route

- **Decision**: direct
- **Rationale**: one outcome, one PR strand, no roadmap item

## Work packages

### P1 — Validator resolves targets against the caller's repository

- **Problem statement**: Hypothesis: `main()` should resolve targets and report paths relative to `Path.cwd()` (pre-commit runs hooks from the consumer's repo root and passes filenames relative to it), while `REPO` stays for hub-only checks keyed to hub-relative paths (`AGENT_DESC_BASELINE_CHARS` `:910-916`, `check_spec_fallback_backlog` `:834`, `check_rpi_backlog` `:652`, `discover_default_targets` `:950`). A `--version` flag and the exit-code contract (0 / 1 on Critical / 2 internal) stay. The specialist may refute the cwd choice if the hub's `task validate:skills` (`Taskfile.yml:173-182`, runs from the repo root with no args) or `tests/test_validate_skills.py` (uses `v.REPO` at `:128`, `:135`, `:145`) would break; the refutation must name the call site.
- **Acceptance criteria**: (a) from a temporary directory containing `skills/x/SKILL.md` with broken frontmatter, `python3 <hub>/scripts/validate_skills.py skills/x/SKILL.md` exits 1 and names `skills/x/SKILL.md` (not a hub path); (b) the same call with a valid skill exits 0; (c) `python3 -m pytest tests/test_validate_skills.py -q` passes, with new tests covering (a)/(b) via `monkeypatch.chdir(tmp_path)`; (d) `python3 scripts/validate_skills.py` from the hub root produces the same finding set as before the change (capture before/after, diff empty); (e) `pre-commit run validate-skills --all-files` in the hub passes
- **Touched files / artifacts**: `scripts/validate_skills.py`, `tests/test_validate_skills.py`
- **Specialist**: `nolte-engineering:fullstack-developer` (description: "turns a sharply-scoped requirement into production-ready, runnable code … plus matching tests")
- **Depends on**: none

### P2 — Console script, installable packaging, hook definition

- **Problem statement**: Hypothesis: `pyproject.toml` gains `[project.scripts] validate-skills = "validate_skills:main"` plus an explicit setuptools mapping (`[tool.setuptools] package-dir = {"" = "scripts"}`, `py-modules = ["validate_skills"]`) and drops the superseded license classifier so `pip install .` succeeds; `.pre-commit-hooks.yaml` declares `id: validate-skills`, `entry: validate-skills`, `language: python`, `additional_dependencies: ["PyYAML>=6"]`, `files:` matching `SKILL.md` under `skills/` and `*.md` under `agents/` (any depth), `pass_filenames: true`. The specialist may refute the packaging shape (e.g. if `py-modules` from a subdirectory does not build) and choose another shape that keeps the console-script name.
- **Acceptance criteria**: (a) `pip install <hub>` into a fresh venv exits 0 and `validate-skills --version` prints the validator version; (b) `pre-commit try-repo <hub> validate-skills --all-files` from the hub root exits 0; (c) the same `try-repo` from a temporary consumer repo with one broken skill exits non-zero naming that file; (d) the hub's own `.pre-commit-config.yaml` hook keeps passing (`pre-commit run validate-skills --all-files`); (e) `task test` exits 0
- **Touched files / artifacts**: `pyproject.toml`, `.pre-commit-hooks.yaml` (new), `.pre-commit-config.yaml` (only if the local hook must change)
- **Specialist**: `nolte-engineering:fullstack-developer`
- **Depends on**: P1

### P3 — Consumer documentation

- **Problem statement**: consumers need the pin snippet from the issue (`repo: https://github.com/nolte/claude-shared`, `rev: <tag>`, `hooks: [id: validate-skills]`). `README.md` is at 201 lines against the 200-line budget of `spec/project/readme-structure/`, so the snippet lands in `docs/en/using.md` §"Install it in your project" (`:62`) with the `docs/de/using.md` counterpart.
- **Acceptance criteria**: (a) both language pages carry the snippet; (b) `task docs` (mkdocs `--strict`) exits 0; (c) `pre-commit run --files docs/en/using.md docs/de/using.md` passes (Vale, markdownlint)
- **Touched files / artifacts**: `docs/en/using.md`, `docs/de/using.md`
- **Specialist**: no matching specialised agent — generalist remediation (`nolte-shared:audience-doc-author` matches by description but requires an `audience-identify` artifact that this repository does not carry; producing one for a ten-line snippet is disproportionate)
- **Depends on**: P2

## Dependency ordering

P1 → P2 → P3.

## Risks

- **Flat-layout discovery**: after the classifier is removed, setuptools may report "Multiple top-level packages discovered" (`tests/__init__.py`, `evals/__init__.py`); the explicit `py-modules` mapping is the mitigation and is measured by P2 (a).
- **Hub tests bound to `REPO`**: keep `REPO` for hub-only checks; only target resolution moves to cwd (P1 (d) diff-empty check guards behaviour).
- **PyYAML absence** would silently weaken the strict-parse check (`:32-34`); `additional_dependencies` pins it in the hook env.
- **`pass_filenames: true`** skips `check_agent_tree` / budget checks (directory-only paths at `:1004-1008`); acceptable for consumers, documented in the hook's `description`.

## Open questions

none

## Dispatch log

2026-09-25 P1 dispatched to nolte-engineering:fullstack-developer — cwd-relative resolution (`_display`, `root = Path.cwd()`), budget keyed via `resolve().relative_to(REPO)` (refutation recorded), 4 new tests; pytest 568 passed, before/after validator diff empty.
2026-09-25 P2 dispatched to nolte-engineering:fullstack-developer — `[project.scripts] validate-skills`, `[tool.setuptools]` py-modules mapping, license classifier removed, `.pre-commit-hooks.yaml`; pip install exit 0, try-repo hub Passed, consumer negative Failed exit 1.
2026-09-25 P3 generalist — snippet in docs/en/using.md and docs/de/using.md §Install; pre-commit Passed, mkdocs --strict built.
