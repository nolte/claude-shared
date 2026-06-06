# Example 02: Transitive MPL-2.0 dependency routed to review

## Input prompt

"Prüf die Lizenzen einmal gründlich, auch die transitiven."

## Input files (optional)

- `LICENSE` — MIT (outbound anchor)
- `docs/requirements.txt` + `uv.lock` — the top-level manifests declare only permissive packages, but the transitive graph pulls in `certifi` and `pathspec` (both MPL-2.0)
- `Taskfile.yml` — declares `license:sbom`

## Expected behaviour

1. Read the outbound `LICENSE` (`MIT`) and set it as the anchor.
2. Generate the SBOM via `task license:sbom`. Crucially, this resolves **transitive** licenses, not just the top-level manifest — a top-level-only scan would miss the MPL-2.0 packages.
3. Dispatch `license-check-scanner` with the SBOM path. The agent returns the inventory; the top-level packages are permissive, but two transitive components surface as weak (file-level) copyleft: `certifi` — MPL-2.0 and `pathspec` — MPL-2.0.
4. Determine the use context per §Scope: both `certifi` and `pathspec` are executed at arm's length (docs / dev / CI tooling), not conveyed, linked, or offered over a network as part of the product. Record the use-context as `arm's-length`.
5. Apply the policy gate: weak/file-level copyleft is `review`-tier, not `deny`. Because MPL-2.0 file-level copyleft does not propagate to this repository's own files and the components are arm's-length, route them to `review` (the gate is `blocked` until each `review` finding has a response), never to `allow` silently.
6. Remediate with confirmation: for each MPL-2.0 finding, propose an `exception with rationale` — a named, time-bounded (`valid-until`, ISO 8601) exception stating "weak file-level copyleft, transitive, arm's-length, not conveyed; no obligation on own files," with an approver. Do not edit any allowlist without a recorded rationale.
7. Persist the artifact with the two `review` findings, their `arm's-length` use-context, and the recorded exceptions; report the verdict `pass` once each `review` finding carries a response (otherwise `blocked`). Surface that the transitive SBOM is what caught these — the value of gating on the SBOM rather than the manifest.
