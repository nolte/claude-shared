# Example 02 — React app, `vercel-react-best-practices` missing

A missing applicable skill becomes a coverage gap; the own reviewers
run unchanged.

## Input prompt

> Audit the frontend thoroughly, with the third-party skills.

## Input files

Same React app as Example 01, but the session lists no skill named
`vercel-react-best-practices` (project, user, or plugin). No URL is
given.

## Expected behaviour

1. `vercel-react-best-practices` reported `missing`; the report lists a
   coverage gap with the pinned command
   `npx skills add vercel-labs/agent-skills@<ref> --skill react-best-practices -a claude-code`.
   `web-design-guidelines` passes the lock check and the
   `frontend-design` plugin is recorded with its plugin version, so the
   header carries no setup Warning.
2. The skill runs no install command itself.
3. `frontend-code-reviewer` runs its full rule set, F6 included; its
   findings are the same as with the skill installed.
4. The rendered strand is a coverage gap ("no application URL
   supplied"); no app is started, and older run directories are removed
   when the new report is written.
