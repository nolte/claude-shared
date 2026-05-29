# Portfolio Tech-Stack Discovery

Status: draft

## Context

The sibling spec `spec/portfolio/tech-stack/` defines the **shape** of the portfolio tech-stack: a global manifest at `portfolio/tech-stack.yml`, a per-repository `tech_stack:` block in `project/portfolio.yml`, an entry schema, a 12-value `kind` enum, additive inheritance with explicit `inherit: false` overrides, and an audit-integration contract. That spec deliberately stops at the schema and the audit; it doesn't answer three orthogonal questions that the tech-stack capture work also depends on:

1. **How's each entry actually discovered—**which repository signals are inspected, in which order, with which user interaction, and how does the discovery flow tell an inherited entry apart from a repo-specific addition?
2. **Who consumes the resulting inventory—**which producers author it, which direct consumers act on it, and which indirect audiences are influenced by it?
3. **What's the portfolio-wide benefit—**why is a centrally curated global stack plus per-repo deltas worth the curation overhead, and which `project/goals.md` outcomes does it serve?

This spec answers those three questions normatively. It pairs with the schema spec the same way `spec/project/audience-identification/` pairs with downstream specs that consume an audience artefact: the schema is the contract, this spec is the methodology, and the two are kept in sync via reciprocal cross-references.

Readers: the `claude-shared` maintainer authoring `portfolio/tech-stack.yml` and the future capture skill; the maintainer of any Portfolio-Member repository authoring or revising its `project/portfolio.yml`'s `tech_stack:` block; the implementer of the capture skill (Claude Code as co-author); the `portfolio-audit` skill as automated consumer of the resulting manifests; contributors and onboarding readers consulting the rendered portfolio docs.

## Goals

- Codify a reproducible discovery methodology so two operators capturing the same repository's tech-stack land on the same set of entries.
- Make the audience model of the tech-stack inventory explicit, with one bullet per audience naming the surface it touches and the expectation it brings.
- Make the benefits of a portfolio-wide stack explicit and linkable, so a maintainer can justify the curation overhead with one verbatim sentence per benefit when reviewing a PR or planning a sprint.
- Keep the schema spec (`spec/portfolio/tech-stack/`) free of methodology and audience prose, so schema changes don't require a methodology PR and vice versa.

## Non-Goals

- Defining the entry schema, the `kind` enum, the inheritance contract, or the audit severity table—those live in `spec/portfolio/tech-stack/` and aren't restated here.
- Recommending specific tools per `kind` (MkDocs vs. `Docusaurus`, `uv` vs. poetry, etc.). Tool selection is the `claude-shared` maintainer's curation call when authoring `portfolio/tech-stack.yml`; this spec governs the path that gets the entry into the manifest, not the answer to which tool wins.
- Authoring the AUDIENCES artefact for the `claude-shared` repository itself—that's the `AUDIENCES.md` already produced via `audience-identification`. This spec consumes that artefact, it doesn't replace it.
- Specifying how `portfolio-audit` mechanically verifies discovered entries against repo signals—the signal-class list lives in `spec/portfolio/tech-stack/` §Portfolio audit integration. This spec governs how an entry gets *captured*; the schema spec governs how it gets *checked*.
- Designing the capture skill's UX or implementation details. The skill is a separate artefact authored per `spec/claude/skill-management/`; this spec only constrains the discovery flow the skill orchestrates.
- Treating portfolio-anchor repositories (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`) differently during discovery. The discovery flow runs unchanged against an anchor repo and captures how the anchor itself is built. What an anchor *offers* the portfolio (shared workflows, vocabularies, Taskfiles) is a `capabilities:` concern in `spec/portfolio/portfolio-management/`, orthogonal to the `tech_stack:` concern.

## Audiences

The tech-stack inventory carries three audience classes. Each class is cross-referenced with the `claude-shared` repository's `AUDIENCES.md` so a revision of either artefact triggers a sync check on the other.

### Producers

Producers author entries—either directly into `portfolio/tech-stack.yml` or into a Portfolio-Member's `tech_stack:` block via the capture skill.

- **`claude-shared` maintainer (curator of the global stack).** Surface: hand-editing `portfolio/tech-stack.yml` in this repository plus the spec-evolution authority that decides which technical building blocks the portfolio standardises on. Expectation: edits are reviewable, kind-enum drift is rare, and a promotion from `experimental` to `active` follows the SHOULD in `spec/portfolio/tech-stack/` §Inheritance semantics. Criticality: primary. Maps to AUDIENCES.md → contributors / maintainers → `"Repo maintainer (nolte)"`.

- **Portfolio-Member maintainer (per-repo additions and overrides author).** Surface: the capture skill running inside their repository, plus direct hand-edits to `project/portfolio.yml`. Expectation: discovery proposes a complete draft from repo signals, every proposed entry is confirmed interactively before any write, and inherited entries aren't silently re-declared as repo-specific additions. Criticality: primary across the portfolio. Tech-stack-specific refinement not in `AUDIENCES.md`: this audience lives outside the `claude-shared` bounded context (per AUDIENCES.md §Bounded context) but is the primary writer of every per-repo `tech_stack:` block, so this spec names it explicitly.

- **Capture skill (Claude Code as co-author).** Surface: skill orchestration that probes repo signals, drafts entries, presents them to the maintainer, and writes the resulting `tech_stack:` block. Expectation: the skill follows this spec's discovery sequence and the schema spec's entry-shape rules; it never invents entries the repo signals don't support. Criticality: primary. Maps to AUDIENCES.md → contributors / maintainers → `"Claude Code itself as co-author"`.

### Direct consumers

Direct consumers read the inventory and act on it.

- **`portfolio-audit` skill (automated consumer).** Surface: parsing every Portfolio-Member's `project/portfolio.yml` plus `claude-shared`'s `portfolio/tech-stack.yml`, running the signal verification defined in `spec/portfolio/tech-stack/` §Portfolio audit integration, and emitting Critical / Warning / Suggestion / Info findings per `spec/claude/review-plan/`. Expectation: the inventory parses cleanly and the inheritance contract is unambiguous so the audit doesn't need heuristics. Criticality: primary. Tech-stack-specific refinement not in `AUDIENCES.md`: this audience is a software capability of the `nolte-shared` plugin, not a human or organisation tracked by `AUDIENCES.md`'s audience categories; the bullet names it explicitly because the audit is the primary automated consumer of the inventory.

- **Downstream Claude Code users in portfolio projects.** Surface: invoking the capture skill in their own repository to author or revise its `tech_stack:` block, plus reading the rendered portfolio inventory under `docs/<lang>/portfolio/`. Expectation: the skill works without per-repo configuration; the inherited entries are immediately visible without manual declaration; the rendered page is a fair representation of the repo's actual stack. Criticality: primary. Maps to AUDIENCES.md → direct consumers → `"Downstream Claude Code users in portfolio projects"`.

- **Contributor reading the rendered docs during onboarding.** Surface: the documentation site under `docs/<lang>/portfolio/` showing the global stack section and the per-repository sections with inherited / repo-specific / suppressed badges. Expectation: a single page answers "what does this repo build on" without grepping the repository's lockfiles and workflow files. Criticality: secondary. Maps to AUDIENCES.md → contributors / maintainers → `"External contributors via pull request"`.

### Indirect consumers

Indirect consumers don't interact with the inventory directly, but the inventory shapes their experience.

- **Other portfolio repos under `nolte/*` as passive standardisation reference.** Surface: none direct; the global stack acts as a de-facto standardisation reference even for repos that haven't yet adopted the capture skill. Expectation: standardisation decisions surface in the rendered inventory rather than as silent norms. Criticality: peripheral. Maps to AUDIENCES.md → indirect → `"Other Nolte portfolio repos as passive consumers of the conventions"`.

- **End users of downstream projects that install `nolte-shared`.** Surface: none direct; the consistency of the tech-stack across portfolio repos shapes the release discipline and quality posture they see. Expectation: nothing directly from this inventory. Criticality: peripheral. Maps to AUDIENCES.md → indirect → `"End users of downstream projects that install nolte-shared"`.

- **Portfolio-consistency anchors (`nolte/gh-plumbing`, `nolte/vale-style`, `nolte/taskfiles`).** Surface: none direct; the anchors are themselves Portfolio-Member repos whose own tech-stack entries become part of the global inventory once they adopt the capture flow. Expectation: the global stack doesn't silently encode a tool choice the anchors haven't agreed to. Criticality: secondary. Maps to AUDIENCES.md → governing parties → `"Portfolio-consistency anchors"`.

## Benefits

A portfolio-wide tech-stack inventory pays back the curation overhead along five concrete axes. Each benefit names the `project/goals.md` outcome it serves so a reviewer can justify the work in PR or sprint discussions.

- **Visibility across repositories—**a single rendered page answers "which repos use MkDocs", "which repos use `uv`", and "which repo deviates from the documentation default". Without it, the same question requires grepping lockfiles in every repo. Serves O-1 (downstream-consistency for portfolio consumers): a downstream maintainer comparing their repo against the portfolio can do so in one read instead of N greps.

- **Contributor onboarding cost compression—**an onboarding contributor reads one page and gets the technical baseline before opening a single file. Today the same orientation requires reading `pyproject.toml`, `Taskfile.yml`, the workflow files, and the documentation config of each repo separately. Serves O-1 (downstream-consistency) and O-2 (authoring-suite ergonomics for the maintainer): every minute saved on orientation is a minute spent on actual contribution.

- **Standardisation pressure with an explicit safety valve—**the inheritance contract gives the portfolio a default stack (MkDocs, Renovate, GitHub Actions) while letting individual repos opt out via `overrides:` with a non-empty rationale. The pressure is therefore visible (a deviating repo announces itself) rather than implicit (everyone reinvents the docs setup). Serves O-1 (downstream-consistency): convergence happens because deviation costs a rationale, not because conformity is enforced.

- **Auditability of structural outliers—**once the inventory exists, `portfolio-audit` can flag a repo that ships rendered documentation HTML but doesn't inherit the `docs` entry and doesn't carry an override, or a repo that declares a `kind: ci` entry whose `.github/workflows/` folder is empty. The audit can ask structural questions a free-form README simply can't answer. Serves O-2 (authoring-suite ergonomics) and O-3 (every spec is dogfooded against `claude-shared` first): the audit's first dogfood pass also exercises `claude-shared`'s own inventory.

- **Dogfooding the planning suite.** `claude-shared` is itself a Portfolio-Member, so its own `project/portfolio.yml` carries a `tech_stack:` block plus the global manifest under `portfolio/tech-stack.yml`. The capture flow therefore runs against this repository before it ships to consumers, which is exactly the proof-of-life pattern O-3 mandates for every spec the plugin produces. Serves O-3 (every spec is dogfooded against `claude-shared` first).

## Requirements

### Discovery sequence per repository

- **MUST** drive per-repository discovery from repo signals first, before inviting the maintainer to confirm. Signal sources include (non-exhaustively): `pyproject.toml`, `uv.lock`, `poetry.lock`, `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `Taskfile.yml`, `.github/workflows/*.yml`, `renovate.json5` / `renovate.json`, `mkdocs.yml`, `.vale.ini`, `.pre-commit-config.yaml`, `.tool-versions`, and `pyproject.toml:[tool.ruff]` / `[tool.uv]` sections.
- **MUST** classify each signal hit under the closed `kind` enum from `spec/portfolio/tech-stack/` §Kind enum. When two enum values are equally plausible, the discovery flow asks the maintainer rather than picking silently.
- **MUST** compare every candidate entry against the active global stack at `portfolio/tech-stack.yml` *before* writing anything. A candidate that matches an inherited global entry (same `name`, same `kind`) is dropped from the proposed `additions:` list; if the maintainer wants to deviate, the flow offers an explicit `overrides:` record with `inherit: false` and prompts for a `rationale`.
- **MUST** confirm every proposed entry interactively with the maintainer before writing. The confirmation surface presents (a) the candidate entry's full field set, (b) the signal sources that justified it, and (c) the inherited-vs-addition classification. The maintainer answers per entry—accept, reject, or edit.
- **MUST NOT** write a `tech_stack:` block until the maintainer has confirmed at least one round of the proposed delta; an empty `tech_stack: {}` is a legitimate outcome and is written only after explicit confirmation.
- **SHOULD** surface entries the signals don't support but which the maintainer explicitly adds (free-form), and require an explicit acknowledgement that the audit will produce a `Warning` for the missing signal. The skill records the acknowledgement in the entry's `rationale` field; the audit then reads the rationale and downgrades the finding to `Suggestion`.
- **MAY** persist discovery state (a draft delta, a list of dismissed candidates) for a single session so the maintainer can stop and resume; persisted state isn't checked into git.
- **SHOULD** pre-populate the optional `version:` field from the detected signal when the signal carries an unambiguous version (for example `pyproject.toml:requires-python` for `kind: language`, name `python`; `package.json:engines.node` for `kind: runtime`, name `node`; a tag pin in `.tool-versions`). When the signal is ambiguous or absent, the field stays blank rather than carrying a guessed value.
- **MAY** emit a "candidates not picked" log alongside the written `tech_stack:` block, listing signal-derived candidates the maintainer rejected during confirmation, with a one-phrase rejection reason per entry. The log is for audit-readable drift detection only; it doesn't get committed to the repository.
- **SHOULD** propose a `lifecycle:` classification for every entry, derived from `kind:` where the mapping is unambiguous (`test`, `lint`, `dep-bot`, `package-manager` typically map to `development`; `ci`, `build`, `docs` typically map to `build`; `deploy-target` typically maps to `runtime`) and asked of the maintainer when ambiguous (`language`, `runtime`, `framework`, `other` depend on whether the repository ships a service, only build artefacts, or both, so a heuristic guess would mislead). The proposal is presented in the confirmation step above; the maintainer accepts, edits, or skips the field. Skipped is legitimate; the field is optional.
- **MUST** propose a `group:` classification for every entry, derived from `kind:` plus the carrying repository's context. Default mapping (used when the carrying repository's purpose isn't already inferred from prior answers): `docs` → `documentation`; `lint` running against documentation sources → `documentation`, otherwise → `quality`; `test` → `quality`; `ci`, `dep-bot`, plus the Probot governance bots → `automation`; `build`, `package-manager` → `build-tooling`; `framework` with `name` matching a Claude Code plugin shape, and `runtime` matching `claude-code` → `plugin-platform`. For `kind: language`, `runtime`, `framework`, `deploy-target`, and `other`, the flow asks the maintainer for the group rather than guessing, because the choice depends on whether the tool is the application's primary runtime, a docs-only helper, or a delivery channel. The proposal is presented in the confirmation step above; the maintainer accepts, edits, or, for an inherited global entry whose repo-specific use diverges, escalates to a `tech_stack.regroup[]` record per `spec/portfolio/tech-stack/` §Group regrouping.

### Global stack curation in `claude-shared`

- **MUST** curate `portfolio/tech-stack.yml` by hand, never via automated detection from Portfolio-Member repositories. Automatic promotion of a tool to portfolio-wide status because it appears in two or three repos is forbidden—promotion is an explicit human decision in a PR.
- **MUST** route every revision of `portfolio/tech-stack.yml` through the standard pull-request workflow (`spec/project/pull-request-workflow/`), so changes are reviewed, the kind-enum integrity is checked, and Conventional-Commits semantics are preserved.
- **SHOULD** accompany every entry transition (`experimental → active`, `active → deprecated`) with a one-sentence rationale in the PR body referencing either a sprint outcome or a `portfolio-audit` finding, so the lifecycle vocabulary doesn't degrade into busywork.
- **MAY** open a tracking issue under `nolte/claude-shared` when an `experimental` entry has been adopted by one consumer for one closed sprint without an override, prompting the promotion-criterion SHOULD from `spec/portfolio/tech-stack/` §Inheritance semantics.

### Audience-fit gate

- **MUST** treat the audiences enumerated under §Audiences above as binding: a change to the discovery sequence, the global stack, or the rendered inventory that affects a primary audience without that audience having been consulted (directly, via `AUDIENCES.md`, or via `audience-identify`) is reviewable but not mergeable.
- **MUST** consult `AUDIENCES.md` whenever a primary audience changes its surface (for example "Downstream Claude Code users in portfolio projects" gain a new opt-in path) and propagate the change to this spec's §Audiences in the same PR.
- **SHOULD** revisit this spec's §Audiences whenever the `AUDIENCES.md` revisit-triggers fire (per `spec/project/audience-identification/`), even when the trigger isn't tech-stack-specific.

### Benefits-documentation gate

- **MUST** keep each bullet under §Benefits anchored to at least one outcome ID from `project/goals.md` (currently `O-1`, `O-2`, `O-3`). A benefit that can't be linked to an outcome is either rephrased or removed.
- **SHOULD** quote the rendered Benefits section verbatim in the portfolio documentation page under `docs/<canonical_language>/portfolio/`, so a reader on the docs site doesn't need to open the spec to see why the inventory exists.
- **MAY** add a new benefit bullet during a PR that materially expands the inventory's reach (for example "Dependency-bot input prioritisation" once `portfolio-audit` feeds Renovate decisions); each new bullet follows the outcome-anchor rule.

### Cross-references

- **MUST** be referenced from `spec/portfolio/tech-stack/` (canonical and every translation) with a cross-reference (a one-sentence pointer or a short subsection) that names this spec as the owner of the discovery methodology, the audience model, and the benefits prose; restating any of the three inside the schema spec is forbidden.
- **MUST NOT** redefine any of the entry-schema fields, the `kind` enum, the inheritance contract, or the audit-severity table; those live in `spec/portfolio/tech-stack/` and are imported by reference.
- **MUST** be referenced from `AUDIENCES.md` under the relevant revisit-trigger when this spec materially changes its §Audiences.

## Acceptance Criteria

- [ ] `spec/portfolio/tech-stack/` (canonical and every existing translation) carries a one-sentence cross-reference to this spec naming it as the owner of discovery methodology, audience model, and benefits prose.
- [ ] `AUDIENCES.md` §Revisit triggers names this spec as a trigger for the case where §Audiences materially changes.
- [ ] Every bullet under §Audiences resolves to an entry in `AUDIENCES.md`, or §Audiences explicitly notes the bullet is a tech-stack-specific refinement of an AUDIENCES.md entry with a one-phrase justification.
- [ ] Every PR that modifies the §Discovery sequence per repository, the §Global stack curation in `claude-shared`, or the rendered inventory and affects a primary audience names in its description which primary audience was consulted and how (a verbatim quote from `AUDIENCES.md`, a direct conversation, or a re-run of `audience-identify` suffices).
- [ ] Every bullet under §Benefits carries at least one explicit outcome-ID reference to `project/goals.md`.
- [ ] `portfolio/tech-stack.yml` in this repository is hand-authored (verified by git-blame showing maintainer commits, never an automated-generation commit).
- [ ] The capture skill (when it lands) implements the §Discovery sequence per repository in the order documented; a skill-review against `spec/claude/skill-review/` confirms the order.
- [ ] The rendered portfolio documentation page under `docs/<canonical_language>/portfolio/` includes either the verbatim §Benefits section or a short paraphrase with a backlink to this spec.
- [ ] No revision of this spec lands without a corresponding sync check against `AUDIENCES.md`; the PR description names the sync result.
- [ ] No revision of `spec/portfolio/tech-stack/` lands without a sync check against this spec; the PR description names the sync result.

## Open Questions

- Default: keep §Benefits at five bullets and don't add a sixth "release-notes generation" bullet; the §Benefits-documentation gate's MAY clause is the mechanism that adds it later. Revisit when all three hold in one PR: (a) `spec/project/release-notes-audience-analysis/` leaves `Status: draft` (reaches `active`/`stable`); (b) a concrete release-path consumer, namely `release-notes-curate` (Skill A in `spec/project/release-skill-layer/`) or `portfolio-audit`, actually reads a `project/portfolio.yml` `tech_stack:` entry to drive a release-notes decision; and (c) `project/goals.md` carries an outcome ID the new bullet can anchor to. Until (c) holds, the §Benefits-documentation gate **MUST** ("keep each bullet anchored to at least one outcome ID") blocks the bullet regardless of (a)/(b).
