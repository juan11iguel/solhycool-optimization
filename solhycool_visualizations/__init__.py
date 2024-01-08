from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import List, Literal
from loguru import logger
from .constants import color_palette, plt_colors, default_fontsize

def save_figure(fig: go.Figure, figure_name: str, figure_path: str | Path, formats: List[Literal['eps', 'png', 'svg']],
                width=600, height=800, scale=2) -> None:

    """ Save figures in different formats """

    for fmt in formats:
        if fmt not in ['eps', 'png', 'svg', 'html']:
            raise ValueError(f'Format {fmt} not supported')

        if fmt == 'html':
            fig.write_html(f'{figure_path}/{figure_name}.{fmt}', include_plotlyjs='cdn', full_html=False)
        else:
            fig.write_image(f'{figure_path}/{figure_name}.{fmt}', format=fmt, width=width, height=height, scale=scale)
            # plt.savefig(f'{figure_path}/{figure_name}.{fmt}', format=fmt)

        logger.info(f'Figure saved in {figure_path}/{figure_name}.{fmt}')


def costs_plot(df: pd.DataFrame) -> go.Figure:
    # Costs plot

    fig = go.Figure()

    # DC
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_dc"],
        name='DC',
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=1.5, color=color_palette['dc_green']),
        stackgroup='Ce'  # define stack group
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_dc_opt"] + df["Ce_wct_opt"] + df["Ce_c_opt"],
        name='Condenser (model)',
        mode='lines',
        line=dict(width=1, color=color_palette['c_blue'], dash='dashdot'),
    ))

    # WCT
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_wct"],
        name='WCT',
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=1.5, color=color_palette['wct_purple']),
        stackgroup='Ce'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_dc_opt"] + df["Ce_wct_opt"],
        name='WCT (model)',
        mode='lines',
        line=dict(width=1.5, color=color_palette['wct_purple'], dash='dashdot'),
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_c"],
        name='Condenser',
        hoverinfo='x+y',
        mode='lines',
        line=dict(width=1, color=color_palette['c_blue']),
        stackgroup='Ce'
    ))
    # Add Ce_dc_opt with a dash dot line, same color as Ce_dc but thinner
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_dc_opt"],
        name='DC (model)',
        mode='lines',
        line=dict(width=1.5, color=color_palette['dc_green'], dash='dashdot'),
    ))

    # Add total consumption thick line
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce"],
        name='Ce',
        mode='lines',
        line=dict(width=5, color=color_palette['yellow']),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Ce_opt"],
        name='Ce (model)',
        mode='lines',
        line=dict(width=2, color=color_palette['yellow'], dash='dashdot'),
    ))

    # Add the water consumption to the right axis
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Cw"],
        name='Cw',
        mode='lines',
        line=dict(width=5, color=color_palette['wct_purple']),
        yaxis='y2'
    ))

    fig.add_trace(go.Scatter(
        x=df.index, y=df["Cw_opt"],
        name='Cw (model)',
        mode='lines',
        line=dict(width=2, color=color_palette['wct_purple'], dash='dashdot'),
        yaxis='y2'
    ))

    fig.update_layout(
        # Configure axis
        xaxis=dict(title='Time'),
        yaxis=dict(title='Electricity consumption (kW<sub>e</sub>)'),
        yaxis2=dict(title='Water consumption (l/h)', showgrid=False, zeroline=False, overlaying='y', side='right'),

        # Configure legend
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
    )

    return fig