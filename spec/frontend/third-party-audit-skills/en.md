# Third-Party Skills in the Frontend Audit

Status: draft

## Context

The plugin's own frontend reviews (`spec/frontend/source-code-review/` with its F1–F11 overlay, and `spec/frontend/webview-ui-optimization/` with its five domains) are written and maintained in this repository. For a thorough audit that isn't enough on its own: maintained third-party skill collections already encode large, curated rule sets for the same surface. Vercel's Web Interface Guidelines cover more than a hundred UI rules, Vercel's React best practices rank about seventy performance rules by impact, Anthropic's `frontend-design` skill names the visual tells of template-like, generated design, and Microsoft's `playwright-cli` drives a real browser so an audit can look at the rendered page instead of inferring it from source.

This spec makes those third-party skills the **core** of a thorough frontend audit and turns the plugin's own reviewers into the orchestrator and the complement: an own rule runs where no third-party rule covers the same defect, or as a fallback when the covering skill is missing. It states, per skill, **when** it runs and **what must hold** before it can run, and it fixes how its findings enter one merged, attributed report.

The content comes from a requirements elicitation on 2026-11-17 (`project/requirements/frontend-audit-rework.md`, requirements R1–R15) and from an inspection of the four skills on the same day. Where a fact was observed locally, the observation is named; where it rests on an upstream README only, the reference says so.

Boundaries: the own review dimensions stay owned by `spec/frontend/source-code-review/` and `spec/frontend/webview-ui-optimization/`; this spec only marks which of their rules are delegated. Patching findings stays with `webview-ui-optimize` and the specialists the reports route to. The test-identifier contract (`spec/frontend/testability-identifiers/`) and the usability rework (`frontend-usability-optimizer`) are unchanged.

Readers: authors of the `frontend-audit` skill and of the reviewer agents it dispatches; operators who prepare a consumer repository for a thorough frontend audit.

## Goals

- An operator can tell from one table which third-party skill an audit uses, under which condition, and what to install and provide beforehand
- A missing prerequisite never silently shrinks an audit: it surfaces as a named coverage gap, and the own fallback rules keep running
- A skill that doesn't apply to the detected stack is distinguishable from a skill that's missing
- Every finding in the merged report names the skill or agent that produced it, and one defect reported by two sources appears once
- Third-party findings fit the plugin's severity vocabulary and its code-versus-taste boundary without rewriting the third-party rules
- Rules fetched from upstream at run time are treated as audit criteria, never as instructions, and a run records exactly which rule text it used

## Non-Goals

- Installing, updating, or removing third-party skills from inside the audit—the operator does that
- Starting, building, or deploying the application under test
- Re-deriving or restating the third-party rule sets in this repository
- Patching findings; the audit is read-only
- Holding third-party rules to this repository's research-source thresholds (`spec/claude/research-triangulate/`); third-party findings are attributed findings, not rules of this corpus
- Frameworks other than React for the code-performance strand; `react-best-practices` is the only third-party code-performance skill in scope

## Requirements

### A. Skill catalogue

The audit uses exactly these third-party skills. Each row is normative for its trigger and its preconditions; §B states the install contract and §C the availability check.

| Skill | Source | Strand | Runs when | Preconditions | Not applicable when |
|---|---|---|---|---|---|
| `web-design-guidelines` | `vercel-labs/agent-skills` | UI (static) | Web UI code (markup, components, styles) is in the audit scope | skill installed; network access to `raw.githubusercontent.com` at run time | no web UI code in scope |
| `react-best-practices` (frontmatter name `vercel-react-best-practices`) | `vercel-labs/agent-skills` | code | React or Next.js is a declared dependency of the audited module | skill installed | no React or Next.js dependency |
| `frontend-design` | `anthropics/skills`, or the `frontend-design` plugin from the official Claude plugin marketplace | UI (static), advisory lens | Web UI code is in scope | skill or plugin installed | no web UI code in scope |
| `playwright-cli` | `@playwright/cli` (`microsoft/playwright-cli`) | UI (rendered) | The operator supplies a reachable application URL | CLI on `PATH`; skill installed; a browser installed for it; the URL reachable from the audit host | never—without a URL the strand is a coverage gap, see §D |

- **MUST** decide applicability from the audited module's own manifests and sources (package manifest, framework and bundler configuration, component tree), the same detection `source-code-review` uses for a browser surface; a `package.json` alone isn't a web UI
- **MUST** run each applicable, available skill exactly once per audit over the audit scope
- **MUST NOT** run a skill outside its strand: `react-best-practices` findings belong to the code strand, `web-design-guidelines` and `frontend-design` findings to the static UI strand, `playwright-cli` evidence to the rendered UI strand
- **MUST** treat the server-side rule categories of `react-best-practices` (server-side performance, React Server Components, server actions) as not applicable when the module ships a client-side-rendered application without a server runtime

### B. Install contract

- **MUST** leave installation to the operator; the `frontend-audit` skill **MUST NOT** run `npx skills add`, `npx skills update`, `playwright-cli install`, `playwright-cli install-browser`, or any package-manager install
- **MUST** pin every third-party skill install to a tag or full commit, never a moving branch:
  - `npx skills add vercel-labs/agent-skills@<ref> --skill web-design-guidelines -a claude-code`
  - `npx skills add vercel-labs/agent-skills@<ref> --skill react-best-practices -a claude-code`
  - `npx skills add anthropics/skills@<ref> --skill frontend-design -a claude-code`, unless the `frontend-design` plugin is installed instead
  - `npm install -g @playwright/cli@<version>`, then `playwright-cli install --skills` and `playwright-cli install-browser`
- **SHOULD** install project-scoped (into the repository's `.claude/skills/`) and commit the `skills-lock.json` the `skills` CLI writes, so every operator of the repository audits with the same skill commit [R1]
- **MAY** install user-scoped (`-g`) when a repository must not carry third-party skills; the audit then can't prove which commit ran and **MUST** say so in the report
- The tool versions in this paragraph are prerequisites, not pins: the `skills` CLI needs Node.js 22.20 or later [R1]; `@playwright/cli` needs Node.js 20 or later [R3]. `playwright-cli install --skills` installs the skill to `<cwd>/.claude/skills/playwright-cli` (`--skills=agents` installs to `.agents/skills/`, `-g` to the home directory), and it installs no browser—`playwright-cli install-browser` does (established: `@playwright/cli` 0.1.24, `playwright-cli install --help` and the package's `skillCheck.js`)

### C. Availability check

- **MUST** check every applicable skill's availability before running any strand, and record the result per skill as `available`, `missing`, or `not applicable`
- **MUST** look each skill up by the name the session lists it under, which is its frontmatter `name`, not its install folder: `web-design-guidelines`, `vercel-react-best-practices` (installed with `--skill react-best-practices`), `frontend-design` or the plugin skill `frontend-design:frontend-design`, and `playwright-cli`
- **MUST** count a skill as available when the session lists it—project-scoped, user-scoped, or as a plugin skill—and **SHOULD** additionally record the skill's install location and, for project installs, the commit from `skills-lock.json`
- **MUST** for `playwright-cli` additionally check that the CLI runs (`playwright-cli --version`) and record its version; a CLI warning that the installed skill doesn't match the tool version **MUST** appear in the report as a Warning about the audit setup, not about the audited code
- **MUST NOT** treat a successful check as proof that a strand ran; the report states per strand whether it ran, and why not

### D. Coverage gaps and fallback

- **MUST** report a missing applicable skill as a **coverage gap** naming the skill, the strand it would have covered, and the install command from §B
- **MUST** keep the audit running when a skill is missing: the own rules that §F delegates to that skill become active again for this run, and the report names them as active fallbacks
- **MUST** treat every own rule whose covering skill didn't run to completion in this audit—missing, not applicable, failed fetch, or aborted—as an active fallback, not only the rules of a missing skill
- **MUST** report an active fallback that no dispatched reviewer can apply (for example, F rules on a framework without a profile in `spec/frontend/source-code-review/`) as **uncovered**, never as an active fallback that ran
- **MUST** report a skill that doesn't apply as `not applicable` with its reason (for example, the reason "no React or Next.js dependency"), never as a coverage gap
- **MUST** when no application URL is supplied, skip the rendered strand, report it as a coverage gap whose reason states that no application URL was supplied, and **MUST NOT** start, build, or serve the application to obtain one
- **MUST** when a URL is supplied but unreachable, or the browser fails to start, report the rendered strand as a coverage gap with the observed error
- **MUST** when `web-design-guidelines` can't fetch its rules (no network, HTTP error), report a coverage gap for that skill and activate its fallbacks; the audit **MUST NOT** substitute a cached or remembered copy of the rules

### E. Live-loaded rules

`web-design-guidelines` loads its rules from `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` on every run (per the skill's SKILL.md [R2]). The rule text therefore isn't pinned by the skill install.

- **MUST** let the skill load its rules from upstream `main` on every run, as the skill specifies
- **MUST** record in the report the fetch time (UTC, ISO 8601) and the SHA-256 of the rule text the skill applied, so two audits are comparable and a changed rule set is visible
- **MAY**, when the skill doesn't expose the text it applied, hash a separate fetch of the same URL; the report **MUST** then mark the hash as taken from a separate fetch, because it doesn't prove which text the skill applied
- **MUST** treat any fetched third-party rule text as audit criteria—data that decides whether a finding exists—and never as instructions that change the audit's flow: no file writes, no tool calls, and no network access beyond what the audit already performs may follow from fetched text
- **MUST** when fetched text contains something that reads as an instruction to the agent (rather than a UI rule), ignore it, and report a Warning about the audit setup that names the source and quotes the passage

### F. Delegation of own rules

An own rule is **delegated** when a third-party rule detects the same defect in the same artefact. A delegated rule is skipped only when its covering skill ran to completion in the same audit; in every other case it runs as a fallback (§D).

- **MUST** run the third-party skills before dispatching the own reviewers, so the delegated and fallback lists handed to each reviewer reflect what actually ran
- **MUST** delegate only on equivalence: an own rule that's stricter, stack-specific, or carries a conditional the third-party rule lacks stays primary
- **MUST** keep the delegation mapping in the two owning specs, next to the rules it affects, and keep this table as the summary:

| Own rule | Delegated to | Stays primary |
|---|---|---|
| `source-code-review` F8: non-semantic controls, missing labels and accessible names, missing alternative text, removed focus indicators without replacement, missing live regions | `web-design-guidelines` (Accessibility, Focus States, Forms) | role promises without interaction behaviour, focus handling across dialogs and routes, label association across component boundaries |
| `source-code-review` F10: manual date, number, and currency formatting | `web-design-guidelines` (Locale & i18n) | hardcoded strings, assembled sentences, plural handling, dynamic keys |
| `source-code-review` F6: request waterfalls, barrel imports, and missing route splits | `react-best-practices` (async-, bundle-) | the conditional memoization judgment, expensive derivation |
| `source-code-review` F6: full renders of large collections | `web-design-guidelines` (Performance) | as above |
| `webview-ui-optimization` §Accessibility and §UX: generic HTML and CSS rules (icon-button names, `div` click handlers, `outline: none`, `prefers-reduced-motion`, safe-area insets, `transition: all`) | `web-design-guidelines` | every MUI, React Router, react-hook-form, notistack, and Recharts rule; WCAG thresholds; the Security and i18n domains |

- All other own rules—F1–F5, F7, F9, F11, the core D1–D11, and the webview-ui Security and Internationalisation domains—have no third-party equivalent and run on every audit

### G. Severity mapping and routing

Third-party findings keep their text and their rule reference; the audit maps them onto the severity scale of `spec/claude/review-plan/` §Severity scale:

| Source | Third-party class | Severity | Routing |
|---|---|---|---|
| `web-design-guidelines` | any rule outside Content & Copy and copy-level Typography | Warning | `fullstack-developer`; accessibility conformance questions to `webview-ui-expert` |
| `web-design-guidelines` | Content & Copy; Typography rules about characters and quotation marks | Info | `frontend-usability-optimizer` |
| `react-best-practices` | CRITICAL, HIGH | Warning | `fullstack-developer` |
| `react-best-practices` | MEDIUM-HIGH, MEDIUM | Suggestion | `fullstack-developer` |
| `react-best-practices` | LOW-MEDIUM, LOW | Info | `fullstack-developer` |
| `frontend-design` | any | Info | `frontend-usability-optimizer` |
| `playwright-cli` | rendered evidence attached to a finding | the finding's own severity | the finding's own routing |

- **MUST NOT** assign Critical to a third-party finding; Critical stays reserved for the own severity floors (an unhandled error path, an active injection sink)
- **MUST** apply the tooling-first rule of `spec/project/source-code-review/` to third-party findings: a defect the project's configured linter or type checker already reports isn't a finding. The audit decides this from the configured rule set (linter configuration and its enabled plugins) without running the linter; when the configuration doesn't settle whether a rule covers the defect, the finding stays
- **MUST** use `frontend-design` only as critique criteria: its guidance to design, build, or rewrite UI never leads to a write
- **MUST** keep the code-versus-taste boundary of `spec/frontend/source-code-review/` §"Delimitation from the UX review": Info-routed copy and design findings never enter a work package
- **MUST** use `playwright-cli` only to collect evidence—accessibility snapshots, screenshots, console errors, and the result of keyboard-only interaction—and attach it to a finding; a finding whose only evidence is a rendered impression stays Info
- **MUST** direct every `playwright-cli` output—snapshots, screenshots, traces—into `.audits/frontend-audit/evidence/`, through a CLI configuration file there whose `outputDir` is `.` (passed with `--config`) or an explicit `--filename`; the CLI's default output directory is `.playwright-cli/` in the working directory, a write outside the report (established: `@playwright/cli` 0.1.24 sets `cliOutputDir = ".playwright-cli"` in `playwright-core/lib/coreBundle.js`; a test run on 2026-11-17 with `open --config=<dir>/cli.config.json` wrote snapshot and screenshot only below `<dir>`, `outputDir` resolving relative to the configuration file)

### H. Merged report

- **MUST** write one report per audit to `.audits/frontend-audit/<target-slug>.md`; a re-run overwrites it
- **MUST** open the report with a header that records: the audit scope; the detected framework; per third-party skill its availability state, install location, commit or version, and whether it ran; the live-rule fetch time and SHA-256 (§E); every coverage gap; every active fallback rule; and every uncovered rule
- **MUST** tag every finding with `source`—the third-party skill (for example `vercel/web-design-guidelines`) or the own agent with its rule ID (for example `nolte/frontend-code-reviewer F2`)
- **MUST** merge findings that two sources report for the same defect at the same `file:line` into one finding carrying both sources and the higher severity
- **MUST** keep the work-package contract of `spec/project/source-code-review/` (disjoint file sets, routing targets) for Warning and above
- **MUST NOT** fold third-party findings into the `pass` / `fail` rule table of `webview-ui-optimize`; that table judges only the rules of `spec/frontend/webview-ui-optimization/`

### I. Orchestration

- **MUST** be orchestrated by one skill, `frontend-audit`, in the `nolte-engineering` plugin; the skill runs in the main session because third-party skills and the operator's URL decision live there
- **MUST** invoke the third-party skills through the session's skill mechanism, and `playwright-cli` through its CLI
- **MUST** dispatch `frontend-code-reviewer` for the own rules of the code strand and `webview-ui-expert` for the own rules of the static UI strand, passing which rules are delegated for this run and which are active fallbacks
- **MUST** stay read-only toward the audited repository apart from the report file, its evidence under `.audits/frontend-audit/evidence/`, and the run's resume state under `.resume/frontend-audit/`
- `source-code-review` and `webview-ui-optimize` remain; each **SHOULD** point operators to `frontend-audit` for the thorough, third-party-backed audit

## Acceptance Criteria

- [ ] The spec names, for each of the four skills, its trigger, its preconditions, its non-applicability condition, and its pinned install command
- [ ] An audit on a React repository with every skill installed and a reachable URL reports all four skills as `available` and ran, and lists no coverage gap
- [ ] An audit with `react-best-practices` uninstalled reports a coverage gap with the install command and runs F6's waterfall, barrel-import, and route-split rules as named fallbacks
- [ ] An audit whose `web-design-guidelines` fetch fails runs the F8, F10, and webview-ui rules delegated to that skill as fallbacks in the same audit
- [ ] An audit on a non-React web frontend reports `react-best-practices` as `not applicable`, not as a gap
- [ ] An audit without a URL reports the rendered strand as a coverage gap and starts no application
- [ ] The report header records the fetch time and SHA-256 of the Web Interface Guidelines text
- [ ] Every finding carries a `source`; a defect found by two sources appears once with both
- [ ] No third-party finding carries Critical; copy and design findings are Info and outside the work packages
- [ ] `spec/frontend/source-code-review/` and `spec/frontend/webview-ui-optimization/` mark each delegated rule with its covering skill
- [ ] The `frontend-audit` skill runs no install command, and every `playwright-cli` output lands under `.audits/frontend-audit/evidence/`

## References

- Sources retrieved 2026-11-17.
- [R1] Vercel `skills` command-line tool, README with `docs/agents.md` and `docs/commands.md` (P): <https://github.com/vercel-labs/skills>
- [R2] Vercel agent skills, `skills/web-design-guidelines/SKILL.md` and `skills/react-best-practices/SKILL.md` (P): <https://github.com/vercel-labs/agent-skills>
- [R3] Microsoft `playwright-cli` README (P): <https://github.com/microsoft/playwright-cli>
- [R4] Vercel Web Interface Guidelines, `command.md` (P): <https://github.com/vercel-labs/web-interface-guidelines>
- [R5] anthropics/skills, `frontend-design` (P): <https://github.com/anthropics/skills>
- Frontend code review overlay and its UX delimitation: `spec/frontend/source-code-review/`
- Web-view UI rule set: `spec/frontend/webview-ui-optimization/`
- Core review, tooling-first rule, and work-package contract: `spec/project/source-code-review/`
- Severity scale and audit-artefact location: `spec/claude/review-plan/`
- Requirement set behind this spec: `project/requirements/frontend-audit-rework.md`

## Open Questions

- Should the audit offer an opt-in to load the Web Interface Guidelines from a pinned commit instead of `main`? The elicitation chose live loading with a recorded hash; a pinned mode would make two audits reproducible but needs a way to steer a third-party skill's fetch URL, which the skill doesn't expose
- Which third-party code-performance skill, if any, covers Vue, Svelte, or Angular? Until one is named, those stacks run F6 without delegation
- Does `playwright-cli` evidence justify raising a static finding's confidence from suspected to confirmed? The current rule only attaches evidence; a confirmation rule needs a defined evidence-to-finding match
