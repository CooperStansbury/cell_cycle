# Cell‑Cycle Pipeline Runner

`pipeline_runner.py` wraps the [Epi2me Labs `wf-single-cell`](https://github.com/epi2me-labs/wf-single-cell) Nextflow pipeline using a YAML configuration file. It prepares the environment, manages output directories, and constructs the pipeline command from user‑provided parameters.

## Requirements

- Python ≥3.7
- Nextflow
- Singularity or compatible container runtime
- Conda (for `environment.yaml`)

## Setup

Create and activate the Conda environment:

```bash
conda env create -f environment.yaml
conda activate epi2me-env
```

## Usage

Activate the environment and load required modules:

```bash
module load openjdk
module load singularity
```

Run the pipeline:

```bash
python pipeline_runner.py --config_path ./config.yaml --overwrite
```

## Reference Genome

Download a 10x Genomics reference (e.g., `refdata-gex-GRCh38-2020-A.tar.gz`) and extract it. Uncompress the GTF file:

```bash
gunzip refdata-gex-GRCh38-2020-A/genes/genes.gtf.gz
```

Specify the reference directory in `config.yaml`:

```bash
ref_genome_dir: /path/to/refdata-gex-GRCh38-2020-A
```

