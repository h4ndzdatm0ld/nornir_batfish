"""Nornir Batfish Init Task Test."""
from nornir_batfish.plugins.tasks.batfish_init import batfish_init

from nornir_utils.plugins.functions import print_result


def test_batfish_init_no_issues(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init without getting Issues back from BF"""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir=snapshot_dir,
        snapshot_name="PROMETHEUS",
        set_network="xenomorph",
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
        set_network="xenomorph",
    )
    print_result(bf_init)
    assert bf_init["nostromo"][0].failed


def test_batfish_init_set_net(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init set pre-existing network."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_snapshot="PROMETHEUS",
        set_network="xenomorph",
    )
    assert not bf_init["nostromo"][0].failed
    assert bf_init["nostromo"][0].result == {"network": "xenomorph", "snapshot": "PROMETHEUS"}


def test_batfish_init_set_snap_missing_key(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init set pre-existing network. Missing snapshot_name."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_network="xenomorph",
    )
    assert bf_init["nostromo"][0].failed
