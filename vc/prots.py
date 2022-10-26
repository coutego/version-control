#!/usr/bin/env python3

"""Protocols for the different components of the VC."""

from typing import Protocol, List, Optional, NamedTuple
from enum import Enum


class DBObjectType(Enum):
    """Types of db object."""

    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"
    TAG = "tag"


# Transfer object for objects in the DB
DBObject = NamedTuple(
    "DBObject", [("type", DBObjectType), ("size", int), ("contents", bytes)]
)
DBObjectKey = str


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

    def put(self, bb: bytes, typ: DBObjectType = DBObjectType.BLOB) -> DBObjectKey:
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


class PCommandProcessor(Protocol):
    """Protocol implemented by the different (sub)commands."""

    @property
    def key(self) -> str:
        """Return the key of this command."""
        ...

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        ...
