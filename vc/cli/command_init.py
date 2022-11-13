"""'init' command."""

import os
from typing import List
from ..impl.db import DB
from ..impl.index import Index
from ..impl.repo import Repo
from ..api import PCommandProcessor
from ..impl.fs import create_vc_root_dir, find_vc_root_dir


class InitCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    @property
    def key(self):
        return "init"

    def process_command(self, _: List[str]) -> None:
        """Process the command with the given args."""
        try:
            d = create_vc_root_dir()
        except:
            print(
                f"Reinitialized existing VC repository in {os.path.abspath(os.curdir)}"
            )
            # FIXME: do actually reinitialize it
            exit(1)
        db = DB(d)
        index = Index(db, d)
        repo = Repo(index, db, d)
        repo.init_repo()
        print(f"Initialized empty VC repository in {d}")
