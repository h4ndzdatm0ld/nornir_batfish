"""Nornir Batfish Assertions."""
from nornir_batfish.plugins.tasks.bf_init import batfish_init
import pytest

from nornir_utils.plugins.functions import print_result
from nornir_batfish.plugins.tasks.bf_assertions_helpers import (
    bf_assert_filter_has_no_unreachable_lines,
    bf_assert_route,
)
from ipaddress import AddressValueError, NetmaskValueError


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
    assert bf_init["nostromo"][0].result["snapshot"]
    assert bf_init["nostromo"][0].result["network"]
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


def test_setup2(nornir, batfish_host, networks):
    """Batfish Network & Snapshot Setup. Use other Networks."""
    bf_init2 = nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir=f"{networks}/example-filters/current",
        snapshot_name="failed-acl",
        set_network="batfish-networks",
        overwrite=True,
    )
    failed_assertion = nornir.run(
        task=bf_assert_filter_has_no_unreachable_lines,
        soft=False,
        snapshot="failed-acl",
        filters="/^acl/",
        session=bf_init2["nostromo"][0].result["session"],
    )
    assert failed_assertion["nostromo"][0].failed


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


def test_bf_assert_has_route_success_node(nornir):
    """Assert route exists in routing table of 'as65000_rr2'."""
    has_route = nornir.run(task=bf_assert_route, expected_route="10.0.0.14/31", node="as65000_rr2")
    assert has_route["nostromo"][0].result == {
        "assertion": True,
        "route": [
            {
                "Admin_Distance": 0,
                "Metric": 0,
                "Network": "10.0.0.14/31",
                "Next_Hop": None,
                "Next_Hop_IP": "AUTO/NONE(-1l)",
                "Next_Hop_Interface": "GigabitEthernet0/0/0/1",
                "Node": "as65000_rr2",
                "Protocol": "connected",
                "Tag": None,
                "VRF": "default",
            }
        ],
    }


@pytest.mark.parametrize(
    "network, error",
    [
        ("potayt0ez", AddressValueError("Expected 4 octets in 'potayt0ez'")),
        ("192.168.699.0/24", AddressValueError("Octet 699 (> 255) not permitted in '192.168.699.0'")),
        ("10.10.10.1/323", NetmaskValueError("'323' is not a valid netmask")),
    ],
)
def test_bf_assert_has_route_fails(nornir, network, error):
    """Assert failure from wrong network input to task."""
    has_route = nornir.run(task=bf_assert_route, expected_route=network)
    assert str(has_route["nostromo"][0].result["msg"]) == str(error)
    assert has_route["nostromo"][0].failed


def test_bf_assert_has_route_success(nornir):
    """Assert route exists in all routes."""
    has_route = nornir.run(task=bf_assert_route, expected_route="10.0.0.6/32")
    assert has_route["nostromo"][0].result == {
        "assertion": True,
        "route": [
            {
                "Admin_Distance": 0,
                "Metric": 0,
                "Network": "10.0.0.6/32",
                "Next_Hop": None,
                "Next_Hop_IP": "AUTO/NONE(-1l)",
                "Next_Hop_Interface": "GigabitEthernet0/0/0/3",
                "Node": "as65000_p1",
                "Protocol": "local",
                "Tag": None,
                "VRF": "default",
            }
        ],
    }


def test_bf_assert_route_failed_missing_args(nornir):
    """Assert failure of assert route missing args."""
    has_route = nornir.run(task=bf_assert_route)
    assert has_route["nostromo"].failed


def test_bf_assert_route_failed_bad_vrf_name(nornir):
    """Assert failure of assert route with bad-vrf filter."""
    has_route = nornir.run(task=bf_assert_route, expected_route="10.0.0.6/32", vrf="potatoe-vrf")
    assert has_route["nostromo"].failed
    print_result(has_route)
