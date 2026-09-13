# Example 04: One-directional compatibility, four fixtures

## Input prompt

"Check these four dependency situations against our licenses before the release."

## Input files (optional)

Four fixture repositories, each with its own root `LICENSE` and one conveyed dependency:

- **A** — `LICENSE` GPL-3.0-or-later; conveys an Apache-2.0 library.
- **B** — `LICENSE` Apache-2.0; conveys a GPL-3.0-only library.
- **C** — `LICENSE` GPL-2.0-only; conveys an Apache-2.0 library.
- **D** — `LICENSE` GPL-3.0-or-later; conveys a BSD-4-Clause library (original advertising clause).

## Expected behaviour

1. For each fixture, read the root `LICENSE` as the compatibility anchor and record the dependency's use context as `conveyed`. The verdicts below come from the one-directional rules in `spec/project/license-check/` §Compatibility against the project's own license, never from a blanket route to `review`.
2. **A — compatible, `allow`.** Apache-2.0 code may be combined into a GPLv3-or-later work, so the lax-permissive dependency is absorbable into the copyleft combination. Record the direction that makes it compatible.
3. **B — incompatible, never `allow`.** GPLv3 code may not be combined into an Apache-2.0-licensed work: the compatibility runs in one direction only. A conveyed strong-copyleft component in a permissively licensed product is `deny` under the default policy; remediate as in example 03.
4. **C — incompatible, `review` naming the clause.** Apache-2.0 is incompatible with GPLv2 because of its patent-termination and indemnification clauses, even though it is compatible with GPLv3. Route it to `review` with that incompatibility named, and offer `replace` or a relicensing check (a GPL-2.0-or-later anchor would change the answer).
5. **D — incompatible, `review` naming the exception.** Lax-permissive licenses are usually absorbable into a copyleft combination, but the original BSD-4-Clause advertising clause is the named exception. Route it to `review` citing that clause; a BSD-3-Clause release of the same library would be `allow`.
6. Persist one finding per fixture with the anchor, the dependency license, the rule applied, and the tier, so the artifact shows the compatibility encoding was exercised in both directions.
