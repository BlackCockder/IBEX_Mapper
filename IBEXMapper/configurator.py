import numpy as np
from scipy.spatial.transform import Rotation as R
from .calculator import Calculator


class Configurator:
    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def buildCenteringRotation(self, new_central_vector: np.ndarray) -> np.ndarray:
        current_vec = np.array([[1., 0., 0.]])
        new_central_vector = self.correctEllipticalVectorsEdgesCases(new_central_vector)
        target_vec = np.array(self.calculator.convertSphericalToCartesian(np.deg2rad(new_central_vector[0]), np.deg2rad(new_central_vector[1])))
        target_vec = target_vec / np.linalg.norm(target_vec)

        rotation, _ = R.align_vectors(current_vec, target_vec)
        return rotation.as_matrix()

    def buildMeridianRotation(self, meridian_vector: np.ndarray, central_rotation: np.ndarray) -> np.ndarray:
        meridian_vector_in_cartesian = self.calculator.convertSphericalToCartesian(np.deg2rad(meridian_vector[0]), np.deg2rad(meridian_vector[1]))
        meridian_vector_in_cartesian /= np.linalg.norm(meridian_vector_in_cartesian)
        rotated_meridian_vector_in_cartesian = central_rotation @ meridian_vector_in_cartesian

        y, z = rotated_meridian_vector_in_cartesian[1], rotated_meridian_vector_in_cartesian[2]
        beta = np.arctan2(y, z)

        return R.from_euler("x", beta).as_matrix()

    def correctEllipticalVectorsEdgesCases(self, vector_to_check: np.ndarray) -> np.ndarray:
        if vector_to_check[0] == 0:
            vector_to_check[0] = 0.00000001
        if vector_to_check[0] == -180:
            vector_to_check[0] = -179.99999999
        if vector_to_check[0] == 180:
            vector_to_check[0] = 179.99999999
        if vector_to_check[1] == 0:
            vector_to_check[1] = 0.00000001
        if vector_to_check[1] == -90:
            vector_to_check[1] = -89.99999999
        if vector_to_check[1] == 90:
            vector_to_check[1] = 89.99999999
        return vector_to_check
