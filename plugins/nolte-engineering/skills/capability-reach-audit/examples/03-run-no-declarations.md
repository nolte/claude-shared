# Example 03: Run on a repository that declares nothing

## Input prompt

"Prüf mal die Capability-Reach von ~/repos/github/dotfiles."

## Input files (optional)

- `~/repos/github/dotfiles/.git` — a local working copy: shell configuration, no `project/`, no workflows with an `on:` block, a README with an install section but no capability claims, no inventory file.

## Expected behaviour

1. Answer in German, since the operator wrote German; keep probe files, manifest, and checkpoint state in English.
2. Confirm the working copy, then invoke the runner; it exits `3` and writes a report headed `Not probed: all. No probe set.` Say that this is not a clean result and route to `derive`.
3. Dispatch `capability-reach-scanner`; its payload reports all four sources with `presence: absent` and `entries: []`.
4. Report that as the result (R15): the repository declares nothing in any of the four sources, so the audit has nothing to measure and can't speak about this repository's reach. Don't render it as clean, don't infer capabilities from the source tree, and don't draft probes yourself.
5. Write only `project/reach-probes/_not-constructible.yml` with `entries: []`, so a later run can tell "the derivation recorded nothing unconstructible" from "the derivation never ran"; checkpoint `phase: persisted` and mark the run `completed`.
6. Tell the operator that the next step, if any, is a declaration in the target repository (a requirement document, a README capability section, an inventory), after which `derive` has something to read.
