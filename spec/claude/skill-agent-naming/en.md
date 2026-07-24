# Skill and Agent Naming

Status: draft
Portfolio-Scope: portfolio

## Context

Until this spec existed, the naming convention for reusable Claude Code artifacts lived split across two owner specs: the skill form in `skill-management` §Frontmatter validation and the agent form in `agent-management` §Structure, with the exception lists mirrored a third time in `scripts/validate_skills.py`. The 2026-07 skills-and-agents audit showed what that split costs: reviewers cite two different anchors for one convention, the two halves drift in wording, and a consumer plugin (such as `claude-home-assistant`) has no single document to inherit. This spec consolidates the whole name-form convention into one **normative owner**. The former host sections in `skill-management` and `agent-management` now delegate here and restate nothing; on any discrepancy between this spec and an older restatement elsewhere, **this spec wins**.

Scope boundary: this spec owns the **form** of a name—its semantic shape, morphology, exceptions, and rename policy. The **character-level** constraints (1–64 chars, lowercase ASCII kebab-case, no leading/trailing hyphen, no `--`, reserved tokens `anthropic`/`claude`, no XML) stay owned by `skill-management` §Frontmatter validation and `agent-management` §Structure; the digest at the end of this document only points there.

Readers: skill and agent authors choosing a conformant name, reviewers citing one anchor for the whole name-form convention, `validate_skills.py` maintainers who mirror the exception lists, and consumer plugins inheriting the convention.

## Goals

- One normative home for the complete naming convention, inheritable by every portfolio plugin
- Deterministic review anchors: a name-form finding cites exactly one spec
- The validator's closed lists and this spec change in lockstep, never independently

## Non-Goals

- Character-level `name` validation (owned by the frontmatter-validation sections named above)
- Renaming any existing artifact (the standing naming-audit decision: suggestions only, no renames)
- Naming of specs, files, branches, or HA domain objects (`spec/ha/naming-conventions` in the HA repo governs Home Assistant entity/device naming—a different subject)

## Requirements

### Upstream baseline

- Anthropic's published convention prefers the **gerund form** for skill names (`processing-pdfs`); verb-noun and noun phrases are acceptable alternatives, but **mixed forms across one repository aren't** ([R1](#references)). This portfolio deliberately standardises on the alternatives below; the no-mixing half of the upstream rule is the part that binds.

### Skill names: `<object-noun>-<action>`

- **MUST** name every skill in verb-noun form, concretely `<object-noun>-<action>`: the leading tokens name the object, the **trailing** token names the action—expressed either as a finite verb (`pull-request-create`, `roadmap-init`, `feature-decompose`, `mission-define`) or as a verb-derived action noun (`dependency-audit`, `gemini-image-handoff`, `skill-management`)
- The action sits **last**, mirroring the agent-side order where the role-noun sits last
- The action vocabulary is **open at rule level**: any finite verb or verb-derived action noun qualifies (`add`, `augment`, `scaffold`, `migrate`, `sync`, `determine`, `release`, and peers). The validator's `SKILL_ACTION_TOKENS` list is a surface mirror that grows with the portfolio's actual tokens—never a semantic gate that outlaws a legitimate verb
- **Closed exceptions** (a reviewer **MUST NOT** flag these; the list is exhaustive): `spec` (bare noun), `yaml-json-schema` (noun compound), `quality-gate` (trailing noun names a thing, not an action). All three predate the convention; renaming would break every consumer call site—and, for `spec`, the `$ref`/cross-reference machinery. Every *new* skill **MUST** follow the convention

### Agent names: `<subject>-<role-noun>`

- **MUST** name every agent in object-role form, `<subject>-<role-noun>`: the trailing token is the role the agent plays over the leading subject (`code-security-reviewer`, `feature-consistency-reviewer`, `portfolio-manifest-collector`, `vocab-drift-scanner`, `lektorat-scanner`)
- The trailing role-noun almost always carries `-er`/`-or`/`-ist` morphology (`-reviewer`, `-checker`, `-scanner`, `-collector`, `-curator`, `-enforcer`, `-extractor`, `-generator`, `-author`, `-developer`); an actor noun naming a role without that morphology is still conformant; `webview-ui-expert` is the standing case
- **Closed exceptions** (a reviewer **MUST NOT** flag these; the list is exhaustive): `png-to-transparent-svg` (a transformation phrase with no role token) and `audience-review` (trailing `review` names an action, not an actor). Renaming either would break every `subagent_type:` call site; the breakage cost outweighs the coherence gain. Every *new* agent **MUST** follow the convention

### One form per artifact type, per plugin

- **MUST** keep naming consistent across the whole plugin—one convention per artifact type; mixing a gerund or free-form name into either surface is itself the discoverability anti-pattern `plugin-scoping` §Namespace and naming coherence warns against
- Domain plugins that inherit this corpus (for example `claude-home-assistant`) **MAY** prepend a fixed domain prefix (`ha-`) to every artifact name; the form after the prefix follows the rules above unchanged (`ha-config-flow-augment`, `ha-blueprint-author`)
- Inheriting plugins audit their surface against this spec's **rules**, not against the nolte-shared validator lists verbatim, and **MUST** declare their own closed exception lists in their spec-index README under the same discipline (closed, greppable, reviewer MUST NOT flag). A **family-suffix exception** (one deliberate, uniform suffix naming an artifact family, such as a `*-solution` front-door family) qualifies when it's declared there and stays internally consistent

### Rename policy

- Renaming an existing artifact is a **breaking change** for every consumer call site and **MUST** ship as a new artifact plus a deprecation note on the old one, never as a silent flip (per `skill-vs-agent` §Portfolio-wide consistency)
- A future coordinated portfolio rename (for example flipping to gerund form) **MAY** happen with a deprecation period; until such a change ships, the forms above are the rule
- The standing 2026 naming-audit decision holds: form deviations in the existing surface are **suggestions to observe**, never rename mandates

### Binding to `scripts/validate_skills.py`

- `scripts/validate_skills.py` operationalises this spec as the **Suggestion-grade** `check_name_form` (a form deviation is a discoverability smell, not a platform failure) with four mirrored closed lists: `SKILL_ACTION_TOKENS`, `SKILL_NAME_FORM_EXCEPTIONS`, `AGENT_ROLE_NOUNS`, `AGENT_NAME_FORM_EXCEPTIONS`
- **MUST** change this spec and those lists in the **same PR** whenever either moves; a list entry without its spec counterpart (or vice versa) is a defect

### Character-level digest (owned elsewhere)

For convenience only—the normative rules live in `skill-management` §Frontmatter validation and `agent-management` §Structure: 1–64 characters, lowercase ASCII letters/digits/hyphens, no leading/trailing hyphen, no `--`, no XML, reserved tokens `anthropic`/`claude` banned in `name` (narrow documented exception via `## Reserved-token rationale`), generic names (`helper`, `utils`, `tools`, `documents`, `data`, `files`) banned.

## Acceptance Criteria

- [ ] `skill-management` and `agent-management` contain no normative restatement of the form convention—only the delegation pointer to this spec
- [ ] Every reviewer-facing citation of the name-form check (`skill-review`, `skills-agents-sweep`, the authoring skills) anchors on this spec
- [ ] The four validator lists match this spec's exception and morphology sets exactly
- [ ] `spec/README.md` indexes this spec; en/de stay structurally in sync

## References

- [R1] Skill authoring best practices, Anthropic platform docs: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- [R2] `plugin-scoping` §Namespace and naming coherence: `spec/claude/plugin-scoping/`
- [R3] Character-level owners: `spec/claude/skill-management/` §Frontmatter validation · `spec/claude/agent-management/` §Structure
- [R4] `scripts/validate_skills.py` (`check_name_form` and the four closed lists)

## Open Questions

_None at this time._
