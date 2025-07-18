from matplotlib.axes import Axes
from matplotlib.colors import Colormap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from .configurator import Configurator
from .calculator import Calculator
from .handler import Handler
from matplotlib.offsetbox import AnchoredText
import os


class Projection:
    """
    A class for handling map projections and visualizations for IBEX data.

    This class provides functionality to create Mollweide projections of data,
    rotate coordinates, draw graticule, and visualize points of interest on maps.
    """

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
        """
        Create a Mollweide projection map with the given data and parameters.

        :param heatmap_data:
        2D array of data values to be plotted

        :param dpi:
        Resolution of the map (number of points in each dimension)

        :param filename:
        Name of the file to save the map to

        :param rotate:
        Whether to rotate the map according to the specified coordinates

        :param central_coords:
        Coordinates [longitude, latitude] in degrees for the central point

        :param meridian_coords:
        Coordinates [longitude, latitude] in degrees for the meridian point

        :param output_path:
        Path to save the map to, defaults to the output directory.

        :return:
        The map is saved to a file and displayed
        """

        filename = os.path.basename(filename)

        heatmap_data = self.changeMapScale(heatmap_data)

        lon = np.linspace(-np.pi, np.pi, dpi)
        lat = np.linspace(np.pi / 2, -np.pi / 2, dpi)
        lon, lat = np.meshgrid(lon, lat)

        fig = plt.figure(figsize=(8, 5))
        ax = fig.add_subplot(111, projection="mollweide")
        ax.set_title("IBEX Mapper")

        rotation1 = self.configurator.buildCenteringRotation(central_coords)
        rotation2 = self.configurator.buildMeridianRotation(meridian_coords, rotation1)


        final_rotation = np.array([])

        if np.allclose(central_coords, meridian_coords):
            final_rotation = rotation1
        else:
            final_rotation = rotation2 @ rotation1



        if rotate:
            self.drawGraticuleOnMap(ax, final_rotation)
        else:
            self.drawGraticuleOnMap(ax, np.eye(3))

        plt.tight_layout()
        ax.set_xticks([])
        ax.set_yticks([])
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.grid(False)

        selected_cmap = self.getMapColorPaletteToProject()

        pcm = ax.pcolormesh(lon, lat, heatmap_data, cmap=selected_cmap, shading="auto",
                            rasterized=True)
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(r'ENA flux (cm$^{-2}$s$^{-1}$sr$^{-1}$keV$^{-1}$)', fontsize=16)
        cbar.ax.tick_params(labelsize=16)

        # Adds Central and Meridian Point to the map
        self.addPointsToMap(ax, rotate, final_rotation)
        self.addCirclesToMap(ax, rotate, final_rotation)
        self.addTextsToMap(ax)
        self.drawSelectedCoordinatesAlongsideGraticule(ax, rotate, final_rotation)

        # If no output path is selected, it chooses the default directory, otherwise it selects chose one
        plt.tight_layout()
        if output_path is None:
            plt.savefig(os.path.join(self.OUTPUT_DIR, f"file_{filename}__res{dpi}.pdf"), format='pdf', dpi=dpi)
        else:
            plt.savefig(os.path.join(output_path, f"file_{filename}__res{dpi}.pdf"), format='pdf', dpi=dpi)
        plt.show()

    def cutDataForMollweideProjection(self, lon_r, lat_r, thresh=np.pi):
        """
        Return copies of lon_r, lat_r with NaNs inserted wherever the curve
        crosses the +/- pi seam, so Matplotlib starts a new segment there.

        :param lon_r:
        Array of longitude values in radians

        :param lat_r:
        Array of latitude values in radians

        :param thresh:
        Threshold value for detecting wrapping, default is np.pi

        :return:
        (lon_r, lat_r) with NaNs inserted at wrap points
        """

        # compute absolute difference between successive longitude samples; if that step is larger than pi randians,
        # it flags the position as a seam crossing so the line can be split there; returning a boolean mask
        jump = np.abs(np.diff(lon_r)) > thresh

        # if no seam crossing, return the original array untouched
        if not jump.any():
            return lon_r, lat_r

        # convert to boolean mask to the indices after which a NaN must be inserted
        idx = np.where(jump)[0] + 1

        # ensure the arrays are of floating dtype so they can hold NaNs
        lon_r, lat_r = lon_r.astype(float), lat_r.astype(float)

        # vectorized insertion set the lon/lat element at every wrap index to NaN
        lon_r[idx] = np.nan
        lat_r[idx] = np.nan
        return lon_r, lat_r

    def rotatePointLonLatCoordinates(self, lon_rad: np.ndarray,
                                     lat_rad: np.ndarray,
                                     rotation_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Rotate longitude and latitude coordinates using a rotation matrix.

        :param lon_rad:
        Array of longitude values in radians

        :param lat_rad:
        Array of latitude values in radians

        :param rotation_matrix:
        3x3 rotation matrix

        :return:
        (lon_rot, lat_rot) rotated coordinates in radians
        """

        orig_shape = lon_rad.shape  # keep grid shape

        # lon/lat -> cartesian
        x, y, z = self.calculator.convertSphericalToCartesian(
            lon_rad.ravel(),
            lat_rad.ravel()
        )
        xyz = np.vstack([x, y, z])  # (3, N)

        # rotates every point
        xyz_rot = rotation_matrix @ xyz  # (3, N)

        # cartesian -> lon/lat
        lon_rot, lat_rot = self.calculator.convertCartesianToSpherical(
            xyz_rot[0], xyz_rot[1], xyz_rot[2]
        )

        # reshape and wrap to (-pi, pi]
        lon_rot = lon_rot.reshape(orig_shape)
        lat_rot = lat_rot.reshape(orig_shape)
        lon_rot = (lon_rot + np.pi) % (2 * np.pi) - np.pi
        return lon_rot, lat_rot

    def drawGraticuleOnMap(self, ax: Axes,
                           rotation_matrix: np.ndarray,
                           lon_step: int = 30,
                           lat_step: int = 30,
                           n_seg: int = 361) -> None:
        """
        Draw a graticule (grid of parallels and meridians) on the map.

        :param ax:
        The axes to draw on

        :param rotation_matrix:
        3x3 rotation matrix

        :param lon_step:
        Step size for longitude lines in degrees, default is 30

        :param lat_step:
        Step size for latitude lines in degrees, default is 30

        :param n_seg:
        Number of segments to use for drawing lines, default is 361
        """

        # Initializing a radian space for drawing latitude graticule
        latitude_graticule_space = np.deg2rad(np.arange(-90, 91, lat_step))

        # Drawing all latitude parallels
        for parallel_step in latitude_graticule_space:
            lon_line = np.linspace(-np.pi, np.pi, n_seg)
            lat_line = np.full_like(lon_line, parallel_step)
            lon_r, lat_r = self.rotatePointLonLatCoordinates(lon_line, lat_line, rotation_matrix)
            lon_r, lat_r = self.cutDataForMollweideProjection(lon_r, lat_r)
            ax.plot(-lon_r, lat_r, lw=.4, color='grey', zorder=3)
            
        # Drawing all latitude meridians
        for lon0 in np.deg2rad(np.arange(-180, 181, lon_step)):
            lat_line = np.linspace(-np.pi / 2, np.pi / 2, n_seg)
            lon_line = np.full_like(lat_line, lon0)
            lon_r, lat_r = self.rotatePointLonLatCoordinates(lon_line, lat_line, rotation_matrix)
            lon_r, lat_r = self.cutDataForMollweideProjection(lon_r, lat_r)
            ax.plot(-lon_r, lat_r, lw=.4, color='grey', zorder=3)

    def addPointsToMap(self, ax: Axes, rotate: bool, final_rotation: np.ndarray) -> None:
        """
        Plots annotated points on the given Matplotlib axis, with optional spherical rotation.

        :param ax:
        An Axes object on which to plot the points.

        :param rotate:
        Whenever to apply the final rotation matrix to the point coordinates.

        :param final_rotation:

        A 3x3 rotation matrix to apply to the point coordinates.
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

    def addCirclesToMap(self, ax: Axes, rotate: bool, final_rotation: np.ndarray) -> None:
        """
        Plots circles on the given Matplotlib axis, with optional spherical rotation.

        :param ax:
        An Axes object on which to plot the circles.

        :param rotate:
        Whenever to apply the final rotation matrix to the circle coordinates.

        :param final_rotation:

        A 3x3 rotation matrix to apply to the circle coordinates.
        """

        circles = self.handler.getCirclesList()

        for circle in circles:

            circle_center_vector = circle["coordinates"]
            circle_center_vector_in_rad = np.array(
                [np.deg2rad(circle_center_vector[0]), np.deg2rad(circle_center_vector[1])])
            alpha = circle["alpha"]
            color = circle["color"]
            circle_linestyle = circle["linestyle"]

            circle_longitude, circle_latitude = self.calculator.createCircle(circle_center_vector_in_rad, alpha)

            if rotate:

                rotated_circle_longitude, rotated_circle_latitude = self.rotatePointLonLatCoordinates(
                    circle_longitude,
                    circle_latitude,
                    final_rotation)

                rotated_circle_longitude_cut, rotated_circle_latitude_cut = self.cutDataForMollweideProjection(
                    rotated_circle_longitude,
                    rotated_circle_latitude)

                ax.plot(-rotated_circle_longitude_cut, rotated_circle_latitude_cut,
                        color=color, linewidth=1.5, zorder=5, linestyle=circle_linestyle)
            else:
                circle_longitude_cut, circle_latitude_cut = self.cutDataForMollweideProjection(
                    circle_longitude,
                    circle_latitude)
                ax.plot(-circle_longitude_cut, circle_latitude_cut,
                        color=color, linewidth=1.5, zorder=5, linestyle=circle_linestyle)

    def addTextsToMap(self, ax: Axes):
        """
        Plots annotated texts on the given Matplotlib axis.

        :param ax:
        An Axes object on which to plot the texts.
        """

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

    def getMapColorPaletteToProject(self) -> str or Colormap:
        """
        Load a colormap from a file and return it as a matplotlib colormap object.

        :return:
        The requested colormap
        """

        batlow_path = os.path.join("public", "batlow.txt")
        batlowk_path = os.path.join("public", "batlowK.txt")
        batloww_path = os.path.join("public", "batlowW.txt")

        cmap_type = self.handler.getHeatmapColor()

        cmaps = {"batlow": batlow_path,
                 "batlowK": batlowk_path,
                 "batlowW": batloww_path,
                 "viridis": "viridis",
                 "magma": "magma",
                 "plasma": "plasma",
                 "inferno": "inferno",
                 "cividis": "cividis"
                 }

        if cmap_type in ["viridis", "magma", "plasma", "inferno", "cividis"]:
            return cmap_type
        else:
            cm_data = np.loadtxt(cmaps[cmap_type])
            colormap = LinearSegmentedColormap.from_list('batlow', cm_data)
            return colormap

    def drawSelectedCoordinatesAlongsideGraticule(self, ax: Axes, rotate: bool,
                                                  final_rotation: np.ndarray):
        """
        Draws labeled longitude and latitude markers on the map alongside the graticule.

        :param ax:
        Matplotlib Axis object on which to draw the labels.

        :param rotate:
        Whether to apply the final rotation matrix to the coordinates.

        :param final_rotation:
        A 3x3 rotation matrix to apply to the coordinates if "rotate" is True.
        """

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
                continue  # Already labeled at the equator

            label = f"{int(lat_deg)}°"
            lat_rad = np.deg2rad(lat_deg)
            lon_rad = 0.0  # Meridian

            if rotate:
                x, y = self.rotatePointLonLatCoordinates(np.array([lon_rad]), np.array([lat_rad]), final_rotation)
            else:
                x, y = np.array([lon_rad]), np.array([lat_rad])
            ax.text(-x[0], y[0], label, fontsize=6, ha='left', va='center', color='white', zorder=4)