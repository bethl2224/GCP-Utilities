import os
import sys
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from snapshot_create.create_disk_from_snapshot import create_disk_from_snapshot
from snapshot_create.utils import *

@mock.patch("snapshot_create.create_disk_from_snapshot.wait_for_disk_creation", autospec=True)
@mock.patch("snapshot_create.create_disk_from_snapshot.read_config", autospec=True)
@mock.patch("snapshot_create.create_disk_from_snapshot.build", autospec=True)
def test_create_disk_from_snapshot(mock_build, mock_read_config, mock_wait_for_disk_creation):
    # Mock service and request objects
    mock_service = mock.MagicMock()
    mock_disks = mock.MagicMock()
    mock_insert_request = mock.MagicMock()
    mock_get_request = mock.MagicMock()

    # Set up the mock service
    mock_build.return_value = mock_service
    mock_service.disks.return_value = mock_disks
    
    #disk has both insert and get return value
    mock_disks.insert.return_value = mock_insert_request
    mock_disks.get.return_value = mock_get_request

    # Mock the insert request execution
    mock_insert_request.execute.return_value = {"status": "DONE"}

    # Mock the get request execution
    mock_get_request.return_value = {"name": "test-disk"}

    # Call the function under test
    result = create_disk_from_snapshot(
        src_project_id="test-src-project",
        target_zone="us-central1-a",
        disk_name="test-disk",
        disk_type="pd-standard",
        disk_size_gb=100,
        target_project_id="test-target-project",
        src_snapshot_name="test-snapshot"
    )
    print("RESULT", result)

    # Assertions
    mock_build.assert_called_once_with("compute", "v1", cache_discovery=False)
    mock_disks.insert.assert_called_once_with(
        project="test-target-project",
        zone="us-central1-a",
        body={
            "name": "test-disk",
            "sizeGb": 100,
            "zone": "us-central1-a",
            "sourceSnapshot": "projects/test-src-project/global/snapshots/test-snapshot",
            "type": "projects/test-target-project/zones/us-central1-a/diskTypes/pd-standard",
        },
    )
    mock_insert_request.execute.assert_called_once()  # Ensure execute is called on insert
    # see if get request get calls
    mock_disks.get.assert_called_once_with(
        project="test-target-project",
        zone="us-central1-a",
        disk="test-disk"
    )
    # mock_get_request.assert_called_once()  # Ensure execute is called on get
    assert result == mock_get_request