# Defect-Class Guards

Status: draft
Portfolio-Scope: portfolio

## Context

`spec/project/test-falsifiability/` covers tests that can't fail. This spec covers the other half of the same epistemic problem: what a **closed** defect leaves behind so its class can't come back.

The evidence is a review of 325 closed issues in `nolte/kamerplanter`. Twenty-three of them name a predecessor in their own title. Issue `#719` is titled as the same IDOR as `#717`, `#948` as the write-side twin of `#927`, `#1018` as the same shape as `#997`, `#952` as the cross-tenant reads that survive `#947`. The chains run four and five links long. The median issue lifetime in that repository is under a day, so throughput isn't what produced them. Each fix repaired the sites it had found, and the next report was the same defect at a site nobody had looked at.

That repository also has the cure, undocumented. It runs a set of `scripts/check_*.py` guards and pre-commit hooks, each named after the issue whose class it locks in: `boundary-validation` (`#970`), `utc-calendar-day` (`#858`), `tenant-body-field` (`#1000`), `workflow-gate-integrity` (`#1313`). The practice works and exists nowhere as a rule, so no other repository inherits it and the repository that invented it applies it unevenly. `nolte/pre-commit-hooks` ships two generic hooks and doesn't know the method.

The rules below are each earned from a specific failure in that corpus rather than derived from principle. This spec declares the identifier space G1–G6, following the D1–D10 and T1–Tn precedent in `spec/project/source-code-review/` and `spec/project/test-falsifiability/`.

Readers: whoever closes a defect and authors its pull request, and reviewers applying `source-code-review` D11 to the guards a fix leaves behind.

## Goals

- A closed defect leaves behind something mechanical that refuses its class, so the class is closed rather than the instance
- The thing left behind is findable from the issue, and the issue is findable from it
- A guard's scope is legible: a reader can tell what it enumerates without running it
- The rules are cheap enough that a one-line fix doesn't acquire a ceremony, and honest enough that "no guard is possible" stays an available answer with a cost attached

## Non-Goals

- Prescribing the guard's technology. A unit test, a lint rule, a pre-commit hook, a compiler setting, or a type that makes the bad state impossible to express are all guards; which one fits is the repository's call
- Prescribing test design. A guard is often a test, and when it's one, `spec/project/test-falsifiability/` and the tier specs govern how it's written
- Owning branch protection. Whether a lane is enforced is `spec/project/quality-gate/` §"Enforced lane per tier"; G2 consumes that answer rather than restating it
- Retroactive application. These rules bind defects closed after the spec is adopted; sweeping a repository's history is a separate, optional exercise
- Not a source of coverage. A guard exists only once somebody has named the class, so this spec is reactive by construction and can't tell anybody where to look. `spec/project/capability-reach-audit/` is the deliberate search that produces the classes a guard then refuses.

## Requirements

### The rules

- **G1—A closed defect class leaves a guard, or a written note saying why it can't.** Closing a defect **MUST** leave behind either a mechanical guard that refuses the class, or a note in the issue stating why no mechanical guard is possible and what a reader should watch for instead. A closure that says only that the fix is obvious and won't recur isn't a note; it's the belief that produced every chain in the corpus. The note is the honest exit and it **MUST** be written down, because an unwritten one is indistinguishable from not having considered the question.
- **G2—The guard runs in an enforced lane.** A guard **MUST** run where it can block the merge that would reintroduce the class. A guard in an advisory lane is a comment: it produces a signal nobody is obliged to read, which is the same confidence failure `test-falsifiability` §Context describes from the other side. Which lanes are enforced is decided by `spec/project/quality-gate/` §"Enforced lane per tier," and that section's ban on exempting a guard-bearing tier is the half of this rule that lives there. Where a guard genuinely can't run before a merge, because it needs a deployed environment, a nightly window, or real credentials, it **MUST** carry the same written note G1 requires, naming what it can't cover and when it does run.
- **G3—The guard enumerates the class; it doesn't check the site.** A guard **MUST** be written as a predicate over the whole class and **MUST NOT** be a check bound to the sites where the defect happened to be found. An enumerating guard finds the member nobody has looked at yet; a site-bound one finds nothing new by construction, and a new site is opted in only by whoever remembers to opt it in. The predicate **MUST** appear in the guard's own header or docstring, not only in the commit message or the pull request that introduced it, because that's the copy a reader has in front of them when they decide whether a new case is covered.
- **G4—Exceptions are an allowlist with a reason per entry, and a stale entry fails.** Where the class has legitimate members that must be permitted, they **MUST** be an explicit allowlist carried with the guard, each entry naming its reason, and an entry that no longer matches anything **MUST** fail the guard. Without the staleness rule the allowlist only grows: entries outlive their reason, and the guard's coverage shrinks silently in the one direction nobody watches. A reason **MUST** survive being read against the thing it excuses. The `#1353` closing record in kamerplanter names three allowlist entries whose stated reason didn't survive review and that were excusing real defects, which is worse than no allowlist, because it writes the drift down as approved.
- **G5—The guard carries the issue number.** A guard's file, test, or rule name **MUST** carry the issue number of the defect it closes, so the finding and the rule stay findable from each other. Not every guard has a name of its own: a required keyword-only parameter, a narrowed type, or a signature that makes the wrong call fail to compile is a guard with nowhere to put a number. Such a guard **MUST** carry the issue number in the docstring or comment at the constraint itself, and that placement is the point, because the reader about to widen the signature back is the reader who needs the reason. Someone reading the guard can reach the evidence that motivated it; someone reading the issue can reach what now holds. A guard whose reason lives only in a merged pull-request description is a rule nobody can evaluate the next time it's inconvenient.
- **G6—The selector matches the property's scope.** A guard's selector **MUST** be as wide as the property it asserts. Where the property belongs to the assembled application, the selector **MUST NOT** be a filename, a directory, or any other list that a new file joins only by being named correctly. Those are opt-in lists with the same hole the guard exists to close, one level up. Derive the set from the thing that holds the property: the mounted router rather than the modules that look like routers, the resolved dependency graph rather than the import list, the built artifact rather than the source directory.
- **G7—The guard asserts nothing the fix didn't repair.** A guard left behind by a fix **MUST NOT** assert, as intended behaviour, any member of the class the fix didn't repair. Where a fix is deliberately partial, the guard **MUST** name the members it didn't repair and fail on them, skip them explicitly, or carry the follow-up issue number at the assertion. G1 asks whether an artefact exists; G7 asks what it says. A test that pins the half that wasn't repaired is worse than no test, because it writes the incompleteness down as intended: a later reader who asks "is this covered?" finds a green, specific, falsifiable test asserting exactly the broken behaviour, and the next occurrence isn't found by the guard that exists for it—the guard is the reason it isn't found. Observed: a fix that repaired a one-sided edge deletion two lines above a bidirectional edge deleted the same one-sided way, whose new test pinned the outbound anchoring for the still-broken edge and whose integration check queried dangling edges for the repaired edge type only; the author's own three-rule sweep reported zero remaining violations because its rules were written around the repaired shape
- **G8—A self-revoking comment satisfies no gate; a marker with grammar, an open issue and a red guard does.** A comment declaring the code beneath it wrong—a module whose central premise the comment calls false, a detector it describes as not yet existing, a part it calls deliberately still absent, a behaviour it files as a known limitation—while that code keeps running and the tests beneath it stay green **MUST NOT** stand alone: it satisfies no gate, and the class stays open until someone happens to read it. Such a site **MUST** carry a marker with a fixed grammar a lane can count—`SELF-REVOKED: #<issue> <YYYY-MM-DD>`—and the marker is valid only while the named issue is open **and** a red or explicitly expected-to-fail guard (`xfail` or equivalent) exists for the revoked behaviour; a marker whose issue is closed, or without such a guard, is a lane failure. That guard is itself subject to G2: it runs in a lane that can block a merge, so a revocation can't be certified by a test nobody runs. A marker older than **30 days** (from its date, overridable per project with a recorded reason) with the issue still open is a lane failure too, so a revocation can't age into a permanent state. Observed: four sites, three of them with tests certifying the revoked behaviour, all repaired by a sweep that nothing but a reader triggered

### Applying the rules proportionately

A one-line fix must not acquire a ceremony. The rules scale with the class, not with the diff:

- A defect with a class of exactly one member satisfies G1 with the note, in one sentence, saying so. Writing that sentence costs a line, and it's the whole of the work
- Where a guard already exists for the class and the defect slipped past it, the work is repairing the guard's predicate or its selector (G3, G6), not adding a second guard beside it. Two guards for one class drift, and the corpus contains that shape too
- Where the class is large enough that the guard can't be written in the same change, the guard **MUST** be its own issue, referenced from the closing one, rather than an intention recorded in a pull-request body. An intention in a merged body is lost at merge

### Binding into the closing process

- A pull request that closes a defect **MUST** record what its class left behind, and `spec/project/pull-request-workflow/` §"Class sweep (Conventional-Commits type `fix`)" is where it records it: that section's `Guard` field is this spec's G1 answer, and its `Predicate` field is G3's predicate. The two specs describe one artifact from two sides, and the fields **MUST NOT** diverge: where a guard exists, its own selector is what the sweep quotes
- `spec/project/issue-orchestration/` makes the completed sweep a closing condition of an orchestrated run
- `spec/project/source-code-review/` D11 is where an existing guard's conformance to G3, G4, and G6 is assessed during review, independently of any single defect

## Acceptance Criteria

- [ ] For a sample of recently closed defects, each left behind either a guard or a written note saying why none is possible; no closure relies on an unwritten judgement that the class can't recur
- [ ] Every guard's predicate is readable in the guard's own header or docstring, and describes a class rather than the sites where the defect was found
- [ ] Every guard runs in a lane that can block a merge, or carries a note naming what its lane can't cover and when it runs
- [ ] Every allowlist entry carries a reason, and removing a matching subject makes the guard fail on the now-stale entry, verified by removing one rather than by inspection
- [ ] Every guard's name carries the issue number of the defect it closes, and every guard without a name of its own, such as a required parameter or a narrowed type, carries it at the constraint
- [ ] No guard asserting a property of the assembled application selects its subjects by filename or directory
- [ ] No guard left behind by a fix asserts a member of its class the fix didn't repair as intended behaviour; where the fix is partial, the guard names those members and fails, skips explicitly, or carries the follow-up issue at the assertion. Applied by hand to kamerplanter's PR `#1573` (issues `#1535`, `#1533`), the rules identify the outbound-anchored adjacency assertion as the violation; a rule set that grades that pull request as conformant is wrong
- [ ] Every comment that revokes the code beneath it carries a `SELF-REVOKED: #<issue> <YYYY-MM-DD>` marker whose issue is open and whose revoked behaviour has a red or expected-to-fail guard; a marker with a closed issue, with no such guard, or older than the project's age bound with the issue still open fails the lane, and a revoking comment without a marker is itself a finding
- [ ] **Falsification.** Applied by hand to kamerplanter's `#927 → #948 → #950 → #952 → #1263` chain, these rules identify at which link the class should have been enumerated and which rule was violated. A rule set that finds that chain compliant is wrong and is reworked before it lands

## References

Every reference below is an issue or pull request in `nolte/kamerplanter`, read at first hand on 2026-09-12. They're the corpus the rules are derived from, not external authority. A sister-repository issue has exactly one canonical location, so reading it at first hand is what `spec/claude/research-triangulate/` §When triangulation is required can ask of it: a second source would re-read the same record rather than corroborate an independently varying fact.

- G1, G3: the chain `#927` (cross-tenant reads, closed at the repository layer) → `#948` (the write-side twin, which names the class and makes sweeping it an acceptance criterion) → `#950` → `#952` → `#1263`. `#1263` records that `#948` fixed two of the four routes carrying its shape
- G3, G6: `#1353` and its closing record. The sweep as first described keyed on the filename `tenant_router.py` and couldn't see three routes in `nutrient_calculations/router.py` and `plant_instances/diary_router.py`; the shipped guard computes the set from the mounted router instead
- G4: `#1353`'s closing record, on three allowlist entries whose stated reasons didn't survive being read against the routes they excused
- G2, G5: the named guards `boundary-validation` (`#970`), `utc-calendar-day` (`#858`), `tenant-body-field` (`#1000`), `workflow-gate-integrity` (`#1313`), and `#1404`, where a guard sat in a lane that couldn't block a merge
- G7: PR `#1573` (closing `#1535` and `#1533`), whose new test pinned the outbound anchoring of the bidirectional edge the fix left one-sided, and whose sweep reported zero violations because its rules matched the repaired shape; `nolte/claude-shared#640` is the work order
- G8: `#1456`, the 2026-09-16 measurement of four self-revoking comments, three of them with tests certifying the revoked behaviour, closed by the sweep of 2026-09-17; `nolte/claude-shared#637` is the work order

## Open Questions

- **Who ships the `SELF-REVOKED` counter.** G8 names the marker grammar, the open-issue binding and the age bound, but the lane that counts markers is the consumer's. The first consumer (`nolte/kamerplanter`, `#1456`) waits for this rule and has an empty seed corpus at HEAD, so a lane armed today would measure nothing; whether the hub should ship a reference implementation of the counter, or only the grammar, is decided once a consumer has run one against a non-empty corpus. Recorded from `nolte/claude-shared#637`
