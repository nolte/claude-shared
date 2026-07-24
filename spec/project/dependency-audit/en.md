# Dependency Audit

Status: draft

## Context
Every repository in the portfolio pulls in third-party packages through one or more dependency manifests (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, and their lockfiles). Each of those packages is a supply-chain attack surface: known vulnerabilities (CVEs / GHSAs / PYSECs) are disclosed continuously, transitive dependencies multiply that surface, and licenses sometimes carry obligations (copyleft, attribution) that the project's own license can't absorb. Without a binding audit practice, vulnerability findings accumulate silently—auditors are run ad hoc, Renovate PRs carry no security context, and the portfolio can't answer "what's our current CVE exposure?" in a reproducible way. This spec defines when dependency audits run, what they cover, how results are classified, and how findings turn into action. It complements `spec/project/workflow-health/` (continuous CI health) and `spec/project/spec-drift-audit/` (periodic deep audit) by owning the specific slice of supply-chain risk.

## Goals
- Every repository with a dependency manifest runs a vulnerability audit at documented trigger points, not by chance
- Findings are classified by a shared severity scale so the same CVE is treated the same way across the portfolio
- Critical and high findings receive a documented response inside a bounded window—never "known, maybe later"
- Audit invocation honours repository conventions (Taskfile targets, ignore lists) so the practice scales to projects with a justified local policy
- License compliance, when enabled, runs on the same cadence and reports through the same artifact so risk is aggregated in one place

## Non-Goals
- Choosing a specific vulnerability auditor (`pip-audit`, `npm audit`, `govulncheck`, `cargo audit`): the audit is tool-agnostic and the repository picks whichever fits its ecosystem
- Declaring an upgrade policy (minor vs major, automated vs reviewed): the decision stays with dependency owners and Renovate / Dependabot configuration
- Replacing continuous CI checks that already scan dependencies on every push—those remain; this spec defines the periodic deep pass and the pre-release gate
- Defining the skill's operational details (Taskfile target detection, output shape)—those belong to `skills/dependency-audit/` and can evolve without a spec change

## Requirements

### Scope
- **MUST** treat as "dependencies" every package declared in a manifest the repository tracks: for Python the `pyproject.toml` / `requirements*.txt` / `poetry.lock` / `uv.lock` / `Pipfile.lock`, for Node the `package.json` + matching lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`), for Go `go.mod`, for Rust `Cargo.toml` + `Cargo.lock`
- **MUST** include every subroot in a monorepo that carries its own manifest (for example `backend/`, `frontend/`, `packages/*`); audits run per subroot so findings can be attributed to the owning team / package
- **MUST** cover transitive dependencies, not just direct ones—a finding in a transitive package is still a finding; the report distinguishes the two so triage can start at the right layer
- **MAY** additionally run a license audit when the repository enables it, using an allowlist located at `.license-allowlist.txt`, under `tool.*` in the manifest, or equivalent; absence of an allowlist means license findings are reported as `review`, not as failure. License auditing counts as "enabled" whenever an allowlist is discoverable per §License audit: the quarterly and full audits then **MUST** run the license pass automatically, while ad-hoc invocations stay opt-in

### Triggers and cadence
- **MUST** run a full audit at least once per calendar quarter in every repository with a dependency manifest; the calendar follows calendar quarters, not individual availability
- **MUST** additionally run before every release tag or production deployment that carries a dependency change since the previous audit
- **SHOULD** run as a pre-PR gate (optional local invocation) whenever the PR modifies a dependency manifest or a lockfile
- **MAY** run on a shorter cadence (monthly, weekly) when the repository's risk profile warrants it—security-sensitive services, public-facing products

### Severity classification
- **MUST** adopt the following severity scale, using the auditor's native classification as the source of truth:
  - **critical**: a CVE with CVSS ≥ 9.0, or the auditor's native `critical` tag; response window: within 7 days
  - **high**: CVSS 7.0–8.9, or the auditor's `high` tag; response window: within 30 days
  - **medium**: CVSS 4.0–6.9, or the auditor's `moderate` / `medium` tag; response window: within the current calendar quarter
  - **low**: CVSS < 4.0, or the auditor's `low` tag; response window: best effort, revisited at the next quarterly audit
  - **unknown**: the auditor couldn't classify the finding; treat as `high` until classified otherwise
- **MUST NOT** downgrade a severity on local judgement alone; disagreement with the auditor's classification is an ignore-list entry with an explicit rationale (see §Ignore discipline)

### Response to findings
- **MUST** apply one of three responses to every finding inside the severity's response window:
  - **upgrade**: bump the affected package to a version that crosses the `fixed_in` boundary
  - **ignore with rationale**: add the advisory ID to the auditor's ignore list with a mandatory `valid-until` date and a one-line rationale; acceptable only when no fix is published yet, the finding genuinely doesn't apply, or the upgrade would break a contract the project can't break inside the window
  - **accept as known**: record the finding in the audit artifact with a business-level acceptance statement; acceptable only for `low` findings or explicitly signed-off `medium` findings
- **MUST** revisit every `ignore with rationale` entry at the latest on its `valid-until` date; the entry **MUST NOT** be renewed without a fresh rationale
- **MUST NOT** mark a `critical` or `high` finding as `accept as known`; those response options are reserved for `medium` / `low` tiers

### Execution mechanics
- **MUST** prefer repository-declared Taskfile targets (`task audit`, `task deps:audit`, `task security:audit`) when they exist and wrap the same auditor the spec would invoke directly—this picks up project-specific ignore lists that the Taskfile already applies
- **MUST** fall back to the ecosystem's native auditor when no Taskfile target exists; the fallback is per subroot, not per repository
- **MUST** record in the audit artifact which tool was invoked (Taskfile target or direct auditor) and its version, so the audit is reproducible
- **MUST NOT** silently skip a subroot whose auditor isn't installed; the audit reports the skip and the install hint, and the gate treats a skipped subroot as `blocked`, not `pass`

### Ignore discipline
- **MUST** store the ignore list in a location the auditor reads natively, for example `pyproject.toml` under `[tool.pip-audit]`, `.npm-audit-ignore.json`, or an equivalent, not as free-form prose that only the audit artifact sees
- **MUST** declare for every ignore entry: advisory ID, affected package, `valid-until` date (ISO 8601), and a one-line rationale; entries without these fields **MUST** fail the audit
- **SHOULD** keep the total number of active ignore entries small (guideline: fewer than ten per subroot); a growing ignore list signals that the dependency strategy itself needs revision—this is a guideline, not an enforced cap; a count above it triggers a dependency-strategy review rather than a gate failure
- **MUST NOT** silence a finding globally (`--ignore-vuln <id>` without a date) just to make the gate green; that pattern defeats the spec's purpose

### Audit artifact
- **MUST** persist the result of every full audit as a commit, issue, or file in the repository; the artifact location stays a per-repository choice rather than a portfolio-wide hard-coded path (mirroring the per-repository freedom `spec/project/spec-drift-audit/` deliberately preserves)
- **SHOULD** default to the canonical path `.audits/dependency-audit/dependencies-YYYY-Q<n>.md` (the portfolio-wide `.audits/<audit-type>/` standard, per `spec/project/spec-drift-audit/`); a GitHub issue labelled `security-audit` is an accepted alternative, and any cross-repo aggregation tooling built later keys off either form
- **MUST** include in the artifact: date, trigger (quarterly, pre-release, manifest-change), scope (which subroots were audited, which were skipped and why), the tools used and their versions, the per-finding severity and response decision, and the Git revision audited
- **SHOULD** link to the prior audit artifact so the progression is traceable across quarters

### License audit (when enabled)
- **MUST** apply the classification and the allow/review/deny policy defined in `spec/project/license-check/`; this pass implements that spec's policy for the dependency slice rather than defining its own, and the portfolio-default policy there counts as the "explicit policy with named disallowed licenses" required below
- **MUST** treat license auditing as "enabled" whenever an allowlist is discoverable (at `.license-allowlist.txt`, under `tool.*` in the manifest, or equivalent); in that case the quarterly and full audits run the license pass automatically and only ad-hoc invocations may opt out
- **MUST** document the allowlist location in the repository's README or equivalent so the rule set is discoverable
- **MUST** classify every package whose license isn't on the allowlist as `review`, not as failure, when no explicit policy exists; a hard failure requires an explicit policy with named disallowed licenses
- **SHOULD** pair a license finding with the response options from §Response to findings, adapted: `replace` (swap to a compatibly-licensed alternative), `add to allowlist` (with rationale and approval), or `accept as known` where that's defensible

### Delimitation
- **MUST** keep dependency audits distinct from `spec/project/workflow-health/`: workflow-health is continuous and broad (CI green, flake triage), dependency audit is targeted and periodic (CVEs + licenses)
- **MUST** integrate with `spec/project/spec-drift-audit/`: the quarterly deep audit references the most recent dependency audit artifact rather than duplicating its work
- **MUST NOT** couple dependency audit triggers to individual PR review cadences; the PR pre-gate is optional, the quarterly audit isn't

## Acceptance Criteria
- [ ] Every repository with a dependency manifest contains a traceable dependency-audit history (commit, issue, or audit file) with at least one entry per calendar quarter since this spec was introduced, or a documented exception naming which quarter was skipped and why
- [ ] The most recent dependency-audit artifact names the tools invoked, their versions, the subroots scoped in and out, and the Git revision audited
- [ ] No `critical` finding from the most recent audit sits beyond its 7-day response window without a documented upgrade, ignore entry, or (only if applicable by the severity rules) accept-as-known decision
- [ ] Every ignore-list entry in the repository carries an advisory ID, affected package, `valid-until` ISO 8601 date, and a one-line rationale
- [ ] The Taskfile (or equivalent task runner) exposes a target that reproduces the audit the skill runs, so contributors can reproduce findings locally
- [ ] When license auditing is enabled, the allowlist is documented in the README or a linked file, and every license finding has a response decision in the audit artifact
- [ ] The audit artifact for any release tag references the dependency-audit state at the release revision, so post-release supply-chain triage can start from a known baseline

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. The per-item decisions and rationale are preserved in git history (decision log, 2026-06-06)._
