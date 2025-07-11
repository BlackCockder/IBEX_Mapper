import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from .configurator import Configurator
from .calculator import Calculator
from matplotlib.offsetbox import AnchoredText, OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import json
import os


class Projection:




    def __init__(self, calculator: Calculator, configurator: Configurator) -> None:
        self.calculator = calculator
        self.configurator = configurator

    #wip
    def _split_at_wrap(self, lon_r, lat_r, thresh=np.pi):
        """Return copies of *lon_r*, *lat_r* with NaNs inserted wherever the curve
        crosses the ±π seam, so Matplotlib starts a new segment there."""
        jump = np.abs(np.diff(lon_r)) > thresh
        if not jump.any():
            return lon_r, lat_r
        idx = np.where(jump)[0] + 1        # segment starts *after* the jump
        lon_r, lat_r = lon_r.astype(float), lat_r.astype(float)
        lon_r[idx] = np.nan
        lat_r[idx] = np.nan
        return lon_r, lat_r

    # wip
    def rotate_lonlat(self, lon_rad, lat_rad, R_mat):
        orig_shape = lon_rad.shape  # keep grid shape

        # lon/lat -> cartesian
        x, y, z = temp_calculator.convertSphericalToCartesian(
            lon_rad.ravel(),
            lat_rad.ravel()
        )
        xyz = np.vstack([x, y, z]) # (3, N)

        # rotate every point
        xyz_rot = R_mat @ xyz # (3, N)

        # cartesian -> lon/lat
        lon_rot, lat_rot = temp_calculator.convertCartesianToSpherical(
            xyz_rot[0], xyz_rot[1], xyz_rot[2]
        )

        # reshape and wrap to (-pi, pi]
        lon_rot = lon_rot.reshape(orig_shape)
        lat_rot = lat_rot.reshape(orig_shape)
        lon_rot = (lon_rot + np.pi) % (2 * np.pi) - np.pi
        return lon_rot, lat_rot

    # wip
    def draw_graticule(self, ax, R_mat, lon_step=30, lat_step=30, n_seg=361):
        # parallels
        for lat0 in np.deg2rad(np.arange(-90, 91, lat_step)):
            lon_line = np.linspace(-np.pi, np.pi, n_seg)
            lat_line = np.full_like(lon_line, lat0)
            lon_r, lat_r = self.rotate_lonlat(lon_line, lat_line, R_mat)
            lon_r, lat_r = self._split_at_wrap(lon_r, lat_r)   # ← NEW
            ax.plot(-lon_r, lat_r, lw=.4, color='#E6DAA6')

        # meridians
        for lon0 in np.deg2rad(np.arange(-180, 181, lon_step)):
            lat_line = np.linspace(-np.pi/2, np.pi/2, n_seg)
            lon_line = np.full_like(lat_line, lon0)
            lon_r, lat_r = self.rotate_lonlat(lon_line, lat_line, R_mat)
            lon_r, lat_r = self._split_at_wrap(lon_r, lat_r)   # ← NEW
            ax.plot(-lon_r, lat_r, lw=.4, color='#E6DAA6')


    def projection(self, z: np.ndarray,
                   n: int, filename: str,
                   rotate: bool,
                   central_coords: tuple[float, float],
                   meridian_coords: tuple[float, float]) -> None:

        lon = np.linspace(-np.pi, np.pi, n)
        lat = np.linspace(np.pi/2, -np.pi/2, n)
        lon, lat = np.meshgrid(lon, lat)

        raw_label = Path(filename).stem
        safe_label = raw_label.replace("_", " ").removesuffix("esa").lstrip("t") # for testing
        # rib, ylm, coeff, year, number = safe_label.split(" ")

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="mollweide")
        # ax.text(x=np.pi, y=np.pi/2, s=f"YEAR: {year}")
        # ax.text(x=-np.pi, y=np.pi/2, s=f"NUMBER: {number}")
        ax.set_title("IBEX Mapper")

        Rotation1 = self.configurator.buildCenteringRotation(np.array(central_coords))
        Rotation2 = self.configurator.buildMeridianRotation(np.array(meridian_coords), Rotation1)

        central_vector_point = self.calculator.convertSphericalToCartesian(np.deg2rad(central_coords[0]), np.deg2rad(central_coords[1]))
        meridian_vector_point = self.calculator.convertSphericalToCartesian(np.deg2rad(meridian_coords[0]), np.deg2rad(meridian_coords[1]))

        FinalRotation = self.calculator.combineRotation(Rotation1, Rotation2)

        rotated_central_vec = Rotation1 @ central_vector_point
        rotated_meridian_vec = FinalRotation @ meridian_vector_point

        central_lon, central_lat = self.calculator.convertCartesianToSpherical(
            np.array([rotated_central_vec[0]]),
            np.array([rotated_central_vec[1]]),
            np.array([rotated_central_vec[2]])
        )

        meridian_lon, meridian_lat = self.calculator.convertCartesianToSpherical(
            np.array([rotated_meridian_vec[0]]),
            np.array([rotated_meridian_vec[1]]),
            np.array([rotated_meridian_vec[2]])
        )

























        # wip
        self.draw_graticule(ax, FinalRotation)

        # watermark
        logo = mpimg.imread("public\logo_ibex.png")
        zoom = 0.3
        imagebox = OffsetImage(logo, zoom=zoom)
        ab = AnnotationBbox(
            imagebox,
            xy=(0.97, 0.04),  # (x, y) in figure-fraction coords (0-1)
            xycoords="figure fraction",
            frameon=False,  # no extra frame; set True if you want one
            box_alignment=(1, 0)  # (1,0) = right-bottom corner of the box
        )
        ab.set_zorder(10)  # draw on top of everything else
        ax.add_artist(ab)

        at = AnchoredText(
            "2025 IBEX Mapper",  # text to display
            loc="lower right",  # 'upper left' | 'upper right' | …
            prop=dict(size=8),  # text style
            frameon=True,  # draws a bbox
            pad=0.3,  # tighten / loosen padding
            borderpad=0.4
        )
        at.patch.set_facecolor("white")  # make sure the box stays white
        at.patch.set_edgecolor("none")  # remove border if not needed
        ax.add_artist(at)
        plt.tight_layout()

        print("Rotated central point (deg):", np.rad2deg(central_lon[0, 0]), np.rad2deg(central_lat[0, 0]))
        print("Rotated meridian point (deg):", np.rad2deg(meridian_lon[0, 0]), np.rad2deg(meridian_lat[0, 0]))

        # ticks
        ticks_deg = np.arange(-150, 180, 30)  # default range
        ticks_rad = np.deg2rad(ticks_deg)
        labels = [f"{abs(t)}°" if t != 0 else "0°" for t in ticks_deg[::-1]]
        signs = ['' if t == 0 else ('-' if t < 0 else '') for t in ticks_deg[::-1]]
        custom_labels = [f"{s}{l}" for s, l in zip(signs, labels)]
        ax.set_xticks(ticks_rad)
        ax.set_xticklabels(custom_labels)
        ax.grid(False)


        pcm = ax.pcolormesh(lon, lat, z, cmap="magma", shading="auto") # cmap: "viridis"
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        ax.plot(central_lon[0], central_lat[0], 'ro', markersize=6, label="Central Point")
        ax.plot(meridian_lon[0], meridian_lat[0], 'bo', markersize=6, label="Meridian Point")
        ax.legend(loc='lower left')
        plt.tight_layout()
        plt.savefig(os.path.join(self.OUTPUT_DIR, f"file_{filename}__res{n}.pdf"), format='pdf', dpi=n)
        plt.show()
