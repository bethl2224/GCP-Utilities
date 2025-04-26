# Prerequisite

1. Make sure to login with your gcloud default
   `zsh gcloud auth default login`
2. Install Docker Desktop or Rancher Desktop (for .devcontainer configuration setup)

# HOW TO RUN

## create_disk_from_snapshots.py

```zsh
usage: create_disk_from_snapshot.py [-h] -c CONFIG -p PROJECT_ID [-d] DRY-RUN

./create_disk_from_snapshot.py
-p target-project-123
-c create_disk_config.yaml
```

Disk is persistent storage attached to VM (Virtual Machine).

Here are two types of disk in GCP:

**SSD-Persistent-Disk**

- **Fast performance**, temporary storage that exists as long as the VM exists. **Data is lost if VM is stopped or deleted.**
  -High IOPS(Input/output oeprations per second)

**Balanced-Persistent-Disk**

- This is the **default option** and more **cost-effective**. Durable, high performance block storage that continue to exists even after VM is deleted.
- Offers **lower IOPS (Input/Output Operations Per Second)** and **throughput** compared to SSD Persistent Disks.

Note 🗒️: All persistent disk is network attached, and its lifecycle is separate from VM instance. For example, If the VM gets deleted, its disk still persist and can be attached to another VM If needed.

## create_snapshots.py

```zsh
Usage: create_snapshot.py [-h] -c CONFIG -p PROJECT_ID [-d] DRY-RUN

 ./create_snapshot.py -p target-project-123 -c create_snapshot_config.yaml
```

Snapshots are backups of persistent disks. They’re commonly used to recover, transfer, or make data accessible to other resources in your project. We can use snapshots to restore disk.

Note 🗒️: 

* Snapshots are build incrementally, which the current snapshot is built upon the previous snapshot layer to reconstruct the state of the disk.

* Deleting a snapshot only deletes data which is NOT needed by other snapshots

## Supplementary

Note in the `create_disk_from_snapshots.py` and `create_snapshot.py` script, we use two different ways to access GCP resources. You are either use [GCP Discovery API](https://cloud.google.com/docs/discovery) or [Compute_v1](https://cloud.google.com/compute/docs/reference/rest/v1) to invoke GCP client methods.

Example for using GCP Discovery API

```zsh
# Discoery compute v1 client
service = build('compute', 'v1', cache_discovery=False)
# Create disk
request = service.disks().insert(project=target_project_id,
                                    zone=target_zone, body=disk_body)
# Execute operation
request.execute()
```

Example for using Compute_v1 API

```zsh
snapshot = compute_v1.Snapshot()
# attach src to disk
snapshot.source_disk = disk.self_link
snapshot.name = snapshot_name
```

## Other Utilities
re
- [test_snapshot.py](./test_snapshot.py) - Contains unit tests for snapshot-related functionalities.
- [utils.py](./utils.py) - Provides utility functions to support snapshot operations.

# Useful Links

-[Snapshots Options](https://cloud.google.com/compute/docs/disks/snapshots)
