# Example 03 — Update: harden a hook and extend the pytest-cookies harness

## Input prompt

> Für `cookiecutter-templates/nolte-python-lib/` brauche ich zwei Dinge:
> 1. Der `pre_gen_project.py`-Hook soll den Import-Namen gegen den
>    Python-Identifier-Regex validieren und mit `sys.exit(1)` abbrechen.
> 2. Die pytest-cookies Tests sollen eine Matrix über `include_ci = [true, false]`
>    abdecken, inklusive GitHub Actions CI-Matrix für OS × Python-Version.

## Input files

- `cookiecutter-templates/nolte-python-lib/hooks/` — directory exists but
  `pre_gen_project.py` is absent.
- `cookiecutter-templates/nolte-python-lib/tests/` — absent (no test harness yet).
- `cookiecutter-templates/nolte-python-lib/cookiecutter.json` (existing):

  ```json
  {
    "project_name": "My Library",
    "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
    "import_name": "my_library",
    "author_name": "Jane Doe",
    "author_email": "jane@example.com",
    "include_ci": true
  }
  ```

- `spec/project/cookiecutter-template-authoring/en.md` — present.

## Expected behaviour

### Step 1 — Scope clarification

Skill identifies two discrete sub-tasks:

- Sub-task A: `hook` mode — author `hooks/pre_gen_project.py`
- Sub-task B: `tests` mode — create `tests/test_bake.py` with matrix and CI matrix

Skill confirms both scopes with the user. Two sequential dispatches will run.

### Step 2 — One-way change check (hook)

A new `pre_gen_project.py` hook that calls `sys.exit(1)` on an invalid
`import_name` will cause template bakes with non-identifier slugs to fail.
This is a behaviour change for existing consumers.

Skill surfaces this:

> Adding `hooks/pre_gen_project.py` with slug-validation will cause bakes
> with a non-identifier `import_name` (e.g. `my-lib`) to fail with a clear
> error message. Existing consumers that already pass a valid `import_name`
> are unaffected. Confirm?

User replies: "ja".

### Step 3 — Dispatch A: hook mode

Skill dispatches `cookiecutter-template-author` in `hook` mode.
The agent authors `hooks/pre_gen_project.py` using the canonical slug-validation
idiom (see agent's `## Reference idioms`):

```python
# hooks/pre_gen_project.py — slug validation
import re
import sys

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"
module_name = "{{ cookiecutter.import_name }}"

if not re.match(MODULE_REGEX, module_name):
    print(f"ERROR: {module_name} is not a valid Python module name (use _ not -)")
    sys.exit(1)
```

Agent bakes locally to confirm the hook fires correctly and returns the report.

### Step 4 — Dispatch B: tests mode

Skill dispatches `cookiecutter-template-author` in `tests` mode.
The agent creates:

- `tests/test_bake.py` with a smoke test plus a `include_ci` parametrized matrix:

  ```python
  import pytest

  @pytest.fixture(params=[True, False], ids=["ci", "no-ci"])
  def include_ci(request):
      return request.param

  def test_bake_matrix(cookies, include_ci):
      result = cookies.bake(extra_context={
          "project_name": "Test Library",
          "import_name": "test_library",
          "include_ci": include_ci,
      })
      assert result.exit_code == 0
      assert result.exception is None
      assert result.project_path.is_dir()
  ```

- `.github/workflows/test-template.yml` with an OS × Python-version matrix
  (`ubuntu-latest` / `macos-latest` × `3.11` / `3.12`).

Agent runs `pytest` in the template root and reports the raw output.

### Step 5 — Follow-ups relayed

Skill relays the combined follow-ups from both agent runs:

1. Review `hooks/pre_gen_project.py` — confirm the regex covers all valid import names.
2. Run `pytest cookiecutter-templates/nolte-python-lib/` locally to verify the matrix.
3. Commit the hook, test file, and CI workflow together.
4. Open a pull request.

## What the skill does NOT do

- Does not skip the one-way-change confirmation for the new hook.
- Does not merge both dispatches into a single agent invocation (modes are separate).
- Does not run `pytest` itself — that is the agent's responsibility.
- Does not commit or push.
