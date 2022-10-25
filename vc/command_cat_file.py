#!/usr/bin/env python3

"""cat-file command."""
import argparse
import hashlib
import sys
from typing import List

from vc.prots import PCommandProcessor, PDB


class CatFileCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    key = "cat-file"

    def __init__(self, db: PDB):
        """Initialize object, preparing the parser."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-e", action="store_true")
        parser.add_argument("-s", action="store_true")
        parser.add_argument("-p", action="store_true")
        parser.add_argument("-t", action="store_true")
        parser.add_argument("hash", type=str)
        self.parser = parser
        self.db = db

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        r = self.parser.parse_args(args)

        hsh = r.hash
        ob = self.db.get(hsh)

        if r.type:
            return ob.type
