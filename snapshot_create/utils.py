#! /usr/bin/env python
import sys
from typing import Any
from google.cloud import compute_v1
from google.api_core.extended_operation import ExtendedOperation
import logging
import time


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
    # operation is long running operation
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


def delete_snapshot(project_id: str, snapshot_name: str) -> None:
    snapshot_client = compute_v1.SnapshotsClient()
    operation = snapshot_client.delete(
        project=project_id, snapshot=snapshot_name)
    wait_for_extended_operation(operation, "snapshot deletion")


def wait_for_disk_creation(project_id, zone, disk_name, operation):
    max_retries = 60  # Maximum retries (e.g., 60 seconds)
    retry_interval = 5  # Time to wait between retries (in seconds)
    disk_client = compute_v1.DisksClient()
    for attempt in range(max_retries):
        result = disk_client.get(project=project_id, zone=zone, disk=disk_name)
        if result.status == "READY":
            logging.info(f"Disk '{disk_name}' is ready.")
            return True
        else:
            logging.info(
                f"Waiting for disk '{disk_name}' to be ready... Attempt {attempt + 1}/{max_retries}")
            time.sleep(retry_interval)

    logging.error(
        f"Disk '{disk_name}' did not become ready within the timeout period.")
    return False


def delete_disk_if_exists(project_id: str, zone: str, disk_name: str) -> None:

    disk_client = compute_v1.DisksClient()
    # Check if the disk exists before attempting to delete
    try:
        res = disk_client.get(project=project_id, zone=zone, disk=disk_name)
        print(disk_client.list(
            project=project_id, zone=zone), file=sys.stderr, flush=True)
        if (res):
            operation = disk_client.delete(
                project=project_id, zone=zone, disk=disk_name)
            wait_for_extended_operation(operation, "disk deletion")
        else:
            logging.debug(
                f"Disk '{disk_name}' not found in zone '{zone}'. No action taken.")
    except Exception as e:
        print(f"Disk '{disk_name}' not found in zone '{zone}': {e}",
              file=sys.stderr, flush=True)
        return
