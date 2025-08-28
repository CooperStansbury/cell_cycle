# DeepCycle Scripts

Utilities for running the [DeepCycle](https://github.com/MCalebO/DeepCycle) model to estimate cell-cycle position.

## Contents
- `run_deepcycle.sh` – example SLURM submission script invoking `DeepCycle.py`
- `DeepCycle/` – directory containing model weights and output files

## Usage
Edit variables in `run_deepcycle.sh` to point to your data and submit with `sbatch`. GPU resources are recommended.
