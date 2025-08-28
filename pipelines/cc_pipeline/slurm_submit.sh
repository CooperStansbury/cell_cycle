#!/bin/bash

#SBATCH --job-name=scfib_epi2me 
#SBATCH --account=indikar1
#SBATCH --partition=largemem,standard
#SBATCH --mail-user=cstansbu@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --mem=150G
#SBATCH --time=36:00:00
#SBATCH --nodes=1                     
#SBATCH --ntasks=1                    
#SBATCH --cpus-per-task=32

module load openjdk
module load singularity
export PATH="/nfs/turbo/umms-indikar/Ram/tools:$PATH"

python pipeline_runner.py --overwrite 