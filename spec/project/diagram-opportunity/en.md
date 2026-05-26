# Diagram Opportunities in Documentation Prose

Status: draft

## Context
MkDocs documentation across the portfolio uses Mermaid as the canonical diagram tool (see `spec/project/mermaid-diagrams/`). The Mermaid spec governs how a diagram is set up, authored, and kept in sync once it exists—but it's silent on the inverse problem: prose that **should** carry a diagram and doesn't. Today, the decision to add a diagram is an unaided author judgment call, and the gap accumulates silently in long-form prose (architecture overviews, workflow descriptions, schema explanations) until a reader has to reconstruct relationships from text that a single picture would have made obvious.

This spec authorizes a read-only `diagram-opportunity-reviewer` agent (analogous to `mermaid-diagram-reviewer`, but with the opposite direction of inquiry: not "is this existing diagram spec-conformant" but "is this prose passage a missing-diagram candidate"). The agent scans Markdown source, matches prose patterns deterministically against the Mermaid §Diagram catalog, and emits an audit-friendly findings list. It never writes; diagram generation remains with `mermaid-diagrams-apply`. It never reviews existing diagrams; that's `mermaid-diagram-reviewer`'s job. Its single load-bearing job is to surface the **gap** between current prose and the catalog of diagram types that would express the same content better, with strict volume and confidence gates so the operator is never overwhelmed by a long suggestion stream.

The agent is intentionally flexible across documentation contexts: the same agent serves `docs/<lang>/` audits, README sweeps, ADR reviews, and blog-post lektorat passes—input shape is single-file, glob, directory, or path list, so a future dispatcher (`lektorat-apply` as a sub-check, `audience-doc-author` as a pre-handoff hook, `docs-freshness` as an `info`-severity finding category) can wire it in without re-architecture.

## Goals
- Every prose passage in portfolio documentation that matches a Mermaid §Diagram catalog pattern is surfaced to the operator as a candidate for visualization, with the proposed diagram type and the exact prose trigger that fired the match
- The proposed diagram type is deterministic: the same prose pattern proposes the same diagram type across every repository, and the catalog stays in lockstep with `spec/project/mermaid-diagrams/`
- Findings are auditable: every match cites the line range and the verbatim prose excerpt that triggered it, so a reviewer can validate or dismiss without re-reading the source from scratch
- The volume of findings per run is bounded by default so the operator can act on the top report without being trained into "ignore the wall of suggestions" muscle memory
- The agent is flexible across documentation contexts: the same agent serves `docs/<lang>/` audits, README sweeps, ADR reviews, and blog-post passes via uniform input shapes

## Non-Goals
- Generating, editing, or applying Mermaid diagrams; that's `mermaid-diagrams-apply`'s job and is dispatched after the operator has triaged the findings
- Reviewing diagrams that already exist in the documentation for spec-conformance, drift, or rendering setup; that's `mermaid-diagram-reviewer`'s job
- Suggesting diagram tools or types outside the Mermaid §Diagram catalog (no PlantUML, no draw.io, no `gitGraph`); the catalog is the closed allowlist
- Suggesting non-diagram visualizations like tables, schema boxes, callouts, or admonitions; that's a future sibling spec if the need materializes, not this one
- Translating or rewriting prose; the agent is read-only and never modifies the source documents
- Editorial quality review (readability, comprehensibility, spelling, style, audience-fit); that's `lektorat-apply` / `lektorat-scanner` per `spec/project/lektorat/`

## Requirements

### Scope and input shapes
- **MUST [MUST]** accept any combination of single-file path, glob pattern, directory path, or explicit path list as input; all four input shapes are equivalent first-class entry points
- **MUST [MUST]** default to scanning `docs/<lang>/**/*.md` for every configured documentation language under the repository when no input path is supplied; explicit input arguments fully override the default
- **MUST [MUST]** restrict scanning to Markdown files (`*.md`); other file types are silently skipped without findings
- **MAY [MAY]** be invoked against any path inside the repository—README files, `project/**/*.md`, `spec/**/*.md`, blog posts, ADRs—when the operator passes an explicit path argument; nothing in the agent is hard-wired to `docs/`

### Trigger → diagram-type catalog
The agent matches prose against the following patterns. Each pattern is derived from the corresponding entry in `spec/project/mermaid-diagrams/` §Diagram catalog and proposes the diagram type that the Mermaid spec designates as default for that structure. Pattern matching is intentionally conservative: when a passage matches no pattern with at least `medium` confidence, no finding is emitted.

- **`flowchart`**: dependency-chain prose (`X depends on Y`, `X feeds into Y`, `X consumes Z`), pipeline descriptions with three or more named stages, decision-tree prose with conditional branches, and lists of three or more directed relations between named entities
- **`C4Component`**: architecture-overview prose (`the system consists of modules A, B, C`), boundary descriptions (`X talks to external service Y`), and `what does this repo look like at a glance` framings with named top-level components
- **`classDiagram`**: type-hierarchy prose (`X is a specialization of Y`, `X has attributes/fields A, B, C and methods foo(), bar()`), manifest-structure descriptions with field types, and plugin / skill schema explanations naming both data and behavior
- **`sequenceDiagram`**: ordered-step prose across multiple actors (`first A calls B, then B responds with X, then A forwards to C`), request-response descriptions naming both endpoints, and end-to-end workflow traversals from user trigger to completion
- **`erDiagram`**: schema-field listings with type and cardinality (`each Foo has 0..n Bars, each Bar belongs to exactly one Foo`), configuration-file schema descriptions naming fields and value types, and `1 to many` / `many to many` relation prose

A passage that matches more than one pattern with comparable confidence **MUST [MUST]** be emitted as a single finding with `diagram_type: ambiguous` listing both candidate types in a `candidates` array; the agent never silently picks one.

### Confidence model
- **MUST [MUST]** assign each candidate match one of three confidence levels: `high`, `medium`, or `low`. `high` requires at least two independent surface signals from the same diagram-type pattern in the same passage; `medium` requires one strong signal; `low` requires only a weak surface signal
- **MUST [MUST]** discard `low`-confidence matches before emitting findings; the operator never sees them. This is the primary noise-control lever
- **MUST [MUST]** record the confidence level on every emitted finding so a downstream consumer can filter further

### Volume control
- **MUST [MUST]** cap the per-file finding count at 3 in the top report; additional matches from the same file are recorded only in the full inventory
- **MUST [MUST]** cap the per-run finding count at 15 in the top report; additional matches are summarized as "+ N further candidates (see `full.json`)"
- **MUST [MUST]** prioritize findings for the top-report cap by (1) confidence (`high` before `medium`), then (2) heading prominence (higher heading level first), then (3) file path (lexicographic) to keep the ordering deterministic across runs
- **MUST [MUST]** persist the complete unbounded findings inventory as `full.json` under `.audits/diagram-opportunity/<YYYY-MM-DD-HHMM>/` so the cap never hides data; the caller (skill, agent, or operator) is responsible for placing the file
- **MUST NOT [MUST NOT]** raise the per-file or per-run cap silently based on confidence; the cap is a hard ceiling and overflow is always summarized rather than streamed

### Severity range
- **MUST [MUST]** assign every finding a severity from the closed set `{suggestion, info}`: `suggestion` for matches the agent expects the operator to act on, `info` for context-only matches (for example a passage suppressed via `<!-- diagram-opportunity-skip: ... -->`, recorded for traceability)
- **MUST NOT [MUST NOT]** emit `warning` or `critical` severities; this is a suggestion tool, not a defects list, and a higher severity would train operator fatigue

### Source-classification suggestion
- **MUST [MUST]** propose a source classification on every `suggestion`-severity finding—either `user-described` (with a one-line summary candidate) or `derived` (with a concrete source-path candidate inside the repository)—matching the `<!-- diagram-source: ... -->` annotation form mandated by `spec/project/mermaid-diagrams/` §Diagram sources
- **SHOULD [SHOULD]** prefer `derived` over `user-described` when the prose names a concrete repository artifact (a config file, a workflow, a plugin manifest, a directory tree) that can serve as the source
- **MAY [MAY]** propose multiple candidate sources on a single finding when the prose references several artifacts; the operator picks at apply time

### Per-site mute marker
- **MUST [MUST]** treat a Markdown comment `<!-- diagram-opportunity-skip: <reason> -->` placed on the line immediately preceding a heading or paragraph as a directive to suppress any findings that would otherwise originate from that heading / paragraph and its enclosed prose, until the next heading of equal or higher level
- **MUST [MUST]** record the suppressed match as an `info`-severity finding referencing the cited reason, so the suppression remains visible in the full inventory without polluting the top report
- **MUST NOT [MUST NOT]** treat any other marker form (HTML attribute, frontmatter key, in-prose tag) as a skip directive; the comment-on-preceding-line form is the only supported shape

### Output shape
- **MUST [MUST]** emit findings as JSON with at least the following fields per finding: `file` (repo-relative path), `line_start`, `line_end`, `excerpt` (verbatim prose trigger, ≤ 240 characters), `diagram_type` (one of the Mermaid §Diagram catalog entries or the literal `ambiguous`), `candidates` (array of exactly two diagram-type strings, present only when `diagram_type == ambiguous`), `confidence` (`high` or `medium`), `severity` (`suggestion` or `info`), `source_classification` (`user-described` or `derived`; present on `suggestion`-severity findings), `source_candidate` (string or array of strings; one-line summary for `user-described`, repo-relative path or paths for `derived`)
- **MUST [MUST]** wrap the per-finding array in a top-level object that also carries `scope` (the resolved input paths), `caps` (`per_file`, `per_run` numeric values used by this run), `truncated` (boolean; true when the top-report cap was reached), `further_candidate_count` (integer; zero when not truncated), and `full_findings` (the uncapped findings array; the caller persists it to `.audits/diagram-opportunity/<YYYY-MM-DD-HHMM>/full.json` while rendering `findings` as the top report). The two arrays MUST share the same per-finding object schema; `findings` is a strict prefix of `full_findings` once the deterministic sort order from §Volume control is applied
- **MUST NOT [MUST NOT]** include any free-form prose, recommendations, or commentary in the JSON; the output is a structured findings inventory only

### Dispatcher integration
- **MUST [MUST]** keep the JSON shape stable enough to be consumed by future dispatchers (`lektorat-apply` as a sub-check, `audience-doc-author` as a pre-handoff hook, `docs-freshness` as an `info`-severity finding category) without re-architecture; field additions remain backward-compatible
- **MUST NOT [MUST NOT]** persist findings itself; the caller is responsible for writing `full.json` and any top-report rendering, exactly as `lektorat-scanner` defers persistence to `lektorat-apply` per `spec/project/lektorat/`

## Acceptance Criteria
- [ ] Invoking the agent without input arguments inside a repository with a configured `docs/<lang>/` tree scans every `*.md` file under that tree and emits a structured findings JSON
- [ ] Invoking the agent with an explicit path (a single README, a glob over `project/`, a directory, or a path list) scans exactly the resolved set and ignores the default scope
- [ ] Every emitted finding cites a verbatim prose excerpt (≤ 240 characters) and a line range that matches the cited excerpt's location in the source file
- [ ] Every emitted finding carries a `diagram_type` value that's either one of `flowchart` / `C4Component` / `classDiagram` / `sequenceDiagram` / `erDiagram` or the literal `ambiguous`; no `gitGraph`, no non-Mermaid type ever appears
- [ ] Every `ambiguous` finding carries a `candidates` array with exactly two distinct catalog entries
- [ ] No emitted finding carries `confidence: low`; `low`-confidence matches are absent from both the top report and the full inventory
- [ ] No emitted finding carries severity `warning` or `critical`; only `suggestion` and `info` appear
- [ ] In a synthetic test file with 10 distinct high-confidence matches, the top-level `findings` array contains exactly 3 entries for that file (per-file cap), and the remaining 7 appear only in the top-level `full_findings` array
- [ ] In a synthetic run with 30 distinct high-confidence matches across many files, the top-level `findings` array contains exactly 15 entries (per-run cap), `truncated: true`, `further_candidate_count: 15`, and the top-level `full_findings` array contains all 30 entries; the caller persists `full_findings` as `.audits/diagram-opportunity/<YYYY-MM-DD-HHMM>/full.json`
- [ ] Top-report ordering is deterministic across two runs against the same input: identical findings in identical order
- [ ] A passage immediately preceded by `<!-- diagram-opportunity-skip: <reason> -->` produces no `suggestion`-severity finding from that passage; the suppression is recorded as an `info`-severity finding referencing the cited reason
- [ ] Every emitted `suggestion`-severity finding's `source_classification` is either `user-described` (with a non-empty summary string) or `derived` (with at least one repo-relative path that exists in the working tree)
- [ ] The agent never writes to any file inside the repository, including under `.audits/`; persistence is the caller's responsibility
- [ ] The agent's tool list is the minimum needed for read-only scanning: `Read`, `Grep`, `Glob`, `Bash`; no `Edit`, no `Write`

## Open Questions
- Should the trigger catalog grow a deny-list of well-known prose patterns that look diagram-fit but are intentionally not (FAQ Q-and-A pairs, install command sequences, error-message lists), or is the `<!-- diagram-opportunity-skip -->` marker the only sanctioned escape valve?
- Should the agent expose the per-file and per-run caps as invocation-time overrides, or are the spec defaults (3 / 15) the only supported values to preserve the "operator never overwhelmed" guarantee as a portfolio-wide property?
- Should `info`-severity findings for suppressed passages be omitted entirely when the operator passes a `--quiet` argument, or is the traceability value always worth the (small) line-count cost in the top report?
