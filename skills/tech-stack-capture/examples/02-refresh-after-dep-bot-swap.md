# Example 2 — Refresh after a Dependabot → Renovate switch

A refresh path in a Portfolio-Member repository that previously declared `dependabot` as a repo-specific addition (before Renovate joined the global stack). The maintainer just switched to Renovate; the skill should drop the addition and confirm the inherited entry is now active.

## Input

- **User prompt** (English): "Refresh the tech_stack block — we just moved off Dependabot to Renovate."
- **Active repository**: `nolte/example-home-assistant-integration` with an existing `tech_stack:`:

  ```yaml
  tech_stack:
    additions:
      - name: dependabot
        kind: dep-bot
        group: automation
        role: Dependency-update bot for the Home Assistant integration's HACS deps.
        status: active
        lifecycle: development
        source_of_truth: .github/dependabot.yml
  ```

- **Repo signals present after the switch**:
  - `renovate.json5` (newly added)
  - `.github/dependabot.yml` (recently deleted from the working tree)
  - The usual `pyproject.toml` / `Taskfile.yml` / workflows / etc. signals

## Expected skill behavior

1. **Preconditions** — confirms `project/portfolio.yml` parses; fetches the global manifest; confirms feature branch.
2. **Inherited set** — `renovate` is in the active global set (status `active`); `dependabot` is not in the global set.
3. **Read existing block (step 2)** — loads `existing_additions = [dependabot]`, `existing_overrides = []`, `existing_regroup = []`.
4. **Probe** — produces candidates including `renovate` (because `renovate.json5` is present) but **not** `dependabot` (because `.github/dependabot.yml` was deleted).
5. **Drop inherited matches** — `renovate` matches the inherited entry by `name` and `kind`; the candidate is dropped from `additions` into inherited-confirmed.
6. **Interactive confirmation** — the skill presents three items:
   - The inherited `renovate` candidate (now confirmed against signals — operator just acknowledges).
   - The pre-existing `dependabot` addition that has no signal anymore. The skill flags it: "The `dependabot` addition you previously declared no longer has a `.github/dependabot.yml` signal. Drop it, keep it (you'd need the `acknowledged-missing-signal:` marker in `rationale:`), or edit it?"
   - The operator picks **drop**.
7. **Compose** — the resulting `tech_stack:` mapping has empty `additions`, no overrides, no regroups.
8. **Write** — composes `tech_stack: {}`, validates, writes, re-parses.

## Expected `tech_stack:` after refresh

```yaml
tech_stack: {}
```

## Expected confirmation summary

> "`project/portfolio.yml` updated. `additions:` 0 (1 dropped: `dependabot` — no signal), `overrides:` 0, `regroup:` 0, inherited-confirmed: 12 (including the newly inherited `renovate`). The next `portfolio-audit` run will pick up the change."

## What this example exercises

- The refresh path of the Capture operation (step 2 reads the existing block).
- The "previously declared, no signal anymore" gotcha (step 7 surfaces it instead of silently dropping or silently keeping).
- The promotion-by-inheritance pattern: `renovate` quietly joins this repo's effective stack because it landed in the global manifest; no per-repo authoring is needed.
- The "candidates not picked" log emission with the rejection reason "no signal".
