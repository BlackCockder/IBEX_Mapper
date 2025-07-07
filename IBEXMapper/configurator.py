import numpy as np
from scipy.spatial.transform import Rotation as R
from calculator import Calculator


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
        new_central_vector = new_central_vector / np.linalg.norm(new_central_vector)

        central_vector_in_cartesian: np.ndarray = self.convertSphericalToCartesianForPoints(new_central_vector[0], new_central_vector[1])

        crossproduct_vector: np.ndarray = np.cross(current_central_vector, central_vector_in_cartesian)

        alpha_in_degrees = np.clip(np.dot(current_central_vector, central_vector_in_cartesian), -1.0, 1.0)
        alpha_in_radians = np.arccos(alpha_in_degrees)

        return R.from_rotvec(alpha_in_radians * crossproduct_vector).as_matrix()

    def buildAligningRotation(self, vector_to_align: np.ndarray) -> np.ndarray:
        vector_to_align_in_cartesian = self.convertSphericalToCartesianForPoints(vector_to_align[0], vector_to_align[1])
        beta = np.arctan2(vector_to_align_in_cartesian[1], vector_to_align_in_cartesian[2])
        return R.from_euler("x", beta).as_matrix()
