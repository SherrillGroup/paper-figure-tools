def create_minor_y_ticks(ylim):
    import numpy as np

    diff = abs(ylim[1] - ylim[0])
    if diff > 100:
        inc = 10
    if diff > 20:
        inc = 5
    elif diff > 10:
        inc = 2.5
    elif diff > 2:
        inc = 1
    else:
        inc = 0.25
    print(ylim)
    if ylim[0] > 2:
        lower_bound = int(ylim[0])
    else:
        lower_bound = ylim[0]
    while lower_bound % inc != 0:
        lower_bound -= 1
    if ylim[1] > 2:
        upper_bound = int(ylim[1])
    else:
        upper_bound = ylim[1]
    while upper_bound % inc != 0:
        upper_bound += 1
    upper_bound += inc
    print(f"{lower_bound = }, {upper_bound = }, {inc = }")
    major_yticks = np.arange(lower_bound, upper_bound, inc)
    minor_yticks = np.arange(lower_bound, upper_bound, inc/2)[:-1]
    return major_yticks, minor_yticks


def violin_plot(
    df,
    df_labels_and_columns: {},
    output_filename: str,
    plt_title: str = None,
    bottom: float = 0.4,
    ylim: list = None,
    transparent: bool = False,
    widths: float = 0.85,
    figure_size: tuple = None,
    set_xlable=False,
    x_label_rotation=90,
    x_label_fontsize=8,
    ylabel=r"Error ($\mathrm{kcal\cdot mol^{-1}}$)",
    dpi=600,
    usetex=True,
    rcParams={
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "mathtext.fontset": "custom",
    },
    colors: list = None,
    legend_loc="upper right",
) -> None:
    """
    Create a dataframe with columns of errors pre-computed for generating
    violin plots with MAE, RMSE, and MaxAE displayed above each violin.

    Args:
        df: DataFrame with columns of errors
        df_labels_and_columns: Dictionary of plotted labels along with the df column for data
        output_filename: Name of the output file
        ylim: list =[-15, 35],
        rcParams: can be set to None if latex is not used
        colors: list of colors for each df column plotted. A default will alternate between blue and green.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd

    if output_filename:
        print(f"Plotting {output_filename}")
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    vLabels, vData = [], []
    annotations = []  # [(x, y, text), ...]
    cnt = 1
    plt.rcParams["text.usetex"] = usetex
    for k, v in df_labels_and_columns.items():
        df[v] = pd.to_numeric(df[v])
        df_sub = df[df[v].notna()].copy()
        vData.append(df_sub[v].to_list())
        if usetex:
            k_label = "\\textbf{" + k + "}"
        else:
            k_label = k
        k_label = convert_deltas_ssapt0(k_label)
        vLabels.append(k_label)
        m = df_sub[v].max()
        rmse = df_sub[v].apply(lambda x: x**2).mean() ** 0.5
        mae = df_sub[v].apply(lambda x: abs(x)).mean()
        max_error = df_sub[v].apply(lambda x: abs(x)).max()
        if usetex:
            text = r"\textit{%.2f}" % mae
            text += "\n"
            text += r"\textbf{%.2f}" % rmse
            text += "\n"
            text += r"\textrm{%.2f}" % max_error
        else:
            text = r"%.2f" % mae
            text += "\n"
            text += r"%.2f" % rmse
            text += "\n"
            text += r"%.2f" % max_error
        annotations.append((cnt, m, text))
        cnt += 1

    pd.set_option("display.max_columns", None)
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    ax = plt.subplot(111)
    vplot = ax.violinplot(
        vData,
        showmeans=True,
        showmedians=False,
        quantiles=[[0.05, 0.95] for i in range(len(vData))],
        widths=widths,
    )
    for n, partname in enumerate(["cbars", "cmins", "cmaxes", "cmeans"]):
        vp = vplot[partname]
        vp.set_edgecolor("black")
        vp.set_linewidth(1)
        vp.set_alpha(1)
    quantile_color = "red"
    quantile_style = "-"
    quantile_linewidth = 0.8
    for n, partname in enumerate(["cquantiles"]):
        vp = vplot[partname]
        vp.set_edgecolor(quantile_color)
        vp.set_linewidth(quantile_linewidth)
        vp.set_linestyle(quantile_style)
        vp.set_alpha(1)

    colors = ["blue" if i % 2 == 0 else "green" for i in range(len(vLabels))]
    for n, pc in enumerate(vplot["bodies"], 1):
        pc.set_facecolor(colors[n - 1])
        pc.set_alpha(0.6)

    vLabels.insert(0, "")
    xs = [i for i in range(len(vLabels))]
    xs_error = [i for i in range(-1, len(vLabels) + 1)]
    x_error_label = r"$\pm$1 $\mathrm{kcal\cdot mol^{-1}}$" if usetex else r"within 1 kcal/mol"
    ax.plot(
        xs_error,
        [1 for i in range(len(xs_error))],
        "k--",
        label=x_error_label,
        zorder=0,
        linewidth=0.6,
    )
    ax.plot(
        xs_error,
        [0 for i in range(len(xs_error))],
        "k--",
        linewidth=0.5,
        alpha=0.5,
        # label=r"Reference Energy",
        zorder=0,
    )
    ax.plot(
        xs_error,
        [-1 for i in range(len(xs_error))],
        "k--",
        zorder=0,
        linewidth=0.6,
    )
    ax.plot(
        [],
        [],
        linestyle=quantile_style,
        color=quantile_color,
        linewidth=quantile_linewidth,
        label=r"5-95th Percentile",
    )
    navy_blue = (0.0, 0.32, 0.96)
    ax.set_xticks(xs)
    plt.setp(
        ax.set_xticklabels(vLabels),
        rotation=x_label_rotation,
        fontsize=x_label_fontsize,
    )
    ax.set_xlim((0, len(vLabels)))
    if ylim is not None:
        ax.set_ylim(ylim)
        major_yticks, minor_yticks = create_minor_y_ticks(ylim)
        ax.set_yticks(major_yticks)
        ax.set_yticks(minor_yticks, minor=True)

    lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

    if set_xlable:
        ax.set_xlabel("Level of Theory", color="k")
    ax.set_ylabel(ylabel, color="k")

    ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
    # Annotations of RMSE
    for x, y, text in annotations:
        ax.annotate(
            text,
            xy=(x, y),
            xytext=(x, y + 0.1),
            color="black",
            fontsize="8",
            horizontalalignment="center",
            verticalalignment="bottom",
        )

    for n, xtick in enumerate(ax.get_xticklabels()):
        xtick.set_color(colors[n - 1])
        xtick.set_alpha(0.8)

    if plt_title is not None:
        plt.title(f"{plt_title}")
    fig.subplots_adjust(bottom=bottom)
    if output_filename:
        ext = "png"
        if len(output_filename.split(".")) > 1:
            output_basename, ext = (
                ".".join(output_filename.split(".")[:-1]),
                output_filename.split(".")[-1],
            )
            path = f"{output_basename}_violin.{ext}"
        else:
            path = output_filename
        print(f"{path}")
        plt.savefig(
            path,
            transparent=transparent,
            bbox_inches="tight",
            dpi=dpi,
        )
    return


def violin_plot_table(
    df,
    df_labels_and_columns: {},
    output_filename: str,
    plt_title: str = None,
    bottom: float = 0.4,
    ylim: list = None,
    transparent: bool = False,
    widths: float = 0.85,
    figure_size: tuple = None,
    set_xlabel=False,
    x_label_rotation=90,
    x_label_fontsize=8,
    table_fontsize=8,
    ylabel=r"Error (kcal$\cdot$mol$^{-1}$)",
    dpi=600,
    usetex=True,
    rcParams={
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "mathtext.fontset": "custom",
    },
    colors: list = None,
    legend_loc="upper right",
) -> None:
    """
    Create a dataframe with columns of errors pre-computed for generating
    violin plots with MAE, RMSE, and MaxAE displayed above each violin.

    Args:
        df: DataFrame with columns of errors
        df_labels_and_columns: Dictionary of plotted labels along with the df column for data
        output_filename: Name of the output file
        ylim: list =[-15, 35],
        rcParams: can be set to None if latex is not used
        colors: list of colors for each df column plotted. A default will alternate between blue and green.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib import gridspec

    print(f"Plotting {output_filename}")
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    vLabels, vData = [], []
    annotations = []  # [(x, y, text), ...]
    cnt = 1
    plt.rcParams["text.usetex"] = usetex
    for k, v in df_labels_and_columns.items():
        df[v] = pd.to_numeric(df[v])
        df_sub = df[df[v].notna()].copy()
        vData.append(df_sub[v].to_list())
        k_label = "\\textbf{" + k + "}"
        k_label = convert_deltas_ssapt0(k_label)
        vLabels.append(k_label)
        m = df_sub[v].max()
        rmse = df_sub[v].apply(lambda x: x**2).mean() ** 0.5
        mae = df_sub[v].apply(lambda x: abs(x)).mean()
        max_pos_error = df_sub[v].apply(lambda x: x).max()
        max_neg_error = df_sub[v].apply(lambda x: x).min()
        text = r"\textit{%.2f}" % mae
        text += "\n"
        text += r"\textbf{%.2f}" % rmse
        text += "\n"
        text += r"\textrm{%.2f}" % max_pos_error
        text += "\n"
        text += r"\textrm{%.2f}" % max_neg_error
        annotations.append((cnt, m, text))
        cnt += 1

    pd.set_option("display.max_columns", None)
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    gs = gridspec.GridSpec(
        2, 1, height_ratios=[0.22, 1]
    )  # Adjust height ratios to change the size of subplots
    ax = plt.subplot(gs[1])  # This will create the subplot for the main violin plot.
    vplot = ax.violinplot(
        vData,
        showmeans=True,
        showmedians=False,
        showextrema=False,
        quantiles=[[0.05, 0.95] for i in range(len(vData))],
        widths=widths,
    )
    for n, partname in enumerate(["cmeans"]):
        vp = vplot[partname]
        vp.set_edgecolor("black")
        vp.set_linewidth(1)
        vp.set_alpha(1)
    quantile_color = "red"
    quantile_style = "-"
    quantile_linewidth = 0.8
    for n, partname in enumerate(["cquantiles"]):
        vp = vplot[partname]
        vp.set_edgecolor(quantile_color)
        vp.set_linewidth(quantile_linewidth)
        vp.set_linestyle(quantile_style)
        vp.set_alpha(1)

    colors = ["blue" if i % 2 == 0 else "green" for i in range(len(vLabels))]
    for n, pc in enumerate(vplot["bodies"], 1):
        pc.set_facecolor(colors[n - 1])
        pc.set_alpha(0.6)

    vLabels.insert(0, "")
    xs = [i for i in range(len(vLabels))]
    xs_error = [i for i in range(-1, len(vLabels) + 1)]
    ax.plot(
        xs_error,
        [1 for i in range(len(xs_error))],
        "k--",
        label=r"$\pm$1 $\mathrm{kcal\cdot mol^{-1}}$",
        zorder=0,
        linewidth=0.6,
    )
    ax.plot(
        xs_error,
        [0 for i in range(len(xs_error))],
        "k--",
        linewidth=0.5,
        alpha=0.5,
        # label=r"Reference Energy",
        zorder=0,
    )
    ax.plot(
        xs_error,
        [-1 for i in range(len(xs_error))],
        "k--",
        zorder=0,
        linewidth=0.6,
    )
    ax.plot(
        [],
        [],
        linestyle=quantile_style,
        color=quantile_color,
        linewidth=quantile_linewidth,
        label=r"5-95th Percentile",
    )
    navy_blue = (0.0, 0.32, 0.96)
    ax.set_xticks(xs)
    plt.setp(
        ax.set_xticklabels(vLabels),
        rotation=x_label_rotation,
        fontsize=x_label_fontsize,
    )
    ax.set_xlim((0, len(vLabels)))
    if ylim is not None:
        ax.set_ylim(ylim)
        major_yticks, minor_yticks = create_minor_y_ticks(ylim)
        ax.set_yticks(major_yticks)
        ax.set_yticks(minor_yticks, minor=True)

    lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

    if set_xlabel:
        ax.set_xlabel("Level of Theory", color="k")
    ax.set_ylabel(ylabel, color="k")

    ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
    for n, xtick in enumerate(ax.get_xticklabels()):
        xtick.set_color(colors[n - 1])
        xtick.set_alpha(0.8)

    ax_error = plt.subplot(gs[0], sharex=ax)
    # ax_error.spines['top'].set_visible(False)
    ax_error.spines["right"].set_visible(False)
    ax_error.spines["left"].set_visible(False)
    ax_error.spines["bottom"].set_visible(False)
    ax_error.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)

    # Synchronize the x-limits with the main subplot
    ax_error.set_xlim((0, len(vLabels)))
    ax_error.set_ylim(0, 1)  # Assuming the upper subplot should have no y range
    error_labels = r"\textit{MAE}"
    error_labels += "\n"
    error_labels += r"\textbf{RMSE}"
    error_labels += "\n"
    error_labels += r"\textrm{MaxE}"
    error_labels += "\n"
    error_labels += r"\textrm{MinE}"
    ax_error.annotate(
        error_labels,
        xy=(0, 1),  # Position at the vertical center of the narrow subplot
        xytext=(0, 0.2),
        color="black",
        fontsize=f"{table_fontsize}",
        ha="center",
        va="center",
    )
    for idx, (x, y, text) in enumerate(annotations):
        ax_error.annotate(
            text,
            xy=(x, 1),  # Position at the vertical center of the narrow subplot
            # xytext=(0, 0),
            xytext=(x, 0.2),
            color="black",
            fontsize=f"{table_fontsize}",
            ha="center",
            va="center",
        )

    if plt_title is not None:
        plt.title(f"{plt_title}")
    fig.subplots_adjust(bottom=bottom)
    ext = "png"
    if len(output_filename.split(".")) > 1:
        output_basename, ext = (
            ".".join(output_filename.split(".")[:-1]),
            output_filename.split(".")[-1],
        )
    path = f"{output_basename}_violin.{ext}"
    print(f"{path}")
    plt.savefig(
        path,
        transparent=transparent,
        bbox_inches="tight",
        dpi=dpi,
    )
    plt.clf()
    return


def violin_plot_table_multi(
    dfs,
    df_labels_and_columns: {},
    output_filename: str,
    plt_title: str = None,
    bottom: float = 0.4,
    transparent: bool = False,
    widths: float = 0.85,
    figure_size: tuple = None,
    set_xlable=False,
    x_label_rotation=90,
    x_label_fontsize=8,
    table_fontsize=8,
    ylabel=r"Error (kcal$\cdot$mol$^{-1}$)",
    dpi=600,
    usetex=True,
    rcParams={
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "mathtext.fontset": "custom",
    },
    colors: list = None,
    legend_loc="upper right",
    grid_heights=None,
    grid_widths=None,
    mcure=None,
    error_labels_position=(0, 0.25),
    violin_alpha=0.6,
) -> None:
    """
    Create a dataframe with columns of errors pre-computed for generating
    violin plots with MAE, RMSE, and MaxAE displayed above each violin.

    Args:
        df: DataFrame with columns of errors
        Example:
        dfs = [
            {"df": df_jdz, "label": "jun-cc-pVDZ", "ylim": [-4, 2]},
            {"df": df_adz, "label": "aug-cc-pVDZ", "ylim": [-2, 2]},
            {"df": df_atz, "label": "aug-cc-pVTZ", "ylim": [-2, 2]},
            {"df": df_adtz, "label": "aug-cc-pV[DT]Z", "ylim": [-2, 2]},
        ]
        df_labels_and_columns: Dictionary of plotted labels along with the df column for data
        output_filename: Name of the output file
        ylim: list =[-15, 35],
        rcParams: can be set to None if latex is not used
        colors: list of colors for each df column plotted. A default will alternate between blue and green.
        mcure: If requested, must pre-compute MCURE for each df_labels_and_columns key and assign as a dictionary
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib import gridspec

    ylabel_initial = ylabel

    print(f"Plotting {output_filename}")
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    if grid_heights is None:
        grid_heights = []
        for i in range(len(dfs)):
            grid_heights.append(0.6)
            grid_heights.append(2)
    print(len(dfs) * 2)

    gs = gridspec.GridSpec(
        len(dfs) * 2, 1, height_ratios=grid_heights
    )  # Adjust height ratios to change the size of subplots
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    for ind_0, j in enumerate(dfs):
        df = j["df"]
        subplot_label = j["label"]
        ylim = j["ylim"]
        vLabels, vData = [], []
        annotations = []  # [(x, y, text), ...]
        cnt = 1
        ind = 2 * ind_0
        print(f"{ind = }, {subplot_label = }")
        plt.rcParams["text.usetex"] = usetex
        non_null = len(df)
        for k, v in df_labels_and_columns.items():
            df[v] = pd.to_numeric(df[v])
            df_sub = df[df[v].notna()].copy()
            local_value = df_sub[v].to_list()
            if len(local_value) == 0:
                local_value = [0] * len(vData[-1])
            vData.append(local_value)
            k_label = "\\textbf{" + k + "}"
            k_label = convert_deltas_ssapt0(k_label)
            vLabels.append(k_label)
            m = df_sub[v].max()
            rmse = df_sub[v].apply(lambda x: x**2).mean() ** 0.5
            mae = df_sub[v].apply(lambda x: abs(x)).mean()
            max_pos_error = df_sub[v].apply(lambda x: x).max()
            max_neg_error = df_sub[v].apply(lambda x: x).min()
            text = r"\textit{%.2f}" % mae
            text += "\n"
            text += r"\textbf{%.2f}" % rmse
            text += "\n"
            text += r"\textrm{%.2f}" % max_pos_error
            text += "\n"
            text += r"\textrm{%.2f}" % max_neg_error
            if mcure is not None:
                text += "\n"
                text += r"\textrm{%.2f}" % mcure[k][ind_0]
            annotations.append((cnt, m, text))
            cnt += 1
            tmp = df_sub[v].notna().sum()
            if tmp < non_null and tmp != 0:
                non_null = tmp

        pd.set_option("display.max_columns", None)
        ax = plt.subplot(
            gs[ind + 1]
        )  # This will create the subplot for the main violin plot.
        vplot = ax.violinplot(
            vData,
            showmeans=True,
            showmedians=False,
            showextrema=False,
            quantiles=[[0.05, 0.95] for i in range(len(vData))],
            widths=widths,
        )
        for n, partname in enumerate(["cmeans"]):
            vp = vplot[partname]
            vp.set_edgecolor("black")
            vp.set_linewidth(1)
            vp.set_alpha(1)
        quantile_color = "red"
        quantile_style = "-"
        quantile_linewidth = 0.8
        for n, partname in enumerate(["cquantiles"]):
            vp = vplot[partname]
            vp.set_edgecolor(quantile_color)
            vp.set_linewidth(quantile_linewidth)
            vp.set_linestyle(quantile_style)
            vp.set_alpha(1)

        if colors is None:
            colors = ["blue" if i % 2 == 0 else "green" for i in range(len(vLabels))]
        for n, pc in enumerate(vplot["bodies"], 1):
            pc.set_facecolor(colors[n - 1])
            pc.set_alpha(violin_alpha)

        vLabels.insert(0, "")
        xs = [i for i in range(len(vLabels))]
        xs_error = [i for i in range(-1, len(vLabels) + 1)]
        ax.plot(
            xs_error,
            [1 for i in range(len(xs_error))],
            "k--",
            label=r"$\pm$1 $\mathrm{kcal\cdot mol^{-1}}$",
            zorder=0,
            linewidth=0.6,
        )
        ax.plot(
            xs_error,
            [0 for i in range(len(xs_error))],
            "k--",
            linewidth=0.5,
            alpha=0.5,
            # label=r"Reference Energy",
            zorder=0,
        )
        ax.plot(
            xs_error,
            [-1 for i in range(len(xs_error))],
            "k--",
            zorder=0,
            linewidth=0.6,
        )
        ax.plot(
            [],
            [],
            linestyle=quantile_style,
            color=quantile_color,
            linewidth=quantile_linewidth,
            label=r"5-95th Percentile",
        )
        navy_blue = (0.0, 0.32, 0.96)
        ax.set_xticks(xs)
        plt.setp(
            ax.set_xticklabels(vLabels),
            rotation=x_label_rotation,
            fontsize=x_label_fontsize,
        )
        ax.set_xlim((0, len(vLabels)))
        if ylim is not None:
            ax.set_ylim(ylim)
            major_yticks, minor_yticks = create_minor_y_ticks(ylim)
            ax.set_yticks(major_yticks)
            ax.set_yticks(minor_yticks, minor=True)

        if ind == 0:
            lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

        if set_xlable:
            ax.set_xlabel("Level of Theory", color="k")
        # ax.set_ylabel(f"{subplot_label}\n{ylabel_initial}", color="k")
        ax.set_ylabel(f"{ylabel_initial}", color="k")

        ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
        for n, xtick in enumerate(ax.get_xticklabels()):
            xtick.set_color(colors[n - 1])
            # xtick.set_alpha(0.8)
            xtick.set_alpha(violin_alpha)

        if ind != len(dfs) * 2 - 2:
            # ax.spines["bottom"].set_visible(False)
            # ax.tick_params(bottom=False)
            ax.tick_params(
                left=True,
                labelleft=True,
                bottom=False,
                labelbottom=False,
            )

            # plt.setp(ax.xaxis.get_ticklabels(), visible=False)
            # do not have xlabels

        ax_error = plt.subplot(gs[ind], sharex=ax)
        # ax_error.spines['top'].set_visible(False)
        ax_error.spines["right"].set_visible(False)
        ax_error.spines["left"].set_visible(False)
        ax_error.spines["bottom"].set_visible(False)
        ax_error.tick_params(
            left=False, labelleft=False, bottom=False, labelbottom=False
        )

        # Synchronize the x-limits with the main subplot
        ax_error.set_xlim((0, len(vLabels)))
        ax_error.set_ylim(0, 1)  # Assuming the upper subplot should have no y range
        error_labels = r"\textit{MAE}"
        error_labels += "\n"
        error_labels += r"\textbf{RMSE}"
        error_labels += "\n"
        error_labels += r"\textrm{MaxE}"
        error_labels += "\n"
        error_labels += r"\textrm{MinE}"
        if mcure is not None:
            error_labels += "\n"
            error_labels += r"\textrm{MCURE}"

        subplot_title = r"\textbf{" + subplot_label + r"}"
        subplot_title += r"(\textbf{" + str(non_null) + r"})" 
        ax_error.set_title(subplot_title, pad=-4)

        ax_error.annotate(
            error_labels,
            xy=(0, 1),  # Position at the vertical center of the narrow subplot
            xytext=error_labels_position,
            color="black",
            fontsize=f"{table_fontsize}",
            ha="center",
            va="center",
        )
        for idx, (x, y, text) in enumerate(annotations):
            ax_error.annotate(
                text,
                xy=(x, 1),  # Position at the vertical center of the narrow subplot
                # xytext=(0, 0),
                xytext=(x, 0.25),
                color="black",
                fontsize=f"{table_fontsize}",
                ha="center",
                va="center",
            )

    if plt_title is not None:
        plt.title(f"{plt_title}")
    fig.subplots_adjust(bottom=bottom)
    ext = "png"
    if len(output_filename.split(".")) > 1:
        output_basename, ext = (
            ".".join(output_filename.split(".")[:-1]),
            output_filename.split(".")[-1],
        )
    path = f"{output_basename}_violin.{ext}"
    print(f"{path}")
    plt.savefig(
        path,
        transparent=transparent,
        bbox_inches="tight",
        dpi=dpi,
    )
    plt.clf()
    return

def violin_plot_table_multi_horizontal(
    dfs,
    df_labels_and_columns: {},
    output_filename: str,
    plt_title: str = None,
    bottom: float = 0.4,
    transparent: bool = False,
    widths: float = 0.85,
    figure_size: tuple = None,
    set_xlable=False,
    x_label_rotation=90,
    x_label_fontsize=8,
    table_fontsize=8,
    ylabel=r"Error (kcal$\cdot$mol$^{-1}$)",
    dpi=600,
    usetex=True,
    rcParams={
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "mathtext.fontset": "custom",
    },
    colors: list = None,
    legend_loc="upper right",
    grid_heights=None,
    grid_widths=None,
    mcure=None,
) -> None:
    """
    Create a dataframe with columns of errors pre-computed for generating
    violin plots with MAE, RMSE, and MaxAE displayed above each violin.

    Args:
        df: DataFrame with columns of errors
        Example:
        dfs = [
            {"df": df_all, "label": "4569", "ylim": [-4, 2]},
            {"df": df_subset, "label": "288", "ylim": [-2, 2]},
        ]
        df_labels_and_columns: Dictionary of plotted labels along with the df column for data
        output_filename: Name of the output file
        ylim: list =[-15, 35],
        rcParams: can be set to None if latex is not used
        colors: list of colors for each df column plotted. A default will alternate between blue and green.
        mcure: If requested, must pre-compute MCURE for each df_labels_and_columns key and assign as a dictionary
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib import gridspec

    ylabel_initial = ylabel

    print(f"Plotting {output_filename}")
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    if grid_heights is None:
        grid_heights = []
        for i in range(len(dfs)):
            grid_heights.append(0.6)
            grid_heights.append(2)
    print(len(dfs) * 2)

    gs = gridspec.GridSpec(
        2, len(dfs), height_ratios=grid_heights, width_ratios=grid_widths
    )  # Adjust height ratios to change the size of subplots
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    vlabels_df = []
    for ind_0, j in enumerate(dfs):
        df = j["df"]
        subplot_label = j["label"]
        ylim = j["ylim"]
        vLabels, vData = [], []
        annotations = []  # [(x, y, text), ...]
        cnt = 1
        ind = 2 * ind_0
        print(f"{ind = }, {subplot_label = }")
        plt.rcParams["text.usetex"] = usetex
        non_null = len(df)
        for k, v in df_labels_and_columns.items():
            if v not in df.columns:
                print(f"{v} not found in df. Skipping...")
                continue
            df[v] = pd.to_numeric(df[v])
            df_sub = df[df[v].notna()].copy()
            vData.append(df_sub[v].to_list())
            k_label = "\\textbf{" + k + "}"
            k_label = convert_deltas_ssapt0(k_label)
            vLabels.append(k_label)
            m = df_sub[v].max()
            rmse = df_sub[v].apply(lambda x: x**2).mean() ** 0.5
            mae = df_sub[v].apply(lambda x: abs(x)).mean()
            max_pos_error = df_sub[v].apply(lambda x: x).max()
            max_neg_error = df_sub[v].apply(lambda x: x).min()
            text = r"\textit{%.2f}" % mae
            text += "\n"
            text += r"\textbf{%.2f}" % rmse
            text += "\n"
            text += r"\textrm{%.2f}" % max_pos_error
            text += "\n"
            text += r"\textrm{%.2f}" % max_neg_error
            if mcure is not None:
                text += "\n"
                text += r"\textrm{%.2f}" % mcure[k][ind_0]
            annotations.append((cnt, m, text))
            cnt += 1
            tmp = df_sub[v].notna().sum()
            if tmp < non_null:
                non_null = tmp
        vlabels_df.append(vLabels)

        pd.set_option("display.max_columns", None)
        ax = plt.subplot(
            gs[ind_0 + len(dfs)]
        )  # This will create the subplot for the main violin plot.
        vplot = ax.violinplot(
            vData,
            showmeans=True,
            showmedians=False,
            showextrema=False,
            quantiles=[[0.05, 0.95] for i in range(len(vData))],
            widths=widths,
        )
        for n, partname in enumerate(["cmeans"]):
            vp = vplot[partname]
            vp.set_edgecolor("black")
            vp.set_linewidth(1)
            vp.set_alpha(1)
        quantile_color = "red"
        quantile_style = "-"
        quantile_linewidth = 0.8
        for n, partname in enumerate(["cquantiles"]):
            vp = vplot[partname]
            vp.set_edgecolor(quantile_color)
            vp.set_linewidth(quantile_linewidth)
            vp.set_linestyle(quantile_style)
            vp.set_alpha(1)

        colors = ["blue" if i % 2 == 0 else "green" for i in range(len(vLabels))]
        for n, pc in enumerate(vplot["bodies"], 1):
            pc.set_facecolor(colors[n - 1])
            pc.set_alpha(0.6)

        vLabels.insert(0, "")
        xs = [i for i in range(len(vLabels))]
        xs_error = [i for i in range(-1, len(vLabels) + 1)]
        ax.plot(
            xs_error,
            [1 for i in range(len(xs_error))],
            "k--",
            label=r"$\pm$1 $\mathrm{kcal\cdot mol^{-1}}$",
            zorder=0,
            linewidth=0.6,
        )
        ax.plot(
            xs_error,
            [0 for i in range(len(xs_error))],
            "k--",
            linewidth=0.5,
            alpha=0.5,
            # label=r"Reference Energy",
            zorder=0,
        )
        ax.plot(
            xs_error,
            [-1 for i in range(len(xs_error))],
            "k--",
            zorder=0,
            linewidth=0.6,
        )
        ax.plot(
            [],
            [],
            linestyle=quantile_style,
            color=quantile_color,
            linewidth=quantile_linewidth,
            label=r"5-95th Percentile",
        )
        navy_blue = (0.0, 0.32, 0.96)
        ax.set_xticks(xs)
        plt.setp(
            ax.set_xticklabels(vLabels),
            rotation=x_label_rotation,
            fontsize=x_label_fontsize,
        )
        ax.set_xlim((0, len(vLabels)))
        if ylim is not None:
            ax.set_ylim(ylim)
            major_yticks, minor_yticks = create_minor_y_ticks(ylim)
            ax.set_yticks(major_yticks)
            ax.set_yticks(minor_yticks, minor=True)

        if ind == 0:
            lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

        if set_xlable:
            ax.set_xlabel("Level of Theory", color="k")
        # ax.set_ylabel(f"{subplot_label}\n{ylabel_initial}", color="k")
        ax.set_ylabel(f"{ylabel_initial}", color="k")

        ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
        for n, xtick in enumerate(ax.get_xticklabels()):
            xtick.set_color(colors[n - 1])
            xtick.set_alpha(0.8)


        ax_error = plt.subplot(gs[ind_0], sharex=ax)
        # ax_error.spines['top'].set_visible(False)
        ax_error.spines["right"].set_visible(False)
        ax_error.spines["left"].set_visible(False)
        ax_error.spines["bottom"].set_visible(False)
        ax_error.tick_params(
            left=False, labelleft=False, bottom=False, labelbottom=False
        )

        # Synchronize the x-limits with the main subplot
        ax_error.set_xlim((0, len(vLabels)))
        ax_error.set_ylim(0, 1)  # Assuming the upper subplot should have no y range
        error_labels = r"\textit{MAE}"
        error_labels += "\n"
        error_labels += r"\textbf{RMSE}"
        error_labels += "\n"
        error_labels += r"\textrm{MaxE}"
        error_labels += "\n"
        error_labels += r"\textrm{MinE}"
        if mcure is not None:
            error_labels += "\n"
            error_labels += r"\textrm{MCURE}"

        subplot_title = r"\textbf{" + subplot_label + r"}"
        subplot_title += r"(\textbf{" + str(non_null) + r"})" 
        ax_error.set_title(subplot_title, pad=-4)

        ax_error.annotate(
            error_labels,
            xy=(0, 1),  # Position at the vertical center of the narrow subplot
            xytext=(0, 0.25),
            color="black",
            fontsize=f"{table_fontsize}",
            ha="center",
            va="center",
        )
        for idx, (x, y, text) in enumerate(annotations):
            ax_error.annotate(
                text,
                xy=(x, 1),  # Position at the vertical center of the narrow subplot
                # xytext=(0, 0),
                xytext=(x, 0.25),
                color="black",
                fontsize=f"{table_fontsize}",
                ha="center",
                va="center",
            )

    if plt_title is not None:
        plt.title(f"{plt_title}")
    fig.subplots_adjust(bottom=bottom)
    ext = "png"
    if len(output_filename.split(".")) > 1:
        output_basename, ext = (
            ".".join(output_filename.split(".")[:-1]),
            output_filename.split(".")[-1],
        )
    path = f"{output_basename}_violin.{ext}"
    print(f"{path}")
    plt.savefig(
        path,
        transparent=transparent,
        bbox_inches="tight",
        dpi=dpi,
    )
    plt.clf()
    return

def convert_deltas_ssapt0(k_label):
    k_label = k_label.replace("DMP2", r"$\delta$MP2").replace("SSAPT0", r"\emph{s}SAPT0").replace("WB97", r"$\omega$B97")
    return k_label

def violin_plot_table_multi_SAPT_components(
    dfs,
    df_labels_and_columns_elst={},
    df_labels_and_columns_exch={},
    df_labels_and_columns_indu={},
    df_labels_and_columns_disp={},
    df_labels_and_columns_total={},
    output_filename: str = "output",
    plt_title: str = None,
    bottom: float = 0.4,
    left: float = None,
    transparent: bool = False,
    widths: float = 0.85,
    figure_size: tuple = None,
    set_xlabel=False,
    x_label_rotation=90,
    x_label_fontsize=8,
    y_label_fontsize=8,
    table_fontsize=8,
    title_fontsize=10,
    ylabel=r"Error (kcal$\cdot$mol$^{-1}$)",
    dpi=600,
    usetex=True,
    rcParams={
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "mathtext.fontset": "custom",
    },
    colors: list = None,
    legend_loc="upper right",
    grid_heights=None,
    grid_widths=None,
    MAE="textit",
    RMSE="textbf",
    MaxE="textrm",
    MinE="textrm",
    mcure=None,
    wspace=None,
    annotations_texty=0.4,
    share_y_axis=False,
    table_delimiter="",
    gridlines_linewidths=0.6,
    violin_alphas=0.6,
    quantile_color = "red",
    quantile_style = "-",
    quantile_linewidth = 0.8,
    pm_alpha=1.0,
    zero_alpha=0.5,
    hide_ytick_label_edges=False,
    add_title=True,
    ylabel_count=True,
    disable_xtick_labels=False,
    bbox_inches="tight",
) -> None:
    """
    TODO: maybe a 4xN grid for the 4 components of SAPT?
    Create a dataframe with columns of errors pre-computed for generating
    violin plots with MAE, RMSE, and MaxAE displayed above each violin.

    Args:
        df: DataFrame with columns of errors
        df_labels_and_columns: Dictionary of plotted labels along with the df column for data
        output_filename: Name of the output file
        ylim: list =[-15, 35],
        rcParams: can be set to None if latex is not used
        colors: list of colors for each df column plotted. A default will alternate between blue and green.
        mcure: If requested, must pre-compute MCURE for each components df_labels_and_columns_<COMPONENT>
        Dictionary structure:
            mcure_labels = {
                "ELST": [],
                "EXCH": [],
                "IND": [],
                "DISP": [],
            }
    """
    colors_initialized = True
    if colors is None:
        colors_initialized = False
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib import gridspec

    ylabel_initial = ylabel

    print(f"Plotting {output_filename}")
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    if grid_heights is None:
        heights = []
        for i in range(len(dfs)):
            heights.append(0.4)
            heights.append(2)
    if grid_widths is None:
        grid_widths = [1, 1, 1, 2]
    print(f"Must have {len(dfs) * 2} heights")
    columns = 0
    sapt_terms_plot = [] 
    if len(df_labels_and_columns_elst) > 0:
        columns += 1
        sapt_terms_plot.append("ELST")
    if len(df_labels_and_columns_exch) > 0:
        columns += 1
        sapt_terms_plot.append("EXCH")
    if len(df_labels_and_columns_indu) > 0:
        columns += 1
        sapt_terms_plot .append("INDU")
    if len(df_labels_and_columns_disp) > 0:
        columns += 1
        sapt_terms_plot.append("DISP")
    if len(df_labels_and_columns_total) > 0:
        columns += 1
        sapt_terms_plot.append("TOTAL")


    gs = gridspec.GridSpec(
        len(dfs) * 2, columns, height_ratios=grid_heights, width_ratios=grid_widths,
    )  # Adjust height ratios to change the size of subplots
    ax1 = None
    axs = []
    if wspace is not None:
        gs.update(wspace=wspace)
    print(f"{gs = }")
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    for nn, term in enumerate(sapt_terms_plot):
        if term == "ELST":
            df_labels_and_columns = df_labels_and_columns_elst
            sapt_color = 'red'
        elif term == "EXCH":
            df_labels_and_columns = df_labels_and_columns_exch
            sapt_color = 'green'
        elif term == "INDU":
            df_labels_and_columns = df_labels_and_columns_indu
            sapt_color = 'blue'
        elif term == "DISP":
            df_labels_and_columns = df_labels_and_columns_disp
            sapt_color = 'orange'
        elif term == "TOTAL":
            df_labels_and_columns = df_labels_and_columns_total
            sapt_color = 'black'
        print(f"{term = }")
        for ind_0, j in enumerate(dfs):
            df = j["df"]
            subplot_label = j["label"]
            ylim = j["ylim"][nn]
            vLabels, vData = [], []
            annotations = []  # [(x, y, text), ...]
            cnt = 1
            ind = ind_0 * 2
            plt.rcParams["text.usetex"] = usetex
            non_null = len(df)
            # print(f"{j['basis']}, {non_null = }")
# -            vData.append(df_sub[v].to_list())
# +            local_value = df_sub[v].to_list()
# +            if len(local_value) == 0:
# +                local_value = [0] * len(vData[-1])
# +            vData.append(local_value)
#              k_label = "\\textbf{" + k + "}"
#              k_label = convert_deltas(k_label)
#              vLabels.append(k_label)
# @@ -549,7 +552,7 @@ def violin_plot_table_multi(
#              annotations.append((cnt, m, text))
#              cnt += 1
#              tmp = df_sub[v].notna().sum()
# -            if tmp < non_null:
# +            if tmp < non_null and tmp != 0:
#                  non_null = tmp
            for col_ind, (k, v) in enumerate(df_labels_and_columns.items()):
                df[v] = pd.to_numeric(df[v])
                df_sub = df[df[v].notna()].copy()
                if len(df_sub) != len(df):
                    print('Missing data in', k, v)
                local_value = df_sub[v].to_list()
                if len(local_value) == 0:
                    local_value = [0] * len(vData[-1])
                vData.append(local_value)
                k_label = r"\noindent\textbf{" + r"}\\\textbf{".join(k.split(r"\\")) + "}"
                # k_label = r"\noindent\textbf{" + k + "}"
                k_label = convert_deltas_ssapt0(k_label)
                vLabels.append(k_label)
                m = df_sub[v].max()
                rmse = df_sub[v].apply(lambda x: x**2).mean() ** 0.5
                mae = df_sub[v].apply(lambda x: abs(x)).mean()
                max_pos_error = df_sub[v].apply(lambda x: x).max()
                max_neg_error = df_sub[v].apply(lambda x: x).min()
                errors_ls = []
                l_delim = table_delimiter if col_ind != len(df_labels_and_columns.keys()) - 1 else ""
                if MAE:
                    errors_ls.append(rf"\{MAE}{{{mae:.2f}}}{l_delim}")
                if RMSE:
                    errors_ls.append(rf"\{RMSE}{{{rmse:.2f}}}{l_delim}")
                if MaxE:
                    errors_ls.append(rf"\{MaxE}{{{max_pos_error:.2f}}}{l_delim}")
                if MinE:
                    errors_ls.append(rf"\{MinE}{{{max_neg_error:.2f}}}{l_delim}")
                # if mcure is not None and term != "TOTAL":
                if mcure is not None:
                    # try:
                        errors_ls.append(rf"\textrm{mcure[term][k][ind_0]:.2f}{l_delim}")
                    # except (Exception) as e:
                    #     print(f"Error: {e}")
                    #     print(f"term: {term}, k: {k}, ind_0: {ind_0}")
                    #     import sys
                    #     sys.exit(1)
                text = "\n".join(errors_ls)
                annotations.append((cnt, m, text))
                cnt += 1
                tmp = df_sub[v].notna().sum()
                if tmp < non_null and tmp != 0:
                    non_null = tmp

            pd.set_option("display.max_columns", None)
            if share_y_axis and ind != 0:
                ax = plt.subplot(
                    gs[ind+1, nn],
                    sharey=ax1,
                )
            else:
                ax = plt.subplot(
                    gs[ind+1, nn]
                )
                ax1 = ax
            axs.append(ax)
            vplot = ax.violinplot(
                vData,
                showmeans=True,
                showmedians=False,
                showextrema=False,
                quantiles=[[0.05, 0.95] for i in range(len(vData))],
                widths=widths,
            )
            for n, partname in enumerate(["cmeans"]):
                vp = vplot[partname]
                vp.set_edgecolor("black")
                vp.set_linewidth(1)
                vp.set_alpha(1)
            for n, partname in enumerate(["cquantiles"]):
                vp = vplot[partname]
                vp.set_edgecolor(quantile_color)
                vp.set_linewidth(quantile_linewidth)
                vp.set_linestyle(quantile_style)
                vp.set_alpha(1)

            if not colors_initialized:
                colors = [["blue" if i % 2 == 0 else "green" for i in range(len(vLabels))] for i in range(columns)]
            else:
                print(f"Term: {nn} colors {colors[nn]}")
            for n, pc in enumerate(vplot["bodies"], 1):
                try:
                    pc.set_facecolor(colors[nn][n - 1])
                except IndexError:
                    pc.set_facecolor('pink')
                pc.set_alpha(violin_alphas)

            vLabels.insert(0, "")
            xs = [i for i in range(len(vLabels))]
            xs_error = [i for i in range(-1, len(vLabels) + 1)]
            ax.plot(
                xs_error,
                [1 for i in range(len(xs_error))],
                "k--",
                label=r"$\pm$1 $\mathrm{kcal\cdot mol^{-1}}$",
                zorder=0,
                alpha=pm_alpha,
                linewidth=gridlines_linewidths,
            )
            ax.plot(
                xs_error,
                [0 for i in range(len(xs_error))],
                "k--",
                linewidth=gridlines_linewidths,
                alpha=zero_alpha,
                # label=r"Reference Energy",
                zorder=0,
            )
            ax.plot(
                xs_error,
                [-1 for i in range(len(xs_error))],
                "k--",
                zorder=0,
                alpha=pm_alpha,
                linewidth=gridlines_linewidths,
            )
            ax.plot(
                [],
                [],
                linestyle=quantile_style,
                color=quantile_color,
                linewidth=quantile_linewidth,
                label=r"5-95th Percentile",
            )
            navy_blue = (0.0, 0.32, 0.96)
            ax.set_xticks(xs)
            ax.spines['top'].set_color(sapt_color)
            ax.spines["right"].set_color(sapt_color)
            ax.spines["left"].set_color(sapt_color)
            ax.spines["bottom"].set_color(sapt_color)
            ax.spines['top'].set_linewidth(2.5)
            ax.spines["right"].set_linewidth(2.5)
            ax.spines["left"].set_linewidth(2.5)
            ax.spines["bottom"].set_linewidth(2.5)
            plt.setp(
                ax.set_xticklabels(vLabels),
                rotation=x_label_rotation,
                fontsize=x_label_fontsize,
            )
            ax.set_xlim((0, len(vLabels)))
            if ylim is not None:
                ax.set_ylim(ylim)
                if not share_y_axis or nn == 0:
                    print(ind, nn, 'ylim')
                    major_yticks, minor_yticks = create_minor_y_ticks(ylim)
                    ax.set_yticks(major_yticks)
                    ax.set_yticks(minor_yticks, minor=True)
                    if hide_ytick_label_edges:
                        major_yticks = list(major_yticks)
                        major_yticks[0] = ""
                        major_yticks[-1] = ""

                    ax.set_yticklabels(
                        major_yticks,
                        fontsize=y_label_fontsize,
                    )
                else:
                    ax.set_yticks([])

            if ind == 0 and nn == columns - 1 and legend_loc is not None:
                lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

            if set_xlabel:
                ax.set_xlabel("Level of Theory", color="k")
            # ax.set_ylabel(f"{subplot_label}\n{ylabel_initial}", color="k")
            if nn == 0:
                ylabel_row = r"\textbf{" + subplot_label + r"}"
                if ylabel_count:
                    ylabel_row += r"(\textbf{" + str(non_null) + r"})" 
                if ylabel_initial is not None:
                    ylabel_row += f"\n{ylabel_initial}"
                ax.set_ylabel(ylabel_row, color="k", fontsize=y_label_fontsize)

            ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
            # ax.grid(color="#54585A", which="minor", linewidth=0.5, alpha=0.5)

            for n, xtick in enumerate(ax.get_xticklabels()):
                try:
                    xtick.set_color(colors[nn][n - 1])
                except IndexError:
                    xtick.set_color('pink')
                xtick.set_alpha(0.8)

            if ind != len(dfs) * 2 - 2:
                ax.tick_params(
                    left=True,
                    labelleft=True,
                    bottom=False,
                    labelbottom=False,
                )

            if disable_xtick_labels:
                plt.setp(ax.xaxis.get_ticklabels(), visible=False)
                # ax.spines["bottom"].set_visible(False)
                # ax.tick_params(bottom=False)
            ax_error = plt.subplot(gs[ind, nn], sharex=ax)
            ax_error.spines['top'].set_visible(False)
            ax_error.spines["right"].set_visible(False)
            ax_error.spines["left"].set_visible(False)
            ax_error.spines["bottom"].set_visible(False)
            ax_error.tick_params(
                left=False, labelleft=False, bottom=False, labelbottom=False
            )

            # Synchronize the x-limits with the main subplot
            if share_y_axis:
                ax.set_xlim((0.5, len(vLabels) - 0.5))
            else:
                ax.set_xlim((0, len(vLabels)))
            ax_error.set_ylim(0, 1)  # Assuming the upper subplot should have no y range
            error_labels = []

            if MAE:
                error_labels.append(rf"\{MAE}{{MAE}}")
            if RMSE:
                error_labels.append(rf"\{RMSE}{{RMSE}}")
            if MaxE:
                error_labels.append(rf"\{MaxE}{{MaxE}}")
            if MinE:
                error_labels.append(rf"\{MinE}{{MinE}}")
            if mcure is not None:
                error_labels.append(rf"\textrm{{MCURE}}")
            error_labels = "\n".join(error_labels)

            if ind == 0:
                if add_title:
                    ax_error.spines['top'].set_visible(True)
                    subplot_title = r"\textbf{" + str(term) + r"}"
                    ax_error.set_title(subplot_title, color=sapt_color, pad=-4, fontsize=title_fontsize)

            if not share_y_axis or nn == 0:
                x_pos = 0
                x_pos_shift = 0
                if share_y_axis:
                    x_pos = 0.5
                    x_pos_shift = -0.5
                ax_error.annotate(
                    error_labels,
                    xy=(x_pos, 1),  # Position at the vertical center of the narrow subplot
                    xytext=(x_pos + x_pos_shift, annotations_texty),
                    color="black",
                    fontsize=f"{table_fontsize}",
                    ha="right",
                    va="center",
                )
            for idx, (x, y, text) in enumerate(annotations):
                ax_error.annotate(
                    text,
                    xy=(x, 1),  # Position at the vertical center of the narrow subplot
                    # xytext=(0, 0),
                    xytext=(x, annotations_texty),
                    color="black",
                    fontsize=f"{table_fontsize}",
                    ha="center",
                    va="center",
                )

    if plt_title is not None:
        plt.title(f"{plt_title}")
        
    fig.subplots_adjust(bottom=bottom)
    if left:
        fig.subplots_adjust(left=left)
    ext = "png"
    if len(output_filename.split(".")) > 1:
        output_basename, ext = (
            ".".join(output_filename.split(".")[:-1]),
            output_filename.split(".")[-1],
        )
    path = f"{output_basename}_violin.{ext}"
    print(f"{path}")
    if share_y_axis:
        # plt.subplots_adjust(hspace=0.1)
        plt.subplots_adjust(wspace=0.05)
    plt.savefig(
        path,
        transparent=transparent,
        bbox_inches=bbox_inches,
        dpi=dpi,
    )
    plt.clf()
    return


def violin_plot_table_multi_general(
    dfs,
    df_labels_and_columns={},
    output_filename: str = "output",
    plt_title: str = None,
    bottom: float = 0.4,
    transparent: bool = False,
    widths: float = 0.85,
    figure_size: tuple = None,
    set_xlable=False,
    x_label_rotation=90,
    x_label_fontsize=8,
    y_label_fontsize=8,
    table_fontsize=8,
    title_fontsize=10,
    ylabel=r"Error (kcal$\cdot$mol$^{-1}$)",
    dpi=600,
    usetex=True,
    rcParams={
        "text.usetex": True,
        "font.family": "sans-serif",
        "font.sans-serif": "Helvetica",
        "mathtext.fontset": "custom",
    },
    colors: list = None,
    legend_loc="upper right",
    grid_heights=None,
    grid_widths=None,
    MA="textit",
    RMS="textbf",
    Max="textrm",
    Min="textrm",
    mcure=None,
    display_counts=None,
    wspace=None,
    annotations_texty=0.4,
    share_y_axis=False,
    table_delimiter="",
    gridlines_linewidths=0.6,
    violin_alphas=0.6,
    quantile_color = "red",
    quantile_style = "-",
    quantile_linewidth = 0.8,
    pm_alpha=1.0,
    zero_alpha=0.5,
    hide_ytick_label_edges=False,
) -> None:
    """
    TODO: maybe a 4xN grid for the 4 components of SAPT?
    Create a dataframe with columns of errors pre-computed for generating
    violin plots with MAE, RMSE, and MaxAE displayed above each violin.

    Args:
        df: DataFrame with columns of errors
        df_labels_and_columns: Dictionary of plotted labels along with the df column for data
        output_filename: Name of the output file
        ylim: list =[-15, 35],
        rcParams: can be set to None if latex is not used
        colors: list of colors for each df column plotted. A default will alternate between blue and green.
        mcure: If requested, must pre-compute MCURE for each components df_labels_and_columns_<COMPONENT>
        Dictionary structure:
            mcure_labels = {
                "ELST": [],
                "EXCH": [],
                "IND": [],
                "DISP": [],
            }
    """
    colors_initialized = True
    if colors is None:
        colors_initialized = False
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib import gridspec

    ylabel_initial = ylabel

    print(f"Plotting {output_filename}")
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    if grid_heights is None:
        heights = []
        for i in range(len(dfs)):
            heights.append(0.4)
            heights.append(2)
    if grid_widths is None:
        grid_widths = [1, 1, 1, 2]
    print(f"Must have {len(dfs) * 2} heights")
    columns = 0
    terms_plot = []
    if len(df_labels_and_columns) > 0:
        columns += 1
        terms_plot.append("Values")


    gs = gridspec.GridSpec(
        len(dfs) * 2, columns, height_ratios=grid_heights, width_ratios=grid_widths,
    )  # Adjust height ratios to change the size of subplots
    ax1 = None
    if wspace is not None:
        gs.update(wspace=wspace)
    print(f"{gs = }")
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    for nn, term in enumerate(terms_plot):
        term_color = 'black'
        print(f"{term = }")
        for ind_0, j in enumerate(dfs):
            df = j["df"]
            subplot_label = j["label"]
            ylim = j["ylim"][nn]
            vLabels, vData = [], []
            annotations = []  # [(x, y, text), ...]
            cnt = 1
            ind = ind_0 * 2
            plt.rcParams["text.usetex"] = usetex
            non_null = len(df)
            # print(f"{j['basis']}, {non_null = }")
            for col_ind, (k, v) in enumerate(df_labels_and_columns.items()):
                df[v] = pd.to_numeric(df[v])
                df_sub = df[df[v].notna()].copy()
                if len(df_sub) != len(df):
                    print('Missing data in', k, v)
                local_value = df_sub[v].to_list()
                # if len(local_value) == 0:
                #     local_value = [0] * len(vData[-1])
                vData.append(local_value)
                k_label = r"\noindent\textbf{" + r"}\\\textbf{".join(k.split(r"\\")) + "}"
                # k_label = r"\noindent\textbf{" + k + "}"
                k_label = convert_deltas_ssapt0(k_label)
                vLabels.append(k_label)
                m = df_sub[v].max()
                local_v = df_sub[v].dropna().to_numpy()
                rmse = np.sqrt(np.mean(local_v ** 2))
                mae = np.mean(np.abs(local_v))
                max_pos_error = local_v.max()
                max_neg_error = local_v.min()
                print(f"{k}, {len(local_v)}, {mae = :.2f}, {rmse = :.2f}, {max_pos_error = :.2f}, {max_neg_error = :.2f}")
                errors_ls = []
                l_delim = table_delimiter if col_ind != len(df_labels_and_columns.keys()) - 1 else ""
                if MA:
                    errors_ls.append(rf"\{MA}{{{mae:.2f}}}{l_delim}")
                if RMS:
                    errors_ls.append(rf"\{RMS}{{{rmse:.2f}}}{l_delim}")
                if Max:
                    errors_ls.append(rf"\{Max}{{{max_pos_error:.2f}}}{l_delim}")
                if Min:
                    errors_ls.append(rf"\{Min}{{{max_neg_error:.2f}}}{l_delim}")
                if mcure is not None and term != "TOTAL":
                    try:
                        errors_ls.append(rf"\textrm{mcure[term][k][ind_0]:.2f}{l_delim}")
                    except (Exception) as e:
                        print(f"Error: {e}")
                        print(f"term: {term}, k: {k}, ind_0: {ind_0}")
                        import sys
                        sys.exit(1)
                if display_counts is not None:
                    errors_ls.append(rf"\{Min}{{{len(local_v)}}}{l_delim}")
                text = "\n".join(errors_ls)
                annotations.append((cnt, m, text))
                cnt += 1
            pd.set_option("display.max_columns", None)
            if share_y_axis and ind != 0:
                ax = plt.subplot(
                    gs[ind+1, nn],
                    sharey=ax1,
                )
            else:
                ax = plt.subplot(
                    gs[ind+1, nn]
                )
                ax1 = ax
            vplot = ax.violinplot(
                vData,
                showmeans=True,
                showmedians=False,
                showextrema=False,
                quantiles=[[0.05, 0.95] for i in range(len(vData))],
                widths=widths,
            )
            for n, partname in enumerate(["cmeans"]):
                vp = vplot[partname]
                vp.set_edgecolor("black")
                vp.set_linewidth(1)
                vp.set_alpha(1)
            for n, partname in enumerate(["cquantiles"]):
                vp = vplot[partname]
                vp.set_edgecolor(quantile_color)
                vp.set_linewidth(quantile_linewidth)
                vp.set_linestyle(quantile_style)
                vp.set_alpha(1)

            if not colors_initialized:
                colors = [["blue" if i % 2 == 0 else "green" for i in range(len(vLabels))] for i in range(columns)]
            else:
                print(f"Term: {nn} colors {colors[nn]}")
            for n, pc in enumerate(vplot["bodies"], 1):
                pc.set_facecolor(colors[nn][n - 1])
                pc.set_alpha(violin_alphas)

            vLabels.insert(0, "")
            xs = [i for i in range(len(vLabels))]
            xs_error = [i for i in range(-1, len(vLabels) + 1)]
            ax.plot(
                xs_error,
                [1 for i in range(len(xs_error))],
                "k--",
                label=r"$\pm$1 $\mathrm{kcal\cdot mol^{-1}}$",
                zorder=0,
                alpha=pm_alpha,
                linewidth=gridlines_linewidths,
            )
            ax.plot(
                xs_error,
                [0 for i in range(len(xs_error))],
                "k--",
                linewidth=gridlines_linewidths,
                alpha=zero_alpha,
                # label=r"Reference Energy",
                zorder=0,
            )
            ax.plot(
                xs_error,
                [-1 for i in range(len(xs_error))],
                "k--",
                zorder=0,
                alpha=pm_alpha,
                linewidth=gridlines_linewidths,
            )
            ax.plot(
                [],
                [],
                linestyle=quantile_style,
                color=quantile_color,
                linewidth=quantile_linewidth,
                label=r"5-95th Percentile",
            )
            navy_blue = (0.0, 0.32, 0.96)
            ax.set_xticks(xs)
            ax.spines['top'].set_color(term_color)
            ax.spines["right"].set_color(term_color)
            ax.spines["left"].set_color(term_color)
            ax.spines["bottom"].set_color(term_color)
            ax.spines['top'].set_linewidth(2.5)
            ax.spines["right"].set_linewidth(2.5)
            ax.spines["left"].set_linewidth(2.5)
            ax.spines["bottom"].set_linewidth(2.5)
            plt.setp(
                ax.set_xticklabels(vLabels),
                rotation=x_label_rotation,
                fontsize=x_label_fontsize,
            )
            if share_y_axis:
                ax.set_xlim((0.5, len(vLabels) - 0.5))
            else:
                ax.set_xlim((0, len(vLabels)))
            if ylim is not None:
                ax.set_ylim(ylim)
                if not share_y_axis or nn == 0:
                    print(ind, nn, 'ylim')
                    major_yticks, minor_yticks = create_minor_y_ticks(ylim)
                    ax.set_yticks(major_yticks)
                    ax.set_yticks(minor_yticks, minor=True)
                    if hide_ytick_label_edges:
                        major_yticks = list(major_yticks)
                        major_yticks[0] = ""
                        major_yticks[-1] = ""

                    ax.set_yticklabels(
                        major_yticks,
                        fontsize=y_label_fontsize,
                    )
                else:
                    ax.set_yticks([])

            if ind == 0 and nn == columns - 1 and legend_loc is not None:
                lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

            if set_xlable:
                ax.set_xlabel("Level of Theory", color="k")
            # ax.set_ylabel(f"{subplot_label}\n{ylabel_initial}", color="k")
            if nn == 0:
                ylabel_row = r"\textbf{" + subplot_label + r"}"
                ylabel_row += r"(\textbf{" + str(non_null) + r"})" f"\n{ylabel_initial}"
                ax.set_ylabel(ylabel_row, color="k", fontsize=y_label_fontsize)

            ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
            # ax.grid(color="#54585A", which="minor", linewidth=0.5, alpha=0.5)
            for n, xtick in enumerate(ax.get_xticklabels()):
                xtick.set_color(colors[nn][n - 1])
                xtick.set_alpha(0.8)

            if ind != len(dfs) * 2 - 2:
                ax.tick_params(
                    left=True,
                    labelleft=True,
                    bottom=False,
                    labelbottom=False,
                )

            ax_error = plt.subplot(gs[ind, nn], sharex=ax)
            ax_error.spines['top'].set_visible(False)
            ax_error.spines["right"].set_visible(False)
            ax_error.spines["left"].set_visible(False)
            ax_error.spines["bottom"].set_visible(False)
            ax_error.tick_params(
                left=False, labelleft=False, bottom=False, labelbottom=False
            )

            # Synchronize the x-limits with the main subplot
            ax_error.set_xlim((0, len(vLabels)))
            ax_error.set_ylim(0, 1)  # Assuming the upper subplot should have no y range
            error_labels = []

            if MA:
                error_labels.append(rf"\{MA}{{MA}}")
            if RMS:
                error_labels.append(rf"\{RMS}{{RMS}}")
            if Max:
                error_labels.append(rf"\{Max}{{Max}}")
            if Min:
                error_labels.append(rf"\{Min}{{Min}}")
            if mcure is not None:
                error_labels.append(rf"\textrm{{MCURE}}")
            if display_counts is not None:
                error_labels.append(rf"\{display_counts}{{Count}}")
            error_labels = "\n".join(error_labels)

            if ind == 0:
                ax_error.spines['top'].set_visible(True)
                # subplot_title = r"\textbf{" + str(term) + r"}" 
                # ax_error.set_title(subplot_title, color=term_color, pad=-4, fontsize=title_fontsize)

            if not share_y_axis or nn == 0:
                ax_error.annotate(
                    error_labels,
                    xy=(0, 1),  # Position at the vertical center of the narrow subplot
                    xytext=(0.0, annotations_texty),
                    color="black",
                    fontsize=f"{table_fontsize}",
                    ha="right",
                    va="center",
                )
            for idx, (x, y, text) in enumerate(annotations):
                ax_error.annotate(
                    text,
                    xy=(x, 1),  # Position at the vertical center of the narrow subplot
                    # xytext=(0, 0),
                    xytext=(x, annotations_texty),
                    color="black",
                    fontsize=f"{table_fontsize}",
                    ha="center",
                    va="center",
                )

    if plt_title is not None:
        plt.title(f"{plt_title}")
    fig.subplots_adjust(bottom=bottom)
    ext = "png"
    if len(output_filename.split(".")) > 1:
        output_basename, ext = (
            ".".join(output_filename.split(".")[:-1]),
            output_filename.split(".")[-1],
        )
    path = f"{output_basename}_violin.{ext}"
    print(f"{path}")
    plt.savefig(
        path,
        transparent=transparent,
        bbox_inches="tight",
        dpi=dpi,
    )
    plt.clf()
    return

if __name__ == "__main__":
    # Fake data generated for example
    import pandas as pd
    import numpy as np
    df = pd.DataFrame(
        {
            "MP2": 5 * np.random.randn(1000) + 0.5,
            "HF": 5 * np.random.randn(1000) - 0.5,
            "MP2.5": 5 * np.random.randn(1000) + 0.5,
        }
    )
    # Only specify columns you want to plot
    vals = {
        "MP2 label": "MP2",
        "HF label": "HF",
    }
    violin_plot(df, vals, ylim=[-20, 35], output_filename="example")
