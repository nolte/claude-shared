# Tool-contract check policy

Per-check violation definitions for the scanner's `### Tool contract` section, referenced from `SKILL.md` §"Hard-fail policy". Load this file when triaging that section. Every check here traces to a MUST in `spec/project/error-tracking/` §"Tool-neutral core" or §"Integration contract" — except the local-path sub-case of environment tagging, which comes from §"Development phase" — so **each hard-fails on a static violation**; none is advisory. Severity vocabulary is defined once in `SKILL.md`; don't restate it here. The three multi-state checks (DSN source, `release`, default-PII) are ruled on in `SKILL.md`, not here.

## SDK declared and initialised at process entry

A Sentry-protocol-compatible SDK for the component's platform is both declared as a dependency **and** initialised before request handling or job consumption begins (the module executed at process entry: the ASGI/WSGI app factory, `main`, the worker bootstrap, the browser entry module).

- **FAIL** — no SDK declared; a declared SDK never initialised; initialisation behind a lazily imported module that no entry path reaches; initialisation after the server or consumer starts accepting work.
- A vendor-proprietary client instead of the Sentry-protocol SDK is a FAIL too: the spec's swappability rule binds instrumentation to the protocol, not a product.

## Global handlers not disabled

The platform's global capture is active, so uncaught exceptions and unhandled promise rejections are captured without per-callsite code.

- **FAIL** — an explicit opt-out of the platform's global integrations (`default_integrations=False` and its per-SDK equivalents) with no replacement wiring; a framework integration registered in a way that swallows the handler chain.
- Not a FAIL: a narrow per-integration disable that leaves uncaught-exception and unhandled-rejection capture intact. Record it as a note.

## Graceful no-DSN no-op

With no DSN configured, the SDK stays inert and the application starts and runs normally.

- **FAIL** — initialisation raises, exits, or blocks startup on a missing DSN; a required-value assertion on the DSN in configuration loading; a health check that reports unhealthy purely because the tracker is unconfigured.
- This is the rule that makes the spec's development-phase default (*SDK off locally*, no DSN set) free; a component that cannot start without a DSN forces every local checkout and CI job to configure one.

## Environment tagging

Every event carries an `environment` value drawn from the project's declared, closed stage vocabulary.

- **FAIL** — no `environment` set at initialisation or in the deployment configuration.
- **FAIL** — a value outside the declared vocabulary (a typo variant, an ad-hoc stage name).
- **FAIL** — a development or local configuration path (a committed `.env`, a local compose file, a dev profile, a test fixture) that pins a production environment value or ships a production DSN. The development phase forbids reporting into production data, and this is the one lifecycle-phase violation decidable from the source tree alone.

## Sampling decision explicit

An explicit sample rate or rate limit is set in the project's configuration.

- **FAIL** — no sampling or rate-limit value anywhere in the component's configuration.
- **PASS** — any explicitly set value, including 100%. Only deliberateness is audited; never fail a low-traffic service for sampling everything, and never fail a value for being too high or too low.
- Error-sampling and trace-sampling are separate knobs; the mandatory one is the error path. A trace/performance sample rate alone does not satisfy this check.

## Before-send scrubbing wired

A before-send filter (or the SDK's equivalent event processor) removes or masks identified fields before the event leaves the process.

- **FAIL** — no before-send hook or event processor registered; a hook registered but returning the event unmodified on every path (a stub).
- **Not this skill's call** — whether a given field is personal data, and whether a leak occurred: that verdict belongs to `gdpr-data-protection-reviewer` (`spec/project/gdpr-audit-process/`). Report only that scrubbing is or is not wired, with `file:line`.
- An allow-list-shaped hook (drop unless known-safe) is stronger than a deny-list; note the shape, but do not fail a deny-list hook.

## No log-sink misuse

Only error-severity events and deliberate captures reach the tracker.

- **FAIL** — a logging integration configured with an INFO or DEBUG capture level; every log record forwarded as a tracker event; a log handler attached at the root logger with no level floor.
- Breadcrumb capture at a lower level is not misuse — breadcrumbs travel with an error event, they are not events. Distinguish the SDK's breadcrumb level from its event level before reporting.

## Runtime-verify inventory

Referenced from `SKILL.md` §"Runtime-verify boundary". These are the contract's obligations that no source-tree scan can settle; each is rendered as an item a live check must confirm, with its owner, and **never** as a static pass or fail. Several are MUSTs — a MUST that lives in the tracker rather than the repository is still not statically decidable.

- Events actually arriving, and grouping into issues sensibly — *owner: the deploying team*
- Alert rules for a new issue and for a regression, existing, firing, and each carrying a **named owning team** — *owner: the tracker administrator*
- No paging for development-environment events, and no on-call paging for staging alerts (both MUST NOTs; staging notifies a team channel instead) — *owner: the tracker administrator*
- New production issues triaged within the project-defined service level, and truthful issue-lifecycle use — resolve on fix, ignore only deliberately — *owner: the triaging team*
- A data-protection review completed before adopting a **hosted** tracker (processing agreement, storage location); self-hosting is the portfolio default posture — *owner: the operator*
- Server-side event retention explicitly configured rather than left indefinite — *owner: the tracker administrator*
- An availability signal for the tracker itself living **outside** the tracker — *owner: the operator*
- Quota headroom and error-storm behaviour, the storm itself being an incident signal — *owner: the operator*
- The staging promotion gate: a new issue first seen in staging for a release candidate blocks promotion until triaged — *owner: the releasing team*

## Advisory items (scored, never a hard fail)

For completeness, the scanner's `### Advisory` section maps to SHOULD-class requirements: source-map or symbolication upload per release, explicit capture at swallowed-error points, and the tracker ingest origin allow-listed in the CSP `connect-src`. A shared init module copied per build context is advisory as well — **Suggestion** with no drift guard, **Info** with one; the spec states no requirement against it.
