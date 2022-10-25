#!/usr/bin/env python3

"""Protocols for the different components of the VC."""

from typing import Protocol, List, NamedTuple, Optional


DBObject = NamedTuple("DBObject", [("type", str), ("size", int), ("contents", bytes)])


class PDB(Protocol):
    """Interactions with the underlying DB."""

    def put(self, key: str, bb: bytes) -> None:
        """Associate the content bb to the key."""
        ...

    def get(self, key: str) -> Optional[DBObject]:
        """Get the contents associated with a key, returning them or None."""
        ...


class PDBObject(Protocol):
    """Object in the DB."""


class PHasher(Protocol):
    """Operations related to hash."""

    def hash(self, bb: bytes) -> str:
        """Calculate the hash for the given bytes."""
        ...

    def valid_hash(self, hsh: str) -> bool:
        """Return True if hsh is a valid hash, False otherwise."""
        ...


class PCommandProcessor(Protocol):
    """Protocol implemented by the different commands."""

    @property
    def key(self) -> str:
        """Return the key of this command."""
        ...

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        ...
