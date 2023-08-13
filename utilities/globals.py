import hjson
import os

def init():
    global config
    
    with open(os.getenv('CONF_FILE', default=None), mode="r", encoding='utf-8') as file: 
        config = hjson.loads(file.read())
    