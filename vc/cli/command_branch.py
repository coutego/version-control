"""'branch' command."""

import sys
import argparse
from typing import List
from ..api import PRepo, PCommandProcessor
from .util import require_initialized_repo


class BranchCommand(PCommandProcessor):
    """Implementation of the 'branch' command."""

    repo: PRepo

    def __init__(self, repo: PRepo):
        """Initialize the repo."""
        self.repo = repo
        parser = argparse.ArgumentParser()
        parser.add_argument("branch_name", nargs="?")
        parser.add_argument("branch2_name", nargs="?")
        parser.add_argument(
            "-d", "--delete", action="store_true", help="Delete a branch"
        )
        parser.add_argument(
            "-m", "--move", action="store_true", help="Move/rename a branch"
        )
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    @property
    def key(self):
        return "branch"

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return
        try:
            if not r.branch_name or len(r.branch_name) == 0:
                if r.delete or r.move:
                    print("branch name needed", sys.stderr)
                    exit(1)
                else:
                    branches, curr = self.repo.list_branches()
                    for b in branches:
                        selected = "*" if b == curr else " "
                        print(f"{selected} {b}")
                    exit(0)
            if r.delete:
                id = self.repo.delete_branch(r.branch_name)
                print(f"Deleted branch {r.branch_name} (was {id})")
            elif r.move:
                self.repo.rename_branch(r.branch_name, r.branch2_name)
            else:
                self.repo.create_branch(r.branch_name)
        except Exception as e:
            print(
                f"{e}", file=sys.stderr
            )  # FIXME: reproduce git style error messages for 'branch'
