# Pipelines

Workflow scripts for processing cell cycle data. Each subdirectory contains configuration files and helper scripts for a specific pipeline.

- `cc_pipeline/` – wrapper around Epi2me Labs' `wf-single-cell` Nextflow pipeline for initial processing of Nanopore reads.
- `TrajectoryNet/` – scripts and logs for running TrajectoryNet on processed count matrices.
- `DeepCycle/` – scripts and outputs for the DeepCycle neural network phase estimator.
- `velocyto_pipeline/` – Snakemake workflow for generating spliced and unspliced matrices with Velocyto.

See the README within each pipeline directory for prerequisites and execution instructions.
