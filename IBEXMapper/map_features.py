import json
import os
from .handler import Handler


class MapFeatures:
    """
    Class that gives user methods to add or remove points, circles and texts from generated map
    as well as defining methods to manipulate map's scale and color.
    """

    # Initializing map_features folder using os package to ensure OS compatibility.
    FEATURES_DIR = "map_features"
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")
    
    def __init__(self, handler: Handler):
        self.handler = handler

    # ------------------------------------
    # POINTS
    # ------------------------------------

    def addPoint(self,
                 point_name: str,
                 coordinates: tuple[float, float],
                 color: str,
                 show_text: bool,
                 point_type: str) -> None:
        """
        Method to add a point to a map.

        :param point_name:
        :param coordinates:
        :param color:
        :param show_text:
        :param point_type:
        :return:
        """

        self.handler.assertPoint(coordinates, color, show_text, point_type)
        
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        if any(p['name'] == point_name for p in data.get("points", [])):
            print(f"Point with name '{point_name}' already exists.")
            return
          
        data["points"].append({
            "name": point_name,
            "coordinates": self.handler.stringlifyValue(coordinates),
            "color": color,
            "show_text": show_text,
            "point_type": point_type
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

    # ------------------------------------
    # CIRCLES
    # ------------------------------------

    def addCircle(self, circle_name: str,
                  coordinates: tuple[float, float],
                  alpha: float,
                  color: str,
                  linestyle: str) -> None:

        self.handler.assertCircle(coordinates, alpha, color, linestyle)

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        if any(p['name'] == circle_name for p in data.get("circles", [])):
            print(f"Circle with name '{circle_name}' already exists.")
            return

        data["circles"].append({
            "name": circle_name,
            "coordinates": self.handler.stringlifyValue(coordinates),
            "alpha": self.handler.stringlifyValue(alpha),
            "color": color,
            "linestyle": linestyle
        })

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
    def removeCircle(self, circle_name: str) -> None:
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

    def removeAllCircles(self):
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["circles"] = []

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    # ------------------------------------
    # TEXTS
    # ------------------------------------

    def addMapText(self,
                   text_name: str,
                   coordinates: tuple[float, float],
                   color: str,
                   font_size: int,
                   tilt_angle: float) -> None:

        self.handler.assertText(coordinates, color, font_size, tilt_angle)

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

            if any(p['name'] == text_name for p in data.get("texts", [])):
                print(f"Text with name '{text_name}' already exists.")
                return

            coord_str = f"({coordinates[0]}, {coordinates[1]})"

            data["texts"].append({
                "name": text_name,
                "coordinates": self.handler.stringlifyValue(coord_str),
                "color": color,
                "font_size": self.handler.stringlifyValue(font_size),
                "tilt_angle": self.handler.stringlifyValue(tilt_angle),
            })

            with open(self.FEATURES_FILE, 'w') as f:
                json.dump(data, f, indent=4)

    def removeMapText(self, text_name: str) -> None:
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        texts = data.get("texts", [])

        for i, text in enumerate(texts):
            if text["name"] == text_name:
                del texts[i]
                break
        else:
            print(f"Point with name '{texts}' does not exist.")
            return

        data["texts"] = texts

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removeAllMapText(self):
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["texts"] = []

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    # ------------------------------------
    # HEATMAP SCALES
    # ------------------------------------

    def changeHeatmapScale(self, scale: tuple[float, float]) -> None:

        self.handler.assertHeatmapScale(scale)

        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_scale"] = self.handler.stringlifyValue(scale)

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def resetHeatmapScaleToDefault(self):
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_scale"] = self.handler.stringlifyValue((0, 0))

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def selectHeatmapColorPalette(self, color: str) -> None:

        # Asserts that color is valid color.
        self.handler.assertHeatmapColor(color)

        # We load the file here.
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_color"] = color

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def resetHeatmapColorPalette(self):
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        data["heatmap_color"] = "magma"

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def cleanMap(self) -> None:
        self.removeAllPoints()
        self.removeAllCircles()
        self.removeAllMapText()
        self.resetHeatmapScaleToDefault()
        self.resetHeatmapColorPalette()
