from __future__ import annotations

from pathlib import Path

from PIL import Image


def image_size(image: str | Path | Image.Image) -> tuple[int, int]:
    """Return ``(width, height)`` of ``image`` in pixels."""
    if isinstance(image, Image.Image):
        return image.size
    with Image.open(image) as im:
        return im.size
