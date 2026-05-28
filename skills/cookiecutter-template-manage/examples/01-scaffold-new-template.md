# Example 01 — Scaffold a new template (with mid-flow confirmations)

## Input prompt

> Leg bitte ein neues Cookiecutter-Template an für nolte-Python-Bibliotheken.
> Der Slug soll `nolte-python-lib` sein. Wir brauchen Variablen für
> Projektname, Import-Name, Autor und ob pytest + GitHub Actions CI
> enthalten sein soll.

## Input files

- `spec/project/cookiecutter-template-authoring/en.md` — present (agent reads it at runtime).
- `spec/project/project-structure/en.md` and sibling bound-corpus specs — present.
- No existing template at `cookiecutter-templates/nolte-python-lib/`.

## Expected behaviour

### Step 1 — Purpose and name confirmation

Skill responds in German (user-language policy). Confirms:

- Purpose: "nolte-spec-conformant Python-Bibliotheks-Template"
- Slug: `nolte-python-lib` (ASCII kebab-case, no collision found)

Waits for affirmative reply before proceeding.

### Step 2 — Variable-name proposals

Skill proposes the following `cookiecutter.json` variables and their order:

| # | Name | Type | Notes |
| - | ---- | ---- | ----- |
| 1 | `project_name` | string | Human-readable title |
| 2 | `project_slug` | string | Derived from `project_name` via Jinja filter |
| 3 | `import_name` | string | Python import identifier |
| 4 | `author_name` | string | Full name |
| 5 | `author_email` | string | Contact address |
| 6 | `include_ci` | boolean | Native JSON `true` (Hard rule #4) |

Skill presents this list and waits for explicit user confirmation or edits.
User approves the list as-is.

### Step 3 — Choice-default confirmation

`include_ci` is a boolean, not a choice list — no reorder confirmation needed.
Skill confirms this and moves on.

### Step 4 — Locked-decision summary

Skill prints a summary block:

```
Approved decisions
──────────────────
Variables (in order): project_name, project_slug, import_name,
  author_name, author_email, include_ci
Defaults: include_ci = true (native JSON boolean)
Hooks requested: post_gen_project.py (remove CI skeleton when include_ci = false)
Mode: scaffold
Template root: cookiecutter-templates/nolte-python-lib/
```

Skill asks "Alles korrekt? Dann dispatch ich den Agent." and waits for "ja".

### Step 5 — Agent dispatch

Skill dispatches `cookiecutter-template-author` in `scaffold` mode, passing the
locked-decision summary as the precondition payload. The agent:

- Writes `cookiecutter.json` with the approved variable list.
- Scaffolds `{{cookiecutter.project_slug}}/` with README, LICENSE, `.gitignore`,
  `src/{{cookiecutter.import_name}}/__init__.py`, and a minimal CI skeleton.
- Authors `hooks/post_gen_project.py` that removes the CI skeleton when
  `include_ci` is `false` (native-boolean form per Hard rule #4).
- Bakes locally with `cookiecutter --no-input` and runs the spec-conformance audit.
- Returns the structured report.

### Step 6 — Follow-ups relayed to user

Skill relays the agent's caller follow-ups verbatim:

1. Review the created files under `cookiecutter-templates/nolte-python-lib/`.
2. Run the test suite: `pytest cookiecutter-templates/nolte-python-lib/`.
3. Commit the new template directory.
4. Open a pull request on `develop`.

Skill does NOT commit, push, bump versions, or open a PR itself.

## What the skill does NOT do

- Does not skip the variable-name confirmation and dispatch immediately.
- Does not infer the variable list silently from the purpose statement.
- Does not install `cookiecutter` if missing — stops and reports the install command.
- Does not resolve a Spec drift finding from the agent silently.
