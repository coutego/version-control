"""'status' command."""

import sys
import argparse
from typing import List
from ..api import PCommandProcessor, PRepo, RepoStatus, FileWithStatus
from .util import require_initialized_repo


class StatusCommand(PCommandProcessor):
    """Implementation of the 'status' command."""

    def __init__(self, repo: PRepo):
        """Initialize the repo."""
        self.repo = repo

        parser = argparse.ArgumentParser()
        parser.add_argument("files", nargs="*")
        try:
            self.parser = parser
        except Exception:
            parser.print_help(sys.stderr)

    @property
    def key(self):
        return "status"

    repo: PRepo

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        # FIXME: implement option to specify files
        require_initialized_repo(self.repo)
        r = self.parser.parse_args(args)
        if r.__contains__("h"):
            self.parser.print_help(sys.stderr)
            return

        try:
            st: RepoStatus = self.repo.status()
        except FileNotFoundError:
            print(
                "fatal: not a vc repository (or any of the parent directories): .vc",
                file=sys.stderr,
            )
            exit(1)

        msg = f"On branch {st.branch}\n"
        msg += _to_be_committed_2str(st.staged)
        msg += _not_staged_2str(st.not_staged)
        msg += _untracked_2str(st.not_tracked)

        print(msg, end="")


def _not_staged_2str(fs: List[FileWithStatus]) -> str:
    if len(fs) == 0:
        return ""
    ret = "Changes not staged for commit:\n"
    ret += '  (use "vc add <file>..." to update what will be committed)\n'
    ret += '  (use "vc restore <file>..." to discard changes in working directory)\n'
    ret += _files_with_status_2str(fs) + "\n"
    return ret


def _to_be_committed_2str(fs: List[FileWithStatus]) -> str:
    if len(fs) == 0:
        return ""
    ret = "Changes to be committed:\n"
    ret += '  (use "vc restore --staged <file>..." to unstage)\n'
    ret += _files_with_status_2str(fs) + "\n"
    return ret


def _untracked_2str(fs: List[FileWithStatus]) -> str:
    if len(fs) == 0:
        return ""
    ret = "Untracked files:\n"
    ret += '  (use "git add <file>..." to include in what will be committed)\n'
    ret += _files_with_status_2str(fs) + "\n"
    return ret


def _files_with_status_2str(fs: List[FileWithStatus]) -> str:
    ret = ""

    for f in fs:
        if f.status:
            ret += f"        {f.status.value}: {f.name}\n"
        else:
            ret += f"        {f.name}\n"

    return ret
