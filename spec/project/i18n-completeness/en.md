# i18n Completeness Audit

Status: draft

## Context

A localized application keeps its user-facing strings in per-locale translation files (one JSON or YAML tree per language) and references them from code through an i18n library's lookup call (`t('key')`, `i18nKey="key"`, `$t('key')`, `<FormattedMessage id="key">`, and similar). Three drifts accumulate silently as the app grows: a key added to the reference locale never lands in the other locales (a user sees a raw key or a fallback-language string); a key referenced in code is never defined (a runtime miss); and a key defined in the files is no longer referenced anywhere (dead weight that misleads translators). None of these is caught by a type-checker or a test suite by default, and they surface as production UI defects in the least-tested locale.

This spec governs a focused, **read-only completeness audit** of translation files against each other and against code usage, operationalised by the `i18n-completeness-checker` agent (`distribution: plugin`). It's the generalised successor to a project-local checker that hard-coded one app's locale paths, reference language, and `react-i18next` call-site patterns. The portfolio form discovers the locale files and source roots and adapts to the project's declared i18n library instead of assuming one.

Readers: agent authors maintaining the checker; reviewers verifying its findings; developers who run it after a feature, before a release, or inside a pre-PR check.

## Goals

- Surface the three completeness drifts—cross-locale parity gaps, code-used-but-undefined keys, and defined-but-unused keys—as a single severity-sorted report
- Stay framework-agnostic in the core algorithm (set-diff across locales plus a usage scan) while adapting the call-site patterns to the project's actual i18n library
- Stay strictly read-only: the audit reports, it never edits translation files or code
- Make the audit cheap to re-run repeatedly within a sprint, because it's side-effect-free
- Draw a clear boundary to the broad webview-UI i18n review and to translation authoring, so the agent is invoked only for file-level completeness

## Non-Goals

- Authoring or correcting translations—the audit reports gaps, a human or a translation workflow fills them
- The broad web-UI internationalisation review (RTL pipeline, i18n bootstrap, locale-switching UX) owned by `spec/frontend/webview-ui-optimization/`; this spec is the narrow file-vs-code completeness slice
- Judging translation *quality* (fluency, tone, terminology) beyond the mechanical "identical across locales ⇒ probably untranslated" heuristic
- Enforcing a particular key-naming convention; the audit MAY report convention drift when a convention is declared, but it doesn't impose one
- Runtime locale loading, lazy-namespace splitting, or bundle-size concerns

## Requirements

### Inputs and discovery

- **MUST** discover the set of per-locale translation files rather than hard-coding any one project's path; the operator MAY point the audit at an explicit locale directory, and absent that the agent locates the conventional locale tree (for example `**/locales/<lang>/*.json`, `**/i18n/<lang>.json`, `**/lang/*.yaml`)
- **MUST** determine a single **reference locale** (the source-of-truth language other locales are measured against): use the operator-named one, else the project's declared default locale, else fall back to a documented heuristic and state which locale it picked
- **MUST** discover the source roots to scan for key usage rather than hard-coding one app's path, and report which roots and file globs it scanned
- **MUST** adapt the call-site lookup patterns to the project's i18n library (react-i18next / i18next `t('…')` and `i18nKey="…"`, `vue-i18n` `$t('…')` / `<i18n-t>`, FormatJS / react-intl `formatMessage`/`<FormattedMessage id>`, and comparable); when the library can't be determined, state the assumed pattern set in the report

### Audit dimensions

- **MUST** flatten every locale file to dotted key paths and compute, against the reference locale: keys present in the reference but missing in another locale, and keys present in another locale but missing from the reference (structural divergence)
- **MUST** report a **structural mismatch** when the same key path resolves to different value types across locales (string in one, object/nested in another)
- **MUST** scan the source roots for key references and classify: a key used in code but defined in no locale (**critical**: a runtime miss), and a key defined in the locales but referenced nowhere in code (**orphan**, informational)
- **MUST** treat statically-undecidable dynamic keys (template-string or variable lookups such as `` t(`enums.${type}`) ``) as a noted caveat, never as a hard miss—report them as "dynamic, not statically verifiable" so they neither inflate the critical count nor get silently dropped
- **SHOULD** run quality heuristics: empty string values per locale; values identical across the reference and another locale (likely untranslated); and interpolation-placeholder parity (the same `{{var}}` / `{var}` / `%s` placeholders appear in every locale's value for a key)
- **MAY**, when the project declares a key-naming convention, report keys that violate it; absent a declared convention the agent doesn't invent one

### Output and side effects

- **MUST** be strictly read-only: declare only read and search tools, and never edit translation files, code, or any other file; the single output is a report
- **MUST** emit a single severity-sorted report ordered **critical** (used-but-undefined; missing in a locale), then **warning** (orphans, structural mismatch), then **info** (identical values, empty values, placeholder drift), led by a summary metrics table (per-locale key counts, missing, orphan, empty, identical, dynamic-skipped)
- **MUST** cap per-category output (for example: show the first N entries and summarise the remainder as "… and {n} more") so a large drift doesn't produce an unreadable wall of keys
- **SHOULD** attribute each used-but-undefined key to a source location (file and line) so the finding is actionable
- **MUST** report which locale files, source roots, globs, reference locale, and call-site patterns it used, so the audit's scope is auditable and reproducible

## Acceptance Criteria

- [ ] Running the audit on a project with diverging locale files produces a severity-sorted report whose summary table lists per-locale key counts plus missing, orphan, empty, identical, and dynamic-skipped counts
- [ ] A key present in the reference locale but absent from another locale appears under a critical "missing translation" finding naming the locale
- [ ] A key referenced in code but defined in no locale appears as critical with a source file:line attribution
- [ ] A key defined in the locales but referenced nowhere appears as an informational orphan, not as a critical finding
- [ ] A dynamic/template-string lookup is reported as "dynamic, not statically verifiable" and is excluded from the critical count
- [ ] A key whose value type differs across locales (string vs. object) is reported as a structural mismatch
- [ ] The report states the discovered locale files, source roots and globs, the chosen reference locale, and the call-site patterns used
- [ ] The agent declares only read/search tools (no write, edit, or execution tools) and makes no file modifications
- [ ] Invoking the audit on a project whose i18n library can't be determined still runs, stating the assumed call-site pattern set in the report
- [ ] The agent cites this spec in its body or `description`

## References

- [R1] Agent authoring rules this agent conforms to: `spec/claude/agent-management/`
- [R2] Skill-vs-agent decision rule and rationale-section requirement: `spec/claude/skill-vs-agent/`
- [R3] Adjacent broad web-UI internationalisation review (delimited against this spec): `spec/frontend/webview-ui-optimization/`
- [R4] Review-plan / audit-output conventions for severity-sorted reports: `spec/claude/review-plan/`

## Open Questions

- Should the audit support a project-level config file (declaring locale paths, reference locale, source globs, and i18n library) so repeat runs need no operator arguments, or is per-invocation discovery sufficient?
- For monorepos with multiple independent locale trees (per package), should the audit treat each tree separately or merge them, and how's the boundary declared?
- Should the "identical across locales" heuristic exempt locales that are legitimately close (for example proper nouns, brand names, units), and if so via an allowlist?
- Should placeholder-parity checking understand ICU MessageFormat plural/select syntax, or stay at simple-placeholder granularity until an ICU-aware pass is warranted?
