from pathlib import Path
import numpy as np
from .calculator import Calculator


class Handler:
    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def processUserDataset(self, dpi: int, target_max_l: int, data: np.ndarray) -> np.ndarray:
        cache_dir = Path(__file__).resolve().parent / "cache"
        cache_dir.mkdir(exist_ok=True)

        file_name = f"DPI{dpi}L{target_max_l}.npy"
        file_path = cache_dir / file_name

        if self.checkForCachedSphericalHarmonics(file_path):
            return self.calculator.calculateMainMatrixFromData(data, self.loadSphericalHarmonicsFromCache(file_path)[:data.shape[0]], dpi)
        else:
            spherical_harmonics_matrices = self.calculator.calculateSphericalHarmonicsDataForSetDPI(dpi, target_max_l)
            self.cacheSphericalHarmonics(file_path, spherical_harmonics_matrices)
            return self.calculator.calculateMainMatrixFromData(data, self.loadSphericalHarmonicsFromCache(file_path)[:data.shape[0]], dpi)

    def checkForCachedSphericalHarmonics(self, file_path) -> bool:
        return file_path.exists()

    def cacheSphericalHarmonics(self, file_path, spherical_harmonics_matrices) -> None:
        np.save(file_path, spherical_harmonics_matrices, allow_pickle=True)

    def loadSphericalHarmonicsFromCache(self, file_path: Path) -> np.ndarray:
        return np.load(file_path, allow_pickle=True)
