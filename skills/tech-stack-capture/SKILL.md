---
name: tech-stack-capture
description: Captures or refreshes the `tech_stack:` block in a Portfolio-Member's `project/portfolio.yml` per the canonical-language file under `spec/portfolio/tech-stack-discovery/` §Discovery sequence. Probes repo signals (lockfiles, `Taskfile.yml`, `.github/workflows/`, `renovate.json5`, `mkdocs.yml`, `.vale.ini`, `.pre-commit-config.yaml`), classifies hits against the closed `kind` (12) and `group` (5) enums from `spec/portfolio/tech-stack/`, compares each candidate against the global stack, drops inherited matches, and confirms every proposed change interactively before writing. Invoke when the user asks to "capture the tech stack", "scaffold a tech_stack block", "refresh the tech_stack section", or equivalent German-language requests. Don't use to author `portfolio/tech-stack.yml` (hand-curated only) or to run signal-verification audits (use `portfolio-audit`). Supports resume on re-invocation per `spec/claude/resumable-work/`.
tags: [scaffolding]
phase: design
summary: "Captures or refreshes the tech_stack block in project/portfolio.yml by probing lockfiles, Taskfile, CI, and tooling configs."
summary_de: "Erfasst oder aktualisiert den tech_stack-Block in project/portfolio.yml durch Sondieren von Lockfiles, Taskfile, CI und Tooling-Configs."
use_when:
  - "you want to capture the tech stack for a Portfolio-Member's portfolio.yml"
  - "you want to refresh the tech_stack section after dependency or tooling changes"
  - "you want a probe-driven scaffold rather than hand-curation"
dont_use_when:
  - situation: "You want signal-verification audits across the portfolio"
    alternative: portfolio-audit
see_also:
  - portfolio-audit
  - tech-stack-drift-reviewer
resumable: true
---

# Tech Stack Capture

Drives the §Discovery sequence per repository defined in `spec/portfolio/tech-stack-discovery/<canonical_language>.md` and produces a `tech_stack:` block in `project/portfolio.yml` that conforms to the entry schema, the inheritance contract, the `kind` enum (12 values), the `group` enum (5 values), and the regroup mechanism declared in `spec/portfolio/tech-stack/<canonical_language>.md`. One operation — fresh capture and refresh share the same path because the spec doesn't distinguish them.

## German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Tech-Stack erfassen"
- "tech_stack-Block aktualisieren"

## Why this is a skill, not an agent

- **Per-entry interactive confirmation is a MUST.** The discovery spec requires the maintainer to accept, reject, or edit every proposed entry, override, and regroup before any write. An agent's fire-and-forget contract would lose that checkpoint per candidate.
- **Persistent on-disk artefact under iterative drafting.** The skill mutates `project/portfolio.yml` (a top-level repo artefact alongside `project/mission.md` and `project/roadmap.md`); the iterative drafting (signal probe → propose → confirm → write) flows back into the main conversation naturally.
- **Cross-spec orchestration.** The skill reads the global manifest, the schema spec, and the discovery spec, then writes per the project's primary YAML conventions. Multi-source orchestration belongs in the skill layer per `spec/claude/skill-vs-agent/`.
- **Counter-dimension considered:** a tool-restricted signal-probing agent could absorb the file-system reads more cleanly, but the load-bearing work is the per-entry conversation with the maintainer, not the probing — skill wins.

## User-language policy

Detect the user's language and respond in it. YAML content written to `project/portfolio.yml` stays English (the file's existing convention; identifiers, kind/group enum tokens, and the `rationale:` prose all stay English regardless of the user's conversation language, matching how every other portfolio manifest in the `nolte/*` portfolio is authored).

## Detection: am I in the right repository?

The skill runs in two roles depending on the active repository:

- **Inside any Portfolio-Member repository** (the typical adopter — repo under `nolte/*` with a `project/portfolio.yml`): the operation runs end-to-end against that repo's `project/portfolio.yml`. Detection: presence of `project/portfolio.yml` AND absence of `.claude-plugin/plugin.json` (so this isn't `claude-shared` itself unless explicitly so).
- **Inside `claude-shared`** (where the global stack lives plus this repository's own `project/portfolio.yml`): the operation runs against `claude-shared`'s own `project/portfolio.yml`. Detection: presence of `.claude-plugin/plugin.json` AND `portfolio/tech-stack.yml` AND `project/portfolio.yml`.

If the active repository carries no `project/portfolio.yml` at all, stop and route the operator to `portfolio-audit` Bootstrap; the per-repo `tech_stack:` block requires the manifest to exist first per `spec/portfolio/portfolio-management/` §Capability inventory per repository.

If the active repository ships its own `portfolio/tech-stack.yml` and isn't `claude-shared`, stop with a `Critical` warning: a Portfolio-Member shipping its own global manifest is forbidden per `spec/portfolio/tech-stack/` §Global tech-stack manifest.

## Preconditions

Before any signal probe, confirm:

- `project/portfolio.yml` exists and parses as YAML. Missing or malformed manifests block the skill; route the operator to `portfolio-audit` Bootstrap or to fixing the parse error first.
- The global manifest at `claude-shared:portfolio/tech-stack.yml` is reachable. When the active repository is `claude-shared`, read it locally. From any other repo, fetch via `gh api repos/nolte/claude-shared/contents/portfolio/tech-stack.yml --jq .content | base64 -d` and discard the raw content once a structured per-entry summary (name, kind, group, status) is in hand. Network-unreachable global manifests block the skill with an explicit error; don't proceed against a stale local cache without operator acknowledgement.
- The active repository is on a feature branch (per `spec/project/branching-model/`), not `develop` or `main`. Confirm via `git rev-parse --abbrev-ref HEAD`. Capturing on a protected branch is a structural error and is refused even if file writes would technically succeed.

## Operations

The single operation produces a `tech_stack:` block in `project/portfolio.yml` (creating it on a fresh capture, replacing it on a refresh). Run the eight steps in order; reordering breaks the spec's discovery sequence.

### 1. Resolve the inherited set

Parse the fetched global manifest into the inherited set: every entry whose `status` is `active` or `experimental`. Drop `deprecated` entries from the inherited working set but keep them visible for later step 7 (deprecation-deviation prompt). Record each inherited entry's `name`, `kind`, and `group` — those are the three fields needed to detect candidate matches and to decide whether a per-repo proposal would shadow an inherited entry.

### 2. Read the existing `tech_stack:` block (refresh path)

When `project/portfolio.yml` already carries a non-empty `tech_stack:` block, parse it into three working sets:

- `existing_additions` — every entry under `tech_stack.additions[]`
- `existing_overrides` — every record under `tech_stack.overrides[]`
- `existing_regroup` — every record under `tech_stack.regroup[]`

On a fresh capture, all three working sets are empty. The operator's confirmations in step 7 decide which existing entries persist, get edited, or get dropped; never silently preserve or remove an existing entry across a refresh.

### 3. Probe repository signals

Read the signal-source set in the order documented in `references/signal-source-map.md`, and read that file now to ground every kind/group/lifecycle proposal that follows: it carries the authoritative per-signal mapping table and is the only source the skill consults for "what does this signal imply".

The probe is read-only. Don't shell out to package managers, don't run installers, don't invoke the language runtime. A missing signal file is an absence, not an error.

For every signal hit, draft a candidate entry with: `name` (kebab-case, derived from the signal), `kind` (from the table), provisional `group` (from the table; refined in step 5), provisional `lifecycle` (from the table), `version` (only when the signal carries an unambiguous version per the spec's SHOULD; otherwise leave blank), and `source_of_truth` (the relative path of the signal that justified the candidate). The candidate's `role` and `status` are deferred until step 7 (operator confirmation) because they aren't signal-derivable.

### 4. Drop inherited matches from the candidate set

For every candidate whose `name` and `kind` both match an inherited entry from step 1, drop it from the candidate `additions` set unconditionally — per the schema spec's MUST NOT, a consumer never re-declares an inherited entry. Record the dropped match in a session-local "inherited-confirmed" list so step 7 can reassure the operator that the inherited entry is already part of their effective stack.

A candidate whose `name` matches an inherited entry but whose `kind` differs is a `Critical` finding — re-declaring under a different kind silently shadows inheritance. Surface it in step 7 with the recommended resolution: rename the candidate, or open a coordination PR against `portfolio/tech-stack.yml` to amend the global entry.

### 5. Propose `group:` per candidate

`group:` is a MUST on every entry (in both `additions[]` and inherited via the global manifest). For every surviving candidate from step 4, propose a `group:` value following the **Deterministic group proposal** rules in `references/signal-source-map.md`: auto-fill the deterministic `kind → group` mappings without prompting (`docs`, `test`, `ci`, `dep-bot`, `build`, `package-manager`, plugin-shaped `framework`, `claude-code` `runtime`), decide the `lint`-kind case from the `source_of_truth` path (`docs/`-scoped → `documentation`, source-tree → `quality`), and **prompt the operator** for the ask-the-maintainer cases (`language`, non-`claude-code` `runtime`, non-plugin `framework`, `deploy-target`, `other`, and any ambiguous `lint`). Heuristic guesses on the ask cases mislead and are forbidden by the spec.

### 6. Propose `lifecycle:` per candidate

`lifecycle:` is optional but SHOULD be proposed. Follow the **Deterministic lifecycle proposal** rules in `references/signal-source-map.md`: auto-fill the unambiguous `kind → lifecycle` mappings (`test` / `lint` / `dep-bot` / `package-manager` → `development`; `ci` / `build` / `docs` → `build`; `deploy-target` → `runtime`) and **prompt** for the ambiguous kinds (`language`, `runtime`, `framework`, `other`), accepting "skip" (leaves the field absent) as a legitimate answer per the SHOULD.

### 7. Interactive per-entry confirmation

Per the discovery spec's MUST, present every proposed delta to the maintainer before any write. The confirmation is a single round through three working sets:

- **Proposed additions** (from steps 3–6): for each candidate, present (a) the full field set (`name`, `kind`, `group`, `lifecycle`, `version`, `source_of_truth`, plus the pending `role` and `status` slots), (b) the signal source(s) that justified the candidate, and (c) the explicit "this is a repo-specific addition, not inherited" classification. The operator answers per entry — accept, reject, or edit. On accept, the operator supplies `role` (one sentence) and confirms `status` (default `active`; `experimental` is a legitimate alternative).
- **Proposed overrides** — for every inherited entry the operator wants to suppress, build an override record with `name`, `inherit: false`, and a non-empty `rationale`. Empty rationale blocks the write. When the operator wants a different version of an inherited entry, surface the spec's two-step path (`overrides:` suppression PLUS a repo-specific `additions:` replacement) — never edit the inherited entry's fields directly.
- **Proposed regroup** — for every inherited entry whose repo-specific purpose differs from the portfolio default (for example `python` used only by the MkDocs build pipeline in this repo), offer a regroup record with `name`, the new `group:`, and a non-empty `rationale`. Refuse a no-op regroup (new `group` equals inherited `group`) and refuse a regroup paired with an override on the same `name` (the override already removes the entry, so the regroup would be dead code).

Free-form additions (entries the operator declares despite no matching signal) are permitted under the spec's SHOULD, but the operator must acknowledge that `portfolio-audit` will `Warning` the missing signal. Record that acknowledgement verbatim in the entry's `rationale` with the marker phrase `acknowledged-missing-signal:` plus a one-sentence justification; the marker downgrades the audit finding to `Suggestion`.

Don't proceed to step 8 until every proposed addition, override, and regroup has been individually confirmed, edited, or rejected. An empty `tech_stack: {}` is a legitimate outcome and is written only after explicit confirmation — silent emptiness is forbidden.

### 8. Compose and write

Compose the final `tech_stack:` block from the three confirmed working sets. Before writing, run the **local validation checklist** in `references/write-validation.md` (mandatory-field, shadow-without-override, override-rationale, regroup, and enum checks); reject or block the write on any failure, surfacing the offending entry.

Then write `project/portfolio.yml` atomically. Preserve unrelated top-level keys (`capabilities:`, `audiences:`, `peers:` — whatever the existing manifest carries); only the `tech_stack:` key is rewritten. Re-parse the file after writing to confirm the result is valid YAML; on parse failure, restore the prior version and surface the parse error.

Confirm in the user's language with the path of the rewritten manifest, a per-section count (`additions:` N, `overrides:` M, `regroup:` K, inherited-confirmed P), and the reminder that opening a PR via `pull-request-create` is the next step — the skill stops at the write.

The skill **MAY** emit a "candidates not picked" log alongside the confirmation summary — signal-derived candidates the operator rejected in step 7, each with a one-phrase reason. The log is for the operator's audit awareness only; it is **NOT** committed to the repository.

## Gotchas

- **`tech_stack: {}` is a legitimate empty result, not a missing block.** A repository that uses the full inherited stack unmodified and has no repo-specific additions writes `tech_stack: {}` after operator confirmation — never omit the key entirely. The audit treats an absent `tech_stack:` key as a `Critical` "manifest doesn't conform to the schema spec"; an empty mapping is the explicit "inherited as-is" affirmation. Don't shortcut by leaving the key out even when the confirmation result has zero additions, overrides, and regroups.
- **The `inherit:` field is a fixed-literal, not a boolean knob.** Every `overrides[]` record carries `inherit: false` exactly — the field is named explicitly for readability and to leave room for a future opt-in semantic without re-shaping the record (per schema §Inheritance semantics). Writing `inherit: true` or omitting the field is a parse error against the schema.
- **Regroup vs. overrides-plus-additions is a one-or-the-other choice.** A consumer who needs a different `group` value on an inherited entry uses `regroup:`. A consumer who needs a different `version`, `role`, `kind`, or any other field on the same entry uses `overrides:` (to suppress) plus `additions:` (to redeclare). Mixing both records for the same `name` is a `Warning` audit finding; the skill refuses to write the combination.
- **Free-form additions need the acknowledged-missing-signal marker.** When the operator insists on declaring an entry that no signal supports (for example a documented deployment target that isn't yet wired into a workflow file), the skill writes `rationale: "acknowledged-missing-signal: <operator-sentence>"`. Without the marker phrase the audit emits a regular `Warning`; with the marker the audit downgrades to `Suggestion`. Don't reword the marker phrase — `portfolio-audit` recognises the exact `acknowledged-missing-signal:` prefix.
- **The global manifest is read-only from this skill.** Even when running inside `claude-shared` itself, the skill never modifies `portfolio/tech-stack.yml`. Promoting a repo-specific addition to portfolio-wide is a hand-curated PR against the global manifest, not a skill operation. When the operator asks the skill to "add this to the global stack", stop and route them to a hand-authored PR.
- **Refresh preserves operator-edited entries that survived a prior round.** When `existing_additions` from step 2 contains entries the current signal probe wouldn't surface (for example a hand-added `kind: deploy-target` entry that doesn't have a signal class), the skill keeps presenting those entries in step 7 with their existing field set so the operator can re-confirm, edit, or drop them. Silently deleting them across a refresh would lose deliberate operator authoring.

## Examples

- Read `examples/01-fresh-capture-empty-additions.md` when running a fresh capture on a project with no existing `tech_stack:` additions.
- Read `examples/02-refresh-after-dep-bot-swap.md` when refreshing the tech-stack capture after Dependabot or Renovate has swapped a dependency.
- Read `examples/03-deviation-with-override-and-regroup.md` when the project deviates from the portfolio baseline and you need to see how overrides and regroup records are authored.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/tech-stack-capture/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- Never write `project/portfolio.yml` without an interactive per-entry confirmation round (steps 7) on every addition, override, and regroup. Skipping confirmation violates the MUST in `spec/portfolio/tech-stack-discovery/` §Discovery sequence per repository regardless of whether the result is technically a no-op.
- Never modify the global manifest `portfolio/tech-stack.yml` from this skill, in any repository. The global manifest is hand-curated per the spec's MUST; automated detection is forbidden.
- Never declare an `additions[]` entry that matches an inherited entry on both `name` and `kind`. Drop inherited matches automatically in step 4; never present them as if they were repo-specific.
- Never write an `overrides[]` record with an empty or whitespace-only `rationale`. The spec's MUST requires a non-empty prose sentence; the audit treats empty rationale as a `Warning`.
- Never write a `regroup[]` record whose new `group` equals the inherited entry's `group` (no-op regroup) or whose `rationale` is empty. Both are `Warning`-grade audit findings — refuse the write upstream.
- Never invent a signal hit. Every candidate entry traces back to a file the skill actually read. Free-form operator additions are permitted via the acknowledged-missing-signal marker; fabricating a signal source the skill didn't probe is forbidden.
- Never edit any field of an inherited entry other than via the schema spec's two mechanisms (`overrides[]` to suppress, `regroup[]` to re-classify the group). The inherited entries' `name`, `kind`, `role`, `version`, `status`, `lifecycle`, `since`, and `source_of_truth` stay portfolio-curated; the per-repo `tech_stack:` block never mutates them.
- Never commit a "candidates not picked" log to the repository. The log is session-local and exists only for the operator's audit awareness; persisting it would couple `portfolio-audit` to in-band log files that aren't part of the schema.
- When `spec/portfolio/tech-stack-discovery/` or `spec/portfolio/tech-stack/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
