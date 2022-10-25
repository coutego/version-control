#!/usr/bin/env python3

"""DB related functionality."""
import os
import os.path
import glob

from typing import Tuple, Optional

from vc.prots import PDB, DBObject

VC_DIR = ".vc"


class DB(PDB):
    """Default implementation of the IPDB protocol."""

    def put(self, key: str, bb: bytes) -> None:
        """Associate the content bb to the key."""
        lfname, ldirs, fname = self._filename_from_key(key)
        if os.path.exists(lfname):
            return
        os.makedirs(ldirs, exist_ok=True)
        with open(lfname, "wb") as f:
            print("Saving new file '{}".format(lfname))
            f.write(bb)

    def get(self, key: str) -> Optional[DBObject]:
        """Get the contents associated with a key, returning them or None."""
        lfname, ldirs, fname = self._filename_from_key(key)

        files = glob.glob(lfname + "*")

        if len(files) != 1:
            return None

        with open(files[0], "rb") as f:
            contents = f.read()
            return DBObject("blob", len(contents), contents)  # FIXME blob is hardcoded

    def init(self) -> None:
        """Create and initialize the DB."""
        if os.path.exists(VC_DIR):
            return
        os.mkdir(VC_DIR)
        os.mkdir(VC_DIR + "/objects")
        d = os.path.realpath(os.path.curdir) + "/" + VC_DIR
        print(f"Initialized empty VC repository in {d}")

    def __find_dir(self) -> str:
        """Find the root dir of the VCS.

        The current implementation only searches in the current dir.
        """
        return _find_vc_dir()

    def _filename_from_key(self, key: str) -> Tuple[str, str, str]:
        root = self.__find_dir()
        if root is None:
            raise FileNotFoundError("Not in a repo")
        if not (isinstance(key, str)) or len(key) < 4:
            raise Exception("Incorrect key")
        d = key[0:2]
        fname = key[2:]
        ldirs = root + "/objects/" + d
        lfname = ldirs + "/" + fname
        return (lfname, ldirs, fname)


def _find_vc_dir(startdir=os.curdir):
    curr = startdir
    prev = None

    while True:
        if prev and os.path.realpath(curr) == os.path.realpath(prev):
            return None
        d = curr + "/" + VC_DIR
        if os.path.isdir(d):
            return d
        prev = curr
        curr = prev + "/.."
