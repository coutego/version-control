"""'checkout' command."""

import sys
import argparse
from typing import List
from ..api import PRepo, PCommandProcessor
from .util import require_initialized_repo


class CheckoutCommand(PCommandProcessor):
    """Implementation of the 'checkout' command."""

    repo: PRepo

    def __init__(self, repo: PRepo):
        """Initialize the repo."""
        self.repo = repo
        parser = argparse.ArgumentParser()
        parser.add_argument("commit_id", nargs=1)
        parser.add_argument("-b", "--branch", action="store_true")
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return

        try:
            message, detached = self.repo.checkout(r.commit_id[0], r.branch)
            _print_success(r.commit_id[0], detached, message)
        except Exception as e:
            print(f"{e}", file=sys.stderr)


def _print_success(commit: str, detached: bool, message: str):
    print(
        f"""Note: switching to '{commit}'.
{_maybe_detached(detached)}
If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  vc switch -c <new-branch-name>

Or undo this operation with:

  vc switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now at {commit} {message}"""
    )


def _maybe_detached(detached: bool) -> str:
    if detached:
        return """
You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.
        """
    else:
        return ""
