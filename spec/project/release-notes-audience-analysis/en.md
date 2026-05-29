# Release Notes Audience Analysis

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

Every GitHub release of a project ships a release-notes document—today typically produced by `release-drafter` and published through `release-automation`. Who actually *reads* that document and what they need from it varies widely: an upgrader wants breaking-change callouts and migration steps; a downstream packager wants the dependency delta; a security team wants CVE references; an automated consumer (Renovate, Dependabot, release-tracking bot) wants a parseable category structure. Without deliberately identifying the release-notes audiences of a project, the notes default to "whatever `release-drafter` happened to group from the PR titles"—a flat list organized by commit type rather than by reader need. The `audience-identification` spec provides the generic method to enumerate audiences of a bounded context; this spec applies that method to the specific bounded context "release notes of a GitHub release of a project," so that the content structure, detail depth, language register, and call-to-actions of each release are produced against a known audience set rather than author assumption. It closes the gap between `release-automation` (which governs *how* a release publishes) and `release-drafter` configuration (which governs *what* a release contains): this spec covers *for whom* the content is assembled.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Apply the `audience-identification` method to the bounded context "release notes of a GitHub release" for a given project
- Produce, per project, an authoritative list of release-notes audiences that `release-drafter` configuration, PR-labeling conventions, and review standards can reference
- Connect each identified audience to the concrete content dimensions it drives—section structure, detail depth, language register, CTAs, machine-readability
- Make the reviewability of release-notes content explicit: a reviewer can say "this draft serves audiences A and B but leaves C's CTA missing" instead of arguing on taste
- Surface assumed or unverified release-notes audiences so they can be validated or retired, rather than accumulating as silent defaults inside `release-drafter.yml`

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Generic audience identification: `audience-identification` already defines the method
- Release publishing mechanics: `release-automation` governs the Draft → Published transition
- Prescribing a changelog format (Conventional Commits, Keep a Changelog, custom)—format choice is left to adopting projects
- Marketing or launch-campaign planning around a release
- Release cadence or versioning policy (inherited from `branching-model` and `release-drafter` configuration)
- CVE or security-advisory disclosure workflow—referenced as a consuming audience, not specified here
- Declaring a new location rule for the audience artifact: this spec adds none and inherits `audience-identification` §Requirements (artifact location)—canonical default `AUDIENCES.md` at the context root, with an "Audiences" README section or a dedicated `docs/release-audiences.md` as accepted alternatives (the same set `release-skill-layer` consumes). Embedding the list only as inline comments in `release-drafter.yml` is excluded, because it isn't deterministically locatable by consuming specs

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->
- **MUST** treat "release notes of a GitHub release of this project" as the written bounded context when applying `audience-identification`, and declare that context before listing audiences
- **MUST** follow the `audience-identification` procedure in full—relationship categories, per-audience fields, `confirmed` / `assumed` tagging—and not restate or override any of its requirements
- **MUST** produce the audience list before configuring or materially changing the project's `release-drafter` categories, PR-label taxonomy, or release-review conventions, so those artifacts can reference the list rather than invent one
- **MUST** evaluate at least the following candidate release-notes audiences, and for each record either a concrete entry or "not applicable" with reason:
  - **Upgraders**: existing adopters moving between versions of this project
  - **New adopters**: parties discovering the project via a release tag, release feed, or package-registry listing
  - **Downstream packagers / distributors**: OS packagers, HACS, npm/PyPI dependents, container-image builders, anyone republishing
  - **Operators / SREs**: parties running the project, reading for operational impact, deprecations, config changes, rollback risk
  - **Integrators**: API or CLI consumers tracking breaking changes
  - **Security-sensitive audiences**: CVE trackers, compliance reviewers, security teams using release notes as a disclosure channel
  - **Automated consumers**: Renovate, Dependabot, release-tracking bots, GitHub release-feed readers, and anything parsing the notes mechanically
  - **Contributors and maintainers**: for attribution and visibility of what landed
- **MUST** link every listed release-notes audience to the content dimensions it drives, covering at minimum:
  - which `release-drafter` section / category label must exist to serve this audience
  - required detail depth per entry for this audience (one-line summary, linked migration guide, embedded code diff, …)
  - language register (end-user vocabulary, operator vocabulary, developer vocabulary)
  - call-to-action (upgrade command, migration link, deprecation deadline, security-advisory pointer)
  - machine-readability constraints (stable category names, PR references, CVE IDs, SemVer labels)
- **MUST** classify breaking-change and security-disclosure audiences as primary whenever the project's scope can produce either class of change, because release notes are the canonical disclosure channel for both and downgrading those audiences risks undisclosed user impact
- **MUST** scope this spec's only release-time obligation for a security-disclosure audience to content coverage: the audience is ranked primary and its content dimensions (advisory pointer, CVE IDs) are verified before `release-publish.yml` is dispatched, per §Acceptance Criteria. The code-level security review stays delegated to the diff-scoped `security-review` skill invoked during the PR flow (the path `pull-request-workflow` already routes security-sensitive diffs through); this spec adds no separate mandatory pre-publish security gate
- **MUST** tag each audience as `confirmed` or `assumed` per `audience-identification`; a release-notes audience claimed without evidence (real representative, subscriber signal, automated-consumer detection, referring issue) stays `assumed`
- **SHOULD** align the project's `release-drafter` category configuration with the identified audiences—every configured category exists because at least one audience needs it, and categories that no audience needs are removed
- **SHOULD** align the project's PR-label taxonomy and Conventional-Commits scope so that `release-drafter` can assemble the audience-driven categories without manual post-editing
- **SHOULD** record per audience the consumption signal it actually uses—GitHub release feed / Atom, email subscription, in-product banner, dependency-bot PR body, release-tracking service—because the signal constrains acceptable length, formatting, and linkability. For automated consumers, discovery is manual enumeration of the project's known bot set (Renovate, Dependabot, release-tracking bots)—not a GitHub API subscriber audit, which isn't reliably available—and validation flips the entry `confirmed` / `assumed` via inspection of an incoming dependency-bot PR body or observation of which fields the bot parsed from one real release (per §Acceptance Criteria worked example)
- **SHOULD** re-evaluate the release-notes audience list whenever the project gains a new consumption channel (public HACS listing, first package-registry publish, container-registry push), adds a regulated data class, or crosses the threshold from internal to public consumption
- **MUST** apply the audience list forward-only: it governs release notes from the first release published after adoption, and already-published release notes are an immutable audit-trail artifact that's not re-audited or rewritten against a newly derived list, consistent with `release-automation`'s immutable-publish posture
- **SHOULD** treat a mid-release-cycle change to the audience list as non-blocking by default—a follow-up reconciled against the next release—EXCEPT when it adds or re-ranks a primary breaking-change or security-disclosure audience whose content dimension is now unmet, which blocks publish per §Acceptance Criteria (every primary audience's content dimensions verified before `release-publish.yml` is dispatched). Reconciliation is performed by re-running the draft-notes curation skill (`release-notes-curate`), which re-derives the audiences-served block from the artifact idempotently
- **MAY**, for a small internal-only project, inherit a minimal portfolio-default release-notes audience list (Upgraders + Automated consumers + Contributors) published from `nolte/gh-plumbing` instead of producing its own, recording the inheritance as a one-line reference; every project that publishes public GitHub releases owns its own list, because `audience-identification` is per-context, not org-wide
- **MAY** subdivide a release-notes audience by deployment scale (self-hoster vs. managed), expertise (end user vs. integrator), or tenancy when those distinctions change the required detail depth or language register
- **MAY** record a minimal "release-notes contract" per audience—a one-line statement of what every release of this project must give that audience (for example "every release must link an upgrade command for Upgraders")

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying the method to one concrete project in the portfolio (for instance `claude-shared` itself, documenting its plugin-consumer release-notes audiences)
- [ ] The produced artifact declares "release notes of <project>" as the bounded context in writing before any audience is listed
- [ ] Every listed audience maps to at least one content dimension (section, detail depth, language register, CTA, machine-readability)
- [ ] Every audience entry is tagged `confirmed` or `assumed`
- [ ] The project's `release-drafter` configuration can be traced back, category by category, to at least one listed audience
- [ ] `release-automation` §Non-Goals (release-notes content generation exclusion) cross-links to this spec so the boundary between mechanics and content is explicit
- [ ] `spec-drift-audit` can flag a project whose `release-drafter` categories, CHANGELOG sections, or release-notes review checklist no longer match its documented release-notes audiences
- [ ] A reviewer of a `release-drafter` draft can, using the audience list, verify that every primary-ranked audience's content dimensions are satisfied before `release-publish.yml` is dispatched
- [ ] Every audience whose consumption signal is an automated consumer has a recorded stability expectation for the fields it parses (category names, PR-reference format, CVE-ID format)

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
_None at this time._
