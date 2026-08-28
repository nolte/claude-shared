# Example 02 — Unrecoverable artefact-validation failure routes `review → cancelled`

Exercises the cancellation path (step 7). The operator triggers a sprint
close, the skill promotes `active → review`, but the per-kind verification
command for the declared `artifact_ref` (a GitHub release) returns a
hard 404 because the release was deleted out of band. The operator
confirms recovery is not feasible at this time. The skill routes to
`review → cancelled`, populates `## Review notes` with the mandatory
one-paragraph rationale naming the lifecycle stage, re-targets every
roadmap item that pointed at this sprint, and explicitly does **not**
advance any roadmap item to `done` despite every feature being
individually `done` per `spec/project/sprint/` §Acceptance Criteria
and `spec/project/roadmap/` §Sprint and feature linkage.

## Input prompt

> Schließe Sprint `0008` ab — alle Features sind `done`, der Tag
> `v0.8.0` war veröffentlicht.

## Input files

`project/sprints/0008-observability-baseline.md` (the sprint to review):

```markdown
---
id: 0008
slug: observability-baseline
status: active
value_statement: Operatoren sehen pro Plugin-Run, welche Skills geladen
  und welche Tools aufgerufen wurden.
roadmap_items: [R-9, R-10]
features: [F-15, F-16]
verifies_sprint_value: F-15
started: 2026-04-12
ended: null
last_commit: 2d77b41eaa
artifact_ref: v0.8.0
---

# Sprint 0008 — Observability baseline

## Features

- [F-15](../features/run-trace-emitter.md) — done
- [F-16](../features/trace-format-spec.md) — done
```

`project/features/run-trace-emitter.md`:

```markdown
---
id: F-15
slug: run-trace-emitter
status: done
sprint: 0008
roadmap_item: R-9
verifies_sprint_value: acceptance-2
---

## Acceptance criteria

- [x] **acceptance-1** — JSONL-Schema dokumentiert.
- [x] **acceptance-2** — End-to-End-Run emittiert eine valide Trace-Datei.
```

`project/features/trace-format-spec.md` is `status: done`,
`verifies_sprint_value: null`.

`project/roadmap.md` excerpt — `R-9` and `R-10` both
`target_sprint: 0008`, `status: active`.

`.claude-plugin/plugin.json` exists. `.claude-plugin/marketplace.json`
**does not** list version `0.8.0` (the marketplace was rolled back). The
git tag `v0.8.0` exists locally and points at `2d77b41eaa`. The GitHub
release `v0.8.0` was **deleted out of band** — `gh release view v0.8.0`
exits with code `1` and prints `release not found`.

(The project type is Claude plugin, so the per-kind verification rule
runs `git rev-parse <tag>` plus the marketplace-resolution probe per
`spec/project/release-artifact/` §Validation at sprint closure. The
marketplace probe fails first.)

No `.github/release-skill-layer.yml` override.

## Expected behaviour

1. **Preconditions.** All pass: sprint `active`, two-feature list,
   every feature `done`, `last_commit` non-null, `artifact_ref`
   non-null.
2. **Operation 1 — `active → review`.** Skill writes `status: review`
   on the sprint (no `ended` yet). Surfaces the sprint summary
   verbatim.
3. **Operation 2 — project-type detection.** Detects
   `.claude-plugin/plugin.json` → Claude plugin.
4. **Operation 3 — artefact validation FAILS.** Skill runs the
   Claude-plugin verification:
   - `git rev-parse v0.8.0` → exit 0, prints `2d77b41eaa…`. Pass.
   - Marketplace-resolution probe: reads
     `.claude-plugin/marketplace.json` at HEAD, **does not** find
     version `0.8.0`. Fail.
   Skill records the failed check verbatim and surfaces it to the
   operator: the marketplace listing is missing for the declared
   artefact. Skill asks the operator whether the failure is
   **recoverable** (re-publish to marketplace and rerun) or
   **unrecoverable** (cancel the sprint). Operator confirms
   unrecoverable: the rollback was deliberate, the artefact will not
   be re-published in this sprint window.
5. **No step 4 / step 5 / step 6.** Skill does **not** check
   `verifies_sprint_value`, does **not** ask about the
   release-skill-layer chain, and does **not** promote `review →
   closed`. The artefact-validation failure short-circuits straight to
   step 7 per the skill's strict-order contract.
6. **Operation 7 — `review → cancelled`.** Skill writes
   `status: cancelled` and `ended: 2026-05-10` on the sprint
   frontmatter. Populates `## Review notes` with a one-paragraph
   rationale that **MUST** name (a) the lifecycle stage at which
   cancellation occurred (`review`) and (b) why recovery wasn't
   feasible at this time. Example wording (operator language):
   > Sprint `0008` wurde im Stadium **review** abgebrochen.
   > Artefakt-Validierung ist fehlgeschlagen, weil
   > `.claude-plugin/marketplace.json` Version `0.8.0` nicht mehr
   > listet (Rollback war beabsichtigt). Eine erneute
   > Marketplace-Veröffentlichung ist im aktuellen Sprint-Fenster nicht
   > vorgesehen, deshalb ist Recovery aktuell nicht praktikabel; die
   > offenen Roadmap-Posten werden auf einen Folge-Sprint umgehängt.
   Missing rationale or missing lifecycle-stage citation is a hard
   validation failure.
7. **Roadmap re-targeting.** Skill walks `R-9` and `R-10`, both still
   pointing at sprint `0008`. Per `spec/project/roadmap/` §Sprint and
   feature linkage, skill clears each `target_sprint` to `null` (or
   asks the operator for a successor `planned` sprint to point at).
8. **Roadmap items stay `active`.** Even though `F-15` and `F-16` are
   both `done`, skill does **NOT** advance `R-9` or `R-10` to
   `status: done`. The `cancelled` sprint cannot carry roadmap items
   across the finish line per `spec/project/roadmap/` §Lifecycle and
   the skill's Hard rules.
9. **Closing summary.** Skill surfaces: path to the cancelled sprint,
   `ended: 2026-05-10`, the rationale paragraph, the re-targeting
   outcome (`R-9 → null`, `R-10 → null` or named successor), and an
   explicit note that no roadmap item was advanced to `done`.

Failure modes that **MUST** be surfaced instead of silently succeeding:

- Routing past step 3 to step 4 or step 5 after a verification failure
  is a Hard-rules violation — must short-circuit to step 7.
- Writing `status: cancelled` without the mandatory
  lifecycle-stage citation in `## Review notes` is a Hard-rules
  violation per `spec/project/sprint/` §Acceptance Criteria.
- Advancing `R-9` or `R-10` to `done` from this `cancelled` sprint
  is a Hard-rules violation; the items remain `active` until a
  successor sprint reaches `closed`.
- Skill **MUST NOT** call `gh release edit --draft=false` at any
  point; the failure mode here forbids any draft-state mutation.
