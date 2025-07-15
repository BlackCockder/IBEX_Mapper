from .handler import Handler
import json
import os


class MapFeatures:
    FEATURES_DIR = "map_features"
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")

    def __init__(self, handler: Handler):
        self.handler = handler

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

    def addCircle(self, circle_name: str, center_of_circle_vector: tuple[float, float], alpha: float, color: str) -> None:
        with open(self.FEATURES_FILE, 'r') as f:
            data = json.load(f)

        if any(circle['name'] == circle_name for circle in data.get("circles", [])):
            print(f"Point with name '{circle_name}' already exists.")
            return

        coord_str = f"({center_of_circle_vector[0]}, {center_of_circle_vector[1]})"

        data["circles"].append({
            "name": circle_name,
            "coordinates": coord_str,
            "alpha": str(alpha),
            "color": color
        })

        with open(self.FEATURES_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def removeCircle(self):
        return

    def removeAllCircles(self):
        return

    def addMapText(self):
        return

    def removeMapText(self):
        return

    def removeAllMapText(self):
        return

    def changeHeatmapScale(self):
        return

    def resetHeatmapScaleToDefault(self):
        return

    def selectHeatmapColorPalette(self):
        return

    def resetHeatmapColorPaletteToDefault(self):
        return
