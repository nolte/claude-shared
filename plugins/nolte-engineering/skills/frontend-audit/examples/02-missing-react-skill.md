# Example 02 — React app, `react-best-practices` missing

A missing applicable skill becomes a coverage gap and reactivates the
own rules it covers.

## Input prompt

> Audit the frontend thoroughly, with the third-party skills.

## Input files

Same React app as Example 01, but the session lists no skill named
`vercel-react-best-practices` (project, user, or plugin). No URL is
given.

## Expected behaviour

1. `react-best-practices` reported `missing`; the report lists a
   coverage gap with the pinned command
   `npx skills add vercel-labs/agent-skills@<ref> --skill react-best-practices -a claude-code`.
2. The skill runs no install command itself.
3. `web-design-guidelines` runs to completion, so full renders of
   large collections stay delegated to it; `frontend-code-reviewer` is
   dispatched with F6's waterfall, barrel-import, and route-split rules
   as active fallbacks, and the header lists them.
4. The rendered strand is a coverage gap ("no application URL
   supplied"); no app is started.
