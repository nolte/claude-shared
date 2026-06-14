# Eval scenario 03 — Multi-language monorepo (Python + TypeScript)

## Input prompt

> Make sure CI will pass — run all checks across the repo.

## Input files

Repository root layout:

```
./
├── backend/
│   ├── pyproject.toml          # [tool.ruff], [tool.mypy], pytest config
│   ├── poetry.lock
│   ├── src/api/__init__.py
│   └── tests/test_api.py
├── frontend/
│   ├── package.json            # "scripts": { "lint": "eslint .", "test": "vitest run" }
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   └── src/index.ts
└── README.md
```

There is **no** root-level `Taskfile.yml` and **no** root-level manifest. Two subroots each carry their own manifest: `backend/` (Python, poetry) and `frontend/` (TypeScript, pnpm).

## Expected behaviour

1. Skip Step 1 (no `Taskfile.yml`) and run a per-subroot detection pass per Step 2 ("For monorepos, run a detection pass per subroot with a manifest, then fan out parallel runs").
2. Detect tooling per stack:
   - **backend/** — Python via `pyproject.toml` + `poetry.lock` (so use `poetry` if a wrapper is needed): `ruff check .` (lint), `mypy .` (typecheck — `[tool.mypy]` is configured), `pytest -q` (tests). Run from inside `backend/`.
   - **frontend/** — Node via `package.json` + `pnpm-lock.yaml` (so use `pnpm`): `pnpm lint` (lint, declared script), `tsc --noEmit` (typecheck — `tsconfig.json` exists), `pnpm test -- --run` (vitest, declared `test` script). Run from inside `frontend/`.
3. Issue **all six** commands as a single parallel batch (Hard rule: parallel by default). Each command terminated with `; echo "EXIT:$?"`. Honour the per-category timeouts (lint 2 min, typecheck 5 min, tests 10 min) per check, not per stack.
4. Tabulate **per stack** so the caller can see which stack failed. The Runner column shows the exact command and the working directory it ran in:

   ```
   | Stack    | Check     | Status | Runner                     | Details                |
   |----------|-----------|--------|----------------------------|------------------------|
   | backend  | Lint      | pass   | `ruff check .` (backend/)  | 0 errors, 0 warnings   |
   | backend  | Typecheck | fail   | `mypy .` (backend/)        | 3 type errors          |
   | backend  | Tests     | pass   | `pytest -q` (backend/)     | 24/24 passed           |
   | frontend | Lint      | pass   | `pnpm lint` (frontend/)    | 0 errors, 2 warnings   |
   | frontend | Typecheck | pass   | `tsc --noEmit` (frontend/) | 0 type errors          |
   | frontend | Tests     | fail   | `pnpm test -- --run`       | 41/43 passed, 2 failed |
   ```

5. Below the table, append ≤10-line excerpts grouped per failing check (`backend / Typecheck` and `frontend / Tests` here). Each excerpt fenced in a code block.
6. Emit the red one-line summary naming the failed checks (Step 6): `Quality gate failed — backend/Typecheck and frontend/Tests are red; see excerpts below.`
7. Do **not** apply any project-local lint ignores the skill guessed at (Hard rule). Do **not** retry timeouts. Do **not** auto-fix.
8. If the caller had supplied a **subroot filter** ("only run frontend"), the skill would have scoped the parallel batch to the three `frontend/` checks and tabulated only those rows.
