#!/usr/bin/env python3

"""hash-object command."""

import argparse
import hashlib
import sys
from typing import List

from vc.db import DB
from vc.prots import PCommandProcessor


class HashObjectCommand(PCommandProcessor):
    """Implementation of the hash-object command."""

    key = "hash-object"
    db = DB()

    def __init__(self):
        """Initialize object, preparing the parser."""
        parser = argparse.ArgumentParser()
        parser.add_argument("-w", action="store_true")
        parser.add_argument("--stdin", action="store_true")
        parser.add_argument("file", type=str)
        self.parser = parser

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        r = self.parser.parse_args(args)

        fil = r.file

        if r.stdin:
            lines = sys.stdin.readlines()
            content = b""
            for line in lines:
                content = content + bytes(line, "UTF-8")
        else:
            with open(fil, "rb") as f:
                content = f.read()

        hs = hashlib.sha1(content).hexdigest()
        if r.w:
            self.db.put(hs, content)
        print(hs)
