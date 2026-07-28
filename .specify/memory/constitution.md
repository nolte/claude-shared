<!--
Sync Impact Report
==================
Version change: (unfilled template) → 1.0.0
Bump rationale: Initial ratification. Every placeholder token replaced with concrete,
  repository-derived governance. MAJOR by definition — the first binding version.

Modified principles: none (no prior version existed)

Added sections:
  - Core Principles I–V (Spec-Anchored Change, English-Canonical Bilingual Parity,
    Isolated Working Copies, Green Gate Before Merge, Distribution-Contract Plugin Scoping)
  - Delivery Constraints
  - Development Workflow
  - Governance

Removed sections: none

Templates requiring updates:
  ✅ .specify/templates/plan-template.md — "Constitution Check" gate is generic
     ("[Gates determined based on constitution file]"); it resolves against the five
     principles below without edit. Complexity Tracking table covers Principle V waivers.
  ✅ .specify/templates/spec-template.md — mandatory sections (User Scenarios & Testing,
     Requirements, Success Criteria, Assumptions) conflict with no principle; the
     spec/ six-section contract governs spec/ artifacts, not .specify/specs/ artifacts.
  ✅ .specify/templates/tasks-template.md — phase categorization is principle-neutral;
     Principle IV is satisfied by the Polish phase invoking `task check`.
  ✅ .claude/skills/speckit-*/SKILL.md — all eleven reference
     `.specify/memory/constitution.md` generically; no agent-specific or outdated
     command names remain (hyphen form matches integration.json `invoke_separator`).
  ✅ CLAUDE.md, README.md — no principle contradicts current runtime guidance; the
     constitution restates their non-negotiables rather than amending them.

Deferred TODOs: none
-->

# claude-shared Constitution

## Core Principles

### I. Spec-Anchored Change (NON-NEGOTIABLE)

Every change to runtime code, CI configuration, plugin assets (`skills/`, `agents/`,
`.claude-plugin/`), or repository documentation MUST either implement an existing
specification under `spec/` or be itself a spec revision. A change that satisfies neither
path is a defect, not a shortcut.

- Every pull request touching paths outside `spec/` MUST carry at least one
  `Refs spec/<topic>/<slug>/` line in its **Linked issues** section.
- Every `skills/<name>/SKILL.md` and every `agents/<name>.md` MUST cite at least one spec
  it implements, in frontmatter `description` or body text.
- No Claude Code prompt — system prompt, slash-command argument, agent prompt, chat
  instruction — is an authoritative source of an implementation decision. When prompt and
  spec disagree, the spec wins and the prompt is corrected.
- `exp/`-prefixed exploration branches MAY proceed without a spec anchor, including
  throwaway merges into `develop`. The anchor obligation engages at promotion to `feat/`,
  `fix/`, `chore/`, or `docs/` — promoting without one is forbidden.

Rationale: without this, decision rationale accumulates in ephemeral prompts and chat
history, and `spec/` degrades from living foundation to stale snapshot. Traceability,
reproducibility, and transparency all rest on this single anchor rule.

### II. English-Canonical Bilingual Parity

English is the canonical authoring language; every other configured language is a
structurally identical translation, written in the **same authoring step** as the canonical
file — never deferred to a follow-up commit.

- The language matrix resolves from `spec/.spec-config.yml` (`canonical_language`,
  `languages`) — one declaration point for `spec/` and `docs/` alike.
- An authoring step MUST NOT report success while any configured language version of a
  touched page is missing from disk. File renames and deletions propagate symmetrically
  across every language tree.
- Translations preserve heading depth, order, and count; frontmatter key sets; and the
  count and order of bullets, table rows, checklist entries, and code blocks. Heading and
  display-string *text* is translated; *structure* and portfolio-wide identifiers are not.
- German words MUST NOT appear in an English canonical file, and MUST NOT be silenced via
  vocabulary accept-lists — rephrase in English instead.
- `README.md` is English-only and exempt from the translation contract.

Rationale: partial writes surface only at the next freshness audit, by which point the
canonical page has drifted and the translation gets reconstructed from a stale snapshot.

### III. Isolated Working Copies

The primary checkout stays on `develop` at all times. Every change to specs, skills,
agents, or docs happens in a dedicated worktree branched off `develop`.

- Creating, switching to, or committing a `feat/`, `fix/`, `chore/`, `docs/`, or `exp/`
  branch in the primary checkout is forbidden — even when exactly one feature is in flight.
- Worktrees live under `${NOLTE_WORKTREE_ROOT:-~/repos/.worktrees}/claude-shared/<slug>/`,
  created via `task worktree:add -- <branch> [slug]`. Nesting a worktree under
  `.claude/worktrees/` is forbidden.
- Before substantive work begins in a new worktree, a foundational implementation plan MUST
  exist at `.resume/<slug>/plan.md`.
- Substantive work runs as a **top-level Claude Code session started from the worktree**,
  not a dispatched subagent — only top-level sessions are recoverable via `claude --resume`.

Rationale: parallel work is the normal case here, and an unrecoverable session or a dirty
integration branch costs more than the discipline does. Two enforcement layers already
exist (a `PreToolUse` guard hook and a pre-commit guard); this principle is what they
enforce.

### IV. Green Gate Before Merge

`task check` is the aggregate quality gate, composed from the repository's existing
Taskfile targets. It MUST run identically from a local workstation and from CI — no
environment branching that makes one stricter than the other.

- The gate MUST run every category the repository has code for. A gate that silently drops
  a category MUST NOT report `pass`; a category whose tooling was not detected reports
  `skipped`, which is distinct from `pass`.
- The four CI jobs gating `develop` — `lint`, `test`, `docs`, `links` — MUST all be green
  before a pull request merges. Merge labels are applied only after checks are green.
- The gate MUST NOT apply ignore rules that are not declared in the repository's own
  configuration files.
- A timed-out category reports `timeout`, not `fail`, and MUST NOT be retried
  automatically — retry is a human decision once the root cause is known.

Rationale: when CI is the first place a failure surfaces, review cycles burn on issues a
local gate would have caught seconds after the edit.

### V. Distribution-Contract Plugin Scoping

This repository ships four plugins from one tree. A plugin split MUST be justified by a
difference in **distribution contract** — a different consumer audience or a different
runtime/dependency requirement — never by topic affinity or artifact count.

- All four plugins version in **lockstep**, on one release line equal to the repository's
  release tag. Each plugin's `plugin.json` `version` and `marketplace.json`
  `metadata.version` are aligned together by the `chore(release): <tag>` bump.
- Plugin-owned skills MUST NOT be copied into a consumer's `.claude/skills/`. Distribution
  happens through the plugin marketplace, and only through it.
- Adding a fifth plugin, or moving a capability between plugins, MUST cite the
  distribution-contract difference that justifies it, per
  `spec/claude/plugin-scoping/` §"When to split into a separate plugin".

Rationale: splitting on topic multiplies install-time weight for every consumer without
giving any of them a reason to care. Splitting on contract is what earns the extra
manifest.

## Delivery Constraints

**Branch roles.** `develop` is the integration branch; all feature work lands there by pull
request. `main` is a presentation-only branch that always equals the most recently published
GitHub Release, written exclusively by release automation. Manual commits, pushes, or merges
to `main` are forbidden — including for hotfixes, which flow as ordinary `fix/` pull
requests against `develop` followed by a patch release.

**Branch names and commit types.** Feature branches use one of `feat/`, `fix/`, `chore/`,
`docs/`, or `exp/`, identical to the Conventional Commits types used in pull-request titles,
so branch name and commit type align without translation.

**Branch protection as code.** Protection rules are declared in `.github/settings.yml` and
synchronized through the Probot Settings app. Ad-hoc configuration in the GitHub UI is
forbidden.

**Sequential merges.** Pull requests merge into `develop` one at a time, with a rebase
between merges.

**Generated configuration is English.** All generated configuration files
(`.github/*.yml`, `Taskfile.yml`, workflow YAML) are written in English regardless of the
language used in conversation, for portfolio consistency.

## Development Workflow

**Authoring paths are not optional.** Each artifact class has exactly one authoring entry
point, because the entry point is what performs the duplicate check, the translation
pairing, and the index regeneration:

| Artifact | Entry point |
| --- | --- |
| Specification under `spec/` | `/nolte-shared:spec` |
| Skill or agent | `/nolte-claude-dev:skill-management` |
| Pull request | `/nolte-shared:pull-request-create` |
| Repository scaffolding | `/nolte-shared:project-structure-apply` |

A spec written outside the `spec` skill is a drift finding regardless of how good its
content is.

**Dogfooding.** This repository is the reference adopter of every spec it ships. A spec
proves it is livable here before downstream repositories adopt it. Development sessions load
all four in-repo plugins via `task plugin:reload`.

**Audit findings resolve two ways only.** Every finding from `spec-drift-audit`,
`workflow-health`, `quality-gate`, `docs-freshness`, or manual observation lands as either a
code change implementing an existing spec, or a spec revision recording the new reality. A
third path — code change without a spec anchor — is itself a finding.

**Spec Kit surface.** Artifacts under `.specify/` (this constitution, `specs/<feature>/`
plans and task lists) are workflow scaffolding for the Spec Kit commands. They do not
replace `spec/`: the `spec/` corpus remains the normative authority for portfolio behaviour,
and a Spec Kit plan that contradicts a published spec is wrong by Principle I.

## Governance

**Authority.** This constitution supersedes ad-hoc practice, undocumented convention, and
any Claude Code prompt. It does not supersede the `spec/` corpus, which it summarizes: where
this document and a published spec disagree, the disagreement is a defect. Resolve it by
amending whichever is wrong in the same change-set — never by silently following one and
ignoring the other.

**Amendment procedure.** Amendments follow the same path as any other change: a dedicated
worktree, a pull request against `develop`, and a `Refs spec/<topic>/<slug>/` line naming
the specs the amendment reflects. An amendment MUST be applied through
`/speckit-constitution` so the Sync Impact Report and dependent-template propagation happen
consistently.

**Versioning policy.** This constitution carries its own semantic version, independent of
the plugin release line:

- **MAJOR** — a principle is removed, or redefined in a backward-incompatible way.
- **MINOR** — a principle or section is added, or existing guidance materially expanded.
- **PATCH** — clarifications, wording, and typo fixes that change no obligation.

**Compliance review.** Every pull request verifies compliance with these principles. The
`Constitution Check` gate in `.specify/templates/plan-template.md` runs before Phase 0
research and again after Phase 1 design. A violation that must ship anyway is recorded in
the plan's **Complexity Tracking** table with its justification and the rejected simpler
alternative; an unjustified violation blocks the merge.

**Runtime guidance.** `CLAUDE.md` is the orientation document for contributors and Claude
Code sessions in this repository. It stays consistent with this constitution and with what
the repository actually ships.

**Version**: 1.0.0 | **Ratified**: 2026-07-28 | **Last Amended**: 2026-07-28
