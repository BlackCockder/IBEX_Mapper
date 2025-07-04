from scipy.special import sph_harm_y_all as spherical_harmonics
import numpy as np
from pathlib import Path


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, spherical_harmonics_values_matrix, dpi):
        coefficients = data[:, 2]
        return np.roll(np.flipud(np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1).T), shift=dpi // 2, axis=1)
                            
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
                            
    def handleUserDataInput(self, dpi: int, target_max_l: int, data: np.ndarray) -> np.ndarray:
        cache_dir = Path(__file__).resolve().parent / "cache"
        cache_dir.mkdir(exist_ok=True)

        file_name = f"DPI{dpi}L{target_max_l}.npy"
        file_path = cache_dir / file_name

        if file_path.is_file():
            spherical_harmonics_matrices = np.load(file_path, allow_pickle=True)[:data.shape[0]]
        else:
            spherical_harmonics_matrices = self.calculateSphericalHarmonicsDataForSetDPI(dpi, target_max_l)
            np.save(file_path, spherical_harmonics_matrices, allow_pickle=True)
            spherical_harmonics_matrices = spherical_harmonics_matrices[:data.shape[0]]

        return self.calculateMainFunctionFromData(data, spherical_harmonics_matrices, dpi)
