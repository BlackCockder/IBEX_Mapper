from scipy.special import sph_harm_y_all as spherical_harmonics
import numpy as np
from pathlib import Path


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, spherical_harmonics_values_matrix):
        coefficients = data[:, 2]
        return np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1
                            
    def calculateSphericalHarmonicsDataForSetDPI(self, dpi, target_max_l):
        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))
        spherical_harmonics_array_on_real_plane = []
        unfiltered_array = spherical_harmonics(target_max_l, target_max_l, colatitude, longitude)
        for l in range(target_max_l + 1):
                for m in range(-l, l + 1):
                    if m < 0:
                        spherical_harmonic_positive = unfiltered_array[l][m]
                        spherical_harmonic_negative = unfiltered_array[l][-m]
                        spherical_harmonic_on_real_space = (1j / np.sqrt(2)) * (spherical_harmonic_positive - (((-1) ** abs(m)) * spherical_harmonic_negative))
                    elif m == 0:
                        spherical_harmonic_on_real_space = unfiltered_array[l][m]
                    else:
                        spherical_harmonic_positive = unfiltered_array[l][m]
                        spherical_harmonic_negative = unfiltered_array[l][-m]
                        spherical_harmonic_on_real_space = (1 / np.sqrt(2)) * (spherical_harmonic_negative + (((-1) ** abs(m)) * spherical_harmonic_positive))

                    spherical_harmonics_array_on_real_plane.append(spherical_harmonic_on_real_space.real)

        return spherical_harmonics_array_on_real_plane
                            
    def handleUserDataInput(self, dpi: int, target_max_l: int, data: np.ndarray) -> None:

        # checks if directory exists, otherwise creates it
        cache_dir = Path(__file__).resolve().parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        calculateSphericalHarmonicsDataForSetDPI(dpi, target_max_l)

        # names a file
        file_name = f"DPI{dpi}L{target_max_l}.npy"
        file_path = cache_dir / file_name

        # checks if file with proper name exists in the "cache" directory, otherwise creates it
        if file_path.is_file():
            matrices = np.load(file_path)
        else:
            #calculateSphericalHarmonicsDataForSetDPI(dpi, target_max_l)
            stacked_matrices = np.stack(matrices)
            stacked_matrices.tofile(file_path)
                            
                            
