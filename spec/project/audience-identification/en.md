# Audience Identification

Status: draft

## Context
<!-- Why does this spec exist? What problem, user need, or constraint drives it? -->

Software modules and projects are consumed, operated, constrained, or observed by multiple audience groups — users, operators, downstream integrators, maintainers, security, compliance, business stakeholders, indirect end users, and more. Without a disciplined way to enumerate which audiences apply to a *bounded context* (a specific module, service, library, or project), decisions about documentation depth, API surface, release cadence, SLAs, and security posture are made against the author's private assumptions rather than against the actual audience set. This spec defines a repeatable method to identify and characterize the audiences of any scoped context so that downstream artifacts (READMEs, specs, threat models, release notes, SLAs) can reference an authoritative audience list instead of reinventing one each time.

## Goals
<!-- What this spec aims to achieve. Bullet points, outcome-oriented. -->
- Provide a consistent procedure for enumerating the audiences of a defined context
- Ensure every identified audience is characterized by its relationship to the context (consume, operate, extend, govern, …)
- Produce an artifact that other specs (`readme-structure`, `pull-request-workflow`, future threat-modeling specs, …) can point to
- Make audience identification repeatable and reviewable rather than the output of a single author's gut feel
- Surface unknown or assumed audiences explicitly so they can be validated or retired

## Non-Goals
<!-- Explicitly out of scope. Prevents creep. -->
- Defining marketing personas or demographic segmentation
- Prescribing how to engage or communicate with audiences once identified
- Producing a permanent, organization-wide master audience list (this spec is scoped per context, not per org)
- Threat modeling — audiences feed into it but are not equivalent to threat actors
- Declaring which artifact format (README section, dedicated file, ADR, …) hosts the audience list; that is an implementation choice left to adopting specs

## Requirements
<!-- Use RFC 2119 keywords: MUST, SHOULD, MAY. One atomic requirement per bullet. -->
- **MUST** begin with a written declaration of the bounded context: what the module or project *is*, where its boundaries run, and what is explicitly outside
- **MUST** enumerate audiences under the following relationship categories, and state "none" with a reason when a category does not apply:
  - **Direct consumers** — who invokes the context's interface (humans, other services, downstream libraries)
  - **Operators** — who runs, deploys, monitors, or hosts the context in production or test
  - **Contributors / maintainers** — who modifies the code or authors its content
  - **Governing parties** — legal, compliance, security, architecture review, business stakeholders with approval or constraint authority
  - **Indirect audiences** — parties affected by the context without interacting with it directly (e.g. end users behind a consumed service)
- **MUST** record for every listed audience:
  - a short label
  - the relationship category
  - the interaction surface (API, CLI, config, docs, dashboard, incident channel, …)
  - what the audience expects or needs from the context
  - any open question or assumption where information is missing
- **MUST** tag every audience as `confirmed` (validated with a real representative or an authoritative source) or `assumed` (inferred by the author)
- **MUST** produce the audience list before downstream artifacts that claim an audience are written (README "intended consumers", SLAs, threat models, …), so those artifacts can reference it rather than restate it
- **SHOULD** rank audiences by criticality to the success of the context (primary / secondary / peripheral)
- **SHOULD** store the audience artifact alongside the context it describes (module README, project-level `docs/audiences.md`, ADR, …) rather than in a central registry
- **SHOULD** revisit the audience list whenever the context's scope materially changes — new public API, new deployment target, new regulated data class, new stakeholder
- **MAY** link each audience entry to the specs, docs, or SLAs produced for it, so coverage is visible
- **MAY** subdivide audiences further by geography, organizational unit, or tenancy when such distinctions change the expected deliverable

## Acceptance Criteria
<!-- Testable, checkable conditions. A reviewer should be able to mark each as done/not done. -->
- [ ] A worked example exists applying the method to one concrete artifact in this repository (for example the `nolte-shared` plugin or one of its skills)
- [ ] The `readme-structure` spec references this spec where it speaks of "intended consumers"
- [ ] An audience list produced under this spec contains at least one audience per applicable relationship category, or records "none" with a reason for any category it omits
- [ ] Every audience entry distinguishes `confirmed` from `assumed`
- [ ] The bounded context is declared in writing before any audience is listed
- [ ] The `spec-drift-audit` skill can flag a module whose documented audiences no longer match its actual interaction surface

## Open Questions
<!-- Unresolved decisions, known unknowns, things that need a stakeholder answer. -->
- Should the audience artifact standardize on a dedicated file (for example `AUDIENCES.md`) or remain a section inside existing artifacts (README, ADR)?
- Is there a minimum context size below which this method is overkill (for example a 50-line internal utility)?
- Does this spec apply portfolio-wide, or only to repositories that explicitly opt in?
- How should an audience list be versioned — per release, per major API change, or continuously through git history?
- Is the "Governing parties" category mandatory even for purely internal, single-team modules, or optional there?
- How does this spec interact with future threat-modeling, privacy-impact, or SLA specs that will also consume the same audience list?
