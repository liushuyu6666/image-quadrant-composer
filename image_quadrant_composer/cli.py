from __future__ import annotations

import argparse
import sys

from .composer import compose_image
from .splitter import split_image


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="image-quadrant-composer",
        description="Split an image into four quadrants or compose them back.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_split = sub.add_parser("split", help="split an image into 1..4.<ext>")
    p_split.add_argument("image", help="path to the input image")
    p_split.add_argument("width", type=int, help="width of the upper-left quadrant")
    p_split.add_argument("height", type=int, help="height of the upper-left quadrant")
    p_split.add_argument(
        "--root",
        default=".",
        help="output root; pieces go under <root>/image_quadrant_composer/splits/<datetime>/",
    )
    p_split.add_argument("--ext", default="jpg", help="output extension (default: jpg)")

    p_compose = sub.add_parser(
        "compose",
        help="replace one quadrant with a new image and compose the four pieces",
    )
    p_compose.add_argument("source", help="directory containing 1.<ext>..4.<ext>")
    p_compose.add_argument("new_image", help="image replacing the quadrant at --position")
    p_compose.add_argument(
        "position", type=int, choices=[1, 2, 3, 4], help="quadrant to replace (1..4)"
    )
    p_compose.add_argument(
        "--root",
        default=".",
        help="output root; results go under <root>/image_quadrant_composer/composes/<datetime>/",
    )
    p_compose.add_argument("--ext", default="jpg", help="extension (default: jpg)")

    args = parser.parse_args(argv)

    if args.command == "split":
        out_dir, paths = split_image(
            args.image,
            (args.width, args.height),
            root=args.root,
            ext=args.ext,
        )
        print(out_dir)
        for p in paths:
            print(p)
        return 0

    if args.command == "compose":
        out_dir, _ = compose_image(
            args.source,
            args.new_image,
            args.position,
            root=args.root,
            ext=args.ext,
        )
        print(out_dir)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
