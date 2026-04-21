from __future__ import annotations

from pathlib import Path

from PIL import Image

from ._paths import SPLITS_FOLDER, timestamped_dir


def split_image(
    image: str | Path | Image.Image,
    size: tuple[int, int],
    root: str | Path = ".",
    ext: str = "jpg",
) -> tuple[Path, list[Path]]:
    """Split an image into four quadrants using ``size`` as the split point.

    Quadrants are numbered in reading order:
        1 = upper-left   (0, 0)          -> (w, h)
        2 = upper-right  (w, 0)          -> (W, h)
        3 = lower-left   (0, h)          -> (w, H)
        4 = lower-right  (w, h)          -> (W, H)

    Where (w, h) is ``size`` and (W, H) is the full image size.

    The pieces are written to a fresh timestamped directory:
        ``<root>/image_quadrant_composer/splits/<YYYY-MM-DD_HH-MM-SS>/``

    Returns ``(output_dir, written_paths)`` where ``written_paths`` are in
    quadrant order.
    """
    img = _load(image)
    w, h = size
    W, H = img.size

    if not (0 < w < W) or not (0 < h < H):
        raise ValueError(
            f"split size {size} must lie strictly inside image size {(W, H)}"
        )

    boxes = [
        (0, 0, w, h),
        (w, 0, W, h),
        (0, h, w, H),
        (w, h, W, H),
    ]

    out_dir = timestamped_dir(root, SPLITS_FOLDER)

    save_rgb = ext.lower() in {"jpg", "jpeg"}
    written: list[Path] = []
    for i, box in enumerate(boxes, start=1):
        piece = img.crop(box)
        if save_rgb and piece.mode != "RGB":
            piece = piece.convert("RGB")
        path = out_dir / f"{i}.{ext}"
        piece.save(path)
        written.append(path)
    return out_dir, written


def _load(image: str | Path | Image.Image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    return Image.open(image)
