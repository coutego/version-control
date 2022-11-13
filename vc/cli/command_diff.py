"""'diff' command."""

import sys
import argparse
from typing import List
from ..api import PCommandProcessor, PRepo
from .util import require_initialized_repo


class DiffCommand(PCommandProcessor):
    """Implementation of the 'diff' command."""

    def __init__(self, repo: PRepo):
        """Initialize the repo."""
        self.repo = repo

        parser = argparse.ArgumentParser()
        parser.add_argument("files", nargs="*")
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    @property
    def key(self):
        return "diff"

    repo: PRepo

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        # FIXME: implement option to specify files
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return

        try:
            diff = self.repo.diff(r.files)
            for e in diff:
                print(e, end="")
        except FileNotFoundError:
            print(
                "fatal: not a vc repository (or any of the parent directories): .vc",
                file=sys.stderr,
            )
            exit(1)
