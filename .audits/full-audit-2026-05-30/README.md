# Full bidirectional spec audit — 2026-05-30

Single entry point for the complete spec-conformance audit of `nolte-shared`. This is the report that gets **worked off afterwards**; it summarises the open points and links to the two detailed audit records that carry every individual finding.

- **Revision audited:** `b91b67b` (`develop` tip at audit time)
- **Working copy:** worktree `full-spec-audit` on branch `chore/full-spec-audit-2026-q2`
- **Status:** open (findings not yet worked off)

## What was audited

Both directions, exhaustively:

1. **Forward — every artefact against every governing spec.** All **69 artefacts** (43 skills + 26 agents) reviewed against `skill-management`, `agent-management`, `skill-vs-agent`, `plugin-scoping`, `resumable-work`, and each artefact's bound domain specs.
2. **Backward — every spec against its implementation.** All **62 spec topics** carrying testable `## Requirements` / `## Acceptance Criteria` reconciled against the repo's implementation surface (`skills/`, `agents/`, `.github/`, `.claude/`, `Taskfile.yml`, `mkdocs.yml`, docs, workflows). 1 285 individual acceptance criteria were scored (806 pass / 226 fail / 3 blocked / 250 not-applicable).

## The three records

| File | Role |
|---|---|
| **this file** | Master entry point + prioritised backlog + how to work it off |
| `.audits/skills-agents-sweep/2026-05-30-full-audit.md` | Forward + cross-cutting record (executive summary, boundary matrix, spec-induced gaps, classification findings, per-cluster triage, wave roadmap, and **Appendix A** with all 69 per-artefact findings) |
| `.audits/spec-drift/2026-Q2.md` | Backward record (spec → implementation), `review-plan` four-section format, per-spec results table + all backward findings — this is the repository's 2026-Q2 `spec-drift-audit` history entry |

## How it was produced (reproducible)

Multi-agent orchestration, two workflow passes:

- **Pass A** (257 agents, ~11.6 M tokens): one reviewer per artefact / per spec on Sonnet, each finding re-checked by an independent **adversarial verifier** that confirmed/refuted and caught missed violations.
- **Dedup**: deterministic collapse of re-reported duplicates (498 → 477 findings).
- **Pass B** (12 agents, Opus): triage of the 8 largest clusters (genuine vs over-escalated), cross-cutting analysis (boundary matrix, spec-induced gaps, classification), wave roadmap, and 3 completeness critics.

### Verification evidence (the audit was checked, multiple times)

| Critic | Verdict | Evidence |
|---|---|---|
| Coverage | **PASS** | 69 forward + 62 backward present; artefact/spec names byte-identical to source tree |
| Format & severity | **PASS** | All 477 findings carry a `[spec_ref]`; severity vocabulary is exactly Critical/Warning/Suggestion/Info; no malformed lines |
| Truthfulness | **PASS** | 12/12 random findings spot-checked against the actual files → **0 hallucinations**. Triage downgrades are severity corrections, not invented findings |

## Headline numbers

- **Raw post-dedup findings: 477** — 197 Critical, 224 Warning, 32 Suggestion, 24 Info.
- **The raw Critical count is inflated by severity over-escalation, not by false claims.** The cited violations are real; many are SHOULD-class or interpretation-dependent and the triage moves them to Warning. Per-cluster genuine-vs-discounted ledger is in the sweep report.

## Prioritised backlog (genuine, load-bearing)

Work these off via the normal `fix/`/`docs/`-PR flow against `develop`. The detailed, per-finding actionable items (with `Where` / `Fix` / `Verify`) live in the two detail records; this is the prioritised summary.

### P1 — Reviewer/agent correctness bugs (these mis-audit or cannot run)

1. **`project-structure-reviewer`** emits a false `Critical` for a missing `tests/` directory — it mis-audits every plugin repo it runs against. *(highest blast radius)*
2. **`spec-readiness-reviewer`** Option B tells it to persist a report to `.audits/`, but it declares no `Write` tool and a Hard rule forbids creating files — the option is unrunnable. Resolve by either granting `Write` or removing the persist instruction.
3. **`diagram-opportunity-reviewer`** exposes cap overrides as inputs against an explicit spec `MUST NOT`, and misquotes §Open Questions to justify it.
4. **`code-security-reviewer`** uses an invented `P0–P3 ↔ critical/high/medium/low` severity scale instead of the mandated Critical/Warning/Suggestion/Info.

### P2 — Spec-MUST structural violations

1. **`webview-ui-expert`** — `Bash` on a read-only agent with no `## Read-only Bash justification` section (runs `git` in-body).
2. **`audience-review`** — `## German trigger phrases` block in the agent body; plugin-distributed bodies MUST be English-only.
3. **`portfolio-inflight-collector` + `portfolio-manifest-collector`** — `tools: [Bash]` but the body claims four tools are declared; align body to the enforced `tools` list (or widen the list if the agent genuinely needs them).
4. **Rationale-heading deviations** (`## Rationale (...)` → `## Why this is a/an …`): `audience-doc-author`, `claude-plugin-developer`, `cookiecutter-template-author`, `webview-ui-optimize`.
5. **Operations-vocabulary — genuine subset only:** `mission-revise` (forbidden `### A./B./C.`), and non-vocab *named* operations in `audience-identify` (`validate`/`revisit`), `roadmap-plan`, `sprint-execute`, `sprint-review`, `spec`, `docs-dry-refactor`, `mermaid-diagrams-apply`, plus partials in `cookiecutter-template-manage`/`lektorat-apply`/`portfolio-audit`/`webview-ui-optimize`/`yaml-json-schema`/`skill-agent-catalog-apply`/`github-issue-templates-apply`.

### P2 — Backward (spec → implementation) genuine gaps

1. **`portfolio-management`** — `.audits/portfolio/` does not exist (spec MUST for the portfolio audit artefact location).
2. **`branching-model`** (Info→track) — `.github/settings.yml` pins gh-plumbing `@v1.1.15` while the four release workflows pin `@v1.1.19` (four minor versions behind).
3. Other genuine spec→impl gaps validated in the backward record: `dependency-audit`, `research-triangulate`, `spec-drift-audit`, `review-plan`, `skill-review`, `docs-audience-tracks`, `mkdocs-structure`, `release-automation`, `continuous-improvement` (see `.audits/spec-drift/2026-Q2.md` §Findings).

### P3 — Cross-cutting hygiene (SHOULD-class)

1. **Boundary delimitation gaps** (one-directional `dont_use_when`): `portfolio-audit` ↔ `portfolio-inflight-triage`; `lektorat-apply` ↔ `prose-vale-curator`; **`continuous-improvement-triage` ships no `dont_use_when` at all** despite being a four-way confusable hub.
2. **Missing `examples/` evaluation scenarios** across several non-trivial skills (SHOULD).
3. **`tools/gemini-image-generation`** — the only genuine spec-induced gap: the spec promises an in-repo `gemini-image-generate` binding that doesn't exist yet. Either build it or mark the spec as deferred/consumer-facing.

### Spec-quality finding (feeds back into the specs themselves)

1. **`skill-management` §Operations vocabulary is ambiguous** about whether the closed-verb rule binds the sequential *procedure steps* of a single-operation skill (e.g. `### 1. Detect project kind`). This ambiguity caused ~8 over-escalated Criticals. Clarify the spec: either scope the rule explicitly to multi-operation dispatch blocks, or mandate a different heading style for procedure runbooks.

## How to work this off

1. Pick a wave from the sweep report's **§Wave-based implementation roadmap** (Wave 1 = systemic structural fixes that retire many findings at once; Wave 2 = remaining MUST fixes; Wave 3 = SHOULD/polish).
2. Land fixes as standard `fix/` / `docs/` PRs against `develop` (per `branching-model` / `pull-request-workflow`). For per-artefact work, the sweep report's Appendix A entries are already in actionable `Where`/`Fix`/`Verify` shape.
3. **Every backward `Critical` (`fail`) needs a documented decision** — adjust implementation, adjust spec, or open question — per `spec-drift-audit` §Feedback loop. Record the decision in `.audits/spec-drift/2026-Q2.md` §Processing log.
4. The `spec-drift/2026-Q2.md` record is the permanent quarterly history entry (keep it). The sweep report is disposable once worked off, per `review-plan`/`skills-agents-sweep` lifecycle.

## Caveats (read before acting)

- **Raw vs triaged.** The detail records carry the full **477 raw post-dedup** findings for completeness and traceability. Only the 8 largest clusters were individually severity-triaged; the long-tail per-artefact findings are real (0% hallucination in spot-checks) but not all re-severity-judged — treat a long-tail `Critical` as "real violation, confirm severity before escalating".
- **Per-artefact plans were consolidated** into Appendix A rather than emitted as 69 separate `.audits/skill-review|agent-review/*.md` plans, to honour the single-report request. Any artefact can be split back into its own review plan when picked up.
