---
name: error-tracking-audit
description: Audits an app's error-tracking wiring against spec/project/error-tracking/ and produces a severity-classified audit artifact plus a plan for the gaps. The default `audit` operation dispatches the read-only error-tracking-audit-scanner agent, then hard-fails on any static tool-contract violation (SDK init at process entry with global handlers, DSN from deployment config, environment and release tagging, explicit sampling, default-PII off plus a wired scrubbing hook, no log-sink misuse) and on a divergent stage vocabulary; tracker-side behaviour is verify-at-runtime. The `plan` operation dispatches implementation-plan-author so a specialist (fullstack-developer) wires the fix — there is no mechanical apply. Invoke to audit error tracking or check Sentry-protocol SDK wiring; also German. Don't use for the telemetry pillars (observability-audit), the PII/GDPR verdict (gdpr-data-protection-reviewer), or red CI runs (workflow-health-triage). Supports resume.
tags: [audit]
phase: quality
summary: "Audits an app's error-tracking wiring against the spec (SDK init, DSN source, environment/release tagging, sampling, PII controls), reports findings, and hands the gaps to a specialist as a plan."
summary_de: "Auditiert die Error-Tracking-Verdrahtung gegen die Spec (SDK-Init, DSN-Quelle, Environment-/Release-Tagging, PII-Kontrollen), meldet Findings und übergibt Lücken als Plan an einen Spezialisten."
use_when:
  - "you want to audit an app's error-tracking wiring against the portfolio contract"
  - "you want a pre-PR or pre-release error-tracking gate before a production deployment"
  - "you want SDK init, DSN source, environment/release tagging and PII scrubbing checked"
  - "you want the error-tracking gaps turned into a specialist-ready implementation plan"
dont_use_when:
  - situation: "You want the four telemetry pillars, the browser error-listener floor, or the cardinality guardrail audited"
    alternative: observability-audit
  - situation: "You want the PII-class definition or the GDPR audit verdict on a leak"
    alternative: gdpr-data-protection-reviewer
  - situation: "You want the raw detection inventory without triage, verdict, report, or plan"
    alternative: error-tracking-audit-scanner
  - situation: "You want the HTTP error-response contract an API returns to clients checked"
    alternative: api-error-check
  - situation: "You want red CI runs or pipeline failures triaged"
    alternative: workflow-health-triage
see_also:
  - error-tracking-audit-scanner
  - observability-audit
  - implementation-plan-author
  - fullstack-developer
resumable: true
---

# Error Tracking Audit

Audit an application's error-tracking wiring against the portfolio contract, produce a severity-classified audit artifact, and hand the gaps to a specialist as an implementation plan. The `audit` operation reports; the `plan` operation turns the findings into specialist-mapped work packages. **There is no mechanical `apply`** — SDK bootstrap, tagging, and scrubbing wiring are real code changes, so remediation is a plan a specialist implements, not an in-place rewrite.

Implements `spec/project/error-tracking/`, which defines the six-capability tool class, the tool-neutral integration contract, the three lifecycle phases with their differing mandates, and the operating duties. This skill owns policy, severity, the report, and the handover; detection belongs to the `error-tracking-audit-scanner` agent.

Delimitation, mirroring the spec's own: `observability-audit` (`spec/project/monitoring-observability/`) owns the four telemetry pillars, the browser error-listener floor, the third-party floor, and the cardinality and PII-redaction guardrails; this skill owns the **error-tracking tool layer** those events land in. `gdpr-data-protection-reviewer` owns the PII-class definition and the leak verdict — here only *that* scrubbing is wired is checked. `api-error-check` owns the error *response* contract an API returns to clients. `workflow-health-triage` owns red CI runs; the tracker watches running applications, not pipelines. The spec's SDK-currency MUST (tracker SDKs stay in the project's normal dependency-update flow) is real but not this skill's gate — it belongs to Renovate and `dependency-audit`; record the pinned SDK version here and route a stale one there rather than hard-failing it.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Error-Tracking auditieren" / "Fehler-Tracking gegen die Spec prüfen"
- "Sentry-/GlitchTip-Anbindung prüfen" / "SDK-Verdrahtung prüfen"
- "PII-Scrubbing und Release-Tagging im Tracker prüfen"

## User-language policy

Detect the user's language from their message and respond in it. The audit artifact uses English section headings (so downstream tooling and the plan author can parse it reliably); prose around the report is localised.

## Inputs

- **Repo root**: default is the current working directory.
- **Operation**: `audit` (default, read-only) or `plan` (dispatches the plan author against an existing audit artifact). Never author a plan without an audit artifact to ground it.
- **Stage vocabulary**: the project's declared, closed set of `environment` values and where it is declared. Absent an operator-supplied set, take the scanner's detected one; no declaration anywhere is itself a finding.
- **Adoption context**: whether the repository declares a production deployment for the audited components, and the path of any recorded adoption exception. Never infer real-user exposure — see Hard-fail policy.
- **SDK anchors**: the tracker SDK package and pinned version per component. Record them; the default-PII ruling depends on the pinned SDK's documented default, so a floating anchor gives a non-reproducible verdict.

## Operations

### `audit` (default, read-only)

1. **Dispatch the read-only scan agent.** Dispatch `error-tracking-audit-scanner` (Agent) for the detection pass. It returns a per-component inventory with `file:line`, every finding tagged `[static]` or `[runtime-verify]`, in per-component `### Tool contract` and `### Advisory` sections plus `## Cross-component consistency`, `## Runtime-verify`, and `## Health`. It assigns no severity and no verdict. Wait for its inventory, and never re-run its detection procedure here.
2. **Apply the hard-fail policy** (below) over the mandatory tool-contract checks and the cross-component stage vocabulary.
3. **Score the advisory items.** Source-map/symbolication upload per release, explicit capture at swallowed-error points, and the tracker ingest origin in the CSP `connect-src` are SHOULD-class: scored and surfaced, never promoted to a hard fail. A shared init module copied per build context is likewise advisory.
4. **Document the `[runtime-verify]` items** — never a static pass or fail (see Runtime-verify boundary).
5. **Render the report.** Read `references/report-shape.md` when rendering and follow that template exactly; its sections mirror the scanner's inventory one-to-one, so a finding maps to its verdict without re-interpretation. Sort per component, tool contract before advisory, so the report diffs cleanly across runs.
6. **Persist the audit artifact** to `.audits/error-tracking-audit/error-tracking-YYYY-MM-DD.md`. It MUST record: date; trigger (pre-PR / pre-release / periodic); scope (components audited, what was skipped and why, the declared stage vocabulary and where it is declared); the pinned SDK packages and versions; the per-component pass/fail verdict with each hard-fail reason; the runtime-verify items surfaced for a live check; and the Git revision audited. Link to the prior artifact so the progression stays traceable.

### `plan` (turns the findings into a specialist-ready implementation plan)

Run when the caller wants the gaps turned into work. This operation performs **no** code change itself.

- **Dispatch `implementation-plan-author`** (Agent) with the persisted audit artifact as its **grounded input**, rather than a GitHub issue. A proposed remediation is a hypothesis, so this brief **MUST** authorise refutation per `spec/claude/dispatch-brief/`: the plan author and the downstream `fullstack-developer` may refute a wiring fix with contradicting evidence (a `file:line`, or a command with its output) plus what they did instead, and that refutation is a valid result the skill records and reconciles rather than discards. The read-only `audit` scan is scope-only detection, which that spec exempts.
- **Map wiring work to `fullstack-developer`** — SDK bootstrap, DSN plumbing through deployment configuration, `environment`/`release` tagging, a sampling decision, a before-send scrubbing hook, and source-map upload are code changes it owns. A neighbour-owned gap is routed out, not planned here: a PII-class or leak verdict → `gdpr-data-protection-reviewer`; a telemetry-pillar gap → `observability-audit`; tracker-side operation (alert rules, retention, the tracker's own availability signal) → the operator, as infrastructure work outside this repository.
- **Leave `[runtime-verify]` items as explicit plan caveats** — verification work for the operator, not a static remediation package.
- The plan author writes its own pre-analysis artifact and returns the work-package table; this skill does **not** dispatch the specialists or open a PR.

## Hard-fail policy

Severities follow `spec/claude/review-plan/`: a hard fail is **Critical**, a scored advisory item is **Warning** or **Suggestion**, and a `[runtime-verify]` item is **Info**. A component is **fail** when any static mandatory check below is violated; advisory findings and `[runtime-verify]` items never flip a pass to fail.

### Adoption: a component with no wiring at all

Adoption is mandatory only for a production deployment of an in-house application with real users, and the spec allows a recorded, justified exception. The skill therefore **never guesses user exposure**; it rules on repository-declared evidence, as an ordered cascade — take the first branch that matches, so the outcomes stay mutually exclusive:

1. **A recorded, justified adoption exception exists** → **PASS with the exception cited**; quote its path in the artifact. A recorded exception is a conformant posture, and it outranks every branch below, which is why it is tested first.
2. **No production deployment path is declared at all** (a library, an internal tool, a spike, a template) → **NOT-REQUIRED (Info)**. Absence of a tracker is conformant there.
3. **A production deployment is declared** (a deployment manifest, chart, or release workflow targeting a stage in the declared production vocabulary) **and** a *structural* exposure marker is present → **Critical**. The markers are declarations, never judgements about who the users are: a declared ingress, route, or public service resource; a shipped browser bundle; or a queue consumer fed by a component carrying one of those. Anything requiring you to reason about real-user exposure belongs in branch 5, not here.
4. **A production deployment is declared and no structural exposure marker is present** (a batch job, an ETL, an internal worker off the request path) → **Warning**. Adoption is likely but unproven: the spec's mandate is scoped to applications with real users, and this component shows none of the markers, so record it as an operator decision — adopt, or record an exception.
5. **Exposure cannot be established statically at all** (the deployment lives outside this repository, or the markers are inconclusive) → **Warning plus an operator decision**: record it as an open scope question rather than inventing either verdict.

### Tool contract: mandatory when wiring exists

Every check in the scanner's `### Tool contract` traces to a MUST in the spec's tool-neutral core and integration contract, and **none of them is advisory**. For the eight binary checks that means a static violation hard-fails outright; the three multi-state checks below (DSN source, `release`, default-PII) trace to the same MUSTs but resolve to a severity per state, because not every state they report is a proven violation. Read `references/check-policy.md` when triaging that section: it fixes, per check, what counts as a violation (SDK initialised at process entry, global handlers not disabled, the graceful no-DSN no-op, environment tagging from the declared vocabulary including the local-path-pins-production sub-case, an explicit sampling decision where only deliberateness is audited, a wired before-send scrubbing hook, and no log-sink misuse). The DSN-source, `release`, and default-PII checks are multi-state; their rulings stay here.

### The three non-binary rulings

The scanner reports these as multi-state on purpose; the split is this skill's to own.

- **`default-PII off`**: explicit `false` → **PASS**. Explicit `true` → **Critical**, the spec's MUST being unconditional. **Unset** (relying on the SDK default) → **Warning**, not a hard fail: the outcome is off for Sentry-protocol SDKs whose documented default is off, but the control is unasserted and an SDK major can flip it silently. It escalates to **Critical** only when the pinned SDK's documented default is *established as* PII-on. When the default cannot be established from the recorded anchor, the finding stays a **Warning** carrying an operator action ("establish the pinned SDK's documented default"); an undetermined state is not a proven MUST violation, and ruling it Critical would contradict how every other undetermined case here is handled. Note that a missing before-send hook is already its own hard fail — don't double-count it as an escalation of this one.
- **DSN source**: deployment environment → **PASS**. Runtime-injected config (secret manager, config service, a container entrypoint writing a served runtime config) → **PASS**; that is deployment configuration by another mechanism, and it keeps the value out of the source tree. **Build-baked** (a build-time bundler variable such as `VITE_*` or `NEXT_PUBLIC_*` frozen into the artifact) → **Warning for every component type**, never Critical: read literally, the spec's rule has two halves — injected via environment/deployment configuration, and no literal in the source tree — and a build-time deployment variable satisfies both. What it costs is stage portability, since one artifact then serves one stage and cannot be redeployed without a rebuild; that is a real concern the spec does not currently mandate, so it is reported and not hard-failed. Do not invent a component-type split here: hard-failing it server-side would enforce an unwritten requirement, and demoting it for browsers would demote a MUST. **Hardcoded literal in the source tree** → **Critical** always; that is the spec's explicit MUST NOT.
- **`release`**: present and moving per build (release tag or commit SHA injected at build/deploy) → **PASS**. **Static constant that never moves** → **Critical**, reported distinctly as a *stale release constant*: every event lands in one bucket forever, so regression detection and deploy attribution — the whole point of the MUST — are defeated exactly as by a missing value, while the remediation differs (wire the build to inject it, do not add the field). One exemption: a version constant the project's release automation bumps per release *is* resolvable to a unique code state; confirm the file is a declared version-bearing file of that flow first. **Missing** → **Critical**.

### Cross-component consistency

- A stage vocabulary **diverging across components** (`prod` here, `production` there) → **Critical**: the spec requires consistent use across all components, because alert rules and release gates filter on it. No declaration anywhere → **Critical** for every component tagging an environment value, since the closed vocabulary is what values are checked against.
- A shared init module copied per build context → **Suggestion** with no drift guard, **Info** with one. The spec states no requirement here, and `spec/claude/review-plan/` invalidates a finding that cites none, so this never rises higher; the scanner is likewise instructed never to flag the duplication itself as a defect. What is worth surfacing is the asymmetric risk: PII-scrubbing rules that diverge between copies leak through the weakest one.

### Runtime-verify boundary

Everything the tracker does server-side, and everything only a live run can show, is `[runtime-verify]` and **never** a static hard fail — including the MUSTs among them, because a MUST that cannot be checked from the source tree is still not statically decidable. Read `references/check-policy.md` §"Runtime-verify inventory" when rendering that section: it enumerates the items and their owners. Document each as an item a live check must confirm.

The scanner's inventory emits only the four it can see the shape of; the rest are spec-derived constants this skill appends, so the report covers the contract rather than only what a repository scan happens to surface. Appending them is not inventing findings — each is carried as an unverified item with its owner, never as a verdict.

## Gotchas

Read `references/gotchas.md` when triaging a finding whose severity or ownership is unclear — it corrects the eight non-obvious facts this audit gets wrong most often: the static-versus-runtime split, why a bare missing DSN is never the finding by itself, why a DSN's visibility is irrelevant while its source is not, why a frozen `release` is worse than an absent one, the scrubbing-wired-versus-PII-verdict boundary, protocol-compatible trackers versus non-protocol clients, the one lifecycle violation visible from the source tree, and why a package name in a manifest is not a dependency declaration.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/error-tracking-audit/<run-id>.yml` after each named phase boundary (detection, triage, artifact-persist, plan-handover). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and the fail-closed semantics on schema or YAML errors live in that spec; don't duplicate them here.

## Hard rules

- **Never** modify the target application in any operation; there is no mechanical `apply`.
- **Never** statically hard-fail a `[runtime-verify]` behaviour (events arriving, an alert firing, a triage service level met, retention configured server-side); document it for a live check.
- **Never** infer a deployment's real-user exposure to force an adoption verdict; walk the adoption cascade in order, rule only on structural markers, honour a recorded justified exception first, and surface an undetermined case as an operator decision.
- **Never** raise an undetermined state to Critical, and never classify any finding as Critical without a spec requirement to cite. A fact you could not establish — an SDK's documented default, a component's exposure, a CSP ingest origin behind an injected DSN — is a Warning with an operator action; stage portability in particular has no requirement behind it today.
- **Never** treat a `release` value that never moves per build as present, and never accept a DSN literal in the source tree for any component type.
- **Never** render the PII-class or leak verdict (`gdpr-data-protection-reviewer`), audit the telemetry pillars or the browser listener floor (`observability-audit`), or triage CI failures (`workflow-health-triage`).
- **Never** promote an advisory (SHOULD) item — source maps, explicit capture, the CSP ingest origin, shared-module drift — to a hard fail, and never demote a mandatory tool-contract check to advisory, without a spec change.
- **Always** record the pinned SDK package and version per component; the unset-default-PII ruling depends on it.
- **Always** persist the audit artifact under `.audits/error-tracking-audit/` with the per-component verdict, hard-fail reasons, runtime-verify items, declared stage vocabulary, and Git revision, and ground the `plan` operation in that artifact.
- When `spec/project/error-tracking/` and this skill disagree, the spec wins; this skill needs the update.

## Why this is a skill, not an agent

This skill follows the hybrid pattern: read-only detection is delegated to the `error-tracking-audit-scanner` agent (context-window isolation, tool restriction), while policy, severity, the report, and the plan handover stay in the skill.

- **Orchestration role**: typical callers run this as one step inside a larger flow (pre-PR gate, release cut, periodic review); the output flows back into the main conversation so the operator can triage.
- **Mid-flow interactivity**: the adoption ruling needs an operator decision whenever exposure cannot be established statically, and the `plan` handoff is operator-gated — both favour the skill side.
- **Persistent artifact**: the deliverable is an on-disk audit artifact under `.audits/error-tracking-audit/`; skills own persistent state.
- **Counter-dimension**: the detection half (locating SDK bootstraps, config layers, tagging, scrubbing hooks, and log bridges across languages and build contexts) is self-contained and verbose — exactly the context-window pressure that favours an agent. That pull is honoured, but only for the scan half, delegated to `error-tracking-audit-scanner`; the interactive adoption ruling and the persistent artifact keep the orchestrating surface a skill.
