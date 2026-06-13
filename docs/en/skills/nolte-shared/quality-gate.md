---
title: quality-gate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# quality-gate

> Runs the project's lint + typecheck + test gate in parallel and tabulates which checks failed.

_Run the project's lint + typecheck + test gate in parallel, tabulate the results, and call out exactly which checks failed so the caller can triage before a commit, a PR, or a release. Prefers repository-declared Taskfile targets (`task lint`, `task test`, `task typecheck`, `task check`) when they exist so project conventions and ignore lists are honoured; otherwise detects and runs the native tooling directly (ruff, pytest, eslint, tsc, vitest, go test, cargo test, and similar). Invoke when the user asks to "run the quality gate," "run lint and tests," "make sure CI will pass," "run all checks before committing," or equivalent German-language requests. Don't use for CVE scanning or license compliance (those are dependency-audit's job, even when task lint wraps a security check) and don't use for documentation builds (those are a separate concern)._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `quality-gate`
- **Source:** [skills/quality-gate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/quality-gate/SKILL.md)

## Use when

- you want to run the project's quality gate before a commit, PR, or release
- you want a parallel lint + typecheck + test run with a tabulated outcome
- you want to verify CI will pass locally

## Don't use when

- **You want a CVE scan rather than the lint/typecheck/test gate** → [`dependency-audit`](dependency-audit.md)
- **You want a documentation build (mkdocs build)** → [`project-structure-apply`](project-structure-apply.md)

## See also

- [`dependency-audit`](dependency-audit.md)

## Referenced by

- [`component-test-reviewer`](../../agents/nolte-shared/component-test-reviewer.md)
- [`fullstack-developer`](../../agents/nolte-shared/fullstack-developer.md)
- [`integration-test-generator`](../../agents/nolte-shared/integration-test-generator.md)
- [`integration-test-reviewer`](../../agents/nolte-shared/integration-test-reviewer.md)
- [`quality-gate-enforcer`](../../agents/nolte-shared/quality-gate-enforcer.md)
- [`test-case-extractor`](../../agents/nolte-shared/test-case-extractor.md)
- [`unit-test-generator`](../../agents/nolte-shared/unit-test-generator.md)
- [`unit-test-reviewer`](../../agents/nolte-shared/unit-test-reviewer.md)
- [`test-pyramid-check`](test-pyramid-check.md)

---

## Quality Gate

Run every lint, typecheck, and test step the project declares, in parallel, and report the outcome as a single table. This skill doesn't fix failures—it surfaces them with enough detail that the caller knows what to fix.

Implements `spec/project/quality-gate/` — the spec defines the gate composition contract, invocation requirements, and output shape. This skill binds those rules to the on-disk procedure.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Quality-Gate ausführen"
- "vor dem Commit prüfen"
- "Linting und Tests laufen lassen"

### User-language policy

Detect the user's language from their message and respond in it. The result table uses English column headers so the output stays diffable; prose around the table is localised.

### Inputs

- **Repo root**: default is the current working directory.
- **Scope override** (optional): caller may restrict the run to a named subset — "lint only," "tests only," "typecheck only," "fast" (lint + typecheck, skip tests).
- **Subroot filter** (optional): in a monorepo, caller may name a subroot (`backend/`, `frontend/`, `packages/foo/`) to scope the run.

### Operations

#### 1. Prefer Taskfile targets

If the repo root has `Taskfile.yml` or `Taskfile.yaml`, enumerate the declared targets:

```
task --list-all 2>/dev/null
```

Look for these target names, in order of preference:

| Category | Preferred target | Fallback targets |
|---|---|---|
| Composite | `check`, `quality`, `gate` | run the category-specific targets below instead |
| Lint | `lint` | `lint:backend`, `lint:frontend`, `ruff`, `eslint` |
| Typecheck | `typecheck`, `types` | `tsc`, `mypy` |
| Tests | `test` | `test:unit`, `test:backend`, `test:frontend`, `pytest`, `vitest` |

Rules for picking targets:

- If a **composite** target exists and clearly wraps lint + typecheck + tests (inspect its description and the commands it runs via `task --summary <name>`), run only that target and report its single pass/fail as the whole gate. Record which target was used.
- Otherwise, pick one target per category and run them **in parallel**. If a category has no target, fall through to native tooling detection (Step 2) for just that category.

Record every chosen target in the report so the caller can see what ran.

#### 2. Detect native tooling (fallback)

For any category not covered by a Taskfile target, detect the tooling from the manifests:

| Language | Lint | Typecheck | Tests |
|---|---|---|---|
| Python — `pyproject.toml` declares `[tool.ruff]` | `ruff check .` | `mypy .` or `pyright` only if configured | `pytest -q` |
| Python — `pyproject.toml` declares flake8 / pylint | that linter | same | `pytest -q` |
| Node — `package.json` has `lint` script | `npm run lint` (or `pnpm lint` / `yarn lint`) | `tsc -b` or `tsc --noEmit` if `tsconfig.json` exists | `npm test -- --run` (vitest) or the declared `test` script |
| Go — `go.mod` exists | `go vet ./...` (and `golangci-lint run` if installed) | `go build ./...` | `go test ./...` |
| Rust — `Cargo.toml` exists | `cargo clippy --all-targets -- -D warnings` | included in build | `cargo test` |

Detection rules:

- Use whichever package manager the repo actually uses. Check the lockfile name: `package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `uv.lock` → uv, `poetry.lock` → poetry.
- Run each detected tool from the subroot its manifest lives in, not from the repo root, unless the Taskfile already scopes it.
- For monorepos, run a detection pass per subroot with a manifest, then fan out parallel runs.

If a category has no detectable tooling and no Taskfile target, record it as `skipped: no tooling detected` rather than claiming pass.

#### 3. Run checks in parallel

Issue every chosen command in a single parallel batch. Each command **must** end with `; echo "EXIT:$?"` so the exit code survives through redirects and shell wrappers. Honour these timeouts:

- Lint: 2 minutes.
- Typecheck: 5 minutes.
- Tests: 10 minutes (raise if the project's Taskfile target clearly documents a longer run).

If a command times out, report it as `timeout` in the status column—don't retry.

#### 4. Parse each result

For every check, capture:

- **Status**: `pass`, `fail`, `skipped`, or `timeout`.
- **Exit code**.
- **Counters where parseable**: number of lint errors and warnings (ruff/eslint JSON), number of type errors (tsc output), number of passed/failed tests (pytest/vitest/go test summary line).
- **First failure snippet**: for failing checks, the first 10 lines of the actual failure output — enough for the caller to triage without re-running.

Project-local conventions that the skill **must** honour when the Taskfile target already honours them:

- A Taskfile wraps `ruff` with an ignore list → don't second-guess and run `ruff` directly.
- A Taskfile passes `--exclude` or `--testpaths` → don't override.

When running tools directly (Step 2 fallback), **don't** add project-local ignores the skill doesn't know about. Report the raw tool output and let the caller decide.

#### 5. Render the result table

```
| Check | Status | Runner | Details |
|---|---|---|---|
| Lint | pass/fail | `task lint` | <n> errors, <m> warnings (exit <code>) |
| Typecheck | pass/fail | `tsc -b` (detected) | <n> type errors (exit <code>) |
| Tests | pass/fail | `task test` | <passed>/<total> passed (exit <code>) |
```

The **Runner** column shows exactly what was invoked — the Taskfile target name or the detected command — so the caller can reproduce the failure locally.

The **Details** column **should** surface the underlying tool's exit code (the `EXIT:$?` value captured in Step 4) per `spec/project/quality-gate/` §Timeouts and failure handling, so the caller can tell "lint found 3 errors" (exit 1) apart from "lint crashed" (exit > 1).

Below the table, for every `fail` or `timeout` row, append a one-paragraph excerpt from the captured output (≤10 lines, fenced in a code block). Group excerpts by check.

#### 6. Overall verdict

- **All `pass`**: one-line green summary (`Quality gate passed — N checks green.`).
- **Any `fail` / `timeout`**: red summary naming the failed checks and pointing at the excerpts below the table.
- **`fast` scope (tests deliberately skipped)**: when the caller ran the `fast` scope (lint + typecheck, tests skipped), report the Tests row as `skipped` with the **Details** noting the deliberate fast-scope reason (for example `skipped: fast scope (pre-commit), tests deferred`), and have the verdict explicitly state that tests were skipped by design — for example `Quality gate (fast scope) passed — lint + typecheck green; tests skipped (fast scope).`. This is a **distinct** verdict note from `skipped: no tooling detected` below: the fast-scope skip is an intentional scoping decision, not a missing-tooling gap, and the caller must be able to tell the two apart per `spec/project/quality-gate/` §Triggers and §Output shape. A `fast` run is never reported as a full `pass`.
- **Any `skipped: no tooling detected`**: mention them explicitly in the summary so the caller can decide whether they're acceptable (a pure-Python repo genuinely has no frontend lint) or a misconfiguration (missing `ruff` config). Keep this distinct from the deliberate fast-scope skip above — the two skip reasons must never be collapsed into one undifferentiated `skipped`.

### Examples

- Read `examples/01-task-targets-when-available.md` when Taskfile targets exist and the skill should prefer them over direct tool invocation.
- Read `examples/02-native-fallback-no-taskfile.md` when no Taskfile is present and the skill must detect and run native tooling directly.
- Read `examples/03-multi-language-monorepo.md` when the repository has multiple language subroots that each need a separate parallel scan.

### Gotchas

- **Taskfile target may exist but wrap nothing**: `task --list-all` lists a target even if it contains no commands or calls a non-existent dependency; always inspect the target via `task --summary <name>` before relying on its output — an empty or broken target silently produces exit 0.
- **Tool detection order is not deterministic across repos**: a monorepo may carry both `pyproject.toml` and `package.json` at the root, making the detected lint/test runner ambiguous; always select the runner per the subroot where its manifest lives and document which runner was chosen in the `Runner` column.
- **Missing Taskfile target for a category is not a failure**: when `task lint` doesn't exist the skill falls through to native tooling — record `skipped: no tooling detected` rather than reporting `fail`; claiming fail without a detected tool is a false positive.

### Hard rules

- **Never** fix failures automatically. This skill surfaces them; fixing is a separate step the caller owns.
- **Never** run checks sequentially when parallel execution is possible and the project doesn't explicitly forbid it. Parallel is the default so feedback is fast.
- **Never** claim `pass` for a check that was skipped. `skipped` is a distinct status.
- **Never** report a `fast`-scope run (tests deliberately skipped) as a plain `pass`, and never collapse the deliberate fast-scope skip into the same verdict note as `skipped: no tooling detected`. The verdict must distinguish "tests skipped by design (fast scope), with the reason recorded in Details" from "tests skipped because no test tooling was detected." Both surface in the verdict; they are never merged.
- **Never** apply a project-specific lint ignore the skill guessed at. Respect Taskfile targets; run the raw tool when falling back.
- **Never** retry a timed-out check; report the timeout so the caller can decide whether the timeout was wrong or the test truly hangs.
- **Always** prefer Taskfile targets over direct tool invocation when a suitable target exists. That keeps project conventions in charge.
- **Always** report exactly what was invoked in the **Runner** column so the caller can reproduce any failure locally.
- **Always** include enough of the failure output (≤10 lines per failing check) that the caller doesn't need to re-run to triage.
- When `spec/project/quality-gate/` and this skill disagree, the spec wins; this skill needs the update.

### Why this is a skill, not an agent

This is a skill, not an agent, because:

- **Orchestration role**: quality gating is one step in a pre-commit / pre-PR flow; the output is meant to flow back into the main conversation so the caller can triage.
- **Interactivity**: the caller typically wants to decide what to do with a failure (fix now, defer, override) as part of the same conversation — skill bias.
- **Context-window impact is acceptable**: the output is compact (one table + short excerpts), so isolation wouldn't pay for itself.
- **Counter-dimension**: parallel execution is an agent-side dimension, but it's already achievable inside a skill via parallel `Bash` calls — it doesn't force the agent choice.
