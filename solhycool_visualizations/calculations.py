from typing import Literal
import numpy as np

actuator_coefficients = {
    # Important: coefficients must be in order of increasing power
    # p(x) = c0 + c1 * x + c2 * x^2 + c3 * x^3 + ... + cn * x^n

    # Cuidado! En MATLAB se definieron al revés!
    'fan_wct': [189.4, -11.54, 0.4118],
    'fan_dc': [-295.6, 48.63, -2.2, 0.04761, -0.0002431],
    'pump_c': [227.8, -38.32, 5.763, 0.1461]
}

supported_actuators = Literal[tuple(actuator_coefficients.keys())]
supported_instruments = Literal['pt100', 'pt1000', 'humidity_capacitive', 'vortex_flow_meter', 'paddle_wheel_flow_meter']


def power_consumption(input: float | int | np.ndarray, actuator: supported_actuators) -> float | np.ndarray:
    """
    Calculate power consumption based on the input and actuator type.

    Parameters:
    - input (float, int, or np.ndarray): Input value(s) representing a unit.
    - actuator (Literal[tuple(actuator_coefficients.keys())]): Type of actuator.

    Returns:
    - float or np.ndarray: Power consumption in kilowatts (kW).

    Raises:
    - ValueError: If the actuator is not one of the supported types.
    """
    # input (unit) -> power (kW)

    coefficients = actuator_coefficients.get(actuator)
    if coefficients is None:
        raise ValueError(f'Actuator must be one of supported types: {supported_actuators}')

    # Calculate power using a generalized polynomial expression
    # power = sum(coeff * input ** order for order, coeff in enumerate(coefficients)) / 1000  # kW

    # Evaluate polynomial expression using numpy
    power = np.polynomial.polynomial.polyval(input, coefficients) / 1000

    return power

def calculate_uncertainty(value: float, instrument: supported_instruments) -> float:
    """
    Calculate uncertainty for a given value and instrument

    Source:
    Wet cooling tower performance prediction in CSP plants: a comparison between
    artificial neural networks and Poppe’s model
    """

    if instrument.lower() == 'pt100':
        return value * 0.005 + 0.03  # 0.5% of reading + 0.03ºC
    elif instrument.lower() == 'pt1000':
        return 0.5  # 0.5ºC
    elif instrument.lower() == 'humidity_capacitive':
        return 3  # 3%
    elif instrument.lower() == 'vortex_flow_meter':
        return 0.65e-2 * value  # 0.65% of reading
    elif instrument.lower() == 'paddle_wheel_flow_meter':
        return 0.5e-2 * 1.95 + 2.5e-2 * value  # 0.5% full scale + 2.5% of reading
    else:
        raise ValueError(f'Instrument {instrument} not supported, supported instruments are {supported_instruments}')