from pathlib import Path
import numpy as np
from .calculator import Calculator


class Handler:
    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def processUserDataset(self, dpi: int, target_max_l: int, data: np.ndarray) -> np.ndarray:
        """
        Main function that generates data for heatmap before configuration is applied.

        :param dpi:
        Resolution of the map. Ranges from 0 to infinity but generally speaking the intended accuracy is around 720.

        :param target_max_l:
        Caching parameter. Ranges from 0 to infinity. Determines how deep will calculator calculate the spherical
        harmonics for. Intended value is one that user sets as default in the config.

        :param data:
        Matrix of (N, 3) size. Generally used for accessing 3rd column where the coefficients are located and for
        cutting the cached spherical harmonics data to match the row length for vectorized matrix multiplication in
        calculator.

        :returns:
        Returns (dpi, dpi) size matrix of data for heatmap.
        """

        # Generating file paths for potential caching
        cache_dir = Path(__file__).resolve().parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        file_name = f"DPI{dpi}L{target_max_l}.npy"
        file_path = cache_dir / file_name

        if self.checkForCachedSphericalHarmonics(file_path):
            # We can cut it directly here because in app.py there is data sanitization that checks whether the inputted
            # file and inputted max_l are properly defined (meaning always max_l >= count_of_rows).
            cached_spherical_harmonics = self.loadSphericalHarmonicsFromCache(file_path)[:data.shape[0]]

            return self.calculator.calculateMainMatrixFromData(data, cached_spherical_harmonics, dpi)
        else:
            spherical_harmonics_matrices = self.calculator.calculateSphericalHarmonicsDataForSetDPI(dpi, target_max_l)

            self.cacheSphericalHarmonics(file_path, spherical_harmonics_matrices)

            # Same assumption here as in line 39.
            cut_spherical_harmonics = spherical_harmonics_matrices[:data.shape[0]]

            return self.calculator.calculateMainMatrixFromData(data, cut_spherical_harmonics, dpi)

    def checkForCachedSphericalHarmonics(self, file_path) -> bool:
        return file_path.exists()

    def cacheSphericalHarmonics(self, file_path, spherical_harmonics_matrices) -> None:
        np.save(file_path, spherical_harmonics_matrices, allow_pickle=True)

    def loadSphericalHarmonicsFromCache(self, file_path: Path) -> np.ndarray:
        return np.load(file_path, allow_pickle=True)
