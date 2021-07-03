"""Test Nornir Batfish Docker Runner - UnitTests."""
from nornir_batfish.plugins.tasks.bf_docker import docker_manager
from nornir_utils.plugins.functions import print_result
from docker.models.containers import ContainerCollection
from unittest.mock import patch
import docker


@patch.object(ContainerCollection, "run", side_effect=docker.errors.ImageNotFound("404 Client Error"))
@patch.object(docker, "from_env")
def test_docker_manager_success(docker_env, container_run, nornir):
    """Test Successfull run of a continer."""
    docker_mnngr = nornir.run(task=docker_manager, docker_image="batfish/batfish:latest", get_client=True)
    assert docker_mnngr["nostromo"][0].result["container"]
    assert docker_mnngr["nostromo"][0].result["client"]
    assert not docker_mnngr["nostromo"][0].failed


# This test works, but needs clean up on the side effect locations.
@patch.object(
    ContainerCollection,
    "run",
    side_effect=[docker.errors.ImageNotFound("404 Client Error"), docker.errors.ImageNotFound("404 Client Error")],
)
@patch.object(docker, "from_env")
def test_docker_manager_failure(doc, run, nornir):
    """Test failure of running container."""
    doc.side_effect = [docker.errors.ImageNotFound("404 Client Error")]
    docker_mnngr = nornir.run(task=docker_manager, docker_image="wrong/wrong", get_client=True)
    print_result(docker_mnngr)
    doc.assert_called_once()
    assert docker_mnngr["nostromo"][0].failed
    # assert docker_mnngr["nostromo"][0].result == {
    #     "client": True,
    #     "container": {},
    #     "msg": "404 Client Error when attempting to run wrong/wrong",
    # }
