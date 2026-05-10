# Example 03: Monorepo with multiple ecosystems

## Input prompt

"Wir cutten heute Abend ein Release über alle Pakete — bitte einmal das Dependency-Gate fahren, Severity-Floor `medium`."

## Input files (optional)

- `backend/pyproject.toml` + `backend/uv.lock` — Python service managed with `uv`
- `frontend/package.json` + `frontend/pnpm-lock.yaml` — Node app managed with pnpm
- `tools/cli/go.mod` + `tools/cli/go.sum` — Go CLI shipped alongside the services
- `Taskfile.yml` — declares a `deps:audit` target that fans out to per-subroot audit subtasks

## Expected behaviour

1. Walk the documented subroot pattern (repo root + `backend/`, `frontend/`, `packages/*`, `apps/*`, plus `tools/*` because manifests live there too) and record three subroots with their kinds: `backend/` → **Python (uv)** via `pip-audit`, `frontend/` → **Node (pnpm)** via `pnpm audit`, `tools/cli/` → **Go** via `govulncheck`; honour the caller's `medium` severity floor and leave the license-audit toggle off (not requested).
2. Probe `Taskfile.yml`, find the wrapping `deps:audit` target, and **prefer the Taskfile invocation over calling auditors directly** per the hard rule — invoke `task deps:audit` once so any project-specific ignore-list the Taskfile applies stays in effect, and record `Taskfile targets used: deps:audit` in the `Health` section. If `task deps:audit` does not emit per-subroot machine-readable output, fall back to running each auditor individually but still attribute the run to the Taskfile target in the report.
3. For each subroot, run the kind-appropriate auditor (`uv export ... | pip-audit -r -` for `backend/`, `pnpm audit --json` for `frontend/`, `govulncheck -json ./...` for `tools/cli/`); if `govulncheck` is missing on the host, emit the install hint `go install golang.org/x/vuln/cmd/govulncheck@latest` and record the skip in `Health` rather than silently dropping the Go subroot — partial coverage is never reported as full coverage.
4. Normalise every finding from all three auditors into the single internal shape (`package`, `installed_version`, `advisory_id`, `severity`, direct-vs-transitive `path`, `fixed_in`, `summary_url`), drop everything below the `medium` floor before rendering, attribute every remaining finding to its originating subroot (so the frontend team and the backend team can act on their own queue), and sort severity-then-name across the whole report rather than per-subroot so the diff stays stable across runs.
5. Render the unified report (English section headings, German prose around it per the user-language policy) with `Auditors run: pip-audit, pnpm audit, govulncheck` and a per-subroot manifest list under `Health`; offer follow-ups per finding without executing them (per-ecosystem upgrade hints — `uv lock --upgrade-package`, `pnpm up`, `go get -u`) and explicitly flag in the closing summary that this run is the **release gate** so the caller can decide whether the remaining `medium`+ findings block the cut.
