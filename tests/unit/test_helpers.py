"""Helpers Unit Tests."""
import pytest
from nornir_batfish.plugins.tasks.helpers import _check_file_ext


def test_check_file():
    with pytest.raises(ValueError) as val_err:
        _check_file_ext("somebadpath.json", ".txt")
    assert str(val_err.value) == "somebadpath.json must end with '.txt'."
