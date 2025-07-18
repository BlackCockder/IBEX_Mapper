from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
from .map_features import MapFeatures
from .app import IBEXMapper as _IBEXMapperClass
from .map_features import MapFeatures

_calculator = Calculator()
_handler = Handler(_calculator)
_map_features = MapFeatures(_handler)
_configurator = Configurator(_calculator)
_projection = Projection(_calculator, _configurator, _handler)
_mapper = _IBEXMapperClass(_projection, _calculator, _configurator, _handler, _map_features)


def getObjectInstance() -> _IBEXMapperClass:
    return _mapper


def generateSingleMapFromGivenFilePath(link: str, output_path: str or None = None, config=None) -> None:
    return _mapper.generateSingleMapFromGivenFilePath(link, output_path, config)

# ----------------------------------------
#                  CONFIG
# ----------------------------------------


def setDefaultConfig(config: dict) -> None:
    return _mapper.setDefaultConfig(config)


def getDefaultConfig() -> dict:
    return _mapper.getDefaultConfig()


def resetConfigToDefaultConfig() -> None:
    return _mapper.resetCurrentDefaultConfigBackToAppDefaultConfig()


def createNewConfig(config: dict) -> dict:
    return _mapper.generateValidConfigFromPartialInfo(config)

# ----------------------------------------
#                  POINTS
# ----------------------------------------


def addPoint(point_name: str,
             coordinates: tuple[float, float],
             color: str = "g",
             show_text: bool = True,
             point_type: str = "o") -> None:
    return _mapper.map_features.addPoint(point_name, coordinates, color, show_text, point_type)


def removePoint(point_name: str) -> None:
    return _mapper.map_features.removePoint(point_name)


def removeAllPoints() -> None:
    return _mapper.map_features.removeAllPoints()

# ----------------------------------------
#                  CIRCLES
# ----------------------------------------


def addCircle(circle_name: str,
              coordinates_of_circle_center: tuple[float, float],
              angle: float = 90,
              color: str = 'g',
              linestyle: str = "-") -> None:
    return _mapper.map_features.addCircle(circle_name,
                                          coordinates_of_circle_center,
                                          angle,
                                          color,
                                          linestyle)


def removeCircle(circle_name: str) -> None:
    return _mapper.map_features.removeCircle(circle_name)


def removeAllCircles() -> None:
    return _mapper.map_features.removeAllCircles()

# ----------------------------------------
#                  TEXTS
# ----------------------------------------


def addMapText(text_name: str,
               coords: tuple[float, float],
               color: str = "g",
               font_size: int = 8,
               tilt_angle: int = 0) -> None:
    return _mapper.map_features.addMapText(text_name, coords, color, font_size, tilt_angle)


def removeMapText(text_name: str) -> None:
    return _mapper.map_features.removeMapText(text_name)


def removeAllMapText() -> None:
    return _mapper.map_features.removeAllMapText()

# ----------------------------------------
#         HEATMAP SCALE AND COLOR
# ----------------------------------------


def changeHeatmapScale(color: tuple[float, float]) -> None:
    return _mapper.map_features.changeHeatmapScale(color)


def resetHeatmapScaleToDefault():
    return _mapper.map_features.resetHeatmapScaleToDefault()


def selectHeatmapColorPalette(color: str) -> None:
    return _mapper.map_features.selectHeatmapColorPalette(color)


def resetHeatmapColorPalette():
    return _mapper.map_features.resetHeatmapColorPalette()


def getMapFeatures() -> dict:
    return _mapper.handler.getMapFeatures()


def getPointsList() -> list:
    return _mapper.handler.getPointsList()


def getCirclesList() -> list:
    return _mapper.handler.getCirclesList()


def getTextsList() -> list:
    return _mapper.handler.getTextsList()


def getHeatmapScale() -> tuple[float, float]:
    return _mapper.handler.getHeatmapScale()


def getHeatmapColor() -> str:
    return _mapper.handler.getHeatmapColor()


def cleanMap() -> None:
    # Warning: Clears all points, circles, texts and defaults heatmap scale and color.
    return _mapper.map_features.cleanMap()


def toggleTypeChecking() -> None:
    _mapper.toggleTypeChecking()
