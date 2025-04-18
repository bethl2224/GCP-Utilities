#! /usr/bin/env python
from __future__ import annotations
import argparse
from googleapiclient.discovery import build

from utils import wait_for_disk_creation, read_config
import logging

#  By default, the logging module in Python logs
# messages with a severity level of WARNING or higher
logging.basicConfig(level=logging.DEBUG)


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
            f"Creating disk {disk_name} in {target_zone} from snapshot {src_snapshot_name} in project {src_project_id} 🟨 "
        )
        # create disk
        request = service.disks().insert(project=target_project_id,
                                         zone=target_zone, body=disk_body)
        # execute operation
        request.execute()
        logging.debug(
            f"Disk {disk_name} created in {target_zone} from snapshot {src_snapshot_name} in project {src_project_id} ✅"
        )
        return service.disks().get(project=target_project_id, zone=target_zone, disk=disk_name)

    except Exception as e:
        logging.error(f"Error creating disk: {e}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Create a disk from a snapshot.")
    parser.add_argument("-c", "--config", required=True,
                        help="Path to the config.yaml file")
    parser.add_argument("-p", "--project_id",
                        required=True, help="GCP Project ID")
    parser.add_argument("-d", "--dry_run", action="store_true",

                        help="Perform a dry run without creating the disk.")
    args = parser.parse_args()

    dry_run = args.dry_run

    project_id = args.project_id
    src_project_id = project_id
    configs = args.config

    # Example usage
    configs = read_config(configs)
    for disk in configs["disks"]:
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
            # delete_disk_if_exists(
            #     project_id=src_project_id,
            #     zone=target_zone,
            #     disk_name=disk_name
            # )
            create_disk_from_snapshot(
                src_project_id=src_project_id,
                target_zone=target_zone,
                disk_name=disk_name,
                disk_type=disk_type,
                disk_size_gb=disk_size_gb,
                target_project_id=target_project_id,
                src_snapshot_name=src_snapshot_name
            )

            # wait for disk creation
            wait_for_disk_creation(
                project_id=target_project_id,
                zone=target_zone,
                disk_name=disk_name,
                operation=None
            )
