# Example 01 — React app, every skill installed, URL supplied

The happy path: all four third-party skills apply and are available, so
every strand runs and the delegated own rules stay off.

## Input prompt

> Run a thorough frontend audit of `frontend/`. The app runs at
> `http://localhost:5173`.

## Input files

`frontend/package.json` depends on `react` and `vite`; `src/` holds a
component tree and a router. `.claude/skills/` contains
`web-design-guidelines`, `react-best-practices` (frontmatter name
`vercel-react-best-practices`, the name the session lists), and
`playwright-cli`. `skills-lock.json` records the commits of the two
Vercel skills; `playwright-cli` came from `playwright-cli install
--skills`, so its version comes from `playwright-cli --version`. The
`frontend-design` plugin is installed. `playwright-cli --version`
prints a version and a browser is installed.

## Expected behaviour

1. Stack detected as React, client-side rendered; the server-side
   categories of `react-best-practices` are `not applicable`.
2. All four skills reported `available` with location and commit or
   version; no coverage gap.
3. The three third-party skills run first and all complete, so the
   F6, F8, and F10 rules and the generic webview-ui Accessibility and
   UX rules are delegated; no fallback, nothing uncovered.
4. The reviewers and the rendered strand run; `playwright-cli` opens
   with `--config=.audits/frontend-audit/evidence/<target-slug>/cli.config.json`,
   so snapshots and screenshots land there, and the session is closed. Rendered evidence
   is attached to findings, never the sole basis above Info.
5. The report header records the guidelines fetch time and SHA-256;
   every finding carries `source`; no third-party finding is Critical.
