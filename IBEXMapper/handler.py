import ast
from pathlib import Path
import numpy as np
from .calculator import Calculator
import os


class Handler:
    CONFIG_DIR = "config"
    FEATURES_DIR = "map_features"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")
    """
    This class is responsible for using logic from calculator to build the final heatmap matrix
    and for sanitizing user given data.
    """
    def __init__(self, calculator: Calculator):
        self.calculator = calculator

    def processUserDataset(self, dpi: int, target_max_l: int, data: np.ndarray) -> np.ndarray:
        """
        Main function that generates data for heatmap before configuration is applied.

        :param dpi:
        Resolution of the map. Ranges from 0 to infinity but generally speaking the intended accuracy is around 720.

        :param target_max_l:
        Caching parameter (related to spherical harmonics). Ranges from 0 to infinity. Determines how deep will
        calculator calculate the spherical harmonics for. Intended value is one that user sets as default in the config.

        :param data:
        Matrix of (N, 4) size. Generally used for accessing 3rd column where the coefficients are located and for
        cutting the cached spherical harmonics data to match the row length for vectorized matrix multiplication in
        calculator.

        :returns:
        Returns (dpi, dpi) size matrix of data for heatmap.
        """

        # Generating file paths for potential caching
        cache_dir = Path(__file__).resolve().parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        file_name = f"DPI{dpi}L{target_max_l}.npy"
        file_path = cache_dir / file_name

        print("Checking for cached spherical harmonics...")

        if self.checkForCachedSphericalHarmonics(file_path):
            print('Found cached spherical harmonics. Loading...')

            # We can cut it directly here because in app.py there is data sanitization that checks whether the inputted
            # file and inputted max_l are properly defined (meaning always max_l >= count_of_rows).
            cached_spherical_harmonics = self.loadSphericalHarmonicsFromCache(file_path)[:data.shape[0]]

            print("Loaded cached spherical harmonics. Initializing heatmap data calculations...")

            return self.calculator.calculateMainMatrixFromData(data, cached_spherical_harmonics, dpi)
        else:

            print(f"No cached spherical harmonics for DPI: {dpi} and L: {target_max_l}")

            print(f"Initializing calculation of spherical harmonics for DPI: {dpi} and L: {target_max_l}...")

            spherical_harmonics_matrices = self.calculator.calculateSphericalHarmonicsDataForSetDPI(dpi, target_max_l)

            print(f"Caching spherical harmonics for DPI: {dpi} and L: {target_max_l}...")

            self.cacheSphericalHarmonics(file_path, spherical_harmonics_matrices)

            print(f"Cached spherical harmonics for DPI: {dpi} and L: {target_max_l}")

            # Same assumption here as in line 51.
            cut_spherical_harmonics = spherical_harmonics_matrices[:data.shape[0]]

            print("Initializing heatmap data calculation...")

            return self.calculator.calculateMainMatrixFromData(data, cut_spherical_harmonics, dpi)

    def checkForCachedSphericalHarmonics(self, file_path) -> bool:
        return file_path.exists()

    def cacheSphericalHarmonics(self, file_path, spherical_harmonics_matrices) -> None:
        # Saves as .npy file.
        np.save(file_path, spherical_harmonics_matrices, allow_pickle=True)

    def loadSphericalHarmonicsFromCache(self, file_path: Path) -> np.ndarray:
        return np.load(file_path, allow_pickle=True)

    def stringlifyValue(self, value: any) -> str or dict[any: str] or list[str]:
        """
        Recursive method that converts all values in a dictionary or list of dictionaries
        to their string representations. Supports tuples, booleans, ints and floats.

        :param value:
        Value to convert. It supports lists of dictionaries even.

        :returns:
        Returns stringlified value. Can be a dictionary or list.
        """

        # Brute force all potential values.
        if isinstance(value, dict):
            return {k: self.stringlifyValue(v) for k, v in value.items()}

        if isinstance(value, list):
            return [self.stringlifyValue(v) for v in value]

        if isinstance(value, tuple):
            return str(value)

        if isinstance(value, bool):
            return "True" if value else "False"

        if isinstance(value, (int, float)):
            return str(value)

        return value

    def formatConfigToPythonDatastructures(self, config: dict) -> dict:
        """
        Method that formats the stringlified config dictionary into config dictionary with correct python datatypes.

        :param config:
        Given config to format.
        Note: It is assumed that the config is valid config dictionary.

        :return:
        Returns config dictionary formatted to correct python datastructures.
        """

        # Agreed schema of config datatypes.
        config_types_schema = {
            "map_accuracy": int,
            "max_l_to_cache": int,
            "rotate": bool,
            "central_point": tuple[float, float],
            "meridian_point": tuple[float, float],
            "allow_negative_values": bool,
        }

        # Initializing formatted config dictionary.
        formatted_config = {}

        # Loop over both key and value and try to parse it into correct datatype using other handler method.
        for key, value in config.items():

            # Get the expected type from schema
            expected_type = config_types_schema.get(key, str)

            try:

                # Use parseStringToPythonDatastructure to parse data.
                formatted_config[key] = self.parseStringsToPythonDatastructures(value, expected_type)

            except Exception as e:

                # If the parser is written correctly, this shouldn't fire even once.
                raise ValueError(f"Error parsing key '{key}' with value '{value}': {e}")

        return formatted_config

    def formatMapFeaturesToPythonDatastructures(self, features: dict) -> dict:
        """
        Formats the stringified map features JSON into proper Python datatypes.

        :param features: Map features dictionary.
        :return: Parsed map features dictionary.
        """

        # Defines feature schema.
        # Note: all "str" values are not defined here, since no conversion is needed for them.
        feature_type_schemas = {
            "points": {
                "coordinates": tuple[float, float],
                "show_text": bool,
            },
            "circles": {
                "coordinates": tuple[float, float],
                "alpha": int,
            },
            "texts": {
                "coordinates": tuple[float, float],
                "font_size": int,
                "tilt_angle": int,
            },
            "heatmap_scale": tuple[float, float],
        }

        # Initializing empty map features dictionary.
        formatted_map_features = {}

        # Processing the non-array features first.
        for key, value in features.items():
            if key not in ["points", "circles", "texts"]:

                # Get the expected type.
                expected_type = feature_type_schemas.get(key, str)
                try:

                    # Again, uses parseStringsToPythonDatastructures method to parse the value.
                    formatted_map_features[key] = self.parseStringsToPythonDatastructures(value, expected_type)

                except Exception as e:

                    # Also again, this shouldn't fire once if parser is written correctly.
                    raise ValueError(f"Error parsing root key '{key}' with value '{value}': {e}")

        # Now we process all the arrays in the map features dictionary.
        for group_key in ["points", "circles", "texts"]:

            # Getting the array to process first.
            group_items = features.get(group_key, [])

            # Getting all expected types.
            schema = feature_type_schemas.get(group_key, {})

            # Initializing parsed array.
            parsed_group = []

            # Now we process them one by one, the same logic as with non-array keys.
            for item in group_items:
                parsed_item = {}
                for item_key, item_value in item.items():
                    expected_type = schema.get(item_key, str)
                    try:
                        parsed_item[item_key] = self.parseStringsToPythonDatastructures(item_value, expected_type)
                    except Exception as e:
                        raise ValueError(
                            f"Error parsing '{group_key}' item key '{item_key}' with value '{item_value}': {e}"
                        )
                parsed_group.append(parsed_item)

            formatted_map_features[group_key] = parsed_group

        return formatted_map_features

    def parseStringsToPythonDatastructures(self, value, expected_type) -> any:
        """
        Method that parsed the validated, stringlified config dictionary values into correct values
        with correct python datastructures.

        :param value:
        Value to parse.
        Note: value is assumed to be validated.

        :param expected_type:
        Expected type to parse correctly.

        :return:
        Returns parsed value.
        """

        # Brute forces all checks.
        if expected_type == bool:
            return str(value).lower() == "true"

        if expected_type == int:
            return int(value)

        if expected_type == float:
            return float(value)

        if expected_type == tuple[float, float]:
            parsed = ast.literal_eval(value)
            return tuple(float(x) for x in parsed)

        else:
            return value

    def assertConfig(self, config: dict) -> None:
        """
        Method that asserts every value associated with every key in given, non-valid config dictionary.

        :param config:
        Config dictionary with keys and values to check.
        """

        # List of all valid keys to check whether the config dictionary doesn't have any unnecessary keys.
        valid_keys = {
            "map_accuracy",
            "max_l_to_cache",
            "rotate",
            "allow_negative_values",
            "central_point",
            "meridian_point"
        }

        # Asserts that given config only contains config dictionary keys.
        for key in config:
            if key not in valid_keys:
                raise TypeError(f"Unknown configuration key: {key}")

        # Asserts that map DPI is a positive integer.
        if "map_accuracy" in config:
            try:
                map_accuracy = config["map_accuracy"]
                if map_accuracy <= 0:
                    raise ValueError("Map accuracy must be a positive integer.")
            except (ValueError, TypeError):
                raise TypeError("Map accuracy must be a positive integer.")

        # Asserts that L is a positive integer.
        if "max_l_to_cache" in config:
            try:
                max_l = config["max_l_to_cache"]
                if max_l <= 0:
                    raise ValueError("Max l must be a positive integer.")
            except (ValueError, TypeError):
                raise ValueError("Max l must be a positive integer.")

        # Asserts that "rotate" is boolean.
        if "rotate" in config:
            rotate = config["rotate"]
            if isinstance(rotate, str):
                if rotate.lower() not in ("true", "false"):
                    raise ValueError("Rotate must be a boolean or a string 'True'/'False'.")
            elif not isinstance(rotate, bool):
                raise ValueError("Rotate must be a boolean.")

        # Asserts that setting about allowing negative values is boolean.
        if "allow_negative_values" in config:
            allow_negative_values = config["allow_negative_values"]
            if isinstance(allow_negative_values, str):
                if allow_negative_values.lower() not in ("true", "false"):
                    raise ValueError("Allow negative values must be a boolean or a string 'True'/'False'.")
            elif not isinstance(allow_negative_values, bool):
                raise ValueError("Allow negative values must be a boolean.")

        # Helper function for asserting that all geopoints are given as floats of tuples in elliptical coordinates.
        # Range is from (-180, -90) to (180, 90).
        def validateGeoPoint(name, val):
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

        # Asserts that given points are valid elliptical points. Uses the helper function.
        if "central_point" in config:
            validateGeoPoint("Central point", config["central_point"])

        if "meridian_point" in config:
            validateGeoPoint("Meridian point", config["meridian_point"])

    def assertPoint(self, coordinates: any, color: any, show_text: any, point_type: any) -> None:
        # Define valid values (these should ideally be class-level constants or passed externally)
        colors = []  # Fill this with valid color strings, e.g., ["red", "blue", "green"]
        point_types = []  # Fill this with valid point type strings, e.g., ["x", "o", "triangle"]

        # 1. Assert coordinates are valid geographic (lon, lat)
        self.assertCoordinates(coordinates, "Point coordinates")

        # 2. Color must be in predefined list
        if not isinstance(color, str):
            raise TypeError("color must be a string.")
        if color not in colors:
            raise ValueError(f"Invalid color '{color}'. Must be one of: {colors}")

        # 3. show_text must be boolean
        if not isinstance(show_text, bool):
            raise TypeError("show_text must be a boolean.")

        # 4. point_type must be in predefined list
        if not isinstance(point_type, str):
            raise TypeError("point_type must be a string.")
        if point_type not in point_types:
            raise ValueError(f"Invalid point_type '{point_type}'. Must be one of: {point_types}")

    def assertCircle(self, coordinates: any, alpha: any, color: any, linestyle: any) -> None:
        # Valid options (populate these as needed)
        colors = []       # Example: ["red", "blue", "green"]
        linestyles = []   # Example: ["solid", "dashed", "dotted"]

        # 1. Coordinates must be valid (lon, lat)
        self.assertCoordinates(coordinates, "Circle coordinates")

        # 2. Alpha must be a float in range (0, 360)
        if not isinstance(alpha, (float, int)):
            raise TypeError("alpha must be a float or int.")
        if not (0 < float(alpha) < 360):
            raise ValueError("alpha must be in the range (0, 360).")

        # 3. Color must be in the list
        if not isinstance(color, str):
            raise TypeError("color must be a string.")
        if color not in colors:
            raise ValueError(f"Invalid color '{color}'. Must be one of: {colors}")

        # 4. Linestyle must be in the list
        if not isinstance(linestyle, str):
            raise TypeError("linestyle must be a string.")
        if linestyle not in linestyles:
            raise ValueError(f"Invalid linestyle '{linestyle}'. Must be one of: {linestyles}")

    def assertText(self, coordinates: any, color: any, font_size: any, tilt_angle: any) -> None:
        # Valid options (define these as needed)
        colors = []           # Example: ["red", "blue", "green"]
        font_size_min = 8     # Minimum allowed font size
        font_size_max = 72    # Maximum allowed font size

        # 1. Coordinates must be valid (lon, lat)
        self.assertCoordinates(coordinates, "Text coordinates")

        # 2. Color must be in the list
        if not isinstance(color, str):
            raise TypeError("color must be a string.")
        if color not in colors:
            raise ValueError(f"Invalid color '{color}'. Must be one of: {colors}")

        # 3. Font size must be a positive integer within defined range
        if not isinstance(font_size, int):
            raise TypeError("font_size must be an integer.")
        if not (font_size_min <= font_size <= font_size_max):
            raise ValueError(f"font_size must be between {font_size_min} and {font_size_max}.")

        # 4. Tilt angle must be a float (or int) in [0, 360]
        if not isinstance(tilt_angle, (float, int)):
            raise TypeError("tilt_angle must be a float or int.")
        if not (0 <= float(tilt_angle) <= 360):
            raise ValueError("tilt_angle must be in the range [0, 360].")


    def assertHeatmapScale(self, heatmap_scale: any) -> None:
        if not isinstance(heatmap_scale, tuple) or len(heatmap_scale) != 2:
            raise TypeError("heatmap_scale must be a tuple of two numeric values.")

        x, y = heatmap_scale

        if not all(isinstance(v, (float, int)) for v in (x, y)):
            raise TypeError("heatmap_scale must contain numeric (float or int) values.")

        if (x, y) == (0, 0):
            print("\033[38;5;208mWarning: Custom heatmap scale given is (0, 0). Projector therefore will use automatic scale selection.\033[0m")
            return

        if x >= y:
            raise ValueError("In heatmap_scale (x, y), x must be less than y and they must not be equal.")

    def assertHeatmapColor(self, heatmap_color: any) -> None:
        # Define the allowed heatmap color palette
        colors = []  # Example: ["viridis", "plasma", "magma", "inferno"]

        if not isinstance(heatmap_color, str):
            raise TypeError("heatmap_color must be a string.")

        if heatmap_color not in colors:
            raise ValueError(f"Invalid heatmap_color '{heatmap_color}'. Must be one of: {colors}")

    def assertCoordinates(self, coordinates: any, name: str) -> None:
        if not isinstance(coordinates, tuple) or len(coordinates) != 2:
            raise TypeError(f"{name} must be a tuple of two numeric values.")
        lon, lat = coordinates
        if not all(isinstance(x, (float, int)) for x in (lon, lat)):
            raise TypeError(f"{name} must contain numeric (float or int) values.")
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError(f"{name} out of bounds: longitude must be [-180, 180], latitude must be [-90, 90].")
