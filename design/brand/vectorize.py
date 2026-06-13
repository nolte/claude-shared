#!/usr/bin/env python3
"""Border flood-fill background removal + vtracer vectorisation for the mascot.

On-demand brand-asset pipeline — NOT part of CI or the build. It turns a flat-
background mascot/logo render (PNG) into a clean transparent SVG. The committed
SVGs under design/brand/mascot/ and design/brand/logo/ were produced with it.

Why border flood-fill rather than global colour-keying: in light mode the cream
face mask and the warm-bone background share the same colour (#F4F1EA). A global
colour key would punch a hole in the face. The figure carries a bold, closed dark
outline, so a flood that starts at the image border and stops at that outline
removes the exterior background while leaving the walled-off interior mask intact.
A lower threshold is needed in dark mode (charcoal background vs. dark figure
parts); see the per-asset thresholds recorded in the prompt documents.

Deps (install on demand; not declared in requirements):
    pip install Pillow numpy vtracer
Usage:
    python3 design/brand/vectorize.py <render.png> <clean.png> <out.svg> [thresh]
Reproduce the committed set: render each prompt document's "Rendered v1.1 asset"
block with image_generate.py at the recorded seed, then run this with the
recorded threshold.
"""
import sys
from collections import deque
import numpy as np
from PIL import Image, ImageDraw
import vtracer

SENTINEL = (255, 0, 255)  # magenta — never present in the brand palette


def strip_ground_shadow(out, band=0.70, min_bright=150, max_spread=24):
    """Drop FLUX's residual contact shadow: light, low-saturation (grey) opaque
    pixels in the lower band of the canvas. The cream paws survive because they
    are warm (R>G>B, high channel spread); the signature streak survives because
    it sits in the upper band, outside this region."""
    arr = np.array(out)
    h, w = arr.shape[:2]
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    spread = arr[:, :, :3].max(2).astype(int) - arr[:, :, :3].min(2).astype(int)
    rows = np.arange(h)[:, None] >= int(h * band)
    grey_shadow = (a == 255) & rows & (np.minimum(np.minimum(r, g), b) > min_bright) & (spread <= max_spread)
    n = int(grey_shadow.sum())
    arr[grey_shadow] = (0, 0, 0, 0)
    print(f"  ground-shadow strip: {n} grey px removed in lower band")
    return Image.fromarray(arr, "RGBA")


def keep_largest_component(out):
    """Keep only the figure: the single LARGEST connected blob of opaque pixels.
    Detached islands (a quantised ground shadow, a stray speckle, a floating
    leaf) are set transparent. The figure (with its gripped branch/leaves) is
    one contiguous silhouette, so this never eats the mask, eyes, streak or paws.
    The largest component is found globally — not by seeding the image centre,
    which fails when the figure is off-centre (e.g. a logo hanging from the top)."""
    arr = np.array(out)
    opaque = arr[:, :, 3] == 255
    h, w = opaque.shape
    label = np.zeros((h, w), np.int32)
    sizes = {}
    cur = 0
    ys, xs = np.nonzero(opaque)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if label[sy, sx]:
            continue
        cur += 1
        cnt = 0
        dq = deque([(sy, sx)])
        label[sy, sx] = cur
        while dq:
            y, x = dq.popleft()
            cnt += 1
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and opaque[ny, nx] and not label[ny, nx]:
                    label[ny, nx] = cur
                    dq.append((ny, nx))
        sizes[cur] = cnt
    if not sizes:
        return out
    keep = max(sizes, key=sizes.get)
    drop_mask = opaque & (label != keep)
    dropped = int(drop_mask.sum())
    arr[drop_mask] = (0, 0, 0, 0)
    print(f"  kept largest of {cur} components ({sizes[keep]} px); dropped {dropped} stray px")
    return Image.fromarray(arr, "RGBA")


def remove_background(in_path, clean_path, thresh):
    img = Image.open(in_path).convert("RGB")
    w, h = img.size
    flood = img.copy()
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for s in seeds:
        ImageDraw.floodfill(flood, s, SENTINEL, thresh=thresh)
    src = img.load()
    fl = flood.load()
    out = Image.new("RGBA", (w, h))
    od = out.load()
    removed = 0
    for y in range(h):
        for x in range(w):
            if fl[x, y] == SENTINEL:
                od[x, y] = (0, 0, 0, 0)
                removed += 1
            else:
                r, g, b = src[x, y]
                od[x, y] = (r, g, b, 255)
    out = strip_ground_shadow(out)
    out = keep_largest_component(out)
    out.save(clean_path)
    pct = 100.0 * removed / (w * h)
    print(f"  bg removed: {removed}/{w*h} px ({pct:.1f}%) -> {clean_path}")
    return pct


def vectorise(clean_path, svg_path):
    vtracer.convert_image_to_svg_py(
        clean_path, svg_path,
        colormode="color", hierarchical="stacked",
        filter_speckle=4, color_precision=6, corner_threshold=60,
        length_threshold=4.0, max_iterations=10, splice_threshold=45,
        path_precision=3,
    )
    import os
    print(f"  svg: {svg_path} ({os.path.getsize(svg_path)} bytes)")


if __name__ == "__main__":
    in_path, clean_path, svg_path = sys.argv[1], sys.argv[2], sys.argv[3]
    thresh = int(sys.argv[4]) if len(sys.argv) > 4 else 50
    print(f"{in_path} (thresh={thresh}):")
    remove_background(in_path, clean_path, thresh)
    vectorise(clean_path, svg_path)
