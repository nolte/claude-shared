# Research-Plan-Implement Discipline

Status: draft
Portfolio-Scope: portfolio

## Context

Every skill and agent in this monorepo that changes something does the same three things in some order: it builds an understanding of the surface it's about to touch, it decides what to change, and it writes. Today each capability invents that sequence for itself. `issue-orchestrate` decomposes before dispatching, `sprint-execute` transitions state directly, the reviewer agents read without writing, and `spec` interviews before authoring. The shapes are similar, but nothing names them, so nothing can check them. A skill that writes on turn one isn't distinguishable, at authoring or at review time, from one that read first.

The industry converged on a name for the sequence. Anthropic's Claude Code guidance frames it as explore, plan, implement, commit, with a read-only plan mode enforcing the boundary. HumanLayer's context-engineering work names the same three phases and adds the reason they're worth separating: the cost of an error scales with the phase it happens in, because one wrong line of research misdirects a whole plan and one wrong line of plan produces hundreds of wrong lines of code. That asymmetry is what makes the plan, rather than the diff, the cheap place to catch a mistake. `AgentPatterns` catalogues the pattern with a per-task-complexity table and an explicit re-plan gate. LangChain measured the payoff from the other side: concentrating reasoning effort at planning and verification while lowering it during implementation moved a coding harness from 52.8% to 66.5% on Terminal Bench 2.0 without changing the model.

The same body of practice carries a warning that matters as much as the pattern. Field studies of spec-driven development report the failure mode of applying full ceremony to a bug fix: 1,300 lines of generated markdown for a date-display feature, reviewers finding markdown stacks more tedious than the code they replaced, one team measuring specification at 50% of total project time before scaling it back. The evolution of the pattern into QRSPI came from three observed failures of a naive reading: an unscoped research prompt burning roughly 40% of the context window on orientation alone, research summaries too unreliable to justify their cost, and agents silently skipping plan steps without telling the operator. A discipline that only says "always research, always plan" reproduces those failures.

This spec fixes both halves: the phase contract that write-bearing capabilities follow, and the rule that phase depth scales with blast radius so a one-line fix doesn't pay a planning tax. It's the foundation `skill-management`, `agent-management`, and `skill-vs-agent` draw on when they shape a capability's workflow.

**Readers:** skill and agent authors in this plugin monorepo, reviewers running `skill-review` and `agent-review`, and the Claude Code runtime executing those capabilities on an operator's behalf.

## Goals

- Give the three phases stable names and a checkable read-only-versus-write boundary, so a reviewer can tell from a skill's own text which phase each step belongs to.
- Scale phase depth to blast radius, so trivial changes stay cheap and cross-cutting ones stay reviewable.
- Make the plan, not the diff, the surface a human reviews, and make that surface concrete enough to review.
- Keep exploration noise out of the context that implements, without letting the condensed summary become a claim nobody can audit.
- Turn re-planning into an explicit, named transition instead of silent in-flight drift.
- Give `skill-management`, `agent-management`, and `skill-vs-agent` a single spec to cite for workflow shape instead of each restating it.

## Non-Goals

- Deciding **what** to build. Capturing intent is owned by `spec/project/requirements-elicitation/`; this discipline starts once the intent is settled and asks how to execute it.
- Replacing `spec/project/spec-driven-development/`. That spec makes the written specification the authority for a change; this one governs how a capability sequences its work under that authority.
- Replacing `spec/project/elicitation-implementation-separation/`. That spec governs a repository-level working mode in which requirements land as their own pull request; this one governs the phase sequence inside a single work package, whichever mode produced it.
- Governing how many independent sources a repo-external claim needs, which is owned by `spec/claude/research-triangulate/`, or what a claim owes its reader, which is owned by `spec/claude/claim-provenance/`.
- Defining the review **findings** artifact, which is owned by `spec/claude/review-plan/`. A review plan records what a reviewer found; an implementation plan records what an implementer intends. They're different artifacts with different lifecycles.
- Choosing between the skill and agent formats for a capability, which stays with `spec/claude/skill-vs-agent/`.
- Prescribing token counts, context-utilization percentages, or reasoning-effort tiers as normative thresholds. The measurements in §Context are evidence for the shape of the rules, not limits this spec enforces.

## Requirements

### Phase definitions and the write boundary

- The discipline names exactly three phases. **Research** builds and records an understanding of the affected surface. **Plan** converts that understanding into a decided, reviewable change description. **Implement** executes the plan and proves it.
- A capability executing Research or Plan **MUST NOT** write the change itself. Writing the phase's own artifact to the path its governing spec assigns (`.resume/<slug>/` per `spec/claude/resumable-work/`, `.audits/<review-type>/` per `spec/claude/review-plan/`, or a scratch directory) is permitted, **including where that path is tracked**: `spec/claude/review-plan/` requires `.audits/` to stay checked into git and `spec/project/issue-orchestration/` requires its pre-analysis artifact to be committed rather than ignored, and this rule doesn't override either. The boundary is artifact versus change, not tracked versus untracked.
- Research **MUST** produce a **findings artifact** and Plan **MUST** produce a **plan artifact** whenever the phase runs at all. The artifact is either a file or, for a capability that holds no write tools, the structured report it returns to the capability that dispatched it, which then owns persisting it. A phase that produces neither hasn't run; it has been narrated.
- The **write gate** is the capability's first write to tracked state that forms part of the change. Where a Plan phase runs, the gate is the Plan-to-Implement transition; at Tier 0, where no Plan phase runs, the gate is the start of Implement. Every tier has a write gate.

### Phase depth scales with blast radius

- Every write-bearing capability **MUST** classify the work in front of it into one of four tiers, and **MUST** run exactly the phases that tier requires:

  | Tier | Work shape | Phases |
  |---|---|---|
  | 0 | The diff is describable in one sentence, touches one file, and is trivially reversible | Implement |
  | 1 | The root cause or target is already known, the surface is familiar, no published interface changes | Plan, Implement |
  | 2 | Multiple files, an unfamiliar surface, or a new capability | Research, Plan, Implement |
  | 3 | Cross-repository, a migration, or a change to a published contract | Research, Plan, Implement, plus the design gate and the verification pass below |

- When a change matches more than one tier row, the **highest** matching tier wins. A one-line change to a published contract is Tier 3, not Tier 0, because the published-contract row outranks the one-sentence-diff row.
- A capability **MUST NOT** force a higher tier than the work requires. Applying Tier 2 ceremony to a Tier 0 change is a defect of the capability, not diligence: the measured failure mode is markdown volume that reviewers skim and agents ignore.
- A capability **MUST NOT** drop below the tier the work requires **silently**. Classifying down (for example, treating a multi-file change as Tier 1) is permitted only when recorded: the capability **MUST** state the classification and its reason in the artifact the chosen tier produces, or, where the chosen tier produces no artifact, in the pull-request body of the resulting change. An unrecorded downgrade is the defect this rule names.
- At Tier 3 the capability **MUST** additionally: settle the design question (**where** the change is going) as an explicit operator-facing decision before the plan describes **how** it gets there, and run a verification pass against the plan after implementation, performed by a context that didn't produce the change.

### The plan is the review surface

- A plan artifact **MUST** name, for every step: the exact files it touches, the change it makes to each, and the check that proves that step. A plan that describes intent without naming files isn't reviewable against the diff it will produce.
- A plan artifact **MUST** be readable on its own, without the conversation that produced it.
- A plan artifact **MUST** state what falls outside the scope of this change.
- At Tier 2 and Tier 3 an operator approval gate **MUST** sit between Plan and Implement. The capability **MUST NOT** cross the write gate on an unapproved plan.
- At Tier 3 the capability **MUST** decompose the plan into slices that are independently verifiable, so verification happens at slice boundaries rather than only at the end.

### Research is isolated and anchored

- Research **SHOULD** run in an isolated context (a subagent, a dispatched reviewer agent, or a separate session) and return a condensed summary rather than its exploration transcript, so the implementing context doesn't pay for the search.
- A findings artifact **MUST** carry, for every load-bearing claim about the repository, a resolvable anchor: a `file:line`, a path, or a command with the output that settles it. An anchor-free summary is exactly the unauditable-stale-research failure mode the pattern is known to produce, and it converts a research error into a silent plan error.
- A findings artifact **MUST** state the question it was scoped to answer. An unscoped investigation is the documented way a research phase consumes the budget the implementation needed.
- Claims in a findings artifact about anything outside the working copy remain subject to `spec/claude/research-triangulate/`; this spec adds the anchoring obligation, it doesn't relax the source-count obligation.
- A capability that dispatches Research to a specialist and states a suspected cause **MUST** compose the dispatch per `spec/claude/dispatch-brief/`, including the refutation clause.

### Verification belongs inside the plan

- Every plan step **MUST** carry a check that returns a signal the executing capability can read: a test, a build exit code, a linter, a diff against a fixture, or a comparable artifact. A step whose only completion signal is the capability's own judgement that it looks done is an incomplete plan step.
- The Implement phase **MUST** run each step's declared check and **MUST** report the check's actual output, not an assertion that it passed.
- At Tier 3 the verification pass **MUST** be performed by a context that didn't produce the change, and **MUST** be scoped to correctness against the plan's stated requirements rather than to style preference. An unscoped adversarial reviewer reliably returns findings whether or not the work is sound, and acting on all of them produces over-engineering.

### Re-planning is explicit

- When implementation surfaces information that contradicts the plan, the capability **MUST** stop, name the assumption that failed, and return to Plan (or to Research when the failed assumption is a research finding). It **MUST NOT** adapt silently and continue.
- The capability **MUST** distinguish a **local adaptation**, where a step's detail differs but the plan's structure holds and the deviation is recorded in the plan artifact, from a **structural regression**, where a decision the plan rests on is wrong and the phase has to rerun. Only the first may proceed without a new approval at Tier 2 and Tier 3.
- A returned refutation from a dispatched specialist **MUST** be treated as a re-plan trigger, per `spec/claude/dispatch-brief/`.

### Binding on skill and agent authoring

- A skill whose workflow writes to tracked paths **MUST** express that workflow in these phase names, **MUST** state the tier or tier range it targets, and **MUST** name the point at which it crosses the write gate.
- A read-only reviewer or scanner agent is a **Research-phase capability**. Its tool set is governed by `spec/claude/agent-management/` §Tool access, including that spec's narrow read-only `Bash` and network-read exceptions; this spec adds no tool ban of its own. Its output **MUST** satisfy the findings-artifact anchoring rule above.
- A capability that hands work to another capability **MUST** name the phase boundary at which it hands off, so the receiving capability knows which phases it owns.
- A resumable capability **MUST** place its checkpoints per `spec/claude/resumable-work/` at phase boundaries at minimum, because a phase boundary is where an artifact exists that a resumed run can read instead of reconstructing.
- A capability governed by this spec **MUST** cite it, per the citation rule in `spec/project/spec-driven-development/`.
- A domain spec that needs this discipline **MUST** cross-reference this spec rather than restate its rules, and **MAY** add only its scope-specific application (for example, which artifacts its Research phase must read).

## Acceptance Criteria

- [ ] The three phase names, and the read-only-versus-write boundary between Plan and Implement, are defined so a reviewer can classify any step of any skill against them.
- [ ] The tier table is complete enough to classify a given change without further judgement calls about which phases apply, and the "don't force a higher tier" rule is stated as a checkable **MUST NOT**.
- [ ] The plan-artifact contract (files, per-file change, per-step check, out-of-scope statement, standalone readability) is stated as requirements a reviewer can check against an actual plan file.
- [ ] The findings-artifact anchoring rule names the accepted anchor forms (`file:line`, path, command with output) and is stated as a **MUST**.
- [ ] Every requirement that overlaps an existing spec cross-references that spec instead of restating its body: `research-triangulate` for source counts, `claim-provenance` for reader-facing provenance, `dispatch-brief` for refutation, `review-plan` for review findings, `resumable-work` for checkpoints, `spec-driven-development` for the citation rule.
- [ ] `skills/*/SKILL.md` and `agents/*.md` that write to tracked paths can be audited against the §"Binding on skill and agent authoring" rules by reading the artifact alone, without running it.
- [ ] Every external claim in §Context resolves to an entry in §References.

## References

- Anthropic, *Best practices for Claude Code*: <https://code.claude.com/docs/en/best-practices> (explore, plan, implement, commit; the "if you could describe the diff in one sentence, skip the plan" rule; subagents for investigation; the adversarial review step and its over-engineering caveat; verification as the highest-leverage practice).
- Anthropic, *Effective context engineering for AI agents*: <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents> (context as a finite attention budget; context rot; sub-agent architectures returning condensed summaries; compaction and structured note-taking).
- HumanLayer, *Advanced Context Engineering for Coding Agents*: <https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md> (the research, plan, implement phases and their artifacts; the cost-of-error hierarchy across research, plan, and code lines; the 40% to 60% context-utilization target; reviewing roughly 200 lines of plan instead of 2,000 lines of code).
- AgentPatterns, *The Research-Plan-Implement Pattern*: <https://agentpatterns.ai/workflows/research-plan-implement/> (the phases-by-task-complexity table; the re-plan gate; the implement-first anti-pattern; the conditions under which the pattern backfires).
- `betterquestions.ai`, *The Necessary Evolution of Research, Plan, Implement as an Agentic Practice in 2026*: <https://betterquestions.ai/the-necessary-evolution-of-research-plan-implement-as-an-agentic-practice-in-2026/> (the three observed failure modes: unscoped research consuming roughly 40% of the window, unreliable research output, and silently skipped plan steps; the design-versus-structure distinction).
- `matanshavit/qrspi`: <https://github.com/matanshavit/qrspi> (per-phase artifacts, fresh context per phase, independently verifiable vertical slices, and the backward-flow rules distinguishing in-place adaptation from regression).
- LangChain harness engineering on Terminal Bench 2.0, reported at <https://www.zenml.io/llmops-database/harness-engineering-for-agentic-coding-systems> and <https://blockchain.news/news/langchain-terminal-bench-harness-engineering-breakthrough> (the reasoning allocation moving the harness from 52.8% to 66.5% without a model change).
- `O'Reilly Radar`, *The Right Amount of Spec for Agentic Development*: <https://www.oreilly.com/radar/the-right-amount-of-spec-for-agentic-development/> (specification depth by work type; the upfront-cost versus downstream-correction trade-off).
- `ianhxu/agentic-engineering-field-study`, *Spec-Driven Development*: <https://github.com/ianhxu/agentic-engineering-field-study/blob/main/04-spec-driven-development.md> (the over-ceremony evidence: 1,300 lines of markdown for a date-display feature, specification at 50% of project time, the problem-size mismatch, spec drift, and agent non-compliance).

## Open Questions

- Automated enforcement isn't wired. `skill-review` and `agent-review` currently check frontmatter and description budgets; whether they should also assert that a write-bearing skill names its tier and its write gate is deferred. **Revisit trigger:** when a second skill in this monorepo is found crossing the write gate without a plan artifact, or when `skills-agents-sweep` gains any body-content assertion beyond its current checks, making the marginal cost of one more assertion near zero.
- The tier boundaries are stated by work shape rather than by a measurable threshold (file count, diff size). A measurable proxy would make the classification auditable after the fact instead of only at authoring time, but every candidate proxy measured so far classifies the cases that matter wrongly (a one-line change to a published contract is Tier 3). **Revisit trigger:** a recorded case where two reviewers classify the same change into different tiers.
- Whether the Tier 3 design gate deserves its own phase name, as the separate Design phase in QRSPI gives it, is left open. This spec folds it into Plan as an ordering rule (settle where before how) because a fourth phase name would need its own artifact contract to be checkable, and no case in this monorepo has yet demanded one.
