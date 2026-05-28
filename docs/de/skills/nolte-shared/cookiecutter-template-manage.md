---
title: cookiecutter-template-manage
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# cookiecutter-template-manage

> Verwaltet den Cookiecutter-Template-Lebenszyklus: scaffolden, überarbeiten, Hooks absichern, pytest-cookies einrichten.

_Manages the lifecycle of a Cookiecutter template: scaffolds a new template or refactors an existing one (with mid-flow user confirmation of variable names and choice defaults), hardens Cookiecutter hooks, and sets up a pytest-cookies test harness. Invoke when the user says "manage a Cookiecutter template lifecycle", "scaffold or refactor a Cookiecutter template (with name + purpose confirmation)", "harden cookiecutter hooks", "set up pytest-cookies harness", "Cookiecutter-Template anlegen", "Cookiecutter-Template überarbeiten", "Cookiecutter-Hook absichern", or "pytest-cookies einrichten". Don't use for plain template consumption (a bare `cookiecutter <url>` call needs no orchestration), generic Python bootstrap, Copier or cruft work, or intentionally diverging templates. Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `scaffolding`
- **Quelle:** [skills/cookiecutter-template-manage/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/cookiecutter-template-manage/SKILL.md)

## Anwenden wenn

- you want to scaffold a new Cookiecutter template
- you want to refactor an existing Cookiecutter template
- you want to harden Cookiecutter hooks (pre_prompt / pre_gen / post_gen)
- you want to set up a pytest-cookies test harness for a template

## Siehe auch

- [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md)

---

## Cookiecutter Template Manage

Orchestrates the full Cookiecutter template lifecycle. The skill owns all mid-flow user confirmations — variable names, choice defaults, hook additions that affect generated output — then dispatches the [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md) agent for the pure authoring step once every decision is locked in. The agent never asks for approvals; that dialogue belongs here.

### Why this is a skill, not an agent

- **Mid-flow confirmations are the load-bearing interaction** — variable-name proposals, choice-default selections, and one-way hook additions all require explicit user sign-off before any file is written. An agent's fire-and-forget contract forfeits those checkpoints; a skill's conversational turn model owns them.
- **Orchestrator role** — per `spec/claude/skill-vs-agent/en.md` §Hybrid pattern, when a workflow's orchestration requires user dialogue but the execution step benefits from a narrow specialist, the orchestrator is a skill and the executor is an agent. This skill is the orchestrator; [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md) is the executor.
- **Output flows back into the main conversation** — confirmation of variable names, the pre-dispatch decision summary, and the post-agent follow-up checklist are all part of the user's working context and must not be buried in a structured agent report.
- Counter-dimension considered: the authoring step itself (reading every template file, running `cookiecutter --no-input`, executing `pytest`) benefits from a narrow system prompt and context-window isolation — that dimension favours an agent for the execution step, which is exactly the hybrid this skill implements.

### German trigger phrases

- "Cookiecutter-Template anlegen"
- "neues Cookiecutter-Template für ein nolte-Projekt"
- "Cookiecutter-Template überarbeiten / refactorn"
- "Cookiecutter-Hook absichern / härten"
- "pytest-cookies Test-Harness einrichten"
- "cookiecutter-template-author beauftragen"

### Preconditions

Before entering any operation, verify:

1. **`cookiecutter` is importable** (`python3 -c 'import cookiecutter'`). If missing: stop and report `pip install cookiecutter` (or `pipx install cookiecutter`); do not install it yourself.
2. **Bound spec corpus is reachable.** The agent reads the specs at runtime; confirm that `spec/project/cookiecutter-template-authoring/` exists in the caller's repository. If it is absent, stop and report the missing spec — the agent cannot run without it.
3. **Caller intent is unambiguous for every one-way decision** before dispatching the agent. Variable renames, new choice defaults, and hook additions that alter generated output are surfaced here, confirmed interactively, and locked into the dispatch payload. The agent receives a fully resolved set of decisions and never asks for approval itself.

### Operations

#### 1. scaffold

Create a brand-new Cookiecutter template end-to-end.

1. **Collect purpose and name** — ask the user for a one-sentence purpose and a proposed template slug (ASCII kebab-case). Confirm both before proceeding.
2. **Propose variable list** — derive an initial set of `cookiecutter.json` variables from the stated purpose. Present the proposed names and description, and wait for explicit user confirmation or edits. Iterate until the user approves the final variable list.
3. **Propose choice defaults** — for every variable that is a choice list, show the proposed ordering (first item = default) and wait for explicit user confirmation. Apply Hard rule: never insert a new choice at position 0 on an existing list.
4. **Lock decisions** — summarise the approved variable names, defaults, and any hook additions in a single confirmation message. Proceed only after the user replies affirmatively.
5. **Dispatch [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md)** — pass the locked decisions as the explicit precondition payload. The agent runs in `scaffold` mode and returns a structured report (files created, anti-pattern audit, spec-conformance audit, local bake result).
6. **Surface follow-ups** — relay the agent's caller follow-ups (commit, PR, test-suite CI) to the user; do not perform them yourself.

#### 2. refactor

Overhaul an existing Cookiecutter template to remove anti-patterns and close spec-conformance gaps.

1. **Identify template root** — confirm the absolute path to the existing template directory with the user.
2. **Audit surface** — before the agent runs, inspect `cookiecutter.json` for variable names and choice defaults that may need renaming or reordering. Surface each one-way change to the user (variable rename, choice reorder, hook addition) and collect explicit approval. A rename without approval is a hard stop.
3. **Lock decisions** — produce the same approval summary as in `scaffold` operation step 4.
4. **Dispatch [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md)** in `refactor` mode with the locked decisions as context.
5. **Surface the agent's Spec drift section** (when present) back to the user verbatim — the user may have intentional divergences; this skill does not resolve them silently.
6. **Relay follow-ups** as above.

#### 3. update

Add or harden a hook, extend the test harness, or add a CI matrix to an existing template without a full refactor.

1. **Clarify scope** — determine whether the update is `hook` mode (author/harden `pre_prompt.py`, `pre_gen_project.py`, `post_gen_project.py`) or `tests` mode (add or extend pytest-cookies tests, optionally with a GitHub Actions matrix). If both are needed, run two sequential dispatches.
2. **Surface any one-way changes** — a new hook that alters generated output, or a test that changes existing default behaviour, requires user confirmation before dispatch.
3. **Dispatch [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md)** in the appropriate mode (`hook` or `tests`).
4. **Relay follow-ups** as above.

### Examples

- Read `examples/01-scaffold-new-template.md` when scaffolding a brand-new template with mid-flow variable-name and choice-default confirmations.
- Read `examples/02-refactor-existing-template.md` when refactoring an existing template and surfacing one-way changes before dispatching the agent.
- Read `examples/03-update-hook-and-tests.md` when adding or hardening a hook and extending the pytest-cookies test harness.

### Gotchas

- **The agent never asks for variable-name or choice-default approval** — that dialogue happens here, in this skill, before the dispatch. If the agent surfaces a question mid-run, it indicates a missing decision in the dispatch payload; stop, resolve it here, and re-dispatch.
- **The spec corpus is read by the agent at runtime from the caller's repository** — if `spec/project/cookiecutter-template-authoring/` is missing, the agent stops immediately. Resolve the missing spec before retrying the dispatch.
- **One-way decisions (variable rename, choice reorder, hook addition that alters output) are irreversible once the agent writes files** — the confirmation step in every operation is not optional; skipping it risks breaking existing `.cookiecutterrc` files and CI invocations in downstream consumers.
- **[`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md) is not a top-level entry point** — it is designed to receive a fully resolved preconditions payload from this skill. Invoking it directly from the main conversation bypasses the variable-name and choice-default approval flow and may produce a template that diverges from the caller's actual intent.
- **Local bake verification is the agent's responsibility** — this skill does not re-run `cookiecutter --no-input` after the agent returns; trust the agent's bake result. If the agent reports a bake failure, relay the raw error to the user and do not mark the operation complete.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/cookiecutter-template-manage/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- Never dispatch [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md) before every one-way decision for the current operation is explicitly confirmed by the user.
- Never resolve a Spec drift conflict silently; always surface it to the user verbatim and wait for their decision.
- Never install Python packages on the caller's machine; report the exact `pip install` command and stop.
- Never commit, push, bump versions, tag releases, or open pull requests; these are caller follow-ups.
- Never re-invoke this skill recursively or dispatch sibling agents other than [`cookiecutter-template-author`](../../agents/nolte-shared/cookiecutter-template-author.md).
- When `spec/claude/skill-vs-agent/en.md` or `spec/project/cookiecutter-template-authoring/` disagrees with these instructions, the spec wins. Surface the conflict to the user rather than silently diverging.

### Multi-model testing

When testing this skill against different Claude models:

- **Confirmation gate**: verify that the skill does not dispatch the agent before printing the variable-name and choice-default confirmation message and receiving an affirmative reply. A model that skips directly to dispatch fails this gate.
- **One-way change detection**: present a `cookiecutter.json` with an existing choice list and ask the skill to add a new option. Verify it proposes appending to the end (not inserting at position 0) and surfaces this as a one-way decision requiring confirmation.
- **Spec-drift relay**: simulate an agent report that contains a "Spec drift" section. Verify the skill relays the section verbatim rather than summarising or resolving it on the user's behalf.
- **Follow-up relay**: verify the skill relays the agent's "Caller follow-ups" list without performing any of the listed actions (no commit, no PR, no version bump).
