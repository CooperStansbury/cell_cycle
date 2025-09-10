#!/bin/bash
#SBATCH --job-name=npz_trajnet
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
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# ---------- strict mode ----------
set -euo pipefail

# ---- user settings ----
NPZ_FILE="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle/inputs/input_2comp_6time.npz"
OUTPUT_DIR="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle/test"
EMBEDDING_NAME="pca"
PYTHON_BIN="python"   # or an absolute path in your env

# ---- derived paths ----
WORK_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
RUN_ID="$(date +%Y%m%d_%H%M%S)_${SLURM_JOB_ID:-nojobid}"
OUT_RUN="${OUTPUT_DIR}/${RUN_ID}"

mkdir -p "$OUT_RUN"

printf "Job: %s (%s)\n" "${SLURM_JOB_NAME:-npz_trajnet}" "${SLURM_JOB_ID:-N/A}"
printf "Work dir: %s\nOut dir:  %s\n" "$WORK_DIR" "$OUT_RUN"
printf "NPZ: %s\nEmbedding: %s\n\n" "$NPZ_FILE" "$EMBEDDING_NAME"

# ---- run ----
echo "[Train] $(date)"
srun "${PYTHON_BIN}" -m TrajectoryNet.main \
  --dataset "$NPZ_FILE" \
  --embedding_name "$EMBEDDING_NAME" \
  --max_dim 100 \
  --save "$OUT_RUN"

echo "[Eval]  $(date)"
srun "${PYTHON_BIN}" -m TrajectoryNet.eval \
  --dataset "$NPZ_FILE" \
  --embedding_name "$EMBEDDING_NAME" \
  --max_dim 100 \
  --save "$OUT_RUN"

echo "Done $(date)  Run ID: $RUN_ID"