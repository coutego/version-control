"""'log' command."""

import sys
import argparse
from typing import List
from ..api import PCommandProcessor, PRepo
from .util import require_initialized_repo


class LogCommand(PCommandProcessor):
    """Implementation of the 'log' command."""

    repo: PRepo

    def __init__(self, repo: PRepo):
        self.repo = repo

        parser = argparse.ArgumentParser()
        parser.add_argument("--oneline", action="store_true")
        parser.add_argument("files", nargs="*")
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    @property
    def key(self):
        return "log"

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        # FIXME: implement option to specify files
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return

        log = self.repo.log()
        for le in log:
            print(f"{le.key[0:6]} {le.comment}")
