"""Default implementation of the Index protocol."""

import os.path

from typing import Dict, Optional, List
from vc.prots import PIndex, PObjectDB, PIndexEntry, DBObjectType


class Index(PIndex):
    """Staging area (index)."""

    db: PObjectDB
    entries: Dict[str, PIndexEntry]

    def __init__(self, db: PObjectDB):
        """Initialize the object."""
        self.db = db

        root = db.root_folder()
        self.entries = _read_index_from_file(root + "/index")

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

        with open(fil_or_dir, "rb") as f:
            bb = f.read()

        key = self.db.put(bb)
        self.entries[key] = PIndexEntry(
            key,
            "f",
            os.path.relpath(fil_or_dir, root + "/.."),
        )
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

    def save_to_db(self) -> str:
        """Save the Index to the DB, returning the key of the saved object."""
        raw_tree = _build_tree(self.entries)

        # Ensure all the intermediate dirs are in the tree
        dirs = set()
        for d in set(raw_tree.keys()):
            for c in _subdirs(d):
                dirs.add(c)

        for d in dirs:
            if d not in raw_tree.keys():
                raw_tree[d] = []

        for d in raw_tree.keys():
            p = _parent_dir(d)
            if d == p:
                continue
            pn = raw_tree[p]
            pn.append(PIndexEntry("", "d", d))

        return _save_to_db_node("", raw_tree, self.db)


def _save_to_db_node(d: str, tree: Dict[str, PIndexEntry], db: PObjectDB) -> str:
    ob = _build_tree_object(d, tree, db)
    return db.put(ob.encode("UTF-8"), DBObjectType.TREE)


def _build_tree_object(d: str, tree: Dict[str, PIndexEntry], db: PObjectDB) -> str:
    ob = ""
    for en in tree[d]:
        if en.type == "f":
            key = en.key
        elif en.type == "d":
            key = _save_to_db_node(en.name, tree, db)
        else:
            raise Exception(f"Internal error: index entry type incorrect ({en.type})")
        ob = ob + en.type + " " + key + " " + en.name + "\n"

    print(f"DEBUG: _build_tree_object for '{d}': \n{ob}")
    return ob


def _subdirs(d: str) -> List[str]:
    """Calculate all the subdirs of a given directory.

    Example:
    _subdirs("src/com/inc") => ["src/com", "src"]
    """
    els = d.split("/")
    ret = [""]
    while len(els) > 0:
        ret.append("/".join(els))
        els = els[:-1]
    return ret


def _parent_dir(d: str) -> Optional[str]:
    """Return the parent dir of the given dir."""
    if d.strip() == "":
        return ""
    return "".join(d.split("/")[:-1])


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
                ret[s[0:40]] = _str_to_entry(
                    s
                )  # FIXME remove 0:40 and take the value from the list

            return ret
    except Exception:
        return {}


def _keyf_dir(e: PIndexEntry) -> str:
    return os.path.dirname(e.name)


def _build_tree(idx: Dict[str, PIndexEntry]):
    ret: Dict[str, list] = {}

    for e in idx.values():
        k, t, n = e
        d = os.path.dirname(n)
        if not ret.get(d):
            ret[d] = []
        ret[d].append(e)

    return ret
