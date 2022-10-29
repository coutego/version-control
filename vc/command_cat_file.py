"""'cat-file' command."""

import argparse
import sys
from typing import List
from vc.prots import PCommandProcessor, PObjectDB


class CatFileCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    key = "cat-file"
    db: PObjectDB

    def __init__(self, db: PObjectDB):
        """Initialize object, preparing the parser."""
        parser = argparse.ArgumentParser(
            description="Consult object DB.", add_help=True
        )
        parser.add_argument(
            "-e", action="store_true", help="Check whether object exists"
        )
        parser.add_argument("-s", action="store_true", help="Print the object size")
        parser.add_argument("-p", action="store_true", help="Print the object contents")
        parser.add_argument("-t", action="store_true", help="Print the object type")
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
                print("Object doesn't exist", file=sys.stderr)  # FIXME Check spec
                return

        if ob is None:
            print(f"fatal: Not a valid object name {hsh}", file=sys.stderr)
            return

        if r.p:
            print("{}".format(ob.contents.decode("UTF-8")))
        elif r.t:
            print(ob.type.name)
        elif r.s:
            print(ob.size)
        else:
            self.parser.print_help(sys.stderr)
