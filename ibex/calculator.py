from scipy.special import sph_harm as spherical_harmonics
import numpy as np
from pathlib import Path


class Calculator:
    def __init__(self):
        pass

    def calculateMainFunctionFromData(self, data, spherical_harmonics_values_matrix):
        coefficients = data[:, 2]
        return np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1)






















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
