---
mission_statement: "claude-shared (the nolte-shared Claude Code plugin) gives downstream Claude Code users in nolte portfolio projects plus the plugin's own dogfooding maintainer a consistent, spec-compliant set of skills, agents, and bilingual specifications they can apply without per-repository reimplementation."
relevant_outcomes:
  - O-1
  - O-3
audiences:
  - Downstream Claude Code users in portfolio projects
  - Plugin author dogfooding inside this repo
verifies_via: F-1:acceptance-1
time_bound:
  kind: mvp_completion
mvp_status: stabilised
created: 2026-05-09
revised_at: 2026-05-29
---

# Mission

## Statement

`claude-shared` (the `nolte-shared` Claude Code plugin) gives downstream Claude Code users in nolte portfolio projects plus the plugin's own dogfooding maintainer a consistent, spec-compliant set of skills, agents, and bilingual specifications they can apply without per-repository reimplementation.

**SMART decomposition:**

- **Specific** — the `mission_statement` names two concrete audiences (downstream Claude Code users in portfolio projects, plus the plugin author dogfooding inside this repo) drawn from `AUDIENCES.md`. Both are tagged `primary`. The "what" is "consistent, spec-compliant skills/agents/specs" and the "for whom" is the audience pair just named — no implicit "users" appears anywhere in the sentence.
- **Measurable** — `verifies_via: F-1:acceptance-1` pins success to the acceptance criterion on `project/features/mission-statement-published.md` that asserts a fully spec-compliant `project/mission.md` exists. When that bullet is checked, the mission is measurably achieved; the proof-of-life is the artefact you're reading.
- **Achievable** — MVP scope is a single roadmap item (`R-1` "Planning-suite dogfood adoption complete") carrying `detail: fine`, `target_sprint: 1`, `mvp: true`. One sprint's worth of work, well inside the 2-5-sprint achievability bound the spec recommends.
- **Relevant** — `relevant_outcomes: [O-1, O-3]` ties the mission to two outcomes from `project/goals.md`: O-1 (downstream consistency for portfolio consumers) and O-3 (the plugin as reference adopter of every spec it ships). Both outcomes resolve back to the audiences named above.
- **Time-bound** — `time_bound: { kind: mvp_completion }` binds the mission to the moment `mvp_status` reaches `achieved` (every `mvp: true` roadmap item is `done` and the verifying acceptance criterion is checked). No calendar date appears anywhere in the frontmatter or this body — the schedule is variable per the sibling `sprint` spec's hobby-scale clause.

## Audiences

**Downstream Claude Code users in portfolio projects.** What the MVP delivers to this audience: a published `nolte-shared` plugin whose slash commands (`/nolte-shared:spec`, `/nolte-shared:skill-management`, `/nolte-shared:pull-request-create`, and the planning-suite skills) produce reproducible, spec-compliant outputs against any repo that installs it. The audience benefits because the plugin removes the "every repo reinvents its review and release rituals" tax — a single install path replaces N copies of the same workflow, and consumers can rely on the bilingual specs as the contract for what each command does.

**Plugin author dogfooding inside this repo.** What the MVP delivers to this audience: a working reference adoption of the planning suite inside `claude-shared` itself — `project/goals.md`, `project/roadmap.md`, `project/features/`, and this `project/mission.md`. The author benefits because every new spec can be lived in this repo before it's released to consumer repos, surfacing rough edges (like missing fallbacks, ambiguous wording, or unspecified back-references) where the cost of fixing them is lowest.

## Verification

The mission's verifying acceptance criterion lives on the feature `F-1` (`project/features/mission-statement-published.md`) under the identifier `acceptance-1`:

> `project/mission.md` exists with all eight required frontmatter fields (`mission_statement`, `relevant_outcomes`, `audiences`, `verifies_via`, `time_bound`, `mvp_status`, `created`, `revised_at`) and the four required level-2 sections (`Statement`, `Audiences`, `Verification`, `Source`) in the declared order per `spec/project/mission/`.

When that checkbox is checked at the close of the sprint that lands this feature, the mission is verified as achieved. `mission-revise` then flips `mvp_status: defining → in_progress → achieved`, and after one full subsequent sprint without regression on a `mvp: true` item, `→ stabilised` per `spec/project/mission/` §Stabilisation gate.

## Source

- **Audience artefact:** `AUDIENCES.md` at the repo root, last-commit SHA `0e3b6f9fc64bbfd97c74c2575d25fcfcae5598d6` at write time.
- **Goals consulted:** `project/goals.md` (authored in the same change-set as this mission file). Outcomes referenced: `O-1`, `O-3`.
- **Authorship:** maintainer `nolte` via inline application of `skills/mission-define/SKILL.md`. The skill wasn't yet loaded as a slash command in the running plugin runtime at the time of writing (it landed on `develop` minutes prior, in PR #46); operations were followed manually against the merged spec at `spec/project/mission/en.md`. A `/reload-plugins` would lift the inline application in any subsequent invocation.
- **2026-05-11 — `mvp_status: defining → in_progress`** via `mission-revise` Operation B. Evidence: roadmap item `R-1` (`mvp: true`) entered `status: active` when sprint `0001` was promoted to `active` and feature `F-1` started (`ready → in_progress`); see commit `9ee8805` on branch `chore/sprint-0001-execute`.
- **2026-05-29 — `mvp_status: in_progress → achieved`** via `mission-revise` Operation B. Evidence: the sole `mvp: true` roadmap item `R-1` is `status: done` and the mission's verifying criterion `F-1:acceptance-1` is checked `[x]`. The flip was overdue: the conditions had held since Sprint `0001` closed, but the status flag lagged until this revision.
- **2026-05-29 — `mvp_status: achieved → stabilised`** via `mission-revise` Operation B (§Stabilisation gate). Evidence: every `mvp: true` item (`R-1`) is `done`; the MVP-closing Sprint `0001` is `closed`; the full subsequent Sprint `0002` (number `0001 + 1`) is `closed` with no MVP item re-opened to `active`; no defect-fix feature against an MVP item is `in_progress`. Reconciliation note: post-MVP items `R-2` and `R-8` were executed to `done` while the flag still read `in_progress`, ahead of where the stabilisation gate would have permitted post-MVP starts; this flip corrects the lag, and the gate conditions hold in retrospect.
