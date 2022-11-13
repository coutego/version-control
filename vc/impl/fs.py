"""Utility functions for filesystem operations."""

import os
import os.path
from typing import Optional, List

VC_DIR = ".vc"


def find_vc_root_dir(startdir=os.curdir) -> Optional[str]:
    """Find the current repo root dir '.vc', if we are in a repo."""
    curr = startdir
    prev = None

    while True:
        if prev and os.path.realpath(curr) == os.path.realpath(prev):
            return None
        d = curr + "/" + VC_DIR
        if os.path.isdir(d):
            return os.path.realpath(d)  # Found it!
        prev = curr
        curr = prev + "/.."


def create_vc_root_dir(parent_dir=os.curdir) -> str:
    """Create a repo in the current dir (or parent_dir)."""
    d = os.path.realpath(parent_dir) + "/" + VC_DIR
    if os.path.exists(d):
        raise Exception(f"File '{d}' already exists.")
    os.mkdir(d)
    return d


def index_write(base_dir: str, contents: str) -> None:
    """Write the contents of the index file."""
    write_file(base_dir, "index", contents)


def index_read(base_dir: str) -> str:
    """Read the contents of the index file."""
    return read_file(base_dir, "index")


def head_write(base_dir: str, contents: str) -> None:
    """Write the contents of the HEAD file."""
    write_file(base_dir, "HEAD", contents)


def head_read(base_dir: str) -> str:
    """Read the contents of the HEAD file."""
    return read_file(base_dir, "HEAD")


def write_file(base_dir: str, file: str, contents: str) -> None:
    """Write to the file from the repo at base_dir, creating it if needed."""
    path = _create_path_if_needed(base_dir, file)
    with open(path, "w") as f:
        f.write(contents + "\n")


def read_file(base_dir: str, file: str) -> str:
    """Read the file from the repo at base_dir, creating it if needed."""
    path = _build_full_path(base_dir, file)
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read().rstrip()


def remove_file(base_dir: str, file_dir: str) -> None:
    """Remove the file or directory file_dir."""
    os.remove(base_dir + "/" + file_dir)


def rename_file(base_dir: str, file_dir1: str, file_dir2: str) -> None:
    """Rename the file or dir file_dir1 to file_dir2."""
    os.rename(base_dir + "/" + file_dir1, base_dir + "/" + file_dir2)


def exists_file(base_dir: str, file: str) -> bool:
    """Return True is the file exists in the repo."""
    return os.path.exists(base_dir + "/" + file)


def list_files(base_dir: str, rel_path: str) -> List[str]:
    """Return the list of files contained in the dir 'rel_path'."""
    full_path = base_dir + "/" + rel_path
    if not os.path.isdir(full_path):
        raise FileNotFoundError(f"'{full_path}' is not a directory")
    files = os.listdir(full_path)
    return [f for f in files if os.path.isfile(full_path + "/" + f)]


def _create_path_if_needed(base_dir: str, file: str) -> str:
    """Creathe the dires for the given file path, if they don't already exist"""
    path = _build_full_path(base_dir, file)
    dir = "/".join(path.split("/")[:-1])
    if dir and not dir.strip() == "":
        if os.path.exists(dir) and not os.path.isdir(dir):
            raise FileExistsError(f"Internal error: dir '{dir}' exists but it's a file")
        elif not os.path.exists(dir):
            os.makedirs(dir)
    if not os.path.exists(path):
        with open(path, "w"):
            pass  # Force create file
    return path


def _build_full_path(base_dir: str, file: str) -> str:
    root = find_vc_root_dir(base_dir)
    if root is None or root.strip() == "":
        raise FileNotFoundError("Not in a repo")
    return root + "/" + file
