#! /usr/bin/env python


from __future__ import annotations

import logging
import sys
from typing import Any

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1

"""

  Kubernetes-practice gcloud compute snapshots create snapshot-1 \
    --project=apt-gear-446423-v0 \
    --source-disk=my-vm-with-startup-script \
    --source-disk-zone=us-central1-b \
    --storage-location=us

➜  Kubernetes-practice gcloud compute snapshots list
NAME        DISK_SIZE_GB  SRC_DISK                                       STATUS
snapshot-1  10            us-central1-b/disks/my-vm-with-startup-script  READY

"""


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:

    result = operation.result(timeout=timeout)

    if operation.error_code:
        print(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
            file=sys.stderr,
            flush=True,
        )
        print(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        print(f"Warnings during {verbose_name}:\n",
              file=sys.stderr, flush=True)
        for warning in operation.warnings:
            print(f" - {warning.code}: {warning.message}",
                  file=sys.stderr, flush=True)

    return result


# Using compute_v1.diskclient() -> find the disk -> regional or zonal (do we assume it is zonal or regional??)
# Create a snapshot instance compute_v1.snapshot()
# Invoke snapshot client and insert snapshot

# after creating snapshot, should i be deleting them?


# 1. first find the disk is source project
# 2. create a snapshot object, link .sourcedisk the it with the disk
# 3. then use snapshotclient.insert the disk in

def create_snapshot(
    project_id: str,
    disk_name: str,
    snapshot_name: str,

    zone: str | None = None,
    region: str | None = None,
    location: str | None = None,
    disk_project_id: str | None = None,
) -> compute_v1.Snapshot:

    if zone is None and region is None:
        raise RuntimeError(
            "You need to specify `zone` or `region` for this function to work."
        )
    if zone is not None and region is not None:
        raise RuntimeError(
            "You can't set both `zone` and `region` parameters.")

    if disk_project_id is None:
        disk_project_id = project_id

   # get zonal disk
    if zone is not None:
        # disk client to query the disk client
        disk_client = compute_v1.DisksClient()
        # disk_client.get()
        disk = disk_client.get(project=disk_project_id,
                               zone=zone, disk=disk_name)
    else:
        # get regional disk
        regio_disk_client = compute_v1.RegionDisksClient()
        disk = regio_disk_client.get(
            project=disk_project_id, region=region, disk=disk_name
        )
    # construct snapshot resource
    snapshot = compute_v1.Snapshot()
    # attach src to disk
    snapshot.source_disk = disk.self_link
    snapshot.name = snapshot_name
    # default as US?
    if location:
        snapshot.storage_locations = [location]

    # compute_v1.SnapshotsClient()
    snapshot_client = compute_v1.SnapshotsClient()

    logging.debug(f"Creating Snapshot to project ${project_id}")
    operation = snapshot_client.insert(
        project=project_id, snapshot_resource=snapshot)
    wait_for_extended_operation(operation, "snapshot creation")
    return snapshot_client.get(project=project_id, snapshot=snapshot_name)


#  project_id: str,
#     disk_name: str,
#     snapshot_name: str,

#     zone: str | None = None,
#     region: str | None = None,
#     location: str | None = None,
#     disk_project_id: str | None = None,

class Snapshot:
    def __init__(self):
        pass


# create snapshot in another project - it works
create_snapshot("my-second-project-447013",  "my-vm-with-startup-script",
                "snapshot-2-copy-from-project-1", "us-central1-b", disk_project_id="apt-gear-446423-v0")
