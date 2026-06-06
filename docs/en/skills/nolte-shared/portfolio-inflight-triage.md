---
title: portfolio-inflight-triage
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# portfolio-inflight-triage

> Runs the read-only periodic in-flight audit across nolte/* (open PRs, branches, issues, review threads) with severity classification.

_Runs the read-only periodic in-flight audit across nolte/* per `spec/portfolio/portfolio-inflight-management/`. Dispatches [`portfolio-inflight-collector`](../../agents/nolte-shared/portfolio-inflight-collector.md) for the four data sources (open issues, open PRs incl. drafts, branches without active PR, unresolved review threads + Discussions), applies spec stalling thresholds with optional `project/inflight.yml` overrides, classifies findings via the four-axis matrix into `Critical`/`Warning`/`Suggestion`/`Info`, attaches a specialist slug per finding, and writes a dated Findings-Report under `.audits/portfolio-inflight/`. Invoke when the user asks to \"audit the portfolio in-flight\", \"run the in-flight triage\", \"check stalled PRs / issues / branches\", or equivalent German-language requests. Don't use to merge / close / delete / resolve anything (operator dispatches), for per-repo CI triage (use [`workflow-health-triage`](workflow-health-triage.md)), or for capability allocation ([`portfolio-audit`](portfolio-audit.md)). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 5 Review (`review`)
- **Tags:** `audit`
- **Source:** [skills/portfolio-inflight-triage/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/portfolio-inflight-triage/SKILL.md)

## Use when

- you want to audit the portfolio's in-flight state across all repos
- you want to find stalled PRs, branches, issues, or review threads
- you want a dated Findings-Report under .audits/portfolio-inflight/

## Don't use when

- **You want per-repo CI triage rather than portfolio in-flight** → [`workflow-health-triage`](workflow-health-triage.md)
- **You want capability allocation rather than in-flight state** → [`portfolio-audit`](portfolio-audit.md)

## See also

- [`portfolio-audit`](portfolio-audit.md)
- [`workflow-health-triage`](workflow-health-triage.md)
- [`portfolio-inflight-collector`](../../agents/nolte-shared/portfolio-inflight-collector.md)

## Referenced by

- [`portfolio-inflight-collector`](../../agents/nolte-shared/portfolio-inflight-collector.md)
- [`portfolio-audit`](portfolio-audit.md)

---

## Portfolio In-Flight Triage

Implements the audit half of `spec/portfolio/portfolio-inflight-management/` as a Claude Code skill in the `nolte-shared` plugin. Single operation: periodic, on-demand cross-repository inspection that surfaces stalled in-flight work (open issues, open PRs, branches without active PR, unresolved review-comment threads, open Discussions) across every nolte Portfolio-Member repository, classifies each finding through the four-axis severity matrix, attaches a recommended specialist (skill or agent slug) per finding, and persists a dispatch-ready Findings-Report under `.audits/portfolio-inflight/<YYYY-MM-DD>.md`.

### Why this is a skill, not an agent

- **Mid-flow user confirmation on threshold overrides and roster-gap escalations.** Two interactive checkpoints are load-bearing: confirming that a Portfolio-Member's `project/inflight.yml` per-repo threshold override should be honoured over the spec default (operator sees default + override side-by-side), and confirming the upgrade of a roster-gap finding to "author a new specialist" when the 3-recurrence threshold from `continuous-improvement §Portfolio gap closure` triggers. An agent's fire-and-forget shape would lose those checkpoints.
- **Persistent on-disk artefact as deliverable.** The audit writes `.audits/portfolio-inflight/<YYYY-MM-DD>.md` in `claude-shared`. Skills own persistent on-disk state; agents return structured reports into the caller's context but don't own write paths.
- **Context-window-protective data collection via agent.** The audit delegates raw per-repository data collection to the [`portfolio-inflight-collector`](../../agents/nolte-shared/portfolio-inflight-collector.md) agent, which fetches the four primary data sources via read-only `gh api` calls and returns a pre-reduced structured per-repository summary. Raw issue / PR / branch / review-comment / discussion bodies never enter the orchestrating conversation, matching the §Findings-Report shape `MUST NOT` clause on raw-body inclusion.
- **Skill-orchestrates-agent-executes is the explicit spec rule.** §Audit operation requires `MUST be implemented as a dedicated skill … MUST NOT be implemented as a Claude Agent` and `MUST dispatch a read-only specialist agent portfolio-inflight-collector for per-repository data-source collection`. The spec pins the hybrid pattern here verbatim; this skill is the orchestrator half.
- **Counter-dimension considered:** a tool-restricted agent could cleanly perform classification and matrix-axis derivation in isolation, given that the data-collection volume is already handled by the collector agent. The decisive counter is the two mid-flow user-confirmation gates and the persistent on-disk write target — both are skill-side per `spec/claude/skill-vs-agent/`.

Follows the same orchestrator pattern as [`portfolio-audit`](portfolio-audit.md) (which dispatches [`portfolio-manifest-collector`](../../agents/nolte-shared/portfolio-manifest-collector.md)).

### User-language policy

Detect the user's language and respond in it. The Findings-Report under `.audits/portfolio-inflight/` follows the conventions of `spec/claude/review-plan/`: section headings (`## Scope`, `## Summary`, `## Findings`, `## Processing log`) stay English so downstream tooling can grep them deterministically; the body may be written in the user's language. Finding identifiers (`<repo>/<source>/<id>`), matrix-axis names (`security_relevance`, `release_blocking`, `age_multiplier`, `cross_repo_blocking`), severities (`Critical` / `Warning` / `Suggestion` / `Info`), and bracketed spec citations (`[portfolio-inflight-management §...]`) stay English verbatim regardless of conversation language.

### Detection: am I in the right repository?

This skill writes its single output artefact (`.audits/portfolio-inflight/<YYYY-MM-DD>.md`) inside the `claude-shared` repository, the same repository that hosts `.audits/portfolio/` for [`portfolio-audit`](portfolio-audit.md). Detection: presence of `.claude-plugin/plugin.json` AND a `spec/portfolio/portfolio-inflight-management/` directory.

When invoked inside any other Portfolio-Member repository (the typical adopter), stop and route the operator to `claude-shared` for the audit — the Findings-Report write path lives there, matching the §Audit operation `SHOULD` and mirroring [`portfolio-audit`](portfolio-audit.md)'s detection rule. Don't try to write the report into the active checkout.

### Operations

#### 1. Run

Runs the cross-repository in-flight audit per `spec/portfolio/portfolio-inflight-management/` §Audit operation. End-to-end produces one Findings-Report under `.audits/portfolio-inflight/<YYYY-MM-DD>.md`.

1. **Detect Portfolio-Member set** per §Portfolio scope `MUST` — reuse the `portfolio-management` resolution. Either dispatch [`portfolio-manifest-collector`](../../agents/nolte-shared/portfolio-manifest-collector.md) (Agent) when the active conversation hasn't already collected the set, or instruct [`portfolio-inflight-collector`](../../agents/nolte-shared/portfolio-inflight-collector.md) to resolve fresh via `gh api orgs/nolte/repos --paginate` (it applies the same `archived: false` / `private: false` / `portfolio: excluded` filters). Record `portfolio: excluded` and per-source `inflight: skip-<source>` markers as `Info`-grade entries so omissions stay inspectable.

2. **Dispatch the collector** — invoke [`portfolio-inflight-collector`](../../agents/nolte-shared/portfolio-inflight-collector.md) (Agent) with the resolved list, all four data sources enabled, and `release-drafter` draft collection enabled (needed for the `release_blocking` matrix axis). Wait for its structured collection report. Per §Findings-Report shape `MUST NOT`, raw issue / PR / branch / review-comment / discussion bodies never enter this conversation — the agent reduces to a structured summary and discards bodies before returning.

3. **Fetch overrides and confirm — gate (one).** For every repository whose collector report carries `inflight.yml override present: yes`, parse the verbatim YAML from `inflight.yml raw content`. Present the spec defaults (Issue 30d, PR 7d/14d/14d/conflict, Branch 30d, Review-comment 7d, Discussion 30d) and the per-repo override side-by-side; ask the operator whether to honour the override for this run. Record the decision in `## Processing log`. Repositories without overrides use the spec defaults silently.

4. **Apply stalling thresholds** per §Stalling thresholds using the per-repository thresholds confirmed in step 3:
   - **Issue**: open longer than `issue.maxAge` (default 30 days), no priority label, no assignee, no maintainer comment in `issue.maxQuietWindow` (default 30 days).
   - **Pull request**: open longer than `pr.maxAgeRedChecks` (default 7d) with red required checks, OR `pr.maxAgeDraft` (default 14d) as draft, OR `pr.maxAgeNoReview` (default 14d) with no reviewer activity, OR `mergeable: CONFLICTING` against `develop` (no threshold for the conflict driver — conflicts block merge regardless of age, per §Stalling thresholds `MUST`).
   - **Branch without active PR**: `daysSinceLastPush > branch.maxAge` (default 30d).
   - **Unresolved review comment**: `daysSinceLastComment > reviewComment.maxAge` (default 7d) with no maintainer reply.
   - **Discussion**: `daysOpen > discussion.maxAge` (default 30d) with `daysSinceLastMaintainerReply == "never"` or beyond the same window.
   Sub-threshold items are excluded per §Stalling thresholds `MUST NOT`. A `Critical` finding may still surface a sub-threshold item when another matrix axis demands it per §Stalling thresholds `SHOULD`.

5. **Derive the four matrix axes** per §Classification and prioritisation for every stalled item. Read `references/matrix-axes-and-report.md` when running this step — it carries the detection MUSTs for all four axes.

6. **Classify into the canonical four severities** (`Critical` / `Warning` / `Suggestion` / `Info`) per §Classification and prioritisation and `spec/claude/review-plan/` §Severity scale. Read `references/matrix-axes-and-report.md` when running this step — it carries the per-severity mapping and the higher-severity tie-break.

7. **Attach a recommended specialist** per §Specialist recommendation to every finding:
   - **Match the catalog.** Read every `description` line under `skills/*/SKILL.md` and `agents/*.md`; name the matching slug verbatim (for example [`dependency-audit`](dependency-audit.md), [`workflow-health-triage`](workflow-health-triage.md), [`feature-decompose`](feature-decompose.md), [`pull-request-merge`](pull-request-merge.md), [`vocab-drift-audit`](vocab-drift-audit.md)).
   - **Red-check exclusivity.** When a PR finding's only driver is a red required check (`requiredChecksState: FAILURE`), name [`workflow-health-triage`](workflow-health-triage.md); **MUST NOT** route the same red-check driver to any other specialist. Other drivers of the same PR (stale draft, unresolved review comments, conflicts) **MAY** produce additional findings with their own specialists; the exclusivity is per-driver, not per-PR.
   - **Slash-command verbatim.** When the recommended action targets a specific PR / branch / issue, include the slash-command invocation verbatim plus the target identifier (for example `/nolte-shared:pull-request-merge against PR #142`). Operator dispatches by copy-paste; the skill never auto-dispatches.
   - **Roster-gap recording.** When no matching specialist exists, record a `Suggestion`-grade finding tagged with a stable lowercase snake-case `<finding-class-token>` (the unmatched specialist slug when one would naturally apply, otherwise a descriptive token like `discussion_no_maintainer_reply`).
   - **Recurrence counting and gate (two).** For every roster-gap finding, `Glob` the prior `.audits/portfolio-inflight/*.md` and `Read` the lexicographically last one. Count occurrences of `<data-source>/<finding-class-token>` across that prior artefact plus the current run. When the count reaches 3 (per `spec/project/continuous-improvement/` §Portfolio gap closure), trigger **User-confirmation gate (two):** ask whether to escalate the recommendation to "author a new specialist `<proposed-slug>`". Record the decision in `## Processing log`. When no prior artefact exists, recurrence is the in-run count only.

8. **Pre-write confirmation — gate (three).** Before any file write, present the per-severity finding counts (`Critical: <n>, Warning: <n>, Suggestion: <n>, Info: <n>`) plus the per-repository counts (top 5 + total). Ask `Write Findings-Report to .audits/portfolio-inflight/<YYYY-MM-DD>.md with these counts? [yes / show-findings / abort]`. On `show-findings`, render the full per-severity list inline and re-ask. On `abort`, stop. On `yes`, proceed.

9. **Write the Findings-Report** at `.audits/portfolio-inflight/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to `spec/claude/review-plan/`. Read `references/matrix-axes-and-report.md` when running this step — it carries the frontmatter, the four required sections, the structure rules, and the per-finding format.

10. **Confirm in the user's language** — the path of the new Findings-Report, the per-severity counts, the count of roster-gap findings (if any), and the next step (open the report and triage `Critical` items first via the recommended slash commands; route roster-gap escalations through [`continuous-improvement-triage`](continuous-improvement-triage.md)).

The Run operation is observational per §Operator authority: it never mutates any Portfolio-Member and writes only `.audits/portfolio-inflight/<YYYY-MM-DD>.md` in `claude-shared` (see Hard rules).

### Reference: spec anchors

This skill implements `spec/portfolio/portfolio-inflight-management/`; read it when in doubt. Sections touched:

- §Portfolio scope, §Data sources, §Stalling thresholds, §Classification and prioritisation, §Specialist recommendation, §Audit operation, §Findings-Report shape, §Integration with continuous-improvement, §Operator authority.

Also touches `spec/claude/review-plan/` (§Severity scale, §Frontmatter, §Plan body structure, §Findings format — the artefact frame) and `spec/project/continuous-improvement/` (§Specialist dispatch, §Portfolio gap closure — the matching pattern and 3-recurrence rule applied in step 7).

When the spec disagrees with this skill, the spec wins. Propose a skill update rather than silently diverging.

### Examples

- Read `examples/01-stalled-pr-with-red-checks.md` when triaging an audit finding for a PR whose only driver is a red required check (the [`workflow-health-triage`](workflow-health-triage.md) exclusivity routing applies).
- Read `examples/02-release-blocker-detection.md` when an open PR carries a `release-blocker` label or its head SHA appears in an open `release-drafter` draft (the `release_blocking` matrix-axis detection MUSTs apply).
- Read `examples/03-roster-gap-3-recurrence.md` when a finding class without a matching specialist crosses the 3-recurrence threshold from the prior audit artefact (the "author a new specialist" escalation user-confirmation gate applies).

### Gotchas

- **The Findings-Report write path lives in `claude-shared`, not in the calling repo.** Writing `.audits/portfolio-inflight/` from a non-`claude-shared` working directory is a structural error; confirm `cwd` resolves to the `claude-shared` checkout (see §Detection) before any write in step 9.
- **`cross_repo_blocking` detection is exact-string only.** The `project/roadmap.md` / `project/sprints/*.md` scan looks for the literal short cross-reference (`nolte/<repo>#<number>`) or the full GitHub URL. Don't infer references from issue titles, branch names, or partial commit SHAs — per §Classification and prioritisation `MUST` the scan is read-only text matching at the audit-run snapshot, no fuzzy matching.
- **`release-drafter`-draft head-SHA membership requires the collector's draft list.** When the collector report is missing the `Open release-drafter drafts` block (the calling skill omitted draft collection, or no drafts exist), only the `release-blocker` label signal applies for `release_blocking` detection — don't try to fetch drafts inline from the skill; the collector owns every `gh api` call per §Audit operation.
- **Threshold-override confirmation happens once per audit, not per-finding.** Step 3 surfaces each repository's `project/inflight.yml` override once; the confirmed thresholds apply to every finding from that repository in step 4. Re-prompting per-finding would be operator-hostile and isn't what the user-confirmation gate is for.
- **Recurrence is counted across prior audit artefacts AND the current run.** The 3-recurrence escalation in step 7 considers the most recent prior `.audits/portfolio-inflight/<YYYY-MM-DD>.md` plus the in-progress run; older artefacts beyond the immediately previous one aren't walked. When no prior artefact exists, recurrence is the in-run count only per §Specialist recommendation `MUST`.
- **`gh api` rate limits scale with N repos × M open PRs.** The collector enforces a headroom precheck (its §Preconditions step 2), but a full run still consumes a non-trivial slice of the hourly budget; check `gh api rate_limit` before back-to-back audits.
- **An empty in-flight surface still produces a Findings-Report.** Per the spec's S-7 acceptance criterion, zero stalled items across the portfolio produces a valid Findings-Report with zero findings under each severity rather than no report at all. Step 9 always writes, never short-circuits on emptiness.

### Hard rules

- Never close any GitHub issue, merge any PR, delete any branch, mark any review comment resolved, or close any Discussion. The audit is observational only per §Operator authority.
- Never invoke `gh api` with `-X POST`, `-X PATCH`, or `-X DELETE` against any repository — including `claude-shared`. The underlying agent enforces this at the harness level; the skill also doesn't issue such calls per §Operator authority.
- Never modify any file in any Portfolio-Member repository other than `claude-shared`. The single write path is `.audits/portfolio-inflight/<YYYY-MM-DD>.md` per §Operator authority.
- Never dispatch the recommended specialist automatically. Emit the slash-command invocation verbatim in the report; the operator dispatches by copy-paste per §Specialist recommendation `MUST NOT` and §Operator authority `MUST`.
- Never use a severity outside the canonical four (`Critical` / `Warning` / `Suggestion` / `Info`). ALL-CAPS variants (`BLOCKER`, `WARNING`, `SUGGESTION`, `INFO`) and additional levels (`HIGH`, `MEDIUM`, `P0`, `P1`) are forbidden per `spec/claude/review-plan/` §Severity scale and §Classification and prioritisation `MUST NOT`.
- Never invent matrix-axis values without the detection signals named in §Classification and prioritisation. `release_blocking` requires the label or the `release-drafter`-draft head-SHA membership; `cross_repo_blocking` requires the exact-string cross-reference scan; `security_relevance` requires a CVE / supply-chain / leaked-credential indicator. No inference, no fuzzy matching, no guesses.
- Never scan repositories outside the resolved Portfolio-Member set, even when the operator names a `nolte/<other>` repository at invocation per §Portfolio scope `MUST NOT`. Scope expansion happens by adopting `portfolio-management`, never by ad-hoc inclusion.
- Never include raw issue / PR / branch / review-comment / discussion bodies in the Findings-Report per §Findings-Report shape `MUST NOT`. The audit reduces every finding to a structured summary plus the recommended specialist and action; verbatim source bodies stay in GitHub and are reachable via the finding identifier.
- Never bypass the three user-confirmation gates: threshold-override honour (step 3), roster-gap 3-recurrence escalation (step 7), and pre-write per-severity-counts confirmation (step 8). The interactive checkpoints are the spec's reason this is a skill rather than an agent; bypassing them undermines `spec/claude/skill-vs-agent/`.
- Never invoke the Skill tool from this skill's body during the data-collection or classification phase — the collector dispatch is an Agent invocation, not a Skill invocation. Calling another skill sequentially (for example [`continuous-improvement-triage`](continuous-improvement-triage.md) to route the report) is allowed and matches the `spec/claude/skill-vs-agent/` hybrid-pattern `SHOULD` on chaining.
- When `spec/portfolio/portfolio-inflight-management/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/portfolio-inflight-triage/<run-id>.yml` after every successful user-approval gate (threshold-override honour in step 3, roster-gap escalation in step 7, pre-write confirmation in step 8) and after each named phase boundary (collector dispatch complete, classification complete). On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, …) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.
