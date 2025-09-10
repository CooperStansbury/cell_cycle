import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time
from pathlib import Path
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
from scipy.ndimage import gaussian_filter
from sklearn.neighbors import KNeighborsRegressor

import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.profiler import profile, ProfilerActivity

import scanpy as sc

from TrajectoryNet import dataset
from TrajectoryNet.parse import parser
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

def dict_to_cli(d):
    """
    Convert a config dict into TrajectoryNet CLI args and parse with defaults.

    Behavior
    --------
    - Non-bool values -> '--key value'
    - Bool True       -> '--key'
    - Bool False/None -> omitted
    The resulting list is parsed by TrajectoryNet's CLI parser to apply defaults.

    Parameters
    ----------
    d : dict
        Option names (without leading dashes) mapped to values.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with TrajectoryNet defaults applied.
    """
    from TrajectoryNet.parse import parser
    args = []
    for k, v in d.items():
        flag = f"--{k}"
        if isinstance(v, bool):
            if v:  # include flag only when True
                args.append(flag)
        else:
            args += [flag, str(v)]
    # parse dict with TrajectoryNet CLI parser for defaults
    args = parser.parse_args(args)
    return args


def print_device_summary(device: torch.device):
    """
    Print a concise PyTorch device summary.

    Parameters
    ----------
    device : torch.device
        Target device ("cpu" or "cuda").

    Notes
    -----
    - Always prints torch, CUDA, and cuDNN versions plus CUDA availability.
    - On CUDA: prints device index/count, name, compute capability, and free/total memory (GiB).
    - On CPU: prints the number of Torch CPU threads.
    """
    print(f"torch={torch.__version__} | cuda={torch.version.cuda} | "
          f"cudnn={torch.backends.cudnn.version()} | cuda_available={torch.cuda.is_available()}")

    if device.type == "cuda":
        idx = torch.cuda.current_device()
        name = torch.cuda.get_device_name(idx)
        cap = torch.cuda.get_device_capability(idx)
        n = torch.cuda.device_count()
        # memory
        to_gb = lambda b: b / (1024 ** 3)
        try:
            free, total = torch.cuda.mem_get_info(idx)  # PyTorch >=1.10
        except Exception:
            total = torch.cuda.get_device_properties(idx).total_memory
            free = total - torch.cuda.memory_allocated(idx)

        print(f"device=cuda:{idx} / {n} gpus | name={name}")
        print(f"capability={cap[0]}.{cap[1]} | mem_free={to_gb(free):.2f} GiB / mem_total={to_gb(total):.2f} GiB")
    else:
        print(f"device=cpu | threads={torch.get_num_threads()}")


def save_loss_plot(history, outpath):
    """
    Save a loss plot to `outpath`.

    Expects `history` with columns: 'iter', 'loss_val', 'loss_avg'.
    """
    p = Path(outpath)
    p.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(4, 3), dpi=200)
    sns.lineplot(data=history, x='iter', y='loss_val', c='k', alpha=0.75, lw=1, label='loss')
    sns.lineplot(data=history, x='iter', y='loss_avg', c='r', lw=1.5, label='mean')
    plt.xlabel("Iteration")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(p, bbox_inches="tight")
    plt.close()
    return p



def trainTrajectoryNet(device, args, model, logger):
    """
    Train TrajectoryNet with mixed precision, optional torch.compile, and minibatching.

    Parameters
    ----------
    device : torch.device
        Target device ("cuda" or "cpu").
    args : Namespace-like
        Must provide: lr, weight_decay, batch_size, niters, val_freq, save_freq,
        leaveout_timepoint, save, and a data handle with:
        - args.data.get_data() -> np.ndarray
        - args.data.get_times() -> np.ndarray
    model : torch.nn.Module
        TrajectoryNet model to train (optionally compiled with torch.compile).
    logger : logging.Logger
        Logger for eval/diagnostics.

    Behavior
    --------
    - Clears CUDA cache, enables TF32 fast paths on CUDA, sets cuDNN benchmark.
    - Tries torch.compile(mode="max-autotune"); falls back silently if unavailable.
    - Uses AdamW optimizer; mixed precision via torch.cuda.amp when on CUDA.
    - Samples on-device minibatches each iteration.
    - Adds regularization loss if `regularization_coeffs` is non-empty (expects
      `get_regularization(model, coeffs)` in scope).
    - Tracks running averages of time and loss; records NFE and total ODE time.
    - Periodically runs evaluation (`tnet_train.train_eval`) and saves checkpoints.

    Returns
    -------
    model : torch.nn.Module
        Trained (in-place updated) model.
    history : pandas.DataFrame
        Per-iteration metrics with columns: iter, time_val, time_avg,
        loss_val, loss_avg, nfe_total.

    Notes
    -----
    Expects `tnet_train.compute_loss`, `tnet_train.train_eval`, `count_nfe`,
    `count_total_time`, `utils.RunningAverageMeter`, and `utils.save_checkpoint`
    to be available in scope.
    """
    torch.cuda.empty_cache()      

    # regularization
    regularization_fns, regularization_coeffs = create_regularization_fns(args)

    # ---- fast math ----
    use_cuda = (device.type == "cuda")
    if use_cuda:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.set_float32_matmul_precision("high")  # enables TF32 fast paths
        torch.backends.cudnn.benchmark = True

    # compile (PyTorch 2.1+); comment out if not available
    try:
        model = torch.compile(model, mode="max-autotune")  # or "reduce-overhead"
        print(f"Compiled model.")
    except Exception:
        print(f"No model compilation.")
        pass

    # Optimizer 
    optimizer = optim.AdamW(
        model.parameters(),
        lr=args.lr, weight_decay=args.weight_decay,
        fused=use_cuda  # fused AdamW kernel on CUDA
    )

    # Meters
    time_meter = utils.RunningAverageMeter(0.93)
    loss_meter = utils.RunningAverageMeter(0.93)
    tt_meter   = utils.RunningAverageMeter(0.93)

    # one transfer to GPU; keep on device
    full_data = torch.from_numpy(
        args.data.get_data()[args.data.get_times() != args.leaveout_timepoint]
    ).to(device=device, dtype=torch.float32)
    full_data.requires_grad_(False)
    N = full_data.shape[0]

    best_loss = float("inf")
    end = time.time()
    history = []

    # optional: amp for speed if on CUDA
    scaler = torch.cuda.amp.GradScaler(enabled=use_cuda)

    for itr in tqdm(range(1, args.niters + 1), total=args.niters, desc="TrajectoryNet"):
        model.train()
        optimizer.zero_grad(set_to_none=True)

        # ---- key change: sample a minibatch on-GPU ----
        bsz = min(args.batch_size, N)  # safe if batch_size > N
        idx = torch.randint(N, (bsz,), device=full_data.device)
        batch = full_data.index_select(0, idx)

        # loss on batch
        with torch.cuda.amp.autocast(enabled=use_cuda):
            loss = tnet_train.compute_loss(device, args, model, None, logger, batch)

            if len(regularization_coeffs) > 0:
                reg_states = get_regularization(model, regularization_coeffs)
                reg_loss = sum(
                    reg_state * coeff
                    for reg_state, coeff in zip(reg_states, regularization_coeffs)
                    if coeff != 0
                )
                loss = loss + reg_loss

        loss_meter.update(loss.detach().item())

        # backward/step
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        # bookkeeping
        nfe_total = count_nfe(model)
        total_time = count_total_time(model)
        tt_meter.update(total_time)
        time_meter.update(time.time() - end)

        history.append({
            "iter": itr,
            "time_val": time_meter.val,      
            "time_avg": time_meter.avg,
            "loss_val": loss_meter.val,
            "loss_avg": loss_meter.avg,
            "nfe_total" : nfe_total,
        })

        # model eval
        if itr % args.val_freq == 0 or itr == args.niters:
            with torch.no_grad():
                tnet_train.train_eval(device, args, model, None, itr, best_loss, logger, full_data)

        if itr % args.save_freq == 0:
            utils.save_checkpoint({"state_dict": model.state_dict()}, args.save, epoch=itr)

        end = time.time()

    return model, pd.DataFrame(history)


def integrate_backwards(model, args, ntimes=100, device="cpu"):
    """
    Integrate a continuous normalizing flow (first chain) backward in time.

    Parameters
    ----------
    model : torch.nn.Module
        Model with `model.chain[0]` callable as `cnf(z, logp, integration_times=...)`.
    args : Namespace-like
        Must provide:
        - args.data.get_data() -> np.ndarray of shape (N, D)
        - args.data.get_times() -> np.ndarray of times (length N)
        - args.int_tps -> 1D array-like of monotonically increasing integration times
    ntimes : int, default 100
        Number of equally spaced time samples to generate (stacked oldest→newest).
    device : str or torch.device, default "cpu"
        Compute device.

    Returns
    -------
    np.ndarray
        Trajectories stacked as shape (ntimes, batch, dim), starting from the final
        dataset time and stepping backward.

    Notes
    -----
    - Starts from samples at the maximum dataset time.
    - Clears CUDA cache, disables grad, and integrates with fixed steps defined by `args.int_tps`.
    """
    torch.cuda.empty_cache()
    # pluck end samples
    end_samples = args.data.get_data()[
        args.data.get_times() == np.max(args.data.get_times())
    ]

    with torch.no_grad():
        z = torch.from_numpy(end_samples).type(torch.float32).to(device)
        zero = torch.zeros(z.shape[0], 1).to(z)
        cnf = model.chain[0]

        zs = [z]
        deltas = []
        int_tps = np.linspace(args.int_tps[0], args.int_tps[-1], ntimes)

        for i, itp in enumerate(int_tps[::-1][:-1]):
            # tp counts down from last
            timescale = int_tps[1] - int_tps[0]
            integration_times = torch.tensor([itp - timescale, itp]).type(torch.float32).to(device)

            # transform to previous timepoint
            z, delta_logp = cnf(zs[-1], zero, integration_times=integration_times)
            zs.append(z)
            deltas.append(delta_logp)

        zs = torch.stack(zs, 0)
        return zs.cpu().numpy()


def unwhiten_trajectories(data, dataset_path, embedding_name, scaler=None):
    """
    Inverse-standardize all trajectories from WHITENED PCA space back to
    ORIGINAL PCA units.

    Parameters
    ----------
    data : np.ndarray
        Shape (T, N, k) in WHITENED PCA space.
    dataset_path : str
        Path to NPZ containing the ORIGINAL (unwhitened) PCA matrix.
    embedding_name : str
        Key holding the original PCA matrix of shape (M, k).
    scaler : sklearn.preprocessing.StandardScaler, optional
        Pre-fit scaler on the ORIGINAL PCA matrix. If None, it is fit here.

    Returns
    -------
    data_unwhitened : np.ndarray
        Shape (T, N, k) in ORIGINAL PCA units.
    scaler : StandardScaler
        The fitted scaler used for the inverse transform.

    Notes
    -----
    Manual inverse (equivalent to StandardScaler.inverse_transform):
        data_unwhitened = data * scaler.scale_ + scaler.mean_
    """
    # fit scaler on ORIGINAL (unwhitened) PCA data if not provided
    if scaler is None:
        raw = np.load(dataset_path, allow_pickle=True)[embedding_name]
        scaler = StandardScaler().fit(raw)

    # vectorized broadcast over last axis (k)
    data = np.asarray(data, dtype=float)
    data_unwhitened = data * scaler.scale_ + scaler.mean_
    return data_unwhitened, scaler


def pca_to_gene(adata, scores, times=None, fill="nan"):
    """
    Back-project PCA scores to gene space and return a DataFrame.
    - scores: (T, k) array (e.g., means_unwhitened)
    - times: optional index of length T; defaults to range(T)
    - fill: "nan" (default) or "mean" for genes not used in PCA
    Columns are adata.var_names (all genes).
    """
    T, k = scores.shape
    vt = adata.varm["PCs"][:, :k]  # loadings: (n_vars_used, k) or (n_vars, k)

    # PCA settings
    pca_uns = adata.uns.get("pca", {})
    params = pca_uns.get("params", {})
    zero_center = bool(params.get("zero_center", True))

    # Matrix PCA was computed on (for means)
    X = adata.layers[params["layer"]] if params.get("layer") in adata.layers else adata.X
    if ss.issparse(X):
        X = X.toarray()

    n_vars = adata.n_vars
    mask_var = params.get("mask_var", None)
    use_hv = bool(params.get("use_highly_variable", False))
    if use_hv and (mask_var in adata.var.columns):
        gmask = adata.var[mask_var].to_numpy().astype(bool)
    else:
        gmask = np.ones(n_vars, dtype=bool)

    used_idx = np.where(gmask)[0] if vt.shape[0] == gmask.sum() else np.arange(n_vars)

    # Means
    mu_stored = pca_uns.get("mean", None)
    if mu_stored is not None and len(mu_stored) == vt.shape[0]:
        mu_used = np.asarray(mu_stored).ravel()
    else:
        mu_used = X[:, used_idx].mean(axis=0)
        if ss.issparse(mu_used):
            mu_used = mu_used.A1
    mu_full = X.mean(axis=0) if zero_center else np.zeros(n_vars)

    # Reconstruct only for genes used by PCA
    recon_used = scores @ vt.T  # (T, k) @ (k, n_used) -> (T, n_used)
    if zero_center:
        recon_used = recon_used + mu_used

    # Assemble full matrix
    if fill == "mean":
        X_full = np.broadcast_to(mu_full, (T, n_vars)).copy()
    else:  # "nan"
        X_full = np.full((T, n_vars), np.nan, dtype=float)

    X_full[:, used_idx] = recon_used

    # DataFrame with proper labels
    if times is None:
        times = np.arange(T)
    df = pd.DataFrame(X_full, index=pd.Index(times, name="time"), columns=adata.var_names)
    return df


