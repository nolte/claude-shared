---
name: portfolio-audit
description: "Audits, renders, and bootstraps the cross-repository capability portfolio across `nolte/*` per `spec/portfolio/portfolio-management/`. Audit dispatches portfolio-manifest-collector agent for read-only inventory collection, then detects capability duplicates, surfaces gaps, verifies tech-stack consistency per `spec/portfolio/tech-stack/`, and writes a Findings-Report under `.audits/portfolio/` using Critical / Warning / Suggestion / Info severities. Render regenerates the aggregated inventory under the per-language docs/ portfolio subtree. Bootstrap creates a repository's first `project/portfolio.yml`. Invoke when the user asks to \"audit the portfolio\", \"check for portfolio duplicates\", \"render the portfolio inventory\", or equivalent German-language requests. Don't use to consolidate duplicates (operator opens cross-repo PRs), to author new capabilities, or for per-repo tech_stack capture or refresh (use tech-stack-capture). Supports resume on re-invocation per `spec/claude/resumable-work/`."
tags: [audit]
phase: quality
summary: "Audits, renders, and bootstraps the cross-repository capability portfolio across nolte/*."
summary_de: "Auditiert, rendert und bootstrappt das cross-repo Capability-Portfolio über nolte/*."
use_when:
  - "you want to audit the portfolio for duplicates or gaps"
  - "you want to render the aggregated portfolio inventory under docs/"
  - "you want to bootstrap a repository's first project/portfolio.yml"
dont_use_when:
  - situation: "You want per-repo tech-stack capture or refresh"
    alternative: tech-stack-capture
  - situation: "You want in-flight state triage (stalled PRs, issues, review threads) rather than capability allocation"
    alternative: portfolio-inflight-triage
see_also:
  - tech-stack-capture
  - portfolio-manifest-collector
  - portfolio-inflight-triage
resumable: true
---

# Portfolio Audit

Implements the `spec/portfolio/portfolio-management/` mechanics as a Claude Code skill in the `nolte-shared` plugin, plus the discovery half of `spec/portfolio/tech-stack-discovery/`. Four operations: **Audit** (the primary path, the reason the spec exists), **Render** (regenerate the docs-site portfolio inventory), **Bootstrap** (help a single repository author its first `project/portfolio.yml`), and **Discover tech stack** (run the tech-stack-discovery methodology against a single repository or across the portfolio).

## Why this is one skill, not three

`spec/claude/skill-management/` §"Coherent units" generally favors one operation per skill. This skill bundles three operations because they share the same inputs (the per-repository `project/portfolio.yml` manifests collected via the GitHub API), the same domain vocabulary (capabilities, audiences, peers, ownership, portfolio scope), and the same output conventions (`review-plan`-format severities, the rendered inventory under `docs/<lang>/portfolio/`). Splitting them upfront would force three skills to re-implement the same manifest-collection plumbing and cross-validate the same vocabulary.

If any of the three operations grows complex enough to need its own dedicated review surface — for example if "Render" sprouts a templating engine or "Bootstrap" needs an interactive multi-turn audience-mapping flow — split it into a sibling skill (`portfolio-inventory-render`, `portfolio-bootstrap`) at that point, leaving "Audit" as the canonical `portfolio-audit`. The three operations below are deliberately structured to be split-friendly: each has its own preconditions, its own output artefact, and no shared mid-flow state.

## Why this is a skill, not an agent

- **Mid-flow user confirmation on duplicate-resolution choices.** The Audit operation surfaces duplicate candidates and gap-class findings; deciding which repository owns a contested capability, or whether a copy-paste smell warrants a new shared capability, is a per-step user dialogue. An agent's fire-and-forget shape would lose those checkpoints.
- **Persistent on-disk artefacts as deliverables.** Audit writes `.audits/portfolio/<YYYY-MM-DD>.md`. Render writes `docs/<lang>/portfolio/*.md`. Bootstrap writes `project/portfolio.yml` in the consuming repository. Skills own persistent state.
- **Context-window-protective manifest collection via agent.** Audit delegates raw manifest collection to the `portfolio-manifest-collector` agent, which fetches and parses each Portfolio-Member's `project/portfolio.yml` via `gh api` and returns a pre-reduced structured summary (declared capabilities, audiences, peer references). Raw YAML is discarded inside the agent before it returns, so the main conversation receives only the synthesised inventory report rather than the full raw manifest dump.
- **Counter-dimension considered**: a tool-restricted agent could perform the Audit operation cleanly in isolation, but Render and Bootstrap both write user-visible files in the active checkout and benefit from staying in the main conversation; bundling all three behind one skill is simpler than splitting Audit out.

## User-language policy

Detect the user's language and respond in it. Manifest content (`project/portfolio.yml`), the rendered inventory under `docs/<lang>/portfolio/`, and the Findings-Report under `.audits/portfolio/` follow the canonical conventions of their target files: YAML stays English, rendered docs follow the existing per-language docs-tree, the Findings-Report uses English for headings (per `review-plan`) but the body may be written in the user's language.

## Detection: am I in the right repository?

This skill operates in two roles depending on the active repository:

- **Inside `claude-shared`** (where this skill itself lives, plus the rendered portfolio inventory and the audit-history `.audits/portfolio/`): all three operations run end-to-end. Detection: presence of `.claude-plugin/plugin.json` AND a `spec/portfolio/portfolio-management/` directory.
- **Inside any other Portfolio-Member repository** (the typical adopter): only the **Bootstrap** operation runs end-to-end; Audit and Render require `claude-shared` access (the `.audits/portfolio/` and `docs/<lang>/portfolio/` write paths live there). Detection: any `nolte/*` repository that lacks the spec but accepts a `project/portfolio.yml`.

If the active repository is neither, stop and ask the user whether to switch to `claude-shared` for Audit / Render or to a Portfolio-Member repository for Bootstrap.

## Operations

Four dispatchable operations. The full step-by-step runbook for each — including the exact `gh api` calls, the four audit checks with their severity grammar, the tech-stack-consistency classification table, the snapshot schema, and the spec anchors — lives in `references/operations.md`. **Read `references/operations.md` when you execute any operation below**; the summaries here are routing only.

- **Audit** is read-only and never mutates a Portfolio-Member, consolidates duplicates, or opens cross-repo PRs.
- **Render** authors only `portfolio/aggregate.yml`; the generator owns the rendered pages.
- **Bootstrap** writes `project/portfolio.yml` only in the active checkout and never edits mission/roadmap/audience artefacts.
- **Discover tech stack** is read-only and never amends the baseline spec.

### 1. Audit (primary path)

Runs the cross-repository capability audit per `spec/portfolio/portfolio-management/` §Portfolio audit: detect the Portfolio-Member set via the GitHub API, dispatch `portfolio-manifest-collector` (Agent) for manifest collection, run the four checks (manifest presence, manifest validity, cross-repository duplicate detection, gap analysis) plus tech-stack consistency per `spec/portfolio/tech-stack/` §Portfolio audit integration, then write the Findings-Report at `.audits/portfolio/<YYYY-MM-DD>.md` (sections `## Scope` / `## Summary` / `## Findings` / `## Tech stack` / `## Processing log`, canonical severities, spec-cited findings) per `spec/claude/review-plan/`. See `references/operations.md` §Audit for the full runbook.

### 2. Render (regenerate the inventory docs)

Regenerates the aggregated portfolio inventory under `claude-shared/docs/<lang>/portfolio/` via the two-stage deterministic mechanism: assemble the committed snapshot `portfolio/aggregate.yml`, then run `task docs:portfolio` (`scripts/docs/gen_portfolio.py`) which renders the per-language pages as a pure function of that snapshot. Verify with `task docs` (mkdocs `--strict`) and a portfolio-subtree `git diff --exit-code`. See `references/operations.md` §Render for the full runbook.

### 3. Bootstrap (initial portfolio.yml for one repository)

Helps a single Portfolio-Member repository author its first `project/portfolio.yml` interactively: confirm the candidate, read the mission / audience / roadmap context, walk capability identification (name, description, audience, status, rationale, optional peers/since), then write and YAML-validate the file. See `references/operations.md` §Bootstrap for the full runbook.

### 4. Discover tech stack

Runs the tech-stack-discovery methodology from `spec/portfolio/tech-stack-discovery/` against one repository or the whole portfolio: read the canonical detection sources, extract the per-layer signal, cross-validate against the baseline in `spec/portfolio/tech-stack/` (in-baseline / drift / net-new), then persist under `.audits/tech-stack/<YYYY-Q<n>>.md` in the `review-plan` section vocabulary and severity grammar. See `references/operations.md` §Discover tech stack for the full runbook.

## Examples

- Read `examples/01-audit-detects-duplicate.md` when the audit surfaces a duplicate capability across portfolio members.
- Read `examples/02-render-inventory-idempotent.md` when re-running the inventory render to verify idempotency.
- Read `examples/03-bootstrap-new-member.md` when bootstrapping a new portfolio member's `project/portfolio.yml` for the first time.

## Gotchas

- **Bootstrap blocks if `tech-stack-capture` hasn't run yet**: Bootstrap reads `project/mission.md` and the audience artefact as inputs; if neither exists in the target repository, Bootstrap has nothing to derive capabilities from — route the user to `mission-define` and `audience-identify` first rather than proceeding with empty fields.
- **`gh api` rate limits can stall portfolio-wide manifest collection**: fetching `project/portfolio.yml` for every public non-archived repository in one call sequence can exhaust the GitHub API rate limit for large portfolios — spread calls across turns or check `gh api rate_limit` before starting a full-portfolio Audit.
- **Findings-Report and rendered inventory must land in `claude-shared`, not in the calling repo**: writing `.audits/portfolio/` or `docs/<lang>/portfolio/` from a non-`claude-shared` working directory is a structural error; confirm `cwd` resolves to the `claude-shared` checkout before any Audit or Render write.

## Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/portfolio-audit/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

## Hard rules

- Never modify a Portfolio-Member repository's `project/portfolio.yml` from this skill; only Bootstrap writes it on first authoring, and only inside the active checkout. Cross-repository edits go through ordinary PR flows in the target repository, not through this skill.
- Never consolidate duplicate capabilities automatically, never mark a capability `status: deprecated` from the audit side, never open a PR against another Portfolio-Member repository. The audit identifies and reports; the operator acts.
- Never use a severity outside the canonical four (`Critical` / `Warning` / `Suggestion` / `Info`). ALL-CAPS variants (`BLOCKER`, `WARNING`, `SUGGESTION`, `INFO`) are forbidden per `spec/claude/review-plan/` §Severity scale and are themselves a `review-plan` violation if they appear in the Findings-Report.
- Never fetch `project/portfolio.yml` from repositories outside the resolved Portfolio-Member set. Scope drift here is a confidentiality risk — private repositories or non-`nolte/*` forks must never enter the manifest collection.
- Never write the Findings-Report or the rendered inventory outside the `claude-shared` repository. Both artefacts live in `claude-shared`; misrouted writes are a structural error, not a typo.
- Never hand-write or hand-edit the rendered `docs/<lang>/portfolio/*.md` pages from the Render operation. Render authors only the `portfolio/aggregate.yml` snapshot; the deterministic generator `scripts/docs/gen_portfolio.py` (via `task docs:portfolio`) owns the pages. Editing the rendered pages directly breaks the CI freshness gate, which diffs them against a fresh generator run.
- Never bypass `continuous-improvement` for routing portfolio findings. The audit emits the report; the triage and specialist-dispatch live in `continuous-improvement`'s loop.
- Never invent a `mission` quote or an `audience` entry for the rendered inventory; quote verbatim from the source files, and if a Portfolio-Member repository lacks a mission or audience artefact, render a placeholder noting the gap and emit a `Warning` finding in the next Audit run.
- When `spec/portfolio/portfolio-management/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
- Always render the portfolio inventory symmetrically across every language tree configured in `spec/.spec-config.yml`'s `languages` list, per `spec/project/docs-multilingual-authoring/` §Authoring protocol. A render that writes `docs/<canonical_language>/portfolio/index.md` without writing the counterpart in every other configured language tree in the same operation is a violation. Verbatim quotes (mission statement, audience entries) are emitted as-is in every language tree per the no-invention rule above; surrounding section titles, table headers, and chrome are localised.
