import os
import os.path
from .db import DB
from .index import Index
from .repo import Repo
from ..api import PRepo


def create_repo(root: str, initialise: bool = False) -> PRepo:
    if not root.endswith("/.vc"):
        if root == "":
            raise FileNotFoundError("Incorrect repo dir")
        if root == ".":
            root = os.path.realpath(os.curdir)
        root = root + (".vc" if root[-1] == "/" else "/.vc")
        if not os.path.exists(root):
            if initialise:
                os.mkdir(root)
            else:
                raise FileNotFoundError("The repo does not exist")

    db = DB(root)
    index = Index(db, root)
    return Repo(index, db, root)
