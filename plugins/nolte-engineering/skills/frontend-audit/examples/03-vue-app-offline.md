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
2. `vercel-react-best-practices` reported `not applicable` (no React or
   Next.js dependency), not as a gap.
3. `web-design-guidelines` fails its fetch: a coverage gap with the
   observed error, and no cached guidelines are used. It didn't run to
   completion, so every rule delegated to it is a fallback.
4. `webview-ui-expert` runs the generic webview-ui Accessibility and UX
   rules as active fallbacks.
5. `frontend-code-reviewer` reports Vue as unsupported per
   `spec/frontend/source-code-review/` §Framework profiles, so the F6,
   F8, and F10 fallbacks have no reviewer that can apply them: the
   header lists them as **uncovered**, not as fallbacks that ran.
6. `frontend-design` still runs as an advisory lens; its findings are
   Info and routed to `frontend-usability-optimizer`.
