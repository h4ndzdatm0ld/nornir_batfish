"""Conftest for Nornir Batfish UnitTests."""
import os
import pytest
import docker
from nornir import InitNornir
from nornir.core.state import GlobalState


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
# If NORNIR_LOG set to True, the log won't be deleted in teardown.
nornir_logfile = os.environ.get("NORNIR_LOG", False)
global_data = GlobalState(dry_run=True)


@pytest.fixture
def snapshot_dir():
    return f"{DIR_PATH}/unit/test_data/mpls_sdn_era/"


@pytest.fixture
def batfish_host():
    """Evaluate wether running this locally or not to allow pipeline to execute
    properly as well as local testing with docker-compose. The batfish
    initializing takes a long time to time out and completely errors out if it
    can't reach the batfish host.

    Get all containers running in our environment.
    This is a try block, as docker service won't be installed in our pipeline
    runner and well resort to our exception and know were running this locally
    and connect to our batfish docker service by name.
    """
    try:
        client = docker.from_env()
        containers = client.containers.list()
        # Loop through all our container and extract the container names
        if [container.name for container in containers if container.name == "batfish"]:
            batfish_host = "localhost"
    except docker.errors.DockerException:
        batfish_host = "batfish"

    return batfish_host


@pytest.fixture(scope="session", autouse=True)
def nornir():
    """Initializes nornir"""
    nr_nr = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": f"{DIR_PATH}/inventory_data/hosts.yml",
                "group_file": f"{DIR_PATH}/inventory_data/groups.yml",
                "defaults_file": f"{DIR_PATH}/inventory_data/defaults.yml",
            },
        },
        logging={
            "log_file": f"{DIR_PATH}/unit/test_data/nornir_test.log",
            "level": "DEBUG",
        },
        dry_run=True,
    )
    nr_nr.data = global_data
    return nr_nr


# @pytest.fixture(scope="session", autouse=True)
# def teardown():
#     """Teardown the log file created by Nornir."""
#     if not nornir_logfile:
#         nornir_log = f"{DIR_PATH}/unit/test_data/nornir_test.log"
#         if os.path.exists(nornir_log):
#             os.remove(nornir_log)


@pytest.fixture(scope="function", autouse=True)
def reset_data():
    """Reset Data."""
    global_data.dry_run = True
    global_data.reset_failed_hosts()
