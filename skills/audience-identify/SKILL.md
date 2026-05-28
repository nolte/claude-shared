---
name: audience-identify
description: Runs the audience-identification methodology from spec/project/audience-identification/ against a bounded context (software module, service, library, or whole project) and produces an authoritative audience artifact. Invoke when the user says things like "identify audiences for this module", "who are the consumers/users of X", "stakeholder identification for X", "audience analysis before I write the README / SLA / threat model", "list the audiences of this library", or equivalent German-language requests. Also triggers when another spec or skill (readme-structure, future SLA or threat-modeling specs) needs to reference an audience list that does not yet exist for the current context. Don't use to review an existing audience artifact for compliance (use audience-review). Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [audience]
phase: plan
summary: "Runs the audience-identification methodology against a bounded context and produces an authoritative audience artifact."
summary_de: "Führt die Audience-Identifikation gegen einen abgegrenzten Kontext aus und erzeugt ein autoritatives Audience-Artefakt."
use_when:
  - "you want to identify audiences for a module, library, or whole project"
  - "you want a stakeholder list before writing a README, SLA, or threat model"
  - "another spec or skill needs an audience artefact that does not exist yet"
dont_use_when:
  - situation: "You want to review an existing audience artifact for compliance"
    alternative: audience-review
see_also:
  - audience-review
  - audience-doc-author
resumable: true
---

# Audience Identification Skill

Operationalizes the methodology from `spec/project/audience-identification/` so a bounded context (module, service, library, project) gets a reviewable audience list instead of one author's private guesswork.

## Why this is a skill, not an agent

- **Mid-flow interactivity is the contract** — every category enumeration step ("who are the operators?", "any indirect audiences?") is a per-step user dialogue; the spec explicitly forbids batched output and requires confirmation per category.
- **Persistent on-disk artifact** — the resulting audience list lives next to the bounded context. Per `spec/project/audience-identification/` §Artifact location, the canonical default is `AUDIENCES.md` at the root of the bounded context; a README section ("## Audiences" or "## Intended consumers") or an ADR remains an acceptable alternative for small or sub-module contexts. The artifact is read by downstream specs (`mission`, `roadmap`, `release-notes-audience-analysis`, `release-skill-layer`, `readme-structure`, future SLA / threat-model specs); a skill owns persistent state, an agent returns a structured report and forgets.
- **`confirmed` vs `assumed` tagging requires the user in the loop** — the spec mandates that `confirmed` only be set after explicit user statement; an agent's isolated context can't gather that signal interactively.
- Counter-dimension considered: a narrow agent prompt could sharpen the relationship-category vocabulary, but the load-bearing dimension here is interactivity, not output specialization — skill wins.

## User-language policy

- Detect the user's language from their message and reply in that language.
- The written audience artifact uses the surrounding repository's primary language (English by default, unless the repo's existing docs show otherwise — follow the precedent).
- The five relationship-category labels stay consistent with the spec (canonical EN version wins).

## German trigger phrases

The frontmatter `description` keeps the trigger lexicon English-only per `spec/claude/skill-management/` §Structure (plugin-distributed skills). Treat the following German paraphrases as equivalent and discoverable through this skill:

- "Zielgruppen für dieses Modul/Projekt/Paket ermitteln"
- "wer sind die Konsumenten/Nutzer von X"
- "Stakeholder-Identifikation für X"
- "Zielgruppenanalyse vor README/SLA/Threat-Model"
- "Audience-Liste aufsetzen"

## Precondition

Before any operation, verify that `spec/project/audience-identification/<canonical_language>.md` is reachable in the current project. If the spec is missing, stop and tell the user the methodology spec is the input to this skill — without it there is no authoritative list of requirements to run against. Do not improvise a replacement.

## Operations

### 1. `run` — produce an audience artifact

Interactive walk-through. Do not batch — surface each step to the user and let them correct before moving on.

1. **Declare the bounded context in writing.** Prompt for: what the context *is*, where its boundaries run, and what is explicitly outside. Block progress until this is captured. The spec forbids listing audiences before the context is written.
2. **Locate the artifact.** Default to `AUDIENCES.md` at the root of the bounded context — that's the canonical default per `spec/project/audience-identification/` §Artifact location. Before proposing it, check whether the repository already has precedent (grep for `AUDIENCES.md`, existing "Audiences" / "Intended consumers" sections in READMEs, audience-related ADRs); when precedent uses a README section or ADR for the same context size, follow the precedent rather than fragmenting the artifact location. Surface README section and ADR as legitimate alternatives only when the context is small enough that a stand-alone `AUDIENCES.md` would be overkill, or when established repo precedent already lives there.
3. **Enumerate audiences category by category**, in this order, asking the user per category:
   - Direct consumers
   - Operators
   - Contributors / maintainers
   - Governing parties
   - Indirect audiences

   If a category does not apply, record `none` with a reason — the spec requires this, not a silent omission.
4. **Capture per audience**: short label, relationship category, interaction surface (API / CLI / config / docs / dashboard / incident channel / …), what the audience expects or needs, the documentation `track` the audience maps to, and any open question or assumption. Missing information is captured as an open question, not invented.
5. **Tag each audience** as `confirmed` (validated with a real representative or authoritative source) or `assumed` (author inference). Never set `confirmed` without the user saying so explicitly.
5a. **Map each audience to a documentation track** — exactly one of `user-docs` or `developer-docs` (or an extension value declared by an active project-type-specific spec) per `spec/project/docs-audience-tracks/` §Audience-to-track mapping. Apply the portfolio-baseline default first and surface it for confirmation: `user` → `user-docs`; `contributor` / `operator` / `release-manager` → `developer-docs`. The operator may override with a one-line rationale recorded inline next to the audience entry. When the repository genuinely doesn't serve one of the two tracks (a library with no end-user surface, an internal-only product with no contributor surface), record an explicit "no audience maps to this track: <reason>" note in the artefact next to the other track's entries.
6. **Rank by criticality** (primary / secondary / peripheral) where the user can express it. Skip silently if the user cannot rank yet — record as open question.
7. **Offer optional subdivisions** (geography, organizational unit, tenancy) only when the user says they change the expected deliverable. Do not add them by default.
8. **Write the artifact** at the chosen location, using the template at `templates/audiences.template.md`. Confirm the path back to the user in their language.

### 2. `validate` — audit an existing artifact

Run this checklist against a given audience artifact path:

- [ ] Bounded context is declared in writing before any audience entry
- [ ] All five relationship categories are addressed (or explicitly marked `none` with reason)
- [ ] Every entry has label, category, interaction surface, expectation, and an open-questions field (even if empty)
- [ ] Every entry carries a `confirmed` or `assumed` tag
- [ ] Every entry carries a `track` field whose value is `user-docs`, `developer-docs`, or an extension value declared by an active project-type-specific spec; entries that override the portfolio-baseline default carry a one-line rationale inline
- [ ] If the artefact omits one of the two canonical tracks, an explicit "no audience maps to this track: <reason>" note is present and matches the portfolio-baseline omission shape required by `spec/project/mkdocs-structure/` §Audience targeting
- [ ] Criticality ranking is present or openly marked as unresolved
- [ ] Artifact lives next to the context it describes (not in a central registry)

Report pass/fail per item. Offer to fix mechanical gaps (missing tags, missing category placeholders) in place. Do not invent `confirmed` tags or missing audiences while fixing.

### 3. `revisit` — update after a scope change

Triggered when the user signals a material scope change (new public API, new deployment target, new regulated data class, new stakeholder). Re-run operation 1 steps 1–7 as a diff against the existing artifact: show which entries stay, which need re-validation, which become irrelevant. Persist the result only after the user accepts each diff item.

## Gotchas

- **Never set `confirmed` on the operator's behalf.** The spec's `confirmed` vs. `assumed` distinction is load-bearing for downstream consumers (mission, roadmap, release-notes-audience-analysis). `confirmed` requires the operator to explicitly state "yes, I've validated this with a real representative or an authoritative source." `assumed` is the safe default; the skill never silently promotes an `assumed` audience to `confirmed` even when the operator describes them confidently.
- **The artifact location follows existing repo precedent, not a fixed default.** The spec names `AUDIENCES.md` at the bounded-context root as the canonical default, but a repo that already uses a README section ("## Audiences" / "## Intended consumers") or an ADR for the same context should keep that location. The skill greps for precedent before proposing a new location; introducing a new location pattern in a repo that already has a different one fragments the audience surface across the codebase.
- **All five relationship categories must be addressed, not "all that apply."** Direct consumers, operators, contributors / maintainers, governing parties, indirect audiences — each one is either populated or explicitly recorded as `none` with a one-line reason. Silently omitting a category is a spec violation; `none` is a valid answer that proves the category was considered.
- **Optional subdivisions add cost, not always value.** Geography, organizational unit, and tenancy subdivisions only get added when they materially change the expected deliverable. A "European users" subdivision is valuable only if it changes the artefact's content for that subgroup; otherwise it's noise that downstream consumers have to disregard. Default to no subdivisions.
- **The German trigger phrases ship in the body, not the description.** The frontmatter `description` is English-only per `agent-management` §Structure (plugin-distributed). German operator-voice triggers like "Zielgruppen für dieses Modul ermitteln" live in the body's `## German trigger phrases` section so they remain greppable inside an open conversation; routing on the frontmatter alone misses them.

## Examples

- Read `examples/01-fresh-bounded-context.md` when starting a new `run` on a context that has no existing audience artifact.
- Read `examples/02-validate-existing-artifact.md` when running `validate` against an artifact already on disk.
- Read `examples/03-revisit-after-scope-change.md` when a material scope change triggers a `revisit` operation.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/audience-identify/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- Never list audiences before the bounded context is declared in writing — this is the load-bearing rule of the underlying spec.
- Never set an audience to `confirmed` without the user explicitly saying so. `assumed` is always the safe default.
- Never invent audience entries, expectations, or interaction surfaces. Missing information is recorded as an open question, not filled in from plausibility.
- Never silently pick a new artifact location pattern if the repository already has one — follow the precedent.
- Never produce a partial artifact. Either all five categories are addressed (with `none` + reason where applicable) or the write is deferred until they are.
- When `spec/project/audience-identification/` disagrees with this skill, the spec wins. Propose updating this skill rather than diverging silently.
