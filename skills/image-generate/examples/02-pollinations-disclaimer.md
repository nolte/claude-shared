# Example 2 — Pollinations (auth-free) and its disclaimer

Pollinations needs no account — ideal for a quick, throwaway image. It is operated by
Myceli.AI OU (Estonia; GDPR applies) and *does* have formal Terms and a Privacy Policy,
but two risks remain that the tool surfaces before the first generation:

1. **Public feed by default.** Pollinations posts generated images and their prompts to a
   public feed. The tool **hard-codes `private=true`** to opt out (not overridable). Note:
   per the privacy policy this only hides the image from the feed — it does **not**
   guarantee non-storage (response caches persist up to ~30 days).
2. **No explicit output licence.** The Terms grant no ownership/licence for the generated
   images; they state *"model licences vary; verify before commercial use"* and defer to
   the underlying model's licence (this tool uses FLUX). For confidential or commercial
   work, prefer `cloudflare` (output ownership + Apache-2.0).

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
