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
        y: float = np.cos(lon) * np.sin(lat)
        z: float = np.sin(lat)
        return np.array([x, y, z])

    def buildCenteringRotation(self, new_central_vector: np.ndarray) -> np.ndarray:
        current_central_vector = np.array([1., 0., 0.])

        central_vector_in_cartesian = self.convertSphericalToCartesianForPoints(new_central_vector[0], new_central_vector[1])
        central_vector_in_cartesian /= np.linalg.norm(central_vector_in_cartesian)

        crossproduct_vector = np.cross(central_vector_in_cartesian, current_central_vector)
        crossproduct_vector /= np.linalg.norm(crossproduct_vector)

        alpha_in_degrees = np.clip(np.dot(central_vector_in_cartesian, current_central_vector), -1.0, 1.0)
        alpha_in_radians = np.arccos(alpha_in_degrees)

        return R.from_rotvec(alpha_in_radians * crossproduct_vector).as_matrix()

    def buildAligningRotation(self, lon_lat_deg: np.ndarray, central_rotation: np.ndarray) -> np.ndarray:
        vec = self.convertSphericalToCartesianForPoints(*lon_lat_deg)
        vec = central_rotation @ vec

        y, z = vec[1], vec[2]
        beta = -np.arctan2(y, z)

        return R.from_euler("x", beta).as_matrix()

