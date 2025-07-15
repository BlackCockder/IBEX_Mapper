import json
import os


class MapFeatures:
    FEATURES_DIR = "map_features"
    FEATURES_FILE = os.path.join(FEATURES_DIR, "map_features.json")

    def __init__(self):
        pass

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

    def removePoint(self):
        return

    def removeAllPoints(self):
        return

    def addCircle(self):
        return

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

    def resetHeatmapColorPalette(self):
        return
