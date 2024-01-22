# TODO: Add vertical line every time the optimization layer is evaluated. A vertical line when it starts, filled until it ends with another vertical line
# TODO: Add legend for control layer (setpoint, output, disturbance)
# TODO: Filter out unreasonable values for consumptions (Ce and Cw)
# TODO: If a system is inactive, its control signal must go to zero, add representation of state with filled areas, ON: color of the system, OFF: gray
# TODO: Add uncertainty bounds for timeseries signals
# TODO: Electricity consumption

import pandas as pd
import datetime
import plotly
import plotly.graph_objects as go
from loguru import logger
from .constants import color_palette, default_fontsize, newshape_style
from .calculations import calculate_uncertainty

def experimental_results_plot(plt_config: dict, df: pd.DataFrame, df_opt: pd.DataFrame) -> go.Figure:

    row_heights = []
    n_yaxis = []
    subplot_titles = []
    for plot_props in plt_config['plots'].values():
        row_heights.append(plot_props["row_height"])
        # plot_bg_colors.append( plot_props.get("plot_bg_colors", "steelblue") )
        subplot_titles.append(plot_props.get("title", ""))

    # n_yaxis          = [2, 2, 3, 1,   1,  1,  1, 1,   1, 1,   1, 1,   1]
    # plot_bg_colors   = ["steelblue" for _ in range(2)]
    # plot_bg_colors.append("#e5a50a")
    # plot_bg_colors.extend(["#B6B6B6" for _ in range(10)])
    # yaxis_labels     = [("T<sub>amb</sub> (ºC)", "ɸ (%)"), ("T<sub>v</sub> (ºC)", "P<sub>th</sub> (kW<sub>th</sub>)"),
    #                     ("C (u.m.)", "C<sub>e</sub> (kWh)", "C<sub>w</sub> (l/h)"), "cv ()", ""]

    # additional_space = [0, 0, 0, 0,   0,  0,  0, 0,   0, 0,   0, 0,   0] # Number of additional vertical_spacing to leave
    # vertical_spacing = 0.03
    vertical_spacing = plt_config["vertical_spacing"]
    xdomain = plt_config["xdomain"]
    height = plt_config["height"]
    width = plt_config["width"]
    yaxis_right_pos = [.86, .95]
    arrow_xrel_pos = plt_config.get("arrow_xrel_pos", 20)
    default_active_color = {'active': color_palette['plotly_green_rgb'], 'inactive': color_palette['gray_rgb']}

    # xdomain = (0, 0.85)
    # height = 1600
    # width = 800
    # subplot_titles=[
    #     "Environment",
    #     "Cooling Requirements - Tv and Pth",
    #     "Costs",
    #     "Temperatures - DC",
    #     "",
    #     "Temperatures - WCT",  # Empty title for spacing
    #     "",
    #     "Flows - q_c",
    #     "",
    #     "Flows - q_dc",
    #     "",
    #     "Flows - q_vm",
    #     ""
    # ]

    # vspacing = [vertical_spacing for _ in range(len(row_heights))]
    # idx = 0
    # for subplot_title, add_space in zip(subplot_titles, additional_space):
    #     # Add "add_space" additional vertical_spacing
    #     vspacing[idx] += vertical_spacing * add_space
    #     # Add one additional vertical_spacing if title
    #     vspacing[idx] += vertical_spacing if subplot_title else 0
    #
    #     idx+=1
    #
    # display(vspacing)

    # Test traces
    # traces_test = [
    #     go.Scatter(x=[1, 2, 3, 4, 5], y=[10, 12, 15, 13, 11]),
    #     go.Scatter(x=[1, 2, 3, 4, 5], y=[50, 45, 40, 35, 30]),
    #     go.Scatter(x=[1, 2, 3, 4, 5], y=[9, 3, 2, 11, 11])
    # ]


    rows = len(row_heights)

    cum_sum = float(sum(row_heights))
    heights = []
    for idx, h in enumerate(row_heights):
        height_ = (1.0 - vertical_spacing * (rows - 1)) * (h / cum_sum)
        heights.append(round(height_, 3))

    # print(heights)
    # print(sum(heights))

    domains = [];
    y2 = 0 - vertical_spacing
    for i in reversed(range(rows)):
        y1 = round(y2 + vertical_spacing, 3)
        y2 = round(y1 + heights[i], 3)
        domains.append((y1, y2))

    domains[-1] = (domains[-1][0], round(domains[-1][-1]))

    # display(domains)
    # display( [(tup[1] - tup[0]) for tup in domains] )

    # See plotly start_cell parameter
    domains.reverse()

    legends_layout = {}
    for legend_id in plt_config['legend'].keys():
        conf = plt_config['legend'][legend_id]
        color = color_palette[conf['bgcolor']] if conf['bgcolor'] in color_palette.keys() else conf['bgcolor']
        color = f"rgba({color},0.1)"

        legends_layout[legend_id] = dict(
            title=f"<b>{conf['title']}</b>",
            x=conf["x"], y=conf["y"],
            xref='paper', yref='paper',
            bgcolor=color,
            font=dict(size=default_fontsize)
        )

    fig = go.Figure()

    xaxes_settings = {}
    yaxes_settings = {}
    # yaxes_settings['yaxis'] = {'domain': domains(1)}

    shapes = []
    idx = 1
    for i, conf in zip(range(rows), plt_config['plots'].values()):
        # traces = copy.deepcopy(traces_test)

        axes_idx = idx if idx > 1 else ""
        xaxes_settings[f'xaxis{axes_idx}'] = dict(anchor=f'y{axes_idx}', matches='x' if idx > 1 else None,
                                                  showticklabels=True if i == rows - 1 else False,
                                                  tickcolor="rgba(0,0,0,0)" if i != rows - 1 else None)  # title= idx,
        title = conf.get('ylabels_left', [None])[0]  # Only one axis is supported anyway

        if conf.get('tigth_vertical_spacing', None):
            domain = (domains[i + 1][-1] + vertical_spacing / 3,
                      # Fill the space between the current and the next axis with some vertical_spacing
                      domains[i][-1])  # Not changed
        else:
            domain = domains[i]

        yaxes_settings[f'yaxis{axes_idx}'] = {"domain": domain, 'anchor': f'x{axes_idx}', 'title': title, 'showgrid': True}

        # Plot configuration
        # Add background color
        bg_color = conf.get("bg_color", None)
        bg_color = color_palette[bg_color] if bg_color in color_palette.keys() else bg_color
        shapes.append(
            dict(
                type="rect", xref=f"x{axes_idx} domain", yref=f"y{axes_idx} domain", opacity=0.1, layer="below",
                line_width=0,
                fillcolor=bg_color,
                x0=-0.01, x1=1.01,
                y0=-0.01, y1=1.01,
            ),
        )

        traces_right = conf.get('traces_right', [])
        overlaying_axis = f'y{idx if idx > 1 else ""}'  # Overlaying axis used to configure right axes

        # Add decision variables updates
        if plt_config.get('show_optimization_updates', True):
            for index, row in df_opt.iterrows():
                shapes.append(
                    dict(
                        type="rect", xref=f"x{axes_idx}", yref=f"y{axes_idx} domain", opacity=0.4, line_width=0,
                        # layer="below",
                        fillcolor="#deddda",
                        x0=index - datetime.timedelta(seconds=row["computation_time"]), x1=index,
                        y0=-0.01, y1=1.01,
                    ),
                )
        else:
            logger.info('Optimization updates not shown in plot, show_optimization_updates: false')


        # Active state plot
        if conf.get('show_active', False):
            if 'active_var_id' in conf.keys():
                active = df[conf['active_var_id']]
            else:
                raise ValueError('active_var_id must be specified in plot configuration if show_active is True')

            if 'active_color' in conf.keys():
                if conf['active_color'] in color_palette.keys():
                    color = color_palette[conf['active_color']]
                else:
                    logger.warning(f'Color {conf["active_color"]} not found in color_palette, using default color')
                    color = default_active_color['active']

                active_color = {'active': color, 'inactive': default_active_color['inactive']}
            else:
                active_color = default_active_color

            # Shift axes idx to +100 to avoid overlapping with other axes
            aux_idx = axes_idx + 100

            # Calculate times when the system changes state
            change_times = active.index[active.diff() != 0]
            change_times = change_times.insert(len(change_times), active.index[-1])

            # Make change_times index of active
            active = active.reindex(change_times, method='ffill')

            # Configure axis so that it's plotted between the current axes and the next one
            yaxes_settings[f'yaxis{aux_idx}'] = {'domain': (domains[i + 1][-1], domains[i][0] - vertical_spacing / 2),
                                                 'anchor': f'x{aux_idx}', 'showgrid': False, 'showticklabels': False,
                                                 'showline': False, 'zeroline': False, 'showspikes': False,
                                                 'fixedrange': True, 'tickcolor': "rgba(0,0,0,0)"}
            xaxes_settings[f'xaxis{aux_idx}'] = {'anchor': f'y{aux_idx}', 'matches': 'x', 'showticklabels': False,
                                                 'showgrid': False, 'showline': False, 'zeroline': False,
                                                 'showspikes': False, 'tickcolor': "rgba(0,0,0,0)"}

            # Add traces for every state change
            for i_act in range(1, len(active)):
                value = active.iloc[i_act]
                span = [active.index[i_act - 1], active.index[i_act]]

                height_active = .8 if value else 0.3
                color = active_color['active'] if value else active_color['inactive']

                # print(value, span, color)

                trace_active = \
                    go.Scatter(
                        x=span, y=[height_active, height_active],
                        name=conf['active_var_id'],
                        showlegend=False, fill='tozeroy', mode='none', fillcolor=f'rgba({color}, 0.6)',
                        xaxis=f'x{aux_idx}', yaxis=f'y{aux_idx}'
                    )

                fig.add_trace(trace_active)

        # Add left traces
        for trace_conf in conf['traces_left']:
            trace_color = trace_conf.get("color", None)
            color = color_palette[trace_color] if trace_color in color_palette.keys() else trace_color
            uncertainty = calculate_uncertainty(df[trace_conf['var_id']], trace_conf['instrument']) if trace_conf.get(
                "instrument", None) else None

            trace = \
                go.Scatter(
                    x=df.index, y=df[trace_conf['var_id']],
                    name=trace_conf['name'],
                    mode=trace_conf.get('mode', 'lines'),
                    line=dict(
                        color=color,
                        dash=trace_conf.get('dash', None),
                        width=trace_conf.get('width', None)
                    ),
                    showlegend=trace_conf.get('showlegend', True),
                    legend=trace_conf.get('legend', None),
                    xaxis=f'x{axes_idx}',
                    yaxis=f'y{idx}'
                )

            # Add uncertainty
            if uncertainty is not None:
                color_rgb = color_palette[trace_color + '_rgb'] if trace_color + '_rgb' in color_palette.keys() else color

                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df[trace_conf['var_id']] - uncertainty,
                        name=f"{trace_conf['name']} uncertainty lower bound",
                        fill=None, line=dict(color='rgba(255,255,255,0)'),
                        showlegend=False,
                        xaxis=f'x{axes_idx}', yaxis=f'y{idx}',
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df[trace_conf['var_id']] + uncertainty,
                        name=f"{trace_conf['name']} uncertainty",
                        fill='tonexty', fillcolor=f'rgba({color_rgb}, 0.1)',
                        line=dict(color='rgba(255,255,255,0)'),
                        showlegend=False,
                        xaxis=f'x{axes_idx}', yaxis=f'y{idx}',
                    )
                )

            fig.add_trace(trace)
            logger.info(
                f'Trace {trace_conf["name"]} added in yaxis{idx} (left), row {i + 1}, uncertainty: {True if uncertainty is not None else False}')

            # If right axis traces and specified in trace configuration, add arrow to indicate axis
            # If specified in configuration, maybe the right axis should not be a requirement?
            if len(traces_right) > 0 and trace_conf.get('axis_arrow', False):
                # trace = fig.data[0]
                fig.add_annotation(
                    x=trace.x[0] - datetime.timedelta(seconds=arrow_xrel_pos),
                    y=trace.y[0] * trace_conf.get('arrow_yrel_pos', 1.05),
                    arrowhead=2, arrowsize=1.5, arrowwidth=1,  # Arrow line width
                    arrowcolor=trace.line.color,  # Arrow color
                    ax=25, ay=0, xref=f'x{axes_idx}', yref=f'y{axes_idx}', showarrow=True,
                )

        idx += 1

        # Traces right
        if len(traces_right) > 0:
            if isinstance(traces_right[0], dict):
                axis_right_configs = [traces_right]  # Single right yaxis
            else:
                axis_right_configs = traces_right  # Multiple right yaxis

            for pos_idx, traces_config in enumerate(axis_right_configs):
                titles = conf.get('ylabels_right', [None] * len(traces_config))

                yaxes_settings[f'yaxis{idx}'] = dict(overlaying=overlaying_axis, side='right', showgrid=False,
                                                     anchor='free', position=yaxis_right_pos[pos_idx],
                                                     title=titles[pos_idx])

                for trace_idx, trace_conf in enumerate(traces_config):
                    # Add trace
                    trace_color = trace_conf.get("color", None)
                    color = color_palette[trace_color] if trace_color in color_palette.keys() else trace_color
                    uncertainty = calculate_uncertainty(df[trace_conf['var_id']],
                                                        trace_conf['instrument']) if trace_conf.get("instrument",
                                                                                                    None) else None

                    trace = \
                        go.Scatter(
                            x=df.index, y=df[trace_conf['var_id']],
                            name=trace_conf['name'],
                            mode=trace_conf.get('mode', 'lines'),
                            line=dict(color=color,
                                      dash=trace_conf.get('dash', None),
                                      width=trace_conf.get('width', None)),
                            showlegend=trace_conf.get('showlegend', True),
                            xaxis=f'x{axes_idx}',
                            yaxis=f'y{idx}'
                        )

                    # Add uncertainty
                    if uncertainty is not None:
                        color_rgb = color_palette[
                            trace_color + '_rgb'] if trace_color + '_rgb' in color_palette.keys() else color

                        fig.add_trace(
                            go.Scatter(
                                x=df.index, y=df[trace_conf['var_id']] - uncertainty,
                                name=f"{trace_conf['name']} uncertainty lower bound",
                                fill=None, line=dict(color='rgba(255,255,255,0)'),
                                showlegend=False,
                                xaxis=f'x{axes_idx}', yaxis=f'y{idx}',
                            )
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=df.index, y=df[trace_conf['var_id']] + uncertainty,
                                name=f"{trace_conf['name']} uncertainty",
                                fill='tonexty', fillcolor=f'rgba({color_rgb}, 0.1)',
                                line=dict(color='rgba(255,255,255,0)'),
                                showlegend=False,
                                xaxis=f'x{axes_idx}', yaxis=f'y{idx}',
                            )
                        )

                    fig.add_trace(trace)
                    logger.info(
                        f'Trace {trace_conf["name"]} added in yaxis{idx} (right), row {i + 1}, uncertainty: {True if uncertainty is not None else False}')

                    # Add arrow to indicate axis
                    if trace_conf.get('axis_arrow', False):
                        fig.add_annotation(
                            x=trace.x[-1] + datetime.timedelta(seconds=arrow_xrel_pos),
                            y=trace.y[-1] * trace_conf.get('arrow_yrel_pos', 1.05),
                            arrowhead=2, arrowsize=1.5, arrowwidth=1,  # Arrow line width
                            arrowcolor=trace.line.color,  # Arrow color
                            ax=-25, ay=0, xref=f'x{axes_idx}', yref=f'y{idx}', showarrow=True,
                        )

                # Add index for each right axis added
                idx += 1
        # else:
        #     idx+=1

    fig.update_layout(
        title_text=f"<b>{plt_config['title']}</b><br>{plt_config['subtitle']}</br>" if plt_config.get('title',
                                                                                                      None) else None,
        title_x=0.05,  # Title position, 0 is left, 1 is right
        height=height,
        width=width,
        plot_bgcolor='rgba(0,0,0,0)',
        # paper_bgcolor='rgba(0,0,0,0)',
        # title_text="Complex Plotly Figure Layout",
        # margin=dict(l=20, r=200, t=100, b=20, pad=5),
        margin=plt_config.get("margin", dict(l=20, r=200, t=100, b=20, pad=5)),
        **xaxes_settings,
        **yaxes_settings,
        **legends_layout,
        shapes=shapes,
        newshape=newshape_style,
    )
    fig.update_xaxes(domain=xdomain)

    # Add subplot titles
    axes_domains = []
    for ydomain in domains:
        axes_domains.append(xdomain)
        axes_domains.append(ydomain)

    plot_title_annotations = plotly._subplots._build_subplot_title_annotations(
        subplot_titles, axes_domains
    )
    fig.layout.annotations = fig.layout.annotations + tuple(plot_title_annotations)

    return fig
