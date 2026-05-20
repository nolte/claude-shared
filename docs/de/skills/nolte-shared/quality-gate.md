---
title: quality-gate
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# quality-gate

_Run the project's lint + typecheck + test gate in parallel, tabulate the results, and call out exactly which checks failed so the caller can triage before a commit, a PR, or a release. Prefers repository-declared Taskfile targets (`task lint`, `task test`, `task typecheck`, `task check`) when they exist so project conventions and ignore lists are honoured; otherwise detects and runs the native tooling directly (ruff, pytest, eslint, tsc, vitest, go test, cargo test, and similar). Invoke when the user asks to "run the quality gate," "run lint and tests," "make sure CI will pass," "run all checks before I commit," or equivalent German-language requests. Don't use for security/CVE scanning (that's `dependency-audit`) and don't use for documentation builds (those are a separate concern)._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `quality-gate`
- **Quelle:** [skills/quality-gate/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/quality-gate/SKILL.md)

---

## Quality Gate

Run every lint, typecheck, and test step the project declares, in parallel, and report the outcome as a single table. This skill doesn't fix failures—it surfaces them with enough detail that the caller knows what to fix.

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

### Operation

#### Step 1: Prefer Taskfile targets

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

#### Step 2: Detect native tooling (fallback)

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

#### Step 3: Run checks in parallel

Issue every chosen command in a single parallel batch. Each command **must** end with `; echo "EXIT:$?"` so the exit code survives through redirects and shell wrappers. Honour these timeouts:

- Lint: 2 minutes.
- Typecheck: 5 minutes.
- Tests: 10 minutes (raise if the project's Taskfile target clearly documents a longer run).

If a command times out, report it as `timeout` in the status column—don't retry.

#### Step 4: Parse each result

For every check, capture:

- **Status**: `pass`, `fail`, `skipped`, or `timeout`.
- **Exit code**.
- **Counters where parseable**: number of lint errors and warnings (ruff/eslint JSON), number of type errors (tsc output), number of passed/failed tests (pytest/vitest/go test summary line).
- **First failure snippet**: for failing checks, the first 10 lines of the actual failure output — enough for the caller to triage without re-running.

Project-local conventions that the skill **must** honour when the Taskfile target already honours them:

- A Taskfile wraps `ruff` with an ignore list → don't second-guess and run `ruff` directly.
- A Taskfile passes `--exclude` or `--testpaths` → don't override.

When running tools directly (Step 2 fallback), **don't** add project-local ignores the skill doesn't know about. Report the raw tool output and let the caller decide.

#### Step 5: Render the result table

```
| Check | Status | Runner | Details |
|---|---|---|---|
| Lint | pass/fail | `task lint` | <n> errors, <m> warnings |
| Typecheck | pass/fail | `tsc -b` (detected) | <n> type errors |
| Tests | pass/fail | `task test` | <passed>/<total> passed |
```

The **Runner** column shows exactly what was invoked — the Taskfile target name or the detected command — so the caller can reproduce the failure locally.

Below the table, for every `fail` or `timeout` row, append a one-paragraph excerpt from the captured output (≤10 lines, fenced in a code block). Group excerpts by check.

#### Step 6: Overall verdict

- **All `pass`**: one-line green summary (`Quality gate passed — N checks green.`).
- **Any `fail` / `timeout`**: red summary naming the failed checks and pointing at the excerpts below the table.
- **Any `skipped: no tooling detected`**: mention them explicitly in the summary so the caller can decide whether they're acceptable (a pure-Python repo genuinely has no frontend lint) or a misconfiguration (missing `ruff` config).

### Hard rules

- **Never** fix failures automatically. This skill surfaces them; fixing is a separate step the caller owns.
- **Never** run checks sequentially when parallel execution is possible and the project doesn't explicitly forbid it. Parallel is the default so feedback is fast.
- **Never** claim `pass` for a check that was skipped. `skipped` is a distinct status.
- **Never** apply a project-specific lint ignore the skill guessed at. Respect Taskfile targets; run the raw tool when falling back.
- **Never** retry a timed-out check; report the timeout so the caller can decide whether the timeout was wrong or the test truly hangs.
- **Always** prefer Taskfile targets over direct tool invocation when a suitable target exists. That keeps project conventions in charge.
- **Always** report exactly what was invoked in the **Runner** column so the caller can reproduce any failure locally.
- **Always** include enough of the failure output (≤10 lines per failing check) that the caller doesn't need to re-run to triage.

### Rationale

This is a skill, not an agent, because:

- **Orchestration role**: quality gating is one step in a pre-commit / pre-PR flow; the output is meant to flow back into the main conversation so the caller can triage.
- **Interactivity**: the caller typically wants to decide what to do with a failure (fix now, defer, override) as part of the same conversation — skill bias.
- **Context-window impact is acceptable**: the output is compact (one table + short excerpts), so isolation wouldn't pay for itself.
- **Counter-dimension**: parallel execution is an agent-side dimension, but it's already achievable inside a skill via parallel `Bash` calls — it doesn't force the agent choice.
