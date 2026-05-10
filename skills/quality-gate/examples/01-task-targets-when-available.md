# Eval scenario 01 — Taskfile targets are honoured

## Input prompt

> Run the quality gate before I open the PR.

## Input files

Repository root layout:

```
./
├── Taskfile.yml
├── pyproject.toml
├── src/
│   └── myapp/__init__.py
└── tests/
    └── test_smoke.py
```

`Taskfile.yml`:

```yaml
version: "3"

tasks:
  lint:
    desc: Lint the codebase with ruff (project-local ignore list)
    cmds:
      - ruff check . --extend-exclude vendor

  typecheck:
    desc: Static type-check with mypy
    cmds:
      - mypy src

  test:
    desc: Run the pytest suite
    cmds:
      - pytest -q
```

`pyproject.toml` declares `[tool.ruff]` and `[tool.mypy]`, so the underlying tools exist; there is **no** composite `check` / `quality` / `gate` target.

## Expected behaviour

1. Detect `Taskfile.yml`, run `task --list-all` to enumerate targets, and find `lint`, `typecheck`, `test` — but **no** composite target. Per Step 1 of the skill, fall through to the per-category targets.
2. Issue all three commands as a single parallel batch:
   - `task lint ; echo "EXIT:$?"` (timeout: 2 min)
   - `task typecheck ; echo "EXIT:$?"` (timeout: 5 min)
   - `task test ; echo "EXIT:$?"` (timeout: 10 min)
3. Do **not** invoke `ruff` / `mypy` / `pytest` directly — the Taskfile targets carry the project-local `--extend-exclude vendor` argument and the skill must not second-guess that ignore list (Hard rule: respect Taskfile targets).
4. Render the result table with the **Runner** column showing the exact `task <name>` invocation:

   ```
   | Check     | Status | Runner          | Details                       |
   |-----------|--------|-----------------|-------------------------------|
   | Lint      | pass   | `task lint`     | 0 errors, 0 warnings          |
   | Typecheck | pass   | `task typecheck`| 0 type errors                 |
   | Tests     | pass   | `task test`     | 12/12 passed                  |
   ```

5. Localise the prose around the table to the user's language (here: English) and emit the green one-line summary `Quality gate passed — 3 checks green.` per Step 6.
6. If any check fails, append a ≤10-line excerpt of the captured stderr/stdout below the table, grouped per failing check. Never auto-fix.
