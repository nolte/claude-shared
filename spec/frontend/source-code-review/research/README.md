# frontend source-code review — Research source material

The five files in this folder are **research artefacts**, not audit findings for the
`claude-shared` repository itself:

- `layering-and-business-logic.md` — where logic belongs in a client, the trust boundary,
  server state vs. client state, client/server rule duplication (feeds F1, F4)
- `error-and-state-handling.md` — fetch failure semantics, error boundaries and their limits,
  the loading/error/empty contract, effect races and cleanup (feeds F2, F5)
- `component-design-and-performance.md` — component API design, effect anti-patterns,
  memoization judgment under an auto-memoizing compiler, design-token drift (feeds F3, F6, F7)
- `accessibility-and-security.md` — the rules of ARIA use, code-level a11y defects, the
  client-side injection sinks the framework does not escape (feeds F8, F9)
- `testing-and-i18n.md` — Testing Library query priority and implementation-detail avoidance,
  frontend test smells, user-facing text and locale handling in code (feeds F10, F11)

Each file pairs every load-bearing claim with **at least two independent authoritative sources**
(W3C, MDN, OWASP, official framework documentation) and carries confidence labels: `verified`
(two or more independent sources), `partial` (normative source plus a single library or
community doc), `unverified` (single source or inference; flagged for spec-input review).

**Volatile-assertion note.** Per `spec/claude/research-triangulate/` §Author-time assertions, an
upstream version pin or a third-party API default that a spec rule would direct an agent to act
on is held to the three-source Release/dispatch tier. This spec deliberately avoids that class:
every rule that would otherwise depend on a volatile upstream fact (most visibly the
memoization rule, which depends on whether an auto-memoizing compiler is enabled) is written
**conditional on the reviewed repository's own build configuration**, which the reviewer reads
directly. Repo-internal facts need no triangulation.

## Purpose

These files were authored as **input** to `spec/frontend/source-code-review/`, which extends
`spec/project/source-code-review/` with the frontend particulars, and which a future frontend
reviewer agent consumes.

This folder lives inside the spec topic it feeds. The `claude-shared` repository ships no
browser-rendered frontend — these notes apply to consumer projects that adopt the spec.

## What this folder is **not**

- Not a `spec-readiness-reviewer` report (see `.audits/spec-readiness/`).
- Not a `source-code-review` findings report (see `.audits/source-code-review/`).
- Not an action plan with severity ratings, deadlines, or owners.
- Not a spec topic of its own: the files are English-only evidence notes, deliberately outside
  the bilingual `{en,de}.md` contract and the Vale gate (which lints `README.md`, `docs/en/`,
  and every `spec/**/en.md`).

## Lifecycle

- **Source of truth**: this folder. Post-publication corrections go into each file's dated
  "Currency addendum" section.
- **Consumed by**: `spec/frontend/source-code-review/{en,de}.md`.
- **Refreshed**: when the reference framework profile's major version changes, when the
  normative accessibility guidance updates, or when a new framework profile is added.
