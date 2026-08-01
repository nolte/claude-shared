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
- SDK declared + initialised at process entry: <PASS | FAIL: <what>> [<file:line>]
- Global handlers active (not disabled): <PASS | FAIL: <what>> [<file:line>]
- DSN source (<deployment env | runtime-injected | build-baked | hardcoded>): <PASS | WARN: <why> | FAIL: <why>> [<file:line>]
- Graceful no-DSN no-op: <PASS | FAIL: <what>> [<file:line>]
- Environment tagging (declared vocabulary; no prod value on a local path): <PASS | FAIL: <what>> [<file:line>]
- Release tagging (<moves per build | static constant | missing>): <PASS | FAIL: <what>> [<file:line>]
- Sampling decision explicit: <PASS: <rate> | FAIL: no decision> [<file:line>]
- default-PII off (<explicit false | unset | explicit true>): <PASS | WARN: unasserted | FAIL: <why>> [<file:line>]
- Before-send scrubbing wired: <PASS | FAIL> [<file:line>]  (PII verdict → gdpr-data-protection-reviewer)
- No log-sink misuse: <PASS | FAIL: <levels routed>> [<file:line>]
### Advisory (scored)
- Source-map/symbolication upload per release: <present | absent | n/a> [<file:line>]
- Explicit capture at swallowed-error points: <present | gaps: <count>> [<file:line>]
- Tracker ingest origin in CSP connect-src: <present | absent | n/a> [<file:line>]

## Cross-component consistency
- Stage vocabulary identical across components: <PASS | FAIL: <divergence>>
- Shared init module: <single source | copied ×<n> (drift guard: <present | absent>)>
- Components with no wiring: <component> — <Critical: production deployment declared | PASS: exception recorded at <path> | NOT-REQUIRED: no production deployment declared | Warning: exposure undetermined, operator decision needed>

## Runtime-verify (documented, never a static verdict)
- <item> — <what a live check must confirm> — <owner>

## Health
- Components audited: <list>; skipped (with reason): <list or none>
- SDK packages/versions pinned: <list>
- Scanner gaps carried over (stack not identified, fallback detection used): <list or none>
- Runtime-verify items surfaced: <count>
```

Severity mapping for the artifact, per `spec/claude/review-plan/`: a hard fail is **Critical**, a scored advisory item is **Warning** or **Suggestion**, and a `[runtime-verify]` item is **Info**. Use the Title-Case vocabulary; never invent a level.
