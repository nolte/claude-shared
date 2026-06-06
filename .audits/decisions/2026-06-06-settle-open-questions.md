---
type: decision-log
title: Settle scale-deferral open questions (watch-list #229)
created: 2026-06-06
context: >
  Operator chose aggressive-settle for the #229 spec open-questions watch-list:
  convert provisional-default and externally-blocked open questions into firm
  standing decisions and remove them from the watch-list. Settling deletes the
  open question; it does not forbid a future spec change — a genuine future need
  can always re-open the topic through the normal `spec` process. The provisional
  default each OQ described is already the spec's encoded rule, so settling makes
  the default permanent and stops tracking the hypothetical revisit.
---

# Decision log — settled open questions (2026-06-06)

Each entry: the spec, the open question, and the now-standing decision.

## Group A — planning & lifecycle specs

### project/roadmap
- **Q1 (tags field):** No `tags` field. The per-item schema stays the seven declared keys. Large-queue filtering is not a goal; if a 20+-item coarse/backlog roadmap ever appears, a future spec change can add it then.
- **Q2 (dependency field):** No `depends_on` field. Flat top-to-bottom list order is the sole dependency encoding.
- **Q4 (phase IDs):** Phases stay ID-less documentation. No stable phase identifiers.

### project/mission
- **Q1 (`verifies_via` as list):** `verifies_via` stays a single `<feature-id>:acceptance-<n>` string.
- **Q2 (tunable stabilisation soak):** Fixed constant of one full subsequent sprint; no `stabilisation_soak_sprints` field.
- **Q3 (revert halts active items):** Softer rule stands — a `stabilised → in_progress` revert blocks new post-MVP starts but lets in-flight items finish; no forced-halt automation.
- **Q4 (machine-readable mission-coverage report):** No mission-coverage report. If a downstream consumer ever needs per-audience MVP-verification keyed off the mission, it is specced then as a generated artefact.

### project/sprint
- **Q1 (concurrent value streams):** Single-active-sprint invariant stands; no track identifier.
- **Q2 (structured `value_statement`):** `value_statement` stays free text (one sentence, end-user perspective).

### project/test-case-derivation
- **Q4 (machine-readable traceability index):** No separate traceability index; the per-case `requirement_id` frontmatter plus the per-document coverage summary are the traceability surface.

### project/i18n-completeness
- **Q3 (identical-across-locales allowlist):** Identical-across-locales stays an info-tier finding with no exemption allowlist.
- **Q4 (ICU MessageFormat granularity):** Placeholder parity stays at simple-placeholder granularity; ICU plural/select bodies are treated as opaque strings.

## Group B — process, docs & release specs (full settle)

### project/docs-multilingual-authoring
- **Q4 (richer translation-debt taxonomy):** Keep the single `needs-review` author-set marker; the binary marker stands.

### project/cookiecutter-template-authoring
- **Q2 (auto-dispatch audience-identify):** Banner-only stands (the rendered-project hook cannot legally auto-dispatch a skill).
- **Q3 (OS matrix):** Linux-only (`ubuntu-latest`) stands; the existing clause already promotes `windows-latest` to MUST for a Windows-targeted template.

### project/parallel-working-copies
- **Q3 (mechanical worktree-remove guard):** Contributor-behaviour convention stands; no removal-time wrapper/hook.

### claude/review-plan
- **Q5 (staleness window):** Six-month open-plan staleness signal stands.

### project/prose-style
- **Q2 (bespoke voice/tone Vale rules):** §Voice and tone stays lektorat-D4/PR-review enforced; no bespoke Vale rules authored upstream pre-emptively.

### claude/resumable-work
- **Q2 (portfolio-wide prune skill):** No dedicated prune skill; per-artefact cleanup stands.

### claude/permission-allowlist
- **Q1 (central base allowlist):** No central allowlist; each repo owns its committed `.claude/settings.json` allow list.

### portfolio/tech-stack-discovery
- **Q1 (sixth Benefits bullet):** §Benefits stays at five bullets.

### project/release-artifact
- **Q1 (marketplace-catalog fallback):** Keep the interim manual marketplace-catalog fallback until a release workflow actually performs the catalog update; no spec change forced now.
- **Q4 (HEAD-200 verification):** HEAD-200 stays the provisional doc-site deploy verification.
- **Q5 (per-project-type bundle extraction):** Keep the taxonomy table inline; no extraction to `references/<project-type>-bundles.md`.

### project/docs-freshness
- **Q2 (anchor-target check MUST):** In-file anchor-target check stays SHOULD.
- **Q3 (N=5 content-staleness cap):** N=5 most-recently-modified spot-check stands.

### project/spec-readiness
- **Q4 (CI-enforced gate):** spec-readiness stays an advisory, operator-enforced gate; not wired into CI.

### project/docs-audience-tracks
- **Q2 (`release-manager` → `release-docs` track):** `release-manager → developer-docs` mapping stands.
- **Q4 (quickstart depth):** Single adaptive snippet satisfies the onboarding MUST.
- **Q6 (arch-overview floor):** One-screen architecture overview stays the floor.
- **Q7 (audience-identification `decision criterion` field):** No new per-audience decision-criterion field; the quickstart `SHOULD` stays a `SHOULD`.

## Group C — partial settle (some open questions retained)

### design/corporate-design-colors (Q1 retained — brand-owner decision, Welle 2)
- **Q3 (token-bundle registry):** Settled — no `design-token-distribution` spec until a producer repo and a published bundle exist; coordinate ad hoc until then.
- **Q6 (CMYK MUST):** Settled — CMYK fallback stays SHOULD.
- **Q7 (imagery-style hand-off):** Settled — no reciprocal hand-off clause until `spec/design/imagery-style/` is authored.
- **Q1 (brand-primary OKLCH):** RETAINED — a brand-owner value decision (Welle 2), not settleable autonomously.

### design/graphic-prompt-authoring (Q2 retained — depends on corporate-design-colors Q1)
- **Q4 (asset-type vocabulary migration):** Settled — the file-naming asset-type vocabulary stays in this spec.
- **Q2 (sref-less style reference):** RETAINED — owned by corporate-design-colors §AI image color contract, blocked on Q1.

### project/mkdocs-structure (None/Resolved notes retained)
- **Q2 (`prerequisites` MAY→SHOULD):** Settled — `prerequisites` stays MAY on tutorial/how-to pages.
