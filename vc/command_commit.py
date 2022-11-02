"""'commit' command."""

import sys
import argparse

from typing import List

from vc.prots import PCommandProcessor, PIndex


class CommitCommand(PCommandProcessor):
    """Implementation of the 'commit' command."""

    key = "commit"
    index: PIndex

    def __init__(self, index: PIndex):
        """Initialize object, preparing the parser."""
        self.index = index

        parser = argparse.ArgumentParser()
        parser.add_argument("-m", required=True)
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        r = self.parser.parse_args(args)
        self.index.commit(r.m)
