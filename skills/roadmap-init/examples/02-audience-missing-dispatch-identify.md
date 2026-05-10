# Example 02 — Audience artefact missing, dispatch `audience-identify`

The repository has no audience artefact in any of the precedent locations. The skill must dispatch `audience-identify`, pause, and resume only after the user signals the artefact is ready — re-reading it from disk on resume.

## Input prompt

> Lege bitte `project/goals.md` und `project/roadmap.md` für dieses Projekt an.

## Input files

- No `AUDIENCES.md` at the repo root.
- No `docs/AUDIENCES.md`, no audience section in `README.md`, no audience ADR.
- No `project/goals.md`, no `project/roadmap.md`.
- `README.md` describes the project as an internal data-pipeline platform in English prose; no audience list anywhere.
- The repository is initialised with git (clean working tree on `develop`).

## Expected behaviour

1. **Language detection** — the skill detects German from the user's prompt and responds in German throughout, even though the README is in English. The eventual `goals.md` and `roadmap.md` prose follows the project's primary language (English here, derived from the README); the skill confirms this language choice with the user before drafting.
2. **Precondition check** — confirms `project/goals.md` and `project/roadmap.md` are absent.
3. **Audience artefact lookup** — searches the precedent locations (`AUDIENCES.md` at the root, `docs/AUDIENCES.md`, an "Audiences" / "Intended consumers" section in the README, an ADR). Finds none.
4. **Refusal to invent** — does **not** fabricate audience identifiers inline. The hard rule "Never invent audience entries inline" is binding; outcomes whose audience is fabricated cannot serve a real reader.
5. **Dispatch** — dispatches the `audience-identify` skill with a brief German hand-off note explaining why (outcome authoring is blocked until the audience artefact exists). Does not poll, does not wait silently — explicitly **pauses** and tells the user that `roadmap-init` will resume once they signal the artefact is ready.
6. **Pause boundary** — the skill stops here. No drafts of `goals.md` or `roadmap.md` exist yet. No partial files have been written.
7. **Resume on user signal** — when the user says "AUDIENCES.md ist fertig, mach weiter" (or any equivalent resume signal), the skill:
   - re-reads the audience artefact **from disk**, never trusting an in-memory copy from before the dispatch,
   - validates the artefact is non-empty and contains at least one audience identifier,
   - proceeds with step 2 (Vision + Outcomes draft) of the normal flow.
8. **Outcome authoring** — every outcome cites an audience identifier resolved from the freshly written artefact; no audience that does not appear in the artefact may be cited.
9. **Approval and atomic write** — same gate as Example 01: explicit approval of both drafts before any write; both files written together; rollback on partial failure.
10. **Hand-off message** — same `roadmap-planner` / `roadmap-refine` reminder, plus an explicit note that the audience artefact at `<resolved-path>` is now the source of truth for future outcome additions.
