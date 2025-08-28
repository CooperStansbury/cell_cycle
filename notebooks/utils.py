import numpy as np
import matplotlib.pyplot as plt

def compute_zscore(X):
    return (X - np.mean(X, axis=0, keepdims=True)) / np.std(X, axis=0, keepdims=True)

def get_masks(adata):
    whitfield_columns = adata.var.filter(like='whitfield').replace({'True': True, 'False': False}) 
    whitfield = np.logical_or.reduce(whitfield_columns.values.astype(bool), axis=1)
    
    go_columns = adata.var.filter(like='GO').replace({'True': True, 'False': False}) 
    go = np.logical_or.reduce(go_columns.values.astype(bool), axis=1)
    
    seurat_columns = adata.var.filter(like='seurat').replace({'True': True, 'False': False})
    seurat = np.logical_or.reduce(seurat_columns.values.astype(bool), axis=1)
    
    kegg = adata.var['is_kegg'].values
    
    liu_columns = adata.var.filter(like='LIU').replace({'True': True, 'False': False}) 
    liu = np.logical_or.reduce(liu_columns.values.astype(bool), axis=1)

    return whitfield, go, seurat, kegg, liu


def plot_gene_trajectories(data_list, gene_names, data_labels, degree=3, xaxis='time', time_partition=None, zscore=True, bin=False, ncols=1):
    times = time_partition.cumsum()

    gene_mask = [np.any(data_list[0].var['gene_name'] == gene) for gene in gene_names]
    gene_names = np.array(gene_names)
    gene_names = gene_names[gene_mask]
    
    time_points = np.array([0] + [data.shape[0] for data in data_list]).cumsum()
    Y = np.zeros((len(gene_names), time_points[-1]))

    fig_rows = int(np.ceil(len(gene_names) / ncols))

    # root = [data_list[0].obs['pred_phase'].tolist().index('M/G1'), 
    #         data_list[0].obs['pred_phase'].tolist().index('G1/S')]
    # print(root)
    
    fig, axs = plt.subplots(fig_rows, ncols, figsize=(2*12, 4*fig_rows), squeeze=False)
    for jj, (ax, gene_name) in enumerate(zip(axs.flatten(), gene_names)):
        if bin:
            xticks = []
        cat_time = []
        cat_data = []
            
        for ii, (adata, phase) in enumerate(zip(data_list, data_labels)):
            gene_mask = adata.var['gene_name'] == gene_name
            # nonzero_mask = adata.X[:,gene_mask].flatten() > -10
            # data_filtered = adata[nonzero_mask, gene_mask]
            data_filtered = adata[:, gene_mask]
            if xaxis == 'order':
                x = np.linspace(times[ii], times[ii+1], data_filtered.shape[0])
            elif xaxis == 'time':
                x = (data_filtered.obs['dpt_pseudotime'].values * time_partition[ii+1]) + times[ii]
            y = data_filtered.layers['zscore'].flatten() if zscore else data_filtered.X.flatten()
            ax.scatter(x, y, alpha=0.1, label=', '.join(phase))

            # ax.scatter(x[root[0]], y[root[0]], marker='*', s=100)
            # ax.scatter(x[root[1]], y[root[1]], marker='*', s=100)

            cat_time.append(x)
            cat_data.append(y)

        x = np.concatenate(cat_time)
        y = np.concatenate(cat_data)
        if bin:
            # Bin the data
            bins = np.arange(x.min(), x.max()+.1)
            bin_indices = np.digitize(x, bins)

            bin_means = []
            bin_stds = []
            bin_centers = []

            for b in range(1, len(bins)):
                bin_mask = bin_indices == b
                bin_data = y[bin_mask]
                if len(bin_data) > 0:
                    bin_means.append(np.mean(bin_data))
                    bin_stds.append(np.std(bin_data))
                    bin_centers.append((bins[b-1] + bins[b]) / 2)  # Center of the bin

            xticks += bin_centers

            bin_means = np.array(bin_means)
            bin_stds = np.array(bin_stds)
            bin_centers = np.array(bin_centers)

            # Plot the bin averages and standard deviation
            ax.plot(bin_centers, bin_means, color="red")
            ax.fill_between(bin_centers, bin_means - bin_stds, bin_means + bin_stds, color="red", alpha=0.2, label="Std dev" if ii==len(data_list)-1 else None)
            Y[jj, time_points[ii]:time_points[ii+1]] = np.interp(np.arange(time_points[ii], time_points[ii+1]), bin_centers, bin_means, left=bin_means[0], right=bin_means[-1])
            
        else:
            # continue
            coefficients = np.polyfit(x, y, degree)
            p = np.poly1d(coefficients)
            y_fit = p(x)
            residuals = y - y_fit
            uncertainty = np.std(residuals)
            
            # Compute upper and lower bounds for uncertainty
            y_upper = y_fit + uncertainty
            y_lower = y_fit - uncertainty
            ax.plot(x, y_fit, color="red")
            ax.fill_between(x, y_lower, y_upper, color="red", alpha=0.2, label="Error std" if ii==len(data_list)-1 else None)
            # Y[jj, time_points[ii]:time_points[ii+1]] = y_fit
            Y[jj] = y_fit
            ax.set_ylim([-3, 3])

        if bin:
            ax.set_xticks(xticks)
        
        ax.set_title(gene_name)
        if jj % ncols == 0:
            ax.set_ylabel('Gene expression' if not zscore else 'z-score')
        if jj >= ncols * (fig_rows-1):
            ax.set_xlabel('Time (h)')
    ax.legend()
    ax.legend(loc='center left', bbox_to_anchor=(1,0.5))
        
    # fig.text(0.5, 0.0, 'Time (h)', ha='center')
    # fig.text(0.0, 0.5, 'Gene expression' if not zscore else 'z-score', va='center', rotation='vertical')
    # fig.legend()
    fig.tight_layout()
    return Y, gene_names