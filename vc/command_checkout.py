#!/usr/bin/env python3

"""'checkout' command."""

import sys
import argparse

from typing import List

from vc.prots import PRepo, PCommandProcessor


class CheckoutCommand(PCommandProcessor):
    """Implementation of the 'checkout' command."""

    key = "checkout"
    repo: PRepo

    def __init__(self, repo: PRepo):
        """Initialize the repo."""
        self.repo = repo

        parser = argparse.ArgumentParser()
        parser.add_argument("commit_id", nargs=1)
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return

        try:
            message: str = self.repo.checkout(r.commit_id[0])
            _print_success(r.commit_id[0], message)
        except Exception as e:
            print(f"{e}", file=sys.stderr)


def _print_success(commit: str, message: str):
    print(
        f"Note: switching to '{commit}'.\n"
        "\n"
        "You are in 'detached HEAD' state. You can look around, make experimental\n"
        "changes and commit them, and you can discard any commits you make in this\n"
        "state without impacting any branches by switching back to a branch.\n"
        "\n"
        "If you want to create a new branch to retain commits you create, you may\n"
        "do so (now or later) by using -c with the switch command. Example:\n"
        "\n"
        "  vc switch -c <new-branch-name>\n"
        "\n"
        "Or undo this operation with:\n"
        "\n"
        "  vc switch -\n"
        "\n"
        "Turn off this advice by setting config variable advice.detachedHead to false\n"
        "\n"
        f"HEAD is now at {commit} {message}"
    )