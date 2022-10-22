#!/usr/bin/env python3

"""Protocols for the different components of the VC."""

from typing import Protocol


class PDB(Protocol):
    """Interactions with the underlying DB."""

    def put(self, key: str, bb: bytes) -> None:
        """Associate the content bb to the key."""
        ...

    def get(self, key: str) -> bytes:
        """Get the contents associated with a key, returning them or None."""
        ...


class PHasher(Protocol):
    """Operations related to hash."""

    def hash(self, bb: bytes) -> str:
        """Calculate the hash for the given bytes."""
        ...
