"""Utilities."""
from pathlib import Path
import os.path
from typing import List


def _check_file_ext(file_name, ext):
    """Check file extension."""
    file_path = Path(file_name)

    if not file_name.endswith(f".{ext}"):
        raise ValueError(f"{file_path} must end with '{ext}'.")
    return file_path.exists()


def _check_path(path_dir):
    """Checks path is valid.

    Args:
        path_dir (str): Path string
    """
    return os.path.exists(path_dir)
