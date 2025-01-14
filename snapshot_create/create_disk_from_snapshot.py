#! /usr/bin/env python


from __future__ import annotations

import sys
from typing import Any

from google.api_core.extended_operation import ExtendedOperation
from googleapiclient.discovery import build
from google.auth import default
import logging

# make sure you default login your crendential to run your program
# GCP will automatically pick up your default GCP crendential
# gcloud auth application-default login 

# configure scope to 
SCOPES = ['https://www.googleapis.com/auth/compute']


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
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {
                operation.error_message}",
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



    # project_id: "apt-gear-446423-v0"
    # target_zone: "us-central1-c",
    # disk_name: "create-disk-sample"
    # disk_type: "pd-ssd"
    # disk_size_gb: "10"
    # target_project_id: "my-second-project-447013"
    # src_snapshot_name: "my-vm-with-startup-script"

def create_disk_from_snapshot(
    src_project_id: str,
    target_zone: str,
    disk_name: str,
    disk_type: str,
    disk_size_gb: int,
    target_project_id: str,
    src_snapshot_name: str
) :
    """
    Creates a new disk in a project in given zone.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone: name of the zone in which you want to create the disk.
        disk_name: name of the disk you want to create.
        disk_type: the type of disk you want to create. This value uses the following format:
            "zones/{zone}/diskTypes/(pd-standard|pd-ssd|pd-balanced|pd-extreme)".
            For example: "zones/us-west3-b/diskTypes/pd-ssd"
        disk_size_gb: size of the new disk in gigabytes
        snapshot_link: a link to the snapshot you want to use as a source for the new disk.
            This value uses the following format: "projects/{project_name}/global/snapshots/{snapshot_name}"

    Returns:
        An unattached Disk instance.
    """
    # code using compute v1 service
    service = build('compute', 'v1', cache_discovery=False)
    
    # disk body
    disk_body = {
        "name": disk_name,
        "sizeGb": disk_size_gb,
        "zone": target_zone,
        "sourceSnapshot": f"projects/{src_project_id}/global/snapshots/{src_snapshot_name}",
        "type": disk_type,
    }
    
    # insert -> create disk

    request = service.disks().insert(project=target_project_id, zone=target_zone, body=disk_body)
    request.execute() # execute operation
    
    # same code using compute_v1 library 
    
    # disk_client = compute_v1.DisksClient()
    # disk = compute_v1.Disk()
    # disk.zone = zone
    # disk.size_gb = disk_size_gb
    # disk.source_snapshot = f"projects/{target_project_id}/global/snapshots/{src_snapshot_name}"
    # disk.type_ = disk_type
    # disk.name = disk_name
    # operation = disk_client.insert(project=project_id, zone=zone, disk_resource=disk)

    # wait_for_extended_operation(operation, "disk creation")
    
    # <class 'googleapiclient.http.HttpRequest'>
    print(type(service.disks().get(project=target_project_id, zone=target_zone, disk=disk_name)))

    return service.disks().get(project=target_project_id, zone=target_zone, disk=disk_name)

# create disk in snapshot "my-second-project-447013"
# by using snapshot in project  "apt-gear-446423-v0"


print(create_disk_from_snapshot(src_project_id="apt-gear-446423-v0",
                          target_zone="us-central1-c",
                          disk_name="dummy",
                          disk_type="projects/my-second-project-447013/zones/us-central1-c/diskTypes/pd-ssd",
                          disk_size_gb="10",
                          target_project_id="my-second-project-447013",
                          src_snapshot_name="snapshot-2"))