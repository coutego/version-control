"""'init' command."""

from typing import List

from .impl.db import DB
from .impl.index import Index
from .impl.repo import Repo
from .prots import PCommandProcessor
from .impl.fs import create_vc_root_dir, find_vc_root_dir


class InitCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    @property
    def key(self):
        return "init"

    def process_command(self, _: List[str]) -> None:
        """Process the command with the given args."""
        if find_vc_root_dir():
            print("Already on a repository. Aborting")
        d = create_vc_root_dir()
        db = DB(d)
        index = Index(db, d)
        repo = Repo(index, db, d)
        repo.init_repo()
        print(f"Initialized empty VC repository in {d}")
