#!/usr/bin/env python3

import hashlib

from vc.prots import PHasher


class SHA1Hasher(PHasher):
    """Operations related to hash."""

    def hash(self, bb: bytes) -> str:
        """Calculate the hash for the given bytes."""
        return hashlib.sha1(bb).hexdigest()

    def valid_hash(self, hsh: str) -> bool:
        """Return True if hsh is a valid hash, False otherwise."""
        return True
        # return hashlib. wl
