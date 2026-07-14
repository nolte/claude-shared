# Example 03 — watermark-free requirement → reroute off Gemini

The route-selection guardrail. The operator wants a Gemini image but
also states the asset must be watermark-free. Because every Gemini UI
output carries an unavoidable SynthID watermark, the skill flags the
contradiction and steers to the watermark-free provider — the route is
wrong, not the prompt.

## Input prompt

> Generate a product image via the Gemini UI — it has to be
> watermark-free for the store listing.

## Expected behaviour

1. **Contradiction surfaced early.** The skill states the **SynthID
   watermark** caveat up front: every Gemini UI output carries an
   invisible SynthID watermark, and there is **no UI toggle** to
   disable it. A watermark-free commercial or store asset cannot come
   from this route.
2. **Reroute recommended.** The skill steers the operator to
   `image-generate --provider cloudflare` (FLUX.1-schnell, Apache-2.0,
   no watermark, no public feed) as the correct path for a
   watermark-free asset — the route is wrong, not the prompt.
3. **Does not proceed with the handoff by default.** It does not paste
   the operator into a Gemini UI flow that would only produce a
   watermarked, unusable result; if the operator insists on Gemini
   anyway (e.g. the watermark turns out acceptable), the skill
   proceeds with the normal author-then-handoff flow from Example 01.
4. **No side effects regardless.** Whichever branch is taken, this
   skill makes no API call, requests no `GEMINI_API_KEY`, and writes no
   image or sidecar — it only advises on the route and, if continued,
   hands over the copy-paste prompt block.
