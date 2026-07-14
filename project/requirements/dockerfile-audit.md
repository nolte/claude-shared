# Requirements — Dockerfile best-practices audit (skill + scanner agent) with mandatory OCI labels

<!--
Produced via the `requirements-elicit` skill, following
spec/project/requirements-elicitation/.
`c_d` is an uncertainty proxy (self-consistency-derived), not a calibrated
probability. A requirement is `confirmed` only after an explicit teach-back.
-->

## Bounded context

- **What is being built:** two coupled artefacts —
  1. a **spec** `spec/project/dockerfile-best-practices/` (EN-canonical + DE translation, `Scope: local`)
     capturing researched Dockerfile best practices (build correctness, security hardening,
     image slimness/reproducibility) with a **mandatory OCI-label contract**
     (`org.opencontainers.image.*` per the GHCR container-labelling guidance) as a first-class,
     hard-failing pillar; and
  2. a **`nolte-engineering` plugin skill** `dockerfile-audit` plus a read-only
     `dockerfile-audit-scanner` agent that audits a repository's Dockerfiles against that spec, reports
     violations with `file:line`, and can optionally **apply** the missing OCI `LABEL` block and other
     mechanical fixes.
- **For whom:** repositories adopting the `nolte-engineering` plugin that build container images
  (the audit consumers); the spec readers; the skill/agent authors.
- **The third sibling** in the best-practices→spec→engineering-artefact family, alongside
  `spec/project/kubernetes-deployment-best-practices/` and `spec/project/bjw-s-common-chart-deployment/` —
  matches their shape (mandatory pillars, version anchors, completeness gate, deep-research grounding).
- **Explicitly out of scope:** the GHCR push / CI publish workflow itself, Kubernetes deployment
  (own sibling spec), generic CI-pipeline generation, and container **runtime** hardening. The change is
  **additive** — it is not a fork of `dependency-audit` or `code-security-reviewer`.

## Understanding KPI

- Thresholds: `τ_low = 0.4`, `τ_high = 0.8`, self-consistency `k = 2`, question budget = `~6`
  (spec defaults; unchanged).
- `U_gate = min_d c_d` over required dimensions = **0.82** (was 0.78 at interview close). The deep-research
  Workflow (`wf_90bd2851-d23`, 5/5 load-bearing claims CONFIRMED) plus the post-research operator sign-off on
  Q7.1 (CI-injected labels) settled the multi-stage / label-placement / CI-scope edge cases, raising
  `edge_cases` 0.78→0.85. All decision dimensions were settled by explicit operator sign-off (Q1–Q5 + Q7.1)
  plus a consolidated teach-back confirmed with "ja".
- Termination: **saturation.** The five open questions (§3 of the plan) plus the one new load-bearing policy
  question surfaced by research (Q7.1, CI-injection scope) are resolved. Only narrow spec-authoring detail
  remains (apply-merge on a pre-existing `LABEL` block; monorepo Dockerfile-discovery glob), routed to the
  `/nolte-shared:spec` authoring step and listed below.

### Gap matrix

| Dimension | Applicable | `c_d` | Uncertainty source | Evidence event |
|---|---|---|---|---|
| `functional` | yes | 0.90 | interpretation | Q1/Q2 sign-off (skill + scanner-agent; audit + optional apply) + teach-back "ja" |
| `non_functional` | yes | 0.85 | interpretation | DRY skill/agent split + routing-budget + plugin distribution (plan §5); teach-back |
| `constraints` | yes | 0.88 | interpretation | EN-canonical, marketplace-only, `<object>-<action>` naming, Vale-from-worktree, `task test` (plan §5) |
| `domain_objects` | yes | 0.88 | interpretation | Q3 sign-off: OCI key set (6 PFLICHT / 5 SHOULD) + ARG-vs-literal presence rule |
| `actors` | yes | 0.85 | interpretation | Teach-back confirmed (adopting repos that build images; spec readers; skill authors) |
| `acceptance_criteria` | yes | 0.85 | interpretation | Q3/Q4 sign-off: mandatory checks (OCI core present, security-core pillars) + apply behaviour |
| `edge_cases` | yes | 0.85 | specification | Research CONFIRMED multi-stage final-stage placement + ARG-presence; Q7.1 settled CI-injection scope |
| `scope_boundaries` | yes | 0.87 | interpretation | Q1/Q2 + Q7.1 sign-off (audit + apply + CI-injection recognised); teach-back out-of-scope list confirmed |

## Requirements

<!-- EARS/CNL form; tagged confirmed/assumed with traceability. -->

### Spec (EN canonical + DE in sync)

- **R1** — WHEN the `dockerfile-best-practices` spec is authored, it SHALL exist as
  `spec/project/dockerfile-best-practices/en.md` (canonical) + `de.md` (strict translation), `Scope: local`,
  mirroring the two sibling best-practices specs (mandatory pillars, version anchors, completeness gate,
  deep-research grounding).
  - _dimension_: `constraints`, `non_functional` · _status_: `confirmed` · _source_: plan §1/§5 + teach-back
- **R2** — WHEN the spec defines the label contract, it SHALL mandate that every audited Dockerfile carry the
  **core** OCI annotations `org.opencontainers.image.{source,title,description,version,revision,created}` as
  PFLICHT (hard-failing), and SHALL mark `{licenses,url,documentation,base.name,base.digest}` as SHOULD.
  - _dimension_: `functional`, `domain_objects` · _status_: `confirmed` (Q3: "Kern-Set") · _source_: Q3 sign-off
- **R3** — WHEN the spec defines what counts as a present label, it SHALL accept BOTH a static literal
  (`LABEL org.opencontainers.image.version="1.2.3"`) AND an `ARG`-wired value
  (`ARG VERSION` + `LABEL org.opencontainers.image.version=$VERSION`); the audit checks presence and wiring,
  never the build-time value substitution.
  - _dimension_: `domain_objects`, `edge_cases` · _status_: `confirmed` (Q3 axis 2) · _source_: Q3 sign-off
- **R4** — WHEN the spec defines the non-label mandatory pillars, it SHALL make PFLICHT: a non-root `USER`,
  no secrets baked into layers/build history, a pinned base image (tag + digest, never `:latest`), and a
  present `.dockerignore`; and SHALL treat multi-stage builds, `HEALTHCHECK`, `COPY`-over-`ADD`,
  apt/package hygiene (`--no-install-recommends` + cache clean), and layer-cache ordering as advisory (scored
  SHOULD, not hard-failing) — mirroring the K8s sibling's security-first mandate.
  - _dimension_: `functional`, `acceptance_criteria` · _status_: `confirmed` (Q4: "Security-Kern") · _source_: Q4 sign-off
- **R5** — WHEN the canonical `en.md` is authored, the `de.md` translation SHALL be kept in strict sync via
  the `/nolte-shared:spec` translation path, with the spec parity/drift check passing (EN canonical per
  `.spec-config.yml`).
  - _dimension_: `constraints` · _status_: `confirmed` · _source_: plan §5 invariants

### Skill + scanner agent (nolte-engineering plugin)

- **R6** — WHEN the tooling is authored, it SHALL take the form of a `dockerfile-audit` **skill** plus a
  read-only `dockerfile-audit-scanner` **agent** (mirroring `dependency-audit` / `license-check`): the agent
  performs detection (discovers `**/Dockerfile*`, classifies findings) and the skill owns policy, severity,
  the report, and the optional apply — never a lone self-contained skill or a lone reviewer agent.
  - _dimension_: `functional`, `non_functional` · _status_: `confirmed` (Q1) · _source_: Q1 sign-off
- **R7** — WHEN the skill runs its `audit` operation, it SHALL emit a severity-classified findings report
  with `file:line` attribution, hard-failing on any missing PFLICHT OCI core key (R2) or missing PFLICHT
  non-label pillar (R4), and scoring the SHOULD items as advisory.
  - _dimension_: `functional`, `acceptance_criteria` · _status_: `confirmed` (Q2 read-only branch + Q3/Q4) · _source_: Q2/Q3/Q4 sign-off
- **R7a** — WHEN a required OCI label is absent from the Dockerfile, the audit SHALL NOT hard-fail before
  checking for CI-side injection: if the repo's CI wires the labels via `docker/metadata-action` /
  `docker build --label` / `--annotation` (detectable in `.github/workflows/`), the requirement is
  satisfied (reported PASS with a note that the labels legitimately live outside the Dockerfile). It
  hard-fails only when the labels are present neither in the Dockerfile nor in CI injection.
  - _dimension_: `edge_cases`, `scope_boundaries` · _status_: `confirmed` (post-research Q7.1: "CI-Injektion anerkennen") · _source_: research-findings §5/§7.1 + operator sign-off
- **R8** — WHEN the skill runs its `apply` operation, it SHALL insert the missing OCI `LABEL` block (and other
  mechanical fixes it can make safely) into the Dockerfile and write the file — apply-style, like
  `project-structure-apply` — leaving value substitution (the actual version/revision/created) to build time.
  - _dimension_: `functional`, `scope_boundaries` · _status_: `confirmed` (Q2: "Report + optionales Apply") · _source_: Q2 sign-off
- **R9** — WHEN the skill and agent are authored, they SHALL be grounded strictly in the
  `dockerfile-best-practices` spec (R1–R4), ship only via the plugin marketplace under
  `plugins/nolte-engineering/`, follow `<object-noun>-<action>` naming, and respect the agent-description
  routing-budget ceiling (the added scanner agent counts against it).
  - _dimension_: `constraints`, `non_functional` · _status_: `confirmed` · _source_: plan §5 + Q1/Q5 sign-off

### Process / quality

- **R10** — WHEN the change is prepared for review, `task test` (`validate_skills.py`: frontmatter + naming +
  description budget) SHALL be green, the changed spec prose SHALL be Vale/lektorat clean (Vale run **from
  the worktree**), `task docs` SHALL regenerate the catalog/i18n cleanly, the plugin SHALL dogfood-load to
  smoke-test the skill, and the PR SHALL autolink the new spec.
  - _dimension_: `acceptance_criteria` · _status_: `confirmed` · _source_: plan §4 steps 5–6

## Surviving assumptions / open risks

**Resolved (settled by operator sign-off Q1–Q5 + consolidated teach-back "ja"):**

- ✅ **Q1 (tool shape):** skill `dockerfile-audit` + read-only `dockerfile-audit-scanner` agent.
- ✅ **Q2 (audit vs apply):** report **and** optional apply of the OCI `LABEL` block.
- ✅ **Q3 (mandatory OCI keys):** core set `{source,title,description,version,revision,created}` PFLICHT;
  presence accepted as static literal **or** `ARG`-wired.
- ✅ **Q4 (PFLICHT pillars beyond labels):** non-root `USER`, no in-layer secrets, pinned base image
  (tag+digest), `.dockerignore`; the rest advisory.
- ✅ **Q5 (naming):** `dockerfile-audit` (agent `dockerfile-audit-scanner`), aligned with sibling engineering skills.
- ✅ **Q7.1 (CI-injection scope — surfaced by research, `revisit`):** the audit recognises CI-side label
  injection (`docker/metadata-action` / `--label`) as satisfying the requirement; hard-fails only when labels
  are absent both in the Dockerfile and in CI. Captured as **R7a**.
- ✅ **Multi-stage label placement:** CONFIRMED (research claim C4) — evaluate labels against the
  **final/publishing** stage; a `LABEL` only in a non-final stage is a false positive.

**Remaining residual risk (narrow spec-authoring detail; routed to `/nolte-shared:spec`, NOT to the operator):**

- **`apply`-merge semantics** on a pre-existing/partial `LABEL` block — merge into the final-stage block vs.
  append; de-duplicate keys, preserve custom labels (research §5 rule: merge, later key wins).
- **Monorepo Dockerfile discovery** — glob (`Dockerfile`, `*.Dockerfile`, `docker/*/Dockerfile`, per-service
  dirs); evaluate each independently; opt-out marker for non-published/test Dockerfiles (research §5).
- These are settled-in-principle by the research; the spec author fixes exact wording. Other research §7
  open questions (numeric-UID range, digest-updater MUST, hadolint version pin + per-rule overrides,
  non-mechanizable-pillar handling) are resolved during spec authoring with the research's recommended
  defaults, consistent with the confirmed requirements above.

**Constraint reminders (confirmed, not risks):** EN canonical + DE in sync; primary checkout stays on
`develop` (all work in this worktree); the skill ships via the marketplace, never copied into a consumer's
`.claude/skills/`; all generated spec/config prose is English (DE is the translation).
