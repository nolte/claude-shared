# Documentation Freshness

Status: draft

## Context
Every portfolio repository that ships documentation does so through MkDocs, typically in a bilingual layout (`docs/en/` and `docs/de/`) with Architecture Decision Records, user guides, and references back into `spec/`, `src/`, and other repo roots. Those documents drift: renames in the codebase break links, one language tree lags the other, ADRs acquire `TODO` markers that nobody revisits, and the MkDocs build still passes because it doesn't treat dead relative links or content-parity gaps as errors. Contributors don't notice the drift until a reader complains, a release blurb links to a moved page, or a search returns two mutually contradictory guides. This spec defines the freshness practice: what categories of drift count, how they're classified, when the audit runs, and how the findings turn into action. It complements `spec/project/spec-drift-audit/` (spec-versus-implementation) and `spec/project/prose-style/` (Vale-driven prose correctness) by owning the surface those two don't—the drift of the documentation itself against the state of the repository and against its counterpart language tree.

## Goals
- Every repository with MkDocs documentation runs a freshness audit at documented triggers, covering every portable category of drift
- The audit is read-only and produces a severity-sorted report; fixes are a deliberate, separate step
- Findings are classified by a shared severity scale so a broken internal link is treated the same across the portfolio
- Bilingual repositories track language parity as a first-class concern; single-language repositories aren't penalised for not having one
- The audit is clearly distinct from Vale prose linting, from MkDocs's own build, and from spec-drift—each concern owns its own surface

## Non-Goals
- Checking external links (anything `http://` or `https://`): the tradeoffs around rate limits, flakiness, geoblocking, and false positives belong in a different tool
- Prose linting, vocabulary consistency, or style-guide enforcement: that's `spec/project/prose-style/` + `prose-vale-curator`
- Rendering validation: MkDocs itself (`mkdocs build --strict` in CI) is the authoritative check that the site renders
- Declaring the on-disk shape of MkDocs (i18n plugin choice, theme, nav structure)—that's now owned by `spec/project/mkdocs-structure/`. This audit reads `mkdocs.yml` to discover what's actually wired up, then checks conformance against `mkdocs-structure`'s expectations; it doesn't redefine the shape itself
- Defining operational details of the agent that implements the audit (`agents/docs-freshness-checker.md`): those can evolve without a spec change

## Requirements

### Scope
- **MUST** include every markdown file under the MkDocs `docs_dir` configured in `mkdocs.yml`; files outside that directory aren't in scope for this audit
- **MUST** include ADRs located at `docs/<lang>/adr/` (the portfolio convention) when an `adr/` folder exists under any configured language tree
- **MUST** follow every internal markdown link (`](relative-path)` and reference-style `[id]: path`) and every path reference into repo roots the docs mention (`spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/`); broken references are findings
- **MAY** narrow the scope to a single category (links only, parity only, ADRs only) when the caller requests a partial audit; the narrowing **MUST** be recorded in the audit artifact

### Categories of drift
The audit **MUST** classify every finding into exactly one of these categories:

- **Internal-link rot**: a relative markdown link whose target doesn't exist on disk. Anchors are resolved strictly—the file must exist; the anchor target inside the file is a `SHOULD` check, not a `MUST`, because anchor detection is fragile across themes.
- **Cross-tree reference rot**: a link from the docs into `spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/` whose target path no longer exists in the working tree.
- **Language-parity gap**: in a bilingual (or multilingual) repository, a relative path that exists in one configured language tree but is missing in another. The authoring counterpart that prevents the gap at the source is `spec/project/docs-multilingual-authoring/` §Authoring protocol.
- **Content-staleness delta**: in a multilingual repository, counterpart files whose last-commit timestamps diverge beyond a threshold (default 30 days) or whose sizes diverge beyond 2×; these are spot-checked on the N most recently modified files per tree rather than checked exhaustively.
- **Mermaid diagram-source drift**: a Mermaid block in the docs annotated with `<!-- diagram-source: derived—<path> -->` (per `spec/project/mermaid-diagrams/`) whose named source artifact has a more recent last-commit timestamp than the markdown file containing the block—the source has changed but the diagram hasn't been redrawn. The detector compares `git log -1 --format=%cs -- <source>` and `git log -1 --format=%cs -- <markdown-file>`; `user-described` blocks aren't checked because they have no machine-readable source.
- **ADR index drift**: an ADR file on disk that isn't referenced by the corresponding `adr/index.md`, or an `adr/index.md` entry whose file doesn't exist. When `adr/index.md` is generated (declared by a generator hook or a frontmatter marker such as `last_updated: generated` per `spec/project/mkdocs-structure/` §Per-page structure), the ADR-index-drift check **MUST** skip it; freshness of generated indices is owned by the generator's own CI freshness check (a `git diff --exit-code` pass), not this read-only audit (see §Read-only discipline and §Delimitation).
- **ADR status hygiene**: an ADR whose declared status isn't one of `proposed`, `accepted`, `superseded`, `deprecated`, `rejected`; or a `Supersedes: ADR-NNN` reference pointing at an ADR whose status is still `accepted`.
- **Stale markers**: occurrences of `TODO`, `FIXME`, `XXX`, `TBD`, `coming soon`, `placeholder`, `Lorem ipsum` (and their German counterparts) inside documentation; classification depends on context (ADR vs. prose).
- **Track-frontmatter drift**: a page under `docs/<lang>/` (outside `_`-prefixed snippet folders) that lacks the `track` frontmatter key, or whose `track` value isn't `user-docs`, `developer-docs`, or an extension value declared by a project-type-specific spec that the repository has opted into. Sourced from `spec/project/docs-audience-tracks/` §Per-page contract.
- **Content-mode drift**: a page under `docs/<lang>/` (outside snippet folders) that lacks the `content_mode` frontmatter key, or whose `content_mode` value isn't one of `tutorial`, `how-to`, `reference`, `explanation`, `troubleshooting`, `glossary`, `meta`, or an extension value declared by a project-type-specific spec. Mixing-violations (a `how-to` page that ships extended `explanation` content, a `reference` page with embedded recipes) are reported as `content-mode mixing` findings at warning severity—the detection is a Reviewer-judgement signal, not a strict regex, so the audit lists candidate pages without automatically failing.
- **Audience-track mismatch**: a page whose `audience` frontmatter value maps to a track different from the page's `track` frontmatter value, per the default mapping declared in `spec/project/docs-audience-tracks/` §Audience-to-track mapping (overridable per project with a recorded rationale in the audience artefact).

Additional categories **MAY** be added by a repository when its documentation needs them (for example, an API-reference-vs-code check in a repository that ships an OpenAPI spec), but the portfolio-level categories above are the floor.

### Severity classification
- **MUST** adopt the following severity scale:
  - **critical**: internal-link rot, cross-tree reference rot, ADR status inconsistency that breaks a supersedes chain, track-frontmatter drift with an unrecognised value (vs. simply missing), content-mode drift with an unrecognised value; response window: before the next release
  - **warning**: language-parity gap, stale marker inside an ADR whose status is `accepted`, ADR index drift, content-staleness delta > 90 days, Mermaid diagram-source drift, track-frontmatter drift (missing key), content-mode drift (missing key), content-mode mixing candidate, audience-track mismatch; response window: within the current quarter
  - **info**: stale marker inside ordinary prose, content-staleness delta 30–90 days, ADR without a declared status (treat as info, not critical—the ADR is still readable); response window: best effort
- **MUST NOT** downgrade a severity on local judgement alone; disagreement with the classification belongs in an explicit waiver recorded in the audit artifact

### Triggers and cadence
- **MUST** run a full audit at least once per calendar quarter in every repository with a `docs_dir`
- **MUST** additionally run before every release tag that includes documentation changes since the previous audit
- **SHOULD** run as a pre-PR gate whenever the PR modifies documentation; the gate is optional but recommended because drift cascades fastest at PR merge time
- **MAY** run on a shorter cadence (monthly) for repositories whose documentation is a primary product surface
- **MAY** narrow a pre-release run to the critical-severity categories only (internal-link rot, cross-tree reference rot, ADR supersedes-chain breaks, unrecognised track/content-mode values) as a fast pre-tag gate—a named "release-readiness" narrowing preset rather than a separate audit mode; the narrowing **MUST** be recorded per §Scope

### Read-only discipline
- **MUST** be read-only: the audit reports findings, and fixes are a separate, opt-in step taken by an author (or a different agent)
- **MUST NOT** modify, create, or delete any file during the audit—not even in a "safe" way like fixing a typo in a broken link
- **MUST NOT** hit the network; external-link validation is out of scope (see §Non-Goals)
- **MUST NOT** translate, rephrase, or otherwise alter content across language trees; the audit reports parity gaps, not closes them

### Audit artifact
- **MUST** persist the result of every full audit as a commit, issue, or file in the repository; the artifact location **SHOULD** follow the portfolio audit-trail convention `.audits/docs-freshness/<YYYY>-Q<n>.md` (matching the `.audits/<skill>/` pattern used elsewhere) and **MUST** live outside the MkDocs `docs_dir` so the audit never self-scans its own artifacts. Resolved jointly with `spec/project/spec-drift-audit/`'s identical question.
- **MUST** include in the artifact: date, trigger (quarterly, pre-release, PR-change), the repo root and `mkdocs.yml` path used, which categories were run (or narrowed out), the Git revision audited, the per-category severity counts, and the full finding list sorted by severity
- **MUST** cap per-category listings at 15 entries in the artifact and summarise the remainder with a count, so large drift clusters don't flood the report
- **SHOULD** consult `spec/project/parallel-working-copies/` §Audit artefacts in multiple worktrees when the audit runs inside a worktree rather than the primary checkout; the cross-tree and parity findings reflect only the working tree the audit was launched from, and the worktree-local commit, transfer, and cleanup rules for the `.audits/docs-freshness/` artifact live there

### Delimitation
- **MUST** stay separate from `spec/project/prose-style/` and the `prose-vale-curator` agent: Vale owns prose correctness and vocabulary; this audit owns structural drift
- **MUST** stay separate from `spec/project/spec-drift-audit/`: that spec covers spec-versus-implementation reconciliation; this one covers documentation-versus-repository reconciliation
- **MUST** stay separate from `mkdocs build --strict`: the build is the rendering check; the audit is a pre-render drift check
- **MUST NOT** replace continuous CI link-checks when a repository already wires a link-checker into CI; the audit is the periodic deep pass and the pre-release gate, running on top of whatever CI already does

## Acceptance Criteria
- [ ] Every repository with a `docs_dir` contains a traceable docs-freshness audit history (commits, issues, or audit files) with at least one entry per calendar quarter since this spec was introduced, or a documented exception naming which quarter was skipped and why
- [ ] The most recent docs-freshness audit artifact covers every category in §Categories of drift that applies to the repository (bilingual checks run in bilingual repos; ADR checks run where ADRs exist)
- [ ] No `critical` finding from the most recent audit sits unresolved at a release-tag creation; pre-release audits either show zero critical findings or the release notes name the waivers explicitly
- [ ] Every docs-freshness audit artifact records the repo root, the `mkdocs.yml` path, the audited Git revision, and the categories that were (and weren't) run
- [ ] No audit run in any repository modified documentation or any other file; the audit's read-only discipline holds in practice, not just in the spec
- [ ] The agent `agents/docs-freshness-checker.md` produces output that maps 1-to-1 onto the categories and severities declared here, so the artifact can be generated mechanically
- [ ] The audit reports a `track-frontmatter drift`, `content-mode drift`, or `audience-track mismatch` finding whenever a docs page under a non-snippet folder violates the corresponding contract from `spec/project/docs-audience-tracks/` or `spec/project/mkdocs-structure/` §Content modes (Diátaxis alignment)

## Open Questions
- Is anchor-target verification inside a file a future hardening step (raise it from SHOULD to MUST once there's a reliable detector), or does the fragility make that a permanent SHOULD?
- Should the content-staleness spot-check grow from N=5 most-recent files to a percentage of the tree for large docs sets, and if so, what's the threshold?
