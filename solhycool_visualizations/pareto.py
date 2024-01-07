# Pareto plot
import plotly
from plotly.validators.scatter.marker import SymbolValidator
from constants import color_palette, plt_colors, default_fontsize
import plotly.graph_objects as go
import pandas as pd

symbols = SymbolValidator().values[2::12]
symbols_open = SymbolValidator().values[3::12]


def pareto_plot(opt_results: pd.DataFrame, ):
    fig = go.Figure()

    # Add vertical area for values of Cw < 150
    fig.add_shape(
        type="rect", xref="x", yref="paper",
        x0=-5, x1=150, y0=0, y1=1,
        fillcolor=color_palette["plotly_yellow"], opacity=0.2,
        layer="below", line_width=0,
    )

    # Add each pareto front with a different line style and mode line+markers
    for idx, p in enumerate(pareto_results):
        p = pd.DataFrame(p)
        p['time'] = pd.to_datetime(p['time'], utc=True)
        # Order by ascending Cw
        p.sort_values(by='Cw', inplace=True)

        if idx == len(pareto_results) - 1:
            name = f'{p.time[0].strftime("%H:%M")} | T<sub>amb</sub>={p["Tamb"][0]:.1f}, ɸ={p["HR"][0]:.0f}, T<sub>v</sub>={p["Tv"][0]:.1f}, P<sub>th</sub>={p["Pth"][0]:.0f}'
        else:
            name = f'{p.time[0].strftime("%H:%M")} | {p["Tamb"][0]:.1f}ºC, {p["HR"][0]:.0f}%, {p["Tv"][0]:.1f}ºC, {p["Pth"][0]:.0f}kW<sub>th</sub>'

        fig.add_trace(
            go.Scatter(
                x=p["Cw"], y=p["Ce"],
                name=name,
                mode='lines+markers',
                line=dict(width=0.5, color=plt_colors[idx], dash='dot'),
                marker=dict(size=10, color=plt_colors[idx], symbol=symbols[idx], opacity=0.7),
            )
        )

    # Add the points of the mono-objective optimization, with the same color as its line and using the variant of the -open marker
    for idx, row in enumerate(df_opt.iterrows()):
        fig.add_trace(
            go.Scatter(
                x=[row[1]['Cw']], y=[row[1]['Ce']],
                name=row[0].strftime("%H:%M"),
                mode='markers', showlegend=False,
                marker=dict(size=20, color=plt_colors[idx], symbol=symbols_open[idx], opacity=0.7, line_width=3),
            )
        )

    fig.update_layout(
        # Configure axis
        xaxis=dict(title='Water consumption (l/h)', range=[-5, 210]),
        yaxis=dict(title='Electricity consumption (kWh)'),
        # Fontsize
        font=dict(size=default_fontsize),
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

    fig.show()