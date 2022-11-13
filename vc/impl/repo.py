"""Implementation of the PRepo protocol."""

from __future__ import annotations  # For factory methods in Commit, etc.
import os
import os.path
import difflib
from itertools import dropwhile
from dataclasses import dataclass
from typing import List, Optional, Callable, Tuple
from ..api import (
    PRepo,
    LogEntry,
    RepoStatus,
    PIndex,
    PObjectDB,
    DirName,
    FileWithStatus,
    FileStatus,
    DirEntry,
    DirDict,
    FileName,
)
from .fs import exists_file, head_read, head_write, list_files, read_file, remove_file, write_file, rename_file

class Repo(PRepo):
    """Represent a repository."""

    _index: PIndex
    _db: PObjectDB
    root: str

    def __init__(self, index: PIndex, db: PObjectDB, root: str):
        """Initialize the index and db."""
        self._index = index
        self._db = db
        self.root = root

    @property
    def db(self) -> PObjectDB:
        """Return the db used by this repo."""
        return self._db

    @property
    def index(self) -> PIndex:
        """Return the index used by this repo."""
        return self._index

    def init_repo(self):
        """Initialize the repo."""
        ini_branch = "master" # FIXME make 'master' configurable
        _branch_create(self.root, ini_branch)
        head_write(self.root, "refs/heads/" + ini_branch)

    def status(self) -> RepoStatus:
        """Calculate and return the status of the repo."""
        return _status(self._index, self._db, self.root)

    def log(self) -> List[LogEntry]:
        """Return the log entries for the current HEAD."""
        return _log(self._db, self.root)

    def checkout(self, commit_id_or_branch: str, create_branch: bool = False) -> str:
        """Checkout the commit and return its short message.

        Any errors are thrown as an exception, with a message ready to
        be shown to the end user. if create_branch is true, commit_id_or_branch
        is assumed to be the name of a branch which will be created if it doesn't
        exist.
        """
        return _checkout(self._index, self._db, self.root, commit_id_or_branch, create_branch)

    def initialized(self) -> bool:
        """Check whether the repo has been initialized or not."""
        return self.root is not None and os.path.exists(self.root)

    def delete_branch(self, branch_name: str) -> str:
        """Delete the branch with the given name, returning its head."""
        return _branch_delete(self.root, branch_name)

    def rename_branch(self, branch_name: str, new_branch_name: str):
        """Move (rename) the branch to the given name."""
        _branch_rename(self.root, branch_name, new_branch_name)

    def create_branch(self, branch_name: str):
        """Create a branch with the given name."""
        _branch_create(self.root, branch_name)

    def list_branches(self) -> Tuple[List[str], Optional[str]]:
        """List the existing branches.."""
        return _branch_list(self.root)

    def diff(self, files: List[str]) -> List[str]:
        """Calculates the diff for the given list of files.

        If the list is empty, provide the diff for all files.
        By default, the diff is between the file in the workdir and the head.
        """
        return _diff(self.root, self.db, self.index, files)

@dataclass
class Commit:
    """Represents a Commit object."""

    id: str
    parents: List[str]
    tree_id: str
    comment: str
    author: str
    committer: str

    @property
    def short_comment(self) -> str:
        """Return the first line of the comment."""
        lines = self.comment.splitlines()
        ret = ""
        for ln in lines:
            if ln.strip() != "":
                ret = ln.strip()
                break
        return ret

    @staticmethod
    def from_str(s: str) -> Commit:
        """Build a Commit from its str file representation."""
        parents: List[str] = []
        id = ""
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
        clns = dropwhile(lambda x: "" == x.strip(), comment.splitlines())
        comment = "\n".join(clns)
        return Commit(id, parents, tree_id, comment, author, committer)

    def to_str(self) -> str:
        """Represent a Commit as a str suitable to store on a file."""
        ret = "" # FIXME: semantics are not clear
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
        try:
            c = db.get(hsh)
        except:
            return None
        cs = c.text
        ret = Commit.from_str(cs)
        ret.id = hsh
        return ret

    @staticmethod
    def from_branch(root: str, branch: str, db: PObjectDB) -> Optional[Commit]:
        """Read a Commit from the db from the head of the branch."""
        commit = _branch_head(root, branch)
        if commit is None:
            return None
        return Commit.from_hash(commit, db)

@dataclass
class TreeEntry:
    """Represents an entry on a tree object."""

    hash: str
    type: str
    name: str

    @staticmethod
    def from_str(s: str) -> TreeEntry:
        """Build a TreeEntry from its str file representation."""
        t, h, *r = s.split(" ")
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
        return self.split("/")[-1]

    @property
    def dir(self):
        """Return the directory of the file, without the filename."""
        if "/" not in self:
            return ""
        return "/".join(self.split("/")[:-1])


def _status(index: PIndex, db: PObjectDB, root: str) -> RepoStatus:
    if root is None or root.strip() == "":
        raise FileNotFoundError("Not in a repository")
    stag_dict: DirDict = index.dirtree()
    dirs = list(stag_dict.keys())
    work_dict: DirDict = _build_working_dict(dirs, _read_ignore(root))
    head_dict: DirDict = _build_head_dict(db, root)

    staged: List[FileWithStatus] = []
    not_staged: List[FileWithStatus] = []
    not_tracked: List[FileWithStatus] = []

    b, h = _branch_current(root)
    ret = RepoStatus(b, h[:7] if b is None else "", staged, not_staged, not_tracked)

    all_files = []
    all_files.extend(stag_dict.all_file_names())
    all_files.extend(work_dict.all_file_names())
    all_files.extend(head_dict.all_file_names())

    set_all_files = set(all_files)
    for f in set_all_files:
        ret = _add_file_to_repostatus(
            FilePath(f), ret, stag_dict, work_dict, head_dict, db
        )
    return ret


def _add_file_to_repostatus(
    f: FilePath,
    rs: RepoStatus,
    stag_dict: DirDict,
    work_dict: DirDict,
    head_dict: DirDict,
    db: PObjectDB,
) -> RepoStatus:
    if f == "":
        f = FilePath(".")
    if not stag_dict.contains_file(f):
        if work_dict.contains_file(f):
            rs.not_tracked.append(FileWithStatus(f, None))
            return rs  # We are done
        if head_dict.contains_file(f):
            rs.not_staged.append(FileWithStatus(f, FileStatus.DELETED))
            return rs  # We are done
    if _file_is_modified_in_staging_tree(f, stag_dict, head_dict):
        if not head_dict.contains_file(f):
            rs.staged.append(FileWithStatus(f, FileStatus.NEW))
        else:
            rs.staged.append(FileWithStatus(f, FileStatus.MODIFIED))
    if _file_is_modified_in_working_tree(f, stag_dict, db):
        rs.not_staged.append(FileWithStatus(f, FileStatus.MODIFIED))
    return rs


def _file_is_modified_in_working_tree(
    f: FilePath, stag_dict: DirDict, db: PObjectDB
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
            st = stag_dict[d]
            fss = [ff for ff in st if ff.ename == f]
            if len(fss) == 0:
                return False
            return fss[0].ehash != k1
    except Exception:
        return False


def _file_is_modified_in_staging_tree(
    f: FilePath, stag_dict: DirDict, head_dict: DirDict
) -> bool:
    """Return True is f is modified in the staging tree, with respect to HEAD."""
    if f == "" or os.path.isdir(f):
        return False
    fes = _get_file_entry_from_dirdict(f, stag_dict)
    feh = _get_file_entry_from_dirdict(f, head_dict)
    fesh = fes.ehash if fes else ""
    fehh = feh.ehash if feh else ""
    if fesh == fehh:
        return False
    else:
        return True


def _get_file_entry_from_dirdict(f: FilePath, di: DirDict) -> Optional[DirEntry]:
    d: str = f.dir
    fs: List[DirEntry] = di[d] if d in di.keys() else []
    fe = [ff for ff in fs if ff.ename == f]
    if len(fe) > 0:
        return fe[0]
    else:
        return None


def _build_head_dict(db: PObjectDB, root: str) -> DirDict:
    """Build the DirDict for the current HEAD, from the DB."""
    _, key = _branch_current(root)
    if key is None or key == "":
        return DirDict()
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
            dd = d + "/" if d != "" else ""
            _add_tree_entries(dd + en.name, en.hash, db, ret)
        else:
            ret[d].append(DirEntry(en.name, en.type, en.hash))
    return ret


def _build_working_dict(
    dirs: List[DirName], ignorefn: Callable[[str], bool] = lambda _: False
) -> DirDict:
    """Build the DirDict for the working dir, only taking into account entries in 'dirs'."""
    ret = DirDict()
    for d in dirs + ['']:
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
            a = f
            if d != "":
                a = d + "/" + a
            ret[d].append(DirEntry(a, typ, ""))
    return ret


def _read_db_tree(db: PObjectDB, key: str, acc: Optional[DirDict] = None) -> DirDict:
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


def _read_ignore(root: str) -> Callable[[str], bool]:
    vcignore = root + "/../.vcignore"
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


def _log(db: PObjectDB, root: str) -> List[LogEntry]:
    """Return the log entries for the current HEAD."""
    ret: List[LogEntry] = []
    _, chash  = _branch_current(root)
    while chash:
        commit = Commit.from_hash(chash, db)
        if commit is None:
            return ret
        ret.append(LogEntry(chash, commit.short_comment))
        if commit.parents and len(commit.parents) > 0:
            chash = commit.parents[0]
        else:
            chash = None
    return ret


def _checkout(
        index: PIndex, db: PObjectDB, root: str, commit_id_or_branch: str, create_branch: bool
) -> Tuple[str, bool]:
    commit = Commit.from_hash(commit_id_or_branch, db)
    branch = None
    if commit is None:
        branch = commit_id_or_branch
        commit = Commit.from_branch(root, branch, db)
        if commit is None and create_branch:
                _branch_create(root, branch)
                commit = Commit.from_hash(_branch_head(root, branch) or "", db)
    if commit is None:
        raise Exception(
            f"error: pathspec '{commit_id_or_branch}' did not match any file(s) known to vc"
        )
    full_commit_hash = db.get_full_key(commit.id)

    de = _dirty_entries_in_index(index, db)
    if de:
        raise Exception(
            "error: Your local changes to the following files would be "
            + "overwritten by checkout:\n"
            + "       "
            + ", ".join([f for f in de])
            + "\n"
            + "Please commit your changes or stash them before you switch branches.\n"
            + "Aborting"
        )
    commit_dict = _add_tree_entries(root, commit.tree_id, db, DirDict())
    for _, fs in commit_dict.items():
        for f in fs:
            if not f.etype == "f":
                continue
            contents = db.get(f.ehash).contents
            with open(f.ename, "wb") as ff:
                ff.write(contents)
    if branch is None: # FIXME: refactor. This is a hack. branch
        head_write(root, full_commit_hash)
    else:
        head_write(root, "refs/heads/" + branch)
    index.set_to_dirtree(commit_dict)
    return (commit.comment.splitlines()[0], branch is None)


def _dirty_entries_in_index(index: PIndex, db: PObjectDB) -> List[FileName]:
    """Return the list of entries which are 'dirty' (different than in work dir)."""
    ret: List[FileName] = []
    tree = index.dirtree()
    for d in tree.keys():
        for f in tree[d]:
            if _is_dirty_in_index(f, db):
                ret.append(f.ename)
    return ret


def _is_dirty_in_index(f: DirEntry, db: PObjectDB) -> bool:
    with open(f.ename, "rb") as ff:
        hsh = db.calculate_key(ff.read())
    if f.ehash == hsh:
        return False
    else:
        return True

def _branch_current(root: str) -> Tuple[Optional[str], str]:
    """Return the name and commit id of the current branch.

    name can be None if head is detached.
    """
    headc = head_read(root)
    if headc[:5] == "refs/":
        rh = "refs/heads/"
        branch = rh + headc[len(rh):]
        branch = headc[len(rh):]

        headc = read_file(root, rh + branch)
        return (branch, headc)
    else:
        return (None, headc)

def _branch_head(root: str, branch: str) -> Optional[str]:
    rh = "refs/heads/" + branch
    commit = read_file(root, rh)
    return commit

def _branch_create(root: str, name: str) -> None:
    hf = "refs/heads/" + name
    if exists_file(root, hf):
        raise FileExistsError(f"The branch {name} already exists")
    _, commit_id = _branch_current(root)
    write_file(root, hf, commit_id)

def _branch_list(root: str) -> Tuple[List[str], Optional[str]]:
    branches = list_files(root, "refs/heads")
    curr, _ = _branch_current(root)
    return (branches, curr)

def _branch_delete(root: str, branch_name: str) -> str:
    b, _ =_branch_current(root)
    if b == branch_name:
        raise FileExistsError(f"error: Cannot delete branch '{b}' checked out at '{root}'")
    h = _branch_head(root, branch_name)
    remove_file(root, "refs/heads/" + branch_name)
    return h[:7] if h else ""

def _branch_rename(root: str, branch_name: str, branch_new_name):
    c = _branch_head(root, branch_name)
    if c == '':
        raise FileNotFoundError(f"error: refname refs/heads/{branch_name} not found")

    c = _branch_head(root, branch_new_name)
    if c != '':
        raise FileExistsError(f"fatal: a branch named '{branch_new_name}' already exists")

    rename_file(root, "refs/heads/" + branch_name, "refs/heads/" + branch_new_name)

def _diff(root: str, db: PObjectDB, index: PIndex, files: List[str]) -> List[str]:
    # FIXME: almost all this code is copied from _status -> refactor
    if root is None or root.strip() == "":
        raise FileNotFoundError("Not in a repository")
    stag_dict: DirDict = index.dirtree()
    dirs = list(stag_dict.keys())
    work_dict: DirDict = _build_working_dict(dirs, _read_ignore(root))
    head_dict: DirDict = _build_head_dict(db, root)

    all_files = []
    all_files.extend(stag_dict.all_file_names())
    all_files.extend(work_dict.all_file_names())
    all_files.extend(head_dict.all_file_names())

    set_all_files = set(all_files)
    if len(files) > 0:
        set_all_files = set_all_files.intersection(files)
    ret = []
    for f in set_all_files:
        ret.append(_diff_file(db, root, stag_dict, f))
    return ret


def _diff_file(db: PObjectDB, root: str, stag_dict: DirDict, file: str) -> str:
    fwdc = ""
    with open(root + '/../' + file, "r") as f:
        fwdc = f.read()
    fst = stag_dict.find_entry(file)
    fstc = ""
    if fst is not None:
        fstc = db.get(fst.ehash).text  # FIXME: support binary files
    return ''.join(difflib.context_diff(fstc.splitlines(True), fwdc.splitlines(True), fromfile=file, tofile=file))
