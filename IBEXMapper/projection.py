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

    def rotate_lonlat(self, lon_rad, lat_rad, R_mat):

        orig_shape = lon_rad.shape

        # 1. → Cartesian
        xyz = temp_calculator.convertSphericalToCartesian(lat_rad.ravel(), lon_rad.ravel())   # (3, N)

        # 2. rotate
        xyz_rot = R_mat @ xyz                                         # (3, N)

        # 3. → spherical
        lon_rot, lat_rot = temp_calculator.convertCartesianToSpherical(xyz_rot[0], xyz_rot[1], xyz_rot[2])
        lon_rot = lon_rot.reshape(orig_shape)
        lat_rot = lat_rot.reshape(orig_shape)

        # 4. wrap longitude to (-π, π]
        lon_rot = (lon_rot + np.pi) % (2 * np.pi) - np.pi
        return lon_rot, lat_rot

    def draw_graticule(self, ax, R_mat, lon_step=30, lat_step=30, n_seg=361):
        # parallels
        for lat0 in np.deg2rad(np.arange(-90, 91, lat_step)):
            lon_line = np.linspace(-np.pi, np.pi, n_seg)
            lat_line = np.full_like(lon_line, lat0)
            lon_r, lat_r = self.rotate_lonlat(lon_line, lat_line, R_mat)
            ax.plot(lon_r, lat_r, lw=.6, color='grey')

        # meridians
        for lon0 in np.deg2rad(np.arange(-180, 181, lon_step)):
            lat_line = np.linspace(-np.pi/2, np.pi/2, n_seg)
            lon_line = np.full_like(lat_line, lon0)
            lon_r, lat_r = self.rotate_lonlat(lon_line, lat_line, R_mat)
            ax.plot(lon_r, lat_r, lw=.6, color='grey')

    def projection(self, z: np.ndarray,
                   n: int, filename: str,
                   central_coords: tuple[float, float],
                   meridian_coords: tuple[float, float]) -> None:

        lon = np.linspace(-np.pi, np.pi, n)
        lat = np.linspace(np.pi/2, -np.pi/2, n)
        lon, lat = np.meshgrid(lon, lat)

        lon_grid = np.deg2rad(np.arange(-180, 181, 30))
        lat_grid = np.deg2rad(np.arange(-90, 91, 30))

        raw_label = Path(filename).stem
        safe_label = raw_label.replace("_", " ").removesuffix("esa").lstrip("t") # for testing
        # rib, ylm, coeff, year, number = safe_label.split(" ")

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="mollweide")

        # ax.text(x=np.pi, y=np.pi/2, s=f"YEAR: {year}")
        # ax.text(x=-np.pi, y=np.pi/2, s=f"NUMBER: {number}")

        ax.set_title("IBEX Mapper")

        Rotation1 = temp_configurator.buildCenteringRotation(np.array(central_coords))
        Rotation2 = temp_configurator.buildMeridianRotation(np.array(meridian_coords), Rotation1)

        # Use your function, but pass them as 1-element arrays
        central_vec = temp_configurator.convertSphericalToCartesianForPoints(np.array(central_coords))
        meridian_vec = temp_configurator.convertSphericalToCartesianForPoints(np.array(central_coords))

        FinalRotation = Rotation2 @ Rotation1

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

        lon_c, lat_c = self.rotate_lonlat(
            np.radians(central_coords[0]), np.radians(central_coords[1]), FinalRotation
        )

        lon_rot, lat_rot = self.rotate_lonlat(lon, lat, FinalRotation)

        # draw the rotated graticule
        # self.draw_graticule(ax, FinalRotation)

        # central and meridian reference points
        lon_c, lat_c = self.rotate_lonlat(
            np.array([[np.radians(central_coords[0])]]),
            np.array([[np.radians(central_coords[1])]]),
            FinalRotation
        )
        lon_m, lat_m = self.rotate_lonlat(
            np.array([[np.radians(meridian_coords[0])]]),
            np.array([[np.radians(meridian_coords[1])]]),
            FinalRotation
        )
        self.draw_graticule(ax, FinalRotation)

        ax.plot(lon_c, lat_c, 'ro', ms=6)

        print("Rotated central point (deg):", np.rad2deg(central_lon[0, 0]), np.rad2deg(central_lat[0, 0]))
        print("Rotated meridian point (deg):", np.rad2deg(meridian_lon[0, 0]), np.rad2deg(meridian_lat[0, 0]))

        pcm = ax.pcolormesh(lon, lat, z, cmap="magma", shading="auto") # cmap: "viridis"
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        # ticks
        ticks_deg = np.arange(-150, 180, 30)  # default range
        ticks_rad = np.deg2rad(ticks_deg)
        labels = [f"{abs(t)}°" if t != 0 else "0°" for t in ticks_deg[::-1]]
        signs = ['' if t == 0 else ('-' if t < 0 else '') for t in ticks_deg[::-1]]
        custom_labels = [f"{s}{l}" for s, l in zip(signs, labels)]
        ax.set_xticks(ticks_rad)
        ax.set_xticklabels(custom_labels)
        ax.grid(False)


        ax.plot(central_lon[0, 0], central_lat[0, 0], 'ro', markersize=6, label="Central Point")
        ax.plot(meridian_lon[0, 0], meridian_lat[0, 0], 'bo', markersize=6, label="Meridian Point")

        ax.legend(loc='lower left')
        plt.tight_layout()
        plt.savefig("IBEX_Mapper.pdf", format='pdf', dpi=n)
        plt.show()
