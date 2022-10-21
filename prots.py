#!/usr/bin/env python3

"""Protocols for the different components of the VC."""

from typing import Protocol

# FIXME: move these to the files with implementations
import os
import os.path


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


class DB(PDB):
    """Default implementation of the IPDB protocol."""

    def put(self, key: str, bb: bytes) -> None:
        """Associate the content bb to the key."""
        root = self.__find_dir()
        d = key[0:2]  # FIXME Check length of key and raise an error if needed
        fname = key[2:]
        ldirs = root + "/objects/" + d
        lfname = ldirs + "/" + fname
        if os.path.exists(lfname):
            return
        os.makedirs(ldirs)
        with open(lfname, "wb") as f:
            print("Saving new file '{}".format(lfname))
            f.write(bb)

    def get(self, key: str) -> bytes:
        """Get the contents associated with a key, returning them or None."""
        pass

    def __find_dir(self) -> str:
        """Find the root dir of the VCS.

        The current implementation only searches in the current dir.
        """
        return "./.pasvc"


# FIXME: delete
db = DB()
db.put("abcd", bytes("jarl!", "UTF-8"))
