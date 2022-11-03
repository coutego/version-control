"""Implementation of the PRepo protocol."""

from __future__ import annotations  # For factory methods in Commit, etc.
import os
import os.path
from dataclasses import dataclass
from typing import List, Optional, Callable
from vc.prots import (
    PRepo,
    RepoStatus,
    PIndex,
    PObjectDB,
    DirName,
    FileWithStatus,
    FileStatus,
    DirEntry,
    DirDict,
)


class Repo(PRepo):
    """Represent a repository."""

    index: PIndex
    db: PObjectDB

    def __init__(self, index: PIndex, db: PObjectDB):
        """Initialize the index and db."""
        self.index = index
        self.db = db

    def status(self) -> RepoStatus:
        """Calculate and return the status of the repo."""
        return _status(self.index, self.db)


@dataclass
class Commit:
    """Represents a Commit object."""

    parents: List[str]
    tree_id: str
    comment: str
    author: str
    committer: str

    @staticmethod
    def from_str(s: str) -> Commit:
        """Build a Commit from its str file representation."""
        parents: List[str] = []
        tree_id = ""
        comment = ""
        author = ""
        committer = ""

        comment_started = False
        for ln in s.splitlines():
            if not comment_started:
                if ln.startswith("parent "):
                    parents.append(ln.removeprefix("parent ").strip())
                elif ln.startswith("tree "):
                    tree_id = ln.removeprefix("tree ").strip()
                elif ln.startswith("author "):
                    author = ln.removeprefix("author ").strip()
                elif ln.startswith("commiter "):
                    committer = ln.removeprefix("commiter ").strip()
                else:
                    comment_started = True
                    comment += ln + "\n"
            else:
                comment += ln + "\n"

        return Commit(parents, tree_id, comment, author, committer)

    def to_str(self) -> str:
        """Represent a Commit as a str suitable to store on a file."""
        ret = ""
        if self.tree_id:
            ret += "tree_id " + self.tree_id + "\n"
        if self.parents:
            for p in self.parents:
                ret += "parent " + p + "\n"
        if self.author:
            ret += "author " + self.author + "\n"
        if self.committer:
            ret += "committer " + self.committer + "\n"
        if self.comment:
            ret += "comment " + self.comment + "\n"

        return ret

    @staticmethod
    def from_hash(hsh: str, db: PObjectDB) -> Optional[Commit]:
        """Read a Commit from the db from its hash."""
        c = db.get(hsh)

        if c is None:
            return None

        cs = c.text
        return Commit.from_str(cs)


@dataclass
class TreeEntry:
    """Represents an entry on a tree object."""

    hash: str
    type: str
    name: str

    @staticmethod
    def from_str(s: str) -> TreeEntry:
        """Build a TreeEntry from its str file representation."""
        h, t, *r = s.split(" ")
        n = " ".join(r)  # In case the file name has spaces
        return TreeEntry(h, t, n)

    def to_str(self) -> str:
        """Represent a TreeEntry as a str suitable to be stored on a file."""
        return f"{self.hash} {self.type} {self.name}"


@dataclass
class Tree:
    """Represents a Tree object."""

    entries: List[TreeEntry]

    @staticmethod
    def from_str(s: str) -> Tree:
        """Build a Tree from its str file representation."""
        ret = []
        for lin in s.splitlines():
            ret.append(TreeEntry.from_str(lin))
        return Tree(ret)

    def to_str(self) -> str:
        """Represent a Treeas a str suitable to be stored on a file."""
        ret = ""
        for e in self.entries:
            ret += e.to_str() + "\n"
        return ret


class FilePath(str):
    """Represents a complete (relative) file path."""

    @property
    def file_name(self):
        """Return the file name, without the path."""
        if "/" not in self:
            return self
        else:
            return self.split("/")[-1]

    @property
    def dir(self):
        """Return the directory of the file, without the filename."""
        if "/" not in self:
            "."
        else:
            return self.split("/")[:-1]


def _status(index: PIndex, db: PObjectDB) -> RepoStatus:
    staging_tree: DirDict = index.dirtree()
    dirs = list(staging_tree.keys())
    working_tree: DirDict = _build_working_dict(dirs, _read_ignore(db))
    head_tree: DirDict = _build_head_dict(db)

    staged: List[FileWithStatus] = []
    not_staged: List[FileWithStatus] = []
    not_tracked: List[FileWithStatus] = []

    ret = RepoStatus("*not implemented*", staged, not_staged, not_tracked)

    all_files = []
    for d in dirs:
        all_files.extend(staging_tree.all_file_names())
        all_files.extend(working_tree.all_file_names())
        all_files.extend(head_tree.all_file_names())

    set_all_files = set(all_files)
    for f in set_all_files:
        ret = _add_file_to_repostatus(
            FilePath(f), ret, staging_tree, working_tree, head_tree, db
        )

    return ret


def _add_file_to_repostatus(
    f: FilePath,
    rs: RepoStatus,
    staging_tree: DirDict,
    working_tree: DirDict,
    head_tree: DirDict,
    db: PObjectDB,
) -> RepoStatus:
    if f == "":
        f = FilePath(".")

    if not staging_tree.contains_file(f):
        if working_tree.contains_file(f):
            rs.not_tracked.append(FileWithStatus(f, None))
            return rs
        if head_tree.contains_file(f):
            rs.not_staged.append(FileWithStatus(f, FileStatus.DELETED))
            return rs

    if not head_tree.contains_file(f):
        rs.staged.append(FileWithStatus(f, FileStatus.NEW))

    if _file_is_modified_in_working_tree(f, working_tree, staging_tree, db):
        rs.not_staged.append(FileWithStatus(f, FileStatus.MODIFIED))

    if _file_is_modified_in_staging_tree(f, staging_tree, head_tree, db):
        rs.staged.append(FileWithStatus(f, FileStatus.MODIFIED))

    return rs


def _file_is_modified_in_working_tree(
    f: FilePath, working_tree: DirDict, staging_tree: DirDict, db: PObjectDB
) -> bool:
    """Return True is f is modified in the working tree, with respect to the index."""
    if f == "" or os.path.isdir(f):
        return False

    try:
        with open(f.file_name, "rb") as ff:
            bb = ff.read()
            k1 = db.calculate_key(bb)
            if f.dir is None:  # FIXME: cleanup the usage of "" vs "." vs None
                d = ""
            else:
                d = f.dir
            st = staging_tree[d]
            fss = [ff for ff in st if ff.ename == f.file_name]

            if len(fss) == 0:
                return False

            return fss[0].ehash != k1
    except Exception:
        return False


def _file_is_modified_in_staging_tree(
    f: FilePath, staging_tree: DirDict, head_tree: DirDict, db: PObjectDB
) -> bool:
    """Return True is f is modified in the staging tree, with respect to HEAD."""
    if f == "" or os.path.isdir(f):
        return False
    try:
        fs = [ff for ff in staging_tree[f.dir] if ff.ename == f.file_name][0]
        fh = [ff for ff in head_tree[f.dir] if ff.ename == f.file_name][0]
        return fs.ehash == fh.ehash
    except Exception:
        return False


def _build_head_dict(db: PObjectDB) -> DirDict:
    """Build the DirDict for the current HEAD, from the DB."""
    key = _read_head_hash(db)
    commit = Commit.from_hash(key, db)

    if commit is None:
        return DirDict()

    key = commit.tree_id

    return _add_tree_entries("", key, db, DirDict())


def _add_tree_entries(d: DirName, key: str, db: PObjectDB, ret: DirDict) -> DirDict:
    """Recursively add the tree entries for the tree of hash key to the DirDict.

    The passed DirDict is modified in place, even if it's also returned, for convenience.
    """
    t = db.get(key)

    if t is None:
        return ret

    tree = Tree.from_str(t.text)

    ret[d] = []
    for en in tree.entries:
        if en.type == "d":
            _add_tree_entries(d + "/" + en.name, en.hash, db, ret)
        else:
            ret[d].append(DirEntry(en.name, en.type, en.hash))

    return ret


def _build_working_dict(
    dirs: List[DirName], ignorefn: Callable[[str], bool] = lambda x: False
) -> DirDict:
    """Build the DirDict for the working dir, only taking into account entries in 'dirs'."""
    ret = DirDict()

    for d in dirs:
        if d == "":
            dd = "."
        else:
            dd = d
        files = os.listdir(dd)
        for f in files:
            if ignorefn(f):
                continue
            if os.path.isdir(f):
                typ = "d"
            else:
                typ = "f"
            if d not in ret:
                ret[d] = []
            ret[d].append(DirEntry(f, typ, ""))

    return ret


def _read_head_hash(db: PObjectDB) -> str:
    """Read and return the hash for the current HEAD."""
    head = db.root_folder() + "/HEAD"

    if not os.path.exists(head):
        return ""

    with open(head, "r") as f:
        return f.read().strip()  # FIXME: follow references


def _read_db_tree(db: PObjectDB, key: str, acc: DirDict = None) -> DirDict:
    """Read a tree object from the DB, recursively building the associated DirDict."""
    if acc is None:
        acc = DirDict()

    linesr = db.get(key)
    if linesr is None:
        raise Exception(f"Object not found: '{key}'")
    lines = linesr.text.splitlines()

    for ln in lines:
        en = DirEntry(ln[43:], ln[0:40], ln[41])
        enp = FilePath(en.ename)

        if en.etype == "d":
            _read_db_tree(db, en.ehash, acc)

        ens = acc[enp]
        if ens is None:
            acc[enp] = []

        acc[enp].append(en)

    return acc


def _read_ignore(db: PObjectDB) -> Callable[[str], bool]:
    vcignore = db.root_folder() + "/../.vcignore"

    entries = ".vc\n"  # Never track the .vc dir

    if os.path.exists(vcignore):
        with open(vcignore, "r") as f:
            entries += f.read()

    return lambda x: _matches(entries.splitlines(), x)


def _matches(patterns: List[str], s: str) -> bool:
    import re

    for p in patterns:
        if re.match(f"^{p}$", s):
            return True

    return False
