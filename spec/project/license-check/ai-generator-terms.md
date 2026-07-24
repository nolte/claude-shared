# AI generator output terms — evidence appendix

> Non-normative evidence appendix to `spec/project/license-check/` §AI
> provenance. The normative rule ("MUST NOT assume a commercial generator's
> terms grant a clean, copyrightable artifact") lives in `en.md`/`de.md`; this
> file carries the volatile per-generator evidence, deliberately kept out of
> the normative text because vendor terms change. Each entry records what was
> verified and when. Re-verify an entry before relying on it in an audit
> decision; update this table (with a new verification date) when a vendor's
> terms move.

Last verification pass: **2026-06-04** (targeted primary-source research,
rounds 3–5 of the license-check research record; see `en.md` §Sources).

## Verified per-generator terms

### GitHub Copilot (verified 2026-06-01)

- IP indemnity ("Copilot Copyright Commitment") applies to **Business and
  Enterprise tiers only**, not Individual/Free; it runs through the "Defense of
  Third Party Claims" mechanism.
- Since 2026-04-03 the duplicate-detection filter is **no longer** a
  precondition of the Copyright Commitment (earlier guidance is superseded).
- Source: `learn.microsoft.com` — customer copyright commitment.

### OpenAI (verified 2026-06-01)

- Assigns output ownership to the customer: "you … own the Output. We hereby
  assign … all our right, title, and interest, if any."
- "Similarity of Content" clause: ownership is not exclusive — similar outputs
  to other customers remain possible.
- Source: `openai.com/policies/row-terms-of-use`.

### Adobe Firefly (verified 2026-06-01)

- Customer owns/controls the output; Adobe claims no IP rights — but does
  **not** warrant copyrightability (jurisdiction-dependent).
- IP indemnity is gated to paid tiers.
- Output carries an automatic C2PA content credential.
- Source: Adobe Firefly legal FAQ (round 3 of the research record).

### Midjourney (verified 2026-06-04)

- Paying users "own all Assets You create … to the fullest extent possible
  under current law"; free-trial output is licensed **CC BY-NC 4.0 only**
  (Midjourney retains ownership).
- Companies with more than 1 million USD revenue need the Pro/Mega tier for
  commercial use.
- Every user grants Midjourney a "perpetual, worldwide, non-exclusive,
  sublicensable, no-charge, royalty-free, irrevocable copyright license" on
  prompts and assets (training, public display, derivatives, sublicensing).
- No indemnification evidenced.
- Source: `docs.midjourney.com` terms (direct fetch returned HTTP 403 at
  verification time; verbatim wording via `terms.law/ai-output-rights/midjourney`).
