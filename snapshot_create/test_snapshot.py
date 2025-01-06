#! /usr/bin/env python

# from ..snapshot_create.create_snapshot import *
import pytest
import subprocess
from list_snapshot import *

# write single test expands to many other ones
# @pytest.mark.parametrize(
    # ('input_n', 'expected'),
    
    
    
# )

def test_list_snapshot():
    
    
    # input = "gcloud compute snapshots list --project apt-gear-446423-v0 --filter name=snapshot-2".split(' ')
   try:
        project = "apt-gear-446423-v0"
        filter = "name=snapshot-2"
        
        # maybe using shlex to part data???
        
        # or awk i think to test
        res = subprocess.check_output([
        "gcloud", "compute", "snapshots", "list",
        "--project", project,
        "--filter", filter
        ])
        shell_output = res.decode('utf-8')
        
        
        # use shlex.split to split name, disk_size_gb, src_disk, and status
        name = subprocess.check_output(["awk", "NR==2 {print $1}"], input = res).decode('utf-8').strip()
        snapshot = list_snapshots(project, filter)
        assert snapshot.name  == name
        
        # snapshot.source_disk #
        # snapshot.status
    
    # query second row, first column info
    #  gcloud compute snapshots list --project apt-gear-446423-v0 --filter "name=snapshot-2" | awk 'NR==2 {print $1}'
    
        
   except subprocess.CalledProcessError as e:
       print(f"Command failed with exit code {e.returncode}")
       
       

    
    
# test_list_snapshot()
