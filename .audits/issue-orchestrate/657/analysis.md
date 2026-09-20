# Pre-analysis: nolte/claude-shared#657

status: approved
classification: bug
run: 20260920T190000Z-bpfr1

## Issue

`--prompt-file` and `--from-prompt-doc` read an operator-named path whole into memory
with no bound. Established by reading the file at the post-#658 tip: both go through
`Path(...).read_text(encoding="utf-8")`, around lines 704 and 709, with no prior check of
the path's type and no cap on its size.

## Classification

`bug`, not `security`. The input is a local path the operator names themselves, on their
own machine, so there is no trust boundary crossing and no credential involved. What is
defective is robustness: a directory raises an opaque error, a FIFO hangs, and a large
file is read whole before anything validates it. The parent class was opened by #643 and
this issue is its named, unrepaired remainder per `spec/project/defect-class-guards/` G7.

## Scope

In scope: the two reads, their bounds, their tests, and the spec rule that states them.
Out of scope: the acknowledgement-file read at roughly line 667, which reads a file this
tool writes itself and is therefore not a member of the class. The issue already states
this and a re-read confirms it.

## Decisions (taken before dispatch, grounded rather than guessed)

| # | Decision | Grounding |
|---|---|---|
| D1 | Cap 1 MiB, constant `MAX_PROMPT_FILE_BYTES` | `spec/design/flux-image-generation/en.md:46`: Cloudflare caps the prompt string at 2048 characters, schnell at 256 tokens. A document holding a prompt plus prose stays far below a megabyte. |
| D2 | Refuse with exit 2 before any network call, never truncate | Consistent with `--ref-image`. A silently shortened prompt would produce an image for a prompt the operator did not write. |
| D3 | Regular-file check on the open descriptor, `O_NONBLOCK` | Measured in #656: `open()` on a FIFO blocks, so a path-then-open check both races and hangs. |
| D4 | Cap at the read, before section extraction | The memory is spent at the read; a cap after parsing bounds nothing. |

## Refutable hypothesis

That one helper can serve both flags and `--ref-image`. If generalising `_open_ref_image`
would weaken its image-specific checks, only the descriptor-opening part is factored out.
A returned refutation is a first-class result per `spec/claude/dispatch-brief/`.

## Class sweep plan

Predicate: `grep -nE '\.read\(|read_bytes\(|read_text\(' <script>`, the same one #656 ran.
Run it rather than estimate it, and report every remaining hit as a member or a non-member
with a stated reason.
