"""Default implementation of the Index protocol."""

import os.path
import json

from typing import Dict
from vc.prots import PIndex, PObjectDB, PIndexEntry


class Index(PIndex):
    """Staging area (index)."""

    db: PObjectDB
    entries: Dict[str, PIndexEntry]

    def __init__(self, db: PObjectDB):
        """Initialize the object."""
        self.db = db
        self.entries = {}

    def stage_file(self, fil_or_dir: str):
        """Stage the given file or directory to the index file.

        If the file has already been added, the entry is updated.
        If the file has not been added, add it.
        """
        root = self.db.root_folder()

        if os.path.isdir(fil_or_dir):
            raise Exception("Directories are not supported yet.")

        if not (os.path.isfile(fil_or_dir)):
            raise FileNotFoundError(f"Not a valid file '{fil_or_dir}'")

        idx = _read_index_from_file(root + "/index")

        with open(fil_or_dir, "rb") as f:
            bb = f.read()

        key = self.db.put(bb)
        idx[key] = (
            key,
            "f",
            os.path.relpath(fil_or_dir, root + "/.."),
        )
        self.entries = idx
        _write_index_to_file(self.entries, root + "/index")

    def unstage_file(self, fil: str):
        """Unstages the file, from the file, reverting it to the previous state."""

    def remove_file(self, fil: str):
        """Remove the file from the index, making it not tracked."""
        if os.path.isdir(fil):
            raise Exception("Directories are not supported yet.")

        if not (os.path.isfile(fil)):
            raise FileNotFoundError(f"Not a valid file '{fil}'")

        del self.entries[os.path.relpath(fil, self.db.root_folder())]
        _write_index_to_file(self.entries, self.db.root_folder() + "/index")


def _entry_to_str(e: PIndexEntry) -> str:
    return f"{e[0]} {e[1]} {e[2]}"


def _str_to_entry(s: str) -> PIndexEntry:
    return PIndexEntry(s[0:40], s[41], s[43:])


def _write_index_to_file(idx: Dict[str, PIndexEntry], fil: str):
    with open(fil, "w") as f:
        for it in idx.values():
            f.write(_entry_to_str(it) + "\n")


def _read_index_from_file(fil: str) -> Dict[str, PIndexEntry]:
    try:
        with open(fil, "r") as f:
            content: str = f.read()
            lines = content.splitlines()

            ret = {}
            for s in lines:
                ret[s[0:40]] = _str_to_entry(s)

            return ret
    except Exception:
        return {}
