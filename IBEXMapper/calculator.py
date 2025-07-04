from scipy.special import sph_harm_y_all as spherical_harmonics
import numpy as np
from pathlib import Path


class Calculator:
    def __init__(self):
        pass

    def calculateMainMatrixFromData(self, data, spherical_harmonics_values_matrix, dpi):
        coefficients = data[:, 2]
        return np.roll(np.flipud(np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1).T), shift=dpi // 2, axis=1)
                            
    def calculateSphericalHarmonicsDataForSetDPI(self, dpi, target_max_l):
        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))
        spherical_harmonics_array_on_real_plane = []
        unfiltered_array = spherical_harmonics(target_max_l, target_max_l, colatitude, longitude)
        for l in range(target_max_l + 1):
                for m in range(-l, l + 1):
                    spherical_harmonics_array_on_real_plane.append(
                        self.filterComplexNumbersFromSphericalHarmonics(
                            m,
                            unfiltered_array[l][m],
                            unfiltered_array[l][-m])
                        .real)

        return spherical_harmonics_array_on_real_plane

    def filterComplexNumbersFromSphericalHarmonics(self, m, spherical_harmonic_positive, spherical_harmonic_negative):
        if m < 0:
            return (1j / np.sqrt(2)) * (spherical_harmonic_positive - (((-1) ** abs(m)) * spherical_harmonic_negative))
        elif m == 0:
            return spherical_harmonic_positive
        else:
            return (1 / np.sqrt(2)) * (spherical_harmonic_negative + (((-1) ** abs(m)) * spherical_harmonic_positive))
