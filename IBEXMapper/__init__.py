from .calculator import Calculator
from .configurator import Configurator
from .projection import Projection
from .handler import Handler
from .app import IBEXMapper as _IBEXMapperClass


_projection = Projection()
_calculator = Calculator()
_configurator = Configurator()
_handler = Handler(_calculator)
_mapper = _IBEXMapperClass(_projection, _calculator, _configurator, _handler)


def generateMapFromLink(link: str, accuracy: int, target_max_l: int):
    return _mapper.generateMapFromLink(link, accuracy, target_max_l)
