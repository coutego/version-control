#!/usr/bin/env python3
"""'log' command."""

import sys
import argparse

from typing import List

from vc.prots import PCommandProcessor, PRepo


class LogCommand(PCommandProcessor):
    """Implementation of the 'log' command."""

    key = "log"
    repo: PRepo

    def __init__(self, repo: PRepo):
        """Initialize the repo."""
        self.repo = repo

        parser = argparse.ArgumentParser()
        parser.add_argument("files", nargs="*")
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        # FIXME: implement option to specify files
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return

        log = self.repo.log()
        for le in log:
            print(le)
