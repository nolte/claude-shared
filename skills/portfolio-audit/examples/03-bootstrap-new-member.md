# Example 03 — Bootstrap a new Portfolio-Member's first portfolio.yml

A fresh `nolte/*` repository that has never carried a
`project/portfolio.yml` runs the Bootstrap operation to author its
first manifest interactively. Exercises Operation 3's precondition
chain (mission + audience artefact must exist before capability
identification can begin) and the hard rule that Bootstrap never
authors `project/mission.md`, `project/roadmap.md`, or the audience
artefact itself.

## Input prompt

> Bootstrap the portfolio manifest for this repository.

## Input files

The active checkout is `nolte/metrics-collector`. It is not
archived, lives under `nolte/`, does not carry the
`portfolio: excluded` opt-out marker in `CLAUDE.md`, and does not
yet have a `project/portfolio.yml` (so the Bootstrap precondition
check passes).

`project/mission.md` exists with `mvp_status: in_progress` and a
mission statement that reads in part:

> Provide a self-hosted metrics-collection service that aggregates
> per-repository CI runtime, test-flake counts, and dependency-audit
> trends across the `nolte/*` portfolio for portfolio maintainers.

`project/audiences.md` (the audience artefact per
`spec/project/audience-identification/`) exists and lists, among
others, the audience entries `portfolio-maintainer` and
`release-engineer`.

`project/roadmap.md` carries two `status: active` items that name
the two candidate capabilities in their titles:
*"CI runtime aggregation across portfolio"* (R-3) and
*"Dependency-audit trend dashboard"* (R-7).

The `claude-shared` repository is not the active checkout — only
the Bootstrap operation is in scope here; Audit and Render are out
of scope per the skill's role-detection rule.

## Expected behaviour

1. **Repository-role detection passes.** The skill confirms the
   active repository is a plausible Portfolio-Member candidate
   (under `nolte/`, not archived, no opt-out marker, no existing
   `project/portfolio.yml`) and selects the Bootstrap operation.
   It explicitly notes that Audit and Render are unavailable from
   this checkout.
2. **Mission precondition checked.** The skill reads
   `project/mission.md` and confirms it exists with a non-empty
   mission statement; the mission scope frames which capabilities
   are admissible. If the file were missing, the skill would stop
   and route the operator to `mission-define` rather than invent a
   mission inline.
3. **Audience-artefact precondition checked.** The skill reads
   `project/audiences.md`, confirms it exists, and caches the list
   of declared audience entries. If the file were missing, the
   skill would stop and route the operator to
   `audience-identification` rather than invent audiences inline.
4. **Roadmap context loaded.** The skill reads `project/roadmap.md`
   to confirm that the candidate capabilities align with active
   roadmap items (R-3 and R-7 are both `status: active`).
5. **Capability-identification walk** runs once per candidate. For
   each capability the skill walks the operator through:
   - `name` proposed in kebab-case from the user's description
     (`ci-runtime-aggregator`, `dependency-audit-trend-dashboard`)
     and confirmed
   - `description` confirmed as one or two sentences naming what
     the capability does and for whom
   - `audience` mapped strictly to existing entries in
     `project/audiences.md` (`portfolio-maintainer`,
     `release-engineer`); a candidate audience that is not in the
     artefact is rejected and the operator is routed to
     `audience-identification` to add it first
   - `status` defaulted to `active`; the operator may override to
     `experimental`
   - `rationale` collected as one or two sentences naming why this
     repository owns the capability — empty or template rationales
     are rejected
   - Optional `peers` (cross-references in `<repo>:<capability>`
     shape) and `since` (ISO date) collected if the operator
     volunteers them
6. **Manifest written** at `project/portfolio.yml` in the active
   checkout, with both capabilities serialised in the schema
   declared by `spec/portfolio/portfolio-management/`
   §Capability inventory per repository (`name`, `description`,
   `audience`, `status`, `rationale`, plus optional `peers` and
   `since`). The skill verifies the file parses as YAML before
   declaring success.
7. **Closing message** confirms the file path back to the operator
   in their language, lists the two captured capabilities as a
   concise summary, and reminds the operator that the next
   `portfolio-audit` run from inside `claude-shared` will pick up
   the new manifest (this checkout cannot run Audit itself).
8. **Hard rules honoured.** The skill did not modify
   `project/mission.md`, `project/roadmap.md`, or
   `project/audiences.md`; did not write anything under
   `claude-shared`; did not open a PR against another
   Portfolio-Member; did not invent an audience entry; rejected
   empty rationales; and did not alter capability status anywhere
   from the audit side (Bootstrap only writes the initial
   manifest).
