#!/bin/bash

module load openjdk
module load singularity
export PATH="/nfs/turbo/umms-indikar/Ram/tools:$PATH"

nextflow clean -f
python pipeline_runner.py --overwrite 
