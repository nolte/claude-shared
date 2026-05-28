---
name: continuous-improvement-triage
description: "Operationalises spec/project/continuous-improvement/ by triaging portfolio audit findings, classifying them against the available specialist catalog, and dispatching hands-on remediation to the most specialised available Claude agent or skill. Invoke when the user asks to \"triage continuous-improvement findings\", \"classify a portfolio-improvement opportunity\", \"dispatch findings to specialised agents\", \"run the quarterly specialist-coverage review\", \"check whether a finding class needs a new specialist\", or equivalent German-language requests. Drives the three-operation loop: audit (periodic specialist-coverage review), update (record decisions and dispatch specialists), close (terminate the triage cycle). Applies the three-recurrence gap-closure rule and records all dispatch decisions in fix-PR Risk / rollout notes. Do not use to perform the hands-on remediation itself—that belongs to the dispatched specialist. Supports resume on re-invocation per `spec/claude/resumable-work/`."
tags: [triage, audit]
phase: review
summary: "Triages portfolio audit findings and dispatches hands-on remediation to the most specialised available agent or skill."
summary_de: "Triagiert Portfolio-Audit-Findings und dispatched die Behebung an den passendsten spezialisierten Agent oder Skill."
use_when:
  - "you want to triage continuous-improvement findings across the portfolio"
  - "you want to classify a portfolio-improvement opportunity against the specialist catalog"
  - "you want to run the quarterly specialist-coverage review"
  - "you want to check whether a finding class needs a new specialist"
resumable: true
---

# Continuous Improvement Triage

Implements `spec/project/continuous-improvement/` §Specialist dispatch, §Portfolio gap closure, and §Continuous loop and quarterly coverage review. The skill is the generalist orchestrator that classifies findings, dispatches the hands-on work to the most specialised available Claude agent or skill, and verifies that every fix PR carries the required audit trail. It never performs the specialist remediation itself when a matching specialist exists.

## Why this is a skill, not an agent

- **User confirmation gates every dispatch decision.** Finding classification, specialist-match confirmation, and gap-closure decisions all require mid-flow dialogue; an agent's fire-and-forget shape misses them.
- **Orchestrator pattern (per `skill-vs-agent`).** The work is *classify, dispatch, verify*—not edit. The dispatched specialist does the mutating work; this skill stays in the main thread and chains other skills (`pull-request-create`, optionally `pull-request-merge`).
- **Quarterly cadence requires standing-session instructions.** The specialist-coverage review surfaces decisions that accumulate across multiple prompts; a skill's persistent instruction context fits this naturally.
- Counter-dimension considered: a narrow agent could handle the classification step in isolation and gain context-window protection, but every downstream lane (dispatch, gap-closure decision, PR annotation) is interactive—keeping the whole flow in one skill is simpler than splitting at the classification boundary.

## German trigger phrases

- „CI-Findings triagen"
- „Quarterly Specialist-Coverage Review durchführen"
- „Findings an Spezialisten dispatchen"
- „Portfolio-Verbesserungsopportunität klassifizieren"
- „Dreifach-Wiederholung prüfen, ob ein neuer Spezialist gebraucht wird"
- „Triage-Zyklus abschließen"

## Preconditions

Before any operation:

- Confirm the working directory is a git repository and `gh auth status` reports authenticated.
- Confirm `spec/project/continuous-improvement/en.md` exists in the current project. If missing, stop and report—without it the classifications are ad-hoc; this skill is the spec's implementer, not its replacement.
- Read `templates/triage.template.md` to understand the triage artifact format before creating or updating a triage file.

A triage artifact must exist for `update` and `close`; if none exists, start with `audit` first.

## Operations

### 1. audit

Perform the periodic specialist-coverage review mandated by the spec (at minimum once per calendar quarter).

1. **Locate merged remediation PRs.** Run `gh pr list --state merged --limit 50 --json number,title,body,labels` and filter for PRs whose body contains a **Risk / rollout notes** section that references an in-scope finding source (`spec-drift-audit`, `workflow-health`, `project-structure-apply`, `vocab-drift-audit`, `prose-style`, manual review Issue, or ad-hoc contributor observation).

2. **Extract dispatch signals.** For each matched PR, parse the **Risk / rollout notes** section for:
   - The named specialist (or the literal phrase "no matching specialised agent—generalist remediation").
   - The originating finding source.
   - If neither appears, flag the PR as **missing audit trail**—this is itself a finding under the spec.

3. **Identify generalist-handled finding classes.** Group the PRs by finding class (derived from the finding source and the nature of the fix). For each class, count how many times it was handled by a generalist (no specialist named). Classes at three or more generalist-handled occurrences trigger the gap-closure rule.

4. **Resolve the current specialist catalog.** `Glob` `agents/*.md` (plus `~/.claude/agents/*.md`), `Read` the `description:` line of every candidate, and build a `(name, description)` table. This is the runtime inventory—not a hard-coded snapshot.

5. **Match finding classes to specialists.** For each generalist-handled finding class, walk the candidates and check whether any specialist's description now covers it. If a match exists but wasn't used historically, record that as a routing correction opportunity. If no match exists and the class has reached the three-recurrence threshold, record a **gap-closure action required** finding.

6. **Initialise the triage artifact.** Instantiate `templates/triage.template.md` with `triage-type: continuous-improvement`, today's date, the repository name, `scope: portfolio`, and `status: open`. Populate `## Findings` with the structured list from steps 2–5 and `## Processing log` with an `audit` entry. Propose the artifact filename as `.audits/continuous-improvement/<YYYY-QN>.md` (for example `.audits/continuous-improvement/2026-Q2.md`) and confirm with the user before writing.

7. **Fold or separate coverage review.** Per the spec, the quarterly specialist-coverage review SHOULD be folded into the `spec-drift-audit` artifact under a `## Specialist coverage review` heading. Ask the user whether to fold or keep standalone; default to folding when a `spec-drift-audit` artifact for the same quarter already exists.

### 2. update

Record decisions on open findings and dispatch specialists.

1. **Confirm a triage artifact is open.** Read the current `.audits/continuous-improvement/` directory to locate the most recent `status: open` artifact. If none exists, redirect to `audit`.

2. **For each unresolved finding in `## Findings`**, present the finding, the current specialist match (from the runtime catalog), and the three decision options:
   - **Dispatch specialist**: select the named specialist and record its `subagent_type` in the finding.
   - **Defer with reason**: record an explicit deferral note (reason + owner + target quarter).
   - **Initiate gap-closure**: if no matching specialist exists and the recurrence threshold is met, dispatch `Agent(subagent_type="nolte-shared:claude-plugin-developer")` to author a new specialist or extend an existing one's `description`.

3. **Dispatch hands-on remediation.** For each finding with a dispatch decision, call `Agent(subagent_type="<plugin>:<agent>")` with the finding class, the finding source reference, and a fix-PR-title hint. Wait for the agent's report. Never perform the specialist remediation inline.

4. **Record every dispatch.** For each dispatched specialist, the eventual fix PR **MUST** include in its **Risk / rollout notes**:
   - The originating finding source (by name and, where available, link).
   - The dispatched specialist (`subagent_type` argument literal), or the phrase "no matching specialised agent—generalist remediation".
   Append these two lines to a `## Decisions` entry in the triage artifact immediately after dispatch.

5. **Gap-closure authoring.** When a new specialist is authored via `claude-plugin-developer`, record the decision in `## Decisions` with the gap-closure justification (three-recurrence threshold, or explicit high-impact rationale for pre-threshold creation). The fix PR for the new specialist itself MUST carry the high-impact justification if created before the threshold.

6. **Cross-repository promotion check.** If the same finding class has been observed in two or more repositories, remind the user that the spec requires plugin distribution for any specialist created in response; do not close the gap-closure decision until the `distribution: plugin` requirement is confirmed.

### 3. close

Terminate the triage cycle after all decisions are recorded.

1. **Verify completeness.** Confirm every finding in `## Findings` carries a decision: dispatched / deferred-with-reason / gap-closure-initiated. Findings with no decision block closing; prompt the user for each.

2. **Verify fix PRs carry the audit trail.** For each dispatched finding, run `gh pr view <number> --json body` and confirm the **Risk / rollout notes** section contains the required two lines. If any are missing, block closing and prompt the user to amend the PR before proceeding.

3. **Flip status to closed.** Update the triage artifact's frontmatter: set `status: closed`, append a `closed` entry to `## Processing log` with the date and a one-line summary (number of findings, dispatched / deferred / gap-closure counts).

4. **Report back.** Return: triage artifact path, finding counts by disposition, any outstanding gap-closure PRs, and the next-review date (today + 90 days, rounded to the nearest calendar quarter boundary).

## Examples

- Read `examples/01-quarterly-specialist-coverage-review.md` when performing the full quarterly audit and dispatching findings to specialised agents.
- Read `examples/02-three-recurrence-finding.md` when a finding class has hit the three-recurrence threshold and requires gap-closure action.
- Read `examples/03-cycle-close.md` when closing a completed triage cycle after all decisions are recorded.

## Gotchas

- **Partial `spec-drift-audit` runs do NOT suppress the quarterly coverage review.** The spec explicitly states that partial-audit narrowing applies to drift, not to coverage. If a narrowed drift audit has already happened this quarter without a coverage section, the quarterly review is still due—and the omission is itself a finding for the next audit cycle.
- **Sprint-review closure is not a substitute.** A successfully closed sprint does not satisfy the quarterly specialist-coverage review. Both cadences are independently mandatory per the spec's §Relationship to existing specs.
- **Three-recurrence count is per finding *class*, not per repository.** Count generalist-handled occurrences across the whole portfolio. Two recurrences in one repo plus one in another equals three—the threshold is met and plugin distribution is required for any new specialist.
- **Missing audit trail is a finding.** A merged remediation PR that lacks the required **Risk / rollout notes** fields is not merely a documentation gap; the spec defines it as an in-scope finding to be recorded and remediated in the next cycle.
- **Pre-threshold early creation requires an explicit justification.** A specialist created before the three-recurrence threshold is valid only when the authoring PR records a high-impact justification (security, release-blocker, or correctness regression). An early-creation without that note is a spec violation—not a saved effort.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/continuous-improvement-triage/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- **Never** perform specialist remediation inline when a matching specialist exists; classify, dispatch, verify.
- **Never** record a gap-closure decision as "no action needed" when the three-recurrence threshold is met; the spec's MUST applies.
- **Never** close a triage cycle while any finding is still undecided; every finding must carry dispatched / deferred-with-reason / gap-closure-initiated.
- **Never** let a fix PR merge without the two required **Risk / rollout notes** fields (originating source + specialist name or explicit generalist note).
- **Never** collapse multiple unrelated findings into a single remediation PR; one PR per finding class (same-class grouping is allowed when the fix is genuinely atomic).
- **Never** use this skill to weaken another spec—a finding whose remediation would require violating another spec is an Open Question, not a shortcut.
- **Always** prefer a plugin-distributed specialist over a project-local one when the finding class has been observed in two or more repositories.
- When `spec/project/continuous-improvement/` and this skill disagree, the spec wins.

## Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the default model; spot-checked on Haiku 4.5 for cost-sensitive quarterly runs; Opus 4.7 is appropriate for high-stakes audits involving security or release-blocker findings that require deeper reasoning. The skill body has no model-specific assumptions beyond standard tool-call semantics.
