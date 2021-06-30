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
    """
    # Add Returns
    # Add Example
    bf_res = {}
    bf_session.host = batfish_host

    # If we are not re-using an old snapshot
    if not set_snapshot:
        if not _check_path(snapshot_dir):
            raise NameError(f"{snapshot_dir} not found.")

        bf_res["init"] = bf_init_snapshot(snapshot_dir, name=snapshot_name, overwrite=overwrite)

        if bf_res["init"]:
            load_questions()

        if get_issues:
            bf_res["issues"] = bfq.initIssues().answer()  # pylint: disable=E1101

        return Result(host=task.host, result=bf_res)

    bf_res["network"] = bf_set_network(set_network)
    bf_res["snapshot"] = bf_set_snapshot(set_snapshot)

    if get_issues:
        bf_res["issues"] = bfq.initIssues().answer()  # pylint: disable=E1101

    return Result(host=task.host, result=bf_res)
