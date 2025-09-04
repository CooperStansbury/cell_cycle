#!/bin/bash
#SBATCH --job-name=umap
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

# ---------- user-adjustable variables ----------
INPUT_ADATA="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle/TrajNet_input.h5ad"
OUTPUT_DIR="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle/umap"

# TrajectoryNet parameters
EMBEDDING_NAME="umap"
MAX_DIM=10
NITER=10000
VECINT="1e-4"
WORKERS=16
BATCH_SIZE=5000

# Execution
PYTHON_BIN="python"          # or full path to python in your env
WORK_DIR="${SLURM_SUBMIT_DIR:-$PWD}"
RUN_ID="$(date +%Y%m%d_%H%M%S)_${SLURM_JOB_ID:-nojobid}"

# ---------- helpers ----------
print_var () { printf "%-22s = %s\n" "$1" "${2:-}"; }

# ---------- echo configuration ----------
echo "=== Job configuration ==="
print_var "JOB_NAME"            "${SLURM_JOB_NAME:-deepcycle}"
print_var "JOB_ID"              "${SLURM_JOB_ID:-N/A}"
print_var "ACCOUNT"             "indikar1"
print_var "PARTITION"           "${SLURM_JOB_PARTITION:-gpu}"
print_var "NODES"               "${SLURM_JOB_NUM_NODES:-1}"
print_var "NTASKS"              "${SLURM_NTASKS:-1}"
print_var "CPUS_PER_TASK"       "${SLURM_CPUS_PER_TASK:-16}"
print_var "MEM"                 "150G"
print_var "GPUS"                "1"
print_var "TIME"                "36:00:00"
echo

echo "=== Paths & parameters ==="
print_var "WORK_DIR"            "$WORK_DIR"
print_var "INPUT_ADATA"         "$INPUT_ADATA"
print_var "OUTPUT_DIR"          "$OUTPUT_DIR"
print_var "RUN_ID"              "$RUN_ID"
print_var "EMBEDDING_NAME"      "$EMBEDDING_NAME"
print_var "MAX_DIM"             "$MAX_DIM"
print_var "NITER"               "$NITER"
print_var "VECINT"              "$VECINT"
print_var "PYTHON_BIN"          "$PYTHON_BIN"
echo

# ---------- prepare output directory (reset/overwrite) ----------
echo "Resetting output directory..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
print_var "OUTPUT_DIR (fresh)"  "$OUTPUT_DIR"
echo

# ---------- run ----------
cd "$WORK_DIR"

echo "=== Training (TrajectoryNet.main) ==="
${PYTHON_BIN} -m TrajectoryNet.main \
    --dataset "$INPUT_ADATA" \
    --embedding_name "$EMBEDDING_NAME" \
    --max_dim "$MAX_DIM" \
    --niters "$NITER" \
    --gpu 0 \
    --num_workers "$WORKERS" \
    --batch_size "$BATCH_SIZE" \
    --vecint "$VECINT" \
    --save "$OUTPUT_DIR"
echo

echo "=== Evaluation (TrajectoryNet.eval) ==="
${PYTHON_BIN} -m TrajectoryNet.eval \
    --dataset "$INPUT_ADATA" \
    --embedding_name "$EMBEDDING_NAME" \
    --max_dim "$MAX_DIM" \
    --niters "$NITER" \
    --vecint "$VECINT" \
    --gpu 0 \
    --num_workers "$WORKERS" \
    --batch_size "$BATCH_SIZE" \
    --save "$OUTPUT_DIR"
echo

echo "Done: $(date)  Run ID: $RUN_ID"