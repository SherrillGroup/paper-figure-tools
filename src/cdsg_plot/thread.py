from cdsg_plot.qcdb_plot import threads as mpl_threads


def plotly_threads(data, labels, color=None, title='', xlimit=4.0, mae=None, mape=None,
    mousetext=None, mouselink=None, mouseimag=None, mousetitle=None, mousediv=None,
    labeled=True, view=True,
    saveas=None, relpath=False, graphicsformat=['pdf']):
    """Generates a tiered slat diagram between model chemistries with
    errors (or simply values) in list *data*, which is supplied as part of the
    dictionary for each participating reaction, along with *dbse* and *rxn* keys
    in argument *data*. The plot is labeled with *title* and each tier with
    an element of *labels* and plotted at *xlimit* from the zero-line. If
    *color* is None, slats are black, if 'sapt', colors are taken from *color*
    key in *data* [0, 1]. Summary statistics *mae* are plotted on the
    overbound side and relative statistics *mape* on the underbound side.
    HTML code for mouseover if mousetext or mouselink or mouseimag specified
    based on recipe of Andrew Dalke from
    http://www.dalkescientific.com/writings/diary/archive/2005/04/24/interactive_html.html
    """
    import hashlib

    # initialize tiers/wefts
    Nweft = len(labels)
    lenS = 0.2
    gapT = 0.04
    positions = range(-1, -1 * Nweft - 1, -1)
    posnS = []
    for weft in range(Nweft):
        posnS.extend([positions[weft] + lenS, positions[weft] - lenS, None])
    posnT = []
    for weft in range(Nweft - 1):
        posnT.extend([positions[weft] - lenS - gapT, positions[weft + 1] + lenS + gapT, None])
    posnM = []
    xticks = [-0.5 * xlimit, -0.25 * xlimit, 0.0, 0.25 * xlimit, 0.5 * xlimit]

    # initialize plot
    import plotly.graph_objects as go
    fig = go.Figure()

    fig.update_layout(
        autosize=False,
        width=72 * 11,
        height=72 * Nweft * 0.8,
        margin=dict(b=36, l=7, r=7, t=34, pad=0),
        showlegend=False,
        xaxis=dict(range=[-xlimit, xlimit], tickvals=xticks, zeroline=True, zerolinewidth=3),
        yaxis=dict(range=[-1 * Nweft - 1, 0], showticklabels=False),
    )

    # label plot and tiers
    annot = []
    annot.append(go.layout.Annotation(
        x=-0.9 * xlimit,
        y=-0.25,
        align='left',
        #xanchor='left',
        text=title,
        showarrow=False,
        font=dict(size=12),
    ))
    for weft in labels:
        annot.append(go.layout.Annotation(
            x=-0.9 * xlimit,
            y=-(1.0 + labels.index(weft)),
            xref="x",
            yref="y",
            text=weft,
            align='left',
            showarrow=False,
            font=dict(size=18),
        ))
    fig.update_layout(annotations=annot)

#     if labeled:
#         ax.text(-0.9 * xlimit, -0.25, title,
#             verticalalignment='bottom', horizontalalignment='left',
#             family='Times New Roman', weight='bold', fontsize=12)
#         for weft in labels:
#             ax.text(-0.9 * xlimit, -(1.2 + labels.index(weft)), weft,
#                 verticalalignment='bottom', horizontalalignment='left',
#                 family='Times New Roman', weight='bold', fontsize=18)

    # plot reaction errors and threads
    for rxn in data:

        # preparation
        xvals = rxn['data']
        clr = rxn['color'] if 'color' in rxn else 'green' 
        slat = []
        for weft in range(Nweft):
            slat.extend([xvals[weft], xvals[weft], None])
        thread = []
        for weft in range(Nweft - 1):
            thread.extend([xvals[weft], xvals[weft + 1], None])

        # plotting
        fig.add_trace(go.Scatter(x=slat,
                                 y=posnS,
                                 mode='lines',
                                 name=rxn['sys'],
                                 line=dict(
                                     color=clr,
                                     dash='solid',
                                     width=1.0,
                                 ),
                                ))

        fig.add_trace(go.Scatter(x=thread, y=posnT,
                                 mode='lines',
                                 name=rxn['sys'],
                                 opacity=0.6, #0.3,
                                 showlegend=False,
                                 line=dict(
                                     color=clr,
                                     dash='solid',
                                     width=0.5,
                                 ),                        
                                ))

    # plot trimmings
    if mae is not None:
        fig.add_trace(go.Scatter(x=[-x for x in mae], y=list(positions),
                                 mode='markers',
                                 name='MAE',
                                 marker=dict(
                                     color='black',
                                     symbol='square'),
                                ))
    if mape is not None:  # equivalent to MAE for a 10 kcal/mol IE
        fig.add_trace(go.Scatter(x=[0.025 * x for x in mape], y=list(positions),
                                 mode='markers',
                                 name='MA%E',
                                 marker=dict(
                                     color='black',
                                     symbol='circle'),
                                ))

    # save and show
    pltuid = title + '_' + ('lbld' if labeled else 'bare') + '_' + hashlib.sha1((title + repr(labels) + repr(xlimit)).encode()).hexdigest()

    if view:
        fig.show()
    return fig


def plotly_ternary(sapt, title='', labeled=True, view=True,
            saveas=None, relpath=False, graphicsformat=['pdf']):
    """Takes array of arrays *sapt* in form [elst, indc, disp] of [elst, indc, disp, lbl] and builds formatted
    two-triangle ternary diagrams. Either fully-readable or dotsonly depending
    on *labeled*. Saves in formats *graphicsformat*.
    """
    import hashlib
    import plotly.graph_objects as go
    fig = go.Figure()

    # initialize plot
    fig.update_layout(
        #autosize=False,
        height=400,
        #width=72 * 6,
        #height=72 * 3.6,
        showlegend=False,
        xaxis=dict(range=[-0.75, 1.25], showticklabels=False, zeroline=False),
        yaxis=dict(range=[-0.18, 1.02], showticklabels=False, zeroline=False,
                   scaleanchor="x", scaleratio=1),
    )

    if labeled:

        # form and color ternary triangles
        fig.update_layout(
            shapes=[
                go.layout.Shape(
                    type="path",
                    path="M0, 0 L1, 0 L0.5, 0.866, Z",
                    line_color="black",
                    fillcolor="white",
                    layer="below",
                ),
                go.layout.Shape(
                    type="path",
                    path="M0, 0 L-0.5, 0.866 L0.5, 0.866, Z",
                    line_color="black",
                    fillcolor="#fff5ee",
                    layer="below",
                ),
            ])

#         # form and color HB/MX/DD dividing lines
#         ax.plot([0.667, 0.5], [0., 0.866], color='#eeb4b4', lw=0.5)
#         ax.plot([-0.333, 0.5], [0.577, 0.866], color='#eeb4b4', lw=0.5)
#         ax.plot([0.333, 0.5], [0., 0.866], color='#7ec0ee', lw=0.5)
#         ax.plot([-0.167, 0.5], [0.289, 0.866], color='#7ec0ee', lw=0.5)

        # label corners
        fig.update_layout(annotations=[
            go.layout.Annotation(
                x=1.0,
                y=-0.08,
                text=u'<b>Elst (\u2212)</b>',
                showarrow=False,
                font=dict(family="Times New Roman", size=18),
            ),
            go.layout.Annotation(
                x=0.5,
                y=0.94,
                text=u'<b>Ind (\u2212)</b>',
                showarrow=False,
                font=dict(family="Times New Roman", size=18),
            ),
            go.layout.Annotation(
                x=0.0,
                y=-0.08,
                text=u'<b>Disp (\u2212)</b>',
                showarrow=False,
                font=dict(family="Times New Roman", size=18),
            ),
            go.layout.Annotation(
                x=-0.5,
                y=0.94,
                text=u'<b>Elst (+)</b>',
                showarrow=False,
                font=dict(family="Times New Roman", size=18),
            ),
        ])

    xvals = []
    yvals = []
    cvals = []
    lvals = []
    for sys in sapt:
        if len(sys) == 3:
            [elst, indc, disp] = sys
            lbl = ''
        elif len(sys) == 4:
            [elst, indc, disp, lbl] = sys

        # calc ternary posn and color
        Ftop = abs(indc) / (abs(elst) + abs(indc) + abs(disp))
        Fright = abs(elst) / (abs(elst) + abs(indc) + abs(disp))
        xdot = 0.5 * Ftop + Fright
        ydot = 0.866 * Ftop
        cdot = 0.5 + (xdot - 0.5) / (1. - Ftop)
        if elst > 0.:
            xdot = 0.5 * (Ftop - Fright)
            ydot = 0.866 * (Ftop + Fright)

        xvals.append(xdot)
        yvals.append(ydot)
        cvals.append(cdot)
        lvals.append(lbl)

    fig.add_trace(go.Scatter(x=xvals, y=yvals,
                             text=lvals,
                             mode='markers',
                             marker=dict(
                                 color=cvals,
                                 colorscale='Jet',
                                 size=6,
                             ),                        
                  ))

#     sc = ax.scatter(xvals, yvals, c=cvals, s=15, marker="o", \
#         cmap=mpl.cm.jet, edgecolor='none', vmin=0, vmax=1, zorder=10)

#     # remove figure outline
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['bottom'].set_visible(False)
#     ax.spines['left'].set_visible(False)

    # save and show
    pltuid = title + '_' + ('lbld' if labeled else 'bare') + '_' + hashlib.sha1((title + repr(sapt)).encode()).hexdigest()

    if view:
        fig.show()
    return fig

if __name__ == "__main__":

    merge_dats = [
        {
            "show": "a",
            "db": "HSG",
            "sys": "1",
            "data": [0.3508, 0.1234, 0.0364, 0.0731, 0.0388],
        },
        {
            "show": "b",
            "db": "HSG",
            "sys": "3",
            "data": [0.2036, -0.0736, -0.1650, -0.1380, -0.1806],
        },
        # {'show':'', 'db':'S22', 'sys':'14', 'data':[np.nan, -3.2144, np.nan, np.nan, np.nan]},
        {
            "show": "c",
            "db": "S22",
            "sys": "14",
            "data": [None, -3.2144, None, None, None],
        },
        {
            "show": "d",
            "db": "S22",
            "sys": "15",
            "data": [-1.5090, -2.5263, -2.9452, -2.8633, -3.1059],
        },
        {
            "show": "e",
            "db": "S22",
            "sys": "22",
            "data": [0.3046, -0.2632, -0.5070, -0.4925, -0.6359],
        },
    ]

    mpl_threads_plt = mpl_threads(
        merge_dats,
        labels=["d", "t", "dt", "q", "tq"],
        color="sapt",
        title="MP2-CPa[]z",
        mae=[0.25, 0.5, 0.5, 0.3, 1.0],
        mape=[20.1, 25, 15, 5.5, 3.6],
        graphicsformat=["png"],
        view=False,
    )

    ply_threads_plt = plotly_threads(
        merge_dats,
        labels=["d", "t", "dt", "q", "tq"],
        color="sapt",
        title="MP2-CPa[]z",
        mae=[0.25, 0.5, 0.5, 0.3, 1.0],
        mape=[20.1, 25, 15, 5.5, 3.6],
    )

