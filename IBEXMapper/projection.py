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

    def projection(self, z: np.ndarray, n: int, filename: str, central_coords: tuple[float, float], meridian_coords: tuple[float, float]) -> None:
        lon = np.linspace(-np.pi, np.pi, n)
        lat = np.linspace(np.pi/2, -np.pi/2, n)

        lon, lat = np.meshgrid(lon, lat)

        raw_label = Path(filename).stem
        safe_label = raw_label.replace("_", " ").removesuffix("esa")

        fig, ax = plt.subplots(figsize=(8, 6))
        pcm = ax.pcolormesh(lon, lat, z, cmap="viridis", shading="auto")
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        ax.set_title("IBEX Mapper (Rectangular Projection)")
        ax.set_xlabel("Longitude (rad)")
        ax.set_ylabel("Latitude (rad)")
        ax.set_xlim([-np.pi, np.pi])
        ax.set_ylim([-np.pi / 2, np.pi / 2])
        ax.set_aspect('auto')


        Rotation1 = temp_configurator.buildCenteringRotation(np.array(central_coords))
        Rotation2 = temp_configurator.buildAligningRotation(np.array(meridian_coords), Rotation1)

        # Use your function, but pass them as 1-element arrays
        central_vec = temp_configurator.convertSphericalToCartesianForPoints(central_coords[0], central_coords[1])
        meridian_vec = temp_configurator.convertSphericalToCartesianForPoints(meridian_coords[0], meridian_coords[1])

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
        print("Rotated central point (deg):", np.rad2deg(central_lon[0, 0]), np.rad2deg(central_lat[0, 0]))
        print("Rotated meridian point (deg):", np.rad2deg(meridian_lon[0, 0]), np.rad2deg(meridian_lat[0, 0]))


        ax.plot(central_lon[0, 0], central_lat[0, 0], 'ro', markersize=6, label="Central Point")
        ax.plot(meridian_lon[0, 0], meridian_lat[0, 0], 'bo', markersize=6, label="Meridian Point")

        ax.legend(loc='lower left')
        plt.tight_layout()
        plt.savefig("IBEX_Mapper.pdf", format='pdf', dpi=n)
        plt.show()

