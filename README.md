# image-quadrant-composer

Split an image into four quadrants, swap one out for a new image, and compose the four pieces back together. Usable as a CLI or as a Python library.

## Installation

```bash
pip install -e .
```

Requires Python 3.9+ and Pillow.

## Output layout

Both operations write to a fresh timestamped directory under a `root` directory (defaults to the current working directory):

```
<root>/
  image_quadrant_composer/
    splits/
      2026-04-20_20-07-51/
        1.jpg   # upper-left
        2.jpg   # upper-right
        3.jpg   # lower-left
        4.jpg   # lower-right
    composes/
      2026-04-20_20-08-02/
        1.jpg        # three originals + the resized new piece
        2.jpg
        3.jpg
        4.jpg
        composed.jpg # the reassembled full image
```

The datetime folder is `YYYY-MM-DD_HH-MM-SS` (local time).

## How the split works

You provide a `(width, height)` that defines the **upper-left quadrant**. That point is also the split point for the whole image: everything to the right and/or below is divided into the remaining three quadrants, in reading order:

| File    | Quadrant    | Box (inclusive-exclusive) |
| ------- | ----------- | ------------------------- |
| `1.jpg` | upper-left  | `(0, 0)` → `(w, h)`       |
| `2.jpg` | upper-right | `(w, 0)` → `(W, h)`       |
| `3.jpg` | lower-left  | `(0, h)` → `(w, H)`       |
| `4.jpg` | lower-right | `(w, h)` → `(W, H)`       |

where `(w, h)` is the size you pass and `(W, H)` is the full image size. The non-upper-left quadrants take whatever space is left — they are not necessarily the same size as the upper-left piece.

## How the compose works

You point at a directory containing four pieces (typically a previous `splits/<datetime>/`), give it a replacement image, and say which quadrant to replace (1..4). The target size for the replacement is derived from the two quadrants that share edges with it — so you don't have to resize beforehand; the composer resizes the new image for you using Lanczos resampling, then pastes all four pieces into a single image.

## CLI

### split

```bash
image-quadrant-composer split <image> <width> <height> [--root .] [--ext jpg]
```

```bash
image-quadrant-composer split input.jpg 150 100
# writes ./image_quadrant_composer/splits/<datetime>/{1,2,3,4}.jpg
```

### compose

```bash
image-quadrant-composer compose <source_dir> <new_image> <position> [--root .] [--ext jpg]
```

- `<source_dir>` — a directory containing `1.<ext>..4.<ext>` (e.g. a previous `splits/<datetime>/`).
- `<new_image>` — the image that replaces one quadrant. Any size; it will be resized to fit.
- `<position>` — the quadrant to replace: `1`=UL, `2`=UR, `3`=LL, `4`=LR.

```bash
image-quadrant-composer compose \
  ./image_quadrant_composer/splits/2026-04-20_20-07-51 \
  replacement.jpg 2
# writes ./image_quadrant_composer/composes/<datetime>/{1,2,3,4}.jpg and composed.jpg
```

### size

Print the width and height of one or more images. Useful for picking a split point.

```bash
image-quadrant-composer size <image> [<image> ...]
```

```bash
$ image-quadrant-composer size input.jpg
input.jpg: 400x300
```

### Module form

Equivalent invocation without the console script:

```bash
python -m image_quadrant_composer split input.jpg 150 100
python -m image_quadrant_composer compose ./.../splits/2026-04-20_20-07-51 replacement.jpg 2
python -m image_quadrant_composer size input.jpg
```

## Library

```python
from image_quadrant_composer import split_image, compose_image, image_size

# inspect — (width, height) in pixels
w, h = image_size("input.jpg")

# split — size is the (width, height) of the upper-left quadrant
split_dir, pieces = split_image("input.jpg", (150, 100))
# split_dir == .../image_quadrant_composer/splits/<datetime>
# pieces   == [<split_dir>/1.jpg, .../2.jpg, .../3.jpg, .../4.jpg]

# compose — replace quadrant 2 with a new image of any size
compose_dir, composed = compose_image(split_dir, "replacement.jpg", position=2)
# compose_dir contains 1..4.jpg plus composed.jpg
# composed is the reassembled PIL.Image
```

### API

- `split_image(image, size, root=".", ext="jpg") -> (Path, list[Path])`
  - `image`: path-like or `PIL.Image.Image`.
  - `size`: `(width, height)` of the upper-left quadrant; must lie strictly inside the image.
  - Returns `(output_dir, [1.jpg, 2.jpg, 3.jpg, 4.jpg])`.
- `compose_image(source, new_image, position, root=".", ext="jpg") -> (Path, PIL.Image.Image)`
  - `source`: directory containing `1.<ext>..4.<ext>`.
  - `new_image`: replacement image (path-like or `PIL.Image.Image`); resized automatically.
  - `position`: integer `1..4` — which quadrant to replace.
  - Returns `(output_dir, composed_image)`. The four pieces and `composed.<ext>` are written into `output_dir`.
- `image_size(image) -> (int, int)`
  - `image`: path-like or `PIL.Image.Image`.
  - Returns `(width, height)` in pixels without loading the full pixel data.
