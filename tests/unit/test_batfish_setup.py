"""Nornir Batfish Init Task Test."""
from nornir_batfish.plugins.tasks.batfish_setup import batfish_init


# from nornir_utils.plugins.functions import print_result
# import pytest


def test_batfish_init_no_issues(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init without getting Issues back from BF"""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir=snapshot_dir,
        snapshot_name="PROMETHEUS",
        get_issues=True,
    )
    assert not bf_init["nostromo"][0].failed


def test_batfish_init_invalid_snap_path(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init task fails unable to find provided snapshot_dir."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir="I'm Lost",
        snapshot_name="PROMETHEUS",
    )
    assert bf_init["nostromo"][0].failed
