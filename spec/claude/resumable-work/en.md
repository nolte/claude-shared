# Resumable Skill and Agent Work

Status: draft

## Context
Long-running, multi-step Claude Code skills and agents (for example `portfolio-audit`, `spec-drift-audit`, `skills-agents-sweep`, `feature-decompose`, `sprint-plan`, `release-notes-curate`) interleave automated work with user-approval gates and produce intermediate artefacts (scan results, drafts, partial findings) along the way. When the host PC crashes, the terminal window closes, the Claude Code session expires, or the operator simply walks away, every byte of that in-flight state evaporates. On the next invocation the operator has to restart from scratch and re-answer every approval prompt, which is both annoying and a quiet source of inconsistency: nobody re-types the same decisions identically twice in a row.

This spec defines a **resume working copy** convention: a small, gitignored, human-readable on-disk persistence layer that long-running skills and agents write to as they progress, and consult on re-invocation. The convention fixes only the envelope (location, identity, mandatory fields, lifecycle); each skill or agent remains free to model its own checkpoint payload inside the envelope.

The convention is deliberately local-first: state lives next to the working copy, gitignored, and never leaves the machine. It's not a distributed state store, not a CI feature, and not a substitute for committing finished work.

Readers: skill and agent authors in `claude-shared`, plus operators who run long workflows and need to recover from interruptions.

## Goals
- Every in-scope skill and agent can be resumed after a crash, terminal close, or session expiry without re-walking user-approval gates that already produced a decision
- A run is uniquely and stably identifiable across sessions on the same machine, so autodetection on re-invocation is deterministic
- The state file format is human-readable (YAML), forward-compatible (carries a `schema_version`), and inspectable with `cat` / `ls` without bespoke tooling
- Skills and agents fail closed: a corrupt, unparseable, or schema-mismatched state file prompts the operator rather than being silently dropped or silently applied
- Operators can tell at the catalog level which skills and agents support resume, so they know when to expect the resume prompt and which workflows are safe to interrupt
- The convention coexists cleanly with `spec/project/parallel-working-copies/`: resume state is per-worktree, never shared via symlink across worktrees

## Non-Goals
- Cross-machine or remote state synchronisation (Dropbox, S3, git, cloud sync)—state is strictly local to the working copy on this machine
- Recovery of harness-tracked background jobs, MCP server processes, long-running shell sessions, or external CI runs—those have their own lifecycles and aren't modelled here
- Trivial one-shot skills and agents whose entire execution is cheap to re-run from scratch (for example `quality-gate`'s lint/test invocation, the `dependency-audit-scanner` agent's scan step)—resume support is unnecessary overhead for them
- The internal content schema of each skill's checkpoint payload—each skill or agent owns the shape of its own `state:` section; this spec fixes only the envelope around it
- Committing or versioning the resume directory in source control—it's `.gitignore`d by default and only relevant to the local working copy
- Replacing the existing `.audits/` output mechanism—finished audit artefacts continue to live under `.audits/`; the resume directory holds in-flight scratch state only

## Requirements

### Scope of applicability
- **MUST** apply to every skill or agent whose normal control flow includes more than one user-approval gate, or more than one internal phase that produces an intermediate artefact the operator would otherwise lose on interruption
- **MUST** be declared in the skill's `SKILL.md` frontmatter (or the agent's frontmatter) via a `resumable: true` field, so the catalog generator and `skill-vs-agent` peer lookups can surface resume support to operators
- **MUST** be referenced from the skill or agent description text (one short clause: "supports resume on re-invocation") whenever `resumable: true` is set, so operators reading the catalog without inspecting frontmatter still know
<!-- vale Microsoft.Contractions = NO -->
- **SHOULD NOT** apply to one-shot skills whose entire execution is a single Bash invocation or a single tool call that's itself cheap to restart; declaring `resumable: false` (or omitting the field) is the correct choice for those
<!-- vale Microsoft.Contractions = YES -->
- **MAY** apply to agents whose contract is otherwise fire-and-forget when they internally span multiple phases that benefit from checkpoint writes; this is a deliberate exception to the usual skills-are-multi-turn / agents-are-single-turn split in `spec/claude/skill-vs-agent/`

### Persistence location
- **MUST** write resume state to `.resume/<skill-or-agent-name>/<run-id>.yml` at the repository root of the working copy
- **MUST** use the kebab-case `name` from the skill or agent frontmatter as `<skill-or-agent-name>` so the directory is predictable from the artefact identifier
- **MUST** ensure the repository's `.gitignore` includes `/.resume/` (anchored at the repo root); when a downstream project consumes this spec, the `project-structure` scaffold step is the place to add the entry
- **MUST** create the `.resume/<skill-or-agent-name>/` directory on the first checkpoint write if it doesn't exist, and **MUST NOT** fail if the directory already exists from a prior run
- **MUST NOT** write resume state outside `.resume/` for this purpose—no `/tmp/...`, no `~/.claude/...`, no `.audits/...`, no committed location inside the repository
- **MUST NOT** symlink `.resume/` from one worktree to another; per `spec/project/parallel-working-copies/` each worktree maintains its own independent `.resume/`

### Run identity
- **MUST** assign each new run a unique `run_id` whose suggested form is an ISO 8601 UTC timestamp followed by a short random suffix, joined with a hyphen—for example `20260522T143012Z-a3f9`; the timestamp prefix sorts runs chronologically in a directory listing, the suffix prevents collisions when two runs start in the same second
- **MUST** embed the `run_id` verbatim in the state file's `run_id:` field, matching the filename stem (without the `.yml` extension)
- **MUST** capture a deterministic `inputs:` snapshot—the initial invocation arguments and any target identifiers (for example target spec topic, target sprint number, target audit bundle)—so that autodetect can match a re-invocation to the right in-progress run by comparing inputs
- **MAY** additionally embed a short human-readable `label:` (free-form, ≤80 chars) so the resume prompt can show "spec-drift-audit · bundle-7 (4 specs)" rather than only a run id

### State file envelope
The following keys form the mandatory envelope every state file MUST carry. Skills and agents add their own keys under `state:`.

- **MUST** include `schema_version` (integer, currently `1`) as the first key in the file
- **MUST** include exactly one of `skill:` or `agent:` whose value is the kebab-case `name` matching the artefact frontmatter
- **MUST** include `run_id` matching the filename stem
- **MUST** include `started_at` (ISO 8601 UTC, set once at run creation) and `last_checkpoint_at` (ISO 8601 UTC, updated on every checkpoint write)
- **MUST** include `inputs:` as a mapping or list snapshot of the initial invocation arguments used for autodetect matching
- **MUST** include `phase:` (free-form short string identifying the last completed checkpoint inside the skill or agent, for example `scanned`, `findings-drafted`, `awaiting-approval-3`)
- **MUST** include `decisions:` as an ordered list of user answers already collected; each entry **MUST** carry `gate` (identifier of the approval gate within the skill), `question` (the question text the operator was asked), `answer` (the operator's chosen value), and `at` (ISO 8601 UTC timestamp of the answer)
- **MUST** include `status:` whose value is exactly one of `in_progress`, `completed`, or `discarded`
- **MAY** include `label:` (see Run identity above) and any number of additional keys under `state:` modelled by the owning skill or agent
- **MUST NOT** store credentials, raw API keys, OAuth tokens, or any other secret material in the state file; the file is plain text on disk and is therefore an unsuitable secret store

### Checkpoint cadence
- **MUST** write a checkpoint immediately after every successful user-approval gate, before performing work that depends on the new decision; this is the load-bearing rule—it's the operator's lived guarantee that no answered question is ever asked twice on resume
- **MUST** write a checkpoint after each named phase boundary inside the skill or agent (for example after a scan completes, after a draft is authored, after a diff is computed), so that long compute steps don't have to repeat on resume
- **MUST** set `last_checkpoint_at` to the current ISO 8601 UTC timestamp on every checkpoint write
- **MUST** append to `decisions:` only—never rewrite or reorder earlier entries—so the checkpoint history is a strictly growing log
<!-- vale Microsoft.Contractions = NO -->
- **SHOULD NOT** write a checkpoint inside a hot inner loop (per-file iteration, per-record scanning); checkpoint at the loop boundary instead, so the file isn't rewritten hundreds of times per second
<!-- vale Microsoft.Contractions = YES -->
- **SHOULD** write the file atomically (write-then-rename) so a crash mid-write doesn't corrupt an existing checkpoint

### Resume detection on re-invocation
- **MUST** scan `.resume/<skill-or-agent-name>/*.yml` on every invocation, before prompting the operator for inputs, and select files whose `status:` is `in_progress`
- **MUST** match resumable candidates by comparing the saved `inputs:` snapshot against the current invocation's inputs; the matching algorithm is owned by each skill or agent but **MUST** be deterministic given the same inputs
- **MUST**, when exactly one in-progress run matches, prompt the operator with: `Resume run <run_id> from phase <phase> (last checkpoint <last_checkpoint_at>)?` and offer exactly three choices: `resume` (re-hydrate state and continue), `start-new` (begin a fresh run; leave the existing file as `in_progress`), `discard` (delete the existing file, then begin a fresh run)
- **MUST**, when multiple in-progress runs match, list them with `run_id`, `label` (if present), `phase`, and `last_checkpoint_at`, and ask the operator which to resume—or to start a new run
- **MUST**, when no in-progress run matches, start a fresh run and write a new state file at the first checkpoint
- **MUST** honour the operator's choice exactly: `resume` re-hydrates from the file and **MUST NOT** re-ask any question whose answer is already in `decisions:`; `start-new` writes a fresh file with a new `run_id` and leaves the old file untouched; `discard` deletes the old file before continuing
- **MUST NOT** treat the file's mere presence as authorisation to resume—the operator's interactive confirmation is required every time, except when the operator passes an explicit non-interactive override (see §Non-interactive override below)

### Completion and cleanup
- **MUST** set `status:` to `completed` on natural completion (the skill or agent reached its terminal step successfully)
- **SHOULD** retain a `completed` state file for one further matching invocation cycle as a "recent run" record, so the operator can inspect what happened on the previous run; a separate housekeeping step or operator action removes it afterwards
- **MUST** set `status:` to `discarded` (or delete the file outright) on operator-driven cancellation; either choice is acceptable, but a partial in-progress file **MUST NOT** be left behind silently
- **MUST NOT** retain stale `in_progress` files older than 30 days without surfacing them to the operator on the next matching invocation; the resume prompt **MUST** then offer `discard` as a clearly named option alongside `resume`
- **MAY** ship a portfolio-wide housekeeping skill (or `task` target) that prunes `completed` and stale `in_progress` files in bulk—this spec doesn't mandate one, only permits it

### Forward compatibility
- **MUST** refuse to resume a state file whose `schema_version` is greater than the version the running skill or agent knows; the refusal **MUST** print a clear message naming both versions and **MUST** offer `start-new` or `discard` as the only legal follow-ups
- **SHOULD** migrate older `schema_version`s in place when the migration is trivial (additive fields only, no rename), writing the upgraded file before resuming
- **MUST** refuse to resume with the same `start-new` / `discard` fallback when an older `schema_version` can't be trivially migrated
- **MUST** refuse to resume when the file is unparseable (broken YAML, truncated mid-write) and offer the same fallback; **MUST NOT** silently start fresh in this case, because the operator may want to inspect or repair the file before discarding it

### Non-interactive override
- **MAY** support a non-interactive override flag (for example `--resume <run-id>`, `--new`, or `--discard <run-id>`) so automation or batch scripts can pre-select the resume choice; when the skill or agent supports such a flag it **MUST** document it in its description
- **MUST**, in the absence of such a flag, default to the interactive prompt described in §Resume detection on re-invocation
- **MUST NOT** silently resume without operator confirmation when no flag is supplied—interactive confirmation remains the safety boundary

### Interaction with other portfolio specs
- **MUST** coexist with `spec/project/parallel-working-copies/`: `.resume/` lives at the root of each worktree independently; no symlinks, no shared state across worktrees
- **MUST** extend the `.gitignore` shaped by `spec/project/project-structure/` with `/.resume/` rather than override or conflict with it
- **MUST** be cross-referenced (not duplicated) from `spec/claude/skill-management/` and `spec/claude/agent-management/`: those specs gain a short rule that in-scope artefacts declare `resumable: true` and follow this spec; the load-bearing detail stays here
- **MUST NOT** reuse `.audits/` (owned by `spec/claude/review-plan/` and skill-specific audit outputs) for in-flight resume state; `.audits/` is final-output territory, `.resume/` is in-flight scratch
- **MUST** continue to write any finished audit, report, or artefact to the location its own spec dictates; resuming a run that produces an `.audits/...` file means the file is written when the run reaches its terminal step, not as a checkpoint side effect

## Acceptance Criteria
- [ ] Every skill and agent under `skills/` and `agents/` whose normal control flow has more than one user-approval gate OR more than one named internal phase carries `resumable: true` in its frontmatter
- [ ] Every skill and agent with `resumable: true` mentions resume support in its `description:` text
- [ ] No skill or agent with `resumable: true` writes resume state outside `.resume/<skill-or-agent-name>/`
- [ ] The repository's `.gitignore` contains an entry that ignores `/.resume/`
- [ ] No file under `.resume/<name>/` has a `schema_version` greater than the version the corresponding skill or agent knows; if mismatches exist they're accompanied by an operator decision (a deleted file, or a `discarded` status)
- [ ] No state file under `.resume/` is missing any of the mandatory envelope keys (`schema_version`, exactly one of `skill`/`agent`, `run_id`, `started_at`, `last_checkpoint_at`, `inputs`, `phase`, `decisions`, `status`)
- [ ] No state file's `run_id` differs from its filename stem
- [ ] No state file contains plain text secrets (API keys, OAuth tokens, passwords) under any key, including `state:`
- [ ] No `.resume/` symlink exists that points outside the current worktree's `.resume/` directory
- [ ] Every state file with `status: in_progress` whose `last_checkpoint_at` is older than 30 days is accompanied by evidence (operator note, follow-up issue, or `discard` decision recorded on a later run) showing the operator was prompted about it
- [ ] On a deliberately interrupted run of a `resumable: true` skill, re-invoking the skill with the same inputs surfaces the resume prompt naming the existing `run_id`, `phase`, and `last_checkpoint_at`
- [ ] On a resume choice, no question whose answer already appears in `decisions:` is re-asked to the operator
- [ ] Both `spec/claude/skill-management/` and `spec/claude/agent-management/` cross-reference this spec from their requirements (no duplication of the envelope or lifecycle rules)

Notes on coverage: The `MUST` rules in §Checkpoint cadence around *when* a checkpoint is written (after each gate, after each named phase, atomic write-then-rename) are skill-internal control-flow conventions with no stable post-hoc observable on the state file itself; they're enforced by author practice and by skill review (`spec/claude/skill-review/`, `spec/claude/agent-review/`) rather than by a mechanical AC. The `MUST` rules in §Forward compatibility around *what to do* on a `schema_version` mismatch or unparseable file are runtime behaviours that surface only when a mismatch occurs; ACs cover the post-hoc shape (no orphan high-version files) but not the per-incident behaviour. The `MUST NOT` against treating file presence alone as resume authorisation (in §Resume detection on re-invocation) is likewise a runtime-behaviour convention; it's observable only by direct operator testing of the skill, not by inspecting the resume directory.

## Open Questions
- Should `.resume/` be a per-language-ecosystem concern (kept distinct for Python tooling vs. Node tooling, similar to lockfiles), or strictly a single top-level convention? The current spec assumes the latter, but a polyglot monorepo might benefit from the former
- Is there a portfolio-wide housekeeping skill that periodically prunes `completed` and stale `in_progress` files (analogous to `git worktree prune`), or is each skill responsible for its own cleanup? §Completion and cleanup permits both but mandates neither
- Should this spec mandate a CLI helper (for example `task resume:list` and `task resume:prune`) for operators to inspect the directory, or is direct `ls .resume/` and `cat .resume/<name>/<run-id>.yml` access sufficient? The latter is the current assumption
- How does this interact with skills that already write to `.audits/` for their findings (`spec-drift-audit`, `portfolio-audit`, `skill-review`, `agent-review`)? Is `.audits/` always the final output and `.resume/` always the in-flight scratchpad, or can a single skill's artefact play both roles by moving from `.resume/` to `.audits/` on completion?
- Should the resume prompt's `start-new` option offer a "diff against existing" preview before discarding, so the operator can compare what they would lose? Currently the spec keeps the prompt minimal (three choices, no preview)
- Should `inputs:` matching be exact, or should each skill be allowed to declare a "normalised match" (case-insensitive, whitespace-tolerant) for human-typed identifiers? The spec currently leaves the matching algorithm to each skill while requiring determinism
