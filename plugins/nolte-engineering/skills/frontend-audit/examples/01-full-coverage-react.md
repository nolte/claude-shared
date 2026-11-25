# Example 01 — React app, every skill installed, URL supplied

The happy path: all four third-party skills apply and are available, so
every strand runs beside the own reviewers and overlap is merged.

## Input prompt

> Run a thorough frontend audit of `frontend/`. The app runs at
> `http://localhost:5173`.

## Input files

`frontend/package.json` depends on `react` and `vite`; `src/` holds a
component tree and a router. `.claude/skills/` contains
`web-design-guidelines`, `vercel-react-best-practices`, and
`playwright-cli`. `skills-lock.json` records the pinned `ref` and the commit of
each of the two Vercel skills; `playwright-cli` came from `playwright-cli install
--skills`, so its version comes from `playwright-cli --version`. The
`frontend-design` plugin is installed. `playwright-cli --version`
prints a version and a browser is installed.

## Expected behaviour

1. Stack detected as React, client-side rendered; findings in the
   server-side categories of `vercel-react-best-practices` are dropped.
2. All four skills reported `available` with location, `ref` and commit
   or version; the two Vercel skills pass the lock check and the
   `frontend-design` plugin is recorded with its plugin version, so the
   plan asks for no extra confirmation and the header carries no setup
   Warning; no coverage gap.
3. The third-party skills run, and both own reviewers run their full
   rule sets alongside them.
4. `playwright-cli` opens with the `cli.config.json` in the run
   directory `.audits/frontend-audit/evidence/<target-slug>/<run-id>/`, so
   snapshots and screenshots land there, and the session is closed.
   Rendered evidence is attached to findings, never the sole basis
   above Info.
5. A missing `alt` attribute that `web-design-guidelines` and
   `frontend-code-reviewer` (F8) both report at `Gallery.tsx:42` appears
   once, with both sources and the reviewer's implementation proposal.
6. The report header records per skill the lock check result, the
   `frontend-design` plugin version, and the guidelines fetch time and
   SHA-256;
   every finding carries `source`; no finding whose only source is a
   third-party skill is Critical. Only after the report is written are
   older run directories of this target removed.
