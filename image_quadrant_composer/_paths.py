from __future__ import annotations

from datetime import datetime
from pathlib import Path

PACKAGE_FOLDER = "image_quadrant_composer"
SPLITS_FOLDER = "splits"
COMPOSES_FOLDER = "composes"


def timestamped_dir(root: str | Path, kind: str) -> Path:
    """Create and return ``<root>/image_quadrant_composer/<kind>/<datetime>/``."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = Path(root) / PACKAGE_FOLDER / kind / stamp
    path.mkdir(parents=True, exist_ok=True)
    return path
