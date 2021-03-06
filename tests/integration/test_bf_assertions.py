"""Nornir Batfish Assertions."""
from nornir_batfish.plugins.tasks.bf_init import batfish_init

# from nornir_utils.plugins.functions import print_result
from nornir_batfish.plugins.tasks.bf_assertions_helpers import bf_assert_filter_has_no_unreachable_lines


def test_setup(nornir, batfish_host, snapshot_dir):
    """Batfish Network & Snapshot Setup. This will ensure our snapshot is created."""
    init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir=snapshot_dir,
        snapshot_name="xenomorph",
        set_network="PROMETHEUS",
        overwrite=True,
    )
    assert not init["nostromo"][0].failed
    assert init["nostromo"][0].result["init"] == "xenomorph"
    assert init["nostromo"][0].result["session"]  # Store session details


def test_failed_unreachable_lines_fail(nornir, batfish_host, snapshot_dir):
    """Initialize an existing snapshot and test failure from missing params."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_snapshot="xenomorph",
        set_network="PROMETHEUS",
        existing_snapshot=True,
    )
    # Filter, snapshot and session must be provided, for Batfish to use to for tracing.
    failed_lines = nornir.run(
        task=bf_assert_filter_has_no_unreachable_lines,
        soft=False,
        snapshot="xenomorph",
        session=bf_init["nostromo"][0].result["session"],
    )
    assert failed_lines["nostromo"][0].failed
    assert (
        failed_lines["nostromo"][0].result["msg"] == "Missing one of the following ARGS: 'snapshot, session or filters'"
    )


def test_failed_unreachable_lines_success(nornir, batfish_host, snapshot_dir):
    """Initialize an existing snapshot and test success."""
    bf_init = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        set_snapshot="xenomorph",
        set_network="PROMETHEUS",
        existing_snapshot=True,
    )
    # Filter must be provided, for Batfish to use to for tracing.
    no_failure = nornir.run(
        task=bf_assert_filter_has_no_unreachable_lines,
        soft=False,
        filters="PL-EBGP-PE3-OUT",
        snapshot="xenomorph",
        session=bf_init["nostromo"][0].result["session"],
    )
    assert not no_failure["nostromo"][0].failed
