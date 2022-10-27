#!/usr/bin/env python3

"""add command."""

import argparse
from typing import List

from vc.prots import PCommandProcessor, PObjectDB, PIndex


class AddCommand(PCommandProcessor):
    """Implementation of the add command."""

    key = "add"
    db: PObjectDB

    def __init__(self, db: PObjectDB, index: PIndex):
        """Initialize object, preparing the parser."""
        self.db = db
        self.index = index

        parser = argparse.ArgumentParser()
        parser.add_argument("files", type=str, nargs="*")
        self.parser = parser

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        r = self.parser.parse_args(args)
        for f in r.files:
            self.index.stage_file(f)
