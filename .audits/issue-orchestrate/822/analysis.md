# Issue #822 — pre-analysis

- Issue: https://github.com/nolte/claude-shared/issues/822 (author nolte, trusted: repository owner)
- Classification: bug (secondary: security). Rationale: a pinned docs build dependency carries a known CVE; the fix is a lock regeneration plus the Renovate config gap that let it go unnoticed.
- Worktree: ~/repos/.worktrees/claude-shared/wcmatch-cve-docs-lock, branch fix/wcmatch-cve-docs-lock off origin/develop 9f45023a (`task worktree:add`).
- Requirements gate: no `project/requirements/` artifact. Operator override (2026-11-27): the issue carries two testable acceptance criteria and a single pin change.
- Route: implement directly (one outcome, one PR strand, no roadmap item). Operator-confirmed scope: bump + lockFileMaintenance.

## Asserted causes, verified

- CVE on the pin: established. `pip-audit==2.10.1 --no-deps --disable-pip -r docs/requirements.lock.txt` on develop: `wcmatch 11.0.1 CVE-2026-132276 fix 11.2`.
- wcmatch is transitive: established. `docs/requirements.lock.txt` `# via mkdocs-include-markdown-plugin`; plugin 7.3.0 requires bare `wcmatch`.
- Why no Renovate PR (first reading, REFUTED by P2's specialist): `renovate.json5` has no `lockFileMaintenance` and no `osvVulnerabilityAlerts`. The shared preset `nolte/gh-plumbing//renovate-configs/common.json@v2.3.1` sets neither. The `pip-compile` manager extracts packages from the source manifest, so a transitive pin moves only on lock-file maintenance. Dependabot alerts are disabled (`GET /dependabot/alerts` → 403 "disabled for this repository").

- Why no Renovate PR (measured): the pip-compile manager enables lockFileMaintenance by default (renovate 45.3.2 `dist/modules/manager/pip-compile/index.js` `defaultConfig.lockFileMaintenance.enabled: true`), but it parsed none of the three lock files: `--dry-run=extract` → `WARN: pip-compile error` "Option --python-version must have equal sign '=' separating it's argument" for all three; dashboard #393 line 7 `⚠️ WARN: pip-compile error`. With headers rewritten to `--python-version=3.14 … --output-file=…`: `"pip-compile": {"fileCount": 3, "depCount": 66}`, no warning, branch `renovate/pip-compile-refresh` planned. Operator re-approved P2 as header fix + guard (2026-11-27).

## Work packages

| id | problem | acceptance | files | specialist | deps |
|---|---|---|---|---|---|
| P1 | wcmatch 11.0.1 vulnerable | lock regenerated via its header command, wcmatch ≥ 11.2, pip-audit clean over the cve-scan set, `mkdocs build --strict` green | docs/requirements.lock.txt | no matching specialised agent — generalist remediation (`dependency-audit` triages, it doesn't regenerate locks) | — |
| P2 | transitive lock pins never refresh | all three lock headers parseable by Renovate's pip-compile manager; class guard refuses an unparseable header or an unmatched lock | the three `*.lock.txt` headers, tests/test_lock_file_header_guard.py | nolte-shared:renovate-config-author (diagnosis), nolte-engineering:unit-test-generator (guard) | — |

## Results

- P1: `uv pip compile --python-version 3.14 docs/requirements.txt -o docs/requirements.lock.txt --upgrade-package wcmatch` → wcmatch 12.0.4, bracex 3.0.1 → 3.2.4 (wcmatch 12.0.4 requires `bracex>=3.2.3`). pip-audit over all 8 cve-scan manifests: "No known vulnerabilities found". `mkdocs build --strict` exit 0; `diff -rq` of the site built with the old and new lock: identical.

- P2: headers regenerated with `uv pip compile --python-version=3.14 <src> --output-file=<lock>`; the two other locks change only their header line. Guard `tests/test_lock_file_header_guard.py`: 21 passed on the worktree; against an origin/develop copy the main test fails with 12 messages (4 per lock file). renovate.json5 unchanged.
- license-drift equivalent (SBOM + scripts/check_licenses.py): 13 identifiers, all covered.

## Findings

| source | head | finding | triage |
|---|---|---|---|
| general-purpose review r1 | 38565617 | S1 rule 7 not fail-closed (commented-out block, enabled:false, enabledManagers, string-only pass; comments/double quotes false-fail) | fixed in branch: comment-aware JSON5-subset reader, refusals listed; packageRules/extends-sourced disables under Not covered |
| general-purpose review r1 | 38565617 | S2 four predicate branches unkilled by mutation | fixed in branch: one test per branch, 11 mutations each red |
| general-purpose review r1 | 38565617 | nits: partition vs split on `=`, 5-space message, zero --output-file stricter than Renovate | over-indent message fixed; the two stricter-than-Renovate cases kept deliberately |
| general-purpose review r2 | 30eec0cd | S: five reader error branches unkilled by mutation | fixed in branch: one test each plus escape/continuation tests, each mutation red (47 passed) |
| general-purpose review r2 | 30eec0cd | nits: empty enabledManagers false-fail, quoted `enabled` inconsistent, ignorePaths docstring | fixed in branch |
