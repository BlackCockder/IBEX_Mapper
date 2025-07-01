from scipy.special import sph_harm as spherical_harmonics
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, dpi):
        latitude, longitude = np.meshgrid(np.linspace(0, 2*np.pi, dpi), np.linspace(0, np.pi, dpi))
        result_array = spherical_harmonics(data[:, 0], data[:, 1], latitude, longitude)
        return np.sum(data[:, 2] * result_array).real
