# Portfolio-Inherited Spec Layer

Status: draft
Portfolio-Scope: portfolio

## Context

The `nolte/*` portfolio governs its repositories through a shared spec corpus. The canonical copy of every portfolio-wide convention—the branching model, the pull-request workflow, the project structure, the plugin-authoring contract—lives in this `claude-shared` hub repository under `spec/`. Today a consumer repository that wants to be governed by one of these conventions has only one option: **copy the spec file verbatim** into its own `spec/` tree. That copy is an immediate DRY violation. The moment the hub revises the canonical spec, every copy is silently stale, and there is no mechanism that can tell an *intentional* per-repository deviation from an *accidental* drift. `spec/project/spec-drift-audit/` can reconcile a single repository's specs against its own implementation, but it has no notion of an upstream canonical a local spec is supposed to track.

This is the gap `spec/portfolio/tech-stack/` already closed for the technical building blocks of a repository: a portfolio-wide global stack lives once in the hub, every member inherits it, and deviations are declared, never implied by omission. This spec brings the same **inherit-by-reference, declare-every-deviation** contract to the spec corpus itself.

It defines a **portfolio-inherited spec layer**: a mechanism by which a consumer repository *references* portfolio-wide specs that live canonically in the hub instead of copying them. The load-bearing premise is **DRY**: a portfolio-wide spec exists **exactly once**, in the hub, and every consumer references it. The consumer stores only the inheritance manifest plus any declared deltas—never a copy of the inherited text.

The contract is a deliberate **hybrid precedence model**, grounded in external best practice (the full cited research is at `.resume/portfolio-inherited-spec-layer/research-report.md`). Configuration tools (TypeScript `extends`, ESLint, Helm, Kustomize, Renovate) converge on *local-wins, last-defined*, but they resolve overrides by position and omission with no marker, so silent divergence is always possible. Governance systems with invariants (AWS IAM explicit-deny-wins, OPA/Rego conflict errors, CSS cascade-layers) instead make divergence loud and let an authoritative layer lock values a local layer can't weaken. A spec corpus is a governance corpus, so this spec adopts the governance model: **inherited specs are authoritative by default; a consumer diverges only through an explicit, reasoned override; undeclared divergence is a hard failure; and a portfolio-locked tier of invariants can't be weakened downstream at all.** This mirrors the two inheritance idioms the portfolio already runs, namely `tech-stack` additive-override-with-rationale and the Probot/Renovate `_extends`/`extends` tag-pinned reference—so the portfolio keeps one mental model for inheritance rather than inventing a third dialect.

Readers: maintainers of `nolte/*` consumer repositories who want to be governed by hub specs without copying them; the `claude-shared` maintainer who curates which specs are portfolio-wide; the `spec` skill, which gains a local-vs-inherited drift pass; `spec-drift-audit` and `spec-readiness`, which classify inheritance findings; contributors migrating a repository from copied specs to referenced ones. Implementors extending the `spec` skill or the `spec/.spec-config.yml` schema work from §Requirements; consumer-repository maintainers work from §"Copy→reference migration path" and §"The inheritance manifest"; a `spec-drift-audit` maintainer works from §"Drift detection."

Provenance: this spec is authored under the `spec` skill and follows the six-section template at `skills/spec/templates/spec.template.md`; future revisions follow the same path per `spec/project/spec-driven-development/`.

## Goals

- A portfolio-wide spec lives **exactly once** in the hub and is referenced by every consumer; no consumer ever stores a verbatim copy of inherited spec content.
- A consumer declares which hub it inherits from, pinned to an explicit release, in one manifest key (`inherits:` in `spec/.spec-config.yml`), so adopting an upstream revision is a conscious, reviewable bump rather than invisible drift.
- Inherited specs are authoritative by default; every consumer deviation is **visible, reasoned, and reviewable**, and undeclared divergence from the canonical is a hard failure, never a silent shadow.
- A small **portfolio-locked invariant** tier exists that a consumer may make stricter but never weaker—the AWS-SCP-style guardrail for rules the portfolio refuses to let any repository opt out of.
- The set of inheritable specs is curated **per spec**, not per directory, so a docs-only consumer is never forced to inherit a code-only spec and vice versa.
- Cross-references resolve deterministically in the combined namespace `local ∪ inherited`, with collisions surfacing as errors rather than silent last-wins, and ghost references caught exactly as `spec/project/spec-readiness/` already requires.
- A consumer whose `canonical_language` differs from the hub's inherits the hub's canonical artefact as the single source of truth and keeps its own language as a derived translation view, so no language pair multiplies the number of authoritative copies.
- There is a defined, mechanical migration path from a copied spec to a referenced one, with `nolte/claude-home-assistant#14` as the worked case.

## Non-Goals

- **Choosing which specs are portfolio-wide.** This spec defines the `Portfolio-Scope:` flag and its semantics; *which* hub specs carry `portfolio` scope is the `claude-shared` maintainer's curation call, made one spec at a time. This spec defines the mechanism, not the membership list.
- **Replacing `spec/portfolio/tech-stack/`.** That spec inherits the *technical building blocks* of a repository; this spec inherits the *spec documents* themselves. They share an inheritance idiom deliberately but govern disjoint artefacts.
- **A general transitive inheritance resolver.** Inheritance is intentionally shallow: one hub layer plus one consumer layer, no multi-hop chains (see §"Shallow chain and root boundary"). A C3-style linearization for deep chains is explicitly out of scope and parked in §Open Questions.
- **Generating the consumer's translation view automatically.** This spec requires that a non-canonical-language rendering be *derived* and *never authoritative*, and that drift checks run canonical-to-canonical; it doesn't define the translation-generation workflow itself, which the `spec` skill's existing translation flow already owns.
- **Redefining the severity scale or the ghost-reference rule.** The severity scale is owned by `spec/claude/review-plan/` §"Severity scale" and the ghost-reference rule by `spec/project/spec-readiness/`; this spec references both and restates neither.
- **The marketplace publish mechanics and plugin-version bump.** Owned by `spec/project/release-automation/` and the manifest specs; this spec only requires that the inheritable spec subset *ships* with the plugin and is *tag-pinned*.
- **Deep-merging inherited prose.** An override replaces a whole declared section; this spec doesn't define paragraph- or sentence-level merge of inherited spec text (see §"Override granularity and merge depth").

## Requirements

### The inheritance manifest

- **MUST** locate the consumer's inheritance declaration in its existing `spec/.spec-config.yml` under a new optional top-level key `inherits:`. A repository with no `inherits:` key inherits nothing and is governed solely by its local `spec/` tree; the key is purely additive to the three keys (`canonical_language`, `languages`, `spec_root`) the file already carries.
- **MUST** structure `inherits:` as a list of **source records**, each carrying exactly these fields:
  - `source`: the hub identifier—the plugin/marketplace name whose shipped spec corpus is being inherited (reference value: `nolte-shared`).
  - `ref`: a **tag-pinned** release identifier of that hub (for example `v0.1.8`). The `ref` **MUST NOT** be a floating branch name; a floating or absent `ref` is a `Warning` audit finding (§"Audit and CI integration"). This is the explicit improvement over Probot Settings `_extends`, which floats the referenced repository's default branch and offers no tag-pinning (see §References).
  - `overrides:` (optional): a list of **override records** per §"Precedence and override declaration."

  ```yaml
  canonical_language: en
  languages: [en, de]
  spec_root: spec
  inherits:
    - source: nolte-shared
      ref: v0.1.8
      overrides:
        - spec: project/branching-model
          section: "§Branch roles"
          reason: "trunk-based repo; the long-lived develop branch role does not apply"
          local: spec/project/branching-model/override.md
  ```

- **MUST** resolve each inherited spec by its **logical key** `<topic>/<slug>` (for example `project/branching-model`), independent of which language file carries it. The key is the stable identifier across the inheritance boundary; the surface filename and language aren't.
- **MUST** treat the resolved hub corpus as a **regenerable cache**: if an implementation materialises inherited spec files on disk for offline reading, it does so under a gitignored cache path (reference path: `.spec-cache/`) and never inside the consumer's tracked `spec/` tree. A tracked verbatim copy of inherited content is a `Critical` audit finding—it's exactly the copy this spec exists to eliminate.

### The `Portfolio-Scope:` flag

- **MUST** gate inheritability **per spec** with a `Portfolio-Scope:` header line in the canonical file, sitting alongside the existing `Status:` line. Its value is one of:
  - `portfolio`: the spec is part of the inheritable set—a genuine portfolio-wide invariant a consumer may reference.
  - `local`: the spec is repo-internal and is never inherited.
- **MUST** default a spec with no `Portfolio-Scope:` line to `local`. Inheritability is opt-in; a spec becomes portfolio-wide only by an explicit, reviewable act in the hub.
- **MUST** make `portfolio` scope available to specs under **both** `spec/project/*` and `spec/claude/*`. The plugin-authoring contract (`spec/claude/*`: `skill-management`, `agent-management`, `skill-vs-agent`, `review-plan`, `resumable-work`, `plugin-scoping`) is the most genuinely portfolio-wide corpus there is, since every code-bearing repository that ships Claude Code capabilities authors them identically; excluding it would leave the most-shared corpus un-shared.
- **MUST NOT** gate inheritability by directory. A blanket "all of `spec/project/*`" rule would force repo-shaped specs (for example `e2e-test-automation`, `mermaid-diagrams`, `blog-author`, `api-error-handling`) onto consumers that lack that capability, contradicting the audience-split principle of `spec/claude/plugin-scoping/`. The flag is the unit; the directory isn't.
- **MUST** keep the inherited unit the hub's **canonical** content. The flag lives on the canonical file; a translation never carries an independent scope.

### Two-source resolution

- **MUST** compute a consumer's **effective spec set** as the union of (a) the local `spec/` tree and (b) every hub spec whose `Portfolio-Scope:` is `portfolio` at the pinned `ref` of each `inherits:` source.
- **MUST** resolve a lookup of logical key `<topic>/<slug>` against the effective set with **local-first** semantics, subject to the conflict rules below—local-first is the *lookup* order, not a licence for local content to silently win on conflict.
- **MUST** treat a local spec that shares a logical key with an inherited `portfolio`-scope spec as one of exactly two cases:
  - The local spec is a **declared override** (it appears as an `overrides:` record targeting that inherited spec): the resolution is the section-level merge defined in §"Precedence and override declaration."
  - The local spec carries **no** declared override: this is an **undeclared divergence** and a `Critical` audit finding. The consumer must either delete the local copy (and inherit) or declare the override. There is no silent-local-wins path; an undeclared key collision fails like an OPA/Rego conflict error rather than resolving by position.
- **MUST** keep inheritance shallow per §"Shallow chain and root boundary": an inherited spec is taken as-is from the hub and isn't itself re-resolved against a third source.

### Precedence and override declaration

- **MUST** treat every inherited `portfolio`-scope spec as **authoritative by default**: in the absence of a declared override, the inherited canonical governs the consumer unchanged.
- **MUST** require that a consumer deviation from an inherited spec be expressed only through an explicit **override record** under the relevant `inherits:` source, carrying exactly these fields:
  - `spec`: the logical key `<topic>/<slug>` of the inherited spec being overridden; **MUST** resolve to an existing `portfolio`-scope spec at the source's pinned `ref`, else a `Warning` audit finding (broken override reference).
  - `section`: the heading of the inherited section the override replaces, in the `§<Section>` form the corpus already uses for cross-references.
  - `reason`: a non-empty prose sentence justifying the deviation; an empty or missing `reason` is a `Warning` audit finding. This mirrors the mandatory `rationale` on `tech-stack` overrides.
  - `local`: a repository-relative path to the local override file carrying the replacing section content.
- **MUST** resolve a declared override as a **section-level replacement**: the effective spec is the inherited canonical with each declared `section` replaced wholesale by the consumer's `local` content; every non-overridden section remains the inherited canonical. The override file carries only the replaced sections—never a copy of the untouched remainder.
- **MUST** support a **portfolio-locked invariant** tier: a requirement marked `[locked]` immediately after its RFC 2119 keyword (for example `- **MUST** [locked] …`) in an inherited `portfolio`-scope spec is non-overridable downstream. An `overrides:` record whose `section` contains a `[locked]` requirement is a `Critical` audit finding. A consumer **MAY** be *stricter* than a locked invariant (an additional local MUST that doesn't contradict it) but **MUST NOT** weaken or suppress it—the AWS-SCP explicit-deny analogue.
- **MUST NOT** permit any override mechanism other than the declared `overrides:` record plus its `local` file. In particular, editing inherited content in place, shadowing it by an undeclared same-key local spec, or suppressing it by omission are all forbidden (the first two are `Critical`; suppression-by-omission can't arise because nothing is copied to omit).

### Override granularity and merge depth

- **MUST** make the **section** the unit of override. There is no implicit deep-merge of inherited prose: a consumer that wants to amend a single requirement inside a section replaces the whole section (with the amendment included) and states the `reason`. This matches the cross-tool finding that arrays and nested blocks default to wholesale replacement, not concatenation—making merge depth explicit avoids the universal config-inheritance pitfall.
- **MUST** treat list-shaped or structured inherited content (for example an enum, a schema block) the same way: an override replaces the whole block; partial-element merge isn't inferred.
- **MAY**, where a future revision defines an explicit additive-merge directive for a specific field, permit deep-merge as a **declared exception** only; until such a directive exists, replace is the only semantics. Any deep-merge MUST be opt-in and named, never the default.

### Combined-namespace cross-reference resolution

- **MUST** resolve every cross-reference of the form `spec/<topic>/<slug>/` against the **combined namespace** `local ∪ inherited`, local-first, exactly as §"Two-source resolution" resolves a direct lookup.
- **MUST** flag a cross-reference whose logical key resolves in neither the local nor the inherited set—or resolves to a spec that lacks the referenced `§<Section>`, as a **ghost reference**, classified `Critical` per `spec/project/spec-readiness/`. This spec adds no new ghost-reference rule; it extends the namespace that rule resolves against to include inherited specs.
- **MUST** treat a logical key that resolves in **both** the local and the inherited set, where the local carries **no** declared override, as a **duplicate-key collision** and a `Critical` finding—never a silent last-wins resolution. This is the JSON-Schema duplicate-`$id` model: a collision is an error, not a precedence puzzle.
- **MUST** resolve a `§<Section>` reference against the **effective** (post-override) spec, so a reference to a section that an override replaced resolves to the replacing content and a reference to a section an override removed is a ghost reference.

### Canonical-language handling

- **MUST** make the inherited unit the hub's **canonical-language** artefact (hub `canonical_language`, currently `en`), identified by its logical key. A consumer inherits the canonical content, not a particular language rendering.
- **MUST** allow a consumer whose `canonical_language` differs from the hub's (for example a `de`-canonical consumer inheriting from an `en`-canonical hub) to inherit the hub canonical as its **source of truth**; the consumer's own-language rendering of an inherited spec is a **derived translation view** and **MUST NOT** be treated as a second canonical copy. Creating a separate authoritative copy in the consumer's language is the silent-fork failure this spec forbids.
- **MUST** run drift detection **canonical-to-canonical**: a consumer's override `local` content is compared, in the hub's canonical language, against the inherited canonical section it replaces at the pinned `ref`. A stale or mismatched translation view never masks or fabricates a divergence, because the check never reads the translation view.
- **SHOULD** maintain the consumer-language translation view of inherited specs through the `spec` skill's existing canonical→translation flow, so a human reader of a `de`-canonical consumer still reads inherited specs in `de` without that view becoming authoritative.

### Distribution and version pinning

- **MUST** distribute the inheritable spec subset by **shipping it with the plugin** through the marketplace, tag-pinned to the plugin release line. This is the package-with-lockfile model: the corpus exists once in the hub registry entry, the consumer references it by pinned version, and the on-disk resolved copy is a regenerable cache. Today `spec/` isn't shipped with any plugin; shipping the `portfolio`-scope subset is a deliberate, bounded packaging change, and the non-`portfolio` (local) specs stay repo-internal.
- **MUST NOT** distribute inherited specs by git submodule, git subtree, sync/vendoring (copier/cruft-style copy), or symlink. Submodules carry documented clone/pull/CI/GC friction; subtree and vendoring physically duplicate the corpus so an intentional override and an accidental drift become indistinguishable; symlinks fail across clones and CI. Each defeats either the exists-exactly-once or the no-silent-divergence goal. (The cruft *drift-detection idea* is adopted in §"Drift detection"; its copy-distribution isn't.)
- **MUST** pin every `inherits:` source to a release tag and adopt upstream revisions by an explicit `ref` bump. The bump **SHOULD** be surfaced per consumer by the portfolio's existing Renovate-style update automation, so staleness becomes a visible PR queue rather than invisible rot.

### Shallow chain and root boundary

- **MUST** keep inheritance **shallow**: exactly one hub layer plus one consumer layer. An inherited spec is taken as-is and is **never** re-resolved against any further source, so no transitive multi-hop chain forms.
- **MUST** treat the hub (`claude-shared`) as the **root**: the hub's own `spec/.spec-config.yml` carries no `inherits:` key, so resolution terminates at the hub. A consumer that's itself a hub for a third repository is out of scope at this revision (see §Open Questions).
- **MUST NOT** allow a cyclic inheritance declaration (a source that resolves, directly or indirectly, back to the consumer); a cycle is a `Critical` audit finding.

### Drift detection

- **MUST** extend the `spec` skill's drift-check operation (today: translation-versus-canonical) with a **local-vs-inherited** pass that, for each `inherits:` source, verifies:
  - every `overrides:` record's `spec` resolves to a `portfolio`-scope spec at the pinned `ref`;
  - every overridden `section` still exists in that inherited spec at the pinned `ref` (a vanished target is a stale override, `Warning`);
  - no overridden `section` contains a `[locked]` requirement (`Critical`);
  - every `reason` is non-empty (`Warning`);
  - no local spec shares a logical key with an inherited `portfolio`-scope spec without a declared override (`Critical`, undeclared divergence);
  - no cross-reference is a ghost reference or a duplicate-key collision in the combined namespace (`Critical`).
- **MUST** run the drift check **against the pinned `ref`**, not against the hub's current `develop`, so a consumer's conformance is judged against the exact upstream it pinned.
- **SHOULD** integrate the local-vs-inherited drift findings into `spec/project/spec-drift-audit/` so inheritance drift is reconciled in the same recurring audit as spec-versus-implementation drift, rather than as an isolated check. Concretely, `spec-drift-audit` surfaces this spec's **inheritance-drift finding class** (the local-vs-inherited findings enumerated above) at the severities mapped in §"Audit and CI integration," alongside its existing spec-versus-implementation findings; this spec owns the finding definitions and severities, `spec-drift-audit` owns the recurring run that reports them.

### Audit and CI integration

- **MUST** classify every finding from this spec using the canonical severity scale from `spec/claude/review-plan/` §"Severity scale"; this spec restates none of the four levels and only maps its findings onto them:
  - `Critical`: a tracked verbatim copy of inherited content in the consumer's `spec/` tree; an undeclared divergence (local spec shadowing an inherited `portfolio`-scope spec without a declared override); an override targeting a `[locked]` requirement; a ghost reference or duplicate-key collision in the combined namespace; a cyclic inheritance declaration.
  - `Warning`: a broken override reference (`spec` doesn't resolve at the pinned `ref`); a stale override (overridden `section` vanished upstream); an empty or missing `reason`; a floating or absent `ref` on an `inherits:` source.
  - `Suggestion`: an `inherits:` `ref` pinned to a hub release more than one closed sprint behind the hub's latest release (the staleness threshold, matching the one-closed-sprint coordination cadence `spec/portfolio/tech-stack/` already uses); a `portfolio`-scope hub spec not yet referenced by any consumer.
  - `Info`: a declared override present on a consumer (deliberate, reviewed deviation—useful context, no action).
- **MUST** make undeclared divergence a **CI failure**, not a soft warning: the local-vs-inherited drift pass exits non-zero on any open `Critical`, so a silent fork can't reach `develop`. This is the loud-failure governance posture, not a discouraged-habit nudge.

### Copy→reference migration path

- **MUST** define the migration from a copied spec to a referenced one as this sequence, for a consumer currently holding a verbatim copy of a hub `portfolio`-scope spec (worked case: `nolte/claude-home-assistant#14`):
  1. Add (or extend) the `inherits:` source in the consumer's `spec/.spec-config.yml`, pinned to a hub `ref` whose corpus contains the canonical spec at the required `Portfolio-Scope: portfolio`.
  2. Diff the local verbatim copy against the inherited canonical at that `ref`. If the copy is identical, delete the local copy outright—it now resolves from the inherited set.
  3. If the copy carries legitimate deviations, capture each as a declared `overrides:` record plus a minimal `local` override file containing only the deviating sections, then delete the rest of the local copy.
  4. Run the local-vs-inherited drift check; resolve every `Critical` (no undeclared divergence, no locked-section override) and every `Warning` before merge.
  5. Land the migration as a spec-anchored PR per `spec/project/pull-request-workflow/`, `Refs`-linking this spec.
- **MUST NOT** complete a migration that leaves both a tracked local copy and an `inherits:` reference for the same logical key; the end state is reference-plus-declared-deltas, never reference-plus-copy.

### Tooling and enforcement

- **MUST** make the resolver entry point for an inherited corpus the plugin's bundled `spec/` payload, read from the installed hub plugin at the pinned `ref` via `${CLAUDE_PLUGIN_ROOT}/spec/`, the same bundled-asset path convention every plugin skill already uses for shipped resources. A consumer's `inherits:` `ref` selects the installed hub-plugin release, and the corpus resolved from `${CLAUDE_PLUGIN_ROOT}/spec/` at that release is the regenerable cache of §"The inheritance manifest." Whether the plugin payload carries only `Portfolio-Scope: portfolio` files or the whole `spec/` tree filtered to `portfolio` scope at resolution time is an implementation choice the tooling step settles; the resolver entry point is fixed at `${CLAUDE_PLUGIN_ROOT}/spec/`, and the marketplace-payload packaging that places `spec/` there is owned by `spec/project/release-automation/`.
- **MUST** extend the `spec/.spec-config.yml` schema with the `inherits:` key (and its source/override record shapes) and recognise the `Portfolio-Scope:` header line and the `[locked]` requirement marker; the schema change is validated by the same CI/pre-commit mechanism that already guards the repository, so a malformed `inherits:` block can't land on `develop`.
- **MUST** extend the `spec` skill (`skills/spec/SKILL.md`) with the local-vs-inherited drift pass defined in §"Drift detection," composing with—not replacing—its existing translation drift-check.
- **MAY** defer richer affordances (a dedicated migration sub-command, automatic override-file scaffolding, a rendered "inherited vs local" view) to later revisions; the load-bearing enforcement is the schema validation plus the drift pass.

## Acceptance Criteria

- [ ] `spec/.spec-config.yml` accepts an optional `inherits:` list of source records (`source`, `ref`, optional `overrides:`); a malformed record is rejected by CI/pre-commit and can't land on `develop`.
- [ ] A spec's canonical file may carry a `Portfolio-Scope:` header line (`portfolio` | `local`); a file with no such line is treated as `local` by the resolution and audit tooling.
- [ ] `Portfolio-Scope: portfolio` is honoured for specs under both `spec/project/*` and `spec/claude/*`; no directory-level inheritability rule exists.
- [ ] The effective spec set of a consumer is the union of its local tree and every inherited `portfolio`-scope spec at each pinned `ref`; a lookup resolves local-first subject to the conflict rules.
- [ ] A local spec sharing a logical key with an inherited `portfolio`-scope spec **without** a declared override produces a `Critical` finding and a non-zero CI exit.
- [ ] A declared `overrides:` record resolves as a section-level replacement: overridden sections come from the consumer's `local` file, all other sections from the inherited canonical, and the `local` file contains only the overridden sections.
- [ ] An `overrides:` record targeting a section that contains a `[locked]` requirement produces a `Critical` finding; a consumer adding a stricter, non-contradicting local MUST alongside a locked invariant doesn't.
- [ ] Every `overrides:` record carries a non-empty `reason`; an empty or missing `reason` produces a `Warning`.
- [ ] Every `inherits:` source carries a tag-pinned `ref`; a floating or absent `ref` produces a `Warning`.
- [ ] A cross-reference whose logical key resolves in neither set, or to a spec lacking the referenced `§Section`, is flagged `Critical` per `spec/project/spec-readiness/`; a key resolving in both sets without a declared override is flagged `Critical` (duplicate-key collision).
- [ ] A `de`-canonical (or otherwise non-hub-canonical) consumer inherits the hub canonical as source of truth; no second authoritative copy in the consumer's language exists, and the drift check compares canonical-to-canonical.
- [ ] No inherited spec is distributed by submodule, subtree, vendoring, or symlink; the inheritable subset ships with the plugin and the consumer references it by pinned `ref`; any tracked verbatim copy of inherited content in `spec/` is a `Critical` finding.
- [ ] Inheritance is shallow and rooted: the hub's `spec/.spec-config.yml` carries no `inherits:` key, an inherited spec isn't re-resolved against a further source, and a cyclic declaration is a `Critical` finding.
- [ ] The `spec` skill's drift-check gains a local-vs-inherited pass run against the pinned `ref` that emits the §"Drift detection" findings and exits non-zero on any open `Critical`.
- [ ] A `spec-drift-audit` run reports the inheritance-drift finding class (the local-vs-inherited findings) at the severities mapped in §"Audit and CI integration," alongside its spec-versus-implementation findings.
- [ ] For a non-hub-canonical consumer, the inherited specs' consumer-language view is produced through the `spec` skill's canonical→translation flow and is never the target the drift check compares against.
- [ ] A `ref` bump on an `inherits:` source is surfaced as a per-consumer update PR by the portfolio's Renovate-style update automation (or an equivalent configured update channel).
- [ ] No repository in the portfolio retains both a tracked copy and an `inherits:` reference for the same logical key (the reference-not-copy end state, verifiable from the local working tree); the `nolte/claude-home-assistant#14` migration is the worked case, verified at PR time against §"Copy→reference migration path."
- [ ] The `.spec-config.yml` schema extension and the `spec` skill drift-check extension are delivered and `task test` passes.

## Open Questions

- **Transitive / multi-hop inheritance.** This revision caps inheritance at one hub + one consumer and treats a consumer-that-is-also-a-hub as out of scope. If a real need for a second layer appears, the resolution rule must become a deterministic, monotonic linearization (C3-style) before depth is permitted, and a `root: true`-style stop boundary must be defined for every layer—revisit then, not pre-emptively.
- **Granularity below the section.** Override granularity is the section. If consumers repeatedly need to amend a single requirement inside a large section and the whole-section replacement proves too coarse in practice, a future revision may add a requirement-ID addressing scheme plus a named additive-merge directive (the declared deep-merge exception §"Override granularity and merge depth" leaves room for). Deferred until the coarse model demonstrably bites.
- **Residual packaging mechanics.** §"Tooling and enforcement" fixes the resolver entry point at `${CLAUDE_PLUGIN_ROOT}/spec/`; the residual choice of whether the plugin payload carries only `Portfolio-Scope: portfolio` files or the whole `spec/` tree filtered at resolution time is a parking-lot detail the tooling step and `spec/project/release-automation/` settle, with no bearing on the inheritance contract itself.

## References

External best-practice sources grounding the precedence and distribution model. The full cited research, with per-claim verification verdicts, is persisted at `.resume/portfolio-inherited-spec-layer/research-report.md` (gitignored working artefact); the load-bearing external behaviours are surfaced here so they're verifiable without it.

- Probot Settings `_extends`, which references a central config in another repo but floats its default branch with no tag pinning: <https://github.com/probot/settings>, <https://github.com/probot/octokit-plugin-config>
- Renovate shareable presets and tag pinning (`extends`, `github>owner/repo#tag`)—the pin-and-bump model this spec mirrors: <https://docs.renovatebot.com/config-presets/>, <https://docs.renovatebot.com/dependency-pinning/>
- AWS IAM policy evaluation—explicit-deny-wins and SCP org-level guardrails, the model for the portfolio-locked invariant tier: <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html>
- OPA/Rego—complete-rule conflict raises a hard `eval_conflict_error` rather than a silent winner, the model for "undeclared divergence fails loud": <https://www.openpolicyagent.org/docs/policy-language/>
- TypeScript `tsconfig` `extends`, where last-defined wins and arrays are replaced wholesale, the merge-depth precedent: <https://www.typescriptlang.org/tsconfig/extends.html>
- npm package locks—pin + lockfile with a regenerable installed cache, the distribution model: <https://docs.npmjs.com/cli/v6/configuring-npm/package-locks/>
- Git submodules—documented clone/pull/CI/GC friction behind the submodule rejection: <https://git-scm.com/book/en/v2/Git-Tools-Submodules>
- cruft—template drift detection via a pinned commit plus an explicit skip-list, the drift-detection idea adopted here (its copy-distribution isn't): <https://github.com/cruft/cruft>
- JSON Schema `$ref`/`$id`, where combined-namespace resolution makes a duplicate `$id` is an error, not a silent last-wins: <https://www.learnjsonschema.com/2020-12/core/ref/>
- CSS cascade layers—an explicit base-guard tier a local layer can't casually override, the cascade analogue of the locked tier: <https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Cascade>
