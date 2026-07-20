# Per-artefact deep-rework triage — evidence (F-17, R-11)

One row per artefact from the phase-1 parallel triage (repo-revision 97048dd84aa59f4dad7773c5ece1ed30f7cb49b1). Verdict `none` = well-formed, no structural rework warranted. The Note column carries any minor (non-rework) conformance observation.

| Artefact | Kind | Plugin | Verdict | Note (minor, non-rework) |
|---|---|---|---|---|
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Minor: the body cites spec/project/test-pyramid-foundation/ for the Meszaros test-double vocabulary (path verified to exist) but this is not listed in see_also; not a rework sig... |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Line 32 prose says "read-only tools only (`Read`, `Bash`)" but frontmatter tools list is `Read, Bash, Glob, Grep`; the Glob/Grep omission in that one sentence is a minor doc lag... |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Agent classification is justified: the "Why this is an agent, not a skill" section grounds self-contained I/O, context-window isolation of high-volume hadolint/parse output, and... |
|  | agent | nolte-engineering | none | Governing spec spec/project/e2e-test-automation/ exists (en.md/de.md/templates); rationale, model pin, scope, procedure and hard rules all conform to agent-management/agent-revi... |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Governing spec spec/project/e2e-test-automation/ confirmed present (en.md, de.md, templates); rationale section fully justifies the agent (vs skill) type and the model:sonnet pi... |
|  | agent | nolte-engineering | none | The frontend family is crowded (frontend-usability-optimizer writer, webview-ui-expert read-only reviewer, webview-ui-optimize skill loop, fullstack-developer builder), but each... |
|  | agent | nolte-engineering | none | All referenced spec paths resolve (spec/claude/agent-management, spec/frontend/testability-identifiers, spec/project/test-pyramid-foundation). Rationale heading matches the spec... |
|  | agent | nolte-engineering | none | Governing spec/project/i18n-completeness/ (en.md, de.md) is present, so not a phantom. Named peer webview-ui-expert is deliberately boundaried (broad RTL/bootstrap/locale-switch... |
|  | agent | nolte-engineering | none | The audit-driven output path (.audits/observability-audit/<timestamp>/plan.md) is described in Step 4 of the Procedure, but the "Write effects" table (Targets/Preconditions rows... |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Governing spec spec/project/test-tier-integration/ (en.md, de.md) exists; rationale section explicitly justifies agent-over-skill and the sonnet model pin per spec/claude/agent-... |
|  | agent | nolte-engineering | none | Standard skill+scanner clustering: kpi-derive owns selection/definition/write, this agent owns read-only detection; tool restriction (Read/Glob/Grep) is load-bearing and the rat... |
|  | agent | nolte-engineering | none | Governing spec spec/project/license-check/ exists (en.md + de.md); the agent explicitly cites it plus spec/claude/agent-management §Tool access read-only exception. The "Why thi... |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Single detection responsibility, load-bearing read-only tool set (Read/Bash/Glob/Grep) with an explicit §Read-only Bash justification; spec/project/release-regression-scope/en.m... |
|  | agent | nolte-engineering | none | Governing spec spec/project/test-case-derivation/ exists (en.md + de.md), so not a phantom. Single body job (derive+write cases), no split signal. Type classification is justifi... |
|  | agent | nolte-engineering | none | Governing spec spec/project/test-cycle-code-adaptation/ (en.md + de.md) exists; body correctly delegates classification to test-result-analyzer, test-writing to tier generators,... |
|  | agent | nolte-engineering | none | Body inlines a fallback baseline for consumer installs lacking spec/, which is a documented pattern, not drift; no issue. |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none |  |
|  | agent | nolte-engineering | none | Declares Bash for a single read-only command (`git rev-parse --is-inside-work-tree`); this is explicitly justified under a dedicated "Read-only Bash justification" section per s... |
|  | skill | nolte-engineering | none | Governing spec spec/project/api-error-handling/ and the referenced spec/project/code-security-audit/ both exist (en.md + de.md). Family peers (dependency-audit, dockerfile-audit... |
|  | skill | nolte-engineering | none | Governing spec spec/project/dependency-audit/ exists (en.md + de.md) — not a phantom. The skill's Step 4 license pass overlaps in surface with the separate license-check skill, ... |
|  | skill | nolte-engineering | none |  |
|  | skill | nolte-engineering | none | Minor: the description names "Kubernetes runtime hardening" as an exclusion without an alternative, while the frontmatter dont_use_when routes that same case to quality-gate; a ... |
|  | skill | nolte-engineering | none |  |
|  | skill | nolte-engineering | none | Adjacent to dependency-audit, which also advertises an optional license-compliance pass, but the two carry explicit mutual dont_use_when boundaries and license-check is declared... |
|  | skill | nolte-engineering | none | Governing spec spec/project/monitoring-observability/ exists (en.md + de.md). Two operations (audit/plan) are facets of one capability, not a split. Pattern and scanner-agent pa... |
|  | skill | nolte-engineering | none |  |
|  | skill | nolte-engineering | none | No structural issues. The delegate-to-scanner + operator-dialogue + resumable-envelope shape matches the sibling audit skills (dockerfile-audit, observability-audit) and the ski... |
|  | skill | nolte-engineering | none |  |
|  | skill | nolte-engineering | none | Unlike its sibling audit skills (dockerfile-audit, observability-audit, dependency-audit, license-check) which each pair with a *-scanner agent, this read-only auditor has no co... |
|  | skill | nolte-engineering | none | Standard audit/patch/expert-review shape matching the mkdocs-structure-apply precedent family; governing spec spec/frontend/webview-ui-optimization/{en,de}.md and bundled refere... |
|  | agent | nolte-media | none |  |
|  | agent | nolte-media | none | Minor (non-blocking): Phases 1-4 embed full Python snippets inline in the body rather than invoking a bundled helper via ${CLAUDE_PLUGIN_ROOT}; the body itself notes "image-file... |
|  | skill | nolte-media | none | Governing spec spec/design/gemini-image-generation/ exists (en.md + de.md); body has clear operations, Hard rules, and an explicit skill-vs-agent rationale section. No structura... |
|  | skill | nolte-media | none | Peer skill gemini-image-handoff shares the Gemini model but is a deliberately distinct manual/no-API route (disambiguated in both artefacts' dont_use_when and gotchas), so it is... |
|  | agent | nolte-shared | none | Minor: the description references `spec/project/` doc-type specs generically and the body lists specific paths (audience-identification, readme-structure, release-notes-audience... |
|  | agent | nolte-shared | none | The name audience-review is an action-not-actor form rather than object-role, but this is an explicit documented exception in agent-management/en.md (AGENT_NAME_FORM_EXCEPTIONS)... |
|  | agent | nolte-shared | none | Minor only: frontmatter omits `resumable`, which is correct since the agent is fire-and-forget single-shot per agent-management §Resumable runs. No structural rework signal. |
|  | agent | nolte-shared | none |  |
|  | agent | nolte-shared | none |  |
|  | agent | nolte-shared | none | Declares Bash despite the read-only-agent invariant that normally bans it, but this is fully sanctioned: the required `## Read-only Bash justification` heading is present with a... |
|  | agent | nolte-shared | none | Single-job scope, fixed five-kind/five-resolution vocabulary sourced from spec/project/feature/, and tool restriction (no Edit/Write/Bash) matches the agent-review read-only inv... |
|  | agent | nolte-shared | none | Minor placement observation (not a rework signal): this code-bearing review agent lives in the nolte-shared root agents/ yet its family (code-security-reviewer, dependency-audit... |
|  | agent | nolte-shared | none | Fully conformant: mandatory `## Why this is an agent, not a skill` heading present with a named counter-dimension; `## Read-only Bash justification` section satisfies agent-mana... |
|  | agent | nolte-shared | none | All referenced paths resolve (spec/project/link-validation/, spec/claude/agent-management/, agent-review/, skill-vs-agent/, scripts/check_links.py). Mandatory heading "## Why th... |
|  | agent | nolte-shared | none | Carries a proper "Why this is an agent, not a skill" rationale (Hybrid pattern with the mermaid-diagrams-apply mutator skill), a fixed finding-kind/resolution vocabulary, and a ... |
|  | agent | nolte-shared | none | Minor: the agent frontmatter and body reference GitHub MCP tools plus a `gh` fallback (F-13 pilot), which is additive per spec/claude/mcp-tool-preference/ and not a structural i... |
|  | agent | nolte-shared | none | Body's "Tool restriction is load-bearing" bullet (line 33) and the §"Why this is an agent" text state "only `Bash` is declared", but frontmatter tools is [Bash, mcp__github__get... |
|  | agent | nolte-shared | none | No structural issue. The rationale section justifies the agent type via the skill-vs-agent Hybrid pattern; tools are minimal (Read, Glob) matching the read-only invariant; body ... |
|  | agent | nolte-shared | none | The §5a "Voice-and-tone spot check" applies editorial heuristics (passive voice, headings, bias-free terms) that touch lektorat-scanner's D4 style territory; it stays a bounded ... |
|  | agent | nolte-shared | none | Governing spec spec/project/quality-gate/{en,de}.md exists (not a phantom); rationale heading and read-only tool set conform. Minor non-blocking placement observation: this agen... |
|  | agent | nolte-shared | none | Distinct from its plan-phase reviewer peers (sprint-readiness-reviewer targets sprints, feature-consistency-reviewer targets features); no overlap. All five cited spec paths (pr... |
|  | agent | nolte-shared | none | All cited spec paths resolve (agent-management, agent-review, review-plan/§Severity scale, skill-vs-agent) and no phantom references exist. The type choice is justified with a m... |
|  | agent | nolte-shared | none | All referenced spec paths (spec/project/spec-readiness, spec/claude/review-plan, research-triangulate, agent-management, skill-vs-agent) exist in the tree; no ghost references. ... |
|  | agent | nolte-shared | none | All referenced spec paths resolve (spec/project/sprint/, spec/project/feature/, spec/claude/agent-management/); rationale uses the exact mandated heading; read-only tool set (Re... |
|  | agent | nolte-shared | none | Both referenced specs (spec/portfolio/tech-stack/, spec/portfolio/tech-stack-discovery/) exist, so no phantom-spec issue. The sibling tech-stack-fitness-reviewer is genuinely di... |
|  | agent | nolte-shared | none | All governing spec paths referenced in the body exist (spec/claude/agent-management/, spec/claude/review-plan/); severity vocabulary and model-pin justification cite them correc... |
|  | agent | nolte-shared | none | The "Tool restriction is load-bearing" bullet (body) enumerates the read-only tool set as "(`Read`, `Glob`, `Grep`, `Bash`)" but the frontmatter `tools` line also grants `mcp__g... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Minor boundary observation (not a rework driver): the skill's `validate` operation (§2, checklist-against-spec plus in-place mechanical fixes) overlaps in intent with the read-o... |
|  | skill | nolte-shared | none | Minor: the "Repo signals → fields" table and Operation-1 step 2 both restate the Component MUST-floor and the never-infer set (lifecycle/system/dependsOn/domain), a small intern... |
|  | skill | nolte-shared | none | Body carries substantial spec restatement (readability thresholds, LIX corridors, bilingual typography) that duplicates content owned by post-writing-style and readability-lix; ... |
|  | skill | nolte-shared | none | Governing spec spec/project/blog-author-trigger/ exists (en.md+de.md); rationale uses the mandated heading with a counter-dimension note; no phantom, no duplication with blog-au... |
|  | skill | nolte-shared | none | Governing spec spec/project/continuous-improvement/ and all cross-referenced specs (trusted-author-injection-guard, mcp-tool-preference, resumable-work) exist; bundled templates... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Uses the operation label `migrate` (brownfield) where sibling family skills use `scaffold`; deliberate, since greenfield skeleton is owned by mkdocs-structure-apply — not a rewo... |
|  | skill | nolte-shared | none | Minor only: dont_use_when lists docs-freshness-checker as an "alternative" but that target is an agent, not a skill — accurate as a routing pointer, not a defect. No structural ... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Minor: the description references `pull-request-workflow` as the alternative for PR templates, but that is a spec name rather than a sibling skill/agent (the PR skills are pull-... |
|  | skill | nolte-shared | none | Minor: operation 5 references `continuous-improvement` §Portfolio gap closure and `spec/claude/mcp-tool-preference/` — both are documentary spec pointers, not phantom operations... |
|  | skill | nolte-shared | none | The three operations (audit/patch/revise) share one detection inventory and entry point, which the §"Why this is a skill" counter-dimension explicitly justifies as intentional c... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Operation 4 (Diagram audit) states it "duplicates" the mermaid-diagram-reviewer agent's scan but frames the inline procedure as fallback under the sanctioned hybrid pattern per ... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Governing spec spec/project/mission/ exists (en.md canonical). Rationale section explicitly justifies skill-not-agent via persistent-artefact + per-step operator-gating dimensio... |
|  | skill | nolte-shared | none | Minor only: the audit/output-contract groupings restate the eleven spec-area names in three separate places (Operations §1, Output contract items 3 and the parenthetical); a sma... |
|  | skill | nolte-shared | none | Minor: the "Old patterns" / "Q2-2026 drift check" section embeds a dated historical record inside SKILL.md; time-stamped state living in the instruction file is slightly at odds... |
|  | skill | nolte-shared | none | Frontmatter (description/summary/use_when) advertises three operations (Audit/Render/Bootstrap) while the body defines four, adding a "Discover tech stack" operation (spec/portf... |
|  | skill | nolte-shared | none | No structural defects: governing spec spec/portfolio/portfolio-inflight-management/ exists (en.md+de.md), as do spec/claude/review-plan/ and spec/project/continuous-improvement/... |
|  | skill | nolte-shared | none | All spec paths it references exist (spec/project/project-structure/, mkdocs-structure/, resumable-work/) — no phantom. Rationale section uses the exact heading with a counter-di... |
|  | skill | nolte-shared | none | Minor: step 6.2 embeds an MCP go/no-go note (github:list_pull_requests preferred over gh pr list) which is fine but is the only operation with such tooling guidance; not a rewor... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Minor: the skill still carries the open question (Gotchas, line 169) about release-drafter re-runs stripping the marker pair, unverified against gh-plumbing's reusable-release-d... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Description cites the spec heading as "§Detail-level convention" while the actual heading is "Detail-level convention and refinement rule" (spec/project/roadmap/en.md:82); the b... |
|  | skill | nolte-shared | none | Minor: the skill leans heavily on four references/ files and three examples/ for load-bearing detail (i18n prohibition, per-surface dependencies), which keeps SKILL.md lean per ... |
|  | skill | nolte-shared | none | Minor only: the Update operation heading uses `Update` while the frontmatter description says "revise"; both map cleanly to the spec's lifecycle `update` verb, so this is cosmet... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Distinct from its family: skill-review/agent-review are per-artefact reviewers it dispatches, spec-drift-audit does spec-vs-impl reconciliation; dont_use_when and see_also disam... |
|  | skill | nolte-shared | none | All referenced spec paths resolve (skill-management, resumable-work, portfolio-inherited-spec-layer, review-plan). Delegations are non-redundant: readiness audit → spec-readines... |
|  | skill | nolte-shared | none | Governing spec mandates exactly four artifact sections `## Scope`, `## Summary`, `## Findings`, `## Processing log` (that order, exact headings) plus the review-plan four-level ... |
|  | skill | nolte-shared | none | All governing-spec paths referenced (spec/project/sprint, feature, roadmap, blog-author-trigger, spec/claude/resumable-work) exist on disk; no phantom references. Operations 1-4... |
|  | skill | nolte-shared | none | Both sprint-plan (step 6) and feature-decompose claim "canonical write authority" for `verifies_sprint_value`; the skill disambiguates by phase (decomposition-time vs planning-t... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Minor only: the discovery spec's §Discovery sequence declares a curated JS/TS `package.json` framework/language allowlist as first-class MUST signals; the SKILL.md body doesn't ... |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none |  |
|  | skill | nolte-shared | none | Minor: the skill states the plan gate as a MUST ("Never skip the plan gate ... MUST be filled") while the governing spec's §Lifecycle: Plan before work and §Claude Code session ... |
|  | skill | nolte-shared | none | Minor only: the body carries seven operations plus extensive Gotchas/Hard-rules; long but each is a distinct facet of the same schema-lifecycle contract, not drift. No action ne... |
