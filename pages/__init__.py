import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc


def generate_nomenclature(config, style=''):
    
    def load_image(width):
        return dmc.Image(
            src='assets/nomenclature_image.svg',
            width=width,
            withPlaceholder=True,
            placeholder=[dmc.Loader(color="gray", size="sm")],
            caption="Nomenclature diagram",
        )
        
    nomenclature_text = ""
    for varName in config["variables"].keys():
        var = config["variables"][varName]
        nomenclature_text = nomenclature_text + f"- **{var['var_id']}** - {var['sensor_id']} ({var['unit']}): {var['description']}\n"


    if style=='vertical':
        content =  [
            dmc.MediaQuery(
                [
                    dmc.Stack(
                        children=[
                            load_image(width='60vw'), 
                            dcc.Markdown(nomenclature_text),
                        ],
                        align="center",
                        justify="center",
                        spacing='xl',
                    )
                ],
                largerThan='lg',
                styles={'display':'none'}
            ),
            
            dmc.MediaQuery(
                [
                    dmc.Stack(
                        children=[
                            load_image(width='80vw'), 
                            dcc.Markdown(nomenclature_text),
                        ],
                        align="center",
                        justify="center",
                        spacing='xl',
                    )
                ],
                smallerThan='lg',
                styles={'display':'none'}
            ),
        ]       
        # content = [
        #     dmc.Stack(
        #         [
        #             load_image(width='768px'),
        #             dcc.Markdown(nomenclature_text),
        #         ],
        #         justify='center',
        #         align='center',
                
        #     )
        # ]
    else:
       content =  [
                    dmc.MediaQuery(
                        [
                            dmc.Stack(
                                children=[
                                    load_image(width='80vw'), 
                                    dcc.Markdown(nomenclature_text),
                                ],
                                align="center",
                                justify="center",
                                spacing='xl',
                                
                            )
                        ],
                        largerThan='lg',
                        styles={'display':'none'}
                    ),
                    
                    dmc.MediaQuery(
                        [
                            dmc.Group(
                                [
                                    dcc.Markdown(nomenclature_text),
                                    load_image(width='100%'),
                                ],
                                position='apart',
                                grow=True,
                            )
                        ],
                        smallerThan='lg',
                        styles={'display':'none'}
                    ),
       ]        
        
    
    return dmc.Modal(
                title="Nomenclature",
                id="nomenclature-modal",
                opened=False,
                centered=True,
                zIndex=10000,
                overflow="outside",
                children=content,
                size='90vw'
            )