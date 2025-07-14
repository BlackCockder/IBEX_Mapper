import numpy as np
from scipy.spatial.transform import Rotation as R
from .calculator import Calculator


class Configurator:
    """
    This class is responsible for building both rotations and handling elliptical coordinates edge cases (in calculations).
    """
    def __init__(self, calculator: Calculator):
        self.calculator = calculator
        
    def buildCenteringRotation(self, new_central_vector: np.ndarray) -> np.ndarray:
        """
        Method that calculates matrix that is responsible for rotating the grid in such way that user given vector
        gets placed at the center of mollweide projection map.

        :param new_central_vector:
        User given vector within range from (-180, -90) to (180, 90) (in degrees).
        Note: This vector's coordinates are verified outside this class.

        :return:
        Returns matrix that is calculated from given vector and angle formula for 3d rotations (rotation around given
        vector for given angle). Numerically it's a 3D numpy array.
        """

        # Cartesian equivalent of elliptical (0, 0) vector (we assume that the sphere has radius of 1)
        current_vec = np.array([[1., 0., 0.]])

        # Edge case correction, brute force way.
        new_central_vector = self.correctEllipticalVectorsEdgesCases(new_central_vector)

        # Convert and normalize the vector in cartesian
        target_vec = np.array(self.calculator.convertSphericalToCartesian(np.deg2rad(new_central_vector[0]), np.deg2rad(new_central_vector[1])))
        target_vec = target_vec / np.linalg.norm(target_vec)

        # Uses scipy.spatial.transform.Rotation to directly calculate the rotation matrix.
        # Angle is calculated internally from given vectors.
        rotation, _ = R.align_vectors(current_vec, target_vec)

        return rotation.as_matrix()

    def buildMeridianRotation(self, meridian_vector: np.ndarray, central_rotation: np.ndarray) -> np.ndarray:
        """
        Method that calculates the second rotation, which purpose is to place the meridian vector on the north
        part of meridian. The angle is derived from principle that we will need y coordinate of the vector after
        transforming it to cartesian and rotating it with first rotation to be equal to 0.
        Now, there are two solutions to this equation, so we use arctan2 function to make sure that the angle
        is always the "north angle".

        :param meridian_vector:
        User given vector within range from (-180, -90) to (180, 90) (in degrees).
        Note: This vector's coordinates are verified outside this class.

        :param central_rotation:
        The central rotation as a 3D numpy array matrix.

        :return:
        Returns the second rotation (meridian rotation) as a matrix. Numerically a 3D numpy array.
        """
        # Edge case correction, brute force way.
        meridian_vector = self.correctEllipticalVectorsEdgesCases(meridian_vector)

        # Convert and normalize the vector in cartesian
        meridian_vector_in_cartesian = self.calculator.convertSphericalToCartesian(np.deg2rad(meridian_vector[0]), np.deg2rad(meridian_vector[1]))
        meridian_vector_in_cartesian /= np.linalg.norm(meridian_vector_in_cartesian)

        # Rotate the vector using central rotation
        rotated_meridian_vector_in_cartesian = central_rotation @ meridian_vector_in_cartesian

        # Take y and z parts of the vector after central rotation and calculate the angle.
        # Note: The np.arctan2() function has a range of (-pi, pi) (used specifically to make sure that the given angle
        # aligns to "north").
        y, z = rotated_meridian_vector_in_cartesian[1], rotated_meridian_vector_in_cartesian[2]
        beta = np.arctan2(y, z)

        # Using simple from_euler method of scipy.spatial.transform.Rotations to construct the rotation matrix
        # around X axis and angle beta.
        return R.from_euler("x", beta).as_matrix()

    def correctEllipticalVectorsEdgesCases(self, vector_to_check: np.ndarray) -> np.ndarray:

        # Brute forcing the edge cases to agreed 8-digit cutoff range.
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
