import numpy as np
import pandas as pd

# def save_figure(fig: go.Figure, figure_name: str, figure_path: str | Path, formats: List[Literal['eps', 'png', 'svg']],
#                 width=600, height=800, scale=2) -> None:
#
#     """ Save figures in different formats """
#
#     for fmt in formats:
#         if fmt not in ['eps', 'png', 'svg', 'html']:
#             raise ValueError(f'Format {fmt} not supported')
#
#         if fmt == 'html':
#             fig.write_html(f'{figure_path}/{figure_name}.{fmt}', include_plotlyjs='cdn', full_html=False)
#         else:
#             fig.write_image(f'{figure_path}/{figure_name}.{fmt}', format=fmt, width=width, height=height, scale=scale)
#             # plt.savefig(f'{figure_path}/{figure_name}.{fmt}', format=fmt)
#
#         logger.info(f'Figure saved in {figure_path}/{figure_name}.{fmt}')


def generate_tooltip_data(pr: pd.DataFrame):

    custom_data = np.stack((
        # Decision variables
        pr['q_c'].values,
        pr['q_dc'].values,
        pr['q_vm'].values,
        pr['Tdc_out'].values,
        pr['Twct_out'].values,

    ), axis=-1)

    # Build hover text
    # hover_text = f"""
    # <b>Decision variables</b><br>
    # - {cv['R1']['label']}: %{{customdata[0]:.2f}} {cv['R1']['unit']}<br>
    # - {cv['R2']['label']}: %{{customdata[1]:.2f}} {cv['R2']['unit']}<br>
    # - {cv['qc']['label']}: %{{customdata[2]:.1f}} {cv['qc']['unit']}<br>
    # - {cv['Tdc_out']['label']}: %{{customdata[3]:.1f}} {cv['Tdc_out']['unit']}<br>
    # - {cv['Twct_out']['label']}: %{{customdata[4]:.1f}} {cv['Twct_out']['unit']}<br>
    # """

    # TODO: do not hardcode label and units
    hover_text = f"""
<b>Decision variables</b><br>
    - q<sub>c</sub>: %{{customdata[0]:.2f}} m³/h<br>
    - q<sub>dc</sub>: %{{customdata[1]:.2f}} m³/h<br>
    - q<sub>vm</sub>: %{{customdata[2]:.1f}} m³/h<br>
    - T<sub>dc,out</sub>: %{{customdata[3]:.1f}} ºC<br>
    - T<sub>wct,out</sub>: %{{customdata[4]:.1f}} ºC<br>
C<sub>e</sub>: %{{y:.2f}} kW<sub>e</sub>, C<sub>w</sub>: %{{x:.2f}} l/h<extra></extra>
"""

    return custom_data, hover_text