"""Nornir Batfish Built-In Assertion Helpers"""
from ipaddress import IPv4Network, IPv4Address, AddressValueError, NetmaskValueError
from nornir.core.task import Result, Task
from pybatfish.client.asserts import assert_filter_has_no_unreachable_lines
from pybatfish.question import bfq

# Docstrings Summary comes from Batfish Read the Docs documentation at
# https://batfish.readthedocs.io/en/latest/asserts.html


def bf_assert_filter_has_no_unreachable_lines(
    task: Task,
    filters: str = None,
    soft: bool = True,
    snapshot: str = None,
    session: str = None,
    df_format: str = "table",
) -> Result:
    """Check that a filter (e.g. an ACL) has no unreachable lines.
        A filter line is considered unreachable if it will never match a packet, e.g.,
        because its match condition is empty or covered completely by those of prior lines.

    Args:
        task (Task): [description]
        filters (str, optional): [description]. Defaults to None.
        soft (bool, optional): [description]. Defaults to True.
        snapshot (str, optional): [description]. Defaults to None.
        session (str, optional): [description]. Defaults to None. XXX
        df_format (str, optional): [description]. Defaults to None.

    Returns:
        Result: Nornir Result
    """
    failed = False
    changed = False
    result = {"assertion": {}}
    if not all([snapshot, session, filters]):
        failed = True
        result["msg"] = "Missing one of the following ARGS: 'snapshot, session or filters'"
    else:
        assertion = assert_filter_has_no_unreachable_lines(filters, soft, snapshot, session, df_format)
        if not assertion:
            failed = True
        result["assertion"] = assertion
    return Result(host=task.host, result=result, failed=failed, changed=changed)


def bf_assert_route(
    task: Task,
    expected_route: str = None,
    node: str = None,
    vrf: str = "default",
):
    failed = False
    changed = False
    result = {}

    # Convert this to a dict, and loop through it for missing args
    required = [expected_route]
    req_args = all(required)
    if not req_args:
        failed = True
        result = {"msg": "Missing required args."}

    if all(required):
        try:
            if expected_route.endswith("/32"):
                expected_route = expected_route.replace("/32", "")
                IPv4Address(expected_route)
                expected_route = f"{expected_route}/32"
            IPv4Network(expected_route)
        except (AddressValueError, NetmaskValueError) as val_err:
            failed = True
            result["msg"] = val_err

    if not failed:
        result = {"route": []}
        result["assertion"] = False

        # Take pandas df and create a list of dicts
        routes = bfq.routes().answer().frame().to_dict("records")

        # Filter on both Node & VRF.
        if all([node, vrf]):
            node = node.lower()
            routes = [route for route in routes if route["Node"] == node and route["VRF"] == vrf]
        # Override VRF(default) and only filter by VRF.
        if not node:
            routes = [route for route in routes if route["VRF"] == vrf]

        if not routes:
            failed = True
            result["msg"] = f"Unable to find routes for Node: {node} or VRF: {vrf}."

        if not failed:
            for route in routes:
                if expected_route != route["Network"]:
                    continue
                result["route"].append(route)
                result["assertion"] = True

        if not result["route"]:
            failed = True
            result["msg"] = f"Unable to find route: {expected_route}"

    return Result(host=task.host, result=result, failed=failed, changed=changed)
