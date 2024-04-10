
def heatmap(dataframe, vmin= -2, vmax=2,  title='Title', xlabel = 'x-label', ylabel=None, color='PiYG', annot=True,annot_fmt = ".2f", annot_fontsize=8, cbar_title = 'Average Error', saveas=None, relpath=False, graphicsformat=["pdf"]):
    import matplotlib.pyplot as plt
    import seaborn as sns
    from cdsg_plot.qcdb_plot import expand_saveas
    sns.heatmap(dataframe, vmin=vmin, vmax=vmax, cmap=color, annot=annot, fmt=annot_fmt, annot_kws={"fontsize":annot_fontsize}, cbar_kws={'label':cbar_title})
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    files_saved = {}
    pltfile = expand_saveas(saveas, def_filename='', def_prefix="heatmap", relpath=relpath)
    for ext in graphicsformat:
        savefile = pltfile + "." + ext.lower()
        plt.savefig(savefile, transparent=True, format=ext, bbox_inches="tight")
        files_saved[ext.lower()] = savefile
    return files_saved

if __name__ == "__main__":
    import pandas as pd
    import math
    data = {'MP2-CP-adz': [-1.012, 0.8976, -1.4342, 1.6523],
            'MP2-CP-adtz': [0.68763, -0.265523, 0.47563, 0.64323],
            'MP2-CP-atz': [1.045234, 0.812312, 1.434243, -1.690313]}
    df = pd.DataFrame.from_dict(data, orient='index', columns=['A', 'B', 'C', 'D'])
    print(df)
    # get maximum absolute error for setting vmin and vmax
    abs_max = abs(df).values.max()
    abs_max = math.ceil(abs_max)
    heatmap(df, vmin = -1*abs_max, vmax=abs_max, title='Example', saveas='heatmap', graphicsformat=['pdf','png'])
