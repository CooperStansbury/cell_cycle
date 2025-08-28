# Velocyto Pipeline

Snakemake workflow for generating spliced and unspliced count matrices using [Velocyto](https://velocyto.org/). The pipeline merges BAM files, prepares barcodes, and runs `velocyto.py`.

## Contents
- `Snakefile` – main workflow description
- `config.yaml` – configuration with sample information
- `prep_velocyto.py` – helper script to adjust BAM files
- `slurm_submit.sh` – example submission script for a SLURM cluster
- `velocyto.yml` – Conda environment for Velocyto

## Usage
Adjust paths in `config.yaml` and run:

```bash
snakemake --use-conda --cores 32
```

Alternatively, submit `slurm_submit.sh` on a cluster scheduler.
