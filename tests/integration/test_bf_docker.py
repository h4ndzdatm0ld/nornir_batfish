"""Test Nornir Batfish Docker Runner."""
from nornir_batfish.plugins.tasks.bf_docker import docker_manager
import os

# from nornir_utils.plugins.functions import print_result

# Don't run these integration tests when testing inside a local docker container.
DOCKER_CONTAINER_ENV = os.environ.get("DOCKER_CONTAINER_ENV", False)


class TestDockerManager:
    """Test Docker Manager."""

    def setup_class(self):
        self.docker_env = DOCKER_CONTAINER_ENV

    def test_docker_manager_success(self, nornir):
        """Test Successfull integration of building and stopping a container."""
        if not self.docker_env:
            docker_mnngr = nornir.run(task=docker_manager, docker_image="batfish/batfish:latest", get_client=True)
            assert docker_mnngr["nostromo"][0].result["container"]
            assert str(docker_mnngr["nostromo"][0].result["container"].image) == "<Image: 'batfish/batfish:latest'>"
            assert docker_mnngr["nostromo"][0].result["container"].status == "created"
            assert docker_mnngr["nostromo"][0].result["client"]
            docker_mnngr["nostromo"][0].result["container"].stop()

    def test_docker_manager_failure(self, nornir):
        """Test invalid docker pull."""
        if not self.docker_env:
            docker_mnngr = nornir.run(task=docker_manager, docker_image="wrong/wrong", get_client=True)
            assert docker_mnngr["nostromo"][0].result == {
                "client": True,
                "container": {},
                "msg": "404 Client Error for "
                "http+docker://localhost/v1.41/images/create?tag=latest&fromImage=wrong%2Fwrong: "
                'Not Found ("pull access denied for wrong/wrong, repository does not '
                "exist or may require 'docker login': denied: requested access to the "
                'resource is denied") when attempting to run wrong/wrong',
            }
            assert docker_mnngr["nostromo"][0].failed
