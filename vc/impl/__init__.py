from .db import DB
from .index import Index
from .repo import Repo
from ..api import PRepo

def create_repo(root: str) -> PRepo:
    db = DB(root)
    index = Index(db, root)
    return Repo(index, db, root)
