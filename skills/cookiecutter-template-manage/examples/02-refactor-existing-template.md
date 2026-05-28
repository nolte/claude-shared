# Example 02 — Refactor an existing template (surface one-way changes)

## Input prompt

> Das Template unter `cookiecutter-templates/nolte-service/` hat noch die
> alte `"y"/"n"`-String-Konvention für Booleans und der Variablenname
> `project_name` soll zu `service_name` umbenannt werden.
> Bitte refactorn und spec-konform machen.

## Input files

- `cookiecutter-templates/nolte-service/cookiecutter.json` (existing):

  ```json
  {
    "project_name": "my-service",
    "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
    "use_docker": "y",
    "include_ci": "y"
  }
  ```

- `cookiecutter-templates/nolte-service/hooks/post_gen_project.py` (existing):
  uses `"{{ cookiecutter.use_docker }}".lower() != "y"` guards.
- `spec/project/cookiecutter-template-authoring/en.md` — present.

## Expected behaviour

### Step 1 — Template root confirmation

Skill confirms absolute path:
`/home/nolte/repos/my-portfolio/cookiecutter-templates/nolte-service/`

Waits for user to confirm this is the correct target.

### Step 2 — One-way change audit

Before dispatching the agent, the skill inspects `cookiecutter.json` and surfaces
every one-way change that requires explicit approval:

**Change A — Variable rename (one-way)**

> `project_name` → `service_name`
>
> This is a breaking rename. Any existing `.cookiecutterrc` or CI invocation
> that passes `project_name=…` will silently fail after the rename.
>
> The agent will add a `pre_prompt.py` migration shim that maps `project_name`
> to `service_name` for one release cycle (Hard rule #9). Confirm to proceed?

User replies: "ja, mit Shim bitte".

**Change B — Boolean convention migration (non-breaking for `scaffold`, one-way for existing consumers)**

> `"use_docker": "y"` and `"include_ci": "y"` will be converted to
> native JSON booleans `true` / `false` (Hard rule #4).
>
> The hook guards in `post_gen_project.py` will be updated to the
> native-boolean form. Existing consumers that pass `use_docker=y` via
> CLI will still work (Cookiecutter coerces truthy strings to booleans
> in ≥ 2.2). Confirm?

User replies: "ja".

### Step 3 — Locked-decision summary

```
Approved decisions
──────────────────
Variable rename: project_name → service_name (with pre_prompt.py shim)
Boolean migration: use_docker, include_ci → native JSON true/false
Hook update: post_gen_project.py guards → native-boolean form
Mode: refactor
Template root: cookiecutter-templates/nolte-service/
```

Skill asks for final confirmation before dispatch.

### Step 4 — Agent dispatch

Skill dispatches `cookiecutter-template-author` in `refactor` mode, passing the
locked-decision summary. The agent:

- Adds `hooks/pre_prompt.py` with the `project_name` → `service_name` shim.
- Migrates `use_docker` and `include_ci` to native JSON booleans in `cookiecutter.json`.
- Updates hook guards to the native-boolean form.
- Bakes locally and runs the spec-conformance audit.
- Returns the structured report including anti-pattern audit (rule #4 and #9 fixed).

### Step 5 — Spec drift relay

The agent's report includes a "Spec drift" section:

> `spec/project/project-structure/en.md` MUST: `.github/settings.yml` must be present.
> Status: fail — the rendered project is missing `.github/settings.yml`.
> Proposed fix: add a minimal `{{cookiecutter.project_slug}}/.github/settings.yml`
> from the nolte template.

Skill relays this section verbatim to the user and asks whether to re-dispatch the
agent with the fix included. Skill does NOT apply the fix silently.

### Step 6 — Follow-ups relayed

Skill relays the agent's caller follow-ups:

1. Review `hooks/pre_prompt.py` shim — schedule removal after one release cycle.
2. Test with existing consumers that pass `project_name=…` via CLI.
3. Commit and open a PR.

## What the skill does NOT do

- Does not dispatch the agent before receiving explicit confirmation for Change A
  and Change B.
- Does not resolve the Spec drift finding by re-dispatching silently.
- Does not perform the commit or PR itself.
