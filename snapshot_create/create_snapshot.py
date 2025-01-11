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
    """
    Waits for the extended (long-running) operation to complete.

    If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
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
        print(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)
        for warning in operation.warnings:
            print(f" - {warning.code}: {warning.message}", file=sys.stderr, flush=True)

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
    
    
    """
    Create a snapshot of a disk.

    You need to pass `zone` or `region` parameter relevant to the disk you want to
    snapshot, but not both. Pass `zone` parameter for zonal disks and `region` for
    regional disks.

    Args:
        project_id: project ID or project number of the Cloud project you want
            to use to store the snapshot.
        disk_name: name of the disk you want to snapshot.
        snapshot_name: name of the snapshot to be created.
        zone: name of the zone in which is the disk you want to snapshot (for zonal disks).
        region: name of the region in which is the disk you want to snapshot (for regional disks).
        location: The Cloud Storage multi-region or the Cloud Storage region where you
            want to store your snapshot.
            You can specify only one storage location. Available locations:
            https://cloud.google.com/storage/docs/locations#available-locations
        disk_project_id: project ID or project number of the Cloud project that
            hosts the disk you want to snapshot. If not provided, will look for
            the disk in the `project_id` project.

    Returns:
        The new snapshot instance.
    """
    if zone is None and region is None:
        raise RuntimeError(
            "You need to specify `zone` or `region` for this function to work."
        )
    if zone is not None and region is not None:
        raise RuntimeError("You can't set both `zone` and `region` parameters.")

    if disk_project_id is None:
        disk_project_id = project_id

   # get zonal disk
    if zone is not None:
        # disk client to query the disk client
        disk_client = compute_v1.DisksClient()
        # disk_client.get()
        disk = disk_client.get(project=disk_project_id, zone=zone, disk=disk_name)
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
    operation = snapshot_client.insert(project=project_id, snapshot_resource=snapshot)

    wait_for_extended_operation(operation, "snapshot creation")

    return snapshot_client.get(project=project_id, snapshot=snapshot_name)


# specify whether want to pass in zonal disk image or regional disk image

# look at the disk project_id to create the snapshot, good!

# create_snapshot(project_id, disk_name, snapshot_name, zone, region, location, disk_project_id)
# create_snapshot("apt-gear-446423-v0", "my-vm-with-startup-script", "snapshot-2", "us-central1-b")


#create snapshot in another project - it works

create_snapshot("my-second-project-447013",  "my-vm-with-startup-script", "snapshot-2-copy-from-project-1", "us-central1-b", disk_project_id="apt-gear-446423-v0")

# note need to enable compute engine api to use


# able to create snapshot within same project or another project


# TODO: move project from one to another