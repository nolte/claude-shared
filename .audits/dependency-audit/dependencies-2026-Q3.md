# Dependency audit — 2026-Q3

- **Date:** 2026-07-25
- **Repository:** `nolte/claude-shared` (branch `chore/496-audit-cadences`, off `origin/develop`)
- **Governing spec:** `spec/project/dependency-audit/` (quarterly full-audit MUST; first recorded run — the spec has been in force since 2026-04-24 with no prior audit history, the gap tracked as `dependency-audit.no-quarterly-audit-history` in #496)
- **Tool:** `pip-audit 2.10.1` (PyPI advisory database), invoked directly in a clean venv; local reproduction: `task deps:audit` (same manifest set via `uvx pip-audit`)

## Scope

All five Python dependency manifests in the repository:

| Manifest | Purpose |
| --- | --- |
| `requirements.txt` | runtime placeholder set |
| `requirements-dev.txt` | dev/tooling (`jsonschema`, `PyYAML`, `pytest`) |
| `docs/requirements.txt` | MkDocs toolchain |
| `evals/requirements-dev.txt` | deterministic eval-harness tests |
| `evals/requirements-eval.txt` | behavioural-eval extras |

No lockfiles exist (pinning happens in the manifests); no non-Python manifests are in scope (GitHub Actions pins are Renovate-managed and out of this audit's CVE surface).

## Result

**0 known vulnerabilities.** `pip-audit` resolved every manifest and matched no advisory:

```
$ pip-audit -r requirements.txt -r requirements-dev.txt -r docs/requirements.txt \
    -r evals/requirements-dev.txt -r evals/requirements-eval.txt
No known vulnerabilities found
```

No findings ⇒ no `fix / mitigate / accept` responses required this quarter.

## Cadence and follow-ups

- Next full audit due **2026-Q4** (quarterly MUST), and additionally before any release tag that carries a dependency change.
- The recurring trigger is now wired: `.github/workflows/audit-cadence-reminder.yml` opens a quarterly reminder issue, and `.github/workflows/audit-gates.yml` runs `pip-audit` on every PR touching a dependency manifest (the continuous slice).
- Persisting path: `.audits/dependency-audit/dependencies-YYYY-Q<n>.md` (this file establishes the convention for this repository).
