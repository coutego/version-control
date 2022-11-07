"""Utility functions for filesystem operations."""

import os
import os.path
from typing import Optional

VC_DIR = ".vc"


def find_vc_root_dir(startdir=os.curdir) -> Optional[str]:
    """Find the current repo root dir '.vc', if we are in a repo."""
    curr = startdir
    prev = None

    while True:
        if prev and os.path.realpath(curr) == os.path.realpath(prev):
            return None
        d = curr + "/" + VC_DIR
        if os.path.isdir(d):
            return d  # Found it!
        prev = curr
        curr = prev + "/.."
    return None  # Wasn't found


def create_vc_root_dir(parent_dir=os.curdir) -> str:
    """Create a repo in the current dir (or parent_dir)."""
    d = os.path.realpath(os.path.curdir) + "/" + VC_DIR
    if os.path.exists(d):
        raise Exception(f"File '{d}' already exists.")
    os.mkdir(d)
    return d
