---
title: workflow-health-triage
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# workflow-health-triage

_Triages a failing GitHub Actions workflow run on `develop` or `main` per `spec/project/workflow-health/`. Classifies the failure into one of `defect` / `flake` / `infra` / `stale pin` / `secret drift` / `other`, dispatches the most specialised Claude agent that matches the classification, records the classification plus the dispatched agent's name in the eventual fix PR's Risk / rollout notes, and verifies the standard `fix/`-PR flow. Invoke when the user asks to \"triage this red workflow\", \"classify this CI failure\", or equivalent German-language requests. Don't use to silence checks via `continue-on-error` shortcuts or by removing required-checks entries (forbidden by spec); don't use to bypass branch protection (`enforce_admins` on develop has no exception path); don't use to merge a fix PR (use `pull-request-merge`). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `audit`, `pull-request`
- **Quelle:** [skills/workflow-health-triage/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/workflow-health-triage/SKILL.md)

---

## Workflow Health Triage

Implements `spec/project/workflow-health/` §Triage before remediation and §Specialised-agent dispatch for remediation. The skill is the generalist that classifies a failure and dispatches the hands-on fix to the most specialised available Claude agent; it never performs the fix itself when a matching specialised agent exists.

### Why this is a skill, not an agent

- **Externally-visible mutations gate on user confirmation.** Classification ambiguity, agent-dispatch confirmation, and the fix-PR title / body are mid-flow user dialogues; an agent's fire-and-forget shape would miss them.
- **Orchestrator pattern (per `skill-vs-agent`).** The work itself is *classify, dispatch, verify*; the dispatched specialised agent does the editing. The orchestrator stays in the main thread and chains other skills (`pull-request-create` for the fix PR, optionally `pull-request-merge` after CI is green).
- **Per-classification user gating.** At least three of the six classes (`defect`, `flake`, `secret drift`) need a human "yes that's the right call" before the dispatcher commits to a remediation lane.
- Counter-dimension considered: a narrow agent could handle the classification step in isolation and gain context-window protection, but every downstream lane (PR creation, agent dispatch, verification) is interactive—keeping the whole flow in one skill is simpler than splitting at the classification boundary.

### User-language policy

Detect the user's language and respond in it. All `git`, `gh`, and `Agent(subagent_type=…)` invocations stay English so the audit trail (PR titles, classification labels, agent names) is grep-able portfolio-wide.

### Preconditions

Before any classification:

- Confirm the working directory is a git repository and `gh auth status` reports authenticated.
- Confirm `spec/project/workflow-health/<canonical_language>.md` exists in the current project. If missing, stop and report—without it the classifications are ad-hoc; this skill is the spec's implementer, not its replacement.
- The user supplies the failing workflow run (a `gh run view <id>` URL, a workflow file name like `release-publish.yml`, or "the red one on develop"). If nothing is supplied, run `gh run list --status failure --branch develop --limit 5` and ask which run to triage.

### Operations

#### 1. Inspect the failing run

Run in parallel:

- `gh run view <id> --json name,headBranch,headSha,event,status,conclusion,workflowName,url,jobs`
- `gh api repos/<owner>/<repo>/actions/runs/<id>/jobs --jq '.jobs[] | {name, conclusion, html_url}'`
- `gh run view <id> --log-failed` (capture the failing-step output for classification)
- `git log --oneline -1 <headSha>` (resolve the commit under the run)

Confirm the run is on `develop` or `main` (the spec's scope) and is `conclusion: failure`. If it's still `in_progress`, stop and ask the user to wait for completion before triage; if it's `cancelled`, classify as `other` with a one-line note and stop.

#### 2. Classify before any re-run

Apply the spec's six classes in order; stop at the first match:

| Signal in the failed-step output | Classification |
|---|---|
| Failing step references a file the head commit's diff modified | `defect` |
| Re-run of the same `headSha` would produce green (no infra signal, no code change in the failing step's surface) | `flake` |
| HTTP 5xx, rate-limit, registry-unreachable, GitHub status incident | `infra` |
| `uses:` pin in the workflow points to a `nolte/gh-plumbing` (or other reusable) tag, and a newer tag exists with the relevant fix | `stale pin` |
| Token, deploy key, or OIDC trust expired or rotated; failure references `401`, `403`, `expired`, `unauthorized` | `secret drift` |
| None of the above | `other` (with a short note explaining why) |

Confirm the chosen class with the user before proceeding—at minimum for `defect`, `flake`, and `secret drift`, where misclassification has the highest cost. Apply the classification by writing it to a scratch note that becomes the seed of the fix PR's Risk / rollout notes.

**Hard:** never call `gh run rerun <id>` more than once before a recorded classification exists; repeated blind re-runs are drift per `spec/project/workflow-health/` §Triage before remediation.

#### 3. Dispatch the most specialised available agent

The set of available agents changes over time; never freeze a snapshot of "which agents exist" inside this skill body. Resolve the dispatch target dynamically each invocation:

1. **Resolve the candidate set.** `Glob` `agents/*.md` (plus `~/.claude/agents/*.md` for the project-distributed half), then `Read` the `description:` line of every candidate. Build a (`name`, `description`) table; the table is the runtime inventory.
2. **Match classification to candidate.** Walk the candidates and pick the one whose `description` most closely matches the (classification, failing-artefact-area) pair: a `defect` in a markdown spec/skill/agent file maps to whichever agent's description names "spec-conformant authoring" or the equivalent; a `defect` in a workflow YAML maps to whichever agent's description names "workflow YAML" or "GitHub Actions"; a documentation `defect` maps to whichever agent names an audience-targeted documentation responsibility; and so on. The match is on the description's stated responsibility, not on the agent's name.
3. **Recognise the no-fix classifications.** `flake` and `secret drift` produce no agent dispatch by design — the work is documenting the flake in the project's flake registry (`FLAKES.md` or the `flake`-labelled issue set, whichever the repository uses) for `flake`, or rotating the credential outside Claude for `secret drift`. The skill produces only the fix PR that re-references the rotated credential.
4. **No match is a portfolio gap.** When the candidate walk produces no plausible match and the failure class has occurred three or more times historically (use `gh run list --status failure --branch develop --limit 50` plus a quick grep to estimate), surface this as a portfolio gap per `spec/project/workflow-health/` §Specialised-agent dispatch — the user is asked whether to author a new agent (via `claude-plugin-developer`) before the fix PR opens. When a match exists, dispatch with `Agent(subagent_type="<plugin>:<agent>")` and pass the classification, the run URL, the failing-step excerpt, and the fix-PR-title hint. Wait for the agent's report.

The dynamic-lookup design means a new specialised agent that lands in `agents/` becomes dispatchable immediately, without a coordinated edit to this skill — and a renamed or removed agent stops being a target the next time the skill runs, with no stale snapshot to mislead the dispatch.

### Old patterns

Earlier revisions of this skill enumerated specific agent names inline (for example `workflow-yaml-fixer`, `claude-plugin-developer`, `audience-doc-author`) as the dispatch table. That snapshot rotted whenever a new agent landed or an existing one renamed; the runtime-Glob design above replaces it. The historical mapping is preserved here only so a reader who recognises the prior wording can spot the transition: `defect` in workflow YAML used to fall back to generalist (no matching agent), `defect` in spec / skill / agent files used to dispatch `claude-plugin-developer`, `defect` in documentation used to dispatch `audience-doc-author`. Use the runtime lookup above instead of this snapshot.

#### 4. Verify the fix PR carries the audit trail

Whether the editing was done by a specialised agent or the generalist, the resulting fix PR **MUST** carry both pieces of evidence in its **Risk / rollout notes** section per the `pull-request-workflow` spec:

- Triage classification verbatim (one of the six labels above, with a one-line note for `other`)
- Dispatched agent name (the literal `subagent_type` argument), or the literal phrase "no matching specialised agent—generalist remediation"

If the user wants the skill to open the fix PR itself, dispatch `pull-request-create` with these two lines pre-populated in the Risk / rollout notes; the user still confirms the title and body before push, per the `pull-request-create` spec's externally-visible-action gate.

#### 5. Verify the standard PR gate

After the fix PR opens, the skill stops. The actual merge belongs to `pull-request-merge`, which re-validates the gate. The skill **MUST NOT**:

- merge the fix PR itself (out of scope; `pull-request-merge` owns that)
- pass `--admin` anywhere (`enforce_admins: true` on `develop` has no exception)
- waive a still-failing required check on the fix PR (the spec forbids `continue-on-error` masking and required-check removal)

Report back the run ID, the classification, the dispatched agent name (or "generalist"), the fix-PR URL, and a one-line "next action: invoke `pull-request-merge` after CI is green".

### Examples

- Read `examples/01-defect-classification-dispatch.md` when triaging a failure that classifies as `defect` and dispatches to a specialised agent.
- Read `examples/02-stale-pin-portfolio-gap.md` when the failure root-causes to a stale pin in the portfolio plumbing.
- Read `examples/03-flake-no-fix-record-only.md` when the failure classifies as `flake` and the skill records the classification without opening a fix PR.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/workflow-health-triage/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- **Never** re-run a failed required workflow run more than once before a recorded triage classification exists; the spec calls repeated blind re-runs drift.
- **Never** classify a failure as `flake` without reproducible evidence (re-run of the same `headSha` returned green and no infra signal explains the first failure).
- **Never** mask a failure: don't propose `continue-on-error: true` on a required job, don't propose removing a check from the required-checks set in `.github/settings.yml` without a tracking Issue, don't propose repointing a `nolte/gh-plumbing` pin from a tag to a branch.
- **Never** bypass branch protection on the fix PR; `enforce_admins: true` on `develop` has no exception path.
- **Never** dispatch a specialised agent with a classification the spec doesn't list. The closed set is `defect / flake / infra / stale pin / secret drift / other`.
- **Never** open a fix PR whose Risk / rollout notes don't carry the classification and the dispatched agent name (or the explicit "no matching specialised agent" note).
- **Always** prefer a plugin-distributed specialised agent over the generalist when one matches; the spec's §Specialised-agent dispatch makes this a SHOULD that this skill upgrades to a hard contract for the dispatch step.
- When `spec/project/workflow-health/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.

### Gotchas

Per `spec/claude/skill-management/` §Gotchas—concrete corrections to non-obvious environment facts the executing agent would otherwise get wrong.

- **`GITHUB_TOKEN`-cascade failures aren't `defect`.** A `release-drafter.yml` that doesn't fire after an `automerge.yaml` squash-merge, or a `release-cd-refresh-master.yml` that doesn't fire after `release-publish.yml`, is the documented `infra` class per `spec/project/workflow-health/` §Known platform constraints—and the remediation is upstream in `nolte/gh-plumbing`, not in the consumer repo. Don't open a fix PR against the consumer's workflow YAML; document the `infra` classification and reference the `nolte/gh-plumbing` tracking Issue.
- **`pascalgn/automerge-action` exits 0 on `mergeResult: 'merge_failed'`.** A `automerge.yaml` run with conclusion `success` whose log carries `mergeResult: 'merge_failed'` or `Failed to merge PR:` is a `stale pin` failure (the reusable's `MERGE_METHOD` default doesn't match the repo's allowed strategy in some pre-fix versions). Triage the `automerge.yaml` `uses:` tag, not the workflow YAML itself.
- **Renovate-generated bump PRs for `nolte/gh-plumbing` aren't automerged in this portfolio.** A `stale pin` remediation that proposes to enable Renovate automerge for `nolte/gh-plumbing` violates `workflow-health` §Upstream drift and the AC against it. The remediation is a human-acknowledged Renovate PR, not an automerge rule.
- **`flake` without reproducible evidence is `defect`.** A "let's just re-run and hope" reflex is exactly what the spec forbids. If the same `headSha` doesn't re-run cleanly green and no infra signal explains the first failure, the class is `defect` and the work is a fix, not a tracking entry.

### Multi-model testing

Examples and operations in this skill are verified on Claude Sonnet 4.6 as the default model; spot-checked on Haiku 4.5 for cost-sensitive runs; Opus 4.7 is appropriate for high-stakes audits that require deeper reasoning. The skill body has no model-specific assumptions beyond standard tool-call semantics.
