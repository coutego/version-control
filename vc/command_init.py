#!/usr/bin/env python3

"""init command."""
from typing import List

from vc.prots import PCommandProcessor, PObjectDB


class InitCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    key = "init"
    db: PObjectDB

    def __init__(self, db: PObjectDB):
        """Initialize object, preparing the parser."""
        self.db = db

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        self.db.init()
