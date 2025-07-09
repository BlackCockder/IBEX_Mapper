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


def overrideDefaultConfigLocally(config: dict) -> dict:
    return _mapper.generateConfigFromPartialInfo(config)


def getObjectInstance() -> _IBEXMapperClass:
    return _mapper
