#!/usr/bin/env python
import sys
import os
import pytest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from snapshot_create.create_snapshot import create_snapshot


'''
A few notes about mocking testing:
1. mock an item in the module where it is used, not where it is defined.
2. mock Decorator patch goes in reverse
3. Make sure to use Autospects to ensure that the mock object has the same interface as the original object.

WARNING: 
I am not an expert in mock testing, so please be careful with the code.
Just learning for fun :)
'''
def test_create_snapshot_no_zone_or_region():
    with pytest.raises(RuntimeError, match="You need to specify `zone` or `region` for this function to work."):
        create_snapshot(
            target_project_id="test-project",
            disk_name="test-disk",
            snapshot_name="test-snapshot"
        )


def test_create_snapshot_both_zone_and_region():
    with pytest.raises(RuntimeError, match="You can't set both `zone` and `region` parameters."):
        create_snapshot(
            target_project_id="test-project",
            disk_name="test-disk",
            snapshot_name="test-snapshot",
            zone="us-central1-a",
            region="us-central1"
        )

@mock.patch("snapshot_create.create_snapshot.compute_v1.Disk", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.Snapshot", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.DisksClient", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.SnapshotsClient", autospec=True)
@mock.patch("snapshot_create.create_snapshot.wait_for_snapshot_creation", autospec=True)
def test_create_snapshot_with_zone(mock_wait, mock_snapshots_client_class, mock_disks_client_class, mock_snapshot, mock_disk):
  
    mock_disk.self_link = "test-disk-link"
    mock_disks_client = mock_disks_client_class.return_value
    mock_disks_client.get.return_value = mock_disk

    mock_snapshots_client = mock_snapshots_client_class.return_value
    mock_snapshots_client.get.return_value = mock_snapshot

    result = create_snapshot(
        target_project_id="test-project",
        disk_name="test-disk",
        snapshot_name="test-snapshot",
        zone="us-central1-a"
    )

    mock_disks_client.get.assert_called_once_with(
        project="test-project", zone="us-central1-a", disk="test-disk"
    )
    mock_snapshots_client.insert.assert_called_once()
    mock_wait.assert_called_once_with("test-project", "test-snapshot")
    assert result == mock_snapshot

# Mocking all necessary classes and methods for region-based snapshot creation
@mock.patch("snapshot_create.create_snapshot.compute_v1.Disk", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.Snapshot", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.RegionDisksClient", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.SnapshotsClient", autospec=True)
@mock.patch("snapshot_create.create_snapshot.wait_for_snapshot_creation", autospec=True)
def test_create_snapshot_with_region(mock_wait, mock_snapshots_client_class, mock_region_disks_client_class, mock_snapshot, mock_disk):
    mock_disk.self_link = "test-disk-link"
    mock_region_disks_client = mock_region_disks_client_class.return_value
    mock_region_disks_client.get.return_value = mock_disk

    mock_snapshots_client = mock_snapshots_client_class.return_value
    mock_snapshots_client.get.return_value = mock_snapshot

    result = create_snapshot(
        target_project_id="test-project",
        disk_name="test-disk",
        snapshot_name="test-snapshot",
        region="us-central1"
    )

    mock_region_disks_client.get.assert_called_once_with(
        project="test-project", region="us-central1", disk="test-disk"
    )
    mock_snapshots_client.insert.assert_called_once()
    mock_wait.assert_called_once_with("test-project", "test-snapshot")
    assert result == mock_snapshot
    
    
'''
 This test with less control, because autospec=True on a parent module/class does not 
 recursively apply autospec to its children/attributes
 But with this example, we do less patching on objects and it is more clean
'''
@mock.patch("snapshot_create.create_snapshot.compute_v1", autospec=True)
@mock.patch("snapshot_create.create_snapshot.wait_for_snapshot_creation", autospec=True)
def test_create_snapshot_with_zone2(mock_wait,  mock_compute_v1):
    mock_disks = mock_compute_v1.Disk()
    mock_disks.self_link = "test-disk-link"
    
    mock_disks_client = mock_compute_v1.DisksClient()
    mock_disks_client.get.return_value = mock_disks
    
    mock_snapshot = mock_compute_v1.Snapshot()
    mock_snapshots_client = mock_compute_v1.SnapshotsClient()
    mock_snapshots_client.get.return_value = mock_snapshot

    result = create_snapshot(
        target_project_id="test-project",
        disk_name="test-disk",
        snapshot_name="test-snapshot",
        zone="us-central1-a"
    )

    mock_disks_client.get.assert_called_once_with(
        project="test-project", zone="us-central1-a", disk="test-disk"
    )
    mock_snapshots_client.insert.assert_called_once()
    mock_wait.assert_called_once_with("test-project", "test-snapshot")
    assert result == mock_snapshot



@mock.patch("snapshot_create.create_snapshot.compute_v1.DisksClient", autospec=True)
@mock.patch("snapshot_create.create_snapshot.compute_v1.SnapshotsClient", autospec=True)
@mock.patch("snapshot_create.create_snapshot.wait_for_snapshot_creation", autospec=True)
def test_create_snapshot_exception_handling(mock_wait, mock_snapshots_client_class, mock_disks_client_class):
    mock_disks_client = mock_disks_client_class.return_value
    mock_disks_client.get.side_effect = Exception("Disk retrieval failed")

    with pytest.raises(SystemExit):
        create_snapshot(
            target_project_id="test-project",
            disk_name="test-disk",
            snapshot_name="test-snapshot",
            zone="us-central1-a"
        )


