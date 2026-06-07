# Research Triangulation

Status: draft

## Context
Skills and agents in the `nolte-shared` plugin regularly produce assertions about things that live **outside** the current working copy: version pins of upstream packages and GitHub Apps, file paths in sister repositories, API signatures and defaults of third-party libraries, configuration schemas of external tools (Renovate, Probot, Vale), URLs, quotas, pricing tiers, and product names. When such an assertion is derived from a **single** source (one web-search snippet, one memory entry, one recollection from pre-training), there is no second look that can catch a hallucination, a stale pin, a renamed package, or an API signature that never existed in the first place. The `skill-management`, `agent-management`, and `skill-vs-agent` specs govern how Claude Code capabilities are shaped, but none of them governs **how those capabilities know that what they're about to claim is true**. This spec defines a portfolio-wide triangulation methodology that fills that gap: a deterministic rule for when to triangulate, how many independent sources to require, how to weigh source classes, how to handle conflicts, and how to document the result so a future reader can audit the claim.

**Readers:** skill and agent authors in the `nolte-shared` plugin who anchor repo-external assertions in their artifacts, plus the Claude Code runtime that executes those skills and agents on behalf of operators at run-time.

## Goals
- Factual assertions about repo-external matters in skill outputs, agent reports, and spec drafts are never derived from a single source
- Hallucination risk for upstream version pins, package names, API signatures, and external service behaviour is measurably reduced before the assertion lands in a write target
- Conflicts between sources are surfaced to the operator before a write happens—there is no silent majority vote
- The minimum number of independent sources scales with the blast radius of the downstream action the assertion authorises
- Each artifact that carries a triangulated assertion makes the source list visible, so a later reader can audit the claim without re-running the research

## Non-Goals
- Repo-internal assertions about the current working copy (paths, file contents, frontmatter values)—those are verified directly via `Read` / `Grep` and need no multi-source comparison
- Subjective design decisions (style preference, roadmap priority, naming taste)—the operator or a governing spec is the source of truth
- General pre-training knowledge with no external claim attached (mathematics, common language syntax, well-known concepts)
- Live operator statements about their own environment—the operator is the primary source, and triangulating against them would be misplaced distrust
- Replacement for `spec-readiness-reviewer` (spec internal consistency), `dependency-audit-scanner` (CVE detection), or `workflow-health-triage` (CI red triage)—triangulation is a research methodology, not a tool that supplants those capability-specific specs

## Requirements

### When triangulation is required
- **MUST** triangulate every factual assertion that refers to something **not verifiable** in the current working copy, including:
  - version pins of upstream packages, GitHub Apps, or container images
  - existence, path, or content of files in sister repositories
  - API signatures, default values, or runtime behaviour of third-party libraries or services
  - configuration schemas, allowed values, or deprecation status of external tools (for example Probot apps, Renovate presets, Vale styles)
  - URLs, endpoints, quotas, pricing tiers, or service-level guarantees
  - product, package, or brand names not anchored in the current repo
- **MUST NOT** triangulate repo-internal assertions separately; those are verified by reading the working copy directly, and triangulation against external sources would be slower and less reliable than a `Grep`
- **MUST NOT** triangulate subjective decisions; they aren't factual claims and have no independent sources to compare against
- **MAY** triangulate even repo-internal assertions when the spec carrying the assertion explicitly requires it (for example because the assertion gates an irreversible write outside the repo)

### Source classes and independence
Triangulation distinguishes four source classes:

| Source class | Examples | Weight |
|---|---|---|
| **Primary** | Official documentation of the upstream project, source-of-truth repository, schema file maintained by the upstream owner | Highest |
| **Secondary** | Curated aggregator (npmjs.com, pypi.org, GitHub Marketplace), maintained mirror, dated and authored blog post that cites the primary source | Medium |
| **Web aggregator** | Search-result snippet without clear provenance, AI-generated summary, undated forum post | Low |
| **Model memory** | Pre-training knowledge, memory entries with no cited source | Hypothesis only |

- **MUST** include **at least one** Primary OR Secondary source in every triangulation; three Web-aggregator hits don't satisfy the requirement on their own
- **MUST** treat sources as independent only when their provenance is genuinely different: two hits from the same domain root, the same news item reposted across mirrors, or multiple aggregator snippets that all point back to the same aggregator count as **one** source
- **MUST NOT** count Model memory as one of the required sources—it MAY suggest the hypothesis to be triangulated, but it MUST be confirmed by at least one Primary or Secondary source before the assertion is treated as verified
- **MUST NOT** count a source announcing a behaviour not yet shipped (release notes for a planned version, roadmap entries, pre-release changelogs) toward the independent-source threshold; such a source is a hypothesis—it MAY suggest the hypothesis to be triangulated, but the behaviour MUST be observable in a Primary source (published version, live schema, shipped endpoint) before the assertion is treated as verified
- **SHOULD** require at least one source to carry a verifiable date (last-modified header, commit timestamp, publication date), so a stale pin or deprecated API is detectable

### Minimum source count scales with blast radius
The minimum number of **independent** sources scales with the downstream action the assertion authorises:

| Downstream effect of the assertion | Minimum independent sources |
|---|---|
| Conversational output to the operator without any subsequent write | **2:** one Primary, one independent Secondary |
| Local edit in the working copy (code, docs, draft spec) | **2:** one Primary, one independent Secondary |
| Write to a configuration file that can trigger a release or workflow dispatch (for example `renovate.json5`, `release-publish.yml`, version-bearing files under `docs/requirements.txt`) | **3:** one Primary plus two independent Secondary, or two independent Primary |
| Force-push, release publish, workflow dispatch, cross-repo pull request | **3** plus explicit operator confirmation of the source list before the call |

- **MUST** reach the required minimum source count before an assertion lands in an artifact
- **MUST**, when the required count is unreachable, mark the assertion as `unverified` and hand control back to the operator—never present an under-triangulated assertion as verified
- **SHOULD** prefer the higher tier when uncertain; the cost of one extra source fetch is lower than the cost of a wrong pin merged to `main`
- **MAY** treat a single Primary source as sufficient when no independent Secondary exists despite a documented good-faith search effort (for example a brand-new upstream tool without aggregator presence yet); in that case the source list **MUST** record the documented search effort, AND for any blast-radius tier above "Local edit" the operator **MUST** explicitly confirm the under-triangulated assertion before the downstream action proceeds; autonomous loops with no reachable operator **MUST** abort the write

### Author-time assertions
Assertions hard-coded into long-lived authoring artifacts (a skill's `SKILL.md`, an agent file under `agents/`, or a spec file under `spec/`) persist across many runs and shape many subsequent operations. They therefore warrant a stricter threshold than the run-time tier the assertion would otherwise sit in.

- **MUST** triangulate any author-time assertion to **at minimum the Release/dispatch tier** (three independent sources) when the assertion will direct skill or agent behaviour toward writes outside the working copy—version pins, paths in sister repos, third-party API signatures, external tool defaults
- **MUST NOT** rely on Model memory alone for any author-time assertion, even when the artifact is still in draft and not yet shipped
- **SHOULD** record the source list in the authoring pull request description when the artifact format has no natural inline slot (for example because the assertion is one of many in a long spec body)

### Conflict resolution
- **MUST**, when two or more sources disagree, **stop** and surface the conflict to the operator with:
  - which sources disagree
  - on which specific detail (a version string, a path, an API field, a flag default)
  - the source class of each disagreeing source
  - a verifiable date for each source where one exists
- **MUST NOT** apply a silent majority vote—not even at 2-to-1
- **MUST NOT** fall back to the source-class hierarchy as an automatic tie-breaker; the hierarchy is presented to the operator as guidance, the operator decides
- **SHOULD** name the most likely explanation in the conflict report (for example "Source A is 18 months older than Source B; the upstream behaviour likely changed between those dates") so the operator can decide without re-running the research from scratch
- **MUST**, when the operator isn't reachable (autonomous loop, scheduled run, cron-driven dispatch), **abort the write** and persist the conflict as a findings report rather than guess at a resolution

### Documentation of the triangulation
The findings-report path uses the per-run snapshot pattern (`.audits/<skill>/<run>/`), not the per-target review-plan path defined in `spec/claude/review-plan/`. A triangulation report captures the source list **at the moment the assertion was made**, which is run-scoped data rather than a durable per-target review record—the two patterns coexist intentionally.

- **MUST** make the source list visible in the artifact that carries the triangulated assertion—either inline (footnote, sources list at the end, `[R1]`-style references) or in an associated findings report under the calling skill's audit directory (`.audits/<skill>/<run>/`), depending on the carrier format
- **MUST** record for each source at minimum: the URL or path, the source class, the retrieval date
- **SHOULD** order the source list by weight (Primary first), so a reader skimming for provenance sees the strongest source immediately
- **SHOULD** treat each recorded source as carrying an advisory time-to-live keyed to the assertion type—30 days for version-pin sources, 90 days for API-behaviour or schema sources (aligned with the staleness thresholds in `spec/project/docs-freshness`); when a carrier skill re-uses an assertion whose newest source is older than its TTL to gate a write above the Local-edit tier, it SHOULD re-validate against a current source before the write
- **MAY** refresh the source list on later re-runs—triangulation ages, and re-confirming an old claim against a current source is a legitimate maintenance task

### Interaction with existing skills and agents
- **MUST** apply this methodology in skills that surface repo-external assertions to the operator, including but not limited to: `dependency-audit`, `release-notes-curate`, `cookiecutter-template-manage`, and any skill that invokes WebSearch or WebFetch
- **MUST** apply this methodology in agents that produce repo-external assertions; the triangulation happens **inside** the agent's run and the source list is returned to the dispatching skill as part of the structured report
- **SHOULD** have the dispatching skill review the agent's source list before the operator approval gate and re-surface any conflict the agent flagged
- **MAY** skip the methodology in skills whose scope is purely repo-internal (for example `quality-gate`, `sprint-execute`, `feature-decompose`, `pull-request-create`), provided they make no repo-external assertions

## Acceptance Criteria
- [ ] A skill that uses WebSearch satisfies the minimum source count from the blast-radius table before presenting an assertion as verified to the operator
- [ ] An agent that anchors a third-party API signature in a draft spec records the source list—including URL or path, source class, and retrieval date for each source—either inline in the spec body or in an associated findings report under `.audits/<skill>/<run>/`
- [ ] On a conflict between two source hits, the calling skill stops and surfaces the conflict, naming which sources disagree, on which detail, with which source class each, and with a verifiable date for each source where one exists, instead of casting a majority vote
- [ ] When the required minimum source count is unreachable, the artifact marks the assertion as `unverified` and the skill hands control back to the operator
- [ ] Repo-internal assertions aren't triangulated against external sources; they're verified via `Read` or `Grep` against the working copy
- [ ] Model memory (pre-training knowledge, memory entries without a cited source) doesn't count toward the independent-source threshold
- [ ] Two source hits from the same domain root, or multiple mirrors of the same upstream news item, are counted as a single source rather than as two independent sources toward the threshold
- [ ] In an autonomous loop with no reachable operator, the skill aborts the pending write on a source conflict and persists the conflict as a findings report under the run's audit directory
- [ ] When only one Primary source is available despite a documented good-faith search effort, a skill running above the "Local edit" blast-radius tier stops the write until the operator confirms the single-source assertion, and an autonomous-loop skill with no reachable operator aborts the write entirely
- [ ] An author-time assertion hard-coded in `SKILL.md`, an `agents/*.md` file, or a spec file that will direct skill or agent behaviour toward repo-external writes is triangulated to at least the Release/dispatch tier (three independent sources) before the authoring pull request is merged

## Open Questions
_None at this time._
