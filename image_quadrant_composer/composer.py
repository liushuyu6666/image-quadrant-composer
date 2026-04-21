from __future__ import annotations

from pathlib import Path

from PIL import Image

from ._paths import COMPOSES_FOLDER, timestamped_dir


def compose_image(
    source: str | Path,
    new_image: str | Path | Image.Image,
    position: int,
    root: str | Path = ".",
    ext: str = "jpg",
) -> tuple[Path, Image.Image]:
    """Replace one quadrant with ``new_image`` and compose the four pieces.

    Reads ``1.<ext>..4.<ext>`` from ``source``. The piece at ``position``
    (1..4, reading order) is replaced by ``new_image``. The target size for
    the new piece is derived from the two quadrants that share edges with
    it, so the caller does not need to resize beforehand — this function
    resizes ``new_image`` to fit.

    The reassembled full image is written as ``composed.<ext>`` into a
    fresh timestamped directory:
        ``<root>/image_quadrant_composer/composes/<YYYY-MM-DD_HH-MM-SS>/``

    Returns ``(output_dir, composed_image)``.
    """
    if position not in (1, 2, 3, 4):
        raise ValueError(f"position must be one of 1..4, got {position}")

    src = Path(source)
    originals = [Image.open(src / f"{i}.{ext}") for i in range(1, 5)]
    _validate_grid(originals)

    target_size = _target_size(originals, position)
    new_piece = _load(new_image)
    if new_piece.size != target_size:
        new_piece = new_piece.resize(target_size, Image.Resampling.LANCZOS)

    pieces = list(originals)
    pieces[position - 1] = new_piece

    save_rgb = ext.lower() in {"jpg", "jpeg"}
    mode = "RGB" if save_rgb else pieces[0].mode

    W = pieces[0].width + pieces[1].width
    H = pieces[0].height + pieces[2].height
    canvas = Image.new(mode, (W, H))
    canvas.paste(_match_mode(pieces[0], mode), (0, 0))
    canvas.paste(_match_mode(pieces[1], mode), (pieces[0].width, 0))
    canvas.paste(_match_mode(pieces[2], mode), (0, pieces[0].height))
    canvas.paste(_match_mode(pieces[3], mode), (pieces[0].width, pieces[0].height))

    out_dir = timestamped_dir(root, COMPOSES_FOLDER)
    canvas.save(out_dir / f"composed.{ext}")

    return out_dir, canvas


def _validate_grid(pieces: list[Image.Image]) -> None:
    ul, ur, ll, lr = pieces
    if ul.height != ur.height or ll.height != lr.height:
        raise ValueError("top/bottom quadrant pairs must share a height")
    if ul.width != ll.width or ur.width != lr.width:
        raise ValueError("left/right quadrant pairs must share a width")


def _target_size(pieces: list[Image.Image], position: int) -> tuple[int, int]:
    ul, ur, ll, lr = pieces
    # Width matches the piece in the same column; height matches the same row.
    if position == 1:
        return (ll.width, ur.height)
    if position == 2:
        return (lr.width, ul.height)
    if position == 3:
        return (ul.width, lr.height)
    return (ur.width, ll.height)  # position == 4


def _load(image: str | Path | Image.Image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    return Image.open(image)


def _match_mode(img: Image.Image, mode: str) -> Image.Image:
    return img if img.mode == mode else img.convert(mode)
