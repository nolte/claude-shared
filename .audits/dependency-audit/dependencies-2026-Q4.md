# Dependency audit — 2026-Q4

- **Date:** 2026-09-13
- **Repository:** `nolte/claude-shared`, `develop` @ `356d6a558456301bc7d8091a34282a7c2a426a4d`
- **Release anchor:** `v0.1.11` @ `c00bcb1fa664`, the latest published release, audited from the manifests as tagged
- **Governing spec:** `spec/project/dependency-audit/` (quarterly full-audit MUST); remediation of spec-drift-audit 2026-Q4 findings F60 (commit SHA) and F61 (release-anchored baseline), #587
- **Tool:** `pip-audit 2.10.1` (PyPI advisory database) through `uvx`, the same invocation as `task deps:audit`

## Scope

All five Python dependency manifests, at both revisions:

| Manifest | Purpose |
| --- | --- |
| `requirements.txt` | runtime placeholder set |
| `requirements-dev.txt` | dev and tooling (`jsonschema`, `PyYAML`, `pytest`, `pre-commit`) |
| `docs/requirements.txt` | MkDocs toolchain |
| `evals/requirements-dev.txt` | deterministic eval-harness tests |
| `evals/requirements-eval.txt` | behavioural-eval extras |

No lockfiles exist; pinning happens in the manifests. GitHub Actions pins are Renovate-managed and outside this CVE surface.

## Result

| Revision | Resolved packages | Known vulnerabilities |
| --- | --- | --- |
| `v0.1.11` (`c00bcb1`) | 42 | 0 |
| `develop` (`356d6a5`) | 50 | 0 |

```
$ uvx pip-audit -r requirements.txt -r requirements-dev.txt -r docs/requirements.txt \
    -r evals/requirements-dev.txt -r evals/requirements-eval.txt --format json
```

No findings, so no `fix / mitigate / accept` responses are required. The `v0.1.11` row is the supply-chain baseline for the shipped release: a later advisory against a package in that set can be triaged against this record.

## Cadence and follow-ups

- Next full audit due 2026-Q1, and before any release tag that carries a dependency change; the next release tag should get its own anchored row.
- The quarterly reminder in `.github/workflows/audit-cadence-reminder.yml` and the per-change `pip-audit` gate in `.github/workflows/audit-gates.yml` stay the recurring triggers.
