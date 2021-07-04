"""Nornir Batfish Built-In Assertion Helpers"""
from nornir.core.task import Result, Task
from pybatfish.client.asserts import assert_filter_has_no_unreachable_lines

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
