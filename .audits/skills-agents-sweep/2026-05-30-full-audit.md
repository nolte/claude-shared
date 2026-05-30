---
audit-type: skills-agents-sweep
target: nolte/claude-shared (43 skills, 26 agents)
scope: forward (artefact -> spec) for all 69 artefacts; cross-cutting dimensions inventory-wide. Backward (spec -> implementation) is the companion record at .audits/spec-drift/2026-Q2.md
repo-revision: b91b67b4578779f9a5784f2e7b4e8d8ccc9ce838
created: 2026-05-30
status: open
per-artefact-plans: 0 (consolidated — 69 per-artefact reviews were run in-workflow and inlined into Appendix A rather than persisted as individual .audits/skill-review/*.md and .audits/agent-review/*.md plans; this is a deliberate operator choice recorded for transparency, see Processing log)
method: multi-agent fan-out (Sonnet review + adversarial Sonnet verify per artefact), deterministic dedup, Opus cluster-triage + cross-cutting synthesis, 3 completeness critics
---

# Skills & Agents Sweep — full audit (2026-05-30)

## Executive summary

This is the **forward + cross-cutting** half of a full bidirectional spec audit of `nolte-shared` at revision `b91b67b`. Every one of the **69 artefacts** (43 skills, 26 agents) was reviewed against its governing specs (`skill-management`, `agent-management`, `skill-vs-agent`, `plugin-scoping`, plus each artefact's bound domain specs); every finding was independently re-verified by an adversarial pass. The **backward** half (every spec vs its implementation) is the companion record at `.audits/spec-drift/2026-Q2.md`. The single worked-off entry point is `.audits/full-audit-2026-05-30/README.md`.

### Headline numbers

- **Raw post-dedup findings (whole audit): 477** — 197 Critical, 224 Warning, 32 Suggestion, 24 Info.
  - Forward (this report): **257** (131C / 93W / 22S / 11I).
  - Backward (spec-drift record): **220** (66C / 131W / 10S / 13I).
- **The raw Critical count is inflated.** Adversarial dedup already removed re-reported duplicates (498 → 477). The Opus triage of the 8 largest clusters then found that a large share of the remaining Criticals are *severity over-escalations*, not false claims: the cited violations are real (truthfulness critic: **12/12 spot-checks confirmed, 0 hallucinations**), but many are SHOULD-class or interpretation-dependent and belong at Warning.

### Top findings (triaged, genuine, load-bearing)

| # | Finding | Severity | Where |
|---|---|---|---|
| 1 | `spec-readiness-reviewer` Option B instructs persisting a report to `.audits/`, but the agent declares no `Write` tool and a Hard rule forbids creating any file — irreconcilable | Critical | agents/spec-readiness-reviewer.md (Option B vs Hard rules) |
| 2 | `project-structure-reviewer` emits a **false Critical** for a missing `tests/` dir on every plugin repo — a reviewer bug that mis-audits all consumers | Critical | agents/project-structure-reviewer.md |
| 3 | `diagram-opportunity-reviewer` exposes cap overrides as inputs, violating the spec's explicit `MUST NOT`, and misquotes §Open Questions to justify it | Critical | agents/diagram-opportunity-reviewer.md |
| 4 | `code-security-reviewer` ships an invented `P0/P1/P2/P3 ↔ critical/high/medium/low` severity scale instead of the mandated Critical/Warning/Suggestion/Info | Critical | agents/code-security-reviewer.md step 3 |
| 5 | `webview-ui-expert` declares `Bash` on a read-only agent with **no** `## Read-only Bash justification` section (and runs `git` in-body) | Critical | agents/webview-ui-expert.md |
| 6 | `audience-review` carries a `## German trigger phrases` block in the agent body; plugin-distributed agent bodies MUST be English-only | Critical | agents/audience-review.md:34 |
| 7 | `portfolio-inflight-collector` & `portfolio-manifest-collector` declare `tools: [Bash]` but the body claims four tools are declared — runtime scope ≠ body claim | Critical ×2 | agents/portfolio-*-collector.md |
| 8 | 4 rationale-heading deviations (`## Rationale (...)` instead of the mandated `## Why this is a/an ...`): audience-doc-author, claude-plugin-developer, cookiecutter-template-author, webview-ui-optimize | Critical | skill-vs-agent §Rationale heading |
| 9 | Genuine operations-vocabulary violations: `mission-revise` uses forbidden `### A./B./C.`; `audience-identify` (`validate`/`revisit`), `roadmap-plan`, `sprint-execute`, `sprint-review`, `spec`, `docs-dry-refactor`, `mermaid-diagrams-apply` use non-vocab *named* operations | Critical | skill-management §Operations vocabulary |
| 10 | `tools/gemini-image-generation` spec promises an in-repo binding (`gemini-image-generate`) that does not exist — the only genuine spec-induced gap | Warning | spec/tools/gemini-image-generation |

### What is NOT a problem (verified)

- **No skill↔agent misclassification exists** in either direction — the highest-value structural question came back clean.
- **The entire `description-third-person` cluster (11 raw findings) is over-strict** — the `"Don't use … (use X)"` disambiguation phrasing is an accepted, widespread convention; 0 genuine after triage.
- **18 of ~19 spec-induced "gaps" are false** — phantom paths are illustrative examples in skill docs; the 7 zero-finding specs are legitimately consumer-facing/axiomatic.
- Two artefacts are fully clean: `portfolio-inflight-triage` (skill), `feature-consistency-reviewer` (agent).

### Per-cluster triage ledger

| Cluster | Raw | Genuine | False-positive / over-escalated | Reclassified |
|---|--:|--:|--:|--:|
| Operations-vocabulary | ~35 | 18 | 8 | 17 |
| Description third-person / frontmatter | ~17 | 0 | 11 | 6 |
| Progressive-disclosure / evaluation / authoring-quality | ~28 | 11 | 1 | 4 |
| Skill-vs-agent classification / agent-management | ~35 | 12 | 4 | 1 |
| Catalog metadata (phase / use_when / tags) | ~13 | 3 | 5 | 4 |
| Boundary / adoption-friction (cross-cutting) | ~6 | 3 | 2 | 1 |
| Spec-induced gaps (cross-cutting) | ~19 | 1 | 18 | 2 |
| Backward big clusters (spec→impl) | ~80 | 11 | 4 | 6 |

## Artefact inventory

| Artefact | Kind | C | W | S | I |
|---|---|--:|--:|--:|--:|
| `audience-doc-author` | agent | 1 | 0 | 1 | 0 |
| `audience-review` | agent | 2 | 1 | 0 | 0 |
| `claude-plugin-developer` | agent | 1 | 1 | 0 | 1 |
| `code-security-reviewer` | agent | 1 | 1 | 1 | 0 |
| `cookiecutter-template-author` | agent | 1 | 0 | 0 | 0 |
| `dependency-audit-scanner` | agent | 0 | 4 | 0 | 0 |
| `diagram-opportunity-reviewer` | agent | 3 | 1 | 0 | 0 |
| `docs-freshness-checker` | agent | 3 | 1 | 0 | 0 |
| `feature-consistency-reviewer` | agent | 0 | 0 | 0 | 0 |
| `graphic-prompt-generator` | agent | 2 | 2 | 0 | 0 |
| `i18n-completeness-checker` | agent | 0 | 3 | 1 | 1 |
| `lektorat-scanner` | agent | 0 | 0 | 1 | 0 |
| `mermaid-diagram-reviewer` | agent | 0 | 3 | 0 | 1 |
| `png-to-transparent-svg` | agent | 0 | 1 | 3 | 0 |
| `portfolio-inflight-collector` | agent | 1 | 1 | 2 | 0 |
| `portfolio-manifest-collector` | agent | 0 | 1 | 0 | 0 |
| `project-structure-reviewer` | agent | 1 | 5 | 0 | 0 |
| `prose-vale-curator` | agent | 0 | 1 | 1 | 0 |
| `quality-gate-enforcer` | agent | 2 | 3 | 0 | 0 |
| `roadmap-coherence-reviewer` | agent | 2 | 2 | 1 | 1 |
| `spec-readiness-reviewer` | agent | 2 | 2 | 1 | 0 |
| `sprint-readiness-reviewer` | agent | 2 | 2 | 0 | 1 |
| `tech-stack-drift-reviewer` | agent | 0 | 2 | 0 | 0 |
| `test-case-extractor` | agent | 3 | 1 | 0 | 0 |
| `vocab-drift-scanner` | agent | 0 | 1 | 0 | 0 |
| `webview-ui-expert` | agent | 1 | 2 | 0 | 0 |
| `agent-review` | skill | 0 | 3 | 0 | 0 |
| `audience-identify` | skill | 2 | 1 | 0 | 0 |
| `blog-author` | skill | 0 | 1 | 1 | 0 |
| `blog-author-trigger` | skill | 1 | 3 | 1 | 0 |
| `continuous-improvement-triage` | skill | 1 | 3 | 0 | 1 |
| `cookiecutter-template-manage` | skill | 2 | 0 | 0 | 0 |
| `dependency-audit` | skill | 6 | 2 | 0 | 0 |
| `docs-audience-tracks-apply` | skill | 2 | 2 | 0 | 0 |
| `docs-dry-refactor` | skill | 2 | 2 | 0 | 0 |
| `feature-decompose` | skill | 3 | 1 | 1 | 0 |
| `github-issue-templates-apply` | skill | 4 | 0 | 0 | 0 |
| `lektorat-apply` | skill | 2 | 0 | 1 | 0 |
| `mermaid-diagrams-apply` | skill | 4 | 1 | 1 | 2 |
| `mission-define` | skill | 4 | 0 | 0 | 0 |
| `mission-revise` | skill | 2 | 0 | 0 | 0 |
| `mkdocs-structure-apply` | skill | 1 | 2 | 1 | 0 |
| `permission-allowlist-maintain` | skill | 1 | 1 | 0 | 0 |
| `portfolio-audit` | skill | 3 | 1 | 0 | 0 |
| `portfolio-inflight-triage` | skill | 0 | 0 | 0 | 0 |
| `project-structure-apply` | skill | 1 | 0 | 0 | 0 |
| `pull-request-create` | skill | 4 | 1 | 0 | 0 |
| `pull-request-merge` | skill | 4 | 1 | 0 | 0 |
| `quality-gate` | skill | 2 | 1 | 0 | 0 |
| `readme-structure-apply` | skill | 0 | 3 | 1 | 1 |
| `release-notes-curate` | skill | 4 | 2 | 1 | 0 |
| `release-publish-trigger` | skill | 5 | 1 | 0 | 0 |
| `roadmap-init` | skill | 2 | 0 | 0 | 0 |
| `roadmap-plan` | skill | 1 | 4 | 0 | 0 |
| `roadmap-refine` | skill | 3 | 1 | 0 | 0 |
| `skill-agent-catalog-apply` | skill | 4 | 0 | 0 | 0 |
| `skill-management` | skill | 4 | 1 | 0 | 0 |
| `skill-review` | skill | 3 | 0 | 0 | 0 |
| `skills-agents-sweep` | skill | 1 | 2 | 0 | 0 |
| `spec` | skill | 4 | 1 | 0 | 0 |
| `spec-drift-audit` | skill | 4 | 3 | 0 | 0 |
| `sprint-execute` | skill | 2 | 1 | 0 | 1 |
| `sprint-plan` | skill | 2 | 2 | 0 | 1 |
| `sprint-review` | skill | 4 | 0 | 0 | 0 |
| `tech-stack-capture` | skill | 2 | 1 | 0 | 0 |
| `vocab-drift-audit` | skill | 2 | 0 | 1 | 0 |
| `webview-ui-optimize` | skill | 2 | 3 | 0 | 0 |
| `workflow-health-triage` | skill | 2 | 0 | 0 | 0 |
| `yaml-json-schema` | skill | 1 | 1 | 1 | 0 |

## Boundary matrix

### Cross-cutting: Skill/Agent boundary matrix (overlapping or confusable scope)

Scope note: this section reports only the inventory-wide view — pairs of artefacts whose `description`/`dont_use_when`/`see_also` could route an operator or Claude to the wrong artefact. Per-artefact conformance findings (operations-vocabulary, third-person, TOC, etc.) are out of scope here and are covered by the per-artefact sections. Severity vocabulary is Critical/Warning/Suggestion/Info per `spec/claude/review-plan/`. The governing SHOULD for boundary delimitation is `spec/claude/skill-management/` §Use-case metadata (and the agent twin in `spec/claude/agent-management/`): authors SHOULD declare `dont_use_when`/`see_also` whenever overlap with another artefact is likely, with a resolvable `alternative`, so the catalog can render the disambiguation and cross-link both directions.

I spot-verified every cited frontmatter against the actual files under `skills/` and `agents/`.

#### Boundary matrix

| Pair | Overlap surface | Boundary crisp in BOTH? | Verdict |
|---|---|---|---|
| `skill-review` vs `agent-review` | "review this thing for spec compliance" | Yes — symmetric mutual `dont_use_when` (skill↔agent) | Clean |
| `skill-review`/`agent-review` vs built-in `review` | the bare verb "review" | Yes — both name "pull-request-level review (`review` skill)" in description | Clean |
| `skill-review`/`agent-review` vs `skills-agents-sweep` | "audit skills/agents" | Yes — sweep's `dont_use_when` names per-artefact review; both review skills are single-target by description | Clean |
| `portfolio-audit` vs `portfolio-inflight-triage` | both `tags:[audit]`, both "across nolte/*" | **No — asymmetric** (see Finding CC-1) | Warning |
| `lektorat-apply` vs `prose-vale-curator` | both edit/review prose | **No — asymmetric** (see Finding CC-2) | Warning |
| `continuous-improvement-triage` vs `portfolio-audit` / `spec-drift-audit` / `skills-agents-sweep` / `workflow-health-triage` | "triage/audit findings, dispatch remediation" | **No — CIT ships zero `dont_use_when`** (see Finding CC-3) | Warning |
| docs-* family (`mkdocs-structure-apply`, `docs-audience-tracks-apply`, `docs-dry-refactor`, `skill-agent-catalog-apply`) | all scaffold/patch MkDocs `docs/` | Yes — dense, mutually-resolving `dont_use_when` web; each names the others | Clean |
| `dependency-audit` vs `quality-gate` | "run checks before PR/release" | Yes — mutual `dont_use_when` (CVE-scan vs lint/typecheck/test), each names the other | Clean |
| `spec-drift-audit` vs `spec-readiness-reviewer` vs `spec` skill | "spec" + "audit/review" | Yes — three-way mutual disambiguation present in all three descriptions | Clean |
| `audience-review` (agent) vs `audience-identify` (skill) | "audience artefact" | Yes — both descriptions disambiguate create-vs-review | Clean |
| `feature-consistency-reviewer` vs `spec-drift-audit` | "drift on features" | Yes — FCR scopes to *draft/new* features + names `spec-drift-audit` for existing; clean | Clean |

#### Genuine findings

**CC-1 — [Warning] [skill-management.use-case-metadata] `portfolio-audit` ↔ `portfolio-inflight-triage` boundary is one-directional.**
`skills/portfolio-inflight-triage/SKILL.md` correctly carries a `dont_use_when` entry redirecting capability-allocation requests to `portfolio-audit`. But `skills/portfolio-audit/SKILL.md` (frontmatter, lines ~61, 70–75) names *only* `tech-stack-capture` in `dont_use_when`/`see_also` and never mentions `portfolio-inflight-triage`. Both skills share `tags:[audit]` and both advertise "audit … across `nolte/*`", so an operator who types "audit the portfolio" (portfolio-audit's literal trigger) when they actually mean stalled-PR/in-flight triage gets no redirect from the artefact they land on. The overlap is real and the SHOULD asks for it to be declared on both sides; the missing reverse link also means the catalog's cross-link and "Don't use when" section render only one direction.

**CC-2 — [Warning] [agent-management.use-case-metadata] `lektorat-apply` ↔ `prose-vale-curator` boundary is asymmetric and the discriminator is thin.**
`skills/lektorat-apply/SKILL.md` cleanly redirects Vale-rule work to `prose-vale-curator` via `dont_use_when`. The reverse is weaker: `agents/prose-vale-curator.md` lists `lektorat-apply` only in `see_also`, never in `dont_use_when`. Its `dont_use_when` discriminates against `audience-doc-author` (net-new docs) and `vocab-drift-audit` (vocab retirement) but is silent on the lektorat boundary — yet both artefacts operate on *existing* Markdown prose and edit it. The operative discriminator (lektorat = five-dimension editorial review incl. audience-fit/readability; prose-vale-curator = mechanical "make Vale green") is recoverable from each description's first sentence, but only one side encodes it as a routing rule. A user asking to "fix the writing in README.md" sits squarely on the seam with no structured redirect from the curator side.

**CC-3 — [Warning] [skill-management.use-case-metadata] `continuous-improvement-triage` ships no `dont_use_when` despite being the single most overlap-prone skill in the inventory.**
Spot-verified: `skills/continuous-improvement-triage/SKILL.md` frontmatter has `use_when` and `see_also`-less metadata — **no `dont_use_when` field at all** (file lines 236–247). Its description ("triaging portfolio audit findings, classifying them … dispatching … remediation") collides head-on with `portfolio-audit` (produces those findings), `skills-agents-sweep` (produces cross-cutting findings + a remediation roadmap), `spec-drift-audit`, and `workflow-health-triage` (also a "triage … dispatch to specialist agent" skill). Triggers like "triage findings" / "dispatch findings to specialised agents" are generic enough to capture requests meant for any of those four. The SHOULD explicitly fires "whenever overlap with other artefacts is likely," and here it is maximally likely. (The per-artefact section flags the same field-absence under `skill-management.use-case-metadata`; surfaced here additionally because only the inventory-wide view shows it is a *four-way* confusable hub, not an isolated omission.)

#### Adoption-friction note (Info)

**CC-4 — [Info] [skill-management.frontmatter-validation] Two high-traffic skills lack the user's most natural phrasing in their trigger surface.**
- `continuous-improvement-triage`: an operator's natural phrasing after an audit is "fix these findings" / "remediate the audit findings" / "behebe die Findings"; the description only offers "triage … findings", "classify … opportunity", "dispatch findings". The remediation-intent verb a user would actually type is absent, so the skill is hard to trigger by natural request even though it is the correct dispatcher. (Not a spec violation — descriptions need not enumerate every phrasing — hence Info.)
- `quality-gate` vs `dependency-audit`: "run all checks before committing" is claimed by `quality-gate`, but a user who says "run a security check before I commit" may be routed to either; the seam is handled (quality-gate's description explicitly carves out "even when `task lint` wraps a security check"), so this is well-managed and noted only for completeness.

#### False positives / reclassified

- **`docs-*` family "overlapping scope"** — NOT a finding. I verified the four docs skills carry a dense, mutually-resolving `dont_use_when`/`see_also` web (`mkdocs-structure-apply` ↔ `docs-audience-tracks-apply` ↔ `docs-dry-refactor` ↔ `skill-agent-catalog-apply`), each naming the others with resolvable alternatives. The prompt named this family as a candidate, but the boundaries are crisply delimited on both sides. False positive for the boundary lens.
- **`skill-review` vs `agent-review` vs `review`** — named by the prompt as a candidate confusable triple; verified clean. Symmetric mutual `dont_use_when` between the two plugin skills, and both name the built-in `review` skill for the PR-level case. No finding.
- **`mkdocs-structure-apply` missing `docs-freshness-checker` in `dont_use_when`/`see_also`** — this *is* a real metadata gap, but it is a per-artefact catalog-cross-link omission already captured twice in the `mkdocs-structure-apply` per-artefact section (two Warnings). Not re-reported here; it is not a *boundary-confusion* risk (drift-detection vs skeleton-scaffolding are not plausibly confusable by an operator), so escalating it under this cross-cutting lens would be double-counting. Reclassified out.

COUNTS: genuine=3 false_positive=2 reclassified=1

## Spec-induced gap inventory

### Cross-Cutting: Spec-Induced Gaps (phantom artefacts, consumer-facing confirmation, missing bindings)

**Method.** I extracted every `spec/<topic>/<slug>/` path referenced from `skills/` and `agents/` bodies, diffed against the 62 actual spec topic directories, and spot-verified each candidate gap by reading the cited spec's own `## Context` / `Implementation:` header (which in this corpus reliably self-declares whether a binding is expected in-repo, downstream, or absent by design).

#### 1. Phantom-artefact table (spec paths referenced but with no matching spec directory)

The raw fan-out flagged several referenced `spec/<topic>/` paths that don't resolve to a real directory. **All are illustrative examples inside skill documentation, not real artefact demands** — every one is a false positive.

| Referenced path | Where | Verdict |
|---|---|---|
| `spec/api/rate-limiting`, `spec/api/authentication` | `skills/spec/examples/01–03*.md` | FALSE POSITIVE — worked examples teaching the `spec` skill; explicitly hypothetical ("Lege bitte eine neue Spec an unter `spec/api/rate-limiting/`") |
| `spec/project/foo`, `spec/project/bar` | `skills/spec/SKILL.md:24–27`; `agents/spec-readiness-reviewer.md:192,264` | FALSE POSITIVE — placeholder prompts and a ghost-reference-check illustration ("`spec/project/foo/` missing → `Critical`") |
| `spec/project/release-config` | `skills/yaml-json-schema/examples/02,03*.md` | FALSE POSITIVE — sample `description:` strings inside YAML schema examples |
| `spec/templates/spec`, `spec/skill/agent` | `skills/spec/SKILL.md`; `workflow-health-triage` prose | FALSE POSITIVE — `templates/spec.template.md` is a real skill-local template path, not a spec dir; `spec/skill/agent` is the substring of the prose phrase "markdown spec/skill/agent file" |

No genuine phantom artefact (a spec-demanded binding cited by path that does not exist) was found.

#### 2. Consumer-facing confirmation (the 7 zero-finding specs)

Each spec's own header was read to confirm intent. **All 7 are legitimately consumer-facing or have an in-repo binding under a differently-spelled slug — none is a silent in-repo gap.**

| Spec | Verdict | Evidence (spec_ref) |
|---|---|---|
| `ansible/playbook-development` | CONFIRMED consumer-facing | Header: `Implementation: documentary-only—Ansible automation lives outside the nolte-shared plugin scope … no Claude Code skill or agent in this plugin operationalises it.` |
| `ansible/role-development` | CONFIRMED consumer-facing | Header: identical `documentary-only` self-declaration; consumed by reference via `ansible-galaxy`/Molecule downstream |
| `design/corporate-design-colors` | CONFIRMED consumer-facing + partial in-repo consumer | `## Context` names "skill and agent authors who generate token bundles, Mermaid themes, README badges, or AI hero images" as readers; it is a token-contract spec consumed by `agents/graphic-prompt-generator.md` (which cites `spec/design/corporate-design-colors/`), not operationalised by a dedicated skill |
| `frontend/webview-ui-optimization` | CONFIRMED — binding EXISTS (refs=2) | Spec §Goals names "the `webview-ui-optimize` skill / `webview-ui-expert` agent that consume them"; both ship (`skills/webview-ui-optimize/`, `agents/webview-ui-expert.md`). Zero-finding because the slug differs from the spec slug, not because it is unbound |
| `project/post-audience-communication` | CONFIRMED consumer-facing | `## Context`: primary readers are "implementors of the `blog-author` skill"; governs post-body shaping consumed by `skills/blog-author/` (refs=1) and downstream `nolte/blog` |
| `project/post-writing-style` | CONFIRMED consumer-facing | `## Context`: same `blog-author`-implementor readership; style contract consumed by `skills/blog-author/`, applied in the consumer repo |
| `tools/gemini-image-generation` | NOT consumer-facing — genuine UNIMPLEMENTED in-repo gap (see §3) | `## Context`: "A future skill or agent (working title: `gemini-image-generate`) will implement it. The spec exists first so the skill/agent can be validated against it." Spec-first-then-implement; the implementation is owed *in this repo* and is absent |

#### 3. Missing-binding list (specs whose governing skill/agent is absent)

Of the eight specs with zero body-level references, five are governed despite the zero count, and three are genuine open gaps. Severity follows each spec's own posture (review-plan vocabulary).

**Governed despite refs=0 — FALSE POSITIVES:**
- `claude/png-to-transparent-svg` — bound to `agents/png-to-transparent-svg.md`; the spec was authored *to* this pre-existing agent ("formalising what the agent does", closing drift finding D-3). refs=0 only because the agent predates the citation convention.
- `project/docs-freshness` — bound to `agents/docs-freshness-checker.md` (same-stem, read-only checker).
- `claude/plugin-scoping` — axiomatic/reviewer-facing spec ("what bounds a plugin itself"); consumed by reviewers and by `skill-management`/`agent-management`, not a workflow needing its own skill. Not a gap.
- `claude/research-triangulate` — cross-cutting methodology spec ("a deterministic rule for when to triangulate"); applies *inside* other skills/agents at authoring/runtime, by design has no standalone binding. Not a gap.
- `project/spec-driven-development` — explicitly axiomatic: "the axiomatic precondition that the existing process specs operate on." No binding owed. Not a gap.

**Genuine missing bindings — GENUINE findings:**

| Spec (spec_ref) | Severity | Finding |
|---|---|---|
| `spec/tools/gemini-image-generation/en.md` §Context | **Warning** | Spec is authored spec-first and explicitly promises an in-repo implementation ("A future skill or agent, working title `gemini-image-generate`, will implement it"). No skill or agent named `gemini-image-generate` (or any gemini/image-generation binding) exists under `skills/` or `agents/`. This is an owed-but-unimplemented gap *in this repo*, not downstream guidance — distinct from the Ansible/blog consumer-facing specs. Track as a known backlog item, not a conformance defect. |
| `spec/ansible/playbook-development/en.md`, `spec/ansible/role-development/en.md` | **Info** | No in-repo binding by design; the specs self-declare `documentary-only`. Listed here for completeness of the "spec without binding" inventory — explicitly NOT a defect. |

Net: the only genuine spec-induced *gap* is `tools/gemini-image-generation` (Warning, spec promises an in-repo binding that doesn't yet exist). Every other "spec without binding" is either documentary/axiomatic/consumer-facing by self-declaration, or already bound under a differently-spelled slug. The raw fan-out's phantom-artefact and zero-finding flags were over-reported: 11+ phantom-path flags collapse to zero genuine, and 7 zero-finding "potential gaps" collapse to 1 genuine.

COUNTS: genuine=1 false_positive=18 reclassified=2

## Skill-vs-agent classification findings

### Skill-vs-Agent Classification & Agent-Management Triage (skill-vs-agent.*, agent-management.* clusters)

**Headline: No genuine misclassification exists.** I read the skill-vs-agent decision rule and spot-checked the artefact tree against it. Every one of the 26 agents is a self-contained, fire-and-forget executor with a structured-report output contract (collectors, reviewers, scanners, generators) — exactly the agent-bias profile (Interactivity = fire-and-forget, Context-window protection, Tool restriction, Specialization). Every skill that was flagged is an orchestrator/interactive surface (mid-flow approval gates, dispatches agents) — the skill bias. The raw fan-out reported **zero** skill→agent or agent→skill flips, and my independent read of the tree confirms none is warranted. The dimensions table and the default-to-skill rule are respected throughout. This is the highest-value question and the answer is clean: the `skill-vs-agent` cluster surfaces only *rationale-heading-wording* drift, never a wrong format choice.

#### Triage table — genuine vs. false-positive

| Artefact | Finding (spec_ref) | Genuine? | Severity |
|---|---|---|---|
| **3 agents**: `audience-doc-author`, `claude-plugin-developer`, `cookiecutter-template-author` | Rationale heading is `## Rationale (why an agent, not a skill)` not the mandated `## Why this is an agent, not a skill` (skill-vs-agent §Rationale section heading, MUST) | **Genuine** — verified by grep; all 3 deviate, rest of corpus conformant | Critical |
| `webview-ui-optimize` (skill) | Rationale heading `## Rationale (why a skill, not just an agent)` ≠ `## Why this is a skill, not an agent` (skill-vs-agent §Rationale section heading, MUST) | **Genuine** | Critical |
| `webview-ui-expert` (agent) | Declares `Bash` in `tools`, is read-only, **no `## Read-only Bash justification` section** present (agent-management §Tool access narrow exception). Verified: body has only `## Why this is an agent`, no justification section; body even runs `git rev-parse` at line 86 | **Genuine** — without the section `Bash` on a read-only agent stays Critical per spec | Critical |
| `code-security-reviewer` (agent) | Step-3 template uses invented P0/P1/P2/P3 ↔ critical/high/medium/low scale (lines 92–100); bound spec MUST use verbatim Critical/Warning/Suggestion/Info | **Genuine** — verified | Critical |
| `audience-review` (agent) | Body carries a `## German trigger phrases` section (line 34); `distribution: plugin` MUST be English-only in body (agent-management §Structure) | **Genuine** — verified | Critical |
| `diagram-opportunity-reviewer` (agent) | Declares per-file/per-run **cap overrides as inputs** (lines 65–66, 213); spec §Volume control line 61 is an explicit `MUST NOT expose the caps as invocation-time overrides`. Agent also **falsely** attributes overrides to the spec's §Open Questions (line 103 has no such entry — it's an explicit MUST NOT) | **Genuine** — both halves verified; the agent actively contradicts a MUST NOT and misquotes the spec | Critical |
| `portfolio-inflight-collector` (agent) | `tools: [Bash]` in frontmatter, but body line 30 falsely claims "only `Read`, `Bash`, `Glob`, and `Grep` are declared." Runtime scope ≠ body claim (agent-management §Tool access; `tools` is the enforcement point) | **Genuine** — verified | Critical |
| `portfolio-manifest-collector` (agent) | Same defect: `tools: [Bash]` but body line 33 claims `Read`, `Bash`, `Glob`, `Grep` declared (agent-management §Tool access) | **Genuine** — verified. *Note: digest under-rated this as Warning; it is the same class as the inflight-collector Critical and should be Critical* | **Reclassified Warning→Critical** |
| `spec-readiness-reviewer` (agent) | Option B (line 179) files report to `.audits/spec-readiness/<slug>.md`, but tools omit `Write` and Hard rule (line 282) says "Never modify, create, or delete any file." Irreconcilable MUST-vs-MUST | **Genuine** — verified; the agent physically cannot honour Option B | Critical |
| Phase-classification findings: `dependency-audit-scanner`, `vocab-drift-scanner`, `portfolio-inflight-collector`/`-manifest-collector` (`phase: review`), `webview-ui-expert`/`spec-readiness-reviewer` (`phase: design`), `audience-review` (`phase: plan`) | Drift-detection/audit/review agents should be `phase: quality` or `review`, not `review`/`design`/`plan` (skill-agent-catalog §Phase classification, SHOULD) | **Genuine but interpretation-dependent** — `phase` value is a SHOULD ("earliest phase normally invoked"); all values are in-vocabulary so no MUST is breached. Real catalog-bucketing drift but non-blocking | Warning (Suggestion for the design/plan ones) |
| Tag-vocabulary findings: `code-security-reviewer` (`security`), `png-to-transparent-svg` (`scaffolding`), `dependency-audit-scanner` (missing `dependency`) | tags outside/mismatched to starter vocabulary (agent-management §Tag vocabulary, SHOULD) | **Genuine, minor** — `png-to-transparent-svg` using `scaffolding` for an image-conversion agent is a real misuse; the others are additive-specificity quibbles | Suggestion |
| Body-length findings: `diagram-opportunity-reviewer` (~360), `docs-freshness-checker` (333), `png-to-transparent-svg` (280), `spec-readiness-reviewer` (263), `portfolio-inflight-collector` (260) | Exceeds ~200-line SHOULD (agent-management §Recommendations) | **Genuine but soft** — explicitly a local `nolte-shared` convention SHOULD, and the spec itself says inline-don't-split. Inlining is defensible for these | Suggestion |
| `lektorat-scanner` (agent) | description says `(use docs-freshness)` but the artefact is named `docs-freshness-checker` (agent-management §description quality) | **Genuine, trivial** — verified at line 92; `dont_use_when`/`see_also` already use the correct full name, so it's a prose typo not a routing break | Suggestion |
| `mermaid-diagram-reviewer` (agent) | description attributes rendering verification to `docs-freshness-checker`, which handles timestamp drift not build-rendering | **Genuine, informational** — factual-attribution nit | Info |
| Spec-fidelity gaps in reviewer agents (`project-structure-reviewer` false-Critical on missing `tests/`; `quality-gate-enforcer` missing `task check` check; `docs-freshness-checker` missing audit-artifact MUST fields/persist; `roadmap-coherence-reviewer`/`sprint-readiness-reviewer` missing-MUST checks; `test-case-extractor` missing output-contract MUSTs; `graphic-prompt-generator` missing mkdir/docs-tree rules; `i18n-completeness-checker` missing disclosure MUSTs; `mermaid-diagram-reviewer` missing the 5th MkDocs MUST) | Each cites a bound *domain* spec MUST the agent fails to implement | **Genuine, but out-of-cluster** — these are content-completeness findings against domain specs, not skill-vs-agent or agent-management structural findings. Real, but they belong to the domain-spec auditor's section, not this cluster's count. The `project-structure-reviewer` false-Critical on `tests/` is the most consequential (it emits a wrong Critical on every plugin repo) | Warning (varies) |
| `feature-consistency-reviewer` | (clean) | n/a — no finding | Info |

#### False positives / over-escalations to discount

- **`code-security-reviewer` tag `security` as a finding** — the spec §Tag vocabulary is a SHOULD that explicitly permits a new tag "when no starter term fits"; `security` is a reasonable, well-scoped addition. Borderline; I keep it only at Suggestion, not a defect to action.
- **Body-length SHOULD findings** treated by the fan-out as actionable conformance gaps — the spec text itself says "tighten the prose rather than splitting it out" and these are intentional single-file inlinings. Real but near-noise; do not escalate.
- **Phase-classification as Critical anywhere** — never warranted; `phase` is a closed-vocabulary MUST only on *membership*, and every flagged value is in-vocabulary, so the MUST is satisfied and only the SHOULD "earliest/closest phase" is in play.
- **Domain-spec-fidelity findings counted under agent-management** — these are genuine but mis-clustered; they are not agent-*management* (structure/frontmatter/tools) findings and should not inflate this section's agent-management count.

#### Single most important call-out
There is **no true misclassification** in either direction. The recurring genuine pattern across the agent corpus is **tool-list-vs-body inconsistency** (`tools: [Bash]` while the body claims four tools — `portfolio-inflight-collector`, `portfolio-manifest-collector`) and **read-only Bash governance** (`webview-ui-expert` missing the justification section; `spec-readiness-reviewer`'s Option B asking a write-less agent to persist a file). Those, plus the three `## Rationale (...)` heading deviations and the invented-severity-scale in `code-security-reviewer`, the plugin-English-only breach in `audience-review`, and the cap-override MUST-NOT breach in `diagram-opportunity-reviewer`, are the load-bearing genuine findings.

COUNTS: genuine=12 false_positive=4 reclassified=1

## Per-cluster triage detail

### Operations-vocabulary

#### Cluster Audit: skill-management § Operations vocabulary

**Scope.** This cluster gathered ~35 raw findings asserting that a skill's `## Operations` block uses sub-operation headings outside the closed verb vocabulary `{audit, scaffold, patch, apply, migrate, run, update, close}` and/or the wrong heading form. The governing spec is `spec/claude/skill-management/en.md` §"Operations vocabulary", lines 108–116. The two load-bearing MUSTs are:

- **L113–114:** "MUST name each operation with one verb from the closed vocabulary … MUST NOT introduce new operation verbs without amending this list."
- **L115:** "MUST title sub-operations as `### N. <verb>` (numbered) **or as a level-3 heading followed by a backtick-quoted command verb**; alphabetic letters (`A.`/`B.`/`C.`) and `### Step N` are non-conformant."

**The decisive discriminator the raw fan-out ignored.** §"Operations vocabulary" line 110 scopes itself to "Skills **with multiple named operations**." The vocabulary MUST binds the *named operations* a skill dispatches between — i.e. distinct user-selectable modes (`audit` vs. `migrate` vs. `patch`). It does **not** unambiguously bind the *sequential procedure steps* of a single-operation skill (e.g. `### 1. Detect project kind`, `### 2. Run auditors`). The raw fan-out mechanically pattern-matched every `### N. <word>` heading against the eight-verb list and escalated all of them to Critical. That over-counts: roughly half the flagged skills declare exactly one operation and use the `### N.` headings as an ordered runbook, not as a vocabulary of dispatchable operations. Per the task contract these are case **(C)** — Warning + spec-ambiguity note, not Critical.

**Spot-verification method.** I read the actual `## Operations` block (intro prose + every `###` heading) of all 35 flagged skills and cross-checked each against its frontmatter `description` (which declares operation count) before trusting the digest. The digest's heading transcriptions were accurate in every case I checked; the errors were all in *severity/verdict*, not in fact.

#### Verdict table

| Skill | Raw sev | Verdict | Corrected sev | Evidence |
|---|---|---|---|---|
| audience-identify | Critical | A — genuine non-vocab verbs | **Critical** | Three *named operations* `### 1. \`run\``,`### 2. \`validate\``,`### 3. \`revisit\``.`validate`/`revisit` ∉ vocab. Backtick form is OK; verbs are not. |
| cookiecutter-template-manage | Critical | A — partial | **Warning** | `### 1. scaffold` / `### 3. update` conform; only `### 2. refactor` is non-vocab. One verb of three. |
| docs-dry-refactor | Critical | A — genuine | **Critical** | Named ops `### 1. \`scan\``,`### 2. \`propose\``,`### 3. \`apply\``.`scan`+`propose`∉ vocab (`apply` OK). |
| lektorat-apply | Critical | A — partial | **Warning** | `### 1. \`audit\``,`### 2. \`patch\`` conform; only `### 3. \`revise\`` is non-vocab. |
| portfolio-audit | Critical | A — partial | **Warning** | `### 1. Audit` conforms; `Render`/`Bootstrap`/`Discover tech stack` (3 named ops) ∉ vocab. Genuine but not "all". |
| project-structure-apply | Critical | A — partial | **Warning** | Named ops `Audit`/`Apply`/`Re-audit` conform; only `### 2. GitHub App installation check` is non-vocab (also a step, not a true operation). |
| roadmap-plan | Critical | A — genuine | **Critical** | Five named ops `add`/`promote`/`retarget`/`transition`/`mvp-flip` — all dispatchable modes, none in vocab. |
| sprint-execute | Critical | A — genuine | **Critical** | Five named ops `Promote`/`Transition`×2/`Sync`/`Decline` — distinct lifecycle operations, none in vocab. |
| sprint-review | Critical | A — genuine | **Critical** | Seven named ops incl. `Promote`/`Detect`/`Validate`/`Cancellation` — distinct operations, none in vocab. |
| spec | Critical (×3, re-reported) | A — genuine (collapse to 1) | **Critical** | Five named ops; `### 1. Create`→should be `scaffold`, `### 3. Drift check`→`audit`, `### 4. Regenerate index`, `### 5. Coverage / duplicate check` ∉ vocab. The 2nd/3rd spec-finding re-report the same heading-form gap → false positives. |
| skill-agent-catalog-apply | Critical | A — partial | **Warning** | `### 1. Audit` conforms; `Propose and apply`/`Verify`/`Adding further source roots` non-vocab. |
| github-issue-templates-apply | Critical | A — partial | **Warning** | `### 5. Apply` conforms; `Detect`/`Resolve`/`Derive`/`Disclose`/`Re-audit` are the apply-flow's *internal steps*, not named ops. Apply-skill: steps under one operation. |
| mermaid-diagrams-apply | Critical | A — genuine | **Critical** | `Setup audit`/`Setup apply`/`Diagram authoring`/`Diagram audit`/`Re-audit` — compound/non-vocab even though `audit`/`apply` are buried inside; these read as named modes. |
| mission-revise | Critical | **B — letter violation** | **Critical** | `### A.`/`### B.`/`### C.` — the spec L115 *explicitly* names `A./B./C.` as non-conformant. Cleanest genuine heading-form violation in the cluster. |
| webview-ui-optimize | Critical | A — partial | **Warning** | `### 1. \`audit\``,`### 2. \`patch\`` conform (backtick command-verb form); only `### 3. \`expert-review\`` is a new verb. One of three. |
| yaml-json-schema | Critical | A — partial | **Warning** | `### 2. Audit existing schemas` ~conforms; `Author`/`Refactor`/`Meta-validation`/`Data validation`/`Lifecycle bump`/`Re-audit` non-vocab. Genuine but mixed. |
| blog-author-trigger | Critical + Warning | **C — single-op procedure steps** | **Warning** + ambiguity note | Frontmatter declares one trigger flow. `Resolve`/`Derive`/`Compute`/`Execute`/`Deferral artefact` are runbook steps, not dispatchable ops. The extra Warning ("noun phrase") re-reports the same heading. |
| dependency-audit | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | Single `audit` operation; `### 0. Dispatch`…`### 5. Render` are its ordered steps (incl. two conformant `### 3/4. Run`). Not named operations. |
| feature-decompose | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation (decompose); `### 1. Decompose` + `### 2. Run the consistency check` are its two steps. |
| mission-define | Critical (×2, re-reported) | **C — single-op procedure steps** (collapse to 1) | **Warning** + ambiguity note | One operation; `Read`/`Walk`/`Compose`/`Confirm` are a runbook. 2nd finding re-reports the same headings as a "format" violation → false positive. |
| permission-allowlist-maintain | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation; `Load`/`Gather`/`Apply`/`Reject`/`Narrow`/`Apply`/`Hand off` are sequential steps. |
| pull-request-create | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation (create PR); `Collect`/`Ensure`/`Build`/`Build` are steps. |
| pull-request-merge | Critical + Critical(`7c`) | **C (steps)** + **B (`7c`)** | **Warning** (steps) + **Warning** (`7c`) | One operation (promote PR); `Inspect`/`Delegate`/…/`Clean` are steps. Separately, `### 7c.` is a genuine alphanumeric heading-form deviation (B) — real but Warning-grade, not Critical. |
| quality-gate | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation; six rendering steps. |
| release-notes-curate | Critical (×2, re-reported) | **C — single-op procedure steps** (collapse to 1) | **Warning** + ambiguity note | Intro prose explicitly says "Operations 4 to 6 form a … Plan-validate-execute cycle" — i.e. steps of one flow. 2nd "heading-must" finding re-reports → false positive. |
| release-publish-trigger | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | Intro: "Operations 2 to 4 form a Plan-validate-execute cycle." Single dispatch operation; `Resolve`/`Validate`/`Disclose`/`Dispatch`/`Verify` are its steps. |
| roadmap-init | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation (scaffold the pair); `Resolve`/`Draft`/`Draft`/`Present`/`Write` are steps. |
| roadmap-refine | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation (enforce invariant); `Resolve`/`Walk`/`Emit`/`Walk`/`Final report` are steps. |
| sprint-plan | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One operation (create sprint file); 7 ordered steps. Digest itself notes "sprint-execute uses the same pattern". |
| tech-stack-capture | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | Intro explicitly: "The single operation produces a `tech_stack:` block … Run the eight steps in order." Self-evidently one operation. |
| vocab-drift-audit | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One `audit` operation; the four items are bold-prose runbook steps (`Locate`/`Dispatch`/`Render`/`Offer`), not even `###` headings. |
| workflow-health-triage | Critical | **C — single-op procedure steps** | **Warning** + ambiguity note | One triage operation; `Inspect`/`Classify`/`Dispatch` are its steps. |
| docs-audience-tracks-apply | Warning (`migrate`/greenfield mislabel) | A — genuine *terminology* drift, not a vocab violation | **Warning** | Headings `### 1. \`audit\``,`### 2. \`migrate\``,`### 3. \`patch\`` all conform. The real finding is that `migrate` is repeatedly labelled "greenfield" though the spec defines `migrate`="brownfield → conforming". Correctly already Warning; keep. |
| skill-management | Critical + Critical + Warning | A (genuine) + B (`### Review / audit`) ; 3rd is re-report | **Critical** + **Warning** | `### 1. Create a new skill` / `### 2. Revise` — `Create`/`Revise` ∉ vocab (genuine A, Critical). `### Review / audit` is unnumbered + slash-compound (genuine B, Warning). The 3rd "extra words after verb" finding re-reports heading 1 → false positive. |

#### Re-reporting / false positives identified

Several skills carry 2–3 findings that describe the **same** non-conformant heading from different angles ("verb not in vocab" vs. "heading form has extra words" vs. "noun phrase"). Under L115 these are one defect, not two. Collapsed re-reports: `blog-author-trigger` (+1), `mission-define` (+1), `release-notes-curate` (+1), `skill-management` (+1), `spec` (+2), `pull-request-merge`'s step-finding overlap. Additionally the `sprint-execute` `[Info]` (stale external cross-refs in `blog-author-trigger/en.md` + `CLAUDE.md`) and `[Warning]` (stale `Operation C/D` prose in the Gotchas body) are **not** Operations-vocabulary heading violations — they are genuine but belong to a *consistent-terminology* finding about stale internal/external references; I reclassify them out of this cluster (kept as 1 genuine Warning for the body-prose drift, the Info is a non-finding observation).

#### Systemic recommendation: structural fix, not per-skill

The cluster's true signal is a **spec design problem, not 35 independent skill defects.** Three quarters of the flagged skills are well-authored runbooks whose only "violation" is that the spec is silent on whether L113–114 reaches into single-operation procedure steps. Per-skill rewrites (renaming `### 1. Resolve` → `### 1. run` across ~17 skills) would *degrade* readability — collapsing an informative 5-step runbook into five headings all reading `### N. run` destroys the navigational value the headings provide, to satisfy a rule that was written for dispatch vocabularies.

The correct fix is **structural, applied once to the spec**:

1. **Amend `spec/claude/skill-management/en.md` §"Operations vocabulary" to scope the verb MUST explicitly.** State that L113–114 binds the *set of named, dispatchable operations* a multi-operation skill exposes (the modes a user/router selects between), and that a single-operation skill's `## Operations` block MAY use descriptive `### N. <step name>` headings for its ordered procedure, provided the operation itself is named with `run` (or the skill's single closed-vocab verb) in the frontmatter/intro. This converts ~17 Criticals to conformant in one edit.
2. **For the genuinely multi-operation skills** (audience-identify, docs-dry-refactor, roadmap-plan, sprint-execute, sprint-review, spec, mermaid-diagrams-apply, portfolio-audit, yaml-json-schema, skill-agent-catalog-apply, cookiecutter-template-manage, lektorat-apply, webview-ui-optimize, github-issue-templates-apply, project-structure-apply): a real per-skill verb-alignment pass is warranted, but most need only renaming the *non-conformant named operations* (e.g. `Render`→pick a vocab verb or amend the list to add `render`/`bootstrap`/`revise`/`scan`/`propose` if the portfolio genuinely needs them). The recurrence of `revise`, `scan`, `propose`, `render`, `bootstrap`, `validate` across multiple skills suggests the **closed list itself is under-sized** — the cheapest correct fix may be to *amend the vocabulary* (which L114 explicitly contemplates) rather than rename operations the whole portfolio already standardises on.
3. **Fix the two unambiguous heading-form deviations now, independent of the above:** `mission-revise` (`### A./B./C.` → numbered) and `pull-request-merge` (`### 7c.` → renumber). These are real under L115 regardless of how the scoping ambiguity resolves.

#### Recorded spec-ambiguity finding

> **[Warning] [skill-management.operations-vocabulary] — spec ambiguity.** `spec/claude/skill-management/en.md` §"Operations vocabulary" (L108–116) opens by scoping itself to "Skills with multiple named operations" (L110) but then states the verb MUST (L113–114) and the heading-form MUST (L115) in unqualified terms that read as binding *every* `### N. <heading>` under any `## Operations` block. The spec never states whether a **single-operation** skill whose `## Operations` block contains sequential *procedure steps* (e.g. `### 1. Detect project kind`, `### 2. Run auditors`) must draw those step headings from the closed eight-verb vocabulary, or whether the vocabulary MUST binds only the set of dispatchable named operations. This ambiguity is the direct cause of ~17 over-escalated Critical findings in this audit. The spec SHOULD be amended to scope L113–114 explicitly (see systemic recommendation #1).

COUNTS: genuine=18 false_positive=8 reclassified=17

### Description third-person & frontmatter

#### Third-person `description` cluster (`skill-management.description-third-person` / `frontmatter-validation`)

**Bottom line: every finding in this cluster is a false positive against the spec's operative definition of the rule.** The MUST (spec `skill-management/en.md` line 46) forbids first/second person, citing exactly two violation examples — `"I help …"` and `"You can use this to …"` — both pronoun-bearing constructions. The repository's own canonical validator `scripts/validate_skills.py` (run by `task test`, the AC-mandated enforcement at spec line 175) operationalizes this MUST as a **pronoun check only**: `FORBIDDEN_PRONOUNS_RE = \b(I|you|your|yours|yourself|we|our|ours|us)\b` (line 61), applied to author-voice text after stripping double-quoted trigger spans (lines 189–196). It does not flag imperative-mood opening verbs, and it does not flag `Don't use…` / `Invoke when…` clauses. Running the validator against revision b91b67b yields **zero** `description-third-person` findings across the entire surface. The fan-out invented a stricter reading than the spec's own enforced semantics.

Two distinct sub-claims were raised; both fail.

**Sub-claim A — `Don't use…` / `Invoke when…` disambiguation clauses are "second-person imperatives."** These are imperative *mood*, not second *person*: they carry no forbidden pronoun, pass the validator, and are the deliberate house style across the whole surface. Spec line 47 independently *requires* the description to name "when to use it" — the `Invoke when` trigger clause is the conformant way to satisfy that half of the discovery contract. False positive.

**Sub-claim B — bare-imperative opening verb (`Review…`, `Scan…`) instead of `Reviews…`/`Scans…`.** Grammatically not third-person singular, and stylistically inconsistent with the -s forms used later in the same description — but the canonical validator deliberately does not flag it, so escalating it to Critical/Warning over-reads the MUST. At most a Suggestion-grade consistency nit; not a genuine violation.

| artefact | quoted phrase | genuine? | corrected severity |
|---|---|---|---|
| agent-review | `Do NOT use for skill review` | no (FP) | — |
| agent-review | opener `Review a Claude Code agent…` | no (interp.) | Suggestion |
| audience-identify | `Don't use to review an existing audience artifact` | no (FP) | — |
| dependency-audit | opener `Scan the current project's…` | no (interp.) | Suggestion |
| docs-dry-refactor | `Don't use for non-MkDocs markdown trees…` | no (FP) | — |
| feature-decompose | opener `Decompose a roadmap item` | no (interp.) | Suggestion |
| feature-decompose | `Don't use to transition feature status` | no (FP) | — |
| mermaid-diagrams-apply | `Invoke when the user asks…` | no (FP) | — |
| mermaid-diagrams-apply | `Don't use for general MkDocs scaffolding` | no (FP) | — |
| mermaid-diagrams-apply | meta: "mis-classified as Warning, must be Critical" | no (FP)¹ | — |
| mkdocs-structure-apply | `Invoke when…` / `Don't use for` | no (FP) | — |
| pull-request-create | opener `Create a GitHub pull request…` + `Invoke when…` | no (interp./FP) | Suggestion |
| pull-request-merge | opener `Promote an open draft…` + `Invoke when…` | no (interp./FP) | Suggestion |
| release-notes-curate | `Invoke when…` / `Don't use to publish…` | no (FP) | — |
| release-publish-trigger | `Invoke when the user asks to …` | no (FP) | — |
| roadmap-init | opener `Scaffold` + `Invoke when…` | no (interp./FP) | Suggestion |
| roadmap-refine | `Don't use to add items…` | no (FP) | — |
| skill-agent-catalog-apply | `Don't use for authoring individual skills/agents` | no (FP) | — |
| skill-management | opener `Author or revise…` + `Invoke when…` | no (interp./FP) | Suggestion |

¹ The mermaid "severity should be Critical not Warning" finding is doubly wrong: the underlying finding is itself a false positive, so there is no severity to escalate.

Spot-verification notes: `audience-identify`, `docs-dry-refactor`, `mermaid-diagrams-apply`, `mkdocs-structure-apply`, `release-notes-curate`, `release-publish-trigger`, `roadmap-refine`, and `skill-agent-catalog-apply` all open with a correct third-person -s verb (`Runs`, `Operationalises`, `Audits`, `Augments`, `Validates`, `Enforces`, `Wires up`) — the fan-out flagged only their `Don't use`/`Invoke when` clauses, which is purely sub-claim A. Files under `/home/nolte/repos/github/claude-shared/skills/<name>/SKILL.md`; rule semantics fixed by `/home/nolte/repos/github/claude-shared/scripts/validate_skills.py` lines 61, 189–196; spec at `/home/nolte/repos/github/claude-shared/spec/claude/skill-management/en.md` line 46.

**Systemic recommendation.** Resolve this rule against its checked-in operationalization, not against an idealized grammar reading: the third-person MUST means "no first/second-person *pronouns* in author voice," and `Don't use…`/`Invoke when…` is the sanctioned, spec-required (line 47) trigger/redirect idiom used uniformly across the surface — it must not be flagged. To stop this false-positive class from recurring in future audits, add one clarifying sentence to spec line 46 stating that the rule targets grammatical person (pronouns), that imperative-mood trigger/redirect clauses are conformant, and pointing reviewers at `scripts/validate_skills.py` as the authoritative arbiter. The bare-imperative openers (`Review…`/`Scan…`/`Decompose…`/`Create…`/`Promote…`/`Author or revise…`/`Scaffold`) are a legitimate but minor Suggestion-grade consistency item — worth a non-blocking sweep to normalize to the -s form for internal consistency, but never Critical/Warning and never merge-blocking.

COUNTS: genuine=0 false_positive=11 reclassified=6

### Progressive-disclosure, evaluation, authoring-quality

#### Progressive disclosure (load-trigger / file-references), Evaluation discipline, and Authoring quality

Scope: the load-trigger / file-reference phrasing variants of `skill-management.progressive-disclosure`, the `evaluation-discipline` / `evaluation-scenarios` cluster, and the `authoring-quality` cluster. All three clusters are SHOULD- or interpretation-class except where a load-trigger is genuinely absent (MUST). I spot-verified every retained finding against the real skill folders at revision b91b67b.

**Boundary note (de-duplication against the TOC cluster):** the raw fan-out filed ~16 findings under the `progressive-disclosure` tag, but the large majority (cookiecutter, mission-define, github-issue-templates, pull-request-create/-merge, release-publish-trigger, roadmap-refine, skill-agent-catalog-apply, portfolio-audit, mission-revise) are *table-of-contents-on-files-over-100-lines* findings, which belong to the §123 TOC MUST, not the §124/§125 load-trigger MUST that defines this cluster. I verified those line counts are real (all flagged files do exceed 100 lines and lack a TOC) but they are owned by the TOC reviewer; I exclude them here to avoid the over-count the brief warns about. Only three findings are genuinely about load-trigger / file-reference *phrasing*.

#### Load-trigger / file-references (§124–125)

| Skill | Asset / location | Spec ref | Raw sev | My verdict | Adjusted |
|---|---|---|---|---|---|
| agent-review | `templates/plan.template.md` (SKILL.md L84, L110) | skill-management §125 | Warning | Genuine per-asset gap — referenced as "Draft the plan from …" / "the starting point", no `when`/`for` clause | **Warning** |
| audience-identify | `templates/audiences.template.md` (L73) | skill-management §125 | Critical | Genuine literal gap ("using the template at …", no `when`/`for`), but over-escalated; trigger is implicit in the write step | **Suggestion** (reclassified from Critical) |
| continuous-improvement-triage | `templates/triage.template.md` (L42) | skill-management §125 | Critical | Borderline false positive — the line **is** an explicit load-trigger ("Read … *to understand* … *before* creating/updating"); it names what the file contains and when to read it, only the preposition (`to`/`before`) differs from the literal `when`/`for` keyword | **Suggestion** (reclassified from Critical) |

Systemic verdict: **not systemic — these are one-offs.** Baseline measurement: 38 of 43 skills already use conformant `Read X when` / `See X for` phrasing, and all three flagged skills use conformant triggers for their *other* assets. continuous-improvement-triage even appears in the conformant-phrasing set; the flagged line is the same template, double-referenced. So the corpus has the pattern internalized; these are isolated wording slips on a single asset each, correctly Suggestion-grade except agent-review (no trigger at all → Warning stands).

#### Evaluation discipline / scenarios (§145, SHOULD — at least three scenarios under `examples/`)

| Skill | examples/ present | Non-trivial? | Spec ref | Verdict |
|---|---|---|---|---|
| blog-author | none | yes (7-step bilingual workflow, multiple approval gates) | skill-management §145 | **Warning** — genuine |
| docs-audience-tracks-apply | none | yes (3 operations) | §145 | **Warning** — genuine |
| docs-dry-refactor | none | yes (3 operations) | §145 | **Warning** — genuine |
| mkdocs-structure-apply | none | yes (3 operations) | §145 | **Suggestion** (raw filed Suggestion; consistent) |
| readme-structure-apply | none | yes (3 operations) | §145 | **Suggestion** (raw filed Suggestion; consistent) |
| portfolio-audit | 3 files, but 4 operations (op 4 "Discover tech stack" unexampled) | yes | §145 | **Suggestion** — partial coverage, not a clean miss |

Systemic verdict: **systemic.** A full `ls` of `skills/` confirms exactly six skills ship no `examples/` directory: the five above plus `webview-ui-optimize` (195 lines, 3 operations — not in the fan-out but the same gap). Every other skill (37) ships ≥3 scenarios. This is the one genuinely systemic SHOULD-gap in my clusters: a consistent six-skill cohort, all non-trivial, all missing the evaluation layer the spec recommends. The severity is correctly SHOULD/Warning, not Critical — the spec is unambiguously SHOULD and these skills are otherwise functional. The mixed Warning/Suggestion in the raw fan-out is noise; I'd normalize the whole cohort to **Warning** since all six are non-trivial multi-step skills.

#### Authoring quality (§90–106, §99 consistent terminology, §95 Gotchas, §85 length)

| Skill | Finding | Spec ref | Raw sev | Verdict |
|---|---|---|---|---|
| blog-author | "Diataxis" (no accent) at L28, L78 vs "Diátaxis" everywhere in governing specs (`post-audience-communication`, `blog-author`) | §99 consistent terminology | Suggestion | **Suggestion** — genuine, verified |
| blog-author-trigger | SKILL.md L120 says "step 5"; authoritative `sprint-execute` SKILL.md L91 and consumer `CLAUDE.md` both say **step 6** | §99 (consistency) | Warning | **Warning** — genuine factual error, verified against L91 |
| blog-author-trigger | no `## Gotchas` section (has `## Hard rules` at L131 only) | §95 SHOULD | Suggestion | **Suggestion** — genuine but discretionary |
| docs-dry-refactor | SKILL.md 157 lines > 150 soft target | §85 SHOULD | Warning | **Suggestion** (reclassified) — §85 is an explicitly *soft* target; 157 is 5% over |
| release-publish-trigger | SKILL.md 160 lines; `## Wait mode` partly duplicates §5 | §85 SHOULD | Warning | **Suggestion** (reclassified) — soft target, minor |

Length findings note: I confirmed the line counts (docs-dry-refactor 157, release-publish-trigger 160, lektorat-apply 168, mermaid 182, release-notes-curate 191, feature-decompose 220, pull-request-merge 232, skill-agent-catalog-apply 268). The §85 "roughly 150 lines" target is explicitly soft, so over-target-but-under-500-line/5000-token findings are Suggestion-grade, not Warning. The one genuine hard-cap breach (skill-agent-catalog-apply ≈6,500 tokens > 5,000-token MUST) is a real Critical but belongs to the token-cap cluster, not authoring-quality-length, so I leave it to that reviewer.

Systemic verdict for authoring-quality: **one-offs, not systemic.** The Diátaxis accent and the step-5/6 fact are both isolated to blog-author / blog-author-trigger. The Gotchas-section SHOULD is discretionary and not worth flagging across the corpus.

#### Systemic recommendation

One genuinely systemic gap: **the six-skill cohort lacking `examples/`** (`blog-author`, `docs-audience-tracks-apply`, `docs-dry-refactor`, `mkdocs-structure-apply`, `readme-structure-apply`, `webview-ui-optimize`). All are non-trivial multi-step skills; the §145 three-scenario SHOULD is unmet uniformly. Recommend a single backlog item to scaffold three evaluation scenarios per skill for this cohort, bringing them in line with the other 37. This is the only cluster-wide action; everything else is per-skill polish. The load-trigger phrasing is effectively a solved problem corpus-wide (38/43 conformant) and needs only three one-line wording fixes.

COUNTS: genuine=11 false_positive=1 reclassified=4

### Catalog metadata & naming

#### skill-agent-catalog — use-case-metadata, phase-classification, naming

Scope: `skill-agent-catalog.use-case-metadata` (~5), `skill-agent-catalog.phase-classification` (~5), and the lone `naming` flag. Severity vocabulary per review-plan: Critical / Warning / Suggestion / Info.

**Governing spec facts (verified against `spec/claude/skill-agent-catalog/en.md`):**
- §Phase classification (lines 59–73): `phase` is a **MUST** — must be present and drawn from the closed 8-value vocab (`vision, plan, design, build, review, quality, close-release, cross-cutting`). Missing/out-of-vocab fails the build. **Which** in-vocab value an author picks is governed only by a **SHOULD** (line 73: "pick the earliest phase … review and quality artifacts … belong to the artifact's own primary purpose, not to the calling phase").
- §Use-case metadata (lines 85–94): `use_when` / `dont_use_when` / `see_also` / `examples` are all **MAY** here. Line 93 is explicit: "their authoring requirement (when authors **SHOULD** declare them) is owned by `skill-management` and `agent-management`. This spec owns only the schema and validation, so the fields stay optional here permanently." The only MUSTs this spec carries are (a) validating the *shape* of *declared* fields and (b) resolving *declared* `dont_use_when[].alternative` / `see_also[]` names.

#### Phase-classification cluster

| artefact | flagged phase | actual phase (verified) | genuine? | severity |
|---|---|---|---|---|
| `dependency-audit-scanner` | should be `quality`, is `review` | `review` (in-vocab) | **Yes** | Suggestion |
| `vocab-drift-scanner` | should be `quality`, is `review` | `review` (in-vocab) | **Yes** | Suggestion |
| `audience-review` | should be `quality`/`review`, is `plan` | `plan` (in-vocab) | No (defensible) | reclassified → Info |
| `webview-ui-expert` | should be `quality`, is `design` | `design` (in-vocab) | borderline | reclassified → Info |
| `spec-readiness-reviewer` | should be `review`, is `design` | `design` (in-vocab) | borderline | reclassified → Info |

All five flags name **in-vocabulary** values, so none is the MUST violation the raw fan-out severity (Warning) implies — they are all §line-73 **SHOULD** judgments, which top out at Suggestion. I keep two as genuine and downgrade the rest:

- **`dependency-audit-scanner` (`review`) — genuine, Suggestion.** Its own description: "Read-only scanner … return a structured CVE drift inventory." A vulnerability scan is squarely the `quality` definition ("audits, scans, … drift detection"). Its parent skill `dependency-audit` is `phase: quality` (verified), and sibling scan agents `tech-stack-drift-reviewer`, `docs-freshness-checker`, `i18n-completeness-checker`, `quality-gate-enforcer` are all `quality`. spec_ref `skill-agent-catalog.phase-classification`; file `agents/dependency-audit-scanner.md` frontmatter. The line-73 SHOULD ("primary purpose, not the calling phase") makes this a clean drift.
- **`vocab-drift-scanner` (`review`) — genuine, Suggestion.** Description: "Read-only scanner that diffs repository-local Vale vocabulary files … drift." Parent skill `vocab-drift-audit` is `phase: quality` (verified). Same reasoning as above. spec_ref `skill-agent-catalog.phase-classification`; file `agents/vocab-drift-scanner.md`. The fan-out's claim that the *MUST* is what's at stake is wrong (the value is in-vocab); the genuine basis is the SHOULD plus parent-skill inconsistency. Severity corrected Warning → Suggestion.
- **`audience-review` (`plan`) — false positive / reclassified to Info.** The fan-out asserts `plan` "is accurate only when it gates a downstream planning step." But the established `nolte-shared` convention is that planning-artefact reviewers sit in `plan`: `roadmap-coherence-reviewer`, `sprint-readiness-reviewer`, and `feature-consistency-reviewer` are all `phase: plan` (verified). `audience-review` audits the audience artefact — a plan-phase input — so `plan` follows local precedent. The SHOULD is satisfiable either way; this is interpretation-dependent, not a drift.
- **`webview-ui-expert` (`design`) and `spec-readiness-reviewer` (`design`) — reclassified to Info.** Both are valid in-vocab values; the raw flags themselves concede "no MUST violation." `spec-readiness-reviewer` plausibly authors-against-specs (design) as much as it reviews; `webview-ui-expert` is a cross-domain advisory expert, not narrowly a drift scanner. No parent-skill inconsistency exists for either (unlike the two genuine cases). Interpretation-dependent SHOULD; not actionable as a finding.

#### Use-case-metadata cluster

Every flag in this cluster targets a **missing optional field** (`dont_use_when` / `see_also` entry not declared). Against this spec they are **false positives by attribution**: §line 93 explicitly disclaims the authoring requirement and parks it in `skill-management` / `agent-management`. The fan-out repeatedly mis-cites `skill-agent-catalog.use-case-metadata` (and the parallel `agent-management.use-case-metadata`) as if this spec *requires* declaring the field.

| artefact | flag | genuine under skill-agent-catalog? | disposition |
|---|---|---|---|
| `readme-structure-apply` | `audience-identify` in prose but not in `dont_use_when` | No | false positive (mis-attributed) |
| `prose-vale-curator` | 3rd don't-use case absent from `dont_use_when` | No | false positive |
| `graphic-prompt-generator` | 2 don't-use cases not in `dont_use_when` | No | false positive |
| `png-to-transparent-svg` | `dont_use_when` / `see_also` absent | No | false positive |
| `i18n-completeness-checker` | (Info) fields conformant | n/a | confirmation, keep as Info |

- **`readme-structure-apply` — false positive.** Verified frontmatter: `dont_use_when` is *present* with three resolvable entries (`audience-doc-author`, `mkdocs-structure-apply`, `prose-vale-curator`) and `see_also` mirrors them. The flag's framing — "§Use-case metadata requires every `dont_use_when` entry to carry a resolvable `alternative`" — misreads the MUST: that MUST governs *declared* entries (all three present here resolve), not the *absence* of an `audience-identify` entry. The underlying observation (prose names a redirect the structured field omits) is a real authoring-completeness nit, but it lands under `skill-management`'s SHOULD, not this spec, and is Suggestion-grade at most. As cited, false positive.
- **`prose-vale-curator`, `graphic-prompt-generator`, `png-to-transparent-svg` — false positives** for the same structural reason: a *missing* optional field cannot violate a spec that declares the field permanently optional and disclaims the authoring SHOULD. These belong to the `agent-management` / `skill-management` audit sections, not here, and the fan-out already grades them Suggestion/Warning inconsistently. The duplicate `skill-management.use-case-metadata` flags on `continuous-improvement-triage`, `permission-allowlist-maintain`, `vocab-drift-audit`, and `yaml-json-schema` are the same pattern under the correct owner-spec ref and are out of this section's scope (owned by the skill-management cluster).
- **`i18n-completeness-checker` (Info)** — legitimately a *conformance confirmation* (declared `dont_use_when` uses the correct `situation`/`alternative` shape and resolves). Keep as Info; not a violation.

#### Naming

- **`skills-agents-sweep` — reclassified Critical → Suggestion (genuine observation, wrong severity).** The flag itself states the convention is recorded as a **SHOULD** and that the name is noun-noun-verb against the plugin's verb-noun norm. A SHOULD deviation cannot be Critical under review-plan severity. The observation is real and worth a Suggestion, but the Critical grade is an over-escalation. spec_ref: skill-management naming SHOULD; file `skills/skills-agents-sweep/SKILL.md`.

#### Systemic recommendation — does the build already fail?

The fan-out's implicit worry (drift in `phase` / use-case fields slipping through) is **already structurally guarded at the MUST layer**, verified in two places:
- `scripts/validate_skills.py` (run via `task test`): `check_phase()` emits a **Critical** and the script exits non-zero when `phase` is missing or out-of-vocabulary (lines 249–255, 277, 295, 376).
- `scripts/docs/gen_catalog.py` (the catalog generator, run on the docs build): `_validate_phase()` raises `CatalogError` (fail-build) on bad phase, validates use-case-field *shape*, and runs the `dont_use_when[].alternative` / `see_also[]` resolvability checks (lines 190, 382, et seq.) — exactly the §Error-handling MUSTs.

So **no new build gate is warranted**, and recommending "the catalog generator should fail the build" would be redundant — it already does, for every MUST this cluster touches. What the build deliberately does *not* enforce is (a) the *quality* of an in-vocab phase choice (the line-73 SHOULD) and (b) the *presence* of optional use-case fields — both correctly left to human review per §line 93. The only genuinely actionable systemic items are the two phase mis-classifications (`dependency-audit-scanner`, `vocab-drift-scanner` → `quality`), which are one-line frontmatter edits that also restore consistency with their `quality`-phase parent skills.

COUNTS: genuine=3 false_positive=5 reclassified=4

### Backward (spec→implementation) cluster validation

#### Backward Direction (spec → implementation drift)

**Scope of this section.** Validation of the largest backward clusters in `.audit-tmp/digest_backward.md` against the actual implementation at revision `b91b67b`. The single most important framing fact, verified directly: **every cluster spec listed below carries `Status: draft`** (`grep "^Status:"` across all twelve). The repo's own `spec-drift-audit` SKILL §step 3 keeps draft specs in audit scope, so the gaps are *real* and *must be closed on promotion* — but they are **not merge-blocking Criticals on a shipped artifact**. The raw fan-out's repeated "Critical" escalation against draft specs is the chief over-counting pattern; I have reclassified accordingly. A second pattern: several "repo gaps" actually target an upstream artifact (`nolte/gh-plumbing` reusable workflow), not a file this repo owns.

#### Cluster validation table

| Spec | Top finding (verified) | Genuine repo gap? | Severity (adjudicated) |
|---|---|---|---|
| `project/dependency-audit` | Skill omits the spec's CVSS severity scale, three-option response taxonomy, ignore-discipline fields, and audit-artifact persistence step. Verified: `skills/dependency-audit/SKILL.md` has no severity-threshold mapping, no "accept as known", no `.audits/dependency-audit/` persistence; `grep` confirms zero matches. | **Yes** — genuine skill→spec drift. The *skill is the shipped deliverable*, so the gap is real even though this repo has no dependency manifest of its own. | Warning ×8, one artifact-persistence gap is the most actionable. (digest had 1 Critical — reclassify to Warning: draft spec, skill-encoding gap not a MUST-violation-on-merge) |
| `claude/research-triangulate` | Three named MUST-apply skills (`dependency-audit`, `release-notes-curate`, `cookiecutter-template-manage`) contain zero triangulation language; only `cookiecutter-template-author.md` partially implements it (≥2 sources + conflict-surface) but lacks blast-radius tiers, source-class/date recording, `unverified` marking, autonomous-loop abort. Verified via `grep -rl`. | **Yes** — genuine, broad. | Warning (digest had 5 Criticals — **reclassify all to Warning**: spec is draft, methodology not yet promoted; gaps to close on promotion per spec's own Context note) |
| `project/spec-drift-audit` | The only artifact (`.audits/spec-drift/2026-Q2.md`) lacks YAML frontmatter and a per-criterion pass/fail table; ~21 specs added after Q2 are uncovered. Verified by reading the artifact head — it has a prose Summary table but no frontmatter/per-criterion grid. | **Yes** for the artifact-shape and coverage gaps. Finding [9] (auditor flagging its own MUST→Warning downgrades) is **meta-noise / FALSE POSITIVE** — it audits the audit, not the repo. | Warning (artifact shape, coverage). Reclassify the self-referential finding [9] out. |
| `portfolio/portfolio-management` | `.audits/portfolio/`, `docs/en/portfolio/`, `docs/de/portfolio/` all genuinely absent (verified `test -e`); portfolio-audit never skill-reviewed; no CI rendering check. | **Yes** — genuinely unbuilt feature surface. AC-8 ("continuous-improvement must list portfolio-audit") is a *cross-spec wording obligation on the OTHER spec's future revision*, not a portfolio-management impl gap — reclassify AC-8. | Warning (draft spec, unbuilt feature). digest's 5 Criticals → Warning. |
| `claude/review-plan` | Two simultaneous `open` portfolio-inflight plans with timestamped filenames (`2026-05-23.md`, `-v2.md`) — but this is a **genuine cross-spec conflict**: `portfolio-inflight-management §Findings-Report` MUSTs `<YYYY-MM-DD>.md` while review-plan MUST-NOTs timestamps. Verified both files exist. | **Partially** — the dual-open-plan/`status: closed` invented-value findings are genuine hygiene gaps. The timestamp finding is a real, unresolved spec-vs-spec contradiction, not pure impl drift. | Warning (genuine), but flag as spec-vs-spec conflict needing a tie-breaker, not a one-sided fix. |
| `claude/skill-review` | 39/43 skills never reviewed; no closure commit matches the required `review(skill-review): close <skill>—<C>C/...` format. Plus a genuine spec-internal contradiction: skill-review line 82 ("any other frontmatter value") over-broadens skill-management line 42 ("name only"), violating its own tie-breaker. | **Yes** for the reserved-token over-specification (genuine, actionable) and the format-drift. The "39/43 unreviewed" is a coverage backlog, real but low-actionability. Note digest double-reports the reserved-token issue (Warning *and* Critical for the same line 82) — collapse to one. | Warning. The reserved-token over-broadening is the most actionable single fix here. |
| `project/docs-audience-tracks` | `docs/en/index.md` + `nutzung.md` (and DE) declare `audience:[maintainer, downstream-user]` with `track: developer-docs`, but AUDIENCES.md maps `downstream-user → user-docs` — verified audience/track contradiction. User-docs content blocks genuinely absent. | **Yes** — genuine, concrete, 4-page mismatch + missing user-docs track. | Warning (draft spec). Most actionable: the 4-page audience↔track contradiction (mechanical fix). |
| `project/mkdocs-structure` | `docs/requirements.txt` uses `>=` floating pins for every plugin, no lockfile. Verified directly (all 7 lines are `>=`). | **Yes** — genuine, concrete, trivially actionable. | Warning (draft spec; would be Critical post-promotion). **Most actionable gap in the whole backward set.** |
| `project/prose-style` | `.vale.ini` sets `MinAlertLevel = suggestion` but Taskfile target uses `--minAlertLevel=error`. Verified directly. Local `vale .` and CI produce different alert sets. | **Yes** — genuine, one-line config divergence. | Warning. Actionable. |
| `project/release-automation` | Findings about title-not-displayed and `plugins[].version` selector target the **upstream `nolte/gh-plumbing:reusable-release-publish.yml@v1.1.19`**, which this repo only thin-wraps. | **Mostly NO for this repo** — these are upstream/consumer-facing gaps not fixable in `claude-shared`'s own files. The v0.1.2 manual-publish AC finding is genuine but **already known and closed-going-forward** (R-2; the loophole pre-dates the automated pipeline). | Reclassify the two "Critical" reusable-internal findings to **out-of-repo / not-actionable-here**; the v0.1.2 finding is Info (historical, mitigated). |
| `project/continuous-improvement` | Sampled PRs (#231, #228, #223, #205) have Risk/rollout notes but **none** names a dispatched specialist or originating-finding-source. Verified via `gh pr view`. The two traceability MUSTs (spec lines 54–55) are genuinely unmet. | **Yes** — genuine, data-backed ("0 of 10"). portfolio-audit & dependency-audit are also genuinely absent from the spec's own "Finding sources in scope" block (lines 25–34). | Warning (draft spec). Genuine process gap; actionable by adding two PR-body fields to the PR-create skill template. |
| `project/docs-freshness` | Agent output `## Scope` template (lines 91–95) lacks `date`, `trigger`, and `Git revision` fields the spec MUSTs. Verified directly. No pre-release/pre-PR CI gate wired. | **Yes** — genuine template gap (3 missing fields) + missing CI wiring. | Warning (draft spec). The 3 missing Scope fields are a mechanical, actionable fix. |

#### Most actionable genuine spec→impl gaps (ranked)

1. **`mkdocs-structure` — floating plugin pins** (`docs/requirements.txt`). All seven deps are `>=`, no lockfile. One-PR fix; deterministic; the spec's MUST is unambiguous. Highest signal-to-effort ratio in the entire backward set.
2. **`docs-audience-tracks` — 4-page audience↔track contradiction.** `downstream-user` (a user-docs audience per AUDIENCES.md) is paired with `track: developer-docs` on `index.md`/`nutzung.md` (EN+DE). Mechanical frontmatter fix or an explicit user-docs opt-out note in AUDIENCES.md.
3. **`prose-style` — Vale alert-level divergence.** `.vale.ini` (`suggestion`) vs Taskfile (`error`). Align the two so local `vale .` matches CI.
4. **`continuous-improvement` — PR-traceability fields absent.** Add "dispatched specialist" + "originating finding source" lines to the `pull-request-create` skill's Risk/rollout-notes template; verified 0/4 sampled PRs carry them.
5. **`docs-freshness` — agent Scope template missing date/trigger/Git-revision.** Three named fields the spec MUSTs; a template edit in `agents/docs-freshness-checker.md`.
6. **`skill-review` — reserved-token over-specification** (line 82 vs skill-management line 42). Genuine spec-internal contradiction that would produce spurious Criticals against valid skills; fix is a one-line spec edit, and the spec's own §Relationship already says the authoring spec wins.

#### Reclassifications / false positives flagged

- **All 5 `research-triangulate` Criticals → Warning**, and the 5 `portfolio-management` Criticals → Warning, and the `spec-drift-audit` MUST-violation Criticals → Warning: every cluster spec is `Status: draft`. Draft specs are in scope for the audit, but a draft spec's unimplemented MUST is a gap-to-close-on-promotion, not a merge-blocking Critical on a shipped artifact.
- **`spec-drift-audit` finding [9]** (auditor flagging its *own* MUST→Warning downgrades): meta-noise, not a repo gap. **False positive** for spec→impl drift.
- **`skill-review` reserved-token issue**: double-reported as both Warning and Critical for the same line 82 — collapse to one finding.
- **`portfolio-management` AC-8**: it obligates *continuous-improvement's future revision*, not portfolio-management's implementation — reclassified as a cross-spec wording item, not a portfolio impl gap.
- **`release-automation` reusable-internal Criticals**: target upstream `nolte/gh-plumbing@v1.1.19`, not files this repo owns — **not actionable in `claude-shared`** (consumer-facing). The v0.1.2 manual-publish finding is genuine but historical and already mitigated by R-2 going forward → Info.

COUNTS: genuine=11 false_positive=4 reclassified=6

## Wave-based implementation roadmap

This roadmap sequences only the **genuine** findings (after triage: false positives and reclassified-out items excluded). Effort is rough: S = single-file edit / one-liner, M = multi-file or judgement-bearing edit, L = multi-artefact cohort or spec-design work. spec_refs use the section/line anchors verified during triage.

### Wave 1 — Systemic structural fixes (one edit retires many findings)

These spec-level edits must land first: they re-baseline severities for the per-artefact waves below and prevent the largest false-positive/over-escalation classes from recurring.

**1A — Scope the Operations-vocabulary MUST in the skill-management spec.**
- spec_ref: `spec/claude/skill-management/en.md` §"Operations vocabulary" L108–116 (esp. L110, L113–114).
- Edit: state explicitly that the verb MUST (L113–114) binds the *set of named, dispatchable operations* a multi-operation skill exposes, and that a single-operation skill MAY use descriptive `### N. <step>` headings for its ordered procedure provided the operation is named with `run` (or its single closed-vocab verb) in frontmatter/intro.
- Retires: ~17 over-escalated Criticals (the case-(C) single-op runbooks: blog-author-trigger, dependency-audit, feature-decompose, mission-define, permission-allowlist-maintain, pull-request-create, pull-request-merge steps, quality-gate, release-notes-curate, release-publish-trigger, roadmap-init, roadmap-refine, sprint-plan, tech-stack-capture, vocab-drift-audit, workflow-health-triage).
- Artefacts touched: 1 spec file. Effort: **M**. Dependencies: none (gates Wave 2 ops-vocab triage).

**1B — Decide and (if needed) amend the closed verb vocabulary.**
- spec_ref: `spec/claude/skill-management/en.md` §"Operations vocabulary" L113–114 (L114 explicitly contemplates amending the list).
- Edit: evaluate adding recurrent portfolio verbs (`revise`, `scan`, `propose`, `render`, `bootstrap`, `validate`) to the closed list vs. forcing per-skill renames. The recurrence across multiple genuinely-multi-op skills indicates the list is under-sized.
- Retires/reshapes: converts many Wave-2 per-skill renames into "conformant as-is" or into a trivial list edit.
- Artefacts touched: 1 spec file. Effort: **M**. Dependencies: do jointly with 1A; **must precede** Wave 2 ops-vocab work (2A), since the verdict determines which renames are still required.

**1C — Clarify the third-person `description` MUST against its checked-in operationalization.**
- spec_ref: `spec/claude/skill-management/en.md` L46 (rule) + L47 (trigger-clause requirement); authoritative arbiter `scripts/validate_skills.py` L61, L189–196.
- Edit: add one sentence stating the rule targets grammatical *person* (first/second-person pronouns), that imperative-mood `Don't use…` / `Invoke when…` trigger/redirect clauses are conformant, and that `validate_skills.py` is the arbiter.
- Retires: all 11 third-person false positives. Validator already reports zero findings at b91b67b, so no code change is needed.
- Artefacts touched: 1 spec file. Effort: **S**. Dependencies: none (independent of 1A/1B).

**Wave 1 net:** 3 spec edits, all in `spec/claude/skill-management/en.md`, retiring ~28 over-escalated findings and one full false-positive class.

### Wave 2 — Per-artefact MUST (Critical) fixes not covered by Wave 1

Genuine Criticals on shipped artefacts. Grouped by theme.

**2A — Multi-operation verb-alignment pass (depends on 1B verdict).**
- spec_ref: `spec/claude/skill-management/en.md` §"Operations vocabulary" L113–115.
- Genuinely multi-op skills with non-vocab named operations: **audience-identify** (`validate`/`revisit`), **docs-dry-refactor** (`scan`/`propose`), **roadmap-plan** (5 modes), **sprint-execute** (5 ops), **sprint-review** (7 ops), **spec** (`Create`→`scaffold`, `Drift check`→`audit`, +others), **mermaid-diagrams-apply** (compound modes), **skill-management** (`Create`/`Revise`).
- Partials (one/few verbs off): **cookiecutter-template-manage** (`refactor`), **lektorat-apply** (`revise`), **portfolio-audit** (`Render`/`Bootstrap`/`Discover tech stack`), **project-structure-apply** (`GitHub App installation check`), **skill-agent-catalog-apply**, **github-issue-templates-apply**, **webview-ui-optimize** (`expert-review`), **yaml-json-schema**.
- Per-skill: rename non-conformant named operations to a vocab verb **or** rely on the 1B list amendment. Do not flatten informative runbooks.
- Artefacts touched: up to 15 SKILL.md files. Effort: **L**. Dependencies: **1B** (a list amendment may zero out many of these); **1A** (confirms which are truly multi-op vs. runbook).

**2B — Unambiguous heading-form deviations (independent of 1A/1B).**
- spec_ref: `spec/claude/skill-management/en.md` §"Operations vocabulary" L115 (`A./B./C.` and alphanumeric forms explicitly non-conformant).
- **mission-revise**: `### A./B./C.` → numbered. **pull-request-merge**: `### 7c.` → renumber. **skill-management**: `### Review / audit` (unnumbered, slash-compound) → numbered single verb.
- Artefacts touched: 3 files. Effort: **S**. Dependencies: none — fix now regardless of how 1A/1B resolve.

**2C — Agent governance: tool-list-vs-body & read-only Bash.**
- spec_ref: `spec/claude/agent-management/` §Tool access (the `tools` field is the enforcement point) + §Tool access narrow exception (read-only Bash justification).
- **portfolio-inflight-collector**: body L30 claims four tools but `tools: [Bash]` — reconcile. **portfolio-manifest-collector**: same defect, body L33 (raw Warning → **reclassified Critical**). **webview-ui-expert**: declares `Bash`, read-only, missing `## Read-only Bash justification` (body runs `git rev-parse` L86) — add the section. **spec-readiness-reviewer**: Option B (L179) writes `.audits/spec-readiness/<slug>.md` but `tools` omit `Write` and Hard rule L282 forbids any file creation — resolve the MUST-vs-MUST (drop Option B or add `Write` + amend Hard rule).
- Artefacts touched: 4 agent files. Effort: **M**. Dependencies: none.

**2D — Agent rationale-heading conformance.**
- spec_ref: `spec/claude/skill-vs-agent/` §Rationale section heading (MUST exact heading).
- **audience-doc-author**, **claude-plugin-developer**, **cookiecutter-template-author**: `## Rationale (why an agent, not a skill)` → `## Why this is an agent, not a skill`. **webview-ui-optimize** (skill): `## Rationale (why a skill, not just an agent)` → `## Why this is a skill, not an agent`.
- Artefacts touched: 4 files. Effort: **S**. Dependencies: none. (Could be folded into a Wave-1-style sweep, but it is a fixed-string substitution, not a spec edit.)

**2E — Agent spec-fidelity Criticals.**
- **code-security-reviewer**: step-3 template uses invented P0–P3 ↔ critical/high/medium/low; bound spec MUSTs verbatim Critical/Warning/Suggestion/Info (lines 92–100). Effort **S**.
- **audience-review**: body L34 `## German trigger phrases`; `distribution: plugin` MUST be English-only in body (spec_ref `agent-management` §Structure). Remove/relocate. Effort **S**.
- **diagram-opportunity-reviewer**: declares cap overrides as inputs (L65–66, L213); spec_ref §Volume control L61 is an explicit `MUST NOT expose the caps as invocation-time overrides`, and the agent falsely attributes them to §Open Questions (L103 has no such entry). Remove the override inputs and the false attribution. Effort **S**.
- Artefacts touched: 3 agent files. Effort: **S** each, **M** group. Dependencies: none.

### Wave 3 — SHOULD/Warning + Suggestion polish

Non-blocking. Can proceed in parallel once Waves 1–2 land.

**3A — `examples/` evaluation-scenario cohort (the one genuinely systemic SHOULD-gap).**
- spec_ref: `spec/claude/skill-management/en.md` §145 (≥3 scenarios under `examples/`).
- Cohort shipping zero `examples/`: **blog-author**, **docs-audience-tracks-apply**, **docs-dry-refactor**, **mkdocs-structure-apply**, **readme-structure-apply**, **webview-ui-optimize**. Scaffold 3 scenarios each; normalize the whole cohort to **Warning** (all six are non-trivial multi-step).
- Artefacts touched: 6 skill folders. Effort: **L**. Dependencies: none (single backlog item).

**3B — Boundary-matrix `dont_use_when` gaps.**
- spec_ref: `spec/claude/skill-management/` §Use-case metadata (and `agent-management` twin).
- **CC-1**: `portfolio-audit` add reverse `dont_use_when` → `portfolio-inflight-triage`. **CC-2**: `prose-vale-curator` add `dont_use_when` → `lektorat-apply`. **CC-3**: `continuous-improvement-triage` ships *no* `dont_use_when` despite being a four-way confusable hub (portfolio-audit / spec-drift-audit / skills-agents-sweep / workflow-health-triage) — add the field.
- Artefacts touched: 3 files. Effort: **S** (CC-1/CC-2), **M** (CC-3). Dependencies: none.

**3C — Load-trigger / file-reference phrasing one-offs.**
- spec_ref: `spec/claude/skill-management/en.md` §125.
- **agent-review** `templates/plan.template.md` (no `when`/`for` clause) → **Warning**. **audience-identify** `templates/audiences.template.md` and **continuous-improvement-triage** `templates/triage.template.md` → **Suggestion** (one-line wording). Corpus is otherwise solved (38/43 conformant).
- Artefacts touched: 3 files. Effort: **S**. Dependencies: none.

**3D — Phase-classification drift (catalog bucketing, SHOULD).**
- spec_ref: `spec/claude/skill-agent-catalog/en.md` §Phase classification L73 ("primary purpose, not the calling phase").
- **dependency-audit-scanner** (`review`→`quality`) and **vocab-drift-scanner** (`review`→`quality`): one-line frontmatter edits that also restore consistency with their `quality`-phase parent skills. (Genuine, **Suggestion**.) Build already fails on out-of-vocab values, so no new gate.
- Artefacts touched: 2 agent files. Effort: **S**. Dependencies: none.

**3E — Authoring-quality one-offs.**
- spec_ref: `spec/claude/skill-management/en.md` §99 (consistent terminology), §95 (Gotchas).
- **blog-author**: `Diataxis` → `Diátaxis` (L28, L78). **blog-author-trigger**: SKILL.md L120 "step 5" → "step 6" (authoritative `sprint-execute` SKILL.md L91); plus discretionary `## Gotchas` section. Body-prose drift in **sprint-execute** Gotchas (stale `Operation C/D` references). Length over-target items (docs-dry-refactor 157, release-publish-trigger 160) are §85 *soft*-target Suggestions — defer.
- Artefacts touched: 3–4 files. Effort: **S**. Dependencies: none.

**3F — Description bare-imperative opener consistency sweep (Suggestion).**
- spec_ref: `spec/claude/skill-management/en.md` L46 (style consistency only; never merge-blocking).
- Normalize bare-imperative openers (`Review…`, `Scan…`, `Decompose…`, `Create…`, `Promote…`, `Author or revise…`, `Scaffold`) to the `-s` third-person form on: **agent-review**, **dependency-audit**, **feature-decompose**, **pull-request-create**, **pull-request-merge**, **roadmap-init**, **skill-management**.
- Artefacts touched: ~7 files. Effort: **M**. Dependencies: **1C** (do after the spec clarification confirms these are Suggestion-grade, not violations).

**3G — Minor agent metadata nits (Suggestion/Info).**
- **png-to-transparent-svg** tag `scaffolding` misused for an image-conversion agent → pick an apt tag (spec_ref `agent-management` §Tag vocabulary, SHOULD). **lektorat-scanner** description typo `(use docs-freshness)` → `docs-freshness-checker` (L92). **mermaid-diagram-reviewer** description mis-attributes rendering verification to `docs-freshness-checker` (Info). **docs-audience-tracks-apply** `migrate` repeatedly mislabelled "greenfield" though spec defines it as brownfield→conforming (Warning, terminology).
- Artefacts touched: 4 files. Effort: **S**. Dependencies: none.

### Cross-cutting backlog (not waved — tracked separately)

These are genuine but either downstream/draft-spec gaps or domain-spec-fidelity items owned by other reviewers; they do not block the per-artefact waves.

- **Most actionable spec→impl gaps (mechanical, one-PR each):** `mkdocs-structure` floating plugin pins in `docs/requirements.txt` (all 7 `>=`, no lockfile); `docs-audience-tracks` 4-page audience↔track contradiction (`downstream-user` + `track: developer-docs` on index/nutzung EN+DE); `prose-style` Vale alert-level divergence (`.vale.ini` `suggestion` vs Taskfile `--minAlertLevel=error`); `docs-freshness` agent `## Scope` template missing `date`/`trigger`/`Git revision` (`agents/docs-freshness-checker.md` L91–95); `continuous-improvement` PR-traceability fields (add "dispatched specialist" + "originating finding source" to the `pull-request-create` template). All **Warning** (draft specs; would be Critical post-promotion).
- **Spec-internal contradictions needing a tie-breaker:** `skill-review` L82 reserved-token over-broadening vs `skill-management` L42 ("name only"); `review-plan` MUST-NOT-timestamps vs `portfolio-inflight-management` MUST `<YYYY-MM-DD>.md`. One-line spec edits.
- **Owed-but-unimplemented binding:** `spec/tools/gemini-image-generation/en.md` promises an in-repo `gemini-image-generate` skill/agent that does not exist (**Warning**, backlog item, not a conformance defect).
- **Draft-spec MUST gaps to close on promotion (not merge-blocking now):** `research-triangulate` (3 named skills lack triangulation language), `portfolio-management` (unbuilt `.audits/portfolio/` + docs subtree), `dependency-audit` skill-encoding gaps. All reclassified Critical→**Warning**.

**Sequencing summary:** Wave 1 (3 spec edits in skill-management) first — it re-baselines severities and gates 2A. Wave 2B/2C/2D/2E run in parallel immediately (independent of Wave 1); 2A waits on 1B. Wave 3 runs in parallel after Wave 2, except 3F which waits on 1C. The cross-cutting backlog is tracked independently and is not in the critical path.

## Processing log

2026-05-30—sweep-created—forward review of 69 artefacts + cross-cutting synthesis at b91b67b; 8 clusters triaged, 3 completeness critics passed (coverage 69/62, format clean, truthfulness 12/12)—verified by agent:full-spec-audit-pass-a + agent:full-spec-audit-pass-b
2026-05-30—per-artefact-plans-consolidated—69 per-artefact reviews inlined into Appendix A instead of 69 separate .audits/skill-review|agent-review/*.md plans, to honour the single-consolidated-report request; downstream working-off may still split any artefact back into its own review plan—verified by human:nolte (pending)

## Appendix A — Per-artefact findings (forward: artefact → spec)

_Raw post-dedup findings for all 69 artefacts (43 skills, 26 agents) at `b91b67b`. Totals: Critical=131, Warning=93, Suggestion=22, Info=11. See the executive summary and roadmap above for the genuine-versus-over-flagged triage._

### Inventory

| Artefact | Kind | C | W | S | I |
|---|---|--:|--:|--:|--:|
| `audience-doc-author` | agent | 1 | 0 | 1 | 0 |
| `audience-review` | agent | 2 | 1 | 0 | 0 |
| `claude-plugin-developer` | agent | 1 | 1 | 0 | 1 |
| `code-security-reviewer` | agent | 1 | 1 | 1 | 0 |
| `cookiecutter-template-author` | agent | 1 | 0 | 0 | 0 |
| `dependency-audit-scanner` | agent | 0 | 4 | 0 | 0 |
| `diagram-opportunity-reviewer` | agent | 3 | 1 | 0 | 0 |
| `docs-freshness-checker` | agent | 3 | 1 | 0 | 0 |
| `feature-consistency-reviewer` | agent | 0 | 0 | 0 | 0 |
| `graphic-prompt-generator` | agent | 2 | 2 | 0 | 0 |
| `i18n-completeness-checker` | agent | 0 | 3 | 1 | 1 |
| `lektorat-scanner` | agent | 0 | 0 | 1 | 0 |
| `mermaid-diagram-reviewer` | agent | 0 | 3 | 0 | 1 |
| `png-to-transparent-svg` | agent | 0 | 1 | 3 | 0 |
| `portfolio-inflight-collector` | agent | 1 | 1 | 2 | 0 |
| `portfolio-manifest-collector` | agent | 0 | 1 | 0 | 0 |
| `project-structure-reviewer` | agent | 1 | 5 | 0 | 0 |
| `prose-vale-curator` | agent | 0 | 1 | 1 | 0 |
| `quality-gate-enforcer` | agent | 2 | 3 | 0 | 0 |
| `roadmap-coherence-reviewer` | agent | 2 | 2 | 1 | 1 |
| `spec-readiness-reviewer` | agent | 2 | 2 | 1 | 0 |
| `sprint-readiness-reviewer` | agent | 2 | 2 | 0 | 1 |
| `tech-stack-drift-reviewer` | agent | 0 | 2 | 0 | 0 |
| `test-case-extractor` | agent | 3 | 1 | 0 | 0 |
| `vocab-drift-scanner` | agent | 0 | 1 | 0 | 0 |
| `webview-ui-expert` | agent | 1 | 2 | 0 | 0 |
| `agent-review` | skill | 0 | 3 | 0 | 0 |
| `audience-identify` | skill | 2 | 1 | 0 | 0 |
| `blog-author` | skill | 0 | 1 | 1 | 0 |
| `blog-author-trigger` | skill | 1 | 3 | 1 | 0 |
| `continuous-improvement-triage` | skill | 1 | 3 | 0 | 1 |
| `cookiecutter-template-manage` | skill | 2 | 0 | 0 | 0 |
| `dependency-audit` | skill | 6 | 2 | 0 | 0 |
| `docs-audience-tracks-apply` | skill | 2 | 2 | 0 | 0 |
| `docs-dry-refactor` | skill | 2 | 2 | 0 | 0 |
| `feature-decompose` | skill | 3 | 1 | 1 | 0 |
| `github-issue-templates-apply` | skill | 4 | 0 | 0 | 0 |
| `lektorat-apply` | skill | 2 | 0 | 1 | 0 |
| `mermaid-diagrams-apply` | skill | 4 | 1 | 1 | 2 |
| `mission-define` | skill | 4 | 0 | 0 | 0 |
| `mission-revise` | skill | 2 | 0 | 0 | 0 |
| `mkdocs-structure-apply` | skill | 1 | 2 | 1 | 0 |
| `permission-allowlist-maintain` | skill | 1 | 1 | 0 | 0 |
| `portfolio-audit` | skill | 3 | 1 | 0 | 0 |
| `portfolio-inflight-triage` | skill | 0 | 0 | 0 | 0 |
| `project-structure-apply` | skill | 1 | 0 | 0 | 0 |
| `pull-request-create` | skill | 4 | 1 | 0 | 0 |
| `pull-request-merge` | skill | 4 | 1 | 0 | 0 |
| `quality-gate` | skill | 2 | 1 | 0 | 0 |
| `readme-structure-apply` | skill | 0 | 3 | 1 | 1 |
| `release-notes-curate` | skill | 4 | 2 | 1 | 0 |
| `release-publish-trigger` | skill | 5 | 1 | 0 | 0 |
| `roadmap-init` | skill | 2 | 0 | 0 | 0 |
| `roadmap-plan` | skill | 1 | 4 | 0 | 0 |
| `roadmap-refine` | skill | 3 | 1 | 0 | 0 |
| `skill-agent-catalog-apply` | skill | 4 | 0 | 0 | 0 |
| `skill-management` | skill | 4 | 1 | 0 | 0 |
| `skill-review` | skill | 3 | 0 | 0 | 0 |
| `skills-agents-sweep` | skill | 1 | 2 | 0 | 0 |
| `spec` | skill | 4 | 1 | 0 | 0 |
| `spec-drift-audit` | skill | 4 | 3 | 0 | 0 |
| `sprint-execute` | skill | 2 | 1 | 0 | 1 |
| `sprint-plan` | skill | 2 | 2 | 0 | 1 |
| `sprint-review` | skill | 4 | 0 | 0 | 0 |
| `tech-stack-capture` | skill | 2 | 1 | 0 | 0 |
| `vocab-drift-audit` | skill | 2 | 0 | 1 | 0 |
| `webview-ui-optimize` | skill | 2 | 3 | 0 | 0 |
| `workflow-health-triage` | skill | 2 | 0 | 0 | 0 |
| `yaml-json-schema` | skill | 1 | 1 | 1 | 0 |

### Findings by artefact

#### `audience-doc-author` (agent)

**Critical**

- [ ] [skill-vs-agent.rationale-section-heading] The rationale section is headed `## Rationale (why an agent, not a skill)` but the spec MUST require exactly `## Why this is an agent, not a skill`; alternative phrasings are explicitly called out as non-conformant.
      Where: agents/audience-doc-author.md line 34.
      Fix: Rename the heading to `## Why this is an agent, not a skill` verbatim..
      Verify: grep -n '^## Why this is an agent, not a skill' agents/audience-doc-author.md returns exactly one match..

**Suggestion**

- [ ] [skill-vs-agent.rationale-documentation-form] The MUST in skill-vs-agent §Rationale documentation (line 89) prescribes 'one short paragraph or a two-to-four-bullet list'. The artefact's rationale section contains five bullets (lines 36-40), which exceeds the stated upper bound of four. Note: the commentary in line 91 makes clear the hard floor is one named dimension, so this is form drift rather than a blocking violation.
      Where: agents/audience-doc-author.md lines 36-40.
      Fix: Consolidate the five rationale bullets to at most four, merging thematically related points (for example, collapse 'Specialization' and 'Fire-and-forget lifecycle' into one bullet)..
      Verify: Count the bullets under the rationale section heading; the list must contain between two and four entries after the fix..

#### `audience-review` (agent)

**Critical**

- [ ] [agent-management.plugin-distribution-english-only] The body contains a dedicated `## German trigger phrases` section with three German-language bullet items. The spec MUST requires that `distribution: plugin` agents stay English-only in both description and body.
      Where: agents/audience-review.md lines 35–41 (`## German trigger phrases` section with bullet items `prüfe diese Zielgruppenliste`, `Audit der Zielgruppenanalyse`, `validiere das Zielgruppen-Artefakt`).
      Fix: Remove the German trigger phrases section from the body. The description already says 'equivalent German-language requests' as a routing hint, which is sufficient. German language support for the agent's *responses* is governed by the MAY clause and needs no body section..
      Verify: Grep the body for non-ASCII characters; confirm none remain outside code fences or quoted examples. Re-confirm the agent still routes correctly from German user requests via the description's 'equivalent German-language requests' phrase..

- [ ] [agent-management.english-only-plugin-body] Finding [0] was correctly identified as a genuine violation but assigned the wrong severity. The spec states a MUST (not a SHOULD) for English-only body in `distribution: plugin` agents. Per spec/claude/review-plan §Severity scale, a MUST violation is Critical, not Warning. The mis-classification means the finding would not block merge under the review-plan's deletion rule (which forbids deleting a plan while any Critical `- [ ]` item is open).
      Where: agents/audience-review.md lines 34-40 (`## German trigger phrases` section); spec/claude/agent-management §Structure line 33 (`distribution: plugin` MUST English-only body); spec/claude/review-plan §Severity scale line 58 (Critical = violates a MUST).
      Fix: Re-classify the existing finding [0] from Warning to Critical so the review plan correctly blocks merge until the German section is removed or relocated outside the agent body..
      Verify: Confirm the plan's `## Summary` shows `Critical: 1` and the finding carries `- [ ]` under `### Critical`; confirm the plan is not deletable until the `- [ ]` is closed..

**Warning**

- [ ] [skill-agent-catalog.phase-classification] The artefact declares `phase: plan`, but the spec SHOULD says to pick the earliest phase the artifact is *normally* invoked in. This agent is a read-only reviewer that audits an existing artefact — the `quality` or `review` phase more accurately reflects its primary function. `plan` is accurate only when it gates a downstream planning step, not for the review activity itself.
      Where: agents/audience-review.md line 7 (`phase: plan`).
      Fix: Consider changing `phase` to `quality` (audit / compliance check) or `review` (if the primary context is pre-PR gate review). `quality` is the better fit given the agent performs drift/compliance checking..
      Verify: Confirm the peer agents in the `audience` tag cluster (`audience-doc-author`, etc.) and the catalog's `quality` or `review` index render this agent alongside functionally similar review/audit artifacts..

#### `claude-plugin-developer` (agent)

**Critical**

- [ ] [skill-vs-agent.rationale-section-heading] The rationale section heading reads `## Rationale (why an agent, not a skill)`. The spec states agents MUST use exactly `## Why this is an agent, not a skill`; it explicitly lists `## Rationale (why an agent, not a skill)` as a non-conformant alternative phrasing.
      Where: /home/nolte/repos/github/claude-shared/agents/claude-plugin-developer.md, line 41.
      Fix: Rename the heading from `## Rationale (why an agent, not a skill)` to `## Why this is an agent, not a skill`. Preserve the bullet content as-is..
      Verify: grep -n '^## Why this is an agent, not a skill' agents/claude-plugin-developer.md should return exactly one match at the section that currently contains the agent-bias bullets..

**Warning**

- [ ] [agent-management.tool-access] The `## Read-only Bash justification` section claims the spec's narrow read-only-agent exception for Bash. That exception applies exclusively to read-only agents that MUST NOT declare `Write`, `Edit`, or `NotebookEdit`. This agent declares `Write` and `Edit` and is not a read-only agent; the exception is therefore inapplicable. Using the exception-section name misleads reviewers and automated validators (the spec states agent-review honours the exception when the section is present), creating a false impression that the agent is constrained to read-only Bash when it is not.
      Where: /home/nolte/repos/github/claude-shared/agents/claude-plugin-developer.md, lines 33-39.
      Fix: Rename the section to something that does not claim the read-only narrow exception, for example `## Bash usage rationale`. Rewrite the body to explain that Bash is used solely for `task lint` because no dedicated tool covers it, and that all other write operations are handled by the explicitly declared `Write` and `Edit` tools. Remove the phrasing that references §Read-only-agent narrow exception..
      Verify: Confirm the section no longer references the 'read-only-agent narrow exception' and that the heading `## Read-only Bash justification` is absent. Confirm the agent still declares `Bash` in frontmatter `tools` alongside `Write` and `Edit`..

**Info**

- [ ] [agent-management.structure] The `name` field contains the reserved token `claude` (`claude-plugin-developer`). The artefact correctly carries the required `## Reserved-token rationale` section explaining the platform-surface exception, and the body notes that the local validator honours the exception while the upstream Anthropic platform validator does not. This is conformant under the narrow exception clause; noted for completeness.
      Where: /home/nolte/repos/github/claude-shared/agents/claude-plugin-developer.md, lines 1 and 29-31.
      Fix: No action required. The exception is properly documented..
      Verify: Confirm the section heading `## Reserved-token rationale` is present and names the platform surface (nolte-shared plugin authoring). Confirm the validator exception behaviour is documented..

#### `code-security-reviewer` (agent)

**Critical**

- [ ] [spec/project/code-security-audit.output.severity-vocabulary] The agent's Step 3 report template uses a P0/P1/P2/P3 scale with labels 'critical', 'high', 'medium', 'low / hardening' — an invented scale. The bound spec MUST NOT invent a P0–P3 or critical/high/medium/low scale and MUST use the portfolio-wide vocabulary Critical / Warning / Suggestion / Info (verbatim Title Case) from spec/claude/review-plan/ §Severity scale.
      Where: agents/code-security-reviewer.md lines 92–100 (Step 3 report template: '## P0 — critical', '## P1 — high', '## P2 — medium', '## P3 — low / hardening') and line 108 ('Sort by severity (P0 → P3)')..
      Fix: Replace the four P0–P3 severity headings with '## Critical', '## Warning', '## Suggestion', '## Info' (Title Case, matching spec/claude/review-plan/ §Severity scale). Update the sort instruction on line 108 to 'Sort by severity (Critical → Info)'. The per-finding 'Confidence' field for confirmed/suspected can be retained — it is not a severity classification..
      Verify: grep the agent body for 'P0\|P1\|P2\|P3\|— high\|— medium\|— low' and confirm no matches remain. Confirm '## Critical', '## Warning', '## Suggestion', '## Info' headings appear in the template..

**Warning**

- [ ] [spec/claude/agent-management.recommendations] The agent body is 117 lines, which is well within the ~200-line guideline, but the Step 3 report template (lines 77–108) hard-codes the forbidden P0–P3 scale as its only illustrative output shape. Even after correcting the severity labels (Finding [0]), the template should model the required Critical / Warning / Suggestion / Info headings so future consumers have a correct reference. Without an updated template the procedural instruction at line 77 ('Emit a single severity-classified report') contradicts the example that follows it, creating an authoring ambiguity.
      Where: agents/code-security-reviewer.md lines 92–100: severity section headings '## P0 — critical', '## P1 — high', '## P2 — medium', '## P3 — low / hardening'.
      Fix: Replace the four ## P-level headings and the 'Sort by severity (P0 → P3)' instruction with the portfolio vocabulary: '## Critical', '## Warning', '## Suggestion', '## Info', and update line 108 to 'Sort by severity (Critical → Info)'. This is the corrective action entailed by Finding [0] but must also be applied to the procedural text to keep the instruction and the template consistent..
      Verify: Grep agents/code-security-reviewer.md for 'P0\|P1\|P2\|P3\|critical\|high\|medium\|low / hardening' — all occurrences in the severity-heading context should be gone, replaced by Critical / Warning / Suggestion / Info verbatim..

**Suggestion**

- [ ] [spec/claude/agent-management.tags.starter-vocabulary] The tags field includes 'security', which is not in the starter vocabulary defined by spec/claude/agent-management/ §Tag vocabulary. The spec SHOULD prefers starter-vocabulary terms when one applies. The existing tags 'review' and 'audit' already classify this agent; 'security' adds specificity but introduces a term outside the shared vocabulary that won't align with cluster-level catalog groupings.
      Where: agents/code-security-reviewer.md line 7: tags: [review, audit, security].
      Fix: Either remove 'security' (the agent is already covered by 'review' and 'audit') or, if 'security' is genuinely needed as a cluster signal, propose adding it to the starter vocabulary in spec/claude/agent-management/ so peer artifacts (dependency-audit-scanner, etc.) can share the tag consistently..
      Verify: grep agents/ skills/ for 'security' in tags fields; confirm either all security-class artifacts share the tag or the tag is removed from this agent..

#### `cookiecutter-template-author` (agent)

**Critical**

- [ ] [skill-vs-agent.rationale-section-heading] The rationale section heading is `## Rationale (why an agent, not a skill)`. The spec mandates the heading to be exactly `## Why this is an agent, not a skill`; any other phrasing is explicitly declared non-conformant.
      Where: /home/nolte/repos/github/claude-shared/agents/cookiecutter-template-author.md, line 28.
      Fix: Rename the heading from `## Rationale (why an agent, not a skill)` to `## Why this is an agent, not a skill`. Additional sub-headings (e.g. `## Why this is one agent across four modes`) MAY be kept alongside the mandatory heading..
      Verify: grep -n 'Why this is an agent, not a skill' agents/cookiecutter-template-author.md should return exactly one match at the renamed line..

#### `dependency-audit-scanner` (agent)

**Warning**

- [ ] [skill-agent-catalog.phase-classification] The agent declares `phase: review` but its primary responsibility is running vulnerability scans and producing a CVE inventory. The phase vocabulary defines `quality` as covering "audits, scans, lint/typecheck/test gates, drift detection" and `review` as "moves change toward develop through reviewed pull requests". This misclassification places the agent in the wrong phase bucket in the catalog index and breaks consistency with its parent `dependency-audit` skill, which correctly declares `phase: quality`.
      Where: Frontmatter, line 8: `phase: review`.
      Fix: Change `phase: review` to `phase: quality` in frontmatter..
      Verify: Confirm frontmatter reads `phase: quality`; run `task docs` and verify the agent appears under the Quality phase heading in the Agents catalog index, alongside the `dependency-audit` skill..

- [ ] [agent-management.recommendations] The spec SHOULD-requires that audit/review agents close with an explicit caller follow-ups / handoff section. The agent body ends with `## Hard rules`, which contains handoff intent scattered in prose ("The inventory is the output; everything else belongs to the dependency-audit skill"), but there is no dedicated headed section that surfaces the handoff contract for a caller at a glance.
      Where: Agent body — last H2 is `## Hard rules` (line 177); no `## Caller handoff` or equivalent section exists..
      Fix: Add a short `## Caller handoff` section (or similarly named) after `## Hard rules` that explicitly states: the agent returns the CVE inventory and stops; the calling `dependency-audit` skill owns all follow-up steps (severity triage, bump authoring, PR drafting)..
      Verify: Grep the body for a H2 containing "handoff" or "caller"; confirm it names the `dependency-audit` skill as the follow-up owner..

- [ ] [agent-management.tag-vocabulary] The agent declares only `tags: [audit]`. The starter vocabulary defines a second applicable tag `dependency` with the description "CVE scans, license compliance, lockfile hygiene" — exactly this agent's domain. Declaring `dependency` alongside `audit` would place the agent in the correct peer cluster (visible in the tag index alongside other CVE/lockfile artifacts) and give the catalog generator a richer routing signal.
      Where: Frontmatter, line 7: `tags: [audit]`.
      Fix: Change to `tags: [audit, dependency]` (two entries, both from the starter vocabulary, well within the five-entry limit)..
      Verify: Run `task docs` and confirm both `audit` and `dependency` tags appear on the agent's catalog page and in the tag index..

- [ ] [agent-management.recommendations] The spec SHOULD-requires that the system prompt begin with role/boundaries, then expected output format, then working procedure. The agent inserts two substantial sections — `## Why this is an agent, not a skill` and `## Read-only Bash justification` — between the opening role paragraph and `## Output shape`, deferring the output format to line 71 of the body. The structural ordering deviates from the prescribed sequence.
      Where: Agent body structure: `## Output shape` appears as the fifth H2 (after `## Why this is an agent, not a skill`, `## Read-only Bash justification`, `## Scope and boundaries`), not immediately after the role/boundaries opening paragraph..
      Fix: Reorder sections so the output contract (`## Output shape`) appears directly after the opening role/boundaries paragraph, before the rationale and justification sections. The `## Read-only Bash justification` section (MUST-required but position-unspecified) can follow the output shape..
      Verify: Confirm the body order is: (1) role/boundaries paragraph, (2) `## Output shape`, (3) `## Inputs`, (4) `## Preconditions`, (5) `## Working procedure`, with rationale and Bash-justification sections placed after the output contract..

#### `diagram-opportunity-reviewer` (agent)

**Critical**

- [ ] [diagram-opportunity.volume-control] The agent advertises per-file and per-run cap overrides as accepted inputs, directly violating the spec's MUST NOT. §Volume control line 61 states: 'MUST NOT expose the caps as invocation-time overrides; the defaults (3 per file, 15 per run) are the only supported values.' The agent's §Inputs section (lines 65–66) declares 'Per-file cap override (integer)' and 'Per-run cap override (integer)' as optional caller inputs, and §Volume control (line 213) reads 'When the caller passes per-file or per-run cap overrides via input, honour them.' The agent also falsely claims (line 65) that 'the spec's §Open Questions notes that overrides are a future-question'; the spec's Open Questions section contains no such entry and instead carries an explicit MUST NOT.
      Where: /home/nolte/repos/github/claude-shared/agents/diagram-opportunity-reviewer.md lines 65–66 (§Inputs) and line 213 (§Volume control).
      Fix: Remove the 'Per-file cap override' and 'Per-run cap override' optional-input entries from §Inputs. Remove the 'When the caller passes per-file or per-run cap overrides via input, honour them' clause from §Volume control. Replace with a statement that the caps are fixed portfolio-wide at 3/15 and cannot be overridden by the caller; operators who need the complete set read `full_findings`. Remove the false Open Questions attribution..
      Verify: Grep the agent body for 'cap override', 'per-file cap', 'per-run cap', and confirm no override-accepting language survives. Confirm that §Volume control states only the fixed 3/15 defaults. Confirm §Inputs has no optional cap-override entry..

- [ ] [diagram-opportunity.trigger-diagram-type-catalog] The agent does not implement the §Structural anti-patterns MUST. The spec (line 47) requires: 'MUST demote to low confidence (and thus discard per §Confidence model) any candidate match whose triggering passage is wholly contained in a recognized non-diagram structure: FAQ question-and-answer pairs, fenced command / install sequences, and flat error-message bullet lists.' The agent body has no mention of these three structural anti-pattern classes, no demotion rule, and no closed deny-list for well-known false-positive patterns. This omission means the agent will emit findings from FAQ blocks, install sequences, and error-message bullet lists that the spec requires to be silently discarded.
      Where: /home/nolte/repos/github/claude-shared/agents/diagram-opportunity-reviewer.md — no section covers structural anti-patterns.
      Fix: Add a §Structural anti-patterns section after the diagram-type catalog entries. The section must state that any candidate match whose triggering passage is wholly contained in an FAQ Q&A pair, a fenced command/install sequence, or a flat error-message bullet list MUST be demoted to low confidence (and therefore discarded before emission). Explain that this is the closed deterministic deny-list; the per-site mute marker is the operator's explicit override for all other cases..
      Verify: Confirm the new section names all three anti-pattern classes explicitly and uses MUST-level language for the demotion. Confirm a test against an FAQ block, a fenced install sequence, and an error-message bullet list produces zero emitted findings..

- [ ] [diagram-opportunity.per-site-mute-marker] The agent narrows the mute-marker suppression scope for paragraph-level markers below what the spec's MUST requires. The spec (line 73) states suppression runs 'until the next heading of equal or higher level' regardless of whether the marker precedes a heading or a paragraph. The agent (line 184) splits into two cases and for the paragraph case states 'the suppression covers exactly that one paragraph and stops at the next blank line.' Stopping at a blank line is substantially more restrictive than stopping at the next heading of equal or higher level, so the agent will generate findings from prose that the spec says must be suppressed.
      Where: /home/nolte/repos/github/claude-shared/agents/diagram-opportunity-reviewer.md lines 182–185 (§Mute-marker handling — Scope of suppression).
      Fix: Replace the two-case split with the unified spec rule: a mute marker on the line immediately preceding a heading or paragraph suppresses any finding that would originate from that heading/paragraph and its enclosed prose until the next heading of equal or higher level (or end of file). For a marker before a paragraph (not a heading), 'enclosed prose' extends through all subsequent paragraphs and sub-sections until a heading of equal or higher level is encountered — not just to the next blank line..
      Verify: Author a test passage where a mute marker precedes a paragraph followed by two further paragraphs before the next same-level heading. Confirm all three paragraphs produce no suggestion-severity findings and each produces one info-severity finding, not just the immediately-following paragraph..

**Warning**

- [ ] [agent-management.recommendations] The agent's system-prompt body is approximately 360 lines (lines 24–382), which is roughly 180 % over the ~200-line SHOULD guidance in §Recommendations: 'SHOULD keep the system prompt focused; if it grows past roughly 200 lines, tighten the prose rather than splitting it out.' Large sections (§Gotchas, the full JSON example in §Output shape, and the verbatim §Hard rules list) duplicate material already expressed in earlier prose sections, inflating the body without adding precision.
      Where: /home/nolte/repos/github/claude-shared/agents/diagram-opportunity-reviewer.md — full body, ~360 lines.
      Fix: Tighten the body by consolidating §Hard rules (largely restates §Scope and boundaries), shortening §Gotchas to the two or three non-obvious cases not already covered by earlier sections, and abbreviating the JSON output-shape example to the minimal shape that illustrates the schema rather than repeating every field's semantics inline. Target ~200–220 lines..
      Verify: Re-count body lines after revision; confirm no MUST-level rule is removed, only duplicated prose is collapsed..

#### `docs-freshness-checker` (agent)

**Critical**

- [ ] [docs-freshness.audit-artifact-must-fields] The agent's output shape (## Scope, ## Summary, ## Health, ## Caller follow-ups) omits three mandatory fields required in every persisted audit artifact: the run date, the trigger (quarterly / pre-release / PR-change), and the Git revision audited. The spec's §Audit artifact MUST says the artifact must include "date, trigger (quarterly, pre-release, PR-change), the repo root and mkdocs.yml path used, which categories were run (or narrowed out), the Git revision audited, the per-category severity counts, and the full finding list sorted by severity".
      Where: /home/nolte/repos/github/claude-shared/agents/docs-freshness-checker.md lines 88–189 (## Output shape template) and lines 192–205 (## Inputs / ## Preconditions).
      Fix: Add a `## Scope` sub-field (or extend the existing `## Scope` block) for `Date:`, `Trigger:`, and `Git revision:` in the report template. Additionally instruct the agent in ## Hard rules or ## Inputs to save the completed report to `.audits/docs-freshness/<YYYY>-Q<n>.md` (outside `docs_dir`) per the MUST-persist requirement in `spec/project/docs-freshness/` §Audit artifact..
      Verify: The output-shape template and the hard rules both mention date, trigger, Git revision, and the `.audits/docs-freshness/` save path. Grep the body for `git rev-parse HEAD` or equivalent instruction for capturing the audited revision..

- [ ] [docs-freshness.audit-artifact-persist] The agent produces an in-conversation report but never instructs itself to write or commit the result to `.audits/docs-freshness/<YYYY>-Q<n>.md`. The spec §Audit artifact MUST says every full audit result must be persisted as a commit, issue, or file in the repository, and it MUST live outside the MkDocs `docs_dir`.
      Where: /home/nolte/repos/github/claude-shared/agents/docs-freshness-checker.md — ## Hard rules (lines 323–333) and ## Caller follow-ups (lines 184–189): no save/write step described anywhere in the body.
      Fix: Add a final working-procedure step (e.g. Phase 9 or a step in ## Hard rules) directing the agent to write the completed report to `.audits/docs-freshness/YYYY-Qn.md` — or, given the read-only `tools` list (no Write/Edit), document that writing the artifact is the caller's responsibility and add a Caller follow-up: "Save this report to `.audits/docs-freshness/<YYYY>-Q<n>.md` to satisfy the docs-freshness spec's audit-trail requirement." Note: since Write/Edit are not in `tools`, the agent cannot write the file itself; the output shape should be clear that the caller must commit it..
      Verify: Either (a) `Write` appears in `tools` and the body directs the agent to write the artifact, or (b) the ## Caller follow-ups section explicitly names the `.audits/docs-freshness/` path and the save-outside-docs_dir requirement..

- [ ] [docs-freshness.categories-adr-index-skip-generated] The spec §Categories of drift states: 'When adr/index.md is generated (declared by a generator hook or a frontmatter marker such as `last_updated: generated` ...), the ADR-index-drift check MUST skip it.' The agent's Phase 5 ADR hygiene procedure (lines 248–256) checks `adr/index.md` for completeness but does not include the skip condition for generated indices.
      Where: /home/nolte/repos/github/claude-shared/agents/docs-freshness-checker.md lines 248–256 (### Phase 5: ADR hygiene).
      Fix: Add a guard at the start of Phase 5: before checking `adr/index.md`, read its frontmatter; if `last_updated: generated` is declared, skip the index-drift check for that file and note it in the report as 'ADR index is generator-maintained — skip per spec/project/docs-freshness/'..
      Verify: Phase 5 contains a guard condition that reads the `last_updated` frontmatter key of `adr/index.md` and skips the index-drift check when the value is `generated`..

**Warning**

- [ ] [agent-management.recommendations-body-length] The agent body is 333 lines, well past the ~200-line SHOULD guideline from `agent-management` §Recommendations. This is a soft local `nolte-shared` convention, not a MUST, but the body has grown primarily through the detailed phase-by-phase working procedure and inline output-shape template; inlining these is intentional and defensible, but the deviation from the guideline is not noted.
      Where: /home/nolte/repos/github/claude-shared/agents/docs-freshness-checker.md — entire body (333 lines).
      Fix: Add a sentence in ## Why this is an agent, not a skill acknowledging the ~200-line guideline and citing the reason for the inline working procedure (e.g. the multi-phase procedure and output template are load-bearing for correctness and can't be placed outside the agents/ tree without recursive-discovery risk)..
      Verify: The rationale section or a body comment explains why the body exceeds ~200 lines..

#### `feature-consistency-reviewer` (agent) — clean

#### `graphic-prompt-generator` (agent)

**Critical**

- [ ] [graphic-prompt-authoring.prompt-document-output-create-directory] The graphic-prompt-authoring spec MUST requires the agent to create the configured design-prompts directory if it does not exist, and explicitly states it is 'an output location, not a precondition.' The agent body never instructs directory creation — Phase 3 simply writes under the directory without any mkdir or directory-creation step, and the Write effects section lists brand sources (not the directory) as the only precondition.
      Where: agents/graphic-prompt-generator.md §Phase 3 (lines 86-120) and §Write effects (lines 54-58).
      Fix: Add an explicit step in Phase 3 (or in Phase 0/precondition prose) instructing the agent to create the configured design-prompts directory if it does not exist before writing prompt documents. Update the Write effects / Preconditions section accordingly to clarify the directory is auto-created, not a precondition..
      Verify: The agent body contains explicit direction to create the directory when absent; the Preconditions section no longer implies the directory must pre-exist..

- [ ] [graphic-prompt-authoring.prompt-document-output-create-directory] The graphic-prompt-authoring spec §Prompt document output (line 54) MUST NOT places prompt documents under the docs/ tree, which is reserved for published audience-facing pages. The agent body never states or enforces this restriction — neither Phase 3 (lines 86-120), the Write effects section (lines 54-58), nor the Scope and boundaries section (lines 40-48) mention the docs/ prohibition.
      Where: agents/graphic-prompt-generator.md — entire agent body; the restriction is absent from §Write effects (lines 54-58), §Phase 3 (lines 85-120), and §Scope and boundaries (lines 40-48).
      Fix: Add an explicit prohibition in the Write effects section and in Phase 3: 'MUST NOT write prompt documents under the docs/ tree, which is reserved for published audience-facing pages.'.
      Verify: Search the agent body for 'docs/' — it produces no results. The spec line 54 states the restriction as a MUST paired with the directory-creation MUST in the same bullet. Grep the spec: 'MUST NOT place prompt documents under the docs/ tree'..

**Warning**

- [ ] [corporate-design-colors.ai-image-color-contract-sref-equivalent] The agent body (line 67) allows 'a fixed reference image or a canonical style paragraph' as the per-model style-reference equivalent for sref-less generators (e.g. Gemini). The corporate-design-colors spec MUST defines this equivalent as a fixed canonical reference image only, and explicitly forbids free-text style paragraphs because they drift between runs. The graphic-prompt-authoring spec MUST defers to that contract without re-deciding it.
      Where: agents/graphic-prompt-generator.md line 67: 'a fixed reference image or a canonical style paragraph'.
      Fix: Remove 'or a canonical style paragraph' from line 67, leaving only 'a fixed reference image' as the per-model equivalent. Update the Style reference template line (line 97) to say 'sref code or per-model canonical reference image identifier' if needed for clarity..
      Verify: grep 'style paragraph' agents/graphic-prompt-generator.md returns no results; line 67 references only a fixed reference image as the Gemini-equivalent alternative to --sref..

- [ ] [agent-management.use-case-metadata-shoulddeclare] The description mentions three 'don't use' scenarios (actually generate the image, clean a PNG background, define the brand color system) but dont_use_when covers only one (PNG cleanup). agent-management SHOULD says to declare dont_use_when whenever overlap with other agents is likely; the two uncovered cases lose the catalog auto-link and scannable-section rendering that structured dont_use_when entries would provide.
      Where: agents/graphic-prompt-generator.md frontmatter dont_use_when list (line 14-17); description negative cases (line 3).
      Fix: Add two more dont_use_when entries: one for 'you want to actually generate the image' (no alternative agent to link — note it is a downstream tool, not a plugin artifact) and one for 'you want to define or modify the brand color system' (alternative: the design tokens spec or the relevant token-authoring agent once it exists). For the image-generation case, if no resolvable alternative exists yet, the situation alone still documents the boundary..
      Verify: The dont_use_when list contains at least three entries covering PNG cleanup, image generation, and brand color definition; every alternative value resolves to a discoverable artifact or is omitted (situation-only entries are valid when no resolvable alternative exists)..

#### `i18n-completeness-checker` (agent)

**Warning**

- [ ] [i18n-completeness.output-side-effects] The spec MUST requires: 'state, where it reports placeholder-parity findings, that parity is checked at simple-placeholder granularity ({{var}} / {var} / %s) and that ICU MessageFormat plural and select bodies are treated as opaque strings.' The agent body mentions placeholder parity in Step 4 and Quality rule 1-5, but never instructs the agent to include this disclosure in the emitted report. The report template (Step 5) and the Quality rules section both omit the required per-finding disclosure about ICU body treatment.
      Where: /home/nolte/repos/github/claude-shared/agents/i18n-completeness-checker.md lines 74-75 (Step 4) and lines 111-116 (Quality rules) — ICU disclosure absent from both the report template and the quality rules..
      Fix: Add a quality rule (e.g. rule 6) that explicitly states: 'Placeholder-parity findings carry a note that parity is checked at simple-placeholder granularity ({{var}} / {var} / %s) and that ICU MessageFormat plural and select bodies are treated as opaque strings, not structurally validated.' Mirror this in the report template's Info section or as a footer note..
      Verify: After the fix, grep the agent body for 'ICU' and 'opaque'; confirm at least one instance appears in the report-output section or quality-rules section, not only in the procedure step..

- [ ] [i18n-completeness.audit-dimensions] The spec MUST requires: 'treat each independent locale tree (per package / subroot) as a separate audit scope and never merge keys across trees.' The agent body makes no mention of monorepo or multi-locale-tree scenarios. Step 1 (Discover inputs) describes locating one conventional locale tree and one reference locale; there is no instruction to iterate over multiple independent trees or compute per-tree results separately.
      Where: /home/nolte/repos/github/claude-shared/agents/i18n-completeness-checker.md lines 55-60 (Step 1 — Discover inputs) — no multi-tree handling..
      Fix: In Step 1, add: 'When multiple independent locale trees exist (e.g. per package in a monorepo), treat each tree as a separate audit scope — discover, reference-locale-determination, and report run independently per tree; never merge keys across trees.' Update the report scope line (Step 5) to emit one scope header per tree when more than one is found..
      Verify: After the fix, confirm Step 1 explicitly names per-tree isolation and Step 5's report template handles multiple scopes..

- [ ] [i18n-completeness.inputs-discovery] The spec declares a MAY for reading an optional `project/i18n-audit.yml` config file, but its associated MUST states: 'The report MUST state, per resolved input, whether the value came from the config file, an operator argument, or discovery.' The agent body is entirely silent on the optional config file and on per-input provenance reporting in the emitted report. Omitting the provenance statement violates the MUST even if supporting the config file itself is optional.
      Where: /home/nolte/repos/github/claude-shared/agents/i18n-completeness-checker.md line 80 (report scope header) and lines 55-60 (Step 1) — no config-file reference, no input-provenance instruction..
      Fix: In Step 1, add a sentence: 'When a `project/i18n-audit.yml` file is present, its values take precedence over discovery; absent the file, per-invocation discovery is the default.' In Step 5's scope header, instruct the agent to annotate each resolved input (locale dir, reference locale, source roots, patterns) with its provenance: config file, operator argument, or discovery..
      Verify: After the fix, the report template's scope line shows a per-input provenance annotation (e.g. 'reference locale: de [from config]') and Step 1 mentions the optional config file..

**Suggestion**

- [ ] [agent-management.resumable-runs] The spec SHOULD NOT for fire-and-forget read-only agents that are cheap to restart. This agent correctly omits `resumable: true`. The body also lacks an explicit statement acknowledging this, but the spec only requires such acknowledgement when resumable is set. No action is strictly required; adding a brief one-liner noting 'resumable: false is intentional — single read-only pass, cheap to restart' in the body would make the design decision explicit for future reviewers.
      Where: /home/nolte/repos/github/claude-shared/agents/i18n-completeness-checker.md frontmatter (no resumable field) — the omission is correct but undocumented..
      Fix: Optionally add a comment in the body such as: 'This agent is not resumable (no `resumable: true`) because it is a single-shot read-only pass with no intermediate artefacts; restarting is cheaper than checkpointing.'.
      Verify: No action required for conformance; this is a documentation suggestion only..

**Info**

- [ ] [skill-agent-catalog.use-case-metadata] The `dont_use_when` field uses the correct mapping shape (`situation` + `alternative`) and the `alternative` value `webview-ui-expert` resolves to an existing agent at `agents/webview-ui-expert.md`. The `see_also` field also references `webview-ui-expert` which resolves. Both fields are within entry and character limits. This is a conformance confirmation.
      Where: /home/nolte/repos/github/claude-shared/agents/i18n-completeness-checker.md lines 14-18 (dont_use_when and see_also)..
      Fix: No action needed..
      Verify: Run `task docs` and confirm the docs build does not fail on unresolvable `alternative` or `see_also` references..

#### `lektorat-scanner` (agent)

**Suggestion**

- [ ] [agent-management.description-quality] The `description` prose ends with '(use docs-freshness)' but the actual artifact name is `docs-freshness-checker`. A reader following the description's negative-trigger advice would search for an artifact that does not exist under that name.
      Where: /home/nolte/repos/github/claude-shared/agents/lektorat-scanner.md, line 3 — `description` field, final clause: 'to detect cross-language parity drift (use docs-freshness)'.
      Fix: Replace 'docs-freshness' with 'docs-freshness-checker' to match the artifact's canonical `name` field. The structured `dont_use_when.alternative` already uses the correct name; align the prose description with it..
      Verify: grep 'docs-freshness' agents/lektorat-scanner.md should show only 'docs-freshness-checker' after the fix..

#### `mermaid-diagram-reviewer` (agent)

**Warning**

- [ ] [mermaid-diagrams.mkdocs-setup] The agent's Surface 1 audit omits the spec MUST that brand Mermaid theme variables MUST NEVER be injected via per-diagram `%%{init: {'theme': …, 'themeVariables': …}}%%` directives. The spec's §MkDocs setup lists five MUST rules; the agent maps only four (superfences, pymdown-extensions version pin, material theme, no mermaid2 plugin). The fifth — detecting the forbidden per-diagram `%%{init:…}%%` directive — is absent from both Surface 1 and Surface 3.
      Where: agents/mermaid-diagram-reviewer.md lines 122–127 (Surface 1 — MkDocs setup bullet list).
      Fix: Add a fifth bullet to Surface 1: any Mermaid block that opens with `%%{init: …}%%` on its first line is an `authoring-violation` finding (severity: warning, rule: per-diagram-theme-init). Also add `per-diagram-theme-init` to the Hard Rules' permitted finding vocabulary..
      Verify: After the fix, grep a test markdown file containing `%%{init: {'theme': 'forest'}}%%` before a mermaid fence and confirm the agent emits an `authoring-violation` finding for the rule..

- [ ] [mermaid-diagrams.authoring-rules] The spec's §Authoring rules states diagrams MUST be placed inline in a markdown file under `docs/<lang>/`, never in a separate `.mmd` source file. The agent scans `docs/<lang>/` for fences but never globs for `*.mmd` files in the repository. A repo that stores diagrams as standalone `.mmd` files would receive a clean report despite a spec MUST violation.
      Where: agents/mermaid-diagram-reviewer.md lines 129–137 (Surface 2 definition) and line 166 (Hard Rules — scan boundary).
      Fix: Add a Glob for `**/*.mmd` (excluding gitignored paths) to the investigation surface. Any hit is a `setup-drift` finding (severity: warning, target: `<path>.mmd`, resolution: `align-mkdocs move-inline`). Alternatively, classify it as `authoring-violation` (rule: mmd-source-file) and add the new rule to Surface 3 and the Hard Rules vocabulary..
      Verify: Place a dummy `docs/en/example.mmd` in a test repo and confirm the agent emits a finding instead of a clean run..

- [ ] [mermaid-diagrams.mkdocs-setup] Surface 1 maps the fifth MUST (no per-diagram %%{init:…}%% directive) to zero audit checks, and Surface 3 also omits it. Because the directive appears inside individual Mermaid blocks (not only in mkdocs.yml), the check belongs in Surface 3 as well as Surface 1 — a per-diagram %%{init: {'theme': …}}%% inside a fenced block in docs/<lang>/ is an authoring violation that the agent currently has no rule to detect.
      Where: agents/mermaid-diagram-reviewer.md lines 139–148 (Surface 3 authoring-rules list) — no rule for per-diagram %%{init:…}%% blocks; spec/project/mermaid-diagrams/en.md line 43.
      Fix: Add an authoring-violation rule to Surface 3: 'The block MUST NOT open with a %%{init: {…}}%% directive (per-diagram theme injection). A hit is an authoring-violation finding (severity: warning, rule: per-diagram-init-directive).' Also add the check to Surface 1's severity-assignment table and to the Severity assignment section (line 156–158) so the new rule:severity pairing is explicit..
      Verify: After adding the rule, confirm that a test Mermaid block starting with `%%{init: {'theme': 'base'}}%%` inside docs/<lang>/ is flagged as authoring-violation with rule per-diagram-init-directive..

**Info**

- [ ] [agent-management.description] The `description` field contains the parenthetical "rendering correctness is verified by `mkdocs build --strict` (covered by `docs-freshness-checker` and CI)". `docs-freshness-checker` handles timestamp-based drift, not build-time rendering verification. The attribution is factually inaccurate and could mislead an operator about which tool actually covers rendering.
      Where: agents/mermaid-diagram-reviewer.md line 3 (frontmatter `description`).
      Fix: Replace `(covered by docs-freshness-checker and CI)` with `(run via CI or task docs locally)` to remove the misattribution while keeping the boundary statement accurate..
      Verify: Re-read the description and confirm no tool is credited with covering a responsibility it doesn't hold..

#### `png-to-transparent-svg` (agent)

**Warning**

- [ ] [agent-management.tag-vocabulary] The agent declares `tags: [scaffolding]`, but the spec's starter vocabulary defines `scaffolding` as covering 'project-structure, catalog wiring, skill/agent scaffolding'. This is an image-conversion agent with no scaffolding responsibility. Using a tag whose definition does not apply is a misuse of the tag vocabulary; the SHOULD rule is to prefer a starter-vocabulary term 'when one applies' — when none applies, either introduce a new tag or omit tags.
      Where: Frontmatter line 7: `tags: [scaffolding]`.
      Fix: Remove `scaffolding` from the tags list. Either introduce a new kebab-case tag such as `image-processing` (which follows the normalization rule) or omit `tags` entirely until a matching starter term is added to the vocab..
      Verify: Confirm the chosen tag (or absence of tags) accurately describes the agent's functional cluster per the starter vocabulary in spec/claude/agent-management/en.md §Tag vocabulary..

**Suggestion**

- [ ] [agent-management.use-case-metadata] The `description` field contains explicit negative cases ('Don't use for PNGs that already carry real alpha transparency…; don't use for photographic content…'), but no structured `dont_use_when` frontmatter is declared. The SHOULD rule requires declaring `dont_use_when` 'whenever overlap with other artefacts is likely'; the sibling agent `graphic-prompt-generator` already references this agent in its own `dont_use_when`, confirming overlap exists in the catalog.
      Where: Frontmatter: `dont_use_when` field is absent.
      Fix: Add a `dont_use_when:` list to the frontmatter with at least two entries: one for PNGs that already carry real alpha transparency and one for photographic content. Each entry uses the schema `{situation: '...', alternative: '...'}` (or a plain string if no alternative agent exists for that case). Ensure every `alternative` value resolves to a discoverable artifact..
      Verify: Run the docs build (`task docs`) and confirm the catalog page renders the 'Don't use when' section without a validation error..

- [ ] [agent-management.recommendations] The agent body is 280 lines. The spec SHOULD rule advises tightening prose rather than letting the body grow past roughly 200 lines, since agents must stay in a single file.
      Where: Full body (lines 1–281); the procedure sections (Phase 1–5) and the inline Python code blocks account for the bulk of the overage..
      Fix: Tighten prose in the Working procedure section: inline code blocks for diagnostic and cleanup Python snippets could be condensed to the essential parameterised form, moving lengthy threshold-tuning commentary into a concise table or footnote. Target ~200 lines or clearly below 250..
      Verify: Re-count lines after editing; confirm no procedure logic is lost..

- [ ] [agent-management.use-case-metadata] The `see_also` field is absent even though the sibling agent `graphic-prompt-generator` cross-references this agent explicitly via its own `see_also` list. The spec SHOULD rule (§Structure, same line as the `dont_use_when` guidance) requires declaring `use_when`, `dont_use_when`, `see_also`, or `examples` 'whenever overlap with other artefacts is likely'. The asymmetric cross-link means catalog-driven peer-cluster lookups only navigate from `graphic-prompt-generator` to this agent, not in the reverse direction.
      Where: Frontmatter: `see_also` field is absent; compare with `agents/graphic-prompt-generator.md` which already declares `see_also: [png-to-transparent-svg]`..
      Fix: Add `see_also:\n  - graphic-prompt-generator` to the frontmatter, making the cross-link bidirectional..
      Verify: Check that `agents/png-to-transparent-svg.md` frontmatter contains a `see_also` entry referencing `graphic-prompt-generator`, matching the reverse declaration already in `agents/graphic-prompt-generator.md`..

#### `portfolio-inflight-collector` (agent)

**Critical**

- [ ] [portfolio-inflight-management.acceptance-criteria-agent-tools] The frontmatter declares `tools: [Bash]` only, omitting `Read`, `Glob`, and `Grep`. The agent body (line 30) falsely claims all four are declared ('only `Read`, `Bash`, `Glob`, and `Grep` are declared'), and the portfolio spec's acceptance criteria explicitly requires the agent to declare `Read`, `Bash`, `Glob`, `Grep`. As a result the runtime does not have `Read`, `Glob`, or `Grep` in the agent's restricted tool scope; those tools are either unavailable or fall through to the inherited caller surface rather than being explicitly scoped.
      Where: /home/nolte/repos/github/claude-shared/agents/portfolio-inflight-collector.md, line 5 (`tools: [Bash]`) and line 30 (body claim).
      Fix: Change the frontmatter `tools` field to `tools: [Read, Bash, Glob, Grep]`. This aligns the runtime tool scope with both the body's stated intent and the portfolio spec acceptance criterion: `The agent 'portfolio-inflight-collector' exists at agents/portfolio-inflight-collector.md, declares only read-only tools (Read, Bash, Glob, Grep)'..
      Verify: After the fix,`grep 'tools:' agents/portfolio-inflight-collector.md` returns `tools: [Read, Bash, Glob, Grep]`;`task test` (frontmatter validation) passes; the body claim on line 30 is accurate..

**Warning**

- [ ] [agent-management.tool-access-principle-of-least-authority] Because `Read`, `Glob`, and `Grep` are absent from `tools`, the declared tool set does not match the minimum set actually needed for the agent's responsibility. The agent's working procedure (§Working procedure steps 4a–4g) reduces raw API JSON entirely through `gh` CLI output and does not appear to require `Read`, `Glob`, or `Grep` against the local filesystem — yet the agent body asserts these tools are present and load-bearing (line 30, 'Enforcing read-only at the harness level'). If the tools are genuinely unused, including them adds unnecessary scope; if they are genuinely needed, omitting them from `tools` violates least-authority scoping. The discrepancy is unresolved.
      Where: /home/nolte/repos/github/claude-shared/agents/portfolio-inflight-collector.md, lines 5 and 30.
      Fix: Audit the working procedure to determine whether any step actually invokes `Read`, `Glob`, or `Grep`. If none do, remove the false claim on line 30 and keep `tools: [Bash]`. If any step does require them (e.g. reading a local cache file), add them to the `tools` frontmatter and document which step uses each. Either way, `tools` and the body claim must agree..
      Verify: Search the working procedure (§Working procedure) for any use of Read/Glob/Grep operations not performed via `gh`/`bash`; `tools` frontmatter matches the actual minimum tool set..

**Suggestion**

- [ ] [agent-management.recommendations-system-prompt-length] The agent body is 260 lines long, exceeding the ~200-line SHOULD threshold. The agent-management spec §Recommendations states: 'SHOULD keep the system prompt focused; if it grows past roughly 200 lines, tighten the prose rather than splitting it out.' At 260 lines the file is 30 % over the local nolte-shared convention.
      Where: /home/nolte/repos/github/claude-shared/agents/portfolio-inflight-collector.md (entire file, 260 lines).
      Fix: Tighten the §Working procedure prose by condensing repeated boilerplate (for example the per-step `gh` command reproductions already fully enumerated in §Read-only Bash justification could be replaced with back-references), and condense the §Hard rules section which largely duplicates the §Scope and boundaries 'does not' list. Aim for ≤200 lines without removing load-bearing specification content..
      Verify: Run `wc -l agents/portfolio-inflight-collector.md` and confirm the result is ≤200..

- [ ] [agent-management.recommendations-structured-report] The agent-management spec §Recommendations states that 'audit and research agents SHOULD close with an explicit caller follow-ups / handoff section.' The agent body ends with the §Hard rules section (line 248–259) and has no dedicated caller-handoff or follow-ups section that explicitly names what the calling skill (`portfolio-inflight-triage`) is expected to do next with the returned report.
      Where: /home/nolte/repos/github/claude-shared/agents/portfolio-inflight-collector.md, end of file (after line 244 §Working procedure step 6).
      Fix: Add a short `## Caller handoff` section after §Working procedure that explicitly names the handoff contract: the calling skill receives the structured report from §Output shape, applies §Stalling thresholds, derives matrix-axis values per §Classification and prioritisation, and writes the Findings-Report artefact to `.audits/portfolio-inflight/<YYYY-MM-DD>.md`..
      Verify: Confirm a `## Caller handoff` (or equivalently titled) section exists after the last working-procedure step and explicitly names the calling skill's next responsibilities..

#### `portfolio-manifest-collector` (agent)

**Warning**

- [ ] [agent-management.tool-access] The frontmatter declares `tools: [Bash]` (one tool) but line 33 of the body asserts "only `Read`, `Bash`, `Glob`, and `Grep` are declared — no `Edit`, no `Write`." This is a factual inconsistency: the harness enforces the frontmatter, so `Read`, `Glob`, and `Grep` are NOT actually restricted to the agent at runtime. The spec MUST have the `tools` field accurately scope the agent (principle of least authority; the `tools` declaration is the enforcement point, not prose in the body).
      Where: agents/portfolio-manifest-collector.md line 5 (`tools: [Bash]`) vs. line 33 (body claims four tools).
      Fix: Correct line 33 to remove the false claim. Since all §Working procedure steps use only `gh api` via Bash and no local-file reads are required, the frontmatter `tools: [Bash]` is the operationally accurate value. Change the bullet to: "**Tool restriction is load-bearing:** only `Bash` is declared — no `Read`, `Edit`, `Write`, `Glob`, or `Grep`. All manifest fetches go through the GitHub API via read-only `gh api` calls; no local filesystem reads are required. Enforcing read-only at the harness level prevents accidental mutations against any portfolio member during collection.".
      Verify: After the fix, grep the body for 'Read.*Bash.*Glob.*Grep' returns no hit, and the frontmatter `tools` list matches every tool mentioned in §Read-only Bash justification and the body's tool-restriction rationale..

#### `project-structure-reviewer` (agent)

**Critical**

- [ ] [project-structure.tests-must-should] Surface 2 unconditionally flags a missing `tests/` directory as `severity: critical` for every repository. The spec downgrades the requirement to SHOULD for Claude Code plugin / prompt-only repositories (the `.claude-plugin/` + `skills/` layout). Any Claude plugin repo audited by this agent will receive a false-Critical finding.
      Where: /home/nolte/repos/github/claude-shared/agents/project-structure-reviewer.md line 141 — `tests/` listed under "Required MUST directories".
      Fix: Change the `tests/` entry in Surface 2 to be conditional: emit `severity: critical` only when no Claude plugin layout (`.claude-plugin/` + `skills/`) is detected; emit `severity: warning` (or a `clean` note) when the Claude plugin signals are present. Add a project-type-specific note analogous to the existing Python/HA/Ansible blocks..
      Verify: Audit a repository that has `.claude-plugin/` + `skills/` but no `tests/` directory. The finding should be `warning`, not `critical`..

**Warning**

- [ ] [project-structure.top-level-files-license] `LICENSE` is entirely absent from Surface 1. The spec states MUST when the repository is public or intended for redistribution, SHOULD otherwise. No coverage and no deferred-scope declaration exists in the agent body or Health template.
      Where: /home/nolte/repos/github/claude-shared/agents/project-structure-reviewer.md lines 121–131 (Surface 1 list) and line 89 (Deferred scope example in Health template) — `LICENSE` never mentioned.
      Fix: Add a `LICENSE` entry to Surface 1: emit `missing-file` (`severity: warning`) when absent, noting that the severity rises to `critical` if the operator confirms the repository is public. Since the agent can't determine public/private status without the live API, a `warning` with a rationale note is appropriate. Alternatively, declare `LICENSE` check as deferred scope in the Health template with a pointer to `project-structure-apply`..
      Verify: Audit a repository without a `LICENSE` file. A `missing-file` finding should appear for `LICENSE`..

- [ ] [project-structure.project-planning-artefacts-layout] Surface 2's `project/` check covers `roadmap.md`, `goals.md`, `sprints/`, and `features/` but omits the `project/release-artifacts/out-of-band/` sub-layout (including `INDEX.md`). The spec MUST (line 84) that when `project/` is present its full canonical layout is respected, which includes the release-artifacts out-of-band subtree when out-of-band releases exist.
      Where: /home/nolte/repos/github/claude-shared/agents/project-structure-reviewer.md line 145 — `project/` layout check lists four items and stops.
      Fix: Extend the Surface 2 `project/` check to also verify: when `project/release-artifacts/out-of-band/` exists, `INDEX.md` must be present alongside it (`missing-file`, `severity: warning`). Alternatively, declare this sub-layout check as deferred scope in the Health template and name the owning spec section..
      Verify: Audit a repository with `project/release-artifacts/out-of-band/<entry>.md` but no `INDEX.md`. A `missing-file` (warning) finding should appear for the `INDEX.md`..

- [ ] [project-structure.documentation-per-language-layout] Surface 2 checks only for the presence of `docs/` but does not audit the per-language subdirectory layout (`docs/en/`, `docs/de/`, …) required by the spec §Documentation MUST. This gap is not declared as deferred scope in the Health template or anywhere in the agent body.
      Where: /home/nolte/repos/github/claude-shared/agents/project-structure-reviewer.md line 139 — `docs/` presence-only check; line 89 — Deferred scope example does not mention docs language layout.
      Fix: Either (a) add a Surface 2 check: when `docs/` exists, verify at least one per-language subdirectory (`docs/en/` or `docs/de/`) is present; emit `layout-violation` (`severity: warning`) otherwise, citing §Documentation. Or (b) explicitly declare the per-language layout check as deferred scope in the Health template with a pointer to `spec/project/mkdocs-structure/` as the owner spec..
      Verify: Audit a repository with a flat `docs/` directory (no `docs/en/` or `docs/de/`). A `layout-violation` (warning) finding should appear, or the deferred scope note should be present in the Health section..

- [ ] [project-structure.requirements-file-no-chaining] The spec §Requirements file format (line 116) states MUST NOT chain requirements-dev.txt to requirements.txt via a -r requirements.txt directive. The agent's Surface 4 Python check (line 159) covers version specifiers and [build-system] but never checks for the -r requirements.txt chaining prohibition. A Python repo with a chained requirements-dev.txt will pass the audit without a finding.
      Where: /home/nolte/repos/github/claude-shared/agents/project-structure-reviewer.md line 159 — Python Surface 4 check lists three sub-checks and omits the -r chaining MUST NOT.
      Fix: Extend the Python optional block in Surface 4 to add: 'requirements-dev.txt MUST NOT contain a -r requirements.txt (or --requirement) directive — layout-violation (severity: warning) when present'. Add this alongside the existing version-specifier check..
      Verify: Read spec/project/project-structure/en.md §Requirements file format (line 116) and confirm the MUST NOT; then confirm the agent line 159 does not mention chaining; then confirm the Acceptance Criteria at spec line 156 also lists this check..

- [ ] [project-structure.boring-cyborg-stale-should] Spec §GitHub repository configuration (lines 62-63) states SHOULD for .github/boring-cyborg.yml extending nolte/gh-plumbing:.github/commons-boring-cyborg.yml, and SHOULD for .github/stale.yml extending nolte/gh-plumbing:.github/commons-stale.yml. Neither file is mentioned anywhere in the agent's Surface 3 checks (lines 150-154), and neither is listed in the deferred-scope example at line 89. SHOULD violations map to Warning severity per the reviewer's own severity ladder.
      Where: /home/nolte/repos/github/claude-shared/agents/project-structure-reviewer.md lines 150-154 (Surface 3 list) and line 89 (Deferred scope) — .github/boring-cyborg.yml and .github/stale.yml never mentioned.
      Fix: Add to Surface 3: '.github/boring-cyborg.yml — missing-file (severity: warning) when absent; MUST extend nolte/gh-plumbing:.github/commons-boring-cyborg.yml — extends-drift (severity: warning) when present but not extending. Same pattern for .github/stale.yml.' If intentionally deferred, add them to the Deferred scope list in the Health template..
      Verify: Read spec/project/project-structure/en.md lines 62-63 to confirm the SHOULD; confirm the agent Surface 3 block omits both files; confirm the Acceptance Criteria at spec line 146 lists both..

#### `prose-vale-curator` (agent)

**Warning**

- [ ] [agent-management.resumable-runs] agent-management §Resumable runs MUST states 'mention resume support in the agent's description text whenever resumable: true is set'. The description satisfies the one-clause mention ('Supports resume on re-invocation per spec/claude/resumable-work/'). However, agent-management §Resumable runs also SHOULD declares 'SHOULD NOT declare resumable: true for fire-and-forget agents whose contract is a single read-only pass cheap to restart'. More importantly, the spec §Resume detection on re-invocation MUST for agents states the agent 'MUST NOT silently resume from a checkpoint without an explicit passed-in choice'. The §Resumability body section documents this correctly. No additional MUST violation is present beyond what finding [0] already attempted to surface.
      Where: agents/prose-vale-curator.md — §Resumability section, line 183.
      Fix: No fix required; the existing description and §Resumability body together satisfy every load-bearing MUST for resumable agents. Finding [0] was the only candidate and it is not a real violation..
      Verify: Re-read spec/claude/resumable-work/ §Non-interactive override and §Scope of applicability and confirm the description clause and body section each satisfy the relevant MUST rules..

**Suggestion**

- [ ] [skill-agent-catalog.use-case-metadata] The `description` field explicitly names three 'don't use' cases (net-new docs, vocabulary retirement audit, authoring Vale style rule YAML), but `dont_use_when` captures only two. The third case — 'authoring new Vale style rule YAML' — is absent from the structured metadata. The spec permits `dont_use_when` entries only when an `alternative` artifact can be named, so the omission is understandable; however, an incomplete structured metadata set means catalog cross-linking and the 'Don't use when' rendered section are silently partial relative to the prose description.
      Where: agents/prose-vale-curator.md — frontmatter `dont_use_when` field (lines 14-18) vs. `description` field (line 3).
      Fix: If a skill or agent for authoring Vale style rule YAML is ever added to the plugin, add a third `dont_use_when` entry pointing to it. As an interim measure, add the missing case to `use_when`'s complement by noting it in the description only (already done) and accept that the structured field intentionally has no `alternative` to cite yet. No immediate action is required; this is a catalog-completeness note..
      Verify: Confirm whether any artifact in skills/ or agents/ covers authoring Vale style rule YAML. If yes, add the entry. If no, leave as-is and note the intentional gap..

#### `quality-gate-enforcer` (agent)

**Critical**

- [ ] [quality-gate.composition-must-task-check] Surface 2 audits only per-category Taskfile targets (`lint`, `typecheck`, `test`) but does not check for the `task check` aggregate target mandated by quality-gate §Composition MUST: "MUST expose the aggregate gate as `task check`". A repository that has all individual category targets but no `task check` entrypoint passes Surface 2 without any finding, silently missing this spec requirement.
      Where: /home/nolte/repos/github/claude-shared/agents/quality-gate-enforcer.md, lines 129–130 (Surface 2, Taskfile preference rule).
      Fix: Add an explicit audit step in Surface 2: when `Taskfile.yml` exists, verify that a `check` target is present and composed from the per-category targets. A missing `task check` aggregate target MUST be reported as a `composition-gap` finding with `severity: critical`, referencing quality-gate §Composition..
      Verify: Confirm the agent body now explicitly checks for a `task check` aggregate Taskfile target and maps its absence to `composition-gap (severity: critical)`. Cross-check against quality-gate spec §Composition third bullet: "MUST expose the aggregate gate as `task check`"..

- [ ] [quality-gate.composition-must-task-check-aggregate] §Composition MUST: 'MUST expose the aggregate gate as `task check`'. The agent's Surface 2 checks only whether `task lint`, `task typecheck`, and `task test` exist as Taskfile targets but never reads whether a `task check` target is present and correctly delegates to those three. A repository missing `task check` entirely receives no finding.
      Where: /home/nolte/repos/github/claude-shared/agents/quality-gate-enforcer.md, lines 129-130 (Surface 2, Taskfile preference rule) — omission covers the entire agent body.
      Fix: Add an explicit check in Surface 2: after verifying the three per-category targets, grep or read the Taskfile for a `check` target and verify it composes the per-category targets. Emit a `composition-gap` finding at `severity: critical` when `task check` is absent or does not reference `task lint`, `task test`, `task typecheck`..
      Verify: After the fix, create a scratch Taskfile that has `lint`, `typecheck`, `test` targets but no `check` target; run the agent and confirm it emits a `composition-gap` finding for the missing `task check`..

**Warning**

- [ ] [quality-gate.triggers-coverage] The agent's three surfaces do not cover quality-gate §Triggers (fast scope, pre-commit hook invocability, gate must not be locked behind CI-only runners). The §Health template in the output shape prompts the author to list spec sections covered, implying §Triggers is intentionally deferred, but no explicit deferred-scope note names §Triggers in the body.
      Where: /home/nolte/repos/github/claude-shared/agents/quality-gate-enforcer.md, line 83 (§Deferred scope) and lines 115–143 (investigation surfaces).
      Fix: Add `spec/project/quality-gate/ §Triggers` to the hard-coded `Deferred scope` note in the output shape's `## Health` section, or add a Surface 4 that audits the triggers requirements (fast scope declaration, CI-only runner guard). Either approach explicitly sets operator expectations..
      Verify: Confirm the §Health section's deferred-scope bullet either names §Triggers explicitly or that a new Surface 4 covers it..

- [ ] [quality-gate.triggers-ci-only-runner] §Triggers MUST NOT: 'MUST NOT gate the gate itself behind a CI-only runner (for example a self-hosted GPU runner needed for the tests)'. This is statically detectable from CI workflow YAML (presence of `runs-on: self-hosted` or similar non-standard runner labels on the gate job). The agent reads all `.github/workflows/` files in Surface 2 for local-vs-CI parity, but no surface checks runner labels against this rule.
      Where: /home/nolte/repos/github/claude-shared/agents/quality-gate-enforcer.md, lines 115-143 (investigation surfaces) — §Triggers MUST NOT is absent from every surface.
      Fix: In Surface 2, add a check: for each CI workflow step that runs the gate, inspect the `runs-on` field of the parent job. If it names a self-hosted or non-standard runner without a corresponding README note that the suite is explicitly split out, emit a `composition-gap` finding at `severity: critical` citing spec §Triggers..
      Verify: Create a CI workflow with `runs-on: [self-hosted, gpu]` on the quality-gate job; confirm the agent emits a finding referencing §Triggers MUST NOT..

- [ ] [quality-gate.monorepo-subroot-scoping] §Monorepo MUST: 'MUST scope each category to the subroots that actually own the relevant manifest'. The agent's Surface 3 monorepo handling (line 143) only says subroots provide additional relevance signals for Surface 1 and that 'the wiring in Surface 2 is checked once per Taskfile target (subroots inherit the target unless a subroot-specific target overrides)'. It does not check whether each category is actually scoped to its owning subroot manifest directory versus running a monolithic walk of the entire tree — a monolithic `ruff .` from the repo root in a monorepo with unrelated subroots violates this MUST but would not produce a finding.
      Where: /home/nolte/repos/github/claude-shared/agents/quality-gate-enforcer.md, line 143 (monorepo subroots paragraph).
      Fix: In Surface 2 (or extend Surface 3), when monorepo subroots are detected: read each Taskfile target's command and check that it passes a subroot-scoped path argument rather than `.` or the repo root. Emit a `composition-gap` finding at `severity: warning` when a per-category command walks the whole tree despite multiple manifests being present in different subroots..
      Verify: Create a monorepo Taskfile where `task lint` runs `ruff .` (root-wide) while `pyproject.toml` only lives in `backend/`; confirm the agent emits a monorepo scoping finding..

#### `roadmap-coherence-reviewer` (agent)

**Critical**

- [ ] [spec/project/mission.smart-achievable] The agent claims to audit against `spec/project/mission/` (Surface 2 header, hard-rule line 156) but omits the SMART §Achievable MUST: every roadmap item with `mvp: true` MUST carry `detail: fine` AND a non-null `target_sprint`. This is a working-tree-checkable MUST distinct from the detail-level invariant (which is scoped to current/next sprint only). No investigation surface, no severity entry, and no Health/deferred acknowledgement covers it.
      Where: agents/roadmap-coherence-reviewer.md, §Surface 2 (lines 122–127) and §Surface 3 / §Severity assignment.
      Fix: Add a bullet under Surface 2 (or Surface 3): 'When `project/mission.md` exists, every item with `mvp: true` MUST carry `detail: fine` and a non-null `target_sprint` per `spec/project/mission/` §SMART contract §Achievable; violations are `shape-drift` findings (severity: critical, because `roadmap-plan` refuses to write an mvp: true item that fails this pair).'.
      Verify: The agent body must scan all `mvp: true` items and flag any whose `detail` is not `fine` or whose `target_sprint` is `null`, independently of whether those items happen to target the current or next sprint..

- [ ] [spec/project/mission.achievable-unbounded-mvp] The agent does not check whether every roadmap item is flagged `mvp: true` (unbounded MVP scope). Mission spec §SMART contract §Achievable (en.md line 65) MUST: 'An unbounded MVP scope (every roadmap item flagged `mvp: true`) defeats achievability and MUST be rejected by consuming skills with a verbatim error.' This is fully checkable from the working tree — count items where `mvp: true` equals the total item count. The check is absent from all three investigation surfaces and from the severity table.
      Where: agents/roadmap-coherence-reviewer.md, §Surface 2 (lines 122-127) and §Severity assignment (lines 141-144) — no surface or severity entry covers unbounded-MVP detection.
      Fix: Add a check in Surface 2 (or Surface 1 after `mvp_status` is resolved): if `project/mission.md` is present and every roadmap item carries `mvp: true`, emit a `shape-drift` finding at `critical` severity citing mission spec §SMART contract §Achievable. Add a corresponding entry to the severity table under `critical`..
      Verify: Author a test `project/roadmap.md` where all items carry `mvp: true` alongside a valid `project/mission.md`; the agent must emit a `critical` `shape-drift` finding rather than a clean result..

**Warning**

- [ ] [spec/project/mission.stabilisation-gate-post-mvp-active] Surface 2 of the agent's investigation does not check the mission spec §Stabilisation gate MUST: a roadmap item with `mvp: false` and `status: active` while `mvp_status` is `defining`, `in_progress`, or `achieved` is a lifecycle violation detectable from the working tree alone (both `mvp_status` in `mission.md` frontmatter and `mvp`/`status` on each roadmap item are readable without git history), yet the check is entirely absent from the agent's investigation surfaces and the severity table.
      Where: agents/roadmap-coherence-reviewer.md, §Surface 2 (lines 122–127) and §Severity assignment (lines 141–144).
      Fix: Add a bullet under Surface 2: 'When `project/mission.md` exists and `mvp_status` is any of `defining`, `in_progress`, or `achieved`, every roadmap item with `mvp: false` and `status: active` is a `lifecycle-drift` finding (severity: warning), per `spec/project/mission/` §Stabilisation gate.' Update the severity table's `warning` row to include this case..
      Verify: Grep the agent body for the phrase 'mvp: false' combined with 'status: active' and a conditional on `mvp_status`; the check must cover all three non-stabilised values (`defining`, `in_progress`, `achieved`)..

- [ ] [spec/project/roadmap.lifecycle-active-marking] Surface 3 checks that every `status: active` roadmap item has a backing `in_progress` or `done` feature (agent line 134), but does not check the converse: a feature with `status: in_progress` whose roadmap item is still `status: proposed`. Roadmap spec §Lifecycle (en.md line 103) MUST: 'mark an item `active` no later than the moment one of its features enters `in_progress`'. Both the feature status and the roadmap item status are readable from the working tree. This reverse-direction check is entirely absent from the investigation surfaces.
      Where: agents/roadmap-coherence-reviewer.md, §Surface 3 (lines 129-138) — the feature → roadmap item direction is not checked.
      Fix: In Surface 3, after reading feature files, add: for every feature with `status: in_progress`, look up its `roadmap_item` field and verify the corresponding roadmap item carries `status: active` (not `proposed`); mismatches are `lifecycle-drift` findings at `warning` severity citing roadmap spec §Lifecycle..
      Verify: Author a test scenario with a feature at `status: in_progress` whose roadmap item is `status: proposed`; the agent must emit a `warning` `lifecycle-drift` finding..

**Suggestion**

- [ ] [spec/project/roadmap.lifecycle] The severity section (line 142) lists '`proposed → done` history' as a checkable `critical` finding, but detecting this transition requires git log access the agent does not have — no `Bash` tool is declared. The parallel git-history limitation for ID monotonicity is correctly demoted to `info` and deferred to Health (line 120), but the same acknowledgement is absent for the `proposed → done` history check, misleading the agent (and its callers) into expecting a finding that cannot be produced.
      Where: agents/roadmap-coherence-reviewer.md, §Severity assignment line 142, compared with §Surface 1 lines 120–121.
      Fix: Remove '`proposed → done` history' from the `critical` bullet in §Severity assignment (the working tree cannot show transition history). Add a note in §Health under 'Surfaces with zero hits' or in the static output template: 'Lifecycle transition history (`proposed → done` without an `active` intermediate) — not verifiable from the working tree alone; requires `git log` the agent's tool set omits.'.
      Verify: After the fix, the severity section's `critical` examples are all working-tree-detectable. The output template's Health section lists the `proposed → done` history check as an explicitly deferred scope item, matching the treatment of ID monotonicity..

**Info**

- [ ] [spec/project/mission.mvp-flag-flip-true-to-false] Mission spec §MVP definition and delimitation (en.md line 74) MUST NOT allow a roadmap item to flip `mvp: true → false` after reaching `status: active`. The agent's line 127 handles only the `false → true` flip check (and correctly defers it to Health because it requires git history). The `true → false` flip is equally git-history-dependent but is not even mentioned in Health as a deferred constraint, leaving callers unaware the agent cannot verify it.
      Where: agents/roadmap-coherence-reviewer.md, §Surface 2 line 127 and §Health section — the `true → false` post-active flip constraint is absent entirely.
      Fix: Add a note in the §Health section template: 'mvp flag true→false flip after active status: not verifiable from the working tree alone; requires git history. Report in Health as deferred when project/mission.md is present.' Mirror the handling already applied to the false→true flip at line 127..
      Verify: Confirm the agent's output §Health section mentions both flip directions as git-history-dependent deferred constraints when `project/mission.md` is present..

#### `spec-readiness-reviewer` (agent)

**Critical**

- [ ] [spec-readiness.read-only-discipline] Option B instructs the agent to file the report 'at .audits/spec-readiness/<slug>.md', but the agent's own Hard rules state 'Never modify, create, or delete any file — not a spec, not an audit artifact, not anything', and the tools list omits Write. The two MUST-level constraints (read-only-discipline MUST and the Hard rules MUST NOT) are irreconcilable: the agent cannot satisfy both simultaneously. A reader dispatching Option B is told the file will be persisted, but it physically cannot be.
      Where: agents/spec-readiness-reviewer.md line 179 (Option B paragraph: 'filing it at .audits/spec-readiness/<slug>.md') vs line 281 (Hard rules: 'Never modify, create, or delete any file — not a spec, not an audit artifact, not anything').
      Fix: Remove the phrase 'filing it at .audits/spec-readiness/<slug>.md' from Option B and replace it with an instruction that the caller saves the returned report to that path. Alternatively, add Write to the tools list, remove the blanket 'not an audit artifact' ban from the Hard rules, and add a 'Write-justification' section analogous to the Bash justification — but only if the spec-readiness §Read-only-discipline MUST ('MUST be read-only') is also relaxed to allow writing audit artifacts..
      Verify: After the fix, Option B and the Hard rules no longer contradict each other; the tools list is consistent with the stated behaviour; and the spec-readiness §Read-only-discipline MUST ('MUST be read-only: the audit reports findings') is honoured..

- [ ] [spec-readiness.audit-artifact] The Option A output template omits three MUST-required fields from the audit artifact: 'date', 'trigger' (quarterly / pre-promotion / PR-change), and 'Git revision audited'. The spec-readiness §Audit artifact states these are all MUST-present in every persisted artifact, but the ## Scope section in the Option A template only records 'Specs in scope', 'Specs requested but not found', 'Canonical language', and 'Prior audit referenced'.
      Where: agents/spec-readiness-reviewer.md lines 101-105 (Option A ## Scope template) vs spec/project/spec-readiness/en.md line 83 (MUST include in the artifact: date, trigger, scope, Git revision, per-spec severity counts, and the full finding list sorted by severity).
      Fix: Add 'Date: <YYYY-MM-DD>', 'Trigger: <quarterly | pre-promotion | PR-change>', and 'Git revision: <SHA>' as required fields in the ## Scope block of the Option A output template..
      Verify: Confirm the Option A ## Scope template contains date, trigger, and Git revision fields; diff against spec/project/spec-readiness/en.md §Audit artifact MUST checklist..

**Warning**

- [ ] [spec-readiness.severity-scale] The Option A output template has no '## Suggestion' section between '## Warning' and '## Info', even though the canonical severity scale mandates four levels and the Suggestion bucket is explicitly available ('MAY populate the Suggestion bucket'). The Summary table includes a Suggestion column, but Suggestion-level findings produced during any audit phase have no designated section in the body template. An agent following the template strictly would either drop Suggestion findings or improvise a section, both of which diverge from the canonical scale.
      Where: agents/spec-readiness-reviewer.md lines 96–175 (Option A output template): template defines '## Critical', '## Warning', '## Info' but no '## Suggestion' section..
      Fix: Add a '## Suggestion' section to the Option A template between '## Warning' and '## Info', with at least one representative entry pattern (e.g., 'one-line improvement, stylistic fix, or MAY-class opportunity'). The existing 'Omit any severity section that's empty' rule already handles the case where there are no Suggestion findings..
      Verify: The Option A template now has all four severity sections in order (Critical, Warning, Suggestion, Info); Suggestion findings produced during a readiness run have a defined home in the output..

- [ ] [agent-management.recommendations] The system-prompt body is 263 lines, exceeding the ~200-line SHOULD guideline in agent-management §Recommendations. The spec states 'if it grows past roughly 200 lines, tighten the prose rather than splitting it out'. The overage is ~30%, driven primarily by the Option A output-template block and the detailed per-phase working procedure.
      Where: agents/spec-readiness-reviewer.md lines 31–293 (system-prompt body, 263 lines)..
      Fix: Tighten prose in the Working procedure phases (especially the repetitive classification-rules tables) and compress the Option A template by replacing example rows with a single representative row plus a prose note. Target ≤200 lines in the body..
      Verify: tail -n +31 agents/spec-readiness-reviewer.md | wc -l returns a value ≤200..

**Suggestion**

- [ ] [agent-management.structure] The frontmatter declares 'phase: design'. The agent's primary responsibility is a read-only review/audit pass; the phase vocabulary includes 'review' which is semantically closer. 'design' is a valid vocabulary entry (no MUST violation), but the mismatch may cause catalog and peer-cluster lookups to group this agent with design-phase artefacts rather than with the review cluster (agent-review, skill-review, spec-drift-audit).
      Where: agents/spec-readiness-reviewer.md line 8: 'phase: design'..
      Fix: Change 'phase: design' to 'phase: review' to align with the agent's functional cluster and improve catalog-routing accuracy..
      Verify: grep '^phase:' agents/spec-readiness-reviewer.md returns 'phase: review'; the catalog renders the agent in the review-phase section alongside agent-review and skill-review..

#### `sprint-readiness-reviewer` (agent)

**Critical**

- [ ] [spec/project/sprint.body-sections-must] Missing sprint body sections are classified as `severity: warning` (non-blocking), but the sprint spec mandates those sections with MUST and its acceptance criteria states "missing sections fail validation" — meaning absence is a blocker, not merely a warning.
      Where: /home/nolte/repos/github/claude-shared/agents/sprint-readiness-reviewer.md line 129 (Surface 1) and line 155 (Severity assignment section). Spec: spec/project/sprint/en.md §Body sections line 55: "MUST carry the following level-2 sections in this order, even when empty"; AC line 110: "missing sections fail validation"..
      Fix: In Surface 1 split the finding into two cases: (1) missing required section → `lifecycle-violation` with `severity: critical` (blocks planned→active); (2) wrong order of existing sections → `lifecycle-violation` with `severity: warning`. Update the Severity assignment section accordingly..
      Verify: Grep the agent for "missing or out-of-order" and confirm the two cases are separated, with missing mapped to critical and out-of-order mapped to warning..

- [ ] [spec/project/sprint.body-sections-must-critical-vs-warning] The severity table at agent line 155 lists 'body sections in wrong order' under `warning`, but does not split out 'missing sections' as `critical`. Combined with line 129's 'missing or out-of-order sections are `lifecycle-violation` findings (`severity: warning`)', the agent will classify a sprint with an entirely absent required section as warning (non-blocking) and may still issue a GO verdict. Sprint spec AC line 110 is unambiguous: 'missing sections fail validation' — this is a MUST-class blocker. The wrong-order case may reasonably remain a warning, but missing sections must be promoted to `critical`.
      Where: /home/nolte/repos/github/claude-shared/agents/sprint-readiness-reviewer.md line 129 and line 155. Spec: spec/project/sprint/en.md line 55 (MUST carry sections), line 110 (missing sections fail validation)..
      Fix: On line 129 split the finding into two cases: (1) missing sections → `lifecycle-violation`, `severity: critical`; (2) out-of-order sections → `lifecycle-violation`, `severity: warning`. On line 155 move 'missing body sections' from the warning bullet into the critical bullet alongside 'empty value_statement' and similar blockers..
      Verify: Re-read lines 129 and 155; confirm the word 'missing' appears only in the critical classification for body sections, and that 'out-of-order' is the sole body-section case listed under warning..

**Warning**

- [ ] [spec/project/feature.consistency-check-gate] Surface 3 (features readiness) does not check whether each `ready` feature has a populated `consistency_check` frontmatter object and a populated `## Consistency notes` body section — both are MUST gates that the feature spec requires before `draft → ready`. A feature could reach `ready` with an empty or absent `consistency_check` and the agent would emit a GO verdict without flagging it.
      Where: /home/nolte/repos/github/claude-shared/agents/sprint-readiness-reviewer.md lines 137–150 (Surface 3). Spec: spec/project/feature/en.md §Lifecycle line 88: "MUST require, before draft → ready: a non-empty ## Description, at least one acceptance-criterion bullet, a populated consistency_check frontmatter, and a populated ## Consistency notes section.".
      Fix: Add two checks to the per-feature loop in Surface 3: (1) `consistency_check` frontmatter object must be present and non-empty — a missing or empty object is a `feature-not-ready` finding (`severity: critical`), resolution `dispatch-skill feature-decompose:run-consistency-check`; (2) `## Consistency notes` body section must be non-empty — a missing or empty section is a `feature-not-ready` finding (`severity: critical`)..
      Verify: After the edit, Surface 3's bullet list explicitly names `consistency_check` and `## Consistency notes` as verified fields, each with a severity mapping..

- [ ] [spec/project/feature.description-non-empty-gate] Surface 3 checks acceptance criteria and test hooks for each `ready` feature, but does not verify that the feature's `## Description` section is non-empty. Feature spec line 88 states MUST require, before `draft → ready`, 'a non-empty `## Description`'. A feature could reach `ready` with an empty Description and the agent would not flag it.
      Where: /home/nolte/repos/github/claude-shared/agents/sprint-readiness-reviewer.md lines 137–150 (Surface 3). Spec: spec/project/feature/en.md line 88..
      Fix: Add a check in Surface 3's per-feature loop: verify that `## Description` is present and non-empty (at least one non-whitespace paragraph). Emit `feature-not-ready` (`severity: critical`) when the section is missing or empty, consistent with how missing acceptance criteria are handled..
      Verify: Confirm that Surface 3 now explicitly names `## Description` non-emptiness as a checked gate, distinct from the acceptance-criteria check..

**Info**

- [ ] [spec/project/sprint.cross-document-surface] `goals.md` appears in the Surface 2 heading and in the Hard rules scan boundary (line 166) but is never actually read or checked in any scan step. No rule in spec/project/sprint/ requires the readiness gate to inspect `goals.md`. The reference is dead scope that misleads readers.
      Where: /home/nolte/repos/github/claude-shared/agents/sprint-readiness-reviewer.md line 131 (Surface 2 heading) and line 166 (Hard rules). Spec: spec/project/sprint/en.md — `goals.md` is not mentioned as a surface for the readiness gate..
      Fix: Either remove `goals.md` from the Surface 2 heading and the Hard rules list, or add an explicit check (e.g., verify that each `roadmap_items` entry's parent outcome links back to a `project/goals.md` entry) and ground it in a spec reference..
      Verify: Grep the agent for `goals.md`; every occurrence either performs a check or explains the deferred scope in the Health section..

#### `tech-stack-drift-reviewer` (agent)

**Warning**

- [ ] [agent-management.tool-access] Surface 4 (lifecycle, line 162) promises "best-effort detection from git history" for the sprint-timing criterion of lifecycle-stale findings, but `Bash` is absent from `tools`, so `git log` is never available. The agent falls back to reporting the constraint in Health, but the fallback is always triggered — the "best-effort" framing overstates what the agent can deliver with its current tool set. The `agent-management` spec provides a `## Read-only Bash justification` escape hatch that would let `Bash` appear with a scoped allowlist; without it, the agent cannot fulfill the claimed detection path.
      Where: agents/tech-stack-drift-reviewer.md line 162.
      Fix: Either (a) add `Bash` to the `tools` field and add a `## Read-only Bash justification` section naming exactly `git log --follow -- portfolio/tech-stack.yml` (or equivalent) and forbidding writes/network mutations — this enables the detection path — or (b) drop the "best-effort detection from git history" claim and reword line 162 to state that the sprint-timing half of the lifecycle-stale check is always deferred to the Health section when the agent has no shell access..
      Verify: Confirm either `Bash` appears in `tools` with a `## Read-only Bash justification` section present, or that line 162 no longer claims git-history detection as a reachable path..

- [ ] [agent-management.structure] The agent body at line 175 states 'The tools list omits `Bash` deliberately' as a hard rule, yet line 162 describes a 'best-effort detection from git history' path and says the agent 'reports the constraint in Health when git-log access isn't available'. The §Hard rules section and Surface 4 prose are internally contradictory: the hard rule treats `Bash` absence as a permanent design choice, while the Surface 4 prose frames it as a runtime availability contingency. A reader of the system prompt cannot reconcile these two positions without external context. The agent-management spec SHOULD keep the system prompt internally consistent (§Recommendations: 'SHOULD begin the system prompt with the agent's role and boundaries').
      Where: agents/tech-stack-drift-reviewer.md lines 162 and 175.
      Fix: Either remove the 'best-effort detection from git history' path from Surface 4 entirely (aligning with the §Hard rules prohibition on shell commands) and replace with a static 'lifecycle-stale sprint-timing criterion is always deferred to Health' note; or add a `## Read-only Bash justification` section per §Tool access escape hatch and add `Bash` to `tools` with a scoped allowlist of `git log --follow`, `git log --diff-filter`..
      Verify: After the fix, the Surface 4 description and §Hard rules must describe the same capability boundary. If `Bash` is added, `## Read-only Bash justification` must be present in the body; if `Bash` stays absent, no claim of git-history-based detection should appear in Surface 4..

#### `test-case-extractor` (agent)

**Critical**

- [ ] [test-case-derivation.output-contract-no-traceability-index] The spec (§Output contract, last bullet) declares a MUST: 'the agent MUST avoid emitting a separate machine-readable traceability index until a downstream coverage tool declares the schema it requires.' This constraint is absent from the agent's system prompt. Without it, a running instance has no instruction preventing it from emitting such an index, violating the MUST.
      Where: /home/nolte/repos/github/claude-shared/agents/test-case-extractor.md — body (§Procedure / Phase 4), lines 96–97; the constraint is nowhere in the body..
      Fix: Add an explicit prohibition in Phase 4 (or in § Hard rules as rule 6): 'Do not emit a separate machine-readable traceability index. The per-case frontmatter, tags, and the per-document coverage summary are the only traceability surface until a downstream tool declares the schema it requires.' This mirrors the MUST in spec/project/test-case-derivation/ §Output contract..
      Verify: After the addition, grep the agent body for 'traceability index' or 'machine-readable' and confirm the prohibition is present..

- [ ] [test-case-derivation.inputs-discovery-report-documents] The spec (§Inputs and discovery) declares: 'the agent MUST report which documents it processed.' Phase 4 of the system prompt specifies a chat summary that lists derived case IDs and open requirements but does not include listing the processed input documents, leaving the MUST partially unimplemented.
      Where: /home/nolte/repos/github/claude-shared/agents/test-case-extractor.md — §Procedure / Phase 4 (lines 96–97). The phrase 'which documents it processed' does not appear anywhere in the body..
      Fix: Expand the Phase 4 chat-summary instruction to read: 'Return a chat summary listing (a) the requirement documents processed, (b) each derived case ID with a one-line title, and (c) the open requirements.' This satisfies the MUST from the governing spec..
      Verify: Grep the body for 'documents processed' or 'processed' to confirm the addition..

- [ ] [test-case-derivation.inputs-discovery-interface-assumption] Spec §Inputs and discovery (line 39) declares a MUST: 'when it [the interface type] can't be determined, default to the requirement's described surface and state the assumption.' Phase 1 of the agent instructs 'Determine the interface type (browser, CLI, API, mobile)' but provides no fallback instruction to state the assumption when the type cannot be determined. A running instance will silently pick a surface without disclosing it, violating the MUST.
      Where: /home/nolte/repos/github/claude-shared/agents/test-case-extractor.md — §Procedure / Phase 1 (line 58). The fallback 'state the assumption' clause appears for the interface-surface discovery path ('otherwise derive from the requirement text alone and say so') but is absent for the interface-type determination path..
      Fix: Append to the Phase 1 instruction: 'When the interface type cannot be determined from the requirement or project surface, default to the interface type described in the requirement and explicitly state that assumption in the chat summary and in the document preamble.'.
      Verify: Search agent body for any instruction to state the interface-type assumption; none exists. Spec line 39 wording: 'when it can't be determined, default to the requirement's described surface and state the assumption.'.

**Warning**

- [ ] [test-case-derivation.derivation-discipline-category-technique-name] Spec §Derivation discipline (line 47) carries a SHOULD: 'apply the standard derivation techniques—user-journey, input/boundary, state-transition, navigation, visual-feedback, and error-guessing—and name the technique a case exercises in its category field.' The agent's Phase 3 template (line 80) shows `**Category**: {happy-path | validation | error | state-transition | navigation | …}`, which omits the spec-required technique names (user-journey, input/boundary, visual-feedback, error-guessing) from the enumeration. The open `…` does not substitute for an explicit instruction to use those names.
      Where: /home/nolte/repos/github/claude-shared/agents/test-case-extractor.md — §Procedure / Phase 3 template (line 80)..
      Fix: Replace the category placeholder with: `**Category**: {happy-path | negative | user-journey | input-boundary | state-transition | navigation | visual-feedback | error-guessing | validation | …}` and add a sentence in Phase 2: 'Record in the Category field the technique (user-journey, input/boundary, state-transition, navigation, visual-feedback, or error-guessing) that the case primarily exercises.'.
      Verify: Agent Phase 2 and Phase 3 template should both reference the six spec-named techniques and instruct the agent to pick one per case..

#### `vocab-drift-scanner` (agent)

**Warning**

- [ ] [skill-agent-catalog.phase-classification] The agent is classified as `phase: review`, but the phase vocabulary defines `review` as "moves change toward develop through reviewed pull requests" and `quality` as "audits, scans, lint/typecheck/test gates, drift detection." A vocab drift scanner is unambiguously a drift-detection artefact and belongs in `quality`. The spec MUST restricts `phase` to the closed eight-value vocabulary and SHOULD directs authors to pick the phase matching the artifact's own primary purpose.
      Where: Frontmatter, line 8: `phase: review`.
      Fix: Change `phase: review` to `phase: quality`..
      Verify: Run `task docs` (or the catalog generator) and confirm the artefact appears under the `quality` phase section; grep the built catalog for `vocab-drift-scanner` and check the phase badge..

#### `webview-ui-expert` (agent)

**Critical**

- [ ] [agent-management.tool-access-bash-exception] The agent declares `Bash` in its `tools` field and is explicitly read-only, but the body contains no `## Read-only Bash justification` section. The spec states: "without the section, `Bash` on a read-only agent stays a `Critical`"; the exception that downgrades to Info requires the section to be present and to name the exact subset of read-only commands used plus an explicit prohibition of side-effecting commands.
      Where: Frontmatter `tools: Read, Glob, Grep, Bash`; no `## Read-only Bash justification` H2 heading exists anywhere in the 181-line body (verified by grep)..
      Fix: Add a `## Read-only Bash justification` section to the agent body that (a) names the exact read-only Bash commands the agent invokes (e.g. `git rev-parse --is-inside-work-tree` used in §Preconditions step 1), and (b) explicitly forbids writes, network mutations, package installs, and file edits. The section heading must be exactly `## Read-only Bash justification` to be recognized by agent-review..
      Verify: grep '## Read-only Bash justification' agents/webview-ui-expert.md returns a result; re-run agent-review and confirm the Bash finding downgrades to Info..

**Warning**

- [ ] [skill-agent-catalog.phase-classification] The agent is classified as `phase: design`, whose vocabulary definition is "authors the conventions, scaffolds, and specifications work depends on." The agent's primary responsibility is a deep-review audit of existing frontend code across five domains — an activity the catalog maps to `quality` ("audits, scans, lint/typecheck/test gates, drift detection"). The spec SHOULD says to pick the earliest phase at which the artifact is normally invoked, and `quality` is the closer fit.
      Where: Frontmatter line 8: `phase: design`..
      Fix: Change `phase: design` to `phase: quality` in the frontmatter. The value `quality` is a valid vocabulary term and is a better semantic match for an audit-and-review agent..
      Verify: grep '^phase:' agents/webview-ui-expert.md returns `phase: quality`; task test passes (validate_skills.py accepts the new value)..

- [ ] [agent-management.tool-access-bash-commands] The agent body (§Preconditions, line 86) instructs the agent to run `git rev-parse --is-inside-work-tree`, but the body provides no explicit prohibition of side-effecting commands anywhere in the text. Even if a `## Read-only Bash justification` section were added to resolve finding [0], the body would still need to name the exact read-only command subset used (at minimum `git rev-parse`) AND carry an explicit prohibition on writes, network mutations, and package installs. The current body states read-only intent in prose but never enumerates the permitted command set or writes a hard prohibition — both are required by the spec exception clause ('names the exact subset of read-only commands the agent invokes and explicitly forbids anything else').
      Where: agents/webview-ui-expert.md line 86: `git rev-parse --is-inside-work-tree` in §Preconditions; no explicit command enumeration or prohibition exists in the body..
      Fix: Add a `## Read-only Bash justification` section that (a) lists every permitted Bash command — at minimum `git rev-parse --is-inside-work-tree` — and (b) includes a sentence explicitly forbidding writes, network mutations, package installs, and file edits. This also resolves finding [0]..
      Verify: Confirm the new section is an H2 heading exactly matching `## Read-only Bash justification`, lists all Bash commands the agent invokes, and contains an explicit prohibition clause. Then confirm no other Bash invocations appear in the body outside that declared set..

#### `agent-review` (skill)

**Warning**

- [ ] [skill-management.description-third-person] The frontmatter `description` field contains 'Do NOT use for skill review' — a second-person imperative — violating the MUST that descriptions be written in third person.
      Where: skills/agent-review/SKILL.md, frontmatter `description` field, phrase 'Do NOT use for skill review (use skill-review) or for pull-request-level review'.
      Fix: Replace the second-person imperative with a third-person negative trigger, e.g. 'Does not handle skill review (use skill-review) or pull-request-level review (use the `review` skill).'.
      Verify: Read the updated `description` and confirm no imperative verb form directed at the reader or Claude remains; check that the negative trigger still reads naturally in Claude's system-prompt context..

- [ ] [skill-management.progressive-disclosure-load-trigger] The `templates/plan.template.md` asset is referenced twice in SKILL.md without an explicit load-trigger phrase using a 'when' or 'for' clause, violating the MUST that every referenced supporting file carries an explicit load-trigger.
      Where: skills/agent-review/SKILL.md, line 84 ('Draft the plan from `templates/plan.template.md`') and line 110 ('The template at `templates/plan.template.md` is the starting point').
      Fix: Rewrite at least one reference to the canonical pattern, e.g. 'Read `templates/plan.template.md` when drafting a new plan in the `run` operation — it contains the plan skeleton with all required frontmatter keys and section stubs.' The step-7 inline reference can remain as-is once an explicit load-trigger appears nearby..
      Verify: Confirm the updated SKILL.md contains a reference to `templates/plan.template.md` that includes an explicit 'when' or 'for' clause per the spec pattern..

- [ ] [skill-management.description-third-person] The description opens with the bare imperative 'Review a Claude Code agent…' instead of a third-person present-tense form ('Reviews a Claude Code agent…'). This is a distinct instance of the same MUST rule the reviewer flagged for 'Do NOT use', but covers the very first word of the description field — the primary invocation sentence that Claude sees first.
      Where: skills/agent-review/SKILL.md, frontmatter description field, opening word 'Review' (bare imperative) instead of 'Reviews' (third-person singular present).
      Fix: Change the opening verb from 'Review' to 'Reviews' so the description reads 'Reviews a Claude Code agent against spec/claude/agent-management/ …'. Also change 'Do NOT use for skill review' to a third-person phrasing such as 'Not intended for skill review (use skill-review)' or move the disambiguation to the dont_use_when field only..
      Verify: Read the updated description and confirm: (1) every sentence in the description is in third person with no imperative or second-person constructions; (2) the opening verb ends in 's' (third-person singular present). Run scripts/validate_skills.py to confirm no frontmatter errors..

#### `audience-identify` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Operations `validate` and `revisit` are not in the closed verb vocabulary. The spec MUST-requires each operation verb to come from exactly: audit, scaffold, patch, apply, migrate, run, update, close — and MUST NOT introduce new verbs without amending the list.
      Where: SKILL.md lines 75 and 90: `### 2. \`validate\`` and `### 3. \`revisit\``.
      Fix: Rename`validate` to `audit` (read-only check) and `revisit` to `update` (mutate an existing artefact). Update all body references and the Examples section load-trigger at line 105–106 accordingly..
      Verify: After rename, grep for `### 2.` and `### 3.` to confirm they read `audit` and `update`; grep full SKILL.md for the old verb strings to confirm no orphan references remain..

- [ ] [skill-management.progressive-disclosure-file-references] The reference to `templates/audiences.template.md` at line 73 is embedded inline in a numbered step without an explicit `when` or `for` load-trigger clause. The spec MUST-requires every asset under `templates/` to carry an explicit load-trigger phrase of the form `Read <path> when <condition>` or `See <path> for <concern>` with an explicit `when` or `for` clause; implicit references are non-conformant.
      Where: SKILL.md line 73: `using the template at \`templates/audiences.template.md\``.
      Fix: Add a standalone load-trigger sentence to the`## Examples` section or alongside step 8, e.g. `Read \`templates/audiences.template.md\` when writing the audience artifact in step 8.`.
      Verify: After fix, grep SKILL.md for`templates/audiences.template.md` and confirm the match contains either `when` or `for` in the same sentence as the path..

**Warning**

- [ ] [skill-management.frontmatter-validation] The `description` field contains `Don't use to review an existing audience artifact for compliance (use audience-review).` — a second-person imperative. The spec MUST-requires `description` to be written in third person; second-person phrasing such as `You can use this to …` is explicitly listed as a violation. The content is also redundant with the `dont_use_when` frontmatter field that already encodes the same redirect.
      Where: SKILL.md frontmatter `description` field, final-clause before the resume sentence.
      Fix: Remove the `Don't use …` sentence from `description` (the `dont_use_when` frontmatter field already carries that redirect for catalog rendering). If retention is desired, rewrite in third person: `Does not replace audience-review for compliance checks on an existing artifact.`.
      Verify: After edit, run `python3 -c "import yaml, re; c=open('skills/audience-identify/SKILL.md').read(); fm=yaml.safe_load(re.match(r'^---\n(.*?)\n---\n', c, re.DOTALL).group(1)); print(fm['description'])"` and confirm no second-person imperative remains..

#### `blog-author` (skill)

**Warning**

- [ ] [skill-management.evaluation-scenarios] The skill ships no evaluation scenarios. skill-management §Evaluation discipline SHOULD ships at least three evaluation scenarios per non-trivial skill (input prompt, optional input files, expected behavior) under examples/. This is a seven-step bilingual workflow with multiple approval gates — clearly non-trivial — yet the skill folder contains only SKILL.md and no examples/ directory.
      Where: /home/nolte/repos/github/claude-shared/skills/blog-author/ (no examples/ folder present).
      Fix: Create skills/blog-author/examples/ with at minimum three scenario files — e.g., 01-new-post-audience-a.md (new post, audience A, full briefing), 02-update-existing-post.md (update flow with update-reason), 03-incomplete-briefing-gap.md (missing grounded artefact, briefing-gap path). Each file should show the input prompt, any pre-existing artefacts, and the expected outputs/behavior per phase..
      Verify: ls skills/blog-author/examples/ returns at least three scenario files; task test passes..

**Suggestion**

- [ ] [skill-management.consistent-terminology] The skill body uses 'Diataxis' (without accent) in §Operations step 2 context and §Inputs (lines 28, 78), while every governing spec — spec/project/blog-author/en.md, spec/project/post-audience-communication/en.md — consistently spells it 'Diátaxis' (with accent). skill-management §Authoring quality SHOULD use consistent terminology throughout the skill. Mixed spelling of a named framework degrades instruction-following.
      Where: /home/nolte/repos/github/claude-shared/skills/blog-author/SKILL.md lines 28 and 78.
      Fix: Replace 'Diataxis' with 'Diátaxis' at lines 28 and 78 to match the canonical spelling used in the three load-bearing specs..
      Verify: grep -n 'Diataxis' skills/blog-author/SKILL.md returns no hits; grep -n 'Diátaxis' returns the two corrected occurrences..

#### `blog-author-trigger` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All five sub-operations inside the `## Operations` block use verbs outside the closed vocabulary. The headings are `### 1. Resolve the trigger event`, `### 2. Derive the briefing`, `### 3. Compute the suggestion and present the three-way choice`, `### 4. Execute the chosen path`, and `### 5. Deferral artefact and consumption`. None of these verbs (`Resolve`, `Derive`, `Compute`, `Execute`, and the noun phrase `Deferral artefact`) appear in the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec states MUST name each operation with one verb from the closed vocabulary and MUST NOT introduce new operation verbs without amending the list.
      Where: SKILL.md lines 71–105 (the five `### N.` sub-headings inside `## Operations`).
      Fix: Rename the five sub-operations to use vocabulary verbs. Suggested mapping: `### 1. run` (or keep as a single top-level `run` since this is fundamentally one workflow with five phases — if the steps are treated as internal phases rather than discrete named operations, collapse them under one `run` operation and rename the sub-steps as plain prose bullets or unnumbered phase headings). If all five are kept as distinct operations, possible mapping: `1. run` (resolve + derive as one initialisation pass), `2. run` (present the choice), `3. apply` (execute the chosen path), `4. update` (consume or write the deferral artefact). Amend `spec/claude/skill-management/en.md` §Operations vocabulary if a new verb genuinely must be introduced..
      Verify: After renaming, run `task test` (`scripts/validate_skills.py`) and confirm no `operations-vocab` error is emitted; grep the updated SKILL.md for `### [0-9]` and verify every verb after the number is in the closed vocabulary..

**Warning**

- [ ] [skill-management.authoring-quality] The `## Automatic dispatch from sprint-execute` section (line 120) states 'Operation C (`in_progress → done`), step 5, dispatches this skill'. The authoritative sources all say step 6: `sprint-execute` SKILL.md step 6 is titled 'Dispatch the `feature → done` blog trigger', the consuming repository's `CLAUDE.md` states 'Operation C step 6 automatically dispatches `/nolte-shared:blog-author-trigger`', and `spec/project/blog-author-trigger/en.md` §Reference example annex states 'step 6'. This factual inconsistency contradicts the skill's own self-declared rule 'When this skill and the spec disagree, the spec wins and this skill needs the update', and violates the skill-management SHOULD for consistent terminology (mixed step numbers for the same fact).
      Where: SKILL.md line 120: `sprint-execute` Operation C (`in_progress → done`), step **5**, dispatches this skill.
      Fix: Change 'step 5' to 'step 6' on line 120 to match `sprint-execute` SKILL.md, the repository `CLAUDE.md`, and the spec §Reference example annex..
      Verify: grep line 120 of SKILL.md reads 'step 6'; cross-check against `skills/sprint-execute/SKILL.md` step 6 heading and `CLAUDE.md` line 67..

- [ ] [skill-management.evaluation-discipline] The skill ships only two evaluation scenarios under `examples/` (`01-new-post-from-feature-done.md` and `02-defer-to-backlog.md`). The spec SHOULD ship at least three evaluation scenarios per non-trivial skill. The missing third scenario — a re-trigger run that encounters an existing deferral artefact and consumes it (Choice 1 or 2 on second pass, setting `status: deferred → consumed`) — is load-bearing coverage for the skill's duplicate-prevention hard rule and is the most operationally distinct path.
      Where: `skills/blog-author-trigger/examples/` — only two files present.
      Fix: Add `examples/03-consume-existing-deferral.md` covering a re-invocation scenario where a prior `project/blog-triggers/<feature-slug>.yml` with `status: deferred` exists, the operator chooses Choice 1 or 2, and the skill sets `status: consumed` on the artefact rather than creating a duplicate. Add a corresponding load-trigger line in SKILL.md §Examples..
      Verify: `ls skills/blog-author-trigger/examples/` shows three `.md` files; SKILL.md §Examples section contains three 'Read `examples/0N-...` when ...' lines each with an explicit when-clause..

- [ ] [skill-management.operations-vocabulary] The spec MUST title sub-operations as '### N. <verb>' — a single verb must be the first token after the number. Operation 5 heading '### 5. Deferral artefact and consumption' uses a noun phrase as the heading, which is a distinct format violation separate from the wrong-vocabulary violation already caught by finding [0]. The format rule requires a verb as the leading token; a noun phrase is non-conformant even if that noun phrase were somehow in the vocabulary.
      Where: SKILL.md line 101: `### 5. Deferral artefact and consumption`.
      Fix: Rename to a verb from the closed vocabulary, e.g. '### 5. close' or '### 5. update', or align with the broader fix for finding [0] when the operations block is revised to use closed-vocabulary verbs throughout..
      Verify: After the fix, confirm the heading matches '### N. <verb>' where <verb> is a single word from the closed vocabulary (audit, scaffold, patch, apply, migrate, run, update, close)..

**Suggestion**

- [ ] [skill-management.authoring-quality] The skill has no `## Gotchas` section. The spec SHOULD include a Gotchas section for non-obvious environment facts the agent would otherwise get wrong. This skill has several non-obvious pitfalls: (a) `sprint-execute` dispatches this skill from the *source* consumer's working directory, so the `git log` call to find the `done`-transition SHA must be relative to that working copy not a blog consumer's clone; (b) when the session ends mid-choice the implicit Choice-3 deferral still fires, which means the pre-staged `.briefing.md` is NOT written (only the `.yml` deferral artefact is); (c) `status: cancelled` must never be set by the skill, only by the operator.
      Where: SKILL.md body — no `## Gotchas` heading present.
      Fix: Add a `## Gotchas` section (between `## User-language policy` and `## Consumer contract resolution`, or before `## Hard rules`) with at least the three concrete corrections listed above..
      Verify: SKILL.md contains a `## Gotchas` heading with at least one concrete environment-fact correction distinct from the hard rules..

#### `continuous-improvement-triage` (skill)

**Critical**

- [ ] [skill-management.progressive-disclosure-load-trigger] The load-trigger phrase for `templates/triage.template.md` (line 42) uses the form `"Read … to understand … before creating or updating"` instead of the required `"Read <path> when <trigger condition>"` or `"See <path> for <specific concern>"` pattern. The spec MUST requires an explicit `when` or `for` clause; other prepositions (`to`, `before`) are non-conformant.
      Where: skills/continuous-improvement-triage/SKILL.md, line 42: `Read \`templates/triage.template.md\` to understand the triage artifact format before creating or updating a triage file.`.
      Fix: Rewrite to use the canonical pattern, e.g.`Read \`templates/triage.template.md\` when creating or updating a triage artifact, to understand the expected format and frontmatter fields.`.
      Verify: Confirm the line contains either the word`when` followed by a trigger condition, or `for` followed by a specific concern, matching the pattern from skill-management §Progressive disclosure & file references MUST..

**Warning**

- [ ] [continuous-improvement.continuous-loop-quarterly-review] The spec MUST states `MUST NOT silently defer an in-scope finding past the response window declared by its originating audit spec; … missed windows are themselves a finding under the next audit.` The skill's `update` operation step 2 offers `Defer with reason` as a legitimate decision option but contains no constraint or warning that deferral past the originating audit spec's own response window is prohibited and is itself a finding. An operator reading only the skill could defer indefinitely without knowing this guard.
      Where: skills/continuous-improvement-triage/SKILL.md, lines 75–78 (update operation, step 2, `Defer with reason` bullet). The constraint also belongs in the Hard rules section..
      Fix: Add a note to the `Defer with reason` bullet along the lines of: `(Note: deferral past the response window declared by the originating audit spec — e.g. spec-drift-audit, workflow-health — is itself a finding and MUST be recorded as such in the next cycle.)` Also add a corresponding Hard rule: `Never let a deferral silently exceed the response window of the originating audit spec.`.
      Verify: Confirm the Defer option explicitly references the response-window constraint from spec/project/continuous-improvement/ §Continuous loop, and that the Hard rules section contains a corresponding invariant..

- [ ] [skill-management.use-case-metadata] The skill has material overlap with `spec-drift-audit`, `workflow-health`, `portfolio-audit`, and any ad-hoc audit workflow. The spec says authors SHOULD declare `dont_use_when` whenever overlap with other artefacts is likely, so the catalog stays scannable and cross-linking can connect related artefacts. The current frontmatter omits the field.
      Where: skills/continuous-improvement-triage/SKILL.md, YAML frontmatter (no `dont_use_when` key present)..
      Fix: Add a `dont_use_when` entry, for example: `dont_use_when: ["you want to perform the hands-on remediation yourself rather than dispatch it to a specialist", "you want to run a specific named audit (use spec-drift-audit, workflow-health, or project-structure-apply instead)"]`.
      Verify: After adding, confirm the field value conforms to the schema in skill-agent-catalog §Use-case metadata, and that the catalog build (`task docs`) reports no validation errors..

- [ ] [continuous-improvement.portfolio-gap-closure] The Hard rules section (line 129) says 'Always prefer a plugin-distributed specialist over a project-local one when the finding class has been observed in two or more repositories.' The spec (§Portfolio gap closure, line 49) is absolute: 'MUST plugin-distribute any specialist that gap closure creates in response to a finding class observed in two or more repositories … a project-local specialist isn't an acceptable closure in the cross-repository case.' 'Always prefer' implies a non-binding preference with possible alternatives; the spec leaves no room for a project-local closure in the cross-repository case. The skill's own update step 6 (line 89) correctly implements the MUST by blocking closure until distribution is confirmed, but the Hard rule undercuts it by softening 'MUST' to 'prefer', creating an internal inconsistency that could mislead operators reading only the Hard rules.
      Where: skills/continuous-improvement-triage/SKILL.md, line 129 (Hard rules section): 'Always prefer a plugin-distributed specialist over a project-local one when the finding class has been observed in two or more repositories.'.
      Fix: Replace 'Always prefer a plugin-distributed specialist over a project-local one' with 'Always use a plugin-distributed specialist (never project-local) when the finding class has been observed in two or more repositories' to mirror the spec's MUST and align with update step 6..
      Verify: Read spec/project/continuous-improvement/en.md §Portfolio gap closure line 49 and compare to SKILL.md Hard rules line 129; confirm the Hard rule now uses unconditional language matching the spec's MUST..

**Info**

- [ ] [resumable-work.non-interactive-override] The spec §Non-interactive override says a skill MAY support a non-interactive override flag (e.g. `--resume <run-id>`, `--new`, `--discard <run-id>`), and `when the skill supports such a flag it MUST document it in its description`. The skill's `## Resumability` section and description do not mention whether such a flag is supported or explicitly declined. This is informational because the MAY makes the feature optional; the MUST only fires if the flag is actually implemented.
      Where: skills/continuous-improvement-triage/SKILL.md, §Resumability (line 117–119) and description frontmatter..
      Fix: If no non-interactive override is planned, add one sentence to §Resumability: `This skill does not support a non-interactive resume flag; operator confirmation is always required.` If an override is added later, document it in the `description` field per the spec MUST..
      Verify: Confirm the Resumability section explicitly states whether the flag is supported or not, so future readers and reviewers don't need to infer the decision..

#### `cookiecutter-template-manage` (skill)

**Critical**

- [ ] [skill-management.operations-vocab] Operation `### 2. refactor` uses the verb `refactor`, which is not in the closed operations vocabulary. The spec MUST-level rule requires each operation to be named with exactly one verb from: audit, scaffold, patch, apply, migrate, run, update, close. New verbs require amending the spec list.
      Where: SKILL.md line 59: `### 2. refactor`.
      Fix: Rename the operation to `### 2. migrate` (brownfield → conforming) or `### 2. update` (mutate an existing artefact) — both fit the semantic of overhauling an existing template. Coordinate with the companion agent (`cookiecutter-template-author`) if it receives the mode string as part of the dispatch payload, as the payload key would change too..
      Verify: grep -n '### .*refactor' skills/cookiecutter-template-manage/SKILL.md returns no results; every operation verb in the `## Operations` block appears in the closed-vocabulary list in spec/claude/skill-management/en.md §Operations vocabulary..

- [ ] [skill-management.progressive-disclosure] Two example reference files longer than 100 lines lack a table of contents. `examples/02-refactor-existing-template.md` is 115 lines and `examples/03-update-hook-and-tests.md` is 122 lines. The spec MUST rule states every reference file longer than 100 lines opens with a table of contents so partial-read previews still surface the file's full scope.
      Where: skills/cookiecutter-template-manage/examples/02-refactor-existing-template.md (115 lines), skills/cookiecutter-template-manage/examples/03-update-hook-and-tests.md (122 lines).
      Fix: Add a short `## Contents` section with anchor links at the top of each file, covering at minimum Input prompt, Input files, Execution trace, and Expected output sections..
      Verify: Both files open with a `## Contents` (or equivalent ToC heading) that links to every major section; each file is independently navigable from a 20-line partial read..

#### `dependency-audit` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Five of the seven numbered sub-operations use verbs outside the closed vocabulary (audit, scaffold, patch, apply, migrate, run, update, close): `### 0. Dispatch`, `### 1. Detect`, `### 2. Prefer`, `### 5. Render`, `### 6. Offer`. Only `### 3. Run` and `### 4. Run` conform. The spec states MUST name each operation with one verb from the closed vocabulary and MUST NOT introduce new operation verbs without amending the list.
      Where: SKILL.md lines 48, 52, 69, 109, 143 — operation headings under `## Operations`.
      Fix: Rename non-conforming sub-operation headings to use allowed verbs. Suggested mappings: `### 0. Dispatch ...` → `### 0. run` (or fold into the preamble since dispatching an agent is not a user-visible operation step); `### 1. Detect ...` → remove heading or fold into the `audit` or `run` step as a procedure paragraph; `### 2. Prefer ...` → fold into step 3 as a procedure note; `### 5. Render ...` → `### 5. run`; `### 6. Offer ...` → `### 6. update`. Alternatively, restructure into fewer operations (`audit`, `run`, `update`) aligned with the real user-visible phases..
      Verify: grep `^### [0-9]` skills/dependency-audit/SKILL.md — every first word after the number and period must be one of: audit, scaffold, patch, apply, migrate, run, update, close..

- [ ] [skill-management.frontmatter-validation-third-person] The `description` opens with the bare infinitive `Scan` instead of the third-person singular present `Scans`. The spec MUST requires third-person ('Generates …', 'Reviews …'). This is specific to this skill; the portfolio pattern of `Invoke when` / `Don't use` embedded in descriptions is a separate corpus-wide concern and not flagged here as a per-skill finding.
      Where: SKILL.md line 3 — `description:` frontmatter field, first word.
      Fix: Change the opening word from `Scan` to `Scans`: `description: Scans the current project's dependency tree for known vulnerabilities…`.
      Verify: Check that `description:` value now starts with `Scans`; confirm no other third-person violations remain in the first sentence..

- [ ] [dependency-audit.audit-artifact] The skill claims to implement `spec/project/dependency-audit/` but omits that spec's §Audit artifact MUST: the skill has no instruction to persist the audit result as a commit, issue, or file. The report is rendered only in-conversation; no step instructs saving to `.audits/dependency-audit/` or any equivalent location.
      Where: SKILL.md — entire `## Operations` body (no persistence step exists); compare with `spec/project/dependency-audit/en.md` §Audit artifact MUST..
      Fix: Add a persistence step (e.g. `### 6. update` before the follow-up-actions step) that instructs: after operator confirmation, write the rendered report to `.audits/dependency-audit/dependencies-YYYY-Q<n>.md` (default) or the caller-specified location, referencing `spec/project/dependency-audit/` §Audit artifact §SHOULD for the canonical path. Alternatively note that persistence is optional for ad-hoc runs but MUST happen for quarterly/pre-release triggers..
      Verify: SKILL.md contains an explicit instruction to persist the final report as a file (or commit/issue) and references the `.audits/dependency-audit/` canonical path from the bound spec..

- [ ] [dependency-audit.audit-artifact] The `### 5. Render the report` template is missing four fields that `spec/project/dependency-audit/` §Audit artifact MUST include: (1) run date, (2) trigger type (quarterly / pre-release / ad-hoc), (3) Git revision audited, and (4) tool versions. It also omits per-finding response decisions (upgrade / ignore-with-rationale / accept-as-known), which the spec requires when a full audit artifact is produced.
      Where: SKILL.md lines 111–139 — the report template code block inside `### 5. Render the report`.
      Fix: Extend the report header with: `Date: <ISO 8601>`, `Trigger: <quarterly | pre-release | ad-hoc>`, `Git revision: <short SHA>`, and augment `Auditors run:` to include version strings. Add a `Response decision:` sub-field per finding (or a `## Response summary` section) so full-audit artifacts satisfy the spec's §Audit artifact MUST requirements..
      Verify: Report template includes Date, Trigger, Git revision, tool versions, and a per-finding or aggregate response decision field..

- [ ] [dependency-audit.ignore-discipline] The skill's follow-up actions (### 6. Offer follow-up actions, line 147-148) instruct offering to add an advisory to the auditor's ignore list but only mention the `valid-until` date. The dependency-audit spec §Ignore discipline (line 60) MUST declares that every ignore entry must carry: advisory ID, affected package, `valid-until` date (ISO 8601), and a one-line rationale. Three of the four mandatory fields (advisory ID, affected package, rationale) are absent from the skill's ignore-entry instruction.
      Where: SKILL.md lines 147-148 — the ignore-list offer inside `### 6. Offer follow-up actions`.
      Fix: Expand the ignore-list offer to explicitly state that the entry MUST include advisory ID, affected package name, a `valid-until` ISO 8601 date, and a one-line rationale. Example: 'offer to add `<advisory-id>` for `<package>` to the auditor's ignore list with `valid-until: <ISO-date>` and a one-line rationale.'.
      Verify: Check that the updated step lists all four required fields (advisory ID, affected package, valid-until date, one-line rationale) for every ignore entry it offers to create..

- [ ] [dependency-audit.ignore-discipline] The skill does not instruct storing ignore entries in a location the auditor reads natively (e.g., `pyproject.toml` under `[tool.pip-audit]`, `.npm-audit-ignore.json`). dependency-audit spec §Ignore discipline (line 59) MUST requires native storage — not free-form prose visible only in the audit artifact. The skill's step 6 describes the ignore entry conceptually but gives no instruction on where it must be written.
      Where: SKILL.md lines 143-149 — `### 6. Offer follow-up actions`, the ignore-list bullet.
      Fix: Add an explicit instruction specifying that ignore entries MUST be written to the auditor's native config location (e.g., `[tool.pip-audit]` in `pyproject.toml` for Python, `.npm-audit-ignore.json` for npm), not as free-form prose in the audit artifact. Reference the spec's examples of native locations..
      Verify: Confirm that the step names the native config file(s) for each supported ecosystem (pip-audit, npm, pnpm, yarn) and explicitly prohibits writing the ignore entry only to the audit artifact..

**Warning**

- [ ] [skill-vs-agent.rationale-documentation] The `## Why this is a skill, not an agent` rationale names three dimensions favoring the skill choice (Orchestration role, Interactivity, Hybrid split) but names no counter-dimension — a dimension that pointed toward agent and was outweighed. The spec SHOULD name at least one such dimension to show the choice was contested.
      Where: SKILL.md lines 181–188 — `## Why this is a skill, not an agent` section.
      Fix: Add one bullet naming the agent-side dimension that was outweighed, for example: `**Context-window impact** pointed toward an agent for the whole skill (the audit output can be verbose), but the interactivity requirement for Step 6 made a pure-agent design unworkable — hence the hybrid split.`.
      Verify: Rationale section contains at least one bullet or sentence that names a dimension pointing toward agent and explains why it was outweighed..

- [ ] [dependency-audit.audit-artifact] The SHOULD in dependency-audit spec §Audit artifact (line 66) recommends defaulting to the canonical path `.audits/dependency-audit/dependencies-YYYY-Q<n>.md`. The skill's report template and operations contain no default path suggestion or mention of the canonical location. A SHOULD omission is a Warning-grade drift.
      Where: SKILL.md — entire `## Operations` body; no canonical path `.audits/dependency-audit/` is referenced anywhere in the skill.
      Fix: Add a note in the persistence step (or in the report template header) recommending `.audits/dependency-audit/dependencies-YYYY-Q<n>.md` as the default save path, noting that a GitHub issue labelled `security-audit` is an accepted alternative..
      Verify: Confirm the skill body now mentions the canonical path and the GitHub-issue alternative as the two accepted persistence targets, consistent with the spec's SHOULD..

#### `docs-audience-tracks-apply` (skill)

**Critical**

- [ ] [docs-audience-tracks.per-page-contract] The operationalised spec (`spec/project/docs-audience-tracks/` §Per-page contract, lines 71 and 86) has two MUSTs that classify specific findings as `docs-freshness` findings: (1) 'MUST treat an unknown track value, a missing track value … as a docs-freshness finding per spec/project/docs-freshness/' and (2) 'MUST treat a page whose audience frontmatter value maps to a different track … as a docs-freshness finding (warning, not error)'. The skill's audit section reports these as its own 'Missing-key findings', 'Unrecognised-value findings', and 'audience-track mismatch' findings, without tagging or routing them as docs-freshness findings. This omits the spec-mandated classification that downstream tooling (docs-freshness-checker, AC-114) depends on.
      Where: skills/docs-audience-tracks-apply/SKILL.md lines 77–83 (audit §Track frontmatter and §Content-mode mapping).
      Fix: In the audit section, label the three finding classes — (a) missing `track:` on a non-snippet page, (b) unrecognised `track:` value, (c) audience-track mismatch — explicitly as `docs-freshness` findings, consistent with the spec's MUST. Suggest routing them to `docs-freshness-checker` or note they feed that checker's report. The patch operation (lines 102–104) should similarly classify the findings it handles with the same label..
      Verify: Grep for 'docs-freshness' in SKILL.md (`grep -n docs-freshness skills/docs-audience-tracks-apply/SKILL.md`); the three finding classes named in spec §Per-page contract (lines 71, 86) should each reference the docs-freshness classification in the audit and patch sections..

- [ ] [docs-audience-tracks.per-page-contract] The docs-freshness spec §Severity classification (line 49) distinguishes two different severities for track-frontmatter findings that the docs-audience-tracks spec (line 71) MUST route there: 'track-frontmatter drift with an unrecognised value' is **critical** and 'track-frontmatter drift (missing key)' is **warning**. The skill's audit section (lines 77–83) conflates both as sibling 'Missing-key findings' and 'Unrecognised-value findings' with no severity distinction. Because the skill is the operationalisation of the spec and the MUST routing (finding [1]) already requires it to emit proper docs-freshness findings, the severity differentiation is a load-bearing part of that MUST compliance — not merely a style note. An audit that routes both classes at the same (unspecified) severity fails the per-finding severity contract that docs-freshness-checker downstream tooling depends on (AC-114 in docs-audience-tracks spec).
      Where: skills/docs-audience-tracks-apply/SKILL.md lines 77–79 (audit §Track frontmatter sub-bullets); spec/project/docs-freshness/en.md line 49 §Severity classification; spec/project/docs-audience-tracks/en.md line 71.
      Fix: In the audit §Track frontmatter sub-bullets, split 'Unrecognised-value findings' from 'Missing-key findings' and annotate each with the correct docs-freshness severity: unrecognised value → critical, missing key → warning. This makes the routed docs-freshness findings carry the severity the downstream tools expect..
      Verify: Read the audit output section of the skill. Confirm that the two track-frontmatter finding sub-types are labelled with distinct severity levels matching docs-freshness §Severity classification (critical for unknown value, warning for missing key)..

**Warning**

- [ ] [skill-management.operations-vocabulary] The `migrate` operation is labelled 'greenfield' in three places (description field: `migrate (greenfield)`, use_when entry: `you want to greenfield-migrate a docs/ tree`, body intro: 'migrates a greenfield documentation tree', and the sub-operation heading `### 2. migrate (greenfield: most pages lack track:)`). The operations-vocabulary MUST in `skill-management` defines `migrate` as 'brownfield → conforming' and `scaffold` as 'greenfield create'. The operation itself is brownfield-conforming (adding `track:` to existing pages), so the verb choice is correct, but the repeated 'greenfield' label contradicts the spec vocabulary throughout the skill and will mislead authors and operators about which operation to choose.
      Where: skills/docs-audience-tracks-apply/SKILL.md — frontmatter description field, use_when[1], body introduction paragraph (line 30), and operation sub-heading (line 88).
      Fix: Replace 'greenfield' with wording that reflects the brownfield semantic: description: `migrate (most pages lack track:)`; use_when[1]: `you want to migrate an existing docs/ tree onto the audience-tracks layer`; body intro: 'migrates a documentation tree that lacks track: conformance'; heading: `### 2. migrate (most pages lack track:)`..
      Verify: Search for 'greenfield' in SKILL.md (`grep -n greenfield skills/docs-audience-tracks-apply/SKILL.md`); no remaining occurrence should be paired with the migrate operation. Confirm the operation verb `migrate` is still present..

- [ ] [skill-management.evaluation-discipline] The `skill-management` spec SHOULD: 'ship at least three evaluation scenarios per non-trivial skill (input prompt, optional input files, expected behavior) under `examples/` or a sibling location'. This is a non-trivial three-operation skill; no `examples/` folder exists and the `examples` frontmatter field is absent.
      Where: skills/docs-audience-tracks-apply/ — directory has only SKILL.md; no examples/ subfolder or examples frontmatter.
      Fix: Create `skills/docs-audience-tracks-apply/examples/` with at least three scenario files covering one case per operation (audit, migrate, patch): prompt text, a sketch of the target repo state, and the expected skill output..
      Verify: `ls skills/docs-audience-tracks-apply/examples/` returns at least three files, each with a clear prompt and expected-outcome section..

#### `docs-dry-refactor` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] The skill declares two operation verbs outside the closed vocabulary: `scan` and `propose`. The spec's §Operations vocabulary MUST requires every named operation to use exactly one verb from the eight-item closed list (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`), and MUST NOT introduces new verbs without amending that list.
      Where: /home/nolte/repos/github/claude-shared/skills/docs-dry-refactor/SKILL.md lines 68 and 93 — `### 1. \`scan\`` and `### 2. \`propose <finding-id>\``; also referenced in`description` and `## Preconditions` section..
      Fix: Remap operations to allowed verbs. `scan` maps naturally to `audit` (read-only check — the spec's own gloss). `propose` has no single-word equivalent in the vocabulary; the closest fit is `run` (the fallback default verb for single-operation skills, but usable here for an interactive proposal step) or a two-step rename: merge `propose` into the `audit` phase output (the findings table already contains the proposed canonical source) and gate the `apply` step on user approval within the `apply` operation itself. Either way, amending the spec to add `scan` and `propose` is the alternative path — open a spec-amendment PR first..
      Verify: After renaming, confirm all three operation headings use verbs that appear verbatim in the closed vocabulary list at `spec/claude/skill-management/en.md` §Operations vocabulary. Grep the skill for the old verb names and confirm no occurrences remain as operation identifiers..

- [ ] [skill-management.frontmatter-description-person] The `description` field MUST be written in third person; never first or second person. The description contains 'Don't use for non-MkDocs markdown trees…' which is a second-person imperative directive addressed to the reader.
      Where: /home/nolte/repos/github/claude-shared/skills/docs-dry-refactor/SKILL.md line 3 — description value: '…Don't use for non-MkDocs markdown trees, single-file snippet authoring, prose linting…'.
      Fix: Rewrite the exclusion clause in third person, e.g. 'Not intended for non-MkDocs markdown trees, single-file snippet authoring, prose linting…' The dont_use_when frontmatter field already captures these exclusions in structured form; the description clause can be dropped or rephrased as a third-person observation..
      Verify: Confirm the updated description contains no imperative verbs addressed to the reader (Don't, Do not, Use, Invoke, Never) in non-third-person form; check that the spec rule at en.md line 46 is satisfied..

**Warning**

- [ ] [skill-management.evaluation-discipline] No `examples/` directory or evaluation scenarios exist. The spec's §Evaluation discipline SHOULD requires at least three evaluation scenarios per non-trivial skill (input prompt, optional input files, expected behavior) under `examples/` so iteration is grounded in observable behavior.
      Where: /home/nolte/repos/github/claude-shared/skills/docs-dry-refactor/ — only `SKILL.md` is present; no `examples/` subfolder exists..
      Fix: Create `examples/` with at least three scenario files covering representative invocations: e.g., a `scan` across a two-language MkDocs tree that has duplicate paragraphs, a `propose`/`apply` for a code-fence snippet with a live canonical source, and a scenario where no canonical source exists and a new `_snippets/` file must be created..
      Verify: Run `ls /home/nolte/repos/github/claude-shared/skills/docs-dry-refactor/examples/` and confirm at least three scenario files are present..

- [ ] [skill-management.recommendations] The skill body is 157 lines, exceeding the 150-line soft target. The spec's §Recommendations SHOULD keep `SKILL.md` under roughly 150 lines and move long-form content into referenced files.
      Where: /home/nolte/repos/github/claude-shared/skills/docs-dry-refactor/SKILL.md — 157 lines total..
      Fix: Extract the verbose §Hard rules section (lines 133–147, 15 lines) and/or the §Gotchas section (lines 149–158) into a `references/hard-rules.md` or `references/gotchas.md` file with an explicit load-trigger phrase in `SKILL.md` (e.g., "Read `references/hard-rules.md` before any `apply` operation"). This brings the body under 150 lines while keeping the content accessible..
      Verify: Run `wc -l /home/nolte/repos/github/claude-shared/skills/docs-dry-refactor/SKILL.md` and confirm the result is ≤150..

#### `feature-decompose` (skill)

**Critical**

- [ ] [skill-management.description-third-person] The `description` field opens with the imperative verb form "Decompose a roadmap item" instead of the required third-person form. The spec explicitly requires third-person phrasing ("Generates …," "Reviews …") and forbids first and second person.
      Where: skills/feature-decompose/SKILL.md, frontmatter line 3 — first word of the `description` value is "Decompose" (imperative) instead of "Decomposes" (third-person singular)..
      Fix: Change the opening of the `description` value from "Decompose a roadmap item into feature files…" to "Decomposes a roadmap item into feature files…" (add the third-person -s inflection to the first verb)..
      Verify: Run `grep '^description:' skills/feature-decompose/SKILL.md` and confirm the value starts with "Decomposes"..

- [ ] [skill-management.operations-vocabulary] Operation 1 is named "Decompose" which is not in the closed operation-verb vocabulary. The spec MUST requires every operation to use exactly one verb from the set: `audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`. "Decompose" is not a member of that set.
      Where: skills/feature-decompose/SKILL.md line 55 — `### 1. Decompose`..
      Fix: Rename Operation 1 to a conformant verb from the closed vocabulary. The closest semantic match is `scaffold` (greenfield create), giving `### 1. Scaffold`. If the intent covers both reading the roadmap state and writing the feature file, `apply` (audit + scaffold + patch in one flow) is also acceptable. Amend the spec if none of the eight verbs fits, per the MUST NOT: "introduce new operation verbs without amending this list" rule..
      Verify: Run `grep '^### ' skills/feature-decompose/SKILL.md` and confirm both operation headings use verbs from the closed vocabulary..

- [ ] [resumable-work.scope-description-clause] The `description` resume reference reads "Supports resume per `spec/claude/resumable-work/`." but the spec's example clause is "supports resume on re-invocation". The phrase "on re-invocation" is absent, making the clause slightly less explicit for operators reading the catalog.
      Where: skills/feature-decompose/SKILL.md, frontmatter line 3 — last sentence of the `description` value..
      Fix: Change "Supports resume per `spec/claude/resumable-work/`." to "Supports resume on re-invocation per `spec/claude/resumable-work/`." to match the spec's illustrative clause and align with the phrasing used by peer skills such as `sprint-execute`..
      Verify: Run `grep 'on re-invocation' skills/feature-decompose/SKILL.md` and confirm the phrase is present in the `description` line..

**Warning**

- [ ] [skill-management.description-third-person] The description contains "Don't use to transition feature status" — a negative imperative directed at the reader that is borderline second-person, but the clearer issue is the broader opening phrase. More importantly, the skill-management spec (line 151) independently states MUST mention resume support in the skill's description whenever resumable: true is set, and the resumable-work spec (line 35) prescribes the exact phrase "supports resume on re-invocation". The description's use of "Supports resume per `spec/claude/resumable-work/`" satisfies the skill-management cross-reference rule but violates the resumable-work exact-phrase rule — a second independent MUST citation for the same gap already identified in finding [2]. Both specs are independently authoritative, so the miss is that only one spec reference was cited instead of both.
      Where: skills/feature-decompose/SKILL.md, frontmatter line 3 — last sentence of the description value; also spec/claude/skill-management/en.md line 151..
      Fix: Change "Supports resume per `spec/claude/resumable-work/`." to "Supports resume on re-invocation per `spec/claude/resumable-work/`." to satisfy both the skill-management cross-reference MUST and the resumable-work exact-phrase MUST simultaneously..
      Verify: Confirm the updated description contains the substring "supports resume on re-invocation" (case-insensitive) and that the total description length remains under 1,024 characters..

**Suggestion**

- [ ] [skill-management.skill-length] SKILL.md is 220 lines, which exceeds the ~150-line soft target. The spec recommends moving long-form content into referenced support files to keep `SKILL.md` scannable.
      Where: skills/feature-decompose/SKILL.md — full file (220 lines)..
      Fix: Consider extracting the verbose Operation 2 ("Run the consistency check", lines 112–172) into `references/consistency-check-protocol.md` with a load-trigger in SKILL.md: "Read `references/consistency-check-protocol.md` when dispatching or falling back the consistency check." This would bring SKILL.md under ~150 lines. The MUST 500-line/5 000-token hard cap is not violated, so this is discretionary..
      Verify: Run `wc -l skills/feature-decompose/SKILL.md` and confirm the result is closer to 150..

#### `github-issue-templates-apply` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Five of six sub-operation headings use verbs outside the closed vocabulary. The spec MUST requires every named operation to use one of: audit, scaffold, patch, apply, migrate, run, update, close. The headings '1. Detect project type', '2. Resolve audience profile', '3. Derive templates and fields', '4. Disclose the plan and confirm', and '6. Re-audit and drift detection' all use verbs not in that set. Only '5. Apply' is conformant.
      Where: SKILL.md lines 57, 74, 82, 106, 133 — `## Operations` sub-headings.
      Fix: Remap the five non-conformant headings to closed-vocabulary verbs. Suggested mapping: '1. Detect project type' → '1. Audit project type' (read-only classification step); '2. Resolve audience profile' → '2. Audit audience profile'; '3. Derive templates and fields' → '3. Scaffold templates and fields' or keep the step labelled under the parent `apply` frame; '4. Disclose the plan and confirm' → rename to fit 'apply' or 'scaffold' framing; '6. Re-audit and drift detection' → '6. Audit drift'. Update the prose in the intro paragraph at line 55 that references 'Operations 3 to 5' if headings shift..
      Verify: grep '^### ' skills/github-issue-templates-apply/SKILL.md — every verb after '### N. ' must appear in the closed vocabulary: audit, scaffold, patch, apply, migrate, run, update, close..

- [ ] [github-issue-templates.skill-contract] The bound spec (spec/project/github-issue-templates/en.md) step 6 of the derivation procedure states: 'A security contact_link is REQUIRED' in config.yml — it must point at GitHub private vulnerability reporting until a SECURITY.md convention is established. The skill's Operation 5 (Apply) never mandates including this security contact_link, and the Hard rules section omits it entirely. A skill that claims to implement the bound spec MUST faithfully satisfy every MUST/REQUIRED in it.
      Where: SKILL.md Operation 5 (lines 119–132) and Hard rules (lines 171–181); bound spec spec/project/github-issue-templates/en.md line 75.
      Fix: Add to Operation 5 an explicit instruction: always include a security contact_link in config.yml pointing at GitHub private vulnerability reporting (until spec/project/project-structure/ specifies a SECURITY.md path, at which point link to that instead). Add a corresponding hard rule: 'Never write config.yml without a security contact_link entry in contact_links.' Mirror the open-question note from the bound spec so the skill author knows when to update it..
      Verify: Re-read Operation 5 and Hard rules — both must explicitly require a security contact_link in config.yml. Cross-check against spec/project/github-issue-templates/en.md §Project-type-driven derivation step 6..

- [ ] [skill-management.progressive-disclosure] The reference file references/project-type-fields.md is 349 lines but opens without a table of contents. The spec MUST requires a table of contents at the top of any reference file longer than 100 lines, so that partial-read previews surface the file's full scope.
      Where: skills/github-issue-templates-apply/references/project-type-fields.md — the file jumps directly to a preamble paragraph then section headings with no TOC block.
      Fix: Insert a table of contents after the opening preamble (before the first `---` separator on line 10), listing the six bundle sections: Claude Code plugin, Python application, Python library, Node / TypeScript library or app, CLI tool, Documentation-only repository — each as a Markdown anchor link..
      Verify: Read the first 15 lines of references/project-type-fields.md and confirm a TOC with anchor links to every section heading is present before the first `---` separator..

- [ ] [github-issue-templates.skill-contract] Operation 4 ('Disclose the plan and confirm') lists six items to surface to the user before writing, but omits the 'per-template strictness profile' which the bound spec's Skill contract MUST-requires to be disclosed. Spec §Skill contract line 113 states: 'surface its derivation (project type, audiences, chosen template kinds, project-specific fields, and the per-template strictness profile) to the user before writing files.' SKILL.md lines 108–115 enumerate detected project type, audience artefact, template list, per-template fields, config.yml shape, and labels/assignees — the per-template strictness profile (strict bug vs. permissive feature-request caps) is absent from this disclosure list.
      Where: SKILL.md lines 108–116 — Operation 4 disclosure bullet list.
      Fix: Add a bullet point to the Operation 4 disclosure plan requiring the per-template strictness profile to be surfaced: e.g. 'the per-template strictness profile (bug reports: required-field cap and dropdown/checkboxes encouragement; feature requests: two-required-field cap, textarea-only substantive field, optional-only project-type extras).'.
      Verify: Read SKILL.md Operation 4 and confirm it explicitly lists the per-template strictness profile as a mandatory disclosure item before any file is written..

#### `lektorat-apply` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] The skill declares `revise` as a named operation under `## Operations`, but `revise` is not in skill-management's closed operations vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec states: "MUST name each operation with one verb from the closed vocabulary" and "MUST NOT introduce new operation verbs without amending this list."
      Where: /home/nolte/repos/github/claude-shared/skills/lektorat-apply/SKILL.md, line 92 (`### 3. \`revise\``); also in`description` field (line 3) and `use_when` (line 11)..
      Fix: Amend `spec/claude/skill-management/en.md` §Operations vocabulary to add `revise` (full-artefact rewrite). The skill correctly implements the contract mandated by `spec/project/lektorat/` (which explicitly requires `revise` as a MUST operation name), so the fix is in the vocabulary list, not in the skill. Until the spec is amended, the skill is technically non-conformant against skill-management..
      Verify: After amending skill-management, re-run the skill review. Confirm `revise` appears in the closed vocabulary list and that the heading `### 3. \`revise\`` now passes the operations-vocabulary check..

- [ ] [resumable-work.scope-of-applicability] The `resumable: true` skill's `description` field ends with "Supports resume per `spec/claude/resumable-work/`." but the spec mandates the exact clause "supports resume on re-invocation" (spec/claude/resumable-work/ §Scope of applicability: "MUST be referenced from the skill or agent description text (one short clause: 'supports resume on re-invocation')"). The phrase "on re-invocation" is missing.
      Where: /home/nolte/repos/github/claude-shared/skills/lektorat-apply/SKILL.md, line 3 (description field, final clause)..
      Fix: Change the description's trailing clause from "Supports resume per `spec/claude/resumable-work/`." to "Supports resume on re-invocation per `spec/claude/resumable-work/`." — identical to the pattern used by `docs-dry-refactor` and `pull-request-create`..
      Verify: Grep the description field for the exact substring "on re-invocation"; confirm it is present..

**Suggestion**

- [ ] [skill-management.recommendations] SKILL.md is 168 lines, exceeding the ~150-line soft guideline. The spec states: "SHOULD keep SKILL.md under roughly 150 lines as a soft target; move long-form content into referenced files." The Operations section (§§1–3) contains detailed step-by-step procedures totalling ~85 lines that could move to a `references/operations.md` file with an explicit load-trigger.
      Where: /home/nolte/repos/github/claude-shared/skills/lektorat-apply/SKILL.md, lines 62–105 (Operations §1–§3)..
      Fix: Extract the detailed per-operation step lists (audit steps 1–9, patch steps 1–7, revise steps 1–8) into `references/operations.md` with a table of contents, and replace each operation's body in SKILL.md with a one-line load-trigger: e.g. "Read `references/operations.md` §1 for the full audit procedure." This keeps the operation overview visible inline while satisfying the soft line-count guideline..
      Verify: Run `wc -l skills/lektorat-apply/SKILL.md` and confirm the result is at or below 150 lines. Confirm each referenced section in `references/operations.md` has a load-trigger phrase in SKILL.md..

#### `mermaid-diagrams-apply` (skill)

**Critical**

- [ ] [skill-management.operations-verb-vocabulary] All five operation sub-headings use verbs outside the closed vocabulary. The spec's MUST says each operation MUST be named with exactly one verb from: audit, scaffold, patch, apply, migrate, run, update, close. The headings '### 1. Setup audit', '### 2. Setup apply', '### 3. Diagram authoring', '### 4. Diagram audit', '### 5. Re-audit' all violate this rule: 'Setup', 'Diagram', and 'Re-audit' are not in the vocabulary, and compound noun-verb forms like 'Setup audit' are non-conformant.
      Where: SKILL.md lines 74, 89, 100, 129, 144 — the five ### sub-headings under ## Operations.
      Fix: Rename sub-operations to single approved verbs. Suggested mapping: '1. Setup audit' → '1. audit', '2. Setup apply' → '2. apply', '3. Diagram authoring' → '3. scaffold' (or 'run' for a single default op), '4. Diagram audit' → '4. audit' (merge with op 1, or rename to distinguish), '5. Re-audit' → '5. run'. If two separate audit phases are needed, disambiguate the heading within the constraint (e.g. '1. audit (setup)' and '4. audit (diagrams)') — but verify that form is acceptable under the spec or amend the spec..
      Verify: grep -n '^### ' skills/mermaid-diagrams-apply/SKILL.md — every match must parse as a single word from {audit,scaffold,patch,apply,migrate,run,update,close}..

- [ ] [skill-management.description-third-person] The description contains two second-person / imperative clauses: 'Invoke when the user asks to ...' and 'Don't use for general MkDocs scaffolding ...'. The spec MUST requires third-person gerund form ('Generates …', 'Reviews …'); imperative commands ('Invoke when', 'Don't use') are non-conformant because the description is injected into Claude's system prompt and inconsistent point-of-view degrades skill discovery.
      Where: SKILL.md frontmatter, description field — the sentences beginning 'Invoke when' and 'Don't use for'.
      Fix: Rewrite in third person: e.g. 'Invoke when …' → 'Invoked when the user asks to …' (or remove — trigger phrases are already covered in use_when), and 'Don't use for …' → 'Not intended for general MkDocs scaffolding …'..
      Verify: Read the description field; confirm no second-person pronoun ('you', 'don't', 'invoke') appears at sentence-start level..

- [ ] [skill-management.description-third-person] The description's 'Invoke when' clause is an imperative directed at the reader of the description (Claude's system prompt). This is a second-person direction, not a third-person capability statement. The spec MUST says write in third person ('Generates …'), never second or first person.
      Where: SKILL.md frontmatter description, line: 'Invoke when the user asks to "wire up Mermaid" ...'.
      Fix: Rephrase to a trigger description in third person: e.g. 'Use when the user asks to wire up Mermaid …' → 'Triggered when a user requests Mermaid setup …' or simply delete; trigger coverage already exists in use_when..
      Verify: Re-read the description after edit and confirm no imperative verb opens a sentence..

- [ ] [skill-management.description-third-person] Findings [1] and [2] both correctly identify a MUST violation but the reviewer mis-classified the severity as Warning. 'MUST write description in third person' is a MUST rule; violations block merge and must be Critical. The reviewer's severity choice of Warning systematically under-reports the urgency of the two third-person findings.
      Where: SKILL.md frontmatter description field — sentences beginning 'Invoke when the user asks to "wire up Mermaid"' (line 11) and 'Don't use for general MkDocs scaffolding' (line 13).
      Fix: Rewrite both clauses in third-person form. 'Invoke when' → 'Triggered when the user asks to …'; 'Don't use for' → 'Not intended for general MkDocs scaffolding (use project-structure-apply), spec authoring (use spec), docs-freshness audits (use docs-freshness-checker), or non-Mermaid diagrams.' These negative-routing hints are already captured in the structured dont_use_when frontmatter field; the inline description clause can be dropped or rewritten as a third-person capability limit..
      Verify: Re-read the description field and confirm every clause uses a third-person subject ('Audits …', 'Generates …', 'Triggered when …', 'Supports …'). Run the local validator (scripts/validate_skills.py) and confirm no third-person lint error is emitted..

**Warning**

- [ ] [skill-management.skill-under-150-lines-soft] SKILL.md is 182 lines, exceeding the SHOULD soft target of 150 lines. The spec labels this a soft target ('roughly 150 lines') and recommends moving long-form content into referenced files. The skill already uses an examples/ folder but the body still contains detailed gotcha prose and multi-paragraph operation descriptions that could be extracted.
      Where: SKILL.md — overall file length (182 lines vs. 150-line guideline).
      Fix: Consider extracting the Gotchas section and/or the detailed operation prose into a references/ file with an explicit load-trigger phrase, bringing SKILL.md closer to the 150-line target. The hard cap is 500 lines / 5,000 tokens (currently ~4,480 tokens — within budget), so this is a SHOULD-class improvement only..
      Verify: wc -l skills/mermaid-diagrams-apply/SKILL.md — target ≤150..

**Suggestion**

- [ ] [skill-vs-agent.rationale-counter-dimension-should] The skill-vs-agent spec SHOULD requires naming at least one dimension that pointed the other way. The rationale does name a counter-dimension ('Counter-dimension considered: a narrower agent could specialize on parsing source artifacts …'), which satisfies the MUST. However, the SHOULD to name the reason it was outweighed relies on an inline 'skill wins' conclusion without fully naming which decision dimension from the spec table was decisive. The rationale is substantively sound but could name the table dimension explicitly (e.g. 'Interactivity — mid-flow user approval is required') for portfolio-audit clarity.
      Where: SKILL.md, ## Why this is a skill, not an agent — the 'Counter-dimension considered' bullet.
      Fix: Add the spec-table dimension name to each rationale bullet, e.g.: 'Per-block user approval is the contract (Interactivity dimension)'..
      Verify: Check that each decisive bullet names a dimension from the skill-vs-agent decision table..

**Info**

- [ ] [skill-management.examples-three-scenarios] The skill ships exactly three example scenarios under examples/, which satisfies the SHOULD of 'at least three evaluation scenarios per non-trivial skill'. All three examples include an input prompt, input files, and expected behavior. Multi-model spot-check note in ## Multi-model testing also aligns with the spec's SHOULD to test across Haiku, Sonnet, and Opus.
      Where: SKILL.md examples/ directory and ## Multi-model testing section.
      Fix: No action required..
      Verify: ls skills/mermaid-diagrams-apply/examples/ — should show three files..

- [ ] [resumable-work.frontmatter-and-description] resumable: true is correctly declared in frontmatter, and the description closes with 'Supports resume on re-invocation per spec/claude/resumable-work/.' — satisfying both the MUST to declare the field and the MUST to mention resume in description text.
      Where: SKILL.md frontmatter line 36 and description field last clause.
      Fix: No action required..
      Verify: grep 'resumable: true' SKILL.md and grep 'resume on re-invocation' SKILL.md..

#### `mission-define` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All five operation sub-headings use verbs outside the closed vocabulary. The spec mandates exactly one verb from: `audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`. The skill uses `Read`, `Walk` (twice), `Compose`, and `Confirm`, none of which appear in the vocabulary. Introducing new verbs without amending the spec list is explicitly forbidden.
      Where: /home/nolte/repos/github/claude-shared/skills/mission-define/SKILL.md lines 58–93 (`### 1. Read inputs`, `### 2. Walk SMART one letter at a time`, `### 3. Walk audiences one at a time`, `### 4. Compose the file`, `### 5. Confirm and write`).
      Fix: Remap each operation to a conformant verb. Suggested mapping: op 1 → `### 1. audit` (read-only check of inputs), op 2 → `### 2. run` (the SMART interactive walk), op 3 → `### 3. run` (or rename to a separate `### 3. scaffold` since it builds the audience section), op 4 → `### 4. scaffold` (greenfield compose), op 5 → `### 5. update` (confirm and write). Alternatively, collapse ops 2–5 into a single `### 1. scaffold` and retain `### 2. audit` for the precondition checks, keeping the step count minimal..
      Verify: Run `grep '^### [0-9]' skills/mission-define/SKILL.md` and confirm every verb after the dot is in {audit, scaffold, patch, apply, migrate, run, update, close}..

- [ ] [skill-management.progressive-disclosure] `examples/01-fresh-mission-claude-plugin.md` is 106 lines but carries no table of contents at the top. The spec states: "MUST include a table of contents at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope." The acceptance criterion likewise reads: "Every reference file longer than 100 lines opens with a table of contents."
      Where: /home/nolte/repos/github/claude-shared/skills/mission-define/examples/01-fresh-mission-claude-plugin.md — 106 lines, no ToC (line 1 is a plain H1 heading, line 8 jumps straight to `## Input prompt`).
      Fix: Add a `## Contents` (or `## Table of contents`) section after the opening H1 and before `## Input prompt`, listing the file's sections with anchor links, for example: `- [Input prompt](#input-prompt)`, `- [Expected behavior](#expected-behavior)`, `- [Step-by-step trace](#step-by-step-trace)` (adjust to match actual headings)..
      Verify: `head -10 skills/mission-define/examples/01-fresh-mission-claude-plugin.md` must show a ToC section before the first content heading..

- [ ] [spec/project/mission.body-sections] The skill instructs Claude to render the `## Statement` SMART decomposition as a "five-line SMART decomposition" (one terse line per letter). The governing mission spec requires "one short paragraph per letter" — a multi-sentence paragraph, not a single line. The skill's output will be narrower (less prose per letter) than what the spec mandates and what downstream validators consuming the file will expect.
      Where: /home/nolte/repos/github/claude-shared/skills/mission-define/SKILL.md line 86 (`immediately followed by a five-line SMART decomposition`) and examples/01-fresh-mission-claude-plugin.md line 93–94 (confirming the five-line format).
      Fix: Change the instruction in Operation 4 from "a five-line SMART decomposition" to "one short paragraph per letter (two-to-four sentences naming which frontmatter field anchors that letter)", aligning with `spec/project/mission/en.md §Body sections`. Update the example's step 5 description to match..
      Verify: Re-read `spec/project/mission/en.md §Body sections` and confirm the skill's Operation 4 `## Statement` instruction now describes paragraphs (not lines) per letter..

- [ ] [claude/skill-management.operations-vocabulary] The sub-operation headings violate the required format in addition to using non-vocabulary verbs. spec/claude/skill-management/en.md line 115 requires sub-operations to be titled '### N. <verb>' where <verb> is one word from the closed list. The skill uses multi-word phrases: '### 1. Read inputs', '### 2. Walk SMART one letter at a time', '### 3. Walk audiences one at a time', '### 4. Compose the file', '### 5. Confirm and write'. While the vocabulary violation is reported in finding [0], the heading-format violation (phrases rather than a single verb following the number) is a separate MUST that was not called out independently. The spec SHOULD guidance (line 116) also notes 'retain operation names short (single word)'.
      Where: /home/nolte/repos/github/claude-shared/skills/mission-define/SKILL.md lines 58, 67, 77, 81, 91 — all five sub-operation headings use multi-word noun phrases after the number rather than a single vocabulary verb.
      Fix: Rename each sub-operation heading to use a single vocabulary verb. Viable mappings: '### 1. read' → 'audit' (read-only input collection), '### 2. Walk SMART' → 'run' (the default for a primary operation), '### 3. Walk audiences' → 'apply' (walks and gathers each audience), '### 4. Compose the file' → 'scaffold' (greenfield file composition), '### 5. Confirm and write' → 'close' (terminates the lifecycle of the drafting flow). Amend the spec if any required verb is genuinely missing from the vocabulary..
      Verify: Grep SKILL.md for '### [0-9]' and confirm every heading matches '### N. <single-closed-vocab-verb>' with nothing after the verb..

#### `mission-revise` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Sub-operation headings use alphabetic letters (A., B., C.) which the spec explicitly forbids. The spec MUST: 'title sub-operations as ### N. <verb> (numbered) ... alphabetic letters (A./B./C.) and ### Step N are non-conformant'.
      Where: /home/nolte/repos/github/claude-shared/skills/mission-revise/SKILL.md lines 57, 69, 94 — '### A. Revise the statement...', '### B. Flip `mvp_status`', '### C. Revise after...'.
      Fix: Renumber sub-operations as '### 1.', '### 2.', '### 3.' instead of '### A.', '### B.', '### C.'..
      Verify: grep -n '^### [A-Z]\.' skills/mission-revise/SKILL.md should return no output after the fix..

- [ ] [skill-management.progressive-disclosure] Two example files exceed 100 lines but lack a table of contents at the top. The spec MUST: 'include a table of contents at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope'.
      Where: /home/nolte/repos/github/claude-shared/skills/mission-revise/examples/01-revise-statement.md (109 lines) and examples/02-flip-mvp-status-to-achieved.md (103 lines) — neither file opens with a ToC..
      Fix: Prepend a short table of contents (a bulleted or numbered list of the H2 section names) immediately after the title line in each file that is over 100 lines..
      Verify: grep -n 'Table of contents\|## Contents\|\- \[' skills/mission-revise/examples/01-revise-statement.md returns a match in the first 10 lines; same for 02-flip-mvp-status-to-achieved.md..

#### `mkdocs-structure-apply` (skill)

**Critical**

- [ ] [skill-management.description-third-person-must] The `description` contains the imperative clauses `Invoke when the user asks` and `Don't use for`, which are second-person imperatives. The spec's MUST requires third person throughout. The primary capability statement (`Audits a repository…`) is correctly third person, but the trigger and negation clauses deviate. This pattern appears portfolio-wide (40+ skills), so this finding is skill-specific only to the extent the spec is enforced.
      Where: SKILL.md frontmatter `description` field — phrases: "Invoke when the user asks…" and "Don't use for theme/typography…".
      Fix: Rewrite the trigger clause in third person, e.g., "Invoke when" → "Use when" is still imperative; prefer a fully third-person form such as "Triggered when the user asks to apply, audit, scaffold, or patch MkDocs…" and "Not for theme/typography decisions…"..
      Verify: After editing, confirm the description contains no imperative verb forms (Invoke, Don't, Use, Run) directing the reader. Re-run `scripts/validate_skills.py` to confirm no new frontmatter errors..

**Warning**

- [ ] [skill-management.dont_use_when-overlap-should] The `dont_use_when` structured frontmatter field is missing the `docs-freshness-checker` alternative for drift-detection scenarios, even though the `description` prose explicitly calls it out as the redirect target. The catalog cross-linking pass derives auto-links from the structured field, not from prose, so the link from this skill to `docs-freshness-checker` will never be rendered.
      Where: SKILL.md frontmatter, `dont_use_when` list (currently 4 entries; drift-detection entry absent).
      Fix: Add a fifth `dont_use_when` entry: `situation: "You want drift detection or i18n-freshness checking"` / `alternative: docs-freshness-checker`. The artifact `agents/docs-freshness-checker.md` exists and is discoverable, so the resolvability check will pass..
      Verify: After adding the entry, run `task docs` (or `mkdocs build`) and confirm the generated catalog page for `mkdocs-structure-apply` renders a hyperlink to `docs-freshness-checker` in the "Don't use when" section..

- [ ] [skill-management.dont_use_when-overlap-should] `docs-freshness-checker` is referenced in the description prose as the redirect target for drift-detection scenarios, but it is absent from both `dont_use_when` (structured field) AND `see_also`. The spec SHOULD says authors should declare `see_also` and `dont_use_when` whenever overlap is likely. Since `docs-freshness-checker` is explicitly called out in the description text, its absence from the structured `see_also` list means the catalog's 'See also' section and the inbound 'Referenced by' section on the `docs-freshness-checker` catalog page will not surface this relationship.
      Where: SKILL.md frontmatter `see_also` list — currently ['docs-audience-tracks-apply', 'docs-dry-refactor', 'skill-agent-catalog-apply']; `docs-freshness-checker` absent.
      Fix: Add `docs-freshness-checker` to the `see_also` list and add a corresponding `dont_use_when` entry: `- situation: "You want drift detection for stale documentation" alternative: docs-freshness-checker`..
      Verify: Run `task docs` and confirm the `mkdocs-structure-apply` catalog page shows `docs-freshness-checker` in the 'Don't use when' and 'See also' sections, and that the `docs-freshness-checker` catalog page shows a 'Referenced by' back-link to `mkdocs-structure-apply`..

**Suggestion**

- [ ] [skill-management.evaluation-discipline-should] No `examples/` directory exists under the skill folder. The spec SHOULD includes at least three evaluation scenarios (input prompt, optional input files, expected behavior) so iteration is grounded in observable behavior rather than authoring intuition.
      Where: /home/nolte/repos/github/claude-shared/skills/mkdocs-structure-apply/ — only `SKILL.md` and `references/operations.md` present.
      Fix: Create `examples/` with at least three scenario files covering representative invocations, e.g., audit on a repo with an existing mkdocs.yml, scaffold on a fresh repo, and patch on a repo with a missing plugin baseline..
      Verify: Confirm three or more scenario files under `skills/mkdocs-structure-apply/examples/` each capturing a prompt and expected behavior description..

#### `permission-allowlist-maintain` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary-verb-closed-set] Five of seven sub-operation headings use verbs that are outside the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). Specifically: `### 1. Load the current allowlist` (Load), `### 2. Gather candidates` (Gather), `### 4. Reject forbidden pattern classes outright` (Reject), `### 5. Narrow the surviving candidates` (Narrow), and `### 7. Hand off to the PR flow` (Hand off) all violate the MUST. Only steps 3 and 6 use the conformant verb `Apply`.
      Where: SKILL.md lines 41, 47, 66, 76, 95 — the `### N. <verb>` headings inside `## Operations`.
      Fix: Replace each non-vocabulary verb with the closest conformant verb from the closed set. Suggested mapping: `Load` → `audit` (read-only inspection of the current allowlist), `Gather` → `run` (or split into `audit` if checking only), `Reject` → `patch` (additive decision gate) or fold the reject logic into the Apply step, `Narrow` → `patch`, `Hand off` → `close` (terminates the curation flow by dispatching to `pull-request-create`). Also amend `spec/claude/skill-management/` §Operations vocabulary if `reject` or `narrow` are genuinely needed as canonical verbs across other skills..
      Verify: Run `grep -n '^### [0-9]' skills/permission-allowlist-maintain/SKILL.md` and confirm every verb after the number is one of: `audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`..

**Warning**

- [ ] [skill-management.use-case-metadata-dont-use-when-should] The `dont_use_when` frontmatter field is absent even though the `description` already embeds an explicit negative trigger ('Don't use to edit `.claude/settings.local.json` or `~/.claude/settings.json` (out of scope per spec)'). The spec says authors SHOULD declare `dont_use_when` whenever overlap with other artefacts is likely; the `update-config` skill covers `.claude/settings.local.json` edits and `~/.claude/settings.json`, making overlap likely.
      Where: SKILL.md frontmatter (lines 1–13) — `dont_use_when` key is absent.
      Fix: Add a `dont_use_when` frontmatter list entry, for example: ```yaml dont_use_when:   - "you want to edit .claude/settings.local.json or ~/.claude/settings.json (use update-config instead)"   - "you need to configure hooks, environment variables, or other settings.json fields beyond permissions.allow"``` This makes the catalog machine-readable for cross-linking and removes the inline negative-trigger clause from `description`..
      Verify: Check that `dont_use_when` appears in the YAML frontmatter block and its values are non-empty strings conforming to the schema in `skill-agent-catalog` §Use-case metadata..

#### `portfolio-audit` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Operations 2 (Render), 3 (Bootstrap), and 4 (Discover tech stack) use verbs that are not in the closed operation vocabulary. The spec MUST requires each operation to use exactly one verb from: audit, scaffold, patch, apply, migrate, run, update, close. 'render', 'bootstrap', and 'discover' are all outside this vocabulary, and MUST NOT introduces new verbs without amending the spec list.
      Where: skills/portfolio-audit/SKILL.md lines 75, 89, 107 — headings '### 2. Render …', '### 3. Bootstrap …', '### 4. Discover tech stack'.
      Fix: Rename Operation 2 to 'update' (it mutates an existing artefact — the rendered docs), Operation 3 to 'scaffold' (greenfield create of project/portfolio.yml), and Operation 4 to 'audit' or propose a spec amendment to add 'discover' to the closed vocabulary before using it. All heading labels must then match the updated verb..
      Verify: grep '^### ' skills/portfolio-audit/SKILL.md — every verb after the period must appear verbatim in the closed vocabulary list in spec/claude/skill-management/en.md §Operations vocabulary..

- [ ] [skill-management.progressive-disclosure] Two example files referenced from SKILL.md exceed 100 lines but lack a table of contents at the top. The spec MUST requires any reference file longer than 100 lines to open with a table of contents so that partial-read previews still surface the file's full scope.
      Where: skills/portfolio-audit/examples/01-audit-detects-duplicate.md (116 lines, no TOC) and skills/portfolio-audit/examples/03-bootstrap-new-member.md (105 lines, no TOC).
      Fix: Add a '## Contents' (or equivalent) TOC section at the top of each file listing the major sections with inline anchors..
      Verify: head -20 skills/portfolio-audit/examples/01-audit-detects-duplicate.md and head -20 skills/portfolio-audit/examples/03-bootstrap-new-member.md must each show a table-of-contents section before any prose content..

- [ ] [skill-management.frontmatter-validation] Operation 4 ('Discover tech stack') has no trigger phrases in the frontmatter description field or in use_when entries, making it undiscoverable by automatic routing. The spec MUST requires the description to name both what the skill does and when to use it; with three of four operations covered and the fourth silently absent, the 'when to use it' contract is only partially fulfilled.
      Where: skills/portfolio-audit/SKILL.md frontmatter: description covers audit/render/bootstrap triggers only; use_when (lines 8–11) lists three entries for Audit, Render, and Bootstrap — Operation 4 is absent from both..
      Fix: Add a trigger phrase for Operation 4 to the frontmatter description (e.g., 'or to discover the tech stack of one or all portfolio repositories') and add a fourth entry to use_when (e.g., 'you want to discover the tech-stack composition of one or all portfolio-member repositories')..
      Verify: Check the frontmatter description and use_when list in SKILL.md each contain at least one trigger phrase that would route a user asking to 'discover the tech stack' or equivalent to this skill..

**Warning**

- [ ] [skill-management.evaluation-discipline] spec/claude/skill-management/en.md line 145 SHOULD requires at least three evaluation scenarios per non-trivial skill. The skill has four operations but only three example files (01-audit-detects-duplicate.md, 02-render-inventory-idempotent.md, 03-bootstrap-new-member.md). Operation 4 (Discover tech stack) has no example scenario.
      Where: skills/portfolio-audit/SKILL.md lines 144–146 (Examples section lists only 3 files); skills/portfolio-audit/examples/ directory contains no file for Operation 4.
      Fix: Add examples/04-discover-tech-stack.md covering a representative Discover tech stack invocation (scope selection, detection-source scan, drift/net-new findings output). Add the corresponding load-trigger line to SKILL.md's Examples section: 'Read examples/04-discover-tech-stack.md when running the Discover tech stack operation.'.
      Verify: ls skills/portfolio-audit/examples/ shows a 04-discover-tech-stack.md file; grep for the load-trigger phrase in SKILL.md.

#### `portfolio-inflight-triage` (skill) — clean

#### `project-structure-apply` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Operation `### 2. GitHub App installation check` uses a name that is not a verb from the closed operations vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec MUST: "name each operation with one verb from the closed vocabulary" and MUST NOT introduce new operation verbs without amending the list.
      Where: /home/nolte/repos/github/claude-shared/skills/project-structure-apply/SKILL.md line 57; also mirrored in /home/nolte/repos/github/claude-shared/skills/project-structure-apply/references/operations.md line 26.
      Fix: Rename to `### 2. Audit` with a parenthetical scope qualifier if needed (e.g. `### 2. Audit (GitHub App installation)`) — but the heading verb itself must be from the closed list. Alternatively, subsume this check into operation 1 (`### 1. Audit`) as a subsection, since it is a read-only verification step that fits the `audit` verb definition..
      Verify: Grep `### [0-9]\.` in SKILL.md and references/operations.md; every match must use exactly one verb from the closed vocabulary with no extra words after the verb (other than a parenthetical qualifier)..

#### `pull-request-create` (skill)

**Critical**

- [ ] [skill-management.description-third-person] The `description` field opens with `"Create a GitHub pull request…"` — imperative mood — and continues with `"Invoke when…"` — second-person imperative. The spec MUST is: write description in third person ("Generates …," "Reviews …"), never first or second person. After those two imperative sentences the description switches to third-person correctly (`Verifies…`, `Supports…`), making the opener inconsistent with the MUST.
      Where: skills/pull-request-create/SKILL.md line 3 (frontmatter `description:` field).
      Fix: Change `"Create a GitHub pull request…"` to `"Creates a GitHub pull request…"` and `"Invoke when the user asks…"` to `"Invokes when the user asks…"` (or restructure: `"Creates a GitHub pull request … when the user asks to open a PR, create a pull request, draft a PR description, create a merge request, or push the branch and open a PR."`)..
      Verify: Confirm the updated description opens with a third-person verb and contains no imperative or second-person clauses. Re-run `scripts/validate_skills.py` and confirm no `description-person` error..

- [ ] [pull-request-workflow.branch-freshness] Step 2 ("Ensure branch freshness") tells the agent to ask the user whether to synchronize via **merge** or **rebase** and states `"the spec permits either"`. This directly contradicts the pull-request-workflow spec §Branch freshness MUST: `"MUST use rebase (not merge) to perform the synchronization with develop"`. Offering merge as a peer option violates the MUST the skill claims to implement.
      Where: skills/pull-request-create/SKILL.md lines 72-76 (Operation 2, bullet 2).
      Fix: Remove the merge option from the user-choice prompt in Step 2. Rebase is the only permitted synchronization method per the governing spec. The agent should inform the user that rebase is required (explaining the default recommendation rationale is fine), execute `git rebase origin/develop`, and stop for conflict resolution if needed. The Hard Rules section at line 172 should also add `"Never use git merge origin/develop to synchronize the feature branch with develop; rebase is mandatory per pull-request-workflow §Branch freshness."`.
      Verify: Confirm Step 2 no longer presents merge as an alternative. Check that the pull-request-workflow §Branch freshness MUST (`"MUST use rebase (not merge)"`) is satisfied end-to-end by the skill's instruction text..

- [ ] [skill-management.operations-vocabulary] The `## Operations` block uses numbered sub-operations (`### 1. Collect change context`, `### 2. Ensure branch freshness`, etc.) which is conformant with the heading form `### N. <verb>`. However the operation verb in `### 2. Ensure branch freshness` uses `Ensure` — a verb not in the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). Steps 1, 3, 4, 5, 6 similarly use `Collect`, `Build`, `Build`, `Verify`, `Push and create` — none are in the declared vocabulary. This is a MUST under §Operations vocabulary.
      Where: skills/pull-request-create/SKILL.md lines 51-158 (every `### N. …` sub-operation heading).
      Fix: Map each sub-operation to the nearest closed-vocabulary verb: e.g. Step 1 → `### 1. audit` or keep as a named section inside a single `## Operations / run` block, Step 6 → `### 6. apply`. Alternatively, treat the whole skill as a single `run` operation (one-flow skill) with internal numbered phases — the spec allows numbered phases under a single `run` operation. Coordinate with the `operations-vocabulary` spec maintainer if the existing verbs are insufficient for PR-creation semantics..
      Verify: After revision, confirm every `### N. <verb>` heading uses a verb from `{audit, scaffold, patch, apply, migrate, run, update, close}` or that the numbered headings are explicitly phase labels under a single declared operation..

- [ ] [pull-request-workflow.branch-freshness] Example file examples/03-branch-lags-develop.md line 57 states 'Per the spec, both rebase and merge are permitted.' This is a direct false assertion about the pull-request-workflow spec, which at §Branch freshness explicitly states 'MUST use rebase (not merge) to perform the synchronization with develop' and parenthetically clarifies 'rebase is the spec-mandated synchronization method per the MUST below in this section, not a contributor preference'. Because this is an asset file an agent will read during operation (load-triggered from SKILL.md line 164), the incorrect claim actively guides runtime behavior toward a spec violation. This is a separate file from SKILL.md and is not covered by finding [1].
      Where: skills/pull-request-create/examples/03-branch-lags-develop.md line 57.
      Fix: Change 'Per the spec, both rebase and merge are permitted' to 'Per the spec, rebase is the only permitted synchronization method (MUST use rebase, not merge).' Then remove the rebase/merge trade-off framing in lines 57-62 and replace it with a single recommendation to rebase, consistent with the spec MUST..
      Verify: Read examples/03-branch-lags-develop.md and confirm no sentence claims merge is spec-permitted. Cross-check against pull-request-workflow spec §Branch freshness line 37..

**Warning**

- [ ] [skill-management.reference-file-toc] `examples/02-feat-pr-with-spec-touch.md` is 101 lines, which exceeds the 100-line threshold. The spec MUST says: `"MUST include a table of contents at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope."` No table of contents is present in that file.
      Where: skills/pull-request-create/examples/02-feat-pr-with-spec-touch.md (101 lines, no TOC).
      Fix: Add a short table of contents (e.g., `- [Input prompt](#input-prompt)`, `- [Input files](#input-files)`, `- [Expected behaviour](#expected-behaviour)`) directly below the first heading in `02-feat-pr-with-spec-touch.md`..
      Verify: Confirm the file opens with a `## Contents` or equivalent TOC immediately after the title heading, before any prose..

#### `pull-request-merge` (skill)

**Critical**

- [ ] [skill-management.description-third-person] The `description` field opens with the imperative/infinitive form "Promote an open draft pull request..." and contains "Invoke when the user asks..." — both are imperative mood, not the required third-person singular present tense ("Promotes …", "Reviews …"). The spec requires every description to be written in third person because it is injected into Claude's system prompt and inconsistent point-of-view degrades skill discovery.
      Where: SKILL.md frontmatter, `description` field, first sentence ("Promote") and trigger sentence ("Invoke when").
      Fix: Change the opening to "Promotes an open draft pull request on the current branch to a merged state on `develop`..." and the trigger sentence to "Invokes when the user asks to promote the draft PR, ship the PR, merge the draft, or bring the PR over the finish line." The remainder of the description ("Also handles ...", "Delegates ...", "Supports ...") is already third-person and requires no change..
      Verify: After the edit, confirm every verb in the `description` value is third-person singular present tense (ends in -s or is an auxiliary like "handles"), with no imperative verbs..

- [ ] [skill-management.operations-vocabulary] The `## Operations` block names its sub-operations with verbs outside the closed vocabulary declared in `skill-management` §Operations vocabulary. The closed vocabulary is: `audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`. The sub-operation headings in use are: Inspect, Delegate, Derive, Verify, Flip, Trigger, Verify, Close, Clean — all but "Close" (step 7c) are outside the vocabulary. The spec MUST rule reads: "name each operation with one verb from the closed vocabulary" and "MUST NOT introduce new operation verbs without amending this list".
      Where: SKILL.md lines 50–184: ### 1. Inspect …, ### 2. Delegate …, ### 3. Derive …, ### 4. Verify …, ### 5. Flip …, ### 6. Trigger …, ### 7. Verify …, ### 8. Clean ….
      Fix: Remap each step to the closest in-vocabulary verb, or split the skill body so the sequential procedure sits under a single top-level operation (e.g., `run`) and the numbered steps become unlabelled prose or inline-bold headings rather than `### N. <verb>` headings that trigger the vocabulary rule. Candidate mapping: step 1 → `audit` (read-only inspect), steps 2–6 → `run` or `apply`, step 7 → `audit`, step 7c → `close`, step 8 → `close`. Alternatively, propose an amendment to the closed-vocabulary list in `spec/claude/skill-management/` to add the needed verbs, then cite that amendment in the PR..
      Verify: After the edit, `grep -n '^### [0-9]' skills/pull-request-merge/SKILL.md` should show only verbs from {audit, scaffold, patch, apply, migrate, run, update, close}, and no verbs outside that set..

- [ ] [skill-management.operations-vocabulary] `### 7c. Close referenced tracking issues` uses an alphanumeric heading suffix (`7c`) that mixes a number with an alphabetic letter. The spec states: "alphabetic letters (`A.`/`B.`/`C.`) and `### Step N` are non-conformant". While `7c` is not a pure alphabetic letter, it violates the `### N. <verb>` (pure number) pattern and is structurally equivalent to the prohibited `A./B./C.` pattern.
      Where: SKILL.md line 158: `### 7c. Close referenced tracking issues`.
      Fix: Renumber step 7c as a standalone numbered step (e.g., `### 8. Close referenced tracking issues`) and shift the current step 8 to `### 9. Clean up local state`, or fold 7c into step 7's prose as a named subsection (bold heading, not an `### N.` heading)..
      Verify: `grep -n '^### ' skills/pull-request-merge/SKILL.md` should show only headings matching `^### \d+\.` with no letter suffix..

- [ ] [skill-management.progressive-disclosure] The spec MUST-requires a table of contents at the top of any reference file longer than 100 lines. Three files referenced from SKILL.md exceed 100 lines and have no TOC: `examples/01-clean-merge-via-automerge-label.md` (108 lines), `examples/02-pending-checks-reports-and-stops.md` (104 lines), and `examples/03-wait-mode-with-explicit-flag.md` (158 lines).
      Where: skills/pull-request-merge/examples/01-clean-merge-via-automerge-label.md (108 lines, no TOC); examples/02-pending-checks-reports-and-stops.md (104 lines, no TOC); examples/03-wait-mode-with-explicit-flag.md (158 lines, no TOC).
      Fix: Add a table of contents at the top of each of the three example files (below the H1 title, before the first section heading) listing the major H2 sections with anchor links so partial-read previews surface the full scope..
      Verify: Read the first 15 lines of each of the three example files and confirm a TOC section with anchor links is present before the first `## Input prompt` heading..

**Warning**

- [ ] [skill-management.skill-length] `SKILL.md` is 232 lines, exceeding the SHOULD soft target of roughly 150 lines. The spec recommends moving long-form content into referenced files under `references/` or `examples/` and using explicit load-trigger phrases to invoke progressive disclosure.
      Where: SKILL.md (232 lines total).
      Fix: The `## Preconditions` block (lines 40–47), the detailed `## Examples` inline summary (lines 204–207), and the `## Hard rules` block (lines 221–232) are all candidates to move into `references/` files with explicit load triggers. Target: bring SKILL.md under 150 lines..
      Verify: `wc -l skills/pull-request-merge/SKILL.md` should report fewer than 150 lines. Every moved block must have an explicit `Read references/<file>.md when <trigger>` phrase in the remaining SKILL.md body..

#### `quality-gate` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All six sub-operation headings under `## Operations` use multi-word descriptive phrases rather than a single verb from the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec MUSTs that each operation be named with one verb from that list and that sub-operations be titled `### N. <verb>`.
      Where: SKILL.md lines 47, 71, 91, 101, 117, 131 — headings: '1. Prefer Taskfile targets', '2. Detect native tooling (fallback)', '3. Run checks in parallel', '4. Parse each result', '5. Render the result table', '6. Overall verdict'.
      Fix: Replace each `### N. <phrase>` heading with a single closed-vocabulary verb. The entire gate is one composite `run` operation; a reasonable mapping is: rename the `## Operations` block to a single `### run` operation and demote the six numbered steps to prose sub-sections, or map them to the closest vocabulary verb (e.g., '3. run', '4. audit', '5. render' — but 'render' is not in the vocabulary). Simplest conformant shape: one top-level `### run` operation containing the six numbered prose steps without their own `###` headings..
      Verify: After the edit, `grep '^### [0-9]' skills/quality-gate/SKILL.md` returns only headings whose label is exactly one word from the closed vocabulary, or returns nothing if the steps are demoted to prose..

- [ ] [quality-gate.monorepo-subroot-behaviour] The spec MUSTs that subroot results be aggregated under the corresponding category row (one row per category, not one row per subroot per stack) and that the Details column carry per-subroot detail. It also MUSTs that the output table have exactly the four columns Check, Status, Runner, Details. Example 03 violates both: it shows a five-column table with an additional Stack column and explodes the table into six rows (one per subroot per check) rather than three category rows.
      Where: skills/quality-gate/examples/03-multi-language-monorepo.md lines 38–46 (table with Stack column and 6 rows); quality-gate spec §Output shape MUST ('single table with columns Check, Status, Runner, Details') and §Monorepo and subroot behaviour MUST ('aggregate subroot results under the corresponding category row … not by row explosion').
      Fix: Rewrite the example 03 table to three rows (Lint, Typecheck, Tests) using only the four mandated columns. Move per-subroot detail (e.g. 'backend: 0 errors; frontend: 0 errors, 2 warnings') into the Details column. Remove the Stack column entirely..
      Verify: After the fix, confirm the table has exactly four columns (Check, Status, Runner, Details) and three category rows, with per-subroot information appearing in the Details column rather than as separate rows..

**Warning**

- [ ] [quality-gate.timeouts-and-failure-handling] The bound spec SHOULDs that the exit code of the underlying tool be surfaced in the `Details` column so consumers can distinguish 'lint found 3 errors (exit 1)' from 'lint crashed (exit >1)'. The skill captures exit codes via `; echo "EXIT:$?"` but the table template in Step 5 and the example files show only counters and test counts in Details — no exit code is routed to that column.
      Where: SKILL.md lines 119–125 (Step 5 table template) and examples/01-task-targets-when-available.md lines 54–61, examples/02-native-fallback-no-taskfile.md lines 47–55, examples/03-multi-language-monorepo.md lines 36–46.
      Fix: Add the exit code to the Details column in the table template and example tables, e.g. `| Lint | fail | \`task lint\` | 3 errors, 0 warnings (exit 1) |`. A one-line addition to Step 5 is enough: 'Include the captured exit code in the Details cell.'.
      Verify: Check that the table template in Step 5 shows an exit-code placeholder in the Details column, and that all three example files include an exit code in at least one Details cell..

#### `readme-structure-apply` (skill)

**Warning**

- [ ] [skill-agent-catalog.use-case-metadata] The `description` prose names `audience-identify` as a 'don't use' case ('Don't use for … the audience artefact (`audience-identify`)') but the structured `dont_use_when` YAML list has no corresponding entry for it. `skill-agent-catalog` §Use-case metadata requires every `dont_use_when` entry to carry a resolvable `alternative` name so the catalog can render it as a link and run the resolvability check. The omission also means the catalog cross-linking pass never surfaces the `audience-identify` redirect for readers who scan the structured fields rather than the prose description.
      Where: SKILL.md frontmatter, `dont_use_when` list (lines 12–18); `see_also` list (lines 19–22).
      Fix: Add a fourth `dont_use_when` entry: `- situation: 'You want to identify or manage the audience artefact for a repository' / alternative: audience-identify`. Also add `audience-identify` to the `see_also` list so the catalog cross-links it..
      Verify: Run `task docs` and confirm the catalog page for `readme-structure-apply` renders an `audience-identify` link in both the 'Don't use when' and 'See also' sections without a docs-build resolvability error..

- [ ] [readme-structure.length-and-density] The skill's audit operation invents a 'hard fail at >250 lines' severity tier that has no basis in the spec it operationalises. `spec/project/readme-structure/` §Length and density states only a SHOULD for ~200 lines; the Acceptance Criteria say 'at most around 200 lines' — no threshold above 200 is defined, and no 'hard fail' category exists. The skill's own Hard rule 5 says 'Never invent requirements that don't appear in the spec', making this self-contradictory.
      Where: SKILL.md line 78: '… report a hard fail at >250 lines …' under `## Operations` §1 `audit`.
      Fix: Remove the '>250 lines = hard fail' tier. Replace it with language that faithfully mirrors the SHOULD: report the finding as a SHOULD-violation (drift) when the README exceeds ~200 lines, with no escalated severity above that, consistent with the spec's single SHOULD rule..
      Verify: Re-read `spec/project/readme-structure/` §Length and density and the Acceptance Criteria; confirm no threshold above 200 appears there and that the skill's audit language now matches exactly..

- [ ] [skill-agent-catalog.use-case-metadata] audience-doc-author and prose-vale-curator are both actively dispatched in the skill body (lines 38, 96, 111, 123) but are absent from the see_also frontmatter list (lines 19-22). Finding [3] only captures the absence of audience-identify. skill-agent-catalog §Use-case metadata says authors SHOULD declare see_also so the catalog cross-linking pass can connect related artefacts — the same SHOULD gap applies to these two agents. Both names resolve to discoverable agents (agents/audience-doc-author.md, agents/prose-vale-curator.md), so adding them would satisfy the resolvability check. The see_also list currently only names artifacts that also appear in dont_use_when, while the primary orchestration targets used inside the skill body are unlisted.
      Where: SKILL.md frontmatter see_also list (lines 19-22); body references at lines 38, 96, 111, 123.
      Fix: Add audience-doc-author and prose-vale-curator to the see_also list. The updated list would be: audience-doc-author, mkdocs-structure-apply, prose-vale-curator, audience-identify (also covering the gap from finding [3])..
      Verify: Run task docs and confirm the catalog cross-linking pass resolves all four see_also entries without build errors; confirm each entry renders as a hyperlink on the skill's catalog page..

**Suggestion**

- [ ] [skill-management.evaluation-discipline] `skill-management` §Evaluation discipline SHOULD ships at least three evaluation scenarios (input prompt, optional input files, expected behavior) under `examples/` or a sibling location for every non-trivial skill. This skill has no `examples/` folder and no evaluation scenarios. It is non-trivial: it has three distinct operations, a multi-step approval flow, and resume logic.
      Where: skills/readme-structure-apply/ directory — no `examples/` subfolder present.
      Fix: Create `skills/readme-structure-apply/examples/` with at least three scenario files: one for `audit` (a synthetic README with known drift), one for `scaffold` (an empty repo), one for `patch` (a README with a missing required section). Each file should state the input, the expected audit output, and the expected edits..
      Verify: Run `task test` (validates skill structure) and confirm `examples/` exists with at least three scenarios. Invoke the skill against each example scenario and verify the output matches expectations..

**Info**

- [ ] [skill-agent-catalog.use-case-metadata] `audience-identify` is referenced in the skill body in three places (lines 38, 89, 123) as a dispatch target, but it is absent from the `see_also` frontmatter field. `skill-agent-catalog` §Use-case metadata uses `see_also` entries to drive automatic catalog cross-linking; the omission means the catalog's cross-linking pass won't surface the `audience-identify` relationship even though the skill actively delegates to it.
      Where: SKILL.md frontmatter `see_also` list (lines 19–22).
      Fix: Add `audience-identify` to the `see_also` list (this is also covered by the Warning finding above on `dont_use_when`; if that fix is applied, this Info is subsumed)..
      Verify: Confirm `task docs` succeeds and the `readme-structure-apply` catalog page shows `audience-identify` under its 'See also' section..

#### `release-notes-curate` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary-must] Every sub-operation in the `## Operations` block MUST be named with a verb from the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The seven sub-operations are instead named with free-form phrases: "Resolve the open draft", "Detect project type", "Resolve audience artefact", "Derive the project-context bundle", "Build the augmentation block", "Disclose, confirm, write", "Re-run drift detection". None of these match the closed vocabulary.
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md lines 52–160, sub-headings `### 1.` through `### 7.`.
      Fix: Rename each sub-operation to a verb from the closed vocabulary. Candidate mappings: 1→`run` (or `audit`), 2→`audit`, 3→`audit`, 4→`run`, 5→`scaffold`, 6→`apply`, 7→`update`. If none of the eight verbs fit all seven operations, amend `skill-management` §Operations vocabulary before merging per the spec's own rule ("MUST NOT introduce new operation verbs without amending this list")..
      Verify: Read every `### N.` heading in the `## Operations` block and confirm each verb appears verbatim in the closed vocabulary list in `spec/claude/skill-management/en.md` §Operations vocabulary..

- [ ] [release-skill-layer.skill-a-conflict-must] The bound spec (`release-skill-layer` §Skill A §Operational contract) MUST: "when the audience artefact and the autodetected project type conflict … prefer the audience artefact as the human-confirmed signal, and emit the conflict into the body's `## Open questions` subsection (§Content placement) so the reviewer sees the disagreement; MUST NOT silently override the artefact with the autodetected type." Operation 3 (Resolve audience artefact) covers the absent-artefact case and states to prefer the artefact, but nowhere does the skill instruct Claude to detect the conflict, emit it into `## Open questions`, or forbid silent override. This leaves the spec's MUST unimplemented.
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md lines 76–84 (Operation 3) — conflict scenario absent.
      Fix: Add a bullet to Operation 3 (or Operation 2): "When the audience artefact's declared audiences are inconsistent with the autodetected project type (for example, the artefact lists 'downstream Python integrators' but the repo signals a Claude plugin), prefer the audience artefact as the human-confirmed signal and record the disagreement as a bullet under `## Open questions` in the augmentation block. Never silently override the audience artefact with the autodetected type.".
      Verify: Read Operation 3 and confirm a conflict-detection branch with the `## Open questions` emission instruction is present..

- [ ] [skill-management.description-third-person-must] The `description` field MUST be written in third person throughout. The first sentence is correctly third-person ('Augments the open release-drafter draft…'), but the trigger and don't-use clauses switch to imperative second-person: 'Invoke when the user asks…' and 'Don't use to publish…'. The spec states the description is injected into Claude's system prompt and inconsistent point-of-view degrades skill discovery.
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md line 3, `description:` field — phrases 'Invoke when' and 'Don\'t use to'.
      Fix: Rewrite the trigger and don't-use clauses in third person. Example: '… Invoke' → 'Invoked when the user asks to …'; 'Don't use to publish' → 'Not intended for publishing the release …'..
      Verify: Read the `description` field and confirm no imperative or second-person constructs remain..

- [ ] [skill-management.operations-vocabulary-heading-must] The spec at skill-management §Operations vocabulary (line 115) says MUST title sub-operations as '### N. <verb>' where the verb is a single word from the closed vocabulary, and explicitly states 'alphabetic letters (A./B./C.) and ### Step N are non-conformant'. The sub-operation format '### 1. Resolve the open draft' is non-conformant not only because the verb is wrong (finding [0]) but also because each heading includes a multi-word phrase after the number rather than a single closed-vocabulary verb. This is the same MUST but from the heading-form clause, which is independently violated from the vocabulary clause: even if the verbs were replaced with closed-vocabulary terms, the headings would still need to be single-word (e.g., '### 1. run' not '### 1. run the draft resolution').
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md lines 52, 61, 76, 87, 102, 136, 153 — all seven ### sub-operation headings carry multi-word descriptions after the number instead of a single closed-vocabulary verb.
      Fix: Rename each sub-operation heading to '### N. <single-closed-vocab-verb>' per the spec. Map the current headings to the vocabulary: Operation 1 → 'run' (default verb for a locating step), Operation 2 → 'audit' (read-only check), Operation 3 → 'audit', Operation 4 → 'apply' or 'run', Operation 5 → 'scaffold', Operation 6 → 'update', Operation 7 → 'run'. Agree on the mapping with the skill author and apply consistently..
      Verify: After the rename, each '### N.' heading contains exactly one word that appears in the closed vocabulary list (audit, scaffold, patch, apply, migrate, run, update, close)..

**Warning**

- [ ] [skill-management.dont-use-when-completeness-should] The description lists four explicit don't-use cases (publish the release; identify audiences; draft notes from scratch; scaffold issue/PR templates), but `dont_use_when` in the structured frontmatter lists only two (`release-publish-trigger`; `audience-identify`). The two omitted cases ('draft notes from scratch' → `audience-doc-author`; 'scaffold issue/PR templates' → `github-issue-templates-apply`) are referenced in `see_also` and the description but absent from the machine-readable `dont_use_when` list, making the catalog's cross-linking pass incomplete.
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md lines 12–16, `dont_use_when:` block.
      Fix: Add two more `dont_use_when` entries: `{ situation: 'You want to draft release notes from scratch rather than augment an existing draft', alternative: audience-doc-author }` and `{ situation: 'You want to scaffold issue or PR templates', alternative: github-issue-templates-apply }`..
      Verify: Read `dont_use_when` and confirm all four anti-trigger scenarios from the description are present as structured entries..

- [ ] [release-skill-layer.skill-a-open-questions-may] The spec at release-skill-layer §Content placement (line 67) says the Open questions subsection MAY be included inside the augmentation block, and Operation 5's template (line 127) shows it as '### Open questions'. The spec §Content placement says '## Open questions' (level-2 heading), while the skill template uses '### Open questions' (level-3 heading inside the block). Although MAY-class, the spec's Content placement section declares the heading level explicitly ('## Open questions subsection') and the skill's template deviates. This is a minor drift between the spec's prescribed heading level and the skill's template.
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md line 127 — template shows '### Open questions'; spec/project/release-skill-layer/en.md line 67 says '## Open questions subsection'.
      Fix: Align the heading level in the skill's augmentation template (line 127) with the spec. Either update the template to use '## Open questions' or propose a spec amendment clarifying that the heading level inside the augmentation block should be ### to match the surrounding block structure..
      Verify: The augmentation block template in Operation 5 and the spec's §Content placement agree on the heading level for the Open questions section..

**Suggestion**

- [ ] [skill-management.150-line-soft-target-should] SKILL.md is 191 lines, exceeding the 150-line soft target. The spec SHOULD keep `SKILL.md` under roughly 150 lines and move long-form content into referenced files. The spec's example bundles inline in Operations 4 (lines 91–96) and the augmentation-block template in Operation 5 (lines 106–132) are good candidates for extraction to `references/` with explicit load-trigger phrases.
      Where: /home/nolte/repos/github/claude-shared/skills/release-notes-curate/SKILL.md lines 91–132 (inline bundle diff recipes and full augmentation template).
      Fix: Move the per-project-type diff recipes (lines 91–96) into `references/project-bundles.md` alongside the existing bundle table, and move the augmentation block template (lines 106–132) into a new `references/augmentation-template.md`. Replace each with a one-line load-trigger in SKILL.md (e.g. 'Read `references/project-bundles.md` for diff recipes per project type'). This would bring SKILL.md below 150 lines..
      Verify: Re-count SKILL.md lines after extraction; confirm each extracted file has an explicit load-trigger phrase remaining in SKILL.md..

#### `release-publish-trigger` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All five operation names (`Resolve`, `Validate`, `Disclose`, `Verify`, and `Dispatch`) are outside the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec states "MUST name each operation with one verb from the closed vocabulary" and "MUST NOT introduce new operation verbs without amending this list".
      Where: SKILL.md lines 50, 56, 92, 104, 112 — `### 1. Resolve the open draft`, `### 2. Validate every pre-publish gate`, `### 3. Disclose the validated state and confirm`, `### 4. Dispatch`, `### 5. Verify the dispatch landed`.
      Fix: Rename the five operations to use only closed-vocabulary verbs. A plausible mapping: `1. audit` (resolve + validate), `2. run` (disclose + confirm), `3. run` (dispatch), `4. audit` (verify post-dispatch) — or rethink the decomposition so each operation corresponds to exactly one closed verb. If none of the eight verbs adequately cover a needed operation, open an amendment PR to `skill-management` §Operations vocabulary before using a new verb here..
      Verify: grep '^### [0-9]' skills/release-publish-trigger/SKILL.md shows only names matching the closed-vocabulary verb list.

- [ ] [skill-management.resumable-runs] The skill has 5 named internal phases and at least one explicit user-approval gate (step 3: "Block the dispatch until the operator confirms"), satisfying the OR-condition in `resumable-work` §Scope of applicability ("more than one internal phase that produces an intermediate artefact the operator would otherwise lose on interruption"). The skill omits `resumable: true` from frontmatter, violating `skill-management` §Resumable runs MUST.
      Where: SKILL.md frontmatter (line 1–20) — `resumable` field is absent. Relevant phase boundary: step 2 produces a gate-validation report; if the session crashes between step 3 confirmation and step 4 dispatch, the user must re-answer the confirmation gate..
      Fix: Add `resumable: true` to frontmatter and add a short clause to the `description` field (e.g., "Supports resume on re-invocation per spec/claude/resumable-work/."). Then implement the on-disk envelope under `.resume/release-publish-trigger/<run-id>.yml` per `spec/claude/resumable-work/` §State file envelope and §Checkpoint cadence..
      Verify: grep 'resumable' skills/release-publish-trigger/SKILL.md returns `resumable: true` in frontmatter AND a mention in the description. Then check that `.resume/release-publish-trigger/` is either created by a trial run or that its creation is covered by the implementation..

- [ ] [skill-management.frontmatter-validation] The `description` field contains the imperative phrase "Invoke when the user asks to …", which is second-person voice. The spec MUST requires description to be written in third person ("Generates …," "Reviews …") and explicitly prohibits second-person forms ("You can use this to …").
      Where: SKILL.md line 3, description field, toward the end: `"Invoke when the user asks to \"publish the release\"…"`.
      Fix: Replace the imperative with a third-person trigger clause, e.g. "Triggered when the user asks to 'publish the release', 'trigger release publish', 'ship the release', or equivalent German-language requests.".
      Verify: The description field contains no imperative or second-person constructions; every sentence reads as third person (subject is the skill, not the operator)..

- [ ] [skill-management.progressive-disclosure] Two example files exceed 100 lines but lack a table of contents at the top: examples/01-clean-dispatch-all-gates-pass.md (113 lines) and examples/03-required-checks-red-route-to-workflow-health.md (120 lines). The spec states 'MUST include a table of contents at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope.'
      Where: skills/release-publish-trigger/examples/01-clean-dispatch-all-gates-pass.md (line 1, no TOC present) and skills/release-publish-trigger/examples/03-required-checks-red-route-to-workflow-health.md (line 1, no TOC present).
      Fix: Add a `## Contents` or `## Table of Contents` section near the top of each of those two example files listing their major sections (e.g. Input prompt, Input files, Expected behavior)..
      Verify: After adding TOCs, confirm both files open with a ToC before any substantive content by reading their first 10 lines..

- [ ] [skill-management.resumable-runs] When `resumable: true` is added (per finding [1]), the skill's `description` will also need to mention resume support. The spec (skill-management line 151) states 'MUST mention resume support in the skill's description text whenever resumable: true is set'. Currently the description contains no such clause.
      Where: SKILL.md line 3 — description field contains no mention of resume, re-invocation, or interruption recovery..
      Fix: Add a short clause to the description such as 'Supports resume on re-invocation per spec/claude/resumable-work/ in case of session interruption between gate validation and dispatch confirmation.'.
      Verify: After adding resumable: true and the description clause, confirm the description contains a phrase matching 'resume' or 're-invocation'..

**Warning**

- [ ] [skill-management.authoring-quality] SKILL.md is 160 lines, exceeding the 150-line soft performance target. The spec states "SHOULD keep SKILL.md under roughly 150 lines as a soft target; move long-form content into referenced files." The `## Wait mode` section (lines 126–136) largely duplicates content already stated inside `### 5. Verify the dispatch landed` (lines 118–124) and could be moved to a referenced file or collapsed.
      Where: SKILL.md lines 126–136 (`## Wait mode`).
      Fix: Either collapse the `## Wait mode` section into a brief cross-reference to the relevant sub-section of `### 5.`, or move the full wait-mode detail into a `references/wait-mode.md` file with an explicit load-trigger phrase in `SKILL.md`..
      Verify: wc -l skills/release-publish-trigger/SKILL.md returns ≤150..

#### `roadmap-init` (skill)

**Critical**

- [ ] [skill-management.description-third-person] The `description` field opens with the imperative "Scaffold" instead of the required third-person form "Scaffolds". The spec explicitly mandates third-person (e.g. "Generates …", "Reviews …") and forbids imperative/second-person phrasing because the description is injected into Claude's system prompt.
      Where: SKILL.md frontmatter, `description` field, first word.
      Fix: Change "Scaffold the project planning pair" to "Scaffolds the project planning pair" (and review the rest of the description for any further imperative constructions)..
      Verify: Confirm the description field starts with a third-person singular present-tense verb form throughout..

- [ ] [skill-management.operations-vocabulary] All five `## Operations` sub-headings use verbs outside the spec's closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The verbs actually used — `Resolve`, `Draft` (×2), `Present`, `Write` — are not in the vocabulary, and the spec MUST is unconditional: "MUST name each operation with one verb from the closed vocabulary" and "MUST NOT introduce new operation verbs without amending this list".
      Where: SKILL.md lines 60, 67, 85, 95, 99 (### 1 through ### 5).
      Fix: Map every sub-operation to the nearest closed-vocabulary verb. Reasonable remappings: (1) `### 1. scaffold` — precondition-and-audience-resolution is the greenfield-create precondition; (2) `### 2. scaffold` — drafting goals.md is part of the same scaffold flow; (3) `### 3. scaffold` — drafting roadmap.md continues the scaffold; (4) `### 4. run` (or keep under the enclosing scaffold); (5) `### 5. scaffold` (the actual write step). Alternatively, collapse all steps under a single `### 1. scaffold` operation with numbered sub-steps as prose, per the spec's allowance for a single `run` operation when a skill has one operation..
      Verify: Grep `### [0-9]` in SKILL.md and confirm every operation verb is drawn from the eight-word closed vocabulary..

#### `roadmap-plan` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All five operation verbs — `add`, `promote`, `retarget`, `transition`, `mvp-flip` — and the sixth sub-heading `Validate every write end-to-end` lie outside the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec says MUST name each operation with one verb from the closed vocabulary and MUST NOT introduce new verbs without amending the list.
      Where: SKILL.md lines 51, 68, 76, 87, 103, 112 (all six `### N.` sub-headings under `## Operations`).
      Fix: Map each operation to the nearest allowed verb or open a spec amendment PR to add the needed verbs to the closed vocabulary before merging. Possible mappings: `add` → `scaffold`, `promote` → `update`, `retarget` → `update`, `transition` → `update` or `close`, `mvp-flip` → `update`, `Validate every write end-to-end` → `audit`. If the domain semantics genuinely require new verbs, amend `spec/claude/skill-management/en.md §Operations vocabulary` first, then update the skill headings..
      Verify: After the fix, grep the `## Operations` block for any sub-heading verb not in the allowed set: `grep -E '^### [0-9]+\.' skills/roadmap-plan/SKILL.md | grep -Ev '\b(audit|scaffold|patch|apply|migrate|run|update|close)\b'` should return no output..

**Warning**

- [ ] [spec/project/mission.smart-contract-achievable] The mission spec MUST requires every roadmap item with `mvp: true` to carry `detail: fine` and a non-null `target_sprint` (the achievability constraint). The skill's `add` operation (§1) and end-to-end validation (§6) only enforce `fine` detail when `target_sprint` resolves to the current or next sprint, leaving MVP items targeted at sprint N+2 or beyond free to carry `detail: coarse` or `backlog`, which violates the achievability bound.
      Where: SKILL.md lines 58–65 (add operation, step 4) and lines 112–122 (§6 validation checklist); mission spec §SMART contract §Achievable.
      Fix: In §6's validation checklist add: 'Every item with `mvp: true` carries `detail: fine` and a non-null `target_sprint`'. Mirror this gate in the `add` and `mvp-flip` operations: when `mvp: true` is set or requested, require the caller to supply `detail: fine` and a non-null sprint before proceeding..
      Verify: Trace through the `add` flow with `mvp: true`, `detail: coarse`, `target_sprint: 5` (beyond next sprint) and confirm the skill refuses the mutation with a verbatim error citing `spec/project/mission/ §SMART contract`..

- [ ] [spec/project/mission.stabilisation-gate] The mission spec MUST says post-MVP roadmap items (`mvp: false`) MUST NOT transition `proposed → active` while `mvp_status` is `defining`, `in_progress`, or `achieved`; the transition is permitted only when `mvp_status: stabilised`. The skill's `transition` operation (§4) lists additional gates only for `active → done` and `proposed → active` (general consistency), but never reads `project/mission.md` to check the stabilisation gate.
      Where: SKILL.md lines 87–101 (§4 transition operation); mission spec §Stabilisation gate.
      Fix: In §4's `proposed → active` gate add a check: when `project/mission.md` exists and the item carries `mvp: false`, read `mvp_status`; if it is `defining`, `in_progress`, or `achieved`, refuse the transition with a verbatim error citing `spec/project/mission/ §Stabilisation gate`. Also add this check to §6's validation checklist..
      Verify: Invoke the transition operation on a `mvp: false` item with `mvp_status: in_progress` and confirm refusal with the required verbatim error..

- [ ] [spec/project/mission.smart-contract-achievable] The mission spec MUST says an unbounded MVP scope — every roadmap item flagged `mvp: true` — MUST be rejected by consuming skills with a verbatim error. The skill has no detection or rejection logic for this case, either in the `mvp-flip` operation or in the end-to-end validation pass.
      Where: SKILL.md §5 (mvp-flip, lines 103–110) and §6 (validation, lines 112–122); mission spec §SMART contract §Achievable.
      Fix: In the `mvp-flip` (false → true) flow, after the stabilisation check, count the current number of `mvp: true` items in `project/roadmap.md`. If flipping this item would leave every item in the roadmap as `mvp: true`, refuse with a verbatim error citing the mission spec's achievability rule. Also add the check to §6..
      Verify: Simulate a roadmap where all items except one are `mvp: true`, then attempt to flip the last `mvp: false` item. Confirm the skill refuses with a verbatim error naming the mission spec..

- [ ] [spec/project/mission.smart-contract-achievable] The mission spec §SMART contract §Achievable says every roadmap item with `mvp: true` must carry a non-null `target_sprint`. The skill's `add` operation (§1) allows `target_sprint: null` even when `mvp: true` is set (line 57–58 never refuses null for mvp:true items), and the end-to-end validation (§6, lines 116–121) has no check that enforces non-null `target_sprint` for mvp:true items. An operator can add an mvp:true item with `target_sprint: null` without any refusal.
      Where: SKILL.md lines 57–58 (add operation, target_sprint collection) and lines 116–121 (§6 validation checklist); mission spec §SMART contract §Achievable and acceptance criteria line 118.
      Fix: In the `add` operation step 1, when the user sets `mvp: true`, refuse `target_sprint: null` with a verbatim error citing mission spec §Achievable. In §6 validation, add a check: every item with `mvp: true` must carry a non-null `target_sprint`; refuse the write when this check fails..
      Verify: Attempt to add a roadmap item with `mvp: true` and `target_sprint: null`; the skill must refuse with a verbatim error. Also verify that the end-to-end validation pass catches an existing mvp:true item whose `target_sprint` is null..

#### `roadmap-refine` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary-must-closed-verb] All five sub-operation headings under ## Operations use verbs outside the closed vocabulary. The headings are '1. Resolve the current and next sprint', '2. Walk the roadmap', '3. Emit violation records', '4. Walk fix proposals per item', and '5. Final report'. The spec states each operation MUST be named with one verb from the closed vocabulary (audit, scaffold, patch, apply, migrate, run, update, close), and sub-operations MUST be titled as '### N. <verb>' (single verb). None of Resolve, Walk, Emit, or 'Final report' appear in the closed vocabulary, and all headings use multi-word phrases rather than single verbs.
      Where: SKILL.md lines 56, 70, 79, 98, 112 — the five ### sub-operation headings inside ## Operations.
      Fix: Map the five steps to vocabulary-conformant names and collapse or re-split as needed. A reasonable mapping: step 1 ('Resolve...') and step 2 ('Walk...') together form the 'audit' operation (read-only invariant check); step 4 ('Walk fix proposals') is the 'patch' or 'apply' operation; step 5 ('Final report') can be absorbed into the enclosing operation's exit text rather than a separate heading. Alternatively, model the entire skill as a single 'apply' operation (audit + patch in one flow) with the numbered steps retitled using vocabulary verbs: '### 1. audit', '### 2. patch', etc..
      Verify: grep '^### [0-9]' skills/roadmap-refine/SKILL.md and confirm every verb after the number is one of: audit, scaffold, patch, apply, migrate, run, update, close..

- [ ] [skill-management.frontmatter-description-third-person-must] The description field contains second-person imperative language: 'Don't use to add items, retarget sprints, or flip MVP flags (use `roadmap-plan`); don't use to scaffold the roadmap from scratch (use `roadmap-init`).' The spec MUST requires the description to be written in third person and explicitly forbids second person ('You can use this to ...'). 'Don't use' is an unambiguous second-person imperative directed at the reader.
      Where: SKILL.md line 3, description field — 'Don't use to add items...; don't use to scaffold...'.
      Fix: Rewrite the negative boundary in third person: replace 'Don't use to add items, retarget sprints, or flip MVP flags (use `roadmap-plan`); don't use to scaffold the roadmap from scratch (use `roadmap-init`)' with 'Does not add, retarget, or flag-flip items (use `roadmap-plan`); does not scaffold a new roadmap (use `roadmap-init`).'.
      Verify: Read the full description field and confirm no word is a second-person imperative ('Invoke', 'Don't', 'Use', 'Run', etc. used as directives to the reader)..

- [ ] [skill-management.progressive-disclosure-toc-must] examples/03-walk-fixes-promote-and-retarget.md is 132 lines, which exceeds the 100-line threshold. The spec MUST requires a table of contents at the top of any reference file longer than 100 lines so partial-read previews still surface the file's full scope. No table of contents is present.
      Where: skills/roadmap-refine/examples/03-walk-fixes-promote-and-retarget.md — 132 lines, no ToC.
      Fix: Add a '## Contents' or '## Table of Contents' section at the top of the file (after the title heading) listing the major sections: Input prompt, Input files, Expected behavior (each scenario step). A 3-5 item ToC suffices..
      Verify: Confirm the file opens with a table of contents after the H1 title: wc -l should still show >100 lines and the ToC should appear within the first 15 lines..

**Warning**

- [ ] [skill-management.authoring-quality-consistent-terminology-should] The use_when entry on line 10 reads 'you want to promote roadmap items from coarse/medium to fine'. The term 'medium' is not a valid value of the roadmap item detail enum. The roadmap spec (spec/project/roadmap/en.md §roadmap.md shape) declares the detail enum as exactly three values: fine, coarse, backlog. 'medium' does not exist in the schema. Using a non-schema term in the discovery metadata introduces inconsistency and may mislead operators about the skill's scope.
      Where: SKILL.md line 10 — use_when entry: 'you want to promote roadmap items from coarse/medium to fine'.
      Fix: Replace 'coarse/medium' with 'coarse/backlog' to match the actual enum values declared in the roadmap spec..
      Verify: Grep the spec for the detail enum: grep -n 'detail.*enum\|fine.*coarse.*backlog' spec/project/roadmap/en.md and confirm only fine, coarse, backlog are defined. Then confirm the use_when entry uses no other terms..

#### `skill-agent-catalog-apply` (skill)

**Critical**

- [ ] [skill-management.authoring-quality-token-cap] SKILL.md is approximately 6,500 tokens (26,119 bytes at ~4 chars/token), exceeding the 5,000-token hard cap. The spec states: "MUST keep SKILL.md under 500 lines and 5,000 tokens (the 5,000-token figure is the genuine hard cap); content beyond that MUST move into references/, templates/assets/, or scripts/ and MUST carry an explicit load-trigger phrase."
      Where: /home/nolte/repos/github/claude-shared/skills/skill-agent-catalog-apply/SKILL.md — full body (~26,119 bytes, 268 lines).
      Fix: Migrate the bulk of Operations §2 (the full generator-hook specification in §2.3, ~80 lines of dense hook-behaviour rules) and the detailed Audit criteria table (§1, ~20 lines) into a `references/generator-spec.md` file. Add explicit load-trigger phrases in SKILL.md: e.g. "Read `references/generator-spec.md` when writing or reviewing the `gen_catalog.py` hook." This should bring SKILL.md comfortably under 5,000 tokens while preserving all content..
      Verify: Re-count tokens after refactoring. With tiktoken or a rough estimate at ~4 chars/token, the byte count of SKILL.md should drop below ~20,000 bytes..

- [ ] [skill-management.operations-vocabulary] Operations 2, 3, and 4 use verbs outside the closed vocabulary (audit, scaffold, patch, apply, migrate, run, update, close). The spec states "MUST name each operation with one verb from the closed vocabulary" and "MUST NOT introduce new operation verbs without amending this list." Operation 2 is titled "Propose and apply changes" (multi-word; "Propose" is not in vocab), Operation 3 is titled "Verify" (not in vocab), and Operation 4 is titled "Adding further source roots later" (gerund; not in vocab).
      Where: /home/nolte/repos/github/claude-shared/skills/skill-agent-catalog-apply/SKILL.md lines 74, 170, 182.
      Fix: Rename: Op 2 → "### 2. Apply" (the full audit-then-patch flow matches the `apply` definition), Op 3 → "### 3. Run" (verification is the terminal execution step; alternatively petition to add `verify` to the vocab by amending skill-management), Op 4 → "### 4. Update" (adding further source roots is a mutation of existing config). If `verify` is the preferred term for Op 3, open a PR that amends the closed vocab in spec/claude/skill-management/en.md first..
      Verify: After renaming, grep SKILL.md for `^### [0-9]\+\.` and confirm every operation title uses exactly one word from the closed vocabulary..

- [ ] [skill-management.frontmatter-validation-description-person] The `description` field contains second-person imperative language: "Don't use for authoring individual skills/agents". The spec states "MUST write description in third person ('Generates …,' 'Reviews …'), never first or second person." "Don't use" is an imperative addressed to the reader, which is second-person voice.
      Where: /home/nolte/repos/github/claude-shared/skills/skill-agent-catalog-apply/SKILL.md line 3, description field — phrase "Don't use for authoring...".
      Fix: Rewrite the exclusion clause in third person: e.g. "Not for authoring individual skills or agents (use `skill-management`) or for general MkDocs scaffolding (use `project-structure-apply`)." The structured `dont_use_when` frontmatter field already captures these exclusions correctly; the inline reference in `description` can be shortened or removed..
      Verify: Re-read the full description value and confirm it contains no imperative or second-person constructions. The structured `dont_use_when` block satisfies the catalog's use-case display; the description needs only to cover what and when in third person..

- [ ] [skill-management.progressive-disclosure-toc] Two example files exceed 100 lines but do not open with a table of contents. The spec states "MUST include a table of contents at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope." `examples/01-plugin-mode-fresh-wireup.md` is 104 lines and `examples/03-drift-tracked-catalog-md.md` is 109 lines; neither contains a ToC.
      Where: /home/nolte/repos/github/claude-shared/skills/skill-agent-catalog-apply/examples/01-plugin-mode-fresh-wireup.md (104 lines, no ToC); /home/nolte/repos/github/claude-shared/skills/skill-agent-catalog-apply/examples/03-drift-tracked-catalog-md.md (109 lines, no ToC).
      Fix: Add a short ToC section near the top of each file (after the H1 title), listing the major headings with anchor links. For example: `## Contents\n- [Input prompt](#input-prompt)\n- [Input files](#input-files)\n- [Expected behavior](#expected-behavior)\n- [Expected output](#expected-output)`. Alternatively, trim each file to under 100 lines if any content can be removed..
      Verify: After adding ToCs, read the first 20 lines of each file and confirm a ToC section is present listing the major headings..

#### `skill-management` (skill)

**Critical**

- [ ] [skill-management.frontmatter-description-person] The `description` field opens with "Author or revise…" — an imperative/infinitive form, not third person. The spec MUST-requires third person ("Generates …," "Reviews …") because the description is injected into Claude's system prompt and inconsistent point-of-view degrades skill discovery.
      Where: SKILL.md frontmatter, `description:` value, first two words.
      Fix: Rewrite the description opening to third person, e.g. "Authors or revises Claude Code skills in the nolte-shared plugin source tree. Invoke when …" — keep the rest of the text intact..
      Verify: Confirm the first verb ends with -s / -es and no imperative or second-person phrasing remains in the description..

- [ ] [skill-management.operations-vocabulary] The `## Operations` block uses the verb `Create` (in `### 1. Create a new skill`) and `Revise` (in `### 2. Revise`). Neither verb is in the closed operations vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec MUST-requires each sub-operation to use exactly one verb from that vocabulary; introducing new verbs is explicitly forbidden without amending the list.
      Where: SKILL.md §Operations, headings `### 1. Create a new skill` and `### 2. Revise`.
      Fix: Rename `### 1. Create a new skill` to `### 1. Scaffold` (matches the vocabulary's `scaffold` for greenfield create) and `### 2. Revise` to `### 2. Patch` (additive fix to an existing artefact) or `### 2. Update` (mutate an existing artefact), whichever intent fits better..
      Verify: Grep `## Operations` block headings; every `### N.` line starts with a verb from the closed vocab..

- [ ] [skill-management.operations-sub-op-heading] The `### Review / audit` heading is non-conformant on two counts: (1) it carries no number (`### 3.`), and (2) it uses a compound slash form rather than a single verb. The spec MUST-requires sub-operations to be titled `### N. <verb>` (numbered) and uses a single closed-vocabulary verb.
      Where: SKILL.md §Operations, heading `### Review / audit`.
      Fix: Either remove this heading entirely (the section already states it is out of scope and defers to `skill-review`, so it can remain as a short prose paragraph under `## Operations` without its own `###` heading), or rename it to `### 3. Audit` if a numbered sub-operation entry is desired (noting that `audit` is in the vocabulary as a read-only check)..
      Verify: After edit, confirm no `###` heading inside `## Operations` lacks a number prefix or uses a verb outside the closed vocabulary..

- [ ] [skill-management.frontmatter-description-person] The description contains additional second-person and imperative instances beyond the opening 'Author or revise' that finding [0] cited: 'Invoke when the user asks…' (imperative) and 'Don't use to review or audit…' (second-person negative imperative). The spec MUST prohibits both first and second person throughout the entire description field, not only at its opening.
      Where: SKILL.md frontmatter, `description:` value — 'Invoke when the user asks to create…' and 'Don't use to review or audit an existing skill…'.
      Fix: Rewrite the entire description in strict third person throughout. E.g. 'Invoke when' → 'Use when'; 'Don't use to review or audit' → 'Does not review or audit existing skills against the spec'. All imperative and second-person forms must be converted..
      Verify: Confirm no bare-infinitive, imperative, or second-person forms ('Don't', 'Invoke', 'Use when') remain anywhere in the `description:` value. The corrected description must read as a factual third-person statement about the skill's behavior from start to finish..

**Warning**

- [ ] [skill-management.operations-sub-op-heading] The heading '### 1. Create a new skill' carries extra words after the single verb: 'a new skill'. The spec requires sub-operations to be titled '### N. <verb>' — a number followed by exactly one verb from the closed vocabulary, with no trailing noun phrase. While the vocabulary violation (Create not in vocab) is already covered by finding [1], the extended phrase beyond the single-verb format is an independent conformance gap in the heading structure.
      Where: SKILL.md §Operations, heading '### 1. Create a new skill' — the words 'a new skill' following the verb.
      Fix: Replace with a heading that uses only a single closed-vocabulary verb, e.g. '### 1. scaffold' (the correct vocabulary term for greenfield skill creation). Remove the noun phrase..
      Verify: After correction, confirm the heading matches '### N. <verb>' exactly, with the verb being one of: audit, scaffold, patch, apply, migrate, run, update, close..

#### `skill-review` (skill)

**Critical**

- [ ] [skill-management.frontmatter-description-third-person] The description opens with the base form "Review a Claude Code skill…" rather than third-person singular present tense ("Reviews…"), as required by skill-management §Frontmatter validation ("Generates …," "Reviews …").
      Where: SKILL.md, frontmatter `description:` field, first word..
      Fix: Change the opening word from `Review` to `Reviews` so the description reads "Reviews a Claude Code skill against…". The peer skill `agent-review` carries the same issue and should be fixed in the same PR..
      Verify: Confirm the description starts with `Reviews` (third-person singular). Run `grep '^description:' skills/skill-review/SKILL.md` and check the first token..

- [ ] [skill-management.progressive-disclosure-load-trigger] Three assets under `examples/` — `examples/01-fresh-review.md`, `examples/02-update-after-fix.md`, and `examples/03-close-plan.md` — exist in the skill folder but carry no load-trigger phrase in `SKILL.md`. Only `examples/walkthrough.md` is referenced. Per skill-management §Progressive disclosure: every asset under `examples/` MUST carry an explicit load-trigger phrase ("Read X when Y" or "See X for <specific concern>") in `SKILL.md`; without it, the files are unreachable under progressive disclosure.
      Where: SKILL.md body — no line references `01-fresh-review.md`, `02-update-after-fix.md`, or `03-close-plan.md`..
      Fix: Add explicit load-trigger phrases for each of the three files, for example: "See `examples/01-fresh-review.md` for a complete example of a fresh review run", "See `examples/02-update-after-fix.md` for checking off fixed items", "See `examples/03-close-plan.md` for closing a plan". Place them near the existing `examples/walkthrough.md` reference on line 105..
      Verify: Grep SKILL.md for each filename: `grep -n '01-fresh-review\|02-update-after-fix\|03-close-plan' skills/skill-review/SKILL.md` should return three hits, each containing a "See … for" or "Read … when" phrase..

- [ ] [skill-management.progressive-disclosure-load-trigger] templates/plan.template.md is referenced twice in SKILL.md (lines 77 and 103) but neither reference carries an explicit load-trigger phrase with a 'when' or 'for' clause as required. Line 77 reads 'Draft the plan from `templates/plan.template.md`' and line 103 reads 'The template at `templates/plan.template.md` is the starting point' — both lack the required 'Read X when Y' or 'See X for Z' pattern with an explicit trigger clause.
      Where: SKILL.md lines 77 and 103 — references to templates/plan.template.md.
      Fix: Replace or supplement the references with explicit load-trigger phrases, e.g. 'Read templates/plan.template.md when drafting a new review plan (Operation 1, step 8)' and 'See templates/plan.template.md for the authoritative plan scaffolding structure.'.
      Verify: Confirm SKILL.md contains at least one reference to templates/plan.template.md matching the pattern 'Read <path> when <condition>' or 'See <path> for <specific concern>' with an explicit 'when' or 'for' clause, per skill-management §Progressive disclosure line 125..

#### `skills-agents-sweep` (skill)

**Critical**

- [ ] [skill-management.frontmatter-validation-naming-convention] The plugin's declared naming convention is verb-noun form (e.g. `pull-request-create`, `roadmap-init`, `dependency-audit`). The name `skills-agents-sweep` follows a noun-noun-verb pattern. While the spec records this as a SHOULD and acknowledges the plugin is committed to verb-noun, the deviation is worth noting for consistency reviews.
      Where: /home/nolte/repos/github/claude-shared/skills/skills-agents-sweep/SKILL.md, frontmatter `name: skills-agents-sweep`.
      Fix: If renaming is feasible, consider `sweep-skills-agents` or a similar verb-first form. This is not blocking but documents the deviation for future portfolio rename consideration..
      Verify: Compare against `ls skills/` to confirm the pattern; no action is required if the portfolio rename is not planned..

**Warning**

- [ ] [skill-management.progressive-disclosure-file-references] The `templates/sweep-report.template.md` reference at line 75 uses `Use \`templates/sweep-report.template.md\`` with no explicit `when` or `for` clause. The spec requires the pattern `"Read <path> when <condition>"` or `"See <path> for <concern>"` with an explicit `when` or `for` keyword.
      Where: /home/nolte/repos/github/claude-shared/skills/skills-agents-sweep/SKILL.md, line 75 — "Use `templates/sweep-report.template.md`. Fill every frontmatter field.".
      Fix: Rewrite the reference to conform to the required pattern, for example:`Read \`templates/sweep-report.template.md\` when drafting the consolidated report in phase 3.` This ensures progressive disclosure works as designed..
      Verify: Grep for the pattern; confirm the line contains either ` when ` or ` for ` after the backtick-quoted path..

- [ ] [skill-management.progressive-disclosure-file-references] Four supporting files exceed 100 lines and none has a table of contents at the top: `examples/01-baseline-sweep.md` (122 lines), `examples/02-cross-cutting-discovery.md` (106 lines), `examples/03-wave-implementation.md` (130 lines), and `templates/sweep-report.template.md` (259 lines). The spec MUST: "include a table of contents at the top of any reference file longer than 100 lines, so partial-read previews still surface the file's full scope."
      Where: /home/nolte/repos/github/claude-shared/skills/skills-agents-sweep/examples/01-baseline-sweep.md (122 lines), examples/02-cross-cutting-discovery.md (106 lines), examples/03-wave-implementation.md (130 lines), templates/sweep-report.template.md (259 lines) — none opens with a ToC.
      Fix: Add a `## Contents` section with anchor links at the top of each of these four files, listing every `##`-level section they contain. The ToC must appear before the first section heading so it's visible in a partial read..
      Verify: Run `head -20` on each of the four files and confirm a ToC section is present..

#### `spec` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Four of five operations use verbs outside the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). `### 1. Create` must be `scaffold`; `### 3. Drift check` must be `audit`; `### 4. Regenerate index` uses `regenerate` which is not in the vocabulary; `### 5. Coverage / duplicate check` uses `coverage` which is not in the vocabulary.
      Where: /home/nolte/repos/github/claude-shared/skills/spec/SKILL.md lines 83, 102, 110, 118 (`### 1. Create`, `### 3. Drift check`, `### 4. Regenerate index`, `### 5. Coverage / duplicate check`).
      Fix: Rename: `### 1. Create` → `### 1. scaffold`, `### 3. Drift check` → `### 3. audit`, `### 4. Regenerate index` → `### 4. update` (index regeneration mutates an existing artefact), `### 5. Coverage / duplicate check` → `### 5. audit` (read-only check). If two operations map to `audit`, distinguish them with a qualifier in the description paragraph rather than in the heading verb..
      Verify: All five `### N. <verb>` headings use a verb from the closed vocabulary. `grep '### [0-9]' skills/spec/SKILL.md` returns only allowed verbs..

- [ ] [skill-management.frontmatter-validation] The `description` field opens with base/imperative-form verbs (`Create, translate, index, deduplicate, and drift-check ...`) rather than third-person singular as required. The spec mandates third person ('Generates …,' 'Reviews …') so the description renders consistently when injected into Claude's system prompt.
      Where: /home/nolte/repos/github/claude-shared/skills/spec/SKILL.md line 3 (`description:` value, first word `Create`).
      Fix: Rewrite the opening clause in third-person singular: e.g., `Creates, translates, indexes, deduplicates, and drift-checks multilingual specifications ...`.
      Verify: Description starts with a third-person singular verb. Run `python3 -c "import re, sys; txt=open('skills/spec/SKILL.md').read(); m=re.search(r'description: (.+)', txt); print(m.group(1)[:30])"` and confirm the first word ends in `-s`..

- [ ] [skill-management.operations-vocabulary] `### 2. Update / prevent drift` is a compound multi-word heading. The spec SHOULD requires operation names to be short (single word). `Update / prevent drift` carries two concepts in the heading verb slot.
      Where: /home/nolte/repos/github/claude-shared/skills/spec/SKILL.md line 93 (`### 2. Update / prevent drift`).
      Fix: Shorten to `### 2. update` (the vocabulary-conformant verb) and move the 'prevent drift' clarification into the body of the section..
      Verify: `grep '### 2' skills/spec/SKILL.md` returns `### 2. update` only..

- [ ] [skill-management.operations-vocabulary] The spec MUST: 'title sub-operations as ### N. <verb> (numbered)'. `### 3. Drift check`, `### 4. Regenerate index`, and `### 5. Coverage / duplicate check` all carry multi-word labels that do not conform to the `### N. <verb>` heading format. Finding [0] correctly flags the vocabulary violations but does not separately call out that the heading form itself (extra words after the verb position) also violates the MUST heading-format rule independently of the vocabulary rule.
      Where: /home/nolte/repos/github/claude-shared/skills/spec/SKILL.md lines 102, 110, 118 (`### 3. Drift check`, `### 4. Regenerate index`, `### 5. Coverage / duplicate check`).
      Fix: Rename to single-verb vocabulary headings: `### 3. audit`, `### 4. update` (or another in-vocab verb), `### 5. audit` (or split into a separate named operation). Each heading MUST be `### N. <single-vocab-verb>` with no additional words..
      Verify: Confirm each operation heading matches the regex `^### [0-9]+\. (audit|scaffold|patch|apply|migrate|run|update|close)$`..

**Warning**

- [ ] [skill-management.frontmatter-validation] Skill name `spec` is a pure noun. The `nolte-shared` plugin convention (recorded in skill-management §Frontmatter validation) requires all skills to follow verb-noun form (e.g., `spec-manage`, `spec-author`). The rule states 'New skills in this plugin MUST follow the verb-noun convention; mixing in a gerund-form name would itself violate the mixed-forms ban.' The name drifts from the established surface (`pull-request-create`, `roadmap-init`, `feature-decompose`, `dependency-audit`).
      Where: /home/nolte/repos/github/claude-shared/skills/spec/SKILL.md line 2 (`name: spec`); folder `skills/spec/`.
      Fix: Rename to a verb-noun form, e.g., `spec-manage` or `spec-author`. This is a breaking change: update the folder name, frontmatter `name`, any `subagent_type:` callers, the `.claude-plugin/` manifest, and `see_also` references in sibling skills (`spec-drift-audit`, `spec-readiness-reviewer`). Ship with a deprecation note on the old name per skill-vs-agent §Portfolio-wide consistency..
      Verify: After rename: `grep 'name:' skills/spec-manage/SKILL.md` returns a verb-noun identifier; `ls skills/spec/` no longer exists; all `see_also: spec` cross-references resolve to the new name..

#### `spec-drift-audit` (skill)

**Critical**

- [ ] [spec-drift-audit.audit-result-artifact-review-plan-layout] The audit artifact template (`templates/audit.template.md`) is missing the mandatory `## Summary` section required by `spec/claude/review-plan`'s four-section layout, and operation step 6 in SKILL.md does not instruct Claude to produce this section. The governing spec (§Audit result artifact) MUST-binds the artifact to the four-section layout (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) of `spec/claude/review-plan`. The template substitutes `## Per-criterion results` and `## Decisions` for `## Summary`, leaving the mandatory summary section (bullet counts per severity plus go/no-go statement) absent from every artifact this skill produces.
      Where: skills/spec-drift-audit/templates/audit.template.md — sections list; skills/spec-drift-audit/SKILL.md line 71 (operation step 6).
      Fix: Add `## Summary` as the second section in `templates/audit.template.md` (after `## Scope`, before `## Per-criterion results`) with placeholder text for per-severity counts and a go/no-go statement, matching the structure mandated by `spec/claude/review-plan` §Plan body structure. Update operation step 6 in SKILL.md to instruct Claude to populate `## Summary` before writing the artifact..
      Verify: Diff `templates/audit.template.md` to confirm `## Summary` appears between `## Scope` and `## Per-criterion results`. Check that `spec/claude/review-plan` AC (`Every plan file contains the four required sections`) would pass against the rendered template..

- [ ] [skill-management.progressive-disclosure-toc] All three example files exceed 100 lines (01: 134 lines, 02: 104 lines, 03: 131 lines) but none opens with a table of contents. `spec/claude/skill-management` §Progressive disclosure MUST requires a table of contents at the top of any reference file longer than 100 lines so that partial-read previews still surface the file's full scope.
      Where: skills/spec-drift-audit/examples/01-quarterly-audit.md (134 lines); skills/spec-drift-audit/examples/02-spec-change-trigger.md (104 lines); skills/spec-drift-audit/examples/03-finding-resolution.md (131 lines).
      Fix: Prepend a brief table of contents (e.g. `## Contents` with anchor links to each `##` section) to each of the three example files. The TOC must appear before any `##` section so a 100-token partial read surfaces it..
      Verify: Read the first 10 lines of each example file and confirm a `## Contents` or equivalent TOC section is present before the first substantive `##` heading..

- [ ] [spec-drift-audit.audit-result-artifact-review-plan-sections] The template (templates/audit.template.md) includes a ## Per-criterion results section that is not part of the four-section layout mandated by spec/claude/review-plan §Plan body structure (## Scope, ## Summary, ## Findings, ## Processing log). Adding an extra section outside the mandated order violates the MUST that requires exactly those sections in that order.
      Where: skills/spec-drift-audit/templates/audit.template.md line 36 (## Per-criterion results heading).
      Fix: Remove ## Per-criterion results as a top-level artifact section. Per-criterion results can be rendered as a subsection inside ## Findings or as a supporting table inside ## Scope, but must not appear as a fifth standalone section that breaks the mandated four-section layout..
      Verify: grep '^## Per-criterion results' skills/spec-drift-audit/templates/audit.template.md returns no output after the fix..

- [ ] [review-plan.plan-body-structure] The SKILL.md operation 2 (update) step 3 instructs Claude to 'Record the decision per finding in the ## Decisions section.' The ## Decisions section does not exist in the spec/claude/review-plan four-section layout, which mandates ## Processing log as the append-only record. Routing decisions into a non-existent ## Decisions section instead of ## Processing log means the update operation produces artifacts that are structurally non-conformant with the spec-drift-audit MUST binding to review-plan.
      Where: skills/spec-drift-audit/SKILL.md line 83 (update operation step 3); templates/audit.template.md lines 63-76 (## Decisions section).
      Fix: Remove ## Decisions from the template and from SKILL.md update instructions. Decision records belong in ## Processing log as append-only entries per review-plan §Plan body structure and the existing SKILL.md step 4 of operation 2 (which already appends to ## Processing log)..
      Verify: grep '^## Decisions' skills/spec-drift-audit/templates/audit.template.md returns no output; SKILL.md operation 2 references only ## Processing log for decision capture..

**Warning**

- [ ] [spec-drift-audit.audit-result-artifact-location] `examples/01-quarterly-audit.md` demonstrates writing the audit artifact to the old `docs/audits/2026-Q2.md` path in three separate places (lines 79, 90, 130). The governing spec §Audit result artifact explicitly states the `.audits/spec-drift/` location as the portfolio-wide standard, "replacing any prior `docs/audits/` convention". A realistic walkthrough example using the superseded path will teach operators the wrong target location.
      Where: skills/spec-drift-audit/examples/01-quarterly-audit.md — lines 79, 90, 130.
      Fix: Replace every occurrence of `docs/audits/2026-Q2.md` in example 01 with `.audits/spec-drift/2026-Q2.md` so the walkthrough matches the canonical location declared by `spec/project/spec-drift-audit/en.md` §Audit result artifact..
      Verify: Run `grep 'docs/audits' skills/spec-drift-audit/examples/01-quarterly-audit.md` — should return no matches. Run `grep '.audits/spec-drift' skills/spec-drift-audit/examples/01-quarterly-audit.md` — should return at least the three corrected lines..

- [ ] [skill-management.frontmatter-description-third-person] The `description` field opens with third-person "Audits …" and "produces …" but then switches to second-person imperative forms: "Invoke when the user asks …" and "Do NOT use for …". `spec/claude/skill-management` MUST requires the description to be written in third person throughout, never first or second person. Note: this is a portfolio-wide pattern present in `workflow-health-triage`, `pull-request-create`, and others — it is not unique to this skill.
      Where: skills/spec-drift-audit/SKILL.md — YAML frontmatter `description` field (line 3), phrases "Invoke when" and "Do NOT use".
      Fix: Rewrite the imperative clauses in third person, e.g. "Triggers when the user asks to …" and "Does not apply to continuous CI health checks …". Apply consistently across the portfolio in a coordinated pass rather than in isolation, to avoid introducing inconsistency..
      Verify: Confirm the description contains no second-person imperative verb phrases ("Invoke", "Do NOT", "Don't"). Cross-check that the same pass is applied to peer skills in the same plugin..

- [ ] [spec-drift-audit.audit-result-artifact-location] Examples 02 and 03 also direct Claude to write the audit artifact to the superseded docs/audits/ path, not .audits/spec-drift/. Example 02 references docs/audits/2026-Q2-pull-request-workflow.md at lines 56 and 99; Example 03 references docs/audits/2026-Q2.md at lines 11, 41, and 102. The reviewer only cited Example 01.
      Where: skills/spec-drift-audit/examples/02-spec-change-trigger.md lines 56, 99; skills/spec-drift-audit/examples/03-finding-resolution.md lines 11, 41, 102.
      Fix: Replace every docs/audits/ occurrence in examples 02 and 03 with the correct .audits/spec-drift/ path, matching the correction needed in example 01..
      Verify: grep -r 'docs/audits' skills/spec-drift-audit/examples/ returns zero results after the fix..

#### `sprint-execute` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All five operation sub-headings use verbs outside the closed vocabulary. The skill uses `Promote`, `Transition` (twice), `Sync`, and `Decline`; the spec's closed set is `audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`. The spec says MUST name each operation with one verb from that list and MUST NOT introduce new verbs without amending the list.
      Where: SKILL.md lines 53, 64, 80, 93, 103 — the five `### N. <verb> …` sub-headings under `## Operations`.
      Fix: Rename each sub-operation to use the nearest conformant verb from the closed vocabulary. Suggested mapping: (1) `Promote planned → active` → `### 1. update` (mutate sprint status from planned to active); (2) `Transition a feature ready → in_progress` → `### 2. update`; (3) `Transition a feature in_progress → done` → `### 3. update`; (4) `Sync ## Features body bullets …` → `### 4. update`; (5) `Decline transitions outside this skill's scope` → `### 5. close` (terminate a lifecycle — the closest semantic match for explicitly refusing and handing off). Retain the current long-form description text in the heading's trailing content or in the sub-section body..
      Verify: After renaming, confirm every `### N.` heading opens with exactly one word from `{audit, scaffold, patch, apply, migrate, run, update, close}`. Run `grep -n '^### [0-9]\.' skills/sprint-execute/SKILL.md` and verify each captured verb is in the closed set..

- [ ] [sprint.lifecycle] The `spec/project/sprint/` §Lifecycle MUST rule and its Acceptance Criterion AC-9 (line 120) both name `sprint-execute` as a co-enforcer of the empty-features gate on `active → review`: 'sprint-execute and sprint-review reject the transition with a verbatim error pointing at the empty list.' The skill's section 5 ('Decline transitions outside this skill's scope') declares `active → review` entirely out of scope and redirects unconditionally to `sprint-review`, without performing the empty-features check the spec assigns to this skill.
      Where: SKILL.md lines 103–112 (section 5 'Decline transitions outside this skill's scope'); see also spec/project/sprint/en.md lines 69 and 120.
      Fix: In section 5, before redirecting the user to `sprint-review`, add an explicit check: read the sprint's `features` frontmatter list and, when it is empty, refuse with a verbatim error naming the empty `features` list — matching the language the sprint spec requires. The redirect to `sprint-review` still follows, but the sprint-execute enforcement of the empty-features gate fires first. Alternatively, if the intent is that this skill never touches the `active → review` path at all, open an issue against `spec/project/sprint/` to remove `sprint-execute` from the list of enforcers for that gate; until the spec is changed, the skill must enforce it..
      Verify: Invoke sprint-execute with a request like 'transition this sprint to review' while the sprint's `features` frontmatter list is empty; confirm the skill emits an error naming the empty list before (or instead of) redirecting. Repeat with a non-empty `features` list to confirm the redirect still fires..

**Warning**

- [ ] [skill-management.operations-vocabulary] The skill-management spec (line 115) MUST title sub-operations as '### N. <verb>' (numbered); alphabetic letters (A./B./C.) are non-conformant. The skill's headings are now correctly numbered, but the Gotchas prose in the skill body (lines 118–119) still cross-references the old alphabetic labels internally: line 118 says 'kept in lockstep by Operation D' and line 119 says 'Operation C confirms both'. The heading MUST was satisfied, but these stale body references create an internal contradiction that will mislead readers and operators who look at the Gotchas section.
      Where: SKILL.md lines 118–119 under ## Gotchas, cross-referencing 'Operation D' and 'Operation C' while the headings now use '### 4. Sync' and '### 3. Transition a feature in_progress → done'.
      Fix: Replace 'Operation D' with 'Operation 4' on line 118 and 'Operation C' with 'Operation 3' on line 119 so the Gotchas prose is internally consistent with the numbered sub-headings..
      Verify: Confirm that after the edit, no occurrence of the strings 'Operation A', 'Operation B', 'Operation C', or 'Operation D' remains anywhere in SKILL.md..

**Info**

- [ ] [skill-management.operations-vocabulary] External references to this skill's operations still use the old alphabetic labels: `spec/project/blog-author-trigger/en.md` §Reference example annex calls it 'Operation C (in_progress → done) step 6', and `CLAUDE.md` says '`sprint-execute` Operation C step 6'. The skill itself was updated to numeric labels (conforming to the spec MUST against alphabetic labels), but the cross-references were not updated. This is an observation about stale prose in those two files, not a nonconformance of the skill itself.
      Where: spec/project/blog-author-trigger/en.md line 146; CLAUDE.md line referencing 'sprint-execute Operation C step 6'.
      Fix: Update the two cross-references to use the numeric label: 'sprint-execute Operation 3 (in_progress → done) step 6'. No change to SKILL.md is needed..
      Verify: Grep both files for 'Operation C' and confirm no hits remain after the update..

#### `sprint-plan` (skill)

**Critical**

- [ ] [spec/project/sprint.value-delivery-contract] Line 66 directs Claude to consult `.github/sprint-rejection-rules.yml` for project-level widening of the rejection verb list. The sprint spec §Value-delivery contract explicitly states that per-repo widening MUST use the existing `.github/release-skill-layer.yml` file (a `sprint_rejection_verbs:` key within it) and a project MUST NOT introduce a new override file such as `.github/sprint-rejection-rules.yml`.
      Where: SKILL.md line 66 — `The list MAY be widened per project; consult .github/sprint-rejection-rules.yml if it exists.`.
      Fix: Replace the reference to `.github/sprint-rejection-rules.yml` with `.github/release-skill-layer.yml` (a `sprint_rejection_verbs:` key in that file). Remove any prose implying a project may introduce a new dedicated override file..
      Verify: Confirm line 66 references `.github/release-skill-layer.yml` with a `sprint_rejection_verbs:` key, not a stand-alone `sprint-rejection-rules.yml` file. grep -n 'sprint-rejection-rules' skills/sprint-plan/SKILL.md should return nothing..

- [ ] [skill-management.operations-vocabulary] The `## Operations` block contains 8 numbered sub-headings (`### 1. Resolve the next sprint number`, `### 2. Capture and validate the value_statement`, etc.) using multi-word descriptive phrases. The spec MUST requires naming each operation with exactly one verb from the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`); the spec further MUST titles sub-operations as `### N. <verb>`. None of the 8 headings uses a verb from the approved vocabulary. Portfolio precedent (sprint-execute uses the same pattern) suggests this is a known divergence, but it remains a spec MUST violation.
      Where: SKILL.md lines 53–141 — all eight `### N. <descriptive phrase>` headings inside `## Operations`.
      Fix: This skill has one user-selectable flow. Restructure `## Operations` with a single top-level operation (`### run`) and move the eight numbered phase descriptions into prose or a `#### Phase N — <description>` sub-level not governed by the operations-vocabulary MUST. If multi-operation form is retained (e.g. one operation per phase), rename each heading to a verb from the closed vocabulary. Raise a portfolio-wide fix if sprint-execute is to be corrected in tandem..
      Verify: After restructuring, confirm every `###` heading under `## Operations` starts with a verb that is exactly one of: `audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`..

**Warning**

- [ ] [spec/project/sprint.frontmatter-schema] The Gotcha at line 148 claims 'The sprint frontmatter names which feature carries the verifier (verifies_sprint_value: F-<n>:acceptance-<m>)'. The sprint spec §Frontmatter schema enumerates exactly nine required fields and one optional `cancelled_reason`; `verifies_sprint_value` is not among them and MUST NOT appear in sprint frontmatter (lints flag unknown keys). The field lives exclusively on the feature. This incorrect claim could lead Claude to write a non-conformant sprint file that lints reject.
      Where: SKILL.md line 148 — Gotcha bullet 'verifies_sprint_value lives on a feature, not on the sprint'.
      Fix: Remove the parenthetical claim that sprint frontmatter carries a `verifies_sprint_value: F-<n>:acceptance-<m>` field. Restate the gotcha accurately: the field belongs on the feature only; the sprint file has no corresponding frontmatter pointer to it — the linkage is discovered by walking the features list..
      Verify: Read the corrected gotcha and confirm it no longer implies a sprint-side `verifies_sprint_value` frontmatter key. Cross-check against spec/project/sprint/en.md §Frontmatter schema to confirm no such field exists there..

- [ ] [skill-management.progressive-disclosure] The file examples/01-create-sprint-from-roadmap.md is 131 lines, which exceeds the 100-line threshold. The skill-management spec §Progressive disclosure MUST requires a table of contents at the top of any reference file longer than 100 lines. The file opens directly with a level-1 heading and an introductory paragraph — no table of contents is present.
      Where: skills/sprint-plan/examples/01-create-sprint-from-roadmap.md — line 1 (file is 131 lines, no table of contents).
      Fix: Add a ## Contents (or ## Table of contents) block immediately after the opening title listing the file's major sections (Input prompt, Input files, Step-by-step trace, Expected output, etc.) so partial-read previews surface the file's full scope per spec/claude/skill-management/en.md line 123..
      Verify: wc -l skills/sprint-plan/examples/01-create-sprint-from-roadmap.md confirms >100 lines; grep -n 'Table of contents\|Contents' skills/sprint-plan/examples/01-create-sprint-from-roadmap.md should return a match within the first ~10 lines..

**Info**

- [ ] [skill-management.resumable-runs] The skill correctly declares `resumable: true` and mentions resume support in the `description` field ('Supports resume on re-invocation per `spec/claude/resumable-work/`'). The `## Resumability` section correctly delegates all load-bearing envelope and lifecycle rules to the spec. No gaps found in resumability conformance.
      Where: SKILL.md frontmatter (line 24) and lines 158–160.
      Fix: No action needed..
      Verify: No action needed..

#### `sprint-review` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All seven sub-operation headings use verbs outside the closed vocabulary. The spec's MUST rule requires every named operation to use exactly one verb from: audit, scaffold, patch, apply, migrate, run, update, close. The skill uses: Promote (×2), Detect, Validate, Confirm, Operator-opt-in, Cancellation — none of which are in the vocabulary.
      Where: /home/nolte/repos/github/claude-shared/skills/sprint-review/SKILL.md lines 55, 61, 74, 93, 103, 119, 126 — the seven `### N. <verb>` headings under `## Operations`.
      Fix: Replace each sub-operation heading verb with the nearest vocabulary match. Suggested mapping: '1. Promote `active → review`' → '1. update' (or 'apply'); '2. Detect the project type' → '2. audit'; '3. Validate `artifact_ref`' → '3. audit'; '4. Confirm `verifies_sprint_value`' → '4. audit'; '5. Operator-opt-in chain …' → '5. run'; '6. Promote `review → closed`' → '6. close'; '7. Cancellation path' → '7. close'. Keep the descriptive qualifier in the heading body after the verb if needed for clarity, but the leading verb must be from the vocabulary..
      Verify: grep -n '^### [0-9]' skills/sprint-review/SKILL.md — every heading must begin with `### N. <vocab-verb>`; none of the non-vocabulary verbs should appear as the first word after the number..

- [ ] [skill-management.progressive-disclosure] Three example files each exceed 100 lines but none opens with a table of contents. The spec MUST rule requires a table of contents at the top of any reference file longer than 100 lines so partial-read previews still surface the file's full scope.
      Where: /home/nolte/repos/github/claude-shared/skills/sprint-review/examples/01-clean-close-claude-plugin.md (154 lines), examples/02-artifact-validation-fails-cancel.md (153 lines), examples/03-chain-into-release-skill-layer.md (169 lines) — each starts with a prose paragraph, not a ToC.
      Fix: Add a `## Contents` (or equivalent level-2) table of contents immediately after the top-level `#` heading in each of the three files. The ToC needs only link to the major sections present in the file (e.g. Initial state, Step-by-step transcript, Resulting sprint file, Outcome)..
      Verify: head -10 skills/sprint-review/examples/01-clean-close-claude-plugin.md skills/sprint-review/examples/02-artifact-validation-fails-cancel.md skills/sprint-review/examples/03-chain-into-release-skill-layer.md — each should show a ToC section within the first 10 lines..

- [ ] [release-artifact.project-type-detection] The `## Gotchas` section claims the skill reads the project type from `project/portfolio.yml` first, falling back to heuristic detection. The governing spec (`spec/project/release-artifact/` §Project-type detection) specifies only filesystem-heuristic signals (`.claude-plugin/plugin.json`, `pyproject.toml`, `package.json`, etc.) plus a `.github/release-skill-layer.yml` override — `project/portfolio.yml` is not a declared detection source. Implementing the undeclared path could silently diverge from the spec-defined detection order.
      Where: /home/nolte/repos/github/claude-shared/skills/sprint-review/SKILL.md line 137 — 'The skill reads the project type from `project/portfolio.yml` (or, when absent, from heuristic detection)'.
      Fix: Either (a) remove the `project/portfolio.yml` reference from the Gotchas section and align it with the spec-defined detection order (filesystem heuristics first, `.github/release-skill-layer.yml` override second), or (b) propose an amendment to `spec/project/release-artifact/` §Project-type detection to formally add `project/portfolio.yml` as a detection signal — but don't silently diverge from the spec..
      Verify: grep 'portfolio.yml' spec/project/release-artifact/en.md should return no hits; if the path stays in the skill, a corresponding addition must appear in the spec..

- [ ] [skill-management.frontmatter-validation] The `description` field opens with 'Close an active sprint…' — an imperative/base-form verb — instead of the third-person singular present tense the spec mandates. `spec/claude/skill-management/en.md` line 46 states: 'MUST write `description` in third person ("Generates …," "Reviews …"), never first or second person', with the explicit counter-example pattern being third-person singular present tense verbs.
      Where: /home/nolte/repos/github/claude-shared/skills/sprint-review/SKILL.md line 3 — `description: Close an active sprint…`.
      Fix: Change the opening verb from the imperative 'Close' to the third-person singular present tense 'Closes'. The corrected opening should read: `description: Closes an active sprint per the project sprint spec, validating the deployable artefact…`.
      Verify: grep '^description:' skills/sprint-review/SKILL.md | head -1 — confirm the value starts with 'Closes' (third-person singular), not 'Close' (imperative base form)..

#### `tech-stack-capture` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] The ## Operations block contains 8 numbered sub-headings (Resolve, Read, Probe, Drop, Propose, Propose, Interactive, Compose) none of which are drawn from the closed operation-verb vocabulary (audit, scaffold, patch, apply, migrate, run, update, close). The skill declares one operation, for which the spec prescribes the default verb `run`. There is no top-level `### run` (or `### 1. run`) heading wrapping the 8 procedural steps; the ## Operations heading leads directly to the numbered sub-steps.
      Where: skills/tech-stack-capture/SKILL.md lines 64-135 (## Operations block).
      Fix: Insert a top-level operation heading `### run` (or `### 1. run`) between the `## Operations` heading and `### 1. Resolve the inherited set`. The 8 existing numbered sub-headings then become sub-operations of the single `run` operation and their free-form verbs are conformant under the sub-operation rule (### N. <verb>)..
      Verify: After the fix, `grep -n '^### ' SKILL.md` should show `### run` (or `### 1. run`) as the first heading under `## Operations`, followed by `#### 1. Resolve…` (or equivalent deeper nesting) for the procedural steps..

- [ ] [skill-management.description-person] The `description` field MUST be written in third person. The spec at §Frontmatter validation line 46 states: 'MUST write `description` in **third person** ("Generates …", "Reviews …"), never first or second person.' The current description contains 'Invoke when the user asks…' and 'Don't use to author…' — both are imperative (second-person) constructions, not third person.
      Where: skills/tech-stack-capture/SKILL.md line 3 (description frontmatter field): 'Invoke when the user asks…' and 'Don't use to author…'.
      Fix: Rewrite the trigger and exclusion clauses in third person. For example: 'Invoke when…' → 'Use when the user asks…' is still imperative; a conformant form would be 'Triggered when the user asks to "capture the tech stack"…' or restructure as 'Supports requests to "capture the tech stack", "scaffold a tech_stack block", or "refresh the tech_stack section". Not intended for authoring `portfolio/tech-stack.yml` (hand-curated only) or for signal-verification audits (use `portfolio-audit`).'.
      Verify: Confirm the entire `description` value uses only third-person verbs (Generates, Reviews, Captures, Supports, Probes…) with no imperative forms (Invoke, Don't use, Use, Run)..

**Warning**

- [ ] [skill-management.authoring-quality] SKILL.md is 168 lines, exceeding the 150-line soft performance guideline ('keep SKILL.md under roughly 150 lines as a soft target; move long-form content into referenced files'). The 500-line MUST cap is not breached, and the estimated token count (~3,880 words × 1.3) remains comfortably within the 5,000-token MUST limit. No action is strictly required.
      Where: skills/tech-stack-capture/SKILL.md (168 lines total).
      Fix: Optionally migrate the detailed per-step prose in § Operations (steps 1–8, ~60 lines) into a new `references/discovery-steps.md` reference file and replace it with a summary paragraph plus a load-trigger phrase ("Read references/discovery-steps.md for the full step-by-step procedure"). This would bring SKILL.md under the 150-line soft target..
      Verify: After any move, confirm `wc -l SKILL.md` is under 150, that every moved section has an explicit load-trigger phrase in SKILL.md, and that `references/discovery-steps.md` opens with a table of contents (it will be >100 lines)..

#### `vocab-drift-audit` (skill)

**Critical**

- [ ] [skill-management.description-third-person] The description opens with the imperative verb 'Audit' and later uses 'Invoke when', both of which are second-person imperative forms. The spec MUST requires description text written in third person ('Generates…', 'Reviews…') throughout. 'Dispatches' and 'Reports' later in the same description are correctly third-person, making the field inconsistent.
      Where: SKILL.md frontmatter, `description` field — first sentence ('Audit repository-local…') and 'Invoke when the user asks…'.
      Fix: Change 'Audit repository-local…' → 'Audits repository-local…' and 'Invoke when the user asks…' → 'Invokes when the user asks…' (or rephrase to 'Use when the user asks…' is still imperative — keep third-person gerund/present-tense-third: 'Invokes when…')..
      Verify: Grep the description for bare-infinitive verb phrases at the start of sentences; every verb should carry the third-person -s inflection..

- [ ] [skill-management.operations-vocabulary] The `## Operations` block contains four numbered prose items with bold labels ('Locate the Vale config.', 'Dispatch …', 'Render the report', 'Offer follow-up actions'). The spec MUST requires sub-operations to be titled as `### N. <verb>` headings using a verb from the closed vocabulary (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). None of the four labels ('Locate', 'Dispatch', 'Render', 'Offer') appear in the closed vocabulary, and none use the `### N.` heading form.
      Where: SKILL.md §Operations, lines 41–47 — numbered list items 1–4.
      Fix: Either (a) convert the four items to `### N. <verb>` headings using permitted verbs (e.g. `### 1. audit` for locate + scan, `### 2. run` for dispatch, `### 3. run` for render, `### 4. apply` for follow-up) or (b) if these are sequential implementation steps of a single `audit` operation rather than distinct user-invocable operations, rename the section to something like `## Procedure` to avoid triggering the operations-vocabulary rules, and document the single operation verb elsewhere..
      Verify: After the fix, grep for `## Operations`; if the heading is retained, every bold-step label must use a closed-vocabulary verb and every sub-step must open with a `### N.` heading..

**Suggestion**

- [ ] [skill-management.use-case-metadata-should] The skill lists `vocab-drift-scanner` and `prose-vale-curator` in `see_also`, signalling known adjacent artifacts. The spec SHOULD declare `dont_use_when` whenever overlap with other artefacts is likely. No `dont_use_when` is present, leaving consumers without explicit routing guidance for when to reach directly for `vocab-drift-scanner` (agent-only read) or `prose-vale-curator` instead.
      Where: SKILL.md frontmatter — `dont_use_when` field absent.
      Fix: Add a `dont_use_when:` list, e.g.: `- situation: 'you only need the raw diff between local and upstream vocabularies without follow-up actions'; alternative: vocab-drift-scanner`..
      Verify: Run `task docs` (or the catalog validator) and confirm the `dont_use_when` entry resolves without build failure..

#### `webview-ui-optimize` (skill)

**Critical**

- [ ] [skill-vs-agent.rationale-section-heading] The rationale section heading is `## Rationale (why a skill, not just an agent)` instead of the required `## Why this is a skill, not an agent`. The spec mandates this exact heading for skills and explicitly lists alternative phrasings as non-conformant.
      Where: /home/nolte/repos/github/claude-shared/skills/webview-ui-optimize/SKILL.md line 38.
      Fix: Rename the heading to exactly `## Why this is a skill, not an agent`. The body content can remain unchanged..
      Verify: grep -n 'Why this is a skill, not an agent' skills/webview-ui-optimize/SKILL.md returns line 38..

- [ ] [skill-management.operations-vocabulary] The skill declares `expert-review` as a named operation (line 152: `### 3. \`expert-review <target>\``), but`expert-review`is not in the closed operations vocabulary. skill-management/en.md line 113 MUST-requires each operation to use one verb from: audit, scaffold, patch, apply, migrate, run, update, close. Line 114 explicitly MUST NOT introduces new operation verbs without amending the list.
      Where: /home/nolte/repos/github/claude-shared/skills/webview-ui-optimize/SKILL.md line 152 (`### 3. \`expert-review <target>\` (deep read-only)`).
      Fix: Rename the`expert-review` operation to a conformant verb from the closed vocabulary. The closest fit is `run` (default verb for a single-purpose operation) or, if the spec list is to be extended, amend spec/claude/skill-management/en.md §Operations vocabulary first and add `expert-review` or a suitable alias there before using it here..
      Verify: grep -n 'expert-review' skills/webview-ui-optimize/SKILL.md — confirm no operation heading uses that verb, or confirm the spec's operations vocabulary was amended to include it..

**Warning**

- [ ] [skill-management.recommendations] SKILL.md is 195 lines, exceeding the ~150-line soft target. The spec SHOULD-recommends keeping SKILL.md under roughly 150 lines and moving long-form content into referenced support files.
      Where: /home/nolte/repos/github/claude-shared/skills/webview-ui-optimize/SKILL.md (195 lines).
      Fix: Extract the verbose `## Operations` sub-sections (especially the audit-report template on lines 79–132, the patch patterns on lines 139–150, and the expert-review dispatch block) into a `references/operations.md` file. Add an explicit load-trigger phrase in SKILL.md: e.g. `Read references/operations.md for the full operation procedure details.`.
      Verify: wc -l skills/webview-ui-optimize/SKILL.md returns ≤150..

- [ ] [skill-management.authoring-quality] No `## Gotchas` section is present. The spec SHOULD-recommends including a Gotchas section listing concrete corrections to non-obvious environment facts the agent would otherwise get wrong (distinct from Hard rules).
      Where: /home/nolte/repos/github/claude-shared/skills/webview-ui-optimize/SKILL.md — section absent.
      Fix: Add a `## Gotchas` section with at least 2–3 concrete non-obvious facts specific to this skill (e.g. that the spec fallback path is the plugin install path at runtime, not the source repo; that vitest-axe requires a running jsdom environment so `npx vitest run` needs the right config; that Mozilla Observatory checks require a live deployed origin — local headers won't satisfy them)..
      Verify: grep -n '## Gotchas' skills/webview-ui-optimize/SKILL.md returns a result..

- [ ] [skill-management.evaluation-discipline] No evaluation scenarios are present. The spec SHOULD-recommends shipping at least three evaluation scenarios per non-trivial skill under `examples/` (input prompt, optional input files, expected behavior) so iteration is grounded in observable behavior.
      Where: /home/nolte/repos/github/claude-shared/skills/webview-ui-optimize/ — no examples/ folder.
      Fix: Create skills/webview-ui-optimize/examples/ with at least three scenario files (e.g. audit-greenfield.md, patch-csp.md, expert-review-auth-flow.md), each containing input prompt, preconditions, and expected output shape..
      Verify: ls skills/webview-ui-optimize/examples/ lists at least 3 files..

#### `workflow-health-triage` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] All five sub-operations in the `## Operations` block use verbs outside the closed vocabulary. The skill names them `1. Inspect`, `2. Classify`, `3. Dispatch`, `4. Verify`, `5. Verify`. None of these appear in the spec's closed set (`audit`, `scaffold`, `patch`, `apply`, `migrate`, `run`, `update`, `close`). The spec states: "MUST name each operation with one verb from the closed vocabulary" and "MUST NOT introduce new operation verbs without amending this list."
      Where: /home/nolte/repos/github/claude-shared/skills/workflow-health-triage/SKILL.md lines 48, 59, 76, 91, 100.
      Fix: Rename each sub-operation to the closest conformant verb from the closed vocabulary, for example: `1. audit` (inspect the run), `2. audit` (classify the failure — or `run` if the skill's single flow pattern fits), `3. patch` (dispatch the remediation), `4. audit` (verify audit-trail), `5. audit` (verify PR gate). If the existing verbs genuinely describe distinct operations that none of the eight cover, amend `spec/claude/skill-management/en.md` §Operations vocabulary to add them first, then update the skill..
      Verify: After renaming, run `grep '^### [0-9]' skills/workflow-health-triage/SKILL.md` and confirm every operation verb is present in the spec's closed list..

- [ ] [skill-management.authoring-quality] The `## Multi-model testing` section names specific model-version suffixes (`Sonnet 4.6`, `Haiku 4.5`, `Opus 4.7`). These are time-sensitive claims that will silently become wrong as new minor versions ship. The spec states: "MUST NOT include time-sensitive information that will become wrong"; the illustrative example is a version-specific API note, and these model-version strings carry the same staleness risk.
      Where: /home/nolte/repos/github/claude-shared/skills/workflow-health-triage/SKILL.md line 142.
      Fix: Drop the version suffixes and refer to the model families by name only: "verified on Claude Sonnet as the default model; spot-checked on Haiku for cost-sensitive runs; Opus is appropriate for high-stakes audits." This satisfies `skill-management` §Evaluation discipline's SHOULD to test against all three tiers without binding to a point version..
      Verify: Grep for `[0-9]\.[0-9]` in the section; no model-version numbers should remain..

#### `yaml-json-schema` (skill)

**Critical**

- [ ] [skill-management.operations-vocabulary] Six of seven operation headings use verbs not in the closed vocabulary (audit, scaffold, patch, apply, migrate, run, update, close). Non-conformant headings: '1. Author a new schema' (author), '3. Refactor (apply audit findings)' (refactor), '4. Meta-validation (schema-against-meta-schema)' (meta-validation is a noun phrase), '5. Data validation (data-against-schema)' (noun phrase), '6. Lifecycle bump (revise an existing schema)' (lifecycle bump), '7. Re-audit' (re-audit). The spec MUST requires each operation to be named with exactly one verb from the closed list, and MUST NOT introduces new verbs without amending the list.
      Where: /home/nolte/repos/github/claude-shared/skills/yaml-json-schema/SKILL.md lines 65–91 (## Operations block).
      Fix: Rename the six non-conformant operations to conformant verbs: '1. Scaffold' (Author → scaffold), '3. Apply' (Refactor → apply, as it combines audit findings and patches), '4. Run' or fold meta-validation into the audit operation under '2. Audit', '5. Run' or fold into '2. Audit', '6. Update' (Lifecycle bump → update), '7. Audit' (Re-audit → audit, or renumber and merge with operation 2). Also amend references/operations.md headings to match..
      Verify: grep '^### [0-9]' skills/yaml-json-schema/SKILL.md — every lead verb must appear in the closed vocabulary: audit, scaffold, patch, apply, migrate, run, update, close..

**Warning**

- [ ] [skill-management.structure] The frontmatter has no `dont_use_when` field despite the description text explicitly listing skip conditions (OpenAPI/AsyncAPI Schema Objects, JSON-encoded schemas, feature-frontmatter rules, project-structure scaffolding). The spec SHOULD declares `dont_use_when` whenever overlap with other artefacts is likely, and the skill's own description names two direct overlaps (project-structure-apply, spec/project/feature/).
      Where: /home/nolte/repos/github/claude-shared/skills/yaml-json-schema/SKILL.md frontmatter (lines 1–27) — `dont_use_when` key is absent.
      Fix: Add a `dont_use_when` frontmatter list mirroring the skip conditions already stated in the description: OpenAPI/AsyncAPI Schema Objects, JSON-encoded schemas, feature frontmatter content rules (use spec/project/feature/ instead), project-structure scaffolding (use project-structure-apply instead). The description text can then drop the inline 'Skip for:' clause or keep it as a shorter reference..
      Verify: python3 -c "import yaml; fm=yaml.safe_load(open('skills/yaml-json-schema/SKILL.md').read().split['---'](1)); print(fm.get('dont_use_when'))" — must return a non-empty list..

**Suggestion**

- [ ] [skill-management.tag-vocabulary] The tag `validation` is not in the starter vocabulary. The starter vocabulary includes `quality-gate` (lint, typecheck, test) which covers validation use cases. The spec SHOULD prefers a starter-vocabulary term when one applies; MAY introduce a new tag only when no starter term fits.
      Where: /home/nolte/repos/github/claude-shared/skills/yaml-json-schema/SKILL.md line 17 — tags: [scaffolding, audit, validation].
      Fix: Replace `validation` with `quality-gate` if the intent is to signal that this skill wires into the repo's quality gate (meta-validation, data-conformance). If the distinct 'schema validation' semantic needs its own tag cluster, add a note to the spec's starter vocabulary rather than silently using an off-vocabulary term..
      Verify: Confirm tag list against spec/claude/skill-management/en.md §Tag vocabulary starter vocabulary; all three tags should appear there or be documented as deliberate additions..
