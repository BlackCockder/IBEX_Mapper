import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
import numpy as np
from copy import deepcopy
import ast
import os
import matplotlib.pyplot as plt


class IBEXMapper:
    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator, handler: Handler) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler
        self.generateDefaultConfig()
        self.def_config = self.formatConfigDatastructures(self.getDefaultConfig())

    def generateMapFromLink(self, file_path: str, config=None) -> None:
        imported_data = np.loadtxt(file_path, comments='#')
        if config is None:
            config = self.def_config

        heatmap_data = self.handler.processUserDataset(config["map_accuracy"], config["max_l_to_cache"], imported_data)
        if config["rotate"]:
            lon = np.linspace(np.pi, -np.pi, config["map_accuracy"])
            lat = np.linspace(np.pi / 2, -np.pi / 2, config["map_accuracy"])
            lon, lat = np.meshgrid(lon, lat)
            x, y, z = self.calculator.convertSphericalToCartesian(lon, lat)
            central_rotation = self.configurator.buildCenteringRotation(config["location_of_central_point"])
            meridian_rotation = self.configurator.buildMeridianRotation(config["meridian_point"], central_rotation)
            x_rot, y_rot, z_rot = self.calculator.rotateGridByTwoRotations(x, y, z, central_rotation, meridian_rotation)
            lon, lat = self.calculator.convertCartesianToSpherical(x_rot, y_rot, z_rot)
            heatmap_data = self.calculator.interpolateDataForNewGrid(heatmap_data, lat, lon)

        return self.projection.projection(heatmap_data, config["map_accuracy"], file_path, config["location_of_central_point"], config["meridian_point"])

    def generateDefaultConfig(self):
        if os.path.exists("config.json"):
            return
        default_config = {
            "map_accuracy": "400",
            "max_l_to_cache": "30",
            "rotate": "False",
            "location_of_central_point": "(0, 0)",  # (lon, lat)
            "meridian_point": "(0, 0)"
        }
        with open("config.json", "w") as config:
            json.dump(default_config, config, indent=4)

    def setDefaultConfig(self, config: dict) -> None:
        with open("config.json", "w") as c:
            json.dump(config, c, indent=4)

    def generateConfigFromPartialInfo(self, partial_config: dict) -> dict:
        default_config = self.formatConfigDatastructures(self.getDefaultConfig())

        merged_config = deepcopy(default_config)

        merged_config.update(partial_config)

        return merged_config

    def getDefaultConfig(self) -> dict:
        with open("config.json", "r") as config_file:
            return json.load(config_file)

    def resetConfig(self) -> None:
        self.generateDefaultConfig()
        self.def_config = self.getDefaultConfig()

    def formatConfigDatastructures(self, config: dict) -> dict:
        config_types_schema = {
            "map_accuracy": int,
            "max_l_to_cache": int,
            "rotate": bool,
            "location_of_central_point": np.ndarray,
            "meridian_point": np.ndarray,
        }
        formatted_config = {}
        for key, value in config.items():
            expected_type = config_types_schema.get(key, str)
            try:
                formatted_config[key] = self.parseDataToCorrectType(value, expected_type)
            except Exception as e:
                raise ValueError(f"Error parsing key '{key}' with value '{value}': {e}")
        return formatted_config

    def parseDataToCorrectType(self, value, expected_type):
        if expected_type == bool:
            return str(value).lower() == "true"
        elif expected_type == int:
            return int(value)
        elif expected_type == np.ndarray:
            tuple_val = ast.literal_eval(value)
            return np.array(tuple_val)
        else:
            return value
