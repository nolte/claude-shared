# Example 03 — Working off findings via `update` and `close`

## Trigger phrases

> "I've fixed F1 and F2 from the Q2 audit. Mark them closed."
> "F3 needs a spec revision, not a code fix — record that decision."
> "All findings resolved. Close the Q2 audit."

## Context

Continuing from Example 01. `docs/audits/2026-Q2.md` has three open findings:
- F1 — Missing feature-request.yml in ISSUE_TEMPLATE (adjust-impl)
- F2 — Skills missing `phase` frontmatter field (adjust-impl)
- F3 — Local vocab duplicates not removed post pin-bump (adjust-spec candidate)

---

## Session transcript — `update` operation

**User:** I've added feature-request.yml in PR #121 and fixed the phase field on all skills. Mark F1 and F2 closed.

**Skill (update, step 2 — verification):**

Verifying F1: reading `.github/ISSUE_TEMPLATE/`…
Found `feature-request.yml` — present and non-empty. Criterion passes.

Verifying F2: reading `plugins/nolte-planning/skills/roadmap-init/SKILL.md`…
`phase: plan` present in frontmatter. Grepping all SKILL.md files for missing phase…

```

grep -rL "^phase:" skills/*/SKILL.md
(no output — all skills have phase field)

```

Criterion passes.

**Skill (update, step 3–5):**

Marking F1 and F2 `- [x]` in `docs/audits/2026-Q2.md`.
Flipping `status` → `in-progress`.
Appending to `## Processing log`:

```

2026-05-20 — F1 — adjust-impl — verified: .github/ISSUE_TEMPLATE/feature-request.yml present (PR #121)
2026-05-20 — F2 — adjust-impl — verified: grep confirms phase field in all SKILL.md files (PR #121)

```

Diff shown. Commit? (Do not commit automatically.)

**User:** Yes, commit it.

**Skill:** Committed: `chore(audit): close F1 F2 in 2026-Q2 spec-drift audit (adjust-impl)`

---

**User:** For F3 — the vocab duplicates — I want to record a spec-revision decision. The prose-style spec should say "within one quarter" not "immediately after pin bump". The current wording is too strict.

**Skill (update, step 2 — verification):**

Verifying F3 context: reading `spec/project/prose-style/en.md` §Vocabulary maintenance…
Current wording: "once the upstream change is released, the local entry MUST be removed."
User proposes relaxing the response window. Decision: `adjust-spec`.

Recording in `## Decisions`:

```

### F3 — Local vocab duplicates not removed post pin-bump
Decision: adjust-spec
Action: Relax prose-style MUST to "local duplicate MUST be removed within one quarter of the upstream release"; tracked in spec-revise PR.
PR/Commit: (pending)
Resolved: 2026-05-20

```

Appending to `## Processing log`:

```

2026-05-20 — F3 — adjust-spec — decision recorded; prose-style spec revision pending

```

Diff shown. Commit?

**User:** Yes.

**Skill:** Committed: `chore(audit): record F3 decision (adjust-spec) in 2026-Q2 audit`

---

## Session transcript — `close` operation

**User:** All three findings have decisions. Close the Q2 audit.

**Skill (close, step 1–2):**

Reading `docs/audits/2026-Q2.md`…
F1: `- [x]` adjust-impl — verified.
F2: `- [x]` adjust-impl — verified.
F3: decision recorded (adjust-spec); no open `- [ ]` findings remain.

No open `fail` findings without a decision. Closure is permitted.

**Skill (close, step 3–4):**

Flipping `status` → `closed`. Recording `closed: 2026-05-20`.

Proposed commit message:

```

chore(audit): close 2026-Q2 spec-drift audit — 3 findings, 3 decisions

F1 adjust-impl (PR #121), F2 adjust-impl (PR #121),
F3 adjust-spec (prose-style revision pending).
repo-revision: b1b4d0b3f9c1a2d4e8f05b6c7d9e0f1a2b3c4d5e

```

Confirm to commit?

**User:** Confirmed.

**Skill:** Committed: `chore(audit): close 2026-Q2 spec-drift audit — 3 findings, 3 decisions`

Audit cycle 2026-Q2 is fully closed. The prose-style spec revision for F3 is the only remaining open action item and is tracked separately.
