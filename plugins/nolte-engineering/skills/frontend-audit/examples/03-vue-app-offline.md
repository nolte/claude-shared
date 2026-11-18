# Example 03 — Vue app, no network for the guidelines fetch

`not applicable` stays distinct from `missing`, and a failed rule
fetch never falls back to a remembered copy.

## Input prompt

> Ausführliches Frontend-Audit für `web/`, bitte.

## Input files

`web/package.json` depends on `vue` and `vite`; every third-party
skill is installed project-scoped and passes the lock check. The guidelines URL on `raw.githubusercontent.com`
is unreachable from the audit host.

## Expected behaviour

1. Response in German; report headings in English.
2. `vercel-react-best-practices` reported `not applicable` (no React or
   Next.js dependency), not as a gap.
3. `web-design-guidelines` fails its fetch: a coverage gap with the
   observed error, and no cached guidelines are used.
4. `webview-ui-expert` runs its rule set over the UI; the React-, MUI-,
   react-hook-form-, notistack-, and Recharts-specific rules are
   recorded as `not applicable`, not as a gap.
5. `frontend-code-reviewer` reports Vue as unsupported per
   `spec/frontend/source-code-review/` §Framework profiles; the report
   lists that as a coverage gap of the code strand.
6. `frontend-design` still runs as an advisory lens; its findings are
   Info and routed to `frontend-usability-optimizer`.
