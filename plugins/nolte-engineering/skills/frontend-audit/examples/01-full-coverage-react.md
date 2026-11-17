# Example 01 — React app, every skill installed, URL supplied

The happy path: all four third-party skills apply and are available, so
every strand runs and the delegated own rules stay off.

## Input prompt

> Run a thorough frontend audit of `frontend/`. The app runs at
> `http://localhost:5173`.

## Input files

`frontend/package.json` depends on `react` and `vite`; `src/` holds a
component tree and a router. `.claude/skills/` contains
`web-design-guidelines`, `vercel-react-best-practices`, and
`playwright-cli`; `skills-lock.json` records their commits. The
`frontend-design` plugin is installed. `playwright-cli --version`
prints a version and a browser is installed.

## Expected behaviour

1. Stack detected as React, client-side rendered; the server-side
   categories of `react-best-practices` are `not applicable`.
2. All four skills reported `available` with location and commit or
   version; no coverage gap.
3. The plan (step 4) lists the F6, F8, and F10 rules and the generic
   webview-ui Accessibility and UX rules as delegated; no fallback.
4. Code, static UI, and rendered strands run; rendered evidence is
   attached to findings, never the sole basis above Info.
5. The report header records the guidelines fetch time and SHA-256;
   every finding carries `source`; no third-party finding is Critical.
