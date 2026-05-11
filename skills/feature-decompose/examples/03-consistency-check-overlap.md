# Example 03 — Consistency check finds overlap with an existing feature

A decomposition where the `feature-consistency-reviewer` agent
returns an `overlap` finding against an already-drafted feature.
Exercises the write-blocking path of Operation 2 step 4 and the two
operator-facing exits: `merge-into <id>` (the redundant feature is
not written) versus `proceed` with an explicit one-paragraph
rationale in `## Consistency notes`.

## Input prompt

> Decompose R-15 into features.

## Input files

`project/roadmap.md` (excerpt):

```yaml
- id: R-15
  title: Surface the latest release tag on the docs landing page
  outcomes: [O-2]
  detail: fine
  target_sprint: 8
  mvp: false
  status: planned
```

`project/features/landing-page-meta-strip.md` already exists with
`status: draft`, `roadmap_item: R-9`, and a `## Description` that
reads in part:

> Adds a meta strip below the hero on the docs landing page that
> displays project metadata (current sprint, latest release tag,
> last build status). The strip pulls release information from the
> GitHub Releases API at build time.

The `feature-consistency-reviewer` agent is reachable.

## Expected behaviour

1. **Preconditions pass** as in Example 01.
2. **One-feature split proposed** for R-15 with a candidate title
   *"Latest release tag on docs landing page"* and the slug
   `latest-release-tag-on-landing-page`. The operator confirms.
3. **Per-feature gathering** runs once and produces a draft
   description, three to seven acceptance criteria, and matching
   test hooks — all in the shape declared by Operation 1 step 3.
4. **Consistency check dispatched.** The agent returns a non-clean
   `findings` array with at least one entry of the form
   `{kind: overlap, target: project/features/landing-page-meta-strip.md,
   resolution: <unresolved>}` because the existing feature already
   covers "latest release tag" rendering on the landing page.
5. **Write blocked.** Per Operation 2 step 4, the skill refuses to
   write the new feature file while an `overlap` finding has no
   acceptable resolution. The skill surfaces the overlap to the
   operator, quotes the conflicting passage from the existing
   feature, and asks them to choose one of:
   - **`merge-into landing-page-meta-strip`** — fold the R-15
     acceptance criteria into the existing feature instead of
     writing a new one.
   - **`proceed`** with a one-paragraph rationale that explains
     why the two features are intentionally separate (e.g. the
     existing meta strip is build-time-only and R-15 needs
     runtime updates from the GitHub Releases API on every page
     load, which is a fundamentally different render path).
6. **Branch A — operator picks `merge-into`.** The skill records
   the `merge-into landing-page-meta-strip` resolution against the
   finding for audit purposes, **does not** write
   `project/features/latest-release-tag-on-landing-page.md`, and
   tells the operator that the merge of R-15's acceptance criteria
   into the existing feature is a separate authoring step (the
   existing feature is owned by `sprint-plan` once it leaves
   `draft`; while still `draft`, hand-edit the acceptance criteria
   into the existing file). The decomposition for R-15 ends here.
7. **Branch B — operator picks `proceed` with rationale.** The
   skill captures the rationale paragraph in `## Consistency notes`
   alongside the overlap finding restated in prose, persists the
   finding in frontmatter as
   `{kind: overlap, target: …, resolution: proceed}`, and only
   then writes the new feature file with the nine frontmatter
   fields and five required body sections in declared order.
8. **Hard rules honoured in both branches.** No status flip past
   `draft`; `verifies_sprint_value` left `null` (R-15 is not the
   MVP-closer); no file written if the operator declines either
   resolution path; the slug, once written in Branch B, is
   immutable thereafter.
