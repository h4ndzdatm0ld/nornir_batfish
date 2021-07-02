"""Nornir Batfish Init."""
from nornir.core.task import Result, Task
from pybatfish.client.commands import (
    bf_init_snapshot,
    bf_set_network,
    bf_session,
    bf_set_snapshot,
)
from pybatfish.question import load_questions
from pybatfish.question import bfq
from nornir_batfish.plugins.tasks.helpers import _check_path


# pylint: disable=too-many-arguments
def batfish_init(
    task: Task,
    batfish_host: str = "localhost",
    snapshot_dir: str = None,
    snapshot_name: str = None,
    overwrite: str = True,
    set_network: str = None,
    set_snapshot: str = None,
    get_issues: bool = False,
) -> Result:
    """Initializes Batfish Snapshot.

    Args:
        task (Task): Task,
        batfish_host (str, optional): [description]. Defaults to "localhost".
        snapshot_dir (str, optional): [description]. Defaults to None.
        snapshot_name (str, optional): [description]. Defaults to None.
        overwrite (str, optional): [description]. Defaults to True.
        set_network (str, optional): [description]. Defaults to None.
        set_snapshot (str, optional): [description]. Defaults to None.
        get_issues (bool, optional): [description]. Defaults to False.

    Example:
        nornir.run(
        task=batfish_init,
        batfish_host=batfish_host,
        snapshot_dir=snapshot_dir,
        snapshot_name="PROMETHEUS",
        get_issues=True,
        )
    """
    failed = False
    changed = False
    result = {}

    # Add Returns
    bf_session.host = batfish_host
    # Need logic to ensure host is reachable.

    # If we are NOT re-using an old snapshot
    if not set_snapshot:
        if not _check_path(snapshot_dir):
            failed = True
            raise ValueError(f"{snapshot_dir} not found.")
        if not failed:  # Raising exception doesn't fail task.
            result["init"] = bf_init_snapshot(snapshot_dir, name=snapshot_name, overwrite=overwrite)

    if set_snapshot:
        result["snapshot"] = bf_set_snapshot(set_snapshot)

    # Questions will always be loaded, as we can't do much without them.
    # They must be loaded to get access to bfq.initIssues
    load_questions()
    if get_issues:
        result["issues"] = bfq.initIssues().answer()  # pylint: disable=E1101

    result["network"] = bf_set_network(set_network)
    changed = True
    return Result(host=task.host, result=result, failed=failed, changed=changed)
