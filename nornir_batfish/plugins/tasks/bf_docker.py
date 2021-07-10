"""Nornir Batfish Docker Runner."""
from nornir.core.task import Result, Task
import docker


def docker_manager(task: Task, docker_image: str = None, get_client: bool = False):
    """[summary]

    Args:
        task (Task): [description]
        docker_image (str, optional): [description]. Defaults to None.
        get_client (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    result = {"container": {}}
    failed = False
    changed = False

    # Add try block here and patch/test.
    client = docker.from_env()

    # Allow user access to full docker api-client operations
    if get_client:
        result["client"] = get_client
        changed = True
    if docker_image:
        try:
            container = client.containers.run(docker_image, detach=True)
            # Return container object in Result.result
            result["container"] = container
            changed = True
        except docker.errors.ImageNotFound as error:
            failed = True
            changed = False
            result["msg"] = f"{error} when attempting to run {docker_image}"
    return Result(host=task.host, result=result, failed=failed, changed=changed)
