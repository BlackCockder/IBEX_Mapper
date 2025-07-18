from scipy.special import sph_harm_y_all as spherical_harmonics
from scipy.interpolate import RegularGridInterpolator
import numpy as np


class Calculator:
    """
    Class that is responsible for all number work on spheres, matrices, complex numbers and more.
    """
    def __init__(self):
        pass

    def calculateMainMatrixFromData(self, data: np.ndarray, spherical_harmonics_values_matrix: np.ndarray, dpi: int) \
            -> np.ndarray:
        """
        Method that calculates main heatmap matrix by vectorized multiplying coefficient with relative value from
        spherical harmonics value matrix.

        :param data:
        A (N, 4) matrix of data given by user.

        :param spherical_harmonics_values_matrix:
        A (dpi, dpi) size matrix of values for corresponding coefficients that will be multiplied with the coefficients.

        :param dpi:
        Final size of matrix (dpi, dpi).
        Note: this parameter must always be the same for matrix given by :param spherical_harmonics_values_matrix: or
        else this will generate errors.

        :return:
        Returns the main matrix but also realigns it, so it has the same coordinate system as the one used in mollweide
        projection. Refer to the projection function in Projection class to see the ranges of the (x, y) matrix of
        coordinates.
        """

        print("Calculating heatmap data...")

        # Assuming that 3rd column is always the column with coefficients
        coefficients = data[:, 2]

        # A tensor dot product to multiply the equivalent coefficients with equivalent spherical harmonics
        # Transposed to switch from (lat, lon) to (lon, lat) system that is used in this app.
        main_matrix = np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1).T

        # Necessary matrix realignment to match mollweide projection
        final_matrix = np.roll(np.fliplr(main_matrix), shift=dpi // 2, axis=1)

        print("Heatmap data calculated")

        return final_matrix
                            
    def calculateSphericalHarmonicsDataForSetDPI(self, dpi: int, target_max_l: int) -> list:
        """
        Method that calculates all spherical harmonics up to given L border.

        :param dpi:
        Parameter that defines raster size of final heatmap on mollweide projection, here used to generate discrete
        values of colatitude and latitude

        :param target_max_l:
        Parameter that defines up to which L size the method will calculate spherical harmonics.
        Range is from 0 to infinity (realistically 30 is used).

        :return:
        Returns a list of calculated spherical harmonics. The convention used:
        [l_0_0, l_1_-1, l_1_0, l_1_1, l_2_-2, l_2_-1, ...]
        Each element is (dpi, dpi) size matrix of all spherical harmonics, used later as to form the discrete heatmap.
        """

        # Forms the discrete range of values for heatmap generation after.
        # The larger dpi is, the larger raster size will the final projection of heatmap have.
        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))

        # Initializing the final list of spherical harmonics.
        spherical_harmonics_array_on_real_plane = []

        print(f"Calculating spherical harmonics for L: {target_max_l}...")

        # Calculating all spherical harmonics up to given l and m sizes.
        # Note: This function also calculates invalid spherical harmonics (like l = 2 and m = 8), but it replaces them
        # with zero after.
        unfiltered_array = spherical_harmonics(target_max_l, target_max_l, colatitude, longitude)

        print("Calculated spherical harmonics")

        print("Filtering spherical harmonics...")

        # Helping variables with showing percentage of calculations done. Agreed step is 5%.
        total_iterations = sum(2 * l + 1 for l in range(target_max_l + 1))
        completed_iterations = 0
        progress_checkpoint = 0

        # We need to filter out the invalid spherical harmonics, double for loop does the job.
        for l in range(target_max_l + 1):
            for m in range(-l, l + 1):

                # Here we transform the spherical harmonics from complex plane to real plane using helper method.
                spherical_harmonics_array_on_real_plane.append(
                    self.filterComplexNumbersFromSphericalHarmonics(
                        m,
                        unfiltered_array[l][m],
                        unfiltered_array[l][-m])
                    .real)

                # Updating progress of filtering
                completed_iterations += 1
                current_progress = int((completed_iterations / total_iterations) * 100)
                if current_progress >= progress_checkpoint + 5:
                    progress_checkpoint = current_progress - (current_progress % 5)
                    print(f"Filtering progress: {progress_checkpoint}%")

        # Return the list.
        return spherical_harmonics_array_on_real_plane

    def filterComplexNumbersFromSphericalHarmonics(self,
                                                   m: float,
                                                   spherical_harmonic_positive: np.ndarray,
                                                   spherical_harmonic_negative: np.ndarray) -> np.ndarray:
        """
        Helper method that takes current state of for loop in method calculateSphericalHarmonicsDataForSetDPI and
        applies the equation of real plane transform to all spherical harmonics.
        Wikipedia link: https://en.wikipedia.org/wiki/Spherical_harmonics#Real_form

        :param m:
        Current m state of for loop.

        :param spherical_harmonic_positive:
        Positive value of currently calculated spherical harmonic.

        :param spherical_harmonic_negative:
        Negative value of currently calculated spherical harmonic.

        :return:
        Returns transformed value onto real plane of the spherical harmonics.
        """

        # Same as in the formula.
        if m < 0:
            return (1j / np.sqrt(2)) * (spherical_harmonic_positive - (((-1) ** abs(m)) * spherical_harmonic_negative))
        elif m == 0:
            return spherical_harmonic_positive
        else:
            return (1 / np.sqrt(2)) * (spherical_harmonic_negative + (((-1) ** abs(m)) * spherical_harmonic_positive))

    def convertSphericalToCartesian(self, lon: np.ndarray or float, lat: np.ndarray or float) \
            -> tuple[np.ndarray, np.ndarray, np.ndarray] or tuple[float, float, float]:
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        return x, y, z

    def convertCartesianToSpherical(self, x: np.ndarray or float, y: np.ndarray or float, z: np.ndarray or float)\
            -> tuple[np.ndarray, np.ndarray] or tuple[float, float]:
        lat = np.arcsin(z)
        lon = np.arctan2(y, x)

        # To prevent out of bounds bug for points.
        if isinstance(y, float):
            if abs(y) < 1e-10:
                lon = 0.0

        return lon, lat

    def rotateGridByRotation(self,
                             x_mesh: np.ndarray,
                             y_mesh: np.ndarray,
                             z_mesh: np.ndarray,
                             rotation: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Method that rotates a mesh of coordinates in cartesian by given rotation.

        :param x_mesh:
        A (N, N) size matrix of X coordinate values.

        :param y_mesh:
        A (N, N) size matrix of Y coordinate values.

        :param z_mesh:
        A (N, N) size matrix of Z coordinate values.
        :param rotation:
        A 3D rotation matrix.

        :return:
        Returns all meshes rotated with the given rotation matrix.
        """

        print("Rotating grid...")

        # Check shape before rotating to reshape the meshes back into meshes after rotation.
        original_shape = x_mesh.shape

        # We stack the meshes into (shape, shape) matrix of 3D vectors.
        cartesian_coordinates_matrix = np.stack((x_mesh, y_mesh, z_mesh), axis=-1).reshape(-1, 3)

        # Apply the rotation
        # Note, we apply the rotation here with transposing because numpy allows vectorized
        # matrix multiplications only when rotation matrix is on the "left side" of the equation.
        # So we need to transpose it.
        rotated_cartesian_coordinates_matrix = cartesian_coordinates_matrix @ rotation.T

        # Split the array back into 3 (shape, shape) meshes.
        rot_x_mesh = rotated_cartesian_coordinates_matrix[:, 0].reshape(original_shape)
        rot_y_mesh = rotated_cartesian_coordinates_matrix[:, 1].reshape(original_shape)
        rot_z_mesh = rotated_cartesian_coordinates_matrix[:, 2].reshape(original_shape)

        print("Grid rotated")

        return rot_x_mesh, rot_y_mesh, rot_z_mesh

    def interpolateDataForNewGrid(self,
                                  data_to_interpolate: np.ndarray,
                                  rotated_lat: np.ndarray,
                                  rotated_lon: np.ndarray) -> np.ndarray:
        """
        Method that given the original data matrix and the new grid system uses linear interpolation to form
        new value matrix that will be later projected in mollweide projection.
        Note: Despite this app using (lon, lat) convention, (lat, lon) is used here because it is required in this order
        by linear grid interpolator.

        :param data_to_interpolate:
        A (N, N) shaped matrix with real value entries.

        :param rotated_lat:
        Latitude part of new grid, as (N, N) size matrix of latitude coordinates.

        :param rotated_lon:
        Longitude part of new grid, as (N, N) size matrix of Longitude coordinates.

        :return:
        Returns a (N, N) shaped matrix with values, that comes from interpolating the initial data matrix with
        new coordinate system.
        """

        print("Interpolating new heatmap data after rotation...")

        # Get the N size.
        dpi = data_to_interpolate.shape[0]

        # We generate the lat and lon meshes of original matrix data.
        lat = np.linspace(np.pi / 2, -np.pi / 2, dpi)
        lon = np.linspace(np.pi, -np.pi, dpi)

        # Initialize the interpolator with data and initial lat and lon.
        interpolator = RegularGridInterpolator((lat, lon), data_to_interpolate,
                                               method='linear', bounds_error=False, fill_value=np.nan)

        # Stack the rotated_lat and rotated_lon meshes into a (N, N) size matrix of 2D vectors.
        rotated_vectors = np.stack((rotated_lat.ravel(), rotated_lon.ravel()), axis=-1)

        # Use the interpolator to interpolate our new grid system with old grid system and its corresponding data to get
        # our new data.
        interpolated_data = interpolator(rotated_vectors).reshape(rotated_lat.shape)

        print("Heatmap data interpolated")

        return interpolated_data

    def createCircle(self, circle_center_vector: np.ndarray, alpha: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Method that generates discrete values for drawing circles on the mollweide projection.

        :param circle_center_vector:
        The vector in elliptical coordinates that around whom will the circle be drawn.

        :param alpha:
        Angle of deviation, corresponding to radius of said circle, in degrees.
        Note: For 90 degrees, formed circle is a Great Circle.

        :return:
        Returns discrete meshes of lat and lon values for circle generation. 360 points each.
        """

        # Initialize discrete space for later mesh of lat and lon coordinates.
        discrete_circle_linspace = np.linspace(0, 2 * np.pi, 360)

        # Converting the elliptical coordinates to cartesian.
        circle_center_vector_in_cartesian = np.array(
            self.convertSphericalToCartesian(circle_center_vector[0], circle_center_vector[1])
        )

        # Converting degrees to radians.
        alpha_in_rad = np.deg2rad(alpha)

        # An arbitrary vector upon which the rotating vector will be built.
        basis_vector = np.array([0, 0, 1])

        # We avoid illegal cross products.
        if np.allclose(circle_center_vector_in_cartesian, basis_vector):
            rotating_vector = np.array([1, 0, 0])
        else:
            # Cross product and normalize the vector
            rotating_vector = np.cross(basis_vector, circle_center_vector_in_cartesian)
            rotating_vector /= np.linalg.norm(rotating_vector)

        # Construct the main vector from the rotating vector and the user given vector that will "draw" the circle.
        main_vector = np.cross(circle_center_vector_in_cartesian, rotating_vector)

        # "Drawing" the circle.
        circle_values_in_cartesian = (
                np.cos(alpha_in_rad) * circle_center_vector_in_cartesian[:, np.newaxis] +
                np.sin(alpha_in_rad) * (
                        np.cos(discrete_circle_linspace) * rotating_vector[:, np.newaxis] +
                        np.sin(discrete_circle_linspace) * main_vector[:, np.newaxis]
                )
        )

        # We convert back to spherical coordinates.
        circle_lon, circle_lat = self.convertCartesianToSpherical(
            circle_values_in_cartesian[0], circle_values_in_cartesian[1], circle_values_in_cartesian[2]
        )

        # Boundary correction (not essential but nice to have).
        circle_lon = (circle_lon + np.pi) % (2 * np.pi) - np.pi

        return circle_lon, circle_lat
