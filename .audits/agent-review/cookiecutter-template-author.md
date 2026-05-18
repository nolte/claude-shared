---
review-type: agent-review
target: "agents/cookiecutter-template-author.md"
target-kind: agent
specs-applied:
  - slug: agent-management
    revision: "11deafb"
  - slug: skill-vs-agent
    revision: "45418ab"
  - slug: review-plan
    revision: "3f5c312"
  - slug: agent-review
    revision: "11deafb"
repo-revision: "73829d7"
created: "2026-05-18"
status: complete
---

# Agent Review: cookiecutter-template-author

## Scope

Target: `agents/cookiecutter-template-author.md` (149 lines, single file, no sibling assets under `agents/cookiecutter-template-author/`). Reviewed: YAML frontmatter, full markdown body (Rationale, Tool-selection rationale, Scope and boundaries, Preconditions, Output contract, Working procedure, Hard rules, Reference idioms).
Specs applied: `agent-management`, `skill-vs-agent`, `review-plan`, `agent-review` (revisions recorded in frontmatter).
Narrowing: none.
Explicitly out of scope: runtime behavior of the agent (i.e. actually dispatching it against a Cookiecutter template), Vale and markdown style (handled by `task lint`), the orchestrating skill or caller that will dispatch this agent, and the substantive cookiecutter best-practice recommendations themselves (those were cross-verified during the authoring phase).
Reviewer context: review was run from the `feat/cookiecutter-agent` worktree at SHA `73829d7`; plan file lives under that worktree's `.audits/agent-review/`.

## Summary

- Critical: 0
- Warning: 1
- Suggestion: 1
- Info: 2

Go/no-go: PASS — agent is structurally spec-conformant; the four open findings are non-blocking polish items.
Next concrete action: author addresses the Warning (cross-platform `/tmp` path) before opening the pull request; Suggestion and Info may be folded into the same PR or deferred to a follow-up.

## Findings

### Warning

- [x] [agent-management.no-absolute-paths] Working procedure step 5 hard-codes `/tmp/<bake-output>` (twice), which is not cross-platform — Cookiecutter templates are commonly authored to support Windows consumers as well, and Windows has no `/tmp`.
      Where: `agents/cookiecutter-template-author.md:79`.
      Fix: Replace `/tmp/<bake-output>` with a portable scratch-directory placeholder, e.g. `<scratch-dir>` plus a one-line note instructing the agent to derive it from `tempfile.mkdtemp()` (Python) or `mktemp -d` (POSIX) / `New-TemporaryFile` (PowerShell). Update both occurrences (bake and cleanup) on the same line.
      Verify: `grep -n '/tmp/' agents/cookiecutter-template-author.md` returns no matches; the surrounding sentence still tells the agent to clean up the scratch directory after inspection.

### Suggestion

- [x] [agent-management.single-responsibility] The `description` field declares four well-bounded modes (`scaffold` / `refactor` / `hook` / `tests`), and `agent-management` §Subagent boundaries SHOULDs single-responsibility design while the acceptance criterion at line 146 of `agent-management/en.md` asks for a "documented reason for the conflation" when the description reads as X+Y+Z. The Rationale section names *Specialization* and the Preconditions list declares an explicit Mode-Declaration handshake, which together *imply* the conflation rationale — but neither states it explicitly as "four modes in one agent rather than four separate agents".
      Where: `agents/cookiecutter-template-author.md:3` (description), `:13–19` (Rationale section).
      Fix: Add one sentence to the Rationale section explicitly justifying the mode split — for example: "These four modes share one agent because they share the same Cookiecutter-domain context (the same `cookiecutter.json` + hooks + tests surface), the same tool set, and have no cross-mode state; splitting them into four agents would duplicate the rationale, the hard rules, and the reference idioms without measurable benefit."
      Verify: `grep -n 'four modes\|one agent' agents/cookiecutter-template-author.md` returns at least one match inside the `## Rationale` section.

### Info

- [x] [agent-management.model-field-absent] No `model` field is declared, so the agent inherits the caller's model per `agent-management` §Model selection (default `inherit`). This is a deliberate MAY-class choice; recording it here so a future audit doesn't read the absence as an oversight.
      Where: `agents/cookiecutter-template-author.md:1–7` (frontmatter).
      Fix: n/a (observation).
      Verify: n/a.
- [x] [agent-management.idiom-hard-rule-tension] The conditional-cleanup reference idiom (`hooks/post_gen_project.py`) compares against the legacy `"y"` / `"n"` strings, while Hard rule #4 explicitly marks that convention as legacy-only for *new* templates. The idiom is correct for the `refactor` mode acting on existing templates, but a reader switching to `scaffold` mode might copy the legacy form by mistake.
      Where: `agents/cookiecutter-template-author.md:88–89` (Hard rule #4) and `:127–135` (Conditional cleanup idiom).
      Fix: Annotate the idiom with a one-line comment such as `# Legacy y/n form retained for backward-compatible refactors; for new templates use `if {{cookiecutter.use_docker}}:` against a JSON boolean.` Optionally include a second snippet showing the native-boolean variant.
      Verify: line 127 carries a `# Legacy form` or equivalent annotation; the cross-reference between Hard rule #4 and the idiom is greppable.

## Processing log

<!-- Append one line per item closure: YYYY-MM-DD — <item-shorthand> — <action taken> — verified: <method> -->
2026-05-18 — warning/no-absolute-paths — replaced `/tmp/<bake-output>` with `<scratch-dir>` placeholder + tempfile/mktemp/New-TemporaryFile guidance + explicit Windows-portability note in Working procedure step 5 — verified: re-read of `agents/cookiecutter-template-author.md:80`, the only remaining `/tmp/` occurrence is the explicit "never hard-code" warning
2026-05-18 — suggestion/single-responsibility — added "Single agent across four modes (not four agents)" bullet under `## Rationale` naming shared cookiecutter-domain surface, shared tool set, shared anti-patterns, and pointing at the precondition handshake for deterministic routing — verified: re-read of `agents/cookiecutter-template-author.md:19`
2026-05-18 — info/model-field-absent — acknowledged as deliberate MAY-class choice; no edit required (Fix: n/a per plan body) — verified: re-confirmed frontmatter at `agents/cookiecutter-template-author.md:1-7` carries no `model:` field, agent inherits caller's model per `agent-management` §Model selection
2026-05-18 — info/idiom-hard-rule-tension — annotated cleanup idiom as "legacy y/n string form (see Hard rule #4)" and added a second snippet showing the native-JSON-boolean variant for new templates, prefaced by a one-paragraph explanation of when each form applies — verified: re-read of `agents/cookiecutter-template-author.md:128-148`
