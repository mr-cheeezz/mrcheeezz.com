from __future__ import annotations

import io
from pathlib import Path

import requests
from PIL import Image


def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])


def _dominant_color(image):
    # Downsample first; this is only for glow color, not exact image analysis.
    small = image.convert("RGB").resize((48, 48))
    colors = small.getcolors(48 * 48) or []
    if not colors:
        return None

    best_score = -1
    best_rgb = None
    for count, (r, g, b) in colors:
        brightness = (r + g + b) / 3
        saturation = max(r, g, b) - min(r, g, b)
        if brightness < 28 or brightness > 242:
            continue
        score = (count * 1.5) + (saturation * 2.0)
        if score > best_score:
            best_score = score
            best_rgb = (r, g, b)

    if best_rgb is None:
        best_rgb = max(colors, key=lambda c: c[0])[1]
    return _rgb_to_hex(best_rgb)


def color_from_local_image(path):
    image_path = Path(path)
    if not image_path.exists():
        return None
    with Image.open(image_path) as img:
        return _dominant_color(img)


def color_from_remote_image(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        with Image.open(io.BytesIO(response.content)) as img:
            return _dominant_color(img)
    except Exception:
        return None
