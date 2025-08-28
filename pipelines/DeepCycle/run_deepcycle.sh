#!/bin/bash

#SBATCH --job-name=deepcycle 
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

# Define input variables
DEEPCYCLE_SCRIPT="/home/cstansbu/git_repositories/DeepCycle/DeepCycle.py"
INPUT_ADATA="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/DeepCycle/deepcycle_input.h5ad"
GENE_LIST="/home/cstansbu/git_repositories/DeepCycle/go_annotation/GO_cell_cycle_annotation_human.txt"
BASE_GENE="TOP2A"
EXPRESSION_THRESHOLD="0.0001"
OUTPUT_ADATA="/nfs/turbo/umms-indikar/shared/projects/HSC/pipeline_outputs/DeepCycle/deepcycle_output.h5ad"

# Echo parameters
echo "Running DeepCycle with the following parameters:"
echo "  Script:                 $DEEPCYCLE_SCRIPT"
echo "  Input AnnData:          $INPUT_ADATA"
echo "  Gene list:              $GENE_LIST"
echo "  Base gene:              $BASE_GENE"
echo "  Expression threshold:   $EXPRESSION_THRESHOLD"
echo "  Output AnnData:         $OUTPUT_ADATA"
echo ""

# Run DeepCycle
python "$DEEPCYCLE_SCRIPT" \
    --input_adata "$INPUT_ADATA" \
    --gene_list "$GENE_LIST" \
    --base_gene "$BASE_GENE" \
    --expression_threshold "$EXPRESSION_THRESHOLD" \
    --gpu \
    --hotelling \
    --output_adata "$OUTPUT_ADATA"
