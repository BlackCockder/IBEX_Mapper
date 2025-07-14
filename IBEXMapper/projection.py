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
    FEATURES_DIR = "map_features"
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")
    OUTPUT_DIR = "output"

    def __init__(self, calculator: Calculator, configurator: Configurator):
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

    def rotate_lonlat(self, lon_rad, lat_rad, R_mat):
        orig_shape = lon_rad.shape  # keep grid shape

        # lon/lat -> cartesian
        x, y, z = self.calculator.convertSphericalToCartesian(
            lon_rad.ravel(),
            lat_rad.ravel()
        )
        xyz = np.vstack([x, y, z]) # (3, N)

        # rotate every point
        xyz_rot = R_mat @ xyz # (3, N)

        # cartesian -> lon/lat
        lon_rot, lat_rot = self.calculator.convertCartesianToSpherical(
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
            ax.plot(-lon_r, lat_r, lw=.4, color='gray')

        # meridians
        for lon0 in np.deg2rad(np.arange(-180, 181, lon_step)):
            lat_line = np.linspace(-np.pi/2, np.pi/2, n_seg)
            lon_line = np.full_like(lat_line, lon0)
            lon_r, lat_r = self.rotate_lonlat(lon_line, lat_line, R_mat)
            lon_r, lat_r = self._split_at_wrap(lon_r, lat_r)   # ← NEW
            ax.plot(-lon_r, lat_r, lw=.4, color='gray')

    def projection(self, z: np.ndarray,
                   n: int, filename: str,
                   rotate: bool,
                   central_coords: np.ndarray,
                   meridian_coords: np.ndarray) -> None:

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
        FinalRotation = np.array([])
        if central_coords[0] == meridian_coords[0] and central_coords[1] == meridian_coords[1]:
            FinalRotation = Rotation1
        else:
            FinalRotation = self.calculator.combineRotation(Rotation1, Rotation2)

        rotated_central_vec = Rotation1 @ central_vector_point
        rotated_meridian_vec = FinalRotation @ meridian_vector_point

        central_lon, central_lat = self.calculator.convertCartesianToSpherical(
            rotated_central_vec[0],
            rotated_central_vec[1],
            rotated_central_vec[2]
        )

        meridian_lon, meridian_lat = self.calculator.convertCartesianToSpherical(
            rotated_meridian_vec[0],
            rotated_meridian_vec[1],
            rotated_meridian_vec[2],
        )

        parsed_points = self.load_points(self.FEATURES_FILE)

        for point in parsed_points:
            name = point["name"]
            spherical = point["coordinates"]
            color = point["color"]
            if rotate:
                point_in_cartesian_coordinates = self.calculator.convertSphericalToCartesian(np.deg2rad(spherical[0]), np.deg2rad(spherical[1]))

                rotated_cartesian = FinalRotation @ point_in_cartesian_coordinates

                lon_spherical, lat_spherical = self.calculator.convertCartesianToSpherical(
                    np.array([rotated_cartesian[0]]),
                    np.array([rotated_cartesian[1]]),
                    np.array([rotated_cartesian[2]])
                )
                ax.plot(-lon_spherical[0], lat_spherical[0], 'o', markersize=5, color=color, zorder=6)
                ax.text(-lon_spherical[0], lat_spherical[0], f' {name}', fontsize=7, color=color, zorder=6)
            else:
                spherical[0] = np.deg2rad(spherical[0])
                spherical[1] = np.deg2rad(spherical[1])
                ax.plot(-spherical[0], spherical[1], 'o', markersize=5, color=color, zorder=6)
                ax.text(-spherical[0], spherical[1], f' {name}', fontsize=7, color=color, zorder=6)

        circle_center_vector = np.array([np.deg2rad(120), np.deg2rad(30)])
        alpha = 30
        lon_circ, lat_circ = self.calculator.createCircle(circle_center_vector, alpha)

        lon_circ_rot, lat_circ_rot = self.rotate_lonlat(lon_circ, lat_circ, FinalRotation)

        lon_circ_rot, lat_circ_rot = self._split_at_wrap(lon_circ_rot, lat_circ_rot)

        rotated_circle_center_vector_lon, rotated_circle_center_vector_lat = self.rotate_lonlat(circle_center_vector[0], circle_center_vector[1], FinalRotation)

        ax.plot(-rotated_circle_center_vector_lon, rotated_circle_center_vector_lat, 'o', markersize=5, color="cyan", zorder=5)
        ax.plot(-lon_circ_rot, lat_circ_rot, color='cyan', linewidth=1.5, zorder=5)

        # wip
        if rotate:
            self.draw_graticule(ax, FinalRotation)
        else:
            self.draw_graticule(ax, np.eye(3))

        # watermark
        logo = mpimg.imread("public\logo_ibex.png")
        zoom = 0.3
        imagebox = OffsetImage(logo, zoom=zoom)
        ab = AnnotationBbox(
            imagebox,
            xy=(0.97, 0.04),
            xycoords="figure fraction",
            frameon=False,
            box_alignment=(1, 0)
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

        print("Rotated central point (deg):", np.rad2deg(central_lon), np.rad2deg(central_lat))
        print("Rotated meridian point (deg):", np.rad2deg(meridian_lon), np.rad2deg(meridian_lat))

        ax.set_xticks([])
        ax.set_yticks([])
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.grid(False)

        pcm = ax.pcolormesh(lon, lat, z, cmap="magma", shading="auto", rasterized=True) # cmap: "viridis"
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        ax.plot(-central_lon, central_lat, 'ro', markersize=6, label="Central Point")
        ax.plot(-meridian_lon, meridian_lat, 'bo', markersize=6, label="Meridian Point")
        ax.legend(loc='lower left')
        equator_degrees = np.arange(-180, 180, 30)
        for lon_deg in equator_degrees:
            if lon_deg == 0:
                label = "0"
            else:
                label = f"{int(lon_deg)}°"
            lon_rad = np.deg2rad(lon_deg)
            lat_rad = 0.0
            if rotate:
                x, y = self.rotate_lonlat(np.array([lon_rad]), np.array([lat_rad]), FinalRotation)
            else:
                x, y = np.array([lon_rad]), np.array([lat_rad])
            ax.text(-x[0], y[0], label, fontsize=6, ha='center', va='bottom', color='white', zorder=7)

        # Add labeled degree points along Meridian (lon = 0°)
        meridian_degrees = np.arange(-90, 91, 30)  # 6 points every 30°
        for lat_deg in meridian_degrees:
            if lat_deg == 0:
                continue  # Already labeled at equator
            label = f"{int(lat_deg)}°"
            lat_rad = np.deg2rad(lat_deg)
            lon_rad = 0.0  # Meridian

            if rotate:
                x, y = self.rotate_lonlat(np.array([lon_rad]), np.array([lat_rad]), FinalRotation)
            else:
                x, y = np.array([lon_rad]), np.array([lat_rad])
            ax.text(-x[0], y[0], label, fontsize=6, ha='left', va='center', color='white', zorder=7)

        plt.tight_layout()
        plt.savefig(os.path.join(self.OUTPUT_DIR, f"file_{filename}__res{n}.pdf"), format='pdf', dpi=n)
        plt.show()

    def load_points(self, json_path: str):
        """
        Loads points from JSON file and parses their coordinates into np.array format.
        Returns a list of dictionaries with 'name', 'coordinates' as np.array([lon, lat]), and 'color' as string.
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        points = data.get("points", [])
        parsed_points = []

        for point in points:
            name = point["name"]
            coord_str = point["coordinates"].strip("()")
            lon_str, lat_str = coord_str.split(",")
            lon, lat = float(lon_str), float(lat_str)
            color = point.get("color", "black")  # default to black if missing

            parsed_points.append({
                "name": name,
                "coordinates": np.array([lon, lat]),
                "color": color
            })

        return parsed_points
