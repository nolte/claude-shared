# Claim Provenance

Status: draft
Portfolio-Scope: portfolio

## Context

An agent that writes "X happens because Y" into an issue hasn't recorded an opinion; it has published a premise. The next reader inherits the sentence as established and builds on it. Nothing in the corpus asks how it was established, so a claim that took one `grep` to refute travels exactly as far as one that was proven.

Three claims published in a single session in `nolte/kamerplanter` make the cost concrete. Each was confidently worded, each was consistent with the symptom it explained, each was wrong, and each was refutable in under five minutes. `PlantCountStep is unreachable UI` went into issue #1207 as a suggested defect; the component is superseded rather than broken, its value is still computed and submitted, and whoever picked the issue up would have hunted a wiring defect that doesn't exist. `The delete case skips because the new row is off the first page` was the working diagnosis before a fix; with 18 seeded records and a page size of 50, the new row sorts to position 8 of 19, so pagination can't be involved. `The harness already has a working version of this helper` framed a fix in a commit message; the second copy has no caller and the helper had never worked in either. Two of the three cost nothing because the next step happened to expose them. The first sat for a day as work that didn't exist.

The pattern isn't carelessness. Each claim was plausible and each was cheap to check. What was missing was the step of trying to refute it *before* writing it down.

Evidence and currency: the three observations above are recorded in `nolte/claude-shared#545` (2026-08-16) and are taken as given here rather than re-derived. This spec asserts nothing about anything outside the working copy, so it carries no external sources.

Boundaries: `spec/claude/dispatch-brief/` owns the delegated case, where an orchestrator hands a hypothesis to a specialist and must authorise its refutation. `spec/claude/research-triangulate/` owns assertions about things *not* verifiable in the working copy and excludes repo-internal ones by design, which is the gap this spec fills. `spec/project/e2e-failure-diagnosis/` §A owns the mechanism bar that gates a *remediation* for a red end-to-end cluster, and applies this spec rather than restating it. `spec/project/test-falsifiability/` owns the property for test code. §Delimitation states each boundary precisely.

Readers: every agent and skill that writes a claim into an artefact somebody else will read; the reviewers and analyzers whose findings *are* claims; anyone reviewing such an artefact.

## Goals

- Make the provenance of a load-bearing claim a **routine, checkable property** of the artefact carrying it, rather than a habit the author has to remember.
- Cover the **self-directed** case, where analyst and actor are the same agent, no brief is written, and nothing authorises refutation.
- Keep the required output **small enough to survive routine work**, so the rule isn't quietly dropped the way a noisy check is.
- Give the rule a **stable, citable home** that domain specs and publishing skills point at instead of restating.

## Non-Goals

- Whatever is *done* about a cause once it's established. The remediation gate for an end-to-end cluster belongs to `spec/project/e2e-failure-diagnosis/` §A, and changing code under a proven cause belongs to the test-cycle specs.
- Falsifiability of test code, its taxonomy, and its detection routes; owned by `spec/project/test-falsifiability/`.
- Sourcing and triangulating assertions about repo-external facts; owned by `spec/claude/research-triangulate/`.
- The refutation clause a dispatching orchestrator owes a specialist; owned by `spec/claude/dispatch-brief/`.
- Claims made in live conversation with the operator, where a correction is one reply away.
- Implementing a linter or scanner. §C deliberately checks substance rather than a token, so there's nothing deterministic to grep; tooling is separate work if a machine-read carrier ever gains a field.

## Requirements

### A. What the rule binds

- A **load-bearing claim** is a statement that's both **checkable against the working copy** and **something another actor's work would build upon**. Four shapes qualify and the rule doesn't distinguish between them: a *cause* ("the test fails because the row sorts to page two"), a *state* ("this component is unreachable"), an *existence* ("the harness already has this helper"), and an *absence* ("no caller remains"). The issue behind this spec named causes, but two of its three measured failures were a state claim and an existence claim.
- The rule **MUST** bind every artefact that **outlives the session** and can be read as a premise: an issue body or comment, a commit message, a pull-request description, a review finding, a plan file, an audit report, spec prose, a feature or sprint file. This list is illustrative; the test is whether the carrier survives the session, not whether it appears here.
- The rule **MUST NOT** bind a judgement ("this is hard to read"), a proposal ("we should extract this"), or a question. None is a checkable statement about the working copy.
- The rule **MUST NOT** bind an assertion about something not verifiable in the working copy—a published version, a third-party API signature, a sister-repo path. Those are owned by `spec/claude/research-triangulate/`, whose source-count discipline is the external twin of this one.
- The rule **MUST NOT** bind live conversation with the operator. The cost this spec addresses is a wrong premise that travels; in conversation the correction is one reply away.

### B. What the artefact must carry

- An artefact carrying a load-bearing claim **MUST** present that claim as exactly one of **established** or **unestablished**. Carrying neither is the defect this spec exists to name.
- A claim presented as **established MUST** name the observation that established it: a command together with the output that settles it, or a `file:line` a reader can open. An unanchored assertion doesn't become established by being stated confidently, and all three of the failures in §Context were confidently stated.
- A claim presented as **unestablished MUST** name the observation that *would* settle it, and **MUST** state that the observation wasn't made. Publishing "I think X, unverified, and here's what would decide it" is fully conformant and is often the right answer; publishing "X" when X is a guess isn't.
- A claim that repeats an already-established claim from another artefact **MAY** discharge the requirement by citing that artefact. The citation is the anchor; a second measurement isn't required.
- Recording a claim as unestablished **MUST NOT** be treated as a weaker contribution than establishing it. An honestly marked hypothesis survives intact until it becomes measurable, which is the outcome this rule is for.

### C. Establishing the claim, and the cost of not doing so

- When the observation named under §B is **cheap with the means already at hand**, the author **MUST** make it rather than publish the claim as unestablished. Every failure in §Context was measurable in under five minutes, so a rule that let them through as honestly-labelled guesses would have relabelled the problem instead of fixing it.
- **Unestablished** is available only when the observation isn't cheap, and the artefact **MUST** then say what makes it expensive—it needs a full suite run, production data, an operator decision, access the author doesn't have.
- The **cheapness judgement stays with the author**; this spec fixes no threshold, because any fixed threshold is wrong in the next context. What the rule requires is that the judgement be *written down*, which turns the exit from free into reviewable: a reader who thinks the observation was cheap can now say so against a stated claim.
- The obligation is to **attempt refutation, not to accumulate proof**. One observation that could have contradicted the claim, actually made, discharges §B and §C together. Demanding more would make every claim expensive and get the rule ignored—the fate `spec/project/test-falsifiability/` already predicts for a noisy check.

### D. Form, and how a reviewer checks it

- The distinction **MUST** be checked on **substance, not on wording**. This spec prescribes no verbatim token, because its carriers include commit messages and prose written in either configured language. The canonical English forms are: *established—`<command>` shows `<result>`* and *unestablished; `<observation>` would settle it, not measured because `<cost>`*.
- A reviewer checks an artefact against this spec with one question: **can I tell, from the artefact alone, whether the author measured or guessed?** If not, the artefact isn't conformant. Where a claim is marked established, the second question is whether the named anchor actually resolves.
- A carrier that already has a machine-readable finding format **MAY** express the distinction as a field rather than as prose, provided the field is defined by the spec owning that format. This spec doesn't define such a field and doesn't require one.
- A domain or scope-specific spec that needs this rule **MUST** cross-reference this spec rather than restate its body, and **MAY** add only its scope-specific application.

### Delimitation

This spec is bounded against its neighbours and **MUST NOT** restate their rules:

- `spec/claude/dispatch-brief/` owns the **delegated** half: a brief that carries a hypothesis must authorise the receiving specialist to refute it, and defines what a valid refutation contains. That rule needs two parties. This spec owns the case where analyst and author are the same agent, so no brief exists and nothing authorises anything. A dispatch brief is also an artefact under §A, so both apply to it; they don't overlap, because one governs what the brief owes the specialist and the other what the brief owes its reader.
- `spec/claude/research-triangulate/` owns **repo-external** assertions and their source-count discipline, and states that repo-internal assertions aren't triangulated because they're verified by reading the working copy directly. This spec is what makes that verification an obligation rather than an assumption. The two are complementary and share no requirement.
- `spec/project/e2e-failure-diagnosis/` §A owns the **mechanism bar** for an end-to-end failure cluster: the three admissible proof forms, and the sufficient-and-necessary standard that gates a remediation. It's reached from a red run and it gates a change. This spec gates the *assertion* and is reached from any artefact. §A applies this spec; neither restates the other, and §A's proof forms stay there. The two bars are deliberately different heights and a reader shouldn't conflate them: **established** here means one refuting observation was attempted and didn't refute, which is enough to write a cause down honestly, while §A's mechanism bar demands sufficiency and necessity before that cause may drive a change.
- `spec/project/test-falsifiability/` owns the property for **test code**—a test that can't fail. This spec governs prose claims. The two are siblings in reasoning, not in scope: both name an assertion that's trusted because it was never asked to fail.
- `spec/claude/review-plan/` owns the **finding format**, including the requirement that a finding cite the spec requirement it rests on. That citation names the rule that was broken; this spec governs the evidence for the cause the finding names. A finding satisfies one and fails the other whenever it cites a rule but guesses at a cause.

### Binding into agents and skills

- An agent whose findings state a cause **MUST** carry the distinction **in the finding itself**, not in a covering note, so it survives extraction into a tracking artefact. This binds the reviewer and analyzer agents that emit causal language.
- A skill that composes a durable artefact **MUST** apply §B when the artefact it writes carries a load-bearing claim. This binds the skills that publish issues, pull-request bodies, plans, features, specs, and audit reports.
- A binding **MUST** live in the artefact body, never in its `description:` frontmatter, so the portfolio's routing budget doesn't regress.

## Acceptance Criteria

- [ ] A reviewer can decide whether a given sentence is in scope, from §A alone: checkable against the working copy, load-bearing for another actor, and carried by an artefact that outlives the session
- [ ] The four qualifying claim shapes (cause, state, existence, absence) are named, and the excluded classes (judgement, proposal, repo-external, live conversation) are named with their owners
- [ ] Exactly two markers are required, each with its own stated obligation, and both obligations are checkable against an actual artefact
- [ ] The measure-when-cheap duty is stated as a `MUST`, with the cost claim itself required in the artefact when the exit is taken
- [ ] The cheapness threshold is explicitly left to the author, with the reason recorded
- [ ] The rule is checked on substance rather than a verbatim token, and a canonical form is offered without being mandated
- [ ] A reviewer's check is stated as a single question answerable from the artefact alone
- [ ] §Delimitation names all five neighbours and restates none of their rules
- [ ] Repeating an already-established claim can be discharged by citing the artefact that established it, and marking a claim unestablished is stated not to be the weaker contribution
- [ ] A spec that needs this rule is required to cross-reference it rather than restate it, and the neighbours wired at authoring time do exactly that
- [ ] Both binding obligations are testable against an artefact: an agent carries the distinction inside the finding, and a skill applies §B to the durable artefact it writes
- [ ] The binding rule forbids `description:` growth, so adopting this spec can't regress the routing budget

## References

- `spec/claude/dispatch-brief/`: the delegated half of the same discipline, which this spec's §Delimitation bounds against
- `spec/claude/research-triangulate/`: the external-assertion twin, whose exclusion of repo-internal assertions this spec owns
- `spec/claude/review-plan/`: the finding format whose spec-citation requirement is orthogonal to this one
- `spec/project/e2e-failure-diagnosis/`: §A, the end-to-end mechanism bar that applies this spec
- `spec/project/test-falsifiability/`: the test-code sibling, and the source of the noisy-check argument in §C
- Source work order and evidence: `nolte/claude-shared#545`, whose three measured false claims are the entire empirical basis; the sibling gap about test doubles is `nolte/claude-shared#542`

## Open Questions

- **Whether a machine-read carrier should gain a provenance field.** §D permits it and defines none. `spec/claude/review-plan/` findings and the editorial scanner output are the two carriers that already have a machine format, and a field there would make the rule greppable in exactly the place findings are produced. *Revisit* if reviewing agents adopt §"Binding into agents and skills" and the prose form proves too weak to extract reliably.
- **Whether existing artefacts should be swept.** This spec binds artefacts written from adoption onward. The repository and the wider portfolio carry unmarked claims from before it, and no retrofit is required here. *Revisit* only with a bounded scope; an unbounded sweep over historical issues and commit messages would cost more than the claims are worth.
- **Whether the cheapness judgement stays author-owned.** §C fixes no threshold deliberately, accepting that an author who systematically overstates cost can still take the unestablished exit. The mitigation is that the cost claim is now written down and disputable. *Revisit* if reviews start finding overstated cost claims rather than unmarked ones.
