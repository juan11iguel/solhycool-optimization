import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Literal
from loguru import logger
from phd_visualizations.constants import color_palette, plt_colors, default_fontsize, newshape_style

def costs_pie_plot(df: pd.DataFrame, current_theme: Literal['light', 'dark'] = 'light') -> go.Figure:

    fig_pies = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])

    Ce = np.abs(df['costs_Ce_dc']) + np.abs(df['costs_Ce_wct']) + np.abs(df['costs_Ce_c'])

    # print(f'Ce_tot = {Ce:.1f}, Ce_dc = {df_s["costs_Ce_dc"]:.1f}, Ce_wct = {df_s["costs_Ce_wct"]:.1f}, Ce_c = {df_s["costs_Ce_c"]:.1f}')

    # Data for the first pie plot
    labels1 = ['DC', 'WCT', 'Pump']
    values1 = [np.abs(df['costs_Ce_dc']) / Ce * 100, np.abs(df['costs_Ce_wct'] / Ce * 100),
               np.abs(df['costs_Ce_c'] / Ce * 100)]
    title1 = f'Electrical power <br>({Ce:.1f} kWe)</br>'

    # Add first pie plot with legend, title, and labels/values inside slices
    fig_pies.add_trace(
        go.Pie(
            labels=labels1,
            values=values1,
            marker=dict(colors=['#82b468', '#9572a5', '#6c8ebf']),
            showlegend=False,
            title=title1,
            hole=.4,
            textposition='inside',
            texttemplate='<b>%{label}</b><br>%{value:.1f} %</br>',
            textinfo='label+percent',  # Display labels and percentages inside slices
            insidetextorientation='radial'  # Display text radially inside slices
        ),
        row=1, col=1
    )

    # m_dc = df['others_m_dc']
    # m_wct = df['others_m_wct']
    #
    # Tdc_out = df['decision_variables_Tdc_out']
    # Tdc_in = df['others_Tdc_in']
    # Twct_out = df['decision_variables_Twct_out']
    # Twct_in = df['others_Twct_in']

    # print(f'm_dc = {m_dc:.1f}, m_wct = {m_wct:.1f}, Tdc_out = {Tdc_out:.1f}, Tdc_in = {Tdc_in:.1f}, Twct_out = {Twct_out:.1f}, Twct_in = {Twct_in:.1f}')

    Pth_dc = (df['decision_variables_Tdc_out'] - df['others_Tdc_in']) * df['others_m_dc']
    Pth_wct = (df['decision_variables_Twct_out'] - df['others_Twct_in']) * df['others_m_wct']
    Pth_tot = Pth_dc + Pth_wct

    # Data for the second pie plot
    labels2 = ['DC', 'WCT']
    values2 = [Pth_dc / Pth_tot * 100, Pth_wct / Pth_tot * 100]
    title2 = f'Cooling power <br>({df["cooling_requirements_Pth"]} kWth)</br>'

    # Add second pie plot with legend, title, and labels/values inside slices
    fig_pies.add_trace(
        go.Pie(
            labels=labels2,
            values=values2,
            marker=dict(colors=['#82b468', '#9572a5']),
            showlegend=False,
            title=title2,
            hole=.4,
            textposition='inside',
            texttemplate='<b>%{label}</b><br>%{value:.1f} %</br>',
            textinfo='label+percent',  # Display labels and percentages inside slices
            insidetextorientation='radial'  # Display text radially inside slices
        ),
        row=1, col=2
    )

    # Update layout
    fig_pies.update_layout(
        title_text='Relative contribution of each component <br>to electricity consumption and cooling power </br>',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        autosize=True,
        margin=dict(t=50, b=0, l=5, r=5),
        template='ggplot2' if current_theme == 'light' else 'plotly_dark'
        # width=500
    )

    # Configure axis
    # xaxis = dict(title='Water consumption (l/h)', range=[xlim[0], xlim[1]], showspikes=True),
    # yaxis = dict(title='Electricity consumption (kW<sub>e</sub>)', range=[ylim[0], ylim[1]], showspikes=True),
    # # Fontsize
    # font = dict(size=default_fontsize),
    # newshape = newshape_style,
    # # hovermode="x",
    # # Configure legend
    # legend = dict(
    #     # # Smaller font
    #     # font=dict(size=default_fontsize-2),
    #     # # orientation="h",
    #     yanchor="bottom",
    #     xanchor="left",
    #     x=0, y=0,
    #     bgcolor=f'rgba(255,255,255,0.5)',
    #     # font_color='white',
    #     # font=dict(),
    #     # entrywidth=0.7, # change it to 0.3
    #     # entrywidthmode='fraction',
    # ),
    #
    # width = 750,
    # height = 450,
    # margin = dict(l=20, r=20, t=20, b=20, pad=5),

    return fig_pies

def costs_evolution_plot(df: pd.DataFrame) -> go.Figure:
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
        newshape=newshape_style,
    )

    return fig
