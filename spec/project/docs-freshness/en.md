# Documentation Freshness

Status: draft

## Context
Every portfolio repository that ships documentation does so through MkDocs, typically in a bilingual layout (`docs/en/` and `docs/de/`) with Architecture Decision Records, user guides, and references back into `spec/`, `src/`, and other repo roots. Those documents drift: renames in the codebase break links, one language tree lags the other, ADRs acquire `TODO` markers that nobody revisits, and the MkDocs build still passes because it doesn't treat dead relative links or content-parity gaps as errors. Contributors don't notice the drift until a reader complains, a release blurb links to a moved page, or a search returns two mutually contradictory guides. This spec defines the freshness practice: what categories of drift count, how they are classified, when the audit runs, and how the findings turn into action. It complements `spec/project/spec-drift-audit/` (spec-versus-implementation) and `spec/project/prose-style/` (Vale-driven prose correctness) by owning the surface those two don't — the drift of the documentation itself against the state of the repository and against its counterpart language tree.

## Goals
- Every repository with MkDocs documentation runs a freshness audit at documented triggers, covering every portable category of drift
- The audit is read-only and produces a severity-sorted report; fixes are a deliberate, separate step
- Findings are classified by a shared severity scale so a broken internal link is treated the same across the portfolio
- Bilingual repositories track language parity as a first-class concern; single-language repositories aren't penalised for not having one
- The audit is clearly distinct from Vale prose linting, from MkDocs's own build, and from spec-drift — each concern owns its own surface

## Non-Goals
- Checking external links (anything `http://` or `https://`): the tradeoffs around rate limits, flakiness, geoblocking, and false positives belong in a different tool
- Prose linting, vocabulary consistency, or style-guide enforcement: that's `spec/project/prose-style/` + `prose-vale-curator`
- Rendering validation: MkDocs itself (`mkdocs build --strict` in CI) is the authoritative check that the site renders
- Declaring the on-disk shape of MkDocs (i18n plugin choice, theme, nav structure) — those are per-repository decisions, and the audit adapts to what `mkdocs.yml` declares
- Defining operational details of the agent that implements the audit (`agents/docs-freshness-checker.md`): those can evolve without a spec change

## Requirements

### Scope
- **MUST** include every markdown file under the MkDocs `docs_dir` configured in `mkdocs.yml`; files outside that directory aren't in scope for this audit
- **MUST** include ADRs located at `docs/<lang>/adr/` (the portfolio convention) when an `adr/` folder exists under any configured language tree
- **MUST** follow every internal markdown link (`](relative-path)` and reference-style `[id]: path`) and every path reference into repo roots the docs mention (`spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/`); broken references are findings
- **MAY** narrow the scope to a single category (links only, parity only, ADRs only) when the caller requests a partial audit; the narrowing **MUST** be recorded in the audit artifact

### Categories of drift
The audit **MUST** classify every finding into exactly one of these categories:

- **Internal-link rot**: a relative markdown link whose target doesn't exist on disk. Anchors are resolved strictly — the file must exist; the anchor target inside the file is a `SHOULD` check, not a `MUST`, because anchor detection is fragile across themes.
- **Cross-tree reference rot**: a link from the docs into `spec/`, `src/`, `scripts/`, `docker/`, `helm/`, `tests/`, `tools/` whose target path no longer exists in the working tree.
- **Language-parity gap**: in a bilingual (or multilingual) repository, a relative path that exists in one configured language tree but is missing in another.
- **Content-staleness delta**: in a multilingual repository, counterpart files whose last-commit timestamps diverge beyond a threshold (default 30 days) or whose sizes diverge beyond 2×; these are spot-checked on the N most recently modified files per tree rather than checked exhaustively.
- **ADR index drift**: an ADR file on disk that isn't referenced by the corresponding `adr/index.md`, or an `adr/index.md` entry whose file doesn't exist.
- **ADR status hygiene**: an ADR whose declared status isn't one of `proposed`, `accepted`, `superseded`, `deprecated`, `rejected`; or a `Supersedes: ADR-NNN` reference pointing at an ADR whose status is still `accepted`.
- **Stale markers**: occurrences of `TODO`, `FIXME`, `XXX`, `TBD`, `coming soon`, `placeholder`, `Lorem ipsum` (and their German counterparts) inside documentation; classification depends on context (ADR vs. prose).

Additional categories **MAY** be added by a repository when its documentation needs them (for example, an API-reference-vs-code check in a repository that ships an OpenAPI spec), but the portfolio-level categories above are the floor.

### Severity classification
- **MUST** adopt the following severity scale:
  - **critical**: internal-link rot, cross-tree reference rot, ADR status inconsistency that breaks a supersedes chain; response window: before the next release
  - **warning**: language-parity gap, stale marker inside an ADR whose status is `accepted`, ADR index drift, content-staleness delta > 90 days; response window: within the current quarter
  - **info**: stale marker inside ordinary prose, content-staleness delta 30 – 90 days, ADR without a declared status (treat as info, not critical — the ADR is still readable); response window: best effort
- **MUST NOT** downgrade a severity on local judgement alone; disagreement with the classification belongs in an explicit waiver recorded in the audit artifact

### Triggers and cadence
- **MUST** run a full audit at least once per calendar quarter in every repository with a `docs_dir`
- **MUST** additionally run before every release tag that includes documentation changes since the previous audit
- **SHOULD** run as a pre-PR gate whenever the PR modifies documentation; the gate is optional but recommended because drift cascades fastest at PR merge time
- **MAY** run on a shorter cadence (monthly) for repositories whose documentation is a primary product surface

### Read-only discipline
- **MUST** be read-only: the audit reports findings, and fixes are a separate, opt-in step taken by an author (or a different agent)
- **MUST NOT** modify, create, or delete any file during the audit — not even in a "safe" way like fixing a typo in a broken link
- **MUST NOT** hit the network; external-link validation is out of scope (see §Non-Goals)
- **MUST NOT** translate, rephrase, or otherwise alter content across language trees; the audit reports parity gaps, not closes them

### Audit artifact
- **MUST** persist the result of every full audit as a commit, issue, or file in the repository; the artifact location **SHOULD** be consistent per repository (for example `docs/audits/docs-freshness-YYYY-Q<n>.md`)
- **MUST** include in the artifact: date, trigger (quarterly, pre-release, PR-change), the repo root and `mkdocs.yml` path used, which categories were run (or narrowed out), the Git revision audited, the per-category severity counts, and the full finding list sorted by severity
- **MUST** cap per-category listings at 15 entries in the artifact and summarise the remainder with a count, so large drift clusters don't flood the report

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

## Open Questions
- Should the spec standardise a single artifact file path (for example `docs/audits/docs-freshness.md` with quarterly sections) portfolio-wide, or does per-repository freedom stay?
- Is anchor-target verification inside a file a future hardening step (raise it from SHOULD to MUST once there's a reliable detector), or does the fragility make that a permanent SHOULD?
- Should the content-staleness spot-check grow from N=5 most-recent files to a percentage of the tree for large docs sets, and if so, what's the threshold?
- Does the portfolio want a dedicated "release-readiness docs audit" mode that runs only §Critical checks for fast pre-tag gating, or does the full audit stay the only mode?
- When an `adr/index.md` is itself generated (by a script or a plugin), should the ADR-index-drift check skip it, or should generated indices be rebuilt and diffed as part of the audit?
