#!/bin/bash
#SBATCH --job-name=TrajectoryNet
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
INPUT_ADATA="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle/pseudotime.h5ad"
OUTPUT_DIR="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle/TrajectoryNet"

# TrajectoryNet parameters
EMBEDDING_NAME="umap"
MAX_DIM=10
NITER=10000
VECINT="1e-4"

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

# ---------- sanity checks ----------
if [[ ! -f "$INPUT_ADATA" ]]; then
  echo "ERROR: INPUT_ADATA not found: $INPUT_ADATA" >&2
  exit 1
fi

# ---------- prepare output directory (reset/overwrite) ----------
echo "Resetting output directory..."
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"
print_var "OUTPUT_DIR (fresh)"  "$OUTPUT_DIR"
echo

# ---------- environment info ----------
echo "=== Environment ==="
print_var "HOSTNAME"            "${HOSTNAME:-N/A}"
print_var "CUDA_VISIBLE_DEVICES" "${CUDA_VISIBLE_DEVICES:-auto}"
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || echo "nvidia-smi not available"
echo

# ---------- run ----------
cd "$WORK_DIR"

echo "=== Training (TrajectoryNet.main) ==="
set -x
srun --ntasks=${SLURM_NTASKS:-1} --cpus-per-task=${SLURM_CPUS_PER_TASK:-16} \
  ${PYTHON_BIN} -m TrajectoryNet.main \
    --dataset "$INPUT_ADATA" \
    --embedding_name "$EMBEDDING_NAME" \
    --max_dim "$MAX_DIM" \
    --niter "$NITER" \
    --vecint "$VECINT" \
    --save "$OUTPUT_DIR"
set +x
echo

echo "=== Evaluation (TrajectoryNet.eval) ==="
set -x
srun --ntasks=${SLURM_NTASKS:-1} --cpus-per-task=${SLURM_CPUS_PER_TASK:-16} \
  ${PYTHON_BIN} -m TrajectoryNet.eval \
    --dataset "$INPUT_ADATA" \
    --embedding_name "$EMBEDDING_NAME" \
    --max_dim "$MAX_DIM" \
    --niter "$NITER" \
    --vecint "$VECINT" \
    --save "$OUTPUT_DIR"
set +x
echo

echo "Done: $(date)  Run ID: $RUN_ID"