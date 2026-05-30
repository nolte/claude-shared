# Example 03 — error contract (missing key, then Free-Tier quota exhausted)

Two terminal error paths the skill must surface verbatim and never paper over.

## Input prompt

> Generate `assets/banner.png` from "a wide abstract teal gradient banner".

## Input files

None.

## Expected behaviour

**Case A — `GEMINI_API_KEY` unset.** Before any network call, the script emits a
setup hint that names `GEMINI_API_KEY`, links `https://aistudio.google.com/apikey`,
and explains Free-Tier needs no billing. The skill relays it and stops with a
non-zero exit; it never prompts the operator to paste a key into the conversation.

**Case B — HTTP 429 (quota exhausted).** With a valid key but exhausted quota,
the script exits `3` with a single message that includes a quantitative ceiling
("roughly 10 requests per minute / 100 per day"). The skill relays the message
and stops. It **does not** retry — each retry would burn more Free-Tier quota.
No image and no sidecar are written. An HTTP 401/403 would instead exit `4` with
a message pointing at the key-management page.
