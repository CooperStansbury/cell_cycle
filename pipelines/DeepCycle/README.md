# DeepCycle Scripts

Tools for running the [DeepCycle](https://github.com/MCalebO/DeepCycle) neural network to estimate cell‑cycle phase.

## Environment
Create the Conda environment:

```bash
# 1) Create env (Python 3.11) at fixed path
mamba create -y -p /nfs/turbo/umms-indikar/Cooper/conda_envs/deep_cycle python=3.11 pip

# 2) Activate
conda activate /nfs/turbo/umms-indikar/Cooper/conda_envs/deep_cycle

# 3) Install TensorFlow 2.16 + matching TensorFlow Probability (no --user)
pip install "tensorflow==2.16.*" "tensorflow_probability==0.24.*" tf-keras tensorflow_datasets

# 4) Install analysis stack
pip install -U pandas scikit-learn matplotlib seaborn anndata

# 5) Sanity checks
which python
which pip
python -V
pip -V
python - <<'PY'
import tensorflow as tf, tensorflow_probability as tfp
print("TF:", tf.__version__)
print("TFP:", tfp.__version__)
PY
```

## Contents
- `run_deepcycle.sh` – example SLURM submission invoking `DeepCycle.py`
- `DeepCycle/` – model weights, outputs, and diagnostic plots

## Usage
Edit variables in `run_deepcycle.sh` to point to your data and submit with `sbatch`. A GPU‑equipped node is recommended. The script expects an input expression matrix and produces phase estimates and diagnostic plots under the `DeepCycle/` directory.

Training requires a GPU with sufficient memory to fit the model. The provided commands assume an HPC environment; adjust batch sizes and learning rates in `run_deepcycle.sh` to suit your hardware.

