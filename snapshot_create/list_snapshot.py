#! /usr/bin/env python


# from google.cloud import compute_v1
import logging
from google.auth import default
from googleapiclient.discovery import build
import pprint as pp
# make sure to set your account as gcloud default auth login


def list_snapshots(proj: str, filter: str):
    """return the most recently created snapshots"""
    service = build('compute', 'v1', cache_discovery=False)
    request = service.snapshots().list(project=proj, filter=filter)
    page = request.execute()
    if len(page['items'] == 0):
        logging.warning(f"No snapshot with in {proj} with filter {filter}")
        return
    sorted_snapshots = sorted(
        page['items'], key=lambda x: x["creationTimestamp"], reverse=True)
    return sorted_snapshots[-1]


if __name__ == "__main__":

    # Reference gcloud command
    # gcloud compute snapshots list --project apt-gear-446423-v0 --filter "name=snapshot-2"
    list_snapshots("apt-gear-446423-v0", "name=snapshot-2")
