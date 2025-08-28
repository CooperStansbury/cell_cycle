# DeepCycle Scripts

Utilities for running the
[DeepCycle](https://github.com/MCalebO/DeepCycle) model to estimate
cell-cycle position.

## Contents
- `run_deepcycle.sh` – Example SLURM submission script invoking `DeepCycle.py`
- `DeepCycle/` – Directory containing model weights and output files

## Usage
Edit the variables in `run_deepcycle.sh` to point to your data and submit
it with `sbatch`. GPU resources are recommended.
