from scipy.special import sph_harm as spherical_harmonics
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, spherical_harmonics_values_matrix):
        coefficients = data[:, 2]
        return np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1)

    def cashing(self, data):
        data_types = [np.int32, np.int32, np.float64, np.float64]

        saved_calculations = np.zeros(l.size, dtype=data_types)

        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))

        for i in range(l):
            for j in range(-i, i):




        saved_calculations_array = np.array(saved_calculations)
        np.savetxt("cashing.txt", saved_calculations_array, delimiter=",")
