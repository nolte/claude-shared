---
name: dependency-audit
description: Scans the current project's dependency tree for known vulnerabilities (CVEs) and, when requested, license-compliance issues. Dispatches dependency-audit-scanner agent for the read-only scan step. Detects project kind from `pyproject.toml` / `requirements*.txt` / `poetry.lock` / `uv.lock` for Python and `package.json` / `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` for Node, runs the appropriate auditors, and produces a severity-sorted report with direct vs transitive attribution. Invoke when the user asks to "audit dependencies," "run a CVE scan," "check for vulnerable packages," "check the license allowlist," "run pip-audit," "run npm audit," or equivalent German-language requests. Also handles a pre-PR / pre-release dependency gate. Don't use for upgrading dependencies (an author's decision), for writing Renovate configs (`project-structure-apply`), or for the full license inventory / SPDX compliance process (`license-check`). Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [dependency]
phase: quality
summary: "Scans the project's dependency tree for known CVEs and (optionally) license-compliance issues; severity-sorted report."
summary_de: "Scannt den Dependency-Baum des Projekts nach bekannten CVEs und optional Lizenz-Compliance-Issues; Severity-sortierter Report."
use_when:
  - "you want to run a CVE scan on the current project"
  - "you want a pre-PR or pre-release dependency-vulnerability gate"
  - "you want to check license compliance across direct and transitive dependencies"
dont_use_when:
  - situation: "You want the full license inventory / SPDX compliance process, not the allowlist quick check"
    alternative: license-check
  - situation: "You want to write or update Renovate config"
    alternative: project-structure-apply
see_also:
  - dependency-audit-scanner
resumable: true
---

# Dependency Audit

Run a CVE and optional license audit against every dependency manifest the current project ships, and produce a single severity-sorted report. This skill reports and recommends; it never upgrades, pins, or removes dependencies on its own.

Implements `spec/project/dependency-audit/` — the spec defines the audit scope, severity mapping, and per-language tooling. This skill binds those rules to the on-disk procedure.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Abhängigkeiten auditieren"
- "CVE-Scan durchführen"
- "Lizenz-Compliance prüfen"

## User-language policy

Detect the user's language from their message and respond in it. The report itself uses English section headings (so downstream tooling can parse it reliably); prose around the report is localised.

## Inputs

- **Repo root**: default is the current working directory.
- **License audit toggle**: defaults to **on** whenever a license allowlist is discoverable in the repo (at `.license-allowlist.txt`, `.licenses/allowed.txt`, under `tool.*` in the manifest, or equivalent) — per `spec/project/dependency-audit/`, a discoverable allowlist means license auditing is "enabled" and the pass runs automatically. When no allowlist is discoverable, the toggle is off by default and the caller opts in explicitly ("also check licenses," "include license compliance"). The caller may always opt out of an automatic license pass for an ad-hoc invocation.
- **Severity floor**: defaults to `low` (report every finding). Caller may narrow to `medium` or `high` to de-noise pre-release gates.

## Operations

### 0. Dispatch the read-only scan agent

Dispatch `dependency-audit-scanner` (Agent) for the read-only audit pass: it detects project type, runs the matching auditor (pip-audit / npm audit / etc.), and returns a structured drift report. Wait for its inventory before proceeding to severity-triage and follow-up actions. This scan dispatch is scope-only detection, which `spec/claude/dispatch-brief/` exempts from the refutation clause; when a later step dispatches a specialist to remediate a finding with a proposed fix (a hypothesis), that brief **MUST** authorise refutation per the same spec.

### 1. Detect project kind

Look in the repo root and obvious subroots (`backend/`, `frontend/`, `packages/*`, `apps/*`):

| Indicator | Kind | Auditor |
|---|---|---|
| `pyproject.toml`, `requirements*.txt`, `poetry.lock`, `uv.lock`, `Pipfile.lock` | Python | `pip-audit` |
| `package.json`, `package-lock.json` | Node (npm) | `npm audit --json` |
| `pnpm-lock.yaml` | Node (pnpm) | `pnpm audit --json` |
| `yarn.lock` | Node (yarn) | `yarn npm audit --json` or `yarn audit --json` depending on version |
| `go.mod` | Go | `govulncheck ./...` (if available; otherwise report "no Go auditor installed") |
| `Cargo.toml` | Rust | `cargo audit` (if available) |

If the project has no detectable manifest, stop and report clearly. Don't guess.

Record every subroot where a manifest was found; audits run per subroot so the report can attribute findings.

### 2. Prefer Taskfile targets when they exist

If the repo has a `Taskfile.yml` (or `Taskfile.yaml`) at the root, check for existing audit-named targets before invoking auditors directly:

```
task --list-all 2>/dev/null | grep -E '^\* (audit|deps:audit|security:audit)'
```

When a target exists and it wraps the same auditor you'd otherwise run, invoke it via `task <target>` instead. Record in the report that the target was used. This keeps the skill consistent with the project's conventions and picks up any project-specific ignore-list the Taskfile applies.

If no matching target exists, call the auditor directly.

### 3. Run auditors

Run every detected auditor per subroot. Use `--json` / equivalent machine-readable output where available; fall back to text when necessary.

- **Python (`pip-audit`)**: `pip-audit --format=json --progress-spinner=off [--require-hashes] [-r <file> | -e .]`. When the project uses `uv`, prefer `uv pip compile`-generated requirements as the input. Skip `pip-audit` when the binary is missing and instead emit an install hint (`pip install pip-audit` or `uv tool install pip-audit`); don't silently skip.
- **Node (`npm audit`)**: `npm audit --json` from the subroot that owns the lockfile. Strip out the `auditReportVersion` metadata before parsing.
- **Node (`pnpm audit`)**: `pnpm audit --json` — JSON shape differs from npm; normalise to the same internal structure.
- **Node (`yarn audit`)**: v1: `yarn audit --json` (newline-delimited JSON); v2+: `yarn npm audit --json`.

Record per finding: `package`, `installed_version`, `advisory_id` (GHSA/CVE/PYSEC), `severity` (`critical` / `high` / `medium` / `low` / `unknown`), `path` (direct or transitive), `fixed_in`, `summary_url`.

**Severity classification (CVSS scale).** Per `spec/project/dependency-audit/` §Severity classification, take the auditor's native classification as the source of truth and map it onto the shared scale by CVSS threshold:

| Severity | CVSS | Auditor tag | Response window |
|---|---|---|---|
| `critical` | ≥ 9.0 | `critical` | within 7 days |
| `high` | 7.0–8.9 | `high` | within 30 days |
| `medium` | 4.0–6.9 | `moderate` / `medium` | within the current calendar quarter |
| `low` | < 4.0 | `low` | best effort, revisited next quarterly audit |
| `unknown` | unclassified | — | treat as `high` until classified otherwise |

When the auditor couldn't classify a finding, record it as `unknown` and **treat it as `high`** for triage and response-window purposes — never as a lower tier. Never downgrade a severity on local judgement alone (disagreement is a dated ignore entry with a rationale, not a reclassification).

**Gate outcome: `blocked`, not `pass`.** When a subroot can't be audited because its auditor isn't installed (or a lockfile is missing), the audit MUST report that subroot's verdict as `blocked` with the install/remediation hint — never `pass`. A `blocked` subroot is not a clean result: the gate fails closed. Only a subroot the auditor actually scanned can return `pass`.

### 4. Run a license audit (auto-on when an allowlist is discoverable)

First check for a license allowlist. Locations to check, in order:

1. `.license-allowlist.txt` or `.licenses/allowed.txt` at the repo root.
2. A `licenses:` array under `tool.pip-audit` or an equivalent config block in `pyproject.toml`.
3. The project's README if it explicitly lists accepted licenses (uncommon).

Per `spec/project/dependency-audit/`, license auditing counts as "enabled" whenever an allowlist is discoverable. When one is found, **run the license pass automatically** (the caller may still opt out for an ad-hoc invocation). When no allowlist is discoverable, run the license pass only when the caller explicitly asked for it.

When the license pass runs:

- **Python**: `pip-licenses --format=json --with-urls --with-license-file=false` (install hint: `pip install pip-licenses`).
- **Node**: `npx --yes license-checker --json --production` (or `pnpm licenses list --long --json` for pnpm).

Compare the discovered licenses against the allowlist. If no allowlist exists (and the caller opted in anyway), flag every non-permissive license (GPL / AGPL / LGPL / SSPL / unknown) as `review`, not as failure. Don't invent a policy.

### 5. Render the report

```
# Dependency Audit

Scope: <repo root>, <n> manifests across <m> subroots (skipped: <list with reasons>)
Trigger: <quarterly | pre-release | manifest-change>
Severity floor: <level>
License audit: <on|off>
Auditors run (with versions): <list>
Git revision: <sha>

## Findings (sorted: critical → high → medium → low)

### <severity> — <count>
- **<package>@<installed_version>** (subroot: <path>, path: direct|transitive via <parent>)
  - Advisory: <GHSA / CVE / PYSEC id> — <short summary>
  - Fixed in: <version range or "no fix yet">
  - Reference: <url>
  - Response: <fix | ignore with rationale (valid-until <date>) | accept as known>

(repeat per finding)

## License review
<only when license audit was requested>
- **<package>@<version>**: <license> — <review reason>

## Health
- Total findings: <n> (critical: <x>, high: <y>, medium: <z>, low: <w>)
- Python manifests audited: <list>
- Node manifests audited: <list>
- Auditors skipped (with reason): <list>
- Taskfile targets used: <list or "none">
```

Sort findings by severity first, then package name alphabetically, so diffs of the rendered report stay stable across runs.

### 6. Triage and respond

Per `spec/project/dependency-audit/` §Response to findings, every finding gets exactly one of three responses inside its severity's response window. Never silently downgrade a severity — disagreement with the auditor's classification is an ignore entry with an explicit rationale, not a reclassification.

- **`fix`**: bump to the smallest version that crosses the `fixed_in` boundary. For a `critical` or `high` finding this is the only response, unless an accepted, dated ignore entry exists.
- **`ignore with rationale`**: record the advisory in the auditor's **native ignore location** (for example `pyproject.toml` under `[tool.pip-audit]`, or `.npm-audit-ignore.json`) — never as free-form prose only the report sees. Every entry MUST carry the advisory ID, the affected package, a `valid-until` ISO-8601 date, and a one-line rationale; an entry missing any of these fails the audit. Revisit each entry at the latest on its `valid-until` date and never renew it without a fresh rationale. Never silence a finding globally (`--ignore-vuln <id>` with no date) just to green the gate.
- **`accept as known`**: permitted only for the `medium` / `low` tiers. A `critical` or `high` finding **MUST NOT** be marked `accept as known`.

Don't execute a bump, write an ignore entry, or draft a `.license-allowlist.txt` without explicit confirmation. Keep the active ignore list small (guideline: fewer than ten per subroot); a growing list signals the dependency strategy itself needs review rather than another one-off ignore.

### 7. Persist the audit artifact

Per `spec/project/dependency-audit/` §Audit artifact, persist every full audit as a git-tracked artifact (a commit or a `security-audit`-labelled issue are accepted alternatives). Default to the canonical path `.audits/dependency-audit/dependencies-YYYY-Q<n>.md` (the portfolio-wide `.audits/<audit-type>/` standard). The artifact MUST record: date; trigger (quarterly / pre-release / manifest-change); scope (which subroots were audited, which were skipped and why); the tools used and their versions; the per-finding severity and response decision; and the Git revision audited. Link to the prior quarter's artifact so the progression stays traceable. The quarterly `spec-drift-audit` references this artifact rather than re-running the scan.

## Gotchas

- **`pip-audit` and `npm audit` exit codes don't agree on what counts as a finding.** `pip-audit` exits non-zero on any vulnerability; `npm audit` exits non-zero only when the vulnerability is at or above its `--audit-level` threshold (default `low`). When the skill aggregates per-ecosystem results, treat exit-code parsing as a fallback signal; the JSON output is the source of truth.
- **`pnpm audit` and `yarn audit` use different JSON shapes than `npm audit`.** A naïve "parse `npm audit --json`" pipeline misses both. Detect the package manager from the lockfile (`pnpm-lock.yaml` / `yarn.lock` / `package-lock.json`) before choosing the audit invocation; don't fall back silently to `npm audit` against a `pnpm`-managed project, because the result will be a clean report based on a missing `node_modules/` instead of a real audit.
- **`uv.lock` audits don't have a first-class CLI yet.** When the project uses `uv`, run `pip-audit -r requirements.txt` after exporting (`uv export --no-hashes`); auditing `uv.lock` directly produces no output. Document the export step in the report so the operator knows the audit was a derivative pass.
- **License-compliance scanners pull from external metadata** (PyPI / npm registry); a transient registry outage produces a false "no findings" report rather than a clear error. Re-run on transient HTTP 5xx; only report `clean` when the run reached the registry successfully.
- **Direct vs transitive attribution requires the lockfile.** Without the lockfile, the audit can only flag the surface that the manifest declares; transitive vulnerabilities don't surface. The skill stops and reports when no lockfile is present rather than producing a misleading direct-only report.

## Examples

- Read `examples/01-python-pip-audit.md` when running the first audit on a Python project.
- Read `examples/02-node-pnpm-audit.md` when auditing a Node.js project managed with pnpm.
- Read `examples/03-multi-ecosystem-monorepo.md` when the repository contains multiple language ecosystems.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/dependency-audit/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Source triangulation

Per `spec/claude/research-triangulate/`, before this skill presents any **repo-external assertion** that goes beyond the auditor's own machine-readable output — a recommended fix version, an interpretation of an advisory's affected range, or a licence's compatibility — triangulate it instead of trusting a single source:

- **Independent sources by blast radius.** At least two independent sources; **at least three** (the Release/dispatch tier) when the assertion will direct a write outside the working copy (a version pin, a sister-repo path, a third-party API signature, an external tool default).
- **Record provenance.** For every source record the URL or path, the source class, and the retrieval date in the audit artifact's source list; at least one source SHOULD carry a verifiable date so a stale advisory or pin is detectable.
- **Surface conflicts, never silent-vote.** When sources disagree, name the most likely explanation and let the operator decide; never apply a majority vote or auto-pick by source class.
- **Mark `unverified` when under-triangulated.** If the required source count is unreachable, mark the assertion `unverified` and hand back to the operator; in an autonomous run with no reachable operator, abort the write and persist the conflict as a findings report.

## Hard rules

- **Never** modify dependency manifests, lockfiles, or ignore lists without explicit user confirmation. This skill reports; mutations are a follow-up step.
- **Never** upgrade dependencies autonomously, even when a fix version is obvious. That's an author decision with test-suite consequences.
- **Never** silently skip an auditor that isn't installed. Emit an install hint and record the skip in the `Health` section, and report that subroot's verdict as `blocked`, **never `pass`** — the gate fails closed on an un-auditable subroot.
- **Always** treat an `unknown`-severity finding as `high` until it is classified otherwise; never let an unclassified finding fall into a lower tier.
- **Never** invent a license policy when the project has no allowlist. Flag findings as `review`, not as failure.
- **Never** report findings below the requested severity floor. Keep the report signal-heavy.
- **Always** prefer a repository-declared Taskfile target over invoking auditors directly, when one exists and wraps the same auditor. This honours any project-specific ignore list the Taskfile applies.
- **Always** attribute every finding to the subroot whose manifest caused it, so consumers with monorepos can act on the right team / package.
- **Always** sort findings deterministically (severity then package name) so the report diffs cleanly.
- When `spec/project/dependency-audit/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: the read-only scan phase is delegated to the `dependency-audit-scanner` agent (context-window isolation, tool restriction), while orchestration and follow-up actions stay in the skill.

- **Orchestration role**: typical callers run this as one step inside a larger flow (pre-PR gate, release cut, periodic security review); the output flows back into the main conversation so the user can triage.
- **Interactivity**: the follow-up actions in Step 6 need user approval — bumping a dependency, adding an advisory ignore entry, drafting a license allowlist — so mid-flow interactivity favours the skill side.
- **Hybrid split**: the pure scanning half (detect lockfile, run auditor, normalise JSON) is self-contained and benefits from context-window isolation; the `dependency-audit-scanner` agent handles it. The follow-up-action half stays here so the user can approve each change interactively.
- **Counter-dimension**: the self-contained, summary-returning shape of the scan phase points toward a pure agent, and its verbose JSON output is exactly the context-window pressure that favours isolation. That pull is honoured — but only for the scan half, which is delegated to `dependency-audit-scanner`. The interactivity of the follow-up actions outweighs it for the capability as a whole, so the orchestrating surface stays a skill.
