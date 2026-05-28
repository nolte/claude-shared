# Example 01 — Fresh bootstrap with existing audience artefact

Happy path: a fresh repository with no `project/` directory, but a populated `AUDIENCES.md` at the repo root. The skill drafts both files, iterates with the user, then writes them after explicit approval.

## Input prompt

> Bitte richte die Roadmap für dieses Projekt ein — wir brauchen `project/goals.md` und `project/roadmap.md` zum ersten Mal.

## Input files

- `AUDIENCES.md` (repo root, non-empty):

  ```markdown
  # Audiences

  - **end-user** — Operators of the deployed CLI; run releases, configure environments.
  - **plugin-author** — Contributors who publish add-ons against the public extension API.
  - **maintainer** — Core team members who own the release cadence and the public API surface.
  ```

- `README.md` (repo root) describing the project as a release-orchestration CLI in German prose. No prior `project/` directory exists.
- No `project/goals.md`, no `project/roadmap.md`, no `project/mission.md`.
- The repository is initialised with git (clean working tree on `develop`).

## Expected behaviour

1. **Language detection** — the skill detects German from the README prose and the user's prompt; it responds in German for the entire interaction. The drafted prose in `goals.md` and `roadmap.md` is written in German. The schema strings (`O-<n>`, `R-<n>`, `fine`, `coarse`, `proposed`, `active`, `done`, `cancelled`) stay in their canonical English form.
2. **Precondition check** — confirms `project/goals.md` and `project/roadmap.md` are absent, confirms the working tree is inside a git repository.
3. **Audience resolution** — locates `AUDIENCES.md` at the repo root, reads it, captures the three audience identifiers (`end-user`, `plugin-author`, `maintainer`). Does **not** dispatch `audience-identify`.
4. **Vision draft** — drafts a one-paragraph `# Vision` section in German, naming what the project is and who it is for. Iterates with the user until approved; does not write.
5. **Outcomes draft** — drafts an `## Outcomes` list with monotonic identifiers (`O-1`, `O-2`, …). Each outcome:
   - is phrased as a one-sentence end-user benefit (not "wir refactoren …" / "we refactor …"),
   - cites one audience identifier from `AUDIENCES.md` in a trailing `_(audience: …)_` cite,
   - does not invent any audience identifier outside the artefact.
6. **Roadmap draft** — drafts `project/roadmap.md` with:
   - a top-of-file paragraph naming `spec/project/roadmap/` as governing spec and pointing maintenance at `roadmap-plan` and `roadmap-refine`,
   - the convention note that `R-<n>` IDs are monotonic and never reused across the project's lifetime,
   - **zero roadmap items** (the queue starts empty by design),
   - phase headings only if the user explicitly asks for them (the skill must ask, not assume).
7. **Approval gate** — presents both drafts side by side and waits for explicit approval of both before any disk write. Refuses to write either file in isolation.
8. **Atomic write** — once approved, creates `project/`, writes `project/goals.md` and `project/roadmap.md` together. If either write fails, rolls back so the project never lands in a half-bootstrapped state with one file present and the other missing.
9. **Hand-off message** — confirms both paths back to the user in German, reminds them that:
   - `roadmap-plan` is the entry point for adding items, retargeting sprints, and flipping MVP flags,
   - `roadmap-refine` walks the queue and enforces the detail-level invariant once items exist,
   - when `project/mission.md` is added later, every roadmap item will start carrying the `mvp` field.
10. **No mission requirement** — the skill does not ask for or require `project/mission.md`; mission authoring belongs to a separate skill family.
