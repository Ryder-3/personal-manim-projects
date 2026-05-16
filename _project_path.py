"""Add the repo root to sys.path so scenes in subfolders can import local packages."""
from __future__ import annotations

import sys
from pathlib import Path


def ensure_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "mobjects").is_dir():
            root = str(parent)
            if root not in sys.path:
                sys.path.insert(0, root)
            return parent
    raise ImportError(
        "Could not find project root. Expected a 'mobjects' directory "
        "in an ancestor of the repo."
    )


ensure_project_root()
