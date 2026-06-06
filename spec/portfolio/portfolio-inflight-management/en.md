# Portfolio In-Flight Management

Status: draft

## Context

The `nolte/*` portfolio already has specs for the static side of organisational health: `portfolio-management` declares *what capability lives where*, `continuous-improvement` declares *how a finding from an audit becomes a specialist-led fix*, and `workflow-health` declares *how a red CI on a single repository gets triaged back to green*. None of these answers the operational question of **what work is currently in-flight across the portfolio and where it has stalled**. Open issues accumulate without triage, pull requests sit at red checks or unresolved review comments, feature branches drift away from `develop` without ever opening a PR, GitHub Discussions surface user questions that nobody routes—and the only existing detection signal is "a maintainer happened to notice." This spec fills that gap with a periodic, on-demand cross-repository inspection that produces a prioritised specialist-dispatch report.

The *in-flight* perspective is complementary to `portfolio-management`. The latter asks "does this capability have an owner?"; this spec asks "is the work that has already started actually moving?" A capability with a clear owner can still have a stalled PR; a repository with a healthy workflow surface can still have issues that nobody has triaged in months. Both audits run independently and feed the same `continuous-improvement` specialist-dispatch loop.

In-flight findings aren't automatically remediated. The audit produces a prioritised report that names, per finding, which existing skill or agent in the `nolte-shared` plugin should handle it—the operator confirms and dispatches. The audit is read-only across every Portfolio-Member repository; it never opens an issue, never merges a PR, never deletes a branch, never resolves a comment. The boundary mirrors the read-only stance established by `portfolio-management` §Non-Goals, which treats the audit as identification only and leaves the consolidation PR to a human-driven follow-up.

Readers: (1) maintainers of `nolte/*` repositories—who decide which dispatched specialist runs against which finding; (2) the Claude Code skill that runs the periodic in-flight audit—which consumes this spec as its authoring contract; (3) downstream readers of the rendered Findings-Report—including the operator at the next audit run and anyone tracing a specialist dispatch back to its trigger.

## Goals

- Every open issue, pull request, branch-without-active-PR, unresolved review comment, and GitHub Discussion across the `nolte/*` Portfolio-Member set is observable in a single periodic audit, so stalled work can't hide inside a per-repository view.
- Each finding carries a recommended specialist (skill or agent from the `nolte-shared` plugin) and a recommended one-sentence action, so the audit report is dispatch-ready rather than analytical.
- Prioritisation is explicit and traceable: every finding has a severity derived from a documented matrix (security relevance × release blocking × age multiplier × cross-repository blocking), not from operator gut feel at read time.
- The audit is read-only: it never opens a PR, never closes an issue, never deletes a branch, never resolves a review comment, never closes a Discussion. The operator (or a downstream remediation skill) acts on the report.
- The audit integrates with `continuous-improvement` as a recognised finding source, so in-flight triage feeds the same specialist-dispatch loop as drift, workflow-health, and vocabulary findings.
- The audit reuses the Portfolio-Member-set resolution mechanism from `portfolio-management` rather than re-deriving it, so adding or removing a repository from the portfolio automatically expands or shrinks the in-flight inspection.
- Gaps in the specialist roster (a recurring finding class without a matching skill or agent) become visible from the same audit, mirroring how `continuous-improvement` surfaces specialist gaps from existing audit sources.

## Non-Goals

- Defining how individual issues, PRs, branches, review comments, or discussions are worked. `pull-request-workflow`, `branching-model`, `feature-decompose`, `pull-request-merge`, and the various per-repository specs remain authoritative for the remediation side.
- Automatic remediation. The audit reports; the operator dispatches. This spec stays one step shy of fire-and-forget automation, matching the read-only boundary that `portfolio-management` §Non-Goals establishes for the parallel capability audit.
- Per-repository CI failure triage. `workflow-health` remains authoritative for red workflow runs on a single repository. The in-flight audit observes that a PR's required checks are red and recommends `workflow-health-triage`; it doesn't duplicate the per-repo triage mechanics.
- Routing of already-classified findings into specialist work. `continuous-improvement` remains authoritative once a finding exists. This spec is one more upstream finding source feeding that loop, not a competing router.
- Capability allocation, duplicate detection across repositories, or any concern about what code lives where. `portfolio-management` is authoritative for the static portfolio surface.
- Issue-template authoring, PR-template authoring, or any opinion about the content of an issue / PR / discussion. `github-issue-templates`, `pull-request-workflow`, and any future discussion-template spec are authoritative for content shape.
- Synchronous, real-time monitoring—this spec describes a periodic audit (quarterly by default, on-demand always), not a notification stream or a dashboard.
- Governance of who may dispatch which specialist—operator authority is assumed; this spec produces the recommendation, the existing `pull-request-workflow` and `branching-model` specs gate the resulting work.

## Requirements

### Portfolio scope

- **MUST** treat the in-flight portfolio scope as exactly the set of Portfolio-Member repositories defined by `spec/portfolio/portfolio-management/` §Portfolio scope at the moment the audit runs. This spec doesn't redefine portfolio membership.
- **MUST** honour the same opt-out marker (`portfolio: excluded` at the top of `CLAUDE.md`) that `portfolio-management` honours; opted-out repositories don't appear in the in-flight audit.
- **MAY** additionally support a per-data-source opt-out via an inline `inflight: skip-<source>` marker in the repository's `CLAUDE.md` (for example `inflight: skip-discussions`) when a repository legitimately doesn't use a data source. The marker is recorded as an `Info`-grade entry in the report so the omission stays inspectable.
- **MUST NOT** scan repositories outside the resolved Portfolio-Member set, even when the operator explicitly names a `nolte/<other>` repository at invocation. Expanding the scope happens by adopting `portfolio-management`, never by ad-hoc inclusion.

### Data sources

- **MUST**, on every audit run, collect the four primary data sources from each in-scope Portfolio-Member repository:
  - **Open issues**: every issue with `state: open` that has no exclusionary label (`triage-done`, `wontfix`, `parking-lot`).
  - **Open pull requests**: every PR with `state: open`, including drafts.
  - **Branches without an active PR**: every branch on the remote that has no open PR pointing to `develop` and isn't the default branch.
  - **Unresolved review comments and GitHub Discussions**: review threads on open PRs whose `resolved: false`, plus open Discussions with no maintainer reply in the last triage window.
- **MUST** collect via read-only `gh api` calls (or the equivalent `gh issue list`, `gh pr list`, `gh api repos/.../branches`, `gh api graphql` for Discussions). The audit never invokes a mutating GitHub API call.
- **SHOULD** parallelise the per-repository collection where possible to stay within GitHub API rate limits; a fan-out via a read-only agent (analogous to `portfolio-manifest-collector`) is the recommended implementation shape.
- **MUST** persist a per-finding identifier of the form `<repo>/<source>/<id>` (for example `claude-shared/issue/142`, `vale-style/branch/feat-decompound-fix`) so the same finding remains addressable across re-runs and prior findings can be correlated against the previous report.
- **MUST NOT** include private repositories, archived repositories, or forks of upstream projects in the collection. The Portfolio-Member-set resolution from `portfolio-management` already filters these out; the in-flight audit inherits the same filter. NOTE: a genuinely-orphaned open PR in an archived repo is surfaced once via `portfolio-management`'s historical-capabilities path, not by re-admitting the repo to the in-flight scan.
- **MUST NOT** scope the unresolved-review-comment source to threads on closed PRs; the source is limited to review threads on *open* PRs, since a closed PR's threads can no longer block a merge. Legitimate follow-ups left behind on a closed PR are captured as a fresh issue via `feature-decompose`, not by widening this data source.

### Stalling thresholds

- **MUST** apply the following default thresholds when deciding whether an item is *stalled* and thus surfaces in the report:
  - **Issue**: open longer than 30 days with no priority label, no assignee, and no maintainer comment in the last 30 days.
  - **Pull request**: open longer than 7 days with red required checks, OR open longer than 14 days as a draft, OR open longer than 14 days with no reviewer activity, OR carrying conflicts against `develop`.
  - **Branch without active PR**: last push older than 30 days AND no open PR pointing to `develop` AND not the default branch.
  - **Unresolved review comment**: thread older than 7 days without a maintainer reply.
  - **Discussion**: open longer than 30 days without a maintainer reply.
- **MAY** override the default thresholds per repository via a `project/inflight.yml` config file at the repository root; overrides **MUST** be inspectable in the rendered report (the report records both the default and the per-repo override) so the operator sees deviations from the portfolio baseline.
- **MUST NOT** classify an item that hasn't crossed the threshold as a finding. Pre-threshold items are excluded from the report to keep signal-to-noise high; running the audit shortly after a maintainer responded to an issue shouldn't surface that issue.
- **MUST**, for a PR carrying conflicts against `develop`, classify the finding as `Warning` regardless of age—no staleness threshold applies to the conflict driver because an unresolved conflict already blocks merge without further passage of time. Other dimensions of the same PR (age, reviewer activity, red checks) may produce additional findings with their own thresholds.
- **SHOULD** treat the threshold as a lower bound, not an absolute boundary: a `Critical` finding may surface an item that hasn't yet crossed the staleness threshold if another matrix axis (security relevance, release blocking) demands it.

### Classification and prioritisation

- **MUST** classify every finding into one of the four canonical severities from `spec/claude/review-plan/` §Severity scale, derived from a matrix with four axes named verbatim in the rendered report: `security_relevance`, `release_blocking`, `age_multiplier`, `cross_repo_blocking`.
  - `Critical`: security-relevant (CVE in dependencies, supply chain advisory, leaked-credential indicator) OR release-blocking (per the `release_blocking` detection MUST below: PR carries a `release-blocker` label OR its head SHA appears in an open `release-drafter` draft) OR cross-portfolio blocking (per the `cross_repo_blocking` detection MUST below: another Portfolio-Member's roadmap or sprint file references the finding).
  - `Warning`: stalled past 2× the threshold, OR blocking a non-release sprint feature, OR a PR with conflicts against `develop`.
  - `Suggestion`: stalled past 1× but not yet 2× the threshold and not blocking, OR a branch-without-PR older than 30 days, OR an unresolved review comment thread older than 7 days on a non-blocking PR.
  - `Info`: observation worth recording but not action-requiring (per-source opt-out marker, a recently stalled item still inside the noise window, an item closed since the previous audit).
- **MUST** record the matrix-axes input values that produced the classification (for example `security_relevance: false, release_blocking: true, age_multiplier: 3×, cross_repo_blocking: false`) on every finding line, so the operator can re-derive the classification without re-running the audit.
- **MUST** detect `release_blocking: true` for a PR finding when either of these signals is present: (a) the PR carries a `release-blocker` label (case-insensitive), OR (b) the PR head SHA appears in an open `release-drafter` draft on the same repository (detectable via `gh api repos/<repo>/releases?per_page=…` filtered to `draft: true`). Repositories without `release-drafter` configured rely on the label signal alone; other signals (milestone match, branch name pattern) **MAY** be added by the implementing skill but the label and `release-drafter`-draft-membership checks are the canonical baseline.
- **MUST** detect `cross_repo_blocking: true` for a finding when another Portfolio-Member repository's `project/roadmap.md` or any `project/sprints/*.md` references the finding's GitHub identifier via either a short cross-reference (`nolte/<repo>#<number>`) or a full GitHub issue / PR URL (`https://github.com/nolte/<repo>/(issues|pull)/<number>`). The detection is a read-only text scan against the referencing repository's source tree at the audit-run snapshot; no inference, no fuzzy matching.
- **SHOULD** prefer the higher severity when an item matches multiple rows; this matches the canonical severity ordering of `spec/claude/review-plan/`.
- **MUST NOT** invent severities outside the canonical four. `BLOCKER`, `HIGH`, `MEDIUM`, or ALL-CAPS variants are forbidden per `spec/claude/review-plan/` §Severity scale and are themselves a `review-plan` violation if they appear in the Findings-Report.

### Specialist recommendation

- **MUST** attach a recommended specialist (skill or agent identifier from the `nolte-shared` plugin) to every finding whenever a matching specialist exists. Specialist matching follows the existing pattern from `spec/project/continuous-improvement/` §Specialist dispatch.
- **MUST** name the matching skill or agent verbatim by its slug (for example `dependency-audit`, `workflow-health-triage`, `feature-decompose`, `pull-request-merge`, `vocab-drift-audit`), so the operator can dispatch without re-deriving the match from the description.
- **MUST**, when a PR finding's only driver is a red required check, name `workflow-health-triage` as the recommended specialist and **MUST NOT** route the same red-check driver to any other specialist. Other dimensions of the same PR (stale draft, unresolved review comments, conflicts) **MAY** produce additional findings with their own recommended specialists; the red-check exclusivity applies per driver, not per PR.
- **MUST**, when the recommended specialist's action targets a specific open PR, branch, or issue (for example `pull-request-merge`, `pull-request-create`, `workflow-health-triage`), include the slash-command invocation verbatim plus the target identifier in the finding's recommended-action line (for example `/nolte-shared:pull-request-merge against PR #142`), so the operator can dispatch by copy-paste rather than re-deriving the invocation surface from the skill description.
- **MUST**, when no matching specialist exists for a finding, record a `Suggestion`-grade finding that the specialist roster has a gap. Recurring gaps (the same finding class three or more times across the portfolio per `spec/project/continuous-improvement/` §Portfolio gap closure) escalate the recommendation to "author a new specialist." Recurrence is counted by reading the most recent prior `.audits/portfolio-inflight/<YYYY-MM-DD>.md` artefact (when one exists) and matching gap-findings by their `<data-source>/<finding-class-token>` tag where `<finding-class-token>` is the unmatched specialist slug or, when no slug applies, a stable lowercase snake-case label the audit assigns at gap-detection time; in the absence of any prior artefact, recurrence is counted within the current run only.
- **MAY** name a generalist fallback when no specialist exists and the gap hasn't yet reached the 3-recurrence threshold. The generalist fallback is marked explicitly so the audit history surfaces under-served finding classes.
- **MUST NOT** dispatch the specialist itself. The audit emits the recommendation; the operator confirms and dispatches via the normal skill-invocation surface.

### Audit operation

- **MUST** be implemented as a dedicated skill `portfolio-inflight-triage` in the `nolte-shared` plugin (analogous to `portfolio-audit`, `dependency-audit`, `workflow-health-triage`), authored per `spec/claude/skill-management/` and reviewed per `spec/claude/skill-review/`.
- **MUST** be invocable on-demand by the operator and **SHOULD** be run quarterly at minimum. The on-demand trigger and the cadence trigger produce the same artefact shape.
- **MUST** dispatch a read-only specialist agent `portfolio-inflight-collector` for per-repository data-source collection, per the same context-window-protection rationale that `portfolio-audit` applies for manifest collection. The collector returns a pre-reduced structured summary; raw issue / PR / branch / discussion bodies never enter the orchestrating conversation.
- **MUST** reuse the Portfolio-Member-set resolution mechanism from `portfolio-management` (the existing `portfolio-manifest-collector` agent or its generalised successor) rather than re-implementing portfolio scoping.
- **MUST NOT** be implemented as a Claude Agent. The audit is a multi-step orchestration that includes mid-flow user confirmation on stalling-threshold overrides and on specialist-roster-gap escalations; that's the skill side of the `spec/claude/skill-vs-agent/` decision rule.
- **SHOULD**, when invoked on-demand inside a non-`claude-shared` repository, stop and route the user to `claude-shared` for the audit—the Findings-Report write path lives there, mirroring `portfolio-audit`'s detection rule.

### Findings-Report shape

- **MUST** write the audit artefact to `.audits/portfolio-inflight/<YYYY-MM-DD>.md` in the `claude-shared` repository—the same repository hosting `.audits/portfolio/` per `portfolio-management` §Portfolio audit.
- **MUST** conform to the `spec/claude/review-plan/` artefact shape, including the four mandatory sections (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) and the canonical four-stage severity vocabulary (`Critical` / `Warning` / `Suggestion` / `Info`) per `review-plan` §Severity scale.
- **MUST** surface a finding whose underlying item closed since the previous audit as an `Info`-grade "closed since previous audit" entry under `## Findings` (no new section), preserving its original `<repo>/<source>/<id>` identifier. A separate `## Resolved since previous audit` section is forbidden because it would add a fifth top-level section and break the four-mandatory-section conformance to `review-plan` required above.
- **MUST** structure the `## Findings` section first by severity (Critical → Warning → Suggestion → Info) and within each severity by Portfolio-Member repository name (alphabetical). Within a per-repository block, order by data source (issues → PRs → branches → review-comments → discussions) and within a data source by ascending finding identifier.
- **MUST** include, per finding, at minimum: the finding identifier (`<repo>/<source>/<id>`), the data source label, the staleness measure (days open, days since last activity), the recommended specialist (or "no specialist matches" with a roster-gap note), the recommended action as a single sentence, and the severity classification with the matrix-axes input values that produced it. Each finding line carries a bracketed prefix citing the originating spec rule, matching the `portfolio-audit` convention (for example `[portfolio-inflight-management §Classification and prioritisation]`).
- **SHOULD** include an opening `## Summary` table with per-severity counts and per-repository counts, so the operator gets the shape of the portfolio at a glance before reading individual findings.
- **MAY** include a "trend vs previous audit" appendix comparing finding counts against the prior `.audits/portfolio-inflight/<YYYY-MM-DD>.md` entry; the trend appendix is informational only and never affects severity classification.
- **MUST**, when a single (repository × data-source) pair produces more than 10 findings in one run, cap the rendered findings at 10 (highest-severity first, then highest age-multiplier first) and emit exactly one `Info`-grade footer finding of the form "see N additional similar `<source>` findings" that names the omitted identifiers. The omitted identifiers **MUST** be recorded verbatim in the `## Processing log` so no finding is silently lost.
- **MUST NOT** include raw issue / PR / branch / discussion bodies in the Findings-Report. The audit reduces every finding to a structured summary plus the recommended specialist and action; verbatim source bodies stay in GitHub and are reachable via the finding identifier.
- **MUST NOT** write a per-repository sub-report; the audit writes a single aggregate artefact. Per-repository views, if ever needed, are a docs-rendering concern (mirroring `portfolio-management` §Documentation rendering), not additional audit files—the `## Findings` section is already structured by repository within each severity, so a maintainer can find their repo's slice inside the single artefact.

### Integration with continuous-improvement

- **MUST** be listed as a recognised audit source under `spec/project/continuous-improvement/` §"Finding sources in scope" in any future revision of that spec. In-flight findings flow through the same triage-and-specialist-dispatch loop as `spec-drift-audit`, `workflow-health`, and `vocab-drift-audit` findings.
- **MUST** identify each finding with the originating spec citation (for example `[portfolio-inflight-management §Classification and prioritisation]`) in the bracketed prefix of the report line, matching the `portfolio-audit` and `review-plan` conventions.
- **SHOULD** open a tracking issue in the affected Portfolio-Member repository for any `Critical` finding that the operator dispatches against. The tracking issue body cites the audit-finding identifier so the loop is closeable from either side, mirroring `portfolio-management` §Gap analysis.
- **MAY**, on a subsequent audit run, surface a `Critical` finding from the previous audit that remains open as a `Critical`-Persisted entry with the original identifier preserved, so persistence of stalled work across audits is visible without diff-walking the audit history.

### Operator authority

- **MUST NOT** close any GitHub issue, merge any PR, delete any branch, mark any review comment resolved, or close any Discussion. The audit is observational only.
- **MUST NOT** modify any file in any Portfolio-Member repository other than `claude-shared` (where the report itself lives). The audit writes exactly one artefact path: `.audits/portfolio-inflight/<YYYY-MM-DD>.md`.
- **MUST NOT** invoke `gh api` with `-X POST`, `-X PATCH`, or `-X DELETE` against any Portfolio-Member repository. The audit-and-collector path uses read-only API calls exclusively, mirroring the `portfolio-manifest-collector` hard rule.
- **MUST**, when the operator attempts to dispatch a specialist directly from the audit conversation, route the dispatch through the existing skill-invocation surface (the operator types the slash command), not through an in-skill automatic invocation. This preserves the boundary that every cross-repository action lands in the consumer-side conversation rather than mid-audit.

## Acceptance Criteria

- [ ] A canonical spec `spec/portfolio/portfolio-inflight-management/en.md` and its translation `de.md` exist and are structurally synchronised (same headings, same requirement count, same acceptance-criteria checkboxes).
- [ ] The skill `portfolio-inflight-triage` exists at `skills/portfolio-inflight-triage/SKILL.md` in the `nolte-shared` plugin, conforms to `spec/claude/skill-management/`, and has been reviewed against `spec/claude/skill-review/` at least once with the resulting plan closed.
- [ ] The agent `portfolio-inflight-collector` exists at `agents/portfolio-inflight-collector.md`, declares only read-only tools (`Read`, `Bash`, `Glob`, `Grep`), and has been reviewed against `spec/claude/agent-review/` at least once with the resulting plan closed.
- [ ] At least one audit Findings-Report exists under `.audits/portfolio-inflight/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to the `review-plan` four-section structure and the canonical severity vocabulary.
- [ ] Every finding in the report carries: identifier `<repo>/<source>/<id>`, data-source label, staleness measure, recommended specialist (or roster-gap note), one-sentence recommended action, and severity classification with the four matrix-axes input values.
- [ ] The audit evaluates `security_relevance` against at least one of: a dependency-audit CVE indicator, a supply-chain advisory referenced by the repository's lockfile, or a secret-scanning leaked-credential alert; a synthetic security trigger fed into the audit produces a finding carrying `security_relevance: true`.
- [ ] The audit evaluates `cross_repo_blocking` by scanning each Portfolio-Member's `project/roadmap.md` and `project/sprints/*.md` for `nolte/<repo>#<number>` or full GitHub URL references to the finding's identifier; a synthetic cross-reference produces a finding carrying `cross_repo_blocking: true`.
- [ ] `continuous-improvement` lists `portfolio-inflight-management` (or the implementing skill `portfolio-inflight-triage`) as a recognised audit source in its "Finding sources in scope" section.
- [ ] Running the audit against an empty in-flight surface (zero stalled items across the portfolio) produces a valid Findings-Report with zero findings under each severity rather than no report at all.
- [ ] The audit dispatches the `portfolio-inflight-collector` agent for per-repository data collection; the orchestrating skill's conversation never receives raw issue / PR / branch / discussion bodies.
- [ ] The audit never invokes a mutating `gh api` call; a static-analysis sweep of the skill and agent source confirms only read-only commands are present.
- [ ] Stalling-threshold overrides declared in a `project/inflight.yml` file of a Portfolio-Member repository are picked up by the audit and explicitly noted in the rendered report (both default and override values are shown).
- [ ] Every finding line carries a bracketed spec citation (for example `[portfolio-inflight-management §...]`) so a downstream reader can trace it back to the originating requirement.

## Open Questions

_All previously deferred open questions were settled on 2026-06-06: each provisional default is now the standing rule. See `.audits/decisions/2026-06-06-settle-open-questions.md` for the per-item decisions and rationale._
