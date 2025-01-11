#! /usr/bin/env python


# from google.cloud import compute_v1
from google.auth import default
from googleapiclient.discovery import build
import pprint as pp
# make sure to set your account as gcloud default auth login

credentials, project = default()

#modify helo

#useful documentation - https://cloud.google.com/compute/docs/samples/compute-snapshot-create?hl=en#compute_snapshot_create-python

def list_snapshots(proj:str , filter:str):
    # client=compute_v1.SnapshotsClient()
    # #why do i need to specify project??
    # request = compute_v1.ListSnapshotsRequest(project=proj, filter=filter)
    # page = client.list(request=request)
    service = build('compute', 'v1', credentials = credentials)
    request = service.snapshots().list(project=proj, filter=filter)
    page = request.execute()
    print(page['items'])
    for snapshot in page['items']:
        res = [snapshot['name'], str(snapshot['diskSizeGb']), 
              snapshot['creationTimestamp'], snapshot['sourceDisk'].split("/")[-1]]
        pp.pprint(res)
        
   
        
    # print(type(request)) # <class 'google.cloud.compute_v1.types.compute.ListSnapshotsRequest'>
    
    
# list_snapshots("apt-gear-446423-v0", "name=snapshot-1")

def create_snapshot():
     pass
 
#gcloud compute snapshots list --project apt-gear-446423-v0 --filter "name=snapshot-2"


# gcloud compute snapshots list --project apt-gear-446423-v0 --filter "name=snapshot-2 OR disk_size_gb=10"

list_snapshots("apt-gear-446423-v0","name=snapshot-2")