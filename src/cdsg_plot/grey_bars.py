from cdsg_plot.qcdb_plot import bars

if __name__ == "__main__":

    more_dats = [
    {'mc':'MP2-CP-adz', 'data':[1.0, 0.8, 1.4, 1.6]},
    {'mc':'MP2-CP-adtz', 'data':[0.6, 0.2, 0.4, 0.6]},
    None,
    {'mc':'MP2-CP-adzagain', 'data':[1.0, 0.8, 1.4, 1.6]}]

    bars(more_dats, title='grey bars plot', graphicsformat=["png"])  # png for GH gallery


