# Report shape

The rendered report template, referenced from `SKILL.md` §Operations step 5. Load this file when rendering the report and follow the template exactly; the same structure is persisted as the audit artifact under `.audits/error-tracking-audit/error-tracking-YYYY-MM-DD.md`.

The section structure mirrors the `error-tracking-audit-scanner` inventory one-to-one, so every scanner finding maps to a verdict line without re-interpretation. Sort per component, tool contract before advisory, so the report diffs cleanly across runs. Omit a per-component subsection only when that component has zero findings in it.

```text
# Error Tracking Audit

Scope: <repo root>, <n> components (skipped: <list with reasons>)
Stage vocabulary: <declared values> (declared in: <file:line | UNDECLARED>)
Trigger: <pre-PR | pre-release | periodic>
Adoption context: production deployment declared: <yes | no | undetermined> (recorded exception: <path | none>)
SDK anchors: <component: package + pinned version, ...>
Git revision: <sha>
Previous artifact: <path | none>

## Verdict
<pass | fail> — components failing: <count>, advisory findings: <count>, runtime-verify items: <count>

## <component path>  (<language/framework>, <SDK + version>) — <PASS | FAIL | NOT-REQUIRED>
### Tool contract (hard-fail on any static FAIL)
- SDK declared + initialised at process entry: <PASS | FAIL: late (after <what>) | FAIL: non-protocol client (<package>) | FAIL: <what>> [<file:line>]
- Global handlers active (not disabled): <PASS | FAIL: <what>> [<file:line>]
- DSN source (<deployment env | runtime-injected | build-baked | hardcoded>): <PASS | WARN: build-baked, stage portability | FAIL: literal in source tree> [<file:line>]
- Graceful no-DSN no-op (init path, config loader, health surface): <PASS | FAIL: <what>> [<file:line>]
- Environment tagging (declared vocabulary): <PASS | FAIL: <what>> [<file:line>]
- No production value pinned on a dev/local path: <PASS | FAIL: <value at file:line>> [<file:line>]
- Release tagging (<moves per build | static constant | missing>): <PASS | FAIL: <what>> [<file:line>]
- Sampling decision explicit: <PASS: <rate> | FAIL: no decision> [<file:line>]
- default-PII off (<scanner overall state>; category source: <package@version> via <installed source | body table>): <PASS | per non-PASS category: <category>=<state> → <WARN | FAIL>: <why> | component-level: <overall state> → <WARN | FAIL>: <why>> [<file:line>]
- Before-send scrubbing wired: <PASS (shape: allow-list | deny-list; breadcrumbs: covered | not covered) | FAIL> [<file:line>]  (PII verdict → gdpr-data-protection-reviewer)
- No log-sink misuse: <PASS | FAIL: <levels routed>> [<file:line>]
### Advisory (scored)
- Source-map/symbolication upload per release: <present | absent | n/a> [<file:line>]
- Explicit capture at swallowed-error points: <present | gaps: <count>> [<file:line>]
- Tracker ingest origin in CSP connect-src: <present | absent | undetermined: DSN injected, origin not statically known | n/a> [<file:line>]
- Trace/performance sample rate (informational; the mandatory knob is the error rate): <explicit: <rate> | not configured> [<file:line>]

## Cross-component consistency
- Stage vocabulary identical across components: <PASS | FAIL: <divergence>>
- Shared init module: <single source | copied ×<n> (drift guard: <present | absent>)>
- Components with no wiring: <component> — <PASS: exception recorded at <path> | NOT-REQUIRED: no production deployment declared | Critical: production deployment declared + structural exposure marker (<marker>) | Warning: production declared, no exposure marker — operator decision | Warning: exposure undetermined — operator decision>

## Runtime-verify (documented, never a static verdict)
- <item> — <what a live check must confirm> — <owner>

## Health
- Components audited: <list>; skipped (with reason): <list or none>
- SDK packages/versions pinned: <list>
- Scanner gaps carried over (stack not identified, fallback detection used): <list or none>
- Runtime-verify items surfaced: <count>
```

On the `default-PII off` line, render one finding per non-PASS category; when the scanner's overall state carries no categories (`EXPLICIT TRUE`, or `UNSET` on an SDK whose category set is unknown), render one component-level finding instead, such as `EXPLICIT TRUE → FAIL: legacy flag true, no structured block`. A Critical ruling renders as `FAIL`, a Warning as `WARN`.

**Remediation for a default-PII FAIL**: carry this into the report so the `plan` operation inherits it. The legacy flag can't reach PASS on its own: Sentry JS `10.75.3` still collects `graphQL.variables` and `stackFrameVariables` under `sendDefaultPii: false`, and `sentry-sdk` Python still collects `http_bodies` under `send_default_pii=False`. The fix is the structured option with every category off in the SDK's own spelling: `dataCollection` on Sentry JS releases that ship it (`10.75.3`, 11), `false` per category and `[]` for `httpBodies`; `data_collection` on `sentry-sdk`, with `{"mode": "off"}` for the key-value categories, `False` for the boolean ones, and `http_bodies: []`. `data_collection=` is a top-level option only from `sentry-sdk` `2.70.0`; on `2.67.0`–`2.69.2` pass the same dict as `_experiments={"data_collection": {…}}`, because a top-level key there makes `init()` raise `TypeError`; below `2.67.0` no integration honours either spelling, so upgrade first (measured 2026-09-25). On a JS 10 release without `dataCollection`, upgrade first. On Python, `include_local_variables=False` alone isn't enough, because `http_bodies` stays on.

Severity mapping is stated once, in `SKILL.md` §"Hard-fail policy" — follow it there rather than re-deriving it here, so the two cannot drift apart.
