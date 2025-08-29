# DeepCycle Scripts

Tools for running the [DeepCycle](https://github.com/MCalebO/DeepCycle) neural network to estimate cell‑cycle phase.

## Environment
Create the Conda environment:

```bash
mamba env create -f env.yaml --prefix [PATH]
```

## Contents
- `run_deepcycle.sh` – example SLURM submission invoking `DeepCycle.py`
- `DeepCycle/` – model weights, outputs, and diagnostic plots

## Usage
Edit variables in `run_deepcycle.sh` to point to your data and submit with `sbatch`. A GPU‑equipped node is recommended.
