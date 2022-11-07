"""'init' command."""
from typing import List

from vc.prots import PCommandProcessor
from vc.impl.fs import create_vc_root_dir, find_vc_root_dir


class InitCommand(PCommandProcessor):
    """Implementation of the cat-file command."""

    key = "init"

    def process_command(self, args: List[str]) -> None:
        """Process the command with the given args."""
        if find_vc_root_dir():
            print("Already on a repository. Aborting")
        d = create_vc_root_dir()
        print(f"Initialized empty VC repository in {d}")
