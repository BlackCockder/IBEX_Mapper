import matplotlib.axes
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from .configurator import Configurator
from .calculator import Calculator
from .handler import Handler
from matplotlib.offsetbox import AnchoredText
import os


class Projection:
    CONFIG_DIR = "config"
    FEATURES_DIR = "map_features"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")
    OUTPUT_DIR = "output"

    def __init__(self, calculator: Calculator, configurator: Configurator, handler: Handler):
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler

    def projectDataOnMollweideProjection(self,
                                         heatmap_data: np.ndarray,
                                         dpi: int,
                                         filename: str,
                                         rotate: bool,
                                         central_coords: np.ndarray,
                                         meridian_coords: np.ndarray,
                                         output_path: str or None) -> None:

        filename = os.path.basename(filename)

        heatmap_data = self.changeMapScale(heatmap_data)

        lon = np.linspace(-np.pi, np.pi, dpi)
        lat = np.linspace(np.pi / 2, -np.pi / 2, dpi)
        lon, lat = np.meshgrid(lon, lat)

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="mollweide")
        ax.set_title("IBEX Mapper")

        Rotation1 = self.configurator.buildCenteringRotation(central_coords)
        Rotation2 = self.configurator.buildMeridianRotation(meridian_coords, Rotation1)

        central_vector_point = self.calculator.convertSphericalToCartesian(np.deg2rad(central_coords[0]), np.deg2rad(central_coords[1]))
        meridian_vector_point = self.calculator.convertSphericalToCartesian(np.deg2rad(meridian_coords[0]), np.deg2rad(meridian_coords[1]))

        FinalRotation = np.array([])

        if central_coords[0] == meridian_coords[0] and central_coords[1] == meridian_coords[1]:
            FinalRotation = Rotation1
        else:
            FinalRotation = Rotation2 @ Rotation1

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

        if rotate:
            self.drawGraticuleOnMap(ax, FinalRotation)
        else:
            self.drawGraticuleOnMap(ax, np.eye(3))

        at = AnchoredText(
            "2025 IBEX Mapper",
            loc="lower right",
            prop=dict(size=8),
            frameon=True,
            pad=0.3,
            borderpad=0.4
        )
        at.patch.set_facecolor("white")  # make sure the box stays white
        at.patch.set_edgecolor("none")  # remove border if not needed
        ax.add_artist(at)
        plt.tight_layout()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.grid(False)

        selected_cmap = self.getMapColorPaletteToProject()

        pcm = ax.pcolormesh(lon, lat, heatmap_data, cmap=selected_cmap, shading="auto", rasterized=True) # cmap: "viridis"
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)

        ax.plot(-central_lon, central_lat, 'ro', markersize=6, label="Central Point")
        ax.plot(-meridian_lon, meridian_lat, 'bo', markersize=6, label="Meridian Point")
        self.addPointsToMap(ax, rotate, FinalRotation)
        self.addCirclesToMap(ax, rotate, FinalRotation)
        self.addTextsToMap(ax)
        self.drawSelectedCoordinatesAlongsideGraticule(ax, rotate, FinalRotation)
        ax.legend(loc='lower left')

        plt.tight_layout()
        if output_path is None:
            plt.savefig(os.path.join(self.OUTPUT_DIR, f"file_{filename}__res{dpi}.pdf"), format='pdf', dpi=dpi)
        else:
            plt.savefig(os.path.join(output_path, f"file_{filename}__res{dpi}.pdf"), format='pdf', dpi=dpi)
        plt.show()

    def cutDataForMolleweideProjeciton(self, lon_r, lat_r, thresh=np.pi):
        """Return copies of lon_r, lat_r with NaNs inserted wherever the curve
        crosses the +/- pi seam, so Matplotlib starts a new segment there."""
        # lon_cont = np.unwrap(lon_r)
        jump = np.abs(np.diff(lon_r)) > thresh
        if not jump.any():
            return lon_r, lat_r
        idx = np.where(jump)[0] + 1
        lon_r, lat_r = lon_r.astype(float), lat_r.astype(float)
        lon_r[idx] = np.nan
        lat_r[idx] = np.nan
        return lon_r, lat_r

    def rotatePointLonLatCoordinates(self, lon_rad, lat_rad, R_mat):
        orig_shape = lon_rad.shape  # keep grid shape

        # lon/lat -> cartesian
        x, y, z = self.calculator.convertSphericalToCartesian(
            lon_rad.ravel(),
            lat_rad.ravel()
        )
        xyz = np.vstack([x, y, z]) # (3, N)

        # rotates every point
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
    def drawGraticuleOnMap(self, ax, R_mat, lon_step=30, lat_step=30, n_seg=361):
        # parallels

        # Initializing a radian space for drawing latitude graticule
        latitude_graticule_space = np.deg2rad(np.arange(-90, 91, lat_step))

        # Drawing all latitude parallels
        for parallel_step in latitude_graticule_space:
            lon_line = np.linspace(-np.pi, np.pi, n_seg)
            lat_line = np.full_like(lon_line, parallel_step)
            lon_r, lat_r = self.rotatePointLonLatCoordinates(lon_line, lat_line, R_mat)
            lon_r, lat_r = self.cutDataForMolleweideProjeciton(lon_r, lat_r)
            ax.plot(-lon_r, lat_r, lw=.4, color='grey', zorder=3)

        # meridians
        for lon0 in np.deg2rad(np.arange(-180, 181, lon_step)):
            lat_line = np.linspace(-np.pi/2, np.pi/2, n_seg)
            lon_line = np.full_like(lat_line, lon0)
            lon_r, lat_r = self.rotatePointLonLatCoordinates(lon_line, lat_line, R_mat)
            lon_r, lat_r = self.cutDataForMolleweideProjeciton(lon_r, lat_r)
            ax.plot(-lon_r, lat_r, lw=.4, color='grey', zorder=3)

    def addPointsToMap(self, ax: matplotlib.axes.Axes, rotate: bool, final_rotation: np.ndarray) -> None:
        """
        Loads points from JSON file and parses their coordinates into np.array format.
        Plots them on the map, with optional rotation. Supports hollow-style markers.
        """
        points = self.handler.getPointsList()

        for point in points:
            name = point["name"]
            spherical = point["coordinates"]
            color = point["color"]
            show_text = point["show_text"]
            point_type = point["point_type"]
            hollow = point["hollow"]

            plot_kwargs = {
                'markersize': 5,
                'color': color,
                'zorder': 9
            }

            if hollow:
                plot_kwargs['markerfacecolor'] = 'none'

            if rotate:
                point_in_cartesian = self.calculator.convertSphericalToCartesian(
                    np.deg2rad(spherical[0]), np.deg2rad(spherical[1])
                )

                rotated_cartesian = final_rotation @ point_in_cartesian

                lon_spherical, lat_spherical = self.calculator.convertCartesianToSpherical(
                    np.array([rotated_cartesian[0]]),
                    np.array([rotated_cartesian[1]]),
                    np.array([rotated_cartesian[2]])
                )

                ax.plot(-lon_spherical[0], lat_spherical[0], point_type, **plot_kwargs)

                if show_text:
                    ax.text(-lon_spherical[0], lat_spherical[0], f' {name}', fontsize=7, color=color, zorder=9)

            else:
                lon_rad = np.deg2rad(spherical[0])
                lat_rad = np.deg2rad(spherical[1])

                ax.plot(-lon_rad, lat_rad, point_type, **plot_kwargs)

                if show_text:
                    ax.text(-lon_rad, lat_rad, f' {name}', fontsize=7, color=color, zorder=9)

    def addCirclesToMap(self, ax: matplotlib.axes.Axes, rotate: bool, final_rotation: np.ndarray) -> None:

        circles = self.handler.getCirclesList()

        for circle in circles:

            circle_center_vector = circle["coordinates"]
            circle_center_vector_in_rad = np.array([np.deg2rad(circle_center_vector[0]), np.deg2rad(circle_center_vector[1])])
            alpha = circle["alpha"]
            color = circle["color"]
            circle_linestyle = circle["linestyle"]

            circle_longitude, circle_latitude = self.calculator.createCircle(circle_center_vector_in_rad, alpha)

            if rotate:

                rotated_circle_longitude, rotated_circle_latitude = self.rotatePointLonLatCoordinates(
                    circle_longitude,
                    circle_latitude,
                    final_rotation)

                rotated_circle_longitude_cut, rotated_circle_latitude_cut = self.cutDataForMolleweideProjeciton(
                    rotated_circle_longitude,
                    rotated_circle_latitude)

                ax.plot(-rotated_circle_longitude_cut, rotated_circle_latitude_cut,
                        color=color, linewidth=1.5, zorder=5, linestyle=circle_linestyle)
            else:
                circle_longitude_cut, circle_latitude_cut = self.cutDataForMolleweideProjeciton(
                    circle_longitude,
                    circle_latitude)
                ax.plot(-circle_longitude_cut, circle_latitude_cut,
                        color=color, linewidth=1.5, zorder=5, linestyle=circle_linestyle)

    def addTextsToMap(self, ax: matplotlib.axes.Axes):

        texts = self.handler.getTextsList()

        for text in texts:
            name = text["name"]
            coordinates = text["coordinates"]
            color = text["color"]
            font_size = text["font_size"]
            tilt_angle = text["tilt_angle"]
            lon_coordinates = np.deg2rad(coordinates[0])
            lat_coordinates = np.deg2rad(coordinates[1])
            ax.text(-lon_coordinates, lat_coordinates, f' {name}',
                    fontsize=font_size, color=color, zorder=6,
                    ha='center',
                    va='center',
                    rotation=-tilt_angle,
                    rotation_mode='anchor')

    def changeMapScale(self, heatmap_data: np.ndarray) -> np.ndarray:
        new_map_scale: tuple[float, float] = self.handler.getHeatmapScale()
        if new_map_scale == (0, 0):
            return heatmap_data
        else:
            return np.clip(heatmap_data, new_map_scale[0], new_map_scale[1])

    def getMapColorPaletteToProject(self) -> str or matplotlib.colors.Colormap:
        """Loads a colormap from a file and returns it as a matplotlib colormap object."""

        batlow_path = os.path.join("public", "batlow.txt")
        batlowk_path = os.path.join("public", "batlowK.txt")
        batloww_path = os.path.join("public", "batlowW.txt")

        cmap_type = self.handler.getHeatmapColor()

        cmaps = {"batlow": batlow_path,
                 "batlowK": batlowk_path,
                 "batlowW": batloww_path,
                 "viridis": "viridis",
                 "magma": "magma"
                 }

        if cmap_type in ["viridis", "magma"]:
            return cmap_type
        else:
            cm_data = np.loadtxt(cmaps[cmap_type])
            colormap = LinearSegmentedColormap.from_list('batlow', cm_data)
            return colormap

    def drawSelectedCoordinatesAlongsideGraticule(self, ax: matplotlib.axes.Axes, rotate: bool, final_rotation: np.ndarray):

        equator_degrees = np.arange(-180, 180, 30)

        for lon_deg in equator_degrees:
            if lon_deg == 0:
                label = "0"
            else:
                label = f"{int(lon_deg)}°"

            lon_rad = np.deg2rad(lon_deg)
            lat_rad = 0.0

            if rotate:
                x, y = self.rotatePointLonLatCoordinates(np.array([lon_rad]), np.array([lat_rad]), final_rotation)
            else:
                x, y = np.array([lon_rad]), np.array([lat_rad])
            ax.text(-x[0], y[0], label, fontsize=6, ha='center', va='bottom', color='white', zorder=4)

        # Add labeled degree points along Meridian (lon = 0°)

        meridian_degrees = np.arange(-90, 91, 30)  # 6 points every 30°

        for lat_deg in meridian_degrees:
            if lat_deg == 0:
                continue  # Already labeled at equator

            label = f"{int(lat_deg)}°"
            lat_rad = np.deg2rad(lat_deg)
            lon_rad = 0.0  # Meridian

            if rotate:
                x, y = self.rotatePointLonLatCoordinates(np.array([lon_rad]), np.array([lat_rad]), final_rotation)
            else:
                x, y = np.array([lon_rad]), np.array([lat_rad])
            ax.text(-x[0], y[0], label, fontsize=6, ha='left', va='center', color='white', zorder=4)