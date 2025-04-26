#! /usr/bin/env python
from __future__ import annotations
import argparse
import logging
import sys
from .utils import wait_for_snapshot_creation, read_config
from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1
from pprint import pprint as pp
# 1. first find the disk's source project
# 2. create a snapshot object, link .sourcedisk the it with the disk
# 3. then use snapshotclient.insert the disk in

# Set the logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)


def create_snapshot(
    target_project_id: str,
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

    # if not specified disk project id, then use the target project id
    if disk_project_id is None:
        disk_project_id = target_project_id
    try:
        # get zonal disk
        if zone is not None:
            # disk client to query the disk client
            disk_client = compute_v1.DisksClient()
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
        # Note:  default as US
        if location:
            snapshot.storage_locations = [location]

        snapshot_client = compute_v1.SnapshotsClient()
        logging.debug(f"Creating Snapshot to project {target_project_id}")
        # create snapshot
        snapshot_client.insert(
            project=target_project_id, snapshot_resource=snapshot)
        wait_for_snapshot_creation(target_project_id, snapshot_name)
        logging.debug(
            f"Snapshot {snapshot_name} created in {target_project_id} from disk {disk_name} in project {disk_project_id} ✅"
        )
        return snapshot_client.get(project=target_project_id, snapshot=snapshot_name)

    except Exception as e:
        logging.error(f"Error creating snapshot: {e}")
        sys.exit(1)
# TODO need a mechanism to ensure the program exit after snapshot resources is created properly


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

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(
        description="Create a disk from a snapshot.")
    parser.add_argument("-c", "--config", required=True,
                        help="Path to the config.yaml file")
    parser.add_argument("-p", "--project_id",
                        required=True, help="GCP Project ID")
    parser.add_argument("-d", "--dry_run", action="store_true",

                        help="Perform a dry run without creating the disk.")
    args = parser.parse_args()
    target_project_id = args.project_id
    configs = args.config
    dry_run = args.dry_run
    try:
        configs = read_config(configs)
        if dry_run:
            pp(configs)
        for snapshots in configs["snapshots"]:
            disk_project_id = snapshots["disk_project_id"]
            target_zone = snapshots["target_zone"]
            disk_name = snapshots["disk_name"]
            disk_type = snapshots["disk_type"]
            disk_size_gb = snapshots["disk_size_gb"]
            src_snapshot_name = snapshots["src_snapshot_name"]
            logging.debug(f"Creating Snapshot to project {target_project_id}")
            # create snapshot
            create_snapshot(target_project_id=target_project_id, disk_name=disk_name,
                            snapshot_name=src_snapshot_name, zone=target_zone, disk_project_id=disk_project_id)
    except Exception as e:
        logging.error(f"Error creating snapshot: {e}", exc_info=True)
        sys.exit(1)
