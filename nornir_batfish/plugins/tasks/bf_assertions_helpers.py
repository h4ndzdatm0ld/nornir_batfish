"""Nornir Batfish Built-In Assertion Helpers"""
from nornir.core.task import Result, Task
from pybatfish.client.asserts import assert_filter_has_no_unreachable_lines, assert_has_no_route, assert_has_route
from typing import Optional, Union
from pybatfish.question import bfq
from pybatfish.client.commands import bf_list_networks, bf_list_snapshots

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
    routes: Optional[dict] = None,
    expected_route: dict = None,
    node: str = None,
    vrf: str = None,
    soft: bool = False,
    state: str = None,
):

    failed = False
    changed = False
    result = {"route": {}}

    REQ_ARGS = all(expected_route, node, state)
    if not REQ_ARGS:
        failed = True
        result = {"msg", "Missing one of the following ARGS: 'expected_route', 'node', state'"}

    # If no routes are passed in, try to get routes of currently loaded snapshot.
    if not routes:
        routes = bfq.routes().answer().frame()

    if state == "present":
        result["assertion"] = assert_has_route(routes, expected_route, node, vrf, soft)

    return Result(host=task.host, result=result, failed=failed, changed=changed)
