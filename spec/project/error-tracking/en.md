# Error Tracking

Status: draft
Portfolio-Scope: portfolio

## Context

An application that only writes errors to logs makes its operators pull: someone has to open the log backend, know what to search for, and reconstruct one failure from many scattered lines. An **error-tracking platform** inverts that into push: the application's SDK captures every unhandled exception with its full context (stack trace, request data, runtime, release, environment), the platform **groups** recurring events into deduplicated *issues*, counts and trends them, detects when a fixed issue **regresses** in a later release, and **alerts** the owning team when something new or resurgent appears. That issue-centric workflow—see, triage, fix, verify—is the mechanism by which the tool improves in-house applications: defects surface minutes after they first happen in any environment, not weeks later out of a support ticket.

The reference tool for this spec is **GlitchTip** (<https://glitchtip.com/>): open source (MIT-licensed backend), self-hostable or hosted, compatible with the Sentry client SDKs, and covering error tracking plus uptime monitoring, basic performance tracing, and log capture. The contract below, however, binds to the **capability class**, not the product: any platform that speaks the Sentry SDK protocol and offers grouping, environments, releases, alerting, and an issue lifecycle satisfies it (Sentry itself, Bugsink, and comparable trackers). Verified against the vendor sources on 2026-07-25; see References.

The tool is useful in **every lifecycle phase of an application, but with different requirements per phase**. During *development* it gives fast feedback without polluting production data; during *test/staging* it catches regressions under production-like wiring before a release; during *production operation* it's the primary detector for real-user failures and the trigger for the fix loop. A large part of this spec therefore is the per-phase contract, plus the duties that come with operating such a tool at all (data protection, triage discipline, and running the tracker itself).

Neighbour delimitation, so nothing is restated: `spec/project/monitoring-observability/` owns the vendor-neutral telemetry *contract* the application emits (metrics, structured logs, traces, health/SLO—including the mandatory browser error-capture floor and the `[locked]` PII-redaction pillar); this spec owns the **error-tracking tool layer** that receives error events and the workflow around it. `spec/project/gdpr-audit-process/` owns the PII-class definition and audit verdict. `spec/project/api-error-handling/` owns the error *response* contract an API returns to clients. `spec/project/workflow-health/` owns red CI runs—build-time failures aren't runtime error tracking.

Readers: developers wiring an application to an error tracker, operators running one (self-hosted or SaaS), and reviewers judging whether a project's error-tracking posture matches its lifecycle phase.

## Goals

- Every in-house application with real users has a defined error-tracking posture: which tool, which projects/environments, who gets alerted, and who triages
- The application-side contract is **tool-neutral**: instrumentation binds to the Sentry SDK protocol and to capability-class concepts (DSN, environment, release, issue lifecycle), so the backend is swappable without touching application code; GlitchTip is named only as the non-binding reference profile
- The **lifecycle phases** (development, test/staging, production) each have an explicit requirements set, because their purposes differ: feedback speed, release gating, and incident detection respectively
- The duties that come **with** operating the tool are explicit: PII discipline at the SDK boundary, event-volume control, triage service levels, data retention, and operating the tracker itself as production infrastructure
- Error tracking closes the loop with the delivery process: issues found by the tracker feed the normal issue → fix → release flow, and release tagging makes regressions attributable to the release that introduced them

## Non-Goals

- The application's general telemetry contract—metrics, structured logs, distributed traces, health/SLO—which is owned by `spec/project/monitoring-observability/`; an error tracker complements, never replaces, those four pillars
- Defining what counts as personal data or auditing leaks—the PII class and verdict are owned by `spec/project/gdpr-audit-process/`; this spec only wires the producing-side controls into the SDK configuration
- The shape of HTTP error responses returned to API clients (owned by `spec/project/api-error-handling/`)
- CI/build failure triage (owned by `spec/project/workflow-health/`); the tracker watches running applications, not pipelines
- Full APM/RUM adoption: the reference tool's performance tracing and the Core Web Vitals layer stay advisory exactly as `spec/project/monitoring-observability/` classifies them
- Mandating one concrete alerting channel, triage SLA number, retention period, or sampling rate—those are project-defined; this spec mandates that each **exists and is written down** (the portfolio defaults recorded in the requirements are SHOULD-level recommendations, project-overridable, not mandates)
- Selecting the tracker for third-party/off-the-shelf software the portfolio merely operates; the scope here is in-house developments

## Requirements

### Tool-neutral core (mandatory)

- The error tracker **MUST** be selected from the capability class defined by these six capabilities: (1) event ingestion via **Sentry-SDK-protocol-compatible** client SDKs configured by a **DSN**; (2) automatic **grouping** of recurring events into issues; (3) an **environment** dimension on every event; (4) a **release** dimension on every event; (5) **alert rules** on new and regressed issues; (6) an **issue lifecycle** (open → resolved → regressed, plus an explicit ignore state). Any product with these six satisfies this spec—the contract binds the class, not the vendor
- Application instrumentation **MUST** use the standard Sentry-compatible SDK for its platform rather than a vendor-proprietary client, so switching backends (GlitchTip ↔ Sentry ↔ compatible) is a configuration change (the DSN), never a code change
- The DSN **MUST** be injected via environment/deployment configuration and **MUST NOT** be hardcoded in the source tree; a missing DSN **MUST** degrade gracefully—the SDK stays a no-op and the application starts and runs normally, so local checkouts and CI need no tracker
- One logical application **SHOULD** map to one tracker project per major component (backend, frontend, worker), with deployment stages separated by the environment tag inside those projects; a separate dev project **MAY** be used where hard isolation of experimental noise is wanted

### Integration contract (mandatory)

- The SDK **MUST** be initialised at process entry, before request handling or job consumption begins, with the platform's global handlers active—uncaught exceptions and unhandled promise rejections are captured without per-callsite code. For browser frontends this is the same two-listener floor that `spec/project/monitoring-observability/` §Frontend observability already mandates; the tracker is the natural sink for it
- Every event **MUST** carry an `environment` value from the project's declared, closed stage vocabulary (for example `development`, `staging`, `production`; the exact names are project-defined but **MUST** be used consistently across all components of the application, because alert rules and release gates filter on them)
- Every deployed build **MUST** set a `release` identifier resolvable to a unique code state (the release tag or the commit SHA; for repositories governed by `spec/project/release-automation/` the release tag is the natural choice). Without release tagging, regression detection and "which deploy introduced this" attribution are impossible—release tagging is what turns the tracker from an error list into an improvement loop
- Errors that are caught and degraded **SHOULD** still be reported explicitly at the decision point (the SDK's capture call with added context), because a swallowed error is invisible to every phase of this spec; this is the runtime complement of the swallowed-error no-go in `spec/project/source-code-review/`
- The tracker **MUST NOT** be used as a general log sink: only events at error severity or deliberately captured messages belong there. Routing all INFO/DEBUG logs into the tracker destroys grouping quality and event budgets; the structured-log pillar of `spec/project/monitoring-observability/` owns logs
- PII controls **MUST** be active at the SDK boundary: the SDK's default-PII behaviour stays off (no raw cookies, auth headers, or request bodies with personal data), and a scrubbing hook (the SDK's before-send filter or equivalent) removes or masks identified fields before the event leaves the process. This is the error-event instance of the `[locked]` emission-boundary redaction pillar in `spec/project/monitoring-observability/`; what counts as personal data is defined by `spec/project/gdpr-audit-process/` and isn't restated here
- Client-side volume controls **MUST** be configured deliberately: an explicit sample-rate/rate-limit decision per project (100% is an acceptable decision for low-traffic services—the requirement is that it's a decision, written in the project's configuration, not an accident), so an error storm can't exhaust quota or take the tracker down. Absent a project-specific decision, the portfolio default **SHOULD** apply (settled 2026-07-25): 100% sampling for low-traffic services, re-evaluated as soon as event volume becomes noticeable
- For minified or transpiled frontend builds, source maps (or the platform's equivalent symbolication artefacts) **SHOULD** be uploaded per release, because an unreadable stack trace defeats the tool's purpose

### Development phase (mandatory when adopted)

The phase's purpose is **fast feedback for the person coding**: the console and debugger are primary, the tracker is secondary.

- Local development **MUST NOT** report into the production tracker project with a production environment tag; the default posture is *SDK disabled locally* (no DSN set), which the graceful-degradation rule above makes free
- A developer **MAY** point a local run at a dev project or `development` environment when the error-tracking wiring itself is under test (grouping behaviour, scrubbing hooks, alert rules); the SDK's debug mode **MAY** be enabled there
- Alert rules **MUST NOT** page anyone for events tagged with the development environment
- The SDK wiring **SHOULD** be part of the application scaffold from the first vertical slice, not bolted on before go-live—retrofitting global handlers, environment/release tagging, and scrubbing late is exactly how PII leaks and untagged releases happen

### Test/staging phase (mandatory when a staging stage exists)

The phase's purpose is **catching regressions before a release**, under wiring identical to production.

- Staging/e2e deployments **MUST** report to the tracker with their own environment tag and the candidate release identifier, using the same SDK configuration path as production—staging is the rehearsal for the production wiring, and a scrubbing hook that's never exercised before production is untested PII protection
- A new issue first seen in staging for a candidate release **SHOULD** block that release's promotion until triaged (fixed, or explicitly accepted with a recorded reason); this is a release-readiness input alongside the gates the project already runs
- Deliberately provoked failures from negative/e2e tests **SHOULD** be kept out of alert noise—either filtered client-side (a tag test suites set) or excluded by alert-rule scoping—so staging alerts stay meaningful
- Staging alerts **SHOULD** notify a team channel and **MUST NOT** page on-call; paging is reserved for production impact

### Production phase (mandatory)

The phase's purpose is **detecting real failures and driving the fix loop**; in production the tracker is a primary operational signal, not an optional convenience.

- Every production deployment of an in-house application with real users **MUST** report to an error tracker; running one without is a recorded, justified exception, not a default
- Alert rules **MUST** be configured for at least: a **new issue** in the production environment, and a **regression** (an issue previously resolved reappearing). Every alert route **MUST** have a named owning team—an alert nobody owns is noise by construction
- New production issues **MUST** be triaged within a project-defined service level (the number is per-project; its existence isn't; the portfolio default **SHOULD** be one business day, settled 2026-07-25). Triage means a human decides: fix now, schedule, or ignore with a recorded reason. The issue lifecycle states **MUST** be used truthfully—resolve on fix, ignore only deliberately—because an issue list that's 90% stale is a tracker nobody reads, and an unread tracker is strictly worse than none: it produces the false confidence of "we'd know"
- Issues requiring code changes **SHOULD** be carried into the project's normal issue workflow (a linked GitHub issue referencing the tracker issue), so the fix flows through the standard branch → PR → release pipeline and the tracker issue is resolved when the fixing release deploys. Creating that link is a **manual** triage act; an automatic tracker-to-GitHub issue bridge is deliberately not used (settled 2026-07-25)
- A regression (an issue resolved in release N reappearing in release N+M) **MUST** be treated with at least the priority of a new issue; regressions are the tool's highest-value signal and only exist because of the mandatory release tagging above
- An **error storm** (event volume saturating the configured rate limits) **MUST** be treated as an incident signal in itself, even when each individual event looks minor
- The reference tool's uptime monitoring **MAY** be used as the black-box probe for third-party/own endpoints, feeding the third-party floor of `spec/project/monitoring-observability/`; it complements and **MUST NOT** replace the health/SLO pillar there

### Operating the tool (mandatory while in use)

- **Data protection**: where events may contain personal data despite scrubbing, the tracker is a processing system in the GDPR sense. Self-hosting keeps event data in-house and is the portfolio default posture; using a hosted tracker **MUST** be preceded by a data-protection review (processing agreement, storage location) per `spec/project/gdpr-audit-process/`. Event **retention MUST** be explicitly configured (project-defined period; the portfolio default **SHOULD** be 90 days, matching the reference tool's own default), not left at "forever"
- **The tracker is production infrastructure**: a self-hosted tracker **MUST** itself be operated to the portfolio's deployment bar (for Kubernetes deployments, `spec/project/kubernetes-deployment-best-practices/` and the chart specs apply), including backups of its datastore and a maintained update cadence. At least one **availability signal for the tracker itself MUST** live outside the tracker (an external uptime check or the cluster's own monitoring)—the watcher needs a watcher, because a silently-down tracker looks identical to a healthy application. The portfolio posture (settled 2026-07-25) is **one shared self-hosted instance** serving all in-house applications, separated per tracker organisation/project, rather than one instance per cluster or application
- **SDK currency**: tracker SDKs **MUST** be part of the project's normal dependency-update flow (Renovate per the portfolio baseline, `spec/project/dependency-audit/` for the audit side); an outdated SDK is both a security surface and a compatibility risk against the server
- **Access control**: tracker organisations/teams **SHOULD** follow least privilege—event payloads can contain sensitive context even after scrubbing, so read access isn't org-wide by default
- **Cost/quota hygiene**: on a hosted plan the event quota is a budget (the reference tool's free tier is 1,000 events/month—one noisy production bug exhausts that in minutes); quota consumption **SHOULD** be reviewed periodically and sampling adjusted deliberately rather than letting the plan's hard cap silently drop events

### Reference profile (non-binding)

- Concrete tooling **MAY** be named only here, and this section is explicitly non-normative. The portfolio reference is **GlitchTip**: open source (MIT-licensed backend, source on GitLab), Sentry-SDK-compatible, feature set covering error tracking, uptime monitoring, basic performance tracing, and log capture; deployable self-hosted (the portfolio default, Docker/Kubernetes) or as SaaS (free tier 1,000 events/month, paid tiers by volume, as of 2026-07-25). A project **MAY** substitute any capability-class-compliant tracker (Sentry self-hosted/SaaS, Bugsink, comparable) and still satisfy every mandatory requirement
- Selection criteria when substituting: Sentry-protocol compatibility (protects the application-side contract), self-hostability and data locality (protects the data-protection posture), and operational weight (a tracker heavier to run than the applications it watches is the wrong trade for a small portfolio)

## Acceptance Criteria

- [ ] `spec/project/error-tracking/` exists with `en.md` (canonical) and `de.md` (translation), carries `Portfolio-Scope: portfolio`, and is listed in `spec/README.md`
- [ ] The tool-neutral core is stated as a mandatory section: the six-capability class definition, Sentry-SDK-protocol instrumentation, DSN via environment with graceful no-DSN degradation, and the project/environment mapping rule
- [ ] The integration contract is stated with RFC 2119 keywords: SDK init at process entry with global handlers, mandatory `environment` and `release` tagging, no log-sink misuse, PII scrubbing at the SDK boundary referencing the locked observability pillar and `gdpr-audit-process`, deliberate volume controls, and source-map upload for frontend builds
- [ ] All three lifecycle phases have their own requirements section, and the per-phase purposes (feedback / release gating / incident detection) are explicit
- [ ] The development phase forbids polluting production data and paging from dev events, and states the scaffold-early rule
- [ ] The test/staging phase mandates production-identical wiring with its own environment tag, states the new-issue-blocks-promotion gate as SHOULD, and reserves paging for production
- [ ] The production phase mandates tracker adoption for user-facing in-house applications, new-issue and regression alerts with named owners, a triage service level, truthful issue-lifecycle use, regression priority, and the error-storm-as-incident rule
- [ ] The operating duties are stated: GDPR posture (self-hosting default, review before SaaS, explicit retention), tracker-as-production-infrastructure with an external availability signal, SDK currency via the dependency flow, least-privilege access, and quota hygiene—plus the portfolio SHOULD-defaults (one-business-day triage, 90-day retention, 100% low-traffic sampling, one shared self-hosted instance)
- [ ] Neighbour delimitation is explicit and reference-only: `monitoring-observability` (telemetry contract, frontend floor, locked PII pillar), `gdpr-audit-process` (PII class/verdict), `api-error-handling` (response contract), `workflow-health` (CI failures)
- [ ] GlitchTip appears only in Context and the non-binding reference profile; every mandatory requirement is satisfiable by any capability-class-compliant tracker
- [ ] A reviewer can hold a real project against this checklist and mark each requirement done or not done

## Open Questions

All five original open questions were settled by the operator on 2026-07-25; the decision records stay here for traceability. The one genuinely open remainder is the concrete shape of the audit capability.

- **First adopter and dogfooding (settled 2026-07-25).** kamerplanter is the first adopter; the application-side preparation is tracked in nolte/kamerplanter#777. The portfolio runs **one shared self-hosted GlitchTip instance** on the production cluster, separated per tracker organisation/project; provisioning is tracked in nolte/k8s-home-lab#833 using the official GlitchTip Helm chart, operated to the Kubernetes baseline referenced in §Operating the tool.
- **Future `error-tracking-audit` capability (planned 2026-07-25, shape open).** Tracked as `nolte/claude-shared#516`, authored after the kamerplanter dogfooding has produced a real adopter to calibrate the checks against. The concrete check set and report format remain the one open point, fixed when authored.
- **Issue-bridge automation (settled 2026-07-25: manual).** Tracker issues don't open GitHub issues automatically; carrying a finding into the issue workflow is a human triage act, now normative in §Production phase. Revisit only if production volume ever makes manual triage the bottleneck.
- **Portfolio-scope promotion (settled 2026-07-25: promoted).** The spec carries `Portfolio-Scope: portfolio` like its `monitoring-observability` sibling; consumer repositories inherit it by reference per `spec/project/portfolio-inherited-spec-layer/` when they next bump their pinned `ref`.
- **Portfolio default numbers (settled 2026-07-25).** The moderate SHOULD-set is normative in the respective sections: triage of new production issues within one business day, event retention 90 days, and 100% sampling for low-traffic services re-evaluated once volume becomes noticeable; all remain project-overridable.

## References

- [R1] *GlitchTip*, product page—feature set (error tracking, uptime, performance, logs), Sentry-SDK compatibility, hosting and pricing (verified 2026-07-25): <https://glitchtip.com/>
- [R2] *GlitchTip documentation*, covering installation, SDK integration, and the feature docs: <https://glitchtip.com/documentation>
- [R3] *GlitchTip backend repository*, MIT license (verified 2026-07-25): <https://gitlab.com/glitchtip/glitchtip-backend>
- [R4] *Sentry SDK documentation*, the platform-SDK configuration surface (DSN, environment, release, before-send scrubbing, sampling) the tool-neutral contract binds to: <https://docs.sentry.io/platforms/>
- [R5] `spec/project/monitoring-observability/`, the telemetry contract this spec complements: frontend error-capture floor, third-party probing, and the `[locked]` PII-redaction pillar
- [R6] `spec/project/gdpr-audit-process/`, the PII-class definition and audit verdict referenced by the scrubbing and data-protection requirements
