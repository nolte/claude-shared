# Eval scenario 02 — Native fallback when no Taskfile exists

## Input prompt

> Linting und Tests laufen lassen, bevor ich committe.

## Input files

Repository root layout:

```
./
├── pyproject.toml
├── uv.lock
├── src/
│   └── widget/__init__.py
└── tests/
    └── test_widget.py
```

`pyproject.toml`:

```toml
[project]
name = "widget"
version = "0.1.0"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
```

There is **no** `Taskfile.yml`, **no** `[tool.mypy]` or `[tool.pyright]` section, and the lockfile is `uv.lock` (so the package manager is `uv`).

## Expected behaviour

1. Skip Step 1 (no `Taskfile.yml` / `Taskfile.yaml` present) and go straight to Step 2 — native tooling detection.
2. Detect Python via `pyproject.toml`; the `[tool.ruff]` table picks `ruff check .` for lint and `pytest -q` for tests.
3. Typecheck has **no** declared tool (no `[tool.mypy]`, no `[tool.pyright]`). Per Step 2, record it as `skipped: no tooling detected` — never claim `pass` for an unrun check (Hard rule).
4. Issue the two detected commands in a single parallel batch, each terminated with `; echo "EXIT:$?"`:
   - `ruff check . ; echo "EXIT:$?"` (timeout: 2 min)
   - `pytest -q ; echo "EXIT:$?"` (timeout: 10 min)
5. Do **not** add any project-local ignores the skill guessed at — only what `pyproject.toml` already configures (Hard rule). Run the raw tools.
6. Render the result table; the typecheck row keeps its `skipped` status with the reason in **Details**:

   ```
   | Check     | Status  | Runner          | Details                          |
   |-----------|---------|-----------------|----------------------------------|
   | Lint      | pass    | `ruff check .`  | 0 errors, 0 warnings             |
   | Typecheck | skipped | —               | no tooling detected              |
   | Tests     | fail    | `pytest -q`     | 7/8 passed, 1 failed             |
   ```

7. Antworte auf Deutsch (per User-language policy), und gib eine rote Zusammenfassung aus, die `Tests` als gefallen benennt und auf den Output-Auszug unter der Tabelle verweist. Erwähne den `skipped`-Eintrag explizit, damit der Caller entscheiden kann, ob das akzeptabel ist (Step 6).
8. Append a ≤10-line excerpt of the failing pytest output below the table, fenced in a code block. Never auto-fix.
