from scipy.special import sph_harm_y_all as spherical_harmonics
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, spherical_harmonics_values_matrix):
        coefficients = data[:, 2]
        return np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1)

    def calculateSphericalHarmonicsDataForSetDPI(self, dpi, target_max_l):
        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))
        spherical_harmonics_array_on_real_plane = []
        unfiltered_array = spherical_harmonics(target_max_l, target_max_l, colatitude, longitude)
        for l in range(target_max_l + 1):
            for m in range(-target_max_l, target_max_l + 1):
                spherical_harmonics_pos_m_value = unfiltered_array[l][m]
                spherical_harmonics_neg_m_value = unfiltered_array[l][-m]
                if m < 0:
                    recalculated_real = (1j / np.sqrt(2)) * (spherical_harmonics_pos_m_value - (-1) ** m * spherical_harmonics_neg_m_value)
                elif m == 0:
                    recalculated_real = unfiltered_array[l][m]
                else:
                    recalculated_real = (1 / np.sqrt(2)) * (spherical_harmonics_neg_m_value + (-1) ** m * spherical_harmonics_pos_m_value)

                spherical_harmonics_array_on_real_plane.append(recalculated_real.real)

        return spherical_harmonics_array_on_real_plane
    