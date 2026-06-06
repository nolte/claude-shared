# `Lektorat Auto-Revise`

Status: draft

## Context

[`spec/project/lektorat/`](../lektorat/en.md) defines the editorial layer: an `audit` produces a structured findings report (D1–D5, severity-classified, audience-bound), a `patch` applies one finding per operator approval, and a `revise` rewrites a full artefact behind an operator diff gate. All three mutating paths put a human in the loop on every write, and `revise` performs the rewrite **inside the `lektorat-apply` skill itself**: a generic, lexical rewrite that has no audience-specific depth model and no binding to the writing-style specs an author would consult.

What's missing is the **autonomous bridge** from an existing audit report to a finished, re-verified artefact, where the rewrite is performed by the **author best suited to the artefact type**: the author whose own contract already mandates reading the audience artefact and the writing-style spec, so that *style* and *audience-fit* compliance is structural rather than re-implemented. The `audience-doc-author` agent already anticipates this: it names a *"future orchestrating skill"* as the driver that turns its fire-and-forget executor contract into a closed loop. `Lektorat Auto-Revise` is that driver.

The layer is **operative**: it mandates one process—consume an audit report, route each affected artefact to the matching author, compose a per-artefact briefing, let the author revise, then re-audit until the artefact converges—with explicit pre- and postconditions, so a downstream skill can implement the contract without re-litigating semantics. It owns **no** editorial rules of its own: severities, dimensions, scope, audience binding, and semantic-preservation guarantees all belong to `lektorat`; the writing-style and audience rules belong to the authors' bound specs. This spec only defines the **orchestration** that wires them together and the **machine verification** (re-audit) that replaces the per-finding human gate.

**Readers** of this spec are implementors of the `lektorat-auto-revise` skill (primary) and operators who invoke autonomous editorial remediation from a sprint-review, a release gate, or a manual cleanup pass (secondary). Familiarity with [`spec/project/lektorat/`](../lektorat/en.md) (the findings report, severities, audience binding, semantic-preservation guarantees), [`spec/project/audience-identification/`](../audience-identification/en.md) (the audience artefact), [`spec/project/prose-style/`](../prose-style/en.md) (EN voice/tone), and the blog-side pair [`spec/project/post-writing-style/`](../post-writing-style/en.md) and [`spec/project/post-audience-communication/`](../post-audience-communication/en.md) is assumed; terms drawn from those specs are used without restatement.

## Goals

- An existing `lektorat audit` findings report can be worked off **automatically**, without a per-finding human approval cycle, so editorial remediation scales beyond what manual `patch` / `revise` allows
- Each affected artefact is routed to the **matching author** by artefact type, so the rewrite is performed by the component whose contract already binds the relevant writing-style and audience specs
- **Writing style and audience-fit are mandatory**, not advisory: the process refuses to dispatch any author without a resolved audience set and a bound writing-style spec, so style and audience compliance is structurally guaranteed
- The autonomous loop is **machine-verified**: a re-audit confirms the artefact converged (no remaining findings at or above the severity floor, no regression) before the run is marked done, replacing the human diff gate with a reproducible check
- The boundary against `lektorat` (the rules, the findings, the `patch` / `revise` operations), `audience-doc-author` and `blog-author` (first-class authorship), and `audience-identification` / `prose-style` / `post-writing-style` / `post-audience-communication` (the rule sources) is sharp enough that no requirement is restated in two specs
- The documentation route runs **fully autonomously**; the blog route runs **assisted**, preserving the one interactive briefing interaction that `blog-author`'s skill contract requires, so the spec is honest about the difference between a dispatchable agent and an interactive skill

## Non-Goals

- Defining, re-classifying, or re-weighting editorial findings, severities (`critical` / `warning` / `suggestion`), or the five quality dimensions (D1–D5)—all owned by [`spec/project/lektorat/`](../lektorat/en.md); `Lektorat Auto-Revise` consumes the findings report and **MUST NOT** redefine any field of it
- Performing the editorial **detection** itself—the input is a findings report produced by a prior `lektorat audit`; this spec never re-implements the scan, it consumes its output and re-invokes it for the convergence check
- First authorship of new artefacts—owned by the `audience-doc-author` agent and the `blog-author` skill; this layer only drives **revision of artefacts that already exist** and already carry findings
- Defining the writing-style rules (EN voice/tone, blog forbidden-words list, bilingual typography) or the audience model—owned by `prose-style`, `post-writing-style`, `post-audience-communication`, and `audience-identification`; the process binds those specs **through the dispatched author**, it doesn't restate them
- Replacing `lektorat`'s `patch` and `revise` operations—those remain the **interactive, human-gated** remediation paths for cases an operator wants to drive by hand; `Lektorat Auto-Revise` is the autonomous, author-routed alternative, and a repository **MAY** use either
- Widening the editorial scope: artefact classes that `lektorat` §Scope and applicability excludes (files under `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`, source code, generated configuration) are **never** routed to an author and are **hard-rejected** here, exactly as `lektorat` forbids them upstream
- Translation or cross-language parity—owned by `spec`, `docs-multilingual-authoring`, and `docs-freshness`; each artefact is revised in its own language by an author working in that language

## Requirements

### Input contract

- **MUST** take as input a **completed `lektorat audit` findings report**: either a path to an existing `.audits/lektorat/<YYYY-MM-DD-HHMM>/findings.json`, or a directive to run a fresh `audit` (via `lektorat-apply`) first and consume its output. The report's shape is the one declared in [`spec/project/lektorat/`](../lektorat/en.md) §Outputs; this spec consumes it verbatim and **MUST NOT** add, drop, or rename any field
- **MUST** process only entries in the report's `findings` array. Entries in `inventory_findings` describe infrastructure conditions that prevented part of the scan from completing; for any file named in an `inventory_findings` entry, the process **MUST NOT** dispatch an author (an artefact that wasn't scanned can't be safely revised) and **MUST** surface the condition to the operator
- **MUST** honour the input run's **severity floor**: by default it addresses every `critical` and `warning` finding and **SHOULD** address `suggestion` findings only when doing so doesn't extend the rewrite scope, mirroring `lektorat` §Operation C. A repository **MAY** narrow the floor to `critical` for a de-noised autonomous pass
- **MUST** group the `findings` array **by `file`** before routing, so every distinct artefact is handled once with the full set of its findings, regardless of how the findings were ordered in the report

### Artefact-type routing

- **MUST** classify every distinct `file` in the findings into **exactly one** routing class before any author is dispatched. The classes and their resolution are:

  | Routing class | Detection signal | Dispatched author |
  | --- | --- | --- |
  | `documentation` | MkDocs page under `docs/<lang>/`, or top-level repository Markdown (`README.md`, `ONBOARDING.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`), or a GitHub Release / Issue / pull-request body; identified by path plus, for MkDocs pages, the `track` / `content_mode` frontmatter from `docs-audience-tracks` | `audience-doc-author` agent |
  | `blog-post` | a post-pair artefact carrying the consumer's cross-language binding key (reference: `translationKey`) in its frontmatter, in the consumer's declared blog-post location (reference: `nolte/blog`) | `blog-author` skill |
  | `rejected` | any path that `lektorat` §Scope and applicability excludes (under `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, `agents/*.md`, source code, generated configuration, binaries) | none, **hard reject** |

- **MUST** route **per file**: a findings report spanning both documentation and blog artefacts fans out to both authors, each handling only the files of its class
- **MUST** hard-reject any `rejected`-class file with a single-sentence message naming the owning authoring flow (the `spec` skill for `spec/`, `skill-management` / `agent-management` for LLM-instruction artefacts) and **MUST NOT** dispatch any author at it. Such a file should never reach this process (a conformant `lektorat audit` already excludes it), but the rejection is a defensive invariant, not an assumption
- **MUST** stop the whole run with an operator-facing message when a file matches **none** of the three classes (an in-scope artefact type this spec doesn't yet route); silently skipping it would hide unresolved findings
- **MUST NOT** allow the routing table to widen to any class that `lektorat` forbids; a repository **MAY** add a new routing class only by amending this spec, exactly as `lektorat` gates its scope

### Author briefing composition

- **MUST**, for each routed file, compose a **briefing** that the dispatched author receives, containing all of:
  1. the **subset of findings** for that file, verbatim from the input report (severity, dimension, line range, message, `rule`, `audience`, `evidence`, `suggested_resolution`)
  2. the file's **resolved audience set**, obtained through the **same priority chain** as `lektorat` §Audience binding (frontmatter `audience:` → artefact-type defaults → whole audience set); this process **MUST NOT** resolve audiences by any other rule
  3. the **bound writing-style specs** for the route (see §Mandatory style and audience binding)
  4. the **target dimensions**: the distinct D1–D5 values present in the file's findings—so the author knows which editorial axes the revision must move
  5. for any file carrying a **D1 readability finding**, the file's **LIX target inputs** per [`spec/project/readability-lix/`](../readability-lix/en.md) §Iterative improvement loop: the current `lix`, the resolved corridor (`aim` / `warn` / `crit` for the file's `content_mode` and language), and the **dominant lever** (`ASL` or `LWP`)—so the author's pass is directed at the right readability lever (split sentences versus shorten long words) rather than rewriting blind
- **MUST** read the **audience artefact** from its canonical location exactly as `lektorat` §Audience binding mandates, and **MUST** stop the **per-file** remediation (not the whole run) with the same operator-facing message pointing at the `audience-identify` skill when the artefact is missing; the process **MUST NOT** invent audiences and **MUST NOT** dispatch an author without a resolved audience set
- **MUST** pass the briefing in a form the dispatched author's own input contract accepts: for `audience-doc-author`, the audience-artefact path, the doc-type spec, the `prose-style` baseline, and the source material (the file under revision); for `blog-author`, the briefing inputs its skill contract requires (see §Autonomy and human interactions for the assisted-interaction rule)

### Mandatory style and audience binding

- **MUST** bind the **writing-style spec** per routing class and **MUST NOT** dispatch an author without it:
  - `documentation` → [`spec/project/prose-style/`](../prose-style/en.md) (plus the doc-type spec the `audience-doc-author` contract resolves, for example `readme-structure`, `release-notes-audience-analysis`)
  - `blog-post` → [`spec/project/post-writing-style/`](../post-writing-style/en.md) and [`spec/project/post-audience-communication/`](../post-audience-communication/en.md)
- **MUST** dispatch the author whose **own contract already mandates consulting** those specs, so writing-style and audience-fit compliance is enforced by the author's contract rather than re-checked here; this process **MUST NOT** maintain a parallel copy of any style or audience rule
- **MUST NOT** rewrite prose itself. The rewrite is **always** delegated to the routed author, precisely so the author's audience-depth model and writing-style competence apply; a generic in-orchestrator rewrite is what `lektorat` §Operation C already offers and is explicitly **not** this layer's job
- **MUST** treat a missing **either** input—resolved audience set **or** bound writing-style spec—as a per-file **stop condition**, never a soft default; "no audience" and "no style spec" aren't states in which an author may run

### Autonomy and human interactions

- **MUST** run the `documentation` route **fully autonomously**: no per-finding approval, no human diff gate. The dispatched `audience-doc-author` agent edits the artefact in place; correctness is verified by the §Re-audit convergence gate, not by a human
- **MUST** run the `blog-post` route **assisted**: `blog-author` is an interactive skill whose contract requires briefing inputs (topic-as-thesis, grounded artefact, primary audience, source list, slug, cross-language binding key) that can't be reconstructed from findings alone. The process **MUST** surface the findings-derived briefing to that skill and **MUST NOT** fabricate the briefing inputs it requires; the operator supplies what the existing post and findings don't
- **MUST** record, per file, whether the route ran `autonomous` or `assisted` in the output (§Outputs), so a reader of the audit trail can see exactly where a human was in the loop
- **MAY**, as a tracked future extension, gain a fully-autonomous blog route once `blog-author` (or a sibling) exposes a findings-driven update mode that needs no interactive briefing; until then the assisted contract above is binding (see §Open Questions)

### Semantic preservation

- **MUST** require the dispatched author to preserve semantic content under the **same guarantees** that `lektorat` §Operation C `revise` and §Refactor safety mandate: every fact, claim, command, identifier, link target, frontmatter key, code block, block-quoted citation, and HTML-comment marker present in the original artefact is preserved byte-identical, with at most lexical change; no list item, table row, or checklist entry is reordered, merged, or dropped; no new factual content (commands, file paths, product names, URLs) absent from the original is introduced. This process **MUST NOT** relax any of those constraints and **MUST NOT** restate them—the authoritative list lives in `lektorat`
- **MUST** treat any author revision that violates a semantic-preservation guarantee as a **failed pass** for that file, surface it to the operator, and **MUST NOT** accept the rewrite onto disk as converged

### Re-audit convergence gate

- **MUST**, after the author completes a file, **re-run the `lektorat audit`** on the revised artefact with the **same configuration** as the input run (severity floor, audience artefact, language pipeline)
- **MUST** treat a file as **converged** only when **both** hold:
  1. **no remaining finding** at or above the severity floor for that file, **and**
  2. **no regression**: the post-revision total finding count for the file is **less than or equal to** the pre-revision count (mirrors `lektorat` §Operation C regression detection)
- **MUST NOT** mark a file done, and **MUST NOT** treat the run as complete, until every routed (non-rejected) file is converged or escalated
- **MUST**, on non-convergence of a file, re-dispatch the author with the **residual findings** for a **bounded** number of author passes (**default: 2** passes per file); after the bound is reached the process **MUST** escalate the residual findings to the operator and **MUST NOT** loop further. The bound and the escalation are load-bearing: an autonomous loop without a cap is forbidden
- **MUST** flag a **regression** (post-revision count higher than pre-revision count) to the operator and **MUST NOT** automatically accept a regressed rewrite as converged, even if it cleared the severity floor
- **MUST** treat a **D1 readability finding** as converged only when the re-audit shows the file's LIX at or below its resolved `warn` corridor per [`spec/project/readability-lix/`](../readability-lix/en.md) §Iterative improvement loop; a re-audit in which LIX moved from above `warn` to at or below `warn` is progress, a re-audit in which LIX rose is a regression, and a pass that lowered LIX through a transformation forbidden by `readability-lix` §Improving a LIX score (decompounding an established term, swapping a precise term for a vaguer shorter one, altering a protected term) is caught by the §Semantic preservation guarantees and is a **failed pass**, never convergence
- **MUST** record, per file, the pre-revision count, the post-revision count, the number of author passes, and the terminal status (`converged` / `regressed` / `escalated`) in the output

### Outputs

- **MUST** write a run trail under `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/` (mirroring `lektorat`'s `.audits/lektorat/` convention), containing:
  - `routing.json`: per file, the routing class, the detection signal that resolved it, and the dispatched author (or the rejection reason)
  - `run.json`: the source audit run consumed (path to the input `findings.json`), the resolved severity floor, and the resolved audience-artefact path
  - per converged or escalated file: the author's rewrite **unified diff**, the pre-revision and post-revision finding counts, the author-pass count, and the terminal status
  - `summary.md`: a human-readable, severity-sorted summary that names, per file, the route (`autonomous` / `assisted`), the terminal status, and any escalated residual findings
- **MUST** reference the **source `lektorat audit` run** it consumed, so the autonomous remediation is traceable back to the audit that triggered it
- **MUST** make any **escalated residual** and any **regressed** file impossible to overlook in `summary.md` (listed first, before converged files); silently truncating unresolved findings is forbidden
- The `.audits/lektorat-auto-revise/` JSON is the **contract**; rendering it as CI or pull-request annotations is a downstream decision out of scope here, consistent with how `lektorat` and the other audit specs treat their on-disk trail as the deliverable

### Skill and agent distribution (recommendation)

The spec leaves the implementation shape **open** but **SHOULD** be implemented as a single orchestrating skill, mirroring the portfolio's hybrid pattern:

- **`lektorat-auto-revise` skill**: the orchestrator and only new component. It consumes the audit report, classifies routing, composes briefings, dispatches the existing `audience-doc-author` agent (documentation route) and the existing `blog-author` skill (blog route), re-runs the `lektorat audit` for the convergence gate, owns the assisted-blog operator interaction, and writes the `.audits/lektorat-auto-revise/` trail. It's a **skill**, not an agent, because the blog route's interactive briefing interaction and the persistent on-disk audit trail are both load-bearing—an agent's fire-and-forget contract would lose the dialogue and the orchestration role
- The skill **MUST NOT** introduce a new scanner; the convergence re-audit reuses the existing `lektorat` audit path (`lektorat-apply` / `lektorat-scanner`), so there's exactly one editorial detection implementation in the portfolio

### Coordination with neighbouring specs

- **MUST** reference [`spec/project/lektorat/`](../lektorat/en.md) as the authoritative source of the findings report shape, severities, dimensions, scope, audience binding, and semantic-preservation guarantees; `Lektorat Auto-Revise` consumes them and **MUST NOT** redefine them
- **MUST** reference [`spec/project/audience-identification/`](../audience-identification/en.md) as the authoritative source of audience identifiers and properties; the process reads the artefact and **MUST NOT** invent audiences
- **MUST** reference [`spec/project/prose-style/`](../prose-style/en.md) (documentation route) and [`spec/project/post-writing-style/`](../post-writing-style/en.md) + [`spec/project/post-audience-communication/`](../post-audience-communication/en.md) (blog route) as the authoritative writing-style rules, bound through the dispatched author and never restated here
- **MUST NOT** override, relax, or duplicate any MUST declared in the specs above; conflicts are resolved by amending the upstream spec, not by exception in `Lektorat Auto-Revise`

## Acceptance Criteria

- [ ] A run takes a `lektorat audit` `findings.json` as input and consumes its `findings` array without adding, dropping, or renaming any field of the report
- [ ] A file named in an `inventory_findings` entry of the input report isn't routed to any author, and the infrastructure condition is surfaced to the operator
- [ ] The `findings` array is grouped by `file` so each artefact is handled once with the full set of its findings
- [ ] A documentation artefact (MkDocs page or top-level Markdown) is routed to `audience-doc-author`; a blog-post artefact (carrying the consumer's cross-language binding key) is routed to `blog-author`; the routing class and dispatched author are recorded in `routing.json`
- [ ] A file under `spec/`, `skills/**/SKILL.md`, `skills/**/templates/**`, `skills/**/examples/**`, or `agents/*.md` is hard-rejected with a message naming the owning authoring flow, and no author is dispatched at it
- [ ] A file matching none of the three routing classes stops the run with an operator-facing message rather than being silently skipped
- [ ] Each dispatched author receives a briefing containing the file's findings, the resolved audience set, the bound writing-style specs, and the target D1–D5 dimensions
- [ ] The audience set is resolved through the `lektorat` §Audience binding priority chain (frontmatter → artefact-type default → whole set), identical to a standalone `lektorat audit`
- [ ] When the audience artefact is missing, the per-file remediation stops with the message pointing at `audience-identify`, and no author is dispatched
- [ ] No author is dispatched without both a resolved audience set and a bound writing-style spec; a missing either is a per-file stop condition
- [ ] The process never rewrites prose itself; every rewrite is performed by the routed author (verifiable from the audit trail crediting the author per file)
- [ ] The documentation route runs without any per-finding approval or human diff gate; the audit trail records the route as `autonomous`
- [ ] The blog route surfaces the findings-derived briefing to `blog-author`, preserves its interactive briefing interaction, doesn't fabricate the briefing inputs `blog-author` requires, and records the route as `assisted`
- [ ] An author revision that drops a code block, list item, table row, checklist entry, link target, frontmatter key, citation, or HTML comment, or that introduces a new command/path/product-name/URL absent from the original, is treated as a failed pass and isn't accepted as converged
- [ ] After each author pass the `lektorat audit` is re-run on the revised artefact with the same configuration as the input run
- [ ] A file is marked converged only when it has no remaining finding at or above the severity floor **and** the post-revision finding count is ≤ the pre-revision count
- [ ] A file whose post-revision finding count exceeds its pre-revision count is flagged as a regression to the operator and isn't automatically accepted as converged
- [ ] A file that doesn't converge within the bounded number of author passes (default 2) has its residual findings escalated to the operator, and the loop doesn't continue past the bound
- [ ] The run writes `routing.json`, `run.json`, per-file rewrite diffs with pre/post counts and pass count, and `summary.md` under `.audits/lektorat-auto-revise/<YYYY-MM-DD-HHMM>/`, and references the source audit run
- [ ] `summary.md` lists escalated and regressed files before converged files so unresolved findings can't be overlooked

## Open Questions

- Should the **blog route** become fully autonomous once a findings-driven `blog-author` update mode exists that needs no interactive briefing? Default today: **assisted**, because `blog-author`'s skill contract requires briefing inputs (topic-as-thesis, source list, slug, cross-language binding key) that can't be reconstructed from editorial findings alone. Revisit when `blog-author` (or a sibling skill/agent) ships a documented findings-driven update operation whose inputs are fully derivable from the existing post plus the findings report; the upstream signal to watch is a `blog-author` revision that adds such an operation.
- Should the convergence loop's **author-pass bound** (default 2) be tunable per repository, and should a repeatedly-escalating artefact feed a `continuous-improvement` signal? Default: a fixed bound of 2 with operator escalation, the simplest cap that prevents an unbounded loop. Revisit when accumulated `.audits/lektorat-auto-revise/` data shows a recurring class of artefacts that escalate every run (a sign the bound is wrong or the findings are structurally not fixable by an author).
- Should this layer ever consume findings for **blog posts** that `lektorat` produced under a consumer-side scope extension, given that `lektorat` §Scope and applicability (in this repository) doesn't list blog posts? Default: the process is **repository-agnostic** and consumes whatever conformant `findings.json` it's handed, however the upstream `lektorat` run produced it (in the blog consumer, `blog-author` step 7 already hands off to `lektorat-apply`). Revisit if the blog consumer's `lektorat` scope and this layer's blog route ever disagree on which blog artefacts are in scope.

## Sources

<!-- Authoritative external references the requirements above were validated against. -->

- [`spec/project/lektorat/`](../lektorat/en.md): the findings report shape, severity classification, audience binding, operations (`audit` / `patch` / `revise`), and semantic-preservation guarantees this layer orchestrates over.
- [`spec/project/audience-identification/`](../audience-identification/en.md): the audience artefact and identifier model the briefing composition resolves against.
- [`spec/project/prose-style/`](../prose-style/en.md): the EN voice/tone rules bound on the documentation route through `audience-doc-author`.
- [`spec/project/post-writing-style/`](../post-writing-style/en.md) and [`spec/project/post-audience-communication/`](../post-audience-communication/en.md): the writing-style and audience rules bound on the blog route through `blog-author`.
- The `audience-doc-author` agent contract (`agents/audience-doc-author.md`), which names a *"future orchestrating skill"* as its driver—the role this spec defines.
