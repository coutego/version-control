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
from ..impl import create_repo


class MainCommandProcessor(PCommandProcessor):
    """Main CommandProcessor."""

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        procs: Dict[str, PCommandProcessor] = {}

        procs["hash-object"] = HashObjectCommand
        procs["cat-file"] = CatFileCommand
        procs["add"] = AddCommand
        procs["commit"] = CommitCommand
        procs["status"] = StatusCommand
        procs["log"] = LogCommand
        procs["checkout"] = CheckoutCommand
        procs["branch"] = BranchCommand
        procs["diff"] = DiffCommand
        procs["init"] = InitCommand

        if len(args) < 2:
            print(
                "Command required. Available commands:"
                + f" {', '.join(procs.keys())}",
                file=sys.stderr,
            )
            exit(-1)

        cmd = args[1]

        if cmd not in procs.keys():
            print(
                f"Command '{cmd}' not implemented. Available commands:"
                + f" {', '.join(procs.keys())}",
                file=sys.stderr,
            )
            exit(-1)

        command = procs[cmd]
        if hasattr(command, 'no_repo_needed') and command.no_repo_needed is True:
            command().process_command(args[2:])
            return
        root = find_vc_root_dir()
        if root is None:
            print("fatal: not a vc repository (or any of the parent directories): .vc", file=sys.stderr)
            exit(1)
        repo = create_repo(root)
        command(repo).process_command(args[2:])


def main(args: List[str]) -> None:
    """Execute the client."""
    p = MainCommandProcessor()
    p.process_command(args)
