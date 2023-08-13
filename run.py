import dash
from dash import Dash
import os
from flask_caching import Cache
import hjson

from appshell import create_appshell

""" Global variables """
with open('webpage.hjson', mode="r", encoding='utf-8') as file: config = hjson.loads(file.read())

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
)


app.layout = create_appshell(config)
server = app.server

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": "redis",
        "CACHE_REDIS_PORT": config["REDIS_PORT"],
    },
)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=config.get("port", 8050))