# Example 03 — Operator opts in to chain into `release-notes-curate` and `release-publish-trigger`

Exercises step 5's chain dispatch under the **opt-in** branch. Sprint
closes cleanly on a Python-library project; operator confirms the chain
explicitly, the skill dispatches `release-notes-curate` first, then
`release-publish-trigger`, captures the run URLs from each downstream
skill, and records the chain decision **verbatim** in `## Review notes`
per `spec/project/sprint/` §Acceptance Criteria and
`spec/project/release-skill-layer/` §Skill A / §Skill B. The recording
is mandatory — a sprint that closes without a captured operator
decision fails validation.

## Input prompt

> Schließe Sprint `0014` ab — Tag `v1.4.0` ist gecuttet, Draft-Release
> liegt vor. Bitte direkt im Anschluss `release-notes-curate` laufen
> lassen und dann `release-publish-trigger` dispatchen, damit der Draft
> heute noch live geht.

## Input files

`project/sprints/0014-batched-readers.md` (the sprint to close):

```markdown
---
id: 0014
slug: batched-readers
status: active
value_statement: Bibliotheks-Konsumenten lesen Frontmatter-Batches mit
  einer einzigen API-Aufruf-Sequenz.
roadmap_items: [R-19]
features: [F-31, F-32]
verifies_sprint_value: F-31
started: 2026-04-26
ended: null
last_commit: 8e2bd913c4
artifact_ref: v1.4.0
---

# Sprint 0014 — Batched readers

## Features

- [F-31](../features/batch-reader-api.md) — done
- [F-32](../features/batch-reader-perf-tests.md) — done
```

`project/features/batch-reader-api.md` (the `verifies_sprint_value`
feature; relevant excerpt only):

```markdown
---
id: F-31
slug: batch-reader-api
status: done
sprint: 0014
roadmap_item: R-19
verifies_sprint_value: acceptance-2
---

## Acceptance criteria

- [x] **acceptance-1** — Public API ist im `__init__.py` exportiert.
- [x] **acceptance-2** — Ein End-to-End-Konsumentenbeispiel läuft mit
      einer einzigen `read_batch()`-Aufruf-Sequenz durch.
- [x] **acceptance-3** — Doku unter `docs/api/batch-readers.md` ist
      veröffentlicht.
```

`project/features/batch-reader-perf-tests.md` is `status: done`,
`verifies_sprint_value: null`.

`pyproject.toml` exists with a `[project]` table that declares the
package — project type: **Python library** per
`spec/project/release-artifact/` §Project-type detection.

The git tag `v1.4.0` exists locally and points at commit `8e2bd913c4`
(matches `last_commit`). The PyPI distribution `v1.4.0` is **not yet
published** (publication is exactly what `release-publish-trigger` will
dispatch). A draft GitHub release for `v1.4.0` exists on develop
(release-drafter authored), and `gh release view v1.4.0` returns the
draft body successfully.

`.github/workflows/release-publish.yml` exists in the repo. Every
required status check on `develop` is currently SUCCESS. No
`.github/release-skill-layer.yml` override.

## Expected behaviour

1. **Preconditions.** All pass: sprint `active`, two-feature list,
   every feature `done`, `last_commit` non-null, `artifact_ref`
   non-null.
2. **Operation 1 — `active → review`.** Skill writes `status: review`
   on the sprint frontmatter (no `ended` yet). Surfaces the sprint
   summary verbatim.
3. **Operation 2 — project-type detection.** Detects `pyproject.toml`
   with a populated `[project]` table → **Python library**.
4. **Operation 3 — artefact validation.** Skill parses
   `artifact_ref: v1.4.0`. Per the Python-library rule the canonical
   verification command is `pip index versions <dist>`; before PyPI
   publication that returns "no matching distribution found" — which
   is the **expected** state at this point in the flow because the
   `release-publish-trigger` step is what will publish the dist. Skill
   resolves this per `spec/project/release-artifact/` §Validation at
   sprint closure: it runs `git rev-parse v1.4.0` (exit 0, prints
   `8e2bd913c4…`, matches `last_commit`) **and** runs
   `gh release view v1.4.0` to confirm the draft release exists on
   develop. Both pass; the dist-publication check is deferred to
   `release-publish-trigger`. Records the verification transcript.
5. **Operation 4 — `verifies_sprint_value` confirmation.** Skill walks
   the two feature files, finds exactly one (`F-31`) with a non-null
   `verifies_sprint_value` (`acceptance-2`), reads
   `features/batch-reader-api.md`, locates the
   `- [x] **acceptance-2** …` bullet, confirms it is checked.
6. **Operation 5 — release-skill-layer chain (operator OPTS IN).**
   Skill asks the user explicitly whether to chain. Operator's prompt
   already named both downstream skills. Skill dispatches in fixed
   order:
   - **`release-notes-curate`** runs first against the open
     `release-drafter` draft for `v1.4.0`. Returns a run summary or
     URL. Skill captures it.
   - **`release-publish-trigger`** runs second. It validates every
     gate from `spec/project/release-automation/` §Pre-publish
     verification (tag reachable from develop tip, version-bearing
     files aligned, alignment commit present if required, every
     required status check on develop SUCCESS, `release-publish.yml`
     exists). All gates pass. Dispatches
     `release-publish.yml` via `gh workflow run`. Returns the
     workflow-run URL. Skill captures it.
   Skill assembles the verbatim `## Review notes` chain entry — the
   recording must be exact, not paraphrased:
   > Chained: release-notes-curate (run summary: <captured>),
   > release-publish-trigger (workflow run URL: <captured>).
7. **Operation 6 — `review → closed`.** Skill writes
   `status: closed` and `ended: 2026-05-10` on the sprint
   frontmatter. Populates `## Review notes` with: the verification
   transcript from step 4 (commands and outcomes), the
   verifying-feature pointer (`features/batch-reader-api.md` plus
   `acceptance-2`), and the **verbatim** chain decision from step 6
   (both downstream invocations with their captured URLs).
8. **Roadmap-item lifecycle.** If every feature owned by `R-19` is
   `done` and falls inside this sprint, skill flips `R-19` to
   `status: done` per `spec/project/roadmap/` §Lifecycle.
9. **Closing summary.** Skill surfaces: path to the closed sprint,
   `ended: 2026-05-10`, `artifact_ref: v1.4.0`, the verifying feature
   (`F-31:acceptance-2`), the chain decision (chained, with both
   captured URLs), and a note that publication is now in flight via
   the dispatched `release-publish.yml` run — the operator should
   monitor it but the sprint itself is closed.

Failure modes that **MUST** be surfaced instead of silently succeeding:

- If the operator's opt-in is implicit ("ja, mach mal") and not
  pinned to both downstream skill names, skill **MUST** ask
  explicitly which to chain — the chain decision needs to be
  recordable verbatim.
- If `release-publish-trigger` refuses to dispatch because a
  pre-publish gate fails (e.g. a required check went red between
  step 4 and step 6), skill records the failure verbatim in
  `## Review notes`, still completes step 7 (`review → closed`)
  because artefact validation already passed in step 4, and routes
  the failed publish to `workflow-health-triage`. The sprint
  closes; publication is operator-initiated later.
- The chain entry in `## Review notes` **MUST** be verbatim — a
  paraphrase ("Chain wurde durchgeführt") fails the
  `spec/project/sprint/` §Acceptance Criteria audit-trail check.
- Skill **MUST NOT** call `gh release edit --draft=false` directly
  at any point — `release-publish-trigger` is the only acceptable
  publish path.
