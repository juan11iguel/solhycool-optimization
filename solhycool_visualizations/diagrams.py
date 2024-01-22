from pathlib import Path
from typing import Literal
import math
import os
import logging
from lxml import etree
import base64
from loguru import logger

""" Global variables """

nsmap = {
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'cc': 'http://web.resource.org/cc/',
    'svg': 'http://www.w3.org/2000/svg',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xlink': 'http://www.w3.org/1999/xlink',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
}

# Diagram generation auxiliary functions
def round_to_nonzero_decimal(n):
    if n == 0:
        return 0
    sgn = -1 if n < 0 else 1
    scale = int(-math.floor(math.log10(abs(n))))
    if scale <= 0:
        scale = 1
    factor = 10 ** scale
    return sgn * math.floor(abs(n) * factor) / factor


def convert_to_float_if_possible(value):
    try:
        converted_value = float(value)
        return converted_value
    except ValueError:
        return value


def change_text(diagram, object_id, new_text):
    obj = diagram.xpath(f'//svg:g[@id="cell-{object_id}"]', namespaces=nsmap)

    for child in obj[0]:
        if child.tag.endswith('g'):
            for child2 in child:
                if child2.tag.endswith('text'):
                    child2.text = new_text
                    break

    return diagram


def get_y(x, xmin, xmax, ymin, ymax):
    return ((ymax - ymin) / (xmax - xmin)) * (x - xmin) + ymin


def adjust_icon(id, size, tag, value, unit, include_boundary=True, max_size=None, max_value=None):
    if unit == 'degree_celsius': unit = '⁰C'

    for child in tag[0]:
        # Adjust icon size
        if 'image' in child.tag:
            pos_x = child.get("x");
            pos_y = child.get("y")
            current_size = float(child.get("width"))
            delta_size = size - current_size

            child.set("width", str(size))
            child.set("height", str(size))

            pos_x = float(pos_x) - delta_size / 2
            pos_y = float(pos_y) - delta_size / 2

            child.set("x", str(pos_x))
            child.set("y", str(pos_y))

            # Add template-id property to be used later
            child.set("template-id", f'icon-{id}')

        # Add text
        if child.tag.endswith('g'):
            for child2 in child:
                if 'text' in child2.tag:
                    if isinstance(value, str):
                        child2.text = f'{value} {unit}'
                    elif isinstance(value, int):
                        child2.text = f'{value} {unit}'
                    else:
                        child2.text = f'{round_to_nonzero_decimal(value)} {unit}'

    # Add boundary circle
    if include_boundary:
        tag[0][0].addprevious(etree.fromstring(generate_boundary_circle(id, size, max_size, max_value, pos_x, pos_y)))
    return tag, pos_x, pos_y


def generate_boundary_circle(id, size_icon, size_boundary, max_value, pos_x, pos_y):
    x = pos_x + size_icon / 2
    y = pos_y + size_icon / 2

    return f"""
    <g id="boundary-{id}">
        <ellipse cx="{x}" cy="{y}" rx="{size_boundary / 2}" ry="{size_boundary / 2}" fill-opacity="0" fill="rgb(255, 255, 255)" stroke="#ececec" stroke-dasharray="3 3" pointer-events="all"/>
        <g fill="#ECECEC" font-family="Helvetica" font-size="10px">
        <text x="{x + size_boundary / 2}" y="{y}">{max_value:.0f}</text></g></g>
    """


def get_level(value, min_value, max_value):
    span = max_value - min_value
    if value < min_value + span / 3:
        level = 1
    elif value < min_value + 2 * span / 3:
        level = 2
    else:
        level = 3
    return level


def change_color_text(diagram, text_color, object_id):
    obj = diagram.xpath(f'//svg:g[@id="cell-{object_id}"]', namespaces=nsmap)

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
    binary_fc = open(image_path, 'rb').read()  # fc aka file_content
    base64_utf8_str = base64.b64encode(binary_fc).decode('utf-8')

    ext = image_path.split('.')[-1]
    if ext == 'svg': ext = 'svg+xml'
    dataurl = f'data:image/{ext};base64,{base64_utf8_str}'

    obj = diagram.xpath(f'//svg:g[@id="cell-{object_id}"]', namespaces=nsmap)

    # print(obj[0].attrib)

    for child in obj[0]:
        if 'image' in child.tag:
            child.set('{http://www.w3.org/1999/xlink}href', dataurl)

    return diagram


def generate_diagram(src_diagram_path: Path, case_study: dict, theme='light'):

    # Load source diagram
    with open(src_diagram_path, 'r') as f:
        diagram = etree.parse(f)

    # Extract assets folder from the original diagram path
    folder_path = os.path.dirname(src_diagram_path)

    # Define some short names
    ptop = case_study['solutions'][ case_study['selected_solution_idx'] - 1 ] # -1 because MATLAB index starts at 1
    op_r = case_study["limits"]
    cr = case_study["cooling_requirements"]

    # Líneas
    lineas = [
        "line_c_in", "line_c_out", "line_r1", "line_dc_in", "line_dc_out",
        "line_r2_out1", "line_r2_out2", "line_wct_in", "line_wct_out", "line_pump_in"
    ]

    line_c_max = 15
    line_c_min = 10

    # Iconos
    iconos = [
        "cost_e_dc", "cost_e_wct", "cost_w_wct", "cooling_req", "fan_dc",
        "fan_wct", "temp_amb", "hr_amb", "temp_dc", "temp_wct", "valve_r1",
        "valve_r2"
    ]

    # Cuadros de texto
    textos = ["line_c_in_text", "line_c_out_text", "pump_c_text"]

    # Get objects to update in diagram
    tags = {}
    for object_ in lineas + iconos + textos:
        tags[object_] = diagram.xpath(f'//svg:g[@id="cell-{object_}"]', namespaces=nsmap)

        if not tags[object_]:
            raise ValueError(f'Object {object_} not found in diagram')

    # Modificar grosor de líneas
    x = ptop["q_c"];
    xmin = op_r["qc_min"];
    xmax = op_r["qc_max"];
    ymin = line_c_min;
    ymax = line_c_max
    line_width = get_y(x, xmin, xmax, ymin, ymax)
    for line in ["line_pump_in", "line_c_in", "line_c_out"]:
        tag = tags[line]

        # Línea y flecha
        for child in tag[0]:
            child.set("stroke-width", str(line_width))

    tag = tags["line_r1"]
    width_line_r1 = line_width * (ptop["R1"])
    # Línea y flecha
    for child in tag[0]:
        child.set("stroke-width", str(width_line_r1))

    width_line_dc = line_width * (1 - ptop["R1"])
    for line in ["line_dc_in", "line_dc_out"]:
        tag = tags[line]
        # Línea y flecha
        for child in tag[0]:
            child.set("stroke-width", str(width_line_dc))

    tag = tags["line_r2_out1"]
    width_r2_out1 = width_line_dc * (1 - ptop["R2"])
    # Línea y flecha
    for child in tag[0]:
        child.set("stroke-width", str(width_r2_out1))

    tag = tags["line_r2_out2"]
    width_line_r2_out2 = width_line_dc * (ptop["R2"])
    # Línea y flecha
    for child in tag[0]:
        child.set("stroke-width", str(width_line_r2_out2))

    for line in ["line_wct_in", "line_wct_out"]:
        tag = tags[line]
        # Línea y flecha
        for child in tag[0]:
            child.set("stroke-width", str(width_line_r1 + width_line_r2_out2))

    # Modificar tamaño de iconos y añadir template-id para texto

    # ["cost_e_dc", "cost_e_wct", "cost_w_wct", "cooling_req", "fan_dc",
    #  "fan_wct", "temp_amb", "hr_amb", "temp_wct", "temp_dc", "valve_r1",
    #  "valve_r2"]

    # tag_copy = deepcopy(tags)

    max_size = 70
    min_size = 30

    icon_ids = ["fan_dc", "fan_wct", "valve_r1", "valve_r2", "temp_amb", "hr_amb", "temp_wct", "temp_dc"]
    var_ids = ["w_dc", "w_wct", "R1", "R2", "Tamb", "HR", "Twct_out", "Tdc_out"]
    objs = [
        ptop, ptop, ptop, ptop, case_study["environment"], case_study["environment"], ptop, ptop
    ]
    units = ["%", "%", "", "", "degree_celsius", "%", "degree_celsius", "degree_celsius"]
    boundaries = [True, True, False, False, True, True, True, True]

    # Costes máximos y mínimos obtenidos a partir de resultados de optimización
    # Min=1e6; for i=1:2, for j=1:2, min_=min(results_total{i,j}.Pe); if min_<Min, Min=min_; end, end, end, disp(Min)
    # Max=1e-6; for i=1:2, for j=1:2, max_=max(results_total{i,j}.Pe); if max_>Max, Max=max_; end, end, end, disp(Max)

    # max_values = []
    # pos_xs = []; pos_ys = []
    for var_id, icon_id, obj, unit, boundary in zip(var_ids, icon_ids, objs, units, boundaries):
        tag = tags[icon_id];
        id_ = var_id
        x = obj[id_]
        xmin = op_r[id_ + '_min'];
        xmax = op_r[id_ + '_max'];
        ymin = min_size;
        ymax = max_size
        size = get_y(x, xmin, xmax, ymin, ymax)

        logging.debug(f'var_id: {var_id}, icon_id: {icon_id}, unit: {unit}, value: {obj[id_]}')

        # max_values.append(xmax)
        tag = adjust_icon(id_, size, tag, convert_to_float_if_possible(obj[id_]),
                          unit, include_boundary=boundary, max_size=max_size, max_value=xmax)
        # pos_xs.append(pos_x); pos_ys.append(pos_y)

    # Añadir valores para cuadros de texto

    # ["line_c_in_text", "line_c_out_text", "pump_c_text"]

    for text_box, var_id, group, unit in zip(["line_c_in_text", "line_c_out_text", "pump_c_text"],
                                             ["Tc_in", "Tc_out", "q_c"],
                                             [ptop, ptop, ptop],
                                             ["°C", "°C", "m³/h"]):

        tag = tags[text_box]
        for child in tag[0]:
            if child.tag.endswith('g'):
                for child2 in child:
                    if 'text' in child2.tag:
                        if unit == 'degree_celsius': unit = '⁰C'
                        child2.text = f'{round_to_nonzero_decimal(ptop[var_id])} {unit}'

    # Cooling requirements
    icon_id = 'cooling_req'
    tag = tags[icon_id];

    x = cr['Pth']
    xmin = op_r['Pth_min'];
    xmax = op_r['Pth_max']
    ymin = min_size;
    ymax = max_size
    size = get_y(x, xmin, xmax, ymin, ymax)
    value = f'{x:.0f} kWth, {cr["Mv"]:.2f} kg/s, {cr["Tv"]:.0f} ⁰C'

    tag = adjust_icon('cooling_req', size, tag, value, unit='', include_boundary=True, max_size=max_size,
                      max_value=xmax)

    # Costs icons and text values
    min_value = op_r['Ce_min']
    max_value = op_r['Ce_max']

    value = ptop['Ce_wct']
    level = get_level(value, min_value, max_value)
    image_path = os.path.join(folder_path, f'electrical_consumption_x{level}.svg')
    diagram = update_image(diagram, image_path, object_id='cost_e_wct')
    tag = tags['cost_e_wct']
    tag = adjust_icon('Ce_wct', 70, tag, value, 'kWe', include_boundary=False, max_size=None, max_value=None)

    value = ptop['Ce_dc']
    level = get_level(value, min_value, max_value)
    image_path = os.path.join(folder_path, f'electrical_consumption_x{level}.svg')
    diagram = update_image(diagram, image_path, object_id='cost_e_dc')
    tag = tags['cost_e_dc']
    tag = adjust_icon('Ce_dc', 70, tag, value, 'kWe', include_boundary=False, max_size=None, max_value=None)

    min_value = 0
    max_value = op_r['Cw_max']
    value = ptop['Cw_wct']
    level = get_level(value, min_value, max_value)
    image_path = os.path.join(folder_path, f'water_consumption_x{level}.svg')
    diagram = update_image(diagram, image_path, object_id='cost_w_wct')
    tag = tags['cost_w_wct']
    tag = adjust_icon('Cw_wct', 70, tag, value, 'l/h', include_boundary=False, max_size=None, max_value=None)

    # Change text for additional variables
    object_ids = ['Twct_in', 'qwct', 'qdc']
    values = [ptop['Twct_in'], ptop['q_wct'], ptop['q_dc']]
    units = ['°C', 'm³/h', 'm³/h']

    for object_id, value, unit in zip(object_ids, values, units):
        diagram = change_text(diagram, object_id, f'{round_to_nonzero_decimal(value)} {unit}')

    # Change background depending on theme
    if theme == 'dark':

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
            symbols_obj = diagram.xpath(f'//svg:g[@id="cell-juWprjBz31KtaNW54uK3-{i}"]', namespaces=nsmap)

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


def generate_facility_diagram(src_diagram_path: Path, case_study: dict, save_diagram: bool = False, output_path: Path = None,
                              theme:Literal['light', 'dark'] = 'light') -> etree.Element:

    diagram = generate_diagram(src_diagram_path, case_study, theme=theme)

    if save_diagram:
        with open(output_path, 'w') as diagram_file:
            diagram_file.write(etree.tostring(diagram).decode())

            logger.info(f'Diagram saved in {output_path}')

    return diagram
