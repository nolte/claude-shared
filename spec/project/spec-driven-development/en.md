# Spec-Driven Development

Status: accepted

## Context

The portfolio already carries a substantial spec corpus under `spec/project/` and `spec/claude/`. Each individual spec governs a topic—branching model, pull-request workflow, skill authoring, planning suite, release automation—and downstream skills, agents, and CI configuration draw from it. What's not yet axiomatically declared is **why specs exist at all and what their relationship to implementation is**. Without that declaration, the portfolio drifts toward a "code-first, spec-as-after-the-fact-documentation" posture: implementation decisions accumulate in Claude Code prompts, ad-hoc conversations, or commit-message rationale, and the spec corpus turns into a snapshot of past intent rather than the living foundation of present practice.

This spec fixes the meta-principle: **every development action in this portfolio is driven by a specification.** The spec exists before the change, the change references the spec it implements, and where reality and spec disagree, the resolution is either a code change that re-aligns implementation to spec or a spec revision that captures the new reality—never silent code drift.

The principle rests on four pillars:

1. **Traceability**: every implementation decision resolves back to a concrete MUST/SHOULD/MAY in a versioned spec under `spec/`.
2. **Reproducibility**: the same spec, applied against a comparable repository, produces the same shape—independent of the operator or the Claude Code session that ran it.
3. **Transparency**: decision-grounding lives in `spec/`-tracked markdown under git, not in ephemeral prompts, undocumented chat history, or oral agreement.
4. **Continuous improvement**: every audit finding, defect, or operational friction lands as either a code change implementing an existing spec or a spec revision capturing the changed reality—never as code change without a spec anchor.

This principle is the axiomatic precondition that the existing process specs (`continuous-improvement`, `spec-drift-audit`, `spec-readiness`, `pull-request-workflow`, `skill-management`, `agent-management`) operate on. The planning suite (`mission`, `roadmap`, `feature`, `sprint`) is itself spec-driven by construction—every artefact under `project/` cites the spec that governs it. This document makes that latent contract explicit and load-bearing.

Readers: every contributor and AI agent making a change in the portfolio (each anchored to a spec), reviewers enforcing the spec-anchor rule on PRs and skill/agent frontmatter, and the `spec-drift-audit` process detecting un-anchored artifacts.

## Goals

- Anchor every implementation change in this portfolio to a versioned specification, so traceability holds across every commit, PR, and release without exception.
- Keep decision rationale out of ephemeral surfaces (Claude Code prompts, chat transcripts, oral agreements) and inside `spec/`-tracked markdown that survives session boundaries and tool churn.
- Treat the existing process specs (`continuous-improvement`, `spec-drift-audit`, `spec-readiness`, `pull-request-workflow`, `skill-management`, `agent-management`) as operational consequences of this principle, not as competitors to it.
- Make the spec the authority and the prompt the implementation: a Claude Code prompt may help a contributor find or apply the spec, but it never overrides the spec when the two disagree.
- Anchor every executable plugin asset (every `skills/<name>/SKILL.md` and every `agents/<name>.md`) to the spec it implements, so the plugin's behaviour is itself traceable to written intent.
- Ensure that the planning suite (`mission`, `roadmap`, `feature`, `sprint`) and every future portfolio capability inherits the same spec-anchor contract automatically by being authored under `spec/` first.

## Non-Goals

- Replacing `continuous-improvement` (the audit-and-dispatch process), `spec-drift-audit` (the spec-versus-implementation reconciliation), or `spec-readiness` (the per-spec quality gate). This spec declares what those three presuppose; it doesn't redo them.
- Prescribing a spec-format convention beyond what the `spec` skill and `templates/spec.template.md` already govern. Seven sections (Context, Goals, Non-Goals, Requirements, Acceptance Criteria, References where the spec cites sources, Open Questions), RFC 2119 keywords, EN-canonical with translations—all that stays delegated.
- Demanding that a fully written spec exist before the first prototype line of code. Exploration via the `exp/`-branch prefix in `branching-model` remains permitted, including direct merges of `exp/`-branches into `develop` as throwaway integrations per `branching-model` §Branch roles; the spec-anchor obligation kicks in only at promotion to a stable Conventional-Commits type (`feat/`, `fix/`, `chore/`, `docs/`), not at exploration or throwaway-merge time.
- Replacing architectural decision records (ADRs). The `docs-freshness` spec governs ADR shape and lifecycle separately; spec-driven development is the umbrella norm under which ADRs and specs both live.
- Mandating any particular tool to enforce spec anchoring. Automation can come later (an `spec-anchor-lint` skill, a CI check); this spec defines the rule, not its enforcement mechanism.

## Requirements

- **MUST** anchor every change to runtime code, CI configuration, plugin assets (`skills/`, `agents/`, `.claude-plugin/`), or repository documentation to an existing spec the change implements, or be itself a spec revision. A change that satisfies neither path is a workflow-health finding per `spec/project/workflow-health/`.
- **MUST**, when a pull request touches implementation paths (anything outside `spec/`), carry at least one `Refs spec/<topic>/<slug>/` line in its **Linked issues** section per `spec/project/pull-request-workflow/`. The spec's existing automatic Refs rule already applies to PRs that touch `spec/`-tracked files; this spec extends the obligation to PRs that touch implementation, so every PR—not just spec PRs—is anchored. Machine-authored dependency-bump PRs (Renovate/Dependabot) are implicitly anchored to `spec/project/dependency-audit/` and `spec/project/project-structure/`, which own pinning strategy and audit cadence, and therefore satisfy this MUST without an explicit `Refs` line; hardening the third-party tool's body template to emit one is out of scope.
- **MUST** route every new specification through the `spec` skill so that the duplicate check, EN-canonical-plus-translation pairing, and `spec/README.md` index regeneration happen consistently. A spec written without that path is a `spec-drift-audit` finding regardless of how good its content is.
- **MUST** cite, in every `skills/<name>/SKILL.md` and every `agents/<name>.md`, at least one spec the artefact implements—either inside the YAML frontmatter `description` field or in the body text. Skills and agents that don't trace back to a spec are a `spec-drift-audit` finding; the absence is itself drift, not an exception.
- **MUST NOT** treat any Claude Code prompt—system prompt, slash-command argument, ad-hoc chat instruction, agent prompt—as the authoritative source of an implementation decision. The prompt may quote, summarise, or help locate the spec, but the spec is the standing answer. When prompt and spec disagree, the spec wins; the prompt is updated, not the spec.
- **SHOULD** route every audit finding (from `spec-drift-audit`, `workflow-health`, `quality-gate`, `docs-freshness`, or manual observation) into one of exactly two outcomes: a code change that implements the existing spec, or a spec revision that records the new reality. A third path—code change without spec touch—is itself a workflow-health finding.
- **MAY** treat purely cosmetic edits (typo fixes, em-dash/Vale prose repairs) as implicitly anchored to `spec/project/prose-style/` (or the spec that defines the originating lint rule, for example a YAML/schema linter); no explicit `Refs` line is required for such edits, because the prose-mechanics-vs-semantic-change boundary is already governed by that anchoring spec.
- **MAY** carry an `exp/`-branch (per `branching-model` §Branch roles) without a spec anchor while exploration is open; this is the foundational exception to Requirement #1's spec-anchor MUST for the exploration phase
- **MAY** merge an `exp/`-branch directly into `develop` as a throwaway integration, also without a spec anchor (Requirement #1's MUST doesn't apply to such merges), on the explicit understanding that `branching-model` classifies them as throwaway integrations rather than stable feature/fix/chore/docs changes and that `release-drafter` keeps them out of user-facing release notes (per `branching-model` §Branch roles SHOULDs on the `exp/` prefix and `exp` PR-title categorisation)
- **MUST**, when an `exp/`-branch is promoted to `feat/`, `fix/`, `chore/`, or `docs/`, ensure the branch being promoted either references an existing spec or is accompanied by a parallel spec revision; the spec-anchor obligation engages at promotion time, and promoting an `exp/` branch that satisfies neither path is forbidden
- **MUST** apply this principle recursively to itself: this spec is authored through the `spec` skill, follows `skills/spec/templates/spec.template.md`, and references the skill's hard rules. Future revisions of this spec follow the same path; no out-of-band edits. The recursion extends to every spec-authoring and PR-authoring tool—including the `claude-plugin-developer` agent (which authors skills and agents from the spec) and the `pull-request-create` skill (which writes the PR bodies that carry `Refs` lines)—via the generic Requirement #4 citation MUST; no special-case clause is needed.

## Acceptance Criteria

- [ ] Every pull request landed on `develop` after this spec's adoption that touches implementation paths carries at least one `Refs spec/<path>` line in its body's **Linked issues** section.
- [ ] Every `skills/<name>/SKILL.md` and every `agents/<name>.md` in the repository cites at least one spec it implements—verifiable by `grep -l "spec/" skills/*/SKILL.md agents/*.md` returning every file.
- [ ] No audit finding is closed by a PR that neither implements an existing spec nor revises one; PRs that try to close findings with a third-path edit fail review.
- [ ] Every `exp/`-branch merge into `develop` carries the `exp` Conventional-Commits type and lands in the non-user-facing release-notes category configured per `branching-model` §Branch roles (the `exp` type maps to a hidden `.github/release-drafter.yml` category or is excluded from configured categories). The spec-anchor obligation in Requirement #1 doesn't apply to such throwaway merges; it engages on subsequent promotion to `feat/`/`fix/`/`chore/`/`docs/`.
- [ ] This spec carries, in its `## Open Questions` section, a verifiable cross-reference to the `spec` skill (`skills/spec/SKILL.md`) and to `skills/spec/templates/spec.template.md` so the recursion claim is auditable.
- [ ] Every spec under `spec/` was authored through the `spec` skill—verifiable by absence of orphaned spec folders that bypass the index regeneration step (every entry in `spec/README.md` resolves and every spec folder appears in the index).
- [ ] No Claude Code prompt artefact under `.claude/` or under skill `description` fields contradicts a published spec; the `spec-drift-audit` skill is the canonical detector for the contradiction.

## Open Questions

- Automated enforcement of the spec-anchor rule for PR bodies and skill/agent frontmatter isn't yet wired. **Decision (2026-06-06, waiver recorded at pre-promotion):** the original "≥3 implementation-path PRs missing a `Refs spec/` line" revisit threshold has been met: the Q2 drift audit (retired to git history; tracked items in issue #453) documented seven such PRs (#211, #212, #214, #216, #218, #219, #224). Despite the threshold being met, CI enforcement stays **deliberately deferred**: the spec-anchor MUST remains operator-enforced at authoring and PR time, with `spec-drift-audit` as the long-tail detector for un-anchored skills and agents (Requirement #4, acceptance criterion on line 54), per the Non-Goals. The exemption encodings—Renovate and Dependabot per Requirement #2, `exp/`-branches per the promotion MUST, cosmetic edits per the cosmetic-edit MAY—already define the lint's exact failure surface, so the hardening remains low-cost when it lands. **New revisit trigger (post-waiver):** harden by extending the gh-plumbing `reusable-pr-lint` workflow with a `Refs spec/` assertion (not a standalone `spec-anchor-lint` skill) when either (a) a first implementation-path PR merges to `develop` **after this spec was promoted** still missing its `Refs spec/` line, or (b) the `reusable-pr-lint` workflow gains any body-content assertion beyond the five section headings (making the marginal cost near zero).
- Recursion anchors (auditable per the §Acceptance Criteria recursion check): this spec is itself authored under the [`spec` skill](../../../skills/spec/SKILL.md) and follows the seven-section template at [`skills/spec/templates/spec.template.md`](../../../skills/spec/templates/spec.template.md).
