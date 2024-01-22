# Pareto plot
import plotly
from plotly.validators.scatter.marker import SymbolValidator
from phd_visualizations.constants import color_palette, plt_colors, default_fontsize, newshape_style
import plotly.graph_objects as go
import pandas as pd
from . import generate_tooltip_data

symbols = SymbolValidator().values[2::12]
symbols_open = SymbolValidator().values[3::12]


def pareto_plot(opt_results: dict, Cws_max:tuple = (150, ), xlim:tuple = (-5, 210), ylim:tuple = (-0.5, 6),
                full_legend:bool = False) -> go.Figure:

    fig = go.Figure()

    # Add vertical area for values of Cw < 150
    for Cw_max in Cws_max:
        fig.add_shape(
            type="rect", xref="x", yref="paper",
            x0=-5, x1=Cw_max, y0=0, y1=1,
            fillcolor=color_palette["plotly_yellow"], opacity=0.2,
            layer="below", line_width=0,
        )


    # Add each pareto front with a different line style and mode line+markers
    for idx, case_study in enumerate(opt_results.values()):
        p = pd.DataFrame(case_study['solutions'])
        case_study['time'] = pd.to_datetime(case_study['time'], utc=True)
        cool_req = case_study['cooling_requirements']
        env_cond = case_study['environment']
        # Order by ascending Cw
        p.sort_values(by='Cw', inplace=True)

        if full_legend:
            name = f'{case_study["time"].strftime("%H:%M")} | T<sub>amb</sub>={env_cond["Tamb"]:.1f} ºC, ɸ={env_cond["HR"]:.0f} %, T<sub>v</sub>={cool_req["Tv"]:.1f} ºC, P<sub>th</sub>={cool_req["Pth"]:.0f} kW<sub>th</sub>'
        else:
            if idx == len(opt_results) - 1:
                name = f'{case_study["time"].strftime("%H:%M")} | T<sub>amb</sub>={env_cond["Tamb"]:.1f}, ɸ={env_cond["HR"]:.0f}, T<sub>v</sub>={cool_req["Tv"]:.1f}, P<sub>th</sub>={cool_req["Pth"]:.0f}'
            else:
                name = f'{case_study["time"].strftime("%H:%M")} | {env_cond["Tamb"]:.1f} ºC, {env_cond["HR"]:.0f} %, {cool_req["Tv"]:.1f} ºC, {cool_req["Pth"]:.0f} kW<sub>th</sub>'

        custom_data, hover_text = generate_tooltip_data(pr=p)

        fig.add_trace(
            go.Scatter(
                x=p["Cw"], y=p["Ce"],
                name=name,
                mode='lines+markers',
                line=dict(width=0.5, color=plt_colors[idx], dash='dot'),
                marker=dict(size=10, color=plt_colors[idx], symbol=symbols[idx], opacity=0.7),
                hovertemplate=hover_text, customdata=custom_data,
            )
        )

    # Add the points of the mono-objective optimization, with the same color as its line and using the variant of
    # the -open marker

    # for idx, row in enumerate(df_opt.iterrows()):
        fig.add_trace(
            go.Scatter(
                x=[p['Cw'][case_study['selected_solution_idx']-1]], y=[p['Ce'][case_study['selected_solution_idx']-1]],
                name=case_study["time"].strftime("%H:%M"),
                mode='markers', showlegend=False,
                marker=dict(size=20, color=plt_colors[idx], symbol=symbols_open[idx], opacity=0.7, line_width=3),
            )
        )

    fig.update_layout(
        # Configure axis
        xaxis=dict(title='Water consumption (l/h)', range=[xlim[0], xlim[1]], showspikes=True),
        yaxis=dict(title='Electricity consumption (kW<sub>e</sub>)', range=[ylim[0], ylim[1]], showspikes=True),
        # Fontsize
        font=dict(size=default_fontsize),
        newshape=newshape_style,
        # hovermode="x",
        # Configure legend
        legend=dict(
            # # Smaller font
            # font=dict(size=default_fontsize-2),
            # # orientation="h",
            yanchor="bottom",
            xanchor="left",
            x=0, y=0,
            bgcolor=f'rgba(255,255,255,0.5)',
            # font_color='white',
            # font=dict(),
            # entrywidth=0.7, # change it to 0.3
            # entrywidthmode='fraction',
        ),

        width=750,
        height=450,
        margin=dict(l=20, r=20, t=20, b=20, pad=5),
    )

    return fig
