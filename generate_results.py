from copy import deepcopy
import json
import argparse
import math
import os
import logging
import re
from lxml import etree
# import xml.etree.ElementTree as ET
# from copy import deepcopy
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import base64


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Configure program arguments
parser = argparse.ArgumentParser()
parser.add_argument("--results_folder_path", help="Path to the folder where the results are saved")
# Source svg diagram
parser.add_argument("--src_diagram_path", help="Path to the original svg diagram")
# Generate dark variant
parser.add_argument("--dark_variant", default=False, help="Generate dark variant", type=bool)
# Destination svg diagram
# parser.add_argument("dst_diagrams_path", help="Path to the generated svg diagram")

args = parser.parse_args()

""" Global vaeriables """

nsmap = {
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'cc': 'http://web.resource.org/cc/',
    'svg': 'http://www.w3.org/2000/svg',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xlink': 'http://www.w3.org/1999/xlink',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
    }

# Whenever a change is detected, action is triggered after CHANGE_DELAY seconds
CHANGE_DELAY = os.getenv("CHANGE_DELAY", default=20)  # seconds

# After an action is triggered, it cannot be triggered again until COOLDOWN_PERIOD seconds have passed
COOLDOWN_PERIOD = os.getenv("COOLDOWN_PERIOD", default=60)  # seconds

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_change_time = 0
        self.last_action_time = 0

    def on_modified(self, event):
        if not event.is_directory:
            current_time = time.time()

            if current_time - self.last_change_time >= CHANGE_DELAY:
                self.last_change_time = current_time

                if current_time - self.last_action_time >= COOLDOWN_PERIOD:
                    logging.info(f"Detected change in {event.src_path}")
                    
                    results = generate_results_file()
                    generate_diagrams(results)
                    
                    self.last_action_time = current_time
                    
                    logging.info("Functions executed")

def generate_results_file():
    # Join the given folder path with a default filename 'results.json'
    results_path = os.path.join(args.results_folder_path, 'results.json')

    # Read existing JSON file, if it exists
    data = {}
    try:
        with open(results_path, 'r') as file:
            data = json.load(file)
            logging.info(f'File {results_path} loaded.')
    except FileNotFoundError:
        data = {}
        logging.warning(f'File {results_path} not found. Creating a new one.')
        
    # Gather all the results files in the folder that have a filename structure: 'ptop_*.json'
    ptop_files = [f for f in os.listdir(args.results_folder_path) if os.path.isfile(os.path.join(args.results_folder_path, f)) and f.startswith('ptop_') and f.endswith('.json')]


    for ptop_id in ptop_files:
        # Read the results file
        ptops_file_path = os.path.join(args.results_folder_path, ptop_id)
        with open(ptops_file_path, 'r') as file:
            ptop = json.load(file)
            
            # Check if environment and cooling requirements exist
            # Extract text from ptop_ to _R1 (not including ptop_ and _R1)
            env_cool_req_id = re.search(r'ptop_(.*?)_R1', ptop_id).group(1)
            
            if env_cool_req_id in data:
                logging.info(f'Adding new data to operation conditions {env_cool_req_id}')
            else:
                logging.info(f'Creating new operation conditions {env_cool_req_id}')
                data[env_cool_req_id] = {}
                
                
            # Check if the operation point exists
            # Extract text from _R1 to .json (including _R1 but not .json)
            optpt_id = 'R1' + re.search(r'_R1(.*?)\.json', ptop_id).group(1)
            
            if optpt_id in data[env_cool_req_id]:
                logging.info(f'Updating operation point {optpt_id}')
            else:
                logging.info(f'Creating new operation point {optpt_id}')
            
            data[env_cool_req_id][optpt_id] = ptop
            
        logging.debug(f'Saving operation point: {optpt_id}')
        
    # Write the serialized JSON to the file
    output_path = os.path.join( args.results_folder_path, 'results.json' )
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    logging.info(f'File {output_path} updated.')
        
    return data
        
        
# Diagram generation auxiliary functions
def round_to_nonzero_decimal(n):
    if n == 0:
        return 0
    sgn = -1 if n < 0 else 1
    scale = int(-math.floor(math.log10(abs(n))))
    if scale <= 0:
        scale = 1
    factor = 10**scale
    return sgn*math.floor(abs(n)*factor)/factor


def convert_to_float_if_possible(value):
    try:
        converted_value = float(value)
        return converted_value
    except ValueError:
        return value

def get_y(x, xmin, xmax, ymin, ymax):
    return ((ymax - ymin) / (xmax - xmin)) * (x - xmin) + ymin

def adjust_icon(id, size, tag, value, unit, include_boundary=True, max_size=None, max_value=None):
    
    if unit=='degree_celsius': unit= '⁰C'
    
    for child in tag[0]:
        # Adjust icon size
        if 'image' in child.tag:
            pos_x = child.get("x"); pos_y = child.get("y")
            current_size = float(child.get("width"))
            delta_size = size - current_size
            
            child.set("width", str(size))
            child.set("height", str(size))
            
            pos_x = float(pos_x)-delta_size/2
            pos_y = float(pos_y)-delta_size/2
            
            child.set("x", str(pos_x))
            child.set("y", str(pos_y))
            
            # Add template-id property to be used later
            child.set("template-id", f'icon-{id}')
            
        # Add text
        if child.tag.endswith('g'):
            for child2 in child:
                if 'text' in child2.tag:
                    if type(value) == str:
                        child2.text = f'{value} {unit}'
                    elif type(value) == int:
                        child2.text = f'{value} {unit}'
                    else:
                        child2.text = f'{round_to_nonzero_decimal(value)} {unit}'
                    
    # Add boundary circle
    if include_boundary:
        tag[0][0].addprevious(etree.fromstring( generate_boundary_circle(id, size, max_size, max_value, pos_x, pos_y) ))
    return tag, pos_x, pos_y

def generate_boundary_circle(id, size_icon, size_boundary, max_value, pos_x, pos_y):
    
    x = pos_x + size_icon/2
    y = pos_y + size_icon/2
    
    return f"""
    <g id="boundary-{id}">
        <ellipse cx="{x}" cy="{y}" rx="{size_boundary/2}" ry="{size_boundary/2}" fill-opacity="0" fill="rgb(255, 255, 255)" stroke="#ececec" stroke-dasharray="3 3" pointer-events="all"/>
        <g fill="#ECECEC" font-family="Helvetica" font-size="10px">
        <text x="{x+size_boundary/2}" y="{y}">{max_value:.0f}</text></g></g>
    """

def get_level(value, min_value, max_value):
    span = max_value - min_value
    if value < min_value + span/3:
        level = 1
    elif value < min_value + 2*span/3:
        level = 2
    else:
        level = 3
    return level

def change_color_text(diagram, text_color, object_id):
    obj = diagram.xpath(f'//svg:g[@id="cell-{object_id}"]',namespaces=nsmap)
    
    for child in obj[0]:
        # print(child.tag)
        if child.tag.endswith('g'):
            # In multiline text, the color is set in the group tag
            child.set('fill', text_color)
            for child_ in child:
                # print(child_.tag)
                if 'text' in child_.tag:
                    child_.set('fill', text_color)
                
    return diagram

def update_image(diagram, image_path, object_id):

    binary_fc       = open(image_path, 'rb').read()  # fc aka file_content
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')

    ext     = image_path.split('.')[-1]
    if ext == 'svg': ext = 'svg+xml'
    dataurl = f'data:image/{ext};base64,{base64_utf8_str}'

    obj = diagram.xpath(f'//svg:g[@id="cell-{object_id}"]',namespaces=nsmap)

    # print(obj[0].attrib)

    for child in obj[0]:
        if 'image' in child.tag:
            child.set('{http://www.w3.org/1999/xlink}href', dataurl)
                
    return diagram

def generate_diagram(diagram, ptop, theme='light'):
    
    # Extract assets folder from the original diagram path
    folder_path = os.path.dirname(args.src_diagram_path) 
    
    # Líneas
    lineas = ["line_c_in", "line_c_out", "line_r2", "line_dc_in", "line_dc_out",
            "line_r1_out1", "line_r1_out2", "line_wct_in", "line_wct_out", "line_pump_in"]

    line_c_max = 15
    line_c_min = 10

    # Iconos
    iconos = ["cost_e_dc", "cost_e_wct", "cost_w_wct", "cooling_req", "fan_dc", 
              "fan_wct", "temp_amb", "hr_amb", "temp_dc", "temp_wct", "valve_r1",
              "valve_r2"]

    # Cuadros de texto
    textos = ["line_c_in_text", "line_c_out_text", "pump_c_text"]
    
    # Define some short names
    op_r = ptop["operating_range"]
    dv = ptop["decision_variables"]
    
    # Get objects to update in diagram
    tags = {}
    for object_ in lineas + iconos + textos:
        tags[object_] = diagram.xpath(f'//svg:g[@id="cell-{object_}"]',namespaces=nsmap)
        
        if not tags[object_]:
            raise ValueError(f'Object {object_} not found in diagram')
        
    # Modificar grosor de líneas

    x = dv["qc"]; xmin = op_r["qc_min"]; xmax = op_r["qc_max"]; ymin = line_c_min; ymax = line_c_max
    line_width = get_y(x, xmin, xmax, ymin, ymax)
    for line in ["line_pump_in", "line_c_in", "line_c_out"]:
        tag = tags[line]
        
        # Línea y flecha
        for child in tag[0]:
            child.set("stroke-width", str(line_width))
            
    tag = tags["line_r2"]
    width_line_r2 = line_width*(1-dv["R2"])
    # Línea y flecha
    for child in tag[0]:
        child.set("stroke-width", str(width_line_r2))

    width_line_dc = line_width*(dv["R2"])
    for line in ["line_dc_in", "line_dc_out"]:
        tag = tags[line]
        # Línea y flecha
        for child in tag[0]:
            child.set("stroke-width", str(width_line_dc))

    tag = tags["line_r1_out1"]
    width_r1_out2 = width_line_dc*(1-dv["R1"])
    # Línea y flecha
    for child in tag[0]:
        child.set("stroke-width", str(width_r1_out2))        
            
    tag = tags["line_r1_out2"]
    width_line_r1_out2 = width_line_dc*(dv["R1"])
    # Línea y flecha
    for child in tag[0]:
        child.set("stroke-width", str(width_line_r1_out2))    
                
    for line in ["line_wct_in", "line_wct_out"]:
        tag = tags[line]
        # Línea y flecha
        for child in tag[0]:
            child.set("stroke-width", str(width_line_r2 + width_line_r1_out2) )
    
    # Modificar tamaño de iconos y añadir template-id para texto

    # ["cost_e_dc", "cost_e_wct", "cost_w_wct", "cooling_req", "fan_dc", 
    #  "fan_wct", "temp_amb", "hr_amb", "temp_wct", "temp_dc", "valve_r1",
    #  "valve_r2"]

    # tag_copy = deepcopy(tags)

    max_size = 70
    min_size = 30

    icon_ids= ["fan_dc", "fan_wct", "valve_r1", "valve_r2", "temp_amb", "hr_amb", "temp_wct", "temp_dc"]
    var_ids = ["w_fan_dc", "w_fan_wct", "R1", "R2", "Tamb", "HR", "Twct_out", "Tdc_out"]
    groups  = ["control_variables", "control_variables", "decision_variables", "decision_variables", "environment", "environment", "decision_variables", "decision_variables"]
    units   = ["%", "%", "", "", "degree_celsius", "%", "degree_celsius", "degree_celsius"]
    boundaries= [True,      True,      False,      False,      True,       True,     True, True]

    # Costes máximos y mínimos obtenidos a partir de resultados de optimización
    # Min=1e6; for i=1:2, for j=1:2, min_=min(results_total{i,j}.Pe); if min_<Min, Min=min_; end, end, end, disp(Min)
    # Max=1e-6; for i=1:2, for j=1:2, max_=max(results_total{i,j}.Pe); if max_>Max, Max=max_; end, end, end, disp(Max)

    # max_values = []
    # pos_xs = []; pos_ys = []
    for var_id, icon_id, group, unit, boundary in zip(var_ids, icon_ids, groups, units, boundaries):
        
        tag = tags[icon_id]; id_ = var_id
        x = ptop[group][id_]
        xmin = op_r[id_+'_min']; xmax = op_r[id_+'_max']; ymin = min_size; ymax = max_size
        size = get_y(x, xmin, xmax, ymin, ymax)
        
        logging.debug(f'var_id: {var_id}, icon_id: {icon_id}, group: {group}, unit: {unit}, value: {ptop[group][id_]}')
        
        # max_values.append(xmax)
        tag = adjust_icon(id_, size, tag, convert_to_float_if_possible(ptop[group][id_]), 
                          unit, include_boundary=boundary, max_size=max_size, max_value=xmax)
        # pos_xs.append(pos_x); pos_ys.append(pos_y)
        
    # Añadir valores para cuadros de texto

    # ["line_c_in_text", "line_c_out_text", "pump_c_text"]

    for text_box, var_id, group, unit in zip(["line_c_in_text", "line_c_out_text", "pump_c_text"], 
                                             ["Tc_in", "Tc_out", "qc"],
                                             ["others", "others", "decision_variables"],
                                             ["°C", "°C", "m3/h"]):
        
        tag = tags[text_box]
        for child in tag[0]:
            if child.tag.endswith('g'):
                for child2 in child:
                    if 'text' in child2.tag:
                        if unit == 'degree_celsius': unit = '⁰C'
                        
                        child2.text = f'{round_to_nonzero_decimal( ptop[group][var_id] )} {unit}'
            
            
    # Cooling requirements
    icon_id = 'cooling_req'
    tag = tags[icon_id];

    cr = ptop["cooling_requirements"]

    x = cr['Pth'] 
    xmin = op_r['Pth_min']; xmax = op_r['Pth_max']
    ymin = min_size; ymax = max_size
    size = get_y(x, xmin, xmax, ymin, ymax)
    value = f'{x:.0f} kWhth, {cr["Mv"]:.2f} kg/s, {cr["Tv"]:.0f} ⁰C'

    tag = adjust_icon('cooling_req', size, tag, value, unit='', include_boundary=True, max_size=max_size, max_value=xmax)
    
    # Costs icons and text values
    min_value = op_r['Ce_min']
    max_value = op_r['Ce_max']

    value = ptop['costs']['Ce_wct']
    level = get_level(value, min_value, max_value)
    image_path = os.path.join(folder_path, f'electrical_consumption_x{level}.svg')
    diagram = update_image(diagram, image_path, object_id='cost_e_wct')
    tag = tags['cost_e_wct']
    tag = adjust_icon('Ce_wct', 70, tag, value, 'kWhe', include_boundary=False, max_size=None, max_value=None)

    value = ptop['costs']['Ce_dc']
    level = get_level(value, min_value, max_value)
    image_path = os.path.join(folder_path, f'electrical_consumption_x{level}.svg')
    diagram = update_image(diagram, image_path, object_id='cost_e_dc')
    tag = tags['cost_e_dc']
    tag = adjust_icon('Ce_dc', 70, tag, value, 'kWhe', include_boundary=False, max_size=None, max_value=None)

    min_value = 0
    max_value = op_r['Cw_max']
    value = ptop['costs']['Cw_wct']
    level = get_level(value, min_value, max_value)
    image_path = os.path.join(folder_path, f'water_consumption_x{level}.svg')
    diagram = update_image(diagram, image_path, object_id='cost_w_wct')
    tag = tags['cost_w_wct']
    tag = adjust_icon('Cw_wct', 70, tag, value, 'L/h', include_boundary=False, max_size=None, max_value=None)
    
    # Change background depending on theme
    if theme=='dark':
        
        # Background image
        image_path = os.path.join(folder_path, 'background_dark.jpg')
        diagram = update_image(diagram, image_path, object_id='background-image')           
        # Logo gobierno
        image_path = os.path.join(folder_path, 'micin-uefeder-aei_letras_blancas.svg')
        diagram = update_image(diagram, image_path, object_id='logo-gobierno')      
        # Logo PSA
        image_path = os.path.join(folder_path, 'logo_psa_letras_blancas_sin_fondo.svg')
        diagram = update_image(diagram, image_path, object_id='logo-psa')
        
        # Symbols legend box
        for i in range(28, 57):
            symbols_obj = diagram.xpath(f'//svg:g[@id="cell-juWprjBz31KtaNW54uK3-{i}"]',namespaces=nsmap)

            if len(symbols_obj) == 0:
                continue
            
            # print(symbols_obj[0].attrib)

            for child in symbols_obj[0]:
                # print(child.tag)
                
                # Update background color
                if 'rect' in child.tag and len(symbols_obj[0]) == 1:
                    # print('changing background of legend box')
                    child.set('fill', '#333333')
                    child.set('stroke', '#ECECEC')
                    
                    
                # Change text color
                if 'g' in child.tag and not 'rect' in child.tag:
                    for child_ in child:
                        if 'text' in child_.tag:
                            child_.set('fill', '#ECECEC')
               
        # Title
        diagram = change_color_text(diagram, text_color='#ECECEC', object_id='titulo')

        # Subtitle
        diagram = change_color_text(diagram, text_color='#ECECEC', object_id='subtitulo')
        
    return diagram
        
def generate_diagrams(results):

    diagram_file = args.src_diagram_path
    output_folder = os.path.join(args.results_folder_path, 'diagrams')
    
    # Load source diagram
    with open(diagram_file, 'r') as f:
        diagram = etree.parse(f)
        
    # From the results file, identify operation points which already have a generated diagram
    existing_diagram_files = os.listdir(output_folder)

    # Iterate over the operation points
    for op_cond in results:
        for ptop_ in results[op_cond]:
            ptop_id = f'{op_cond}_{ptop_}'
            
            if ptop_id in existing_diagram_files:
                logging.info(f'Diagram for operation point {ptop_id} already exists. Not generating a new one.')
                continue
            
            ptop = results[op_cond][ptop_]
            
            try:
                diagram_copy = deepcopy(diagram)
                diagram_light = generate_diagram(diagram_copy, ptop)
                
                if args.dark_variant:
                    diagram_copy = deepcopy(diagram)
                    diagram_dark = generate_diagram(diagram_copy, ptop, theme='dark')
                    
            except Exception as e:
                logging.error(f'Error generating diagram for operation point {ptop_id}.')
                logging.error(e)
                
            
            with open(os.path.join(output_folder, ptop_id+'.svg'), 'w') as diagram_file:
                diagram_file.write( etree.tostring(diagram_light).decode() )
                
            logging.info(f'Diagram for operation point {ptop_id} generated.')
            
            if args.dark_variant:
                with open(os.path.join(output_folder, ptop_id+'_dark.svg'), 'w') as diagram_file:
                    diagram_file.write( etree.tostring(diagram_dark).decode() )
                    
                logging.info(f'Dark variant of diagram for operation point {ptop_id} generated.')
        
    
    
if __name__ == '__main__':
    # Run program indefinitevily, watching for changes in folder and subfolders of results_folder_path, and then trigger functions
    
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=args.results_folder_path, recursive=True)
    observer.start()
    logging.info(f"Watching {args.results_folder_path} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
    
    logging.info("Program finished")
    # results = generate_results_file()
    # generate_diagrams(results)