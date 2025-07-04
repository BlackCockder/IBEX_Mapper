import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

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

        # lon_r na lat_r changed
        pcm = ax.pcolormesh(lon, lat, z, cmap="viridis", shading="auto")
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        plt.title("IBEX Mapper")
        plt.savefig("IBEX_Mapper.pdf", format='pdf', dpi=n)
        plt.show()

