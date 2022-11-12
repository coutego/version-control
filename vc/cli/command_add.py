"""'add' command."""

import argparse
from typing import List
from ..api import PCommandProcessor, PRepo
from ..util import require_initialized_repo


class AddCommand(PCommandProcessor):
    """Implementation of the add command."""

    repo: PRepo

    def __init__(self, repo: PRepo):
        """Initialize object, preparing the parser."""
        self.repo = repo
        parser = argparse.ArgumentParser()
        parser.add_argument("files", type=str, nargs="*")
        self.parser = parser

    @property
    def key(self):
        return "add"

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)

        for f in r.files:
            self.repo.index.stage_file(f)
