# Project Sprint

Status: draft

## Context

Readers: repo maintainers of hobby-scale nolte projects who invoke the `sprint-plan`, `sprint-execute`, and `sprint-review` skills, plus the implementing authors writing those skills against this schema.

The sibling `roadmap` spec defines the queue of work and ties every item back to a project outcome, but it deliberately doesn't specify how that work is grouped, executed, and shipped. This spec fills that gap. A sprint in the nolte portfolio is a markdown-tracked unit of work that bundles one or more features (defined by the sibling `feature` spec) and **must end in a deployable artefact** (defined by the sibling `release-artifact` spec) **that delivers a direct benefit to the end user**. Two properties matter: hobby-scale projects need genuinely variable duration (a sprint can last a weekend or three months), and consuming Claude skills (`sprint-plan`, `sprint-execute`, `sprint-review`) need a deterministic markdown shape they can read, mutate, and validate. This spec defines that shape and the lifecycle that governs it.

## Goals

- Define the on-disk shape of a sprint as a single markdown file at `project/sprints/<NNNN>-<slug>.md`, one file per sprint, never split.
- Specify the per-sprint frontmatter schema (sprint number, status, value statement, artifact reference, feature list) so consuming skills can parse and mutate sprints without ad-hoc parsers.
- Mandate the value-delivery contract: every sprint **MUST** have a one-sentence `value_statement` from the end-user perspective, and at least one feature in the sprint **MUST** carry an acceptance criterion that directly verifies that statement.
- Mandate the artefact contract: every closed sprint **MUST** point at a concrete deployable artefact (release tag, container image tag, plugin version, or doc-site deploy) that materialises the value statement, governed in detail by the sibling `release-artifact` spec.
- Define the sprint lifecycle (`planned → active → review → closed`) and which transitions are legal, so that sprint-plan, sprint-execute, and sprint-review have non-overlapping authority.
- Stay portfolio-reusable across hobby-scale variability: sprint duration is an output of the work, not an input, and the spec explicitly tolerates pauses and irregular cadence.

## Non-Goals

- Defining the roadmap, feature, or release-artefact internals. Each is owned by its own sibling spec; this spec only declares relationships and the sprint-side surface.
- Replacing project-management tooling. The sprint markdown is the authoritative record under version control; cross-references to issue trackers are allowed but never authoritative.
- Mandating a fixed cadence or duration. The sibling `roadmap` spec already declares dates and time estimates out of scope, and this spec follows suit at sprint granularity.
- Substituting `continuous-improvement`. Retrospective process change is event- and calendar-driven there; sprint-review here is a per-sprint closure ritual, not a process audit.
- Substituting `release-automation` or `release-skill-layer`. The deployable-artefact reference points **at** those mechanisms; it doesn't redefine them.
- Inventing acceptance criteria. Feature-level acceptance lives in the sibling `feature` spec; sprint-review only verifies that the sprint's value statement is covered by at least one feature's existing criterion.

## Requirements

### Directory layout and file shape

- **MUST** place every sprint at `project/sprints/<NNNN>-<slug>.md`, where `<NNNN>` is a four-digit zero-padded monotonically-assigned sprint number and `<slug>` is an ASCII kebab-case summary of the sprint goal.
- **MUST** keep exactly one markdown file per sprint; sprint content is never split across multiple files.
- **MUST NOT** reuse a sprint number after a sprint is `cancelled` or `closed`; numbers are strictly monotonic across the project's lifetime.
- **SHOULD** keep `<slug>` aligned with the sprint's value statement so directory listings remain self-describing.

### Frontmatter schema

- **MUST** open the file with a YAML frontmatter fence carrying the following fields, in this order:
  - `number` (integer, required)—matches `<NNNN>` in the filename;
  - `status` (enum, required)—one of `planned`, `active`, `review`, `closed`, `cancelled`;
  - `started` (ISO date or null, required)—the date the sprint moved to `active`; null until then;
  - `ended` (ISO date or null, required)—the date the sprint reached either `closed` or `cancelled` (both terminal states share this field, hence the neutral name); null until the sprint terminates;
  - `value_statement` (string, required, non-empty)—one sentence describing the direct end-user benefit this sprint delivers;
  - `artifact_ref` (string, list of strings, or null, required)—the field is always present in the frontmatter; **MUST** be non-null no later than transition to `review`. Concrete reference to the deployable artefact (for example `v0.4.0`, `ghcr.io/owner/repo:v0.4.0`, `nolte-shared@1.7.0`, `docs.example.com@2026-05-08`); a list form is permitted for hybrid project types that ship two coupled artefacts in one sprint (for example `[v0.4.0, ghcr.io/owner/repo:v0.4.0]`); the allowed shapes per project type are governed by the sibling `release-artifact` spec;
  - `last_commit` (string or null, required)—the commit SHA of the last source change that this sprint contributed; null until the first feature in the sprint reaches `done`. `sprint-execute` updates this field whenever a feature in the sprint moves to `done`. The field anchors the artefact ancestry check that the sibling `release-artifact` spec runs at closure;
  - `roadmap_items` (list of roadmap-item IDs, required, may be empty)—every entry **MUST** match an `R-<n>` defined in `project/roadmap.md`;
  - `features` (list of feature IDs, required, may be empty)—every entry **MUST** match a feature ID defined in `project/features/<slug>.md` per the sibling `feature` spec.
- **MUST NOT** include effort estimates, velocity metrics, or assignment fields beyond what's declared above; lints flag unknown frontmatter keys.

### Body sections

- **MUST** carry the following level-2 sections in this order, even when empty (skills depend on stable section headings):
  - `## Goal`: a paragraph elaborating the `value_statement` from the operator's perspective; what success looks like at sprint close.
  - `## Features`: bullet list of the features in scope, each linking to `project/features/<slug>.md` and showing the feature's current status; the feature list **MUST** mirror the `features` frontmatter field exactly.
  - `## Out of scope`: explicit list of items that were considered but excluded from this sprint, each pointing at the roadmap item it came from when applicable; prevents creep mid-sprint.
  - `## Review notes`: populated by `sprint-review` at closure; before that, the section exists but may be empty or carry a placeholder.
- **MAY** carry an additional `## Risks` section listing known unknowns and workarounds; recommended for sprints whose features cross unfamiliar boundaries.

### Lifecycle

- **MUST** transition `status` only along these paths: `planned → active`, `active → review`, `review → closed`, `review → cancelled`, `planned → cancelled`, `active → cancelled`. Direct transitions outside these paths are forbidden; in particular, `active → closed` without passing `review` is forbidden because the value-coverage check (see §Value-delivery contract) lives in `review`. The `review → cancelled` path exists for the case where artefact validation per the sibling `release-artifact` spec fails at closure and the sprint can't recover (for example the underlying release pipeline is broken and re-cutting the artefact isn't feasible at this time).
- **MUST** ensure that at most one sprint per project is in `active` status at any moment; multiple parallel active sprints break the linear cadence assumption that consuming skills rely on.
- **MUST** automatically promote the lowest-numbered `planned` sprint to `active` no later than the moment one of its features moves from `ready` to `in_progress` per the sibling `feature` spec; `sprint-execute` is the canonical enforcement point. The promotion fails (and the feature transition is rejected) when another sprint is already `active`.
- **MAY** keep multiple sprints in `planned` status at once; the next sprint is always the lowest-numbered `planned` sprint.
- **SHOULD** move a sprint into `review` as soon as every feature it contains is `done` per the `feature` spec; **MUST** populate `## Review notes` and verify the value-delivery contract before transitioning to `closed`.
- **MUST** reject any `active → review` transition while the sprint's `features` frontmatter list is empty, because an empty list can't satisfy the §Value-delivery contract (no feature can declare `verifies_sprint_value`); `sprint-execute` and `sprint-review` enforce this gate. The schema-level "required, may be empty" allowance for `features` (see §Frontmatter schema) applies during `planned`; the empty-list state is no longer permitted at the moment the `active → review` transition is attempted.

### Value-delivery contract

- **MUST** carry a non-empty `value_statement` phrased from the end-user perspective; operator-internal language isn't a value statement and **MUST** be rejected by `sprint-plan` before persisting the sprint file. The rejection rule **MUST** apply at minimum when the statement begins with or is built around an internal verb in the project's primary language (`refactor`, `restructure`, `set up`, `configure`, `clean up`, `migrate`, `bump`, `update dependency`, plus the same set in German: `refaktorieren`, `umbauen`, `einrichten`, `konfigurieren`, `aufräumen`, `migrieren`, `aktualisieren`, `Abhängigkeit erneuern`); `sprint-plan` **MUST** surface the violation with the offending verb quoted, and **MAY** widen the rule list per project. The check is a heuristic, not a complete classifier: operators who genuinely deliver an end-user-facing change whose phrasing happens to start with one of these verbs **MAY** override with a one-line rationale recorded in the sprint's `## Goal` section.
- **MUST** ensure that at least one feature listed in the sprint declares itself as the value-verifier by setting the `verifies_sprint_value: acceptance-<n>` frontmatter field per the sibling `feature` spec, and that the named acceptance criterion when checked directly verifies the sprint's `value_statement`. The verifying feature's criterion **MAY** be expressed as a CLI command, a manual demo step, or a test reference; the form is feature-spec business, but the **existence** of the frontmatter marker is enforced here.
- **MUST** refuse to close a sprint (`review → closed`) when no feature in the sprint declares `verifies_sprint_value`, when the named criterion doesn't exist on the feature, or when the named criterion is still unchecked.
- **MUST** record the verifying criterion's full location (`features/<slug>.md` plus the `acceptance-<n>` ID) inside `## Review notes` at closure so future readers find the audit trail without re-walking the feature files.

### Artefact contract

- **MUST** carry a non-null `artifact_ref` no later than transition to `review`; an empty `artifact_ref` at `review` is a blocker.
- **MAY** carry `artifact_ref` as a list of strings when the project type ships two coupled artefacts in a single sprint (for example a CLI tool plus its container image, or a Python library plus its docs-site deploy); each list entry **MUST** match a taxonomy shape from the sibling `release-artifact` spec.
- **MUST** ensure that the referenced artefact is concrete enough to be re-fetched **at the moment of sprint closure** (a git tag, a container-image digest tag, a published plugin version, a dated doc-site deploy URL); commit SHAs alone are insufficient unless the project explicitly publishes by SHA. The spec doesn't promise indefinite re-fetchability beyond the project's own retention policy: tag deletion or registry rotation that occurs after closure is a separate concern (covered by the consuming repo's archival posture, not this spec).
- **MUST** ensure the artefact is **deployable to production** in the project's sense (for hobby-scale projects, "production" may mean "the operator's own deployed instance"—but the artefact must be runnable end-to-end, not a half-built branch).
- **MUST** validate the artefact reference at sprint closure: the sibling `release-artifact` spec defines the per-project-type validation rules and the dispatch into `release-skill-layer` skills; sprint-review delegates to those rules rather than redoing them.

### Dispatch into release machinery

- **MAY**, when sprint-review runs and the project type publishes via `release-publish.yml`, dispatch `release-notes-curate` to enrich the open draft's body and `release-publish-trigger` to perform the publish. Both dispatches are operator-opt-in at sprint closure; sprint-review **MUST NOT** chain unattended, and the sprint **MUST** record the operator's decision (chained or skipped) in `## Review notes`.
- **MUST NOT** call `gh release edit --draft=false`, `gh api -X PATCH /repos/.../releases/<id> draft=false`, or any other path that flips the draft state outside `release-publish.yml`. The rule comes from `release-automation` and `release-skill-layer` and is non-negotiable here too.
- **SHOULD**, when the operator declines the curate / publish chain at closure, leave a one-line note in `## Review notes` stating who or what's expected to dispatch publication later (operator manually, automated post-merge job, or a follow-up sprint) so the audit trail is unbroken.

### Roadmap and feature linkage

- **MUST** ensure that every entry in `roadmap_items` resolves to an `R-<n>` defined in `project/roadmap.md`; a sprint **MAY** carry an empty `roadmap_items` list (for example a hardening sprint that exists for its own sake), but its features still **MUST** carry a `roadmap_item` per the sibling `feature` spec—declare the hardening intent as a roadmap item first, link the features to it, then leave the sprint's `roadmap_items` empty if the hardening item is the only one. The sprint's `## Goal` section **MUST** make the empty-list case explicit when it occurs, naming the hardening intent and citing the roadmap item the features link to.
- **MUST** ensure that every entry in `features` resolves to a feature file under `project/features/`; the feature file's frontmatter **MUST** carry `sprint: <NNNN>` matching the sprint number, otherwise the back-reference is broken (the back-reference itself is governed by the sibling `feature` spec).
- **MUST** keep the body's `## Features` bullet list in sync with the `features` frontmatter list; `sprint-execute` is the canonical enforcement point and **MUST** refuse to update one without updating the other in the same operation.
- **MAY** add or remove features mid-sprint while `status: active`, but **MUST NOT** alter the `value_statement` after activation; if the value statement no longer matches reality, the sprint **MUST** be cancelled and rescheduled.

### Hobby-scale variability

- **MUST NOT** require a duration target, a calendar deadline, or a cadence assumption; `started` and `closed` are recorded after the fact, not predicted up-front.
- **SHOULD** tolerate paused sprints: a sprint may sit in `active` for an extended period; the value-delivery and artefact contracts still apply at closure regardless of elapsed time.
- **MAY** mark a sprint `cancelled` when reality changes faster than the sprint can adapt, and **MAY** reach `cancelled` from `planned`, `active`, or `review`; cancellation is a first-class outcome, not a failure state, and **MUST** be reflected in `## Review notes` with a one-paragraph rationale before `cancelled` is final. The rationale **MUST** state which lifecycle stage the sprint was in when cancelled and why recovery wasn't feasible at this time.

## Acceptance Criteria

- [ ] Every sprint exists as exactly one file at `project/sprints/<NNNN>-<slug>.md` with monotonically-assigned `<NNNN>`; no sprint number is reused across the project's lifetime.
- [ ] Every sprint's frontmatter carries the nine schema fields (`number`, `status`, `started`, `ended`, `value_statement`, `artifact_ref`, `last_commit`, `roadmap_items`, `features`) in the declared order; lints flag unknown keys and reject `closed` as a frontmatter field name (the field is named `ended` because it covers both `closed` and `cancelled` terminal states).
- [ ] Every sprint's body carries the four required level-2 sections (`Goal`, `Features`, `Out of scope`, `Review notes`) in the declared order; missing sections fail validation.
- [ ] No sprint transitions `active → closed` without passing through `review`; transition-graph violations are rejected by `sprint-execute` and `sprint-review`.
- [ ] No sprint moves a feature to `in_progress` while a different sprint is still in `active` status; `sprint-execute` fails the feature transition rather than starting a parallel active sprint.
- [ ] Every closed sprint has at least one feature in its `features` list whose frontmatter declares `verifies_sprint_value: acceptance-<n>`, and the named acceptance criterion is checked; `sprint-review` refuses closure otherwise.
- [ ] Every sprint that reaches `review` carries a non-null `artifact_ref` whose shape (string or list) matches the sibling `release-artifact` spec for the project's detected type; commit-SHA-only references fail unless the project publishes by SHA.
- [ ] Every closed sprint's `last_commit` is non-null and points at a commit reachable from the artefact referenced in `artifact_ref`; `sprint-execute` is the canonical write authority for this field per §Frontmatter schema (writing it incrementally as features in the sprint reach `done`), and `sprint-review` at `active → review` confirms the field is non-null and consistent with `artifact_ref` rather than producing it.
- [ ] The `Features` body section and the `features` frontmatter list are identical at every sprint mutation; `sprint-execute` refuses partial updates.
- [ ] Every entry in `roadmap_items` resolves to an `R-<n>` in `project/roadmap.md`; every entry in `features` resolves to a feature file whose own frontmatter back-references this sprint's `number`.
- [ ] Every operator decision on the `release-skill-layer` chain at sprint closure (chained or skipped) is recorded in `## Review notes`; sprint files closed without a recorded decision fail validation.
- [ ] Every cancelled sprint's `## Review notes` carries a one-paragraph rationale that names the lifecycle stage at which cancellation occurred (`planned`, `active`, or `review`); a missing rationale or stage citation fails validation.
- [ ] No sprint transitions `active → review` while its `features` frontmatter list is empty; an empty list would make the value-delivery contract at §Value-delivery contract unsatisfiable, so `sprint-execute` and `sprint-review` reject the transition with a verbatim error pointing at the empty list.

## Open Questions

- Should a single project ever have parallel sprint tracks (for example one user-facing track and one infrastructure track) and, if so, how does the "at most one active sprint" invariant relax? Defer until a portfolio project genuinely needs parallel tracks; the simpler invariant covers hobby scale today.
- Should `value_statement` accept a structured format (audience-id + benefit) rather than free text, so that downstream tooling can group sprints by audience? Defer until a real reporting need appears; structured statements add ceremony for little benefit at hobby scale.
- Should `cancelled` sprints carry a `cancelled_reason` enum (`replanned`, `descope`, `obsoleted`, `paused-indefinitely`) in addition to the prose rationale? Cheap to add later; currently the rationale paragraph is enough.
- Mid-sprint hot-fixes are tracked as out-of-band artefacts under `project/release-artifacts/out-of-band/` per the sibling `release-artifact` spec; an open question is whether such an out-of-band release should also retroactively note the disruption in the currently-active sprint's `## Review notes`. Defer until a real hotfix scenario appears.
- The operator-internal-language rejection list in §Value-delivery contract is heuristic. Should it move to `.github/sprint-rejection-rules.yml` so each repo can extend it without forking the spec? Defer until a project genuinely needs a per-repo extension.
