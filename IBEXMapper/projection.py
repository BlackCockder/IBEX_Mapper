import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from .configurator import Configurator
from .calculator import Calculator
from scipy.spatial.transform import Rotation as R

temp_calculator = Calculator()
temp_configurator = Configurator(temp_calculator)


class Projection:
    def __init__(self):
        pass

    @staticmethod
    def sph2cart(lon_deg, lat_deg):
        lon = np.radians(lon_deg)
        lat = np.radians(lat_deg)
        x = np.cos(lat) * np.cos(lon)
        y = np.cos(lat) * np.sin(lon)
        z = np.sin(lat)
        return np.vstack((x, y, z)).T            # shape: (N,3)

    @staticmethod
    def cart2sph(xyz):
        x, y, z = xyz.T
        lon = np.degrees(np.arctan2(y, x))
        hyp = np.hypot(x, y)
        lat = np.degrees(np.arctan2(z, hyp))
        return lon, lat

    def projection(self, z: np.ndarray,
                   n: int, filename: str,
                   central_coords: np.ndarray,
                   meridian_coords: np.ndarray) -> None:

        lon = np.linspace(-np.pi, np.pi, n)
        lat = np.linspace(np.pi/2, -np.pi/2, n)
        lon, lat = np.meshgrid(lon, lat)

        lon_step, lat_step = 30, 30
        lon_grid = np.deg2rad(np.arange(-180, 181, lon_step))
        lat_grid = np.deg2rad(np.arange(-90, 91, lat_step))
        graticule_handles = []

        raw_label = Path(filename).stem
        safe_label = raw_label.replace("_", " ").removesuffix("esa").lstrip("t") # for testing
        # rib, ylm, coeff, year, number = safe_label.split(" ")

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="mollweide")

        pcm = ax.pcolormesh(lon, lat, z, cmap="magma", shading="auto") # cmap: "viridis"
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        # ax.text(x=np.pi, y=np.pi/2, s=f"YEAR: {year}")
        # ax.text(x=-np.pi, y=np.pi/2, s=f"NUMBER: {number}")

        ax.set_title("IBEX Mapper")
        # ax.set_xlabel("Longitude (rad)")
        # ax.set_ylabel("Latitude (rad)")
        # ax.set_xlim([-np.pi, np.pi])
        # ax.set_ylim([-np.pi / 2, np.pi / 2])
        # ax.set_aspect('auto')
        # ax.invert_xaxis()

        Rotation1 = temp_configurator.buildCenteringRotation(np.array(central_coords))
        Rotation2 = temp_configurator.buildMeridianRotation(np.array(meridian_coords), Rotation1)

        # Use your function, but pass them as 1-element arrays
        central_vec = temp_configurator.convertSphericalToCartesianForPoints(central_coords)
        meridian_vec = temp_configurator.convertSphericalToCartesianForPoints(meridian_coords)

        FinalRotation = Rotation2 @ Rotation1

        for delta in lon_grid:
            theta_line = np.linspace(np.pi/2, -np.pi/2, 361)
            delta_line = np.full_like(theta_line, delta)



        rotated_central_vec = Rotation1 @ central_vec
        print(rotated_central_vec)
        rotated_meridian_vec = FinalRotation @ meridian_vec

        central_lon, central_lat = temp_calculator.convertCartesianToSpherical(
            np.array([[rotated_central_vec[0]]]),
            np.array([[rotated_central_vec[1]]]),
            np.array([[rotated_central_vec[2]]])
        )

        meridian_lon, meridian_lat = temp_calculator.convertCartesianToSpherical(
            np.array([[rotated_meridian_vec[0]]]),
            np.array([[rotated_meridian_vec[1]]]),
            np.array([[rotated_meridian_vec[2]]])
        )
        print("Rotated central point (deg):", np.rad2deg(central_lon[0, 0]), np.rad2deg(central_lat[0, 0]))
        print("Rotated meridian point (deg):", np.rad2deg(meridian_lon[0, 0]), np.rad2deg(meridian_lat[0, 0]))


        ax.plot(central_lon[0, 0], central_lat[0, 0], 'ro', markersize=6, label="Central Point")
        ax.plot(meridian_lon[0, 0], meridian_lat[0, 0], 'bo', markersize=6, label="Meridian Point")

        ax.legend(loc='lower left')
        plt.tight_layout()
        plt.savefig("IBEX_Mapper.pdf", format='pdf', dpi=n)
        plt.show()
