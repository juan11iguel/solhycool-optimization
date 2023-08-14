
import os
import dash
import dash_mantine_components as dmc
from dash import dcc, html, Input, Output, State, callback
from dash_iconify import DashIconify
import hjson
import json
import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import random
from flask_caching import Cache

# with open('webpage.hjson', mode="r", encoding='utf-8') as file: config = hjson.loads(file.read())
from utilities import globals

""" Globals """
app = dash.get_app()
config = globals.config

dash.register_page(
    __name__,
    path="/optimization",
    title="solhycool - Optimization",
    description="One of the challenges related to solar thermal power plants is the high water consumption, "
    "which mainly comes from the cooling process of the power cycle. Combined cooling systems "
    "are presented as a potential solution to reduce water consumption, while also avoiding a high penalty "
    "due to efficiency loss in the power block. This paper analyzes the application of optimization strategies "
    "for a combined cooling system in order to evaluate the most suitable operating configuration according "
    "to different operating and environmental criteria. For this purpose, it has been necessary to carry out "
    "an exhaustive experimental campaign in a pilot plant at Plataforma Solar de Almería - CIEMAT, in order "
    "to train and obtain models based on neural networks. The potential of the optimization strategy is "
    "analyzed by simulating different case studies.",
    image="assets/logo.png"
)

with open(config["pareto_results_path"], mode="r", encoding='utf-8') as file: 
    results = json.loads(file.read())

if os.getenv("CACHE_TYPE", default="local") == "redis":
    cache = Cache(
            app.server,
            config={
                "CACHE_TYPE": "RedisCache",
                "CACHE_REDIS_HOST": "redis",
                "CACHE_REDIS_PORT": os.getenv("REDIS_PORT", default=6379),
            },
        )
else:
    cache = Cache(
        app.server, 
        config={
            'CACHE_TYPE': 'filesystem',
            'CACHE_DIR': config.get("CACHE_DIR", "tmp/"),

            # should be equal to maximum number of users on the app at a single time
            # higher numbers will store more data in the filesystem / redis cache
            'CACHE_THRESHOLD': 20
        }
    )


def create_figure():
    return go.Figure(
        {
            "data": [
                go.Bar(
                    x=list(range(10)),
                    y=[random.randint(200, 1000) for _ in range(10)],
                    name="SF",
                    marker={"line": {"width": 0}},
                    marker_color=dmc.theme.DEFAULT_COLORS["gray"][4],
                ),
                go.Bar(
                    x=list(range(10)),
                    y=[random.randint(200, 1000) for _ in range(10)],
                    name="Montréal",
                    marker={"line": {"width": 0}},
                    marker_color=dmc.theme.DEFAULT_COLORS["indigo"][4],
                ),
            ],
            "layout": go.Layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis={"showgrid": False, "zeroline": False, "visible": False},
                yaxis={"showgrid": False, "zeroline": False, "visible": False},
                showlegend=False,
            ),
        }
    )

def create_graph(id):
    return dcc.Graph(figure=create_figure(), config={"displayModeBar": False}, id=id)

def create_title(title, id):
    return dmc.Text(title, align="center", style={"fontSize": 40}, id=id)

def create_section_title(title, id):
    return dmc.Text(title, align="left", style={"fontSize": 20}, id=id, weight=700, mb=20)

def create_item(text):
    return dmc.Text(f'• {text}', align="left", my=10, mx=0)

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


layout = html.Div(
    [
        dmc.Container(
            size="lg",
            mt=30,
            children=[
                create_section_title("Environment", id="environment",),
                create_item("Ambient temperature (Tamb, ºC)"),
                dmc.SegmentedControl(
                    color="blue",
                    size='sm',
                    data = [str(value) for value in config["variables"]["Tamb"]["values"]],
                    orientation="horizontal",
                    fullWidth=True,
                    mx=30,
                    id="segmented_control_Tamb",
                    value=str(config["variables"]["Tamb"]["values"][0]),
                ),
                
                create_item("Relative humidity (HR, %)"),
                dmc.SegmentedControl(
                    color="blue",
                    size='sm',
                    data = [str(value) for value in config["variables"]["HR"]["values"]],
                    orientation="horizontal",
                    fullWidth=True,
                    mx=30,
                    mb=50,
                    id="segmented_control_HR",
                    value=str(config["variables"]["HR"]["values"][0]),
                ),
                
                create_section_title("Cooling requirements", id="cooling_requirements",),
                create_item("Vapour temperature (Tv, ºC)"),
                dmc.SegmentedControl(
                    color="red",
                    size='sm',
                    data = [str(value) for value in config["variables"]["Tv"]["values"]],
                    orientation="horizontal",
                    fullWidth=True,
                    mx=30,
                    id="segmented_control_Tv",
                    value=str(config["variables"]["Tv"]["values"][0]),
                ),
                
                create_item("Thermal power (Pth, kWth)"),
                dmc.SegmentedControl(
                    color="red",
                    size='sm',
                    data = [str(value) for value in config["variables"]["Pth"]["values"]],
                    orientation="horizontal",
                    fullWidth=True,
                    mx=30,
                    mb=40,
                    id="segmented_control_Pth",
                    value=str(config["variables"]["Pth"]["values"][0]),
                ),
                
                dmc.Group(
                    [
                        dmc.Button("Evaluate", id='button_evaluate', leftIcon=DashIconify(icon="line-md:chevron-small-right", width=20)),
                        dmc.Button(
                            "Export results",
                            # variant="outline",
                            leftIcon=DashIconify(icon="line-md:download-loop", width=20),
                            disabled=True,
                        ),
                    ],
                    position="center",
                    mt=30,
                    mb=90,
                    mx=30,
                    
                    grow=True
                ),
                
                dcc.Loading(type="graph", children=[
                    dmc.Paper([], withBorder=True, id='pareto_container'),
                ]),
                dcc.Loading(type="graph", children=[
                    dmc.Paper(id='results_container', withBorder=True, mt=30, mb=30, px=40, py=20,
                            children=[
                                dmc.Text("Click on a point in the pareto front to generate the updated diagram", align="center", my=30, mx=0, weight=700, color='gray'),
                                dmc.Image(src="/assets/optimization_V1/diagrams/WASCOP-Resultados JJAA.svg", alt="wascop-diagram", 
                                            caption="Facility diagram with highlighted components and flow paths", width="100%",
                                            withPlaceholder=True, placeholder=[dmc.Loader(color="gray", size="sm")]
                                )
                                ]
                            )
                ]),
            ],
        ),
    ]
)

# Cache this callback
# Callback to update results visualization
@callback(
    Output("pareto_container", "children"),
    Input("button_evaluate", "n_clicks"),
    State("segmented_control_Tamb", "value"),
    State("segmented_control_HR", "value"),
    State("segmented_control_Tv", "value"),
    State("segmented_control_Pth", "value"),
    State("theme-store", "data"),
    # prevent_initial_call=True,
)
@cache.memoize()
def update_pareto(n_clicks, Tamb_str, HR_str, Tv_str, Pth_str, current_theme):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    current_theme = current_theme['colorScheme']
    
    if not n_clicks:
        return [
            dmc.Text("Press evaluate to see the results", align="center", mt=30, mx=0, weight=700, color='gray'),
            dcc.Graph(figure=go.Figure(layout={'xaxis':{'title':'Water consumption (L/h)'}, 'yaxis':{'title':'Electrical consumption (kWe)'},
                                               'title': 'Pareto front', 'template': 'ggplot2' if current_theme=='light' else 'plotly_dark'},
                                      ),
                                      config={"displayModeBar": False}, id='pareto_front_plot')  
        ]
    
    # Evaluate validity of input values
    # Convert values to float
    Tamb = float(Tamb_str); HR = float(HR_str); Tv = float(Tv_str); Pth = float(Pth_str)
    if Tv<=Tamb:
        return [dmc.Text("Tv must be greater than Tamb", align="center", my=30, mx=0, weight=700, color='red')]
    
    # Build point id from input values
    opcond_id = f'Tamb{Tamb_str}_HR{HR_str}_Tv{Tv_str}_Pth{Pth_str}'
    
    if opcond_id not in results.keys():
        return [dmc.Text("Results not available, please try with a different combination of operation conditions", 
                         align="center", my=30, mx=0, weight=700, color='red')]
    
    # Get data
    raw_data = pd.read_csv( os.path.join( config["raw_data_path"], opcond_id+'.csv') )
    pareto_data = []
    for ptop in results[opcond_id]:
        pareto_data.append( flatten_dict( results[opcond_id][ptop] ) ) 
    
    pareto_data = pd.DataFrame(pareto_data)
    # Order pareto data by increasing values of Cw
    pareto_data = pareto_data.sort_values(by=['costs_Cw'])
    
    
    fig = go.Figure( 
                layout={
                    'xaxis':{'title':'Water consumption (L/h)'}, 
                    'yaxis':{'title':'Electrical consumption (kWe)'},
                    'title': f"Pareto Front for Tv={Tv}ºC and Pth={Pth}kWth, Tamb={Tamb}ºC and HR={HR}%",
                    'legend':{
                        'orientation':'h',  # Horizontal orientation
                        'x':0.4,  # X position of the legend (0.5 centers it)
                        'y':1,  # Y position of the legend (1.1 places it above the plot)
                     },
                    'template': 'ggplot2' if current_theme=='light' else 'plotly_dark'
                }
    )

    
    # Add cloud of operation points with x symbols, grey colors and alpha 70%
    fig.add_trace(
        go.Scatter(
            x=raw_data['Cw'], y=raw_data['Ce'], name='Evaluated op. points', mode='markers',
            marker=dict(
                symbol='x',  # Custom symbol for x
                opacity=0.7,  # Alpha (transparency)
                color=dmc.theme.DEFAULT_COLORS["gray"][4],  # Grey color
                line=None,  # No line
            )    
        ), 
    )

    pr = pareto_data
    cv = config["variables"]
    
    custom_data = np.stack((
        # Decision variables
        pr['decision_variables_R1'].values, 
        pr['decision_variables_R2'].values,
        pr['decision_variables_qc'].values,
        pr['decision_variables_Tdc_out'].values,   
        pr['decision_variables_Twct_out'].values,   
    ), axis=-1)
    
    # Build hover text
    hover_text = f"""
    <b>Decision variables</b><br>
    - {cv['R1']['label']}: %{{customdata[0]:.2f}} {cv['R1']['unit']}<br>
    - {cv['R2']['label']}: %{{customdata[1]:.2f}} {cv['R2']['unit']}<br>
    - {cv['qc']['label']}: %{{customdata[2]:.1f}} {cv['qc']['unit']}<br>
    - {cv['Tdc_out']['label']}: %{{customdata[3]:.1f}} {cv['Tdc_out']['unit']}<br>
    - {cv['Twct_out']['label']}: %{{customdata[4]:.1f}} {cv['Twct_out']['unit']}<br>
    """
    
    # Add pareto front with tooltip, rounded filled markers and alpha 100%
    fig.add_trace(go.Scatter(x=pareto_data['costs_Cw'], y=pareto_data['costs_Ce'], name='Pareto front', 
                             hovertemplate=hover_text, customdata=custom_data, mode='lines+markers',
                             marker=dict(
                                symbol='circle',  # Custom symbol
                                opacity=1,  # Alpha (transparency)
                                color=dmc.theme.DEFAULT_COLORS["blue"][4],  # Grey color
                                size=10,
                                line=dict(width=1, color='DarkSlateGrey')
                            )
                            )
                 ) 
    
    # Falta toda la parte de tooltips y demás
 
    return [dcc.Graph(figure=fig, id='pareto_front_plot')]


# Cache this callback
@callback(
    Output("results_container", "children"),
    Input("pareto_front_plot", "clickData"),
    State("segmented_control_Tamb", "value"),
    State("segmented_control_HR", "value"),
    State("segmented_control_Tv", "value"),
    State("segmented_control_Pth", "value"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
@cache.memoize()
def update_results(clickedData, Tamb_str, HR_str, Tv_str, Pth_str, current_theme):
    # changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if not clickedData: return dash.no_update
    
    current_theme = current_theme['colorScheme']
    
    # Evaluate validity of input values
    # Convert values to float
    Tamb = float(Tamb_str); HR = float(HR_str); Tv = float(Tv_str); Pth = float(Pth_str)
    if Tv<=Tamb:
        return dash.no_update
    
    
    # Build point id from input values
    opcond_id = f'Tamb{Tamb_str}_HR{HR_str}_Tv{Tv_str}_Pth{Pth_str}'
    
    # Identify operation point from selected data
    cd = clickedData['points'][0]['customdata']
    R1 = round(cd[0]*100)
    R2 = round(cd[1]*100)
    qc = round(cd[2], 1)
    Tdc_out = round(cd[3], 1)
    Twct_out = round(cd[4], 1)
    
    ptop_id = f'R1{R1}_R2{R2}_mc{qc}_Tdc{Tdc_out}_Twct{Twct_out}'
    
    if opcond_id not in results.keys():
        return dash.no_update
    if ptop_id not in results[opcond_id].keys():
        return dash.no_update
    
    diagram_name = opcond_id+'_'+ptop_id+'.svg' if current_theme=='light' else opcond_id+'_'+ptop_id+'_dark.svg'
    diagram_path = os.path.join('assets', 'optimization_V1', 'diagrams')
    
    # Check if the dark version is not available and try the light version instead
    if current_theme == 'dark' and diagram_name not in os.listdir(diagram_path):
        diagram_name = diagram_name.replace("_dark", "")
        
    if diagram_name not in os.listdir(diagram_path):
        diagram = dmc.Text("Diagram not available for selected operation point", align="center", my=30, mx=0, weight=700, color='red')


    else:
        caption = f"""Facility diagram with highlighted components and flow paths for cooling requirements: Tv={Tv}ºC and Pth={Pth}kWth,
        environment conditions: Tamb={Tamb}ºC and HR={HR}% and decision variables: R1={R1}, R2={R2}, Qc={qc} m³/h, Tdc,out={Tdc_out} ºC and Twct,out={Twct_out} ºC."""
        
        diagram = dmc.Image(src=os.path.join(diagram_path, diagram_name), alt="wascop-diagram", 
                                             caption=caption, width="100%",
                                             withPlaceholder=True, placeholder=[dmc.Loader(color="gray", size="sm")]
                                            ) 
    
    # data = results[opcond_id][ptop_id]
    
    # # cooling_power
    # flattened_dict = flatten_dict(data)
    # # costs_dict = {k: v for k, v in flattened_dict.items() if k.startswith('costs_Ce_')}

    # df_costs = pd.DataFrame.from_dict(costs_dict, orient='index', columns=['value'])

    
    # header_group = dmc.Group(
    #     [
    #         # Cooling power plot
    #         dcc.Grap(px.pie(df, values='pop', names='country', title='Population of European continent')),
    #         # Electrical consumption plot
    #         dcc.Graph(px.pie(df, values='pop', names='country', title='Population of European continent')),
    #         # Sinkey diagram
    #         dcc.Graph(
    #             go.Figure(
    #                 data=[
    #                     go.Sankey(
    #                         node = dict(
    #                             pad = 15,
    #                             thickness = 20,
    #                             line = dict(color = "black", width = 0.5),
    #                             label = ["A1", "A2", "B1", "B2", "C1", "C2"],
    #                             color = "blue"
    #                         ),
    #                         link = dict(
    #                             source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
    #                             target = [2, 3, 3, 4, 4, 5],
    #                             value = [8, 4, 2, 8, 4, 2]
    #                         )
    #                     )
    #                 ],
    #                 )
    #         ),
    #     ],
    #     position="apart",
    #     mx=30,
    # )
    
    
    layout = dmc.Stack(
        [
            # Plots at top
            # header_group,
            # Diagram
            diagram
        ],
        align="center",
        mt=30,
    )
    
    return layout