"""Protocols for the different components of the VC."""

from dataclasses import dataclass
from typing import Protocol, List, Optional, NamedTuple, Dict, Union
from enum import Enum


#####################################
# Repository
#####################################
FileName = str  # ex. 'foo.txt'
DirName = str  # ex. 'src/module'
Key = str  # Hash
Branch = str  # Hash representing a branch

FileStatus = Enum(
    "FileStatus",
    [
        ("NEW", "new"),
        ("MODIFIED", "modified"),
        ("DELETED", "deleted"),
        ("RENAMED", "renamed"),
    ],
)

FileWithStatus = NamedTuple(
    "FileWithStatus", [("name", FileName), ("status", Optional[FileStatus])]
)


FileType = str  # "f" or "d" FIXME: make it typesafe


@dataclass
class DirEntry:
    """Entry of a directory. It has a name, a type and an optional hash."""

    ename: FileName
    etype: FileType
    ehash: Key


class DirDict(Dict[DirName, List[DirEntry]]):
    """Dict mapping directories to the list of their contents."""

    def contains_file(self, f: FileName) -> bool:
        """Return True is the DirTree contains the given file."""
        for k, fs in self.items():
            if f in [fl.ename for fl in fs]:
                return True
        return False

    def all_file_names(self) -> List[FileName]:
        """Return all the (complete) file names in this DirTree."""
        ret = []
        for ens in self.values():
            for f in ens:
                ret.append(f.ename)

        return ret


@dataclass
class RepoStatus:
    """Captures the status of a repo."""

    branch: Branch
    not_tracked: List[FileWithStatus]
    not_staged: List[FileWithStatus]
    staged: List[FileWithStatus]


class PRepo(Protocol):
    """Represent a repository."""

    def status(self) -> RepoStatus:
        """Calculate and return the status of the repo."""


#####################################
# Object DB
#####################################
class DBObjectType(Enum):
    """Types of db object."""

    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"
    TAG = "tag"


DBObjectKey = str


@dataclass
class DBObject:
    """Representation of an object in the DB."""

    type: DBObjectType
    size: int
    contents: bytes

    @property
    def text(self) -> str:
        """Return the contents of the object, as a string."""
        return self.contents.decode("UTF-8")


class PHasher(Protocol):
    """Responsible to calculate hashes to be used as DB keys."""

    def hash(self, bb: bytes) -> str:
        """Calculate the hash for the given bytes."""
        ...

    def valid_hash(self, hsh: str) -> bool:
        """Return True if hsh is a valid hash, False otherwise."""
        ...


class PObjectDB(Protocol):
    """Interactions with the underlying DB."""

    def init(self) -> None:
        """Create and initialize the DB."""
        ...

    def put(
        self, bb: Union[bytes, str], typ: DBObjectType = DBObjectType.BLOB
    ) -> DBObjectKey:
        """Associate the content bb to the key.

        Return the object key if succesful (either new entry created or
        an existing one found).
        """
        ...

    def calculate_key(self, bb: bytes):
        """Calculate the key for a given contents, same as in 'put'."""
        ...

    def get(self, key: str) -> Optional[DBObject]:
        """Get the contents associated with a key, returning them or None."""
        ...

    def root_folder(self) -> str:
        """Return the root folder where this DB is located."""
        ...


#####################################
# Index (staging area)
#####################################
IndexEntry = NamedTuple("IndexEntry", [("key", str), ("type", str), ("name", str)])

IndexStatus = NamedTuple(
    "IndexStatus",
    [
        ("branch", str),
        ("not_tracked", List[FileWithStatus]),
        ("not_staged", List[FileWithStatus]),
        ("staged", List[FileWithStatus]),
    ],
)


class PIndex(Protocol):
    """Staging area (index)."""

    def stage_file(self, fil_or_dir: str):
        """Stage the given file or directory to the index file.

        If the file has already been added, the entry is updated.
        If the file has not been added, add it.
        """
        ...

    def unstage_file(self, fil: str):
        """Unstages the file, from the file, reverting it to the previous state."""
        ...

    def remove_file(self, fil: str):
        """Remove the file from the index, making it not tracked."""
        ...

    def save_to_db(self) -> str:
        """Save the Index to the DB, returning the key of the saved object."""
        ...

    def commit(self, message: str = None) -> str:
        """Commit this index, returning the hash of the commit."""
        ...

    def dirtree(self) -> DirDict:
        """Return the representation of the stage area as a DirTree."""
        ...


#####################################
# Commands
#####################################
class PCommandProcessor(Protocol):
    """Protocol implemented by the (sub)commands."""

    @property
    def key(self) -> str:
        """Return the key of this command."""
        ...

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        ...
