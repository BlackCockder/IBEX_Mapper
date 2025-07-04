import numpy as np
from scipy.spatial.transform import Rotation as R

class Configurator:
    def __init__(self):
        pass

    def sph2cart(self, lon: float, lat: float) -> np.ndarray:
        x: float = np.cos(lat) * np.cos(lon)
        y: float = np.cos(lon) * np.sin(lat)
        z: float = np.sin(lat)
        return np.array([x, y, z])

    def build_rotation(self, v1_lon: float, v1_lat: float, v2_lon: float, v2_lat: float) -> float:
        x_axis = np.array([1., 0., 0.])

        # conversion from degrees to radians
        v1_lon_rad, v1_lat_rad = np.deg2rad(v1_lon), np.deg2rad(v1_lat)
        v2_lon_rad, v2_lat_rad = np.deg2rad(v2_lon), np.deg2rad(v2_lat)

        # converting to cartesian coordinates
        v1: np.ndarray = self.sph2cart(v1_lon_rad, v1_lat_rad)
        v2: np.ndarray = self.sph2cart(v2_lon_rad, v2_lat_rad)

        R1, _ = R.align_vectors([x_axis], [v1])

        v2p = R1.apply(v2)
        beta = np.arctan2(v2p[1], v2p[2])
        R2 = R.from_euler("x", beta)

        return R2 * R1 # whole rotation matrix