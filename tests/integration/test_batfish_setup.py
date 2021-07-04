"""Nornir Batfish Init Task Test."""
from nornir_batfish.plugins.tasks.bf_init import batfish_init

# from nornir_utils.plugins.functions import print_result


def test_batfish_init_no_issues(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init without getting Issues back from BF.
    Creating a new network, uploading configs and setting new snapshot."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir=snapshot_dir,
        snapshot_name="xenomorph",
        set_network="PROMETHEUS",
        get_issues=True,
        overwrite=True,
    )
    assert bf_init["nostromo"][0].result["issues"]
    assert not bf_init["nostromo"][0].failed


def test_batfish_init_fail_missing_set_network(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init missing keys - existing_snapshot=True.
    Missing "set_network "when re-using a snapshot."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_snapshot="xenomorph",
        existing_snapshot=True,
    )
    assert bf_init["nostromo"][0].failed
    assert "issues" not in bf_init["nostromo"][0].result.keys()


def test_batfish_init_fail_missing_set_snapshot(nornir, batfish_host):
    """Testing Batfish init missing keys - existing_snapshot=True.
    Missing "set_snapshot" when re-using a snapshot."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_network="PROMETHEUS",
        existing_snapshot=True,
        get_issues=True,
    )
    assert bf_init["nostromo"][0].failed


def test_batfish_init_invalid_snap_path(nornir, batfish_host):
    """Testing Batfish init task fails unable to find provided snapshot_dir."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir="I'm Lost",
        snapshot_name="xenomorph",
        set_network="PROMETHEUS",
    )
    assert bf_init["nostromo"][0].failed


def test_batfish_init_set_net(nornir, batfish_host):
    """Testing Batfish init set pre-existing network."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_snapshot="xenomorph",
        set_network="PROMETHEUS",
        existing_snapshot=True,
    )
    assert not bf_init["nostromo"][0].failed
    assert bf_init["nostromo"][0].result["network"] == "PROMETHEUS"
    assert bf_init["nostromo"][0].result["snapshot"] == "xenomorph"
    assert bf_init["nostromo"][0].result["session"]
    # Only assert session key/object exists, will be different each time this runs.


def test_batfish_init_set_net_invalid_snapshot(nornir, batfish_host):
    """Testing Batfish init set pre-existing network."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_snapshot="The Hive",
        set_network="PROMETHEUS",
        existing_snapshot=True,
    )
    assert bf_init["nostromo"][0]
    error = "No snapshot named The Hive was found in network PROMETHEUS: ['xenomorph']"
    assert error in bf_init["nostromo"][0].result


def test_batfish_init_set_snap_missing_key(nornir, batfish_host, snapshot_dir):
    """Testing Batfish init set pre-existing network. Missing snapshot_name."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_network="xenomorph",
    )
    assert bf_init["nostromo"][0].failed
