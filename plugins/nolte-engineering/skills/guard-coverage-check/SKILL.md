---
name: guard-coverage-check
description: Answers which rules a project claims, which of them are mechanically enforced, in which lane, and which exist only in prose. Dispatches the read-only `guard-coverage-scanner` agent to inventory the assertions in CLAUDE.md, architecture docs, ADRs, NFRs and specs, then persists a per-rule report under .audits/guard-coverage/ carrying a verdict of enforced, advisory or prose-only plus a drift flag where the text claims enforcement the repository doesn't have. Reads each assertion's own modality first, so a passage that honestly calls its lane advisory is never reported as drift. Invoke to find out which rules are actually enforced, find inert or unwired controls, or audit documentation that asserts more than the code does; also German. Don't use to audit an existing guard's predicate or allowlist (`source-code-review` D11), to audit the required-check set (`quality-gate-enforcer`), or to fix a rule. Supports resume.
tags: [audit]
phase: quality
summary: "Reports, per asserted rule, whether a mechanical guard exists, which lane it runs in, and whether the documentation is honest about it."
summary_de: "Meldet je behaupteter Regel, ob ein mechanischer Guard existiert, in welcher Lane er läuft und ob die Dokumentation darüber ehrlich ist."
use_when:
  - "you want to know which of this project's stated rules are actually enforced"
  - "you suspect a documented control is wired nowhere"
  - "you want the prose-only rules separated from the enforced ones before a security or compliance review"
dont_use_when:
  - situation: "You want an existing guard's predicate, selector, or allowlist audited"
    alternative: source-code-review
  - situation: "You want the required-status-check set audited for tier coverage"
    alternative: quality-gate-enforcer
  - situation: "You want to know whether a given test can fail at all"
    alternative: test-pyramid-check
see_also:
  - guard-coverage-scanner
  - quality-gate-enforcer
  - source-code-review
examples:
  - prompt: "Which of our documented security rules are actually enforced?"
    outcome: "A per-rule table with verdicts and file:line, and the drift cases listed first."
resumable: true
---

# Guard Coverage Check

Answer one question about a repository: **which rules does this project claim, which of them are mechanically enforced, in which lane, and which exist only in prose?**

That question is asked by nothing else in the portfolio. `spec/project/test-falsifiability/` stops at the individual test; this operates one level above it, on the controls a reader would assume are enforced. The expensive instances all have the same shape: a network policy made inert by the rule next to it, a freshness check anchored so it can never alert, a pin assertion excluded by its own path filter, a gate requiring a check that structurally can't report at that point, an authorization dependency documented as enforced and wired nowhere.

Implements `spec/project/defect-class-guards/`, which owns the definitions of *guard* (G1) and *enforced lane* (G2); `spec/project/quality-gate/` §"Enforced lane per tier" owns which lanes are enforced. This skill binds those to a procedure and owns dispatch and persistence; the judgement lives in the dispatched agent.

## Why this is a skill, not an agent

- **Orchestration and persistence.** It dispatches the scanner, writes the report to a path the operator later cites, and hands gaps onward. The `observability-audit` / `observability-audit-scanner` pair in this plugin is the same shape.
- **The scope question is a dialogue.** Which documents count as this project's assertions is a judgement the operator makes, and it differs per repository.
- **Output flows back into the conversation.** The drift list is what the operator acts on, and it belongs in their working context rather than behind an agent boundary.
- Counter-dimension considered: the inventory itself is self-contained and context-heavy, which argues for an agent. That's precisely why the agent exists and this skill only orchestrates.

## German trigger phrases

"Welche Regeln sind wirklich erzwungen", "prüfe die Guard-Abdeckung", "welche Kontrollen existieren nur auf dem Papier", "ist diese Regel irgendwo verdrahtet".

## User-language policy

Detect the user's language and respond in it. The report artifact is written in English, so it stays greppable across the portfolio.

## Inputs

- **Repository root** — defaults to the current working tree.
- **Assertion sources** — defaults to what the scanner discovers: `CLAUDE.md`, `README.md`, the ADR directory, the requirements or NFR directory, and targeted greps through `docs/` and `spec/`. The operator may narrow or widen this before dispatch.
- **Scope** — optionally a subject area (authorization, data handling, CI) so the run answers one question instead of all of them.

## Operations

### `check` (default)

1. **Resolve the sources.** List the assertion-bearing documents you found and present them. Ask before dropping one: a document the operator considers authoritative and you don't is the gap the run exists to close.
2. **Dispatch `guard-coverage-scanner`** with the resolved root and source list. Per `spec/claude/dispatch-brief/`, the brief names the root, the sources, the scope if any, the resolved required status checks when `.github/settings.yml` extends a file outside the repository (the scanner can't read it), and the refutation the run would accept: naming the check that enforces a rule you'd otherwise report as prose-only, with its `path:line` and its lane.
   When `nolte-engineering` isn't installed in the session the agent can't be dispatched. Record that in the report and stop; don't perform the inventory inline at a generalist's level of care and present it as the scanner's.
3. **Persist** the returned report to `.audits/guard-coverage/<YYYY-MM-DD-HHMM>/report.md`, unchanged apart from the front matter the artifact needs. The agent's findings block is the load-bearing part; don't re-summarise it into prose that loses the `path:line` pairs.
4. **Report back**, drift first, then the honest `advisory` and `prose-only` rules as an inventory. State the counts and let the table carry the detail.

### `plan`

Hand the drift findings to `implementation-plan-author` so a specialist gets work packages. Wiring a control is real code work, so there's no mechanical apply: the remediation is a plan someone implements, not a rewrite this skill performs.

## Resolutions the operator chooses from

Each drift finding has exactly three honest outcomes, and the run names which one it proposes:

- **Wire it.** Build the guard so the claim becomes true. Per `defect-class-guards` G3 the guard enumerates the rule's class rather than the sites you happened to check, and per G2 it runs where it can block a merge.
- **Correct the text.** Where the rule isn't worth enforcing, the documentation says what's actually true. This is a real fix, not a retreat: the cost of the defect class is a reader trusting a control that isn't there.
- **Record the half-state deliberately.** Keep both the rule and its unenforced status, in the passage itself, with what would change it. The current `CLAUDE.md` in `nolte/kamerplanter` does this well enough to be the reference: its sections on access control and on security scanning each carry a "what is actually enforced, as of <date>" paragraph, name the advisory lanes as advisory, and give the command that verifies the branch protection.

A half-state nobody wrote down is the expensive option, and it's the one that produced every case in the evidence.

## Gotchas

Per `spec/claude/skill-management/` §Gotchas.

- **An honest "not yet enforced" is not a finding.** The single biggest failure mode of this run is reporting well-maintained documentation as drift. The scanner reads modality before code for exactly this reason; if its report flags a passage that states its own limits correctly, that's a bug in the run, not a finding to relay.
- **A required status check can be declared and still absent.** `.github/settings.yml` may inherit an empty `contexts: []` from the `nolte/gh-plumbing` commons file. A repository can look configured and enforce nothing, so follow the `_extends` pointer rather than reading the local file alone.
- **Grepping for a symbol's definition proves nothing about its use.** The evidence that a dependency is wired is a call site in a router or handler, not the factory that defines it. The `require_permission` case in `nolte/kamerplanter#1042` is exactly this: defined, documented, used by zero routers.
- **A guard can be enforced and still inert.** A path filter that excludes the file the guard asserts about, or an anchor that can never alert, leaves a required check that passes for structural reasons. Note the suspicion in the report and route it onward; proving it belongs to the guard's own review.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/guard-coverage-check/<run-id>.yml` after the source-resolution gate and after each phase boundary (resolve, dispatch, persist). On re-invocation, scan that directory for `status: in_progress` files whose `inputs:` snapshot matches; if one matches, prompt `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The envelope and the fail-closed semantics on schema or YAML errors live in the spec; they aren't duplicated here.

## Hard rules

- **Never** report drift on a passage whose own words say the rule isn't enforced yet and are right. Honest documentation of a half-state is the behaviour this skill exists to reward.
- **Never** report a rule as prose-only without the search that came back empty, carried in the report so a reader can repeat it.
- **Never** fix a rule or wire a guard in this run. The skill reports; remediation is a plan or an issue.
- **Never** present an inline inventory as the scanner's output when the agent wasn't available. Record the gap, per `spec/project/issue-orchestration/` §"Verification and traceability" on unavailable sibling-plugin targets.
- **Never** treat a green required check as proof its rule is enforced when the check's own trigger excludes the file the rule is about; say what you suspect and route it.
- When `spec/project/defect-class-guards/` and this skill disagree, the spec wins and this skill needs the update.
