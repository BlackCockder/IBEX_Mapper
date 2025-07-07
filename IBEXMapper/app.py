import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
import numpy as np
from copy import deepcopy


class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator, handler: Handler) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler
        self.generateDefaultConfig()
        self.def_config = self.getDefaultConfig()

    def generateMapFromLink(self, file_path: str, config=None) -> None:
        imported_data = np.loadtxt(file_path, comments='#')
        if config is None:
            config = self.def_config

        heatmap_data  = self.handler.processUserDataset(int(config["map_accuracy"]), int(config["max_l_to_cache"]), imported_data)
        if config["rotate"]:
            lon = np.linspace(-np.pi, np.pi, int(config["map_accuracy"]))
            lat = np.linspace(np.pi / 2, -np.pi / 2, int(config["map_accuracy"]))
            x, y, z = self.calculator.convertSphericalToCartesian(lon, lat)

            aligned_data = self.configurator.buildCenteringRotation(config["location_of_central_point"])
            rotated_data = self.configurator.buildAligningRotation(config["meridian_point"])
            x_rot, y_rot, z_rot = self.calculator.rotateGridByTwoRotations(x, y, z, aligned_data, rotated_data)
            lon, lat = self.calculator.convertCartesianToSpherical(z_rot, y_rot, z_rot)
            heatmap_data = self.calculator.interpolateDataForNewGrid(heatmap_data, lat, lon)

        return self.projection.projection(heatmap_data, int(config["map_accuracy"]), file_path)

    def generateDefaultConfig(self):
        default_config = {
            "map_accuracy": "720",
            "max_l_to_cache": "30",
            "rotate": "False",
            "location_of_central_point": "(0, 0)",
            "meridian_point": "(90, -120)",
        }
        with open("config.json", "w") as config:
            json.dump(default_config, config, indent=4)

    def setDefaultConfig(self, config: dict) -> None:
        with open("config.json", "w") as c:
            json.dump(config, c, indent=4)