# Velocyto Pipeline

Snakemake workflow that generates spliced and unspliced count matrices using [Velocyto](https://velocyto.org/). The pipeline merges BAM files, prepares barcodes, and runs `velocyto.py`.

## Contents
- `Snakefile` – main workflow definition.
- `config.yaml` – sample configuration.
- `prep_velocyto.py` – helper script to adjust BAM files.
- `slurm_submit.sh` – example SLURM submission script.
- `velocyto.yml` – Conda environment specification.

## Usage
Edit `config.yaml` to match your data and execute:

```bash
snakemake --use-conda --cores 32
```

Alternatively, submit `slurm_submit.sh` on a cluster scheduler.
