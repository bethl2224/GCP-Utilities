#! /usr/bin/env python


from google.cloud import compute_v1

# add shebang as it locate Python in the user's PATH


#modify helo

#useful documentation - https://cloud.google.com/compute/docs/samples/compute-snapshot-create?hl=en#compute_snapshot_create-python

def list_snapshots(proj:str , filter:str):
    client=compute_v1.SnapshotsClient()
    #why do i need to specify project??
    request = compute_v1.ListSnapshotsRequest(project=proj, filter=filter)
    page = client.list(request=request)
    for el in page.items:
        # print(el, type(el))
        pass
        
    # print(type(request)) # <class 'google.cloud.compute_v1.types.compute.ListSnapshotsRequest'>
    return page.items[0]
    
# list_snapshots("apt-gear-446423-v0", "name=snapshot-1")

def create_snapshot():
     pass
 
#gcloud compute snapshots list --project apt-gear-446423-v0 --filter "name=snapshot-2"


# gcloud compute snapshots list --project apt-gear-446423-v0 --filter "name=snapshot-2 OR disk_size_gb=10"

