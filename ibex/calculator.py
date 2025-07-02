from scipy.special import sph_harm as spherical_harmonics
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, spherical_harmonics_values_matrix):
        coefficients = data[:, 2]
        return np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1)










