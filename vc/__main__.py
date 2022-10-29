#!/usr/bin/env python3

"""Entry point to the vc module."""

import sys
from typing import List

from vc.prots import PCommandProcessor
from vc.command_hash_object import HashObjectCommand
from vc.command_cat_file import CatFileCommand
from vc.command_init import InitCommand
from vc.command_add import AddCommand
from vc.impl.db import DB
from vc.impl.sha1hasher import SHA1Hasher
from vc.impl.index import Index


class MainCommandProcessor(PCommandProcessor):
    """Main CommandProcessor."""

    processors: List[PCommandProcessor] = []
    key = ""

    def __init__(self):
        """Build the object tree."""
        db = DB(SHA1Hasher())
        index = Index(db)
        self.processors.append(HashObjectCommand(db))
        self.processors.append(CatFileCommand(db))
        self.processors.append(InitCommand(db))
        self.processors.append(AddCommand(index))

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        if len(args) < 2:
            commands = ""
            for p in self.processors:
                if len(commands) > 0:
                    commands = commands + ", "
                commands = commands + p.key
            print(
                "No command especified. Available commands: " + commands,
                file=sys.stderr,
            )
            return None

        iargs = args[2:]
        cmd = args[1]

        for p in self.processors:
            if p.key == cmd:
                return p.process_command(iargs)
        print(f"Internal error: {cmd} command not found", file=sys.stderr)


if __name__ == "__main__":
    p = MainCommandProcessor()
    p.process_command(sys.argv)
