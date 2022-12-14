"""Protocols for the different components of the VC."""

from dataclasses import dataclass
from typing import Protocol, List, Optional, NamedTuple, Dict, Union, Tuple
from enum import Enum


#####################################
# Common types used by the Protocols
#####################################
class VCUserException(Exception):
    """Exception for errors to show to the end user."""


FileName = str  # ex. 'foo.txt'
DirName = str  # ex. 'src/module'
Key = str  # Hash
Branch = str  # Hash representing a branch


class FileStatus(Enum):
    NEW = "new file"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class FileWithStatus:
    """Representation of a file with a status, for the status report."""

    name: FileName
    status: Optional[FileStatus]


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
        for _, fs in self.items():
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

    def find_entry(self, f: FileName) -> Optional[DirEntry]:
        """Find the entry for the given filename and return it."""
        for _, fs in self.items():
            for fl in fs:
                if fl.ename == f:
                    return fl
        return None  # FIXME: implement contains_file on top of this method


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


class PObjectDB(Protocol):
    """Interactions with the underlying DB."""

    def put(
        self, content: Union[bytes, str], typ: DBObjectType = DBObjectType.BLOB
    ) -> DBObjectKey:
        """Associate the content bb to the key.

        Return the object key if succesful (either new entry created or
        an existing one found).
        """
        ...

    def calculate_key(self, content: bytes):
        """Calculate the key for a given contents, same as in 'put'."""
        ...

    def get(self, key: str) -> DBObject:
        """Get the contents associated with a key.

        Return the db object or raise a FileNotFoundError if not found.
        """
        ...

    def get_full_key(self, commit_id: str) -> str:
        """Return the full key from a partial key."""
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

    def commit(self, message: Optional[str] = None) -> str:
        """Commit this index, returning the hash of the commit."""
        ...

    def dirtree(self) -> DirDict:
        """Return the representation of the stage area as a DirTree."""
        ...

    def set_to_dirtree(self, dd: DirDict) -> None:
        """Make the index correspond to the passed dd."""
        ...


#####################################
# Repository
#####################################


@dataclass
class RepoStatus:
    """Captures the status of a repo."""

    branch: Optional[Branch]
    detached: Optional[str]
    not_tracked: List[FileWithStatus]
    not_staged: List[FileWithStatus]
    staged: List[FileWithStatus]


@dataclass
class LogEntry:
    """Represent an entry in the 'log'."""

    key: str
    comment: str


class PRepo(Protocol):
    """Represent a repository."""

    def status(self) -> RepoStatus:
        """Calculate and return the status of the repo."""
        ...

    def log(self) -> List[LogEntry]:
        """Return the log entries for the current HEAD."""
        ...

    def checkout(
        self, commit_id_or_branch: str, create_branch: bool = False
    ) -> Tuple[str, bool]:
        """Checkout the commit and return its short message.

        Any errors are thrown as an exception, with a message ready to
        be shown to the end user. if create_branch is true, commit_id_or_branch
        is assumed to be the name of a branch which will be created if it doesn't
        exist.
        """
        ...

    def initialized(self) -> bool:
        """Check whether the repo has been initialized or not."""
        ...

    def delete_branch(self, branch_name: str) -> str:
        """Delete the branch with the given name, returning its head.

        Raise a FileNotFoundError if the branch doesn't exist.
        Raise a FileExistsError if the branch is checked out.
        """
        ...

    def rename_branch(self, branch_name: str, destination_branch_name: str):
        """Move (rename) the branch to the given name.

        Raise a FileNotFoundError if branch_name doesn't exist.
        Raise a FileExistsError if destination_branch_name already exists.
        """
        ...

    def create_branch(self, branch_name: str):
        """Create a branch with the given name.

        Raise FileExistsError is the branch already exists.
        """
        ...

    def list_branches(self) -> Tuple[List[str], Optional[str]]:
        """List the existing branches.."""
        ...

    def diff(self, files: List[str]) -> List[str]:
        """Calculates the diff for the given list of files.

        If the list is empty, provide the diff for all files.
        By default, the diff is between the file in the workdir and the head.
        """
        ...

    @property
    def db(self) -> PObjectDB:
        """Return the db used by this repo."""
        ...

    @property
    def index(self) -> PIndex:
        """Return the index used by this repo."""
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
