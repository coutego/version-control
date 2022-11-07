"""DB related functionality, exposed through the PDB protocol."""

import os
import os.path
import glob
import zlib
from typing import Tuple, Optional, Union
from vc.prots import PObjectDB, DBObject, DBObjectType, DBObjectKey, PHasher

VC_DIR = ".vc"


class DB(PObjectDB):
    """Default implementation of the PDB protocol."""

    hasher: PHasher
    root: str

    def __init__(self, hasher: PHasher, root: str):
        """Configure the hasher to use in the DB."""
        self.hasher = hasher
        self.root = root

    def calculate_key(self, content: Union[bytes, str]):
        """Calculate the key using the internal hasher."""
        key, _ = _prepare_to_save(self.hasher, content)
        return key

    def put(
        self, content: Union[bytes, str], typ: DBObjectType = DBObjectType.BLOB
    ) -> DBObjectKey:
        """Associate the content bb to the key."""
        key, bcontent = _prepare_to_save(self.hasher, content)
        lfname, ldirs, _ = self._filename_from_key(key)
        if os.path.exists(lfname):
            return key
        os.makedirs(ldirs, exist_ok=True)
        with open(lfname, "wb") as f:
            f.write(bcontent)
        return key

    def get(self, key: str) -> Optional[DBObject]:
        """Get the contents associated with a key, returning them or None."""
        if key is None or key.strip() == "":
            return None
        lfname, _, _ = self._filename_from_key(key)
        files = glob.glob(lfname + "*")
        if len(files) != 1:
            return None
        with open(files[0], "rb") as f:
            contents = f.read()
            contents = zlib.decompress(contents)
            idx_typ = contents.index(b" ")
            idx_len = contents.index(0)
            typ = contents[0:idx_typ].decode("UTF-8")
            length = contents[idx_typ:idx_len].decode("UTF-8")
            contents = contents[idx_len + 1 :]
            return DBObject(DBObjectType(typ), int(length), contents)

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
            raise Exception(f"Incorrect key: '{key}'")
        d = key[0:2]
        fname = key[2:]
        ldirs = root + "/objects/" + d
        lfname = ldirs + "/" + fname
        return lfname, ldirs, fname


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


def _prepare_to_save(
    hasher: PHasher, content: Union[bytes, str], typ: DBObjectType = DBObjectType.BLOB
) -> Tuple[DBObjectKey, bytes]:
    # FIXME: this compression doesn't match git results: look into that
    bs: bytes
    if type(content) == bytes:
        bs = content
    elif type(content) == str:
        bs = content.encode("UTF-8")
    s = f"{typ.name.lower()} {len(bs)}\0"
    bcontent = s.encode("UTF-8") + bs
    bcontent = zlib.compress(bcontent)
    key = hasher.hash(bcontent)
    return key, bcontent
