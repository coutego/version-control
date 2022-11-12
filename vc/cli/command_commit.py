"""'commit' command."""

import sys
import argparse
from typing import List
from ..api import PCommandProcessor, PRepo
from ..util import require_initialized_repo


class CommitCommand(PCommandProcessor):
    """Implementation of the 'commit' command."""

    repo: PRepo

    def __init__(self, repo: PRepo):
        """Initialize object, preparing the parser."""
        self.repo = repo

        parser = argparse.ArgumentParser()
        parser.add_argument("-m", required=True)
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    @property
    def key(self):
        return "commit"

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)
        self.repo.index.commit(r.m)
