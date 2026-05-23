---
title: webview-ui-optimize
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# webview-ui-optimize

_Audits a browser-rendered frontend against the canonical-language file under spec/frontend/webview-ui-optimization/ and, with per-item user approval, patches findings across five domains: Performance, Security, Accessibility (WCAG 2.2 AA), Internationalisation, and UX. Three operations: `audit` (written to `.audits/webview-ui-optimize/`), `patch` (one finding at a time), `expert-review` (dispatches `webview-ui-expert`). Invoke when the user asks to \"audit the frontend\", \"check the UI against the webview-ui spec\", \"optimise for performance / a11y / i18n / UX / security\", \"fix the CSP\", \"wire up vitest-axe\", or equivalent German-language requests. Don't use for brand-design decisions, audience artefact (`audience-identify`), prose linting (`prose-vale-curator`), CVE audits (`dependency-audit`), or release-pipeline (`release-automation`). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 3 Design (`design`)
- **Tags:** `audit`, `scaffolding`
- **Source:** [skills/webview-ui-optimize/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/webview-ui-optimize/SKILL.md)

---

## Web-View UI Optimize

Operationalises `spec/frontend/webview-ui-optimization/<canonical_language>.md` inside the current repository. The skill audits a target frontend against the five-domain rule set (Performance, Security, Accessibility, Internationalisation, UX) and — with explicit per-item user consent — patches one finding at a time. For cross-file reasoning that goes beyond a single rule (a CSP rewrite plus its Vite + Emotion + nginx pipeline; an a11y review of a complex feature), the skill dispatches the `webview-ui-expert` agent for a read-only deep review whose output the skill then feeds back into the per-item approval loop.

When the spec isn't present in the target repository, fall back to the copy shipped by the `nolte-shared` plugin (read it at runtime from the plugin install path). Never invent rules that don't appear in the spec.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "Frontend gegen die Spec prüfen"
- "WebView optimieren"
- "a11y-Audit"

### Rationale (why a skill, not just an agent)

Per `spec/claude/skill-vs-agent/` §Decision dimensions, this capability is a skill because:

- **Mid-flow user approval is the contract.** Each finding's patch — a CSP header, a `dangerouslySetInnerHTML` quarantine, a focus-on-route-change hook, an `Intl.NumberFormat` migration, a snackbar-variant change — is written only with explicit user confirmation. The frontend is the user's voice in the product and individual changes can ripple visibly.
- **Persistent on-disk artefacts that flow back into the main conversation.** The per-domain audit table, the planned-edit list, and the post-edit verification (vitest-axe smoke, Mozilla Observatory check) all surface as files under `.audits/webview-ui-optimize/` so the user can re-read and the next session can resume.
- **Orchestrator pattern.** The skill dispatches `webview-ui-expert` for deep cross-file review, dispatches `dependency-audit` for the supply-chain MUSTs, and routes to `quality-gate` for the post-patch lint/type/test sweep. Per `spec/claude/skill-vs-agent/` §Hybrid pattern, the orchestrator is always a skill.
- **Precedent.** Follows the audit + patch shape of `mkdocs-structure-apply`, `readme-structure-apply`, `docs-audience-tracks-apply`, `project-structure-apply`; portfolio-wide consistency favours the same artefact type.
- **Counter-dimension considered.** A pure agent could specialise on one domain (a11y or security alone), but the load-bearing dimension is the per-rule approval dialogue across five interleaved domains; skill wins. The agent role is reserved for the read-only deep-review subtask.

### User-language policy

Detect the user's language from their message and respond in it. The audit-table content (rule IDs, file paths, MUST/SHOULD verbatim quotes) stays in the spec's canonical language (English by default per `spec/.spec-config.yml`); prose summaries and approval prompts follow the user's language. Code, ESLint rule names, HTTP header strings, ARIA attribute names, and other technical identifiers stay in English regardless.

### Tool selection rationale

Declared tools: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`.

- `Read` / `Glob` / `Grep` for repository inspection: `package.json`, `vite.config.ts`, `index.html`, `tsconfig*.json`, `eslint.config.*`, `nginx*.conf` / `*.inc`, `src/**/*.{ts,tsx,css}`, every `*.json` translation file, every `.audits/webview-ui-expert/<domain>.md` source-of-truth research note.
- `Write` to land a new audit report under `.audits/webview-ui-optimize/<timestamp>.md`; `Edit` to apply individual approved patches to existing files. Never overwrite a hand-edited audit; append a new timestamped report instead.
- `Bash` for read-only verifications: `npm ls`, `npx vitest run <pattern>` for a targeted axe-smoke, `curl -sI` for header verification when the operator points at a deployed origin, `grep -R 'VITE_' dist/` for env-var leakage post-build, `node -e "console.log(import('dompurify'))"` style sanity checks. No destructive bash, no `npm audit` invocation (that belongs to `dependency-audit`).
- No `WebFetch` / `WebSearch`: the spec and its `.audits/webview-ui-expert/<domain>.md` research notes are the only sources of truth. Vendor-doc lookups during an audit indicate a missing entry in the research notes and should surface as a `# TODO` rather than be auto-fetched.

### Preconditions

Before doing anything:

1. Confirm the working directory is a git repository (`git rev-parse --is-inside-work-tree`).
2. Locate `spec/frontend/webview-ui-optimization/<canonical_language>.md` — either in the target repo or via the `nolte-shared` plugin. If neither is reachable, stop and ask the user which spec source to use.
3. Detect the target frontend module:
   - default: the repository root.
   - monorepo with a `frontend/` or `src/frontend/` subroot: scope to that subroot.
   - the user may name a different subroot explicitly.
4. Confirm the stack matches the spec's reference: `package.json` declares `react ^19`, `vite ^8`, `@mui/material ^9`, `@reduxjs/toolkit`, `react-router-dom ^7`, `react-hook-form`, `react-i18next`, `notistack`. Mark divergences (`react ^18`, no MUI, etc.) in the audit's pre-state and continue — most rules still apply, but the stack-specific MUSTs degrade to SHOULDs against the actual dependency.
5. Locate the `.audits/webview-ui-expert/` research directory. If the directory doesn't exist (a green-field consumer), prompt the user to copy the bundled research notes from the `nolte-shared` plugin before continuing; per-rule audit findings reference those notes.
6. Check for uncommitted changes touching `package.json`, `vite.config.ts`, `index.html`, `eslint.config.*`, `nginx*.conf*`, or `src/`. If any are dirty, report and ask whether to stash, commit, or abort — never overwrite uncommitted work.

### Operations

#### 1. `audit` (read-only)

Walk through every MUST and SHOULD in the spec's `## Requirements` section, classify each rule as `pass`, `fail`, `partial`, or `n/a`. Group findings by domain (Performance, Security, Accessibility, Internationalisation, UX, Cross-cutting verification). Produce a single timestamped report under `.audits/webview-ui-optimize/<YYYY-MM-DDThhmm>.md` with this shape:

```
## Web-View UI Audit — <repo>@<branch> — <iso-timestamp>

### Pre-state
- Target subroot: <path>
- Stack matches spec reference: yes | partial (<deltas>)
- Research notes resolved at: <path>

### Summary
| Domain | Rules | Pass | Fail | Partial | n/a |
|---|---|---|---|---|---|
| Performance | … | … | … | … | … |
| Security | … | … | … | … | … |
| Accessibility | … | … | … | … | … |
| Internationalisation | … | … | … | … | … |
| UX / Native-feel | … | … | … | … | … |

### Findings
#### Performance
| Rule | Status | Evidence | Spec anchor |
|---|---|---|---|
| LCP/INP/CLS budgets met (p75) | fail | no CrUX/RUM wiring detected | spec §Performance › Core-Web-Vitals targets |
| Viewport meta present and well-formed | pass | `index.html:5` | spec §Performance › Core-Web-Vitals targets |
| … | … | … | … |

#### Security
…

#### Accessibility
…

#### Internationalisation
…

#### UX / Native-feel
…

#### Cross-cutting verification
…

### Triage recommendations
- Critical (security MUSTs failing): <list>
- High (a11y MUSTs failing): <list>
- Medium (performance MUSTs failing): <list>
- Low (SHOULDs failing): <list>

### Caller follow-ups
- For each critical or high finding, run `patch <rule-id>` to apply the fix with per-item approval.
- For findings that need cross-file reasoning (CSP, focus-management hooks, MUI-X locale wiring), run `expert-review <file-or-component>`.
- Run `quality-gate` after the patch sweep to verify lint/type/test.
- Run `dependency-audit` for supply-chain MUSTs (npm audit + license).
```

Audit is read-only — never autofix during audit. Each row's `Evidence` cell points at a concrete file:line or names the absent artefact ("no `nginx-security-headers.inc`"); never produce a finding without evidence.

#### 2. `patch <rule-id>` (additive: one finding at a time)

For a single rule whose audit status is `fail` or `partial`, propose the exact change and ask the user to approve it before writing. Don't bundle unrelated rules into one approval step. Patterns:

- **Performance MUSTs** (e.g. `font-display: swap`, deep MUI icon imports, `loading="lazy"` on `<img>`, `Cache-Control` headers): propose the smallest change that closes the finding; show the before / after for the affected file(s).
- **Security MUSTs** (CSP, source-map suppression, `rel="noopener noreferrer"`, `redux-persist` whitelist tightening): propose header / config edits or ESLint rule additions; for CSP changes name every chunk-source affected so the user understands the blast radius.
- **Accessibility MUSTs** (`aria-invalid` triple on forms, focus-on-route-change hook, `contrastThreshold: 4.5`, skip-link): propose the JSX / hook / theme change and, where applicable, the matching `vitest-axe` smoke test.
- **i18n MUSTs** (locale URL prefix, `Intl.NumberFormat` migration, `<Trans>` over `dangerouslySetInnerHTML`, MUI-X picker locale lockstep): propose the source edit AND the translation-file shape; for plural keys, propose the JSON-v4 suffix grammar.
- **UX MUSTs** (`<ScrollRestoration/>` mount, theme-token use, `colorSchemes` + `cssVariables` migration, snackbar `maxSnack` cap): propose the layout / theme / provider edit; for snackbar discipline, show the resulting variant matrix.

After every successful write, the skill verifies the patch closed the finding:

- Re-run the audit rule against the patched file(s) only; if the rule now passes, mark `fixed`. If `partial` remains, surface the residual evidence.
- For a11y-touching patches, dispatch `vitest-axe` against the patched component(s) (`npx vitest run <pattern>`) and surface the violation count.
- Never claim "verified" without re-running the rule.

#### 3. `expert-review <target>` (deep read-only)

For a named file, route module, or feature whose findings cross several spec rules (e.g. "the auth flow", "the dashboard chart", "the i18n bootstrap"), dispatch the `webview-ui-expert` agent. The agent receives:

- The target path (or feature description).
- The current audit report's findings for that target.
- The relevant research notes from `.audits/webview-ui-expert/<domain>.md`.

The agent returns a structured deep-review report (see `agents/webview-ui-expert.md` §Output shape) which the skill writes verbatim under `.audits/webview-ui-optimize/expert-review-<target>-<iso-timestamp>.md`, then summarises in the conversation and queues the resulting findings into the patch backlog.

### Output contract

The skill returns to the user, in this order:

1. **Operation + target**: which operation ran (`audit` / `patch <rule-id>` / `expert-review <target>`), the resolved target subroot, the spec source (local repo vs plugin fallback), the absolute path of any audit or expert-review artefact written.
2. **Pre-state**: brief summary of what was found (stack-match status, dirty-file warnings, missing research notes).
3. **Audit findings** (for `audit`): the summary table plus the per-domain Findings tables, with one row per Acceptance-Criteria-equivalent rule.
4. **Planned edits** (for `patch`): the single change being proposed, with rationale linking back to the spec line and the research-notes anchor.
5. **Approval gate** (for `patch`): explicit user-decision point; nothing is written until the user confirms.
6. **Applied edits** (after approval): the absolute path(s) of the written file(s), plus the post-write verification result.
7. **Caller follow-ups**: dispatch `quality-gate` after a patch sweep, dispatch `dependency-audit` for supply-chain MUSTs, route to `prose-vale-curator` if any docs strings were rewritten, open the PR via `pull-request-create`.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/webview-ui-optimize/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

1. **Never** apply more than one rule's patch per approval step; bundling silently shifts the user's attention away from the change they're consenting to.
2. **Never** autofix during `audit`; the audit is read-only by contract.
3. **Never** claim a CSP / security header change is verified without surfacing the post-change Mozilla HTTP Observatory grade (or a clearly labelled "operator must re-verify against the deployed origin").
4. **Never** mark an a11y finding as fixed without re-running `vitest-axe` against the patched component(s) and surfacing the violation count.
5. **Never** propose a patch that contradicts a higher-precedence rule in another domain (e.g. an Emotion-style fix that breaks the strict-CSP nonce wiring); when domains collide, surface the conflict and stop until the user decides.
6. **Never** bypass the spec — every patch's rationale must cite the exact `spec/frontend/webview-ui-optimization/<canonical_language>.md` line.
7. **Always** read the spec at runtime: prefer the target repo's `spec/frontend/webview-ui-optimization/<canonical_language>.md`; fall back to the copy shipped by the `nolte-shared` plugin only when the target repo lacks one.
8. **Always** keep the research notes under `.audits/webview-ui-expert/<domain>.md` available; a finding without a research-note anchor (and the ≥ 2 independent authoritative sources behind it) is not a finding.

### Sources

- `spec/frontend/webview-ui-optimization/` — the canonical authoritative spec this skill operationalises.
- `.audits/webview-ui-expert/<domain>.md` — the per-domain research notes that anchor every normative rule to ≥ 2 independent authoritative sources.
- `spec/project/prose-style/` — the Vale rule set that the audit prose and the patch rationales should ultimately pass (delegated to `prose-vale-curator`).
- `spec/claude/skill-vs-agent/` — the skill-vs-agent decision dimensions that justify this artefact as a skill, with the `webview-ui-expert` agent as the deep-review specialist.
- `agents/webview-ui-expert.md` — the read-only deep-review agent dispatched by the `expert-review` operation.
