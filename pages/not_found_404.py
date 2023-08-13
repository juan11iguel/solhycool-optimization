import dash
import dash_mantine_components as dmc
from dash_extensions import Lottie
import random
import glob

# Get a list of all the file paths in the assets folder that match the pattern "404-*.json"
file_paths = glob.glob("assets/404-*.json")

def layout():
    return dmc.Stack(
        align="center",
        justify="center",
        children=[
            Lottie(
                options=dict(loop=True, autoplay=True),
                isClickToPauseDisabled=True,
                # url="https://assets5.lottiefiles.com/packages/lf20_kcsr6fcp.json",
                url=random.choice(file_paths),
                width="100%",
            ),
            dmc.Text(
                [
                    "¿Realmente ha sido un accidente o querías ver otra animación?",
                    # dmc.Anchor(
                    #     "here",
                    #     underline=False,
                    #     href="https://github.com/snehilvj/dash-mantine-components/issues/new",
                    # ),
                    # ".",
                ],
                align="center",
            ),
            dmc.Anchor("Go back to home ->", href="/", underline=False),
        ],
    )

dash.register_page(__name__, path="/404")
