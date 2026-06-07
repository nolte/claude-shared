# Portfolio Management

Status: draft

## Context

The `nolte/*` GitHub organization holds a growing collection of repositories that solve adjacent problems—a Home Assistant integration here, a Python application there, a shared Claude Code plugin, an Ansible role library, vocabulary curation, plumbing repositories. Each repository declares **its own** purpose via `project/mission.md`, **its own** scope via `project/roadmap.md`, and **its own** internal shape via `project/project-structure/`. What no current spec answers is **the cross-repository question**: which repository should own a given capability, where do two repositories quietly carry the same logic in parallel, and which capabilities does the portfolio need but nobody currently provides?

The closest existing controls are partial: `continuous-improvement` enforces a 3-recurrence trigger for Claude-Agent / Claude-Skill specialist gaps, `skill-vs-agent` §Portfolio-wide consistency mandates plugin-level promotion of capabilities recurring across three or more consumers, and `project-structure` defines the *shape* every repository shares. None of those address general capability allocation, cross-repository duplicate detection beyond Claude artifacts, or the existence of a portfolio inventory rendered as documentation. This spec fills that gap.

A *capability* in this spec is a coherent unit of value the repository delivers to a named audience: *plant-care tracking*, *Home Assistant integration*, *reusable Claude Code skills and agents*, *shared GitHub-Actions plumbing*, *Vale style vocabularies* are representative examples. Capabilities are deliberately **coarse-grained**: a capability is roughly what one would write in the README's first paragraph, not what one would put into a function docstring. Finer granularity (modules, libraries, individual functions) is the responsibility of each repository's own internal structure, not of portfolio management.

Readers: maintainers of `nolte/*` repositories, the Claude Code skill / agent that runs the periodic portfolio audit, contributors who consider where to land a new feature.

## Goals

- Every capability in the portfolio has exactly one **owner repository**, declared explicitly and discoverable from a single, machine-readable manifest per repository.
- Cross-repository duplicate capabilities (two or more repositories carrying overlapping logic) are detected by a periodic audit and surfaced as findings, not silently tolerated.
- Portfolio gaps—capabilities that one repository's manifest references as a peer dependency but no Portfolio-Member repository actually provides, or capabilities that another spec demands but the portfolio doesn't yet supply—are detected by the same audit and routed to a remediation owner.
- The aggregated portfolio inventory is rendered as part of the `claude-shared` documentation site, generated automatically from the per-repository manifests, never hand-maintained.
- Allocation decisions ("capability X belongs in repository Y because Z") are recorded with rationale so a later audit can re-evaluate the call without rediscovering the original reasoning.
- The audit itself integrates with `continuous-improvement` as one more audit source, so portfolio findings flow through the same triage and specialist-dispatch loop as drift, workflow-health, and vocabulary findings.

## Non-Goals

- Defining the implementation details of individual capabilities; *how* a capability is built belongs to its owner repository, not to this spec.
- Migration tooling for consolidating duplicate capabilities into a single owner. The audit *identifies* the duplicate; the human-driven consolidation PR is its own work.
- Repository-internal architecture; once a capability is allocated to a repository, the repository's own `project-structure`, `mission`, `roadmap`, and `feature` specs govern its shape. This spec's interest stops at the repository boundary.
- Roadmap prioritization across the portfolio; sequencing of capability introduction is each repository's `roadmap` and `mission` concern, not this spec's.
- Cross-repository runtime dependency tracking (which repository's deployment depends on which other repository's release). That's a deployment / release-pipeline concern, addressed by `release-automation` and any future cross-repo deployment spec.
- Governance of the `nolte/*` organization itself (member access, repo creation rights, etc.). This spec governs *what* lives where, not *who* may decide.
- External (non-`nolte/*`) dependency cataloguing—supply-chain visibility lives in `portfolio/tech-stack` and `dependency-audit`, not in this spec's capability inventory. The rendered portfolio inventory stays strictly within the `nolte/*` boundary.

## Requirements

### Portfolio scope

- **MUST** treat the portfolio as exactly the set of public, non-archived repositories under the `nolte` GitHub organization at the moment a portfolio audit runs. Forks of upstream repositories aren't portfolio members unless ownership has been transferred and the upstream relationship has been severed.
- **MAY** explicitly exclude an individual repository from portfolio scope by setting `portfolio: excluded` at the top of its `CLAUDE.md` together with a one-line rationale; opt-out is intentional and inspectable, never silent.
- **MUST NOT** include archived repositories in the active portfolio inventory. Archived repositories **MAY** appear in a separate "historical capabilities" section of the rendered inventory, marked with the archival date, so peer references from active repositories still resolve.
- **MUST** detect portfolio membership at audit time by querying the GitHub API (`gh api users/nolte/repos --paginate --jq '.[] | select(.archived==false and .private==false and .fork==false) | .name'`) rather than from a hand-maintained list, so adding a new repository to the account automatically pulls it into scope. `nolte` is a GitHub **user** account, so the `users/nolte/repos` endpoint is authoritative (`orgs/nolte/repos` returns 404); the `.fork==false` filter operationalises the fork-exclusion rule above (a fork whose ownership has been transferred and whose upstream link has been severed is re-admitted by hand).

### Capability inventory per repository

- **MUST** require every Portfolio-Member repository to ship a `project/portfolio.yml` manifest that declares the repository's capabilities, audiences served, and peer references to other Portfolio-Member repositories.
- **MUST** structure each capability entry with at minimum: `name` (kebab-case identifier, unique within the manifest), `description` (one or two prose sentences naming what the capability does and for whom), `audience` (a list of audience identifiers cross-referenced with the project's `project/audiences.md` artefact per `audience-identification`), `status` (one of `experimental`, `active`, `deprecated`), and `rationale` (one or two sentences naming why this repository owns the capability).
- **MAY** include optional fields per capability: `peers` (list of `<repo>:<capability-name>` references to capabilities in other Portfolio-Member repositories that this capability depends on or coordinates with), `deprecated_in_favor_of` (when `status: deprecated`, a `<repo>:<capability-name>` reference to the replacement), and `since` (ISO date when the capability first appeared in the repository).
- **MUST** keep capability `name` values stable; renames are explicit decisions tracked in the manifest's git history and **MUST** be coordinated with peer references in other Portfolio-Member repositories during the same coordination window.
- **MUST NOT** declare a capability the repository doesn't actually deliver in shipped code, documentation, or workflows; the audit verifies that each declared capability has at least one corresponding implementation artefact (a code module, a workflow file, a doc page, or a skill / agent file) in the repository.
- **MAY** transition a capability `experimental → active` at the owner repository's discretion; promotion is recommended once the capability is delivered by at least one acceptance-criterion-verified feature in a closed sprint, so the status reflects real delivery rather than intent. The spec deliberately **doesn't** couple capability status to `mission` MVP-status or to `roadmap` item status.
- **SHOULD** surface a capability that has carried `status: experimental` for longer than four closed owner-repository sprints (measured from its `since:` field) as a `Suggestion`-grade stagnation finding, never higher, to prevent indefinite experimental status from becoming hidden drift. This makes `since:` effectively required for `experimental` capabilities.
- **MUST** treat granularity per §Context (README-first-paragraph level): related sub-offerings that share one audience and one purpose are **one** capability—for example, reusable Claude Code skills and agents are a single capability, not two.
- **MUST**, for a shared-library or plugin repository, declare the capabilities it OFFERS to consumers as its own owned capabilities; a consumer that uses them references them via `peers:` and **MUST NOT** re-declare them. The audit treats an owned offering plus consumer `peers:` references as the correct shape, not a duplicate.
- **SHOULD** seed a repository's first `project/portfolio.yml` via the `portfolio-audit` skill's Bootstrap operation, drafted from `project/mission.md` plus the audience artefact; the seed **MUST** be operator-reviewed before commit and **MUST NOT** be generated silently without review, because the mandatory `rationale` and `audience` cross-references can't be fully derived from mission and roadmap alone.

### Tech-stack block

- **MUST** treat `project/portfolio.yml`'s top-level `tech_stack:` key as defined entirely by `spec/portfolio/tech-stack/`; this spec neither redefines the field shape nor constrains its sub-blocks. Whether the key is mandatory or optional for a given Portfolio-Member is decided by the adoption rules in the referenced spec, not here. Capability entries and the `tech_stack:` block are orthogonal: capabilities answer *what* the repository delivers, `tech_stack:` answers *how* it's technically built.

### Cross-repository duplicate detection

- **MUST**, during every audit run, compare every capability across every Portfolio-Member repository's manifest and flag any pair of capabilities whose `description` statements semantically overlap (not just keyword-overlap) as a **duplicate candidate**. Overlap is detected by an LLM-based semantic comparison pass executed by the `portfolio-audit` skill; every flagged pair is surfaced to the operator for confirmation before it becomes a finding (keyword-intersection alone is insufficient).
- **MUST**, on a confirmed duplicate, require the maintainers to either consolidate the capability into one owner repository (the other repositories mark `status: deprecated` with `deprecated_in_favor_of: <owner>:<capability-name>`) or document why the duplication is genuinely necessary (different audience, different runtime constraint, different licensing) in the rationale field of both capabilities.
- **MUST** apply a tolerance window of **one closed sprint per repository, OR 90 calendar days from the first `Warning`, whichever elapses first** before a confirmed duplicate becomes a `Critical` finding; the same audit run that identifies it produces a `Warning`-grade finding, and the next audit after the tolerance window elapses without resolution upgrades the severity. The 90-day calendar backstop keeps the window mechanically enforceable when a repository sits idle and closes no sprint.
- **SHOULD**, when allocating ownership in a consolidation, prefer the repository whose existing `mission` and `audience` artefacts most closely match the capability's audience; ties are resolved in favor of the repository that already hosts the most peer-cluster artefacts (per the `tags` clustering convention from `skill-management` and `agent-management`).
- **MUST NOT** silently leave two `active` capabilities with overlapping `description` in two different Portfolio-Member repositories beyond the tolerance window; the audit treats this as a `Critical` finding routed through `continuous-improvement`'s triage loop.

### Gap analysis

- **MUST** identify, during every audit run, three classes of portfolio gap:
  - **Broken peer reference**: a capability lists a `peers:` entry pointing to a `<repo>:<capability-name>` that no Portfolio-Member repository actually declares (the referenced repo or capability doesn't exist).
  - **Spec-demanded gap**: another spec under `spec/` declares a capability as a precondition (for example a future spec might require "every nolte project provides a release-notes Slack-notifier") and no Portfolio-Member repository's manifest declares that capability.
  - **Cross-repository copy-paste smell**: when the same custom workflow file, configuration block, or non-trivial code pattern is duplicated across three or more Portfolio-Member repositories without a corresponding shared capability in any single Portfolio-Member repository, the pattern is a candidate for promotion to a shared capability—analogous to the 3-recurrence rule in `skill-vs-agent` §Portfolio-wide consistency, but extended beyond Claude artefacts.
- **MUST** route every identified gap to a remediation owner: the audit emits a finding that names the gap class, the affected repositories, and the proposed remediation (create new capability in repository X, extend existing capability in repository Y, decommission the broken peer reference, etc.).
- **SHOULD** open a tracking issue in the most relevant Portfolio-Member repository for any gap that can't be remediated within the same audit cycle; the issue's body **MUST** cite the audit-finding identifier so the loop is closeable from either side.

### Portfolio audit

- **MUST** be implemented as a dedicated skill `portfolio-audit` in the `nolte-shared` plugin (analogous to `dependency-audit`, `vocab-drift-audit`, `docs-freshness-checker`), authored per `skill-management` and reviewed per `skill-review`.
- **MUST** run on a quarterly cadence at minimum, and **MUST** also be invokable on-demand by the operator; the cadence trigger and the on-demand trigger produce the same artefact shape.
- **MUST** produce a Findings-Report file under `.audits/portfolio/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to the `review-plan` artefact spec including the four mandatory sections (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) and the canonical severity vocabulary (`Critical` / `Warning` / `Suggestion` / `Info`) per `review-plan` §Severity scale.
- **MUST** classify findings using the same severity scale as every other audit in the portfolio: a duplicate beyond the tolerance window is `Critical`, a fresh duplicate or a broken peer reference is `Warning`, a copy-paste smell or a spec-demanded gap below the 3-recurrence threshold is `Suggestion`, an observation that doesn't yet require action is `Info`.
- **MUST** integrate with `continuous-improvement` as a recognized audit source by being listed under that spec's "Finding sources in scope" section in any future revision; portfolio findings flow through the same triage-and-specialist-dispatch loop as `spec-drift-audit` and `workflow-health` findings.
- **MUST NOT** be implemented as a Claude Agent—the audit is a multi-step orchestration that includes mid-flow user confirmation on duplicate-resolution decisions, which is the skill side of the `skill-vs-agent` decision rule. The audit **MAY** dispatch read-only specialist agents (for example a `manifest-parser` agent) for context-window-heavy subtasks.

### Documentation rendering

- **MUST** render the aggregated portfolio inventory under `docs/<canonical_language>/portfolio/` in the `claude-shared` repository, with a translation under `docs/<other_language>/portfolio/` for every configured documentation language.
- **MUST** generate the rendered inventory automatically from the per-repository `project/portfolio.yml` manifests; the rendered files **MUST NOT** be hand-edited, and a CI check **MUST** verify that the rendered output matches what the generator would produce. The generation is two-stage: the `portfolio-audit` Render operation collects the manifests (plus each member's verbatim `project/mission.md`) into a committed intermediate snapshot at `portfolio/aggregate.yml`, and a deterministic generator (`scripts/docs/gen_portfolio.py`, invoked by `task docs:portfolio`) renders the per-language pages as a pure function of that snapshot. The snapshot is the only hand-touchable artefact in the chain; the CI freshness check diffs the committed pages against a fresh generator run.
- **MUST** structure the rendered inventory with one section per Portfolio-Member repository, each section containing: the repository's mission statement (quoted from `project/mission.md`), the capability list with status badges, the audiences served (cross-referenced to `audience-identification`), and an outbound-peer-reference list naming which other repositories this one depends on.
- **SHOULD** include a Mermaid diagram visualizing the capability-to-repository mapping and the cross-repository peer references (per `mermaid-diagrams` portfolio spec), so the entire portfolio's structure is visible at a glance.
- **MUST** record retired capabilities—those belonging to archived repositories per §Portfolio scope—in a single canonical "historical capabilities" appendix of the rendered inventory, listing each capability with its archival date. This appendix is the authoritative destination other specs point at when they need to surface a retired or orphaned item once without re-admitting the archived repository to active scope (for example `portfolio-inflight-management` §Data sources), so historical peer references remain resolvable.

### Decision documentation

- **MUST** carry a non-empty `rationale` field on every capability entry naming why the owner repository was chosen; a one-sentence rationale is acceptable, an empty or template rationale is a `Warning` finding from the audit.
- **SHOULD** record any genuinely contested allocation decision as an Architecture Decision Record under `docs/adr/` in the owner repository, with a backlink from the capability's `rationale` field; this lifts the most important allocation choices into the documentation layer instead of leaving them only in the manifest.
- **MUST** treat re-allocation of a capability from one repository to another as a coordinated atomic operation: the new owner repository declares the capability in its manifest, the old owner repository simultaneously sets `status: deprecated` with `deprecated_in_favor_of` pointing to the new owner, and both changes land within the same coordination window (one closed sprint, OR 90 calendar days, whichever elapses first—mirroring the duplicate-detection backstop). The audit treats half-finished re-allocations as `Critical` findings.

## Acceptance Criteria

- [ ] Every non-archived public repository in the `nolte` GitHub organization either ships a valid `project/portfolio.yml` manifest **or** declares `portfolio: excluded` with a rationale at the top of `CLAUDE.md`.
- [ ] Every `project/portfolio.yml` parses as valid YAML and contains at least one capability entry with the mandatory fields (`name`, `description`, `audience`, `status`, `rationale`).
- [ ] No two `active` capabilities in two different Portfolio-Member repositories share an overlapping `description` beyond the one-closed-sprint tolerance window; running the duplicate-detection check across the portfolio produces zero `Critical` findings.
- [ ] Every `peers:` reference in every manifest resolves to a capability that actually exists in the named Portfolio-Member repository's manifest; running the broken-peer-reference check produces zero `Warning` findings.
- [ ] The skill `portfolio-audit` exists at `skills/portfolio-audit/SKILL.md` in the `nolte-shared` plugin, conforms to `skill-management`, and has been reviewed against `skill-review` at least once with the resulting plan closed.
- [ ] At least one quarterly audit Findings-Report exists under `.audits/portfolio/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to the `review-plan` four-section structure and the canonical severity vocabulary.
- [ ] The aggregated portfolio inventory is published under `docs/<canonical_language>/portfolio/` and renders correctly via `task docs`; a CI check verifies that the rendered output matches what regenerating from the manifests would produce.
- [ ] `continuous-improvement` lists `portfolio-audit` as a recognized audit source in its "Finding sources in scope" section.
- [ ] Every capability in every manifest has a non-empty `rationale` field; running the rationale-presence check produces zero `Warning` findings.
- [ ] The `claude-shared` `docs/<canonical_language>/portfolio/index.md` includes a Mermaid diagram visualizing the capability-to-repository mapping per `mermaid-diagrams`.

## Open Questions

_None at this time._
