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
                ax.plot(-lon_spherical[0], lat_spherical[0], 'o', markersize=5, color=color)
                ax.text(-lon_spherical[0], lat_spherical[0], f' {name}', fontsize=7, color=color)
            else:
                spherical[0] = np.deg2rad(spherical[0])
                spherical[1] = np.deg2rad(spherical[1])
                ax.plot(-spherical[0], spherical[1], 'o', markersize=5, color=color)
                ax.text(-spherical[0], spherical[1], f' {name}', fontsize=7, color=color)













































        pcm = ax.pcolormesh(lon, lat, z, cmap="magma", shading="auto") # cmap: "viridis"
        cbar = fig.colorbar(pcm, ax=ax, orientation="horizontal", pad=0.05)
        cbar.set_label(safe_label)

        ax.plot(central_lon[0], central_lat[0], 'ro', markersize=6, label="Central Point")
        ax.plot(meridian_lon[0], meridian_lat[0], 'bo', markersize=6, label="Meridian Point")
        ax.legend(loc='lower left')
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
