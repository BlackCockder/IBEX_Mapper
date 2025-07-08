import numpy as np
from scipy.spatial.transform import Rotation as R
from .calculator import Calculator


class Configurator:
    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def convertSphericalToCartesianForPoints(self, lon: float, lat: float) -> np.ndarray:
        lon = np.deg2rad(lon)
        lat = np.deg2rad(lat)
        x: float = np.cos(lat) * np.cos(lon)
        y: float = np.cos(lat) * np.sin(lon)
        z: float = np.sin(lat)
        return np.array([x, y, z])

    def buildCenteringRotation(self, new_central_vector: np.ndarray) -> np.ndarray:
        current_vec = np.array([[1., 0., 0.]])
        target_vec = self.convertSphericalToCartesianForPoints(new_central_vector[0], new_central_vector[1])
        target_vec = target_vec / np.linalg.norm(target_vec)

        rotation, _ = R.align_vectors(current_vec, target_vec)
        return rotation.as_matrix()

    def buildMeridianRotation(self, lon_lat_deg: np.ndarray, central_rotation: np.ndarray) -> np.ndarray:
        vec = self.convertSphericalToCartesianForPoints(lon_lat_deg[0], lon_lat_deg[1])
        vec /= np.linalg.norm(vec)
        print(vec)
        vec = central_rotation @ vec
        print(vec)

        y, z = vec[1], vec[2]
        beta = np.arctan2(y, z)
        print("--------------------------------------------")
        print(R.from_euler("x", beta).as_matrix())
        print("--------------------------------------------")

        return R.from_euler("x", beta).as_matrix()

