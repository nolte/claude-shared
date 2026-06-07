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

## Welle 6 — external-watch & genuinely-open (full settle)

Each default is the standing rule; a platform/upstream/consumer change re-opens via the normal spec process.

- **ansible/playbook-development** Q1 (split single-environment-bootstrap spec) + Q3 (sops MAY→SHOULD): no split, sops stays MAY; revisit only if a second Ansible adopter / a committed key-store spec lands.
- **claude/plugin-scoping** Q2 (skill-count discipline) + Q3 (second plugin split): single `nolte-shared` plugin, full-body preload discipline stands; revisit on the upstream claude-code#14882 outcome or a genuinely divergent distribution contract.
- **claude/skill-agent-catalog** Q3 (pre-build vs gen-files under folder-i18n): pre-build stays required; revisit on a mkdocs-static-i18n release that stops dropping out-of-docs_dir gen-files.
- **claude/skill-review** Q6 (reserved-command overlap check): not added; revisit when a queryable reserved-command list exists or skill-vs-agent makes commands a first-class artifact.
- **claude/skill-vs-agent** Q3 (third command artifact class): two-class decision rule stands; revisit on a Claude Code release shipping a distinct command artifact format.
- **project/audience-identification** Q5 (security/privacy/SLA cross-ref): no bidirectional wiring until the first such spec exists; that spec's author wires it then.
- **project/code-security-audit** Q3 (threat-modeling delimitation): no reciprocal Non-Goal until a threat-modeling spec or roadmap item exists.
- **project/dependency-audit** Q4 (compliance-regime cadence): MAY stays MAY; revisit when a repo declares a named compliance regime.
- **project/blog-author-trigger** Q3 (start-of-work trigger) + Q4 (sprint-summary trigger): single feature-to-done trigger stands; revisit on an explicit operator request or a roadmap item.
- **project/feature** Q2 (`depends_on` field): no dependency field; sprint membership + roadmap link express ordering. Revisit on a real same-sprint feature chain.
- **project/post-audience-communication** Q3 (corpus distribution gate), Q4 (correction-channel formalism), Q5 (permission threshold), Q6 (Diátaxis frontmatter signal): all defaults stand (50/20/30 model, public-form correction, reactive tightening, implicit-in-lede Diátaxis).
- **project/post-writing-style** Q1 (quantitative FK gate), Q2 (DE readability target), Q4 (override-procedure formalism): reviewer-judgement readability stands; prose override mechanism stays prose. Revisit on real corpus growth.
- **project/release-skill-layer** Q2 (pre-release bundle), Q3 (release-drafter rerun safety): stable-only bundles stand, marker-block re-run safety stands; revisit on a first pre-release tag / observed rerun-strip.
- **portfolio/portfolio-inflight-management** Q7 (org-level discussions source): repository-level discussion scope stands; revisit when a portfolio-wide discussion-locations artefact is declared.

## Welle 6 — partial (blog-author)
- **project/blog-author** Q2 (handover-contract YAML schema) + Q3 (hero-image corpus policy): both settled (prose contract stands; hero policy stays consumer-side). Q1 (resolved 2026-06-06 as standing two-route design) and the "Intentionally not open" subsection are retained.
- **project/github-issue-templates** Q3 (security-report routing): chooser routes via `config.yml` contact_links to GitHub private vulnerability reporting; revisit when project-structure defines a concrete SECURITY.md convention.
- **project/lektorat** Q3 (API-reference scope) + Q5 (batched-vs-per-file dispatch): generated reference text stays out of scope; batched dispatch stays the default.

## Welle 2 — brand-owner value decision (2026-06-06)

- **design/corporate-design-colors Q1 (brand-primary OKLCH):** RESOLVED. Brand owner chose a muted indigo `oklch(0.47 0.12 276)`, sRGB hex `#4A529D`. Verified in-gamut (peak chroma ~0.29 at L0.47/H276, so chroma 0.12 is muted with headroom); the +60° tertiary (H336, peak ~0.21), 180° complement (H96, peak ~0.10), split-complement (H66/H126) and analog (H246/H306) derivations all stay in sRGB gamut. Recorded in §Brand harmony axes; the OQ is removed.
- **design/graphic-prompt-authoring Q2 (sref-less style reference):** RESOLVED. Already answered by `corporate-design-colors` §AI image color contract (line 119), which mandates a fixed canonical reference image rather than a free-text style paragraph; with brand-primary now decided, the dependency is closed. The OQ is removed.

The #229 watch-list is now fully cleared.
