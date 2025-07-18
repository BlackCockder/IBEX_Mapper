import json
import os
from .handler import Handler


class MapFeatures:
    """
    Class for managing various map features in the IBEX Mapper application.
    
    This class provides methods to add, remove, and manage different types of map features
    such as points, circles, text annotations, and heatmap settings. All features are
    stored in a JSON file for persistence.
    """
    # Initializing map_features folder using os package to ensure OS compatibility.
    CONFIG_DIR = "config"
    FEATURES_DIR = "map_features"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")
    
    def __init__(self, handler: Handler):
        self.handler = handler

    # ----------------------------------------
    #                  POINTS
    # ----------------------------------------

    def addPoint(self,
                 point_name: str,
                 coordinates: tuple[float, float],
                 color: str,
                 show_text: bool,
                 point_type: str,
                 hollow: bool) -> None:
        """
        Add a point to the map.

        :param point_name:
        Unique name identifier for the point

        :param coordinates:
        Latitude and longitude coordinates

        :param color:
        Color of the point marker

        :param show_text:
        Whether to display the point name on the map

        :param point_type:
        Type of point marker to display

        :param hollow:
        Whether the point marker should be hollow or not
            
        Note:
        If a point with the same name already exists, it will be overwritten.
        """

        if self.getMapFeaturesTypeCheckingValue():
            self.handler.assertPoint(coordinates, color, show_text, point_type,  hollow)
        
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        if any(p['name'] == point_name for p in data.get("points", [])):
            print(f"Point with name '{point_name}' already exists. Overwriting...")
          
        data["points"].append({
            "name": point_name,
            "coordinates": self.handler.stringifyValue(coordinates),
            "color": color,
            "show_text": self.handler.stringifyValue(show_text),
            "point_type": point_type,
            "hollow": self.handler.stringifyValue(hollow)
        })

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removePoint(self, point_name: str) -> None:
        """
        Remove a point from the map by its name.

        :param point_name:
        Name of the point to remove

        Note:
        If a point with the specified name does not exist, a message will be printed.
        """

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
        """
        Remove all points from the map.
        
        This method clears all points from the map features file.
        """

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["points"] = []

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    # ----------------------------------------
    #                  CIRCLES
    # ----------------------------------------

    def addCircle(self, circle_name: str,
                  coordinates: tuple[float, float],
                  alpha: float,
                  color: str,
                  linestyle: str) -> None:
        """
        Add a circle to the map.

        :param circle_name:
        Unique name identifier for the circle

        :param coordinates:
        Center coordinates (latitude, longitude)

        :param alpha:
        Transparency level of the circle (0.0 to 1.0)

        :param color:
        Color of the circle

        :param linestyle:
        Style of the circle's outline (e.g., 'solid', 'dashed')

        Note:
        If a circle with the same name already exists, it will be overwritten.
        """
        if self.getMapFeaturesTypeCheckingValue():
            self.handler.assertCircle(coordinates, alpha, color, linestyle)

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        if any(p['name'] == circle_name for p in data.get("circles", [])):
            print(f"Circle with name '{circle_name}' already exists. Overwriting...")

        data["circles"].append({
            "name": circle_name,
            "coordinates": self.handler.stringifyValue(coordinates),
            "alpha": self.handler.stringifyValue(alpha),
            "color": color,
            "linestyle": linestyle
        })

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
    def removeCircle(self, circle_name: str) -> None:
        """
        Remove a circle from the map by its name.

        :param circle_name:
        Name of the circle to remove

        Note:
        If a circle with the specified name does not exist, a message will be printed.
        """

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        circles = data.get("circles", [])

        for i, circle in enumerate(circles):
            if circle["name"] == circle_name:
                del circles[i]
                break
        else:
            print(f"Point with name '{circle_name}' does not exist.")
            return

        data["points"] = circles

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removeAllCircles(self) -> None:
        """
        Remove all circles from the map.
        
        This method clears all circles from the map features file.
        """

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["circles"] = []

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    # ----------------------------------------
    #                  TEXTS
    # ----------------------------------------

    def addMapText(self,
                   text_name: str,
                   coordinates: tuple[float, float],
                   color: str,
                   font_size: int,
                   tilt_angle: float) -> None:
        """
        Add text annotation to the map.

        :param text_name:
        Unique name identifier for the text, also the text to display

        :param coordinates:
        Position coordinates (latitude, longitude)

        :param color:
        Color of the text

        :param font_size:
        Size of the text font

        :param tilt_angle:
        Rotation angle of the text in degrees. Defaults to 0.

        Note:
        If a text with the same name already exists, it will be overwritten.
        """

        if self.getMapFeaturesTypeCheckingValue():
            self.handler.assertText(coordinates, color, font_size, tilt_angle)

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

            if any(p['name'] == text_name for p in data.get("texts", [])):
                print(f"Text with name '{text_name}' already exists. Overwriting...")

            data["texts"].append({
                "name": text_name,
                "coordinates": self.handler.stringifyValue(coordinates),
                "color": color,
                "font_size": self.handler.stringifyValue(font_size),
                "tilt_angle": self.handler.stringifyValue(tilt_angle),
            })

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removeMapText(self, text_name: str) -> None:
        """
        Remove text annotation from the map by its name.

        :param text_name:
        Name of the text to remove

        Note:
        If a text with the specified name does not exist, a message will be printed.
        """

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        texts = data.get("texts", [])

        for i, text in enumerate(texts):
            if text["name"] == text_name:
                del texts[i]
                break
        else:
            print(f"Point with name '{text_name}' does not exist.")
            return

        data["texts"] = texts

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removeAllMapText(self) -> None:
        """
        Remove all text annotations from the map.
        
        This method clears all text annotations from the map features file.
        """

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["texts"] = []

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    # ----------------------------------------
    #         HEATMAP SCALE AND COLOR
    # ----------------------------------------

    def changeHeatmapScale(self, scale: tuple[float, float]) -> None:
        """
        Method that changes the heatmap scale.

        :param scale:
        A tuple[x: float, y: float] containing the new heatmap scale.
        Note: x must always be lower than y.
        """

        if self.getMapFeaturesTypeCheckingValue():
            self.handler.assertHeatmapScale(scale)

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_scale"] = self.handler.stringifyValue(scale)

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def resetHeatmapScaleToDefault(self):
        """
        Method that resets the heatmap scale to the default value.
        """
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_scale"] = self.handler.stringifyValue((0, 0))

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def selectHeatmapColorPalette(self, color: str) -> None:
        """
        Method that selects the color palette.

        :param color:
        String that represents the color palette.
        """

        # Asserts that color is valid color.
        if self.getMapFeaturesTypeCheckingValue():
            self.handler.assertHeatmapColor(color)

        # We load the file here.
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        # Change the color.
        data["heatmap_color"] = color

        # Dump it back.
        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def resetHeatmapColorPalette(self):
        """
        Method that resets the color palette back to the default value, which is "magma".
        """

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_color"] = "magma"

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def cleanMap(self) -> None:
        """
        Method that cleans all map features.
        """
        self.removeAllPoints()
        self.removeAllCircles()
        self.removeAllMapText()
        self.resetHeatmapScaleToDefault()
        self.resetHeatmapColorPalette()

    def getMapFeaturesTypeCheckingValue(self) -> bool:
        """
        Helper method that returns current value of type checking flag and enforces it in all map features methods.
        """

        # Load the file.
        with open(self.CONFIG_FILE, 'r') as f:
            config = json.load(f)

        # We cannot access getConfig method in map_features so we need to manually check if the value is True or False.
        value = config.get("map_features_type_checking", "False")
        return value.lower() == "true"
