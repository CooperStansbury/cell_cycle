import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time
import logging
from tqdm.auto import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import griddata
from scipy.stats import gaussian_kde
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore
import scipy.sparse as ss
from scipy.stats import pearsonr

import argparse
from pathlib import Path
import yaml

import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.profiler import profile, ProfilerActivity

import scanpy as sc
import tn_utils

from TrajectoryNet import dataset
import TrajectoryNet.main as tnet_train
import TrajectoryNet.eval as tnet_eval
from TrajectoryNet.lib import utils
from TrajectoryNet.train_misc import (
    count_nfe,
    count_total_time,
    create_regularization_fns,
    get_regularization,
    append_regularization_to_log,
    build_model_tabular,
)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="TrajectoryNet: load config and print.")
    ap.add_argument(
        "config",
        nargs="?",
        type=Path,
        default=Path("./config.yaml"),
        help="Path to config.yaml (default: ./config.yaml)",
    )
    # parse config and set args
    cli_args = ap.parse_args()
    cfg = yaml.safe_load(cli_args.config.read_text())
    print(f"# Loaded config: {cli_args.config.resolve()}")
    print(yaml.safe_dump(cfg, sort_keys=False, default_flow_style=False).rstrip())

    """ SET UP """
    print("="*50, ' SETTING UP MODEL ', "="*50)
    # parse args for TrajectoryNet
    args = tn_utils.dict_to_cli(cfg['args']) 
    
    # output directory
    utils.makedirs(args.save)

    # device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tn_utils.print_device_summary(device)

    # data
    args.data = dataset.SCData.factory(args.dataset, args)

    # timepoints based on scaling
    args.timepoints = args.data.get_unique_times()
    args.int_tps = (np.arange(int(np.max(args.timepoints)) + 1) + 1.0) * args.time_scale

    # regularization
    regularization_fns, regularization_coeffs = create_regularization_fns(args)

    # model
    model = build_model_tabular(args, args.data.get_shape()[0], regularization_fns).to(device)

    # logger
    logging.disable(logging.CRITICAL)
    logger = logging.getLogger()

    """ TRAINING """
    print("="*50, ' TRAINING ', "="*50)
    model, history = tn_utils.trainTrajectoryNet(
        device, 
        args, 
        model, 
        logger,
    )

    # save history
    outpath = f"{args.save}/training_history.csv"
    history.to_csv(outpath)
    print(f"Saved: {outpath}")

    outpath = f"{args.save}/training_loss.png"
    tn_utils.save_loss_plot(history, outpath)
    print(f"Saved: {outpath}")

    """ INTEGRATION """
    print("="*50, ' PREPARING OUTPUTS ', "="*50)

    # load anndata
    adata = sc.read_h5ad(cfg['adata'])
    outpath = f"{args.save}/adata.h5ad"
    adata.write(outpath)
    print(f"Saved: {outpath}")

    # save whitened data
    whitened_data = args.data.get_data()
    outpath = f"{args.save}/whitened_data.npy"
    np.save(outpath, whitened_data)
    
    for t in cfg['integration_args']['times']:
        print(f"Working trajectories with {t} timepoints...")
        trajectories = tn_utils.integrate_backwards(
            model=model, 
            args=args,
            ntimes=t,
            device=device,
        )

        # save embedding trajectories
        outpath = f"{args.save}/{args.embedding_name}_trajectories_{t}.npy"
        np.save(outpath, trajectories)
        print(f"Saved: {outpath}")

        # unwhiten the data
        trajectories, scaler = tn_utils.unwhiten_trajectories(
            trajectories, 
            args.dataset, 
            args.embedding_name,
        )

        # convert to gene expression space and store
        results = []
        for i in range(trajectories.shape[1]):
            traj = trajectories[:, i, :]       
            X_recon = tn_utils.pca_to_gene(adata, traj)
            X_recon['cell_idx'] = i
            X_recon = X_recon.reset_index()
            results.append(X_recon)

        # save results
        results = pd.concat(results)
        outpath = f"{args.save}/gene_trajectories_{t}.parquet"
        results.to_csv(outpath)
        print(f"Saved: {outpath}")
        break
        

        

    


    

    


