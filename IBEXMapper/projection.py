import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from .configurator import Configurator
from .calculator import Calculator

temp_calculator = Calculator()
temp_configurator = Configurator(temp_calculator)


class Projection:
    def __init__(self):
        pass

    def projection(self, z: np.ndarray, n: int, filename: str) -> None:
        lon = np.linspace(-np.pi, np.pi, n)
        lat = np.linspace(np.pi/2, -np.pi/2, n)

        lon, lat = np.meshgrid(lon, lat)

        raw_label = Path(filename).stem
        safe_label = raw_label.replace("_", " ").removesuffix("esa")

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="mollweide")
        # Points in degrees (lon, lat)
        central_point_deg = (-120.0, 43.0)
        meridian_point_deg = (5.0, 40.0)

        Rotation1 = temp_configurator.buildCenteringRotation(np.array(central_point_deg))
        Rotation2 = temp_configurator.buildAligningRotation(np.array(meridian_point_deg))

        # Use your function, but pass them as 1-element arrays
        central_vec = temp_configurator.convertSphericalToCartesianForPoints(central_point_deg[0], central_point_deg[1])
        meridian_vec = temp_configurator.convertSphericalToCartesianForPoints(meridian_point_deg[0], meridian_point_deg[1])

        FinalRotation = Rotation2 @ Rotation1

        rotated_central_vec = FinalRotation @ central_vec
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


        ax.plot(central_lon[0, 0], central_lat[0, 0], 'ro', markersize=6, label="Central Point")
        ax.plot(meridian_lon[0, 0], meridian_lat[0, 0], 'bo', markersize=6, label="Meridian Point")

        ax.legend(loc='lower left')


        pcm = ax.pcolormesh(lon, lat, z, cmap="viridis", shading="auto")
        # mask
        mask_neg = z < 0
        lon_r = np.where(mask_neg, lon, np.nan)
        lat_r = np.where(mask_neg, lat, np.nan)

        # scatter line below zero
        cs = ax.contour(
            lon_r, lat_r, z,
            levels=[0],
            colors="red",
            linestyles="--",
            linewidths=0.8
        )
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        plt.title("IBEX Mapper")
        plt.savefig("IBEX_Mapper.pdf", format='pdf', dpi=n)
        plt.show()

