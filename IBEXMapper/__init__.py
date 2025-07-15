from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
from .map_features import MapFeatures
from .app import IBEXMapper as _IBEXMapperClass


_calculator = Calculator()
_map_features = MapFeatures()
_configurator = Configurator(_calculator)
_projection = Projection(_calculator, _configurator)
_handler = Handler(_calculator)
_mapper = _IBEXMapperClass(_projection, _calculator, _configurator, _handler, _map_features)


def getObjectInstance() -> _IBEXMapperClass:
    return _mapper


def generateSingleMapFromGivenFilePath(link: str, config=None) -> None:
    return _mapper.generateSingleMapFromGivenFilePath(link, config)


def setDefaultConfig(config: dict) -> None:
    return _mapper.setDefaultConfig(config)


def resetConfigToDefaultConfig() -> None:
    return _mapper.resetCurrentDefaultConfigBackToAppDefaultConfig()


def createNewConfig(config: dict) -> dict:
    return _mapper.generateValidConfigFromPartialInfo(config)


def addPoint(point_name: str, point: tuple[float, float], color: str) -> None:
    return _mapper.addPoint(point_name, point, color)


def removePoint(point_name: str) -> None:
    return _mapper.map_features.removePoint(point_name)


def removeAllPoints() -> None:
    return _mapper.map_features.removeAllPoints()


def addCircle(name: str, point: tuple[float, float], angle: float) -> None:
    return _mapper.addCircle(name, point, angle)


def removeCircle(circle_name: str) -> None:
    return _mapper.removeCircle(circle_name)


def removeAllCircles() -> None:
    return _projection.removeAllCircles()


def cleanMap() -> None:
    return _mapper.map_features.cleanMap()
