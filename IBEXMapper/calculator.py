from scipy.special import sph_harm_y_all as spherical_harmonics
from scipy.interpolate import RegularGridInterpolator
import numpy as np


class Calculator:
    def __init__(self):
        pass

    def calculateMainMatrixFromData(self, data, spherical_harmonics_values_matrix, dpi):
        coefficients = data[:, 2]
        return np.roll(np.flipud(np.tensordot(coefficients, np.stack(spherical_harmonics_values_matrix), axes=1).T), shift=dpi // 2, axis=1)
                            
    def calculateSphericalHarmonicsDataForSetDPI(self, dpi, target_max_l):
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

    def filterComplexNumbersFromSphericalHarmonics(self, m, spherical_harmonic_positive, spherical_harmonic_negative):
        if m < 0:
            return (1j / np.sqrt(2)) * (spherical_harmonic_positive - (((-1) ** abs(m)) * spherical_harmonic_negative))
        elif m == 0:
            return spherical_harmonic_positive
        else:
            return (1 / np.sqrt(2)) * (spherical_harmonic_negative + (((-1) ** abs(m)) * spherical_harmonic_positive))

    def convertSphericalToCartesian(self, lon_mesh: np.ndarray, lat_mesh: np.ndarray) -> np.ndarray:
        x = np.cos(lat_mesh) * np.cos(lon_mesh)
        y = np.cos(lat_mesh) * np.sin(lon_mesh)
        z = np.sin(lat_mesh)
        return np.stack((x, y, z), axis=-1)

    def convertCartesianToSpherical(self, x_mesh: np.ndarray, y_mesh: np.ndarray, z_mesh: np.ndarray) -> np.ndarray:
        lat = np.arcsin(z_mesh)
        lon = np.arctan2(y_mesh, x_mesh)
        return np.stack((lat, lon), axis=-1)

    def rotateGridByTwoRotations(self,
                                 x_mesh: np.ndarray,
                                 y_mesh: np.ndarray,
                                 z_mesh: np.ndarray,
                                 central_rotation: np.ndarray,
                                 meridian_rotation: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

        full_rotation = meridian_rotation @ central_rotation

        original_shape = x_mesh.shape

        cartesian_coordinates_matrix = np.stack((x_mesh, y_mesh, z_mesh), axis=-1).reshape(-1, 3)

        rotated_cartesian_coordinates_matrix = cartesian_coordinates_matrix @ full_rotation.T

        rot_x_mesh = rotated_cartesian_coordinates_matrix[:, 0].reshape(original_shape)
        rot_y_mesh = rotated_cartesian_coordinates_matrix[:, 1].reshape(original_shape)
        rot_z_mesh = rotated_cartesian_coordinates_matrix[:, 2].reshape(original_shape)

        return rot_x_mesh, rot_y_mesh, rot_z_mesh

    def interpolateDataForNewGrid(self, data_to_interpolate: np.ndarray, rotated_lat: np.ndarray, rotated_lon: np.ndarray) -> np.ndarray:

        dpi = data_to_interpolate.shape[0]

        lat = np.linspace(np.pi / 2, -np.pi / 2, dpi)
        lon = np.linspace(-np.pi, np.pi, dpi)

        rotated_lon_wrapped = np.mod(rotated_lon + np.pi, 2 * np.pi) - np.pi

        interpolator = RegularGridInterpolator((lat, lon), data_to_interpolate, method='linear', bounds_error=False, fill_value=np.nan)

        points = np.stack((rotated_lat.ravel(), rotated_lon_wrapped.ravel()), axis=-1)

        interpolated = interpolator(points).reshape(rotated_lat.shape)

        return interpolated
      