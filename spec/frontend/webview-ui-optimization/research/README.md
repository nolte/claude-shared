# webview-ui-expert — Research source material

The five files in this folder are **research artefacts**, not audit findings for the `claude-shared` repository itself:

- `accessibility.md` — WCAG 2.2 Level AA conformance practices, ARIA APG patterns, `vitest-axe`, MUI a11y notes
- `i18n.md` — Browser `Intl.*`, `i18next` + `react-i18next`, MUI RTL, `dayjs` localized formats, `Content-Language` header
- `performance.md` — React 19, Vite 8, MUI v9, Redux Toolkit, React Router v7 data routers, recharts, nginx static-serving
- `security.md` — CSP, token-bearer auth, axios, react-hook-form + zod, qrcode.react, nginx security headers
- `ux.md` — React Router v7 data routers, react-hook-form + zod, notistack, MUI X data grid, RTK Query patterns

Each file pairs every best-practice claim with **at least two independent authoritative sources** (W3C, MDN, WebAIM, Deque, web.dev, official vendor docs) and carries confidence labels: `verified` (two or more independent sources), `partial` (normative source plus a single library / community doc), `unverified` (single source or inference; flagged for spec-input review).

## Purpose

These files were authored as **input** to `spec/frontend/webview-ui-optimization/`, which the `webview-ui-optimize` skill operationalises (and which the `webview-ui-expert` agent uses for cross-file deep reviews of named frontend targets).

This folder lives inside the spec topic it feeds (relocated 2026-07-24 from `.audits/webview-ui-expert/`, where its research nature was routinely mistaken for a disposable findings report). The `claude-shared` repository ships no browser-rendered frontend — these notes apply to consumer projects (`kamerplanter`, `kamerplanter-ha`, future webview-ui-bearing repos) that adopt the spec.

## What this folder is **not**

- Not a `spec-readiness-reviewer` report (see `.audits/spec-readiness/`).
- Not a `spec-drift-audit` report (see `.audits/spec-drift/`).
- Not a `portfolio-inflight-triage` finding set (see `.audits/portfolio-inflight/`).
- Not an action plan with severity ratings, deadlines, or owners.
- Not a spec topic of its own: the files are English-only evidence notes, deliberately outside the bilingual `{en,de}.md` contract and the Vale gate (which lints only `spec/**/en.md`).

If you are looking for actionable claude-shared audit findings, browse the `.audits/<audit-type>/` folders instead.

## Lifecycle

- **Source of truth**: this folder. Updates land here as research material evolves; post-publication corrections go into each file's dated "Currency addendum" section.
- **Consumed by**: `spec/frontend/webview-ui-optimization/{en,de}.md` (when the spec lifts a rule from research into a normative requirement).
- **Shipped mirror**: `plugins/nolte-engineering/skills/webview-ui-optimize/references/research-notes/` bundles a copy for plugin consumers; refresh both together.
- **Refreshed**: when the underlying library versions in scope change materially (React major bump, Vite major bump, MUI major bump, …) or when WCAG / ARIA APG normative guidance updates.
