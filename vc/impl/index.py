"""Default implementation of the Index protocol."""

import os.path

from typing import Dict, Optional, List, Set
from vc.prots import (
    PIndex,
    PObjectDB,
    IndexEntry,
    DBObjectType,
    DirDict,
    DirEntry,
    Key,
    FileType,
    FileName,
)


class Index(PIndex):
    """Staging area (index)."""

    db: PObjectDB
    root: str

    def __init__(self, db: PObjectDB):
        """Initialize the object."""
        self.db = db
        self.root = db.root_folder()

    def stage_file(self, fil_or_dir: str) -> None:
        """Stage the given file or directory to the index file.

        If the file has already been added, the entry is updated.
        If the file has not been added, add it.
        """
        entries = _read_index_from_file(self.root + "/index")
        if os.path.isdir(fil_or_dir):
            raise Exception("Directories are not supported yet.")
        if not (os.path.isfile(fil_or_dir)):
            raise FileNotFoundError(f"Not a valid file '{fil_or_dir}'")
        with open(fil_or_dir, "rb") as f:
            bb = f.read()
        key = self.db.put(bb)
        entries[key] = IndexEntry(
            key,
            "f",
            os.path.relpath(fil_or_dir, self.root + "/.."),
        )
        _write_index_to_file(entries, self.root + "/index")

    def unstage_file(self, fil: str):
        """Unstages the file, from the file, reverting it to the previous state."""

    def remove_file(self, fil: str):
        """Remove the file from the index, making it not tracked."""
        entries = _read_index_from_file(self.root + "/index")

        if os.path.isdir(fil):
            raise Exception("Directories are not supported yet.")
        if not (os.path.isfile(fil)):
            raise FileNotFoundError(f"Not a valid file '{fil}'")

        del entries[os.path.relpath(fil, self.db.root_folder())]
        _write_index_to_file(entries, self.db.root_folder() + "/index")

    def save_to_db(self) -> str:
        """Save the Index to the DB, returning the key of the saved object."""
        entries = _read_index_from_file(self.root + "/index")
        raw_tree = _build_tree(entries)

        # Ensure all the intermediate dirs are in the tree
        dirs = _all_dirs_in_index(raw_tree)
        for d in dirs:
            if d not in raw_tree.keys():
                raw_tree[d] = []
        for d in raw_tree.keys():
            p = _parent_dir(d)
            if d == p:
                continue
            pn = raw_tree[p]
            pn.append(IndexEntry("", "d", d))
        return _save_to_db_node("", raw_tree, self.db)

    def commit(self, message: str = None) -> str:
        """Commit the current index, returning the commit hash."""
        if message is None:
            message = "<no commit message>"
        root = self.db.root_folder()
        head = root + "/HEAD"
        parent = ""

        if os.path.exists(head):
            with open(head, "r") as f:
                parent = f.read()

        commit = _prepare_commit(self.save_to_db(), parent, message)
        nkey = self.db.put(commit)
        with open(head, "w") as f:
            f.write(f"{nkey}\n")
        return nkey

    def dirtree(self) -> DirDict:
        """Return the contents of the staging area as a DirDict."""
        entries = _read_index_from_file(self.root + "/index")
        raw_tree = _build_tree(entries)
        ret = DirDict()
        for k, en in raw_tree.items():
            for e in en:
                if k not in ret.keys():
                    ret[k] = []
                ret[k].append(DirEntry(FileName(e.name), FileType(e.type), Key(e.key)))
        return ret


def _all_dirs_in_index(raw_tree: Dict[str, List[IndexEntry]]) -> Set[str]:
    dirs = set("")
    for d in set(raw_tree.keys()):
        for c in _subdirs(d):
            dirs.add(c)
    return dirs


def _prepare_commit(tree: str, parent_hash: str, message: str) -> str:
    ret = f"tree {tree}\n"

    if parent_hash and parent_hash.strip() != "":
        ret = ret + f"parent {parent_hash}\n"

    # ret = ret + "author\n"
    # ret = ret + "committer\n"
    ret = ret + "\n"
    ret = ret + f"{message}\n"

    return ret


def _save_to_db_node(d: str, tree: Dict[str, List[IndexEntry]], db: PObjectDB) -> str:
    ob = _build_tree_object(d, tree, db)
    return db.put(ob, DBObjectType.TREE)


def _build_tree_object(d: str, tree: Dict[str, List[IndexEntry]], db: PObjectDB) -> str:
    ob = ""
    for en in tree[d]:
        if en.type == "f":
            key = en.key
        elif en.type == "d":
            key = _save_to_db_node(en.name, tree, db)
        else:
            raise Exception(f"Internal error: index entry type incorrect ({en.type})")
        ob = ob + en.type + " " + key + " " + en.name + "\n"

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


def _entry_to_str(e: IndexEntry) -> str:
    return f"{e[0]} {e[1]} {e[2]}"


def _str_to_entry(s: str) -> IndexEntry:
    return IndexEntry(s[0:40], s[41], s[43:])


def _write_index_to_file(idx: Dict[str, IndexEntry], fil: str):
    with open(fil, "w") as f:
        for it in idx.values():
            f.write(_entry_to_str(it) + "\n")


def _read_index_from_file(fil: str) -> Dict[str, IndexEntry]:
    try:
        with open(fil, "r") as f:
            content: str = f.read()
            lines = content.splitlines()
            ret = {}
            for s in lines:
                en = _str_to_entry(s)
                ret[en[2]] = en
            return ret
    except Exception:
        return {}


def _keyf_dir(e: IndexEntry) -> str:
    return os.path.dirname(e.name)


def _build_tree(idx: Dict[str, IndexEntry]):
    ret: Dict[str, list] = {}
    for e in idx.values():
        k, t, n = e
        d = os.path.dirname(n)
        if not ret.get(d):
            ret[d] = []
        ret[d].append(e)
    return ret
