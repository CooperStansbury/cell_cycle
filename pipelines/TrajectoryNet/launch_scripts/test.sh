#!/bin/bash
set -euo pipefail

BASE_DIR="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/integrated_anndata/cell_cycle"
OUTPUT_DIR="${BASE_DIR}/test"
NPZ_FILE="${BASE_DIR}/input_umap2.npz"
EMBEDDING_NAME="umap"
OUT_RUN="$OUTPUT_DIR"

# safe clean: only if OUTPUT_DIR is inside BASE_DIR
abs_base="$(readlink -f "$BASE_DIR")"
abs_out="$(readlink -f "$OUTPUT_DIR")"
[[ -n "$abs_out" && "$abs_out" == "$abs_base"/* ]] || { echo "Refusing to delete: $abs_out"; exit 1; }
rm -rf --one-file-system -- "$abs_out"; mkdir -p "$abs_out"

PARAMS_FILE="params.train"

# Parse: strip inline comments, split into tokens, build array
TRAIN_ARGS=()
while IFS= read -r line; do
  line="${line%%#*}"              # drop inline comments
  for tok in $line; do            # split on whitespace
    [[ -n "$tok" ]] && TRAIN_ARGS+=("$tok")
  done
done < "$PARAMS_FILE"

# Debug/record
echo "[TRAIN ARGS]"; printf '  %q' "${TRAIN_ARGS[@]}"; echo
mkdir -p "$OUT_RUN"
cp -v "$PARAMS_FILE" "$OUT_RUN/"
printf '%s\n' "${TRAIN_ARGS[@]}" > "$OUT_RUN/effective_train_args.tokens"

# Use them
python -m TrajectoryNet.main \
  --dataset "$NPZ_FILE" --embedding_name "$EMBEDDING_NAME" \
  --save "$OUT_RUN" \
  "${TRAIN_ARGS[@]}"

python -m TrajectoryNet.eval \
  --dataset "$NPZ_FILE" --embedding_name "$EMBEDDING_NAME" \
  --save "$OUT_RUN" \
  "${TRAIN_ARGS[@]}"

# report contents
echo
echo "[Artifacts in $OUT_RUN]"
if command -v tree >/dev/null 2>&1; then
  tree -ah "$OUT_RUN"
else
  ls -lahR "$OUT_RUN"
fi