# Example 03 — Refusal when planning pair already exists

The skill is invoked on a project that has already been bootstrapped. Either `project/goals.md` or `project/roadmap.md` (or both) already exists. The skill must refuse and route the user to the correct sibling skill instead of overwriting.

## Input prompt

> Bootstrap bitte die Roadmap — leg `project/goals.md` und `project/roadmap.md` an.

## Input files

Three sub-scenarios, each of which must trigger the refusal independently:

### Sub-scenario 3a — both files present

- `project/goals.md` exists with a populated Vision and three outcomes (`O-1`, `O-2`, `O-3`).
- `project/roadmap.md` exists with a queue of two items (`R-1`, `R-2`) at `coarse` detail.
- `AUDIENCES.md` exists at the repo root.

### Sub-scenario 3b — only `project/goals.md` present

- `project/goals.md` exists with a Vision and one outcome (`O-1`).
- `project/roadmap.md` does **not** exist.
- `AUDIENCES.md` exists at the repo root.

### Sub-scenario 3c — only `project/roadmap.md` present

- `project/goals.md` does **not** exist.
- `project/roadmap.md` exists with a top-of-file paragraph and zero items.
- `AUDIENCES.md` exists at the repo root.

## Expected behaviour

1. **Language detection** — the skill responds in German throughout (matches the user's prompt language).
2. **Precondition check fails** — the skill detects that at least one of `project/goals.md` or `project/roadmap.md` already exists. The hard rule "Never overwrite an existing `project/goals.md` or `project/roadmap.md`" is binding.
3. **Refusal** — the skill stops immediately. It does **not**:
   - draft a replacement `goals.md` or `roadmap.md`,
   - read or modify either existing file,
   - dispatch `audience-identify` (the audience-resolution step never runs because the precondition gate failed first),
   - offer a "merge" or "append" mode (none exists in this skill's contract).
4. **Routing message** — the refusal message names the offending path(s) and routes the user explicitly:
   - **For sub-scenario 3a (both present)** — "`project/goals.md` und `project/roadmap.md` existieren bereits. Für neue Roadmap-Einträge oder Sprint-Retargeting nutze `roadmap-planner`. Für die Detail-Level-Invariante nutze `roadmap-refine`."
   - **For sub-scenario 3b (only `goals.md`)** — names the existing `project/goals.md` path, refuses, and routes the user to `roadmap-planner` (which is also the right entry point to author the missing `project/roadmap.md` against the existing goals).
   - **For sub-scenario 3c (only `roadmap.md`)** — names the existing `project/roadmap.md` path, refuses, and routes the user to `roadmap-planner` for adding items (with a note that authoring `project/goals.md` retroactively is outside this skill's scope and should be raised with the operator).
5. **No partial action** — no file is created, modified, or deleted. The git working tree is unchanged after the refusal.
6. **No silent override** — the skill never offers a `--force` flag or interactive confirmation to bypass the refusal. The hard rule has no exception path inside this skill; if the user genuinely wants to re-bootstrap, they delete the offending file(s) themselves and re-invoke the skill.
