#!/bin/bash
#SBATCH --job-name=tnet_test
#SBATCH --account=indikar1
#SBATCH --partition=gpu,gpu_mig40,spgpu
#SBATCH --mail-user=cstansbu@umich.edu
#SBATCH --mail-type=END,FAIL
#SBATCH --mem=150G
#SBATCH --gpus=1
#SBATCH --time=36:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

python trainTrajectoryNet.py