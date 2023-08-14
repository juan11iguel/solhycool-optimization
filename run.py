import os
from dash import Dash
from appshell import create_appshell
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# parser = argparse.ArgumentParser()
# parser.add_argument("--config_file", help="Configuration file path", default="webpage.hjson")
# args = parser.parse_args()

""" Global variables """
from utilities import globals
globals.init()

config = globals.config

scripts = [
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/locale/ru.min.js",
]

app = Dash(
    __name__,
    title=config.get("title", "Dashboard"),
    suppress_callback_exceptions=False,
    use_pages=True,
    external_scripts=scripts,
    update_title=None,
    url_base_pathname=config.get("url_base_pathname", "/"),
    assets_folder=os.path.join(os.getcwd(), "assets"),
)

app.layout = create_appshell(config)
server = app.server


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=config.get("port", 8050))