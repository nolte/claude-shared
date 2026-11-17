# Example 03 — Vue app, no network for the guidelines fetch

`not applicable` stays distinct from `missing`, and a failed rule
fetch never falls back to a remembered copy.

## Input prompt

> Ausführliches Frontend-Audit für `web/`, bitte.

## Input files

`web/package.json` depends on `vue` and `vite`; every third-party
skill is installed. The guidelines URL on `raw.githubusercontent.com`
is unreachable from the audit host.

## Expected behaviour

1. Response in German; report headings in English.
2. `react-best-practices` reported `not applicable` (no React or
   Next.js dependency), not as a gap.
3. `web-design-guidelines` fails its fetch: a coverage gap with the
   observed error; the generic webview-ui rules and the F8/F10
   delegated rules run as fallbacks. No cached guidelines are used.
4. `frontend-code-reviewer` reports the Vue framework as unsupported
   per `spec/frontend/source-code-review/` §Framework profiles; the
   report says so in its header.
5. `frontend-design` still runs as an advisory lens; its findings are
   Info and routed to `frontend-usability-optimizer`.
