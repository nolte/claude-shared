# Whole-Repository GDPR Data-Protection Audit

Status: draft

## Context

The portfolio already audits a repository's code for general security (`spec/project/code-security-audit/`, OWASP-aligned, whole-repository) and for vulnerable dependencies (`spec/project/dependency-audit/`, CVE-scoped). Neither answers a distinct question that nolte's EU-facing projects must answer: **does this codebase process personal data in a way the GDPR (Regulation (EU) 2016/679) and its German companion law permit?** A security audit asks "can an attacker break in?"; a data-protection audit asks "are we lawfully collecting, minimising, securing, retaining, and deleting personal data, and can a data subject exercise their rights?" The two overlap only at Article 32 (security of processing); everything else—data minimisation, lawful basis, consent, data-subject-rights endpoints, retention, third-country transfers, cookies/trackers—is GDPR-specific and unaudited today.

This spec governs that data-protection audit, operationalised by a `gdpr-data-protection-reviewer` agent (`distribution: plugin`). Like the security auditor it's generalised, **read-only**, and stack-agnostic in methodology: it discovers the repository's stack and personal-data surfaces rather than assuming one app's framework, and it audits—it never edits source, redacts data, or applies fixes.

The audit has one structural honesty constraint that the security audit doesn't: **most of the GDPR isn't implemented in code.** A repository can show that a deletion endpoint exists; it can't show that a Data Processing Agreement was actually signed, that the chosen lawful basis is legally valid, or that a consent banner's wording makes consent "freely given." The audit therefore separates two finding classes—code-verifiable (a signal the agent confirms or refutes from the repository) and **legal-review-required** (a signal the agent surfaces for a human or Data Protection Officer to judge)—and never reports a legal conclusion as a confirmed pass or fail.

Readers: agent authors maintaining the auditor; reviewers and Data Protection Officers who consume its report; developers who run a data-protection pass before shipping a feature that touches personal data or before a release.

## Goals

- Provide a whole-repository, GDPR-aligned data-protection audit that correlates personal-data handling across files—the data model against the deletion path, the logging layer against the personal-data it emits, the third-party integrations against the international-transfer surface
- Stay strictly read-only: the audit finds and reports; it never edits source, redacts or moves personal data, suppresses findings, or changes behaviour
- Stay stack-agnostic in methodology (the GDPR articles are fixed) while adapting concrete detection patterns to the project's detected stack (web framework, ORM/data layer, frontend, third-party SDKs, cloud/region config)
- Separate **code-verifiable** findings from **legal-review-required** findings so the audit never overstates legal compliance from a code signal
- Produce a severity-classified, article-attributed report a human can act on, with a file:line attribution per code-verifiable finding
- Draw explicit boundaries to the OWASP security audit (general AppSec), the dependency/CVE audit, and the diff-scoped review, so the agent is invoked only for the whole-repository data-protection audit

## Non-Goals

- General application-security review (authentication, access control, injection, secret handling beyond personal data)—owned by `spec/project/code-security-audit/`. This audit reaches into security only at the GDPR Article 32 intersection (personal-data encryption, pseudonymisation, personal-data-in-logs) and defers the rest
- CVE / dependency / lockfile vulnerability scanning—owned by `spec/project/dependency-audit/`
- Diff-scoped review of the current branch's changes—owned by the `security-review` CLI skill; this audit is whole-repository
- **Rendering a legal compliance verdict.** The audit reports code-verifiable signals and surfaces legal-review-required items; it doesn't certify GDPR compliance, validate the legal sufficiency of a lawful basis, a DPA, a DPIA conclusion, or consent wording, and it's not legal advice
- **Applying fixes or remediation.** The agent is read-only; the fix step belongs to a human or a separate skill, so the audit stays single-responsibility
- Authoring the legal artifacts themselves (the privacy notice text, the Records of Processing Activities, the DPIA)—the audit checks for their presence and for code consistency with them, it doesn't write them
- Running third-party privacy/PII-scanning tooling or DSAR-automation platforms—the agent performs LLM-driven pattern analysis over the repository; external runners stay out of scope

## Requirements

### Read-only contract

- **MUST** be strictly read-only: declare only read and search tools (`Read`, `Grep`, `Glob`), declare no `Edit`, `Write`, `NotebookEdit`, and apply no fixes; the single output is the audit report
- **MUST NOT** redact, move, export, or otherwise touch any personal data it encounters in seed data, fixtures, or logs; it reports the location and class of the exposure, it doesn't act on the data
- **MUST NOT** suppress, downgrade, or annotate findings in the source; reporting is the only action
- **MUST** return the report in its final message; persisting the report is the calling skill's or operator's responsibility. When persisted, the report lives at `.audits/gdpr-audit-process/<target-slug>.md` (subdirectory = this spec's slug) per `spec/claude/review-plan/` §File location and naming; a re-run overwrites the single canonical file rather than accumulating timestamped snapshots

### Discovery and stack adaptation

- **MUST** discover the repository's **personal-data surfaces** rather than hard-coding one project's paths: the data models / schemas / migrations, the request/response DTOs, the logging configuration, the third-party SDK integrations, the cloud/infrastructure region configuration, and the frontend analytics/tag layer; the report **MUST** state which roots and globs it scanned
- **MUST** detect the project's stack (web framework, data-access layer, frontend framework, third-party processors) and adapt concrete detection patterns to it—the methodology (GDPR articles) is fixed, the example patterns are stack-specific
- **MUST** detect what classes of personal data the repository handles—at minimum: direct identifiers (name, email, phone, address, government IDs), online identifiers (IP address, device ID, cookies), and **special categories under Article 9** (health, biometric, genetic, racial/ethnic, political, religious, sexual-orientation, trade-union data)—and treat special-category data as a severity amplifier
- **MUST**, when the project declares a data-protection posture (a privacy notice, a Records of Processing Activities document, a retention policy, a documented lawful basis per processing), audit the code against that declared posture; absent a declared posture, audit against GDPR defaults and state the assumption

### Audit coverage

The audit **MUST** cover the following dimensions, correlating across files rather than per-file. Each finding **MUST** be attributed to the GDPR articles it derives from and classified as code-verifiable or legal-review-required (§Code-verifiable versus legal-review boundary).

- **MUST** audit **lawfulness, consent and transparency** (Art. 5(1)(a), 6, 7, 9, 12–14): presence of a privacy notice artifact or `/privacy` route; consent capture in code where consent is the basis, including the opt-in default rule—pre-ticked boxes, opt-out defaults, or consent assumed without an affirmative action are findings; bundled/forced consent; handling of withdrawal of consent being as easy as giving it; special-category processing carrying an Article 9 condition
- **MUST** audit **data minimisation and purpose limitation** (Art. 5(1)(b)(c), 25): data models and DTOs that collect more personal data than the stated purpose needs; privacy **by default** (the default configuration exposes/processes the minimum); over-broad reads of personal data; free-text or catch-all fields that silently absorb personal data
- **MUST** audit **storage limitation and retention** (Art. 5(1)(e)): presence of a retention/deletion mechanism (TTL, scheduled purge job, retention configuration); the **absence** of any retention or deletion mechanism for a store holding personal data is a finding; backups/exports that escape the retention policy
- **MUST** audit **data-subject-rights implementation** (Art. 12–22) as first-class correlated checks—for each right, whether the codebase implements a path: access/transparency (Art. 15), rectification (Art. 16), **erasure / right to be forgotten** (Art. 17)—including the trap that a soft-delete or de-activation flag that leaves personal data intact doesn't satisfy erasure—restriction (Art. 18), **data portability** in a structured, commonly used, machine-readable format such as JSON or CSV (Art. 20), objection/opt-out (Art. 21), and **automated decision-making / profiling** safeguards including a human-in-the-loop path (Art. 22)
- **MUST** audit **security of processing for personal data** (Art. 32), scoped to personal data and delimited from the general OWASP audit: encryption of personal data in transit (TLS enforced) and at rest (database/field-level encryption of sensitive fields); **pseudonymisation and anonymisation** of personal data where feasible; and—a first-class GDPR-specific check—personal data in logs, error messages, stack traces, analytics events, and crash reports (emails, names, tokens, full IP addresses, special-category data emitted to log sinks)
- **MUST** audit **processors and international transfers** (Art. 28, 44–49): detect third-party services that receive personal data (analytics, error/crash reporting, email, payment, support, cloud/storage) from dependencies and configuration; detect the third-country transfer surface—cloud regions and data-residency configuration (for example a US region for EU personal data) and US-based or other non-adequate-country SaaS receiving personal data; surface the need for a Data Processing Agreement (Art. 28) per detected processor and an Article 46 safeguard (Standard Contractual Clauses, adequacy, transfer impact assessment per Schrems II) per detected transfer as legal-review-required
- **MUST** audit **cookies, trackers and telemetry** against the ePrivacy regime and its German implementation (TDDDG, the successor to the TTDSG): non-essential cookies, trackers, tag managers, or fingerprinting set **before** an affirmative consent signal; analytics or product telemetry that defaults to on without opt-in; a consent banner / consent-management layer being present and gating non-essential storage
- **SHOULD** audit **accountability and impact-assessment signals** (Art. 5(2), 30, 33/34, 35): presence of a Records of Processing Activities artifact (Art. 30); **DPIA triggers** (Art. 35)—large-scale processing of special-category data, systematic monitoring, or automated profiling present in the code without a corresponding Data Protection Impact Assessment artifact; breach-readiness signals (audit trails / access logging that would support an Art. 33/34 notification). Most of this dimension is legal-review-required; the agent surfaces the trigger and the artifact's presence/absence, not a conclusion

### Code-verifiable versus legal-review boundary

- **MUST** classify every finding as exactly one of:
  - **code-verifiable**: the agent confirmed or refuted the signal from the repository (for example: "no erasure path deletes rows from `users`"; "full IP address logged at `api/mw/log.py:42`"; "Google Analytics loaded before consent at `web/index.html:18`"). These carry a file:line attribution
  - **legal-review-required**: the agent detected a signal whose compliance can only be judged by a human or Data Protection Officer (for example: "Stripe receives personal data—confirm a Data Processing Agreement exists"; "personal data stored in a US region—confirm an Article 46 transfer safeguard"; "consent banner present—confirm wording makes consent freely given"). These name the detected signal and the legal question, never a verdict
- **MUST NOT** report a legal-review-required item as a confirmed compliance pass or failure, and **MUST NOT** state or imply that the audit certifies GDPR compliance or constitutes legal advice
- **MUST** state, when the absence of an artifact (RoPA, DPA, DPIA, privacy notice) is reported, that absence-in-repo is a signal and the artifact may exist outside the repository—routing it to legal-review-required rather than asserting non-compliance

### Output

- **MUST** emit a single severity-classified report using the portfolio-wide severity vocabulary from `spec/claude/review-plan/` §Severity scale (Critical / Warning / Suggestion / Info, verbatim Title Case)—it **MUST NOT** invent a parallel scale; each finding carries a title, the GDPR articles, the code-verifiable/legal-review-required class, a file:line attribution for code-verifiable findings, the problem, and a concrete remediation recommendation (described, not applied)
- **MUST** lead with an overall assessment table (per audit dimension: rating + finding count + code-verifiable/legal-review split) and a **data-subject-rights matrix** (right Art. 15–22 × implemented? × file:line / gap)
- **MUST** include a **personal-data inventory** (data class × where collected × where stored × where it leaves the system / which processor / which region) so the data flows the findings reference are visible
- **MUST** state the audit scope (scanned roots, globs, detected stack, detected personal-data classes, declared posture or GDPR-default assumption) so the audit is reproducible
- **SHOULD** distinguish confirmed findings from suspected-but-uncertain ones so the consumer can triage; an uncertain finding is reported, not silently dropped
- **MUST** cite this spec in the agent body or `description`

## Acceptance Criteria

- [ ] The agent declares only `Read`, `Grep`, `Glob` (no write/edit/execution tools), applies no source edits, and never redacts or moves personal data it encounters
- [ ] Running the audit produces a report classified by the `spec/claude/review-plan/` §Severity scale vocabulary (Critical / Warning / Suggestion / Info) whose findings each carry a title, GDPR articles, code-verifiable/legal-review-required class, file:line (for code-verifiable), problem, and a described (not applied) remediation
- [ ] The report leads with a per-dimension assessment table, a data-subject-rights matrix, and a personal-data inventory, and states the scanned roots, globs, detected stack, and detected personal-data classes
- [ ] A store holding personal data with no retention or deletion mechanism is reported (Art. 5(1)(e)); a soft-delete that leaves personal data intact is flagged as not satisfying erasure (Art. 17)
- [ ] Personal data emitted to a log, error message, or analytics event (email, name, token, full IP, special-category data) is reported as Critical with a file:line (Art. 32)
- [ ] A non-essential cookie/tracker/telemetry that fires before an affirmative consent signal is reported (ePrivacy / TDDDG); analytics defaulting to on without opt-in is reported
- [ ] A detected third-party processor and a detected third-country transfer (for example EU personal data in a US region) are each surfaced as legal-review-required, naming the DPA / Article 46 safeguard question without rendering a verdict
- [ ] Special-category (Article 9) data raises the severity of the findings that touch it
- [ ] No finding asserts overall GDPR compliance certification or legal advice; absence-in-repo of a legal artifact is reported as a signal that may exist outside the repository
- [ ] The audit is delimited from `code-security-audit` (general OWASP/AppSec), `dependency-audit` (CVE scope), and `security-review` (diff scope), and the agent's `description` states these negative cases
- [ ] The agent inserts no suppression comment (`# noqa`, `# nosec`, an ESLint-disable directive, or any equivalent) into any source file, and the report is delivered in the agent's final message rather than as a file write or an intermediate turn
- [ ] When the repository declares a data-protection posture, the report names that posture and audits against it; when none is declared, the report states it's auditing against GDPR defaults
- [ ] The report includes findings—or an explicit "no gap detected" statement—for the data minimisation and purpose limitation dimension (Art. 5(1)(b)(c), 25)
- [ ] Legal-review-required findings are structurally distinguishable from code-verifiable findings (by an explicit per-finding class label or a dedicated section) so a Data Protection Officer can enumerate them without reading every finding body
- [ ] When the repository contains a DPIA trigger (large-scale special-category processing, systematic monitoring, or automated profiling), the report includes an accountability-and-DPIA-signals section surfacing the trigger and the relevant artifact's presence/absence (Art. 5(2), 30, 35)
- [ ] The agent body or `description` cites `spec/project/gdpr-audit-process/`

## References

- [R1] Agent authoring rules and read-only tool discipline: `spec/claude/agent-management/`
- [R2] Skill-vs-agent decision rule and rationale-section requirement: `spec/claude/skill-vs-agent/`
- [R3] Whole-codebase security audit (delimited against this spec at the Art. 32 intersection): `spec/project/code-security-audit/`
- [R4] CVE / dependency vulnerability audit (delimited against this spec): `spec/project/dependency-audit/`
- [R5] Review-plan / audit-output persistence and severity vocabulary: `spec/claude/review-plan/`
- [R6] Regulation (EU) 2016/679 (GDPR), full text: <https://gdpr-info.eu/>
- [R7] GDPR Article 5 (principles), Article 25 (data protection by design and by default), Article 30 (records of processing), Article 32 (security of processing), Articles 12–22 (data-subject rights), Articles 44–49 (transfers to third countries)
- [R8] EU GDPR compliance checklist: <https://gdpr.eu/checklist/>
- [R9] German Telecommunications-Digital-Services Data Protection Act (TDDDG, successor to the TTDSG) governing cookies/trackers and telemedia; ePrivacy Directive 2002/58/EC

## Open Questions

- **Companion skill vs agent-only.** This spec defines the read-only `gdpr-data-protection-reviewer` agent. Whether a thin `gdpr-audit` CLI skill should wrap it (to persist the report under `.audits/gdpr-audit-process/` and chain it into release flows, mirroring how `security-review` relates to `code-security-reviewer`) is deferred. Revisit when a release or pre-ship gate needs an operator-invocable entry point; decide per `spec/claude/skill-vs-agent/`.
- **Reciprocal boundary to a future threat-modeling spec.** Article 35 DPIA overlaps an architecture-level threat-modeling concern. Revisit when `spec/project/threat-modeling/` is created or a roadmap item for one is opened; at that moment add a reciprocal delimitation bullet to both specs. Checkable predicate today: `test -d spec/project/threat-modeling` is false.
- **Relationship to a license-check process.** A sibling `license-check-process` is in flight (branch `feat/license-check-process`). If it lands as a compliance-audit family, consider whether GDPR and license audits should share a common report shell. Revisit when that branch merges.
