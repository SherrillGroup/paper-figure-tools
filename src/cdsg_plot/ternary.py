from cdsg_plot.qcdb_plot import ternary as mpl_ternary


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

    ply_tern_plt = plotly_ternary([[-1,-1,-1, "cat"],[-1,-2,-3, "mouse"],[1,-2,-3],[-1,-.1,-.1, "hen"], [-.1,-.1,-1]])

    # writes file but hangs on pop-up, hence view=False
    mpl_tern_plt = mpl_ternary([[-1,-1,-1],[-1,-2,-3],[1,-2,-3],[-1,-.1,-.1], [-.1,-.1,-1]], graphicsformat=["png"],
view=False)

