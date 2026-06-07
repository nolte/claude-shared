# Example 02 — Reject operator-internal `value_statement`

Negative-path scenario for operation 2 of `SKILL.md`. The operator supplies a
value statement that begins with an operator-internal verb (`refactor`); the
skill MUST reject it, surface the offending verb, and ask for a user-visible
rephrase before continuing. No file is written until the rephrase passes.

## Input prompt

> Open the next sprint. Value statement: "Refactor the release pipeline so
> the publish workflow is cleaner."

## Input files

`project/sprints/0011-stabilise-mermaid-render.md` exists with
`status: closed`; the highest existing sprint `number` is `11`.

`project/roadmap.md` (excerpt):

```markdown
- id: R-22
  title: Release-pipeline cleanup
  outcomes: [O-2]
  status: proposed
  target_sprint: 12
  detail: fine
  mvp: false
```

`project/features/release-pipeline-cleanup.md` exists, links
`roadmap_item: R-22`, has `sprint: null`, `status: ready`.

No `sprint_rejection_verbs:` key is set in `.github/release-skill-layer.yml`,
so the default rejection verb list applies.

## Expected behaviour

1. Skill replies in the user's language (English here).
2. Operation 1 resolves the next sprint number as `12`; this is computed
   but not yet written.
3. Operation 2 — the value statement begins with `Refactor`. The skill
   matches `refactor` against the English operator-internal verb list,
   rejects the statement, and surfaces the violation explicitly:
   - quotes the offending verb (`refactor`),
   - cites that operator-internal verbs name internal restructuring,
     not user-visible value,
   - explains that the heuristic-override path requires a one-line
     rationale describing the user-facing change the refactor enables.
4. Skill asks the user to rephrase the value statement from the
   end-user perspective, OR to supply an explicit override rationale
   that names the user-visible change. Skill does NOT proceed to
   operation 3, does NOT slugify, does NOT touch any file.
5. Suppose the user rephrases to: "Maintainers can publish a release in
   a single click without hand-editing workflow YAML." The new statement
   contains no operator-internal verb; the skill accepts it and resumes
   at operation 3 with the new phrasing.
6. Alternative path — if the user instead insists on the original
   `Refactor …` phrasing AND supplies a rationale like "the refactor is
   load-bearing because it is the only way users get the one-click
   publish behaviour they have been asking for", the skill MAY accept
   under the heuristic-override clause and MUST record the rationale
   verbatim in the written sprint's `## Goal` section.
7. The skill never silently accepts the original `Refactor …` phrasing.
   No `project/sprints/0012-*.md` file is created until either the
   rephrase or the explicit override is on record.
