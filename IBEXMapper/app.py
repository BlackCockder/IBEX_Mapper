import json
from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
import numpy as np
from copy import deepcopy
import ast
import os


class IBEXMapper:
    CONFIG_DIR = "config"
    FEATURES_DIR = "map_features"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")

    def __init__(self, projection: Projection, calculator: Calculator, configurator: Configurator,
                 handler: Handler) -> None:
        self.projection = projection
        self.calculator = calculator
        self.configurator = configurator
        self.handler = handler

        os.makedirs(self.CONFIG_DIR, exist_ok=True)

        os.makedirs(self.FEATURES_DIR, exist_ok=True)

        if not os.path.exists(self.CONFIG_FILE):
            self.generateDefaultConfig()
        if not os.path.exists(self.FEATURES_FILE):
            with open(self.FEATURES_FILE, "w") as f:
                json.dump({"points": [], "circles": []}, f, indent=4)

    def generateMapFromLink(self, file_path: str, config=None) -> None:
        imported_data = np.loadtxt(file_path, comments='#')
        if config is None:
            config = self.formatConfigDatastructures(self.getDefaultConfig())

        heatmap_data = self.handler.processUserDataset(config["map_accuracy"], config["max_l_to_cache"], imported_data)
        if config["rotate"]:
            lon = np.linspace(np.pi, -np.pi, config["map_accuracy"])
            lat = np.linspace(np.pi / 2, -np.pi / 2, config["map_accuracy"])
            lon, lat = np.meshgrid(lon, lat)
            x, y, z = self.calculator.convertSphericalToCartesian(lon, lat)
            central_rotation = self.configurator.buildCenteringRotation(config["central_point"])
            if config["central_point"][0] == config["meridian_point"][0] and config["central_point"][1] == config["meridian_point"][1]:
                main_rotation = central_rotation.T
            else:
                meridian_rotation = self.configurator.buildMeridianRotation(config["meridian_point"], central_rotation)
                main_rotation = self.calculator.combineRotation(central_rotation, meridian_rotation).T
            x_rot, y_rot, z_rot = self.calculator.rotateGridByRotation(x, y, z, main_rotation)
            lon, lat = self.calculator.convertCartesianToSpherical(x_rot, y_rot, z_rot)
            heatmap_data = self.calculator.interpolateDataForNewGrid(heatmap_data, lat, lon)

        heatmap_data[heatmap_data < 0] = 0
        return self.projection.projection(heatmap_data, config["map_accuracy"], file_path, config["rotate"],
                                          config["central_point"], config["meridian_point"])

    def addPoint(self, point_name: str, coordinates: tuple[float, float], color: str) -> None:
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        if any(p['name'] == point_name for p in data.get("points", [])):
            print(f"Point with name '{point_name}' already exists.")
            return

        coord_str = f"({coordinates[0]}, {coordinates[1]})"

        data["points"].append({
            "name": point_name,
            "coordinates": coord_str,
            "color": color
        })

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removePoint(self, point_name: str) -> None:
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        points = data.get("points", [])

        for i, point in enumerate(points):
            if point["name"] == point_name:
                del points[i]
                break
        else:
            print(f"Point with name '{point_name}' does not exist.")
            return

        data["points"] = points

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removeAllPoints(self) -> None:
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["points"] = []

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def generateDefaultConfig(self):
        default_config = {
            "map_accuracy": "400",
            "max_l_to_cache": "30",
            "rotate": "False",
            "central_point": "(0, 0)",  # (lon, lat)
            "meridian_point": "(0, 0)"
        }
        with open(self.CONFIG_FILE, "w") as config:
            json.dump(default_config, config, indent=4)

    def setDefaultConfig(self, config: dict) -> None:
        def convert_value(value):
            if isinstance(value, (int, bool)):
                return str(value)
            elif isinstance(value, np.ndarray):
                return str(tuple(value.tolist()))
            else:
                return str(value)

        serialized_config = {key: convert_value(value) for key, value in config.items()}
        with open(self.CONFIG_FILE, "w") as c:
            json.dump(serialized_config, c, indent=4)

    def generateConfigFromPartialInfo(self, partial_config: dict) -> dict:
        default_config = self.formatConfigDatastructures(self.getDefaultConfig())

        merged_config = deepcopy(default_config)

        self.assertConfig(partial_config)

        merged_config.update(partial_config)

        return merged_config

    def getDefaultConfig(self) -> dict:
        with open(self.CONFIG_FILE, "r") as config_file:
            return json.load(config_file)

    def resetConfig(self) -> None:
        self.generateDefaultConfig()

    def formatConfigDatastructures(self, config: dict) -> dict:
        config_types_schema = {
            "map_accuracy": int,
            "max_l_to_cache": int,
            "rotate": bool,
            "central_point": np.ndarray,
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

    def assertConfig(self, config: dict) -> None:
        if "map_accuracy" in config:
            try:
                map_accuracy = int(config["map_accuracy"])
                if map_accuracy <= 0:
                    raise ValueError("Map accuracy must be a positive integer.")
            except (ValueError, TypeError):
                raise ValueError("Map accuracy must be a positive integer.")

        if "max_l_to_cache" in config:
            try:
                max_l = int(config["max_l_to_cache"])
                if max_l <= 0:
                    raise ValueError("Max l must be a positive integer.")
            except (ValueError, TypeError):
                raise ValueError("Max l must be a positive integer.")

        if "rotate" in config:
            rotate = config["rotate"]
            if isinstance(rotate, str):
                if rotate.lower() not in ("true", "false"):
                    raise ValueError("Rotate must be a boolean or a string 'True'/'False'.")
            elif not isinstance(rotate, bool):
                raise ValueError("Rotate must be a boolean.")

        def validate_geo_point(name, val):
            try:
                if isinstance(val, str):
                    val = ast.literal_eval(val)
                arr = np.array(val)
                if arr.ndim != 1 or arr.shape[0] != 2:
                    raise ValueError(f"{name} must be a 1D array of two values.")
                lon, lat = arr
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    raise ValueError(f"{name} coordinates out of bounds: "
                                     f"longitude must be in [-180, 180], latitude in [-90, 90].")
            except Exception:
                raise ValueError(f"{name} must be a 1D array-like structure of two floats (e.g., (lon, lat)).")

        if "central_point" in config:
            validate_geo_point("Central point", config["central_point"])

        if "meridian_point" in config:
            validate_geo_point("Meridian point", config["meridian_point"])
