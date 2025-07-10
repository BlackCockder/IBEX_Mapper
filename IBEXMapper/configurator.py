import numpy as np
from scipy.spatial.transform import Rotation as R
from .calculator import Calculator


class Configurator:
    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def convertSphericalToCartesianForPoints(self, vector_to_convert: np.ndarray) -> np.ndarray:
        lon = np.deg2rad(vector_to_convert[0])
        lat = np.deg2rad(vector_to_convert[1])
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        return np.array([x, y, z])

    def buildCenteringRotation(self, new_central_vector: np.ndarray) -> np.ndarray:
        if new_central_vector[0] == 0:
            new_central_vector[0] = 0.00000001
        if new_central_vector[1] == 0:
            new_central_vector[1] = 0.00000001
        current_vec = np.array([[1., 0., 0.]])
        target_vec = self.convertSphericalToCartesianForPoints(new_central_vector)
        target_vec = target_vec / np.linalg.norm(target_vec)

        rotation, _ = R.align_vectors(current_vec, target_vec)
        return rotation.as_matrix()

    def buildMeridianRotation(self, lon_lat_deg: np.ndarray, central_rotation: np.ndarray) -> np.ndarray:
        if lon_lat_deg[0] == 0:
            lon_lat_deg[0] = 0.00000001
        if lon_lat_deg[1] == 0:
            lon_lat_deg[1] = 0.00000001
        vec = self.convertSphericalToCartesianForPoints(lon_lat_deg)
        vec /= np.linalg.norm(vec)
        vec = central_rotation @ vec

        y, z = vec[1], vec[2]
        beta = np.arctan2(y, z)

        return R.from_euler("x", beta).as_matrix()
