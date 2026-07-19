# Skill and Agent Frontmatter Field Reference

Status: draft
Portfolio-Scope: local

## Context

A skill (`SKILL.md`) and an agent (`agents/<name>.md`) both carry YAML frontmatter, and the rules for that frontmatter are spread across three specs: `skill-management` owns the skill fields, `agent-management` owns the agent fields, and `skill-agent-catalog` owns the catalog/routing fields (`phase`, `summary`, the use-case metadata). Each of those specs is complete for its own surface, but there's no single place that answers the two questions an author or reviewer asks most often: *what is the full set of fields I may write, and which of them are portable Claude Code standard fields versus this repository's own inventions?* Without that map, the standard-versus-invention distinction lives only in scattered prose (a parenthetical "extends the formal Agent Skills spec" here, a "nolte-shared plugin choice" there), and an author can't tell at a glance whether dropping a field breaks portability to a non-Claude-Code runtime or merely drops a house-local catalog feature.

This spec is that map. It's a **descriptive, aggregating reference**: for every skill- and agent-frontmatter field it records the field's task, type, limits, required/optional status, an explicit **provenance marker** (Anthropic/Claude Code standard, with the upstream source—versus nolte-local invention), and a back-reference to the spec that **normatively owns** the field's rules. It deliberately doesn't restate those rules as a second source of truth; on any discrepancy the owner spec wins. It ships alongside a machine-readable JSON-Schema companion that encodes the same field set at the parse-error level, and it defines the maintenance process that keeps the reference, the schema, the owners, and `scripts/validate_skills.py` from drifting apart.

## Goals

- One consolidated reference covering **every** skill- and agent-frontmatter field in a single document, so an author or reviewer sees the whole surface at once.
- An explicit **provenance marker** per field—portable Claude Code standard (with its upstream source) versus non-portable nolte-local invention—so the portability consequence of using or dropping a field is visible.
- A **back-reference** from every field to the spec that normatively owns its rules, so the reader can reach the authoritative limit without this document having to restate (and risk forking) it.
- A machine-readable **JSON-Schema companion** at the parse-error level that mirrors the field set for tooling to consume.
- A **maintenance process** that binds any new or changed field to a provenance review and a sync gate across the owners, the schema, and the validator.

## Non-Goals

- **Restating or replacing the owner specs' rules.** This reference maps and points; it doesn't fork. The normative limits stay in `skill-management`, `agent-management`, and `skill-agent-catalog`. Promoting this document to the single normative field registry (the rejected "Model B") is explicitly out of scope.
- **Changing `scripts/validate_skills.py` behaviour.** Wiring the JSON-Schema companion into the validator is a maintenance follow-up, not part of this spec.
- **The skill-versus-agent format decision** (owned by `skill-vs-agent`), **plugin scoping** (owned by `plugin-scoping`), and the **catalog rendering** of these fields (owned by `skill-agent-catalog`).
- **Runtime semantics of the Claude Code standard fields** beyond citing the upstream source; the authoritative behaviour is Anthropic's, linked from the References.

## Requirements

### Normative model—descriptive and aggregating

- **MUST** be authored as a **descriptive, aggregating reference**: for every field it records the field's attributes and points back to the spec that owns the field's normative rules. It **MUST NOT** be presented as the authoritative registry that the owner specs defer to.
- **MUST** carry, for every field it documents, a back-reference to the **normative owner** section (`skill-management`, `agent-management`, or `skill-agent-catalog`); the limits and allowed values shown here are a **convenience digest** of that owner, never a competing definition.
- **MUST** resolve any discrepancy between this reference and an owner spec in favour of the **owner**; a divergence is a maintenance defect in this document (§Maintenance), not a new rule.
- **MUST NOT** introduce a field rule, limit, or allowed value that no owner spec (or the upstream Claude Code / Agent Skills source) already defines; a field this reference would newly constrain belongs in its owner spec first.

### Field reference contract

- **MUST** document, for **every** field in §Field reference, all seven attributes: **field name**, **applies-to** (`skill` / `agent` / `both`), **type**, **limits or allowed values**, **required/optional status**, **provenance marker**, and **normative owner**.
- **MUST** cover **both** skills and agents in this one document, using the shared `applies-to` axis so a field common to both (for example `name`, `description`, `model`, and the catalog fields) is described once rather than twice.
- **MUST** mark a field **required** only where its owner spec makes it a `MUST`: `name` and `description` for both objects, `phase` for both objects, and `distribution` for agents. Every other field is **optional** (some carry a conditional `MUST`, for example `resumable` when a skill or agent spans more than one approval gate—noted in the field's row and left to the owner).
- **MUST** keep the field name and every technical value in the reference verbatim from the source; field names are identifiers and aren't translated between the canonical and translated files.

### Provenance taxonomy

- **MUST** classify every field with exactly one **provenance marker**:
  - **Standard**: a field defined by the formal Agent Skills specification ([R1](#references)), the Anthropic platform validator ([R2](#references)), or Claude Code's documented frontmatter ([R3](#references) for skills, [R7](#references) for agents). Standard fields are portable to the Claude Code runtime; the Agent-Skills-spec subset (`name`, `description`) is portable to any conformant Agent Skills runtime.
  - **nolte**: a field this repository invented for catalog rendering, routing, or house convention. A nolte field isn't portable: a non-nolte runtime ignores it, and the Anthropic platform validator treats unknown fields per its own rules.
- **MUST** cite, for every **Standard** field, the upstream source ([R1](#references), [R2](#references), [R3](#references), [R7](#references)) so the portability claim is checkable.
- **MUST** record every field currently invented by this repository as **nolte**: `distribution`, `tags`, `phase`, `summary`, `summary_<lang>`, `use_when`, `dont_use_when`, `see_also`, `examples`, and `resumable`.
- **MUST** preserve the two cross-cutting reservations the owners already declare: the reserved tokens `anthropic` and `claude` are banned in `name` (not in other fields), and the underscore prefix (for example `_translation-pending`) is reserved for catalog-generator auto-tags and **MUST NOT** appear in author-declared `tags`.

### Machine-readable companion

- **MUST** ship a JSON-Schema companion at `spec/schemas/skill-agent-frontmatter-v1.0.schema.yaml` (JSON-Schema draft 2020-12), in the house style of `spec/schemas/spec-config-v1.0.schema.yaml` and `portfolio/schemas/tech-stack-v1.0.schema.yaml`.
- **MUST** restrict the schema to the **parse-error class** only—field presence, type, primitive limits (string length, list length, enum membership, pattern)—and **MUST NOT** encode semantics that would fork an owner rule (for example the cross-artifact resolvability of `dont_use_when[].alternative`, which stays an audit-time check in `skill-agent-catalog`).
- **MUST** keep the schema consistent with §Field reference: every field marked required here is `required` there, every enum here is an `enum`/`pattern` there, and every provenance marker maps to a schema description note.
- **MAY** be consumed by `scripts/validate_skills.py` in a later change; the schema is a companion the validator can adopt, and this spec doesn't require that wiring.

### Maintenance

- **MUST** carry a `## Maintenance` section that governs how a field is **added, changed, or removed** in this reference.
- **MUST** require, for any new or changed field, a **provenance review**: the author classifies the field **Standard** (and links the upstream source that introduced it) or **nolte** (and names the owner spec and the routing/catalog reason), and records the outcome in the field's row.
- **MUST** require a **sync gate** on any field change: the reference row, the JSON-Schema companion, the normative owner spec, and (where the field is validator-enforced) `scripts/validate_skills.py` are updated in the **same change** or the divergence is called out explicitly; a field that appears in one surface but not the others is a defect.
- **MUST** bind the sync gate to a **PR checklist item** so a reviewer confirms the four surfaces agree before merge.
- **SHOULD** re-run the provenance review when Claude Code or the Agent Skills spec ships a new frontmatter field, so a field that becomes standard upstream is re-marked from **nolte** (or absent) to **Standard** rather than silently staying mislabeled.

## Field reference

The tables below are a **convenience digest**. The **Owner** column names the normative source; on any discrepancy the owner wins (§Normative model). Field names and values are verbatim identifiers and aren't translated between language files.

Provenance markers: **Standard·AgentSkills** (Agent Skills spec [R1], portable to any conformant runtime), **Standard·Platform** (Anthropic platform validator [R2]), **Standard·CC** (Claude Code frontmatter [R3]/[R7], portable to the Claude Code runtime only), **nolte** (this repository's invention, non-portable).

### Required fields

| Field | Applies to | Type | Limits / allowed values | Provenance | Owner |
|---|---|---|---|---|---|
| `name` | both | string | 1–64 chars; lowercase ASCII letters/digits/hyphens; no leading/trailing hyphen; no `--`; no reserved token `anthropic`/`claude`; no XML tags; equals folder/file name | Standard·AgentSkills + Standard·Platform | `skill-management` §Frontmatter validation · `agent-management` §Structure |
| `description` | both | string | non-empty; ≤1024 chars; third person; states *what* / *when* / *don't-use-for-X→Y* shape; no XML tags; agents additionally: no `user:`/`assistant:`/`<commentary>`/`<example>` blocks, tightened delimitation chains | Standard·AgentSkills + Standard·Platform | `skill-management` §Frontmatter validation · `agent-management` §Structure / §Description contract |
| `distribution` | agent | enum | exactly `plugin` or `project` | nolte | `agent-management` §Distribution |
| `phase` | both | enum | one of `vision`, `plan`, `design`, `build`, `review`, `quality`, `close-release`, `cross-cutting`; never a list | nolte | `skill-agent-catalog` §Phase classification |

### Standard optional fields—Claude Code, skill surface

| Field | Applies to | Type | Limits / allowed values | Provenance | Owner |
|---|---|---|---|---|---|
| `when_to_use` | skill | string | combined `description` + `when_to_use` under 1,536 chars (runtime truncates beyond) | Standard·CC | `skill-management` §Frontmatter validation / §Runtime & lifecycle |
| `argument-hint` | skill | string | free-form hint shown for slash-command arguments | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `arguments` | skill | string | argument declaration for the slash command | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `disable-model-invocation` | skill | boolean | `true` bars model-driven invocation (user-invoked only); blocks subagent `skills:` preload; don't set on a skill another skill dispatches mid-flow | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `user-invocable` | skill | boolean | whether the skill is exposed as a `/`-command | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `allowed-tools` | skill | list of strings | a **permission grant** (pre-approved calls), not a restriction | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `context` | skill | enum | `fork`: run the skill in a forked subagent context (with `agent`) | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `agent` | skill | string | agent type providing tools/model when `context: fork` | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `paths` | skill | list of globs | gate on **automatic** invocation only; explicit `/<plugin>:<name>` always works; not a routing-budget lever | Standard·CC | `skill-management` §Runtime & lifecycle awareness |
| `shell` | skill | string | shell binding for the skill's command execution | Standard·CC | `skill-management` §Runtime & lifecycle awareness |

### Standard optional fields—Claude Code, agent surface

| Field | Applies to | Type | Limits / allowed values | Provenance | Owner |
|---|---|---|---|---|---|
| `tools` | agent | list of strings | least authority; **omitting grants every inherited tool** (a sprawl trap); read-only agents carry no write/edit/exec tools; never list `Agent` | Standard·CC | `agent-management` §Tool access |
| `disallowedTools` | agent | list of strings | denylist subtracted from the inherited set; applied before `tools` | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `permissionMode` | agent | enum | `default`/`acceptEdits`/`auto`/`dontAsk`/`bypassPermissions`/`plan`; **ignored for `distribution: plugin`** (MUST NOT set) | Standard·CC | `agent-management` §Plugin-distribution security constraints |
| `maxTurns` | agent | integer | caps agentic turns before stopping | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `skills` | agent | list of strings | preloads full skill content at startup; skips `disable-model-invocation: true` skills | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `mcpServers` | agent | mapping / refs | per-subagent MCP servers; **ignored for `distribution: plugin`** (MUST NOT set) | Standard·CC | `agent-management` §Plugin-distribution security constraints |
| `memory` | agent | enum | `user`/`project`/`local`; enables Read/Write/Edit and memory-curation prompt | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `background` | agent | boolean | always run as a background task; permissions pre-approved | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `isolation` | agent | enum | `worktree`: run in a temporary git worktree | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `color` | agent | enum | `red`/`blue`/`green`/`yellow`/`purple`/`orange`/`pink`/`cyan` | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |
| `initialPrompt` | agent | string | first user turn when the agent runs as the main session via `--agent` | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields |

### Standard optional fields—Claude Code, both surfaces

| Field | Applies to | Type | Limits / allowed values | Provenance | Owner |
|---|---|---|---|---|---|
| `model` | both | string | model alias (`sonnet`/`opus`/`haiku`), a full model ID, or `inherit`; **default `inherit`** when omitted | Standard·CC | `agent-management` §Model selection · `skill-management` §Runtime & lifecycle awareness |
| `effort` | both | enum | `low`/`medium`/`high`/`xhigh`/`max`; overrides session effort | Standard·CC | `agent-management` §Optional Claude Code frontmatter fields · `skill-management` §Runtime & lifecycle awareness |
| `hooks` | both | mapping | lifecycle hooks; on agents **ignored for `distribution: plugin`** (MUST NOT set) | Standard·CC | `skill-management` §Runtime & lifecycle awareness · `agent-management` §Plugin-distribution security constraints |

### nolte optional fields—catalog, routing, house convention

| Field | Applies to | Type | Limits / allowed values | Provenance | Owner |
|---|---|---|---|---|---|
| `tags` | both | list of strings | lowercase ASCII kebab-case; each ≤30 chars; ≤5 entries; no entry begins with `_` (reserved for generator auto-tags) | nolte | `skill-management` / `agent-management` §Tag vocabulary · `skill-agent-catalog` |
| `summary` | both | string | ≤200 chars; plain string; English (canonical) | nolte | `skill-agent-catalog` §Per-language short summary |
| `summary_<lang>` | both | string | ≤200 chars; plain string; one per additional docs language (for example `summary_de`) | nolte | `skill-agent-catalog` §Per-language short summary |
| `use_when` | both | list of strings | ≤6 entries; each ≤120 chars; one trigger scenario per entry | nolte | `skill-agent-catalog` §Use-case metadata |
| `dont_use_when` | both | list of mappings | keys `situation` (≤120 chars) + `alternative` (a discoverable artifact `name`); ≤6 entries; `alternative` must resolve or the docs build fails | nolte | `skill-agent-catalog` §Use-case metadata |
| `see_also` | both | list of strings | ≤8 entries; each a discoverable artifact `name`; must resolve | nolte | `skill-agent-catalog` §Use-case metadata |
| `examples` | both | list of mappings | keys `prompt` (≤200 chars) + `outcome` (≤200 chars); ≤4 entries | nolte | `skill-agent-catalog` §Use-case metadata |
| `resumable` | both | boolean | `true` when the artifact spans more than one approval gate or named phase; then `description` must mention resume support | nolte | `skill-management` / `agent-management` §Resumable runs · `resumable-work` |

### Cross-cutting reservations

- **Reserved tokens.** `anthropic` and `claude` **MUST NOT** appear anywhere in `name`; other fields (`description`, `tags`, `summary`, …) MAY mention them. A narrow closed exception exists for artifacts that author a Claude Code / Anthropic surface, gated by a `## Reserved-token rationale` body section—see `skill-management` §Frontmatter validation and `agent-management` §Structure.
- **Reserved tag prefix.** A leading underscore (`_translation-pending`) marks a generator-emitted auto-tag; author-declared `tags` **MUST NOT** use it—see `skill-agent-catalog` §Per-language short summary.
- **No per-artifact version field.** Neither skills nor agents carry a `version` or compatibility field; versioning is plugin-scoped and per-artifact history is git—see `skill-management` §Distribution and `agent-management` §Distribution.

## Maintenance

This reference stays true only if it changes in lockstep with the surfaces it maps. A field lives in up to four places: this reference row, the JSON-Schema companion, the normative owner spec, and `scripts/validate_skills.py` (when the field is validator-enforced). The process below keeps them aligned.

**When a field is added, changed, or removed:**

1. **Provenance review.** Classify the field **Standard** (name the upstream source—Agent Skills spec, Anthropic platform, or Claude Code docs—that introduced it) or **nolte** (name the owner spec and the routing/catalog reason). Record the outcome in the field's §Field reference row.
2. **Update the owner first.** The normative rule lives in `skill-management`, `agent-management`, or `skill-agent-catalog`. Change the owner, then update this reference's digest to match—never the reverse.
3. **Sync the four surfaces in one change.** The §Field reference row, `spec/schemas/skill-agent-frontmatter-v1.0.schema.yaml`, the owner spec, and (if validator-enforced) `scripts/validate_skills.py` are updated together, or the deliberate divergence is stated explicitly. A field present in one surface but missing from another is a defect.
4. **Keep the schema at the parse-error class.** A new limit that's a primitive constraint (length, enum, pattern) goes into the schema; a cross-artifact or semantic check (resolvability, phase-earliest heuristic) stays an audit-time rule in the owner, **not** a schema constraint.
5. **Re-mark on upstream change.** When Claude Code or the Agent Skills spec ships a new frontmatter field, or promotes one, re-run the provenance review so a field that becomes standard upstream is re-marked from **nolte** (or absent) to **Standard**.

**PR checklist item** (added to any PR that touches a frontmatter field's definition):

- [ ] Frontmatter field change: provenance reviewed, and the §Field reference row, the JSON-Schema companion, the owner spec, and `validate_skills.py` (if enforced) all agree—or the divergence is stated.

## Acceptance Criteria

- [ ] `spec/claude/skill-agent-frontmatter/en.md` (canonical) and `de.md` (translation) exist, `Status: draft`, `Portfolio-Scope: local`, structurally in sync.
- [ ] Every field in §Field reference declares all seven attributes (name, applies-to, type, limits/allowed values, required status via table placement, provenance, owner).
- [ ] Both skills and agents are covered in the one document via the `applies-to` axis; no field common to both is described twice.
- [ ] Exactly `name`, `description`, `phase` (both) and `distribution` (agent) are placed as required; every other field is optional.
- [ ] Every field carries exactly one provenance marker; every **Standard** field cites an upstream source ([R1](#references), [R2](#references), [R3](#references), [R7](#references)); the ten nolte fields (`distribution`, `tags`, `phase`, `summary`, `summary_<lang>`, `use_when`, `dont_use_when`, `see_also`, `examples`, `resumable`) are marked **nolte**.
- [ ] Every field row names a normative owner section, and the document states the owner wins on any discrepancy.
- [ ] `spec/schemas/skill-agent-frontmatter-v1.0.schema.yaml` exists (draft 2020-12), covers the parse-error class only, and is consistent with §Field reference (required set, enums, limits).
- [ ] A `## Maintenance` section defines the provenance review, the four-surface sync gate, and a PR checklist item.
- [ ] The document restates no owner limit as a competing definition; each limit shown is a digest with a back-reference.
- [ ] `task test` passes and the changed spec prose is Vale-clean (run from the worktree).

## References

- [R1] Agent Skills, formal specification: <https://agentskills.io/specification>
- [R2] Skill authoring best practices, Anthropic platform docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R3] Extend Claude with skills, Claude Code docs: <https://code.claude.com/docs/en/skills>
- [R4] `skill-management` (normative owner of skill frontmatter): `spec/claude/skill-management/`
- [R5] `agent-management` (normative owner of agent frontmatter): `spec/claude/agent-management/`
- [R6] `skill-agent-catalog` (normative owner of the catalog/routing fields): `spec/claude/skill-agent-catalog/`
- [R7] Create custom subagents, Claude Code docs: <https://code.claude.com/docs/en/sub-agents>

## Open Questions

_None at this time._
