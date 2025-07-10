from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
from .app import IBEXMapper as _IBEXMapperClass


_projection = Projection()
_calculator = Calculator()
_configurator = Configurator(_calculator)
_handler = Handler(_calculator)
_mapper = _IBEXMapperClass(_projection, _calculator, _configurator, _handler)


def generateMapFromLink(link: str, config=None) -> None:
    return _mapper.generateMapFromLink(link, config)


def setDefaultConfig(config: dict) -> None:
    return _mapper.setDefaultConfig(config)


def resetConfigToDefaultConfig() -> None:
    return _mapper.resetConfig()


def createNewConfig(config: dict) -> dict:
    return _mapper.generateConfigFromPartialInfo(config)


def getObjectInstance() -> _IBEXMapperClass:
    return _mapper


def addPoint(point_name: str, point: tuple[float, float], color: str) -> None:
    return _mapper.addPoint(point_name, point, color)


# def addCircle(name: str, point: tuple[float, float], angle: float) -> None:
#     return _projection.addCircle(name, point, angle)
#
#
def removePoint(point_name: str) -> None:
    return _mapper.removePoint(point_name)


# def removeCircle(circle_name: str) -> None:
#     return _projection.removeCircle(circle_name)
#
#
def removeAllPoints() -> None:
    return _mapper.removeAllPoints()


# def removeAllCircles() -> None:
#     return _projection.removeAllCircles()
#
#
# def cleanMap() -> None:
#     return _mapper.cleanMap()
