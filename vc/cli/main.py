#!/usr/bin/env python3

"""Entry point to the vc module."""

import sys
from typing import Dict, List
from ..api import PCommandProcessor
from .command_hash_object import HashObjectCommand
from .command_cat_file import CatFileCommand
from .command_init import InitCommand
from .command_add import AddCommand
from .command_commit import CommitCommand
from .command_status import StatusCommand
from .command_log import LogCommand
from .command_checkout import CheckoutCommand
from .command_branch import BranchCommand
from .command_diff import DiffCommand
from ..impl.fs import find_vc_root_dir
from ..impl.db import DB
from ..impl.index import Index
from ..impl.repo import Repo


class MainCommandProcessor(PCommandProcessor):
    """Main CommandProcessor."""

    processors: Dict[str, PCommandProcessor] = {}

    def __init__(self):
        """Build the object tree."""
        root = find_vc_root_dir()
        procs = []
        procs.append(InitCommand())
        if root is not None:
            db = DB(root)
            index = Index(db, root)
            repo = Repo(index, db, root)
            procs.append(HashObjectCommand(repo))
            procs.append(CatFileCommand(repo))
            procs.append(AddCommand(repo))
            procs.append(CommitCommand(repo))
            procs.append(StatusCommand(repo))
            procs.append(LogCommand(repo))
            procs.append(CheckoutCommand(repo))
            procs.append(BranchCommand(repo))
            procs.append(DiffCommand(repo))

        for p in procs:
            self.processors[p.key] = p

    @property
    def key(self):
        return ""

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        if len(args) < 2:
            print(
                "Command required. Available commands:"
                + f" {', '.join(self.processors.keys())}",
                file=sys.stderr,
            )
            exit(-1)

        cmd = args[1]

        if cmd not in self.processors.keys():
            print(
                f"Command '{cmd}' not implemented. Available commands:"
                + f" {', '.join(self.processors.keys())}",
                file=sys.stderr,
            )
            exit(-1)

        self.processors[cmd].process_command((args[2:]))


def main(args: List[str]) -> None:
    p = MainCommandProcessor()
    p.process_command(args)
