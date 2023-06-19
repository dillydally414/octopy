from typing import Optional, Tuple, Union, List, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def shortest_distances(
    observed_distances: pd.DataFrame,
    expected_distances: Optional[Union[np.ndarray, Tuple[np.ndarray, float, float]]] = None,
    show: Optional[bool] = True,
    **kwargs,
) -> Union[plt.Axes, Tuple[plt.Axes, plt.Axes]]:
    """Plot the distribution of observed distances from each cell in one group to its closest
    cell of a second group as calculated by :func:`monkeybread.calc.shortest_distances`. 

    Optionally, also plot the null distribution of these distances under the null hypothesis 
    that the two cell types do not co-locate as computed by :func:`monkeybread.stat.shortest_distances`.

    Parameters
    ----------
    observed_distances
        The observed shortest distances, as calculated by :func:`monkeybread.calc.shortest_distances`.
    expected_distances
        The expected distances  under the null hypothesis that the two cell types do not co-locate. 
        Otional to include the distance threshold and p-value, as calculated by
        :func:`monkeybread.stat.shortest_distances`.
    show
        If true, displays the plot(s). If false, returns the Axes instead.
    kwargs
        Keyword arguments to pass to :func:`seaborn.histplot`.

    Returns
    -------
    If `show = False`, returns nothing. Otherwise, returns a single Axes object or a tuple of
    two Axes objects if expected_distances is provided.
    """
    # Set up plot structure
    ax = None
    axs: Tuple[Optional[plt.Axes], Optional[plt.Axes]] = (None, None)
    if expected_distances is not None:
        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
        ax = axs[0]

    # Plot actual distances on first axis
    ax = sns.histplot(observed_distances["distance"], ax=ax, legend=None, stat="density", **kwargs)
    ax.set_title("Observed Shortest Distances")

    # Plot expected distances distribution on second axis if exists
    if expected_distances is not None:
        sns.histplot(expected_distances[0], ax=axs[1], stat="density", **kwargs)

        axs[1].set_title("Expected Shortest Distances")
        max_y = max(axs[0].get_ylim(), axs[1].get_ylim())
        axs[0].set_ylim(max_y)
        axs[1].set_ylim(max_y)
        x_bounds = min(axs[0].get_xlim()[0], axs[1].get_xlim()[0]), max(axs[0].get_xlim()[1], axs[1].get_xlim()[1])
        axs[0].set_xlim(x_bounds)
        axs[1].set_xlim(x_bounds)
        axs[0].set_xlabel("Distance")
        axs[1].set_xlabel("Distance")

        # If p-value and threshold included, add to plots
        if type(expected_distances) == tuple:
            axs[0].text(
                0.97,
                0.97,
                f"p-value: {expected_distances[2]:.2f}",
                horizontalalignment="right",
                verticalalignment="top",
                transform=axs[0].transAxes,
            )
            threshold = expected_distances[1]
            threshold_line = axs[0].axvline(threshold, 0, 1.0, color="red", linestyle="--")
            axs[1].axvline(threshold, 0, 1.0, color="red", linestyle="--")
            axs[0].legend(handles=[threshold_line], labels=["Threshold"], loc="center left", bbox_to_anchor=(1, 0.5))
        plt.tight_layout()

    if show:
        plt.show()
    else:
        return axs if axs is not None else ax


def shortest_distances_pairwise(
        g1_to_g2_to_pval: Dict[str, Dict[str, float]],
        cmap: Optional[str] = 'viridis_r',
        annot: Optional[bool] = True,
        fmt: Optional[str] = '.2f',
        order_x: Optional[List[str]] = None,
        order_y: Optional[List[str]] = None,
        show: Optional[bool] = True,
        ax: Optional[plt.Axes] = None,
        **kwargs
    ) ->  plt.Axes:
    """Plot a heatmap of the p-values calculated by :func:`monkeybread.stat.shortest_distances_pairwise`
    that is the result of testing the co-localization between every cell type in one set to every
    cell type in a second set (e.g., myeloid cell types to T cell subtypes).

    Parameters
    ----------
    g1_to_g2_to_pval
        A dictionary mapping each cell type in one set to a cell type in a second set to a 
        p-value describing the signficance of their co-localization. This data structure
        is output by :func:`monkeybread.stat.shortest_distances_pairwise`.
    cmap
        Colormap used to color the heatmap.
    annot:
        If True, annotate the heatmap.
    fmt
        String format used to annotate the heatmap.
    order_x
        Order of labels along the x-axis (keys of the inner-dictionary within the `g1_to_g2_to_pval`
        argument.
    order_y
        Order of labels along the y-axis (keys of the outer-dictionary within the `g1_to_g2_to_pval`
        argument.
    show
        If True, show the plot and don't return the `plt.Axes` object.
    ax
        `plt.Axes` object to plot to
    kwargs
        Keyword arguments to pass to :func:`seaborn.heatmap`.

    Returns
    -------
    If `show = False`, returns nothing. Otherwise, returns a single Axes object or a tuple of
    two Axes objects if expected_distances is provided.
    """

    if order_y is None:
        cell_types_y = sorted(g1_to_g2_to_perms.keys())
    else:
        cell_types_y = order_y

    if order_x is None:
        cell_types_x = sorted(g1_to_g2_to_perms[cell_types_y[0]].keys())
    else:
        cell_types_x = order_x

    # Create dataframe used to plot
    mat = []
    for ct1 in cell_types_y:
        row = []
        for ct2 in cell_types_x:
            row.append(g1_to_g2_to_pval[ct1][ct2])
        mat.append(row)
    df_plot = pd.DataFrame(
        data=mat,
        index=cell_types_y,
        columns=cell_types_x
    )

    # Create heatmap
    if ax is None:
        fig, ax = plt.subplots(1,1, figsize=(6,2))
    sns.heatmap(
        df_plot, 
        cmap=cmap, 
        annot=annot,
        fmt=fmt,
        cbar_kws={'label': 'p-value'},
        vmin=0.0,
        vmax=1.0,
        ax=ax,
        **kwargs
    )
    if show:
        plt.show()
    else:
        return ax

