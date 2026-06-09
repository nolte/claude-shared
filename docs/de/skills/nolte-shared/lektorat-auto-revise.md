---
title: lektorat-auto-revise
audience: [maintainer]
content_mode: reference
track: developer-docs
last_updated: generated
---

# lektorat-auto-revise

> Arbeitet einen Lektorat-Audit-Report autonom ab, indem es jedes Artefakt an den passenden Author routet und bis zur Konvergenz re-auditiert.

_Autonomously works off a `lektorat audit` findings report by routing each artefact by type — documentation to the [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md) agent (fully autonomous), blog posts to the [`blog-author`](blog-author.md) skill (assisted) — composing a per-file briefing that binds the audience artefact and writing-style spec, letting the author revise, then re-auditing until no finding above the severity floor remains and there is no regression. Operationalises `spec/project/lektorat-auto-revise/`. Invoke when the user asks to "arbeite das Lektorat-Audit automatisch ab", "auto-revise the audit findings", "remediate the lektorat findings with the right author", or equivalent EN/DE requests. Don't use for the read-only audit or interactive per-finding fixes (use [`lektorat-apply`](lektorat-apply.md)), or for first authorship ([`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md)/[`blog-author`](blog-author.md)). Writes to `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/`. Supports resume per `spec/claude/resumable-work/`._

- **Plugin:** `nolte-shared`
- **Phase:** 6 Quality (`quality`)
- **Tags:** `prose`, `audit`
- **Quelle:** [skills/lektorat-auto-revise/SKILL.md](https://github.com/nolte/claude-shared/blob/main/skills/lektorat-auto-revise/SKILL.md)

## Anwenden wenn

- you want to work off a lektorat audit report automatically, without a per-finding approval cycle
- you want the matching author (docs vs blog) to fix editorial findings per artefact type
- you want autonomous editorial remediation gated by a machine re-audit

## Nicht anwenden wenn

- **You want the read-only editorial audit, not remediation** → [`lektorat-apply`](lektorat-apply.md)
- **You want to drive per-finding fixes interactively by hand** → [`lektorat-apply`](lektorat-apply.md)
- **You want to author a new artefact from scratch** → [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md)

## Siehe auch

- [`lektorat-apply`](lektorat-apply.md)
- [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md)
- [`blog-author`](blog-author.md)
- [`lektorat-scanner`](../../agents/nolte-shared/lektorat-scanner.md)

---

## Lektorat Auto-Revise

Operationalises `spec/project/lektorat-auto-revise/` for the `nolte-shared` plugin: the autonomous bridge from an existing `lektorat audit` findings report to a finished, re-verified artefact. It consumes the audit, routes each affected artefact to the **author best suited to its type**, composes a per-file briefing, lets that author revise, and re-audits until the artefact converges.

This skill binds the spec's contract to an on-disk procedure. It owns **no** editorial rules of its own — severities, dimensions, scope, audience binding, and semantic-preservation guarantees belong to `spec/project/lektorat/`; the writing-style and audience rules belong to the dispatched author's bound specs. When this skill and a spec disagree, the spec wins and this skill needs the update.

### German trigger phrases

This skill also triggers on equivalent German-language requests, including:

- "arbeite das Lektorat-Audit automatisch ab"
- "lass den passenden Author die Findings abarbeiten"
- "vollautomatische Lektorats-Remediation"
- "revidiere die Audit-Findings automatisch"

### User-language policy

Detect the user's language from their message and respond in it. The machine-readable JSON output uses English keys (mirroring `spec/project/lektorat/` §Outputs); the human-readable `summary.md` uses English section headings so downstream tooling can parse it; prose around the report is localised.

### Why this is a skill, not an agent

- **The blog route's interactive touchpoint is load-bearing**: [`blog-author`](blog-author.md) is an interactive skill whose briefing inputs (topic-as-thesis, source list, slug, cross-language binding key) can't be reconstructed from findings; surfacing that dialogue back to the operator only fits a skill.
- **Externally visible writes**: outputs land under `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/` and the dispatched author edits in-scope artefacts in place; the skill owns the persistent on-disk state.
- **Orchestration role**: the skill dispatches the [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md) agent and the [`blog-author`](blog-author.md) skill, re-runs the `lektorat audit` for the convergence gate, and stays in the main thread to compose briefings, run the assisted-blog dialogue, and write outputs.
- **Counter-dimension considered**: the documentation route alone is fire-and-forget and would fit an agent, but consolidating both routes plus the convergence loop behind one entry point keeps the operator's mental model coherent and is where the load-bearing interactivity lives.

### Inputs

- **Audit report** (required): a path to an existing `.audits/lektorat/<YYYY-MM-DD-HHMM>/findings.json`, or a directive to run a fresh [`lektorat-apply`](lektorat-apply.md) audit first and consume its output. The report's shape is `spec/project/lektorat/` §Outputs; consume it verbatim and never add, drop, or rename a field.
- **Severity floor** (optional): inherited from the input run; defaults to addressing every `critical` and `warning` finding. A caller may narrow to `critical` for a de-noised pass.
- **Audience-artefact path** (optional): resolved through the same priority chain as `lektorat` §Audience binding; a missing artefact stops per-file remediation with the message pointing at [`audience-identify`](audience-identify.md).

### Procedure

Run the steps in order. Each maps to a requirement block in the spec; consult the spec for the authoritative rules rather than relying on this summary.

1. **Resolve the audit report** (§Input contract). Load the `findings.json`. Process only the `findings` array. For any file named in an `inventory_findings` entry, do **not** dispatch an author — surface the infrastructure condition to the operator instead.
2. **Group findings by `file`** so each artefact is handled once with the full set of its findings.
3. **Route each file** (§Artefact-type routing) into exactly one class before any dispatch:
   - `documentation` (MkDocs page under `docs/<lang>/`, top-level Markdown, or a GitHub Release/Issue/PR body) → [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md) agent.
   - `blog-post` (carries the consumer's cross-language binding key, e.g. `translationKey`, in its frontmatter) → [`blog-author`](blog-author.md) skill.
   - `rejected` (any path `lektorat` §Scope and applicability excludes — `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`, source, generated config) → hard-reject with a one-sentence message naming the owning flow; dispatch no author.
   - A file matching none of the three classes stops the whole run with an operator-facing message; never silently skip it.
4. **Compose the briefing per file** (§Author briefing composition): the file's findings verbatim, the resolved audience set (via the `lektorat` priority chain, no other rule), the bound writing-style spec(s), and the target D1–D6 dimensions. For any file with a **D1 readability finding**, also pass the LIX target inputs per `spec/project/readability-lix/` §Iterative improvement loop: the current `lix`, the resolved corridor (`aim`/`warn`/`crit` for the file's `content_mode` and language), and the dominant lever (`ASL` or `LWP`), so the author's pass targets the right readability lever. Never dispatch an author without **both** a resolved audience set and a bound writing-style spec — a missing either is a per-file stop condition.
5. **Dispatch the matching author** (§Autonomy and human touchpoints):
   - Documentation → dispatch [`audience-doc-author`](../../agents/nolte-shared/audience-doc-author.md) **fully autonomously** (no per-finding approval, no diff gate). Pass the audience-artefact path, the doc-type spec, the `prose-style` baseline, and the file under revision.
   - Blog → run **assisted**: surface the findings-derived briefing to [`blog-author`](blog-author.md) and let its briefing touchpoint stand. Never fabricate the briefing inputs it requires.
   - Never rewrite prose in this skill; the rewrite is always the author's.
6. **Re-audit convergence gate** (§Re-audit convergence gate). After each author pass, re-run the `lektorat audit` on the revised artefact with the same configuration. A file is **converged** only when it has no remaining finding at or above the severity floor **and** its post-revision finding count is ≤ its pre-revision count. A D1 readability finding converges only when the re-audit shows LIX at or below the file's `warn` corridor (`readability-lix` §Iterative improvement loop); a LIX drop achieved by a forbidden transformation (decompounding an established term, vaguer-shorter swaps, altering a protected term) is a semantic-preservation failure, not convergence. On non-convergence, re-dispatch the author with the residual findings up to **2 author passes** per file, then **escalate** the residual to the operator — never loop further. Flag any **regression** (post-count higher than pre-count, or a risen LIX) and never auto-accept it as converged. Treat any semantic-preservation violation (§Semantic preservation) as a failed pass.
7. **Write the run trail** (§Outputs) under `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/`: `routing.json`, `run.json` (referencing the source audit run), per-file rewrite diffs with pre/post counts and pass count, and `summary.md`. List escalated and regressed files **first** in `summary.md` so unremediated findings can't be overlooked.

### Hard rules

- Never define, re-classify, or re-weight findings, severities, or dimensions; consume the `lektorat` report verbatim. The rules live in the spec, not here.
- Never dispatch an author without both a resolved audience set and a bound writing-style spec. "No audience" and "no style spec" are stop conditions, not soft defaults.
- Never rewrite prose in this skill — every rewrite is delegated to the routed author, so the author's audience and writing-style competence applies.
- Never run the documentation route with a human gate, and never run the blog route without [`blog-author`](blog-author.md)'s briefing touchpoint.
- Never mark a file converged while it has a finding at or above the severity floor or a regression; never loop past 2 author passes — escalate instead.
- Never route or dispatch an author at a `rejected`-class path; never widen the routing table to a class `lektorat` forbids.
- Never silently skip an unroutable file or truncate unremediated findings — stop the run or escalate, and record it.

### Resumability

Per `spec/claude/resumable-work/`, this skill is `resumable: true`. State is persisted to `.resume/lektorat-auto-revise/<run-id>.yml` after every successful per-file convergence and after each named phase boundary. On re-invocation, scan that directory for files with `status: in_progress` whose `inputs:` snapshot matches the current invocation; if one matches, prompt the operator with `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)? [resume / start-new / discard]`. The state-file envelope and fail-closed semantics on schema or YAML errors are defined in the spec; don't duplicate them here.
