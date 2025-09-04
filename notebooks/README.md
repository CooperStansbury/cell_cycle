# Notebooks

Exploratory Jupyter notebooks and helper utilities for cell‑cycle analysis. Each notebook is self‑contained and can be run independently once the required data files are available.

- `analyze_trajectories.ipynb` – evaluate learned trajectories from models such as TrajectoryNet.
- `buid_velocity_data.ipynb` – build RNA velocity input matrices.
- `cell_cycle_genes.ipynb` – visualize curated cell‑cycle gene sets.
- `compare_imputation.ipynb` – assess the effect of different imputation strategies.
- `clock_plots.ipynb` – display cell‑cycle position as a circular clock.
- `impute.ipynb` – impute missing expression values.
- `phase_alignment.ipynb` – align cells to known cell‑cycle phases.
- `prepare_TrajectoryNet.ipynb` – preprocess data and configuration for TrajectoryNet runs.
- `rank_study.ipynb` – explore gene ranking approaches for phase determination.
- `trajectory_inference.ipynb` – compare trajectory‑inference methods.
- `velocity_analysis.ipynb` – downstream analyses of RNA velocity results.

### Archived notebooks
The `archive/` directory stores older exploratory notebooks and utilities that are kept for reference:

- `archive/magic_NG.ipynb` – apply MAGIC for gene‑expression smoothing.
- `archive/magic_explore.ipynb` – explore MAGIC‑imputed data.
- `archive/utils.py` – helper functions formerly shared across notebooks.
