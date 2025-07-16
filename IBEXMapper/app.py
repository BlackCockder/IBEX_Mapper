import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
from .map_features import MapFeatures
import numpy as np
from copy import deepcopy
import os


class IBEXMapper:
    CONFIG_DIR = "config"
    FEATURES_DIR = "map_features"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")
    OUTPUT_DIR = "output"

    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator,
                 handler: Handler, map_features: MapFeatures) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler
        self.map_features = map_features

        os.makedirs(self.CONFIG_DIR, exist_ok=True)

        os.makedirs(self.FEATURES_DIR, exist_ok=True)

        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        self.generateDefaultConfig()

        self.generateDefaultMapFeatures()

    def generateSingleMapFromGivenFilePath(self, file_path: str, config=None) -> None:

        imported_data = np.loadtxt(file_path, comments='#')

        if config is None:
            config = self.getDefaultConfig()

        config_max_l = config["max_l_to_cache"]

        file_max_l = imported_data[-1, 0]

        # We need to check if there is a l mismatch in file and config.
        self.checkFor_L_Mismatch(file_max_l, config_max_l)

        heatmap_data = self.handler.processUserDataset(config["map_accuracy"], config["max_l_to_cache"], imported_data)
        if config["rotate"]:
            lon = np.linspace(np.pi, -np.pi, config["map_accuracy"])
            lat = np.linspace(np.pi / 2, -np.pi / 2, config["map_accuracy"])
            lon, lat = np.meshgrid(lon, lat)
            x, y, z = self.calculator.convertSphericalToCartesian(lon, lat)
            central_rotation = self.configurator.buildCenteringRotation(config["central_point"])
            if (config["central_point"][0] == config["meridian_point"][0]
                    and config["central_point"][1] == config["meridian_point"][1]):
                main_rotation = central_rotation.T
            else:
                meridian_rotation = self.configurator.buildMeridianRotation(config["meridian_point"], central_rotation)
                main_rotation = (meridian_rotation @ central_rotation).T
            x_rot, y_rot, z_rot = self.calculator.rotateGridByRotation(x, y, z, main_rotation)
            lon, lat = self.calculator.convertCartesianToSpherical(x_rot, y_rot, z_rot)
            heatmap_data = self.calculator.interpolateDataForNewGrid(heatmap_data, lat, lon)

        if not config["allow_negative_values"]:
            heatmap_data[heatmap_data < 0] = 0
        return self.projection.projection(heatmap_data, config["map_accuracy"], file_path, config["rotate"],
                                          config["central_point"], config["meridian_point"])

    def generateDefaultConfig(self) -> None:
        """
        Method that generates default config and writes it directly to config/config.json.
        """

        # App set default config.
        default_config = {
            "map_accuracy": "400",
            "max_l_to_cache": "30",
            "rotate": "False",
            "central_point": "(0, 0)",  # (lon, lat)
            "meridian_point": "(0, 0)",
            "allow_negative_values": "True",
        }

        # Write it to config/config.json.
        with open(self.CONFIG_FILE, "w") as config:
            json.dump(default_config, config, indent=4)

    def getDefaultConfig(self) -> dict:
        """
        Method that fetches config from config/config.json file as python dictionary
        and returns it with parsed data from strings to python datastructures.
        """

        # Loads the config/config.json file.
        with open(self.CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)

        # Uses Handler class method to parse the entire dictionary from {key: str} to {key: correct_datatype}.
        return self.handler.formatConfigToPythonDatastructures(config)

    def setDefaultConfig(self, config: dict) -> None:
        """
        Method that takes a valid config dictionary, stringlifies it and overrides config/config.json file
        with it, setting it as new default config.

        :param config:
        Dictionary with chosen config.
        Note: This dictionary is NOT stringlified and assumed valid.
        """

        # Stringlifies the config dictionary.
        stringlified_config = self.handler.stringlifyValue(config)

        # Puts the new stringlified config into config/config.json.
        with open(self.CONFIG_FILE, "w") as c:
            json.dump(stringlified_config, c, indent=4)

    def resetCurrentDefaultConfigBackToAppDefaultConfig(self) -> None:
        """
        Method that resets the current default config back to app's default config.
        """

        # Basically overrides the current config/config.json by generating default config again.
        self.generateDefaultConfig()

    def generateDefaultMapFeatures(self) -> None:
        """
        Generates default map_features.json file by throwing app defaults into it.
        """

        # Initializing app's default map features.
        default_map_features = {
            "points": [],
            "circles": [],
            "texts": [],
            # We set (0, 0) tuple as default since assert requires it to be tuple of floats.
            # Projection will then detect whether the heatmap scale tuple is (0, 0) and if it is, projection will not
            # apply the scale (it will use dynamic scale generator based on given heatmap data).
            "heatmap_scale": "(0, 0)",
            "heatmap_color": "magma"
        }

        # Dumps it into map_features.json
        with open(self.FEATURES_FILE, "w") as map_features:
            json.dump(default_map_features, map_features, indent=4)

    # ----------------------------------------------
    # Getters for all the map feature related stuff.
    # ----------------------------------------------
    def getMapFeatures(self) -> dict:

        with open(self.FEATURES_FILE, "r") as features_file:
            map_features = json.load(features_file)

        return self.handler.formatMapFeaturesToPythonDatastructures(map_features)

    def getPointsList(self) -> list:
        return self.getMapFeatures().get("points", [])

    def getCirclesList(self) -> list:
        return self.getMapFeatures().get("circles", [])

    def getTextsList(self) -> list:
        return self.getMapFeatures().get("texts", [])

    def getHeatmapScale(self) -> tuple[float, float]:
        return self.getMapFeatures().get("heatmap_scale")

    def getHeatmapColor(self) -> str:
        return self.getMapFeatures().get("heatmap_color")

    def generateValidConfigFromPartialInfo(self, partial_config: dict) -> dict:
        """
        Method that takes a dictionary that have one or more config keys and turns it into a copy of current
        default config with overwritten user-given changes.
        Note: This is the only method that should be used to generate config dictionaries,
        because it contains assertion of config dictionary.

        :param partial_config:
        Any dictionary that has at least 1 and at most all matching keys with config.

        :return:
        Returns a non-stringlified, valid config dictionary.
        """

        # Gets the default config.
        default_config = self.getDefaultConfig()

        # Deepcopy the config to make it easy to update later.
        merged_config = deepcopy(default_config)

        # Asserts if partial_config is valid partial config dictionary.
        self.handler.assertConfig(partial_config)

        # Applies the changes by updating matching keys.
        merged_config.update(partial_config)

        return merged_config

    def checkFor_L_Mismatch(self, file_max_l: int, config_max_l: int) -> None:
        """
        Method tha checks a very dangerous exception, which is file max l being higher than config max l and
        raising ValueError if it actually is higher.

        :param file_max_l:
        File detected max l.

        :param config_max_l:
        Max l declared in config.
        """
        if file_max_l < config_max_l:
            raise ValueError("Config error: Config max l should be greater or equal to file max l.")
