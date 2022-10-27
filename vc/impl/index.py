"""Default implementation of the Index protocol."""

import os.path
import json

from typing import NamedTuple, Dict
from vc.prots import PIndex, PObjectDB


IndexEntry = NamedTuple("IndexEntry", [("key", str), ("type", str), ("name", str)])


class Index(PIndex):
    """Staging area (index)."""

    db: PObjectDB
    entries: Dict[str, IndexEntry]

    def __init__(self, db: PObjectDB):
        """Initialize the object."""
        self.db = db
        self.entries = {}

    def stage_file(self, fil_or_dir: str):
        """Stage the given file or directory to the index file.

        If the file has already been added, the entry is updated.
        If the file has not been added, add it.
        """
        if os.path.isdir(fil_or_dir):
            raise Exception("Directories are not supported yet.")

        if not (os.path.isfile(fil_or_dir)):
            raise FileNotFoundError(f"Not a valid file '{fil_or_dir}'")

        with open(fil_or_dir, "rb") as f:
            bb = f.read()

        key = self.db.put(bb)
        self.entries[key] = (
            key,
            "f",
            os.path.realpath(fil_or_dir),
        )  # FIXME: remove vc root file from the path
        _write_index_to_file(self.entries, self.db.root_folder() + "/index")

    def unstage_file(self, fil: str):
        """Unstages the file, from the file, reverting it to the previous state."""

    def remove_file(self, fil: str):
        """Remove the file from the index, making it not tracked."""
        if os.path.isdir(fil):
            raise Exception("Directories are not supported yet.")

        if not (os.path.isfile(fil)):
            raise FileNotFoundError(f"Not a valid file '{fil}'")

        del self.entries[os.path.realpath(fil)]  # FIXME make name canonical
        _write_index_to_file(self.entries, self.db.root_folder() + "/index")


def _write_index_to_file(idx: Dict[str, IndexEntry], fil: str):
    with open(fil, "w") as f:
        json.dump(list(idx.values()), f, indent=0)


def _read_index_from_file(idx: Dict[str, IndexEntry], fil: str):
    with open(fil, "r") as f:
        json.load(f)
