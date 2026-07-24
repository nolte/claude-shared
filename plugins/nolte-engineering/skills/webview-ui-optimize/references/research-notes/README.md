# webview-ui-expert — Research source material

> **Bundled copy.** This folder is a shipped mirror of the hub `spec/frontend/webview-ui-optimization/research/` research notes, packaged with the `nolte-engineering` `webview-ui-optimize` skill so consumers that install the plugin (and therefore receive no hub `spec/` tree) still have the per-rule research anchors. The hub-root folder remains the source of truth; refresh both together.

The five files in this folder are **research artefacts**, not audit findings for the `claude-shared` repository itself:

- `accessibility.md` — WCAG 2.2 Level AA conformance practices, ARIA APG patterns, `vitest-axe`, MUI a11y notes
- `i18n.md` — Browser `Intl.*`, `i18next` + `react-i18next`, MUI RTL, `dayjs` localized formats, `Content-Language` header
- `performance.md` — React 19, Vite 8, MUI v9, Redux Toolkit, React Router v7 data routers, recharts, nginx static-serving
- `security.md` — CSP, token-bearer auth, axios, react-hook-form + zod, qrcode.react, nginx security headers
- `ux.md` — React Router v7 data routers, react-hook-form + zod, notistack, MUI X data grid, RTK Query patterns

Each file pairs every best-practice claim with **at least two independent authoritative sources** (W3C, MDN, WebAIM, Deque, web.dev, official vendor docs) and carries confidence labels: `verified` (two or more independent sources), `partial` (normative source plus a single library / community doc), `unverified` (single source or inference; flagged for spec-input review).

**Tiered source floor (2026-07-24, closing the systemic slice of #469).** The two-source floor is the baseline for durable standards-level claims (W3C / WCAG / ARIA / MDN), where a second authoritative source already clears the triangulation gate's hallucination-risk bar. A **volatile external assertion** (an upstream version pin, a third-party library's API signature / default / runtime behaviour, or an external-tool default) that the spec lifts into a rule directing the `webview-ui-optimize` skill or `webview-ui-expert` agent toward a repo-external write or an audit `fail` is instead held to the **Release/dispatch tier** of three independent sources per `spec/claude/research-triangulate/` §Author-time assertions. This is a scoped escalation, not a blanket raise: it bites precisely on the volatile-pin class the triangulation gate exists for, and leaves the stable-standards majority on the two-source floor. The two resolved Open Questions in the spec (Emotion + Trusted Types; `contrastThreshold` under MUI v9 `colorSchemes`) are the worked examples, each carrying three-plus sources in the currency addenda of `security.md` and `accessibility.md`.

## Purpose

These files were authored as **input** to `spec/frontend/webview-ui-optimization/`, which the `webview-ui-optimize` skill operationalises (and which the `webview-ui-expert` agent uses for cross-file deep reviews of named frontend targets).

The `.audits/` location was chosen for proximity to the consuming spec, not because the material represents actionable findings for `claude-shared`. The `claude-shared` repository ships no browser-rendered frontend — these notes apply to consumer projects (`kamerplanter`, `kamerplanter-ha`, future webview-ui-bearing repos) that adopt the spec.

## What this folder is **not**

- Not a `spec-readiness-reviewer` report (see `.audits/spec-readiness/`).
- Not a `spec-drift-audit` report (see `.audits/spec-drift/`).
- Not a `portfolio-inflight-triage` finding set (see `.audits/portfolio-inflight/`).
- Not an action plan with severity ratings, deadlines, or owners.

If you are looking for actionable claude-shared audit findings, browse the other `.audits/<audit-type>/` folders instead.

## Lifecycle

- **Source of truth**: this folder. Updates land here as research material evolves.
- **Consumed by**: `spec/frontend/webview-ui-optimization/{en,de}.md` (when the spec lifts a rule from research into a normative requirement).
- **Refreshed**: when the underlying library versions in scope change materially (React major bump, Vite major bump, MUI major bump, …) or when WCAG / ARIA APG normative guidance updates.
