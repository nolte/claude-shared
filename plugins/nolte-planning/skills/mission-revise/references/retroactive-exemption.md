# Evaluating the retroactive exemption

Read this file when operation 2 step 2 finds no subsequent sprint that satisfies the "one full subsequent sprint" condition. It implements the retroactive-MVP exemption from `spec/project/mission/<canonical_language>.md` §Stabilisation gate. The spec is authoritative; if this procedure and the spec disagree, the spec wins.

The exemption waives **only** the one-full-subsequent-sprint condition. The other three gate conditions, the explicit operator flip, and the re-verification before the write (step 5) still apply. Evaluate every condition below at the time of the flip. If any condition fails, or can't be evaluated, block the flip and name it in the report. Never infer a pass.

## Preconditions

- **Full history.** If `git rev-parse --is-shallow-repository` prints `true`, refuse to evaluate the exemption and block the flip: a shallow clone can't evidence any condition.
- **Fixed paths.** `project/mission.md`, `project/roadmap.md`, and `project/sprints/` live at fixed paths per their specs. Read every historical version at that path (`git show <sha>:project/mission.md`). Don't use `--follow`.
- **Full history on path-limited logs.** Always pass `--full-history` to a path-limited `git log`, so commits on merged side branches aren't pruned.
- **Committed state only.** If `git status --porcelain -- project/mission.md project/roadmap.md project/sprints/` shows uncommitted changes, block the flip: uncommitted edits can't be evidenced. Ask the operator to commit them first.

## Parsing rules

Parse the files as YAML. Never use regex matches on `key: value` lines, because quoting and spacing vary.

- **Mission frontmatter.** Take the YAML between the opening `---` line and the next `---` line, then read `mvp_status`.
- **Roadmap items.** Each item is a level-3 heading followed by a fenced `yaml` block. Parse every block and key it by `id`. An item counts as an MVP item when `mvp` is boolean `true`.
- **Sprint frontmatter.** Same as the mission frontmatter; read `number` and `status`.

## Conditions

Let `<A>` be the first-add commit:

```sh
git log --full-history --diff-filter=A --format=%H -- project/mission.md | tail -1
```

Using the oldest add means deleting and re-creating the file doesn't reset it.

1. **C1: retroactive first write.** In `git show <A>:project/mission.md`, the frontmatter `mvp_status` is `achieved`. Its `## Source` also contains a statement that the MVP is recorded retroactively. Quote that sentence to the operator and have them confirm it's the retroactive-recording statement. A first version at `defining` fails C1, since `mission-define` writes every new mission at `defining`.
2. **C2: never stabilised.** For every commit from `git log --full-history --format=%H -- project/mission.md`, parse the frontmatter of `git show <sha>:project/mission.md`. None may have `mvp_status` equal to `stabilised`. A version that did means the exemption would serve a re-stabilisation after a regression, which the spec forbids.
3. **C3: MVP set unchanged.** Parse the roadmap items in `git show <A>:project/roadmap.md` and in `git show HEAD:project/roadmap.md`. Both versions must have the same set of `id`s with `mvp: true`, and every one of them is `status: done` at `<A>`. If an MVP item was added under the mission, it was delivered under the mission, so the exemption doesn't apply.
4. **C4: no regression.** Check `<A>` itself and every commit from `git log --full-history --format=%H <A>..HEAD -- project/roadmap.md`. In each version, parse every item block: no `mvp: true` item may have `status: active`. Report the failing item by ID and commit.
5. **C5: later sprints untouched.** Every `project/sprints/*.md` whose frontmatter `number` is greater than the MVP-closing sprint's `number` must have `status: planned`. It also passes when no such sprint exists. A later sprint that's `active`, `review`, `closed`, or `cancelled` means the exemption doesn't apply, and the normal condition decides.

## Evidence

On a pass, show the operator one line per condition: the commit and the value read, or the item and sprint IDs checked. Also show the MVP-closing sprint's `number` and `ended`.

Step 5 then collects the operator's one-paragraph rationale naming the exemption. Never generate it yourself. The rationale must carry exactly this evidence:

- the MVP-closing sprint's number and `ended` date;
- the first-add commit `<A>`;
- the operator decision date.
