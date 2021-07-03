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
    existing_snapshot: bool = False,
) -> Result:
    """Initializes Batfish Snapshot.

    Args:
        task (Task): Task.
        batfish_host (str, optional): Batfish Instance. Defaults to "localhost".
        snapshot_dir (str, optional): Directory of Configs. Defaults to None.
        snapshot_name (str, optional): Snapshot Name. Defaults to None.
        overwrite (str, optional): OverWrite Snapshot. Defaults to False.
        set_network (str, optional): Set new or existing Network. Defaults to None.
        set_snapshot (str, optional): Set existing snapshot. Defaults to None.
        get_issues (bool, optional): Get Parsing Issues. Defaults to False.
        existing_snapshot (bool, optional): Task Helper for operations. Defaults to False.

    Raises:
        FileNotFoundError: Unable to find local snapshot directory.

    Examples:
        batfish_init:
            bf_init = nornir.run(
            task=batfish_init,
            batfish_host=batfish_host,
            snapshot_dir=snapshot_dir,
            snapshot_name="xenomorph",
            set_network="PROMETHEUS",
            get_issues=True,
            overwrite=True,
        )
    Documentation:
        [Interacting With Batfish](https://batfish.readthedocs.io/en/latest/notebooks/interacting.html)

    Returns:
        Result: Nornir Aggregated Results
    """
    failed = False
    changed = False
    result = {}

    # if set_snapshot and any(snapshot_dir, snapshot_name):
    #     failed = True
    #     result = "Setting a snapshot doesn't require args: snapshot_dir & snapshot_name"

    # Add Returns
    bf_session.host = batfish_host
    # Need logic to ensure host is reachable.

    if existing_snapshot:
        if not all([set_snapshot, set_network]):
            failed = True
            result["msg"] = "Task set to existing snapshot, but did not provide 'set_snapshot' or 'set_network'."
        if all([set_snapshot, set_network]):
            result["network"] = bf_set_network(set_network)
            result["snapshot"] = bf_set_snapshot(set_snapshot)

    if not existing_snapshot:
        if not _check_path(snapshot_dir):
            failed = True
            raise FileNotFoundError(f"{snapshot_dir} not found.")

        if not failed:
            result["network"] = bf_set_network(set_network)
            result["init"] = bf_init_snapshot(snapshot_dir, name=snapshot_name, overwrite=overwrite)

            # Questions will always be loaded, as we can't do much without them.
            # They must be loaded to get access to bfq.initIssues
            load_questions()
            changed = True

    if get_issues:
        result["issues"] = bfq.initIssues().answer()  # pylint: disable=E1101

    return Result(host=task.host, result=result, failed=failed, changed=changed)
