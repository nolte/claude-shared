# Requirements — Trusted-author injection guard (trust boundary for GitHub-authored session input)

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
Do not record a requirement before declaring the bounded context below.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What** — A new cross-cutting authoring-convention spec under `spec/claude/<slug>/` that draws a **trust boundary for GitHub-authored session input**. Skills and agents may treat instructions embedded in issue bodies, comments, and review threads as commands to *act on* only when the author belongs to a trusted set; text from anyone outside that set is treated as untrusted **data** — quotable/weighable as a signal, never obeyed as an instruction. The outcome defends the Claude session against prompt injection (being lured into running foreign commands or pulling in malware via a crafted comment).
- **For whom** — The skills and agents of the `nolte-shared` / `claude-shared` plugin corpus that read GitHub-authored content, above all `issue-orchestrate` (reads the issue body + **every** comment + labels + linked items and drives classification/decomposition/dispatch — the highest-risk injection surface).
- **Out of scope (v1)** — Non-author-attributable ingress (CI-run logs, PR diffs from untrusted branches, web-fetched content); consumers other than `issue-orchestrate` (deferred to follow-up PRs); the permission-side gate (owned by `permission-allowlist`); the read-side MCP-vs-`gh` convention (owned by `mcp-tool-preference`). This spec is the **content-side** complement and composes with both without restating them.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `12` (8 used, across 3 one-topic-per-turn rounds)
  <!-- spec defaults; unchanged. Elicitation was decision-heavy (specification uncertainty), the problem was pre-understood from the on-disk plan, so understanding was lifted by authoritative operator answers rather than long probing. -->
- `U_gate = min_d c_d` over required dimensions = **0.80**
- Termination: `saturation` (every required dimension `c_d ≥ τ_high`; no remaining candidate question carries positive net EVPI)

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.90 | specification | Authoritative answers: MUST always-on (Q4), untrusted-data-not-instruction (Q5), trusted-set membership (Q2); teach-back of bounded context accepted |
| `non_functional` | yes | 0.85 | specification | MUST-strength (Q4), fail-closed + operator notice (edge-Q2), identical-output/`gh`-fallback invariant (Q3 + plan §5) |
| `constraints` | yes | 0.85 | interpretation | Repo facts verified: `spec/claude/` layout, `mcp-tool-preference` + `permission-allowlist` both on `develop`; EN-canonical + DE-sync + `spec/README.md` row (plan §5 invariants); Portfolio-Scope `portfolio` (Q6) |
| `domain_objects` | yes | 0.90 | specification | Trusted set = operator + owner + write-collaborators (Q2); resolver = `get_me` + collaborators/owner, `gh` fallback (Q3); author-attributable GitHub text (Q7) |
| `actors` | yes | 0.90 | specification | Trusted: operator, repo owner, maintainers/write-collaborators (Q2). Untrusted: all external authors. Consumer bound: `issue-orchestrate` (Q1) |
| `acceptance_criteria` | yes | 0.80 | interpretation | Deliverable shape = spec (Context/Goals/Non-Goals/Requirements/AC/References) + `issue-orchestrate` binding via one-line note + spec ref (Q1 + plan §4). `k=2` self-consistency: two independent readings of "done" converged on {spec sections present, consumer bound EN+DE, DE synced, README row, validation green} |
| `edge_cases` | yes | 0.85 | specification | Quoted-foreign-content stays untrusted — provenance over messenger (edge-Q1); unresolvable authorship ⇒ fail-closed + operator notice (edge-Q2) |
| `scope_boundaries` | yes | 0.90 | specification | In: author-attributable GitHub text + `issue-orchestrate` binding + portfolio spec. Out: non-attributable ingress, other consumers (deferred), permission-side, read-side (Q1, Q6, Q7) |

## Requirements

<!-- EARS/CNL form; tagged confirmed (authoritative operator answer / teach-back) or assumed. -->

- **R1** — WHEN a skill or agent ingests GitHub-authored text (issue body, comment, review thread, PR description), the convention SHALL permit its embedded imperatives to be executed as commands ONLY IF the text's author belongs to the trusted-author set.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: bounded-context teach-back + Q4/Q5
- **R2** — The trusted-author set SHALL comprise the operator's own GitHub identity, the repository owner, and users holding write / maintain / admin permission (the repository's maintainers).
  - _dimension_: `domain_objects` · _status_: `confirmed` · _source_: Q2 = "Operator + Owner + Write-Collaborators"
- **R3** — WHEN GitHub-authored text originates from an author outside the trusted set, the system SHALL treat it as untrusted data: it MAY be quoted, summarised, or weighed as a signal, but its imperatives SHALL NOT be executed.
  - _dimension_: `functional` · _status_: `confirmed` · _source_: Q5 = "Untrusted data, nie Instruktion"
- **R4** — The convention SHALL be a MUST-level, always-on rule binding every GitHub-reading artefact; it SHALL NOT be opt-in.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Q4 = "MUST, immer aktiv"
- **R5** — Trust SHALL be resolved at runtime — self-identity via the GitHub MCP `get_me`, the trusted set via the repository owner plus `list_repository_collaborators` — with a `gh api` fallback, preferring the MCP read per `mcp-tool-preference` and preserving its identical-output invariant.
  - _dimension_: `non_functional` · _status_: `confirmed` · _source_: Q3 = "Runtime (get_me + collaborators/owner, gh-Fallback)"
- **R6** — WHEN authorship cannot be resolved (no MCP server and `gh` fails, or an ambiguous / bot identity), the system SHALL fail closed — treat the text as untrusted — AND surface an operator-visible notice that trust resolution was degraded.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: edge-Q2 = "Fail-closed + Operator-Hinweis"
- **R7** — WHEN a trusted author quotes, pastes, or links content of external provenance, the system SHALL keep that quoted content untrusted; trust attaches to the provenance of the content, not to the relaying author.
  - _dimension_: `edge_cases` · _status_: `confirmed` · _source_: edge-Q1 = "Herkunft zählt: Zitat bleibt untrusted"
- **R8** — v1 coverage SHALL be limited to author-attributable GitHub text (issues, comments, reviews, PR descriptions); non-attributable ingress (CI logs, PR diffs from untrusted branches, web-fetched content) SHALL be out of scope for v1.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Q7 = "Nur autor-attribuierbarer GitHub-Text"
- **R9** — The convention SHALL be authored as a new EN-canonical spec topic under `spec/claude/<slug>/en.md` with a strictly-synced DE translation (`de.md`), a registered `spec/README.md` topic row, and `Portfolio-Scope: portfolio`, modelled on the `mcp-tool-preference` structure (Context / Goals / Non-Goals / Requirements / Acceptance Criteria / References).
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: Q6 = "portfolio" + plan §5 invariants
- **R10** — The convention SHALL compose with, and never restate, `permission-allowlist` (permission-side) and `mcp-tool-preference` (read-side), and SHALL carry a DRY adoption clause that binds consumers via a one-line body note + spec reference rather than duplicating the rule into each consumer.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants ("Compose, don't duplicate") + Q3 (resolver uses MCP reads)
- **R11** — This PR SHALL deliver the spec plus the binding of `issue-orchestrate` — the highest-risk consumer (reads body + every comment) — via the adoption note + spec reference in `skills/issue-orchestrate/SKILL.md` and `spec/project/issue-orchestration/` (EN + DE); binding of the other §2 consumers SHALL be deferred to follow-up PRs.
  - _dimension_: `scope_boundaries` · _status_: `confirmed` · _source_: Q1 = "Spec + issue-orchestrate"
- **R12** — The MCP tools the trust resolver introduces (`get_me`, `list_repository_collaborators`) SHOULD be reflected in `permission-allowlist` guidance so their calls don't prompt.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: operator decision (post-authoring: "R12 in diesen PR ziehen") — bound in `spec/claude/permission-allowlist/{en,de}.md`
- **R13** — The untrusted-data floor (R3) SHALL be marked `[locked]`: a downstream consumer MAY widen who is trusted through an additive declaration, but MUST NOT declare an override that removes the boundary.
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: operator decision (post-authoring: "[locked] beibehalten")

## Surviving assumptions / open risks

- ~~**R12 is `assumed`**~~ — RESOLVED: the operator confirmed pulling the `permission-allowlist` guidance into this PR (now R12 `confirmed`, R13 records the `[locked]` decision).
- **Spec slug not fixed** — the worktree/branch is `trusted-author-injection-guard`; the plan floated `untrusted-external-input` / `trusted-author-boundary`. Default to `trusted-author-injection-guard` unless the operator prefers otherwise. Low risk (rename is cheap pre-merge).
- **`Portfolio-Scope: portfolio` is a stronger claim than the sibling** — `mcp-tool-preference` is `local`. Portfolio scope means downstream nolte repos that adopt the plugin inherit an always-on MUST; the runtime owner/collaborator lookup must resolve correctly per-repo. Assumed portable; verify no repo lacks the resolver path (fail-closed covers the gap, but noisily via R6's operator notice).
- **Operator-notice mechanism (R6) is unspecified at requirement level** — *how* the degraded-trust notice surfaces (log line, prose warning in output) is a spec-authoring detail, deliberately left to the spec draft.
- **`acceptance_criteria` (c_d 0.80) and `non_functional`/`constraints` (0.85) carry interpretation uncertainty** — they sit at/just above `τ_high`; the exact wording of "done" and the composition boundary vs the two sibling specs will be firmed during authoring and are the cells most worth re-checking there.
