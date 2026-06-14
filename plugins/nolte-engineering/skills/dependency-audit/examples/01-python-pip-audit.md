# Example 01: Python project with pyproject.toml + uv.lock

## Input prompt

"Auditiere die Abhängigkeiten dieses Projekts und sag mir, ob ich vor dem Release einen offenen CVE habe."

## Input files (optional)

- `pyproject.toml` — declares the runtime + dev dependency groups via PEP 621 (`[project]` and `[dependency-groups]`)
- `uv.lock` — `uv`-managed lockfile pinning the full transitive graph with hashes
- `Taskfile.yml` — repository task runner; no `audit` / `deps:audit` / `security:audit` target declared

## Expected behaviour

1. Detect project kind by finding `pyproject.toml` + `uv.lock` at the repo root, classify as **Python (uv)**, and record one Python subroot (`.`); confirm no Node / Go / Rust manifests exist alongside, default the severity floor to `low`, and leave the license-audit toggle off because the user did not opt in.
2. Probe `Taskfile.yml` with `task --list-all 2>/dev/null | grep -E '^\* (audit|deps:audit|security:audit)'`, find no matching target, and fall back to a direct auditor invocation; record `Taskfile targets used: none` for the `Health` section.
3. Materialise a hash-pinned requirements file from the lockfile via `uv export --format requirements-txt --no-hashes --no-emit-project -o /tmp/uv-export-<sha>.txt` (do **not** audit `uv.lock` directly, `pip-audit` consumes a `requirements`-shaped input), then run `pip-audit --format=json --progress-spinner=off -r /tmp/uv-export-<sha>.txt`; if `pip-audit` is missing, emit the install hint `uv tool install pip-audit` and record the skip in `Health` instead of silently dropping the run.
4. Parse the JSON, normalise every advisory into the per-finding shape (`package`, `installed_version`, `advisory_id` for GHSA / CVE / PYSEC, `severity`, direct-vs-transitive `path` resolved against the `pyproject.toml` direct-dependency set, `fixed_in`, `summary_url`), sort first by severity (`critical → high → medium → low`) then alphabetically by package name, and render the report with the canonical English section headings while keeping the surrounding prose in German per the user-language policy.
5. Offer follow-ups without executing them: for every finding with a `fixed_in` version, propose the smallest version bump that crosses the fix boundary (annotated as a `pyproject.toml` constraint change plus a `uv lock --upgrade-package <name>` invocation the user would run); for findings without a fix, offer to wire `pip-audit --ignore-vuln <id>` into a future Taskfile `audit` target with a `valid-until` date — and explicitly **do not** mutate `pyproject.toml`, `uv.lock`, or any ignore list in this run.
