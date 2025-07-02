import matplotlib.pyplot as plt
import numpy as np


class Projection:
    def __init__(self):
        pass

    def projection(self, z, n: int) -> None:
        lon_min, lon_max, lat_min, lat_max = -180, 180, -90, 90
        lon, lat = np.meshgrid(
            np.linspace(lon_min, lon_max, n),
            np.linspace(lat_min, lat_max, n)
        )

        lon_r , lat_r = np.deg2rad(lon), np.deg2rad(lat) # in radians

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="mollweide")

        pcm = ax.pcolormesh(lon_r, lat_r, z, cmap="viridis", shading="auto")
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label("unit of z")

        plt.title("IBEX Mapper")
        plt.savefig("IBEX_Mapper.pdf", format='pdf', dpi=300)
        plt.show()

