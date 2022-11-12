"""Utility functions."""

from ..api import PRepo


def require_initialized_repo(repo: PRepo):
    """Print an error message and file if we are not in a repo."""
    if not repo.initialized():
        print("fatal: not a vc repository (or any of the parent directories): .vc")
        exit(1)
