"""Utilities."""
from pathlib import Path
import os.path


def _check_file(file_name):
    """Check file_name exists based on input."""
    file_path = Path(file_name)

    if not file_name.endswith(".xlsx"):
        raise ValueError(f"{file_path} must end with 'xlsx'.")
    return file_path.exists()


def _check_path(path_dir):
    """Checks path is valid.

    Args:
        path_dir (str): Path string
    """
    return os.path.exists(path_dir)
