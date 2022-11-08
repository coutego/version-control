"""DB related functionality, exposed through the PDB protocol."""

import os
import os.path
import glob
import zlib
import hashlib
from typing import Tuple, Union
from vc.prots import PObjectDB, DBObject, DBObjectType, DBObjectKey

VC_DIR = ".vc"


class DB(PObjectDB):
    """Default implementation of the PDB protocol."""

    root: str

    def __init__(self, root: str):
        """Configure the hasher to use in the DB."""
        if root and not os.path.isdir(root):
            raise FileNotFoundError(f"File path doesn't exist: '{root}'")
        self.root = root

    def calculate_key(self, content: Union[bytes, str]):
        """Calculate the key using the internal hasher."""
        self._check_repo()
        key, _ = _prepare_to_save(content)
        return key

    def put(
        self, content: Union[bytes, str], typ: DBObjectType = DBObjectType.BLOB
    ) -> DBObjectKey:
        """Associate the content bb to the key."""
        self._check_repo()
        key, bcontent = _prepare_to_save(content)
        lfname, ldirs, _ = self._filename_from_key(key)
        if os.path.exists(lfname):
            return key
        os.makedirs(ldirs, exist_ok=True)
        with open(lfname, "wb") as f:
            f.write(bcontent)
        return key

    def get(self, key: str) -> DBObject:
        """Get the contents associated with a key, returning them or None."""
        self._check_repo()
        if key is None or key.strip() == "":
            raise FileNotFoundError("Empty key")
        lfname, _, _ = self._filename_from_key(key)
        files = glob.glob(lfname + "*")
        if len(files) != 1:
            raise FileNotFoundError("Object not found")
        with open(files[0], "rb") as f:
            contents = f.read()
            contents = zlib.decompress(contents)
            idx_typ = contents.index(b" ")
            idx_len = contents.index(0)
            typ = contents[0:idx_typ].decode("UTF-8")
            length = contents[idx_typ:idx_len].decode("UTF-8")
            contents = contents[idx_len + 1 :]
            return DBObject(DBObjectType(typ), int(length), contents)

    def _filename_from_key(self, key: str) -> Tuple[str, str, str]:
        self._check_repo()
        root = self.root
        if not (isinstance(key, str)) or len(key) < 4:
            raise FileNotFoundError(f"Incorrect key format: '{key}'")
        d = key[0:2]
        fname = key[2:]
        ldirs = root + "/objects/" + d
        lfname = ldirs + "/" + fname
        return lfname, ldirs, fname

    def _check_repo(self) -> None:
        if self.root is None or not os.path.isdir(self.root):
            raise FileNotFoundError("Not in a repo")


def _prepare_to_save(
    content: Union[bytes, str], typ: DBObjectType = DBObjectType.BLOB
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
    key = hashlib.sha1(bcontent).hexdigest()
    return key, bcontent
