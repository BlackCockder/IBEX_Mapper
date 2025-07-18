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
    """
    Main app class. Handles all top level logic.
    """
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

        # We need to generate few directories to make sure app works correctly.
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        os.makedirs(self.FEATURES_DIR, exist_ok=True)
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        # Generate default JSON files in these dirs.
        self.generateDefaultConfig()
        self.generateDefaultMapFeatures()

    def generateSingleMapFromGivenFilePath(self, file_path: str, output_path: str or None, config=None) -> None:
        """
        Main method of the app. From given path to .txt file with coefficients of spherical harmonics,
        it generates a custom mollweide projection based or user given config and map features.

        :param file_path:
        Full path to the file. Works with absolute and relative paths.

        :param output_path:
        Full path to the output folder. Works with absolute and relative paths.
        Note: App will create as many folders as it is given, so for example if "D:/data/data1/data2/data3" is given,
        then if only data exists, app will make data1, data2 and data3 and output the PDF file to the data3 folder.

        :param config:
        Config dictionary if user wishes to not use default config (use other config but not setting it up as default).

        """

        # Import the data from .txt file.
        # Note: It is user responsibility to verify that the file is valid file for this app's method of
        # generating spherical harmonics. It has to be a (N, 4) array, where first column contains
        # l of spherical harmonics function, second column contains its m, 3rd column contains the coefficients
        # and 4th column contains the uncertainties.
        imported_data = np.loadtxt(file_path, comments='#')

        # Get default config if there is no config given.
        if config is None:
            config = self.getDefaultConfig()

        # Make the directories given by the output path if it is given.
        if output_path is not None:
            os.makedirs(output_path, exist_ok=True)

        # Getting both max l's to check for potential mismatch.
        config_max_l = config["max_l_to_cache"]
        file_max_l = imported_data[-1, 0]

        # We need to check if there is l mismatch in file and config.
        self.checkFor_L_Mismatch(file_max_l, config_max_l)
        
        # Changing both points to np.arrays to use correct calculations.
        config["central_point"] = np.array(config["central_point"])
        config["meridian_point"] = np.array(config["meridian_point"])

        # Calculate the heatmap data before potential rotations.
        heatmap_data = self.handler.processUserDataset(config["map_accuracy"], config["max_l_to_cache"], imported_data)

        if config["rotate"]:
            # Initializing the grid that will be rotated.
            lon = np.linspace(np.pi, -np.pi, config["map_accuracy"])
            lat = np.linspace(np.pi / 2, -np.pi / 2, config["map_accuracy"])
            lon, lat = np.meshgrid(lon, lat)

            # Convert the grid to cartesian coordinates.
            x, y, z = self.calculator.convertSphericalToCartesian(lon, lat)

            # Build central rotation.
            central_rotation = self.configurator.buildCenteringRotation(config["central_point"])

            # If central and meridian points are the same, do only the first rotation.
            if np.allclose(config["central_point"], config["meridian_point"]) or np.allclose(config["meridian_point"], [0.0, 0.0]):

                # Why we transpose will be explained in few next lines.
                main_rotation = central_rotation.T
            else:

                # Build the second rotation.
                meridian_rotation = self.configurator.buildMeridianRotation(config["meridian_point"], central_rotation)

                # Combine rotations and transpose (again, why we transpose will be explained in a second).
                main_rotation = (meridian_rotation @ central_rotation).T

            # Rotate the grid by transposed combined rotation.
            x_rot, y_rot, z_rot = self.calculator.rotateGridByRotation(x, y, z, main_rotation)

            # Get the lon and lat coordinates back.
            lon, lat = self.calculator.convertCartesianToSpherical(x_rot, y_rot, z_rot)

            # We interpolated the new grid with old data.
            # Note: We need to transpose the rotation for the interpolator, because of how interpolation works.
            # Basically interpolator takes the data in new, unofficial coordinate system (where our central point
            # is true (0, 0)) and calculates reverse rotation to "guess" what value should be in given point
            # by doing linear interpolation. That is why we need to give it the transposed combined rotations.
            heatmap_data = self.calculator.interpolateDataForNewGrid(heatmap_data, lat, lon)

        # Filter out all negative values if this option in config is false.
        if not config["show_negative_values"]:
            heatmap_data[heatmap_data < 0] = 0

        # Passes all of this data to second main method, which is projection.
        return self.projection.projectDataOnMollweideProjection(heatmap_data, config["map_accuracy"], file_path,
                                                                config["rotate"], config["central_point"],
                                                                config["meridian_point"], output_path)

    def generateDefaultConfig(self) -> None:
        """
        Method that generates the default config and writes it directly to config/config.json.
        """

        # App set default config.
        default_config = {
            "map_accuracy": "400",
            "max_l_to_cache": "30",
            "rotate": "False",
            "central_point": "(0, 0)",  # (lon, lat)
            "meridian_point": "(0, 0)",
            "show_negative_values": "True",
            "map_features_type_checking": "True"
        }

        # Write it to config/config.json.
        with open(self.CONFIG_FILE, "w") as config:
            json.dump(default_config, config, indent=4)

    def getDefaultConfig(self) -> dict:
        """
        Method that fetches config from a config/config.json file as a python dictionary
        and returns it with parsed data from strings to python datastructures.
        """

        # Loads the config/config.json file.
        with open(self.CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)

        # Uses Handler class method to parse the entire dictionary from {key: str} to {key: correct_datatype}.
        return self.handler.formatConfigToPythonDatastructures(config)

    def setDefaultConfig(self, config: dict) -> None:
        """
        Method that takes a valid config dictionary, stringifies it and overrides the config / config.json file
        with it, setting it as the new default config.

        :param config:
        Dictionary with chosen config.
        Note: This dictionary is NOT stringified and assumed valid.
        """

        # Stringifies the config dictionary.
        stringified_config = self.handler.stringifyValue(config)

        # Puts the new stringified config into config/config.json.
        with open(self.CONFIG_FILE, "w") as c:
            json.dump(stringified_config, c, indent=4)

    def resetCurrentDefaultConfigBackToAppDefaultConfig(self) -> None:
        """
        Method that resets the current default config back to the app's default config.
        """

        # Basically overrides the current config/config.json by generating the default config again.
        self.generateDefaultConfig()

    def generateDefaultMapFeatures(self) -> None:
        """
        Method that generates default map_features.json file by throwing app defaults into it.
        """

        # Initializing app's default map features.
        default_map_features = {
            "points": [],
            "circles": [],
            "texts": [],
            # We set (0, 0) tuple as default since assert requires it to be a tuple of floats.
            # Projection will then detect whether the heatmap scale tuple is (0, 0), and if it is, projection will not
            # apply the scale (it will use dynamic scale generator based on given heatmap data).
            "heatmap_scale": "(0, 0)",
            "heatmap_color": "magma"
        }

        # Dumps it into map_features.json
        with open(self.FEATURES_FILE, "w") as map_features:
            json.dump(default_map_features, map_features, indent=4)

    def generateValidConfigFromPartialInfo(self, partial_config: dict) -> dict:
        """
        Method that takes a dictionary that have one or more config keys and turns it into a copy of the current
        default config with overwritten user-given changes.
        Note: This is the only method that should be used to generate config dictionaries,
        because it contains assertion of config dictionary.

        :param partial_config:
        Any dictionary that has at least 1 and at most all matching keys with config.

        :return:
        Returns a non-stringified, valid config dictionary.
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
        Method that checks a very dangerous exception, which is file max l being higher than config max l and
        raising ValueError if it actually is higher.
        :param file_max_l:
        File detected max l.

        :param config_max_l:
        Max l declared in config.
        """
        if file_max_l > config_max_l:
            raise ValueError("Config error: Config max l should be greater or equal to file max l.")
            
    def toggleTypeChecking(self) -> None:
        """
        Method that disables or enables type checking in map features.
        It toggles state every time it is called.
        """

        # Get default config.
        config = self.getDefaultConfig()

        # Toggle boolean to opposite.
        config["map_features_type_checking"] = not config["map_features_type_checking"]

        # Set it as default config
        self.setDefaultConfig(config)
