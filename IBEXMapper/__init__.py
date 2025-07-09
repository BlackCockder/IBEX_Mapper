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

#
# def addPoint(name: str, point: tuple[float, float]) -> None:
#     return _projection.addPoint(name, point)
#
#
# def addCircle(name: str, point: tuple[float, float], angle: float) -> None:
#     return _projection.addCircle(name, point, angle)
#
#
# def removePoint(point_name: str) -> None:
#     return _projection.removePoint(point_name)
#
#
# def removeCircle(circle_name: str) -> None:
#     return _projection.removeCircle(circle_name)
#
#
# def removeAllPoints() -> None:
#     return _projection.removeAllPoints()
#
#
# def removeAllCircles() -> None:
#     return _projection.removeAllCircles()
#
#
# def cleanMap() -> None:
#     return _projection.cleanMap()
