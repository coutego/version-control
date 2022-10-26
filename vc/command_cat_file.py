#!/usr/bin/env python3

"""cat-file command."""
import argparse
from typing import List

from vc.prots import PCommandProcessor, PObjectDB


class CatFileCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    key = "cat-file"
    db: PObjectDB

    def __init__(self, db: PObjectDB):
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

        if r.e:
            if ob:
                return
            else:
                print("Object doesn't exist")  # FIXME Check spec
                return

        if ob is None:
            print(f"fatal: Not a valid object name {hsh}")
            return

        if r.p:
            print("{}".format(ob.contents.decode("UTF-8")))
        elif r.t:
            print(ob.type.name)
        elif r.s:
            print(ob.size)
