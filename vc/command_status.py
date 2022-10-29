#!/usr/bin/env python3
"""'status' command."""

import sys
import argparse

from typing import List

from vc.prots import PCommandProcessor, PIndex, IndexStatus


class StatusCommand(PCommandProcessor):
    """Implementation of the 'status' command."""

    key = "status"
    index: PIndex

    def __init__(self, index: PIndex):
        """Initialize object, preparing the parser."""
        self.index = index

        parser = argparse.ArgumentParser()
        parser.add_argument("files")
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        # r = self.parser.parse_args(args) # FIXME: add option to specify files
        st: IndexStatus = self.index.status()

        print(
            (
                f"On branch {st.branch}\n"
                "Your branch is up to date with '<not implemented>'.\n"
                "Changes not staged for commit:\n"
                '  (use "vc add <file>..." to update what will be committed)\n'
                '  (use "vc restore <file>..." to discard changes in working directory)\n'
                f"        modified:   {', '.join(st.staged)}\n"  # FIXME: staged can be new, modified, ...?
                "\n"
                "Untracked files:\n"
                '  (use "vc add <file>..." to include in what will be committed)\n'
                f"       {','.join(st.not_tracked)}\n"
                'no changes added to commit (use "vc add" and/or "vc commit -a"\n'
            )
        )
