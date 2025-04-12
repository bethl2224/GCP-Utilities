#! /usr/bin/env python
from __future__ import annotations
import sys
from typing import Any
from google.api_core.extended_operation import ExtendedOperation
import argparse
from googleapiclient.discovery import build
from google.auth import default
from pprint import pprint as pp
import logging
import yaml


def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
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

# TODO: delete snapshot


def create_disk_from_snapshot(
    src_project_id: str,
    target_zone: str,
    disk_name: str,
    disk_type: str,
    disk_size_gb: int,
    target_project_id: str,
    src_snapshot_name: str,
):
    # code using compute v1 service
    try:
        service = build('compute', 'v1', cache_discovery=False)
        # disk body
        disk_body = {
            "name": disk_name,
            "sizeGb": disk_size_gb,
            "zone": target_zone,
            "sourceSnapshot": f"projects/{src_project_id}/global/snapshots/{src_snapshot_name}",
            "type": f"projects/{target_project_id}/zones/{target_zone}/diskTypes/{disk_type}",
        }
        logging.debug(
            f"Creating disk {disk_name} in {target_zone} from snapshot {src_snapshot_name} in project {src_project_id}"
        )
        # create disk
        request = service.disks().insert(project=target_project_id,
                                         zone=target_zone, body=disk_body)
        # execute operation
        request.execute()
        logging.debug(
            f"Disk {disk_name} created in {target_zone} from snapshot {src_snapshot_name} in project {src_project_id}"
        )
        return service.disks().get(project=target_project_id, zone=target_zone, disk=disk_name)

    except Exception as e:
        logging.error(f"Error creating disk: {e}")


def read_config(file_path: str) -> dict:
    # Read configuration from config.yaml
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Create a disk from a snapshot.")
    parser.add_argument("-p", "--project_id",
                        required=True, help="GCP Project ID")
    parser.add_argument("-d", "--dry_run", action="store_true",

                        help="Perform a dry run without creating the disk.")
    args = parser.parse_args()

    dry_run = args.dry_run

    project_id = args.project_id
    src_project_id = project_id

    # Example usage
    config = read_config("config.yaml")
    for disk in config["disks"]:
        target_zone = disk["target_zone"]
        disk_name = disk["disk_name"]
        disk_type = disk["disk_type"]
        disk_size_gb = disk["disk_size_gb"]
        target_project_id = disk["target_project_id"]
        src_snapshot_name = disk["src_snapshot_name"]
        if dry_run:
            print(
                f"Disk: {disk_name} created from snapshot {src_snapshot_name} in project {target_project_id}.")
        else:
            print(
                f"Disk: {disk_name} would be created from snapshot {src_snapshot_name} in project {target_project_id}.")
            create_disk_from_snapshot(
                src_project_id=src_project_id,
                target_zone=target_zone,
                disk_name=disk_name,
                disk_type=disk_type,
                disk_size_gb=disk_size_gb,
                target_project_id=target_project_id,
                src_snapshot_name=src_snapshot_name
            )
