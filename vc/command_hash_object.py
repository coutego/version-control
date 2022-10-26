#!/usr/bin/env python3

"""hash-object command."""

import argparse
import sys
from typing import List

from vc.prots import PCommandProcessor, PObjectDB


class HashObjectCommand(PCommandProcessor):
    """Implementation of the hash-object command."""

    key = "hash-object"

    def __init__(self, db: PObjectDB):
        """Initialize object, preparing the parser."""
        parser = argparse.ArgumentParser(
            description="Calculate hash and, optionally, write objects to DB"
        )
        parser.add_argument("-w", action="store_true", help="Write object to DB")
        parser.add_argument(
            "--stdin", action="store_true", help="Read objecdt contents from stdin"
        )
        parser.add_argument(
            "file", type=str, nargs="?", help="name of the file to read from"
        )
        self.parser = parser
        self.db = db

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        r = self.parser.parse_args(args)

        fil = r.file

        if r.stdin:
            if r.file:
                self.parser.print_help(sys.stderr)
                return
            lines = sys.stdin.readlines()
            content = b""
            for line in lines:
                content = content + bytes(line, "UTF-8")
        else:
            if r.file is None:
                self.parser.print_help(sys.stderr)
                return
            with open(fil, "rb") as f:
                content = f.read()

        if r.w:
            print(self.db.put(content))
        else:
            print(self.db.calculate_key(content))
