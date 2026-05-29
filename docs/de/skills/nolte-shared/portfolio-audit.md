---
title: portfolio-audit
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# portfolio-audit

> Auditiert, rendert und bootstrappt das cross-repo Capability-Portfolio über nolte/*.

_Audits, renders, and bootstraps the cross-repository capability portfolio across `nolte/*` per `spec/portfolio/portfolio-management/`. Audit dispatches portfolio-manifest-collector agent for read-only inventory collection, then detects capability duplicates, surfaces gaps (broken peer references, spec-demanded gaps, copy-paste smells), and writes a Findings-Report under `.audits/portfolio/` with Critical / Warning / Suggestion / Info severities. Render regenerates the aggregated inventory under the per-language docs/ portfolio subtree. Bootstrap creates a repository's first `project/portfolio.yml`. Invoke when the user asks to \"audit the portfolio\", \"check for portfolio duplicates\", \"render the portfolio inventory\", or equivalent German-language requests. Don't use to consolidate duplicates (operator opens cross-repo PRs), to author new capabilities, or for per-repo tech_stack capture or refresh (use tech-stack-capture). Supports resume on re-invocation per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `audit`
- **Quelle:** [skills/portfolio-audit/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/portfolio-audit/SKILL.md)

## Anwenden wenn

- you want to audit the portfolio for duplicates or gaps
- you want to render the aggregated portfolio inventory under docs/
- you want to bootstrap a repository's first project/portfolio.yml

## Nicht anwenden wenn

- **You want per-repo tech-stack capture or refresh** → [`tech-stack-capture`](tech-stack-capture.md)

## Siehe auch

- [`tech-stack-capture`](tech-stack-capture.md)
- [`portfolio-manifest-collector`](../../agents/nolte-shared/portfolio-manifest-collector.md)

---

## Portfolio Audit

Implements the `spec/portfolio/portfolio-management/` mechanics as a Claude Code skill in the `nolte-shared` plugin, plus the discovery half of `spec/portfolio/tech-stack-discovery/`. Four operations: **Audit** (the primary path, the reason the spec exists), **Render** (regenerate the docs-site portfolio inventory), **Bootstrap** (help a single repository author its first `project/portfolio.yml`), and **Discover tech stack** (run the tech-stack-discovery methodology against a single repository or across the portfolio).

### Why this is one skill, not three

`spec/claude/skill-management/` §"Coherent units" generally favors one operation per skill. This skill bundles three operations because they share the same inputs (the per-repository `project/portfolio.yml` manifests collected via the GitHub API), the same domain vocabulary (capabilities, audiences, peers, ownership, portfolio scope), and the same output conventions (`review-plan`-format severities, the rendered inventory under `docs/<lang>/portfolio/`). Splitting them upfront would force three skills to re-implement the same manifest-collection plumbing and cross-validate the same vocabulary.

If any of the three operations grows complex enough to need its own dedicated review surface — for example if "Render" sprouts a templating engine or "Bootstrap" needs an interactive multi-turn audience-mapping flow — split it into a sibling skill (`portfolio-inventory-render`, `portfolio-bootstrap`) at that point, leaving "Audit" as the canonical `portfolio-audit`. The three operations below are deliberately structured to be split-friendly: each has its own preconditions, its own output artefact, and no shared mid-flow state.

### Why this is a skill, not an agent

- **Mid-flow user confirmation on duplicate-resolution choices.** The Audit operation surfaces duplicate candidates and gap-class findings; deciding which repository owns a contested capability, or whether a copy-paste smell warrants a new shared capability, is a per-step user dialogue. An agent's fire-and-forget shape would lose those checkpoints.
- **Persistent on-disk artefacts as deliverables.** Audit writes `.audits/portfolio/<YYYY-MM-DD>.md`. Render writes `docs/<lang>/portfolio/*.md`. Bootstrap writes `project/portfolio.yml` in the consuming repository. Skills own persistent state.
- **Context-window-protective manifest collection via agent.** Audit delegates raw manifest collection to the [`portfolio-manifest-collector`](../../agents/nolte-shared/portfolio-manifest-collector.md) agent, which fetches and parses each Portfolio-Member's `project/portfolio.yml` via `gh api` and returns a pre-reduced structured summary (declared capabilities, audiences, peer references). Raw YAML is discarded inside the agent before it returns, so the main conversation receives only the synthesised inventory report rather than the full raw manifest dump.
- **Counter-dimension considered**: a tool-restricted agent could perform the Audit operation cleanly in isolation, but Render and Bootstrap both write user-visible files in the active checkout and benefit from staying in the main conversation; bundling all three behind one skill is simpler than splitting Audit out.

### User-language policy

Detect the user's language and respond in it. Manifest content (`project/portfolio.yml`), the rendered inventory under `docs/<lang>/portfolio/`, and the Findings-Report under `.audits/portfolio/` follow the canonical conventions of their target files: YAML stays English, rendered docs follow the existing per-language docs-tree, the Findings-Report uses English for headings (per `review-plan`) but the body may be written in the user's language.

### Detection: am I in the right repository?

This skill operates in two roles depending on the active repository:

- **Inside `claude-shared`** (where this skill itself lives, plus the rendered portfolio inventory and the audit-history `.audits/portfolio/`): all three operations run end-to-end. Detection: presence of `.claude-plugin/plugin.json` AND a `spec/portfolio/portfolio-management/` directory.
- **Inside any other Portfolio-Member repository** (the typical adopter): only the **Bootstrap** operation runs end-to-end; Audit and Render require `claude-shared` access (the `.audits/portfolio/` and `docs/<lang>/portfolio/` write paths live there). Detection: any `nolte/*` repository that lacks the spec but accepts a `project/portfolio.yml`.

If the active repository is neither, stop and ask the user whether to switch to `claude-shared` for Audit / Render or to a Portfolio-Member repository for Bootstrap.

### Operations

#### 1. Audit (primary path)

Runs the cross-repository capability audit per `spec/portfolio/portfolio-management/` §Portfolio audit.

1. **Detect Portfolio-Member set** — query the GitHub API for the active set of public, non-archived repositories under `nolte` via `gh api orgs/nolte/repos --paginate --jq '.[] | select(.archived==false and .private==false) | .name'`. Cross-check each repository for an opt-out marker (`portfolio: excluded` at the top of `CLAUDE.md`); excluded repositories drop out of the audit set with their rationale recorded.
2. **Collect per-repository manifests via agent** — Dispatch [`portfolio-manifest-collector`](../../agents/nolte-shared/portfolio-manifest-collector.md) (Agent) to gather manifests from all portfolio members. Wait for its inventory report before proceeding to duplicate-detection and gap-classification. The agent fetches `project/portfolio.yml` for each member via `gh api`, reduces raw YAML to structured per-repository summaries (declared capabilities, audiences, peer references, missing-manifest indicator), and returns the full manifest-inventory report. Repositories without `project/portfolio.yml` produce a `missing-manifest` entry rather than an error.
3. **Run the four checks against the collected summary**:
   - **Manifest presence**: every Portfolio-Member repository ships a `project/portfolio.yml` or has the opt-out marker. Missing manifests on opted-in repositories are `Warning` findings.
   - **Manifest validity**: each manifest parses as YAML and contains the required fields (`name`, `description`, `audience`, `status`, `rationale`) per `spec/portfolio/portfolio-management/` §Capability inventory per repository. Schema violations are `Critical` findings.
   - **Cross-repository duplicate detection**: every pair of capabilities across all manifests gets a semantic-overlap comparison on `description` (not keyword-overlap). Fresh duplicates are `Warning`; duplicates persisting beyond the one-closed-sprint tolerance window are `Critical`. Resolution path is documented in the spec; this skill emits the finding, the operator makes the consolidation PR.
   - **Gap analysis** (three sub-classes per spec):
     - Broken peer reference: a `peers:` entry pointing to a non-existent `<repo>:<capability-name>` is a `Warning`.
     - Spec-demanded gap: a sibling spec under `spec/` declares a capability as a precondition that no manifest provides. `Warning`.
     - Cross-repository copy-paste smell: same workflow file / config block / non-trivial code pattern duplicated across three or more repositories without a corresponding shared capability is a `Suggestion` (under threshold) or `Warning` (at and above the 3-recurrence threshold from `skill-vs-agent` §Portfolio-wide consistency).
4. **Write the Findings-Report** at `.audits/portfolio/<YYYY-MM-DD>.md` in the `claude-shared` repository, conforming to `spec/claude/review-plan/`:
   - Required sections: `## Scope`, `## Summary`, `## Findings`, `## Processing log`
   - Severity vocabulary: `Critical` / `Warning` / `Suggestion` / `Info` exactly (Title Case, never ALL-CAPS) per `review-plan` §Severity scale
   - Each finding cites the originating spec rule in the bracketed prefix (e.g. `[portfolio-management §Cross-repository duplicate detection]`) so a downstream reader can trace it
5. **Confirm in the user's language** with: the path of the new Findings-Report, the per-severity counts, and the next step (typically: open the Findings-Report and start triaging the `Critical`-grade items first via `continuous-improvement`'s specialist-dispatch loop).

Audit operation **never** consolidates duplicates, never deletes capabilities, never opens PRs against Portfolio-Member repositories. It identifies and reports; the operator (or a future remediation skill) acts.

#### 2. Render (regenerate the inventory docs)

Regenerates the aggregated portfolio inventory pages under `claude-shared/docs/<lang>/portfolio/` from the same manifests collected in Audit.

1. **Manifest collection** — when the same conversation has already collected manifests (operation 1 step 2) within this turn, reuse the cached structured summary; otherwise dispatch [`portfolio-manifest-collector`](../../agents/nolte-shared/portfolio-manifest-collector.md) (Agent) afresh to collect the manifests via the same `gh api` flow as operation 1 step 2.
2. **Generate per-repository sections** for each Portfolio-Member: mission statement (quoted from `project/mission.md`), capability list with status badges (`active` / `experimental` / `deprecated`), audiences served (cross-referenced to the repository's audience artefact per `audience-identification`), outbound-peer-reference list.
3. **Generate the Mermaid diagram** (per `spec/project/mermaid-diagrams/`) visualizing the capability-to-repository mapping and cross-repository peer references. Pick the diagram type from the supported catalog; default to `flowchart` direction `LR` for the cross-repo map.
4. **Generate the `historical capabilities` appendix** if any archived repositories had registered capabilities; capabilities listed here keep peer references resolvable but are marked with the archival date.
5. **Write the rendered files** under `docs/<canonical_language>/portfolio/` and the corresponding translation under `docs/<other_language>/portfolio/` for every configured documentation language. Files **MUST** be marked auto-generated (header comment per `mkdocs-gen-files` convention so `task docs` doesn't treat them as drift).
6. **Verify** by running `task docs` (mkdocs `--strict`); if the build fails, surface the error and stop — don't commit broken renders.
7. **Confirm in the user's language** with: which files were written, which Portfolio-Member sections were included, and a one-line note when the rendered output didn't change (the regeneration is idempotent when manifests didn't change).

Render operation **never** modifies the source-of-truth manifests, never edits the spec, never publishes the docs (publication is the existing `task docs` / MkDocs pipeline's job).

#### 3. Bootstrap (initial portfolio.yml for one repository)

Helps a single Portfolio-Member repository author its first `project/portfolio.yml` interactively.

1. **Check the active repository** is a plausible Portfolio-Member candidate: it lives under `nolte/`, isn't archived, doesn't already carry the opt-out marker, and doesn't already have a `project/portfolio.yml`.
2. **Read the existing context**: `project/mission.md` (the mission statement constrains capability scope per `spec/project/mission/`), the audience artefact per `audience-identification`, and `project/roadmap.md` (active capabilities should align with active roadmap items).
3. **Walk the user through capability identification** — for each candidate capability:
   - Propose `name` (kebab-case, derived from the user's description) and confirm
   - Confirm `description` (one or two sentences naming what + for whom)
   - Map `audience` to entries in the existing audience artefact; new audiences need to be added to `project/audiences.md` first via `audience-identification`, this skill doesn't invent audiences inline
   - Default `status` to `active`; the user can override to `experimental` for early-stage capabilities
   - Collect `rationale` (one or two sentences naming why this repository owns the capability — never accept an empty or template rationale)
   - Optional: collect `peers` (list of `<repo>:<capability-name>` cross-references) and `since` (ISO date)
4. **Write `project/portfolio.yml`** at the repository root with the collected entries. Verify the file parses as YAML before declaring success.
5. **Confirm in the user's language** with: the file path, the capability list as a concise summary, and a follow-up reminder that the next `portfolio-audit` run from the `claude-shared` side will pick up the new manifest.

Bootstrap operation **never** modifies `project/mission.md`, `project/roadmap.md`, or the audience artefact — those are owned by their own dedicated skills and authoring flows. If the user discovers during Bootstrap that their mission or audience list needs updating first, this skill stops and routes them to the appropriate skill.

#### 4. Discover tech stack

Runs the tech-stack-discovery methodology from `spec/portfolio/tech-stack-discovery/` against a single repository or across every Portfolio-Member repository.

1. **Determine the scope** the user asked for: single-repo (the active checkout, or a user-supplied path) versus portfolio-wide (every Portfolio-Member repository known via the GitHub API).
2. **For each in-scope repository, read the canonical detection sources** declared in `spec/portfolio/tech-stack-discovery/` (typically `pyproject.toml`, `package.json`, `Taskfile.yml`, `.github/workflows/`, `Dockerfile`, language-specific lockfiles). Don't invent detection sources the spec doesn't sanction.
3. **Extract the tech-stack signal per layer** the spec defines (language runtime, package manager, build tool, lint stack, test stack, CI runner, deployment target, plugin engines, external services). Report the detected value plus the source path and line.
4. **Cross-validate against the portfolio baseline** declared in `spec/portfolio/tech-stack/`. Findings shape:
   - **In-baseline** — the detected value matches what the portfolio baseline ratifies.
   - **Drift** — the detected value diverges from the baseline (`pyproject.toml` pins a Python version different from the baseline, or a Taskfile uses a different lint target).
   - **Net-new** — the detected value isn't in the baseline at all (the repository introduces a tool the portfolio hasn't ratified yet).
5. **Persist the result** under `.audits/tech-stack/<YYYY-Q<n>>.md` (or the per-repo equivalent) — same severity grammar as Audit, same `Caller follow-ups` shape.

Discover-tech-stack is read-only — it doesn't modify the portfolio baseline in `spec/portfolio/tech-stack/`. When the user discovers a net-new tool worth ratifying, this skill stops and routes them to the [`spec`](spec.md) skill to propose a baseline extension, rather than silently amending the spec from here.

### Reference: spec anchors

This skill implements rules declared in `spec/portfolio/portfolio-management/`. Read those rules when in doubt:

- §Portfolio scope — defines what counts as a Portfolio-Member repository, including the opt-out marker
- §Capability inventory per repository — defines the `project/portfolio.yml` schema
- §Cross-repository duplicate detection — defines the duplicate semantic-overlap rule and the tolerance window
- §Gap analysis — defines the three gap classes (broken peer reference, spec-demanded gap, copy-paste smell)
- §Portfolio audit — defines this skill's required output shape and integration with `continuous-improvement`
- §Documentation rendering — defines what the rendered inventory under `docs/<lang>/portfolio/` must contain
- §Decision documentation — defines the `rationale` field requirement and the re-allocation atomic-operation rule

The Discover-tech-stack operation implements `spec/portfolio/tech-stack-discovery/`:

- §Detection sources — defines which on-disk files are canonical signals for which stack layer
- §Cross-validation against baseline — defines the in-baseline / drift / net-new finding classes against `spec/portfolio/tech-stack/`
- §Audit persistence — defines the per-repo audit artefact shape under `.audits/tech-stack/`

When the spec disagrees with this skill's instructions, the spec wins. Propose a skill update rather than silently diverging.

### Examples

- Read `examples/01-audit-detects-duplicate.md` when the audit surfaces a duplicate capability across portfolio members.
- Read `examples/02-render-inventory-idempotent.md` when re-running the inventory render to verify idempotency.
- Read `examples/03-bootstrap-new-member.md` when bootstrapping a new portfolio member's `project/portfolio.yml` for the first time.

### Gotchas

- **Bootstrap blocks if [`tech-stack-capture`](tech-stack-capture.md) hasn't run yet**: Bootstrap reads `project/mission.md` and the audience artefact as inputs; if neither exists in the target repository, Bootstrap has nothing to derive capabilities from — route the user to [`mission-define`](mission-define.md) and [`audience-identify`](audience-identify.md) first rather than proceeding with empty fields.
- **`gh api` rate limits can stall portfolio-wide manifest collection**: fetching `project/portfolio.yml` for every public non-archived repository in one call sequence can exhaust the GitHub API rate limit for large portfolios — spread calls across turns or check `gh api rate_limit` before starting a full-portfolio Audit.
- **Findings-Report and rendered inventory must land in `claude-shared`, not in the calling repo**: writing `.audits/portfolio/` or `docs/<lang>/portfolio/` from a non-`claude-shared` working directory is a structural error; confirm `cwd` resolves to the `claude-shared` checkout before any Audit or Render write.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/portfolio-audit/<run-id>.yml` after every successful user-approval gate and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope (`schema_version`, `run_id`, `inputs`, `phase`, `decisions[]`, `status`, ...) and the fail-closed semantics on schema or YAML errors are load-bearing in the spec; don't duplicate those rules here.

### Hard rules

- Never modify a Portfolio-Member repository's `project/portfolio.yml` from this skill; only Bootstrap writes it on first authoring, and only inside the active checkout. Cross-repository edits go through ordinary PR flows in the target repository, not through this skill.
- Never consolidate duplicate capabilities automatically, never mark a capability `status: deprecated` from the audit side, never open a PR against another Portfolio-Member repository. The audit identifies and reports; the operator acts.
- Never use a severity outside the canonical four (`Critical` / `Warning` / `Suggestion` / `Info`). ALL-CAPS variants (`BLOCKER`, `WARNING`, `SUGGESTION`, `INFO`) are forbidden per `spec/claude/review-plan/` §Severity scale and are themselves a `review-plan` violation if they appear in the Findings-Report.
- Never fetch `project/portfolio.yml` from repositories outside the resolved Portfolio-Member set. Scope drift here is a confidentiality risk — private repositories or non-`nolte/*` forks must never enter the manifest collection.
- Never write the Findings-Report or the rendered inventory outside the `claude-shared` repository. Both artefacts live in `claude-shared`; misrouted writes are a structural error, not a typo.
- Never bypass `continuous-improvement` for routing portfolio findings. The audit emits the report; the triage and specialist-dispatch live in `continuous-improvement`'s loop.
- Never invent a `mission` quote or an `audience` entry for the rendered inventory; quote verbatim from the source files, and if a Portfolio-Member repository lacks a mission or audience artefact, render a placeholder noting the gap and emit a `Warning` finding in the next Audit run.
- When `spec/portfolio/portfolio-management/` disagrees with this skill, the spec wins. Propose updating this skill rather than silently diverging.
- Always render the portfolio inventory symmetrically across every language tree configured in `spec/.spec-config.yml`'s `languages` list, per `spec/project/docs-multilingual-authoring/` §Authoring protocol. A render that writes `docs/<canonical_language>/portfolio/index.md` without writing the counterpart in every other configured language tree in the same operation is a violation. Verbatim quotes (mission statement, audience entries) are emitted as-is in every language tree per the no-invention rule above; surrounding section titles, table headers, and chrome are localised.
