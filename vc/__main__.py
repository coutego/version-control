#!/usr/bin/env python3

"""Entry point to the vc module."""

import sys
from typing import List

from vc.command_hash_object import HashObjectCommand
from vc.prots import PCommandProcessor


class MainCommandProcessor(PCommandProcessor):
    """Main CommandProcessor."""

    processors: List[PCommandProcessor] = []
    key = ""

    def __init__(self):
        """Constructor."""
        self.processors.append(HashObjectCommand())

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        cmd = args[1]
        iargs = args[2:]

        for p in self.processors:
            if p.key == cmd:
                return p.process_command(iargs)


if __name__ == "__main__":
    p = MainCommandProcessor()
    p.process_command(sys.argv)
