def create_minor_y_ticks(ylim):
    import numpy as np

    diff = abs(ylim[1] - ylim[0])
    if diff > 100:
        inc = 10
    if diff > 20:
        inc = 5
    elif diff > 10:
        inc = 2.5
    else:
        inc = 1
    lower_bound = int(ylim[0])
    while lower_bound % inc != 0:
        lower_bound -= 1
    upper_bound = int(ylim[1])
    while upper_bound % inc != 0:
        upper_bound += 1
    upper_bound += inc
    minor_yticks = np.arange(lower_bound, upper_bound, inc)
    return minor_yticks


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
        vLabels.append(k_label)
        m = df_sub[v].max()
        rmse = df_sub[v].apply(lambda x: x**2).mean() ** 0.5
        mae = df_sub[v].apply(lambda x: abs(x)).mean()
        max_error = df_sub[v].apply(lambda x: abs(x)).max()
        text = r"\textit{%.2f}" % mae
        text += "\n"
        text += r"\textbf{%.2f}" % rmse
        text += "\n"
        text += r"\textrm{%.2f}" % max_error
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
        minor_yticks = create_minor_y_ticks(ylim)
        ax.set_yticks(minor_yticks, minor=True)

    lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

    if set_xlable:
        ax.set_xlabel("Level of Theory", color="k")
    ax.set_ylabel(ylabel, color="k")

    ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
    ax.grid(color="#54585A", which="minor", linewidth=0.5, alpha=0.5)
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
        minor_yticks = create_minor_y_ticks(ylim)
        ax.set_yticks(minor_yticks, minor=True)

    lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

    if set_xlable:
        ax.set_xlabel("Level of Theory", color="k")
    ax.set_ylabel(ylabel, color="k")

    ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
    ax.grid(color="#54585A", which="minor", linewidth=0.5, alpha=0.5)
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

    ylabel_initial = ylabel

    print(f"Plotting {output_filename}")
    fig = plt.figure(dpi=dpi)
    if figure_size is not None:
        plt.figure(figsize=figure_size)
    if grid_heights is None:
        grid_heights = []
        for i in range(len(dfs)):
            grid_heights.append(0.4)
            grid_heights.append(2)
    print(len(dfs) * 2)

    gs = gridspec.GridSpec(
        len(dfs) * 2, 1, height_ratios=grid_heights
    )  # Adjust height ratios to change the size of subplots
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    for ind, j in enumerate(dfs):
        df = j["df"]
        subplot_label = j["label"]
        ylim = j["ylim"]
        vLabels, vData = [], []
        annotations = []  # [(x, y, text), ...]
        cnt = 1
        ind *= 2
        print(f"{ind = }, {subplot_label = }")
        plt.rcParams["text.usetex"] = usetex
        non_null = len(df)
        for k, v in df_labels_and_columns.items():
            df[v] = pd.to_numeric(df[v])
            df_sub = df[df[v].notna()].copy()
            vData.append(df_sub[v].to_list())
            k_label = "\\textbf{" + k + "}"
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
            tmp = df_sub[v].notna().sum()
            if tmp < non_null:
                non_null = tmp
            print(f"{non_null = }")

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
            minor_yticks = create_minor_y_ticks(ylim)
            ax.set_yticks(minor_yticks, minor=True)

        if ind == 0:
            lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

        if set_xlable:
            ax.set_xlabel("Level of Theory", color="k")
        # ax.set_ylabel(f"{subplot_label}\n{ylabel_initial}", color="k")
        ax.set_ylabel(f"{ylabel_initial}", color="k")

        ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
        ax.grid(color="#54585A", which="minor", linewidth=0.5, alpha=0.5)
        for n, xtick in enumerate(ax.get_xticklabels()):
            xtick.set_color(colors[n - 1])
            xtick.set_alpha(0.8)

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

        subplot_title = r"\textbf{" + subplot_label + r"}"
        subplot_title += r"(\textbf{" + str(non_null) + r"})" 
        ax_error.set_title(subplot_title, pad=-4)
        # subplot_label = r"\textbf{" + subplot_label + r"}"
        # subplot_label += "\n" r"(\textbf{" + str(non_null) + r"}" ")\n"
        # ax_error.set_ylabel(subplot_label, color="k")

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

def violin_plot_table_multi_SAPT_components(
    dfs,
    df_labels_and_columns_elst: {},
    df_labels_and_columns_exch: {},
    df_labels_and_columns_indu: {},
    df_labels_and_columns_disp: {},
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
        heights = []
        for i in range(len(dfs)):
            heights.append(0.4)
            heights.append(2)
    if grid_widths is None:
        grid_widths = [1, 1, 1, 2]
    print(len(dfs) * 2)

    gs = gridspec.GridSpec(
        len(dfs) * 2, 4, height_ratios=grid_heights, width_ratios=grid_widths,
    )  # Adjust height ratios to change the size of subplots
    print(f"{gs = }")
    if rcParams is not None:
        plt.rcParams.update(rcParams)
    for nn, term in enumerate(['ELST', 'EXCH', 'IND', 'DISP']):
        if nn == 0:
            df_labels_and_columns = df_labels_and_columns_elst
            sapt_color = 'red'
        elif nn == 1:
            df_labels_and_columns = df_labels_and_columns_exch
            sapt_color = 'blue'
        elif nn == 2:
            df_labels_and_columns = df_labels_and_columns_indu
            sapt_color = 'green'
        elif nn == 3:
            df_labels_and_columns = df_labels_and_columns_disp
            sapt_color = 'orange'
        print(f"{term = }")
        for ind, j in enumerate(dfs):
            df = j["df"]
            subplot_label = j["label"]
            ylim = j["ylim"][nn]
            vLabels, vData = [], []
            annotations = []  # [(x, y, text), ...]
            cnt = 1
            ind *= 2
            print(f"{ind = }, {subplot_label = }")
            plt.rcParams["text.usetex"] = usetex
            non_null = len(df)
            for k, v in df_labels_and_columns.items():
                df[v] = pd.to_numeric(df[v])
                df_sub = df[df[v].notna()].copy()
                vData.append(df_sub[v].to_list())
                k_label = "\\textbf{" + k + "}"
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
                tmp = df_sub[v].notna().sum()
                if tmp < non_null:
                    non_null = tmp
                print(f"{non_null = }")

            pd.set_option("display.max_columns", None)
            ax = plt.subplot(
                gs[ind+1, nn]
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
                minor_yticks = create_minor_y_ticks(ylim)
                ax.set_yticks(minor_yticks, minor=True)

            if ind == 0 and nn == 3:
                lg = ax.legend(loc=legend_loc, edgecolor="black", fontsize="8")

            if set_xlable:
                ax.set_xlabel("Level of Theory", color="k")
            # ax.set_ylabel(f"{subplot_label}\n{ylabel_initial}", color="k")
            if nn == 0:
                ylabel_row = r"\textbf{" + subplot_label + r"}"
                ylabel_row += r"(\textbf{" + str(non_null) + r"})" f"\n{ylabel_initial}"
                ax.set_ylabel(ylabel_row, color="k")

            ax.grid(color="#54585A", which="major", linewidth=0.5, alpha=0.5, axis="y")
            ax.grid(color="#54585A", which="minor", linewidth=0.5, alpha=0.5)
            for n, xtick in enumerate(ax.get_xticklabels()):
                xtick.set_color(colors[n - 1])
                xtick.set_alpha(0.8)

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
            error_labels = r"\textit{MAE}"
            error_labels += "\n"
            error_labels += r"\textbf{RMSE}"
            error_labels += "\n"
            error_labels += r"\textrm{MaxE}"
            error_labels += "\n"
            error_labels += r"\textrm{MinE}"

            if ind == 0:
                # subplot_title = r"\textbf{" + subplot_label + r"}"
                # subplot_title += r"(\textbf{" + str(non_null) + r"})" 
                ax_error.spines['top'].set_visible(True)
                subplot_title = r"\textbf{" + str(term) + r"}" 
                ax_error.set_title(subplot_title, color=sapt_color, pad=-4)
            # subplot_label = r"\textbf{" + subplot_label + r"}"
            # subplot_label += "\n" r"(\textbf{" + str(non_null) + r"}" ")\n"
            # ax_error.set_ylabel(subplot_label, color="k")

            ax_error.annotate(
                error_labels,
                xy=(0, 1),  # Position at the vertical center of the narrow subplot
                xytext=(0, 0.4),
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
                    xytext=(x, 0.4),
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
