# Example 2 — Pollinations (auth-free) and its disclaimer

Pollinations needs no account — ideal for a quick, throwaway image. But it carries two
risks the tool surfaces before the first generation:

1. **Public feed by default.** Pollinations posts generated images and their prompts to a
   public feed. The tool **hard-codes `private=true`** to opt out — this is not overridable.
2. **Undocumented output licence.** Only the platform code is MIT-licensed; the licence and
   ownership of generated images are not officially documented. Don't use it for
   confidential or commercial work — prefer `cloudflare` there.

## Generate (first time → disclaimer)

```bash
python3 skills/image-generate/scripts/image_generate.py \
    --provider pollinations \
    --prompt "a single tree, bold comic style, thick black outlines" \
    --out /tmp/tree.jpg
```

On the first run the tool prints the disclaimer and waits for acknowledgement. In an
interactive shell, type `yes`. Non-interactively (CI), acknowledge explicitly:

```bash
python3 skills/image-generate/scripts/image_generate.py \
    --provider pollinations --prompt "…" --out /tmp/tree.jpg --accept-data-policy
```

The acknowledgement (a SHA-256 digest of the exact notice text) is stored at
`$XDG_STATE_HOME/nolte-shared/image-generate/pollinations/ack`, so you are not re-prompted
until the notice text changes.

## Notes

- **Pollinations returns JPEG** — use a `.jpg` target to avoid the extension/MIME warning.
- Set `POLLINATIONS_API_TOKEN` to remove watermarks (optional).
- The tool sends a browser-style `User-Agent`; the default `urllib` UA is blocked by
  Pollinations' Cloudflare bot protection (HTTP 403, error 1010).
