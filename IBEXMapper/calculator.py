from scipy.special import sph_harm_y_all as spherical_harmonics
from scipy.interpolate import RegularGridInterpolator
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainMatrixFromData(self, data: np.ndarray, spherical_harmonics_values_matrix: np.ndarray, dpi: int) -> np.ndarray:
        """
        Function that calculates main heatmap matrix by vectorized multiplying coefficient with relative value from
        spherical harmonics value matrix.

        :param data:
        A (N, 4) matrix of data given by user

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
        # Assuming that 3rd column is always the column with coefficients
        coefficients = data[:, 2]

        main_matrix = np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1).T

        # Matrix realignment
        return np.roll(np.fliplr(main_matrix), shift=dpi // 2, axis=1)
                            
    def calculateSphericalHarmonicsDataForSetDPI(self, dpi: int, target_max_l: int) -> list:
        """
        Function
        :param dpi:
        :param target_max_l:
        :return:
        """
        colatitude, longitude = np.meshgrid(np.linspace(0, np.pi, dpi), np.linspace(0, 2 * np.pi, dpi))
        spherical_harmonics_array_on_real_plane = []
        unfiltered_array = spherical_harmonics(target_max_l, target_max_l, colatitude, longitude)
        for l in range(target_max_l + 1):
                for m in range(-l, l + 1):
                    spherical_harmonics_array_on_real_plane.append(
                        self.filterComplexNumbersFromSphericalHarmonics(
                            m,
                            unfiltered_array[l][m],
                            unfiltered_array[l][-m])
                        .real)
        return spherical_harmonics_array_on_real_plane

    def filterComplexNumbersFromSphericalHarmonics(self,
                                                   m: float,
                                                   spherical_harmonic_positive: np.ndarray,
                                                   spherical_harmonic_negative: np.ndarray) -> np.ndarray:
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

    def convertCartesianToSpherical(self, x: float, y: float, z: float) -> tuple[float, float]:
        lat = np.arcsin(z)
        lon = np.arctan2(y, x)

        if isinstance(y, float):
            if abs(y) < 1e-10:
                lon = 0.0

        return lon, lat

    def rotateGridByRotation(self,
                             x_mesh: np.ndarray,
                             y_mesh: np.ndarray,
                             z_mesh: np.ndarray,
                             rotation: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        original_shape = x_mesh.shape

        cartesian_coordinates_matrix = np.stack((x_mesh, y_mesh, z_mesh), axis=-1).reshape(-1, 3)

        rotated_cartesian_coordinates_matrix = cartesian_coordinates_matrix @ rotation.T

        rot_x_mesh = rotated_cartesian_coordinates_matrix[:, 0].reshape(original_shape)
        rot_y_mesh = rotated_cartesian_coordinates_matrix[:, 1].reshape(original_shape)
        rot_z_mesh = rotated_cartesian_coordinates_matrix[:, 2].reshape(original_shape)

        return rot_x_mesh, rot_y_mesh, rot_z_mesh

    def interpolateDataForNewGrid(self,
                                  data_to_interpolate: np.ndarray,
                                  rotated_lat: np.ndarray,
                                  rotated_lon: np.ndarray) -> np.ndarray:

        dpi = data_to_interpolate.shape[0]

        lat = np.linspace(np.pi / 2, -np.pi / 2, dpi)
        lon = np.linspace(np.pi, -np.pi, dpi)

        interpolator = RegularGridInterpolator((lat, lon), data_to_interpolate, method='linear', bounds_error=False, fill_value=np.nan)

        rotated_vectors = np.stack((rotated_lat.ravel(), rotated_lon.ravel()), axis=-1)

        interpolated_data = interpolator(rotated_vectors).reshape(rotated_lat.shape)

        return interpolated_data

    def combineRotation(self, original_rotation: np.ndarray, input_rotation: np.ndarray) -> np.ndarray:
        return input_rotation @ original_rotation
