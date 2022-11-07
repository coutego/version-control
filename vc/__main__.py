#!/usr/bin/env python3

"""Entry point to the vc module."""

import sys
from typing import Dict, List
from vc.prots import PCommandProcessor
from vc.command_hash_object import HashObjectCommand
from vc.command_cat_file import CatFileCommand
from vc.command_init import InitCommand
from vc.command_add import AddCommand
from vc.command_commit import CommitCommand
from vc.command_status import StatusCommand
from vc.command_log import LogCommand
from vc.command_checkout import CheckoutCommand
from vc.impl.db import DB
from vc.impl.sha1hasher import SHA1Hasher
from vc.impl.index import Index
from vc.impl.repo import Repo


class MainCommandProcessor(PCommandProcessor):
    """Main CommandProcessor."""

    processors: Dict[str, PCommandProcessor] = {}
    key = ""

    def __init__(self):
        """Build the object tree."""
        db = DB(SHA1Hasher())
        index = Index(db)
        repo = Repo(index, db)
        procs = []
        procs.append(HashObjectCommand(db))
        procs.append(CatFileCommand(db))
        procs.append(InitCommand(db))
        procs.append(AddCommand(index))
        procs.append(CommitCommand(index))
        procs.append(StatusCommand(repo))
        procs.append(LogCommand(repo))
        procs.append(CheckoutCommand(repo))

        for p in procs:
            self.processors[p.key] = p

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        if len(args) < 2:
            print(
                f"Command required. Available commands: {', '.join(self.processors.keys())}",
                file=sys.stderr,
            )
            exit(-1)

        cmd = args[1]

        if cmd not in self.processors.keys():
            print(
                f"Command '{cmd}' not implemented. Available commands: {', '.join(self.processors.keys())}",
                file=sys.stderr,
            )
            exit(-1)

        self.processors[cmd].process_command((args[2:]))


if __name__ == "__main__":
    p = MainCommandProcessor()
    p.process_command(sys.argv)
